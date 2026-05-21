"""AC-T.4a — Generic event-envelope shape-pin (R2 rider W-1).

The envelope is the common contract every event in 31-2's append-only log
conforms to. This pin asserts it is exactly five fields (event_id /
timestamp / plan_revision / event_type / payload) so downstream emitters
cannot silently add envelope-level fields.
"""

from __future__ import annotations

from datetime import UTC, datetime

from app.marcus.lesson_plan.events import EventEnvelope

EXPECTED_ENVELOPE_FIELDS = {
    "event_id",
    "timestamp",
    "plan_revision",
    "event_type",
    "payload",
}


def test_event_envelope_shape_is_frozen_at_five_fields() -> None:
    actual = set(EventEnvelope.model_fields.keys())
    assert actual == EXPECTED_ENVELOPE_FIELDS, (
        f"EventEnvelope drift. Missing: {EXPECTED_ENVELOPE_FIELDS - actual}. "
        f"New: {actual - EXPECTED_ENVELOPE_FIELDS}. Any envelope change breaks "
        f"31-2 emission, all downstream event types, and 30-4 fanout audit."
    )


def test_event_envelope_roundtrips_through_json() -> None:
    now = datetime.now(tz=UTC)
    env = EventEnvelope(
        timestamp=now,
        plan_revision=3,
        event_type="plan_unit.created",
        payload={"unit_id": "gagne-event-1"},
    )
    # Default serialization keeps all five fields.
    dumped = env.model_dump()
    assert set(dumped.keys()) == EXPECTED_ENVELOPE_FIELDS


def test_event_id_is_auto_generated_uuid4() -> None:
    env = EventEnvelope(
        timestamp=datetime.now(tz=UTC),
        plan_revision=0,
        event_type="plan.locked",
    )
    # UUID4 canonical string form is 36 chars with four hyphens.
    assert env.event_id.count("-") == 4
    assert len(env.event_id) == 36
