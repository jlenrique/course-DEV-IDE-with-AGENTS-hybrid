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


def test_enrique_declares_coverage_receipt_used() -> None:
    enrique = CONSUMER_REGISTRY["enrique"]
    by_asset = {c.asset_id: c.usage for c in enrique.consumes}
    assert by_asset.get("coverage-receipt") is AssetUsage.USED
    assert "coverage-receipt" in enrique.required_assets()
