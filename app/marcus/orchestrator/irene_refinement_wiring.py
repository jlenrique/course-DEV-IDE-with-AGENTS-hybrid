"""Irene-refinement runner-wired orchestration hook (Story G0-S3).

After operator confirm-gate #1 (G0E) confirms the typed manifest + provisional
Learning Objectives, this brick:

  1. CONSUMES the gate-#1-confirmed provisional ``LearningObjective``s (read from
     the frozen S2 ``g0-enrichment.json`` in the run dir);
  2. REFINES each in place (``provisional -> refined``; same ``objective_id``)
     with a populated ``bloom_level`` + an ADVISORY :class:`SourceAdequacy`;
  3. emits the **signed LO-delta contract** (all channels + count reconciliation,
     NO silent drops) frozen to ``<run_dir>/irene-refinement.json``;
  4. feeds operator ratify-gate #2 (``G0R``), where the operator verdict (never the
     model) advances ``refined -> ratified``.

ATTACH MECHANIC (mirrors the S2 g0-enrichment brick exactly)
------------------------------------------------------------
Adds an ``irene-refinement`` orchestration node + a ``g0-ratify-gate`` (``G0R``)
pause gate to the manifest (topology refinement within the v4.2 lineage; pack/HUD
invisible). The runner invokes THIS hook at the ``irene-refinement`` node id, then
pauses at the ``G0R`` gate that follows.

TWO-WALK PARITY (memory ``project_production_runner_two_walks``)
---------------------------------------------------------------
The node sits BEFORE node ``01`` (after the G0E gate), so on the trial path it
fires on the START walk; the side-effect is present in BOTH walk bodies (start +
continuation/recover) so a resume/recover re-entry before the ``G0R`` gate also
produces the artifact. Wiring one walk only is the silent-no-op bug.

FEATURE FLAG
------------
Consistent with S2: the brick is active EXACTLY when the G0-enrichment brick is
active (``MARCUS_G0_ENRICHMENT_ACTIVE``) — refinement cannot run without the
provisional LOs the enrichment brick confirms at gate #1. With the flag UNSET the
``irene-refinement`` node is a no-op pass and the ``G0R`` gate is traversed.

OFFLINE GUARD
-------------
Live refinement calls ``make_chat_model("marcus")`` (the ``pre_gate_marcus`` seam,
``irene-refinement.j2``). Offline/test runs use the deterministic refinement; the
operator-gated live toggle reuses S2's ``MARCUS_G0_DISPATCH_LIVE``.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any
from uuid import UUID

from app.marcus.lesson_plan.irene_refinement import (
    REFINEMENT_LIVE_MODEL_ID,
    REFINEMENT_MODEL_MARKER,
    IreneRefinementResult,
    build_refinement_result,
)
from app.marcus.lesson_plan.learning_objective import LearningObjective
from app.marcus.orchestrator import g0_enrichment_wiring
from app.models.runtime.production_envelope import ProductionEnvelope, SpecialistContribution

logger = logging.getLogger(__name__)

# Runner-wired at this manifest node id (mirrors G0_ENRICHMENT_NODE_ID).
IRENE_REFINEMENT_NODE_ID = "irene-refinement"
IRENE_REFINEMENT_NODE_IDS: frozenset[str] = frozenset({IRENE_REFINEMENT_NODE_ID})
IRENE_REFINEMENT_GATE_CODE = "G0R"

# Dedicated contribution identity (canonicalizes to "irene_refinement").
IRENE_REFINEMENT_SPECIALIST_ID = "irene_refinement"
IRENE_REFINEMENT_MODEL_MARKER = REFINEMENT_MODEL_MARKER
IRENE_REFINEMENT_LIVE_MODEL_ID = REFINEMENT_LIVE_MODEL_ID

# Thin contract key (the frozen refinement result on the contribution output).
REFINEMENT_RESULT_KEY = "irene_refinement_result"

_DECISION_ARTIFACT_BASENAME = "irene-refinement.json"
_CACHE_DIRNAME = "irene-refinement-cache"


def irene_refinement_active() -> bool:
    """Active EXACTLY when the G0-enrichment brick is woken (feature-flag parity, S2).

    Refinement consumes the provisional LOs the enrichment brick confirms at gate
    #1; it cannot run without them, so it rides the same env toggle
    (``MARCUS_G0_ENRICHMENT_ACTIVE``).
    """
    return g0_enrichment_wiring.g0_enrichment_active()


def ir_dispatch_live() -> bool:
    """Operator-gated live-refinement toggle (reuses S2's MARCUS_G0_DISPATCH_LIVE)."""
    return g0_enrichment_wiring.g0_dispatch_live()


def _cache_path(run_dir: Path, fingerprint: str) -> Path:
    return run_dir / _CACHE_DIRNAME / f"{fingerprint}.json"


def _load_confirmed_provisional_los(
    run_dir: Path,
) -> tuple[list[LearningObjective], str, str]:
    """Read the gate-#1-confirmed provisional LOs + corpus fingerprint + source context.

    Irene reads the FROZEN, operator-confirmed S2 enrichment result
    (``<run_dir>/g0-enrichment.json``); the provisional LOs there are the
    refinement input. A1: a missing/empty enrichment artifact is RED (refinement
    cannot run before gate #1 produced its result).

    The ``source_context`` is assembled from the typed components (label + locator
    + verbatim excerpt) so Irene assesses adequacy AGAINST the real extracted
    source — without it she judges blind and returns all-``gap`` (the live-test
    defect that motivated this).
    """
    payload = g0_enrichment_wiring.load_enrichment_result(run_dir)
    if not payload:
        raise ValueError(
            "irene-refinement: no g0-enrichment result on disk — refinement runs "
            "AFTER the G0 enrichment node + confirm-gate #1 (the provisional LOs "
            "are its input)"
        )
    los = [LearningObjective.model_validate(row) for row in payload.get("provisional_los", [])]
    fingerprint = str(payload.get("corpus_fingerprint", "")) or "unknown"
    source_context = "\n".join(
        f"[{c.get('source_type', '?')}] {c.get('label', '')} @ {c.get('locator', '')}: "
        f"{c.get('excerpt', '')}"
        for c in payload.get("typed_components", [])
    )
    return los, fingerprint, source_context


def build_result_for_run(
    *,
    run_dir: Path,
    dispatch_live: bool,
    chat_model_factory: Any | None = None,
) -> IreneRefinementResult:
    """Assemble the frozen refinement result from the on-disk gate-#1 provisional LOs."""
    provisional_los, fingerprint, source_context = _load_confirmed_provisional_los(run_dir)
    return build_refinement_result(
        provisional_los=provisional_los,
        corpus_fingerprint=fingerprint,
        dispatch_live=dispatch_live,
        chat_model_factory=chat_model_factory,
        source_context=source_context,
    )


def run_irene_refinement(
    *,
    node_id: str,
    production_envelope: ProductionEnvelope,
    trial_id: UUID | str,
    runs_root: Path,
    dispatch_live: bool = False,
    chat_model_factory: Any | None = None,
) -> ProductionEnvelope:
    """Execute the Irene-refinement hook at ``node_id``; idempotent + corpus-cached.

    Mirrors ``g0_enrichment_wiring.run_g0_enrichment``:
      - a node already carrying its contribution is not re-run (resume-safe);
      - the frozen result is cached keyed to the upstream CORPUS FINGERPRINT under
        ``<run_dir>/irene-refinement-cache/<fp>.json`` so a graph replay with an
        unchanged corpus reads the cache rather than re-refining.

    Writes ``<run_dir>/irene-refinement.json`` (the frozen result the G0R card
    reads) and lands a first-class envelope contribution.
    """
    if node_id not in IRENE_REFINEMENT_NODE_IDS:
        return production_envelope
    if (
        production_envelope.get_contribution(IRENE_REFINEMENT_SPECIALIST_ID, node_id=node_id)
        is not None
    ):
        return production_envelope

    run_dir = runs_root / str(trial_id)
    run_dir.mkdir(parents=True, exist_ok=True)

    provisional_los, fingerprint, source_context = _load_confirmed_provisional_los(run_dir)
    cache_path = _cache_path(run_dir, fingerprint)

    if cache_path.is_file():
        result = IreneRefinementResult.model_validate_json(cache_path.read_text(encoding="utf-8"))
        logger.info("irene-refinement: cache hit for fingerprint %s", fingerprint[:12])
    else:
        result = build_refinement_result(
            provisional_los=provisional_los,
            corpus_fingerprint=fingerprint,
            dispatch_live=dispatch_live,
            chat_model_factory=chat_model_factory,
            source_context=source_context,
        )
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(
            result.model_dump_json(indent=2),
            encoding="utf-8",
        )

    artifact_path = run_dir / _DECISION_ARTIFACT_BASENAME
    artifact_path.write_text(
        json.dumps(result.to_card_payload(), indent=2, default=str),
        encoding="utf-8",
    )

    updated = production_envelope.model_copy(deep=True)
    updated.add_contribution(
        SpecialistContribution.from_output(
            specialist_id=IRENE_REFINEMENT_SPECIALIST_ID,
            output={
                REFINEMENT_RESULT_KEY: result.to_card_payload(),
                "corpus_fingerprint": fingerprint,
            },
            model_used=IRENE_REFINEMENT_LIVE_MODEL_ID
            if dispatch_live
            else IRENE_REFINEMENT_MODEL_MARKER,
            node_id=node_id,
        )
    )
    return updated


def load_refinement_result(run_dir: Path) -> dict[str, Any] | None:
    """Read the frozen public card payload off disk (G0R decision-card seam)."""
    artifact = run_dir / _DECISION_ARTIFACT_BASENAME
    if not artifact.is_file():
        return None
    try:
        return json.loads(artifact.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def load_refinement_full(run_dir: Path) -> IreneRefinementResult | None:
    """Rehydrate the FULL frozen refinement result (ledger + refined LOs) from cache.

    Reads the corpus-keyed cache sidecar (the public card payload is lossy — it
    projects to dicts). Used by the G0R ratify handler to advance refined->ratified
    + run the completeness assert against the real entities.
    """
    cache_dir = run_dir / _CACHE_DIRNAME
    if not cache_dir.is_dir():
        return None
    for cache_file in sorted(cache_dir.glob("*.json")):
        try:
            return IreneRefinementResult.model_validate_json(
                cache_file.read_text(encoding="utf-8")
            )
        except (OSError, ValueError):
            continue
    return None


__all__ = [
    "IRENE_REFINEMENT_GATE_CODE",
    "IRENE_REFINEMENT_LIVE_MODEL_ID",
    "IRENE_REFINEMENT_MODEL_MARKER",
    "IRENE_REFINEMENT_NODE_ID",
    "IRENE_REFINEMENT_NODE_IDS",
    "IRENE_REFINEMENT_SPECIALIST_ID",
    "REFINEMENT_RESULT_KEY",
    "build_result_for_run",
    "ir_dispatch_live",
    "irene_refinement_active",
    "load_refinement_full",
    "load_refinement_result",
    "run_irene_refinement",
]
