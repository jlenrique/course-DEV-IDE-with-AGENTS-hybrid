"""T4 — coverage segmentation + derived-first intent pass (OFFLINE).

Mirrors the P3 test split: the deterministic OFFLINE pass + the live PARSE/BUILD
helpers exercised against a CANNED gpt-5 response fixture. NO live LLM/network — the
real gpt-5 segmentation is the orchestrator's job (T8). The model only cuts spans;
risk flags + intents are asserted DETERMINISTIC (AC5/AC7).
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.marcus.lesson_plan.coverage_annotation import (
    COVERAGE_LIVE_MODEL,
    COVERAGE_OFFLINE_MODEL,
    MAX_ASSERTIONS_PER_BLOCK,
    CoverageAnnotation,
    build_coverage_annotations,
    build_coverage_from_rows,
    detect_risk_flags,
    extract_coverage_rows,
    load_coverage_annotation,
)
from app.marcus.lesson_plan.source_point import SourcePoint

_REPO_ROOT = Path(__file__).resolve().parents[3]
_FIXTURE = _REPO_ROOT / "tests" / "fixtures" / "coverage" / "live_segmentation_response.json"
_TS = datetime(2026, 6, 30, 12, 0, 0, tzinfo=UTC)

_NOTES_1 = (
    "U.S. healthcare spending reached $5.2 trillion in 2024. "
    "Independent practice fell drastically while hospital employment surged. "
    "You cannot just optimize your own clinic."
)


def _narration_rec(cid: str = "src-001-c001", notes: str = _NOTES_1, **extra) -> dict:
    rec = {
        "component_id": cid, "type": "narration",
        "locator": "Module 1 > Slide 1", "excerpt": notes,
    }
    rec.update(extra)
    return rec


# --------------------------------------------------------------------------- #
# Deterministic risk detection (AC5)
# --------------------------------------------------------------------------- #


def test_detect_numeric_and_dosing() -> None:
    assert "numeric" in detect_risk_flags("reached $5.2 trillion in 2024")
    assert set(detect_risk_flags("administer 5 mg daily")) >= {"numeric", "dosing"}


def test_detect_negation_and_comparator() -> None:
    assert "negation" in detect_risk_flags("this is not a personal failing")
    assert "comparator" in detect_risk_flags("burden increased more than before")


def test_detect_exemplary_and_clinical_gated() -> None:
    assert "exemplary_language" in detect_risk_flags("such as sepsis")
    # clinical_claim only when a lexicon is injected (deferred ontology leg)
    assert "clinical_claim" not in detect_risk_flags("sepsis is dangerous")
    assert "clinical_claim" in detect_risk_flags(
        "sepsis is dangerous", clinical_terms=frozenset({"sepsis"})
    )


# --------------------------------------------------------------------------- #
# Offline pass (AC2/AC3 — assertion unit + derived intents)
# --------------------------------------------------------------------------- #


def test_offline_pass_segments_only_narration() -> None:
    comps = [
        _narration_rec(),
        {"component_id": "src-001-c009", "type": "slide", "locator": "Slide 1", "excerpt": "x. y."},
    ]
    anns = build_coverage_annotations(comps, generated_at=_TS)
    assert len(anns) == 1
    ann = anns[0]
    assert ann.component_id == "src-001-c001"
    assert ann.transform_model == COVERAGE_OFFLINE_MODEL
    assert ann.segmentation == "assertion_level"
    assert ann.is_v1_shippable()
    # three sentences → three source points, ordinals 1..3
    assert [sp.ordinal for sp in ann.source_points] == [1, 2, 3]
    assert all(isinstance(sp, SourcePoint) for sp in ann.source_points)


def test_offline_points_carry_derived_risk_and_verbatim_floor() -> None:
    ann = build_coverage_annotations([_narration_rec()], generated_at=_TS)[0]
    first = ann.source_points[0]
    assert "numeric" in first.risk_flags  # "$5.2 trillion ... 2024"
    assert first.verbatim_required is True  # numeric → floor
    # the verbatim span is preserved (identity keys on the span, not a paraphrase)
    assert "5.2 trillion" in first.verbatim_text


def test_offline_intents_force_both_when_lo_load_bearing() -> None:
    ann = build_coverage_annotations(
        [_narration_rec(lo_refs=["lo-g0-001"])], generated_at=_TS
    )[0]
    # LO-load-bearing → BOTH surfaces on every point
    for sp in ann.source_points:
        assert set(sp.coverage_intents) == {"gist_on_slide", "detail_in_narration"}


def test_offline_pass_byte_stable_across_runs() -> None:
    a = build_coverage_annotations([_narration_rec()], generated_at=_TS)
    b = build_coverage_annotations([_narration_rec()], generated_at=_TS)
    assert [x.model_dump(mode="json") for x in a] == [y.model_dump(mode="json") for y in b]


# --------------------------------------------------------------------------- #
# Live PARSE/BUILD via canned fixture (AC-OP2 offline-tested; no live call)
# --------------------------------------------------------------------------- #


def test_extract_rows_from_canned_fixture() -> None:
    content = _FIXTURE.read_text(encoding="utf-8")
    rows = extract_coverage_rows(content)
    assert [r["component_id"] for r in rows] == ["src-001-c001", "src-001-c002"]


def test_extract_rows_tolerates_fences_and_prose() -> None:
    body = "Here you go:\n```json\n" + _FIXTURE.read_text(encoding="utf-8") + "\n```\nDone."
    rows = extract_coverage_rows(body)
    assert len(rows) == 2


def test_extract_rows_degrades_on_garbage() -> None:
    assert extract_coverage_rows("not json at all") == []
    assert extract_coverage_rows("") == []


def test_build_from_rows_assigns_deterministic_risk_and_live_model() -> None:
    rows = json.loads(_FIXTURE.read_text(encoding="utf-8"))["blocks"]
    components = [_narration_rec("src-001-c001"), _narration_rec("src-001-c002", notes="ignored")]
    anns = build_coverage_from_rows(rows, components, generated_at=_TS, clinical_terms=None)
    by_id = {a.component_id: a for a in anns}
    assert set(by_id) == {"src-001-c001", "src-001-c002"}
    assert by_id["src-001-c001"].transform_model == COVERAGE_LIVE_MODEL
    # the negation assertion in c002 carries a negation risk + verbatim floor
    neg_point = by_id["src-001-c002"].source_points[0]
    assert "negation" in neg_point.risk_flags
    assert neg_point.verbatim_required is True


def test_build_from_rows_clamps_over_segmentation() -> None:
    over = [{"component_id": "src-001-c001", "assertions": [f"s{i}." for i in range(30)]}]
    anns = build_coverage_from_rows(
        over, [_narration_rec("src-001-c001")], generated_at=_TS, clinical_terms=None
    )
    assert len(anns[0].source_points) == MAX_ASSERTIONS_PER_BLOCK


def test_build_from_rows_skips_unknown_component() -> None:
    rows = [{"component_id": "ghost", "assertions": ["a."]}]
    out = build_coverage_from_rows(
        rows, [_narration_rec("src-001-c001")], generated_at=_TS, clinical_terms=None
    )
    assert out == ()


# --------------------------------------------------------------------------- #
# Model invariants (Irene caveat: segmentation stamp load-bearing)
# --------------------------------------------------------------------------- #


def test_annotation_rejects_foreign_source_point() -> None:
    foreign = SourcePoint(
        source_point_id="other#1", component_id="other", ordinal=1, slide_key="Slide 1",
        verbatim_text="x", coverage_intents=("gist_on_slide",), segmentation="assertion_level",
    )
    with pytest.raises(ValidationError, match="join-key integrity"):
        CoverageAnnotation(
            component_id="src-001-c001", slide_key="Slide 1",
            source_points=(foreign,), segmentation="assertion_level",
        )


def test_annotation_rejects_segmentation_grain_mismatch() -> None:
    point = SourcePoint(
        source_point_id="src-001-c001#1", component_id="src-001-c001", ordinal=1,
        slide_key="Slide 1", verbatim_text="x", coverage_intents=("gist_on_slide",),
        segmentation="assertion_level",
    )
    with pytest.raises(ValidationError, match="load-bearing"):
        CoverageAnnotation(
            component_id="src-001-c001", slide_key="Slide 1",
            source_points=(point,), segmentation="block_level_v1",
        )


def test_annotation_round_trip_load() -> None:
    ann = build_coverage_annotations([_narration_rec()], generated_at=_TS)[0]
    assert load_coverage_annotation(ann.model_dump(mode="json")) == ann
