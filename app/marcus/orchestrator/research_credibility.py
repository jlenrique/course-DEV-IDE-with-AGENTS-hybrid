"""Evidence-hierarchy credibility classification (Agentic Research Foundations R4).

Maps Texas rows onto the closed tier set in
``docs/dev-guide/research-evidence-hierarchy.md``. Heuristic metadata only —
not a clinical grade of evidence.
"""

from __future__ import annotations

from typing import Any, Literal

EvidenceHierarchyTier = Literal[
    "T1_systematic",
    "T2_peer_rct_or_equiv",
    "T3_peer_observational",
    "T4_peer_other",
    "T5_preprint",
    "T6_grey_institutional",
    "T7_secondary_media",
    "T8_unknown",
]

EVIDENCE_HIERARCHY_TIERS: frozenset[str] = frozenset(
    {
        "T1_systematic",
        "T2_peer_rct_or_equiv",
        "T3_peer_observational",
        "T4_peer_other",
        "T5_preprint",
        "T6_grey_institutional",
        "T7_secondary_media",
        "T8_unknown",
    }
)

_PREPRINT_MARKERS = ("arxiv", "biorxiv", "medrxiv", "ssrn", "preprint")
_SYSTEMATIC_MARKERS = ("systematic review", "meta-analysis", "meta analysis", "guideline")
_RCT_MARKERS = ("randomized", "randomised", "rct", "controlled trial")


def _nested_meta(row: Any) -> dict[str, Any]:
    meta = getattr(row, "provider_metadata", None) or {}
    if not isinstance(meta, dict):
        return {}
    for key in ("scite", "consensus", "jefferson_library"):
        nest = meta.get(key)
        if isinstance(nest, dict):
            return nest
    return {}


def classify_evidence_hierarchy(row: Any) -> tuple[EvidenceHierarchyTier, bool]:
    """Return ``(tier_code, peer_reviewed)`` for a Texas row.

    Never invents T1 without detectable systematic/meta signals. Unknown → T8.
    """
    title = str(getattr(row, "title", "") or "").lower()
    body = str(getattr(row, "body", "") or "").lower()
    nest = _nested_meta(row)
    venue = str(nest.get("venue") or nest.get("journal") or "").lower()
    study = str(nest.get("study_design_tag") or nest.get("study_type") or "").lower()
    blob = f"{title} {body} {venue} {study}"

    if any(marker in blob for marker in _PREPRINT_MARKERS):
        return "T5_preprint", False
    if any(marker in blob for marker in _SYSTEMATIC_MARKERS):
        return "T1_systematic", True
    if any(marker in study for marker in _RCT_MARKERS) or any(
        marker in title for marker in _RCT_MARKERS
    ):
        return "T2_peer_rct_or_equiv", True

    authority = getattr(row, "authority_tier", None)
    if authority == "peer_reviewed":
        return "T4_peer_other", True

    provider = str(getattr(row, "provider", "") or "")
    if provider in {"scite", "consensus"} and venue:
        return "T4_peer_other", True
    if provider in {"scite", "consensus"}:
        # B4c: scite/consensus are indexed-literature providers — a row they
        # return is, by construction, an indexed scholarly record. Do not
        # exclude it purely for a missing venue string. Any non-blank indexed
        # identifier (DOI ``10.x``, PMID digits, or a provider-native paper id)
        # qualifies for the peer-literature default; only a row with no usable
        # identifier at all falls through to T8. (Rows with a blank source_id
        # are already dropped upstream as ``source_invalid``.) Genuine
        # low-credibility exclusion for non-indexed providers is untouched.
        sid = str(getattr(row, "source_id", "") or "").strip()
        if sid:
            return "T4_peer_other", True
        return "T8_unknown", False

    if provider == "jefferson_library":
        return "T4_peer_other", True

    return "T8_unknown", False


def provider_provenance_for_row(row: Any) -> list[str]:
    """Providers that contributed this row (single-provider mint = one entry)."""
    provider = str(getattr(row, "provider", "") or "").strip()
    return [provider] if provider else []


__all__ = [
    "EVIDENCE_HIERARCHY_TIERS",
    "EvidenceHierarchyTier",
    "classify_evidence_hierarchy",
    "provider_provenance_for_row",
]
