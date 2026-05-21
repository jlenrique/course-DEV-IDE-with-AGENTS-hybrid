"""SG-1 structural enforcement for the vocabulary specialist roster."""

from __future__ import annotations

from app.models.decision_cards import SpecialistId


def test_specialist_roster_is_exactly_eleven() -> None:
    assert len(list(SpecialistId)) == 11, "SG-1 floor violation"
    expected = {
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
    }
    assert {specialist.value for specialist in SpecialistId} == expected
