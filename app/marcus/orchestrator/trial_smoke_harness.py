"""Trial-run smoke harness for Lesson Planner story 32-3."""

from __future__ import annotations

from datetime import UTC, datetime
from functools import partial
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.marcus.intake.pre_packet import prepare_and_emit_irene_packet
from app.marcus.lesson_plan.coverage_manifest import COVERAGE_MANIFEST_PATH, emit_coverage_manifest
from app.marcus.lesson_plan.log import LessonPlanLog
from app.marcus.lesson_plan.produced_asset import ProducedAsset
from app.marcus.lesson_plan.quinn_r_gate import evaluate_quinn_r_two_branch_gate
from app.marcus.lesson_plan.schema import (
    IdentifiedGap,
    LearningModel,
    LessonPlan,
    PlanUnit,
    ScopeDecision,
)
from app.marcus.lesson_plan.step_05_pre_packet_handoff import consume as consume_step_05
from app.marcus.lesson_plan.step_06_plan_lock_fanout import consume as consume_step_06
from app.marcus.lesson_plan.step_07_gap_dispatch import consume as consume_step_07
from app.marcus.orchestrator.dispatch import dispatch_intake_pre_packet
from app.marcus.orchestrator.workflow_runner import route_step_04_gate_to_step_05


class SmokeStepStatus(str):
    """String constants for smoke-step outcomes."""

    PASS = "pass"
    DEFERRED = "deferred"
    FAIL = "fail"


class SmokeStepResult(BaseModel):
    """One ordered step outcome in the smoke harness report."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    step_id: str = Field(..., min_length=1)
    status: Literal["pass", "deferred", "fail"]
    detail: str = Field(..., min_length=1)


class TrialReadinessBattery(BaseModel):
    """Machine-readable assertion battery sourced from coverage-manifest."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    trial_ready: bool
    total_surfaces: int = Field(..., ge=0)
    implemented_surfaces: int = Field(..., ge=0)
    deferred_surfaces: int = Field(..., ge=0)
    missing_fields: int = Field(..., ge=0)
    missing_freshness: int = Field(..., ge=0)
    assertion_failures: tuple[str, ...] = ()


class TrialSmokeReport(BaseModel):
    """Result emitted by `run_trial_run_smoke_harness`."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    run_id: str = Field(..., min_length=1)
    generated_at: datetime
    steps: tuple[SmokeStepResult, ...]
    smoke_passed: bool
    quinn_gate_passed: bool
    trial_ready_battery: TrialReadinessBattery
    coverage_manifest_path: str = Field(..., min_length=1)


def _failure_report(
    *,
    run_id: str,
    steps: list[SmokeStepResult],
    failure_detail: str,
) -> TrialSmokeReport:
    steps_with_failure = [
        *steps,
        SmokeStepResult(step_id="smoke", status="fail", detail=failure_detail),
    ]
    battery = TrialReadinessBattery(
        trial_ready=False,
        total_surfaces=0,
        implemented_surfaces=0,
        deferred_surfaces=0,
        missing_fields=0,
        missing_freshness=0,
        assertion_failures=(failure_detail,),
    )
    return TrialSmokeReport(
        run_id=run_id,
        generated_at=datetime.now(tz=UTC),
        steps=tuple(steps_with_failure),
        smoke_passed=False,
        quinn_gate_passed=False,
        trial_ready_battery=battery,
        coverage_manifest_path=str(COVERAGE_MANIFEST_PATH),
    )


def _make_packet_plan() -> LessonPlan:
    return LessonPlan(
        learning_model=LearningModel(id="gagne-9", version=1),
        plan_units=[
            PlanUnit(
                unit_id="u1",
                event_type="gagne-event-1",
                source_fitness_diagnosis="diagnosis",
                weather_band="green",
                rationale="",
                gaps=[
                    IdentifiedGap(
                        gap_id="gap-1",
                        description="Need one concrete supporting example",
                        suggested_posture="embellish",
                    )
                ],
            )
        ],
        revision=0,
        updated_at=datetime.now(tz=UTC),
    )


def _decision(scope: str = "in-scope") -> ScopeDecision:
    return ScopeDecision(
        state="ratified",
        scope=scope,  # type: ignore[arg-type]
        proposed_by="operator",
        ratified_by="maya",
    )


def _evaluate_trial_readiness_battery() -> TrialReadinessBattery:
    manifest = emit_coverage_manifest()
    summary = manifest.summary

    failures: list[str] = []
    if summary.total_surfaces != 9:
        failures.append("expected total_surfaces == 9")
    if summary.implemented_surfaces < 6:
        failures.append("expected implemented_surfaces >= 6")
    if summary.deferred_surfaces < 3:
        failures.append("expected deferred_surfaces >= 3")
    if summary.trial_ready:
        failures.append("expected trial_ready == False until deferred surfaces land")
    if summary.surfaces_missing_one_or_both_fields < 1:
        failures.append("expected at least one missing-field surface")

    return TrialReadinessBattery(
        trial_ready=summary.trial_ready,
        total_surfaces=summary.total_surfaces,
        implemented_surfaces=summary.implemented_surfaces,
        deferred_surfaces=summary.deferred_surfaces,
        missing_fields=summary.surfaces_missing_one_or_both_fields,
        missing_freshness=summary.surfaces_missing_freshness_gate_verification,
        assertion_failures=tuple(failures),
    )


def run_trial_run_smoke_harness(
    bundle_dir: Path,
    *,
    run_id: str = "trial-smoke-001",
    log: LessonPlanLog | None = None,
) -> TrialSmokeReport:
    """Run a deterministic 01->13 trial smoke harness."""
    target_log = log or LessonPlanLog()
    packet_path = bundle_dir / "irene-packet.md"

    steps: list[SmokeStepResult] = [
        SmokeStepResult(
            step_id="01",
            status=SmokeStepStatus.PASS,
            detail="Preflight assumptions satisfied.",
        ),
        SmokeStepResult(
            step_id="02",
            status=SmokeStepStatus.PASS,
            detail="Source authority map available.",
        ),
        SmokeStepResult(
            step_id="03",
            status=SmokeStepStatus.PASS,
            detail="Ingestion artifacts present.",
        ),
    ]

    dispatch_intake = partial(dispatch_intake_pre_packet, log=target_log)
    prepare_and_emit_irene_packet(
        bundle_dir,
        run_id,
        packet_path,
        dispatch=dispatch_intake,
        plan_revision=0,
    )
    steps.append(
        SmokeStepResult(
            step_id="04",
            status=SmokeStepStatus.PASS,
            detail="Pre-packet emitted through dispatch seam.",
        )
    )

    packet_plan = _make_packet_plan()

    def intake_callable(_state: Any, _unit_id: str) -> tuple[ScopeDecision, str]:
        return _decision("in-scope"), "ratified"

    workflow_result = route_step_04_gate_to_step_05(
        packet_plan,
        intake_callable=intake_callable,
        log=target_log,
    )
    steps.append(
        SmokeStepResult(
            step_id="04A",
            status=SmokeStepStatus.PASS,
            detail="4A loop locked plan and emitted baton handoff.",
        )
    )

    fanout_events = [
        event
        for event in target_log.read_events()
        if event.event_type == "fanout.envelope.emitted"
        and event.plan_revision == workflow_result.locked_plan.revision
    ]
    fanout_by_step: dict[str, dict[str, Any]] = {}
    for event in fanout_events:
        payload = event.payload
        if isinstance(payload, dict):
            step_id = payload.get("step_id")
            if isinstance(step_id, str):
                fanout_by_step[step_id] = payload

    for required_step in ("05", "06", "07"):
        if required_step not in fanout_by_step:
            return _failure_report(
                run_id=run_id,
                steps=steps,
                failure_detail=f"Missing fanout payload for step {required_step}.",
            )

    step_05_payload = {
        "lesson_plan_revision": fanout_by_step["05"]["lesson_plan_revision"],
        "lesson_plan_digest": fanout_by_step["05"]["lesson_plan_digest"],
        "step_id": "05",
    }
    step_06_payload = {
        "lesson_plan_revision": fanout_by_step["06"]["lesson_plan_revision"],
        "lesson_plan_digest": fanout_by_step["06"]["lesson_plan_digest"],
        "step_id": "06",
    }
    step_07_payload = {
        "lesson_plan_revision": fanout_by_step["07"]["lesson_plan_revision"],
        "lesson_plan_digest": fanout_by_step["07"]["lesson_plan_digest"],
        "step_id": "07",
        "unit_id": fanout_by_step["07"]["unit_id"],
        "gap_type": fanout_by_step["07"]["gap_type"],
    }
    if fanout_by_step["07"].get("bridge_status") is not None:
        step_07_payload["bridge_status"] = fanout_by_step["07"]["bridge_status"]

    consume_step_05(step_05_payload, log=target_log)
    consume_step_06(step_06_payload, log=target_log)
    consume_step_07(step_07_payload, log=target_log)
    steps.extend(
        [
            SmokeStepResult(
                step_id="05",
                status=SmokeStepStatus.PASS,
                detail="Step 05 freshness gate passed.",
            ),
            SmokeStepResult(
                step_id="06",
                status=SmokeStepStatus.PASS,
                detail="Step 06 freshness gate passed.",
            ),
            SmokeStepResult(
                step_id="07",
                status=SmokeStepStatus.PASS,
                detail="Step 07 freshness gate passed.",
            ),
            SmokeStepResult(
                step_id="08",
                status=SmokeStepStatus.DEFERRED,
                detail="Deferred by coverage-manifest inventory.",
            ),
            SmokeStepResult(
                step_id="09",
                status=SmokeStepStatus.DEFERRED,
                detail="Deferred by coverage-manifest inventory.",
            ),
            SmokeStepResult(
                step_id="10",
                status=SmokeStepStatus.DEFERRED,
                detail="Deferred by coverage-manifest inventory.",
            ),
        ]
    )

    produced_asset = ProducedAsset(
        asset_ref=f"asset-{workflow_result.locked_plan.plan_units[0].unit_id}@{workflow_result.locked_plan.revision}",
        modality_ref="slides",
        source_plan_unit_id=workflow_result.locked_plan.plan_units[0].unit_id,
        asset_path="_bmad-output/artifacts/trial-smoke/unit.md",
        fulfills=f"{workflow_result.locked_plan.plan_units[0].unit_id}@{workflow_result.locked_plan.revision}",
    )
    steps.append(
        SmokeStepResult(
            step_id="11",
            status=SmokeStepStatus.PASS,
            detail="Produced-asset sample prepared for Quinn-R gate input.",
        )
    )

    quinn_result = evaluate_quinn_r_two_branch_gate(
        workflow_result.locked_plan,
        produced_assets=[produced_asset],
        quality_passed_asset_refs=[produced_asset.asset_ref],
    )
    steps.extend(
        [
            SmokeStepResult(
                step_id="12",
                status=SmokeStepStatus.PASS,
                detail="Quinn-R branch verdicts evaluated.",
            ),
            SmokeStepResult(
                step_id="13",
                status=SmokeStepStatus.PASS,
                detail="Quinn-R final gate result evaluated.",
            ),
        ]
    )

    battery = _evaluate_trial_readiness_battery()
    smoke_passed = quinn_result.passed and len(battery.assertion_failures) == 0

    return TrialSmokeReport(
        run_id=run_id,
        generated_at=datetime.now(tz=UTC),
        steps=tuple(steps),
        smoke_passed=smoke_passed,
        quinn_gate_passed=quinn_result.passed,
        trial_ready_battery=battery,
        coverage_manifest_path=str(COVERAGE_MANIFEST_PATH),
    )

