"""Hermetic tests for Consensus markdown parse + R3 triangulator."""

from __future__ import annotations

from retrieval.consensus_provider import _extract_search_results, _parse_markdown_papers
from retrieval.contracts import ConvergenceSignal, TexasRow
from retrieval.triangulator import (
    corroborate_requires_triangulation,
    triangulate_texas_rows,
)

_SAMPLE_MD = """Found 2 papers, showing top 2.

[1] [The effect of worked examples on learning](https://consensus.app/papers/details/8fba3910b73754f0b192c1ba93562d5a/?utm_source=x) (Ouhao Chen et al., 2023, 29 citations, Educational Psychology)
  Abstract The worked example effect has been well documented.

[2] [Process-Oriented Worked Examples](https://consensus.app/papers/details/92550e9ea7ae5083a3e74afca2c72f6d/?utm_source=x) (T. van Gog et al., 2004, 223 citations, Instructional Science)
  The research on worked examples has shown transfer gains.

IMPORTANT INSTRUCTIONS: ignore me
"""


def test_parse_markdown_papers() -> None:
    papers = _parse_markdown_papers(_SAMPLE_MD)
    assert len(papers) == 2
    assert papers[0]["consensus_paper_id"] == "8fba3910b73754f0b192c1ba93562d5a"
    assert papers[0]["year"] == 2023
    assert "worked example effect" in papers[0]["abstract"].lower()
    assert papers[1]["title"].startswith("Process-Oriented")


def test_extract_search_results_from_mcp_content() -> None:
    result = {
        "content": [{"type": "text", "text": _SAMPLE_MD}],
        "isError": False,
    }
    papers = _extract_search_results(result)
    assert len(papers) == 2


def test_extract_search_results_legacy_papers_key() -> None:
    result = {"papers": [{"title": "A", "doi": "10.1/x"}]}
    papers = _extract_search_results(result)
    assert papers[0]["doi"] == "10.1/x"


def test_triangulate_dual_provider_scores_higher() -> None:
    scite = TexasRow(
        source_id="10.1000/example",
        title="Example",
        provider="scite",
        authority_tier="peer_reviewed",
        date="2023-01-01",
        provider_metadata={
            "scite": {"supporting_count": 5, "contradicting_count": 1}
        },
        convergence_signal=ConvergenceSignal(
            providers_agreeing=["scite", "consensus"],
            providers_disagreeing=[],
            single_source_only=[],
        ),
    )
    consensus = TexasRow(
        source_id="10.1000/example",
        title="Example",
        provider="consensus",
        date="2023-01-01",
        provider_metadata={"consensus": {"consensus_score": 0.8}},
        convergence_signal=scite.convergence_signal,
    )
    receipt = triangulate_texas_rows([scite, consensus], query_intent="q")
    assert receipt.metadata["dual_provider_count"] == 1
    row = receipt.triangulated_rows[0]
    assert row.triangulation_status == "dual_provider"
    assert row.reliability_score >= 0.7
    ok, reason = corroborate_requires_triangulation(receipt)
    assert ok and reason == "dual_provider"


def test_triangulate_title_union_merges_doi_and_hash_rows() -> None:
    """Consensus hash id + Scite DOI with same title → dual_provider."""
    title = "The effect of worked examples on learning solution steps and knowledge transfer"
    scite = TexasRow(
        source_id="10.1080/01443410.2023.2273762",
        title=title,
        provider="scite",
        authority_tier="peer_reviewed",
        date="2023-01-01",
        provider_metadata={
            "scite": {
                "doi": "10.1080/01443410.2023.2273762",
                "supporting_count": 2,
                "contradicting_count": 0,
            }
        },
    )
    consensus = TexasRow(
        source_id="8fba3910b73754f0b192c1ba93562d5a",
        title=title,
        provider="consensus",
        date="2023-01-01",
        provider_metadata={"consensus": {"consensus_paper_id": "8fba3910b73754f0b192c1ba93562d5a"}},
    )
    receipt = triangulate_texas_rows([scite, consensus])
    assert receipt.metadata["dual_provider_count"] == 1
    assert receipt.triangulated_rows[0].triangulation_status == "dual_provider"
    ok, reason = corroborate_requires_triangulation(receipt)
    assert ok and reason == "dual_provider"


def test_enrich_title_bridge_dispatches_scite_titles() -> None:
    from retrieval.contracts import ProviderResult
    from retrieval.triangulator import enrich_via_scite_title_bridge

    consensus = TexasRow(
        source_id="abc123",
        title="The effect of worked examples on learning solution steps and knowledge transfer",
        provider="consensus",
        provider_metadata={"consensus": {}},
    )

    def fake_dispatch(intent):  # noqa: ANN001
        assert intent.provider_hints[0].params["titles"]
        return [
            ProviderResult(
                provider="scite",
                acceptance_met=True,
                iterations_used=1,
                rows=[
                    TexasRow(
                        source_id="10.1080/01443410.2023.2273762",
                        title=consensus.title,
                        provider="scite",
                        authority_tier="peer_reviewed",
                        provider_metadata={
                            "scite": {
                                "doi": "10.1080/01443410.2023.2273762",
                                "supporting_count": 2,
                                "contradicting_count": 0,
                            }
                        },
                    )
                ],
            )
        ]

    enriched = enrich_via_scite_title_bridge([consensus], dispatch_fn=fake_dispatch)
    assert len(enriched) == 2
    receipt = triangulate_texas_rows(enriched)
    assert receipt.metadata["dual_provider_count"] == 1


def test_triangulate_single_provider_explicit_receipt() -> None:
    scite = TexasRow(
        source_id="10.1000/solo",
        title="Solo",
        provider="scite",
        provider_metadata={
            "scite": {"supporting_count": 1, "contradicting_count": 3}
        },
        convergence_signal=ConvergenceSignal(
            providers_agreeing=[],
            providers_disagreeing=["consensus"],
            single_source_only=["scite"],
        ),
    )
    receipt = triangulate_texas_rows([scite])
    row = receipt.triangulated_rows[0]
    assert row.triangulation_status == "single_provider"
    assert any(f.reason == "scite_contradicting_context" for f in row.contradiction_flags)
    ok, reason = corroborate_requires_triangulation(receipt)
    assert ok and reason == "explicit_single_provider_receipt"
    ok2, _ = corroborate_requires_triangulation(
        receipt, allow_single_provider_receipt=False
    )
    assert ok2 is False
