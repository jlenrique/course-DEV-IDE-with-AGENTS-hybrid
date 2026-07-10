"""Hermetic Batch cost/latency report (B4).

Aggregates usage from joined Batch output rows + receipt timestamps.
Does **not** call LiteLLM Enterprise billing APIs.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from app.runtime.cascade_config import PricingTable, load_pricing
from app.runtime.llm_batch.join import JoinedBatchRow, JoinResult
from app.runtime.llm_batch.receipts import BatchReceipt

COST_REPORT_FILENAME = "cost-report.json"


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _usage_from_row(row: JoinedBatchRow) -> dict[str, int] | None:
    if not row.ok or not isinstance(row.raw, dict):
        return None
    response = row.raw.get("response")
    if not isinstance(response, dict):
        return None
    body = response.get("body")
    if not isinstance(body, dict):
        return None
    usage = body.get("usage")
    if not isinstance(usage, dict):
        return None
    prompt = usage.get("prompt_tokens", usage.get("input_tokens"))
    completion = usage.get("completion_tokens", usage.get("output_tokens"))
    total = usage.get("total_tokens")
    try:
        prompt_i = int(prompt) if prompt is not None else 0
        completion_i = int(completion) if completion is not None else 0
        total_i = prompt_i + completion_i if total is None else int(total)
    except (TypeError, ValueError):
        return None
    if prompt_i == 0 and completion_i == 0 and total_i == 0:
        return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    return {
        "prompt_tokens": prompt_i,
        "completion_tokens": completion_i,
        "total_tokens": total_i,
    }


def build_batch_cost_report(
    *,
    receipt: BatchReceipt,
    joined: JoinResult,
    pricing: PricingTable | None = None,
    realtime: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a deterministic cost/latency report dict (hermetic)."""

    notes: list[str] = []
    prompt_tokens = 0
    completion_tokens = 0
    total_tokens = 0
    usage_rows = 0
    missing_usage_rows = 0
    for custom_id in joined.order_seen:
        row = joined.by_custom_id[custom_id]
        if not row.ok:
            continue
        usage = _usage_from_row(row)
        if usage is None:
            missing_usage_rows += 1
            notes.append(f"missing usage for custom_id={custom_id}")
            continue
        usage_rows += 1
        prompt_tokens += usage["prompt_tokens"]
        completion_tokens += usage["completion_tokens"]
        total_tokens += usage["total_tokens"]

    if not joined.order_seen:
        notes.append("no output rows")

    estimated_cost_usd: float | None = None
    pricing_reason: str | None = None
    table = pricing if pricing is not None else None
    if table is None:
        try:
            table = load_pricing()
        except Exception as exc:  # noqa: BLE001 — fail-soft report
            pricing_reason = f"pricing_load_failed:{exc}"
            table = None
    model = receipt.model
    if table is not None and model:
        try:
            estimated_cost_usd = float(
                table.compute_cost(
                    model,
                    input_tokens=prompt_tokens,
                    output_tokens=completion_tokens,
                )
            )
            pricing_reason = None
        except Exception as exc:  # noqa: BLE001
            estimated_cost_usd = None
            pricing_reason = f"pricing_unavailable:{exc}"
    elif not model:
        pricing_reason = "receipt.model missing"
    elif pricing_reason is None:
        pricing_reason = "pricing table unavailable"

    submitted = _parse_iso(receipt.submitted_at)
    completed = _parse_iso(receipt.completed_at)
    latency_s: float | None = None
    latency_reason: str | None = None
    if submitted is not None and completed is not None:
        latency_s = max((completed - submitted).total_seconds(), 0.0)
    else:
        latency_reason = "submitted_at and/or completed_at missing or unparsable"

    realtime_section = realtime if realtime is not None else {
        "available": False,
        "reason": "no realtime usage supplied to B4 report",
        "prompt_tokens": None,
        "completion_tokens": None,
        "total_tokens": None,
        "estimated_cost_usd": None,
    }

    return {
        "schema_version": "llm-batch-cost-report.v1",
        "trial_id": receipt.run_id,
        "batch_id": receipt.batch_id,
        "model": model,
        "row_count": receipt.row_count,
        "rows_seen": len(joined.order_seen),
        "rows_ok": len(joined.ok_ids),
        "rows_failed": len(joined.failed_ids),
        "rows_with_usage": usage_rows,
        "rows_missing_usage": missing_usage_rows,
        "batch": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "estimated_cost_usd": estimated_cost_usd,
            "pricing_reason": pricing_reason,
            "latency_seconds": latency_s,
            "latency_reason": latency_reason,
            "submitted_at": receipt.submitted_at,
            "completed_at": receipt.completed_at,
        },
        "realtime": realtime_section,
        "notes": notes,
    }


def write_batch_cost_report(
    runs_root: Path,
    report: dict[str, Any],
) -> Path:
    """Write ``runs/<trial_id>/llm_batch/cost-report.json``."""

    trial_id = str(report["trial_id"])
    out_dir = runs_root / trial_id / "llm_batch"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / COST_REPORT_FILENAME
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def emit_batch_cost_report_fail_soft(
    *,
    runs_root: Path,
    receipt: BatchReceipt,
    joined: JoinResult,
) -> Path | None:
    """Build+write report; swallow errors so perception/resume never blocks."""

    try:
        report = build_batch_cost_report(receipt=receipt, joined=joined)
        return write_batch_cost_report(runs_root, report)
    except Exception:  # noqa: BLE001
        return None


__all__ = [
    "COST_REPORT_FILENAME",
    "build_batch_cost_report",
    "emit_batch_cost_report_fail_soft",
    "write_batch_cost_report",
]
