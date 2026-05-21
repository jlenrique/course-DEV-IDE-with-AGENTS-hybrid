"""Shared helpers for `app.models.state` shape-pin tests.

Centralizes the round-trip + forbidden-field assertion patterns so each
per-model test file expresses only the model-specific intent.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel

GOLDEN_FIXTURES_DIR: Path = (
    Path(__file__).resolve().parents[3] / "fixtures" / "models" / "state"
)


def load_golden(name: str) -> dict[str, Any]:
    """Load a golden JSON fixture by short name (e.g. ``"sanctum_fingerprint"``)."""
    path = GOLDEN_FIXTURES_DIR / f"golden_{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def assert_round_trip(model_class: type[BaseModel], golden: dict[str, Any]) -> None:
    """Assert the model round-trips the golden fixture byte-for-byte.

    Validates JSON → model → dict and asserts the residual matches the
    parsed golden dict (modulo JSON whitespace, which json.loads
    canonicalizes by parsing both sides through dict equality).
    """
    instance = model_class.model_validate(golden)
    dumped = instance.model_dump(mode="json")
    assert dumped == golden, (
        f"{model_class.__name__} round-trip diverged:\n"
        f"  golden:  {json.dumps(golden, sort_keys=True, indent=2)}\n"
        f"  dumped:  {json.dumps(dumped, sort_keys=True, indent=2)}"
    )


def assert_forbids_extra_field(
    model_class: type[BaseModel],
    valid_kwargs: dict[str, Any],
) -> None:
    """Assert ``model_class(**valid_kwargs, bogus_field=True)`` raises ValidationError."""
    from pydantic import ValidationError

    polluted = {**valid_kwargs, "bogus_extra_field_for_test": True}
    try:
        model_class.model_validate(polluted)
    except ValidationError:
        return
    msg = (
        f"{model_class.__name__} accepted bogus extra field; extra='forbid' is "
        "missing or not enforced."
    )
    raise AssertionError(msg)
