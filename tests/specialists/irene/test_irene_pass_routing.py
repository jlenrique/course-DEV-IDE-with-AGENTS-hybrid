from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any

from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.irene.graph import _act


@dataclass
class _FakeChat:
    response_text: str

    def invoke(self, messages: list[dict[str, str]]) -> SimpleNamespace:
        del messages
        return SimpleNamespace(content=self.response_text, usage_metadata={"input_tokens": 42})


@dataclass
class _FakeHandle:
    response_text: str

    @property
    def entry(self) -> ModelResolutionEntry:
        return ModelResolutionEntry(
            level="registry_default",
            requested=None,
            resolved="gpt-5",
            reason="test",
            timestamp=datetime.now(UTC),
            cache_prefix_hash="a" * 64,
        )

    @property
    def chat(self) -> _FakeChat:
        return _FakeChat(response_text=self.response_text)


def _state(payload: dict[str, Any]) -> RunState:
    return RunState(
        graph_version="v0.1-stub",
        temperature=0.0,
        cache_state=CacheState(
            cache_prefix=json.dumps(payload, sort_keys=True),
            entries_count=0,
        ),
        model_resolution_trail=[
            ModelResolutionEntry(
                level="registry_default",
                requested=None,
                resolved="gpt-5",
                reason="test",
                timestamp=datetime.now(UTC),
                cache_prefix_hash="a" * 64,
            )
        ],
    )


def test_irene_pass_1_dispatch_branch(monkeypatch: Any) -> None:
    def _fake_model(*args: Any, **kwargs: Any) -> _FakeHandle:
        del args, kwargs
        return _FakeHandle(
            response_text=json.dumps(
                {
                    "learning_objectives": ["obj-1"],
                    "structural_outline": [{"section": "intro"}],
                    "cluster_intent": "teach core concept",
                }
            )
        )

    monkeypatch.setattr("app.specialists.irene.graph.make_chat_model", _fake_model)
    update = _act(_state({"pass_phase": "pass-1", "topic": "cells"}))
    output = json.loads(update["cache_state"]["cache_prefix"])
    assert "irene_lesson_design" in output
    assert output["irene_lesson_design"]["learning_objectives"] == ["obj-1"]
    assert output["irene_pass_2_envelope"] is None


def test_irene_pass_1_honors_min_cluster_floor_from_envelope(monkeypatch: Any) -> None:
    """AC#3 arrival + Task-2 integration: a min_cluster_floor threaded into the
    envelope payload is consumed at Pass-1 and subdivides the emitted clustering."""
    # Members carry role tags so the split is role-VERIFIABLE (P5 fail-safe: a
    # role-less cluster refuses to split blind rather than risk severing a figure
    # from its narration).
    outline = [
        {
            "cluster_intent": "c0",
            "source_points": [{"kind": "content", "text": "a"}, {"kind": "content", "text": "b"}],
        },
        {
            "cluster_intent": "c1",
            "source_points": [{"kind": "content", "text": "c"}, {"kind": "content", "text": "d"}],
        },
    ]

    def _fake_model(*args: Any, **kwargs: Any) -> _FakeHandle:
        del args, kwargs
        return _FakeHandle(
            response_text=json.dumps(
                {
                    "learning_objectives": ["obj-1"],
                    "structural_outline": outline,
                    "cluster_intent": "walk",
                }
            )
        )

    monkeypatch.setattr("app.specialists.irene.graph.make_chat_model", _fake_model)
    update = _act(_state({"pass_phase": "pass-1", "min_cluster_floor": 3}))
    output = json.loads(update["cache_state"]["cache_prefix"])
    honored = output["irene_lesson_design"]["structural_outline"]
    assert len(honored) >= 3
    # split-only byte-identity: the flattened member text is unchanged
    flat = [m["text"] for cluster in honored for m in cluster.get("source_points", [])]
    assert flat == ["a", "b", "c", "d"]


def test_irene_pass_1_without_floor_is_unchanged(monkeypatch: Any) -> None:
    """No floor bound -> the clustering is passed through verbatim (quiet)."""
    outline = [{"section": "intro"}, {"section": "body"}]

    def _fake_model(*args: Any, **kwargs: Any) -> _FakeHandle:
        del args, kwargs
        return _FakeHandle(
            response_text=json.dumps(
                {
                    "learning_objectives": [],
                    "structural_outline": outline,
                    "cluster_intent": "",
                }
            )
        )

    monkeypatch.setattr("app.specialists.irene.graph.make_chat_model", _fake_model)
    update = _act(_state({"pass_phase": "pass-1", "topic": "cells"}))
    output = json.loads(update["cache_state"]["cache_prefix"])
    assert output["irene_lesson_design"]["structural_outline"] == outline


def test_irene_pass_2_default_branch_stays_intact(monkeypatch: Any, tmp_path: Any) -> None:
    from tests.specialists.irene.conftest import (
        joined_pass2_response,
        make_grounded_pass2_payload,
    )

    response = joined_pass2_response()

    def _fake_model(*args: Any, **kwargs: Any) -> _FakeHandle:
        del args, kwargs
        return _FakeHandle(response_text=json.dumps(response))

    monkeypatch.setattr("app.specialists.irene.graph.make_chat_model", _fake_model)
    update = _act(_state(make_grounded_pass2_payload(tmp_path, topic="cells")))
    output = json.loads(update["cache_state"]["cache_prefix"])
    assert output["narration_script"] == response["narration_script"]
    assert output["segment_manifest_deltas"] == response["segment_manifest_deltas"]

