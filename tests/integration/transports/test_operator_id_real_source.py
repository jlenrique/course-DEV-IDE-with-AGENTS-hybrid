from __future__ import annotations

import ast
from pathlib import Path


def test_operator_id_real_source() -> None:
    forbidden = {"scheduler", "system", "auto", "marcus", "cora", ""}
    targets = [
        Path("app/mcp_server/tools/gate_decide.py"),
        Path("app/http/gate_endpoint.py"),
        Path("app/marcus/cli/gate_cli.py"),
    ]
    for path in targets:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                assert node.value not in forbidden, (
                    f"{path} hard-codes forbidden operator_id literal"
                )
