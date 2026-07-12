# F-E2E-1 fix — completion notes

**Date:** 2026-07-12
**Branch:** dev/hud-revival-2026-07-11 (working tree only — NOT committed)
**Defect source:** `_bmad-output/planning-artifacts/epic-35-story-35.7-party-performance-review-2026-07-11.md`

## The defect

The HUD's GATE-class next-action command emitted
`gate decide --trial-id ... --gate-id ... --verb approve --card-id ... --decision-card-digest ... --operator-id ...`.
Pasted from a fresh operator shell it failed `GateError: card_missing` because
`gate_cli.run_gate_decide -> resume_api.resume_from_verdict` reads an in-memory
`_CARD_STORE` that is empty cross-process AND never drives the walk. JTBD#1
(copy-paste-to-act) was broken for the most common pause class.

## The fix (party-adopted approach from Amelia)

1. **Inline-verdict mode added to `trial resume`** (`app/marcus/cli/trial.py`).
   - `--verdict-file` is now OPTIONAL. New inline flags added to the `resume`
     subparser: `--gate-id`, `--verb` (choices approve/edit/reject/select),
     `--card-id`, `--decision-card-digest`, `--operator-id`, plus optional
     `--edit-payload` / `--reject-reason`.
   - `resume_trial_cli` validates the two sources are mutually exclusive and
     that exactly one is present (exit 2 with a clear stderr message otherwise);
     when inline flags are present it requires all five core flags.
   - New helper `_build_inline_verdict(args)` assembles the `OperatorVerdict`
     from the flags — minting `verdict_id` via `uuid4()` and `timestamp` via
     `datetime.now(UTC)`; `card_id` string is coerced to UUID by pydantic.
   - `resume_trial(...)` now accepts either `verdict_file` OR a pre-built
     `verdict` (exactly-one guard) and converges on the SAME proven
     `resume_production_trial` disk-rehydration + walk-continuation path that
     `--verdict-file` already used. No new import of `app.gates.resume_api`
     (C3 contract stays intact — verified by lint-imports).

2. **`build_next_action` GATE branch flipped** (`app/marcus/cli/next_action.py`)
   from `gate decide ...` to `trial resume ...`. Error-class (`trial recover`)
   and batch-class (`trial resume-batch`) branches UNCHANGED. Digest still read
   from the OUTER card digest. Module docstring updated to explain the change.

3. **Round-trip test upgraded** (`tests/unit/marcus/cli/test_next_action.py`) —
   see "Test level" below.

## Exact command `build_next_action` now emits for a gate

```
trial resume --trial-id <trial_id> --gate-id <gate> --verb approve --card-id <card_id> --decision-card-digest <digest> --operator-id <op>
```

Live example (verified):
```
trial resume --trial-id 22b27500-6e67-4dd7-8308-fd89defe3d99 --gate-id G4A --verb approve --card-id 131e70a2-0000-4000-8000-000000000001 --decision-card-digest aaaa...(64 hex) --operator-id juanl
```

## Test level achieved

**Level: parse + verdict-construction (one below cross-process subprocess).**
The upgraded `test_paused_at_gate_command_round_trips`:
1. builds the gate command via `build_next_action`,
2. shlex-splits it and parses it through the REAL `trial resume` argparse
   grammar (`build_trial_parser`), asserting `trial_command == "resume"`,
   `verb == "approve"`, `verdict_file is None` (inline mode), etc.,
3. drives the parsed args through `_build_inline_verdict` and asserts a VALID
   `OperatorVerdict` results (trial_id / gate_id / verb / card_id / digest /
   operator_id all match) — proving the command is EXECUTABLE-shaped, not just
   parseable.

A true cross-process subprocess test was NOT added: driving it hermetically
requires a stubbed run directory + a fake `resume_production_trial` (the real
one spends live LLM calls and needs a real checkpoint), which is out of the
F-E2E-1 lane and would duplicate the assembler/runner-emission integration
coverage. The parse+verdict-build level directly exercises the exact failure
mode the old parse-acceptance-only test hid (a valid digest is now required, so
the test uses a 64-char lowercase-hex digest that actually satisfies the
`OperatorVerdict` invariant — the old `"abc123"` would not).

## Verification results

- `pytest tests/unit/marcus/cli tests/unit/marcus/orchestrator/test_operator_surface_assembler.py tests/unit/marcus/orchestrator/test_runner_projection_emission.py tests/contracts/test_30_1_zero_test_edits.py` → **140 passed**.
- `pytest tests/contracts/test_operator_surface_parity.py tests/hud` → **171 passed** (no next-action regressions).
- `ruff check` on all changed files → **All checks passed**.
- `lint-imports` → **18 kept, 0 broken** (C3 resume_api-bridge contract intact).
- `check_pipeline_manifest_lockstep.py` → **exit 0** (PASS trace written).

## Files changed

Production:
- `app/marcus/cli/next_action.py` — GATE branch flipped to `trial resume`; docstring.
- `app/marcus/cli/trial.py` — inline-verdict mode: `resume` subparser flags,
  `_build_inline_verdict`, `resume_trial_cli` source validation, `resume_trial`
  dual-source signature.
- `app/marcus/cli/__main__.py` — UNCHANGED (routing already dispatches
  `trial resume` -> `resume_trial_cli`; no new wiring needed).

Tests:
- `tests/unit/marcus/cli/test_next_action.py` — gate round-trip upgraded to
  parse-through-real-grammar + OperatorVerdict construction; `gate decide`
  assertions updated to `trial resume`; removed now-unused gate_cli import.
- `tests/unit/marcus/orchestrator/test_operator_surface_assembler.py` — gate
  next-action assertion updated `gate decide` -> `trial resume` (+`--verb approve`).
- `tests/unit/marcus/orchestrator/test_runner_projection_emission.py` — same
  gate-command-shape assertion updated (real regression from the flip).
- `tests/contracts/test_30_1_zero_test_edits.py` — added the two above CLI/
  orchestrator test files to `_ALLOWED_MODIFIED_PATHS_UNDER_TESTS` with an
  F-E2E-1 comment so the zero-test-edits guard stays green on commit.

## Deviations / notes

- **Beyond the stated ownership list, two extra test files were edited** because
  the command-shape flip is a real behavioral change they assert on:
  `test_operator_surface_assembler.py` (already allowlisted for 35.9) and
  `test_runner_projection_emission.py` (newly allowlisted). Leaving them would
  have left the suite red. Neither touches `production_runner.py` or
  `app/hud/**` source.
- **`__main__.py` needed no change** — the `trial resume` route already existed
  and simply calls `resume_trial_cli`, which now handles both sources.
- **Cosmetic follow-on (out of lane, NOT changed):**
  `tests/hud/_render_fixtures.py::GATE_CMD` is a hardcoded illustrative HUD
  render fixture that still contains an old-style `gate decide ...` example
  string. It is NOT produced by `build_next_action` (the render golden tests
  render whatever the constant holds, so they still pass). Refreshing it to the
  `trial resume` shape belongs to the HUD render lane (35.9) and would churn the
  render goldens; flagged here rather than edited to stay inside the F-E2E-1
  lane.
