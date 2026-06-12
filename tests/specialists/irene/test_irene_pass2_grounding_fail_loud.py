"""PIN-G2 — Pass 2 refuses to dispatch on hollow grounding (dp-v1.1, 2026-06-12).

Red twins of Trial-3 cycle-4 defect 1: node 08 received ``input keys:
cache_prefix`` only and Irene authored a sepsis narration from her L5
exemplars with ``provenance: real``. The "payload empty, proceed anyway"
branch must not exist: every missing grounding input raises a typed
SpecialistDispatchError BEFORE the chat model is invoked, and a parsed
response that does not join the real slide roster raises after.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.dispatch_errors import SpecialistDispatchError
from app.specialists.irene.graph import Pass2GroundingError, _act
from app.specialists.source_bundle import SourceBundleError
from tests.specialists.irene.conftest import make_grounded_pass2_payload


class _RefusingChat:
    """A chat handle that fails the test if Pass 2 dispatches ungrounded."""

    def invoke(self, messages: Any) -> Any:
        raise AssertionError(
            "chat model invoked despite missing grounding — the "
            "proceed-anyway branch is the cycle-4 defect"
        )


def _entry() -> ModelResolutionEntry:
    return ModelResolutionEntry(
        level="registry_default",
        requested=None,
        resolved="gpt-5",
        reason="test",
        timestamp=datetime.now(UTC),
        cache_prefix_hash="a" * 64,
    )


def _state(payload: dict[str, Any]) -> RunState:
    return RunState(
        graph_version="v0.1-stub",
        temperature=0.0,
        cache_state=CacheState(
            cache_prefix=json.dumps(payload, sort_keys=True), entries_count=0
        ),
        model_resolution_trail=[_entry()],
    )


def _patch_refusing_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "app.specialists.irene.graph.make_chat_model",
        lambda *a, **k: SimpleNamespace(chat=_RefusingChat(), entry=_entry()),
    )


def test_empty_payload_raises_before_dispatch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_refusing_model(monkeypatch)
    with pytest.raises(SourceBundleError):
        _act(_state({}))


def test_missing_roster_raises_before_dispatch(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _patch_refusing_model(monkeypatch)
    payload = make_grounded_pass2_payload(tmp_path)
    del payload["gary_slide_output"]
    with pytest.raises(Pass2GroundingError) as excinfo:
        _act(_state(payload))
    assert excinfo.value.tag == "irene.pass2.grounding-missing"


def test_missing_lesson_plan_raises_before_dispatch(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _patch_refusing_model(monkeypatch)
    payload = make_grounded_pass2_payload(tmp_path)
    del payload["lesson_plan"]
    with pytest.raises(Pass2GroundingError) as excinfo:
        _act(_state(payload))
    assert excinfo.value.tag == "irene.pass2.grounding-missing"


def test_grounding_errors_are_recoverable_dispatch_family() -> None:
    # The runner converts SpecialistDispatchError to error-pause + recover;
    # grounding failures must ride that family, not crash the cycle.
    assert issubclass(Pass2GroundingError, SpecialistDispatchError)
    assert issubclass(SourceBundleError, SpecialistDispatchError)


def test_unjoined_narration_raises_after_parse(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Residual-confabulation kill: a response referencing slides outside the
    real roster (exemplar bleed despite grounding) fails loud."""
    response = SimpleNamespace(
        content=json.dumps(
            {
                "narration_script": [{"id": "seg-1", "narration_text": "Sepsis..."}],
                "segment_manifest_deltas": [
                    {
                        "id": "seg-1",
                        "visual_references": [
                            {"perception_source": "slide-clu-sepsis-01-1"}
                        ],
                    }
                ],
            }
        ),
        usage_metadata={"input_tokens": 10},
    )

    class _Chat:
        def invoke(self, messages: Any) -> Any:
            return response

    monkeypatch.setattr(
        "app.specialists.irene.graph.make_chat_model",
        lambda *a, **k: SimpleNamespace(chat=_Chat(), entry=_entry()),
    )
    with pytest.raises(Pass2GroundingError) as excinfo:
        _act(_state(make_grounded_pass2_payload(tmp_path)))
    assert excinfo.value.tag == "irene.pass2.slide-join-failed"
