"""Production-graph runner composition layer for migrated trials."""

from __future__ import annotations

import copy
import hashlib
import json
import logging
import os
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Literal
from uuid import UUID, uuid4

import yaml

from app.gates.errors import GateError
from app.gates.resume_api import (
    get_registered_decision_card,
    register_decision_card,
    resume_from_verdict,
)
from app.manifest.compiler import (
    _canonical_specialist_id,
    compile_run_graph,
    production_gate_ids,
)
from app.manifest.loader import load as load_manifest
from app.manifest.schema import NodeSpec
from app.marcus.lesson_plan import coverage_receipt
from app.marcus.lesson_plan.composition import compose_manifest
from app.marcus.orchestrator import (
    chooser_publisher,
    conversation_persistence,
    coverage_gate_wiring,
    coverage_runner,
    enrichment_consumption,
    g0_enrichment_wiring,
    gate_runner,
    irene_refinement_wiring,
    package_builders,
    pre_gate_marcus,
    research_detective_gate,
    research_wiring,
    specialist_summary_writer,
    storyboard_publisher,
    udac_wiring,
    workbook_wiring,
)
from app.marcus.orchestrator.dispatch_adapter import ProductionDispatchAdapter
from app.marcus.orchestrator.operator_surface_assembler import (
    DEFAULT_HUD_CONFIG_PATH,
    OperatorSurfaceAssembler,
)
from app.marcus.orchestrator.pre_gate_marcus import PreFillProposal
from app.marcus.orchestrator.research_citation import CitationFidelityError
from app.marcus.orchestrator.slide_variant_selection import (
    SlideVariantSelectionError,
    validate_selections,
)
from app.models.decision_cards import (
    AnyDecisionCardAdapter,
    DecisionCardMeta,
    G0ECard,
    G0RCard,
    G1Card,
    G2BCard,
    G2CCard,
    G3Card,
    G4ACard,
    G4Card,
)
from app.models.decision_cards._base import DecisionCardMeta as DecisionCardBaseMeta
from app.models.runtime.production_envelope import (
    ProductionEnvelope,
    SpecialistContribution,
    compute_output_digest,
)
from app.models.runtime.production_trial_envelope import ProductionTrialEnvelope
from app.models.runtime.trial_economics_report import (
    AgentCostEntry,
    BudgetStatus,
    TrialEconomicsReport,
)
from app.models.state.cache_state import CacheState
from app.models.state.component_selection import ComponentSelection
from app.models.state.operator_verdict import OperatorVerdict
from app.models.state.run_state import LlmExecutionMode, RunState
from app.runtime.cascade_config import ensure_pricing_covers_cascade, load_cascade, load_pricing
from app.runtime.economics import RUNS_ROOT, measure_trial_cost, record_trial_cost_report
from app.runtime.llm_batch.adapter import LiteLlmBatchAdapter
from app.runtime.llm_batch.cost_report import emit_batch_cost_report_fail_soft
from app.runtime.llm_batch.errors import WaitingForProviderBatchError
from app.runtime.llm_batch.receipts import (
    normalize_batch_object,
    read_receipt,
    write_receipt,
)
from app.specialists._shared.voice_direction_map import voice_direction_active
from app.specialists.dispatch_errors import SpecialistDispatchError

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MANIFEST_PATH = REPO_ROOT / "state" / "config" / "pipeline-manifest.yaml"
# Leg-C: the CD-owned styleguide SSOT. The orchestrator reads this yaml DIRECTLY
# (mirroring ``_gamma_settings_from_directive``) to resolve the scripted floor — it
# does NOT import ``app/specialists/gary`` (specialist/orchestrator import boundary).
GAMMA_STYLE_GUIDES_SSOT_PATH = REPO_ROOT / "state" / "config" / "gamma-style-guides.yaml"
# The one scripted class the orchestrator threads. Mirrors the sealed registry
# (``styleguide_library.SCRIPTED_ENUM_CLASSES``); kept as a local literal so the
# orchestrator never imports the specialist. Adding a class is a party governance act.
_SCRIPTED_MIN_CLUSTER_FLOOR_CLASS = "min_cluster_floor"
DEFAULT_GRAPH_VERSION = "v42"
LOGGER = logging.getLogger(__name__)

# Braid S3 (M1) → Canonical-arc S6 (D1): live-research toggle. DEFAULT ON —
# every canonical (unset-env) production run dispatches live research at §04.55.
# Read at BOTH walk sites (start + continuation) so the two-walk discipline holds
# — §04.55 is only reached on the continuation walk. Creds-absent is handled by
# the D4 degrade precondition inside run_research_wiring (visible recorded-empty),
# NOT by keeping this flag off. Read at BOTH walk sites (start + continuation).
RESEARCH_DISPATCH_LIVE_ENV = "MARCUS_RESEARCH_DISPATCH_LIVE"

# The explicit falsy kill-switch set (stripped/lowered). Membership → OFF (the
# dormant no-live-call escape hatch, for byte-identical / legacy / creds-absent
# walks that want to skip dispatch entirely). EVERYTHING ELSE — unset, empty,
# whitespace, truthy, unrecognized — defaults to live-ON. Enumerated as a real
# code contract (mirrors S5's g0_enrichment F-1802 kill-switch model), NOT
# ``value in TRUTHY`` (which would wrongly stay OFF on the canonical unset run).
RESEARCH_DISPATCH_LIVE_KILL_SWITCH: frozenset[str] = frozenset(
    {"0", "false", "no", "off"}
)


def _research_dispatch_live() -> bool:
    """Return True iff live research dispatch is enabled (DEFAULT ON — S6 D1).

    Canonical (unset-env) runs dispatch live research at §04.55. Only an EXPLICIT
    falsy kill-switch value (:data:`RESEARCH_DISPATCH_LIVE_KILL_SWITCH`) returns
    the dormant no-live-call path. Mirrors S5's ``g0_enrichment_active``.
    """
    return (
        os.environ.get(RESEARCH_DISPATCH_LIVE_ENV, "").strip().lower()
        not in RESEARCH_DISPATCH_LIVE_KILL_SWITCH
    )


class MissingUpstreamContributionError(RuntimeError):
    """Raised when a dependency map names an upstream contribution that is absent."""

    def __init__(
        self,
        *,
        specialist_id: str,
        downstream_input_key: str,
        downstream_specialist_id: str,
    ) -> None:
        self.specialist_id = specialist_id
        self.downstream_input_key = downstream_input_key
        self.downstream_specialist_id = downstream_specialist_id
        super().__init__(
            "missing upstream contribution "
            f"{specialist_id!r} for downstream input {downstream_input_key!r} "
            f"while invoking {downstream_specialist_id!r}"
        )


class LegacyEnvelopeSchemaError(RuntimeError):
    """Raised when resuming a run whose envelope predates per-node keying.

    S2 (SCP 2026-06-11): production-envelope.v1 rows carry no node_id; a
    resume against them would re-dispatch every specialist (double spend)
    or half-read the walk state. Murat's characterization ruling: legacy
    envelopes are migrated explicitly or rejected loudly — never half-read.
    Per the operator's relaunch-as-cycle-2 ruling, v1 runs stay frozen as
    evidence and new cycles launch fresh.
    """


class GateBypassError(RuntimeError):
    """Raised when a production pause-point gate would be silently skipped."""


class PreflightGateFailed(RuntimeError):  # noqa: N818 — a gate outcome, named for the event
    """Start-path pre-flight did not go all-green — SPOC spawn is blocked (AD-7/11).

    Raised from :func:`run_production_trial` BEFORE any specialist dispatch when
    a pre-flight/heartbeat item is not ``pass``. The registered projection is
    already persisted showing the failed item(s) plus a terminal trace event;
    the walk never runs. ``blocking_items`` are the non-soft items that gated
    the spawn (each a contract ``PreflightItem``).
    """

    def __init__(self, trial_id: UUID | str, blocking_items: list[Any]) -> None:
        self.trial_id = trial_id
        self.blocking_items = blocking_items
        names = ", ".join(
            f"{item.name}={item.state}" for item in blocking_items
        ) or "<none>"
        super().__init__(
            f"pre-flight blocked SPOC spawn for trial {trial_id}: {names}. "
            "Fix the failed dependency and re-run trial start."
        )


def _has_live_openai() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def _has_langsmith_env() -> bool:
    return bool(os.getenv("LANGSMITH_API_KEY") and os.getenv("LANGSMITH_PROJECT"))


def _now() -> datetime:
    return datetime.now(UTC)


def _run_dir(trial_id: UUID | str, runs_root: Path) -> Path:
    return runs_root / str(trial_id)


def _udac_ratify_gate(gate_code: str | None, trial_id: UUID | str, runs_root: Path) -> None:
    """UDAC v1 gate-crossing ratification side-effect, fired on EVERY gate-crossing
    branch in BOTH walks (review F3, M-5 parity).

    Guarded so that NOTHING new — not even ``_run_dir(...)`` — evaluates when UDAC is
    OFF (Blind-F3), keeping the flag-OFF path provably byte-identical regardless of
    ``_run_dir`` purity. ``record_gate_ratification`` is crash-proof + a harmless
    no-op on a branch whose mapped asset never landed on disk, so calling it on the
    asleep-gate / offline branches closes the walk-dependence gap without risk.
    """
    if not udac_wiring.udac_active():
        return
    udac_wiring.record_gate_ratification(
        gate_code=gate_code, run_dir=_run_dir(trial_id, runs_root)
    )


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )


def _emit_operator_surface(envelope: ProductionTrialEnvelope, runs_root: Path) -> None:
    """Project the envelope transition through the sole-writer assembler (AD-2).

    Wrapper double-guard: the assembler already swallows every exception
    (amendment 8), but the runner walk must NEVER be perturbed by projection
    emission, so we belt-and-suspenders here too. ``run.json`` is already
    written by the time we reach this call, so it remains truth (AD-17).
    """
    try:
        OperatorSurfaceAssembler(envelope.trial_id, runs_root).emit(envelope)
    except Exception:  # noqa: BLE001 — emission must never break the walk
        LOGGER.exception("operator-surface emit wrapper failed — swallowed")


def _emit_operator_surface_steps(
    trial_id: UUID, runs_root: Path, manifest: Any, walk_index: int
) -> None:
    """Project the two-stage steps map + walk index (AD-15). Never raises."""
    try:
        OperatorSurfaceAssembler(trial_id, runs_root).update_steps(manifest, walk_index)
    except Exception:  # noqa: BLE001 — emission must never break the walk
        LOGGER.exception("operator-surface steps wrapper failed — swallowed")


def _append_operator_surface_trace(
    trial_id: UUID | str, runs_root: Path, event: str, detail: str | None = None
) -> None:
    """Append one state-trace event to the projection (AD-16). Never raises."""
    try:
        OperatorSurfaceAssembler(trial_id, runs_root).append_trace(event, detail)
    except Exception:  # noqa: BLE001 — trace append must never break the start path
        LOGGER.exception("operator-surface trace wrapper failed — swallowed")


# --------------------------------------------------------------------------
# Ambient operator-surface sections (F-E2E-2): health / specialists /
# modalities / trace — populated from live run state DURING the walk so the
# HUD's health strip (FR9), specialist chips (FR7), modality chips (FR10), and
# state-trace well (FR8) are non-empty mid-run rather than empty. Every read is
# guarded and zero-lie: a value not cheaply known mid-walk renders `unknown`
# (never green), and a missing source omits its tile/field, never fabricates.
# --------------------------------------------------------------------------


def _operator_surface_cost_reading(
    trial_id: UUID | str, runs_root: Path, run_state: Any
) -> tuple[float | None, str]:
    """``(cost_usd, confidence)`` for the run-cost health tile.

    Prefers the persisted ``cost-report.json`` total; falls back to the live
    accumulated per-contribution spend (a real, known partial mid-walk). Never
    raises — returns ``(None, "unknown")`` when nothing is resolvable.
    """
    try:
        path = runs_root / str(trial_id) / "cost-report.json"
        if path.is_file():
            data = json.loads(path.read_text(encoding="utf-8"))
            cost = data.get("total_cost_usd") if isinstance(data, dict) else None
            if isinstance(cost, (int, float)) and cost >= 0:
                return float(cost), "proxy"
    except Exception:  # noqa: BLE001
        LOGGER.warning("operator-surface cost-report read failed for %s", trial_id)
    try:
        pe = getattr(run_state, "production_envelope", None)
        contributions = getattr(pe, "contributions", ()) or ()
        total = 0.0
        for contribution in contributions:
            value = getattr(contribution, "cost_usd", 0.0)
            total += float(value) if isinstance(value, (int, float)) else 0.0
        return total, "proxy"
    except Exception:  # noqa: BLE001
        return None, "unknown"


def _operator_surface_health_tiles(
    trial_id: UUID | str, runs_root: Path, run_state: Any
) -> list[Any]:
    """Build the health-strip tiles (FR9). Never-false-green (AD): unknown stays unknown."""
    from app.models.runtime.operator_surface import HealthTile

    now = _now()
    tiles: list[Any] = []
    cost_value, cost_conf = _operator_surface_cost_reading(trial_id, runs_root, run_state)
    if cost_value is not None:
        tiles.append(
            HealthTile(
                as_of=now,
                label="run cost",
                value=round(cost_value, 6),
                unit="USD",
                confidence=cost_conf,
                threshold_state="unknown",
            )
        )
    # Platform quota/credit is not cheaply known mid-walk -> unknown, never green.
    for label in ("openai", "gamma"):
        tiles.append(
            HealthTile(
                as_of=now,
                label=f"{label} quota",
                value="unknown",
                confidence="unknown",
                threshold_state="unknown",
            )
        )
    return tiles


def _operator_surface_specialist_roster(run_state: Any) -> list[Any]:
    """Build the specialist roster (FR7) from accumulated envelope contributions.

    A display projection (AD-16 bounded): one row per specialist, cost summed,
    ``current_node``/``model`` from the most recent contribution. Empty until the
    first specialist contributes; never fabricates a roster.
    """
    from app.models.runtime.operator_surface import SpecialistEntry

    roster: list[Any] = []
    try:
        pe = getattr(run_state, "production_envelope", None)
        contributions = getattr(pe, "contributions", ()) or ()
        agg: dict[str, dict[str, Any]] = {}
        order: list[str] = []
        for contribution in contributions:
            sid = getattr(contribution, "specialist_id", None)
            if not sid:
                continue
            if sid not in agg:
                agg[sid] = {"cost": 0.0, "node": None, "model": None}
                order.append(sid)
            value = getattr(contribution, "cost_usd", 0.0)
            agg[sid]["cost"] += float(value) if isinstance(value, (int, float)) else 0.0
            node = getattr(contribution, "node_id", None)
            if node:
                agg[sid]["node"] = node
            model = getattr(contribution, "model_used", None)
            if model:
                agg[sid]["model"] = model
        for sid in order:
            entry = agg[sid]
            roster.append(
                SpecialistEntry(
                    name=sid,
                    status="contributed",
                    current_node=entry["node"],
                    model=entry["model"],
                    last_artifact=None,
                    cost_usd=max(entry["cost"], 0.0),
                )
            )
    except Exception:  # noqa: BLE001
        LOGGER.warning("operator-surface specialist roster build failed")
    return roster


def _operator_surface_styleguide(directive_path: Path) -> tuple[str | None, str | None]:
    """Resolve styleguide name(s) + provenance from the directive. Never raises."""
    if not directive_path.is_file():
        return None, None
    loaded = yaml.safe_load(directive_path.read_text(encoding="utf-8")) or {}
    if not isinstance(loaded, dict):
        return None, None
    names: list[str] = []
    raw = loaded.get("gamma_settings")
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, dict):
                styleguide = item.get("styleguide")
                if isinstance(styleguide, str) and styleguide.strip():
                    names.append(styleguide.strip())
    resolved = ", ".join(dict.fromkeys(names)) or None
    provenance: str | None = None
    prov = loaded.get("styleguide_picker_provenance")
    if isinstance(prov, dict):
        source = prov.get("source") or prov.get("provenance") or prov.get("picker")
        if source:
            provenance = str(source)[:240]
    return resolved, provenance


def _operator_surface_modalities(
    trial_id: UUID | str, runs_root: Path, run_state: Any
) -> dict[str, Any] | None:
    """Build the modality readings (FR10): batch mode, detective disposition, styleguide."""
    mod: dict[str, Any] = {}
    lem = getattr(run_state, "llm_execution_mode", None)
    if lem:
        mod["llm_execution_mode"] = str(lem)
    run_dir = runs_root / str(trial_id)
    try:
        receipt = research_detective_gate.load_disposition(run_dir)
        if receipt and receipt.get("disposition"):
            mod["detective_disposition"] = str(receipt.get("disposition"))
        elif research_detective_gate.landing_path(run_dir).is_file():
            mod["detective_disposition"] = "awaiting_disposition"
    except Exception:  # noqa: BLE001
        LOGGER.warning(
            "operator-surface detective disposition read failed for %s", trial_id
        )
    try:
        styleguide, provenance = _operator_surface_styleguide(run_dir / "directive.yaml")
        if styleguide:
            mod["styleguide"] = styleguide
        if provenance:
            mod["styleguide_provenance"] = provenance
    except Exception:  # noqa: BLE001
        LOGGER.warning("operator-surface styleguide read failed for %s", trial_id)
    return mod or None


def _refresh_operator_surface_ambient(
    trial_id: UUID | str,
    runs_root: Path,
    run_state: Any,
    *,
    trace_event: tuple[str, str | None] | None = None,
) -> None:
    """Refresh ambient HUD sections (health/specialists/modalities [+trace]).

    Populates the four sections the walk (F-E2E-2) otherwise left empty mid-run.
    Double-guarded (the assembler also swallows), so ambient refresh can NEVER
    perturb the paid walk (greenlight amendment 8 / AD-17: run.json stays truth).
    """
    try:
        OperatorSurfaceAssembler(trial_id, runs_root).update_ambient(
            health_tiles=_operator_surface_health_tiles(trial_id, runs_root, run_state),
            specialist_roster=_operator_surface_specialist_roster(run_state),
            modalities=_operator_surface_modalities(trial_id, runs_root, run_state),
            trace_event=trace_event,
        )
    except Exception:  # noqa: BLE001 — ambient refresh must never break the walk
        LOGGER.exception("operator-surface ambient wrapper failed — swallowed")


def emit_registered_and_terminal_trace(
    trial_id: UUID,
    runs_root: Path,
    *,
    corpus_path: Path,
    preset: Literal["production", "explore"],
    operator_id: str,
    event: str,
    detail: str | None = None,
) -> None:
    """Emit a ``registered`` projection + a terminal trace event (amendment 12).

    Pre-envelope start exits (``cancelled-at-g0`` / ``saved-only``) happen in
    ``start_trial`` BEFORE ``run_production_trial`` ever persists a projection.
    Per greenlight amendment 12 those exits leave the projection at
    ``registered`` with a terminal trace event, so this builds a minimal
    registered envelope, emits it (establishing the projection), then appends
    the terminal trace. Idempotent and never raises into the caller.
    """
    try:
        production_envelope = ProductionEnvelope(trial_id=trial_id)
        envelope = ProductionTrialEnvelope(
            trial_id=trial_id,
            preset=preset,
            corpus_path=corpus_path.as_posix(),
            operator_id=operator_id,
            started_at=_now(),
            status="registered",
            production_clone_launch_evidence=False,
            production_clone_launch_evidence_reason="registered-no-specialist-fired",
            production_envelope=production_envelope,
        )
        _emit_operator_surface(envelope, runs_root)
        _append_operator_surface_trace(trial_id, runs_root, event, detail)
    except Exception:  # noqa: BLE001 — a pre-envelope exit must never raise here
        LOGGER.exception(
            "emit_registered_and_terminal_trace failed for trial %s — swallowed",
            trial_id,
        )


def _run_start_preflight_gate(
    trial_id: UUID,
    run_dir: Path,
    runs_root: Path,
    *,
    hud: Literal["on", "off"],
    producer_pid: int,
) -> Any:
    """Launch the HUD server + notifier (``--hud`` gated) and run pre-flight.

    Returns a ``PreflightResult``. Pre-flight itself is runtime-owned and runs
    regardless of ``--hud``; only the server + notifier LAUNCHES are gated by
    the flag (AD-7). A server child that fails to launch (or fails its healthz
    identity check) surfaces as a pre-flight FAIL, never a raise.
    """
    from app.marcus.orchestrator.preflight import (
        PreflightDeps,
        launch_hud_server,
        run_preflight,
    )
    from app.models.runtime.operator_surface import PreflightItem, load_hud_config

    config, _parse_status = load_hud_config(DEFAULT_HUD_CONFIG_PATH)
    port = config.hud_port

    healthz_url: str | None = None
    expected_launch_nonce: str | None = None
    healthz_fn = None
    notifier_alive_fn = None
    if hud == "on":
        expected_launch_nonce = uuid4().hex
        server_proc = launch_hud_server(
            trial_id=trial_id,
            run_dir=run_dir,
            launch_nonce=expected_launch_nonce,
            port=port,
            mode="session",
        )
        if server_proc is None:
            # Launch failure → healthz item FAIL, never a raise (AD-7).
            def healthz_fn() -> PreflightItem:  # type: ignore[misc]
                return PreflightItem(
                    name="hud-server-healthz",
                    state="fail",
                    output="HUD server child failed to launch",
                )
        else:
            healthz_url = f"http://127.0.0.1:{port}/healthz"
        try:
            from app.notify.__main__ import launch_notifier

            notifier_proc = launch_notifier(
                str(trial_id), str(run_dir), producer_pid=producer_pid
            )
            notifier_alive_fn = lambda: notifier_proc.poll() is None  # noqa: E731
        except Exception:  # noqa: BLE001 — a notifier launch failure is a FAIL item
            LOGGER.exception("notifier launch failed — recording as pre-flight item")

            def notifier_alive_fn() -> bool:  # type: ignore[misc]
                return False

    deps = PreflightDeps(
        healthz_url=healthz_url,
        healthz_fn=healthz_fn,
        expected_trial_id=str(trial_id),
        expected_launch_nonce=expected_launch_nonce,
        notifier_alive_fn=notifier_alive_fn,
    )
    return run_preflight(trial_id, runs_root, deps)


def _persist_envelope(envelope: ProductionTrialEnvelope, runs_root: Path) -> Path:
    path = _run_dir(envelope.trial_id, runs_root) / "run.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(envelope.model_dump_json(indent=2) + "\n", encoding="utf-8")
    # AD-2: emit the projection AFTER the run.json write (never before; run.json
    # write semantics are unchanged — same plain write_text, same bytes).
    _emit_operator_surface(envelope, runs_root)
    return path


def _fallback_cost_report(trial_id: str) -> TrialEconomicsReport:
    cascade = load_cascade()
    pricing = load_pricing()
    ensure_pricing_covers_cascade(cascade, pricing)
    return TrialEconomicsReport(
        trial_id=trial_id,
        measured_at=_now(),
        total_cost_usd=0.0,
        per_agent_breakdown={
            "marcus": AgentCostEntry(
                agent_name="marcus",
                model_assigned=cascade.marcus.model,
                call_count=0,
                input_tokens=0,
                output_tokens=0,
                cost_usd=0.0,
            )
        },
        per_model_breakdown={cascade.marcus.model: 0.0},
        cascade_config_digest=cascade.sha256_digest,
        pricing_table_digest=pricing.sha256_digest,
        langsmith_trace_url=None,
        drift_alerts=[],
        budget_status=BudgetStatus(state="no-cap", over_by_usd=0.0),
    )


@contextmanager
def _trial_trace_context(
    *,
    trial_id: UUID,
    preset: str,
    operator_id: str,
) -> Any:
    metadata = {
        "trial_id": str(trial_id),
        "preset": preset,
        "operator_id": operator_id,
    }
    try:
        from langsmith import tracing_context
    except ImportError:
        yield metadata
        return
    with tracing_context(metadata=metadata):
        yield metadata


def _trace_run(
    *,
    trial_id: UUID,
    specialist_id: str,
    model_id: str,
    input_tokens: int,
    output_tokens: int,
) -> SimpleNamespace:
    return SimpleNamespace(
        id=str(uuid4()),
        trace_id=str(trial_id),
        name=f"{specialist_id} production dispatch",
        run_type="llm",
        prompt_tokens=input_tokens,
        completion_tokens=output_tokens,
        total_tokens=input_tokens + output_tokens,
        extra={
            "metadata": {
                "trial_id": str(trial_id),
                "specialist_id": specialist_id,
                "model_id": model_id,
            }
        },
        child_runs=[],
    )


def _trace_run_for_contribution(
    *,
    trial_id: UUID,
    contribution: SpecialistContribution,
) -> SimpleNamespace:
    usage = contribution.output.get("usage")
    input_tokens = 25
    output_tokens = 10
    if isinstance(usage, dict):
        input_tokens = int(usage.get("input_tokens") or usage.get("prompt_tokens") or 25)
        output_tokens = int(
            usage.get("output_tokens") or usage.get("completion_tokens") or 10
        )
    return _trace_run(
        trial_id=trial_id,
        specialist_id=contribution.specialist_id,
        model_id=contribution.model_used,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )


def _trace_run_for_pre_gate_marcus(
    *,
    trial_id: UUID,
    gate_id: str,
    proposal: PreFillProposal,
) -> SimpleNamespace:
    return SimpleNamespace(
        id=str(uuid4()),
        trace_id=str(trial_id),
        name=f"pre-gate-marcus {gate_id}",
        run_type="llm",
        prompt_tokens=1,
        completion_tokens=1,
        total_tokens=2,
        extra={
            "metadata": {
                "trial_id": str(trial_id),
                "specialist_id": "marcus",
                "node_id": "pre-gate-marcus",
                "gate_id": gate_id,
                "model_id": "gpt-5-nano",
                "decision": proposal.decision,
                "directive": proposal.directive,
            }
        },
        child_runs=[],
    )


def _trace_root(
    *,
    trial_id: UUID,
    metadata: dict[str, str],
    child_runs: list[SimpleNamespace],
) -> SimpleNamespace:
    return SimpleNamespace(
        id=str(trial_id),
        trace_id=str(trial_id),
        name="production trial",
        run_type="chain",
        extra={"metadata": metadata},
        child_runs=child_runs,
    )


def _trace_to_json(root: SimpleNamespace) -> dict[str, Any]:
    def convert(value: Any) -> Any:
        if isinstance(value, SimpleNamespace):
            return {key: convert(item) for key, item in vars(value).items()}
        if isinstance(value, list):
            return [convert(item) for item in value]
        if isinstance(value, dict):
            return {key: convert(item) for key, item in value.items()}
        return value

    return {"root": convert(root)}


def _default_dependency_map_for(
    *,
    specialist_id: str,
    production_envelope: ProductionEnvelope,
) -> dict[str, str]:
    """Derive the deterministic dependency fallback for undeclared manifest nodes."""
    prior_ids = [item.specialist_id for item in production_envelope.contributions]
    if not prior_ids:
        return {}
    if specialist_id == "cd" and "texas" in prior_ids:
        return {"source_bundle": "texas"}
    return {"upstream_output": prior_ids[-1]}


def _canonical_dependency_specialist_id(specialist_id: str) -> str:
    return _canonical_specialist_id(specialist_id) or specialist_id


def _normalize_dependency_map(
    *,
    dependency_map: dict[str, str],
    production_envelope: ProductionEnvelope,
) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for downstream_input_key, upstream_specialist_id in dependency_map.items():
        # Presence checks use latest_for_specialist — the intentful any-node
        # API (Winston S2-A: bare get_contribution without node_id is pinned
        # out of production call sites).
        if production_envelope.latest_for_specialist(upstream_specialist_id) is not None:
            normalized[downstream_input_key] = upstream_specialist_id
            continue
        canonical = _canonical_dependency_specialist_id(upstream_specialist_id)
        normalized[downstream_input_key] = (
            canonical
            if production_envelope.latest_for_specialist(canonical) is not None
            else upstream_specialist_id
        )
    return normalized


def _ensure_upstream_contributions_present(
    *,
    dependency_map: dict[str, str],
    production_envelope: ProductionEnvelope,
    downstream_specialist_id: str,
) -> None:
    for downstream_input_key, upstream_specialist_id in dependency_map.items():
        if production_envelope.latest_for_specialist(upstream_specialist_id) is None:
            raise MissingUpstreamContributionError(
                specialist_id=upstream_specialist_id,
                downstream_input_key=downstream_input_key,
                downstream_specialist_id=downstream_specialist_id,
            )


def _resolve_dependency_map(
    *,
    node: NodeSpec,
    specialist_id: str,
    production_envelope: ProductionEnvelope,
) -> dict[str, str]:
    if node.dependencies:
        dependency_map = dict(node.dependencies)
    else:
        dependency_map = _default_dependency_map_for(
            specialist_id=specialist_id,
            production_envelope=production_envelope,
        )
    dependency_map = _normalize_dependency_map(
        dependency_map=dependency_map,
        production_envelope=production_envelope,
    )
    _ensure_upstream_contributions_present(
        dependency_map=dependency_map,
        production_envelope=production_envelope,
        downstream_specialist_id=specialist_id,
    )
    return dependency_map


def _card_meta(node_id: str) -> DecisionCardMeta:
    return DecisionCardMeta(
        cache_state="mixed",
        affected_nodes=[node_id],
        override_trail=[],
        reject_rate=0.0,
        party_mode_contributions=[],
        sanctum_warnings=[],
    )


def _base_card_meta(meta: DecisionCardMeta) -> DecisionCardBaseMeta:
    return DecisionCardBaseMeta(
        cache_state=meta.cache_state,
        affected_nodes=meta.affected_nodes,
        override_trail=meta.override_trail,
    )


def _latest_contribution_output(production_envelope: Any, specialist_id: str) -> dict[str, Any]:
    """Latest production-envelope output dict for a specialist (S0.3 card binding)."""
    contributions = getattr(production_envelope, "contributions", None) or []
    latest: dict[str, Any] = {}
    for contrib in contributions:
        cid = getattr(contrib, "specialist_id", None)
        if cid is None and isinstance(contrib, dict):
            cid = contrib.get("specialist_id")
        if str(cid or "") != specialist_id:
            continue
        output = getattr(contrib, "output", None)
        if output is None and isinstance(contrib, dict):
            output = contrib.get("output")
        if isinstance(output, dict):
            latest = output  # append-order: keep the last match
    return latest


def _voice_candidates(production_envelope: Any) -> tuple[list[str], list[dict[str, Any]]]:
    """(voice_id list, structured options) from enrique voice_preview (S0.3 / T4-F6).

    Surfaces the real voice options the producer already emitted onto the card —
    Trial-4 had `voice_candidates: []` while enrique's voice_preview.voices held
    3 real options with sample URLs.
    """
    output = _latest_contribution_output(production_envelope, "enrique")
    preview = output.get("voice_preview") if isinstance(output, dict) else None
    voices = preview.get("voices") if isinstance(preview, dict) else None
    if not isinstance(voices, list):
        return [], []
    ids: list[str] = []
    options: list[dict[str, Any]] = []
    for voice in voices:
        if not isinstance(voice, dict):
            continue
        vid = str(voice.get("voice_id") or "")
        if not vid:
            continue
        ids.append(vid)
        options.append(
            {
                "voice_id": vid,
                "voice_name": voice.get("voice_name"),
                "sample_audio_url": voice.get("sample_audio_url"),
                "characteristics": voice.get("characteristics"),
            }
        )
    return ids, options


def _variant_candidates(production_envelope: Any) -> tuple[list[str], list[dict[str, Any]]]:
    """(variant-id list, per-slide options) from gary_slide_output (S0.3).

    Pre-N-dispatch this yields the single dispatch variant; once Gary
    N-dispatches (charter T5b) it naturally becomes the N selectable variants.
    """
    output = _latest_contribution_output(production_envelope, "gary")
    rows = output.get("gary_slide_output") if isinstance(output, dict) else None
    if not isinstance(rows, list):
        return [], []
    per_slide: dict[str, list[dict[str, Any]]] = {}
    variants: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        slide_id = str(row.get("slide_id") or "")
        variant = str(row.get("dispatch_variant") or "A")
        variants.add(variant)
        per_slide.setdefault(slide_id, []).append(
            {
                "variant": variant,
                "file_path": row.get("file_path"),
                "display_title": row.get("display_title"),
                "gamma_settings": row.get("gamma_settings"),
            }
        )
    options = [{"slide_id": sid, "variants": rows} for sid, rows in per_slide.items()]
    return sorted(variants), options


def _variant_gamma_settings(production_envelope: Any) -> list[dict[str, Any]]:
    output = _latest_contribution_output(production_envelope, "gary")
    raw = output.get("variant_gamma_settings") if isinstance(output, dict) else None
    if isinstance(raw, list) and all(isinstance(item, dict) for item in raw):
        return [dict(item) for item in raw]
    rows = output.get("gary_slide_output") if isinstance(output, dict) else None
    if not isinstance(rows, list):
        return []
    by_variant: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        settings = row.get("gamma_settings")
        variant = str(row.get("dispatch_variant") or row.get("variant_id") or "")
        if variant and isinstance(settings, dict):
            by_variant.setdefault(variant, dict(settings))
    return [by_variant[key] for key in sorted(by_variant)]


def _build_decision_card(
    *,
    gate_id: str,
    trial_id: UUID,
    node_id: str,
    operator_id: str,
    pending_nodes: list[str],
    artifact_paths: list[Path],
    production_envelope: Any = None,
    pre_fill: PreFillProposal | None = None,
    runs_root: Path = RUNS_ROOT,
) -> Any:
    drafted_proposal: dict[str, Any] = {"node_id": node_id, "operator_id": operator_id}
    if pre_fill is not None:
        drafted_proposal.update(
            {
                "decision": pre_fill.decision,
                "directive": pre_fill.directive,
                "rationale": pre_fill.rationale,
                "confidence": pre_fill.confidence,
                "confidence_signals": list(pre_fill.confidence_signals),
            }
        )
    evidence = [{"kind": "production-runner", "node_id": node_id}]
    adjacent_summary = specialist_summary_writer.load_most_recent_summary(
        trial_id=trial_id,
        runs_root=runs_root,
        before=_now(),
    )
    if adjacent_summary is not None:
        evidence.append(
            {
                "kind": "specialist-summary",
                "path": adjacent_summary.path.as_posix(),
                "content": adjacent_summary.text,
            }
        )
    common = {
        "card_id": uuid4(),
        "trial_id": trial_id,
        "created_at": _now(),
        "drafted_proposal": drafted_proposal,
        "evidence": evidence,
        "risks": [],
        "verb": "approve",
        "meta": _card_meta(node_id),
    }
    if gate_id == "G1":
        return G1Card(
            card_id=common["card_id"],
            trial_id=common["trial_id"],
            created_at=common["created_at"],
            decision_card_digest="0" * 64,
            drafted_proposal=drafted_proposal,
            evidence=evidence,
            meta=_base_card_meta(common["meta"]),
            verb=common["verb"],
            trial_summary="Production graph reached Gate 1.",
            opened_by="production_runner",
            next_nodes=pending_nodes[:3],
        )
    if gate_id == "G2C":
        return G2CCard(
            card_id=common["card_id"],
            trial_id=common["trial_id"],
            created_at=common["created_at"],
            decision_card_digest="0" * 64,
            meta=_base_card_meta(common["meta"]),
            verb=common["verb"],
            readiness_status="ready",
            blocking_issues=[],
            ready_nodes=pending_nodes[:3],
        )
    if gate_id == "G3":
        return G3Card(
            card_id=common["card_id"],
            trial_id=common["trial_id"],
            created_at=common["created_at"],
            decision_card_digest="0" * 64,
            meta=_base_card_meta(common["meta"]),
            verb=common["verb"],
            progress_percent=50.0,
            active_node_id=node_id,
            pending_nodes=pending_nodes,
            operator_prompt="Approve, edit, or reject the in-flight package.",
        )
    if gate_id == "G4":
        return G4Card(
            card_id=common["card_id"],
            trial_id=common["trial_id"],
            created_at=common["created_at"],
            decision_card_digest="0" * 64,
            meta=_base_card_meta(common["meta"]),
            verb=common["verb"],
            final_status="partial",
            artifact_paths=[path.as_posix() for path in artifact_paths],
            outcome_summary="Production graph reached closeout review.",
        )
    if gate_id == "G2B":
        # Arc 2 woken variant-pick HIL (07B-gate, after node 07B quinn-r variant
        # eval). `pick_context` carries the adjacent quinn-r evaluation (evidence,
        # incl. the specialist summary) so the operator has the variants to pick
        # FROM; the operator picks one or default-accepts (verb=approve,
        # selected_variant_id=None). Structured `variant_candidates` parsing is a
        # follow-on (weed-clearing posture: the pick must function + show the
        # evaluation; rich per-candidate parsing is a postmortem-harvest item).
        variant_ids, variant_options = _variant_candidates(production_envelope)
        gamma_settings = _variant_gamma_settings(production_envelope)
        g2b_context = list(evidence)
        if variant_options:
            g2b_context.append({"kind": "variant-options", "slides": variant_options})
        if gamma_settings:
            g2b_context.append({"kind": "gamma-settings", "settings": gamma_settings})
        return G2BCard(
            card_id=common["card_id"],
            trial_id=common["trial_id"],
            created_at=common["created_at"],
            decision_card_digest="0" * 64,
            meta=_base_card_meta(common["meta"]),
            verb=common["verb"],
            variant_candidates=variant_ids,
            selected_variant_id=None,
            gamma_settings=gamma_settings,
            pick_context=g2b_context,
            operator_prompt="Approve the proposed slide variants, or edit to select alternates.",
        )
    if gate_id == "G4A":
        # Arc 2 woken voice-pick HIL (11-gate, after node 11 elevenlabs voice
        # options). S0.3/T4-F6: project enrique's real voice_preview.voices onto
        # `voice_candidates` (+ structured options into pick_context) so the card
        # carries the choices, not just the summary text.
        voice_ids, voice_options = _voice_candidates(production_envelope)
        g4a_context = list(evidence)
        if voice_options:
            g4a_context.append({"kind": "voice-options", "voices": voice_options})
        return G4ACard(
            card_id=common["card_id"],
            trial_id=common["trial_id"],
            created_at=common["created_at"],
            decision_card_digest="0" * 64,
            meta=_base_card_meta(common["meta"]),
            verb=common["verb"],
            voice_candidates=voice_ids,
            selected_voice_id=None,
            pick_context=g4a_context,
            operator_prompt="Approve the proposed voice, or edit to select an alternate.",
        )
    if gate_id == "G0E":
        # Operator confirm-gate #1 (G0-S2). The g0-enrichment orchestration node
        # froze the typed manifest + provisional LOs + A10 provenance/roots to
        # run_dir/g0-enrichment.json; surface that as the confirm card. Deterministic
        # guard: the model's typing/LO proposal NEVER auto-advances — this card is a
        # PROPOSAL the operator confirms (verb defaults to approve only as the
        # operator's own default-accept, decided by the verdict, not the model).
        enrichment = (
            g0_enrichment_wiring.load_enrichment_result(_run_dir(trial_id, runs_root))
            or {}
        )
        return G0ECard(
            card_id=common["card_id"],
            trial_id=common["trial_id"],
            created_at=common["created_at"],
            decision_card_digest="0" * 64,
            meta=_base_card_meta(common["meta"]),
            verb=common["verb"],
            typed_components=enrichment.get("typed_components", []),
            provisional_los=enrichment.get("provisional_los", []),
            traversal_roots=enrichment.get("traversal_roots", []),
            enumeration_provenance=enrichment.get("enumeration_provenance", []),
            reconcile=enrichment.get("reconcile", {}),
            dissents=enrichment.get("dissents", []),
            coverage_plan=coverage_receipt.coverage_plan_view_from_dicts(
                enrichment.get("coverage_annotations", [])
            ),
            operator_prompt=(
                "Confirm the source TYPE manifest + candidate provisional LOs "
                "(or edit/reject). Marcus proposes; you decide."
            ),
        )
    if gate_id == "G0R":
        # Operator ratify-gate #2 (G0-S3). The irene-refinement orchestration node
        # refined the gate-#1 provisional LOs in place and froze the refined plan +
        # signed LO-delta ledger + per-LO adequacy + count reconciliation to
        # run_dir/irene-refinement.json; surface that as the ratify card.
        # Deterministic guard: the model NEVER auto-ratifies — the operator verdict
        # advances refined->ratified.
        refinement = (
            irene_refinement_wiring.load_refinement_result(_run_dir(trial_id, runs_root))
            or {}
        )
        return G0RCard(
            card_id=common["card_id"],
            trial_id=common["trial_id"],
            created_at=common["created_at"],
            decision_card_digest="0" * 64,
            meta=_base_card_meta(common["meta"]),
            verb=common["verb"],
            refined_los=refinement.get("refined_los", []),
            lo_delta=refinement.get("lo_delta", []),
            reconcile=refinement.get("reconcile", {}),
            flagged_for_operator=refinement.get("flagged_for_operator", []),
            operator_prompt=(
                "Ratify the refined learning objectives + signed LO-delta (or "
                "edit/reject). Adequacy alerts are advisory; rule on any "
                "recommend-drop / proposed-new. Marcus proposes; you decide."
            ),
        )
    raise RuntimeError(f"unsupported production gate id: {gate_id}")


def _persist_conversation_turn_if_possible(
    *,
    card: Any,
    gate_id: str,
    trial_id: UUID,
    operator_id: str,
    runs_root: Path,
) -> Path | None:
    draft = getattr(card, "drafted_proposal", {}) or {}
    required = {"decision", "directive", "rationale", "confidence", "confidence_signals"}
    if not required.issubset(draft):
        return None
    if not (runs_root / str(trial_id) / "directive.yaml").is_file():
        LOGGER.debug(
            "skipping conversation turn persistence for trial %s: directive.yaml missing",
            trial_id,
        )
        return None
    return conversation_persistence.write_turn(
        trial_id=str(trial_id),
        gate_id=gate_id,
        decision_card={
            "decision": draft["decision"],
            "directive": draft["directive"],
            "rationale": draft["rationale"],
            "confidence": draft["confidence"],
            "confidence_signals": draft["confidence_signals"],
        },
        free_text_rationale=str(draft["rationale"]),
        operator_id=operator_id,
        runs_root=runs_root,
    )


def _pack_hash_binding(
    manifest_path: Path,
    *,
    selection: ComponentSelection | None = None,
    composed_manifest: Any | None = None,
) -> str:
    """Bind the run-summary to the graph that ACTUALLY ran.

    When the selected graph is structurally identical to the raw manifest, this
    returns the raw manifest-file sha256. When the raw manifest contains optional
    nodes outside the selected components (for example 07W while the default is
    deck+motion), it binds the COMPOSED graph's node set so the audit trail never
    claims an unselected component ran.

    No-op detection is STRUCTURAL — the composed graph's node set is compared to
    the raw manifest's node set — rather than ``selection == production_default()``.
    """
    raw = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    if selection is None:
        return raw
    raw_manifest = load_manifest(manifest_path)
    composed = (
        composed_manifest
        if composed_manifest is not None
        else compose_manifest(raw_manifest, selection)
    )
    raw_node_ids = sorted(node.id for node in raw_manifest.nodes)
    composed_node_ids = sorted(node.id for node in composed.nodes)
    if composed_node_ids == raw_node_ids:
        return raw  # composition was a no-op for this manifest -> byte-identical
    payload = json.dumps(
        {
            "manifest_file_sha256": raw,
            "component_selection": selection.as_map(),
            "composed_node_ids": composed_node_ids,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _conversation_chain_digest(*, trial_id: UUID, runs_root: Path) -> str:
    digest = conversation_persistence.latest_turn_digest(str(trial_id), runs_root)
    if digest is not None:
        return digest
    directive_path = runs_root / str(trial_id) / "directive.yaml"
    if directive_path.is_file():
        return hashlib.sha256(directive_path.read_bytes()).hexdigest()
    return "0" * 64


def _emit_run_summary_yaml(
    *,
    trial_id: UUID,
    terminal_gate: str,
    runs_root: Path,
    manifest_path: Path,
    langsmith_trace_id: str | None,
    silent_bypass_events: int = 0,
    selection: ComponentSelection | None = None,
    composed_manifest: Any | None = None,
) -> Path:
    if silent_bypass_events != 0:
        LOGGER.debug(
            "run_summary.yaml silent_bypass_events expected 0, got %s",
            silent_bypass_events,
        )
    payload = {
        "terminal_gate": terminal_gate,
        "silent_bypass_events": silent_bypass_events,
        "specialist_roster_count": len(specialist_summary_writer.CANONICAL_SPECIALIST_IDS),
        "pack_hash_binding": _pack_hash_binding(
            manifest_path,
            selection=selection,
            composed_manifest=composed_manifest,
        ),
        "component_selection": selection.as_map() if selection is not None else None,
        "conversation_chain_digest": _conversation_chain_digest(
            trial_id=trial_id,
            runs_root=runs_root,
        ),
        "langsmith_trace_id": langsmith_trace_id or "skipped-no-langsmith-env",
    }
    path = _run_dir(trial_id, runs_root) / "run_summary.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(payload, sort_keys=False),
        encoding="utf-8",
        newline="\n",
    )
    return path


def _quartile_engagement_counts(child_runs: list[SimpleNamespace]) -> tuple[int, int]:
    if not child_runs:
        return 0, 0
    quartile_size = max(1, len(child_runs) // 4)
    return len(child_runs[:quartile_size]), len(child_runs[-quartile_size:])


def _emit_engagement_decay_report(
    *,
    trial_id: UUID,
    child_runs: list[SimpleNamespace],
) -> Path:
    first_quartile, last_quartile = _quartile_engagement_counts(child_runs)
    result = gate_runner.emit_engagement_decay_report(
        trial_id=str(trial_id),
        first_quartile_events=first_quartile,
        last_quartile_events=last_quartile,
    )
    return Path(result["report_path"])


def _write_checkpoint(
    *,
    trial_id: UUID,
    runs_root: Path,
    node_index: int,
    gate_id: str,
    run_state: RunState,
    envelope: ProductionTrialEnvelope,
    manifest_path: Path,
    allow_offline_cost_report: bool,
    max_specialist_calls: int,
    directive_path: Path | None,
    bundle_dir: Path | None,
) -> Path:
    path = _run_dir(trial_id, runs_root) / "checkpoint.json"
    _write_json(
        path,
        {
            "trial_id": str(trial_id),
            "next_node_index": node_index + 1,
            "gate_id": gate_id,
            "run_state": run_state.model_dump(mode="json"),
            "runner": {
                "corpus_path": envelope.corpus_path,
                "preset": envelope.preset,
                "operator_id": envelope.operator_id,
                "manifest_path": manifest_path.as_posix(),
                "allow_offline_cost_report": allow_offline_cost_report,
                "max_specialist_calls": max_specialist_calls,
                "directive_path": directive_path.as_posix() if directive_path else None,
                "bundle_dir": bundle_dir.as_posix() if bundle_dir else None,
            },
        },
    )
    return path


def _canonical_directive_path(*, trial_id: UUID, runs_root: Path) -> Path:
    return _run_dir(trial_id, runs_root) / "directive.yaml"


def _resolve_resume_directive_path(
    runner: dict[str, Any], *, trial_id: UUID, runs_root: Path
) -> Path | None:
    directive_path_raw = runner.get("directive_path")
    if directive_path_raw:
        return Path(directive_path_raw)
    canonical = _canonical_directive_path(trial_id=trial_id, runs_root=runs_root)
    return canonical if canonical.is_file() else None


def _resolve_resume_bundle_dir(
    runner: dict[str, Any],
    *,
    trial_id: UUID,
    runs_root: Path,
    directive_path: Path | None,
) -> Path | None:
    bundle_dir_raw = runner.get("bundle_dir")
    if bundle_dir_raw:
        return Path(bundle_dir_raw)
    if directive_path is None:
        return None
    return _run_dir(trial_id, runs_root) / "bundle"


def _ensure_decision_card_registered_from_disk(
    *,
    trial_id: UUID,
    gate_id: str,
    run_dir: Path,
) -> None:
    if get_registered_decision_card(trial_id, gate_id) is not None:
        return
    decision_path = run_dir / f"decision-card-{gate_id}.json"
    if not decision_path.exists():
        return
    payload = json.loads(decision_path.read_text(encoding="utf-8"))
    issued_at_raw = payload.get("issued_at")
    if not issued_at_raw:
        raise GateError(
            "card_missing",
            "persisted DecisionCard is missing issued_at; cannot validate "
            "decision-card digest binding after registry loss",
        )
    issued_at = datetime.fromisoformat(str(issued_at_raw).replace("Z", "+00:00"))
    card = AnyDecisionCardAdapter.validate_python(payload["card"])
    stored = register_decision_card(
        card,
        issuance_timestamp=issued_at,
        server_nonce=str(payload["server_nonce"]),
    )
    if stored.digest != payload["digest"]:
        raise GateError(
            "digest_mismatch",
            "persisted DecisionCard digest does not match rehydrated card metadata",
        )


# BETA T5b (party-ratified Option B, 2026-06-19): the `select` picker verb does a
# SURGICAL OVERLAY of an operator selection onto the existing envelope, distinct
# from `edit` (full-replace, contract preserved). Per-gate selectable-key
# allowlist — a select carrying any other key fails loud (no partial write).
_SELECTABLE_KEYS_BY_GATE: dict[str, frozenset[str]] = {
    "G4A": frozenset({"selected_voice_id"}),
    "G2B": frozenset({"selected_variant_id", "slide_variant_selections"}),
}


class SelectionBindingError(ValueError):  # noqa: N818
    """A `select` verdict could not be bound (missing envelope or non-selectable key)."""


class UnknownSelectionKeyError(SelectionBindingError):
    """A `select` verdict carried a key outside the gate's selectable-key allowlist."""


class VariantSelectionError(RuntimeError):
    """The deck-wide selected variant could not be applied to Gary's roster."""


def _merge_selection_into_envelope(
    existing: dict[str, Any], selection: dict[str, Any], gate_id: str
) -> dict[str, Any]:
    """Overlay an operator selection onto the existing envelope (leaf-merge).

    Invariants (Winston/Amelia/Murat, T5b): additive — never drop a pre-existing
    key; voice nests at ``voice_selection.selected_voice_id`` (siblings preserved);
    unknown keys fail loud BEFORE any mutation.
    """
    allowed = _SELECTABLE_KEYS_BY_GATE.get(gate_id, frozenset())
    unknown = sorted(set(selection) - allowed)
    if unknown:
        raise UnknownSelectionKeyError(
            f"select verdict for {gate_id} carried non-selectable key(s) {unknown}; "
            f"allowed: {sorted(allowed)}"
        )
    merged = dict(existing)
    if "selected_voice_id" in selection:
        voice_selection = dict(merged.get("voice_selection") or {})
        voice_selection["selected_voice_id"] = selection["selected_voice_id"]
        voice_selection.setdefault("operator_id", "operator-select")
        merged["voice_selection"] = voice_selection
        # top-level mirror (enrique falls back to payload['selected_voice_id'])
        merged["selected_voice_id"] = selection["selected_voice_id"]
    if "selected_variant_id" in selection:
        merged["selected_variant_id"] = selection["selected_variant_id"]
    if "slide_variant_selections" in selection:
        merged["slide_variant_selections"] = selection["slide_variant_selections"]
    return merged


def _selected_variant_id_from_run_state(run_state: RunState) -> str | None:
    raw = run_state.cache_state.cache_prefix if run_state.cache_state else None
    if not raw:
        return None
    try:
        envelope = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(envelope, dict):
        raise VariantSelectionError("cache_prefix JSON envelope must be an object")
    selected = envelope.get("selected_variant_id")
    if selected is None:
        return None
    if not isinstance(selected, str) or not selected.strip():
        raise VariantSelectionError(
            "selected_variant_id must be a non-empty deck-wide string when present"
        )
    return selected.strip()


def _slide_variant_selections_from_run_state(run_state: RunState) -> dict[str, str] | None:
    raw = run_state.cache_state.cache_prefix if run_state.cache_state else None
    if not raw:
        return None
    try:
        envelope = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(envelope, dict):
        raise VariantSelectionError("cache_prefix JSON envelope must be an object")
    selections = envelope.get("slide_variant_selections")
    if selections is None:
        return None
    if not isinstance(selections, dict) or not selections:
        raise VariantSelectionError(
            "slide_variant_selections must be a non-empty {slide_id: variant} object"
        )
    return {str(key): str(value).strip().upper() for key, value in selections.items()}


def _apply_per_slide_variant_selection(
    production_envelope: ProductionEnvelope,
    run_state: RunState,
) -> ProductionEnvelope:
    """Resolve the per-slide A/B picks (Storyboard A) to one row per slide before perception.

    Fail-loud total-coverage (Winston/Murat): every original slide must keep exactly one row
    matching the operator's per-slide pick; a missing/extra/unknown choice HALTS naming the
    slide — never silently defaults. No-op when no per-slide map is set (legacy path).
    """
    selections = _slide_variant_selections_from_run_state(run_state)
    if selections is None:
        return production_envelope
    gary = production_envelope.latest_for_specialist("gary")
    rows = gary.output.get("gary_slide_output") if gary is not None else None
    if not isinstance(rows, list):
        # Mine-next T2 recover ``reenter_at_node=07`` drops Gary before the
        # continuation walk starts. Variant picks stay in run_state; apply
        # after Gary re-dispatches (see ``_dispatch_specialist_at_node``).
        # Raising here made upstream re-entry unrecoverable.
        return production_envelope
    variants_by_slide: dict[str, set[str]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        slide_id = str(row.get("slide_id") or "").strip()
        if slide_id:
            variants_by_slide.setdefault(slide_id, set()).add(
                str(row.get("dispatch_variant") or "A")
            )
    try:
        validate_selections(selections, variants_by_slide)
    except SlideVariantSelectionError as exc:
        raise VariantSelectionError(str(exc)) from exc
    filtered = [
        row
        for row in rows
        if isinstance(row, dict)
        and str(row.get("dispatch_variant") or "A")
        == selections.get(str(row.get("slide_id") or "").strip())
    ]
    by_slide: dict[str, int] = {}
    for row in filtered:
        slide_id = str(row.get("slide_id") or "").strip()
        by_slide[slide_id] = by_slide.get(slide_id, 0) + 1
    violations = sorted(slide_id for slide_id, count in by_slide.items() if count != 1)
    if violations:
        raise VariantSelectionError(
            "per-slide selection must leave exactly one row per slide; "
            f"violations={violations}"
        )
    missing = sorted(set(variants_by_slide) - set(by_slide))
    if missing:
        raise VariantSelectionError(f"per-slide selection dropped slide(s) entirely: {missing}")
    output = dict(gary.output)
    output["gary_slide_output"] = filtered
    replacement = gary.model_copy(
        update={"output": output, "output_digest": compute_output_digest(output)}
    )
    contributions = tuple(
        replacement if contribution is gary else contribution
        for contribution in production_envelope.contributions
    )
    return production_envelope.model_copy(update={"contributions": contributions})


def _apply_variant_selection(
    production_envelope: ProductionEnvelope,
    run_state: RunState,
) -> ProductionEnvelope:
    """Per-slide selection (Storyboard A) takes precedence; deck-wide is the legacy fallback."""
    if _slide_variant_selections_from_run_state(run_state) is not None:
        return _apply_per_slide_variant_selection(production_envelope, run_state)
    return _apply_deckwide_variant_selection(production_envelope, run_state)


def _apply_deckwide_variant_selection(
    production_envelope: ProductionEnvelope,
    run_state: RunState,
) -> ProductionEnvelope:
    selected_variant_id = _selected_variant_id_from_run_state(run_state)
    if selected_variant_id is None:
        return production_envelope
    gary = production_envelope.latest_for_specialist("gary")
    rows = gary.output.get("gary_slide_output") if gary is not None else None
    if not isinstance(rows, list):
        # Same reenter-at-07 deferral as the per-slide path.
        return production_envelope
    original_slide_ids = {
        slide_id
        for row in rows
        if isinstance(row, dict)
        for slide_id in [str(row.get("slide_id") or "").strip()]
        if slide_id
    }
    filtered = [
        row
        for row in rows
        if isinstance(row, dict)
        and str(row.get("dispatch_variant") or "A") == selected_variant_id
    ]
    if not filtered:
        raise VariantSelectionError(
            f"selected_variant_id={selected_variant_id!r} matched zero Gary rows"
        )
    by_slide: dict[str, int] = {}
    for row in filtered:
        slide_id = str(row.get("slide_id") or "").strip()
        if not slide_id:
            raise VariantSelectionError("selected Gary variant row has no slide_id")
        by_slide[slide_id] = by_slide.get(slide_id, 0) + 1
    missing = sorted(original_slide_ids - set(by_slide))
    if missing:
        raise VariantSelectionError(
            "selected variant must retain exactly one row for every original slide_id; "
            f"missing={missing}"
        )
    duplicates = sorted(slide_id for slide_id, count in by_slide.items() if count != 1)
    if duplicates:
        raise VariantSelectionError(
            "selected variant must leave exactly one row per slide_id; "
            f"violations={duplicates}"
        )
    output = dict(gary.output)
    output["gary_slide_output"] = filtered
    replacement = gary.model_copy(
        update={
            "output": output,
            "output_digest": compute_output_digest(output),
        }
    )
    contributions = tuple(
        replacement if contribution is gary else contribution
        for contribution in production_envelope.contributions
    )
    return production_envelope.model_copy(update={"contributions": contributions})


def _apply_verdict_to_run_state(
    run_state: RunState,
    verdict: OperatorVerdict,
) -> RunState:
    if verdict.verb == "edit":
        return run_state.model_copy(
            update={
                "cache_state": CacheState(
                    cache_prefix=json.dumps(verdict.edit_payload, sort_keys=True),
                    entries_count=1,
                    last_invalidated_at=None,
                )
            }
        )
    if verdict.verb == "select":
        raw = run_state.cache_state.cache_prefix if run_state.cache_state else None
        try:
            existing = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            existing = None
        if not isinstance(existing, dict):
            raise SelectionBindingError(
                f"select verdict for {verdict.gate_id} has no decodable envelope to "
                f"overlay onto (cache_prefix missing/unparseable)"
            )
        merged = _merge_selection_into_envelope(
            existing, verdict.edit_payload or {}, verdict.gate_id
        )
        return run_state.model_copy(
            update={
                "cache_state": CacheState(
                    cache_prefix=json.dumps(merged, sort_keys=True),
                    entries_count=1,
                    last_invalidated_at=None,
                )
            }
        )
    # approve / reject: envelope is a no-op (verdict drives run-state/gate status only)
    return run_state


def _apply_g0r_ratification(*, run_dir: Path) -> Path | None:
    """G0-S3 ratify-gate #2 side-effect: advance refined->ratified + completeness assert.

    Runs ONLY from the operator-verdict path (G0R, non-reject). The model NEVER
    auto-ratifies. Advances each refined LO to ``ratified`` (``actor="operator"``),
    runs the AC-S3-5 completeness hard-assert (ACCESS + ASSESSMENT-PRESENCE — a
    thin/gap verdict PASSES; an unreachable source or absent adequacy is RED), and
    writes the ratified LOs to ``<run_dir>/ratified-los.json`` as evidence.
    """
    from app.marcus.lesson_plan.irene_refinement import assert_completeness, ratify_refined_los

    result = irene_refinement_wiring.load_refinement_full(run_dir)
    if result is None:
        # No frozen refinement on disk — nothing to ratify (the brick produced no
        # refined set; e.g. an asleep-brick continuation). No-op, not an error.
        return None

    surviving = [lo for lo in result.refined_los if lo.status == "refined"]
    # ACCESS + ASSESSMENT-PRESENCE assert (per the enumerated/typed source set).
    enrichment = g0_enrichment_wiring.load_enrichment_result(run_dir) or {}
    # Provisional-LO source_refs point at the enumerated FILE id (a component's
    # parent_source_id), which is what the ACCESS check resolves against. Components
    # are the typed deliverables; their parent files are the A6 enumeration unit.
    enumerated_source_ids = {
        str(comp.get("parent_source_id"))
        for comp in enrichment.get("typed_components", [])
        if comp.get("parent_source_id")
    }
    assert_completeness(
        refined_los=surviving,
        ledger=result.ledger,
        enumerated_source_ids=enumerated_source_ids,
    )
    ratified = ratify_refined_los(surviving)
    ratified_path = run_dir / "ratified-los.json"
    _write_json(
        ratified_path,
        {"ratified_los": [lo.model_dump(mode="json") for lo in ratified]},
    )
    return ratified_path


def _record_cost(
    *,
    trial_id: UUID,
    runs_root: Path,
    trace_root: Any | None,
    allow_offline_cost_report: bool,
) -> Path:
    if trace_root is not None:
        report = measure_trial_cost(str(trial_id), trace_root=trace_root, history=[])
    elif allow_offline_cost_report:
        report = _fallback_cost_report(str(trial_id))
    else:
        report = _fallback_cost_report(str(trial_id))
    return record_trial_cost_report(str(trial_id), report, runs_root=runs_root)


def _merge_artifact_paths(
    existing: list[Path], *candidates: Path | None
) -> list[Path]:
    """Append candidates in order, dropping Nones and duplicates.

    Multi-gate pause-and-resume re-emits stable-path artifacts
    (checkpoint.json, run_summary.yaml, the cost report) at every pause;
    without dedupe the envelope accumulates one duplicate per crossed gate.
    """
    merged: list[Path] = []
    for path in (*existing, *candidates):
        if path is None:
            continue
        candidate = Path(path)
        if candidate not in merged:
            merged.append(candidate)
    return merged


def _has_production_evidence(
    *,
    graph_step_completed: bool,
    specialist_calls: int,
    allow_offline_cost_report: bool,
) -> bool:
    return (
        graph_step_completed
        and specialist_calls > 0
        and _has_live_openai()
        and _has_langsmith_env()
        and not allow_offline_cost_report
    )


def _active_node_handler(compiled_graph: Any, node_id: str) -> Any:
    return compiled_graph.nodes[node_id].runnable.func


def apply_llm_execution_mode_overlay(
    *,
    specialist_id: str,
    run_state: RunState,
    runner_payload: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Inject Batch mode into vision runner payload only when opted in.

    Winston B6-land MUST: overlay ``llm_execution_mode=batch`` only for
    ``specialist_id == "vision"`` and only when RunState mode is exactly
    ``batch``. Do **not** overlay ``realtime`` (missing key == realtime in B2).
    Non-vision payloads must never carry the key from this seam.
    """

    if specialist_id != "vision":
        if runner_payload and "llm_execution_mode" in runner_payload:
            return {
                key: value
                for key, value in runner_payload.items()
                if key != "llm_execution_mode"
            }
        return runner_payload
    if run_state.llm_execution_mode != "batch":
        return runner_payload
    return {**(runner_payload or {}), "llm_execution_mode": "batch"}


def _runner_payload_for_specialist(
    *,
    specialist_id: str,
    directive_path: Path | None,
    bundle_dir: Path | None,
    gate_code: str | None = None,
    production_envelope: ProductionEnvelope | None = None,
    runs_root: Path | None = None,
    trial_id: UUID | None = None,
) -> dict[str, Any] | None:
    """Build runner_supplied_payload for specialists needing runner-side context.

    Story 7a.1 / A-R3 Option A: Texas receives directive/bundle paths when
    directive composition has run.

    Trial-3 finding #10 (2026-06-11): Quinn-R receives the dispatching
    node's ``gate_code`` as ``gate_id`` (its _act selects its body from the
    payload; production dispatch previously supplied no gate context).

    S4 (party review 2026-06-12, manifest-edge-key-projection-s4 LANDED):
    content keys now flow through manifest ``dependency_projections`` — the
    S3 bridge spread is retired (its tombstone test was updated
    deliberately, per Winston S3-A). This seam carries RUNNER CONTEXT only:
    Texas's directive/bundle paths, Quinn-R's gate_id, Gary's run-dir
    ``export_dir``, CD's ``directive_projection``. Content delivery via the
    seam is forbidden — the adapter collision guard refuses any seam key
    that a projection or dependency also delivers.

    Canonical-arc S1 (D2, 2026-07-06): CD receives ``directive_projection``
    ``{gamma_settings (verbatim), styleguide_picker_provenance (verbatim,
    if present), directive_digest (sha256 of the directive file bytes)}`` at
    the §4.75 dispatch site. Directive-derived styleguide context is
    CHARTERED runner context per the gary ``gamma_settings`` precedent
    above — not content delivery (the corpus/content plane still travels
    exclusively through dependencies/projections). CD never opens the
    directive file; the deterministic neck emits the ``styleguide_resolution``
    audit block from this projection alone.

    Canonical-arc S3 (D1/D4, F-802 option-(i) ruling): gary additionally
    receives three parity-context keys as CHARTERED runner context —
    ``cd_styleguide_resolution`` (the committed block verbatim from the
    envelope's LATEST cd contribution, the same ``latest_for_specialist``
    selector §06 uses; ``None`` when the cd contribution is absent at
    dispatch time or predates S1 — legacy tolerance, never a raise),
    ``directive_digest`` (sha256 of the SAME bytes the gamma-settings parse
    read — read-once, no TOCTOU), and ``trial_start_directive_digest``
    (from ``run_dir/"trial-start.json"``'s ``directive_digest`` key per
    F-801 — NOT run.json, which is the ProductionTrialEnvelope and carries
    no digest field; ``None`` when the file or key is absent). Same data
    family as ``gamma_settings``/``directive_projection`` — observability
    context for Gary's shadow-parity audit, not content delivery.

    Other specialists receive None.
    """
    if specialist_id == "texas" and directive_path is not None and bundle_dir is not None:
        return {
            "directive_path": directive_path.as_posix(),
            "bundle_dir": bundle_dir.as_posix(),
        }
    # The walker passes the CANONICAL id ("quinn_r" via SPECIALIST_ALIASES),
    # not the manifest spelling ("quinn-r") — match both; the hyphen form
    # cost a second live ModeMismatchError('') crash on 2026-06-11.
    if specialist_id in {"quinn_r", "quinn-r"} and gate_code:
        return {"gate_id": gate_code}
    if specialist_id == "gary" and runs_root is not None and trial_id is not None:
        run_dir = runs_root / str(trial_id)
        payload: dict[str, Any] = {
            "export_dir": (run_dir / "exports" / "gary").as_posix()
        }
        # Canonical-arc S3 D4: read-once — settings AND digest come from the
        # SAME directive bytes (the :852-854 sha256 pattern; no TOCTOU).
        gamma_settings, directive_digest = _gamma_settings_and_digest_from_directive(
            directive_path
        )
        if gamma_settings is not None:
            payload["gamma_settings"] = gamma_settings
        # Canonical-arc S3 D1 (F-802 option (i)): CD's committed
        # styleguide_resolution block travels VERBATIM as chartered runner
        # context, sourced from the envelope's latest cd contribution —
        # None when absent-at-dispatch-time or pre-S1 (legacy; NEVER a
        # raise, so rewind-recovered golden bundles never false-fail).
        cd_block: Any = None
        if production_envelope is not None:
            cd_contribution = production_envelope.latest_for_specialist("cd")
            if cd_contribution is not None and isinstance(cd_contribution.output, dict):
                cd_block = cd_contribution.output.get("styleguide_resolution")
        # T11 P4(b): deepcopy at capture — the payload value must never alias
        # the live envelope contribution dict (the receipt seam is an
        # attestation of dispatch-time state, not a live pointer).
        payload["cd_styleguide_resolution"] = (
            copy.deepcopy(cd_block) if cd_block is not None else None
        )
        payload["directive_digest"] = directive_digest
        # F-801: the trial-start attestation lives ONLY in trial-start.json
        # (trial.py:536); absent (legacy runs, start-walk harness contexts)
        # => honest None (the comparator treats it as not-comparable).
        payload["trial_start_directive_digest"] = _trial_start_directive_digest(run_dir)
        return payload
    # Canonical-arc S1 (D2): CD's §4.75 directive_projection — the ONE branch
    # both walks reach through the shared _dispatch_specialist_at_node (F-203
    # wiring altitude: never per-walk wiring). gamma_settings verbatim per the
    # gary precedent above; digest via the :852-854 sha256 pattern. No
    # directive on disk ⇒ None ⇒ CD's neck emits no_picks_at_authoring.
    # Remediation T1 (review 2026-07-06, HIGH): the directive is read ONCE —
    # bytes → sha256 → decode/parse of the SAME bytes for settings AND
    # provenance (no TOCTOU) — and EVERY failure (unreadable file, non-UTF-8
    # bytes, malformed YAML) raises into the SpecialistDispatchError family
    # (`cd.directive.*` tags) so BOTH walkers' `except SpecialistDispatchError`
    # routes it through `_pause_at_error` recoverably (the
    # AssetResolutionError / CoverageAssuranceError precedent) instead of
    # crashing the walk un-persisted.
    if specialist_id == "cd" and directive_path is not None and directive_path.is_file():
        try:
            directive_bytes = directive_path.read_bytes()
        except OSError as exc:
            raise SpecialistDispatchError(
                f"cd directive_projection: directive at {directive_path} is "
                f"unreadable: {exc}",
                tag="cd.directive.unreadable",
            ) from exc
        try:
            directive_text = directive_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise SpecialistDispatchError(
                f"cd directive_projection: directive at {directive_path} is "
                f"not valid UTF-8: {exc}",
                tag="cd.directive.unreadable",
            ) from exc
        try:
            loaded = yaml.safe_load(directive_text) or {}
        except yaml.YAMLError as exc:
            raise SpecialistDispatchError(
                f"cd directive_projection: directive at {directive_path} is "
                f"not parseable YAML: {exc}",
                tag="cd.directive.malformed",
            ) from exc
        if not isinstance(loaded, dict):
            # Tolerant like _gamma_settings_from_directive: a parseable-but-
            # non-mapping directive projects digest + null picks (the neck
            # emits an honest no_picks_at_authoring), matching pre-T1 behavior.
            loaded = {}
        raw_settings = loaded.get("gamma_settings")
        projection: dict[str, Any] = {
            "gamma_settings": (
                [dict(item) for item in raw_settings if isinstance(item, dict)]
                if isinstance(raw_settings, list)
                else None
            ),
            "directive_digest": hashlib.sha256(directive_bytes).hexdigest(),
        }
        provenance_block = loaded.get("styleguide_picker_provenance")
        if isinstance(provenance_block, dict):
            projection["styleguide_picker_provenance"] = dict(provenance_block)
        return {"directive_projection": projection}
    # P5-S2 Consumer A (Step 6): the narration node ("irene" == Pass-2; Pass-1 is
    # the separate "irene-pass1" specialist) gets the orchestrator-projected
    # per-SLIDE role-derived voice seed table. ORCHESTRATOR-SIDE projection (Winston
    # A1/A3): load the frozen card via the existing load_enrichment_result (no third
    # loader), match narration components → roles → the frozen voice map. AND-gated
    # by the narration flag + card presence; flag-OFF / card-absent ⇒ None ⇒ the
    # runner adds no key ⇒ the irene cache_prefix is byte-identical to today. The
    # specialist re-keys this per-slide table onto its own segment ids (the segment
    # manifest does not exist until after Pass-2, so the orchestrator cannot key by
    # segment id — pinned slide-ordinal join, Winston A4).
    if (
        specialist_id == "irene"
        and runs_root is not None
        and trial_id is not None
        and voice_direction_active()
    ):
        card = g0_enrichment_wiring.load_enrichment_result(runs_root / str(trial_id))
        seeds_by_slide = enrichment_consumption.project_role_derived_voice_by_slide(card)
        if seeds_by_slide:
            # Story enhanced-vo.1 (Slice 0): thread ONLY the seed table, keyed by
            # SOURCE-deck slide ordinal (== the specialist's ``slide_key``). The
            # specialist now resolves each FINAL segment to its TRUE source slide via
            # the deterministic lineage (slide_briefs.source_ref + lesson_plan
            # plan_units) and joins by slide_key IDENTITY — so the legacy
            # ``source_slide_ordinals`` EDGE-1 divergence guard (which FAILED OPEN on
            # every clustered deck) is retired and no longer threaded. NOTE: if irene
            # ever gains a baseline runner payload, MERGE this key rather than
            # returning a fresh dict.
            return {
                "role_derived_voice_by_slide": {
                    "by_slide": seeds_by_slide,
                }
            }
        return None
    # Motion data-plane isolation (Leg-2, concierge-production-substrate 2026-06-30):
    # DECOUPLE two previously-fused concerns.
    #  (1) bundle_path roots kira's motion/ receipts + downloaded .mp4 under the
    #      PER-RUN dir. This is a per-run ISOLATION INVARIANT and is threaded
    #      UNCONDITIONALLY whenever runs_root + trial_id are present — otherwise
    #      kira's boundary (`payload.get("bundle_path") or DEFAULT_BUNDLE_PATH`)
    #      silently falls back to the process-global REPO_ROOT/runs/kira-motion,
    #      cross-contaminating concurrent real SPOC runs' receipts + mp4s.
    #  (2) motion_plan_path is the vestigial seed/replay OVERRIDE — now that the
    #      in-graph 07D.5 motion_planner has landed it is normally absent, but it
    #      is PRESERVED for seed/replay: threaded ONLY when KIRA_MOTION_PLAN_PATH
    #      is set. Neither key collides with 07E's dependency (upstream_output).
    # Fail-loud precondition unchanged: a non-run caller (runs_root/trial_id None)
    # returns None and NEVER re-defaults to the global dir.
    # Leg-C (gamma-styleguide): irene-pass1 receives the resolved scripted
    # ``min_cluster_floor`` (RUNNER CONTEXT — a resolved run-config scalar, peer of
    # Gary's ``gamma_settings``). The orchestrator reads the styleguide SSOT yaml
    # DIRECTLY (no app/specialists/gary import). Absent styleguide / absent scripted ->
    # no key (clean; no None-leak). ``min_cluster_floor`` collides with no projection
    # or dependency, so the adapter collision-guard passes.
    # F1 (live-diagnosed 2026-07-01): the walk canonicalizes BEFORE this call — the
    # manifest compiler stamps handler.__production_specialist_id__ with
    # _canonical_specialist_id(...) via SPECIALIST_ALIASES ("irene-pass1" ->
    # "irene_pass1", app/manifest/compiler.py:42-45/:163), and both walkers pass
    # that canonical id down to this seam. A hyphen-only match returned None on
    # EVERY real dispatch (instrumented live proof), silently un-threading the
    # floor. Match both forms — same lesson the quinn_r branch above learned
    # on 2026-06-11.
    if specialist_id in {"irene-pass1", "irene_pass1"}:
        # Merge runner-context keys (floor + optional planning_context). Never
        # leak explicit None values; absent framing → omit the key entirely.
        irene_payload: dict[str, Any] = {}
        floor = _min_cluster_floor_from_directive(directive_path)
        if floor is not None:
            irene_payload["min_cluster_floor"] = floor
        if runs_root is not None and trial_id is not None:
            # Lazy import: keep runner free of lesson_plan import cycles at module load.
            from app.marcus.lesson_plan.planning_context import (
                PlanningContextError,
                load_planning_context,
            )

            try:
                planning_ctx = load_planning_context(runs_root / str(trial_id))
            except PlanningContextError as exc:
                # BH-1 / ECH-03: wrap as SpecialistDispatchError so both walkers
                # route through recoverable _pause_at_error (not un-persisted crash).
                # Use the module-level import — a local re-import here would shadow
                # SpecialistDispatchError for the whole function (UnboundLocalError
                # on the earlier cd.directive.* raise sites).
                raise SpecialistDispatchError(
                    f"irene_pass1 planning_context load failed: {exc}",
                    tag="irene_pass1.planning_context.malformed",
                ) from exc
            if planning_ctx is not None:
                irene_payload["planning_context"] = planning_ctx.to_payload_dict()
        return irene_payload or None
    if specialist_id == "kira":
        if runs_root is None or trial_id is None:
            return None
        kira_payload: dict[str, Any] = {
            "bundle_path": (runs_root / str(trial_id)).as_posix(),
        }
        plan_path = os.environ.get("KIRA_MOTION_PLAN_PATH")
        if plan_path:
            kira_payload["motion_plan_path"] = plan_path
        return kira_payload
    return None


def _scripted_min_cluster_floor_for_record(record: Any) -> int | None:
    """Read ``scripted.min_cluster_floor`` off ONE styleguide record (SSOT-direct).

    Tolerant of a single-dict or list-of-entries ``scripted`` block. A malformed value
    is NOT threaded (returns None) — the offline write-gate RED-gates it; the runner
    never threads a bad floor.
    """
    if not isinstance(record, dict):
        return None
    block = record.get("scripted")
    if isinstance(block, dict):
        entries = [block]
    elif isinstance(block, list):
        entries = [e for e in block if isinstance(e, dict)]
    else:
        return None
    for entry in entries:
        if str(entry.get("class") or "").strip() != _SCRIPTED_MIN_CLUSTER_FLOOR_CLASS:
            continue
        value = entry.get("value")
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            # P7 (Leg-C review): a PRESENT-but-malformed floor is NOT silently dropped.
            # WARN loudly (the offline write-gate RED-gates it; this is defense in depth
            # so a bad SSOT edit that slipped the gate cannot vanish without a trace).
            LOGGER.warning(
                "scripted min_cluster_floor present but malformed (value=%r); "
                "not threading it — the styleguide SSOT should have been RED-gated "
                "by validate_gamma_style_guides.py",
                value,
            )
            return None
        return value
    return None


def _min_cluster_floor_from_directive(directive_path: Path | None) -> int | None:
    """Resolve the scripted ``min_cluster_floor`` bound by the directive's styleguide(s).

    Reads the per-variant ``gamma_settings[].styleguide`` name(s) from the directive, then
    resolves each name's ``scripted.min_cluster_floor`` from the styleguide SSOT yaml
    DIRECTLY (no app/specialists/gary import). When more than one bound styleguide
    declares a floor, the STRICTEST (max) is threaded — Pass-1 clustering is shared
    across A/B variants, and over-honoring is bounded by the split-only byte-identity
    guard + the SOFT-floor source-content veto (under-honoring would silently drop a
    multi-beat style's identity). Absent styleguide / absent scripted -> None.
    """
    if directive_path is None or not directive_path.is_file():
        return None
    loaded = yaml.safe_load(directive_path.read_text(encoding="utf-8")) or {}
    if not isinstance(loaded, dict):
        return None
    raw = loaded.get("gamma_settings")
    if not isinstance(raw, list):
        return None
    names = [
        item["styleguide"].strip()
        for item in raw
        if isinstance(item, dict)
        and isinstance(item.get("styleguide"), str)
        and item["styleguide"].strip()
    ]
    if not names:
        return None
    if not GAMMA_STYLE_GUIDES_SSOT_PATH.is_file():
        return None
    ssot = yaml.safe_load(GAMMA_STYLE_GUIDES_SSOT_PATH.read_text(encoding="utf-8")) or {}
    guides = ssot.get("style_guides") if isinstance(ssot, dict) else None
    if not isinstance(guides, dict):
        return None
    floors = [
        floor
        for name in names
        if (floor := _scripted_min_cluster_floor_for_record(guides.get(name))) is not None
    ]
    if not floors:
        return None
    return max(floors)


def _gamma_settings_and_digest_from_directive(
    directive_path: Path | None,
) -> tuple[list[dict[str, Any]] | None, str | None]:
    """Read the directive ONCE: settings and sha256 from the SAME bytes.

    Canonical-arc S3 D4 refactor of ``_gamma_settings_from_directive`` (which
    remains a behavior-identical thin wrapper): the parity comparator's
    ``directive_digest`` must attest exactly the bytes the gamma-settings
    parse read (no TOCTOU). Directive absent ⇒ ``(None, None)``; present but
    settings-less/non-mapping ⇒ ``(None, digest)``.
    """
    if directive_path is None or not directive_path.is_file():
        return None, None
    directive_bytes = directive_path.read_bytes()
    digest = hashlib.sha256(directive_bytes).hexdigest()
    loaded = yaml.safe_load(directive_bytes.decode("utf-8")) or {}
    if not isinstance(loaded, dict):
        return None, digest
    raw = loaded.get("gamma_settings")
    if raw is None:
        return None, digest
    if not isinstance(raw, list):
        return None, digest
    return [dict(item) for item in raw if isinstance(item, dict)], digest


def _gamma_settings_from_directive(directive_path: Path | None) -> list[dict[str, Any]] | None:
    return _gamma_settings_and_digest_from_directive(directive_path)[0]


def _trial_start_directive_digest(run_dir: Path) -> str | None:
    """The trial-start directive attestation (F-703 third digest; F-801).

    Sourced from ``run_dir/"trial-start.json"``'s ``directive_digest`` key —
    the ONLY place `start_trial` persists it (trial.py:533/536; run.json is
    the ProductionTrialEnvelope and has no digest field). Total: an absent
    file/key (legacy runs, harness contexts) or an unreadable/malformed file
    yields ``None`` (WARN-logged) — parity context must never block dispatch.
    """
    trial_start_path = run_dir / "trial-start.json"
    if not trial_start_path.is_file():
        return None
    try:
        payload = json.loads(trial_start_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        LOGGER.warning(
            "trial-start.json at %s is unreadable/malformed (%s); parity "
            "receipt will record the trial-start digest as not-comparable",
            trial_start_path,
            exc,
        )
        return None
    if not isinstance(payload, dict):
        # T11 P5: parseable-but-non-mapping content is malformed — WARN as the
        # docstring promises (still None; parity context never blocks dispatch).
        LOGGER.warning(
            "trial-start.json at %s is not a JSON object (got %s); parity "
            "receipt will record the trial-start digest as not-comparable",
            trial_start_path,
            type(payload).__name__,
        )
        return None
    digest = payload.get("directive_digest")
    if isinstance(digest, str) and digest:
        return digest
    # `directive_digest: null` is a LEGITIMATE produced shape (single-file
    # trials write it; E4) and an ABSENT key is legacy — both stay silent.
    # T11 P5: any OTHER present value (non-string / empty string) is a
    # producer-side type regression and must be operator-visible.
    if "directive_digest" in payload and digest is not None:
        LOGGER.warning(
            "trial-start.json at %s carries a non-string/empty "
            "directive_digest (%r) — producer-side type regression; parity "
            "receipt will record the trial-start digest as not-comparable",
            trial_start_path,
            digest,
        )
    return None


# (Remediation T1: the former `_picker_provenance_from_directive` helper was
# folded into the cd branch of `_runner_payload_for_specialist` — provenance
# now comes from the SAME single guarded directive read as settings + digest,
# so a separate tolerant re-read helper would misstate real seam behavior.)


# BETA S0.4 flake budget (T5a-F2): dispatch tags that represent LLM-output
# VARIANCE (a re-roll plausibly succeeds), not deterministic substrate defects.
# Only these auto-retry; everything else fails loud immediately. Tunable by
# party-mode as new variance points are observed across trials.
_RETRYABLE_DISPATCH_TAGS: frozenset[str] = frozenset(
    {
        "irene.pass2.slide-join-failed",
        # Gamma text-mode=generate intermittently re-titles a slide so the bijective
        # brief<->page title match fails for one variant; a re-roll matches (observed on
        # variant B slide-06, 2026-06-24). LLM-variance class — auto-retry like Pass-2.
        "gamma.export.brief-unmatched",
        # Desmond LLM intermittently omits the exact ``## Automation Advisory``
        # heading (Tejal P4 fullwalk 2026-07-10). Re-roll is the right fix once
        # HandoffParseError is SpecialistDispatchError (recoverable pause + retry).
        "handoff.parsed.advisory-missing",
    }
)
_MAX_DISPATCH_RETRIES = 3  # total attempts = 1 + 3; irene needed 3 re-rolls in T5a-rerun


def _invoke_specialist_with_retry(adapter: Any, invoke_kwargs: dict[str, Any], node_id: str) -> Any:
    """Invoke a specialist with bounded AUTOMATIC retry for LLM-variance tags.

    BETA S0.4 flake-budget (T5a-F2 fix): a known LLM-output-variance failure
    (e.g. irene pass-2 perception_source join) is absorbed in-process by
    re-asking the LLM, instead of forcing an operator-manual `trial recover`
    (which fails the "error-free" criterion). Each retry re-dispatches fresh (a
    raised attempt records no contribution). A non-retryable tag re-raises
    immediately — fail-loud is preserved for deterministic substrate defects.
    """
    attempt = 0
    while True:
        try:
            return adapter.invoke_specialist(**invoke_kwargs)
        except SpecialistDispatchError as exc:
            retryable = getattr(exc, "tag", None) in _RETRYABLE_DISPATCH_TAGS
            if retryable and attempt < _MAX_DISPATCH_RETRIES:
                attempt += 1
                LOGGER.warning(
                    "retryable dispatch variance [%s] at node %s — auto-retry %d/%d",
                    exc.tag,
                    node_id,
                    attempt,
                    _MAX_DISPATCH_RETRIES,
                )
                continue
            raise


def _operator_selected_voice(run_state: Any) -> str | None:
    """The operator's G4A-selected voice id from the run_state envelope, if any.

    Set as a top-level mirror by the `select` verdict merge (T5b); absent until
    the operator actually picks, so threading it (T5a-F3 repair) is a no-op for
    runs/nodes where no voice was selected.
    """
    cache_state = getattr(run_state, "cache_state", None)
    raw = getattr(cache_state, "cache_prefix", None) if cache_state is not None else None
    if not raw:
        return None
    try:
        env = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None
    if isinstance(env, dict) and env.get("selected_voice_id"):
        return str(env["selected_voice_id"])
    return None


def _effective_quinn_r_gate_code(node: NodeSpec, manifest: Any) -> str | None:
    """Resolve the gate_code that selects Quinn-R's body at an evaluation node.

    Quinn-R's _act picks its mode (variant/pre/g5/...) from the dispatched
    gate_id, which is the node's ``gate_code``. Arc-1a (2026-06-18) split the
    woken HIL gate_code off the Quinn-R evaluation node (G2B moved from 07B onto
    the content-free ``07B-gate``) to keep the wake pack-neutral — which left
    node 07B with no gate_id and crashed Quinn-R with ``ModeMismatchError('')``.
    Recover it from the CONTENT-FREE gate node (``specialist_id is None``)
    inserted immediately after this node — distinguishing ``07B-gate``/G2B from
    a sibling CONTENT gate that also follows (``07C``/G2C). Nodes that still
    carry their own gate_code (e.g. 07C) are returned unchanged.
    """
    if node.gate_code:
        return node.gate_code
    for candidate in manifest.nodes:
        if (
            candidate.gate_code
            and candidate.specialist_id is None
            and getattr(candidate, "insertion_after", None) == node.id
        ):
            return candidate.gate_code
    return None


def _should_invoke_pre_gate_marcus(*, allow_offline_cost_report: bool) -> bool:
    api_key = os.getenv("OPENAI_API_KEY")
    return bool(
        api_key
        and not api_key.startswith("sk-test")
        and not api_key.startswith("sk-fake")
        and not allow_offline_cost_report
    )


def _pre_gate_slot_values(
    *,
    trial_id: UUID,
    gate_id: str,
    production_envelope: ProductionEnvelope,
    pending_nodes: list[str],
    artifact_paths: list[Path],
) -> dict[str, Any]:
    return {
        "trial_id": str(trial_id),
        "gate_id": gate_id,
        "upstream_contributions": [
            contribution.model_dump(mode="json")
            for contribution in production_envelope.contributions
        ],
        "pending_nodes": pending_nodes,
        "artifact_paths": [path.as_posix() for path in artifact_paths],
    }


def _invoke_pre_gate_marcus_for_gate(
    *,
    gate_id: str,
    trial_id: UUID,
    production_envelope: ProductionEnvelope,
    pending_nodes: list[str],
    artifact_paths: list[Path],
    allow_offline_cost_report: bool,
) -> PreFillProposal | None:
    if not _should_invoke_pre_gate_marcus(
        allow_offline_cost_report=allow_offline_cost_report
    ):
        return None
    slot_values = _pre_gate_slot_values(
        trial_id=trial_id,
        gate_id=gate_id,
        production_envelope=production_envelope,
        pending_nodes=pending_nodes,
        artifact_paths=artifact_paths,
    )
    return pre_gate_marcus.invoke_pre_gate_marcus(
        gate_id=gate_id,
        slot_values=slot_values,
    )


def _pause_at_gate(
    *,
    gate_id: str,
    node_id: str,
    node_index: int,
    manifest: Any,
    trial_id: UUID,
    operator_id: str,
    envelope: ProductionTrialEnvelope,
    production_envelope: ProductionEnvelope,
    run_state: RunState,
    child_runs: list[SimpleNamespace],
    trace_metadata: dict[str, str],
    specialist_calls: int,
    graph_step_completed: bool,
    manifest_path: Path,
    runs_root: Path,
    allow_offline_cost_report: bool,
    max_specialist_calls: int,
    directive_path: Path | None,
    bundle_dir: Path | None,
) -> ProductionTrialEnvelope:
    """Pause the trial at ``gate_id``: draft, card, checkpoint, persist, return.

    Extracted verbatim from the run_production_trial gate branch (Trial-3
    attempt-3 fix, 2026-06-11) so BOTH walkers share one pause implementation.
    The resume walker previously had no pause path at all — it raised
    GateBypassError at every gate in live mode, making any live trial unable
    to advance from one gate to the next (pause logic existed once, was wired
    once — the A23 fork pattern at function granularity).
    """
    pending = [item.id for item in manifest.nodes[node_index + 1 :]]
    pre_fill = _invoke_pre_gate_marcus_for_gate(
        gate_id=gate_id,
        trial_id=trial_id,
        production_envelope=production_envelope,
        pending_nodes=pending,
        artifact_paths=envelope.artifact_paths,
        allow_offline_cost_report=allow_offline_cost_report,
    )
    if pre_fill is not None:
        child_runs.append(
            _trace_run_for_pre_gate_marcus(
                trial_id=trial_id,
                gate_id=gate_id,
                proposal=pre_fill,
            )
        )
    card = _build_decision_card(
        gate_id=gate_id,
        trial_id=trial_id,
        node_id=node_id,
        operator_id=operator_id,
        pending_nodes=pending,
        artifact_paths=envelope.artifact_paths,
        production_envelope=production_envelope,
        pre_fill=pre_fill,
        runs_root=runs_root,
    )
    conversation_path = _persist_conversation_turn_if_possible(
        card=card,
        gate_id=gate_id,
        trial_id=trial_id,
        operator_id=operator_id,
        runs_root=runs_root,
    )
    stored = register_decision_card(card)
    checkpoint = _write_checkpoint(
        trial_id=trial_id,
        runs_root=runs_root,
        node_index=node_index,
        gate_id=gate_id,
        run_state=run_state,
        envelope=envelope,
        manifest_path=manifest_path,
        allow_offline_cost_report=allow_offline_cost_report,
        max_specialist_calls=max_specialist_calls,
        directive_path=directive_path,
        bundle_dir=bundle_dir,
    )
    decision_path = (
        _run_dir(trial_id, runs_root) / f"decision-card-{gate_id}.json"
    )
    _write_json(
        decision_path,
        {
            "card": card.model_dump(mode="json"),
            "digest": stored.digest,
            "issued_at": stored.issued_at.astimezone(UTC)
            .isoformat()
            .replace("+00:00", "Z"),
            "server_nonce": stored.server_nonce,
            "checkpoint_path": checkpoint.as_posix(),
        },
    )
    trace_root = (
        _trace_root(
            trial_id=trial_id,
            metadata=trace_metadata,
            child_runs=child_runs,
        )
        if child_runs
        else None
    )
    # A resume segment can reach the next gate with zero new child runs
    # (e.g., pre-gate-Marcus declined under a non-live key). Preserve the
    # prior segment's persisted values instead of regressing them to None.
    cost_report_path = (
        _record_cost(
            trial_id=trial_id,
            runs_root=runs_root,
            trace_root=trace_root,
            allow_offline_cost_report=allow_offline_cost_report,
        )
        if trace_root is not None or allow_offline_cost_report
        else envelope.cost_report_path
    )
    trace_path = None
    if trace_root is not None:
        trace_path = _run_dir(trial_id, runs_root) / "trace-fixture.json"
        _write_json(trace_path, _trace_to_json(trace_root))
    langsmith_trace_id = (
        str(trial_id) if child_runs else envelope.langsmith_trace_id
    )
    run_summary_path = _emit_run_summary_yaml(
        trial_id=trial_id,
        terminal_gate=gate_id,
        runs_root=runs_root,
        manifest_path=manifest_path,
        langsmith_trace_id=langsmith_trace_id,
        # S5: bind the COMPOSED graph (the one in hand), not the raw manifest, so a
        # non-default selection is honored in the run summary across both walks.
        selection=run_state.component_selection,
        composed_manifest=manifest,
    )
    evidence = (
        _has_production_evidence(
            graph_step_completed=graph_step_completed,
            specialist_calls=specialist_calls,
            allow_offline_cost_report=allow_offline_cost_report,
        )
    )
    envelope = envelope.model_copy(
        update={
            "status": "paused-at-gate",
            "paused_gate": gate_id,
            "paused_error_tag": None,
            "langsmith_trace_id": langsmith_trace_id,
            "production_clone_launch_evidence": evidence,
            "production_clone_launch_evidence_reason": (
                "live-specialist-call-recorded"
                if evidence
                else "paused-before-live-specialist-call"
            ),
            "production_envelope": production_envelope,
            "cost_report_path": cost_report_path,
            "artifact_paths": _merge_artifact_paths(
                envelope.artifact_paths,
                decision_path,
                checkpoint,
                conversation_path,
                cost_report_path,
                trace_path,
                run_summary_path,
            ),
        }
    )
    _persist_envelope(envelope, runs_root)
    return envelope


def _dispatch_specialist_at_node(
    *,
    adapter: Any,
    node: NodeSpec,
    manifest: Any,
    specialist_id: str,
    production_envelope: ProductionEnvelope,
    run_state: RunState,
    child_runs: list[SimpleNamespace],
    trial_id: UUID,
    runs_root: Path,
    directive_path: Path | None,
    bundle_dir: Path | None,
) -> tuple[ProductionEnvelope, RunState]:
    """The single specialist-dispatch call site shared by both walkers.

    S4 part 2 (SCP 2026-06-11, Winston d.2): the start and resume walkers
    each carried a verbatim copy of this block, and every new invoke kwarg
    broke one copy or the other (finding #10; the projection_map fake
    breakage). One call site means dispatch semantics evolve in one place.
    """
    # UDAC v1 (M-4 / MT-3) — fail-loud dispatch guard, walk-invariant (the single
    # shared dispatch site). For each asset this consumer declares as `used` that
    # the RAI marks RATIFIED, resolve_asset recomputes the digest FROM DISK and
    # RAISES AssetResolutionError (a SpecialistDispatchError) on a missing/stale
    # ratified asset — caught by BOTH walkers' `except SpecialistDispatchError`
    # and routed through `_pause_at_error` (no parallel channel). Gated on
    # udac_active() so NOTHING (not even _run_dir) evaluates when OFF (Blind-F3) →
    # byte-identical; also a no-op when no RAI exists yet (provisional window).
    if udac_wiring.udac_active():
        udac_wiring.resolve_consumed_assets(
            specialist_id=specialist_id,
            run_dir=_run_dir(trial_id, runs_root),
        )
    # Coverage fail-loud gate (AC8) — walk-invariant (this shared dispatch site is
    # taken by BOTH walkers). Before the audio-spending specialist dispatches, a
    # must-cover source point uncovered with no planned surface raises
    # CoverageAssuranceError (a SpecialistDispatchError) — caught by BOTH walkers'
    # `except SpecialistDispatchError` and routed through `_pause_at_error` BEFORE
    # any ElevenLabs/Descript spend. Gated on coverage_gate_active() so NOTHING (not
    # even _run_dir) evaluates when OFF (byte-identical firewall); no-op when no
    # receipt exists yet (provisional window).
    if coverage_gate_wiring.coverage_gate_active():
        coverage_gate_wiring.enforce_coverage_gate_before_audio(
            specialist_id=specialist_id,
            run_dir=_run_dir(trial_id, runs_root),
        )
    # R7 Teeth-Thin — when MARCUS_RESEARCH_DETECTIVE_LIVE is ON, Irene Pass-2
    # (node 08) is blocked until approve|reject|defer disposition is on disk.
    # Flag-OFF is a no-op (byte-identical). Resume/recover = TRAIL.
    # ResearchDetectiveGateError ⊂ SpecialistDispatchError → _pause_at_error.
    research_detective_gate.enforce_before_pass2(
        specialist_id=specialist_id,
        node_id=node.id,
        run_dir=_run_dir(trial_id, runs_root),
    )
    dependency_map = _resolve_dependency_map(
        node=node,
        specialist_id=specialist_id,
        production_envelope=production_envelope,
    )
    invoke_kwargs: dict[str, Any] = {
        "specialist_id": specialist_id,
        "envelope": production_envelope,
        "dependency_map": dependency_map,
        "cost_usd": 0.0,
        "base_state": run_state,
        "node_id": node.id,
    }
    if node.dependency_projections:
        invoke_kwargs["projection_map"] = node.dependency_projections
    runner_payload = _runner_payload_for_specialist(
        specialist_id=specialist_id,
        directive_path=directive_path,
        bundle_dir=bundle_dir,
        gate_code=_effective_quinn_r_gate_code(node, manifest),
        production_envelope=production_envelope,
        runs_root=runs_root,
        trial_id=trial_id,
    )
    # T5a-F3 repair (BETA): thread the operator's G4A voice `select` into the
    # post-G4A elevenlabs SYNTHESIS. The select-merge lands in
    # run_state.cache_prefix, but a node that builds its payload from
    # dependencies (the synthesis node) drops the base envelope (dispatch_adapter
    # line 122), so the merged pick never reaches enrique. enrique reads
    # payload['selected_voice_id'] as a fallback, so supplying it via
    # runner_supplied_payload binds the pick. Gated to dependency-bearing
    # elevenlabs nodes (the synthesis), NOT the voice-options node which relies
    # on the base envelope; no-op until the operator actually selects.
    if specialist_id in {"elevenlabs", "enrique"} and node.dependency_projections:
        operator_voice = _operator_selected_voice(run_state)
        if operator_voice:
            runner_payload = {**(runner_payload or {}), "selected_voice_id": operator_voice}
    runner_payload = apply_llm_execution_mode_overlay(
        specialist_id=specialist_id,
        run_state=run_state,
        runner_payload=runner_payload,
    )
    if runner_payload is not None:
        invoke_kwargs["runner_supplied_payload"] = runner_payload
    production_envelope = _invoke_specialist_with_retry(adapter, invoke_kwargs, node.id)
    # After Gary lands, apply deferred Storyboard-A / deck-wide variant picks
    # (needed when recover re-entered at 07 with selections already in run_state).
    if specialist_id == "gary":
        production_envelope = _apply_variant_selection(production_envelope, run_state)
    run_state = run_state.model_copy(
        update={"production_envelope": production_envelope}
    )
    contribution = production_envelope.get_contribution(specialist_id, node_id=node.id)
    if contribution is not None:
        child_runs.append(
            _trace_run_for_contribution(
                trial_id=trial_id,
                contribution=contribution,
            )
        )
    return production_envelope, run_state


def _pause_at_error(
    *,
    error: SpecialistDispatchError,
    node_id: str,
    node_index: int,
    specialist_id: str,
    trial_id: UUID,
    envelope: ProductionTrialEnvelope,
    production_envelope: ProductionEnvelope,
    run_state: RunState,
    child_runs: list[SimpleNamespace],
    trace_metadata: dict[str, str],
    last_gate_crossed: str | None,
    graph_step_completed: bool,
    specialist_calls: int,
    manifest_path: Path,
    runs_root: Path,
    allow_offline_cost_report: bool,
    max_specialist_calls: int,
    directive_path: Path | None,
    bundle_dir: Path | None,
) -> ProductionTrialEnvelope:
    """Pause the trial at a typed dispatch failure instead of killing the cycle.

    S4 part 2 (Amelia trap 1): a transient Gamma/Kling/bridge blip previously
    unwound the whole walk, so the operator paid a fresh cycle to retry one
    node. The error-pause persists everything ``trial recover`` needs to retry
    the FAILED node itself — note ``node_index`` is stored unshifted, unlike
    the gate checkpoint's ``next_node_index`` (+1), because recovery re-enters
    at the failed node rather than past a decided gate.
    """
    LOGGER.error(
        "dispatch error at manifest node %s (specialist %s): [%s] %s — "
        "pausing trial %s for recovery",
        node_id,
        specialist_id,
        error.tag,
        error,
        trial_id,
    )
    error_pause_path = _run_dir(trial_id, runs_root) / "error-pause.json"
    _write_json(
        error_pause_path,
        {
            "trial_id": str(trial_id),
            "node_index": node_index,
            "node_id": node_id,
            "specialist_id": specialist_id,
            "tag": error.tag,
            "message": str(error),
            "last_gate_crossed": last_gate_crossed,
            "run_state": run_state.model_dump(mode="json"),
            "runner": {
                "corpus_path": envelope.corpus_path,
                "preset": envelope.preset,
                "operator_id": envelope.operator_id,
                "manifest_path": manifest_path.as_posix(),
                "allow_offline_cost_report": allow_offline_cost_report,
                "max_specialist_calls": max_specialist_calls,
                "directive_path": directive_path.as_posix() if directive_path else None,
                "bundle_dir": bundle_dir.as_posix() if bundle_dir else None,
            },
        },
    )
    trace_root = (
        _trace_root(
            trial_id=trial_id,
            metadata=trace_metadata,
            child_runs=child_runs,
        )
        if child_runs
        else None
    )
    # Spend already incurred this segment is recorded at the pause, exactly
    # as _pause_at_gate does — an error pause must not orphan cost evidence.
    cost_report_path = (
        _record_cost(
            trial_id=trial_id,
            runs_root=runs_root,
            trace_root=trace_root,
            allow_offline_cost_report=allow_offline_cost_report,
        )
        if trace_root is not None or allow_offline_cost_report
        else envelope.cost_report_path
    )
    trace_path = None
    if trace_root is not None:
        trace_path = _run_dir(trial_id, runs_root) / "trace-fixture.json"
        _write_json(trace_path, _trace_to_json(trace_root))
    langsmith_trace_id = str(trial_id) if child_runs else envelope.langsmith_trace_id
    evidence = _has_production_evidence(
        graph_step_completed=graph_step_completed,
        specialist_calls=specialist_calls,
        allow_offline_cost_report=allow_offline_cost_report,
    )
    envelope = envelope.model_copy(
        update={
            "status": "paused-at-error",
            "paused_gate": None,
            "paused_error_tag": error.tag,
            "langsmith_trace_id": langsmith_trace_id,
            "production_clone_launch_evidence": evidence,
            "production_clone_launch_evidence_reason": (
                f"paused-at-dispatch-error:{error.tag}"
            ),
            "production_envelope": production_envelope,
            "cost_report_path": cost_report_path,
            "artifact_paths": _merge_artifact_paths(
                envelope.artifact_paths,
                error_pause_path,
                cost_report_path,
                trace_path,
            ),
        }
    )
    _persist_envelope(envelope, runs_root)
    return envelope


def _pause_at_provider_batch(
    *,
    waiting: WaitingForProviderBatchError,
    node_id: str,
    node_index: int,
    specialist_id: str,
    trial_id: UUID,
    envelope: ProductionTrialEnvelope,
    production_envelope: ProductionEnvelope,
    run_state: RunState,
    child_runs: list[SimpleNamespace],
    trace_metadata: dict[str, str],
    last_gate_crossed: str | None,
    graph_step_completed: bool,
    specialist_calls: int,
    manifest_path: Path,
    runs_root: Path,
    allow_offline_cost_report: bool,
    max_specialist_calls: int,
    directive_path: Path | None,
    bundle_dir: Path | None,
) -> ProductionTrialEnvelope:
    """Pause while a LiteLLM Batch job is still non-terminal (B3)."""

    LOGGER.info(
        "provider batch waiting at node %s (specialist %s) batch_id=%s — "
        "pausing trial %s (resume: trial resume-batch --trial-id %s)",
        node_id,
        specialist_id,
        waiting.batch_id,
        trial_id,
        trial_id,
    )
    pause_path = _run_dir(trial_id, runs_root) / "provider-batch-pause.json"
    _write_json(
        pause_path,
        {
            "trial_id": str(trial_id),
            "node_index": node_index,
            "node_id": node_id,
            "specialist_id": specialist_id,
            "tag": waiting.tag,
            "message": str(waiting),
            "batch_id": waiting.batch_id,
            "receipt_path": waiting.receipt_path.as_posix(),
            "last_gate_crossed": last_gate_crossed,
            "run_state": run_state.model_dump(mode="json"),
            "runner": {
                "corpus_path": envelope.corpus_path,
                "preset": envelope.preset,
                "operator_id": envelope.operator_id,
                "manifest_path": manifest_path.as_posix(),
                "allow_offline_cost_report": allow_offline_cost_report,
                "max_specialist_calls": max_specialist_calls,
                "directive_path": directive_path.as_posix() if directive_path else None,
                "bundle_dir": bundle_dir.as_posix() if bundle_dir else None,
            },
            "resume_command": f"trial resume-batch --trial-id {trial_id}",
        },
    )
    trace_root = (
        _trace_root(
            trial_id=trial_id,
            metadata=trace_metadata,
            child_runs=child_runs,
        )
        if child_runs
        else None
    )
    cost_report_path = (
        _record_cost(
            trial_id=trial_id,
            runs_root=runs_root,
            trace_root=trace_root,
            allow_offline_cost_report=allow_offline_cost_report,
        )
        if trace_root is not None or allow_offline_cost_report
        else envelope.cost_report_path
    )
    evidence = _has_production_evidence(
        graph_step_completed=graph_step_completed,
        specialist_calls=specialist_calls,
        allow_offline_cost_report=allow_offline_cost_report,
    )
    envelope = envelope.model_copy(
        update={
            "status": "waiting_for_provider_batch",
            "paused_gate": None,
            "paused_error_tag": None,
            "waiting_batch_id": waiting.batch_id,
            "production_clone_launch_evidence": evidence,
            "production_clone_launch_evidence_reason": (
                f"waiting-for-provider-batch:{waiting.batch_id}"
            ),
            "production_envelope": production_envelope,
            "cost_report_path": cost_report_path,
            "artifact_paths": _merge_artifact_paths(
                envelope.artifact_paths,
                pause_path,
                cost_report_path,
            ),
        }
    )
    _persist_envelope(envelope, runs_root)
    return envelope


def _dispatch_specialist_catching_batch_wait(
    *,
    adapter: Any,
    node: Any,
    manifest: Any,
    specialist_id: str,
    production_envelope: ProductionEnvelope,
    run_state: RunState,
    child_runs: list[SimpleNamespace],
    trial_id: UUID,
    runs_root: Path,
    directive_path: Path | None,
    bundle_dir: Path | None,
    node_index: int,
    envelope: ProductionTrialEnvelope,
    trace_metadata: dict[str, str],
    last_gate_crossed: str | None,
    graph_step_completed: bool,
    specialist_calls: int,
    manifest_path: Path,
    allow_offline_cost_report: bool,
    max_specialist_calls: int,
) -> tuple[ProductionEnvelope, RunState] | ProductionTrialEnvelope:
    """Shared two-walk chokepoint: dispatch, provider-batch wait, or error-pause."""

    try:
        return _dispatch_specialist_at_node(
            adapter=adapter,
            node=node,
            manifest=manifest,
            specialist_id=specialist_id,
            production_envelope=production_envelope,
            run_state=run_state,
            child_runs=child_runs,
            trial_id=trial_id,
            runs_root=runs_root,
            directive_path=directive_path,
            bundle_dir=bundle_dir,
        )
    except WaitingForProviderBatchError as waiting:
        return _pause_at_provider_batch(
            waiting=waiting,
            node_id=node.id,
            node_index=node_index,
            specialist_id=specialist_id,
            trial_id=trial_id,
            envelope=envelope,
            production_envelope=production_envelope,
            run_state=run_state,
            child_runs=child_runs,
            trace_metadata=trace_metadata,
            last_gate_crossed=last_gate_crossed,
            graph_step_completed=graph_step_completed,
            specialist_calls=specialist_calls,
            manifest_path=manifest_path,
            runs_root=runs_root,
            allow_offline_cost_report=allow_offline_cost_report,
            max_specialist_calls=max_specialist_calls,
            directive_path=directive_path,
            bundle_dir=bundle_dir,
        )
    except SpecialistDispatchError as exc:
        return _pause_at_error(
            error=exc,
            node_id=node.id,
            node_index=node_index,
            specialist_id=specialist_id,
            trial_id=trial_id,
            envelope=envelope,
            production_envelope=production_envelope,
            run_state=run_state,
            child_runs=child_runs,
            trace_metadata=trace_metadata,
            last_gate_crossed=last_gate_crossed,
            graph_step_completed=graph_step_completed,
            specialist_calls=specialist_calls,
            manifest_path=manifest_path,
            runs_root=runs_root,
            allow_offline_cost_report=allow_offline_cost_report,
            max_specialist_calls=max_specialist_calls,
            directive_path=directive_path,
            bundle_dir=bundle_dir,
        )


def run_production_trial(
    corpus_path: Path,
    preset: Literal["production", "explore"],
    operator_id: str,
    trial_id: UUID | None = None,
    *,
    runs_root: Path = RUNS_ROOT,
    allow_offline_cost_report: bool = False,
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
    max_specialist_calls: int = 1,
    pause_at_gates: bool = True,
    directive_path: Path | None = None,
    component_selection: ComponentSelection | None = None,
    llm_execution_mode: LlmExecutionMode = "realtime",
    hud: Literal["on", "off"] = "on",
) -> ProductionTrialEnvelope:
    """Register, compose, and start a production trial.

    ``directive_path`` (Story 7a.1): when provided, the runner derives
    ``bundle_dir = run_dir / "bundle"`` and threads both to Texas's _act
    via ``ProductionDispatchAdapter.invoke_specialist(runner_supplied_payload=...)``
    so Texas's ``dispatch_retrieval`` is called with non-None args (closing
    trial-475 silent-bypass at line 34-40 of retrieval_dispatch.py).
    """
    if not corpus_path.exists():
        raise FileNotFoundError(f"trial input path does not exist: {corpus_path}")

    effective_trial_id = trial_id or uuid4()
    composer_run_dir = runs_root / str(effective_trial_id)
    bundle_dir: Path | None = None
    if directive_path is not None:
        bundle_dir = composer_run_dir / "bundle"
        bundle_dir.mkdir(parents=True, exist_ok=True)
    production_envelope = ProductionEnvelope(trial_id=effective_trial_id)
    envelope = ProductionTrialEnvelope(
        trial_id=effective_trial_id,
        preset=preset,
        corpus_path=corpus_path.as_posix(),
        operator_id=operator_id,
        started_at=_now(),
        status="registered",
        production_clone_launch_evidence=False,
        production_clone_launch_evidence_reason="registered-no-specialist-fired",
        production_envelope=production_envelope,
    )
    _persist_envelope(envelope, runs_root)

    # Compile-time composition (S2): assemble ONLY the selected components' nodes,
    # then freeze. The default (deck+motion) reproduces today's full graph
    # byte-identically, so this is a no-op until the front door (S5) narrows the
    # selection. The selection is persisted on RunState so the continuation walk
    # rehydrates it and never re-defaults (two-walk trap).
    selection = component_selection or ComponentSelection.production_default()
    manifest = compose_manifest(load_manifest(manifest_path), selection)
    # AD-15: project the composed-manifest identity + two-stage steps map at
    # composition (walk index 0), so the in-flight emit below already carries steps.
    _emit_operator_surface_steps(effective_trial_id, runs_root, manifest, 0)

    # AD-7/AD-8/AD-11 pinned start sequence: with the run dir + registered
    # projection + steps in place, launch the HUD server child (--hud gated),
    # launch the notifier, and run pre-flight/heartbeats BEFORE any specialist
    # dispatch — SPOC spawn is gated on all-green. Pre-flight is runtime-owned
    # regardless of the --hud flag; only the server/notifier launches are gated.
    # Offline harness runs (allow_offline_cost_report) skip the live gate: they
    # carry no keys and are not real clone-launch starts (their status is
    # already "registered-offline").
    if not allow_offline_cost_report:
        _preflight_result = _run_start_preflight_gate(
            effective_trial_id,
            composer_run_dir,
            runs_root,
            hud=hud,
            producer_pid=os.getpid(),
        )
        if not _preflight_result.all_green:
            # Abort cleanly BEFORE any specialist dispatch. The projection is
            # left at `registered` showing the failed pre-flight item(s); append
            # a terminal trace event; the walk never runs (AD-7/AD-11).
            blocking = _preflight_result.blocking_items()
            _append_operator_surface_trace(
                effective_trial_id,
                runs_root,
                "preflight-blocked-spawn",
                detail="; ".join(f"{i.name}={i.state}" for i in blocking) or None,
            )
            raise PreflightGateFailed(effective_trial_id, blocking)

    active_gate_ids = production_gate_ids(manifest)
    graph = compile_run_graph(manifest)
    adapter = ProductionDispatchAdapter()
    run_state = RunState(
        run_id=effective_trial_id,
        status="running",
        graph_version=DEFAULT_GRAPH_VERSION,
        component_selection=selection,
        llm_execution_mode=llm_execution_mode,
        cache_state=CacheState(
            cache_prefix=json.dumps(
                {
                    "trial_id": str(effective_trial_id),
                    "corpus_path": corpus_path.as_posix(),
                    "preset": preset,
                },
                sort_keys=True,
            ),
        ),
        production_envelope=production_envelope,
    )
    # F-E2E-2: establish the ambient sections (health/specialists/modalities +
    # an opening trace event) BEFORE the in-flight transition persists, so the
    # in-flight emit's read-merge-write inherits a present health section and the
    # witness-mode lifecycle invariant ("status=in-flight requires the health
    # section") never fires. run_state already carries llm_execution_mode.
    _refresh_operator_surface_ambient(
        effective_trial_id,
        runs_root,
        run_state,
        trace_event=("walk-start", "specialist walk starting"),
    )
    envelope = envelope.model_copy(update={"status": "in-flight"})
    _persist_envelope(envelope, runs_root)

    child_runs: list[SimpleNamespace] = []
    specialist_calls = 0
    graph_step_completed = False
    last_gate_crossed: str | None = None
    trace_metadata: dict[str, str]

    _start_assembler = OperatorSurfaceAssembler(effective_trial_id, runs_root)
    with _start_assembler.freshness_tick(), _trial_trace_context(
        trial_id=effective_trial_id,
        preset=preset,
        operator_id=operator_id,
    ) as trace_metadata:
        for index, node in enumerate(manifest.nodes):
            # AD-15: advance the projected walk index as the loop progresses
            # (a node-lifecycle progress event; bumps progress_seq, AD-10).
            _emit_operator_surface_steps(effective_trial_id, runs_root, manifest, index)
            # F-E2E-2: refresh ambient sections + append a node-enter trace event
            # each iteration so the health cost tile, specialist chips, and the
            # state-trace well grow as the walk progresses (ambient refresh: seq
            # bumps, progress_seq does not — the steps emit above owns progress).
            _refresh_operator_surface_ambient(
                effective_trial_id,
                runs_root,
                run_state,
                trace_event=("node-enter", str(node.id)),
            )
            handler = _active_node_handler(graph, node.id)
            node_kind = getattr(handler, "__production_node_kind__", None)
            if node_kind == "gate":
                gate_id = handler.__production_gate_id__
                if (
                    gate_id == g0_enrichment_wiring.G0_ENRICHMENT_GATE_CODE
                    and not g0_enrichment_wiring.g0_enrichment_active()
                ):
                    # AC-S2-7: with the G0-enrichment brick asleep, confirm-gate #1
                    # is traversed (no pause) so deck-default flow is byte-identical
                    # (the first pause stays G1). Woken via MARCUS_G0_ENRICHMENT_ACTIVE.
                    last_gate_crossed = gate_id
                    _udac_ratify_gate(gate_id, effective_trial_id, runs_root)  # F3
                    graph_step_completed = True
                    continue
                if (
                    gate_id == irene_refinement_wiring.IRENE_REFINEMENT_GATE_CODE
                    and not irene_refinement_wiring.irene_refinement_active()
                ):
                    # AC-S3-4 (start-walk leg): with the brick asleep, ratify-gate #2
                    # is traversed (no pause) so deck-default flow is byte-identical
                    # (feature-flag parity with G0E). Woken via MARCUS_G0_ENRICHMENT_ACTIVE.
                    last_gate_crossed = gate_id
                    _udac_ratify_gate(gate_id, effective_trial_id, runs_root)  # F3
                    graph_step_completed = True
                    continue
                if not pause_at_gates:
                    if gate_id in active_gate_ids and not allow_offline_cost_report:
                        raise GateBypassError(
                            f"refused silent bypass of gate {gate_id} at manifest node {node.id}"
                        )
                    last_gate_crossed = gate_id
                    # UDAC v1 (M-1 / M-5): a start-walk gate crossing (the
                    # bypass/offline path) ratifies the gate's assets too, so
                    # ratified_at is identical whether a gate clears on the start
                    # or continuation walk. No-op when UDAC is OFF / no asset landed.
                    _udac_ratify_gate(gate_id, effective_trial_id, runs_root)
                    graph_step_completed = True
                    continue
                # S5 criterion 7 (operator-ratified 2026-06-12): storyboard
                # review gates publish their ONLINE interactive pack BEFORE
                # the pause — a storyboard gate without its review surface is
                # the attempt-4 quality-theater class. Publish failure
                # error-pauses (recoverable; retry re-enters this gate node).
                try:
                    storyboard_publisher.publish_storyboard_for_gate(
                        gate_id=gate_id,
                        trial_id=str(effective_trial_id),
                        production_envelope=production_envelope,
                        runs_root=runs_root,
                    )
                    chooser_publisher.publish_chooser_for_gate(
                        gate_id=gate_id,
                        trial_id=str(effective_trial_id),
                        production_envelope=production_envelope,
                        runs_root=runs_root,
                    )
                    # Coverage interlock (Step 4, R5-A7): at the G3 storyboard-publish
                    # seam, DERIVE + WRITE + RENDER the coverage receipt (no-op off-G3 /
                    # coverage-OFF). Walk-parity: the IDENTICAL call on the continuation
                    # walk. ``run_state`` is a RunState MODEL → pass its json model_dump so
                    # the marshaller reads plan_units/slide_briefs lineage (the never-true
                    # ``isinstance(run_state, dict)`` guard marshalled NOTHING). Defensive
                    # (never raises); deck+narration are read from the run-dir exports SSOT.
                    coverage_runner._derive_and_write_coverage_receipt(
                        _run_dir(effective_trial_id, runs_root),
                        gate_id,
                        run_state.model_dump(mode="json") if run_state is not None else None,
                    )
                except SpecialistDispatchError as exc:
                    return _pause_at_error(
                        error=exc,
                        node_id=node.id,
                        node_index=index,
                        specialist_id="storyboard_publisher",
                        trial_id=effective_trial_id,
                        envelope=envelope,
                        production_envelope=production_envelope,
                        run_state=run_state,
                        child_runs=child_runs,
                        trace_metadata=trace_metadata,
                        last_gate_crossed=last_gate_crossed,
                        graph_step_completed=graph_step_completed,
                        specialist_calls=specialist_calls,
                        manifest_path=manifest_path,
                        runs_root=runs_root,
                        allow_offline_cost_report=allow_offline_cost_report,
                        max_specialist_calls=max_specialist_calls,
                        directive_path=directive_path,
                        bundle_dir=bundle_dir,
                    )
                return _pause_at_gate(
                    gate_id=gate_id,
                    node_id=node.id,
                    node_index=index,
                    manifest=manifest,
                    trial_id=effective_trial_id,
                    operator_id=operator_id,
                    envelope=envelope,
                    production_envelope=production_envelope,
                    run_state=run_state,
                    child_runs=child_runs,
                    trace_metadata=trace_metadata,
                    specialist_calls=specialist_calls,
                    graph_step_completed=graph_step_completed,
                    manifest_path=manifest_path,
                    runs_root=runs_root,
                    allow_offline_cost_report=allow_offline_cost_report,
                    max_specialist_calls=max_specialist_calls,
                    directive_path=directive_path,
                    bundle_dir=bundle_dir,
                )

            if node.id in workbook_wiring.WORKBOOK_BAND_NODE_IDS:
                # 38.3b: unconditional terminal workbook-band seam. These
                # deterministic hooks do not depend on credentials, live flags,
                # or offline-cost mode; later injected factories own that choice.
                try:
                    production_envelope = workbook_wiring.run_workbook_band_node(
                        node_id=node.id,
                        production_envelope=production_envelope,
                        runtime_context=workbook_wiring.runtime_context_for_run(
                            runs_root / str(effective_trial_id), node_id=node.id
                        ),
                    )
                except SpecialistDispatchError as exc:
                    return _pause_at_error(
                        error=exc,
                        node_id=node.id,
                        node_index=index,
                        specialist_id=workbook_wiring.WORKBOOK_BAND_SPECIALIST_IDS[
                            node.id
                        ],
                        trial_id=effective_trial_id,
                        envelope=envelope,
                        production_envelope=production_envelope,
                        run_state=run_state,
                        child_runs=child_runs,
                        trace_metadata=trace_metadata,
                        last_gate_crossed=last_gate_crossed,
                        graph_step_completed=graph_step_completed,
                        specialist_calls=specialist_calls,
                        manifest_path=manifest_path,
                        runs_root=runs_root,
                        allow_offline_cost_report=allow_offline_cost_report,
                        max_specialist_calls=max_specialist_calls,
                        directive_path=directive_path,
                        bundle_dir=bundle_dir,
                    )
                run_state = run_state.model_copy(
                    update={"production_envelope": production_envelope}
                )
                graph_step_completed = True
                continue

            if (
                node_kind == "orchestration"
                and node.id in package_builders.BUILDER_NODE_IDS
                and _has_live_openai()
                and not allow_offline_cost_report
            ):
                # S3 (SCP 2026-06-11): §06 builds the Gary slide-brief
                # package as a first-class contribution at its own node
                # (pre_gate_marcus runner-invocation pattern; deterministic,
                # so it runs on the live path only, mirroring specialists).
                # WAVE-0 tranche 2 (2026-06-17): a BuilderInputError starvation
                # now error-pauses recoverably (the last live-walk dispatch leg
                # to join the family) instead of killing the trial — the pause
                # halts BEFORE the next gate, so no quality-theater path opens
                # (Murat/John adjudication; S5-crit-5 contract preserved).
                try:
                    production_envelope = package_builders.run_builder_node(
                        node_id=node.id,
                        production_envelope=production_envelope,
                        runs_root=runs_root,
                        trial_id=effective_trial_id,
                    )
                except SpecialistDispatchError as exc:
                    return _pause_at_error(
                        error=exc,
                        node_id=node.id,
                        node_index=index,
                        specialist_id=package_builders.BUILDER_SPECIALIST_ID,
                        trial_id=effective_trial_id,
                        envelope=envelope,
                        production_envelope=production_envelope,
                        run_state=run_state,
                        child_runs=child_runs,
                        trace_metadata=trace_metadata,
                        last_gate_crossed=last_gate_crossed,
                        graph_step_completed=graph_step_completed,
                        specialist_calls=specialist_calls,
                        manifest_path=manifest_path,
                        runs_root=runs_root,
                        allow_offline_cost_report=allow_offline_cost_report,
                        max_specialist_calls=max_specialist_calls,
                        directive_path=directive_path,
                        bundle_dir=bundle_dir,
                    )
                run_state = run_state.model_copy(
                    update={"production_envelope": production_envelope}
                )
                graph_step_completed = True
                continue

            if (
                node_kind == "orchestration"
                and node.id in research_wiring.RESEARCH_WIRING_NODE_IDS
            ):
                # Braid S3 (option A): the Irene→Tracy→Texas research-wiring hook
                # fires at the §04.55 plan-lock fanout node. TWO-WALK PARITY
                # (memory project_production_runner_two_walks): §04.55 sits AFTER
                # G1, so on the trial path this only ever fires via the
                # CONTINUATION walk — but the side-effect is present in BOTH walk
                # bodies (storyboard/chooser-publisher precedent). Bridge dispatch
                # is local; the live Texas fetch rides the MARCUS_RESEARCH_DISPATCH_LIVE
                # toggle (S6 D1: DEFAULT ON — every canonical run dispatches live at
                # §04.55; only an explicit falsy kill-switch value skips it). A
                # creds-absent walk degrades VISIBLY at run_research_wiring entry
                # (D4) rather than firing a doomed call.
                try:
                    production_envelope = research_wiring.run_research_wiring(
                        node_id=node.id,
                        production_envelope=production_envelope,
                        posture_selector=research_wiring.DeterministicPostureSelector(),
                        dispatch_live=_research_dispatch_live(),
                    )
                except CitationFidelityError as exc:
                    # G2 FAIL mode (spec §3.4): an unsourced citation error-pauses
                    # the trial (recoverable) rather than killing the walk.
                    return _pause_at_error(
                        error=SpecialistDispatchError(
                            f"G2 citation-fidelity FAIL: {exc} "
                            f"(unsourced_citations={exc.unsourced_citations})",
                            tag="citation_fidelity_fail",
                        ),
                        node_id=node.id,
                        node_index=index,
                        specialist_id=research_wiring.RESEARCH_WIRING_SPECIALIST_ID,
                        trial_id=effective_trial_id,
                        envelope=envelope,
                        production_envelope=production_envelope,
                        run_state=run_state,
                        child_runs=child_runs,
                        trace_metadata=trace_metadata,
                        last_gate_crossed=last_gate_crossed,
                        graph_step_completed=graph_step_completed,
                        specialist_calls=specialist_calls,
                        manifest_path=manifest_path,
                        runs_root=runs_root,
                        allow_offline_cost_report=allow_offline_cost_report,
                        max_specialist_calls=max_specialist_calls,
                        directive_path=directive_path,
                        bundle_dir=bundle_dir,
                    )
                run_state = run_state.model_copy(
                    update={"production_envelope": production_envelope}
                )
                graph_step_completed = True
                continue

            if (
                node_kind == "orchestration"
                and node.id in g0_enrichment_wiring.G0_ENRICHMENT_NODE_IDS
                and g0_enrichment_wiring.g0_enrichment_active()
            ):
                # G0-S2 brick: the Marcus-SPOC G0 pre-pass (typing + provisional-LO
                # extraction) OFF the deterministic critical path, frozen + corpus-
                # fingerprint-cached, feeding operator confirm-gate #1 (G0E, the next
                # node). TWO-WALK PARITY: this node sits BEFORE node 01, so it fires
                # on the START walk here; the SAME side-effect is mirrored into the
                # continuation walk (resume/recover re-entry before G0E). The live
                # LLM is operator-gated via _research_dispatch_live()'s sibling
                # offline guard (_has_live_openai): offline runs use the deterministic
                # recorded pre-pass; the live-segment proof (AC-S2-8) exercises the
                # real model.
                try:
                    production_envelope = g0_enrichment_wiring.run_g0_enrichment(
                        node_id=node.id,
                        production_envelope=production_envelope,
                        corpus_dir=corpus_path,
                        trial_id=effective_trial_id,
                        runs_root=runs_root,
                        dispatch_live=(
                            g0_enrichment_wiring.g0_dispatch_live()
                            and _has_live_openai()
                            and not allow_offline_cost_report
                        ),
                    )
                except SpecialistDispatchError as exc:
                    return _pause_at_error(
                        error=exc,
                        node_id=node.id,
                        node_index=index,
                        specialist_id=g0_enrichment_wiring.G0_ENRICHMENT_SPECIALIST_ID,
                        trial_id=effective_trial_id,
                        envelope=envelope,
                        production_envelope=production_envelope,
                        run_state=run_state,
                        child_runs=child_runs,
                        trace_metadata=trace_metadata,
                        last_gate_crossed=last_gate_crossed,
                        graph_step_completed=graph_step_completed,
                        specialist_calls=specialist_calls,
                        manifest_path=manifest_path,
                        runs_root=runs_root,
                        allow_offline_cost_report=allow_offline_cost_report,
                        max_specialist_calls=max_specialist_calls,
                        directive_path=directive_path,
                        bundle_dir=bundle_dir,
                    )
                run_state = run_state.model_copy(
                    update={"production_envelope": production_envelope}
                )
                graph_step_completed = True
                continue

            if (
                node_kind == "orchestration"
                and node.id in irene_refinement_wiring.IRENE_REFINEMENT_NODE_IDS
                and irene_refinement_wiring.irene_refinement_active()
            ):
                # G0-S3 brick (START WALK leg): Irene refines the gate-#1-confirmed
                # provisional LOs in place (provisional->refined), produces the
                # advisory per-LO adequacy + the signed LO-delta ledger, frozen +
                # corpus-fingerprint-cached, feeding operator ratify-gate #2 (G0R,
                # the next gate node). TWO-WALK PARITY: the SAME side-effect is
                # mirrored into the continuation walk (resume/recover re-entry before
                # G0R). Idempotent: a node already carrying its contribution is not
                # re-run.
                try:
                    production_envelope = irene_refinement_wiring.run_irene_refinement(
                        node_id=node.id,
                        production_envelope=production_envelope,
                        trial_id=effective_trial_id,
                        runs_root=runs_root,
                        dispatch_live=(
                            irene_refinement_wiring.ir_dispatch_live()
                            and _has_live_openai()
                            and not allow_offline_cost_report
                        ),
                    )
                except SpecialistDispatchError as exc:
                    return _pause_at_error(
                        error=exc,
                        node_id=node.id,
                        node_index=index,
                        specialist_id=irene_refinement_wiring.IRENE_REFINEMENT_SPECIALIST_ID,
                        trial_id=effective_trial_id,
                        envelope=envelope,
                        production_envelope=production_envelope,
                        run_state=run_state,
                        child_runs=child_runs,
                        trace_metadata=trace_metadata,
                        last_gate_crossed=last_gate_crossed,
                        graph_step_completed=graph_step_completed,
                        specialist_calls=specialist_calls,
                        manifest_path=manifest_path,
                        runs_root=runs_root,
                        allow_offline_cost_report=allow_offline_cost_report,
                        max_specialist_calls=max_specialist_calls,
                        directive_path=directive_path,
                        bundle_dir=bundle_dir,
                    )
                run_state = run_state.model_copy(
                    update={"production_envelope": production_envelope}
                )
                graph_step_completed = True
                continue

            if node_kind == "specialist" and specialist_calls < max_specialist_calls:
                specialist_id = handler.__production_specialist_id__
                # S2 per-node keying (SCP 2026-06-11): the skip rule guards
                # node revisits, not specialist revisits — the per-specialist
                # Path-Z rule silently skipped irene_pass1's §05/§05B jobs.
                if production_envelope.get_contribution(specialist_id, node_id=node.id) is not None:
                    LOGGER.info(
                        "manifest node %s (specialist %s) already carries its "
                        "contribution; node re-dispatch skipped per S2 "
                        "per-node idempotency contract",
                        node.id,
                        specialist_id,
                    )
                    graph_step_completed = True
                    continue
                if _has_live_openai() and not allow_offline_cost_report:
                    dispatched = _dispatch_specialist_catching_batch_wait(
                        adapter=adapter,
                        node=node,
                        manifest=manifest,
                        specialist_id=specialist_id,
                        production_envelope=production_envelope,
                        run_state=run_state,
                        child_runs=child_runs,
                        trial_id=effective_trial_id,
                        runs_root=runs_root,
                        directive_path=directive_path,
                        bundle_dir=bundle_dir,
                        node_index=index,
                        envelope=envelope,
                        trace_metadata=trace_metadata,
                        last_gate_crossed=last_gate_crossed,
                        graph_step_completed=graph_step_completed,
                        specialist_calls=specialist_calls,
                        manifest_path=manifest_path,
                        allow_offline_cost_report=allow_offline_cost_report,
                        max_specialist_calls=max_specialist_calls,
                    )
                    if isinstance(dispatched, ProductionTrialEnvelope):
                        return dispatched
                    production_envelope, run_state = dispatched
                    specialist_calls += 1
                graph_step_completed = True

    completed_at = _now()
    trace_root = _trace_root(
        trial_id=effective_trial_id,
        metadata=trace_metadata,
        child_runs=child_runs,
    ) if child_runs else None
    cost_report_path = _record_cost(
        trial_id=effective_trial_id,
        runs_root=runs_root,
        trace_root=trace_root,
        allow_offline_cost_report=allow_offline_cost_report,
    )
    trace_path = None
    if trace_root is not None:
        trace_path = _run_dir(effective_trial_id, runs_root) / "trace-fixture.json"
        _write_json(trace_path, _trace_to_json(trace_root))
    langsmith_trace_id = str(effective_trial_id) if child_runs else None
    run_summary_path = _emit_run_summary_yaml(
        trial_id=effective_trial_id,
        # Last gate actually traversed this walk; "G4" only as the legacy
        # fallback for manifests that carry no gate nodes at all.
        terminal_gate=last_gate_crossed or "G4",
        runs_root=runs_root,
        manifest_path=manifest_path,
        langsmith_trace_id=langsmith_trace_id,
        selection=run_state.component_selection,
        composed_manifest=manifest,
    )
    engagement_report_path = _emit_engagement_decay_report(
        trial_id=effective_trial_id,
        child_runs=child_runs,
    )
    evidence = (
        _has_production_evidence(
            graph_step_completed=graph_step_completed,
            specialist_calls=specialist_calls,
            allow_offline_cost_report=allow_offline_cost_report,
        )
    )
    reason = "live-specialist-call-recorded" if evidence else "no-live-specialist-call-recorded"
    envelope = envelope.model_copy(
        update={
            "status": "completed",
            "completed_at": completed_at,
            "paused_gate": None,
            "langsmith_trace_id": langsmith_trace_id,
            "production_clone_launch_evidence": evidence,
            "production_clone_launch_evidence_reason": reason,
            "production_envelope": production_envelope,
            "cost_report_path": cost_report_path,
            "artifact_paths": _merge_artifact_paths(
                envelope.artifact_paths,
                cost_report_path,
                trace_path,
                run_summary_path,
                engagement_report_path,
            ),
        }
    )
    _persist_envelope(envelope, runs_root)
    return envelope


def resume_production_trial(
    *,
    trial_id: UUID,
    verdict: OperatorVerdict,
    runs_root: Path = RUNS_ROOT,
    max_specialist_calls: int | None = None,
) -> ProductionTrialEnvelope:
    """Validate a gate verdict and continue the persisted trial past the gate."""
    run_dir = _run_dir(trial_id, runs_root)
    envelope = ProductionTrialEnvelope.model_validate_json(
        (run_dir / "run.json").read_text(encoding="utf-8"),
        # Witness-mode lifecycle invariants: violations on persisted state are
        # recorded to the run's anomaly sidecar, never raised (S4p2 follow-on;
        # witness->strict flip is a post-S5 ceremony).
        context={"anomaly_sink": run_dir / "anomalies.jsonl"},
    )
    # AD-17: reconcile-on-entry — re-emit the projection from the current
    # (run.json-derived) envelope FIRST, before doing anything else, so a stale
    # projection (crash between run.json persist and projection write) renders
    # run.json truth after any runner touch. Idempotent + cheap.
    _emit_operator_surface(envelope, runs_root)
    if envelope.status != "paused-at-gate":
        raise RuntimeError(
            f"trial {trial_id} is not paused at a gate; status={envelope.status!r}"
        )
    if envelope.paused_gate != verdict.gate_id:
        raise GateError(
            "checkpoint_gate_mismatch",
            f"verdict gate_id={verdict.gate_id} does not match paused_gate={envelope.paused_gate}",
        )
    if envelope.production_envelope.schema_version == "production-envelope.v1":
        raise LegacyEnvelopeSchemaError(
            f"trial {trial_id} carries a production-envelope.v1 (per-specialist "
            "keyed) envelope; v1 runs are not resumable after the S2 per-node "
            "keying migration (SCP 2026-06-11) — relaunch as a new cycle; the "
            "run dir stays frozen as evidence."
        )
    _ensure_decision_card_registered_from_disk(
        trial_id=trial_id,
        gate_id=verdict.gate_id,
        run_dir=run_dir,
    )
    checkpoint_path = run_dir / "checkpoint.json"
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    if checkpoint.get("trial_id") != str(trial_id) or checkpoint.get("gate_id") != verdict.gate_id:
        raise GateError(
            "checkpoint_gate_mismatch",
            "persisted checkpoint does not match the accepted verdict gate",
        )
    command = resume_from_verdict(verdict)
    runner = checkpoint.get("runner") or {}
    run_state = RunState.model_validate_json(json.dumps(checkpoint["run_state"]))
    run_state = run_state.model_copy(
        update={"production_envelope": envelope.production_envelope}
    )
    run_state = _apply_verdict_to_run_state(run_state, verdict)
    if (
        verdict.gate_id == irene_refinement_wiring.IRENE_REFINEMENT_GATE_CODE
        and verdict.verb != "reject"
    ):
        # AC-S3-4/AC-S3-5: the operator verdict (never the model) advances the
        # refined LOs refined->ratified, then the completeness hard-assert (ACCESS
        # + ASSESSMENT-PRESENCE, NOT adequacy outcome) gates hand-off-to-Gary. A
        # thin/gap verdict PASSES (§3.1); an unreachable source or a silently-absent
        # adequacy is RED.
        _apply_g0r_ratification(run_dir=run_dir)
    _write_json(
        run_dir / "resume-command.json",
        {
            "command": command.resume,
            "run_state": run_state.model_dump(mode="json"),
        },
    )
    if verdict.verb == "reject":
        manifest_path = Path(runner.get("manifest_path") or DEFAULT_MANIFEST_PATH)
        run_summary_path = _emit_run_summary_yaml(
            trial_id=trial_id,
            terminal_gate=verdict.gate_id,
            runs_root=runs_root,
            manifest_path=manifest_path,
            langsmith_trace_id=envelope.langsmith_trace_id,
            # No composed manifest in hand on the early-reject path; pass the
            # rehydrated selection so the binding still reflects the composed
            # graph (recomputed inside _pack_hash_binding) for a non-default run.
            selection=run_state.component_selection,
        )
        updated = envelope.model_copy(
            update={
                "status": "failed",
                "completed_at": _now(),
                "production_clone_launch_evidence_reason": "operator-rejected-at-gate",
                "artifact_paths": _merge_artifact_paths(
                    envelope.artifact_paths, run_summary_path
                ),
            }
        )
        _persist_envelope(updated, runs_root)
        return updated

    manifest_path = Path(runner.get("manifest_path") or DEFAULT_MANIFEST_PATH)
    resumed_max_specialist_calls = (
        max_specialist_calls
        if max_specialist_calls is not None
        else int(runner.get("max_specialist_calls") or 1)
    )
    directive_path = _resolve_resume_directive_path(
        runner, trial_id=trial_id, runs_root=runs_root
    )
    bundle_dir = _resolve_resume_bundle_dir(
        runner,
        trial_id=trial_id,
        runs_root=runs_root,
        directive_path=directive_path,
    )
    return _continue_production_walk(
        trial_id=trial_id,
        envelope=envelope,
        run_state=run_state,
        runner=runner,
        manifest_path=manifest_path,
        runs_root=runs_root,
        start_index=int(checkpoint["next_node_index"]),
        # The gate just approved is the last crossed until the walk traverses
        # further gates (offline mode); live mode pauses at the next gate.
        last_gate_crossed=verdict.gate_id,
        max_specialist_calls=resumed_max_specialist_calls,
        directive_path=directive_path,
        bundle_dir=bundle_dir,
        extra_artifacts=(run_dir / "resume-command.json",),
    )


def resume_batch_production_trial(
    *,
    trial_id: UUID,
    runs_root: Path = RUNS_ROOT,
    max_specialist_calls: int | None = None,
    adapter: LiteLlmBatchAdapter | None = None,
) -> ProductionTrialEnvelope:
    """Poll existing provider Batch receipt and continue when completed (B3).

    Never re-uploads. If still non-terminal, remains ``waiting_for_provider_batch``.
    Terminal failed/expired/cancelled fail loud.
    """

    from app.specialists.vision.batch_route import TERMINAL_STATUSES

    run_dir = _run_dir(trial_id, runs_root)
    envelope = ProductionTrialEnvelope.model_validate_json(
        (run_dir / "run.json").read_text(encoding="utf-8"),
        context={"anomaly_sink": run_dir / "anomalies.jsonl"},
    )
    # AD-17: reconcile-on-entry (re-emit run.json truth before anything else).
    _emit_operator_surface(envelope, runs_root)
    if envelope.status != "waiting_for_provider_batch":
        raise RuntimeError(
            f"trial {trial_id} is not waiting for a provider batch; "
            f"status={envelope.status!r} — use `trial resume-batch` only for "
            "waiting_for_provider_batch runs"
        )
    pause_path = run_dir / "provider-batch-pause.json"
    pause = json.loads(pause_path.read_text(encoding="utf-8"))
    if pause.get("trial_id") != str(trial_id):
        raise RuntimeError(
            "persisted provider-batch-pause record does not match the trial: "
            f"{pause.get('trial_id')!r} != {trial_id}"
        )
    batch_id = str(pause.get("batch_id") or envelope.waiting_batch_id or "")
    if not batch_id:
        raise RuntimeError(f"trial {trial_id} provider-batch-pause missing batch_id")

    receipt = read_receipt(runs_root, str(trial_id))
    client = adapter or LiteLlmBatchAdapter()
    batch_obj = client.retrieve_batch(batch_id)
    polled = normalize_batch_object(
        batch_obj,
        run_id=str(trial_id),
        row_count=receipt.row_count,
        model=receipt.model,
        submitted_at=receipt.submitted_at,
    )
    receipt = polled.model_copy(
        update={
            "submitted_at": receipt.submitted_at,
            "metadata": dict(receipt.metadata),
            "model": receipt.model or polled.model,
        }
    )
    write_receipt(runs_root, receipt)

    resume_receipt_path = run_dir / "trial-resume-batch.json"
    _write_json(
        resume_receipt_path,
        {
            "trial_id": str(trial_id),
            "batch_id": batch_id,
            "status": receipt.status,
            "still_waiting": receipt.status not in TERMINAL_STATUSES,
        },
    )

    if receipt.status not in TERMINAL_STATUSES:
        LOGGER.info(
            "trial %s batch %s still status=%s — remaining waiting_for_provider_batch",
            trial_id,
            batch_id,
            receipt.status,
        )
        return envelope.model_copy(
            update={
                "artifact_paths": _merge_artifact_paths(
                    envelope.artifact_paths, resume_receipt_path
                )
            }
        )

    if receipt.status != "completed":
        raise RuntimeError(
            f"provider batch {batch_id!r} ended status={receipt.status!r} "
            f"(tag=vision.batch.not-completed); no realtime fallback"
        )

    # Cost report is emitted again after vision join on continue; also emit a
    # receipt-only stub here if join has not run yet (fail-soft empty join).
    from app.runtime.llm_batch.join import JoinResult

    emit_batch_cost_report_fail_soft(
        runs_root=runs_root,
        receipt=receipt,
        joined=JoinResult(
            by_custom_id={},
            order_seen=(),
            missing_custom_ids=(),
            unexpected_custom_ids=(),
        ),
    )

    runner = pause.get("runner") or {}
    run_state = RunState.model_validate_json(json.dumps(pause["run_state"]))
    run_state = run_state.model_copy(
        update={"production_envelope": envelope.production_envelope}
    )
    directive_path = _resolve_resume_directive_path(
        runner, trial_id=trial_id, runs_root=runs_root
    )
    bundle_dir = _resolve_resume_bundle_dir(
        runner,
        trial_id=trial_id,
        runs_root=runs_root,
        directive_path=directive_path,
    )
    # Clear waiting stamp before continue so a later pause can re-set it.
    envelope = envelope.model_copy(
        update={
            "status": "in-flight",
            "waiting_batch_id": None,
            "paused_gate": None,
            "paused_error_tag": None,
        }
    )
    _persist_envelope(envelope, runs_root)
    return _continue_production_walk(
        trial_id=trial_id,
        envelope=envelope,
        run_state=run_state,
        runner=runner,
        manifest_path=Path(runner.get("manifest_path") or DEFAULT_MANIFEST_PATH),
        runs_root=runs_root,
        start_index=int(pause["node_index"]),
        last_gate_crossed=pause.get("last_gate_crossed"),
        max_specialist_calls=(
            max_specialist_calls
            if max_specialist_calls is not None
            else int(runner.get("max_specialist_calls") or 1)
        ),
        directive_path=directive_path,
        bundle_dir=bundle_dir,
        extra_artifacts=(resume_receipt_path,),
        non_evidence_reason="resumed-after-provider-batch",
    )


def recover_production_trial(
    *,
    trial_id: UUID,
    runs_root: Path = RUNS_ROOT,
    max_specialist_calls: int | None = None,
    reenter_at_node: str | None = None,
) -> ProductionTrialEnvelope:
    """Continue an error-paused trial from the failed node — no verdict needed.

    S4 part 2 (SCP 2026-06-11, Amelia trap 1): the recovery counterpart to
    ``resume_production_trial``. Gates carry operator verdicts; dispatch-error
    pauses carry none — the operator (or a wrapper) fixes the transient cause
    and re-enters the walk at the node that failed. Idempotent with respect to
    completed work: every prior contribution is per-node keyed, so recovery
    re-dispatches only the failed node and onward.

    Mine-next trust T2 (``recover-with-reenter-node-affordance``): when the fix
    is UPSTREAM of the failed node, pass ``reenter_at_node=<manifest node_id>``
    to drop contributions from that node through the failed index and restart
    the walk there. Default (``None``) preserves today's unshifted failed-node
    retry.
    """
    run_dir = _run_dir(trial_id, runs_root)
    envelope = ProductionTrialEnvelope.model_validate_json(
        (run_dir / "run.json").read_text(encoding="utf-8"),
        # Witness-mode lifecycle invariants: violations on persisted state are
        # recorded to the run's anomaly sidecar, never raised (S4p2 follow-on;
        # witness->strict flip is a post-S5 ceremony).
        context={"anomaly_sink": run_dir / "anomalies.jsonl"},
    )
    # AD-17: reconcile-on-entry (re-emit run.json truth before anything else).
    _emit_operator_surface(envelope, runs_root)
    if envelope.status != "paused-at-error":
        raise RuntimeError(
            f"trial {trial_id} is not paused at a dispatch error; "
            f"status={envelope.status!r} — `trial recover` only applies to "
            "error-paused runs (gate pauses take `trial resume` + a verdict)"
        )
    if envelope.production_envelope.schema_version == "production-envelope.v1":
        raise LegacyEnvelopeSchemaError(
            f"trial {trial_id} carries a production-envelope.v1 (per-specialist "
            "keyed) envelope; v1 runs are not recoverable after the S2 per-node "
            "keying migration (SCP 2026-06-11) — relaunch as a new cycle; the "
            "run dir stays frozen as evidence."
        )
    error_pause_path = run_dir / "error-pause.json"
    error_pause = json.loads(error_pause_path.read_text(encoding="utf-8"))
    if error_pause.get("trial_id") != str(trial_id):
        raise RuntimeError(
            "persisted error-pause record does not match the trial being "
            f"recovered: {error_pause.get('trial_id')!r} != {trial_id}"
        )
    runner = error_pause.get("runner") or {}
    run_state = RunState.model_validate_json(json.dumps(error_pause["run_state"]))
    run_state = run_state.model_copy(
        update={"production_envelope": envelope.production_envelope}
    )
    directive_path = _resolve_resume_directive_path(
        runner, trial_id=trial_id, runs_root=runs_root
    )
    bundle_dir = _resolve_resume_bundle_dir(
        runner,
        trial_id=trial_id,
        runs_root=runs_root,
        directive_path=directive_path,
    )
    failed_index = int(error_pause["node_index"])
    start_index = failed_index
    non_evidence_reason = "recovered-after-error-pause"
    if reenter_at_node is not None:
        selection = (
            run_state.component_selection or ComponentSelection.production_default()
        )
        manifest = compose_manifest(
            load_manifest(Path(runner.get("manifest_path") or DEFAULT_MANIFEST_PATH)),
            selection,
        )
        node_ids = [node.id for node in manifest.nodes]
        try:
            reenter_index = node_ids.index(reenter_at_node)
        except ValueError as exc:
            raise RuntimeError(
                f"reenter_at_node={reenter_at_node!r} is not a node in the "
                f"composed manifest for trial {trial_id}; known={node_ids}"
            ) from exc
        if reenter_index > failed_index:
            raise RuntimeError(
                f"reenter_at_node={reenter_at_node!r} is DOWNSTREAM of the "
                f"failed node (index {reenter_index} > failed {failed_index}); "
                "upstream re-entry only — omit the flag to retry the failed node"
            )
        drop_ids = set(node_ids[reenter_index : failed_index + 1])
        legacy_workbook_stub = (
            envelope.production_envelope.get_contribution(
                workbook_wiring.LEGACY_WORKBOOK_BRIEF_SPECIALIST_ID,
                node_id="07W.1",
            )
            if reenter_at_node == "07W.1"
            else None
        )
        dropped = envelope.production_envelope.drop_contributions_from_nodes(drop_ids)
        if legacy_workbook_stub is not None:
            envelope.production_envelope.add_contribution(legacy_workbook_stub)
        run_state = run_state.model_copy(
            update={"production_envelope": envelope.production_envelope}
        )
        # AD-2: the lone direct run.json bypass is routed through
        # _persist_envelope so the projection stays reconciled (byte-identical
        # envelope content — _persist_envelope writes the same
        # model_dump_json(indent=2) + "\n" this bypass used to write directly).
        _persist_envelope(envelope, runs_root)
        start_index = reenter_index
        non_evidence_reason = (
            f"recovered-reenter-at-node:{reenter_at_node}:dropped={dropped}"
        )
    return _continue_production_walk(
        trial_id=trial_id,
        envelope=envelope,
        run_state=run_state,
        runner=runner,
        manifest_path=Path(runner.get("manifest_path") or DEFAULT_MANIFEST_PATH),
        runs_root=runs_root,
        # Default: unshifted failed-node retry. With reenter_at_node: upstream.
        start_index=start_index,
        last_gate_crossed=error_pause.get("last_gate_crossed"),
        max_specialist_calls=(
            max_specialist_calls
            if max_specialist_calls is not None
            else int(runner.get("max_specialist_calls") or 1)
        ),
        directive_path=directive_path,
        bundle_dir=bundle_dir,
        non_evidence_reason=non_evidence_reason,
    )



def _continue_production_walk(
    *,
    trial_id: UUID,
    envelope: ProductionTrialEnvelope,
    run_state: RunState,
    runner: dict[str, Any],
    manifest_path: Path,
    runs_root: Path,
    start_index: int,
    last_gate_crossed: str | None,
    max_specialist_calls: int,
    directive_path: Path | None = None,
    bundle_dir: Path | None = None,
    extra_artifacts: tuple[Path, ...] = (),
    non_evidence_reason: str = "resumed-after-gate",
) -> ProductionTrialEnvelope:
    """Walk manifest nodes from ``start_index`` to the next pause or completion.

    Shared by ``resume_production_trial`` (post-verdict) and
    ``recover_production_trial`` (post-error-pause) so the continuation walk
    exists exactly once — the resume walker was already the A23 second copy
    of the start walk; a third copy for recovery was vetoed (S4 part 2,
    Winston d.2).
    """
    run_dir = _run_dir(trial_id, runs_root)
    # Two-walk trap: REHYDRATE the frozen component_selection from the run record
    # and recompose the SAME graph — never re-default. run_state was loaded from
    # the persisted checkpoint/error-pause by the caller, so its component_selection
    # is the selection the start walk froze.
    selection = run_state.component_selection or ComponentSelection.production_default()
    manifest = compose_manifest(load_manifest(manifest_path), selection)
    # AD-15: project the recomposed steps map at the continuation entry index.
    # An index REGRESSION vs the last-seen walk index (recover-reenter) is
    # inferred inside the assembler as a labeled re-entry (walk_generation++).
    _emit_operator_surface_steps(trial_id, runs_root, manifest, start_index)
    graph = compile_run_graph(manifest)
    adapter = ProductionDispatchAdapter()
    production_envelope = envelope.production_envelope
    child_runs = [
        _trace_run_for_contribution(trial_id=trial_id, contribution=contribution)
        for contribution in production_envelope.contributions
        # Deterministic §06 builder rows carry no LLM spend and no pricing
        # entry; in-segment they are never traced as child runs either —
        # seeding them here crashed cost recording on any continuation past
        # a builder node (latent since S3; surfaced by the S4p2 recover walk).
        if contribution.model_used != package_builders.BUILDER_MODEL_MARKER
    ]
    specialist_calls = 0
    allow_offline_cost_report = bool(runner.get("allow_offline_cost_report", False))
    graph_step_completed = bool(production_envelope.contributions)
    production_envelope = _apply_variant_selection(
        production_envelope,
        run_state,
    )
    run_state = run_state.model_copy(update={"production_envelope": production_envelope})

    # UDAC v1 (M-1): the continuation walk is entered with `last_gate_crossed` set
    # to the gate the operator just cleared (resume) / the error-pause gate
    # (recover). Marking that gate's ratified assets is a gate-crossing side-effect
    # that fires here in the continuation body (the start walk pauses at the first
    # active gate, so asset-bearing gates clear on THIS walk across the per-gate
    # resume loop). Disk-primary + rehydrate-reconcile-monotonic → both-walks parity
    # (M-5); a no-op when UDAC is OFF. Idempotent re-cross preserves ratified_at.
    _udac_ratify_gate(last_gate_crossed, trial_id, runs_root)

    # F-E2E-2: repopulate ambient sections at continuation entry — run_state was
    # rehydrated from the persisted checkpoint/error-pause, so its contributions
    # (specialist roster / live cost) and modes are known and must not read empty
    # on the HUD after a resume/recover.
    _refresh_operator_surface_ambient(
        trial_id,
        runs_root,
        run_state,
        trace_event=("walk-continue", f"resuming at index {start_index}"),
    )
    _continue_assembler = OperatorSurfaceAssembler(trial_id, runs_root)
    with _continue_assembler.freshness_tick(), _trial_trace_context(
        trial_id=trial_id,
        preset=runner.get("preset") or envelope.preset,
        operator_id=runner.get("operator_id") or envelope.operator_id,
    ) as trace_metadata:
        for index, node in enumerate(manifest.nodes[start_index:], start=start_index):
            # AD-15: advance the projected walk index as the continuation walk
            # progresses (node-lifecycle progress event; bumps progress_seq).
            _emit_operator_surface_steps(trial_id, runs_root, manifest, index)
            # F-E2E-2: refresh ambient sections + node-enter trace on the
            # continuation walk too (two-walk parity — the HUD must not go empty
            # after a resume/recover).
            _refresh_operator_surface_ambient(
                trial_id,
                runs_root,
                run_state,
                trace_event=("node-enter", str(node.id)),
            )
            handler = _active_node_handler(graph, node.id)
            node_kind = getattr(handler, "__production_node_kind__", None)
            if node_kind == "gate":
                gate_id = handler.__production_gate_id__
                if (
                    gate_id == g0_enrichment_wiring.G0_ENRICHMENT_GATE_CODE
                    and not g0_enrichment_wiring.g0_enrichment_active()
                ):
                    # AC-S2-7 (continuation-walk leg): traverse the asleep G0E gate
                    # so a resume/recover flow is byte-identical too (two-walk parity).
                    last_gate_crossed = gate_id
                    _udac_ratify_gate(gate_id, trial_id, runs_root)  # F3
                    graph_step_completed = True
                    continue
                if (
                    gate_id == irene_refinement_wiring.IRENE_REFINEMENT_GATE_CODE
                    and not irene_refinement_wiring.irene_refinement_active()
                ):
                    # AC-S3-4 (continuation-walk leg): traverse the asleep G0R ratify
                    # gate so a resume/recover flow is byte-identical too (two-walk
                    # parity, feature-flag parity with G0E).
                    last_gate_crossed = gate_id
                    _udac_ratify_gate(gate_id, trial_id, runs_root)  # F3
                    graph_step_completed = True
                    continue
                if allow_offline_cost_report:
                    # Offline runs traverse gates without pausing (existing
                    # contract); keep the pre-gate draft + trace append the
                    # prior code performed before continuing.
                    pending = [item.id for item in manifest.nodes[index + 1 :]]
                    pre_fill = _invoke_pre_gate_marcus_for_gate(
                        gate_id=gate_id,
                        trial_id=trial_id,
                        production_envelope=production_envelope,
                        pending_nodes=pending,
                        artifact_paths=envelope.artifact_paths,
                        allow_offline_cost_report=allow_offline_cost_report,
                    )
                    if pre_fill is not None:
                        child_runs.append(
                            _trace_run_for_pre_gate_marcus(
                                trial_id=trial_id,
                                gate_id=gate_id,
                                proposal=pre_fill,
                            )
                        )
                    last_gate_crossed = gate_id
                    _udac_ratify_gate(gate_id, trial_id, runs_root)  # F3 (offline branch)
                    graph_step_completed = True
                    continue
                # Trial-3 attempt-3 fix (2026-06-11): live resume previously
                # raised GateBypassError at EVERY gate — the pause machinery
                # existed only in the start walker, so no live trial could
                # ever advance gate-to-gate. The guard is deliberately
                # converted to the shared pause (the decided gate is never
                # revisited: start_index = checkpoint.next_node_index is
                # already past it, so this only fires at genuinely new gates).
                # S5 criterion 7: storyboard gates publish their online pack
                # before pausing — see start-walker note.
                try:
                    storyboard_publisher.publish_storyboard_for_gate(
                        gate_id=gate_id,
                        trial_id=str(trial_id),
                        production_envelope=production_envelope,
                        runs_root=runs_root,
                    )
                    # G2B is ALWAYS reached via this continuation walk (the start
                    # walk stops at the first gate, G1), so the per-slide chooser
                    # MUST publish here too — not only in the start walk. Without
                    # this, the Storyboard-A chooser never auto-publishes and the
                    # per-slide pick cannot be made (found 2026-06-24).
                    chooser_publisher.publish_chooser_for_gate(
                        gate_id=gate_id,
                        trial_id=str(trial_id),
                        production_envelope=production_envelope,
                        runs_root=runs_root,
                    )
                    # Coverage interlock (Step 4, R5-A7) — continuation/recover walk leg
                    # (the LIVE path; the start walk stops at G1). The IDENTICAL shared
                    # helper as the start walk (both-walks parity); no-op off-G3 /
                    # coverage-OFF. ``run_state`` is a RunState MODEL → pass its json
                    # model_dump so the marshaller reads plan_units/slide_briefs lineage.
                    coverage_runner._derive_and_write_coverage_receipt(
                        _run_dir(trial_id, runs_root),
                        gate_id,
                        run_state.model_dump(mode="json") if run_state is not None else None,
                    )
                except SpecialistDispatchError as exc:
                    return _pause_at_error(
                        error=exc,
                        node_id=node.id,
                        node_index=index,
                        specialist_id="storyboard_publisher",
                        trial_id=trial_id,
                        envelope=envelope,
                        production_envelope=production_envelope,
                        run_state=run_state,
                        child_runs=child_runs,
                        trace_metadata=trace_metadata,
                        last_gate_crossed=last_gate_crossed,
                        graph_step_completed=graph_step_completed,
                        specialist_calls=specialist_calls,
                        manifest_path=manifest_path,
                        runs_root=runs_root,
                        allow_offline_cost_report=allow_offline_cost_report,
                        max_specialist_calls=max_specialist_calls,
                        directive_path=directive_path,
                        bundle_dir=bundle_dir,
                    )
                return _pause_at_gate(
                    gate_id=gate_id,
                    node_id=node.id,
                    node_index=index,
                    manifest=manifest,
                    trial_id=trial_id,
                    operator_id=runner.get("operator_id") or envelope.operator_id,
                    envelope=envelope,
                    production_envelope=production_envelope,
                    run_state=run_state,
                    child_runs=child_runs,
                    trace_metadata=trace_metadata,
                    specialist_calls=len(production_envelope.contributions),
                    graph_step_completed=graph_step_completed,
                    manifest_path=manifest_path,
                    runs_root=runs_root,
                    allow_offline_cost_report=allow_offline_cost_report,
                    max_specialist_calls=max_specialist_calls,
                    directive_path=directive_path,
                    bundle_dir=bundle_dir,
                )

            if node.id in workbook_wiring.WORKBOOK_BAND_NODE_IDS:
                # 38.3b continuation/recover mirror: same unconditional helper,
                # exact-coordinate idempotency covers persisted/partial resumes.
                try:
                    production_envelope = workbook_wiring.run_workbook_band_node(
                        node_id=node.id,
                        production_envelope=production_envelope,
                        runtime_context=workbook_wiring.runtime_context_for_run(
                            runs_root / str(trial_id), node_id=node.id
                        ),
                    )
                except SpecialistDispatchError as exc:
                    return _pause_at_error(
                        error=exc,
                        node_id=node.id,
                        node_index=index,
                        specialist_id=workbook_wiring.WORKBOOK_BAND_SPECIALIST_IDS[
                            node.id
                        ],
                        trial_id=trial_id,
                        envelope=envelope,
                        production_envelope=production_envelope,
                        run_state=run_state,
                        child_runs=child_runs,
                        trace_metadata=trace_metadata,
                        last_gate_crossed=last_gate_crossed,
                        graph_step_completed=graph_step_completed,
                        specialist_calls=specialist_calls,
                        manifest_path=manifest_path,
                        runs_root=runs_root,
                        allow_offline_cost_report=allow_offline_cost_report,
                        max_specialist_calls=max_specialist_calls,
                        directive_path=directive_path,
                        bundle_dir=bundle_dir,
                    )
                run_state = run_state.model_copy(
                    update={"production_envelope": production_envelope}
                )
                graph_step_completed = True
                continue

            if (
                node_kind == "orchestration"
                and node.id in package_builders.BUILDER_NODE_IDS
                and _has_live_openai()
                and not allow_offline_cost_report
            ):
                # S3 §06 package builder — see start-walker note. WAVE-0
                # tranche 2 (2026-06-17): error-pause wrap mirrored onto the
                # recover walker so a §06 starvation pauses recoverably here
                # too — the recover path is the one most likely to re-enter a
                # still-starved node, so an unwrapped sibling would let it kill.
                try:
                    production_envelope = package_builders.run_builder_node(
                        node_id=node.id,
                        production_envelope=production_envelope,
                        runs_root=runs_root,
                        trial_id=trial_id,
                    )
                except SpecialistDispatchError as exc:
                    return _pause_at_error(
                        error=exc,
                        node_id=node.id,
                        node_index=index,
                        specialist_id=package_builders.BUILDER_SPECIALIST_ID,
                        trial_id=trial_id,
                        envelope=envelope,
                        production_envelope=production_envelope,
                        run_state=run_state,
                        child_runs=child_runs,
                        trace_metadata=trace_metadata,
                        last_gate_crossed=last_gate_crossed,
                        graph_step_completed=graph_step_completed,
                        specialist_calls=specialist_calls,
                        manifest_path=manifest_path,
                        runs_root=runs_root,
                        allow_offline_cost_report=allow_offline_cost_report,
                        max_specialist_calls=max_specialist_calls,
                        directive_path=directive_path,
                        bundle_dir=bundle_dir,
                    )
                run_state = run_state.model_copy(
                    update={"production_envelope": production_envelope}
                )
                graph_step_completed = True
                continue

            if (
                node_kind == "orchestration"
                and node.id in research_wiring.RESEARCH_WIRING_NODE_IDS
            ):
                # Braid S3 (option A) — CONTINUATION WALK leg. §04.55 plan-lock is
                # ALWAYS reached via this continuation walk (the start walk stops
                # at G1, which precedes §04.55), so the research-wiring side-effect
                # MUST fire here too — not only in the start walk. Mirrors the
                # storyboard/chooser-publisher both-walks parity. AC-D2 executes a
                # real continuation (resume) walk to prove this fires. The live
                # Texas fetch rides the MARCUS_RESEARCH_DISPATCH_LIVE toggle (S6 D1:
                # DEFAULT ON), read here too so the continuation walk honors it
                # (two-walk parity — §04.55 is ONLY reached on this walk on the
                # trial path). Creds-absent degrades VISIBLY at node entry (D4).
                try:
                    production_envelope = research_wiring.run_research_wiring(
                        node_id=node.id,
                        production_envelope=production_envelope,
                        posture_selector=research_wiring.DeterministicPostureSelector(),
                        dispatch_live=_research_dispatch_live(),
                    )
                except CitationFidelityError as exc:
                    # G2 FAIL mode (spec §3.4): unsourced citation error-pauses
                    # the continuation walk (recoverable) rather than crashing it.
                    return _pause_at_error(
                        error=SpecialistDispatchError(
                            f"G2 citation-fidelity FAIL: {exc} "
                            f"(unsourced_citations={exc.unsourced_citations})",
                            tag="citation_fidelity_fail",
                        ),
                        node_id=node.id,
                        node_index=index,
                        specialist_id=research_wiring.RESEARCH_WIRING_SPECIALIST_ID,
                        trial_id=trial_id,
                        envelope=envelope,
                        production_envelope=production_envelope,
                        run_state=run_state,
                        child_runs=child_runs,
                        trace_metadata=trace_metadata,
                        last_gate_crossed=last_gate_crossed,
                        graph_step_completed=graph_step_completed,
                        specialist_calls=specialist_calls,
                        manifest_path=manifest_path,
                        runs_root=runs_root,
                        allow_offline_cost_report=allow_offline_cost_report,
                        max_specialist_calls=max_specialist_calls,
                        directive_path=directive_path,
                        bundle_dir=bundle_dir,
                    )
                run_state = run_state.model_copy(
                    update={"production_envelope": production_envelope}
                )
                graph_step_completed = True
                continue

            if (
                node_kind == "orchestration"
                and node.id in g0_enrichment_wiring.G0_ENRICHMENT_NODE_IDS
                and g0_enrichment_wiring.g0_enrichment_active()
            ):
                # G0-S2 brick — CONTINUATION WALK leg (two-walk parity). The
                # g0-enrichment node sits before node 01, so on the trial path it
                # fires on the START walk; this mirror covers a resume/recover that
                # re-enters the node before the G0E gate (the storyboard/chooser +
                # research-wiring both-walks discipline). Idempotent: a node already
                # carrying its contribution is not re-run.
                try:
                    production_envelope = g0_enrichment_wiring.run_g0_enrichment(
                        node_id=node.id,
                        production_envelope=production_envelope,
                        corpus_dir=Path(envelope.corpus_path),
                        trial_id=trial_id,
                        runs_root=runs_root,
                        dispatch_live=(
                            g0_enrichment_wiring.g0_dispatch_live()
                            and _has_live_openai()
                            and not allow_offline_cost_report
                        ),
                    )
                except SpecialistDispatchError as exc:
                    return _pause_at_error(
                        error=exc,
                        node_id=node.id,
                        node_index=index,
                        specialist_id=g0_enrichment_wiring.G0_ENRICHMENT_SPECIALIST_ID,
                        trial_id=trial_id,
                        envelope=envelope,
                        production_envelope=production_envelope,
                        run_state=run_state,
                        child_runs=child_runs,
                        trace_metadata=trace_metadata,
                        last_gate_crossed=last_gate_crossed,
                        graph_step_completed=graph_step_completed,
                        specialist_calls=specialist_calls,
                        manifest_path=manifest_path,
                        runs_root=runs_root,
                        allow_offline_cost_report=allow_offline_cost_report,
                        max_specialist_calls=max_specialist_calls,
                        directive_path=directive_path,
                        bundle_dir=bundle_dir,
                    )
                run_state = run_state.model_copy(
                    update={"production_envelope": production_envelope}
                )
                graph_step_completed = True
                continue

            if (
                node_kind == "orchestration"
                and node.id in irene_refinement_wiring.IRENE_REFINEMENT_NODE_IDS
                and irene_refinement_wiring.irene_refinement_active()
            ):
                # G0-S3 brick — CONTINUATION WALK leg (two-walk parity). The
                # irene-refinement node sits before node 01 (after G0E), so on the
                # trial path it fires on the START walk; this mirror covers a
                # resume/recover that re-enters the node before the G0R gate.
                # Idempotent: a node already carrying its contribution is not re-run.
                try:
                    production_envelope = irene_refinement_wiring.run_irene_refinement(
                        node_id=node.id,
                        production_envelope=production_envelope,
                        trial_id=trial_id,
                        runs_root=runs_root,
                        dispatch_live=(
                            irene_refinement_wiring.ir_dispatch_live()
                            and _has_live_openai()
                            and not allow_offline_cost_report
                        ),
                    )
                except SpecialistDispatchError as exc:
                    return _pause_at_error(
                        error=exc,
                        node_id=node.id,
                        node_index=index,
                        specialist_id=irene_refinement_wiring.IRENE_REFINEMENT_SPECIALIST_ID,
                        trial_id=trial_id,
                        envelope=envelope,
                        production_envelope=production_envelope,
                        run_state=run_state,
                        child_runs=child_runs,
                        trace_metadata=trace_metadata,
                        last_gate_crossed=last_gate_crossed,
                        graph_step_completed=graph_step_completed,
                        specialist_calls=specialist_calls,
                        manifest_path=manifest_path,
                        runs_root=runs_root,
                        allow_offline_cost_report=allow_offline_cost_report,
                        max_specialist_calls=max_specialist_calls,
                        directive_path=directive_path,
                        bundle_dir=bundle_dir,
                    )
                run_state = run_state.model_copy(
                    update={"production_envelope": production_envelope}
                )
                graph_step_completed = True
                continue

            if (
                node_kind == "specialist"
                and specialist_calls < max_specialist_calls
            ):
                specialist_id = handler.__production_specialist_id__
                # S2 per-node keying — see start-walker note.
                if production_envelope.get_contribution(specialist_id, node_id=node.id) is not None:
                    LOGGER.info(
                        "manifest node %s (specialist %s) already carries its "
                        "contribution; node re-dispatch skipped per S2 "
                        "per-node idempotency contract",
                        node.id,
                        specialist_id,
                    )
                    graph_step_completed = True
                    continue
                if _has_live_openai() and not allow_offline_cost_report:
                    dispatched = _dispatch_specialist_catching_batch_wait(
                        adapter=adapter,
                        node=node,
                        manifest=manifest,
                        specialist_id=specialist_id,
                        production_envelope=production_envelope,
                        run_state=run_state,
                        child_runs=child_runs,
                        trial_id=trial_id,
                        runs_root=runs_root,
                        directive_path=directive_path,
                        bundle_dir=bundle_dir,
                        node_index=index,
                        envelope=envelope,
                        trace_metadata=trace_metadata,
                        last_gate_crossed=last_gate_crossed,
                        graph_step_completed=graph_step_completed,
                        specialist_calls=specialist_calls,
                        manifest_path=manifest_path,
                        allow_offline_cost_report=allow_offline_cost_report,
                        max_specialist_calls=max_specialist_calls,
                    )
                    if isinstance(dispatched, ProductionTrialEnvelope):
                        return dispatched
                    production_envelope, run_state = dispatched
                    specialist_calls += 1
                graph_step_completed = True

    completed_at = _now()
    trace_root = (
        _trace_root(
            trial_id=trial_id,
            metadata=trace_metadata,
            child_runs=child_runs,
        )
        if child_runs
        else None
    )
    cost_report_path = _record_cost(
        trial_id=trial_id,
        runs_root=runs_root,
        trace_root=trace_root,
        allow_offline_cost_report=allow_offline_cost_report,
    )
    trace_path = None
    if trace_root is not None:
        trace_path = run_dir / "trace-fixture.json"
        _write_json(trace_path, _trace_to_json(trace_root))
    langsmith_trace_id = (
        str(trial_id) if child_runs else envelope.langsmith_trace_id
    )
    run_summary_path = _emit_run_summary_yaml(
        trial_id=trial_id,
        # "G4" only as the legacy fallback for walks that crossed no gate at
        # all (e.g., recovery of a pre-G1 error pause in offline mode).
        terminal_gate=last_gate_crossed or "G4",
        runs_root=runs_root,
        manifest_path=manifest_path,
        langsmith_trace_id=langsmith_trace_id,
        selection=run_state.component_selection,
        composed_manifest=manifest,
    )
    engagement_report_path = _emit_engagement_decay_report(
        trial_id=trial_id,
        child_runs=child_runs,
    )
    evidence = _has_production_evidence(
        graph_step_completed=graph_step_completed,
        specialist_calls=len(production_envelope.contributions),
        allow_offline_cost_report=allow_offline_cost_report,
    )
    reason = "live-specialist-call-recorded" if evidence else non_evidence_reason
    updated = envelope.model_copy(
        update={
            "status": "completed",
            "completed_at": completed_at,
            "paused_gate": None,
            "paused_error_tag": None,
            "langsmith_trace_id": langsmith_trace_id,
            "production_clone_launch_evidence": evidence,
            "production_clone_launch_evidence_reason": reason,
            "production_envelope": production_envelope,
            "cost_report_path": cost_report_path,
            "artifact_paths": _merge_artifact_paths(
                envelope.artifact_paths,
                *extra_artifacts,
                cost_report_path,
                trace_path,
                run_summary_path,
                engagement_report_path,
            ),
        }
    )
    _persist_envelope(updated, runs_root)
    return updated


__all__ = [
    "DEFAULT_MANIFEST_PATH",
    "GateBypassError",
    "MissingUpstreamContributionError",
    "PreflightGateFailed",
    "apply_llm_execution_mode_overlay",
    "emit_registered_and_terminal_trace",
    "recover_production_trial",
    "resume_batch_production_trial",
    "resume_production_trial",
    "run_production_trial",
]
