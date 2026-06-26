"""S2 RED floor (a) — DETERMINISM across process restarts x PYTHONHASHSEED.

Same component_selection -> identical (input_closure_digest, composed_graph_digest)
across >=3 subprocess invocations, parametrized PYTHONHASHSEED in {0, "random"}.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
_RUNS = 3


def _run_subprocess(selection_spec: str, hashseed: str) -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = hashseed
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.run(
        [sys.executable, "-m", "tests.unit.composition._digest_cli", selection_spec],
        cwd=_REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(proc.stdout.strip())


@pytest.mark.parametrize("hashseed", ["0", "random"])
@pytest.mark.parametrize("selection_spec", ["deck", "deck,motion", "deck,motion,workbook"])
def test_digest_is_deterministic_across_restarts_and_hashseeds(
    selection_spec: str, hashseed: str
) -> None:
    results = [_run_subprocess(selection_spec, hashseed) for _ in range(_RUNS)]
    first = results[0]
    for r in results[1:]:
        assert r["input_closure_digest"] == first["input_closure_digest"]
        assert r["composed_graph_digest"] == first["composed_graph_digest"]


def test_digest_is_identical_across_both_hashseeds() -> None:
    seed0 = _run_subprocess("deck,motion", "0")
    seed_random = _run_subprocess("deck,motion", "random")
    assert seed0["input_closure_digest"] == seed_random["input_closure_digest"]
    assert seed0["composed_graph_digest"] == seed_random["composed_graph_digest"]
