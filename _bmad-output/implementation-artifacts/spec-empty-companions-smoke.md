---
title: 'empty-companions smoke — planning companions under a run dir never silently pass as framing'
type: 'feature'
created: '2026-07-11'
status: 'done'
review_loop_iteration: 0
baseline_revision: '54333b46814a218ba92b828ebf9ab6c026e818b9'
followup_review_recommended: false
context: []
warnings: []
---

<intent-contract>

## Intent

**Problem:** The integrated path (run-dir companions → `load_planning_context` → production-runner irene_pass1 payload) has three distinct empty/missing behaviors, only one of which is test-pinned: absent files → `None` (pinned); **0-byte files → `PlanningContextError` (unpinned — only `{not-json` malformed is pinned); `{}`/no-usable-framing files → `None` silently by explicit design ("treat as absent", planning_context.py ~383-385) (unpinned at any level).** Nothing asserts the integrated path can't fabricate phantom framing from empty companions. Deferred residual `empty-companions-smoke` (Phase-2 six-mine CLOSE-amendment).

**Approach:** Test-only smoke pinning all three arms at both seams: unit (`load_planning_context`) and runner (`_runner_payload_for_specialist` irene_pass1 branch). "Does not silently succeed" is pinned as: 0-byte/malformed fail LOUD (`PlanningContextError` → `SpecialistDispatchError` tagged `irene_pass1.planning_context.malformed`), and `{}`-companions produce NO `planning_context` key in the payload (treat-as-absent — never partial/phantom framing). The design question "should empty-but-present warn instead of silently treating as absent?" is filed as a defer, not decided here.

## Boundaries & Constraints

**Always:** Hermetic; `.venv/Scripts/python.exe -m pytest`; extend the existing test files and their fixture conventions (`tests/marcus/lesson_plan/test_planning_context.py`, `tests/marcus/orchestrator/test_runner_planning_context_thread.py` — reuse its run-dir/tmp_path arrangement and the existing malformed→SpecialistDispatchError pattern at ~L125).

**Block If:** Any arm behaves differently than stated above (e.g. 0-byte does NOT raise, or `{}` produces a payload key) — that's a production-behavior discovery requiring human disposition.

**Never:** No production-code changes (planning_context.py, production_runner.py read-only). Do not decide the warn-on-empty design question — file it as a defer. No live walk (the runner-seam tests exercise `_runner_payload_for_specialist` directly per the existing file's pattern, not a full trial).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| 0-byte ratification | run dir with 0-byte planning-ratification.json | `PlanningContextError` (unit); `SpecialistDispatchError` tag `irene_pass1.planning_context.malformed` (runner) | fail loud, both seams |
| 0-byte ratified-los | ratification valid, ratified-los.json 0-byte | same as above | fail loud, both seams |
| `{}` both companions | both files contain `{}` | unit: returns `None` (treat-as-absent by design); runner: `planning_context` key ABSENT from irene payload | silent by design — pinned as no-phantom-framing |
| `{}` single companion | only planning-ratification.json exists, contains `{}` | same as `{}` both | same |
| Absent (control) | run dir with neither file | unit `None`; runner key absent (already pinned — reuse, do not duplicate) | n/a |

</intent-contract>

## Code Map

- `app/marcus/lesson_plan/planning_context.py:318-386 (load_planning_context; _read_json ~74-89; treat-as-absent ~383-385)` — read-only behavior anchors.
- `app/marcus/orchestrator/production_runner.py:1657-1677` — runner consume/wrap seam (read-only).
- `tests/marcus/lesson_plan/test_planning_context.py` — ADD unit pins: 0-byte ratification, 0-byte los, `{}` both, `{}` single.
- `tests/marcus/orchestrator/test_runner_planning_context_thread.py` — ADD runner pins: 0-byte → SpecialistDispatchError (model on existing malformed test ~L125), `{}` → payload key absent (model on existing absent test ~L97).

## Tasks & Acceptance

**Execution:**
- [x] `tests/marcus/lesson_plan/test_planning_context.py` — add 4 unit pins per matrix — closes the unit gap.
- [x] `tests/marcus/orchestrator/test_runner_planning_context_thread.py` — add 2 runner-seam pins — closes the integrated-path gap named by the residual.

**Acceptance Criteria:**
- Given the new tests, when run hermetically with the full two files, then all pass with zero regressions.
- Given `git diff`, when inspected, then only the two test files changed.
- Given the defer file, when read, then the warn-on-empty design question is filed with evidence.

## Spec Change Log

## Review Triage Log

### 2026-07-11 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 7: (high 0, medium 3, low 4)
- defer: 3: (medium 2, low 1)
- reject: 3
- addressed_findings:
  - `[medium]` `[patch]` pin-6 disjunction had a dead arm and missed the never-leak-explicit-None invariant — now asserts `payload is None` exactly + new floor-present variant makes the dict arm live.
  - `[medium]` `[patch]` runner-seam pins hard-coded the underscore alias despite the file's F1 hyphen/underscore lesson — parametrized over both forms.
  - `[medium]` `[patch]` non-object neighbor arm ([]/null → "must be a JSON object") was wholly unpinned — added parametrized pin.
  - `[low]` `[patch]` 0-byte pins didn't pin WHICH companion failed — file-label match anchors added (sibling convention).
  - `[low]` `[patch]` runner 0-byte coverage asymmetric — parametrized over which companion is 0-byte.
  - `[low]` `[patch]` third treat-as-absent combination (ratified-los alone {}) unpinned — added.
  - `[low]` `[patch]` docstrings mis-cited the defer location and hardcoded line numbers — corrected to deferred-work.md + semantic anchor.

## Auto Run Result

- **Summary:** Deferred residual `empty-companions-smoke` cleared: 14 pins (parametrized) across unit + runner seams — 0-byte/malformed/non-object companions fail LOUD end-to-end (SpecialistDispatchError tag, both alias forms), {}-companions pin the designed treat-as-absent (no phantom framing, floor-only payload variant), warn-on-empty design question filed for operator disposition.
- **Files changed:** tests/marcus/lesson_plan/test_planning_context.py (+70), tests/marcus/orchestrator/test_runner_planning_context_thread.py (+144). Test-only.
- **Review breakdown:** 7 patches applied; 4 defers filed (warn-on-empty design question + 3 product findings: BOM rejection of healthy files, non-string coercion fabricating phantom framing, silent framing drop on nonexistent run dir); 3 rejected (style/idiom duplication).
- **Verification:** 27 passed hermetically (13→16 unit, 6→11 runner); adversarial mutation hunts on the pins came back clean (pins real, not vacuous).
- **Residual risks:** the three deferred product findings are genuine hardening candidates in the phantom-framing class — they need human-gated production changes.
