from mcp.server.fastmcp import FastMCP
import sqlite3
from datetime import datetime

mcp = FastMCP("Expense Tracker")

# ---------------- Database ----------------

conn = sqlite3.connect("expenses.db")

conn.execute("""
CREATE TABLE IF NOT EXISTS expenses(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    amount REAL,
    category TEXT,
    note TEXT
)
""")

conn.commit()
conn.close()

# ---------------- Add Expense ----------------

@mcp.tool()
def add_expense(
    date: str,
    amount: str,
    category: str,
    note: str = ""
):
    """Add a new expense."""

    if date.lower() == "today":
        date = datetime.now().strftime("%Y-%m-%d")

    amount = float(amount.replace("₹", "").strip())

    conn = sqlite3.connect("expenses.db")

    conn.execute(
        "INSERT INTO expenses(date, amount, category, note) VALUES (?, ?, ?, ?)",
        (date, amount, category, note)
    )

    conn.commit()
    conn.close()

    return "Expense added successfully."

# ---------------- Show Expenses ----------------

@mcp.tool()
def list_expenses():
    """Show all expenses."""

    conn = sqlite3.connect("expenses.db")

    cur = conn.execute(
        "SELECT date, amount, category, note FROM expenses"
    )

    rows = cur.fetchall()

    conn.close()

    if not rows:
        return "No expenses found."

    result = ""

    for date, amount, category, note in rows:

        result += (
            f"Date : {date}\n"
            f"Amount : ₹{amount}\n"
            f"Category : {category}\n"
            f"Note : {note}\n\n"
        )

    return result

# ---------------- Total Expense ----------------

@mcp.tool()
def total_expense():
    """Calculate total expense."""

    conn = sqlite3.connect("expenses.db")

    cur = conn.execute("SELECT SUM(amount) FROM expenses")

    total = cur.fetchone()[0]

    conn.close()

    if total is None:
        return "No expenses found."

    return f"Your total expense is ₹{total:.2f}"

# ---------------- Run MCP ----------------

if __name__ == "__main__":
    mcp.run()
    