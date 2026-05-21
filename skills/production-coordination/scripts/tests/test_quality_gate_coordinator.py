# /// script
# requires-python = ">=3.10"
# ///
"""Tests for quality_gate_coordinator.py."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import quality_gate_coordinator as qgc

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS production_runs (
    run_id TEXT PRIMARY KEY,
    purpose TEXT NOT NULL,
    status TEXT NOT NULL,
    preset TEXT NOT NULL,
    context_json TEXT,
    course_code TEXT,
    module_id TEXT,
    started_at TEXT,
    completed_at TEXT,
    created_at TEXT,
    updated_at TEXT
);

CREATE TABLE IF NOT EXISTS quality_gates (
    gate_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    stage TEXT NOT NULL,
    status TEXT NOT NULL,
    reviewer TEXT,
    findings_json TEXT,
    score REAL,
    decided_at TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS agent_coordination (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    action TEXT NOT NULL,
    payload_json TEXT,
    timestamp TEXT
);

CREATE TABLE IF NOT EXISTS observability_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    gate TEXT,
    run_mode TEXT NOT NULL,
    fidelity_o_count INTEGER,
    fidelity_i_count INTEGER,
    fidelity_a_count INTEGER,
    quality_scores_json TEXT,
    agent_metrics_json TEXT,
    payload_json TEXT,
    created_at TEXT NOT NULL
);
"""


class TempDB:
    def __init__(self) -> None:
        self._tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.path = Path(self._tmp.name)
        self._tmp.close()

    def __enter__(self) -> TempDB:
        conn = sqlite3.connect(str(self.path))
        conn.executescript(SCHEMA_SQL)
        conn.execute(
            """
            INSERT INTO production_runs
            (run_id, purpose, status, preset, context_json, course_code, module_id, started_at, created_at, updated_at)
            VALUES ('RUN-001', 'test', 'in-progress', 'production', '{}', 'C1', 'M1', '2026-01-01T00:00:00', '2026-01-01T00:00:00', '2026-01-01T00:00:00')
            """
        )
        conn.commit()
        conn.close()
        return self

    def __exit__(self, *args: object) -> None:
        self.path.unlink(missing_ok=True)


class TestQualityGateCoordinator(unittest.TestCase):
    def test_gate_pass_with_human_checkpoint(self) -> None:
        with TempDB() as db:
            result = qgc.evaluate_quality_gate(
                run_id="RUN-001",
                stage="creative-direction",
                reviewer_score=0.95,
                content="# Heading\nClear and concise content.",
                run_mode="default",
                decision_point=True,
                db_path=db.path,
            )
            self.assertEqual(result["decision"], "pass")
            self.assertEqual(result["workflow_action"], "human-checkpoint")
            self.assertTrue(result["quality_log"]["logged"])
            self.assertTrue(result["audit_log"]["logged"])

    def test_gate_override_path(self) -> None:
        with TempDB() as db:
            result = qgc.evaluate_quality_gate(
                run_id="RUN-001",
                stage="slide_generation",
                reviewer_score=0.1,
                content="Short content.",
                run_mode="default",
                override=True,
                override_reason="Creative judgment over threshold",
                db_path=db.path,
            )
            self.assertEqual(result["decision"], "override-pass")
            self.assertTrue(result["override_applied"])
            self.assertIn(result["workflow_action"], {"proceed", "human-checkpoint"})

    def test_ad_hoc_no_durable_persistence(self) -> None:
        with TempDB() as db:
            result = qgc.evaluate_quality_gate(
                run_id="RUN-001",
                stage="slide_generation",
                reviewer_score=0.9,
                content="Sandbox run text.",
                run_mode="ad-hoc",
                db_path=db.path,
            )
            self.assertFalse(result["quality_log"]["logged"])
            self.assertFalse(result["audit_log"]["logged"])

            conn = sqlite3.connect(str(db.path))
            quality_count = conn.execute("SELECT COUNT(*) FROM quality_gates").fetchone()[0]
            coord_count = conn.execute("SELECT COUNT(*) FROM agent_coordination").fetchone()[0]
            conn.close()

            self.assertEqual(quality_count, 0)
            self.assertEqual(coord_count, 0)

    def test_policy_load_error_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            invalid_policy = Path(td) / "tool_policies.yaml"
            invalid_policy.write_text("run_presets: [bad", encoding="utf-8")

            data, error = qgc._load_policies(invalid_policy)
            self.assertEqual(data, {})
            self.assertIsNotNone(error)


if __name__ == "__main__":
    unittest.main()
