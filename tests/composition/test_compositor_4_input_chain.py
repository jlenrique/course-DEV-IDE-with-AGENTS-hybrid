from __future__ import annotations

import pytest

from app.specialists.compositor import _act as compositor_act
from tests.composition._chain_test_base import ChainTestBase
from tests.specialists.compositor._fixtures import compositor_payload


@pytest.mark.timeout(120)
class TestCompositorFourInputChain(ChainTestBase):
    upstream_specialist = "gary"
    downstream_specialist = "compositor"
    gate_id = "G3"
    cassette_path = "tests/fixtures/composition/kira-to-compositor"

    def test_envelope_handoff_shape(self) -> None:
        self.assert_envelope_handoff()
        self.assert_no_cross_specialist_substrate_drift()

    def test_four_input_payload_consumes_into_pipeline(self, tmp_path) -> None:
        payload = compositor_payload(tmp_path)
        verdict = compositor_act.run_compositor_pipeline(payload)
        assert len(verdict["synced_assets"]["visuals"]) == 2
        assert len(verdict["synced_assets"]["motion"]) == 1
        assert payload["audio_paths"]
        assert payload["audio_bed_paths"]
        assert compositor_act.Path(verdict["assembly_guide_path"]).is_file()
