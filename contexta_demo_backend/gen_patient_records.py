"""Regenerates doctor_data.py from the source markdown at the repo root.

The markdown is gitignored (`*.md`), so it never reaches a deployment -- its
contents have to live inside a committed .py file for the bot to read them.
Run this after editing the markdown:

    python gen_doctor_data.py

Only the RECORDS file is embedded. The companion Q&A file
(internal_doctor_chatbot_qa_training.md) is deliberately NOT used: every answer
in it is derivable from these records, and feeding the model an answer key makes
it match questions instead of reading the chart -- which fails the moment a
doctor phrases something the key doesn't anticipate. Verified that the model
derives the same totals, breakdowns and trends unaided.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTEXT_SRC = ROOT / "internal_doctor_chatbot_context.md"
OUT = Path(__file__).resolve().parent / "doctor_data.py"

HEADER = '''"""Static patient records for the internal Doctor Assistant (/doctor) ONLY.

GENERATED FILE -- do not edit by hand. Run `python gen_doctor_data.py` instead;
the source of truth is the markdown at the repo root.

Kept separate from ortho_clinic_data.py (ChatBot) and doctors_data.py (Visit
Notes) so changes here can never touch either shipped feature. Read-only.

This is the raw chart -- three patients' visit histories plus the surgical
schedule. There is no answer key and no retrieval step: the whole thing is ~1% of
Sonnet's 1M window, so it goes into the cached system prompt verbatim and the
model derives each answer by reading it. See doctor_service.py.
"""

# Reference "today" for every relative query ("last week", "next week").
# Deliberately frozen rather than a live clock: the records describe a fixed
# window (surgeries Jan-Aug 2026), so a real clock would drift out of them and
# make "next week" empty. It also keeps the prompt byte-stable, which is what
# lets the whole thing cache.
REFERENCE_DATE = "Thursday, 16 July 2026"

'''


def emit(name: str, text: str) -> str:
    if "'''" in text:
        raise ValueError(f"{name} contains a triple-quote; adjust the delimiter")
    return f"{name} = r'''\n{text.strip()}\n'''\n\n"


def main() -> None:
    records_md = CONTEXT_SRC.read_text(encoding="utf-8")

    body = HEADER + emit("RECORDS_MD", records_md)
    OUT.write_text(body, encoding="utf-8")

    print(f"wrote {OUT.name}: {len(records_md)} chars")
    print("Token count is NOT chars/4 -- that undercounts these tables ~2x. To "
          "re-measure, call doctor_service.warm_cache() and read cache_write.")


if __name__ == "__main__":
    main()
