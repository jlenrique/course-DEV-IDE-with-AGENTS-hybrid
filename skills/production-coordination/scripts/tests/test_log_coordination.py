# /// script
# requires-python = ">=3.10"
# ///
"""Tests for log_coordination.py — agent coordination event logging."""
from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import log_coordination

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS production_runs (
    run_id TEXT PRIMARY KEY, purpose TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending',
    preset TEXT NOT NULL DEFAULT 'draft', context_json TEXT, course_code TEXT, module_id TEXT,
    started_at TEXT, completed_at TEXT, created_at TEXT, updated_at TEXT
);
CREATE TABLE IF NOT EXISTS agent_coordination (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL, agent_name TEXT NOT NULL,
    action TEXT NOT NULL, payload_json TEXT, timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (run_id) REFERENCES production_runs(run_id)
);
CREATE TABLE IF NOT EXISTS quality_gates (
    gate_id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL, stage TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending', reviewer TEXT, findings_json TEXT, score REAL,
    decided_at TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (run_id) REFERENCES production_runs(run_id)
);
"""


class TempDB:
    def __init__(self) -> None:
        self._tmpfile = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.path = self._tmpfile.name
        self._tmpfile.close()

    def __enter__(self) -> TempDB:
        conn = sqlite3.connect(self.path)
        conn.executescript(SCHEMA_SQL)
        conn.commit()
        conn.close()
        return self

    def __exit__(self, *args: object) -> None:
        try:
            Path(self.path).unlink(missing_ok=True)
        except OSError:
            pass


class TestLogEvent(unittest.TestCase):
    def test_log_basic(self) -> None:
        with TempDB() as db:
            args = log_coordination.build_parser().parse_args([
                "--db", db.path, "log",
                "--run-id", "RUN-001", "--agent", "gamma-specialist",
                "--action", "delegated", "--run-mode", "default",
            ])
            result = log_coordination.cmd_log(args)
            self.assertEqual(result["run_id"], "RUN-001")
            self.assertEqual(result["agent"], "gamma-specialist")
            self.assertEqual(result["action"], "delegated")
            self.assertIn("event_id", result)

    def test_log_with_payload(self) -> None:
        with TempDB() as db:
            payload = json.dumps({"content_type": "slides", "module": "M2"})
            args = log_coordination.build_parser().parse_args([
                "--db", db.path, "log",
                "--run-id", "RUN-001", "--agent", "gamma-specialist",
                "--action", "delegated", "--payload", payload, "--run-mode", "default",
            ])
            result = log_coordination.cmd_log(args)
            self.assertIn("event_id", result)

    def test_log_multiple_events(self) -> None:
        with TempDB() as db:
            for action in ["delegated", "working", "completed"]:
                args = log_coordination.build_parser().parse_args([
                    "--db", db.path, "log",
                    "--run-id", "RUN-001", "--agent", "gamma-specialist",
                    "--action", action, "--run-mode", "default",
                ])
                log_coordination.cmd_log(args)

            hist_args = log_coordination.build_parser().parse_args(["--db", db.path, "history", "RUN-001"])
            result = log_coordination.cmd_history(hist_args)
            self.assertEqual(result["count"], 3)

    def test_log_ad_hoc_is_noop(self) -> None:
        with TempDB() as db:
            args = log_coordination.build_parser().parse_args([
                "--db", db.path, "log",
                "--run-id", "RUN-001", "--agent", "gamma-specialist",
                "--action", "delegated", "--run-mode", "ad-hoc",
            ])
            result = log_coordination.cmd_log(args)
            self.assertFalse(result["logged"])
            self.assertEqual(result["code"], "NOOP_AD_HOC")

            conn = sqlite3.connect(db.path)
            count = conn.execute("SELECT COUNT(*) FROM agent_coordination").fetchone()[0]
            conn.close()
            self.assertEqual(count, 0)


class TestHistory(unittest.TestCase):
    def test_history_empty(self) -> None:
        with TempDB() as db:
            args = log_coordination.build_parser().parse_args(["--db", db.path, "history", "EMPTY-RUN"])
            result = log_coordination.cmd_history(args)
            self.assertEqual(result["count"], 0)
            self.assertEqual(result["events"], [])

    def test_history_returns_ordered(self) -> None:
        with TempDB() as db:
            for agent in ["content-creator", "gamma-specialist", "quality-reviewer"]:
                args = log_coordination.build_parser().parse_args([
                    "--db", db.path, "log",
                    "--run-id", "RUN-002", "--agent", agent, "--action", "delegated", "--run-mode", "default",
                ])
                log_coordination.cmd_log(args)

            hist_args = log_coordination.build_parser().parse_args(["--db", db.path, "history", "RUN-002"])
            result = log_coordination.cmd_history(hist_args)
            agents = [e["agent"] for e in result["events"]]
            self.assertEqual(agents, ["content-creator", "gamma-specialist", "quality-reviewer"])

    def test_history_parses_payload(self) -> None:
        with TempDB() as db:
            payload = json.dumps({"status": "completed", "score": 0.9})
            args = log_coordination.build_parser().parse_args([
                "--db", db.path, "log",
                "--run-id", "RUN-003", "--agent", "quality-reviewer",
                "--action", "completed", "--payload", payload, "--run-mode", "default",
            ])
            log_coordination.cmd_log(args)

            hist_args = log_coordination.build_parser().parse_args(["--db", db.path, "history", "RUN-003"])
            result = log_coordination.cmd_history(hist_args)
            self.assertEqual(result["events"][0]["payload"]["score"], 0.9)


if __name__ == "__main__":
    unittest.main()
