"""Plan-lock fanout emitter seam (Story 30-4).

This module builds step 05+ envelopes from a locked lesson plan and emits
``fanout.envelope.emitted`` log events through the caller-injected dispatch
callable (single-writer discipline).
"""

from __future__ import annotations

import logging
import typing
from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, datetime
from typing import Any, get_args

from pydantic import BaseModel, ConfigDict, Field

from app.marcus.lesson_plan.event_type_registry import EVENT_FANOUT_ENVELOPE_EMITTED
from app.marcus.lesson_plan.events import EventEnvelope
from app.marcus.lesson_plan.schema import IdentifiedGap, LessonPlan, PlanUnit

logger = logging.getLogger(__name__)

_POSTURE_TO_GAP_TYPE: dict[str, str] = {
    "embellish": "enrichment",
    "corroborate": "evidence",
    "gap_fill": "missing_concept",
}

# G6 B2 (party-mode 2026-04-19 follow-on): assert posture mapping covers every
# Literal value declared by IdentifiedGap.suggested_posture so a future Literal
# widening surfaces at import time rather than as a runtime KeyError on the
# fanout path. Safe under typing.get_type_hints because Pydantic preserves
# Literal annotations on field metadata.
_IDENTIFIED_GAP_POSTURES: frozenset[str] = frozenset(
    get_args(typing.get_type_hints(IdentifiedGap)["suggested_posture"])
)
assert frozenset(_POSTURE_TO_GAP_TYPE) == _IDENTIFIED_GAP_POSTURES, (
    "fanout._POSTURE_TO_GAP_TYPE keys must equal IdentifiedGap.suggested_posture "
    f"Literal values; mapping={sorted(_POSTURE_TO_GAP_TYPE)}, "
    f"literal={sorted(_IDENTIFIED_GAP_POSTURES)}"
)


class StepFanoutEnvelope(BaseModel):
    """Top-level plan-ref envelope for step 05+ fanout boundaries."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    step_id: str = Field(..., min_length=2)
    lesson_plan_revision: int = Field(..., ge=0)
    lesson_plan_digest: str = Field(..., min_length=1)
    unit_id: str | None = None
    gap_type: str | None = None
    bridge_status: str | None = None


class PlanLockFanoutResult(BaseModel):
    """Result shape returned by :func:`emit_plan_lock_fanout`."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    envelopes: tuple[StepFanoutEnvelope, ...]
    bridge_results: tuple[dict[str, Any], ...] = ()


def _plan_dict_for_bridge(plan: LessonPlan) -> dict[str, Any]:
    """Map LessonPlan schema into IreneTracyBridge expected shape."""
    units: list[dict[str, Any]] = []
    for unit in plan.plan_units:
        scope = unit.scope_decision.scope if unit.scope_decision is not None else None
        identified_gaps: list[dict[str, Any]] = []
        for gap in unit.gaps:
            gap_type = _POSTURE_TO_GAP_TYPE[gap.suggested_posture]
            identified_gaps.append(
                {
                    "type": gap_type,
                    "description": gap.description,
                    "claim": "",
                    "source_context": "",
                    "enrichment_type": "general",
                    "content_type": "explanation",
                    "scope": "unit",
                }
            )
        units.append(
            {
                "id": unit.unit_id,
                "scope_decision": scope,
                "identified_gaps": identified_gaps,
            }
        )
    return {"units": units}


def _gap_envelopes_for_unit(
    unit: PlanUnit,
    *,
    revision: int,
    digest: str,
    bridge_results: Sequence[Mapping[str, Any]],
) -> list[StepFanoutEnvelope]:
    results_by_gap_type: dict[str, Mapping[str, Any]] = {}
    for result in bridge_results:
        posture = str(result.get("posture", "")) if isinstance(result, Mapping) else ""
        if posture == "gap-fill":
            results_by_gap_type["missing_concept"] = result
        elif posture == "embellish":
            results_by_gap_type["enrichment"] = result
        elif posture == "corroborate":
            results_by_gap_type["evidence"] = result

    envelopes: list[StepFanoutEnvelope] = []
    for gap in unit.gaps:
        gap_type = _POSTURE_TO_GAP_TYPE[gap.suggested_posture]
        bridge_status = None
        matched = results_by_gap_type.get(gap_type)
        if matched is not None:
            bridge_status = str(matched.get("status", "unknown"))
        envelopes.append(
            StepFanoutEnvelope(
                step_id="07",
                lesson_plan_revision=revision,
                lesson_plan_digest=digest,
                unit_id=unit.unit_id,
                gap_type=gap_type,
                bridge_status=bridge_status,
            )
        )
    return envelopes


def emit_plan_lock_fanout(
    locked_plan: LessonPlan,
    *,
    dispatch: Callable[[EventEnvelope], None],
    bridge: Any | None = None,
) -> PlanLockFanoutResult:
    """Emit step 05+ fanout envelopes after plan-lock.

    Emits one ``fanout.envelope.emitted`` event per step envelope.
    """
    if locked_plan.digest == "":
        from app.marcus.lesson_plan.digest import compute_digest

        locked_plan = locked_plan.model_copy(update={"digest": compute_digest(locked_plan)})

    envelopes: list[StepFanoutEnvelope] = [
        StepFanoutEnvelope(
            step_id="05",
            lesson_plan_revision=locked_plan.revision,
            lesson_plan_digest=locked_plan.digest,
        ),
        StepFanoutEnvelope(
            step_id="06",
            lesson_plan_revision=locked_plan.revision,
            lesson_plan_digest=locked_plan.digest,
        ),
    ]

    bridge_results: tuple[dict[str, Any], ...] = ()
    in_scope_units = [
        unit
        for unit in locked_plan.plan_units
        if unit.scope_decision is not None
        and unit.scope_decision.scope == "in-scope"
        and len(unit.gaps) > 0
    ]

    if bridge is not None and in_scope_units:
        try:
            raw = bridge.process_plan_locked(_plan_dict_for_bridge(locked_plan))
        except Exception as exc:
            # G6 B1 (party-mode 2026-04-19 follow-on): silent except-Exception
            # was diagnostically opaque. Bridge failures still produce empty
            # bridge_results — fanout envelopes still emit with bridge_status=None
            # — but the operator gets a single warning naming the bridge type
            # and the exception class for actionable diagnosis.
            logger.warning(
                "Irene-Tracy bridge raised %s during plan-lock fanout "
                "(bridge=%s); proceeding with empty bridge_results",
                type(exc).__name__,
                type(bridge).__name__,
            )
            raw = []
        if isinstance(raw, Sequence):
            normalized_results: list[dict[str, Any]] = []
            for item in raw:
                if isinstance(item, Mapping):
                    normalized_results.append(dict(item))
            bridge_results = tuple(normalized_results)

    for unit in in_scope_units:
        envelopes.extend(
            _gap_envelopes_for_unit(
                unit,
                revision=locked_plan.revision,
                digest=locked_plan.digest,
                bridge_results=bridge_results,
            )
        )

    for envelope_model in envelopes:
        dispatch(
            EventEnvelope(
                timestamp=datetime.now(tz=UTC),
                plan_revision=locked_plan.revision,
                event_type=EVENT_FANOUT_ENVELOPE_EMITTED,
                payload=envelope_model.model_dump(mode="json"),
            )
        )

    return PlanLockFanoutResult(envelopes=tuple(envelopes), bridge_results=bridge_results)

