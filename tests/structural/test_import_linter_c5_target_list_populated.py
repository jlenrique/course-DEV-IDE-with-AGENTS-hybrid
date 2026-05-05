from __future__ import annotations

import re
import subprocess
import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
if sys.platform == "win32":
    LINT_IMPORTS = REPO_ROOT / ".venv" / "Scripts" / "lint-imports.exe"
else:
    LINT_IMPORTS = REPO_ROOT / ".venv" / "bin" / "lint-imports"

C5_NAME = "C5: §02A composer boundary may not import corpus-scan fallback paths"
EXPECTED_FORBIDDEN_MODULES = [
    "app.composers._fallback",
    "app.composers.legacy",
    "app.marcus.orchestrator.directive_composer",
]


def _c5_contract() -> dict[str, object]:
    pyproject = tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))
    contracts = pyproject["tool"]["importlinter"]["contracts"]
    matches = [contract for contract in contracts if contract["name"] == C5_NAME]
    assert len(matches) == 1, C5_NAME
    return matches[0]


def test_c5_forbidden_modules_populated_with_legacy_composer_guards() -> None:
    contract = _c5_contract()

    assert contract["type"] == "forbidden"
    assert contract["source_modules"] == ["app.composers.section_02a.*"]
    assert contract["forbidden_modules"] == EXPECTED_FORBIDDEN_MODULES
    assert contract["include_external_packages"] is False


def test_lint_imports_kept_count_remains_unchanged_after_c5_population() -> None:
    result = subprocess.run(
        [str(LINT_IMPORTS)],
        check=False,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    match = re.search(r"Contracts:\s+(\d+)\s+kept,\s+0\s+broken", result.stdout)
    assert match, result.stdout
    assert int(match.group(1)) == 12
