"""Winston W2 / AC-E negative-path — `gate_decision` raises NotImplementedError when traversed.

This pins the Slab-1 stub semantics of `app.gates.resume_api.resume_from_verdict`.
At Slab 3.3 the body is replaced; this test will then need to update to assert
the new behavior. The failure mode caught: silent fallthrough through
`gate_decision` without exercising the resume binding.
"""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.gates.resume_api import resume_from_verdict
from app.models.state.operator_verdict import OperatorVerdict


def test_resume_from_verdict_raises_not_implemented_at_slab_1() -> None:
    """Confirm the Slab-1 substrate stub raises NotImplementedError when invoked.

    Synthetic verify-fail edge that traverses gate_decision → resume_from_verdict
    will hit this raise at runtime per Winston W2 binding.
    """
    verdict = OperatorVerdict(
        verb="approve",
        gate_id="irene-gate-decision-test",
        decision_card_id=uuid4(),
        operator_id="test-operator",
    )
    with pytest.raises(NotImplementedError, match="Slab 1 substrate stub"):
        resume_from_verdict(verdict)
