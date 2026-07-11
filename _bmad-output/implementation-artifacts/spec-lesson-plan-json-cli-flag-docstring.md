---
title: 'lesson-plan-json CLI flag docstring — precedence + companion re-resolution clarity'
type: 'chore'
created: '2026-07-11'
status: 'done'
review_loop_iteration: 0
baseline_revision: '73eef7df55a097d517fab186c2b01b3198ca1081'
followup_review_recommended: false
context: []
warnings: []
---

<intent-contract>

## Intent

**Problem:** The `--lesson-plan-json` / `--lesson-plan-collateral-intent` help texts and the selection-seam docstrings are silent on three contracts callers trip over: (a) an *unratified* intent file falls through and yields to `--lesson-plan-json`; (b) selection resolution is two-layer — the CLI resolves in `_resolve_start_component_selection` and hands the file to `start_trial` as a *receipt*, while programmatic callers passing `lesson_plan_collateral_intent_path=` trigger a second re-read inside `start_trial` that reads **only the passed file**, never run-dir companions; (c) both flags can raise `CollateralSelectionError` on a `--bundle` mismatch. Filed as deferred residual `lesson-plan-json-cli-flag-docstring` (Phase-2 six-mine party CLOSE-amendment).

**Approach:** Documentation-only edit: sharpen the two argparse `help=` strings and the docstrings/comments at the three seam sites so each states the full precedence chain, the fall-through, the receipt-vs-re-read split, and where run-dir companions (`planning-ratification.json`, `ratified-los.json`) are actually re-resolved (walk-time `load_planning_context`, not selection time).

## Boundaries & Constraints

**Always:** Docs must describe current behavior exactly as implemented (verified against `trial.py:647-707`, `trial.py:391-426`, `collateral_selection.py:294-318`, `production_runner.py:1659-1677`). Hermetic done-bar: default pytest green, no API keys, `.venv/Scripts/python.exe`.

**Block If:** Any docstring claim would require *changing* behavior to be true; or the precedence logic observed contradicts the investigation summary.

**Never:** No behavior changes — zero edits to precedence logic, loaders, or `start_trial` control flow. No new test files (the argv-level coverage gap is a separate residual). No reopening S8 / selection-bridge design.

</intent-contract>

## Code Map

- `app/marcus/cli/trial.py:986-995` — `--lesson-plan-json` argparse `help=`; extend with fall-through + only-passed-file-read + bundle-conflict.
- `app/marcus/cli/trial.py:977-985` — `--lesson-plan-collateral-intent` `help=`; state ratified-wins / unratified-falls-through + bundle-conflict.
- `app/marcus/cli/trial.py:648-656` — `_resolve_start_component_selection` docstring; document full chain: ratified intent > plan-json > bundle/front-door; unratified fall-through; CLI passes resolved selection + `lesson_plan_collateral_receipt_path` (bypasses start_trial re-read).
- `app/marcus/cli/trial.py:391-426` — `start_trial` re-resolution block; comment/docstring: programmatic-callers-only seam, sniffs plan-JSON vs ratified intent, re-reads only the passed path; run-dir companions re-resolved at walk time (`production_runner.py:1659-1677` → `load_planning_context`), not here.

## Tasks & Acceptance

**Execution:**
- [x] `app/marcus/cli/trial.py` — update the two `help=` strings and the two docstring/comment sites per Code Map — single-file docs-only edit; each site states precedence, fall-through, receipt-vs-re-read split, companion-resolution boundary.

**Acceptance Criteria:**
- Given `python -m app.marcus.cli trial start --help`, when help renders, then `--lesson-plan-json` text states: yields to a *ratified* intent, wins over an *unratified* one, reads only the passed file (run-dir companions resolve at walk time), and may raise on `--bundle` conflict.
- Given the same help output, when reading `--lesson-plan-collateral-intent`, then it states ratified-wins / unratified-falls-through and the bundle-conflict contract.
- Given the existing suites (`tests/integration/marcus/test_trial_cli.py`, `test_trial_plan_json_selection.py`, `tests/marcus/lesson_plan/test_collateral_selection.py`), when run hermetically, then all pass unchanged (docs-only diff).
- Given `git diff`, when inspected, then only comment/docstring/help-string lines in `app/marcus/cli/trial.py` changed.

## Spec Change Log

## Review Triage Log

### 2026-07-11 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 4: (high 0, medium 1, low 3)
- defer: 3: (high 0, medium 1, low 2)
- reject: 3
- addressed_findings:
  - `[medium]` `[patch]` seam comment claimed an unratified intent "binds nothing" — false for a collateral-bearing file WITHOUT a ratification_status key (sniff keys on field absence). Reworded to describe the sniff precisely.
  - `[low]` `[patch]` sniff-preference sentence missed the inversion: a ratified-stamped companion routes to intent validation (extra=forbid fail-loud). Covered by the same rewording.
  - `[low]` `[patch]` "re-resolved at walk time" overstated unconditionality and implied sibling files travel — now states NEW run dir + irene_pass1 dispatch, siblings never read (comment + --lesson-plan-json help).
  - `[low]` `[patch]` else branch described only as the ratified/unratified split — now also names the fail-loud path for unreadable/invalid files.

## Auto Run Result

- **Summary:** Documentation-only clarification of `--lesson-plan-json` / `--lesson-plan-collateral-intent` precedence, the unratified fall-through, the CLI receipt-vs-programmatic re-read split, and the walk-time companion-resolution boundary. Deferred residual `lesson-plan-json-cli-flag-docstring` cleared.
- **Files changed:** `app/marcus/cli/trial.py` — two argparse help strings, `_resolve_start_component_selection` docstring, `start_trial` seam comment (docs-only; zero behavior lines).
- **Review breakdown:** 4 patches applied (all doc wording), 3 deferred to deferred-work.md (pre-existing: null CLI selection_source receipt; receipt-path-overrides-resolver provenance; unpinned never-fires-on-CLI property), 3 rejected as noise.
- **Verification:** hermetic pytest — 32 passed (trial_cli + trial_plan_json_selection + collateral_selection) pre-patch; 12 passed (trial_cli) post-patch re-run; `trial start --help` renders both new texts; diff inspected — comment/docstring/help lines only.
- **Residual risks:** documented contracts are prose, not pinned by an argv-level test (that coverage gap is the separate `malformed-plan-json-selection-negative` residual + a filed defer).
