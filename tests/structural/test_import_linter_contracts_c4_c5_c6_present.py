from __future__ import annotations

import re
import subprocess
import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
# Path-portability per NFR-7c-X3: Windows venv binaries live under .venv/Scripts/*.exe;
# POSIX venv binaries live under .venv/bin/*. This conditional preserves
# Windows-first behavior while keeping the test runnable on POSIX CI.
if sys.platform == "win32":
    LINT_IMPORTS = REPO_ROOT / ".venv" / "Scripts" / "lint-imports.exe"
else:
    LINT_IMPORTS = REPO_ROOT / ".venv" / "bin" / "lint-imports"
PRE_7C_0A_KEPT_BASELINE = 9

C4_NAME = "C4: parity-DSL boundary may not import graph-runtime modules"
C5_NAME = "C5: §02A composer boundary may not import corpus-scan fallback paths"
C6_NAME = "C6: HIL-surface modules may not import each other across surfaces"


def _load_contracts() -> list[dict[str, object]]:
    pyproject = tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))
    return pyproject["tool"]["importlinter"]["contracts"]


def _contract_by_name(name: str) -> dict[str, object]:
    contracts = _load_contracts()
    matches = [contract for contract in contracts if contract["name"] == name]
    assert len(matches) == 1, name
    return matches[0]


def test_c4_c5_c6_contracts_exist_by_name_with_empty_forbidden_lists() -> None:
    for name in [C4_NAME, C5_NAME, C6_NAME]:
        contract = _contract_by_name(name)
        assert contract["type"] == "forbidden"
        assert contract["forbidden_modules"] == []
        assert contract["include_external_packages"] is False


def test_contract_source_module_expressions_are_future_safe() -> None:
    c4 = _contract_by_name(C4_NAME)
    c5 = _contract_by_name(C5_NAME)
    c6 = _contract_by_name(C6_NAME)

    assert c4["source_modules"] == ["app.parity.contracts.*"]
    assert c5["source_modules"] == ["app.composers.section_02a.*"]
    assert c6["source_modules"] == [
        "app.gates.section_02a.*",
        "app.gates.section_04a.*",
        "app.gates.section_04_5.*",
        "app.gates.section_04_55.*",
        "app.gates.section_05_5.*",
        "app.gates.section_07b.*",
        "app.gates.section_07d.*",
        "app.gates.section_07f.*",
        "app.gates.section_08b.*",
        "app.gates.section_11.*",
        "app.gates.section_11b.*",
        "app.gates.section_15.*",
    ]


def test_lint_imports_kept_count_increases_by_three() -> None:
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
    assert int(match.group(1)) == PRE_7C_0A_KEPT_BASELINE + 3
