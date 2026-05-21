from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HARNESS_PATHS = {
    "scripts/utilities/run_cache_hit_harness.py",
    "scripts/utilities/run_5_api_smoke.py",
}
PERMITTED_PYTHON_DIFFS = {
    *HARNESS_PATHS,
    "scripts/utilities/detect_tw_7c_4_live_dispatch_scope_creep.py",
    "tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py",
    "tests/trial/test_trial3_readiness.py",
}


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def _git_lines(*args: str) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return [line.replace("\\", "/") for line in result.stdout.splitlines() if line.strip()]


def test_tw_7c_4_detector_reports_no_fire() -> None:
    result = _run("scripts/utilities/detect_tw_7c_4_live_dispatch_scope_creep.py")

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload == {"status": "PASS", "tripwire_id": "TW-7c-4", "violations": []}


def test_live_dispatch_python_scope_is_bounded() -> None:
    changed = set(_git_lines("diff", "--name-only", "HEAD", "--", "*.py"))
    untracked = set(_git_lines("ls-files", "--others", "--exclude-standard", "--", "*.py"))
    touched_python = changed | untracked

    app_scope = sorted(path for path in touched_python if path.startswith("app/"))
    assert app_scope == [], f"TW-7c-4 fired: app-layer Python touched: {app_scope}"

    unexpected = sorted(
        path
        for path in touched_python
        if path not in PERMITTED_PYTHON_DIFFS
        and not path.startswith(".venv/")
        and not path.startswith("runs/")
    )
    assert unexpected == [], f"TW-7c-4 fired: unexpected Python scope: {unexpected}"


def test_named_harnesses_have_authored_live_dispatch_not_pending_stub() -> None:
    for rel_path in HARNESS_PATHS:
        text = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
        assert "live_dispatch_pending_authoring" not in text
        assert "post-Slab-7c" in text


def test_default_harness_invocations_remain_fail_closed() -> None:
    cache_result = _run("scripts/utilities/run_cache_hit_harness.py", "--all-specialists")
    cache_payload = json.loads(cache_result.stdout)
    assert cache_result.returncode == 1
    assert cache_payload["verdict"] == "not_run"

    smoke_result = _run("scripts/utilities/run_5_api_smoke.py")
    smoke_payload = json.loads(smoke_result.stdout)
    assert smoke_result.returncode == 1
    assert smoke_payload["verdict"] == "not_run"
    assert [row["name"] for row in smoke_payload["apis"]] == [
        "gamma",
        "elevenlabs",
        "canvas",
        "qualtrics",
        "panopto",
    ]


def test_epic3_retirement_and_deferred_inventory_close_are_recorded() -> None:
    epic_text = (
        REPO_ROOT
        / "_bmad-output/planning-artifacts/epics-langchain-langgraph-migration.md"
    ).read_text(encoding="utf-8")
    assert "7c.21a retirement record" in epic_text
    assert "retired-via-7a+7b+7c" in epic_text
    for rel_path in (
        "_bmad-output/planning-artifacts/epics-slab-7a-inter-gate-orchestration.md",
        "_bmad-output/planning-artifacts/epics-slab-7b-specialist-activation-eleven.md",
        "_bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md",
    ):
        assert rel_path in epic_text

    inventory_text = (
        REPO_ROOT / "_bmad-output/planning-artifacts/deferred-inventory.md"
    ).read_text(encoding="utf-8")
    assert "CLOSED 2026-05-07 via 7c.21a" in inventory_text
    assert "_codex-handoff/7c-21a.ready-for-review.md" in inventory_text
