from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import Optional
import io

from schemas import NoteRequest, PDFRequest
from llm_service import extract_clinical_data
from speech_service import transcribe_audio
from engine import ClinicalTemplate
from pdf_service import create_emr_pdf

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.post("/api/transcribe")
async def transcribe(file: UploadFile = File(...), language: Optional[str] = Form(None)):
    """
    Receives audio from the browser and returns transcribed text via Groq Whisper.

    `language` ("en"/"te") forces a language; omit it to let Whisper auto-detect.
    The detected language is returned so the caller can keep replying in kind --
    it is None when Whisper heard something this app doesn't support.
    """
    try:
        audio_bytes = await file.read()
        if len(audio_bytes) < 100:
            raise HTTPException(status_code=400, detail="Audio file too short or empty.")

        text, detected_language = await transcribe_audio(
            audio_bytes, filename=file.filename or "audio.webm", language=language
        )

        if not text.strip():
            raise HTTPException(status_code=400, detail="No speech detected in the audio.")

        return {"text": text, "language": detected_language}
    except RuntimeError as re:
        raise HTTPException(status_code=503, detail=str(re))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")



@router.post("/api/parse-note")
async def parse_note(req: NoteRequest):
    if not req.voice_note.strip():
        raise HTTPException(status_code=400, detail="Empty text stream.")

    try:
        extracted_data = extract_clinical_data(req.voice_note)
        template = ClinicalTemplate(extracted_data.get("base_template"))

        # Set prescriptions from dictation extraction/ If not mentioned use standard template one
        template.set_prescriptions(extracted_data.get("prescriptions", []))
        
        for override in extracted_data.get("overrides", []):
            if override.get("variant_template") and override.get("section"):
                template.override_section(override["variant_template"], override["section"])
            
        template.fill_slots(extracted_data.get("slots", {}))
        
        for ext in extracted_data.get("extensions", []):
            if ext.get("section") and ext.get("item_name"):
                template.extend_section(ext["section"], {"item_name": ext["item_name"], "value": ext.get("value", "")})
            
        return template.export()

    except RuntimeError as re:
        raise HTTPException(status_code=503, detail=str(re))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/generate-pdf")
async def generate_pdf(req: PDFRequest):
    try:
        pdf_bytes = create_emr_pdf(req.model_dump())
        return StreamingResponse(
            io.BytesIO(pdf_bytes), media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="EMR.pdf"'}
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))