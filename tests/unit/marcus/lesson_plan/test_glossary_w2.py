"""Hermetic RED tests for W2 encyclopedia glossary projection + compose."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

import pytest

from app.marcus.lesson_plan.collateral_spec import (
    DepthDeltaContract,
    Exercise,
    WorkbookSection,
    WorkbookSpec,
)
from app.marcus.lesson_plan.glossary_projection import (
    GLOSSARY_CAPABILITY_NOTE,
    GLOSSARY_WRITER_REQUIRED_MARKER,
    default_glossary_writer,
    glossary_inputs_from_run,
    project_glossary_articles,
)
from app.marcus.lesson_plan.produced_asset import ProductionContext
from app.marcus.lesson_plan.research_packet import ResearchPacket
from app.marcus.lesson_plan.schema import PlanUnit
from app.marcus.lesson_plan.workbook_producer import (
    LearningObjectiveBrief,
    WorkbookFidelityError,
    WorkbookProducer,
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
TEST_OUTPUT_ROOT = "_bmad-output/artifacts/workbooks-test"


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
    from app.marcus.lesson_plan.research_packet import SCHEMA_VERSION, _digest_payload

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
        operator_id="w2",
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
        unit_id="w2-glossary-unit",
        event_type="present-trends",
        source_fitness_diagnosis="w2 hermetic",
        weather_band="green",
        modality_ref="workbook",
    )


def _section_body(md: str, heading: str) -> str:
    marker = f"## {heading}\n"
    start = md.index(marker) + len(marker)
    rest = md[start:]
    nxt = rest.find("\n## ")
    return rest if nxt == -1 else rest[:nxt]


def test_default_writer_is_encyclopedia_not_dictionary_gloss() -> None:
    article = default_glossary_writer(_entry())
    assert "encyclopedia" in article.headline.lower()
    # John done-bar: no HTML stub marker in learner-facing body.
    assert GLOSSARY_WRITER_REQUIRED_MARKER not in article.body
    # Winston honesty: capability note remains visible (not silent SME-complete).
    assert GLOSSARY_CAPABILITY_NOTE in article.body
    assert "not a human sme-reviewed" in article.body.lower()
    assert "dictionary gloss" in article.body.lower()
    assert "no study findings are invented" in article.body.lower()
    assert article.source_ref.startswith("retrieval:")
    assert article.evidence_hierarchy_tier == "T4_peer_other"
    assert "scite" in article.provider_provenance


def test_injectable_writer_replaces_default_body() -> None:
    from app.marcus.lesson_plan.glossary_projection import GlossaryArticleBrief

    def custom(entry: dict) -> GlossaryArticleBrief:
        return GlossaryArticleBrief(
            term="Custom Term",
            headline="Custom headline",
            body="Injectable body replaces default.",
            citation_id=str(entry["citation_id"]),
            source_ref=str(entry["source_ref"]),
            source_id=str(entry["source_id"]),
            provider=str(entry["provider"]),
            evidence_hierarchy_tier=str(entry["evidence_hierarchy_tier"]),
            peer_reviewed=True,
            provider_provenance=("scite",),
            triangulation_status="dual_provider",
            title=str(entry["title"]),
        )

    articles, reason, _ = project_glossary_articles(
        _packet([_entry()]), writer=custom
    )
    assert reason is None
    assert len(articles) == 1
    assert articles[0].body == "Injectable body replaces default."
    assert GLOSSARY_CAPABILITY_NOTE not in articles[0].body


def test_missing_provenance_skipped_not_fabricated() -> None:
    bad = _entry()
    del bad["provider_provenance"]
    # Shape-invalid rows never reach project via packet; simulate degraded packet
    # with a row missing provenance that somehow passed (empty list).
    bad["provider_provenance"] = []
    articles, reason, losses = project_glossary_articles(_packet([bad, _entry(citation_id="cite-002")]))
    assert len(articles) == 1
    assert articles[0].citation_id == "cite-002"
    assert any("missing_provenance" in loss for loss in losses)
    assert reason is None


def test_empty_packet_recorded_empty() -> None:
    articles, reason, _losses = project_glossary_articles(
        _packet([], status="empty")
    )
    assert articles == ()
    assert reason is not None
    assert "not fabricated" in reason.lower() or "explicitly-empty" in reason.lower()


def test_compose_renders_research_glossary_section() -> None:
    segments = load_transcript_segments(TEJAL_MANIFEST)
    articles, _, _ = project_glossary_articles(_packet([_entry()]))
    doc = compose_workbook(
        _plan(),
        ProductionContext(lesson_plan_revision=1, lesson_plan_digest="w2"),
        _spec(),
        segments,
        prose_revoicer=default_prose_revoicer,
        glossary_articles=articles,
    )
    md = render_markdown(doc)
    body = _section_body(md, "Research Glossary")
    assert "### " in body
    assert "Provenance:" in body
    assert "10.1000/worked-examples" in body
    assert "T4_peer_other" in body
    # Glossary sits before References.
    assert md.index("## Research Glossary") < md.index("## References")


def test_compose_empty_glossary_not_fabricated() -> None:
    segments = load_transcript_segments(TEJAL_MANIFEST)
    doc = compose_workbook(
        _plan(),
        ProductionContext(lesson_plan_revision=1, lesson_plan_digest="w2"),
        _spec(),
        segments,
        prose_revoicer=default_prose_revoicer,
        glossary_empty_reason="no usable research packet rows for glossary",
    )
    body = _section_body(render_markdown(doc), "Research Glossary")
    assert "no usable research packet" in body
    assert "https://doi.org/" not in body


def test_glossary_inputs_from_run(tmp_path: Path) -> None:
    _write_run(tmp_path, [_entry()])
    articles, reason, _losses = glossary_inputs_from_run(tmp_path)
    assert reason is None
    assert len(articles) == 1
    assert articles[0].source_ref == "retrieval:scite:10.1000/worked-examples"


def test_produce_g2_fails_on_fabricated_glossary_source_ref() -> None:
    segments = load_transcript_segments(TEJAL_MANIFEST)
    source_text = (
        REPO_ROOT
        / "course-content/staging/tracked/source-bundles"
        / "apc-c1m1-tejal-20260419b-motion"
        / "extracted.md"
    ).read_text(encoding="utf-8")
    articles, _, _ = project_glossary_articles(_packet([_entry()]))
    # Fabricate: article cites a source_ref absent from the G2 manifest.
    producer = WorkbookProducer(output_root=TEST_OUTPUT_ROOT)
    with pytest.raises(WorkbookFidelityError):
        producer.produce(
            _plan(),
            ProductionContext(lesson_plan_revision=1, lesson_plan_digest="w2"),
            spec=_spec(),
            segments=segments,
            source_text=source_text,
            learning_objectives=(
                LearningObjectiveBrief(
                    "obj-lo2", "analyze", "Analyze the macro-economic trends."
                ),
            ),
            glossary_articles=articles,
            source_ref_manifest={},  # empty → fabricate path RED
            citations=[],
        )
