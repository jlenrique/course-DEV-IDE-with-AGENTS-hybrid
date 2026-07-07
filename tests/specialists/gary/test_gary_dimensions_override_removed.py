"""Leg-A AC#4 — the baked-in unconditional 16:9 override at ``_act.py:789`` is GONE.

RED-first: today EVERY Classic dispatch carries ``cardOptions.dimensions == "16x9"``
regardless of the resolved style. After removal, the resolved style's ``dimensions``
alone drives ``cardOptions`` (fluid -> fluid/omit, 16x9 -> 16:9, absent -> omit).

Offline: a fake Gamma client captures ``generate_deck`` kwargs; no network.
The live two-style differential (AC#5) is the SKIPPED skeleton at the bottom.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from app.specialists.gary import _act as gary_act

from ._s4_seed import install_seed_resolver, seed_name


def _titled_zip(tmp_path: Path, stems: list[str]) -> Path:
    zpath = tmp_path / "gamma-export.zip"
    with zipfile.ZipFile(zpath, "w") as archive:
        for stem in stems:
            archive.writestr(f"{stem}.png", f"bytes::{stem}".encode())
    return zpath


class _CapturingClient:
    def __init__(self) -> None:
        self.generate_calls: list[dict[str, object]] = []

    def list_themes(self, limit: int = 20) -> list[dict[str, str]]:
        return [
            {"id": "njim9kuhfnljvaa", "name": "2026 HIL APC Tejal"},
            {"id": "e8tz1vxb9v1urqp", "name": "Blueprint Editorial"},
        ]

    def generate_deck(self, input_text: str, **kwargs: object) -> dict[str, object]:
        self.generate_calls.append({"input_text": input_text, **kwargs})
        return {
            "generation_id": f"gen-{len(self.generate_calls)}",
            "exportUrl": "https://example.invalid/export.zip",
        }


def _call_for_variant(client: _CapturingClient, variant: str) -> dict[str, object]:
    marker = f"Variant {variant}."
    for call in client.generate_calls:
        if marker in str(call.get("additional_instructions") or ""):
            return call
    raise AssertionError(f"no generate_deck call found for variant {variant}")


def _run(tmp_path: Path, monkeypatch, gamma_settings: list[dict[str, object]]) -> _CapturingClient:
    zpath = _titled_zip(tmp_path, ["1_Only-Slide"])
    monkeypatch.setattr(
        gary_act, "download_export", lambda url, *, output_dir, filename: str(zpath)
    )
    client = _CapturingClient()
    payload = {
        "slides": [{"slide_id": "s1", "title": "Only Slide"}],
        "export_dir": str(tmp_path),
        "gamma_settings": gamma_settings,
    }
    gary_act.generate_gamma_variants(payload, client=client)
    return client


def test_fluid_style_emits_no_forced_16x9(tmp_path: Path, monkeypatch) -> None:
    client = _run(
        tmp_path,
        monkeypatch,
        [{"variant_id": "A", "styleguide": "hil-2026-apc-crossroads-classic"}],
    )
    card_options = _call_for_variant(client, "A").get("card_options") or {}
    # The removed override would have forced 16x9 here. A fluid style must NOT.
    assert card_options.get("dimensions") != "16x9"
    assert card_options.get("dimensions") in (None, "fluid")


def test_16x9_style_emits_16x9(tmp_path: Path, monkeypatch) -> None:
    # S4: a NAMED variant must be styleguide-bound; the byte-identical seed
    # supplies the base while the per-variant dimensions override is under test.
    install_seed_resolver(monkeypatch)
    client = _run(
        tmp_path,
        monkeypatch,
        [{"variant_id": "A", "styleguide": seed_name("A"), "dimensions": "16x9"}],
    )
    card_options = _call_for_variant(client, "A").get("card_options") or {}
    assert card_options.get("dimensions") == "16x9"


def test_absent_dimensions_omits_card_options(tmp_path: Path, monkeypatch) -> None:
    # A variant whose resolved style names no dimensions must NOT smuggle a forced
    # 16:9 back in — cardOptions is OMITTED entirely (tightened per code-review #8).
    install_seed_resolver(monkeypatch)
    client = _run(
        tmp_path,
        monkeypatch,
        [{"variant_id": "A", "styleguide": seed_name("A"), "dimensions": "default"}],
    )
    call = _call_for_variant(client, "A")
    assert "card_options" not in call, (
        f"cardOptions must be omitted; got {call.get('card_options')!r}"
    )


def test_bound_styleguide_omits_template_none_clause(tmp_path: Path, monkeypatch) -> None:
    # Item #9: a bound styleguide has no `template` key, so the settings summary must
    # NOT render a literal `template=None.` into additionalInstructions.
    client = _run(
        tmp_path,
        monkeypatch,
        [{"variant_id": "A", "styleguide": "hil-2026-apc-crossroads-classic"}],
    )
    instr = str(_call_for_variant(client, "A").get("additional_instructions") or "")
    assert "template=None" not in instr, f"leaked template=None clause; instr={instr!r}"


def test_styleguide_preserves_source_detail(tmp_path: Path, monkeypatch) -> None:
    """PROTECTED INVARIANT (operator, in-flight): a styleguide is a BASE-LAYER DEFAULT
    PROVIDER ONLY. Source-derived detail — the multi-line design brief
    (payload additional_instructions) + per-variant source keywords — must compose ON
    TOP of the styleguide base and WIN on conflict; the styleguide may only fill UNSET
    keys (theme / art-style / dimensions / ...). Any loss, reorder, truncation, or
    clobber of source detail is a HARD failure.
    """
    source_brief = (
        "Composition: one centered hero diagram with three supporting callouts.\n"
        "Color palette: deep navy #0B1F3A, warm gold #C8A24B, off-white background.\n"
        "Required text labels: 'Systole', 'Diastole', 'Mean Arterial Pressure'."
    )
    source_keywords = ["hero-diagram", "annotated-callouts", "clinical-navy-gold"]
    zpath = _titled_zip(tmp_path, ["1_Only-Slide"])
    monkeypatch.setattr(
        gary_act, "download_export", lambda url, *, output_dir, filename: str(zpath)
    )
    client = _CapturingClient()
    payload = {
        "slides": [{"slide_id": "s1", "title": "Only Slide"}],
        "export_dir": str(tmp_path),
        # Source-derived design brief lives at payload level (the styleguide resolver
        # must never touch it).
        "additional_instructions": source_brief,
        "gamma_settings": [
            {
                "variant_id": "A",
                "styleguide": "hil-2026-apc-crossroads-classic",
                # Source-derived keywords on the item must WIN over the styleguide's own.
                "keywords": source_keywords,
            }
        ],
    }
    gary_act.generate_gamma_variants(payload, client=client)
    call = _call_for_variant(client, "A")
    instr = str(call.get("additional_instructions") or "")

    # 1) AC#4 — the source brief survives BYTE-IDENTICAL (one contiguous verbatim
    #    substring, upgraded from line-by-line "present" to character-equal).
    assert source_brief in instr, f"source brief not byte-identical; instr={instr!r}"
    for line in source_brief.split("\n"):
        assert line in instr, f"source instruction line lost: {line!r}"
    # 2) AC#1 — the merely-redundant settings-dump is GONE (channel cleanup): no
    #    summary sentence, no key=value echoes of the structured params.
    assert "Apply this variant's Gamma settings" not in instr
    for token in ("image_style_preset=", "amount=", "tone=", "template=", "image_style="):
        assert token not in instr, f"leaked settings token {token!r}; instr={instr!r}"
    # 3) AC#3 — source keywords survive as natural imagery GUIDANCE (values verbatim,
    #    NO `keywords=` machine-field), and the source brief LEADS (source wins).
    assert "keywords=" not in instr
    guidance = f"Emphasize this imagery: {', '.join(source_keywords)}."
    assert guidance in instr, f"keyword guidance prose missing; instr={instr!r}"
    for kw in source_keywords:
        assert kw in instr, f"source keyword lost: {kw!r}; instr={instr!r}"
    assert instr.index(source_brief) < instr.index(guidance)
    # 4) The styleguide's OWN keywords did NOT clobber or pollute the source set
    #    (crossroads carries an EMPTY library keyword list, so the source set must
    #    stand alone; 'minimalist'/'vector' would be classic-family pollution).
    assert "minimalist" not in instr
    assert "vector" not in instr
    # 5) The styleguide only FILLED unset defaults: theme + art-style + dimensions came
    #    from the library because the item did not set them.
    assert call["theme_id"] == "njim9kuhfnljvaa"
    assert (call.get("image_options") or {}).get("stylePreset") == "illustration"
    assert (call.get("card_options") or {}).get("dimensions") in (None, "fluid")


# =========================================================================== #
# gamma-instructions-channel-cleanup — de-redundant the additionalInstructions
# channel. The structured style settings (image_style_preset/amount/tone) travel
# via imageOptions/textOptions ONLY; keywords stay in prose as natural imagery
# guidance. RED-first: AC#1/AC#2 are demonstrated RED on current code pre-fix.
# =========================================================================== #

# `image_style` is intentionally None here — the old code rendered the literal
# `image_style=None` bug (AC#2). `template` is vestigial ("default").
_SETTINGS_FULL: dict[str, object] = {
    "variant_id": "A",
    "image_style_preset": "illustration",
    "image_style": None,
    "amount": "brief",
    "tone": "Clear, professional",
    "template": "default",
    "keywords": ["hero-diagram", "clinical-navy-gold"],
}


def _emit(payload_instr: str, settings: dict[str, object] | None) -> str:
    return gary_act._instructions_for_variant(
        {"additional_instructions": payload_instr}, variant="A", settings=settings
    )


def test_ac1_settings_dump_absent() -> None:
    # AC#1 [RED on current code] — no summary sentence, no key=value echoes of
    # params already forwarded structurally via imageOptions/textOptions.
    instr = _emit("Source brief.", _SETTINGS_FULL)
    assert "Apply this variant's Gamma settings" not in instr
    for token in ("image_style_preset=", "amount=", "tone=", "template=", "image_style="):
        assert token not in instr, f"leaked settings token {token!r}: {instr!r}"


def test_ac2_no_literal_none() -> None:
    # AC#2 [RED on current code] — the `image_style=None` literal bug is gone for
    # every settings/keywords combination (kill by construction).
    for settings in (
        _SETTINGS_FULL,
        {**_SETTINGS_FULL, "keywords": []},
        {"variant_id": "A"},  # bare settings: every style key absent
    ):
        instr = _emit("Source brief.", settings)
        assert "None" not in instr, f"literal None leaked: {instr!r}"
        assert "image_style=None" not in instr


def test_ac3_keywords_as_guidance_and_empty_guard() -> None:
    # AC#3 — keywords de-tokenized to natural imagery guidance; empty-guard holds.
    instr = _emit("Source brief.", _SETTINGS_FULL)
    assert "keywords=" not in instr
    assert "Emphasize this imagery: hero-diagram, clinical-navy-gold." in instr
    empty = _emit("Source brief.", {**_SETTINGS_FULL, "keywords": []})
    assert "Emphasize this imagery" not in empty
    assert "  " not in empty, f"dangling separator on empty keywords: {empty!r}"


def test_ac4_source_verbatim_precedes_guidance() -> None:
    # AC#4 [protected invariant] — source brief byte-identical AND leading (wins).
    brief = "Composition: centered hero.\nPalette: navy #0B1F3A."
    instr = _emit(brief, _SETTINGS_FULL)
    assert brief in instr, f"source brief not byte-identical: {instr!r}"
    guidance = "Emphasize this imagery: hero-diagram, clinical-navy-gold."
    assert instr.index(brief) < instr.index(guidance)


def test_ac5_structured_options_still_carry_settings() -> None:
    # AC#5 [co-regression tripwire] — the params removed from PROSE must still
    # travel STRUCTURALLY via imageOptions.stylePreset + textOptions.amount/tone.
    settings = {
        "variant_id": "A",
        "image_style_preset": "illustration",
        "amount": "brief",
        "tone": "Clear, professional",
    }
    image_opts = gary_act._image_options_for_variant(settings)
    text_opts = gary_act._text_options_for_variant(settings)
    assert image_opts.get("stylePreset") == "illustration"
    assert text_opts.get("amount") == "brief"
    assert text_opts.get("tone") == "Clear, professional"


def test_prompt_editor_amount_aliases_translate_to_api_values() -> None:
    assert gary_act._text_options_for_variant({"amount": "minimal"})["amount"] == "brief"
    assert gary_act._text_options_for_variant({"amount": "concise"})["amount"] == "medium"


def test_ac7_wellformed_no_dangling_separators() -> None:
    # AC#7 — no double-space / dangling separator across empty-settings,
    # empty-keywords, empty-brief, and full cases; label always terminal.
    for payload_instr, settings in (
        ("Source brief.", None),
        ("Source brief.", {"variant_id": "A"}),
        ("Source brief.", _SETTINGS_FULL),
        ("", _SETTINGS_FULL),
    ):
        instr = _emit(payload_instr, settings)
        assert "  " not in instr, f"double-space: {instr!r}"
        assert not instr.startswith(" "), f"leading space: {instr!r}"
        assert instr.endswith("Variant A."), f"label not terminal: {instr!r}"
        assert "None" not in instr, f"literal None: {instr!r}"


# --- AC#5 live differential proof — SKELETON ONLY (gated on corpus + operator) ---

@pytest.mark.skip(reason="live Gamma proof — Leg-A AC#5, gated on corpus + operator")
def test_live_two_style_differential_to_storyboard_b() -> None:  # pragma: no cover
    """Two seed styles (>=1 Classic + >=1 Studio) over the same small proof corpus
    render machine-detectably different Gamma artifacts, real Gamma API, terminating
    at Storyboard B (no Descript assembly). First-run-stands. Requires a live
    GAMMA_API_KEY, the operator-confirmed Part-3 proof slugs, and a live
    template-existence check for g_nv5q4da69qiiu8q before the Studio render.
    """
    raise NotImplementedError("live proof executed under operator gate, not in CI")
