from __future__ import annotations

import ast
from pathlib import Path

SCAN_ROOTS = (
    Path("app/marcus/orchestrator"),
    Path("app/marcus/cli"),
)
SPECIALIST_GRAPHS = tuple(Path("app/specialists").glob("*/graph.py"))
ALLOWED_CALL_SITE = Path("app/marcus/orchestrator/pre_gate_marcus.py")


def _make_chat_model_call_lines(path: Path) -> list[tuple[str, int]]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    parents: dict[ast.AST, ast.AST] = {}
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parents[child] = parent

    calls: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Name) or node.func.id != "make_chat_model":
            continue
        function = "<module>"
        parent = parents.get(node)
        while parent is not None:
            if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef)):
                function = parent.name
                break
            parent = parents.get(parent)
        calls.append((function, node.lineno))
    return calls


def test_pre_gate_marcus_is_only_orchestrator_cli_make_chat_model_call_site() -> None:
    violations: list[str] = []
    for root in SCAN_ROOTS:
        for path in root.rglob("*.py"):
            if path == ALLOWED_CALL_SITE:
                continue
            for function, line in _make_chat_model_call_lines(path):
                violations.append(f"{path}:{line} in {function}")

    assert violations == []


def test_specialist_gate_decision_functions_do_not_invoke_make_chat_model() -> None:
    violations: list[str] = []
    for path in SPECIALIST_GRAPHS:
        for function, line in _make_chat_model_call_lines(path):
            if "gate" in function:
                violations.append(f"{path}:{line} in {function}")

    assert violations == []
