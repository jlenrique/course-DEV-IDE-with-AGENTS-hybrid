"""Tests for scripts/validate_fidelity_contracts.py.

Covers the short-circuit precondition enforcement added per the
party-mode Blocker-A consensus (A2 + blocks_on), plus regression coverage
for the existing schema checks so a broken fidelity contract never reaches
CI silently.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import yaml

from scripts.validate_fidelity_contracts import validate_contract


def _write_contract(tmp_path: Path, body: str) -> Path:
    filepath = tmp_path / "g9-test.yaml"
    filepath.write_text(textwrap.dedent(body).lstrip(), encoding="utf-8")
    return filepath


def _base_contract() -> dict:
    """Minimal valid contract: one deterministic + one agentic with blocks_on."""
    return {
        "gate": "G9",
        "gate_name": "Test Gate",
        "producing_agent": "test-agent",
        "source_of_truth": {
            "primary": "test source",
            "schema_ref": "test/schema.md",
        },
        "criteria": [
            {
                "id": "G9-01",
                "name": "deterministic first",
                "description": "must run first",
                "fidelity_class": ["creative"],
                "severity": "high",
                "evaluation_type": "deterministic",
                "check": "count(x) == 1",
                "requires_perception": False,
            },
            {
                "id": "G9-02",
                "name": "agentic with blocks_on",
                "description": "must block on G9-01",
                "fidelity_class": ["creative"],
                "severity": "high",
                "evaluation_type": "agentic",
                "check": "semantic judgment",
                "requires_perception": False,
                "blocks_on": ["G9-01"],
            },
        ],
    }


def _write_dict(tmp_path: Path, data: dict) -> Path:
    filepath = tmp_path / "g9-test.yaml"
    filepath.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return filepath


class TestBaselineSchema:
    """Regression tests for the pre-existing schema surface."""

    def test_minimal_valid_contract_has_no_errors(self, tmp_path: Path) -> None:
        filepath = _write_dict(tmp_path, _base_contract())
        assert validate_contract(filepath) == []

    def test_missing_top_level_field_detected(self, tmp_path: Path) -> None:
        contract = _base_contract()
        del contract["gate_name"]
        filepath = _write_dict(tmp_path, contract)
        errors = validate_contract(filepath)
        assert any("Missing required top-level field: gate_name" in e for e in errors)

    def test_missing_schema_ref_detected(self, tmp_path: Path) -> None:
        contract = _base_contract()
        del contract["source_of_truth"]["schema_ref"]
        filepath = _write_dict(tmp_path, contract)
        errors = validate_contract(filepath)
        assert any("source_of_truth missing field: schema_ref" in e for e in errors)

    def test_invalid_severity_detected(self, tmp_path: Path) -> None:
        contract = _base_contract()
        contract["criteria"][0]["severity"] = "catastrophic"
        filepath = _write_dict(tmp_path, contract)
        errors = validate_contract(filepath)
        assert any("invalid severity 'catastrophic'" in e for e in errors)

    def test_invalid_evaluation_type_detected(self, tmp_path: Path) -> None:
        contract = _base_contract()
        contract["criteria"][0]["evaluation_type"] = "vibes"
        filepath = _write_dict(tmp_path, contract)
        errors = validate_contract(filepath)
        assert any("invalid evaluation_type 'vibes'" in e for e in errors)

    def test_duplicate_criterion_id_detected(self, tmp_path: Path) -> None:
        contract = _base_contract()
        contract["criteria"][1]["id"] = "G9-01"
        filepath = _write_dict(tmp_path, contract)
        errors = validate_contract(filepath)
        assert any("duplicate id 'G9-01'" in e for e in errors)


class TestOrderingInvariant:
    """A2: deterministic criteria must precede agentic criteria."""

    def test_deterministic_before_agentic_passes(self, tmp_path: Path) -> None:
        filepath = _write_dict(tmp_path, _base_contract())
        assert validate_contract(filepath) == []

    def test_deterministic_after_agentic_fails(self, tmp_path: Path) -> None:
        contract = _base_contract()
        # Swap order: agentic first, deterministic second.
        contract["criteria"] = [contract["criteria"][1], contract["criteria"][0]]
        filepath = _write_dict(tmp_path, contract)
        errors = validate_contract(filepath)
        assert any(
            "deterministic criterion 'G9-01' appears after agentic criterion" in e
            for e in errors
        )

    def test_multiple_deterministic_after_agentic_all_reported(self, tmp_path: Path) -> None:
        contract = _base_contract()
        contract["criteria"] = [
            {
                "id": "G9-A",
                "name": "agentic first",
                "description": "wrong place",
                "fidelity_class": ["creative"],
                "severity": "high",
                "evaluation_type": "agentic",
                "check": "check",
                "requires_perception": False,
                "blocks_on": ["G9-B"],
            },
            {
                "id": "G9-B",
                "name": "deterministic after",
                "description": "violation 1",
                "fidelity_class": ["creative"],
                "severity": "high",
                "evaluation_type": "deterministic",
                "check": "check",
                "requires_perception": False,
            },
            {
                "id": "G9-C",
                "name": "deterministic after agentic, second time",
                "description": "violation 2",
                "fidelity_class": ["creative"],
                "severity": "high",
                "evaluation_type": "deterministic",
                "check": "check",
                "requires_perception": False,
            },
        ]
        filepath = _write_dict(tmp_path, contract)
        errors = validate_contract(filepath)
        ordering_errors = [e for e in errors if "appears after agentic criterion" in e]
        assert len(ordering_errors) == 2
        assert any("'G9-B'" in e for e in ordering_errors)
        assert any("'G9-C'" in e for e in ordering_errors)


class TestBlocksOnInvariant:
    """A2: every agentic criterion must declare blocks_on with real sibling ids."""

    def test_agentic_without_blocks_on_fails(self, tmp_path: Path) -> None:
        contract = _base_contract()
        del contract["criteria"][1]["blocks_on"]
        filepath = _write_dict(tmp_path, contract)
        errors = validate_contract(filepath)
        assert any(
            "agentic criterion 'G9-02' missing required blocks_on field" in e for e in errors
        )

    def test_agentic_with_empty_blocks_on_fails(self, tmp_path: Path) -> None:
        contract = _base_contract()
        contract["criteria"][1]["blocks_on"] = []
        filepath = _write_dict(tmp_path, contract)
        errors = validate_contract(filepath)
        assert any("blocks_on must be a non-empty list" in e for e in errors)

    def test_agentic_blocks_on_nonlist_fails(self, tmp_path: Path) -> None:
        contract = _base_contract()
        contract["criteria"][1]["blocks_on"] = "G9-01"  # string instead of list
        filepath = _write_dict(tmp_path, contract)
        errors = validate_contract(filepath)
        assert any("blocks_on must be a non-empty list" in e for e in errors)

    def test_agentic_blocks_on_references_unknown_id_fails(self, tmp_path: Path) -> None:
        contract = _base_contract()
        contract["criteria"][1]["blocks_on"] = ["G9-99"]
        filepath = _write_dict(tmp_path, contract)
        errors = validate_contract(filepath)
        assert any(
            "blocks_on references 'G9-99' which is not a deterministic sibling id" in e
            for e in errors
        )

    def test_agentic_blocks_on_references_agentic_sibling_fails(self, tmp_path: Path) -> None:
        """Agentic criteria can only block on deterministic siblings — not other agentic."""
        contract = _base_contract()
        contract["criteria"].append(
            {
                "id": "G9-03",
                "name": "another agentic",
                "description": "agentic",
                "fidelity_class": ["creative"],
                "severity": "high",
                "evaluation_type": "agentic",
                "check": "check",
                "requires_perception": False,
                "blocks_on": ["G9-02"],  # references agentic, not deterministic
            }
        )
        filepath = _write_dict(tmp_path, contract)
        errors = validate_contract(filepath)
        assert any(
            "blocks_on references 'G9-02' which is not a deterministic sibling id" in e
            for e in errors
        )

    def test_deterministic_may_omit_blocks_on(self, tmp_path: Path) -> None:
        """Deterministic criteria don't require blocks_on; optional field."""
        contract = _base_contract()
        # G9-01 is deterministic and has no blocks_on — must not be an error.
        filepath = _write_dict(tmp_path, contract)
        errors = validate_contract(filepath)
        assert not any("G9-01" in e and "blocks_on" in e for e in errors)

    def test_deterministic_with_blocks_on_must_reference_real_ids(self, tmp_path: Path) -> None:
        contract = _base_contract()
        contract["criteria"][0]["blocks_on"] = ["G9-NOPE"]
        filepath = _write_dict(tmp_path, contract)
        errors = validate_contract(filepath)
        assert any(
            "blocks_on references 'G9-NOPE' which is not a deterministic sibling id" in e
            for e in errors
        )


class TestRepoContractsAllValid:
    """Smoke test: every real contract in the repo passes validation.

    Guards against future drift introduced outside the validator test suite.
    """

    def test_all_repo_contracts_pass(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        contracts_dir = repo_root / "state" / "config" / "fidelity-contracts"
        contract_files = sorted(contracts_dir.glob("g*.yaml"))
        assert contract_files, "expected at least one contract file"
        failures: dict[str, list[str]] = {}
        for filepath in contract_files:
            errors = validate_contract(filepath)
            if errors:
                failures[filepath.name] = errors
        assert not failures, f"repo contracts failed validation: {failures}"
