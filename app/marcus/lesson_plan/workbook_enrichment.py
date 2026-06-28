"""P5-S1 — project the frozen G0 enriched corpus into workbook producer inputs.

This is the **consumption layer** that closes the P5 loop: it READS the frozen,
operator-confirmed ``G0EnrichmentResult`` card payload (P1 typed_components +
P2 citation_resolutions + P3 pedagogy_annotations + provisional_los) and projects
it into the producer's render inputs so the learner-facing workbook is genuinely
SHAPED BY the enriched corpus rather than by hardcoded constants.

HONESTY BAR (Irene): a field is honestly consumed iff changing it changes the
rendered artifact. This module shapes the deliverable with TWO fields from TWO
passes: the P2 citation ``access_url`` (further-reading link) AND the P3 pedagogy
``bloom`` (exercise + learning-objective level).

RENDER GATE (Texas — most-restrictive-wins AND-conjunction):
    A citation renders an AUTHORITATIVE link IFF
        teachable == True              (P3, from the component's annotation)
      AND resolution_status == "resolved"
      AND resolved_ref["access_url"] is truthy.
    A ``resolved`` citation on a ``teachable == False`` component is a COHERENCE
    BREACH: it is SUPPRESSED and a hard diagnostic is emitted (logger.error —
    never a silent drop). ``failed`` / ``ungrounded`` citations never produce a
    clickable/authoritative URL (they are omitted; never a fabricated bare URL).

P5-RO READ-ONLY INVARIANT: this layer makes ZERO retrieval/network/model calls.
It READS the frozen verdict (the single source of truth) — no scite re-resolve,
no OpenAI. The byte-exact ``access_url`` is used VERBATIM; a DOI is NEVER
re-constructed into ``https://doi.org/{doi}`` here.

Dependency arrow (Winston): this module is lesson_plan-INTERNAL. It imports only
the low-level lesson_plan content models (``collateral_spec`` /
``workbook_producer``); it MUST NOT import ``app.marcus.orchestrator`` or any
``app.*.gates`` module (the specialist act imports THIS, never the reverse). The
trivial on-disk read is replicated here (rather than reusing the orchestrator's
``load_enrichment_result``) precisely to honor import-linter Contract M3
(``app.specialists`` may not import ``app.marcus.orchestrator``).
"""

from __future__ import annotations

import hashlib
import json
import logging
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.marcus.lesson_plan.collateral_spec import (
    DepthDeltaContract,
    Exercise,
    WorkbookSection,
    WorkbookSpec,
)
from app.marcus.lesson_plan.g0_enrichment import (
    ENRICHMENT_CARD_BASENAME as _SHARED_ENRICHMENT_CARD_BASENAME,
)
from app.marcus.lesson_plan.workbook_producer import (
    FurtherReadingEntry,
    LearningObjectiveBrief,
)

logger = logging.getLogger(__name__)

# The frozen public card payload the G0E decision card reads. SINGLE-SOURCED
# (Winston A2) from ``app.marcus.lesson_plan.g0_enrichment`` — the same basename
# the orchestrator loader uses — re-exported here so existing importers of
# ``workbook_enrichment.ENRICHMENT_CARD_BASENAME`` are unchanged. Sourced from the
# lesson_plan model module (NOT app.marcus.orchestrator) to honor Contract M3.
ENRICHMENT_CARD_BASENAME = _SHARED_ENRICHMENT_CARD_BASENAME

_DEFAULT_BLOOM = "understand"
_TITLE_MAX_CHARS = 160


@dataclass(frozen=True)
class WorkbookEnrichmentProjection:
    """The enriched producer inputs projected from the frozen G0 card payload.

    Drop-in replacements for the slots the enriched corpus covers: the
    ``spec`` (sections + Bloom-leveled exercises), the ``learning_objectives``
    (provisional LO statements + per-LO Bloom from the pedagogy overlay), the
    ``further_reading`` (gated, byte-exact citation links), and the G2
    citation/manifest pair. Segments / source_text / vo_script remain the
    producer's run-dir inputs (the enriched corpus does not displace them).
    """

    spec: WorkbookSpec
    learning_objectives: tuple[LearningObjectiveBrief, ...]
    further_reading: tuple[FurtherReadingEntry, ...]
    answer_keys: dict[str, str]
    citations: tuple[dict[str, str], ...]
    source_ref_manifest: dict[str, str]


# ---------------------------------------------------------------------------
# Loader (trivial on-disk read; READ-ONLY)
# ---------------------------------------------------------------------------


def load_enrichment_card(run_dir: Path) -> dict[str, Any] | None:
    """Read the frozen ``<run_dir>/g0-enrichment.json`` card payload (or None).

    READ-ONLY: returns the public card-payload dict
    (``G0EnrichmentResult.to_card_payload()`` shape) or ``None`` when the run
    carries no enrichment artifact (backward-compatible non-enrichment runs).
    Never raises on a missing/corrupt artifact — absence falls back to the
    constant producer path.
    """
    artifact = run_dir / ENRICHMENT_CARD_BASENAME
    if not artifact.is_file():
        return None
    try:
        decoded = json.loads(artifact.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return decoded if isinstance(decoded, dict) else None


# ---------------------------------------------------------------------------
# The render gate (Deliverable 2) — airtight AND-conjunction
# ---------------------------------------------------------------------------


def citation_renders_authoritative(
    *,
    teachable: bool,
    resolution_status: Any,
    resolved_ref: dict[str, Any] | None,
) -> bool:
    """Texas's 6-condition gate as a most-restrictive-wins AND-conjunction.

    Returns True iff an AUTHORITATIVE (clickable, real) citation link may render:
    ``teachable`` (P3) AND ``resolution_status == "resolved"`` (P2) AND a truthy
    ``resolved_ref["access_url"]``. Any failing conjunct → no authoritative link.
    """
    return bool(
        teachable is True
        and resolution_status == "resolved"
        and (resolved_ref or {}).get("access_url")
    )


def _teachable_for(component_id: str, annotation_by_id: dict[str, dict[str, Any]]) -> bool:
    """The P3 teachable verdict for a component (default True when un-annotated).

    Read VERBATIM from ``pedagogy_annotations`` (P3 already derived it from the
    front-matter resolution_status — NEVER recomputed from citation_resolutions
    here). A component with no annotation (e.g. a reference_citation, which P3
    does not annotate) carries no suppression signal, so it defaults to teachable
    — the citation rides on its resolution verdict + access_url, not on a P3 gate.
    """
    ann = annotation_by_id.get(component_id)
    if ann is None:
        return True
    return ann.get("teachable") is True


# ---------------------------------------------------------------------------
# Projection (Deliverable 1)
# ---------------------------------------------------------------------------


def _as_card_payload(card: Any) -> dict[str, Any]:
    """Accept a card-payload dict OR a parsed G0EnrichmentResult (duck-typed)."""
    if hasattr(card, "to_card_payload"):
        return card.to_card_payload()
    if isinstance(card, dict):
        return card
    raise TypeError(
        "project_enrichment_to_workbook_inputs expects a card-payload dict or a "
        f"G0EnrichmentResult; got {type(card).__name__}"
    )


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _project_further_reading(
    citation_resolutions: list[dict[str, Any]],
    annotation_by_id: dict[str, dict[str, Any]],
) -> tuple[FurtherReadingEntry, ...]:
    """One gated, byte-exact FurtherReadingEntry per AUTHORITATIVE citation.

    Non-authoritative citations (failed / ungrounded / teachable-False) are
    OMITTED (never a fabricated bare URL). A ``resolved`` citation on a
    ``teachable == False`` component is the COHERENCE BREACH: suppressed + a hard
    ``logger.error`` diagnostic (defense-in-depth; never silent).
    """
    entries: list[FurtherReadingEntry] = []
    for cit in citation_resolutions:
        cid = str(cit.get("component_id") or "")
        status = cit.get("resolution_status")
        resolved_ref = cit.get("resolved_ref") or {}
        access_url = resolved_ref.get("access_url")
        ann = annotation_by_id.get(cid)
        teachable = _teachable_for(cid, annotation_by_id)

        # COHERENCE BREACH: a real resolved+linkable citation hung on a component
        # P3 marked NOT teachable. Suppress AND alarm (never silent-drop).
        if (
            status == "resolved"
            and access_url
            and ann is not None
            and ann.get("teachable") is not True
        ):
            logger.error(
                "P5 coherence breach: resolved citation %r (access_url=%r) hangs on "
                "a teachable=False component; suppressing the authoritative link",
                cid,
                access_url,
            )
            continue

        if not citation_renders_authoritative(
            teachable=teachable,
            resolution_status=status,
            resolved_ref=resolved_ref,
        ):
            # failed / ungrounded / non-teachable -> no authoritative URL.
            continue

        title = str(resolved_ref.get("title") or cid)
        entries.append(
            FurtherReadingEntry(
                citation_id=cid,
                title=title,
                source_ref=cid,
                # P5-RO: the frozen access_url VERBATIM; never re-built from doi.
                locator=resolved_ref["access_url"],
                supports_segment_id=None,
            )
        )
    return tuple(entries)


def _lo_bloom_map(annotations: list[dict[str, Any]]) -> dict[str, str]:
    """objective_id -> Bloom (first annotation referencing the LO wins; stable)."""
    out: dict[str, str] = {}
    for ann in annotations:
        bloom = ann.get("bloom")
        if not bloom:
            continue
        for ref in ann.get("lo_refs") or ():
            out.setdefault(str(ref), str(bloom))
    return out


def _project_exercises(
    typed_components: list[dict[str, Any]],
    annotation_by_id: dict[str, dict[str, Any]],
    surfaced_ids: list[str],
) -> tuple[dict[str, list[Exercise]], dict[str, str]]:
    """Quiz components x their pedagogy annotation -> Bloom-leveled exercises.

    Each ``quiz`` typed-component with a pedagogy annotation becomes one
    :class:`Exercise` whose ``bloom_level`` is the annotation's Bloom and whose
    answer-key reference is the annotation's ``assessment_link`` (the assessed
    target) falling back to the first served LO. Render gate: a ``teachable ==
    False`` quiz is SUPPRESSED (no exercise). Returns (exercises grouped by the
    home-section objective_id, answer_keys).
    """
    surfaced = set(surfaced_ids)
    by_section: dict[str, list[Exercise]] = defaultdict(list)
    answer_keys: dict[str, str] = {}
    for comp in typed_components:
        if comp.get("source_type") != "quiz":
            continue
        cid = str(comp.get("component_id") or "")
        ann = annotation_by_id.get(cid)
        if ann is None:
            continue  # no pedagogy overlay -> no Bloom to consume; skip
        if ann.get("teachable") is not True:
            continue  # render gate: suppress a non-teachable exercise
        lo_refs = [str(r) for r in (ann.get("lo_refs") or ())]
        assessed = ann.get("assessment_link")
        answer_ref = str(assessed) if assessed else (lo_refs[0] if lo_refs else cid)
        exercise = Exercise(
            exercise_id=cid,
            bloom_level=ann["bloom"],  # type: ignore[arg-type]
            prompt_intent=str(comp.get("excerpt") or comp.get("label") or cid),
            answer_key_source_ref=answer_ref,
        )
        # Home section: the first served LO that is surfaced, else the first LO.
        home = next((r for r in lo_refs if r in surfaced), None) or (
            surfaced_ids[0] if surfaced_ids else cid
        )
        by_section[home].append(exercise)
        answer_keys[cid] = (
            f"Worked answer is grounded by source_ref `{answer_ref}` "
            "(P3-linked assessment target)."
        )
    return dict(by_section), answer_keys


def project_enrichment_to_workbook_inputs(card: Any) -> WorkbookEnrichmentProjection:
    """Project the frozen G0 enriched card payload into workbook producer inputs.

    Maps:
      * P2 ``citation_resolutions`` -> gated, byte-exact ``further_reading``;
      * ``quiz`` ``typed_components`` x P3 ``pedagogy_annotations`` -> Bloom-leveled
        ``Exercise`` objects (suppressed when not teachable);
      * ``provisional_los`` + P3 ``lo_refs``/``bloom`` -> ``LearningObjectiveBrief``
        + one bound :class:`WorkbookSection` per LO (carrying its exercises).

    Pure + offline + deterministic (READ-ONLY over the frozen verdict).
    """
    payload = _as_card_payload(card)
    typed_components = list(payload.get("typed_components") or [])
    provisional_los = list(payload.get("provisional_los") or [])
    citation_resolutions = list(payload.get("citation_resolutions") or [])
    annotations = list(payload.get("pedagogy_annotations") or [])
    annotation_by_id = {
        str(a.get("component_id")): a for a in annotations if a.get("component_id")
    }

    # --- Learning objectives (statement from P0/P1; Bloom from the P3 overlay) ---
    bloom_map = _lo_bloom_map(annotations)
    surfaced_ids = [str(lo.get("objective_id")) for lo in provisional_los if lo.get("objective_id")]
    lo_briefs = tuple(
        LearningObjectiveBrief(
            objective_id=str(lo["objective_id"]),
            bloom_level=bloom_map.get(str(lo["objective_id"]), _DEFAULT_BLOOM),
            statement=str(lo.get("statement") or ""),
        )
        for lo in provisional_los
        if lo.get("objective_id")
    )

    # --- Exercises (quiz components x P3 annotation), grouped by home section ---
    exercises_by_section, answer_keys = _project_exercises(
        typed_components, annotation_by_id, surfaced_ids
    )

    # --- Sections: one per surfaced LO (bound 1:1 so S1 binding is exact) ---
    sections: list[WorkbookSection] = []
    for lo in provisional_los:
        oid = lo.get("objective_id")
        if not oid:
            continue
        oid = str(oid)
        statement = str(lo.get("statement") or oid)
        sections.append(
            WorkbookSection(
                section_id=f"sec-{oid}",
                learning_objective_id=oid,
                title=statement[:_TITLE_MAX_CHARS] or oid,
                depth_delta=DepthDeltaContract(
                    deferred_from_slide=oid,
                    deferred_depth=(
                        f"Workbook-deferred depth for {oid}: {statement} "
                        "(read-channel companion to the glance deck)."
                    ),
                ),
                exercises=exercises_by_section.get(oid, []),
                narrative_intent=statement,
            )
        )
    spec = WorkbookSpec(sections=sections)

    # --- Further reading (gated, byte-exact) + the G2 manifest/citation pair ---
    further_reading = _project_further_reading(citation_resolutions, annotation_by_id)
    source_ref_manifest = {e.source_ref: _hash(e.title) for e in further_reading}
    citations = tuple({"source_ref": e.source_ref} for e in further_reading)

    return WorkbookEnrichmentProjection(
        spec=spec,
        learning_objectives=lo_briefs,
        further_reading=further_reading,
        answer_keys=answer_keys,
        citations=citations,
        source_ref_manifest=source_ref_manifest,
    )


__all__ = [
    "ENRICHMENT_CARD_BASENAME",
    "WorkbookEnrichmentProjection",
    "citation_renders_authoritative",
    "load_enrichment_card",
    "project_enrichment_to_workbook_inputs",
]
