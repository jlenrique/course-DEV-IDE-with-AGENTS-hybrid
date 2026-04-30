from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from tests.parity._sanctum_parity_base import REPO_ROOT, SanctumParityTestBase


def _state(payload: dict[str, object]) -> RunState:
    return RunState(
        graph_version="v0.1-stub",
        model_resolution_trail=[
            ModelResolutionEntry(
                level="per_specialist",
                requested="gpt-5",
                resolved="gpt-5",
                reason="test",
                timestamp="2026-01-01T00:00:00Z",
                cache_prefix_hash="d" * 64,
            )
        ],
        cache_state=CacheState(cache_prefix=json.dumps(payload)),
    )


@pytest.mark.timeout(30)
class TestVeraActivationContract(SanctumParityTestBase):
    specialist_name = "vera"
    class_template_id = "A"

    def _skill_md_path(self) -> Path:
        return REPO_ROOT / "skills" / "bmad-agent-fidelity-assessor" / "SKILL.md"

    def _sanctum_dir(self) -> Path:
        return REPO_ROOT / "_bmad" / "memory" / "bmad-agent-vera"

    def cold_activation_smoke(self) -> None:
        from app.specialists.vera.graph import build_vera_graph

        assert {"receive", "plan", "act", "verify", "handoff"}.issubset(
            build_vera_graph().nodes
        )

    def test_class_a_template_conformance(self) -> None:
        self.assert_class_template_conformance()

    def test_sg4_alignment_and_cold_activation(self) -> None:
        self.assert_skill_md_minimal_frontmatter()
        self.assert_sanctum_path_equality()
        self.cold_activation_smoke()

    def test_four_gate_oia_circuit_and_summary_contract(self, tmp_path: Path) -> None:
        from app.specialists.vera.graph import _act

        gates = {}
        for gate in ("G0", "G1", "G3", "G4"):
            payload: dict[str, object] = {"gate_id": gate, "runs_root": str(tmp_path)}
            if gate == "G0":
                payload["extracted_text"] = "source claim [evidence: src]"
            output = json.loads(_act(_state(payload))["cache_state"]["cache_prefix"])
            gates[gate] = output["vera_finding"]["gate_id"]
            assert Path(output["summary_path"]).parent.name == "specialist-summaries"
            assert {"O", "I", "A"} <= {
                item["category"] for item in output["vera_finding"]["findings"]
            }
        assert gates == {"G0": "G0", "G1": "G1", "G3": "G3", "G4": "G4"}

    def test_circuit_breaker_halts_on_hard_fail(self, tmp_path: Path) -> None:
        from app.specialists.vera.graph import _act

        output = json.loads(
            _act(
                _state(
                    {
                        "gate_id": "G0",
                        "runs_root": str(tmp_path),
                        "injected_findings": [
                            {
                                "category": "O",
                                "severity": "critical",
                                "evidence_anchor": "source:1",
                                "description": "required source claim missing",
                            }
                        ],
                    }
                )
            )["cache_state"]["cache_prefix"]
        )
        assert output["vera_finding"]["verdict"]["status"] == "HALT-AND-REMEDIATE"
        assert output["vera_finding"]["verdict"]["verb"] == "halt"
