import tempfile
from pathlib import Path

import streamlit as st

from src.chatbot.chat_assistant import SCMChatAssistant
from src.chatbot.voice_assistant import run_voice_assistant


st.set_page_config(
    page_title="SCM AI Assistant",
    page_icon="📦",
    layout="wide",
)


st.title("SCM AI Assistant")
st.caption("AI-powered Supply Chain Management assistant")


# =========================================================
# SESSION STATE
# =========================================================

if "assistant" not in st.session_state:
    st.session_state.assistant = SCMChatAssistant()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# =========================================================
# DISPLAY CHAT HISTORY
# =========================================================

for message in st.session_state.chat_history:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# =========================================================
# TEXT INPUT
# =========================================================

question = st.chat_input(
    "Ask about inventory, demand, or restocking..."
)


if question:

    st.session_state.chat_history.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):

        with st.spinner("Analyzing SCM data..."):

            answer = st.session_state.assistant.ask(
                question
            )

        st.markdown(answer)

    st.session_state.chat_history.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("SCM Assistant")

    st.write("Ask questions about:")

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

    # =====================================================
    # VOICE INPUT
    # =====================================================

    st.subheader("Voice Input")

    audio_file = st.file_uploader(
        "Upload an audio question",
        type=["m4a", "wav", "mp3"],
    )

    if audio_file is not None:

        if st.button(
            "Process Voice",
            use_container_width=True,
        ):

            temp_path = None

            try:

                suffix = Path(
                    audio_file.name
                ).suffix

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=suffix,
                ) as temp_file:

                    temp_file.write(
                        audio_file.getbuffer()
                    )

                    temp_path = temp_file.name

                with st.spinner(
                    "Converting speech to text..."
                ):

                    transcript, answer = (
                        run_voice_assistant(
                            temp_path
                        )
                    )

                if transcript:

                    st.session_state.chat_history.append(
                        {
                            "role": "user",
                            "content": (
                                f"**Voice question:** "
                                f"{transcript}"
                            ),
                        }
                    )

                st.session_state.chat_history.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )

                st.success(
                    "Voice question processed successfully."
                )

                st.rerun()

            except Exception as exc:

                st.error(
                    f"Voice processing failed: {exc}"
                )

            finally:

                if temp_path:

                    Path(temp_path).unlink(
                        missing_ok=True
                    )

    st.divider()

    # =====================================================
    # CLEAR CONVERSATION
    # =====================================================

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