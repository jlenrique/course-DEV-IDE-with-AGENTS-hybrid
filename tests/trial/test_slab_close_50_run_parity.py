from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.utilities.run_slab_close_50_run_parity import (
    LEDGER_MARKER,
    append_ledger_entry,
    build_ledger_entry,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
WRAPPER = REPO_ROOT / "scripts" / "utilities" / "run_slab_close_50_run_parity.py"


def test_slab_close_parity_wrapper_reports_not_fired() -> None:
    completed = subprocess.run(
        [sys.executable, str(WRAPPER), "--run-count", "2", "--no-ledger"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)

    assert result["tripwire_id"] == "TW-7c-6"
    assert result["run_count"] == 2
    assert result["cell_count"] == 68
    assert result["fired_verdict"] == "not_fired"
    assert result["failed_cells"] == []


def test_slab_close_parity_ledger_append_is_idempotent(tmp_path: Path) -> None:
    sprint_status = tmp_path / "sprint-status.yaml"
    sprint_status.write_text(
        "tripwire_events:\n"
        "\n"
        "# =============================================================================\n"
        "# DEVELOPMENT PLAN:\n",
        encoding="utf-8",
    )
    entry = build_ledger_entry(
        {
            "fired_verdict": "not_fired",
            "run_count": 50,
            "cell_count": 68,
            "failed_cells": [],
            "budgets": {"pre_7c": 0.001, "slab_7c_added": 0.0005},
        }
    )

    assert append_ledger_entry(sprint_status, entry) == "appended"
    first = sprint_status.read_text(encoding="utf-8")
    assert LEDGER_MARKER in first
    assert "tripwire_id: TW-7c-6" in first

    assert append_ledger_entry(sprint_status, entry) == "already_recorded"
    assert sprint_status.read_text(encoding="utf-8") == first
