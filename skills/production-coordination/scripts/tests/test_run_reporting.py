# /// script
# requires-python = ">=3.10"
# ///
"""Tests for run_reporting.py."""

from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import run_reporting

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

        context = {
            "mode": "default",
            "stages": [
                {
                    "stage": "draft",
                    "status": "approved",
                    "stage_started_at": "2026-01-01T00:00:00",
                    "stage_completed_at": "2026-01-01T00:10:00",
                },
                {
                    "stage": "review",
                    "status": "approved",
                    "stage_started_at": "2026-01-01T00:10:00",
                    "stage_completed_at": "2026-01-01T00:25:00",
                },
            ],
        }
        conn.execute(
            """
            INSERT INTO production_runs
            (run_id, purpose, status, preset, context_json, course_code, module_id, started_at, completed_at, created_at, updated_at)
            VALUES ('RUN-REP', 'report test', 'completed', 'production', ?, 'C1', 'M1', '2026-01-01T00:00:00', '2026-01-01T00:25:00', '2026-01-01T00:00:00', '2026-01-01T00:25:00')
            """,
            (json.dumps(context),),
        )
        conn.execute(
            """
            INSERT INTO production_runs
            (run_id, purpose, status, preset, context_json, course_code, module_id, started_at, completed_at, created_at, updated_at)
            VALUES ('RUN-BASE', 'baseline', 'completed', 'draft', '{"mode": "default"}', 'C1', 'M1', '2026-01-01T00:00:00', '2026-01-01T00:30:00', '2026-01-01T00:00:00', '2026-01-01T00:30:00')
            """
        )
        conn.execute(
            """
            INSERT INTO production_runs
            (run_id, purpose, status, preset, context_json, course_code, module_id, started_at, completed_at, created_at, updated_at)
            VALUES ('RUN-ADHOC', 'sandbox', 'completed', 'draft', '{"mode": "ad-hoc"}', 'C1', 'M1', '2026-01-01T00:00:00', '2026-01-01T00:05:00', '2026-01-01T00:00:00', '2026-01-01T00:05:00')
            """
        )

        conn.execute(
            """
            INSERT INTO quality_gates (run_id, stage, status, reviewer, score, decided_at, created_at)
            VALUES ('RUN-REP', 'review', 'pass', 'quinn-r', 0.95, '2026-01-01T00:24:00', '2026-01-01T00:24:00')
            """
        )
        conn.execute(
            """
            INSERT INTO agent_coordination (run_id, agent_name, action, payload_json, timestamp)
            VALUES ('RUN-REP', 'gamma-specialist', 'completed', '{}', '2026-01-01T00:20:00')
            """
        )
        conn.execute(
            """
            INSERT INTO observability_events
            (run_id, event_type, gate, run_mode, fidelity_o_count, fidelity_i_count, fidelity_a_count, quality_scores_json, agent_metrics_json, payload_json, created_at)
            VALUES ('RUN-REP', 'gate_result', 'review', 'default', 0, 0, 0, '{"reviewer": 0.95}', '{}', '{"passed": true}', '2026-01-01T00:24:00')
            """
        )

        conn.commit()
        conn.close()
        return self

    def __exit__(self, *args: object) -> None:
        self.path.unlink(missing_ok=True)


class TestRunReporting(unittest.TestCase):
    def test_generate_report(self) -> None:
        with TempDB() as db:
            report = run_reporting.generate_run_report(
                run_id="RUN-REP",
                db_path=db.path,
                write_report=False,
                capture_learning=False,
            )
            self.assertEqual(report["run_id"], "RUN-REP")
            self.assertEqual(report["status"], "completed")
            self.assertGreater(len(report["stage_metrics"]), 0)
            self.assertGreaterEqual(report["quality_gate_results"]["count"], 1)
            self.assertTrue(report["comparative_analysis"]["ad_hoc_excluded"])
            self.assertEqual(report["comparative_analysis"]["baseline_count"], 1)

    def test_capture_learning_handles_empty_lists(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            report = {
                "run_id": "RUN-EMPTY",
                "bottlenecks": [],
                "observability": {},
                "optimization_recommendations": [],
            }

            with patch.object(run_reporting, "project_root", return_value=Path(td)):
                with patch.object(
                    run_reporting,
                    "enforce_ad_hoc_boundary",
                    return_value={"allowed": True, "code": "ALLOWED_DEFAULT_MODE", "reason": "ok"},
                ):
                    result = run_reporting._capture_learning_insights(report, "default")

            self.assertTrue(result["captured"])
            target = Path(result["path"])
            self.assertTrue(target.exists())
            contents = target.read_text(encoding="utf-8")
            self.assertIn("Longest stage: n/a", contents)
            self.assertIn("Recommendation: n/a", contents)

    def test_observability_summary_includes_error_detail_on_failure(self) -> None:
        """Low-risk logging: failed observability import/summary must be diagnosable."""

        def _boom(*_a: object, **_k: object) -> None:
            raise RuntimeError("simulated observability failure")

        fake_obs = types.ModuleType("observability_hooks")
        fake_obs.summarize_run = _boom

        with patch.dict(sys.modules, {"observability_hooks": fake_obs}):
            with self.assertLogs("run_reporting", level="WARNING") as cm:
                summary = run_reporting._observability_summary("RUN-X", db_path=None)

        self.assertEqual(summary["error"], "observability summary unavailable")
        self.assertEqual(summary["observability_error_type"], "RuntimeError")
        self.assertIn("simulated observability failure", summary["observability_error_message"])
        self.assertTrue(any("Observability summary failed" in r.getMessage() for r in cm.records))

    def test_generate_report_handles_mixed_timezone_timestamps(self) -> None:
        with TempDB() as db:
            conn = sqlite3.connect(str(db.path))
            conn.execute(
                """
                UPDATE production_runs
                SET started_at = '2026-01-01T00:00:00+00:00',
                    completed_at = '2026-01-01T00:25:00'
                WHERE run_id = 'RUN-REP'
                """
            )
            conn.commit()
            conn.close()

            report = run_reporting.generate_run_report(
                run_id="RUN-REP",
                db_path=db.path,
                write_report=False,
                capture_learning=False,
            )

            self.assertEqual(report["total_duration_seconds"], 1500.0)


class TestDoubleDispatchReporting(unittest.TestCase):
    """Story 12.5: double_dispatch flag appears in run reports."""

    def _make_db_with_context(self, context: dict) -> TempDB:
        """Create a TempDB with a single run using custom context."""
        db = TempDB()
        conn = sqlite3.connect(str(db.path))
        conn.executescript(SCHEMA_SQL)
        conn.execute(
            """
            INSERT INTO production_runs
            (run_id, purpose, status, preset, context_json, course_code, module_id,
             started_at, completed_at, created_at, updated_at)
            VALUES ('RUN-DD', 'dd test', 'completed', 'production', ?, 'C1', 'M1',
                    '2026-01-01T00:00:00', '2026-01-01T00:25:00',
                    '2026-01-01T00:00:00', '2026-01-01T00:25:00')
            """,
            (json.dumps(context),),
        )
        conn.commit()
        conn.close()
        return db

    def test_report_includes_double_dispatch_true(self) -> None:
        context = {
            "mode": "default",
            "double_dispatch": True,
            "stages": [
                {
                    "stage": "slides",
                    "status": "approved",
                    "stage_started_at": "2026-01-01T00:00:00",
                    "stage_completed_at": "2026-01-01T00:10:00",
                },
            ],
        }
        db = self._make_db_with_context(context)
        try:
            report = run_reporting.generate_run_report(
                run_id="RUN-DD", db_path=db.path,
                write_report=False, capture_learning=False,
            )
            self.assertTrue(report["double_dispatch"])
            self.assertIn("cost_estimation", report)
            self.assertEqual(report["cost_estimation"]["gamma_call_multiplier"], 2)
        finally:
            db.path.unlink(missing_ok=True)


class TestMotionReporting(unittest.TestCase):
    def test_report_includes_motion_metrics_when_motion_enabled(self) -> None:
        with TempDB() as db, tempfile.TemporaryDirectory() as td:
            motion_plan = Path(td) / "motion_plan.yaml"
            motion_plan.write_text(
                """
slides:
  - slide_id: slide-01
    motion_type: static
  - slide_id: slide-02
    motion_type: video
    motion_status: approved
    motion_duration_seconds: 5.0
    estimated_credits: 8.0
  - slide_id: slide-03
    motion_type: animation
    motion_status: imported
    motion_duration_seconds: 7.0
""".strip()
                + "\n",
                encoding="utf-8",
            )
            context = {
                "mode": "default",
                "motion_enabled": True,
                "context_paths": {"motion_plan": str(motion_plan)},
                "stages": [
                    {
                        "stage": "motion-generation",
                        "status": "approved",
                        "stage_started_at": "2026-01-01T00:00:00",
                        "stage_completed_at": "2026-01-01T00:10:00",
                    },
                ],
            }

            conn = sqlite3.connect(str(db.path))
            conn.execute("DELETE FROM production_runs WHERE run_id = 'RUN-REP'")
            conn.execute(
                """
                INSERT INTO production_runs
                (run_id, purpose, status, preset, context_json, course_code, module_id, started_at, completed_at, created_at, updated_at)
                VALUES ('RUN-REP', 'motion report test', 'completed', 'production', ?, 'C1', 'M1', '2026-01-01T00:00:00', '2026-01-01T00:25:00', '2026-01-01T00:00:00', '2026-01-01T00:25:00')
                """,
                (json.dumps(context),),
            )
            conn.commit()
            conn.close()

            report = run_reporting.generate_run_report(
                run_id="RUN-REP",
                db_path=db.path,
                write_report=False,
                capture_learning=False,
            )

            assert report["motion_enabled"] is True
            assert report["motion_metrics"]["clips_generated"] == 1
            assert report["motion_metrics"]["animations_imported"] == 1
            assert report["motion_metrics"]["total_motion_duration_seconds"] == 12.0
            assert report["motion_metrics"]["kling_credits_consumed"] == 8.0

    def test_report_includes_double_dispatch_false(self) -> None:
        context = {
            "mode": "default",
            "stages": [
                {
                    "stage": "slides",
                    "status": "approved",
                    "stage_started_at": "2026-01-01T00:00:00",
                    "stage_completed_at": "2026-01-01T00:10:00",
                },
            ],
        }
        db = TempDB()
        conn = sqlite3.connect(str(db.path))
        conn.executescript(SCHEMA_SQL)
        conn.execute(
            """
            INSERT INTO production_runs
            (run_id, purpose, status, preset, context_json, course_code, module_id,
             started_at, completed_at, created_at, updated_at)
            VALUES ('RUN-DD', 'dd test', 'completed', 'production', ?, 'C1', 'M1',
                    '2026-01-01T00:00:00', '2026-01-01T00:25:00',
                    '2026-01-01T00:00:00', '2026-01-01T00:25:00')
            """,
            (json.dumps(context),),
        )
        conn.commit()
        conn.close()
        try:
            report = run_reporting.generate_run_report(
                run_id="RUN-DD", db_path=db.path,
                write_report=False, capture_learning=False,
            )
            self.assertFalse(report["double_dispatch"])
            self.assertNotIn("cost_estimation", report)
        finally:
            db.path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
