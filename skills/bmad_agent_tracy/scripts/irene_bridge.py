import logging
from typing import Any

logger = logging.getLogger(__name__)


class IreneTracyBridge:
    """Bridge connecting Irene's lesson plan output to Tracy's research postures."""

    def __init__(self, posture_dispatcher: Any) -> None:
        self.dispatcher = posture_dispatcher

    def process_plan_locked(self, lesson_plan: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Scan the lesson plan for research intent on in-scope units and dispatch
        each to Tracy.

        DUAL-READ (canonical-arc S6 D7, Fix A): research intent arrives via EITHER
        source, and BOTH are honored (union, provenance-distinct):
          - ``units[].identified_gaps`` — the Gagne ``IdentifiedGap`` path (real
            G1A-curated / smoke-harness), OR
          - ``research_goals[]`` — the real Irene-Pass-1 producer path
            (``collateral.research_goals``, carried in mechanically upstream).

        ⚠️ MECHANICAL FIELD-CARRY ONLY (binding J1 quality fence): a research goal
        contributes its ``pedagogical_intent`` SEED, its ``binds_to_objective_id``
        target, and its ``goal_id`` provenance — nothing else. It decides NO
        research KIND / relevance / gap_type / posture; the posture selector +
        Texas own research QUALITY unchanged.
        """
        results = []
        units = lesson_plan.get("units") or []
        for unit in units:
            if not isinstance(unit, dict):
                continue
            scope_decision = unit.get("scope_decision")
            if scope_decision != "in-scope":
                continue

            gaps = unit.get("identified_gaps") or []
            for gap in gaps:
                if not isinstance(gap, dict):
                    continue
                brief = {
                    "gap_type": gap.get("type"),
                    "scope_decision": scope_decision,
                    "target_element": unit.get("id", ""),
                    "gap_description": gap.get("description", ""),
                    "claim": gap.get("claim", ""),
                    "source_context": gap.get("source_context", ""),
                    "enrichment_type": gap.get("enrichment_type", "general"),
                    "content_type": gap.get("content_type", "explanation"),
                    "scope": gap.get("scope", "unit"),
                }
                # Remove None or empty string keys without dropping legitimate falsy values
                brief = {k: v for k, v in brief.items() if v is not None and v != ""}
                # Ensure scope_decision is always present
                brief["scope_decision"] = scope_decision

                try:
                    res = self.dispatcher.select_posture(brief)
                    results.append(res)
                except Exception as e:
                    logger.exception("Failed to dispatch Tracy posture for gap")
                    results.append({"status": "failed", "reason": str(e), "gap": gap})

        # S6 D7 — collateral.research_goals[] (the real Irene-Pass-1 path). Each
        # goal is a MECHANICAL field-carry: pedagogical_intent SEED -> the shaping
        # seed, binds_to_objective_id -> the target element, goal_id -> provenance.
        research_goals = lesson_plan.get("research_goals") or []
        for goal in research_goals:
            if not isinstance(goal, dict):
                continue
            brief = {
                # provenance: carried through so the dispatched intent traces back
                # to collateral.research_goals (never a quality decision).
                "research_goal_id": goal.get("goal_id", ""),
                # the pedagogical_intent SEED drives the shaping (never a raw query).
                "gap_description": goal.get("pedagogical_intent", ""),
                # binds_to_objective_id is the target element (optional).
                "target_element": goal.get("binds_to_objective_id") or "",
            }
            brief = {k: v for k, v in brief.items() if v is not None and v != ""}
            # research_goals are lesson-scoped enrichment intent — always in-scope.
            brief["scope_decision"] = "in-scope"

            try:
                res = self.dispatcher.select_posture(brief)
                results.append(res)
            except Exception as e:
                logger.exception("Failed to dispatch Tracy posture for research goal")
                results.append({"status": "failed", "reason": str(e), "goal": goal})

        return results

    def process_dials(self, plan_unit: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Dispatch to Tracy based on dial operator endorsements.
        """
        results = []
        dials = plan_unit.get("dials") or {}
        if not isinstance(dials, dict):
            return results

        for dial_name, endorsement in dials.items():
            # Support both boolean flags and dictionary objects for endorsements
            is_endorsed = False
            if isinstance(endorsement, bool):
                is_endorsed = endorsement
            elif isinstance(endorsement, dict):
                is_endorsed = bool(endorsement.get("endorsed"))

            if is_endorsed:
                brief = {
                    "dial": dial_name,
                    "target_element": plan_unit.get("id", ""),
                    "scope_decision": plan_unit.get("scope_decision", "in-scope"),
                }
                try:
                    res = self.dispatcher.select_posture(brief)
                    results.append(res)
                except Exception as e:
                    logger.exception("Failed to dispatch Tracy posture for dial %s", dial_name)
                    results.append({"status": "failed", "reason": str(e), "dial": dial_name})

        return results
