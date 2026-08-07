# File reference

Module by module: what it owns, the public surface, and the reasoning that is easy
to break by accident.

---

## Entry points

### `redact.py`
CLI for a single document. Reads a PDF (or `.txt`), runs the pipeline, prints
side-by-side and an entity table, writes a redacted PDF and optional JSON.

| Flag | Effect |
|---|---|
| `--nlp-engine spacy\|transformers` | Detection engine. Default `transformers` |
| `--transformer-model stanford\|obi\|<hf-id>` | Clinical model |
| `--model` | spaCy model (default `en_core_web_lg`) |
| `--threshold` | Minimum confidence. **Default 0.35 — raising it leaks** |
| `--flat` | Linear extraction instead of layout blocks, for comparison |
| `--keep ENTITY...` | Detect but do not redact, e.g. `--keep DATE_TIME` |
| `--drop ENTITY...` | Ignore an entity type entirely |
| `--no-allow-list` | Disable the clinical allow-list |
| `--allow-list-file PATH` | Extra never-redact terms, one per line |
| `--json PATH` · `--out-pdf PATH` · `--no-pdf` · `--quiet` · `--width N` | Output control |

Refuses to overwrite the source PDF. Exits with a clear error on a scanned/image-only
PDF rather than silently passing it through.

### `evaluate.py`
Scores configs against `evaluation/probes.yml`. Lives in `evaluation/` alongside its
ground truth and corpus. See [../evaluation/README.md](../evaluation/README.md).

`--list` · `--configs` · `--all` · `--detail` · `--report PATH` · `--gate` · `--force`

Validates ground truth before scoring and refuses to run against invalid probes.

---

## `contexta_redact/`

### `recognizers.py`
The identifiers Presidio cannot know about. **This is the layer no managed service
replaces.**

*Verhoeff checksum* — `verhoeff_valid()`, `verhoeff_check_digit()`. Without it
`\b[2-9]\d{11}\b` matches any 12-digit number: order IDs, bill numbers, timestamps.

*`PatternRecognizer` subclasses* — regex plus an optional `validate_result` hook
(`True` → promote to 1.0, `False` → discard, `None` → leave):

| Class | Entity | Note |
|---|---|---|
| `AadhaarRecognizer` | `IN_AADHAAR` | Verhoeff-validated; leading 0/1 rejected |
| `PanRecognizer` | `IN_PAN` | 4th char must be a valid holder-type code |
| `AbhaNumberRecognizer` | `IN_ABHA_NUMBER` | Hyphenated 0.85; bare 14 digits 0.3, needs context |
| `AbhaAddressRecognizer` | `IN_ABHA_ADDRESS` | `name@abdm` — a handle, not an email |
| `IndianPhoneRecognizer` | `IN_PHONE` | 10 digits starting 6–9, loose spacing |
| `IndianPinCodeRecognizer` | `IN_PIN_CODE` | **Base 0.25, deliberately below threshold** |
| `ContextaUhidRecognizer` | `IN_UHID` | `CTX-\d{6}`, `UMR\d{5,}`, labelled `UHID:` |
| `VehicleRegistrationRecognizer` | `IN_VEHICLE_REG` | `TS09AB1234` |
| `InsurancePolicyRecognizer` | `IN_INSURANCE_ID` | Context-driven; formats vary per insurer |
| `HonorificNameRecognizer` | `IN_PERSON_NAME` | `MRS.`/`DR` + capitalised run |

*`LocalRecognizer` subclasses* — `LabelAnchoredRecognizer` (base),
`PatientNameRecognizer`, `ReferringDoctorRecognizer`. These return **only the named
capture group**, so `Patient Name: X` redacts `X` and keeps the label.
`PatternRecognizer` would report the whole match and destroy the structure a
summariser reads.

> **The PIN code score is load-bearing.** A bare 6-digit number is far more likely to
> be a bill amount or a lab value. Only a nearby context word lifts it into range
> (0.25 + 0.35 = 0.60, which is exactly what runs print). Raising the base score
> without context is the fastest way to wreck precision, and
> `test_pin_code_below_threshold_without_context` guards it.

### `engine.py`
Pipeline assembly — the single source of truth, so the CLI, the harness and any
future caller get identical detection behaviour.

- **`RedactionConfig`** — `model`, `threshold`, `keep`, `drop`, `nlp_engine`, `transformer_model`, `tokenizer_model`, `allow_list`, `use_clinical_allow_list`, `use_custom_recognizers`, `min_span_chars`
- **`Span`** — `entity_type`, `start`, `end`, `score`, `text`, `.marker`
- **`build_analyzer()`** — spaCy or `TransformersNlpEngine`; readable errors for missing models
- **`merge_overlaps(spans, text)`** — collapse overlaps, **rebuild `.text` over the merged range**
- **`enclosing_term()`** — widen a span outward to whitespace
- **`_filter_spans()`** — min length + enclosing-term allow, in **one** place
- **`RedactionPipeline`** — `.analyze()`, `.redact()`, **`.redact_blocks()`**, `.redact_via_anonymizer()`
- **`TRANSFORMER_ENTITY_MAPPING`** — i2b2 labels → Presidio entities. **An unmapped label is silently dropped.**

> **Build the pipeline once and reuse it.** Construction loads the NLP model —
> seconds for spaCy, longer for a transformer. Doing it per page or per request makes
> this look far more expensive than it is.

> **`_filter_spans()` is shared deliberately.** `analyze()` and `redact_blocks()` are
> separate paths and previously applied their guards independently — which is exactly
> how a fix landed on one and missed the other, leaving a live PHI leak. Anything
> span-filtering goes there.

### `allowlist.py`
Clinical terms that must never be redacted: `UNITS`, `LAB_TESTS`, `LAB_METHODS`,
`REPORT_TERMS`, `FORM_ABBREVIATIONS`, `COMMON_DRUGS`.
`clinical_allow_list(extra)` returns them de-duplicated, longest-first.

> **Never add a term that could also be a name.** Mercy, Grace and Sunitha are all
> real Indian given names as well as plausible drug or hospital names. An entry here
> is a term that will *never* be redacted.

`COMMON_DRUGS` is a 26-item placeholder. Seed it properly:
```sql
SELECT DISTINCT drug_name FROM core.patient_medications;
```

### `pdf.py`
PyMuPDF in and out.

- `extract_pages()` · `extract_text()`
- **`extract_page_blocks()`** — layout-aware, the fix for units being swallowed
- **`write_redacted_pdf()`** — `apply_redactions()` removes glyphs from the content stream
- `MIN_NEEDLE_CHARS = 3`, `MAX_RECTS_PER_SPAN = 12`
- `PdfRedactionStats` — `boxes_drawn`, `not_located`, `too_short`, `runaway`

> **Redaction is by text search, not by offset.** PyMuPDF's extracted text and its
> on-page layout are different coordinate spaces, so a value broken across a line may
> not be found — those land in `not_located`, and **every entry there is PHI still in
> the output file.** Check it; do not assume it is empty.

> **The runaway guards are not optional.** A `PERSON 'A'` detection matched 118
> positions and blacked out every letter A in a document — destroying the lab results
> it was meant to preserve while reporting success. Redacting the whole page is not a
> safe failure mode.

### `report.py`
Rendering, stdlib only: `entity_table()`, `summary_counts()`, `side_by_side()`,
`to_dict()`, `to_json()`.

JSON deliberately includes `not_located` and the kept list — a report that only shows
what worked is a report you cannot audit.

---

## Data & tests

### `evaluation/probes.yml`
`common` block plus per-document `must_redact` / `must_keep`. YAML anchors share the
lab-report footer. Triage judgement calls are documented inline. Every entry must
occur in its document — `evaluate.py` enforces it.

### `tests/test_recognizers.py`
33 tests, runs without spaCy (`nlp_artifacts=None`, so context boosting is off and
context-gated recognizers are pinned at their bare score).

```bash
python tests/test_recognizers.py    # or: pytest tests/
```

Load-bearing regressions:

| Test | Guards |
|---|---|
| `aadhaar_rejects_bad_checksum` | The reason the checksum exists |
| `pin_code_below_threshold_without_context` | The most dangerous tuning mistake |
| `patient_name_does_not_cross_a_newline` | An anchor that grabbed `70 Years / Female` as the name |
| `merge_overlaps_rebuilds_text_over_the_merged_range` | The `Asif` PHI leak |
| `min_span_chars_rejects_single_character_detections` | The 118-match runaway |
| `enclosing_term_widens_to_whitespace` | The `A/GRatio` over-redaction |

### `evaluation/corpus/`
The evaluation corpus — 1 bill + 6 lab reports, same patient. **Real clinical
documents.** See the warning in the README.

---

## Dependencies

`requirements.txt` — `presidio-analyzer` 2.2.364, `presidio-anonymizer` 2.2.364,
`spacy` 3.8.14, `pymupdf` 1.28.0. Plus `python -m spacy download en_core_web_lg`.

`requirements-transformers.txt` — `spacy-huggingface-pipelines` 0.0.4,
`transformers` 4.57.6, `torch` 2.13.0. Plus `en_core_web_sm` as the tokenizer.

> **Presidio gates on `spacy-huggingface-pipelines`, not on `transformers`** —
> `TransformersNlpEngine.is_available = bool(spacy_huggingface_pipelines)`.
> `pip install "transformers>=4.40"` resolves to 5.x, which that package caps, and
> fails with a misleading *"NLP engine 'transformers' is not available"*.

> **Pin versions.** A new Presidio release can add entity types, which changes
> detection behaviour. Treat that as a behaviour change, not a patch bump.

---

## Not in the repository

`deid_spike.py` — the Azure Health De-identification spike. Gitignored; kept locally
as the reference if that deployment decision is revisited. Its findings are recorded
in [architecture.md](architecture.md), and the leak-counter idea it introduced became
`evaluate.py`.
