# Story 7a.3 Code Review — Pre-Gate-Marcus Shared LLM Node

**Reviewer:** Claude Opus 4.7 (final code-review under new cycle).
**Reviewed:** 2026-04-29 against working tree post-Codex T1-T10.
**Codex self-review:** `_bmad-output/implementation-artifacts/7a-3-codex-self-review-2026-04-29.md` (PASS-WITH-NOTE).

## Verdict

**PASS.** 0 PATCH items. 1 NOTE (defensive guard against fake OpenAI keys triggering live LLM calls in tests; correct behavior). Story ready to flip done.

## Triage Summary

| Disposition | Count |
|---|---:|
| PATCH | 0 |
| DEFER | 0 |
| DISMISS | 0 |
| NOTE (acceptable Codex addition) | 1 |

## Layer Findings

### Layer 1 — Blind Hunter

| ID | Severity | Disposition | Finding | Evidence |
|---|---|---|---|---|
| BH-1 | NOTE | ACCEPTABLE | Codex added `_should_invoke_pre_gate_marcus` guard that suppresses pre-gate LLM call for `sk-test*` / `sk-fake*` API keys + `allow_offline_cost_report=True` runs. | `app/marcus/orchestrator/production_runner.py:556-563`. Necessary defense — without it, every existing test using placeholder API keys would attempt a live `make_chat_model("marcus")` call. The guard is conservative (only skips when offline OR clearly-fake key) and the actual production path with a real `sk-*` key still invokes pre-gate-marcus. Codex documented in self-review. |

### Layer 2 — Edge Case Hunter

All edge cases per Codex self-review independently sound:
- StrictUndefined Jinja2 templates fail loud on missing slots ✓
- Missing template raises FileNotFoundError ✓
- Rationale <20 chars raises ValueError (NFR-OX3 floor) ✓
- Confidence outside [0,1] raises at parse time ✓
- No-pre-fill path preserves existing decision-card shape (backward compat) ✓
- 7a.6 vocabulary closure test now active (registry exists) ✓

### Layer 3 — Acceptance Auditor

All 9 ACs (A-I) PASS at acceptance-auditor layer per Codex self-review. Independently spot-verified:
- AC-A: lockstep trace records `directive-composer + pre-gate-marcus` orchestration-only nodes ✓
- AC-B: 17 focused tests pass ✓
- AC-C: 4 Jinja2 templates present at `docs/conversational-gates/g{1,2c,3,4}.j2` ✓
- AC-D: single-call-site + vocabulary-closure structural tests both active ✓
- AC-E: Composition Spec §3.5 unaltered (precedence rule unchanged) ✓
- AC-F: LangSmith trace test asserts exactly one pre-gate-marcus span per gate ✓
- AC-G: `_build_decision_card` accepts `pre_fill: PreFillProposal | None` kwarg; persisted in decision-card JSON ✓

## Independent Verification Battery

```
.venv/Scripts/python.exe -m pytest tests/unit/marcus/orchestrator/test_pre_gate_marcus.py tests/structural/test_pre_gate_marcus_*.py tests/composition/test_pre_gate_marcus_*.py tests/integration/marcus/test_pre_gate_marcus_*.py tests/integration/marcus/test_runner_threads_pre_fill_to_decision_card.py
→ 17 passed in 1.51s

.venv/Scripts/python.exe -m pytest tests/unit/manifest tests/integration/marcus tests/composition tests/parity tests/structural tests/specialists/texas tests/specialists/_scaffold tests/unit/models -q --tb=line --ignore=tests/integration/marcus/test_directive_confirm_or_edit_prompt.py
→ 509 passed, 20 skipped in 16.01s

.venv/Scripts/python.exe scripts/utilities/check_pipeline_manifest_lockstep.py
→ exit 0; trace records orchestration_only_nodes: [directive-composer, pre-gate-marcus]

.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7a-3-pre-gate-marcus-shared-llm-node.md
→ PASS
```

## Composition Spec §11 Trigger Check

**Verdict:** no trigger fires.

- §3.5 gate precedence UNALTERED (per AC-E; pre-fill only changes decision-card draft content; per-specialist gates remain non-blocking).
- Additive orchestration node + additive `pre_fill` kwarg on `_build_decision_card`.
- No §10 Decision Log entry needed (Tier-1 patch).

## Close Action

Claude flips `migration-7a-3-pre-gate-marcus-shared-llm-node` review → done in BOTH spec file + sprint-status.yaml. No remediation cycle needed. Commit + continue.
