"""Import adapter exposing execute_generation from hyphenated source tree."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
SOURCE_FILE = REPO_ROOT / "skills" / "gamma-api-mastery" / "scripts" / "gamma_operations.py"


def _load_source_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "skills.gamma_api_mastery._source_gamma_operations",
        SOURCE_FILE,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load gamma operations module from {SOURCE_FILE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_SOURCE = _load_source_module()
execute_generation = _SOURCE.execute_generation


def __getattr__(name: str) -> Any:
    return getattr(_SOURCE, name)

