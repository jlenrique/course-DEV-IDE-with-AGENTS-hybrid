"""Vocabulary registry load pins for Story 7a.6."""

from __future__ import annotations

from app.models.decision_cards import load_vocabulary_registry


def test_vocabulary_registry_loads_successfully() -> None:
    registry = load_vocabulary_registry()
    assert registry["schema_version"] == "1.0"


def test_vocabulary_registry_has_three_namespaces() -> None:
    registry = load_vocabulary_registry()
    assert set(registry["namespaces"]) == {"gates", "specialists", "shared"}


def test_gate_decision_and_directive_tokens_are_non_empty_closed_lists() -> None:
    tokens = load_vocabulary_registry()["namespaces"]["gates"]["tokens"]
    assert tokens["decision"] == [
        "confirm",
        "revise",
        "reject",
        "escape",
        "skip-slide",
        "abort-run",
    ]
    assert tokens["directive"] == [
        "accept-as-is",
        "apply-edit",
        "re-emit",
        "halt-for-repair",
    ]


def test_specialist_roster_has_exactly_eleven_entries() -> None:
    roster = load_vocabulary_registry()["namespaces"]["specialists"]["tokens"]["roster"]
    assert roster == [
        "texas",
        "irene",
        "dan",
        "tracy",
        "gary",
        "kira",
        "wanda",
        "enrique",
        "compositor",
        "quinn_r",
        "vera",
    ]
