"""Story 33-3 DC-1 resolution checks."""

from __future__ import annotations

from pathlib import Path

from scripts.utilities.pipeline_manifest import load_manifest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACK_PATH = (
    PROJECT_ROOT
    / "docs"
    / "workflow"
    / "production-prompt-pack-v4.2-gen-narrated-lesson-with-video-or-animation.md"
)
MANIFEST_PATH = PROJECT_ROOT / "state" / "config" / "pipeline-manifest.yaml"


def test_g25_gate_visible_in_regenerated_pack() -> None:
    """Verify G2.5 appears in both manifest and regenerated pack."""
    manifest = load_manifest(MANIFEST_PATH)
    step_75 = next(step for step in manifest.steps if step.id == "7.5")

    assert step_75.gate is True
    assert step_75.gate_code == "G2.5"

    pack_text = PACK_PATH.read_text(encoding="utf-8")
    assert "## 7.5) Cluster Coherence G2.5 Gate" in pack_text
