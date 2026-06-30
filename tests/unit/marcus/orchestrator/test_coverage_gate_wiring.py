"""T6 — coverage fail-loud gate wiring at the both-walks UDAC dispatch seam.

The gate is a READER at the SHARED dispatch site (``_dispatch_specialist_at_node``),
which is walk-invariant — wiring there covers BOTH the start walk and the
continuation/recover walk by construction (mirrors ``resolve_consumed_assets``). The
gate fires only before the AUDIO-spending specialist, only when the feature flag is
ON, and routes through ``CoverageAssuranceError`` (a ``SpecialistDispatchError``) so
both walkers' ``except SpecialistDispatchError`` pause the run before audio spend.

Flag OFF ⇒ provably no-op (byte-identical firewall). OFFLINE — no live LLM/network.
"""

from __future__ import annotations

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


def _blocking_receipt():
    pt = SourcePoint(
        source_point_id="src-001-c001#1", component_id="src-001-c001", ordinal=1,
        slide_key="Slide 1", verbatim_text="Dose is 5 mg daily.",
        risk_flags=("numeric", "dosing"), coverage_intents=("detail_in_narration",),
        segmentation="assertion_level",
    )
    ann = CoverageAnnotation(
        component_id="src-001-c001", slide_key="Slide 1", source_points=(pt,),
        segmentation="assertion_level", generated_at=_TS,
    )
    return derive_coverage_receipt([ann], anchors={}, generated_at=_TS)


def _clear_receipt():
    span = "Dose is 5 mg daily."
    pt = SourcePoint(
        source_point_id="src-001-c001#1", component_id="src-001-c001", ordinal=1,
        slide_key="Slide 1", verbatim_text=span, risk_flags=("numeric", "dosing"),
        coverage_intents=("detail_in_narration",), segmentation="assertion_level",
    )
    ann = CoverageAnnotation(
        component_id="src-001-c001", slide_key="Slide 1", source_points=(pt,),
        segmentation="assertion_level", generated_at=_TS,
    )
    anchors = {
        "Slide 1": AnchorResolution(
            slide_key="Slide 1", slide_present=False, narration_present=True, narration_text=span
        )
    }
    return derive_coverage_receipt([ann], anchors=anchors, generated_at=_TS)


def test_flag_default_off(monkeypatch) -> None:
    monkeypatch.delenv(cgw.COVERAGE_GATE_ACTIVE_ENV, raising=False)
    assert cgw.coverage_gate_active() is False


def test_persist_and_load_round_trip(tmp_path: Path) -> None:
    receipt = _blocking_receipt()
    path = cgw.write_coverage_receipt(tmp_path, receipt)
    assert path.name == "coverage-receipt.json"
    loaded = cgw.load_coverage_receipt_from_disk(tmp_path)
    # The on-disk artifact is the VOLATILE-FREE canonical projection (Round-4 SHA
    # stability — generated_at is intentionally NOT persisted), so equality holds on
    # the canonical payload (rows + segmentation + diagnostics), not on generated_at.
    assert loaded.canonical_hash_payload() == receipt.canonical_hash_payload()
    assert loaded.rows == receipt.rows


def test_gate_noop_when_flag_off(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv(cgw.COVERAGE_GATE_ACTIVE_ENV, raising=False)
    cgw.write_coverage_receipt(tmp_path, _blocking_receipt())
    # flag OFF → byte-identical firewall: never loads, never raises
    assert cgw.enforce_coverage_gate_before_audio(specialist_id="enrique", run_dir=tmp_path) is None


def test_gate_noop_for_non_audio_specialist(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(cgw.COVERAGE_GATE_ACTIVE_ENV, "1")
    cgw.write_coverage_receipt(tmp_path, _blocking_receipt())
    # gary/irene are not audio-spending → no gate
    assert cgw.enforce_coverage_gate_before_audio(specialist_id="gary", run_dir=tmp_path) is None


def test_gate_noop_when_no_receipt(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(cgw.COVERAGE_GATE_ACTIVE_ENV, "1")
    # no receipt persisted yet (provisional window) → no enforcement
    assert cgw.enforce_coverage_gate_before_audio(specialist_id="enrique", run_dir=tmp_path) is None


@pytest.mark.parametrize("audio_specialist", sorted(cgw.AUDIO_SPEND_SPECIALISTS))
def test_gate_blocks_audio_spend_both_walks(tmp_path: Path, monkeypatch, audio_specialist) -> None:
    # The seam is walk-invariant: this same call path is taken by BOTH the start
    # and the continuation/recover walker. A blocking receipt → CoverageAssuranceError
    # (a SpecialistDispatchError) → routed through _pause_at_error before audio spend.
    monkeypatch.setenv(cgw.COVERAGE_GATE_ACTIVE_ENV, "1")
    cgw.write_coverage_receipt(tmp_path, _blocking_receipt())
    with pytest.raises(CoverageAssuranceError) as exc:
        cgw.enforce_coverage_gate_before_audio(specialist_id=audio_specialist, run_dir=tmp_path)
    assert exc.value.tag == "marcus.coverage.must-cover-uncovered"


def test_gate_passes_when_clear(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(cgw.COVERAGE_GATE_ACTIVE_ENV, "1")
    cgw.write_coverage_receipt(tmp_path, _clear_receipt())
    assert cgw.enforce_coverage_gate_before_audio(specialist_id="enrique", run_dir=tmp_path) is None
