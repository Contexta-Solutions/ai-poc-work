from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class NoteRequest(BaseModel):
    voice_note: str

class PDFRequest(BaseModel):
    visit_date: str
    doctor: str
    patient: str = ""
    template_id: str = ""
    # "en" | "te" | "hi". Non-English notes are translated before rendering.
    language: str = "en"
    # The document exactly as it stands on screen, edits included.
    clinical_data: Dict[str, Any]

# ─── ChatBot Schemas ───

class HistoryItem(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[HistoryItem] = []
    # Language Whisper detected on the user's latest voice message ("en"/"te").
    # None for typed messages, or when detection was inconclusive.
    language: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str