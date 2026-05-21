from __future__ import annotations

import json

import pytest
import yaml

from app.specialists.tracy import _act as tracy_act
from app.specialists.tracy.graph import build_tracy_graph
from tests.integration.scaffold_conformance.scaffold_contract import validate_scaffold
from tests.parity._sanctum_parity_base import REPO_ROOT, SanctumParityTestBase

CLASS_C_PLUS_SIDECAR_FILES = {
    "INDEX.md",
    "PERSONA.md",
    "chronology.md",
    "access-boundaries.md",
}


@pytest.mark.timeout(30)
class TestTracyActivationContract(SanctumParityTestBase):
    specialist_name = "tracy"
    class_template_id = "C+"

    def cold_activation_smoke(self) -> None:
        assert build_tracy_graph().nodes

    def assert_sanctum_path_equality(self) -> None:
        sidecar = self._sanctum_dir()
        assert sidecar.is_dir(), f"missing sidecar dir: {sidecar}"
        present = {path.name for path in sidecar.iterdir() if path.is_file()}
        assert present == CLASS_C_PLUS_SIDECAR_FILES

    def test_class_c_plus_scaffold_conformance(self) -> None:
        result = validate_scaffold("tracy", build_tracy_graph())
        assert result.is_conforming
        self.assert_class_template_conformance()

    def test_four_file_sidecar_pattern(self) -> None:
        self.assert_sanctum_path_equality()

    def test_live_llm_only_binding(self) -> None:
        config = yaml.safe_load(
            (REPO_ROOT / "app" / "specialists" / "tracy" / "model_config.yaml").read_text(
                encoding="utf-8"
            )
        )
        assert config["default_model"] == "gpt-5.4"
        assert config["temperature_default"] == 0.3
        source = (REPO_ROOT / "app" / "specialists" / "tracy" / "_act.py").read_text(
            encoding="utf-8"
        )
        forbidden = ("gamma_client", "kling_client", "elevenlabs_client", "wondercraft_client")
        assert not any(name in source for name in forbidden)

    def test_cache_hit_rate_harness_wired(self) -> None:
        harness = REPO_ROOT / "tests" / "end_to_end" / "test_tracy_cache_hit_rate.py"
        text = harness.read_text(encoding="utf-8")
        assert harness.is_file()
        assert "@pytest.mark.llm_live" in text
        assert "median(ratios[2:]) >= 0.85" in text

    def test_retrieval_intent_shape(self) -> None:
        intents = tracy_act.parse_retrieval_intents(
            json.dumps(
                {
                    "retrieval_intents": [
                        {
                            "intent": "Find peer-reviewed evidence for spacing effects.",
                            "provider_hints": [
                                {"provider": "scite", "params": {"mode": "search"}}
                            ],
                            "acceptance_criteria": {
                                "mechanical": {"min_results": 3},
                                "provider_scored": {
                                    "authority_tier_min": "peer-reviewed"
                                },
                                "semantic_deferred": "Tracy evaluates final fit.",
                            },
                        }
                    ]
                }
            )
        )
        assert intents[0]["intent"].startswith("Find peer-reviewed")
        assert intents[0]["provider_hints"][0]["provider"] == "scite"

    def test_skill_md_activation_order(self) -> None:
        self.assert_skill_md_minimal_frontmatter()
        text = self._skill_md_path().read_text(encoding="utf-8")
        assert "_bmad/memory/bmad-agent-tracy/" in text
        for name in CLASS_C_PLUS_SIDECAR_FILES:
            assert name in text

    def test_cold_activation_smoke(self) -> None:
        self.cold_activation_smoke()
