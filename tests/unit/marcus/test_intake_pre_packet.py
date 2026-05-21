from __future__ import annotations

from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.marcus.intake import PrePacketSnapshot, extract_pre_packet


def test_pre_packet_snapshot_shape_strict() -> None:
    snapshot = PrePacketSnapshot.model_validate(
        {
            "run_id": "run-001",
            "source_ref": "source-001",
            "operator_prompt": "build it",
            "normalized_payload": {"mode": "test"},
        }
    )

    assert snapshot.run_id == "run-001"
    with pytest.raises(ValidationError):
        PrePacketSnapshot.model_validate(
            {
                "run_id": "run-001",
                "source_ref": "source-001",
                "operator_prompt": "build it",
                "normalized_payload": {},
                "extra_field": True,
            }
        )


def test_intake_appends_one_event_via_write_api(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, object]] = []

    def _spy(state: object, event: dict[str, object]) -> dict[str, object]:
        calls.append(event)
        state.events.append(event)
        return event

    monkeypatch.setattr("app.marcus.intake.append_event", _spy)
    state = SimpleNamespace(
        run_id="run-001",
        input_bundle={"source_ref": "src-1", "operator_prompt": "prompt"},
        events=[],
    )

    snapshot = extract_pre_packet(state)

    assert snapshot.source_ref == "src-1"
    assert len(calls) == 1
    assert len(state.events) == 1
    assert state.events[0]["event_type"] == "pre_packet_snapshot"
