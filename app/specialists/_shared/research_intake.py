"""Research retrieval intake — Agentic Research Foundations R6 (thin).

Consumes wrangled ``research_entries`` (R4 credibility + R3 triangulation) for
Irene Pass-2 / narration without fabricating citations. Lives under
``app.specialists._shared`` so both Marcus wiring and Irene can import it
(M3 forbids specialists → ``app.marcus.orchestrator``).

Full Sprint ``irene-retrieval-intake`` story remains the thicker contract;
this module is the foundations thin borrow that closes the fabricate-cite
hole and exposes a durable intake packet on the run contribution.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

IntakeMode = Literal["corroborate", "embellish", "gap_fill", "mixed", "none"]

CONVERGENCE_NARRATION_PATTERNS: dict[str, str] = {
    "dual_provider": (
        "Corroborated by multiple independent sources, with support from "
        "peer-reviewed citation context and synthesis evidence."
    ),
    "scite_only": "According to scite.ai citation-context analysis.",
    "consensus_only": "Per Consensus research synthesis.",
    "jefferson_only": "Per institutional full-text access (Jefferson library).",
    "single_provider": "According to available retrieval evidence.",
    "none": "According to available retrieval evidence.",
}


class FabricatedCitationError(ValueError):
    """Raised when narration cites a source_id absent from wrangled research."""


class RetrievalProvenanceItem(BaseModel):
    """Additive segment provenance (contract-compatible shape)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    source_id: str = Field(min_length=1)
    providers: list[str] = Field(min_length=1)
    citation_id: str | None = None
    source_ref: str | None = None
    evidence_hierarchy_tier: str | None = None
    peer_reviewed: bool | None = None
    triangulation_status: str | None = None
    reliability_score: float | None = None
    attribution_phrase: str = ""


class ResearchIntakePacket(BaseModel):
    """Durable intake packet attached to the research_wiring contribution."""

    model_config = ConfigDict(extra="forbid")

    cluster_id: str = Field(min_length=1)
    intake_mode: IntakeMode = "corroborate"
    evidence_bolster_active: bool = False
    entries_consumed: int = Field(ge=0)
    retrieval_provenance: list[RetrievalProvenanceItem] = Field(default_factory=list)
    known_losses: list[str] = Field(default_factory=list)
    attribution_phrases: list[str] = Field(default_factory=list)


def _providers_for_entry(entry: dict[str, Any]) -> list[str]:
    prov = entry.get("provider_provenance")
    if isinstance(prov, list) and prov:
        return [str(p) for p in prov if str(p).strip()]
    provider = str(entry.get("provider") or "").strip()
    return [provider] if provider else []


def attribution_phrase_for_entry(entry: dict[str, Any]) -> str:
    """Deterministic convergence → narration phrase (lookup, not inference)."""
    status = str(entry.get("triangulation_status") or "none")
    providers = {p.lower() for p in _providers_for_entry(entry)}
    if status == "dual_provider" or len(providers) >= 2:
        return CONVERGENCE_NARRATION_PATTERNS["dual_provider"]
    if providers == {"scite"}:
        return CONVERGENCE_NARRATION_PATTERNS["scite_only"]
    if providers == {"consensus"}:
        return CONVERGENCE_NARRATION_PATTERNS["consensus_only"]
    if providers == {"jefferson_library"}:
        return CONVERGENCE_NARRATION_PATTERNS["jefferson_only"]
    if status == "single_provider":
        return CONVERGENCE_NARRATION_PATTERNS["single_provider"]
    return CONVERGENCE_NARRATION_PATTERNS["none"]


def build_retrieval_provenance(
    entries: list[dict[str, Any]],
) -> list[RetrievalProvenanceItem]:
    """Lift research_entries into additive retrieval_provenance items."""
    items: list[RetrievalProvenanceItem] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        source_id = str(entry.get("source_id") or "").strip()
        providers = _providers_for_entry(entry)
        if not source_id or not providers:
            continue
        items.append(
            RetrievalProvenanceItem(
                source_id=source_id,
                providers=providers,
                citation_id=entry.get("citation_id"),
                source_ref=entry.get("source_ref"),
                evidence_hierarchy_tier=entry.get("evidence_hierarchy_tier"),
                peer_reviewed=entry.get("peer_reviewed"),
                triangulation_status=entry.get("triangulation_status"),
                reliability_score=entry.get("reliability_score"),
                attribution_phrase=attribution_phrase_for_entry(entry),
            )
        )
    return items


def resolvable_source_ids(entries: list[dict[str, Any]]) -> set[str]:
    """Source ids that narration may cite without fabricating."""
    out: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        sid = str(entry.get("source_id") or "").strip()
        if sid:
            out.add(sid)
            out.add(sid.lower())
        ref = str(entry.get("source_ref") or "").strip()
        if ref:
            out.add(ref)
    return out


def assert_no_fabricated_citations(
    cited_source_ids: list[str],
    entries: list[dict[str, Any]],
) -> None:
    """Fail-loud RED when a cite is not in the wrangled research set."""
    allowed = resolvable_source_ids(entries)
    fabricated = [
        cid
        for cid in cited_source_ids
        if str(cid).strip() and str(cid).strip() not in allowed
        and str(cid).strip().lower() not in allowed
    ]
    if fabricated:
        raise FabricatedCitationError(
            "Irene retrieval intake refuses fabricated citations: "
            f"{fabricated!r} not present in wrangled research_entries"
        )


def consume_research_entries(
    entries: list[dict[str, Any]],
    *,
    cluster_id: str,
    intake_mode: IntakeMode = "corroborate",
    evidence_bolster_active: bool = False,
) -> ResearchIntakePacket:
    """Build an intake packet from wrangled rows; empty → known_losses, no crash."""
    clean = [e for e in entries if isinstance(e, dict)]
    provenance = build_retrieval_provenance(clean)
    known_losses: list[str] = []
    if not provenance:
        known_losses.append(f"retrieval_empty_for_cluster_{cluster_id}")
    phrases = [p.attribution_phrase for p in provenance if p.attribution_phrase]
    # Dedupe phrases while preserving order
    seen: set[str] = set()
    unique_phrases: list[str] = []
    for phrase in phrases:
        if phrase not in seen:
            seen.add(phrase)
            unique_phrases.append(phrase)
    return ResearchIntakePacket(
        cluster_id=cluster_id,
        intake_mode=intake_mode,
        evidence_bolster_active=evidence_bolster_active,
        entries_consumed=len(provenance),
        retrieval_provenance=provenance,
        known_losses=known_losses,
        attribution_phrases=unique_phrases,
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
