"""Adapter integration test (Story 1.3 AC-1.3-E).

Verifies that `make_chat_model`:
  1. Returns a `ChatOpenAI` constructed with the cascade-resolved model_id
  2. Returns a `ModelResolutionEntry` matching the resolution that fired
  3. Carries the per-NFR-O4 metadata tag set
     `{model_id, level, requested, resolved, reason, cache_prefix_hash}`
  4. Is appendable to a `RunState.model_resolution_trail` by the caller
     (the explicit-return pattern chosen at T1 — see adapter docstring)

Skips the live LangSmith verification when `LANGSMITH_API_KEY` is unset
(sandbox-AC discipline), but the in-process metadata + trail-append path
still fires.
"""

from __future__ import annotations

import os

import pytest

from app.models.adapter import make_chat_model
from app.models.state import RunState


def test_adapter_returns_chat_model_with_resolution_trail_entry() -> None:
    handle = make_chat_model("any-specialist")
    assert handle.chat is not None
    # ChatOpenAI exposes the resolved model via model_name attribute
    assert handle.chat.model_name == handle.entry.resolved


def test_adapter_metadata_carries_full_resolution_tag_set() -> None:
    handle = make_chat_model("any-specialist", per_call_override="gpt-5-nano")
    metadata = handle.chat.metadata or {}
    expected_keys = {
        "specialist_id",
        "model_id",
        "level",
        "requested",
        "resolved",
        "reason",
        "cache_prefix_hash",
    }
    missing = expected_keys - set(metadata.keys())
    assert not missing, f"NFR-O4 violation: adapter metadata missing keys {missing}"
    assert metadata["model_id"] == "gpt-5-nano"
    assert metadata["level"] == "per_call"
    assert metadata["requested"] == "gpt-5-nano"
    assert metadata["resolved"] == "gpt-5-nano"
    assert metadata["cache_prefix_hash"] is not None


def test_adapter_tags_include_specialist_and_resolution_level() -> None:
    handle = make_chat_model("irene", per_call_override="gpt-5")
    tags = handle.chat.tags or []
    assert "specialist:irene" in tags
    assert "resolution_level:per_call" in tags


def test_caller_can_append_resolution_entry_to_run_state_trail() -> None:
    """Explicit-return pattern (per spec AC-1.3-E T1 choice): caller appends."""
    rs = RunState(graph_version="v0.1-stub")
    assert rs.model_resolution_trail == []

    handle = make_chat_model("any-specialist")
    rs.model_resolution_trail.append(handle.entry)

    assert len(rs.model_resolution_trail) == 1
    assert rs.model_resolution_trail[0].resolved == handle.entry.resolved
    assert rs.model_resolution_trail[0].cache_prefix_hash == handle.entry.cache_prefix_hash


def test_max_completion_tokens_binds_output_ceiling_on_chat_model() -> None:
    # Additive output-budget param (root-cause fix for the 2026-06-29 gpt-5
    # truncation crash): when set it binds the ChatOpenAI output ceiling.
    handle = make_chat_model("marcus", max_completion_tokens=123)
    assert handle.chat.max_tokens == 123


def test_max_completion_tokens_default_none_leaves_ceiling_unset() -> None:
    # Default None preserves legacy behaviour (no output ceiling bound).
    handle = make_chat_model("marcus")
    assert handle.chat.max_tokens is None


@pytest.mark.live_api
def test_langsmith_span_carries_resolution_metadata_when_key_set() -> None:
    """Live-tier assertion: LangSmith span has the resolution tag set on it.

    Skipped when `LANGSMITH_API_KEY` is unset per sandbox-AC discipline.
    The full assertion exercises the in-process metadata path; the actual
    LangSmith export verification is deferred to Story 1.1c-D's pattern
    (which 1.3 inherits — both rely on `LANGCHAIN_TRACING_V2=true`).
    """
    if not os.getenv("LANGSMITH_API_KEY"):
        pytest.skip("LANGSMITH_API_KEY unset; sandbox-AC discipline (skip-not-fail)")
    handle = make_chat_model("any-specialist")
    assert (handle.chat.metadata or {}).get("cache_prefix_hash") is not None
