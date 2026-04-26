from __future__ import annotations

import ast
from pathlib import Path


def test_cd_graph_uses_validator_single_import() -> None:
    source = Path("app/specialists/cd/graph.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        and node.module == "scripts.utilities.creative_directive_validator"
    ]
    assert len(imports) == 1
    assert any(alias.name == "validate_creative_directive" for alias in imports[0].names)


def test_cd_graph_no_schema_path_or_top_level_key_constants() -> None:
    source = Path("app/specialists/cd/graph.py").read_text(encoding="utf-8")
    assert "CREATIVE_DIRECTIVE_SCHEMA_PATH" not in source
    assert "EXPERIENCE_PROFILES_PATH" not in source
