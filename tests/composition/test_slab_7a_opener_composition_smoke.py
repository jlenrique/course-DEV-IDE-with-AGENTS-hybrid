"""CI wrapper for the Slab 7a slab-opener Composition Smoke gate (Story 7a.1, AC-7.1-F)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SMOKE_SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "_bmad-output"
    / "implementation-artifacts"
    / "migration-7-1-directive-composer-composition-smoke.py"
)


def test_composition_smoke_script_exists() -> None:
    assert SMOKE_SCRIPT.exists(), (
        f"missing slab-7a Composition Smoke script at {SMOKE_SCRIPT}"
    )


def test_composition_smoke_script_passes() -> None:
    """Smoke script exits 0 and stdout carries the PASS marker line."""
    result = subprocess.run(
        [sys.executable, str(SMOKE_SCRIPT)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"smoke script exit={result.returncode}; "
        f"stdout={result.stdout!r}; stderr={result.stderr!r}"
    )
    assert "PASS slab-7a-opener composition smoke" in result.stdout, (
        f"PASS marker absent from stdout: {result.stdout!r}"
    )
