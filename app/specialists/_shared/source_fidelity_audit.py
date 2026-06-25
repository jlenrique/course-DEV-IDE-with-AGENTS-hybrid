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

    The semantic-coverage leg and any tripwire threshold are NOT implemented in
    this module — see ``SEMANTIC_TRIPWIRE`` below. They are deliberately deferred
    until >=3 tracked runs exist so a "trends up" claim is falsifiable.

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
]

# Semantic-coverage tripwire threshold. NOT tuned — the semantic leg is
# measurement-only and explicitly non-gating until >=3 tracked runs exist (F1).
# Keeping this `None` makes a future "net-new trends up run-over-run" claim
# falsifiable: there is no number to relitigate, only a documented absence.
SEMANTIC_TRIPWIRE = None  # not tuned until >=3 runs


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
            "unsourced_framing": {
                "count": 0,
                "items": [],
                "note": (
                    "STUB — numeric leg leaves this empty; the future semantic "
                    "leg populates framing/structure elaboration here."
                ),
            },
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
        # F3 STUB: numeric leg never populates this; the report schema carries it
        # so the semantic leg can fill framing/structure elaboration later.
        "unsourced_framing": {
            "count": 0,
            "items": [],
            "note": (
                "STUB — numeric leg leaves this empty; the future semantic leg "
                "populates framing/structure elaboration here (sanctioned "
                "composition, NOT drift)."
            ),
        },
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
