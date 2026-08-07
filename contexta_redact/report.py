"""
Rendering: entity table, side-by-side diff, JSON.

Stdlib only. A redaction tool that pulls in a table-formatting library to print
its own output has its priorities backwards.
"""

import json
import textwrap
from collections import Counter


def entity_table(spans: list, kept: list = ()) -> str:
    """One row per detection, highest confidence first. Kept entities marked."""
    rows = [(s, False) for s in spans] + [(s, True) for s in kept]
    if not rows:
        return "  (no entities detected)"

    rows.sort(key=lambda r: (-r[0].score, r[0].start))
    width = max(len(s.entity_type) for s, _ in rows)

    out = [f"  {'ENTITY'.ljust(width)}  SCORE  POS      TEXT"]
    for span, is_kept in rows:
        flag = "  [KEPT]" if is_kept else ""
        snippet = span.text if len(span.text) <= 40 else span.text[:37] + "..."
        out.append(
            f"  {span.entity_type.ljust(width)}  {span.score:>5.2f}  "
            f"{span.start:>5}    {snippet!r}{flag}"
        )
    return "\n".join(out)


def summary_counts(spans: list) -> str:
    """`PERSON x3, IN_AADHAAR x1` — the at-a-glance line."""
    if not spans:
        return "nothing detected"
    counts = Counter(s.entity_type for s in spans)
    return ", ".join(f"{k} x{v}" for k, v in counts.most_common())


def side_by_side(original: str, redacted: str, total_width: int = 150) -> str:
    """
    Original on the left, redacted on the right.

    Wrapped independently per column, so the two sides drift out of vertical
    alignment once a replacement changes a line's length. That is expected --
    this is for eyeballing what got caught, not for a precise diff. Use the JSON
    output when you need exact positions.
    """
    col = max(30, (total_width - 3) // 2)

    def wrap(text: str) -> list:
        lines = []
        for para in text.splitlines() or [""]:
            lines.extend(textwrap.wrap(para, col) or [""])
        return lines

    left, right = wrap(original), wrap(redacted)
    height = max(len(left), len(right))
    left += [""] * (height - len(left))
    right += [""] * (height - len(right))

    head = f"  {'ORIGINAL'.ljust(col)} | REDACTED"
    rule = f"  {'-' * col}-+-{'-' * col}"
    body = [f"  {l.ljust(col)} | {r}" for l, r in zip(left, right)]
    return "\n".join([head, rule, *body])


def to_dict(
    source: str,
    result,
    pdf_stats=None,
    config=None,
) -> dict:
    """
    Machine-readable output.

    Deliberately includes `not_located` and the kept-entity list: a report that
    only shows what worked is a report you cannot audit.
    """
    payload = {
        "source": source,
        "config": {
            "model": getattr(config, "model", None),
            "threshold": getattr(config, "threshold", None),
            "kept_entity_types": sorted(getattr(config, "keep", []) or []),
        },
        "counts": dict(Counter(s.entity_type for s in result.spans)),
        "redacted_text": result.redacted,
        "entities": [
            {
                "entity_type": s.entity_type,
                "start": s.start,
                "end": s.end,
                "score": round(s.score, 4),
                "text": s.text,
            }
            for s in result.spans
        ],
        "kept": [
            {
                "entity_type": s.entity_type,
                "start": s.start,
                "end": s.end,
                "score": round(s.score, 4),
                "text": s.text,
            }
            for s in result.kept
        ],
    }
    if pdf_stats is not None:
        payload["pdf"] = {
            "pages": pdf_stats.pages,
            "spans_requested": pdf_stats.spans_requested,
            "boxes_drawn": pdf_stats.boxes_drawn,
            "not_located": pdf_stats.not_located,
        }
    return payload


def to_json(*args, **kwargs) -> str:
    return json.dumps(to_dict(*args, **kwargs), indent=2, ensure_ascii=False)
