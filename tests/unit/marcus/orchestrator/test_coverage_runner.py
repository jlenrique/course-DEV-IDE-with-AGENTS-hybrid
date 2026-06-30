"""Step 3 render + Step 4 G3 derive/write SCAFFOLD (offline; defensive).

The ONE shared both-walks helper ``_derive_and_write_coverage_receipt`` (guarded
``gate_id == "G3"``): drops the receipt-expected marker, marshals run-state surfaces
DEFENSIVELY, derives + writes the canonical receipt, and renders the standalone
``coverage-report.html``. NEVER crashes on a missing/garbage run-state.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.marcus.lesson_plan.coverage_receipt import load_coverage_receipt
from app.marcus.orchestrator import coverage_gate_wiring as cgw
from app.marcus.orchestrator import coverage_runner as cr

# A minimal frozen g0-enrichment.json carrying ONE narration component's authored
# coverage annotation (component_id src-001, slide_key "Slide 1", one assertion).
_ENRICHMENT = {
    "coverage_annotations": [
        {
            "component_id": "src-001",
            "slide_key": "Slide 1",
            "segmentation": "assertion_level",
            "source_points": [
                {
                    "source_point_id": "src-001#1",
                    "component_id": "src-001",
                    "ordinal": 1,
                    "slide_key": "Slide 1",
                    "verbatim_text": "Dose is 5 mg daily.",
                    "risk_flags": ["dosing", "numeric"],
                    "coverage_intents": ["detail_in_narration"],
                    "segmentation": "assertion_level",
                    "verbatim_required": True,
                    "operator_signed_exclusion": False,
                }
            ],
        }
    ]
}


def _write_enrichment(run_dir: Path) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "g0-enrichment.json").write_text(json.dumps(_ENRICHMENT), encoding="utf-8")


def test_noop_off_g3(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(cgw.COVERAGE_GATE_ACTIVE_ENV, "1")
    assert cr._derive_and_write_coverage_receipt(tmp_path, "G2B", {}) is None
    assert not cgw.coverage_receipt_path(tmp_path).exists()


def test_noop_when_coverage_off(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv(cgw.COVERAGE_GATE_ACTIVE_ENV, raising=False)
    assert cr._derive_and_write_coverage_receipt(tmp_path, "G3", {}) is None
    assert not cgw.coverage_receipt_path(tmp_path).exists()
    assert not cgw.coverage_receipt_expected(tmp_path)  # no marker, no work


def test_g3_marks_expected_and_writes_receipt_and_html(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(cgw.COVERAGE_GATE_ACTIVE_ENV, "1")
    _write_enrichment(tmp_path)
    span = "Dose is 5 mg daily."
    run_state = {
        "gary_slide_content": [{"slide_index": 1, "title": "Trends", "body": span}],
        "joined_narration": [{"slide_key": "Slide 1", "narration_text": span}],
        "slide_key_map": {"1": "Slide 1"},
    }
    path = cr._derive_and_write_coverage_receipt(tmp_path, "G3", run_state)
    assert path is not None and path.name == "coverage-receipt.json"
    assert cgw.coverage_receipt_expected(tmp_path)  # marker dropped
    receipt = load_coverage_receipt(json.loads(path.read_text(encoding="utf-8")))
    assert len(receipt.rows) == 1
    row = receipt.rows[0]
    # the span reaches BOTH the deck slide and the narration -> covered
    assert row.coverage_status in {"both", "covered_in_narration", "covered_on_slide"}
    # the standalone html report is rendered next to the receipt
    html = (tmp_path / cr.COVERAGE_REPORT_BASENAME).read_text(encoding="utf-8")
    assert "Source-note coverage" in html and "Slide 1" in html


def test_g3_defensive_on_empty_run_state_records_diagnostics(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(cgw.COVERAGE_GATE_ACTIVE_ENV, "1")
    _write_enrichment(tmp_path)
    # no surfaces at all -> the point is missing, diagnostics recorded, NEVER crashes
    path = cr._derive_and_write_coverage_receipt(tmp_path, "G3", None)
    assert path is not None
    receipt = load_coverage_receipt(json.loads(path.read_text(encoding="utf-8")))
    assert receipt.diagnostics  # unresolved joins surfaced on the receipt face
    assert receipt.rows[0].coverage_status == "missing"
    assert cgw.coverage_receipt_expected(tmp_path)  # marker stands → gate fires loud


def test_g3_vacuous_when_no_annotations(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(cgw.COVERAGE_GATE_ACTIVE_ENV, "1")
    # no g0-enrichment.json -> zero source points -> vacuous PASS receipt, no crash
    path = cr._derive_and_write_coverage_receipt(tmp_path, "G3", {})
    assert path is not None
    receipt = load_coverage_receipt(json.loads(path.read_text(encoding="utf-8")))
    assert receipt.rows == ()
