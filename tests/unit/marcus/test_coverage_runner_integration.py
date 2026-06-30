"""Runner-integration core — canonical SHA, fail-loud-on-missing, vacuous PASS.

Offline. RED-first for the three Round-4 keystones:
  * canonical/idempotent receipt body (the RAI CANONICAL_SHA256 pin survives the
    resume/recover G3 crossing — volatile fields excluded; recompute, never append);
  * gate FAIL-LOUD on missing-receipt-at-audio past G3 (Marcus keystone), with the
    dev provisional escape hatch;
  * empty-coverage -> PASS-vacuous (never crash/block).
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

_TS_A = datetime(2026, 6, 30, 12, 0, 0, tzinfo=UTC)
_TS_B = datetime(2026, 6, 30, 18, 30, 0, tzinfo=UTC)  # a DIFFERENT wall-clock time


def _annotation():
    pt = SourcePoint(
        source_point_id="src-001#1", component_id="src-001", ordinal=1,
        slide_key="Slide 1", verbatim_text="Dose is 5 mg daily.",
        risk_flags=("numeric", "dosing"), coverage_intents=("detail_in_narration",),
        segmentation="assertion_level",
    )
    return CoverageAnnotation(
        component_id="src-001", slide_key="Slide 1", source_points=(pt,),
        segmentation="assertion_level", generated_at=_TS_A,
    )


def _clear_anchors(span: str = "Dose is 5 mg daily."):
    return {
        "Slide 1": AnchorResolution(
            slide_key="Slide 1", slide_present=False, narration_present=True, narration_text=span
        )
    }


# --- Keystone: canonical/idempotent receipt body --------------------------------


def test_canonical_hash_excludes_volatile_generated_at() -> None:
    r1 = derive_coverage_receipt([_annotation()], anchors=_clear_anchors(), generated_at=_TS_A)
    r2 = derive_coverage_receipt([_annotation()], anchors=_clear_anchors(), generated_at=_TS_B)
    # same surfaces, DIFFERENT generated_at -> identical canonical payload + SHA
    assert r1.generated_at != r2.generated_at
    assert r1.canonical_hash_payload() == r2.canonical_hash_payload()
    assert "generated_at" not in r1.canonical_hash_payload()
    assert r1.canonical_sha256() == r2.canonical_sha256()


def test_on_disk_receipt_digest_stable_across_re_derive(tmp_path: Path) -> None:
    from app.marcus.lesson_plan.run_asset_index import DigestAlgo, recompute_digest_from_disk

    p1 = cgw.write_coverage_receipt(
        tmp_path, derive_coverage_receipt([_annotation()], anchors=_clear_anchors(),
                                          generated_at=_TS_A)
    )
    d1 = recompute_digest_from_disk(p1, DigestAlgo.CANONICAL_SHA256)
    # a SECOND derive at a different wall-clock time, re-written, must hash identically
    p2 = cgw.write_coverage_receipt(
        tmp_path, derive_coverage_receipt([_annotation()], anchors=_clear_anchors(),
                                          generated_at=_TS_B)
    )
    d2 = recompute_digest_from_disk(p2, DigestAlgo.CANONICAL_SHA256)
    assert d1 == d2


# --- Keystone: gate FAIL-LOUD on missing-receipt-at-audio past G3 ----------------


def test_fail_loud_when_past_g3_and_no_receipt(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(cgw.COVERAGE_GATE_ACTIVE_ENV, "1")
    monkeypatch.delenv(cgw.COVERAGE_GATE_PROVISIONAL_ENV, raising=False)
    cgw.mark_coverage_receipt_expected(tmp_path)  # G3 crossed, receipt expected here
    # no receipt on disk -> audio about to dispatch -> RAISE (not the silent no-op)
    with pytest.raises(CoverageAssuranceError) as exc:
        cgw.enforce_coverage_gate_before_audio(specialist_id="enrique", run_dir=tmp_path)
    assert exc.value.tag == cgw.COVERAGE_RECEIPT_MISSING_TAG


def test_provisional_dev_flag_downgrades_missing_to_noop(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(cgw.COVERAGE_GATE_ACTIVE_ENV, "1")
    monkeypatch.setenv(cgw.COVERAGE_GATE_PROVISIONAL_ENV, "1")
    cgw.mark_coverage_receipt_expected(tmp_path)
    # dev provisional escape hatch -> no-op even past G3 with no receipt
    assert cgw.enforce_coverage_gate_before_audio(specialist_id="enrique", run_dir=tmp_path) is None


def test_no_marker_is_provisional_window_noop(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(cgw.COVERAGE_GATE_ACTIVE_ENV, "1")
    monkeypatch.delenv(cgw.COVERAGE_GATE_PROVISIONAL_ENV, raising=False)
    # G3 NOT crossed (no marker) -> the legitimate provisional window -> no-op
    assert cgw.enforce_coverage_gate_before_audio(specialist_id="enrique", run_dir=tmp_path) is None


# --- Keystone: empty-coverage -> PASS-vacuous ------------------------------------


def test_empty_coverage_is_pass_vacuous(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(cgw.COVERAGE_GATE_ACTIVE_ENV, "1")
    monkeypatch.delenv(cgw.COVERAGE_GATE_PROVISIONAL_ENV, raising=False)
    receipt = derive_coverage_receipt([], anchors={})  # zero source points
    assert receipt.rows == ()
    cgw.write_coverage_receipt(tmp_path, receipt)
    cgw.mark_coverage_receipt_expected(tmp_path)
    # a vacuous receipt EXISTS -> gate passes, never crashes/blocks
    assert cgw.enforce_coverage_gate_before_audio(specialist_id="enrique", run_dir=tmp_path) is None
