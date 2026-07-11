"""Hermetic tests for R4 evidence-hierarchy credibility surfacing."""

from __future__ import annotations

from types import SimpleNamespace

from app.marcus.orchestrator.research_citation import (
    apply_triangulation_to_entries,
    assert_credibility_fields,
    mint_cited_entry,
)
from app.marcus.orchestrator.research_credibility import classify_evidence_hierarchy


def test_classify_systematic_from_title() -> None:
    row = SimpleNamespace(
        title="A systematic review of worked examples",
        body="",
        provider="scite",
        source_id="10.1000/sys",
        authority_tier=None,
        provider_metadata={},
    )
    tier, peer = classify_evidence_hierarchy(row)
    assert tier == "T1_systematic" and peer is True


def test_classify_preprint() -> None:
    row = SimpleNamespace(
        title="Worked examples preprint",
        body="",
        provider="scite",
        source_id="10.1000/pre",
        authority_tier=None,
        provider_metadata={"scite": {"venue": "bioRxiv"}},
    )
    tier, peer = classify_evidence_hierarchy(row)
    assert tier == "T5_preprint" and peer is False


def test_mint_cited_entry_carries_credibility_fields() -> None:
    row = SimpleNamespace(
        title="Effects of worked examples on transfer",
        body="abstract",
        provider="scite",
        source_id="10.1080/01443410.2023.2273762",
        authority_tier="peer_reviewed",
        provider_metadata={"scite": {"venue": "Educational Psychology", "doi": "10.1080/01443410.2023.2273762"}},
    )
    entry = mint_cited_entry(row, citation_index=1)
    assert_credibility_fields(entry)
    assert entry.evidence_hierarchy_tier == "T4_peer_other"
    assert entry.peer_reviewed is True
    assert entry.provider_provenance == ["scite"]
    assert entry.triangulation_status == "none"


def test_apply_triangulation_overlays_dual_provider() -> None:
    row = SimpleNamespace(
        title="The effect of worked examples on learning solution steps and knowledge transfer",
        body="",
        provider="consensus",
        source_id="8fba3910b73754f0b192c1ba93562d5a",
        authority_tier=None,
        provider_metadata={"consensus": {"venue": "Educational Psychology"}},
    )
    entry = mint_cited_entry(row, citation_index=1)

    cluster = SimpleNamespace(
        triangulation_status="dual_provider",
        reliability_score=0.85,
        rows_by_provider={
            "consensus": row,
            "scite": SimpleNamespace(
                source_id="10.1080/01443410.2023.2273762",
                title=row.title,
                provider="scite",
            ),
        },
    )
    receipt = SimpleNamespace(triangulated_rows=[cluster])
    updated = apply_triangulation_to_entries([entry], receipt)
    assert updated[0].triangulation_status == "dual_provider"
    assert updated[0].reliability_score == 0.85
    assert set(updated[0].provider_provenance) == {"consensus", "scite"}
    assert_credibility_fields(updated[0])
