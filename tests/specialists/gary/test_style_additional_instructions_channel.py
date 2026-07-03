"""Style-level ``additional_instructions`` channel — resolver + composition.

RED-first (green-light party 2026-07-02): a style may carry a persistent
deck-level prose register (``prompt_configuration.additional_instructions``,
optional list of strings) that COMPLEMENTS, never OVERWRITES, the per-deck
source-derived instructions and Gary's hardcoded card rule. These pin:
- the resolver emits the cleaned list (empty ⇒ absent), studio never emits it;
- the two frozensets stay in lockstep;
- composition is a SEPARATE part, style-first then per-deck source-derived;
- absent/empty ⇒ byte-identical additionalInstructions (additive-safe);
- each part is independently carried (no collision / no silent overwrite).
"""

from __future__ import annotations

import pytest

from app.specialists.gary import _act as gary_act
from app.specialists.gary._act import (
    GAMMA_SETTING_KEYS,
    _instructions_for_variant,
    _normalized_gamma_settings,
)
from app.specialists.gary.styleguide_library import (
    RESOLVED_API_KEYS,
    resolve_styleguide,
)


def _api_guide(**pc_extra: object) -> dict:
    pc: dict = {
        "text_content": {"mode": "condense"},
        "visuals": {"image_source": "aiGenerated", "style_preset": "illustration"},
    }
    pc.update(pc_extra)
    return {
        "production_mode": "api",
        "theme": {"id": "njim9kuhfnljvaa"},
        "prompt_configuration": pc,
        "page_settings": {"card_options": {"dimensions": "fluid"}},
    }


# --- AC-2 resolver -----------------------------------------------------------
def test_resolver_emits_additional_instructions_list() -> None:
    r = resolve_styleguide("g", guides={"g": _api_guide(additional_instructions=["one.", "two."])})
    assert r["additional_instructions"] == ["one.", "two."]


def test_resolver_absent_additional_instructions_key_absent() -> None:
    r = resolve_styleguide("g", guides={"g": _api_guide()})
    assert "additional_instructions" not in r


@pytest.mark.parametrize("empty", [[], ["", "   "]])
def test_resolver_empty_or_blank_list_is_absent(empty: list) -> None:
    r = resolve_styleguide("g", guides={"g": _api_guide(additional_instructions=empty)})
    assert "additional_instructions" not in r


def test_resolved_key_in_both_frozensets_and_subset_holds() -> None:
    assert "additional_instructions" in RESOLVED_API_KEYS
    assert "additional_instructions" in GAMMA_SETTING_KEYS
    assert set() == RESOLVED_API_KEYS - GAMMA_SETTING_KEYS


def test_studio_resolver_never_emits_additional_instructions() -> None:
    # A studio record carrying additional_instructions is NOT a surface violation
    # and the resolver does not emit it (studio template-lock list stays documented).
    guides = {
        "s": {
            "production_mode": "studio",
            "studio_template": {"gamma_id": "g_x"},
            "prompt_configuration": {"additional_instructions": ["Preserve template."]},
        }
    }
    r = resolve_styleguide("s", guides=guides)
    assert r == {"production_mode": "studio", "studio_template_id": "g_x"}


def _synthetic_api_base() -> dict:
    return {
        "production_mode": "api",
        "theme": "njim9kuhfnljvaa",
        "text_mode": "condense",
        "image_source": "aiGenerated",
        "dimensions": "fluid",
        "additional_instructions": ["STYLE_REGISTER."],
    }


def test_normalized_settings_carries_style_block(monkeypatch) -> None:
    monkeypatch.setattr(gary_act, "resolve_styleguide", lambda name: _synthetic_api_base())
    out = _normalized_gamma_settings(
        {"gamma_settings": [{"variant_id": "A", "styleguide": "synthetic-guide"}]}
    )
    a = next(item for item in out if item["variant_id"] == "A")
    # The resolved base-layer style register flows into the per-variant settings.
    assert a["additional_instructions"] == ["STYLE_REGISTER."]


def test_per_variant_additional_instructions_fails_loud(monkeypatch) -> None:
    # additional_instructions is a STYLE-ONLY channel — authoring it inside a
    # gamma_settings[] item must FAIL LOUD (consistent with the module's fail-loud
    # discipline), never be silently dropped (code-review B, both hunter lanes).
    from app.specialists.gary._act import GaryActError

    monkeypatch.setattr(gary_act, "resolve_styleguide", lambda name: _synthetic_api_base())
    with pytest.raises(GaryActError) as exc:
        _normalized_gamma_settings(
            {
                "gamma_settings": [
                    {
                        "variant_id": "A",
                        "styleguide": "synthetic-guide",
                        "additional_instructions": ["SHOULD_FAIL_LOUD."],
                    }
                ]
            }
        )
    assert exc.value.tag == "gamma.settings.invalid"


# --- AC-3 / AC-4 composition -------------------------------------------------
_PAYLOAD = "ZZ_PAYLOAD_SOURCE_ZZ"
_STYLE = "ZZ_STYLE_REGISTER_ZZ"
_KW = "ZZ_KEYWORD_ZZ"


def _compose(*, style: object = None, payload: str = _PAYLOAD, keywords: object = (_KW,)) -> str:
    settings: dict = {}
    if style is not None:
        settings["additional_instructions"] = style
    if keywords is not None:
        settings["keywords"] = list(keywords)
    return _instructions_for_variant(
        {"additional_instructions": payload}, variant="A", settings=settings
    )


def test_all_parts_survive_and_order_is_style_first() -> None:
    out = _compose(style=[_STYLE])
    # AC-4: every part co-exists simultaneously.
    for token in (_STYLE, _PAYLOAD, "verbatim", "do not merge or split",
                  f"Emphasize this imagery: {_KW}.", "Variant A."):
        assert token in out, f"missing part: {token!r} in {out!r}"
    # AC-3: ordering — style block FIRST, then per-deck source-derived, then card
    # rule, then keywords imagery, then the variant tail.
    assert (
        out.index(_STYLE)
        < out.index(_PAYLOAD)
        < out.index("verbatim")
        < out.index(f"Emphasize this imagery: {_KW}.")
        < out.index("Variant A.")
    )


def test_multi_item_style_list_joins_into_one_part() -> None:
    out = _compose(style=["FIRST_DIRECTIVE.", "SECOND_DIRECTIVE."])
    assert "FIRST_DIRECTIVE." in out and "SECOND_DIRECTIVE." in out
    # Both land before the per-deck payload (single style-register part, style-first).
    assert out.index("SECOND_DIRECTIVE.") < out.index(_PAYLOAD)


@pytest.mark.parametrize("drop", ["style", "payload", "keywords"])
def test_each_part_is_independently_carried(drop: str) -> None:
    # Teeth for the no-overwrite guarantee: removing one input removes EXACTLY its
    # token and leaves the others intact — no part subsumes/collides with another.
    style: object = [_STYLE]
    payload = _PAYLOAD
    keywords: object = (_KW,)
    if drop == "style":
        style = None
    elif drop == "payload":
        payload = ""
    elif drop == "keywords":
        keywords = None
    out = _compose(style=style, payload=payload, keywords=keywords)
    dropped_token = {"style": _STYLE, "payload": _PAYLOAD, "keywords": _KW}[drop]
    assert dropped_token not in out
    for name, token in {"style": _STYLE, "payload": _PAYLOAD, "keywords": _KW}.items():
        if name != drop:
            assert token in out
    assert "verbatim" in out and out.rstrip().endswith("Variant A.")


# --- AC-6 additive-safe byte-identity ---------------------------------------
@pytest.mark.parametrize("empty", [None, [], ["", "   "]])
def test_byte_identical_when_style_absent_or_empty(empty: object) -> None:
    base = _compose(style=None)  # today's string (no style register)
    out = _compose(style=empty)
    assert out == base


def test_settings_none_unchanged_from_today() -> None:
    # No styleguide bound at all — the classic path — must be byte-identical too.
    out = _instructions_for_variant(
        {"additional_instructions": _PAYLOAD}, variant="A", settings=None
    )
    assert out.startswith(_PAYLOAD)
    assert out.rstrip().endswith("Variant A.")
    assert _STYLE not in out
