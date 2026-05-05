from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FIRING_SPEC = REPO_ROOT / "app" / "parity" / "contracts" / "tw_7c_3_firing.py"


def test_tw_7c_3_firing_spec_exports_single_source_contract() -> None:
    tree = ast.parse(FIRING_SPEC.read_text(encoding="utf-8"))
    names = {
        node.name
        for node in tree.body
        if isinstance(node, ast.ClassDef | ast.FunctionDef)
    }
    assignments = {
        target.id
        for node in tree.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    }

    assert "LockstepResult" in names
    assert "LOCKSTEP_CHECK" in names
    assert "FOUR_FILE_GLOBS" in assignments


def test_decision_card_shape_pins_do_not_rederive_tw_7c_3_rule() -> None:
    offenders: list[str] = []
    for path in sorted((REPO_ROOT / "tests" / "parity").glob("test_decision_card_*_shape.py")):
        text = path.read_text(encoding="utf-8")
        if "FOUR_FILE_GLOBS" in text or "all_four_present" in text:
            offenders.append(path.relative_to(REPO_ROOT).as_posix())

    assert offenders == []
