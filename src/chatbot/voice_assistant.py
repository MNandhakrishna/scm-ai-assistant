from pathlib import Path

from langchain_core.messages import HumanMessage

from src.speech.speech_to_text import transcribe_audio
from src.agents.graph import scm_graph


def run_voice_assistant(audio_file):
    """
    Complete voice-to-SCM workflow:

    Audio → Speech-to-Text → LangGraph → SCM response
    """

    audio_path = Path(audio_file)

    if not audio_path.exists():
        raise FileNotFoundError(
            f"Audio file not found: {audio_path}"
        )

    print("\n=== SPEECH-TO-TEXT ===\n")

    transcript = transcribe_audio(audio_path)

    print(transcript)

    print("\n=== SCM AI ASSISTANT ===\n")

    result = scm_graph.invoke(
        {
            "messages": [
                HumanMessage(content=transcript)
            ]
        }
    )

    # Find the final AI response.
    for message in reversed(result["messages"]):

        if getattr(message, "type", None) == "ai":
            if message.content:
                return transcript, message.content

    return transcript, "No response was generated."


if __name__ == "__main__":

    audio_file = "data/test_audio.m4a"

    transcript, response = run_voice_assistant(audio_file)

    print("\n=== TRANSCRIPT ===\n")
    print(transcript)

    print("\n=== FINAL SCM RESPONSE ===\n")
    print(response)