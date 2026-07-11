"""T0: join Batch output rows by custom_id (out-of-order + failed isolation)."""

from __future__ import annotations

import pytest

from app.runtime.llm_batch.errors import LlmBatchError
from app.runtime.llm_batch.join import join_output_rows, parse_output_jsonl


def test_join_out_of_order_by_custom_id() -> None:
    rows = [
        {
            "custom_id": "run:slide-02",
            "response": {"status_code": 200, "body": {"choices": [{"message": {"content": "b"}}]}},
        },
        {
            "custom_id": "run:slide-01",
            "response": {"status_code": 200, "body": {"choices": [{"message": {"content": "a"}}]}},
        },
    ]
    result = join_output_rows(
        rows,
        expected_custom_ids=["run:slide-01", "run:slide-02"],
    )
    assert result.order_seen == ("run:slide-02", "run:slide-01")
    assert set(result.ok_ids) == {"run:slide-01", "run:slide-02"}
    assert result.by_custom_id["run:slide-01"].ok is True
    assert result.missing_custom_ids == ()
    assert result.unexpected_custom_ids == ()


def test_join_isolates_failed_row() -> None:
    rows = [
        {
            "custom_id": "run:ok",
            "response": {"status_code": 200, "body": {}},
        },
        {
            "custom_id": "run:bad",
            "error": {"code": "invalid_request", "message": "boom"},
        },
    ]
    result = join_output_rows(rows, expected_custom_ids=["run:ok", "run:bad"])
    assert result.ok_ids == ("run:ok",)
    assert result.failed_ids == ("run:bad",)
    assert result.by_custom_id["run:bad"].error is not None


def test_join_rejects_duplicate_custom_id() -> None:
    rows = [
        {"custom_id": "dup", "response": {"status_code": 200, "body": {}}},
        {"custom_id": "dup", "error": {"message": "second"}},
    ]
    with pytest.raises(LlmBatchError) as exc_info:
        join_output_rows(rows)
    assert exc_info.value.tag == "llm_batch.join.duplicate-custom-id"


def test_join_non_numeric_status_code_marks_failed() -> None:
    rows = [
        {"custom_id": "run:weird", "response": {"status_code": "nope", "body": {}}},
    ]
    result = join_output_rows(rows, expected_custom_ids=["run:weird"])
    assert result.failed_ids == ("run:weird",)


def test_join_reports_missing_expected_ids() -> None:
    rows = [
        {
            "custom_id": "run:only",
            "response": {"status_code": 200, "body": {}},
        }
    ]
    result = join_output_rows(rows, expected_custom_ids=["run:only", "run:missing"])
    assert result.missing_custom_ids == ("run:missing",)


def test_parse_output_jsonl_roundtrip() -> None:
    text = (
        '{"custom_id":"a","response":{"status_code":200}}\n'
        '{"custom_id":"b","error":{"message":"x"}}\n'
    )
    rows = parse_output_jsonl(text)
    joined = join_output_rows(rows, expected_custom_ids=["a", "b"])
    assert joined.ok_ids == ("a",)
    assert joined.failed_ids == ("b",)
