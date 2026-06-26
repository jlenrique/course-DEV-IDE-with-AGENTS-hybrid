"""S2 — ComponentSelection canonical record + serialization."""

from __future__ import annotations

import pytest

from app.models.state.component_selection import ComponentSelection


def test_defaults_are_deck_only_base() -> None:
    sel = ComponentSelection()
    assert sel.deck is True
    assert sel.motion is False
    assert sel.workbook is False


def test_production_default_is_deck_plus_motion() -> None:
    sel = ComponentSelection.production_default()
    assert sel.as_map() == {"deck": True, "motion": True, "workbook": False}


def test_selected_components_is_sorted_subset() -> None:
    sel = ComponentSelection(deck=True, motion=True, workbook=False)
    assert sel.selected_components() == ("deck", "motion")
    full = ComponentSelection(deck=True, motion=True, workbook=True)
    assert full.selected_components() == ("deck", "motion", "workbook")


def test_canonical_bytes_is_sorted_and_stable() -> None:
    sel = ComponentSelection(deck=True, motion=True, workbook=False)
    assert sel.canonical_bytes() == b'{"deck":true,"motion":true,"workbook":false}'
    # Independent of construction order — canonical-JSON sorts keys.
    other = ComponentSelection(workbook=False, motion=True, deck=True)
    assert other.canonical_bytes() == sel.canonical_bytes()


def test_selection_is_frozen_immutable() -> None:
    sel = ComponentSelection.production_default()
    with pytest.raises(Exception):  # noqa: B017 — pydantic frozen raises ValidationError
        sel.motion = False  # type: ignore[misc]


def test_extra_fields_forbidden() -> None:
    with pytest.raises(Exception):  # noqa: B017
        ComponentSelection(deck=True, podcast=True)  # type: ignore[call-arg]
