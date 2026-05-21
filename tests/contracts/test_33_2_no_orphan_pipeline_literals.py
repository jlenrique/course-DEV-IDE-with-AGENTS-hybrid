"""Contract checks for 33-2 pipeline literal hygiene."""

from __future__ import annotations

import ast
from pathlib import Path

from scripts.utilities.pipeline_manifest import load_manifest


def test_no_hardcoded_pipeline_step_lists() -> None:
    root = Path(__file__).resolve().parents[2]
    manifest_ids = {step.id for step in load_manifest().steps}
    violations: list[str] = []

    for path in (root / "scripts").rglob("*.py"):
        if path.name in {"pipeline_manifest.py"}:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.List, ast.Tuple)) and len(node.elts) >= 5:
                literals = []
                for elt in node.elts:
                    if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                        literals.append(elt.value)
                if literals and all(item in manifest_ids for item in literals):
                    violations.append(str(path))
                    break

    assert not violations, f"hardcoded pipeline literal lists found: {violations}"


def test_insert_between_arguments_resolve_to_manifest_ids() -> None:
    root = Path(__file__).resolve().parents[2]
    manifest_ids = {step.id for step in load_manifest().steps}
    workflow_runner = root / "app" / "marcus" / "orchestrator" / "workflow_runner.py"
    tree = ast.parse(workflow_runner.read_text(encoding="utf-8"))
    invalid: list[str] = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)):
            continue
        if node.func.id != "insert_between" or len(node.args) < 2:
            continue
        before = node.args[0].value if isinstance(node.args[0], ast.Constant) else None
        after = node.args[1].value if isinstance(node.args[1], ast.Constant) else None
        if isinstance(before, str) and before not in manifest_ids:
            invalid.append(before)
        if isinstance(after, str) and after not in manifest_ids:
            invalid.append(after)

    assert not invalid, f"insert_between references unknown IDs: {invalid}"

