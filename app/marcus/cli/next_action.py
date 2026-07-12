"""Next-action command builder, co-located with the CLI grammar (Epic 35 / 35.2).

Architecture spine AD-3: the HUD never composes commands and the runner never
freehands them — the exact copy-paste command per pause class comes from THIS
builder, which lives beside the CLI definitions it targets:

* ``paused-at-gate`` -> ``trial resume ...`` inline-verdict mode (grammar in
  ``app.marcus.cli.trial``). The former ``gate decide ...`` target read an
  in-memory ``_CARD_STORE`` that is empty cross-process and never drove the
  walk, so a freshly-pasted command failed ``card_missing`` (F-E2E-1). The
  ``trial resume`` inline path builds the ``OperatorVerdict`` from the flags and
  reuses the proven disk-rehydration + walk-continuation of ``--verdict-file``.
* ``paused-at-error`` -> ``trial recover ...`` (grammar in ``app.marcus.cli.trial``)
* ``waiting_for_provider_batch`` -> ``trial resume-batch ...`` (same grammar)

An L1 test round-trips every built string through the ACTUAL argparse parsers,
so a renamed flag fails the producer (this builder), never the operator.

This module imports stdlib only — no heavy CLI/runtime imports — so the
assembler can import it lazily without dragging in ``app.marcus.cli``'s package
init (which imports ``trial`` -> ``production_runner``).
"""

from __future__ import annotations

import json
import logging
import shlex
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger(__name__)


def _read_card_fields(card_path: Path | None) -> tuple[str, str]:
    """Return ``(card_id, decision_card_digest)`` from the decision-card json.

    The runner writes ``decision-card-<gate>.json`` as
    ``{"card": {...card_id...}, "digest": ...}`` before the pause emit, so the
    file is reliably present at build time. Missing/garbage input degrades to
    empty strings (logged) rather than raising — the assembler wraps this.
    """
    if card_path is None:
        return "", ""
    try:
        payload: dict[str, Any] = json.loads(card_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        LOGGER.warning("next-action: unreadable decision card %s: %s", card_path, exc)
        return "", ""
    card = payload.get("card")
    card_id = ""
    if isinstance(card, dict):
        card_id = str(card.get("card_id") or "")
    digest = str(payload.get("digest") or "")
    return card_id, digest


def build_next_action(envelope: Any, card_path: Path | None = None) -> str:
    """Build the exact next-action command string for the envelope's pause class.

    Raises ``ValueError`` if the envelope is not in a pause class (callers
    should only invoke it for paused statuses).
    """
    status = envelope.status
    trial_id = str(envelope.trial_id)

    if status == "paused-at-gate":
        gate_id = str(envelope.paused_gate or "")
        card_id, digest = _read_card_fields(card_path)
        operator_id = str(envelope.operator_id)
        return (
            "trial resume"
            f" --trial-id {shlex.quote(trial_id)}"
            f" --gate-id {shlex.quote(gate_id)}"
            " --verb approve"
            f" --card-id {shlex.quote(card_id)}"
            f" --decision-card-digest {shlex.quote(digest)}"
            f" --operator-id {shlex.quote(operator_id)}"
        )

    if status == "paused-at-error":
        return f"trial recover --trial-id {shlex.quote(trial_id)}"

    if status == "waiting_for_provider_batch":
        return f"trial resume-batch --trial-id {shlex.quote(trial_id)}"

    raise ValueError(f"build_next_action called for non-pause status {status!r}")


__all__ = ["build_next_action"]
