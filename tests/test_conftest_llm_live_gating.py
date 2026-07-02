"""Gate-semantics contract for the ``llm_live`` marker (carried-findings D-C1).

Party-ratified semantics (2026-07-02, carried-findings remediation batch,
`carried-findings-remediation-greenlight-party-record-2026-07-02.md` D-C1):

1. ``llm_live`` tests are DESELECTED in the default pytest profile — even when
   a real ``OPENAI_API_KEY`` is present. ``--run-live`` is the ONLY switch that
   selects them (``-m llm_live`` alone does not bypass the deselection).
2. Under ``--run-live``, the pre-existing key-based auto-skip is RETAINED:
   a missing/placeholder ``OPENAI_API_KEY`` yields a graceful SKIP, not an
   error and not a live call.
3. Rot guard: ``--run-live --collect-only -m llm_live`` over ``tests/`` must
   collect the full pinned llm_live module set, so the global gating flip can
   never silently kill the live battery.

RED-first witness: authored 2026-07-02 BEFORE the tests/conftest.py flip;
``test_default_profile_deselects_llm_live_even_with_real_key`` was RED at HEAD
(llm_live tests were collected — and would spend — in the default profile
whenever a real key was present).

Each check shells out to a fresh pytest subprocess so the repo's real
``tests/conftest.py`` collection hooks are exercised end-to-end. All
subprocess runs are either ``--collect-only`` or placeholder-key runs:
zero live-LLM spend.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

VISION_LIVE_TEST = "tests/specialists/vision/test_vision_live_roundtrip.py"

# A syntactically real-looking key that is NOT the Slab-1 placeholder sentinel.
# tests/conftest.py only copies .env values for keys absent from the
# environment, so setting this in the subprocess env wins over .env.
_REAL_LOOKING_KEY = "sk-test-real-looking-key-for-gating-contract-000"
_PLACEHOLDER_KEY = "sk-substrate-no-real-key-do-not-invoke"

# Rot-guard pin: the known llm_live module set (derived by marker grep +
# `--run-live --collect-only -m llm_live` at flip time, 2026-07-02: 11 tests
# across these 10 modules). If you add/remove an llm_live test module, update
# this pin DELIBERATELY — that loudness is the point.
EXPECTED_LLM_LIVE_MODULES = {
    "tests/end_to_end/test_cache_hit_rate_baseline.py",
    "tests/end_to_end/test_cache_hit_rate_kira_populated.py",
    "tests/end_to_end/test_dan_cache_hit_rate.py",
    "tests/end_to_end/test_irene_pass1_cache_hit_rate.py",
    "tests/end_to_end/test_tracy_cache_hit_rate.py",
    "tests/integration/marcus/test_adhoc_facade.py",
    "tests/specialists/cd/test_cd_act_node_dispatch.py",
    "tests/specialists/desmond/test_desmond_act_node_authoring.py",
    "tests/specialists/irene/test_irene_act_node_llm_invocation.py",
    "tests/specialists/vision/test_vision_live_roundtrip.py",
}


def _run_pytest(args: list[str], *, openai_key: str) -> subprocess.CompletedProcess[str]:
    """Run pytest in a fresh subprocess with a controlled OPENAI_API_KEY."""
    env = os.environ.copy()
    env["OPENAI_API_KEY"] = openai_key
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-n0", "-q", *args],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    )


def _collected_nodeids(stdout: str) -> list[str]:
    return [
        line.strip()
        for line in stdout.splitlines()
        if "::" in line and not line.startswith(("=", "<", " "))
    ]


def test_default_profile_deselects_llm_live_even_with_real_key() -> None:
    """(i) Default profile + real-looking key -> llm_live DESELECTED, not run."""
    proc = _run_pytest(
        [VISION_LIVE_TEST, "--collect-only"], openai_key=_REAL_LOOKING_KEY
    )
    nodeids = _collected_nodeids(proc.stdout)
    assert nodeids == [], (
        "llm_live test was COLLECTED in the default profile with a real-looking "
        "key present — the D-C1 global gating flip is not in effect. Collected: "
        f"{nodeids!r}\n--- stdout ---\n{proc.stdout}"
    )
    assert "deselected" in proc.stdout, (
        "expected loud deselection reporting in the default profile; got:\n"
        f"{proc.stdout}"
    )


def test_run_live_collects_llm_live() -> None:
    """(ii) --run-live -> llm_live tests are collected."""
    proc = _run_pytest(
        [VISION_LIVE_TEST, "--collect-only", "--run-live"],
        openai_key=_REAL_LOOKING_KEY,
    )
    nodeids = _collected_nodeids(proc.stdout)
    assert any(
        "test_live_gpt55_perceives_six_real_pngs_and_captures_recordings" in n
        for n in nodeids
    ), (
        "--run-live must collect the llm_live vision roundtrip test; collected: "
        f"{nodeids!r}\n--- stdout ---\n{proc.stdout}"
    )


def test_rot_guard_run_live_collects_full_llm_live_module_set() -> None:
    """(iii) Rot guard: --run-live collect-only over tests/ pins the module set."""
    proc = _run_pytest(
        ["tests/", "--collect-only", "--run-live", "-m", "llm_live"],
        openai_key=_REAL_LOOKING_KEY,
    )
    nodeids = _collected_nodeids(proc.stdout)
    modules = {n.split("::", 1)[0].replace("\\", "/") for n in nodeids}
    assert modules == EXPECTED_LLM_LIVE_MODULES, (
        "llm_live module set drifted from the rot-guard pin.\n"
        f"missing: {sorted(EXPECTED_LLM_LIVE_MODULES - modules)}\n"
        f"unexpected: {sorted(modules - EXPECTED_LLM_LIVE_MODULES)}\n"
        f"--- stdout ---\n{proc.stdout}"
    )


def test_run_live_e2e_alone_arms_double_marked_llm_live_tests() -> None:
    """(v) Matrix cell: a test double-marked ``llm_live`` + ``live_api_e2e``
    under ``--run-live-e2e`` ALONE must be collected — the e2e opt-in arms its
    own double-marked tests (llm_live deselection is waived for them). Pass-2
    key-skip still applies. Uses a synthetic double-marked probe under
    ``tests/`` (removed after) so the real conftest hooks are exercised in the
    subprocess without touching the live battery."""
    probe_dir = REPO_ROOT / "tests" / f"_synthetic_gating_probe_{uuid.uuid4().hex}"
    probe_dir.mkdir()
    probe = probe_dir / "test_double_marked_probe.py"
    probe.write_text(
        "import pytest\n"
        "\n"
        "\n"
        "@pytest.mark.llm_live\n"
        "@pytest.mark.live_api_e2e\n"
        "def test_double_marked_probe() -> None:\n"
        "    pass\n",
        encoding="utf-8",
    )
    rel = probe.relative_to(REPO_ROOT).as_posix()
    try:
        proc = _run_pytest(
            [rel, "--collect-only", "--run-live-e2e"], openai_key=_REAL_LOOKING_KEY
        )
        nodeids = _collected_nodeids(proc.stdout)
        assert any("test_double_marked_probe" in n for n in nodeids), (
            "--run-live-e2e alone must collect a double-marked "
            "llm_live+live_api_e2e test (the e2e opt-in arms its own "
            f"double-marked tests); collected: {nodeids!r}\n"
            f"--- stdout ---\n{proc.stdout}"
        )
        # Pass-2 key-skip still applies on the e2e arm: placeholder key -> SKIP.
        proc_skip = _run_pytest([rel, "--run-live-e2e"], openai_key=_PLACEHOLDER_KEY)
        assert proc_skip.returncode == 0 and "1 skipped" in proc_skip.stdout, (
            "--run-live-e2e + placeholder key must SKIP the double-marked test "
            f"gracefully. returncode={proc_skip.returncode}\n"
            f"--- stdout ---\n{proc_skip.stdout}\n--- stderr ---\n{proc_skip.stderr}"
        )
    finally:
        shutil.rmtree(probe_dir, ignore_errors=True)


def test_run_live_without_real_key_skips_not_errors() -> None:
    """(iv) --run-live + placeholder key -> graceful SKIP (pass-2 retained)."""
    proc = _run_pytest(
        [VISION_LIVE_TEST, "--run-live"], openai_key=_PLACEHOLDER_KEY
    )
    assert proc.returncode == 0, (
        "--run-live with the placeholder key must SKIP gracefully, not error. "
        f"returncode={proc.returncode}\n--- stdout ---\n{proc.stdout}\n"
        f"--- stderr ---\n{proc.stderr}"
    )
    assert "1 skipped" in proc.stdout, (
        f"expected '1 skipped' under --run-live + placeholder key; got:\n{proc.stdout}"
    )
