"""AC-T.1 — ScopeDecision / ScopeDecisionTransition / EventEnvelope shape-pin (R2 AM-1).

Third of three shape-family pin files. Own snapshot + own changelog entry.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.marcus.lesson_plan.events import EventEnvelope, ScopeDecisionTransition
from app.marcus.lesson_plan.schema import ScopeDecision

FIXTURES = Path(__file__).parent / "fixtures" / "lesson_plan"
CHANGELOG = (
    Path(__file__).parents[2]
    / "_bmad-output"
    / "implementation-artifacts"
    / "SCHEMA_CHANGELOG.md"
)


def _load_snapshot(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _field_names(model_cls) -> set[str]:
    return set(model_cls.model_fields.keys())


SNAPSHOT = _load_snapshot("scope_shape_v1_0.json")


def test_scope_decision_fields_match_snapshot() -> None:
    expected = set(SNAPSHOT["fields"]["ScopeDecision"])
    actual = _field_names(ScopeDecision)
    assert actual == expected, (
        f"ScopeDecision schema drift. Missing: {expected - actual}. "
        f"New: {actual - expected}."
    )


def test_scope_decision_transition_fields_match_snapshot() -> None:
    expected = set(SNAPSHOT["fields"]["ScopeDecisionTransition"])
    actual = _field_names(ScopeDecisionTransition)
    assert actual == expected


def test_event_envelope_fields_match_snapshot() -> None:
    expected = set(SNAPSHOT["fields"]["EventEnvelope"])
    actual = _field_names(EventEnvelope)
    assert actual == expected


def test_schema_changelog_pins_scope_decision_v1_0() -> None:
    text = CHANGELOG.read_text(encoding="utf-8")
    assert "Scope Decision v1.0" in text, (
        "SCHEMA_CHANGELOG.md does not pin `Scope Decision v1.0` — per R2 AM-1 the "
        "scope_decision / scope_decision_transition / event_envelope shape family "
        "requires its own changelog entry."
    )
