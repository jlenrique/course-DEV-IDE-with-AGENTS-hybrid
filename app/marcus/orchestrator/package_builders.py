"""S3 pre-dispatch package builders (SCP 2026-06-11 segment-data-plane).

Pure, deterministic transforms that turn upstream envelope contributions
into the exact payload vocabulary a downstream specialist consumes. No LLM:
the pipeline-manifest regime forbids LLMs in the deterministic neck, and
brief derivation from a ratified lesson plan + creative directive is a
mechanical projection (the pre_gate_marcus single-LLM-call pattern remains
the licensed exception for judgment work; not needed here).

Invocation follows the established pre_gate_marcus pattern: the walkers
invoke the builder AT its manifest node, and the output lands as a
first-class envelope contribution keyed to that node (Winston: the manifest
tells the truth — §06 "Pre-Dispatch Package Build" actually builds).

Scope (S3): §06 (Gary slide-brief package). §6.2/§6.3 (conditional
cluster prompt-engineering/sequencing) and §06B (literal-visual OPERATOR
build) remain orchestration no-ops — recorded in the S3 story record for
party review; they are conditional-path / operator-input nodes, not the
G0→G2C data plane.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import UUID

from app.marcus.lesson_plan.pass1_authority import (
    Pass1PlanAuthorityError,
    assert_receipt_matches_plan,
)
from app.marcus.lesson_plan.slide_authority import read_contained_regular_bytes
from app.marcus.orchestrator import enrichment_consumption, g0_enrichment_wiring
from app.models.runtime.production_envelope import (
    ProductionEnvelope,
    SpecialistContribution,
)
from app.pass1_generation_lock import (
    Pass1GenerationLockError,
    pass1_generation_lock,
)
from app.specialists.dispatch_errors import SpecialistDispatchError
from app.specialists.gary.payload_contract import (
    CONSUMED_PAYLOAD_KEYS as GARY_CONSUMED_PAYLOAD_KEYS,
)

# Dedicated identity (Winston ruling c, party review 2026-06-12): the envelope
# must tell the truth about who produced what — a deterministic builder is not
# the Marcus persona, and latest_for_specialist("marcus") must never return
# builder output to a consumer expecting persona output.
BUILDER_SPECIALIST_ID = "package_builder"
GARY_PACKAGE_NODE_ID = "06"
BUILDER_NODE_IDS: frozenset[str] = frozenset({GARY_PACKAGE_NODE_ID})
BUILDER_MODEL_MARKER = "deterministic-package-builder"
CURRENT_BUILDER_MODEL_MARKER = "deterministic-package-builder-authority-v1"


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate authority key: {key}")
        result[key] = value
    return result


class BuilderInputError(SpecialistDispatchError):
    """Raised when a package builder's upstream inputs are missing or malformed.

    S0 fail-loud policy: a builder never invents a package from absent
    inputs — that is exactly how Gary's fixture slides reached G2C.

    WAVE-0 tranche 2 (2026-06-17, party-ratified): re-based onto
    ``SpecialistDispatchError`` (RuntimeError-derived, byte-identical
    ``(message, *, tag)`` ctor — inherited, no override needed) so a §06
    starvation ERROR-PAUSES recoverably (``trial recover`` re-enters node-06)
    instead of KILLING the trial. Node-06 was the last live-walk dispatch leg
    outside the error-pause family. Fail-loud intent preserved: the pause is
    non-silent (tagged error-pause.json), opens no DecisionCard, and halts
    BEFORE the G2C gate — no quality-theater path is created (Murat/John
    adjudication, S5-crit-5 + Finding-#8 mechanism migrated crash→error-pause,
    contract unchanged).

    Tag taxonomy spans two classes, told apart by the per-condition ``tag`` on
    the persisted error-pause.json (party no-split ruling — one family, honest
    tags): TRANSIENT/INPUT conditions (``upstream-missing``,
    ``lesson-plan-shape``, ``cd-directive-shape``, ``no-in-scope-units``) that
    ``trial recover`` resolves once upstream is fixed; and DEFENSIVE
    programmer-error conditions (``unknown-node`` — unreachable while
    ``BUILDER_NODE_IDS`` matches the dispatch set; ``contract-violation``) that
    also error-pause rather than crash, but which recovery cannot resolve
    without a code change. Pausing them is still strictly better than killing a
    paid walk; the tag is what signals "fix code, not corpus".
    """


def _unit_included(unit: dict[str, Any]) -> bool:
    """Include unless the unit is explicitly ratified out-of-scope.

    The lesson-plan schema carries scope_decision as either a bare string
    or a {"scope": ...} mapping; absence of a ratified decision keeps the
    unit IN (conservative: dropping content silently is the failure mode
    this arc exists to kill).
    """
    decision: Any = unit.get("scope_decision")
    if isinstance(decision, dict):
        decision = decision.get("scope")
    return decision != "out-of-scope"


def build_gary_briefs(
    lesson_plan: dict[str, Any],
    cd_directive: dict[str, Any],
    *,
    enrichment_hint: str | None = None,
) -> dict[str, Any]:
    """Project a ratified lesson plan + creative directive into Gary's vocabulary.

    Output keys are a strict subset of gary's CONSUMED_PAYLOAD_KEYS (S1
    contract regime); the subset relation is both asserted here (belt) and
    pinned by the package-builder ratchet (suspenders).

    P5-S2 Consumer B (Step 6): when ``enrichment_hint`` is supplied (the
    orchestrator-projected short structured G0 role/LO token, gated upstream by the
    deck flag + card presence), it is appended to ``additional_instructions`` ONLY
    — so the directive SENT to Gamma is enrichment-shaped, byte-deterministically.
    The hint NEVER enters ``slides`` / ``prompt`` (the ``text_mode="preserve"`` card
    body) nor the Studio lock (GARY-A1 content-channel firewall). ``None`` ⇒ the
    package is byte-identical to the non-enriched build. No NEW payload key is added
    (the hint rides the existing ``additional_instructions``), so the gary contract
    + Ratchet-D are unchanged.
    """
    plan_units = lesson_plan.get("plan_units") if isinstance(lesson_plan, dict) else None
    if not isinstance(plan_units, list) or not plan_units:
        raise BuilderInputError(
            "lesson_plan carries no plan_units; cannot derive slide briefs",
            tag="builder.gary.lesson-plan-shape",
        )
    if not isinstance(cd_directive, dict) or not cd_directive.get("experience_profile"):
        raise BuilderInputError(
            "cd_directive missing experience_profile; cannot derive slide briefs",
            tag="builder.gary.cd-directive-shape",
        )
    if not all(isinstance(unit, dict) for unit in plan_units):
        raise BuilderInputError(
            "lesson_plan plan_units must all be objects",
            tag="builder.gary.plan-authority-invalid",
        )
    all_unit_ids: list[str] = []
    for unit in plan_units:
        unit_id = unit.get("unit_id")
        if (
            not isinstance(unit_id, str)
            or not unit_id
            or unit_id != unit_id.strip()
            or unit_id in all_unit_ids
        ):
            raise BuilderInputError(
                "lesson_plan carries blank or duplicate unit authority",
                tag="builder.gary.plan-authority-invalid",
            )
        all_unit_ids.append(unit_id)
    units = [
        unit
        for unit in plan_units
        if isinstance(unit, dict) and _unit_included(unit)
    ]
    if not units:
        raise BuilderInputError(
            "every plan_unit is ratified out-of-scope; nothing to brief",
            tag="builder.gary.no-in-scope-units",
        )

    slides: list[dict[str, str]] = []
    recognized_fidelity = frozenset({"creative", "literal-text", "literal-visual"})
    for index, unit in enumerate(units, start=1):
        title = str(unit.get("title") or f"Unit {index}")
        objective = str(unit.get("learning_objective") or "").strip()
        prompt = f"{title} — {objective}" if objective else title
        slide: dict[str, str] = {
            "slide_id": f"slide-{index:02d}",
            "title": title,
            "prompt": prompt,
            "source_ref": str(unit.get("unit_id") or f"unit-{index}"),
        }
        # Irene literal-text supersedes styleguide truncation: carry recognized
        # fidelity onto Gary slides so generate_gamma_variants can force preserve
        # on the literal cohort. Missing/unknown → omit (creative cohort).
        raw_fidelity = str(unit.get("fidelity") or "").strip()
        if raw_fidelity in recognized_fidelity:
            slide["fidelity"] = raw_fidelity
        slides.append(slide)

    expected_refs = [str(unit["unit_id"]) for unit in units]
    actual_refs = [slide["source_ref"] for slide in slides]
    slide_ids = [slide["slide_id"] for slide in slides]
    if actual_refs != expected_refs or len(set(slide_ids)) != len(slide_ids):
        raise BuilderInputError(
            "package slide authority is not a unique ordered plan projection",
            tag="builder.gary.plan-authority-invalid",
        )

    proportions = cd_directive.get("slide_mode_proportions")
    rationale = str(cd_directive.get("creative_rationale") or "").strip()
    instruction_parts = [f"Experience profile: {cd_directive['experience_profile']}."]
    if rationale:
        instruction_parts.append(f"Creative rationale: {rationale}")
    if isinstance(proportions, dict) and proportions:
        rendered = ", ".join(f"{key}={value}" for key, value in sorted(proportions.items()))
        instruction_parts.append(f"Slide mode proportions: {rendered}.")
    # P5-S2 Consumer B: append the enrichment hint to the deck-level instructions
    # ONLY (firewall — never the card body / Studio lock). Absent ⇒ byte-identical.
    if enrichment_hint:
        instruction_parts.append(enrichment_hint)

    package: dict[str, Any] = {
        "slides": slides,
        "prompt": "\n---\n".join(slide["prompt"] for slide in slides),
        "additional_instructions": " ".join(instruction_parts),
    }
    unknown = set(package) - GARY_CONSUMED_PAYLOAD_KEYS
    if unknown:
        raise BuilderInputError(
            f"builder emitted keys outside gary's payload contract: {sorted(unknown)}",
            tag="builder.gary.contract-violation",
        )
    return package


def _deck_enrichment_hint(runs_root: Path | None, trial_id: UUID | str | None) -> str | None:
    """Project the deck enrichment hint from the frozen card (or ``None``).

    ORCHESTRATOR-SIDE projection (Winston A1): the frozen card is read via the
    existing ``g0_enrichment_wiring.load_enrichment_result`` (no third loader). The
    card lives at ``<run_dir>/g0-enrichment.json``, written on the START walk before
    node 01; node 06 (this builder) runs on the continuation walk POST-G1, so the
    artifact is already on disk on whichever walk reaches here (Winston A6). AND-gated
    by the deck flag + card presence; OFF / absent ⇒ ``None`` ⇒ byte-identical deck.
    """
    if runs_root is None or trial_id is None:
        return None
    if not enrichment_consumption.deck_enrichment_active():
        return None
    card = g0_enrichment_wiring.load_enrichment_result(runs_root / str(trial_id))
    return enrichment_consumption.project_deck_enrichment_hint(card)


def run_builder_node(
    *,
    node_id: str,
    production_envelope: ProductionEnvelope,
    runs_root: Path | None = None,
    trial_id: UUID | str | None = None,
) -> ProductionEnvelope:
    """Execute one package builder under the shared Pass-1 generation lock."""
    run_dir = (
        runs_root / str(trial_id)
        if runs_root is not None and trial_id is not None
        else None
    )
    try:
        if run_dir is not None and run_dir.is_dir():
            with pass1_generation_lock(run_dir):
                return _run_builder_node_locked(
                    node_id=node_id,
                    production_envelope=production_envelope,
                    runs_root=runs_root,
                    trial_id=trial_id,
                )
        return _run_builder_node_locked(
            node_id=node_id,
            production_envelope=production_envelope,
            runs_root=runs_root,
            trial_id=trial_id,
        )
    except Pass1GenerationLockError as exc:
        raise BuilderInputError(
            str(exc), tag="builder.gary.plan-authority-invalid"
        ) from exc


def _run_builder_node_locked(
    *,
    node_id: str,
    production_envelope: ProductionEnvelope,
    runs_root: Path | None = None,
    trial_id: UUID | str | None = None,
) -> ProductionEnvelope:
    """Execute the builder registered at ``node_id``; idempotent per node.

    Mirrors the walkers' per-node skip rule: a node that already carries
    its contribution is not rebuilt (resume-safe). Missing upstream
    contributions fail loud with the offending specialist named.

    ``runs_root`` + ``trial_id`` (P5-S2): when supplied, the §06 Gary package picks
    up the orchestrator-projected deck enrichment hint from the frozen G0 card. Both
    default ``None`` for backward compatibility (the non-enriched build is unchanged).
    """
    if node_id not in BUILDER_NODE_IDS:
        raise BuilderInputError(
            f"no package builder registered for manifest node {node_id!r}",
            tag="builder.unknown-node",
        )
    existing_package = production_envelope.get_contribution(
        BUILDER_SPECIALIST_ID, node_id=node_id
    )

    irene = production_envelope.latest_for_specialist("irene_pass1")
    cd = production_envelope.latest_for_specialist("cd")
    missing = [
        name
        for name, contribution in (("irene_pass1", irene), ("cd", cd))
        if contribution is None
    ]
    if missing:
        raise BuilderInputError(
            f"§06 builder missing upstream contribution(s): {', '.join(missing)}",
            tag="builder.gary.upstream-missing",
        )

    lesson_plan = irene.output.get("lesson_plan") or {}
    authority_receipt = irene.output.get("plan_authority_receipt")
    authority_receipt_path = irene.output.get("plan_authority_receipt_path")
    authority_path = (
        runs_root / str(trial_id) / "irene-pass1.plan-authority.json"
        if runs_root is not None and trial_id is not None
        else None
    )
    try:
        persisted_marker = authority_path is not None and (
            authority_path.exists() or authority_path.is_symlink()
        )
        current_markers = (
            authority_receipt is not None
            or authority_receipt_path is not None
            or persisted_marker
        )
        current_format = current_markers or (
            existing_package is not None
            and existing_package.model_used == CURRENT_BUILDER_MODEL_MARKER
        )
        legacy_format = (
            not current_format
            and existing_package is not None
            and existing_package.model_used == BUILDER_MODEL_MARKER
        )
        if not current_format and not legacy_format:
            raise Pass1PlanAuthorityError(
                "Pass-1 contribution has no current receipt or positive legacy evidence"
            )
        if current_format and authority_receipt is None:
            raise Pass1PlanAuthorityError(
                "current Pass-1 contribution is missing its authority receipt"
            )
        if authority_receipt is not None:
            assert_receipt_matches_plan(lesson_plan, authority_receipt)
            if authority_receipt_path is not None and (
                authority_path is None
                or Path(str(authority_receipt_path)).resolve()
                != authority_path.resolve()
            ):
                raise Pass1PlanAuthorityError(
                    "Pass-1 authority receipt path disagrees with run coordinate"
                )
            if authority_path is not None:
                if authority_path.is_symlink() or not authority_path.is_file():
                    raise Pass1PlanAuthorityError(
                        "current Pass-1 authority sidecar is missing or unsafe"
                    )
                persisted = json.loads(
                    read_contained_regular_bytes(
                        authority_path.parent,
                        authority_path,
                        "Pass-1 authority sidecar",
                    ).decode("utf-8"),
                    object_pairs_hook=_unique_json_object,
                )
                if persisted != authority_receipt:
                    raise Pass1PlanAuthorityError(
                        "Pass-1 authority sidecar and contribution disagree"
                    )
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise BuilderInputError(
            f"Pass-1 plan authority validation failed: {exc}",
            tag="builder.gary.plan-authority-invalid",
        ) from exc

    package = build_gary_briefs(
        lesson_plan,
        cd.output.get("cd_directive") or {},
        enrichment_hint=_deck_enrichment_hint(runs_root, trial_id),
    )
    if existing_package is not None:
        if existing_package.output != package:
            raise BuilderInputError(
                "existing §06 package disagrees with current authority projection",
                tag="builder.gary.plan-authority-invalid",
            )
        if current_format and existing_package.model_used == BUILDER_MODEL_MARKER:
            replacement = existing_package.model_copy(
                update={"model_used": CURRENT_BUILDER_MODEL_MARKER}
            )
            contributions = tuple(
                replacement if row is existing_package else row
                for row in production_envelope.contributions
            )
            return production_envelope.model_copy(
                update={"contributions": contributions}
            )
        if current_format and existing_package.model_used != CURRENT_BUILDER_MODEL_MARKER:
            raise BuilderInputError(
                "existing §06 package carries an unknown authority-format marker",
                tag="builder.gary.plan-authority-invalid",
            )
        return production_envelope
    updated = production_envelope.model_copy(deep=True)
    updated.add_contribution(
        SpecialistContribution.from_output(
            specialist_id=BUILDER_SPECIALIST_ID,
            output=package,
            model_used=(
                CURRENT_BUILDER_MODEL_MARKER
                if current_format
                else BUILDER_MODEL_MARKER
            ),
            node_id=node_id,
        )
    )
    return updated


__all__ = [
    "BUILDER_MODEL_MARKER",
    "CURRENT_BUILDER_MODEL_MARKER",
    "BUILDER_NODE_IDS",
    "BUILDER_SPECIALIST_ID",
    "BuilderInputError",
    "GARY_PACKAGE_NODE_ID",
    "build_gary_briefs",
    "run_builder_node",
]
