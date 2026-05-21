"""Marcus-side narration grammar for Tracy-backed research turns.

Maya-facing note
----------------

Maya does not see Tracy's raw payload shape. She hears one Marcus sentence that
explains what kind of research support is available and invites the next move.

Developer discipline note
-------------------------

This module is a pure wording seam for Story 30-5. It does not dispatch
retrieval, mutate lesson-plan state, write to the log, or implement 30-3b's 4A
conversation flow. It only turns a Tracy-style posture result into one
Marcus-facing sentence.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final

__all__ = ["RetrievalNarrationError", "render_retrieval_narration"]


class RetrievalNarrationError(ValueError):
    """Raised when a Tracy posture result cannot be narrated safely."""


_EMBELLISH_TEMPLATE: Final[str] = (
    "I found a detail that enriches this section, and I can weave it in if you want?"
)
_CORROBORATE_TEMPLATE: Final[str] = (
    "I found {classification_phrase} for this claim, and I can anchor that nuance here if you want?"
)
_GAP_FILL_TEMPLATE: Final[str] = (
    "I found source material that fills the missing background here, "
    "and I can fold it in if you want?"
)
_CORROBORATE_CLASSIFICATION_PHRASES: Final[dict[str, str]] = {
    "supporting": "evidence that supports it",
    "contrasting": "evidence that challenges it",
    "mentioning": "a source that mentions it without fully settling it",
}


def _require_mapping(value: Any) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise RetrievalNarrationError("I need a structured Tracy result before I can phrase it.")
    return value


def _normalize_posture(raw_posture: Any) -> str:
    if not isinstance(raw_posture, str) or raw_posture == "":
        raise RetrievalNarrationError("I need a named research posture before I can phrase it.")

    normalized = raw_posture.strip().lower().replace("_", "-")
    if normalized not in {"embellish", "corroborate", "gap-fill"}:
        raise RetrievalNarrationError(
            "I can only phrase embellish, corroborate, or gap-fill research turns."
        )
    return normalized


def _require_success(result: Mapping[str, Any]) -> None:
    if result.get("status") != "success":
        raise RetrievalNarrationError("I need a usable Tracy result before I can phrase it.")


def _corroborate_phrase(result: Mapping[str, Any]) -> str:
    output = _require_mapping(result.get("output"))
    raw_classification = output.get("classification")
    if not isinstance(raw_classification, str) or raw_classification == "":
        raise RetrievalNarrationError(
            "I need a corroboration classification before I can phrase it."
        )

    normalized = raw_classification.strip().lower()
    phrase = _CORROBORATE_CLASSIFICATION_PHRASES.get(normalized)
    if phrase is None:
        raise RetrievalNarrationError(
            "I can only phrase supporting, contrasting, or mentioning corroboration."
        )
    return phrase


def render_retrieval_narration(result: Mapping[str, Any]) -> str:
    """Return the canonical Marcus sentence for a Tracy posture result."""
    structured = _require_mapping(result)
    _require_success(structured)
    posture = _normalize_posture(structured.get("posture"))

    if posture == "embellish":
        return _EMBELLISH_TEMPLATE
    if posture == "corroborate":
        return _CORROBORATE_TEMPLATE.format(
            classification_phrase=_corroborate_phrase(structured)
        )
    return _GAP_FILL_TEMPLATE
