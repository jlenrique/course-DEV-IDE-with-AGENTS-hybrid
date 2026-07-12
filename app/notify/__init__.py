"""Operator HUD notifier package (Epic 35 / Story 35.6).

The push + watchdog lane of the single-writer projected read model
(ARCHITECTURE-SPINE.md ADs 9/10/18/19). It runs as its **own OS process**
(launched by the start path, never fate-shared with the runtime session's
Python process) so the watchdog cannot die with what it guards. It consumes
the runtime-owned ``operator-surface.json`` projection and
``state/config/hud-config.yaml`` ONLY, deriving the five v1 event classes
through the contract's ``derive_event_transitions`` / ``stall_condition`` —
this package never re-implements derivation and never strict-parses (AD-4/18).

Channel split (AD-9): this lane owns **push** (through Apprise URL strings —
Pushover primary, ntfy fallback, env-only credentials). On-HUD toast + sound
are the HUD page's, driven from the config echo in the projection. Notifier
failures never propagate — the loop is fault-tolerant by construction.

Layer rule: imports nothing from ``app.marcus``, ``app.hud``, or
``app.gates`` — only the contract package (+ stdlib + apprise).
"""

from __future__ import annotations

from app.notify.service import (
    ALLOWED_PUSH_SCHEMES,
    DEFAULT_POLL_INTERVAL_SECONDS,
    DEFAULT_STATE_ROOT,
    NotificationEvent,
    NotifierService,
    NotifierState,
    validate_push_urls,
)

__all__ = [
    "ALLOWED_PUSH_SCHEMES",
    "DEFAULT_POLL_INTERVAL_SECONDS",
    "DEFAULT_STATE_ROOT",
    "NotificationEvent",
    "NotifierService",
    "NotifierState",
    "validate_push_urls",
]
