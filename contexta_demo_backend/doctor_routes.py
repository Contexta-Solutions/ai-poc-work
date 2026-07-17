"""API routes for the internal Doctor Assistant (/doctor).

Schemas live here rather than in schemas.py so this POC touches exactly one
existing file (main.py, one include_router line). Nothing here is imported by
Visit Notes or the ChatBot.
"""

from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from doctor_service import DOCTOR_NAME, ask_doctor_bot, warm_cache

router = APIRouter()


class DoctorHistoryItem(BaseModel):
    role: str
    content: str


class DoctorAskRequest(BaseModel):
    question: str
    history: List[DoctorHistoryItem] = []


class DoctorAskResponse(BaseModel):
    answer: str
    # Cache telemetry, surfaced so caching can be verified without reading logs.
    # cache_read should be 11592 on every request after the first; a persistent 0
    # means the cached prefix stopped being byte-stable.
    usage: dict


@router.post("/api/doctor/ask", response_model=DoctorAskResponse)
def doctor_ask(request: DoctorAskRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        answer, usage = ask_doctor_bot(question, request.history)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return DoctorAskResponse(answer=answer, usage=usage)


@router.post("/api/doctor/warm")
def doctor_warm():
    """Pre-write the prompt cache. Called by the frontend on mount so the first
    real question doesn't pay for a cold cache. Never fails the page -- a warm
    miss just means the first answer is a little slower."""
    try:
        return {"ok": True, "usage": warm_cache()}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@router.get("/api/doctor/context")
def doctor_context():
    """Who the assistant thinks it is. Lets the UI label itself from one source."""
    return {"doctor": DOCTOR_NAME}
