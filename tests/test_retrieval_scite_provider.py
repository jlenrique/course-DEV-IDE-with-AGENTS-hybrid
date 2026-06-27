"""AC-T.1 / T.3 / T.10 / T.11 — SciteProvider unit tests (Story 27-2).

Atomicity-split per Murat MUST-FIX #2: 11 AC-T.1 atoms + 2 AC-T.3 refinement
atoms + 1 AC-T.10 module-prefix exception contract + 1 AC-T.11 no-stateful-mock
anti-pattern guard.

Each test that hits the MCP transport uses `responses.RequestsMock()` **per-test**
(anti-pattern #8 guard — no module-level leaks). Synthetic JSON fixtures under
`tests/fixtures/retrieval/scite/` are the single source of truth for response
shapes; provenance in the directory's README.md.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
import responses
from retrieval import (
    AcceptanceCriteria,
    MCPAuthError,
    ProviderHint,
    RetrievalIntent,
)
from retrieval.scite_provider import (
    SCITE_AUTHORITY_TIERS,
    SCITE_MCP_URL,
    SCITE_REFINEMENT_KEY_ORDER,
    SciteProvider,
)

from tests._helpers.mcp_fixtures import jsonrpc_response

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "retrieval" / "scite"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_fixture(name: str) -> dict[str, Any]:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def _scite_creds(monkeypatch: pytest.MonkeyPatch) -> None:
    """Every test gets valid env creds so `MCPClient._build_auth_header` succeeds."""
    monkeypatch.setenv("SCITE_USER_NAME", "test-user")
    monkeypatch.setenv("SCITE_PASSWORD", "test-pass")


def _intent_search(
    *, params: dict[str, Any] | None = None, **criteria: Any
) -> RetrievalIntent:
    return RetrievalIntent(
        intent="sleep hygiene adults",
        provider_hints=[ProviderHint(provider="scite", params=params or {})],
        acceptance_criteria=AcceptanceCriteria(
            mechanical=criteria.get("mechanical", {}),
            provider_scored=criteria.get("provider_scored", {}),
        ),
    )


def _intent_doi(doi: str) -> RetrievalIntent:
    return RetrievalIntent(
        intent=doi,
        provider_hints=[
            ProviderHint(provider="scite", params={"mode": "paper", "doi": doi})
        ],
        kind="direct_ref",
    )


# ---------------------------------------------------------------------------
# AC-T.1 formulate_query atoms (3)
# ---------------------------------------------------------------------------


def test_scite_formulate_query_deterministic() -> None:
    """Same intent → byte-identical query dict across 100 invocations."""
    provider = SciteProvider()
    intent = _intent_search(mechanical={"min_results": 5})
    serialized = {
        json.dumps(provider.formulate_query(intent), sort_keys=True)
        for _ in range(100)
    }
    assert len(serialized) == 1, (
        "SciteProvider.formulate_query must be byte-deterministic across "
        "invocations with the same intent"
    )


def test_scite_formulate_query_search_mode() -> None:
    """Topical intent + no explicit mode hint → search-shaped query dict."""
    provider = SciteProvider()
    intent = _intent_search(
        mechanical={"date_range": ["2020-01-01", "2026-12-31"], "min_results": 5},
        provider_scored={"authority_tier_min": "peer-reviewed"},
    )
    query = provider.formulate_query(intent)
    assert query["mode"] == "search"
    assert query["query"] == "sleep hygiene adults"
    assert query["max_results"] == 5
    assert query["filters"].get("date_range") == ["2020-01-01", "2026-12-31"]


def test_scite_formulate_query_doi_mode() -> None:
    """Direct-DOI intent + `{mode: "paper"}` hint → paper-shaped query dict."""
    provider = SciteProvider()
    intent = _intent_doi("10.1038/s41586-021-00001")
    query = provider.formulate_query(intent)
    assert query["mode"] == "paper"
    assert query["doi"] == "10.1038/s41586-021-00001"


# ---------------------------------------------------------------------------
# AC-T.1 execute atoms (3)
# ---------------------------------------------------------------------------


def test_scite_execute_calls_correct_tool_name() -> None:
    """MCPClient is invoked via JSON-RPC `tools/call` with the search tool name."""
    provider = SciteProvider()
    intent = _intent_search(mechanical={"min_results": 1})
    query = provider.formulate_query(intent)
    with responses.RequestsMock() as rsps:
        rsps.post(SCITE_MCP_URL, json=jsonrpc_response(result=_load_fixture("search_happy.json")))
        provider.execute(query)
        assert len(rsps.calls) == 1
        body = json.loads(rsps.calls[0].request.body)
        assert body["method"] == "tools/call"
        # Verified at first live run (2026-06-25): the live tool is `search_literature`.
        assert body["params"]["name"] == "search_literature"


def test_scite_execute_maps_args_to_live_tool_shape() -> None:
    """`execute` maps the formulated query to the live `search_literature` args
    (`term`/`limit`, + date_from/date_to from a date_range filter)."""
    provider = SciteProvider()
    intent = _intent_search(
        mechanical={"date_range": ["2020-01-01", "2026-12-31"], "min_results": 3}
    )
    query = provider.formulate_query(intent)
    with responses.RequestsMock() as rsps:
        rsps.post(SCITE_MCP_URL, json=jsonrpc_response(result=_load_fixture("search_happy.json")))
        provider.execute(query)
        body = json.loads(rsps.calls[0].request.body)
        args = body["params"]["arguments"]
        assert args["term"] == query["query"]
        assert args["limit"] == query["max_results"]
        assert args["date_from"] == "2020-01-01"
        assert args["date_to"] == "2026-12-31"


def test_scite_execute_dois_hint_routes_search_literature_with_dois_no_term() -> None:
    """FIX 2 / DD8: a `dois` provider-hint dereferences via `search_literature`
    with args `{dois:[...], limit:...}` and NO `term` key (a DOI dereference,
    not a topical term search). Offline: the MCP HTTP layer is faked by
    `responses`, the network is never touched."""
    provider = SciteProvider()
    intent = _intent_search(
        params={"mode": "search", "dois": ["10.1001/jama.2019.13978"], "max_results": 1}
    )
    query = provider.formulate_query(intent)
    # formulate_query carries the dois hint through onto the query dict.
    assert query.get("dois") == ["10.1001/jama.2019.13978"]
    with responses.RequestsMock() as rsps:
        rsps.post(
            SCITE_MCP_URL,
            json=jsonrpc_response(result=_load_fixture("search_happy.json")),
        )
        provider.execute(query)
        body = json.loads(rsps.calls[0].request.body)
        assert body["method"] == "tools/call"
        assert body["params"]["name"] == "search_literature"
        args = body["params"]["arguments"]
        assert args["dois"] == ["10.1001/jama.2019.13978"]
        assert args["limit"] == 1
        assert "term" not in args


def test_scite_execute_returns_parsed_list() -> None:
    """`execute` returns a list of paper dicts with the expected scite fields."""
    provider = SciteProvider()
    intent = _intent_search(mechanical={"min_results": 1})
    query = provider.formulate_query(intent)
    with responses.RequestsMock() as rsps:
        rsps.post(SCITE_MCP_URL, json=jsonrpc_response(result=_load_fixture("search_happy.json")))
        results = provider.execute(query)
    assert isinstance(results, list)
    assert len(results) == 3
    first = results[0]
    for key in ("doi", "title", "supporting_count", "cited_by_count"):
        assert key in first, f"expected key {key!r} in scite paper dict"


# ---------------------------------------------------------------------------
# AC-T.1 execute error path (1)
# ---------------------------------------------------------------------------


def test_scite_execute_and_normalize_real_mcp_shape() -> None:
    """Live shape (verified 2026-06-25): tools/call returns the payload wrapped in
    `content[0].text` under `hits`, with `journal`/`tally`/`authorName` fields."""
    provider = SciteProvider()
    intent = _intent_search(mechanical={"min_results": 1})
    query = provider.formulate_query(intent)
    real_payload = {
        "hits": [
            {
                "doi": "10.1111/1468-0009.12077",
                "title": "The Dynamics of Community Health Care Consolidation",
                "authors": [{"authorName": "Jon B. Christianson"}],
                "journal": "milbank quarterly",
                "abstract": "Physician practice consolidation ...",
                "year": 2014,
                "isOa": True,
                "tally": {"total": 23, "supporting": 1, "contrasting": 0, "mentioning": 22},
            }
        ]
    }
    mcp_result = {"content": [{"type": "text", "text": json.dumps(real_payload)}]}
    with responses.RequestsMock() as rsps:
        rsps.post(SCITE_MCP_URL, json=jsonrpc_response(result=mcp_result))
        hits = provider.execute(query)
    assert len(hits) == 1 and hits[0]["doi"] == "10.1111/1468-0009.12077"
    rows = provider.normalize(hits)
    assert len(rows) == 1
    row = rows[0]
    assert provider.identity_key(row) == "10.1111/1468-0009.12077"
    assert row.authors == ["Jon B. Christianson"]
    meta = row.provider_metadata["scite"]
    assert meta["supporting_count"] == 1 and meta["cited_by_count"] == 23
    assert meta["venue"] == "milbank quarterly"  # mapped from `journal`


def test_scite_execute_auth_error_propagates() -> None:
    """401 response surfaces as `MCPAuthError` (re-raised unchanged by adapter)."""
    provider = SciteProvider()
    intent = _intent_search(mechanical={"min_results": 1})
    query = provider.formulate_query(intent)
    with responses.RequestsMock() as rsps:
        rsps.post(SCITE_MCP_URL, status=401, body="unauthorized")
        with pytest.raises(MCPAuthError):
            provider.execute(query)


# ---------------------------------------------------------------------------
# AC-T.1 normalize atoms (3) + paywall degradation (1)
# ---------------------------------------------------------------------------


def test_scite_normalize_extracts_doi_to_identity() -> None:
    """DOI flows into provider_metadata.scite.doi AND is returned by identity_key."""
    provider = SciteProvider()
    fixture = _load_fixture("search_happy.json")
    rows = provider.normalize(fixture["papers"])
    assert len(rows) == 3
    first = rows[0]
    assert first.provider_metadata["scite"]["doi"] == "10.1038/s41586-021-00001"
    assert provider.identity_key(first) == "10.1038/s41586-021-00001"


def test_scite_normalize_truncates_citation_contexts_to_3_per_classification() -> None:
    """10/10/10 contexts truncate to 3/3/3 in provider_metadata."""
    provider = SciteProvider()
    fixture = _load_fixture("citation_context_happy.json")
    # Build a single paper dict with the full 30 contexts embedded.
    paper = {
        "doi": "10.1038/context-test",
        "scite_paper_id": "sp-context",
        "title": "Context truncation test",
        "authors": [],
        "abstract": "abs",
        "full_text_available": False,
        "citation_contexts": fixture["contexts"],
    }
    rows = provider.normalize([paper])
    snippets = rows[0].provider_metadata["scite"]["citation_context_snippets"]
    buckets: dict[str, int] = {}
    for snip in snippets:
        buckets[snip["classification"]] = buckets.get(snip["classification"], 0) + 1
    assert buckets == {"supporting": 3, "contradicting": 3, "mentioning": 3}


def test_scite_normalize_derives_authority_tier_via_lookup_table() -> None:
    """'Nature Medicine' → peer-reviewed via SCITE_AUTHORITY_TIERS lookup."""
    provider = SciteProvider()
    fixture = _load_fixture("search_happy.json")
    rows = provider.normalize(fixture["papers"])
    nature_row = next(r for r in rows if "Nature Medicine" in str(
        r.provider_metadata["scite"]["venue"]))
    assert nature_row.authority_tier == "peer-reviewed"
    assert SCITE_AUTHORITY_TIERS["nature medicine"] == "peer-reviewed"


def test_scite_normalize_paywall_degrades_to_abstract() -> None:
    """full_text_available=False → body=abstract; known_losses sentinel populated."""
    provider = SciteProvider()
    fixture = _load_fixture("paper_metadata_paywalled.json")
    rows = provider.normalize([fixture])
    row = rows[0]
    assert "abstract is accessible" in row.body
    assert row.provider_metadata["scite"]["known_losses"] == [
        "full_text_paywalled"
    ]


# ---------------------------------------------------------------------------
# AC-T.3 refinement atoms (2)
# ---------------------------------------------------------------------------


def test_scite_refine_monotonic_looseness() -> None:
    """Each refine() call drops exactly one filter from the scite-specific order."""
    provider = SciteProvider()
    criteria = AcceptanceCriteria(
        mechanical={"date_range": ["2020-01-01", "2026-12-31"]},
        provider_scored={
            "authority_tier_min": "peer-reviewed",
            "supporting_citations_min": 5,
            "cited_by_count_min": 10,
        },
    )
    query = {
        "mode": "search",
        "query": "x",
        "max_results": 5,
        "filters": {
            "supporting_citations_min": 5,
            "authority_tier_min": "peer-reviewed",
            "date_range": ["2020-01-01", "2026-12-31"],
            "cited_by_count_min": 10,
        },
    }
    prev_filter_count = len(query["filters"])
    current = query
    seen: set[frozenset[str]] = {frozenset(query["filters"])}
    for _ in range(len(SCITE_REFINEMENT_KEY_ORDER)):
        nxt = provider.refine(current, [], criteria)
        if nxt is None:
            break
        assert len(nxt["filters"]) < prev_filter_count, (
            "refine must drop at least one filter per iteration (monotonic looseness)"
        )
        prev_filter_count = len(nxt["filters"])
        assert frozenset(nxt["filters"]) not in seen, (
            "refine produced a filter-set that was already visited"
        )
        seen.add(frozenset(nxt["filters"]))
        current = nxt


def test_scite_refine_drops_keys_in_declared_priority_order() -> None:
    """PATCH-1 regression: refine() must drop keys in SCITE_REFINEMENT_KEY_ORDER.

    Prior bug: `drop_filters_in_order` was called with the cumulative iteration
    counter against a filtered (shrinking) key_order, which caused call 2 to
    drop `keys[1]` (date_range) instead of `keys[0]` (authority_tier_min) —
    skipping authority_tier_min entirely. This atom asserts the exact drop
    order so the bug cannot recur silently.
    """
    provider = SciteProvider()
    criteria = AcceptanceCriteria(
        mechanical={"date_range": ["2020-01-01", "2026-12-31"]},
        provider_scored={
            "authority_tier_min": "peer-reviewed",
            "supporting_citations_min": 5,
            "cited_by_count_min": 10,
        },
    )
    current: dict[str, Any] = {
        "mode": "search",
        "query": "x",
        "max_results": 5,
        "filters": {
            "supporting_citations_min": 5,
            "authority_tier_min": "peer-reviewed",
            "date_range": ["2020-01-01", "2026-12-31"],
            "cited_by_count_min": 10,
        },
    }
    # Expected drop order matches SCITE_REFINEMENT_KEY_ORDER exactly.
    expected_drops = list(SCITE_REFINEMENT_KEY_ORDER)
    for expected_dropped in expected_drops:
        filters_before = set(current["filters"])
        nxt = provider.refine(current, [], criteria)
        assert nxt is not None, (
            f"refine returned None before {expected_dropped!r} was dropped"
        )
        filters_after = set(nxt["filters"])
        actually_dropped = filters_before - filters_after
        assert actually_dropped == {expected_dropped}, (
            f"expected to drop {expected_dropped!r}, actually dropped "
            f"{sorted(actually_dropped)}. SCITE_REFINEMENT_KEY_ORDER = "
            f"{list(SCITE_REFINEMENT_KEY_ORDER)}"
        )
        current = nxt
    # After all priority-list keys dropped, next call returns None.
    assert provider.refine(current, [], criteria) is None


def test_scite_refine_returns_none_for_non_search_modes() -> None:
    """PATCH-14: refine() must return None when previous_query.mode != 'search'.

    Paper / citation_contexts modes are DOI-direct lookups; loosening would not
    improve results. This atom exercises the `if previous_query.get("mode") !=
    "search": return None` guard at scite_provider.py:494.
    """
    provider = SciteProvider()
    criteria = AcceptanceCriteria(mechanical={}, provider_scored={})
    for mode in ("paper", "citation_contexts"):
        query = {"mode": mode, "doi": "10.1/test"}
        assert provider.refine(query, [], criteria) is None, (
            f"refine() must return None for mode={mode!r}"
        )


def test_scite_identity_key_falls_back_to_scite_paper_id_when_doi_missing() -> None:
    """PATCH-12: 3-tier identity_key fallback — scite_paper_id second tier.

    Exercises the branch at scite_provider.py:540-542 where `doi` is empty
    but `scite_paper_id` is present. Prior tests only covered the DOI-primary
    happy path.
    """
    from retrieval import TexasRow

    provider = SciteProvider()
    row = TexasRow(
        source_id="fallback-src",
        provider="scite",
        provider_metadata={
            "scite": {"doi": "", "scite_paper_id": "sp-preprint-001"}
        },
    )
    assert provider.identity_key(row) == "sp-preprint-001"


def test_scite_identity_key_falls_back_to_source_id_when_doi_and_paper_id_missing() -> None:
    """PATCH-12: 3-tier identity_key fallback — source_id final fallback."""
    from retrieval import TexasRow

    provider = SciteProvider()
    row = TexasRow(
        source_id="emergency-fallback-id",
        provider="scite",
        provider_metadata={"scite": {"doi": None, "scite_paper_id": None}},
    )
    assert provider.identity_key(row) == "emergency-fallback-id"


def test_scite_identity_key_raises_when_all_three_tiers_empty() -> None:
    """PATCH-12: identity_key must raise NotImplementedError when every
    fallback tier is empty — the dispatcher's cross_validate=True preflight
    catches this at dispatch-time per 27-0 anti-pattern #10.
    """
    from retrieval import TexasRow

    provider = SciteProvider()
    # source_id is required non-empty by the TexasRow pydantic model; to
    # simulate "all three empty" we need a row whose source_id is present
    # but whose provider_metadata.scite lacks both DOI and paper_id, AND
    # whose source_id is falsy (which pydantic rejects). Emulate the raise
    # path by constructing a row with empty provider_metadata and empty
    # source_id via model_construct to bypass validation.
    row = TexasRow.model_construct(
        source_id="",
        provider="scite",
        provider_metadata={"scite": {}},
    )
    with pytest.raises(NotImplementedError, match="no DOI"):
        provider.identity_key(row)


def test_scite_apply_mechanical_exclude_ids_matches_scite_paper_id() -> None:
    """PATCH-13: exclude_ids can reference either DOI OR scite_paper_id.

    The branch at scite_provider.py:363-367 checks both; prior tests only
    covered the DOI path. This atom exercises the scite_paper_id match.
    """
    provider = SciteProvider()
    raw = [
        {"doi": "10.1/a", "scite_paper_id": "sp-001", "title": "A"},
        {"doi": "10.1/b", "scite_paper_id": "sp-002", "title": "B"},
        {"doi": "10.1/c", "scite_paper_id": "sp-003", "title": "C"},
    ]
    # Exclude by scite_paper_id, not DOI.
    filtered = provider.apply_mechanical(raw, {"exclude_ids": ["sp-002"]})
    assert {r["doi"] for r in filtered} == {"10.1/a", "10.1/c"}


def test_scite_refine_exhausts_and_returns_none() -> None:
    """Once all SCITE_REFINEMENT_KEY_ORDER keys are dropped, refine returns None."""
    provider = SciteProvider()
    criteria = AcceptanceCriteria(
        mechanical={"date_range": ["2020-01-01", "2026-12-31"]},
        provider_scored={
            "authority_tier_min": "peer-reviewed",
            "supporting_citations_min": 5,
            "cited_by_count_min": 10,
        },
    )
    current: dict[str, Any] = {
        "mode": "search",
        "query": "x",
        "max_results": 5,
        "filters": {
            "supporting_citations_min": 5,
            "authority_tier_min": "peer-reviewed",
            "date_range": ["2020-01-01", "2026-12-31"],
            "cited_by_count_min": 10,
        },
    }
    for _ in range(len(SCITE_REFINEMENT_KEY_ORDER)):
        nxt = provider.refine(current, [], criteria)
        if nxt is None:
            break
        current = nxt
    # One more call must return None.
    assert provider.refine(current, [], criteria) is None


# ---------------------------------------------------------------------------
# AC-T.10 — module-prefix exception contract (Winston MUST-FIX #2)
# ---------------------------------------------------------------------------


def test_scite_provider_exceptions_never_leak_transport_types() -> None:
    """Every raised exception's module must start with `retrieval.` — no requests.*."""
    provider = SciteProvider()
    intent = _intent_search(mechanical={"min_results": 1})
    query = provider.formulate_query(intent)
    # Exercise the four HTTP error paths in sequence; each gets its own RequestsMock.
    for status in (401, 429, 500, 400):
        with responses.RequestsMock() as rsps:
            rsps.post(SCITE_MCP_URL, status=status, body="err")
            raised: BaseException | None = None
            try:
                provider.execute(query)
            except Exception as exc:  # noqa: BLE001 — contract boundary check
                raised = exc
            assert raised is not None, f"expected exception for HTTP {status}"
            module = type(raised).__module__
            assert module.startswith("retrieval."), (
                f"SciteProvider leaked {module}.{type(raised).__name__} — "
                f"must be retrieval.* (Option-X escape hatch)"
            )
            assert "requests" not in module
            assert "urllib3" not in module


# ---------------------------------------------------------------------------
# AC-T.11 — no-stateful-mock anti-pattern guard (Murat strengthening #8)
# ---------------------------------------------------------------------------


def test_scite_provider_test_module_has_no_stateful_mocks() -> None:
    """Prevents stateful-mock reintroduction (Model A guard).

    Tokens are assembled at runtime so this self-test does not trip on its own
    source text. Any *literal* appearance in the module of the forbidden tokens
    (e.g., an `import` line, a direct instantiation) will fail the assert.
    """
    source = Path(__file__).read_text(encoding="utf-8")
    # Concatenate at runtime so the literal tokens never appear in-file.
    forbidden = (
        "Magic" + "Mock",
        "Async" + "Mock",
        "unittest" + ".mock",
    )
    for token in forbidden:
        assert token not in source, (
            f"SciteProvider tests must not use {token!r} — "
            f"use `responses.RequestsMock()` + deterministic fixtures instead."
        )
