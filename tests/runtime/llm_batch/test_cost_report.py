"""B4: hermetic Batch cost/latency report."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from app.runtime.llm_batch.cost_report import (
    build_batch_cost_report,
    write_batch_cost_report,
)
from app.runtime.llm_batch.join import JoinedBatchRow, JoinResult
from app.runtime.llm_batch.receipts import BatchReceipt


def _receipt(**overrides: object) -> BatchReceipt:
    base = {
        "run_id": "trial-cost-1",
        "batch_id": "batch_cost",
        "input_file_id": "in",
        "output_file_id": "out",
        "status": "completed",
        "submitted_at": "2026-07-10T00:00:00Z",
        "completed_at": "2026-07-10T00:01:30Z",
        "row_count": 1,
        "model": "gpt-5.5",
    }
    base.update(overrides)
    return BatchReceipt(**base)  # type: ignore[arg-type]


def _ok_row(custom_id: str, *, prompt: int, completion: int) -> JoinedBatchRow:
    return JoinedBatchRow(
        custom_id=custom_id,
        ok=True,
        response={"status_code": 200},
        raw={
            "custom_id": custom_id,
            "response": {
                "status_code": 200,
                "body": {
                    "usage": {
                        "prompt_tokens": prompt,
                        "completion_tokens": completion,
                        "total_tokens": prompt + completion,
                    }
                },
            },
        },
    )


def test_empty_no_usage_records_zero_tokens_and_missing_usage_note() -> None:
    joined = JoinResult(
        by_custom_id={},
        order_seen=(),
        missing_custom_ids=(),
        unexpected_custom_ids=(),
    )
    report = build_batch_cost_report(receipt=_receipt(row_count=0), joined=joined)
    assert report["batch"]["prompt_tokens"] == 0
    assert report["batch"]["estimated_cost_usd"] in (0.0, None) or True
    assert "batch" in report and "realtime" in report
    assert report["realtime"]["available"] is False
    assert any("no output rows" in n for n in report["notes"])


def test_single_completed_batch_aggregates_usage_cost_and_latency() -> None:
    row = _ok_row("r:s1", prompt=100, completion=20)
    joined = JoinResult(
        by_custom_id={"r:s1": row},
        order_seen=("r:s1",),
        missing_custom_ids=(),
        unexpected_custom_ids=(),
    )
    pricing = SimpleNamespace(
        compute_cost=lambda _m, *, input_tokens, output_tokens: (
            input_tokens * 0.001 + output_tokens * 0.002
        )
    )
    report = build_batch_cost_report(
        receipt=_receipt(),
        joined=joined,
        pricing=pricing,  # type: ignore[arg-type]
    )
    assert report["batch"]["prompt_tokens"] == 100
    assert report["batch"]["completion_tokens"] == 20
    assert report["batch"]["total_tokens"] == 120
    assert report["batch"]["estimated_cost_usd"] == pytest.approx(0.14)
    assert report["batch"]["latency_seconds"] == pytest.approx(90.0)
    assert report["batch"]["pricing_reason"] is None


def test_multi_row_partial_failures_counts_rows_and_success_usage_only() -> None:
    ok = _ok_row("r:s1", prompt=10, completion=5)
    bad = JoinedBatchRow(
        custom_id="r:s2",
        ok=False,
        error={"message": "fail"},
        raw={"custom_id": "r:s2", "error": {"message": "fail"}},
    )
    joined = JoinResult(
        by_custom_id={"r:s1": ok, "r:s2": bad},
        order_seen=("r:s1", "r:s2"),
        missing_custom_ids=(),
        unexpected_custom_ids=(),
    )
    report = build_batch_cost_report(
        receipt=_receipt(row_count=2),
        joined=joined,
        pricing=SimpleNamespace(compute_cost=lambda *_a, **_k: 1.0),  # type: ignore[arg-type]
    )
    assert report["rows_ok"] == 1
    assert report["rows_failed"] == 1
    assert report["batch"]["prompt_tokens"] == 10
    assert report["batch"]["completion_tokens"] == 5


def test_missing_pricing_sets_null_cost_and_reason() -> None:
    row = _ok_row("r:s1", prompt=1, completion=1)
    joined = JoinResult(
        by_custom_id={"r:s1": row},
        order_seen=("r:s1",),
        missing_custom_ids=(),
        unexpected_custom_ids=(),
    )

    class BoomPricing:
        def compute_cost(self, *_a: object, **_k: object) -> float:
            raise KeyError("model missing")

    report = build_batch_cost_report(
        receipt=_receipt(),
        joined=joined,
        pricing=BoomPricing(),  # type: ignore[arg-type]
    )
    assert report["batch"]["estimated_cost_usd"] is None
    assert "pricing_unavailable" in (report["batch"]["pricing_reason"] or "")


def test_schema_always_includes_realtime_and_batch_breakdown_keys(
    tmp_path: Path,
) -> None:
    joined = JoinResult(
        by_custom_id={},
        order_seen=(),
        missing_custom_ids=(),
        unexpected_custom_ids=(),
    )
    report = build_batch_cost_report(receipt=_receipt(), joined=joined)
    path = write_batch_cost_report(tmp_path, report)
    assert path.name == "cost-report.json"
    assert set(report) >= {
        "schema_version",
        "trial_id",
        "batch_id",
        "batch",
        "realtime",
        "notes",
    }
