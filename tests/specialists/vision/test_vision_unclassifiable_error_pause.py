"""AC-7 (RED-first per Murat #6) — unclassifiable HIGH/perceived → NON-retryable error-pause.

A HIGH/perceived artifact whose perceived geometry cannot be deterministically
classified by the reading-path classifier (e.g. visual_elements carry no
positioned bbox) makes the classifier raise ``ReadingPathClassificationError``
(a ValueError). The vision node MUST convert that into a NON-retryable
``VisionProviderError`` tagged ``vision.reading-path.unclassifiable`` that
routes through the error-pause contract and MUST NOT trigger the transport
retry loop (call-count stays at exactly 1).

This is the deterministic error-pause contract authored RED-first BEFORE the
provider rewrite, so the retry/taxonomy semantics are pinned independently of
the live gpt-5.5 wiring.
"""

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
from app.specialists.vision.provider import VisionProviderError


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


def test_unclassifiable_high_perceived_artifact_pauses_and_does_not_retry(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """RED-first AC-7: unclassifiable → non-retryable error-pause, exactly one call."""
    png = _png(tmp_path)
    calls = 0

    def fake_perceive(path: Path, *, slide_id: str, **_: Any) -> VisionProviderResponse:
        nonlocal calls
        calls += 1
        # HIGH/perceived but visual_elements carry NO positioned bbox and the
        # text carries no ordinal cadence — the deterministic classifier cannot
        # assign a reading_path and raises ReadingPathClassificationError.
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
    payload = {"gary_slide_output": [{"slide_id": "slide-01", "file_path": str(png)}]}

    with pytest.raises(VisionProviderError) as excinfo:
        _act.act(_state(payload))

    # The error-pause is tagged for routing and is NON-retryable.
    assert excinfo.value.tag == "vision.reading-path.unclassifiable"
    assert not _act._is_retryable_provider_error(excinfo.value)
    # CRITICAL: the artifact was perceived once and the failure did NOT retry.
    assert calls == 1


def test_empty_visual_elements_pauses_as_controlled_unclassifiable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """P2-4c S1 fold-in: empty visual_elements degrades through error-pause."""
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
    payload = {"gary_slide_output": [{"slide_id": "slide-01", "file_path": str(png)}]}

    with pytest.raises(VisionProviderError) as excinfo:
        _act.act(_state(payload))

    assert excinfo.value.tag == "vision.reading-path.unclassifiable"
    assert not _act._is_retryable_provider_error(excinfo.value)
