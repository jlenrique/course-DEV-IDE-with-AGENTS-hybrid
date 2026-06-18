"""Story 33-3 DC-3 split verification."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACK_PATH = (
    PROJECT_ROOT
    / "docs"
    / "workflow"
    / "production-prompt-pack-v4.2-gen-narrated-lesson-with-video-or-animation.md"
)


def test_pack_emits_split_04_5_and_04_55_sections() -> None:
    """Assert split sections exist with canonical headings."""
    pack_text = PACK_PATH.read_text(encoding="utf-8")
    assert "## 04.5) Parent Slide Count Polling" in pack_text
    assert "## 04.55) Estimator + Run Constants Lock" in pack_text
