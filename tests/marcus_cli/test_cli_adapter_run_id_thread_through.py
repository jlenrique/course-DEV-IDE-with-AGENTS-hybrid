from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

import yaml

from app.marcus.cli import trial as trial_module


def test_start_trial_threads_effective_trial_id_to_section_02a_adapter(
    tmp_path: Path,
) -> None:
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    (corpus_dir / "lesson.md").write_text("lesson", encoding="utf-8")
    runs_root = tmp_path / "runs"
    trial_id = uuid4()
    directive_path = runs_root / str(trial_id) / "directive.yaml"

    def _compose_and_write(**kwargs):
        directive_path.parent.mkdir(parents=True, exist_ok=True)
        directive_path.write_text("run_id: test\nsources: []\n", encoding="utf-8")
        return directive_path, "0" * 64

    with patch.object(
        trial_module,
        "compose_and_write",
        side_effect=_compose_and_write,
    ) as mock_compose:
        result = trial_module.start_trial(
            preset="production",
            input_path=corpus_dir,
            operator_id="operator_test",
            trial_id=trial_id,
            allow_offline_cost_report=True,
            runs_root=runs_root,
            confirm_fn=lambda **_kwargs: "saved-only",
            # S2 P17 belt-and-braces: this legacy suite exercises the
            # interactive start path — pin it pickless explicitly.
            picker_preflight_fn=lambda **_kwargs: None,
        )

    assert result["status"] == "saved-only"
    kwargs = mock_compose.call_args.kwargs
    assert kwargs["corpus_dir"] == corpus_dir
    assert kwargs["run_dir"] == runs_root / str(trial_id)
    assert kwargs["run_id"] == trial_id
    assert kwargs["gamma_settings"] is None


def test_start_trial_threads_gamma_settings_file_to_section_02a_adapter(
    tmp_path: Path,
) -> None:
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    (corpus_dir / "lesson.md").write_text("lesson", encoding="utf-8")
    runs_root = tmp_path / "runs"
    trial_id = uuid4()
    directive_path = runs_root / str(trial_id) / "directive.yaml"
    settings_path = tmp_path / "gamma-settings.yaml"
    settings_path.write_text(
        yaml.safe_dump([{"variant_id": "A"}, {"variant_id": "B"}], sort_keys=False),
        encoding="utf-8",
    )

    def _compose_and_write(**kwargs):
        directive_path.parent.mkdir(parents=True, exist_ok=True)
        directive_path.write_text("run_id: test\nsources: []\n", encoding="utf-8")
        return directive_path, "0" * 64

    with patch.object(
        trial_module,
        "compose_and_write",
        side_effect=_compose_and_write,
    ) as mock_compose:
        result = trial_module.start_trial(
            preset="production",
            input_path=corpus_dir,
            operator_id="operator_test",
            trial_id=trial_id,
            allow_offline_cost_report=True,
            runs_root=runs_root,
            confirm_fn=lambda **_kwargs: "saved-only",
            # S2 P17 belt-and-braces: this legacy suite exercises the
            # interactive start path — pin it pickless explicitly.
            picker_preflight_fn=lambda **_kwargs: None,
            gamma_settings_file=settings_path,
        )

    assert result["status"] == "saved-only"
    assert mock_compose.call_args.kwargs["gamma_settings"] == [
        {"variant_id": "A"},
        {"variant_id": "B"},
    ]


def test_start_trial_cli_loads_gamma_settings_file(tmp_path: Path, monkeypatch) -> None:
    settings_path = tmp_path / "gamma-settings.json"
    settings_path.write_text(
        '[{"variant_id": "A"}, {"variant_id": "B"}]',
        encoding="utf-8",
    )
    captured: dict[str, object] = {}

    def _fake_start_trial(**kwargs):
        captured.update(kwargs)
        return {"status": "saved-only", "trial_id": "trial-test"}

    monkeypatch.setattr(trial_module, "start_trial", _fake_start_trial)
    args = SimpleNamespace(
        preset="production",
        input=str(tmp_path / "corpus"),
        operator_id="operator_test",
        trial_id=None,
        allow_offline_cost_report=True,
        runs_root=str(tmp_path / "runs"),
        auto_confirm_directive=True,
        max_specialist_calls=None,
        gamma_settings_file=str(settings_path),
    )

    assert trial_module.start_trial_cli(args) == 0
    assert captured["gamma_settings_file"] == settings_path
