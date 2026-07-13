from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class NoteRequest(BaseModel):
    voice_note: str

class PDFRequest(BaseModel):
    visit_date: str
    doctor: str
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