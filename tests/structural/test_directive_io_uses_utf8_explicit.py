from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FILES_TO_SCAN = (
    REPO_ROOT / "app/marcus/cli/trial.py",
    REPO_ROOT / "app/marcus/orchestrator/directive_composer.py",
    REPO_ROOT / "app/composers/section_02a/composer.py",
)
TEXT_IO_METHODS = {"read_text", "write_text", "open"}
BINARY_IO_METHODS = {"read_bytes", "write_bytes"}


def _call_name(node: ast.Call) -> str:
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    if isinstance(node.func, ast.Name):
        return node.func.id
    return ""


def _has_utf8_encoding(node: ast.Call) -> bool:
    return any(
        keyword.arg == "encoding"
        and isinstance(keyword.value, ast.Constant)
        and keyword.value.value == "utf-8"
        for keyword in node.keywords
    )


def _is_binary_open(node: ast.Call) -> bool:
    for arg in node.args[1:2]:
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            return "b" in arg.value
    for keyword in node.keywords:
        if (
            keyword.arg == "mode"
            and isinstance(keyword.value, ast.Constant)
            and isinstance(keyword.value.value, str)
        ):
            return "b" in keyword.value.value
    return False


def _is_directive_site(source_segment: str) -> bool:
    lowered = source_segment.lower()
    return "directive" in lowered


def test_directive_text_io_calls_use_explicit_utf8_encoding():
    violations: list[str] = []
    scanned_binary_sites: list[str] = []

    for path in FILES_TO_SCAN:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = _call_name(node)
            segment = ast.get_source_segment(source, node) or ""
            if name in BINARY_IO_METHODS and _is_directive_site(segment):
                scanned_binary_sites.append(f"{path.relative_to(REPO_ROOT).as_posix()}:{node.lineno}")
                continue
            if name not in TEXT_IO_METHODS or not _is_directive_site(segment):
                continue
            if name == "open" and _is_binary_open(node):
                continue
            if not _has_utf8_encoding(node):
                violations.append(f"{path.relative_to(REPO_ROOT).as_posix()}:{node.lineno}")

    assert scanned_binary_sites
    assert violations == []
