"""AC-T.2 — `RetrievalAdapter` ABC contract tests.

Parametrized over every concrete adapter via the `ADAPTER_FACTORIES` list.
Each factory returns a `AdapterHarness` with everything the parametrized tests
need (adapter instance + intent + known-identity row + raw sample for filter
tests). New adapters (27-2.5 Consensus, 27-3 image, 27-4 YouTube) add a factory
here instead of reimplementing contract tests in their own modules — Amelia
MUST-FIX #1 (Story 27-2 green-light).

Atomic test splits per Amelia green-light: contract-shape / error-propagation /
provider_hints-validation tests live separately.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest
from retrieval.base import RetrievalAdapter
from retrieval.contracts import (
    AcceptanceCriteria,
    ProviderHint,
    RetrievalIntent,
    TexasRow,
)
from retrieval.fake_provider import FakeProvider, make_row
from retrieval.gamma_docs_provider import GammaDocsProvider
from retrieval.provider_directory import reset_adapter_registry
from retrieval.scite_provider import SciteProvider

# ---------------------------------------------------------------------------
# Factory harness — one per adapter under test
# ---------------------------------------------------------------------------


@dataclass
class AdapterHarness:
    """Bundle of everything a parametrized contract test needs for one adapter."""

    adapter: RetrievalAdapter
    intent: RetrievalIntent
    # A raw execute()-shaped sample the adapter can filter via apply_mechanical
    # without needing network mocking. FakeProvider: list[TexasRow]; SciteProvider:
    # list[dict] (scite paper dicts).
    raw_sample: list[Any]
    # A row whose identity_key is deterministically known ahead of time.
    known_identity_row: TexasRow
    known_identity_value: str
    # Keys we expect the adapter to honor (subset assertion — tests check membership).
    expected_honored_keys: set[str]


def _make_fake_harness() -> AdapterHarness:
    adapter = FakeProvider(
        rows_by_query={
            "initial:x": [make_row("doi:a"), make_row("doi:b")],
            "refined(1):x": [
                make_row("doi:a"),
                make_row("doi:b"),
                make_row("doi:c"),
            ],
        }
    )
    intent = RetrievalIntent(
        intent="x",
        provider_hints=[ProviderHint(provider="fake")],
        acceptance_criteria=AcceptanceCriteria(mechanical={"min_results": 1}),
    )
    raw_sample = [make_row("doi:a"), make_row("doi:b")]
    known_row = make_row("doi:xyz")
    return AdapterHarness(
        adapter=adapter,
        intent=intent,
        raw_sample=raw_sample,
        known_identity_row=known_row,
        known_identity_value="doi:xyz",
        expected_honored_keys={"min_results", "date_range", "authority_tier_min"},
    )


def _make_scite_harness() -> AdapterHarness:
    """Build a SciteProvider with no network dependency for pure-contract tests.

    Tests that call `apply_mechanical` / `normalize` / `refine` / `identity_key`
    exercise deterministic Python paths only; network-bound `execute` is covered
    separately in `tests/test_retrieval_scite_provider.py` with `responses` mocks.
    """
    adapter = SciteProvider()
    intent = RetrievalIntent(
        intent="sleep hygiene adults",
        provider_hints=[ProviderHint(provider="scite")],
        acceptance_criteria=AcceptanceCriteria(
            mechanical={"min_results": 1},
            provider_scored={"authority_tier_min": "peer-reviewed"},
        ),
    )
    raw_sample: list[Any] = [
        {
            "doi": "10.1/a",
            "title": "Paper A",
            "year": 2023,
            "publication_date": "2023-01-01",
            "venue": "Nature",
            "supporting_count": 5,
            "cited_by_count": 10,
        },
        {
            "doi": "10.1/b",
            "title": "Paper B",
            "year": 2024,
            "publication_date": "2024-06-01",
            "venue": "bioRxiv",
            "supporting_count": 2,
            "cited_by_count": 3,
        },
    ]
    # Build a row with a known DOI under provider_metadata.scite so identity_key
    # returns it deterministically.
    known_row = TexasRow(
        source_id="fallback-src",
        provider="scite",
        provider_metadata={"scite": {"doi": "10.42/known-doi"}},
    )
    return AdapterHarness(
        adapter=adapter,
        intent=intent,
        raw_sample=raw_sample,
        known_identity_row=known_row,
        known_identity_value="10.42/known-doi",
        expected_honored_keys={
            "date_range", "min_results", "exclude_ids", "license_allow",
            "authority_tier_min", "supporting_citations_min", "cited_by_count_min",
        },
    )


def _make_gamma_docs_harness() -> AdapterHarness:
    """GammaDocsProvider contract harness (Leg-E AC#2, Murat M-1 / Texas T-8).

    Pure-contract tests only exercise deterministic paths (formulate_query /
    apply_* passthroughs / identity_key / quality_delta); the network-bound
    `execute` is covered in `tests/test_retrieval_gamma_docs_provider.py` with
    per-test `responses` mocks over recorded real-page fixtures.
    """
    doc_url = "https://developers.gamma.app/reference/image-model-accepted-values.md"
    adapter = GammaDocsProvider()
    intent = RetrievalIntent(
        intent="gamma live-doc audit fetch",
        provider_hints=[
            ProviderHint(provider="gamma_docs", params={"pages": [doc_url]})
        ],
        kind="direct_ref",
        iteration_budget=1,
    )
    # execute()-shaped raw rows (per-page dicts); apply_* are declared passthroughs.
    raw_sample: list[Any] = [
        {"doc_url": doc_url, "http_status": 200, "text": "# Image models\n"},
        {
            "doc_url": "https://developers.gamma.app/changelog/readme.md",
            "http_status": 200,
            "text": "# Changelog\n",
        },
    ]
    known_row = TexasRow(
        source_id="fallback-src",
        provider="gamma_docs",
        provider_metadata={"gamma_docs": {"doc_url": doc_url}},
    )
    return AdapterHarness(
        adapter=adapter,
        intent=intent,
        raw_sample=raw_sample,
        known_identity_row=known_row,
        known_identity_value=doc_url,
        # Declared degenerate: the adapter honors no acceptance-criteria keys
        # (audit-fact vocabulary is DRIVER knowledge per Texas T-2).
        expected_honored_keys=set(),
    )


def _make_jefferson_library_harness() -> AdapterHarness:
    """JeffersonLibraryProvider contract harness (R5) — hermetic fetch_fn."""
    from retrieval.jefferson_library_provider import JeffersonLibraryProvider

    doi = "10.1056/NEJMoa2034577"

    def _fetch(query: dict) -> list[dict]:
        return [
            {
                "doi": query["doi"],
                "title": "Fixture full text",
                "pdf_bytes_len": 128,
                "pdf_sha256": "abc",
                "content_type": "application/pdf",
                "access_url": "https://example.test/pdf",
                "pdf_url": query.get("pdf_url"),
                "is_pdf": True,
                "access_path": "fixture",
            }
        ]

    adapter = JeffersonLibraryProvider(fetch_fn=_fetch)
    intent = RetrievalIntent(
        intent=doi,
        provider_hints=[
            ProviderHint(
                provider="jefferson_library",
                params={"doi": doi, "pdf_url": f"https://www.nejm.org/doi/pdf/{doi}"},
            )
        ],
        kind="direct_ref",
        iteration_budget=1,
        acceptance_criteria=AcceptanceCriteria(mechanical={"min_results": 1}),
    )
    raw_sample = [
        {
            "doi": doi,
            "title": "A",
            "pdf_bytes_len": 10,
            "pdf_sha256": "x",
            "is_pdf": True,
        },
        {
            "doi": "10.1000/other",
            "title": "B",
            "pdf_bytes_len": 10,
            "pdf_sha256": "y",
            "is_pdf": True,
        },
    ]
    known_row = TexasRow(
        source_id=doi,
        provider="jefferson_library",
        provider_metadata={"jefferson_library": {"doi": doi}},
    )
    return AdapterHarness(
        adapter=adapter,
        intent=intent,
        raw_sample=raw_sample,
        known_identity_row=known_row,
        known_identity_value=doi.lower(),
        expected_honored_keys={"min_results", "exclude_ids"},
    )


# Parametrization target — adapters land here as they ship.
ADAPTER_FACTORIES: list[tuple[str, Any]] = [
    ("fake", _make_fake_harness),
    ("scite", _make_scite_harness),
    ("gamma_docs", _make_gamma_docs_harness),
    ("jefferson_library", _make_jefferson_library_harness),
]


@pytest.fixture(params=ADAPTER_FACTORIES, ids=lambda pair: pair[0])
def harness(request: pytest.FixtureRequest) -> AdapterHarness:
    _provider_id, factory = request.param
    return factory()


# ---------------------------------------------------------------------------
# Parametrized contract tests — run once per adapter in ADAPTER_FACTORIES
# ---------------------------------------------------------------------------


def test_adapter_formulate_query_deterministic(harness: AdapterHarness) -> None:
    """Same input → byte-identical output across invocations (AC-T.2)."""
    import json as _json
    first = harness.adapter.formulate_query(harness.intent)
    for _ in range(20):
        nxt = harness.adapter.formulate_query(harness.intent)
        # Compare via sorted JSON so dict ordering differences don't flake.
        try:
            assert _json.dumps(first, sort_keys=True, default=str) == _json.dumps(
                nxt, sort_keys=True, default=str
            )
        except TypeError:
            # Plain-string query (FakeProvider) — direct equality works.
            assert first == nxt


def test_adapter_apply_mechanical_deterministic(harness: AdapterHarness) -> None:
    """Same raw + criteria → same filtered output across invocations."""
    out1 = harness.adapter.apply_mechanical(harness.raw_sample, {})
    out2 = harness.adapter.apply_mechanical(harness.raw_sample, {})
    assert len(out1) == len(out2)
    assert len(out1) == len(harness.raw_sample), (
        "empty criteria must not drop rows"
    )


def test_adapter_declare_honored_criteria_introspection(
    harness: AdapterHarness,
) -> None:
    """Adapters must enumerate the criteria keys they evaluate (AC-B.3)."""
    honored = harness.adapter.declare_honored_criteria()
    assert isinstance(honored, set)
    # Factory's expected keys must be a subset of what the adapter declares.
    missing = harness.expected_honored_keys - honored
    assert not missing, (
        f"adapter missing honored keys the factory declared: {sorted(missing)}"
    )


def test_adapter_identity_key_returns_known_string(
    harness: AdapterHarness,
) -> None:
    """Every real adapter must implement identity_key (anti-pattern #10)."""
    key = harness.adapter.identity_key(harness.known_identity_row)
    assert isinstance(key, str) and key == harness.known_identity_value


def test_adapter_quality_delta_monotonic(harness: AdapterHarness) -> None:
    """Default delta: >0 on growth, 0 on flat, <0 on shrink."""
    prev = harness.raw_sample[:1]
    more = harness.raw_sample[:]
    less: list[Any] = []
    assert harness.adapter.quality_delta(prev, more) > 0
    assert harness.adapter.quality_delta(prev, prev) == 0
    assert harness.adapter.quality_delta(prev, less) < 0


# ---------------------------------------------------------------------------
# FakeProvider-specific contract tests (not-parametrized)
# ---------------------------------------------------------------------------


@pytest.fixture
def fake_adapter() -> FakeProvider:
    return FakeProvider(
        rows_by_query={
            "initial:x": [make_row("doi:a"), make_row("doi:b")],
            "refined(1):x": [
                make_row("doi:a"),
                make_row("doi:b"),
                make_row("doi:c"),
            ],
        }
    )


@pytest.fixture
def fake_intent() -> RetrievalIntent:
    return RetrievalIntent(
        intent="x",
        provider_hints=[ProviderHint(provider="fake")],
        acceptance_criteria=AcceptanceCriteria(mechanical={"min_results": 1}),
    )


def test_fake_provider_apply_mechanical_excludes_ids(
    fake_adapter: FakeProvider,
) -> None:
    """FakeProvider honors exclude_ids — doubles as sanity check on the factory fixture."""
    results = fake_adapter.execute(
        fake_adapter.formulate_query(
            RetrievalIntent(
                intent="x", provider_hints=[ProviderHint(provider="fake")]
            )
        )
    )
    out = fake_adapter.apply_mechanical(results, {"exclude_ids": ["doi:b"]})
    assert "doi:b" not in {r.source_id for r in out}


def test_adapter_base_refine_monotonic_looseness_fake(
    fake_adapter: FakeProvider, fake_intent: RetrievalIntent
) -> None:
    """FakeProvider refine must broaden (inherited shape for new adapters)."""
    q0 = fake_adapter.formulate_query(fake_intent)
    q1 = fake_adapter.refine(q0, [], fake_intent.acceptance_criteria)
    q2 = fake_adapter.refine(q1, [], fake_intent.acceptance_criteria)
    assert q1 is not None and q1 != q0
    assert q2 is not None and q2 != q1


def test_adapter_base_normalize_returns_canonical_rows(
    fake_adapter: FakeProvider,
) -> None:
    """normalize() emits TexasRow instances with provider field set."""
    raw = [make_row("doi:a"), make_row("doi:b")]
    out = fake_adapter.normalize(raw)
    assert len(out) == 2
    assert all(r.provider == "fake" for r in out)


def test_adapter_auto_registers_in_directory() -> None:
    """AC-B.8: PROVIDER_INFO auto-registers via __init_subclass__."""
    from retrieval.provider_directory import list_providers

    # FakeProvider + SciteProvider are registered on import.
    ids = {p.id for p in list_providers()}
    assert "fake" in ids
    assert "scite" in ids
    reset_adapter_registry()
    # After reset, live registrations clear but static placeholders remain.
    ids = {p.id for p in list_providers()}
    assert "fake" not in ids
    assert "openai_chatgpt" in ids, "backlog placeholders must survive reset"
    # Scite is NOT registered after reset; the static placeholder surfaces with
    # status="ratified". PATCH-7 (2026-04-18): prior assertion accepted either
    # "ready" or "ratified" — which cannot fail meaningfully because after a
    # reset the placeholder is the only entry left, always at "ratified".
    scite_entry = next((p for p in list_providers() if p.id == "scite"), None)
    assert scite_entry is not None
    assert scite_entry.status == "ratified", (
        "After reset_adapter_registry(), the static `scite: ratified` "
        "placeholder is the sole source. If this fails with `ready`, the "
        "live adapter is registering via import-order side-effect outside "
        "the expected __init_subclass__ path."
    )
