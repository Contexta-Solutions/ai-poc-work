#!/usr/bin/env python
"""
Redact PHI from a clinical PDF (or text file) and show what happened.

    python redact.py report.pdf
    python redact.py report.pdf --keep DATE_TIME          # keep dates for summarisation
    python redact.py report.pdf --nlp-engine transformers # clinical de-id model
    python redact.py report.pdf --flat                    # old linear extraction, to compare
    python redact.py note.txt --json out.json

Outputs:
    1. side-by-side original vs redacted
    2. entity table (type, score, position, matched text)
    3. <input>.redacted.pdf   -- glyphs removed, not covered over
    4. --json <path>          -- machine-readable, for diffing runs

Three defences, in order of how much they cost you:

  block extraction  (free)   stops spans crossing table columns, so units like
                             `U/L` are never swallowed into the next test name
  allow-list        (free)   never redact known units, lab tests, methods, drugs
  clinical NER      (~500MB) a model that has actually seen clinical text and
                             knows "Alanine Aminotransferase" is not a person

Setup:
    pip install -r requirements.txt
    python -m spacy download en_core_web_lg

    # for --nlp-engine transformers:
    pip install -r requirements-transformers.txt
    python -m spacy download en_core_web_sm

    NOT `pip install "transformers>=4.40"` -- Presidio gates on
    spacy-huggingface-pipelines, not on transformers, and that package caps
    transformers below 5.x. Installing transformers alone resolves to 5.x and
    fails with "NLP engine 'transformers' is not available".
"""

import argparse
import os
import sys

from contexta_redact import RedactionConfig, RedactionPipeline
from contexta_redact.allowlist import load_extra_terms
from contexta_redact.engine import TRANSFORMER_MODELS
from contexta_redact.pdf import extract_page_blocks, extract_pages
from contexta_redact.report import entity_table, side_by_side, summary_counts, to_json


def read_pages(path: str, flat: bool) -> list:
    """
    Returns a list of pages; each page is a list of blocks.

    `--flat` collapses each page to a single block, reproducing the old
    behaviour so you can measure what block extraction actually bought.
    """
    if path.lower().endswith(".pdf"):
        return [[p] for p in extract_pages(path)] if flat else extract_page_blocks(path)
    with open(path, encoding="utf-8") as fh:
        return [[fh.read()]]


def parse_args(argv=None):
    p = argparse.ArgumentParser(
        description="Redact PHI from clinical PDFs using Presidio + Indian recognizers.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("input", help="PDF or .txt file to redact")

    g = p.add_argument_group("detection")
    g.add_argument("--nlp-engine", choices=["spacy", "transformers"], default="spacy",
                   help="spacy (fast, general) or transformers (clinical de-id model)")
    g.add_argument("--transformer-model", default="stanford",
                   help=f"{' | '.join(TRANSFORMER_MODELS)} or any HF model id "
                        f"(default: stanford)")
    g.add_argument("--model", default=None, help="spaCy model (default en_core_web_lg)")
    g.add_argument("--threshold", type=float, default=None,
                   help="Minimum confidence (default 0.35)")
    g.add_argument("--flat", action="store_true",
                   help="Linear text extraction instead of layout blocks (comparison)")

    g = p.add_argument_group("policy")
    g.add_argument("--keep", nargs="*", default=[], metavar="ENTITY",
                   help="Detect but do NOT redact, e.g. --keep DATE_TIME. HIPAA "
                        "treats dates as identifiers; keeping them is a deliberate "
                        "trade for summarisation quality.")
    g.add_argument("--drop", nargs="*", default=[], metavar="ENTITY",
                   help="Ignore an entity type entirely, e.g. --drop URL")
    g.add_argument("--no-allow-list", action="store_true",
                   help="Disable the clinical allow-list (units, lab tests, methods)")
    g.add_argument("--allow-list-file", metavar="PATH",
                   help="Extra never-redact terms, one per line")

    g = p.add_argument_group("output")
    g.add_argument("--json", metavar="PATH", help="Write the full result as JSON")
    g.add_argument("--out-pdf", metavar="PATH",
                   help="Redacted PDF path (default: <input>.redacted.pdf)")
    g.add_argument("--no-pdf", action="store_true", help="Skip writing a redacted PDF")
    g.add_argument("--width", type=int, default=150, help="Side-by-side width")
    g.add_argument("--quiet", action="store_true", help="Entity table only")
    return p.parse_args(argv)


def build_config(args) -> RedactionConfig:
    kwargs = {
        "keep": frozenset(args.keep),
        "drop": frozenset(args.drop),
        "nlp_engine": args.nlp_engine,
        "use_clinical_allow_list": not args.no_allow_list,
        "transformer_model": TRANSFORMER_MODELS.get(
            args.transformer_model, args.transformer_model
        ),
    }
    if args.threshold is not None:
        kwargs["threshold"] = args.threshold
    if args.model is not None:
        kwargs["model"] = args.model
    if args.allow_list_file:
        kwargs["allow_list"] = tuple(load_extra_terms(args.allow_list_file))
    return RedactionConfig(**kwargs)


def main(argv=None) -> int:
    args = parse_args(argv)

    if not os.path.isfile(args.input):
        print(f"error: no such file: {args.input}", file=sys.stderr)
        return 2

    pages = read_pages(args.input, args.flat)
    if not any(b.strip() for page in pages for b in page):
        print("error: no extractable text. Scanned/image-only PDF?", file=sys.stderr)
        print("       Text redaction cannot help here — this needs OCR first.",
              file=sys.stderr)
        return 3

    config = build_config(args)
    try:
        pipeline = RedactionPipeline(config)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 4

    page_results = [pipeline.redact_blocks(blocks) for blocks in pages]

    # Stitch pages into document coordinates for display and JSON.
    from contexta_redact.engine import Span

    combined_spans, combined_kept, cursor = [], [], 0
    for res in page_results:
        combined_spans += [
            Span(s.entity_type, s.start + cursor, s.end + cursor, s.score, s.text)
            for s in res.spans
        ]
        combined_kept += [
            Span(s.entity_type, s.start + cursor, s.end + cursor, s.score, s.text)
            for s in res.kept
        ]
        cursor += len(res.original) + 1  # +1 for the \f join

    class _Combined:
        original = "\f".join(r.original for r in page_results)
        redacted = "\f".join(r.redacted for r in page_results)
        spans = combined_spans
        kept = combined_kept

    combined = _Combined()

    pdf_stats = out_pdf = None
    if args.input.lower().endswith(".pdf") and not args.no_pdf:
        from contexta_redact.pdf import write_redacted_pdf

        out_pdf = args.out_pdf or f"{os.path.splitext(args.input)[0]}.redacted.pdf"
        if os.path.abspath(out_pdf) == os.path.abspath(args.input):
            print("error: refusing to overwrite the source PDF", file=sys.stderr)
            return 5
        pdf_stats = write_redacted_pdf(args.input, out_pdf, [r.spans for r in page_results])

    # ---- output ----------------------------------------------------------
    engine_desc = (
        f"transformers:{config.transformer_model}"
        if config.nlp_engine == "transformers"
        else f"spacy:{config.model}"
    )
    extraction = "flat" if args.flat else "blocks"

    if not args.quiet:
        print(f"\n{'=' * args.width}")
        print(f"  {args.input}   ({len(pages)} page(s), {engine_desc}, "
              f"extraction={extraction}, threshold={config.threshold}, "
              f"allow_list={'off' if args.no_allow_list else 'on'})")
        print("=" * args.width)
        print(f"\n{side_by_side(combined.original, combined.redacted, args.width)}")

    print("\n--- entities ---")
    print(entity_table(combined.spans, combined.kept))
    print(f"\n  redacted: {summary_counts(combined.spans)}")
    if combined.kept:
        print(f"  kept:     {summary_counts(combined.kept)}")

    if pdf_stats is not None:
        print("\n--- redacted pdf ---")
        print(f"  wrote {out_pdf}")
        print(f"  {pdf_stats.boxes_drawn} box(es) over "
              f"{pdf_stats.spans_requested} requested span(s)")
        if pdf_stats.too_short:
            print(f"  skipped {len(pdf_stats.too_short)} needle(s) under "
                  f"{len(pdf_stats.too_short) and 3} chars: "
                  f"{', '.join(repr(t) for t in pdf_stats.too_short)}")
        if pdf_stats.runaway:
            print(f"\n  !! {len(pdf_stats.runaway)} runaway needle(s) skipped — too "
                  f"generic to be PHI, redacting them would black out the page:")
            for t, n in pdf_stats.runaway:
                print(f"       {t!r} matched {n} times")
        if pdf_stats.not_located:
            print(f"\n  !! {len(pdf_stats.not_located)} span(s) NOT located on the page "
                  f"and still present in the PDF:")
            for t in pdf_stats.not_located:
                print(f"       {t!r}")
            print("     (text search vs page layout mismatch — usually a line break)")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            fh.write(to_json(args.input, combined, pdf_stats, config))
        print(f"\n  wrote {args.json}")

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
