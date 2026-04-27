from __future__ import annotations

from app.runtime.cascade_config import ensure_pricing_covers_cascade, load_cascade, load_pricing


def test_every_cascade_model_has_a_pricing_entry() -> None:
    ensure_pricing_covers_cascade(load_cascade(), load_pricing())
