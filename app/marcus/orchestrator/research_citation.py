"""Braid S3 — cited-entry minting + G2 citation-fidelity gate (FAIL mode).

This module is the citation-facing half of the S3 research wiring. It:

1. **Mints cited research entries** from accepted ``TexasRow``s with a
   deterministic ``source_ref`` (a pure function of ``(provider, source_id)``)
   and a stable ``source_hash`` (a content hash over the row's identity/body).

2. Runs the **G2 citation-fidelity gate in FAIL mode**: every workbook/run
   citation's ``source_ref`` MUST resolve to a ``TexasRow`` (or corpus source)
   in this run's retrieval set. ``unsourced_citations == 0`` is the gate — a
   single unresolved citation is RED. This is a NEW, citation-facing check; it
   is NOT the warn-only numeric drift rate and must not be conflated with it.

3. Wraps the **L2 ``research_supplements`` channel**: retrieved research figures
   are passed to ``audit_numeric_provenance(..., research_supplements=...)`` so
   they classify as ``research_supplement`` (legitimately-sourced), NOT drift.
   The L2 engine is called READ-ONLY — no signature change, no new state
   (frozen-neck discipline; the warn-only numeric leg is unchanged).

NAMED BOUNDARY (Murat #5 / G1) — do NOT fold into this gate
-----------------------------------------------------------
``unsourced_citations == 0`` is a **resolvability** check: the source EXISTS in
the retrieval set. It does NOT verify the cited source SUPPORTS the attached
claim, nor that it grounds the slide content. Claim↔source *support* faithfulness
is a NAMED operator-gated spot-check (AC-O4), held explicitly OUT of L2. The
semantic claim↔citation audit is a deferred follow-on, never smuggled here.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.marcus.orchestrator.research_credibility import (
    EVIDENCE_HIERARCHY_TIERS,
    classify_evidence_hierarchy,
    provider_provenance_for_row,
)
from app.specialists._shared.source_fidelity_audit import audit_numeric_provenance

logger = logging.getLogger(__name__)


class CitationFidelityError(RuntimeError):
    """Raised by the FAIL-mode gate when ``unsourced_citations > 0``."""

    def __init__(self, message: str, *, unsourced_citations: int) -> None:
        super().__init__(message)
        self.unsourced_citations = unsourced_citations


class CitedResearchEntry(BaseModel):
    """One cited research entry handed to the S2 workbook producer."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    citation_id: str = Field(min_length=1)
    source_ref: str = Field(min_length=1)
    provider: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    title: str = ""
    source_hash: str = Field(min_length=1)
    # R4 credibility surfacing (taxonomy: research-evidence-hierarchy.md)
    evidence_hierarchy_tier: str = "T8_unknown"
    peer_reviewed: bool = False
    provider_provenance: list[str] = Field(default_factory=list)
    triangulation_status: str = "none"
    reliability_score: float | None = None

    @field_validator("evidence_hierarchy_tier")
    @classmethod
    def _tier_closed_set(cls, value: str) -> str:
        if value not in EVIDENCE_HIERARCHY_TIERS:
            raise ValueError(
                f"evidence_hierarchy_tier {value!r} not in closed set "
                f"{sorted(EVIDENCE_HIERARCHY_TIERS)}"
            )
        return value

    @field_validator("provider_provenance")
    @classmethod
    def _provenance_nonempty_when_present(cls, value: list[str]) -> list[str]:
        # Empty list allowed only as pre-mint default; mint_cited_entry always
        # fills at least the row provider. Fail-loud helper enforces post-mint.
        return value


def derive_source_ref(provider: str, source_id: str) -> str:
    """``source_ref`` = the canonical provenance handle for a retrieved row.

    Pure function of ``(provider, source_id)`` — NO invented refs. Deterministic
    and stable across calls so the citation manifest is auditable.
    """
    return f"retrieval:{provider}:{source_id}"


def compute_source_hash(row: Any) -> str:
    """Stable content hash over a ``TexasRow``'s identity + body.

    Deterministic across two calls on the same row (pinned by AC-D5).
    """
    parts = (
        str(getattr(row, "provider", "")),
        str(getattr(row, "source_id", "")),
        str(getattr(row, "title", "")),
        str(getattr(row, "body", "")),
    )
    digest = hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def mint_cited_entry(
    row: Any,
    *,
    citation_index: int,
    triangulation_status: str = "none",
    reliability_score: float | None = None,
    provider_provenance: list[str] | None = None,
) -> CitedResearchEntry:
    """Mint a ``CitedResearchEntry`` from an accepted ``TexasRow``."""
    provider = str(getattr(row, "provider", ""))
    source_id = str(getattr(row, "source_id", ""))
    tier, peer_reviewed = classify_evidence_hierarchy(row)
    provenance = provider_provenance or provider_provenance_for_row(row)
    if not provenance:
        raise ValueError(
            "mint_cited_entry: provider_provenance missing (fail-loud R4)"
        )
    return CitedResearchEntry(
        citation_id=f"cite-{citation_index:03d}",
        source_ref=derive_source_ref(provider, source_id),
        provider=provider,
        source_id=source_id,
        title=str(getattr(row, "title", "")),
        source_hash=compute_source_hash(row),
        evidence_hierarchy_tier=tier,
        peer_reviewed=peer_reviewed,
        provider_provenance=list(provenance),
        triangulation_status=triangulation_status,
        reliability_score=reliability_score,
    )


def assert_credibility_fields(entry: CitedResearchEntry) -> None:
    """R4 fail-loud: required credibility fields must be present and non-vacuous."""
    if entry.evidence_hierarchy_tier not in EVIDENCE_HIERARCHY_TIERS:
        raise ValueError(
            f"missing/invalid evidence_hierarchy_tier on {entry.citation_id}"
        )
    if not entry.provider_provenance:
        raise ValueError(f"missing provider_provenance on {entry.citation_id}")
    if entry.triangulation_status not in {
        "dual_provider",
        "single_provider",
        "none",
    }:
        raise ValueError(
            f"invalid triangulation_status on {entry.citation_id}: "
            f"{entry.triangulation_status!r}"
        )


def apply_triangulation_to_entries(
    entries: list[CitedResearchEntry],
    receipt: Any,
) -> list[CitedResearchEntry]:
    """Overlay triangulation status/score (+ multi-provider provenance) onto entries."""
    clusters = list(getattr(receipt, "triangulated_rows", None) or [])
    if not clusters:
        return list(entries)

    def _title_key(title: str) -> str:
        return " ".join("".join(c if c.isalnum() else " " for c in title.lower()).split())

    by_source: dict[str, Any] = {}
    by_title: dict[str, Any] = {}
    for cluster in clusters:
        for provider, row in (getattr(cluster, "rows_by_provider", None) or {}).items():
            sid = str(getattr(row, "source_id", "") or "")
            if sid:
                by_source[f"{provider}:{sid}"] = cluster
            tk = _title_key(str(getattr(row, "title", "") or ""))
            if len(tk) >= 16:
                by_title[tk] = cluster

    out: list[CitedResearchEntry] = []
    for entry in entries:
        cluster = by_source.get(f"{entry.provider}:{entry.source_id}")
        if cluster is None:
            cluster = by_title.get(_title_key(entry.title))
        if cluster is None:
            out.append(entry)
            continue
        providers = sorted((getattr(cluster, "rows_by_provider", None) or {}).keys())
        out.append(
            entry.model_copy(
                update={
                    "triangulation_status": getattr(
                        cluster, "triangulation_status", entry.triangulation_status
                    ),
                    "reliability_score": getattr(
                        cluster, "reliability_score", entry.reliability_score
                    ),
                    "provider_provenance": providers or list(entry.provider_provenance),
                }
            )
        )
    return out


def build_retrieval_source_refs(rows: list[Any]) -> set[str]:
    """The resolvable ``source_ref`` set for this run's retrieval rows."""
    return {
        derive_source_ref(str(getattr(r, "provider", "")), str(getattr(r, "source_id", "")))
        for r in rows
    }


def count_unsourced_citations(
    citations: list[dict[str, Any]],
    *,
    resolvable_source_refs: set[str],
) -> int:
    """Count citations whose ``source_ref`` does NOT resolve in the retrieval set.

    ``citations`` are run/workbook citation dicts each carrying a ``source_ref``.
    ``resolvable_source_refs`` is the union of this run's retrieval ``source_ref``s
    and any corpus source refs. A citation with a missing/empty/unresolvable
    ``source_ref`` is unsourced.
    """
    unsourced = 0
    for citation in citations:
        source_ref = citation.get("source_ref")
        if not isinstance(source_ref, str) or source_ref not in resolvable_source_refs:
            unsourced += 1
    return unsourced


def gate_citation_fidelity(
    citations: list[dict[str, Any]],
    *,
    resolvable_source_refs: set[str],
) -> int:
    """G2 FAIL-mode gate. Returns ``unsourced_citations``; raises if non-zero.

    This is the ONLY new gating check S3 adds. It is distinct from the warn-only
    numeric ``drift_rate`` (a resolvability count, not a numeric-provenance rate).
    """
    unsourced = count_unsourced_citations(
        citations, resolvable_source_refs=resolvable_source_refs
    )
    if unsourced > 0:
        raise CitationFidelityError(
            f"G2 citation-fidelity FAIL: {unsourced} citation(s) resolve to no "
            f"TexasRow/corpus source in this run's retrieval set",
            unsourced_citations=unsourced,
        )
    return unsourced


def audit_research_supplements(
    narration_text: str,
    source_text: str,
    *,
    retrieved_figures: set[str] | None,
) -> dict:
    """Read-only L2 call routing retrieved figures through ``research_supplements``.

    Retrieved research figures classify as ``research_supplement`` (sanctioned),
    NOT ``unsourced_numeric`` drift. The L2 engine is unchanged — this is a pure
    caller (frozen-neck discipline).
    """
    return audit_numeric_provenance(
        narration_text,
        source_text,
        research_supplements=retrieved_figures or set(),
    )


def build_citation_manifest(
    entries: list[CitedResearchEntry],
) -> list[dict[str, str]]:
    """The ``citation_id → source_ref → source_hash`` manifest for the run record."""
    return [
        {
            "citation_id": e.citation_id,
            "source_ref": e.source_ref,
            "source_hash": e.source_hash,
        }
        for e in entries
    ]


def assemble_l2_citation_report(
    entries: list[CitedResearchEntry],
    *,
    resolvable_source_refs: set[str],
    l2_numeric_report: dict,
) -> dict[str, Any]:
    """Assemble the run-record L2 fail-mode citation report (AC-O2 shape).

    Carries (1) the warn-only L2 numeric report unchanged, (2) the citation
    manifest, and (3) the ``unsourced_citations`` count. The count is computed
    over the minted entries' own ``source_ref``s against the resolvable set, so a
    self-consistent run reports 0.
    """
    citations = [{"source_ref": e.source_ref} for e in entries]
    unsourced = count_unsourced_citations(
        citations, resolvable_source_refs=resolvable_source_refs
    )
    # S2-analogue fix: an un-auditable numeric leg (zero-denominator -> status
    # "FAIL") must NOT be folded in as if it were a clean attachment. Surface the
    # L2 numeric leg's own status at the top level so a consumer can tell a
    # genuinely-clean numeric report from an un-auditable one, AND flag the
    # un-auditable case explicitly so it cannot read as silently-clean.
    l2_numeric_status = (
        l2_numeric_report.get("status")
        if isinstance(l2_numeric_report, dict)
        else None
    )
    return {
        "l2_numeric_report": l2_numeric_report,
        # Hoisted from the numeric report so an un-auditable ("FAIL") numeric leg
        # is visible at the report root, not buried (S2-analogue zero-denominator).
        "l2_numeric_status": l2_numeric_status,
        "l2_numeric_auditable": l2_numeric_status not in {None, "FAIL"},
        "citation_manifest": build_citation_manifest(entries),
        "unsourced_citations": unsourced,
        # Named boundary (Murat #5): resolvability only — NOT support faithfulness.
        "scope_note": (
            "resolvability gate: source_ref resolves to a real retrieved row. "
            "claim<->source SUPPORT faithfulness is the named operator spot-check "
            "(AC-O4), held OUT of L2."
        ),
    }


def find_duplicate_citations(
    entries: list[CitedResearchEntry],
) -> list[tuple[str, str]]:
    """Return the ``(provider, source_id)`` keys that appear on >1 cited entry.

    ``build_retrieval_source_refs`` collapses duplicate ``(provider, source_id)``
    rows into a set, but the minter assigns DISTINCT ``citation_id``s to identical
    refs — so two citations can point at one source. This surfaces those so the
    wiring can de-dup (keep the first) or flag, rather than silently emit twins.
    """
    seen: set[tuple[str, str]] = set()
    dupes: list[tuple[str, str]] = []
    for entry in entries:
        key = (entry.provider, entry.source_id)
        if key in seen and key not in dupes:
            dupes.append(key)
        seen.add(key)
    return dupes


def dedupe_cited_entries(
    entries: list[CitedResearchEntry],
) -> list[CitedResearchEntry]:
    """Drop later entries sharing a ``(provider, source_id)`` with an earlier one.

    First-wins: identical ``source_ref``s collapse to one citation, so the manifest
    carries no duplicate provenance rows.
    """
    seen: set[tuple[str, str]] = set()
    out: list[CitedResearchEntry] = []
    for entry in entries:
        key = (entry.provider, entry.source_id)
        if key in seen:
            continue
        seen.add(key)
        out.append(entry)
    return out


__all__ = [
    "CitationFidelityError",
    "CitedResearchEntry",
    "apply_triangulation_to_entries",
    "assert_credibility_fields",
    "assemble_l2_citation_report",
    "audit_research_supplements",
    "build_citation_manifest",
    "build_retrieval_source_refs",
    "compute_source_hash",
    "count_unsourced_citations",
    "dedupe_cited_entries",
    "derive_source_ref",
    "find_duplicate_citations",
    "gate_citation_fidelity",
    "mint_cited_entry",
]
