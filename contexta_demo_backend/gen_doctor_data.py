"""Regenerates doctor_data.py from the two source markdown files at the repo root.

The markdown files are gitignored (`*.md`), so they never reach a deployment --
their contents have to live inside a committed .py file for the bot to read them.
Run this after editing either markdown file:

    python gen_doctor_data.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTEXT_SRC = ROOT / "internal_doctor_chatbot_context.md"
QA_SRC = ROOT / "internal_doctor_chatbot_qa_training.md"
OUT = Path(__file__).resolve().parent / "doctor_data.py"

HEADER = '''"""Static knowledge base for the internal Doctor Assistant (/doctor) ONLY.

GENERATED FILE -- do not edit by hand. Run `python gen_doctor_data.py` instead;
the source of truth is the two markdown files at the repo root.

Kept separate from ortho_clinic_data.py (ChatBot) and doctors_data.py (Visit
Notes) so changes here can never touch either shipped feature. Read-only.

The whole knowledge base measures 11,592 tokens on claude-sonnet-4-6 (counted via
usage.cache_creation_input_tokens, not estimated -- markdown tables tokenize about
twice as dense as a chars/4 guess suggests). That is ~1% of Sonnet's 1M window, so
there is no retrieval step: both documents go into the cached system prompt
verbatim and Claude answers from them. See doctor_service.py.
"""

# Reference "today" for every relative query ("last week", "next week").
# Deliberately frozen, not a live clock: the QA answers below are pre-computed
# against this date, and a moving date would both invalidate them and break the
# prompt cache on every request.
REFERENCE_DATE = "Thursday, 16 July 2026"

'''


def emit(name: str, text: str) -> str:
    if "'''" in text:
        raise ValueError(f"{name} contains a triple-quote; adjust the delimiter")
    return f"{name} = r'''\n{text.strip()}\n'''\n\n"


def main() -> None:
    context_md = CONTEXT_SRC.read_text(encoding="utf-8")
    qa_md = QA_SRC.read_text(encoding="utf-8")

    body = HEADER + emit("CONTEXT_MD", context_md) + emit("QA_MD", qa_md)
    OUT.write_text(body, encoding="utf-8")

    print(f"wrote {OUT.name}: {len(context_md)} + {len(qa_md)} chars")
    print("Token count is NOT chars/4 -- that undercounts these tables ~2x. To "
          "re-measure, call doctor_service.warm_cache() and read cache_write.")


if __name__ == "__main__":
    main()
