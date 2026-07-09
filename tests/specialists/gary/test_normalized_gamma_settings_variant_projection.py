"""Retire the ``[A,B]`` dispatch padding — ``_normalized_gamma_settings`` returns
ONLY the variants actually named in the payload ``gamma_settings`` list, in payload
order.

RED-first (story ``styleguide-retire-default-variant-pair``): before the fix the
normalizer ends with a hardcoded ``return [by_variant["A"], by_variant["B"]]`` and so
always emits BOTH variants regardless of what the payload named — a single-styleguide
binding still paid-dispatches an unbound fixture-B deck. AC#1 (single-variant → len 1)
is RED before the fix; AC#2 (two-variant A/B) never goes red.
"""

from __future__ import annotations

import logging

import pytest

from app.specialists.gary._act import (
    GaryActError,
    _normalized_gamma_settings,
)

from ._s4_seed import install_seed_resolver, seed_name


def _payload(*items: dict[str, object]) -> dict[str, object]:
    return {"gamma_settings": list(items)}


def _seeded(*variant_ids: str) -> dict[str, object]:
    # Canonical-arc S4: a NAMED variant must carry a styleguide binding
    # (styleguide-less now fails loud). Bind each to the byte-identical seed.
    return _payload(
        *({"variant_id": vid, "styleguide": seed_name(vid)} for vid in variant_ids)
    )


def test_single_variant_binds_one(monkeypatch: pytest.MonkeyPatch) -> None:
    # AC#1 [RED before fix] — a payload naming ONE variant returns exactly that one.
    install_seed_resolver(monkeypatch)
    out = _normalized_gamma_settings(_seeded("A"))
    assert len(out) == 1
    assert out[0]["variant_id"] == "A"


def test_two_variant_path_preserved(monkeypatch: pytest.MonkeyPatch) -> None:
    # AC#2 [regression pin — must stay GREEN] — naming both A and B returns both,
    # A before B (payload order). Protects the legacy concierge A/B default flow.
    install_seed_resolver(monkeypatch)
    out = _normalized_gamma_settings(_seeded("A", "B"))
    assert len(out) == 2
    assert [item["variant_id"] for item in out] == ["A", "B"]


def test_variant_order_is_payload_order(monkeypatch: pytest.MonkeyPatch) -> None:
    # AC#3 — output order == payload list order (``dict.fromkeys``, not ``set``).
    install_seed_resolver(monkeypatch)
    out = _normalized_gamma_settings(_seeded("B", "A"))
    assert [item["variant_id"] for item in out] == ["B", "A"]


def test_empty_list_returns_empty() -> None:
    # AC#4 — ``gamma_settings == []`` → ``[]`` (parity with ``None``, which already
    # returns ``[]``). Shape-pin so a future refactor cannot resurrect the pair.
    assert _normalized_gamma_settings({"gamma_settings": []}) == []
    assert _normalized_gamma_settings({"gamma_settings": None}) == []


def test_unknown_variant_id_fails_loud() -> None:
    # AC#5 — a present-but-unknown ``variant_id`` raises (pins the existing guard),
    # never silently dropped, never padded to A/B.
    with pytest.raises(GaryActError) as exc:
        _normalized_gamma_settings(_payload({"variant_id": "C"}))
    assert exc.value.tag == "gamma.settings.invalid"


def test_base_seed_does_not_resurrect_padding(monkeypatch: pytest.MonkeyPatch) -> None:
    # AC#6 — a single named variant (now styleguide-bound) returns len 1; the
    # base fills fields for the requested variant only and must NOT re-add the
    # sibling.
    install_seed_resolver(monkeypatch)
    out = _normalized_gamma_settings(_seeded("B"))
    assert len(out) == 1
    assert out[0]["variant_id"] == "B"


def test_styleguide_less_named_variant_now_raises_unbound() -> None:
    # Canonical-arc S4 amendment (AC-9): S3/pre-S4 seeded a present variant from
    # DEFAULT_VARIANT_PAIR with a WARNING. S4 Flip A retires the hidden default —
    # a present variant with no bound styleguide is now a governance error.
    with pytest.raises(GaryActError) as exc:
        _normalized_gamma_settings(_payload({"variant_id": "A"}))
    assert exc.value.tag == "gamma.styleguide.unbound"
    assert "A" in str(exc.value)


# --- RED-first remediation (3-lane review, styleguide-retire-default-variant-pair) --


def test_duplicate_variant_id_fails_loud(monkeypatch: pytest.MonkeyPatch) -> None:
    # R1 (Blind Hunter SHOULD-FIX) [RED before fix] — a payload naming the SAME
    # variant twice currently silently merge-accumulates (order-dependent, hidden).
    # It must FAIL LOUD instead of quietly collapsing to one projected entry.
    # (S4: both entries are styleguide-bound so the duplicate guard — not Flip A —
    # is the surface under test.)
    install_seed_resolver(monkeypatch)
    with pytest.raises(GaryActError) as exc:
        _normalized_gamma_settings(
            _payload(
                {"variant_id": "A", "styleguide": seed_name("A")},
                {"variant_id": "A", "styleguide": seed_name("A")},
            )
        )
    assert exc.value.tag == "gamma.settings.invalid"
    assert "more than once" in str(exc.value)


def test_nonempty_settings_naming_zero_valid_variants_fails_loud() -> None:
    # R2 (Edge Case Hunter) [RED before fix] — a NON-EMPTY gamma_settings whose
    # entries are all skipped (``[None]``) yields present_ids == {} → returns []
    # → the consumer's ``or (...)`` fallback re-dispatches the default A/B fixture,
    # silently re-introducing the exact unbound-fixture dispatch this story retired.
    # It must FAIL LOUD.
    with pytest.raises(GaryActError) as exc:
        _normalized_gamma_settings({"gamma_settings": [None]})
    assert exc.value.tag == "gamma.settings.invalid"
    with pytest.raises(GaryActError):
        _normalized_gamma_settings({"gamma_settings": [None, None]})


def test_empty_and_none_still_return_empty_after_r2_guard() -> None:
    # R2 regression pin — the R2 guard must fire ONLY for a NON-EMPTY raw that
    # yields zero present_ids. An EMPTY list and ``None`` still return ``[]``
    # (AC#4 preserved), never raise.
    assert _normalized_gamma_settings({"gamma_settings": []}) == []
    assert _normalized_gamma_settings({"gamma_settings": None}) == []


def test_styleguide_bound_variant_emits_no_warning(
    caplog: pytest.LogCaptureFixture,
) -> None:
    # R4 (Acceptance Auditor) negative-WARN — a variant BOUND to a real CD-owned
    # styleguide seeds from the library record (the ``if`` branch), NOT from the
    # DEFAULT_VARIANT_PAIR smoke fixture, so it emits NO WARNING. Guards against a
    # future refactor hoisting the honesty WARN above the styleguide-branch split.
    with caplog.at_level(logging.WARNING, logger="app.specialists.gary._act"):
        out = _normalized_gamma_settings(
            _payload({"variant_id": "A", "styleguide": "hil-2026-apc-crossroads-classic"})
        )
    assert len(out) == 1
    assert out[0]["variant_id"] == "A"
    warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert not warnings, f"styleguide-bound variant must not WARN; got {warnings!r}"
