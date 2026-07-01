"""Leg-C review remediation — P1 (LLM-payload strip) + P2 (fork-#2 false-positive).

RED-first:

- P1: ``min_cluster_floor`` (and any scripted-derived key) must NOT reach the
      LLM-visible ``envelope_payload`` serialized into the model's user content.
      The model must receive BYTE-IDENTICAL input whether or not a floor is bound —
      the deterministic post-hoc split is the ONLY delta (protects the live
      differential + honors the "never re-parameterize the LLM objective" amendment).
- P2: a non-list ``structural_outline`` under a BOUND floor must NOT raise
      ``DeadFloorConfigError`` (a floor-binding must not turn a tolerated/odd-shaped
      LLM outline into a run halt); it behaves like the no-floor path.

Hermetic: a recording fake handle, no real model call.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from types import SimpleNamespace

from app.models.state.cache_state import CacheState
from app.models.state.run_state import RunState
from app.specialists.irene.graph import _act_pass_1


@dataclass
class _RecordingChat:
    response_text: str
    calls: list[list[dict[str, str]]] = field(default_factory=list)

    def invoke(self, messages: list[dict[str, str]]) -> SimpleNamespace:
        self.calls.append(messages)
        return SimpleNamespace(content=self.response_text, usage_metadata=None)


@dataclass
class _RecordingHandle:
    response_text: str
    chat: _RecordingChat = field(init=False)

    def __post_init__(self) -> None:
        self.chat = _RecordingChat(self.response_text)


def _state() -> RunState:
    return RunState(
        graph_version="v0.1-stub",
        temperature=0.0,
        cache_state=CacheState(cache_prefix="{}", entries_count=0),
    )


def _user_content(handle: _RecordingHandle) -> str:
    messages = handle.chat.calls[-1]
    user = [m for m in messages if m["role"] == "user"][-1]
    return user["content"]


# ------------------------------------------------------------------------- P1
def test_min_cluster_floor_absent_from_llm_visible_payload() -> None:
    outline = [
        {"cluster_intent": "c0", "source_points": [{"kind": "content", "text": "a"}]},
        {"cluster_intent": "c1", "source_points": [{"kind": "content", "text": "b"}]},
    ]
    response = json.dumps(
        {"learning_objectives": [], "structural_outline": outline, "cluster_intent": ""}
    )
    handle = _RecordingHandle(response)
    _act_pass_1(
        _state(),
        handle=handle,
        envelope_payload={"pass_phase": "pass-1", "topic": "cells", "min_cluster_floor": 2},
        model_id="gpt-5",
    )
    assert "min_cluster_floor" not in _user_content(handle)


def test_llm_payload_byte_identical_with_and_without_floor() -> None:
    outline = [
        {"cluster_intent": "c0", "source_points": [{"kind": "content", "text": "a"}]},
        {"cluster_intent": "c1", "source_points": [{"kind": "content", "text": "b"}]},
    ]
    response = json.dumps(
        {"learning_objectives": [], "structural_outline": outline, "cluster_intent": ""}
    )
    base = {"pass_phase": "pass-1", "topic": "cells"}

    h_no = _RecordingHandle(response)
    _act_pass_1(_state(), handle=h_no, envelope_payload=dict(base), model_id="gpt-5")

    h_floor = _RecordingHandle(response)
    # floor 2 == emitted count -> honoring is a no-op (no raise); the ONLY difference
    # from the control is the (stripped) floor key, which must not perturb the input.
    _act_pass_1(
        _state(),
        handle=h_floor,
        envelope_payload={**base, "min_cluster_floor": 2},
        model_id="gpt-5",
    )
    assert _user_content(h_no) == _user_content(h_floor)


# ------------------------------------------------------------------------- P2
def test_non_list_outline_with_bound_floor_does_not_raise_dead_config() -> None:
    response = json.dumps(
        {"learning_objectives": [], "structural_outline": "not-a-list", "cluster_intent": ""}
    )
    handle = _RecordingHandle(response)
    # Must NOT raise DeadFloorConfigError just because a floor is bound.
    update = _act_pass_1(
        _state(),
        handle=handle,
        envelope_payload={"pass_phase": "pass-1", "min_cluster_floor": 3},
        model_id="gpt-5",
    )
    out = json.loads(update["cache_state"]["cache_prefix"])
    # behaves like the no-floor path: the (non-list) outline is passed through unchanged
    assert out["irene_lesson_design"]["structural_outline"] == "not-a-list"


def test_non_list_outline_no_floor_still_quiet() -> None:
    """Control for P2: the no-floor path on a non-list outline is already quiet."""
    response = json.dumps(
        {"learning_objectives": [], "structural_outline": "not-a-list", "cluster_intent": ""}
    )
    handle = _RecordingHandle(response)
    update = _act_pass_1(
        _state(),
        handle=handle,
        envelope_payload={"pass_phase": "pass-1"},
        model_id="gpt-5",
    )
    out = json.loads(update["cache_state"]["cache_prefix"])
    assert out["irene_lesson_design"]["structural_outline"] == "not-a-list"
