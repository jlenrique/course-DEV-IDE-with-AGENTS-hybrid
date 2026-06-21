from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import httpx
import pytest

from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.vision import _act
from app.specialists.vision.payload_contract import VisionProviderResponse
from app.specialists.vision.provider import (
    VisionProviderError,
    VisionProviderTimeout,
    perceive_png,
)


def _state(payload: dict[str, Any]) -> RunState:
    return RunState(
        run_id=uuid4(),
        graph_version="v42",
        model_resolution_trail=[
            ModelResolutionEntry(
                level="registry_default",
                requested=None,
                resolved="gpt-5",
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


def _response(slide_id: str = "slide-01", coverage: str = "perceived") -> VisionProviderResponse:
    return VisionProviderResponse(
        slide_id=slide_id,
        confidence="HIGH" if coverage == "perceived" else "LOW",
        coverage=coverage,
        provenance="png-grounded" if coverage == "perceived" else "not-covered",
        extracted_text="$4.5T spend. Building photo.",
        layout_description="Three stat callouts beside a building photo.",
        visual_elements=[
            {
                "id": "metric",
                "kind": "callout",
                "text": "$4.5T",
                "bbox": [0.12, 0.12, 0.38, 0.26],
            },
            {
                "id": "building",
                "kind": "photo",
                "label": "building photo",
                "bbox": [0.50, 0.18, 0.90, 0.80],
            },
        ],
        source_png_path="slide-01.png",
        provider_model_id="vision-fixture-v1",
    )


def test_act_emits_per_slide_artifacts_and_not_covered_for_unreadable_slide(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    png = _png(tmp_path)
    calls: list[str] = []

    def fake_perceive(path: Path, *, slide_id: str, **_: Any) -> VisionProviderResponse:
        calls.append(str(path))
        return _response(slide_id)

    monkeypatch.setattr(_act, "perceive_png", fake_perceive)
    payload = {
        "gary_slide_output": [
            {"slide_id": "slide-01", "file_path": str(png)},
            {"slide_id": "slide-02", "file_path": str(tmp_path / "missing.png")},
        ]
    }

    result = _act.act(_state(payload))
    output = json.loads(result["cache_state"]["cache_prefix"])

    assert calls == [str(png)]
    assert [row["slide_id"] for row in output["perception_artifacts"]] == [
        "slide-01",
        "slide-02",
    ]
    assert output["perception_artifacts"][0]["coverage"] == "perceived"
    assert output["perception_artifacts"][0]["reading_path"] == "top_down"
    assert output["perception_artifacts"][1]["coverage"] == "not-covered"
    assert output["perception_artifacts"][1]["reading_path"] is None


def test_reading_path_classification_failure_converts_to_vision_provider_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # P2-4a T11 (party-mode 5/5, Cluster 3a): a HIGH/perceived artifact whose
    # elements carry no positioned geometry makes the deterministic classifier
    # raise ReadingPathClassificationError (a ValueError). The vision node must
    # convert that to a NON-retryable VisionProviderError routed through the
    # error-pause contract — never let a bare ValueError escape the retry guard.
    png = _png(tmp_path)

    def fake_perceive(path: Path, *, slide_id: str, **_: Any) -> VisionProviderResponse:
        return VisionProviderResponse(
            slide_id=slide_id,
            confidence="HIGH",
            coverage="perceived",
            provenance="png-grounded",
            extracted_text="Building photo only.",
            layout_description="A single building photo.",
            visual_elements=[{"id": "building", "kind": "photo", "label": "building photo"}],
            source_png_path="slide-01.png",
            provider_model_id="vision-fixture-v1",
        )

    monkeypatch.setattr(_act, "perceive_png", fake_perceive)
    payload = {"gary_slide_output": [{"slide_id": "slide-01", "file_path": str(png)}]}

    with pytest.raises(VisionProviderError, match="reading-path classification failed"):
        _act.act(_state(payload))


@pytest.mark.parametrize(
    "error",
    [
        VisionProviderTimeout("timeout"),
        VisionProviderError("server error", status_code=500),
        VisionProviderError("busy", status_code=429),
        VisionProviderError("request timeout", status_code=408),
        VisionProviderError("connect reset", tag="vision.provider.transport"),
    ],
)
def test_transport_retry_is_one_retry_for_timeout_5xx_429_408_or_transport(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, error: VisionProviderError
) -> None:
    png = _png(tmp_path)
    calls = 0

    def flaky(path: Path, *, slide_id: str, **_: Any) -> VisionProviderResponse:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise error
        return _response(slide_id)

    monkeypatch.setattr(_act, "perceive_png", flaky)
    result = _act.act(
        _state({"gary_slide_output": [{"slide_id": "slide-01", "file_path": str(png)}]})
    )

    assert calls == 2
    output = json.loads(result["cache_state"]["cache_prefix"])
    assert output["perception_artifacts"][0]["coverage"] == "perceived"


@pytest.mark.parametrize(
    "error",
    [
        VisionProviderError("bad request", status_code=400),
        VisionProviderError("low fidelity", status_code=None),
    ],
)
def test_act_does_not_retry_4xx_or_quality_failures(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, error: Exception
) -> None:
    png = _png(tmp_path)
    calls = 0

    def failing(path: Path, *, slide_id: str, **_: Any) -> VisionProviderResponse:
        nonlocal calls
        calls += 1
        raise error

    monkeypatch.setattr(_act, "perceive_png", failing)

    with pytest.raises(type(error)):
        _act.act(
            _state(
                {"gary_slide_output": [{"slide_id": "slide-01", "file_path": str(png)}]}
            )
        )

    assert calls == 1


def test_provider_rejects_mismatched_slide_id_or_model_id(tmp_path: Path) -> None:
    png = _png(tmp_path)

    def wrong_slide_handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                **_response("wrong-slide").model_dump(),
                "provider_model_id": "vision-fixture-v1",
            },
        )

    def wrong_model_handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={**_response("slide-01").model_dump(), "provider_model_id": "wrong-model"},
        )

    with pytest.raises(VisionProviderError, match="slide_id mismatch"):
        perceive_png(
            png,
            slide_id="slide-01",
            model_id="vision-fixture-v1",
            endpoint="https://vision.test",
            client=httpx.Client(transport=httpx.MockTransport(wrong_slide_handler)),
        )

    with pytest.raises(VisionProviderError, match="model mismatch"):
        perceive_png(
            png,
            slide_id="slide-01",
            model_id="vision-fixture-v1",
            endpoint="https://vision.test",
            client=httpx.Client(transport=httpx.MockTransport(wrong_model_handler)),
        )
