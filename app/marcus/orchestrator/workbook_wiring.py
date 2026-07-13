"""Deterministic orchestration seam for the four-node workbook band."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from typing import Final, TypeAlias

from app.marcus.lesson_plan.research_packet import (
    ASK_A_ENRICHMENT_NODE_ID,
    ASK_A_ENRICHMENT_SPECIALIST_ID,
    ASK_B_HOT_TOPICS_NODE_ID,
    ASK_B_HOT_TOPICS_SPECIALIST_ID,
)
from app.models.runtime.production_envelope import (
    ProductionEnvelope,
    SpecialistContribution,
)
from app.specialists.dispatch_errors import SpecialistDispatchError

WORKBOOK_BRIEF_NODE_ID: Final[str] = "07W.1"
WORKBOOK_REVIEW_NODE_ID: Final[str] = "07W.3"
WORKBOOK_BRIEF_SPECIALIST_ID: Final[str] = "workbook_brief_stub"
WORKBOOK_REVIEW_SPECIALIST_ID: Final[str] = "workbook_review_stub"
WORKBOOK_BAND_MODEL_MARKER: Final[str] = "deterministic-workbook-band-stub"
WORKBOOK_BAND_NODE_IDS: Final[tuple[str, ...]] = (
    WORKBOOK_BRIEF_NODE_ID,
    ASK_A_ENRICHMENT_NODE_ID,
    WORKBOOK_REVIEW_NODE_ID,
    ASK_B_HOT_TOPICS_NODE_ID,
)

WorkbookBandFactory: TypeAlias = Callable[
    [str, ProductionEnvelope], dict[str, object]
]

WORKBOOK_BAND_SPECIALIST_IDS: Final[dict[str, str]] = {
    WORKBOOK_BRIEF_NODE_ID: WORKBOOK_BRIEF_SPECIALIST_ID,
    ASK_A_ENRICHMENT_NODE_ID: ASK_A_ENRICHMENT_SPECIALIST_ID,
    WORKBOOK_REVIEW_NODE_ID: WORKBOOK_REVIEW_SPECIALIST_ID,
    ASK_B_HOT_TOPICS_NODE_ID: ASK_B_HOT_TOPICS_SPECIALIST_ID,
}


def _brief_stub(_node_id: str, _envelope: ProductionEnvelope) -> dict[str, object]:
    return {
        "stub_status": "not_yet_wired",
        "brief_payload": {},
        "known_losses": ["semantic_writers_not_yet_wired"],
    }


def _ask_a_stub(_node_id: str, _envelope: ProductionEnvelope) -> dict[str, object]:
    return {
        "research_entries": [],
        "stub_status": "not_yet_wired",
        "known_losses": ["ask_a_not_yet_wired"],
    }


def _review_stub(_node_id: str, _envelope: ProductionEnvelope) -> dict[str, object]:
    return {
        "stub_status": "not_yet_wired",
        "review_payload": {},
        "known_losses": ["semantic_writers_not_yet_wired"],
    }


def _ask_b_stub(_node_id: str, _envelope: ProductionEnvelope) -> dict[str, object]:
    return {
        "research_entries": [],
        "stub_status": "not_yet_wired",
        "known_losses": ["ask_b_not_yet_wired"],
    }


DEFAULT_WORKBOOK_BAND_FACTORIES: Final[dict[str, WorkbookBandFactory]] = {
    WORKBOOK_BRIEF_NODE_ID: _brief_stub,
    ASK_A_ENRICHMENT_NODE_ID: _ask_a_stub,
    WORKBOOK_REVIEW_NODE_ID: _review_stub,
    ASK_B_HOT_TOPICS_NODE_ID: _ask_b_stub,
}


def run_workbook_band_node(
    *,
    node_id: str,
    production_envelope: ProductionEnvelope,
    factories: Mapping[str, WorkbookBandFactory] | None = None,
) -> ProductionEnvelope:
    """Run one node, skipping an exact persisted coordinate before its factory."""
    if not isinstance(production_envelope, ProductionEnvelope):
        raise SpecialistDispatchError(
            "workbook band requires a ProductionEnvelope context",
            tag="workbook.band.invalid-context",
        )
    specialist_id = WORKBOOK_BAND_SPECIALIST_IDS.get(node_id)
    if specialist_id is None:
        raise SpecialistDispatchError(
            f"no workbook band factory registered for node {node_id!r}",
            tag="workbook.band.unknown-node",
        )
    if production_envelope.get_contribution(specialist_id, node_id=node_id) is not None:
        return production_envelope

    selected = DEFAULT_WORKBOOK_BAND_FACTORIES if factories is None else factories
    factory = selected.get(node_id)
    if factory is None:
        raise SpecialistDispatchError(
            f"no workbook band factory registered for node {node_id!r}",
            tag="workbook.band.unknown-node",
        )
    try:
        output = factory(node_id, production_envelope)
    except SpecialistDispatchError:
        raise
    except Exception as exc:
        raise SpecialistDispatchError(
            f"workbook band factory failed at node {node_id!r}: {exc}",
            tag="workbook.band.factory-failed",
        ) from exc
    if not isinstance(output, dict):
        raise SpecialistDispatchError(
            f"workbook band factory at node {node_id!r} returned "
            f"{type(output).__name__}, expected dict",
            tag="workbook.band.invalid-output",
        )
    try:
        json.dumps(output, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise SpecialistDispatchError(
            f"workbook band factory at node {node_id!r} returned "
            f"non-serializable output: {exc}",
            tag="workbook.band.invalid-output",
        ) from exc
    updated = production_envelope.model_copy(deep=True)
    updated.add_contribution(
        SpecialistContribution.from_output(
            specialist_id=specialist_id,
            node_id=node_id,
            output=output,
            model_used=WORKBOOK_BAND_MODEL_MARKER,
        )
    )
    return updated


__all__ = [
    "DEFAULT_WORKBOOK_BAND_FACTORIES",
    "WORKBOOK_BAND_MODEL_MARKER",
    "WORKBOOK_BAND_NODE_IDS",
    "WORKBOOK_BAND_SPECIALIST_IDS",
    "WORKBOOK_BRIEF_NODE_ID",
    "WORKBOOK_BRIEF_SPECIALIST_ID",
    "WORKBOOK_REVIEW_NODE_ID",
    "WORKBOOK_REVIEW_SPECIALIST_ID",
    "WorkbookBandFactory",
    "run_workbook_band_node",
]
