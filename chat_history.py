import sqlite3
from datetime import datetime


DB = "chat_history.db"


def init_db():

    conn = sqlite3.connect(DB)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            conversation_id TEXT,
            role TEXT,
            content TEXT,
            timestamp TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_message(
    user_id,
    conversation_id,
    role,
    content
):

    conn = sqlite3.connect(DB)

    conn.execute(
        """
        INSERT INTO messages
        (user_id, conversation_id, role, content, timestamp)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            str(user_id),
            str(conversation_id),
            role,
            content,
            datetime.now().isoformat()
        )
    )

    conn.commit()
    conn.close()


def get_history(
    user_id,
    conversation_id,
    limit=20
):

    conn = sqlite3.connect(DB)

    rows = conn.execute(
        """
        SELECT role, content
        FROM messages
        WHERE user_id = ?
        AND conversation_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (
            str(user_id),
            str(conversation_id),
            limit
        )
    ).fetchall()

    conn.close()

    rows.reverse()

    return rows