from __future__ import annotations

import pytest

from app.specialists.gary import _act as gary_act
from tests.composition._chain_test_base import ChainTestBase


@pytest.mark.timeout(120)
class TestGaryToVeraG3Chain(ChainTestBase):
    upstream_specialist = "gary"
    downstream_specialist = "vera"
    gate_id = "G3"
    cassette_path = "tests/fixtures/composition/gary-to-vera-g3"

    def test_envelope_handoff_shape(self) -> None:
        self.assert_envelope_handoff()
        self.assert_no_cross_specialist_substrate_drift()

    def test_vera_g3_receives_gamma_artifact_paths(self) -> None:
        expected = self.replay_chain_from_cassette()
        invocation = gary_act.build_vera_g3_invocation(expected["gary_slide_output"])
        assert invocation == expected["vera_g3_invocation"]
        assert all(path.endswith(".png") for path in invocation["artifact_paths"])
