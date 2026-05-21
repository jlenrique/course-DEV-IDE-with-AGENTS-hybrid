# /// script
# requires-python = ">=3.10"
# ///
"""Production intelligence and run reporting.

Builds run completion reports with stage timing, quality results,
observability insights, bottlenecks, and comparative run analysis.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import logging
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

LOGGER = logging.getLogger(__name__)

try:
    from scripts.utilities.ad_hoc_persistence_guard import enforce_ad_hoc_boundary
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

    _guard_mod = _load_util_module("ad_hoc_persistence_guard.py", "ad_hoc_persistence_guard_local")
    _file_mod = _load_util_module("file_helpers.py", "file_helpers_local")
    enforce_ad_hoc_boundary = _guard_mod.enforce_ad_hoc_boundary
    project_root = _file_mod.project_root


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _connect(db_path: Path | str | None = None) -> sqlite3.Connection:
    path = Path(db_path) if db_path else project_root() / "state" / "runtime" / "coordination.db"
    if not path.exists():
        raise FileNotFoundError(f"Database not found: {path}")
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def _parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    candidates = [value]
    if value.endswith("Z"):
        candidates.append(value.replace("Z", "+00:00"))
    for item in candidates:
        try:
            parsed = datetime.fromisoformat(item)
            if parsed.tzinfo is None:
                return parsed.replace(tzinfo=UTC)
            return parsed.astimezone(UTC)
        except ValueError:
            continue
    return None


def _duration_seconds(start: str | None, end: str | None) -> float | None:
    start_dt = _parse_ts(start)
    end_dt = _parse_ts(end)
    if not start_dt or not end_dt:
        return None
    return round((end_dt - start_dt).total_seconds(), 2)


def _parse_context(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {}


def _stage_timings(context: dict[str, Any]) -> list[dict[str, Any]]:
    stages = context.get("stages", [])
    metrics: list[dict[str, Any]] = []
    for idx, stage in enumerate(stages):
        started = stage.get("stage_started_at") or stage.get("started_at")
        completed = stage.get("stage_completed_at") or stage.get("completed_at")
        metrics.append(
            {
                "index": idx,
                "stage": stage.get("stage", f"stage-{idx}"),
                "status": stage.get("status", "unknown"),
                "started_at": started,
                "completed_at": completed,
                "duration_seconds": _duration_seconds(started, completed),
                "specialist": stage.get("specialist"),
            }
        )
    return metrics


def _summarize_quality(conn: sqlite3.Connection, run_id: str) -> dict[str, Any]:
    rows = conn.execute(
        "SELECT stage, status, score, reviewer, decided_at FROM quality_gates WHERE run_id = ?",
        (run_id,),
    ).fetchall()
    if not rows:
        return {
            "count": 0,
            "pass_count": 0,
            "fail_count": 0,
            "avg_score": None,
            "rows": [],
        }

    pass_count = sum(
        1
        for r in rows
        if str(r["status"]).startswith("pass") or str(r["status"]) == "approved"
    )
    fail_count = sum(1 for r in rows if str(r["status"]).startswith("fail"))
    scores = [float(r["score"]) for r in rows if r["score"] is not None]
    avg = round(sum(scores) / len(scores), 4) if scores else None

    return {
        "count": len(rows),
        "pass_count": pass_count,
        "fail_count": fail_count,
        "avg_score": avg,
        "rows": [dict(r) for r in rows],
    }


def _summarize_coordination(conn: sqlite3.Connection, run_id: str) -> dict[str, Any]:
    rows = conn.execute(
        (
            "SELECT agent_name, action, payload_json, timestamp "
            "FROM agent_coordination WHERE run_id = ? ORDER BY timestamp ASC"
        ),
        (run_id,),
    ).fetchall()
    return {
        "count": len(rows),
        "rows": [dict(r) for r in rows],
    }


def _observability_summary(run_id: str, db_path: Path | str | None = None) -> dict[str, Any]:
    try:
        from observability_hooks import summarize_run

        return summarize_run(run_id, db_path=str(db_path) if db_path else None)
    except Exception as exc:
        LOGGER.warning(
            "Observability summary failed for run_id=%s: %s",
            run_id,
            exc,
            exc_info=True,
        )
        return {
            "run_id": run_id,
            "gate_pass_rate": None,
            "fidelity_oia": {"omissions": 0, "inventions": 0, "alterations": 0},
            "quality_dimension_averages": {},
            "governance_findings": [],
            "cache_metrics": {"hits": 0, "misses": 0, "hit_rate": None},
            "error": "observability summary unavailable",
            "observability_error_type": type(exc).__name__,
            "observability_error_message": str(exc),
        }


def _comparative_analysis(
    conn: sqlite3.Connection,
    *,
    run_id: str,
    course_code: str,
    module_id: str,
    current_duration: float | None,
) -> dict[str, Any]:
    rows = conn.execute(
        """
        SELECT run_id, status, started_at, completed_at, context_json
        FROM production_runs
        WHERE run_id != ? AND course_code = ? AND module_id = ?
        ORDER BY updated_at DESC
        LIMIT 10
        """,
        (run_id, course_code, module_id),
    ).fetchall()

    baseline_durations: list[float] = []
    baseline_ids: list[str] = []
    for row in rows:
        context = _parse_context(row["context_json"])
        if context.get("mode") == "ad-hoc":
            continue
        dur = _duration_seconds(row["started_at"], row["completed_at"])
        if dur is not None:
            baseline_durations.append(dur)
            baseline_ids.append(str(row["run_id"]))

    baseline_avg = (
        round(sum(baseline_durations) / len(baseline_durations), 2)
        if baseline_durations
        else None
    )
    delta = (
        round(current_duration - baseline_avg, 2)
        if (current_duration is not None and baseline_avg is not None)
        else None
    )

    trend = None
    if delta is not None:
        trend = "faster" if delta < 0 else "slower" if delta > 0 else "unchanged"

    return {
        "baseline_run_ids": baseline_ids,
        "baseline_count": len(baseline_ids),
        "baseline_avg_duration_seconds": baseline_avg,
        "current_vs_baseline_seconds": delta,
        "trend": trend,
        "ad_hoc_excluded": True,
    }


def _recommendations(
    *,
    bottlenecks: list[dict[str, Any]],
    quality: dict[str, Any],
    observability: dict[str, Any],
) -> list[str]:
    recs: list[str] = []
    if bottlenecks:
        recs.append(
            f"Review stage '{bottlenecks[0]['stage']}' for task decomposition "
            "or parallelization; it is the longest step."
        )
    if quality.get("fail_count", 0) > 0:
        recs.append(
            "Add a pre-gate checklist for recurring quality failures before specialist handoff."
        )
    if observability.get("governance_findings"):
        recs.append(
            "Address lane-boundary findings by tightening decision_scope in delegation envelopes."
        )
    if not recs:
        recs.append(
            "Current workflow is stable; continue with the same preset and monitor cache hit rate."
        )
    return recs


def _summarize_motion_plan(context: dict[str, Any]) -> dict[str, Any] | None:
    if not bool(context.get("motion_enabled", False)):
        return None

    context_paths = context.get("context_paths", {})
    motion_plan_path = None
    if isinstance(context_paths, dict):
        motion_plan_path = context_paths.get("motion_plan")
    if not motion_plan_path:
        return {
            "motion_enabled": True,
            "clips_generated": 0,
            "animations_imported": 0,
            "total_motion_duration_seconds": 0.0,
            "kling_credits_consumed": 0.0,
            "error": "motion_plan unavailable",
        }

    path = Path(str(motion_plan_path))
    if not path.is_file():
        return {
            "motion_enabled": True,
            "clips_generated": 0,
            "animations_imported": 0,
            "total_motion_duration_seconds": 0.0,
            "kling_credits_consumed": 0.0,
            "error": f"motion_plan not found: {path}",
        }

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    slides = data.get("slides", []) if isinstance(data, dict) else []
    clips_generated = 0
    animations_imported = 0
    total_duration = 0.0
    kling_credits_consumed = 0.0
    for row in slides:
        if not isinstance(row, dict):
            continue
        motion_type = str(row.get("motion_type") or "static").strip().lower()
        duration = row.get("motion_duration_seconds")
        if isinstance(duration, (int, float)):
            total_duration += float(duration)
        if motion_type == "video":
            if row.get("motion_status") in {"generated", "approved"}:
                clips_generated += 1
            credits = row.get("credits_consumed", row.get("estimated_credits"))
            if isinstance(credits, (int, float)):
                kling_credits_consumed += float(credits)
        elif motion_type == "animation" and row.get("motion_status") in {"imported", "approved"}:
            animations_imported += 1

    return {
        "motion_enabled": True,
        "clips_generated": clips_generated,
        "animations_imported": animations_imported,
        "total_motion_duration_seconds": round(total_duration, 2),
        "kling_credits_consumed": round(kling_credits_consumed, 2),
        "motion_plan_path": str(path),
    }


def _capture_learning_insights(report: dict[str, Any], run_mode: str) -> dict[str, Any]:
    guard = enforce_ad_hoc_boundary("durable_memory_patterns", run_mode)
    if not guard["allowed"]:
        return {"captured": False, "code": guard["code"], "reason": guard["reason"]}

    patterns_path = (
        project_root() / "_bmad" / "memory" / "marcus-sidecar" / "patterns.md"
    )
    patterns_path.parent.mkdir(parents=True, exist_ok=True)

    bottlenecks = report.get("bottlenecks") or []
    recommendations = report.get("optimization_recommendations") or []
    longest_stage = bottlenecks[0]["stage"] if bottlenecks else "n/a"
    top_recommendation = recommendations[0] if recommendations else "n/a"

    lines = [
        f"\n## Run {report['run_id']} ({_now()})",
        f"- Longest stage: {longest_stage}",
        f"- Gate pass rate: {report['observability'].get('gate_pass_rate')}",
        f"- Cache hit rate: {report['observability'].get('cache_metrics', {}).get('hit_rate')}",
        f"- Recommendation: {top_recommendation}",
    ]
    with patterns_path.open("a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return {"captured": True, "path": str(patterns_path)}


def generate_run_report(
    *,
    run_id: str,
    db_path: Path | str | None = None,
    write_report: bool = True,
    capture_learning: bool = True,
) -> dict[str, Any]:
    conn = _connect(db_path)
    try:
        row = conn.execute("SELECT * FROM production_runs WHERE run_id = ?", (run_id,)).fetchone()
        if not row:
            return {"error": f"Run not found: {run_id}"}

        context = _parse_context(row["context_json"])
        stage_metrics = _stage_timings(context)
        stage_durations = [s for s in stage_metrics if s["duration_seconds"] is not None]
        stage_durations.sort(key=lambda item: item["duration_seconds"], reverse=True)
        bottlenecks = stage_durations[:3]

        quality = _summarize_quality(conn, run_id)
        coordination = _summarize_coordination(conn, run_id)
        observability = _observability_summary(run_id, db_path=db_path)

        started = row["started_at"]
        ended = row["completed_at"] or row["updated_at"]
        total_duration = _duration_seconds(started, ended)

        comparative = _comparative_analysis(
            conn,
            run_id=run_id,
            course_code=str(row["course_code"] or ""),
            module_id=str(row["module_id"] or ""),
            current_duration=total_duration,
        )

        effectiveness = {
            "completed_stage_count": sum(1 for s in stage_metrics if s["status"] == "approved"),
            "rework_signals": sum(
                1
                for s in stage_metrics
                if s["status"] in {"awaiting-review", "rework", "failed"}
            ),
            "quality_gate_failures": quality["fail_count"],
        }

        is_double_dispatch = bool(context.get("double_dispatch", False))

        report = {
            "run_id": run_id,
            "run_mode": context.get("mode", "default"),
            "double_dispatch": is_double_dispatch,
            "motion_enabled": bool(context.get("motion_enabled", False)),
            "run_purpose": row["purpose"],
            "status": row["status"],
            "preset": row["preset"],
            "started_at": started,
            "ended_at": ended,
            "total_duration_seconds": total_duration,
            "stage_metrics": stage_metrics,
            "quality_gate_results": quality,
            "effectiveness_analysis": effectiveness,
            "coordination": coordination,
            "observability": observability,
            "bottlenecks": bottlenecks,
            "optimization_recommendations": _recommendations(
                bottlenecks=bottlenecks,
                quality=quality,
                observability=observability,
            ),
            "comparative_analysis": comparative,
            "orchestrator_summary": "Here's how the run went...",
            "generated_at": _now(),
        }

        if is_double_dispatch:
            report["cost_estimation"] = {
                "gamma_call_multiplier": 2,
                "note": "Double-dispatch mode: 2x Gamma API calls for A/B variant comparison.",
            }
        motion_metrics = _summarize_motion_plan(context)
        if motion_metrics is not None:
            report["motion_metrics"] = motion_metrics
    finally:
        conn.close()

    learning_capture = (
        _capture_learning_insights(report, report["run_mode"])
        if capture_learning
        else {"captured": False, "reason": "capture disabled"}
    )
    report["learning_insights_capture"] = learning_capture

    output_path = None
    if write_report:
        output_path = (
            project_root() / "skills" / "reports" / "production-runs" / run_id / "run-report.json"
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        report["report_path"] = str(output_path)

    return report


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate production run intelligence report")
    parser.add_argument("--db", help="Override coordination database path")
    parser.add_argument("run_id", help="Production run id")
    parser.add_argument("--no-write", action="store_true", help="Do not write report to file")
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)
    result = generate_run_report(
        run_id=args.run_id,
        db_path=args.db,
        write_report=not args.no_write,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
