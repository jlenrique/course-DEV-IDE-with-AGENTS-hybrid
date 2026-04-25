"""AC-H invalid-payload red-rejection (Story 2a.2 four-file-lockstep TESTS).

IreneEnvelope rejects payload_in beyond 50KB cap + specialist_id mismatch.
IreneReturn rejects specialist_id mismatch + cross-field invariants from parent.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.specialists.irene.state import IreneEnvelope, IreneReturn


def test_envelope_rejects_specialist_id_mismatch() -> None:
    with pytest.raises(ValidationError, match="must equal 'irene'"):
        IreneEnvelope(specialist_id="not-irene", payload_in={})


def test_envelope_rejects_payload_over_50kb() -> None:
    payload = {"big": "x" * 51_000}
    with pytest.raises(ValidationError, match="exceeds 50KB cap"):
        IreneEnvelope(specialist_id="irene", payload_in=payload)


def test_return_rejects_specialist_id_mismatch() -> None:
    with pytest.raises(ValidationError, match="must equal 'irene'"):
        IreneReturn(specialist_id="not-irene", verb="proceed")


def test_return_rejects_edit_verb_without_payload() -> None:
    """Cross-field invariant inherited from SpecialistReturn: edit verb requires edit_payload."""
    with pytest.raises(ValidationError):
        IreneReturn(specialist_id="irene", verb="edit", edit_payload=None)
