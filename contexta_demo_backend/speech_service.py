import os
import httpx
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_TRANSCRIPTION_URL = "https://api.groq.com/openai/v1/audio/transcriptions"

async def transcribe_audio(audio_bytes: bytes, filename: str = "audio.webm") -> str:
    """
    Sends audio to Groq's Whisper API for transcription.
    Uses whisper-large-v3-turbo for fast, cheap, accurate results.
    Free tier: no credit card needed, no token cost.
    """
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY environment variable is missing.")

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
    }

    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "webm"
    content_type_map = {
        "webm": "audio/webm",
        "ogg": "audio/ogg",
        "mp3": "audio/mpeg",
        "wav": "audio/wav",
        "m4a": "audio/m4a",
        "mp4": "audio/mp4",
        "flac": "audio/flac",
    }
    content_type = content_type_map.get(ext, "audio/webm")

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            GROQ_TRANSCRIPTION_URL,
            headers=headers,
            files={
                "file": (filename, audio_bytes, content_type),
            },
            data={
                "model": "whisper-large-v3-turbo",
                "response_format": "json",
                "language": "en",
            },
        )

        if response.status_code != 200:
            raise RuntimeError(f"Groq Whisper error ({response.status_code}): {response.text}")

        result = response.json()
        return result.get("text", "").strip()
