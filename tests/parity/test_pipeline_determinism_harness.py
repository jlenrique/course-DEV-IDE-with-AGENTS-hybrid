from __future__ import annotations

import hashlib

import pytest

from app.specialists.compositor import _act as compositor_act
from tests.specialists.compositor._fixtures import compositor_payload


def _asset_hashes(verdict: dict[str, object]) -> tuple[str, ...]:
    synced = verdict["synced_assets"]
    assert isinstance(synced, dict)
    paths = [path for group in synced.values() for path in group.values()]
    return tuple(
        sorted(
            hashlib.sha256(compositor_act.Path(str(path)).read_bytes()).hexdigest()
            for path in paths
        )
    )


@pytest.mark.timeout(120)
def test_compositor_pipeline_determinism_harness(tmp_path) -> None:
    snapshots: list[tuple[tuple[str, ...], str]] = []
    for _ in range(10):
        payload = compositor_payload(tmp_path)
        verdict = compositor_act.run_compositor_pipeline(payload)
        snapshots.append((_asset_hashes(verdict), str(verdict["assembly_guide_field_masked_hash"])))

    baseline = snapshots[0]
    matches = sum(1 for snapshot in snapshots if snapshot == baseline)
    assert matches >= 9
    assert matches / len(snapshots) >= 0.99
