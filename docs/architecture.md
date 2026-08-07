# Architecture & decisions

What we explored, what we learned from each approach, and what each layer is
measurably worth.

**Nothing here is a decision.** Two approaches were built and measured during an
exploratory spike. Neither has been selected or approved. This document exists so
the reasoning and the findings survive, not to record a conclusion.

---

## 1. The problem

Contexta's summariser sends patient data to a third-party LLM. The structured
fields were already minimised — the patient's name never crossed the boundary,
enforced at the schema layer. Two surfaces were not:

1. **PDF attachment text.** Lab report text was extracted and concatenated
   straight into the prompt. A lab report carries the patient name, UHID, phone,
   address, referring physician and hospital letterhead. None of it was filtered.
2. **Free-text clinical fields.** Chief complaint, diagnosis, SOAP assessment and
   plan are typed by a doctor. `"Pt Ramesh, ph 98765, referred by Dr. Sharma"`
   appears constantly.

A third surface remains unsolved: **base64 images** go to the vision API
completely raw. Text de-identification cannot touch them.

---

## 2. Approach 1 — Azure Health De-identification 

A managed, clinically-trained PHI service. One HTTPS call:

```
POST {endpoint}/deid?api-version=2024-11-15
{ "inputText": "...", "operation": "Tag" }
```

**Why it was the right first choice:** the deployment target was Azure. That made
the call intra-region, covered by an existing Microsoft BAA, with no egress cost —
and a clinically-trained managed service beats one you assemble yourself.

**What we learned building the spike:**

- `operation` has three modes: `Tag`, `Redact`, `Surrogate`
- **Server-side `Redact` breaks a summariser.** The 2024-11-15 API exposes only
  `redactionFormat` and `surrogateLocale` — there is **no category allow-list**.
  Microsoft's own example: `"Kimberly Brown is a 34 y.o. ... PCP 2/6/2025"` →
  `"[patient] is a [age] y.o. ... PCP [date]"`. Age and date both go. The design
  answer is `Tag` + client-side selective redaction.
- `offset` and `length` are `StringIndex` **objects** (`{codePoint, utf16, utf8}`),
  not integers. Python must use `codePoint`.
- 48,000 character input limit; 28 PHI categories; 50 MB/month free.
- Entra ID auth, not an API key. Needs two RBAC roles.
- **None of the 28 categories is Aadhaar, ABHA, PAN or UHID.**

**Why we stopped pursuing it:** the deployment target changed. Without Azure, the same
service becomes a new vendor, a new DPA, and a cross-border transfer of raw PHI
under DPDP § 16 — for a service you otherwise have no relationship with. The
argument was never "Azure is good"; it was "a managed clinical service you are
already inside beats one you assemble." Remove the premise and the conclusion goes
with it.

**If the deployment target changes again,** the same reasoning revives — for Azure,
or AWS Comprehend Medical, or GCP Healthcare API. All three still need a custom
recognizer layer for Indian identifiers.

---

## 3. Approach 2 — Presidio, self-hosted

The approach we took furthest, because it was the one that stayed viable once Azure
was off the table. One trust boundary instead of two. Free. No new data processor,
no cross-border transfer of raw PHI. The cost: **you own detection accuracy**, which
is why every score has a test behind it and every layer has a measured contribution.

### Also looked at

| Option | What we found |
|---|---|
| LangChain `PIIMiddleware` | Five built-in types (email, credit card, IP, MAC, URL) — **zero PHI**. Regex cannot detect a name. And it's a `create_agent` hook, so using it means restructuring the service around LangChain to get `re.sub`. |
| LangChain `piiRedactionMiddleware` (JS) | No built-in detectors at all — bring-your-own-regex. Same structural ceiling. |
| Third-party PHI redaction libraries | The credible ones are Presidio wrappers, so you inherit the accuracy ceiling plus a single-maintainer dependency in the most sensitive path. Publish no benchmarks. |
| Aisera / Emitrr / Automation Anywhere | Category error. An ITSM agent platform, a patient-SMS product and an RPA suite. "HIPAA-compliant" describes contracts and infrastructure, not whether a tool can find a name in a sentence. |

---

## 4. The pipeline

```
PDF
 │
 ├─ pdf.py: get_text("blocks")           layout-aware extraction
 │
 ├─ PASS 1: NER + all recognizers, PER BLOCK
 │            spans cannot cross a table column
 ├─ PASS 2: label anchors, on the JOINED page
 │            restores label ↔ value adjacency
 │
 ├─ _filter_spans()                       min length + enclosing-term allow
 ├─ merge_overlaps(spans, text)           collapse, rebuild text over the range
 │
 └─ outputs: masked text · entity table · redacted PDF · JSON
```

### Why two passes

Two detector families need **opposite** things from the layout.

**NER needs blocks.** In the flat text stream a lab report reads:

```
...<34 U/L\nAspartate Aminotransferase,(AST/SGOT)...
```

The unit ends one line and the next test name begins the following one, so the
model spans the newline and reports `U/L\nAspartate Aminotransferase` as a single
ORGANIZATION. **The units were never targeted — they were swallowed** into a span
that started before them. Confined to a block, a span physically cannot cross a
column boundary.

**Label anchors need the joined page.** PDF forms put a label and its value in
*separate* blocks — block 45 is `'Name\n:'`, block 47 is the name. Per block,
`Patient Name:` and the name never appear in the same string, so the anchor cannot
fire.

Run only per-block and the patient's name leaks. Run only joined and the units get
swallowed. Hence both.

### The three detector layers

**1. Custom recognizers** — regex, ~0 ms, deterministic. The identifiers no vendor
model can know: `IN_AADHAAR` (Verhoeff-validated), `IN_PAN` (holder-type check),
`IN_ABHA_NUMBER`, `IN_ABHA_ADDRESS`, `IN_PHONE`, `IN_PIN_CODE`, `IN_UHID`,
`IN_VEHICLE_REG`, `IN_INSURANCE_ID`, `IN_PERSON_NAME`, `IN_PATIENT_NAME`,
`IN_DOCTOR_NAME`.

Catches anything with a **format**. Cannot catch a name in prose — a name has no
format; it is identifiable only from linguistic context. That is the boundary of
the technique, not a gap in the implementation.

**2. Clinical NER** — `StanfordAIMI/stanford-deidentifier-base` via Presidio's
`TransformersNlpEngine`, with our own i2b2 → Presidio label mapping.

This is a **de-identification** model, not a medical-entity model. It was trained
on clinical text to find PHI *within* it, so it has seen
`Alanine Aminotransferase` thousands of times and knows it is not a person. spaCy
never has. (A medical-entity model like `blaze999/Medical-NER` is the wrong tool —
it finds diseases and drugs and misses the patient.)

**3. Clinical allow-list** — units, ~60 lab tests, assay methods, report furniture,
form abbreviations, drugs. Treats the symptom rather than the cause: it only covers
what you enumerate. Necessary with spaCy, largely redundant with the clinical model.

---

## 5. Gaps in Presidio itself that had to be closed

| Gap | Fix |
|---|---|
| `allow_list` compares against the **detected span**, so it cannot suppress a detection that is a **fragment** of an allowed term. `A/GRatio` is allow-listed; the model reported `GRatio` (PERSON, 0.99). Neither `exact` nor `regex` mode helps — regex searches allow-list terms *inside* the detection, the wrong direction. | `enclosing_term()` — widen the span outward to whitespace, strip punctuation, re-check. Generalises to every future fragment. |
| A merged span covers a **wider** range than either input, so the winner's `.text` no longer matches `[start:end]`. Invisible in text output (sliced by offset), but the PDF writer searches by `.text` — so `Dr.Abdur Rehman` won the label, the range correctly extended over `Asif`, and the surname stayed readable. **A live PHI leak.** | `merge_overlaps(spans, text)` rebuilds `.text` from the merged range. |
| Transformer NER fragments: `PERSON 'A'` out of `A/GRatio`, `ID '-'` out of `APMC/FMR/78102`. Each becomes a text-search needle — `'A'` matched **118 times** and blacked out every letter A in the document. | `min_span_chars` in the engine, plus `MIN_NEEDLE_CHARS` and `MAX_RECTS_PER_SPAN` in the PDF writer, which *report* skips rather than applying them. |
| Presidio raises `ValueError: No matching recognizers were found` rather than returning empty when asked for an entity nothing serves. | Intersect requested entities with `get_supported_entities()` before asking. |
| No concept of PDF layout. | `extract_page_blocks()` + the two-pass design above. |
| A black box drawn over text is trivially undone. | PyMuPDF `apply_redactions()` **removes glyphs from the content stream**. Verified by re-extracting text from the output. |

Two of these were live PHI leaks found only because the evaluation harness existed.
That is the argument for building it.

---

## 6. Policy choices made in the prototype

These are the settings the code currently uses and why. Each is a candidate for
review, not a ruling.

**`keep` — detect but do not redact.** HIPAA counts dates as identifiers, so
redacting them is the compliant default. But the summariser asks the LLM for trends
over time and doses by age, and a transcript full of `[DATE_TIME]` cannot answer
that. `--keep DATE_TIME` is the trade the prototype exposes. If this ever ships, the
choice needs recording deliberately rather than inheriting a default.

**Threshold left at 0.35.** Raising it to 0.6 reduces cosmetic noise and **leaks 12
identifiers**. Over-redaction is annoying; under-redaction is a breach.

**Custom recognizers kept, even though `stanford-no-custom` scores marginally
better.** That result is an artifact of the corpus — these 7 documents contain no
Aadhaar, PAN, ABHA or `CTX-` MRN, so the recognizers built for them contribute
nothing here but two false positives. Under spaCy, where they *do* carry load, the
same comparison is 37 → 57 leaks. Do not read that row as permission to delete them.

---

## 7. Open questions

None of these are settled. They are what a real decision would have to work through.

- **Deploying on AWS or GCP** → Comprehend Medical / Healthcare API become live options and the "already inside a managed clinical service" argument returns. Both still need the Indian recognizer layer.
- **A contractual requirement that PHI never leave your tenancy** → would rule out every managed option, leaving this approach as the only viable one. Worth knowing before committing either way.
- **Volume where ~6 s/document hurts** → would mean revisiting spaCy plus a stronger custom layer. The harness can decide it; we have not measured at volume.
- **Someone wanting vendor liability rather than better numbers** → a legitimate business preference that no measurement can settle. Worth naming rather than arguing past.
