from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


def test_texas_run_wrangler_is_module_loadable() -> None:
    runner_path = (
        Path(__file__).resolve().parents[3]
        / "skills"
        / "bmad-agent-texas"
        / "scripts"
        / "run_wrangler.py"
    )
    spec = importlib.util.spec_from_file_location("run_wrangler_story_3_1_probe", runner_path)
    if spec is None or spec.loader is None:
        pytest.skip("spec_from_file_location returned None for Texas run_wrangler.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["run_wrangler_story_3_1_probe"] = module
    spec.loader.exec_module(module)
    assert hasattr(module, "build_dispatch_envelope")
