"""AST and import-time guardrails for FR34 tamper-evidence."""

from __future__ import annotations

import ast
import sys
from collections.abc import Iterable
from pathlib import Path

from app.gates.errors import SchedulerImportError, UnauthorizedResumeBypassError

_FORBIDDEN_MODULES = {"threading", "apscheduler", "schedule"}
_FORBIDDEN_LOADED_MODULES = {"apscheduler", "schedule"}


def assert_scheduler_modules_not_loaded() -> None:
    """Import-time guard against runtime-loaded scheduler frameworks."""
    for module_name in sorted(_FORBIDDEN_LOADED_MODULES):
        if module_name in sys.modules:
            raise SchedulerImportError(
                f"forbidden scheduler module {module_name!r} already loaded in sys.modules"
            )


def _call_name(node: ast.Call) -> str | None:
    func = node.func
    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
        return f"{func.value.id}.{func.attr}"
    if isinstance(func, ast.Name):
        return func.id
    return None


def assert_no_scheduler_or_bypass_source(source: str, *, source_name: str) -> None:
    """Reject scheduler imports and direct `Command(resume=...)` bypass patterns."""
    tree = ast.parse(source, filename=source_name)
    allow_direct_resume = source_name.endswith("resume_api.py")
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root_name = alias.name.split(".", 1)[0]
                if root_name in _FORBIDDEN_MODULES:
                    raise SchedulerImportError(
                        f"{source_name} imports forbidden scheduler module {alias.name!r}"
                    )
        if isinstance(node, ast.ImportFrom) and node.module:
            root_name = node.module.split(".", 1)[0]
            if root_name in _FORBIDDEN_MODULES:
                raise SchedulerImportError(
                    f"{source_name} imports forbidden scheduler module {node.module!r}"
                )
        if isinstance(node, ast.Call):
            call_name = _call_name(node)
            if call_name == "asyncio.sleep":
                raise SchedulerImportError(
                    f"{source_name} calls forbidden scheduler primitive 'asyncio.sleep'"
                )
            if not allow_direct_resume and call_name == "Command" and any(
                keyword.arg == "resume" for keyword in node.keywords if keyword.arg is not None
            ):
                raise UnauthorizedResumeBypassError(
                    f"{source_name} constructs Command(resume=...) directly"
                )


def scan_paths(paths: Iterable[Path]) -> None:
    for path in paths:
        assert_no_scheduler_or_bypass_source(
            path.read_text(encoding="utf-8"),
            source_name=str(path),
        )


__all__ = [
    "assert_no_scheduler_or_bypass_source",
    "assert_scheduler_modules_not_loaded",
    "scan_paths",
]
