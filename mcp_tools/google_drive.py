from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

from mcp.server.fastmcp import FastMCP


# ==========================================
# CONFIG
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

CREDENTIALS_FILE = BASE_DIR / "drive_credentials.json"
TOKEN_FILE = BASE_DIR / "drive_token.json"

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.file",
]


# ==========================================
# MCP SERVER
# ==========================================

mcp = FastMCP("google_drive")


# ==========================================
# GOOGLE DRIVE CONNECTION
# ==========================================

def get_drive():

    credentials = None

    # --------------------------------------
    # Load existing token
    # --------------------------------------

    if TOKEN_FILE.exists():

        credentials = Credentials.from_authorized_user_file(
            str(TOKEN_FILE),
            SCOPES
        )

    # --------------------------------------
    # Refresh existing token
    # --------------------------------------

    if credentials:

        if credentials.valid:
            pass

        elif credentials.expired and credentials.refresh_token:

            try:

                credentials.refresh(Request())

                TOKEN_FILE.write_text(
                    credentials.to_json(),
                    encoding="utf-8"
                )

            except Exception as e:

                raise RuntimeError(
                    f"Google Drive token refresh failed: {e}"
                )

        else:

            raise RuntimeError(
                "Google Drive authorization is invalid. "
                "Please authorize Drive once again."
            )

    # --------------------------------------
    # First-time authorization
    # --------------------------------------

    else:

        if not CREDENTIALS_FILE.exists():

            raise RuntimeError(
                f"Missing Google Drive credentials file: "
                f"{CREDENTIALS_FILE}"
            )

        flow = InstalledAppFlow.from_client_secrets_file(
            str(CREDENTIALS_FILE),
            SCOPES
        )

        credentials = flow.run_local_server(
            port=0
        )

        TOKEN_FILE.write_text(
            credentials.to_json(),
            encoding="utf-8"
        )

    # --------------------------------------
    # Build Drive API
    # --------------------------------------

    return build(
        "drive",
        "v3",
        credentials=credentials
    )


# ==========================================
# SEARCH DRIVE
# ==========================================

@mcp.tool()
def search_drive(query: str):

    """
    Search Google Drive files by name.
    """

    drive = get_drive()

    # Escape single quotes for Drive query
    safe_query = query.replace("'", "\\'")

    result = drive.files().list(
        q=f"name contains '{safe_query}' and trashed = false",
        spaces="drive",
        fields="files(id,name,mimeType,modifiedTime,webViewLink)",
        pageSize=20
    ).execute()

    files = result.get("files", [])

    if not files:
        return "No files found."

    return "\n".join(
        f"{file['name']} | "
        f"{file['mimeType']} | "
        f"{file['id']} | "
        f"{file.get('webViewLink', '')}"
        for file in files
    )


# ==========================================
# RECENT FILES
# ==========================================

@mcp.tool()
def recent_files():

    """
    Get recently modified files from Google Drive.
    """

    drive = get_drive()

    result = drive.files().list(
        q="trashed = false",
        spaces="drive",
        orderBy="modifiedTime desc",
        fields="files(id,name,mimeType,modifiedTime,webViewLink)",
        pageSize=20
    ).execute()

    files = result.get("files", [])

    if not files:
        return "No files found."

    return "\n".join(
        f"{file['name']} | "
        f"{file['mimeType']} | "
        f"{file['modifiedTime']} | "
        f"{file['id']}"
        for file in files
    )


# ==========================================
# GET FILE
# ==========================================

@mcp.tool()
def get_file(file_id: str):

    """
    Get information about a Google Drive file.
    """

    drive = get_drive()

    file = drive.files().get(
        fileId=file_id,
        fields=(
            "id,name,mimeType,size,"
            "createdTime,modifiedTime,webViewLink"
        )
    ).execute()

    return str(file)


# ==========================================
# DOWNLOAD FILE
# ==========================================

@mcp.tool()
def download_file(file_id: str, output_path: str):

    """
    Download a Google Drive file.
    """

    from googleapiclient.http import MediaIoBaseDownload

    drive = get_drive()

    file_info = drive.files().get(
        fileId=file_id,
        fields="id,name,mimeType"
    ).execute()

    mime_type = file_info.get("mimeType", "")

    # --------------------------------------
    # Google Docs files need export
    # --------------------------------------

    if mime_type.startswith("application/vnd.google-apps."):

        if mime_type == "application/vnd.google-apps.document":

            request = drive.files().export_media(
                fileId=file_id,
                mimeType="application/pdf"
            )

        elif mime_type == "application/vnd.google-apps.spreadsheet":

            request = drive.files().export_media(
                fileId=file_id,
                mimeType=(
                    "application/"
                    "vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                )
            )

        elif mime_type == "application/vnd.google-apps.presentation":

            request = drive.files().export_media(
                fileId=file_id,
                mimeType=(
                    "application/"
                    "vnd.openxmlformats-officedocument."
                    "presentationml.presentation"
                )
            )

        else:

            return (
                f"Cannot directly download this Google file type: "
                f"{mime_type}"
            )

    else:

        request = drive.files().get_media(
            fileId=file_id
        )

    # --------------------------------------
    # Output path
    # --------------------------------------

    output = Path(output_path)

    if not output.is_absolute():
        output = BASE_DIR / output

    output.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------
    # Download
    # --------------------------------------

    with open(output, "wb") as file:

        downloader = MediaIoBaseDownload(
            file,
            request
        )

        done = False

        while not done:

            _, done = downloader.next_chunk()

    return f"Downloaded: {output}"


# ==========================================
# RUN MCP SERVER
# ==========================================

if __name__ == "__main__":

    mcp.run(transport="stdio")