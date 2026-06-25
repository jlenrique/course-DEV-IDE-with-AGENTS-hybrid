"""Braid S3 — thin Irene→Tracy→Texas research-wiring (runner-wired, option A).

Wires the *already-built* Irene→Tracy→Texas bridge through the production
runner's node walk so research-enrichment goals on in-scope plan units produce
**cited research entries** carrying ``source_ref`` / ``source_hash`` for the S2
workbook producer.

ATTACH MECHANIC (option A, decided at T1)
-----------------------------------------
The plan-lock fanout node is manifest node ``04.55`` ("Estimator + Run Constants
Lock"; emits the ``plan.locked`` learning event). Its ``specialist_id`` is
``marcus`` — absent from ``state/config/dispatch-registry.yaml`` — so the
compiler resolves it to an **orchestration** node. The walkers already invoke
orchestration handlers AT their manifest node (the ``package_builders``
precedent at node ``06``); this module joins that branch keyed by node id.

**No manifest node is added or edited** (option B was NOT taken): the side-effect
is a runner-invoked orchestration hook keyed by ``RESEARCH_WIRING_NODE_ID``,
exactly mirroring ``package_builders.BUILDER_NODE_IDS``. The pipeline-manifest
lockstep regime therefore does NOT trip (no ``block_mode_trigger_paths`` member
is touched).

TWO-WALK PARITY (memory ``project_production_runner_two_walks``)
---------------------------------------------------------------
Node ``04.55`` sits AFTER the first gate G1 (node ``04``). The start walk
``run_production_trial`` stops at G1, so ``04.55`` is reached ONLY on the
continuation walk (``_continue_production_walk`` via resume/recover). The
side-effect is added to BOTH walk bodies for parity (the builder-precedent
discipline); the continuation walk is where it actually fires on the trial path,
and the parity test EXECUTES a real continuation walk to prove it.

BRIDGE → TEXAS PATH
-------------------
1. ``IreneTracyBridge.process_plan_locked`` scans in-scope units' identified
   gaps and dispatches each to a posture selector → a ``RetrievalIntent``.
2. The intent is dispatched through Texas's ``dispatcher.dispatch`` against the
   live Scite/Consensus adapters → ``TexasRow``s.
3. Each accepted row is minted into a cited research entry
   (``research_entries`` on the run record); ``source_ref`` is a pure function
   of ``(provider, source_id)``; ``source_hash`` is a stable content hash.

Live retrieval is operator-gated: the dev-agent path runs the bridge + intent
shaping locally (no network) and SKIPS the live Texas dispatch when provider
credentials are absent / the service is unreachable.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

from app.marcus.orchestrator.research_citation import (
    CitedResearchEntry,
    assemble_l2_citation_report,
    audit_research_supplements,
    build_citation_manifest,
    dedupe_cited_entries,
    gate_citation_fidelity,
    mint_cited_entry,
)
from app.models.runtime.production_envelope import (
    ProductionEnvelope,
    SpecialistContribution,
)

logger = logging.getLogger(__name__)

# Plan-lock fanout node (§04.55). Keyed by id so NO manifest node is added — the
# runner invokes this hook AT the existing orchestration node (option A).
RESEARCH_WIRING_NODE_ID = "04.55"
RESEARCH_WIRING_NODE_IDS: frozenset[str] = frozenset({RESEARCH_WIRING_NODE_ID})

# The accepted cited entries land as a first-class envelope contribution under
# this dedicated identity (mirrors package_builders' BUILDER_SPECIALIST_ID), so a
# consumer expecting persona output never receives wiring output.
RESEARCH_WIRING_SPECIALIST_ID = "research_wiring"
RESEARCH_WIRING_MODEL_MARKER = "deterministic-research-wiring"

# Thin contract key with the S2 workbook producer (pinned by an AC-D test).
RESEARCH_ENTRIES_KEY = "research_entries"

# Run-record keys the G2 gate stamps onto the contribution output (spec §3.4 +
# G2): the L2 fail-mode citation report and the citation->source_ref->source-hash
# manifest. These are attached on the TRIAL PATH (not just unit-tested) so the
# run record carries the gate's evidence.
L2_CITATION_REPORT_KEY = "l2_citation_report"
CITATION_MANIFEST_KEY = "citation_manifest"
# AC-D3 no-silent-drop trace: the COUNT (and reasons) of bridge results that the
# wiring filtered as failed/non-intent, recorded so a shaping failure leaves a
# run-record trace rather than vanishing.
DROPPED_DISPATCH_KEY = "dropped_dispatch_failures"

_TEXAS_SCRIPTS_DIR = (
    Path(__file__).resolve().parents[3] / "skills" / "bmad-agent-texas" / "scripts"
)


class DeterministicPostureSelector:
    """Real bridge posture selector — shapes a gap brief into a ``RetrievalIntent``.

    Deterministic (NO LLM): the pipeline-manifest regime forbids an LLM in the
    deterministic neck, and projecting a gap brief into a Texas-compatible intent
    is a mechanical transform (Tracy's authored ``_act`` LLM path is the licensed
    judgment exception used elsewhere; the runner-wired plan-lock fanout uses this
    deterministic selector to keep the trial path reproducible).

    Provider selection consults the LIVE provider directory: it names only
    ``ready``/``stub`` retrieval providers from ``list_providers()`` (AC-D3 —
    never names a provider the directory does not register).
    """

    def select_posture(self, brief: dict[str, Any]) -> Any:
        retrieval_intent_cls, _, list_providers = _import_retrieval()
        from retrieval import AcceptanceCriteria, ProviderHint  # noqa: PLC0415

        ready = sorted(
            p.id
            for p in list_providers(shape="retrieval")
            if p.status in {"ready", "stub"}
        )
        if not ready:
            raise RetrievalProviderUnavailableError(
                "no ready/stub retrieval providers registered; cannot shape "
                "a RetrievalIntent for the research-enrichment gap"
            )
        selected = ready[:2] if len(ready) > 1 else ready[:1]
        description = str(brief.get("gap_description") or brief.get("description") or "")
        target = str(brief.get("target_element") or "")
        intent_text = (
            f"Find evidence for research-enrichment gap on {target}: {description}".strip()
            if description or target
            else "Find evidence for the in-scope research-enrichment gap"
        )
        return retrieval_intent_cls(
            intent=intent_text,
            provider_hints=[
                ProviderHint(provider=provider, params={"mode": "search"})
                for provider in selected
            ],
            acceptance_criteria=AcceptanceCriteria(
                mechanical={"min_results": 1},
                provider_scored={},
                semantic_deferred=(
                    "post-fetch claim screening is the operator spot-check (AC-O4); "
                    "not evaluated here"
                ),
            ),
            cross_validate=len(selected) > 1,
        )


class RetrievalProviderUnavailableError(RuntimeError):
    """Raised when no ready/stub retrieval provider exists to shape an intent."""


def _import_retrieval() -> tuple[Any, Any, Any]:
    """Import the Texas retrieval package surfaces (dispatcher + contracts).

    Late import keeps module-load cheap and avoids a hard dependency on the
    Texas scripts dir being on ``sys.path`` at import time.
    """
    if str(_TEXAS_SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(_TEXAS_SCRIPTS_DIR))
    from retrieval import RetrievalIntent  # noqa: PLC0415
    from retrieval.dispatcher import dispatch as dispatch_intent  # noqa: PLC0415
    from retrieval.provider_directory import list_providers  # noqa: PLC0415

    return RetrievalIntent, dispatch_intent, list_providers


def _locked_plan_dict(production_envelope: ProductionEnvelope) -> dict[str, Any] | None:
    """Return the locked lesson plan in IreneTracyBridge ``{"units": [...]}`` shape.

    The locked plan rides as irene_pass1's ``lesson_plan`` contribution. Returns
    ``None`` when no plan is present (degenerate-empty path).
    """
    irene = production_envelope.latest_for_specialist("irene_pass1")
    if irene is None:
        return None
    lesson_plan = irene.output.get("lesson_plan")
    if not isinstance(lesson_plan, dict):
        return None
    return _plan_dict_for_bridge_from_raw(lesson_plan)


def _plan_dict_for_bridge_from_raw(lesson_plan: dict[str, Any]) -> dict[str, Any]:
    """Map a raw lesson-plan dict into the bridge-expected ``{"units": [...]}``.

    The runner holds the plan as a serialized dict (envelope contribution), not a
    ``LessonPlan`` model, so we cannot reuse ``fanout._plan_dict_for_bridge``
    (which takes a ``LessonPlan``). This mirrors its mapping over raw dicts.
    """
    units: list[dict[str, Any]] = []
    for unit in lesson_plan.get("plan_units") or []:
        if not isinstance(unit, dict):
            continue
        scope_decision = unit.get("scope_decision")
        scope = (
            scope_decision.get("scope")
            if isinstance(scope_decision, dict)
            else scope_decision
        )
        identified_gaps: list[dict[str, Any]] = []
        for gap in unit.get("gaps") or []:
            if not isinstance(gap, dict):
                continue
            identified_gaps.append(
                {
                    "type": _POSTURE_TO_GAP_TYPE.get(
                        gap.get("suggested_posture"), "enrichment"
                    ),
                    "description": gap.get("description", ""),
                    "claim": "",
                    "source_context": "",
                    "enrichment_type": "general",
                    "content_type": "explanation",
                    "scope": "unit",
                }
            )
        units.append(
            {
                "id": unit.get("unit_id", ""),
                "scope_decision": scope,
                "identified_gaps": identified_gaps,
            }
        )
    return {"units": units}


# Mirror of fanout._POSTURE_TO_GAP_TYPE (kept local to avoid a private import).
_POSTURE_TO_GAP_TYPE: dict[str, str] = {
    "embellish": "enrichment",
    "corroborate": "evidence",
    "gap_fill": "missing_concept",
}


def has_research_goals(production_envelope: ProductionEnvelope) -> bool:
    """Return True iff some in-scope unit carries a research-enrichment gap."""
    plan_dict = _locked_plan_dict(production_envelope)
    if plan_dict is None:
        return False
    for unit in plan_dict["units"]:
        if unit.get("scope_decision") == "in-scope" and unit.get("identified_gaps"):
            return True
    return False


def _dispatch_intents_to_texas(intents: list[Any]) -> list[Any]:
    """Dispatch each ``RetrievalIntent`` through Texas; collect accepted rows.

    Live network call. Caller decides (via env / reachability) whether to invoke
    this at all — the dev-agent path skips it; the operator-gated live run runs
    it. Returns the flat list of accepted ``TexasRow``s.
    """
    _, dispatch_intent, _ = _import_retrieval()
    from retrieval.dispatcher import DispatchError  # noqa: PLC0415

    rows: list[Any] = []
    for intent in intents:
        try:
            result = dispatch_intent(intent)
        except DispatchError:
            # Fail-soft (AC-D3 spirit): one bad/unregistered/dead provider hint
            # must NOT kill the whole research node — the dispatcher raises
            # DispatchError for an unregistered or non-default-constructor
            # provider. Record + continue so the remaining intents still run.
            logger.warning(
                "research-wiring: dispatch failed for one intent; "
                "skipping it fail-soft",
                exc_info=True,
            )
            continue
        results = result if isinstance(result, list) else [result]
        for provider_result in results:
            if getattr(provider_result, "acceptance_met", False):
                rows.extend(provider_result.rows)
    return rows


def run_research_wiring(
    *,
    node_id: str,
    production_envelope: ProductionEnvelope,
    posture_selector: Any,
    dispatch_live: bool = False,
    injected_cited_entries: list[CitedResearchEntry] | None = None,
    injected_resolvable_source_refs: set[str] | None = None,
) -> ProductionEnvelope:
    """Execute the research-wiring hook registered at ``node_id``; idempotent.

    Mirrors ``package_builders.run_builder_node``:
      - a node that already carries its contribution is not re-run (resume-safe);
      - the degenerate-empty path (no in-scope research gaps) records an
        empty-but-present ``research_entries`` section and returns.

    ``posture_selector`` is the real bridge posture dispatcher (must expose
    ``select_posture(brief) -> RetrievalIntent``). ``dispatch_live`` gates the
    live Texas network dispatch (False on the dev-agent path; True only on the
    operator-gated live run).

    On the TRIAL PATH (per spec §3.4 + G2): once cited entries exist, this CALLS
    the G2 FAIL-mode citation gate, assembles the L2 fail-mode citation report,
    and builds the citation manifest, attaching both to the contribution so the
    run record is stamped. An unsourced citation raises ``CitationFidelityError``
    (FAIL mode), which the runner converts into an error-pause.

    ``injected_cited_entries`` is a deterministic test seam (legit DI, NOT a mock
    of the system under test): when supplied it stands in for the minted entries
    so the wired gate/manifest/report path can be exercised without live creds.
    ``injected_resolvable_source_refs`` independently seeds the run's retrieval
    set: supplying a set that does NOT contain an injected entry's ``source_ref``
    makes that citation unsourced and triggers the FAIL-mode gate on the wired
    path. When omitted, the resolvable set defaults to the entries' own refs
    (a self-consistent live run reports 0 unsourced).
    """
    if node_id not in RESEARCH_WIRING_NODE_IDS:
        # Defensive: keyed dispatch should never reach here with a foreign node.
        return production_envelope
    if (
        production_envelope.get_contribution(
            RESEARCH_WIRING_SPECIALIST_ID, node_id=node_id
        )
        is not None
    ):
        return production_envelope

    plan_dict = _locked_plan_dict(production_envelope)
    in_scope_with_gaps = bool(
        plan_dict
        and any(
            u.get("scope_decision") == "in-scope" and u.get("identified_gaps")
            for u in plan_dict["units"]
        )
    )

    cited_entries: list[CitedResearchEntry] = []
    dropped_failures: list[dict[str, Any]] = []
    if injected_cited_entries is not None:
        cited_entries = list(injected_cited_entries)
    elif in_scope_with_gaps:
        from skills.bmad_agent_tracy.scripts.irene_bridge import (  # noqa: PLC0415
            IreneTracyBridge,
        )

        bridge = IreneTracyBridge(posture_selector)
        raw_results = bridge.process_plan_locked(plan_dict)
        # AC-D3 no-silent-drop: the bridge catches select_posture failures into
        # {"status": "failed", ...} dicts; we filter non-intents here. RECORD the
        # dropped count + reasons so a shaping failure leaves a run-record trace
        # (fail-soft, but observable) instead of vanishing.
        intents: list[Any] = []
        for result in raw_results:
            if _is_retrieval_intent(result):
                intents.append(result)
            else:
                dropped_failures.append(_describe_dropped_result(result))

        if dispatch_live and intents:
            rows = _dispatch_intents_to_texas(intents)
            for citation_index, row in enumerate(rows, start=1):
                cited_entries.append(
                    mint_cited_entry(row, citation_index=citation_index)
                )

    # Duplicate-citation de-dup (SHOULD-FIX): identical (provider, source_id)
    # rows are minted as distinct citation_ids; collapse them first-wins so the
    # manifest carries no duplicate provenance rows.
    cited_entries = dedupe_cited_entries(cited_entries)

    output: dict[str, Any] = {
        RESEARCH_ENTRIES_KEY: [e.model_dump(mode="json") for e in cited_entries],
        DROPPED_DISPATCH_KEY: {
            "count": len(dropped_failures),
            "failures": dropped_failures,
        },
    }

    # --- G2 trial-path gate + run-record assembly (spec §3.4) ---
    if cited_entries:
        resolvable = (
            injected_resolvable_source_refs
            if injected_resolvable_source_refs is not None
            else build_retrieval_source_refs_for_entries(cited_entries)
        )
        # FAIL mode: unsourced_citations == 0 gates. Each minted entry's
        # source_ref must resolve in the run's retrieval set. Raises
        # CitationFidelityError (-> runner error-pause) on any unsourced citation.
        citations = [{"source_ref": e.source_ref} for e in cited_entries]
        gate_citation_fidelity(citations, resolvable_source_refs=resolvable)

        l2_numeric_report = audit_research_supplements(
            "", "", retrieved_figures={e.source_ref for e in cited_entries}
        )
        output[L2_CITATION_REPORT_KEY] = assemble_l2_citation_report(
            cited_entries,
            resolvable_source_refs=resolvable,
            l2_numeric_report=l2_numeric_report,
        )
        output[CITATION_MANIFEST_KEY] = build_citation_manifest(cited_entries)

    updated = production_envelope.model_copy(deep=True)
    updated.add_contribution(
        SpecialistContribution.from_output(
            specialist_id=RESEARCH_WIRING_SPECIALIST_ID,
            output=output,
            model_used=RESEARCH_WIRING_MODEL_MARKER,
            node_id=node_id,
        )
    )
    return updated


def build_retrieval_source_refs_for_entries(
    entries: list[CitedResearchEntry],
) -> set[str]:
    """Resolvable ``source_ref`` set derived from the cited entries themselves.

    On the thin S3 trial path the retrieval set IS the set of rows that were
    minted into cited entries, so the resolvable set is the union of their
    ``source_ref``s. A self-consistent run therefore reports 0 unsourced; an
    injected citation whose ``source_ref`` is absent here is unsourced -> FAIL.
    """
    return {e.source_ref for e in entries}


def _describe_dropped_result(result: Any) -> dict[str, Any]:
    """Render a filtered bridge result into a recordable, JSON-safe trace entry."""
    if isinstance(result, dict):
        return {
            "status": str(result.get("status", "dropped")),
            "reason": str(result.get("reason", "non-intent bridge result")),
        }
    return {"status": "dropped", "reason": f"non-intent result: {type(result).__name__}"}


def _is_retrieval_intent(candidate: Any) -> bool:
    """Duck-type check that the posture selector returned a RetrievalIntent."""
    retrieval_intent_cls, _, _ = _import_retrieval()
    return isinstance(candidate, retrieval_intent_cls)


def research_entries_from_envelope(
    production_envelope: ProductionEnvelope,
) -> list[dict[str, Any]]:
    """Read the accepted cited entries off the run record (S2 handoff)."""
    contribution = production_envelope.get_contribution(
        RESEARCH_WIRING_SPECIALIST_ID, node_id=RESEARCH_WIRING_NODE_ID
    )
    if contribution is None:
        return []
    entries = contribution.output.get(RESEARCH_ENTRIES_KEY)
    return list(entries) if isinstance(entries, list) else []


__all__ = [
    "CITATION_MANIFEST_KEY",
    "DROPPED_DISPATCH_KEY",
    "L2_CITATION_REPORT_KEY",
    "RESEARCH_ENTRIES_KEY",
    "RESEARCH_WIRING_MODEL_MARKER",
    "RESEARCH_WIRING_NODE_ID",
    "RESEARCH_WIRING_NODE_IDS",
    "RESEARCH_WIRING_SPECIALIST_ID",
    "DeterministicPostureSelector",
    "RetrievalProviderUnavailableError",
    "build_retrieval_source_refs_for_entries",
    "has_research_goals",
    "research_entries_from_envelope",
    "run_research_wiring",
]
