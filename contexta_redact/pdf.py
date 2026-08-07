"""
PDF in, redacted PDF out.

Uses PyMuPDF, which apps/py-backend already depends on -- same library that
extracts attachment text in summary/service.py, so what you see here is what
that code path would see.

On real redaction: `apply_redactions()` removes the glyphs from the content
stream. It is not a black rectangle drawn on top. That distinction is the whole
game -- an overlay is trivially undone with any PDF editor, or by selecting the
text underneath and copying it.
"""

from dataclasses import dataclass

try:
    import fitz  # PyMuPDF
except ImportError:  # PyMuPDF >= 1.24 also exposes the modern name
    import pymupdf as fitz


#: A needle shorter than this matches far too much. Belt-and-braces against
#: RedactionConfig.min_span_chars: this file must be safe on its own, because
#: anything that reaches search_for gets applied to the whole page.
MIN_NEEDLE_CHARS = 3

#: More hits than this on one page means the needle is generic, not repeated
#: PHI. On the Tenet report a PERSON span of 'A' matched 118 times and blacked
#: out every letter A in the document -- lab test names, reference ranges,
#: section headers. Redacting the entire page is not a safe failure mode: it
#: destroys the clinical content while telling you it succeeded.
MAX_RECTS_PER_SPAN = 12


@dataclass
class PdfRedactionStats:
    pages: int = 0
    spans_requested: int = 0
    boxes_drawn: int = 0
    not_located: list = None   # entity texts the layout search could not find
    too_short: list = None     # skipped: needle below MIN_NEEDLE_CHARS
    runaway: list = None       # skipped: (needle, hit_count) over the cap

    def __post_init__(self) -> None:
        if self.not_located is None:
            self.not_located = []
        if self.too_short is None:
            self.too_short = []
        if self.runaway is None:
            self.runaway = []


def extract_pages(path: str) -> list:
    """Per-page plain text. Page-scoped so entity offsets stay page-local."""
    with fitz.open(path) as doc:
        return [page.get_text() for page in doc]


def extract_text(path: str) -> str:
    """Whole document as one string, pages separated by form feeds."""
    return "\f".join(extract_pages(path))


def extract_page_blocks(path: str) -> list:
    """
    Per page, the text of each layout block -- the geometry-aware alternative
    to `extract_pages`.

    A lab report is a table. `get_text()` linearizes it into a stream where the
    units column and the test-name column end up adjacent, separated by nothing
    but a newline, which is how `U/L\\nGamma GT` becomes one ORGANIZATION. Blocks
    preserve the layout grouping, so analysis can be confined within a cell.

    `get_text("blocks")` yields (x0, y0, x1, y1, text, block_no, block_type);
    block_type 1 is an image, which has no text to analyze.
    """
    pages = []
    with fitz.open(path) as doc:
        for page in doc:
            blocks = [
                b[4].strip()
                for b in page.get_text("blocks")
                if len(b) > 6 and b[6] == 0 and b[4].strip()
            ]
            pages.append(blocks)
    return pages


def write_redacted_pdf(src: str, dst: str, page_spans: list) -> PdfRedactionStats:
    """
    Write a copy of `src` with every span in `page_spans[i]` removed from page i.

    `page_spans` must be parallel to the pages returned by extract_pages().

    Caveat worth knowing: located by text search, not by offset. PyMuPDF's
    extracted text and its on-page layout are not the same coordinate space --
    a value broken across a line, or split into separate spans by kerning, may
    not be found. Those land in `not_located`, and every entry there is PHI that
    is still in the output file. Check it; do not assume it is empty.
    """
    stats = PdfRedactionStats()

    with fitz.open(src) as doc:
        stats.pages = doc.page_count

        for page_index, page in enumerate(doc):
            spans = page_spans[page_index] if page_index < len(page_spans) else []
            for span in spans:
                needle = span.text.strip()
                stats.spans_requested += 1
                if not needle:
                    continue

                if len(needle) < MIN_NEEDLE_CHARS:
                    stats.too_short.append(needle)
                    continue

                rects = page.search_for(needle)
                if not rects:
                    stats.not_located.append(needle)
                    continue

                if len(rects) > MAX_RECTS_PER_SPAN:
                    # Generic string, not repeated PHI. Blacking out all of it
                    # would destroy the page; report instead of guessing.
                    stats.runaway.append((needle, len(rects)))
                    continue

                for rect in rects:
                    page.add_redact_annot(rect, fill=(0, 0, 0))
                    stats.boxes_drawn += 1

            # Per page: applying removes the glyphs under every annot on it.
            page.apply_redactions()

        doc.save(dst, garbage=4, deflate=True)

    return stats
