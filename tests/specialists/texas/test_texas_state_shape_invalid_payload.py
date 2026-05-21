from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.specialists.texas.state import TexasEnvelope, TexasReturn


def test_texas_envelope_rejects_specialist_id_mismatch() -> None:
    with pytest.raises(ValidationError, match="must equal 'texas'"):
        TexasEnvelope(specialist_id="not-texas", payload_in={})


def test_texas_envelope_rejects_payload_over_50kb() -> None:
    with pytest.raises(ValidationError, match="exceeds 50KB cap"):
        TexasEnvelope(specialist_id="texas", payload_in={"big": "x" * 51_000})


def test_texas_return_rejects_specialist_id_mismatch() -> None:
    with pytest.raises(ValidationError, match="must equal 'texas'"):
        TexasReturn(specialist_id="not-texas", verb="proceed")


def test_texas_return_rejects_edit_without_payload() -> None:
    with pytest.raises(ValidationError):
        TexasReturn(specialist_id="texas", verb="edit", edit_payload=None)
