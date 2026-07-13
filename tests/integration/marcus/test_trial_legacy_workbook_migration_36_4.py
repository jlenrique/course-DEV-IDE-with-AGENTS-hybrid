from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

import pytest

from app.marcus.cli import trial as trial_module
from app.marcus.lesson_plan.prework_artifact import (
    WorkbookBriefRuntimeContext,
    read_runtime_context,
    write_runtime_context,
)
from app.models.runtime.production_envelope import ProductionEnvelope, SpecialistContribution
from app.models.runtime.production_trial_envelope import ProductionTrialEnvelope
from app.models.state.component_selection import ComponentSelection
from app.models.state.run_state import RunState

TRIAL_ID = UUID("72345678-1234-4234-8234-123456789abc")
SOURCE = Path("course-content/courses/tejal-apc-c1-m1-p2-trends").resolve()


def _seed_legacy(run_root: Path, *, workbook: bool = True) -> Path:
    run_dir = run_root / str(TRIAL_ID)
    run_dir.mkdir(parents=True)
    production = ProductionEnvelope(trial_id=TRIAL_ID)
    production.add_contribution(
        SpecialistContribution.from_output(
            specialist_id="workbook_brief_stub",
            node_id="07W.1",
            output={"stub_status": "not_yet_wired"},
            model_used="deterministic-workbook-band-stub",
        )
    )
    envelope = ProductionTrialEnvelope(
        trial_id=TRIAL_ID,
        preset="production",
        corpus_path="legacy",
        operator_id="operator_test",
        started_at=datetime.now(UTC),
        status="paused-at-error",
        paused_error_tag="workbook-brief.legacy-reentry-required",
        production_clone_launch_evidence=False,
        production_envelope=production,
    )
    (run_dir / "run.json").write_text(envelope.model_dump_json(indent=2) + "\n", "utf-8")
    state = RunState(
        run_id=TRIAL_ID,
        graph_version="v42",
        status="running",
        production_envelope=production,
        component_selection=ComponentSelection(deck=True, workbook=workbook),
    )
    (run_dir / "error-pause.json").write_text(
        json.dumps(
            {
                "trial_id": str(TRIAL_ID),
                "run_state": state.model_dump(mode="json"),
                "runner": {"allow_offline_cost_report": True},
            }
        ),
        "utf-8",
    )
    return run_dir


def test_api_migrates_idempotently_and_forces_07w1_reentry(tmp_path, monkeypatch) -> None:
    run_dir = _seed_legacy(tmp_path)
    captured = {}
    fake = ProductionTrialEnvelope.model_validate_json((run_dir / "run.json").read_text("utf-8"))

    def recover(**kwargs):
        captured.update(kwargs)
        return fake

    monkeypatch.setattr(trial_module, "recover_production_trial", recover)
    first = trial_module.recover_trial(
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
        course_source_root=SOURCE,
        encounter_mode="live",
    )
    second_path = trial_module._migrate_legacy_workbook_context(
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
        course_source_root=SOURCE,
        encounter_mode="live",
    )
    context = read_runtime_context(run_dir)
    assert first["workbook_context_migrated"] is True
    assert captured["reenter_at_node"] == "07W.1"
    assert second_path == run_dir / "workbook-runtime-context.v1.json"
    assert context.context_origin == "operator_migrated"
    assert context.course_source_root == SOURCE
    assert context.encounter_mode == "live"


def test_migration_rejects_non_workbook_and_conflicting_reentry(tmp_path) -> None:
    _seed_legacy(tmp_path, workbook=False)
    with pytest.raises(ValueError, match="non-workbook"):
        trial_module.recover_trial(
            trial_id=TRIAL_ID,
            runs_root=tmp_path,
            course_source_root=SOURCE,
            encounter_mode="recorded",
        )


def test_migration_rejects_real_context_and_conflicting_repeat(tmp_path) -> None:
    run_dir = _seed_legacy(tmp_path)
    write_runtime_context(
        WorkbookBriefRuntimeContext(
            run_dir=run_dir,
            course_source_root=SOURCE,
            encounter_mode="recorded",
            context_origin="new_start",
            writer_execution_mode="offline_stub",
        )
    )
    with pytest.raises(ValueError, match="real/non-legacy"):
        trial_module._migrate_legacy_workbook_context(
            trial_id=TRIAL_ID,
            runs_root=tmp_path,
            course_source_root=SOURCE,
            encounter_mode="recorded",
        )

    (run_dir / "workbook-runtime-context.v1.json").unlink()
    trial_module._migrate_legacy_workbook_context(
        trial_id=TRIAL_ID,
        runs_root=tmp_path,
        course_source_root=SOURCE,
        encounter_mode="recorded",
    )
    with pytest.raises(ValueError, match="conflicts"):
        trial_module._migrate_legacy_workbook_context(
            trial_id=TRIAL_ID,
            runs_root=tmp_path,
            course_source_root=SOURCE,
            encounter_mode="live",
        )
    with pytest.raises(ValueError, match="07W.1"):
        trial_module.recover_trial(
            trial_id=TRIAL_ID,
            runs_root=tmp_path,
            reenter_at_node="07W.2",
            course_source_root=SOURCE,
            encounter_mode="recorded",
        )


def test_recover_cli_exposes_named_migration_flags(monkeypatch, capsys) -> None:
    captured = {}
    monkeypatch.setattr(
        trial_module,
        "recover_trial",
        lambda **kwargs: captured.update(kwargs) or {"status": "in-flight"},
    )
    code = trial_module.recover_trial_cli(
        argparse.Namespace(
            trial_id=TRIAL_ID,
            runs_root=None,
            max_specialist_calls=None,
            reenter_at_node=None,
            course_source_root=str(SOURCE),
            encounter_mode="recorded",
        )
    )
    assert code == 0
    assert captured["course_source_root"] == SOURCE
    assert captured["encounter_mode"] == "recorded"
    assert json.loads(capsys.readouterr().out)["status"] == "in-flight"
