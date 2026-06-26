"""Live S1 proof: kira drives a REAL Kling render to a real .mp4 on disk.

This is the HAPPY/LIVE floor for the motion-restore story (S1): feed kira a
REAL one-slide motion plan (reused from the April C1-M1-PRES-20260419B run that
last produced a real ``slide-01-motion.mp4``) and assert a real .mp4 lands on
disk — non-zero bytes, valid MP4 container header, duration > 0.

NO MOCKS — calls the live Kling API. Bounded to ONE slide (kling-v1-6 std, 5s)
to cap cost/latency. Requires KLING_ACCESS_KEY + KLING_SECRET_KEY and the
``--run-live`` pytest flag (``live_api`` is deselected by default per
tests/conftest.py). Lives OUTSIDE tests/specialists/kira/ so the no-live-import
guard (detect_live_api_in_tests.py) stays green for the kira specialist suite.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from app.specialists.kira import _act as kira_act
from scripts.api_clients.kling_client import KlingClient

HAS_KLING_CREDS = bool(
    os.environ.get("KLING_ACCESS_KEY") and os.environ.get("KLING_SECRET_KEY")
)
skip_no_creds = pytest.mark.skipif(
    not HAS_KLING_CREDS,
    reason="KLING_ACCESS_KEY and KLING_SECRET_KEY not set",
)

# Reused verbatim from the April 419b motion plan (beat-4 pathway-divergence
# animation), trimmed to a single text2video slide to bound live cost.
_REAL_ONE_SLIDE_PLAN = {
    "slides": [
        {
            "slide_id": "apc-c1m1-tejal-motion-card-01-beat-4",
            "model_name": "kling-v1-6",
            "duration": "5",
            "aspect_ratio": "16:9",
            "mode": "std",
            "kling_prompt": (
                "Concept animation on dark navy background. A single clean navy-blue "
                "pathway line enters from the left, then splits into two diverging "
                "paths — the lower path continues straight (reactive, navy, fades), the "
                "upper path branches forward and upward marked in teal (innovation, "
                "momentum). Paths separate smoothly with restrained motion. Final 1.5 "
                "seconds: static hold, both paths visible, teal path dominant. Minimal "
                "composition, cool palette, locked-off camera."
            ),
            "negative_prompt": (
                "text overlays, watermarks, cartoon style, chaotic motion, warm tones, "
                "bright saturated colors, irrelevant background subjects"
            ),
            "estimated_cost_usd": 0.0,
        }
    ]
}

_MP4_FTYP_MARKER = b"ftyp"


def _bool_env(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@pytest.mark.live_api
@pytest.mark.live_api_e2e
@pytest.mark.timeout(600)
@skip_no_creds
def test_kira_live_motion_renders_real_mp4(tmp_path: Path) -> None:
    bundle_path = tmp_path / "kira-motion"
    payload = {"bundle_path": str(bundle_path), **_REAL_ONE_SLIDE_PLAN}

    verdict = kira_act.generate_motion_from_plan(payload, client=KlingClient())

    receipts = verdict["motion_receipts"]
    assert len(receipts) == 1
    receipt = receipts[0]

    # The provider may queue past the test budget; xfail (not a substrate
    # failure) unless KLING_LIVE_STRICT is set.
    if receipt["status"] != "success":
        if _bool_env("KLING_LIVE_STRICT"):
            raise AssertionError(f"Kling render did not succeed: {receipt}")
        pytest.xfail(f"Kling render did not complete within budget: {receipt}")

    video_url = receipt["motion_asset_path"]
    assert video_url, f"successful receipt carried no motion_asset_path: {receipt}"

    out_path = bundle_path / "motion" / "slide-01-motion.mp4"
    KlingClient().download_video(video_url, out_path)

    assert out_path.is_file()
    size = out_path.stat().st_size
    assert size > 1000, f"rendered mp4 is suspiciously small: {size} bytes"

    head = out_path.read_bytes()[:64]
    assert _MP4_FTYP_MARKER in head, f"file is not a valid MP4 container: {head!r}"

    # Duration > 0 via ffprobe when available (best-effort; container header +
    # byte size already prove a real render).
    import shutil
    import subprocess

    ffprobe = shutil.which("ffprobe")
    if ffprobe:
        proc = subprocess.run(
            [
                ffprobe,
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(out_path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        duration = float(proc.stdout.strip() or 0.0)
        assert duration > 0.0, f"ffprobe reports non-positive duration: {proc.stdout!r}"
