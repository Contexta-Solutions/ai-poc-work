# Evaluation

Everything needed to measure redaction quality — harness, ground truth, corpus, docs.

```
evaluation/
├── README.md      ← you are here
├── evaluate.py    the harness
├── probes.yml     ground truth: what must and must not survive
└── corpus/        the test documents (real clinical PDFs)
```

How the numbers are produced, what they do and do not mean, and how to reproduce
them.

---

## Why this exists

A redaction system that cannot report a leak count is a system nobody can compare,
tune, or defend. Every claim in this repository traces to a number this harness
produced.

It has already earned its place: two live PHI leaks and two harness bugs were found
only because it existed — a merged span leaving a surname readable in the output
PDF, and a single-character detection blacking out 118 positions in a document.

---

## Method — probe lists

Full span annotation is the rigorous approach and costs hours per document. This
uses **probe lists** instead: per document, literal strings that must or must not
survive, matched case-insensitively.

```yaml
common:
  must_redact: [NAGA LAXMI J, UMR2162620, 25BNJH0012386, ...]

documents:
  25BNJH0012386.pdf:
    must_redact: ["6281651144", 8-2-269/4/B, sadf, ...]
    must_keep:   ["3,499.00", TNT61899, Glucose Fasting, ...]
```

Matching is deliberately crude and **biased toward reporting a leak**. A probe that
survives in any form counts against recall. A checker that under-reports would be
worse than no checker, because it manufactures confidence.

### Metrics

| Metric | Definition | Real? |
|---|---|---|
| **Leaked** | `must_redact` strings still present in the output | ✅ The gate metric |
| **Recall** | `(total must_redact − leaked) / total must_redact` | ✅ On the identifiers listed |
| **Over-redacted** | `must_keep` strings missing from the output | ✅ |
| **Preservation** | `(total must_keep − over_redacted) / total must_keep` | ✅ |
| **Unreviewed** | Detections matching neither list | ✅ A triage queue |
| **Precision** | `justified detections / all detections` | ⚠️ **Lower bound** |
| **F2** | `5PR / (4P + R)` | ⚠️ **Lower bound** |

**Why F2 rather than F1.** F2 weights recall roughly double. In de-identification
that is the correct weighting: a miss leaks PHI, a false positive costs a lab value.

**Why precision is a lower bound.** A probe list cannot see PHI nobody listed. Every
`unreviewed` detection is counted as a false positive, so precision is pessimistic
by exactly the number of items awaiting triage. It becomes real only when
`unreviewed` reaches 0.

### Ground-truth validation

`validate_probes()` asserts every probe string actually occurs in its document, and
`evaluate.py` **refuses to score** otherwise (override with `--force`).

A phantom probe corrupts the metrics in both directions: a `must_keep` that is not
there reads as permanent over-redaction, and a `must_redact` that is not there can
never leak, inflating recall for free. **Both happened on the first draft of
`probes.yml`** — it reported 2 over-redactions that did not exist. Ground truth is
hand-written and needs a test of its own.

---

## Results

7 documents (1 bill + 6 lab reports, same patient), 7 configs. Ranked by leaks, then
over-redaction, then unreviewed noise.

| Config | Leaked | Recall | Prec* | F2* | Over-red | Preserve | Unrev | Time |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| stanford-no-custom | 0 | 100.0% | 92.9% | 98.5% | 6 | 93.1% | 4 | 39.5s |
| **stanford** ← current default in code | **0** | **100.0%** | 91.2% | 98.1% | 6 | 93.1% | 6 | 45.4s |
| stanford-t0.6 | 12 | 90.4% | 92.6% | 90.8% | 4 | 95.4% | 5 | 44.6s |
| spacy | 37 | 70.4% | 58.9% | 67.7% | 3 | 96.6% | 48 | 2.3s |
| spacy-flat | 37 | 70.4% | 54.2% | 66.4% | 11 | 87.4% | 49 | 1.1s |
| spacy-no-allowlist | 37 | 70.4% | 46.2% | 63.7% | 18 | 79.3% | 74 | 2.0s |
| spacy-no-custom | 57 | 54.4% | 51.3% | 53.8% | 3 | 96.6% | 52 | 2.1s |

All six lab reports redact clean under `stanford`. All 6 remaining over-redactions
are on the billing document: `36AAGCC8833Q1ZX` (the lab's GST number), `TNT61899`
(service code), `Tenet Advance Health Check Up`, `Can.amt`, `www.tenetdiagnostics.in`
— business identifiers the model reads as IDs. Whether those count as PHI is a
triage decision, not a defect.

### What each layer is worth

Read as ablations against `spacy` (37 leaks, 3 over-redacted):

| Layer removed | Effect |
|---|---|
| Custom recognizers | 37 → **57 leaks**, recall 70.4% → 54.4% |
| Clinical model (spaCy instead) | 0 → **37 leaks**, recall 100% → 70.4% |
| Block extraction (`--flat`) | leaks unchanged, over-redaction 3 → **11** |
| Allow-list | leaks unchanged, over-redaction 3 → **18**, precision 58.9% → 46.2% |

Two things this makes precise:

- **Block extraction and the allow-list buy precision, not recall.** Neither moves
  the leak count. They exist to stop the summariser losing lab values.
- **The clinical model buys recall.** It caught `25BNJH0012386` (the accession
  number, also the filename), `30644477` and `FMR/78102` — three identifiers spaCy
  leaked from every document.

### `stanford-no-custom` scoring higher is an artifact

It wins on precision (92.9% vs 91.2%) because **these 7 documents contain no
Aadhaar, PAN, ABHA or `CTX-` MRN**. The recognizers built for those identifiers are
not exercised, so all they contribute here is two false positives. The `spacy` pair
shows what they are worth when they do fire: 37 → 57 leaks. Do not read that row as
permission to delete them.

---

## Reproducing

```bash
python evaluation/evaluate.py --list                     # available configs
python evaluation/evaluate.py                            # default set
python evaluation/evaluate.py --detail                   # per-document errors
python evaluation/evaluate.py --report report.md          # markdown report
python evaluation/evaluate.py --configs stanford,spacy --detail
python evaluation/evaluate.py --all                      # includes obi
python evaluation/evaluate.py --configs stanford --gate  # CI: exit 1 on any leak
```

`--gate` is the regression guard. Wire it into CI as-is; it fails the build on any
leak.

Transformer configs take ~6 s/document; the whole default set is a few minutes. The
`spacy-*` configs run in about 2 s total.

### Adding a config

`CONFIGS` in [`evaluate.py`](evaluate.py). **Pin `nlp_engine` explicitly on every
entry.** When `RedactionConfig`'s default changed from `"spacy"` to
`"transformers"`, every `spacy-*` row silently became a transformer run — producing
a table where `spacy-default` and `stanford` were byte-identical and "spaCy" configs
took 40 s. An evaluation harness must not depend on a default it does not own.

### Adding a document

1. Drop the PDF in [`corpus/`](corpus/).
2. Add a block to [`probes.yml`](probes.yml) with `must_redact` and `must_keep`.
3. Run `python evaluation/evaluate.py --configs spacy-flat` — the fastest config, so
   ground-truth validation comes back in seconds.
4. Fix anything it reports before trusting a score.

---

## Limits — read before quoting any number

- **7 documents, one patient, one lab.** Enough to rank configs and catch
  regressions. Not a benchmark, and not evidence of generalisation.
- **"100% recall" means: on the identifiers listed in `probes.yml`.** Not in the
  published sense.
- **Precision and F2 are lower bounds** until `unreviewed` reaches 0.
- **No inter-annotator agreement.** The probe lists were drafted by one pass over
  the extracted text. Judgement calls — whether the lab's own name and GST number
  are PHI — are documented in `probes.yml` and are arguable.
- **Metrics say nothing about images.** They are outside the pipeline entirely.
