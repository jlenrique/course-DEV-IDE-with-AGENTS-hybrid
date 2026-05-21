from __future__ import annotations

import yaml

from scripts.utilities.validate_parity_test_class_conformance import (
    RUNTIME_GATE_IDS,
    build_tw_7c_3_entry,
    gate_lockstep_result,
    is_valid_runtime_gate_id,
    write_tripwire_entry,
)

EXPECTED_RUNTIME_IDS = frozenset(
    {
        "G0",
        "G0A",
        "G0B",
        "G1",
        "G1A",
        "G1.5",
        "G2",
        "G2B",
        "G2C",
        "G2M",
        "G2.5",
        "G2F",
        "G3",
        "G3B",
        "G4",
        "G4A",
        "G4B",
        "G5",
    }
)


def test_validator_recognizes_all_18_runtime_gate_ids() -> None:
    assert RUNTIME_GATE_IDS == EXPECTED_RUNTIME_IDS
    assert all(is_valid_runtime_gate_id(gate_id) for gate_id in EXPECTED_RUNTIME_IDS)
    assert not is_valid_runtime_gate_id("G6")
    assert not is_valid_runtime_gate_id("G9")


def test_lockstep_check_reports_missing_g0_four_file_set(tmp_path) -> None:
    result = gate_lockstep_result("G0", repo_root=tmp_path)

    assert result.gate_id == "G0"
    assert result.all_four_present is False
    assert set(result.files_present) == {
        "golden_fixture",
        "model",
        "schema",
        "shape_pin",
    }
    assert result.failure_reason


def test_tw_7c_3_firing_entry_can_write_to_tmp_ledger(tmp_path) -> None:
    sprint_status = tmp_path / "sprint-status.yaml"
    sprint_status.write_text("tripwire_events: []\n", encoding="utf-8")
    result = gate_lockstep_result("G0", repo_root=tmp_path)
    entry = build_tw_7c_3_entry(gate_id="G0", result=result)

    write_tripwire_entry(sprint_status, entry)

    payload = yaml.safe_load(sprint_status.read_text(encoding="utf-8"))
    event = payload["tripwire_events"][0]
    assert event["tripwire_id"] == "TW-7c-3"
    assert event["fired_verdict"] == "fired"
    assert event["severity"] == "critical"
    assert event["measured_value"]["gate_id"] == "G0"
