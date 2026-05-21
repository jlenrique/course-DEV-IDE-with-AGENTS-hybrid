from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import validate

from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from tests.parity._sanctum_parity_base import REPO_ROOT, SanctumParityTestBase


def _state(cache_prefix: str) -> RunState:
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
        cache_state=CacheState(cache_prefix=cache_prefix),
    )


def _payload(tmp_path: Path, gate_id: str) -> str:
    return json.dumps(
        {
            "gate_id": gate_id,
            "gate_phase": "post-composition" if gate_id == "G3B" else "pre-composition",
            "runs_root": str(tmp_path),
            "slides": [{"slide_id": "s1", "title": "Intro"}],
            "narration_profile_controls": {"target_wpm": 120},
            "vtt_text": "WEBVTT\n\n00:00:00.000 --> 00:00:05.000\ncaption\n",
            "narration_segments": [
                {
                    "slide_id": "s1",
                    "text": "one two three four five six seven eight nine ten",
                    "duration_seconds": 5,
                    "motion_duration_seconds": 5,
                }
            ],
        }
    )


@pytest.mark.timeout(30)
class TestQuinnRActivationContract(SanctumParityTestBase):
    specialist_name = "quinn-r"
    class_template_id = "A"

    def _skill_md_path(self) -> Path:
        return REPO_ROOT / "skills" / "bmad-agent-quality-reviewer" / "SKILL.md"

    def _sanctum_dir(self) -> Path:
        return REPO_ROOT / "_bmad" / "memory" / "bmad-agent-quinn-r"

    def cold_activation_smoke(self) -> None:
        from app.specialists.quinn_r.graph import build_quinn_r_graph

        assert {"receive", "plan", "act", "verify", "handoff"}.issubset(
            build_quinn_r_graph().nodes
        )

    def test_class_a_template_conformance(self) -> None:
        self.assert_class_template_conformance()

    def test_sg4_alignment_and_cold_activation(self) -> None:
        self.assert_skill_md_minimal_frontmatter()
        self.assert_sanctum_path_equality()
        self.cold_activation_smoke()

    def test_two_mode_contract_and_g5_partition(self, tmp_path: Path) -> None:
        from app.specialists.quinn_r.graph import _act

        g2c = json.loads(_act(_state(_payload(tmp_path, "G2C")))["cache_state"]["cache_prefix"])
        g5 = json.loads(_act(_state(_payload(tmp_path, "G5")))["cache_state"]["cache_prefix"])
        assert g2c["quinn_r_review"]["mode"] == "pre-composition"
        assert "advisory" in g5["quinn_r_review"]
        assert "blocking" in g5["quinn_r_review"]

    def test_authorized_storyboard_schema_validity(self, tmp_path: Path) -> None:
        from app.specialists.quinn_r.graph import _act

        output = json.loads(_act(_state(_payload(tmp_path, "G2C")))["cache_state"]["cache_prefix"])
        artifact = Path(output["quinn_r_review"]["artifact_paths"][0])
        schema = json.loads(
            (REPO_ROOT / "state/config/schemas/authorized-storyboard.schema.json").read_text(
                encoding="utf-8"
            )
        )
        validate(instance=json.loads(artifact.read_text(encoding="utf-8")), schema=schema)

    def test_summary_lands_at_canonical_path(self, tmp_path: Path) -> None:
        from app.specialists.quinn_r.graph import _act

        output = json.loads(_act(_state(_payload(tmp_path, "G2C")))["cache_state"]["cache_prefix"])
        summary = Path(output["summary_path"])
        assert summary.parent.name == "specialist-summaries"
        assert "specialist_id: quinn_r" in summary.read_text(encoding="utf-8")

