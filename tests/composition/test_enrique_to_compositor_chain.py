from __future__ import annotations

import pytest

from app.specialists.enrique import _act as enrique_act
from tests.composition._chain_test_base import ChainTestBase


@pytest.mark.timeout(120)
class TestEnriqueToCompositorChain(ChainTestBase):
    upstream_specialist = "enrique"
    downstream_specialist = "compositor"
    gate_id = "G3"
    cassette_path = "tests/fixtures/composition/enrique-to-compositor"

    def test_envelope_handoff_shape(self) -> None:
        self.assert_envelope_handoff()
        self.assert_no_cross_specialist_substrate_drift()

    def test_compositor_receives_audio_and_caption_paths(self) -> None:
        expected = self.replay_chain_from_cassette()
        invocation = enrique_act.build_compositor_invocation(expected["narration_outputs"])
        assert invocation == expected["compositor_invocation"]
        assert all(path.endswith(".mp3") for path in invocation["audio_paths"])
        assert all(path.endswith(".vtt") for path in invocation["caption_paths"])
