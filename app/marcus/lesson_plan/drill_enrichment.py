"""Project frozen G0 enrichment into DrillSpec inputs (Mine 5).

Mirrors ``workbook_enrichment``: read-only card consumption, no network/model
calls, import-linter Contract M3 safe (no orchestrator imports).
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any

from app.marcus.lesson_plan.drill_spec import (
    DrillPracticeItem,
    DrillSourceRef,
    DrillSpec,
)
from app.marcus.lesson_plan.workbook_enrichment import load_enrichment_card

logger = logging.getLogger(__name__)

# Prefer quiz/assessment-like components for drill prompts; fall back to slides.
_PREFERRED_TYPES = frozenset(
    {"quiz", "exercise_lab", "assignment_instructions", "discussion_forum"}
)
_FALLBACK_TYPES = frozenset({"slide", "narration", "workbook"})

_OPEN_ID_SAFE = re.compile(r"[^a-zA-Z0-9_-]+")


def _safe_id(raw: str, *, prefix: str) -> str:
    """Build an OPEN_ID (``^[a-z0-9._-]+$``) from arbitrary text."""
    cleaned = _OPEN_ID_SAFE.sub("-", raw.strip()).strip("-_. ").lower()
    cleaned = re.sub(r"[-_.]{2,}", "-", cleaned).strip("-_.")
    if not cleaned:
        cleaned = "item"
    candidate = f"{prefix}-{cleaned}".lower()
    if candidate[0].isdigit():
        candidate = f"{prefix}-x{cleaned}"
    return candidate[:64]


@dataclass(frozen=True)
class DrillEnrichmentProjection:
    """Projected drill inputs + honesty diagnostics."""

    spec: DrillSpec
    warnings: tuple[str, ...] = ()
    empty_source: bool = False


def project_enrichment_to_drill_inputs(card: Any) -> DrillEnrichmentProjection:
    """Project a G0 enrichment card (dict or model) into a ``DrillSpec``.

    Empty / unusable source → empty items + warning (Murat negative #5), never
    a silent zero-byte success claim at the producer layer.
    """
    if card is None:
        return DrillEnrichmentProjection(
            spec=DrillSpec(title="Practice drill (empty source)", items=()),
            warnings=("empty enrichment card: no drill items projected",),
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
    pedagogy = {
        str(p.get("component_id") or ""): p
        for p in (payload.get("pedagogy_annotations") or [])
        if isinstance(p, dict)
    }

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
        warnings.append(
            "no quiz/assessment/slide components available for drill projection"
        )
        return DrillEnrichmentProjection(
            spec=DrillSpec(title="Practice drill (empty source)", items=()),
            warnings=tuple(warnings),
            empty_source=True,
        )
    if not preferred:
        warnings.append(
            "no preferred quiz/assessment components; using slide/narration fallback"
        )

    items: list[DrillPracticeItem] = []
    for index, raw in enumerate(pool[:12], start=1):
        component_id = str(raw.get("component_id") or f"comp-{index}")
        label = str(raw.get("label") or component_id).strip()
        excerpt = str(raw.get("excerpt") or label).strip()
        locator = str(raw.get("locator") or component_id).strip()
        ped = pedagogy.get(component_id) or {}
        bloom = str(ped.get("bloom") or ped.get("role") or "apply").strip() or "apply"
        lo_raw = lo_ids[(index - 1) % len(lo_ids)]
        lo_id = (
            lo_raw.lower()
            if re.match(r"^[a-z0-9._-]+$", lo_raw.lower()) and lo_raw.lower()[0].isalpha()
            else _safe_id(lo_raw, prefix="lo")
        )
        prompt = f"Practice: {label}"
        if excerpt and excerpt != label:
            # Keep prompt short — first sentence-ish
            snippet = excerpt.split("\n")[0].strip()
            if len(snippet) > 180:
                snippet = snippet[:177] + "..."
            prompt = f"Using the source material, respond: {snippet}"
        focus = bloom.lower().strip() or "apply"
        items.append(
            DrillPracticeItem(
                item_id=_safe_id(component_id, prefix="drill"),
                learning_objective_id=lo_id,
                prompt=prompt,
                expected_focus=focus,
                source_refs=(
                    DrillSourceRef(
                        ref_id=_safe_id(component_id, prefix="ref"),
                        locator=locator,
                        excerpt=excerpt[:240],
                    ),
                ),
            )
        )

    title = "Practice drill"
    if lo_ids and lo_ids[0] != "lo-default-001":
        title = f"Practice drill ({len(items)} items)"

    return DrillEnrichmentProjection(
        spec=DrillSpec(title=title, items=tuple(items)),
        warnings=tuple(warnings),
        empty_source=False,
    )


__all__ = [
    "DrillEnrichmentProjection",
    "load_enrichment_card",
    "project_enrichment_to_drill_inputs",
]
