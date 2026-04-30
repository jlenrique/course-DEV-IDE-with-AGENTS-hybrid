from __future__ import annotations

import pytest

from app.specialists.wanda import _act as wanda_act
from tests.composition._chain_test_base import ChainTestBase


@pytest.mark.timeout(120)
class TestWandaToCompositorChain(ChainTestBase):
    upstream_specialist = "wanda"
    downstream_specialist = "compositor"
    gate_id = "G3"
    cassette_path = "tests/fixtures/composition/wanda-to-compositor"

    def test_envelope_handoff_shape(self) -> None:
        self.assert_envelope_handoff()
        self.assert_no_cross_specialist_substrate_drift()

    def test_compositor_receives_audio_bed_paths(self) -> None:
        expected = self.replay_chain_from_cassette()
        invocation = wanda_act.build_compositor_invocation(expected["audio_beds"])
        assert invocation == expected["compositor_invocation"]
        assert all(path.endswith(".mp3") for path in invocation["audio_bed_paths"])
