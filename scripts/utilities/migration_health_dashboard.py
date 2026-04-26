"""Migration health dashboard — single-pane status of the LangChain/LangGraph migration.

Companion to trial_run_preflight.py. Where preflight checks "is the substrate ready
for THIS trial-run?" the dashboard answers "what's the current state of the migration
overall?" — useful for operator status checks, daily standup, post-Slab-close audits.

Usage:
    .venv/Scripts/python.exe scripts/utilities/migration_health_dashboard.py
    .venv/Scripts/python.exe scripts/utilities/migration_health_dashboard.py --json   # machine-readable

What it reports:
    - Per-epic state (done / in-progress / pending)
    - Per-story counts by state
    - Open conditional milestones (M2 / M3 / M4) with resolution-path
    - Deferred-inventory total + categorized counts
    - Import-linter contracts (count + KEPT / BROKEN tally)
    - Ruff debt count (legacy)
    - Test collection summary (collected / errors)
    - Trial-replay last-run timestamp (if available)
    - Ledger row count (if Postgres reachable)
    - Sanctum mutation count (last 7 days; if ledger reachable)
    - Migration-master-status enum value (post-5a.5)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class HealthReport:
    timestamp: str
    sprint_summary: dict[str, Any] = field(default_factory=dict)
    conditional_milestones: list[dict[str, str]] = field(default_factory=list)
    deferred_inventory: dict[str, Any] = field(default_factory=dict)
    import_linter: dict[str, Any] = field(default_factory=dict)
    ruff_debt: dict[str, Any] = field(default_factory=dict)
    test_collection: dict[str, Any] = field(default_factory=dict)
    trial_replay: dict[str, Any] = field(default_factory=dict)
    ledger: dict[str, Any] = field(default_factory=dict)
    sanctum_mutations_7d: dict[str, Any] = field(default_factory=dict)
    migration_master_status: str = "in-flight"
    notes: list[str] = field(default_factory=list)


def _parse_sprint_status() -> dict[str, Any]:
    path = REPO_ROOT / "_bmad-output" / "implementation-artifacts" / "sprint-status.yaml"
    if not path.is_file():
        return {"error": "sprint-status.yaml not found"}
    content = path.read_text(encoding="utf-8")
    epics = {}
    story_states = {"done": 0, "in-progress": 0, "ready-for-dev": 0, "pending": 0, "deleted": 0, "other": 0}
    for line in content.split("\n"):
        s = line.strip()
        if s.startswith("migration-epic-"):
            parts = s.split(":", 1)
            if len(parts) == 2:
                key = parts[0].strip()
                state = parts[1].split("#")[0].strip()
                epics[key] = state
        elif re.match(r"^migration-[0-9a-z-]+:", s):
            parts = s.split(":", 1)
            if len(parts) == 2:
                state = parts[1].split("#")[0].strip()
                story_states[state] = story_states.get(state, 0) + 1 if state in story_states else story_states["other"] + 1
    return {"epics": epics, "story_states": story_states, "total_stories": sum(story_states.values())}


def _detect_conditional_milestones() -> list[dict[str, str]]:
    """Inspect M2/M3/M4 verdict artifacts."""
    artifacts = [
        ("M2", REPO_ROOT / "_bmad-output" / "implementation-artifacts" / "slab-2c-m2-acceptance-verdict.md"),
        ("M3", REPO_ROOT / "_bmad-output" / "implementation-artifacts" / "slab-3-m3-acceptance-verdict.md"),
        ("M4", REPO_ROOT / "_bmad-output" / "implementation-artifacts" / "slab-4-m4-acceptance-verdict.md"),
    ]
    results = []
    for milestone, path in artifacts:
        if not path.is_file():
            results.append({"milestone": milestone, "state": "PENDING-AUTHORING", "artifact": str(path.relative_to(REPO_ROOT))})
            continue
        content = path.read_text(encoding="utf-8")
        if "CONDITIONAL-GREEN" in content or "CONDITIONAL-PENDING" in content:
            results.append({"milestone": milestone, "state": "CONDITIONAL-GREEN-PENDING-OPERATOR-ADDENDUM", "artifact": str(path.relative_to(REPO_ROOT))})
        elif "GREEN-LIGHT" in content:
            results.append({"milestone": milestone, "state": "GREEN-LIGHT", "artifact": str(path.relative_to(REPO_ROOT))})
        else:
            results.append({"milestone": milestone, "state": "UNKNOWN", "artifact": str(path.relative_to(REPO_ROOT))})
    return results


def _count_deferred_inventory() -> dict[str, Any]:
    path = REPO_ROOT / "_bmad-output" / "planning-artifacts" / "deferred-inventory.md"
    if not path.is_file():
        return {"error": "not found", "total": 0}
    content = path.read_text(encoding="utf-8")
    # Rough counts: table rows starting with `| **`
    table_rows = len(re.findall(r"^\| \*\*", content, re.MULTILINE))
    backlog_epics = len(re.findall(r"backlog.*epic", content, re.IGNORECASE))
    return {"total_table_rows": table_rows, "backlog_mentions": backlog_epics}


def _check_import_linter() -> dict[str, Any]:
    """Run lint-imports + parse output."""
    binary = REPO_ROOT / ".venv" / "Scripts" / "lint-imports.exe"
    if not binary.exists():
        binary = REPO_ROOT / ".venv" / "bin" / "lint-imports"
    if not binary.exists():
        return {"error": "lint-imports binary not found in .venv"}
    try:
        result = subprocess.run(
            [str(binary), "--config", str(REPO_ROOT / "pyproject.toml")],
            capture_output=True, text=True, timeout=30, cwd=str(REPO_ROOT),
        )
        # Parse "Contracts: N kept, M broken."
        m = re.search(r"Contracts:\s*(\d+)\s*kept,\s*(\d+)\s*broken", result.stdout)
        if m:
            return {"kept": int(m.group(1)), "broken": int(m.group(2)), "exit_code": result.returncode}
        return {"raw_tail": result.stdout[-200:], "exit_code": result.returncode}
    except subprocess.TimeoutExpired:
        return {"error": "timeout after 30s"}
    except Exception as exc:
        return {"error": str(exc)}


def _count_ruff_debt() -> dict[str, Any]:
    binary = REPO_ROOT / ".venv" / "Scripts" / "python.exe"
    if not binary.exists():
        binary = REPO_ROOT / ".venv" / "bin" / "python"
    if not binary.exists():
        return {"error": ".venv python not found"}
    try:
        result = subprocess.run(
            [str(binary), "-m", "ruff", "check", "app/", "tests/", "skills/", "scripts/", "marcus/"],
            capture_output=True, text=True, timeout=30, cwd=str(REPO_ROOT),
        )
        m = re.search(r"Found (\d+) error", result.stdout)
        if m:
            return {"errors": int(m.group(1)), "exit_code": result.returncode}
        if "All checks passed" in result.stdout:
            return {"errors": 0, "exit_code": result.returncode}
        return {"raw_tail": result.stdout[-200:], "exit_code": result.returncode}
    except Exception as exc:
        return {"error": str(exc)}


def _test_collection_summary() -> dict[str, Any]:
    binary = REPO_ROOT / ".venv" / "Scripts" / "python.exe"
    if not binary.exists():
        binary = REPO_ROOT / ".venv" / "bin" / "python"
    if not binary.exists():
        return {"error": ".venv python not found"}
    try:
        result = subprocess.run(
            [str(binary), "-m", "pytest", "--collect-only", "-q"],
            capture_output=True, text=True, timeout=60, cwd=str(REPO_ROOT),
        )
        # Parse "N/M tests collected (X deselected), K errors"
        m = re.search(r"(\d+)/(\d+) tests collected", result.stdout)
        errors_match = re.search(r"(\d+)\s+error", result.stdout)
        if m:
            return {
                "collected": int(m.group(1)),
                "total_seen": int(m.group(2)),
                "collection_errors": int(errors_match.group(1)) if errors_match else 0,
            }
        # Fallback for clean run
        clean_match = re.search(r"(\d+)\s+tests collected", result.stdout)
        if clean_match:
            return {"collected": int(clean_match.group(1)), "collection_errors": 0}
        return {"raw_tail": result.stdout[-200:]}
    except subprocess.TimeoutExpired:
        return {"error": "timeout after 60s"}
    except Exception as exc:
        return {"error": str(exc)}


def _check_trial_replay_last_run() -> dict[str, Any]:
    """Check if any recent trial-replay run produced output."""
    # Slab 5a.1 ships replay; pre-Slab-5a, this returns SKIP
    replay_dir = REPO_ROOT / "tests" / "trial_replay"
    if not replay_dir.is_dir():
        return {"state": "Slab-5a.1-pending; trial-replay infrastructure not yet shipped"}
    # Look for recent test artifacts (heuristic)
    py_files = list(replay_dir.glob("test_*.py"))
    if not py_files:
        return {"state": "trial_replay/ exists but no test files"}
    return {"state": "trial-replay tests present", "test_count": len(py_files)}


def _check_ledger() -> dict[str, Any]:
    """Query Postgres for ledger row counts."""
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        return {"state": "DATABASE_URL not set"}
    try:
        import psycopg
        conn = psycopg.connect(db_url, connect_timeout=5)
        with conn.cursor() as cur:
            cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'ledger_events')")
            row = cur.fetchone()
            if not row or not row[0]:
                conn.close()
                return {"state": "ledger_events table not loaded (Slab 4.4 schema.sql pending)"}
            cur.execute("SELECT COUNT(*), COUNT(DISTINCT trial_id) FROM ledger_events")
            row = cur.fetchone()
            total_events, distinct_trials = (row[0], row[1]) if row else (0, 0)
        conn.close()
        return {"total_events": total_events, "distinct_trials": distinct_trials}
    except ImportError:
        return {"error": "psycopg not installed"}
    except Exception as exc:
        return {"error": str(exc)[:200]}


def _check_sanctum_mutations_7d() -> dict[str, Any]:
    """Query ledger for sanctum_mutation events in last 7 days."""
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        return {"state": "DATABASE_URL not set"}
    try:
        import psycopg
        conn = psycopg.connect(db_url, connect_timeout=5)
        with conn.cursor() as cur:
            cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'ledger_events')")
            row = cur.fetchone()
            if not row or not row[0]:
                conn.close()
                return {"state": "ledger_events table not loaded"}
            cutoff = datetime.now(UTC) - timedelta(days=7)
            cur.execute(
                "SELECT COUNT(*) FROM ledger_events WHERE kind = 'sanctum_mutation' AND created_at >= %s",
                (cutoff,)
            )
            row = cur.fetchone()
            count = row[0] if row else 0
        conn.close()
        return {"count": count, "window": "7 days"}
    except ImportError:
        return {"error": "psycopg not installed"}
    except Exception as exc:
        return {"error": str(exc)[:200]}


def _detect_master_status() -> str:
    path = REPO_ROOT / "_bmad-output" / "implementation-artifacts" / "sprint-status.yaml"
    if not path.is_file():
        return "unknown"
    content = path.read_text(encoding="utf-8")
    if "migration-master-status: shipped" in content:
        return "shipped"
    if "migration-master-status: iterate-pending" in content:
        return "iterate-pending"
    if "migration-master-status: rolled-back" in content:
        return "rolled-back"
    return "in-flight"


def collect_health() -> HealthReport:
    return HealthReport(
        timestamp=datetime.now(UTC).isoformat(),
        sprint_summary=_parse_sprint_status(),
        conditional_milestones=_detect_conditional_milestones(),
        deferred_inventory=_count_deferred_inventory(),
        import_linter=_check_import_linter(),
        ruff_debt=_count_ruff_debt(),
        test_collection=_test_collection_summary(),
        trial_replay=_check_trial_replay_last_run(),
        ledger=_check_ledger(),
        sanctum_mutations_7d=_check_sanctum_mutations_7d(),
        migration_master_status=_detect_master_status(),
    )


def render_text(report: HealthReport) -> str:
    lines = [
        "=== Migration Health Dashboard ===",
        f"Timestamp: {report.timestamp}",
        f"Master status: {report.migration_master_status}",
        "",
        "--- Sprint Progress ---",
    ]
    epics = report.sprint_summary.get("epics", {})
    for k, v in epics.items():
        lines.append(f"  {k}: {v}")
    states = report.sprint_summary.get("story_states", {})
    state_parts = [f"{k}={v}" for k, v in states.items() if v > 0]
    lines.append(f"  Story states: {', '.join(state_parts)}")
    lines.append(f"  Total stories: {report.sprint_summary.get('total_stories', 'unknown')}")
    lines.append("")
    lines.append("--- Conditional Milestones ---")
    for cm in report.conditional_milestones:
        lines.append(f"  {cm['milestone']}: {cm['state']}")
    lines.append("")
    lines.append("--- Deferred Inventory ---")
    lines.append(f"  Total table rows: {report.deferred_inventory.get('total_table_rows', 'unknown')}")
    lines.append("")
    lines.append("--- Import-Linter Contracts ---")
    if "kept" in report.import_linter:
        lines.append(f"  KEPT: {report.import_linter['kept']}, BROKEN: {report.import_linter['broken']}")
    else:
        lines.append(f"  {report.import_linter}")
    lines.append("")
    lines.append("--- Ruff Debt ---")
    if "errors" in report.ruff_debt:
        lines.append(f"  Errors: {report.ruff_debt['errors']}")
    else:
        lines.append(f"  {report.ruff_debt}")
    lines.append("")
    lines.append("--- Test Collection ---")
    if "collected" in report.test_collection:
        lines.append(f"  Collected: {report.test_collection['collected']}; collection errors: {report.test_collection.get('collection_errors', 0)}")
    else:
        lines.append(f"  {report.test_collection}")
    lines.append("")
    lines.append("--- Ledger ---")
    if "total_events" in report.ledger:
        lines.append(f"  Total events: {report.ledger['total_events']}; distinct trials: {report.ledger['distinct_trials']}")
    else:
        lines.append(f"  {report.ledger.get('state', report.ledger.get('error', 'unknown'))}")
    lines.append("")
    lines.append("--- Sanctum Mutations (7d) ---")
    if "count" in report.sanctum_mutations_7d:
        lines.append(f"  Count: {report.sanctum_mutations_7d['count']}")
    else:
        lines.append(f"  {report.sanctum_mutations_7d.get('state', report.sanctum_mutations_7d.get('error', 'unknown'))}")
    lines.append("")
    lines.append("--- Trial Replay ---")
    lines.append(f"  {report.trial_replay.get('state', 'unknown')}")
    return "\n".join(lines)


def render_json(report: HealthReport) -> str:
    return json.dumps(
        {
            "timestamp": report.timestamp,
            "migration_master_status": report.migration_master_status,
            "sprint_summary": report.sprint_summary,
            "conditional_milestones": report.conditional_milestones,
            "deferred_inventory": report.deferred_inventory,
            "import_linter": report.import_linter,
            "ruff_debt": report.ruff_debt,
            "test_collection": report.test_collection,
            "trial_replay": report.trial_replay,
            "ledger": report.ledger,
            "sanctum_mutations_7d": report.sanctum_mutations_7d,
        },
        indent=2,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()
    report = collect_health()
    output = render_json(report) if args.json else render_text(report)
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
