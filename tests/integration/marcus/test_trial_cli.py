from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.marcus.cli.__main__ import main
from app.marcus.cli.trial import start_trial

TRIAL_ID = "12345678-1234-4234-8234-123456789abc"


def test_start_trial_registers_run_and_cost_report(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGSMITH_PROJECT", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr("app.marcus.cli.trial._load_env_if_available", lambda: None)

    result = start_trial(
        preset="production",
        input_path=Path("tests/fixtures/trial_corpus/README.md"),
        operator_id="operator_test",
        allow_offline_cost_report=True,
        runs_root=tmp_path,
    )

    run_dir = tmp_path / result["trial_id"]
    assert result["status"] == "registered-offline"
    assert result["langsmith_trace_status"] == "skipped-no-langsmith-env"
    assert result["production_clone_launch_evidence"] is False
    assert (run_dir / "run.json").exists()
    assert (run_dir / "cost-report.json").exists()
    assert (run_dir / "cost-report.md").exists()

    envelope = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    assert envelope["trial_id"] == result["trial_id"]
    assert envelope["preset"] == "production"
    assert Path(envelope["corpus_path"]).as_posix() == "tests/fixtures/trial_corpus/README.md"
    assert envelope["schema_version"] == "production-trial-envelope.v1"
    assert envelope["production_clone_launch_evidence"] is False
    assert envelope["cost_report_path"] == str(run_dir / "cost-report.json")


def test_trial_start_cli_accepts_production_input(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGSMITH_PROJECT", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr("app.marcus.cli.trial._load_env_if_available", lambda: None)

    exit_code = main(
        [
            "trial",
            "start",
            "--preset",
            "production",
            "--input",
            "tests/fixtures/trial_corpus/README.md",
            "--operator-id",
            "operator_test",
            "--trial-id",
            TRIAL_ID,
            "--allow-offline-cost-report",
            "--runs-root",
            str(tmp_path),
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["trial_id"] == TRIAL_ID
    assert payload["production_clone_launch_evidence"] is False
    assert payload["run_registry_path"] == str(tmp_path / TRIAL_ID / "run.json")


def test_start_trial_requires_langsmith_for_production_evidence(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGSMITH_PROJECT", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr("app.marcus.cli.trial._load_env_if_available", lambda: None)

    with pytest.raises(RuntimeError, match="LANGSMITH_API_KEY and LANGSMITH_PROJECT"):
        start_trial(
            preset="production",
            input_path=Path("tests/fixtures/trial_corpus/README.md"),
            operator_id="operator_test",
            runs_root=tmp_path,
        )

    assert not any(tmp_path.iterdir())
