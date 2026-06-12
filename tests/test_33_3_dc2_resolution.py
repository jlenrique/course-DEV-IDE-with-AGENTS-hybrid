"""Story 33-3 DC-2 resolution checks."""

from __future__ import annotations

from pathlib import Path

from app.manifest.loader import load as load_graph_manifest
from app.manifest.schema import is_orchestration_only
from scripts.utilities.check_pipeline_manifest_lockstep import _parse_pack_sections
from scripts.utilities.pipeline_manifest import load_manifest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACK_PATH = (
    PROJECT_ROOT
    / "docs"
    / "workflow"
    / "production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md"
)
MANIFEST_PATH = PROJECT_ROOT / "state" / "config" / "pipeline-manifest.yaml"


def test_pack_section_sequence_matches_manifest_order() -> None:
    """Ensure regenerated pack follows manifest ordering, including 04A.

    Renderer/L1 story 2026-06-12: the comparison roster is the RENDERABLE
    steps — the four Slab-7a orchestration nodes are runtime-only and never
    pack prose (shared predicate; same exclusion the L1 check applies).
    """
    graph = load_graph_manifest(MANIFEST_PATH)
    orchestration_ids = {
        node.id.upper() for node in graph.nodes if is_orchestration_only(node)
    }
    manifest = load_manifest(MANIFEST_PATH)
    manifest_ids = [
        step.id.upper()
        for step in manifest.steps
        if step.id.upper() not in orchestration_ids
    ]
    manifest_set = set(manifest_ids)
    pack_ids = [
        step["id"]
        for step in _parse_pack_sections(PACK_PATH)
        if step["id"] in manifest_set
    ]

    assert pack_ids == manifest_ids
    assert pack_ids.index("04A") > pack_ids.index("04")
    assert pack_ids.index("04A") < pack_ids.index("04.5")
