from __future__ import annotations

import pytest

from app.specialists.kira import _act as kira_act
from tests.composition._chain_test_base import ChainTestBase


@pytest.mark.timeout(120)
class TestKiraToCompositorChain(ChainTestBase):
    upstream_specialist = "kira"
    downstream_specialist = "compositor"
    gate_id = "G3"
    cassette_path = "tests/fixtures/composition/kira-to-compositor"

    def test_envelope_handoff_shape(self) -> None:
        self.assert_envelope_handoff()
        self.assert_no_cross_specialist_substrate_drift()

    def test_compositor_receives_motion_asset_paths(self) -> None:
        expected = self.replay_chain_from_cassette()
        invocation = kira_act.build_compositor_invocation(expected["motion_receipts"])
        assert invocation == expected["compositor_invocation"]
        assert all(path.endswith(".mp4") for path in invocation["motion_asset_paths"])
