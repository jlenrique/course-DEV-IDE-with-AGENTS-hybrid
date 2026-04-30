"""SG-1 aggregator — assert all 11 Slab 7b body specialists are addressable.

Story 7b.12 T3 / AC-B / FR105 / NFR-I10. Bound to
`.github/workflows/activation-contract.yml` as required CI check.

Asserts:
- name-set equality with the canonical FR88 11-specialist roster
- each specialist has a corresponding `tests/parity/test_<name>_activation_contract.py`
  authored by its body story (Texas/Quinn-R/Vera/Irene/Tracy/Gary/Kira/Enrique/
  Wanda/Dan/Compositor)
- each parity test inherits `SanctumParityTestBase` and declares a non-empty
  `class_template_id` ∈ {A, B, C+, C, D1, D2} per NFR-I12
"""
from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PARITY_DIR = REPO_ROOT / "tests" / "parity"

CANONICAL_ROSTER: frozenset[str] = frozenset(
    {
        "texas",
        "quinn_r",
        "vera",
        "irene_pass1",
        "tracy",
        "gary",
        "kira",
        "enrique",
        "wanda",
        "dan",
        "compositor",
    }
)

CANONICAL_CLASS_IDS: frozenset[str] = frozenset(
    {"A", "B", "C+", "C", "D1", "D2", "CPLUS"}
)


def _activation_contract_files() -> dict[str, Path]:
    return {
        path.stem.removeprefix("test_").removesuffix("_activation_contract"): path
        for path in sorted(PARITY_DIR.glob("test_*_activation_contract.py"))
    }


def _literal_class_attr(class_node: ast.ClassDef, attr_name: str) -> str | None:
    for stmt in class_node.body:
        if not isinstance(stmt, ast.Assign):
            continue
        for target in stmt.targets:
            if isinstance(target, ast.Name) and target.id == attr_name:
                if isinstance(stmt.value, ast.Constant) and isinstance(
                    stmt.value.value, str
                ):
                    return stmt.value.value
    return None


def test_eleven_specialists_addressable_roster_floor() -> None:
    files = _activation_contract_files()
    found = set(files.keys())
    missing = CANONICAL_ROSTER - found
    extras = found - CANONICAL_ROSTER
    assert not missing, f"Missing activation-contract files for: {sorted(missing)}"
    assert not extras, f"Unexpected activation-contract files: {sorted(extras)}"


def test_eleven_specialists_addressable_count() -> None:
    files = _activation_contract_files()
    assert len(files) == 11, f"Expected 11 activation-contract files, found {len(files)}"


def test_each_specialist_declares_class_template_id() -> None:
    files = _activation_contract_files()
    for specialist, path in files.items():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        class_nodes = [
            node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
        ]
        assert class_nodes, f"{specialist}: no test class found in {path.name}"
        contract_classes = [
            cls
            for cls in class_nodes
            if any(
                isinstance(base, ast.Name) and base.id == "SanctumParityTestBase"
                for base in cls.bases
            )
        ]
        assert contract_classes, (
            f"{specialist}: no class inherits SanctumParityTestBase"
        )
        for cls in contract_classes:
            template_id = _literal_class_attr(cls, "class_template_id")
            assert template_id is not None, (
                f"{specialist}: class {cls.name} missing class_template_id"
            )
            assert template_id.upper() in CANONICAL_CLASS_IDS, (
                f"{specialist}: class {cls.name} has invalid "
                f"class_template_id={template_id!r}; "
                f"expected one of {sorted(CANONICAL_CLASS_IDS)}"
            )
