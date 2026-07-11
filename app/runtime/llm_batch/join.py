"""Join Batch output rows by ``custom_id`` (B1)."""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from app.runtime.llm_batch.errors import LlmBatchError


@dataclass(frozen=True)
class JoinedBatchRow:
    """One output row keyed by ``custom_id`` after join."""

    custom_id: str
    ok: bool
    response: Mapping[str, Any] | None = None
    error: Mapping[str, Any] | None = None
    raw: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class JoinResult:
    """Out-of-order join result; failed rows are isolated, not dropped silently."""

    by_custom_id: dict[str, JoinedBatchRow]
    order_seen: tuple[str, ...]
    missing_custom_ids: tuple[str, ...]
    unexpected_custom_ids: tuple[str, ...]

    @property
    def ok_ids(self) -> tuple[str, ...]:
        return tuple(cid for cid, row in self.by_custom_id.items() if row.ok)

    @property
    def failed_ids(self) -> tuple[str, ...]:
        return tuple(cid for cid, row in self.by_custom_id.items() if not row.ok)


def _row_ok(row: Mapping[str, Any]) -> bool:
    error = row.get("error")
    if error not in (None, "", {}, []):
        return False
    response = row.get("response")
    if not isinstance(response, Mapping):
        return False
    status = response.get("status_code")
    if status is None:
        return True
    try:
        return int(status) < 400
    except (TypeError, ValueError):
        return False


def join_output_rows(
    rows: Iterable[Mapping[str, Any]],
    *,
    expected_custom_ids: Sequence[str] | None = None,
) -> JoinResult:
    """Index output JSONL rows by ``custom_id``; order of ``rows`` is irrelevant."""

    by_id: dict[str, JoinedBatchRow] = {}
    order: list[str] = []
    for raw in rows:
        custom_id = str(raw.get("custom_id") or "")
        if not custom_id:
            raise LlmBatchError(
                "batch output row missing custom_id",
                tag="llm_batch.join.missing-custom-id",
            )
        if custom_id in by_id:
            raise LlmBatchError(
                f"duplicate custom_id in batch output: {custom_id!r}",
                tag="llm_batch.join.duplicate-custom-id",
            )
        order.append(custom_id)
        ok = _row_ok(raw)
        error_val = raw.get("error")
        by_id[custom_id] = JoinedBatchRow(
            custom_id=custom_id,
            ok=ok,
            response=raw.get("response") if isinstance(raw.get("response"), Mapping) else None,
            error=error_val if isinstance(error_val, Mapping) else None,
            raw=dict(raw),
        )

    expected = list(expected_custom_ids) if expected_custom_ids is not None else list(by_id)
    missing = tuple(cid for cid in expected if cid not in by_id)
    unexpected = tuple(cid for cid in by_id if cid not in set(expected))
    return JoinResult(
        by_custom_id=by_id,
        order_seen=tuple(order),
        missing_custom_ids=missing,
        unexpected_custom_ids=unexpected,
    )


def parse_output_jsonl(text: str | bytes) -> list[dict[str, Any]]:
    """Parse Batch output-file JSONL into row dicts."""

    if isinstance(text, bytes):
        text = text.decode("utf-8")
    rows: list[dict[str, Any]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        payload = json.loads(line)
        if isinstance(payload, dict):
            rows.append(payload)
    return rows


__all__ = [
    "JoinResult",
    "JoinedBatchRow",
    "join_output_rows",
    "parse_output_jsonl",
]
