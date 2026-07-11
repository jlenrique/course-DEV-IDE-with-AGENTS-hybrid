"""B6-land: real trial-start.json receipt for llm_execution_mode."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from uuid import uuid4

import pytest

from app.marcus.cli.trial import start_trial


@pytest.fixture(autouse=True)
def _offline_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGSMITH_PROJECT", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr("app.marcus.cli.trial._load_env_if_available", lambda: None)
    monkeypatch.setenv("MARCUS_G0_ENRICHMENT_ACTIVE", "0")


def _fake_envelope(trial_id: Any) -> SimpleNamespace:
    return SimpleNamespace(
        status="registered",
        cost_report_path=None,
        production_clone_launch_evidence=False,
        production_clone_launch_evidence_reason="test",
        trial_id=trial_id,
    )


@pytest.mark.parametrize(
    ("mode", "expect_note"),
    [("realtime", False), ("batch", True)],
)
def test_start_trial_writes_llm_execution_mode_receipt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mode: str,
    expect_note: bool,
) -> None:
    captured: dict[str, Any] = {}
    spies = {"create_file": 0, "create_batch": 0}

    def boom_create_file(*_a: Any, **_k: Any) -> Any:
        spies["create_file"] += 1
        raise AssertionError("create_file must not run during receipt-only start")

    def boom_create_batch(*_a: Any, **_k: Any) -> Any:
        spies["create_batch"] += 1
        raise AssertionError("create_batch must not run during receipt-only start")

    def fake_run_production_trial(**kwargs: Any) -> SimpleNamespace:
        captured.update(kwargs)
        run_dir = Path(kwargs["runs_root"]) / str(kwargs["trial_id"])
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "run.json").write_text("{}", encoding="utf-8")
        return _fake_envelope(kwargs["trial_id"])

    monkeypatch.setattr("app.marcus.cli.trial.run_production_trial", fake_run_production_trial)
    monkeypatch.setattr("litellm.create_file", boom_create_file)
    monkeypatch.setattr("litellm.create_batch", boom_create_batch)
    monkeypatch.setattr(
        "app.runtime.llm_batch.adapter.litellm.create_file", boom_create_file
    )
    monkeypatch.setattr(
        "app.runtime.llm_batch.adapter.litellm.create_batch", boom_create_batch
    )

    trial_id = uuid4()
    result = start_trial(
        preset="production",
        input_path=Path("tests/fixtures/trial_corpus/README.md"),
        operator_id="operator_test",
        trial_id=trial_id,
        allow_offline_cost_report=True,
        auto_confirm_directive=True,
        runs_root=tmp_path,
        llm_execution_mode=mode,  # type: ignore[arg-type]
    )

    assert captured["llm_execution_mode"] == mode
    assert result["llm_execution_mode"] == mode
    receipt_path = tmp_path / str(trial_id) / "trial-start.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["llm_execution_mode"] == mode
    if expect_note:
        assert "Batch completion" in (receipt["llm_batch_wait_note"] or "")
    else:
        assert receipt["llm_batch_wait_note"] is None
    assert spies["create_file"] == 0
    assert spies["create_batch"] == 0
    assert not any(p for p in tmp_path.rglob("llm_batch") if p.is_dir())
