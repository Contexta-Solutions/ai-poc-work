"""
Indian / Contexta-specific PHI recognizers for Presidio.

Presidio ships PERSON, LOCATION, DATE_TIME, EMAIL_ADDRESS, PHONE_NUMBER, URL and
IP_ADDRESS. Everything an Indian clinic actually keys off — Aadhaar, PAN, ABHA,
UHID, PIN codes — it does not. That gap is this module.

Design notes:
  * Scores are deliberate, not decorative. A checksum-validated Aadhaar is 0.9;
    a bare 6-digit PIN code starts at 0.25 and only clears the threshold when a
    context word ("pin", "pincode") sits nearby. Presidio adds ~0.35 for context.
  * `validate_result` is Presidio's hook for post-regex validation. Returning
    True promotes the score, False discards the match outright, None leaves it.
    Aadhaar and PAN use it; that's what makes them safe to trust at high scores.
  * Every recognizer here is independently testable — see tests/test_recognizers.py.
    Do not raise a score without a test that justifies it.
"""

import re

from presidio_analyzer import LocalRecognizer, Pattern, PatternRecognizer, RecognizerResult

# --------------------------------------------------------------------------
# Verhoeff checksum — used by Aadhaar.
#
# Without it, `\b[2-9]\d{11}\b` matches any 12-digit number: order IDs, bill
# numbers, timestamps. The checksum takes false positives to ~1-in-10.
# --------------------------------------------------------------------------

_D = (
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
    (1, 2, 3, 4, 0, 6, 7, 8, 9, 5),
    (2, 3, 4, 0, 1, 7, 8, 9, 5, 6),
    (3, 4, 0, 1, 2, 8, 9, 5, 6, 7),
    (4, 0, 1, 2, 3, 9, 5, 6, 7, 8),
    (5, 9, 8, 7, 6, 0, 4, 3, 2, 1),
    (6, 5, 9, 8, 7, 1, 0, 4, 3, 2),
    (7, 6, 5, 9, 8, 2, 1, 0, 4, 3),
    (8, 7, 6, 5, 9, 3, 2, 1, 0, 4),
    (9, 8, 7, 6, 5, 4, 3, 2, 1, 0),
)

_P = (
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
    (1, 5, 7, 6, 2, 8, 3, 0, 9, 4),
    (5, 8, 0, 3, 7, 9, 6, 1, 4, 2),
    (8, 9, 1, 6, 0, 4, 3, 5, 2, 7),
    (9, 4, 5, 3, 1, 2, 6, 8, 7, 0),
    (4, 2, 8, 6, 5, 7, 3, 9, 0, 1),
    (2, 7, 9, 3, 8, 0, 6, 4, 1, 5),
    (7, 0, 4, 6, 9, 1, 3, 2, 5, 8),
)

_INV = (0, 4, 3, 2, 1, 5, 6, 7, 8, 9)


def verhoeff_valid(digits: str) -> bool:
    """True if `digits` (check digit included) passes Verhoeff."""
    if not digits.isdigit():
        return False
    c = 0
    for i, d in enumerate(reversed(digits)):
        c = _D[c][_P[i % 8][int(d)]]
    return c == 0


def verhoeff_check_digit(digits: str) -> int:
    """Check digit for a payload WITHOUT one. Used by the tests to build valid samples."""
    c = 0
    for i, d in enumerate(reversed(digits)):
        c = _D[c][_P[(i + 1) % 8][int(d)]]
    return _INV[c]


# --------------------------------------------------------------------------
# Recognizers
# --------------------------------------------------------------------------


class AadhaarRecognizer(PatternRecognizer):
    """
    12 digits, first digit 2-9 (0 and 1 are never issued). Commonly written
    `1234 5678 9012` or `1234-5678-9012`. Verhoeff-validated.
    """

    ENTITY = "IN_AADHAAR"

    def __init__(self) -> None:
        super().__init__(
            supported_entity=self.ENTITY,
            patterns=[
                Pattern(
                    name="aadhaar_grouped",
                    regex=r"\b[2-9]\d{3}[\s-]?\d{4}[\s-]?\d{4}\b",
                    score=0.5,  # promoted to 1.0 by validate_result on checksum pass
                )
            ],
            context=["aadhaar", "aadhar", "uidai", "uid"],
        )

    def validate_result(self, pattern_text: str):
        digits = "".join(ch for ch in pattern_text if ch.isdigit())
        if len(digits) != 12:
            return False
        return verhoeff_valid(digits)


class PanRecognizer(PatternRecognizer):
    """
    Permanent Account Number: 5 letters, 4 digits, 1 letter (AAAAA9999A).
    The 4th character encodes holder type; 'P' = individual, which is what a
    patient record would carry. Structurally rigid, so false positives are rare.
    """

    ENTITY = "IN_PAN"
    _HOLDER_TYPES = set("ABCFGHLJPTK")

    def __init__(self) -> None:
        super().__init__(
            supported_entity=self.ENTITY,
            patterns=[Pattern(name="pan", regex=r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", score=0.6)],
            context=["pan", "permanent account", "income tax"],
        )

    def validate_result(self, pattern_text: str):
        if len(pattern_text) != 10:
            return False
        return pattern_text[3] in self._HOLDER_TYPES


class AbhaNumberRecognizer(PatternRecognizer):
    """
    ABHA (Ayushman Bharat Health Account) number: 14 digits, conventionally
    written `12-3456-7890-1234`. The primary patient identifier under ABDM —
    neither Presidio nor Azure ships a recognizer for it.
    """

    ENTITY = "IN_ABHA_NUMBER"

    def __init__(self) -> None:
        super().__init__(
            supported_entity=self.ENTITY,
            patterns=[
                Pattern(
                    name="abha_hyphenated",
                    regex=r"\b\d{2}-\d{4}-\d{4}-\d{4}\b",
                    score=0.85,  # the hyphen grouping is distinctive on its own
                ),
                Pattern(
                    name="abha_plain",
                    regex=r"\b\d{14}\b",
                    score=0.3,  # bare 14 digits needs context to clear threshold
                ),
            ],
            context=["abha", "health id", "ayushman", "abdm"],
        )


class AbhaAddressRecognizer(PatternRecognizer):
    """ABHA address — a handle, not an email: `ramesh.kumar@abdm`, `xyz@sbx`."""

    ENTITY = "IN_ABHA_ADDRESS"

    def __init__(self) -> None:
        super().__init__(
            supported_entity=self.ENTITY,
            patterns=[
                Pattern(
                    name="abha_address",
                    regex=r"\b[A-Za-z0-9._-]{3,}@(?:abdm|sbx)\b",
                    score=0.9,
                )
            ],
            context=["abha", "health id", "abdm"],
        )


class IndianPhoneRecognizer(PatternRecognizer):
    """
    Indian mobile: 10 digits starting 6-9, optional +91/0 prefix and internal
    spacing. Presidio's PHONE_NUMBER needs region="IN" and still misses the
    loose `98765 43210` spacing that clinic notes are full of.
    """

    ENTITY = "IN_PHONE"

    def __init__(self) -> None:
        super().__init__(
            supported_entity=self.ENTITY,
            patterns=[
                Pattern(
                    name="in_mobile_prefixed",
                    regex=r"(?:\+?91[\s-]?|\b0)?[6-9]\d{4}[\s-]?\d{5}\b",
                    score=0.65,
                ),
            ],
            context=["phone", "mobile", "contact", "ph", "cell", "tel", "whatsapp"],
        )


class IndianPinCodeRecognizer(PatternRecognizer):
    """
    6-digit postal code, first digit 1-9.

    Deliberately scored below Presidio's default 0.35 threshold: a bare 6-digit
    number is far more likely to be a bill amount or a lab value. Only a nearby
    context word ("pin", "pincode", "postal") lifts it into range. Raising this
    base score without adding context is the fastest way to wreck precision.
    """

    ENTITY = "IN_PIN_CODE"

    def __init__(self) -> None:
        super().__init__(
            supported_entity=self.ENTITY,
            patterns=[Pattern(name="pin_code", regex=r"\b[1-9]\d{5}\b", score=0.25)],
            context=["pin", "pincode", "pin code", "postal", "post code", "zip"],
        )


class ContextaUhidRecognizer(PatternRecognizer):
    """
    Contexta's own MRN plus the generic `UHID: <value>` label seen on lab reports.
    This is the class of identifier no vendor model can know about — it is the
    single strongest argument for a custom recognizer layer.
    """

    ENTITY = "IN_UHID"

    def __init__(self) -> None:
        super().__init__(
            supported_entity=self.ENTITY,
            patterns=[
                Pattern(name="contexta_mrn", regex=r"\bCTX-\d{6}\b", score=0.95),
                Pattern(
                    name="labelled_uhid",
                    regex=r"(?i)\b(?:UHID|MRN|MR\s*No\.?|Patient\s*ID|TID/SID)\s*[:\-]?\s*([A-Z]{0,4}[-/]?\d{4,12})\b",
                    score=0.8,
                ),
                # Lab-issued record numbers: letter prefix + long digit run.
                # On the Tenet report `UMR2162620/` was detected as ORGANIZATION,
                # which is the right span for the wrong reason -- it is an ID.
                Pattern(
                    name="prefixed_record_no",
                    regex=r"\b(?:UMR|UHID|MRN|SID|TID|LAB|ACC)[-/]?\d{5,12}\b",
                    score=0.85,
                ),
            ],
            context=["uhid", "mrn", "medical record", "patient id", "hospital no",
                     "tid", "sid", "lab no"],
        )


class VehicleRegistrationRecognizer(PatternRecognizer):
    """Indian vehicle plate: TS09AB1234, MH-12-AB-1234. HIPAA identifier #12."""

    ENTITY = "IN_VEHICLE_REG"

    def __init__(self) -> None:
        super().__init__(
            supported_entity=self.ENTITY,
            patterns=[
                Pattern(
                    name="vehicle_reg",
                    regex=r"\b[A-Z]{2}[\s-]?\d{1,2}[\s-]?[A-Z]{1,3}[\s-]?\d{4}\b",
                    score=0.6,
                )
            ],
            context=["vehicle", "registration", "reg no", "car", "ambulance"],
        )


class InsurancePolicyRecognizer(PatternRecognizer):
    """
    Health plan / TPA identifiers. Formats vary per insurer, so this leans on
    context rather than trying to enumerate them: a slash-separated alphanumeric
    run near the word "policy" is the reliable signal. HIPAA identifier #9.
    """

    ENTITY = "IN_INSURANCE_ID"

    def __init__(self) -> None:
        super().__init__(
            supported_entity=self.ENTITY,
            patterns=[
                Pattern(
                    name="slashed_policy",
                    regex=r"\b[A-Z]{2,4}[/-]\d{2,4}[/-][A-Z0-9]{2,6}[/-]\d{4,8}\b",
                    score=0.55,
                ),
                Pattern(
                    name="labelled_policy",
                    regex=r"(?i)\bpolicy\s*(?:no\.?|number|#)?\s*[:\-]?\s*([A-Z0-9][A-Z0-9/\-]{5,24})\b",
                    score=0.6,
                ),
            ],
            context=["policy", "insurance", "tpa", "mediclaim", "pmjay", "ayushman"],
        )


# --------------------------------------------------------------------------
# Label-anchored recognizers
#
# A lab report is a template, not prose. `Patient Name:` is a guarantee;
# "spaCy thinks this is a person" is a guess. On the real Tenet Diagnostics
# report, NER found the consultant's name and missed the patient's entirely --
# the patient was only partially caught because "MRS.NA" happens to look like a
# Namibian domain. For templated documents, anchor on the label.
# --------------------------------------------------------------------------


class LabelAnchoredRecognizer(LocalRecognizer):
    """
    Match `<label>: <value>` and return a span covering ONLY the value.

    PatternRecognizer reports the whole regex match, which would redact the
    label too ("[IN_PATIENT_NAME]" instead of "Patient Name: [IN_PATIENT_NAME]")
    and destroy the document structure a summariser reads. Hence a
    LocalRecognizer with an explicit named group.
    """

    ENTITY = "OVERRIDE_ME"
    REGEX = ""
    SCORE = 0.9

    def __init__(self, supported_language: str = "en") -> None:
        super().__init__(
            supported_entities=[self.ENTITY],
            name=type(self).__name__,
            supported_language=supported_language,
        )
        self._compiled = re.compile(self.REGEX, re.IGNORECASE)

    def load(self) -> None:  # nothing to load; required by the interface
        return None

    def analyze(self, text, entities, nlp_artifacts=None):
        if self.ENTITY not in entities:
            return []
        results = []
        for match in self._compiled.finditer(text):
            start, end = match.span("value")
            value = text[start:end].rstrip()
            if not value:
                continue
            end = start + len(value)  # don't swallow trailing whitespace
            results.append(
                RecognizerResult(
                    entity_type=self.ENTITY,
                    start=start,
                    end=end,
                    score=self.SCORE,
                )
            )
        return results


class PatientNameRecognizer(LabelAnchoredRecognizer):
    """
    `Patient Name: MRS.NAGA ...`, `Name : Ramesh Kumar`, `Pt Name- X`.

    The value must be on the SAME LINE as the colon -- `[ \\t]*`, never `\\s*`.

    With `\\s*` the match jumped a newline and, on the Tenet report, anchored
    `Name\\n:` to the block that follows it in reading order, capturing
    `70 Years / Female` as the patient's name. That redacted the age and gender
    (which the summariser needs) while leaving the actual name untouched -- worse
    than not firing at all. Reading order is not visual layout; a form label and
    its value are only reliably associated when they share a line.

    Where they don't, HonorificNameRecognizer picks the name up instead.
    """

    ENTITY = "IN_PATIENT_NAME"
    SCORE = 0.95
    REGEX = (
        r"\b(?:patient\s*name|pt\.?\s*name|patient|name)\s*[:\-][ \t]*"
        r"(?P<value>[^\n]{2,60}?)(?=\s{2,}|\n|$)"
    )


class ReferringDoctorRecognizer(LabelAnchoredRecognizer):
    """`Ref. By: Dr. X`, `Referred By - Dr Y`, `Consultant: Z`. Same-line only."""

    ENTITY = "IN_DOCTOR_NAME"
    SCORE = 0.9
    REGEX = (
        r"\b(?:ref\.?\s*by|referred\s*by|referring\s*(?:physician|doctor)|"
        r"consultant|physician)\s*[:\-][ \t]*"
        r"(?P<value>[^\n]{2,60}?)(?=\s{2,}|\n|$)"
    )


class HonorificNameRecognizer(PatternRecognizer):
    """
    An honorific followed by a capitalised run: `MRS.NAGA LAXMI J`, `Dr. A Sharma`.

    Indian medical records almost always prefix the patient with MR/MRS/MS/BABY,
    and lab systems print the value in caps. spaCy misses these outright -- on the
    Tenet report `MRS.NAGA LAXMI J` sat alone in its own block and drew no PERSON
    detection at all; the only reason any of it was blacked out is that Presidio's
    URL recognizer read `MRS.NA` as a Namibian domain.

    The honorific is what makes this safe to score high: an all-caps run is weak
    evidence on its own, but an all-caps run immediately after `MRS.` is a name.
    """

    ENTITY = "IN_PERSON_NAME"

    def __init__(self) -> None:
        super().__init__(
            supported_entity=self.ENTITY,
            patterns=[
                Pattern(
                    name="honorific_name",
                    regex=(
                        r"\b(?:MR|MRS|MS|MISS|DR|SHRI|SMT|KUM|BABY|MASTER|B/O|W/O|S/O|D/O)"
                        r"\.?\s*(?:[A-Z][A-Za-z]*\.?\s*){1,5}[A-Z][A-Za-z]*\b"
                    ),
                    score=0.85,
                )
            ],
            context=["patient", "name", "pt", "attendant"],
        )


# --------------------------------------------------------------------------

INDIAN_RECOGNIZER_CLASSES = (
    AadhaarRecognizer,
    PanRecognizer,
    AbhaNumberRecognizer,
    AbhaAddressRecognizer,
    IndianPhoneRecognizer,
    IndianPinCodeRecognizer,
    ContextaUhidRecognizer,
    VehicleRegistrationRecognizer,
    InsurancePolicyRecognizer,
    PatientNameRecognizer,
    ReferringDoctorRecognizer,
    HonorificNameRecognizer,
)

#: Custom entity labels, for building anonymizer operators and reports.
INDIAN_ENTITIES = tuple(cls.ENTITY for cls in INDIAN_RECOGNIZER_CLASSES)

#: Recognizers that need the label and its value adjacent, so they must run on
#: joined page text rather than per layout block. See engine.redact_blocks.
LABEL_ANCHORED_ENTITIES = frozenset(
    cls.ENTITY
    for cls in INDIAN_RECOGNIZER_CLASSES
    if issubclass(cls, LabelAnchoredRecognizer)
)


def build_indian_recognizers() -> list:
    """Fresh instances of every custom recognizer."""
    return [cls() for cls in INDIAN_RECOGNIZER_CLASSES]
