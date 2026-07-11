"""Round-trip tests for the CLI-co-located next-action builder (Story 35.2 / AD-3).

Every built command string must parse cleanly through the ACTUAL argparse
parser for its subcommand, so a renamed flag fails THIS builder (the producer),
never the operator staring at a broken copy-paste command.
"""

from __future__ import annotations

import argparse
import json
import shlex
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.marcus.cli.gate_cli import build_parser as build_gate_parser
from app.marcus.cli.next_action import build_next_action
from app.marcus.cli.trial import build_trial_parser


def _trial_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="trial")
    build_trial_parser(parser)
    return parser


def _env(status: str, **kw):
    base = dict(
        trial_id=uuid4(),
        status=status,
        paused_gate=None,
        paused_error_tag=None,
        waiting_batch_id=None,
        operator_id="operator_cli",
    )
    base.update(kw)
    return SimpleNamespace(**base)


def test_paused_at_gate_command_round_trips(tmp_path: Path) -> None:
    env = _env("paused-at-gate", paused_gate="G1")
    card_path = tmp_path / "decision-card-G1.json"
    card_path.write_text(
        json.dumps({"card": {"card_id": str(uuid4())}, "digest": "abc123"}),
        encoding="utf-8",
    )
    cmd = build_next_action(env, card_path=card_path)
    tokens = shlex.split(cmd)
    assert tokens[0] == "gate"
    ns = build_gate_parser().parse_args(tokens[1:])  # drop the "gate" program token
    assert ns.command == "decide"
    assert ns.trial_id == str(env.trial_id)
    assert ns.gate_id == "G1"
    assert ns.verb == "approve"
    assert ns.card_id  # non-empty
    assert ns.decision_card_digest == "abc123"
    assert ns.operator_id == "operator_cli"


def test_paused_at_error_command_round_trips() -> None:
    env = _env("paused-at-error", paused_error_tag="gamma_blip")
    cmd = build_next_action(env)
    tokens = shlex.split(cmd)
    assert tokens[0] == "trial"
    ns = _trial_parser().parse_args(tokens[1:])  # drop the "trial" program token
    assert ns.trial_command == "recover"
    assert ns.trial_id == env.trial_id  # trial parser coerces to UUID


def test_waiting_for_provider_batch_command_round_trips() -> None:
    env = _env("waiting_for_provider_batch", waiting_batch_id="batch_9")
    cmd = build_next_action(env)
    tokens = shlex.split(cmd)
    assert tokens[0] == "trial"
    ns = _trial_parser().parse_args(tokens[1:])
    assert ns.trial_command == "resume-batch"
    assert ns.trial_id == env.trial_id


def test_non_pause_status_raises() -> None:
    with pytest.raises(ValueError):
        build_next_action(_env("in-flight"))


def test_missing_card_degrades_without_raising() -> None:
    # No card file present: builder returns empty card fields rather than raising.
    env = _env("paused-at-gate", paused_gate="G1")
    cmd = build_next_action(env, card_path=Path("does-not-exist.json"))
    assert cmd.startswith("gate decide")
    assert "--gate-id G1" in cmd
