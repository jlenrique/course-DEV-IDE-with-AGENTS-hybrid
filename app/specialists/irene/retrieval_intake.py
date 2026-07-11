"""Irene-facing re-export of foundations R6 research intake (thin).

Specialists must not import ``app.marcus.orchestrator`` (M3). Pass-2 / Irene
authoring imports from here or ``app.specialists._shared.research_intake``.
"""

from app.specialists._shared.research_intake import (
    CONVERGENCE_NARRATION_PATTERNS,
    FabricatedCitationError,
    ResearchIntakePacket,
    RetrievalProvenanceItem,
    assert_no_fabricated_citations,
    attribution_phrase_for_entry,
    build_retrieval_provenance,
    consume_research_entries,
    resolvable_source_ids,
)

__all__ = [
    "CONVERGENCE_NARRATION_PATTERNS",
    "FabricatedCitationError",
    "ResearchIntakePacket",
    "RetrievalProvenanceItem",
    "assert_no_fabricated_citations",
    "attribution_phrase_for_entry",
    "build_retrieval_provenance",
    "consume_research_entries",
    "resolvable_source_ids",
]
