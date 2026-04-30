# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Tool ecosystem monitoring and documentation synthesis (Story G.2).

Builds a periodic synthesis report that aggregates:
- Tool documentation refresh signals from tech-spec-wrangler doc-sources files
- Specialist sidecar learning pattern summaries
- Governance health metrics (lane violations, baton redirects, cache performance)
- Prioritized recommendations for docs, agent behavior, and contracts
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ModuleNotFoundError:
    yaml = None  # type: ignore[assignment]

try:
    from scripts.utilities.file_helpers import project_root
except ModuleNotFoundError:
    def _load_util_module(file_name: str, module_name: str) -> Any:
        for parent in Path(__file__).resolve().parents:
            candidate = parent / "scripts" / "utilities" / file_name
            if candidate.exists():
                spec = importlib.util.spec_from_file_location(module_name, candidate)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    return module
        raise

    _file_mod = _load_util_module("file_helpers.py", "file_helpers_local")
    project_root = _file_mod.project_root


THEME_KEYWORDS: dict[str, list[str]] = {
    "recurring_issues": ["issue", "fail", "error", "blocked", "violation", "drift"],
    "calibration_trends": ["calibration", "confidence", "threshold", "tune", "waive"],
    "effective_parameters": ["effective", "works", "sweet spot", "recommend", "best"],
}


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    candidates = [value]
    if value.endswith("Z"):
        candidates.append(value.replace("Z", "+00:00"))
    for candidate in candidates:
        try:
            return datetime.fromisoformat(candidate)
        except ValueError:
            continue
    return None


def _staleness_days(last_refreshed: str | None, now: datetime) -> int | None:
    parsed = _parse_iso(last_refreshed)
    if parsed is None:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return max(0, int((now - parsed).total_seconds() // 86400))


def _load_yaml(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("pyyaml is required for tool ecosystem synthesis")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def collect_tool_capability_changes(root: Path) -> list[dict[str, Any]]:
    now = datetime.now(timezone.utc)
    changes: list[dict[str, Any]] = []
    for path in sorted(root.glob("skills/*/references/doc-sources.yaml")):
        payload = _load_yaml(path)
        tool = str(payload.get("tool") or path.parent.parent.name)
        agent = payload.get("agent")
        sources = payload.get("doc_sources") if isinstance(payload.get("doc_sources"), list) else []
        last_refreshed = payload.get("last_refreshed")
        refresh_notes = payload.get("refresh_notes")

        stale_days = _staleness_days(last_refreshed, now)
        status = "fresh"
        if last_refreshed in (None, ""):
            status = "missing-refresh-metadata"
        elif stale_days is not None and stale_days > 60:
            status = "stale"

        changes.append(
            {
                "tool": tool,
                "agent": agent,
                "doc_sources_path": str(path.relative_to(root)),
                "source_count": len(sources),
                "last_refreshed": last_refreshed,
                "refresh_notes": refresh_notes,
                "staleness_days": stale_days,
                "status": status,
            }
        )
    return changes


def _pattern_lines(path: Path) -> list[str]:
    if not path.exists():
        return []

    text: str
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # Some legacy sidecar files were written in cp1252 on Windows.
        text = path.read_text(encoding="cp1252", errors="replace")

    lines: list[str] = []
    for raw in text.splitlines():
        stripped = raw.strip()
        if stripped.startswith("- "):
            lines.append(stripped[2:])
    return lines


def collect_sidecar_pattern_synthesis(root: Path) -> dict[str, Any]:
    sidecar_root = root / "_bmad" / "memory"
    theme_counts: Counter[str] = Counter()
    per_sidecar: list[dict[str, Any]] = []

    if not sidecar_root.exists():
        return {
            "total_sidecars": 0,
            "sidecars_with_entries": 0,
            "sidecars_without_entries": 0,
            "total_pattern_entries": 0,
            "theme_counts": {},
            "per_sidecar": [],
        }

    for sidecar_dir in sorted(sidecar_root.glob("*-sidecar")):
        patterns_path = sidecar_dir / "patterns.md"
        lines = _pattern_lines(patterns_path)
        lower_lines = [line.lower() for line in lines]

        for line in lower_lines:
            for theme, keywords in THEME_KEYWORDS.items():
                if any(keyword in line for keyword in keywords):
                    theme_counts[theme] += 1

        per_sidecar.append(
            {
                "sidecar": sidecar_dir.name,
                "patterns_path": str(patterns_path.relative_to(root)),
                "entry_count": len(lines),
            }
        )

    with_entries = sum(1 for item in per_sidecar if item["entry_count"] > 0)
    total_entries = sum(int(item["entry_count"]) for item in per_sidecar)

    return {
        "total_sidecars": len(per_sidecar),
        "sidecars_with_entries": with_entries,
        "sidecars_without_entries": len(per_sidecar) - with_entries,
        "total_pattern_entries": total_entries,
        "theme_counts": dict(theme_counts),
        "per_sidecar": per_sidecar,
    }


def _table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    ).fetchone()
    return row is not None


def collect_governance_health_metrics(
    root: Path,
    db_path: Path | str | None = None,
) -> dict[str, Any]:
    path = Path(db_path) if db_path else root / "state" / "runtime" / "coordination.db"
    result: dict[str, Any] = {
        "db_path": str(path),
        "db_available": False,
        "lane_violations": 0,
        "baton_redirects": 0,
        "cache_metrics": {
            "hits": 0,
            "misses": 0,
            "hit_rate": None,
        },
        "errors": [],
    }

    if not path.exists():
        result["errors"].append(f"coordination DB not found: {path}")
        return result

    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    result["db_available"] = True
    try:
        if _table_exists(conn, "observability_events"):
            lane_row = conn.execute(
                "SELECT COUNT(*) AS c FROM observability_events WHERE event_type = 'lane_violation'"
            ).fetchone()
            result["lane_violations"] = int(lane_row["c"] if lane_row else 0)

            cache_row = conn.execute(
                """
                SELECT
                    SUM(CASE WHEN event_type = 'cache_hit' THEN 1 ELSE 0 END) AS hits,
                    SUM(CASE WHEN event_type = 'cache_miss' THEN 1 ELSE 0 END) AS misses
                FROM observability_events
                """
            ).fetchone()
            hits = int(cache_row["hits"] or 0) if cache_row else 0
            misses = int(cache_row["misses"] or 0) if cache_row else 0
            total = hits + misses
            result["cache_metrics"] = {
                "hits": hits,
                "misses": misses,
                "hit_rate": round(hits / total, 4) if total else None,
            }

        if _table_exists(conn, "agent_coordination"):
            redirect_row = conn.execute(
                """
                SELECT COUNT(*) AS c
                FROM agent_coordination
                WHERE lower(action) LIKE '%redirect%'
                   OR lower(coalesce(payload_json, '')) LIKE '%active_baton_redirect%'
                   OR lower(coalesce(payload_json, '')) LIKE '%no_active_baton%'
                """
            ).fetchone()
            result["baton_redirects"] = int(redirect_row["c"] if redirect_row else 0)
    except sqlite3.Error as exc:
        result["errors"].append(str(exc))
    finally:
        conn.close()

    return result


def build_prioritized_recommendations(
    tool_changes: list[dict[str, Any]],
    sidecar_summary: dict[str, Any],
    governance_metrics: dict[str, Any],
) -> list[dict[str, Any]]:
    recommendations: list[dict[str, Any]] = []

    stale_tools = [
        item["tool"]
        for item in tool_changes
        if item["status"] in {"missing-refresh-metadata", "stale"}
    ]
    if stale_tools:
        recommendations.append(
            {
                "priority": "high",
                "category": "doc-updates",
                "title": "Refresh tool documentation metadata",
                "action": (
                    "Update stale doc-sources refresh metadata and notes for: "
                    + ", ".join(stale_tools)
                ),
                "evidence": {"stale_or_missing_tools": stale_tools},
            }
        )

    lane_violations = int(governance_metrics.get("lane_violations", 0))
    if lane_violations > 0:
        recommendations.append(
            {
                "priority": "high",
                "category": "contract-changes",
                "title": "Reduce lane boundary violations",
                "action": (
                    "Tighten delegation envelope decision_scope checks and add "
                    "targeted lane-matrix regression tests."
                ),
                "evidence": {"lane_violations": lane_violations},
            }
        )

    baton_redirects = int(governance_metrics.get("baton_redirects", 0))
    if baton_redirects > 3:
        recommendations.append(
            {
                "priority": "medium",
                "category": "agent-revisions",
                "title": "Improve baton handoff clarity",
                "action": (
                    "Add specialist prompt examples for reroute-to-Marcus and "
                    "standalone consult transitions."
                ),
                "evidence": {"baton_redirects": baton_redirects},
            }
        )

    cache_hit_rate = governance_metrics.get("cache_metrics", {}).get("hit_rate")
    if isinstance(cache_hit_rate, float) and cache_hit_rate < 0.5:
        recommendations.append(
            {
                "priority": "medium",
                "category": "agent-revisions",
                "title": "Increase perception cache reuse",
                "action": (
                    "Review cache key normalization for repeated assets and add "
                    "cache hit instrumentation checks."
                ),
                "evidence": {"cache_hit_rate": cache_hit_rate},
            }
        )

    sidecars_without_entries = int(sidecar_summary.get("sidecars_without_entries", 0))
    total_sidecars = int(sidecar_summary.get("total_sidecars", 0))
    if total_sidecars > 0 and sidecars_without_entries >= max(3, total_sidecars // 2):
        recommendations.append(
            {
                "priority": "medium",
                "category": "agent-revisions",
                "title": "Increase sidecar learning capture",
                "action": (
                    "Add end-of-run prompts so each specialist writes at least one "
                    "pattern entry for completed runs."
                ),
                "evidence": {
                    "sidecars_without_entries": sidecars_without_entries,
                    "total_sidecars": total_sidecars,
                },
            }
        )

    if not recommendations:
        recommendations.append(
            {
                "priority": "low",
                "category": "monitoring",
                "title": "Maintain current synthesis cadence",
                "action": (
                    "No critical issues detected. Continue periodic synthesis and "
                    "monitor trend deltas."
                ),
                "evidence": {},
            }
        )

    priority_order = {"high": 0, "medium": 1, "low": 2}
    recommendations.sort(key=lambda item: priority_order.get(item["priority"], 99))
    return recommendations


def generate_synthesis_report(
    *,
    db_path: Path | str | None = None,
    output_path: Path | str | None = None,
    write_report: bool = True,
) -> dict[str, Any]:
    root = project_root()
    tool_changes = collect_tool_capability_changes(root)
    sidecar_summary = collect_sidecar_pattern_synthesis(root)
    governance_metrics = collect_governance_health_metrics(root, db_path=db_path)
    recommendations = build_prioritized_recommendations(
        tool_changes,
        sidecar_summary,
        governance_metrics,
    )

    report = {
        "generated_at": _now_utc(),
        "tool_capability_changes": tool_changes,
        "sidecar_pattern_synthesis": sidecar_summary,
        "governance_health_metrics": governance_metrics,
        "prioritized_recommendations": recommendations,
        "summary": {
            "tools_monitored": len(tool_changes),
            "sidecars_summarized": sidecar_summary.get("total_sidecars", 0),
            "high_priority_recommendations": sum(
                1 for item in recommendations if item.get("priority") == "high"
            ),
        },
    }

    if write_report:
        target = Path(output_path) if output_path else (
            root
            / "_bmad-output"
            / "implementation-artifacts"
            / "reports"
            / "tool-ecosystem-synthesis-report.json"
        )
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(report, indent=2), encoding="utf-8")
        report["report_path"] = str(target)

    return report


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate tool ecosystem monitoring synthesis report"
    )
    parser.add_argument("--db", help="Override coordination database path")
    parser.add_argument("--output", help="Override report output path")
    parser.add_argument("--no-write", action="store_true", help="Do not write report")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    report = generate_synthesis_report(
        db_path=args.db,
        output_path=args.output,
        write_report=not args.no_write,
    )
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
