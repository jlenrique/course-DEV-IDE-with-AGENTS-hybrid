"""`app.gates.resume_api` stub tests (AC-1.4-E1).

Asserts the Slab 1 substrate stub raises `NotImplementedError` with the named
body so callers cannot silently dispatch. The signature is stable — Slab 3
Story 3.3 replaces the body only, preserving import-linter Contract C3's
symbol binding.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.gates.resume_api import resume_from_verdict
from app.models.state.operator_verdict import OperatorVerdict


def _sample_verdict(verb: str = "approve") -> OperatorVerdict:
    return OperatorVerdict(
        verb=verb,  # type: ignore[arg-type]
        gate_id="G2C",
        decision_card_id=uuid4(),
        operator_id="juanl",
        timestamp=datetime.now(UTC),
    )


def test_resume_from_verdict_raises_not_implemented_error() -> None:
    with pytest.raises(NotImplementedError, match="Slab 1 substrate stub"):
        resume_from_verdict(_sample_verdict())


def test_resume_from_verdict_error_message_echoes_verdict() -> None:
    with pytest.raises(NotImplementedError) as exc_info:
        resume_from_verdict(_sample_verdict(verb="approve"))
    message = str(exc_info.value)
    assert "verb='approve'" in message
    assert "gate_id='G2C'" in message


def test_resume_from_verdict_signature_is_stable() -> None:
    """Contract C3 binds to this exact symbol name; Slab 3 replaces body, not signature."""
    import inspect
    import typing

    sig = inspect.signature(resume_from_verdict)
    assert list(sig.parameters) == ["verdict"]
    hints = typing.get_type_hints(resume_from_verdict)
    assert hints["verdict"] is OperatorVerdict
