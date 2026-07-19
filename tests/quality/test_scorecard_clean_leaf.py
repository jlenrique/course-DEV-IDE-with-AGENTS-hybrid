"""Story Q1.1 — AC5: ``app.quality`` clean-leaf structural guard (GL-3).

Asserts that every module in the ``app/quality/`` package (recursively — including
future subpackages such as Q1.2's signal readers) imports **zero** foreign ``app.*``
modules at module scope. This is the leaf's honesty-pin: ``app.quality`` is in zero
import-linter contracts today, so this pytest — not CI import-linter — is the guard
that keeps the reader a clean, cheaply-importable leaf (NFR4). It must stay green
from here through Q1.2, which computes fence facts at the ``production_runner`` seam
and passes them in as plain data precisely so this test never goes red.

"Module scope" here is *runtime* module scope: the top-level statement list PLUS the
bodies of module-level ``if`` / ``try`` / ``with`` / ``for`` / ``while`` blocks (a
foreign import nested in a bare ``try: import app.x`` still couples at import time).
It deliberately does NOT descend into ``def`` / ``async def`` / ``class`` bodies —
function-local deferred imports are the sanctioned GL-3 escape hatch. Two carve-outs:

  * ``if TYPE_CHECKING:`` blocks are type-only (never executed at runtime) → exempt;
  * relative imports (``from .x import …``, ``node.level > 0``) reference no
    ``app.*`` name at all → allowed (intra-package cohesion).

"Foreign" = any absolute ``app.*`` import whose target is outside this package's own
subtree (``app.quality`` / ``app.quality.*``).

RED-first witness (both demonstrated during development, then reverted):
  (i) a subpackage module ``app/quality/_scratch_subpkg/x.py`` with a module-scope
      ``import app.marcus`` → the recursive scan FAILS naming that file;
  (ii) a module-scope ``try: import app.marcus / except Exception: pass`` in an
      existing module → the block-descending scan FAILS.
  And ``if TYPE_CHECKING:`` + ``from app.marcus import X`` does NOT trip it.
See the story's Completion Notes / Debug Log.
"""

from __future__ import annotations

import ast
from pathlib import Path

_PKG_DIR = Path(__file__).resolve().parents[2] / "app" / "quality"
_OWN_PREFIX = "app.quality"

# Compound statements whose bodies still execute at module import time — the scan
# descends into these. FunctionDef/AsyncFunctionDef/ClassDef are intentionally absent
# (their bodies are deferred / not import-time module scope).
_DESCEND_INTO = (ast.With, ast.AsyncWith, ast.For, ast.AsyncFor, ast.While)


def _is_type_checking_test(test: ast.expr) -> bool:
    """True for ``TYPE_CHECKING`` / ``typing.TYPE_CHECKING`` guard expressions."""
    if isinstance(test, ast.Name):
        return test.id == "TYPE_CHECKING"
    if isinstance(test, ast.Attribute):
        return test.attr == "TYPE_CHECKING"
    return False


def _iter_module_scope_imports(body: list[ast.stmt]):
    """Yield Import/ImportFrom nodes reachable at import time from ``body``.

    Recurses through module-level compound statements but not into function/class
    bodies; skips the body of an ``if TYPE_CHECKING:`` guard (its ``orelse`` still
    runs at runtime, so that branch is still walked).
    """
    for node in body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            yield node
        elif isinstance(node, ast.If):
            if not _is_type_checking_test(node.test):
                yield from _iter_module_scope_imports(node.body)
            # The else-branch of `if TYPE_CHECKING:` executes at runtime → always walk.
            yield from _iter_module_scope_imports(node.orelse)
        elif isinstance(node, ast.Try):
            yield from _iter_module_scope_imports(node.body)
            for handler in node.handlers:
                yield from _iter_module_scope_imports(handler.body)
            yield from _iter_module_scope_imports(node.orelse)
            yield from _iter_module_scope_imports(node.finalbody)
        elif isinstance(node, _DESCEND_INTO):
            yield from _iter_module_scope_imports(node.body)
            yield from _iter_module_scope_imports(getattr(node, "orelse", []))
        # def / async def / class / everything else: do not descend.


def _is_foreign_app(module: str) -> bool:
    if not (module == "app" or module.startswith("app.")):
        return False
    # Allow the package's own subtree (app.quality / app.quality.*).
    return not (module == _OWN_PREFIX or module.startswith(_OWN_PREFIX + "."))


def _foreign_app_imports(source: str) -> list[str]:
    tree = ast.parse(source)
    violations: list[str] = []
    for node in _iter_module_scope_imports(tree.body):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if _is_foreign_app(alias.name):
                    violations.append(f"import {alias.name} (line {node.lineno})")
        # level>0 => relative import (e.g. `from .scorecard import x`) — allowed.
        elif (
            isinstance(node, ast.ImportFrom)
            and node.level == 0
            and node.module
            and _is_foreign_app(node.module)
        ):
            violations.append(f"from {node.module} import … (line {node.lineno})")
    return violations


def test_app_quality_is_a_clean_leaf() -> None:
    py_files = sorted(p for p in _PKG_DIR.rglob("*.py") if "__pycache__" not in p.parts)
    assert py_files, f"expected python modules under {_PKG_DIR}"
    all_violations: dict[str, list[str]] = {}
    for path in py_files:
        found = _foreign_app_imports(path.read_text(encoding="utf-8"))
        if found:
            all_violations[path.relative_to(_PKG_DIR).as_posix()] = found
    assert not all_violations, (
        "app.quality must import zero foreign app.* modules at module scope "
        f"(clean-leaf / GL-3); violations: {all_violations}"
    )
