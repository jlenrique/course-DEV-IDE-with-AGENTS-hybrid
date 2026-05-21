"""Migrated-runtime data sources for the operator HUD."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import yaml

from app.models.runtime import TrialEconomicsReport
from app.runtime.cascade_config import CASCADE_PATH, PRICING_PATH
from app.runtime.economics import RUNS_ROOT, summarize_cost_reports
from scripts.utilities.file_helpers import project_root

ROOT = project_root()
UPSTREAM_STATE = ROOT / "_bmad-output" / "upstream-state.md"
DEFERRED_INVENTORY = ROOT / "_bmad-output" / "planning-artifacts" / "deferred-inventory.md"


@dataclass(frozen=True)
class ActiveTrialView:
    trial_id: str
    status: str
    current_step: str
    current_agent: str
    current_model: str
    per_agent_cost: dict[str, float] = field(default_factory=dict)
    langsmith_trace_url: str | None = None
    drift_alerts_last_24h: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CostEngineeringView:
    cascade_preview: dict[str, str]
    pricing_preview: dict[str, dict[str, float]]
    median_trial_cost_last_5: float | None
    soft_cap_budget_usd: float | None


@dataclass(frozen=True)
class M5WindowView:
    visible: bool
    days_remaining: int
    open_conditions: list[dict[str, str]]
    demotion_threshold: str


@dataclass(frozen=True)
class AdhocSummaryView:
    available: bool
    total_cost_last_24h: float | None
    run_count_last_24h: int
    note: str


def _safe_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _load_cost_report(path: Path) -> TrialEconomicsReport | None:
    if not path.is_file():
        return None
    try:
        return TrialEconomicsReport.model_validate_json(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _latest_trial_dir(runs_root: Path) -> Path | None:
    if not runs_root.is_dir():
        return None
    candidates = [path for path in runs_root.iterdir() if path.is_dir()]
    if not candidates:
        return None
    return max(candidates, key=lambda item: item.stat().st_mtime)


def read_active_trial(
    trial_id: str | None,
    *,
    runs_root: Path = RUNS_ROOT,
    now: datetime | None = None,
) -> ActiveTrialView | None:
    """Read the active or latest migrated-runtime trial snapshot."""
    run_dir = runs_root / trial_id if trial_id else _latest_trial_dir(runs_root)
    if run_dir is None or not run_dir.is_dir():
        return None
    resolved_trial_id = trial_id or run_dir.name

    run_payload: dict[str, Any] = {}
    for name in ("trial-start.json", "run.json"):
        path = run_dir / name
        if path.is_file():
            try:
                run_payload = json.loads(path.read_text(encoding="utf-8"))
                break
            except json.JSONDecodeError:
                continue

    report = _load_cost_report(run_dir / "cost-report.json")
    status = str(
        run_payload.get("status")
        or ("complete" if report is not None else "running")
    )
    current_step = str(run_payload.get("current_step") or run_payload.get("preset") or "unknown")
    per_agent_cost: dict[str, float] = {}
    current_agent = "unknown"
    current_model = "unknown"
    trace_url: str | None = None
    drift_alerts: list[str] = []
    if report is not None:
        per_agent_cost = {
            agent: entry.cost_usd
            for agent, entry in report.per_agent_breakdown.items()
        }
        if report.per_agent_breakdown:
            first_agent, first_entry = next(iter(report.per_agent_breakdown.items()))
            current_agent = first_agent
            current_model = first_entry.model_assigned
        trace_url = report.langsmith_trace_url
        cutoff = (now or datetime.now(UTC)) - timedelta(hours=24)
        if report.measured_at >= cutoff:
            drift_alerts = [
                (
                    f"{alert.agent_name}: {alert.deviation_pct:.2f}% "
                    f"vs rolling median"
                )
                for alert in report.drift_alerts
            ]
    return ActiveTrialView(
        trial_id=resolved_trial_id,
        status=status,
        current_step=current_step,
        current_agent=current_agent,
        current_model=current_model,
        per_agent_cost=per_agent_cost,
        langsmith_trace_url=trace_url,
        drift_alerts_last_24h=drift_alerts,
    )


def read_cost_engineering_state(
    *,
    cascade_path: Path = CASCADE_PATH,
    pricing_path: Path = PRICING_PATH,
    runs_root: Path = RUNS_ROOT,
) -> CostEngineeringView:
    """Read model cascade, pricing, recent cost trend, and soft cap."""
    cascade_raw = _safe_yaml(cascade_path)
    pricing_raw = _safe_yaml(pricing_path)
    specialists = cascade_raw.get("specialists", {})
    cascade_preview: dict[str, str] = {}
    marcus = cascade_raw.get("marcus", {})
    if isinstance(marcus, dict) and marcus.get("model"):
        cascade_preview["marcus"] = str(marcus["model"])
    if isinstance(specialists, dict):
        for name, entry in sorted(specialists.items()):
            if isinstance(entry, dict) and entry.get("model"):
                cascade_preview[str(name)] = str(entry["model"])

    pricing_preview: dict[str, dict[str, float]] = {}
    models = pricing_raw.get("models", {})
    if isinstance(models, dict):
        for model_id, row in sorted(models.items()):
            if isinstance(row, dict):
                pricing_preview[str(model_id)] = {
                    "input": float(row.get("input_per_1m_tokens_usd", 0.0)),
                    "output": float(row.get("output_per_1m_tokens_usd", 0.0)),
                }

    summary = summarize_cost_reports(runs_root=runs_root)
    raw_budget = (os.getenv("MARCUS_TRIAL_BUDGET_USD") or "").strip()
    budget = float(raw_budget) if raw_budget else None
    return CostEngineeringView(
        cascade_preview=cascade_preview,
        pricing_preview=pricing_preview,
        median_trial_cost_last_5=summary.get("median_trial_cost_last_5"),
        soft_cap_budget_usd=budget,
    )


def _condition_status(text: str, condition: str) -> str:
    pattern = re.compile(rf"{re.escape(condition)}.*?(closed|resolved|open|pending)", re.I)
    match = pattern.search(text)
    return match.group(1).lower() if match else "open"


def read_m5_window_state(
    *,
    upstream_state_path: Path = UPSTREAM_STATE,
    deferred_inventory_path: Path = DEFERRED_INVENTORY,
    now: datetime | None = None,
) -> M5WindowView:
    """Read M5 conditional-window posture from governance artifacts."""
    text = ""
    for path in (upstream_state_path, deferred_inventory_path):
        if path.is_file():
            text += "\n" + path.read_text(encoding="utf-8", errors="replace")
    deadline = datetime(2026, 5, 3, tzinfo=UTC)
    timestamp = now or datetime.now(UTC)
    days_remaining = max(0, (deadline.date() - timestamp.date()).days)
    visible = timestamp <= deadline or "SHIP-CONDITIONAL" in text
    names = [
        "M2 Wondercraft live artifact",
        "M3 Texas live retrieval",
        "production runner",
        "dispatch-registry swap",
    ]
    return M5WindowView(
        visible=visible,
        days_remaining=days_remaining,
        open_conditions=[
            {"condition": name, "status": _condition_status(text, name)}
            for name in names
        ],
        demotion_threshold="Demote to iterate-pending if unresolved after 2026-05-03.",
    )


def read_adhoc_summary(*, now: datetime | None = None) -> AdhocSummaryView | None:
    """Query the ad-hoc LangSmith project when credentials are available."""
    if os.getenv("PYTEST_CURRENT_TEST"):
        return AdhocSummaryView(
            available=False,
            total_cost_last_24h=None,
            run_count_last_24h=0,
            note="LangSmith query skipped under pytest.",
        )
    if not os.getenv("LANGSMITH_API_KEY"):
        return AdhocSummaryView(
            available=False,
            total_cost_last_24h=None,
            run_count_last_24h=0,
            note="LANGSMITH_API_KEY unset; ad-hoc trace summary unavailable.",
        )
    try:
        from langsmith import Client
    except ImportError:
        return AdhocSummaryView(
            available=False,
            total_cost_last_24h=None,
            run_count_last_24h=0,
            note="langsmith SDK not importable.",
        )
    try:
        client = Client(api_key=os.getenv("LANGSMITH_API_KEY"))
        cutoff = (now or datetime.now(UTC)) - timedelta(hours=24)
        runs = list(
            client.list_runs(
                project_name="course-content-adhoc",
                start_time=cutoff,
                limit=200,
                select=["id"],
            )
        )
    except Exception as exc:
        return AdhocSummaryView(
            available=False,
            total_cost_last_24h=None,
            run_count_last_24h=0,
            note=f"LangSmith query failed: {exc}",
        )
    return AdhocSummaryView(
        available=True,
        total_cost_last_24h=None,
        run_count_last_24h=len(runs),
        note="LangSmith exposes run count here; token-cost rollup remains inline per CLI.",
    )


__all__ = [
    "ActiveTrialView",
    "AdhocSummaryView",
    "CostEngineeringView",
    "M5WindowView",
    "read_active_trial",
    "read_adhoc_summary",
    "read_cost_engineering_state",
    "read_m5_window_state",
]
