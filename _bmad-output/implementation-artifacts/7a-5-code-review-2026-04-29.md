# Story 7a.5 Code Review — Conversation Persistence + Specialist-Summary Writer

**Reviewer:** Claude Opus 4.7 (final code-review under new cycle).
**Reviewed:** 2026-04-29 against working tree post-Codex T1-T10.
**Codex self-review:** `_bmad-output/implementation-artifacts/7a-5-codex-self-review-2026-04-29.md` (PASS).

## Verdict

**PASS.** 0 PATCH / 0 DEFER / 0 DISMISS. Story ready to flip done.

## Layer Findings

### Layer 1 — Blind Hunter

PASS. Independent verification: tamper-evident chain anchored at directive.yaml; SHA256 chain via `compute_output_digest` patterns mirroring Slab 6.0 substrate; `SpecialistContribution.output_digest` invariant unchanged; specialist `_act` bodies untouched (only `_emit_spans` hooks modified per AC-7.5-F constraint).

**Notable Codex remediation during dev:** Initial implementation had `app.specialists.{tracy,vera,wanda,...}.graph -> app.marcus.orchestrator.specialist_summary_writer` violating M3 import contract (specialists must not import marcus.orchestrator). Codex resolved by moving the implementation to `app.models.state.specialist_summary_artifacts` (acceptable import direction: specialists → models) AND keeping `app.marcus.orchestrator.specialist_summary_writer` as the orchestrator-facing facade. Elegant fix; both contract directions preserved.

### Layer 2 — Edge Case Hunter

PASS. All edge cases per Codex self-review independently sound:
- `ConversationChainBrokenError` raised on tampered turn / missing prior_envelope_digest ✓
- Missing `_schema_version` defaults to "1.0" with warning log ✓
- 15-25 line summary envelope enforced as RAISE (not lint warning) ✓
- Deferred specialists (`dan`, `compositor`) emit no-op marker via same writer path ✓
- Path Z duplicate-skip preserves single turn JSON; chain integrity preserved ✓

### Layer 3 — Acceptance Auditor

All 10 ACs (A-J) PASS:

| AC | Verdict | Test pin |
|---|---|---|
| A — Conversation persistence module + structured-record format | PASS | `tests/unit/marcus/orchestrator/test_conversation_persistence.py` |
| B — SHA256 tamper-evident chain | PASS | `tests/unit/marcus/orchestrator/test_conversation_chain_integrity.py` |
| C — Specialist-summary writer module | PASS | `tests/unit/marcus/orchestrator/test_specialist_summary_writer.py` |
| D — 15-25 line envelope | PASS | `tests/unit/marcus/orchestrator/test_specialist_summary_length_envelope.py` |
| E — Gate-handler loads adjacent summary | PASS | `tests/integration/marcus/test_gate_handler_loads_adjacent_summary.py` |
| F — SpecialistState four-file-lockstep + 9-of-11 wiring | PASS | `tests/unit/models/test_specialist_state_shape_pin.py` + emit-node hooks in 9 specialist graph.py files |
| G — Path Z compatibility | PASS | `tests/integration/marcus/test_path_z_first_contribution_wins_with_persistence.py` |
| H — Trial-run capture envelope | PASS | `tests/integration/marcus/test_run_summary_yaml_emit.py` |
| I — Schema versioning | PASS | `tests/unit/marcus/orchestrator/test_conversation_persistence_schema_versioning.py` |
| J — N-item / D12 close | HANDOFF-TO-CLAUDE | Claude flips done. |

## Independent Verification Battery

```
.venv/Scripts/python.exe -m pytest tests/unit/marcus/orchestrator/test_conversation_persistence.py tests/unit/marcus/orchestrator/test_conversation_chain_integrity.py tests/unit/marcus/orchestrator/test_specialist_summary_writer.py tests/unit/marcus/orchestrator/test_specialist_summary_length_envelope.py tests/unit/marcus/orchestrator/test_conversation_persistence_schema_versioning.py tests/unit/models/test_specialist_state_shape_pin.py tests/integration/marcus/test_gate_handler_loads_adjacent_summary.py tests/integration/marcus/test_path_z_first_contribution_wins_with_persistence.py tests/integration/marcus/test_run_summary_yaml_emit.py
→ 32 passed in 1.55s

.venv/Scripts/python.exe -m pytest tests/unit/manifest tests/integration/marcus tests/composition tests/parity tests/structural tests/specialists/texas tests/specialists/_scaffold tests/unit/models tests/unit/marcus tests/cli -q --ignore=tests/integration/marcus/test_directive_confirm_or_edit_prompt.py
→ 667 passed, 20 skipped in 18.47s

.venv/Scripts/python.exe scripts/utilities/check_pipeline_manifest_lockstep.py
→ exit 0

.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7a-5-conversation-persistence-specialist-summary-writer.md
→ PASS

.venv/Scripts/lint-imports.exe
→ Contracts: 9 kept, 0 broken

(ruff clean per Codex T9; verified focused targets independently)
```

## Composition Spec §11 Trigger Check

**Verdict:** no trigger fires.

- §3.1 envelope append-only + SHA256 invariants HONORED (FR-A11-A14).
- §11 trigger NEGATIVE (additive persistence files; no envelope shape change; no adapter contract change; no specialist `_act` body touched — only `_emit_spans` hooks).
- ADR-D3 Postgres checkpointer evolution: 7a.5 designed file format Postgres-compatible (additive-only schema; `_schema_version` field) but did NOT migrate runtime to Postgres (post-Slab-7a per ADR-D3).

## Close Action

Claude flips `migration-7a-5-conversation-persistence-specialist-summary-writer` review → done in BOTH spec file + sprint-status.yaml. **Wave 5 (7a.8 dual-gate strict-last) NOW UNBLOCKED — all 7 prior Slab 7a stories closed.** Commit + continue.
