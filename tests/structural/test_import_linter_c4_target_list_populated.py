from __future__ import annotations

import subprocess
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_C4_FORBIDDEN = {
    "app.gates.resume_api",
    "app.marcus.orchestrator.write_api",
    "app.specialists.*",
}
EXPECTED_C5_FORBIDDEN = {
    "app.composers._fallback",
    "app.composers.legacy",
    "app.marcus.orchestrator.directive_composer",
}
# C6 became `independence` type per T11 P-1 patch on 7c.4b. The full
# §section target population (filled in incrementally as each §section
# package lands per 7c.6 / 7c.7 / ... / 7c.15) spans these 12 modules.
EXPECTED_C6_SECTION_TARGETS = {
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
}


def _contracts() -> list[dict]:
    data = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return data["tool"]["importlinter"]["contracts"]


def test_c4_forbidden_modules_target_list_is_populated():
    c4 = next(
        contract
        for contract in _contracts()
        if contract["name"].startswith("C4: parity-DSL boundary")
    )

    assert set(c4["forbidden_modules"]) == EXPECTED_C4_FORBIDDEN
    assert c4["source_modules"] == ["app.parity.contracts.*"]


def test_c5_forbidden_modules_and_c6_independence_modules_are_populated():
    contracts_by_name = {contract["name"]: contract for contract in _contracts()}

    assert (
        set(contracts_by_name[
            "C5: §02A composer boundary may not import corpus-scan fallback paths"
        ]["forbidden_modules"])
        == EXPECTED_C5_FORBIDDEN
    )
    c6 = contracts_by_name[
        "C6: HIL-surface modules may not import each other across surfaces"
    ]
    assert c6["type"] == "independence"
    assert set(c6["modules"]) <= EXPECTED_C6_SECTION_TARGETS
    assert "app.gates.section_02a" in c6["modules"]


def test_import_linter_keeps_contract_count_at_twelve():
    result = subprocess.run(
        [str(REPO_ROOT / ".venv/Scripts/lint-imports.exe")],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Contracts: 12 kept, 0 broken." in result.stdout
