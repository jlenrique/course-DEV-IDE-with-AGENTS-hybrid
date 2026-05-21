from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ADR_PATH = (
    REPO_ROOT / "docs" / "dev-guide" / "adr" / "0002-slab-7c-gate-taxonomy.md"
)

FAMILY_IDS = {"G0", "G1", "G2A", "G2C", "G3", "G4", "G5", "G6"}
RUNTIME_IDS = {
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
ALIAS_MAPPINGS = {
    "G0A": "G1",
    "G0B": "G1",
    "G1A": "G1",
    "G2B": "G2C",
    "G2M": "G2C",
    "G2.5": "G2C",
    "G2F": "G2C",
    "G3B": "G3",
    "G4A": "G4",
    "G4B": "G4",
}


def _read_adr() -> str:
    return ADR_PATH.read_text(encoding="utf-8")


def test_adr_0002_slab_7c_gate_taxonomy_exists() -> None:
    assert ADR_PATH.exists(), ADR_PATH.as_posix()


def test_adr_contains_required_taxonomy_sections() -> None:
    text = _read_adr()

    heading_patterns = [
        r"^##\s+\d+\.\s+.*net-new.*gate.*famil",
        r"^##\s+\d+\.\s+.*alias.*gate",
        r"^##\s+\d+\.\s+.*alias.*DSL.*inherit",
        r"^##\s+\d+\.\s+.*PRODUCTION_GATE_IDS.*expansion",
        r"^##\s+\d+\.\s+.*status.*cross-reference",
        r"^##\s+.*worked.*example.*G0A.*inherit.*G1",
    ]

    for pattern in heading_patterns:
        assert re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE), pattern


def test_adr_ratifies_eight_family_contracts_and_ten_aliases() -> None:
    text = _read_adr()

    for gate_id in FAMILY_IDS:
        assert re.search(rf"`{re.escape(gate_id)}`", text), gate_id

    assert "ten explicit mappings" in text
    assert '"6 alias gates" wording' in text
    for alias_id, parent_id in ALIAS_MAPPINGS.items():
        assert re.search(
            rf"\|\s*`{re.escape(alias_id)}`\s*\|\s*`{re.escape(parent_id)}`\s*\|",
            text,
        ), f"{alias_id}->{parent_id}"


def test_adr_ratifies_eighteen_runtime_gate_ids() -> None:
    text = _read_adr()

    assert "18 runtime IDs" in text
    assert '"4 -> 14" phrase' in text
    for gate_id in RUNTIME_IDS:
        assert re.search(rf"\b{re.escape(gate_id)}\b", text), gate_id


def test_worked_example_routes_g0a_to_g1_lockstep_files() -> None:
    text = _read_adr()

    expected_tokens = [
        'surface_id="G0A"',
        'alias_of="G1"',
        "app/models/decision_cards/g1.py",
        "app/models/decision_cards/schema/g1.v1.schema.json",
        "tests/parity/test_decision_card_g1_shape.py",
        "tests/fixtures/decision_cards/g1_golden.json",
        "DecisionCardMeta.cache_state",
    ]

    for token in expected_tokens:
        assert token in text
