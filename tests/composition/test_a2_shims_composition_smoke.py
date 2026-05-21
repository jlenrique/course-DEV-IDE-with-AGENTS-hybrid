"""CI wrapper for A2 shims Composition Smoke (Story 7a.7, AC-7.7-C)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SMOKE_SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "_bmad-output"
    / "implementation-artifacts"
    / "migration-7-7-a2-shims-composition-smoke.py"
)


def test_a2_shims_composition_smoke_script_exists() -> None:
    assert SMOKE_SCRIPT.exists(), f"missing {SMOKE_SCRIPT}"


def test_a2_shims_composition_smoke_script_passes() -> None:
    result = subprocess.run(
        [sys.executable, str(SMOKE_SCRIPT)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"smoke exit={result.returncode}; stdout={result.stdout!r}; stderr={result.stderr!r}"
    )
    assert "PASS slab-7a A2-shims composition smoke" in result.stdout
