"""Texas pass-0 — universal-md corpus shaping + live citation resolution (P2).

Turns the frozen P1 ``G0EnrichmentResult`` typed components into a clean,
provenance-anchored **universal-md** corpus and resolves citations LIVE
(``resolved`` | ``failed`` | ``ungrounded`` — never fabricated). Lossless; no
paraphrase at this layer.

Authority: ``_bmad-output/planning-artifacts/p2-texas-pass0-design-strawman-2026-06-26.md``
§"R2 Phase A — SYNTHESIZED DESIGN" (DD1-DD8 + the Irene required-shapes list).

DEPENDENCY DIRECTION (DD2): this package is Texas-side and MUST NOT import
``app.marcus`` (the dependency arrow is ``app/marcus -> skills/bmad-agent-texas``
ONLY). It therefore:
  - returns PLAIN DICTS for citation resolutions (the ``app/marcus`` wiring maps
    them into the ``CitationResolution`` pydantic model);
  - receives the canonical markdown normalizer (``_normalize_for_groundedness``)
    as an INJECTED callable rather than importing it from ``app.marcus``;
  - reuses only the sibling Texas ``retrieval`` package (``normalize`` /
    ``dispatcher`` / ``contracts``).
"""

from __future__ import annotations

from .citation_resolver import (
    DOI_RE,
    NORMALIZATION_VERSION,
    RESOLVER_PROVIDER,
    extract_doi,
    resolve_citations,
)
from .universal_markdown_preamble import emit_front_matter, parse_front_matter
from .universal_md import (
    build_component_record,
    content_fingerprint,
    is_excerpt_grounded,
)

__all__ = [
    "DOI_RE",
    "NORMALIZATION_VERSION",
    "RESOLVER_PROVIDER",
    "build_component_record",
    "content_fingerprint",
    "emit_front_matter",
    "extract_doi",
    "is_excerpt_grounded",
    "parse_front_matter",
    "resolve_citations",
]
