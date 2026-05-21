# /// script
# requires-python = ">=3.10"
# ///
"""Tests for content_entity_manager.py."""

from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import content_entity_manager as cem

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS asset_evolution (
    evolution_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    asset_id TEXT NOT NULL,
    version INTEGER NOT NULL,
    content_hash TEXT,
    decision_rationale TEXT,
    metadata_json TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS learning_objective_map (
    mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    asset_id TEXT NOT NULL,
    objective_id TEXT NOT NULL,
    validation_status TEXT NOT NULL,
    aligned_at TEXT
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
        conn.commit()
        conn.close()
        return self

    def __exit__(self, *args: object) -> None:
        self.path.unlink(missing_ok=True)


class TestContentEntityManager(unittest.TestCase):
    def test_asset_evolution_versions_increment(self) -> None:
        with TempDB() as db, tempfile.TemporaryDirectory() as td:
            artifact = Path(td) / "asset.md"
            artifact.write_text("Initial content", encoding="utf-8")

            r1 = cem.track_asset_evolution(
                run_id="RUN-1",
                asset_id="slide-deck",
                artifact_path=artifact,
                decision_rationale="initial",
                run_mode="default",
                db_path=db.path,
            )
            artifact.write_text("Updated content", encoding="utf-8")
            r2 = cem.track_asset_evolution(
                run_id="RUN-1",
                asset_id="slide-deck",
                artifact_path=artifact,
                decision_rationale="revise",
                run_mode="default",
                db_path=db.path,
            )

            self.assertEqual(r1["version"], 1)
            self.assertEqual(r2["version"], 2)

    def test_alignment_persists_default_mode(self) -> None:
        with TempDB() as db:
            result = cem.validate_learning_objective_alignment(
                run_id="RUN-2",
                asset_id="script",
                objectives=["Explain cardiac output", "Define preload"],
                content="This lesson will explain cardiac output and preload in context.",
                run_mode="default",
                db_path=db.path,
            )
            self.assertTrue(result["persisted"])
            self.assertIn(result["alignment_status"], {"aligned", "partial"})

            conn = sqlite3.connect(str(db.path))
            count = conn.execute("SELECT COUNT(*) FROM learning_objective_map").fetchone()[0]
            conn.close()
            self.assertEqual(count, 2)

    def test_alignment_blocked_in_ad_hoc(self) -> None:
        with TempDB() as db:
            result = cem.validate_learning_objective_alignment(
                run_id="RUN-3",
                asset_id="script",
                objectives=["Explain dosage math"],
                content="Sandbox text for practice.",
                run_mode="ad-hoc",
                db_path=db.path,
            )
            self.assertFalse(result["persisted"])
            self.assertIsNotNone(result["blocked"])

    def test_release_manifest_created(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "manifest.json"
            result = cem.generate_release_manifest(
                run_id="RUN-4",
                assets=[{"asset_id": "slides", "path": "x"}],
                quality_certified=True,
                output_path=out,
            )
            self.assertTrue(out.exists())
            stored = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(stored["run_id"], "RUN-4")
            self.assertTrue(stored["quality_certified"])
            self.assertEqual(result["manifest"]["asset_count"], 1)

    def test_alignment_with_no_objectives(self) -> None:
        with TempDB() as db:
            result = cem.validate_learning_objective_alignment(
                run_id="RUN-5",
                asset_id="notes",
                objectives=[],
                content="Some content",
                run_mode="default",
                db_path=db.path,
            )
            self.assertEqual(result["alignment_status"], "no-objectives")


if __name__ == "__main__":
    unittest.main()
