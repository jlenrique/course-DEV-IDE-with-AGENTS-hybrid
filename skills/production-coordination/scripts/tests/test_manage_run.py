# /// script
# requires-python = ">=3.10"
# ///
"""Tests for manage_run.py — production run lifecycle management.

Self-contained: can run directly with `python test_manage_run.py`.
Uses temporary in-memory SQLite databases.
"""
from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import manage_run

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS production_runs (
    run_id         TEXT PRIMARY KEY,
    purpose        TEXT NOT NULL,
    status         TEXT NOT NULL DEFAULT 'pending',
    preset         TEXT NOT NULL DEFAULT 'draft',
    context_json   TEXT,
    course_code    TEXT,
    module_id      TEXT,
    started_at     TEXT NOT NULL DEFAULT (datetime('now')),
    completed_at   TEXT,
    created_at     TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at     TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS agent_coordination (
    event_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id         TEXT NOT NULL,
    agent_name     TEXT NOT NULL,
    action         TEXT NOT NULL,
    payload_json   TEXT,
    timestamp      TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (run_id) REFERENCES production_runs(run_id)
);

CREATE TABLE IF NOT EXISTS quality_gates (
    gate_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id         TEXT NOT NULL,
    stage          TEXT NOT NULL,
    status         TEXT NOT NULL DEFAULT 'pending',
    reviewer       TEXT,
    findings_json  TEXT,
    score          REAL,
    decided_at     TEXT,
    created_at     TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (run_id) REFERENCES production_runs(run_id)
);
"""

SAMPLE_STAGES = [
    {"stage": "outline", "specialist": "content-creator", "description": "Draft outline"},
    {"stage": "slides", "specialist": "gamma-specialist", "description": "Generate slides"},
    {"stage": "review", "specialist": "quality-reviewer", "description": "Quality review"},
    {"stage": "checkpoint", "specialist": "human", "description": "User approval"},
]


class TempDB:
    """Context manager that provides a temporary SQLite database with schema."""

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


def _create_run(db_path: str, run_id: str = "TEST-RUN-001", stages: list | None = None) -> dict:
    """Helper to create a run for testing."""
    stages = stages or SAMPLE_STAGES
    args = [
        "--db", db_path,
        "create",
        "--run-id", run_id,
        "--purpose", "Test production run",
        "--content-type", "lecture-slides",
        "--course", "C1",
        "--module", "M2",
        "--lesson", "L3",
        "--stages-json", json.dumps(stages),
    ]
    ns = manage_run.build_parser().parse_args(args)
    return manage_run.cmd_create(ns)


def _write_baton(runtime_dir: str, run_id: str) -> Path:
    """Create a transient baton file for a run."""
    runtime = Path(runtime_dir)
    runtime.mkdir(parents=True, exist_ok=True)
    path = runtime / f"run_baton.{run_id}.json"
    path.write_text(
        json.dumps(
            {
                "run_id": run_id,
                "orchestrator": "marcus",
                "current_gate": "G2",
                "invocation_mode": "delegated",
                "allowed_delegates": ["gamma-specialist"],
                "escalation_target": "marcus",
                "blocking_authority": "human",
                "active": True,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return path


class TestCreateRun(unittest.TestCase):
    def test_create_basic(self) -> None:
        with TempDB() as db:
            result = _create_run(db.path)
            self.assertEqual(result["run_id"], "TEST-RUN-001")
            self.assertEqual(result["status"], "planning")
            self.assertEqual(result["stages_count"], 4)

    def test_create_auto_id(self) -> None:
        with TempDB() as db:
            args = manage_run.build_parser().parse_args([
                "--db", db.path,
                "create",
                "--content-type", "assessment",
                "--course", "C1",
                "--module", "M3",
            ])
            result = manage_run.cmd_create(args)
            self.assertIn("C1", result["run_id"])
            self.assertIn("M3", result["run_id"])

    def test_create_tracked_alias_normalizes_to_default(self) -> None:
        with TempDB() as db:
            run_id = f"TRACKED-{uuid.uuid4().hex[:10]}"
            args = manage_run.build_parser().parse_args([
                "--db", db.path,
                "create",
                "--run-id", run_id,
                "--course", "C1",
                "--module", "M1",
                "--mode", "tracked",
            ])
            result = manage_run.cmd_create(args)
            self.assertTrue(result["persisted"])
            self.assertEqual(result["mode"], "default")
            self.assertEqual(result["execution_mode"], "tracked")

    def test_create_duplicate_id(self) -> None:
        with TempDB() as db:
            _create_run(db.path, "DUP-001")
            result = _create_run(db.path, "DUP-001")
            self.assertIn("error", result)
            self.assertIn("already exists", result["error"])

    def test_create_ad_hoc_is_transient(self) -> None:
        with TempDB() as db, tempfile.TemporaryDirectory() as rt:
            run_id = f"ADHOC-{uuid.uuid4().hex[:10]}"
            args = manage_run.build_parser().parse_args([
                "--db", db.path,
                "--runtime-dir", rt,
                "create",
                "--run-id", run_id,
                "--content-type", "assessment",
                "--course", "C1",
                "--module", "M1",
                "--mode", "ad-hoc",
                "--stages-json", json.dumps([{"stage": "draft", "specialist": "content-creator"}]),
            ])
            result = manage_run.cmd_create(args)
            self.assertFalse(result["persisted"])
            self.assertEqual(result["mode"], "ad-hoc")
            for path in result["context_paths"].values():
                self.assertTrue(str(path).startswith(rt))

            canonical_dir = Path(__file__).resolve().parents[4] / "state" / "config" / "runs" / run_id
            self.assertFalse(canonical_dir.exists())

            conn = sqlite3.connect(db.path)
            count = conn.execute("SELECT COUNT(*) FROM production_runs WHERE run_id = ?", (run_id,)).fetchone()[0]
            conn.close()
            self.assertEqual(count, 0)

    def test_create_default_writes_canonical_context(self) -> None:
        with TempDB() as db:
            run_id = f"DEFAULT-{uuid.uuid4().hex[:10]}"
            args = manage_run.build_parser().parse_args([
                "--db", db.path,
                "create",
                "--run-id", run_id,
                "--course", "C1",
                "--module", "M1",
            ])
            result = manage_run.cmd_create(args)
            self.assertTrue(result["persisted"])
            self.assertEqual(result["mode"], "default")

            canonical_dir = Path(__file__).resolve().parents[4] / "state" / "config" / "runs" / run_id
            self.assertTrue(canonical_dir.exists())
            self.assertTrue((canonical_dir / "course_context.yaml").exists())
            for child in canonical_dir.glob("*"):
                child.unlink(missing_ok=True)
            canonical_dir.rmdir()

    def test_create_ad_hoc_without_db_still_succeeds(self) -> None:
        with tempfile.TemporaryDirectory() as rt:
            missing_db = Path(rt) / "missing.db"
            args = manage_run.build_parser().parse_args([
                "--db", str(missing_db),
                "--runtime-dir", rt,
                "create",
                "--run-id", "ADHOC-NODB-001",
                "--mode", "ad-hoc",
                "--course", "C1",
                "--module", "M1",
                "--stages-json", json.dumps([{"stage": "draft", "specialist": "content-creator"}]),
            ])
            result = manage_run.cmd_create(args)
            self.assertFalse(result["persisted"])
            self.assertEqual(result["mode"], "ad-hoc")


class TestAdvanceRun(unittest.TestCase):
    def test_advance_first_stage(self) -> None:
        with TempDB() as db:
            _create_run(db.path)
            args = manage_run.build_parser().parse_args(["--db", db.path, "advance", "TEST-RUN-001"])
            result = manage_run.cmd_advance(args)
            self.assertEqual(result["stage_index"], 1)
            self.assertEqual(result["advanced_to"]["stage"], "slides")
            self.assertEqual(result["status"], "in-progress")

    def test_advance_nonexistent(self) -> None:
        with TempDB() as db:
            args = manage_run.build_parser().parse_args(["--db", db.path, "advance", "NOPE"])
            result = manage_run.cmd_advance(args)
            self.assertIn("error", result)

    def test_advance_past_end(self) -> None:
        with TempDB() as db:
            _create_run(db.path, stages=[{"stage": "only", "specialist": "test"}])
            args = manage_run.build_parser().parse_args(["--db", db.path, "advance", "TEST-RUN-001"])
            result = manage_run.cmd_advance(args)
            self.assertIn("error", result)

    def test_advance_updates_baton_gate(self) -> None:
        with TempDB() as db, tempfile.TemporaryDirectory() as rt:
            _create_run(db.path, run_id="RUN-GATE")
            baton_path = _write_baton(rt, "RUN-GATE")

            args = manage_run.build_parser().parse_args(
                ["--db", db.path, "--runtime-dir", rt, "advance", "RUN-GATE"]
            )
            result = manage_run.cmd_advance(args)
            self.assertTrue(result["baton_gate_updated"])
            self.assertEqual(result["baton_gate_sync"]["status"], "updated")

            baton_data = json.loads(baton_path.read_text(encoding="utf-8"))
            self.assertEqual(baton_data["current_gate"], "slides")

    def test_advance_without_baton_reports_not_found_sync(self) -> None:
        with TempDB() as db, tempfile.TemporaryDirectory() as rt:
            _create_run(db.path, run_id="RUN-NO-BATON")
            args = manage_run.build_parser().parse_args(
                ["--db", db.path, "--runtime-dir", rt, "advance", "RUN-NO-BATON"]
            )
            result = manage_run.cmd_advance(args)
            self.assertFalse(result["baton_gate_updated"])
            self.assertEqual(result["baton_gate_sync"]["status"], "not-found")


class TestCheckpoint(unittest.TestCase):
    def test_checkpoint_current(self) -> None:
        with TempDB() as db:
            _create_run(db.path)
            args = manage_run.build_parser().parse_args(["--db", db.path, "checkpoint", "TEST-RUN-001"])
            result = manage_run.cmd_checkpoint(args)
            self.assertEqual(result["status"], "awaiting-review")

            conn = sqlite3.connect(db.path)
            gates = conn.execute("SELECT * FROM quality_gates WHERE run_id = 'TEST-RUN-001'").fetchall()
            conn.close()
            self.assertEqual(len(gates), 1)


class TestApprove(unittest.TestCase):
    def test_approve_at_checkpoint(self) -> None:
        with TempDB() as db:
            _create_run(db.path)
            cp_args = manage_run.build_parser().parse_args(["--db", db.path, "checkpoint", "TEST-RUN-001"])
            manage_run.cmd_checkpoint(cp_args)

            args = manage_run.build_parser().parse_args(["--db", db.path, "approve", "TEST-RUN-001"])
            result = manage_run.cmd_approve(args)
            self.assertEqual(result["approved_stage"]["status"], "approved")
            self.assertEqual(result["next_action"], "advance")

    def test_approve_not_at_checkpoint(self) -> None:
        with TempDB() as db:
            _create_run(db.path)
            args = manage_run.build_parser().parse_args(["--db", db.path, "approve", "TEST-RUN-001"])
            result = manage_run.cmd_approve(args)
            self.assertIn("error", result)

    def test_approve_final_stage(self) -> None:
        with TempDB() as db:
            stages = [{"stage": "final", "specialist": "human"}]
            _create_run(db.path, stages=stages)
            manage_run.cmd_checkpoint(
                manage_run.build_parser().parse_args(["--db", db.path, "checkpoint", "TEST-RUN-001"])
            )
            args = manage_run.build_parser().parse_args(["--db", db.path, "approve", "TEST-RUN-001"])
            result = manage_run.cmd_approve(args)
            self.assertEqual(result["next_action"], "complete")


class TestComplete(unittest.TestCase):
    def test_complete_all_approved(self) -> None:
        with TempDB() as db:
            stages = [{"stage": "s1", "specialist": "t"}]
            _create_run(db.path, stages=stages)
            manage_run.cmd_checkpoint(
                manage_run.build_parser().parse_args(["--db", db.path, "checkpoint", "TEST-RUN-001"])
            )
            manage_run.cmd_approve(
                manage_run.build_parser().parse_args(["--db", db.path, "approve", "TEST-RUN-001"])
            )
            args = manage_run.build_parser().parse_args(["--db", db.path, "complete", "TEST-RUN-001"])
            result = manage_run.cmd_complete(args)
            self.assertEqual(result["status"], "completed")
            self.assertIn("completed_at", result)

    def test_complete_unapproved_stages(self) -> None:
        with TempDB() as db:
            _create_run(db.path)
            args = manage_run.build_parser().parse_args(["--db", db.path, "complete", "TEST-RUN-001"])
            result = manage_run.cmd_complete(args)
            self.assertIn("error", result)
            self.assertIn("unapproved", result)

    def test_complete_closes_baton(self) -> None:
        with TempDB() as db, tempfile.TemporaryDirectory() as rt:
            stages = [{"stage": "s1", "specialist": "t"}]
            _create_run(db.path, run_id="RUN-CLOSE", stages=stages)
            _write_baton(rt, "RUN-CLOSE")
            cache_dir = Path(rt) / "perception-cache"
            cache_dir.mkdir(parents=True, exist_ok=True)
            cache_file = cache_dir / "RUN-CLOSE.json"
            cache_file.write_text("{}", encoding="utf-8")

            manage_run.cmd_checkpoint(
                manage_run.build_parser().parse_args(["--db", db.path, "checkpoint", "RUN-CLOSE"])
            )
            manage_run.cmd_approve(
                manage_run.build_parser().parse_args(["--db", db.path, "approve", "RUN-CLOSE"])
            )

            args = manage_run.build_parser().parse_args(
                ["--db", db.path, "--runtime-dir", rt, "complete", "RUN-CLOSE"]
            )
            result = manage_run.cmd_complete(args)
            self.assertEqual(result["status"], "completed")
            self.assertTrue(result["baton_closed"])
            self.assertEqual(result["baton_close"]["status"], "closed")
            self.assertTrue(result["cache_cleared"])
            self.assertFalse((Path(rt) / "run_baton.RUN-CLOSE.json").exists())
            self.assertFalse(cache_file.exists())


class TestCancel(unittest.TestCase):
    def test_cancel_run(self) -> None:
        with TempDB() as db, tempfile.TemporaryDirectory() as rt:
            _create_run(db.path, run_id="RUN-CANCEL")
            _write_baton(rt, "RUN-CANCEL")
            cache_dir = Path(rt) / "perception-cache"
            cache_dir.mkdir(parents=True, exist_ok=True)
            cache_file = cache_dir / "RUN-CANCEL.json"
            cache_file.write_text("{}", encoding="utf-8")

            args = manage_run.build_parser().parse_args(
                ["--db", db.path, "--runtime-dir", rt, "cancel", "RUN-CANCEL"]
            )
            result = manage_run.cmd_cancel(args)
            self.assertEqual(result["status"], "cancelled")
            self.assertTrue(result["baton_closed"])
            self.assertEqual(result["baton_close"]["status"], "closed")
            self.assertTrue(result["cache_cleared"])
            self.assertFalse((Path(rt) / "run_baton.RUN-CANCEL.json").exists())
            self.assertFalse(cache_file.exists())

    def test_cancel_without_baton_reports_not_found(self) -> None:
        with TempDB() as db, tempfile.TemporaryDirectory() as rt:
            _create_run(db.path, run_id="RUN-CANCEL-NO-BATON")
            args = manage_run.build_parser().parse_args(
                ["--db", db.path, "--runtime-dir", rt, "cancel", "RUN-CANCEL-NO-BATON"]
            )
            result = manage_run.cmd_cancel(args)
            self.assertEqual(result["status"], "cancelled")
            self.assertFalse(result["baton_closed"])
            self.assertEqual(result["baton_close"]["status"], "not-found")

    def test_cancel_completed_run_disallowed(self) -> None:
        with TempDB() as db:
            stages = [{"stage": "s1", "specialist": "t"}]
            _create_run(db.path, run_id="RUN-FINAL", stages=stages)
            manage_run.cmd_checkpoint(
                manage_run.build_parser().parse_args(["--db", db.path, "checkpoint", "RUN-FINAL"])
            )
            manage_run.cmd_approve(
                manage_run.build_parser().parse_args(["--db", db.path, "approve", "RUN-FINAL"])
            )
            manage_run.cmd_complete(
                manage_run.build_parser().parse_args(["--db", db.path, "complete", "RUN-FINAL"])
            )

            args = manage_run.build_parser().parse_args(["--db", db.path, "cancel", "RUN-FINAL"])
            result = manage_run.cmd_cancel(args)
            self.assertIn("error", result)
            self.assertIn("Cannot cancel", result["error"])


class TestStatus(unittest.TestCase):
    def test_status_basic(self) -> None:
        with TempDB() as db:
            _create_run(db.path)
            args = manage_run.build_parser().parse_args(["--db", db.path, "status", "TEST-RUN-001"])
            result = manage_run.cmd_status(args)
            self.assertEqual(result["run_id"], "TEST-RUN-001")
            self.assertEqual(result["status"], "planning")
            self.assertEqual(result["stages_total"], 4)
            self.assertEqual(result["stages_completed"], 0)
            self.assertIsNotNone(result["current_stage"])

    def test_status_nonexistent(self) -> None:
        with TempDB() as db:
            args = manage_run.build_parser().parse_args(["--db", db.path, "status", "NOPE"])
            result = manage_run.cmd_status(args)
            self.assertIn("error", result)


class TestResume(unittest.TestCase):
    def test_resume_db_run(self) -> None:
        with TempDB() as db:
            _create_run(db.path, run_id="RUN-RESUME")
            p = manage_run.build_parser()
            manage_run.cmd_advance(p.parse_args(["--db", db.path, "advance", "RUN-RESUME"]))
            result = manage_run.cmd_resume(p.parse_args(["--db", db.path, "resume", "RUN-RESUME"]))
            self.assertEqual(result["status"], "in-progress")
            self.assertTrue(result["persisted"])

    def test_resume_ad_hoc_run(self) -> None:
        with TempDB() as db, tempfile.TemporaryDirectory() as rt:
            p = manage_run.build_parser()
            create = manage_run.cmd_create(
                p.parse_args([
                    "--db", db.path,
                    "--runtime-dir", rt,
                    "create",
                    "--run-id", "RUN-RESUME-ADHOC",
                    "--mode", "ad-hoc",
                    "--stages-json", json.dumps([
                        {"stage": "draft", "specialist": "content-creator"},
                        {"stage": "review", "specialist": "human"},
                    ]),
                ])
            )
            self.assertFalse(create["persisted"])

            result = manage_run.cmd_resume(
                p.parse_args([
                    "--db", db.path,
                    "--runtime-dir", rt,
                    "resume",
                    "RUN-RESUME-ADHOC",
                ])
            )
            self.assertEqual(result["mode"], "ad-hoc")
            self.assertFalse(result["persisted"])


class TestList(unittest.TestCase):
    def test_list_active(self) -> None:
        with TempDB() as db:
            _create_run(db.path, "RUN-A")
            _create_run(db.path, "RUN-B")
            args = manage_run.build_parser().parse_args(["--db", db.path, "list"])
            result = manage_run.cmd_list(args)
            self.assertEqual(result["count"], 2)

    def test_list_excludes_completed(self) -> None:
        with TempDB() as db:
            stages = [{"stage": "s1", "specialist": "t"}]
            _create_run(db.path, "RUN-DONE", stages=stages)
            manage_run.cmd_checkpoint(
                manage_run.build_parser().parse_args(["--db", db.path, "checkpoint", "RUN-DONE"])
            )
            manage_run.cmd_approve(
                manage_run.build_parser().parse_args(["--db", db.path, "approve", "RUN-DONE"])
            )
            manage_run.cmd_complete(
                manage_run.build_parser().parse_args(["--db", db.path, "complete", "RUN-DONE"])
            )
            _create_run(db.path, "RUN-ACTIVE")

            args = manage_run.build_parser().parse_args(["--db", db.path, "list"])
            result = manage_run.cmd_list(args)
            self.assertEqual(result["count"], 1)
            self.assertEqual(result["runs"][0]["run_id"], "RUN-ACTIVE")


class TestFullLifecycle(unittest.TestCase):
    """Integration test: full run from create through complete."""

    def test_full_lifecycle(self) -> None:
        with TempDB() as db:
            stages = [
                {"stage": "draft", "specialist": "content-creator"},
                {"stage": "review", "specialist": "human"},
            ]
            create_result = _create_run(db.path, "LIFECYCLE-001", stages=stages)
            self.assertEqual(create_result["status"], "planning")

            p = manage_run.build_parser()

            advance1 = manage_run.cmd_advance(p.parse_args(["--db", db.path, "advance", "LIFECYCLE-001"]))
            self.assertEqual(advance1["stage_index"], 1)

            cp = manage_run.cmd_checkpoint(p.parse_args(["--db", db.path, "checkpoint", "LIFECYCLE-001"]))
            self.assertEqual(cp["status"], "awaiting-review")

            approve = manage_run.cmd_approve(p.parse_args(["--db", db.path, "approve", "LIFECYCLE-001"]))
            self.assertEqual(approve["next_action"], "complete")

            # Approve first stage too (it was auto-approved by advance)
            # Complete the run
            complete = manage_run.cmd_complete(p.parse_args(["--db", db.path, "complete", "LIFECYCLE-001"]))
            self.assertEqual(complete["status"], "completed")

            status = manage_run.cmd_status(p.parse_args(["--db", db.path, "status", "LIFECYCLE-001"]))
            self.assertEqual(status["status"], "completed")
            self.assertEqual(status["stages_completed"], 2)

    def test_full_lifecycle_with_baton_sync_and_close(self) -> None:
        with TempDB() as db, tempfile.TemporaryDirectory() as rt:
            stages = [
                {"stage": "draft", "specialist": "content-creator"},
                {"stage": "review", "specialist": "human"},
            ]
            _create_run(db.path, "LIFECYCLE-BATON-001", stages=stages)
            _write_baton(rt, "LIFECYCLE-BATON-001")

            p = manage_run.build_parser()
            advance1 = manage_run.cmd_advance(
                p.parse_args(["--db", db.path, "--runtime-dir", rt, "advance", "LIFECYCLE-BATON-001"])
            )
            self.assertTrue(advance1["baton_gate_updated"])
            self.assertEqual(advance1["baton_gate_sync"]["status"], "updated")

            cp = manage_run.cmd_checkpoint(
                p.parse_args(["--db", db.path, "checkpoint", "LIFECYCLE-BATON-001"])
            )
            self.assertEqual(cp["status"], "awaiting-review")

            approve = manage_run.cmd_approve(
                p.parse_args(["--db", db.path, "approve", "LIFECYCLE-BATON-001"])
            )
            self.assertEqual(approve["next_action"], "complete")

            complete = manage_run.cmd_complete(
                p.parse_args(["--db", db.path, "--runtime-dir", rt, "complete", "LIFECYCLE-BATON-001"])
            )
            self.assertEqual(complete["status"], "completed")
            self.assertTrue(complete["baton_closed"])
            self.assertEqual(complete["baton_close"]["status"], "closed")


class TestDoubleDispatchFlag(unittest.TestCase):
    """Story 12.5: double_dispatch flag propagation through manage_run."""

    def test_create_with_double_dispatch_flag(self) -> None:
        with TempDB() as db:
            run_id = f"DD-{uuid.uuid4().hex[:10]}"
            args = manage_run.build_parser().parse_args([
                "--db", db.path,
                "create",
                "--run-id", run_id,
                "--course", "C1",
                "--module", "M1",
                "--double-dispatch",
            ])
            result = manage_run.cmd_create(args)
            self.assertEqual(result["run_id"], run_id)
            self.assertTrue(result["persisted"])

            conn = sqlite3.connect(db.path)
            row = conn.execute(
                "SELECT context_json FROM production_runs WHERE run_id = ?", (run_id,)
            ).fetchone()
            conn.close()
            context = json.loads(row[0])
            self.assertTrue(context["double_dispatch"])

    def test_create_without_double_dispatch_defaults_false(self) -> None:
        with TempDB() as db:
            run_id = f"NO-DD-{uuid.uuid4().hex[:10]}"
            args = manage_run.build_parser().parse_args([
                "--db", db.path,
                "create",
                "--run-id", run_id,
                "--course", "C1",
                "--module", "M1",
            ])
            result = manage_run.cmd_create(args)
            conn = sqlite3.connect(db.path)
            row = conn.execute(
                "SELECT context_json FROM production_runs WHERE run_id = ?", (run_id,)
            ).fetchone()
            conn.close()
            context = json.loads(row[0])
            self.assertFalse(context["double_dispatch"])

    def test_ad_hoc_double_dispatch(self) -> None:
        with TempDB() as db, tempfile.TemporaryDirectory() as rt:
            run_id = f"DD-ADHOC-{uuid.uuid4().hex[:10]}"
            args = manage_run.build_parser().parse_args([
                "--db", db.path,
                "--runtime-dir", rt,
                "create",
                "--run-id", run_id,
                "--mode", "ad-hoc",
                "--course", "C1",
                "--module", "M1",
                "--double-dispatch",
            ])
            result = manage_run.cmd_create(args)
            self.assertFalse(result["persisted"])
            self.assertEqual(result["mode"], "ad-hoc")

            ad_hoc_path = Path(rt) / "ad-hoc-runs" / f"{run_id}.json"
            self.assertTrue(ad_hoc_path.exists())
            data = json.loads(ad_hoc_path.read_text(encoding="utf-8"))
            self.assertTrue(data["context_json"]["double_dispatch"])


class TestMotionFlags(unittest.TestCase):
    """Epic 14: motion run flags and context sidecar propagation."""

    def test_create_with_motion_flags_persists_context_and_sidecar(self) -> None:
        with TempDB() as db:
            run_id = f"MOTION-{uuid.uuid4().hex[:10]}"
            args = manage_run.build_parser().parse_args([
                "--db", db.path,
                "create",
                "--run-id", run_id,
                "--course", "C1",
                "--module", "M1",
                "--motion-enabled",
                "--motion-budget-max-credits", "24",
                "--motion-budget-model-preference", "pro",
            ])
            result = manage_run.cmd_create(args)
            self.assertTrue(result["persisted"])

            conn = sqlite3.connect(db.path)
            row = conn.execute(
                "SELECT context_json FROM production_runs WHERE run_id = ?", (run_id,)
            ).fetchone()
            conn.close()
            context = json.loads(row[0])
            self.assertTrue(context["motion_enabled"])
            self.assertEqual(context["motion_budget"]["max_credits"], 24.0)
            self.assertEqual(context["motion_budget"]["model_preference"], "pro")

            motion_plan = Path(result["context_paths"]["motion_plan"])
            self.assertTrue(motion_plan.exists())
            plan_data = json.loads(json.dumps(__import__("yaml").safe_load(motion_plan.read_text(encoding="utf-8"))))
            self.assertTrue(plan_data["motion_enabled"])
            self.assertEqual(plan_data["motion_budget"]["max_credits"], 24.0)

    def test_motion_defaults_remain_off(self) -> None:
        with TempDB() as db:
            run_id = f"STATIC-{uuid.uuid4().hex[:10]}"
            args = manage_run.build_parser().parse_args([
                "--db", db.path,
                "create",
                "--run-id", run_id,
                "--course", "C1",
                "--module", "M1",
            ])
            result = manage_run.cmd_create(args)
            self.assertTrue(result["persisted"])

            conn = sqlite3.connect(db.path)
            row = conn.execute(
                "SELECT context_json FROM production_runs WHERE run_id = ?", (run_id,)
            ).fetchone()
            conn.close()
            context = json.loads(row[0])
            self.assertFalse(context["motion_enabled"])
            self.assertEqual(context["motion_budget"]["model_preference"], "std")

    def test_ad_hoc_motion_run_uses_transient_motion_plan(self) -> None:
        with TempDB() as db, tempfile.TemporaryDirectory() as rt:
            run_id = f"MOTION-ADHOC-{uuid.uuid4().hex[:10]}"
            args = manage_run.build_parser().parse_args([
                "--db", db.path,
                "--runtime-dir", rt,
                "create",
                "--run-id", run_id,
                "--mode", "ad-hoc",
                "--course", "C1",
                "--module", "M1",
                "--motion-enabled",
                "--motion-budget-max-credits", "12",
            ])
            result = manage_run.cmd_create(args)
            self.assertFalse(result["persisted"])
            motion_plan = Path(result["context_paths"]["motion_plan"])
            self.assertTrue(str(motion_plan).startswith(rt))
            self.assertTrue(motion_plan.exists())

    def test_motion_enabled_requires_explicit_budget(self) -> None:
        with TempDB() as db:
            run_id = f"MOTION-NOBUDGET-{uuid.uuid4().hex[:10]}"
            args = manage_run.build_parser().parse_args([
                "--db", db.path,
                "create",
                "--run-id", run_id,
                "--course", "C1",
                "--module", "M1",
                "--motion-enabled",
            ])
            result = manage_run.cmd_create(args)
            self.assertEqual(result["code"], "MOTION_BUDGET_REQUIRED")
            self.assertIn("motion_budget_max_credits", result["error"])


if __name__ == "__main__":
    unittest.main()
