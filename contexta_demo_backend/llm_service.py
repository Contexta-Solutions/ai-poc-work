import os
import json
import re
from dotenv import load_dotenv
from anthropic import Anthropic

from clinical_data import TEMPLATE_SECTIONS, BASE_TEMPLATES

load_dotenv()
anthropic_client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY")) if os.environ.get("ANTHROPIC_API_KEY") else None


def _build_slot_catalog() -> str:
    """
    Computed once at import time (clinical_data.py is static/read-only for the
    process lifetime) rather than per-request. Walks every base template's
    sections and lists each fillable "slot"/"rx_slot" item's exact slot_key
    plus the template line/dose pattern it fills, so the extraction prompt can
    reference precise keys instead of a vague "if applicable" instruction.

    Also doubles as a load-time integrity check: slot_keys must be globally
    unique across the whole catalog, so an authoring mistake in clinical_data.py
    fails loudly at import time instead of silently confusing the LLM later.
    """
    blocks = []
    seen_keys = {}
    for template_id, display_name in BASE_TEMPLATES.items():
        sections = TEMPLATE_SECTIONS.get(template_id, {})
        rows = []
        for section_name, items in sections.items():
            for item in items:
                item_type = item.get("type")
                if item_type == "slot":
                    slot_key = item["slot_key"]
                    pattern = item["line"]
                elif item_type == "rx_slot":
                    slot_key = item["slot_key"]
                    pattern = f"{item['drug']} -- {item['dose']}"
                else:
                    continue

                owner = seen_keys.get(slot_key)
                if owner and owner != template_id:
                    raise RuntimeError(
                        f"slot_key '{slot_key}' is used by both {owner} and "
                        f"{template_id} -- slot_keys must be globally unique "
                        f"across TEMPLATE_SECTIONS."
                    )
                seen_keys[slot_key] = template_id
                rows.append(f'    "{slot_key}" -> "{pattern}"  (section: {section_name})')

        if rows:
            blocks.append(f"  {template_id} -- {display_name}:\n" + "\n".join(rows))

    return "\n".join(blocks)


SLOT_CATALOG = _build_slot_catalog()
BASE_TEMPLATE_ID_LIST = ", ".join(f'"{tid}"' for tid in BASE_TEMPLATES)


def extract_clinical_data(voice_note: str) -> dict:
    prompt = f"""
    You are an expert clinical NLP parser driving an Object-Oriented Template Engine.
    Analyze the clinical text and return a strict, minified JSON object mapping structure.

    HOW THE TEMPLATE ENGINE WORKS (read this before extracting anything):
    Every base template already contains a complete, clinically-written set of
    complaint / advice / plan / follow-up-plan / lab / imaging sentences for its
    diagnosis. Each sentence is either:
      - FIXED: renders exactly as written, always, no matter what the dictation says.
      - a SLOT (shown with a blank / "___" in the catalog below): renders ONLY if
        you supply that exact slot_key's value in the "slots" object AND the
        dictation actually states that specific data point. If the doctor never
        mentions it, leave the slot_key out -- the blank sentence is simply
        omitted from the final note. Never invent, estimate, round, or default a
        value that was not explicitly stated.
    Your entire job is: (1) identify which base template the dictation matches,
    (2) fill in the slot_keys the dictation actually gives values for, (3)
    extract any medicines mentioned, and (4) capture genuinely new clinical
    content that has no matching template line as an "extension". You do NOT
    write freeform complaint sentences -- the template already has them.

    IDENTIFICATION MATRICES:
    - Base Identifiers (choose exactly one that best matches the dictation): {BASE_TEMPLATE_ID_LIST}

    SLOT CATALOG (CRITICAL -- the exact, only slot_keys that exist):
{SLOT_CATALOG}

    SLOT-FILLING RULES:
    1. Only use slot_keys that belong to the base_template you identified. Ignore every other template's slot_keys.
    2. Only include a slot_key in "slots" if the dictation explicitly states that value (a number, a duration, a grade, a distance, a score -- whatever the pattern's blank represents).
    3. Copy the value as the doctor stated it (e.g. "2 years", "40", "Grade II") -- do not reformat, convert units, or round.
    4. If a data point is mentioned but doesn't match any slot_key's pattern for the identified template, it is NOT a slot -- put it in "extensions" instead (see below).

    PRESCRIPTION EXTRACTION (CRITICAL):
    You MUST extract ALL medications/prescriptions the doctor mentions DIRECTLY from the dictation, independent of the template's own fixed prescription list (which renders automatically and does not need to be repeated here).
    - Each prescription must be a JSON object with "drug" (medicine name), "dose" (dosage + frequency + duration), and "notes" (any additional instructions).
    - ONLY include medicines the doctor actually prescribed in the dictation. Do NOT add default or assumed medicines.
    - If the doctor says "prescribing Ibuprofen 600mg morning and night after food for 5 days", extract:
      {{"drug": "Tab Ibuprofen 600mg", "dose": "BD x 5 days", "notes": "After food"}}
    - Use standard medical abbreviations: OD (once daily), BD (twice daily), TDS (three times daily), SOS (as needed).
    - If no medicines are mentioned in the dictation, return an empty array.

    EXTENSIONS (CRITICAL -- genuinely new clinical content only):
    Use "extensions" for anything clinically real that the doctor said which has
    NO matching fixed or slot line anywhere in the identified template's catalog
    above. Each extension is {{"section": ..., "item_name": ..., "value": ...}}.
    Valid section names depend on which base_template you identified:
    - ORT-* (orthopaedic) templates: "chief_complaint", "history_complaints",
      "examination_findings", "impression", "management_plan", "lab_orders",
      "imaging_orders", "follow_up_plan".
    - DIA-T2DM / PUL-ASTHMA / PED-ARI: "complaints", "advice", "plan",
      "follow_up_plan".
    Only use section names valid for the template you picked. Do NOT use
    extensions for something a slot_key already covers -- fill the slot instead.

    OUTPUT FORMAT:
    {{
      "base_template": "ORT-TKR",
      "slots": {{"pain_dur": "2 years", "vas": "7"}},
      "prescriptions": [
        {{"drug": "Tab Ibuprofen 600mg", "dose": "BD x 5 days", "notes": "After food"}}
      ],
      "extensions": [
        {{"section": "plan", "item_name": "MRI Right Knee", "value": "Ordered"}},
        {{"section": "lab_orders", "item_name": "Serum Uric Acid", "value": "Ordered -- query gout"}}
      ]
    }}

    1. Output raw JSON only. No markdown, no code fences, no explanation.
    2. "base_template" is MANDATORY -- pick the single best-matching id from the Base Identifiers list above.
    3. "slots" is MANDATORY (can be empty {{}}) -- see SLOT-FILLING RULES above.
    4. "prescriptions" is MANDATORY (can be empty []) -- see PRESCRIPTION EXTRACTION above.
    5. "extensions" is MANDATORY (can be empty []) -- see EXTENSIONS above.
    6. Do NOT output a "complaints" array or any freeform complaint sentences -- complaints are template-driven via "slots" and "extensions", exactly like advice/plan/follow_up_plan.
    7. Do NOT put medicines into extensions -- they belong in "prescriptions".

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
