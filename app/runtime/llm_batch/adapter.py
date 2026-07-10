"""LiteLLM Files + Batches SDK wrappers (B1).

Product Batch path — **not** ``litellm.batch_completion`` (parallel sync helper).
Normalize LiteLLM return objects into ``BatchReceipt`` / join types; do not assume
scratchpad raw-OpenAI client shapes.
"""

from __future__ import annotations

import io
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

import litellm

from app.runtime.llm_batch.errors import LlmBatchError
from app.runtime.llm_batch.join import JoinResult, join_output_rows, parse_output_jsonl
from app.runtime.llm_batch.jsonl import (
    DEFAULT_MAX_JSONL_BYTES,
    encode_batch_jsonl,
)
from app.runtime.llm_batch.receipts import (
    DEFAULT_ENDPOINT,
    DEFAULT_PROVIDER,
    BatchReceipt,
    normalize_batch_object,
    utc_now_iso,
    write_receipt,
)

# Forbidden product path — hermetic tests AST/source-guard this name.
_FORBIDDEN_BATCH_COMPLETION = "batch_completion"

CreateFileFn = Callable[..., Any]
CreateBatchFn = Callable[..., Any]
RetrieveBatchFn = Callable[..., Any]
FileContentFn = Callable[..., Any]
CancelBatchFn = Callable[..., Any]


def _ensure_not_batch_completion(fn: Callable[..., Any], *, label: str) -> None:
    name = getattr(fn, "__name__", "")
    qual = getattr(fn, "__qualname__", "")
    if _FORBIDDEN_BATCH_COMPLETION in name or _FORBIDDEN_BATCH_COMPLETION in qual:
        raise LlmBatchError(
            f"refusing to use litellm.{_FORBIDDEN_BATCH_COMPLETION} as Batch transport ({label})",
            tag="llm_batch.forbidden.batch_completion",
        )


class LiteLlmBatchAdapter:
    """Thin LiteLLM Batch client with injectable SDK callables (hermetic T0)."""

    def __init__(
        self,
        *,
        custom_llm_provider: str = DEFAULT_PROVIDER,
        endpoint: str = DEFAULT_ENDPOINT,
        completion_window: str = "24h",
        max_jsonl_bytes: int = DEFAULT_MAX_JSONL_BYTES,
        create_file_fn: CreateFileFn | None = None,
        create_batch_fn: CreateBatchFn | None = None,
        retrieve_batch_fn: RetrieveBatchFn | None = None,
        file_content_fn: FileContentFn | None = None,
        cancel_batch_fn: CancelBatchFn | None = None,
    ) -> None:
        self.custom_llm_provider = custom_llm_provider
        self.endpoint = endpoint
        self.completion_window = completion_window
        self.max_jsonl_bytes = max_jsonl_bytes

        self._create_file = create_file_fn or litellm.create_file
        self._create_batch = create_batch_fn or litellm.create_batch
        self._retrieve_batch = retrieve_batch_fn or litellm.retrieve_batch
        self._file_content = file_content_fn or litellm.file_content
        self._cancel_batch = cancel_batch_fn or litellm.cancel_batch

        for label, fn in (
            ("create_file", self._create_file),
            ("create_batch", self._create_batch),
            ("retrieve_batch", self._retrieve_batch),
            ("file_content", self._file_content),
            ("cancel_batch", self._cancel_batch),
        ):
            _ensure_not_batch_completion(fn, label=label)

        # Defense in depth: never bind batch_completion on this instance.
        if hasattr(self, _FORBIDDEN_BATCH_COMPLETION):
            raise LlmBatchError(
                "adapter must not expose batch_completion",
                tag="llm_batch.forbidden.batch_completion",
            )

    def upload_batch_jsonl(
        self,
        rows: Sequence[Mapping[str, Any]],
        *,
        filename: str = "batch_input.jsonl",
    ) -> str:
        """Encode rows, enforce size budget, upload via LiteLLM ``create_file``."""

        payload = encode_batch_jsonl(rows, max_bytes=self.max_jsonl_bytes)
        file_obj = (filename, io.BytesIO(payload), "application/jsonl")
        result = self._create_file(
            file=file_obj,
            purpose="batch",
            custom_llm_provider=self.custom_llm_provider,
        )
        file_id = _extract_id(result)
        if not file_id:
            raise LlmBatchError(
                "LiteLLM create_file returned no file id",
                tag="llm_batch.upload.missing-id",
            )
        return file_id

    def create_batch(
        self,
        *,
        input_file_id: str,
        metadata: dict[str, str] | None = None,
    ) -> Any:
        """Submit Batch job via LiteLLM ``create_batch``."""

        return self._create_batch(
            completion_window=self.completion_window,
            endpoint=self.endpoint,
            input_file_id=input_file_id,
            custom_llm_provider=self.custom_llm_provider,
            metadata=metadata,
        )

    def retrieve_batch(self, batch_id: str) -> Any:
        return self._retrieve_batch(
            batch_id=batch_id,
            custom_llm_provider=self.custom_llm_provider,
        )

    def cancel_batch(self, batch_id: str) -> Any:
        return self._cancel_batch(
            batch_id=batch_id,
            custom_llm_provider=self.custom_llm_provider,
        )

    def download_output_jsonl(self, output_file_id: str) -> bytes:
        content = self._file_content(
            file_id=output_file_id,
            custom_llm_provider=self.custom_llm_provider,
        )
        return _coerce_file_bytes(content)

    def submit_and_receipt(
        self,
        rows: Sequence[Mapping[str, Any]],
        *,
        run_id: str,
        runs_root: Path,
        model: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> BatchReceipt:
        """Upload JSONL → create batch → normalize + persist receipt."""

        input_file_id = self.upload_batch_jsonl(rows)
        batch_obj = self.create_batch(input_file_id=input_file_id, metadata=metadata)
        receipt = normalize_batch_object(
            batch_obj,
            run_id=run_id,
            row_count=len(rows),
            model=model,
            submitted_at=utc_now_iso(),
            metadata=metadata,
        )
        if not receipt.input_file_id:
            receipt = receipt.model_copy(update={"input_file_id": input_file_id})
        if not receipt.batch_id:
            raise LlmBatchError(
                "LiteLLM create_batch returned no batch id",
                tag="llm_batch.submit.missing-id",
            )
        write_receipt(runs_root, receipt)
        return receipt

    def join_completed_output(
        self,
        receipt: BatchReceipt,
        *,
        expected_custom_ids: Sequence[str] | None = None,
    ) -> JoinResult:
        """Download output (+ error) files and join by ``custom_id``."""

        if not receipt.output_file_id and not receipt.error_file_id:
            raise LlmBatchError(
                f"batch {receipt.batch_id!r} has no output_file_id or "
                f"error_file_id yet (status={receipt.status})",
                tag="llm_batch.download.no-output",
            )
        rows: list[dict[str, Any]] = []
        if receipt.output_file_id:
            rows.extend(parse_output_jsonl(self.download_output_jsonl(receipt.output_file_id)))
        if receipt.error_file_id:
            rows.extend(parse_output_jsonl(self.download_output_jsonl(receipt.error_file_id)))
        return join_output_rows(rows, expected_custom_ids=expected_custom_ids)


def _extract_id(obj: Any) -> str:
    if obj is None:
        return ""
    if isinstance(obj, dict):
        return str(obj.get("id") or "")
    return str(getattr(obj, "id", "") or "")


def _coerce_file_bytes(content: Any) -> bytes:
    if isinstance(content, bytes):
        return content
    if isinstance(content, str):
        return content.encode("utf-8")
    # LiteLLM HttpxBinaryResponseContent
    if hasattr(content, "content") and isinstance(content.content, (bytes, bytearray)):
        return bytes(content.content)
    if hasattr(content, "read"):
        data = content.read()
        if isinstance(data, bytes):
            return data
        if isinstance(data, str):
            return data.encode("utf-8")
        raise LlmBatchError(
            f"unsupported file_content .read() type: {type(data)!r}",
            tag="llm_batch.download.bad-content",
        )
    raise LlmBatchError(
        f"unsupported file_content return type: {type(content)!r}",
        tag="llm_batch.download.bad-content",
    )


__all__ = ["LiteLlmBatchAdapter"]
