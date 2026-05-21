# /// script
# requires-python = ">=3.10"
# ///
"""Tests for read-mode-state.py."""
from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "read-mode-state.py"


def create_test_db(db_path: Path) -> None:
    """Create a test coordination database with sample data."""
    conn = sqlite3.connect(str(db_path))
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS production_runs (
            run_id TEXT PRIMARY KEY, purpose TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending', preset TEXT NOT NULL DEFAULT 'draft',
            context_json TEXT, course_code TEXT, module_id TEXT,
            started_at TEXT NOT NULL DEFAULT (datetime('now')),
            completed_at TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS quality_gates (
            gate_id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL, stage TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending', reviewer TEXT,
            findings_json TEXT, score REAL, decided_at TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (run_id) REFERENCES production_runs(run_id)
        );
    """)
    conn.commit()
    conn.close()


def test_no_database(tmp_path: Path) -> None:
    """Script returns valid JSON when database doesn't exist."""
    db_path = tmp_path / "nonexistent.db"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--db-path", str(db_path)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
    data = json.loads(result.stdout)
    assert data["db_exists"] is False
    assert data["mode"] == "default"
    assert data["active_run"] is None


def test_empty_database(tmp_path: Path) -> None:
    """Script returns valid JSON for an empty database."""
    db_path = tmp_path / "coord.db"
    create_test_db(db_path)
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--db-path", str(db_path)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
    data = json.loads(result.stdout)
    assert data["db_exists"] is True
    assert data["active_run"] is None
    assert data["last_completed_run"] is None
    assert data["session"]["pending_gates"] == 0


def test_active_run(tmp_path: Path) -> None:
    """Script detects an active production run."""
    db_path = tmp_path / "coord.db"
    create_test_db(db_path)
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        "INSERT INTO production_runs (run_id, purpose, status, course_code, module_id) VALUES (?, ?, ?, ?, ?)",
        ("RUN-001", "lecture-slides", "in_progress", "PHARM101", "M2"),
    )
    conn.commit()
    conn.close()

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--db-path", str(db_path)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["active_run"] is not None
    assert data["active_run"]["run_id"] == "RUN-001"
    assert data["active_run"]["status"] == "in_progress"
    assert data["active_run"]["course_code"] == "PHARM101"


def test_completed_run(tmp_path: Path) -> None:
    """Script returns the most recent completed run."""
    db_path = tmp_path / "coord.db"
    create_test_db(db_path)
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        "INSERT INTO production_runs (run_id, purpose, status, completed_at) VALUES (?, ?, ?, ?)",
        ("RUN-DONE", "case-study", "completed", datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--db-path", str(db_path)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["last_completed_run"] is not None
    assert data["last_completed_run"]["run_id"] == "RUN-DONE"


def test_pending_gates(tmp_path: Path) -> None:
    """Script counts pending quality gates."""
    db_path = tmp_path / "coord.db"
    create_test_db(db_path)
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        "INSERT INTO production_runs (run_id, purpose, status) VALUES (?, ?, ?)",
        ("RUN-002", "assessment", "in_progress"),
    )
    conn.execute(
        "INSERT INTO quality_gates (run_id, stage, status) VALUES (?, ?, ?)",
        ("RUN-002", "review", "pending"),
    )
    conn.execute(
        "INSERT INTO quality_gates (run_id, stage, status) VALUES (?, ?, ?)",
        ("RUN-002", "checkpoint", "pending"),
    )
    conn.commit()
    conn.close()

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--db-path", str(db_path)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["session"]["pending_gates"] == 2


def test_mode_from_file(tmp_path: Path) -> None:
    """Script reads mode from mode_state.json when present."""
    db_path = tmp_path / "coordination.db"
    create_test_db(db_path)
    mode_file = tmp_path / "mode_state.json"
    mode_file.write_text(json.dumps({"mode": "ad-hoc", "switched_at": "2026-03-26T12:00:00"}))

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--db-path", str(db_path)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
    data = json.loads(result.stdout)
    assert data["mode"] == "ad-hoc", f"Expected ad-hoc, got {data['mode']}"


def test_mode_default_without_file(tmp_path: Path) -> None:
    """Script defaults to 'default' mode when mode_state.json is absent."""
    db_path = tmp_path / "coordination.db"
    create_test_db(db_path)

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--db-path", str(db_path)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["mode"] == "default"


def test_help_flag() -> None:
    """Script supports --help."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "coordination database" in result.stdout.lower()


if __name__ == "__main__":
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    tests = [test_no_database, test_empty_database, test_active_run, test_completed_run, test_pending_gates, test_mode_from_file, test_mode_default_without_file, test_help_flag]
    for test in tests:
        try:
            if test == test_help_flag:
                test()
            else:
                test_dir = tmp / test.__name__
                test_dir.mkdir(parents=True, exist_ok=True)
                test(test_dir)
            print(f"  PASS: {test.__name__}")
        except AssertionError as e:
            print(f"  FAIL: {test.__name__}: {e}")
