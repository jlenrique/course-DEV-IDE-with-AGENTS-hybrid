"""Vision Batch route (B2) — LiteLLM multimodal Batch for 07G perception.

ON only when payload ``llm_execution_mode == "batch"`` exactly and A3 marks
vision v1-routable. OFF path never imports/calls this module's submit path from
``act`` (``act`` branches before calling here).
"""

from __future__ import annotations

import time
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

from app.runtime.llm_batch.adapter import LiteLlmBatchAdapter
from app.runtime.llm_batch.cost_report import emit_batch_cost_report_fail_soft
from app.runtime.llm_batch.errors import LlmBatchError, WaitingForProviderBatchError
from app.runtime.llm_batch.jsonl import make_chat_completions_row
from app.runtime.llm_batch.prompt_cache import (
    prompt_cache_extra_body,
    resolve_vision_prompt_cache_key,
)
from app.runtime.llm_batch.receipts import (
    BatchReceipt,
    normalize_batch_object,
    read_receipt,
    utc_now_iso,
    write_receipt,
)
from app.runtime.llm_batch_eligibility import load_batch_eligibility
from app.runtime.llm_execution_config import load_llm_execution
from app.specialists.vision.payload_contract import VisionProviderResponse
from app.specialists.vision.provider import (
    VisionProviderError,
    _parse_response,
    build_perception_openai_messages,
)

TERMINAL_STATUSES = frozenset({"completed", "failed", "expired", "cancelled", "canceled"})
DEFAULT_POLL_INTERVAL_S = 2.0
DEFAULT_POLL_TIMEOUT_S = 3600.0


def resolve_vision_execution_mode(payload: dict[str, Any]) -> str:
    """Return payload mode; only exact ``batch`` is ON."""

    raw = payload.get("llm_execution_mode")
    if raw is None:
        return "realtime"
    return str(raw)


def is_batch_mode(payload: dict[str, Any]) -> bool:
    return resolve_vision_execution_mode(payload) == "batch"


def custom_id_for(run_id: str, slide_id: str) -> str:
    return f"{run_id}:{slide_id}"


def _assert_unique_slide_ids(slides: Sequence[tuple[str, Path]]) -> None:
    """Fail loud on blank or duplicate slide_id before any Files API call."""

    seen: set[str] = set()
    for slide_id, _ in slides:
        if not str(slide_id).strip():
            raise VisionProviderError(
                "vision batch slide_id is blank",
                tag="vision.batch.slide-id-invalid",
            )
        if slide_id in seen:
            raise VisionProviderError(
                f"vision batch duplicate slide_id={slide_id!r}",
                tag="vision.batch.slide-id-invalid",
            )
        seen.add(slide_id)


def build_vision_batch_rows(
    slides: Sequence[tuple[str, Path]],
    *,
    run_id: str,
    model: str,
    max_completion_tokens: int,
    prompt_cache_key: str | None = None,
) -> list[dict[str, Any]]:
    """Build N chat-completions JSONL rows (text before image_url).

    ``prompt_cache_key`` defaults to the shared B5 vision strategy key when
    omitted (stable across slides — not per-slide).
    """

    _assert_unique_slide_ids(slides)
    cache_key = (
        prompt_cache_key
        if prompt_cache_key is not None
        else resolve_vision_prompt_cache_key(mode="batch")
    )
    extra = prompt_cache_extra_body(cache_key)
    rows: list[dict[str, Any]] = []
    for slide_id, png_path in slides:
        messages = build_perception_openai_messages(png_path, slide_id=slide_id)
        rows.append(
            make_chat_completions_row(
                custom_id=custom_id_for(run_id, slide_id),
                model=model,
                messages=messages,
                max_completion_tokens=max_completion_tokens,
                extra_body=extra or None,
            )
        )
    return rows


def extract_assistant_text(joined_raw: dict[str, Any], *, custom_id: str) -> str:
    """Pull assistant text from an OpenAI Batch output row body."""

    response = joined_raw.get("response")
    if not isinstance(response, dict):
        raise VisionProviderError(
            f"batch row {custom_id!r} missing response object",
            tag="vision.batch.row-shape",
        )
    body = response.get("body")
    if not isinstance(body, dict):
        raise VisionProviderError(
            f"batch row {custom_id!r} missing response.body",
            tag="vision.batch.row-shape",
        )
    choices = body.get("choices")
    if not isinstance(choices, list) or not choices:
        raise VisionProviderError(
            f"batch row {custom_id!r} has no choices",
            tag="vision.batch.row-shape",
        )
    message = choices[0].get("message") if isinstance(choices[0], dict) else None
    if not isinstance(message, dict):
        raise VisionProviderError(
            f"batch row {custom_id!r} missing message",
            tag="vision.batch.row-shape",
        )
    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise VisionProviderError(
            f"batch row {custom_id!r} empty assistant content",
            tag="vision.batch.row-shape",
        )
    return content


def poll_until_terminal(
    adapter: LiteLlmBatchAdapter,
    batch_id: str,
    *,
    run_id: str,
    row_count: int,
    model: str | None,
    sleep_fn: Callable[[float], None] = time.sleep,
    interval_s: float = DEFAULT_POLL_INTERVAL_S,
    timeout_s: float = DEFAULT_POLL_TIMEOUT_S,
) -> BatchReceipt:
    """Poll LiteLLM retrieve until a terminal status; return normalized receipt."""

    deadline = time.monotonic() + timeout_s
    last: BatchReceipt | None = None
    while time.monotonic() < deadline:
        batch_obj = adapter.retrieve_batch(batch_id)
        last = normalize_batch_object(
            batch_obj,
            run_id=run_id,
            row_count=row_count,
            model=model,
            submitted_at=utc_now_iso(),
        )
        if last.status in TERMINAL_STATUSES:
            return last
        sleep_fn(interval_s)
    raise LlmBatchError(
        f"batch {batch_id!r} poll timed out after {timeout_s}s "
        f"(last_status={getattr(last, 'status', None)!r})",
        tag="vision.batch.poll-timeout",
    )


def run_vision_batch_perception(
    slides: Sequence[tuple[str, Path]],
    *,
    run_id: str,
    runs_root: Path,
    adapter: LiteLlmBatchAdapter | None = None,
    sleep_fn: Callable[[float], None] = time.sleep,
    poll_interval_s: float = DEFAULT_POLL_INTERVAL_S,
    poll_timeout_s: float = DEFAULT_POLL_TIMEOUT_S,
    wait_policy: str = "block",
) -> list[VisionProviderResponse]:
    """Submit-or-resume one Batch job for all slides; parse via ``_parse_response``.

    ``wait_policy``:
    - ``block`` — poll until terminal (harness / hermetic completed fakes).
    - ``raise_pending`` — production: if non-terminal after submit/retrieve,
      raise ``WaitingForProviderBatchError`` (B3 pause) without sleep-loop.
    """

    if not load_batch_eligibility().is_v1_batch_routable("vision"):
        raise VisionProviderError(
            "llm_execution_mode=batch but vision is not v1 batch-routable",
            tag="vision.batch.ineligible",
        )
    if not slides:
        return []

    _assert_unique_slide_ids(slides)
    profile = load_llm_execution().resolve_profile("vision", mode="batch")
    model = profile.model
    max_tokens = profile.max_completion_tokens
    client = adapter or LiteLlmBatchAdapter()
    expected_ids = [custom_id_for(run_id, slide_id) for slide_id, _ in slides]

    receipt: BatchReceipt | None = None
    receipt_path = runs_root / run_id / "llm_batch" / "receipt.json"
    if receipt_path.is_file():
        try:
            existing = read_receipt(runs_root, run_id)
        except (OSError, ValueError) as exc:
            raise LlmBatchError(
                f"vision batch receipt unreadable at {receipt_path}: {exc}",
                tag="vision.batch.receipt-corrupt",
            ) from exc
        if not existing.batch_id:
            raise LlmBatchError(
                f"vision batch receipt at {receipt_path} has empty batch_id",
                tag="vision.batch.receipt-corrupt",
            )
        if existing.row_count != len(slides):
            raise LlmBatchError(
                f"vision batch receipt row_count={existing.row_count} "
                f"!= current slides={len(slides)} at {receipt_path}",
                tag="vision.batch.receipt-stale",
            )
        receipt = existing

    if receipt is None:
        rows = build_vision_batch_rows(
            slides,
            run_id=run_id,
            model=model,
            max_completion_tokens=max_tokens,
        )
        receipt = client.submit_and_receipt(
            rows,
            run_id=run_id,
            runs_root=runs_root,
            model=model,
            metadata={"node": "vision"},
        )

    if receipt.status not in TERMINAL_STATUSES:
        if wait_policy == "raise_pending":
            write_receipt(runs_root, receipt)
            raise WaitingForProviderBatchError(
                f"vision batch {receipt.batch_id!r} still status={receipt.status!r}; "
                f"resume with: trial resume-batch --trial-id {run_id}",
                batch_id=receipt.batch_id,
                receipt_path=receipt_path,
                receipt=receipt,
            )
        polled = poll_until_terminal(
            client,
            receipt.batch_id,
            run_id=run_id,
            row_count=len(slides),
            model=model,
            sleep_fn=sleep_fn,
            interval_s=poll_interval_s,
            timeout_s=poll_timeout_s,
        )
        receipt = polled.model_copy(
            update={
                "submitted_at": receipt.submitted_at,
                "metadata": dict(receipt.metadata),
                "model": receipt.model or polled.model,
            }
        )
        write_receipt(runs_root, receipt)

    if receipt.status != "completed":
        raise LlmBatchError(
            f"vision batch {receipt.batch_id!r} ended status={receipt.status!r}",
            tag="vision.batch.not-completed",
        )

    joined = client.join_completed_output(receipt, expected_custom_ids=expected_ids)
    if joined.missing_custom_ids:
        raise LlmBatchError(
            f"vision batch missing custom_ids: {joined.missing_custom_ids}",
            tag="vision.batch.missing-rows",
        )
    if joined.unexpected_custom_ids:
        raise LlmBatchError(
            f"vision batch unexpected custom_ids: {joined.unexpected_custom_ids}",
            tag="vision.batch.unexpected-rows",
        )
    emit_batch_cost_report_fail_soft(
        runs_root=runs_root, receipt=receipt, joined=joined
    )

    path_by_id = {custom_id_for(run_id, sid): path for sid, path in slides}
    slide_by_id = {custom_id_for(run_id, sid): sid for sid, _ in slides}
    results: list[VisionProviderResponse] = []
    for custom_id in expected_ids:
        row = joined.by_custom_id[custom_id]
        if not row.ok:
            raise VisionProviderError(
                f"vision batch row failed custom_id={custom_id!r} error={row.error!r}",
                tag="vision.batch.row-failed",
            )
        text = extract_assistant_text(dict(row.raw), custom_id=custom_id)
        try:
            results.append(
                _parse_response(
                    text,
                    slide_id=slide_by_id[custom_id],
                    model_id=model,
                    source_png_path=str(path_by_id[custom_id]),
                )
            )
        except VisionProviderError as exc:
            raise VisionProviderError(
                f"vision batch row {custom_id!r} parse failed: {exc}",
                status_code=exc.status_code,
                tag=exc.tag,
            ) from exc
    return results


__all__ = [
    "build_vision_batch_rows",
    "custom_id_for",
    "extract_assistant_text",
    "is_batch_mode",
    "poll_until_terminal",
    "resolve_vision_execution_mode",
    "run_vision_batch_perception",
]
