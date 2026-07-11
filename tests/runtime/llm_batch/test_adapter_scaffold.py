"""T0: JSONL size budget + mocked LiteLLM submit→receipt→join."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from app.runtime.llm_batch.adapter import LiteLlmBatchAdapter
from app.runtime.llm_batch.errors import LlmBatchError
from app.runtime.llm_batch.jsonl import (
    assert_within_size_budget,
    encode_batch_jsonl,
    estimate_jsonl_bytes,
    make_chat_completions_row,
)
from app.runtime.llm_batch.receipts import read_receipt


def test_size_budget_fail_loud() -> None:
    rows = [
        make_chat_completions_row(
            custom_id="r:1",
            model="gpt-5.5",
            messages=[{"role": "user", "content": "x" * 100}],
            max_completion_tokens=100,
        )
    ]
    size = estimate_jsonl_bytes(rows)
    with pytest.raises(LlmBatchError) as exc_info:
        assert_within_size_budget(rows, max_bytes=size - 1)
    assert exc_info.value.tag == "llm_batch.jsonl.oversize"


def test_encode_batch_jsonl_within_budget() -> None:
    rows = [
        make_chat_completions_row(
            custom_id="run:slide-01",
            model="gpt-5.5",
            messages=[
                {"role": "system", "content": "sys"},
                {"role": "user", "content": "hi"},
            ],
            max_completion_tokens=8192,
        )
    ]
    payload = encode_batch_jsonl(rows, max_bytes=10_000)
    assert b"run:slide-01" in payload
    assert b"/v1/chat/completions" in payload
    assert payload.endswith(b"\n")


def test_submit_and_receipt_with_mocked_litellm(tmp_path: Path) -> None:
    uploaded: dict[str, object] = {}

    def fake_create_file(**kwargs: object) -> SimpleNamespace:
        uploaded["purpose"] = kwargs.get("purpose")
        uploaded["provider"] = kwargs.get("custom_llm_provider")
        return SimpleNamespace(id="file_input_1")

    def fake_create_batch(**kwargs: object) -> SimpleNamespace:
        uploaded["endpoint"] = kwargs.get("endpoint")
        uploaded["input_file_id"] = kwargs.get("input_file_id")
        return SimpleNamespace(
            id="batch_abc",
            status="validating",
            endpoint=kwargs.get("endpoint"),
            input_file_id=kwargs.get("input_file_id"),
            output_file_id=None,
            error_file_id=None,
            completion_window="24h",
            request_counts={"total": 2, "completed": 0, "failed": 0},
            model=None,
            completed_at=None,
        )

    adapter = LiteLlmBatchAdapter(
        create_file_fn=fake_create_file,
        create_batch_fn=fake_create_batch,
        retrieve_batch_fn=lambda **_k: None,
        file_content_fn=lambda **_k: b"",
        cancel_batch_fn=lambda **_k: None,
    )
    rows = [
        make_chat_completions_row(
            custom_id="run:s1",
            model="gpt-5.5",
            messages=[{"role": "user", "content": "a"}],
            max_completion_tokens=100,
        ),
        make_chat_completions_row(
            custom_id="run:s2",
            model="gpt-5.5",
            messages=[{"role": "user", "content": "b"}],
            max_completion_tokens=100,
        ),
    ]
    receipt = adapter.submit_and_receipt(
        rows,
        run_id="trial-uuid-1",
        runs_root=tmp_path,
        model="gpt-5.5",
        metadata={"node": "vision"},
    )
    assert uploaded["purpose"] == "batch"
    assert uploaded["provider"] == "openai"
    assert uploaded["endpoint"] == "/v1/chat/completions"
    assert receipt.batch_id == "batch_abc"
    assert receipt.input_file_id == "file_input_1"
    assert receipt.row_count == 2
    assert receipt.model == "gpt-5.5"

    loaded = read_receipt(tmp_path, "trial-uuid-1")
    assert loaded.batch_id == "batch_abc"
    assert (tmp_path / "trial-uuid-1" / "llm_batch" / "receipt.json").is_file()


def test_join_completed_output_via_adapter() -> None:
    output = (
        b'{"custom_id":"run:s2","response":{"status_code":200,"body":{}}}\n'
        b'{"custom_id":"run:s1","error":{"message":"nope"}}\n'
    )

    adapter = LiteLlmBatchAdapter(
        create_file_fn=lambda **_k: SimpleNamespace(id="f"),
        create_batch_fn=lambda **_k: SimpleNamespace(id="b"),
        retrieve_batch_fn=lambda **_k: None,
        file_content_fn=lambda **_k: output,
        cancel_batch_fn=lambda **_k: None,
    )
    from app.runtime.llm_batch.receipts import BatchReceipt

    receipt = BatchReceipt(
        run_id="r",
        batch_id="b",
        input_file_id="f",
        output_file_id="file_out",
        status="completed",
        submitted_at="2026-07-10T00:00:00Z",
        row_count=2,
        model="gpt-5.5",
    )
    joined = adapter.join_completed_output(
        receipt,
        expected_custom_ids=["run:s1", "run:s2"],
    )
    assert joined.ok_ids == ("run:s2",)
    assert joined.failed_ids == ("run:s1",)


def test_submit_rejects_empty_batch_id(tmp_path: Path) -> None:
    adapter = LiteLlmBatchAdapter(
        create_file_fn=lambda **_k: SimpleNamespace(id="file_input_1"),
        create_batch_fn=lambda **_k: SimpleNamespace(
            id="",
            status="validating",
            endpoint="/v1/chat/completions",
            input_file_id="file_input_1",
            output_file_id=None,
            error_file_id=None,
            completion_window="24h",
            request_counts={},
            model=None,
            completed_at=None,
        ),
        retrieve_batch_fn=lambda **_k: None,
        file_content_fn=lambda **_k: b"",
        cancel_batch_fn=lambda **_k: None,
    )
    rows = [
        make_chat_completions_row(
            custom_id="run:s1",
            model="gpt-5.5",
            messages=[{"role": "user", "content": "a"}],
            max_completion_tokens=100,
        )
    ]
    with pytest.raises(LlmBatchError) as exc_info:
        adapter.submit_and_receipt(rows, run_id="t", runs_root=tmp_path, model="gpt-5.5")
    assert exc_info.value.tag == "llm_batch.submit.missing-id"


def test_join_merges_error_file_rows() -> None:
    files = {
        "file_out": b'{"custom_id":"run:ok","response":{"status_code":200,"body":{}}}\n',
        "file_err": b'{"custom_id":"run:bad","error":{"message":"fail"}}\n',
    }

    def fake_content(*, file_id: str, **_k: object) -> bytes:
        return files[file_id]

    adapter = LiteLlmBatchAdapter(
        create_file_fn=lambda **_k: SimpleNamespace(id="f"),
        create_batch_fn=lambda **_k: SimpleNamespace(id="b"),
        retrieve_batch_fn=lambda **_k: None,
        file_content_fn=fake_content,
        cancel_batch_fn=lambda **_k: None,
    )
    from app.runtime.llm_batch.receipts import BatchReceipt

    receipt = BatchReceipt(
        run_id="r",
        batch_id="b",
        input_file_id="f",
        output_file_id="file_out",
        error_file_id="file_err",
        status="completed",
        submitted_at="2026-07-10T00:00:00Z",
        row_count=2,
        model="gpt-5.5",
    )
    joined = adapter.join_completed_output(
        receipt,
        expected_custom_ids=["run:ok", "run:bad"],
    )
    assert joined.ok_ids == ("run:ok",)
    assert joined.failed_ids == ("run:bad",)
