"""Tests for quality_logger.py."""

import importlib.util
import json
import sqlite3
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "quality_logger",
    Path(__file__).resolve().parent.parent / "quality_logger.py",
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


SCHEMA = """
CREATE TABLE IF NOT EXISTS quality_gates (
    gate_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id         TEXT NOT NULL,
    stage          TEXT NOT NULL,
    status         TEXT NOT NULL DEFAULT 'pending',
    reviewer       TEXT,
    findings_json  TEXT,
    score          REAL,
    decided_at     TEXT,
    created_at     TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


def _create_test_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "test_coordination.db"
    conn = sqlite3.connect(str(db_path))
    conn.executescript(SCHEMA)
    conn.close()
    return db_path


class TestLogQualityResult:
    def test_default_mode_persists(self, tmp_path):
        db_path = _create_test_db(tmp_path)
        result = mod.log_quality_result(
            run_id="test-run-001",
            stage="content-review",
            status="pass",
            reviewer="quinn-r",
            findings=[{"severity": "low", "description": "minor typo"}],
            score=0.95,
            run_mode="default",
            db_path=db_path,
        )
        assert result["logged"] is True
        assert "gate_id" in result

        conn = sqlite3.connect(str(db_path))
        row = conn.execute("SELECT * FROM quality_gates WHERE run_id = 'test-run-001'").fetchone()
        conn.close()
        assert row is not None

    def test_adhoc_mode_suppresses(self):
        result = mod.log_quality_result(
            run_id="test-run-002",
            stage="slide-review",
            status="fail",
            reviewer="quinn-r",
            findings=[{"severity": "critical", "description": "heading skip"}],
            score=0.3,
            run_mode="ad-hoc",
        )
        assert result["logged"] is False
        assert "ad-hoc" in result["reason"]
        assert result["record"]["run_id"] == "test-run-002"

    def test_missing_db_returns_not_logged(self):
        result = mod.log_quality_result(
            run_id="test-run-003",
            stage="review",
            status="pass",
            reviewer="quinn-r",
            findings=[],
            score=1.0,
            run_mode="default",
            db_path=Path("/nonexistent/db.sqlite"),
        )
        assert result["logged"] is False
        assert "not found" in result["reason"]

    def test_findings_stored_as_json(self, tmp_path):
        db_path = _create_test_db(tmp_path)
        findings = [
            {"severity": "high", "description": "brand violation"},
            {"severity": "medium", "description": "tone mismatch"},
        ]
        mod.log_quality_result(
            run_id="test-run-004",
            stage="brand-review",
            status="fail",
            reviewer="quinn-r",
            findings=findings,
            score=0.6,
            run_mode="default",
            db_path=db_path,
        )

        conn = sqlite3.connect(str(db_path))
        row = conn.execute("SELECT findings_json FROM quality_gates WHERE run_id = 'test-run-004'").fetchone()
        conn.close()
        stored = json.loads(row[0])
        assert len(stored) == 2
        assert stored[0]["severity"] == "high"
