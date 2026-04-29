from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "app" / "marcus" / "orchestrator" / "per_slide_subgraph.py"
MODULE_NAME = "app.marcus.orchestrator.per_slide_subgraph"


def _imports_per_slide_subgraph(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == MODULE_NAME:
            return True
        if isinstance(node, ast.Import) and any(alias.name == MODULE_NAME for alias in node.names):
            return True
    return False


def _contains_interrupt(call: ast.AST) -> bool:
    if not isinstance(call, ast.Call):
        return False
    if isinstance(call.func, ast.Name):
        return call.func.id == "interrupt"
    return isinstance(call.func, ast.Attribute) and call.func.attr == "interrupt"


def _is_per_slide_loop(node: ast.For) -> bool:
    target = ast.unparse(node.target).lower()
    iterator = ast.unparse(node.iter).lower()
    return "slide" in target or "slide" in iterator


def _fm3_offenses(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    offenses: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.For) and _is_per_slide_loop(node) and any(
            _contains_interrupt(child) for child in ast.walk(node)
        ):
            offenses.append(f"{path.as_posix()}:{node.lineno}")
    return offenses


def test_no_parent_graph_interrupt_inside_per_slide_loop() -> None:
    paths = [MODULE_PATH]
    paths.extend(
        path
        for path in (ROOT / "app").rglob("*.py")
        if path != MODULE_PATH and _imports_per_slide_subgraph(path)
    )

    offenses = [offense for path in paths for offense in _fm3_offenses(path)]

    assert offenses == []


def test_fm3_fake_parent_loop_is_detected(tmp_path: Path) -> None:
    fake = tmp_path / "fake_parent.py"
    fake.write_text(
        "from app.marcus.orchestrator.per_slide_subgraph import fan_out_per_slide\n"
        "def parent(slides):\n"
        "    for slide in slides:\n"
        "        interrupt({'slide': slide})\n",
        encoding="utf-8",
    )

    assert _fm3_offenses(fake)
