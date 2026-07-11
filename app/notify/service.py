"""Notifier service — projection watcher + stall watchdog + push (Story 35.6).

ADs 9/10/18/19. The watcher polls ``operator-surface.json`` (open-read-close,
mtime-gated), lenient-parses it, and derives event classes ONLY through the
contract's :func:`derive_event_transitions`. The watchdog rides projection
monotonicity via the contract's :func:`stall_condition` plus a producer-dead
reading. Push fires through Apprise for push-enabled classes; on-HUD toast and
sound are the HUD page's job (channel split, AD-9).

Everything in this module is fault-tolerant: any failure — unreadable
projection, bad config, transport raising, corrupt state file — is logged and
swallowed, never raised into the caller's loop. The only public entry points a
caller needs are :class:`NotifierService` (construct once) and its
:meth:`NotifierService.poll_once` (call every tick).
"""

from __future__ import annotations

import json
import logging
import os
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from app.models.runtime.operator_surface import (
    OperatorSurfaceProjection,
    Unrecognized,
    derive_event_transitions,
    load_hud_config,
    read_operator_surface_lenient,
    stall_condition,
)

LOGGER = logging.getLogger(__name__)

#: The single projection filename inside a run dir (AD-1 naming convention).
PROJECTION_FILENAME = "operator-surface.json"

#: Repo root, resolved from this module's location so the notifier's own state
#: dir is stable regardless of the launching process's cwd.
_REPO_ROOT = Path(__file__).resolve().parents[2]

#: The notifier's OWN state dir (never the run dir — single-writer rule, AD-9).
DEFAULT_STATE_ROOT = _REPO_ROOT / "state" / "runtime" / "notify"

#: Canonical HUD config (AD-19). Used when no ``config_path`` is given so a
#: bare ``python -m app.notify`` picks up the operator's real opt-in matrix;
#: :func:`load_hud_config` already degrades to defaults (with reason) if absent.
DEFAULT_CONFIG_PATH = _REPO_ROOT / "state" / "config" / "hud-config.yaml"

#: Poll cadence (~2s) per AD-2 open-read-close consumer contract.
DEFAULT_POLL_INTERVAL_SECONDS = 2.0

#: Terminal envelope statuses that end the notifier's life (after a grace).
TERMINAL_STATUSES: frozenset[str] = frozenset({"completed", "failed"})

#: Push scheme allowlist (AD-9): Pushover + ntfy only. Email/webhook stay OUT
#: of v1 — adding a channel class is a scope change, not a config line.
ALLOWED_PUSH_SCHEMES: frozenset[str] = frozenset({"ntfy", "ntfys", "pover"})

#: Environment variable carrying comma-separated Apprise push URLs (creds live
#: here, NEVER in config or the repo).
PUSH_URLS_ENV = "HUD_PUSH_URLS"

#: Environment variable carrying the producer PID (for the producer-dead read).
PRODUCER_PID_ENV = "HUD_PRODUCER_PID"

#: Max delivery attempts for a push-enabled event before acking anyway with a
#: "push-failed" note (review S3 — a failed push must not silently ack, but it
#: must not retry forever either).
MAX_PUSH_ATTEMPTS = 3

#: Envelope statuses that mean "the run is parked awaiting the operator".
#: Observing any OTHER status closes the pause episode (review M1): the acked
#: pause keys are cleared so a later re-pause at the SAME gate fires again.
_PAUSED_STATUSES: frozenset[str] = frozenset({"paused-at-gate", "paused-at-error"})

#: Ack-key prefixes that belong to a pause episode (cleared on episode reset).
_PAUSE_ACK_PREFIXES: tuple[str, ...] = ("paused_at_gate:", "paused_at_error:")

#: Envelope status -> pause event class (retry path, review S3).
_PAUSE_CLASS_BY_STATUS: dict[str, str] = {
    "paused-at-gate": "paused_at_gate",
    "paused-at-error": "paused_at_error",
}


def _utcnow() -> datetime:
    return datetime.now(UTC)


def validate_push_urls(urls: list[str]) -> tuple[list[str], list[str]]:
    """Split ``urls`` into (accepted, rejected) by the scheme allowlist.

    A URL is accepted iff its scheme is in :data:`ALLOWED_PUSH_SCHEMES`. Any
    other scheme (``mailto``, ``json``, ``slack``, …) is rejected — email and
    webhook channels are explicitly out of v1 (AD-9). Never raises.
    """
    accepted: list[str] = []
    rejected: list[str] = []
    for url in urls:
        candidate = (url or "").strip()
        if not candidate:
            continue
        scheme = urlsplit(candidate).scheme.lower()
        if scheme in ALLOWED_PUSH_SCHEMES:
            accepted.append(candidate)
        else:
            rejected.append(candidate)
    return accepted, rejected


def _push_urls_from_env() -> list[str]:
    raw = os.environ.get(PUSH_URLS_ENV, "")
    return [part.strip() for part in raw.split(",") if part.strip()]


def _producer_pid_from_env() -> int | None:
    raw = os.environ.get(PRODUCER_PID_ENV, "").strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        LOGGER.warning("ignoring non-integer %s=%r", PRODUCER_PID_ENV, raw)
        return None


def _default_pid_alive(pid: int | None) -> bool:
    """Best-effort liveness probe. Unknown PID -> assume alive (never false-alarm).

    Cross-platform: Windows uses ``OpenProcess`` via ctypes; POSIX uses the
    ``kill(pid, 0)`` liveness signal. Any error resolves to "alive" EXCEPT the
    definitive "no such process" signals, so a flaky probe never manufactures a
    producer-dead alarm.
    """
    if pid is None:
        return True
    try:
        if sys.platform == "win32":
            import ctypes

            process_query_limited_information = 0x1000
            still_active = 259
            kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
            handle = kernel32.OpenProcess(process_query_limited_information, False, pid)
            if not handle:
                return False
            try:
                exit_code = ctypes.c_ulong()
                if kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
                    return exit_code.value == still_active
                return True
            finally:
                kernel32.CloseHandle(handle)
        else:
            os.kill(pid, 0)
            return True
    except ProcessLookupError:
        return False
    except PermissionError:
        # The process exists (we just may not signal it) -> alive.
        return True
    except OSError:
        return True


class _RealApprise:
    """Thin default transport wrapping :mod:`apprise` (imported lazily)."""

    def __init__(self) -> None:
        import apprise  # local import: only real push paths need the dependency

        self._apprise = apprise.Apprise()

    def add(self, url: str) -> bool:
        return bool(self._apprise.add(url))

    def notify(self, *, title: str, body: str) -> bool:
        return bool(self._apprise.notify(title=title, body=body))


@dataclass
class NotifierState:
    """The notifier's own persisted restart state (AD-9). NEVER in the run dir.

    ``acked`` maps an event key (pause/stall identity) to the ISO timestamp we
    first pushed it, so a restart mid-pause does not re-alert an already-handled
    condition; an unacknowledged active pause fires exactly once. Pause-episode
    keys are CLEARED when a non-paused status is observed (review M1) so a
    resume followed by a re-pause at the same gate alerts again.

    ``push_attempts`` counts failed delivery attempts per event key (review
    S3): a push-enabled event whose push failed is NOT acked (so the next poll
    retries) until :data:`MAX_PUSH_ATTEMPTS` is reached.
    """

    last_processed_progress_seq: int | None = None
    last_status: str | None = None
    acked: dict[str, str] = field(default_factory=dict)
    push_attempts: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "last_processed_progress_seq": self.last_processed_progress_seq,
            "last_status": self.last_status,
            "acked": dict(self.acked),
            "push_attempts": dict(self.push_attempts),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NotifierState:
        acked_raw = data.get("acked")
        acked = (
            {str(k): str(v) for k, v in acked_raw.items()}
            if isinstance(acked_raw, dict)
            else {}
        )
        attempts_raw = data.get("push_attempts")
        push_attempts = (
            {str(k): int(v) for k, v in attempts_raw.items() if isinstance(v, int)}
            if isinstance(attempts_raw, dict)
            else {}
        )
        seq = data.get("last_processed_progress_seq")
        status = data.get("last_status")
        return cls(
            last_processed_progress_seq=seq if isinstance(seq, int) else None,
            last_status=status if isinstance(status, str) else None,
            acked=acked,
            push_attempts=push_attempts,
        )


@dataclass(frozen=True)
class NotificationEvent:
    """One derived notification the service acted on this poll (test surface)."""

    event_class: str
    enabled: bool
    sound: bool
    push: bool
    pushed: bool
    reason: str | None = None


class NotifierService:
    """Stateless-per-tick projection watcher + watchdog + push (AD-9/10/18/19).

    Construct once with the bound ``trial_id`` + ``run_dir``; call
    :meth:`poll_once` every ~2s. The service reads the projection open-read-
    close (mtime-gated), derives events through the contract, honours the
    ``HudConfig`` opt-in matrix, pushes push-enabled classes through the
    injected Apprise transport, and evaluates the stall/producer-dead watchdog
    on every poll. No method raises.
    """

    def __init__(
        self,
        trial_id: str,
        run_dir: str | Path,
        *,
        config_path: str | Path | None = None,
        state_dir: str | Path | None = None,
        push_urls: list[str] | None = None,
        producer_pid: int | None = None,
        apprise_factory: Callable[[], Any] | None = None,
        pid_alive_fn: Callable[[int | None], bool] | None = None,
        now_fn: Callable[[], datetime] | None = None,
        on_event: Callable[[NotificationEvent], None] | None = None,
    ) -> None:
        self.trial_id = str(trial_id)
        self.run_dir = Path(run_dir)
        self.projection_path = self.run_dir / PROJECTION_FILENAME
        # No explicit path -> the repo-canonical config (review S2). The single
        # loader degrades to defaults (with the parse-status reason) if absent.
        self.config_path = Path(config_path) if config_path is not None else DEFAULT_CONFIG_PATH
        self.state_dir = Path(state_dir) if state_dir is not None else DEFAULT_STATE_ROOT
        self.state_path = self.state_dir / f"{self.trial_id}.json"
        self._now = now_fn or _utcnow
        self._on_event = on_event
        self._pid_alive = pid_alive_fn or _default_pid_alive
        self.producer_pid = producer_pid if producer_pid is not None else _producer_pid_from_env()

        # Config (single owner/loader/defaults — AD-19). Never raises.
        self.config, self.config_parse_status = load_hud_config(self.config_path)

        # Push transport. Scheme-allowlist BEFORE any target is added (AD-9).
        raw_urls = push_urls if push_urls is not None else _push_urls_from_env()
        self.push_targets, self.rejected_urls = validate_push_urls(raw_urls)
        for bad in self.rejected_urls:
            LOGGER.warning("rejecting push URL with disallowed scheme: %s", _redact(bad))
        self._apprise_factory = apprise_factory or _RealApprise
        self._apprise: Any | None = None  # lazily built on first push

        # Volatile in-process view.
        self._prev_projection: OperatorSurfaceProjection | None = None
        self._cur_projection: OperatorSurfaceProjection | None = None
        self._last_mtime_ns: int | None = None

        # Durable restart state.
        self.state = self._load_state()

    # -- state file ------------------------------------------------------

    def _load_state(self) -> NotifierState:
        try:
            text = self.state_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return NotifierState()
        except OSError as exc:
            LOGGER.warning("unreadable notifier state (%s) — starting fresh", type(exc).__name__)
            return NotifierState()
        try:
            data = json.loads(text)
        except (json.JSONDecodeError, ValueError):
            LOGGER.warning("corrupt notifier state — starting fresh")
            return NotifierState()
        if not isinstance(data, dict):
            return NotifierState()
        return NotifierState.from_dict(data)

    def _persist_state(self) -> None:
        try:
            self.state_dir.mkdir(parents=True, exist_ok=True)
            tmp = self.state_path.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(self.state.to_dict(), indent=2), encoding="utf-8")
            os.replace(tmp, self.state_path)
        except OSError:
            LOGGER.exception("failed to persist notifier state (continuing)")

    # -- projection read -------------------------------------------------

    def _read_projection(
        self,
    ) -> tuple[int | None, OperatorSurfaceProjection | Unrecognized | None]:
        """Open-read-close the projection once. (mtime_ns, parsed | None)."""
        try:
            with self.projection_path.open("rb") as handle:
                raw = handle.read()
                mtime_ns = os.fstat(handle.fileno()).st_mtime_ns
        except FileNotFoundError:
            return None, None
        except OSError as exc:
            LOGGER.warning("unreadable projection (%s)", type(exc).__name__)
            return None, Unrecognized(reason=f"unreadable ({type(exc).__name__})", raw_value=None)
        return mtime_ns, read_operator_surface_lenient(raw)

    # -- main tick -------------------------------------------------------

    def poll_once(self, now: datetime | None = None) -> list[NotificationEvent]:
        """Process one poll: transitions (on change) + watchdog (always).

        Returns the notification events acted on this poll. Never raises — any
        exception is logged and swallowed so the caller's loop keeps flying.
        """
        moment = now or self._now()
        events: list[NotificationEvent] = []
        attempted: set[str] = set()
        try:
            mtime_ns, parsed = self._read_projection()
            changed = mtime_ns != self._last_mtime_ns and mtime_ns is not None

            if changed:
                self._last_mtime_ns = mtime_ns
                if isinstance(parsed, OperatorSurfaceProjection):
                    events.extend(self._process_transition(parsed, moment, attempted))
                    self._prev_projection = parsed
                    self._cur_projection = parsed
                    self.state.last_processed_progress_seq = parsed.progress_seq
                    self.state.last_status = parsed.envelope.status
                    self._persist_state()
                elif isinstance(parsed, Unrecognized):
                    LOGGER.warning("skipping unrecognized projection: %s", parsed.reason)

            # Watchdog runs EVERY poll, incl. frozen ones (that is the point).
            events.extend(self._evaluate_watchdog(moment, mtime_frozen=not changed))
            # Failed-push retry (review S3) also runs every poll: an active
            # pause whose push never landed is re-attempted until it delivers
            # or MAX_PUSH_ATTEMPTS is exhausted.
            events.extend(self._retry_failed_pushes(moment, attempted))
        except Exception:  # noqa: BLE001 — the notifier must never propagate
            LOGGER.exception("unexpected error in poll_once (swallowed)")
        return events

    # -- transition-derived events (AD-18) -------------------------------

    def _process_transition(
        self, cur: OperatorSurfaceProjection, now: datetime, attempted: set[str]
    ) -> list[NotificationEvent]:
        self._reset_pause_episode(cur)
        acted: list[NotificationEvent] = []
        for event_class in derive_event_transitions(self._prev_projection, cur):
            key = self._ack_key(event_class, cur)
            deduped = event_class in ("paused_at_gate", "paused_at_error", "run_stalled")
            if deduped and key in self.state.acked:
                continue
            event = self._act(event_class, cur, now, reason=None)
            if event is None:
                continue
            if deduped:
                attempted.add(key)
                self._record_outcome(event, key, now)
            acted.append(event)
        return acted

    def _reset_pause_episode(self, cur: OperatorSurfaceProjection) -> None:
        """Close the pause episode on any non-paused status (review M1).

        Observing in-flight/completed/failed/waiting proves the prior pause was
        handled, so its acked keys (and any pending push-retry counters) are
        cleared — a later re-pause at the SAME gate must alert again. Restart
        dedup is untouched: a restart that observes a still-paused run never
        passes through a non-paused status, so its acks survive.
        """
        if cur.envelope.status in _PAUSED_STATUSES:
            return
        for store in (self.state.acked, self.state.push_attempts):
            for key in [k for k in store if k.startswith(_PAUSE_ACK_PREFIXES)]:
                del store[key]

    def _record_outcome(self, event: NotificationEvent, key: str, now: datetime) -> None:
        """Ack ``key`` — but NOT on a failed enabled push (review S3).

        A push-enabled event whose push did not deliver keeps its ack key open
        so the next poll retries, bounded by :data:`MAX_PUSH_ATTEMPTS`; on
        exhaustion the key is acked anyway with a "push-failed" note.
        """
        push_expected = event.push and bool(self.push_targets)
        if push_expected and not event.pushed:
            attempts = self.state.push_attempts.get(key, 0) + 1
            self.state.push_attempts[key] = attempts
            if attempts < MAX_PUSH_ATTEMPTS:
                LOGGER.warning(
                    "push failed for %s (attempt %d/%d) — will retry next poll",
                    key,
                    attempts,
                    MAX_PUSH_ATTEMPTS,
                )
                return
            LOGGER.warning(
                "push-failed: giving up on %s after %d attempts — acking", key, attempts
            )
            self.state.acked[key] = f"{now.isoformat()} push-failed"
            self.state.push_attempts.pop(key, None)
            return
        self.state.acked[key] = now.isoformat()
        self.state.push_attempts.pop(key, None)

    def _retry_failed_pushes(
        self, now: datetime, attempted: set[str]
    ) -> list[NotificationEvent]:
        """Re-attempt an active pause whose push failed earlier (review S3).

        Only pause classes need this path: ``run_stalled`` retries for free via
        the watchdog (its unacked key re-fires while the stall persists), and
        the on-HUD-only classes never gate their ack on push delivery.
        """
        cur = self._cur_projection
        if cur is None:
            return []
        event_class = _PAUSE_CLASS_BY_STATUS.get(cur.envelope.status)
        if event_class is None:
            return []
        key = self._ack_key(event_class, cur)
        if key in attempted or key in self.state.acked or key not in self.state.push_attempts:
            return []
        event = self._act(event_class, cur, now, reason=None)
        if event is None:
            return []
        self._record_outcome(event, key, now)
        self._persist_state()
        return [event]

    # -- watchdog (AD-10) ------------------------------------------------

    def _evaluate_watchdog(self, now: datetime, *, mtime_frozen: bool) -> list[NotificationEvent]:
        cur = self._cur_projection
        if cur is None:
            return []
        # Producer-dead reading: only meaningful while the projection is frozen
        # (a fresh write proves the producer is alive) and status is in-flight.
        if (
            mtime_frozen
            and cur.envelope.status == "in-flight"
            and self.producer_pid is not None
            and not self._pid_alive(self.producer_pid)
        ):
            return self._fire_stall(cur, now, reason="producer dead")
        # Frozen-progress stall (contract predicate; batch status exempt).
        if stall_condition(cur, now, self.config.stall_budget_seconds):
            return self._fire_stall(cur, now, reason="progress stalled")
        return []

    def _fire_stall(
        self, cur: OperatorSurfaceProjection, now: datetime, *, reason: str
    ) -> list[NotificationEvent]:
        key = self._ack_key("run_stalled", cur)
        if key in self.state.acked:
            return []
        event = self._act("run_stalled", cur, now, reason=reason)
        if event is None:
            return []
        self._record_outcome(event, key, now)
        self._persist_state()
        return [event]

    # -- act (config gate + push) ----------------------------------------

    def _act(
        self,
        event_class: str,
        cur: OperatorSurfaceProjection,
        now: datetime,
        *,
        reason: str | None,
    ) -> NotificationEvent | None:
        rule = self.config.notifications.get(event_class)  # type: ignore[arg-type]
        if rule is None:
            LOGGER.debug("no config rule for %s — skipping", event_class)
            return None
        if not rule.enabled:
            return None
        pushed = False
        if rule.push:
            pushed = self._push(event_class, cur, reason)
        event = NotificationEvent(
            event_class=event_class,
            enabled=rule.enabled,
            sound=rule.sound,
            push=rule.push,
            pushed=pushed,
            reason=reason,
        )
        if self._on_event is not None:
            try:
                self._on_event(event)
            except Exception:  # noqa: BLE001 — a bad sink must not break the loop
                LOGGER.exception("on_event sink raised (swallowed)")
        return event

    def _push(
        self, event_class: str, cur: OperatorSurfaceProjection, reason: str | None
    ) -> bool:
        if not self.push_targets:
            return False
        try:
            transport = self._ensure_transport()
        except Exception:  # noqa: BLE001 — transport build must never propagate
            LOGGER.exception("failed to build push transport (swallowed)")
            return False
        if transport is None:
            return False
        title, body = _compose(event_class, cur, reason)
        try:
            return bool(transport.notify(title=title, body=body))
        except Exception:  # noqa: BLE001 — a raising transport is a swallowed fault
            LOGGER.exception("push transport raised for %s (swallowed)", event_class)
            return False

    def _ensure_transport(self) -> Any | None:
        if self._apprise is None:
            transport = self._apprise_factory()
            for url in self.push_targets:
                try:
                    transport.add(url)
                except Exception:  # noqa: BLE001
                    LOGGER.exception("failed to add push URL (swallowed)")
            self._apprise = transport
        return self._apprise

    # -- helpers ---------------------------------------------------------

    def _ack_key(self, event_class: str, cur: OperatorSurfaceProjection) -> str:
        if event_class == "paused_at_gate":
            return f"paused_at_gate:{cur.envelope.paused_gate}"
        if event_class == "paused_at_error":
            return f"paused_at_error:{cur.envelope.paused_error_tag}"
        if event_class == "run_stalled":
            return f"run_stalled:{cur.progress_seq}"
        return f"{event_class}:{cur.progress_seq}"

    def current_status(self) -> str | None:
        if self._cur_projection is None:
            return self.state.last_status
        return self._cur_projection.envelope.status

    def is_terminal(self) -> bool:
        return self.current_status() in TERMINAL_STATUSES


def _compose(
    event_class: str, cur: OperatorSurfaceProjection, reason: str | None
) -> tuple[str, str]:
    """Push copy per EXPERIENCE.md §Notifications. Push tells the operator to
    come look — it never carries a verdict affordance."""
    lesson = cur.identity.lesson
    node = _current_node(cur)
    if event_class == "paused_at_gate":
        gate = cur.envelope.paused_gate or "?"
        return (
            f"Gate {gate} awaits your verdict",
            f"{lesson} · gate {gate} parked — come look at the HUD.",
        )
    if event_class == "paused_at_error":
        tag = cur.envelope.paused_error_tag or "?"
        return (
            f"Run paused at error {tag}",
            f"{lesson} · error {tag} — recoverable, see the HUD.",
        )
    if event_class == "batch_pause_resumed":
        return ("Batch landed — run resumed", f"{lesson} · resumed at {node}.")
    if event_class == "health_threshold":
        return (
            "Health threshold crossed",
            f"{lesson} · a health tile crossed its threshold — see HUD.",
        )
    if event_class == "run_stalled":
        why = reason or "progress stalled"
        return (
            "Run quiet — worth a look",
            f"{lesson} · nominally in flight at {node} but {why}. Worth a look.",
        )
    return (event_class, f"{lesson} · {event_class}")


def _current_node(cur: OperatorSurfaceProjection) -> str:
    if cur.steps is not None and cur.steps.entries:
        idx = cur.steps.walk_index
        if 0 <= idx < len(cur.steps.entries):
            return cur.steps.entries[idx].step_id
    return "the current step"


def _redact(url: str) -> str:
    """Show only the scheme + host of a push URL in logs — never credentials."""
    parts = urlsplit(url)
    host = parts.hostname or ""
    return f"{parts.scheme}://{host}/…" if parts.scheme else "<malformed url>"


__all__ = [
    "ALLOWED_PUSH_SCHEMES",
    "DEFAULT_CONFIG_PATH",
    "DEFAULT_POLL_INTERVAL_SECONDS",
    "DEFAULT_STATE_ROOT",
    "MAX_PUSH_ATTEMPTS",
    "PROJECTION_FILENAME",
    "PRODUCER_PID_ENV",
    "PUSH_URLS_ENV",
    "TERMINAL_STATUSES",
    "NotificationEvent",
    "NotifierService",
    "NotifierState",
    "validate_push_urls",
]
