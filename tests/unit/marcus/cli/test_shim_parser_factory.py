"""Shared shim parser factory tests (Story 7a.7, AC-7.7-E)."""

from __future__ import annotations

from pathlib import Path
from uuid import UUID, uuid4

import pytest

from app.marcus.cli.gate_shims._shim_parser import (
    ACTIVE_TERMINAL_GATES,
    build_shim_parser,
)


def test_active_terminal_gates_canonical_inventory() -> None:
    # Arc 2 (2026-06-18): G2B (variant) + G4A (voice) woken HIL gates added —
    # the operator drives their verdict through the same single-decision shim.
    # G0-S2 (2026-06-26): +G0E source-enrichment confirm-gate #1.
    assert ACTIVE_TERMINAL_GATES == ("G0E", "G1", "G2B", "G2C", "G3", "G4A", "G4")


@pytest.mark.parametrize("gate_id", list(ACTIVE_TERMINAL_GATES))
def test_factory_builds_parser_with_all_required_args(gate_id: str) -> None:
    parser = build_shim_parser(gate_id)
    trial_id = uuid4()
    args = parser.parse_args(
        [
            "--trial-id",
            str(trial_id),
            "--verdict-file",
            "/tmp/verdict.json",
            "--operator-id",
            "juanl",
        ]
    )
    assert isinstance(args.trial_id, UUID)
    assert args.trial_id == trial_id
    assert args.verdict_file == Path("/tmp/verdict.json")
    assert args.operator_id == "juanl"
    assert args.runs_root is None


def test_factory_help_text_carries_four_named_sections() -> None:
    parser = build_shim_parser("G1")
    help_text = parser.format_help()
    assert "OPERATOR\n========" in help_text
    assert "INPUTS\n======" in help_text
    assert "OUTPUTS\n=======" in help_text
    assert "REFERENCE\n=========" in help_text


def test_factory_rejects_unknown_gate_id() -> None:
    with pytest.raises(ValueError, match="unknown gate_id"):
        build_shim_parser("G99")


def test_factory_trial_id_parses_as_uuid() -> None:
    parser = build_shim_parser("G2C")
    bad = parser.parse_args(["--trial-id", str(uuid4()), "--verdict-file", "x"])
    assert isinstance(bad.trial_id, UUID)


def test_factory_verdict_file_parses_as_path() -> None:
    parser = build_shim_parser("G3")
    args = parser.parse_args(["--trial-id", str(uuid4()), "--verdict-file", "x.json"])
    assert isinstance(args.verdict_file, Path)
