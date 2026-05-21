"""Cross-field validators for `SpecialistReturn` (NFR-M5 four-file-lockstep).

Mirrors the verb/payload-consistency invariant from `OperatorVerdict` for
the specialist-side return surface. Lifted as a standalone function so
the test layer can exercise it without constructing the full Pydantic
model (matches the 31-1 G6 test-discoverability pattern).
"""

from __future__ import annotations

from typing import Any


def enforce_specialist_verb_payload_consistency(
    *,
    verb: str,
    edit_payload: dict[str, Any] | None,
    reject_reason: str | None,
) -> None:
    """Raise ValueError if specialist verb-payload pairing is inconsistent.

    - ``verb == "edit"`` ⇒ ``edit_payload`` MUST be non-None
    - ``verb == "reject"`` ⇒ ``reject_reason`` MUST be non-None
    - ``verb == "proceed"`` ⇒ both payload fields MUST be None (typo guard)
    """
    if verb == "edit" and edit_payload is None:
        raise ValueError("SpecialistReturn.verb='edit' requires edit_payload to be set")
    if verb == "reject" and reject_reason is None:
        raise ValueError("SpecialistReturn.verb='reject' requires reject_reason to be set")
    if verb == "proceed" and (edit_payload is not None or reject_reason is not None):
        raise ValueError(
            "SpecialistReturn.verb='proceed' must not carry edit_payload or reject_reason; "
            "if you intended to amend or reject, set verb accordingly."
        )
