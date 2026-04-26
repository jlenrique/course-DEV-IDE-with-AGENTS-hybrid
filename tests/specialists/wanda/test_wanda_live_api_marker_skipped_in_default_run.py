from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
LIVE_TEST = "tests/specialists/wanda/test_wanda_live_api_artifact.py"


def _collect(*extra: str) -> subprocess.CompletedProcess[str]:
    # Clear inherited addopts so a developer shell cannot accidentally opt into live tests.
    clean_env = {key: value for key, value in os.environ.items() if key != "PYTEST_ADDOPTS"}
    clean_env["PYTEST_ADDOPTS"] = ""
    return subprocess.run(
        [sys.executable, "-m", "pytest", LIVE_TEST, "--collect-only", "-q", *extra],
        capture_output=True,
        text=True,
        env=clean_env,
        cwd=str(REPO_ROOT),
        check=False,
    )


def _deselected_count(output: str) -> int:
    matches = re.findall(r"(\d+) deselected", output)
    return int(matches[-1]) if matches else 0


def _collected_count(output: str) -> int:
    matches = re.findall(r"(\d+) tests? collected", output)
    return int(matches[-1]) if matches else 0


def test_default_run_deselects_live_api() -> None:
    result = _collect()
    output = result.stdout + result.stderr
    assert result.returncode == 5
    assert _deselected_count(output) == 1


def test_run_live_collects_live_api() -> None:
    result = _collect("--run-live")
    output = result.stdout + result.stderr
    assert result.returncode == 0
    assert _collected_count(output) == 1
    assert _deselected_count(output) == 0
