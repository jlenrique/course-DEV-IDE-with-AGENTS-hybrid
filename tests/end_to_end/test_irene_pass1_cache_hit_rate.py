from __future__ import annotations

import json
from statistics import median
from typing import Any

import pytest

from app.models.state.cache_state import CacheState
from app.models.state.run_state import RunState
from app.specialists.irene_pass1.graph import _act, _plan


def _cached_ratio(usage: dict[str, Any]) -> float:
    prompt_tokens = usage.get("input_tokens") or usage.get("prompt_tokens")
    details = usage.get("input_token_details") or usage.get("prompt_tokens_details") or {}
    cached_tokens = details.get("cached_tokens", 0)
    if not prompt_tokens or prompt_tokens < 1024:
        pytest.fail(
            "prefix below OpenAI cache threshold 1024 tokens; "
            f"prompt_tokens={prompt_tokens!r}"
        )
    return cached_tokens / prompt_tokens


@pytest.mark.llm_live
def test_irene_pass1_cache_hit_rate_post_warmup() -> None:
    payload = {
        "mode": "pass-1",
        "run_id": "cache-harness",
        "topic": "cardiac pharmacology",
        "source_corpus": "beta blockers " * 900,
    }
    ratios = []
    for _ in range(10):
        state = RunState(
            graph_version="v0.1-stub",
            temperature=0.0,
            cache_state=CacheState(
                cache_prefix=json.dumps(payload, sort_keys=True),
                entries_count=0,
            ),
        )
        state = state.model_copy(update=_plan(state))
        update = _act(state)
        output = json.loads(update["cache_state"]["cache_prefix"])
        assert output["model_id"] == "gpt-5.4"
        ratios.append(_cached_ratio(output["usage"] or {}))

    assert median(ratios[2:]) >= 0.85
