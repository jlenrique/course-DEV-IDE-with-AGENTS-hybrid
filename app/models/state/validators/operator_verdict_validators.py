"""Cross-field validators for `OperatorVerdict` (FR31 + FR34 tamper-evidence).

Two invariants live here as standalone testable functions:

1. `enforce_no_tamper_verbs` — the second of the triple-layer red-rejection
   for the FR34 tamper-evidence guarantee. Even though the `Literal[
   "approve", "edit", "reject"]` field type makes tamper verbs unconstructible
   via the normal path, this re-check fires on `validate_assignment=True`
   mutations and on any future code path that bypasses the `Literal` (e.g.,
   `model_construct` for raw dict ingest). The schema-pin test is the third
   layer.

2. `enforce_verb_payload_consistency` — `verb == "edit"` REQUIRES `edit_payload`
   non-None; `verb == "reject"` REQUIRES `reject_reason` non-None; conversely,
   ``approve`` with either field set is rejected as a likely typo.
"""

from __future__ import annotations

from typing import Any

_TAMPER_VERBS: frozenset[str] = frozenset({"timeout", "auto_approve"})
"""Verbs that the verdict surface MUST never accept (FR34 — operator agency)."""


def enforce_no_tamper_verbs(verb: str) -> None:
    """Raise ValueError if ``verb`` is a tamper-evidence-violating value.

    The Pydantic ``Literal`` field type rejects these at construction; this
    function is the second red-rejection layer that fires on mutation-path
    construction (e.g., `validate_assignment=True` reassignment) and on
    `model_construct(...)` raw-dict bypass. The schema-pin test is layer 3.
    """
    if verb in _TAMPER_VERBS:
        raise ValueError(
            f"OperatorVerdict.verb={verb!r} is a tamper-evidence-forbidden "
            f"value (FR34). Allowed: ['approve', 'edit', 'reject']."
        )


def enforce_verb_payload_consistency(
    *,
    verb: str,
    edit_payload: dict[str, Any] | None,
    reject_reason: str | None,
) -> None:
    """Raise ValueError if verb-payload pairing is inconsistent.

    - ``verb == "edit"`` ⇒ ``edit_payload`` MUST be non-None
    - ``verb == "reject"`` ⇒ ``reject_reason`` MUST be non-None
    - ``verb == "approve"`` ⇒ both payload fields MUST be None (typo guard)
    """
    if verb == "edit" and edit_payload is None:
        raise ValueError("OperatorVerdict.verb='edit' requires edit_payload to be set")
    if verb == "reject" and reject_reason is None:
        raise ValueError("OperatorVerdict.verb='reject' requires reject_reason to be set")
    if verb == "approve" and (edit_payload is not None or reject_reason is not None):
        raise ValueError(
            "OperatorVerdict.verb='approve' must not carry edit_payload or reject_reason; "
            "if you intended to amend or reject, set verb accordingly."
        )
