"""AC-9 — recorded-real gpt-5.5 responses replayed through parse->validate->classify.

These deterministic unit tests feed RECORDED-REAL gpt-5.5 responses (captured by
the AC-8 live roundtrip; provenance metadata: captured_at, model_id,
prompt_sha256, source_png, slide_id) through the production
``perceive_png`` parse seam via a STUBBED ``chat.invoke`` and then through the
reading-path classifier. The recordings live under
``tests/fixtures/vision/recordings/`` and are NEVER reachable as a production
return path — the only way they enter the code is by stubbing the LLM call in a
test (the production ``perceive_png`` always invokes the live adapter).

Murat #1: this gives a deterministic seam over real perception data without a
live call on every suite run, while the recordings' provenance block keeps them
auditable and clearly labeled as test fixtures.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from app.models.perception.perception_artifact import PerceptionArtifact
from app.specialists.vision import provider as provider_mod
from app.specialists.vision.payload_contract import VisionProviderResponse
from app.specialists.vision.provider import perceive_png
from scripts.utilities.reading_path_classifier import (
    READING_PATH_PATTERNS,
    with_classified_reading_path,
)

RECORDINGS_DIR = (
    Path(__file__).resolve().parents[2] / "fixtures" / "vision" / "recordings"
)
SLIDE_IDS = [f"slide-{n:02d}" for n in range(1, 7)]


def _load_recording(slide_id: str) -> dict[str, Any]:
    return json.loads((RECORDINGS_DIR / f"{slide_id}.json").read_text(encoding="utf-8"))


class _StubChat:
    """Returns the recorded raw response content; satisfies bind(...).invoke(...)."""

    def __init__(self, content: str) -> None:
        self._content = content

    def bind(self, **_: Any) -> _StubChat:
        return self

    def invoke(self, _messages: Any) -> Any:
        class _Resp:
            content = self._content

        return _Resp()


def _stub_factory(content: str) -> Any:
    class _Handle:
        chat = _StubChat(content)

    def _factory(*_a: Any, **_k: Any) -> _Handle:
        return _Handle()

    return _factory


def test_recordings_exist_for_all_six_slides() -> None:
    for slide_id in SLIDE_IDS:
        path = RECORDINGS_DIR / f"{slide_id}.json"
        assert path.is_file(), f"missing recorded-real fixture {path}"
        rec = _load_recording(slide_id)
        prov = rec["_provenance"]
        assert prov["model_id"] == "gpt-5.5"
        assert prov["slide_id"] == slide_id
        assert prov["captured_at"]
        assert len(prov["prompt_sha256"]) == 64
        assert prov["source_png"].endswith(f"{slide_id}.png")


@pytest.mark.parametrize("slide_id", SLIDE_IDS)
def test_recorded_real_response_replays_through_parse_validate_classify(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, slide_id: str
) -> None:
    """Replay the recorded response through the production parse seam + classifier."""
    rec = _load_recording(slide_id)
    raw_content = json.dumps(rec["response"])

    # A real PNG must exist for perceive_png's input-missing guard; bytes are
    # irrelevant because chat.invoke is stubbed.
    png = tmp_path / f"{slide_id}.png"
    png.write_bytes(b"\x89PNG\r\n\x1a\nstub")

    monkeypatch.setattr(provider_mod, "make_chat_model", _stub_factory(raw_content))

    response = perceive_png(png, slide_id=slide_id, model_id="gpt-5.5")
    assert isinstance(response, VisionProviderResponse)
    assert response.slide_id == slide_id

    artifact = PerceptionArtifact.model_validate(response.model_dump())
    if artifact.coverage == "perceived" and artifact.confidence == "HIGH":
        classified = with_classified_reading_path(artifact)
        assert classified.reading_path in READING_PATH_PATTERNS


def test_slide01_recorded_real_carries_economic_anchors() -> None:
    """The captured slide-01 perception carries the real economic anchors."""
    rec = _load_recording("slide-01")
    response = VisionProviderResponse.model_validate(rec["response"])
    blob = (
        response.extracted_text
        + " "
        + response.slide_title
        + " "
        + " ".join(str(b) for b in response.text_blocks)
        + " "
        + " ".join(str(e.get("text", "")) for e in response.visual_elements)
    ).lower()
    # S6: accept equivalent surface forms so the assertion is robust to a
    # re-capture that writes "3×"/"$4.5 trillion" while staying non-vacuous.
    for variants in (("$4.5t", "4.5 trillion"), ("74%",), ("3x", "3×")):
        assert any(v in blob for v in variants), (
            f"recorded slide-01 missing any of anchor variants {variants!r}"
        )
    assert response.confidence == "HIGH"
    for element in response.visual_elements:
        bbox = element.get("bbox")
        assert isinstance(bbox, (list, tuple)) and len(bbox) == 4
        x1, y1, x2, y2 = (float(v) for v in bbox)
        assert 0.0 <= x1 <= x2 <= 1.0
        assert 0.0 <= y1 <= y2 <= 1.0
