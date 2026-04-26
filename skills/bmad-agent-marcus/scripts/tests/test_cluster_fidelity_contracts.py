from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[4]
CONTRACTS_DIR = ROOT / "state" / "config" / "fidelity-contracts"
G2_PATH = CONTRACTS_DIR / "g2-slide-brief.yaml"
G3_PATH = CONTRACTS_DIR / "g3-generated-slides.yaml"
PROTOCOL_PATH = (
    ROOT / "skills" / "bmad-agent-fidelity-assessor" / "references" / "gate-evaluation-protocol.md"
)


def _criterion(contract: dict, criterion_id: str) -> dict:
    return next(c for c in contract["criteria"] if c["id"] == criterion_id)


def test_g2_contract_exempts_interstitial_lo_traceability() -> None:
    contract = yaml.safe_load(G2_PATH.read_text(encoding="utf-8"))
    g2_01 = _criterion(contract, "G2-01")

    assert "interstitial" in g2_01["description"]
    assert "inherit LO coverage" in g2_01["description"]
    assert "cluster_role null or head" in g2_01["check"]
    assert "referenced head slide" in g2_01["check"]


def test_g2_contract_exempts_interstitial_fidelity_classification() -> None:
    contract = yaml.safe_load(G2_PATH.read_text(encoding="utf-8"))
    g2_03 = _criterion(contract, "G2-03")

    assert "inherit the head slide's fidelity classification" in g2_03["description"]
    assert "cluster_role interstitial slides are exempt" in g2_03["check"]


def test_g3_contract_uses_effective_brief_count_formula() -> None:
    contract = yaml.safe_load(G3_PATH.read_text(encoding="utf-8"))
    g3_01 = _criterion(contract, "G3-01")

    assert "effective renderable count" in g3_01["description"]
    assert "cluster heads" in g3_01["description"]
    assert "cluster_role in (null, head)" in g3_01["check"]
    assert "cluster_interstitial_count" in g3_01["check"]


def test_vera_protocol_documents_cluster_carveouts_for_g2_and_g3() -> None:
    protocol = PROTOCOL_PATH.read_text(encoding="utf-8")

    assert "G2-01" in protocol
    assert "inherits LO coverage from its head" in protocol
    assert "G2-03" in protocol
    assert "inherits fidelity from its head" in protocol
    assert "G3-01" in protocol
    assert "cluster_role in (null, head)" in protocol
