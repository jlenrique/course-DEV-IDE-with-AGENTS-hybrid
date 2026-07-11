"""Thin research triangulator — Agentic Research Foundations R3.

Consumes post-dispatch ``ProviderResult`` / ``TexasRow`` lists (with optional
``ConvergenceSignal``) and emits a deterministic composite reliability score
plus structural contradiction flags. Does **not** call HTTP clients — Texas
dispatcher remains the only fetch path (party decision).

Identity merge prefers DOI, then normalized title (Consensus MCP markdown often
lacks DOIs). Optional ``enrich_via_scite_title_bridge`` resolves Consensus
titles through Scite's ``titles`` filter so live dual-provider clusters form.
"""

from __future__ import annotations

import re
from typing import Any, Callable, Literal

from pydantic import BaseModel, ConfigDict, Field

from .contracts import (
    AcceptanceCriteria,
    ConvergenceSignal,
    ProviderHint,
    ProviderResult,
    RetrievalIntent,
    TexasRow,
)

TriangulationStatus = Literal["dual_provider", "single_provider", "none"]
ContradictionReason = Literal[
    "scite_contradicting_context",
    "single_source_only",
    "no_rows",
]

_DOI_RE = re.compile(r"10\.\d{4,9}/[^\s\"<>]+", re.IGNORECASE)
_TITLE_NON_ALNUM = re.compile(r"[^a-z0-9\s]+")
_TITLE_WS = re.compile(r"\s+")


class ContradictionFlag(BaseModel):
    """One structural contradiction / weakness signal on a triangulated row."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    source_id: str = Field(min_length=1)
    reason: ContradictionReason
    detail: dict[str, Any] = Field(default_factory=dict)


class TriangulatedRow(BaseModel):
    """One identity-keyed cluster after triangulation."""

    model_config = ConfigDict(extra="forbid")

    source_id: str = Field(min_length=1)
    identity_key: str = Field(min_length=1)
    rows_by_provider: dict[str, TexasRow] = Field(default_factory=dict)
    convergence_signal: ConvergenceSignal | None = None
    reliability_score: float = Field(ge=0.0, le=1.0)
    triangulation_status: TriangulationStatus
    contradiction_flags: list[ContradictionFlag] = Field(default_factory=list)


class TriangulationReceipt(BaseModel):
    """Receipt attached to research_wiring contribution output (R3)."""

    model_config = ConfigDict(extra="forbid")

    query_intent: str = ""
    triangulated_rows: list[TriangulatedRow] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


def _scite_meta(row: TexasRow) -> dict[str, Any]:
    meta = row.provider_metadata or {}
    scite = meta.get("scite")
    return scite if isinstance(scite, dict) else {}


def _consensus_meta(row: TexasRow) -> dict[str, Any]:
    meta = row.provider_metadata or {}
    consensus = meta.get("consensus")
    return consensus if isinstance(consensus, dict) else {}


def normalize_title_key(title: str | None) -> str | None:
    """Deterministic title fingerprint for cross-provider identity merge."""
    if not title or not str(title).strip():
        return None
    cleaned = _TITLE_NON_ALNUM.sub(" ", str(title).lower())
    cleaned = _TITLE_WS.sub(" ", cleaned).strip()
    # Short titles collide too easily across unrelated papers.
    if len(cleaned) < 16:
        return None
    return cleaned


def extract_doi(row: TexasRow) -> str | None:
    """Pull a DOI from source_id or nested provider metadata."""
    sid = (row.source_id or "").strip()
    if sid.lower().startswith("10.") and "/" in sid:
        return sid.lower().rstrip(".,;)")
    match = _DOI_RE.search(sid)
    if match:
        return match.group(0).lower().rstrip(".,;)")
    for nest in (row.provider_metadata or {}).values():
        if not isinstance(nest, dict):
            continue
        doi = nest.get("doi")
        if isinstance(doi, str) and doi.strip():
            found = doi.strip().lower().rstrip(".,;)")
            if found.startswith("10."):
                return found
            match = _DOI_RE.search(found)
            if match:
                return match.group(0).lower().rstrip(".,;)")
    return None


def _identity_key(row: TexasRow) -> str:
    """Prefer DOI; then normalized title; else provider-scoped id."""
    doi = extract_doi(row)
    if doi:
        return doi
    title_key = normalize_title_key(row.title)
    if title_key:
        return f"title:{title_key}"
    sid = (row.source_id or "").strip() or "unknown"
    return f"{row.provider}:{sid}"


def _merge_clusters_sharing_titles(
    clusters: dict[str, dict[str, TexasRow]],
    signals: dict[str, ConvergenceSignal | None],
) -> tuple[dict[str, dict[str, TexasRow]], dict[str, ConvergenceSignal | None]]:
    """Union clusters that share a normalized title (DOI vs title-key split)."""
    title_to_keys: dict[str, list[str]] = {}
    for key, by_provider in clusters.items():
        for row in by_provider.values():
            tk = normalize_title_key(row.title)
            if tk:
                title_to_keys.setdefault(tk, []).append(key)

    parent = {key: key for key in clusters}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for keys in title_to_keys.values():
        unique = list(dict.fromkeys(keys))
        for other in unique[1:]:
            union(unique[0], other)

    merged_clusters: dict[str, dict[str, TexasRow]] = {}
    merged_signals: dict[str, ConvergenceSignal | None] = {}
    for key, by_provider in clusters.items():
        root = find(key)
        bucket = merged_clusters.setdefault(root, {})
        bucket.update(by_provider)
        sig = signals.get(key)
        if sig is not None:
            merged_signals[root] = sig
        else:
            merged_signals.setdefault(root, None)
    return merged_clusters, merged_signals


def enrich_via_scite_title_bridge(
    rows: list[TexasRow],
    *,
    max_titles: int = 5,
    dispatch_fn: Callable[[RetrievalIntent], Any] | None = None,
) -> list[TexasRow]:
    """Fetch Scite rows for Consensus titles that lack DOI overlap.

    Uses Texas ``dispatch`` (or injected ``dispatch_fn``) — no parallel HTTP.
    """
    scite_titles = {
        normalize_title_key(r.title)
        for r in rows
        if r.provider == "scite" and normalize_title_key(r.title)
    }
    bridge_titles: list[str] = []
    seen: set[str] = set()
    for row in rows:
        if row.provider != "consensus":
            continue
        if extract_doi(row):
            continue
        tk = normalize_title_key(row.title)
        if not tk or tk in scite_titles or tk in seen:
            continue
        seen.add(tk)
        bridge_titles.append(row.title.strip())
        if len(bridge_titles) >= max_titles:
            break
    if not bridge_titles:
        return list(rows)

    if dispatch_fn is None:
        from .dispatcher import dispatch as dispatch_fn  # noqa: PLC0415

    intent = RetrievalIntent(
        intent="R3 title-bridge: resolve Consensus titles via Scite",
        provider_hints=[
            ProviderHint(
                provider="scite",
                params={"titles": bridge_titles, "max_results": len(bridge_titles)},
            )
        ],
        acceptance_criteria=AcceptanceCriteria(
            mechanical={"min_results": 1},
        ),
        convergence_required=False,
        cross_validate=False,
    )
    results = dispatch_fn(intent)
    if not isinstance(results, list):
        results = [results]
    bridged: list[TexasRow] = []
    for provider_result in results:
        bridged.extend(list(getattr(provider_result, "rows", None) or []))
    if not bridged:
        return list(rows)
    return list(rows) + bridged


def _score_cluster(
    rows_by_provider: dict[str, TexasRow],
    signal: ConvergenceSignal | None,
) -> tuple[float, TriangulationStatus, list[ContradictionFlag]]:
    flags: list[ContradictionFlag] = []
    providers = sorted(rows_by_provider)
    primary_id = next(iter(rows_by_provider.values())).source_id

    if not providers:
        return 0.0, "none", [
            ContradictionFlag(
                source_id="none",
                reason="no_rows",
                detail={},
            )
        ]

    agreeing = list(signal.providers_agreeing) if signal else []
    single_only = list(signal.single_source_only) if signal else []

    if len(providers) >= 2 or len(agreeing) >= 2:
        status: TriangulationStatus = "dual_provider"
    else:
        status = "single_provider"

    score = 0.0
    if status == "dual_provider":
        score += 0.4
    if len(agreeing) >= 2:
        score += 0.1

    scite_row = rows_by_provider.get("scite")
    if scite_row is not None:
        sm = _scite_meta(scite_row)
        supporting = int(sm.get("supporting_count") or 0)
        contradicting = int(sm.get("contradicting_count") or 0)
        if supporting > contradicting:
            score += 0.15
        if contradicting > supporting:
            flags.append(
                ContradictionFlag(
                    source_id=scite_row.source_id,
                    reason="scite_contradicting_context",
                    detail={
                        "supporting_count": supporting,
                        "contradicting_count": contradicting,
                    },
                )
            )
        if scite_row.authority_tier:
            score += 0.2

    consensus_row = rows_by_provider.get("consensus")
    if consensus_row is not None:
        cm = _consensus_meta(consensus_row)
        cscore = cm.get("consensus_score")
        try:
            if cscore is not None and float(cscore) >= 0.5:
                score += 0.15
        except (TypeError, ValueError):
            pass

    # Mild recency: any row with a date starting 20xx
    for row in rows_by_provider.values():
        if row.date and str(row.date)[:2] == "20":
            score += 0.1
            break

    if status == "single_provider":
        flags.append(
            ContradictionFlag(
                source_id=primary_id,
                reason="single_source_only",
                detail={
                    "providers": providers,
                    "single_source_only": single_only,
                },
            )
        )

    return min(1.0, max(0.0, score)), status, flags


def triangulate_texas_rows(
    rows: list[TexasRow],
    *,
    query_intent: str = "",
    title_bridge: bool = False,
    max_bridge_titles: int = 5,
    dispatch_fn: Callable[[RetrievalIntent], Any] | None = None,
) -> TriangulationReceipt:
    """Cluster Texas rows by identity key and score each cluster.

    When ``title_bridge`` is True, Consensus titles without DOI overlap are
    resolved through Scite before clustering (live dual-provider path).
    """
    working = list(rows)
    bridge_added = 0
    if title_bridge:
        before = len(working)
        working = enrich_via_scite_title_bridge(
            working,
            max_titles=max_bridge_titles,
            dispatch_fn=dispatch_fn,
        )
        bridge_added = len(working) - before

    clusters: dict[str, dict[str, TexasRow]] = {}
    signals: dict[str, ConvergenceSignal | None] = {}
    for row in working:
        key = _identity_key(row)
        clusters.setdefault(key, {})[row.provider] = row
        if row.convergence_signal is not None:
            signals[key] = row.convergence_signal
        else:
            signals.setdefault(key, None)

    clusters, signals = _merge_clusters_sharing_titles(clusters, signals)

    triangulated: list[TriangulatedRow] = []
    for key, by_provider in sorted(clusters.items()):
        score, status, flags = _score_cluster(by_provider, signals.get(key))
        # Prefer DOI-bearing source_id when present after title-union merge.
        primary = next(iter(by_provider.values()))
        for candidate in by_provider.values():
            if extract_doi(candidate):
                primary = candidate
                break
        identity = extract_doi(primary) or key
        triangulated.append(
            TriangulatedRow(
                source_id=primary.source_id,
                identity_key=identity,
                rows_by_provider=by_provider,
                convergence_signal=signals.get(key),
                reliability_score=score,
                triangulation_status=status,
                contradiction_flags=flags,
            )
        )

    return TriangulationReceipt(
        query_intent=query_intent,
        triangulated_rows=triangulated,
        metadata={
            "row_count": len(working),
            "cluster_count": len(triangulated),
            "dual_provider_count": sum(
                1 for t in triangulated if t.triangulation_status == "dual_provider"
            ),
            "single_provider_count": sum(
                1 for t in triangulated if t.triangulation_status == "single_provider"
            ),
            "title_bridge_rows_added": bridge_added,
        },
    )


def triangulate_provider_results(
    provider_results: list[ProviderResult],
    *,
    query_intent: str = "",
) -> TriangulationReceipt:
    """Flatten ``ProviderResult`` rows then triangulate."""
    rows: list[TexasRow] = []
    for result in provider_results:
        rows.extend(list(result.rows or []))
    return triangulate_texas_rows(rows, query_intent=query_intent)


def corroborate_requires_triangulation(
    receipt: TriangulationReceipt,
    *,
    allow_single_provider_receipt: bool = True,
) -> tuple[bool, str]:
    """R3 AC-2 gate helper for corroborate path.

    Returns ``(ok, reason)``. Dual-provider success always OK. Single-provider
    OK only when ``allow_single_provider_receipt`` and receipt explicitly
    records single_provider clusters (fail-loud otherwise).
    """
    if not receipt.triangulated_rows:
        return False, "no_triangulated_rows"
    if any(r.triangulation_status == "dual_provider" for r in receipt.triangulated_rows):
        return True, "dual_provider"
    if allow_single_provider_receipt and any(
        r.triangulation_status == "single_provider" for r in receipt.triangulated_rows
    ):
        return True, "explicit_single_provider_receipt"
    return False, "corroborate_requires_triangulation_or_single_provider_receipt"
