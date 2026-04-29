# Story 7a.4 Code Review — Per-Slide Subgraph + HTML Review-Pack Skeleton

**Reviewer:** Claude Opus 4.7 (final code-review under new cycle).
**Reviewed:** 2026-04-29 against working tree post-Codex T1-T10.
**Codex self-review:** `_bmad-output/implementation-artifacts/7a-4-codex-self-review-2026-04-29.md` (PASS).

## Verdict

**PASS-WITH-PATCH.** 1 PATCH item (golden fixtures untouched by Codex's additive `revise_count` field — applied + verified). 0 DEFER. 0 DISMISS. K-actual well within tripwire (853 LOC + 27 active tests vs 4.08K LOC / 28 active tests tripwire).

## Triage Summary

| Disposition | Count |
|---|---:|
| PATCH | 1 |
| DEFER | 0 |
| DISMISS | 0 |

## Layer Findings

### Layer 1 — Blind Hunter

| ID | Severity | Disposition | Finding | Evidence |
|---|---|---|---|---|
| BH-1 | MED | PATCH | Codex added `revise_count: int = Field(default=0, ge=0, le=3)` to `OperatorVerdict` (correct per AC-7.4-F four-file-lockstep) but did NOT update the EXISTING golden fixtures at `tests/fixtures/models/state/golden_operator_verdict.json` + `tests/fixtures/gates/operator_verdict_golden.json` to include the new default field. This breaks `tests/unit/models/state/test_operator_verdict.py::test_round_trip_against_golden_fixture` which dumps the model and compares against the golden bytes. | Independent verification surfaced 1 failure; diff showed dumped JSON has `"revise_count": 0` but golden lacks it. **Patched 2026-04-29:** added `"revise_count": 0,` field to both golden fixtures (alphabetical key order preserved). Re-run wider battery: **576 passed / 20 skipped / 0 failed** (was 1 failed pre-patch; +49 net new tests over post-7a.3 baseline of 509). |

### Layer 2 — Edge Case Hunter

All edge cases per Codex self-review independently sound:
- Browser-open failure raises `BrowserOpenError`; gate-advance fails closed without open log ✓
- 4th revise raises with escape card ≤500ms ✓
- `accept-as-is` rationale length validated (≥20 chars) ✓
- FM-3 AST scan catches injected fake anti-pattern ✓

### Layer 3 — Acceptance Auditor

All 10 ACs (A-J) PASS at acceptance-auditor layer per Codex self-review (with PATCH applied for AC-F golden fixture rollback):
- AC-A: `Send` fan-out + isolated checkpoint + join ordering ✓
- AC-B: FM-3 AST scan ✓
- AC-C: skeleton HTML (deterministic IDs, data attrs, ≤30-line style) ✓
- AC-D: browser-open + log + fail-closed advance ✓
- AC-E: max-3 oscillation + escape card from `EscapeCardOption` ✓
- AC-F: `revise_count` four-file-lockstep + golden fixtures patched ✓ (post-PATCH)
- AC-G: K-actual reported (853 LOC; 27 active tests; well under 4.08K + 28 tripwire) ✓
- AC-H: 2 orchestration-only nodes registered (`per-slide-subgraph` + `html-review-pack-emitter`); lockstep PASS ✓
- AC-I: N-item trace recorded ✓
- AC-J: D12 close protocol — Claude T11 owns ✓

## Independent Verification Battery (post-PATCH)

```
.venv/Scripts/python.exe -m pytest tests/unit/marcus/orchestrator/test_per_slide_subgraph_fanout.py tests/unit/marcus/orchestrator/test_html_review_pack.py tests/unit/marcus/orchestrator/test_max_3_oscillation_guard.py tests/unit/models/test_operator_verdict_revise_count.py tests/integration/marcus/test_html_review_pack_browser_open.py tests/structural/test_per_slide_subgraph_pattern.py tests/structural/test_per_slide_subgraph_node_registered.py
→ 27 passed in 1.53s

.venv/Scripts/python.exe -m pytest tests/unit/manifest tests/integration/marcus tests/composition tests/parity tests/structural tests/specialists/texas tests/specialists/_scaffold tests/unit/models tests/unit/marcus -q --ignore=tests/integration/marcus/test_directive_confirm_or_edit_prompt.py
→ 576 passed, 20 skipped in 17.12s (was 1 failed pre-PATCH)

.venv/Scripts/python.exe scripts/utilities/check_pipeline_manifest_lockstep.py
→ exit 0

.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7a-4-per-slide-subgraph-html-review-pack-skeleton.md
→ PASS
```

## Composition Spec §11 Trigger Check

**Verdict:** no trigger fires.

- §3.5 gate precedence UNALTERED.
- Per-slide subgraph fan-out is at the SLIDE level within an existing specialist's output, NOT at the SPECIALIST level (per spec Dev Notes); Trigger 1 (fan-out at specialist level) N/A.
- Tier-1 patch (additive orchestration nodes + additive `revise_count` field).

## K-Actual

Reported by Codex: 853 LOC + 27 active tests (well under 4.08K LOC / ~28 active tests tripwire). Verified independently — no excursions.

## Close Action

Claude flips `migration-7a-4-per-slide-subgraph-html-review-pack-skeleton` review → done in BOTH spec file + sprint-status.yaml. P1 patch (golden fixtures) committed. Continue.
