# /// script
# requires-python = ">=3.10"
# ///
"""Read current run mode, last run ID, and session timestamps from the coordination database.

Returns structured JSON for agent consumption. Falls back gracefully when
the database doesn't exist or has no production runs.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path


def find_project_root() -> Path:
    """Walk up from script location to find the project root (contains state/)."""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "state").is_dir():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent.parent


def read_mode_from_file(runtime_dir: Path) -> str:
    """Read the current run mode from the persistent mode state file.

    Args:
        runtime_dir: Path to state/runtime/ directory.

    Returns:
        Current mode string ('default' or 'ad-hoc').
    """
    mode_file = runtime_dir / "mode_state.json"
    if mode_file.exists():
        try:
            with open(mode_file) as f:
                data = json.load(f)
            return data.get("mode", "default")
        except (json.JSONDecodeError, OSError):
            return "default"
    return "default"


def read_mode_state(db_path: Path) -> dict:
    """Query the coordination database and mode file for current production state.

    Args:
        db_path: Path to the SQLite coordination database.

    Returns:
        Dictionary with mode, last run, and session state.
    """
    runtime_dir = db_path.parent
    result = {
        "timestamp": datetime.now().isoformat(),
        "db_exists": db_path.exists(),
        "mode": read_mode_from_file(runtime_dir),
        "active_run": None,
        "last_completed_run": None,
        "session": {
            "last_activity": None,
            "pending_gates": 0,
        },
    }

    if not db_path.exists():
        return result

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        active = conn.execute(
            """SELECT run_id, purpose, status, preset, course_code, module_id,
                      started_at, updated_at
               FROM production_runs
               WHERE status NOT IN ('completed', 'cancelled')
               ORDER BY updated_at DESC
               LIMIT 1"""
        ).fetchone()

        if active:
            result["active_run"] = {
                "run_id": active["run_id"],
                "purpose": active["purpose"],
                "status": active["status"],
                "preset": active["preset"],
                "course_code": active["course_code"],
                "module_id": active["module_id"],
                "started_at": active["started_at"],
                "updated_at": active["updated_at"],
            }

        last_completed = conn.execute(
            """SELECT run_id, purpose, status, course_code, module_id,
                      started_at, completed_at
               FROM production_runs
               WHERE status = 'completed'
               ORDER BY completed_at DESC
               LIMIT 1"""
        ).fetchone()

        if last_completed:
            result["last_completed_run"] = {
                "run_id": last_completed["run_id"],
                "purpose": last_completed["purpose"],
                "course_code": last_completed["course_code"],
                "module_id": last_completed["module_id"],
                "started_at": last_completed["started_at"],
                "completed_at": last_completed["completed_at"],
            }

        last_activity_row = conn.execute(
            "SELECT MAX(updated_at) as last FROM production_runs"
        ).fetchone()
        if last_activity_row and last_activity_row["last"]:
            result["session"]["last_activity"] = last_activity_row["last"]

        pending_gates_row = conn.execute(
            "SELECT COUNT(*) as cnt FROM quality_gates WHERE status = 'pending'"
        ).fetchone()
        result["session"]["pending_gates"] = pending_gates_row["cnt"] if pending_gates_row else 0

    finally:
        conn.close()

    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Read current run mode, last run ID, and session timestamps from the coordination database.",
        epilog="Returns structured JSON to stdout. Diagnostics to stderr.",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=None,
        help="Path to the coordination SQLite database. Default: state/runtime/coordination.db",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print diagnostic info to stderr.",
    )
    args = parser.parse_args()

    project_root = find_project_root()
    db_path = args.db_path or (project_root / "state" / "runtime" / "coordination.db")

    if args.verbose:
        print(f"Project root: {project_root}", file=sys.stderr)
        print(f"Database path: {db_path}", file=sys.stderr)
        print(f"Database exists: {db_path.exists()}", file=sys.stderr)

    try:
        state = read_mode_state(db_path)
        json.dump(state, sys.stdout, indent=2)
        print()
        sys.exit(0)
    except Exception as e:
        error = {"error": str(e), "timestamp": datetime.now().isoformat()}
        json.dump(error, sys.stderr, indent=2)
        print(file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
