from __future__ import annotations

from pathlib import Path

import yaml

from app.manifest.gate_fold_manifest_emit import (
    DEFAULT_MANIFEST_PATH,
    emit_gate_fold_manifest,
    gate_fold_entries,
)
from app.manifest.loader import load

EXPECTED = {
    "G0": ("fold_with", "G1"),
    "G0A": ("fold_with", "G1"),
    "G0B": ("fold_with", "G1"),
    "G0E": ("pause_point", None),  # G0-S2 (2026-06-26): confirm-gate #1 (surfaced)
    "G1": ("pause_point", None),
    "G1A": ("fold_with", "G2C"),
    "G2": ("fold_with", "G2C"),
    "G1.5": ("fold_with", "G2C"),
    "G2.5": ("fold_with", "G2C"),
    "G2B": ("pause_point", None),  # Arc 2 (2026-06-18): woken
    "G2C": ("pause_point", None),
    "G2M": ("fold_with", "G2C"),
    "G2F": ("fold_with", "G3"),
    "G3B": ("fold_with", "G3"),
    "G3": ("pause_point", None),
    "G4": ("pause_point", None),
    "G4A": ("pause_point", None),  # Arc 2 (2026-06-18): woken
    "G4B": ("fold_with", "G4"),
    "G5": ("fold_with", "G4"),
}


def test_emit_live_manifest_produces_expected_mapping(tmp_path: Path) -> None:
    output = tmp_path / "gate_fold_manifest.yaml"

    emit_gate_fold_manifest(DEFAULT_MANIFEST_PATH, output)
    payload = yaml.safe_load(output.read_text(encoding="utf-8"))
    actual = {
        entry["code"]: (entry["mechanism"], entry["fold_target"])
        for entry in payload["gates"]
    }

    assert actual == EXPECTED


def test_emit_is_byte_stable(tmp_path: Path) -> None:
    first = tmp_path / "first.yaml"
    second = tmp_path / "second.yaml"

    emit_gate_fold_manifest(DEFAULT_MANIFEST_PATH, first)
    emit_gate_fold_manifest(DEFAULT_MANIFEST_PATH, second)

    assert first.read_bytes() == second.read_bytes()


def test_emit_lists_all_declared_gate_codes(tmp_path: Path) -> None:
    output = tmp_path / "gate_fold_manifest.yaml"

    emit_gate_fold_manifest(DEFAULT_MANIFEST_PATH, output)
    text = output.read_text(encoding="utf-8")

    assert text.count("- code:") == 19  # +G0E (G0-S2 confirm-gate #1)


def test_gate_fold_entries_have_non_null_mechanisms() -> None:
    manifest = load(DEFAULT_MANIFEST_PATH)

    assert all(entry["mechanism"] for entry in gate_fold_entries(manifest))
