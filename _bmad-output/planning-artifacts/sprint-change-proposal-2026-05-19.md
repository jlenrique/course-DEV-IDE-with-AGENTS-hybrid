# Sprint Change Proposal — TW-7c-4 Pre-Trial-3 Substrate Amendment

**Authored at:** 2026-05-19 (post-Slice-A + post-Slice-D revert; Path-1 housekeeping arc, post-Quinn R5 synthesis)
**Skill:** `bmad-correct-course` (Batch mode)
**Operator strategic approval:** GRANTED 2026-05-19 (option `dispatch_correct_course` selected from orchestrator decision-point)
**Branch:** `dev/langchain-langgraph-foundation` @ `f7cecd1` (working tree clean; origin synced)
**Scope classification:** **Moderate** (substrate amendment to tripwire allowlist + lockstep test edits; not a full PRD/epic restructure)

---

## Section 1: Issue Summary

**Problem statement.** During the pre-Trial-3 housekeeping arc executed in this session (operator-chosen Path 1, party-mode-gated each slice), the team discovered that **TW-7c-4 (the "no live-dispatch scope creep" tripwire authored at Slab 7c.21a close, 2026-05-07 commit `669e99f`)** is materially broader in scope than the team appreciated at Round-1 and Round-2 party-mode deliberation. Specifically:

- The tripwire (`tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py::test_live_dispatch_python_scope_is_bounded`) carries TWO assertions: line 56 (`app_scope == []` — forbids `app/`-layer Python touches) AND line 65 (`unexpected == []` — forbids ANY working-tree Python file change outside the 5-path `PERMITTED_PYTHON_DIFFS` allowlist).
- Round 2 party-mode reasoned about line 56 only. Slice D (`git rm tests/migration/test_slab_2c_next_session_start_here_updated.py`) fired line 65 despite being a pure `tests/` deletion.
- **Implication:** the pre-Trial-3 freeze is total for ALL Python file modifications, not just `app/`. Most catalogued post-S6 housekeeping items (`s6-tier-3-post-trial-3-housekeeping-batch`, 16 items aggregate) require Python edits and are structurally blocked.

**Evidence captured.**
- Slice A probe: 9-line path-pin update to `app/marcus/lesson_plan/coverage_manifest.py` resolved 12 broad-regression failures (88→78, −10 net) before reverting per Quinn's R5 synthesis. Diff preserved verbatim at `.tmp/slice-a-diff.patch` (9308 bytes; gitignored).
- Slice D probe: `git rm tests/migration/test_slab_2c_next_session_start_here_updated.py` fired TW-7c-4 line 65 by design (deletion `unexpected` path); broad regression dropped 88→87 transiently before revert.
- Probe-capture entries filed in `_bmad-output/planning-artifacts/deferred-inventory.md §Post-S6 Housekeeping Probe — Slice A` (commits `4698ce5` + `f7cecd1`; both pushed).
- Pre-drafted dispatch motion preserved at `.tmp/slice-a-post-trial-3-correct-course-draft.md` (gitignored; superseded by this formal Sprint Change Proposal).

**Trigger category (per checklist 1.2):** Technical limitation discovered during implementation. The freeze was authored at S6 close to lock substrate for Trial-3's forensic-comparison protocol; the breadth of "Python edit" scope was not surfaced to the team that ratified the freeze. This is a calibration issue, not a strategic pivot.

---

## Section 2: Impact Analysis (per checklist §2 + §3)

**Epic impact (checklist §2):** None. This proposal does not modify Epic scope, sequencing, or acceptance criteria. Slab 7c is closed; `s6-tier-3-post-trial-3-housekeeping-batch` remains an active deferred-inventory cluster whose reactivation triggers are unchanged.

**PRD impact (checklist §3.1):** None. No core PRD goals are touched.

**Architecture impact (checklist §3.2):** **Yes, narrowly scoped.**
- `tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py::PERMITTED_PYTHON_DIFFS` (line 13-18) needs allowlist extension.
- `tests/contracts/test_30_1_zero_test_edits.py::_ALLOWED_MODIFIED_PATHS_UNDER_TESTS` (line 52-59) needs allowlist extension to authorize the lockstep test-side path-pin fix.
- `_bmad-output/implementation-artifacts/broad-regression-baseline-2026-05-07.md` Summary needs catalog refresh post-amendment.
- No `state/config/pipeline-manifest.yaml::block_mode_trigger_paths` changes. No M5 import-linter contract semantics changes. (Per Winston's Round-1 binding tripwire — confirmed.)

**UI/UX impact (checklist §3.3):** N/A.

**Other artifacts (checklist §3.4):**
- Deferred-inventory entry `s6-housekeeping-coverage-manifest-path-pin-probe` will be CLOSED with strikethrough + `CLOSED-AT-<commit>` marker after this amendment lands.
- `next-session-start-here.md` does NOT need pre-amendment edits (it's gitignored hybrid-local; refreshed at session-WRAPUP).
- The `bmad-sprint-governance.mdc` and `CLAUDE.md` will be updated at WRAPUP to fold the new impasse-resolution chain governance (Dr. Quinn → John tiebreaker; orthogonal to this proposal but ratified the same session).

**Trial-3 launch impact:** This is the critical concern.
- **Forensic catalog impact:** `broad-regression-baseline-2026-05-07.md` is the reference operator greps during Trial-3 review to distinguish pre-existing noise from new regressions. Amending the substrate now changes the substrate the catalog references. **Mitigation:** refresh the catalog Summary post-amendment AND annotate the catalog's measurement_run section with the amendment commit reference. The forensic-comparison protocol then has two valid baselines (pre-amendment 88 + post-amendment ~76); Trial-3 review compares against post-amendment.
- **Freeze rationale impact:** the freeze was authored to prevent substrate destabilization pre-Trial-3. The amendment is a bounded, evidence-backed extension to the allowlist — NOT a relaxation of the freeze predicate. The freeze remains in effect for all OTHER Python paths.
- **Trial-3 launch readiness impact:** none. AM-11 launch-permission token (`tests/trial/test_trial3_readiness.py + tests/test_preflight_check.py + tests/marcus_capabilities/test_preflight_receipt_contract.py`) is independent of the amended paths. 30-1 contract suite (17/17) is independent. M5 import-linter (13 contracts) is independent.

---

## Section 3: Recommended Approach (per checklist §4)

**Selected path:** **Hybrid (Option 1 + bounded substrate amendment).** Direct adjustment via story-equivalent commit, scoped tightly to the path-pin fix surface, with explicit allowlist amendments justified by the probe evidence.

**Rationale:**
- **Option 1 (Direct Adjustment) alone:** insufficient — the housekeeping work requires Python edits that the freeze blocks. Cannot land mechanical fixes without substrate amendment.
- **Option 2 (Rollback):** N/A. No completed work to roll back.
- **Option 3 (PRD MVP Review):** N/A. PRD scope unchanged; no MVP reduction needed.

**Effort estimate:** Low (~30 min total: 2-file substrate amendment + Slice A re-application + Slice D re-application + test-side path-pin lockstep + catalog refresh + 2-3 commits + 1-2 pushes).
**Risk level:** Low-Medium. The bounded amendment is justified by the probe evidence; the freeze predicate is preserved; the catalog refresh path is well-understood. Risk concentrated in the catalog-refresh step (must be lockstep with the amendment commit or operator's Trial-3 forensic-comparison protocol degrades).

**Trade-off accepted:** the pre-Trial-3 freeze is selectively weakened on 1-2 explicitly named paths. The broader freeze (predicate-level `app_scope == []` and `unexpected == []`) remains in effect for all other paths. Post-Trial-3, the allowlist returns to its current 5-path form (or operator decides to leave the amendment in place permanently).

---

## Section 4: Detailed Change Proposals

### 4.1 — TW-7c-4 allowlist amendment

**File:** `tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py`

**OLD (lines 9-18):**
```python
HARNESS_PATHS = {
    "scripts/utilities/run_cache_hit_harness.py",
    "scripts/utilities/run_5_api_smoke.py",
}
PERMITTED_PYTHON_DIFFS = {
    *HARNESS_PATHS,
    "scripts/utilities/detect_tw_7c_4_live_dispatch_scope_creep.py",
    "tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py",
    "tests/trial/test_trial3_readiness.py",
}
```

**NEW:**
```python
HARNESS_PATHS = {
    "scripts/utilities/run_cache_hit_harness.py",
    "scripts/utilities/run_5_api_smoke.py",
}
PERMITTED_PYTHON_DIFFS = {
    *HARNESS_PATHS,
    "scripts/utilities/detect_tw_7c_4_live_dispatch_scope_creep.py",
    "tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py",
    "tests/trial/test_trial3_readiness.py",
    # Pre-Trial-3 substrate amendment 2026-05-19 (sprint-change-proposal-2026-05-19.md):
    # post-S2 namespace-collapse lockstep fixes ratified via party-mode after
    # Quinn R5 "Probe-Capture" synthesis surfaced TW-7c-4's broader-than-appreciated
    # scope (line 65 `unexpected == []` predicate). Bounded allowlist extension;
    # freeze predicate intact for all other paths. Post-Trial-3: revisit whether
    # this list reverts to original or stays extended.
    "app/marcus/lesson_plan/coverage_manifest.py",
    "tests/test_coverage_manifest_regenerates_on_current_state.py",
    "tests/migration/test_slab_2c_next_session_start_here_updated.py",
}
```

**Rationale.** Three paths added:
- `app/marcus/lesson_plan/coverage_manifest.py` — Slice A scope (9-line path-pin update; lockstep with already-correct JSON manifest)
- `tests/test_coverage_manifest_regenerates_on_current_state.py` — Slice A lockstep test-pin update (line 51 `assert entry.module_path == "marcus/lesson_plan/quinn_r_gate.py"` → `app/marcus/...`)
- `tests/migration/test_slab_2c_next_session_start_here_updated.py` — Slice D scope (delete stale gitignored-file content-pin test)

### 4.2 — 30-1 guard allowlist amendment

**File:** `tests/contracts/test_30_1_zero_test_edits.py`

**OLD (lines 52-59):**
```python
_ALLOWED_MODIFIED_PATHS_UNDER_TESTS: frozenset[str] = frozenset(
    {
        # 30-2a G6-D1 deferral + 30-2b AC-B.9: extend the side-effect
        # guard to cover the new marcus.intake.pre_packet and
        # marcus.orchestrator.dispatch modules that land at 30-2b.
        "tests/test_marcus_import_chain_side_effects.py",
    }
)
```

**NEW:**
```python
_ALLOWED_MODIFIED_PATHS_UNDER_TESTS: frozenset[str] = frozenset(
    {
        # 30-2a G6-D1 deferral + 30-2b AC-B.9: extend the side-effect
        # guard to cover the new marcus.intake.pre_packet and
        # marcus.orchestrator.dispatch modules that land at 30-2b.
        "tests/test_marcus_import_chain_side_effects.py",
        # Pre-Trial-3 substrate amendment 2026-05-19 (sprint-change-proposal-2026-05-19.md):
        # post-S2 namespace-collapse lockstep test-pin update authorized via
        # party-mode after Quinn R5 synthesis. Same arc as TW-7c-4 allowlist extension.
        "tests/test_coverage_manifest_regenerates_on_current_state.py",
    }
)
```

**Rationale.** The 30-1 zero-test-edit invariant was authored to isolate the 30-1 changeset's diff; it scopes to `tests/` and reports any test file change outside the allowlist. The post-S2 namespace-collapse lockstep work surfaces a stale test-side path pin that needs lockstep update. Adding the file to `_ALLOWED_MODIFIED_PATHS_UNDER_TESTS` is the canonical mechanism for authorizing such an edit per the guard's docstring.

### 4.3 — Slice A re-application (production code path-pin)

**File:** `app/marcus/lesson_plan/coverage_manifest.py`

**Diff:** preserved verbatim at `.tmp/slice-a-diff.patch` (9308 bytes). Lines 223, 238, 250, 262, 279, 295, 311, 328, 345 — replace `module_path="marcus/lesson_plan/<file>.py"` with `module_path="app/marcus/lesson_plan/<file>.py"` (9 entries).

**Rationale.** Lockstep alignment with the canonical JSON manifest at `_bmad-output/maps/coverage-manifest/lesson-plan-envelope-coverage-manifest.json` (which has already-correct `app/marcus/...` paths). Pure data update; no code-behavior change. Resolves `CoverageManifestError: Inventory drift` raised at `coverage_manifest.py:599` and cascades to ~10-18 broad-regression failures.

### 4.4 — Slice A lockstep test-pin update

**File:** `tests/test_coverage_manifest_regenerates_on_current_state.py`

**OLD (line 51):**
```python
assert entry.module_path == "marcus/lesson_plan/quinn_r_gate.py"
```

**NEW:**
```python
assert entry.module_path == "app/marcus/lesson_plan/quinn_r_gate.py"
```

**Rationale.** Lockstep with §4.3 production fix. Test was authored to pin a previous step-12 fix and was not lockstep-updated when post-S2 namespace collapse moved the module. Authorized by §4.2 allowlist extension.

### 4.5 — Slice D re-application (stale gitignored-file content-pin test)

**Action:** `git rm tests/migration/test_slab_2c_next_session_start_here_updated.py`

**Rationale.** Test asserts content of `next-session-start-here.md` which is gitignored per `.gitignore:96` (hybrid-local session-guidance discipline; not synced with primary). CI environments cannot see the file; the test cannot pass in any non-operator-local environment. Deletion is the cleanest fix; the test served no production purpose post the gitignore policy change.

### 4.6 — Catalog refresh (Trial-3 forensic-comparison protocol preservation)

**File:** `_bmad-output/implementation-artifacts/broad-regression-baseline-2026-05-07.md`

Add post-S6 closure annotation:

> **RESOLVED-AT-`<commit>`** (Pre-Trial-3 Substrate Amendment 2026-05-19): Cat-1 sub-entry (1 of 4 — `test_pack_section_sequence_matches_manifest_order` unchanged) + Cat-3 sub-entry (none affected) + Cat-7 sub-entry (none affected) + Cat-8 sub-entry (`test_slab_2c_next_session_start_here_updated` REMOVED via deletion) + Cat-12 sub-entry (`test_g0_poll_surface_dsl_registration` RESOLVED via Slice A cascade) + the trial-smoke-harness battery (8 entries) and coverage-manifest cluster (3 entries). **Post-amendment broad-regression count: ~76 failures (88 → 76 = −12 net).** This becomes the new Trial-3 forensic-comparison baseline.

Update the Summary table count from `82` → `~76`.

### 4.7 — Deferred-inventory entry closure

**File:** `_bmad-output/planning-artifacts/deferred-inventory.md §Post-S6 Housekeeping Probe — Slice A`

Add to the existing entry: `~~strikethrough~~` the entry's title with **CLOSED 2026-05-19 via sprint-change-proposal-2026-05-19.md (commit `<sha>`)** marker. Preserve the entry verbatim for audit trail.

---

## Section 5: Implementation Handoff (per checklist §5.5)

**Scope classification:** **Moderate**. Substrate amendment to a test-side tripwire + lockstep test edits + production code path-pin update + catalog refresh. Not a full PRD/epic restructure; not a major architecture revision. Direct implementation by Developer agent (orchestrator role for this session).

**Sequencing (single-commit-cluster or multi-commit; recommend multi for forensic clarity):**
1. **Commit C1** — TW-7c-4 + 30-1 allowlist amendments (substrate amendment ratified by party-mode round 3 on this proposal). Single commit with HEREDOC-style message referencing this proposal.
2. **Commit C2** — Slice A path-pin re-application (`coverage_manifest.py`) + Slice A lockstep test-pin update (`test_coverage_manifest_regenerates_on_current_state.py:51`) + Slice D deletion (`tests/migration/test_slab_2c_next_session_start_here_updated.py`). Single bundled commit with `git rm` + edits. Diff size: ~22 lines total.
3. **Commit C3** — catalog refresh (`broad-regression-baseline-2026-05-07.md`) + deferred-inventory closure marker. Docs-only commit.
4. **Push** between C1+C2 and after C3 (per push-cadence policy).

**Verification gates (binding):**
- After C1: TW-7c-4 must PASS. 30-1 guard pass/fail unchanged from pre-amendment baseline.
- After C2: broad regression delta must be net-negative AND no NEW failing test IDs may appear that aren't in the post-amendment baseline.
- After C3: docs-only; no test changes.

**Handoff recipients:**
- **Orchestrator (this agent)** executes C1 + C2 + C3.
- **Operator** approves the proposal explicitly before C1 lands (checklist §6.3 binding).
- **Party-mode (Murat + Amelia + Winston + John)** ratifies the proposal as a substrate-amendment round per BMAD sprint governance §2.

**Success criteria:**
- TW-7c-4 PASS post-amendment
- 30-1 guard pass-state unchanged or improved
- Broad regression at ≤76 failures
- No new failure IDs introduced beyond pre-amendment baseline
- Origin synced; working tree clean; push-cadence honored

---

## Section 6: Approval + Routing

**Operator approval status:** GRANTED 2026-05-19 (strategic direction; option `dispatch_correct_course` selected from orchestrator decision-point).

**Party-mode ratification status:** PENDING. Convening Round 3 immediately on this proposal (Murat + Amelia + Winston + John; possibly Mary for stakeholder framing). Per new governance amendment: impasse → Quinn → John tiebreaker.

**Post-ratification action:** orchestrator applies C1 → verify → C2 → verify → C3 → push.
