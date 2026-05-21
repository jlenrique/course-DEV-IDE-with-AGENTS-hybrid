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


def _state(cache_prefix: str) -> RunState:
    return RunState(
        graph_version="v0.1-stub",
        temperature=0.3,
        cache_state=CacheState(cache_prefix=cache_prefix, entries_count=0),
        model_resolution_trail=[
            ModelResolutionEntry(
                level="per_specialist",
                requested="gpt-5.4",
                resolved="gpt-5.4",
                reason="test",
                timestamp=datetime.now(UTC),
                cache_prefix_hash="c" * 64,
            )
        ],
    )


def _intent_payload(**overrides: Any) -> dict[str, Any]:
    row = {
        "intent": "Find peer-reviewed evidence for spacing effects.",
        "provider_hints": [{"provider": "scite", "params": {"mode": "search"}}],
        "acceptance_criteria": {
            "mechanical": {"min_results": 3},
            "provider_scored": {"authority_tier_min": "peer-reviewed"},
            "semantic_deferred": "Tracy screens rows against the narration claim.",
        },
        "cross_validate": False,
    }
    row.update(overrides)
    return {"retrieval_intents": [row]}


@dataclass
class _Handle:
    content: str

    @property
    def chat(self):
        return SimpleNamespace(
            invoke=lambda _messages: SimpleNamespace(
                content=self.content,
                usage_metadata={
                    "input_tokens": 1400,
                    "input_token_details": {"cached_tokens": 1200},
                },
            )
        )


def test_parse_retrieval_intents_ok() -> None:
    out = tracy_act.parse_retrieval_intents(json.dumps(_intent_payload()))
    assert out[0]["intent"].startswith("Find peer-reviewed")
    assert out[0]["provider_hints"][0]["provider"] == "scite"


@pytest.mark.parametrize(
    "raw,tag",
    [
        ("{bad", "retrieval_intent.parsed.malformed"),
        ('{"retrieval_intents":[]}', "retrieval_intent.parsed.empty"),
        ('{"retrieval_intents":"x"}', "retrieval_intent.parsed.empty"),
        (
            json.dumps(_intent_payload(provider_hints=[{"provider": "unknown", "params": {}}])),
            "retrieval_intent.parsed.provider-unknown",
        ),
    ],
)
def test_parse_retrieval_intents_branch_errors(raw: str, tag: str) -> None:
    with pytest.raises(tracy_act.RetrievalIntentParseError) as exc_info:
        tracy_act.parse_retrieval_intents(raw)
    assert exc_info.value.tag == tag


def test_tracy_act_returns_retrieval_intents() -> None:
    update = tracy_act.act(
        _state(json.dumps({"topic": "spacing effects"})),
        handle=_Handle(json.dumps(_intent_payload())),
        model_id="gpt-5.4",
    )
    output = json.loads(update["cache_state"]["cache_prefix"])
    assert output["retrieval_intents"][0]["provider_hints"][0]["provider"] == "scite"
    assert output["posture_tag"] == "posture.selected:supporting_evidence"
    assert update["model_resolution_trail"][-1].reason == "retrieval_intent.parsed.ok"


def test_tracy_act_malformed_envelope_sets_trail_tag() -> None:
    state = _state("{bad")
    with pytest.raises(tracy_act.RetrievalIntentParseError) as exc_info:
        tracy_act.act(state, handle=_Handle(json.dumps(_intent_payload())), model_id="gpt-5.4")
    assert exc_info.value.tag == "retrieval_intent.parsed.malformed"


def test_tracy_act_loc_budget() -> None:
    logical_lines = [
        line for line in inspect.getsource(tracy_act.act).splitlines() if line.strip()
    ]
    assert len(logical_lines) <= 150
