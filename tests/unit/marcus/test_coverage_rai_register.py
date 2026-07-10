"""Step 2 — RAI register: the G3 coverage-receipt asset row + enrique consumer.

The OBSERVED receipt is a ``RunAssetEntry`` on the UDAC Run-Asset-Index pinned with
CANONICAL_SHA256, registered at gate G3 (the storyboard-publish seam). ``enrique``
(the audio-spend consumer) declares it USES the coverage-receipt.
"""

from __future__ import annotations

from app.marcus.lesson_plan.coverage_receipt import (
    COVERAGE_RECEIPT_ASSET_ID,
    COVERAGE_RECEIPT_BASENAME,
)
from app.marcus.lesson_plan.run_asset_index import (
    CONSUMER_REGISTRY,
    GATE_ASSET_MAP,
    AssetUsage,
    DigestAlgo,
)


def test_g3_coverage_receipt_asset_registered() -> None:
    assert "G3" in GATE_ASSET_MAP
    specs = GATE_ASSET_MAP["G3"]
    assert len(specs) == 1
    spec = specs[0]
    assert spec.asset_id == COVERAGE_RECEIPT_ASSET_ID == "coverage-receipt"
    assert spec.rel_path == COVERAGE_RECEIPT_BASENAME == "coverage-receipt.json"
    assert spec.digest_algo is DigestAlgo.CANONICAL_SHA256


def test_g1_locked_lesson_plan_asset_registered() -> None:
    specs = GATE_ASSET_MAP["G1"]
    assert len(specs) == 1
    assert specs[0].asset_id == "locked-lesson-plan"
    assert specs[0].rel_path == "irene-pass1.lesson-plan.json"
    assert specs[0].digest_algo is DigestAlgo.CANONICAL_SHA256


def test_g2c_authorized_storyboard_asset_registered() -> None:
    specs = GATE_ASSET_MAP["G2C"]
    assert len(specs) == 1
    assert specs[0].asset_id == "authorized-storyboard"
    assert specs[0].rel_path == "storyboard-publish-G2C.json"
    assert specs[0].digest_algo is DigestAlgo.CANONICAL_SHA256


def test_gate_asset_map_universality_pins_verifiable_run_dir_rows() -> None:
    """Mine-next T1: G0E/G0R/G1/G2C/G3 are pinned; G4/G4A stay OUT until run-dir paths exist."""
    assert set(GATE_ASSET_MAP) >= {"G0E", "G0R", "G1", "G2C", "G3"}
    assert "G4" not in GATE_ASSET_MAP
    assert "G4A" not in GATE_ASSET_MAP


def test_enrique_declares_coverage_receipt_used() -> None:
    enrique = CONSUMER_REGISTRY["enrique"]
    by_asset = {c.asset_id: c.usage for c in enrique.consumes}
    assert by_asset.get("coverage-receipt") is AssetUsage.USED
    assert "coverage-receipt" in enrique.required_assets()
