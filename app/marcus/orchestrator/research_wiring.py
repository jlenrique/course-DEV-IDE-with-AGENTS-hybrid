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
import os
import sys
from pathlib import Path
from typing import Any, Literal

from app.marcus.orchestrator.research_citation import (
    CitedResearchEntry,
    apply_triangulation_to_entries,
    assert_credibility_fields,
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
# R3 — triangulation receipt (composite reliability + contradiction flags).
TRIANGULATION_RECEIPT_KEY = "triangulation_receipt"
# R6 — Irene retrieval intake packet (consumable by Pass-2; no fabricate-cite).
RESEARCH_INTAKE_KEY = "research_intake"

# --- Canonical-arc S6 ------------------------------------------------------- #
# D2 — Scite-canonical literature research. The literature-shape research
# dispatch is scoped to SCITE only: consensus is party-DEFERRED
# (``consensus-provider-live-enablement``) and gamma_docs is a Gamma-doc-audit
# provider with NO DOIs. Both are EXCLUDED so a live dispatch reaches
# SciteProvider (real DOIs), never consensus/gamma_docs. The provider directory
# sorts ready providers to ``['consensus','gamma_docs','scite']``, so the prior
# ``ready[:2]`` selector silently excluded scite — the S6 MUST-FIX.
LITERATURE_RESEARCH_PROVIDER = "scite"
DEFERRED_LITERATURE_PROVIDERS: frozenset[str] = frozenset({"consensus", "gamma_docs"})

# D4 — creds-absent degrade (X4/W-deg). When live dispatch is requested but Scite
# creds are absent, the node records a VISIBLE, explicitly-empty degrade envelope
# (never a silent drop, never a live call, never a halt) under this key + marker.
RESEARCH_DEGRADE_KEY = "research_degrade"
RESEARCH_DEGRADE_MARKER = "research enrichment skipped — credentials unavailable"

# Agentic Research Foundations R1 — opt-in detective posture shaping.
# Distinct from MARCUS_RESEARCH_DISPATCH_LIVE (network gate). Default OFF until
# R3+R4 hermetic+live green; flag-OFF path must stay bit-identical to pre-R1.
RESEARCH_DETECTIVE_LIVE_ENV = "MARCUS_RESEARCH_DETECTIVE_LIVE"
RESEARCH_DETECTIVE_LIVE_TRUTHY: frozenset[str] = frozenset(
    {"1", "true", "yes", "on"}
)

# R2 — evidence-bolster control surface (layer 1 operator knob). When true on a
# corroborate brief, selector emits scite+consensus with cross_validate=True.
# Distinct from MARCUS_RESEARCH_DETECTIVE_LIVE (posture text) and
# MARCUS_RESEARCH_DISPATCH_LIVE (network gate). Default OFF.
EVIDENCE_BOLSTER_ENV = "MARCUS_EVIDENCE_BOLSTER"
EVIDENCE_BOLSTER_TRUTHY: frozenset[str] = frozenset({"1", "true", "yes", "on"})
BOLSTER_CROSS_VALIDATE_PROVIDERS: tuple[str, ...] = ("scite", "consensus")

ResearchPosture = Literal["corroborate", "gap_fill", "embellish"]

_TEXAS_SCRIPTS_DIR = (
    Path(__file__).resolve().parents[3] / "skills" / "bmad-agent-texas" / "scripts"
)


def research_detective_live() -> bool:
    """Return True iff detective posture shaping is opted in (default OFF)."""
    return (
        os.environ.get(RESEARCH_DETECTIVE_LIVE_ENV, "").strip().lower()
        in RESEARCH_DETECTIVE_LIVE_TRUTHY
    )


def _truthy_flag(value: Any) -> bool:
    if value is True:
        return True
    if value is False or value is None:
        return False
    return str(value).strip().lower() in EVIDENCE_BOLSTER_TRUTHY


def evidence_bolster_active(brief: dict[str, Any] | None = None) -> bool:
    """Layer-1 evidence_bolster knob: brief field wins, else env (default OFF)."""
    if brief is not None and "evidence_bolster" in brief:
        return _truthy_flag(brief.get("evidence_bolster"))
    return (
        os.environ.get(EVIDENCE_BOLSTER_ENV, "").strip().lower()
        in EVIDENCE_BOLSTER_TRUTHY
    )


def consensus_creds_present() -> bool:
    """True when Consensus Bearer or Basic auth env is configured.

    Also treats a cached mcp-remote OAuth access_token as sufficient (loads into
    ``CONSENSUS_API_KEY`` when unset).
    """
    if os.environ.get("CONSENSUS_API_KEY", "").strip():
        return True
    # Lazy import via Texas scripts path (same seam as _import_retrieval).
    texas = str(_TEXAS_SCRIPTS_DIR)
    if texas not in sys.path:
        sys.path.insert(0, texas)
    try:
        from retrieval.consensus_provider import (  # noqa: PLC0415
            ensure_consensus_bearer_from_mcp_auth,
        )
    except ImportError:
        ensure_consensus_bearer_from_mcp_auth = None  # type: ignore[assignment]
    if ensure_consensus_bearer_from_mcp_auth is not None:
        try:
            if ensure_consensus_bearer_from_mcp_auth():
                return True
        except Exception:  # noqa: BLE001 — creds probe must not raise
            pass
    user = os.environ.get("CONSENSUS_USER_NAME", "").strip()
    password = os.environ.get("CONSENSUS_PASSWORD", "").strip()
    return bool(user and password)


def resolve_research_posture(brief: dict[str, Any]) -> ResearchPosture:
    """Map a gap/goal brief to one of Tracy's three research postures.

    Deterministic mechanical rules (no LLM). Explicit ``posture`` /
    ``suggested_posture`` on the brief wins when it names a known posture.
    """
    explicit = str(
        brief.get("posture") or brief.get("suggested_posture") or ""
    ).strip().lower().replace("-", "_")
    if explicit in {"corroborate", "gap_fill", "embellish"}:
        return explicit  # type: ignore[return-value]
    if explicit == "gapfill":
        return "gap_fill"

    claim = str(brief.get("claim") or "").strip()
    if claim:
        return "corroborate"

    enrichment_type = str(brief.get("enrichment_type") or "").strip()
    gap_type = str(brief.get("gap_type") or "").strip().lower()
    dial = str(brief.get("dial") or "").strip()
    if enrichment_type or dial or gap_type in {"enrichment", "embellish"}:
        return "embellish"

    return "gap_fill"


def _legacy_intent_text(brief: dict[str, Any]) -> str:
    """Pre-R1 generic intent text — preserved for flag-OFF bit-identity."""
    description = str(brief.get("gap_description") or brief.get("description") or "")
    target = str(brief.get("target_element") or "")
    if description or target:
        return (
            f"Find evidence for research-enrichment gap on {target}: "
            f"{description}"
        ).strip()
    return "Find evidence for the in-scope research-enrichment gap"


def _detective_intent_text(brief: dict[str, Any], posture: ResearchPosture) -> str:
    """Posture-aware intent text used when ``MARCUS_RESEARCH_DETECTIVE_LIVE`` is ON."""
    claim = str(brief.get("claim") or "").strip()
    source_context = str(brief.get("source_context") or "").strip()
    description = str(brief.get("gap_description") or brief.get("description") or "")
    target = str(brief.get("target_element") or "")
    enrichment_type = str(brief.get("enrichment_type") or "general").strip()
    content_type = str(brief.get("content_type") or "explanation").strip()

    if posture == "corroborate":
        base = f"Corroborate claim: {claim}" if claim else _legacy_intent_text(brief)
        if source_context:
            return f"{base} (context: {source_context})"
        return base
    if posture == "embellish":
        focus = description or enrichment_type
        where = f" on {target}" if target else ""
        return f"Embellish{where} with {enrichment_type}: {focus}".strip()
    # gap_fill
    focus = description or "in-scope research gap"
    where = f" on {target}" if target else ""
    return f"Fill research gap ({content_type}){where}: {focus}".strip()


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

    When ``MARCUS_RESEARCH_DETECTIVE_LIVE`` is OFF (default), intent text and
    hint params match the pre-R1 generic Scite search path (bit-identical).
    When ON, intents are posture-tagged (corroborate / gap_fill / embellish).
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

        detective = research_detective_live()
        posture = resolve_research_posture(brief)
        bolster = evidence_bolster_active(brief)

        # R2 — corroborate + evidence_bolster: Scite∩Consensus cross_validate.
        # Default / non-bolster / non-corroborate remains S6 Scite-canonical
        # (consensus stays deferred on that path; gamma_docs always excluded).
        if posture == "corroborate" and bolster:
            selected = [
                p
                for p in BOLSTER_CROSS_VALIDATE_PROVIDERS
                if p in ready and p not in {"gamma_docs"}
            ]
            missing = [
                p for p in BOLSTER_CROSS_VALIDATE_PROVIDERS if p not in selected
            ]
            if missing:
                raise RetrievalProviderUnavailableError(
                    "evidence_bolster corroborate requires ready providers "
                    f"{list(BOLSTER_CROSS_VALIDATE_PROVIDERS)}; missing {missing}"
                )
        else:
            selected = [
                p
                for p in ready
                if p == LITERATURE_RESEARCH_PROVIDER
                and p not in DEFERRED_LITERATURE_PROVIDERS
            ]
            if not selected:
                raise RetrievalProviderUnavailableError(
                    f"the canonical literature-research provider "
                    f"{LITERATURE_RESEARCH_PROVIDER!r} is not registered ready/stub; "
                    "cannot shape a Scite-canonical RetrievalIntent for the "
                    "research-enrichment gap"
                )

        intent_text = (
            _detective_intent_text(brief, posture)
            if detective
            else _legacy_intent_text(brief)
        )
        # S6 D7 — MECHANICAL provenance carry: when the brief originates from a
        # collateral.research_goal, stamp the goal_id onto each provider hint's
        # (provider-opaque) params so the dispatched intent traces back to
        # collateral.research_goals, NOT identified_gaps. Pure provenance label —
        # NOT a research KIND / relevance / posture decision (J1 fence).
        hint_params: dict[str, Any] = {"mode": "search"}
        research_goal_id = str(brief.get("research_goal_id") or "")
        if research_goal_id:
            hint_params["research_goal_id"] = research_goal_id
        # Detective-only posture stamp — absent when flag OFF so flag-OFF
        # params stay bit-identical to the pre-R1 shape.
        if detective:
            hint_params["posture"] = posture
        if posture == "corroborate" and bolster:
            hint_params["evidence_bolster"] = True
        return retrieval_intent_cls(
            intent=intent_text,
            provider_hints=[
                ProviderHint(provider=provider, params=dict(hint_params))
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
    return {"units": units, "research_goals": _research_goals_from_raw(lesson_plan)}


def _research_goals_from_raw(lesson_plan: dict[str, Any]) -> list[dict[str, Any]]:
    """Mechanically carry ``collateral.research_goals[]`` into the bridge dict (D7).

    Fix A (consumer-side dual-read). The real Irene-Pass-1 producer emits research
    intent as ``lesson_plan["collateral"]["research_goals"]`` (a
    ``ResearchEnrichmentGoal`` list of ``{goal_id, pedagogical_intent,
    binds_to_objective_id}``) and NEVER fills ``plan_units[].identified_gaps`` — so
    the identified_gaps-only read left the §04.55 dispatch UNREACHABLE on every real
    run.

    ⚠️ MECHANICAL FIELD-CARRY ONLY (binding J1 quality fence): carry the
    ``pedagogical_intent`` SEED (never author a query/URL), the
    ``binds_to_objective_id`` target, and ``goal_id`` provenance — then STOP. This
    decides NO research KIND / relevance / gap_type / posture; the existing
    downstream posture-selection + Texas fetch own research QUALITY unchanged.
    Additive: the Irene producer, the Gagne ``IdentifiedGap`` model, and
    ``plan_units[]`` are untouched.
    """
    collateral = lesson_plan.get("collateral")
    if not isinstance(collateral, dict):
        return []
    goals: list[dict[str, Any]] = []
    for goal in collateral.get("research_goals") or []:
        if not isinstance(goal, dict):
            continue
        goal_id = str(goal.get("goal_id") or "")
        pedagogical_intent = str(goal.get("pedagogical_intent") or "")
        # A research goal with no carryable seed nor provenance is a no-op — skip
        # it rather than dispatch an empty intent.
        if not (goal_id or pedagogical_intent):
            continue
        goals.append(
            {
                "goal_id": goal_id,
                "pedagogical_intent": pedagogical_intent,
                "binds_to_objective_id": goal.get("binds_to_objective_id"),
            }
        )
    return goals


# Mirror of fanout._POSTURE_TO_GAP_TYPE (kept local to avoid a private import).
_POSTURE_TO_GAP_TYPE: dict[str, str] = {
    "embellish": "enrichment",
    "corroborate": "evidence",
    "gap_fill": "missing_concept",
}


def has_research_goals(production_envelope: ProductionEnvelope) -> bool:
    """Return True iff the locked plan carries dispatchable research intent (D7).

    DUAL-READ (Fix A): the intent may arrive as EITHER an in-scope unit's
    ``identified_gaps`` (real G1A-curated / smoke-harness path) OR as
    ``collateral.research_goals[]`` (the real Irene-Pass-1 producer path). Both are
    honored (union); either one alone makes the §04.55 dispatch reachable.
    """
    plan_dict = _locked_plan_dict(production_envelope)
    if plan_dict is None:
        return False
    for unit in plan_dict["units"]:
        if unit.get("scope_decision") == "in-scope" and unit.get("identified_gaps"):
            return True
    return bool(plan_dict.get("research_goals"))


def _is_degraded_contribution(contribution: Any) -> bool:
    """True iff a research_wiring contribution is a D4 creds-degrade marker (R1).

    The degrade envelope carries ``research_degrade.degraded == True`` (built by
    :func:`_creds_absent_degrade_output`). Such a contribution is a recorded
    NON-result — the idempotency guard must NOT treat it as a completed research
    dispatch, so a post-re-auth resume can re-dispatch instead of short-circuiting.
    """
    output = getattr(contribution, "output", None)
    if not isinstance(output, dict):
        return False
    degrade = output.get(RESEARCH_DEGRADE_KEY)
    return isinstance(degrade, dict) and bool(degrade.get("degraded"))


def _scite_creds_present() -> bool:
    """Return True iff an OAuth Bearer token is available for a live dispatch (S6).

    **Bearer-only (S6 R3).** The canonical live-Scite MCP path requires an OAuth
    Bearer token and REJECTS HTTP-Basic (repo memory "Scite MCP needs OAuth not
    Basic"; ``scite_provider`` treats Basic as a legacy/local-server path). So
    ``.env`` Basic creds are NOT real-endpoint credentials: gating on them would
    let a bearer-expired machine pass this check and fire a doomed Basic call →
    401 → either a silent-empty result (bypassing the D4 degrade marker) or a
    non-``DispatchError`` httpx crash of the continuation walk. Gating on the
    Bearer token alone means a bearer-absent machine degrades cleanly with the
    visible D4 marker. Never raises — an absent/unrefreshable token yields
    ``None`` → False.
    """
    if str(_TEXAS_SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(_TEXAS_SCRIPTS_DIR))
    from retrieval.scite_oauth_token import load_bearer_token  # noqa: PLC0415

    return load_bearer_token() is not None


def _creds_absent_degrade_output() -> dict[str, Any]:
    """Build the VISIBLE, recorded-empty creds-degrade contribution output (D4).

    The ``research_entries`` section is PRESENT + explicitly empty (not silently
    dropped); a visible reason marker + a headed-relogin offer ride alongside so
    the SPOC can narrate the honest-degrade lane. The walk PROCEEDS.
    """
    return {
        RESEARCH_ENTRIES_KEY: [],
        DROPPED_DISPATCH_KEY: {"count": 0, "failures": []},
        RESEARCH_DEGRADE_KEY: {
            "degraded": True,
            "provider": LITERATURE_RESEARCH_PROVIDER,
            "reason": RESEARCH_DEGRADE_MARKER,
            "relogin_offer": (
                "Scite credentials are unavailable. Re-authenticate with "
                "`python skills/bmad-agent-texas/scripts/scite_oauth_login_auto.py` "
                "(headed OAuth login), then resume the run to enrich with live "
                "research."
            ),
        },
    }


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
    # --- S6 R1 (D4 degrade-resume DEFEAT fix) — idempotency guard ---
    # A GENUINELY-COMPLETED (non-degraded) contribution short-circuits (D3: no
    # double-dispatch, no double paid Scite call). But a D4 DEGRADE-marker
    # contribution (recorded when creds were absent) is NOT a completed research
    # result — treating it as complete would permanently defeat resume: the
    # operator re-authenticates, RESUMES, and the guard would short-circuit the
    # degraded envelope, never re-dispatching. So a degraded contribution FALLS
    # THROUGH and (when creds are now present) re-dispatches on resume.
    existing = production_envelope.get_contribution(
        RESEARCH_WIRING_SPECIALIST_ID, node_id=node_id
    )
    if existing is not None and not _is_degraded_contribution(existing):
        return production_envelope

    plan_dict = _locked_plan_dict(production_envelope)
    # D7 DUAL-READ: dispatchable research intent is present when EITHER an in-scope
    # unit carries identified_gaps OR the plan carries collateral.research_goals[]
    # (the real Irene-Pass-1 path). Either alone makes §04.55 reach Scite.
    in_scope_with_gaps = bool(
        plan_dict
        and (
            any(
                u.get("scope_decision") == "in-scope" and u.get("identified_gaps")
                for u in plan_dict["units"]
            )
            or plan_dict.get("research_goals")
        )
    )

    # --- S6 D4: creds precondition at NODE ENTRY (before any live dispatch) ---
    # When a live dispatch is genuinely requested for a real research gap but
    # Scite creds are absent, short-circuit to a VISIBLE, recorded-empty degrade
    # envelope INSTEAD of the old silent fail-soft drop (research_wiring §265).
    # No live call is attempted; the walk PROCEEDS. The ``injected_cited_entries``
    # test seam bypasses live dispatch entirely, so it is not creds-gated.
    if (
        dispatch_live
        and injected_cited_entries is None
        and in_scope_with_gaps
        and not _scite_creds_present()
    ):
        logger.warning(
            "research-wiring: live dispatch requested but Scite creds absent; "
            "recording a visible degrade envelope (recorded-empty) and proceeding"
        )
        updated = production_envelope.model_copy(deep=True)
        updated.add_contribution(
            SpecialistContribution.from_output(
                specialist_id=RESEARCH_WIRING_SPECIALIST_ID,
                output=_creds_absent_degrade_output(),
                model_used=RESEARCH_WIRING_MODEL_MARKER,
                node_id=node_id,
            )
        )
        return updated

    cited_entries: list[CitedResearchEntry] = []
    dropped_failures: list[dict[str, Any]] = []
    triangulation_receipt: Any | None = None
    evidence_bolster_active = False
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
            # R3 — attach triangulation receipt whenever live rows exist.
            try:
                if str(_TEXAS_SCRIPTS_DIR) not in sys.path:
                    sys.path.insert(0, str(_TEXAS_SCRIPTS_DIR))
                from retrieval.triangulator import (  # noqa: PLC0415
                    corroborate_requires_triangulation,
                    triangulate_texas_rows,
                )

                triangulation_receipt = triangulate_texas_rows(
                    rows,
                    query_intent="; ".join(
                        getattr(i, "intent", "") for i in intents[:3]
                    ),
                    title_bridge=bool(
                        research_detective_live()
                        and any(getattr(i, "cross_validate", False) for i in intents)
                    ),
                )
                # R4 — overlay triangulation status/score onto cited entries.
                cited_entries = apply_triangulation_to_entries(
                    cited_entries, triangulation_receipt
                )
                bolstered_corroborate = any(
                    getattr(i, "cross_validate", False) for i in intents
                )
                evidence_bolster_active = bool(bolstered_corroborate)
                if bolstered_corroborate and research_detective_live():
                    ok, reason = corroborate_requires_triangulation(
                        triangulation_receipt
                    )
                    if not ok:
                        logger.warning(
                            "research-wiring: corroborate triangulation gate "
                            "failed (%s); recording receipt anyway",
                            reason,
                        )
            except Exception:  # noqa: BLE001 — triangulation must not kill wiring
                logger.warning(
                    "research-wiring: triangulation failed; continuing without receipt",
                    exc_info=True,
                )
                triangulation_receipt = None

            # R4 fail-loud: every minted row carries hierarchy + provenance.
            for entry in cited_entries:
                assert_credibility_fields(entry)
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
    if triangulation_receipt is not None:
        output[TRIANGULATION_RECEIPT_KEY] = triangulation_receipt.model_dump(
            mode="json"
        )

    # R6 — durable intake packet for Irene Pass-2 / other consumers.
    try:
        from app.specialists._shared.research_intake import (  # noqa: PLC0415
            consume_research_entries,
        )

        intake = consume_research_entries(
            [e.model_dump(mode="json") for e in cited_entries],
            cluster_id="research_wiring",
            intake_mode="corroborate",
            evidence_bolster_active=evidence_bolster_active,
        )
        output[RESEARCH_INTAKE_KEY] = intake.model_dump(mode="json")
    except Exception:  # noqa: BLE001 — intake must not kill wiring
        logger.warning(
            "research-wiring: research intake packet failed; continuing",
            exc_info=True,
        )

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
    "DEFERRED_LITERATURE_PROVIDERS",
    "DROPPED_DISPATCH_KEY",
    "L2_CITATION_REPORT_KEY",
    "LITERATURE_RESEARCH_PROVIDER",
    "RESEARCH_DEGRADE_KEY",
    "RESEARCH_DEGRADE_MARKER",
    "RESEARCH_ENTRIES_KEY",
    "RESEARCH_INTAKE_KEY",
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
