"""Operator-surface projection contract (Epic 35 / Story 35.1).

The contract package for the Operator HUD flight deck (architecture spine
AD-1/3/4/5/16/18/19). One versioned document —
``state/config/runs/<trial_id>/operator-surface.json`` — is the ONLY input to
HUD data collection and the notifier. This module owns:

* ``OperatorSurfaceProjection`` — the strict producer model (byte-pin source,
  ``extra="forbid"``); per-lifecycle presence rules run witness-by-default /
  strict-via-context, mirroring ``production_trial_envelope._lifecycle_invariants``.
* ``read_operator_surface_lenient`` — the consumer parse surface: tolerates
  unknown ADDED fields (strip-then-validate), returns a typed
  ``Unrecognized`` on unknown ``schema_version`` / unknown status / garbage —
  never raises (AD-4).
* ``derive_event_transitions`` + ``stall_condition`` — contract-owned pure
  event derivation so notifier and view can never drift (AD-18). The
  ``run_stalled`` class is in the vocabulary but is watchdog-owned: it is not
  transition-derivable from a (prev, cur) pair, so it never appears in
  ``derive_event_transitions`` output; the watchdog evaluates the companion
  ``stall_condition`` predicate instead (AD-10).
* ``HudConfig`` + ``load_hud_config`` + ``HUD_CONFIG_DEFAULTS`` — single
  config owner, single defaults constant (AD-19).

Layer rule (enforced): this module imports nothing from ``app.marcus``,
``app.hud``, or ``app.notify`` — pure Pydantic + stdlib (+ PyYAML for the
config loader).
"""

from __future__ import annotations

import json
import logging
import types
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Literal, Union, get_args, get_origin
from uuid import UUID

import yaml
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    ValidationInfo,
    field_validator,
    model_validator,
)

from app.models.state._base import enforce_tz_aware, enforce_uuid4_version

LOGGER = logging.getLogger(__name__)

# --------------------------------------------------------------------------
# Vocabularies
# --------------------------------------------------------------------------

# AD-5: the envelope vocabulary is the status contract. These seven values are
# deliberately re-declared VERBATIM (not imported) so the L1 set-equality test
# against ``ProductionTrialStatus`` is a real tripwire, not a tautology.
OperatorSurfaceStatus = Literal[
    "registered",
    "in-flight",
    "paused-at-gate",
    "paused-at-error",
    "waiting_for_provider_batch",
    "completed",
    "failed",
]

#: The three pause classes (subset of the status vocabulary) that demand an
#: exact next-action command string (AD-3).
PauseClass = Literal[
    "paused-at-gate",
    "paused-at-error",
    "waiting_for_provider_batch",
]

#: The five v1 notification event classes (EXPERIENCE.md §Notifications).
EventClass = Literal[
    "paused_at_gate",
    "paused_at_error",
    "batch_pause_resumed",
    "health_threshold",
    "run_stalled",
]

#: Canonical event-class ordering (deterministic derivation output order).
EVENT_CLASSES: tuple[str, ...] = (
    "paused_at_gate",
    "paused_at_error",
    "batch_pause_resumed",
    "health_threshold",
    "run_stalled",
)

# AD-11: ``missed`` (reading absent/overdue) and ``fail`` (check ran and
# failed) are two different alarms — both are first-class states.
PreflightItemState = Literal["pending", "running", "pass", "fail", "missed"]

#: Never-false-green: a quota/credit reading may claim green only with
#: ``direct`` or ``proxy`` confidence; ``unknown`` never renders green.
QuotaConfidence = Literal["direct", "proxy", "unknown"]

HealthThresholdState = Literal["nominal", "warning", "breached", "unknown"]

# --------------------------------------------------------------------------
# Caps + size budget (AD-16)
# --------------------------------------------------------------------------

TRACE_RING_CAP = 200
HEALTH_HISTORY_CAP = 50
PROJECTION_SIZE_TARGET_BYTES = 128 * 1024
PROJECTION_SIZE_LIMIT_BYTES = 256 * 1024

_KNOWN_STATUSES: frozenset[str] = frozenset(get_args(OperatorSurfaceStatus))
_PAUSED_STATUSES: frozenset[str] = frozenset(get_args(PauseClass))


# --------------------------------------------------------------------------
# HudConfig (AD-19) — single owner, single loader, single defaults constant
# --------------------------------------------------------------------------


class NotificationRule(BaseModel):
    """Per-event-class opt-in matrix row: {enabled, sound, push}."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    enabled: bool
    sound: bool = False
    push: bool = False


def _default_notifications() -> dict[str, NotificationRule]:
    """Defaults per EXPERIENCE.md §Notifications table ([ASSUMPTION]-tagged).

    ``health_threshold`` is on-HUD only (enabled, no sound, no push) — the
    EXPERIENCE.md table supersedes the earlier brief-addendum §E sketch's
    ``enabled: false``.
    """
    return {
        "paused_at_gate": NotificationRule(enabled=True, sound=True, push=True),
        "paused_at_error": NotificationRule(enabled=True, sound=True, push=True),
        "batch_pause_resumed": NotificationRule(enabled=True, sound=True, push=False),
        "health_threshold": NotificationRule(enabled=True, sound=False, push=False),
        "run_stalled": NotificationRule(enabled=True, sound=True, push=True),
    }


class HudConfig(BaseModel):
    """The one HUD/notify config shape (AD-19). Value-object: frozen."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    notifications: dict[EventClass, NotificationRule] = Field(
        default_factory=_default_notifications,
        description="Per-event-class notification matrix {enabled, sound, push}.",
    )
    staleness_budget_seconds: int = Field(default=5, gt=0)
    stall_budget_seconds: int = Field(default=600, gt=0)
    hud_port: int = Field(
        default=8791,
        ge=1,
        le=65535,
        description="HUD server port (config key hud.port; AD-6 [ASSUMPTION] default 8791).",
    )


#: AD-19: defaults are defined exactly once. This is that once.
HUD_CONFIG_DEFAULTS = HudConfig()


def load_hud_config(path: str | Path) -> tuple[HudConfig, str]:
    """Load ``hud-config.yaml``; unreadable/invalid input never raises.

    Returns ``(config, parse_status)``. ``parse_status`` is ``"ok"`` on a
    clean parse, otherwise a human-readable reason with defaults active —
    the assembler echoes both into the projection so the HUD can render
    "config unreadable — defaults active" (AD-9 / AD-19).
    """
    try:
        try:
            text = Path(path).read_text(encoding="utf-8-sig")
        except OSError as exc:
            return HUD_CONFIG_DEFAULTS, (
                f"unreadable ({type(exc).__name__}) — defaults active"
            )
        try:
            raw = yaml.safe_load(text)
        except yaml.YAMLError as exc:
            return HUD_CONFIG_DEFAULTS, (
                f"yaml parse error ({type(exc).__name__}) — defaults active"
            )
        if raw is None:
            raw = {}
        if not isinstance(raw, dict):
            return HUD_CONFIG_DEFAULTS, (
                "malformed (top level is not a mapping) — defaults active"
            )
        data = dict(raw)
        # Normalize the ``hud: {port: N}`` nesting (config-key convention
        # ``hud.port``) onto the flat model field. A ``hud:`` block that is
        # present but unusable must NOT be silently swallowed as "ok"
        # (zero-lie config echo — review S2).
        if "hud" in data:
            hud_block = data.pop("hud")
            if isinstance(hud_block, dict) and "port" in hud_block:
                if "hud_port" not in data:
                    data["hud_port"] = hud_block["port"]
            elif hud_block is not None:
                return HUD_CONFIG_DEFAULTS, (
                    "malformed 'hud' block (expected mapping with 'port') "
                    "— defaults active"
                )
        # Partial notification matrices merge over the defaults so an
        # operator override of one class never silently disables the rest.
        provided = data.get("notifications")
        if isinstance(provided, dict):
            merged: dict[str, Any] = {
                name: rule.model_dump() for name, rule in _default_notifications().items()
            }
            merged.update(provided)
            data["notifications"] = merged
        try:
            return HudConfig.model_validate(data), "ok"
        except ValidationError as exc:
            first = exc.errors()[0] if exc.errors() else {}
            loc = ".".join(str(part) for part in first.get("loc", ()))
            return HUD_CONFIG_DEFAULTS, (
                f"invalid config ({loc or 'validation error'}) — defaults active"
            )
    except Exception as exc:  # noqa: BLE001 — the loader must never raise
        LOGGER.exception("unexpected error loading hud config from %s", path)
        return HUD_CONFIG_DEFAULTS, (
            f"unexpected error ({type(exc).__name__}) — defaults active"
        )


# --------------------------------------------------------------------------
# Projection sections
# --------------------------------------------------------------------------


class _Section(BaseModel):
    """Base for all projection sections: strict + per-section ``as_of``."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    as_of: datetime = Field(description="UTC timestamp of this section's last write.")

    @field_validator("as_of")
    @classmethod
    def _enforce_as_of_tz(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)


class IdentitySection(_Section):
    """Run identity — the HUD refuses to render on mismatch (AD-8)."""

    trial_id: UUID
    lesson: str = Field(description="Lesson/corpus label, verbatim.")
    preset: Literal["production", "explore"]
    operator_id: str

    @field_validator("trial_id")
    @classmethod
    def _enforce_trial_uuid4(cls, value: UUID) -> UUID:
        return enforce_uuid4_version(value)


class EnvelopeSection(_Section):
    """Envelope status verbatim (AD-5) + pause metadata."""

    status: OperatorSurfaceStatus
    paused_gate: str | None = None
    paused_error_tag: str | None = None
    waiting_batch_id: str | None = None
    completed_at: datetime | None = None

    @field_validator("completed_at")
    @classmethod
    def _enforce_completed_tz(cls, value: datetime | None) -> datetime | None:
        return enforce_tz_aware(value) if value is not None else None


class NextActionSection(_Section):
    """The exact next-action command per pause class (AD-3; never freehand)."""

    command: str = Field(
        description="Exact CLI command string from the CLI-co-located builder, verbatim.",
    )
    pause_class: PauseClass


class StepEntry(BaseModel):
    """One row of the two-stage you-are-here map."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    step_id: str
    label: str
    stage: Literal["stage-1", "stage-2"] = Field(
        description="stage-1 = manifest step; stage-2 = ratified hud_tracked node.",
    )
    status: str = Field(
        description="Per-step walker status, verbatim (vocabulary owned by the producer).",
    )
    conditions: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    locked_artifact_summary: str | None = None


class StepsSection(_Section):
    """Two-stage step list + composed-manifest identity + walk markers (AD-15)."""

    manifest_digest: str = Field(description="Compiled-graph digest of the composed manifest.")
    node_count: int = Field(ge=0)
    walk_index: int = Field(ge=0)
    walk_generation: int = Field(
        default=0,
        ge=0,
        description="Incremented on recover-reenter so index regression renders as re-entry.",
    )
    reentered_from: int | None = Field(
        default=None,
        ge=0,
        description="Walk index the run re-entered from on recover-reenter, if any.",
    )
    entries: list[StepEntry] = Field(default_factory=list)


class PreflightItem(BaseModel):
    """One pre-flight / heartbeat item (AD-11): ``missed`` != ``fail``."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    name: str
    state: PreflightItemState
    output: str | None = None
    latency_ms: float | None = Field(default=None, ge=0)
    quota_reading: str | None = Field(
        default=None,
        description="Quota/credit reading, verbatim display string.",
    )
    quota_confidence: QuotaConfidence = "unknown"


class PreflightSection(_Section):
    items: list[PreflightItem] = Field(default_factory=list)


class HealthReading(BaseModel):
    """One historical health reading (feeds the tile drill-down)."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    at: datetime
    value: float | str

    @field_validator("at")
    @classmethod
    def _enforce_at_tz(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)


class HealthTile(_Section):
    """One health-strip tile; history capped at ``HEALTH_HISTORY_CAP`` (AD-16)."""

    label: str
    value: float | str
    unit: str | None = None
    confidence: QuotaConfidence = "unknown"
    threshold_state: HealthThresholdState = "unknown"
    history: list[HealthReading] = Field(default_factory=list)

    @field_validator("history")
    @classmethod
    def _trim_history(cls, value: list[HealthReading]) -> list[HealthReading]:
        """Ring semantics: keep the newest CAP readings; trim, never raise."""
        if len(value) > HEALTH_HISTORY_CAP:
            return value[-HEALTH_HISTORY_CAP:]
        return value


class HealthSection(_Section):
    tiles: list[HealthTile] = Field(default_factory=list)


class SpecialistEntry(BaseModel):
    """Specialist roster activity row."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    name: str
    status: str = Field(description="Specialist activity status, verbatim.")
    current_node: str | None = None
    model: str | None = None
    last_artifact: str | None = None
    cost_usd: float | None = Field(default=None, ge=0)


class SpecialistsSection(_Section):
    roster: list[SpecialistEntry] = Field(default_factory=list)


class ModalitiesSection(_Section):
    """Run-modality readings (batch / detective / styleguide + provenance)."""

    llm_execution_mode: str | None = None
    detective_disposition: str | None = None
    styleguide: str | None = None
    styleguide_provenance: str | None = None


# --------------------------------------------------------------------------
# Run-settings standing readout (Story 42.3) — the ~16 run-defining toggles.
#
# ADDITIVE within v1 (AD-4: new OPTIONAL section, NO schema_version literal
# bump). The v1 literal is the back-compat hinge — the lenient reader hard-
# requires ``schema_version == "v1"`` and strip-then-validates unknown ADDED
# fields, so a run carrying only the old ``modalities`` slice (pre-42.3 frozen
# surface) still parses (AC-6). "Bump the schema" here means the REGENERATED
# JSON Schema artifact (a new ``$def`` + a new root property), byte-pinned in
# the same diff — the governance discipline, not a breaking version flip
# (which would make every prior v1 surface Unrecognized and contradict AC-6).
#
# ``RUN_SETTINGS_TOGGLES`` is the ONE canonical (field, label) source of truth
# shared by the resolver (assembler), the keep-in-sync guard test (AC-5), and
# the HUD render — so a future new knob that isn't added here fails loudly.
# --------------------------------------------------------------------------

#: Canonical ordered ``(field_name, operator_label)`` for the run-settings
#: readout. The tuple ORDER is the render order. Every field named here MUST
#: exist on ``RunSettingsSection`` and vice-versa (pinned by AC-5).
RUN_SETTINGS_TOGGLES: tuple[tuple[str, str], ...] = (
    ("component_deck", "Component · Deck"),
    ("component_motion", "Component · Motion"),
    ("component_workbook", "Component · Workbook"),
    ("preset", "Preset"),
    ("encounter_mode", "Encounter mode"),
    ("llm_execution_mode", "LLM execution mode"),
    ("g0_dispatch_live", "MARCUS_G0_DISPATCH_LIVE"),
    ("research_dispatch_live", "MARCUS_RESEARCH_DISPATCH_LIVE"),
    ("research_detective_live", "MARCUS_RESEARCH_DETECTIVE_LIVE"),
    ("narration_figure_fidelity_active", "MARCUS_NARRATION_FIGURE_FIDELITY_ACTIVE"),
    ("voice_direction", "Voice direction"),
    ("deck_enrichment_active", "MARCUS_DECK_ENRICHMENT_ACTIVE"),
    ("udac_active", "MARCUS_UDAC_ACTIVE"),
    ("coverage_gate", "Coverage-gate family"),
    ("trial_budget_usd", "MARCUS_TRIAL_BUDGET_USD"),
    ("treatment_slots", "Treatment slots A/B"),
)


class RunSettingsSection(_Section):
    """The ~16 run-defining toggles as a standing readout (Story 42.3, AD-1).

    Every field is a REQUIRED resolved display string — env-absent toggles
    render an explicit resolved default (``"off"`` / ``"unset"``), never a
    missing key (AC-3). The assembler's deterministic resolver populates all
    sixteen from env / directive / run_summary / the prior projection, so the
    section is a pure projection of resolved run settings (double-emit on
    identical inputs is byte-identical modulo ``as_of``).
    """

    component_deck: str
    component_motion: str
    component_workbook: str
    preset: str
    encounter_mode: str
    llm_execution_mode: str
    g0_dispatch_live: str
    research_dispatch_live: str
    research_detective_live: str
    narration_figure_fidelity_active: str
    voice_direction: str
    deck_enrichment_active: str
    udac_active: str
    coverage_gate: str
    trial_budget_usd: str
    treatment_slots: str


class TraceEvent(BaseModel):
    """One state-trace event."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    at: datetime
    event: str
    detail: str | None = None

    @field_validator("at")
    @classmethod
    def _enforce_at_tz(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)


class TraceSection(_Section):
    """State-trace ring buffer, capped at ``TRACE_RING_CAP`` (AD-16)."""

    events: list[TraceEvent] = Field(default_factory=list)

    @field_validator("events")
    @classmethod
    def _trim_ring(cls, value: list[TraceEvent]) -> list[TraceEvent]:
        """Ring semantics: keep the newest CAP events; trim, never raise."""
        if len(value) > TRACE_RING_CAP:
            return value[-TRACE_RING_CAP:]
        return value


class NotificationsEchoSection(_Section):
    """Assembler echo of the parsed config + its parse status (AD-9/19)."""

    config: HudConfig
    parse_status: str = Field(
        description='"ok" or the loader reason string (e.g. defaults-active).',
    )


# --------------------------------------------------------------------------
# Decision-card / error / deliverables sections (Story 35.9 — KEY DECISION 2)
#
# Three OPTIONAL sections added ADDITIVELY within v1 (AD-4: new optional
# fields, NO schema_version bump). Every inner field is optional because the
# source artifacts are VERB-CONDITIONAL: G1 carries a drafted_proposal +
# confidence but no operator_prompt; G4A/G2B carry gate_focus / operator_prompt
# / pick_context but no drafted_proposal. The assembler maps each artifact
# field 1:1 into these sections at the pause / completion choke-points; a
# missing/garbage artifact leaves the section absent (None), never a lie.
# --------------------------------------------------------------------------


class DraftedProposal(BaseModel):
    """The runtime's drafted verdict for a gate (decision-card ``drafted_proposal``)."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    decision: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    rationale: str | None = None


class DecisionCardSection(_Section):
    """The active decision card at a gate pause (EXPERIENCE.md §Projection Demands).

    All fields optional/verb-conditional. ``pick_context`` (variant/voice
    options) and ``evidence`` are pre-summarized display strings the render
    feeds straight into the collapse-beyond-3 ``_artifacts_block`` helper.
    """

    gate_focus: str | None = None
    operator_prompt: str | None = None
    drafted_proposal: DraftedProposal | None = None
    pick_context: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)


class ErrorMessageSection(_Section):
    """The verbatim runtime error at an error pause (``error-pause.json``)."""

    message: str | None = None
    node_index: int | None = None
    tag: str | None = None


class DeliverableComponents(BaseModel):
    """The run's component-selection booleans (``run_summary.yaml``)."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    deck: bool | None = None
    motion: bool | None = None
    workbook: bool | None = None


class DeliverablesSection(_Section):
    """Landed deliverables at completion (EXPERIENCE.md §Projection Demands).

    MINIMAL by design (KEY DECISION 2 waiver): component booleans + total cost
    + cheaply-resolvable top-level export paths. Rich per-artifact path
    enumeration is the ONE registered fast-follow waiver (dated 2026-07-11,
    story 35.7) — do NOT build it here.
    """

    components: DeliverableComponents | None = None
    total_cost_usd: float | None = Field(default=None, ge=0)
    export_paths: list[str] = Field(default_factory=list)


# --------------------------------------------------------------------------
# Top-level projection
# --------------------------------------------------------------------------


class OperatorSurfaceProjection(BaseModel):
    """The v1 operator-surface projection (AD-1) — strict producer model.

    Lifecycle-presence rules (AD-15): at ``registered`` only identity,
    envelope (the status carrier), and notifications_echo are mandatory —
    every other section is ``None`` (pre-flight pending). Once past
    ``registered``, ``steps`` and ``health`` are mandatory, and any paused
    status additionally demands ``next_action``. Enforcement follows the
    envelope's witness-don't-gate pattern: violations LOG by default and
    raise only under ``invariant_mode: "strict"`` validation context.

    Note on the envelope section: the story field-inventory lists only
    identity + notifications_echo as mandatory at ``registered``, but the
    lifecycle discriminator IS ``envelope.status`` and greenlight amendment 12
    pins pre-envelope exits as "projection at ``registered``" — so the
    envelope section is structurally required and simply reads
    ``status="registered"`` before the runtime envelope exists.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    schema_version: Literal["v1"] = "v1"
    seq: int = Field(ge=0, description="Write counter; bumps on EVERY write (AD-10).")
    progress_seq: int = Field(
        ge=0,
        description=(
            "Progress counter; advances only on walk-index change, node lifecycle, "
            "pre-flight item completion, or gate/pause/resume transitions (AD-10)."
        ),
    )
    last_progress_at: datetime
    envelope_digest: str = Field(
        description="Hash of the run.json content this projection derives from (AD-17).",
    )
    as_of: datetime

    identity: IdentitySection
    envelope: EnvelopeSection
    notifications_echo: NotificationsEchoSection

    next_action: NextActionSection | None = None
    steps: StepsSection | None = None
    preflight: PreflightSection | None = None
    health: HealthSection | None = None
    specialists: SpecialistsSection | None = None
    modalities: ModalitiesSection | None = None
    # Story 42.3 — additive within v1 (AD-4): the standing run-settings readout.
    run_settings: RunSettingsSection | None = None
    trace: TraceSection | None = None

    # Story 35.9 — additive within v1 (AD-4): decision card at a gate pause,
    # verbatim error at an error pause, landed deliverables at completion.
    decision_card: DecisionCardSection | None = None
    error_message: ErrorMessageSection | None = None
    deliverables: DeliverablesSection | None = None

    @field_validator("last_progress_at", "as_of")
    @classmethod
    def _enforce_top_tz(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)

    @model_validator(mode="after")
    def _lifecycle_invariants(self, info: ValidationInfo) -> OperatorSurfaceProjection:
        """Witness-mode lifecycle presence rules (strict via context)."""
        violations: list[str] = []
        status = self.envelope.status
        if status != "registered":
            if self.steps is None:
                violations.append(f"status={status} requires the steps section")
            if self.health is None:
                violations.append(f"status={status} requires the health section")
        if status in _PAUSED_STATUSES and self.next_action is None:
            violations.append(f"status={status} requires next_action")
        if status == "paused-at-gate" and self.envelope.paused_gate is None:
            violations.append("status=paused-at-gate requires envelope.paused_gate")
        if status == "paused-at-error" and self.envelope.paused_error_tag is None:
            violations.append("status=paused-at-error requires envelope.paused_error_tag")
        if status == "waiting_for_provider_batch" and not self.envelope.waiting_batch_id:
            violations.append(
                "status=waiting_for_provider_batch requires envelope.waiting_batch_id"
            )
        if status == "completed" and self.envelope.completed_at is None:
            violations.append("status=completed requires envelope.completed_at")
        if not violations:
            return self
        context = info.context or {}
        if context.get("invariant_mode") == "strict":
            raise ValueError(
                f"projection for trial {self.identity.trial_id} lifecycle "
                "invariant violation(s): " + "; ".join(violations)
            )
        LOGGER.warning(
            "projection for trial %s lifecycle invariant violation(s) [witness mode]: %s",
            self.identity.trial_id,
            "; ".join(violations),
        )
        return self


# --------------------------------------------------------------------------
# Schema emitter (AD-4a — decision-card byte-pin pattern)
# --------------------------------------------------------------------------

SCHEMA_PATH = (
    Path(__file__).resolve().parents[1] / "schemas" / "operator-surface.v1.schema.json"
)


def operator_surface_schema_text() -> str:
    """Return the canonical emitted JSON Schema bytes as text."""
    return (
        json.dumps(
            OperatorSurfaceProjection.model_json_schema(),
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )


def emit_operator_surface_schema(schema_path: Path = SCHEMA_PATH) -> None:
    """Emit the operator-surface v1 JSON Schema to the committed pin path."""
    schema_path.parent.mkdir(parents=True, exist_ok=True)
    schema_path.write_text(operator_surface_schema_text(), encoding="utf-8", newline="\n")


# --------------------------------------------------------------------------
# Lenient consumer read surface (AD-4b)
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Unrecognized:
    """Typed refusal: the consumer renders this literally, never coerces."""

    reason: str
    raw_value: Any
    schema_version: str | None = None


def _strip_value(annotation: Any, value: Any) -> Any:
    """Recursively drop keys unknown to the target annotation's models."""
    origin = get_origin(annotation)
    if origin in (Union, types.UnionType):
        for arg in get_args(annotation):
            if isinstance(arg, type) and issubclass(arg, BaseModel) and isinstance(value, dict):
                return _strip_unknown_fields(arg, value)
        return value
    if origin is list and isinstance(value, list):
        args = get_args(annotation)
        item_annotation = args[0] if args else Any
        return [_strip_value(item_annotation, item) for item in value]
    if origin is dict and isinstance(value, dict):
        args = get_args(annotation)
        value_annotation = args[1] if len(args) == 2 else Any
        return {key: _strip_value(value_annotation, item) for key, item in value.items()}
    if (
        isinstance(annotation, type)
        and issubclass(annotation, BaseModel)
        and isinstance(value, dict)
    ):
        return _strip_unknown_fields(annotation, value)
    return value


def _strip_unknown_fields(model_cls: type[BaseModel], data: dict[str, Any]) -> dict[str, Any]:
    """Keep only keys the strict model knows; unknown ADDED fields are ignored."""
    stripped: dict[str, Any] = {}
    for name, field in model_cls.model_fields.items():
        if name in data:
            stripped[name] = _strip_value(field.annotation, data[name])
    return stripped


def read_operator_surface_lenient(
    raw: str | bytes | dict[str, Any],
) -> OperatorSurfaceProjection | Unrecognized:
    """Consumer parse surface (AD-4): tolerant of additive evolution, never raises.

    * unknown ADDED fields (any nesting level) are ignored (strip-then-validate);
    * unknown ``schema_version`` -> ``Unrecognized`` (zero-lie: rendered literally);
    * unknown envelope ``status`` -> ``Unrecognized``;
    * garbage bytes / non-JSON / non-object / shape violations -> ``Unrecognized``;
    * NO input, of any type or content, makes this function raise.
    """
    try:
        if isinstance(raw, bytes):
            try:
                text: str | None = raw.decode("utf-8-sig")
            except UnicodeDecodeError:
                return Unrecognized(reason="undecodable bytes (not UTF-8)", raw_value=raw)
        elif isinstance(raw, str):
            text = raw.lstrip("﻿")
        else:
            text = None

        if text is not None:
            try:
                payload: Any = json.loads(text)
            except (json.JSONDecodeError, ValueError):
                return Unrecognized(reason="not valid JSON", raw_value=raw)
        else:
            payload = raw

        if not isinstance(payload, dict):
            return Unrecognized(
                reason=f"projection payload is not a JSON object (got {type(payload).__name__})",
                raw_value=raw,
            )

        raw_schema_version = payload.get("schema_version")
        schema_version = raw_schema_version if isinstance(raw_schema_version, str) else None
        if raw_schema_version != "v1":
            return Unrecognized(
                reason=f"unknown schema_version {raw_schema_version!r} (expected 'v1')",
                raw_value=raw,
                schema_version=schema_version,
            )

        envelope = payload.get("envelope")
        status = envelope.get("status") if isinstance(envelope, dict) else None
        if status not in _KNOWN_STATUSES:
            return Unrecognized(
                reason=f"unknown status {status!r}",
                raw_value=raw,
                schema_version=schema_version,
            )

        stripped = _strip_unknown_fields(OperatorSurfaceProjection, payload)
        try:
            return OperatorSurfaceProjection.model_validate(stripped)
        except ValidationError as exc:
            first = exc.errors()[0] if exc.errors() else {}
            loc = ".".join(str(part) for part in first.get("loc", ()))
            return Unrecognized(
                reason=f"validation failed at {loc or '<root>'}: {first.get('msg', 'invalid')}",
                raw_value=raw,
                schema_version=schema_version,
            )
    except Exception as exc:  # noqa: BLE001 — the lenient reader must never raise
        LOGGER.exception("unexpected error reading operator-surface projection")
        return Unrecognized(
            reason=f"unexpected error ({type(exc).__name__})",
            raw_value=raw,
        )


# --------------------------------------------------------------------------
# Event derivation (AD-18) + stall predicate (AD-10)
# --------------------------------------------------------------------------


def _health_states(projection: OperatorSurfaceProjection | None) -> dict[str, str]:
    if projection is None or projection.health is None:
        return {}
    return {tile.label: tile.threshold_state for tile in projection.health.tiles}


def derive_event_transitions(
    prev: OperatorSurfaceProjection | None,
    cur: OperatorSurfaceProjection,
) -> list[str]:
    """Pure transition-derived event classes (AD-18). Both consumers use THIS.

    Derivation rules:

    * ``paused_at_gate`` / ``paused_at_error`` — fire when ``cur`` is in that
      paused status and ``prev`` was not (``prev is None`` counts: the first
      observation of a paused run is an alert-worthy fact, and the notifier's
      own ack state file dedupes across restarts per AD-9). They ALSO fire on
      a same-status snapshot pair whose pause identity changed
      (``paused_gate`` G1 -> G2, or a new ``paused_error_tag``) — a slow
      poller must not swallow a resume+repause window (review S1).
    * ``batch_pause_resumed`` — fires ONLY on an observed
      ``waiting_for_provider_batch`` -> ``in-flight`` transition (transition-only
      per AD-9; ``prev is None`` cannot fire it).
    * ``health_threshold`` — fires when any tile (matched by label) enters
      ``warning``/``breached`` from a different state; crossings need a
      baseline, so ``prev is None`` (or a missing health section) derives
      nothing. Emitted at most once per call.
    * ``run_stalled`` — in the vocabulary (``EVENT_CLASSES``) but NEVER
      derived here: stalling is the absence of writes, invisible to a
      (prev, cur) pair. The watchdog owns it via :func:`stall_condition`.

    Output order is deterministic (``EVENT_CLASSES`` order), no duplicates.
    """
    fired: list[str] = []
    prev_status = prev.envelope.status if prev is not None else None
    cur_status = cur.envelope.status

    if cur_status == "paused-at-gate" and (
        prev_status != "paused-at-gate"
        or (prev is not None and prev.envelope.paused_gate != cur.envelope.paused_gate)
    ):
        # Same-status pause with a NEW gate identity (G1 -> G2 between two
        # polls) is a fresh alert-worthy pause, not a repeat (review S1).
        fired.append("paused_at_gate")
    if cur_status == "paused-at-error" and (
        prev_status != "paused-at-error"
        or (
            prev is not None
            and prev.envelope.paused_error_tag != cur.envelope.paused_error_tag
        )
    ):
        fired.append("paused_at_error")
    if prev_status == "waiting_for_provider_batch" and cur_status == "in-flight":
        fired.append("batch_pause_resumed")

    if prev is not None and prev.health is not None:
        prev_states = _health_states(prev)
        for label, state in _health_states(cur).items():
            if state in ("warning", "breached") and prev_states.get(label, "nominal") != state:
                fired.append("health_threshold")
                break

    return fired


def stall_condition(
    cur: OperatorSurfaceProjection,
    now: datetime,
    budget_seconds: float,
) -> bool:
    """Watchdog predicate for ``run_stalled`` (AD-10): pure, no I/O.

    True iff the run is nominally ``in-flight`` and ``progress_seq`` has not
    advanced within the budget (measured off ``last_progress_at``).
    ``waiting_for_provider_batch`` is exempt by status. ``now`` must be
    timezone-aware (naive comparison would lie across DST/UTC).
    """
    if now.tzinfo is None:
        raise ValueError("stall_condition requires a timezone-aware 'now'")
    if cur.envelope.status != "in-flight":
        return False
    return (now - cur.last_progress_at).total_seconds() > budget_seconds


__all__ = [
    "EVENT_CLASSES",
    "EventClass",
    "HEALTH_HISTORY_CAP",
    "HUD_CONFIG_DEFAULTS",
    "DecisionCardSection",
    "DeliverableComponents",
    "DeliverablesSection",
    "DraftedProposal",
    "ErrorMessageSection",
    "HealthReading",
    "HealthSection",
    "HealthThresholdState",
    "HealthTile",
    "HudConfig",
    "IdentitySection",
    "EnvelopeSection",
    "ModalitiesSection",
    "NextActionSection",
    "NotificationRule",
    "NotificationsEchoSection",
    "OperatorSurfaceProjection",
    "OperatorSurfaceStatus",
    "PROJECTION_SIZE_LIMIT_BYTES",
    "PROJECTION_SIZE_TARGET_BYTES",
    "PauseClass",
    "PreflightItem",
    "PreflightItemState",
    "PreflightSection",
    "QuotaConfidence",
    "RUN_SETTINGS_TOGGLES",
    "RunSettingsSection",
    "SCHEMA_PATH",
    "SpecialistEntry",
    "SpecialistsSection",
    "StepEntry",
    "StepsSection",
    "TRACE_RING_CAP",
    "TraceEvent",
    "TraceSection",
    "Unrecognized",
    "derive_event_transitions",
    "emit_operator_surface_schema",
    "load_hud_config",
    "operator_surface_schema_text",
    "read_operator_surface_lenient",
    "stall_condition",
]
