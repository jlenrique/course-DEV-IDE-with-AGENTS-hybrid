from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from skills.bmad_create_specialist.scripts import generate


@pytest.fixture
def temp_repo_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir(parents=True)

    # minimal tree required by the generator
    templates_src = Path("skills") / "bmad-create-specialist" / "templates"
    templates_dst = root / "skills" / "bmad-create-specialist" / "templates"
    templates_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(templates_src, templates_dst)

    skill_src = root / "skills" / "bmad-agent-content-creator"
    skill_src.mkdir(parents=True)
    (skill_src / "SKILL.md").write_text("# skill", encoding="utf-8")

    for name in ("bmad-agent-audra", "bmad-agent-cora"):
        denied = root / "skills" / name
        denied.mkdir(parents=True)
        (denied / "SKILL.md").write_text("# denied", encoding="utf-8")

    # destination roots
    (root / "app" / "specialists").mkdir(parents=True)
    (root / "tests" / "specialists").mkdir(parents=True)
    (root / "tests" / "fixtures" / "specialists").mkdir(parents=True)
    (root / "tests" / "integration" / "scaffold_conformance").mkdir(parents=True)
    return root


@pytest.fixture
def make_request():
    def _make(
        *,
        name: str = "toytest",
        mcp_tool: str = "none",
        expertise_tier: str = "L5-toy",
        from_skill: Path | None = None,
        dry_run: bool = False,
        force: bool = False,
        repo_root: Path | None = None,
    ) -> generate.GenerationRequest:
        return generate.GenerationRequest(
            name=name,
            mcp_tool=mcp_tool,
            expertise_tier=expertise_tier,
            from_skill=from_skill,
            dry_run=dry_run,
            force=force,
            repo_root=repo_root,
        )

    return _make
