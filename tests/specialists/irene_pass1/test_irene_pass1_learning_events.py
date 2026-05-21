from __future__ import annotations

from app.specialists.irene_pass1._act import build_learning_events


def test_scope_decision_and_plan_locked_events_shape() -> None:
    locked_scope = {"locked": True, "plan_units": [{"unit_id": "unit-1"}]}
    events = build_learning_events(run_id="run-123", locked_scope=locked_scope)

    assert [event["event_type"] for event in events] == [
        "scope_decision.set",
        "plan.locked",
    ]
    for event in events:
        assert event["run_id"] == "run-123"
        assert event["gate"] == "G1A"
        assert event["timestamp"].endswith("+00:00")
        assert event["payload"]
