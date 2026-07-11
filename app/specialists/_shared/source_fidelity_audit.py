"""L2 source-provenance audit — numeric leg (WARN-ONLY, NON-GATING, EXPERIMENTAL).

This module measures how faithfully a delivered narration's *numeric* assertions
trace to the *source corpus*. It is the downstream "safety net" of the
source-fidelity QA layer (spec
`_bmad-output/implementation-artifacts/spec-fidelity-qa-qc-source-provenance.md`).

WARN-ONLY CONTRACT (binding party amendment F1, John+Murat):
    `audit_numeric_provenance` only ever RETURNS a report dict. It NEVER raises
    or blocks on drift. Drift is *measured and reported*, not gated. The only
    failure condition is a zero-denominator guard (F2): if either narration OR
    source yields zero numeric tokens, the report `status` is "FAIL" because the
    audit cannot be performed (not a misleading clean PASS).

    The semantic-coverage leg is a **WARN-only heuristic tripwire** (see
    ``SEMANTIC_TRIPWIRE`` / ``audit_semantic_framing``). It reports candidate
    framing sentences; it NEVER gates production. Claim fence: pipeline +
    disposition only — not comprehensive semantic claim↔source faithfulness.

FROZEN NECK (binding party amendment F4, Winston):
    This module is a *pure read-only caller* of
    ``app.specialists._shared.figure_tokens._figures`` /
    ``_normalize_figure``. It imports and calls them; it makes ZERO edits to
    ``figure_tokens.py`` (no signature change, no new state). Any extra
    extraction (e.g. named-entity provenance) is built HERE, never by mutating
    the frozen neck (now 3 readers).

ORTHOGONAL TO G5 (binding party amendment F5, Winston):
    This is a SOURCE-facing layer. It is orthogonal to the slide-facing G5
    figure detector and the chosen-variant figure-citation gate (different
    referent: source corpus vs rendered slide; different lifecycle: warn-first).
    G5 + the figure-citation gate are UNTOUCHED.
"""

from __future__ import annotations

import re

from app.specialists._shared.figure_tokens import _figures, _normalize_figure

__all__ = [
    "SEMANTIC_TRIPWIRE",
    "audit_numeric_provenance",
    "audit_semantic_framing",
]

# WARN-only semantic disposition (TRAIL trio 2026-07-10 party MUST).
# Non-None so the pipeline + disposition are falsifiable; still NEVER gates
# production. Claim fence: heuristic framing candidates only — not a
# comprehensive semantic claim↔source audit.
SEMANTIC_TRIPWIRE: dict[str, object] = {
    "mode": "warn_only",
    "gates_production": False,
    "disposition": "pipeline_and_disposition",
    "version": "v0-heuristic-2026-07-10",
    "claim_fence": (
        "Reports candidate framing sentences that look like claims without "
        "citation anchors and with weak lexical overlap to the source corpus. "
        "Does NOT assert comprehensive semantic claim↔source faithfulness."
    ),
}

_CLAIM_CUE_RE = re.compile(
    r"\b("
    r"causes?|caused|leads?\s+to|results?\s+in|increases?|decreases?|"
    r"associated\s+with|significantly|more\s+than|less\s+than|"
    r"proves?|demonstrates?|shows\s+that|indicates?\s+that"
    r")\b",
    re.IGNORECASE,
)
_CITATION_ANCHOR_RE = re.compile(
    r"("
    r"\[\d+\]|"
    r"\(cite[:\s]|"
    r"doi:\s*10\.\d{4,9}/|"
    r"10\.\d{4,9}/[^\s]+|"
    r"\([A-Z][A-Za-z\-]+(?:\s+et\s+al\.)?,?\s+\d{4}\)"
    r")",
)
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
_WORD_RE = re.compile(r"[A-Za-z][A-Za-z\-']{2,}")
_STOP = frozenset(
    {
        "the",
        "and",
        "for",
        "that",
        "this",
        "with",
        "from",
        "are",
        "was",
        "were",
        "been",
        "have",
        "has",
        "had",
        "not",
        "but",
        "than",
        "more",
        "less",
        "into",
        "onto",
        "over",
        "under",
        "about",
        "their",
        "there",
        "which",
        "while",
        "when",
        "where",
        "what",
        "who",
        "how",
        "why",
        "also",
        "only",
        "such",
        "then",
        "they",
        "them",
        "these",
        "those",
        "through",
        "between",
        "among",
        "using",
        "used",
        "use",
        "can",
        "may",
        "might",
        "will",
        "would",
        "should",
        "could",
        "does",
        "did",
        "doing",
        "very",
        "just",
    }
)


def audit_semantic_framing(
    narration_text: str,
    source_text: str,
) -> dict:
    """Heuristic WARN-only framing candidates (not a full semantic audit).

    Returns a report fragment for ``unsourced_framing``. Never raises; never
    implies production FAIL. Empty narration/source → empty items (numeric
    zero-denominator guard remains the FAIL path).
    """
    items: list[dict] = []
    narration = (narration_text or "").strip()
    source = (source_text or "").strip()
    if not narration or not source:
        return {
            "count": 0,
            "items": [],
            "note": (
                "WARN-only semantic framing leg: empty narration or source — "
                "no framing candidates scored. "
                + str(SEMANTIC_TRIPWIRE["claim_fence"])
            ),
            "disposition": SEMANTIC_TRIPWIRE,
        }

    source_words = {
        w.lower()
        for w in _WORD_RE.findall(source)
        if w.lower() not in _STOP
    }
    for sentence in _SENTENCE_SPLIT_RE.split(narration):
        text = sentence.strip()
        if len(text) < 24:
            continue
        if not _CLAIM_CUE_RE.search(text):
            continue
        if _CITATION_ANCHOR_RE.search(text):
            continue
        content = [
            w.lower()
            for w in _WORD_RE.findall(text)
            if w.lower() not in _STOP
        ]
        if len(content) < 3:
            continue
        overlap = sum(1 for w in content if w in source_words)
        overlap_ratio = overlap / len(content)
        if overlap_ratio >= 0.35:
            continue
        items.append(
            {
                "sentence": text,
                "reason": "claim_cue_without_citation_anchor_and_weak_source_overlap",
                "overlap_ratio": round(overlap_ratio, 3),
                "severity": "warn_only",
            }
        )

    return {
        "count": len(items),
        "items": items,
        "note": (
            "WARN-only semantic framing leg populated by heuristic tripwire; "
            "does not gate production. "
            + str(SEMANTIC_TRIPWIRE["claim_fence"])
        ),
        "disposition": SEMANTIC_TRIPWIRE,
    }


def _normalized_token_map(text: str) -> dict[str, set[str]]:
    """Map each normalized figure -> the set of raw surface forms producing it.

    Read-only caller of the frozen-neck extractor: we re-run the same
    ``_FIGURE_RE`` indirectly via ``_figures`` for the normalized set, and walk
    the raw matches ourselves (in THIS module) to keep the offending surface
    forms for the witness report. ``figure_tokens.py`` is never mutated.
    """
    surface_by_norm: dict[str, set[str]] = {}
    # _figures() gives us the canonical normalized set (frozen-neck contract).
    for norm in _figures(text):
        surface_by_norm.setdefault(norm, set())
    # Recover raw surface forms (witness data) by re-walking with the same regex
    # object exported from the neck — read-only access, no mutation.
    from app.specialists._shared.figure_tokens import _FIGURE_RE

    for match in _FIGURE_RE.finditer(text):
        raw = match.group(0).strip()
        norm = _normalize_figure(raw)
        surface_by_norm.setdefault(norm, set()).add(raw)
    return surface_by_norm


def _normalize_supplements(research_supplements: set[str] | None) -> dict[str, str]:
    """Normalize declared research-supplement tokens -> their declared surface form.

    Supplements may be declared as raw figures (e.g. "$4.5 trillion"). We
    normalize each via the frozen neck so classification matches on the same
    canonical key space as narration/source.
    """
    if not research_supplements:
        return {}
    out: dict[str, str] = {}
    for raw in research_supplements:
        out[_normalize_figure(raw.strip())] = raw.strip()
    return out


def audit_numeric_provenance(
    narration_text: str,
    source_text: str,
    *,
    research_supplements: set[str] | None = None,
) -> dict:
    """Classify every numeric token in ``narration_text`` against the source corpus.

    WARN-ONLY / NON-GATING: returns a report; never raises on drift.

    Provenance classification per narration numeric token (normalized form):
      - ``source_derived``       : normalized form present in source's token set.
      - ``research_supplement``  : normalized form in the declared
                                   ``research_supplements`` set (and NOT counted
                                   as drift).
      - ``unsourced_numeric``    : neither in source nor a declared supplement —
                                   the credibility risk.

    F3 (Mary): ``unsourced`` is split from day one. This numeric leg only
    populates ``unsourced_numeric``. The report carries a sibling
    ``unsourced_framing`` STUB (empty here) so the future semantic leg can
    populate framing/structure elaboration without lumping it with numeric drift.

    F2 (Murat): the report is a real witness — it carries non-zero-denominator
    guards, per-token classification with offending value pairs, a computed
    drift rate, and the three buckets explicitly counted (incl. an
    empty-but-present research-supplement section).

    Returns a JSON-serializable dict.
    """
    narration_map = _normalized_token_map(narration_text)
    source_map = _normalized_token_map(source_text)
    supplement_map = _normalize_supplements(research_supplements)

    narration_token_count = len(narration_map)
    source_token_count = len(source_map)

    # ---- F2 zero-denominator guard: cannot audit with no tokens -> FAIL ----
    framing = audit_semantic_framing(narration_text, source_text)
    if narration_token_count == 0 or source_token_count == 0:
        return {
            "status": "FAIL",
            "non_gating": True,
            "experimental": True,
            "reason": (
                "zero-denominator: cannot audit numeric provenance with "
                f"narration_token_count={narration_token_count}, "
                f"source_token_count={source_token_count}"
            ),
            "narration_token_count": narration_token_count,
            "source_token_count": source_token_count,
            "drift_rate": None,
            "buckets": {
                "source_derived": {"count": 0, "tokens": []},
                "research_supplement": {"count": 0, "tokens": []},
                "unsourced_numeric": {"count": 0, "pairs": []},
            },
            "unsourced_framing": framing,
            "classifications": [],
            "semantic_tripwire": SEMANTIC_TRIPWIRE,
        }

    source_norms = set(source_map.keys())

    source_derived_tokens: list[str] = []
    research_supplement_tokens: list[str] = []
    unsourced_pairs: list[dict] = []
    classifications: list[dict] = []

    for norm, surfaces in sorted(narration_map.items()):
        surface_list = sorted(surfaces)
        primary_surface = surface_list[0] if surface_list else norm

        if norm in source_norms:
            provenance = "source_derived"
            source_derived_tokens.append(norm)
            classifications.append(
                {
                    "token": primary_surface,
                    "normalized": norm,
                    "provenance": provenance,
                }
            )
        elif norm in supplement_map:
            provenance = "research_supplement"
            research_supplement_tokens.append(norm)
            classifications.append(
                {
                    "token": primary_surface,
                    "normalized": norm,
                    "provenance": provenance,
                    "declared_as": supplement_map[norm],
                }
            )
        else:
            provenance = "unsourced_numeric"
            # Offending pair (F2): the unsourced narration token + the nearest
            # plausible source token of the same *kind* (e.g. money-trillion),
            # if one is determinable, else None.
            nearest = _nearest_source_token(norm, source_map)
            pair = {
                "narration_token": primary_surface,
                "narration_normalized": norm,
                "nearest_source_token": (
                    sorted(source_map[nearest])[0] if nearest else None
                ),
                "nearest_source_normalized": nearest,
            }
            unsourced_pairs.append(pair)
            classifications.append(
                {
                    "token": primary_surface,
                    "normalized": norm,
                    "provenance": provenance,
                    "nearest_source_token": pair["nearest_source_token"],
                }
            )

    unsourced_count = len(unsourced_pairs)
    drift_rate = unsourced_count / narration_token_count

    return {
        # WARN-ONLY: never blocks. status reflects auditability, not drift.
        "status": "AUDIT",
        "non_gating": True,
        "experimental": True,
        "narration_token_count": narration_token_count,
        "source_token_count": source_token_count,
        # drift_rate = unsourced_numeric / narration_token_count (F2).
        "drift_rate": drift_rate,
        "buckets": {
            "source_derived": {
                "count": len(source_derived_tokens),
                "tokens": source_derived_tokens,
            },
            # Empty-but-present from day one (F2 + research seam).
            "research_supplement": {
                "count": len(research_supplement_tokens),
                "tokens": research_supplement_tokens,
            },
            "unsourced_numeric": {
                "count": unsourced_count,
                "pairs": unsourced_pairs,
            },
        },
        # F3: semantic framing leg (WARN-only tripwire; never gates).
        "unsourced_framing": framing,
        "classifications": classifications,
        "semantic_tripwire": SEMANTIC_TRIPWIRE,
    }


def _nearest_source_token(
    narration_norm: str, source_map: dict[str, set[str]]
) -> str | None:
    """Best-effort nearest source token of the SAME KIND for the witness pair.

    "Kind" is the normalized prefix the frozen neck emits (``money-trillion:``,
    ``money-bare:``, ``percent:``, ``multiple:``). Among same-kind source
    tokens, pick the numerically closest. Returns the source normalized key, or
    None if no same-kind source token exists.
    """
    kind = _kind_of(narration_norm)
    n_val = _value_of(narration_norm)
    if kind is None or n_val is None:
        return None

    best_key: str | None = None
    best_dist: float | None = None
    for src_norm in source_map:
        if _kind_of(src_norm) != kind:
            continue
        s_val = _value_of(src_norm)
        if s_val is None:
            continue
        dist = abs(s_val - n_val)
        if best_dist is None or dist < best_dist:
            best_dist = dist
            best_key = src_norm
    return best_key


_KIND_RE = re.compile(r"^([a-z-]+):")


def _kind_of(norm: str) -> str | None:
    match = _KIND_RE.match(norm)
    return match.group(1) if match else None


def _value_of(norm: str) -> float | None:
    if ":" not in norm:
        return None
    tail = norm.split(":", 1)[1]
    try:
        return float(tail)
    except ValueError:
        return None
