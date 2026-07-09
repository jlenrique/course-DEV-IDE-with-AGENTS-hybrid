"""Lightweight planning ratification recorder for the Phase-2 selection bridge.

Captures purpose, audience, plan choices, and gap-fill tradeoffs, then emits a
canonical S8 ``RatifiedLessonPlanCollateralIntent`` for the existing selection
edge. This is not a planning workflow engine.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.marcus.lesson_plan.collateral_selection import (
    RatifiedLessonPlanCollateralIntent,
    ResolvedCollateralSelection,
    load_lesson_plan_collateral_selection,
    resolve_lesson_plan_collateral_selection,
)
from app.marcus.lesson_plan.collateral_spec import CollateralSpec
from app.marcus.lesson_plan.source_assessment import SourceAssessment
from app.models.state.component_selection import ComponentSelection

GapFillChoice = Literal[
    "synthesize",
    "wait",
    "ask_operator",
    "ask_sme",
    "lighter_collateral",
]

WorkflowChoice = Literal[
    "narrated-deck",
    "narrated-deck-with-motion",
    "narrated-deck-with-workbook",
]

OVERCLAIM_MARKERS = (
    "full lecture ingestion",
    "lecture-complete selection",
    "full lecture-video ingestion",
    "complete remote lms ingestion",
)


class PlanningRatificationError(ValueError):
    """Raised when ratification cannot proceed honestly."""


class GapFillTradeoff(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)

    chosen: GapFillChoice | Literal["none"]
    considered: tuple[GapFillChoice, ...] = Field(default_factory=tuple)
    rationale: str = ""

    @model_validator(mode="after")
    def _tradeoff_shape(self) -> GapFillTradeoff:
        if self.chosen == "none":
            return self
        if not self.considered:
            raise ValueError(
                "gap-fill tradeoff requires considered[] alternatives "
                "(or chosen='none')"
            )
        if self.chosen not in self.considered:
            # chosen must be among considered for auditability
            raise ValueError("gap-fill chosen must appear in considered[]")
        if len(self.considered) < 2:
            raise ValueError(
                "gap-fill tradeoff requires at least two considered options "
                "when a choice is made"
            )
        return self


class AssetPlanItem(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)

    kind: str
    attributes: dict[str, str] = Field(default_factory=dict)


class PlanningRatificationRecord(BaseModel):
    """Companion ratification record that also emits canonical S8 intent."""

    model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)

    schema_version: Literal["0.1"] = "0.1"
    purpose: str
    audience: str
    source_assessment: SourceAssessment
    assets_to_create: tuple[AssetPlanItem, ...] = Field(default_factory=tuple)
    workflow: WorkflowChoice
    gap_fill: GapFillTradeoff
    claim_fence: str = (
        "Does not claim full lecture ingestion or lecture-complete selection."
    )
    s8_intent: RatifiedLessonPlanCollateralIntent

    @field_validator("purpose", "audience")
    @classmethod
    def _nonempty(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("purpose and audience are required")
        return cleaned

    @field_validator("claim_fence")
    @classmethod
    def _fence_present(cls, value: str) -> str:
        cleaned = value.strip().lower()
        deny_ok = (
            "does not claim" in cleaned
            or "do not claim" in cleaned
            or "not claim" in cleaned
        )
        names_forbidden = (
            "full lecture" in cleaned or "lecture-complete" in cleaned
        )
        if not (deny_ok and names_forbidden):
            raise ValueError(
                "claim_fence must explicitly deny full lecture ingestion / "
                "lecture-complete selection"
            )
        # Reject affirmative overclaim smuggled into the fence string.
        affirmative = (
            "we achieved",
            "we completed",
            "proven full lecture",
            "achieved full lecture",
            "completed full lecture",
        )
        if any(marker in cleaned for marker in affirmative):
            raise ValueError("claim_fence must not assert over-claim affirmatively")
        return value.strip()


class SelectionDelta(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)

    before_bundle_id: str
    after_bundle_id: str
    before_selection: dict[str, bool]
    after_selection: dict[str, bool]

    @property
    def changed(self) -> bool:
        return (
            self.before_bundle_id != self.after_bundle_id
            or self.before_selection != self.after_selection
        )


def reject_overclaim_text(text: str) -> None:
    """Fail loud if text asserts full lecture ingestion / lecture-complete selection."""
    lowered = text.lower()
    for marker in OVERCLAIM_MARKERS:
        if marker in lowered:
            raise PlanningRatificationError(
                f"over-claim rejected: contains {marker!r}"
            )


def _selection_dict(selection: ComponentSelection) -> dict[str, bool]:
    return {
        "deck": bool(selection.deck),
        "motion": bool(selection.motion),
        "workbook": bool(selection.workbook),
    }


def _intent_for_workflow(
    workflow: WorkflowChoice,
    *,
    collateral: CollateralSpec | None = None,
) -> RatifiedLessonPlanCollateralIntent:
    if workflow == "narrated-deck-with-workbook":
        if collateral is None or collateral.declaration != "present":
            raise PlanningRatificationError(
                "workbook workflow requires CollateralSpec declaration=present"
            )
        return RatifiedLessonPlanCollateralIntent(
            ratification_status="ratified",
            bundle_id="narrated-deck-with-workbook",
            collateral=collateral,
        )
    return RatifiedLessonPlanCollateralIntent(
        ratification_status="ratified",
        bundle_id=workflow,
    )


def _assert_gap_fill_consistent_with_workflow(
    workflow: WorkflowChoice,
    gap_fill: GapFillTradeoff,
) -> None:
    """Gap-fill disposition must not contradict the chosen workflow (load-bearing)."""
    if gap_fill.chosen == "none":
        return
    if (
        gap_fill.chosen == "lighter_collateral"
        and workflow == "narrated-deck-with-workbook"
    ):
        raise PlanningRatificationError(
            "gap_fill=lighter_collateral contradicts workbook workflow; "
            "choose a lighter catalog bundle or a different gap-fill"
        )
    if gap_fill.chosen == "wait" and workflow == "narrated-deck-with-workbook":
        raise PlanningRatificationError(
            "gap_fill=wait contradicts shipping a full workbook workflow now"
        )


def ratify_planning_decision(
    *,
    assessment: SourceAssessment | None,
    purpose: str,
    audience: str,
    workflow: WorkflowChoice,
    gap_fill: GapFillTradeoff,
    assets_to_create: tuple[AssetPlanItem, ...] = (),
    collateral: CollateralSpec | None = None,
    claim_fence: str | None = None,
) -> PlanningRatificationRecord:
    """Record a planning decision and emit canonical S8 intent."""
    if assessment is None:
        raise PlanningRatificationError(
            "ratification requires a prior source assessment"
        )
    reject_overclaim_text(purpose)
    reject_overclaim_text(audience)
    _assert_gap_fill_consistent_with_workflow(workflow, gap_fill)
    # claim_fence must *deny* full lecture ingestion (validator); do not run
    # reject_overclaim_text on the fence body itself.
    fence = claim_fence or (
        "Does not claim full lecture ingestion or lecture-complete selection."
    )
    intent = _intent_for_workflow(workflow, collateral=collateral)
    # Pin that S8 resolver accepts the emitted intent.
    resolved = resolve_lesson_plan_collateral_selection(intent)
    if resolved.source != "ratified":
        raise PlanningRatificationError(
            "emitted S8 intent did not resolve as ratified"
        )
    if resolved.bundle_id != workflow:
        raise PlanningRatificationError(
            f"workflow {workflow!r} resolved to bundle {resolved.bundle_id!r}"
        )
    return PlanningRatificationRecord(
        purpose=purpose,
        audience=audience,
        source_assessment=assessment,
        assets_to_create=assets_to_create,
        workflow=workflow,
        gap_fill=gap_fill,
        claim_fence=fence,
        s8_intent=intent,
    )


def write_ratification_artifacts(
    record: PlanningRatificationRecord,
    output_dir: Path,
) -> dict[str, Path]:
    """Write companion record + canonical S8 intent YAML for trial start."""
    output_dir.mkdir(parents=True, exist_ok=True)
    companion = output_dir / "planning-ratification.json"
    intent_path = output_dir / "ratified-collateral-intent.yaml"
    companion.write_text(
        record.model_dump_json(indent=2),
        encoding="utf-8",
    )
    intent_path.write_text(
        yaml.safe_dump(
            record.s8_intent.model_dump(mode="json"),
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return {"companion": companion, "s8_intent": intent_path}


def compute_selection_delta(
    *,
    before: ResolvedCollateralSelection,
    after: ResolvedCollateralSelection,
) -> SelectionDelta:
    delta = SelectionDelta(
        before_bundle_id=before.bundle_id,
        after_bundle_id=after.bundle_id,
        before_selection=_selection_dict(before.selection),
        after_selection=_selection_dict(after.selection),
    )
    if not delta.changed:
        raise PlanningRatificationError(
            "selection delta required but before==after "
            f"(bundle_id={before.bundle_id!r})"
        )
    return delta


def write_selection_delta(delta: SelectionDelta, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(delta.model_dump_json(indent=2), encoding="utf-8")
    return path


def resolve_intent_file(path: Path) -> ResolvedCollateralSelection:
    """Load and resolve a canonical S8 intent file (frozen resolver path)."""
    return load_lesson_plan_collateral_selection(path)


def default_baseline_selection() -> ResolvedCollateralSelection:
    """Unratified/default selection used as the 'before' baseline."""
    return resolve_lesson_plan_collateral_selection(None)


__all__ = [
    "AssetPlanItem",
    "GapFillChoice",
    "GapFillTradeoff",
    "OVERCLAIM_MARKERS",
    "PlanningRatificationError",
    "PlanningRatificationRecord",
    "SelectionDelta",
    "WorkflowChoice",
    "compute_selection_delta",
    "default_baseline_selection",
    "ratify_planning_decision",
    "reject_overclaim_text",
    "resolve_intent_file",
    "write_ratification_artifacts",
    "write_selection_delta",
]
