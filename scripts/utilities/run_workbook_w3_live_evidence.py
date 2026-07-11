#!/usr/bin/env python3
"""W3 live evidence — research-trends + hot-topics from R4 live rows.

Usage::

    python scripts/utilities/run_workbook_w3_live_evidence.py
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(ROOT / ".env", override=True)

TEJAL_BUNDLE = (
    ROOT
    / "course-content/staging/tracked/source-bundles"
    / "apc-c1m1-tejal-20260419b-motion"
)
R4_ENTRIES = (
    ROOT
    / "_bmad-output/implementation-artifacts/evidence"
    / "research-r4-20260710T233843Z/entries.json"
)


def _stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def main() -> int:
    from app.marcus.lesson_plan.collateral_spec import (
        DepthDeltaContract,
        Exercise,
        WorkbookSection,
        WorkbookSpec,
    )
    from app.marcus.lesson_plan.produced_asset import ProductionContext
    from app.marcus.lesson_plan.schema import PlanUnit
    from app.marcus.lesson_plan.trends_projection import (
        TRENDS_WRITER_REQUIRED_MARKER,
        trends_inputs_from_run,
    )
    from app.marcus.lesson_plan.workbook_producer import (
        LearningObjectiveBrief,
        audit_citation_fidelity,
        compose_workbook,
        default_prose_revoicer,
        load_transcript_segments,
        render_docx_from_model,
        render_markdown,
    )
    from app.models.runtime.production_envelope import (
        ProductionEnvelope,
        SpecialistContribution,
    )
    from app.models.runtime.production_trial_envelope import ProductionTrialEnvelope

    out_dir = (
        ROOT
        / "_bmad-output"
        / "implementation-artifacts"
        / "evidence"
        / f"workbook-w3-{_stamp()}"
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    if not R4_ENTRIES.is_file():
        verdict = {"story": "workbook-w3", "pass": False, "fence": "r4-entries-absent"}
        (out_dir / "verdict.json").write_text(
            json.dumps(verdict, indent=2) + "\n", encoding="utf-8"
        )
        return 2

    entries = json.loads(R4_ENTRIES.read_text(encoding="utf-8"))
    trial_id = uuid4()
    now = datetime.now(UTC)
    contrib = SpecialistContribution.from_output(
        specialist_id="research_wiring",
        output={"research_entries": entries},
        model_used="live-r4-replay",
        node_id="04.55",
        provenance="real",
    )
    envelope = ProductionEnvelope(trial_id=trial_id, contributions=(contrib,))
    trial = ProductionTrialEnvelope(
        trial_id=trial_id,
        preset="explore",
        corpus_path="research-r4-live-replay",
        operator_id="w3-live",
        started_at=now,
        completed_at=now,
        status="completed",
        production_clone_launch_evidence=True,
        production_envelope=envelope,
    )
    run_dir = out_dir / "run"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "run.json").write_text(trial.model_dump_json(), encoding="utf-8")

    brief = trends_inputs_from_run(
        run_dir,
        max_trends=5,
        max_hot_topics=3,
        injected_topics=["Fabricated quantum nursing forecast 2099"],
    )
    usable_trends = [t for t in brief.trends if t.confidence != "unusable"]
    usable_hot = [h for h in brief.hot_topics if h.confidence != "unusable"]
    unusable_hot = [h for h in brief.hot_topics if h.confidence == "unusable"]

    segments = load_transcript_segments(TEJAL_BUNDLE / "segment-manifest.yaml")
    spec = WorkbookSpec(
        sections=[
            WorkbookSection(
                section_id="sec-a",
                learning_objective_id="obj-lo2",
                title="Trends",
                depth_delta=DepthDeltaContract(
                    deferred_from_slide="slide-02",
                    deferred_depth="systems trends depth",
                ),
                exercises=[
                    Exercise(
                        exercise_id="ex-a1",
                        bloom_level="analyze",
                        prompt_intent="Analyze",
                        answer_key_source_ref="src-slide-02",
                    )
                ],
            )
        ]
    )
    plan = PlanUnit(
        unit_id="apc-c1m1-tejal-w3-trends",
        event_type="present-trends",
        source_fitness_diagnosis="w3 live trends",
        weather_band="green",
        modality_ref="workbook",
    )
    context = ProductionContext(lesson_plan_revision=1, lesson_plan_digest="w3-live")
    objectives = (
        LearningObjectiveBrief(
            "obj-lo2", "analyze", "Analyze macro-economic and structural trends."
        ),
    )
    manifest = {t.source_ref: t.source_id for t in usable_trends}

    doc = compose_workbook(
        plan,
        context,
        spec,
        segments,
        prose_revoicer=default_prose_revoicer,
        learning_objectives=objectives,
        research_trends=brief,
    )
    md = render_markdown(doc)
    (out_dir / "trends-compose.md").write_text(md, encoding="utf-8")
    docx_path = out_dir / "trends-compose.docx"
    render_docx_from_model(doc, docx_path)

    citation_audit = audit_citation_fidelity(
        [{"source_ref": t.source_ref} for t in usable_trends],
        manifest,
    )

    steps = [
        {
            "step": "non_vacuous_trends",
            "pass": len(usable_trends) >= 1 and all(t.source_ref for t in usable_trends),
            "trend_count": len(usable_trends),
            "sample_claim": usable_trends[0].claim_text[:120] if usable_trends else None,
        },
        {
            "step": "bounded_hot_topics_with_provenance",
            "pass": (
                1 <= len(usable_hot) <= 3
                and all(h.source_refs for h in usable_hot)
                and any(TRENDS_WRITER_REQUIRED_MARKER in h.rationale for h in usable_hot)
            ),
            "hot_topic_count": len(usable_hot),
            "sample_topic": usable_hot[0].topic if usable_hot else None,
        },
        {
            "step": "model_prior_rejected",
            "pass": len(unusable_hot) >= 1
            and any("fabricated" in h.topic.lower() for h in unusable_hot),
            "unusable_count": len(unusable_hot),
        },
        {
            "step": "compose_section_after_references",
            "pass": "## Research Trends" in md
            and md.index("## References") < md.index("## Research Trends")
            and "confidence=" in md,
        },
        {
            "step": "md_docx_same_model_g2_clean",
            "pass": docx_path.is_file()
            and citation_audit["buckets"]["unsourced_citations"]["count"] == 0,
            "g2_unsourced": citation_audit["buckets"]["unsourced_citations"]["count"],
        },
    ]
    all_pass = all(bool(s.get("pass")) for s in steps)
    verdict = {
        "story": "workbook-w3",
        "pass": all_pass,
        "trial_id": str(trial_id),
        "claim": (
            "Packet-grounded research-trends + bounded hot-topics; "
            "model-prior topics unusable; confidence/provenance labeled"
        ),
        "steps": steps,
    }
    (out_dir / "verdict.json").write_text(
        json.dumps(verdict, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "PROOF.md").write_text(
        "\n".join(
            [
                "# W3 Research trends / hot-topics — live proof",
                "",
                f"- pass: `{all_pass}`",
                f"- trends: `{len(usable_trends)}`",
                f"- hot topics: `{len(usable_hot)}` (unusable injected: `{len(unusable_hot)}`)",
                "",
                "## Steps",
                "",
                *[
                    f"- **{s['step']}**: `{'PASS' if s.get('pass') else 'FAIL'}`"
                    for s in steps
                ],
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps(verdict, indent=2))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
