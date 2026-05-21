"""Per-trial cost measurement + persistence for the migrated runtime."""

from __future__ import annotations

import json
import os
from collections.abc import Iterable
from datetime import UTC, datetime, timedelta
from pathlib import Path
from statistics import median
from types import SimpleNamespace
from typing import Any

from app.models.runtime import (
    AgentCostEntry,
    BudgetStatus,
    DriftStatus,
    TrialEconomicsReport,
)
from app.runtime.cascade_config import (
    CascadeConfig,
    PricingTable,
    ensure_pricing_covers_cascade,
    load_cascade,
    load_pricing,
    normalize_agent_name,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNS_ROOT = REPO_ROOT / "state" / "config" / "runs"
DEFAULT_LANGSMITH_TRACE_HOST = "https://smith.langchain.com/traces"


def _round_usd(value: float) -> float:
    return round(value, 8)


def _as_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {}


def _get_field(value: Any, name: str, default: Any = None) -> Any:
    if isinstance(value, dict):
        return value.get(name, default)
    return getattr(value, name, default)


def _run_id(value: Any) -> str | None:
    raw = _get_field(value, "id")
    return str(raw) if raw is not None else None


def _flatten_runs(root: Any) -> list[Any]:
    if root is None:
        return []
    flattened: list[Any] = []
    queue = [root]
    seen: set[str] = set()
    while queue:
        current = queue.pop(0)
        identifier = _run_id(current) or f"anon:{id(current)}"
        if identifier in seen:
            continue
        seen.add(identifier)
        flattened.append(current)
        children = _get_field(current, "child_runs", []) or []
        for child in children:
            queue.append(child)
    return flattened


def _extract_metadata(run: Any) -> dict[str, Any]:
    extra = _as_dict(_get_field(run, "extra", {}))
    metadata = extra.get("metadata")
    return metadata if isinstance(metadata, dict) else {}


def _extract_tags(run: Any) -> list[str]:
    tags = _get_field(run, "tags", []) or []
    if isinstance(tags, list):
        return [str(tag) for tag in tags]
    return []


def _extract_agent_name(run: Any) -> str | None:
    metadata = _extract_metadata(run)
    for key in ("specialist_id", "agent", "specialist", "agent_name"):
        value = metadata.get(key)
        if isinstance(value, str) and value.strip():
            return value
    for tag in _extract_tags(run):
        if tag.startswith("specialist:"):
            return tag.split(":", 1)[1]
        if tag.startswith("agent:"):
            return tag.split(":", 1)[1]
    for container in (_get_field(run, "inputs", {}), _get_field(run, "outputs", {})):
        payload = _as_dict(container)
        for key in ("specialist_id", "agent", "agent_name"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value
    name = _get_field(run, "name")
    if isinstance(name, str) and name.strip():
        return name
    return None


def _extract_model_id(run: Any) -> str | None:
    metadata = _extract_metadata(run)
    for key in ("model_id", "model", "resolved"):
        value = metadata.get(key)
        if isinstance(value, str) and value.strip():
            return value
    serialized = _as_dict(_get_field(run, "serialized", {}))
    kwargs = _as_dict(serialized.get("kwargs"))
    for key in ("model_name", "model"):
        value = kwargs.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return None


def _extract_trial_hints(run: Any) -> set[str]:
    hints: set[str] = set()
    metadata = _extract_metadata(run)
    for key in ("trial_id", "run_id"):
        value = metadata.get(key)
        if isinstance(value, str) and value.strip():
            hints.add(value)
    for container in (_get_field(run, "inputs", {}), _get_field(run, "outputs", {})):
        payload = _as_dict(container)
        for key in ("trial_id", "run_id"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                hints.add(value)
    trace_id = _get_field(run, "trace_id")
    if trace_id is not None:
        hints.add(str(trace_id))
    return hints


def _extract_usage(run: Any) -> tuple[int, int]:
    input_tokens = _get_field(run, "prompt_tokens")
    output_tokens = _get_field(run, "completion_tokens")
    if input_tokens is None:
        input_tokens = 0
    if output_tokens is None:
        output_tokens = 0
    return int(input_tokens), int(output_tokens)


def _is_billable_llm_run(run: Any) -> bool:
    input_tokens, output_tokens = _extract_usage(run)
    if input_tokens > 0 or output_tokens > 0:
        return True
    total_tokens = _get_field(run, "total_tokens")
    return int(total_tokens or 0) > 0


def _trace_url_for(run: Any) -> str | None:
    app_path = _get_field(run, "app_path")
    if isinstance(app_path, str) and app_path.strip():
        return app_path
    trace_id = _get_field(run, "trace_id")
    if trace_id is None:
        trace_id = _get_field(run, "id")
    if trace_id is None:
        return None
    return f"{DEFAULT_LANGSMITH_TRACE_HOST}/{trace_id}"


def _load_langsmith_client() -> Any:
    from langsmith import Client

    api_key = os.getenv("LANGSMITH_API_KEY")
    if not api_key:
        raise RuntimeError("LANGSMITH_API_KEY is required to read live traces")
    return Client(api_key=api_key)


def _fetch_trial_trace(
    *,
    trial_id: str,
    client: Any,
    project_name: str,
    limit: int = 200,
) -> Any:
    runs = list(
        client.list_runs(
            project_name=project_name,
            limit=limit,
            select=[
                "id",
                "trace_id",
                "parent_run_id",
                "child_run_ids",
                "name",
                "run_type",
                "extra",
                "inputs",
                "outputs",
                "tags",
                "prompt_tokens",
                "completion_tokens",
                "total_tokens",
                "app_path",
                "serialized",
                "start_time",
            ],
        )
    )
    matched_root: Any | None = None
    for run in runs:
        if trial_id not in _extract_trial_hints(run):
            continue
        if _get_field(run, "parent_run_id") is None:
            matched_root = run
            break
        matched_root = run
    if matched_root is None:
        raise RuntimeError(
            f"no LangSmith trace matched trial_id={trial_id!r} in project {project_name!r}"
        )
    root_id = _get_field(matched_root, "id")
    return client.read_run(root_id, load_child_runs=True)


def _load_report_history(
    *,
    runs_root: Path = RUNS_ROOT,
    exclude_trial_id: str | None = None,
) -> list[TrialEconomicsReport]:
    history: list[TrialEconomicsReport] = []
    if not runs_root.is_dir():
        return history
    for path in runs_root.glob("*/cost-report.json"):
        trial_dir_name = path.parent.name
        if exclude_trial_id is not None and trial_dir_name == exclude_trial_id:
            continue
        try:
            report = TrialEconomicsReport.model_validate_json(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        history.append(report)
    return sorted(history, key=lambda item: item.measured_at)


def check_trial_budget(running_total_usd: float, budget_usd: float | None) -> BudgetStatus:
    """Evaluate the soft-cap budget posture for the current running total."""

    if budget_usd is None:
        return BudgetStatus(state="no-cap", over_by_usd=0.0)
    if budget_usd < 0.0:
        raise ValueError("budget_usd must be non-negative when provided")
    if running_total_usd > budget_usd:
        return BudgetStatus(
            state="over-budget-warning",
            over_by_usd=_round_usd(running_total_usd - budget_usd),
        )
    return BudgetStatus(state="under-budget", over_by_usd=0.0)


def compute_per_agent_drift(
    report: TrialEconomicsReport,
    history: list[TrialEconomicsReport],
) -> dict[str, DriftStatus]:
    """Compare the report against the rolling 5-trial historical median."""

    if len(history) < 5:
        return {}
    trailing = history[-5:]
    alerts: dict[str, DriftStatus] = {}
    for agent_name, entry in report.per_agent_breakdown.items():
        if entry.call_count == 0:
            continue
        observed = entry.cost_usd / entry.call_count
        history_values: list[float] = []
        for prior in trailing:
            prior_entry = prior.per_agent_breakdown.get(agent_name)
            if prior_entry is None or prior_entry.call_count == 0:
                continue
            history_values.append(prior_entry.cost_usd / prior_entry.call_count)
        if len(history_values) < 5:
            continue
        rolling_median = float(median(history_values))
        if rolling_median == 0.0:
            if observed == 0.0:
                continue
            deviation_pct = 100.0
        else:
            deviation_pct = ((observed - rolling_median) / rolling_median) * 100.0
        if abs(deviation_pct) >= 50.0:
            alerts[agent_name] = DriftStatus(
                agent_name=agent_name,
                rolling_median_usd_per_call=_round_usd(rolling_median),
                observed_usd_per_call=_round_usd(observed),
                deviation_pct=round(deviation_pct, 2),
            )
    return alerts


def measure_trial_cost(
    trial_id: str,
    *,
    client: Any | None = None,
    project_name: str | None = None,
    trace_root: Any | None = None,
    trace_runs: Iterable[Any] | None = None,
    history: list[TrialEconomicsReport] | None = None,
    cascade: CascadeConfig | None = None,
    pricing: PricingTable | None = None,
    budget_usd: float | None = None,
) -> TrialEconomicsReport:
    """Read one trial's trace and produce a strict economics report."""

    loaded_cascade = cascade or load_cascade()
    loaded_pricing = pricing or load_pricing()
    ensure_pricing_covers_cascade(loaded_cascade, loaded_pricing)

    effective_client = client
    effective_project = project_name or os.getenv("LANGSMITH_PROJECT")
    if trace_runs is None and trace_root is None:
        if not effective_project:
            raise RuntimeError("LANGSMITH_PROJECT is required to read live traces")
        if effective_client is None:
            effective_client = _load_langsmith_client()
        trace_root = _fetch_trial_trace(
            trial_id=trial_id,
            client=effective_client,
            project_name=effective_project,
        )

    runs = list(trace_runs) if trace_runs is not None else _flatten_runs(trace_root)
    if not runs:
        raise RuntimeError(f"trial_id={trial_id!r} produced no trace runs")

    per_agent: dict[str, dict[str, Any]] = {}
    per_model: dict[str, float] = {}

    for run in runs:
        if not _is_billable_llm_run(run):
            continue
        model_id = _extract_model_id(run)
        if model_id is None:
            raise RuntimeError("billable LangSmith run missing model identifier")
        input_tokens, output_tokens = _extract_usage(run)
        cost_usd = loaded_pricing.compute_cost(
            model_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
        raw_agent_name = _extract_agent_name(run) or "unknown"
        resolved = loaded_cascade.resolve_entry(raw_agent_name)
        canonical_agent = (
            resolved[0] if resolved is not None else normalize_agent_name(raw_agent_name)
        )
        assigned_model = resolved[1].model if resolved is not None else model_id
        bucket = per_agent.setdefault(
            canonical_agent,
            {
                "agent_name": canonical_agent,
                "model_assigned": assigned_model,
                "call_count": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "cost_usd": 0.0,
            },
        )
        bucket["call_count"] += 1
        bucket["input_tokens"] += input_tokens
        bucket["output_tokens"] += output_tokens
        bucket["cost_usd"] += cost_usd
        per_model[model_id] = per_model.get(model_id, 0.0) + cost_usd

    if not per_agent:
        raise RuntimeError(f"trial_id={trial_id!r} had no billable LLM spans")

    per_agent_breakdown = {
        name: AgentCostEntry(
            agent_name=payload["agent_name"],
            model_assigned=payload["model_assigned"],
            call_count=payload["call_count"],
            input_tokens=payload["input_tokens"],
            output_tokens=payload["output_tokens"],
            cost_usd=_round_usd(payload["cost_usd"]),
        )
        for name, payload in sorted(per_agent.items())
    }
    per_model_breakdown = {
        model_id: _round_usd(cost)
        for model_id, cost in sorted(per_model.items())
    }
    total_cost_usd = _round_usd(sum(item.cost_usd for item in per_agent_breakdown.values()))
    measured_at = datetime.now(UTC)
    effective_history = (
        history
        if history is not None
        else _load_report_history(exclude_trial_id=trial_id)
    )
    report_stub = TrialEconomicsReport(
        trial_id=trial_id,
        measured_at=measured_at,
        total_cost_usd=total_cost_usd,
        per_agent_breakdown=per_agent_breakdown,
        per_model_breakdown=per_model_breakdown,
        cascade_config_digest=loaded_cascade.sha256_digest,
        pricing_table_digest=loaded_pricing.sha256_digest,
        langsmith_trace_url=_trace_url_for(trace_root or runs[0]),
        drift_alerts=[],
        budget_status=BudgetStatus(state="no-cap", over_by_usd=0.0),
    )
    drift_alerts = list(compute_per_agent_drift(report_stub, effective_history).values())
    resolved_budget = budget_usd
    if resolved_budget is None:
        raw_budget = (os.getenv("MARCUS_TRIAL_BUDGET_USD") or "").strip()
        if raw_budget:
            resolved_budget = float(raw_budget)
    budget_status = check_trial_budget(total_cost_usd, resolved_budget)
    return report_stub.model_copy(
        update={
            "drift_alerts": drift_alerts,
            "budget_status": budget_status,
        }
    )


def _render_cost_report_markdown(report: TrialEconomicsReport) -> str:
    lines = [
        f"# Trial Cost Report — {report.trial_id}",
        "",
        "## Total",
        "",
        f"- Measured at: {report.measured_at.isoformat()}",
        f"- Total cost USD: ${report.total_cost_usd:.6f}",
        f"- LangSmith trace: {report.langsmith_trace_url or 'unavailable'}",
        "",
        "## Per-Agent",
        "",
        "| Agent | Assigned Model | Calls | Input Tokens | Output Tokens | Cost USD |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for entry in report.per_agent_breakdown.values():
        lines.append(
            f"| {entry.agent_name} | {entry.model_assigned} | {entry.call_count} | "
            f"{entry.input_tokens} | {entry.output_tokens} | {entry.cost_usd:.6f} |"
        )
    lines.extend(
        [
            "",
            "## Per-Model",
            "",
            "| Model | Cost USD |",
            "| --- | ---: |",
        ]
    )
    for model_id, cost in report.per_model_breakdown.items():
        lines.append(f"| {model_id} | {cost:.6f} |")
    lines.extend(["", "## Drift Alerts", ""])
    if report.drift_alerts:
        lines.extend(
            [
                "| Agent | Rolling Median USD/Call | Observed USD/Call | Deviation % |",
                "| --- | ---: | ---: | ---: |",
            ]
        )
        for alert in report.drift_alerts:
            lines.append(
                f"| {alert.agent_name} | {alert.rolling_median_usd_per_call:.6f} | "
                f"{alert.observed_usd_per_call:.6f} | {alert.deviation_pct:.2f} |"
            )
    else:
        lines.append("No drift alerts.")
    lines.extend(
        [
            "",
            "## Budget Status",
            "",
            f"- State: {report.budget_status.state}",
            f"- Over by USD: ${report.budget_status.over_by_usd:.6f}",
            "",
            "## Digests",
            "",
            f"- Cascade config digest: `{report.cascade_config_digest}`",
            f"- Pricing table digest: `{report.pricing_table_digest}`",
        ]
    )
    return "\n".join(lines) + "\n"


def record_trial_cost_report(
    trial_id: str,
    report: TrialEconomicsReport,
    *,
    runs_root: Path = RUNS_ROOT,
) -> Path:
    """Persist machine-readable and operator-readable report forms."""

    run_dir = runs_root / trial_id
    run_dir.mkdir(parents=True, exist_ok=True)
    json_path = run_dir / "cost-report.json"
    markdown_path = run_dir / "cost-report.md"
    json_path.write_text(report.model_dump_json(indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(_render_cost_report_markdown(report), encoding="utf-8")
    return json_path


def summarize_cost_reports(
    *,
    runs_root: Path = RUNS_ROOT,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Aggregate on-disk cost reports for the health dashboard."""

    reports = _load_report_history(runs_root=runs_root)
    if not reports:
        return {
            "trials_with_cost_reports": 0,
            "median_trial_cost_last_5": None,
            "drift_alerts_last_24h": 0,
        }
    recent = reports[-5:]
    timestamp = now or datetime.now(UTC)
    cutoff = timestamp - timedelta(hours=24)
    alerts_last_24h = sum(
        len(report.drift_alerts)
        for report in reports
        if report.measured_at >= cutoff
    )
    return {
        "trials_with_cost_reports": len(reports),
        "median_trial_cost_last_5": _round_usd(
            float(median(report.total_cost_usd for report in recent))
        ),
        "drift_alerts_last_24h": alerts_last_24h,
    }


def load_trace_fixture(path: Path) -> Any:
    """Load a synthetic trace fixture into simple attribute-backed objects."""

    def build(payload: Any) -> Any:
        if isinstance(payload, dict):
            child_runs = payload.get("child_runs")
            if isinstance(child_runs, list):
                payload = {
                    **payload,
                    "child_runs": [build(child) for child in child_runs],
                }
            return SimpleNamespace(**payload)
        return payload

    raw = json.loads(path.read_text(encoding="utf-8"))
    return build(raw["root"])


__all__ = [
    "RUNS_ROOT",
    "check_trial_budget",
    "compute_per_agent_drift",
    "load_trace_fixture",
    "measure_trial_cost",
    "record_trial_cost_report",
    "summarize_cost_reports",
]
