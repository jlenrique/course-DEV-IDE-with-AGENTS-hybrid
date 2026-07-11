"""Hermetic RED tests for W3 research-trends + hot-topics backmatter."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from app.marcus.lesson_plan.collateral_spec import (
    DepthDeltaContract,
    Exercise,
    WorkbookSection,
    WorkbookSpec,
)
from app.marcus.lesson_plan.produced_asset import ProductionContext
from app.marcus.lesson_plan.research_packet import SCHEMA_VERSION, ResearchPacket
from app.marcus.lesson_plan.schema import PlanUnit
from app.marcus.lesson_plan.trends_projection import (
    TRENDS_WRITER_REQUIRED_MARKER,
    project_trends_from_packet,
    reject_model_prior_topic,
    trends_inputs_from_run,
)
from app.marcus.lesson_plan.workbook_producer import (
    compose_workbook,
    default_prose_revoicer,
    load_transcript_segments,
    render_markdown,
)
from app.models.runtime.production_envelope import (
    ProductionEnvelope,
    SpecialistContribution,
)
from app.models.runtime.production_trial_envelope import ProductionTrialEnvelope

REPO_ROOT = Path(__file__).resolve().parents[4]
TEJAL_MANIFEST = (
    REPO_ROOT
    / "course-content/staging/tracked/source-bundles"
    / "apc-c1m1-tejal-20260419b-motion"
    / "segment-manifest.yaml"
)


def _entry(**overrides: object) -> dict:
    base = {
        "citation_id": "cite-001",
        "source_ref": "retrieval:scite:10.1000/worked-examples",
        "provider": "scite",
        "source_id": "10.1000/worked-examples",
        "title": "Worked examples improve novice transfer in instruction",
        "source_hash": "sha256:abc",
        "evidence_hierarchy_tier": "T4_peer_other",
        "peer_reviewed": True,
        "provider_provenance": ["scite", "consensus"],
        "triangulation_status": "dual_provider",
        "reliability_score": 0.7,
    }
    base.update(overrides)
    return base


def _packet(entries: list[dict], *, status: str = "ready") -> ResearchPacket:
    from app.marcus.lesson_plan.research_packet import _digest_payload

    payload = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "entries": entries,
        "known_losses": [],
        "research_intake": None,
        "triangulation_receipt": None,
    }
    return ResearchPacket(
        schema_version=SCHEMA_VERSION,
        status=status,  # type: ignore[arg-type]
        entries=tuple(entries),
        known_losses=(),
        research_intake=None,
        triangulation_receipt=None,
        packet_digest=_digest_payload(payload),
        node_id="04.55",
        specialist_id="research_wiring",
    )


def _write_run(run_dir: Path, entries: list[dict]) -> None:
    trial_id = UUID("12345678-1234-4234-8234-123456789abc")
    started = datetime(2026, 7, 10, 12, 0, tzinfo=UTC)
    contrib = SpecialistContribution.from_output(
        specialist_id="research_wiring",
        output={"research_entries": entries},
        model_used="fixture",
        node_id="04.55",
        provenance="fixture",
    )
    envelope = ProductionEnvelope(
        trial_id=trial_id,
        contributions=(contrib,),
        fixture_run=True,
    )
    trial = ProductionTrialEnvelope(
        trial_id=trial_id,
        preset="explore",
        corpus_path="fixture",
        operator_id="w3",
        started_at=started,
        completed_at=started,
        status="completed",
        production_clone_launch_evidence=True,
        production_envelope=envelope,
    )
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "run.json").write_text(trial.model_dump_json(), encoding="utf-8")


def _spec() -> WorkbookSpec:
    return WorkbookSpec(
        sections=[
            WorkbookSection(
                section_id="sec-a",
                learning_objective_id="obj-lo2",
                title="Chapter 2",
                depth_delta=DepthDeltaContract(
                    deferred_from_slide="slide-02",
                    deferred_depth="why administrative waste is an innovation target",
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


def _plan() -> PlanUnit:
    return PlanUnit(
        unit_id="w3-trends-unit",
        event_type="present-trends",
        source_fitness_diagnosis="w3 hermetic",
        weather_band="green",
        modality_ref="workbook",
    )


def _section_body(md: str, heading: str) -> str:
    marker = f"## {heading}\n"
    start = md.index(marker) + len(marker)
    rest = md[start:]
    nxt = rest.find("\n## ")
    return rest if nxt == -1 else rest[:nxt]


def test_packet_grounded_trends_and_hot_topics() -> None:
    brief = project_trends_from_packet(_packet([_entry()]))
    assert brief.usable
    assert len(brief.trends) == 1
    assert brief.trends[0].confidence in {"high", "medium", "low"}
    assert brief.trends[0].source_ref.startswith("retrieval:")
    assert len(brief.hot_topics) >= 1
    assert TRENDS_WRITER_REQUIRED_MARKER in brief.hot_topics[0].rationale
    assert "forecast" in brief.hot_topics[0].rationale.lower()


def test_model_prior_topic_marked_unusable() -> None:
    packet = _packet([_entry()])
    rejected = reject_model_prior_topic("Quantum teleportation in nursing education", packet)
    assert rejected.confidence == "unusable"
    assert "model-prior" in rejected.rationale.lower()

    brief = project_trends_from_packet(
        packet,
        injected_topics=["Completely fabricated hot topic XYZ"],
    )
    unusable = [h for h in brief.hot_topics if h.confidence == "unusable"]
    assert len(unusable) == 1
    assert "fabricated hot topic" in unusable[0].topic.lower()


def test_empty_packet_recorded_empty() -> None:
    brief = project_trends_from_packet(_packet([], status="empty"))
    assert not brief.usable
    assert brief.empty_reason is not None
    assert "not fabricated" in brief.empty_reason.lower()


def test_compose_renders_trends_after_references() -> None:
    segments = load_transcript_segments(TEJAL_MANIFEST)
    brief = project_trends_from_packet(_packet([_entry()]))
    doc = compose_workbook(
        _plan(),
        ProductionContext(lesson_plan_revision=1, lesson_plan_digest="w3"),
        _spec(),
        segments,
        prose_revoicer=default_prose_revoicer,
        research_trends=brief,
    )
    md = render_markdown(doc)
    body = _section_body(md, "Research Trends")
    assert "Research trends" in body
    assert "Hot topics" in body
    assert "confidence=" in body
    assert "Provenance:" in body
    assert md.index("## References") < md.index("## Research Trends")


def test_compose_empty_trends_not_fabricated() -> None:
    segments = load_transcript_segments(TEJAL_MANIFEST)
    brief = project_trends_from_packet(_packet([], status="absent"))
    doc = compose_workbook(
        _plan(),
        ProductionContext(lesson_plan_revision=1, lesson_plan_digest="w3"),
        _spec(),
        segments,
        prose_revoicer=default_prose_revoicer,
        research_trends=brief,
    )
    body = _section_body(render_markdown(doc), "Research Trends")
    assert "explicitly-empty" in body.lower() or "not fabricated" in body.lower()
    assert "https://doi.org/" not in body


def test_trends_inputs_from_run(tmp_path: Path) -> None:
    _write_run(tmp_path, [_entry()])
    brief = trends_inputs_from_run(tmp_path)
    assert brief.usable
    assert brief.trends[0].citation_id == "cite-001"
