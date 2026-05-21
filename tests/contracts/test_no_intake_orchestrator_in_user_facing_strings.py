"""AC-T.14 — no user-facing `intake` / `orchestrator` leak (R2 rider S-3 / R1 amendment 17).

Scans user-facing surfaces across the ``marcus/lesson_plan/`` package for
the tokens ``intake`` / ``orchestrator``. User-facing surfaces are:

    (1) Pydantic ``Field(description=...)`` string values (AST-scanned).
    (2) Pydantic validator error messages: ``raise ValueError(...)`` /
        ``ValidationError(...)`` string arguments (AST-scanned).
    (3) Literal enum values that appear in public (non-``SkipJsonSchema``)
        fields — scanned via the emitted JSON Schema, so SkipJsonSchema'd
        audit-only Literals are automatically exempt.
    (4) JSON Schema ``description`` / ``title`` / ``errorMessage`` entries
        in both committed schema files.
    (5) ``dials-spec.md`` body prose.

Internal module/class/import-path names + internal-only Literal values
(wrapped in ``SkipJsonSchema``) are exempt because they cannot reach a
serialized payload, error message, or rendered UI.

Failure message names the file + line + offending string so maintainers can
remediate immediately.
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path

PACKAGE_ROOT = Path(__file__).parents[2] / "app" / "marcus" / "lesson_plan"
SCHEMA_FILES = list((PACKAGE_ROOT / "schema").glob("*.schema.json"))
DIALS_SPEC = PACKAGE_ROOT / "dials-spec.md"
PYTHON_FILES = [
    p for p in PACKAGE_ROOT.rglob("*.py") if "__pycache__" not in p.parts
]

FORBIDDEN_RX = re.compile(r"(?i)\b(intake|orchestrator)\b")


# ---------------------------------------------------------------------------
# JSON Schema + dials-spec.md surface (text scan)
# ---------------------------------------------------------------------------


def test_json_schema_files_have_no_leak() -> None:
    violations: list[str] = []
    for schema_path in SCHEMA_FILES:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        _walk_json_schema_strings(schema, schema_path, violations, path="$")
    assert not violations, (
        "User-facing JSON Schema string values leak `intake` / `orchestrator`:\n  - "
        + "\n  - ".join(violations)
    )


def _walk_json_schema_strings(
    node: object, schema_path: Path, violations: list[str], path: str
) -> None:
    """Walk a JSON-Schema tree and check `description` / `title` / `errorMessage` values."""
    if isinstance(node, dict):
        for key, value in node.items():
            sub_path = f"{path}.{key}"
            if (
                key in {"description", "title", "errorMessage"}
                and isinstance(value, str)
                and FORBIDDEN_RX.search(value)
            ):
                violations.append(f"{schema_path.name} @ {sub_path}: {value!r}")
            _walk_json_schema_strings(value, schema_path, violations, sub_path)
            # Also scan enum values (they are user-facing through serialization).
            if key == "enum" and isinstance(value, list):
                for i, v in enumerate(value):
                    if isinstance(v, str) and FORBIDDEN_RX.search(v):
                        violations.append(
                            f"{schema_path.name} @ {sub_path}[{i}]: {v!r}"
                        )
    elif isinstance(node, list):
        for i, item in enumerate(node):
            _walk_json_schema_strings(item, schema_path, violations, f"{path}[{i}]")


def test_dials_spec_prose_has_no_leak() -> None:
    assert DIALS_SPEC.exists()
    text = DIALS_SPEC.read_text(encoding="utf-8")
    violations: list[str] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if FORBIDDEN_RX.search(line):
            violations.append(f"dials-spec.md:{line_no}: {line!r}")
    assert not violations, (
        "dials-spec.md prose leaks `intake` / `orchestrator`:\n  - "
        + "\n  - ".join(violations)
    )


# ---------------------------------------------------------------------------
# Python source surfaces — AST scan of Field(description=...) + error messages
# ---------------------------------------------------------------------------


def _is_field_call(node: ast.Call) -> bool:
    """Return True if this Call is a Pydantic ``Field(...)`` or ``pydantic.Field(...)``."""
    if isinstance(node.func, ast.Name) and node.func.id == "Field":
        return True
    return isinstance(node.func, ast.Attribute) and node.func.attr == "Field"


def _is_raise_error(node: ast.Raise) -> bool:
    """Return True if this Raise emits a user-facing error class."""
    if node.exc is None:
        return False
    exc = node.exc
    if isinstance(exc, ast.Call):
        if isinstance(exc.func, ast.Name) and exc.func.id in {
            "ValueError",
            "ValidationError",
            "TypeError",
            "StaleRevisionError",
        }:
            return True
        if isinstance(exc.func, ast.Attribute) and exc.func.attr in {
            "ValueError",
            "ValidationError",
            "TypeError",
        }:
            return True
    return False


def _concat_str_constants(node: ast.AST) -> str | None:
    """Recover the literal-string value of a static concatenation chain."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        # f-string; recover literal parts only (conservative).
        parts: list[str] = []
        for v in node.values:
            if isinstance(v, ast.Constant) and isinstance(v.value, str):
                parts.append(v.value)
            else:
                return None
        return "".join(parts)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = _concat_str_constants(node.left)
        right = _concat_str_constants(node.right)
        if left is not None and right is not None:
            return left + right
    return None


def test_python_source_field_descriptions_have_no_leak() -> None:
    violations: list[str] = []
    for py_path in PYTHON_FILES:
        tree = ast.parse(py_path.read_text(encoding="utf-8"), filename=str(py_path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and _is_field_call(node):
                # Inspect keyword description= argument.
                for kw in node.keywords:
                    if kw.arg == "description":
                        text = _concat_str_constants(kw.value)
                        if text and FORBIDDEN_RX.search(text):
                            violations.append(
                                f"{py_path.name}:{kw.value.lineno}: "
                                f"Field(description=...) leak: {text!r}"
                            )
    assert not violations, (
        "Pydantic Field(description=...) values leak `intake` / `orchestrator`:\n  - "
        + "\n  - ".join(violations)
    )


def test_python_source_error_messages_have_no_leak() -> None:
    violations: list[str] = []
    for py_path in PYTHON_FILES:
        tree = ast.parse(py_path.read_text(encoding="utf-8"), filename=str(py_path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Raise) and _is_raise_error(node):
                assert isinstance(node.exc, ast.Call)
                for arg in node.exc.args:
                    text = _concat_str_constants(arg)
                    if text and FORBIDDEN_RX.search(text):
                        violations.append(
                            f"{py_path.name}:{node.lineno}: "
                            f"error message leak: {text!r}"
                        )
    assert not violations, (
        "Validator error messages leak `intake` / `orchestrator`:\n  - "
        + "\n  - ".join(violations)
    )
