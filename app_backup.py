import streamlit as st

from src.chatbot.chat_assistant import SCMChatAssistant
from src.chatbot.voice_assistant import run_voice_assistant


st.set_page_config(
    page_title="SCM AI Assistant",
    page_icon="📦",
    layout="wide",
)


st.title("SCM AI Assistant")
st.caption(
    "AI-powered Supply Chain Management assistant"
)


# Keep the chatbot instance across Streamlit reruns.
if "assistant" not in st.session_state:
    st.session_state.assistant = SCMChatAssistant()


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ---------------------------------------------------------
# CHAT HISTORY
# ---------------------------------------------------------

for message in st.session_state.chat_history:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ---------------------------------------------------------
# USER INPUT
# ---------------------------------------------------------

question = st.chat_input(
    "Ask about inventory, demand, or restocking..."
)


if question:

    # Display user message
    st.session_state.chat_history.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    # Generate SCM response
    with st.chat_message("assistant"):

        with st.spinner("Analyzing SCM data..."):

            answer = (
                st.session_state.assistant.ask(
                    question
                )
            )

        st.markdown(answer)

    # Store assistant response
    st.session_state.chat_history.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

with st.sidebar:

    st.header("SCM Assistant")

    st.write(
        "Ask questions about:"
    )

    st.markdown(
        """
        - Inventory
        - Low-stock products
        - Restocking
        - Demand
        - Demand forecasts
        - Warehouse inventory risk
        """
    )

    st.divider()

    if st.button(
        "Clear Conversation",
        use_container_width=True,
    ):

        st.session_state.assistant = (
            SCMChatAssistant()
        )

        st.session_state.chat_history = []

        st.rerun()

    st.divider()

    st.caption(
        "Powered by LangGraph + Groq + Python SCM tools"
    )