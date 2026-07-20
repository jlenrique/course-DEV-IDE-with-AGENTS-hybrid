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
    RUN_SETTINGS_TOGGLES,
    EnvelopeSection,
    EventClass,
    IdentitySection,
    NotificationsEchoSection,
    OperatorSurfaceProjection,
    OperatorSurfaceStatus,
    QualitySection,
    RunSettingsSection,
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
# Story 42.3 — run-settings standing readout: shape + keep-in-sync guard (AC-5)
# ---------------------------------------------------------------------------

_SIXTEEN_TOGGLE_FIELDS = {
    "component_deck",
    "component_motion",
    "component_workbook",
    "preset",
    "encounter_mode",
    "llm_execution_mode",
    "g0_dispatch_live",
    "research_dispatch_live",
    "research_detective_live",
    "narration_figure_fidelity_active",
    "voice_direction",
    "deck_enrichment_active",
    "udac_active",
    "coverage_gate",
    "trial_budget_usd",
    "treatment_slots",
}


def test_run_settings_section_is_in_schema_defs() -> None:
    schema = OperatorSurfaceProjection.model_json_schema()
    assert "RunSettingsSection" in schema["$defs"]
    assert "run_settings" in schema["properties"]
    assert schema["$defs"]["RunSettingsSection"]["additionalProperties"] is False


def test_run_settings_carries_exactly_the_sixteen_toggles() -> None:
    """AC-1: the section carries all 16 run-defining toggles (+ the as_of stamp)."""
    fields = set(RunSettingsSection.model_fields) - {"as_of"}
    assert fields == _SIXTEEN_TOGGLE_FIELDS
    assert len(fields) == 16


def test_keep_in_sync_canonical_list_pins_the_sixteen_toggles() -> None:
    """AC-5 keep-in-sync guard: the canonical (field, label) list and the model
    share ONE source of truth, so a future knob that isn't added to BOTH the
    readout model and the canonical list fails loudly here."""
    canonical_fields = [field for field, _label in RUN_SETTINGS_TOGGLES]
    assert len(canonical_fields) == 16
    assert len(set(canonical_fields)) == 16, "duplicate toggle field in the canonical list"
    assert set(canonical_fields) == (set(RunSettingsSection.model_fields) - {"as_of"}), (
        "RUN_SETTINGS_TOGGLES drifted from RunSettingsSection — a new knob must be "
        "added to BOTH the canonical list and the readout model in lockstep"
    )
    # every canonical label is a non-empty operator-facing string
    for _field, label in RUN_SETTINGS_TOGGLES:
        assert isinstance(label, str) and label.strip()


def test_run_settings_fields_are_required_never_missing_key() -> None:
    """AC-3: env-absent toggles render an explicit resolved default, never a
    missing key — so every field is REQUIRED on the strict producer model."""
    with pytest.raises(ValidationError):
        RunSettingsSection(as_of=_BASE_TIME)  # no toggles → strict model rejects


# ---------------------------------------------------------------------------
# Story Q4.1 — quality tile: shape + additive-within-v1 pins (AC1/AC5)
# ---------------------------------------------------------------------------

_QUALITY_SUBSTANTIVE_FIELDS = {
    "available",
    "band",
    "ranked_leak_count",
    "top_leaks",
    "coverage_gaps",
    "trend",
    # FIX 2 — the COMMITTED scorecard doc date (staleness signal), additive-within-v1.
    "scorecard_as_of",
}


def test_quality_section_is_in_schema_defs() -> None:
    schema = OperatorSurfaceProjection.model_json_schema()
    assert "QualitySection" in schema["$defs"]
    assert "quality" in schema["properties"]
    assert schema["$defs"]["QualitySection"]["additionalProperties"] is False


def test_quality_section_carries_exactly_the_tile_fields_plus_as_of() -> None:
    """AC1 (QLW-7): ONLY the six substantive fields (NO /100 score) + the read-stamp."""
    fields = set(QualitySection.model_fields)
    assert fields == _QUALITY_SUBSTANTIVE_FIELDS | {"as_of"}
    # NO /100 numeric score anywhere on the tile (report.py's no-false-precise design).
    assert "score" not in fields
    assert "max" not in fields


def test_quality_section_field_types_are_none_able_scalars() -> None:
    """AC1: band/ranked_leak_count/coverage_gaps/trend are None-able; top_leaks -> []."""
    section = QualitySection(as_of=_BASE_TIME)
    assert section.available is False
    assert section.band is None
    assert section.ranked_leak_count is None
    assert section.coverage_gaps is None
    assert section.trend is None
    assert section.top_leaks == []


def test_quality_unavailable_posture_must_be_fully_null_structural() -> None:
    """FIX 3: the zero-lie invariant is STRUCTURAL — an ``available=False`` tile
    MUST carry a null posture (no band, no counts, no trend, no scorecard_as_of,
    empty top_leaks). Any substantive value alongside ``available=False`` RAISES."""
    for kwargs in (
        {"available": False, "band": "A"},
        {"available": False, "ranked_leak_count": 3},
        {"available": False, "coverage_gaps": 1},
        {"available": False, "trend": "rising"},
        {"available": False, "scorecard_as_of": "2026-07-19"},
        {"available": False, "top_leaks": ["paid-walk · x · Dim"]},
    ):
        with pytest.raises(ValidationError):
            QualitySection(as_of=_BASE_TIME, **kwargs)


def test_quality_available_tile_must_carry_a_band_structural() -> None:
    """FIX 3: an ``available=True`` tile with no band is a self-contradiction and
    RAISES (the assembler must never build one)."""
    with pytest.raises(ValidationError):
        QualitySection(as_of=_BASE_TIME, available=True, band=None)


def test_quality_unavailable_default_posture_validates_clean() -> None:
    """FIX 3: the honest fail-soft posture (available=False + all defaults) is legal."""
    section = QualitySection(as_of=_BASE_TIME, available=False)
    assert section.available is False
    assert section.band is None


def test_quality_defaults_to_none_on_projection_additive_within_v1() -> None:
    """AC5: the section is OPTIONAL — every existing status builds with it absent."""
    proj = OperatorSurfaceProjection(**_registered_kwargs())
    assert proj.quality is None
    # it is NOT in the schema's root required list (unknown == None).
    schema = OperatorSurfaceProjection.model_json_schema()
    assert "quality" not in set(schema.get("required", []))


def test_operator_surface_model_imports_nothing_from_app_quality() -> None:
    """AC1/AC5 layer rule: operator_surface.py (the contract layer) imports NOTHING
    from app.quality — QualitySection is a fresh typed mirror of plain scalars, and
    app.quality is reached ONLY by the assembler's deferred import."""
    import ast as _ast

    import app.models.runtime.operator_surface as osm

    tree = _ast.parse(Path(osm.__file__).read_text(encoding="utf-8"))
    for node in _ast.walk(tree):
        if isinstance(node, _ast.ImportFrom):
            assert not (node.module or "").startswith("app.quality"), (
                f"operator_surface.py must not import from app.quality (line {node.lineno})"
            )
        if isinstance(node, _ast.Import):
            for alias in node.names:
                assert not alias.name.startswith("app.quality"), (
                    f"operator_surface.py must not import app.quality (line {node.lineno})"
                )


def test_quality_section_populated_round_trips() -> None:
    proj = OperatorSurfaceProjection(**_registered_kwargs())
    updated = proj.model_copy(
        update={
            "quality": QualitySection(
                as_of=_BASE_TIME,
                available=True,
                band="D",
                ranked_leak_count=5,
                top_leaks=["paid-walk · slug-x · Dim"],
                coverage_gaps=0,
                trend="baseline",
            )
        }
    )
    dumped = updated.model_dump(mode="json")
    restored = OperatorSurfaceProjection.model_validate(dumped)
    assert restored.quality is not None
    assert restored.quality.band == "D"
    assert restored.quality.ranked_leak_count == 5
    assert restored.model_dump(mode="json") == dumped


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
