"""`SciteProvider` — first real consumer of 27-0's `RetrievalAdapter` ABC.

Story 27-2. scite.ai adapter using 27-0's `MCPClient` (Option Y JSON-RPC)
against the scite MCP. Auto-registers via `PROVIDER_INFO` ClassVar,
superseding the `scite: ratified` placeholder in `provider_directory.py`
so `list_providers()` surfaces `scite: ready`.

Architectural guardrails (27-0 anti-patterns, enforced here):
  - Deterministic query formulation only — no LLM in the loop (AC-C.7).
  - Refinement monotonically-loosening (delegates to
    `refinement_registry.drop_filters_in_order` per PDG-3 path A).
  - Library-agnostic `MCPClient` public surface — no `requests.Response`
    or `requests.*` exception types leak out (AC-C.2, AC-T.10).
  - `provider_metadata.scite` is an opaque sub-object; per-provider fields
    do not pollute the top-level `TexasRow` schema (AC-C.4, AC-B.2).
"""

from __future__ import annotations

import os
from typing import Any, ClassVar

from .base import RetrievalAdapter
from .contracts import (
    AcceptanceCriteria,
    ProviderInfo,
    RetrievalIntent,
    TexasRow,
)
from .mcp_client import MCPClient, MCPServerConfig
from .normalize import build_texas_row, coerce_authors
from .refinement_registry import drop_filters_in_order

# ---------------------------------------------------------------------------
# Module-level constants — data, not inference (AC-C.7 guardrail).
# ---------------------------------------------------------------------------

SCITE_MCP_URL = os.environ.get("SCITE_MCP_URL", "https://api.scite.ai/mcp")
"""scite MCP endpoint. Override via `SCITE_MCP_URL` env for local testing."""

SCITE_AUTH_ENV_VARS: tuple[str, str] = ("SCITE_USER_NAME", "SCITE_PASSWORD")
"""HTTP Basic auth env var pair (user, password). MCPClient reads lazily."""


# Authority-tier lookup table: scite venue-string → canonical tier.
# Data-driven (NOT inference) per AC-C.7. Keys lowercased for case-insensitive
# matching; unknown venues → None (falls through to caller default).
SCITE_AUTHORITY_TIERS: dict[str, str] = {
    # Peer-reviewed journals (illustrative — list grows as venues are observed)
    "nature": "peer-reviewed",
    "nature medicine": "peer-reviewed",
    "nature neuroscience": "peer-reviewed",
    "science": "peer-reviewed",
    "cell": "peer-reviewed",
    "the lancet": "peer-reviewed",
    "new england journal of medicine": "peer-reviewed",
    "jama": "peer-reviewed",
    "pnas": "peer-reviewed",
    "proceedings of the national academy of sciences": "peer-reviewed",
    # Preprint servers
    "arxiv": "preprint",
    "biorxiv": "preprint",
    "medrxiv": "preprint",
    "ssrn": "preprint",
    "psyarxiv": "preprint",
    "chemrxiv": "preprint",
}

# Tier → numeric rank for ordered comparison (higher = stricter).
_AUTHORITY_TIER_RANK: dict[str | None, int] = {
    "peer-reviewed": 3,
    "preprint": 2,
    "web": 1,
    None: 0,
}

# Refinement key order (PDG-3 path A): progressively drop the most-restrictive
# filter first. Order is scite-specific domain knowledge, captured as data.
SCITE_REFINEMENT_KEY_ORDER: tuple[str, ...] = (
    "supporting_citations_min",
    "authority_tier_min",
    "date_range",
    "cited_by_count_min",
)


# MCP tool names (PDG-2 path B: inferred from scite.ai/api-docs + public MCP docs).
# Exact shapes to be verified at first-live-run; see `27-2-live-cassette-refresh`
# follow-on ticket. Fixture provenance documented at
# `tests/fixtures/retrieval/scite/README.md`.
_SCITE_TOOL_SEARCH = "search"
_SCITE_TOOL_PAPER = "paper_metadata"
_SCITE_TOOL_CITATIONS = "citation_contexts"

# Citation-context retention cap per classification (AC-B.2 § normalize).
_CITATION_CONTEXT_RETAIN_PER_CLASS = 3

# Honored acceptance-criteria keys (AC-B.3: NOT the default empty set).
_HONORED_CRITERIA: frozenset[str] = frozenset({
    "date_range",
    "min_results",
    "exclude_ids",
    "license_allow",
    "authority_tier_min",
    "supporting_citations_min",
    "cited_by_count_min",
})


# ---------------------------------------------------------------------------
# Helpers: authority-tier derivation + query-mode selection (data-driven).
# ---------------------------------------------------------------------------


def _derive_authority_tier(venue: Any) -> str | None:
    """Map a scite venue-string to a canonical authority tier.

    Resolution order:
      1. Exact case-insensitive match against `SCITE_AUTHORITY_TIERS`.
      2. Substring match (first matching key wins — iteration order is stable).
      3. None (unknown venue → downstream falls through to "web" or null).

    PATCH-6 (2026-04-18): non-string venues (int, dict, list — provider-shape
    surprise) return None rather than crashing on `.strip()`.
    """
    if not venue or not isinstance(venue, str):
        return None
    key = venue.strip().lower()
    if key in SCITE_AUTHORITY_TIERS:
        return SCITE_AUTHORITY_TIERS[key]
    for venue_key, tier in SCITE_AUTHORITY_TIERS.items():
        if venue_key in key:
            return tier
    return None


def _mode_from_intent(intent: RetrievalIntent) -> str:
    """Determine query-mode from intent + provider_hints[scite].params.

    Resolution:
      1. Explicit `params["mode"]` on the scite provider_hint (takes priority).
      2. Intent `kind="direct_ref"` → "paper" mode (DOI lookup).
      3. Default → "search" (topical query).
    """
    for hint in intent.provider_hints:
        if hint.provider == "scite":
            mode = hint.params.get("mode")
            if mode in ("search", "paper", "citation_contexts"):
                return mode
    if intent.kind == "direct_ref":
        return "paper"
    return "search"


def _extract_filters_from_mechanical(
    mechanical: dict[str, Any],
) -> dict[str, Any]:
    """Lift mechanical-criteria keys into a scite-compatible filter subset.

    Deterministic Python — no reordering that would break
    formulate_query byte-determinism. Returns a fresh dict.
    """
    out: dict[str, Any] = {}
    # Iterate in declared key order for determinism.
    for key in ("date_range", "exclude_ids", "license_allow"):
        if key in mechanical:
            out[key] = mechanical[key]
    return out


# ---------------------------------------------------------------------------
# The adapter.
# ---------------------------------------------------------------------------


class SciteProvider(RetrievalAdapter):
    """scite.ai retrieval adapter — Story 27-2.

    Implements the 7 abstract methods of `RetrievalAdapter`. Uses 27-0's
    `MCPClient` for transport. Auto-registers via `PROVIDER_INFO`.
    """

    PROVIDER_INFO: ClassVar[ProviderInfo] = ProviderInfo(
        id="scite",
        shape="retrieval",
        status="ready",
        capabilities=[
            "citation-network",
            "supporting-contrasting-counts",
            "authority-tier",
            "smart-citation-classification",
        ],
        auth_env_vars=list(SCITE_AUTH_ENV_VARS),
        spec_ref="_bmad-output/implementation-artifacts/27-2-scite-ai-provider.md",
        notes=(
            "scite.ai MCP adapter — scholarly-citation retrieval with smart-"
            "citation context (supporting / contradicting / mentioning). "
            "Uses 27-0 MCPClient (Option Y JSON-RPC). Identity key: DOI."
        ),
    )

    HONORED_CRITERIA: ClassVar[frozenset[str]] = _HONORED_CRITERIA

    def __init__(
        self,
        mcp_client: MCPClient | None = None,
        *,
        mcp_url: str | None = None,
    ) -> None:
        self._mcp_client = mcp_client  # Lazy: real instance built on first execute().
        self._mcp_url = mcp_url or SCITE_MCP_URL

    # ---- Lazy MCPClient wiring (AC-C.2 library-agnostic) ------------------

    def _client(self) -> MCPClient:
        """Lazy MCPClient instantiation — env vars resolved at first call, not __init__."""
        if self._mcp_client is None:
            config = MCPServerConfig(
                url=self._mcp_url,
                auth_env=list(SCITE_AUTH_ENV_VARS),
                auth_style="basic",
            )
            self._mcp_client = MCPClient({self.PROVIDER_INFO.id: config})
        return self._mcp_client

    # ---- T3: formulate_query + query-mode helpers -------------------------

    def formulate_query(self, intent: RetrievalIntent) -> dict[str, Any]:
        """Translate intent + hints into a scite query dict (deterministic).

        Byte-identical across invocations with the same intent. Three modes:
          - "search": topical query + filters (most common).
          - "paper": DOI-direct lookup (intent.kind="direct_ref" or explicit).
          - "citation_contexts": DOI-direct citation-context fetch.
        """
        mode = _mode_from_intent(intent)
        # Pull the scite hint's params (guaranteed to exist — dispatcher
        # only routes here when "scite" is in provider_hints).
        scite_params: dict[str, Any] = {}
        for hint in intent.provider_hints:
            if hint.provider == "scite":
                scite_params = dict(hint.params)
                break
        if mode == "paper":
            return self._build_query_paper(intent, scite_params)
        if mode == "citation_contexts":
            return self._build_query_citations(intent, scite_params)
        return self._build_query_search(intent, scite_params)

    def _build_query_search(
        self,
        intent: RetrievalIntent,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Build a scite search-mode query dict."""
        mechanical = intent.acceptance_criteria.mechanical or {}
        filters = _extract_filters_from_mechanical(mechanical)
        # Provider-scored min-count hints (scite honors these server-side).
        scored = intent.acceptance_criteria.provider_scored or {}
        if "supporting_citations_min" in scored:
            filters["supporting_citations_min"] = scored["supporting_citations_min"]
        if "cited_by_count_min" in scored:
            filters["cited_by_count_min"] = scored["cited_by_count_min"]
        # Declared order preserves determinism.
        query: dict[str, Any] = {
            "mode": "search",
            "query": intent.intent,
            "max_results": int(mechanical.get("min_results", 10)),
            "filters": filters,
        }
        # Operator-hint overrides (e.g., explicit max_results cap).
        if "max_results" in params:
            query["max_results"] = int(params["max_results"])
        return query

    def _build_query_paper(
        self,
        intent: RetrievalIntent,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Build a scite paper-metadata query dict (DOI-direct)."""
        # DOI source priority: params["doi"] → intent-text DOI-like → raise.
        doi = params.get("doi")
        if not doi:
            # Intent text is the DOI for direct_ref mode.
            doi = intent.intent.strip()
        return {
            "mode": "paper",
            "doi": doi,
        }

    def _build_query_citations(
        self,
        intent: RetrievalIntent,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Build a scite citation-contexts query dict."""
        doi = params.get("doi") or intent.intent.strip()
        return {
            "mode": "citation_contexts",
            "doi": doi,
        }

    # ---- T4: execute via MCPClient ----------------------------------------

    def execute(self, query: dict[str, Any]) -> list[dict[str, Any]]:
        """Dispatch `query` to scite MCP via MCPClient.

        Mode selects the tool: search | paper_metadata | citation_contexts.
        Returns a list of provider-shaped dicts (not yet normalized; T6).

        Let MCPClient exceptions propagate unchanged — the dispatcher wraps
        them in a `ProviderResult` with `acceptance_met: False`. No retry
        logic here (AC-C.11 dumbness clause).
        """
        mode = query.get("mode")
        client = self._client()
        if mode == "paper":
            args = {"doi": query["doi"]}
            result = client.call_tool(self.PROVIDER_INFO.id, _SCITE_TOOL_PAPER, args)
            # Paper mode returns a single record; wrap in a list for
            # normalize() uniformity.
            return [result] if result else []
        if mode == "citation_contexts":
            args = {"doi": query["doi"]}
            result = client.call_tool(
                self.PROVIDER_INFO.id, _SCITE_TOOL_CITATIONS, args
            )
            contexts = result.get("contexts") if isinstance(result, dict) else None
            return list(contexts) if isinstance(contexts, list) else []
        # Default: search mode.
        args = {
            "query": query["query"],
            "max_results": query.get("max_results", 10),
            "filters": dict(query.get("filters", {})),
        }
        result = client.call_tool(self.PROVIDER_INFO.id, _SCITE_TOOL_SEARCH, args)
        papers = result.get("papers") if isinstance(result, dict) else None
        return list(papers) if isinstance(papers, list) else []

    # ---- T5: apply_mechanical + apply_provider_scored ---------------------

    def apply_mechanical(
        self,
        results: list[dict[str, Any]],
        criteria: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Deterministic-predicate filter over mechanical acceptance criteria.

        Honored keys: date_range, exclude_ids, license_allow, min_results
        (min_results is dispatcher-evaluated post-filter — passthrough here).
        """
        out = list(results)
        # date_range: [start, end] as "YYYY-MM-DD" strings.
        date_range = criteria.get("date_range")
        if isinstance(date_range, list | tuple) and len(date_range) == 2:
            start, end = str(date_range[0]), str(date_range[1])
            out = [
                r for r in out
                if _row_date(r) is None or (start <= _row_date(r) <= end)
            ]
        # exclude_ids: drop rows whose DOI / scite_paper_id appear in the list.
        exclude = criteria.get("exclude_ids") or []
        if exclude:
            exclude_set = {str(x) for x in exclude}
            out = [
                r for r in out
                if str(r.get("doi", "")) not in exclude_set
                and str(r.get("scite_paper_id", "")) not in exclude_set
            ]
        # license_allow: substring match against the row's license string.
        license_allow = criteria.get("license_allow")
        if isinstance(license_allow, list | tuple) and license_allow:
            allow_lower = {str(x).lower() for x in license_allow}
            out = [
                r for r in out
                if str(r.get("license", "")).lower() in allow_lower
                or not r.get("license")  # unknown license → pass
            ]
        return out

    def apply_provider_scored(
        self,
        results: list[dict[str, Any]],
        criteria: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Provider-scored filter: scite-native signals (authority + citations)."""
        out = list(results)
        # authority_tier_min: compare derived tier against rank threshold.
        tier_min = criteria.get("authority_tier_min")
        if tier_min:
            min_rank = _AUTHORITY_TIER_RANK.get(tier_min, 0)
            out = [
                r for r in out
                if _AUTHORITY_TIER_RANK.get(_derive_authority_tier(r.get("venue")), 0)
                >= min_rank
            ]
        # supporting_citations_min: scite's supporting_count field.
        sup_min = criteria.get("supporting_citations_min")
        if isinstance(sup_min, int):
            out = [
                r for r in out
                if int(r.get("supporting_count", 0) or 0) >= sup_min
            ]
        # cited_by_count_min: total citation count.
        cited_min = criteria.get("cited_by_count_min")
        if isinstance(cited_min, int):
            out = [
                r for r in out
                if int(r.get("cited_by_count", 0) or 0) >= cited_min
            ]
        return out

    # ---- T6: normalize → TexasRow with provider_metadata.scite ------------

    def normalize(self, results: list[dict[str, Any]]) -> list[TexasRow]:
        """Scite paper dicts → canonical TexasRow list.

        Paywall degradation: `full_text_available: false` → body = abstract only;
        `provider_metadata.scite.known_losses = ["full_text_paywalled"]`.
        """
        rows: list[TexasRow] = []
        for result in results:
            doi = str(result.get("doi") or "")
            scite_paper_id = str(result.get("scite_paper_id") or "")
            source_id = doi or scite_paper_id or str(result.get("id") or "scite-unknown")
            title = str(result.get("title") or "")
            authors = coerce_authors(result.get("authors"))
            year = result.get("year")
            date = str(year) if year else None
            venue = result.get("venue")
            authority_tier = _derive_authority_tier(venue)

            # Body composition: full text if available, else abstract only.
            full_text_available = bool(result.get("full_text_available", False))
            abstract = str(result.get("abstract") or "")
            full_text = str(result.get("full_text") or "") if full_text_available else ""
            body = full_text if full_text else abstract

            # Citation contexts — top-N per classification, stable ordering.
            raw_contexts = result.get("citation_contexts") or []
            citation_snippets = _truncate_citation_contexts(raw_contexts)

            # Known losses sentinel (AC-B.4 paywall degradation).
            known_losses: list[str] = []
            if not full_text_available:
                known_losses.append("full_text_paywalled")

            provider_metadata: dict[str, Any] = {
                "scite": {
                    "doi": doi or None,
                    "scite_paper_id": scite_paper_id or None,
                    "venue": venue,
                    "year": year,
                    "supporting_count": int(result.get("supporting_count", 0) or 0),
                    "contradicting_count": int(result.get("contradicting_count", 0) or 0),
                    "mentioning_count": int(result.get("mentioning_count", 0) or 0),
                    "cited_by_count": int(result.get("cited_by_count", 0) or 0),
                    "citation_context_snippets": citation_snippets,
                    "scite_report_url": result.get("scite_report_url"),
                    "known_losses": known_losses,
                },
            }

            row = build_texas_row(
                source_id=source_id,
                provider=self.PROVIDER_INFO.id,
                title=title,
                body=body,
                authors=authors,
                date=date,
                authority_tier=authority_tier,
                provider_metadata=provider_metadata,
            )
            rows.append(row)
        return rows

    # ---- T7: refine — monotonic looseness via drop_filters_in_order -------

    def refine(
        self,
        previous_query: dict[str, Any],
        previous_results: list[dict[str, Any]],
        criteria: AcceptanceCriteria,
    ) -> dict[str, Any] | None:
        """Monotonically-loosen the query by dropping one filter per iteration.

        Uses `refinement_registry.drop_filters_in_order` with the scite-specific
        key-order list. Iteration counter is embedded in the query under
        `_refinement_iteration` so `refine` is a pure function of the previous
        query (FakeProvider pattern — no internal cursor state).

        Returns None when all keys in `SCITE_REFINEMENT_KEY_ORDER` are exhausted.
        """
        # Paper / citation_contexts modes don't benefit from refinement —
        # those are DOI-direct lookups; loosening would not improve results.
        if previous_query.get("mode") != "search":
            return None

        iteration = int(previous_query.get("_refinement_iteration", 0)) + 1

        # `current_filters` already reflects prior-iteration drops; `key_order`
        # recomputes to the subset of SCITE_REFINEMENT_KEY_ORDER still present.
        # We always drop the FIRST remaining key in that priority list — which
        # means `drop_filters_in_order` is called with iteration=1, not the
        # cumulative counter. Code-review PATCH-1 (2026-04-18): prior version
        # passed the cumulative iteration, which caused `date_range` to be
        # dropped on call 2 instead of `authority_tier_min`, violating the
        # declared scite priority order.
        current_filters = dict(previous_query.get("filters", {}))

        key_order = [k for k in SCITE_REFINEMENT_KEY_ORDER if k in current_filters]
        if not key_order:
            # All priority-list filters have been dropped; no further loosening.
            return None

        new_filters = drop_filters_in_order(
            current_filters,
            criteria,
            iteration=1,
            order=key_order,
        )
        if new_filters is None:
            return None

        new_query = dict(previous_query)
        new_query["filters"] = new_filters
        new_query["_refinement_iteration"] = iteration
        return new_query

    # ---- T2: identity_key — 3-tier fallback -------------------------------

    def identity_key(self, row: TexasRow) -> str:
        """Return DOI (primary) → scite_paper_id → source_id (final fallback).

        Raises `NotImplementedError` only if all three are empty/absent —
        the dispatcher surfaces this at `cross_validate: true` preflight
        (anti-pattern #10 from 27-0).
        """
        meta = row.provider_metadata or {}
        scite_meta = meta.get("scite") or {}
        doi = scite_meta.get("doi")
        if isinstance(doi, str) and doi:
            return doi
        paper_id = scite_meta.get("scite_paper_id")
        if isinstance(paper_id, str) and paper_id:
            return paper_id
        if row.source_id:
            return row.source_id
        raise NotImplementedError(
            f"SciteProvider.identity_key: no DOI / scite_paper_id / source_id "
            f"on row {row!r}. Cross-validation requires one of these."
        )

    def declare_honored_criteria(self) -> set[str]:
        """AC-B.3 — explicit frozenset (not the default empty set)."""
        return set(self.HONORED_CRITERIA)


# ---------------------------------------------------------------------------
# Module-level helpers (testable in isolation).
# ---------------------------------------------------------------------------


def _row_date(result: dict[str, Any]) -> str | None:
    """Extract a normalized YYYY-MM-DD-comparable date from a scite result dict.

    Uses:
      1. `publication_date` field (assumed ISO-shaped) if present.
      2. `year` field → "<year>-01-01" (year-only comparison).
      3. None.
    """
    pub_date = result.get("publication_date")
    if isinstance(pub_date, str) and pub_date:
        return pub_date[:10]  # YYYY-MM-DD slice
    year = result.get("year")
    if isinstance(year, int):
        return f"{year:04d}-01-01"
    return None


def _truncate_citation_contexts(
    raw_contexts: list[Any],
) -> list[dict[str, Any]]:
    """Retain top-N per classification (supporting / contradicting / mentioning).

    Preserves order within each classification (scite returns most-relevant
    first by convention). Stable across invocations for determinism.
    """
    buckets: dict[str, list[dict[str, Any]]] = {
        "supporting": [],
        "contradicting": [],
        "mentioning": [],
    }
    for ctx in raw_contexts:
        if not isinstance(ctx, dict):
            continue
        classification = ctx.get("classification")
        if classification not in buckets:
            continue
        if len(buckets[classification]) >= _CITATION_CONTEXT_RETAIN_PER_CLASS:
            continue
        buckets[classification].append({
            "classification": classification,
            "citing_doi": ctx.get("citing_doi"),
            "snippet": ctx.get("snippet"),
        })
    # Concatenate in declared order for determinism.
    out: list[dict[str, Any]] = []
    for classification in ("supporting", "contradicting", "mentioning"):
        out.extend(buckets[classification])
    return out


__all__ = [
    "SCITE_AUTHORITY_TIERS",
    "SCITE_AUTH_ENV_VARS",
    "SCITE_MCP_URL",
    "SCITE_REFINEMENT_KEY_ORDER",
    "SciteProvider",
]
