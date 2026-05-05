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


def test_c5_is_populated_and_c6_forbidden_modules_remain_empty():
    contracts_by_name = {contract["name"]: contract for contract in _contracts()}

    assert (
        set(contracts_by_name[
            "C5: §02A composer boundary may not import corpus-scan fallback paths"
        ]["forbidden_modules"])
        == EXPECTED_C5_FORBIDDEN
    )
    assert (
        contracts_by_name[
            "C6: HIL-surface modules may not import each other across surfaces"
        ]["forbidden_modules"]
        == []
    )


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
