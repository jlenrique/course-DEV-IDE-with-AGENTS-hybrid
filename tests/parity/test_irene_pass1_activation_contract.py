from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.models.state.cache_state import CacheState
from app.models.state.run_state import RunState
from app.specialists.irene_pass1._act import (
    ModeMismatchError,
    build_learning_events,
    read_sanctum_digest,
    write_lesson_plan,
)
from app.specialists.irene_pass1.graph import _receive, build_irene_pass1_graph
from tests.integration.scaffold_conformance.scaffold_contract import validate_scaffold
from tests.parity._sanctum_parity_base import REPO_ROOT, SanctumParityTestBase


@pytest.mark.timeout(30)
class TestIrenePass1ActivationContract(SanctumParityTestBase):
    specialist_name = "irene_pass1"
    class_template_id = "B"

    def _skill_md_path(self) -> Path:
        return REPO_ROOT / "skills" / "bmad-agent-content-creator" / "SKILL.md"

    def _sanctum_dir(self) -> Path:
        return REPO_ROOT / "_bmad" / "memory" / "bmad-agent-content-creator"

    def cold_activation_smoke(self) -> None:
        assert build_irene_pass1_graph().nodes

    def test_class_b_scaffold_conformance(self) -> None:
        result = validate_scaffold("irene_pass1", build_irene_pass1_graph())
        assert result.is_conforming
        self.assert_class_template_conformance()

    def test_lesson_plan_artifact_write_contract(self, tmp_path: Path) -> None:
        path = write_lesson_plan(
            {
                "lesson_summary": "Synthetic plan",
                "plan_units": [{"unit_id": "unit-1", "title": "Intro"}],
            },
            run_id="run-123",
            runs_root=tmp_path,
        )
        assert path == tmp_path / "run-123" / "irene-pass1.md"
        assert path.is_file()

    def test_scope_lock_learning_events(self) -> None:
        events = build_learning_events(
            run_id="run-123",
            locked_scope={"locked": True, "plan_units": [{"unit_id": "unit-1"}]},
        )
        assert {event["event_type"] for event in events} == {
            "scope_decision.set",
            "plan.locked",
        }

    def test_mode_singularity(self) -> None:
        state = RunState(
            graph_version="v0.1-stub",
            cache_state=CacheState(cache_prefix=json.dumps({"mode": "pass-2"})),
        )
        with pytest.raises(ModeMismatchError):
            _receive(state)

    def test_shared_sanctum_fingerprint(self) -> None:
        self.assert_skill_md_minimal_frontmatter()
        self.assert_sanctum_path_equality()
        assert read_sanctum_digest() == read_sanctum_digest()

    def test_cold_activation_smoke(self) -> None:
        self.cold_activation_smoke()
