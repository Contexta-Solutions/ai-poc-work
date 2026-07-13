import os
import json
import re
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
anthropic_client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY")) if os.environ.get("ANTHROPIC_API_KEY") else None

def extract_clinical_data(voice_note: str) -> dict:
    prompt = f"""
    You are an expert clinical NLP parser driving an Object-Oriented Template Engine.
    Analyze the clinical text and return a strict, minified JSON object mapping structure.

    IDENTIFICATION MATRICES:
    - Base Identifiers: "ORT-TKR", "DIA-T2DM", "PUL-ASTHMA", "PED-ARI".

    COMPLAINTS EXTRACTION (CRITICAL):
    You MUST extract the patient's presenting complaints DIRECTLY from the doctor's dictation.
    - Read the dictation carefully and identify every symptom, finding, or complaint the doctor mentions.
    - Output each complaint as a concise, clinical sentence in the "complaints" array.
    - ONLY include complaints that the doctor actually mentioned in the dictation. Do NOT invent or assume complaints.
    - Examples: "Right knee pain after twisting injury", "Immediate swelling noted", "Unable to bear weight"

    PRESCRIPTION EXTRACTION (CRITICAL):
    You MUST extract ALL medications/prescriptions the doctor mentions DIRECTLY from the dictation.
    - Each prescription must be a JSON object with "drug" (medicine name), "dose" (dosage + frequency + duration), and "notes" (any additional instructions).
    - ONLY include medicines the doctor actually prescribed in the dictation. Do NOT add default or assumed medicines.
    - If the doctor says "prescribing Ibuprofen 600mg morning and night after food for 5 days", extract:
      {{"drug": "Tab Ibuprofen 600mg", "dose": "BD × 5 days", "notes": "After food"}}
    - Use standard medical abbreviations: OD (once daily), BD (twice daily), TDS (three times daily), SOS (as needed).
    - If no medicines are mentioned in the dictation, return an empty array.

    OUTPUT FORMAT:
    {{
      "base_template": "ORT-TKR",
      "complaints": [
        "Right knee pain after twisting injury",
        "Immediate swelling noted"
      ],
      "prescriptions": [
        {{"drug": "Tab Ibuprofen 600mg", "dose": "BD × 5 days", "notes": "After food"}},
        {{"drug": "Tab Pantoprazole 40mg", "dose": "OD", "notes": "Gastro-protection"}}
      ],
      "slots": {{}},
      "extensions": [
        {{"section": "plan", "item_name": "MRI Right Knee", "value": "Ordered"}},
        {{"section": "advice", "item_name": "Weight bearing", "value": "As tolerated with crutches"}}
      ]
    }}

    1. Output raw JSON only. No markdown, no code fences, no explanation.
    2. The "complaints" array is MANDATORY — extract ALL presenting complaints from the dictation text.
    3. The "prescriptions" array is MANDATORY — extract ALL medicines the doctor prescribed from the dictation. If none mentioned, use empty array.
    4. Unmapped items that are NOT complaints or prescriptions go to extensions (e.g. extra advice, plan items, follow-up instructions).
    5. Do NOT put complaints into extensions — they MUST go in the "complaints" array.
    6. Do NOT put medicines into extensions — they MUST go in the "prescriptions" array.
    7. "slots" can contain extracted values for template blanks (e.g. duration, scores) if applicable.

    Clinical Text Input:
    "{voice_note}"
    """

    if not anthropic_client:
        raise RuntimeError("ANTHROPIC_API_KEY environment variable is missing.")
        
    try:
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            temperature=0.0,
            system="You are a precise clinical schema JSON mapping instrument. Output ONLY valid JSON with no markdown formatting, no code fences, and no surrounding text.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        raw_text = response.content[0].text.strip()
        
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            pass
        
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        
        first_brace = raw_text.find('{')
        last_brace = raw_text.rfind('}')
        if first_brace != -1 and last_brace != -1:
            return json.loads(raw_text[first_brace:last_brace + 1])
        
        raise RuntimeError("Could not parse JSON from Claude response")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON from Claude: {str(e)}")
    except Exception as e:
        if "RuntimeError" in type(e).__name__:
            raise
        raise RuntimeError(f"Anthropic Pipeline Fault: {str(e)}")