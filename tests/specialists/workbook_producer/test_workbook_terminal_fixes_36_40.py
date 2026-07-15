"""Red-first floors for the terminal 07W emission fixes (epics 36-40).

Six coupled defects kept the terminal workbook node from reaching a captured,
conforming, deterministic deliverable. These floors pin the producer-facing
five (the sixth, B7 zero-provider-call replay safety, lives in the
orchestrator reconcile test module):

- Q1: the enrichment overlay (keyed ``lo-g0-NNN``) resolves against a collateral
  section bound to a plan-unit id (``uNN``) via the plan-unit ``[evidence:
  src-NNN]`` bridge; an unbridgeable objective records a VISIBLE loss instead of
  silently degrading.
- B5: research-leg figures are declared as G1 ``research_supplements`` so a
  legitimate research numeral does not fail the numeric gate.
- B6: the deliverable is emitted under a TRIAL-SCOPED ``<run_dir>/exports`` path
  (governed-inventory bindable) by default.
- B8: the rendered DOCX is byte-deterministic across two renders of one model.
- Q2: corpus-native references (references/*.md + per-slide ``**References:**``)
  populate the S6 References channel on a references-bearing corpus.

OFFLINE ONLY: no live LLM / network. Deterministic.
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

from app.marcus.lesson_plan.workbook_enrichment import (
    corpus_native_further_reading,
    corpus_root_from_run,
)
from app.marcus.lesson_plan.workbook_producer import (
    WorkbookFidelityError,
    WorkbookProducer,
    _ComposedDoc,
    render_docx_from_model,
)
from app.models.runtime.production_envelope import (
    ProductionEnvelope,
    SpecialistContribution,
)
from app.models.runtime.production_trial_envelope import ProductionTrialEnvelope
from app.specialists.workbook_producer import _act as wb_act

from ._run_fixture import collateral_present, section

REPO_ROOT = Path(__file__).resolve().parents[3]

# Numeral-free corpus + narration so the G1 symbol gate is a non-event unless a
# test deliberately injects a research numeral.
_CORPUS = "The clinician diagnoses the operational root cause before buying a fix.\n"
_SEGMENTS = [
    {
        "segment_id": "seg-01",
        "id": "seg-01",
        "slide_id": "slide-01",
        "narration_text": "Innovating inside the hospital means navigating legacy systems.",
    },
    {
        "segment_id": "seg-02",
        "id": "seg-02",
        "slide_id": "slide-02",
        "narration_text": "Fall in love with the problem before committing to any solution.",
    },
]


@pytest.fixture
def output_root() -> Iterator[Path]:
    target = (
        REPO_ROOT
        / "_bmad-output"
        / "artifacts"
        / "workbooks-test-s7"
        / f"_term-{uuid.uuid4().hex}"
    )
    target.mkdir(parents=True, exist_ok=True)
    try:
        yield target
    finally:
        shutil.rmtree(target, ignore_errors=True)


def _write_run_json(
    run_dir: Path,
    *,
    collateral: dict[str, Any],
    plan_units: list[dict[str, Any]],
    lesson_summary: str = "clinician innovator terminal fixes",
    research_entries: list[dict[str, Any]] | None = None,
    corpus_path: str = "course-content/courses/fixture-lesson",
) -> None:
    """Write a valid ``run.json`` with a controllable ``corpus_path`` (for Q2)."""
    trial_id = uuid.uuid4()
    envelope = ProductionEnvelope(trial_id=trial_id)
    envelope.add_contribution(
        SpecialistContribution.from_output(
            specialist_id="irene_pass1",
            output={
                "lesson_plan": {
                    "lesson_summary": lesson_summary,
                    "plan_units": plan_units,
                    "collateral": collateral,
                }
            },
            model_used="fixture-irene",
            node_id="03",
        )
    )
    if research_entries is not None:
        envelope.add_contribution(
            SpecialistContribution.from_output(
                specialist_id="research_wiring",
                output={"research_entries": research_entries},
                model_used="fixture-research",
                node_id="04.55",
            )
        )
    trial = ProductionTrialEnvelope(
        trial_id=trial_id,
        preset="production",
        corpus_path=corpus_path,
        operator_id="fixture-operator",
        started_at=datetime.now(UTC),
        status="in-flight",
        production_clone_launch_evidence=False,
        production_envelope=envelope,
    )
    (run_dir / "run.json").write_text(trial.model_dump_json(), encoding="utf-8")


def _make_run_dir(
    root: Path,
    *,
    collateral: dict[str, Any],
    plan_units: list[dict[str, Any]],
    enrichment_card: dict[str, Any] | None = None,
    research_entries: list[dict[str, Any]] | None = None,
    corpus_path: str = "course-content/courses/fixture-lesson",
    corpus_text: str = _CORPUS,
) -> Path:
    run_dir = root / "run"
    (run_dir / "exports").mkdir(parents=True, exist_ok=True)
    (run_dir / "bundle").mkdir(parents=True, exist_ok=True)
    (run_dir / "exports" / "segment-manifest-storyboard-b.yaml").write_text(
        yaml.safe_dump({"segments": _SEGMENTS}, sort_keys=False), encoding="utf-8"
    )
    (run_dir / "bundle" / "extracted.md").write_text(corpus_text, encoding="utf-8")
    if enrichment_card is not None:
        (run_dir / "g0-enrichment.json").write_text(
            json.dumps(enrichment_card), encoding="utf-8"
        )
    _write_run_json(
        run_dir,
        collateral=collateral,
        plan_units=plan_units,
        research_entries=research_entries,
        corpus_path=corpus_path,
    )
    return run_dir


# --------------------------------------------------------------------------- #
# Q1 — LO-id namespace bridge (uNN <-> lo-g0-NNN)                              #
# --------------------------------------------------------------------------- #

_Q1_CARD = {
    "provisional_los": [
        {
            "objective_id": "lo-g0-006",
            "statement": "Q1-ENRICHED-SENTINEL analyze the structural shift",
            "source_refs": [{"source_id": "src-006"}],
        }
    ],
    "typed_components": [],
    "pedagogy_annotations": [],
    "citation_resolutions": [],
}
_Q1_PLAN_UNITS = [
    {
        "unit_id": "u01",
        "cluster_role": "head",
        "source_refs": [
            "# Slide 1: The Economic & Structural Reality",
            "- **Visual Format:** Dual-Axis chart. [evidence: src-006]",
        ],
    }
]
_Q1_COLLATERAL = collateral_present(
    [
        section(
            "sec-u01",
            "u01",
            title="Reading the structural shift",
            deferred_depth="Read-channel derivation of the structural-shift objective.",
            narrative_intent="The fuller structural-shift narrative for the reader.",
        )
    ]
)


def test_q1_unit_bound_section_resolves_enrichment_overlay(tmp_path: Path) -> None:
    """A ``uNN``-bound collateral section resolves the ``lo-g0-NNN`` overlay LO.

    RED-first: without the ``[evidence: src-NNN]`` bridge, ``overlay_lo.get("u01")``
    is None and the LO silently degrades to the placeholder.
    """
    run_dir = _make_run_dir(
        tmp_path, collateral=_Q1_COLLATERAL, plan_units=_Q1_PLAN_UNITS, enrichment_card=_Q1_CARD
    )
    inputs = wb_act.build_workbook_inputs(run_dir, run_id="q1test")
    assert inputs is not None
    lo = next(o for o in inputs.learning_objectives if o.objective_id == "u01")
    # Re-keyed onto the bound uNN objective (so the S1 binding assertion holds)
    # while carrying the enrichment statement.
    assert lo.objective_id == "u01"
    assert "Q1-ENRICHED-SENTINEL" in lo.statement
    assert "objective statement unresolved" not in lo.statement
    # No loss recorded when every bound objective resolves.
    assert inputs.lo_overlay_loss is None


def test_q1_unbridgeable_objective_records_visible_loss(tmp_path: Path) -> None:
    """An objective with no overlay bridge records a VISIBLE loss (not silent).

    RED-first: the old path degraded to the placeholder with no recorded count.
    """
    plan_units = [{"unit_id": "u01", "cluster_role": "head", "source_refs": ["no evidence tag"]}]
    run_dir = _make_run_dir(
        tmp_path, collateral=_Q1_COLLATERAL, plan_units=plan_units, enrichment_card=_Q1_CARD
    )
    inputs = wb_act.build_workbook_inputs(run_dir, run_id="q1loss")
    assert inputs is not None
    assert inputs.lo_overlay_loss is not None
    assert inputs.lo_overlay_loss["unresolved_count"] == 1
    assert "u01" in inputs.lo_overlay_loss["unresolved_objectives"]


# --------------------------------------------------------------------------- #
# B5 — research-leg numerals declared as G1 supplements                       #
# --------------------------------------------------------------------------- #

_B5_RESEARCH = [
    {
        "citation_id": "rc-1",
        "source_ref": "scite:10.1234/example.doi",
        "provider": "scite",
        "source_id": "10.1234/example.doi",
        "title": "A cited study reporting $7 billion in avoidable spend",
        "source_hash": "cafebabecafebabe",
    }
]


def test_b5_research_numeral_declared_as_supplement_passes_g1(tmp_path: Path) -> None:
    """A research-leg numeral (``$7 billion``) not in corpus clears G1 as a supplement.

    RED-first: producing WITHOUT ``research_supplements`` fails G1 (the numeral is
    ``unsourced_numeric``); the fix threads the declared supplements so it passes.
    """
    # Corpus carries an in-source numeral (25%) so the audit's zero-denominator
    # guard does not fire and per-token classification actually runs; the research
    # entry's ``$7 billion`` is the token that must be cleared via the supplement.
    run_dir = _make_run_dir(
        tmp_path,
        collateral=_Q1_COLLATERAL,
        plan_units=_Q1_PLAN_UNITS,
        enrichment_card=_Q1_CARD,
        research_entries=_B5_RESEARCH,
        corpus_text="Administrative waste is roughly 25% of total spend.\n",
    )
    inputs = wb_act.build_workbook_inputs(run_dir, run_id="b5test")
    assert inputs is not None
    # The research numeral is declared as a supplement.
    assert any("money-trillion" in tok for tok in inputs.research_supplements)

    producer = WorkbookProducer(output_root=str(run_dir / "exports" / "workbooks"))

    def _produce(*, research_supplements: set[str] | None) -> Any:
        return producer.produce(
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
            research_omitted_note=inputs.research_omitted_note,
            glossary_articles=inputs.glossary_articles,
            glossary_empty_reason=inputs.glossary_empty_reason,
            research_trends=inputs.research_trends,
            research_supplements=research_supplements,
        )

    # Undeclared -> G1 fails (proves the coupling is real).
    with pytest.raises(WorkbookFidelityError, match="unsourced"):
        _produce(research_supplements=None)
    # Declared (as the fix threads it) -> G1 passes.
    sidecar = _produce(research_supplements=inputs.research_supplements)
    assert sidecar.numeric_audit["buckets"]["unsourced_numeric"]["count"] == 0


# --------------------------------------------------------------------------- #
# B6 — trial-scoped deliverable path                                          #
# --------------------------------------------------------------------------- #


def test_b6_default_output_is_trial_scoped(tmp_path: Path) -> None:
    """With no override, the deliverable lands under ``<run_dir>/exports``.

    RED-first: the old default wrote to the shared, non-trial
    ``_bmad-output/artifacts/workbooks`` root (unbindable by the run inventory).
    Uses an in-repo run dir so the repo-containment check holds.
    """
    run_root = (
        REPO_ROOT
        / "_bmad-output"
        / "artifacts"
        / "workbooks-test-s7"
        / f"_b6-{uuid.uuid4().hex}"
    )
    run_dir = _make_run_dir(
        run_root, collateral=_Q1_COLLATERAL, plan_units=_Q1_PLAN_UNITS, enrichment_card=_Q1_CARD
    )
    try:
        from app.models.state.cache_state import CacheState
        from app.models.state.model_resolution_entry import ModelResolutionEntry
        from app.models.state.run_state import RunState

        entry = ModelResolutionEntry(
            level="per_specialist",
            requested="gpt-5-nano",
            resolved="gpt-5-nano",
            reason="seed",
            timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        )
        state = RunState(
            graph_version="v0.1-stub",
            temperature=0.0,
            model_resolution_trail=[entry],
            cache_state=CacheState(
                cache_prefix=json.dumps({"run_dir": str(run_dir)}), entries_count=0
            ),
        )
        # No output_root override in the payload -> trial-scoped default.
        sidecar = wb_act.produce_workbook(state, {"run_dir": str(run_dir)})
        assert sidecar is not None
        rel = sidecar.markdown_path.replace("\\", "/")
        assert "/exports/workbooks/" in rel
        assert rel.startswith((run_dir / "exports" / "workbooks").relative_to(REPO_ROOT).as_posix())
        assert "_bmad-output/artifacts/workbooks/" not in rel
    finally:
        shutil.rmtree(run_root, ignore_errors=True)


# --------------------------------------------------------------------------- #
# B8 — DOCX byte-determinism                                                   #
# --------------------------------------------------------------------------- #


def test_b8_docx_render_is_byte_deterministic(tmp_path: Path) -> None:
    """Two renders of the SAME composed model produce byte-identical DOCX.

    RED-first: python-docx stamps wall-clock into the OPC zip members + core
    properties, so the old render differed byte-for-byte between runs.
    """
    doc = _ComposedDoc(title="Determinism Probe")
    doc.blocks.append((2, "Overview", "A short deterministic body line."))
    doc.blocks.append((2, "Learning Objectives", "- `obj-1` deterministic objective"))

    a = tmp_path / "a.docx"
    b = tmp_path / "b.docx"
    render_docx_from_model(doc, a)
    render_docx_from_model(doc, b)
    assert a.read_bytes() == b.read_bytes()


# --------------------------------------------------------------------------- #
# Q2 — corpus-native references populate the S6 References channel            #
# --------------------------------------------------------------------------- #


def _write_tiny_corpus(root: Path) -> Path:
    corpus = root / "corpus"
    (corpus / "references").mkdir(parents=True, exist_ok=True)
    (corpus / "slides").mkdir(parents=True, exist_ok=True)
    (corpus / "references" / "intro-video-youtube.md").write_text(
        "# Multimedia Integration: Video\n\n"
        "- Format: [https://www.youtube.com/watch?v=EXAMPLE](https://www.youtube.com/watch?v=EXAMPLE)\n",
        encoding="utf-8",
    )
    (corpus / "slides" / "slide-1.md").write_text(
        "# Slide 1\n\n"
        "Body prose here.\n\n"
        "**References:** CMS NHE Fact Sheet; American Medical Association Report. "
        "[evidence: src-006]\n",
        encoding="utf-8",
    )
    return corpus


def test_q2_corpus_native_references_projected(tmp_path: Path) -> None:
    """references/*.md + per-slide ``**References:**`` yield further-reading entries.

    RED-first: with empty ``citation_resolutions`` the in-graph References channel
    rendered EMPTY despite a references-bearing corpus.
    """
    corpus = _write_tiny_corpus(tmp_path)
    entries = corpus_native_further_reading(corpus)
    titles = {e.title for e in entries}
    # URL-bearing reference file.
    video = next(e for e in entries if e.title == "Multimedia Integration: Video")
    assert video.locator == "https://www.youtube.com/watch?v=EXAMPLE"
    # Name-only per-slide references (no fabricated URL).
    assert "CMS NHE Fact Sheet" in titles
    assert "American Medical Association Report" in titles
    cms = next(e for e in entries if e.title == "CMS NHE Fact Sheet")
    assert cms.locator is None
    # The [evidence: ...] tag is stripped from the rendered name.
    assert not any("evidence" in e.title for e in entries)


def test_q2_in_graph_references_populated_and_g2_consistent(tmp_path: Path) -> None:
    """The in-graph build folds corpus-native references into further-reading + G2.

    RED-first: the old build left further_reading empty on this run.
    """
    corpus = _write_tiny_corpus(tmp_path)
    run_dir = _make_run_dir(
        tmp_path,
        collateral=_Q1_COLLATERAL,
        plan_units=_Q1_PLAN_UNITS,
        enrichment_card=_Q1_CARD,
        corpus_path=str(corpus),
    )
    assert corpus_root_from_run(run_dir) == corpus
    inputs = wb_act.build_workbook_inputs(run_dir, run_id="q2test")
    assert inputs is not None
    assert inputs.further_reading, "corpus-native references must populate the channel"
    titles = {e.title for e in inputs.further_reading}
    assert "CMS NHE Fact Sheet" in titles
    # Every rendered reference resolves in the G2 manifest (no unsourced citation).
    for entry in inputs.further_reading:
        assert entry.source_ref in inputs.source_ref_manifest
        assert {"source_ref": entry.source_ref} in list(inputs.citations)


# --------------------------------------------------------------------------- #
# Terminal 07W emission fixes (frozen runs dfc372b7 / 503e54c1)               #
# --------------------------------------------------------------------------- #


def _write_run_json_with_contributions(
    run_dir: Path, contributions: list[SpecialistContribution]
) -> None:
    """Write a valid ``run.json`` carrying arbitrary envelope contributions."""
    trial_id = uuid.uuid4()
    envelope = ProductionEnvelope(trial_id=trial_id)
    for contribution in contributions:
        envelope.add_contribution(contribution)
    trial = ProductionTrialEnvelope(
        trial_id=trial_id,
        preset="production",
        corpus_path="course-content/courses/fixture-lesson",
        operator_id="fixture-operator",
        started_at=datetime.now(UTC),
        status="in-flight",
        production_clone_launch_evidence=False,
        production_envelope=envelope,
    )
    (run_dir / "run.json").write_text(trial.model_dump_json(), encoding="utf-8")


def _state_without_envelope() -> Any:
    """A RunState with ``production_envelope`` NULLED (as the dispatch adapter hands it)."""
    from app.models.state.model_resolution_entry import ModelResolutionEntry
    from app.models.state.run_state import RunState

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
        production_envelope=None,
    )


def _run_produce(
    producer: WorkbookProducer, inputs: Any, *, research_supplements: Any = ...
) -> Any:
    """Drive ``produce()`` from a built ``WorkbookInputs`` (forwarding every field)."""
    return producer.produce(
        inputs.plan_unit,
        inputs.context,
        workbook_title=inputs.workbook_title,
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
        research_omitted_note=inputs.research_omitted_note,
        glossary_articles=inputs.glossary_articles,
        glossary_empty_reason=inputs.glossary_empty_reason,
        research_trends=inputs.research_trends,
        research_supplements=(
            inputs.research_supplements if research_supplements is ... else research_supplements
        ),
    )


# --- Fix 1: production_envelope threading (the 07W blocker) ------------------ #


def test_fix1_loader_reads_persisted_envelope(tmp_path: Path) -> None:
    """``_load_persisted_production_envelope`` re-reads the envelope from run.json.

    Guarded: absent / symlinked run.json returns None (clean degrade).
    """
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    _write_run_json(run_dir, collateral=_Q1_COLLATERAL, plan_units=_Q1_PLAN_UNITS)
    envelope = wb_act._load_persisted_production_envelope(run_dir)
    assert envelope is not None
    assert any(c.specialist_id == "irene_pass1" for c in envelope.contributions)
    # Absent run.json → None (never a fabricated authority).
    assert wb_act._load_persisted_production_envelope(tmp_path / "missing") is None


def test_fix1_reconcile_consults_persisted_envelope_when_state_null(tmp_path: Path) -> None:
    """With ``state.production_envelope`` NULLED, the reconcile loads run.json.

    RED-first: the old path saw ``envelope is None`` and (no sidecar) returned
    ``None`` WITHOUT ever consulting the persisted authority — so on a real run
    with a brief sidecar it error-paused ``authority-missing`` at 07W. The fix
    loads the persisted envelope and runs the collision logic against it: a
    ``workbook_brief`` contribution pinned to the WRONG node_id is a collision
    that can ONLY be detected by reading run.json, proving the seam is wired.
    """
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    _write_run_json_with_contributions(
        run_dir,
        [
            SpecialistContribution.from_output(
                specialist_id="workbook_brief",
                output={},
                model_used="fixture",
                node_id="99",  # NOT 07W.1 → a coordinate collision
            )
        ],
    )
    state = _state_without_envelope()
    with pytest.raises(wb_act.WorkbookProducerActError) as excinfo:
        wb_act._reconcile_workbook_brief_authority(state, run_dir)
    assert excinfo.value.tag == "workbook-brief.sidecar-mismatch"


def test_fix1_reconcile_null_envelope_no_authority_returns_none(tmp_path: Path) -> None:
    """A run.json with no brief authority + no sidecar still returns None (no false raise)."""
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    _write_run_json(run_dir, collateral=_Q1_COLLATERAL, plan_units=_Q1_PLAN_UNITS)
    state = _state_without_envelope()
    assert wb_act._reconcile_workbook_brief_authority(state, run_dir) is None


# --- Fix 2: G1 numeric-fidelity hardening on authored pedagogy prose --------- #

_FIX2_COLLATERAL = collateral_present(
    [
        section(
            "sec-u01",
            "u01",
            title="Reading the structural shift",
            deferred_depth="Read-channel derivation of the structural-shift objective.",
            # An AUTHORED pedagogy numeral (not in corpus/narration).
            narrative_intent="The cited intervention reduces clinician burnout by 88% in cohort.",
        )
    ]
)


def test_fix2_authored_prose_numeral_declared_as_supplement(tmp_path: Path) -> None:
    """A numeral authored into collateral prose (``88%``) clears G1 as a supplement.

    RED-first: producing with the pre-fix (research-only) supplement set leaves the
    authored ``88%`` ``unsourced_numeric`` → ``WorkbookFidelityError`` hard-pause.
    The fix declares authored-prose figures as G1 supplements so it passes.
    """
    run_dir = _make_run_dir(
        tmp_path,
        collateral=_FIX2_COLLATERAL,
        plan_units=_Q1_PLAN_UNITS,
        enrichment_card=_Q1_CARD,
        # In-source numeral so the audit's zero-denominator guard does not fire.
        corpus_text="Administrative waste is roughly 25% of total spend.\n",
    )
    inputs = wb_act.build_workbook_inputs(run_dir, run_id="fix2")
    assert inputs is not None
    # The authored numeral is now declared as a supplement.
    assert "percent:88" in inputs.research_supplements

    producer = WorkbookProducer(output_root=str(run_dir / "exports" / "workbooks"))
    # RED: the pre-fix set (research figures only) does NOT clear the authored 88%.
    research_only = wb_act._research_figure_supplements(
        inputs.research_entries,
        inputs.further_reading,
        inputs.glossary_articles,
        inputs.research_trends,
    )
    assert "percent:88" not in research_only
    with pytest.raises(WorkbookFidelityError, match="unsourced"):
        _run_produce(producer, inputs, research_supplements=research_only)
    # GREEN: the fix's declared supplements clear it.
    sidecar = _run_produce(producer, inputs)
    assert sidecar.numeric_audit["buckets"]["unsourced_numeric"]["count"] == 0


# --- Fix 3: TRENDS-WRITER-REQUIRED marker leak ------------------------------ #


def test_fix3_trends_marker_not_rendered_but_field_retained() -> None:
    """The inline writer-required marker is stripped from rendered MD (and thus DOCX).

    RED-first: ``_render_docx_body`` only skips lines that START with ``<!--``, so
    the INLINE ``<!-- TRENDS-WRITER-REQUIRED -->`` in each hot-topic rationale
    leaked verbatim into the client MD + DOCX. The fix strips inline comment spans
    at render time while retaining the marker on the ``rationale`` field.
    """
    from app.marcus.lesson_plan.trends_projection import (
        TRENDS_WRITER_REQUIRED_MARKER,
        HotTopicCallout,
        ResearchTrendsBrief,
        render_trends_markdown,
    )

    topic = HotTopicCallout(
        topic="Physician leadership gap",
        rationale=(
            f"{TRENDS_WRITER_REQUIRED_MARKER} Bounded hot-topic callout grounded in "
            "`cite-1` (confidence=medium). Not a forecast."
        ),
        supporting_citation_ids=("cite-1",),
        source_refs=("retrieval:scite:10.1/x",),
        confidence="medium",
    )
    brief = ResearchTrendsBrief(
        trends=(), hot_topics=(topic,), known_losses=(), empty_reason=None
    )
    md = render_trends_markdown(brief)
    # The programmatic signal is retained on the FIELD…
    assert TRENDS_WRITER_REQUIRED_MARKER in topic.rationale
    # …but NEVER leaks into the client-facing rendered output.
    assert "TRENDS-WRITER-REQUIRED" not in md
    assert "<!--" not in md
    assert "Physician leadership gap" in md
    assert "Bounded hot-topic callout grounded in `cite-1`" in md


# --- Fix 4: human-readable H1/DOCX title (not the open-id slug) -------------- #


def test_fix4_display_title_human_readable_not_slug(tmp_path: Path) -> None:
    """The H1/DOCX title reads the un-slugged lesson summary, not the open-id slug.

    RED-first: the old title was ``event_type`` (an 80-char hyphenated open-id
    slug), producing "Workbook: this-lesson-builds-a-case-for-change-…".
    """
    long_summary = (
        "This lesson builds a case for change by moving from healthcare economic "
        "and structural reality to waste and burnout, then to accelerating knowledge"
    )
    run_dir = _make_run_dir(
        tmp_path, collateral=_Q1_COLLATERAL, plan_units=_Q1_PLAN_UNITS, enrichment_card=_Q1_CARD
    )
    _write_run_json(
        run_dir,
        collateral=_Q1_COLLATERAL,
        plan_units=_Q1_PLAN_UNITS,
        lesson_summary=long_summary,
    )
    inputs = wb_act.build_workbook_inputs(run_dir, run_id="fix4")
    assert inputs is not None
    # The display title is human-readable prose (un-slugged)…
    assert inputs.workbook_title.startswith("This lesson builds a case for change")
    # …while the open-id ``event_type`` stays the hyphenated slug (unchanged contract).
    assert inputs.plan_unit.event_type.startswith("this-lesson-builds")
    assert " " not in inputs.plan_unit.event_type

    producer = WorkbookProducer(output_root=str(run_dir / "exports" / "workbooks"))
    sidecar = _run_produce(producer, inputs)
    h1 = (REPO_ROOT / sidecar.markdown_path).read_text(encoding="utf-8").splitlines()[0]
    assert "This lesson builds a case for change" in h1
    # The hyphenated slug must NOT be the rendered title.
    assert inputs.plan_unit.event_type not in h1
