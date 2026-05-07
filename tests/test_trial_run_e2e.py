"""Story 32-3 — trial-run smoke harness tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.marcus.lesson_plan.log import LessonPlanLog
from app.marcus.orchestrator.trial_smoke_harness import run_trial_run_smoke_harness


@pytest.fixture(autouse=True)
def _patch_pre_packet_repo_root(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from app.marcus.intake import pre_packet

    monkeypatch.setattr(pre_packet, "_REPO_ROOT", tmp_path)


def _bundle(tmp_path: Path) -> Path:
    bundle = tmp_path / "bundle"
    bundle.mkdir(parents=True)
    (bundle / "extracted.md").write_text("# Extracted\nbody", encoding="utf-8")
    (bundle / "operator-directives.md").write_text("# Directives\nnone", encoding="utf-8")
    (bundle / "ingestion-quality-gate-receipt.md").write_text(
        "receipt: pass",
        encoding="utf-8",
    )
    (bundle / "metadata.json").write_text(
        json.dumps(
            {
                "primary_source": "fixture-source.pdf",
                "total_sections": 1,
                "overall_confidence": "high",
            }
        ),
        encoding="utf-8",
    )
    return bundle


def test_trial_smoke_harness_runs_end_to_end(tmp_path: Path) -> None:
    report = run_trial_run_smoke_harness(
        _bundle(tmp_path), log=LessonPlanLog(path=tmp_path / "log.jsonl")
    )
    assert report.smoke_passed is True
    assert report.quinn_gate_passed is True


def test_trial_smoke_harness_reports_expected_step_order(tmp_path: Path) -> None:
    report = run_trial_run_smoke_harness(
        _bundle(tmp_path), log=LessonPlanLog(path=tmp_path / "log.jsonl")
    )
    assert [step.step_id for step in report.steps] == [
        "01",
        "02",
        "03",
        "04",
        "04A",
        "05",
        "06",
        "07",
        "08",
        "09",
        "10",
        "11",
        "12",
        "13",
    ]


def test_trial_smoke_harness_marks_08_to_10_deferred(tmp_path: Path) -> None:
    report = run_trial_run_smoke_harness(
        _bundle(tmp_path), log=LessonPlanLog(path=tmp_path / "log.jsonl")
    )
    status_by_id = {step.step_id: step.status for step in report.steps}
    assert status_by_id["08"] == "deferred"
    assert status_by_id["09"] == "deferred"
    assert status_by_id["10"] == "deferred"


def test_trial_smoke_harness_writes_pre_packet_artifact(tmp_path: Path) -> None:
    bundle = _bundle(tmp_path)
    run_trial_run_smoke_harness(bundle, log=LessonPlanLog(path=tmp_path / "log.jsonl"))
    assert (bundle / "irene-packet.md").exists()


def test_trial_smoke_harness_includes_trial_ready_battery(tmp_path: Path) -> None:
    report = run_trial_run_smoke_harness(
        _bundle(tmp_path), log=LessonPlanLog(path=tmp_path / "log.jsonl")
    )
    assert report.trial_ready_battery.total_surfaces == 9
    assert report.trial_ready_battery.trial_ready is False


def test_trial_smoke_harness_battery_has_no_assertion_failures(tmp_path: Path) -> None:
    report = run_trial_run_smoke_harness(
        _bundle(tmp_path), log=LessonPlanLog(path=tmp_path / "log.jsonl")
    )
    assert report.trial_ready_battery.assertion_failures == ()


def test_trial_smoke_harness_exposes_coverage_manifest_path(tmp_path: Path) -> None:
    report = run_trial_run_smoke_harness(
        _bundle(tmp_path), log=LessonPlanLog(path=tmp_path / "log.jsonl")
    )
    assert report.coverage_manifest_path.replace("\\", "/").endswith(
        "_bmad-output/maps/coverage-manifest/lesson-plan-envelope-coverage-manifest.json"
    )


def test_trial_smoke_harness_requires_bundle_inputs(tmp_path: Path) -> None:
    bad_bundle = tmp_path / "bundle"
    bad_bundle.mkdir(parents=True)
    with pytest.raises(FileNotFoundError):
        run_trial_run_smoke_harness(bad_bundle, log=LessonPlanLog(path=tmp_path / "log.jsonl"))


def test_trial_smoke_harness_is_stable_for_five_consecutive_runs(tmp_path: Path) -> None:
    bundle = _bundle(tmp_path)
    outcomes = []
    for idx in range(5):
        report = run_trial_run_smoke_harness(
            bundle,
            run_id=f"trial-smoke-{idx}",
            log=LessonPlanLog(path=tmp_path / f"log-{idx}.jsonl"),
        )
        outcomes.append(report.smoke_passed)
    assert outcomes == [True, True, True, True, True]


def test_trial_smoke_harness_records_04a_step(tmp_path: Path) -> None:
    report = run_trial_run_smoke_harness(
        _bundle(tmp_path), log=LessonPlanLog(path=tmp_path / "log.jsonl")
    )
    detail = next(step.detail for step in report.steps if step.step_id == "04A")
    assert "4A loop locked plan" in detail

