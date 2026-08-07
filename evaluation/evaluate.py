#!/usr/bin/env python
"""
Evaluation harness — score redaction configs against ground-truth probe lists.

    python evaluation/evaluate.py                     # default config set
    python evaluation/evaluate.py --list              # show available configs
    python evaluation/evaluate.py --configs spacy,stanford
    python evaluation/evaluate.py --detail            # per-document errors
    python evaluation/evaluate.py --report report.md
    python evaluation/evaluate.py --gate              # exit 1 if anything leaked

Ground truth is probes.yml and the corpus is corpus/, both beside this file.

WHAT THE NUMBERS MEAN

  leaked        must_redact strings still present in the output. The gate metric.
  recall        of the PHI strings listed in probes.yml, the fraction that did
                NOT survive into the output. A miss is a leak.
  preservation  of the clinical strings listed, the fraction still present.
                Over-redaction costs summary quality, not privacy.
  unreviewed    detections matching neither list. Candidate false positives
                awaiting triage.
  precision/F2  LOWER BOUNDS while unreviewed > 0 -- every untriaged detection is
                counted as a false positive.

Recall and preservation are real. Precision is a lower bound, because a probe
list cannot see PHI you forgot to list: every `unreviewed` item must be moved
into must_redact or must_keep before precision means anything in the published
sense. The harness reports the count so the gap stays visible rather than being
quietly assumed away.

Ranking is by leaks first, then over-redaction, then unreviewed noise. That
ordering is the whole editorial position of this file: over-redaction is
annoying, under-redaction is a breach.
"""

import argparse
import os
import sys
import time
from dataclasses import dataclass, field

# Repo root on the path so `contexta_redact` imports whichever directory this is
# run from. Same convention as tests/test_recognizers.py.
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import yaml  # noqa: E402

from contexta_redact import RedactionConfig, RedactionPipeline  # noqa: E402
from contexta_redact.pdf import extract_page_blocks, extract_pages  # noqa: E402

#: Ground truth and corpus live beside this script, not at the repo root.
PROBES = os.path.join(HERE, "probes.yml")
PDF_DIR = os.path.join(HERE, "corpus")


# --------------------------------------------------------------------------
# Config matrix
# --------------------------------------------------------------------------


@dataclass
class EvalConfig:
    name: str
    config: RedactionConfig
    flat: bool = False
    note: str = ""


# nlp_engine is pinned EXPLICITLY on every entry, never inherited.
# RedactionConfig's default changed from "spacy" to "transformers" and every
# spacy-* row here silently became a transformer run -- producing a table where
# spacy-default and stanford were byte-identical and "spaCy" configs took 40s.
# An evaluation harness must not depend on a default it does not own.
CONFIGS = {
    "spacy": EvalConfig(
        "spacy", RedactionConfig(nlp_engine="spacy"),
        note="spaCy lg, all defences"),
    "spacy-t0.6": EvalConfig(
        "spacy-t0.6", RedactionConfig(nlp_engine="spacy", threshold=0.6),
        note="spaCy, higher confidence bar"),
    "spacy-no-allowlist": EvalConfig(
        "spacy-no-allowlist",
        RedactionConfig(nlp_engine="spacy", use_clinical_allow_list=False),
        note="spaCy: what the allow-list is worth"),
    "spacy-flat": EvalConfig(
        "spacy-flat", RedactionConfig(nlp_engine="spacy"), flat=True,
        note="spaCy: what block extraction is worth"),
    "spacy-no-custom": EvalConfig(
        "spacy-no-custom",
        RedactionConfig(nlp_engine="spacy", use_custom_recognizers=False),
        note="spaCy: what the 12 recognizers are worth"),
    "stanford": EvalConfig(
        "stanford", RedactionConfig(nlp_engine="transformers"),
        note="clinical de-id model — current code default"),
    "stanford-t0.6": EvalConfig(
        "stanford-t0.6", RedactionConfig(nlp_engine="transformers", threshold=0.6),
        note="clinical model, noise floor raised"),
    "stanford-no-custom": EvalConfig(
        "stanford-no-custom",
        RedactionConfig(nlp_engine="transformers", use_custom_recognizers=False),
        note="clinical model: what the 12 recognizers are worth"),
    "obi": EvalConfig(
        "obi", RedactionConfig(nlp_engine="transformers",
                               transformer_model="obi/deid_roberta_i2b2"),
        note="alternative clinical model"),
}

DEFAULT_SET = ["spacy", "spacy-no-allowlist", "spacy-flat", "spacy-no-custom",
               "stanford", "stanford-t0.6", "stanford-no-custom"]


# --------------------------------------------------------------------------
# Scoring
# --------------------------------------------------------------------------


@dataclass
class DocScore:
    doc: str
    leaked: list = field(default_factory=list)
    over_redacted: list = field(default_factory=list)
    unreviewed: list = field(default_factory=list)
    n_redact: int = 0
    n_keep: int = 0
    n_detections: int = 0
    seconds: float = 0.0


@dataclass
class ConfigScore:
    name: str
    note: str = ""
    docs: list = field(default_factory=list)
    error: str = ""

    def _sum(self, attr) -> int:
        return sum(len(getattr(d, attr)) for d in self.docs)

    @property
    def leaked(self) -> int:
        return self._sum("leaked")

    @property
    def over_redacted(self) -> int:
        return self._sum("over_redacted")

    @property
    def unreviewed(self) -> int:
        return self._sum("unreviewed")

    @property
    def recall(self) -> float:
        total = sum(d.n_redact for d in self.docs)
        return (total - self.leaked) / total if total else 0.0

    @property
    def preservation(self) -> float:
        total = sum(d.n_keep for d in self.docs)
        return (total - self.over_redacted) / total if total else 1.0

    @property
    def seconds(self) -> float:
        return sum(d.seconds for d in self.docs)

    @property
    def n_detections(self) -> int:
        return sum(d.n_detections for d in self.docs)

    @property
    def precision(self) -> float:
        """
        Justified detections / all detections.

        ONLY meaningful once `unreviewed` is 0. Until then every unclassified
        detection is counted as a false positive, so this is a LOWER BOUND --
        pessimistic by exactly the number of items still awaiting triage.
        """
        total = self.n_detections
        if not total:
            return 0.0
        justified = total - self.over_redacted - self.unreviewed
        return max(0.0, justified / total)

    @property
    def f2(self) -> float:
        """
        F-beta with beta=2 — the de-identification standard, because recall is
        worth roughly double: a miss leaks PHI, a false positive costs a lab value.
        """
        p, r = self.precision, self.recall
        return (5 * p * r) / (4 * p + r) if (p + r) else 0.0


def probes_for(probes: dict, doc: str) -> tuple:
    """Merge the common block with this document's own entries."""
    common = probes.get("common") or {}
    own = (probes.get("documents") or {}).get(doc) or {}
    must_redact = list(common.get("must_redact") or []) + list(own.get("must_redact") or [])
    must_keep = list(common.get("must_keep") or []) + list(own.get("must_keep") or [])
    return must_redact, must_keep


def score_document(doc: str, redacted: str, spans: list, must_redact: list,
                   must_keep: list, seconds: float) -> DocScore:
    """
    Substring matching, case-insensitive, deliberately crude.

    It is biased toward REPORTING a leak: a probe that survives in any form
    counts against recall. A checker that under-reports would be worse than
    having no checker, because it would manufacture false confidence.
    """
    low = redacted.lower()

    leaked = [p for p in must_redact if p.lower() in low]
    over_redacted = [p for p in must_keep if p.lower() not in low]

    # Triage every detection: does it correspond to something we declared PHI?
    unreviewed = []
    for span in spans:
        text = span.text.strip().lower()
        if not text:
            continue
        if any(p.lower() in text or text in p.lower() for p in must_redact):
            continue                                   # justified detection
        if any(p.lower() in text or text in p.lower() for p in must_keep):
            continue                                   # already counted as over-redaction
        unreviewed.append(span.text.strip())

    return DocScore(
        doc=doc, leaked=leaked, over_redacted=over_redacted, unreviewed=unreviewed,
        n_redact=len(must_redact), n_keep=len(must_keep),
        n_detections=len(spans), seconds=seconds,
    )


def run_config(ec: EvalConfig, docs: list, probes: dict, verbose=True) -> ConfigScore:
    result = ConfigScore(name=ec.name, note=ec.note)
    if verbose:
        print(f"  {ec.name} ...", end="", flush=True)

    try:
        pipeline = RedactionPipeline(ec.config)
    except RuntimeError as exc:
        result.error = str(exc).splitlines()[0]
        if verbose:
            print(f" SKIPPED ({result.error})")
        return result

    for doc in docs:
        path = os.path.join(PDF_DIR, doc)
        if not os.path.isfile(path):
            continue
        must_redact, must_keep = probes_for(probes, doc)

        t0 = time.time()
        pages = [[p] for p in extract_pages(path)] if ec.flat else extract_page_blocks(path)
        results = [pipeline.redact_blocks(blocks) for blocks in pages]
        elapsed = time.time() - t0

        redacted = "\f".join(r.redacted for r in results)
        spans = [s for r in results for s in r.spans]
        result.docs.append(
            score_document(doc, redacted, spans, must_redact, must_keep, elapsed))

    if verbose:
        print(f" done  ({result.seconds:.1f}s)")
    return result


# --------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------


def validate_probes(probes: dict, docs: list) -> list:
    """
    Every probe string must actually occur in its document's text.

    A probe that isn't there silently corrupts the metrics in BOTH directions: a
    phantom must_keep reads as permanent over-redaction, and a phantom
    must_redact can never leak, so it inflates recall for free. Ground truth is
    hand-written, so it needs a check of its own.
    """
    problems = []
    for doc in docs:
        path = os.path.join(PDF_DIR, doc)
        if not os.path.isfile(path):
            problems.append(f"{doc}: file not found")
            continue
        text = "\n".join("\n".join(b) for b in extract_page_blocks(path)).lower()
        must_redact, must_keep = probes_for(probes, doc)
        for kind, items in (("must_redact", must_redact), ("must_keep", must_keep)):
            for item in items:
                if str(item).lower() not in text:
                    problems.append(f"{doc}: {kind} {item!r} does not appear in the document")
    return problems


def rank(scores: list) -> list:
    """Leaks first, then over-redaction, then noise. Failed configs last."""
    return sorted(
        scores,
        key=lambda s: (bool(s.error), s.leaked, s.over_redacted, s.unreviewed),
    )


def table(scores: list) -> str:
    hdr = (f"  {'CONFIG':<20} {'LEAKED':>7} {'RECALL':>8} {'PREC*':>7} {'F2*':>7} "
           f"{'OVER-RED':>9} {'PRESERVE':>9} {'UNREV':>6} {'TIME':>7}   NOTE")
    rows = [hdr, "  " + "-" * 118]
    for s in scores:
        if s.error:
            rows.append(f"  {s.name:<20} {'-':>7} {'-':>8} {'-':>7} {'-':>7} {'-':>9} "
                        f"{'-':>9} {'-':>6} {'-':>7}   SKIPPED: {s.error}")
            continue
        flag = "  <-- LEAKS" if s.leaked else ""
        rows.append(
            f"  {s.name:<20} {s.leaked:>7} {s.recall:>7.1%} {s.precision:>6.1%} "
            f"{s.f2:>6.1%} {s.over_redacted:>9} {s.preservation:>8.1%} "
            f"{s.unreviewed:>6} {s.seconds:>6.1f}s   {s.note}{flag}")
    rows.append("")
    rows.append("  * PREC and F2 are LOWER BOUNDS while UNREV > 0 — every untriaged")
    rows.append("    detection is counted as a false positive.")
    return "\n".join(rows)


def detail(scores: list, limit: int = 80) -> str:
    out = []
    for s in scores:
        if s.error:
            continue
        out.append(f"\n{'=' * 78}\n{s.name}\n{'=' * 78}")
        for d in s.docs:
            if not (d.leaked or d.over_redacted):
                out.append(f"  {d.doc:<28} clean  ({d.n_detections} detections)")
                continue
            out.append(f"  {d.doc}")
            if d.leaked:
                out.append(f"      !! LEAKED ({len(d.leaked)}): {', '.join(d.leaked)}")
            if d.over_redacted:
                out.append(f"      ~~ over-redacted ({len(d.over_redacted)}): "
                           f"{', '.join(d.over_redacted)}")
        noise = sorted({u for d in s.docs for u in d.unreviewed})
        if noise:
            shown = ", ".join(repr(n) for n in noise[:limit])
            more = f"  (+{len(noise) - limit} more)" if len(noise) > limit else ""
            out.append(f"\n  unreviewed detections ({len(noise)} unique): {shown}{more}")
            out.append("  → triage these into must_redact or must_keep in probes.yml")
    return "\n".join(out)


def markdown(scores: list, docs: list) -> str:
    best = next((s for s in scores if not s.error), None)
    lines = [
        "# PHI Redaction — Evaluation Report",
        "",
        f"{len(docs)} documents · {len([s for s in scores if not s.error])} configs "
        f"· ground truth: `evaluation/probes.yml`",
        "",
        "## Results",
        "",
        "| Config | Leaked | Recall | Over-redacted | Preservation | Unreviewed | Time | Note |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for s in scores:
        if s.error:
            lines.append(f"| `{s.name}` | — | — | — | — | — | — | SKIPPED: {s.error} |")
            continue
        lines.append(
            f"| `{s.name}` | **{s.leaked}** | {s.recall:.1%} | {s.over_redacted} | "
            f"{s.preservation:.1%} | {s.unreviewed} | {s.seconds:.1f}s | {s.note} |")

    lines += ["", "## Reading this", "",
              "- **Leaked** — PHI strings that survived into the output. "
              "The gate metric; anything above zero is a defect.",
              "- **Recall** — fraction of listed PHI removed.",
              "- **Over-redacted** — clinical strings destroyed. Costs summary quality, not privacy.",
              "- **Unreviewed** — detections matching neither list. Candidate false positives, "
              "not counted against any score.",
              "",
              "Ranked by leaks, then over-redaction, then noise. Over-redaction is annoying; "
              "under-redaction is a breach.",
              "",
              "## Limits", "",
              "Probe lists are not span annotations. **Precision is not computed** — a probe list "
              "cannot see PHI nobody listed. Recall is only as complete as `probes.yml`. "
              "Every unreviewed detection must be triaged into `must_redact` or `must_keep` "
              "before these numbers can be called precision and recall in the published sense.",
              ""]

    if best:
        lines += ["## Leaders", "",
                  f"- **Fewest leaks:** `{best.name}` "
                  f"({best.leaked} leaked, {best.recall:.1%} recall)"]
        clean = [s for s in scores if not s.error and s.over_redacted == 0]
        if clean:
            lines.append(f"- **No over-redaction:** " + ", ".join(f"`{s.name}`" for s in clean))
        lines.append("")

    lines += ["## Per-document errors", "", "```", detail(scores).strip(), "```", ""]
    return "\n".join(lines)


# --------------------------------------------------------------------------


def main(argv=None) -> int:
    # Windows consoles default to cp1252 and die on the arrows and em-dashes
    # below -- after a 2-minute transformer run, which is an expensive way to
    # lose a report. errors="replace" degrades rather than raises.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    p = argparse.ArgumentParser(description="Score redaction configs against probe lists.")
    p.add_argument("--configs", help="comma-separated config names (default: a fast set)")
    p.add_argument("--all", action="store_true", help="run every config including obi")
    p.add_argument("--list", action="store_true", help="list configs and exit")
    p.add_argument("--detail", action="store_true", help="print per-document errors")
    p.add_argument("--report", metavar="PATH", help="write a markdown report")
    p.add_argument("--gate", action="store_true", help="exit 1 if any config leaked")
    p.add_argument("--force", action="store_true",
                   help="score even if ground-truth validation fails")
    args = p.parse_args(argv)

    if args.list:
        print("\n  available configs:\n")
        for name, ec in CONFIGS.items():
            mark = "*" if name in DEFAULT_SET else " "
            print(f"   {mark} {name:<22} {ec.note}")
        print("\n   * = in the default set\n")
        return 0

    if not os.path.isfile(PROBES):
        print(f"error: no ground truth at {PROBES}", file=sys.stderr)
        return 2
    with open(PROBES, encoding="utf-8") as fh:
        probes = yaml.safe_load(fh)

    docs = sorted((probes.get("documents") or {}).keys())
    if not docs:
        print("error: probes.yml lists no documents", file=sys.stderr)
        return 2

    problems = validate_probes(probes, docs)
    if problems:
        print("\n  GROUND TRUTH PROBLEMS — fix these before trusting any number:\n",
              file=sys.stderr)
        for p_ in problems:
            print(f"    {p_}", file=sys.stderr)
        print(file=sys.stderr)
        if not args.force:
            print("  refusing to score against broken ground truth (--force to override)\n",
                  file=sys.stderr)
            return 2

    if args.all:
        names = list(CONFIGS)
    elif args.configs:
        names = [n.strip() for n in args.configs.split(",")]
    else:
        names = DEFAULT_SET

    unknown = [n for n in names if n not in CONFIGS]
    if unknown:
        print(f"error: unknown config(s): {', '.join(unknown)}", file=sys.stderr)
        print(f"       available: {', '.join(CONFIGS)}", file=sys.stderr)
        return 2

    print(f"\n{len(docs)} documents x {len(names)} configs\n")
    scores = [run_config(CONFIGS[n], docs, probes) for n in names]
    scores = rank(scores)

    print(f"\n{table(scores)}\n")

    if args.detail:
        print(detail(scores))
        print()

    if args.report:
        with open(args.report, "w", encoding="utf-8") as fh:
            fh.write(markdown(scores, docs))
        print(f"  wrote {args.report}\n")

    leaked = sum(s.leaked for s in scores if not s.error)
    if args.gate and leaked:
        print(f"  GATE FAILED — {leaked} leak(s) across all configs\n", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
