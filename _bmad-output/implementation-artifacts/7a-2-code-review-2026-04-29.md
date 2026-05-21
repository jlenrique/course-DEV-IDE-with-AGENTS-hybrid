# Story 7a.2 Code Review — Manifest Fold-Flags + Compiler Extension

**Reviewer:** Claude Opus 4.7 (final code-review under new cycle: Claude reviews Codex's developed code).
**Reviewed:** 2026-04-29 against working tree post-Codex T1-T10.
**Branch:** `dev/langchain-langgraph-foundation` (HEAD `05bb2aa`).
**Codex self-review:** `_bmad-output/implementation-artifacts/7a-2-codex-self-review-2026-04-29.md` (PASS-WITH-NOTE).

## Verdict

**PASS-WITH-PATCH.** Codex's implementation is sound: 10 ACs (A-J) all PASS at acceptance-auditor layer; SG-1/SG-2/SG-3 invariants honored; Composition Spec §11 trigger absent; Tier-1 patch discipline preserved (no schema_version/pack_version bumps). However, two PATCH items affect existing-test compatibility, and one DEFER carries forward.

## Triage Summary

| Disposition | Count |
|---|---:|
| PATCH | 2 |
| DEFER | 1 |
| DISMISS | 1 |

## Layer Findings

### Layer 1 — Blind Hunter

| ID | Severity | Disposition | Finding | Evidence |
|---|---|---|---|---|
| BH-1 | HIGH | PATCH | `resume_production_trial` raises `GateBypassError` at the FIRST encounter of a downstream active gate after resume, breaking existing `test_approve_verdict_resumes_execution` and `test_edit_verdict_propagates_to_resume_state` semantics. The spec AC-7.2-E text "the runner raises GateBypassError" conflates two cases: (a) trial attempts to BYPASS an active gate without verdict (silent-bypass, raise correct), vs (b) trial REACHES an active gate fresh (normal pause-and-wait per FR34 HIL). Codex implemented (a)'s behavior for both, breaking (b). | `app/marcus/orchestrator/production_runner.py:877` raises on every active-gate-without-verdict; `tests/integration/marcus/test_production_runner_gate_pause_resume.py::test_approve_verdict_resumes_execution` asserts `envelope.status == "completed"` after one G1 verdict (now fails because G2C raises). |
| BH-2 | LOW | DISMISS | Codex notes a 7a.1 editor fallback test fails on environments without `vi` on PATH. | `tests/integration/marcus/test_directive_confirm_or_edit_prompt.py::test_resolve_editor_posix_fallback`. Out of 7a.2 scope; this is a 7a.1 test brittleness against bare environments — not a 7a.2 regression. File as a 7a.1-followup if the operator wants. |

### Layer 2 — Edge Case Hunter

| ID | Severity | Disposition | Finding | Evidence |
|---|---|---|---|---|
| EH-1 | MED | PATCH | `tests/structural/test_gate_fold_manifest_in_sync.py` is order-dependent: passes in isolation; fails when run in the wider battery because some upstream test mutates `state/config/gate_fold_manifest.yaml` in-tree. | Wider battery shows `assert b'# Auto-gene..._target: G4\n' == b'# Auto-gene..._target: G4\n'` (truncated diff) — bytes differ but the visible chunks match. Likely the deterministic timestamp env var or sort_keys=False ordering varies based on whether a prior test has rewritten the file. |

### Layer 3 — Acceptance Auditor

| ID | Severity | Disposition | Finding | Violated AC / rider |
|---|---|---|---|---|
| AA-1 | HIGH | PATCH | AC-7.2-E behavioral semantics: spec text says "raises GateBypassError" but the production-correct semantic is pause-and-wait at active gates (preserve FR34 HIL). The failing tests reveal Codex implemented spec-literal but the spec was ambiguous. | AC-7.2-E |
| AA-2 | LOW | DEFER | Resume-mode `pause_at_gates=False` short-circuit per AC-7.2-E case (c) is preserved per Codex implementation, but the structural test for it (offline-cost-report mode advances past active gates) is implicit in the existing `test_pause_at_g1_verdict_continues_execution_to_completion` rather than a dedicated test. | AC-7.2-E case (c) test pin coverage. |

## Suggested PATCH Commits

### P1 — Refine GateBypassError firing condition (BH-1, AA-1)

**File:** `app/marcus/orchestrator/production_runner.py`.

**Change:** `GateBypassError` should fire ONLY when the runner is about to advance PAST a folded gate whose upstream active gate has NOT received a verdict in the trial's history. Encountering a FRESH active gate (no prior verdict for it) should fall through to the normal pause-and-wait logic (existing `register_decision_card` + `_write_checkpoint` + halt-and-yield-to-operator). The intent of FR-A23 is to refuse SILENT bypass; pause-and-wait is the opposite of silent.

**Test fix companion:** Update `tests/integration/marcus/test_production_runner_gate_pause_resume.py::test_approve_verdict_resumes_execution` and `test_edit_verdict_propagates_to_resume_state` to either:
- (a) Provide G2C verdicts via a second `resume_production_trial` call after the G1 verdict, OR
- (b) Assert the post-resume state is `paused_gate == "G2C"` (the correct multi-gate trial semantics now that 7a.2 honors the full gate inventory), OR
- (c) Use a fixture manifest that has only G1 as the single active gate.

Option (b) is the closest to the original test intent (verify resume continues past the first gate) while honoring the new multi-gate reality.

### P2 — Fix order-dependent gate_fold_manifest sync test (EH-1)

**File:** `tests/structural/test_gate_fold_manifest_in_sync.py` and/or `tests/unit/manifest/test_gate_fold_manifest_emit.py`.

**Change:** Identify which upstream test mutates the on-tree `state/config/gate_fold_manifest.yaml`. Likely culprit: a unit test in `test_gate_fold_manifest_emit.py` calls the emitter against the production output path instead of `tmp_path`. Fix by:
- Audit emit tests use `tmp_path / "gate_fold_manifest.yaml"` exclusively, NEVER the on-tree path.
- The sync test re-emits to `tmp_path` and compares to the committed bytes via `Path.read_bytes()`.

After the fix, run the wider battery 3 times in a row to verify non-flakiness.

## Composition Spec §11 Trigger Check

**Verdict:** no trigger fires.

- No fan-out / parallel dispatch introduced (Trigger 1 N/A).
- No partial state mid-execution (Trigger 2 N/A).
- Gate precedence: 18 declared gates → 4 active pause-points unchanged at runtime semantics; the change is data-shape (manifest declarations + compiler derivation) not policy (Trigger 3 N/A).
- Adapter LOC unchanged (Trigger 4 N/A).
- No new `_act` body category (Trigger 5 N/A).
- §10 entries: Codex correctly did NOT add a §10 entry (Tier-1 additive patch; §10 reserved for substrate evolution).

## Independent Verification Battery

```
.venv/Scripts/python.exe -m pytest tests/unit/manifest tests/integration/marcus tests/composition tests/parity tests/structural tests/specialists/texas tests/specialists/_scaffold -q --tb=line
→ 244 passed, 1 skipped, 3 failed
  Failures: BH-1/AA-1 (2 tests) + EH-1 (1 sync test, order-dependent)

.venv/Scripts/python.exe -m pytest tests/structural/test_gate_fold_manifest_in_sync.py tests/unit/manifest -q
→ 5 passed in 0.61s (sync test passes in isolation)

.venv/Scripts/python.exe scripts/utilities/check_pipeline_manifest_lockstep.py
→ exit 0; trace records orchestration_only_nodes: [directive-composer]

.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7a-2-manifest-fold-flags-compiler-extension.md
→ PASS

.venv/Scripts/lint-imports.exe
→ Contracts: 9 kept, 0 broken.

.venv/Scripts/python.exe -m app.manifest.gate_fold_manifest_emit
.venv/Scripts/python.exe -m app.manifest.gate_topology --unfolded
.venv/Scripts/python.exe -m app.manifest.gate_topology --folded
→ all PASS, expected outputs.
```

## AC Coverage Matrix

| AC | Verdict | Test pin | Notes |
|---|---|---|---|
| A — NodeSpec fold fields | PASS | `tests/unit/manifest/test_node_spec_fold_fields.py` | Mutual-exclusion validator works. |
| B — manifest fold_with declarations | PASS | `tests/unit/manifest/test_manifest_fold_with_declarations.py` | Canonical fold mapping per AC-7.2-B applied. |
| C — production_gate_ids derivation | PASS | `tests/unit/manifest/test_production_gate_ids_derived.py` + `tests/unit/manifest/test_compiler.py` | Hardcoded frozenset removed; function exported. |
| D — gate_fold_manifest emit | PASS-WITH-PATCH | `tests/unit/manifest/test_gate_fold_manifest_emit.py` + `tests/structural/test_gate_fold_manifest_in_sync.py` | Sync test order-dependent (EH-1). |
| E — runner refuses gate-bypass | PASS-WITH-PATCH | `tests/integration/marcus/test_gate_bypass_refusal.py` | Refusal logic too strict for fresh gate-encounter (BH-1, AA-1). |
| F — operator topology CLI | PASS | `tests/unit/manifest/test_gate_topology_cli.py` + manual CLI runs | --unfolded, --folded, --audit all behave per spec. |
| G — lockstep orchestration tolerance + directive-composer registration | PASS | `tests/structural/test_lockstep_orchestration_only_tolerance.py` + `tests/structural/test_pipeline_manifest_directive_composer_node.py` | 7a.1's deferred follow-on closed cleanly. |
| H — Tier-1 discipline | PASS | Schema/pack versions unchanged; lockstep PASS | Codex correctly resisted Tier-2 framing in old prose. |
| I — N-item trace | PASS | Codex self-review records trace | All N-items honored. |
| J — D12 close protocol | HANDOFF-TO-CLAUDE | (this review) | Claude closes after P1/P2 remediation. |

## Rider / Spec Trace

All AC-7.2-A through AC-7.2-J spec elements honored in implementation; PATCH items address production-semantics + test-isolation concerns surfaced during independent verification.

## Suggested Remediation Plan

1. Apply P1 (runner GateBypassError refinement + test updates).
2. Apply P2 (sync-test order-independence).
3. Re-run wider regression battery; expect 247+ passed / 1 skipped / 0 failed.
4. Update Codex's 7a.2 spec Dev Agent Record with Claude's remediation cycle 1 notes.
5. Flip `migration-7a-2-manifest-fold-flags-compiler-extension` review → done in sprint-status.yaml.
6. Mark `7a-1-deferred-directive-composer-manifest-node` follow-on as CLOSED-by-7a.2 in deferred-inventory.md.
7. Commit.
