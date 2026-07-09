"""RED/GREEN tests for Phase-2 planning ratification bridge (AC-P2-2..7)."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from app.marcus.course_source.input_bundle import build_lesson_planning_input_bundle
from app.marcus.lesson_plan.collateral_selection import (
    resolve_lesson_plan_collateral_selection,
)
from app.marcus.lesson_plan.collateral_spec import (
    CollateralSpec,
    DepthDeltaContract,
    WorkbookSection,
    WorkbookSpec,
)
from app.marcus.lesson_plan.planning_ratification import (
    AssetPlanItem,
    GapFillTradeoff,
    PlanningRatificationError,
    compute_selection_delta,
    default_baseline_selection,
    ratify_planning_decision,
    reject_overclaim_text,
    resolve_intent_file,
    write_ratification_artifacts,
    write_selection_delta,
)
from app.marcus.lesson_plan.source_assessment import (
    assess_from_corpus_dir,
    assess_from_input_bundle,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = (
    REPO_ROOT
    / "_bmad-output"
    / "implementation-artifacts"
    / "evidence"
    / "s7p2-story-b-syllabus-metadata-20260708T110225"
)
HAI_ROOT = (
    REPO_ROOT
    / "course-content"
    / "courses"
    / "aziz-nazha-hai-510-generative-ai-in-healthcare"
)
TEJAL_RICH = (
    REPO_ROOT
    / "course-content"
    / "courses"
    / "tejal-c1m1-p4-assessments-bridge"
)


def _workbook_collateral() -> CollateralSpec:
    return CollateralSpec(
        declaration="present",
        workbook=WorkbookSpec(
            sections=[
                WorkbookSection(
                    section_id="sec-1",
                    learning_objective_id="obj-1",
                    title="Read in depth",
                    depth_delta=DepthDeltaContract(
                        deferred_from_slide="slide-1",
                        deferred_depth="the supporting method",
                    ),
                )
            ]
        ),
    )


def _hai_assessment():
    bundle = build_lesson_planning_input_bundle(
        course_root=HAI_ROOT,
        proposal_path=EVIDENCE / "hai-510" / "module-metadata.yaml",
        module_id="module-01-foundations-of-ai-in-healthcare",
        operator_focus="Plan around missing lecture video and slide source.",
    )
    return assess_from_input_bundle(bundle)


def _lighter_tradeoff() -> GapFillTradeoff:
    return GapFillTradeoff(
        chosen="lighter_collateral",
        considered=("lighter_collateral", "wait", "synthesize"),
        rationale="Thin source: ship deck+motion; defer workbook until slides exist.",
    )


def _workbook_tradeoff() -> GapFillTradeoff:
    return GapFillTradeoff(
        chosen="synthesize",
        considered=("synthesize", "wait", "lighter_collateral"),
        rationale="Rich curated source: synthesize workbook companion from available material.",
    )


def test_planning_ratification_requires_source_assessment() -> None:
    with pytest.raises(PlanningRatificationError, match="source assessment"):
        ratify_planning_decision(
            assessment=None,
            purpose="Teach foundations",
            audience="Graduate clinicians",
            workflow="narrated-deck-with-motion",
            gap_fill=_lighter_tradeoff(),
        )


def test_planning_ratification_requires_purpose_and_audience() -> None:
    assessment = _hai_assessment()
    with pytest.raises(ValidationError):
        ratify_planning_decision(
            assessment=assessment,
            purpose="   ",
            audience="Graduate clinicians",
            workflow="narrated-deck-with-motion",
            gap_fill=_lighter_tradeoff(),
        )


def test_thin_hai_lighter_collateral_emits_ratified_s8_intent(tmp_path: Path) -> None:
    assessment = _hai_assessment()
    record = ratify_planning_decision(
        assessment=assessment,
        purpose="Introduce generative AI foundations despite missing lecture video",
        audience="HAI 510 enrolled learners",
        workflow="narrated-deck-with-motion",
        gap_fill=_lighter_tradeoff(),
        assets_to_create=(
            AssetPlanItem(kind="narrated_deck", attributes={"fidelity": "mixed"}),
        ),
    )
    assert record.s8_intent.ratification_status == "ratified"
    assert record.s8_intent.bundle_id == "narrated-deck-with-motion"
    paths = write_ratification_artifacts(record, tmp_path)
    resolved = resolve_intent_file(paths["s8_intent"])
    assert resolved.source == "ratified"
    assert resolved.bundle_id == "narrated-deck-with-motion"
    assert resolved.selection.workbook is False


def test_rich_tejal_workbook_path_emits_workbook_bundle(tmp_path: Path) -> None:
    assessment = assess_from_corpus_dir(TEJAL_RICH, corpus_id="tejal-c1m1-p4")
    record = ratify_planning_decision(
        assessment=assessment,
        purpose="Bridge assessments to Module 2 with workbook companion",
        audience="APC C1 learners",
        workflow="narrated-deck-with-workbook",
        gap_fill=_workbook_tradeoff(),
        collateral=_workbook_collateral(),
        assets_to_create=(
            AssetPlanItem(kind="workbook", attributes={"kind": "deck-companion"}),
        ),
    )
    paths = write_ratification_artifacts(record, tmp_path)
    resolved = resolve_intent_file(paths["s8_intent"])
    assert resolved.source == "ratified"
    assert resolved.bundle_id == "narrated-deck-with-workbook"
    assert resolved.selection.workbook is True


def test_planning_ratification_emits_selection_delta(tmp_path: Path) -> None:
    """AC-P2-5: same thin fixture, two ratified dispositions → delta."""
    assessment = _hai_assessment()
    wait_deck = ratify_planning_decision(
        assessment=assessment,
        purpose="Minimal deck-only delivery while waiting on source",
        audience="HAI 510 enrolled learners",
        workflow="narrated-deck",
        gap_fill=GapFillTradeoff(
            chosen="wait",
            considered=("wait", "lighter_collateral", "synthesize"),
            rationale="Wait on lecture assets; ship deck-only now.",
        ),
    )
    lighter_motion = ratify_planning_decision(
        assessment=assessment,
        purpose="Ship deck+motion now; defer workbook until slides exist",
        audience="HAI 510 enrolled learners",
        workflow="narrated-deck-with-motion",
        gap_fill=_lighter_tradeoff(),
    )
    before = resolve_lesson_plan_collateral_selection(wait_deck.s8_intent)
    after = resolve_lesson_plan_collateral_selection(lighter_motion.s8_intent)
    delta = compute_selection_delta(before=before, after=after)
    assert delta.changed
    assert delta.before_bundle_id == "narrated-deck"
    assert delta.after_bundle_id == "narrated-deck-with-motion"
    out = write_selection_delta(delta, tmp_path / "selection-delta.json")
    assert out.is_file()
    assert "narrated-deck-with-motion" in out.read_text(encoding="utf-8")


def test_claim_fence_rejects_affirmative_overclaim() -> None:
    assessment = _hai_assessment()
    with pytest.raises(ValidationError, match="claim_fence|over-claim|deny"):
        ratify_planning_decision(
            assessment=assessment,
            purpose="Teach foundations",
            audience="HAI learners",
            workflow="narrated-deck",
            gap_fill=_lighter_tradeoff(),
            claim_fence="We achieved full lecture ingestion for HAI 510",
        )


def test_selection_flow_rejects_missing_delta() -> None:
    before = default_baseline_selection()
    after = default_baseline_selection()
    with pytest.raises(PlanningRatificationError, match="selection delta required"):
        compute_selection_delta(before=before, after=after)


def test_s8_resolver_behavior_remains_frozen() -> None:
    # Compatibility pin: absent intent still defaults to narrated-deck-with-motion.
    absent = resolve_lesson_plan_collateral_selection(None)
    assert absent.source == "absent"
    assert absent.bundle_id == "narrated-deck-with-motion"
    # Workbook collateral still maps to workbook bundle (unchanged S8 rule).
    workbook = resolve_lesson_plan_collateral_selection(
        {
            "ratification_status": "ratified",
            "collateral": _workbook_collateral().model_dump(mode="json"),
        }
    )
    assert workbook.source == "ratified"
    assert workbook.bundle_id == "narrated-deck-with-workbook"


def test_gap_fill_lighter_rejects_workbook_workflow() -> None:
    assessment = _hai_assessment()
    with pytest.raises(PlanningRatificationError, match="lighter_collateral"):
        ratify_planning_decision(
            assessment=assessment,
            purpose="Teach foundations",
            audience="HAI learners",
            workflow="narrated-deck-with-workbook",
            gap_fill=_lighter_tradeoff(),
            collateral=_workbook_collateral(),
        )


def test_overclaim_full_lecture_ingestion_rejected() -> None:
    with pytest.raises(PlanningRatificationError, match="over-claim"):
        reject_overclaim_text("We achieved full lecture ingestion for HAI 510")


def test_gap_fill_tradeoff_requires_structured_alternatives() -> None:
    with pytest.raises(ValidationError):
        GapFillTradeoff(chosen="wait", considered=("wait",))
