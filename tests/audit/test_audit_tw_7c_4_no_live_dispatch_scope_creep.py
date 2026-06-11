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
    # Trial-3-blocking wiring fix 2026-05-21 (sprint-change-proposal-2026-05-21-trial3-wiring.md):
    # §02A LLM-driven composer was authored at Story 7c.3a but never wired into the
    # trial CLI; G0 directive composition was still invoking the legacy Story-7a.1
    # naive corpus-scan fallback. Party-mode-ratified Round 1 4-of-4 APPROVE-with-
    # amendments (Winston W-A1 lifted adapter to app/composers/section_02a/cli_adapter.py
    # so future consumers reuse the call-shape bridge). Bounded 2-path extension;
    # freeze predicates (line 56 + line 65) remain in force for all other paths.
    "app/marcus/cli/trial.py",
    "app/composers/section_02a/cli_adapter.py",
    # SCP 2026-05-21 §7 M-A1: new adapter wiring-contract tests authored as
    # part of C2a; allowlisting per same C1 substrate-amendment scope.
    "tests/marcus_cli/__init__.py",
    "tests/marcus_cli/test_compose_section_02a_directive_adapter.py",
    # Epic 34 §02A downstream-consumer coherence amendment 2026-05-22
    # (sprint-change-proposal-2026-05-22-epic-34-substrate-amendment.md):
    # Phase B Quinn-synthesis ratified Option 5 "Round-Trip First, Then Harmonize."
    # 7-story Epic resolving §02A→wrangler→pre_packet schema drift surfaced by
    # Trial-3 attempt-2 (run-id 6a3393f8-...). SCP-ratification party-mode Round
    # 1 (2026-05-22): 4-of-4 APPROVE-with-amendments (W-SCP-A1 + A-A1/A-A2/A-A3
    # + M-Murat-SCP-1..3 + A-John-1/A-John-2). 27-path bounded extension across
    # the §02A composer package + Texas wrangler script + Marcus intake + new
    # integration-test paths + temporary translator scaffolding + §02A test
    # surface for src_id→ref_id migration + legacy composer test surface for
    # Story 34-6 rewire/delete. Freeze predicates (L79 app_scope bind / L84
    # `app_scope == []` assert + L89 unexpected bind / L96 `unexpected == []`
    # assert) remain enforced for all non-allowlisted paths.
    #
    # Story 34-1 — NEW temporary in-tree translator scaffolding (deleted at
    # Story 34-7 per NFR-E34-10 hard AC); integration-test ship-proof.
    "app/composers/section_02a/_wrangler_translator.py",
    "tests/integration/test_section_02a_to_wrangler_subprocess_roundtrip.py",
    # Story 34-1 fixture-dir defensive (Murat seam): pre-bind in case Codex T1-T9
    # emits any .py under fixture dir (__init__.py / conftest.py). Fixture data
    # files (.yaml/.md/.txt) escape the *.py-scoped predicate at audit-file L64.
    "tests/fixtures/integration/section_02a/__init__.py",
    "tests/fixtures/integration/section_02a/conftest.py",
    # Story 34-2 — wrangler input validator: 6-role union + excluded_reason
    # + cross-field invariants (Winston A1 + Murat M-Murat-3 bindings).
    "skills/bmad-agent-texas/scripts/run_wrangler.py",
    # Trial-3 attempt-3 crash fix 2026-06-11 (run-id 235e0570-...): production
    # dispatch invoked the wrangler subprocess with cwd=REPO_ROOT while the
    # §02A composer emits corpus-relative locators — every local_file fetch
    # failed File-not-found → empty bundle → RetrievalScopeError at Texas
    # hardening (observed_words=7 vs floor=570). Fix mirrors the Story 34-1
    # ratchet's pinned invocation contract (cwd=directive.corpus_dir) in
    # app/specialists/texas/retrieval_dispatch.py + pins the cwd contract in
    # the dispatch test (the prior kwargs-pin only asserted cwd truthy).
    # Bounded 3-path extension; freeze predicates remain in force. Second
    # finding in the same crash arc: _act.py's exit-10 -> "no-results"
    # early-return discarded valid complete_with_warnings bundles (903
    # extracted words dropped); the wrangler taxonomy has no "no-results"
    # status. Exit-10 bundles now parse exactly like exit 0.
    "app/specialists/texas/retrieval_dispatch.py",
    "app/specialists/texas/_act.py",
    "tests/specialists/texas/test_texas_act_node_dispatch.py",
    # Third finding, same trial arc: CANONICAL_SPECIALIST_IDS never adopted
    # irene_pass1 (a distinct §04 specialist package the compiler's
    # SPECIALIST_ALIASES already targets) — first live §04 dispatch crashed
    # at emit_spans with "unknown specialist_id". Roster 11 -> 12 with
    # coordinated shape-pin bump in test_run_summary_yaml_emit.py.
    "app/models/state/specialist_summary_artifacts.py",
    "tests/integration/marcus/test_run_summary_yaml_emit.py",
    # Story 34-2 wrangler-side test (substrate-audit-corrected path 2026-05-22;
    # co-located with existing test_run_wrangler.py at skills/.../tests/).
    "skills/bmad-agent-texas/scripts/tests/test_run_wrangler_role_enum_union_and_excluded_reason.py",
    # Story 34-4 wrangler-side test (also under skills/.../tests/).
    "skills/bmad-agent-texas/scripts/tests/test_run_wrangler_sme_refs_emission.py",
    # Story 34-3 — §02A composer src_id → ref_id rename + J-A1(a)/(b)
    # cli_adapter completion (Winston A2 binding).
    "app/composers/section_02a/directive_model.py",
    "app/composers/section_02a/composer.py",
    "app/composers/section_02a/_prompt.py",
    "app/composers/section_02a/_cache.py",
    # Story 34-3 / 34-7 — §02A package __init__.py re-export surface
    # (Winston W-SCP-A1 + Amelia A-A2 2-voice consensus); covers both
    # field-rename ripple AND translator-deletion re-export prune.
    "app/composers/section_02a/__init__.py",
    # Story 34-3 — §02A test surface migration for `src_id → ref_id` rename
    # (Amelia A-A1 grep-verified hits across both composer + gate test trees).
    "tests/composers/section_02a/_helpers.py",
    "tests/composers/section_02a/__init__.py",
    "tests/composers/section_02a/test_composer_cache_key_normalization.py",
    "tests/composers/section_02a/test_composer_classification.py",
    "tests/composers/section_02a/test_composer_directive_model_shape.py",
    "tests/composers/section_02a/test_composer_trial_2_finding_2_regression.py",
    "tests/composers/section_02a/test_composer_utf8_write.py",
    "tests/gates/section_02a/_helpers.py",
    "tests/gates/section_02a/test_g0_poll_surface_field_level_edit.py",
    # Story 34-4 — wrangler metadata.json sme_refs additive emission;
    # pre_packet possibly minor touch (consumer side).
    "app/marcus/intake/pre_packet.py",
    # Story 34-5 — translator-shrinkage sequence test (carrier story).
    "tests/integration/test_section_02a_translator_shrinkage_sequence.py",
    # Story 34-7 — final translator deletion + round-trip simplification.
    "docs/dev-guide/specialist-anti-patterns.md",
    # Story 34-6 — legacy directive_composer.py DELETION; 7 test files
    # rewired or deleted (existing tests; deletion still counts as
    # `git diff` touch for the L79/L84 + L89/L96 predicates).
    "app/marcus/orchestrator/directive_composer.py",
    "tests/unit/marcus/orchestrator/test_directive_composer_pure.py",
    "tests/unit/marcus/orchestrator/test_directive_composer_materialization.py",
    "tests/specialists/texas/test_texas_live_retrieval_against_real_directive.py",
    "tests/parity/test_trial_475_texas_hardening_regression.py",
    "tests/parity/test_trial_475_directive_composition_regression.py",
    "tests/composition/test_texas_to_cd_chain.py",
    "tests/composition/test_slab_7b_wave_1_opener_composition_smoke.py",
    # Story 34-6 structural orphan cleanup after deleting the legacy composer.
    "tests/structural/test_directive_io_uses_utf8_explicit.py",
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

    # SCP 2026-05-21 §4.1 + C1b (Trial-3 wiring fix substrate amendment): the
    # `app_scope` predicate was originally a hard ban on all app/ Python edits,
    # not allowlist-aware. The 2026-05-19 SCP and 2026-05-21 Round-1 party-mode
    # ratification both reasoned only about the line-74 `unexpected` predicate;
    # the dual-predicate structure (line-65 + line-74) was a known-but-
    # underspecified seam. C1b folds line-65 into the same PERMITTED_PYTHON_DIFFS
    # allowlist mechanism so that ratified app/ edits (currently
    # app/marcus/cli/trial.py + app/composers/section_02a/cli_adapter.py) can
    # land without tripwire firing. Defense-in-depth is preserved: app/ edits
    # still require explicit allowlisting; non-app/ edits also still bounded by
    # line 74.
    app_scope = sorted(
        path
        for path in touched_python
        if path.startswith("app/") and path not in PERMITTED_PYTHON_DIFFS
    )
    assert app_scope == [], (
        f"TW-7c-4 fired: unauthorized app-layer Python touched (not in "
        f"PERMITTED_PYTHON_DIFFS): {app_scope}"
    )

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
