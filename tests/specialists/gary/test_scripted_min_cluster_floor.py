"""Leg-C AC#1/#2 — scripted-only accessor + leak guard.

RED-first: the ``resolve_scripted`` accessor + the sealed ``SCRIPTED_ENUM_CLASSES``
registry do not exist yet. These pin:

- AC#1  ``min_cluster_floor`` is a registered ``scripted`` class; the accessor
        returns the typed positive int; an unregistered class -> RED
        (``gamma.scripted.unknown-class``); a non-int/negative value -> RED.
- AC#2  leak guard: a ``min_cluster_floor`` in a styleguide NEVER reaches any
        resolved ``gamma_settings[]`` key (the accessor and Gary's resolver are
        NON-overlapping projections).

Hermetic: no network, no DB.
"""

from __future__ import annotations

import pytest

from app.specialists.gary.styleguide_library import (
    RESOLVED_API_KEYS,
    SCRIPTED_ENUM_CLASSES,
    SCRIPTED_UNKNOWN_CLASS_TAG,
    StyleguideError,
    expand_record,
    resolve_scripted,
)


def _api_record_with_floor(value: object = 5) -> dict:
    return {
        "production_mode": "api",
        "theme": {"id": "njim9kuhfnljvaa"},
        "prompt_configuration": {
            "text_content": {"mode": "condense"},
            "visuals": {"image_source": "aiGenerated", "keywords": ["hero"]},
        },
        "page_settings": {"card_options": {"dimensions": "fluid"}},
        "scripted": [
            {
                "class": "min_cluster_floor",
                "value": value,
                "rationale": "This style reads as a multi-beat narrative walk.",
                "provenance": {
                    "authoring_styleguide": "multi-beat-walk",
                    "envelope_write_stamp": "2026-07-01T00:00:00Z",
                },
            }
        ],
    }


# --------------------------------------------------------------------------- AC#1
def test_min_cluster_floor_is_registered() -> None:
    assert "min_cluster_floor" in SCRIPTED_ENUM_CLASSES


def test_accessor_returns_typed_positive_int() -> None:
    value = resolve_scripted(_api_record_with_floor(5), "min_cluster_floor")
    assert value == 5
    assert isinstance(value, int) and not isinstance(value, bool)


def test_accessor_absent_scripted_returns_none() -> None:
    record = _api_record_with_floor()
    record.pop("scripted")
    assert resolve_scripted(record, "min_cluster_floor") is None


def test_accessor_unknown_class_raises() -> None:
    with pytest.raises(StyleguideError) as exc:
        resolve_scripted(_api_record_with_floor(), "publication_target")
    assert exc.value.tag == SCRIPTED_UNKNOWN_CLASS_TAG


@pytest.mark.parametrize("bad", [-3, 0, "5", 2.5, True, None])
def test_accessor_bad_value_raises(bad: object) -> None:
    with pytest.raises(StyleguideError):
        resolve_scripted(_api_record_with_floor(bad), "min_cluster_floor")


# --------------------------------------------------------------------------- AC#2
def test_floor_never_reaches_resolved_gamma_settings() -> None:
    record = _api_record_with_floor(7)
    resolved = expand_record(record, name="leak-guard")
    # (a) the accessor sees the floor
    assert resolve_scripted(record, "min_cluster_floor") == 7
    # (b) the Gary resolver NEVER emits it — non-overlapping projections
    assert "min_cluster_floor" not in resolved
    assert "min_cluster_floor" not in RESOLVED_API_KEYS
    assert set(resolved) <= RESOLVED_API_KEYS
    # scripted metadata is structurally incapable of reaching the API surface
    assert "scripted" not in resolved
