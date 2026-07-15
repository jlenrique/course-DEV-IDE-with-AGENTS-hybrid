"""Shared 39.1 test substrate — live-shape fixtures only (protocol plank 2).

Every shape derives from the two real runs:

- ``runs/a940c5eb…`` — the real 1-row Ask-A pool + the live-authored Tejal
  Part-2 skeleton (already frozen under
  ``tests/fixtures/deep_dive_enrichment_37_2b/``; reused via that helper).
- ``runs/8b275e5b…`` — the real W1 generic-research packet rows whose
  title-mangled headwords are the J-F3 regression shape (frozen under
  ``tests/fixtures/glossary_39_1/``).

Mutants are mutated COPIES of those frozen shapes, never hand-invented
structures.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from app.marcus.lesson_plan.ask_a_enrichment import AskAKnowledgeEntryV1
from app.marcus.lesson_plan.glossary_projection import (
    glossary_projection_from_contribution,
    glossary_reference_lines,
    render_glossary_projection_markdown,
)

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "glossary_39_1"
CITE_003_FIXTURE = FIXTURE_DIR / "cite-003-ask-a-entry.v1.json"
W1_PACKET_ROWS_FIXTURE = FIXTURE_DIR / "w1-packet-rows-8b275e5b.json"
FIXTURE_MANIFEST = FIXTURE_DIR / "fixture-manifest.json"

_GLOSSARY_HEADING = "## Research Glossary"


def _validate_entry(payload: dict[str, Any]) -> AskAKnowledgeEntryV1:
    return AskAKnowledgeEntryV1.model_validate_json(
        json.dumps(payload, separators=(",", ":"), ensure_ascii=False), strict=True
    )


def cite_003_fixture_payload() -> dict[str, Any]:
    """The full M2 fixture file (``derivation`` declaration + ``entry``)."""
    return json.loads(CITE_003_FIXTURE.read_text(encoding="utf-8"))


def cite_003_entry() -> AskAKnowledgeEntryV1:
    """The J-F3 ``cite-003`` mislabel row (cross-sectional carrying T1_systematic)."""
    return _validate_entry(cite_003_fixture_payload()["entry"])


def w1_packet_fixture_payload() -> dict[str, Any]:
    return json.loads(W1_PACKET_ROWS_FIXTURE.read_text(encoding="utf-8"))


def w1_packet_entries() -> tuple[AskAKnowledgeEntryV1, ...]:
    """The five real 8b275e5b W1 rows (association fields synthesized, declared)."""
    return tuple(
        _validate_entry(row) for row in w1_packet_fixture_payload()["entries"]
    )


def mangled_headwords() -> tuple[str, ...]:
    """The REAL title-derived mangled headwords from ``u01@1.md`` (J-F3)."""
    return tuple(w1_packet_fixture_payload()["mangled_headwords"])


def conforming_glossary_body(contribution: Any) -> str:
    """The 39.1 term-keyed section body for a loaded 07W.3 contribution."""
    return render_glossary_projection_markdown(
        glossary_projection_from_contribution(contribution)
    )


def glossary_only_reference_lines(
    contribution: Any, *, exclude_citation_ids: tuple[str, ...] = ()
) -> tuple[str, ...]:
    return glossary_reference_lines(
        glossary_projection_from_contribution(contribution),
        exclude_citation_ids=exclude_citation_ids,
    )


def swap_glossary_section(markdown: str, contribution: Any) -> str:
    """Replace the fixture MD's (pre-39.1) glossary section with the conforming
    term-keyed render for ``contribution`` — the fixture file itself stays
    frozen (digest-pinned); the swap happens on the in-memory copy."""
    body = conforming_glossary_body(contribution)
    pattern = re.compile(
        rf"(\n{re.escape(_GLOSSARY_HEADING)}\n)(.*?)(?=\n## )", re.DOTALL
    )
    replaced, count = pattern.subn(lambda m: f"{m.group(1)}\n{body}\n", markdown)
    if count != 1:
        raise AssertionError(
            "fixture markdown must carry exactly one Research Glossary section"
        )
    return replaced
