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

class ChatResponse(BaseModel):
    reply: str