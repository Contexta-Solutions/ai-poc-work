"""
Presidio pipeline assembly.

One place that knows how to build a configured analyzer, so the CLI, the tests
and anything that later imports this all get identical detection behaviour.
Divergence here is how two callers end up with different leak rates and nobody
can explain why.
"""

from dataclasses import dataclass, field

from presidio_analyzer import AnalyzerEngine, RecognizerResult
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

from .allowlist import clinical_allow_list
from .recognizers import LABEL_ANCHORED_ENTITIES, build_indian_recognizers

DEFAULT_MODEL = "en_core_web_lg"
DEFAULT_THRESHOLD = 0.35

#: Clinical de-identification transformers. Unlike spaCy these were trained ON
#: clinical text, so they have seen "Alanine Aminotransferase" and know it is
#: not a person. That is the fix for the false positives spaCy produces on lab
#: reports -- allow-lists only suppress the ones you thought to enumerate.
TRANSFORMER_MODELS = {
    "stanford": "StanfordAIMI/stanford-deidentifier-base",
    "obi": "obi/deid_roberta_i2b2",
}

#: Both models use i2b2-derived label schemes. Naming varies between them and
#: between revisions, so map generously and treat anything unmapped as a signal
#: to check the model card -- unmapped labels are silently dropped by Presidio.
TRANSFORMER_ENTITY_MAPPING = {
    "PATIENT": "PERSON",
    "DOCTOR": "PERSON",
    "STAFF": "PERSON",
    "HCW": "PERSON",
    "PER": "PERSON",
    "NAME": "PERSON",
    "HOSPITAL": "ORGANIZATION",
    "HOSP": "ORGANIZATION",
    "PATORG": "ORGANIZATION",
    "ORG": "ORGANIZATION",
    "VENDOR": "ORGANIZATION",
    "LOC": "LOCATION",
    "LOCATION": "LOCATION",
    "CITY": "LOCATION",
    "STATE": "LOCATION",
    "STREET": "LOCATION",
    "COUNTRY": "LOCATION",
    "ZIP": "LOCATION",
    "DATE": "DATE_TIME",
    "TIME": "DATE_TIME",
    "AGE": "AGE",
    "PHONE": "PHONE_NUMBER",
    "FAX": "PHONE_NUMBER",
    "EMAIL": "EMAIL_ADDRESS",
    "ID": "ID",
    "IDNUM": "ID",
    "MEDICALRECORD": "ID",
    "DEVICE": "ID",
    "BIOID": "ID",
    "URL": "URL",
    "USERNAME": "USERNAME",
    "PROFESSION": "PROFESSION",
    "OTHERPHI": "OTHER_PHI",
}

#: Entities to detect but NOT redact.
#:
#: HIPAA Safe Harbor counts dates as identifiers, so redacting them is the
#: compliant default and that is what ships. But the Contexta summariser asks
#: Claude for trends over time, and a transcript full of [DATE_TIME] cannot
#: answer that -- run with `--keep DATE_TIME` for that path and record the
#: decision. This is a real trade, not an oversight; make it deliberately.
DEFAULT_KEEP: frozenset = frozenset()

#: Presidio's URL recognizer reads `Reg.No` as a Norwegian domain and `MRS.NA`
#: as a Namibian one. The allow-list handles the common form labels; drop the
#: whole entity type here if your documents contain no real URLs.
DEFAULT_DROP: frozenset = frozenset()


@dataclass
class Span:
    """One detected entity, in original-text coordinates."""

    entity_type: str
    start: int
    end: int
    score: float
    text: str

    @property
    def marker(self) -> str:
        return f"[{self.entity_type}]"


@dataclass
class RedactionConfig:
    model: str = DEFAULT_MODEL
    threshold: float = DEFAULT_THRESHOLD
    keep: frozenset = DEFAULT_KEEP
    drop: frozenset = DEFAULT_DROP
    language: str = "en"
    #: "transformers" is the default on evidence, not preference: across 7 real
    #: lab documents the clinical model leaked 0 PHI probes at 100% recall,
    #: while spaCy en_core_web_lg leaked 25 at 76.2% -- including the
    #: requisition number in EVERY document. See evaluate.py.
    #:
    #: There is deliberately NO silent fallback to spaCy when the transformer
    #: deps are missing. build_analyzer() raises with the install command
    #: instead. Quietly degrading to an engine that leaks is the worst possible
    #: failure mode for privacy tooling -- it would look like it was working.
    nlp_engine: str = "transformers"      # "spacy" | "transformers"
    transformer_model: str = TRANSFORMER_MODELS["stanford"]
    tokenizer_model: str = "en_core_web_sm"   # transformers still need a tokenizer
    allow_list: tuple = ()
    use_clinical_allow_list: bool = True

    #: Register the 12 Indian/Contexta recognizers. Off only to measure what
    #: they contribute over bare Presidio -- no vendor model knows Aadhaar,
    #: ABHA or CTX-448192, so this should show a visible recall drop.
    use_custom_recognizers: bool = True

    #: Discard detections shorter than this many non-space characters.
    #:
    #: Transformer NER fragments: on the Tenet report it emitted PERSON 'A'
    #: (0.81) out of "A/GRatio" and ID '-' (0.79) out of "APMC/FMR/78102".
    #: Neither is PHI -- no identifier is one character -- but each becomes a
    #: text-search needle that matches everywhere in the PDF. 'A' alone hit 118
    #: times. Real PHI is never this short, so dropping them costs nothing.
    min_span_chars: int = 2

    def resolved_allow_list(self) -> list:
        extra = list(self.allow_list)
        return clinical_allow_list(extra) if self.use_clinical_allow_list else extra


@dataclass
class RedactionResult:
    original: str
    redacted: str
    spans: list = field(default_factory=list)   # redacted, in original coords
    kept: list = field(default_factory=list)    # detected but deliberately left in


def _nlp_configuration(config: RedactionConfig) -> dict:
    if config.nlp_engine == "transformers":
        return {
            "nlp_engine_name": "transformers",
            "models": [
                {
                    "lang_code": config.language,
                    "model_name": {
                        "spacy": config.tokenizer_model,
                        "transformers": config.transformer_model,
                    },
                }
            ],
            "ner_model_configuration": {
                "model_to_presidio_entity_mapping": TRANSFORMER_ENTITY_MAPPING,
                "labels_to_ignore": ["O"],
                "aggregation_strategy": "simple",
                "stride": 14,
            },
        }
    return {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": config.language, "model_name": config.model}],
    }


def build_analyzer(config: RedactionConfig) -> AnalyzerEngine:
    """
    Analyzer with the configured NLP engine plus every custom Indian recognizer.

    Raises a readable error if a model is missing -- the bare OSError spaCy and
    transformers throw sends people hunting in the wrong place.
    """
    provider = NlpEngineProvider(nlp_configuration=_nlp_configuration(config))
    try:
        nlp_engine = provider.create_engine()
    except (OSError, ValueError) as exc:
        if config.nlp_engine == "transformers":
            raise RuntimeError(
                f"could not load transformer {config.transformer_model!r} "
                f"(tokenizer {config.tokenizer_model!r}).\n"
                f"    pip install 'transformers>=4.40' torch\n"
                f"    python -m spacy download {config.tokenizer_model}\n"
                f"original error: {exc}"
            ) from exc
        raise RuntimeError(
            f"spaCy model {config.model!r} not found. Install it with:\n"
            f"    python -m spacy download {config.model}"
        ) from exc

    analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=[config.language])
    if config.use_custom_recognizers:
        for recognizer in build_indian_recognizers():
            analyzer.registry.add_recognizer(recognizer)
    return analyzer


def merge_overlaps(spans: list, text: str = None) -> list:
    """
    Collapse overlapping spans, keeping the higher-scoring label.

    Presidio resolves most conflicts itself, but custom and built-in recognizers
    can still both claim a run (IN_PHONE vs PHONE_NUMBER). Two markers written
    over one span corrupts the offsets of everything after it, so this has to
    happen before any replacement.

    Pass `text` whenever you have it. A merged span covers a WIDER range than
    either input, so the winner's original `.text` no longer matches
    [start:end]. That mismatch is invisible in the text output (which slices by
    offset) but leaks PHI in the PDF output (which searches by `.text`): on the
    Tenet report, PERSON 'Dr.Abdur Rehman' (1.00) beat IN_PERSON_NAME
    'Dr.Abdur Rehman Asif' (0.85), the range correctly extended over 'Asif',
    but `.text` stayed short -- so the PDF blacked out the first two words and
    left the surname on the page.
    """
    if not spans:
        return []

    def _rebuild(entity_type, start, end, score) -> Span:
        return Span(
            entity_type=entity_type,
            start=start,
            end=end,
            score=score,
            text=text[start:end] if text is not None else "",
        )

    ordered = sorted(spans, key=lambda s: (s.start, -s.score))
    merged = [ordered[0]]
    for span in ordered[1:]:
        last = merged[-1]
        if span.start < last.end:  # overlap
            winner = span if span.score > last.score else last
            start, end = last.start, max(last.end, span.end)
            merged[-1] = (
                _rebuild(winner.entity_type, start, end, winner.score)
                if text is not None
                else Span(winner.entity_type, start, end, winner.score, winner.text)
            )
        else:
            merged.append(span)
    return merged


def _to_spans(results: list, text: str) -> list:
    return [
        Span(
            entity_type=r.entity_type,
            start=r.start,
            end=r.end,
            score=r.score,
            text=text[r.start : r.end],
        )
        for r in results
    ]


class RedactionPipeline:
    """
    Analyze -> filter -> redact.

    Construct once and reuse: building the analyzer loads the NLP model, which
    is the slow part (seconds for spaCy, longer for a transformer). Doing it per
    page or per request is the classic way to make this look far more expensive
    than it is.
    """

    def __init__(self, config: RedactionConfig | None = None) -> None:
        self.config = config or RedactionConfig()
        self.analyzer = build_analyzer(self.config)
        self.anonymizer = AnonymizerEngine()
        self._allow_list = self.config.resolved_allow_list()
        #: Lowercased set for the enclosing-term check, built once.
        self._allow_lower = {t.lower() for t in self._allow_list}

    # -- span filtering ----------------------------------------------------

    @staticmethod
    def enclosing_term(text: str, start: int, end: int) -> str:
        """Widen a span outward to whitespace, returning the whole token it sits in."""
        i, j = start, end
        while i > 0 and not text[i - 1].isspace():
            i -= 1
        while j < len(text) and not text[j].isspace():
            j += 1
        return text[i:j]

    def _allowed_by_enclosing_term(self, text: str, span) -> bool:
        """
        True if the token CONTAINING this span is allow-listed.

        Presidio's own allow_list compares against the detected span text, so it
        cannot suppress a detection that is a FRAGMENT of an allowed term:
        `A/GRatio` sits in LAB_TESTS, the model reported `GRatio` (PERSON, 0.99),
        and nothing matched. `allow_list_match="regex"` searches allow-list terms
        *inside* the detection, which is the wrong direction for this case.

        So widen outward instead: `GRatio` -> `A/GRatio.` -> strip punctuation ->
        matches LAB_TESTS. Generalises to every future fragment of a known
        clinical term without another whack-a-mole list entry.
        """
        term = self.enclosing_term(text, span.start, span.end).strip(" \t.,;:()[]")
        return bool(term) and term.lower() in self._allow_lower

    def _filter_spans(self, spans: list, text: str) -> list:
        """
        Both guards, in one place.

        analyze() and redact_blocks() are separate code paths and previously
        applied these independently -- which is exactly how a fix landed on one
        and missed the other. Anything span-filtering goes here now.
        """
        return [
            s for s in spans
            if len(s.text.strip()) >= self.config.min_span_chars
            and not self._allowed_by_enclosing_term(text, s)
        ]

    # -- analysis ----------------------------------------------------------

    def _raw_analyze(self, text: str) -> list:
        results: list[RecognizerResult] = self.analyzer.analyze(
            text=text,
            language=self.config.language,
            score_threshold=self.config.threshold,
            allow_list=self._allow_list,
        )
        return [r for r in results if r.entity_type not in self.config.drop]

    def analyze(self, text: str) -> tuple[list, list]:
        """Returns (spans_to_redact, spans_deliberately_kept), both merged."""
        spans = self._filter_spans(_to_spans(self._raw_analyze(text), text), text)
        to_redact = merge_overlaps(
            [s for s in spans if s.entity_type not in self.config.keep], text
        )
        kept = merge_overlaps(
            [s for s in spans if s.entity_type in self.config.keep], text
        )
        return to_redact, kept

    # -- redaction ---------------------------------------------------------

    @staticmethod
    def _apply(text: str, spans: list) -> str:
        """Replace back-to-front so earlier offsets stay valid as lengths change."""
        out = text
        for span in sorted(spans, key=lambda s: s.start, reverse=True):
            out = out[: span.start] + span.marker + out[span.end :]
        return out

    def redact(self, text: str) -> RedactionResult:
        to_redact, kept = self.analyze(text)
        return RedactionResult(
            original=text,
            redacted=self._apply(text, to_redact),
            spans=to_redact,
            kept=kept,
        )

    def redact_blocks(self, blocks: list, join: str = "\n") -> RedactionResult:
        """
        Two passes over two different views of the page, because the two detector
        families need opposite things from the layout.

        NER, per block. In the flat stream a lab report reads
        `...<34 U/L\\nAspartate Aminotransferase...` -- the unit ends one line and
        the next test name begins the following one, so the model spans the newline
        and reports `U/L\\nAspartate Aminotransferase` as one ORGANIZATION. Confined
        to a block, a span physically cannot cross a column boundary.

        Label anchors, on the joined page. PDF forms put a label and its value in
        SEPARATE blocks -- on the Tenet report, block 45 is `'Name\\n:'` and block 47
        is `'MRS.NAGA LAXMI J'`. Per block, `Patient Name:` and the name never appear
        in the same string and the anchor cannot fire. Joining restores adjacency.

        Run only per-block and the patient's name leaks. Run only joined and the
        units get swallowed. Hence both, merged.
        """
        joined = join.join(blocks)

        # Pass 1 -- everything, per block, offset into joined coordinates.
        spans, cursor = [], 0
        for block in blocks:
            spans += [
                Span(s.entity_type, s.start + cursor, s.end + cursor, s.score, s.text)
                for s in _to_spans(self._raw_analyze(block), block)
            ]
            cursor += len(block) + len(join)

        # Pass 2 -- label-anchored recognizers only, across block boundaries.
        # Intersect with what is actually registered: Presidio raises
        # "No matching recognizers were found" rather than returning empty when
        # asked for an entity nothing serves, and use_custom_recognizers=False
        # deregisters every label-anchored recognizer at once.
        wanted = (LABEL_ANCHORED_ENTITIES - self.config.drop) & set(
            self.analyzer.get_supported_entities(language=self.config.language)
        )
        if wanted:
            label_results = self.analyzer.analyze(
                text=joined,
                language=self.config.language,
                entities=sorted(wanted),
                score_threshold=self.config.threshold,
                allow_list=self._allow_list,
            )
            spans += _to_spans(label_results, joined)

        # Shared with analyze() via _filter_spans, so a guard added there can no
        # longer miss this path. Pass `joined` so merged spans carry text
        # matching [start:end].
        spans = self._filter_spans(spans, joined)

        to_redact = merge_overlaps(
            [s for s in spans if s.entity_type not in self.config.keep], joined
        )
        kept = merge_overlaps(
            [s for s in spans if s.entity_type in self.config.keep], joined
        )

        return RedactionResult(
            original=joined,
            redacted=self._apply(joined, to_redact),
            spans=to_redact,
            kept=kept,
        )

    def redact_via_anonymizer(self, text: str) -> str:
        """
        Same output via Presidio's AnonymizerEngine.

        Kept as a cross-check on `redact()`: if the two ever disagree, the span
        arithmetic above is wrong. Exercised by the tests.
        """
        results = [r for r in self._raw_analyze(text) if r.entity_type not in self.config.keep]
        operators = {
            e: OperatorConfig("replace", {"new_value": f"[{e}]"})
            for e in {r.entity_type for r in results}
        }
        operators["DEFAULT"] = OperatorConfig("replace", {"new_value": "[REDACTED]"})
        return self.anonymizer.anonymize(
            text=text, analyzer_results=results, operators=operators
        ).text
