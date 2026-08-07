"""
contexta_redact — PHI redaction for Indian clinical text, built on Presidio.

    from contexta_redact import RedactionPipeline, RedactionConfig

    pipeline = RedactionPipeline(RedactionConfig(keep=frozenset({"DATE_TIME"})))
    result = pipeline.redact("Pt Ramesh Kumar, MRN CTX-448192")
    result.redacted   # 'Pt [PERSON], MRN [IN_UHID]'

Build the pipeline once and reuse it; construction loads the spaCy model.
"""

from .allowlist import clinical_allow_list, load_extra_terms
from .engine import (
    DEFAULT_DROP,
    DEFAULT_KEEP,
    DEFAULT_MODEL,
    DEFAULT_THRESHOLD,
    TRANSFORMER_MODELS,
    RedactionConfig,
    RedactionPipeline,
    RedactionResult,
    Span,
    merge_overlaps,
)
from .recognizers import (
    INDIAN_ENTITIES,
    build_indian_recognizers,
    verhoeff_check_digit,
    verhoeff_valid,
)

__all__ = [
    "RedactionPipeline",
    "RedactionConfig",
    "RedactionResult",
    "Span",
    "merge_overlaps",
    "build_indian_recognizers",
    "INDIAN_ENTITIES",
    "clinical_allow_list",
    "load_extra_terms",
    "verhoeff_valid",
    "verhoeff_check_digit",
    "TRANSFORMER_MODELS",
    "DEFAULT_MODEL",
    "DEFAULT_THRESHOLD",
    "DEFAULT_KEEP",
    "DEFAULT_DROP",
]
