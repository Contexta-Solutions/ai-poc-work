"""
Translate a clinical note into Telugu or Hindi for printing.

Deliberately does NOT translate drug names or compositions. A pharmacist reads
those off the printout, and transliterating "Etoricoxib" into Telugu script is a
dispensing-error risk. Same for ICD-10 codes, dose codes (1-0-0-0), numbers,
dates and units -- they stay in Latin/ASCII and are protected by the prompt.
"""

import json
import os
import re

from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
_client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY")) if os.environ.get("ANTHROPIC_API_KEY") else None

LANGUAGE_NAMES = {"te": "Telugu", "hi": "Hindi"}

# Prescription fields that get translated. `drug` and `composition` are absent
# on purpose -- see the module docstring.
RX_TRANSLATABLE = ("dosage", "frequency", "duration", "instructions")


def _collect(doc: dict):
    """Every string in the document that should be translated, with a pointer
    back to where it came from so we can put the translation back."""
    slots = []  # (section, index, field, text)
    for section, items in (doc or {}).items():
        if not items:
            continue
        for i, item in enumerate(items):
            if section == "prescription":
                for field in RX_TRANSLATABLE:
                    text = str(item.get(field, "") or "").strip()
                    if text:
                        slots.append((section, i, field, text))
            else:
                text = str(item.get("rendered_line", "") or "").strip()
                if text:
                    slots.append((section, i, "rendered_line", text))
    return slots


def _parse_json_array(raw: str, expected: int):
    raw = raw.strip()
    try:
        out = json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\[.*\]", raw, re.DOTALL)
        if not m:
            raise RuntimeError("Translator did not return a JSON array")
        out = json.loads(m.group(0))

    if not isinstance(out, list) or len(out) != expected:
        raise RuntimeError(
            f"Translator returned {len(out) if isinstance(out, list) else '?'} items, expected {expected}"
        )
    return [str(x) for x in out]


def translate_document(doc: dict, language: str) -> dict:
    """
    Return a copy of `doc` with its text translated into `language` ("te"/"hi").
    Anything else (including "en") is returned untouched.
    """
    if language not in LANGUAGE_NAMES:
        return doc
    if not _client:
        raise RuntimeError("ANTHROPIC_API_KEY environment variable is missing.")

    slots = _collect(doc)
    if not slots:
        return doc

    target = LANGUAGE_NAMES[language]
    payload = json.dumps([text for (_, _, _, text) in slots], ensure_ascii=False, indent=0)

    prompt = f"""Translate each string in this JSON array from English into {target}.

    RULES:
    1. Return ONLY a JSON array of {len(slots)} strings, in the same order. No commentary, no code fences.
    2. Translate the medical meaning naturally, the way a doctor would write it for a patient to read. Do not translate word-for-word.
    3. KEEP THESE IN LATIN SCRIPT / ASCII EXACTLY AS THEY APPEAR -- never transliterate them into {target} script:
       - Drug and brand names (Etoricoxib, Ultracet, Pantoprazole, ...)
       - Chemical / composition names (Tramadol 37.5mg + Paracetamol 325mg)
       - ICD-10 codes (M17.9, S83.511A)
       - Dose-frequency codes (1-0-0-0, 1-0-1-0, SOS)
       - All digits 0-9, dates (2026-07-22), clock times (09:00 AM)
       - Units and abbreviations: mg, ml, IU, OD, BD, TDS, ROM, VAS, MRI, X-ray, ECG, CBC, ESR, CRP, HbA1c, NCV, USG
       - Anatomical grades written in Roman numerals (Grade IV)
    4. Everything else -- the surrounding words, instructions, findings, advice -- must be translated into {target}.
    5. A blank "___" in a string means a value the doctor did not fill in. Keep the "___" exactly as it is.

    Example ({target}): "Tab Etoricoxib 90mg" stays as-is; "1 tablet" and "After food" get translated; "1-0-0-0 (Morning only)" keeps the code and translates only the words in brackets.

    JSON array to translate:
    {payload}
    """

    response = _client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8000,
        temperature=0.0,
        system=f"You are a precise medical translator (English -> {target}). You output ONLY a valid JSON array of strings, never anything else.",
        messages=[{"role": "user", "content": prompt}],
    )

    translations = _parse_json_array(response.content[0].text, len(slots))

    # Deep-ish copy: new lists and new item dicts, so we never mutate the caller's
    # document (or, via it, the shared template data).
    out = {section: [dict(item) for item in items] for section, items in (doc or {}).items()}
    for (section, i, field, _), translated in zip(slots, translations):
        out[section][i][field] = translated

    return out
