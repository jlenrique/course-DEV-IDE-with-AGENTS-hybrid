"""Decision-card JSON Schema sync check for Story 7a.6."""

from __future__ import annotations

from pathlib import Path

from app.models.decision_cards import decision_card_schema_text


def test_decision_cards_schema_is_in_sync() -> None:
    schema_path = (
        Path(__file__).resolve().parents[2]
        / "app"
        / "models"
        / "schemas"
        / "decision_cards.schema.json"
    )
    assert decision_card_schema_text() == schema_path.read_text(encoding="utf-8")
