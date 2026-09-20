# 🤖 Eran — Personal AI Agent

> A tool-enabled personal AI assistant built with **Python, LangGraph, MCP, Groq, Streamlit, Telegram, and SQLite**.

Eran is a personal AI assistant designed to go beyond simple chat. It can understand user requests, decide when external tools are required, execute those tools through the **Model Context Protocol (MCP)**, and return the result through a conversational interface.

The project combines an LLM-powered chatbot with a collection of MCP tools for everyday tasks such as weather information, currency conversion, expense tracking, web search, Gmail, and Google Drive.

---

## ✨ Features

* 🤖 **AI-powered conversational assistant**
* 🧠 **LangGraph-based agent workflow**
* 🔧 **MCP tool integration**
* 🌦️ Weather information
* 💱 Currency conversion
* 💰 Expense tracking
* 🌐 Web search
* 📧 Gmail integration
* 📁 Google Drive integration
* 💬 Telegram bot interface
* 🖥️ Streamlit web interface
* 💾 SQLite-based conversation history
* 🔄 Automatic tool calling based on the user's request
* 🧩 Modular MCP tool architecture

---

## 🏗️ Architecture

```text
                    ┌─────────────────────┐
                    │       User          │
                    └──────────┬──────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
        ┌───────▼────────┐          ┌────────▼────────┐
        │ Streamlit UI   │          │ Telegram Bot    │
        └───────┬────────┘          └────────┬────────┘
                │                            │
                └──────────────┬─────────────┘
                               │
                        ┌──────▼──────┐
                        │   Chatbot   │
                        │   Engine    │
                        └──────┬──────┘
                               │
                        ┌──────▼──────┐
                        │   Groq LLM  │
                        └──────┬──────┘
                               │
                        ┌──────▼──────┐
                        │  LangGraph  │
                        │ Agent Flow  │
                        └──────┬──────┘
                               │
                    ┌──────────▼──────────┐
                    │    MCP Tool Layer   │
                    └──────────┬──────────┘
                               │
       ┌──────────┬────────────┼────────────┬───────────┐
       │          │            │            │           │
    Weather   Currency     Expense      Web Search   Gmail
                                                        │
                                                   Google Drive

                               │
                        ┌──────▼──────┐
                        │   SQLite    │
                        │ Chat History│
                        └─────────────┘
```

---

## 🧠 How It Works

Eran uses **LangGraph** to manage the interaction between the language model and external tools.

The basic flow is:

```text
User Message
     ↓
LLM
     ↓
Does the request require a tool?
     ↓
 ┌───┴────┐
 │        │
 No      Yes
 │        │
 ↓        ↓
Answer   MCP Tool
           ↓
        Tool Result
           ↓
          LLM
           ↓
        Final Answer
```

The chatbot loads available MCP servers dynamically and binds their tools to the language model. LangGraph then routes the conversation either directly to the final response or through the tool execution node.

---

## 🛠️ MCP Tools

The project currently includes the following MCP integrations:

| Tool               | Purpose                           |
| ------------------ | --------------------------------- |
| 🌦️ Weather        | Get weather-related information   |
| 💱 Currency        | Convert between currencies        |
| 💰 Expense Tracker | Manage/query expenses             |
| 🌐 Web Search      | Search the web for information    |
| 📧 Gmail           | Work with Gmail                   |
| 📁 Google Drive    | Access Google Drive functionality |

The MCP tools are stored inside the `mcp_tools/` directory and are loaded by the main chatbot dynamically.

---

## 📁 Project Structure

```text
personal_Ai_Agent/
│
├── mcp_tools/
│   ├── weather.py
│   ├── convert_currency.py
│   ├── expense_tracker.py
│   ├── web_search.py
│   ├── gmail.py
│   └── google_drive.py
│
├── chatbot.py
├── chat_history.py
├── telegram_bot.py
├── ui.py
│
├── .env
├── requirements.txt
└── README.md
```

### Core Files

#### `chatbot.py`

The main AI agent engine.

It handles:

* Groq LLM initialization
* MCP server loading
* Tool discovery
* LangGraph workflow
* Tool routing
* Chat execution

The current implementation uses Groq's `openai/gpt-oss-120b` model and integrates MCP tools through `MultiServerMCPClient`.

#### `chat_history.py`

Handles persistent conversation storage using SQLite.

It provides functionality to:

* Initialize the database
* Save messages
* Retrieve conversation history
* Associate messages with users and conversations

The database stores user ID, conversation ID, role, content, and timestamp.

#### `ui.py`

Provides the web-based chat interface using **Streamlit**.

The interface includes:

* Eran branding
* Chat history within the session
* Chat input
* AI response display
* Tools-used information

#### `telegram_bot.py`

Provides a Telegram interface for Eran.

User messages received through Telegram are passed to the same chatbot engine, and conversations are saved using the SQLite chat-history layer.

---

# 🚀 Getting Started

## 1. Clone the Repository

```bash
git clone https://github.com/minatoNamikage-cyber/personal_Ai_Agent.git
```

```bash
cd personal_Ai_Agent
```

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv venv
```

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create a `.env` file in the project root.

```env
GROQ_API_KEY=your_groq_api_key

TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# Add other credentials required by the MCP tools
```

> **Important:** Never commit your `.env` file or API keys to GitHub.

Add this to `.gitignore`:

```gitignore
.env
venv/
.venv/
__pycache__/
*.pyc
chat_history.db
```

---

# ▶️ Running the Application

## Streamlit Interface

Run:

```bash
streamlit run ui.py
```

Then open the local Streamlit URL shown in your terminal.

---

## Telegram Bot

Configure your Telegram bot token in `.env`:

```env
TELEGRAM_BOT_TOKEN=your_token_here
```

Then run:

```bash
python telegram_bot.py
```

Your Telegram messages will be processed by the Eran chatbot and responses will be sent back through Telegram.

---

# 🔐 Environment & Security

This project may require credentials for external services such as:

* Groq
* Telegram
* Gmail
* Google Drive
* Web search services

Keep all credentials inside environment variables.

### Never upload:

```text
.env
API keys
Access tokens
OAuth credentials
Service-account JSON files
Private credentials
```

---

# 🧰 Tech Stack

### AI / LLM

* Python
* Groq
* LangChain
* LangGraph

### Agent & Tooling

* Model Context Protocol (MCP)
* `langchain-mcp-adapters`
* LangGraph ToolNode

### Interface

* Streamlit
* Telegram Bot API

### Storage

* SQLite

### Integrations

* Gmail
* Google Drive
* Web Search
* Weather
* Currency
* Expense Tracking

---

# 🎯 Project Goals

Eran is being developed as a modular personal AI assistant that can:

1. Understand natural-language requests.
2. Decide whether external tools are required.
3. Select the appropriate MCP tool.
4. Execute the tool.
5. Process the returned information.
6. Generate a natural-language response.
7. Maintain conversation history.
8. Work through multiple interfaces such as Web UI and Telegram.

---

# 🔮 Future Improvements

Planned improvements can include:

* 🧠 Long-term memory
* 👤 User-specific preferences
* 🗣️ Voice interaction
* 📅 Calendar integration
* 📱 More messaging platforms
* 🔐 Improved authentication
* 🧩 More MCP tools
* 📊 Personal analytics dashboard
* ⚡ Streaming responses
* 🧠 More advanced multi-agent workflows
* 🗂️ Better document and knowledge management

---

# 📌 Project Status

🚧 **Active Development**

Eran is currently a work-in-progress personal AI agent. Features and integrations may change as the project evolves.

---

# 👨‍💻 Author

**Siddharth Kumar**

GitHub: [@minatoNamikage-cyber](https://github.com/minatoNamikage-cyber)

---

## ⭐ Support

If you find this project interesting, consider giving the repository a ⭐ on GitHub.

---

## 📄 License

This project does not currently specify a license.

If you intend to make the project open-source, consider adding an appropriate license such as MIT.
