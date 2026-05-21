from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_cascade_config_validate_cli_exits_zero() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "app.runtime.cascade_config", "validate"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, (
        f"expected exit 0, got {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "PASS: cascade + pricing validated" in result.stdout
    assert "cascade_digest=" in result.stdout
    assert "pricing_digest=" in result.stdout
