"""Log quality review results to SQLite quality_gates table.

Supports mode-aware logging: default mode writes to DB,
ad-hoc mode returns the record without persisting.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path


def get_db_path() -> Path:
    """Resolve the coordination database path."""
    try:
        from scripts.utilities.file_helpers import project_root
        return project_root() / "state" / "runtime" / "coordination.db"
    except ImportError:
        return Path("state/runtime/coordination.db")


def log_quality_result(
    run_id: str,
    stage: str,
    status: str,
    reviewer: str,
    findings: list[dict],
    score: float,
    run_mode: str = "default",
    db_path: Path | None = None,
) -> dict:
    """Log a quality review result to the quality_gates table.

    Args:
        run_id: Production run identifier.
        stage: Review stage (e.g., "content-review", "slide-review").
        status: Review verdict (pass, pass_with_notes, fail, partial_review).
        reviewer: Reviewing agent name (e.g., "quinn-r").
        findings: List of finding dicts from the quality report.
        score: Overall confidence score (0.0-1.0).
        run_mode: "default" persists to DB; "ad-hoc" returns record only.
        db_path: Override path for the database.

    Returns:
        Dict with the logged record and persistence status.
    """
    record = {
        "run_id": run_id,
        "stage": stage,
        "status": status,
        "reviewer": reviewer,
        "findings_json": json.dumps(findings),
        "score": score,
        "decided_at": datetime.now(UTC).isoformat(),
    }

    if run_mode == "ad-hoc":
        return {
            "logged": False,
            "reason": "ad-hoc mode — quality review executed but not persisted",
            "record": record,
        }

    db = db_path or get_db_path()
    if not db.exists():
        return {
            "logged": False,
            "reason": f"Database not found at {db}",
            "record": record,
        }

    conn = sqlite3.connect(str(db))
    try:
        conn.execute(
            """INSERT INTO quality_gates
               (run_id, stage, status, reviewer, findings_json, score, decided_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                record["run_id"],
                record["stage"],
                record["status"],
                record["reviewer"],
                record["findings_json"],
                record["score"],
                record["decided_at"],
            ),
        )
        conn.commit()
        gate_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    finally:
        conn.close()

    return {
        "logged": True,
        "gate_id": gate_id,
        "record": record,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] == "--help":
        print("Usage: quality_logger.py <quality_report.json> [--mode default|ad-hoc]")
        print("  Reads a quality report JSON and logs to SQLite quality_gates table.")
        sys.exit(0)

    report_path = Path(sys.argv[1])
    mode = "default"
    if "--mode" in sys.argv:
        idx = sys.argv.index("--mode")
        mode = sys.argv[idx + 1]

    report = json.loads(report_path.read_text(encoding="utf-8"))
    result = log_quality_result(
        run_id=report.get("run_id", "unknown"),
        stage=report.get("stage", "quality-review"),
        status=report.get("status", "unknown"),
        reviewer=report.get("reviewer", "quinn-r"),
        findings=report.get("findings", []),
        score=report.get("score", 0.0),
        run_mode=mode,
    )
    print(json.dumps(result, indent=2))
