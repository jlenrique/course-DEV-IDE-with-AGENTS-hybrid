"""Temporary in-tree translator scaffold for Epic 34 Section 02A -> Texas wrangler boundary.

# DELETE-AT-EPIC-34-CLOSE — SCAFFOLDING

This module is BORN DEAD at Story 34-1 (integration test landing) and DIES at
Story 34-7 (translator deletion + A23/P5 anti-pattern entries + Epic 34 close).
See `_bmad-output/planning-artifacts/epics-section-02a-downstream-coherence.md`
NFR-E34-10 + AC-34-7-A/B/H for the deletion gate.

Do NOT import this module from any production runtime path EXCEPT via the
integration test at `tests/integration/test_section_02a_to_wrangler_subprocess_roundtrip.py`.
The translator's job is to bridge Section 02A's `Directive` output schema to the
Texas wrangler's currently-stricter input schema while Stories 34-2/34-3/34-4
harmonize the substrate one drift dimension at a time. Translator's
TRANSLATOR_ACTIVE_MAPPINGS shrinks monotonically across the Epic; Story 34-7
verifies it reaches frozenset() empty before deleting the file.
"""

from __future__ import annotations

from typing import Any

from app.composers.section_02a.directive_model import Directive

__epic_34_scaffolding__ = True  # AC-34-7-H grep-sweep target (post-Story-34-7 must return 0)

TRANSLATOR_ACTIVE_MAPPINGS: frozenset[str] = frozenset(
    {
        "src-id-to-ref-id",
    }
)


def translate_directive_for_wrangler(directive: Directive) -> dict[str, Any]:
    """Map Section 02A Directive to wrangler-acceptable plain dict."""

    payload = directive.model_dump(mode="json")
    translated_sources: list[dict[str, Any]] = []

    for source in payload["sources"]:
        row = dict(source)

        if "src-id-to-ref-id" in TRANSLATOR_ACTIVE_MAPPINGS:
            row["ref_id"] = row.pop("src_id")

        translated_sources.append(row)

    payload["sources"] = translated_sources
    return payload
