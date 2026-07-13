import os
import httpx
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_TRANSCRIPTION_URL = "https://api.groq.com/openai/v1/audio/transcriptions"

# whisper-large-v3, NOT -turbo. Turbo is a distilled model whose accuracy drops
# most on low-resource languages, and Telugu is already one of Whisper's weaker
# ones. The small extra latency is worth it for a bilingual EN/TE assistant.
WHISPER_MODEL = "whisper-large-v3"

# Whisper will confidently "detect" Hindi/Kannada/Sanskrit from a short or noisy
# Telugu clip. Anything outside the two languages this app actually speaks is
# treated as *undetected* rather than trusted, so the caller can fall back to
# whatever language the conversation was already in.
_LANGUAGE_ALIASES = {
    "en": "en", "english": "en",
    "te": "te", "telugu": "te",
}


def _normalize_language(raw: str) -> str | None:
    """Whisper's verbose_json reports a language *name* ("telugu"), not an ISO
    code. Map both forms onto our codes; return None for anything unsupported."""
    if not raw:
        return None
    return _LANGUAGE_ALIASES.get(raw.strip().lower())


async def transcribe_audio(
    audio_bytes: bytes,
    filename: str = "audio.webm",
    language: str | None = None,
) -> tuple[str, str | None]:
    """
    Send audio to Groq's Whisper API.

    language: "en" / "te" to force a language, or None to let Whisper auto-detect.
    Returns (text, detected_language). detected_language is None when Whisper
    reported a language this app doesn't support.
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

    # verbose_json (not json) so Whisper tells us which language it heard.
    form = {
        "model": WHISPER_MODEL,
        "response_format": "verbose_json",
        "temperature": "0",
    }
    normalized = _normalize_language(language) if language else None
    if normalized:
        form["language"] = normalized

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            GROQ_TRANSCRIPTION_URL,
            headers=headers,
            files={
                "file": (filename, audio_bytes, content_type),
            },
            data=form,
        )

        if response.status_code != 200:
            raise RuntimeError(f"Groq Whisper error ({response.status_code}): {response.text}")

        result = response.json()
        text = result.get("text", "").strip()
        detected = _normalize_language(result.get("language", ""))
        return text, detected
