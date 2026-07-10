"""Stable vision prompt-cache key derivation (B5).

Shared contract for realtime + batch so cache-key behavior cannot drift.
Cache key is request metadata only — not a second transport.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.runtime.llm_execution_config import ExecutionMode, load_llm_execution

# Strategy → stable key prefix. Version bump here intentionally drifts keys.
_STRATEGY_KEYS: dict[str, str] = {
    "stable_perception_v1": "vision:perception:v1",
}


def derive_prompt_cache_key(
    strategy: str | None,
    *,
    node: str = "vision",
) -> str | None:
    """Return a stable, non-per-slide cache key for ``strategy``.

    Unknown/empty strategy → ``None`` (caller omits the field).
    """

    if strategy is None or not str(strategy).strip():
        return None
    key = _STRATEGY_KEYS.get(str(strategy).strip())
    if key is None:
        # Unknown strategies still produce a deterministic key so callers can
        # pin drift when the strategy string itself changes.
        return f"{node}:perception:{strategy.strip()}"
    return key


def resolve_vision_prompt_cache_key(
    *,
    mode: ExecutionMode = "realtime",
) -> str | None:
    """Resolve cache key from ``llm_execution.yaml`` vision profile for ``mode``.

    Realtime and batch strategies must match so arms cannot silently diverge.
    """

    cfg = load_llm_execution()
    node = cfg.node("vision")
    rt_strategy = node.realtime.prompt_cache_key_strategy
    bt_strategy = (
        node.batch.prompt_cache_key_strategy if node.batch is not None else None
    )
    if bt_strategy is not None and rt_strategy != bt_strategy:
        raise ValueError(
            "vision realtime/batch prompt_cache_key_strategy mismatch: "
            f"realtime={rt_strategy!r} batch={bt_strategy!r}"
        )
    profile = cfg.resolve_profile("vision", mode=mode)
    return derive_prompt_cache_key(
        profile.prompt_cache_key_strategy,
        node="vision",
    )


def prompt_cache_extra_body(cache_key: str | None) -> dict[str, str]:
    """Body fragment for chat/completions Batch JSONL (empty when no key)."""

    if not cache_key:
        return {}
    return {"prompt_cache_key": cache_key}


def extract_cached_tokens(usage: Mapping[str, Any] | None) -> int | None:
    """Pull ``cached_tokens`` from usage / prompt_tokens_details when present.

    Live measurement is optional — returns ``None`` when absent (never raises).
    """

    if not isinstance(usage, Mapping):
        return None
    direct = usage.get("cached_tokens")
    if isinstance(direct, int):
        return direct
    details = usage.get("prompt_tokens_details")
    if isinstance(details, Mapping):
        nested = details.get("cached_tokens")
        if isinstance(nested, int):
            return nested
    return None


__all__ = [
    "derive_prompt_cache_key",
    "extract_cached_tokens",
    "prompt_cache_extra_body",
    "resolve_vision_prompt_cache_key",
]
