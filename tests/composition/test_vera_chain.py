from __future__ import annotations

import pytest

from tests.composition._chain_test_base import ChainTestBase


@pytest.mark.timeout(120)
class TestVeraChain(ChainTestBase):
    upstream_specialist = "irene"
    downstream_specialist = "vera"
    gate_id = "G4"
    cassette_path = "tests/fixtures/composition/vera_chain"

    def test_texas_to_vera_g0_envelope_handoff(self) -> None:
        self.upstream_specialist = "texas"
        self.gate_id = "G0"
        self.assert_envelope_handoff()

    def test_irene_pass2_to_vera_g4_replay_is_deterministic(self) -> None:
        replay = self.replay_chain_from_cassette()
        assert replay["upstream_specialist"] == "irene"
        assert replay["downstream_consumer"] == "marcus-gate-runner"
        assert replay["gate_id"] == "G4"

    def test_vera_chain_replay_does_not_touch_dispatch_adapter(self) -> None:
        self.assert_no_cross_specialist_substrate_drift()
