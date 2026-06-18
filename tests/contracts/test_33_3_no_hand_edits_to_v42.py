"""Contract tests for story 33-3 regeneration integrity."""

from __future__ import annotations

from pathlib import Path

from scripts.generators.v42.render import render_pack

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = PROJECT_ROOT / "state" / "config" / "pipeline-manifest.yaml"
PACK_PATH = (
    PROJECT_ROOT
    / "docs"
    / "workflow"
    / "production-prompt-pack-v4.2-gen-narrated-lesson-with-video-or-animation.md"
)


def _normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n")


def test_v42_pack_commit_is_regeneration_output(tmp_path: Path) -> None:
    """Ensure committed pack equals generator output for current manifest."""
    rendered_path = tmp_path / "rendered-pack.md"
    render_pack(MANIFEST_PATH, rendered_path)

    committed = _normalize_newlines(PACK_PATH.read_text(encoding="utf-8"))
    rendered = _normalize_newlines(rendered_path.read_text(encoding="utf-8"))
    assert committed == rendered
