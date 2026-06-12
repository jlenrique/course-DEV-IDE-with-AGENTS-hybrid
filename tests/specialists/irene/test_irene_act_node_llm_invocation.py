"""AC-B — Irene act-node real-LLM invocation (Story 2a.2).

@pytest.mark.llm_live test: exercises the full _plan → _act path against a real
OpenAI key. Auto-skips when OPENAI_API_KEY is unset or holds the Slab-1
placeholder sentinel (per tests/conftest.py Pass 2 fixture).

Asserts:
- Resolution-trail entry is appended at _plan
- _act builds the deterministic prompt + invokes the LLM + parses the response
- The response carries usage_metadata with prompt_tokens >= 1024 (MF2 floor)
- cache_state.cache_prefix carries the parsed output (envelope-carrier-hack
  receipt; Slab 3 will replace this with first-class specialist-output field)

Per Murat MF2: prompt-token floor pre-check fails loudly (named pytest.fail)
if the assembled prompt is below 1024 tokens — explicit failure, NOT a silent
0% report.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from app.models.state.cache_state import CacheState
from app.models.state.run_state import RunState
from app.specialists.irene.graph import _act, _plan


@pytest.mark.llm_live
def test_irene_act_node_real_llm_invocation_with_token_floor(tmp_path: Any) -> None:
    """Run _plan → _act with a real OpenAI key; assert MF2 floor + parse success."""
    from tests.specialists.irene.conftest import make_grounded_pass2_payload

    # Synthetic envelope payload — embedded in cache_state.cache_prefix per the
    # Slab-2 envelope-carrier-hack pattern documented in graph.py module
    # docstring. Slab 3 retires this hack. dp-v1.1: grounded fail-loud.
    envelope_payload: dict[str, Any] = make_grounded_pass2_payload(
        tmp_path,
        lesson_slug="test-c1m1",
        perception_artifacts=[
            {"slide_id": "s1", "confidence": "HIGH", "elements": ["title-banner"]},
            {"slide_id": "s2", "confidence": "HIGH", "elements": ["diagram", "labels"]},
        ],
        narration_profile_controls={
            "bridge_cadence_minutes": 2,
            "visual_references_per_slide": 2,
        },
    )
    payload_blob = json.dumps(
        envelope_payload, sort_keys=True, ensure_ascii=True, separators=(",", ":")
    )
    state = RunState(
        graph_version="v0.1-stub",
        temperature=0.0,  # deterministic for cache-prefix stability
        cache_state=CacheState(cache_prefix=payload_blob, entries_count=0),
    )
    plan_update = _plan(state)
    state = state.model_copy(update=plan_update)
    assert len(state.model_resolution_trail) == 1
    assert state.model_resolution_trail[-1].resolved == "gpt-5"

    act_update = _act(state)
    assert "cache_state" in act_update
    new_cache = act_update["cache_state"]
    assert new_cache["entries_count"] == 1
    # Output blob is sorted-keys JSON — parse + spot-check fields.
    output = json.loads(new_cache["cache_prefix"])
    assert output["model_id"] == "gpt-5"
    # MF2 floor: prompt_tokens >= 1024 in usage metadata.
    usage = output.get("usage")
    if usage is None:
        pytest.fail(
            "AC-B: response.usage_metadata is None — cannot verify MF2 prompt-token "
            "floor. ChatOpenAI may not be returning usage_metadata; verify model + "
            "client configuration. Cache-hit-rate measurement (AC-D) cannot proceed "
            "without this field."
        )
    prompt_tokens = usage.get("input_tokens") or usage.get("prompt_tokens")
    if prompt_tokens is None:
        pytest.fail(
            f"AC-B: usage_metadata missing prompt_tokens / input_tokens key. "
            f"Got keys: {sorted(usage.keys())}"
        )
    assert prompt_tokens >= 1024, (
        f"AC-B / MF2: prompt_tokens={prompt_tokens} below 1024 floor; "
        "Pass-2 reference bundle is too short to qualify for OpenAI prefix cache. "
        "Cannot close M1 ACCEPT-WITH-GAP at current envelope size."
    )
