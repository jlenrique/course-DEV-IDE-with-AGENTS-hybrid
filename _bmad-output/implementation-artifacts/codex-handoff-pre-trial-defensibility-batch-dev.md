# Codex dispatch: pre-trial Batch 2 — SHIP-defensibility passes (B-trace + B-nfr + B-tr)

**Session:** 2026-04-26 (operator-authorized; runs AFTER Batch 1 closes)
**Branch:** `dev/langchain-langgraph-foundation`
**Predecessor:** Batch 1 (`codex-handoff-pre-trial-batch-dev.md`) closed; B1+B2+B3+B5+B7+B9 done; B-extra attempted (succeeded or fell back); B-cr code review patches landed.
**Mission:** produce structured ship-defensibility evidence on the actual post-Batch-1 state. These are READ-AND-REPORT passes — they do NOT change code. They produce evidence artifacts that strengthen the M5 SHIP-CONDITIONAL claim and surface any defensibility gaps before operator runs a real trial.

## Why a second batch

Batch 1 was build-and-fix work: cascade YAML corrections, live-smoke scaffolds, doc actualization, dispatch-registry swap, optional launcher, code-review-driven patches. That batch CHANGES the code.

Batch 2 is structured-review work using the BMAD `testarch` skill family. Three independent passes, each producing a discrete evidence artifact:

- **B-trace** — FR → AC → test → implementation traceability matrix.
- **B-nfr** — non-functional requirement assessment against the M5 NFR set.
- **B-tr** — test-quality audit on the 5a.3 cost-engineering surface.

Run AFTER Batch 1 so the assessments cover post-fix state. These passes do NOT belong in Batch 1 because (a) running them on a moving target wastes effort and (b) they're orthogonal to Batch 1's defect-fix work.

**Operator preference (binding, same as Batch 1):** "do it right, no band-aids, only rational trade-offs that get named in writing." If a pass surfaces a gap, file it explicitly with reactivation gate; do not silently shelve.

## Tasks (run in roughly this order; B-trace + B-nfr can parallelize)

### B-trace — `bmad-testarch-trace` (FR traceability matrix)

**Goal:** produce a traceability matrix that maps every load-bearing FR to its acceptance criteria, the tests that exercise it, and the implementation files that carry it. The 15-invariant matrix at `_bmad-output/implementation-artifacts/15-invariant-audit-matrix.md` already does this for the 15 invariants; B-trace extends to the broader FR set.

**FR set in scope (M5-relevant):**
- **FR51** — trial replay byte-for-byte reproducibility (5a.1).
- **FR52** — head-to-head parity (5a.2).
- **FR54** — cache hit-rate / prefix stability (5a.3 substitute metric).
- **FR55, FR56** — cost-engineering foundation (5a.3 amended scope).
- **FR60** — backport channel closed.
- **FR61** — forward-port playbook.
- **FR62** — rollback plan.
- **FR63** — invariant preservation evidence (5a.4).
- **FR64** — anti-pattern catalog (5a.4).
- **FR2** — FastAPI + MCP transport parity (Slab 1 + 3).
- **FR30** — sanctum cold-read fingerprinting.
- **FR34** — HIL gate authority (operator verdict + resume API).
- **FR40** — Marcus/Cora lane separation.
- **FR42** — LangSmith trace export.
- **FR43** — frozen-graph compiled-digest stability.
- **FR59** — sanctum_watcher.

**Invocation:**
1. Invoke `bmad-testarch-trace` skill via the Skill tool.
2. Source-of-truth FR set: `_bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md` (the architecture doc enumerates FRs); cross-reference with story specs for AC mappings.
3. Test discovery: walk `tests/` with `pytest --collect-only -q` for the canonical test inventory; map each FR to its exercising tests by reading test docstrings + AC pin references in story specs.
4. Implementation discovery: read story specs for "File Structure Requirements §NEW files" + grep for the FR identifier in code comments.

**Deliverable:** `_bmad-output/implementation-artifacts/m5-fr-traceability-matrix.md` with table format:

| FR | Description | Slab/Story | ACs | Tests | Implementation files | Status |
|---|---|---|---|---|---|---|
| FR51 | Trial replay byte-for-byte | 5a.1 | AC-5a.1-A,B,C,D | tests/integration/replay/*, tests/trial_replay/* | app/replay/{discovery,regression}.py | TRACED |
| ... | ... | ... | ... | ... | ... | ... |

Status enum: `TRACED` (every FR has at least one test + implementation file) / `PARTIAL` (FR has implementation but tests are gap-shaped) / `GAP` (FR has neither, or implementation is silent on the FR).

**Disposition rule:**
- `TRACED` items: no action; included in matrix as evidence.
- `PARTIAL` items: file as deferred-inventory entries (`m5-fr-trace-partial-<FR>` with reactivation gate "test surface added that exercises FR<N> end-to-end").
- `GAP` items: HALT and surface to operator. A genuine FR gap at M5 is a finding that should affect the conditional-window resolution path. Do not silently file.

**Critical:** the matrix is a defensibility artifact, not a re-litigation of M5. If a `GAP` is found, the question is "what do we do during the conditional window," not "should we re-vote M5." Surface clearly with options.

**Verify:** matrix file exists; row count matches FR set in scope (16 FRs minimum); each row has populated columns; status enum honored.

**Time estimate:** ~2-3 hours.

### B-nfr — `bmad-testarch-nfr` (non-functional requirement assessment)

**Goal:** assess whether the M5 NFR set is actually MET by the implementation — not just "we have a test for it" but "the NFR contract holds."

**NFR set in scope:**
- **NFR-X1** — replay determinism (5a.1).
- **NFR-X3** — variance-band tolerance for sanctum-fingerprint (5a.1, D1 sanctum variance policy).
- **NFR-X4** — per-trial wall-clock budget ≤15 min (5a.1).
- **NFR-X5** — replay completeness (100% of closed trials replay-covered) (5a.1).
- **Cost-engineering NFRs** (implicit, derived from 5a.3 amendment): per-trial cost reports persisted; per-agent attribution computed; cascade digest stable; pricing digest stable.
- **Sanctum NFRs** — cold-read fingerprint determinism + watcher debounce (Slab 4 4.6).
- **Transport NFRs** — FastAPI ↔ MCP byte-equivalent parity (Story 1-1d).

**Invocation:**
1. Invoke `bmad-testarch-nfr` skill via the Skill tool.
2. NFR source: architecture doc + story specs (especially 5a.1, 5a.2, 5a.3, 1-1d).
3. Implementation source: relevant `app/` modules + test fixtures.

**Deliverable:** `_bmad-output/implementation-artifacts/m5-nfr-assessment.md` with per-NFR:

```
### NFR-X4 — Per-trial wall-clock budget ≤15 min
**Source:** Slab 5a Story 5a.1.
**Implementation:** app/replay/regression.py::replay_trial wraps in time.perf_counter() + raises ReplayBudgetExceeded.
**Test coverage:** tests/integration/replay/test_replay_budget.py (under-budget passes; over-budget raises).
**Assessment:** MET. Implementation enforces; test exercises both branches.
**Confidence:** HIGH. (Implementation is direct; test is parametrize-collapsible to single-purpose.)
**Risk:** none surfaced.
```

Confidence enum: `HIGH` / `MEDIUM` / `LOW` / `UNVERIFIABLE-IN-DEV` (last for NFRs that can only be confirmed by real trial execution; document the verification gate).

**Disposition rule:**
- `MET, HIGH/MEDIUM`: no action.
- `MET, LOW`: file as deferred-inventory entry with reactivation gate "additional test surface to raise confidence."
- `MET, UNVERIFIABLE-IN-DEV`: name the verification gate explicitly (likely closes during operator trial run).
- `NOT MET`: HALT and surface. NFR-not-met at M5 is a finding that affects ship state.

**Verify:** assessment file exists; one §-block per NFR in scope; confidence + assessment + risk fields populated.

**Time estimate:** ~1-2 hours.

### B-tr — `bmad-testarch-test-review` (test-quality audit)

**Goal:** quantitative assessment of the 5a.3 test surface specifically (highest-risk surface for "tests pass + production breaks" because the cost-engineering foundation depends on Pydantic v2 strict-mode contracts firing correctly).

**Scope:**
- `tests/unit/runtime/test_trial_economics_report_strict.py`
- `tests/unit/runtime/test_check_trial_budget.py`
- `tests/unit/runtime/test_compute_per_agent_drift.py`
- `tests/integration/runtime/test_measure_trial_cost.py`
- `tests/integration/runtime/test_cascade_config_loading.py`
- `tests/integration/runtime/test_pricing_table_covers_cascade.py`
- `tests/integration/runtime/test_record_trial_cost_report.py`
- `tests/integration/runtime/test_migration_health_dashboard_cost_rows.py`
- `tests/migration/test_5a_3_characterization_baseline_present.py`

**Invocation:**
1. Invoke `bmad-testarch-test-review` skill via the Skill tool.
2. Use 0-100 scoring per the catalog spec. Sub-scores per dimension if the skill outputs them (assertion strength, fixture realism, edge-case coverage, mutation resistance, etc.).
3. Critical questions to answer per test file:
   - Does the test exercise what it claims, or does it pass tautologically?
   - Does it cover the negative path (e.g., does `test_trial_economics_report_strict.py` actually verify rejection of invalid inputs, not just acceptance of valid ones)?
   - Does the fixture data resemble production data, or is it minimal-to-pass?
   - Would a reasonable code mutation be caught by the test?

**Deliverable:** `_bmad-output/implementation-artifacts/5a-3-test-quality-audit.md` with per-file score + per-file finding list + overall surface score + recommended remediation if score < 70.

**Disposition rule:**
- Files scoring ≥70: no action.
- Files scoring 50-69: file as deferred-inventory entry with reactivation gate "test hardening pass on `<file>`."
- Files scoring <50: HALT. A test surface scoring <50 on a load-bearing M5 surface is a finding that affects ship state. Surface to operator with options (patch now / file as M5 condition / accept with explicit rider).

**Verify:** audit file exists; one block per file in scope; per-file score + overall score; remediation noted for any below-70 file.

**Time estimate:** ~1-2 hours.

## What NOT to do in this batch

- **No code changes.** B-trace, B-nfr, B-tr are read-and-report. Findings get filed; they do NOT auto-patch.
- **No re-vote on M5.** SHIP-CONDITIONAL stands. These passes are evidence-strengthening, not verdict-revisiting.
- **No new tests.** If B-tr finds a test gap, FILE the finding. Do not author the missing test inside this batch — that would be Batch-3 work (or operator-decision-made).
- **No expansion outside the M5 surface.** If B-trace surfaces FR gaps in NON-M5 surfaces (e.g., Slab 2c), file as deferred but do not chase.
- **No retrospective work.** `slab-5a-retrospective.md` is final.

## What to escalate, if needed

- **Genuine FR `GAP` finding from B-trace.** Operator-decision: does the gap affect ship state during the conditional window?
- **NFR `NOT MET` finding from B-nfr.** Operator-decision: same as above.
- **Test surface `<50` score from B-tr on a load-bearing surface.** Operator-decision: same as above.

In all three cases: HALT and surface; do not silently file. The defensibility batch is meant to either confirm the M5 SHIP-CONDITIONAL claim is sound OR identify the gaps that should affect resolution path during the conditional window.

## Verification gates at batch close

For each pass:
- `_bmad-output/implementation-artifacts/m5-fr-traceability-matrix.md` exists; row count + columns valid; status enum honored.
- `_bmad-output/implementation-artifacts/m5-nfr-assessment.md` exists; per-NFR §-blocks; confidence + assessment + risk per NFR.
- `_bmad-output/implementation-artifacts/5a-3-test-quality-audit.md` exists; per-file score + overall + remediation.

For the batch as a whole:
- Every `patch` / `defer` / `decision_needed` finding has a recorded disposition.
- Any HALT-and-surface findings are documented at the top of each artifact AND in this batch's close report.
- `_bmad-output/planning-artifacts/deferred-inventory.md` reflects all newly-filed entries.

## Operator-presence work that remains AFTER both batches

If both batches land cleanly and no HALT-and-surface findings arise:

1. **M2 Wondercraft live-artifact ceremony** (~10-15 min operator + render time).
2. **M3 Texas live-retrieval ceremony** (~5-10 min operator).
3. **One real trial run** through the migrated runtime against live OpenAI (~30-60 min operator + trial duration).

Three operator-windows in one focused session. After: unconditional SHIP at the next session.

If B-extra in Batch 1 succeeded, item 3 also closes the 5a.2 launcher rider in the same operator session.

If any HALT-and-surface findings emerge in Batch 2, operator decides whether to remediate now (Batch 3) or accept as conditional-window remediation tasks.

## Carry-forward notes

- Repo-wide pytest remains environment-tainted on operator's Windows machine. B-tr must work from collected-test inventory + per-file analysis, not from running the tests; if the skill needs running tests, document the limitation.
- B-trace + B-nfr produce defensibility artifacts that should be referenced from `_bmad-output/upstream-state.md` and `_bmad-output/implementation-artifacts/m5-decision.md` so they're discoverable post-trial.
- These artifacts may be re-run after the operator trial closes the M2 + M3 + 5a.2-launcher conditions to update the defensibility record before unconditional SHIP.

## Why this batch matters

The M5 SHIP-CONDITIONAL verdict is operator-accepted, but the conditional window is short (through 2026-05-03). The operator wants the close to be defensible, not just achieved. Three structured-review passes that produce written evidence — FR traced, NFRs assessed, test quality audited — are exactly the artifacts a "do it right" close calls for.

If all three pass cleanly, the SHIP-CONDITIONAL claim is structurally vindicated and the conditional window is about closing the 4 named conditions, not about discovering hidden defects.

If any finding emerges, it surfaces while there's still time to address it within the window — which is the point.

## Final notes

These passes are evidence-producing, not code-changing. The deliverables are Markdown artifacts that join the M5 close evidence stack alongside `m5-decision.md`, `slab-5a-retrospective.md`, `15-invariant-audit-matrix.md`, and `migrated-runtime-characterization-2026-04-26.md`.

After this batch: the M5 SHIP-CONDITIONAL evidence base is as defensible as Codex-time can make it. The remaining gaps are operator-presence-only.
