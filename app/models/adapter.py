"""`app.models.adapter` — thin `ChatOpenAI` wrapper (Story 1.3, AC-1.3-E).

Per PRD Decision 3 ("reject the LangChain cage") this module exposes ONLY a
direct `ChatOpenAI` factory with cascade-resolved model + LangSmith span
tags. No high-level agent abstractions, no LCEL wrapping; the caller gets a
plain `ChatOpenAI` it can `.invoke(...)` against.

**Pattern choice (per spec AC-1.3-E "context-var or explicit return — pick
the cleaner pattern at T1"):** EXPLICIT RETURN of `(ChatOpenAI,
ModelResolutionEntry)` tuple. The caller is responsible for appending the
entry to `RunState.model_resolution_trail`. Rationale (party-mode consensus
posture):
  - Zero global state — no ContextVar, no thread-local
  - Easy to test — no fixture-shaped setup
  - Caller's `RunState` reference is already explicit at the call site
  - Adapter stays pure-functional from RunState's perspective

LangSmith span tag set per NFR-O4 + AC-1.3-E:
`{model_id, level, requested, resolved, reason, cache_prefix_hash}`. These
ride on `ChatOpenAI(metadata={...})` so they attach automatically when
`langchain` tracing fires (LANGCHAIN_TRACING_V2=true + LANGSMITH_API_KEY set).
"""

from __future__ import annotations

import os
from typing import NamedTuple

from langchain_openai import ChatOpenAI

from app.models import selector
from app.models.state.model_resolution_entry import ModelResolutionEntry

_PLACEHOLDER_API_KEY: str = "sk-substrate-no-real-key-do-not-invoke"
"""Sentinel passed to ChatOpenAI when OPENAI_API_KEY is unset.

Slab 1 substrate exercises construction + metadata only; actual `.invoke(...)`
calls fail loudly with this sentinel because the openai SDK rejects it server-
side. Slab 3+ specialist nodes that genuinely invoke require the operator to
set OPENAI_API_KEY (NFR-S1: API-key secret management via .env discipline).
"""


class ChatModelHandle(NamedTuple):
    """Adapter return: the constructed chat model + the resolution audit entry.

    Caller appends `entry` to `RunState.model_resolution_trail` per
    NFR-X4 reproducibility.
    """

    chat: ChatOpenAI
    entry: ModelResolutionEntry


def _resolution_metadata(
    *, specialist_id: str, entry: ModelResolutionEntry, model_id: str
) -> dict[str, object]:
    """Build the LangSmith span metadata dict from the resolution entry."""
    return {
        "specialist_id": specialist_id,
        "model_id": model_id,
        "level": entry.level,
        "requested": entry.requested,
        "resolved": entry.resolved,
        "reason": entry.reason,
        "cache_prefix_hash": entry.cache_prefix_hash,
    }


def make_chat_model(
    specialist_id: str,
    per_call_override: str | None = None,
    *,
    temperature: float = 0.0,
    tier_request: str | None = None,
    system_prompt_hash: str = "",
    request_timeout: float | None = None,
    max_retries: int | None = None,
    max_completion_tokens: int | None = None,
) -> ChatModelHandle:
    """Resolve via the cascade + construct a `ChatOpenAI` with span metadata.

    The returned `ChatOpenAI` is unconfigured for API key — the langchain
    SDK reads `OPENAI_API_KEY` from env at invocation time. Slab 1 substrate
    does not exercise `.invoke(...)`; the integration test asserts construction
    + metadata only.

    ``request_timeout`` / ``max_retries`` (additive; default ``None`` preserves the
    prior behaviour) bind a HARD per-request client timeout + retry budget at
    construction. They propagate into the underlying OpenAI client (built in a
    langchain validator at construction time), so a caller on a reasoning model
    (gpt-5) can guarantee a single slow call cannot hang indefinitely. With both
    ``None`` the langchain/openai defaults apply (no hard per-request timeout; SDK
    default retries) — i.e. the legacy behaviour is unchanged.

    ``max_completion_tokens`` (additive; default ``None`` preserves the prior
    behaviour) binds a GENEROUS output-token ceiling at construction. langchain-openai
    1.x exposes this as the ``max_tokens`` field (its serialization alias IS
    ``max_completion_tokens``, the OpenAI reasoning-model param), so the value is bound
    via ``max_tokens=`` and surfaces on ``chat.max_tokens``. Reasoning models (gpt-5)
    spend output budget on hidden reasoning FIRST, then emit the visible response; a too-
    small (or unset, SDK-default-capped) ceiling truncates the visible JSON mid-structure
    — the 2026-06-29 live G0-extraction crash. Setting a generous ceiling prevents that.
    With ``None`` no ceiling is bound (legacy behaviour).
    """
    result = selector.resolve(
        specialist_id,
        per_call_override=per_call_override,
        temperature=temperature,
        tier_request=tier_request,
        system_prompt_hash=system_prompt_hash,
    )
    metadata = _resolution_metadata(
        specialist_id=specialist_id,
        entry=result.entry,
        model_id=result.model_id,
    )
    api_key = os.getenv("OPENAI_API_KEY") or _PLACEHOLDER_API_KEY
    extra: dict[str, object] = {}
    if request_timeout is not None:
        extra["timeout"] = request_timeout
    if max_retries is not None:
        extra["max_retries"] = max_retries
    if max_completion_tokens is not None:
        # langchain-openai 1.x field name is ``max_tokens`` (alias ``max_completion_tokens``);
        # binds the output ceiling and surfaces on ``chat.max_tokens``.
        extra["max_tokens"] = max_completion_tokens
    chat = ChatOpenAI(
        model=result.model_id,
        temperature=temperature,
        metadata=metadata,
        tags=[f"specialist:{specialist_id}", f"resolution_level:{result.entry.level}"],
        api_key=api_key,
        **extra,
    )
    return ChatModelHandle(chat=chat, entry=result.entry)


__all__ = ["ChatModelHandle", "make_chat_model"]
