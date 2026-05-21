"""Shape pins for the Story 7a.6 vocabulary decision-card schema."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from app.models.decision_cards import (
    VocabularyDecisionCard,
    decision_card_schema_text,
)

_GOLDEN_PATH = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "decision_cards"
    / "decision_card_golden.json"
)
_SCHEMA_PATH = (
    Path(__file__).resolve().parents[3]
    / "app"
    / "models"
    / "schemas"
    / "decision_cards.schema.json"
)


def test_valid_card_constructs_from_golden_fixture() -> None:
    card = VocabularyDecisionCard.model_validate_json(_GOLDEN_PATH.read_text(encoding="utf-8"))
    assert card.decision.value == "confirm"
    assert card.directive.value == "accept-as-is"


def test_unknown_decision_token_raises_validation_error() -> None:
    with pytest.raises(ValidationError):
        VocabularyDecisionCard(
            decision="auto-approve",
            directive="accept-as-is",
            rationale="Operator rationale meets the twenty character floor.",
        )


def test_unknown_directive_token_raises_validation_error() -> None:
    with pytest.raises(ValidationError):
        VocabularyDecisionCard(
            decision="confirm",
            directive="silently-continue",
            rationale="Operator rationale meets the twenty character floor.",
        )


def test_extra_field_raises_validation_error() -> None:
    with pytest.raises(ValidationError):
        VocabularyDecisionCard(
            decision="confirm",
            directive="accept-as-is",
            rationale="Operator rationale meets the twenty character floor.",
            decison="typo",
        )


def test_short_rationale_raises_validation_error() -> None:
    with pytest.raises(ValidationError):
        VocabularyDecisionCard(
            decision="confirm",
            directive="accept-as-is",
            rationale="too short",
        )


def test_emitted_json_schema_is_byte_identical_to_tree_fixture() -> None:
    assert decision_card_schema_text() == _SCHEMA_PATH.read_text(encoding="utf-8")


def test_schema_carries_closed_enum_and_additional_properties_false() -> None:
    schema = VocabularyDecisionCard.model_json_schema()
    assert schema["additionalProperties"] is False
    assert schema["properties"]["decision"]["$ref"] == "#/$defs/GateDecisionToken"
    assert schema["properties"]["directive"]["$ref"] == "#/$defs/GateDirectiveToken"
    assert schema["properties"]["rationale"]["minLength"] == 20
