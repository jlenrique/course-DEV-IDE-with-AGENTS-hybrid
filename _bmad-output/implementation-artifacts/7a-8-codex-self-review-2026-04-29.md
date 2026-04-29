# Story 7a.8 Codex Self-Review - 2026-04-29

**Story:** `migration-7a-8-integration-parity-test-suite-slab-7a-closeout`  
**Review mode:** G6 self-review (Blind / Edge / Auditor)  
**Verdict:** PASS-WITH-OPERATOR-GATE-PENDING

## Blind Review

- No specialist bodies were modified.
- The existing 7a.6 parity suite remains canonical; no parallel 33-file suite was introduced.
- Active-test count is exactly 44 excluding skipped placeholders, at but not above the 7a.8 tripwire.
- `gate_runner.py` is additive and stdlib-only; no ruamel or new dependency introduced.
- Marcus-duality assertion is enforced in `ProductionDispatchAdapter.build_specialist_state`.

## Edge Review

- Calibration tripwire records both fire and quiet events to JSONL; quiet is explicit, not inferred.
- Synthetic disagreement at three axes fires and locks batch approval for three trials.
- Engagement-decay breach writes the report and fires C1 through the same tripwire log.
- `silent_bypass_events: 0` and max-3 `revise_count` are pinned across active terminal gates.
- The production runner now auto-emits the engagement-decay report on completed trial close.

## Acceptance Audit

| AC | Status | Evidence |
|---|---|---|
| AC-A | PASS | `tests/parity/test_operator_control_parity.py` + row metadata check |
| AC-B | PASS | `tests/parity/test_composition_spec_invariants.py` |
| AC-C | PASS | `app/marcus/orchestrator/gate_runner.py` + calibration tests |
| AC-D | PASS | run summary invariant in `test_marcus_duality_boundary.py`; existing GateBypassError tests preserved |
| AC-E | PASS | engagement report generator + tests |
| AC-F | PASS | max-3 invariant across `{G1,G2C,G3,G4}` |
| AC-G | PASS | adapter-level Marcus-duality assertion + tests |
| AC-H | PASS | `tests/parity/test_nfr_cg_block_aggregated.py` |
| AC-I | PARTIAL-OPERATOR | BS-2 requires operator trial-2 or dry-run ceremony |
| AC-J | DRAFTED | `slab-7a-retrospective.md`; sprint/status/deferred close flips remain Claude T12-owned |
| AC-K | DRAFTED | recommend exact deferred key `slab-7a-trial-2-golden-trace-fixtures-deferred-to-slab-7b` if trial-2 has not run |
| AC-L | PREPARED | `7a-8-gate2-evidence-commands.ps1` prepared; operator stdout paste pending |

## Verification Run By Codex

```text
.venv/Scripts/python.exe -m pytest tests/parity/test_operator_control_parity.py tests/parity/test_operator_control_parity_row_count.py tests/parity/test_composition_spec_invariants.py tests/parity/test_nfr_cg_block_aggregated.py tests/integration/marcus/test_calibration_tripwire.py tests/integration/marcus/test_engagement_decay_report.py tests/integration/marcus/test_marcus_duality_boundary.py -q --tb=short
-> 44 passed, 18 skipped in 1.79s

.venv/Scripts/python.exe -m ruff check app/marcus/orchestrator/gate_runner.py app/marcus/orchestrator/dispatch_adapter.py app/marcus/orchestrator/production_runner.py tests/parity tests/integration/marcus/test_calibration_tripwire.py tests/integration/marcus/test_engagement_decay_report.py tests/integration/marcus/test_marcus_duality_boundary.py
-> All checks passed

.venv/Scripts/python.exe -m pytest tests/unit/manifest tests/integration/marcus tests/composition tests/parity tests/structural tests/unit/marcus tests/specialists/texas tests/specialists/_scaffold tests/cli tests/unit/models -q --tb=line
-> 711 passed, 19 skipped, 1 failed
-> Failure: tests/integration/marcus/test_directive_confirm_or_edit_prompt.py::test_resolve_editor_posix_fallback expects `vi` on PATH. This is the known environment-sensitive 7a.1 test documented in prior 7a reviews, not introduced by 7a.8.

.venv/Scripts/python.exe -m pytest tests/unit/manifest tests/integration/marcus tests/composition tests/parity tests/structural tests/unit/marcus tests/specialists/texas tests/specialists/_scaffold tests/cli tests/unit/models -q --tb=line --ignore=tests/integration/marcus/test_directive_confirm_or_edit_prompt.py
-> 696 passed, 19 skipped in 20.07s

.venv/Scripts/python.exe scripts/utilities/check_pipeline_manifest_lockstep.py
-> PASS; trace reports/dev-coherence/2026-04-29-0603/check-pipeline-manifest-lockstep.PASS.yaml

.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py <all 8 Slab 7a story files>
-> PASS — no sandbox-AC violations across 8 story file(s).

.venv/Scripts/lint-imports.exe
-> Contracts: 9 kept, 0 broken.

.venv/Scripts/python.exe _bmad-output/implementation-artifacts/migration-7-1-directive-composer-composition-smoke.py
-> PASS slab-7a-opener composition smoke

.venv/Scripts/python.exe _bmad-output/implementation-artifacts/migration-7-7-a2-shims-composition-smoke.py
-> PASS slab-7a A2-shims composition smoke
```

## Proposed Claude T12 Closeout Content

- Flip 7a.8 `review -> done` only after operator Gate-2 evidence is pasted.
- Update `sprint-status.yaml`, `bmm-workflow-status.yaml`, `next-session-start-here.md`, and `deferred-inventory.md` per AC-J.
- If trial-2 did not run, add or alias the exact deferred inventory key: `slab-7a-trial-2-golden-trace-fixtures-deferred-to-slab-7b`.
- Confirm BS-2 A-1..A-7, especially `silent_bypass_events: 0`, before closing Slab 7a.
