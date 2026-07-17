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

import app.marcus.cli.trial as trial_cli
from app.marcus.cli.next_action import build_next_action
from app.marcus.cli.trial import (
    _build_inline_verdict,
    build_trial_parser,
    resume_trial_cli,
)
from app.models.state.operator_verdict import OperatorVerdict


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


def _resume_line(surface: str, verb: str) -> str:
    """Extract the single ``trial resume ... --verb <verb> ...`` paste line from
    the Story-42.1 NEUTRAL multi-verb next-action surface.

    ``build_next_action`` for a ``paused-at-gate`` no longer returns ONE approve-
    prefilled command — it returns a neutral surface with one paste line per
    allowed verb. The F-E2E-1 round-trip proof (executable-shaped, builds a valid
    OperatorVerdict) now applies to each extracted per-verb line.
    """
    for raw in surface.splitlines():
        line = raw.strip()
        if line.startswith("trial resume") and f" --verb {verb} " in f"{line} ":
            return line
    raise AssertionError(f"no resume line for verb {verb!r} in surface:\n{surface}")


def test_paused_at_gate_command_round_trips(tmp_path: Path) -> None:
    """F-E2E-1: the gate-class next-action must be EXECUTABLE-shaped, not merely
    parseable. It now targets `trial resume` inline-verdict mode, and the round
    trip proves the parsed args assemble a VALID OperatorVerdict — the exact
    object the resume walk consumes — so a fresh-shell copy-paste can act.

    (The former `gate decide` target read an empty in-memory `_CARD_STORE`
    cross-process and failed `card_missing`; parse-acceptance alone hid that.)
    """
    env = _env("paused-at-gate", paused_gate="G1")
    card_id = str(uuid4())
    digest = "a" * 64  # OperatorVerdict requires a lowercase sha256 hex digest
    card_path = tmp_path / "decision-card-G1.json"
    card_path.write_text(
        json.dumps({"card": {"card_id": card_id}, "digest": digest}),
        encoding="utf-8",
    )
    surface = build_next_action(env, card_path=card_path)
    cmd = _resume_line(surface, "approve")  # round-trip the approve paste line
    tokens = shlex.split(cmd)

    # (1) The command routes through the REAL `trial resume` grammar.
    assert tokens[0] == "trial"
    ns = _trial_parser().parse_args(tokens[1:])  # drop the "trial" program token
    assert ns.trial_command == "resume"
    assert ns.trial_id == env.trial_id  # trial parser coerces to UUID
    assert ns.gate_id == "G1"
    assert ns.verb == "approve"
    assert ns.card_id == card_id
    assert ns.decision_card_digest == digest
    assert ns.operator_id == "operator_cli"
    assert ns.verdict_file is None  # inline mode — no file source

    # (2) The parsed args actually BUILD a valid OperatorVerdict via the same
    # inline-verdict builder resume_trial_cli uses. If the command were merely
    # parseable but not verdict-shaped, this construction would raise.
    verdict = _build_inline_verdict(ns)
    assert isinstance(verdict, OperatorVerdict)
    assert verdict.trial_id == env.trial_id
    assert verdict.gate_id == "G1"
    assert verdict.verb == "approve"
    assert str(verdict.card_id) == card_id
    assert verdict.decision_card_digest == digest
    assert verdict.operator_id == "operator_cli"


def test_gate_command_reaches_resume_walk_cross_process(
    tmp_path: Path, monkeypatch
) -> None:
    """F-E2E-1 execution-level (Murat's fence): drive the built gate command
    through `resume_trial_cli` and prove it REACHES `resume_trial` with a valid
    inline verdict — the cross-process path `gate decide` never reached. No
    live LLM: `resume_trial` is stubbed to capture the verdict.
    """
    env = _env("paused-at-gate", paused_gate="G2B")
    card_id = str(uuid4())
    digest = "b" * 64
    card_path = tmp_path / "decision-card-G2B.json"
    card_path.write_text(
        json.dumps({"card": {"card_id": card_id}, "digest": digest}), encoding="utf-8"
    )
    surface = build_next_action(env, card_path=card_path)
    tokens = shlex.split(_resume_line(surface, "approve"))
    ns = _trial_parser().parse_args(tokens[1:])

    captured: dict = {}

    def _fake_resume_trial(*, trial_id, verdict_file, verdict, runs_root, **kw):
        captured["verdict"] = verdict
        captured["verdict_file"] = verdict_file
        return {"status": "paused-at-gate", "paused_gate": "G2C"}

    monkeypatch.setattr(trial_cli, "resume_trial", _fake_resume_trial)
    rc = resume_trial_cli(ns)

    assert rc == 0
    assert captured["verdict_file"] is None  # inline path, not file
    v = captured["verdict"]
    assert isinstance(v, OperatorVerdict)
    assert v.gate_id == "G2B" and v.verb == "approve"
    assert str(v.card_id) == card_id and v.decision_card_digest == digest


def test_resume_cli_rejects_both_file_and_inline(tmp_path: Path) -> None:
    parser = _trial_parser()
    ns = parser.parse_args(
        [
            "resume",
            "--trial-id",
            str(uuid4()),
            "--verdict-file",
            str(tmp_path / "v.json"),
            "--gate-id",
            "G1",
            "--verb",
            "approve",
            "--card-id",
            str(uuid4()),
            "--decision-card-digest",
            "a" * 64,
            "--operator-id",
            "juanl",
        ]
    )
    assert resume_trial_cli(ns) == 2  # mutually exclusive


def test_resume_cli_missing_inline_flag_exits_2() -> None:
    parser = _trial_parser()
    ns = parser.parse_args(
        ["resume", "--trial-id", str(uuid4()), "--gate-id", "G1", "--verb", "approve"]
    )
    assert resume_trial_cli(ns) == 2  # incomplete inline verdict


def test_resume_cli_edit_verb_without_payload_exits_2_not_traceback(
    monkeypatch,
) -> None:
    """F-E2E-1 review SHOULD-2: an invalid inline verdict (edit w/o payload)
    surfaces as a clean exit-2, not a raw pydantic traceback."""
    parser = _trial_parser()
    ns = parser.parse_args(
        [
            "resume",
            "--trial-id",
            str(uuid4()),
            "--gate-id",
            "G1",
            "--verb",
            "edit",
            "--card-id",
            str(uuid4()),
            "--decision-card-digest",
            "a" * 64,
            "--operator-id",
            "juanl",
        ]
    )
    # resume_trial must NOT be reached (validation fails first)
    monkeypatch.setattr(
        trial_cli, "resume_trial", lambda **kw: pytest.fail("should not reach resume")
    )
    assert resume_trial_cli(ns) == 2


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
    # The neutral surface still emits the per-verb resume paste lines.
    env = _env("paused-at-gate", paused_gate="G1")
    surface = build_next_action(env, card_path=Path("does-not-exist.json"))
    approve = _resume_line(surface, "approve")
    assert approve.startswith("trial resume")
    assert "--gate-id G1" in surface
