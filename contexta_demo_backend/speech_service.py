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

# Whisper reports the language either as an ISO code or as an English name,
# depending on the endpoint. Accept both forms of the only two we speak.
_LANGUAGE_ALIASES = {
    "en": "en", "english": "en",
    "te": "te", "telugu": "te",
}


def _normalize_language(raw: str) -> str | None:
    """Map Whisper's reported language onto our codes. None = not a language
    this assistant speaks."""
    if not raw:
        return None
    return _LANGUAGE_ALIASES.get(raw.strip().lower())


async def _call_whisper(audio_bytes: bytes, filename: str, language: str | None) -> tuple[str, str]:
    """One Whisper call. Returns (text, raw_language_reported_by_whisper)."""
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY environment variable is missing.")

    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}

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
    if language:
        form["language"] = language

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            GROQ_TRANSCRIPTION_URL,
            headers=headers,
            files={"file": (filename, audio_bytes, content_type)},
            data=form,
        )

        if response.status_code != 200:
            raise RuntimeError(f"Groq Whisper error ({response.status_code}): {response.text}")

        result = response.json()
        return result.get("text", "").strip(), str(result.get("language", "")).strip().lower()


async def transcribe_audio(
    audio_bytes: bytes,
    filename: str = "audio.webm",
    language: str | None = None,
) -> tuple[str, str | None]:
    """
    Transcribe audio via Groq Whisper, constrained to the two languages this
    assistant actually speaks (English and Telugu).

    Whisper's language ID is unreliable for Telugu: it routinely hears Telugu
    speech as Gujarati, Hindi or Kannada, and then writes the Telugu words out
    in THAT language's script -- e.g. "kavali" (కావాలి, "I want") comes back as
    "કાવાલી" or "कावाली". The words are right, the script is wrong, and every
    downstream step then treats the patient as a Gujarati/Hindi speaker.

    Since only English and Telugu are supported, anything Whisper detects that
    isn't English is re-transcribed with Telugu forced, which puts the text back
    into Telugu script. That costs a second call only when detection went wrong.

    `language` ("en"/"te") skips detection entirely and forces that language --
    Visit Notes uses this to pin clinical dictation to English.

    Returns (text, language) where language is always "en" or "te".
    """
    forced = _normalize_language(language) if language else None
    if forced:
        text, _ = await _call_whisper(audio_bytes, filename, forced)
        return text, forced

    text, detected_raw = await _call_whisper(audio_bytes, filename, None)
    detected = _normalize_language(detected_raw)

    # Whisper is reliable at spotting English, so trust that.
    if detected == "en":
        return text, "en"

    # It already said Telugu -- the text is in Telugu script, nothing to redo.
    if detected == "te":
        return text, "te"

    # Anything else (gujarati / hindi / kannada / ...) is a misdetection: this
    # assistant has no other languages. Redo it as Telugu to recover the script.
    text, _ = await _call_whisper(audio_bytes, filename, "te")
    return text, "te"
