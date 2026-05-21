from __future__ import annotations

from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
SOURCE_ROOT = REPO_ROOT / "tests" / "fixtures" / "specialists" / "compositor" / "source"


def compositor_payload(tmp_path: Path) -> dict[str, Any]:
    return {
        "bundle_path": str(tmp_path / "bundle"),
        "run_id": "fixture-run",
        "gary_slide_output": [
            {"slide_id": "slide-01", "file_path": str(SOURCE_ROOT / "slide-01.png")},
            {"slide_id": "slide-02", "file_path": str(SOURCE_ROOT / "slide-02.png")},
        ],
        "motion_receipts": [
            {"slide_id": "slide-01", "motion_asset_path": str(SOURCE_ROOT / "slide-01.mp4")}
        ],
        "audio_paths": [str(SOURCE_ROOT / "narration-01.mp3")],
        "audio_bed_paths": [str(SOURCE_ROOT / "bed-01.mp3")],
    }
