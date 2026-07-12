"""Shape pins for the Story 35.1 operator-surface projection contract (AD-4a).

Mirrors the decision-card byte-pin pattern: the emitted JSON Schema must be
byte-identical to the committed ``operator-surface.v1.schema.json``, plus
structural asserts (``additionalProperties: false`` everywhere, the seven
verbatim status literals) and strict-model rejection behavior.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import get_args
from uuid import UUID

import pytest
from pydantic import ValidationError

from app.models.runtime.operator_surface import (
    HUD_CONFIG_DEFAULTS,
    EnvelopeSection,
    EventClass,
    IdentitySection,
    NotificationsEchoSection,
    OperatorSurfaceProjection,
    OperatorSurfaceStatus,
    operator_surface_schema_text,
)

_SCHEMA_PATH = (
    Path(__file__).resolve().parents[3]
    / "app"
    / "models"
    / "schemas"
    / "operator-surface.v1.schema.json"
)

_BASE_TIME = datetime(2026, 7, 11, 12, 0, 0, tzinfo=UTC)
_TRIAL_ID = UUID("12345678-1234-4321-8765-123456789abc")

_SEVEN_STATUSES = {
    "registered",
    "in-flight",
    "paused-at-gate",
    "paused-at-error",
    "waiting_for_provider_batch",
    "completed",
    "failed",
}


def _registered_kwargs() -> dict:
    return {
        "seq": 1,
        "progress_seq": 1,
        "last_progress_at": _BASE_TIME,
        "envelope_digest": "sha256:0000",
        "as_of": _BASE_TIME,
        "identity": IdentitySection(
            as_of=_BASE_TIME,
            trial_id=_TRIAL_ID,
            lesson="tejal-part-3",
            preset="production",
            operator_id="juan",
        ),
        "envelope": EnvelopeSection(as_of=_BASE_TIME, status="registered"),
        "notifications_echo": NotificationsEchoSection(
            as_of=_BASE_TIME,
            config=HUD_CONFIG_DEFAULTS,
            parse_status="ok",
        ),
    }


# ---------------------------------------------------------------------------
# AD-4a — byte-identical committed schema pin
# ---------------------------------------------------------------------------


def test_emitted_json_schema_is_byte_identical_to_tree_fixture() -> None:
    assert operator_surface_schema_text() == _SCHEMA_PATH.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Structural asserts
# ---------------------------------------------------------------------------


def test_schema_root_and_all_defs_forbid_additional_properties() -> None:
    schema = OperatorSurfaceProjection.model_json_schema()
    assert schema["additionalProperties"] is False
    for def_name, def_schema in (schema.get("$defs") or {}).items():
        assert def_schema.get("additionalProperties") is False, (
            f"$defs.{def_name} does not carry additionalProperties: false — "
            "extra='forbid' missing on that model"
        )


def test_schema_status_enum_membership_is_the_seven_verbatim_literals() -> None:
    schema = OperatorSurfaceProjection.model_json_schema()
    status_enum = set(schema["$defs"]["EnvelopeSection"]["properties"]["status"]["enum"])
    assert status_enum == _SEVEN_STATUSES


def test_status_literal_carries_the_seven_verbatim_values() -> None:
    assert set(get_args(OperatorSurfaceStatus)) == _SEVEN_STATUSES


def test_schema_version_literal_is_v1() -> None:
    schema = OperatorSurfaceProjection.model_json_schema()
    assert schema["properties"]["schema_version"]["const"] == "v1"


def test_hud_config_schema_pins_the_five_event_classes() -> None:
    """AD-19 schema-pin rides alongside AD-4's: the notification matrix keys."""
    schema = OperatorSurfaceProjection.model_json_schema()
    notif = schema["$defs"]["HudConfig"]["properties"]["notifications"]
    assert set(notif["propertyNames"]["enum"]) == set(get_args(EventClass))


def test_preflight_state_enum_distinguishes_missed_from_fail() -> None:
    schema = OperatorSurfaceProjection.model_json_schema()
    states = set(schema["$defs"]["PreflightItem"]["properties"]["state"]["enum"])
    assert "missed" in states
    assert "fail" in states


def test_quota_confidence_enum_is_direct_proxy_unknown() -> None:
    schema = OperatorSurfaceProjection.model_json_schema()
    conf = set(schema["$defs"]["PreflightItem"]["properties"]["quota_confidence"]["enum"])
    assert conf == {"direct", "proxy", "unknown"}


# ---------------------------------------------------------------------------
# Strict-model behavior
# ---------------------------------------------------------------------------


def test_registered_projection_constructs() -> None:
    projection = OperatorSurfaceProjection(**_registered_kwargs())
    assert projection.schema_version == "v1"
    assert projection.envelope.status == "registered"
    assert projection.steps is None
    assert projection.health is None


def test_extra_field_raises_validation_error() -> None:
    with pytest.raises(ValidationError):
        OperatorSurfaceProjection(**_registered_kwargs(), fleet_view={"future": True})


def test_unknown_status_raises_validation_error_on_strict_model() -> None:
    with pytest.raises(ValidationError):
        EnvelopeSection(as_of=_BASE_TIME, status="hyperspace")


def test_naive_datetime_raises_validation_error() -> None:
    kwargs = _registered_kwargs()
    kwargs["as_of"] = datetime(2026, 7, 11, 12, 0, 0)  # noqa: DTZ001 — naive on purpose
    with pytest.raises(ValidationError):
        OperatorSurfaceProjection(**kwargs)


def test_non_uuid4_trial_id_raises_validation_error() -> None:
    with pytest.raises(ValidationError):
        IdentitySection(
            as_of=_BASE_TIME,
            trial_id=UUID("12345678-1234-1321-8765-123456789abc"),  # version 1
            lesson="tejal-part-3",
            preset="production",
            operator_id="juan",
        )


# ---------------------------------------------------------------------------
# Lifecycle invariants: witness by default, strict via validation context
# ---------------------------------------------------------------------------


def _in_flight_payload_missing_sections() -> dict:
    projection = OperatorSurfaceProjection(**_registered_kwargs())
    payload = projection.model_dump(mode="json")
    payload["envelope"]["status"] = "in-flight"
    return payload


def test_lifecycle_violation_is_witnessed_not_gated_by_default() -> None:
    projection = OperatorSurfaceProjection.model_validate(_in_flight_payload_missing_sections())
    assert projection.envelope.status == "in-flight"
    assert projection.steps is None  # witnessed, not coerced


def test_lifecycle_violation_raises_under_strict_context() -> None:
    with pytest.raises(ValidationError, match="lifecycle invariant"):
        OperatorSurfaceProjection.model_validate(
            _in_flight_payload_missing_sections(),
            context={"invariant_mode": "strict"},
        )
