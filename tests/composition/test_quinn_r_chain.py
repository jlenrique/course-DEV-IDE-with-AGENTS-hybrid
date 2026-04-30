from __future__ import annotations

import pytest

from tests.composition._chain_test_base import ChainTestBase


@pytest.mark.timeout(120)
class TestQuinnRChain(ChainTestBase):
    upstream_specialist = "directive-composer"
    downstream_specialist = "quinn_r"
    gate_id = "G2C"
    cassette_path = "tests/fixtures/composition/quinn_r_chain"

    def test_directive_composer_to_quinn_r_envelope_handoff(self) -> None:
        self.assert_envelope_handoff()

    def test_quinn_r_to_gate_runner_replay_is_deterministic(self) -> None:
        replay = self.replay_chain_from_cassette()
        assert replay["downstream_consumer"] == "marcus-gate-runner"
        assert replay["gate_id"] == "G2C"

    def test_chain_replay_does_not_touch_dispatch_adapter(self) -> None:
        self.assert_no_cross_specialist_substrate_drift()

