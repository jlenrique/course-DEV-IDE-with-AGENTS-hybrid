from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def _pyproject_text() -> str:
    return Path("pyproject.toml").read_text(encoding="utf-8")


def test_cora_to_marcus_import_boundary_rule_declared() -> None:
    pyproject = _pyproject_text()

    assert "Cora Contract C1 - app.cora may not import app.marcus or marcus" in pyproject
    assert 'source_modules = ["app.cora"]' in pyproject
    assert 'forbidden_modules = ["app.marcus", "marcus"]' in pyproject


def test_marcus_to_cora_import_boundary_rule_declared_and_lint_passes() -> None:
    pyproject = _pyproject_text()

    assert "Cora Contract C2 - Marcus may not import app.cora" in pyproject
    assert 'source_modules = ["app.marcus", "marcus"]' in pyproject
    assert 'forbidden_modules = ["app.cora"]' in pyproject

    lint_imports_cmd = shutil.which("lint-imports")
    if lint_imports_cmd is None:
        lint_imports_cmd = str(Path(sys.executable).with_name("lint-imports.exe"))
    result = subprocess.run(
        [lint_imports_cmd, "--config", "pyproject.toml"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
