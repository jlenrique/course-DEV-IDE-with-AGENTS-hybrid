"""Validate Slab 7b per-specialist parity test class shape.

Initial Story 7b.1 scope enforces only Class-A activation contracts. Later
Class-B/C/C+/D1/D2 stories extend this scaffold in lockstep with their first
per-class parity tests.
"""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TARGET = REPO_ROOT / "tests" / "parity"


@dataclass(frozen=True)
class Violation:
    path: Path
    line: int
    message: str

    def render(self) -> str:
        rel = self.path.relative_to(REPO_ROOT).as_posix()
        return f"{rel}:{self.line}: {self.message}"


def _iter_activation_contract_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target] if target.name.endswith("_activation_contract.py") else []
    return sorted(target.rglob("test_*_activation_contract.py"))


def _name_of_expr(node: ast.expr) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Subscript):
        return _name_of_expr(node.value)
    return ""


def _literal_class_attr(class_node: ast.ClassDef, attr: str) -> object:
    for stmt in class_node.body:
        value: ast.expr | None = None
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Name) and target.id == attr:
                    value = stmt.value
                    break
        elif (
            isinstance(stmt, ast.AnnAssign)
            and isinstance(stmt.target, ast.Name)
            and stmt.target.id == attr
        ):
            value = stmt.value
        if value is not None:
            try:
                return ast.literal_eval(value)
            except ValueError:
                return None
    return None


def _method_names(class_node: ast.ClassDef) -> set[str]:
    return {
        stmt.name
        for stmt in class_node.body
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def _inherits_from_sanctum_base(
    class_node: ast.ClassDef,
    class_index: dict[str, ast.ClassDef],
    seen: set[str] | None = None,
) -> bool:
    seen = seen or set()
    for base in class_node.bases:
        base_name = _name_of_expr(base)
        if base_name == "SanctumParityTestBase":
            return True
        if base_name in seen:
            continue
        seen.add(base_name)
        parent = class_index.get(base_name)
        if parent is not None and _inherits_from_sanctum_base(
            parent, class_index, seen
        ):
            return True
    return False


def _validate_file(path: Path) -> list[Violation]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        return [Violation(path, exc.lineno or 1, f"syntax error: {exc.msg}")]
    classes = [node for node in tree.body if isinstance(node, ast.ClassDef)]
    class_index = {node.name: node for node in classes}
    test_classes = [node for node in classes if node.name.startswith("Test")]
    if not test_classes:
        return [Violation(path, 1, "no pytest test class found")]

    violations: list[Violation] = []
    for class_node in test_classes:
        if not _inherits_from_sanctum_base(class_node, class_index):
            violations.append(
                Violation(
                    path,
                    class_node.lineno,
                    f"{class_node.name} must derive from SanctumParityTestBase",
                )
            )
        specialist_name = _literal_class_attr(class_node, "specialist_name")
        class_template_id = _literal_class_attr(class_node, "class_template_id")
        if not isinstance(specialist_name, str) or not specialist_name:
            violations.append(
                Violation(
                    path,
                    class_node.lineno,
                    f"{class_node.name} must set specialist_name",
                )
            )
        if not isinstance(class_template_id, str) or not class_template_id:
            violations.append(
                Violation(
                    path,
                    class_node.lineno,
                    f"{class_node.name} must set class_template_id",
                )
            )
            continue
        if class_template_id.upper() != "A":
            violations.append(
                Violation(
                    path,
                    class_node.lineno,
                    "Story 7b.1 validator scaffold only enforces Class-A tests",
                )
            )
            continue
        if "cold_activation_smoke" not in _method_names(class_node):
            violations.append(
                Violation(
                    path,
                    class_node.lineno,
                    "Class-A parity test must override cold_activation_smoke",
                )
            )
    return violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "target",
        nargs="?",
        default=str(DEFAULT_TARGET),
        help="Parity test file or directory; defaults to tests/parity/",
    )
    args = parser.parse_args(argv)

    target = Path(args.target)
    if not target.is_absolute():
        target = REPO_ROOT / target
    files = _iter_activation_contract_files(target)
    violations: list[Violation] = []
    for path in files:
        violations.extend(_validate_file(path))

    if violations:
        for violation in violations:
            print(violation.render())
        return 1
    print(f"PASS: {len(files)} activation contract file(s) conform")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
