"""Contract: extracted section prose stays verbatim to v4.2 source."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from scripts.generators.v42.manifest import load_generator_manifest

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "state/config/pipeline-manifest.yaml"
SECTIONS = ROOT / "scripts/generators/v42/templates/sections"
SOURCE = ROOT / (
    "docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md"
)
GENERATED = ROOT / (
    "docs/workflow/production-prompt-pack-v4.2-gen-narrated-lesson-with-video-or-animation.md"
)


@dataclass(frozen=True)
class SectionVerbatimExclusion:
    section_id: str
    reason: str
    substitute_invariant: str


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
# Formal rule (P2-2 T11 Option A, party-ratified 2026-06-20):
# verbatim extraction applies to frozen-origin sections from the v4.2 mapping
# axis. Net-new `-gen` sections and value-substituting sections cannot be byte
# identical to the frozen source; each exclusion must be explicitly enrolled in
# a substitute invariant. This closed allowlist is governance-controlled; do
# not replace it with a regex that silently admits future 07X/08X sections.
CHECK9_INVARIANT = "L1 Check-9 regeneration-determinism"
_VERBATIM_EXCLUDED_SECTIONS = {
    "04.55": SectionVerbatimExclusion(
        section_id="04.55",
        reason="value-substituting",
        substitute_invariant=CHECK9_INVARIANT,
    ),
    "02A": SectionVerbatimExclusion(
        section_id="02A",
        reason="value-substituting",
        substitute_invariant=CHECK9_INVARIANT,
    ),
    "07G": SectionVerbatimExclusion(
        section_id="07G",
        reason="net-new-prose",
        substitute_invariant=CHECK9_INVARIANT,
    ),
}


def test_existing_sections_match_source_pack_byte_identical() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    gm = load_generator_manifest(MANIFEST)
    checked = 0
    for step in gm.steps:
        if step.id in _VERBATIM_EXCLUDED_SECTIONS:
            continue
        text = (SECTIONS / Path(step.template_name).name).read_text(encoding="utf-8")
        cleaned = _strip_jinja(text)
        assert cleaned in source, f"Template prose drift for {step.id}"
        checked += 1
    assert checked >= 30  # the boundary-markup majority stays under the ratchet


def test_verbatim_exclusions_are_closed_and_check9_governed() -> None:
    gm = load_generator_manifest(MANIFEST)
    determinism_sections = {step.id for step in gm.steps}

    assert set(_VERBATIM_EXCLUDED_SECTIONS) == {"04.55", "02A", "07G"}
    for section_id, exclusion in _VERBATIM_EXCLUDED_SECTIONS.items():
        assert exclusion.section_id == section_id
        assert exclusion.reason in {"value-substituting", "net-new-prose"}
        assert exclusion.substitute_invariant == CHECK9_INVARIANT
        assert section_id in determinism_sections


def test_07g_generated_section_is_present_non_empty_and_ordered() -> None:
    text = GENERATED.read_text(encoding="utf-8")
    headings = [
        (match.group("id"), match.start())
        for match in re.finditer(r"^## (?P<id>[0-9A-Z.]+)\)", text, flags=re.M)
    ]
    positions = {section_id: index for index, (section_id, _) in enumerate(headings)}

    assert positions["07F"] < positions["07G"] < positions["08"]

    start = headings[positions["07G"]][1]
    end = headings[positions["08"]][1]
    body = text[start:end].strip()

    assert body.startswith("## 07G) PNG-Grounded Vision Perception")
    assert len(body.splitlines()) > 3
