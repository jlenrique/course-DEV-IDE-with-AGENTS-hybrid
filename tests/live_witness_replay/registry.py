"""Witness-replay registry loader + the strict-mode discipline (skip ≠ green).

Minimal by design (amendment A12: replay + strict mode; no framework-building).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = Path(__file__).with_name("witnesses.yaml")
STRICT_ENV = "WITNESS_REPLAY_STRICT"
# R6: STRICT arms on these values (case-insensitive, stripped); the explicit
# false-set (or unset/empty) disarms; ANY other non-empty value is a hard
# configuration error — a typo'd flag must never silently disarm a pre-flight.
_STRICT_TRUE = frozenset({"1", "true", "yes", "on"})
_STRICT_FALSE = frozenset({"", "0", "false", "no", "off"})


def load_registry() -> dict[str, Any]:
    registry = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    assert registry["schema_version"] == "witness-replay-registry.v1"
    return registry


def family(name: str) -> dict[str, Any]:
    for row in load_registry()["families"]:
        if row["family"] == name:
            return row
    raise KeyError(f"witness family not enrolled: {name}")


def strict_mode() -> bool:
    raw = os.environ.get(STRICT_ENV, "")
    value = raw.strip().lower()
    if value in _STRICT_TRUE:
        return True
    if value in _STRICT_FALSE:
        return False
    raise ValueError(
        f"{STRICT_ENV}={raw!r} is not a recognized flag: use one of "
        f"{sorted(_STRICT_TRUE)} to arm strict mode or "
        f"{sorted(v for v in _STRICT_FALSE if v)} / unset to disarm "
        "(an unrecognized value never silently disarms)"
    )


def skip_or_fail(reason: str) -> None:
    """SKIP in normal runs; FAIL in strict pre-flight runs (skip ≠ green)."""
    if strict_mode():
        pytest.fail(f"{STRICT_ENV}=1: {reason} (skip is not green)")
    pytest.skip(reason)


def witness_path(row: dict[str, Any]) -> Path:
    return REPO_ROOT / str(row["path"])
