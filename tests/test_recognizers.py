"""
Per-recognizer tests.

Presidio's own guidance: test each recognizer on representative data before you
trust it, and record how the accuracy was established. These are that record.
Every score in recognizers.py should have a case here justifying it.

Runs without spaCy — PatternRecognizer.analyze() works with nlp_artifacts=None.
That also means context boosting is OFF here, so context-gated recognizers are
tested at their bare score, which is exactly the behaviour worth pinning down.

    pytest tests/                      # or
    python tests/test_recognizers.py   # no pytest needed
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contexta_redact.engine import Span, merge_overlaps  # noqa: E402
from contexta_redact.recognizers import (  # noqa: E402
    AadhaarRecognizer,
    AbhaAddressRecognizer,
    AbhaNumberRecognizer,
    ContextaUhidRecognizer,
    HonorificNameRecognizer,
    IndianPhoneRecognizer,
    IndianPinCodeRecognizer,
    InsurancePolicyRecognizer,
    PanRecognizer,
    PatientNameRecognizer,
    ReferringDoctorRecognizer,
    VehicleRegistrationRecognizer,
    verhoeff_check_digit,
    verhoeff_valid,
)

THRESHOLD = 0.35  # engine default; context-gated matches must fall below it


def detect(recognizer, text: str) -> list:
    """(matched_text, score) for every hit, without NLP context enhancement."""
    results = recognizer.analyze(
        text, entities=[recognizer.ENTITY], nlp_artifacts=None
    )
    return [(text[r.start : r.end], r.score) for r in results]


def valid_aadhaar(payload_11: str = "23456789012") -> str:
    """A checksum-valid 12-digit number. Synthetic — never use a real Aadhaar."""
    assert len(payload_11) == 11
    return payload_11 + str(verhoeff_check_digit(payload_11))


# --------------------------------------------------------------------------
# Verhoeff
# --------------------------------------------------------------------------


def test_verhoeff_round_trip():
    for payload in ("23456789012", "98765432109", "20000000000"):
        full = payload + str(verhoeff_check_digit(payload))
        assert verhoeff_valid(full), full


def test_verhoeff_rejects_corruption():
    good = valid_aadhaar()
    # Flip one digit — Verhoeff catches every single-digit error by construction.
    bad = good[:5] + str((int(good[5]) + 1) % 10) + good[6:]
    assert not verhoeff_valid(bad)
    assert not verhoeff_valid("notdigits123")


# --------------------------------------------------------------------------
# Aadhaar
# --------------------------------------------------------------------------


def test_aadhaar_valid_is_detected():
    rec = AadhaarRecognizer()
    good = valid_aadhaar()
    assert detect(rec, f"Aadhaar {good} on file"), "valid Aadhaar not detected"


def test_aadhaar_rejects_bad_checksum():
    """The whole reason for the checksum: 12-digit noise must not match."""
    rec = AadhaarRecognizer()
    good = valid_aadhaar()
    bad = good[:-1] + str((int(good[-1]) + 1) % 10)
    assert not detect(rec, f"Ref {bad}"), "bad checksum should be discarded"


def test_aadhaar_rejects_leading_0_and_1():
    rec = AadhaarRecognizer()
    assert not detect(rec, "order 012345678901 shipped")
    assert not detect(rec, "order 112345678901 shipped")


def test_aadhaar_accepts_grouped_formatting():
    rec = AadhaarRecognizer()
    good = valid_aadhaar()
    spaced = f"{good[:4]} {good[4:8]} {good[8:]}"
    hyphened = f"{good[:4]}-{good[4:8]}-{good[8:]}"
    assert detect(rec, f"UID {spaced}"), "space-grouped Aadhaar missed"
    assert detect(rec, f"UID {hyphened}"), "hyphen-grouped Aadhaar missed"


# --------------------------------------------------------------------------
# PAN
# --------------------------------------------------------------------------


def test_pan_detected():
    rec = PanRecognizer()
    hits = detect(rec, "PAN ABCPK1234F submitted")
    assert hits and hits[0][0] == "ABCPK1234F"


def test_pan_rejects_invalid_holder_type():
    """4th char is the holder-type code; 'X' is not one, so this is not a PAN."""
    rec = PanRecognizer()
    assert not detect(rec, "code ABCXK1234F here")


# --------------------------------------------------------------------------
# ABHA
# --------------------------------------------------------------------------


def test_abha_hyphenated_scores_high():
    rec = AbhaNumberRecognizer()
    hits = detect(rec, "ABHA 12-3456-7890-1234")
    assert hits and hits[0][1] >= 0.8


def test_abha_plain_14_digits_needs_context():
    """Bare 14 digits is weak evidence — must sit below threshold unaided."""
    rec = AbhaNumberRecognizer()
    hits = detect(rec, "txn 12345678901234 posted")
    assert hits, "pattern should still match"
    assert max(s for _, s in hits) < THRESHOLD


def test_abha_address_detected_and_not_an_email():
    rec = AbhaAddressRecognizer()
    assert detect(rec, "ABHA address ramesh.kumar@abdm")
    assert not detect(rec, "email ramesh.kumar@gmail.com")


# --------------------------------------------------------------------------
# Phone
# --------------------------------------------------------------------------


def test_indian_phone_formats():
    rec = IndianPhoneRecognizer()
    for text in (
        "ph +91 98765 43210",
        "contact 9876543210",
        "mob +919876543210",
        "call 98765-43210",
    ):
        assert detect(rec, text), f"missed: {text}"


def test_indian_phone_rejects_landline_leading_digits():
    """Indian mobiles start 6-9. A 10-digit run starting 1-5 is not one."""
    rec = IndianPhoneRecognizer()
    assert not detect(rec, "ref 1234567890 noted")


# --------------------------------------------------------------------------
# PIN code — the deliberate low scorer
# --------------------------------------------------------------------------


def test_pin_code_below_threshold_without_context():
    """
    Guards the most dangerous tuning mistake in this module. A 6-digit number is
    usually a bill amount or a lab value; only context makes it a PIN code. If
    this test starts failing, precision has been traded away somewhere.
    """
    rec = IndianPinCodeRecognizer()
    hits = detect(rec, "total 500034 rupees")
    assert hits, "pattern should match"
    assert max(s for _, s in hits) < THRESHOLD, "PIN must not clear threshold unaided"


# --------------------------------------------------------------------------
# UHID / MRN
# --------------------------------------------------------------------------


def test_contexta_mrn_high_confidence():
    rec = ContextaUhidRecognizer()
    hits = detect(rec, "MRN CTX-448192 admitted")
    assert hits
    assert max(s for _, s in hits) >= 0.9, "our own format should be near-certain"


def test_labelled_uhid_variants():
    rec = ContextaUhidRecognizer()
    for text in ("UHID: 4481920", "Patient ID - AB-448192", "MR No. 99881122"):
        assert detect(rec, text), f"missed: {text}"


# --------------------------------------------------------------------------
# Vehicle / insurance
# --------------------------------------------------------------------------


def test_vehicle_registration():
    rec = VehicleRegistrationRecognizer()
    assert detect(rec, "ambulance TS09AB1234 dispatched")
    assert detect(rec, "vehicle MH-12-AB-1234")


def test_insurance_policy():
    rec = InsurancePolicyRecognizer()
    assert detect(rec, "policy SH/2024/HYD/889201 active")
    assert detect(rec, "Policy No: STAR12345678")


# --------------------------------------------------------------------------
# Label-anchored recognizers
# --------------------------------------------------------------------------


def test_patient_name_returns_value_not_label():
    """The span must cover the name only — redacting 'Patient Name:' as well
    would destroy the document structure a summariser reads."""
    rec = PatientNameRecognizer()
    hits = detect(rec, "Patient Name: Ramesh Kumar")
    assert hits, "patient name not detected"
    assert hits[0][0].strip() == "Ramesh Kumar", hits


def test_patient_name_stops_at_column_gap():
    """Lab reports put the next field on the same line after wide spacing."""
    rec = PatientNameRecognizer()
    hits = detect(rec, "Patient Name: Ramesh Kumar     UHID: CTX-448192")
    assert hits and "UHID" not in hits[0][0], hits


def test_patient_name_does_not_cross_a_newline():
    """
    Regression guard for the worst bug found on the real Tenet report.

    With `\\s*` after the colon this anchored `Name\\n:` to the NEXT block in
    reading order and captured '70 Years / Female' as the patient's name —
    redacting age and gender while leaving the real name in the document.
    A form label only reliably owns a value that shares its line.
    """
    rec = PatientNameRecognizer()
    hits = detect(rec, "Name\n:\n70 Years / Female\nMRS.NAGA LAXMI J")
    assert not hits, f"must not capture across a newline, got {hits}"


def test_referring_doctor():
    rec = ReferringDoctorRecognizer()
    hits = detect(rec, "Ref.By: Dr. Anita Sharma")
    assert hits and "Anita" in hits[0][0], hits


# --------------------------------------------------------------------------
# Honorific names — what actually caught the patient on the real report
# --------------------------------------------------------------------------


def test_honorific_catches_all_caps_indian_name():
    """
    `MRS.NAGA LAXMI J` sat alone in its own block and drew NO spaCy PERSON
    detection. This recognizer is the reason it gets redacted.
    """
    rec = HonorificNameRecognizer()
    for text in ("MRS.NAGA LAXMI J", "DR RAJASHEKAR CHAKRAVATHY M",
                 "Dr.Abdur Rehman Asif", "Baby of MRS SUNITHA"):
        assert detect(rec, text), f"missed: {text}"


def test_honorific_requires_the_honorific():
    """An all-caps run alone is weak evidence — section headers are all-caps too."""
    rec = HonorificNameRecognizer()
    assert not detect(rec, "DEPARTMENT OF CLINICAL CHEMISTRY")
    assert not detect(rec, "LIVER FUNCTION TEST")


def test_prefixed_record_number():
    """`UMR2162620` was previously mislabelled ORGANIZATION — right span, wrong reason."""
    rec = ContextaUhidRecognizer()
    hits = detect(rec, "TID/SID : UMR2162620/")
    assert hits, "lab record number not detected"
    assert max(s for _, s in hits) >= 0.8


# --------------------------------------------------------------------------
# Span arithmetic
# --------------------------------------------------------------------------


def test_merge_overlaps_keeps_higher_score():
    """
    Two recognizers claiming one run must collapse to a single span. Writing two
    markers over the same text corrupts every offset after it.
    """
    spans = [
        Span("PHONE_NUMBER", 10, 20, 0.6, "9876543210"),
        Span("IN_PHONE", 10, 20, 0.85, "9876543210"),
    ]
    merged = merge_overlaps(spans)
    assert len(merged) == 1
    assert merged[0].entity_type == "IN_PHONE"


def test_merge_overlaps_extends_to_widest_span():
    spans = [
        Span("A", 0, 10, 0.9, "x"),
        Span("B", 5, 18, 0.4, "y"),
    ]
    merged = merge_overlaps(spans)
    assert len(merged) == 1
    assert (merged[0].start, merged[0].end) == (0, 18)
    assert merged[0].entity_type == "A"


def test_merge_overlaps_rebuilds_text_over_the_merged_range():
    """
    Regression: a merged span is WIDER than either input, so the winner's
    original .text no longer matches [start:end]. Invisible in text output
    (which slices by offset) but leaks PHI in the PDF output (which searches by
    .text). On the Tenet report PERSON 'Dr.Abdur Rehman' (1.00) beat
    IN_PERSON_NAME 'Dr.Abdur Rehman Asif' (0.85); the range extended correctly
    but .text stayed short, so 'Asif' was left readable on the page.
    """
    text = "Dr.Abdur Rehman Asif signed"
    spans = [
        Span("PERSON", 0, 15, 1.00, "Dr.Abdur Rehman"),
        Span("IN_PERSON_NAME", 0, 20, 0.85, "Dr.Abdur Rehman Asif"),
    ]
    merged = merge_overlaps(spans, text)
    assert len(merged) == 1
    assert merged[0].entity_type == "PERSON"          # higher score wins the label
    assert (merged[0].start, merged[0].end) == (0, 20)  # but the range extends
    assert merged[0].text == "Dr.Abdur Rehman Asif", merged[0].text


def test_merge_overlaps_without_text_still_merges():
    """The text arg is optional; existing callers must keep working."""
    merged = merge_overlaps([Span("A", 0, 10, 0.9, "x"), Span("B", 5, 18, 0.4, "y")])
    assert len(merged) == 1 and (merged[0].start, merged[0].end) == (0, 18)


def test_min_span_chars_rejects_single_character_detections():
    """
    Regression: transformer NER emitted PERSON 'A' (0.81) from "A/GRatio" and
    ID '-' (0.79) from "APMC/FMR/78102". Neither is PHI, but each became a
    text-search needle -- 'A' alone matched 118 times and blacked out every
    letter A in the document, destroying the lab results it was meant to keep.
    """
    from contexta_redact.pdf import MIN_NEEDLE_CHARS

    spans = [
        Span("PERSON", 0, 1, 0.81, "A"),
        Span("ID", 5, 6, 0.79, "-"),
        Span("PERSON", 10, 26, 0.92, "MRS.NAGA LAXMI J"),
    ]
    kept = [s for s in spans if len(s.text.strip()) >= 2]
    assert len(kept) == 1 and kept[0].text == "MRS.NAGA LAXMI J"
    # pdf.py must refuse them independently of the engine filter
    assert len("A") < MIN_NEEDLE_CHARS and len("-") < MIN_NEEDLE_CHARS


def test_enclosing_term_widens_to_whitespace():
    """
    Regression: the model reported PERSON 'GRatio' (0.99) out of 'A/GRatio.' on
    the Tenet LFT report. 'A/GRatio' IS in LAB_TESTS, but Presidio's allow_list
    compares against the detected span, and the detection is a FRAGMENT of the
    allowed term — so neither "exact" nor "regex" mode suppresses it. Widening
    the span outward to whitespace is what makes the allow-list reachable.
    """
    from contexta_redact.engine import RedactionPipeline as RP

    text = "Globulin. Method:Calculated A/GRatio. 1.06"
    start = text.index("GRatio")
    assert RP.enclosing_term(text, start, start + len("GRatio")) == "A/GRatio."

    # Already a whole token — widening must be a no-op.
    s = text.index("Globulin")
    assert RP.enclosing_term(text, s, s + len("Globulin.")) == "Globulin."

    # Span at the very start and very end must not walk off the string.
    assert RP.enclosing_term("abc", 0, 1) == "abc"
    assert RP.enclosing_term("abc", 2, 3) == "abc"


def test_merge_overlaps_leaves_disjoint_alone():
    spans = [Span("A", 0, 5, 0.9, "a"), Span("B", 10, 15, 0.9, "b")]
    assert len(merge_overlaps(spans)) == 2
    assert merge_overlaps([]) == []


def test_back_to_front_replacement_preserves_offsets():
    """
    Mirrors RedactionPipeline.redact(). Replacing front-to-back with markers of a
    different length shifts every later offset — this pins the correct order.
    """
    text = "Ramesh Kumar has MRN CTX-448192 today"
    spans = [
        Span("PERSON", 0, 12, 0.9, "Ramesh Kumar"),
        Span("IN_UHID", 21, 31, 0.95, "CTX-448192"),
    ]
    out = text
    for s in sorted(spans, key=lambda s: s.start, reverse=True):
        out = out[: s.start] + s.marker + out[s.end :]
    assert out == "[PERSON] has MRN [IN_UHID] today", out


# --------------------------------------------------------------------------


def _run_all() -> int:
    tests = [(n, f) for n, f in sorted(globals().items())
             if n.startswith("test_") and callable(f)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"  ok    {name}")
        except AssertionError as exc:
            failed += 1
            print(f"  FAIL  {name}: {exc}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"  ERROR {name}: {type(exc).__name__}: {exc}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(_run_all())
