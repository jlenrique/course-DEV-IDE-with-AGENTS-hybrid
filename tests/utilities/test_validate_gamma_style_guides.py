"""Leg-A AC#1/#2 — hermetic offline audit of the CD-owned styleguide library.

RED-first: the validator + runtime YAML do not exist yet. These pin the
inverted-polarity completeness teeth, the discriminated-union surface violation,
the frozen-enum reuse, and the roster floor. NO network (the only network path is
behind --check-existence, which these tests never touch).
"""

from __future__ import annotations

import copy

import pytest

from app.specialists.gary.styleguide_library import StyleguideError
from scripts.utilities.validate_gamma_style_guides import (
    GAMMA_STYLE_GUIDES_PATH,
    load_style_guides,
    validate_style_guides,
)

pytestmark = pytest.mark.filterwarnings("ignore")


def _runtime_data() -> dict:
    return load_style_guides(GAMMA_STYLE_GUIDES_PATH)


def test_runtime_yaml_loads_and_passes_offline() -> None:
    data = _runtime_data()
    errors = validate_style_guides(data)  # check_existence defaults OFF (no network)
    assert errors == [], f"runtime styleguide library is not copacetic: {errors}"


def test_two_proof_seeds_present_and_clean() -> None:
    data = _runtime_data()
    guides = data["style_guides"]
    assert "classic-freeform-x-cards" in guides
    assert "hil-2026-apc-studio-image-card" in guides
    # classic proof seed is PURE representation: dimensions fluid, NO forced 16:9.
    classic = guides["classic-freeform-x-cards"]
    assert classic["production_mode"] == "api"
    assert classic["page_settings"]["card_options"]["dimensions"] == "fluid"
    studio = guides["hil-2026-apc-studio-image-card"]
    assert studio["production_mode"] == "studio"
    assert studio["studio_template"]["gamma_id"] == "g_nv5q4da69qiiu8q"


def test_roster_floor_requires_classic_and_studio() -> None:
    data = _runtime_data()
    # Drop every studio guide -> roster floor must fail.
    stripped = copy.deepcopy(data)
    stripped["style_guides"] = {
        name: rec
        for name, rec in stripped["style_guides"].items()
        if rec.get("production_mode") != "studio"
    }
    errors = validate_style_guides(stripped)
    assert any("roster" in e.lower() and "studio" in e.lower() for e in errors), errors


def test_inverted_polarity_null_required_field_fails() -> None:
    data = _runtime_data()
    broken = copy.deepcopy(data)
    # Null out a REQUIRED surface field on the classic proof seed.
    broken["style_guides"]["classic-freeform-x-cards"]["theme"]["id"] = None
    errors = validate_style_guides(broken)
    assert any("theme" in e.lower() for e in errors), errors


def test_inverted_polarity_default_sentinel_fails() -> None:
    data = _runtime_data()
    broken = copy.deepcopy(data)
    # A "default" sentinel on a required field is as bad as null (inverted polarity).
    broken["style_guides"]["classic-freeform-x-cards"]["page_settings"][
        "card_options"
    ]["dimensions"] = "default"
    errors = validate_style_guides(broken)
    assert any("dimension" in e.lower() for e in errors), errors


def test_studio_carrying_classic_key_is_surface_violation() -> None:
    data = _runtime_data()
    broken = copy.deepcopy(data)
    studio = broken["style_guides"]["hil-2026-apc-studio-image-card"]
    # Inject a Classic-only page setting onto a studio guide.
    studio.setdefault("page_settings", {}).setdefault("card_options", {})[
        "dimensions"
    ] = "16x9"
    errors = validate_style_guides(broken)
    assert any("surface-violation" in e for e in errors), errors


def test_invalid_enum_value_fails_against_frozen_enum() -> None:
    data = _runtime_data()
    broken = copy.deepcopy(data)
    broken["style_guides"]["classic-freeform-x-cards"]["page_settings"][
        "card_options"
    ]["dimensions"] = "cinemascope"  # not in CARD_DIMENSION_VALUES
    errors = validate_style_guides(broken)
    assert any("dimension" in e.lower() for e in errors), errors


def test_missing_triad_rationale_fails_coherence() -> None:
    data = _runtime_data()
    broken = copy.deepcopy(data)
    broken["style_guides"]["classic-freeform-x-cards"]["presentation"]["narrative"][
        "triad_rationale"
    ] = ""
    errors = validate_style_guides(broken)
    assert any("triad" in e.lower() or "coherence" in e.lower() for e in errors), errors


def test_load_missing_file_raises_styleguide_error(tmp_path) -> None:
    # Item #2: a load/parse failure must be inside the StyleguideError family so
    # Gary's `except StyleguideError` recoverable path can catch it (never a bare
    # ValueError/FileNotFoundError/YAMLError that crashes the walk uncatchably).
    with pytest.raises(StyleguideError) as exc:
        load_style_guides(tmp_path / "does-not-exist.yaml")
    assert exc.value.tag == "gamma.styleguide.load-error"


def test_load_malformed_yaml_raises_styleguide_error(tmp_path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("style_guides: [unterminated\n", encoding="utf-8")
    with pytest.raises(StyleguideError) as exc:
        load_style_guides(bad)
    assert exc.value.tag == "gamma.styleguide.load-error"


def test_load_non_mapping_top_level_raises_styleguide_error(tmp_path) -> None:
    bad = tmp_path / "list.yaml"
    bad.write_text("- just\n- a\n- list\n", encoding="utf-8")
    with pytest.raises(StyleguideError) as exc:
        load_style_guides(bad)
    assert exc.value.tag == "gamma.styleguide.load-error"


def test_studio_carrying_theme_is_surface_violation() -> None:
    # Item #3(a): a studio record carrying a Classic-only foundational `theme` block
    # (theme is the api authority) must FAIL with surface-violation.
    data = _runtime_data()
    broken = copy.deepcopy(data)
    studio = broken["style_guides"]["hil-2026-apc-studio-image-card"]
    studio["theme"] = {"id": "njim9kuhfnljvaa", "name": "leaked theme"}
    errors = validate_style_guides(broken)
    assert any("surface-violation" in e for e in errors), errors


def test_studio_carrying_visuals_image_source_is_surface_violation() -> None:
    # Item #3(a): a studio record carrying a Classic visuals directive (image_source)
    # must FAIL with surface-violation — the template is the sole style authority.
    data = _runtime_data()
    broken = copy.deepcopy(data)
    studio = broken["style_guides"]["hil-2026-apc-studio-image-card"]
    studio.setdefault("prompt_configuration", {}).setdefault("visuals", {})[
        "image_source"
    ] = "aiGenerated"
    errors = validate_style_guides(broken)
    assert any("surface-violation" in e for e in errors), errors


def test_custom_style_preset_without_custom_style_fails() -> None:
    # Item #6: `style_preset: custom` with no `custom_style` crashes Gary at dispatch
    # (`image_style is required when image_style_preset='custom'`); the offline
    # write-gate must reject it at write time, not defer the crash to render.
    data = _runtime_data()
    broken = copy.deepcopy(data)
    visuals = broken["style_guides"]["classic-freeform-x-cards"]["prompt_configuration"][
        "visuals"
    ]
    visuals["style_preset"] = "custom"
    visuals["custom_style"] = None
    errors = validate_style_guides(broken)
    assert any("custom" in e.lower() for e in errors), errors
