"""`python -m app.runtime.cleanup_threads --dry-run` with bad DATABASE_URL (AC-1.5-D).

Runs the CLI with a deliberately-bad `DATABASE_URL` override + asserts exit 1
with a named-error stderr line. Per Murat's amendment 2026-04-22, this test
validates the CLI's `exit 1` failure-surface behavior only when the TEST
ENVIRONMENT has `DATABASE_URL` set — the test itself skips when `DATABASE_URL`
is unset (sandbox-AC discipline: we only exercise the failure surface when
the happy path is reachable-but-credentials-bad, not unreachable).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_cleanup_cli_exits_one_on_bad_database_url() -> None:
    if not os.environ.get("DATABASE_URL"):
        pytest.skip("DATABASE_URL not set; exit-1 surface only validated on reachable envs.")

    # Deliberately bad credentials in a structurally valid URL shape
    env = {**os.environ, "DATABASE_URL": "postgresql://baduser:badpass@localhost:5432/nodb_xyz"}
    result = subprocess.run(
        [sys.executable, "-m", "app.runtime.cleanup_threads", "--dry-run"],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 1, (
        f"expected CLI exit=1 for bad DATABASE_URL, got {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "ERROR:" in result.stderr, f"expected named error in stderr, got: {result.stderr}"
