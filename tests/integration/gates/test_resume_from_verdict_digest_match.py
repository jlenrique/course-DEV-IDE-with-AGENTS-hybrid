from __future__ import annotations

from uuid import UUID

import pytest
from langgraph.types import Command

from app.gates import GateError, clear_resume_registry, resume_from_verdict
from tests.unit.gates._helpers import sample_verdict


def test_digest_match_resumes() -> None:
    clear_resume_registry()
    verdict = sample_verdict(trial_id=UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"))
    command = resume_from_verdict(verdict)
    assert isinstance(command, Command)
    assert command.resume["verb"] == "approve"
    assert command.resume["gate_id"] == "G1"


def test_digest_mismatch_raises_gate_error() -> None:
    clear_resume_registry()
    verdict = sample_verdict(
        trial_id=UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"),
        digest="0" * 64,
    )
    with pytest.raises(GateError, match="digest_mismatch"):
        resume_from_verdict(verdict)
