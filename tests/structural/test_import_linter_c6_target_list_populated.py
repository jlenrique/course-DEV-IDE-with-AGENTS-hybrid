from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = REPO_ROOT / "pyproject.toml"
if sys.platform == "win32":
    LINT_IMPORTS = REPO_ROOT / ".venv" / "Scripts" / "lint-imports.exe"
else:
    LINT_IMPORTS = REPO_ROOT / ".venv" / "bin" / "lint-imports"

# T11 P-1 patch on 7c.4b: C6 became `independence` type. Modules list grows
# incrementally as each §section package lands. Today only section_02a
# exists; the full target population spans these 12 §sections.
ALL_SECTION_TARGETS = [
    "app.gates.section_02a",
    "app.gates.section_04a",
    "app.gates.section_04_5",
    "app.gates.section_04_55",
    "app.gates.section_05_5",
    "app.gates.section_06b",
    "app.gates.section_07b",
    "app.gates.section_07c",
    "app.gates.section_07d",
    "app.gates.section_07f",
    "app.gates.section_08b",
    "app.gates.section_11",
    "app.gates.section_11b",
    "app.gates.section_15",
]


def _c6_contract() -> dict[str, object]:
    payload = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    contracts = payload["tool"]["importlinter"]["contracts"]
    for contract in contracts:
        if str(contract["name"]).startswith("C6:"):
            return contract
    raise AssertionError("C6 import-linter contract not found")


def test_c6_uses_independence_contract_type() -> None:
    contract = _c6_contract()
    assert contract["type"] == "independence", (
        "C6 must use the `independence` contract type so cross-§section "
        "imports are caught symmetrically and lint-imports tolerates the "
        "incremental modules-list growth pattern."
    )


def test_c6_modules_list_is_subset_of_known_section_targets() -> None:
    contract = _c6_contract()
    modules = contract["modules"]
    assert isinstance(modules, list)
    assert len(modules) >= 1, "C6 modules list must include at least app.gates.section_02a"
    for module in modules:
        assert module in ALL_SECTION_TARGETS, (
            f"C6 modules list contains unknown §section target: {module!r}. "
            f"Known targets are: {ALL_SECTION_TARGETS}"
        )


def test_c6_modules_list_includes_section_02a() -> None:
    contract = _c6_contract()
    assert "app.gates.section_02a" in contract["modules"], (
        "section_02a is the canonical HIL pattern and must always be in C6."
    )


def test_lint_imports_still_reports_12_kept() -> None:
    result = subprocess.run(
        [str(LINT_IMPORTS)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Contracts: 12 kept, 0 broken." in result.stdout
