"""Per-gate shim basic invocation tests (Story 7a.7, AC-7.7-A)."""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest

SHIM_MODULES = [
    ("app.marcus.cli.gate_shims.g1_shim", "G1"),
    ("app.marcus.cli.gate_shims.g2c_shim", "G2C"),
    ("app.marcus.cli.gate_shims.g3_shim", "G3"),
    ("app.marcus.cli.gate_shims.g4_shim", "G4"),
]


def _write_verdict(
    tmp_path: Path,
    trial_id: UUID,
    gate_id: str,
    verb: str = "approve",
) -> Path:
    payload = {
        "verdict_id": "11111111-1111-4111-8111-111111111111",
        "trial_id": str(trial_id),
        "card_id": "22222222-2222-4222-8222-222222222222",
        "verb": verb,
        "gate_id": gate_id,
        "decision_card_digest": "a" * 64,
        "operator_id": "juanl",
        "edit_payload": None,
        "reject_reason": None,
        "revise_count": 0,
        "timestamp": "2026-04-29T12:00:00Z",
    }
    target = tmp_path / "verdict.json"
    target.write_text(json.dumps(payload), encoding="utf-8")
    return target


@pytest.mark.parametrize(("module_name", "gate_id"), SHIM_MODULES)
def test_shim_main_success_invokes_resume_and_returns_zero(
    module_name: str,
    gate_id: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Each shim loads verdict, calls resume_production_trial, exits 0."""
    module = importlib.import_module(module_name)
    trial_id = uuid4()
    verdict_path = _write_verdict(tmp_path, trial_id, gate_id)
    runs_root = tmp_path / "runs"

    fake_envelope = MagicMock()
    fake_envelope.status = "completed"
    fake_envelope.paused_gate = None
    fake_envelope.cost_report_path = None
    fake_envelope.production_clone_launch_evidence = False

    captured: dict[str, Any] = {}

    def _fake_resume(*, trial_id, verdict, runs_root):
        captured["trial_id"] = trial_id
        captured["verdict_trial_id"] = verdict.trial_id
        captured["runs_root"] = runs_root
        return fake_envelope

    monkeypatch.setattr(module, "resume_production_trial", _fake_resume)
    rc = module.main(
        [
            "--trial-id",
            str(trial_id),
            "--verdict-file",
            str(verdict_path),
            "--operator-id",
            "juanl",
            "--runs-root",
            str(runs_root),
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload["status"] == "completed"
    assert payload["gate_id"] == gate_id
    assert captured["trial_id"] == trial_id
    assert captured["verdict_trial_id"] == trial_id


@pytest.mark.parametrize(("module_name", "gate_id"), SHIM_MODULES)
def test_shim_invalid_verdict_returns_exit_code_2(
    module_name: str,
    gate_id: str,
    tmp_path: Path,
) -> None:
    module = importlib.import_module(module_name)
    bad = tmp_path / "bad.json"
    bad.write_text("{not valid json", encoding="utf-8")
    trial_id = uuid4()
    rc = module.main(
        [
            "--trial-id",
            str(trial_id),
            "--verdict-file",
            str(bad),
        ]
    )
    assert rc == 2


@pytest.mark.parametrize(("module_name", "gate_id"), SHIM_MODULES)
def test_shim_trial_id_mismatch_returns_exit_code_1(
    module_name: str,
    gate_id: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = importlib.import_module(module_name)
    trial_id_a = uuid4()
    trial_id_b = uuid4()
    verdict_path = _write_verdict(tmp_path, trial_id_a, gate_id)
    rc = module.main(
        [
            "--trial-id",
            str(trial_id_b),
            "--verdict-file",
            str(verdict_path),
        ]
    )
    assert rc == 1


@pytest.mark.parametrize(("module_name", "gate_id"), SHIM_MODULES)
def test_shim_runtime_error_returns_exit_code_1(
    module_name: str,
    gate_id: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = importlib.import_module(module_name)
    trial_id = uuid4()
    verdict_path = _write_verdict(tmp_path, trial_id, gate_id)

    def _boom(**_kwargs):
        raise RuntimeError("trial not paused at this gate")

    monkeypatch.setattr(module, "resume_production_trial", _boom)
    rc = module.main(
        [
            "--trial-id",
            str(trial_id),
            "--verdict-file",
            str(verdict_path),
        ]
    )
    assert rc == 1
