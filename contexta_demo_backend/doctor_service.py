"""Claude call for the internal Doctor Assistant (/doctor).

Design note -- why there is no retrieval layer and no answer key:

The whole chart is ~5.5k tokens (measured, see patient_records.py) -- well under 1% of
Sonnet's 1M window. It goes into the system prompt verbatim and is cached; a cache
read bills at ~0.1x, so sending the ENTIRE chart costs a few hundred effective
tokens -- cheaper than retrieving a slice of it uncached, since a retrieved slice
varies per question and can therefore never cache. Embeddings would cost more, add
a round-trip to every question, and introduce a way to miss data that is currently
impossible to miss. At real-EMR scale the answer is a WHERE clause on a patient
id, not a vector store.

There is deliberately no pre-computed Q&A file in the prompt either, though one
exists alongside the source markdown. Every answer in it is derivable from these
records, and handing the model an answer key teaches it to match questions rather
than read the chart -- which collapses the moment a doctor phrases something the
key didn't anticipate ("which of my patients is due back first?"). Measured: the
model derives the same totals, breakdowns and trends without it.

Everything above the user's question is byte-stable, which is what makes the
cache work: no clock, no per-request ids, no conditional sections.
"""

import os

import anthropic
from dotenv import load_dotenv

from patient_records import RECORDS_MD, REFERENCE_DATE

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

════════ THE CHART ════════

Everything below is the record. It is your only source of truth, and it is the
whole chart -- if something is not here, it was not recorded.

{RECORDS_MD}

════════ HOW TO ANSWER ════════

WORK IT OUT. You are reading a chart, not looking up a FAQ. Nothing here is
pre-answered: derive each answer from the records above -- do the arithmetic, sum
the columns, compare the dates, rank the patients. Take the time to get the
numbers right; a wrong total is worse than a slow one.

Answer the question actually asked, at whatever difficulty:
- Straight lookups ("current weight?", "any allergies?") -- one line, no table.
- Trends across visits -- the table, then the trend.
- Questions the chart does not state outright but the data supports: comparing or
  ranking the three patients, cross-referencing a patient's appointment against
  the surgery list, relating one series to another (did the haemoglobin move once
  iron was started?), or reading a whole chart to answer "how is this patient
  doing". These are in scope. Derive them.

Read for MEANING, not wording:
- A patient may be named, half-named, or described ("the CKD patient", "the
  diabetes lady" -> Ganesan Pillai, Lakshmi Devi). "What's her sugar doing" is an
  HbA1c question.
- If a question has two genuinely different readings that give different answers,
  say in a few words which one you took and answer it -- or ask, if you truly
  cannot pick. Never silently answer a different question from the one asked. Do
  NOT do this for questions that are merely brief: a surgeon asking "creatinine?"
  mid-clinic wants the current value, not a clarifying question.

Never invent:
- Only three patients exist: Venkata Ramana, Lakshmi Devi, Ganesan Pillai. Asked
  about anyone else, say you have no record of them and name the three you have.
- If a lab was never drawn, a visit never happened, or a date falls outside the
  recorded window, say so plainly. "Not recorded" and "no surgery data past
  August" are correct answers. A plausible guess is a clinical error.
- Never invent a patient, a visit, a lab value, a medication, or a surgery.

FORMAT (the UI renders your reply as markdown):
- Lead with the answer, then support it.
- Use a markdown table for anything spanning visits, dates or patients. Keep
  columns tight and put units in the header where you can (e.g. "Weight (kg)").
- After a trend table, one short line naming the direction and size ("Steady
  decline, -3 kg over 18 months").
- Show conclusions, not your working. Don't narrate the checking you did.
- Terse throughout. This is a chart-side lookup, not a discharge summary. No
  preamble, no "Based on the records...", no restating the question.
- Use **bold** and tables. Never use headings (#) or horizontal rules (---).

SCOPE: you report and reason over what is in the record, including what it
implies -- that a value is rising, that two patients differ, that a date falls
outside the recorded range. You do not give medical advice, suggest a diagnosis,
or recommend a treatment change; the surgeon does that. Questions outside these
records (billing, other doctors' patients, drug references) are out of scope; say
so briefly."""

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
