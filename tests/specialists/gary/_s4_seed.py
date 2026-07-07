"""Canonical-arc S4 test helper — bind the retired DEFAULT_VARIANT_PAIR seed
through a styleguide binding.

S4 Flip A retires the styleguide-less DEFAULT_VARIANT_PAIR seed: a NAMED variant
present in ``gamma_settings`` with no ``styleguide`` key now fails loud
(``gamma.styleguide.unbound``). A body of pre-S4 unit tests exercised OTHER
behavior (enum/theme/studio/packet validation) via a styleguide-LESS named
variant, relying on the seed for defaults. To keep testing that real intent on
the NOW-canonical styleguide-bound path WITHOUT weakening any assertion (AC-9
superset discipline), these tests bind each variant to a synthetic guide whose
resolved base is EXACTLY the old ``DEFAULT_VARIANT_PAIR`` seed for that variant
(minus ``variant_id``, which the merge sets explicitly). The merged per-variant
settings are then BYTE-IDENTICAL to the pre-S4 styleguide-less path, so every
downstream assertion holds unchanged — the only change is that the seed now
arrives via the canonical styleguide binding instead of the retired hidden
default.
"""

from __future__ import annotations

from typing import Any

from app.specialists.gary import _act as gary_act


def seed_name(variant_id: str) -> str:
    """The synthetic styleguide name that resolves to the seed for a variant."""
    return f"s4-seed-{variant_id.upper()}"


def install_seed_resolver(monkeypatch: Any) -> None:
    """Monkeypatch ``resolve_styleguide`` so ``seed_name(vid)`` resolves to the
    DEFAULT_VARIANT_PAIR base for ``vid`` (byte-identical to the retired seed)."""
    seeds = {
        seed_name(item["variant_id"]): {
            key: value for key, value in item.items() if key != "variant_id"
        }
        for item in gary_act.DEFAULT_VARIANT_PAIR
    }

    def _fake(name: str, **_kwargs: Any) -> dict[str, Any]:
        # Deep-ish copy via dict(); nested lists (keywords) are copied so a
        # per-variant override can never mutate the shared seed table.
        base = seeds[name]
        return {
            key: (list(value) if isinstance(value, list) else value)
            for key, value in base.items()
        }

    monkeypatch.setattr(gary_act, "resolve_styleguide", _fake)
