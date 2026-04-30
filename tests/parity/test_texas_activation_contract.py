from __future__ import annotations

import pytest

from tests.parity._sanctum_parity_base import SanctumParityTestBase


@pytest.mark.timeout(30)
class TestTexasActivationContract(SanctumParityTestBase):
    specialist_name = "texas"
    class_template_id = "A"

    def cold_activation_smoke(self) -> None:
        from app.specialists.texas.graph import build_texas_graph

        graph = build_texas_graph()
        assert {"receive", "plan", "act", "verify", "handoff"}.issubset(graph.nodes)

    def test_class_a_template_conformance(self) -> None:
        self.assert_class_template_conformance()

    def test_sg4_alignment_and_activation_contract(self) -> None:
        self.assert_skill_md_minimal_frontmatter()
        self.assert_sanctum_path_equality()
        self.cold_activation_smoke()
