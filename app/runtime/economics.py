"""Per-trial cost measurement + persistence for the migrated runtime."""

from __future__ import annotations

import hashlib
import json
import os
import stat
import tempfile
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path
from statistics import median
from types import SimpleNamespace
from typing import Any

from app.marcus.lesson_plan.pass1_call_journal import (
    Pass1CallJournalError,
    validate_pass1_call_journal,
)
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
PASS1_ATTEMPT_LEDGER_FILENAME = "irene-pass1-provider-attempts.v1.json"
COST_TRANSACTION_FILENAME = "cost-report-transaction.v1.json"
COST_LOCK_FILENAME = ".cost-report.lock"


def _round_usd(value: float) -> float:
    return round(value, 8)


def _canonical_digest(value: object) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _stable_json_object(path: Path) -> dict[str, Any]:
    """Read one regular JSON file through a stable, non-following handle."""
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        path_before = path.lstat()
        if not stat.S_ISREG(path_before.st_mode):
            raise RuntimeError("economics evidence is not a regular file")
        descriptor = os.open(path, flags)
        try:
            before = os.fstat(descriptor)
            if not stat.S_ISREG(before.st_mode) or (
                path_before.st_dev,
                path_before.st_ino,
            ) != (before.st_dev, before.st_ino):
                raise RuntimeError("economics evidence changed before read")
            with os.fdopen(descriptor, "rb", closefd=False) as stream:
                raw = stream.read()
            after = os.fstat(descriptor)
            path_after = path.lstat()
        finally:
            os.close(descriptor)
        stable_fields = ("st_dev", "st_ino", "st_size", "st_mtime_ns")
        if any(getattr(before, field) != getattr(after, field) for field in stable_fields) or any(
            getattr(after, field) != getattr(path_after, field) for field in stable_fields
        ):
            raise RuntimeError("economics evidence changed during read")
        payload = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise RuntimeError(f"economics evidence is unreadable: {path}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"economics evidence root is invalid: {path}")
    return payload


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


def _extract_provider_response_id(run: Any) -> str | None:
    """Find a provider/AI-message response identity in common trace output shapes."""
    queue: list[Any] = [_get_field(run, "outputs", {})]
    seen: set[int] = set()
    while queue:
        current = queue.pop(0)
        marker = id(current)
        if marker in seen:
            continue
        seen.add(marker)
        if isinstance(current, dict):
            for key in ("response_id", "provider_response_id"):
                value = current.get(key)
                if isinstance(value, str) and value.strip():
                    return value
            value = current.get("id")
            if isinstance(value, str) and value.startswith(("resp-", "chatcmpl-", "run-")):
                return value
            queue.extend(current.values())
        elif isinstance(current, (list, tuple)):
            queue.extend(current)
        elif hasattr(current, "model_dump"):
            queue.append(current.model_dump(mode="python"))
    return None


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
        if (path.parent / COST_TRANSACTION_FILENAME).exists():
            # A visible transaction means the artifact set is not committed yet.
            continue
        try:
            payload = _stable_json_object(path)
            if "cost_posture" not in payload or "unavailable_attempt_count" not in payload:
                continue
            report = TrialEconomicsReport.model_validate(payload)
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
        if report.unavailable_attempt_count and normalize_agent_name(agent_name) == "irene_pass1":
            continue
        if entry.call_count == 0:
            continue
        observed = entry.cost_usd / entry.call_count
        history_values: list[float] = []
        for prior in trailing:
            prior_entry = prior.per_agent_breakdown.get(agent_name)
            if (
                prior.unavailable_attempt_count
                and normalize_agent_name(agent_name) == "irene_pass1"
            ):
                continue
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
    trace_provider_attempts: list[dict[str, Any]] = []
    irene_execution_nodes: set[str] = set()

    for run in runs:
        raw_agent_name = _extract_agent_name(run) or "unknown"
        metadata = _extract_metadata(run)
        if metadata.get("economics_evidence") == "irene-pass1-journal-authority-marker.v1":
            node_id = metadata.get("node_id")
            if normalize_agent_name(raw_agent_name) != "irene_pass1" or not isinstance(
                node_id, str
            ) or not node_id:
                raise RuntimeError("Irene journal-authority marker identity is invalid")
            if node_id in irene_execution_nodes:
                raise RuntimeError("Irene journal-authority marker node is duplicated")
            irene_execution_nodes.add(node_id)
        if not _is_billable_llm_run(run):
            continue
        model_id = _extract_model_id(run)
        if model_id is None:
            raise RuntimeError("billable LangSmith run missing model identifier")
        if model_id.startswith("deterministic-"):
            # Audio-arc fix (2026-06-12): deterministic node markers
            # (deterministic-compositor-v0, deterministic-package-builder)
            # are NOT LLM spend — pricing has no row for them by design.
            # Cycle-5's full walk through §15 completed in memory and was
            # LOST when this loop KeyError'd on the compositor's marker at
            # the completion-path cost recording.
            continue
        input_tokens, output_tokens = _extract_usage(run)
        cost_usd = loaded_pricing.compute_cost(
            model_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
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
        trace_provider_attempts.append(
            {
                "trace_run_id": _run_id(run),
                "request_digest": metadata.get("irene_request_digest"),
                "response_id": _extract_provider_response_id(run),
                "agent_name": canonical_agent,
                "model_id": model_id,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost_usd": _round_usd(cost_usd),
            }
        )

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
        model_id: _round_usd(cost) for model_id, cost in sorted(per_model.items())
    }
    total_cost_usd = _round_usd(sum(item.cost_usd for item in per_agent_breakdown.values()))
    measured_at = datetime.now(UTC)
    effective_history = (
        history if history is not None else _load_report_history(exclude_trial_id=trial_id)
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
    report = report_stub.model_copy(
        update={
            "drift_alerts": drift_alerts,
            "budget_status": budget_status,
        }
    )
    object.__setattr__(report, "_trace_provider_attempts", tuple(trace_provider_attempts))
    object.__setattr__(report, "_irene_execution_nodes", tuple(sorted(irene_execution_nodes)))
    object.__setattr__(report, "_budget_usd", resolved_budget)
    object.__setattr__(report, "_economics_history", tuple(effective_history))
    return report


def _load_pass1_provider_attempts(
    *, trial_id: str, runs_root: Path, pricing: PricingTable
) -> list[dict[str, Any]]:
    """Read every Irene call journal into one truthful local-cost posture."""
    run_dir = runs_root / trial_id
    attempts: list[dict[str, Any]] = []
    for path in sorted(run_dir.glob("irene-pass1-call-*.v1.json")):
        try:
            journal = _stable_json_object(path)
        except RuntimeError as exc:
            raise RuntimeError(f"Irene provider-attempt journal unreadable: {path}") from exc
        try:
            validate_pass1_call_journal(journal, journal_path=path)
        except Pass1CallJournalError as exc:
            raise RuntimeError(f"Irene provider-attempt journal invalid: {path}") from exc
        identity_keys = {
            "schema_version",
            "processor_version",
            "run_id",
            "node_id",
            "model_id",
            "model_config_digest",
            "catalog_digest",
            "messages",
            "messages_digest",
        }
        identity_body = {key: journal.get(key) for key in identity_keys}
        request_digest = journal.get("request_digest")
        if (
            journal.get("schema_version") != "irene-pass1-call.v1"
            or journal.get("run_id") != trial_id
            or request_digest != _canonical_digest(identity_body)
            or journal.get("messages_digest") != _canonical_digest(journal.get("messages"))
            or path.name != f"irene-pass1-call-{journal.get('node_id')}.v1.json"
        ):
            raise RuntimeError(f"Irene provider-attempt identity invalid: {path}")
        state = journal.get("state")
        if state not in {
            "call_in_progress",
            "response_received",
            "candidate_decoded",
            "completed",
        }:
            raise RuntimeError(f"Irene provider-attempt state invalid: {path}")
        model_id = journal.get("model_id")
        if not isinstance(model_id, str) or not model_id:
            raise RuntimeError(f"Irene provider-attempt model invalid: {path}")
        input_tokens: int | None = None
        output_tokens: int | None = None
        cost_usd: float | None = None
        unavailable_reason: str | None = None
        response_id: str | None = None
        if state == "call_in_progress":
            unavailable_reason = "provider_outcome_ambiguous"
        else:
            raw_response = journal.get("raw_response")
            evidence = journal.get("provider_evidence")
            if (
                not isinstance(raw_response, str)
                or journal.get("raw_response_digest") != _canonical_digest(raw_response)
                or not isinstance(evidence, dict)
                or journal.get("provider_evidence_digest") != _canonical_digest(evidence)
            ):
                raise RuntimeError(f"Irene provider-attempt response evidence invalid: {path}")
            usage = evidence.get("usage_metadata")
            raw_response_id = evidence.get("response_id")
            response_id = raw_response_id if isinstance(raw_response_id, str) else None
            if not isinstance(usage, dict):
                unavailable_reason = "provider_usage_metadata_unavailable"
            else:
                raw_input = usage.get("input_tokens", usage.get("prompt_tokens"))
                raw_output = usage.get("output_tokens", usage.get("completion_tokens"))
                if (
                    not isinstance(raw_input, int)
                    or isinstance(raw_input, bool)
                    or raw_input < 0
                    or not isinstance(raw_output, int)
                    or isinstance(raw_output, bool)
                    or raw_output < 0
                ):
                    unavailable_reason = "provider_usage_metadata_incomplete"
                elif raw_input + raw_output == 0:
                    unavailable_reason = "provider_usage_zero_untrusted"
                else:
                    input_tokens = raw_input
                    output_tokens = raw_output
                    try:
                        cost_usd = _round_usd(
                            pricing.compute_cost(
                                model_id,
                                input_tokens=input_tokens,
                                output_tokens=output_tokens,
                            )
                        )
                    except (KeyError, ValueError):
                        unavailable_reason = f"pricing_unavailable_for_{model_id}"
        attempts.append(
            {
                "attempt_id": request_digest,
                "journal_filename": path.name,
                "journal_state": state,
                "node_id": journal.get("node_id"),
                "model_id": model_id,
                "response_id": response_id,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost_usd": cost_usd,
                "cost_status": "known" if cost_usd is not None else "unavailable",
                "cost_unavailable_reason": unavailable_reason,
            }
        )
    return attempts


def _reconcile_pass1_provider_attempts(
    report: TrialEconomicsReport,
    *,
    trial_id: str,
    runs_root: Path,
) -> tuple[TrialEconomicsReport, dict[str, Any] | None]:
    trace_attempts = [
        dict(item)
        for item in getattr(report, "_trace_provider_attempts", ())
        if isinstance(item, dict) and item.get("agent_name") == "irene_pass1"
    ]
    if not any((runs_root / trial_id).glob("irene-pass1-call-*.v1.json")):
        has_irene_aggregate = any(
            normalize_agent_name(name) == "irene_pass1"
            for name in report.per_agent_breakdown
        )
        if (
            trace_attempts
            or has_irene_aggregate
            or getattr(report, "_irene_execution_nodes", ())
        ):
            raise RuntimeError("Irene trace contains provider attempts without durable journals")
        return report, None
    pricing = load_pricing()
    if pricing.sha256_digest != report.pricing_table_digest:
        raise RuntimeError("Irene journal pricing identity does not match the economics report")
    attempts = _load_pass1_provider_attempts(
        trial_id=trial_id,
        runs_root=runs_root,
        pricing=pricing,
    )
    if not attempts:
        return report, None
    observed_nodes = set(getattr(report, "_irene_execution_nodes", ()))
    journal_nodes = {str(attempt.get("node_id")) for attempt in attempts}
    missing_journal_nodes = observed_nodes - journal_nodes
    if missing_journal_nodes:
        raise RuntimeError(
            "Irene execution markers lack durable journals for nodes: "
            + ", ".join(sorted(missing_journal_nodes))
        )
    known = [attempt for attempt in attempts if attempt["cost_status"] == "known"]
    def _unique_trace_match(field: str, value: object) -> tuple[int, dict[str, Any]] | None:
        if not isinstance(value, str) or not value:
            return None
        matches = [
            (index, item)
            for index, item in enumerate(trace_attempts)
            if item.get(field) == value
        ]
        if len(matches) > 1:
            raise RuntimeError(f"Irene trace carries duplicate {field} correlation")
        return matches[0] if matches else None

    unmatched: list[dict[str, Any]] = []
    consumed_trace_indexes: set[int] = set()
    for attempt in attempts:
        matched = _unique_trace_match("request_digest", attempt["attempt_id"])
        correlation = "request_digest"
        if matched is None:
            matched = _unique_trace_match("response_id", attempt.get("response_id"))
            correlation = "response_id"
        if matched is None:
            attempt["trace_correlation"] = "unmatched"
            unmatched.append(attempt)
            continue
        match_index, match = matched
        if match_index in consumed_trace_indexes:
            raise RuntimeError("one Irene trace attempt cannot satisfy multiple journals")
        consumed_trace_indexes.add(match_index)
        trace_request = match.get("request_digest")
        trace_response = match.get("response_id")
        if (
            isinstance(trace_request, str)
            and trace_request
            and trace_request != attempt["attempt_id"]
        ) or (
            isinstance(trace_response, str)
            and trace_response
            and isinstance(attempt.get("response_id"), str)
            and trace_response != attempt["response_id"]
        ):
            raise RuntimeError("Irene journal/trace correlation identifiers conflict")
        if match.get("model_id") != attempt["model_id"] or (
            attempt["cost_status"] == "known"
            and (
                match.get("input_tokens") != attempt["input_tokens"]
                or match.get("output_tokens") != attempt["output_tokens"]
                or match.get("cost_usd") != attempt["cost_usd"]
            )
        ):
            raise RuntimeError("Irene journal/trace correlation disagrees on billable identity")
        attempt["trace_correlation"] = correlation
        attempt["trace_run_id"] = match.get("trace_run_id")
        attempt["trace_cost_usd"] = match.get("cost_usd")

    leftover_trace_indexes = set(range(len(trace_attempts))) - consumed_trace_indexes
    if leftover_trace_indexes:
        raise RuntimeError("Irene trace contains provider attempts without durable journals")

    per_agent = dict(report.per_agent_breakdown)
    existing_keys = [key for key in per_agent if normalize_agent_name(key) == "irene_pass1"]
    existing = per_agent[existing_keys[0]] if existing_keys else None
    if existing is not None and not trace_attempts:
        raise RuntimeError("Irene trace aggregate exists without per-attempt correlation evidence")
    if trace_attempts and existing is None:
        raise RuntimeError("Irene per-attempt traces exist without an aggregate cost bucket")
    per_model = dict(report.per_model_breakdown)
    if unmatched:
        for key in existing_keys:
            per_agent.pop(key, None)
        added_known = [attempt for attempt in unmatched if attempt["cost_status"] == "known"]
        model_ids = {str(attempt["model_id"]) for attempt in unmatched}
        if existing is not None:
            model_ids.add(existing.model_assigned)
        per_agent["irene_pass1"] = AgentCostEntry(
            agent_name="irene_pass1",
            model_assigned=next(iter(model_ids)) if len(model_ids) == 1 else "mixed",
            call_count=(existing.call_count if existing else 0) + len(unmatched),
            input_tokens=(existing.input_tokens if existing else 0)
            + sum(int(attempt["input_tokens"] or 0) for attempt in added_known),
            output_tokens=(existing.output_tokens if existing else 0)
            + sum(int(attempt["output_tokens"] or 0) for attempt in added_known),
            cost_usd=_round_usd(
                (existing.cost_usd if existing else 0.0)
                + sum(float(attempt["cost_usd"] or 0.0) for attempt in added_known)
            ),
        )
        for attempt in added_known:
            model_id = str(attempt["model_id"])
            per_model[model_id] = _round_usd(
                per_model.get(model_id, 0.0) + float(attempt["cost_usd"])
            )
    total_cost = _round_usd(sum(entry.cost_usd for entry in per_agent.values()))
    budget_usd = getattr(report, "_budget_usd", None)
    if budget_usd is None and report.budget_status.state == "over-budget-warning":
        budget_usd = _round_usd(report.total_cost_usd - report.budget_status.over_by_usd)
    if budget_usd is None and report.budget_status.state == "under-budget":
        raise RuntimeError("trial budget identity is unavailable for Irene reconciliation")
    preliminary = report.model_copy(
        update={
            "per_agent_breakdown": dict(sorted(per_agent.items())),
            "per_model_breakdown": dict(sorted(per_model.items())),
            "total_cost_usd": total_cost,
            "budget_status": (
                BudgetStatus(state="unknown-cost", over_by_usd=0.0)
                if any(attempt["cost_status"] == "unavailable" for attempt in attempts)
                and budget_usd is not None
                and total_cost <= budget_usd
                else check_trial_budget(total_cost, budget_usd)
            ),
            "drift_alerts": [],
            "unavailable_attempt_count": sum(
                attempt["cost_status"] == "unavailable" for attempt in attempts
            ),
            "cost_posture": (
                "exact"
                if all(attempt["cost_status"] == "known" for attempt in attempts)
                else "known-lower-bound-with-explicit-unavailable-attempts"
            ),
        }
    )
    history = list(
        getattr(
            report,
            "_economics_history",
            _load_report_history(runs_root=runs_root, exclude_trial_id=trial_id),
        )
    )
    reconciled = preliminary.model_copy(
        update={"drift_alerts": list(compute_per_agent_drift(preliminary, history).values())}
    )
    reconciliation_status = (
        "all_correlated"
        if not unmatched
        else "journal_added"
        if len(unmatched) == len(attempts)
        else "partially_correlated"
    )
    body: dict[str, Any] = {
        "schema_version": "irene-pass1-provider-attempts.v1",
        "trial_id": trial_id,
        "attempts": attempts,
        "known_cost_usd": _round_usd(sum(float(attempt["cost_usd"] or 0.0) for attempt in known)),
        "pricing_table_digest": pricing.sha256_digest,
        "added_cost_usd": _round_usd(
            sum(
                float(attempt["cost_usd"] or 0.0)
                for attempt in unmatched
                if attempt["cost_status"] == "known"
            )
        ),
        "unavailable_attempt_count": sum(
            attempt["cost_status"] == "unavailable" for attempt in attempts
        ),
        "trace_reconciliation_status": reconciliation_status,
        "all_attempts_accounted": True,
        "cost_posture": (
            "exact"
            if all(attempt["cost_status"] == "known" for attempt in attempts)
            else "known-lower-bound-with-explicit-unavailable-attempts"
        ),
    }
    return reconciled, {**body, "artifact_digest": _canonical_digest(body)}


def _render_cost_report_markdown(
    report: TrialEconomicsReport,
    *,
    pass1_attempt_ledger: dict[str, Any] | None = None,
) -> str:
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
    if pass1_attempt_ledger is not None:
        lines.extend(
            [
                "",
                "## Irene Provider Attempts",
                "",
                "| Attempt | State | Model | Input | Output | Cost USD | Posture |",
                "| --- | --- | --- | ---: | ---: | ---: | --- |",
            ]
        )
        for attempt in pass1_attempt_ledger["attempts"]:
            input_value = (
                attempt["input_tokens"] if attempt["input_tokens"] is not None else "unavailable"
            )
            output_value = (
                attempt["output_tokens"] if attempt["output_tokens"] is not None else "unavailable"
            )
            cost_value = attempt["cost_usd"] if attempt["cost_usd"] is not None else "unavailable"
            lines.append(
                f"| {attempt['attempt_id']} | {attempt['journal_state']} | "
                f"{attempt['model_id']} | {input_value} | {output_value} | "
                f"{cost_value} | "
                f"{attempt['cost_status']}: {attempt['cost_unavailable_reason'] or 'priced'} |"
            )
        unavailable = int(pass1_attempt_ledger["unavailable_attempt_count"])
        if unavailable:
            suffix = "attempt" if unavailable == 1 else "attempts"
            lines.extend(
                [
                    "",
                    f"Total cost excludes {unavailable} unavailable Irene {suffix}; "
                    "see the explicit posture above.",
                ]
            )
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


def _atomic_write_bytes(path: Path, content: bytes) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        _fsync_directory(path.parent)
    finally:
        temporary.unlink(missing_ok=True)


def _fsync_directory(path: Path) -> None:
    """Make directory-entry changes durable where the platform supports it."""
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError:
        return
    try:
        os.fsync(descriptor)
    except OSError:
        # Windows does not expose portable directory fsync semantics.
        pass
    finally:
        os.close(descriptor)


@contextmanager
def _exclusive_cost_report_lock(run_dir: Path) -> Iterator[None]:
    lock = run_dir / COST_LOCK_FILENAME
    if lock.exists() or lock.is_symlink():
        before = lock.lstat()
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise RuntimeError("cost-report persistence lock coordinate is unsafe")
    flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(lock, flags, 0o600)
    opened = os.fstat(descriptor)
    after = lock.lstat()
    if (
        not stat.S_ISREG(opened.st_mode)
        or opened.st_nlink != 1
        or (opened.st_dev, opened.st_ino) != (after.st_dev, after.st_ino)
    ):
        os.close(descriptor)
        raise RuntimeError("cost-report persistence lock coordinate is unsafe")
    stream = os.fdopen(descriptor, "r+b")
    acquired = False
    try:
        if os.name == "nt":
            import msvcrt

            stream.seek(0)
            if stream.read(1) == b"":
                stream.write(b"0")
                stream.flush()
            stream.seek(0)
            try:
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError as exc:
                raise RuntimeError("cost-report persistence lock is held") from exc
        else:
            import fcntl

            try:
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                raise RuntimeError("cost-report persistence lock is held") from exc
        acquired = True
        yield
    finally:
        try:
            if acquired and os.name == "nt":
                import msvcrt

                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            elif acquired:
                import fcntl

                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
        finally:
            stream.close()


def _recover_cost_artifact_transaction(run_dir: Path) -> None:
    transaction_path = run_dir / COST_TRANSACTION_FILENAME
    if not transaction_path.exists() and not transaction_path.is_symlink():
        return
    transaction = _stable_json_object(transaction_path)
    artifacts = transaction.get("artifacts")
    delete_artifacts = transaction.get("delete_artifacts", [])
    if transaction.get("schema_version") != "cost-report-transaction.v1" or not isinstance(
        artifacts, dict
    ):
        raise RuntimeError("cost-report transaction is invalid")
    if not isinstance(delete_artifacts, list) or any(
        filename != PASS1_ATTEMPT_LEDGER_FILENAME for filename in delete_artifacts
    ):
        raise RuntimeError("cost-report transaction deletion set is invalid")
    if set(artifacts).intersection(delete_artifacts):
        raise RuntimeError("cost-report transaction writes and deletes the same artifact")
    expected = {"cost-report.json", "cost-report.md"}
    if PASS1_ATTEMPT_LEDGER_FILENAME in artifacts:
        expected.add(PASS1_ATTEMPT_LEDGER_FILENAME)
    if set(artifacts) != expected:
        raise RuntimeError("cost-report transaction artifact set is incomplete")
    for filename, row in artifacts.items():
        if filename not in {
            "cost-report.json",
            "cost-report.md",
            PASS1_ATTEMPT_LEDGER_FILENAME,
        } or not isinstance(row, dict):
            raise RuntimeError("cost-report transaction artifact is invalid")
        content = row.get("content")
        if (
            not isinstance(content, str)
            or row.get("sha256") != hashlib.sha256(content.encode("utf-8")).hexdigest()
        ):
            raise RuntimeError("cost-report transaction digest is invalid")
        _atomic_write_bytes(run_dir / filename, content.encode("utf-8"))
    for filename in delete_artifacts:
        (run_dir / filename).unlink(missing_ok=True)
        _fsync_directory(run_dir)
    transaction_path.unlink()
    _fsync_directory(run_dir)


def _persist_cost_artifact_set(
    *,
    run_dir: Path,
    report_json: str,
    report_markdown: str,
    pass1_attempt_ledger: dict[str, Any] | None,
) -> None:
    artifacts: dict[str, str] = {
        "cost-report.json": report_json,
        "cost-report.md": report_markdown,
    }
    if pass1_attempt_ledger is not None:
        artifacts[PASS1_ATTEMPT_LEDGER_FILENAME] = (
            json.dumps(
                pass1_attempt_ledger,
                indent=2,
                sort_keys=True,
                ensure_ascii=True,
                allow_nan=False,
            )
            + "\n"
        )
    transaction = {
        "schema_version": "cost-report-transaction.v1",
        "artifacts": {
            filename: {
                "content": content,
                "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
            }
            for filename, content in artifacts.items()
        },
        "delete_artifacts": (
            [] if pass1_attempt_ledger is not None else [PASS1_ATTEMPT_LEDGER_FILENAME]
        ),
    }
    _atomic_write_bytes(
        run_dir / COST_TRANSACTION_FILENAME,
        (json.dumps(transaction, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8"),
    )
    for filename in (
        PASS1_ATTEMPT_LEDGER_FILENAME,
        "cost-report.md",
        "cost-report.json",
    ):
        content = artifacts.get(filename)
        if content is not None:
            _atomic_write_bytes(run_dir / filename, content.encode("utf-8"))
    if pass1_attempt_ledger is None:
        (run_dir / PASS1_ATTEMPT_LEDGER_FILENAME).unlink(missing_ok=True)
        _fsync_directory(run_dir)
    (run_dir / COST_TRANSACTION_FILENAME).unlink()
    _fsync_directory(run_dir)


def record_trial_cost_report(
    trial_id: str,
    report: TrialEconomicsReport,
    *,
    runs_root: Path = RUNS_ROOT,
) -> Path:
    """Persist machine-readable and operator-readable report forms."""

    run_dir = runs_root / trial_id
    run_dir.mkdir(parents=True, exist_ok=True)
    with _exclusive_cost_report_lock(run_dir):
        _recover_cost_artifact_transaction(run_dir)
        report, pass1_attempt_ledger = _reconcile_pass1_provider_attempts(
            report,
            trial_id=trial_id,
            runs_root=runs_root,
        )
        json_path = run_dir / "cost-report.json"
        _persist_cost_artifact_set(
            run_dir=run_dir,
            report_json=report.model_dump_json(indent=2) + "\n",
            report_markdown=_render_cost_report_markdown(
                report,
                pass1_attempt_ledger=pass1_attempt_ledger,
            ),
            pass1_attempt_ledger=pass1_attempt_ledger,
        )
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
    exact_reports = [report for report in reports if report.cost_posture == "exact"]
    recent = exact_reports[-5:]
    timestamp = now or datetime.now(UTC)
    cutoff = timestamp - timedelta(hours=24)
    alerts_last_24h = sum(
        len(report.drift_alerts) for report in reports if report.measured_at >= cutoff
    )
    return {
        "trials_with_cost_reports": len(reports),
        "median_trial_cost_last_5": (
            _round_usd(float(median(report.total_cost_usd for report in recent)))
            if recent
            else None
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
