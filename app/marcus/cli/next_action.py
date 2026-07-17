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

#: Canonical closed decision-verb set for a standard DecisionCard gate, mirroring
#: ``app.models.decision_cards.base.DecisionCardVerb`` = ``approve | edit | reject``.
#: Kept as a stdlib-only literal (this module must not import the pydantic
#: decision-card package). A gate's allowed set is THREADED from the card on disk
#: when it carries an explicit ``allowed_verbs`` list; otherwise this closed set is
#: the default. Ordering is presentation order, NOT preference — no verb is the
#: default (Story 42.1 finding G: the next-action must not preselect a verdict).
_DEFAULT_GATE_VERBS: tuple[str, ...] = ("approve", "edit", "reject")

#: Per-verb placeholder suffix appended so the paste line is completable but never
#: pre-filled with a fabricated verdict payload.
_VERB_PAYLOAD_HINT: dict[str, str] = {
    "edit": " --edit-payload '<edit-json>'",
    "reject": " --reject-reason '<reason>'",
    "select": " --edit-payload '<selection-json>'",
}


def _read_card_fields(card_path: Path | None) -> tuple[str, str, tuple[str, ...]]:
    """Return ``(card_id, decision_card_digest, allowed_verbs)`` from the card json.

    The runner writes ``decision-card-<gate>.json`` as
    ``{"card": {...card_id...}, "digest": ...}`` before the pause emit, so the
    file is reliably present at build time. Missing/garbage input degrades to
    empty strings + the default verb set (logged) rather than raising — the
    assembler wraps this.

    ``allowed_verbs`` is threaded from an explicit ``card.allowed_verbs`` list
    when present (future gates may differ, e.g. a confirm-only gate); otherwise it
    defaults to the canonical closed set :data:`_DEFAULT_GATE_VERBS`.
    """
    if card_path is None:
        return "", "", _DEFAULT_GATE_VERBS
    try:
        payload: dict[str, Any] = json.loads(card_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        LOGGER.warning("next-action: unreadable decision card %s: %s", card_path, exc)
        return "", "", _DEFAULT_GATE_VERBS
    card = payload.get("card")
    card_id = ""
    allowed: tuple[str, ...] = _DEFAULT_GATE_VERBS
    if isinstance(card, dict):
        card_id = str(card.get("card_id") or "")
        declared = card.get("allowed_verbs")
        if isinstance(declared, (list, tuple)) and declared:
            allowed = tuple(str(v) for v in declared)
    digest = str(payload.get("digest") or "")
    return card_id, digest, allowed


def _render_neutral_gate_next_action(
    *,
    trial_id: str,
    gate_id: str,
    card_id: str,
    digest: str,
    operator_id: str,
    allowed_verbs: tuple[str, ...],
) -> str:
    """Build the NEUTRAL next-step surface for a ``paused-at-gate`` pause (finding G).

    Emits one ``trial resume ... --verb <v> ...`` paste line PER allowed verb,
    presented without bias — the operator completes the concrete command by
    picking a verb. The card id + digest ride EVERY line so any choice is
    actionable. No single verb is preselected as THE next action, and the copy
    honors "Marcus proposes; you decide."
    """
    base = (
        "trial resume"
        f" --trial-id {shlex.quote(trial_id)}"
        f" --gate-id {shlex.quote(gate_id)}"
    )
    tail = (
        f" --card-id {shlex.quote(card_id)}"
        f" --decision-card-digest {shlex.quote(digest)}"
        f" --operator-id {shlex.quote(operator_id)}"
    )
    header = (
        f"Paused at gate {gate_id or '(unknown)'} — choose ONE verdict "
        "(Marcus proposes; you decide):"
    )
    lines = [header]
    for verb in allowed_verbs:
        lines.append(f"  # {verb}:")
        lines.append(f"  {base} --verb {verb}{tail}{_VERB_PAYLOAD_HINT.get(verb, '')}")
    return "\n".join(lines)


def build_next_action(envelope: Any, card_path: Path | None = None) -> str:
    """Build the exact next-action command string for the envelope's pause class.

    Raises ``ValueError`` if the envelope is not in a pause class (callers
    should only invoke it for paused statuses).
    """
    status = envelope.status
    trial_id = str(envelope.trial_id)

    if status == "paused-at-gate":
        gate_id = str(envelope.paused_gate or "")
        card_id, digest, allowed_verbs = _read_card_fields(card_path)
        operator_id = str(envelope.operator_id)
        return _render_neutral_gate_next_action(
            trial_id=trial_id,
            gate_id=gate_id,
            card_id=card_id,
            digest=digest,
            operator_id=operator_id,
            allowed_verbs=allowed_verbs,
        )

    if status == "paused-at-error":
        return f"trial recover --trial-id {shlex.quote(trial_id)}"

    if status == "waiting_for_provider_batch":
        return f"trial resume-batch --trial-id {shlex.quote(trial_id)}"

    raise ValueError(f"build_next_action called for non-pause status {status!r}")


__all__ = ["build_next_action"]
