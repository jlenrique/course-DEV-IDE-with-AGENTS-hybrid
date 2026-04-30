from __future__ import annotations

import ast

import pytest

from tests.parity._sanctum_parity_base import REPO_ROOT


@pytest.mark.timeout(30)
def test_compositor_act_imports_no_llm_or_third_party_clients() -> None:
    path = REPO_ROOT / "app" / "specialists" / "compositor" / "_act.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    forbidden = {
        "ChatOpenAIAdapter",
        "make_chat_model",
        "GammaClient",
        "KlingClient",
        "ElevenLabsClient",
        "WondercraftClient",
        "requests",
        "httpx",
    }
    names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    imports = {
        alias.name.split(".", 1)[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imports.update(
        str(node.module).split(".", 1)[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    )
    assert forbidden.isdisjoint(names | imports)
