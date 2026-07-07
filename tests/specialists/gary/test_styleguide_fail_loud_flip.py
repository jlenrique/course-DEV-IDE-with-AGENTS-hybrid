"""Canonical-arc S4 — Flip A: styleguide-less WARN-seed -> pre-spend hard failure.

Spec: `_bmad-output/implementation-artifacts/canonical-arc-s4-fail-loud-flip.md`
(D1; RED-first plan #1). Covers AC-1 (named-variant-styleguide-less raises
`gamma.styleguide.unbound`, zero generative dispatch, names the variant, +
companion negative for empty gamma_settings), AC-2 (F-705 byte-diff witness:
old honesty-WARN absent, tag fires, DEFAULT_VARIANT_PAIR intact), AC-3
(success-path byte-identity to pre-flip `7630d091`), AC-7 (no clock coupling).

The comparator (`app/styleguide/parity.py`) is FROZEN; S4 changes only the
CALLER's action. Flip A lives in the styleguide-less ``else`` branch of the
per-variant seed loop in ``_normalized_gamma_settings`` — a raise BEFORE any
paid Gamma call (``list_themes`` metadata read is permitted, F-1104).
"""

from __future__ import annotations

import inspect
import json
import logging
import zipfile
from pathlib import Path
from typing import Any

import pytest

from app.specialists.cd.graph import _styleguide_resolution_from_projection
from app.specialists.gary import _act as gary_act

GARY_LOGGER = "app.specialists.gary._act"
REAL_GUIDE = "hil-2026-apc-crossroads-classic"
SAME_DIGEST = "f" * 64

# AC-3 pre-flip golden (captured from HEAD `13792617` on the ok/match success
# path, identical inputs). Byte-identity pin: neither flip may move a
# styling/keyword/prompt byte on the non-raising path (protected invariant —
# source-detail->Gamma conveyance + VO<->on-screen alignment).
_GOLDEN_CALLS_CANON = (
    '[{"additional_instructions": "Use each section\'s leading heading as that '
    "card's title verbatim; produce exactly one card per section; do not add a "
    "cover, agenda, divider, or summary card; do not merge or split sections. "
    'Emphasize this imagery: hero-diagram, clinical-navy-gold. Variant A.", '
    '"card_options": {"dimensions": "fluid"}, "card_split": "inputTextBreaks", '
    '"export_as": "png", "image_options": {"model": "gpt-image-2-mini", '
    '"source": "aiGenerated", "stylePreset": "illustration"}, "input_text": '
    '"# Only Slide", "num_cards": 1, "text_mode": "condense", "text_options": '
    '{"amount": "brief", "language": "en"}, "theme_id": "njim9kuhfnljvaa"}]'
)
_GOLDEN_VGS_CANON = (
    '[{"amount": "brief", "dimensions": "fluid", "image_model": '
    '"gpt-image-2-mini", "image_source": "aiGenerated", "image_style_preset": '
    '"illustration", "keywords": ["hero-diagram", "clinical-navy-gold"], '
    '"language": "en", "production_mode": "api", "text_mode": "condense", '
    '"theme": "njim9kuhfnljvaa", "variant_id": "A"}]'
)


class _CapturingClient:
    """Offline Gamma client: captures generate_deck kwargs; no network. Any
    create-from-template / studio call would surface as an AttributeError, so a
    generative dispatch on a fail-loud path fails the test loudly."""

    def __init__(self) -> None:
        self.generate_calls: list[dict[str, object]] = []

    def list_themes(self, limit: int = 20) -> list[dict[str, str]]:
        del limit
        return [
            {"id": "njim9kuhfnljvaa", "name": "2026 HIL APC Tejal"},
            {"id": "t-parity", "name": "Parity Theme"},
        ]

    def generate_deck(self, input_text: str, **kwargs: object) -> dict[str, object]:
        self.generate_calls.append({"input_text": input_text, **kwargs})
        return {
            "generation_id": f"gen-{len(self.generate_calls)}",
            "exportUrl": "https://example.invalid/export.zip",
        }


def _titled_zip(tmp_path: Path) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    zpath = tmp_path / "gamma-export.zip"
    with zipfile.ZipFile(zpath, "w") as archive:
        archive.writestr("1_Only-Slide.png", b"bytes::only-slide")
    return zpath


def _run(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    payload_extra: dict[str, Any],
    *,
    gamma_settings: list[dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], _CapturingClient]:
    zpath = _titled_zip(tmp_path)
    monkeypatch.setattr(
        gary_act, "download_export", lambda url, *, output_dir, filename: str(zpath)
    )
    client = _CapturingClient()
    payload: dict[str, Any] = {
        "slides": [{"slide_id": "s1", "title": "Only Slide"}],
        "export_dir": str(tmp_path / "exports"),
        **payload_extra,
    }
    if gamma_settings is not None:
        payload["gamma_settings"] = gamma_settings
    result = gary_act.generate_gamma_variants(payload, client=client)
    return result, client


def _real_ssot_cd_block(picks: list[dict[str, Any]] | None) -> dict[str, Any]:
    return _styleguide_resolution_from_projection(
        {"gamma_settings": picks, "directive_digest": SAME_DIGEST}
    )


# --- AC-1: named-variant-styleguide-less raises pre-spend (F-1101) --------------


def test_ac1_named_variant_no_styleguide_raises_unbound_pre_spend(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    client_holder: list[_CapturingClient] = []
    zpath = _titled_zip(tmp_path)
    monkeypatch.setattr(
        gary_act, "download_export", lambda url, *, output_dir, filename: str(zpath)
    )
    client = _CapturingClient()
    client_holder.append(client)
    payload = {
        "slides": [{"slide_id": "s1", "title": "Only Slide"}],
        "export_dir": str(tmp_path / "exports"),
        # variant B is PRESENT but carries NO styleguide key -> Flip A fires.
        "gamma_settings": [{"variant_id": "B"}],
    }
    with pytest.raises(gary_act.GaryActError) as excinfo:
        gary_act.generate_gamma_variants(payload, client=client)
    assert excinfo.value.tag == "gamma.styleguide.unbound"
    # Names the offending variant.
    assert "B" in str(excinfo.value)
    # Pre-spend: zero generative dispatch (list_themes metadata read is
    # permitted per F-1104 and does NOT count as spend).
    assert client.generate_calls == [], "a fail-loud path must not dispatch Gamma"


def test_ac1_companion_negative_empty_gamma_settings_does_not_raise_unbound(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Empty/absent gamma_settings falls back to default-A (variant_settings=None,
    # styleguide-less, NO raise) — deliberately OUT of S4 scope (closed later by
    # the deferred trial-start pre-check). The both-pickless run classifies
    # ok/status-keyed-no-picks and dispatches.
    result, client = _run(
        tmp_path,
        monkeypatch,
        {"cd_styleguide_resolution": _real_ssot_cd_block(None)},
        gamma_settings=None,
    )
    assert client.generate_calls, "default-A path must still dispatch"
    assert result["styleguide_parity"]["outcome"] == "ok"
    assert result["styleguide_parity"]["reason"] == "status-keyed-no-picks"


# --- R3: mixed variants — one bound, one styleguide-less -> raises on the naked one


def test_r3_mixed_variants_unbound_second_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # R3 (coverage): variant A carries a real styleguide binding; variant B is
    # PRESENT with NO styleguide key. Flip A fires on B (the per-item else
    # branch), naming B, with zero generative dispatch. A binding on a sibling
    # variant does not license a naked one.
    zpath = _titled_zip(tmp_path)
    monkeypatch.setattr(
        gary_act, "download_export", lambda url, *, output_dir, filename: str(zpath)
    )
    client = _CapturingClient()
    payload = {
        "slides": [{"slide_id": "s1", "title": "Only Slide"}],
        "export_dir": str(tmp_path / "exports"),
        "gamma_settings": [
            {"variant_id": "A", "styleguide": REAL_GUIDE},
            {"variant_id": "B"},  # present, styleguide-less -> Flip A on B
        ],
    }
    with pytest.raises(gary_act.GaryActError) as excinfo:
        gary_act.generate_gamma_variants(payload, client=client)
    assert excinfo.value.tag == "gamma.styleguide.unbound"
    assert "B" in str(excinfo.value), "the raise must name the offending variant B"
    assert client.generate_calls == [], "a fail-loud path must not dispatch Gamma"


# --- R4: empty-LIST gamma_settings -> default-A, NO unbound raise (None companion)


def test_r4_empty_list_gamma_settings_defaults_a_no_unbound_raise(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # R4 (coverage): an EMPTY LIST is distinct from absent/None but shares the
    # fallback — it names zero variants, so the per-item else branch never runs,
    # default-A dispatches styleguide-less, and NO gamma.styleguide.unbound
    # raises (mirrors the None companion-negative; the empty/declined-pick leg
    # is deliberately out of S4 scope).
    result, client = _run(
        tmp_path,
        monkeypatch,
        {"cd_styleguide_resolution": _real_ssot_cd_block(None)},
        gamma_settings=[],
    )
    assert client.generate_calls, "empty-list gamma_settings must still dispatch default-A"
    assert result["styleguide_parity"]["outcome"] == "ok"
    assert result["styleguide_parity"]["reason"] == "status-keyed-no-picks"


# --- AC-2: F-705 byte-diff witness ----------------------------------------------


def test_ac2_honesty_warn_no_longer_fires_and_tag_fires(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    zpath = _titled_zip(tmp_path)
    monkeypatch.setattr(
        gary_act, "download_export", lambda url, *, output_dir, filename: str(zpath)
    )
    client = _CapturingClient()
    payload = {
        "slides": [{"slide_id": "s1", "title": "Only Slide"}],
        "export_dir": str(tmp_path / "exports"),
        "gamma_settings": [{"variant_id": "A"}],
    }
    with (
        caplog.at_level(logging.DEBUG, logger=GARY_LOGGER),
        pytest.raises(gary_act.GaryActError) as excinfo,
    ):
        gary_act.generate_gamma_variants(payload, client=client)
    assert excinfo.value.tag == "gamma.styleguide.unbound"
    # (i) the old honesty-WARN log record no longer fires on that path.
    seed_records = [
        r for r in caplog.records if "DEFAULT_VARIANT_PAIR" in r.getMessage()
    ]
    assert seed_records == [], "the styleguide-less honesty WARN-seed must be retired"


def test_ac2_default_variant_pair_still_defined_and_by_variant_intact() -> None:
    # (iii) DEFAULT_VARIANT_PAIR stays importable/defined (still feeds the
    # by_variant projection map); deleting it is out of scope.
    assert isinstance(gary_act.DEFAULT_VARIANT_PAIR, tuple)
    assert len(gary_act.DEFAULT_VARIANT_PAIR) == 2
    by_variant = {item["variant_id"] for item in gary_act.DEFAULT_VARIANT_PAIR}
    assert by_variant == {"A", "B"}


def test_ac2_flip_a_is_localized_raise_not_a_seed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # (iv) diff-scoped inspection: the styleguide-less else branch now RAISES
    # with the pinned tag and no longer seeds from by_variant.
    source = inspect.getsource(gary_act._normalized_gamma_settings)
    assert 'tag="gamma.styleguide.unbound"' in source
    assert "merged = dict(by_variant[variant_id])" not in source
    # The retired future-tense WARN text is gone.
    assert "fail-loud deferred to cd-envelope-authoring" not in source


# --- AC-3: success-path byte-identity to pre-flip 7630d091 -----------------------


def _canon(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=True)


def test_ac3_success_path_dispatch_bytes_identical_to_pre_flip(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    settings = [
        {
            "variant_id": "A",
            "styleguide": REAL_GUIDE,
            "keywords": ["hero-diagram", "clinical-navy-gold"],
        }
    ]
    result, client = _run(
        tmp_path,
        monkeypatch,
        {
            "cd_styleguide_resolution": _real_ssot_cd_block(
                [{"variant_id": "A", "styleguide": REAL_GUIDE}]
            ),
            "directive_digest": SAME_DIGEST,
            "trial_start_directive_digest": SAME_DIGEST,
        },
        gamma_settings=settings,
    )
    assert result["styleguide_parity"]["outcome"] == "ok"
    assert result["styleguide_parity"]["reason"] == "match"
    assert client.generate_calls, "non-vacuity: the success run dispatched"
    assert _canon(client.generate_calls) == _GOLDEN_CALLS_CANON, (
        "Flip A/B moved a dispatched-packet byte on the success path"
    )
    assert _canon(result["variant_gamma_settings"]) == _GOLDEN_VGS_CANON, (
        "Flip A/B moved a merged-settings byte on the success path"
    )


# --- AC-7: no clock coupling (E4 two-way ruling) --------------------------------


def test_ac7_neither_flip_reads_clock_eligible() -> None:
    # Flip A branches on styleguide-key presence; Flip B on receipt["outcome"].
    # Neither introduces a clock_eligible attestation gate (E4 ruling: S4 adds
    # no new attestation gate; three-way clock strength stays with S-flip).
    norm_src = inspect.getsource(gary_act._normalized_gamma_settings)
    gen_src = inspect.getsource(gary_act.generate_gamma_variants)
    assert "clock_eligible" not in norm_src, "Flip A must not read clock_eligible"
    assert "clock_eligible" not in gen_src, "Flip B must not read clock_eligible"
    # Flip B keys on the outcome field only.
    assert '"outcome"' in gen_src or "'outcome'" in gen_src
