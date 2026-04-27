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


def _autoload_dotenv() -> None:
    """Auto-load .env at startup so DATABASE_URL + LANGSMITH + per-API checks
    reflect operator's real .env state without requiring shell sourcing."""
    try:
        sys.path.insert(0, str(REPO_ROOT))
        from scripts.utilities.env_loader import load_env
        load_env()
    except (FileNotFoundError, ImportError):
        pass


_autoload_dotenv()


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
    # Slab-4 + Slab-5a metrics (added Tier-2-E 2026-04-26)
    frozen_graph_v42: dict[str, Any] = field(default_factory=dict)
    sanctum_watcher: dict[str, Any] = field(default_factory=dict)
    storypoint_burndown: dict[str, Any] = field(default_factory=dict)
    replay_suite: dict[str, Any] = field(default_factory=dict)
    cost_reports: dict[str, Any] = field(default_factory=dict)
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
        verdict_match = re.search(r"Consensus verdict:\s*([A-Z-]+)", content)
        verdict = verdict_match.group(1) if verdict_match else ""
        if verdict == "CONDITIONAL-GREEN":
            results.append({"milestone": milestone, "state": "CONDITIONAL-GREEN-PENDING-OPERATOR-ADDENDUM", "artifact": str(path.relative_to(REPO_ROOT))})
        elif verdict == "GREEN-LIGHT":
            results.append({"milestone": milestone, "state": "GREEN-LIGHT", "artifact": str(path.relative_to(REPO_ROOT))})
        elif verdict == "GREEN-WITH-RIDERS":
            results.append({"milestone": milestone, "state": "GREEN-WITH-RIDERS", "artifact": str(path.relative_to(REPO_ROOT))})
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


def _check_frozen_graph_v42() -> dict[str, Any]:
    """Verify Slab 4.5 frozen-graph artifacts + digest sha256-shape (added Tier-2-E)."""
    v42_dir = REPO_ROOT / "runtime" / "graphs" / "v42"
    if not v42_dir.is_dir():
        return {"state": "Slab-4.5 not yet shipped (runtime/graphs/v42/ absent)"}
    expected = ["manifest-snapshot.yaml", "pack-version.txt", "compiled-graph-digest.txt"]
    present = [a for a in expected if (v42_dir / a).is_file()]
    digest_path = v42_dir / "compiled-graph-digest.txt"
    digest_state = "absent"
    digest_prefix = ""
    if digest_path.is_file():
        digest = digest_path.read_text(encoding="utf-8").strip()
        if len(digest) == 64 and all(c in "0123456789abcdef" for c in digest.lower()):
            digest_state = "sha256-shaped"
            digest_prefix = f"{digest[:8]}...{digest[-8:]}"
        elif digest:
            digest_state = "non-sha256"
            digest_prefix = digest[:30]
    pack_version = ""
    if (v42_dir / "pack-version.txt").is_file():
        pack_version = (v42_dir / "pack-version.txt").read_text(encoding="utf-8").strip()
    return {
        "artifacts_present": len(present),
        "artifacts_expected": len(expected),
        "digest_state": digest_state,
        "digest_prefix": digest_prefix,
        "pack_version": pack_version,
    }


def _check_sanctum_watcher() -> dict[str, Any]:
    """Verify Slab 4.6 sanctum_watcher module + watchdog dep (added Tier-2-E)."""
    watcher_path = REPO_ROOT / "app" / "runtime" / "sanctum_watcher.py"
    state = {"module_present": watcher_path.is_file()}
    try:
        import watchdog
        state["watchdog_dep"] = "installed"
        state["watchdog_version"] = getattr(watchdog, "__version__", "unknown")
    except ImportError:
        state["watchdog_dep"] = "MISSING — pip install watchdog"
    return state


def _compute_storypoint_burndown() -> dict[str, Any]:
    """Per-Slab story-point burndown roll-up (added Tier-2-E)."""
    path = REPO_ROOT / "_bmad-output" / "implementation-artifacts" / "sprint-status.yaml"
    if not path.is_file():
        return {"error": "sprint-status.yaml not found"}
    content = path.read_text(encoding="utf-8")
    # Heuristic: count `done` rows per Slab prefix
    slab_done = {"1": 0, "2a": 0, "2b": 0, "2c": 0, "3": 0, "4": 0, "5a": 0}
    for line in content.split("\n"):
        s = line.strip()
        for prefix in slab_done:
            if s.startswith(f"migration-{prefix}-") or s.startswith(f"migration-{prefix}.") or s.startswith(f"migration-2{prefix[1:] if prefix.startswith('2') else ''}-"):
                if ": done" in s:
                    slab_done[prefix] += 1
                    break
    return {
        "stories_done_per_slab": slab_done,
        "total_done": sum(slab_done.values()),
    }


def _check_replay_suite_status() -> dict[str, Any]:
    """Verify Slab 5a.1 trial-replay status + GHA workflow presence (added Tier-2-E)."""
    replay_dir = REPO_ROOT / "tests" / "trial_replay"
    workflow = REPO_ROOT / ".github" / "workflows" / "trial-replay.yml"
    if not replay_dir.is_dir():
        return {"state": "Slab-5a.1 not yet shipped (tests/trial_replay/ absent)"}
    py_files = list(replay_dir.glob("test_*.py"))
    return {
        "test_files": len(py_files),
        "workflow_present": workflow.is_file(),
        "workflow_path": str(workflow.relative_to(REPO_ROOT)) if workflow.is_file() else None,
    }


def _check_cost_reports() -> dict[str, Any]:
    """Summarize persisted per-trial economics artifacts (added Tier-2-F)."""

    try:
        sys.path.insert(0, str(REPO_ROOT))
        from app.runtime.economics import summarize_cost_reports
    except ImportError as exc:
        return {"error": str(exc)}
    return summarize_cost_reports()


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
        # Tier-2-E additions (post-Slab-4 close)
        frozen_graph_v42=_check_frozen_graph_v42(),
        sanctum_watcher=_check_sanctum_watcher(),
        storypoint_burndown=_compute_storypoint_burndown(),
        replay_suite=_check_replay_suite_status(),
        cost_reports=_check_cost_reports(),
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
    lines.append("")
    lines.append("--- Frozen-Graph v42 (Slab 4.5) ---")
    fg = report.frozen_graph_v42
    if "artifacts_present" in fg:
        lines.append(f"  Artifacts: {fg['artifacts_present']}/{fg['artifacts_expected']}; pack-version: {fg.get('pack_version', 'unknown')}")
        lines.append(f"  Digest: {fg.get('digest_state', 'unknown')} ({fg.get('digest_prefix', 'n/a')})")
    else:
        lines.append(f"  {fg.get('state', 'unknown')}")
    lines.append("")
    lines.append("--- Sanctum Watcher (Slab 4.6) ---")
    sw = report.sanctum_watcher
    lines.append(f"  Module: {'present' if sw.get('module_present') else 'ABSENT'}; watchdog dep: {sw.get('watchdog_dep', 'unknown')}")
    lines.append("")
    lines.append("--- Story-Point Burndown ---")
    bd = report.storypoint_burndown
    if "stories_done_per_slab" in bd:
        per_slab = ", ".join(f"Slab{k}={v}" for k, v in bd["stories_done_per_slab"].items() if v > 0)
        lines.append(f"  Done by slab: {per_slab}")
        lines.append(f"  Total done: {bd['total_done']}")
    else:
        lines.append(f"  {bd}")
    lines.append("")
    lines.append("--- Replay Suite (Slab 5a.1) ---")
    rs = report.replay_suite
    if "test_files" in rs:
        wf = "PRESENT" if rs.get("workflow_present") else "ABSENT"
        lines.append(f"  Test files: {rs['test_files']}; GHA workflow: {wf}")
    else:
        lines.append(f"  {rs.get('state', 'unknown')}")
    lines.append("")
    lines.append("--- Cost Reports (Slab 5a.3) ---")
    cr = report.cost_reports
    if "trials_with_cost_reports" in cr:
        lines.append(f"  Trials with cost reports: {cr['trials_with_cost_reports']}")
        lines.append(
            "  Median trial cost USD (last 5): "
            f"{cr['median_trial_cost_last_5'] if cr['median_trial_cost_last_5'] is not None else 'n/a'}"
        )
        lines.append(f"  Drift alerts (last 24h): {cr['drift_alerts_last_24h']}")
    else:
        lines.append(f"  {cr.get('error', 'unknown')}")
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
            "frozen_graph_v42": report.frozen_graph_v42,
            "sanctum_watcher": report.sanctum_watcher,
            "storypoint_burndown": report.storypoint_burndown,
            "replay_suite": report.replay_suite,
            "cost_reports": report.cost_reports,
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
