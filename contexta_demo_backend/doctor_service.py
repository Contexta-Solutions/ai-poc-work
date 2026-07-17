"""Claude call for the internal Doctor Assistant (/doctor).

Design note -- why there is no retrieval layer here:

The entire knowledge base is 11,592 tokens (measured, see doctor_data.py) -- about
1% of Sonnet's 1M window. Both documents go into the system prompt verbatim and
are cached; a cache read bills at ~0.1x, so sending the WHOLE knowledge base costs
~1.2k effective tokens, which is cheaper than retrieving even a 2k-token slice
uncached (retrieved slices vary per question, so they can never be cached).
Embeddings would cost more, add an embedding round-trip to every question, and
introduce a way to miss data that is currently impossible to miss. If this ever
grows to a real patient roster, the answer is a WHERE clause on a patient id --
not a vector store.

Everything above the user's question is byte-stable, which is what makes the
cache work: no clock, no per-request ids, no conditional sections.
"""

import os

import anthropic
from dotenv import load_dotenv

from doctor_data import CONTEXT_MD, QA_MD, REFERENCE_DATE

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=api_key) if api_key else None

MODEL = "claude-sonnet-4-6"

# Answers are terse tables by design, not prose. 2000 leaves room for the
# longest one (the 6-month monthly trend table) without inviting an essay.
MAX_TOKENS = 2000

DOCTOR_NAME = "Dr. Suresh Kumar Nair"

_SYSTEM_PROMPT = f"""You are the Clinical Assistant inside the Contexta Health EMR, answering questions for {DOCTOR_NAME} about his own patients and his own surgical schedule. You are an internal, doctor-facing tool -- your user is the treating surgeon, not a patient.

TODAY IS: {REFERENCE_DATE}.
Resolve every relative date ("last week", "next week", "last month", "next month", "in the last 3 months") against THIS date and nothing else. Never use a real-world clock.

════════ KNOWLEDGE BASE ════════

The two documents below are your ONLY source of truth. The first holds the raw
records; the second holds answers already computed from them.

--- DOCUMENT 1: PATIENT RECORDS & SURGERY SCHEDULE ---
{CONTEXT_MD}

--- DOCUMENT 2: PRE-COMPUTED ANSWERS ---
{QA_MD}

════════ HOW TO ANSWER ════════

- DOCUMENT 2 IS AUTHORITATIVE. If it already answers the question -- even phrased
  differently -- reuse its exact figures. Do not recompute a total, re-sum a
  column, or redo date arithmetic that Document 2 has already done. Where the two
  documents could be read as disagreeing, Document 2 wins.
- Match on MEANING, not wording. A doctor will not phrase things the way Document
  2 does. "what's her sugar doing", "how's the diabetes going", and "HbA1c trend
  for Lakshmi Devi" are the same question -- answer all of them from the HbA1c
  table. Same for a patient referred to by first name, surname, or condition
  ("the CKD patient" is Ganesan Pillai).
- ONLY the three patients in Document 1 exist: Venkata Ramana, Lakshmi Devi,
  Ganesan Pillai. If asked about anyone else, say you have no record of that
  patient and name the three you do have. Never invent a patient, a visit, a lab
  value, a medication, or a surgery.
- If a question is about a real patient but the data isn't recorded (a lab that
  was never drawn, a visit that never happened), say so plainly. An honest "not
  recorded" is correct; a plausible guess is a clinical error.

FORMAT (the UI renders your reply as markdown):
- Lead with the answer. For a single fact, one short line -- no table.
- For anything across visits or dates, use a markdown table. Keep columns tight
  and put units in the header where you can (e.g. "Weight (kg)").
- After a trend table, add one short line naming the trend and direction, the way
  Document 2 does ("Steady decline, -3 kg over 18 months").
- Terse throughout. This is a chart-side lookup, not a discharge summary. No
  preamble, no "Based on the records...", no restating the question.
- Use **bold** and tables. Never use headings (#) or horizontal rules (---).

SCOPE: you report what is in the record. You do not give medical advice, suggest
diagnoses, or recommend treatment changes -- the surgeon does that. Questions
outside these records (billing, other doctors' patients, drug references) are out
of scope; say so briefly."""

# The single cache breakpoint. Everything before it -- instructions, the frozen
# date, both documents -- is identical on every request, so this whole block is
# written once and then read at ~0.1x for an hour. The 1h TTL costs 2x on that
# one write and survives the gaps between stall visitors, which the default 5m
# TTL would not.
_SYSTEM_BLOCK = [{
    "type": "text",
    "text": _SYSTEM_PROMPT,
    "cache_control": {"type": "ephemeral", "ttl": "1h"},
}]


def _require_client() -> None:
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY is missing from .env file")


def warm_cache() -> dict:
    """Write the cache without paying for an answer.

    max_tokens=0 runs prefill and returns immediately with empty content, so the
    first real question of the day reads a hot cache instead of waiting on a cold
    write. The frontend fires this on mount -- the cache warms while the doctor is
    still reading the chart.

    The generation params below MUST stay identical to ask_doctor_bot's. They look
    pointless on a request that generates nothing, but they are part of the cache
    key: a warm call that omits output_config writes an entry keyed differently
    from the one real questions read, so the warm silently does nothing and the
    first question still pays the cold write. Verified via cache_read_input_tokens.
    """
    _require_client()
    response = client.messages.create(
        model=MODEL,
        max_tokens=0,
        thinking={"type": "disabled"},
        output_config={"effort": "low"},
        system=_SYSTEM_BLOCK,
        messages=[{"role": "user", "content": "warmup"}],
    )
    return _usage(response)


def ask_doctor_bot(question: str, history: list) -> tuple[str, dict]:
    """Answer one question. Returns (markdown_answer, cache_usage)."""
    _require_client()

    messages = []
    for turn in history[-8:]:
        role = "assistant" if turn.role == "bot" else "user"
        if turn.content.strip():
            messages.append({"role": role, "content": turn.content})
    messages.append({"role": "user", "content": question})

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            # Thinking off + low effort: these are table lookups against answers
            # that are already computed. Sonnet 4.6 defaults to effort "high",
            # which buys nothing here and costs latency in front of a visitor.
            thinking={"type": "disabled"},
            output_config={"effort": "low"},
            system=_SYSTEM_BLOCK,
            messages=messages,
        )
    except Exception as e:
        raise RuntimeError(f"Claude API Error: {str(e)}")

    text = next((b.text for b in response.content if b.type == "text"), "")
    return text, _usage(response)


def _usage(response) -> dict:
    """Cache telemetry. cache_read should be ~6k on every request after the
    first; a persistent 0 means something upstream broke byte-stability."""
    u = response.usage
    return {
        "cache_read": getattr(u, "cache_read_input_tokens", 0) or 0,
        "cache_write": getattr(u, "cache_creation_input_tokens", 0) or 0,
        "uncached_input": u.input_tokens,
        "output": u.output_tokens,
    }
