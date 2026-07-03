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


# --------------------------------------------------- Lifecycle (session-07 A1)
_PRE_SESSION_07_PERMANENTS = {
    "classic-freeform-x-cards",
    "hil-2026-apc-blueprint-classic",
    "hil-2026-apc-studio-image-card",
    "leg-c-part3-floor-probe",
    "leg-c-part3-floor-toohigh",
}


def test_runtime_records_carry_explicit_lifecycle() -> None:
    """Every runtime record has an explicit lifecycle; the 5 pre-session-07
    records are retro-marked permanent (Dan's amendment); any candidate carries
    its promotion contract."""
    data = _runtime_data()
    for name, record in data["style_guides"].items():
        lifecycle = record.get("lifecycle")
        assert lifecycle in {"candidate", "permanent", "deprecated"}, (
            f"{name}: runtime record must carry an explicit lifecycle"
        )
        if name in _PRE_SESSION_07_PERMANENTS:
            assert lifecycle == "permanent", (
                f"{name}: pre-session-07 record must be retro-marked permanent"
            )
        if lifecycle == "candidate":
            assert record.get("promotion_criteria"), name
            assert record.get("authored_session"), name


def test_lifecycle_unknown_value_fails() -> None:
    data = _runtime_data()
    broken = copy.deepcopy(data)
    broken["style_guides"]["classic-freeform-x-cards"]["lifecycle"] = "shipped"
    errors = validate_style_guides(broken)
    assert any("gamma.lifecycle.unknown-value" in e for e in errors), errors


def test_lifecycle_candidate_requires_promotion_contract_fields() -> None:
    data = _runtime_data()
    broken = copy.deepcopy(data)
    record = broken["style_guides"]["classic-freeform-x-cards"]
    record["lifecycle"] = "candidate"
    record.pop("promotion_criteria", None)
    record.pop("authored_session", None)
    errors = validate_style_guides(broken)
    assert any("gamma.lifecycle.missing-promotion-criteria" in e for e in errors), errors
    assert any("gamma.lifecycle.missing-authored-session" in e for e in errors), errors


def test_lifecycle_candidate_with_contract_fields_is_clean() -> None:
    data = _runtime_data()
    patched = copy.deepcopy(data)
    record = patched["style_guides"]["classic-freeform-x-cards"]
    record["lifecycle"] = "candidate"
    record["promotion_criteria"] = (
        "B-corpus stress test + re-run reliability proof (operator-ratified 2026-07-02)"
    )
    record["authored_session"] = "2026-07-02-session-07"
    errors = validate_style_guides(patched)
    assert errors == [], errors


def test_lifecycle_absent_warns_defaulted_candidate() -> None:
    from scripts.utilities.validate_gamma_style_guides import validate_style_guides_full

    data = _runtime_data()
    stripped = copy.deepcopy(data)
    stripped["style_guides"]["classic-freeform-x-cards"].pop("lifecycle")
    errors, warnings = validate_style_guides_full(stripped)
    assert errors == [], errors
    assert any("gamma.lifecycle.defaulted-candidate" in w for w in warnings), warnings


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


# ---------------------------------------------------------------------------
# Leg-B1 — documented dependency rules (warnings channel + Rules 2/3; dedup 6/theme)
# RED-first: these assert the new warnings channel, Rule 2 (ERROR), Rule 3 (WARN),
# and the dedup membership of the studio-surface rules. Diagnostic id/string is
# asserted, not just exit code. NO network in any test.
# ---------------------------------------------------------------------------


def test_warnings_channel_shape_and_backcompat() -> None:
    # AC#1: the full API returns a (errors, warnings) tuple; the default
    # validate_style_guides is unchanged (errors-only list); strict folds warnings
    # into the failing list. Seeds are clean on BOTH channels.
    from scripts.utilities.validate_gamma_style_guides import validate_style_guides_full

    data = _runtime_data()
    result = validate_style_guides_full(data)
    assert isinstance(result, tuple) and len(result) == 2, result
    errors, warnings = result
    assert isinstance(errors, list) and isinstance(warnings, list)
    assert errors == [], errors
    assert warnings == [], warnings
    # Back-compat: default call still returns the errors list only.
    assert validate_style_guides(data) == []


def test_rule2_image_model_without_aigenerated_errors() -> None:
    # AC#2 / AC#9 teeth: image_model set + image_source != aiGenerated -> ERROR
    # (the model string is a silent no-op under non-aiGenerated sources).
    data = _runtime_data()
    broken = copy.deepcopy(data)
    visuals = broken["style_guides"]["hil-2026-apc-blueprint-classic"][
        "prompt_configuration"
    ]["visuals"]
    # blueprint already carries image_model=recraft-v3-svg; flip source off aiGenerated.
    visuals["image_source"] = "pexels"
    errors = validate_style_guides(broken)
    assert any("gamma.dep.image-model-source" in e for e in errors), errors


def test_rule2_image_model_with_aigenerated_passes() -> None:
    # AC#7 good: image_model + aiGenerated is the valid pairing (no false error).
    data = _runtime_data()
    errors = validate_style_guides(data)
    assert not any("gamma.dep.image-model-source" in e for e in errors), errors


def test_rule3_named_preset_plus_image_style_warns_not_errors() -> None:
    # AC#3 / AC#9 teeth: a named preset + a set image_style (visuals.custom_style)
    # -> WARN gamma.dep.preset-style-subordinated, NOT an error. Evaluated on the
    # RAW record. Warning does not fail the default exit; --strict folds it in.
    from scripts.utilities.validate_gamma_style_guides import validate_style_guides_full

    data = _runtime_data()
    broken = copy.deepcopy(data)
    visuals = broken["style_guides"]["classic-freeform-x-cards"][
        "prompt_configuration"
    ]["visuals"]
    # style_preset is 'illustration' (a named preset); add a conflicting image_style.
    visuals["custom_style"] = "loose watercolor washes"
    errors, warnings = validate_style_guides_full(broken)
    assert any("gamma.dep.preset-style-subordinated" in w for w in warnings), warnings
    assert not any("gamma.dep.preset-style-subordinated" in e for e in errors), errors
    # Non-strict exit is unaffected by a warning:
    assert not any(
        "gamma.dep.preset-style-subordinated" in e
        for e in validate_style_guides(broken)
    )
    # --strict folds the warning into the failing set:
    assert any(
        "gamma.dep.preset-style-subordinated" in e
        for e in validate_style_guides(broken, strict=True)
    )


def test_rule3_named_preset_alone_no_warning() -> None:
    # AC#7 good: a named preset WITHOUT an image_style -> no subordination warning.
    from scripts.utilities.validate_gamma_style_guides import validate_style_guides_full

    data = _runtime_data()  # classic seed: illustration + custom_style null
    _errors, warnings = validate_style_guides_full(data)
    assert not any(
        "gamma.dep.preset-style-subordinated" in w for w in warnings
    ), warnings


def test_rule3_custom_preset_with_style_no_subordination_warning() -> None:
    # AC#7 good: 'custom' preset + custom_style is the REQUIRED pairing (Leg-A rule),
    # never a subordination conflict -> no warning.
    from scripts.utilities.validate_gamma_style_guides import validate_style_guides_full

    data = _runtime_data()
    good = copy.deepcopy(data)
    visuals = good["style_guides"]["classic-freeform-x-cards"]["prompt_configuration"][
        "visuals"
    ]
    visuals["style_preset"] = "custom"
    visuals["custom_style"] = "loose watercolor washes"
    _errors, warnings = validate_style_guides_full(good)
    assert not any(
        "gamma.dep.preset-style-subordinated" in w for w in warnings
    ), warnings


def test_rule6_studio_dimensions_single_surface_violation_no_double_fire() -> None:
    # AC#4 dedup: dimensions on a studio record is ALREADY rejected by the
    # discriminated-union surface check; assert single-fire, no gamma.dep dup.
    data = _runtime_data()
    broken = copy.deepcopy(data)
    studio = broken["style_guides"]["hil-2026-apc-studio-image-card"]
    studio.setdefault("page_settings", {}).setdefault("card_options", {})[
        "dimensions"
    ] = "16x9"
    errors = validate_style_guides(broken)
    surface = [e for e in errors if "surface-violation" in e]
    assert len(surface) == 1, surface
    assert not any("gamma.dep" in e for e in errors), errors


def test_studio_theme_id_already_caught_by_surface_violation_no_double_fire() -> None:
    # AC#5 dedup: from-template + theme.id is ALREADY rejected by the surface union
    # ('theme' in STYLEGUIDE_CLASSIC_ONLY_KEYS). One surface-violation, no dup, and
    # no separate gamma.dep.studio-theme-conflict double-fire.
    data = _runtime_data()
    broken = copy.deepcopy(data)
    studio = broken["style_guides"]["hil-2026-apc-studio-image-card"]
    studio["theme"] = {"id": "njim9kuhfnljvaa", "name": "leaked theme"}
    errors = validate_style_guides(broken)
    surface = [e for e in errors if "surface-violation" in e and "theme" in e]
    assert len(surface) == 1, surface
    assert not any("gamma.dep.studio-theme-conflict" in e for e in errors), errors


def test_good_studio_no_theme_and_good_api_theme_pass() -> None:
    # AC#5 good: a clean studio (template, no theme) and a clean api (theme, no
    # template) both pass with zero errors (covered by the shipped seeds).
    data = _runtime_data()
    assert validate_style_guides(data) == []


def test_three_seeds_zero_errors_and_zero_warnings() -> None:
    # AC#7: the shipped seeds stay copacetic on BOTH channels after all rules land.
    from scripts.utilities.validate_gamma_style_guides import validate_style_guides_full

    errors, warnings = validate_style_guides_full(_runtime_data())
    assert errors == [], errors
    assert warnings == [], warnings


def test_default_validation_makes_no_network_call(monkeypatch) -> None:
    # AC#8 hermetic guard: the default path must not open a network socket. The load
    # (local disk) happens before the guard is armed; validation itself must be inert.
    import socket

    data = _runtime_data()

    def _boom(*_a, **_k):
        raise AssertionError("validate_style_guides opened a network socket")

    monkeypatch.setattr(socket, "socket", _boom)
    from scripts.utilities.validate_gamma_style_guides import validate_style_guides_full

    assert validate_style_guides(data) == []
    assert validate_style_guides_full(data) == ([], [])
