"""Story 35.1 producer<->consumer parity + contract behavior (AD-4b/5/16/18/19).

Lesson-plan-parity pattern: field presence, enum parity (including the AD-5 L1
set-equality against ``ProductionTrialStatus``), round-trip, bidirectional
required/optional. Plus the 35.1 behavior set: lenient-reader fixtures,
``derive_event_transitions`` goldens (five classes incl. resume-that-repauses
and recover-reenter), ring-buffer caps, the 256KB size tripwire, and the
``HudConfig`` loader.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import get_args
from uuid import UUID

import pytest
from pydantic import BaseModel

from app.models.runtime.operator_surface import (
    EVENT_CLASSES,
    HEALTH_HISTORY_CAP,
    HUD_CONFIG_DEFAULTS,
    PROJECTION_SIZE_LIMIT_BYTES,
    PROJECTION_SIZE_TARGET_BYTES,
    TRACE_RING_CAP,
    DecisionCardSection,
    DeliverableComponents,
    DeliverablesSection,
    DraftedProposal,
    EnvelopeSection,
    ErrorMessageSection,
    EventClass,
    HealthReading,
    HealthSection,
    HealthTile,
    HudConfig,
    IdentitySection,
    ModalitiesSection,
    NextActionSection,
    NotificationRule,
    NotificationsEchoSection,
    OperatorSurfaceProjection,
    OperatorSurfaceStatus,
    PreflightItem,
    PreflightSection,
    RunSettingsSection,
    SpecialistEntry,
    SpecialistsSection,
    StepEntry,
    StepsSection,
    TraceEvent,
    TraceSection,
    Unrecognized,
    derive_event_transitions,
    load_hud_config,
    read_operator_surface_lenient,
    stall_condition,
)
from app.models.runtime.production_trial_envelope import ProductionTrialStatus

SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "app"
    / "models"
    / "schemas"
    / "operator-surface.v1.schema.json"
)

BASE_TIME = datetime(2026, 7, 11, 12, 0, 0, tzinfo=UTC)
TRIAL_ID = UUID("12345678-1234-4321-8765-123456789abc")

_PAUSE_CLASS_OF_STATUS = {
    "paused-at-gate": "paused-at-gate",
    "paused-at-error": "paused-at-error",
    "waiting_for_provider_batch": "waiting_for_provider_batch",
}


def _load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Fixture builders (contract-local)
# ---------------------------------------------------------------------------


def _identity() -> IdentitySection:
    return IdentitySection(
        as_of=BASE_TIME,
        trial_id=TRIAL_ID,
        lesson="tejal-part-3",
        preset="production",
        operator_id="juan",
    )


def _echo() -> NotificationsEchoSection:
    return NotificationsEchoSection(
        as_of=BASE_TIME, config=HUD_CONFIG_DEFAULTS, parse_status="ok"
    )


def _steps(walk_index: int = 3) -> StepsSection:
    return StepsSection(
        as_of=BASE_TIME,
        manifest_digest="sha256:manifest",
        node_count=42,
        walk_index=walk_index,
        entries=[
            StepEntry(
                step_id="04.5",
                label="Clustering poll",
                stage="stage-1",
                status="active",
                conditions=["irene-pass-1 complete"],
                blockers=[],
                locked_artifact_summary=None,
            ),
        ],
    )


def _run_settings() -> RunSettingsSection:
    return RunSettingsSection(
        as_of=BASE_TIME,
        component_deck="on",
        component_motion="off",
        component_workbook="on",
        preset="production",
        encounter_mode="recorded",
        llm_execution_mode="batch",
        g0_dispatch_live="on",
        research_dispatch_live="off",
        research_detective_live="off",
        narration_figure_fidelity_active="off",
        voice_direction="on",
        deck_enrichment_active="off",
        udac_active="off",
        coverage_gate="standard",
        trial_budget_usd="10.00",
        treatment_slots="hil-2026-apc-crossroads-classic",
    )


def _health(threshold_state: str = "nominal") -> HealthSection:
    return HealthSection(
        as_of=BASE_TIME,
        tiles=[
            HealthTile(
                as_of=BASE_TIME,
                label="openai-credit",
                value=123.45,
                unit="USD",
                confidence="direct",
                threshold_state=threshold_state,
                history=[HealthReading(at=BASE_TIME, value=123.45)],
            ),
        ],
    )


def build_projection(
    status: str = "in-flight",
    *,
    seq: int = 10,
    progress_seq: int = 7,
    last_progress_at: datetime = BASE_TIME,
    health: HealthSection | None = None,
    trace: TraceSection | None = None,
) -> OperatorSurfaceProjection:
    envelope_kwargs: dict = {"as_of": BASE_TIME, "status": status}
    next_action = None
    if status == "paused-at-gate":
        envelope_kwargs["paused_gate"] = "G1"
        next_action = NextActionSection(
            as_of=BASE_TIME,
            command="trial resume --trial-id 12345678 --gate G1",
            pause_class="paused-at-gate",
        )
    elif status == "paused-at-error":
        envelope_kwargs["paused_error_tag"] = "specialist-dispatch-error"
        next_action = NextActionSection(
            as_of=BASE_TIME,
            command="trial recover --trial-id 12345678",
            pause_class="paused-at-error",
        )
    elif status == "waiting_for_provider_batch":
        envelope_kwargs["waiting_batch_id"] = "batch-abc123"
        next_action = NextActionSection(
            as_of=BASE_TIME,
            command="trial resume-batch --trial-id 12345678",
            pause_class="waiting_for_provider_batch",
        )
    elif status == "completed":
        envelope_kwargs["completed_at"] = BASE_TIME
    return OperatorSurfaceProjection(
        seq=seq,
        progress_seq=progress_seq,
        last_progress_at=last_progress_at,
        envelope_digest="sha256:envelope",
        as_of=BASE_TIME,
        identity=_identity(),
        envelope=EnvelopeSection(**envelope_kwargs),
        notifications_echo=_echo(),
        next_action=next_action,
        steps=None if status == "registered" else _steps(),
        preflight=PreflightSection(
            as_of=BASE_TIME,
            items=[
                PreflightItem(
                    name="openai-heartbeat",
                    state="pass",
                    output="200 OK",
                    latency_ms=412.0,
                    quota_reading="$123.45 remaining",
                    quota_confidence="direct",
                ),
                PreflightItem(name="gamma-heartbeat", state="missed"),
            ],
        ),
        health=health if health is not None else (None if status == "registered" else _health()),
        specialists=SpecialistsSection(
            as_of=BASE_TIME,
            roster=[
                SpecialistEntry(
                    name="irene",
                    status="working",
                    current_node="04.5",
                    model="gpt-5",
                    last_artifact="runs/x/irene-pass-1.json",
                    cost_usd=1.25,
                ),
            ],
        ),
        modalities=ModalitiesSection(
            as_of=BASE_TIME,
            llm_execution_mode="batch",
            detective_disposition="on",
            styleguide="hil-2026-apc-crossroads-classic",
            styleguide_provenance="style-control-map",
        ),
        run_settings=_run_settings(),
        trace=trace
        if trace is not None
        else TraceSection(
            as_of=BASE_TIME,
            events=[TraceEvent(at=BASE_TIME, event="node-started", detail="04.5")],
        ),
    )


# ---------------------------------------------------------------------------
# (a) field presence
# ---------------------------------------------------------------------------

_SECTION_DEFS: list[tuple[type[BaseModel], str]] = [
    (IdentitySection, "IdentitySection"),
    (EnvelopeSection, "EnvelopeSection"),
    (NextActionSection, "NextActionSection"),
    (StepsSection, "StepsSection"),
    (StepEntry, "StepEntry"),
    (PreflightSection, "PreflightSection"),
    (PreflightItem, "PreflightItem"),
    (HealthSection, "HealthSection"),
    (HealthTile, "HealthTile"),
    (HealthReading, "HealthReading"),
    (SpecialistsSection, "SpecialistsSection"),
    (SpecialistEntry, "SpecialistEntry"),
    (ModalitiesSection, "ModalitiesSection"),
    (RunSettingsSection, "RunSettingsSection"),
    (TraceSection, "TraceSection"),
    (TraceEvent, "TraceEvent"),
    (NotificationsEchoSection, "NotificationsEchoSection"),
    (HudConfig, "HudConfig"),
    (NotificationRule, "NotificationRule"),
    # Story 35.9 additive sections
    (DecisionCardSection, "DecisionCardSection"),
    (DraftedProposal, "DraftedProposal"),
    (ErrorMessageSection, "ErrorMessageSection"),
    (DeliverablesSection, "DeliverablesSection"),
    (DeliverableComponents, "DeliverableComponents"),
]


def test_projection_root_fields_present_in_schema() -> None:
    schema = _load_schema()
    root_props = set(schema["properties"].keys())
    pydantic_fields = set(OperatorSurfaceProjection.model_fields.keys())
    assert root_props == pydantic_fields, (
        f"OperatorSurfaceProjection JSON Schema / Pydantic field drift: "
        f"missing in schema={pydantic_fields - root_props}, "
        f"missing in model={root_props - pydantic_fields}"
    )


@pytest.mark.parametrize(("model_cls", "def_name"), _SECTION_DEFS)
def test_section_fields_present_in_schema(model_cls: type[BaseModel], def_name: str) -> None:
    schema = _load_schema()
    defs = schema.get("$defs") or {}
    assert def_name in defs, f"{def_name} missing from $defs: {sorted(defs.keys())}"
    def_props = set(defs[def_name].get("properties", {}).keys())
    pydantic_fields = set(model_cls.model_fields.keys())
    assert def_props == pydantic_fields, (
        f"{def_name}: missing in schema={pydantic_fields - def_props}, "
        f"missing in model={def_props - pydantic_fields}"
    )


# ---------------------------------------------------------------------------
# (b) enum parity — incl. the AD-5 L1 set-equality against the envelope
# ---------------------------------------------------------------------------


def test_status_set_equality_against_production_trial_status() -> None:
    """AD-5 L1: projection status vocabulary == ProductionTrialStatus, verbatim."""
    assert set(get_args(OperatorSurfaceStatus)) == set(get_args(ProductionTrialStatus)), (
        "Projection status vocabulary drifted from ProductionTrialStatus. "
        "The envelope vocabulary IS the status contract (AD-5); update the "
        "projection Literal verbatim and bump per additive-evolution rules."
    )


def test_schema_status_enum_matches_production_trial_status() -> None:
    schema = _load_schema()
    status_enum = set(schema["$defs"]["EnvelopeSection"]["properties"]["status"]["enum"])
    assert status_enum == set(get_args(ProductionTrialStatus))


def test_event_class_vocabulary_is_the_five_classes() -> None:
    assert set(get_args(EventClass)) == {
        "paused_at_gate",
        "paused_at_error",
        "batch_pause_resumed",
        "health_threshold",
        "run_stalled",
    }
    assert tuple(EVENT_CLASSES) == tuple(get_args(EventClass))


def test_pause_class_enum_parity() -> None:
    schema = _load_schema()
    pause_enum = set(
        schema["$defs"]["NextActionSection"]["properties"]["pause_class"]["enum"]
    )
    assert pause_enum == {"paused-at-gate", "paused-at-error", "waiting_for_provider_batch"}
    assert pause_enum <= set(get_args(ProductionTrialStatus))


# ---------------------------------------------------------------------------
# (c) round-trip
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "status",
    [
        "registered",
        "in-flight",
        "paused-at-gate",
        "paused-at-error",
        "waiting_for_provider_batch",
        "completed",
        "failed",
    ],
)
def test_model_dump_roundtrip_per_status(status: str) -> None:
    projection = build_projection(status)
    dumped = projection.model_dump(mode="json")
    restored = OperatorSurfaceProjection.model_validate(dumped)
    assert restored.envelope.status == status
    assert restored.identity.trial_id == TRIAL_ID
    assert restored.model_dump(mode="json") == dumped


def test_lenient_reader_roundtrip_from_producer_json() -> None:
    projection = build_projection("paused-at-gate")
    result = read_operator_surface_lenient(projection.model_dump_json())
    assert isinstance(result, OperatorSurfaceProjection)
    assert result.envelope.status == "paused-at-gate"
    assert result.next_action is not None
    assert result.next_action.command == projection.next_action.command


# ---------------------------------------------------------------------------
# Story 35.9 additive sections — all optional, verb-conditional, round-trip
# ---------------------------------------------------------------------------


def test_new_sections_default_to_none() -> None:
    """Additive within v1: every existing status builds with the trio absent."""
    for status in get_args(OperatorSurfaceStatus):
        proj = build_projection(status)
        assert proj.decision_card is None
        assert proj.error_message is None
        assert proj.deliverables is None


# ---------------------------------------------------------------------------
# Story 42.3 — run-settings standing readout: round-trip + back-compat (AC-6)
# ---------------------------------------------------------------------------


def test_run_settings_section_round_trips() -> None:
    proj = build_projection("in-flight")
    assert proj.run_settings is not None
    dumped = proj.model_dump(mode="json")
    restored = OperatorSurfaceProjection.model_validate(dumped)
    assert restored.run_settings is not None
    assert restored.run_settings.udac_active == "off"
    assert restored.run_settings.component_deck == "on"
    assert restored.model_dump(mode="json") == dumped


def test_run_settings_defaults_to_none_additive_within_v1() -> None:
    """The section is OPTIONAL — a run without it is a valid v1 projection."""
    proj = build_projection("in-flight")
    proj.run_settings = None
    assert proj.model_dump(mode="json")["run_settings"] is None


def test_back_compat_pre_42_3_modalities_only_surface_still_parses() -> None:
    """AC-6: a frozen pre-42.3 surface (old ``modalities`` slice, NO
    ``run_settings`` key) still parses through the lenient reader (additive,
    tolerant read) — schema_version stays 'v1', so it is never Unrecognized."""
    payload = build_projection("in-flight").model_dump(mode="json")
    del payload["run_settings"]  # a surface written before 42.3 landed
    result = read_operator_surface_lenient(payload)
    assert isinstance(result, OperatorSurfaceProjection)
    assert result.schema_version == "v1"
    assert result.run_settings is None
    # the old modalities slice is untouched
    assert result.modalities is not None
    assert result.modalities.llm_execution_mode == "batch"


def test_decision_card_section_all_inner_fields_optional() -> None:
    """G1 shape: drafted_proposal + confidence, NO operator_prompt."""
    card = DecisionCardSection(
        as_of=BASE_TIME,
        gate_focus="trial_open",
        drafted_proposal=DraftedProposal(
            decision="revise", confidence=0.72, rationale="minor taxonomy issues"
        ),
        evidence=["production-runner", "runs/x/texas.md"],
    )
    assert card.operator_prompt is None
    assert card.drafted_proposal.confidence == 0.72
    assert card.pick_context == []
    # G4A shape: gate_focus/operator_prompt/pick_context, NO drafted_proposal.
    voice_card = DecisionCardSection(
        as_of=BASE_TIME,
        gate_focus="voice_selection",
        operator_prompt="Approve the proposed voice, or edit to select an alternate.",
        pick_context=["production-runner", "Sarah", "Shannon"],
    )
    assert voice_card.drafted_proposal is None
    assert voice_card.evidence == []


def test_drafted_proposal_confidence_bounds() -> None:
    with pytest.raises(ValueError):
        DraftedProposal(confidence=1.5)
    with pytest.raises(ValueError):
        DraftedProposal(confidence=-0.1)


def test_error_message_and_deliverables_sections_roundtrip() -> None:
    proj = build_projection("completed")
    updated = proj.model_copy(
        update={
            "error_message": ErrorMessageSection(
                as_of=BASE_TIME,
                message="scope=narration; slide slide-05 narration figures not present",
                node_index=33,
                tag="irene.pass2.figure-contradiction",
            ),
            "deliverables": DeliverablesSection(
                as_of=BASE_TIME,
                components=DeliverableComponents(deck=True, motion=True, workbook=True),
                total_cost_usd=0.44444605,
                export_paths=["exports/gary-dispatch-payload.json", "exports/storyboard-A-pack"],
            ),
        }
    )
    dumped = updated.model_dump(mode="json")
    restored = OperatorSurfaceProjection.model_validate(dumped)
    assert restored.error_message.message.startswith("scope=narration")
    assert restored.error_message.node_index == 33
    assert restored.deliverables.components.workbook is True
    assert restored.deliverables.total_cost_usd == 0.44444605
    assert len(restored.deliverables.export_paths) == 2
    # lenient reader tolerates the widened document unchanged
    lenient = read_operator_surface_lenient(updated.model_dump_json())
    assert isinstance(lenient, OperatorSurfaceProjection)
    assert lenient.deliverables is not None


# ---------------------------------------------------------------------------
# (d) required-vs-optional bidirectional parity (lesson-plan AM-2 pattern)
# ---------------------------------------------------------------------------


def _pydantic_required_fields(model_cls: type[BaseModel]) -> set[str]:
    from pydantic_core import PydanticUndefined

    required: set[str] = set()
    for name, field in model_cls.model_fields.items():
        if field.default is PydanticUndefined and field.default_factory is None:
            required.add(name)
    return required


def _json_schema_required_for(schema: dict, model_name: str) -> set[str]:
    if schema.get("title") == model_name:
        return set(schema.get("required", []))
    defs = schema.get("$defs") or {}
    if model_name in defs:
        return set(defs[model_name].get("required", []))
    raise AssertionError(
        f"{model_name} not found in schema $defs; available defs: {sorted(defs.keys())}"
    )


@pytest.mark.parametrize(
    ("model_cls", "def_name"),
    [(OperatorSurfaceProjection, "OperatorSurfaceProjection"), *_SECTION_DEFS],
)
def test_required_optional_bidirectional_parity(
    model_cls: type[BaseModel], def_name: str
) -> None:
    schema = _load_schema()
    expected_required = _pydantic_required_fields(model_cls)
    actual_required = _json_schema_required_for(schema, def_name)
    missing = expected_required - actual_required
    extra = actual_required - expected_required
    assert not missing, f"{def_name}: required-in-Pydantic not required-in-JSON: {missing}"
    assert not extra, f"{def_name}: required-in-JSON not required-in-Pydantic: {extra}"


# ---------------------------------------------------------------------------
# Lenient-reader fixtures — never raises, typed Unrecognized (AD-4)
# ---------------------------------------------------------------------------


def test_lenient_reader_ignores_future_added_fields() -> None:
    payload = build_projection("in-flight").model_dump(mode="json")
    payload["fleet_view"] = {"runs": 3}  # future top-level addition
    payload["identity"]["future_hint"] = "v1.1 field"  # future nested addition
    payload["steps"]["entries"][0]["eta_seconds"] = 12  # future list-item addition
    payload["notifications_echo"]["config"]["future_channel"] = "sms"  # nested config addition
    result = read_operator_surface_lenient(payload)
    assert isinstance(result, OperatorSurfaceProjection), (
        f"future-added fields must be ignored, got {result!r}"
    )
    assert result.envelope.status == "in-flight"


def test_lenient_reader_unknown_status_returns_unrecognized() -> None:
    payload = build_projection("in-flight").model_dump(mode="json")
    payload["envelope"]["status"] = "hyperspace"
    result = read_operator_surface_lenient(json.dumps(payload))
    assert isinstance(result, Unrecognized)
    assert "hyperspace" in result.reason
    assert result.schema_version == "v1"


def test_lenient_reader_unknown_schema_version_returns_unrecognized() -> None:
    payload = build_projection("in-flight").model_dump(mode="json")
    payload["schema_version"] = "v2"
    result = read_operator_surface_lenient(payload)
    assert isinstance(result, Unrecognized)
    assert result.schema_version == "v2"
    assert "schema_version" in result.reason


def test_lenient_reader_missing_schema_version_returns_unrecognized() -> None:
    payload = build_projection("in-flight").model_dump(mode="json")
    del payload["schema_version"]
    result = read_operator_surface_lenient(payload)
    assert isinstance(result, Unrecognized)


@pytest.mark.parametrize(
    "garbage",
    [
        b"\x00\x01\xff\xfe not even text",
        b"{truncated json",
        "not json at all",
        "[1, 2, 3]",
        "42",
        "null",
        "{}",
        b"",
        "",
    ],
)
def test_lenient_reader_garbage_never_raises(garbage: str | bytes) -> None:
    result = read_operator_surface_lenient(garbage)
    assert isinstance(result, Unrecognized)
    assert result.reason  # always carries a human-readable reason


def test_lenient_reader_shape_violation_returns_unrecognized() -> None:
    payload = build_projection("in-flight").model_dump(mode="json")
    payload["seq"] = -5  # violates ge=0
    result = read_operator_surface_lenient(payload)
    assert isinstance(result, Unrecognized)
    assert "seq" in result.reason


# ---------------------------------------------------------------------------
# derive_event_transitions goldens (AD-18) — five classes
# ---------------------------------------------------------------------------


def test_no_transition_derives_nothing() -> None:
    prev = build_projection("in-flight")
    cur = build_projection("in-flight")
    assert derive_event_transitions(prev, cur) == []


def test_transition_to_paused_at_gate_fires() -> None:
    assert derive_event_transitions(
        build_projection("in-flight"), build_projection("paused-at-gate")
    ) == ["paused_at_gate"]


def test_first_observation_of_paused_run_fires() -> None:
    assert derive_event_transitions(None, build_projection("paused-at-gate")) == [
        "paused_at_gate"
    ]


def test_repeated_paused_snapshot_does_not_refire() -> None:
    prev = build_projection("paused-at-gate")
    cur = build_projection("paused-at-gate", seq=11)
    assert derive_event_transitions(prev, cur) == []


def test_same_status_new_gate_identity_fires(  # review S1 fold
) -> None:
    """G1 -> G2 between two polls (resume+repause inside one poll window)."""
    prev = build_projection("paused-at-gate")
    cur = build_projection("paused-at-gate", seq=12)
    cur = cur.model_copy(
        update={"envelope": cur.envelope.model_copy(update={"paused_gate": "G2B"})}
    )
    assert derive_event_transitions(prev, cur) == ["paused_at_gate"]


def test_same_status_new_error_tag_fires() -> None:  # review S1 fold
    prev = build_projection("paused-at-error")
    cur = build_projection("paused-at-error", seq=12)
    cur = cur.model_copy(
        update={
            "envelope": cur.envelope.model_copy(
                update={"paused_error_tag": "irene.figure-contradiction"}
            )
        }
    )
    assert derive_event_transitions(prev, cur) == ["paused_at_error"]


def test_transition_to_paused_at_error_fires() -> None:
    assert derive_event_transitions(
        build_projection("in-flight"), build_projection("paused-at-error")
    ) == ["paused_at_error"]


def test_batch_resume_fires_on_waiting_to_in_flight() -> None:
    assert derive_event_transitions(
        build_projection("waiting_for_provider_batch"), build_projection("in-flight")
    ) == ["batch_pause_resumed"]


def test_resume_that_repauses_sequence_golden() -> None:
    """waiting -> in-flight -> paused-at-gate: two distinct events, in order."""
    waiting = build_projection("waiting_for_provider_batch")
    inflight = build_projection("in-flight")
    repaused = build_projection("paused-at-gate")
    assert derive_event_transitions(waiting, inflight) == ["batch_pause_resumed"]
    assert derive_event_transitions(inflight, repaused) == ["paused_at_gate"]


def test_recover_reenter_golden_derives_nothing() -> None:
    """paused-at-error -> in-flight is a recover re-entry, not a batch resume."""
    assert (
        derive_event_transitions(
            build_projection("paused-at-error"), build_projection("in-flight")
        )
        == []
    )


def test_health_threshold_fires_on_tile_crossing() -> None:
    prev = build_projection("in-flight", health=_health("nominal"))
    cur = build_projection("in-flight", health=_health("breached"))
    assert derive_event_transitions(prev, cur) == ["health_threshold"]


def test_health_threshold_does_not_refire_on_steady_breach() -> None:
    prev = build_projection("in-flight", health=_health("breached"))
    cur = build_projection("in-flight", health=_health("breached"))
    assert derive_event_transitions(prev, cur) == []


def test_health_threshold_needs_a_baseline() -> None:
    cur = build_projection("in-flight", health=_health("breached"))
    assert derive_event_transitions(None, cur) == []


def test_run_stalled_is_never_transition_derived() -> None:
    """run_stalled is watchdog-owned (AD-10): in the vocabulary, not in derivation."""
    assert "run_stalled" in EVENT_CLASSES
    fixtures = [
        (None, build_projection("in-flight")),
        (build_projection("in-flight"), build_projection("in-flight")),
        (build_projection("in-flight"), build_projection("paused-at-gate")),
        (build_projection("waiting_for_provider_batch"), build_projection("in-flight")),
    ]
    for prev, cur in fixtures:
        assert "run_stalled" not in derive_event_transitions(prev, cur)


def test_stall_condition_predicate() -> None:
    now = BASE_TIME + timedelta(seconds=700)
    stale = build_projection("in-flight", last_progress_at=BASE_TIME)
    assert stall_condition(stale, now, budget_seconds=600) is True
    assert stall_condition(stale, BASE_TIME + timedelta(seconds=100), 600) is False
    waiting = build_projection("waiting_for_provider_batch", last_progress_at=BASE_TIME)
    assert stall_condition(waiting, now, budget_seconds=600) is False  # exempt by status


def test_stall_condition_rejects_naive_now() -> None:
    projection = build_projection("in-flight")
    with pytest.raises(ValueError, match="timezone-aware"):
        stall_condition(projection, datetime(2026, 7, 11, 12, 30, 0), 600)


# ---------------------------------------------------------------------------
# Ring-buffer caps (AD-16) — trim, never raise
# ---------------------------------------------------------------------------


def test_trace_ring_201st_event_drops_oldest() -> None:
    events = [
        TraceEvent(at=BASE_TIME + timedelta(seconds=i), event=f"event-{i}")
        for i in range(TRACE_RING_CAP + 1)
    ]
    section = TraceSection(as_of=BASE_TIME, events=events)
    assert len(section.events) == TRACE_RING_CAP
    assert section.events[0].event == "event-1"  # oldest (event-0) dropped
    assert section.events[-1].event == f"event-{TRACE_RING_CAP}"


def test_health_history_51st_reading_drops_oldest() -> None:
    history = [
        HealthReading(at=BASE_TIME + timedelta(seconds=i), value=float(i))
        for i in range(HEALTH_HISTORY_CAP + 1)
    ]
    tile = HealthTile(as_of=BASE_TIME, label="tokens", value=1.0, history=history)
    assert len(tile.history) == HEALTH_HISTORY_CAP
    assert tile.history[0].value == 1.0  # oldest (0.0) dropped
    assert tile.history[-1].value == float(HEALTH_HISTORY_CAP)


def test_caps_trim_on_assignment_too() -> None:
    section = TraceSection(as_of=BASE_TIME, events=[])
    section.events = [
        TraceEvent(at=BASE_TIME + timedelta(seconds=i), event=f"event-{i}")
        for i in range(TRACE_RING_CAP + 50)
    ]
    assert len(section.events) == TRACE_RING_CAP


# ---------------------------------------------------------------------------
# Size tripwire (AD-16)
# ---------------------------------------------------------------------------


def _representative_max_projection() -> OperatorSurfaceProjection:
    """Every section at cap: the biggest projection the contract permits."""
    trace = TraceSection(
        as_of=BASE_TIME,
        events=[
            TraceEvent(
                at=BASE_TIME + timedelta(seconds=i),
                event=f"node-lifecycle-event-{i}",
                detail=(
                    f"step 04.5 sub-slide {i}: clustering poll returned partition "
                    f"verdict with confidence annotation and artifact pointer {i}"
                ),
            )
            for i in range(TRACE_RING_CAP)
        ],
    )
    tiles = [
        HealthTile(
            as_of=BASE_TIME,
            label=f"platform-{n}-credit-remaining",
            value=12345.67,
            unit="USD",
            confidence="proxy",
            threshold_state="warning",
            history=[
                HealthReading(at=BASE_TIME + timedelta(seconds=i), value=12345.67 - i)
                for i in range(HEALTH_HISTORY_CAP)
            ],
        )
        for n in range(8)
    ]
    projection = build_projection("in-flight", trace=trace)
    projection.health = HealthSection(as_of=BASE_TIME, tiles=tiles)
    projection.steps = StepsSection(
        as_of=BASE_TIME,
        manifest_digest="sha256:" + "a" * 64,
        node_count=80,
        walk_index=40,
        walk_generation=2,
        reentered_from=38,
        entries=[
            StepEntry(
                step_id=f"{i:02d}",
                label=f"Pipeline step {i} with a realistically long operator-facing label",
                stage="stage-2" if i % 2 else "stage-1",
                status="complete" if i < 40 else "pending",
                conditions=[f"condition-{i}-a", f"condition-{i}-b"],
                blockers=[f"blocker-{i}"] if i == 40 else [],
                locked_artifact_summary=f"artifact runs/x/step-{i}.json locked at G2",
            )
            for i in range(80)
        ],
    )
    projection.preflight = PreflightSection(
        as_of=BASE_TIME,
        items=[
            PreflightItem(
                name=f"heartbeat-platform-{i}",
                state="pass",
                output="HTTP 200 within budget; quota endpoint reachable",
                latency_ms=412.5,
                quota_reading="$1,234.56 remaining of $2,000.00 monthly budget",
                quota_confidence="proxy",
            )
            for i in range(20)
        ],
    )
    projection.specialists = SpecialistsSection(
        as_of=BASE_TIME,
        roster=[
            SpecialistEntry(
                name=f"specialist-{i}",
                status="working",
                current_node="04.5",
                model="gpt-5-with-a-long-deployment-suffix",
                last_artifact=f"runs/{TRIAL_ID}/artifacts/specialist-{i}-output.json",
                cost_usd=12.34,
            )
            for i in range(12)
        ],
    )
    return projection


def test_size_tripwire_representative_max_fixture_under_limit() -> None:
    projection = _representative_max_projection()
    size = len(projection.model_dump_json().encode("utf-8"))
    assert size <= PROJECTION_SIZE_LIMIT_BYTES, (
        f"TRIPWIRE: representative max projection serialized to {size} bytes, "
        f"over the {PROJECTION_SIZE_LIMIT_BYTES}-byte hard limit (AD-16). "
        "The 525KB run.json trap is being reborn — shrink sections or caps."
    )
    if size > PROJECTION_SIZE_TARGET_BYTES:
        pytest.fail(
            f"representative max projection is {size} bytes, over the "
            f"{PROJECTION_SIZE_TARGET_BYTES}-byte TARGET (AD-16). Not yet at the "
            "hard limit, but caps/fields need a look before more sections land."
        )


# ---------------------------------------------------------------------------
# HudConfig loader (AD-19) — defaults constant, never raises
# ---------------------------------------------------------------------------


def test_defaults_constant_covers_all_five_event_classes() -> None:
    assert set(HUD_CONFIG_DEFAULTS.notifications.keys()) == set(get_args(EventClass))
    assert HUD_CONFIG_DEFAULTS.notifications["paused_at_gate"].push is True
    assert HUD_CONFIG_DEFAULTS.notifications["batch_pause_resumed"].push is False
    assert HUD_CONFIG_DEFAULTS.notifications["health_threshold"] == NotificationRule(
        enabled=True, sound=False, push=False
    )
    assert HUD_CONFIG_DEFAULTS.staleness_budget_seconds == 5
    assert HUD_CONFIG_DEFAULTS.stall_budget_seconds == 600
    assert HUD_CONFIG_DEFAULTS.hud_port == 8791


def test_load_hud_config_missing_file_returns_defaults_with_status(tmp_path: Path) -> None:
    config, status = load_hud_config(tmp_path / "does-not-exist.yaml")
    assert config == HUD_CONFIG_DEFAULTS
    assert status != "ok"
    assert "defaults active" in status


def test_load_hud_config_unparseable_yaml_returns_defaults(tmp_path: Path) -> None:
    path = tmp_path / "hud-config.yaml"
    path.write_text("notifications: [unclosed\n  ]broken: {{{", encoding="utf-8")
    config, status = load_hud_config(path)
    assert config == HUD_CONFIG_DEFAULTS
    assert status != "ok"


def test_load_hud_config_non_mapping_returns_defaults(tmp_path: Path) -> None:
    path = tmp_path / "hud-config.yaml"
    path.write_text("- just\n- a\n- list\n", encoding="utf-8")
    config, status = load_hud_config(path)
    assert config == HUD_CONFIG_DEFAULTS
    assert "defaults active" in status


def test_load_hud_config_malformed_hud_block_not_silently_ok(  # review S2 fold
    tmp_path: Path,
) -> None:
    """A present-but-unusable ``hud:`` block must surface, not vanish as 'ok'."""
    for bad in ("hud: 9000\n", "hud: {prot: 9000}\n"):
        path = tmp_path / "hud-config.yaml"
        path.write_text(bad, encoding="utf-8")
        config, status = load_hud_config(path)
        assert config == HUD_CONFIG_DEFAULTS
        assert "defaults active" in status
        assert status != "ok"


def test_load_hud_config_unknown_event_class_returns_defaults(tmp_path: Path) -> None:
    path = tmp_path / "hud-config.yaml"
    path.write_text(
        "notifications:\n  reactor_meltdown: {enabled: true}\n", encoding="utf-8"
    )
    config, status = load_hud_config(path)
    assert config == HUD_CONFIG_DEFAULTS
    assert "defaults active" in status


def test_load_hud_config_partial_matrix_merges_over_defaults(tmp_path: Path) -> None:
    path = tmp_path / "hud-config.yaml"
    path.write_text(
        "notifications:\n"
        "  health_threshold: {enabled: false, sound: false, push: false}\n"
        "staleness_budget_seconds: 7\n"
        "hud:\n"
        "  port: 9000\n",
        encoding="utf-8",
    )
    config, status = load_hud_config(path)
    assert status == "ok"
    assert config.notifications["health_threshold"].enabled is False
    # untouched classes keep their defaults — a one-class override never
    # silently disables the rest of the matrix
    assert config.notifications["paused_at_gate"].push is True
    assert config.staleness_budget_seconds == 7
    assert config.stall_budget_seconds == 600
    assert config.hud_port == 9000


def test_load_hud_config_empty_file_is_pure_defaults_ok(tmp_path: Path) -> None:
    path = tmp_path / "hud-config.yaml"
    path.write_text("", encoding="utf-8")
    config, status = load_hud_config(path)
    assert status == "ok"
    assert config == HUD_CONFIG_DEFAULTS
