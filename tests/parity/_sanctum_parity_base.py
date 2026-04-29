"""Reusable SG-4 parity helpers for Slab 7b per-specialist tests.

Pytest classes mix this in directly and keep assertions as ordinary methods:

    class TestTexasActivationContract(SanctumParityTestBase):
        specialist_name = "texas"
        class_template_id = "A"

        def cold_activation_smoke(self):
            from app.specialists.texas.graph import build_texas_graph

            assert build_texas_graph().nodes

        def test_sanctum_alignment(self):
            self.assert_skill_md_minimal_frontmatter()
            self.assert_sanctum_path_equality()
            self.assert_class_template_conformance()
            self.cold_activation_smoke()

The base intentionally does not inherit ``unittest.TestCase``. It is a small
pytest-friendly mixin for shared filesystem and class-shape assertions.
"""

from __future__ import annotations

import inspect
import subprocess
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import ClassVar

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
REQUIRED_SANCTUM_FILES = (
    "INDEX.md",
    "PERSONA.md",
    "CREED.md",
    "BOND.md",
    "MEMORY.md",
    "CAPABILITIES.md",
)


class SanctumParityTestBase(ABC):
    """Shared assertions for SG-4 sanctum-vs-shipped-path parity tests."""

    specialist_name: ClassVar[str]
    class_template_id: ClassVar[str]

    def _skill_md_path(self) -> Path:
        return REPO_ROOT / "skills" / f"bmad-agent-{self.specialist_name}" / "SKILL.md"

    def _sanctum_dir(self) -> Path:
        return REPO_ROOT / "_bmad" / "memory" / f"bmad-agent-{self.specialist_name}"

    def assert_skill_md_minimal_frontmatter(self) -> None:
        skill_path = self._skill_md_path()
        assert skill_path.is_file(), f"missing SKILL.md: {skill_path}"
        text = skill_path.read_text(encoding="utf-8")
        assert text.startswith("---\n"), f"{skill_path} has no YAML frontmatter"
        try:
            _, frontmatter, _ = text.split("---", 2)
        except ValueError as exc:
            raise AssertionError(f"{skill_path} frontmatter is not closed") from exc
        parsed = yaml.safe_load(frontmatter) or {}
        assert isinstance(parsed, dict), f"{skill_path} frontmatter must be a mapping"
        keys = set(parsed)
        assert keys == {"name", "description"}, (
            f"{skill_path} frontmatter keys must be only name+description; got "
            f"{sorted(keys)}"
        )

    def assert_sanctum_path_equality(self) -> None:
        if str(self.class_template_id).upper() == "D2":
            return
        sanctum_dir = self._sanctum_dir()
        assert sanctum_dir.is_dir(), f"missing sanctum dir: {sanctum_dir}"
        missing = [
            name
            for name in REQUIRED_SANCTUM_FILES
            if not (sanctum_dir / name).is_file()
        ]
        assert not missing, f"{sanctum_dir} missing BMB files: {missing}"

    def assert_class_template_conformance(self) -> None:
        script = REPO_ROOT / "scripts" / "utilities" / (
            "validate_parity_test_class_conformance.py"
        )
        test_file = Path(inspect.getfile(self.__class__)).resolve()
        completed = subprocess.run(
            [sys.executable, str(script), str(test_file)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert completed.returncode == 0, (
            "parity class conformance failed:\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )

    @abstractmethod
    def cold_activation_smoke(self) -> None:
        """Import the specialist graph and assert node-list smoke succeeds."""
