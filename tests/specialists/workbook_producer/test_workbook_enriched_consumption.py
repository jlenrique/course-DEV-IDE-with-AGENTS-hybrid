"""P5-S1 RED-first floors: the workbook producer CONSUMES the enriched corpus.

These close the P5 loop: the workbook producer must fill its pedagogically
meaningful slots (further-reading links, exercise Bloom levels, learning
objectives) from the frozen ``G0EnrichmentResult`` card payload — NOT from the
hardcoded constants (``_FURTHER_READING`` / ``_CH2_KC`` / ``_CH3_KC`` /
constant LO briefs).

RED-first discipline (anti-tautology): each behavioural test asserts an ENRICHED
value the constant producer cannot emit (an enriched exercise id ``src-001-c021``
never exists in the constant path; a sentinel URL/statement/Bloom is unique to the
mutated fixture). A test that passes against today's constants is testing the
constant, not the consumption — those are rejected here.

The committed live-enriched fixture is the substrate
(``tests/fixtures/p5_workbook_corpus/live_enriched_result_card.json``): the byte
judge is the resolved JAMA citation ``src-001-c007`` whose
``resolved_ref.access_url`` is ``https://doi.org/10.1001/jama.2019.13978``.

OFFLINE ONLY: no live LLM / network. The render path reads the frozen verdict.
"""

from __future__ import annotations

import copy
import json
import logging
import shutil
import uuid
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
import yaml

from app.marcus.lesson_plan.workbook_enrichment import (
    project_enrichment_to_workbook_inputs,
)
from app.marcus.lesson_plan.workbook_producer import WorkbookProducer
from app.specialists.workbook_producer import _act as wb_act

from ._run_fixture import collateral_present, section, write_run_json

# S7: the enrichment card is a RESOLUTION OVERLAY now (it no longer authors
# sections). Irene's collateral blueprint (on run.json) is the section/objective
# authority. This blueprint binds the objectives the overlay resolves against:
# lo-g0-006 (the home objective of the fixture quiz component src-001-c021 -> its
# overlay exercise attaches here) and lo-g0-001 (probed by the LO-provenance test).
# Depth-delta prose is numeral-free (so the G1 symbol-gate is a non-event) and
# distinct from the narration (so the AC-8 dual-coding superset holds).
_ENRICHED_COLLATERAL = collateral_present(
    [
        section(
            "sec-lo-g0-006",
            "lo-g0-006",
            title="Redesignable administrative surface",
            deferred_depth=(
                "The deferred systems-design derivation the glance deck gestures "
                "at but cannot carry: quantify redesignable administrative waste "
                "as a concrete intrapreneurial innovation target."
            ),
            narrative_intent="The fuller intrapreneurial reframe for objective six.",
        ),
        section(
            "sec-lo-g0-001",
            "lo-g0-001",
            title="The innovation mindset",
            deferred_depth=(
                "The read-channel companion depth for the innovation-mindset "
                "objective: falling in love with the problem rather than the "
                "solution before any diagnosis begins."
            ),
            narrative_intent="The fuller narrative for the innovation-mindset objective.",
        ),
    ]
)

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "p5_workbook_corpus"
    / "live_enriched_result_card.json"
)

# The byte-judge literal (live-resolved JAMA citation).
JAMA_URL = "https://doi.org/10.1001/jama.2019.13978"
JAMA_CITATION_ID = "src-001-c007"
QUIZ_COMPONENT_ID = "src-001-c021"
# 39.1b (D2 MERGE, intentional pin flip enumerated in the 39-1b dev diff):
# overlay exercise ids are ``g0-``-prefixed at the attach seam (collision
# guard D2-3), so the RENDERED id carries the prefix.
RENDERED_QUIZ_EXERCISE_ID = f"g0-{QUIZ_COMPONENT_ID}"

# Numeral-free segments / corpus so the G1 symbol-only numeric gate is a non-event
# (the enriched body asserts no $/%/x tokens; the gate has nothing to clear).
_SEGMENTS = [
    {
        "segment_id": "seg-01",
        "id": "seg-01",
        "slide_id": "slide-01",
        "narration_text": (
            "Healthcare delivery is shifting toward proactive, population-focused "
            "models and clinician leadership."
        ),
    },
    {
        "segment_id": "seg-02",
        "id": "seg-02",
        "slide_id": "slide-02",
        "narration_text": (
            "Administrative friction is a redesignable surface for innovation "
            "rather than an inevitability."
        ),
    },
]
_CORPUS = (
    "Healthcare delivery shifts toward proactive, population-focused models and "
    "clinician leadership; administrative friction is a redesignable surface.\n"
)


def _load_card() -> dict[str, Any]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _citation(card: dict[str, Any], component_id: str) -> dict[str, Any]:
    for cit in card["citation_resolutions"]:
        if cit["component_id"] == component_id:
            return cit
    raise KeyError(component_id)


def _annotation(card: dict[str, Any], component_id: str) -> dict[str, Any] | None:
    for ann in card["pedagogy_annotations"]:
        if ann["component_id"] == component_id:
            return ann
    return None


def _provisional_lo(card: dict[str, Any], objective_id: str) -> dict[str, Any]:
    for lo in card["provisional_los"]:
        if lo["objective_id"] == objective_id:
            return lo
    raise KeyError(objective_id)


def _add_annotation_for(card: dict[str, Any], component_id: str, *, teachable: bool) -> None:
    """Inject a P3 annotation for a component (used to gate a citation component)."""
    card["pedagogy_annotations"].append(
        {
            "component_id": component_id,
            "lo_refs": [],
            "bloom": "understand",
            "pedagogical_role": "definition",
            "teaches_after": [],
            "prerequisite_concepts": [],
            "assessment_link": None,
            "teachable": teachable,
            "rationale": f"injected teachable={teachable} for {component_id}",
            "transform_model": "marcus",
            "transform_version": "ped-v1",
            "generated_at": "2026-06-27T05:19:26.487412Z",
        }
    )


@pytest.fixture
def output_root() -> Iterator[Path]:
    target = (
        REPO_ROOT
        / "_bmad-output"
        / "artifacts"
        # Distinct parent from the shared ``workbooks-test`` dir the pre-existing
        # tejal producer tests write their fixed ``…@3.docx`` stem into (avoids
        # aggravating that pre-existing shared-output-root race).
        / "workbooks-test-s7"
        / f"_p5-{uuid.uuid4().hex}"
    )
    target.mkdir(parents=True, exist_ok=True)
    try:
        yield target
    finally:
        shutil.rmtree(target, ignore_errors=True)


def _make_run_dir(root: Path, card: dict[str, Any]) -> Path:
    run_dir = root / "run"
    (run_dir / "exports").mkdir(parents=True, exist_ok=True)
    (run_dir / "bundle").mkdir(parents=True, exist_ok=True)
    (run_dir / "exports" / "segment-manifest-storyboard-b.yaml").write_text(
        yaml.safe_dump({"segments": _SEGMENTS}, sort_keys=False), encoding="utf-8"
    )
    (run_dir / "bundle" / "extracted.md").write_text(_CORPUS, encoding="utf-8")
    (run_dir / "g0-enrichment.json").write_text(
        json.dumps(card), encoding="utf-8"
    )
    # S7: the collateral blueprint (run.json) is the section authority; the
    # enrichment card resolves exercises / further-reading / LO statements onto it.
    write_run_json(
        run_dir,
        collateral=_ENRICHED_COLLATERAL,
        plan_units=[{"unit_id": "u-innovation-mindset"}],
        lesson_summary="clinician innovator opportunity mindset",
    )
    return run_dir


def _render(run_dir: Path, output_root: Path) -> str:
    """Render the workbook through the real producer; return the canonical MD."""
    inputs = wb_act.build_workbook_inputs(run_dir, run_id="p5testrun01")
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
        diff_files=["app/marcus/lesson_plan/workbook_producer.py"],
        reuse_sha="p5test",
    )
    return (REPO_ROOT / sidecar.markdown_path).read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# T8 — projection reachability over the card-payload shape (07W on-disk shape)
# ---------------------------------------------------------------------------


def test_t8_projection_reachable_over_card_payload_shape() -> None:
    """T8: the projection works on the card payload as load_enrichment_card returns it.

    RED-first: the projection function did not exist before P5-S1 (ImportError).
    """
    card = _load_card()
    projection = project_enrichment_to_workbook_inputs(card)

    fr = {e.citation_id: e for e in projection.further_reading}
    # Exactly the ONE resolved citation projects an authoritative entry; the six
    # failed citations are omitted (never a fabricated bare URL).
    assert set(fr) == {JAMA_CITATION_ID}
    assert fr[JAMA_CITATION_ID].locator == JAMA_URL
    # The enriched quiz exercise carries the P3 Bloom.
    exercises = [ex for sec in projection.spec.sections for ex in sec.exercises]
    assert any(
        ex.exercise_id == QUIZ_COMPONENT_ID and ex.bloom_level == "analyze"
        for ex in exercises
    )
    # Every projected citation resolves in the G2 manifest.
    assert all(c["source_ref"] in projection.source_ref_manifest for c in projection.citations)


# ---------------------------------------------------------------------------
# T1 — substitution anti-tautology (enriched values, not constants)
# ---------------------------------------------------------------------------


def test_t1_enriched_values_displace_constants(tmp_path: Path, output_root: Path) -> None:
    """T1: enriched URL / Bloom / LO text render; the constants do NOT.

    RED-first: against the constant producer the sentinels are absent and the
    constant exercise/url/LO are present — the inverse of every assertion here.
    """
    sentinel_url = "https://doi.org/10.5555/p5-enriched-anti-tautology"
    sentinel_lo = "ENRICHED-LO-SENTINEL quantify redesignable administrative waste"

    card = _load_card()
    _citation(card, JAMA_CITATION_ID)["resolved_ref"]["access_url"] = sentinel_url
    _provisional_lo(card, "lo-g0-006")["statement"] = sentinel_lo
    _annotation(card, QUIZ_COMPONENT_ID)["bloom"] = "create"

    md = _render(_make_run_dir(tmp_path, card), output_root)

    # Enriched values present.
    assert sentinel_url in md
    assert sentinel_lo in md
    assert "Bloom level: **create**" in md
    assert f"Exercise `{RENDERED_QUIZ_EXERCISE_ID}`" in md

    # Constants ABSENT (the proof the enriched corpus displaced them).
    assert "nhe-fact-sheet" not in md  # constant CMS further-reading URL
    assert "ex-ch2-q1" not in md  # constant knowledge-check exercise id
    assert "obj-lo2-analyze-trends" not in md  # constant LO id


# ---------------------------------------------------------------------------
# T2 — byte-exact citation URL (independently RED-able)
# ---------------------------------------------------------------------------


def test_t2_byte_exact_citation_url(tmp_path: Path, output_root: Path) -> None:
    """T2: rendered further-reading URL == citation resolved_ref.access_url, verbatim.

    A unique sentinel URL (distinct from every constant) makes this independently
    RED-able and proves the byte is read off the citation, not reconstructed.
    """
    sentinel_url = "https://doi.org/10.4242/p5-byte-exact-probe-7"
    card = _load_card()
    _citation(card, JAMA_CITATION_ID)["resolved_ref"]["access_url"] = sentinel_url

    md = _render(_make_run_dir(tmp_path, card), output_root)

    # The exact markdown link target is the verbatim access_url.
    assert f"]({sentinel_url})" in md
    # The constant JAMA URL must NOT leak in (proves no constant fallback).
    assert JAMA_URL not in md


def test_t2_byte_exact_uses_fixture_literal(tmp_path: Path, output_root: Path) -> None:
    """T2 (literal): the unmutated fixture renders the live JAMA access_url verbatim."""
    md = _render(_make_run_dir(tmp_path, _load_card()), output_root)
    assert f"]({JAMA_URL})" in md


# ---------------------------------------------------------------------------
# T3 — byte-exact Bloom (independently RED-able from T2)
# ---------------------------------------------------------------------------


def test_t3_byte_exact_exercise_bloom(tmp_path: Path, output_root: Path) -> None:
    """T3: rendered exercise Bloom == pedagogy_annotations[quiz].bloom; flip → flips.

    Independent of T2 (no citation mutation). RED-first: the constant path has no
    ``src-001-c021`` exercise at all.
    """
    card = _load_card()
    _annotation(card, QUIZ_COMPONENT_ID)["bloom"] = "evaluate"

    md = _render(_make_run_dir(tmp_path, card), output_root)

    assert f"Exercise `{RENDERED_QUIZ_EXERCISE_ID}`" in md
    assert "Bloom level: **evaluate**" in md
    # The original fixture Bloom must not survive the flip.
    assert "Bloom level: **analyze**" not in md


# ---------------------------------------------------------------------------
# T4 — learning-objective line provenance
# ---------------------------------------------------------------------------


def test_t4_lo_line_provenance(tmp_path: Path, output_root: Path) -> None:
    """T4: mutate a provisional LO statement → the workbook LO line changes."""
    sentinel = "MUTATED-LO-STATEMENT define the innovation mindset sentinel"
    card = _load_card()
    _provisional_lo(card, "lo-g0-001")["statement"] = sentinel

    md = _render(_make_run_dir(tmp_path, card), output_root)
    assert sentinel in md


# ---------------------------------------------------------------------------
# T5 — injected-fault resolution_status gate (leak-bait: access_url left populated)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("bad_status", ["failed", "ungrounded"])
def test_t5_resolution_status_gate_suppresses_url(
    tmp_path: Path, output_root: Path, bad_status: str
) -> None:
    """T5: a non-resolved citation never renders an authoritative URL.

    Leak-bait: ``resolution_status`` is flipped to failed/ungrounded but the
    ``access_url`` is LEFT populated; the render gate must still drop the URL.
    RED-first: the constant producer always carries the JAMA URL.
    """
    card = _load_card()
    cit = _citation(card, JAMA_CITATION_ID)
    cit["resolution_status"] = bad_status  # access_url intentionally left in place

    md = _render(_make_run_dir(tmp_path, card), output_root)

    assert JAMA_URL not in md  # no link, no bare URL


# ---------------------------------------------------------------------------
# T6 — injected-fault teachable render-gate (both directions mandatory)
# ---------------------------------------------------------------------------


def test_t6_teachable_gate_suppresses_exercise(tmp_path: Path, output_root: Path) -> None:
    """T6 (False): a non-teachable quiz renders NO exercise."""
    card = _load_card()
    _annotation(card, QUIZ_COMPONENT_ID)["teachable"] = False

    md = _render(_make_run_dir(tmp_path, card), output_root)
    assert f"Exercise `{RENDERED_QUIZ_EXERCISE_ID}`" not in md


def test_t6_teachable_gate_reappears_when_true(tmp_path: Path, output_root: Path) -> None:
    """T6 (True): a teachable quiz reappears as a rendered exercise.

    RED-first: the constant producer has no ``src-001-c021`` exercise to render.
    """
    md = _render(_make_run_dir(tmp_path, _load_card()), output_root)
    assert f"Exercise `{RENDERED_QUIZ_EXERCISE_ID}`" in md
    assert "Bloom level: **analyze**" in md


# ---------------------------------------------------------------------------
# T6b — coherence-breach alarm (resolved citation on a teachable==False component)
# ---------------------------------------------------------------------------


def test_t6b_coherence_breach_alarms_and_suppresses(
    tmp_path: Path, output_root: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """T6b: a resolved+linkable citation on a teachable==False component is
    SUPPRESSED and a hard diagnostic is emitted (defense-in-depth; never silent)."""
    card = _load_card()
    # The JAMA citation stays resolved with its access_url; we hang a teachable=False
    # annotation on its component — the coherence breach.
    _add_annotation_for(card, JAMA_CITATION_ID, teachable=False)

    with caplog.at_level(logging.ERROR, logger="app.marcus.lesson_plan.workbook_enrichment"):
        md = _render(_make_run_dir(tmp_path, card), output_root)

    # Hard diagnostic emitted.
    assert any(
        "coherence breach" in rec.getMessage().lower()
        and JAMA_CITATION_ID in rec.getMessage()
        for rec in caplog.records
    )
    # AND the authoritative URL suppressed.
    assert JAMA_URL not in md


def test_t6b_projection_breach_is_byte_observable() -> None:
    """T6b (projection): the breach drops the entry from the projection too."""
    card = _load_card()
    _add_annotation_for(card, JAMA_CITATION_ID, teachable=False)
    projection = project_enrichment_to_workbook_inputs(card)
    assert all(e.citation_id != JAMA_CITATION_ID for e in projection.further_reading)


# ---------------------------------------------------------------------------
# T7 — no re-derivation (zero retrieval/network/model calls; READ-ONLY)
# ---------------------------------------------------------------------------


def test_t7_no_model_or_network_re_derivation(
    tmp_path: Path, output_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """T7: rendering the enriched workbook instantiates NO model client and opens
    NO network connection — it reads the frozen verdict (P5-RO)."""

    def _boom_model(*args: Any, **kwargs: Any) -> Any:  # pragma: no cover - must not fire
        raise AssertionError("P5-RO violated: a model client was constructed")

    def _boom_net(*args: Any, **kwargs: Any) -> Any:  # pragma: no cover - must not fire
        raise AssertionError("P5-RO violated: a network client was constructed")

    monkeypatch.setattr("app.models.adapter.make_chat_model", _boom_model)
    # OpenAI SDK constructor (best-effort; guarded if the SDK is absent).
    try:  # pragma: no cover - import availability varies
        import openai

        monkeypatch.setattr(openai, "OpenAI", _boom_model, raising=False)
    except ImportError:
        pass
    # Retrieval/scite network entry points.
    import httpx

    monkeypatch.setattr(httpx, "Client", _boom_net, raising=False)
    monkeypatch.setattr(httpx, "AsyncClient", _boom_net, raising=False)

    md = _render(_make_run_dir(tmp_path, _load_card()), output_root)
    # The render still produced an enriched artifact (so the no-call assertion is
    # over a real render, not a short-circuit).
    assert f"]({JAMA_URL})" in md


def test_t7_projection_is_pure_offline() -> None:
    """T7 (projection): the projection itself touches no model/network."""
    card = _load_card()
    # A second projection of a deep copy is byte-identical on the load-bearing
    # fields — deterministic, no external state.
    a = project_enrichment_to_workbook_inputs(card)
    b = project_enrichment_to_workbook_inputs(copy.deepcopy(card))
    assert [e.locator for e in a.further_reading] == [e.locator for e in b.further_reading]
    assert a.source_ref_manifest == b.source_ref_manifest
