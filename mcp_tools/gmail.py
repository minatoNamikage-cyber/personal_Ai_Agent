import base64
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"


# ============================================================
# MCP SERVER
# ============================================================

mcp = FastMCP("Gmail")


# ============================================================
# GMAIL SCOPES
# ============================================================

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]


# ============================================================
# GET GMAIL SERVICE
# ============================================================

def get_gmail_service():

    creds = None

    # --------------------------------------------------------
    # Check credentials.json
    # --------------------------------------------------------

    if not CREDENTIALS_FILE.exists():

        raise FileNotFoundError(
            f"credentials.json not found:\n"
            f"{CREDENTIALS_FILE}"
        )

    # --------------------------------------------------------
    # Load existing token
    # --------------------------------------------------------

    if TOKEN_FILE.exists():

        try:

            creds = Credentials.from_authorized_user_file(
                str(TOKEN_FILE),
                SCOPES
            )

        except Exception:

            # Corrupted/invalid token
            creds = None

    # --------------------------------------------------------
    # Existing token is not valid
    # --------------------------------------------------------

    if not creds or not creds.valid:

        # ----------------------------------------------------
        # Refresh existing token
        # ----------------------------------------------------

        if creds and creds.expired and creds.refresh_token:

            try:

                creds.refresh(Request())

            except Exception as e:

                print(
                    f"Gmail token refresh failed: {e}"
                )

                creds = None

        # ----------------------------------------------------
        # Fresh OAuth login
        # ----------------------------------------------------

        if not creds or not creds.valid:

            print(
                "\nStarting Gmail OAuth authentication..."
            )

            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE),
                SCOPES
            )

            creds = flow.run_local_server(
                port=0
            )

        # ----------------------------------------------------
        # Save new token
        # ----------------------------------------------------

        with open(
            TOKEN_FILE,
            "w",
            encoding="utf-8"
        ) as token:

            token.write(
                creds.to_json()
            )

    # ========================================================
    # BUILD GMAIL SERVICE
    # ========================================================

    return build(
        "gmail",
        "v1",
        credentials=creds,
        cache_discovery=False
    )


# ============================================================
# SEARCH EMAILS
# ============================================================

@mcp.tool()
def search_emails(
    query: str = "",
    max_results: int = 10
) -> str:

    """
    Search Gmail emails.

    Examples:

    from:linkedin
    from:canva
    is:unread
    today
    subject:interview
    """

    try:

        service = get_gmail_service()

        # ----------------------------------------------------
        # Normalize query
        # ----------------------------------------------------

        query = query.strip()

        # ----------------------------------------------------
        # Today
        # ----------------------------------------------------

        if query.lower() == "today":

            yesterday = (
                datetime.now() - timedelta(days=1)
            ).strftime("%Y/%m/%d")

            query = f"after:{yesterday}"

        # ----------------------------------------------------
        # Gmail API
        # ----------------------------------------------------

        response = (
            service.users()
            .messages()
            .list(
                userId="me",
                q=query,
                maxResults=max_results
            )
            .execute()
        )

        messages = response.get(
            "messages",
            []
        )

        if not messages:

            return "No emails found."

        # ----------------------------------------------------
        # Get email metadata
        # ----------------------------------------------------

        results = []

        for index, message in enumerate(
            messages,
            start=1
        ):

            message_id = message["id"]

            data = (
                service.users()
                .messages()
                .get(
                    userId="me",
                    id=message_id,
                    format="metadata",
                    metadataHeaders=[
                        "From",
                        "To",
                        "Subject",
                        "Date"
                    ]
                )
                .execute()
            )

            headers = (
                data
                .get("payload", {})
                .get("headers", [])
            )

            header_map = {
                header["name"]: header["value"]
                for header in headers
            }

            results.append(
                f"{index}. "
                f"ID: {message_id}\n"
                f"From: {header_map.get('From', '')}\n"
                f"To: {header_map.get('To', '')}\n"
                f"Subject: {header_map.get('Subject', '')}\n"
                f"Date: {header_map.get('Date', '')}\n"
            )

        return "\n".join(results)

    except Exception as e:

        return (
            "Unable to search emails: "
            f"{str(e)}"
        )


# ============================================================
# READ EMAIL
# ============================================================

@mcp.tool()
def read_email(
    message_id: str
) -> str:

    """
    Read a Gmail email using its message ID.
    """

    try:

        service = get_gmail_service()

        data = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=message_id,
                format="full"
            )
            .execute()
        )

        payload = data.get(
            "payload",
            {}
        )

        # ----------------------------------------------------
        # Headers
        # ----------------------------------------------------

        headers = payload.get(
            "headers",
            []
        )

        header_map = {
            header["name"]: header["value"]
            for header in headers
        }

        # ----------------------------------------------------
        # Email body
        # ----------------------------------------------------

        body = ""

        # ----------------------------------------------------
        # Simple text/plain email
        # ----------------------------------------------------

        if payload.get("mimeType") == "text/plain":

            encoded_data = (
                payload
                .get("body", {})
                .get("data")
            )

            if encoded_data:

                body = base64.urlsafe_b64decode(
                    encoded_data
                ).decode(
                    "utf-8",
                    errors="ignore"
                )

        # ----------------------------------------------------
        # Multipart email
        # ----------------------------------------------------

        else:

            parts = payload.get(
                "parts",
                []
            )

            for part in parts:

                if part.get("mimeType") == "text/plain":

                    encoded_data = (
                        part
                        .get("body", {})
                        .get("data")
                    )

                    if encoded_data:

                        body = (
                            base64.urlsafe_b64decode(
                                encoded_data
                            )
                            .decode(
                                "utf-8",
                                errors="ignore"
                            )
                        )

                        break

        # ----------------------------------------------------
        # Result
        # ----------------------------------------------------

        return (
            f"From: {header_map.get('From', '')}\n"
            f"To: {header_map.get('To', '')}\n"
            f"Subject: {header_map.get('Subject', '')}\n"
            f"Date: {header_map.get('Date', '')}\n\n"
            f"{body}"
        )

    except Exception as e:

        return (
            "Unable to read email: "
            f"{str(e)}"
        )


# ============================================================
# SEND EMAIL
# ============================================================

@mcp.tool()
def send_email(
    to: str,
    subject: str,
    body: str
) -> str:

    """
    Send an email directly.
    """

    try:

        service = get_gmail_service()

        # ----------------------------------------------------
        # Create message
        # ----------------------------------------------------

        message = MIMEText(
            body,
            "plain",
            "utf-8"
        )

        message["To"] = to
        message["Subject"] = subject

        # ----------------------------------------------------
        # Encode
        # ----------------------------------------------------

        raw_message = (
            base64.urlsafe_b64encode(
                message.as_bytes()
            )
            .decode()
        )

        # ----------------------------------------------------
        # Send
        # ----------------------------------------------------

        result = (
            service.users()
            .messages()
            .send(
                userId="me",
                body={
                    "raw": raw_message
                }
            )
            .execute()
        )

        return (
            "Email sent successfully.\n"
            f"To: {to}\n"
            f"Subject: {subject}\n"
            f"Message ID: {result.get('id', '')}"
        )

    except Exception as e:

        return (
            "Failed to send email: "
            f"{str(e)}"
        )


# ============================================================
# DELETE EMAIL
# ============================================================

@mcp.tool()
def delete_email(
    message_id: str
) -> str:

    """
    Move a Gmail email to Trash.
    """

    try:

        service = get_gmail_service()

        (
            service.users()
            .messages()
            .trash(
                userId="me",
                id=message_id
            )
            .execute()
        )

        return (
            "Email moved to Trash successfully.\n"
            f"Message ID: {message_id}"
        )

    except Exception as e:

        return (
            "Failed to delete email: "
            f"{str(e)}"
        )


# ============================================================
# RUN MCP SERVER
# ============================================================

if __name__ == "__main__":

    mcp.run()