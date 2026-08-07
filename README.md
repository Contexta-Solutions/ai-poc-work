# contexta-redact

> **⚠️ Exploratory spike — nothing here is a decision.**
> This repository records what we learned while investigating how to redact PHI
> before sending clinical data to an LLM. Two approaches were built and measured.
> **Neither has been chosen, approved, or integrated into Contexta.** Numbers below
> are findings from a 7-document test corpus, not production results. Treat every
> configuration as a candidate under evaluation.

PHI redaction for Indian clinical documents, built on [Microsoft Presidio](https://github.com/microsoft/presidio).

Explores removing patient identifiers from lab reports and clinical notes **before**
they reach a third-party LLM, with detection running in-process so no patient data
leaves your infrastructure at the redaction step.

```
Patient data  →  contexta-redact  →  masked text  →  LLM  →  response
                 (in-process)
```

## Measured results

7 real Tenet Diagnostics documents, one patient. Ranked by leaks.

| Config | Leaked | Recall | Precision* | F2* | Over-redacted | Preservation | Time |
|---|---:|---:|---:|---:|---:|---:|---:|
| **stanford** (current default in code) | **0** | **100.0%** | 91.2% | 98.1% | 6 | 93.1% | 45.4s |
| stanford-t0.6 | 12 | 90.4% | 92.6% | 90.8% | 4 | 95.4% | 44.6s |
| spacy | 37 | 70.4% | 58.9% | 67.7% | 3 | 96.6% | 2.3s |
| spacy-no-allowlist | 37 | 70.4% | 46.2% | 63.7% | 18 | 79.3% | 2.0s |
| spacy-no-custom | 57 | 54.4% | 51.3% | 53.8% | 3 | 96.6% | 2.1s |

<sub>\* Precision and F2 are **lower bounds** — 6 detections remain untriaged and are counted as false positives. See [evaluation/README.md](evaluation/README.md).</sub>

All six lab reports redact completely clean. The remaining over-redactions are on
the billing document, where the model masks the lab's GST number and service
codes — business identifiers, not patient data.

**Stock Presidio on the same corpus: 37 leaks, 70.4% recall.** What closed the
gap is documented in [docs/architecture.md](docs/architecture.md).

These are the best numbers the exploration reached. They are not a claim that this
is the right approach for Contexta — that question is still open.

## Quickstart

```bash
python -m venv .venv
.venv/Scripts/activate                      # Windows: .venv\Scripts\activate.bat
pip install -r requirements.txt
pip install -r requirements-transformers.txt # for the clinical model (default)
python -m spacy download en_core_web_lg
python -m spacy download en_core_web_sm      # tokenizer for the transformer
```

> `pip install "transformers>=4.40"` on its own **will not work** — Presidio gates
> on `spacy-huggingface-pipelines`, which caps transformers below 5.x. Use the
> requirements file.

```bash
python redact.py evaluation/corpus/25BNJH0012386_d.pdf   # redact a document
python redact.py file.pdf --keep DATE_TIME               # keep dates for summarisation
python tests/test_recognizers.py                         # 33 tests, no spaCy needed
python evaluation/evaluate.py --detail                   # score every config
python evaluation/evaluate.py --configs stanford --gate  # CI gate: exit 1 on any leak
```

Outputs: side-by-side original vs redacted, an entity table, `<input>.redacted.pdf`
with the glyphs **removed from the content stream** (not a black box drawn over
readable text), and optional JSON.

## How it works

Three detector layers with complementary failure modes. Each one's contribution
is measured, not assumed.

| Layer | Catches | Cannot catch | Worth |
|---|---|---|---|
| **Custom recognizers** (12) | Anything with a format — Aadhaar, ABHA, PAN, UHID, `+91` | Names in prose | 57 → 37 leaks |
| **Clinical NER** (Stanford de-id) | Names, places, dates, IDs in prose | Aadhaar, ABHA — never seen them | 37 → 0 leaks |
| **Clinical allow-list** | Suppresses lab tests, units, methods, drugs | Terms not enumerated | over-redaction 18 → 3 |

Plus **layout-aware extraction** — analysis runs per PDF layout block so a span
cannot cross a table column, then label anchors run on the joined page. Worth
over-redaction 11 → 3.

Full detail in [docs/architecture.md](docs/architecture.md).

## Repository layout

```
├── redact.py                   CLI: redact a PDF or text file
├── contexta_redact/
│   ├── recognizers.py          12 Indian/Contexta recognizers + Verhoeff
│   ├── engine.py               pipeline assembly, span merging, policy
│   ├── allowlist.py            clinical terms never to redact
│   ├── pdf.py                  PyMuPDF extraction + true redaction
│   └── report.py               entity table, side-by-side, JSON
├── evaluation/                 self-contained: harness + ground truth + corpus
│   ├── README.md               metrics methodology and how to reproduce
│   ├── evaluate.py             CLI: score configs, CI gate
│   ├── probes.yml              what must and must not survive
│   └── corpus/                 the test documents
├── tests/test_recognizers.py   33 tests
├── docs/
│   ├── architecture.md         approaches explored, what each layer is worth
│   ├── files.md                module-by-module reference
│   └── PHI-Redaction-Architecture.drawio
└── COMPLIANCE.md               HIPAA & DPDP reference
```

Per-file detail in [docs/files.md](docs/files.md).

## Known limitations

Read these before relying on any number above.

- **Images are not redacted.** Base64 images bypass text de-identification entirely — HIPAA identifier #17. Needs OCR-then-redact, or stripping images from the prompt. Unsolved.
- **Scanned PDFs have no text layer.** `redact.py` exits with an error rather than silently passing them through.
- **The corpus is 7 documents, one patient, one lab.** Enough to rank configs and gate regressions. Not enough to certify anything.
- **Precision is a lower bound** — 6 detections still untriaged.
- **Redaction is not compliance.** HIPAA Safe Harbor needs the 18 identifiers gone *and* no actual knowledge of re-identifiability, which a probabilistic model cannot certify. DPDP does not treat redaction as a status change at all. See [COMPLIANCE.md](COMPLIANCE.md).
- **You own the accuracy.** There is no vendor to escalate to on a miss. That is the cost of keeping data in-process.
- **`--threshold 0.6` leaks.** Measured at 12 leaks vs 0 at the default 0.35. Do not raise it to reduce cosmetic noise.

## ⚠️ This repository must stay private

`evaluation/corpus/` contains real clinical documents with patient identifiers,
committed deliberately as the evaluation corpus. `evaluation/probes.yml` quotes
those identifiers verbatim. Git history is permanent — treat access control as the
primary safeguard.
