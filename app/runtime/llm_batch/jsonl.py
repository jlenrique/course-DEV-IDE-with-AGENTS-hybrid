"""JSONL row encoding + pre-upload size budget for LiteLLM Batch (B1)."""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from app.runtime.llm_batch.errors import LlmBatchError

# OpenAI Batch input files are capped at 200 MiB; fail before upload.
DEFAULT_MAX_JSONL_BYTES = 200 * 1024 * 1024

CHAT_COMPLETIONS_URL = "/v1/chat/completions"


def estimate_jsonl_bytes(rows: Sequence[Mapping[str, Any]]) -> int:
    """Return UTF-8 byte length of the JSONL payload (including newlines)."""

    if not rows:
        return 0
    total = 0
    for row in rows:
        total += len(json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
        total += 1  # newline
    return total


def assert_within_size_budget(
    rows: Sequence[Mapping[str, Any]],
    *,
    max_bytes: int = DEFAULT_MAX_JSONL_BYTES,
) -> int:
    """Estimate size and raise ``LlmBatchError`` if over budget.

    Returns the estimated byte count when within budget.
    """

    size = estimate_jsonl_bytes(rows)
    if size > max_bytes:
        raise LlmBatchError(
            f"batch JSONL payload {size} bytes exceeds budget {max_bytes} bytes",
            tag="llm_batch.jsonl.oversize",
        )
    return size


def encode_batch_jsonl(
    rows: Iterable[Mapping[str, Any]],
    *,
    max_bytes: int = DEFAULT_MAX_JSONL_BYTES,
) -> bytes:
    """Serialize batch request rows to JSONL bytes after size-budget check."""

    materialized = list(rows)
    assert_within_size_budget(materialized, max_bytes=max_bytes)
    lines = [
        json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in materialized
    ]
    return ("\n".join(lines) + ("\n" if lines else "")).encode("utf-8")


def make_chat_completions_row(
    *,
    custom_id: str,
    model: str,
    messages: list[dict[str, Any]],
    max_completion_tokens: int,
    temperature: float = 0.0,
    extra_body: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build one OpenAI Batch JSONL row for ``/v1/chat/completions``."""

    body: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_completion_tokens": max_completion_tokens,
    }
    if extra_body:
        body.update(dict(extra_body))
    return {
        "custom_id": custom_id,
        "method": "POST",
        "url": CHAT_COMPLETIONS_URL,
        "body": body,
    }


__all__ = [
    "CHAT_COMPLETIONS_URL",
    "DEFAULT_MAX_JSONL_BYTES",
    "assert_within_size_budget",
    "encode_batch_jsonl",
    "estimate_jsonl_bytes",
    "make_chat_completions_row",
]
