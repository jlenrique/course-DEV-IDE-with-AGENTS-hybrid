"""Write-gate coverage for the first-class ``additional_instructions`` field.

RED-first (green-light party 2026-07-02):
- AC-1: the OPTIONAL ``prompt_configuration.additional_instructions`` is validated
  as a list of non-empty strings for BOTH api + studio records; absent ⇒ clean;
  wrong type / empty / blank item ⇒ RED. It is NOT a Classic-surface violation.
- AC-5: advances the filed ``gamma-prose-vs-param-noncontradiction-validator`` —
  prose that CONTRADICTS a structured param ⇒ ERROR; prose that merely ECHOES
  Gary's hardcoded card rule ⇒ WARN. Conservative first cut; the runtime SSOT is
  byte-unchanged and trips neither.
"""

from __future__ import annotations

import copy

import pytest

from scripts.utilities.validate_gamma_style_guides import (
    GAMMA_STYLE_GUIDES_PATH,
    load_style_guides,
    validate_style_guides,
    validate_style_guides_full,
)

pytestmark = pytest.mark.filterwarnings("ignore")

_CLASSIC = "classic-freeform-x-cards"  # api: style_preset=illustration, source=aiGenerated
_STUDIO = "hil-2026-apc-studio-image-card"


def _data() -> dict:
    return load_style_guides(GAMMA_STYLE_GUIDES_PATH)


def _set_ai(guide: dict, value: object) -> None:
    guide.setdefault("prompt_configuration", {})["additional_instructions"] = value


# --- runtime SSOT stays copacetic (additive-safe) ---------------------------
def test_runtime_yaml_still_passes_with_studio_annotation() -> None:
    # The studio record's real template-lock annotation must remain write-gate valid.
    errors = validate_style_guides(_data())
    assert errors == [], errors


# --- AC-1 shape validation (both modes) -------------------------------------
def test_valid_list_of_strings_is_accepted() -> None:
    data = copy.deepcopy(_data())
    _set_ai(data["style_guides"][_CLASSIC], ["Keep a calm clinical register."])
    errors = validate_style_guides(data)
    assert errors == [], errors


@pytest.mark.parametrize(
    "bad",
    [
        "a bare string not a list",
        [],  # empty list
        ["ok", ""],  # blank item
        ["ok", 5],  # non-string item
    ],
)
def test_malformed_additional_instructions_fails(bad: object) -> None:
    data = copy.deepcopy(_data())
    _set_ai(data["style_guides"][_CLASSIC], bad)
    errors = validate_style_guides(data)
    assert any("additional-instructions" in e for e in errors), errors


def test_studio_additional_instructions_shape_is_validated_and_not_surface_violation() -> None:
    data = copy.deepcopy(_data())
    # A malformed studio annotation is caught by shape validation ...
    _set_ai(data["style_guides"][_STUDIO], "bare string")
    errors = validate_style_guides(data)
    assert any("additional-instructions" in e for e in errors), errors
    # ... but a well-formed one is NOT a surface violation (shared field, not Classic-only).
    data2 = copy.deepcopy(_data())
    _set_ai(data2["style_guides"][_STUDIO], ["Preserve the template composition."])
    errors2 = validate_style_guides(data2)
    assert not any("surface-violation" in e for e in errors2), errors2
    assert not any("additional-instructions" in e for e in errors2), errors2


# --- AC-5 non-contradiction write-gate --------------------------------------
def test_photographic_prose_contradicts_illustration_preset() -> None:
    data = copy.deepcopy(_data())
    _set_ai(data["style_guides"][_CLASSIC], ["Render each card as a photorealistic photograph."])
    errors = validate_style_guides(data)
    assert any("gamma.prose.contradicts-param" in e for e in errors), errors


def test_stock_photo_prose_contradicts_ai_generated_source() -> None:
    data = copy.deepcopy(_data())
    _set_ai(data["style_guides"][_CLASSIC], ["Use stock photos from a commercial library."])
    errors = validate_style_guides(data)
    assert any("gamma.prose.contradicts-param" in e for e in errors), errors


def test_illustration_prose_contradicts_photorealistic_preset() -> None:
    data = copy.deepcopy(_data())
    guide = data["style_guides"][_CLASSIC]
    guide["prompt_configuration"]["visuals"]["style_preset"] = "photorealistic"
    _set_ai(guide, ["Draw everything as flat vector line art."])
    errors = validate_style_guides(data)
    assert any("gamma.prose.contradicts-param" in e for e in errors), errors


def test_card_rule_echo_is_a_warning_not_an_error() -> None:
    data = copy.deepcopy(_data())
    _set_ai(data["style_guides"][_CLASSIC], ["Produce exactly one card per section."])
    errors, warnings = validate_style_guides_full(data)
    # A mere echo of Gary's mechanical card rule is a WARN (advisory), not a hard error.
    assert not any("gamma.prose" in e for e in errors), errors
    assert any("gamma.prose.echoes-param" in w for w in warnings), warnings


def test_benign_prose_trips_neither() -> None:
    data = copy.deepcopy(_data())
    _set_ai(data["style_guides"][_CLASSIC], ["Keep a calm, spacious clinical register throughout."])
    errors, warnings = validate_style_guides_full(data)
    assert not any("gamma.prose" in e for e in errors), errors
    assert not any("gamma.prose" in w for w in warnings), warnings


# --- code-review remediation: false-positive guards (word-boundary + negation) ---
@pytest.mark.parametrize(
    "prose",
    [
        "Explain photosynthesis with clear diagrams.",  # 'photo' substring, not photographic
        "Illustrate the telephoto lens concept.",  # 'photo' mid-word
        "Never use photographs; keep everything illustrated.",  # negated photographic prose
    ],
)
def test_illustration_preset_does_not_false_positive(prose: str) -> None:
    data = copy.deepcopy(_data())
    _set_ai(data["style_guides"][_CLASSIC], [prose])  # classic preset = illustration
    errors = validate_style_guides(data)
    assert not any("gamma.prose.contradicts-param" in e for e in errors), errors


def test_photorealistic_preset_not_flagged_on_math_vector() -> None:
    data = copy.deepcopy(_data())
    guide = data["style_guides"][_CLASSIC]
    guide["prompt_configuration"]["visuals"]["style_preset"] = "photorealistic"
    _set_ai(guide, ["Show the vector field and scalar gradient clearly."])
    errors = validate_style_guides(data)
    assert not any("gamma.prose.contradicts-param" in e for e in errors), errors


def test_card_rule_echo_not_warned_on_studio_prose() -> None:
    # Studio prose is never emitted (template-lock-only) — the card-rule echo WARN
    # is meaningless there and must not fire (code-review C).
    data = copy.deepcopy(_data())
    _set_ai(data["style_guides"][_STUDIO], ["Keep exactly one card per section, verbatim."])
    _errors, warnings = validate_style_guides_full(data)
    assert not any("gamma.prose.echoes-param" in w for w in warnings), warnings
