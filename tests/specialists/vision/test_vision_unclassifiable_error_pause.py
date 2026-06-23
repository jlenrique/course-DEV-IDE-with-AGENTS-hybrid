"""Unclassifiable HIGH/perceived artifacts safe-degrade instead of hard-pausing."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest

from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.vision import _act
from app.specialists.vision.payload_contract import VisionProviderResponse


def _state(payload: dict[str, Any]) -> RunState:
    return RunState(
        run_id=uuid4(),
        graph_version="v42",
        model_resolution_trail=[
            ModelResolutionEntry(
                level="registry_default",
                requested=None,
                resolved="gpt-5.5",
                reason="test",
                timestamp=datetime.now(UTC),
                cache_prefix_hash="0" * 64,
            )
        ],
        cache_state=CacheState(cache_prefix=json.dumps(payload), entries_count=1),
    )


def _png(tmp_path: Path) -> Path:
    path = tmp_path / "slide-01.png"
    path.write_bytes(b"\x89PNG\r\n\x1a\nfixture")
    return path


def test_unclassifiable_high_perceived_artifact_safe_defaults_and_does_not_retry(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    png = _png(tmp_path)
    calls = 0

    def fake_perceive(path: Path, *, slide_id: str, **_: Any) -> VisionProviderResponse:
        nonlocal calls
        calls += 1
        return VisionProviderResponse(
            slide_id=slide_id,
            confidence="HIGH",
            coverage="perceived",
            provenance="png-grounded",
            extracted_text="Building photo only.",
            layout_description="A single building photo.",
            visual_elements=[{"id": "building", "kind": "photo", "label": "building photo"}],
            source_png_path="slide-01.png",
            provider_model_id="gpt-5.5",
        )

    monkeypatch.setattr(_act, "perceive_png", fake_perceive)
    monkeypatch.setattr(
        "scripts.utilities.reading_path_classifier.request_live_reading_path_tuple",
        lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("transport down")),
    )
    payload = {"gary_slide_output": [{"slide_id": "slide-01", "file_path": str(png)}]}

    result = _act.act(_state(payload))
    artifact = json.loads(result["cache_state"]["cache_prefix"])["perception_artifacts"][0]

    assert calls == 1
    assert artifact["reading_path"] == "top_down"
    assert artifact["macro_layout"] == "single_text_block"
    assert artifact["reading_path_source"] == "safe_default"
    assert artifact["reading_path_degraded"] is True
    assert artifact["reading_path_rationale"] == {"degraded": "transport down"}


def test_empty_visual_elements_emit_controlled_empty_image_roles_without_pause(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    png = _png(tmp_path)

    def fake_perceive(path: Path, *, slide_id: str, **_: Any) -> VisionProviderResponse:
        return VisionProviderResponse(
            slide_id=slide_id,
            confidence="HIGH",
            coverage="perceived",
            provenance="png-grounded",
            extracted_text="No visible objects returned.",
            layout_description="Empty perception result.",
            visual_elements=[],
            source_png_path="slide-01.png",
            provider_model_id="gpt-5.5",
        )

    monkeypatch.setattr(_act, "perceive_png", fake_perceive)
    monkeypatch.setattr(
        "scripts.utilities.reading_path_classifier.request_live_reading_path_tuple",
        lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("transport down")),
    )
    payload = {"gary_slide_output": [{"slide_id": "slide-01", "file_path": str(png)}]}

    result = _act.act(_state(payload))
    output = json.loads(result["cache_state"]["cache_prefix"])

    artifact = output["perception_artifacts"][0]
    assert artifact["reading_path"] == "top_down"
    assert artifact["macro_layout"] == "single_text_block"
    assert artifact["image_roles"] == []
    assert artifact["reading_path_source"] == "safe_default"
