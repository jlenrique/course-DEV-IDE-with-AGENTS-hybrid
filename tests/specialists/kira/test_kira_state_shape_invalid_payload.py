from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.specialists.kira.state import KiraEnvelope, KiraReturn


def test_kira_envelope_rejects_specialist_id_mismatch() -> None:
    with pytest.raises(ValidationError, match="must equal 'kira'"):
        KiraEnvelope(specialist_id="not-kira", payload_in={})


def test_kira_envelope_rejects_payload_over_50kb() -> None:
    with pytest.raises(ValidationError, match="exceeds 50KB cap"):
        KiraEnvelope(specialist_id="kira", payload_in={"big": "x" * 51_000})


def test_kira_return_rejects_specialist_id_mismatch() -> None:
    with pytest.raises(ValidationError, match="must equal 'kira'"):
        KiraReturn(specialist_id="not-kira", verb="proceed")


def test_kira_return_rejects_edit_without_edit_payload() -> None:
    with pytest.raises(ValidationError):
        KiraReturn(specialist_id="kira", verb="edit", edit_payload=None)
