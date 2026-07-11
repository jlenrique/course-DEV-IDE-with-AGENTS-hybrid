"""Hermetic tests for JeffersonLibraryProvider (R5)."""

from __future__ import annotations

from retrieval.contracts import AcceptanceCriteria, ProviderHint, RetrievalIntent
from retrieval.jefferson_library_provider import (
    JeffersonLibraryProvider,
    jefferson_session_preflight,
)
from retrieval.provider_directory import get_provider


def test_directory_surfaces_jefferson_ready() -> None:
    info = get_provider("jefferson_library")
    assert info is not None
    assert info.status == "ready"
    assert info.shape == "retrieval"


def test_formulate_normalize_identity_hermetic() -> None:
    doi = "10.1056/NEJMoa2034577"

    def fetch(query: dict) -> list[dict]:
        assert query["doi"] == doi
        return [
            {
                "doi": doi,
                "title": "NEJM fixture",
                "pdf_bytes_len": 771183,
                "pdf_sha256": "deadbeef",
                "content_type": "application/pdf",
                "access_url": f"https://www.nejm.org/doi/pdf/{doi}",
                "pdf_url": f"https://www.nejm.org/doi/pdf/{doi}",
                "is_pdf": True,
                "access_path": "fixture",
            }
        ]

    provider = JeffersonLibraryProvider(fetch_fn=fetch)
    intent = RetrievalIntent(
        intent=doi,
        provider_hints=[ProviderHint(provider="jefferson_library", params={"doi": doi})],
        kind="direct_ref",
        acceptance_criteria=AcceptanceCriteria(mechanical={"min_results": 1}),
    )
    query = provider.formulate_query(intent)
    raw = provider.execute(query)
    rows = provider.normalize(raw)
    assert len(rows) == 1
    assert rows[0].provider == "jefferson_library"
    assert rows[0].source_id == doi
    assert provider.identity_key(rows[0]) == doi.lower()
    assert rows[0].provider_metadata["jefferson_library"]["is_pdf"] is True
    assert provider.refine(query, raw, intent.acceptance_criteria) is None


def test_exclude_ids_mechanical() -> None:
    provider = JeffersonLibraryProvider(fetch_fn=lambda q: [])
    raw = [
        {"doi": "10.1/a", "title": "A"},
        {"doi": "10.1/b", "title": "B"},
    ]
    filtered = provider.apply_mechanical(raw, {"exclude_ids": ["10.1/a"]})
    assert [r["doi"] for r in filtered] == ["10.1/b"]


def test_preflight_shape() -> None:
    report = jefferson_session_preflight()
    assert "chrome_user_data_exists" in report
    assert "ready" in report
    assert "live_armed" in report
