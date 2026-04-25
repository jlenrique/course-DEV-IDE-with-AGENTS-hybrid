from __future__ import annotations

import json
from typing import Any

import openai
import pytest

from app.models.state.cache_state import CacheState
from app.models.state.run_state import RunState
from app.specialists.kira.graph import _act, _plan


@pytest.mark.llm_live
def test_kira_act_node_real_llm_with_mocked_dispatch(monkeypatch: pytest.MonkeyPatch) -> None:
    def _fake_dispatch(**_: Any) -> dict[str, Any]:
        return {
            "status": "mocked",
            "motion_asset_path": "tests/fixtures/specialists/kira/mock_motion.mp4",
            "kling_choices": {
                "model_name": "kling-v1",
                "mode": "std",
                "duration": 5.0,
                "negative_prompt": "",
            },
        }

    monkeypatch.setattr("app.specialists.kira.graph.dispatch_to_kling", _fake_dispatch)
    envelope_payload = {
        "slide_id": "slide-001",
        "visual_file": "artifacts/segment-001.png",
        "motion_goal": "show smooth camera pan over anatomy diagram",
    }
    payload_blob = json.dumps(
        envelope_payload, sort_keys=True, ensure_ascii=True, separators=(",", ":")
    )
    state = RunState(
        graph_version="v0.1-stub",
        temperature=0.0,
        cache_state=CacheState(cache_prefix=payload_blob, entries_count=0),
    )
    plan_update = _plan(state)
    state = state.model_copy(update=plan_update)
    try:
        act_update = _act(state)
    except openai.NotFoundError as exc:
        pytest.skip(f"Model not available in this environment: {exc}")
    output = json.loads(act_update["cache_state"]["cache_prefix"])
    assert output["motion_asset_path"].endswith(".mp4")
    assert output["visual_file"] == "artifacts/segment-001.png"
    assert output["kling_prompt"]
    assert output["model_id"] == "gpt-5-haiku"
    usage = output.get("usage")
    if usage is None:
        pytest.fail("AC-B: missing usage metadata for Kira LLM invocation")
    prompt_tokens = usage.get("input_tokens") or usage.get("prompt_tokens")
    if prompt_tokens is None:
        pytest.fail(f"AC-B: usage missing prompt token key. keys={sorted(usage.keys())}")
    assert prompt_tokens >= 1024, (
        f"AC-B: prompt_tokens={prompt_tokens} below 1024 cache-eligibility floor"
    )
