# Story 7a.2 Codex Self-Review — 2026-04-29

## Verdict

PASS-WITH-NOTE for Codex development scope. All 7a.2-focused checks pass. The unmodified broad Marcus slice still has one unrelated 7a.1 editor fallback failure when no `vi` binary is on PATH; with a temporary PATH shim for `vi`, the full requested pytest battery passes.

## Blind Hunter

- PATCH applied — `production_gate_ids(manifest)` derives active pause points from live manifest metadata and the retired `PRODUCTION_GATE_IDS` symbol is gone from compiler exports and runner imports.
- PATCH applied — resume-mode originally skipped later active gates after a verdict; `resume_production_trial` now raises `GateBypassError` on later active gate bypass unless the checkpoint was created for offline-cost-report mode.
- PATCH applied — existing tests that used live `pause_at_gates=False` as a convenience bypass were moved to gate-free fixture manifests or offline-cost-report mode, so they no longer depend on silent active-gate skipping.
- DISMISS — PyYAML audit byte stability risk is bounded by deterministic timestamp, `sort_keys=False`, `allow_unicode=True`, `default_flow_style=False`, and `line_break="\n"`; structural sync test compares committed bytes.

## Edge Case Hunter

- `production_gate_ids`: covered empty manifest via `model_construct`, folded via `fold_with`, folded via `fold_target`, and live manifest active set.
- `NodeSpec` fold validator: covered neither field, each field independently, and mutual-exclusion rejection.
- Fold cycles and bad targets: emitter rejects unknown `fold_with`, self-folds, and cycles before writing audit output.
- Lockstep tolerance: only `specialist_id is None and gate is False and hud_tracked is False` is tolerated; a fake specialist node without HUD/pack entry still fails.
- Gate bypass: start-mode active gate bypass, folded-gate pass-through, offline-cost-report bypass, and resume-mode later-gate bypass are pinned.

## Acceptance Auditor

| AC | Status | Test Pins |
| --- | --- | --- |
| A | PASS | `tests/unit/manifest/test_node_spec_fold_fields.py` |
| B | PASS | `tests/unit/manifest/test_manifest_fold_with_declarations.py` |
| C | PASS | `tests/unit/manifest/test_production_gate_ids_derived.py`; `tests/unit/manifest/test_compiler.py` |
| D | PASS | `tests/unit/manifest/test_gate_fold_manifest_emit.py`; `tests/structural/test_gate_fold_manifest_in_sync.py` |
| E | PASS | `tests/integration/marcus/test_gate_bypass_refusal.py` |
| F | PASS | `tests/unit/manifest/test_gate_topology_cli.py`; manual CLI outputs captured in T9 |
| G | PASS | `tests/structural/test_lockstep_orchestration_only_tolerance.py`; `tests/structural/test_pipeline_manifest_directive_composer_node.py` |
| H | PASS | `tests/structural/test_pipeline_manifest_directive_composer_node.py`; lockstep PASS; schema/pack versions unchanged |
| I | PASS | This review records N-item trace below |
| J | HANDOFF | Sprint-status/deferred-inventory close remains Claude-owned per operator boundary |

## N-Item Trace

- N1 PASS — `app/manifest/gate_fold_manifest_emit.py` is additive and covered by unit + structural sync tests.
- N2 PASS — Composition Spec §3.6 dependencies preserved; §11 trigger check did not fire for this Tier-1 additive patch.
- N4 PASS — no specialist body files touched.
- N9 PASS-PENDING-OPERATOR — topology CLI outputs are available for operator UX validation.
- N10 PASS — audit emitter is CI-pinned; orchestration-only classification is structural.
- A9/A11/A12 honored — live tree paths verified, `Path` used at boundaries, no new manual sync step.

## Verification

- PASS: `pytest tests/unit/manifest ... tests/structural/test_gate_fold_manifest_in_sync.py` -> 79 passed.
- PASS with temporary `vi` PATH shim: full requested pytest battery -> 147 passed.
- NOTE: unshimmed broad Marcus slice -> 165 passed / 1 skipped / 1 failed, failing only `tests/integration/marcus/test_directive_confirm_or_edit_prompt.py::test_resolve_editor_posix_fallback` because the 7a.1 editor fallback now requires `vi` on PATH.
- PASS: `scripts/utilities/check_pipeline_manifest_lockstep.py`; trace records `orchestration_only_nodes: [directive-composer]`.
- PASS: sandbox-AC validator.
- PASS: ruff on requested 7a.2 surfaces plus modified adjacent tests.
- PASS: import-linter 9/9 contracts kept.
- PASS: `python -m app.manifest.gate_fold_manifest_emit`.
- PASS: `python -m app.manifest.gate_topology --unfolded`, `--folded`, and `--audit`.

## K-Actual

New test pins: 29 tests, below the ~34-test tripwire. New files total about 630 lines; modified LOC remains well below the ~3.4K tripwire.

## Handoff Notes

Claude review should pay special attention to the resume-mode `GateBypassError` behavior. It is intentionally strict: a later active gate after a verdict cannot be silently skipped unless the persisted checkpoint was created under offline-cost-report mode.
