from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime

from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.dan import _act as dan_act


@dataclass
class _Response:
    content: str
    usage_metadata: dict[str, object]


class _Chat:
    def __init__(self, payload: dict[str, object]) -> None:
        self.payload = payload

    def invoke(self, messages: list[dict[str, str]]) -> _Response:
        assert messages[0]["role"] == "system"
        return _Response(
            content=json.dumps(self.payload),
            usage_metadata={
                "input_tokens": 4096,
                "input_token_details": {"cached_tokens": 3600},
            },
        )


class _Handle:
    def __init__(self, payload: dict[str, object]) -> None:
        self.chat = _Chat(payload)


def _state() -> RunState:
    return RunState(
        graph_version="v0.1-stub",
        cache_state=CacheState(
            cache_prefix=json.dumps({"topic": "renal physiology"}),
            entries_count=0,
        ),
        model_resolution_trail=[
            ModelResolutionEntry(
                level="per_specialist",
                requested="reasoning",
                resolved="gpt-5.4",
                reason="test",
                timestamp=datetime.now(UTC),
                cache_prefix_hash="a" * 64,
            )
        ],
    )


def _llm_payload() -> dict[str, object]:
    return {
        "contributions": [
            {
                "gate_id": "G1",
                "contribution_type": "creative_director_critique",
                "prose": "Open with the learner tension before the outline branches.",
            },
            {
                "gate_id": "G1A",
                "contribution_type": "narrative_arc_check",
                "prose": "Hold cluster boundaries to question changes, not source headings.",
            },
            {
                "gate_id": "G2",
                "contribution_type": "tone_voice_consistency_review",
                "prose": "Keep narration grounded in the visible storyboard action.",
            },
        ]
    }


def test_dan_act_emits_g1_g1a_g2_aux_contributions() -> None:
    update = dan_act.act(_state(), handle=_Handle(_llm_payload()), model_id="gpt-5.4")
    output = json.loads(update["cache_state"]["cache_prefix"])
    assert output["specialist_id"] == "dan"
    assert output["model_id"] == "gpt-5.4"
    assert output["verb"] == "proceed"
    assert set(output["aux_contributions_by_gate"]) == {"G1", "G1A", "G2"}


def test_dan_contributions_obey_word_limits_and_advisory_partition() -> None:
    rows = dan_act.parse_aux_contributions(_llm_payload(), {})
    limits = {"G1": 300, "G1A": 200, "G2": 300}
    for row in rows:
        assert len(row["prose"].split()) <= limits[row["gate_id"]]
        assert row["advisory"] is True
        assert row["blocking"] is False


def test_dan_fallback_covers_all_three_gates() -> None:
    rows = dan_act.parse_aux_contributions({"contributions": []}, {"topic": "shock"})
    assert {row["gate_id"] for row in rows} == {"G1", "G1A", "G2"}
