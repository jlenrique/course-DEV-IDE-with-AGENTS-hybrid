"""Broad-suite mirror of the frozen-pack SHA registry (Arc-1a, Murat condition b).

The authoritative check lives in `check_pipeline_manifest_lockstep.py` check 10
(L1, where the pipeline-manifest regime gates). This mirror trips for any dev
running `pytest` without invoking L1 — it is a cheap hash compare, no
determinism flakiness.

Two distinct risks are pinned (Murat):
  * `mapping-axis-frozen` (v4.2) — freeze-integrity: a silent in-place
    regeneration would shift the legacy axis the slab-7 mapping checklist maps
    against (the defect already caught once during this arc).
  * `production-canonical` (v5) — anti-regeneration: v5 is hand-authored and
    OUTSIDE the lockstep loop, so a SHA pin + `generated: false` sentinel is the
    tripwire against a future generator run overwriting hand-authored content.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REGISTRY = PROJECT_ROOT / "state" / "config" / "frozen-pack-shas.json"


def _registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def _safe_registry() -> dict:
    """Collection-time safe: a missing/malformed registry must NOT crash module
    collection — it lets `test_registry_exists_and_parses` emit the actionable
    failure instead (Arc-1a code review, Edge Case Hunter SHOULD-FIX)."""
    try:
        return _registry()
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def test_registry_exists_and_parses() -> None:
    assert REGISTRY.exists(), "frozen-pack-shas.json registry missing"
    reg = _registry()
    assert reg.get("frozen_packs"), "registry must declare at least one frozen pack"


@pytest.mark.parametrize("rel_path", list(_safe_registry().get("frozen_packs", {})))
def test_frozen_pack_sha_matches_disk(rel_path: str) -> None:
    meta = _registry()["frozen_packs"][rel_path]
    fp = PROJECT_ROOT / rel_path
    assert fp.exists(), f"frozen pack missing: {rel_path}"
    disk_sha = hashlib.sha256(fp.read_bytes()).hexdigest()
    assert disk_sha == meta["sha256"], (
        f"{rel_path} SHA drift (frozen-at-ship violation). "
        f"If this change is intended, re-pin the SHA in the registry in the SAME commit. "
        f"expected={meta['sha256']} disk={disk_sha}"
    )


@pytest.mark.parametrize("rel_path", list(_safe_registry().get("frozen_packs", {})))
def test_generated_false_sentinel_intact(rel_path: str) -> None:
    meta = _registry()["frozen_packs"][rel_path]
    if meta.get("generated") is not False:
        pytest.skip(f"{rel_path} is not a generated:false pack")
    fp = PROJECT_ROOT / rel_path
    assert "generated: false" in fp.read_text(encoding="utf-8")[:3000], (
        f"{rel_path} lost its `generated: false` anti-regeneration sentinel"
    )
