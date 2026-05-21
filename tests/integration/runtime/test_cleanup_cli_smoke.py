"""`python -m app.runtime.cleanup_threads --dry-run` CLI smoke (AC-1.5-D).

Runs the CLI against a reachable Postgres + asserts exit 0 + parses the
deletion-count line. Skips when DATABASE_URL unset or Postgres unreachable.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import psycopg
import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]


def _is_unreachable_error(exc: psycopg.OperationalError) -> bool:
    text = str(exc).lower()
    return any(
        marker in text
        for marker in (
            "connection refused",
            "could not connect",
            "connection timed out",
            "timeout expired",
        )
    )


def test_cleanup_cli_dry_run_exits_zero_and_prints_count() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        pytest.skip("DATABASE_URL not set; skipping CLI smoke.")

    # Early probe — if Postgres is unreachable we skip rather than run the subprocess
    try:
        with psycopg.connect(database_url, connect_timeout=3):
            pass
    except psycopg.OperationalError as exc:
        if _is_unreachable_error(exc):
            pytest.skip(f"Postgres unreachable: {exc}")
        raise

    result = subprocess.run(
        [sys.executable, "-m", "app.runtime.cleanup_threads", "--dry-run"],
        cwd=REPO_ROOT,
        env={**os.environ},
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, (
        f"CLI exited non-zero: {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "Retention policy:" in result.stdout
    assert "cleanup dry-run:" in result.stdout
    # Line shape: "cleanup dry-run: N thread(s) eligible."
    import re

    match = re.search(r"cleanup dry-run: (\d+) thread\(s\) eligible\.", result.stdout)
    assert match, f"expected deletion-count line in stdout; got: {result.stdout}"
    assert int(match.group(1)) >= 0
