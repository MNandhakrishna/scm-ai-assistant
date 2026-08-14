import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

from src.utils.logger import get_logger


logger = get_logger(__name__)


load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY was not found in the .env file.")

client = Groq(api_key=api_key)


def transcribe_audio(audio_file):
    """
    Convert an audio file into text using Groq Whisper.
    """

    audio_path = Path(audio_file)

    if not audio_path.exists():

        logger.error(
            "Audio file not found: %s",
            audio_path,
        )

        raise FileNotFoundError(
            f"Audio file not found: {audio_path}"
        )

    logger.info(
        "Starting audio transcription: %s",
        audio_path.name,
    )

    try:

        with open(audio_path, "rb") as file:

            transcription = client.audio.transcriptions.create(
                file=file,
                model="whisper-large-v3-turbo",
                response_format="json",
            )

        logger.info(
            "Audio transcription completed successfully"
        )

        return transcription.text

    except Exception:

        logger.exception(
            "Audio transcription failed"
        )

        raise


if __name__ == "__main__":

    audio_file = "data/test_audio.m4a"

    text = transcribe_audio(audio_file)

    print("\n=== TRANSCRIPTION ===\n")
    print(text)