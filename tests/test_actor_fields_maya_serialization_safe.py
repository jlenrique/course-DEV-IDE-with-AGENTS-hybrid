"""AC-T.15 — Two-level actor serialization safety (R2 rider S-4).

Asserts that the Maya-facing default serialization surface of ScopeDecision
and ScopeDecisionTransition NEVER leaks the private internal actor taxonomy
(``marcus``, ``marcus-intake``, ``marcus-orchestrator``, ``irene``).

The internal audit surface is intentionally reachable — but only through the
explicit ``to_audit_dump()`` helper, NOT the default ``model_dump`` /
``model_dump_json``.
"""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime

from app.marcus.lesson_plan.events import ScopeDecisionTransition
from app.marcus.lesson_plan.schema import ScopeDecision

FORBIDDEN_VALUES = ("marcus", "marcus-intake", "marcus-orchestrator", "irene")


def _assert_no_internal_values(payload: dict | str) -> None:
    # Convert with a string-coercing default so datetime values don't break json.dumps.
    text = payload if isinstance(payload, str) else json.dumps(payload, default=str)
    for forbidden in FORBIDDEN_VALUES:
        # Match as a whole VALUE (wrap in quotes to reject substring hits from
        # future innocuous string content; internal actor Literals are exact).
        pattern = rf'"{re.escape(forbidden)}"'
        assert not re.search(pattern, text), (
            f"Maya-facing serialization leaked internal actor value {forbidden!r}. "
            f"The internal_* fields MUST use Field(exclude=True); the default "
            f"dump must expose only the public 'system' | 'operator' surface."
        )


def _build_scope_decision(internal: str) -> ScopeDecision:
    return ScopeDecision(
        state="proposed",
        scope="in-scope",
        proposed_by="system",
        _internal_proposed_by=internal,
    )


def _build_transition(internal: str) -> ScopeDecisionTransition:
    return ScopeDecisionTransition(
        unit_id="gagne-event-1",
        plan_revision=0,
        from_state="proposed",
        to_state="ratified",
        from_scope="in-scope",
        to_scope="in-scope",
        actor="system" if internal != "maya" else "operator",
        _internal_actor=internal,
        timestamp=datetime.now(tz=UTC),
        rationale_snapshot="",
    )


def test_scope_decision_model_dump_never_leaks_internal() -> None:
    for internal in FORBIDDEN_VALUES:
        sd = _build_scope_decision(internal)
        dumped = sd.model_dump()
        _assert_no_internal_values(dumped)
        assert sd.proposed_by == "system"  # public surface only


def test_scope_decision_model_dump_json_never_leaks_internal() -> None:
    for internal in FORBIDDEN_VALUES:
        sd = _build_scope_decision(internal)
        _assert_no_internal_values(sd.model_dump_json())


def test_transition_model_dump_never_leaks_internal() -> None:
    for internal in FORBIDDEN_VALUES:
        tr = _build_transition(internal)
        _assert_no_internal_values(tr.model_dump())


def test_transition_model_dump_json_never_leaks_internal() -> None:
    for internal in FORBIDDEN_VALUES:
        tr = _build_transition(internal)
        _assert_no_internal_values(tr.model_dump_json())


def test_scope_decision_to_audit_dump_includes_internal() -> None:
    """The audit surface IS reachable — explicitly, not by default."""
    sd = _build_scope_decision("marcus-orchestrator")
    audit = sd.to_audit_dump()
    assert audit["_internal_proposed_by"] == "marcus-orchestrator"


def test_transition_to_audit_dump_includes_internal() -> None:
    tr = _build_transition("irene")
    audit = tr.to_audit_dump()
    assert audit["_internal_actor"] == "irene"
