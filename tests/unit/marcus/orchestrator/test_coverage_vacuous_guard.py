"""MF1+MF2+SF2 — the VACUOUS-RECEIPT GUARD wired into the runtime gate.

The headline false-PASS hole: ``CoverageReceipt.is_vacuous()`` / ``joined_row_count()``
existed but were NEVER consulted by the runtime gate, so a run with real authored
notes but a broken/empty bridge (every row ``missing``, or zero rows when the pass
silently didn't run) PASSED to ElevenLabs whenever no point happened to be
``must_cover``. These cases pin the fail-loud guard at
``enforce_coverage_gate_before_audio`` for BOTH the vacuous-with-content and the
empty-when-content-exists vectors, while NEVER blocking the legitimately-empty case
(no note-bearing content) or an all-``deliberately_excluded`` receipt (SF2).

OFFLINE — no live LLM/network.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.marcus.lesson_plan.coverage_annotation import CoverageAnnotation
from app.marcus.lesson_plan.coverage_gate import CoverageAssuranceError
from app.marcus.lesson_plan.coverage_receipt import (
    AnchorResolution,
    derive_coverage_receipt,
)
from app.marcus.lesson_plan.source_point import SourcePoint
from app.marcus.orchestrator import coverage_gate_wiring as cgw

_TS = datetime(2026, 6, 30, 12, 0, 0, tzinfo=UTC)


def _point(
    *,
    component_id: str = "src-001-c001",
    slide_key: str = "Slide 1",
    text: str = "healthcare is consolidating rapidly",
    risk_flags=(),
    intents=("gist_on_slide",),
    operator_signed: bool = False,
) -> SourcePoint:
    return SourcePoint(
        source_point_id=f"{component_id}#1",
        component_id=component_id,
        ordinal=1,
        slide_key=slide_key,
        verbatim_text=text,
        risk_flags=risk_flags,
        coverage_intents=intents,
        segmentation="assertion_level",
        operator_signed_exclusion=operator_signed,
    )


def _ann(point: SourcePoint) -> CoverageAnnotation:
    return CoverageAnnotation(
        component_id=point.component_id,
        slide_key=point.slide_key,
        source_points=(point,),
        segmentation="assertion_level",
        generated_at=_TS,
    )


def _write_enrichment(run_dir: Path, *, narration: bool) -> None:
    """g0-enrichment.json carrying (or not) a note-bearing narration typed component."""
    typed = []
    if narration:
        typed.append(
            {"component_id": "src-001-c001", "source_type": "narration",
             "label": "notes", "locator": "Slide 1", "excerpt": "spoken"}
        )
    else:
        typed.append(
            {"component_id": "src-001-c001", "source_type": "slide",
             "label": "deck", "locator": "Slide 1", "excerpt": "visual"}
        )
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "g0-enrichment.json").write_text(
        json.dumps({"typed_components": typed}), encoding="utf-8"
    )


def _mark_and_write(run_dir: Path, receipt) -> None:
    cgw.mark_coverage_receipt_expected(run_dir)
    cgw.write_coverage_receipt(run_dir, receipt)


# ---------------------------------------------------------------------------
# MF1 — vacuous-with-content: rows>0 but joined_row_count()==0 -> BLOCK
# ---------------------------------------------------------------------------


def test_vacuous_with_content_blocks_at_gate(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(cgw.COVERAGE_GATE_ACTIVE_ENV, "1")
    # A NON-must-cover point with NO anchor -> missing, joined_row_count()==0, rows>0.
    # The regular gate (must_cover predicate) does NOT block this; only the vacuous
    # guard catches it (the broken/empty-bridge false-PASS vector).
    receipt = derive_coverage_receipt([_ann(_point())], anchors={}, generated_at=_TS)
    assert receipt.rows and receipt.joined_row_count() == 0
    assert receipt.is_vacuous() is True
    _write_enrichment(tmp_path, narration=True)
    _mark_and_write(tmp_path, receipt)
    with pytest.raises(CoverageAssuranceError):
        cgw.enforce_coverage_gate_before_audio(specialist_id="enrique", run_dir=tmp_path)


# ---------------------------------------------------------------------------
# MF2 — empty-when-content-exists: zero rows but note-bearing content existed -> BLOCK
# ---------------------------------------------------------------------------


def test_empty_receipt_with_note_bearing_content_blocks(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(cgw.COVERAGE_GATE_ACTIVE_ENV, "1")
    empty = derive_coverage_receipt([], anchors={}, generated_at=_TS)
    assert empty.rows == ()
    _write_enrichment(tmp_path, narration=True)  # narration component exists
    _mark_and_write(tmp_path, empty)
    with pytest.raises(CoverageAssuranceError):
        cgw.enforce_coverage_gate_before_audio(specialist_id="enrique", run_dir=tmp_path)


# ---------------------------------------------------------------------------
# MF2 (negative) — legitimately empty (no note-bearing content) -> PASS, not blocked
# ---------------------------------------------------------------------------


def test_empty_receipt_no_note_bearing_content_passes(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(cgw.COVERAGE_GATE_ACTIVE_ENV, "1")
    empty = derive_coverage_receipt([], anchors={}, generated_at=_TS)
    _write_enrichment(tmp_path, narration=False)  # NO narration component
    _mark_and_write(tmp_path, empty)
    # empty-coverage never blocks (Round-4 contract)
    assert cgw.enforce_coverage_gate_before_audio(specialist_id="enrique", run_dir=tmp_path) is None


def test_empty_receipt_no_enrichment_file_passes(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(cgw.COVERAGE_GATE_ACTIVE_ENV, "1")
    empty = derive_coverage_receipt([], anchors={}, generated_at=_TS)
    _mark_and_write(tmp_path, empty)  # no g0-enrichment.json at all
    assert cgw.enforce_coverage_gate_before_audio(specialist_id="enrique", run_dir=tmp_path) is None


# ---------------------------------------------------------------------------
# SF2 — an all-deliberately_excluded receipt is NON-vacuous (legit "nothing to cover")
# ---------------------------------------------------------------------------


def test_all_deliberately_excluded_receipt_is_not_vacuous(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(cgw.COVERAGE_GATE_ACTIVE_ENV, "1")
    pt = _point(intents=("deliberately_excluded",), operator_signed=True)
    receipt = derive_coverage_receipt([_ann(pt)], anchors={}, generated_at=_TS)
    assert receipt.rows and receipt.joined_row_count() == 0
    # SF2: all operator-signed exclusions = legitimate nothing-to-cover, NOT vacuous.
    assert receipt.is_vacuous() is False
    _write_enrichment(tmp_path, narration=True)
    _mark_and_write(tmp_path, receipt)
    assert cgw.enforce_coverage_gate_before_audio(specialist_id="enrique", run_dir=tmp_path) is None


# ---------------------------------------------------------------------------
# Escape hatch — PROVISIONAL_OK downgrades the vacuous block (consistent with the
# existing missing-receipt provisional pattern); shipped default stays fail-loud.
# ---------------------------------------------------------------------------


def test_provisional_ok_downgrades_vacuous_block(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(cgw.COVERAGE_GATE_ACTIVE_ENV, "1")
    monkeypatch.setenv(cgw.COVERAGE_GATE_PROVISIONAL_ENV, "1")
    receipt = derive_coverage_receipt([_ann(_point())], anchors={}, generated_at=_TS)
    _write_enrichment(tmp_path, narration=True)
    _mark_and_write(tmp_path, receipt)
    assert cgw.enforce_coverage_gate_before_audio(specialist_id="enrique", run_dir=tmp_path) is None


# ---------------------------------------------------------------------------
# A genuinely-covered receipt still passes (no over-blocking from the guard).
# ---------------------------------------------------------------------------


def test_covered_receipt_passes_guard(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(cgw.COVERAGE_GATE_ACTIVE_ENV, "1")
    span = "healthcare is consolidating rapidly"
    pt = _point(text=span)
    anchors = {
        "Slide 1": AnchorResolution(slide_key="Slide 1", slide_present=True, slide_text=span)
    }
    receipt = derive_coverage_receipt([_ann(pt)], anchors=anchors, generated_at=_TS)
    assert receipt.joined_row_count() == 1 and receipt.is_vacuous() is False
    _write_enrichment(tmp_path, narration=True)
    _mark_and_write(tmp_path, receipt)
    assert cgw.enforce_coverage_gate_before_audio(specialist_id="enrique", run_dir=tmp_path) is None
