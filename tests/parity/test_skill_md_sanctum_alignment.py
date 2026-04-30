from __future__ import annotations

from pathlib import Path

from tests.parity._sanctum_parity_base import REPO_ROOT, SanctumParityTestBase


class TestTexasSkillMdSanctumAlignment(SanctumParityTestBase):
    specialist_name = "texas"
    class_template_id = "A"

    def cold_activation_smoke(self) -> None:
        from app.specialists.texas.graph import build_texas_graph

        assert build_texas_graph().nodes

    def test_texas_skill_md_has_minimal_frontmatter(self) -> None:
        self.assert_skill_md_minimal_frontmatter()

    def test_texas_sanctum_has_six_file_bmb_pattern(self) -> None:
        self.assert_sanctum_path_equality()

    def test_texas_cold_activation_smoke(self) -> None:
        self.cold_activation_smoke()


class TestQuinnRSkillMdSanctumAlignment(SanctumParityTestBase):
    specialist_name = "quinn-r"
    class_template_id = "A"

    def _skill_md_path(self) -> Path:
        return REPO_ROOT / "skills" / "bmad-agent-quality-reviewer" / "SKILL.md"

    def _sanctum_dir(self) -> Path:
        return REPO_ROOT / "_bmad" / "memory" / "bmad-agent-quinn-r"

    def cold_activation_smoke(self) -> None:
        from app.specialists.quinn_r.graph import build_quinn_r_graph

        assert build_quinn_r_graph().nodes

    def test_quinn_r_skill_md_has_minimal_frontmatter(self) -> None:
        self.assert_skill_md_minimal_frontmatter()

    def test_quinn_r_sanctum_has_six_file_bmb_pattern(self) -> None:
        self.assert_sanctum_path_equality()

    def test_quinn_r_cold_activation_smoke(self) -> None:
        self.cold_activation_smoke()


class TestVeraSkillMdSanctumAlignment(SanctumParityTestBase):
    specialist_name = "vera"
    class_template_id = "A"

    def _skill_md_path(self) -> Path:
        return REPO_ROOT / "skills" / "bmad-agent-fidelity-assessor" / "SKILL.md"

    def _sanctum_dir(self) -> Path:
        return REPO_ROOT / "_bmad" / "memory" / "bmad-agent-vera"

    def cold_activation_smoke(self) -> None:
        from app.specialists.vera.graph import build_vera_graph

        assert build_vera_graph().nodes

    def test_vera_skill_md_has_minimal_frontmatter(self) -> None:
        self.assert_skill_md_minimal_frontmatter()

    def test_vera_sanctum_has_six_file_bmb_pattern(self) -> None:
        self.assert_sanctum_path_equality()

    def test_vera_cold_activation_smoke(self) -> None:
        self.cold_activation_smoke()


class TestIrenePass1SkillMdSanctumAlignment(SanctumParityTestBase):
    specialist_name = "irene_pass1"
    class_template_id = "B"

    def _skill_md_path(self) -> Path:
        return REPO_ROOT / "skills" / "bmad-agent-content-creator" / "SKILL.md"

    def _sanctum_dir(self) -> Path:
        return REPO_ROOT / "_bmad" / "memory" / "bmad-agent-content-creator"

    def cold_activation_smoke(self) -> None:
        from app.specialists.irene_pass1.graph import build_irene_pass1_graph

        assert build_irene_pass1_graph().nodes

    def test_irene_pass1_skill_md_has_minimal_frontmatter(self) -> None:
        self.assert_skill_md_minimal_frontmatter()

    def test_irene_pass1_sanctum_has_six_file_bmb_pattern(self) -> None:
        self.assert_sanctum_path_equality()

    def test_irene_pass1_cold_activation_smoke(self) -> None:
        self.cold_activation_smoke()


class TestTracySkillMdSanctumAlignment(SanctumParityTestBase):
    specialist_name = "tracy"
    class_template_id = "C+"

    def assert_sanctum_path_equality(self) -> None:
        sidecar = self._sanctum_dir()
        assert sidecar.is_dir(), f"missing sidecar dir: {sidecar}"
        present = {path.name for path in sidecar.iterdir() if path.is_file()}
        assert present == {
            "INDEX.md",
            "PERSONA.md",
            "chronology.md",
            "access-boundaries.md",
        }

    def cold_activation_smoke(self) -> None:
        from app.specialists.tracy.graph import build_tracy_graph

        assert build_tracy_graph().nodes

    def test_tracy_skill_md_has_minimal_frontmatter(self) -> None:
        self.assert_skill_md_minimal_frontmatter()

    def test_tracy_sanctum_has_four_file_class_c_plus_pattern(self) -> None:
        self.assert_sanctum_path_equality()

    def test_tracy_cold_activation_smoke(self) -> None:
        self.cold_activation_smoke()


class TestGarySkillMdSanctumAlignment(SanctumParityTestBase):
    specialist_name = "gary"
    class_template_id = "C"

    def cold_activation_smoke(self) -> None:
        from app.specialists.gary.graph import build_gary_graph

        assert build_gary_graph().nodes

    def test_gary_skill_md_has_minimal_frontmatter(self) -> None:
        self.assert_skill_md_minimal_frontmatter()

    def test_gary_sanctum_has_six_file_bmb_pattern(self) -> None:
        self.assert_sanctum_path_equality()

    def test_gary_cold_activation_smoke(self) -> None:
        self.cold_activation_smoke()


class TestKiraSkillMdSanctumAlignment(SanctumParityTestBase):
    specialist_name = "kira"
    class_template_id = "C"

    def cold_activation_smoke(self) -> None:
        from app.specialists.kira.graph import build_kira_graph

        assert build_kira_graph().nodes

    def test_kira_skill_md_has_minimal_frontmatter(self) -> None:
        self.assert_skill_md_minimal_frontmatter()

    def test_kira_sanctum_has_six_file_bmb_pattern(self) -> None:
        self.assert_sanctum_path_equality()

    def test_kira_cold_activation_smoke(self) -> None:
        self.cold_activation_smoke()


class TestTracySkillMdSanctumAlignment(SanctumParityTestBase):
    specialist_name = "tracy"
    class_template_id = "C+"

    def cold_activation_smoke(self) -> None:
        from app.specialists.tracy.graph import build_tracy_graph

        assert build_tracy_graph().nodes

    def test_tracy_skill_md_has_minimal_frontmatter(self) -> None:
        self.assert_skill_md_minimal_frontmatter()

    def test_tracy_sanctum_has_four_file_bmb_pattern(self) -> None:
        names = sorted(path.name for path in self._sanctum_dir().iterdir())
        assert names == [
            "INDEX.md",
            "PERSONA.md",
            "access-boundaries.md",
            "chronology.md",
        ]

    def test_tracy_cold_activation_smoke(self) -> None:
        self.cold_activation_smoke()
