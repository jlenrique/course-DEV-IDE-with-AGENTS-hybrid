from __future__ import annotations

import inspect
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any

import pytest

from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.tracy import _act as tracy_act


@dataclass
class _FakeChat:
    response_text: str

    def invoke(self, messages: list[dict[str, str]]) -> SimpleNamespace:
        assert messages[0]["role"] == "system"
        assert "RetrievalIntent" in messages[1]["content"]
        return SimpleNamespace(
            content=self.response_text,
            usage_metadata={
                "input_tokens": 1400,
                "input_token_details": {"cached_tokens": 1190},
            },
        )


@dataclass
class _FakeHandle:
    response_text: str

    @property
    def chat(self) -> _FakeChat:
        return _FakeChat(self.response_text)


def _state(payload: dict[str, Any]) -> RunState:
    return RunState(
        graph_version="v0.1-stub",
        temperature=0.3,
        cache_state=CacheState(cache_prefix=json.dumps(payload, sort_keys=True)),
        model_resolution_trail=[
            ModelResolutionEntry(
                level="per_specialist",
                requested="gpt-5.4",
                resolved="gpt-5.4",
                reason="test",
                timestamp=datetime.now(UTC),
                cache_prefix_hash="b" * 64,
            )
        ],
    )


def _intent_payload(*, cross_validate: bool) -> dict[str, Any]:
    hints = [{"provider": "scite", "params": {"mode": "search"}}]
    if cross_validate:
        hints.append({"provider": "consensus", "params": {"mode": "search"}})
    return {
        "retrieval_intents": [
            {
                "intent": "Find peer-reviewed evidence for spacing effects.",
                "provider_hints": hints,
                "acceptance_criteria": {
                    "mechanical": {"min_results": 3},
                    "provider_scored": {"authority_tier_min": "peer-reviewed"},
                    "semantic_deferred": "Tracy screens rows against the narration claim.",
                },
                "cross_validate": cross_validate,
            }
        ]
    }


@pytest.mark.parametrize("cross_validate", [False, True])
def test_tracy_emits_retrieval_intent_shape(cross_validate: bool) -> None:
    update = tracy_act.act(
        _state({"topic": "spacing effect"}),
        handle=_FakeHandle(json.dumps(_intent_payload(cross_validate=cross_validate))),
        model_id="gpt-5.4",
    )
    output = json.loads(update["cache_state"]["cache_prefix"])
    intent = output["retrieval_intents"][0]
    assert output["model_id"] == "gpt-5.4"
    assert intent["intent"].startswith("Find peer-reviewed evidence")
    assert intent["provider_hints"]
    assert intent["cross_validate"] is cross_validate
    assert set(intent["acceptance_criteria"]) == {
        "mechanical",
        "provider_scored",
        "semantic_deferred",
    }
    assert update["model_resolution_trail"][-1].reason == "retrieval_intent.parsed.ok"


def test_prompt_assembly_is_byte_stable() -> None:
    payload = {"topic": "spacing effect", "mode": "pass-2"}
    assert tracy_act.assemble_tracy_prompt(payload) == tracy_act.assemble_tracy_prompt(
        dict(reversed(payload.items()))
    )


def test_unknown_provider_hints_fail_loud() -> None:
    bad = _intent_payload(cross_validate=False)
    bad["retrieval_intents"][0]["provider_hints"][0]["provider"] = "unknown"
    with pytest.raises(tracy_act.RetrievalIntentParseError) as exc_info:
        tracy_act.parse_retrieval_intents(json.dumps(bad))
    assert exc_info.value.tag == "retrieval_intent.parsed.provider-unknown"


def test_malformed_envelope_fails_loud() -> None:
    state = _state({"topic": "spacing effect"})
    state.cache_state = CacheState(cache_prefix="{bad")
    with pytest.raises(tracy_act.RetrievalIntentParseError) as exc_info:
        tracy_act.decode_envelope_payload(state)
    assert exc_info.value.tag == "retrieval_intent.parsed.malformed"


def test_tracy_act_loc_budget() -> None:
    logical_lines = [line for line in inspect.getsource(tracy_act.act).splitlines() if line.strip()]
    assert len(logical_lines) <= 150
