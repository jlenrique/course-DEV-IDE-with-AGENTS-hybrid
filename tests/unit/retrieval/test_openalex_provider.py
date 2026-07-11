"""Hermetic tests for OpenAlexProvider (TRAIL trio slice 1)."""

from __future__ import annotations

from retrieval.contracts import AcceptanceCriteria, ProviderHint, RetrievalIntent
from retrieval.openalex_provider import OpenAlexProvider
from retrieval.provider_directory import get_provider


def test_directory_surfaces_openalex_ready() -> None:
    info = get_provider("openalex")
    assert info is not None
    assert info.status == "ready"
    assert info.shape == "retrieval"
    assert "doi-metadata" in info.capabilities
    assert "oa-fulltext-links" in info.capabilities


def test_formulate_doi_and_normalize_hermetic() -> None:
    doi = "10.1038/s41586-020-2649-2"

    def fetch(query: dict) -> list[dict]:
        assert query["mode"] == "doi"
        assert query["doi"] == doi
        return [
            {
                "doi": doi,
                "openalex_id": "https://openalex.org/W3042166323",
                "source_id": doi,
                "title": "A global database of COVID-19 vaccinations",
                "date": "2021",
                "authors": ["Mathieu, Edouard"],
                "is_oa": True,
                "oa_status": "gold",
                "oa_urls": ["https://example.org/oa.pdf"],
                "cited_by_count": 100,
                "type": "article",
            }
        ]

    provider = OpenAlexProvider(fetch_fn=fetch)
    intent = RetrievalIntent(
        intent=doi,
        provider_hints=[ProviderHint(provider="openalex", params={"doi": doi})],
        kind="direct_ref",
        acceptance_criteria=AcceptanceCriteria(mechanical={"min_results": 1}),
    )
    query = provider.formulate_query(intent)
    raw = provider.execute(query)
    rows = provider.normalize(raw)
    assert len(rows) == 1
    assert rows[0].provider == "openalex"
    assert rows[0].source_id == doi
    assert provider.identity_key(rows[0]) == doi.lower()
    meta = rows[0].provider_metadata["openalex"]
    assert meta["is_oa"] is True
    assert meta["oa_urls"] == ["https://example.org/oa.pdf"]
    assert meta["known_losses"] == []
    # Amelia CLOSE MUST-FIX: OA must not imply peer_reviewed authority_tier.
    assert rows[0].authority_tier is None
    assert provider.refine(query, raw, intent.acceptance_criteria) is None


def test_search_mode_and_no_oa_known_loss() -> None:
    def fetch(query: dict) -> list[dict]:
        assert query["mode"] == "search"
        assert "vaccine" in query["search"].lower()
        return [
            {
                "doi": "10.1/no-oa",
                "source_id": "10.1/no-oa",
                "title": "Closed access fixture",
                "is_oa": False,
                "oa_status": "closed",
                "oa_urls": [],
            }
        ]

    provider = OpenAlexProvider(fetch_fn=fetch)
    intent = RetrievalIntent(
        intent="vaccine hesitancy trends",
        provider_hints=[
            ProviderHint(provider="openalex", params={"search": "vaccine hesitancy"})
        ],
        kind="query",
        acceptance_criteria=AcceptanceCriteria(mechanical={"min_results": 1}),
    )
    query = provider.formulate_query(intent)
    rows = provider.normalize(provider.execute(query))
    assert rows[0].provider_metadata["openalex"]["known_losses"] == [
        "no_oa_fulltext_link_on_record"
    ]


def test_exclude_ids_mechanical() -> None:
    provider = OpenAlexProvider(fetch_fn=lambda q: [])
    raw = [
        {"doi": "10.1/a", "source_id": "10.1/a", "title": "A"},
        {"doi": "10.1/b", "source_id": "10.1/b", "title": "B"},
    ]
    filtered = provider.apply_mechanical(raw, {"exclude_ids": ["10.1/a"]})
    assert [r["doi"] for r in filtered] == ["10.1/b"]


def test_empty_fetch_normalizes_empty() -> None:
    provider = OpenAlexProvider(fetch_fn=lambda q: [])
    assert provider.normalize([]) == []
