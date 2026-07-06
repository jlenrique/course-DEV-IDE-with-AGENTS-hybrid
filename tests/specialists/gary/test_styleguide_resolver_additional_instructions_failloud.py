"""Resolver fail-loud on present-but-invalid additional_instructions (review finding P2).

The Gary production resolver (`expand_record` → `_expand_api`) used to SILENTLY SKIP a
malformed `prompt_configuration.additional_instructions` (non-list), so an invalid registry
edit that bypassed the write-gate validator would drop the authored style prose with no
signal. That violates the fail-loud / never-silent-drop invariant. The resolver now mirrors
the validator's AC-1 rule (validate_gamma_style_guides.py::_validate_additional_instructions_shape)
byte-for-byte: absent ⇒ key-absent; present ⇒ MUST be a non-empty list of non-empty strings,
else StyleguideError (error-pause on the live path).
"""

from __future__ import annotations

import copy

import pytest

from app.specialists.gary.styleguide_library import (
    ADDITIONAL_INSTRUCTIONS_TAG,
    StyleguideError,
    expand_record,
    load_style_guides,
)


def _base_api_record() -> dict:
    """A complete, valid production_mode=api record to mutate in isolation."""
    guides = load_style_guides()["style_guides"]
    return copy.deepcopy(guides["hil-2026-apc-crossroads-classic"])


def test_absent_additional_instructions_resolves_clean() -> None:
    rec = _base_api_record()
    rec["prompt_configuration"].pop("additional_instructions", None)
    out = expand_record(rec, name="t")
    assert "additional_instructions" not in out


def test_valid_nonempty_list_resolves_and_strips() -> None:
    rec = _base_api_record()
    rec["prompt_configuration"]["additional_instructions"] = [
        "  Keep it warm.  ",
        "One idea per card.",
    ]
    out = expand_record(rec, name="t")
    assert out["additional_instructions"] == ["Keep it warm.", "One idea per card."]


def test_non_list_fails_loud() -> None:
    rec = _base_api_record()
    rec["prompt_configuration"]["additional_instructions"] = "a bare string, not a list"
    with pytest.raises(StyleguideError) as ei:
        expand_record(rec, name="t")
    assert ei.value.tag == ADDITIONAL_INSTRUCTIONS_TAG


def test_empty_list_resolves_absent() -> None:
    # `[]` is the intentional "unset" ergonomic (additive-safe): no prose to drop, so key
    # ABSENT — NOT a fail-loud case (matches test_style_additional_instructions_channel).
    rec = _base_api_record()
    rec["prompt_configuration"]["additional_instructions"] = []
    out = expand_record(rec, name="t")
    assert "additional_instructions" not in out


def test_blank_only_list_resolves_absent() -> None:
    # A list of only-blank strings cleans to empty ⇒ unset ⇒ key ABSENT (not fail-loud).
    rec = _base_api_record()
    rec["prompt_configuration"]["additional_instructions"] = ["   ", ""]
    out = expand_record(rec, name="t")
    assert "additional_instructions" not in out


def test_blank_string_among_real_entries_is_filtered_not_raised() -> None:
    rec = _base_api_record()
    rec["prompt_configuration"]["additional_instructions"] = ["keep this", "  "]
    out = expand_record(rec, name="t")
    assert out["additional_instructions"] == ["keep this"]


def test_non_string_entry_fails_loud() -> None:
    # A non-STRING entry is a genuine malformation (would be silently coerced/dropped).
    rec = _base_api_record()
    rec["prompt_configuration"]["additional_instructions"] = ["ok", 123]
    with pytest.raises(StyleguideError) as ei:
        expand_record(rec, name="t")
    assert ei.value.tag == ADDITIONAL_INSTRUCTIONS_TAG
