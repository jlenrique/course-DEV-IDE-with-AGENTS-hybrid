"""Irene Pass-1 lesson-plan coauthoring implementation."""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.marcus.lesson_plan.collateral_spec import CollateralSpec
from app.models.state.operator_verdict import OperatorVerdict
from app.models.state.run_state import RunState
from app.specialists.dispatch_errors import SpecialistDispatchError
from app.specialists.gary.styleguide_library import SCRIPTED_ENUM_CLASSES
from app.specialists.irene_pass1.cluster_floor import (
    CLUSTER_FLOOR_LLM_FALLBACK_TAG,
    ClusterFloorMismatchError,
    assert_floor_consulted,
    consume_min_cluster_floor,
)
from app.specialists.source_bundle import SourceBundleError, read_extracted_source

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[3]
SANCTUM_DIR = REPO_ROOT / "_bmad" / "memory" / "bmad-agent-content-creator"
REFERENCES_DIR = REPO_ROOT / "skills" / "bmad-agent-content-creator" / "references"
PASS_1_REFERENCES = (
    "cluster-planning.md",
    "cluster-decision-criteria.md",
    "cluster-narrative-arc-schema.md",
    "cluster-density-controls.md",
    "content-sequencing.md",
    "learning-objective-decomposition.md",
    "pedagogical-framework.md",
    "retrieval-intake-contract.md",
    "template-lesson-plan.md",
)

# Story 1.1: canonical cluster literals (mirror the Pass-2 template's
# ClusterRole / ClusterPosition Literal sets and the narrative-arc-schema's
# develop_type / master_behavioral_intent vocab). Kept as plain tuples to keep
# _act.py's import surface minimal (no heavy pydantic imports here).
CLUSTER_ROLES = ("head", "interstitial")
CLUSTER_POSITIONS = ("establish", "tension", "develop", "resolve")
DEVELOP_TYPES = ("deepen", "reframe", "exemplify")
MASTER_BEHAVIORAL_INTENTS = (
    "credible",
    "alarming",
    "provocative",
    "reflective",
    "moving",
    "clear-guidance",
    "attention-reset",
)
PASS_1_SYSTEM_MESSAGE = (
    "You are Irene Pass-1. Coauthor a lesson plan, slide-scope outline, and "
    "per-plan-unit ratification surface. Return strict JSON with key plan_units."
)
PASS1_MODES = {"pass-1", "irene-pass1", "irene_pass1"}
PASS2_MODES = {"pass-2", "irene-pass2", "irene_pass2"}

# Leg-C R3 AC#15 (D-0): scripted-derived payload keys the deterministic post-hoc
# honoring reads but the LLM must NEVER see. Keyed off the scripted NAMESPACE
# (the sealed registry in the CD-owned styleguide spine), never a hand-list —
# a future 2nd scripted class is auto-hidden. The FULL payload stays available
# post-hoc.
#
# D-3 byte-identity, honestly scoped (R3 remediation): with the strip + the
# floor-annotation scrub below, the model input is BYTE-IDENTICAL with and
# without a bound floor for the CREATION pass and for any pass given IDENTICAL
# incoming plans ("never re-parameterize the LLM clustering objective"). A
# refinement pass whose incoming plan was itself reshaped by honoring
# legitimately sees the honored plan — the extra clusters (minted ``#f`` ids
# included) are real downstream plan state, NOT a leak; only the floor-ENGINE-
# OWNED provenance key (``floor_subdivision_index``) is scrubbed from the
# model-visible copy so the model cannot fingerprint that a floor ran.
_LLM_HIDDEN_PAYLOAD_KEYS: frozenset[str] = frozenset(SCRIPTED_ENUM_CLASSES)

# R3 (Blind#1): floor-engine-owned plan_unit annotation keys scrubbed
# (recursively, targeted key removal) from the model-visible payload copy.
# Kept in the FULL payload + the persisted plan (provenance for the arbiter).
_FLOOR_ENGINE_ANNOTATION_KEYS: frozenset[str] = frozenset({"floor_subdivision_index"})


def _scrub_floor_annotations(value: Any) -> Any:
    """Recursively remove ``_FLOOR_ENGINE_ANNOTATION_KEYS`` from a JSON-shaped
    structure (pure: returns copies, never mutates the input)."""
    if isinstance(value, dict):
        return {
            k: _scrub_floor_annotations(v)
            for k, v in value.items()
            if k not in _FLOOR_ENGINE_ANNOTATION_KEYS
        }
    if isinstance(value, list):
        return [_scrub_floor_annotations(item) for item in value]
    return value


class ModeMismatchError(SpecialistDispatchError):
    """Raised when Pass-1 receives a Pass-2 envelope.

    Re-based onto SpecialistDispatchError (BETA S0.1 crash-taxonomy guard
    2026-06-19) so a mode mismatch error-pauses recoverably instead of crashing
    the walk (sibling of the quinn_r 07B Trial-4 crash). Stays RuntimeError-derived.
    """

    def __init__(self, message: str, *, tag: str = "irene_pass1.mode.unresolved") -> None:
        SpecialistDispatchError.__init__(self, message, tag=tag)


class BulkRatificationError(RuntimeError):
    """Raised when an operator attempts one verdict for all plan units."""


class PlanUnitRatificationError(RuntimeError):
    """Raised when per-plan-unit ratification is incomplete or invalid."""


def _json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"), default=str)


def decode_envelope_payload(state: RunState) -> dict[str, Any]:
    if state.cache_state is None or not state.cache_state.cache_prefix:
        return {}
    try:
        decoded = json.loads(state.cache_state.cache_prefix)
    except json.JSONDecodeError as exc:
        raise ValueError("irene_pass1 cache_prefix must be valid JSON") from exc
    if not isinstance(decoded, dict):
        raise ValueError("irene_pass1 cache_prefix must decode to a mapping")
    return decoded


def enforce_pass1_mode(payload: dict[str, Any]) -> None:
    mode = payload.get("mode") or payload.get("pass_phase") or payload.get("irene_mode")
    if mode is None:
        return
    normalized = str(mode).strip().lower()
    if normalized in PASS2_MODES:
        raise ModeMismatchError("Irene Pass-1 cannot run a Pass-2 envelope")
    if normalized not in PASS1_MODES:
        raise ModeMismatchError(f"Irene Pass-1 received unsupported mode {mode!r}")


def read_sanctum_digest(sanctum_dir: Path = SANCTUM_DIR) -> str:
    if not sanctum_dir.is_dir():
        return ""
    rows = []
    for path in sorted(sanctum_dir.rglob("*"), key=lambda p: p.relative_to(sanctum_dir).as_posix()):
        if path.is_file():
            rel = path.relative_to(sanctum_dir).as_posix()
            rows.append(f"{rel}\t{hashlib.sha256(path.read_bytes()).hexdigest()}")
    return "\n".join(rows)


def read_references(references_dir: Path = REFERENCES_DIR) -> str:
    parts = []
    for name in PASS_1_REFERENCES:
        path = references_dir / name
        body = path.read_text(encoding="utf-8") if path.is_file() else f"<missing: {name}>"
        parts.append(f"### Reference: {name}\n{body}")
    return "\n\n".join(parts)


def assemble_pass1_prompt(
    payload: dict[str, Any], *, extracted_source: str | None
) -> tuple[str, str]:
    # Trial-3 cycle-2 content-plane fix (2026-06-12): the prompt previously
    # carried only bundle METADATA (the quarantined 04A edge) — no corpus
    # text — and Pass-1 confabulated a lesson plan from the reference docs'
    # domain. At plan CREATION (§04A) the extracted source leads the prompt
    # and is the only planning basis. At refinement passes (§05/§05B) the
    # prior corpus-grounded plan arrives in the payload AND the corpus is
    # STILL projected alongside it — manifest nodes 05/05B declare the same
    # `dependency_projections.bundle_reference: {from: texas}` corpus
    # projection as 04A (state/config/pipeline-manifest.yaml:411-414 and
    # :429-435, dp-v1) — so `extracted_source` is non-None at refinement too
    # (R1 remediation: the earlier "corpus omitted at refinement" framing
    # from the cycle-3 error-pause predates dp-v1 and was wrong against the
    # current manifest). The `extracted_source is None` branch below is a
    # DEGRADED defensive fallback for a corpus-delivery regression, not the
    # production 05/05B shape.
    corpus_section = (
        "## Source corpus (extracted) — the ONLY planning basis\n\n"
        "Plan ONLY from the source corpus below. Reference material further "
        "down informs FORM (unit structure, scope discipline), never TOPIC.\n\n"
        f"{extracted_source}\n\n"
        if extracted_source is not None
        else "## Refinement pass — the prior corpus-grounded lesson plan in "
        "the envelope payload below is the planning basis; stay on ITS "
        "topic.\n\n"
    )
    # Leg-C R3 AC#15 (D-0 strip): scripted-derived keys never reach the model's
    # view of the payload; the caller's payload dict is untouched (post-hoc
    # consumers read the floor from the FULL payload). R3 remediation: the
    # floor-engine-owned annotation key is additionally scrubbed recursively
    # (a prior floored plan riding upstream_output.lesson_plan.plan_units must
    # not fingerprint the honoring to the model; the plan's minted clusters
    # themselves stay visible — they ARE the plan).
    model_visible_payload = _scrub_floor_annotations(
        {k: v for k, v in payload.items() if k not in _LLM_HIDDEN_PAYLOAD_KEYS}
    )
    return (
        PASS_1_SYSTEM_MESSAGE,
        f"{corpus_section}"
        "## Sanctum digest\n\n"
        f"{read_sanctum_digest()}\n\n"
        "## Irene Pass-1 references\n\n"
        f"{read_references()}\n\n"
        "## Envelope payload\n\n"
        f"```json\n{_json_dumps(model_visible_payload)}\n```\n\n"
        f"{_cluster_emission_instructions()}\n\n"
        f"{_fidelity_emission_instructions()}\n\n"
        f"{_collateral_emission_instructions()}",
    )


def _cluster_emission_instructions() -> str:
    """Story 1.1: the additive cluster-emission contract + decision guidance.

    Requests the per-plan-unit cluster fields and embeds the chunk-by-default /
    keep-dense-singleton routing from cluster-decision-criteria.md (CD) and the
    narrative-arc vocab from cluster-narrative-arc-schema.md (NA). The detailed
    reference bodies are loaded above; this block is the actionable instruction.
    """
    return (
        "Return JSON: {\"plan_units\":[{\n"
        "  \"unit_id\":\"...\",\"title\":\"...\",\"learning_objective\":\"...\",\n"
        "  \"scope_decision\":\"in-scope|out-of-scope\",\"rationale\":\"...\",\n"
        "  \"cluster_id\":\"c-uNN\",                 // every unit belongs to a "
        "cluster; singleton = its own\n"
        "  \"cluster_role\":\"head|interstitial\",\n"
        "  \"cluster_position\":\"establish|tension|develop|resolve\",\n"
        "  \"narrative_arc\":\"From <start> to <end> through <mechanism>\", "
        "// on head; inherited by members\n"
        "  \"master_behavioral_intent\":\"credible|alarming|provocative|reflective|"
        "moving|clear-guidance|attention-reset\", // on head\n"
        "  \"develop_type\":\"deepen|reframe|exemplify|null\", "
        "// develop-position interstitials only\n"
        "  \"parent_slide_id\":\"<head unit_id>\",   // interstitials only\n"
        "  \"cluster_interstitial_count\":<int>,     // on head (0 for a "
        "singleton/keep-dense unit)\n"
        "  \"source_refs\":[\"<short verbatim source quote>\", ...] "
        "// 1-6 anchors per unit\n"
        "}],\"lesson_summary\":\"...\"}.\n\n"
        "## Cluster decision guidance (apply the CD framework)\n"
        "- Chunk by DEFAULT a dense unit (3+ explanatory beats / high "
        "concept-density or visual-complexity or pedagogical-weight) into a "
        "head + N interstitials (N=1-3) under one shared narrative_arc, beats "
        "ordered establish -> tension -> develop -> resolve. Each interstitial "
        "is its own plan_unit with cluster_role:interstitial, "
        "parent_slide_id=head, same cluster_id.\n"
        "- KEEP DENSE (singleton, never chunk a gestalt): synthesis / "
        "big-picture / comparison (two-up) / diagram-driven / before-after / "
        "the resolve/takeaway slide whose value IS the simultaneous whole. "
        "Emit ONE plan_unit, cluster_role:head, cluster_position:establish, "
        "cluster_interstitial_count:0. keep-dense is an INPUT to the decision, "
        "never a veto applied after.\n"
        "- Singletons still carry a cluster_id (degenerate size-1 cluster).\n"
        "- SOURCE ANCHORS: every plan_unit carries \"source_refs\" — 1-6 SHORT "
        "quotes (roughly 3-15 words each) copied VERBATIM, character-for-"
        "character, from the source corpus, citing the exact passages this "
        "unit plans. Anchors are citations of planning work already done; "
        "they never introduce new structure. At a refinement pass (no source "
        "corpus section above), CARRY each unit's source_refs FORWARD "
        "UNCHANGED from the incoming plan's plan_units — do not re-derive, "
        "edit, or drop them."
    )


RECOGNIZED_FIDELITY = frozenset({"creative", "literal-text", "literal-visual"})
_FIDELITY_ALIASES: dict[str, str] = {
    "literal_text": "literal-text",
    "literal-text": "literal-text",
    "literal_visual": "literal-visual",
    "literal-visual": "literal-visual",
    "literal-image": "literal-visual",
    "literal_image": "literal-visual",
    "creative": "creative",
}


def _fidelity_emission_instructions() -> str:
    """Restore per-plan-unit fidelity classification (pre-migration Pass-1 contract).

    Sibling of :func:`_cluster_emission_instructions`. Requests ``fidelity`` on
    each plan_unit so Gary's literal-cohort preserve path can fire. Classification
    covers both literal-text and literal-visual; production streamlining for
    literal-visual images is a separate follow-on.
    """
    return (
        "## Per-unit fidelity classification (additive on each plan_unit)\n"
        "ALSO emit \"fidelity\" on EVERY plan_unit — exactly one of:\n"
        "  creative | literal-text | literal-visual\n"
        "Default is creative. Do not over-tag — most units should be creative.\n"
        "- literal-text: exact text/data must appear as written (assessment topic "
        "lists, tested statistics, accreditation terminology, dosage tables).\n"
        "- literal-visual: a specific SME-provided image/diagram must be faithfully "
        "placed (labeled charts, clinical flowcharts, framework diagrams). Tag "
        "classification only; do not invent image URLs.\n"
        "- creative: content may be enhanced by Gamma (default).\n"
        "If the envelope payload carries \"fidelity_guidance\", HONOR it for the "
        "named items (user guidance supplements your judgment; it does not replace "
        "independent literal needs you identify). At a refinement pass, CARRY "
        "recognized fidelity tags FORWARD from the incoming plan_units unless you "
        "deliberately reclassify."
    )


def _collateral_emission_instructions() -> str:
    """Braid S1: the additive collateral content-model emission contract (DP4).

    Sibling of :func:`_cluster_emission_instructions`. Requests a WORKBOOK
    CONTENT MODEL + a research-enrichment goals block on a top-level
    ``collateral`` key, alongside (never replacing) the plan_units / cluster
    emission. The empty case is the explicit ``declaration:"none"`` decision —
    a decision on record, not an absent key. The shapes mirror
    ``app/marcus/lesson_plan/collateral_spec.py`` (the single source of truth).
    """
    return (
        "## Workbook collateral content model (additive top-level key)\n"
        "ALSO return a top-level \"collateral\" object — the spec the client's "
        "workbook is built from. It is the read-in-depth dual-coding partner to "
        "the glance-deck: it carries the depth deferred OFF the slides so the "
        "slide voiceover can stay tight. Shape:\n"
        "{\"collateral\":{\n"
        "  \"declaration\":\"present|none\", // \"none\" = on-record decision to "
        "ship deck-only (NOT an omitted key)\n"
        "  \"workbook\":{ // present iff declaration==\"present\"\n"
        "    \"sections\":[{\n"
        "      \"section_id\":\"sec-...\",\n"
        "      \"learning_objective_id\":\"<a real plan_unit id>\", // REQUIRED; "
        "binds the section to a learning objective\n"
        "      \"title\":\"...\",\n"
        "      \"depth_delta\":{ // REQUIRED; what depth moves off the slide\n"
        "        \"deferred_from_slide\":\"<plan_unit id>\",\n"
        "        \"deferred_depth\":\"<what depth the workbook carries>\",\n"
        "        \"retained_on_slide\":\"<what stays at glance altitude>\" // optional\n"
        "      },\n"
        "      \"exercises\":[{ // may be empty for a pure-narrative section\n"
        "        \"exercise_id\":\"ex-...\",\n"
        "        \"bloom_level\":\"remember|understand|apply|analyze|evaluate|create\",\n"
        "        \"prompt_intent\":\"<pedagogical intent, not the worked prompt>\",\n"
        "        \"answer_key_source_ref\":\"<a source reference slot>\" // grounded; "
        "not a fabricated citation\n"
        "      }],\n"
        "      \"narrative_intent\":\"<the fuller-narrative brief>\"\n"
        "    }]\n"
        "  },\n"
        "  \"research_goals\":[{ // pedagogical INTENT, never a raw fetch query/URL\n"
        "    \"goal_id\":\"rg-...\",\n"
        "    \"pedagogical_intent\":\"learner needs the primary-source basis for "
        "the 23% figure\",\n"
        "    \"binds_to_objective_id\":\"<objective id>\" // optional\n"
        "  }]\n"
        "}}.\n"
        "- Express research as pedagogical INTENT, not a search query — the "
        "research wiring translates intent to fetch downstream.\n"
        "- If the lesson genuinely ships deck-only, emit "
        "{\"collateral\":{\"declaration\":\"none\"}} explicitly."
    )


def _singleton_cluster_id(unit_id: str) -> str:
    """Derive a deterministic degenerate size-1 cluster id from a unit id."""
    base = str(unit_id).strip() or "unit"
    return base if base.startswith("c-") else f"c-{base}"


def normalize_clusters(plan: dict[str, Any]) -> dict[str, Any]:
    """Pure post-parse backstop that makes cluster structure downstream-valid.

    Story 1.1 (Scope item 3). PURE: returns a new dict, never mutates the input.
    LLM cluster output is variance-prone; this guarantees every plan_unit carries
    a well-formed cluster shape regardless of model sloppiness:

    PARENT LINKAGE IS AUTHORITATIVE. An interstitial's cluster membership is
    decided by its head (resolved via parent_slide_id, or — when the model
    omits it — by a matching head cluster_id), and the interstitial's cluster_id
    + narrative_arc are then derived FROM that head. This keeps the three keyed
    operations (count, arc inheritance, grouping) mutually consistent instead of
    trusting three independently-sloppy model fields (T11 code-review root-cause
    fix: cluster_id-vs-parent_slide_id key confusion, Blind+Edge MAJOR).

    Guarantees regardless of model sloppiness:
    - roles coerced FIRST (invalid -> head) so the head set reflects normalized
      roles, not raw/mis-cased values
    - every unit gets a UNIQUE cluster_id; missing/blank/duplicate unit_ids use
      an index-stable synthetic key so distinct units never collapse into one
      cluster; duplicate head cluster_ids are split
    - an interstitial with no resolvable head -> demoted to its own singleton
      head (no orphans reach Gary); a resolved interstitial inherits its head's
      cluster_id + narrative_arc
    - head cluster_position defaults to "establish" (the arc anchor); an
      interstitial's missing/invalid position -> None (never force "establish")
    - invalid develop_type / master_behavioral_intent -> None (tolerance)
    - cluster_interstitial_count recomputed on each head from actual members
    - pure (no input mutation), idempotent, never crashes
    """
    if not isinstance(plan, dict):
        return {"plan_units": []}
    raw_units = plan.get("plan_units")
    if not isinstance(raw_units, list):
        return {**plan, "plan_units": []}

    # Work on copies so the function is pure (no input mutation).
    units: list[dict[str, Any]] = [dict(u) if isinstance(u, dict) else {} for u in raw_units]

    def _uid(unit: dict[str, Any], idx: int) -> str:
        value = unit.get("unit_id")
        text = str(value).strip() if value is not None else ""
        return text or f"u{idx}"

    # Pass 1: coerce roles up front so the head set is built from normalized
    # roles (a mis-cased "Head" no longer orphans its real interstitials).
    for unit in units:
        role = unit.get("cluster_role")
        unit["cluster_role"] = role if role in CLUSTER_ROLES else "head"

        dtype = unit.get("develop_type")
        if dtype is not None and dtype not in DEVELOP_TYPES:
            unit["develop_type"] = None
        mbi = unit.get("master_behavioral_intent")
        if mbi is not None and mbi not in MASTER_BEHAVIORAL_INTENTS:
            unit["master_behavioral_intent"] = None

    # Pass 2: assign each HEAD a unique cluster_id (keep the model's if present
    # and not already taken; else derive from the head's unit_id) and index
    # the heads for parent resolution.
    used_cluster_ids: set[str] = set()
    head_by_uid: dict[str, dict[str, Any]] = {}
    head_by_cluster_id: dict[str, dict[str, Any]] = {}
    head_uid_by_cluster_id: dict[str, str] = {}
    for idx, unit in enumerate(units):
        if unit["cluster_role"] != "head":
            continue
        uid = _uid(unit, idx)
        cid = unit.get("cluster_id")
        if not (isinstance(cid, str) and cid.strip() and cid not in used_cluster_ids):
            cid = _singleton_cluster_id(uid)
            suffix = 1
            while cid in used_cluster_ids:
                suffix += 1
                cid = f"{_singleton_cluster_id(uid)}-{suffix}"
        unit["cluster_id"] = cid
        used_cluster_ids.add(cid)
        head_by_uid.setdefault(uid, unit)
        head_by_cluster_id.setdefault(cid, unit)
        head_uid_by_cluster_id.setdefault(cid, uid)

    # Pass 3: resolve each interstitial to a head (parent_slide_id first, then a
    # matching head cluster_id); inherit the head's cluster_id + arc, or demote.
    for idx, unit in enumerate(units):
        if unit["cluster_role"] != "head":
            parent = unit.get("parent_slide_id")
            head = head_by_uid.get(str(parent)) if parent is not None else None
            if head is None:
                head = head_by_cluster_id.get(str(unit.get("cluster_id")))
            if head is None:
                # Orphan -> demote to its own singleton head.
                unit["cluster_role"] = "head"
                unit.pop("parent_slide_id", None)
                uid = _uid(unit, idx)
                cid = _singleton_cluster_id(uid)
                suffix = 1
                while cid in used_cluster_ids:
                    suffix += 1
                    cid = f"{_singleton_cluster_id(uid)}-{suffix}"
                unit["cluster_id"] = cid
                used_cluster_ids.add(cid)
                head_by_uid.setdefault(uid, unit)
                head_by_cluster_id.setdefault(cid, unit)
                head_uid_by_cluster_id.setdefault(cid, uid)
            else:
                # Parent-authoritative: inherit the head's cluster_id + arc.
                head_cid = head["cluster_id"]
                unit["cluster_id"] = head_cid
                unit["parent_slide_id"] = head_uid_by_cluster_id[head_cid]
                head_arc = head.get("narrative_arc")
                if not unit.get("narrative_arc") and isinstance(head_arc, str) and head_arc.strip():
                    unit["narrative_arc"] = head_arc

    # Pass 4: position semantics — head anchors at establish; interstitial
    # missing/invalid -> None (never force an interstitial to establish).
    for unit in units:
        pos = unit.get("cluster_position")
        if unit["cluster_role"] == "head":
            unit["cluster_position"] = pos if pos in CLUSTER_POSITIONS else "establish"
        elif pos is not None and pos not in CLUSTER_POSITIONS:
            unit["cluster_position"] = None

    # Pass 5: recompute cluster_interstitial_count per head from real members
    # (cluster_id is now consistent because interstitials inherited the head's).
    interstitial_counts: dict[str, int] = {}
    for unit in units:
        if unit["cluster_role"] == "interstitial":
            cid = str(unit.get("cluster_id"))
            interstitial_counts[cid] = interstitial_counts.get(cid, 0) + 1
    for unit in units:
        if unit["cluster_role"] == "head":
            cid = str(unit.get("cluster_id"))
            unit["cluster_interstitial_count"] = interstitial_counts.get(cid, 0)

    return {**plan, "plan_units": units}


def normalize_collateral(plan: dict[str, Any]) -> dict[str, Any]:
    """Pure post-parse backstop guaranteeing a well-formed ``collateral`` block.

    Braid S1 (Scope item 3). Mirrors :func:`normalize_clusters`: PURE (returns a
    new dict, never mutates the input), idempotent, never crashes. Guarantees
    ``plan["collateral"]`` validates as a :class:`CollateralSpec` shape on BOTH
    the LLM-output path and the fallback-unit path:

    - missing / non-dict / unparseable collateral -> the explicit
      ``{"declaration": "none"}`` decision-on-record (degenerate-empty), NOT an
      absent key
    - a collateral block that fails ``CollateralSpec`` validation (e.g. a
      ``declaration:"present"`` with no usable workbook, or a malformed section)
      degrades to the ``"none"`` declaration rather than crashing the walk —
      the additive/no-regression invariant holds even on sloppy model output
    - a well-formed block is canonicalized through ``CollateralSpec`` so the
      emitted block is exactly the validated shape (sorted, defaulted)

    The producer (S2) and research wiring (S3) read the validated shape; S1's
    job is to make a well-formed instance always present.

    ``CollateralSpec`` is imported at module level (the import-anchor discipline,
    mirror Amelia-a.2) so the schema family is statically reachable in the
    import graph and cannot rot as an orphan module. Marcus Contract M3 forbids
    app.specialists importing only marcus.facade / marcus.intake /
    marcus.orchestrator — not app.marcus.lesson_plan — so this edge is allowed.
    """
    none_block = {"declaration": "none"}
    if not isinstance(plan, dict):
        return {"collateral": dict(none_block)}

    raw = plan.get("collateral")
    if not isinstance(raw, dict):
        return {**plan, "collateral": dict(none_block)}

    try:
        spec = CollateralSpec.model_validate(raw)
    except Exception as exc:
        # Never-crash backstop: degrade a malformed block to the on-record
        # deck-only declaration rather than propagating a validation error.
        # FIX-1: make the degrade OBSERVABLE. A genuine declaration:"none"
        # (or absent / non-dict, handled above) is a legitimate decision and
        # must NOT warn; but a block that *intended* a workbook — declaration
        # "present" OR a non-empty workbook payload — losing the whole workbook
        # silently collapses DP4's decision-on-record distinction. Warn (once)
        # capturing the validation error before returning the none decision.
        declared_present = raw.get("declaration") == "present"
        workbook = raw.get("workbook")
        has_workbook_payload = bool(workbook) and isinstance(workbook, dict)
        if declared_present or has_workbook_payload:
            logger.warning(
                "irene-pass1 collateral degraded to declaration:'none' — a "
                "present/workbook block failed CollateralSpec validation and "
                "was dropped: %s",
                exc,
            )
        return {**plan, "collateral": dict(none_block)}

    # Canonicalize to the validated shape (mode="json" so it round-trips through
    # CacheState's JSON cache_prefix without datetime/enum surprises).
    return {**plan, "collateral": spec.model_dump(mode="json")}


def _canonicalize_fidelity(raw: Any) -> str | None:
    """Return a recognized fidelity mode, or None to omit the key."""
    if raw is None:
        return None
    if not isinstance(raw, str):
        return None
    stripped = raw.strip()
    if not stripped:
        return None
    lowered = stripped.lower()
    aliased = _FIDELITY_ALIASES.get(lowered)
    if aliased is not None:
        return aliased
    # Hyphen/underscore-normalized lookup already covered; reject unknowns.
    if lowered in RECOGNIZED_FIDELITY:
        return lowered
    return None


def normalize_fidelity(plan: dict[str, Any]) -> dict[str, Any]:
    """Pure soft-coerce for per-unit ``fidelity`` (emit-recovery backstop).

    Recognized values (and known aliases such as ``literal-image`` →
    ``literal-visual``) are kept. Missing / empty / unknown values omit the
    key — never invent a tag from prose. PURE: returns a new plan dict.
    """
    if not isinstance(plan, dict):
        return plan
    raw_units = plan.get("plan_units")
    if not isinstance(raw_units, list):
        return plan
    units: list[Any] = []
    for unit in raw_units:
        if not isinstance(unit, dict):
            units.append(unit)
            continue
        next_unit = dict(unit)
        canonical = _canonicalize_fidelity(next_unit.get("fidelity"))
        if canonical is None:
            next_unit.pop("fidelity", None)
        else:
            next_unit["fidelity"] = canonical
        units.append(next_unit)
    return {**plan, "plan_units": units}


# R7 (Edge#4): internal marker set by parse_pass1_response when the model's
# output was NOT usable structured JSON and the single synthetic fallback unit
# was substituted. act() POPS it (never persisted / never model-visible) and
# uses it to give a bound-floor mismatch on the fallback plan a DISTINCT
# llm-format-fallback diagnostic instead of the generic
# styleguide-vs-content framing.
_PARSE_FALLBACK_KEY = "_llm_format_fallback"


def parse_pass1_response(raw_text: str) -> dict[str, Any]:
    stripped = raw_text.strip()
    if "```json" in stripped:
        start = stripped.find("```json") + len("```json")
        end = stripped.find("```", start)
        if end > start:
            stripped = stripped[start:end].strip()
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        parsed = {"lesson_summary": raw_text, "plan_units": []}
    if not isinstance(parsed, dict):
        parsed = {"lesson_summary": raw_text, "plan_units": []}
    # Normalize cluster structure on whatever the model produced (after JSON
    # parse, before the fallback-unit branch) so both LLM output and the
    # fallback unit get a well-formed cluster shape.
    parsed = normalize_clusters(parsed)
    units = parsed.get("plan_units")
    if not isinstance(units, list) or not units:
        topic = parsed.get("lesson_summary") or "Irene Pass-1 lesson plan"
        parsed["plan_units"] = [
            {
                "unit_id": "unit-1",
                "title": "Core lesson scope",
                "learning_objective": str(topic),
                "scope_decision": "in-scope",
                "rationale": "Fallback unit from unstructured Pass-1 response.",
            }
        ]
        # The fallback unit is itself a degenerate size-1 cluster.
        parsed = normalize_clusters(parsed)
        parsed[_PARSE_FALLBACK_KEY] = True  # R7: flag the format fallback
    # Braid S1: guarantee a well-formed collateral block on BOTH the LLM-output
    # path and the fallback-unit path (additive; degenerate-empty -> "none").
    parsed = normalize_collateral(parsed)
    # Fidelity emit recovery: soft-coerce recognized modes; never invent tags.
    parsed = normalize_fidelity(parsed)
    return parsed


def write_lesson_plan(plan: dict[str, Any], *, run_id: str, runs_root: Path | None = None) -> Path:
    root = runs_root or REPO_ROOT / "runs"
    run_dir = root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / "irene-pass1.md"
    # Soft-canonicalize fidelity so alias callers (literal_text / literal-image)
    # still surface a line even when they bypass parse_pass1_response.
    plan = normalize_fidelity(plan)
    lines = ["# Irene Pass-1 Lesson Plan", ""]
    if plan.get("lesson_summary"):
        lines.extend([str(plan["lesson_summary"]), ""])
    for unit in plan["plan_units"]:
        lines.extend(
            [
                f"## {unit.get('unit_id', 'unit')}: {unit.get('title', 'Untitled')}",
                f"- Learning objective: {unit.get('learning_objective', '')}",
                f"- Scope decision: {unit.get('scope_decision', '')}",
                f"- Rationale: {unit.get('rationale', '')}",
            ]
        )
        # Story 1.1: cluster fields are the witness the 1.2 emission gate reads.
        # Additive — flat lines above are unchanged.
        lines.append(f"- Cluster id: {unit.get('cluster_id', '')}")
        lines.append(f"- Cluster role: {unit.get('cluster_role', '')}")
        lines.append(f"- Cluster position: {unit.get('cluster_position', '')}")
        if unit.get("narrative_arc"):
            lines.append(f"- Narrative arc: {unit['narrative_arc']}")
        if unit.get("cluster_role") == "interstitial" and unit.get("parent_slide_id"):
            lines.append(f"- Parent slide id: {unit['parent_slide_id']}")
        is_head = unit.get("cluster_role") == "head"
        if is_head and unit.get("cluster_interstitial_count") is not None:
            lines.append(
                f"- Cluster interstitial count: {unit['cluster_interstitial_count']}"
            )
        raw_fidelity = unit.get("fidelity")
        if isinstance(raw_fidelity, str) and raw_fidelity in RECOGNIZED_FIDELITY:
            lines.append(f"- Fidelity: {raw_fidelity}")
        lines.append("")
    # Braid S1: additive collateral content-model section. Appended AFTER all
    # plan-unit / cluster lines so the cluster-section lines stay byte-unchanged
    # (the no-regression invariant). Absent/none collateral emits the explicit
    # deck-only declaration line; never an absent section.
    lines.extend(_collateral_artifact_lines(plan.get("collateral")))
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return path


def _oneline(value: Any) -> str:
    """Collapse CR/LF in a free-text field to single spaces for flat rendering.

    FIX-3 (S1->S2 seam robustness): the collateral artifact section interpolates
    free-text fields (title, narrative_intent, prompt_intent, pedagogical_intent,
    deferred_depth) into flat ``- `` / ``### `` lines that S2 parses back. A
    field carrying a newline would inject fake markdown lines. This sanitizes at
    the RENDERING SITE ONLY — the stored schema values stay verbatim.
    """
    return str(value).replace("\r\n", " ").replace("\r", " ").replace("\n", " ")


def _collateral_artifact_lines(collateral: Any) -> list[str]:
    """Render the additive ``## Workbook collateral`` artifact section.

    Pure helper. A missing or ``declaration:"none"`` block renders the explicit
    deck-only line (the decision-on-record); a ``present`` block renders the
    workbook sections + research goals as flat, additive lines.
    """
    block = collateral if isinstance(collateral, dict) else {}
    declaration = block.get("declaration", "none")
    out: list[str] = ["## Workbook collateral", f"- Declaration: {declaration}"]
    if declaration != "present":
        out.append("- Workbook: none (lesson ships deck-only)")
        out.append("")
        return out

    workbook = block.get("workbook") or {}
    sections = workbook.get("sections") if isinstance(workbook, dict) else None
    for section in sections or []:
        if not isinstance(section, dict):
            continue
        out.append(
            f"### {section.get('section_id', 'section')}: "
            f"{_oneline(section.get('title', 'Untitled'))}"
        )
        out.append(
            f"- Learning objective id: {section.get('learning_objective_id', '')}"
        )
        depth = section.get("depth_delta") or {}
        if isinstance(depth, dict):
            out.append(
                f"- Depth deferred from: {depth.get('deferred_from_slide', '')}"
            )
            out.append(f"- Depth deferred: {_oneline(depth.get('deferred_depth', ''))}")
            if depth.get("retained_on_slide"):
                out.append(f"- Retained on slide: {depth['retained_on_slide']}")
        if section.get("narrative_intent"):
            out.append(f"- Narrative intent: {_oneline(section['narrative_intent'])}")
        for exercise in section.get("exercises") or []:
            if not isinstance(exercise, dict):
                continue
            out.append(
                f"- Exercise {exercise.get('exercise_id', '')} "
                f"[{exercise.get('bloom_level', '')}]: "
                f"{_oneline(exercise.get('prompt_intent', ''))} "
                f"(answer key source: {exercise.get('answer_key_source_ref', '')})"
            )
    for goal in block.get("research_goals") or []:
        if not isinstance(goal, dict):
            continue
        out.append(
            f"- Research goal {goal.get('goal_id', '')}: "
            f"{_oneline(goal.get('pedagogical_intent', ''))}"
        )
    out.append("")
    return out


def confirm_plan_units(
    plan: dict[str, Any],
    verdicts: dict[str, OperatorVerdict] | OperatorVerdict,
) -> dict[str, Any]:
    units = plan.get("plan_units", [])
    if isinstance(verdicts, OperatorVerdict):
        raise BulkRatificationError("bulk confirmation is forbidden; confirm each unit")
    if not isinstance(verdicts, dict):
        raise PlanUnitRatificationError("verdicts must be keyed by plan unit")
    locked_units = []
    for unit in units:
        unit_id = str(unit.get("unit_id", ""))
        verdict = verdicts.get(unit_id)
        if not isinstance(verdict, OperatorVerdict):
            raise PlanUnitRatificationError(f"missing OperatorVerdict for {unit_id}")
        if verdict.verb not in {"approve", "edit"}:
            raise PlanUnitRatificationError(f"unit {unit_id} rejected")
        updated = dict(unit)
        if verdict.edit_payload:
            updated.update(verdict.edit_payload)
        updated["ratified_by"] = verdict.operator_id
        updated["ratification_verdict_id"] = str(verdict.verdict_id)
        locked_units.append(updated)
    return {"plan_units": locked_units, "locked": True}


def build_learning_events(*, run_id: str, locked_scope: dict[str, Any]) -> list[dict[str, Any]]:
    now = datetime.now(UTC).isoformat()
    base = {"run_id": run_id, "gate": "G1A", "timestamp": now}
    return [
        {**base, "event_type": "scope_decision.set", "payload": locked_scope},
        {**base, "event_type": "plan.locked", "payload": {"locked_scope": locked_scope}},
    ]


def act(state: RunState, *, handle: Any, model_id: str) -> dict[str, Any]:
    payload = decode_envelope_payload(state)
    enforce_pass1_mode(payload)
    upstream = payload.get("upstream_output")
    has_prior_plan = isinstance(upstream, dict) and "lesson_plan" in upstream
    try:
        extracted_source: str | None = read_extracted_source(payload)
    except SourceBundleError:
        if not has_prior_plan:
            raise  # plan creation without corpus = contract violation
        extracted_source = None  # refinement pass over the prior plan
    system_msg, user_msg = assemble_pass1_prompt(
        payload, extracted_source=extracted_source
    )
    response = handle.chat.invoke(
        [{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}]
    )
    raw = response.content if hasattr(response, "content") else str(response)
    plan = parse_pass1_response(raw if isinstance(raw, str) else str(raw))
    llm_format_fallback = bool(plan.pop(_PARSE_FALLBACK_KEY, False))
    # Leg-C R3: deterministic post-hoc min_cluster_floor honoring on the FULL
    # payload (the LLM never saw the floor — D-0 strip above). Runs on EVERY
    # Pass-1 dispatch (04A creation AND 05/05B refinement — the manifest
    # projects the corpus to 05/05B too, so extracted_source is normally
    # non-None on all three nodes): refinement CONSOLIDATES clusters, so the
    # LATEST pass must honor. The dead-config guard (D-1/D-3) fails loud if a
    # bound floor ever bypasses this seam.
    try:
        floored_units, floor_receipt = consume_min_cluster_floor(
            payload, plan["plan_units"], extracted_source=extracted_source
        )
    except ClusterFloorMismatchError as exc:
        if llm_format_fallback:
            # R7: same recoverable error class, DISTINCT diagnostic — the
            # mismatch is an artifact of the LLM format failure (one synthetic
            # unit, no source_refs), not a styleguide/content pairing problem.
            raise ClusterFloorMismatchError(
                "llm-format-fallback: the Pass-1 response was not usable "
                "structured JSON, so the plan is the single synthetic fallback "
                "unit (no source_refs); a bound min_cluster_floor cannot be "
                "assessed against it — triage the LLM output format, not the "
                f"styleguide/content pairing. Underlying mismatch: {exc}",
                tag=CLUSTER_FLOOR_LLM_FALLBACK_TAG,
            ) from exc
        raise
    assert_floor_consulted(payload, floor_receipt)
    plan = {**plan, "plan_units": floored_units}
    run_id = str(payload.get("run_id") or state.run_id)
    runs_root_value = payload.get("runs_root")
    runs_root = Path(str(runs_root_value)) if runs_root_value else None
    artifact_path = write_lesson_plan(plan, run_id=run_id, runs_root=runs_root)
    locked_scope = {"plan_units": plan["plan_units"], "locked": False}
    events = build_learning_events(run_id=run_id, locked_scope=locked_scope)
    output = {
        "specialist_id": "irene_pass1",
        "model_id": model_id,
        "lesson_plan": plan,
        "artifact_path": str(artifact_path),
        "locked_scope": locked_scope,
        "learning_events": events,
        "usage": getattr(response, "usage_metadata", None),
    }
    entries_count = state.cache_state.entries_count if state.cache_state is not None else 0
    return {
        "cache_state": {
            "cache_prefix": _json_dumps(output),
            "entries_count": entries_count + 1,
        }
    }


# Amelia a.2 (party review 2026-06-12): the payload contract participates in
# the act's import graph so it cannot rot as an orphan module.
from app.specialists.irene_pass1.payload_contract import CONSUMED_PAYLOAD_KEYS  # noqa: E402

__all__ = [
    "BulkRatificationError",
    "CONSUMED_PAYLOAD_KEYS",
    "ModeMismatchError",
    "PASS_1_REFERENCES",
    "PASS_1_SYSTEM_MESSAGE",
    "PlanUnitRatificationError",
    "act",
    "assemble_pass1_prompt",
    "assert_floor_consulted",
    "build_learning_events",
    "confirm_plan_units",
    "consume_min_cluster_floor",
    "decode_envelope_payload",
    "enforce_pass1_mode",
    "normalize_clusters",
    "normalize_collateral",
    "normalize_fidelity",
    "parse_pass1_response",
    "read_sanctum_digest",
    "write_lesson_plan",
]
