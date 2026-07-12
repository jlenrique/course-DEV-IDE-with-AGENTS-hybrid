"""§Projection-Demands parity pin — the THIRD contract gate (Story 35.9, Splinter).

The dual-pin from 35.1 proved producer==consumer (parity) and status==envelope
(AD-5 L1), but never checked the contract against the UX spine — which is how
the ``decision_card`` / ``error_message`` / ``deliverables`` drift went unnoticed
until 35.5 render (KEY DECISION 2). This fence closes that gap: every
EXPERIENCE.md §Projection-Demands bullet (plus the gate/error/deliverables
briefing-component rows the demands imply) MUST map to a real
``OperatorSurfaceProjection`` section/field, OR be waived by a DATED entry in the
registered waiver list. Exactly ONE waiver is allowed — the rich per-artifact
deliverables path enumeration, deferred to story 35.7.

The mapping + waiver list are EXPLICIT module constants so a future contract
drift (a renamed/removed field, a demand added to the UX spine with no contract
home) trips this test RED. Source of record for the demands:
``_bmad-output/planning-artifacts/ux-designs/ux-operator-hud-2026-07-11/EXPERIENCE.md``
§"Projection Demands" (the ~10 bullets) + the briefing-component rows.
"""

from __future__ import annotations

from dataclasses import dataclass

import app.models.runtime.operator_surface as osm

# ---------------------------------------------------------------------------
# The registered waiver list — EXACTLY ONE entry allowed (KEY DECISION 2 §5).
# A demand may be left unmapped ONLY if it names a key present here, and the
# entry MUST carry a date + a fast-follow ticket. Anything else fails RED.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Waiver:
    date: str  # ISO date the waiver was registered
    ticket: str  # the fast-follow ticket that will retire it
    reason: str


WAIVERS: dict[str, Waiver] = {
    "rich-per-artifact-deliverables-enumeration": Waiver(
        date="2026-07-11",
        ticket="35.7",
        reason=(
            "Rich per-artifact deliverables path enumeration (every export / "
            "motion segment / specialist-summary path) is the ONE registered "
            "fast-follow (KEY DECISION 2 §5). v1 carries the MINIMAL deliverables "
            "(component booleans + total_cost_usd + top-level export paths); the "
            "full enumeration rides 35.7's scoped verdict."
        ),
    ),
}


# ---------------------------------------------------------------------------
# The demand -> contract mapping. Each demand is satisfied iff every field in
# ``mapping`` exists on the named contract model, OR ``waiver`` names a
# registered waiver. ``mapping`` entries are "ModelClassName.field_name".
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Demand:
    demand_id: str
    bullet: str  # verbatim-ish EXPERIENCE.md demand text
    mapping: tuple[str, ...] = ()
    waiver: str | None = None


PROJECTION_DEMANDS: tuple[Demand, ...] = (
    Demand(
        "envelope-status-pause-timestamps",
        "envelope status (canonical seven) + pause metadata "
        "(paused_gate, paused_error_tag, waiting_batch_id) + timestamps",
        (
            "EnvelopeSection.status",
            "EnvelopeSection.paused_gate",
            "EnvelopeSection.paused_error_tag",
            "EnvelopeSection.waiting_batch_id",
            "EnvelopeSection.completed_at",
            "EnvelopeSection.as_of",
        ),
    ),
    Demand(
        "run-identity",
        "run identity (trial_id, lesson/corpus, preset, operator_id)",
        (
            "IdentitySection.trial_id",
            "IdentitySection.lesson",
            "IdentitySection.preset",
            "IdentitySection.operator_id",
        ),
    ),
    Demand(
        "preflight-heartbeat-items",
        "pre-flight/heartbeat item list with per-item state, output, latency, "
        "quota reading + confidence tag",
        (
            "PreflightItem.name",
            "PreflightItem.state",
            "PreflightItem.output",
            "PreflightItem.latency_ms",
            "PreflightItem.quota_reading",
            "PreflightItem.quota_confidence",
        ),
    ),
    Demand(
        "two-stage-step-list",
        "two-stage step list (stage-1 manifest steps; stage-2 hud_tracked nodes) "
        "with per-step status, conditions, blockers, locked-artifact summary, walk index",
        (
            "StepsSection.walk_index",
            "StepsSection.manifest_digest",
            "StepEntry.stage",
            "StepEntry.status",
            "StepEntry.conditions",
            "StepEntry.blockers",
            "StepEntry.locked_artifact_summary",
        ),
    ),
    Demand(
        "decision-card-and-next-action",
        "active decision card (full card incl. pick context and digest) and the "
        "exact next-action command string per pause class",
        (
            "DecisionCardSection.gate_focus",
            "DecisionCardSection.operator_prompt",
            "DecisionCardSection.drafted_proposal",
            "DecisionCardSection.pick_context",
            "DecisionCardSection.evidence",
            "DraftedProposal.decision",
            "DraftedProposal.confidence",
            "NextActionSection.command",
            "NextActionSection.pause_class",
        ),
    ),
    Demand(
        "specialist-roster",
        "specialist roster activity (per-agent current node, status, model, "
        "last artifact, cost attribution)",
        (
            "SpecialistEntry.name",
            "SpecialistEntry.status",
            "SpecialistEntry.current_node",
            "SpecialistEntry.model",
            "SpecialistEntry.last_artifact",
            "SpecialistEntry.cost_usd",
        ),
    ),
    Demand(
        "health-readings",
        "health readings (token burn, cost vs budget_status, per-platform "
        "credit/quota + confidence, LangSmith trace URL) incl. per-reading history",
        (
            "HealthTile.label",
            "HealthTile.value",
            "HealthTile.unit",
            "HealthTile.confidence",
            "HealthTile.threshold_state",
            "HealthTile.history",
            "HealthReading.at",
            "HealthReading.value",
        ),
    ),
    Demand(
        "modality-readings",
        "modality readings (llm_execution_mode, detective disposition, "
        "styleguide + provenance)",
        (
            "ModalitiesSection.llm_execution_mode",
            "ModalitiesSection.detective_disposition",
            "ModalitiesSection.styleguide",
            "ModalitiesSection.styleguide_provenance",
        ),
    ),
    Demand(
        "state-trace-events",
        "state-trace events (append-only)",
        (
            "TraceSection.events",
            "TraceEvent.at",
            "TraceEvent.event",
            "TraceEvent.detail",
        ),
    ),
    Demand(
        "notification-echo-and-heartbeat",
        "notification config echo + watchdog progress heartbeat",
        (
            "NotificationsEchoSection.config",
            "NotificationsEchoSection.parse_status",
            "OperatorSurfaceProjection.progress_seq",
            "OperatorSurfaceProjection.last_progress_at",
        ),
    ),
    # --- briefing-component rows the demands imply (T1 reading) --------------
    Demand(
        "error-briefing",
        "error briefing card: paused_error_tag, error-pause.json message verbatim, "
        "node_id + walk index, re-entry point (EXPERIENCE.md briefing rows)",
        (
            "ErrorMessageSection.message",
            "ErrorMessageSection.node_index",
            "ErrorMessageSection.tag",
        ),
    ),
    Demand(
        "deliverables-summary",
        "deliverables summary: exports produced (deck/audio/workbook/bundle) as "
        "path/link + final cost line (EXPERIENCE.md briefing rows)",
        (
            "DeliverablesSection.components",
            "DeliverablesSection.total_cost_usd",
            "DeliverablesSection.export_paths",
            "DeliverableComponents.deck",
            "DeliverableComponents.motion",
            "DeliverableComponents.workbook",
        ),
    ),
    Demand(
        "deliverables-rich-enumeration",
        "RICH per-artifact deliverables path enumeration (every export / motion "
        "segment / specialist-summary path) — WAIVED to 35.7",
        mapping=(),
        waiver="rich-per-artifact-deliverables-enumeration",
    ),
)


# ---------------------------------------------------------------------------
# Resolver + tests
# ---------------------------------------------------------------------------


def _field_exists(dotted: str) -> bool:
    """Resolve "ModelClassName.field_name" against the contract module."""
    model_name, _, field_name = dotted.partition(".")
    model_cls = getattr(osm, model_name, None)
    if model_cls is None or not hasattr(model_cls, "model_fields"):
        return False
    return field_name in model_cls.model_fields


def test_every_projection_demand_is_mapped_or_waived() -> None:
    """The core fence: no demand may be silently unmapped (KEY DECISION 2 §4)."""
    failures: list[str] = []
    for demand in PROJECTION_DEMANDS:
        if demand.waiver is not None:
            if demand.waiver not in WAIVERS:
                failures.append(
                    f"{demand.demand_id}: cites unregistered waiver {demand.waiver!r}"
                )
            continue
        if not demand.mapping:
            failures.append(f"{demand.demand_id}: no mapping and no registered waiver")
            continue
        missing = [f for f in demand.mapping if not _field_exists(f)]
        if missing:
            failures.append(f"{demand.demand_id}: contract fields missing/renamed: {missing}")
    assert not failures, (
        "§Projection-Demands parity drift — the contract no longer covers the UX "
        "spine. Either add the missing field(s) to app/models/runtime/"
        "operator_surface.py or register a dated waiver:\n  " + "\n  ".join(failures)
    )


def test_exactly_one_waiver_is_registered() -> None:
    """KEY DECISION 2 §5: exactly ONE waiver, dated, citing the 35.7 fast-follow."""
    assert set(WAIVERS) == {"rich-per-artifact-deliverables-enumeration"}, (
        "the parity pin permits EXACTLY ONE waiver (rich per-artifact deliverables "
        "enumeration); adding another requires party-mode sign-off"
    )
    waiver = WAIVERS["rich-per-artifact-deliverables-enumeration"]
    assert waiver.date == "2026-07-11"
    assert "35.7" in waiver.ticket


def test_the_registered_waiver_is_actually_referenced() -> None:
    """Registry hygiene: no dangling waiver — the one waiver must be in use."""
    referenced = {d.waiver for d in PROJECTION_DEMANDS if d.waiver is not None}
    assert referenced == set(WAIVERS), (
        f"waiver registry / demand references drift: registered={set(WAIVERS)}, "
        f"referenced={referenced}"
    )


def test_new_35_9_sections_are_present_on_the_projection() -> None:
    """The drift this fence was born to catch: the three KEY DECISION 2 sections."""
    root = osm.OperatorSurfaceProjection.model_fields
    for name in ("decision_card", "error_message", "deliverables"):
        assert name in root, f"{name} section missing from OperatorSurfaceProjection"


def test_all_mapping_entries_resolve_to_real_contract_fields() -> None:
    """Every mapped field must resolve — a typo in the pin is itself a defect."""
    for demand in PROJECTION_DEMANDS:
        for dotted in demand.mapping:
            assert _field_exists(dotted), (
                f"{demand.demand_id}: mapping entry {dotted!r} does not resolve to a "
                "real contract field (fix the pin or the contract)"
            )
