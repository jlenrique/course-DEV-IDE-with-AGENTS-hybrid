from __future__ import annotations

import json

import pytest

from app.specialists.dan import _act as dan_act
from app.specialists.dan.graph import build_dan_graph
from app.specialists.dan.state import DanEnvelope, DanReturn
from tests.integration.scaffold_conformance.scaffold_contract import validate_scaffold
from tests.parity._sanctum_parity_base import REPO_ROOT, SanctumParityTestBase

FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "specialists" / "dan"


@pytest.mark.timeout(30)
class TestDanActivationContract(SanctumParityTestBase):
    specialist_name = "dan"
    class_template_id = "D1"

    def cold_activation_smoke(self) -> None:
        assert build_dan_graph().nodes

    def test_class_d1_scaffold_conformance(self) -> None:
        result = validate_scaffold("dan", build_dan_graph())
        assert result.is_conforming
        self.assert_class_template_conformance()

    def test_six_file_bmb_sanctum_pattern(self) -> None:
        self.assert_skill_md_minimal_frontmatter()
        self.assert_sanctum_path_equality()

    def test_single_skill_md_pattern(self) -> None:
        assert self._skill_md_path().is_file()
        assert not (REPO_ROOT / "skills" / "bmad-agent-dan-api").exists()

    def test_llm_only_shared_facade(self) -> None:
        graph_source = (REPO_ROOT / "app" / "specialists" / "dan" / "graph.py").read_text(
            encoding="utf-8"
        )
        act_source = (REPO_ROOT / "app" / "specialists" / "dan" / "_act.py").read_text(
            encoding="utf-8"
        )
        assert "make_chat_model" in graph_source
        assert "requests" not in act_source
        assert "httpx" not in act_source
        assert "WondercraftClient" not in act_source

    def test_aux_contribution_shape(self) -> None:
        rows = dan_act.parse_aux_contributions(
            {
                "contributions": [
                    {
                        "gate_id": "G1",
                        "contribution_type": "creative_director_critique",
                        "prose": "Draft critique.",
                    },
                    {
                        "gate_id": "G1A",
                        "contribution_type": "narrative_arc_check",
                        "prose": "Boundary check.",
                    },
                    {
                        "gate_id": "G2",
                        "contribution_type": "tone_voice_consistency_review",
                        "prose": "Voice check.",
                    },
                ]
            },
            {},
        )
        assert {row["gate_id"] for row in rows} == {"G1", "G1A", "G2"}
        assert all(row["advisory"] is True for row in rows)

    def test_advisory_only_partition(self) -> None:
        fixture = json.loads((FIXTURE_ROOT / "golden_return.json").read_text(encoding="utf-8"))
        payload = fixture["payload"]
        assert fixture["verb"] == "proceed"
        assert payload["advisory_only"] is True
        assert all(not row["blocking"] for row in payload["contributions"])
        assert "halt" not in json.dumps(payload).lower()

    def test_golden_fixture_replay(self) -> None:
        envelope = json.loads(
            (FIXTURE_ROOT / "golden_envelope.json").read_text(encoding="utf-8")
        )
        returned = json.loads(
            (FIXTURE_ROOT / "golden_return.json").read_text(encoding="utf-8")
        )
        assert DanEnvelope.model_validate(envelope).specialist_id == "dan"
        model = DanReturn.model_validate(returned)
        assert model.specialist_id == "dan"
        assert model.dan_aux == returned["payload"]

    def test_cold_activation_smoke(self) -> None:
        self.cold_activation_smoke()
