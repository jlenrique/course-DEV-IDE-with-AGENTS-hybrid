from __future__ import annotations

import pytest

from app.specialists.dan import _act as dan_act
from tests.composition._chain_test_base import ChainTestBase


@pytest.mark.timeout(120)
class TestDanToCompositorChain(ChainTestBase):
    upstream_specialist = "dan"
    downstream_specialist = "compositor"
    gate_id = "G2"
    cassette_path = "tests/fixtures/composition/dan-to-compositor"

    def test_envelope_handoff_shape(self) -> None:
        self.assert_envelope_handoff()
        self.assert_no_cross_specialist_substrate_drift()

    def test_compositor_receives_creative_direction_context(self) -> None:
        expected = self.replay_chain_from_cassette()
        rows = dan_act.parse_aux_contributions(
            {"contributions": expected["dan_aux"]["contributions"]},
            {},
        )
        assert rows == expected["dan_aux"]["contributions"]
        assert expected["compositor_invocation"]["upstream_specialist"] == "dan"
        assert set(expected["compositor_invocation"]["aux_contributions_by_gate"]) == {
            "G1",
            "G1A",
            "G2",
        }
