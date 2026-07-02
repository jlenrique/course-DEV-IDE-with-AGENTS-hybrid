"""AC-8 — live gpt-5.5 multimodal roundtrip over the 6 real corpus PNGs.

@pytest.mark.llm_live: auto-skipped when OPENAI_API_KEY is unset or holds the
Slab-1 placeholder sentinel (tests/conftest.py Pass 2). Non-vacuous assertions
on slide-01 (the real `slide-1-the-economic-structural-reality` frame); the
raw VisionProviderResponse for every slide is captured to disk on the live run
(Mary #6) for operator inspection and as the seed for the AC-9 recorded-real
replay fixtures.

Per the rapid-dev / weed-clearing posture and Amelia's "first-run-stands"
discipline: ONE retry max and only via the existing retryable provider
classes — NEVER retry on an assertion failure. A real perception miss is
REPORTED, not tuned away.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from vision_capture_support import normalize_capture_response_paths

from app.models.perception.perception_artifact import PerceptionArtifact
from app.specialists.vision.provider import (
    PERCEPTION_SYSTEM_MESSAGE,
    VisionProviderError,
    VisionProviderTimeout,
    _perception_prompt,
    perceive_png,
)
from scripts.utilities.reading_path_classifier import (
    READING_PATH_PATTERNS,
    ReadingPathClassificationError,
    with_classified_reading_path,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
VISUALS_DIR = REPO_ROOT / "runs" / "compositor" / "assembly-bundle" / "visuals"
CAPTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "vision" / "recordings"
SLIDE_IDS = [f"slide-{n:02d}" for n in range(1, 7)]


def _perceive_with_one_retry(png: Path, *, slide_id: str):
    """Perceive once; retry at most ONCE and only on a retryable provider class."""
    try:
        return perceive_png(png, slide_id=slide_id, model_id="gpt-5.5")
    except VisionProviderTimeout:
        return perceive_png(png, slide_id=slide_id, model_id="gpt-5.5")
    except VisionProviderError as exc:
        if exc.status_code in {408, 429} or (
            exc.status_code is not None and exc.status_code >= 500
        ):
            return perceive_png(png, slide_id=slide_id, model_id="gpt-5.5")
        raise


@pytest.mark.llm_live
def test_live_gpt55_perceives_six_real_pngs_and_captures_recordings() -> None:
    """Perceive all 6 real PNGs live; assert non-vacuous on slide-01; capture raw."""
    for slide_id in SLIDE_IDS:
        assert (VISUALS_DIR / f"{slide_id}.png").is_file(), f"missing {slide_id}.png"

    CAPTURE_DIR.mkdir(parents=True, exist_ok=True)
    captured_at = datetime.now(UTC).isoformat()
    responses: dict[str, object] = {}

    for slide_id in SLIDE_IDS:
        png = VISUALS_DIR / f"{slide_id}.png"
        response = _perceive_with_one_retry(png, slide_id=slide_id)
        # Capture raw provider response with provenance metadata (Mary #6 / AC-9 seed).
        prompt = PERCEPTION_SYSTEM_MESSAGE + "\n" + _perception_prompt(slide_id)
        record = {
            "_provenance": {
                "captured_at": captured_at,
                "model_id": "gpt-5.5",
                "source_png": str(png.relative_to(REPO_ROOT)).replace("\\", "/"),
                "slide_id": slide_id,
                "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                "harness": "tests/specialists/vision/test_vision_live_roundtrip.py",
            },
            # Capture-layer portability (carried-findings D-C2): the runtime
            # provider sets source_png_path absolute (correct at runtime);
            # the RECORDED copy is normalized to repo-relative posix so the
            # committed fixture stays portable. Out-of-repo png -> FAIL LOUD.
            "response": normalize_capture_response_paths(
                response.model_dump(), repo_root=REPO_ROOT
            ),
        }
        (CAPTURE_DIR / f"{slide_id}.json").write_text(
            json.dumps(record, indent=2, sort_keys=True), encoding="utf-8"
        )
        responses[slide_id] = response

        # Reading-path classification must succeed (or raise the unclassifiable
        # contract) — exercise the production parse->validate->classify seam.
        artifact = PerceptionArtifact.model_validate(response.model_dump())
        if artifact.coverage == "perceived" and artifact.confidence == "HIGH":
            try:
                classified = with_classified_reading_path(artifact)
            except ReadingPathClassificationError as exc:
                pytest.fail(
                    f"{slide_id}: HIGH/perceived but unclassifiable reading_path: {exc}"
                )
            assert classified.reading_path in READING_PATH_PATTERNS

    # ---- Non-vacuous assertions on slide-01 (the economic-reality frame) ----
    s1 = responses["slide-01"]
    text = (s1.extracted_text + " " + s1.slide_title + " "
            + " ".join(str(b) for b in s1.text_blocks)
            + " " + " ".join(str(e.get("text", "")) for e in s1.visual_elements)).lower()

    # S6: accept equivalent surface forms of each real figure so a CORRECT
    # perception that writes "3×" (U+00D7) or "$4.5 trillion" does not false-
    # fail. Each anchor remains non-vacuous — the real figure must be present.
    anchor_variants: tuple[tuple[str, ...], ...] = (
        ("$4.5t", "4.5 trillion"),
        ("74%",),
        ("3x", "3×"),
    )
    for variants in anchor_variants:
        assert any(v in text for v in variants), (
            f"slide-01 perceived text missing any of anchor variants {variants!r}; "
            f"got text={text!r}"
        )

    # Element-count band: a multi-stat economic slide should yield several regions.
    assert 2 <= len(s1.visual_elements) <= 30, (
        f"slide-01 element count {len(s1.visual_elements)} outside [2,30] band"
    )

    # Every bbox normalized in [0,1] with x1<x2<=1 and y1<y2<=1 (width/height fit).
    for element in s1.visual_elements:
        bbox = element.get("bbox")
        assert isinstance(bbox, (list, tuple)) and len(bbox) == 4, (
            f"slide-01 element {element.get('id')} bbox malformed: {bbox!r}"
        )
        x1, y1, x2, y2 = (float(v) for v in bbox)
        assert 0.0 <= x1 <= 1.0 and 0.0 <= y1 <= 1.0
        assert 0.0 <= x2 <= 1.0 and 0.0 <= y2 <= 1.0
        assert x1 <= x2 and y1 <= y2, f"bbox not top-left/bottom-right ordered: {bbox!r}"

    assert s1.confidence == "HIGH", f"slide-01 confidence={s1.confidence}, expected HIGH"

    s1_artifact = with_classified_reading_path(
        PerceptionArtifact.model_validate(s1.model_dump())
    )
    assert s1_artifact.reading_path in READING_PATH_PATTERNS
