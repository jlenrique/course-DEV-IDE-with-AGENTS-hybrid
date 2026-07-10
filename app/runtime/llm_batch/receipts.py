"""Batch receipts persisted under ``runs/<uuid>/llm_batch/`` (B1)."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

DEFAULT_ENDPOINT = "/v1/chat/completions"
DEFAULT_PROVIDER = "openai"
RECEIPT_FILENAME = "receipt.json"


class BatchReceipt(BaseModel):
    """Normalized receipt — LiteLLM return shapes are mapped into this type."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    run_id: str
    batch_id: str
    input_file_id: str
    output_file_id: str | None = None
    error_file_id: str | None = None
    status: str
    endpoint: str = DEFAULT_ENDPOINT
    custom_llm_provider: str = DEFAULT_PROVIDER
    model: str | None = None
    completion_window: str = "24h"
    submitted_at: str
    completed_at: str | None = None
    row_count: int = Field(..., ge=0)
    request_counts: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, str] = Field(default_factory=dict)


def receipt_dir(runs_root: Path, run_id: str) -> Path:
    """Return ``runs/<run_id>/llm_batch/`` (created by ``write_receipt``)."""

    return Path(runs_root) / run_id / "llm_batch"


def write_receipt(runs_root: Path, receipt: BatchReceipt) -> Path:
    """Persist receipt JSON under ``runs/<run_id>/llm_batch/receipt.json``."""

    target_dir = receipt_dir(runs_root, receipt.run_id)
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / RECEIPT_FILENAME
    path.write_text(
        json.dumps(receipt.model_dump(mode="python"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def read_receipt(runs_root: Path, run_id: str) -> BatchReceipt:
    """Load a previously written receipt."""

    path = receipt_dir(runs_root, run_id) / RECEIPT_FILENAME
    payload = json.loads(path.read_text(encoding="utf-8"))
    return BatchReceipt.model_validate(payload)


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_batch_object(
    batch_obj: Any,
    *,
    run_id: str,
    row_count: int,
    model: str | None = None,
    submitted_at: str | None = None,
    metadata: dict[str, str] | None = None,
) -> BatchReceipt:
    """Map a LiteLLM / OpenAI-like batch object into ``BatchReceipt``.

    Accepts pydantic models, dicts, or attribute bags — dispatch details may
    differ from the scratchpad raw-OpenAI client.
    """

    def _get(name: str, default: Any = None) -> Any:
        if isinstance(batch_obj, dict):
            return batch_obj.get(name, default)
        return getattr(batch_obj, name, default)

    request_counts = _get("request_counts") or {}
    if hasattr(request_counts, "model_dump"):
        request_counts = request_counts.model_dump()
    elif not isinstance(request_counts, dict):
        request_counts = dict(request_counts) if request_counts else {}

    return BatchReceipt(
        run_id=run_id,
        batch_id=str(_get("id") or ""),
        input_file_id=str(_get("input_file_id") or ""),
        output_file_id=_optional_str(_get("output_file_id")),
        error_file_id=_optional_str(_get("error_file_id")),
        status=str(_get("status") or "unknown"),
        endpoint=str(_get("endpoint") or DEFAULT_ENDPOINT),
        custom_llm_provider=DEFAULT_PROVIDER,
        model=model or _optional_str(_get("model")),
        completion_window=str(_get("completion_window") or "24h"),
        submitted_at=submitted_at or utc_now_iso(),
        completed_at=_optional_str(_get("completed_at")),
        row_count=row_count,
        request_counts={str(k): v for k, v in request_counts.items()},
        metadata=dict(metadata or {}),
    )


def _optional_str(value: Any) -> str | None:
    if value is None or value == "":
        return None
    return str(value)


__all__ = [
    "BatchReceipt",
    "DEFAULT_ENDPOINT",
    "DEFAULT_PROVIDER",
    "RECEIPT_FILENAME",
    "normalize_batch_object",
    "read_receipt",
    "receipt_dir",
    "utc_now_iso",
    "write_receipt",
]
