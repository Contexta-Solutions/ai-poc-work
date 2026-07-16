from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import Optional
import io

from schemas import NoteRequest, PDFRequest
from llm_service import extract_clinical_data
from speech_service import transcribe_audio
from engine import ClinicalTemplate
from pdf_service import create_emr_pdf
from translate_service import translate_document
from doctors_data import DOCTORS
from clinical_data import BASE_TEMPLATES, SAMPLE_DICTATIONS

router = APIRouter()

# Section order + labels for the Template Library preview. Mirrors the ortho
# templates' own structure. "diagnosis" is intentionally absent -- its single
# ICD-10 line is surfaced as the card subtitle instead of a full section.
_LIBRARY_SECTIONS = [
    ("chief_complaint", "Chief Complaint"),
    ("history_complaints", "History & Complaints"),
    ("examination_findings", "Examination & Findings"),
    ("impression", "Impression / Diagnosis"),
    ("management_plan", "Management Plan"),
    ("prescription", "Prescription (Rx)"),
    ("lab_orders", "Lab Orders"),
    ("imaging_orders", "Imaging Orders"),
    ("follow_up_plan", "Follow-up Plan"),
]

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

@router.get("/api/doctors")
async def list_doctors():
    """Doctor roster, so the Visit Notes doctor picker uses the same source of
    truth as the ChatBot instead of hardcoding its own list."""
    return {"doctors": DOCTORS}


@router.get("/api/templates")
async def list_templates():
    """
    The 15 orthopaedic base templates, fully rendered, for the Template Library.

    Built by running each template through the SAME engine that produces a live
    note (ClinicalTemplate.export()), so the preview can never drift from what a
    dictation actually renders. Unfilled slots keep their "___" blank, which the
    UI highlights as a dictatable field. Non-ortho (DIA/PUL/PED) templates and
    variant/override sub-ids (e.g. ORT-TKR-RX-PF) are excluded.
    """
    templates = []
    for template_id, name in BASE_TEMPLATES.items():
        if not template_id.startswith("ORT-"):
            continue

        document = ClinicalTemplate(template_id).export()["document"]

        diagnosis_items = document.get("diagnosis") or []
        icd10 = diagnosis_items[0].get("rendered_line", "") if diagnosis_items else ""

        sections = []
        slot_count = 0
        rx_count = 0
        for key, label in _LIBRARY_SECTIONS:
            items = document.get(key) or []
            if not items:
                continue

            if key == "prescription":
                rx = [{
                    "drug": it.get("drug", ""),
                    "composition": it.get("composition", ""),
                    "dosage": it.get("dosage", ""),
                    "frequency": it.get("frequency", ""),
                    "duration": it.get("duration", ""),
                    "instructions": it.get("instructions", ""),
                } for it in items]
                rx_count = len(rx)
                sections.append({"key": key, "label": label, "kind": "rx", "items": rx})
            else:
                lines = []
                for it in items:
                    is_slot = it.get("type") in ("slot", "rx_slot")
                    if is_slot:
                        slot_count += 1
                    lines.append({"text": it.get("rendered_line", ""), "slot": is_slot})
                sections.append({"key": key, "label": label, "kind": "lines", "items": lines})

        templates.append({
            "id": template_id,
            "name": name,
            "icd10": icd10,
            "slot_count": slot_count,
            "rx_count": rx_count,
            "sample_dictation": SAMPLE_DICTATIONS.get(template_id, ""),
            "sections": sections,
        })

    return {"templates": templates}


@router.post("/api/generate-pdf")
async def generate_pdf(req: PDFRequest):
    """
    Render the note as a PDF in English, Telugu or Hindi.

    The frontend posts the document as it currently stands on screen, so any
    edits the doctor made are what gets printed. For a non-English language the
    text is translated first (drug names and codes are left in Latin).
    """
    try:
        payload = req.model_dump()

        if payload.get("language") in ("te", "hi"):
            payload["clinical_data"] = translate_document(
                payload.get("clinical_data") or {}, payload["language"]
            )

        pdf_bytes = create_emr_pdf(payload)

        lang = payload.get("language", "en")
        filename = f"EMR_{payload.get('visit_date', '')}_{lang}.pdf".replace(" ", "_")
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except RuntimeError as re:
        raise HTTPException(status_code=503, detail=str(re))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))