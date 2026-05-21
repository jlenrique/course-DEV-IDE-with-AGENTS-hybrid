# /// script
# requires-python = ">=3.10"
# ///
"""Predictive workflow optimization for Marcus (Story 10.1).

Uses historical production run telemetry to suggest:
- optimized workflow sequence for a new run
- predicted bottlenecks with preemptive mitigation
- resource allocation guidance
- explicit accept/modify/override options for conversational control
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

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


def _parse_ts(value: str | None) -> datetime | None:
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
        payload = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _db_path(db_path: Path | str | None = None) -> Path:
    if db_path:
        return Path(db_path)
    return project_root() / "state" / "runtime" / "coordination.db"


def _connect(db_path: Path | str | None = None) -> sqlite3.Connection:
    path = _db_path(db_path)
    if not path.exists():
        raise FileNotFoundError(f"Database not found: {path}")
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def _load_similar_runs(
    conn: sqlite3.Connection,
    *,
    run_context: dict[str, Any],
    history_limit: int,
) -> list[dict[str, Any]]:
    course_code = str(run_context.get("course_code") or "").strip()
    module_id = str(run_context.get("module_id") or "").strip()
    preset = str(run_context.get("preset") or "").strip()

    clauses: list[str] = ["status = 'completed'"]
    params: list[Any] = []

    if course_code:
        clauses.append("course_code = ?")
        params.append(course_code)
    if module_id:
        clauses.append("module_id = ?")
        params.append(module_id)
    if preset:
        clauses.append("preset = ?")
        params.append(preset)

    where_clause = " AND ".join(clauses) if clauses else "1=1"
    query = (
        "SELECT run_id, purpose, preset, context_json, started_at, completed_at, updated_at "
        f"FROM production_runs WHERE {where_clause} "
        "ORDER BY updated_at DESC LIMIT ?"
    )
    params.append(history_limit)

    rows = conn.execute(query, tuple(params)).fetchall()
    return [dict(row) for row in rows]


def _mitigation_for_stage(stage_name: str) -> str:
    lowered = stage_name.lower()
    if "review" in lowered or "gate" in lowered:
        return "Pre-stage checklist and earlier self-review reduce downstream gate delays."
    if "draft" in lowered or "outline" in lowered:
        return "Front-load source bundle and scope constraints before drafting."
    if "render" in lowered or "synthesis" in lowered:
        return "Batch heavy generation tasks and reserve fallback rendering windows."
    return "Consider decomposition or parallel handoff to reduce single-stage dwell time."


def suggest_predictive_workflow(
    *,
    run_context: dict[str, Any],
    db_path: Path | str | None = None,
    history_limit: int = 20,
    write_report: bool = True,
    output_path: Path | str | None = None,
) -> dict[str, Any]:
    similar_runs: list[dict[str, Any]] = []
    ad_hoc_excluded = 0

    sequence_counts: Counter[tuple[str, ...]] = Counter()
    stage_duration_map: defaultdict[str, list[float]] = defaultdict(list)
    specialist_usage: Counter[str] = Counter()

    try:
        conn = _connect(db_path)
    except FileNotFoundError:
        conn = None

    if conn is not None:
        try:
            raw_runs = _load_similar_runs(
                conn,
                run_context=run_context,
                history_limit=history_limit,
            )
        finally:
            conn.close()

        for run in raw_runs:
            context = _parse_context(run.get("context_json"))
            if context.get("mode") == "ad-hoc":
                ad_hoc_excluded += 1
                continue

            stages = context.get("stages") if isinstance(context.get("stages"), list) else []
            sequence: list[str] = []
            for stage in stages:
                if not isinstance(stage, dict):
                    continue
                stage_name = str(stage.get("stage") or "").strip()
                if not stage_name:
                    continue
                sequence.append(stage_name)

                started = stage.get("stage_started_at") or stage.get("started_at")
                completed = stage.get("stage_completed_at") or stage.get("completed_at")
                duration = _duration_seconds(started, completed)
                if duration is not None:
                    stage_duration_map[stage_name].append(duration)

                specialist = str(stage.get("specialist") or "").strip()
                if specialist:
                    specialist_usage[specialist] += 1

            if sequence:
                sequence_counts[tuple(sequence)] += 1
                similar_runs.append(
                    {
                        "run_id": run.get("run_id"),
                        "sequence": sequence,
                    }
                )

    best_sequence = list(sequence_counts.most_common(1)[0][0]) if sequence_counts else []

    if not best_sequence and isinstance(run_context.get("stages"), list):
        best_sequence = [
            str(stage.get("stage") or "")
            for stage in run_context["stages"]
            if isinstance(stage, dict) and stage.get("stage")
        ]

    bottlenecks: list[dict[str, Any]] = []
    for stage_name, durations in stage_duration_map.items():
        if not durations:
            continue
        avg_duration = round(sum(durations) / len(durations), 2)
        bottlenecks.append(
            {
                "stage": stage_name,
                "average_duration_seconds": avg_duration,
                "sample_size": len(durations),
                "mitigation": _mitigation_for_stage(stage_name),
            }
        )
    bottlenecks.sort(key=lambda item: item["average_duration_seconds"], reverse=True)

    resource_suggestions: list[dict[str, Any]] = []
    for specialist, count in specialist_usage.most_common(5):
        suggestion = "Maintain current assignment cadence."
        if count >= 3:
            suggestion = "Reserve this specialist earlier to avoid queue contention."
        resource_suggestions.append(
            {
                "specialist": specialist,
                "historical_stage_count": count,
                "suggestion": suggestion,
            }
        )

    confidence_label = "low"
    if len(similar_runs) >= 5:
        confidence_label = "high"
    elif len(similar_runs) >= 2:
        confidence_label = "medium"

    recommendation = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "run_context": run_context,
        "similar_runs_considered": len(similar_runs),
        "similar_run_ids": [item.get("run_id") for item in similar_runs],
        "ad_hoc_runs_excluded": ad_hoc_excluded,
        "workflow_sequence_recommendation": {
            "recommended_sequence": best_sequence,
            "confidence": confidence_label,
        },
        "predicted_bottlenecks": bottlenecks[:3],
        "resource_allocation_suggestions": resource_suggestions,
        "options": {
            "accept": {
                "action": "use_recommended_sequence",
                "sequence": best_sequence,
            },
            "modify": "Adjust stage order or specialist assignment, then re-run prediction.",
            "override": "Proceed with custom workflow and capture reason for sidecar learning.",
        },
    }

    if write_report:
        if output_path:
            target = Path(output_path)
        else:
            slug = "-".join(
                filter(
                    None,
                    [
                        str(run_context.get("course_code") or "na"),
                        str(run_context.get("module_id") or "na"),
                        datetime.now().strftime("%Y%m%dT%H%M%S"),
                    ],
                )
            )
            target = (
                project_root()
                / "skills"
                / "reports"
                / "predictive-workflow"
                / f"{slug}.json"
            )
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(recommendation, indent=2), encoding="utf-8")
        recommendation["report_path"] = str(target)

    return recommendation


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate predictive workflow recommendations")
    parser.add_argument("--db", help="Override coordination database path")
    parser.add_argument("--course-code", default="", help="Course code for similarity lookup")
    parser.add_argument("--module-id", default="", help="Module id for similarity lookup")
    parser.add_argument("--preset", default="production", help="Run preset for similarity lookup")
    parser.add_argument("--content-type", default="", help="Optional content type token")
    parser.add_argument("--output", help="Optional output path")
    parser.add_argument("--no-write", action="store_true", help="Do not write report")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    run_context = {
        "course_code": args.course_code,
        "module_id": args.module_id,
        "preset": args.preset,
        "content_type": args.content_type,
    }
    recommendation = suggest_predictive_workflow(
        run_context=run_context,
        db_path=args.db,
        write_report=not args.no_write,
        output_path=args.output,
    )
    print(json.dumps(recommendation, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
