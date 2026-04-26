# /// script
# requires-python = ">=3.10"
# ///
"""Tests for deployment_coordinator.py."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import deployment_coordinator as dc

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

CREATE TABLE IF NOT EXISTS deployment_events (
    deployment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    platform TEXT NOT NULL,
    status TEXT NOT NULL,
    details_json TEXT,
    deployed_at TEXT
);

CREATE TABLE IF NOT EXISTS agent_coordination (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    action TEXT NOT NULL,
    payload_json TEXT,
    timestamp TEXT
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
            VALUES ('RUN-DEP', 'deploy test', 'completed', 'production', '{}', 'C1', 'M1', '2026-01-01T00:00:00', '2026-01-01T00:00:00', '2026-01-01T00:00:00')
            """
        )
        conn.commit()
        conn.close()
        return self

    def __exit__(self, *args: object) -> None:
        self.path.unlink(missing_ok=True)


class TestDeploymentCoordinator(unittest.TestCase):
    def test_deploy_default_mode_persists(self) -> None:
        with TempDB() as db, tempfile.TemporaryDirectory() as td:
            asset = Path(td) / "module.md"
            asset.write_text("# Module\nAccessible content", encoding="utf-8")

            result = dc.deploy_content(
                run_id="RUN-DEP",
                platform="Canvas",
                artifact_paths=[str(asset)],
                run_mode="default",
                db_path=db.path,
            )
            self.assertEqual(result["status"], "deployed")
            self.assertTrue(result["persisted"])

            conn = sqlite3.connect(str(db.path))
            event_count = conn.execute("SELECT COUNT(*) FROM deployment_events").fetchone()[0]
            run_status = conn.execute("SELECT status FROM production_runs WHERE run_id = 'RUN-DEP'").fetchone()[0]
            conn.close()

            self.assertEqual(event_count, 1)
            self.assertEqual(run_status, "deployed")

    def test_deploy_ad_hoc_mode_no_persistence(self) -> None:
        with TempDB() as db, tempfile.TemporaryDirectory() as td:
            asset = Path(td) / "module.md"
            asset.write_text("# Sandbox\nAccessible content", encoding="utf-8")

            result = dc.deploy_content(
                run_id="RUN-DEP",
                platform="Canvas",
                artifact_paths=[str(asset)],
                run_mode="ad-hoc",
                db_path=db.path,
            )
            self.assertEqual(result["status"], "deployed-simulated")
            self.assertFalse(result["persisted"])

            conn = sqlite3.connect(str(db.path))
            event_count = conn.execute("SELECT COUNT(*) FROM deployment_events").fetchone()[0]
            conn.close()

            self.assertEqual(event_count, 0)

    def test_deploy_unknown_run_blocked(self) -> None:
        with TempDB() as db, tempfile.TemporaryDirectory() as td:
            asset = Path(td) / "module.md"
            asset.write_text("# Module\nAccessible content", encoding="utf-8")

            result = dc.deploy_content(
                run_id="RUN-UNKNOWN",
                platform="Canvas",
                artifact_paths=[str(asset)],
                run_mode="default",
                db_path=db.path,
            )
            self.assertEqual(result["status"], "blocked")
            self.assertIn("Run not found", result["reason"])

    def test_deploy_requires_checkable_accessibility_artifacts(self) -> None:
        with TempDB() as db, tempfile.TemporaryDirectory() as td:
            asset = Path(td) / "module.png"
            asset.write_bytes(b"fakepng")

            result = dc.deploy_content(
                run_id="RUN-DEP",
                platform="Canvas",
                artifact_paths=[str(asset)],
                run_mode="default",
                db_path=db.path,
            )
            self.assertEqual(result["status"], "blocked")
            self.assertIn("requires at least one checkable text artifact", result["reason"])
            self.assertEqual(result["accessibility"]["skipped_count"], 1)
            self.assertEqual(
                result["accessibility"]["skipped_artifacts"][0]["reason"],
                "unsupported_extension",
            )


if __name__ == "__main__":
    unittest.main()
