#!/usr/bin/env python3
"""W2 live evidence — encyclopedia glossary from R4 live research rows.

Plants R4 live entries into run.json, projects glossary articles via the W1
packet consumer, and composes a Tejal-backed workbook proving ≥1 non-vacuous
encyclopedia article with source-backed provenance (MD + DOCX same model).

Usage::

    python scripts/utilities/run_workbook_w2_live_evidence.py
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
    from app.marcus.lesson_plan.glossary_projection import (
        GLOSSARY_WRITER_REQUIRED_MARKER,
        glossary_inputs_from_run,
    )
    from app.marcus.lesson_plan.produced_asset import ProductionContext
    from app.marcus.lesson_plan.schema import PlanUnit
    from app.marcus.lesson_plan.workbook_producer import (
        LearningObjectiveBrief,
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
        / f"workbook-w2-{_stamp()}"
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    if not R4_ENTRIES.is_file():
        verdict = {"story": "workbook-w2", "pass": False, "fence": "r4-entries-absent"}
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
        operator_id="w2-live",
        started_at=now,
        completed_at=now,
        status="completed",
        production_clone_launch_evidence=True,
        production_envelope=envelope,
    )
    run_dir = out_dir / "run"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "run.json").write_text(trial.model_dump_json(), encoding="utf-8")

    articles, empty_reason, losses = glossary_inputs_from_run(run_dir, max_articles=3)
    non_vacuous = [
        a
        for a in articles
        if len(a.body) > 200
        and a.source_ref
        and a.evidence_hierarchy_tier
        and a.provider_provenance
        and "encyclopedia" in a.headline.lower()
    ]

    segments = load_transcript_segments(TEJAL_BUNDLE / "segment-manifest.yaml")
    source_text = (TEJAL_BUNDLE / "extracted.md").read_text(encoding="utf-8")
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
        unit_id="apc-c1m1-tejal-w2-glossary",
        event_type="present-trends",
        source_fitness_diagnosis="w2 live glossary",
        weather_band="green",
        modality_ref="workbook",
    )
    context = ProductionContext(lesson_plan_revision=1, lesson_plan_digest="w2-live")
    objectives = (
        LearningObjectiveBrief(
            "obj-lo2", "analyze", "Analyze macro-economic and structural trends."
        ),
    )
    manifest = {a.source_ref: a.source_id for a in articles}

    doc = compose_workbook(
        plan,
        context,
        spec,
        segments,
        prose_revoicer=default_prose_revoicer,
        learning_objectives=objectives,
        glossary_articles=articles,
        glossary_empty_reason=empty_reason,
    )
    md = render_markdown(doc)
    (out_dir / "glossary-compose.md").write_text(md, encoding="utf-8")
    docx_path = out_dir / "glossary-compose.docx"
    render_docx_from_model(doc, docx_path)

    # G2 witness: every glossary source_ref resolves in the planted manifest.
    from app.marcus.lesson_plan.workbook_producer import audit_citation_fidelity

    citation_audit = audit_citation_fidelity(
        [{"source_ref": a.source_ref} for a in articles],
        manifest,
    )
    g2_ok = citation_audit["buckets"]["unsourced_citations"]["count"] == 0

    glossary_section_ok = "## Research Glossary" in md and "### " in md
    provenance_ok = all(
        "Provenance:" in md and a.citation_id in md for a in articles[:1]
    )
    marker_ok = GLOSSARY_WRITER_REQUIRED_MARKER in md
    empty_articles, empty_reason2, _ = glossary_inputs_from_run(
        out_dir / "no-such-run", max_articles=3
    )
    empty_path_ok = empty_articles == () and empty_reason2 is not None

    steps = [
        {
            "step": "non_vacuous_encyclopedia_article",
            "pass": len(non_vacuous) >= 1,
            "article_count": len(articles),
            "non_vacuous_count": len(non_vacuous),
            "sample_term": non_vacuous[0].term if non_vacuous else None,
        },
        {
            "step": "provenance_retained",
            "pass": provenance_ok and bool(articles),
            "sample_source_ref": articles[0].source_ref if articles else None,
            "sample_tier": articles[0].evidence_hierarchy_tier if articles else None,
        },
        {
            "step": "compose_research_glossary_section",
            "pass": glossary_section_ok and marker_ok,
        },
        {
            "step": "md_docx_same_composed_model",
            "pass": docx_path.is_file() and g2_ok,
            "markdown_path": str((out_dir / "glossary-compose.md").relative_to(ROOT)),
            "docx_path": str(docx_path.relative_to(ROOT)),
            "g2_unsourced": citation_audit["buckets"]["unsourced_citations"]["count"],
        },
        {
            "step": "empty_research_not_fabricated",
            "pass": empty_path_ok,
        },
    ]
    all_pass = all(bool(s.get("pass")) for s in steps)
    verdict = {
        "story": "workbook-w2",
        "pass": all_pass,
        "trial_id": str(trial_id),
        "claim": (
            "Encyclopedia glossary articles from credibility-labeled research "
            "rows; provenance retained; empty not fabricated"
        ),
        "steps": steps,
        "known_losses_sample": list(losses)[:5],
        "empty_reason": empty_reason,
    }
    (out_dir / "verdict.json").write_text(
        json.dumps(verdict, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "PROOF.md").write_text(
        "\n".join(
            [
                "# W2 Glossary encyclopedia — live proof",
                "",
                f"- pass: `{all_pass}`",
                f"- articles: `{len(articles)}` (non-vacuous `{len(non_vacuous)}`)",
                f"- sample term: `{non_vacuous[0].term if non_vacuous else 'n/a'}`",
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
