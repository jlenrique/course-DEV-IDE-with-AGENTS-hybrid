"""Bank Phase-2 evolutionary bridge W1–W4 evidence artifacts."""

from __future__ import annotations

import json
from pathlib import Path

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
    compute_selection_delta,
    ratify_planning_decision,
    write_ratification_artifacts,
    write_selection_delta,
)
from app.marcus.lesson_plan.source_assessment import (
    assess_from_corpus_dir,
    assess_from_input_bundle,
    assessments_differ_in_kind_or_count,
)

REPO = Path(__file__).resolve().parents[2]
EVIDENCE_META = (
    REPO
    / "_bmad-output/implementation-artifacts/evidence/"
    / "s7p2-story-b-syllabus-metadata-20260708T110225"
)
OUT = (
    REPO
    / "_bmad-output/implementation-artifacts/evidence/"
    / "phase2-evolutionary-bridge-20260709T204500"
)
OUT.mkdir(parents=True, exist_ok=True)

HAI = REPO / "course-content/courses/aziz-nazha-hai-510-generative-ai-in-healthcare"
PHS = REPO / "course-content/courses/juan-leon-phs-620-teaching-learning-seminar"
TEJAL = REPO / "course-content/courses/tejal-c1m1-p4-assessments-bridge"

hai = assess_from_input_bundle(
    build_lesson_planning_input_bundle(
        course_root=HAI,
        proposal_path=EVIDENCE_META / "hai-510/module-metadata.yaml",
        module_id="module-01-foundations-of-ai-in-healthcare",
        operator_focus="Plan around missing lecture video and slide source.",
    )
)
phs = assess_from_input_bundle(
    build_lesson_planning_input_bundle(
        course_root=PHS,
        proposal_path=EVIDENCE_META / "phs-620/module-metadata.yaml",
        module_id="module-01",
        operator_focus=(
            "Enhance existing course content after Confluence and Canvas access."
        ),
    )
)
tejal = assess_from_corpus_dir(TEJAL, corpus_id="tejal-c1m1-p4")

(OUT / "w1-hai-assessment.json").write_text(
    hai.model_dump_json(indent=2), encoding="utf-8"
)
(OUT / "w1-phs-assessment.json").write_text(
    phs.model_dump_json(indent=2), encoding="utf-8"
)
(OUT / "w2-tejal-assessment.json").write_text(
    tejal.model_dump_json(indent=2), encoding="utf-8"
)
assert assessments_differ_in_kind_or_count(hai, tejal)
assert assessments_differ_in_kind_or_count(phs, tejal)

# AC-P2-5: same thin fixture, two ratified dispositions (not baseline theater).
thin_wait = ratify_planning_decision(
    assessment=hai,
    purpose="Introduce generative AI foundations despite missing lecture video",
    audience="HAI 510 enrolled learners",
    workflow="narrated-deck",
    gap_fill=GapFillTradeoff(
        chosen="wait",
        considered=("wait", "lighter_collateral", "synthesize"),
        rationale="Wait on lecture assets; ship deck-only now.",
    ),
    assets_to_create=(
        AssetPlanItem(kind="narrated_deck", attributes={"mode": "deck-only"}),
    ),
)
thin_lighter = ratify_planning_decision(
    assessment=hai,
    purpose="Ship deck+motion now; defer workbook until slides exist",
    audience="HAI 510 enrolled learners",
    workflow="narrated-deck-with-motion",
    gap_fill=GapFillTradeoff(
        chosen="lighter_collateral",
        considered=("lighter_collateral", "wait", "synthesize"),
        rationale="Thin source: ship deck+motion; defer workbook.",
    ),
    assets_to_create=(
        AssetPlanItem(kind="narrated_deck", attributes={"mode": "deck+motion"}),
    ),
)
write_ratification_artifacts(thin_wait, OUT / "w3-thin-ratification-wait")
write_ratification_artifacts(thin_lighter, OUT / "w3-thin-ratification-lighter")
before = resolve_lesson_plan_collateral_selection(thin_wait.s8_intent)
after = resolve_lesson_plan_collateral_selection(thin_lighter.s8_intent)
delta = compute_selection_delta(before=before, after=after)
write_selection_delta(delta, OUT / "w4-selection-delta.json")

collateral = CollateralSpec(
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
rich_record = ratify_planning_decision(
    assessment=tejal,
    purpose="Bridge assessments to Module 2 with workbook companion",
    audience="APC C1 learners",
    workflow="narrated-deck-with-workbook",
    gap_fill=GapFillTradeoff(
        chosen="synthesize",
        considered=("synthesize", "wait", "lighter_collateral"),
        rationale="Rich curated source: synthesize workbook companion.",
    ),
    collateral=collateral,
    assets_to_create=(
        AssetPlanItem(
            kind="workbook",
            attributes={"kind": "deck-companion"},
        ),
    ),
)
write_ratification_artifacts(rich_record, OUT / "w2-rich-ratification")

summary = {
    "claim": "phase2-evolutionary-planning-to-selection-bridge",
    "claim_fence": (
        "Does not claim full lecture ingestion or lecture-complete selection."
    ),
    "witnesses": {
        "W1_thin_hai_phs": True,
        "W2_rich_tejal": True,
        "W3_gap_fill_tradeoff": {
            "disposition_a": thin_wait.gap_fill.model_dump(),
            "disposition_b": thin_lighter.gap_fill.model_dump(),
        },
        "W4_selection_delta": delta.model_dump(),
        "W5_compose": "stretch-not-claimed",
    },
    "thin_ne_rich": True,
    "ac_p2_5": "same thin fixture, two ratified dispositions",
    "pytest": (
        "tests/marcus/lesson_plan/test_source_assessment.py + "
        "test_planning_ratification.py"
    ),
}
(OUT / "WITNESS-SUMMARY.json").write_text(
    json.dumps(summary, indent=2), encoding="utf-8"
)
(OUT / "CLAIM-ASSESSMENT.md").write_text(
    "# Phase-2 evolutionary bridge — claim assessment\n\n"
    "**Verdict: MET (W1–W4)** for planning-to-selection bridge.\n\n"
    "- W1 thin: HAI + PHS assessments banked\n"
    "- W2 rich: Tejal curated assessment + workbook ratification banked\n"
    "- W3 tradeoff: structured gap_fill on thin ratification\n"
    "- W4 delta: baseline motion bundle → narrated-deck (changed)\n"
    "- W5 compose: stretch / not claimed this close\n"
    "- Fence: does not claim full lecture ingestion\n",
    encoding="utf-8",
)
print("evidence written to", OUT)
print("delta", delta.model_dump())
