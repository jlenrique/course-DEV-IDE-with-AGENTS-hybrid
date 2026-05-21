from __future__ import annotations

import ast
from pathlib import Path

from skills.bmad_create_specialist.scripts import generate
from tests.fixtures.specialists.fixture_generated_specialist_for_acceptance_test import (
    EXPECTED_TREE,
)
from tests.integration.scaffold_conformance.scaffold_contract import SCAFFOLD_NODE_IDS


def test_generate_toytest_writes_expected_files(temp_repo_root: Path, make_request) -> None:
    request = make_request(repo_root=temp_repo_root)
    result = generate.generate_specialist(request)

    assert not result.dry_run
    assert len(result.written_files) == 9
    produced = [path.relative_to(temp_repo_root).as_posix() for path in result.written_files]
    assert produced == EXPECTED_TREE
    specialist_root = temp_repo_root / "app" / "specialists" / "toytest"
    assert (specialist_root / "__init__.py").is_file()
    assert (specialist_root / "graph.py").is_file()
    assert (specialist_root / "state.py").is_file()
    assert (specialist_root / "model_config.yaml").is_file()
    assert (specialist_root / "expertise" / "README.md").is_file()


def test_generated_graph_template_contains_canonical_node_ids(
    temp_repo_root: Path, make_request
) -> None:
    generate.generate_specialist(make_request(repo_root=temp_repo_root))
    graph_path = temp_repo_root / "app" / "specialists" / "toytest" / "graph.py"
    source = graph_path.read_text(encoding="utf-8")
    ast.parse(source)

    for node_id in SCAFFOLD_NODE_IDS:
        assert f'"{node_id}"' in source
    assert "resume_from_verdict" in source


def test_generated_state_contains_classvar_specialist_pin(
    temp_repo_root: Path, make_request
) -> None:
    generate.generate_specialist(make_request(repo_root=temp_repo_root))
    state_path = temp_repo_root / "app" / "specialists" / "toytest" / "state.py"
    source = state_path.read_text(encoding="utf-8")
    assert "ClassVar" in source
    assert '_SPECIALIST_ID: ClassVar[str] = "toytest"' in source
