import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Currency Server")


@mcp.tool()
def convert_currency(frm: str, to: str, amount: str):
    """Convert currency from one currency to another.

    Args:
        frm: Source currency code, for example USD.
        to: Target currency code, for example INR.
        amount: Currency amount as text, for example 100.
    """

    amount = float(amount)

    data = requests.get(
        "https://open.er-api.com/v6/latest/" + frm.upper(),
        timeout=20
    ).json()

    if data["result"] != "success":
        return {
            "error": "Unable to fetch exchange rate"
        }

    rate = data["rates"][to.upper()]

    return {
        "from": frm.upper(),
        "to": to.upper(),
        "amount": amount,
        "rate": rate,
        "converted_amount": round(amount * rate, 2)
    }


if __name__ == "__main__":
    mcp.run()