from mcp.server.fastmcp import FastMCP
from ddgs import DDGS


mcp = FastMCP("Web Search Server")


@mcp.tool()
def web_search(query: str) -> str:
    """
    Search the internet using DuckDuckGo.

    Use this tool when the user asks for:
    - latest information
    - current events
    - recent news
    - sports results
    - information that may have changed recently

    Args:
        query: A clear web search query.
    """

    query = query.strip()

    if not query:
        return "Search query cannot be empty."

    try:
        results = DDGS().text(
            query,
            max_results=5
        )

        if not results:
            return "No search results found."

        output = []

        for result in results:

            title = result.get("title", "")
            url = result.get("href", "")
            snippet = result.get("body", "")

            output.append(
                f"Title: {title}\n"
                f"URL: {url}\n"
                f"Snippet: {snippet}"
            )

        return "\n\n".join(output)

    except Exception as e:

        return f"Search failed: {str(e)}"


if __name__ == "__main__":
    mcp.run()