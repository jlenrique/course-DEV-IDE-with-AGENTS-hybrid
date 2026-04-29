# Story 7a.4 Codex G6 Self-Review — 2026-04-29

## Summary

Verdict: PASS.

Codex implemented T1-T10 for Story 7a.4: per-slide subgraph fan-out, FM-3 AST guard, skeleton HTML review pack, browser-open logging/refusal, max-3 oscillation escape card, `OperatorVerdict.revise_count` lockstep artifacts, and manifest registration for the two orchestration-only nodes.

## K-Actual

- Source + focused test/support LOC counted across 12 7a.4 files: 853 LOC.
- Active focused 7a.4 tests: 27 passed.
- K-target: ~3.5K LOC and ~28 active tests.
- Tripwire: >4.08K LOC or materially above ~28 active tests.
- Result: PASS. The implementation is well under LOC tripwire and at 27 active tests.

## Blind Hunter

No blocking findings. The parent fan-out helper emits LangGraph `Send` objects only; the only `interrupt()` call lives inside the per-slide subgraph node, not inside a parent per-slide loop. The FM-3 structural test includes an injected fake anti-pattern and catches it.

## Edge Case Hunter

No blocking findings. Browser-open failure raises `BrowserOpenError`; gate advance fails closed without the open log. The fourth revise path surfaces an escape card immediately and validates `accept-as-is` rationale length before writing acceptance.

Residual note: the HTML pack is intentionally skeleton-only. It persists textarea/radio values through sessionStorage but does not implement a full operator UI workflow; that is the explicit K-contract boundary.

## Acceptance Auditor

All 10 ACs are covered:

- AC-A: fan-out via `Send`, isolated checkpoint namespace, join ordering tests.
- AC-B: FM-3 AST scan over module/importers plus fake anti-pattern.
- AC-C: deterministic skeleton HTML rows, hidden fields, digest, data attributes, style/JS bounds.
- AC-D: browser open hook, open log, fail-closed gate advance.
- AC-E: max-3 revise guard and escape-card options from `EscapeCardOption`.
- AC-F: `OperatorVerdict.revise_count` model/schema/golden/shape-pin lockstep.
- AC-G: K-contract reported here and in T9 notes.
- AC-H: `per-slide-subgraph` and `html-review-pack-emitter` manifest nodes registered as orchestration-only.
- AC-I: N-item trace recorded in story completion notes.
- AC-J: D12 close evidence recorded; Composition Spec Section 11 trigger did not fire.

## Verification

```text
.venv\Scripts\python.exe -m pytest tests/unit/marcus/orchestrator/test_per_slide_subgraph_fanout.py tests/unit/marcus/orchestrator/test_html_review_pack.py tests/unit/marcus/orchestrator/test_max_3_oscillation_guard.py tests/unit/models/test_operator_verdict_revise_count.py tests/integration/marcus/test_html_review_pack_browser_open.py tests/structural/test_per_slide_subgraph_pattern.py tests/structural/test_per_slide_subgraph_node_registered.py -q --tb=short
-> 27 passed

.venv\Scripts\python.exe -m pytest tests/unit/models/test_operator_verdict_revise_count.py tests/unit/models/state/test_schema_pin.py -q --tb=short
-> 14 passed

.venv\Scripts\python.exe -m pytest tests/unit/manifest tests/integration/marcus tests/composition tests/parity tests/structural tests/specialists/texas tests/specialists/_scaffold -q --tb=line
-> 287 passed, 20 skipped with temporary POSIX vi shim

.venv\Scripts\python.exe scripts\utilities\check_pipeline_manifest_lockstep.py
-> PASS

.venv\Scripts\python.exe scripts\utilities\validate_migration_story_sandbox_acs.py _bmad-output\implementation-artifacts\migration-7a-4-per-slide-subgraph-html-review-pack-skeleton.md
-> PASS

.venv\Scripts\python.exe -m ruff check app\marcus\orchestrator\per_slide_subgraph.py app\marcus\orchestrator\html_review_pack.py app\models\state\operator_verdict.py tests\unit\marcus\orchestrator tests\unit\models\test_operator_verdict_revise_count.py tests\integration\marcus\test_html_review_pack_browser_open.py tests\structural
-> All checks passed

.venv\Scripts\lint-imports.exe
-> Contracts: 9 kept, 0 broken
```

Unshimmed wider pytest has the known Windows environment failure in Story 7a.1's `test_resolve_editor_posix_fallback` because `vi` is not on PATH when the test monkeypatches `sys.platform` to `linux`.
