from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from skills.bmad_create_specialist.scripts import generate

TEMP_PYPROJECT = """[project]
name = "temp-generator-tests"
version = "0.0.0"
requires-python = ">=3.11"

[tool.importlinter]
root_packages = ["app"]
include_external_packages = true

[[tool.importlinter.contracts]]
name = "app.marcus and app.cora are lane-isolated siblings (D3 + D4 lane separation)"
type = "independence"
modules = ["app.marcus", "app.cora"]

[[tool.importlinter.contracts]]
name = "app.gates.** may not import schedulers (D3 HIL tamper-evidence)"
type = "forbidden"
source_modules = ["app.gates"]
forbidden_modules = ["threading", "apscheduler", "schedule"]

[[tool.importlinter.contracts]]
name = "Contract C3 — only the three authorized bridge modules may import app.gates.resume_api (D3)"
type = "forbidden"
source_modules = [
    "app.runtime",
    "app.specialists",
    "app.cora",
    "app.models",
    "app.manifest",
    "app.mcp_server",
]
forbidden_modules = ["app.gates.resume_api"]
ignore_imports = [
    "app.mcp_server.tools.gate_decide -> app.gates.resume_api",
    "app.specialists._scaffold.graph -> app.gates.resume_api",
    "app.specialists.irene.graph -> app.gates.resume_api",
    "app.specialists.kira.graph -> app.gates.resume_api",
    "app.specialists.texas.graph -> app.gates.resume_api",
]
"""


def _write_module(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


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
    (root / "pyproject.toml").write_text(TEMP_PYPROJECT, encoding="utf-8")

    # import-linter contract placeholders for parser-level checks.
    _write_module(root / "app" / "runtime" / "__init__.py")
    _write_module(root / "app" / "cora" / "__init__.py")
    _write_module(root / "app" / "marcus" / "__init__.py")
    _write_module(root / "app" / "models" / "__init__.py")
    _write_module(root / "app" / "manifest" / "__init__.py")
    _write_module(root / "app" / "gates" / "__init__.py")
    _write_module(
        root / "app" / "gates" / "resume_api.py",
        "def resume_from_verdict():\n    return None\n",
    )
    _write_module(root / "app" / "mcp_server" / "__init__.py")
    _write_module(root / "app" / "mcp_server" / "tools" / "__init__.py")
    _write_module(
        root / "app" / "mcp_server" / "tools" / "gate_decide.py",
        "from app.gates.resume_api import resume_from_verdict\n",
    )
    _write_module(root / "app" / "specialists" / "_scaffold" / "__init__.py")
    _write_module(
        root / "app" / "specialists" / "_scaffold" / "graph.py",
        "from app.gates.resume_api import resume_from_verdict\n",
    )
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
