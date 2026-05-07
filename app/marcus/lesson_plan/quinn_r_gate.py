"""Deterministic Quinn-R step-13 two-branch gate for Lesson Plan units.

Audience: 32-1 workflow wiring, 32-3 trial-run smoke, and 29-2 carry-forward
consumers. This module evaluates the current lesson plan without mutating it and
emits a machine-readable artifact for step-13 auditing.

Discipline notes:

* Non-blueprint units pass only through the produced-asset quality branch.
* Blueprint units pass only through the Irene+writer sign-off branch.
* Out-of-scope units stay in the tree as audited Declined nodes with verbatim
  rationale preserved for the next Irene diagnostic pass.
* This module does not write to the 31-2 log and does not impersonate the
  broader Quinn-R quality-review workflow.
"""

from __future__ import annotations

import json
from collections import defaultdict
from collections.abc import Collection, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Final, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.marcus.lesson_plan.gagne_diagnostician import PriorDeclinedRationale
from app.marcus.lesson_plan.produced_asset import ProducedAsset
from app.marcus.lesson_plan.schema import LessonPlan, PlanRef, PlanUnit

REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[2]
DEFAULT_QUINN_R_GATE_OUTPUT_ROOT: Final[str] = "_bmad-output/artifacts/quinn-r"


class QuinnRGateError(ValueError):
    """Raised when a plan cannot be evaluated by the step-13 gate."""


class QuinnRUnitVerdict(BaseModel):
    """Per-plan-unit step-13 verdict."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    unit_id: str = Field(..., min_length=1)
    branch: Literal["produced-asset", "blueprint-signoff", "declined-audit"]
    passed: bool
    reason: str = Field(..., min_length=1)
    asset_ref: str | None = Field(
        default=None,
        description="Quality-approved asset ref when the produced-asset branch passes.",
    )


class QuinnRTwoBranchResult(BaseModel):
    """Ordered step-13 result across all plan units."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    plan_ref: PlanRef
    evaluated_at: datetime
    passed: bool
    unit_verdicts: list[QuinnRUnitVerdict] = Field(default_factory=list)
    prior_declined_rationales: list[PriorDeclinedRationale] = Field(default_factory=list)

    @field_validator("evaluated_at", mode="after")
    @classmethod
    def _evaluated_at_must_be_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("evaluated_at must be timezone-aware")
        return value


def _resolve_output_root(output_root: str | Path) -> Path:
    path = Path(output_root)
    if not path.is_absolute():
        path = REPO_ROOT / path
    try:
        path.relative_to(REPO_ROOT)
    except ValueError as exc:
        raise QuinnRGateError(
            f"Quinn-R gate output_root must live under the repo root; got {path}"
        ) from exc
    return path


def _relative_asset_path(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def _group_assets_by_unit(
    produced_assets: Sequence[ProducedAsset],
) -> dict[str, list[ProducedAsset]]:
    assets_by_unit: dict[str, list[ProducedAsset]] = defaultdict(list)
    for asset in produced_assets:
        assets_by_unit[asset.source_plan_unit_id].append(asset)
    return dict(assets_by_unit)


def _require_scope(plan_unit: PlanUnit) -> str:
    if plan_unit.scope_decision is None:
        raise QuinnRGateError(
            "Quinn-R two-branch gate requires scope_decision on every plan unit; "
            f"missing on unit_id={plan_unit.unit_id!r}"
        )
    return plan_unit.scope_decision.scope


def evaluate_quinn_r_two_branch_gate(
    plan: LessonPlan,
    *,
    produced_assets: Sequence[ProducedAsset] = (),
    quality_passed_asset_refs: Collection[str] = (),
    evaluated_at: datetime | None = None,
) -> QuinnRTwoBranchResult:
    """Evaluate the Lesson Plan against Quinn-R's step-13 two-branch rule."""
    approved_refs = set(quality_passed_asset_refs)
    assets_by_unit = _group_assets_by_unit(produced_assets)

    verdicts: list[QuinnRUnitVerdict] = []
    prior_declined: list[PriorDeclinedRationale] = []

    for unit in plan.plan_units:
        scope = _require_scope(unit)

        if scope == "out-of-scope":
            if unit.rationale == "":
                verdicts.append(
                    QuinnRUnitVerdict(
                        unit_id=unit.unit_id,
                        branch="declined-audit",
                        passed=False,
                        reason=(
                            "Out-of-scope units must preserve a verbatim Declined "
                            "rationale for future Irene carry-forward."
                        ),
                    )
                )
                continue

            prior_declined.append(
                PriorDeclinedRationale(unit_id=unit.unit_id, rationale=unit.rationale)
            )
            verdicts.append(
                QuinnRUnitVerdict(
                    unit_id=unit.unit_id,
                    branch="declined-audit",
                    passed=True,
                    reason="Declined rationale preserved for future Irene preload.",
                )
            )
            continue

        if scope == "blueprint":
            signoff = unit.blueprint_signoff
            if signoff and signoff.irene_review_complete and signoff.writer_signoff_complete:
                verdicts.append(
                    QuinnRUnitVerdict(
                        unit_id=unit.unit_id,
                        branch="blueprint-signoff",
                        passed=True,
                        reason=(
                            "Blueprint branch cleared via completed Irene + writer sign-off."
                        ),
                    )
                )
            else:
                verdicts.append(
                    QuinnRUnitVerdict(
                        unit_id=unit.unit_id,
                        branch="blueprint-signoff",
                        passed=False,
                        reason=(
                            "Blueprint units require completed Irene + writer sign-off "
                            "before the step-13 gate can pass."
                        ),
                    )
                )
            continue

        unit_assets = assets_by_unit.get(unit.unit_id, [])
        approved_asset = next(
            (asset for asset in unit_assets if asset.asset_ref in approved_refs),
            None,
        )
        if approved_asset is not None:
            verdicts.append(
                QuinnRUnitVerdict(
                    unit_id=unit.unit_id,
                    branch="produced-asset",
                    passed=True,
                    reason="Produced asset cleared quality review.",
                    asset_ref=approved_asset.asset_ref,
                )
            )
            continue

        if not unit_assets:
            verdicts.append(
                QuinnRUnitVerdict(
                    unit_id=unit.unit_id,
                    branch="produced-asset",
                    passed=False,
                    reason=(
                        "No produced asset available for a non-blueprint unit at step 13."
                    ),
                )
            )
            continue

        verdicts.append(
            QuinnRUnitVerdict(
                unit_id=unit.unit_id,
                branch="produced-asset",
                passed=False,
                reason=(
                    "Produced asset exists but no asset_ref was explicitly marked "
                    "quality-passed."
                ),
            )
        )

    effective_evaluated_at = evaluated_at or datetime.now(tz=UTC)
    return QuinnRTwoBranchResult(
        plan_ref=PlanRef(
            lesson_plan_revision=plan.revision,
            lesson_plan_digest=plan.digest,
        ),
        evaluated_at=effective_evaluated_at,
        passed=all(verdict.passed for verdict in verdicts),
        unit_verdicts=verdicts,
        prior_declined_rationales=prior_declined,
    )


def extract_prior_declined_rationales(
    result: QuinnRTwoBranchResult,
) -> list[PriorDeclinedRationale]:
    """Return ordered carry-forward Declined rationale entries for 29-2."""
    return list(result.prior_declined_rationales)


def render_quinn_r_gate_json(result: QuinnRTwoBranchResult) -> str:
    """Return the canonical deterministic JSON representation of ``result``."""
    return json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True) + "\n"


def emit_quinn_r_gate_artifact(
    result: QuinnRTwoBranchResult,
    *,
    output_root: str | Path = DEFAULT_QUINN_R_GATE_OUTPUT_ROOT,
) -> str:
    """Write the step-13 gate artifact and return the repo-relative path."""
    root = _resolve_output_root(output_root)
    path = root / f"lesson-plan@{result.plan_ref.lesson_plan_revision}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_quinn_r_gate_json(result), encoding="utf-8")
    return _relative_asset_path(path)


__all__ = [
    "DEFAULT_QUINN_R_GATE_OUTPUT_ROOT",
    "QuinnRGateError",
    "QuinnRTwoBranchResult",
    "QuinnRUnitVerdict",
    "emit_quinn_r_gate_artifact",
    "evaluate_quinn_r_two_branch_gate",
    "extract_prior_declined_rationales",
    "render_quinn_r_gate_json",
]
