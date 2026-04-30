from __future__ import annotations

import ast

import pytest

from app.specialists.compositor.graph import build_compositor_graph
from tests.integration.scaffold_conformance.scaffold_contract import validate_scaffold
from tests.parity._sanctum_parity_base import REPO_ROOT, SanctumParityTestBase


@pytest.mark.timeout(30)
class TestCompositorActivationContract(SanctumParityTestBase):
    specialist_name = "compositor"
    class_template_id = "D2"

    def _skill_md_path(self):
        return REPO_ROOT / "skills" / "compositor" / "SKILL.md"

    def cold_activation_smoke(self) -> None:
        assert build_compositor_graph().nodes

    def test_class_d2_scaffold_conformance(self) -> None:
        result = validate_scaffold("compositor", build_compositor_graph())
        assert result.is_conforming
        self.assert_class_template_conformance()

    def test_four_file_operational_sidecar_pattern(self) -> None:
        sidecar = REPO_ROOT / "_bmad" / "memory" / "bmad-agent-compositor"
        assert sorted(path.name for path in sidecar.iterdir() if path.is_file()) == [
            "access-boundaries.md",
            "chronology.md",
            "contract.md",
            "version.md",
        ]
        assert not (sidecar / "PERSONA.md").exists()

    def test_single_compositor_skill_md_pattern(self) -> None:
        assert self._skill_md_path().is_file()
        assert not (REPO_ROOT / "skills" / "bmad-agent-compositor").exists()
        self.assert_skill_md_minimal_frontmatter()

    def test_no_llm_or_third_party_api(self) -> None:
        source = (REPO_ROOT / "app/specialists/compositor/_act.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
        forbidden = {
            "make_chat_model",
            "ChatOpenAIAdapter",
            "GammaClient",
            "KlingClient",
            "ElevenLabsClient",
            "WondercraftClient",
        }
        assert forbidden.isdisjoint(names)

    def test_pipeline_determinism_harness_wired(self) -> None:
        assert (REPO_ROOT / "tests" / "parity" / "test_pipeline_determinism_harness.py").is_file()
        harness = REPO_ROOT / "tests" / "end_to_end" / (
            "test_compositor_pipeline_determinism.py"
        )
        assert harness.is_file()

    def test_field_mask_yaml_consumed(self) -> None:
        source = (REPO_ROOT / "app/specialists/compositor/_act.py").read_text(encoding="utf-8")
        assert "field-mask.yaml" in source
        assert "mask_assembly_guide" in source

    def test_four_input_chain_test_present(self) -> None:
        assert (REPO_ROOT / "tests" / "composition" / "test_compositor_4_input_chain.py").is_file()

    def test_operator_control_and_decision_log_landed(self) -> None:
        parity = (
            REPO_ROOT / "docs/operator/legacy-vs-langgraph-control-parity.md"
        ).read_text(encoding="utf-8")
        spec = (
            REPO_ROOT / "docs/dev-guide/composition-specification.md"
        ).read_text(encoding="utf-8")
        assert "Compositor" in parity
        assert "Class-D2 sidecar variant" in spec

    def test_cold_activation_smoke(self) -> None:
        self.cold_activation_smoke()
