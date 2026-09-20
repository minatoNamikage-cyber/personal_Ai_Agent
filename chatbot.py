import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient

from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode

from chat_history import get_history


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
MCP_DIR = BASE_DIR / "mcp_tools"


# LLM
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)


# MCP TOOLS
MCP_FILES = {
    "weather": MCP_DIR / "weather.py",
    "currency": MCP_DIR / "convert_currency.py",
    "expense": MCP_DIR / "expense_tracker.py",
    "web_search": MCP_DIR / "web_search.py",
    "gmail": MCP_DIR / "gmail.py",
    "google_drive": MCP_DIR / "google_drive.py",
}


graph = None


async def initialize_graph():

    global graph

    if graph is not None:
        return graph

    # -----------------------------
    # Load MCP servers
    # -----------------------------

    servers = {}

    for name, file in MCP_FILES.items():

        if file.exists():

            servers[name] = {
                "transport": "stdio",
                "command": sys.executable,
                "args": [str(file)]
            }

    # -----------------------------
    # Get all tools
    # -----------------------------

    client = MultiServerMCPClient(servers)

    tools = await client.get_tools()

    print("Loaded tools:")

    for tool in tools:
        print("-", tool.name)


    # -----------------------------
    # Bind tools to LLM
    # -----------------------------

    model = llm.bind_tools(tools)


    # -----------------------------
    # Chatbot Node
    # -----------------------------

    def chatbot(state: MessagesState):

        response = model.invoke(
            state["messages"]
        )

        return {
            "messages": [response]
        }


    # -----------------------------
    # Router
    # -----------------------------

    def router(state: MessagesState):

        last_message = state["messages"][-1]

        if last_message.tool_calls:
            return "tools"

        return END


    # -----------------------------
    # LangGraph
    # -----------------------------

    builder = StateGraph(MessagesState)

    builder.add_node(
        "chatbot",
        chatbot
    )

    builder.add_node(
        "tools",
        ToolNode(tools)
    )


    # START → chatbot

    builder.add_edge(
        START,
        "chatbot"
    )


    # chatbot → tools / END

    builder.add_conditional_edges(
        "chatbot",
        router,
        {
            "tools": "tools",
            END: END
        }
    )


    # tools → chatbot

    builder.add_edge(
        "tools",
        "chatbot"
    )


    # Compile graph

    graph = builder.compile()

    return graph


async def chat(
        user_input: str,
        user_id,
        conversation_id
    ):

    if not user_input.strip():

        return {
            "status": "error",
            "result": "Please enter a message.",
            "tool_names": []
        }


    # Get compiled LangGraph

    global graph

    if graph is None:
        await initialize_graph()


    # Run LangGraph

    history = get_history(
        user_id,
        conversation_id
    )

    messages = []

    for role, content in history:

        messages.append({
           "role": role,
           "content": content
    })

    messages.append({
        "role": "user",
         "content": user_input
    })



    response = await graph.ainvoke({

      "messages": messages

    })


    # -----------------------------
    # Messages
    # -----------------------------

    messages = response["messages"]


    # -----------------------------
    # Tools used
    # -----------------------------

    tools_used = []

    for message in messages:

        if getattr(message, "name", None):

            if message.name not in tools_used:
                tools_used.append(message.name)


        for call in getattr(
            message,
            "tool_calls",
            []
        ):

            name = call["name"]

            if name not in tools_used:
                tools_used.append(name)


    # -----------------------------
    # UI Response
    # -----------------------------

    return {

        "status": "success",

        "result": messages[-1].content,

        "tool_names": tools_used

    }