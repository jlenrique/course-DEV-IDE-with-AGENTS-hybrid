"""Leg-C AC#1 (validator) + AC#8 — scripted-block write-gate + learned-store pin.

RED-first: the validator does not yet inspect the ``scripted`` block. These pin:

- AC#1  unregistered ``scripted`` class -> RED (``gamma.scripted.unknown-class``);
        non-int/negative value -> RED; missing/empty ``rationale`` -> RED;
        missing provenance -> RED; a well-formed scripted entry is clean.
- AC#8  Leg-C adds ZERO learned entries: the Leg-B2 learned store + manifest stay
        empty even with a scripted floor present.

Hermetic: no network (only the --check-existence flag touches the network; these
tests never set it).
"""

from __future__ import annotations

import copy

import pytest

from app.specialists.gary.learned_dependencies import (
    GAMMA_LEARNED_RULES_LOCK_PATH,
    active_learned_rules,
    load_manifest,
)
from scripts.utilities.validate_gamma_style_guides import (
    GAMMA_STYLE_GUIDES_PATH,
    load_style_guides,
    validate_style_guides,
)

pytestmark = pytest.mark.filterwarnings("ignore")


def _runtime_data() -> dict:
    return load_style_guides(GAMMA_STYLE_GUIDES_PATH)


def _well_formed_floor() -> dict:
    return {
        "class": "min_cluster_floor",
        "value": 4,
        "rationale": "This style reads as a multi-beat narrative walk.",
        "provenance": {
            "authoring_styleguide": "classic-freeform-x-cards",
            "envelope_write_stamp": "2026-07-01T00:00:00Z",
        },
    }


def _with_scripted(entry: dict) -> dict:
    data = copy.deepcopy(_runtime_data())
    data["style_guides"]["classic-freeform-x-cards"]["scripted"] = [entry]
    return data


def _with_scripted_entries(entries: list) -> dict:
    data = copy.deepcopy(_runtime_data())
    data["style_guides"]["classic-freeform-x-cards"]["scripted"] = entries
    return data


# --------------------------------------------------------------------------- AC#1
def test_well_formed_scripted_floor_is_clean() -> None:
    errors = validate_style_guides(_with_scripted(_well_formed_floor()))
    assert errors == [], errors


def test_unregistered_scripted_class_is_red() -> None:
    entry = _well_formed_floor()
    entry["class"] = "make_it_pretty"
    errors = validate_style_guides(_with_scripted(entry))
    assert any("gamma.scripted.unknown-class" in e for e in errors), errors


@pytest.mark.parametrize("bad", [-1, 0, "4", 2.5, True])
def test_non_positive_int_value_is_red(bad: object) -> None:
    entry = _well_formed_floor()
    entry["value"] = bad
    errors = validate_style_guides(_with_scripted(entry))
    assert any("scripted" in e and "value" in e for e in errors), errors


@pytest.mark.parametrize("rationale", [None, "", "   "])
def test_missing_rationale_is_red(rationale: object) -> None:
    entry = _well_formed_floor()
    entry["rationale"] = rationale
    errors = validate_style_guides(_with_scripted(entry))
    assert any("rationale" in e.lower() for e in errors), errors


def test_duplicate_scripted_class_is_red() -> None:
    """P6: two entries of the SAME scripted class must RED (currently first-wins
    silently across the 3 readers)."""
    errors = validate_style_guides(
        _with_scripted_entries([_well_formed_floor(), _well_formed_floor()])
    )
    assert any("duplicate" in e.lower() and "min_cluster_floor" in e for e in errors), errors


def test_missing_provenance_is_red() -> None:
    entry = _well_formed_floor()
    entry.pop("provenance")
    errors = validate_style_guides(_with_scripted(entry))
    assert any("provenance" in e.lower() for e in errors), errors


def test_partial_provenance_is_red() -> None:
    entry = _well_formed_floor()
    entry["provenance"] = {"authoring_styleguide": "classic-freeform-x-cards"}
    errors = validate_style_guides(_with_scripted(entry))
    assert any("provenance" in e.lower() for e in errors), errors


# --------------------------------------------------------------------------- AC#8
def test_runtime_yaml_carries_no_learned_entries() -> None:
    data = _runtime_data()
    assert active_learned_rules(data.get("learned_dependencies")) == []
    assert load_manifest(GAMMA_LEARNED_RULES_LOCK_PATH) == []


def test_scripted_floor_introduces_zero_learned_entries() -> None:
    # A styleguide with a scripted floor still contributes ZERO learned rules —
    # the only floor in play comes from the DOCUMENTED scripted class.
    data = _with_scripted(_well_formed_floor())
    assert active_learned_rules(data.get("learned_dependencies")) == []
