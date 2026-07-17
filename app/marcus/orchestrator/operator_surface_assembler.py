"""Operator-surface projection assembler (Epic 35 / Story 35.2).

The single writer of ``state/config/runs/<trial_id>/operator-surface.json``
(architecture spine AD-2 / AD-15 / AD-17). This module owns:

* ``OperatorSurfaceAssembler`` — a **stateless, construct-on-demand** writer
  keyed ``(trial_id, runs_root)`` (greenlight amendment 13). It does a
  read-merge-write of the existing projection through the contract's lenient
  reader + a strict re-serialize, so no singleton and no per-trial global is
  needed — which dissolves the standing two-walk gotcha (a pause side-effect
  landing in one walk and not the other): each walk simply constructs an
  assembler and writes; the on-disk document IS the state.
* ``seq`` (bumped on EVERY write) and ``progress_seq`` (bumped ONLY on progress
  events — envelope status/pause-identity transitions, walk-index change, node
  lifecycle, pre-flight item completion; NEVER on freshness ticks or health
  refreshes) per AD-10.
* Atomic writes (temp file + ``os.replace``) with a bounded retry — on Windows
  ``os.replace`` raises ``PermissionError`` while a reader holds the file open;
  on retry exhaustion the write **logs and skips, never propagates into the
  walk** (``run.json`` remains truth per AD-17; the next tick self-heals).
* A ``freshness_tick`` context manager: a daemon thread that writes a tick
  (``seq`` bump + ``as_of`` refresh, NO ``progress_seq``) every ~2s while the
  ``with`` block is open, stopped in a guaranteed ``finally``.

Every public method is wrapped so that no exception ever escapes into the
runner walk (greenlight amendment 8): failures are logged and swallowed.

Layer rule: this module imports the contract package, stdlib, and PyYAML
(``run_summary.yaml`` is YAML — the contract package already depends on PyYAML)
only. The CLI-co-located next-action builder is imported **lazily** inside
``emit`` to avoid an import cycle with ``app.marcus.cli`` (whose package
``__init__`` imports ``trial`` → ``production_runner``).
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import threading
import time
from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager, suppress
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

import yaml

from app.models.runtime.operator_surface import (
    DecisionCardSection,
    DeliverableComponents,
    DeliverablesSection,
    DraftedProposal,
    EnvelopeSection,
    ErrorMessageSection,
    HealthSection,
    HealthTile,
    IdentitySection,
    ModalitiesSection,
    NextActionSection,
    NotificationsEchoSection,
    OperatorSurfaceProjection,
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
    load_hud_config,
    read_operator_surface_lenient,
)

LOGGER = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_HUD_CONFIG_PATH = REPO_ROOT / "state" / "config" / "hud-config.yaml"

PROJECTION_FILENAME = "operator-surface.json"

#: Run-dir artifacts the pause/completion emit maps 1:1 into the projection
#: (Story 35.9). Every read is guarded — a missing/garbage artifact yields a
#: ``None`` section, never a raise into the walk (greenlight amendment 8).
ERROR_PAUSE_FILENAME = "error-pause.json"
RUN_SUMMARY_FILENAME = "run_summary.yaml"
DIRECTIVE_FILENAME = "directive.yaml"
COST_REPORT_FILENAME = "cost-report.json"
COST_REPORT_TRANSACTION_FILENAME = "cost-report-transaction.v1.json"
EXPORTS_DIRNAME = "exports"

#: Env truthiness convention (matches udac_wiring / g0_enrichment_wiring /
#: enrichment_consumption verbatim). A toggle env var is "on" iff its stripped
#: lowercased value is in this set; absent/anything-else → "off" (never a
#: missing key — Story 42.3 AC-3).
_ENV_TRUTHY: frozenset[str] = frozenset({"1", "true", "yes", "on"})

#: Environment-var name for the voice-direction toggle (run config; folded into
#: the run-settings readout as an on/off resolved default when the directive
#: carries no explicit ``voice_direction`` value).
_VOICE_DIRECTION_ENV = "MARCUS_NARRATION_VOICE_DIRECTION_ACTIVE"

#: Bound on any resolved run-settings display string (AD-16 anti-bloat).
_RUN_SETTING_MAX_CHARS = 240

#: Bounds so the additive sections cannot reopen the 525KB run.json trap (AD-16).
_CONTEXT_ENTRY_MAX_CHARS = 240
_MAX_EXPORT_PATHS = 40

#: Bounded retry for ``os.replace`` under a concurrent open reader (AD-2).
_REPLACE_RETRIES = 5
_REPLACE_BACKOFF_S = 0.02

#: Freshness-tick interval — must be <= the minimum staleness budget (AD-2: 2s).
_FRESHNESS_TICK_INTERVAL_S = 2.0

# --------------------------------------------------------------------------
# Module-level per-trial write lock (AD-15: writes serialize through one lock)
# --------------------------------------------------------------------------

_LOCKS: dict[str, threading.Lock] = {}
_LOCKS_GUARD = threading.Lock()


def _lock_for(trial_id: UUID | str) -> threading.Lock:
    key = str(trial_id)
    with _LOCKS_GUARD:
        lock = _LOCKS.get(key)
        if lock is None:
            lock = threading.Lock()
            _LOCKS[key] = lock
        return lock


def _now() -> datetime:
    return datetime.now(UTC)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _run_json_digest(envelope: Any) -> str:
    """Digest of the exact bytes ``_persist_envelope`` writes to run.json (AD-17)."""
    return _sha256_text(envelope.model_dump_json(indent=2) + "\n")


# --------------------------------------------------------------------------
# Run-settings resolver (Story 42.3) — the ONE deterministic place mapping each
# of the 16 canonical toggles to its resolved display value.
#
# Pure + I/O-guarded: reads env + the run-dir ``directive.yaml`` /
# ``run_summary.yaml`` + the prior projection (for run_state-carried values
# already on the surface — llm_execution_mode, preset). It NEVER reaches into
# ``run_state`` directly (that lives in the runner, off the assembler's sole-
# writer lane) and NEVER raises. The section it returns is a pure projection of
# resolved settings, so a double-emit on identical inputs is byte-identical
# apart from ``as_of`` (AC-3). One source of truth with the canonical list:
# ``RUN_SETTINGS_TOGGLES`` names the fields; this resolver fills them.
# --------------------------------------------------------------------------


def _safe_yaml_mapping(path: Path) -> dict[str, Any]:
    """Read a YAML file into a mapping; missing/garbage → ``{}`` (never raises)."""
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 — a missing/garbage artifact is not fatal
        return {}
    return raw if isinstance(raw, dict) else {}


def _env_flag(env: Mapping[str, str], name: str) -> str:
    """Resolve an env toggle to an explicit ``"on"``/``"off"`` (never missing)."""
    return "on" if (env.get(name) or "").strip().lower() in _ENV_TRUTHY else "off"


def _str_or_unset(value: Any) -> str:
    """A present non-empty scalar → its bounded str; otherwise ``"unset"``."""
    if value is None:
        return "unset"
    text = str(value).strip()
    return text[:_RUN_SETTING_MAX_CHARS] if text else "unset"


def _component_state(selection: Mapping[str, Any], key: str) -> str:
    """Component-selection bool → ``"on"``/``"off"``; missing → ``"unset"``."""
    value = selection.get(key)
    if isinstance(value, bool):
        return "on" if value else "off"
    return "unset"


def _treatment_slots(directive: Mapping[str, Any]) -> str:
    """Styleguide picks (treatment slots A/B) from the directive; else ``unset``."""
    names: list[str] = []
    raw = directive.get("gamma_settings")
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, dict):
                styleguide = item.get("styleguide")
                if isinstance(styleguide, str) and styleguide.strip():
                    names.append(styleguide.strip())
    joined = ", ".join(dict.fromkeys(names))
    if joined:
        return joined[:_RUN_SETTING_MAX_CHARS]
    return _str_or_unset(directive.get("treatment_slots"))


def resolve_run_settings(
    run_dir: Path,
    prev: OperatorSurfaceProjection | None,
    now: datetime,
    *,
    env: Mapping[str, str] | None = None,
) -> RunSettingsSection:
    """Resolve all 16 run-defining toggles into a ``RunSettingsSection`` (AC-1/3).

    Deterministic given (env, run_dir artifacts, prev). Every field resolves to
    an explicit value — env-absent toggles read ``"off"``, unknown non-env
    settings read ``"unset"`` — so the readout never carries a missing key.
    """
    env = os.environ if env is None else env
    directive = _safe_yaml_mapping(run_dir / DIRECTIVE_FILENAME)
    run_summary = _safe_yaml_mapping(run_dir / RUN_SUMMARY_FILENAME)
    selection = run_summary.get("component_selection")
    selection = selection if isinstance(selection, dict) else {}

    # Preset + llm_execution_mode are already resolved onto the surface by the
    # envelope/modalities writers (run_state-sourced); prefer them, then the
    # directive, then an explicit default — never reaching into run_state here.
    preset = directive.get("preset")
    if prev is not None:
        preset = prev.identity.preset
    llm_mode = None
    if prev is not None and prev.modalities is not None:
        llm_mode = prev.modalities.llm_execution_mode
    if not llm_mode:
        llm_mode = directive.get("llm_execution_mode")

    voice = directive.get("voice_direction")
    voice_direction = (
        _str_or_unset(voice)
        if voice not in (None, "")
        else _env_flag(env, _VOICE_DIRECTION_ENV)
    )
    coverage = directive.get("coverage_gate")
    if coverage in (None, ""):
        coverage = directive.get("coverage_gate_family")

    return RunSettingsSection(
        as_of=now,
        component_deck=_component_state(selection, "deck"),
        component_motion=_component_state(selection, "motion"),
        component_workbook=_component_state(selection, "workbook"),
        preset=_str_or_unset(preset),
        encounter_mode=_str_or_unset(directive.get("encounter_mode")),
        llm_execution_mode=_str_or_unset(llm_mode),
        g0_dispatch_live=_env_flag(env, "MARCUS_G0_DISPATCH_LIVE"),
        research_dispatch_live=_env_flag(env, "MARCUS_RESEARCH_DISPATCH_LIVE"),
        research_detective_live=_env_flag(env, "MARCUS_RESEARCH_DETECTIVE_LIVE"),
        narration_figure_fidelity_active=_env_flag(
            env, "MARCUS_NARRATION_FIGURE_FIDELITY_ACTIVE"
        ),
        voice_direction=voice_direction,
        deck_enrichment_active=_env_flag(env, "MARCUS_DECK_ENRICHMENT_ACTIVE"),
        udac_active=_env_flag(env, "MARCUS_UDAC_ACTIVE"),
        coverage_gate=_str_or_unset(coverage),
        trial_budget_usd=_str_or_unset(env.get("MARCUS_TRIAL_BUDGET_USD")),
        treatment_slots=_treatment_slots(directive),
    )


class OperatorSurfaceAssembler:
    """Sole writer of the operator-surface projection (AD-15).

    Stateless construct-on-demand: all state lives in the on-disk document;
    every write is a read-merge-write under the per-trial lock.
    """

    def __init__(
        self,
        trial_id: UUID | str,
        runs_root: Path,
        *,
        hud_config_path: Path | None = None,
    ) -> None:
        self.trial_id = trial_id
        self.runs_root = Path(runs_root)
        self.hud_config_path = hud_config_path or DEFAULT_HUD_CONFIG_PATH
        self._lock = _lock_for(trial_id)

    # -- paths -------------------------------------------------------------

    @property
    def run_dir(self) -> Path:
        return self.runs_root / str(self.trial_id)

    @property
    def projection_path(self) -> Path:
        return self.run_dir / PROJECTION_FILENAME

    # -- low-level read/write ---------------------------------------------

    def _read_prev(self) -> OperatorSurfaceProjection | None:
        """Return the current on-disk projection, or ``None`` if absent/garbage."""
        try:
            raw = self.projection_path.read_bytes()
        except OSError:
            return None
        parsed = read_operator_surface_lenient(raw)
        if isinstance(parsed, OperatorSurfaceProjection):
            return parsed
        if isinstance(parsed, Unrecognized):
            LOGGER.warning(
                "operator-surface at %s unrecognized (%s) — rebuilding fresh",
                self.projection_path,
                parsed.reason,
            )
        return None

    def _atomic_write(self, text: str) -> bool:
        """temp file + ``os.replace`` with bounded retry; exhaustion logs+skips."""
        self.run_dir.mkdir(parents=True, exist_ok=True)
        tmp = self.projection_path.with_name(
            f"{PROJECTION_FILENAME}.tmp.{os.getpid()}.{threading.get_ident()}"
        )
        try:
            tmp.write_text(text, encoding="utf-8", newline="\n")
        except OSError as exc:
            LOGGER.warning("operator-surface temp write failed for %s: %s", tmp, exc)
            return False
        last_exc: Exception | None = None
        for _ in range(_REPLACE_RETRIES):
            try:
                os.replace(tmp, self.projection_path)
                return True
            except PermissionError as exc:  # Windows: reader holds file open
                last_exc = exc
                time.sleep(_REPLACE_BACKOFF_S)
        LOGGER.warning(
            "operator-surface replace exhausted %d retries for %s (%s) — "
            "logged and skipped; run.json remains truth, next tick self-heals",
            _REPLACE_RETRIES,
            self.projection_path,
            last_exc,
        )
        with suppress(OSError):
            tmp.unlink()
        return False

    # -- core merge --------------------------------------------------------

    def _merge_write(
        self,
        *,
        build: Callable[[OperatorSurfaceProjection | None, datetime], dict[str, Any]],
        progress: Callable[[OperatorSurfaceProjection | None], bool],
        require_prev: bool,
    ) -> bool:
        """Read-merge-write under the per-trial lock. Returns True on write."""
        with self._lock:
            prev = self._read_prev()
            if prev is None and require_prev:
                # No projection to refresh/extend yet — the next envelope emit
                # establishes it. Refresh-only / section calls are no-ops here.
                return False
            now = _now()
            base: dict[str, Any] = (
                prev.model_dump(mode="json") if prev is not None else {}
            )
            updates = build(prev, now)
            base.update(updates)

            is_progress = progress(prev)
            base["schema_version"] = "v1"
            base["seq"] = (prev.seq + 1) if prev is not None else 0
            # The first-ever write establishes progress_seq at its 0 baseline;
            # subsequent progress events increment it (AD-10).
            base["progress_seq"] = (
                0 if prev is None else prev.progress_seq + (1 if is_progress else 0)
            )
            if is_progress or prev is None or "last_progress_at" not in base:
                base["last_progress_at"] = now.isoformat()
            base["as_of"] = now.isoformat()

            try:
                # Strict re-serialize (witness-mode lifecycle invariants: no
                # strict context, so presence violations log, never raise).
                projection = OperatorSurfaceProjection.model_validate(base)
            except Exception as exc:  # noqa: BLE001 — writer must never raise
                LOGGER.exception(
                    "operator-surface merge produced an invalid projection for "
                    "trial %s: %s",
                    self.trial_id,
                    exc,
                )
                return False
            return self._atomic_write(projection.model_dump_json(indent=2) + "\n")

    # -- notifications echo helper ----------------------------------------

    def _notifications_echo_dict(self, now: datetime) -> dict[str, Any]:
        config, parse_status = load_hud_config(self.hud_config_path)
        return NotificationsEchoSection(
            as_of=now, config=config, parse_status=parse_status
        ).model_dump(mode="json")

    def _ensure_notifications_echo(
        self, prev: OperatorSurfaceProjection | None, now: datetime
    ) -> dict[str, Any]:
        if prev is not None and prev.notifications_echo is not None:
            return prev.notifications_echo.model_dump(mode="json")
        return self._notifications_echo_dict(now)

    # -- public API: envelope transition emit (AD-2) ----------------------

    def emit(self, envelope: Any) -> bool:
        """Project an envelope transition. Never raises (amendment 8)."""
        try:
            digest = _run_json_digest(envelope)

            def _progress(prev: OperatorSurfaceProjection | None) -> bool:
                if prev is None:
                    return True
                pe = prev.envelope
                return (
                    pe.status != envelope.status
                    or pe.paused_gate != envelope.paused_gate
                    or pe.paused_error_tag != envelope.paused_error_tag
                    or pe.waiting_batch_id != getattr(envelope, "waiting_batch_id", None)
                )

            def _build(
                prev: OperatorSurfaceProjection | None, now: datetime
            ) -> dict[str, Any]:
                updates: dict[str, Any] = {
                    "envelope_digest": digest,
                    "identity": IdentitySection(
                        as_of=now,
                        trial_id=envelope.trial_id,
                        lesson=envelope.corpus_path,
                        preset=envelope.preset,
                        operator_id=envelope.operator_id,
                    ).model_dump(mode="json"),
                    "envelope": EnvelopeSection(
                        as_of=now,
                        status=envelope.status,
                        paused_gate=envelope.paused_gate,
                        paused_error_tag=envelope.paused_error_tag,
                        waiting_batch_id=getattr(envelope, "waiting_batch_id", None),
                        completed_at=envelope.completed_at,
                    ).model_dump(mode="json"),
                    "notifications_echo": self._ensure_notifications_echo(prev, now),
                    "next_action": self._next_action_dict(envelope, now),
                    # Story 35.9 — verb-conditional sections mapped 1:1 from the
                    # run-dir artifacts. Each returns None off its trigger status
                    # so the field CLEARS on transition (same as next_action).
                    "decision_card": self._decision_card_dict(envelope, now),
                    "error_message": self._error_message_dict(envelope, now),
                    "deliverables": self._deliverables_dict(envelope, now),
                }
                return updates

            return self._merge_write(
                build=_build, progress=_progress, require_prev=False
            )
        except Exception:  # noqa: BLE001 — emit must never raise into the walk
            LOGGER.exception(
                "operator-surface emit failed for trial %s — swallowed", self.trial_id
            )
            return False

    def _next_action_dict(self, envelope: Any, now: datetime) -> dict[str, Any] | None:
        status = envelope.status
        if status not in ("paused-at-gate", "paused-at-error", "waiting_for_provider_batch"):
            return None
        try:
            # Lazy import: avoids the app.marcus.cli package-init import cycle.
            from app.marcus.cli.next_action import build_next_action

            card_path: Path | None = None
            if status == "paused-at-gate" and envelope.paused_gate:
                card_path = self.run_dir / f"decision-card-{envelope.paused_gate}.json"
            command = build_next_action(envelope, card_path=card_path)
        except Exception:  # noqa: BLE001 — a builder failure must not sink emit
            LOGGER.exception(
                "next-action builder failed for trial %s (status=%s)",
                self.trial_id,
                status,
            )
            return None
        return NextActionSection(
            as_of=now, command=command, pause_class=status
        ).model_dump(mode="json")

    # -- Story 35.9: decision-card / error / deliverables (verb-conditional) --

    @staticmethod
    def _summarize_context_entry(entry: Any) -> str:
        """One pick_context/evidence entry -> one short display string (1:1).

        Precedence: a concrete artifact ``path`` > voice-option names > a
        ``kind (node_id)`` tag > the raw value. Bounded so a fat card cannot
        bloat the projection (AD-16).
        """
        text: str
        if isinstance(entry, dict):
            path = entry.get("path")
            voices = entry.get("voices")
            if isinstance(path, str) and path:
                text = path
            elif isinstance(voices, list) and voices:
                names = [
                    str(v.get("voice_name"))
                    for v in voices
                    if isinstance(v, dict) and v.get("voice_name")
                ]
                text = "voice options: " + ", ".join(names) if names else "voice options"
            else:
                kind = entry.get("kind")
                node = entry.get("node_id")
                if kind and node:
                    text = f"{kind} ({node})"
                else:
                    text = str(kind or node or entry.get("voice_name") or "context")
        else:
            text = str(entry)
        return text[:_CONTEXT_ENTRY_MAX_CHARS]

    def _decision_card_dict(self, envelope: Any, now: datetime) -> dict[str, Any] | None:
        """Map ``decision-card-{gate}.json`` -> DecisionCardSection at a gate pause."""
        if envelope.status != "paused-at-gate" or not envelope.paused_gate:
            return None
        try:
            path = self.run_dir / f"decision-card-{envelope.paused_gate}.json"
            card = json.loads(path.read_text(encoding="utf-8")).get("card")
            if not isinstance(card, dict):
                return None
            proposal = None
            dp = card.get("drafted_proposal")
            if isinstance(dp, dict):
                conf = dp.get("confidence")
                confidence = (
                    float(conf)
                    if isinstance(conf, (int, float)) and 0.0 <= float(conf) <= 1.0
                    else None
                )
                proposal = DraftedProposal(
                    decision=dp.get("decision"),
                    confidence=confidence,
                    rationale=dp.get("rationale"),
                )
            pick_context = [
                self._summarize_context_entry(e)
                for e in (card.get("pick_context") or [])
            ]
            evidence = [
                self._summarize_context_entry(e) for e in (card.get("evidence") or [])
            ]
            return DecisionCardSection(
                as_of=now,
                gate_focus=card.get("gate_focus"),
                operator_prompt=card.get("operator_prompt"),
                drafted_proposal=proposal,
                pick_context=pick_context,
                evidence=evidence,
            ).model_dump(mode="json")
        except Exception:  # noqa: BLE001 — a missing/garbage card never sinks emit
            LOGGER.exception(
                "decision-card map failed for trial %s (gate=%s) — section omitted",
                self.trial_id,
                envelope.paused_gate,
            )
            return None

    def _error_message_dict(self, envelope: Any, now: datetime) -> dict[str, Any] | None:
        """Map ``error-pause.json`` -> ErrorMessageSection at an error pause."""
        if envelope.status != "paused-at-error":
            return None
        try:
            path = self.run_dir / ERROR_PAUSE_FILENAME
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                return None
            raw_index = data.get("node_index")
            node_index = int(raw_index) if isinstance(raw_index, (int, float)) else None
            message = data.get("message")
            return ErrorMessageSection(
                as_of=now,
                message=str(message) if message is not None else None,
                node_index=node_index,
                tag=data.get("tag"),
            ).model_dump(mode="json")
        except Exception:  # noqa: BLE001 — a missing/garbage artifact never sinks emit
            LOGGER.exception(
                "error-pause map failed for trial %s — section omitted", self.trial_id
            )
            return None

    def _deliverables_dict(self, envelope: Any, now: datetime) -> dict[str, Any] | None:
        """Map run_summary + cost-report + exports -> DeliverablesSection on completion.

        Each of the three reads is INDEPENDENTLY guarded so a missing cost
        report never suppresses the component booleans, and vice versa
        (greenlight amendment 8). MINIMAL export enumeration only (KEY DECISION
        2 waiver): top-level ``exports/`` entries, not a rich per-artifact walk.
        """
        if envelope.status != "completed":
            return None
        try:
            components = self._read_component_selection()
            total_cost_usd = self._read_total_cost()
            export_paths = self._read_export_paths()
            if components is None and total_cost_usd is None and not export_paths:
                return None
            return DeliverablesSection(
                as_of=now,
                components=components,
                total_cost_usd=total_cost_usd,
                export_paths=export_paths,
            ).model_dump(mode="json")
        except Exception:  # noqa: BLE001
            LOGGER.exception(
                "deliverables map failed for trial %s — section omitted", self.trial_id
            )
            return None

    def _read_component_selection(self) -> DeliverableComponents | None:
        try:
            raw = yaml.safe_load(
                (self.run_dir / RUN_SUMMARY_FILENAME).read_text(encoding="utf-8")
            )
            sel = raw.get("component_selection") if isinstance(raw, dict) else None
            if not isinstance(sel, dict):
                return None
            return DeliverableComponents(
                deck=sel.get("deck") if isinstance(sel.get("deck"), bool) else None,
                motion=sel.get("motion") if isinstance(sel.get("motion"), bool) else None,
                workbook=(
                    sel.get("workbook") if isinstance(sel.get("workbook"), bool) else None
                ),
            )
        except Exception:  # noqa: BLE001
            LOGGER.warning(
                "run_summary component_selection unreadable for trial %s", self.trial_id
            )
            return None

    def _read_total_cost(self) -> float | None:
        try:
            if (self.run_dir / COST_REPORT_TRANSACTION_FILENAME).exists():
                return None
            raw_report = (self.run_dir / COST_REPORT_FILENAME).read_text(encoding="utf-8")
            data = json.loads(raw_report)
            if (
                not isinstance(data, dict)
                or "cost_posture" not in data
                or "unavailable_attempt_count" not in data
            ):
                return None
            from app.models.runtime import TrialEconomicsReport

            validated = TrialEconomicsReport.model_validate_json(raw_report)
            return validated.total_cost_usd if validated.cost_posture == "exact" else None
        except Exception:  # noqa: BLE001
            LOGGER.warning("cost-report total_cost_usd unreadable for trial %s", self.trial_id)
            return None

    def _read_export_paths(self) -> list[str]:
        try:
            exports = self.run_dir / EXPORTS_DIRNAME
            if not exports.is_dir():
                return []
            names = sorted(p.name for p in exports.iterdir())
            return [f"{EXPORTS_DIRNAME}/{n}" for n in names[:_MAX_EXPORT_PATHS]]
        except Exception:  # noqa: BLE001
            LOGGER.warning("exports enumeration failed for trial %s", self.trial_id)
            return []

    # -- public API: steps section (AD-15) --------------------------------

    def update_steps(
        self,
        manifest: Any,
        walk_index: int,
        *,
        hud_tracked_ids: set[str] | None = None,
    ) -> bool:
        """Project the two-stage you-are-here map + composed-manifest identity.

        ``walk_generation`` / ``reentered_from`` are inferred from an observed
        walk-index REGRESSION (recover-reenter), so the runner need not thread
        generation markers through its continuation-walk signatures.
        """
        try:
            nodes = list(getattr(manifest, "nodes", []) or [])
            node_ids = [str(node.id) for node in nodes]
            digest = _sha256_text("|".join(node_ids))
            node_count = len(nodes)

            def _progress(prev: OperatorSurfaceProjection | None) -> bool:
                if prev is None or prev.steps is None:
                    return True
                return (
                    prev.steps.walk_index != walk_index
                    or prev.steps.manifest_digest != digest
                    or prev.steps.node_count != node_count
                )

            def _build(
                prev: OperatorSurfaceProjection | None, now: datetime
            ) -> dict[str, Any]:
                walk_generation = 0
                reentered_from: int | None = None
                if prev is not None and prev.steps is not None:
                    walk_generation = prev.steps.walk_generation
                    reentered_from = prev.steps.reentered_from
                    if walk_index < prev.steps.walk_index:
                        walk_generation = prev.steps.walk_generation + 1
                        # The index the run re-entered FROM is the previous
                        # (higher) walk position, per the contract field
                        # description (review S2).
                        reentered_from = prev.steps.walk_index
                entries: list[dict[str, Any]] = []
                for idx, node in enumerate(nodes):
                    if idx < walk_index:
                        step_status = "complete"
                    elif idx == walk_index:
                        step_status = "active"
                    else:
                        step_status = "pending"
                    is_hud = bool(getattr(node, "hud_tracked", False)) or (
                        hud_tracked_ids is not None and str(node.id) in hud_tracked_ids
                    )
                    entries.append(
                        StepEntry(
                            step_id=str(node.id),
                            label=getattr(node, "label", None) or str(node.id),
                            stage="stage-2" if is_hud else "stage-1",
                            status=step_status,
                        ).model_dump(mode="json")
                    )
                return {
                    "steps": StepsSection(
                        as_of=now,
                        manifest_digest=digest,
                        node_count=node_count,
                        walk_index=walk_index,
                        walk_generation=walk_generation,
                        reentered_from=reentered_from,
                        entries=[],
                    ).model_dump(mode="json")
                    | {"entries": entries},
                }

            return self._merge_write(
                build=_build, progress=_progress, require_prev=True
            )
        except Exception:  # noqa: BLE001
            LOGGER.exception("update_steps failed for trial %s — swallowed", self.trial_id)
            return False

    # -- public API: preflight section (AD-11) ----------------------------

    def update_preflight_item(self, item: PreflightItem | dict[str, Any]) -> bool:
        """Merge one pre-flight/heartbeat item (progress event per AD-10)."""
        try:
            model = (
                item
                if isinstance(item, PreflightItem)
                else PreflightItem.model_validate(item)
            )
            item_dict = model.model_dump(mode="json")

            def _build(
                prev: OperatorSurfaceProjection | None, now: datetime
            ) -> dict[str, Any]:
                items: list[dict[str, Any]] = []
                if prev is not None and prev.preflight is not None:
                    items = [
                        it.model_dump(mode="json")
                        for it in prev.preflight.items
                        if it.name != model.name
                    ]
                items.append(item_dict)
                return {
                    "preflight": PreflightSection(as_of=now, items=[]).model_dump(
                        mode="json"
                    )
                    | {"items": items}
                }

            return self._merge_write(
                build=_build, progress=lambda prev: True, require_prev=True
            )
        except Exception:  # noqa: BLE001
            LOGGER.exception(
                "update_preflight_item failed for trial %s — swallowed", self.trial_id
            )
            return False

    # -- public API: health section (NOT a progress event, AD-10) ---------

    def update_health(self, tiles: list[HealthTile | dict[str, Any]]) -> bool:
        """Refresh the health strip. Bumps ``seq`` only, never ``progress_seq``."""
        try:
            tile_dicts = [
                (t if isinstance(t, HealthTile) else HealthTile.model_validate(t)).model_dump(
                    mode="json"
                )
                for t in tiles
            ]

            def _build(
                prev: OperatorSurfaceProjection | None, now: datetime
            ) -> dict[str, Any]:
                return {
                    "health": HealthSection(as_of=now, tiles=[]).model_dump(mode="json")
                    | {"tiles": tile_dicts}
                }

            return self._merge_write(
                build=_build, progress=lambda prev: False, require_prev=True
            )
        except Exception:  # noqa: BLE001
            LOGGER.exception(
                "update_health failed for trial %s — swallowed", self.trial_id
            )
            return False

    # -- public API: ambient sections (health/specialists/modalities/trace) --

    def update_ambient(
        self,
        *,
        health_tiles: list[HealthTile | dict[str, Any]] | None = None,
        specialist_roster: list[SpecialistEntry | dict[str, Any]] | None = None,
        modalities: ModalitiesSection | dict[str, Any] | None = None,
        trace_event: tuple[str, str | None] | None = None,
    ) -> bool:
        """Refresh the ambient (non-progress) HUD sections in ONE merge-write.

        Populates the health strip (FR9), specialist chips (FR7), modality chips
        (FR10), and appends one state-trace event (FR8) — the four sections the
        walk otherwise left empty mid-run (F-E2E-2). A ``None`` argument leaves
        that section untouched (prev value preserved); an argument that is a
        present-but-empty list still WRITES the (empty) section so a run with no
        contributions yet renders a present-but-empty projection, never a null.

        Never a progress event (AD-10: ``seq`` bumps, ``progress_seq`` does not —
        these are ambient refreshes, not walk advances). Never raises into the
        walk (greenlight amendment 8): a bad tile/entry logs and skips.
        """
        try:
            tile_dicts: list[dict[str, Any]] | None = None
            if health_tiles is not None:
                tile_dicts = [
                    (
                        t
                        if isinstance(t, HealthTile)
                        else HealthTile.model_validate(t)
                    ).model_dump(mode="json")
                    for t in health_tiles
                ]
            roster_dicts: list[dict[str, Any]] | None = None
            if specialist_roster is not None:
                roster_dicts = [
                    (
                        s
                        if isinstance(s, SpecialistEntry)
                        else SpecialistEntry.model_validate(s)
                    ).model_dump(mode="json")
                    for s in specialist_roster
                ]

            if (
                tile_dicts is None
                and roster_dicts is None
                and modalities is None
                and trace_event is None
            ):
                return False

            def _build(
                prev: OperatorSurfaceProjection | None, now: datetime
            ) -> dict[str, Any]:
                built: dict[str, Any] = {}
                # Story 42.3 — the standing run-settings readout rides EVERY
                # ambient refresh (both walks call this same path), so all ~16
                # toggles are present from launch through terminal. Resolution
                # is independently guarded: a failure here must never drop the
                # other ambient sections (amendment 8).
                try:
                    built["run_settings"] = resolve_run_settings(
                        self.run_dir, prev, now
                    ).model_dump(mode="json")
                except Exception:  # noqa: BLE001 — never sink the ambient write
                    LOGGER.exception(
                        "run-settings resolve failed for trial %s — readout skipped",
                        self.trial_id,
                    )
                if tile_dicts is not None:
                    built["health"] = HealthSection(
                        as_of=now, tiles=[]
                    ).model_dump(mode="json") | {"tiles": tile_dicts}
                if roster_dicts is not None:
                    built["specialists"] = SpecialistsSection(
                        as_of=now, roster=[]
                    ).model_dump(mode="json") | {"roster": roster_dicts}
                if modalities is not None:
                    if isinstance(modalities, ModalitiesSection):
                        section = modalities.model_copy(update={"as_of": now})
                    else:
                        section = ModalitiesSection(as_of=now, **modalities)
                    built["modalities"] = section.model_dump(mode="json")
                if trace_event is not None:
                    event, detail = trace_event
                    events: list[dict[str, Any]] = []
                    if prev is not None and prev.trace is not None:
                        events = [e.model_dump(mode="json") for e in prev.trace.events]
                    events.append(
                        TraceEvent(at=now, event=event, detail=detail).model_dump(
                            mode="json"
                        )
                    )
                    built["trace"] = TraceSection(
                        as_of=now, events=[]
                    ).model_dump(mode="json") | {"events": events}
                return built

            return self._merge_write(
                build=_build, progress=lambda prev: False, require_prev=True
            )
        except Exception:  # noqa: BLE001
            LOGGER.exception(
                "update_ambient failed for trial %s — swallowed", self.trial_id
            )
            return False

    # -- public API: trace ring (AD-16) -----------------------------------

    def append_trace(
        self, event: str, detail: str | None = None, at: datetime | None = None
    ) -> bool:
        """Append one state-trace event (ring-buffer capped in the contract)."""
        try:
            new_event = TraceEvent(at=at or _now(), event=event, detail=detail)

            def _build(
                prev: OperatorSurfaceProjection | None, now: datetime
            ) -> dict[str, Any]:
                events: list[dict[str, Any]] = []
                if prev is not None and prev.trace is not None:
                    events = [e.model_dump(mode="json") for e in prev.trace.events]
                events.append(new_event.model_dump(mode="json"))
                return {
                    "trace": TraceSection(as_of=now, events=[]).model_dump(mode="json")
                    | {"events": events}
                }

            return self._merge_write(
                build=_build, progress=lambda prev: False, require_prev=True
            )
        except Exception:  # noqa: BLE001
            LOGGER.exception(
                "append_trace failed for trial %s — swallowed", self.trial_id
            )
            return False

    # -- public API: notifications echo (AD-9/19) -------------------------

    def set_notifications_echo(self) -> bool:
        """Re-read hud-config.yaml and echo it (+ parse status) into the projection."""
        try:

            def _build(
                prev: OperatorSurfaceProjection | None, now: datetime
            ) -> dict[str, Any]:
                return {"notifications_echo": self._notifications_echo_dict(now)}

            return self._merge_write(
                build=_build, progress=lambda prev: False, require_prev=True
            )
        except Exception:  # noqa: BLE001
            LOGGER.exception(
                "set_notifications_echo failed for trial %s — swallowed", self.trial_id
            )
            return False

    # -- public API: freshness tick (AD-2) --------------------------------

    def _freshness_tick_once(self) -> bool:
        """One tick: ``seq`` bump + ``as_of`` refresh only. No progress_seq."""
        try:
            return self._merge_write(
                build=lambda prev, now: {},
                progress=lambda prev: False,
                require_prev=True,
            )
        except Exception:  # noqa: BLE001
            LOGGER.exception(
                "freshness tick failed for trial %s — swallowed", self.trial_id
            )
            return False

    @contextmanager
    def freshness_tick(
        self, interval: float = _FRESHNESS_TICK_INTERVAL_S
    ) -> Iterator[None]:
        """Daemon-thread freshness ticker for the duration of the ``with`` block.

        Guaranteed to stop in ``finally`` on every pause/terminal/raise path.
        """
        stop = threading.Event()

        def _loop() -> None:
            while not stop.wait(interval):
                self._freshness_tick_once()

        thread = threading.Thread(
            target=_loop, name=f"operator-surface-tick-{self.trial_id}", daemon=True
        )
        started = False
        try:
            # A thread that cannot start (resource pressure) degrades to
            # no-tick — it must never raise into the paid walk (review MUST-1;
            # amendment 8).
            try:
                thread.start()
                started = True
            except Exception:
                LOGGER.exception(
                    "operator-surface freshness tick failed to start; "
                    "continuing without ticks (trial=%s)",
                    self.trial_id,
                )
            yield
        finally:
            stop.set()
            if started:
                with suppress(Exception):
                    thread.join(timeout=interval + 1.0)


__all__ = [
    "DEFAULT_HUD_CONFIG_PATH",
    "OperatorSurfaceAssembler",
    "PROJECTION_FILENAME",
    "resolve_run_settings",
]
