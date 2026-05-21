from __future__ import annotations

import pytest

from app.specialists.irene.state import IreneEnvelope
from app.specialists.irene_pass1.state import IrenePass1Return
from tests.composition._chain_test_base import ChainTestBase


@pytest.mark.timeout(120)
class TestIrenePass1ToPass2Chain(ChainTestBase):
    upstream_specialist = "irene_pass1"
    downstream_specialist = "irene"
    gate_id = "G1A"
    cassette_path = "tests/fixtures/composition/irene_pass1_to_pass2"

    def test_pass1_return_locked_scope_is_pass2_envelope_compatible(self) -> None:
        returned = IrenePass1Return(
            specialist_id="irene_pass1",
            verb="proceed",
            payload={"locked_scope": {"plan_units": [{"unit_id": "unit-1"}]}},
            locked_scope={"plan_units": [{"unit_id": "unit-1"}], "locked": True},
        )
        envelope = IreneEnvelope(
            specialist_id="irene",
            payload_in={"locked_scope": returned.locked_scope},
        )
        assert envelope.payload_in["locked_scope"]["locked"] is True
        assert envelope.specialist_id == "irene"

    def test_chain_base_handoff_shape(self) -> None:
        self.assert_envelope_handoff()
