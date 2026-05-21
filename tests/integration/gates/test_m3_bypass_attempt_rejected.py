from __future__ import annotations

import pytest

from app.gates.errors import UnauthorizedResumeBypassError
from app.gates.guardrails import assert_no_scheduler_or_bypass_source


def test_m3_bypass_attempt_rejected() -> None:
    source = (
        "from langgraph.types import Command\n"
        "Command(resume='approve')\n"
    )
    with pytest.raises(UnauthorizedResumeBypassError):
        assert_no_scheduler_or_bypass_source(source, source_name="synthetic_bypass_attempt.py")
