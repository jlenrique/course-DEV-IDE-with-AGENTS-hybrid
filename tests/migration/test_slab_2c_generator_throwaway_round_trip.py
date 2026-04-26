from __future__ import annotations

import re
import shutil
import uuid
from pathlib import Path

import pytest

from skills.bmad_create_specialist.scripts import generate
from tests.integration.scaffold_conformance.scaffold_contract import SCAFFOLD_NODE_IDS
from tests.specialists.generator.conftest import TEMP_PYPROJECT


@pytest.fixture
def isolated_repo_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir(parents=True)
    shutil.copytree(
        Path("skills") / "bmad-create-specialist" / "templates",
        root / "skills" / "bmad-create-specialist" / "templates",
    )
    (root / "app" / "specialists").mkdir(parents=True)
    (root / "tests" / "specialists").mkdir(parents=True)
    (root / "tests" / "fixtures" / "specialists").mkdir(parents=True)
    (root / "tests" / "integration" / "scaffold_conformance").mkdir(parents=True)
    (root / "pyproject.toml").write_text(TEMP_PYPROJECT, encoding="utf-8")
    return root


@pytest.fixture
def throwaway_generation(isolated_repo_root: Path, request: pytest.FixtureRequest):
    name = f"tmp_validate_{uuid.uuid4().hex[:8]}"
    specialist_root = isolated_repo_root / "app" / "specialists" / name
    test_root = isolated_repo_root / "tests" / "specialists" / name
    fixture_root = isolated_repo_root / "tests" / "fixtures" / "specialists" / name
    scaffold_test = (
        isolated_repo_root
        / "tests"
        / "integration"
        / "scaffold_conformance"
        / f"test_scaffold_{name}.py"
    )

    assert not specialist_root.exists()

    def cleanup() -> None:
        for path in (specialist_root, test_root, fixture_root):
            if path.exists():
                shutil.rmtree(path)
        if scaffold_test.exists():
            scaffold_test.unlink()
        generate.retire_specialist(name, repo_root=isolated_repo_root)

    request.addfinalizer(cleanup)
    yield isolated_repo_root, name
    cleanup()


def _request(name: str, repo_root: Path) -> generate.GenerationRequest:
    return generate.GenerationRequest(
        name=name,
        mcp_tool="none",
        expertise_tier="L5-podcast-production",
        repo_root=repo_root,
    )


def _read_pyproject(repo_root: Path) -> str:
    return (repo_root / "pyproject.toml").read_text(encoding="utf-8")


def test_throwaway_second_specialist_round_trip(throwaway_generation) -> None:
    repo_root, name = throwaway_generation

    result = generate.generate_specialist(_request(name, repo_root))

    assert re.fullmatch(r"tmp_validate_[0-9a-f]{8}", name)
    assert len(result.written_files) == 9
    assert all(path.is_file() for path in result.written_files)
    graph_source = (repo_root / "app" / "specialists" / name / "graph.py").read_text(
        encoding="utf-8"
    )
    for node_id in SCAFFOLD_NODE_IDS:
        assert f'"{node_id}"' in graph_source
    assert f"app.specialists.{name}.graph -> app.gates.resume_api" in _read_pyproject(
        repo_root
    )


def test_throwaway_round_trip_is_idempotent_under_force(throwaway_generation) -> None:
    repo_root, name = throwaway_generation

    generate.generate_specialist(_request(name, repo_root))
    first_pyproject = _read_pyproject(repo_root)
    generate.generate_specialist(
        generate.GenerationRequest(
            name=name,
            mcp_tool="none",
            expertise_tier="L5-podcast-production",
            repo_root=repo_root,
            force=True,
        )
    )
    second_pyproject = _read_pyproject(repo_root)

    target = f"app.specialists.{name}.graph -> app.gates.resume_api"
    assert first_pyproject == second_pyproject
    assert second_pyproject.count(target) == 1
