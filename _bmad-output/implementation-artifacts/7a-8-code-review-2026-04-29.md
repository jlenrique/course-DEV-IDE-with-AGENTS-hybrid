# Story 7a.8 Code Review — Integration + Parity-Test Suite + Slab 7a Closeout

**Reviewer:** Claude Opus 4.7 (final code-review under new cycle).
**Reviewed:** 2026-04-29 against working tree post-Codex T1-T11.
**Codex self-review:** `_bmad-output/implementation-artifacts/7a-8-codex-self-review-2026-04-29.md` (PASS-WITH-OPERATOR-GATE-PENDING).

## Verdict

**PASS-WITH-OPERATOR-GATE-PENDING.** 0 PATCH / 0 DEFER / 0 DISMISS on Codex's automated deliverables. The DUAL-GATE Gate-2 operator-witnessed ceremony (AC-7.8-I trial-2 BS-2 readiness predicate confirmation) is the only remaining item; Codex prepared the script + automated evidence; operator runs trial-2 (or trial-2 dry-run) + pastes verbatim stdout to fully close.

## Triage Summary

| Disposition | Count |
|---|---:|
| PATCH | 0 |
| DEFER | 0 |
| DISMISS | 0 |
| OPERATOR-GATE-PENDING | 1 (AC-7.8-I; BS-2 readiness) |

## Layer Findings

### Layer 1 — Blind Hunter

PASS. Independent verification spot-checks confirm:
- No specialist `_act` bodies modified (substrate-isolation invariant N4 preserved across all 8 stories).
- No parallel 33-file parity suite created — Codex correctly used the EXISTING 7a.6 scaffold and added per-row metadata (`MAPPING_CHECKLIST_ROW` + `REFERENCES_FRS` headers).
- 44 active tests + 18 skipped placeholders (placeholders awaiting Slab 7b activation per AC-7.6-D); active count exactly at the K-target band.
- `app/marcus/orchestrator/gate_runner.py` is additive + stdlib-only (no new third-party deps).
- Marcus-duality assertion correctly enforced at `ProductionDispatchAdapter.build_specialist_state` (verified via `dispatch_adapter.py:14` import + `dispatch_adapter.py:81` call site `assert_payload_duality_boundary(payload)`).

### Layer 2 — Edge Case Hunter

PASS. All edge cases per Codex self-review independently sound:
- Calibration-tripwire records BOTH fire AND quiet events to JSONL (FM-5 inverse honored — silence not assumed healthy; quiet must be witnessed).
- Synthetic 3-axis disagreement injection fixture fires the tripwire + locks batch-approve for next 3 trials.
- Engagement-decay breach writes the report AND fires C1 calibration-tripwire through the same JSONL log.
- `silent_bypass_events: 0` invariant (FR-A23 from 7a.2) + max-3 `revise_count` invariant (FR-A21 from 7a.4) pinned across G1/G2C/G3/G4 in `tests/parity/test_nfr_cg_block_aggregated.py`.
- Production runner now auto-emits engagement-decay report on completed trial close (extends 7a.5's `_emit_run_summary_yaml` flow).

### Layer 3 — Acceptance Auditor

| AC | Verdict | Independent verification |
|---|---|---|
| A — 33-row parity-test suite mirrors mapping checklist | PASS | `tests/parity/test_operator_control_parity.py` carries `MAPPING_CHECKLIST_ROW` + `REFERENCES_FRS` per-row metadata; row-count CI assertion still 33 in `test_operator_control_parity_row_count.py` (SG-2 floor structurally enforced). |
| B — Composition Spec invariant test suite (7 §§) | PASS | `tests/parity/test_composition_spec_invariants.py` covers §3.1, §3.5, §3.6, §6, §9, §10, §11. SG-3 aggregated. |
| C — Calibration-tripwire substrate | PASS | `app/marcus/orchestrator/gate_runner.py` + `tests/integration/marcus/test_calibration_tripwire.py`. Synthetic disagreement + consensus paths both pinned. |
| D — Gate-bypass detection (FR-A23) | PASS | `silent_bypass_events == 0` invariant in run_summary.yaml; existing 7a.2 `GateBypassError` tests preserved. |
| E — Engagement-decay report (SM-4 threshold) | PASS | `tests/integration/marcus/test_engagement_decay_report.py`; auto-emit on trial close. |
| F — Max-3 oscillation invariant across all gates | PASS | NFR-CG aggregated suite verifies `revise_count <= 3` enforcement spans G1/G2C/G3/G4 (not just per-gate hand-rolling). |
| G — Marcus-duality boundary (FR-A24) | PASS | `dispatch_adapter.py:81` calls `assert_payload_duality_boundary`; `tests/integration/marcus/test_marcus_duality_boundary.py` pins runtime assertion. |
| H — NFR-CG block aggregated (11 cases) | PASS | `tests/parity/test_nfr_cg_block_aggregated.py` covers NFR-CG{1..11} structurally. |
| I — Trial-2 readiness predicate BS-2 (A-1..A-7) | **PARTIAL — OPERATOR-GATE-PENDING** | BS-2 requires operator trial-2 OR trial-2 dry-run ceremony; Codex prepared `7a-8-gate2-evidence-commands.ps1` runner; operator must execute + paste verbatim stdout. **This is the DUAL-GATE Gate-2 evidence ceremony — out of Codex's scope by design.** |
| J — D12 close protocol (sprint-status / bmm-workflow / next-session / deferred-inventory updates + retrospective convening) | DRAFTED | `slab-7a-retrospective.md` authored as draft per AC-7.8-J; sprint/bmm/next-session/deferred-inventory flips remain Claude T12-owned per Codex/Claude boundary. |
| K — Golden-trace fixtures from trial-2 | DRAFTED | If trial-2 hasn't run, file deferred-inventory entry `slab-7a-trial-2-golden-trace-fixtures-deferred-to-slab-7b` per Codex recommendation; Slab 7b inherits as input. |
| L — N-item / Composition Spec trace + Gate-2 ceremony | PREPARED | `7a-8-gate2-evidence-commands.ps1` is the operator-runnable evidence script; verbatim stdout pastes into Completion Notes once operator runs it. |

## Independent Verification Battery

```
.venv/Scripts/python.exe -m pytest tests/parity/test_operator_control_parity.py tests/parity/test_operator_control_parity_row_count.py tests/parity/test_composition_spec_invariants.py tests/parity/test_nfr_cg_block_aggregated.py tests/integration/marcus/test_calibration_tripwire.py tests/integration/marcus/test_engagement_decay_report.py tests/integration/marcus/test_marcus_duality_boundary.py
→ 44 passed, 18 skipped in 1.73s

.venv/Scripts/python.exe -m pytest tests/unit/manifest tests/integration/marcus tests/composition tests/parity tests/structural tests/unit/marcus tests/specialists/texas tests/specialists/_scaffold tests/cli tests/unit/models -q --tb=line --ignore=tests/integration/marcus/test_directive_confirm_or_edit_prompt.py
→ 696 passed, 19 skipped in 20.45s
   (+29 tests over post-7a.5-close baseline of 667)

.venv/Scripts/python.exe scripts/utilities/check_pipeline_manifest_lockstep.py
→ exit 0; trace at reports/dev-coherence/2026-04-29-0612/check-pipeline-manifest-lockstep.PASS.yaml

.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py <all 8 Slab 7a story files>
→ PASS — no sandbox-AC violations across 8 story file(s).

.venv/Scripts/python.exe -m ruff check app/marcus/orchestrator/gate_runner.py app/marcus/orchestrator/dispatch_adapter.py app/marcus/orchestrator/production_runner.py tests/parity tests/integration/marcus/test_calibration_tripwire.py tests/integration/marcus/test_engagement_decay_report.py tests/integration/marcus/test_marcus_duality_boundary.py
→ All checks passed!

.venv/Scripts/lint-imports.exe
→ Contracts: 9 kept, 0 broken.

.venv/Scripts/python.exe _bmad-output/implementation-artifacts/migration-7-1-directive-composer-composition-smoke.py
→ PASS slab-7a-opener composition smoke
   trial_id=...; directive_digest=25538298995c50c4...; texas_contribution_digest=eb5f35b9f5707c10...

.venv/Scripts/python.exe _bmad-output/implementation-artifacts/migration-7-7-a2-shims-composition-smoke.py
→ PASS slab-7a A2-shims composition smoke
   shim G1: exit 0; shim G2C: exit 0; shim G3: exit 0; shim G4: exit 0
```

## Composition Spec §11 Trigger Check

**Verdict:** no trigger fires.
- 7a.8 is purely additive: parity tests + Composition Spec invariant tests + NFR-CG aggregator + calibration-tripwire substrate + engagement-decay report + Marcus-duality assertion (additive call at adapter site).
- All 8 Slab 7a stories aggregate-clean against §11 triggers; no Option-B-to-C migration triggered. The Slab 7a "substrate completeness" thesis holds: Option B accommodated all 7 scope-binding commitments without escalation.

## Slab 7a Aggregate Verdict

**All 8 stories closed (or close-ready):**

| Story | Status | Codex/Claude split |
|---|---|---|
| 7a.1 directive-composer | done (2026-04-29) | Claude OLD CYCLE author + dev; Codex review (HALT-AND-REMEDIATE → 6 PATCH); Claude P1-P6 remediation |
| 7a.2 manifest fold-flags + compiler ext | done (2026-04-29) | NEW CYCLE: Claude spec; Codex dev; Claude review PASS-WITH-PATCH (P1+P2) |
| 7a.6 vocabulary registry + parity-table | done (2026-04-29) | NEW CYCLE: Claude spec (SG-2 amendment 34→33 mid-flight); Codex dev; Claude review PASS |
| 7a.3 pre-gate-marcus shared LLM node | done (2026-04-29) | NEW CYCLE: Claude spec; Codex dev; Claude review PASS |
| 7a.4 per-slide subgraph + HTML review-pack | done (2026-04-29) | NEW CYCLE: Claude spec; Codex dev; Claude review PASS-WITH-PATCH (P1 golden fixtures) |
| 7a.7 A2 single-decision shims | done (2026-04-29) | Claude direct (operator instruction; Codex on 7a.5) |
| 7a.5 conversation persistence + summary writer | done (2026-04-29) | NEW CYCLE: Claude spec; Codex dev (M3 facade-module fix); Claude review PASS |
| 7a.8 integration + closeout | review (PARTIAL — operator BS-2 ceremony pending) | NEW CYCLE: Claude spec; Codex dev; Claude review PASS-WITH-OPERATOR-GATE-PENDING |

**SG-1 (11-roster), SG-2 (33-row), SG-3 (Composition Spec invariants) all structurally enforced.** Trial-2 substrate readiness UNBLOCKED — operator can launch trial-2 against the Slab 7a substrate without further substrate code changes. The remaining row-content gaps are explicitly Slab 7b specialist activation territory.

## Close Action

**Two paths:**

1. **Close 7a.8 NOW pending operator BS-2 ceremony**: Claude flips spec status `review` → `done` based on automated PASS verdict + Codex's prepared Gate-2 evidence runner; operator runs `7a-8-gate2-evidence-commands.ps1` + trial-2 dry-run later as a separate post-close confirmation. Risk: AC-7.8-I is recorded as PARTIAL until operator confirms.

2. **Hold 7a.8 at `review` until operator runs Gate-2 ceremony**: cleaner DUAL-GATE discipline; operator runs ceremony + pastes stdout; Claude flips done after evidence pasted. **Recommended path** per DUAL-GATE convention.

**Awaiting operator decision (path 1 or path 2)** before flipping done in sprint-status + executing AC-7.8-J closeout protocol (sprint-status update, bmm-workflow-status update, next-session-start-here update, deferred-inventory finalization, retrospective party-mode-style sign-off).

If path 1: file `slab-7a-trial-2-bs-2-readiness-confirmation-deferred-to-operator-trial-2-ceremony` in deferred-inventory; close 7a.8 as done; reactivate the entry when operator runs ceremony.

If path 2: hold 7a.8 at `review` until operator pastes Gate-2 stdout into Completion Notes; Claude flips done immediately after.
