"""Shared importlib helper for specialist dispatch wrappers."""

from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType


def load_module(module_name: str, module_path: Path) -> ModuleType:
    """Load a Python module from a filesystem path."""
    spec = spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load module spec for {module_name} at {module_path}")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


__all__ = ["load_module"]
