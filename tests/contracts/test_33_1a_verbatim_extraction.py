"""Contract: extracted section prose stays verbatim to v4.2 source."""

from __future__ import annotations

import re
from pathlib import Path

from scripts.generators.v42.manifest import load_generator_manifest

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "state/config/pipeline-manifest.yaml"
SECTIONS = ROOT / "scripts/generators/v42/templates/sections"
SOURCE = ROOT / (
    "docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md"
)


def _strip_jinja(value: str) -> str:
    value = re.sub(r"\{\{.*?\}\}", "", value, flags=re.S)
    value = re.sub(r"\{\%.*?\%\}", "", value, flags=re.S)
    return value.strip()


# Sections whose templates substitute VALUES inline (not just boundary
# markup), so stripped template prose can never equal rendered prose:
#   04.55 — original 33-1a exclusion;
#   02A   — workflow-policy substitutions ({{ poll_floor_minutes }} etc.,
#           Slab 7c parameterization; renderer/L1 story 2026-06-12).
# Byte fidelity for these is guaranteed by the STRONGER whole-pack
# regeneration-determinism leg (L1 Check 9) landed with the renderer fix.
_VALUE_SUBSTITUTING_SECTIONS = {"04.55", "02A"}


def test_existing_sections_match_source_pack_byte_identical() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    gm = load_generator_manifest(MANIFEST)
    checked = 0
    for step in gm.steps:
        if step.id in _VALUE_SUBSTITUTING_SECTIONS:
            continue
        text = (SECTIONS / Path(step.template_name).name).read_text(encoding="utf-8")
        cleaned = _strip_jinja(text)
        assert cleaned in source, f"Template prose drift for {step.id}"
        checked += 1
    assert checked >= 30  # the boundary-markup majority stays under the ratchet
