"""Project frozen G0 enrichment into QuizSpec inputs (Mine-next N3).

Prefer quiz-typed components; fall back to assessment-like types. Import-linter
Contract M3 safe (no orchestrator imports).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from app.marcus.lesson_plan.quiz_spec import QuizItem, QuizSourceRef, QuizSpec
from app.marcus.lesson_plan.workbook_enrichment import load_enrichment_card

_PREFERRED_TYPES = frozenset({"quiz", "assignment_instructions"})
_FALLBACK_TYPES = frozenset({"exercise_lab", "discussion_forum", "slide"})
_OPEN_ID_SAFE = re.compile(r"[^a-zA-Z0-9_-]+")


def _safe_id(raw: str, *, prefix: str) -> str:
    cleaned = _OPEN_ID_SAFE.sub("-", raw.strip()).strip("-_. ").lower()
    cleaned = re.sub(r"[-_.]{2,}", "-", cleaned).strip("-_.")
    if not cleaned:
        cleaned = "item"
    candidate = f"{prefix}-{cleaned}".lower()
    if candidate[0].isdigit():
        candidate = f"{prefix}-x{cleaned}"
    return candidate[:64]


@dataclass(frozen=True)
class QuizEnrichmentProjection:
    """Projected quiz inputs + honesty diagnostics."""

    spec: QuizSpec
    warnings: tuple[str, ...] = ()
    empty_source: bool = False


def project_enrichment_to_quiz_inputs(card: Any) -> QuizEnrichmentProjection:
    """Project a G0 enrichment card into a ``QuizSpec``."""
    if card is None:
        return QuizEnrichmentProjection(
            spec=QuizSpec(title="Practice quiz (empty source)", items=()),
            warnings=("empty enrichment card: no quiz items projected",),
            empty_source=True,
        )
    if hasattr(card, "model_dump"):
        payload = card.model_dump(mode="json")
    elif isinstance(card, dict):
        payload = card
    else:
        raise TypeError(f"enrichment card must be dict or model, got {type(card)!r}")

    components = payload.get("typed_components") or []
    los = payload.get("provisional_los") or []
    lo_ids: list[str] = []
    for index, lo in enumerate(los):
        if not isinstance(lo, dict):
            continue
        oid = str(lo.get("objective_id") or "").strip()
        if not oid:
            oid = _safe_id(f"lo-{index + 1}", prefix="lo")
        lo_ids.append(oid)
    if not lo_ids:
        lo_ids = ["lo-default-001"]

    preferred: list[dict[str, Any]] = []
    fallback: list[dict[str, Any]] = []
    for raw in components:
        if not isinstance(raw, dict):
            continue
        st = str(raw.get("source_type") or "")
        if st in _PREFERRED_TYPES:
            preferred.append(raw)
        elif st in _FALLBACK_TYPES:
            fallback.append(raw)

    pool = preferred or fallback
    warnings: list[str] = []
    if not pool:
        return QuizEnrichmentProjection(
            spec=QuizSpec(title="Practice quiz (empty source)", items=()),
            warnings=("no quiz/assessment components available for quiz projection",),
            empty_source=True,
        )
    if not preferred:
        warnings.append("no preferred quiz components; using slide/lab fallback")

    items: list[QuizItem] = []
    for index, raw in enumerate(pool[:10], start=1):
        component_id = str(raw.get("component_id") or f"comp-{index}")
        label = str(raw.get("label") or component_id).strip()
        excerpt = str(raw.get("excerpt") or label).strip()
        locator = str(raw.get("locator") or component_id).strip()
        lo_raw = lo_ids[(index - 1) % len(lo_ids)]
        lo_id = (
            lo_raw.lower()
            if re.match(r"^[a-z0-9._-]+$", lo_raw.lower()) and lo_raw.lower()[0].isalpha()
            else _safe_id(lo_raw, prefix="lo")
        )
        snippet = excerpt.split("\n")[0].strip()
        if len(snippet) > 160:
            snippet = snippet[:157] + "..."
        prompt = f"Check your understanding: {snippet or label}"
        items.append(
            QuizItem(
                item_id=_safe_id(component_id, prefix="quiz"),
                learning_objective_id=lo_id,
                prompt=prompt,
                choices=(
                    "Apply the concept to a clinical decision",
                    "Recall the figure without context",
                    "Defer until Module 2 without mapping",
                ),
                expected_answer_focus="apply",
                source_refs=(
                    QuizSourceRef(
                        ref_id=_safe_id(component_id, prefix="ref"),
                        locator=locator,
                        excerpt=excerpt[:240],
                    ),
                ),
            )
        )

    return QuizEnrichmentProjection(
        spec=QuizSpec(
            title=f"Practice quiz ({len(items)} items)",
            items=tuple(items),
        ),
        warnings=tuple(warnings),
        empty_source=False,
    )


__all__ = [
    "QuizEnrichmentProjection",
    "load_enrichment_card",
    "project_enrichment_to_quiz_inputs",
]
