from __future__ import annotations

from pathlib import Path

from app.manifest.loader import load

REPO_ROOT = Path(__file__).resolve().parents[3]
LIVE_MANIFEST = REPO_ROOT / "state" / "config" / "pipeline-manifest.yaml"

EXPECTED_FOLD_WITH = {
    "G0": "G1",
    "G0A": "G1",
    "G0B": "G1",
    "G1": None,
    "G1A": "G2C",
    "G2": "G2C",
    "G1.5": "G2C",
    "G2.5": "G2C",
    "G2B": "G2C",
    "G2C": None,
    "G2M": "G2C",
    "G2F": "G3",
    "G3B": "G3",
    "G3": None,
    "G4": None,
    "G4A": "G4",
    "G4B": "G4",
    "G5": "G4",
}


def test_live_manifest_declares_canonical_fold_with_values() -> None:
    manifest = load(LIVE_MANIFEST)
    actual = {
        node.gate_code: node.fold_with
        for node in manifest.nodes
        if node.gate and node.gate_code
    }

    assert actual == EXPECTED_FOLD_WITH
