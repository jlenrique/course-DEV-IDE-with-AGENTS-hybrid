"""B6-land: trial CLI --llm-execution-mode surface."""

from __future__ import annotations

import argparse
from uuid import uuid4

import pytest

from app.marcus.cli import trial as trial_mod
from app.marcus.cli.trial import build_trial_parser, start_trial_cli


def test_trial_parser_defaults_llm_execution_mode_realtime() -> None:
    parser = argparse.ArgumentParser()
    build_trial_parser(parser)
    args = parser.parse_args(["start", "--input", "x"])
    assert args.llm_execution_mode == "realtime"


def test_trial_parser_accepts_batch() -> None:
    parser = argparse.ArgumentParser()
    build_trial_parser(parser)
    args = parser.parse_args(
        ["start", "--input", "x", "--llm-execution-mode", "batch"]
    )
    assert args.llm_execution_mode == "batch"


def test_trial_start_help_mentions_opt_in_batch_and_resume() -> None:
    parser = argparse.ArgumentParser()
    build_trial_parser(parser)
    # Subparser help is nested; check start action help via parse.
    start = next(
        a for a in parser._subparsers._group_actions[0].choices["start"]._actions
        if getattr(a, "dest", None) == "llm_execution_mode"
    )
    assert "default: realtime" in (start.help or "")
    assert "resume-batch" in (start.help or "")
    assert "cost-report.json" in (start.help or "")
    assert "resume-batch" in parser._subparsers._group_actions[0].choices


def test_trial_parser_rejects_batch_uppercase() -> None:
    parser = argparse.ArgumentParser()
    build_trial_parser(parser)
    with pytest.raises(SystemExit):
        parser.parse_args(["start", "--input", "x", "--llm-execution-mode", "BATCH"])


def test_start_trial_cli_threads_llm_execution_mode_to_start_trial(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def fake_start_trial(**kwargs: object) -> dict[str, object]:
        captured.update(kwargs)
        return {
            "status": "registered-offline",
            "trial_id": str(uuid4()),
            "llm_execution_mode": kwargs.get("llm_execution_mode"),
        }

    monkeypatch.setattr("app.marcus.cli.trial.start_trial", fake_start_trial)
    monkeypatch.setattr(
        "app.marcus.cli.trial._resolve_start_component_selection",
        lambda _args: trial_mod._StartSelection(selection=None),
    )
    parser = argparse.ArgumentParser()
    build_trial_parser(parser)
    args = parser.parse_args(
        [
            "start",
            "--input",
            "corpus",
            "--llm-execution-mode",
            "batch",
            "--allow-offline-cost-report",
        ]
    )
    rc = start_trial_cli(args)
    assert rc == 0
    assert captured["llm_execution_mode"] == "batch"
