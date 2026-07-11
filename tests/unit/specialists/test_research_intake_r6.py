"""Hermetic tests for R6 research retrieval intake (no fabricate-cite)."""

from __future__ import annotations

import pytest

from app.specialists._shared.research_intake import (
    FabricatedCitationError,
    assert_no_fabricated_citations,
    consume_research_entries,
)


def _entry(**overrides: object) -> dict:
    base = {
        "citation_id": "cite-001",
        "source_ref": "retrieval:scite:10.1000/x",
        "provider": "scite",
        "source_id": "10.1000/x",
        "title": "Example",
        "evidence_hierarchy_tier": "T4_peer_other",
        "peer_reviewed": True,
        "provider_provenance": ["scite", "consensus"],
        "triangulation_status": "dual_provider",
        "reliability_score": 0.8,
    }
    base.update(overrides)
    return base


def test_consume_builds_provenance_and_dual_phrase() -> None:
    packet = consume_research_entries(
        [_entry()],
        cluster_id="c1",
        evidence_bolster_active=True,
    )
    assert packet.entries_consumed == 1
    assert packet.known_losses == []
    assert packet.retrieval_provenance[0].source_id == "10.1000/x"
    assert "multiple independent sources" in packet.attribution_phrases[0].lower()


def test_empty_entries_record_known_loss_not_crash() -> None:
    packet = consume_research_entries([], cluster_id="empty-cluster")
    assert packet.entries_consumed == 0
    assert packet.known_losses == ["retrieval_empty_for_cluster_empty-cluster"]


def test_fabricated_citation_path_is_red() -> None:
    entries = [_entry()]
    assert_no_fabricated_citations(["10.1000/x"], entries)
    with pytest.raises(FabricatedCitationError, match="fabricated"):
        assert_no_fabricated_citations(["10.9999/FAKE"], entries)


def test_scite_only_phrase() -> None:
    packet = consume_research_entries(
        [
            _entry(
                provider_provenance=["scite"],
                triangulation_status="single_provider",
            )
        ],
        cluster_id="c2",
    )
    assert "scite.ai" in packet.attribution_phrases[0].lower()
