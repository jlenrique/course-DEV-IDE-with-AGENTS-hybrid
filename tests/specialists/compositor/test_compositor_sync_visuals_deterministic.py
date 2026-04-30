from __future__ import annotations

import hashlib

import pytest

from app.specialists.compositor import _act as compositor_act
from tests.specialists.compositor._fixtures import SOURCE_ROOT, compositor_payload


@pytest.mark.timeout(30)
def test_sync_visuals_bytes_identical_across_runs(tmp_path) -> None:
    payload = compositor_payload(tmp_path)
    first = compositor_act.sync_visuals(payload)
    first_bytes = {
        path: hashlib.sha256(path_obj.read_bytes()).hexdigest()
        for path, path_obj in (
            (target, compositor_act.Path(target))
            for group in first.values()
            for target in group.values()
        )
    }

    second = compositor_act.sync_visuals(payload)
    second_bytes = {
        path: hashlib.sha256(compositor_act.Path(path).read_bytes()).hexdigest()
        for group in second.values()
        for path in group.values()
    }

    assert first == second
    assert first_bytes == second_bytes
    assert (tmp_path / "bundle" / "assembly-bundle" / "visuals" / "slide-01.png").read_bytes() == (
        SOURCE_ROOT / "slide-01.png"
    ).read_bytes()
