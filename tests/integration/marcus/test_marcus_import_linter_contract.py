from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def _pyproject_text() -> str:
    return Path("pyproject.toml").read_text(encoding="utf-8")


def test_write_api_single_writer_rule_declared() -> None:
    pyproject = _pyproject_text()
    assert "Marcus Contract M1" in pyproject
    assert "app.marcus.orchestrator.write_api" in pyproject


def test_no_cora_imports_rule_declared() -> None:
    pyproject = _pyproject_text()
    assert "Marcus Contract M2" in pyproject
    assert 'forbidden_modules = ["app.cora"]' in pyproject


def test_dispatch_contract_shim_re_export_identity() -> None:
    from app.marcus.dispatch.contract import DispatchKind as AppDispatchKind
    from marcus.dispatch.contract import DispatchKind as RootDispatchKind

    assert RootDispatchKind is AppDispatchKind


def test_specialist_to_marcus_boundary_rule_declared() -> None:
    pyproject = _pyproject_text()
    assert "Marcus Contract M3" in pyproject
    assert "app.specialists" in pyproject


def test_dispatch_contract_dependency_rule_declared() -> None:
    pyproject = _pyproject_text()
    assert "Marcus Contract M4" in pyproject
    assert "app.marcus.dispatch" in pyproject


def test_lint_imports_passes_for_repo() -> None:
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
