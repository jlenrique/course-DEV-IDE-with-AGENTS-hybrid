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
        [{"variant_id": "A", "styleguide": "classic-freeform-x-cards"}],
    )
    card_options = _call_for_variant(client, "A").get("card_options") or {}
    # The removed override would have forced 16x9 here. A fluid style must NOT.
    assert card_options.get("dimensions") != "16x9"
    assert card_options.get("dimensions") in (None, "fluid")


def test_16x9_style_emits_16x9(tmp_path: Path, monkeypatch) -> None:
    client = _run(
        tmp_path,
        monkeypatch,
        [{"variant_id": "A", "dimensions": "16x9"}],
    )
    card_options = _call_for_variant(client, "A").get("card_options") or {}
    assert card_options.get("dimensions") == "16x9"


def test_absent_dimensions_omits_card_options(tmp_path: Path, monkeypatch) -> None:
    # A variant whose resolved style names no dimensions must NOT smuggle a forced
    # 16:9 back in — cardOptions is OMITTED entirely (tightened per code-review #8).
    client = _run(
        tmp_path,
        monkeypatch,
        [{"variant_id": "A", "dimensions": "default"}],
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
        [{"variant_id": "A", "styleguide": "classic-freeform-x-cards"}],
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
                "styleguide": "classic-freeform-x-cards",
                # Source-derived keywords on the item must WIN over the styleguide's own.
                "keywords": source_keywords,
            }
        ],
    }
    gary_act.generate_gamma_variants(payload, client=client)
    call = _call_for_variant(client, "A")
    instr = str(call.get("additional_instructions") or "")

    # 1) Every source instruction line survives verbatim, unclobbered.
    for line in source_brief.split("\n"):
        assert line in instr, f"source instruction line lost: {line!r}"
    # 2) Order preserved: the source brief LEADS, before the styleguide-settings summary.
    assert instr.index(source_brief.split("\n")[0]) < instr.index(
        "Apply this variant's Gamma settings"
    )
    # 3) Every source keyword survives, in order.
    kw_field = f"keywords={', '.join(source_keywords)};"
    assert kw_field in instr, f"source keywords lost/reordered; instr={instr!r}"
    # 4) The styleguide's OWN keywords did NOT clobber or pollute the source set
    #    (classic-freeform's library keywords include 'minimalist'/'vector').
    assert "minimalist" not in instr
    assert "vector" not in instr
    # 5) The styleguide only FILLED unset defaults: theme + art-style + dimensions came
    #    from the library because the item did not set them.
    assert call["theme_id"] == "njim9kuhfnljvaa"
    assert (call.get("image_options") or {}).get("stylePreset") == "illustration"
    assert (call.get("card_options") or {}).get("dimensions") in (None, "fluid")


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
