"""Live citation resolution (DD1 / DD3 / DD8).

Resolves a typed component's embedded citation to a real, dereferenced reference
(``resolved`` | ``failed`` | ``ungrounded`` — NEVER a fabricated DOI/title).

SEAM (DD1): resolution routes through the IN-PROCESS Texas
``retrieval.dispatcher.dispatch`` against the OAuth-proven ``SciteProvider`` —
the same path ``app/marcus/orchestrator/research_wiring.py`` uses. We do NOT use
``retrieval_dispatch.py::dispatch_retrieval`` (a subprocess shell-out for locator
bundles; wrong seam). For OFFLINE unit tests the ``dispatch`` callable is
injected with a fake; the LIVE leg uses the real dispatcher.

DOI-DEREFERENCE (DD8): we ask scite via ``search_literature({"dois":[doi],
"limit":1})`` (no ``term``). The ``paper_metadata`` tool is unverified — never
used here; the ``SciteProvider`` search path is extended (additively) to accept a
``dois`` filter so this routes cleanly.

DEPENDENCY DIRECTION (DD2): Texas-side; no ``app.marcus`` import. Returns plain
dicts (the wiring maps them into ``CitationResolution``). The markdown normalizer
used for the A4 groundedness gate (DD6) is INJECTED (``normalize_fn``) so the
canonical ``g0_enrichment_wiring._normalize_for_groundedness`` is reused without
a back-arrow import.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Callable, Iterable
from typing import Any

from .universal_md import is_excerpt_grounded

logger = logging.getLogger(__name__)

RESOLVER_PROVIDER = "scite"
NORMALIZATION_VERSION = "tex-norm-v1"

# DOI matcher. The registered-DOI grammar is ``10.<registrant>/<suffix>``; the
# suffix is greedy but STOPS at whitespace and the delimiters that routinely
# enclose an inline citation (``"`` ``]`` ``<`` ``>``). NOTE: ``)`` is INTENTIONALLY
# allowed inside the match — biomedical DOIs embed BALANCED parens, e.g. the Lancet
# DOI ``10.1016/S0140-6736(09)60401-3``. The wrapping case
# ``(doi:10.1001/jama.2019.13978)`` leaves a single UNBALANCED trailing ``)`` which
# :func:`_strip_doi_trailing` removes; balanced inner parens survive. A trailing run
# of sentence punctuation (``. , ; :``) is likewise stripped.
DOI_RE = re.compile(r"10\.\d{4,9}/[^\s\"<>\]]+", re.IGNORECASE)
_DOI_TRAILING_PUNCT = ".,;:"


def _strip_doi_trailing(doi: str) -> str:
    """Strip trailing sentence punctuation and any UNBALANCED trailing ``)``.

    A ``)`` is only removed when there are more closing than opening parens in the
    candidate (i.e. it wraps the citation rather than belonging to the DOI). This
    preserves embedded balanced parens (Lancet-style DOIs) while still stripping a
    wrapping paren. Sentence punctuation and wrapping parens may interleave (e.g.
    ``...13978).``), so we peel one trailing char at a time until stable.
    """
    while doi:
        last = doi[-1]
        if last in _DOI_TRAILING_PUNCT or (
            last == ")" and doi.count(")") > doi.count("(")
        ):
            doi = doi[:-1]
        else:
            break
    return doi


def extract_doi(text: str) -> str | None:
    """Return the FIRST DOI found in ``text`` (stripped of trailing punctuation), else None."""
    if not text:
        return None
    match = DOI_RE.search(text)
    if not match:
        return None
    doi = _strip_doi_trailing(match.group(0))
    return doi or None


def _build_intent(doi: str) -> Any:
    """Build the scite DOI-dereference ``RetrievalIntent`` (DD8 ``dois`` route)."""
    from retrieval import (  # noqa: PLC0415
        AcceptanceCriteria,
        ProviderHint,
        RetrievalIntent,
    )

    return RetrievalIntent(
        intent=doi,
        kind="direct_ref",
        provider_hints=[
            ProviderHint(
                provider=RESOLVER_PROVIDER,
                # mode="search" forces the (verified) search_literature tool; the
                # `dois` filter makes it a DOI dereference, not a topical term
                # search (DD8). max_results=1 honors the {"limit":1} contract.
                params={"mode": "search", "dois": [doi], "max_results": 1},
            )
        ],
        acceptance_criteria=AcceptanceCriteria(mechanical={"min_results": 1}),
        iteration_budget=1,
        convergence_required=False,
        cross_validate=False,
    )


def _default_dispatch(intent: Any) -> Any:
    """Real in-process Texas dispatch (DD1 seam). Returns a ``ProviderResult``."""
    from retrieval.dispatcher import dispatch as dispatch_intent  # noqa: PLC0415

    return dispatch_intent(intent)


def _first_result(dispatched: Any) -> Any:
    """Normalize ``dispatch`` return (single ProviderResult or list) to one result."""
    if isinstance(dispatched, list):
        return dispatched[0] if dispatched else None
    return dispatched


def _resolved_ref_from_row(row: Any) -> dict[str, Any]:
    """Build the ``resolved_ref`` dict from a ``TexasRow`` (DD5 canonicalization).

    Reuses ``retrieval.normalize.coerce_authors`` for author canonicalization.
    ``access_url`` is the canonical ``https://doi.org/<doi>`` form (scite MCP
    instruction). Optional keys (journal/authors/year) are omitted when absent so
    a thin record stays thin.
    """
    from retrieval.normalize import coerce_authors  # noqa: PLC0415

    meta = getattr(row, "provider_metadata", None) or {}
    scite_meta = meta.get("scite") if isinstance(meta, dict) else {}
    scite_meta = scite_meta or {}

    doi = scite_meta.get("doi") or getattr(row, "source_id", "") or ""
    title = getattr(row, "title", "") or ""
    ref: dict[str, Any] = {
        "title": title,
        "doi": doi or None,
        "access_url": f"https://doi.org/{doi}" if doi else None,
    }
    venue = scite_meta.get("venue")
    if venue:
        ref["journal"] = venue
    authors = coerce_authors(getattr(row, "authors", None))
    if authors:
        ref["authors"] = authors
    year = scite_meta.get("year") or getattr(row, "date", None)
    if year:
        ref["year"] = str(year)
    return ref


def _is_acceptance_met(result: Any) -> bool:
    return bool(getattr(result, "acceptance_met", False))


def _rows(result: Any) -> list[Any]:
    rows = getattr(result, "rows", None)
    return list(rows) if rows else []


def _select_components(components: Iterable[Any]) -> list[Any]:
    """Components to resolve: ``reference_citation`` typed OR DOI-bearing excerpt.

    The design scopes resolution to ``reference_citation`` components (DD3). We
    ALSO include any component whose verbatim excerpt carries a DOI — inline
    citations frequently land inside ``narration``/``slide`` excerpts in real
    corpora, and resolving them is what P5 needs. The set is a strict SUPERSET of
    the ``reference_citation`` set, so the design scope is never narrowed.
    """
    selected: list[Any] = []
    for comp in components:
        source_type = getattr(comp, "source_type", None)
        excerpt = getattr(comp, "excerpt", "") or ""
        if source_type == "reference_citation" or extract_doi(excerpt) is not None:
            selected.append(comp)
    return selected


def resolve_citation_for_component(
    comp: Any,
    source_text: str | None,
    *,
    dispatch: Callable[[Any], Any],
    normalize_fn: Callable[[str], str] | None,
) -> dict[str, Any]:
    """Resolve ONE component's citation → a CitationResolution-shaped dict.

    Order (DD6 then DD8):
      1. A4 groundedness (excerpt-vs-source ONLY): excerpt not grounded in its
         parent source → ``ungrounded`` (never resolve a DOI off an ungrounded
         excerpt). Skipped when no normalizer / source text is available.
      2. DOI extraction: no DOI in the excerpt → ``failed`` / ``no_doi_in_excerpt``.
      3. Live dereference: dispatch raises → ``failed`` / ``dispatch_error``;
         empty result (scite ``total:0``) → ``failed`` / ``not_in_index``;
         a hit echoing the DOI → ``resolved`` with a real ``resolved_ref``.
    """
    component_id = getattr(comp, "component_id", "")
    excerpt = getattr(comp, "excerpt", "") or ""

    base: dict[str, Any] = {
        "component_id": component_id,
        "doi": None,
        "resolution_status": "failed",
        "resolved_ref": None,
        "reason": None,
        "resolver_provider": RESOLVER_PROVIDER,
        "normalization_version": NORMALIZATION_VERSION,
    }

    # 1. A4 groundedness (DD6). Scope = excerpt-vs-source ONLY.
    if (
        normalize_fn is not None
        and source_text is not None
        and not is_excerpt_grounded(excerpt, source_text, normalize_fn)
    ):
        base["resolution_status"] = "ungrounded"
        logger.warning(
            "pass0: component %r excerpt is NOT grounded in its parent source "
            "(A4); marking ungrounded, not resolving a DOI off it",
            component_id,
        )
        return base

    # 2. DOI extraction.
    doi = extract_doi(excerpt)
    if doi is None:
        base["reason"] = "no_doi_in_excerpt"
        return base
    base["doi"] = doi

    # 3. Live dereference via the in-process Texas dispatcher (DD1 + DD8).
    try:
        result = _first_result(dispatch(_build_intent(doi)))
    except Exception:  # noqa: BLE001 — any dispatch failure is a fail-soft reason
        logger.warning(
            "pass0: dispatch error resolving DOI %r for component %r",
            doi,
            component_id,
            exc_info=True,
        )
        base["reason"] = "dispatch_error"
        return base

    rows = _rows(result)
    if not rows or not _is_acceptance_met(result):
        base["reason"] = "not_in_index"
        return base

    base["resolution_status"] = "resolved"
    base["resolved_ref"] = _resolved_ref_from_row(rows[0])
    return base


def resolve_citations(
    components: Iterable[Any],
    source_by_id: dict[str, str],
    *,
    dispatch: Callable[[Any], Any] | None = None,
    normalize_fn: Callable[[str], str] | None = None,
) -> list[dict[str, Any]]:
    """Resolve every citation-bearing component → CitationResolution-shaped dicts.

    ``components`` are the P1 ``TypedComponent`` rows (duck-typed: read
    ``component_id`` / ``source_type`` / ``excerpt`` / ``parent_source_id``).
    ``source_by_id`` maps ``parent_source_id`` → the parent's raw source text
    (for the A4 groundedness gate). ``dispatch`` defaults to the real in-process
    Texas dispatcher (DD1); inject a fake for offline unit tests. ``normalize_fn``
    is the canonical markdown normalizer (inject
    ``g0_enrichment_wiring._normalize_for_groundedness``); when None the
    groundedness gate is skipped.

    Returns one dict per SELECTED component (reference_citation OR DOI-bearing),
    in component order. The result is replay-deterministic given a frozen
    dispatch (DD7: the wiring serializes it into the existing fingerprint cache).
    """
    dispatch = dispatch or _default_dispatch
    out: list[dict[str, Any]] = []
    for comp in _select_components(components):
        parent_id = getattr(comp, "parent_source_id", "")
        source_text = source_by_id.get(parent_id)
        out.append(
            resolve_citation_for_component(
                comp,
                source_text,
                dispatch=dispatch,
                normalize_fn=normalize_fn,
            )
        )
    return out


__all__ = [
    "DOI_RE",
    "NORMALIZATION_VERSION",
    "RESOLVER_PROVIDER",
    "extract_doi",
    "resolve_citation_for_component",
    "resolve_citations",
]
