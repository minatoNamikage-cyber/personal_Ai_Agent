import asyncio
import streamlit as st

from chatbot import chat


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Eran",
    page_icon="🤖",
    layout="centered"
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        max-width: 900px;
        padding-top: 2rem;
        padding-bottom: 5rem;
    }

    .eran-title {
        text-align: center;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .eran-subtitle {
        text-align: center;
        color: #888;
        font-size: 0.95rem;
        margin-bottom: 2rem;
    }

    .tool-used {
        font-size: 0.75rem;
        color: #888;
        margin-top: 8px;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="eran-title">🤖 Eran</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="eran-subtitle">'
    'Your Personal AI Assistant'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================
# CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    role = message.get("role", "assistant")
    content = message.get("content", "")

    with st.chat_message(role):
        st.write(content)


# ============================================================
# CHAT INPUT
# ============================================================

user_input = st.chat_input("Message Eran")


# ============================================================
# PROCESS USER MESSAGE
# ============================================================

if user_input:

    # --------------------------------------------------------
    # Save user message
    # --------------------------------------------------------

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # --------------------------------------------------------
    # Show user message
    # --------------------------------------------------------

    with st.chat_message("user"):
        st.write(user_input)

    # --------------------------------------------------------
    # AI RESPONSE
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:

                # Run async chatbot
                response = asyncio.run(
                    chat(user_input)
                )

                # ------------------------------------------------
                # Result
                # ------------------------------------------------

                result = response.get(
                    "result",
                    "I couldn't generate a response."
                )

                # ------------------------------------------------
                # Tools
                # ------------------------------------------------

                tool_names = response.get(
                    "tool_names",
                    []
                )

                # ------------------------------------------------
                # Display result
                # ------------------------------------------------

                st.write(result)

                # ------------------------------------------------
                # Show tools used
                # ------------------------------------------------

                if tool_names:

                    st.markdown(
                        '<div class="tool-used">'
                        '🔧 Tools Used: '
                        + ", ".join(tool_names)
                        + '</div>',
                        unsafe_allow_html=True
                    )

                # ------------------------------------------------
                # Save assistant message
                # ------------------------------------------------

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result
                })

            except Exception as e:

                st.error("❌ Eran Error")

                # Show complete error
                st.exception(e)