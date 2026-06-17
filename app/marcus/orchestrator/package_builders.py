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

from typing import Any

from app.models.runtime.production_envelope import (
    ProductionEnvelope,
    SpecialistContribution,
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
    lesson_plan: dict[str, Any], cd_directive: dict[str, Any]
) -> dict[str, Any]:
    """Project a ratified lesson plan + creative directive into Gary's vocabulary.

    Output keys are a strict subset of gary's CONSUMED_PAYLOAD_KEYS (S1
    contract regime); the subset relation is both asserted here (belt) and
    pinned by the package-builder ratchet (suspenders).
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
    for index, unit in enumerate(units, start=1):
        title = str(unit.get("title") or f"Unit {index}")
        objective = str(unit.get("learning_objective") or "").strip()
        prompt = f"{title} — {objective}" if objective else title
        slides.append(
            {
                "slide_id": f"slide-{index:02d}",
                "title": title,
                "prompt": prompt,
                "source_ref": str(unit.get("unit_id") or f"unit-{index}"),
            }
        )

    proportions = cd_directive.get("slide_mode_proportions")
    rationale = str(cd_directive.get("creative_rationale") or "").strip()
    instruction_parts = [f"Experience profile: {cd_directive['experience_profile']}."]
    if rationale:
        instruction_parts.append(f"Creative rationale: {rationale}")
    if isinstance(proportions, dict) and proportions:
        rendered = ", ".join(f"{key}={value}" for key, value in sorted(proportions.items()))
        instruction_parts.append(f"Slide mode proportions: {rendered}.")

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


def run_builder_node(
    *, node_id: str, production_envelope: ProductionEnvelope
) -> ProductionEnvelope:
    """Execute the builder registered at ``node_id``; idempotent per node.

    Mirrors the walkers' per-node skip rule: a node that already carries
    its contribution is not rebuilt (resume-safe). Missing upstream
    contributions fail loud with the offending specialist named.
    """
    if node_id not in BUILDER_NODE_IDS:
        raise BuilderInputError(
            f"no package builder registered for manifest node {node_id!r}",
            tag="builder.unknown-node",
        )
    if production_envelope.get_contribution(BUILDER_SPECIALIST_ID, node_id=node_id) is not None:
        return production_envelope

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

    package = build_gary_briefs(
        irene.output.get("lesson_plan") or {},
        cd.output.get("cd_directive") or {},
    )
    updated = production_envelope.model_copy(deep=True)
    updated.add_contribution(
        SpecialistContribution.from_output(
            specialist_id=BUILDER_SPECIALIST_ID,
            output=package,
            model_used=BUILDER_MODEL_MARKER,
            node_id=node_id,
        )
    )
    return updated


__all__ = [
    "BUILDER_MODEL_MARKER",
    "BUILDER_NODE_IDS",
    "BUILDER_SPECIALIST_ID",
    "BuilderInputError",
    "GARY_PACKAGE_NODE_ID",
    "build_gary_briefs",
    "run_builder_node",
]
