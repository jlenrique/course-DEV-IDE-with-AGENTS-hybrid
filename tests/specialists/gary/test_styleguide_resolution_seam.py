"""Leg-A AC#3 — Gary resolves ``styleguide:<name>`` to base-layer API keys ONLY.

RED-first: the resolver + the ``styleguide`` seam in ``_normalized_gamma_settings``
do not exist yet. These pin metadata-stripping (a metadata key must NEVER reach a
``gamma_settings[]`` item, else the :375 unknown-key gate would trip), the
unknown-name fail-loud, and the base-layer/override precedence.
"""

from __future__ import annotations

import pytest

from app.specialists.gary._act import (
    GAMMA_SETTING_KEYS,
    GaryActError,
    _normalized_gamma_settings,
)
from app.specialists.gary.styleguide_library import (
    StyleguideError,
    resolve_styleguide,
)


def _settings(**b: object) -> dict[str, object]:
    return {"gamma_settings": [{"variant_id": "A", **b}]}


def test_styleguide_only_in_setting_keys_not_metadata() -> None:
    # The ONLY key added to the frozen set is ``styleguide`` — metadata keys are
    # never whitelisted (that is what keeps the :375 gate meaningful).
    assert "styleguide" in GAMMA_SETTING_KEYS
    for leaked in ("display_name", "presentation", "narrative", "scripted", "provenance"):
        assert leaked not in GAMMA_SETTING_KEYS


def test_classic_styleguide_expands_to_api_keys() -> None:
    out = _normalized_gamma_settings(_settings(styleguide="classic-freeform-x-cards"))
    a = next(item for item in out if item["variant_id"] == "A")
    # Base-layer seed came from the library.
    assert a["theme"] == "njim9kuhfnljvaa"
    assert a["dimensions"] == "fluid"
    assert a["image_style_preset"] == "illustration"
    assert a["amount"] == "brief"  # registry UI `minimal` -> Gamma API `brief`
    assert a["text_mode"] == "condense"
    assert a["production_mode"] == "api"


def test_concise_styleguide_amount_expands_to_api_medium() -> None:
    out = _normalized_gamma_settings(_settings(styleguide="videographic-glance-track"))
    a = next(item for item in out if item["variant_id"] == "A")
    assert a["amount"] == "medium"


def test_resolved_item_carries_only_setting_keys_metadata_stripped() -> None:
    out = _normalized_gamma_settings(_settings(styleguide="classic-freeform-x-cards"))
    a = next(item for item in out if item["variant_id"] == "A")
    # No metadata / presentation / scripted / styleguide-name key survived into the
    # per-variant settings dict; every key is a recognized Gamma setting key.
    leaked = set(a) - GAMMA_SETTING_KEYS
    assert leaked == set(), f"metadata leaked into gamma_settings item: {sorted(leaked)}"
    assert "styleguide" not in a  # the name itself is consumed, not passed on


def test_per_variant_override_beats_styleguide_base() -> None:
    out = _normalized_gamma_settings(
        _settings(styleguide="classic-freeform-x-cards", dimensions="16x9")
    )
    a = next(item for item in out if item["variant_id"] == "A")
    # Explicit per-variant value wins over the styleguide's base-layer seed.
    assert a["dimensions"] == "16x9"


def test_source_keywords_win_over_styleguide_base() -> None:
    # PROTECTED INVARIANT (merge level): source-derived keywords on the item WIN over
    # the styleguide's base keywords (never clobbered/reordered), while the styleguide
    # still fills UNSET keys (theme/dimensions/image_style_preset).
    source_keywords = ["hero-diagram", "annotated-callouts", "clinical-navy-gold"]
    out = _normalized_gamma_settings(
        _settings(styleguide="classic-freeform-x-cards", keywords=source_keywords)
    )
    a = next(item for item in out if item["variant_id"] == "A")
    assert a["keywords"] == source_keywords  # exact set + order, no styleguide pollution
    # Styleguide filled the keys the item left unset.
    assert a["theme"] == "njim9kuhfnljvaa"
    assert a["dimensions"] == "fluid"
    assert a["image_style_preset"] == "illustration"


def test_unknown_styleguide_fails_loud() -> None:
    with pytest.raises(GaryActError) as exc:
        _normalized_gamma_settings(_settings(styleguide="no-such-guide"))
    assert exc.value.tag == "gamma.styleguide.unknown"


def test_studio_styleguide_resolves_to_studio_surface() -> None:
    out = _normalized_gamma_settings(
        {"gamma_settings": [{"variant_id": "B", "styleguide": "hil-2026-apc-studio-image-card"}]}
    )
    b = next(item for item in out if item["variant_id"] == "B")
    assert b["production_mode"] == "studio"
    assert b["studio_template_id"] == "g_nv5q4da69qiiu8q"
    # A studio guide must NOT resolve to Classic-only keys — the key is ABSENT
    # (not merely falsy). Tightened per code-review item #8.
    for classic_only in ("text_mode", "dimensions", "amount", "tone", "keywords"):
        assert classic_only not in b, f"studio surface leaked Classic-only key {classic_only!r}"


def test_null_theme_api_styleguide_is_incomplete() -> None:
    # Item #1: an api record with an absent/null theme.id must FAIL LOUD
    # (resolver completeness), never silently yield a themeless base that
    # `_theme_id` then fills with an arbitrary themes[0].id (wrong paid deck).
    guides = {
        "themeless-api": {
            "production_mode": "api",
            "theme": None,
            "prompt_configuration": {
                "text_content": {"mode": "condense"},
                "visuals": {"image_source": "aiGenerated"},
            },
            "page_settings": {"card_options": {"dimensions": "fluid"}},
        }
    }
    with pytest.raises(StyleguideError) as exc:
        resolve_styleguide("themeless-api", guides=guides)
    assert exc.value.tag == "gamma.styleguide.incomplete"


def test_studio_bound_variant_with_classic_override_is_surface_violation() -> None:
    # Item #3(b): per-variant Classic overrides on a studio-bound variant must
    # FAIL LOUD instead of being silently dropped.
    with pytest.raises(GaryActError) as exc:
        _normalized_gamma_settings(
            {
                "gamma_settings": [
                    {
                        "variant_id": "B",
                        "styleguide": "hil-2026-apc-studio-image-card",
                        "text_mode": "preserve",
                        "dimensions": "16x9",
                    }
                ]
            }
        )
    assert exc.value.tag == "gamma.styleguide.surface-violation"


def test_empty_keywords_list_does_not_clobber_styleguide() -> None:
    # Item #7: an empty/blank-only keyword LIST means "unset" (symmetry with the
    # empty-string skip) — it must NOT clobber the styleguide's curated keywords.
    out = _normalized_gamma_settings(_settings(styleguide="classic-freeform-x-cards", keywords=[]))
    a = next(item for item in out if item["variant_id"] == "A")
    assert a["keywords"] == ["vector", "minimalist", "flat-color", "linework", "bold"]


def test_blank_styleguide_name_fails_loud() -> None:
    # Item #10: a present-but-blank styleguide value must fail loud (a present key
    # must name a real guide), not silently revert to the DEFAULT_VARIANT_PAIR fixture.
    for blank in ("", "   "):
        with pytest.raises(GaryActError) as exc:
            _normalized_gamma_settings(_settings(styleguide=blank))
        assert exc.value.tag == "gamma.styleguide.unknown"


def test_resolved_api_keys_subset_of_gamma_setting_keys() -> None:
    # Item #4: make the promised drift-guard real. RESOLVED_API_KEYS must be a
    # strict subset of Gary's GAMMA_SETTING_KEYS or a resolved key would trip the
    # :375 unknown-key gate at dispatch.
    from app.specialists.gary.styleguide_library import RESOLVED_API_KEYS

    assert set() == RESOLVED_API_KEYS - GAMMA_SETTING_KEYS
