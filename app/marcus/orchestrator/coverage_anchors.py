"""Step 0 pure core — slide_key reconciliation + anchor projection (FORK A).

The DECK side of the coverage join, ORCHESTRATOR-side and M3-clean (no cross-import
of ``app.specialists`` — the enhanced-vo.1 lineage is REPLICATED here as the minimal
pure mapping, mirroring Irene's ``_slide_id_ordinal`` loader-replication discipline).

Two pure functions, both offline-testable:

* :func:`resolve_slide_key_map` — the PRIMARY ``{final_slide_id: slide_key}`` map from
  the explicit ``slide_briefs.source_ref`` -> ``plan_units`` lineage carrier
  (``slide_key`` = the SOURCE-deck slide ordinal each FINAL segment descends from;
  N clustered sub-slides share one source key). Re-refinement drift (a brief whose
  ``source_ref`` is not in the plan) is OMITTED, never guessed.
* :func:`build_coverage_anchors` — the PURE reconciliation core (Amelia ruling:
  reconciliation is passed IN, NEVER computed from run-state), keyed by the coverage
  ``slide_key`` namespace. The adversarial joins (off-by-one 1/0-based, missing-key
  narration, ambiguous collision, empty inputs) are therefore offline-fixtured. The
  only live seam is the marshalling adapter (``coverage_gate_wiring``) the orchestrator
  finalizes against live shapes.
"""

from __future__ import annotations

import re
from typing import Any

from app.marcus.lesson_plan.coverage_receipt import AnchorResolution

# Trailing-ordinal extractor (replicates irene ``_SLIDE_ID_ORDINAL_RE``; M3-clean copy).
_TRAILING_ORDINAL_RE: re.Pattern[str] = re.compile(r"(\d+)\s*$")


def _slide_id_ordinal(slide_id: Any) -> int | None:
    """1-based ordinal from a segment ``slide_id`` (trailing digit run); else ``None``."""
    match = _TRAILING_ORDINAL_RE.search(str(slide_id or ""))
    return int(match.group(1)) if match else None


def _source_slide_id_for_unit(unit: dict[str, Any]) -> str | None:
    """The SOURCE-deck slide id a plan_unit descends from (M3-clean replica).

    A head IS its own source slide (``unit_id``); an interstitial borrows its head's
    ``parent_slide_id``. An interstitial with NO resolvable parent returns ``None``
    (the caller omits it — the orchestrator-side coverage map degrades to a recorded
    diagnostic rather than the loud ``VoiceDirectionError`` Irene raises; coverage is
    additive, never a run-halting lineage authority).
    """
    unit_id = str(unit.get("unit_id") or "").strip()
    if unit.get("cluster_role") == "interstitial":
        parent = str(unit.get("parent_slide_id") or "").strip()
        return parent or None
    return unit_id or None


def resolve_slide_key_map(plan_units: Any, slide_briefs: Any) -> dict[str, str]:
    """PRIMARY ``{final_slide_id: slide_key}`` from the explicit ``source_ref`` carrier.

    ``slide_key`` is the SOURCE-deck slide ordinal (as a string) each FINAL segment
    descends from. First-wins dedup on both ``plan_units`` (by ``unit_id``) and
    ``slide_briefs`` (by ``slide_id``). A brief whose ``source_ref`` is not in the plan
    (re-refinement drift) is OMITTED. PURE / offline / DATA-only (M3).
    """
    units = plan_units if isinstance(plan_units, list) else []
    unit_by_id: dict[str, dict[str, Any]] = {}
    for unit in units:
        if not isinstance(unit, dict):
            continue
        unit_id = str(unit.get("unit_id") or "").strip()
        if unit_id and unit_id not in unit_by_id:  # first-wins
            unit_by_id[unit_id] = unit

    briefs = slide_briefs if isinstance(slide_briefs, list) else []
    out: dict[str, str] = {}
    for brief in briefs:
        if not isinstance(brief, dict):
            continue
        final_slide_id = str(brief.get("slide_id") or "").strip()
        source_ref = str(brief.get("source_ref") or "").strip()
        if not final_slide_id or not source_ref or final_slide_id in out:
            continue
        unit = unit_by_id.get(source_ref)
        if unit is None:
            continue  # re-refinement drift -> omitted (diagnosed by the caller)
        source_slide_id = _source_slide_id_for_unit(unit)
        ordinal = _slide_id_ordinal(source_slide_id)
        if ordinal is None:
            continue
        out[final_slide_id] = str(ordinal)
    return out


def resolve_slide_key_lineage(plan_units: Any, slide_briefs: Any) -> list[dict[str, str]]:
    """Per-final-slide lineage rows the marshaller's COLLISION GUARD reconciles over.

    Returns ``[{final_slide_id, ordinal, source_slide_id}, …]`` — the SAME
    ``source_ref → plan_units → source-slide ordinal`` lineage as
    :func:`resolve_slide_key_map`, but RETAINING the ``source_slide_id`` (the source
    identity) so the marshaller can tell a LEGITIMATE many-final-to-one-source map
    (clustered sub-slides share a head) from a CROSS-PART COLLISION (two DISTINCT
    source slides whose ids happen to share a trailing ordinal). The guard DECISION
    (which ordinals to omit) stays marshaller-side (R5-A2); this stays PURE / offline /
    DATA-only (M3) so ``coverage_anchors.py`` never owns reconciliation policy.
    """
    units = plan_units if isinstance(plan_units, list) else []
    unit_by_id: dict[str, dict[str, Any]] = {}
    for unit in units:
        if not isinstance(unit, dict):
            continue
        unit_id = str(unit.get("unit_id") or "").strip()
        if unit_id and unit_id not in unit_by_id:  # first-wins
            unit_by_id[unit_id] = unit

    briefs = slide_briefs if isinstance(slide_briefs, list) else []
    out: list[dict[str, str]] = []
    seen_final: set[str] = set()
    for brief in briefs:
        if not isinstance(brief, dict):
            continue
        final_slide_id = str(brief.get("slide_id") or "").strip()
        source_ref = str(brief.get("source_ref") or "").strip()
        if not final_slide_id or not source_ref or final_slide_id in seen_final:
            continue
        unit = unit_by_id.get(source_ref)
        if unit is None:
            continue  # re-refinement drift -> omitted (diagnosed by the caller)
        source_slide_id = _source_slide_id_for_unit(unit)
        ordinal = _slide_id_ordinal(source_slide_id)
        if source_slide_id is None or ordinal is None:
            continue
        seen_final.add(final_slide_id)
        out.append(
            {
                "final_slide_id": final_slide_id,
                "ordinal": str(ordinal),
                "source_slide_id": str(source_slide_id),
            }
        )
    return out


def _deck_row_key(row: dict[str, Any]) -> str | None:
    """The deck row's identity key for the ``slide_key_map`` lookup.

    Prefers ``slide_index`` (the story's deck join axis), normalized to a string so
    a map keyed on either the int or its string form resolves; falls back to
    ``slide_id``.
    """
    if "slide_index" in row and row.get("slide_index") is not None:
        return str(row.get("slide_index"))
    sid = row.get("slide_id")
    return str(sid) if sid else None


def _deck_slide_text(row: dict[str, Any]) -> str:
    """``title\\nbody`` deck-surface text (drops empties; deterministic)."""
    parts = [str(row.get("title") or "").strip(), str(row.get("body") or "").strip()]
    return "\n".join(p for p in parts if p)


def _narration_row_slide_key(row: dict[str, Any]) -> str | None:
    """The narration row's coverage ``slide_key`` (its own ``Slide N`` locator origin).

    Falls back to ``slide_id`` when ``slide_key`` is absent (the flag-OFF case where the
    narration surface carries no explicit coverage key).
    """
    key = str(row.get("slide_key") or "").strip()
    if key:
        return key
    sid = str(row.get("slide_id") or "").strip()
    return sid or None


def _union_text(existing: str | None, incoming: str | None) -> str | None:
    """UNION two surface texts for one shared ordinal (SF1; clustered sub-slides).

    Newline-joins non-empty parts, deduping an exact-equal incoming so a re-derive
    over identical surfaces stays idempotent. Either side ``None``/empty degrades to
    the other; both empty → ``None``.
    """
    parts = [p for p in (existing, incoming) if p and p.strip()]
    if not parts:
        return None
    if len(parts) == 1:
        return parts[0]
    if existing == incoming:
        return existing
    return f"{existing}\n{incoming}"


def _narration_text(row: dict[str, Any]) -> str | None:
    for field in ("narration_text", "text", "narration", "body"):
        val = row.get(field)
        if isinstance(val, str) and val.strip():
            return val
    return None


def build_coverage_anchors(
    gary_slide_content: list[dict[str, Any]] | None,
    joined_narration: list[dict[str, Any]] | None,
    slide_key_map: dict[str, str] | None,
    ambiguous_ordinals: set[str] | frozenset[str] | None,
) -> dict[str, AnchorResolution]:
    """PURE projection of deck + narration surfaces into ``{slide_key: AnchorResolution}``.

    Reconciliation is passed IN (Amelia ruling). Output keyed by the coverage
    ``slide_key`` (string source-ordinal namespace the ``SourcePoint`` carries):

      * DECK side — each deck row's identity key (``slide_index`` when present, else
        ``slide_id``) resolves to a coverage ``slide_key`` via ``slide_key_map``;
        ``slide_text = title + "\\n" + body``. A deck row whose key is NOT in the map
        is skipped (the caller records the unresolved join as a receipt diagnostic;
        never a crash).
      * NARRATION side — ``narration_text`` from the joined row, reconciled to its own
        coverage ``slide_key`` (the component's ``Slide N`` locator origin; falls back
        to ``slide_id`` when ``slide_key`` is absent — the flag-OFF case).
      * ``narration_ambiguous`` — set iff the ``slide_key`` is in ``ambiguous_ordinals``
        (the ``enrichment_consumption.py:335`` 0/>1 role-seed drop, surfaced explicitly).

    SF1 — CLUSTERED SUB-SLIDE UNION: when N FINAL slides share ONE source ordinal
    (a legitimately clustered deck), their ``slide_text`` (and likewise
    ``narration_text``) are UNIONED (newline-joined, deduped), NOT last-write-wins.
    Last-write-wins kept only the LAST sub-slide's text, so a span carried on an
    EARLIER sub-slide read as ``missing`` → a spurious BLOCK that muted the gate.

    Empty inputs -> ``{}``.
    """
    deck_rows = gary_slide_content or []
    narration_rows = joined_narration or []
    key_map = slide_key_map or {}
    ambiguous = set(ambiguous_ordinals or set())

    # Accumulate per coverage slide_key, then freeze into AnchorResolution rows. SF1:
    # text is UNIONED across rows sharing an ordinal (clustered sub-slides) rather than
    # last-write-wins — see ``_union_text``.
    acc: dict[str, dict[str, Any]] = {}

    def _slot(slide_key: str) -> dict[str, Any]:
        return acc.setdefault(
            slide_key,
            {
                "slide_present": False,
                "slide_text": None,
                "narration_present": False,
                "narration_text": None,
            },
        )

    for row in deck_rows:
        if not isinstance(row, dict):
            continue
        deck_key = _deck_row_key(row)
        if deck_key is None:
            continue
        slide_key = key_map.get(deck_key)
        if slide_key is None:  # also try the raw (non-normalized) key form
            slide_key = key_map.get(row.get("slide_index")) if isinstance(key_map, dict) else None
        if not slide_key:
            continue  # unresolved deck join -> caller diagnoses
        slot = _slot(str(slide_key))
        slot["slide_present"] = True
        slot["slide_text"] = _union_text(slot["slide_text"], _deck_slide_text(row))

    for row in narration_rows:
        if not isinstance(row, dict):
            continue
        slide_key = _narration_row_slide_key(row)
        if not slide_key:
            continue
        slot = _slot(str(slide_key))
        slot["narration_present"] = True
        slot["narration_text"] = _union_text(slot["narration_text"], _narration_text(row))

    return {
        slide_key: AnchorResolution(
            slide_key=slide_key,
            slide_present=slot["slide_present"],
            slide_text=slot["slide_text"],
            narration_present=slot["narration_present"],
            narration_ambiguous=slide_key in ambiguous,
            narration_text=slot["narration_text"],
        )
        for slide_key, slot in acc.items()
    }


__all__ = ["build_coverage_anchors", "resolve_slide_key_lineage", "resolve_slide_key_map"]
