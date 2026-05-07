"""Lesson Planner workflow runner seam for Step 4A insertion (Story 32-1).

Story 32-5 adds ``pre_collected_decisions`` to
:func:`route_step_04_gate_to_step_05` so the production HIL intake callable
can be wired from the operator's conversational ratification decisions.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.marcus.facade import Facade
from app.marcus.lesson_plan.log import LessonPlanLog
from app.marcus.lesson_plan.schema import LessonPlan
from app.marcus.orchestrator.loop import IntakeCallable
from scripts.utilities.pipeline_manifest import load_manifest


class StepBatonHandoff(BaseModel):
    """Baton payload handed from Step 4A to Step 05."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    step_from: str = Field(default="04A")
    step_to: str = Field(default="05")
    lesson_plan_revision: int = Field(..., ge=0)
    lesson_plan_digest: str = Field(..., min_length=1)


class Step4AWorkflowResult(BaseModel):
    """Result emitted by the 32-1 workflow seam."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    locked_plan: LessonPlan
    handoff: StepBatonHandoff


def insert_between(
    before_id: str, after_id: str, new_step: str, steps: Iterable[str]
) -> tuple[str, ...]:
    """Ensure new_step appears between before_id and after_id."""
    step_map = {step.id: step for step in load_manifest().steps}
    if before_id not in step_map:
        raise ValueError(f"pipeline manifest does not define step '{before_id}'")
    if after_id not in step_map:
        raise ValueError(f"pipeline manifest does not define step '{after_id}'")

    ordered = list(steps)
    if before_id not in ordered:
        raise ValueError(f"pipeline is missing required step '{before_id}'")
    if after_id not in ordered:
        raise ValueError(f"pipeline is missing required step '{after_id}'")

    idx_before = ordered.index(before_id)
    idx_after = ordered.index(after_id)
    if idx_before >= idx_after:
        raise ValueError(
            f"pipeline order invalid: step '{before_id}' must precede step '{after_id}'"
        )

    between = ordered[idx_before + 1 : idx_after]
    if new_step in between:
        return tuple(ordered)

    ordered.insert(idx_after, new_step)
    return tuple(ordered)


def route_step_04_gate_to_step_05(
    packet_plan: LessonPlan,
    *,
    intake_callable: IntakeCallable | None = None,
    pre_collected_decisions: dict[str, tuple[str, str]] | None = None,
    facade: Facade | None = None,
    prior_declined_rationales: tuple[tuple[str, str], ...] = (),
    log: LessonPlanLog | None = None,
    tracy_bridge: Any | None = None,
) -> Step4AWorkflowResult:
    """Run the 4A loop and return the baton contract for step 05.

    Exactly one of ``intake_callable`` or ``pre_collected_decisions`` must
    be provided.  When ``pre_collected_decisions`` is given,
    :func:`~marcus.orchestrator.hil_intake.build_hil_intake_callable`
    constructs the callable from the operator's conversational decisions
    (Step 04A production HIL path — Story 32-5).
    """
    if len(packet_plan.plan_units) == 0:
        raise ValueError("step-04 handoff requires at least one plan unit before 4A routing")

    # G6-P1: exactly one source — ambiguous when both provided
    if intake_callable is not None and pre_collected_decisions is not None:
        raise ValueError(
            "route_step_04_gate_to_step_05 requires exactly one of intake_callable "
            "or pre_collected_decisions, not both"
        )

    if pre_collected_decisions is not None:
        from app.marcus.orchestrator.hil_intake import build_hil_intake_callable
        # G6-P2: validate no extra / missing unit_ids in the decisions map
        plan_unit_ids = {unit.unit_id for unit in packet_plan.plan_units}
        decision_ids = set(pre_collected_decisions.keys())
        extra = decision_ids - plan_unit_ids
        missing = plan_unit_ids - decision_ids
        if extra:
            raise ValueError(
                f"pre_collected_decisions contains unit_ids not in the packet plan: {sorted(extra)}"
            )
        if missing:
            raise ValueError(
                "pre_collected_decisions is missing unit_ids present in the packet plan: "
                f"{sorted(missing)}"
            )
        intake_callable = build_hil_intake_callable(pre_collected_decisions)
    elif intake_callable is None:
        raise ValueError(
            "route_step_04_gate_to_step_05 requires either intake_callable "
            "or pre_collected_decisions"
        )

    resolved_facade = facade or Facade()
    locked_plan = resolved_facade.run_4a(
        packet_plan,
        intake_callable=intake_callable,
        prior_declined_rationales=prior_declined_rationales,
        log=log,
        tracy_bridge=tracy_bridge,
    )
    handoff = StepBatonHandoff(
        lesson_plan_revision=locked_plan.revision,
        lesson_plan_digest=locked_plan.digest,
    )
    return Step4AWorkflowResult(locked_plan=locked_plan, handoff=handoff)

