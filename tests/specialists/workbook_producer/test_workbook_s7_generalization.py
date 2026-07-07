"""S7 canonical-arc RED-first floors: the 07W producer generalizes off tejal.

Encodes the S7 acceptance criteria (spec
``canonical-arc-s7-workbook-generalization.md``):

- AC-1 no tejal leakage on BOTH paths (no-card fallback KC/further-reading;
  card-present header ``Unit ID:`` / H1 title).
- AC-2 blueprint provenance: sections/titles/depth trace to Irene's collateral,
  NOT the enrichment ``provisional_los`` synthesis (enrichment extra LO/section
  is ignored — collateral is the structural authority).
- AC-3 declaration honored: present+absent-blueprint => fail-loud; none =>
  explicit no-op skip (no stale artifact; valid return contract).
- AC-4 research_entries under G2 (F-2601/F-2604): DOI rendered with
  source_ref/provider/citation_id; a corrupt research source_ref FAILS G2;
  supports_segment_id only when present; zero rows => recorded-empty w/ reason.

RED-first: each assertion targets S7 behavior the pre-S7 constant producer could
not emit (tejal constants + tejal header on every run; enrichment authored the
sections; research rendered outside G2; the hardcoded "deferred" note).

OFFLINE ONLY: no live LLM / network. The producer reads the frozen run.json.
"""

from __future__ import annotations

import json
import shutil
import uuid
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
import yaml

from app.marcus.lesson_plan.workbook_producer import (
    ResearchEntry,
    WorkbookFidelityError,
    WorkbookProducer,
)
from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.workbook_producer import _act as wb_act

from ._run_fixture import collateral_present, section, write_run_json

REPO_ROOT = Path(__file__).resolve().parents[3]

# A NON-tejal corpus + numeral-free narration (so the G1 symbol-gate is a
# non-event and no tejal Chapter-2/3 numerals appear).
_CORPUS = (
    "The clinician-innovator diagnoses the operational root cause before buying "
    "a solution; opportunity is scanned across past, present, and future.\n"
)
_SEGMENTS = [
    {
        "segment_id": "seg-01",
        "id": "seg-01",
        "slide_id": "slide-01",
        "narration_text": (
            "Innovating inside the hospital means navigating politics and legacy "
            "systems rather than launching a standalone startup."
        ),
    },
    {
        "segment_id": "seg-02",
        "id": "seg-02",
        "slide_id": "slide-02",
        "narration_text": (
            "Fall in love with the problem: diagnose the systemic root cause "
            "before committing to any single solution."
        ),
    },
]

# Distinctive, non-tejal collateral blueprint (Part-3 flavored).
_COLLATERAL = collateral_present(
    [
        section(
            "sec-opportunity-radar",
            "lo-core-radar",
            title="The Opportunity Radar past present future",
            deferred_depth=(
                "The read-channel derivation the glance deck defers: audit past "
                "frustrations, present workarounds, and future trends to surface a "
                "vetted opportunity via the five-whys root-cause discipline."
            ),
            narrative_intent="The fuller opportunity-radar narrative for the reader.",
        ),
    ]
)


def _make_run_dir(
    root: Path,
    *,
    collateral: dict[str, Any] | None,
    enrichment_card: dict[str, Any] | None = None,
    plan_units: list[dict[str, Any]] | None = None,
    lesson_summary: str = "opportunity clinician innovator",
    research_entries: list[dict[str, Any]] | None = None,
) -> Path:
    run_dir = root / "run"
    (run_dir / "exports").mkdir(parents=True, exist_ok=True)
    (run_dir / "bundle").mkdir(parents=True, exist_ok=True)
    (run_dir / "exports" / "segment-manifest-storyboard-b.yaml").write_text(
        yaml.safe_dump({"segments": _SEGMENTS}, sort_keys=False), encoding="utf-8"
    )
    (run_dir / "bundle" / "extracted.md").write_text(_CORPUS, encoding="utf-8")
    if enrichment_card is not None:
        (run_dir / "g0-enrichment.json").write_text(
            json.dumps(enrichment_card), encoding="utf-8"
        )
    if collateral is not None:
        write_run_json(
            run_dir,
            collateral=collateral,
            plan_units=plan_units
            if plan_units is not None
            else [{"unit_id": "u-opportunity-clinician-innovator"}],
            lesson_summary=lesson_summary,
            research_entries=research_entries,
        )
    return run_dir


@pytest.fixture
def output_root() -> Iterator[Path]:
    # Distinct parent (NOT the shared ``workbooks-test`` dir the pre-existing
    # tejal producer tests write their fixed ``…@3.docx`` stem into) so this
    # file's mkdir/rmtree churn cannot aggravate that pre-existing shared-output-
    # root race.
    target = (
        REPO_ROOT
        / "_bmad-output"
        / "artifacts"
        / "workbooks-test-s7"
        / f"_s7-{uuid.uuid4().hex}"
    )
    target.mkdir(parents=True, exist_ok=True)
    try:
        yield target
    finally:
        shutil.rmtree(target, ignore_errors=True)


def _render(run_dir: Path, output_root: Path) -> str:
    inputs = wb_act.build_workbook_inputs(run_dir, run_id="s7testrun01")
    assert inputs is not None
    producer = WorkbookProducer(output_root=str(output_root))
    sidecar = producer.produce(
        inputs.plan_unit,
        inputs.context,
        spec=inputs.spec,
        segments=inputs.segments,
        source_text=inputs.source_text,
        citations=inputs.citations,
        source_ref_manifest=inputs.source_ref_manifest,
        vo_script_text=inputs.vo_script_text,
        learning_objectives=inputs.learning_objectives,
        answer_keys=inputs.answer_keys,
        further_reading=inputs.further_reading,
        research_entries=inputs.research_entries,
        research_empty_reason=inputs.research_empty_reason,
        diff_files=["app/marcus/lesson_plan/workbook_producer.py"],
        reuse_sha="s7test",
    )
    return (REPO_ROOT / sidecar.markdown_path).read_text(encoding="utf-8")


def _seed_state(payload: dict[str, Any]) -> RunState:
    entry = ModelResolutionEntry(
        level="per_specialist",
        requested="gpt-5-nano",
        resolved="gpt-5-nano",
        reason="seed",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
    )
    return RunState(
        graph_version="v0.1-stub",
        temperature=0.0,
        model_resolution_trail=[entry],
        cache_state=CacheState(
            cache_prefix=json.dumps(payload, sort_keys=True), entries_count=0
        ),
    )


_TEJAL_LEAK_TOKENS = (
    "ex-ch2-q1",
    "ex-ch3-q1",
    "nhe-fact-sheet",
    "Chapter 2 — The Macro Trends",
    "Chapter 3 — The Case for Change",
    "Between 2012 and 2022",
    "73 days",
    "present-trends",
    "tejal-apc-c1-m1",
    "macro-trends",
)


# --------------------------------------------------------------------------- #
# AC-1 — no tejal leakage (BOTH paths)                                         #
# --------------------------------------------------------------------------- #
def test_ac1_no_card_fallback_emits_no_tejal_constants(tmp_path, output_root) -> None:
    # No enrichment card => the OLD producer fell back to the tejal KC / further-
    # reading constants. S7 retires them: a non-tejal run must carry NONE.
    run_dir = _make_run_dir(tmp_path, collateral=_COLLATERAL, enrichment_card=None)
    md = _render(run_dir, output_root)
    for token in _TEJAL_LEAK_TOKENS:
        assert token not in md, f"tejal constant leaked into a non-tejal workbook: {token!r}"
    # Positive control: the run's REAL collateral drives the artifact.
    assert "The Opportunity Radar past present future" in md


def test_ac1_card_present_header_carries_no_tejal_unit_metadata(
    tmp_path, output_root
) -> None:
    # The card-present enriched path is the vector that survives live: the tejal
    # unit_id / event_type header. S7 derives them from the run's real lesson plan.
    run_dir = _make_run_dir(tmp_path, collateral=_COLLATERAL, enrichment_card={})
    md = _render(run_dir, output_root)
    h1 = md.splitlines()[0]
    assert h1.startswith("# Workbook:")
    unit_line = next(line for line in md.splitlines() if line.startswith("Unit ID:"))
    for forbidden in ("tejal", "present-trends", "macro-trends"):
        assert forbidden not in h1.lower()
        assert forbidden not in unit_line.lower()
    # Traces to the run's real corpus/plan (non-tejal derivation).
    assert "opportunity" in (h1 + unit_line).lower()


# --------------------------------------------------------------------------- #
# AC-2 — blueprint provenance (collateral authoritative; enrichment extra      #
# LO/section is IGNORED — the projection may not author sections)             #
# --------------------------------------------------------------------------- #
_ENRICH_EXTRA = {
    "provisional_los": [
        {"objective_id": "lo-enrich-alpha", "statement": "ENRICH-SYNTH-SECTION alpha stmt"},
    ],
    "typed_components": [
        {"component_id": "quiz-alpha", "source_type": "quiz", "excerpt": "quiz alpha"},
    ],
    "pedagogy_annotations": [
        {
            "component_id": "quiz-alpha",
            "lo_refs": ["lo-enrich-alpha"],
            "bloom": "apply",
            "teachable": True,
            "assessment_link": None,
        }
    ],
    "citation_resolutions": [],
}


def test_ac2_sections_trace_to_collateral_not_enrichment_synthesis(
    tmp_path, output_root
) -> None:
    run_dir = _make_run_dir(
        tmp_path, collateral=_COLLATERAL, enrichment_card=_ENRICH_EXTRA
    )
    md = _render(run_dir, output_root)
    # Section id / title / depth trace to Irene's authored collateral strings.
    assert "sec-opportunity-radar" in md
    assert "The Opportunity Radar past present future" in md
    assert "five-whys root-cause discipline" in md
    # Enrichment's extra LO/section is NOT authored (collateral is authoritative).
    assert "ENRICH-SYNTH-SECTION alpha stmt" not in md
    assert "sec-lo-enrich-alpha" not in md


# --------------------------------------------------------------------------- #
# AC-3 — declaration honored (fail-loud vs no-op-skip)                         #
# --------------------------------------------------------------------------- #
def test_ac3_present_but_absent_blueprint_fails_loud(tmp_path, output_root) -> None:
    # declaration=="present" but no usable workbook sections => fail-loud
    # (recoverable dispatch error) BEFORE producing a scaffold.
    bad = {"declaration": "present", "workbook": {"sections": []}, "research_goals": []}
    run_dir = _make_run_dir(tmp_path, collateral=bad)
    state = _seed_state({"run_dir": str(run_dir), "output_root": str(output_root)})
    with pytest.raises(wb_act.WorkbookProducerActError) as exc:
        wb_act.act(state)
    assert "blueprint" in exc.value.tag


def test_ac3_declaration_none_is_explicit_no_op_skip(tmp_path, output_root) -> None:
    run_dir = _make_run_dir(tmp_path, collateral={"declaration": "none"})
    state = _seed_state({"run_dir": str(run_dir), "output_root": str(output_root)})
    update = wb_act.act(state)
    out = json.loads(update["cache_state"]["cache_prefix"])
    # Explicit recorded skip; valid (empty) specialist return contract.
    assert out["workbook"]["skipped"] is True
    assert "no artifact" in out["workbook"]["reason"].lower()
    assert "markdown_path" not in out["workbook"]
    assert "docx_path" not in out["workbook"]
    assert update["model_resolution_trail"][-1].reason.endswith("skipped.declaration-none")
    # Negative twin: NO stale artifact was written under the output root.
    assert not list(output_root.glob("*.md"))
    assert not list(output_root.glob("*.docx"))


def test_ac3_absent_collateral_skips(tmp_path, output_root) -> None:
    # A run with segments but NO run.json (absent collateral) => no-op skip.
    run_dir = _make_run_dir(tmp_path, collateral=None)
    state = _seed_state({"run_dir": str(run_dir), "output_root": str(output_root)})
    update = wb_act.act(state)
    out = json.loads(update["cache_state"]["cache_prefix"])
    assert out["workbook"]["skipped"] is True


# --------------------------------------------------------------------------- #
# AC-4 — research_entries under G2 (F-2601 / F-2604)                           #
# --------------------------------------------------------------------------- #
_RESEARCH = [
    {
        "citation_id": "rc-1",
        "source_ref": "scite:10.1234/example.doi",
        "provider": "scite",
        "source_id": "10.1234/example.doi",
        "title": "A real cited study",
        "source_hash": "cafebabecafebabe",
    }
]


def test_ac4_research_entry_rendered_with_provenance_under_g2(
    tmp_path, output_root
) -> None:
    run_dir = _make_run_dir(
        tmp_path, collateral=_COLLATERAL, research_entries=_RESEARCH
    )
    inputs = wb_act.build_workbook_inputs(run_dir, run_id="s7research01")
    assert inputs is not None
    # F-2601: the research source_ref is folded into the G2 manifest.
    assert "scite:10.1234/example.doi" in inputs.source_ref_manifest
    producer = WorkbookProducer(output_root=str(output_root))
    sidecar = producer.produce(
        inputs.plan_unit,
        inputs.context,
        spec=inputs.spec,
        segments=inputs.segments,
        source_text=inputs.source_text,
        citations=inputs.citations,
        source_ref_manifest=inputs.source_ref_manifest,
        vo_script_text=inputs.vo_script_text,
        learning_objectives=inputs.learning_objectives,
        answer_keys=inputs.answer_keys,
        further_reading=inputs.further_reading,
        research_entries=inputs.research_entries,
        research_empty_reason=inputs.research_empty_reason,
    )
    md = (REPO_ROOT / sidecar.markdown_path).read_text(encoding="utf-8")
    assert "https://doi.org/10.1234/example.doi" in md
    assert "provider: scite" in md
    assert "citation_id: `rc-1`" in md
    assert "source_ref: `scite:10.1234/example.doi`" in md
    # The rendered research DOI passed under the G2 citation gate (0 unsourced).
    assert sidecar.citation_audit["buckets"]["unsourced_citations"]["count"] == 0


def test_ac4_corrupt_research_source_ref_fails_g2(output_root) -> None:
    # F-2601 teeth: a rendered research DOI whose source_ref is absent from the G2
    # manifest FAILS the citation gate (produce-level, independently RED-able).
    from app.marcus.lesson_plan.produced_asset import ProductionContext
    from app.marcus.lesson_plan.schema import PlanUnit
    from app.marcus.lesson_plan.workbook_producer import TranscriptSegment

    plan_unit = PlanUnit(
        unit_id="u-x",
        event_type="companion",
        source_fitness_diagnosis="x",
        weather_band="green",
        modality_ref="workbook",
    )
    ctx = ProductionContext(lesson_plan_revision=1, lesson_plan_digest="deadbeef")
    from app.marcus.lesson_plan.collateral_spec import (
        DepthDeltaContract,
        WorkbookSection,
        WorkbookSpec,
    )

    spec = WorkbookSpec(
        sections=[
            WorkbookSection(
                section_id="sec-x",
                learning_objective_id="obj-x",
                title="X",
                depth_delta=DepthDeltaContract(
                    deferred_from_slide="slide-01",
                    deferred_depth="deferred depth for objective x carried in the workbook",
                ),
            )
        ]
    )
    segments = (
        TranscriptSegment(
            segment_id="seg-01",
            narration_text="A short numeral-free narration line.",
            visual_file=None,
            visual_references=(),
            source_ref="src-seg-01",
        ),
    )
    corrupt = ResearchEntry(
        citation_id="rc-1",
        title="A study",
        source_ref="ghost-unresolvable-ref",
        provider="scite",
        source_id="10.1/x",
    )
    producer = WorkbookProducer(output_root=str(output_root))
    with pytest.raises(WorkbookFidelityError, match="citation"):
        producer.produce(
            plan_unit,
            ctx,
            spec=spec,
            segments=segments,
            source_text="A short numeral-free source line.",
            citations=[],
            source_ref_manifest={},  # research source_ref is NOT in the manifest
            vo_script_text="A short numeral-free narration line.",
            research_entries=[corrupt],
        )


def test_ac4_supports_segment_id_rendered_only_when_present(
    tmp_path, output_root
) -> None:
    with_support = [dict(_RESEARCH[0], supports_segment_id="seg-02")]
    run_dir = _make_run_dir(
        tmp_path, collateral=_COLLATERAL, research_entries=with_support
    )
    md = _render(run_dir, output_root)
    assert "supports `seg-02`" in md
    # And a run WHOSE entry omits supports renders NO supports clause (no inference).
    shutil.rmtree(run_dir, ignore_errors=True)
    run_dir2 = _make_run_dir(
        tmp_path / "b", collateral=_COLLATERAL, research_entries=_RESEARCH
    )
    md2 = _render(run_dir2, output_root)
    live_block = md2.split("Live-research")[-1]
    assert "supports `" not in live_block


def test_ac4_zero_rows_recorded_empty_not_fabricated(tmp_path, output_root) -> None:
    # A creds-present-but-empty run (research contribution present, zero rows) =>
    # recorded explicitly-empty WITH reason; NO fabricated DOI.
    run_dir = _make_run_dir(tmp_path, collateral=_COLLATERAL, research_entries=[])
    md = _render(run_dir, output_root)
    live_block = md.split("Live-research")[-1]
    assert "recorded" in live_block.lower() and "explicitly-empty" in live_block.lower()
    assert "https://doi.org/" not in live_block
