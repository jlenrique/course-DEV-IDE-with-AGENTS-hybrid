from __future__ import annotations

from pathlib import Path

import pytest

from app.specialists.vision.provider import VisionProviderError, perceive_png


@pytest.mark.live
def test_live_vision_roundtrip_skips_when_provider_unreachable(tmp_path: Path) -> None:
    png = tmp_path / "slide.png"
    png.write_bytes(b"\x89PNG\r\n\x1a\nfixture")
    try:
        artifact = perceive_png(png, slide_id="slide-live")
    except VisionProviderError as exc:
        pytest.skip(f"vision provider unavailable: {exc}")

    assert artifact.slide_id == "slide-live"
    assert artifact.coverage in {"perceived", "low-confidence", "not-covered"}
