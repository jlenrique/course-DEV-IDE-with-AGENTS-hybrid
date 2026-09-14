# Claude Shadow Monitor - fresh round (2026-07-06)

Started: 2026-07-06T19:17:35-04:00
Branch: `dev/workbook-2026-07-06`
Baseline HEAD: `d049453b` (`docs(session-16): WRAPUP - Canonical Production Conversation arc S0+S1+S2 CLOSED, both live-proven (Class S)`)
Status at setup: armed; run-start signal received 2026-07-06T19:21:05-04:00.

## Product boundary

The monitor judges changes only against the Marcus-SPOC runtime orchestrator product goal: the operator-facing surface that drives a real instance of the app and its production runtime. Exploratory, concierge, trial, and proofing runs are evidence vehicles only. Findings from those runs matter only when they expose a product-relevant defect, missing gate, vacuous-green risk, or regression in the production SPOC runtime.

## Monitor lane

This is an independent, read-only shadow-monitoring lane for the upcoming run. The monitor writes only to this ledger. It may read repo state, diffs, logs, evidence, tests, and existing governance artifacts, and it may run read-only verification commands when useful. It must not edit production code, tests, runtime state, story artifacts, commits, or dev-agent-owned work.

## Polling protocol

- First poll: when the operator alerts that the run has started.
- Cadence after first poll: every 10 minutes while the run remains active, plus any operator-requested checkpoint poll.
- Each poll records current repo state, reviewed diffs/evidence, findings, recommendations, and disposition of prior findings.
- Verdict grammar: `CONCUR`, `CONCUR-WITH-FINDINGS`, or `OBJECT`.
- Finding IDs use `F-NNN` and stay open until explicitly closed or superseded.
- Recommendations must distinguish product-impacting fixes from proofing-run convenience.

## Baseline

- Existing canonical shadow reports are in `_bmad-output/implementation-artifacts/`.
- This ledger intentionally does not overwrite the untracked prior workbook ledgers:
  - `claude-shadow-monitor-workbook-2026-07-06.md`
  - `claude-shadow-monitor-workbook-2026-07-06.pre-poll007-recovered.md`
- Baseline `git status --short --branch`:

```text
## dev/workbook-2026-07-06...origin/dev/workbook-2026-07-06
?? _bmad-output/artifacts/workbooks-test/
?? _bmad-output/implementation-artifacts/claude-shadow-monitor-workbook-2026-07-06.md
?? _bmad-output/implementation-artifacts/claude-shadow-monitor-workbook-2026-07-06.pre-poll007-recovered.md
```

## Poll Log

### SETUP-000 - monitor armed (2026-07-06T19:17:35-04:00)

Fresh ledger created in the repo's canonical implementation-artifacts location. No run-start poll has been performed yet. Awaiting operator signal.

### POLL-001 - run-start / spec-preflight (2026-07-06T19:21:05-04:00)

**Trigger:** operator signaled dev operations are under way and the new deliverables are being specified.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with `origin/dev/workbook-2026-07-06`.
- HEAD: `d049453b` (`docs(session-16): WRAPUP - Canonical Production Conversation arc S0+S1+S2 CLOSED, both live-proven (Class S)`).
- No new commit since setup.
- No new spec/deliverable artifact visible yet beyond this fresh monitor ledger.
- Current untracked set:

```text
?? _bmad-output/artifacts/workbooks-test/
?? _bmad-output/implementation-artifacts/claude-shadow-monitor-fresh-round-2026-07-06.md
?? _bmad-output/implementation-artifacts/claude-shadow-monitor-workbook-2026-07-06.md
?? _bmad-output/implementation-artifacts/claude-shadow-monitor-workbook-2026-07-06.pre-poll007-recovered.md
```

**Inherited context verified:**

- `next-session-start-here.md` names the immediate next canonical arc action as S3: Gary shadow-parity WARN + §06 fold + both-walk receipts.
- Prior canonical monitor `canonical-arc-claude-shadow-monitor-2026-07-06.md` closes S2 and explicitly carries S3 spec obligations F-402, F-304, and F-702..F-705 into the next poll.
- The same prior record carries F-605 as an S5-opening precondition: green the known 13-red `g0_enrichment` battery before S5, rather than letting that accepted baseline red become a later regression fog.

**Findings:**

- **F-001 (preflight, open):** no new S3/deliverable spec is visible yet, so the monitor cannot certify inheritance. The first spec artifact must explicitly include F-402, F-304, and F-702..F-705 before dev dispatch.
- **F-002 (preflight, open):** there are two plausible "next" tracks in local context: the canonical arc S3 listed at the top of `next-session-start-here.md`, and later workbook/orientation language in the same file. This is not a code defect, but it is a spec-risk. The new deliverable spec should name which track is active and why, so the monitor does not apply the wrong acceptance frame.

**Recommendations before dispatch:**

1. If the new deliverable is S3, include these non-negotiables in the spec text: status-keyed parity clock; directive/envelope pick source rather than sidecar source; trial-start digest vs CD envelope digest cross-check; shared resolver only, not picker pickability; full emitted `_styleguide_resolution_block` key set as schema-v1 SSOT; WARN-seed untouched until S4.
2. If the new deliverable is the workbook/orientation track, state that it is intentionally superseding or sequencing ahead of S3, and restate the Marcus-SPOC product impact so proofing convenience does not become the design target.
3. Carry the accepted baseline reds by name in the spec's green criteria. Do not let F-605 or the known pre-existing Marcus battery reds become ambiguous "new work broke tests" noise.
4. Keep this lane ledger-only. Prior session evidence includes a stash roundtrip that briefly hid untracked monitor history; use throwaway worktrees for destructive experiments or branch comparisons.

**Verdict:** `CONCUR-WITH-FINDINGS` for spec drafting to continue. Do not dispatch dev implementation until F-001 and F-002 are resolved in the spec or by operator clarification.

**Next poll:** heartbeat automation `shadow-monitor-fresh-round-poll` is active on a 10-minute cadence.

**Operator clarification (2026-07-06T19:24 local):** the workbook question was informational, not a request to redirect the active run. Canonical order stands: S3 = Gary shadow-parity; S4 = FAIL-LOUD; S5 = G0 canonical; S6 = Tracy canonical; S7 = workbook generalization; S8 = composed proof. **F-002 CLOSED** - no ambiguity for the monitor frame unless a later operator directive explicitly changes the sequence.

### POLL-002 / SOP-008 - S3 spec pre-dispatch review (2026-07-06T19:30:25-04:00)

**Trigger:** heartbeat poll. New untracked S3 spec appeared: `_bmad-output/implementation-artifacts/canonical-arc-s3-gary-shadow-parity.md`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, still synced with origin.
- HEAD unchanged: `d049453b`.
- New untracked spec: `canonical-arc-s3-gary-shadow-parity.md` (19,025 bytes, modified 2026-07-06 19:27 local).
- No production code/test changes visible yet.

**SOP-008 inheritance check:**

- **F-402 honored.** The spec makes the committed CD emission function the schema-v1 SSOT: `_styleguide_resolution_from_projection` in `app/specialists/cd/graph.py`, not the stale S1 D3 sketch. It enumerates the full block key set.
- **F-304 honored.** The spec treats missing v1 keys as `divergence/contract-violation`, not a tolerant degrade.
- **F-702 honored.** The parity clock is status-keyed, with pick presence derived from the directive/envelope at CD-read time and never sidecar events.
- **F-703 honored.** The spec requires trial-start/CD/Gary directive digest cross-checking and classifies digest mismatch as `expected-ordering-gap/directive-drift`, never divergence.
- **F-704 honored.** The comparator uses the shared resolver path only and explicitly keeps picker pickability out of parity.
- **F-705 honored.** The spec carries public `read_pick_events`, heterogeneous sidecar tolerance, `trial_id.hex`, F-605 baseline reds, and WARN-seed untouched until S4.
- Workbook scope is correctly out of scope and sequenced to S7.

**Code-claim spot checks:**

- CD function exists at `app/specialists/cd/graph.py` and currently emits `styleguide_resolution`.
- Gary resolve site still has `DEFAULT_VARIANT_PAIR`, inline `{"A","B"}`, and the WARN-seed text the spec says S3 must not flip.
- Runner currently supplies Gary only `export_dir` + `gamma_settings`; S3's D4 digest-threading is therefore a real new seam, not already-present behavior.
- Public `read_pick_events` exists, with `_read_pick_events` preserved only as a back-compat alias.
- The package-builder fold target is real: `build_gary_briefs` is currently gated against `app.specialists.gary.payload_contract.CONSUMED_PAYLOAD_KEYS`, so the D1 payload-contract extension will be load-bearing.

**Disposition of prior findings:**

- **F-001 CLOSED.** The S3 spec is visible and explicitly inherits F-402, F-304, and F-702..F-705.
- **F-002 CLOSED previously by operator clarification.**

**New findings:**

- **F-003 (material, spec consistency):** D3 prose says Gary's one-read SSOT sha256 "feeds the receipt's `gary_ssot_digest`", and the divergence rationale says `ssot_digest` comparison discriminates mid-run SSOT drift. But the v1 receipt schema lists no `gary_ssot_digest` top-level field. It only lists `cd_bound_guides` / `gary_bound_guides` and resolution/directive digests. This is fixable, but it should be explicit before dev dispatch: either add `gary_ssot_digest` (and likely the relevant CD guide-level `ssot_digest` comparison rule) to the receipt schema, or state that SSOT drift evidence lives only inside `gary_bound_guides`/`detail`.

**Recommendations before dev dispatch:**

1. Patch the S3 spec for F-003 so the receipt schema and comparison prose name the same SSOT-drift evidence.
2. Keep D1's projection fallback narrow. If manifest `dependency_projections` cannot carry `None`, the fallback to runner context should be recorded as a named deviation and still tested by both-walk receipt witnesses; otherwise the "manifest-truthful data plane" claim becomes too loose.
3. Instruct the dev agent to preserve exact pins rather than updating them wholesale. This story touches shared digest, manifest, and Gary dispatch seams; weakened exact-shape assertions would hide the class of drift S3 is supposed to expose.

**Verdict:** `CONCUR-WITH-FINDINGS`. The spec is on the right track and satisfies the inherited SOP-008 obligations, but F-003 should be corrected in the spec text before implementation dispatch.

### POLL-003 - post-SOP-008 relay / ready-for-dev check (2026-07-06T19:40:25-04:00)

**Trigger:** heartbeat poll.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, still synced with origin.
- HEAD unchanged: `d049453b`.
- Modified tracked artifacts:
  - `_bmad-output/implementation-artifacts/canonical-arc-claude-shadow-monitor-2026-07-06.md`
  - `_bmad-output/planning-artifacts/canonical-production-conversation-arc-greenlight-party-record-2026-07-06.md`
- Untracked S3 spec remains: `_bmad-output/implementation-artifacts/canonical-arc-s3-gary-shadow-parity.md`.
- No production code/test diff visible yet.

**Observed changes:**

- Canonical monitor ledger now includes relayed **SOP-008** for S3 and marks dev dispatch approved after F-801/F-802 amendments.
- S3 spec status changed to `READY-FOR-DEV`.
- S3 spec incorporates the main SOP-008 amendments: `trial-start.json` is now the digest source (F-801); `cd_styleguide_resolution` now travels through chartered runner context, not manifest projection / package-builder mutation (F-802); F-805 path fence and F-806 resolver-emitted mutation are encoded.
- Party record gained a binding S7 operator checkpoint addendum: workbook generalization spec must go through operator review/edit/approval for purpose, contents, design/structure, and sources before monitor pre-dispatch and dev dispatch.

**Prior finding disposition:**

- **F-001 CLOSED.** Still closed; S3 spec is present and inherited obligations were also verified by the canonical SOP-008.
- **F-002 CLOSED.** Still closed; sequence remains S3 now, workbook at S7.
- **F-003 OPEN.** The amended S3 spec still says Gary's SSOT byte read feeds the receipt's `gary_ssot_digest`, but the v1 receipt schema still does not list `gary_ssot_digest`. The schema lists `cd_bound_guides` / `gary_bound_guides`, but the prose names a top-level receipt field. This mismatch was not addressed by the F-801/F-802 amendments.

**New findings:**

- **F-004 (process, material):** the spec is now `READY-FOR-DEV` and the relayed canonical SOP-008 says dev was dispatched, while this ledger's F-003 remains unresolved. This is not a production-code defect, but it creates a high-likelihood implementation ambiguity: the dev agent may either add an unplanned `gary_ssot_digest`, omit it despite prose, or hide it in nested `gary_bound_guides` while tests assert a different shape.

**Recommendations:**

1. Before or during dev T1, amend the S3 spec to close F-003 explicitly. Preferred low-risk wording: add `gary_ssot_digest` to the v1 receipt schema if the comparator needs a top-level SSOT drift oracle. Alternative: delete the top-level-field wording and require SSOT drift evidence inside `gary_bound_guides` plus `detail`.
2. At SOP-009/dev-complete, inspect the implemented receipt shape first, before test counts. The first question should be whether `styleguide_parity` has exactly the shape the spec intends after F-003 is resolved.
3. Preserve the S7 operator checkpoint addendum; it is product-relevant because workbook purpose/content/source choices are operator-facing, not just implementation mechanics.

**Verdict:** `CONCUR-WITH-FINDINGS`. S3 can continue only if F-003 is resolved in the dev handoff or spec patch; otherwise SOP-009 should treat the receipt shape as suspect until proven by code and tests.

### POLL-004 - quiet cadence / no visible dev diff yet (2026-07-06T19:50:25-04:00)

**Trigger:** heartbeat poll.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, still synced with origin.
- HEAD unchanged: `d049453b`.
- Worktree shape unchanged from POLL-003:
  - modified tracked artifacts: canonical arc monitor ledger + party record
  - untracked S3 spec + this fresh monitor ledger + prior workbook monitor artifacts + `_bmad-output/artifacts/workbooks-test/`
- No production code/test diff visible yet.
- No new spec/evidence artifact since the S3 READY-FOR-DEV update.

**Finding disposition:**

- **F-001 CLOSED.**
- **F-002 CLOSED.**
- **F-003 OPEN.** Still no visible spec patch resolving the `gary_ssot_digest` receipt schema/prose mismatch.
- **F-004 OPEN.** Still applicable: S3 is READY-FOR-DEV while F-003 is open in this monitor lane.

**Recommendations carried forward:**

1. SOP-009/dev-complete should inspect the implemented `styleguide_parity` receipt shape before treating test counts as meaningful.
2. If the dev implementation includes a top-level `gary_ssot_digest`, the spec should be patched to include it in the v1 receipt schema. If it does not, the prose should stop naming it as a receipt field and tests should assert the chosen nested evidence location.
3. Continue treating the S7 operator checkpoint addendum as binding; no workbook spec should dispatch before operator review of purpose, contents, design/structure, and information sources.

**Verdict:** `CONCUR-WITH-FINDINGS`. No new blocker beyond carried F-003/F-004; next useful poll is at visible dev-complete diff or the next cadence interval.

### POLL-005 - S3 RED scaffold visible (2026-07-06T20:00:35-04:00)

**Trigger:** heartbeat poll.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, still synced with origin.
- HEAD unchanged: `d049453b`.
- New visible S3 dev work is test-first / RED-scaffold oriented:
  - modified tracked test: `tests/marcus/orchestrator/test_picker_cd_vocabulary_lockstep.py`
  - modified tracked test: `tests/integration/marcus/test_package_builders.py`
  - untracked tests: `tests/styleguide/test_parity_comparator.py`, `tests/specialists/gary/test_styleguide_parity_receipt.py`, `tests/orchestrator/test_gary_parity_payload_seam.py`, `tests/composition/test_gary_parity_walk_pin.py`
- No app/runtime implementation file is visible yet.

**What the RED scaffolds cover well:**

- F-801 is encoded concretely: `test_gary_parity_payload_seam.py` sources `trial_start_directive_digest` from `trial-start.json`, and the walk pin adds a continuation-walk non-null digest witness.
- F-802 is encoded concretely: tests require legacy/pre-S3 envelopes to dispatch cleanly with `cd_styleguide_resolution is None` and an honest `cd-envelope-absent-legacy` receipt.
- D5/F-704 lockstep is encoded: picker + CD + Gary vocabularies are expected to converge through a test-only three-way pin.
- AC-4 is represented with byte-identity checks for Gamma packet/settings, WARN-seed text, and resolver `guides=` parity.
- The RED scaffolds preserve the product boundary: they target Marcus-SPOC runtime data flow and observability, not proofing-run convenience.

**Finding disposition:**

- **F-001 CLOSED.**
- **F-002 CLOSED.**
- **F-003 OPEN, sharpened.** `tests/styleguide/test_parity_comparator.py` defines `RECEIPT_KEYS` and asserts `set(receipt) == RECEIPT_KEYS`; that set omits `gary_ssot_digest`. The amended spec still says Gary's one-read SSOT sha256 "feeds the receipt's `gary_ssot_digest`." The tests now make the implementation choice concrete: unless changed, top-level `gary_ssot_digest` will be excluded by test contract while the spec continues to name it as present.
- **F-004 OPEN.** Still applicable until F-003 is explicitly resolved in spec and tests.

**New findings:**

- **F-005 (material, RED-contract drift):** the RED scaffold currently codifies one side of the F-003 ambiguity without closing the spec. If the intended design is "SSOT drift evidence lives in `gary_bound_guides` and `detail.gary_view.ssot_digest`, not top-level `gary_ssot_digest`," the spec should say that. If the intended design is a top-level field, `RECEIPT_KEYS` must add it before the implementation is written to the wrong contract. This is a test/spec lockstep issue, not a runtime bug yet.

**Recommendations:**

1. Resolve F-003/F-005 before or at the next dev handoff. The cleanest patch is either:
   - add `gary_ssot_digest` to the spec receipt schema and to `RECEIPT_KEYS`, or
   - remove the phrase "receipt's `gary_ssot_digest`" from D3 and require SSOT drift evidence in `gary_bound_guides` plus `detail.gary_view.ssot_digest`.
2. At SOP-009, verify both the code and tests agree on the exact `styleguide_parity` receipt contract before reviewing broader behavior.
3. Keep the current RED direction on F-801/F-802; those tests are product-relevant and should stay at full strength.

**Verdict:** `CONCUR-WITH-FINDINGS`. RED-first scaffolding is useful and mostly aligned, but F-003/F-005 should be fixed before the receipt schema hardens further.

### POLL-006 - S3 implementation visible / focused suites green (2026-07-06T20:10:25-04:00)

**Trigger:** heartbeat poll.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, still synced with origin.
- HEAD unchanged: `d049453b`.
- S3 app implementation is now visible in the working tree:
  - `app/styleguide/parity.py` added
  - `app/specialists/cd/graph.py` digest helper extraction
  - `app/specialists/gary/_act.py` parity receipt wiring at `generate_gamma_variants`
  - `app/specialists/gary/payload_contract.py` payload-key extension
  - `app/marcus/orchestrator/production_runner.py` runner parity context and `trial-start.json` digest source
- Additional touched tests include audit scope, package-builder pins, Gary dispatch, and additional-instructions channel tests.

**Verification run by monitor:**

- `python -m pytest tests\styleguide\test_parity_comparator.py -q` failed before collection because the default system Python is 3.10 and cannot import `datetime.UTC` used by the repo harness.
- Re-run with repo venv: `.\.venv\Scripts\python.exe -m pytest tests\styleguide\test_parity_comparator.py -q` → **43 passed**.
- `.\.venv\Scripts\python.exe -m pytest tests\specialists\gary\test_styleguide_parity_receipt.py -q` → **12 passed**.

**Implementation spot-checks:**

- F-801 appears implemented as specified: `production_runner._trial_start_directive_digest` reads `run_dir/"trial-start.json"` and returns `None` for absent/malformed/no-key cases; tests pin the non-null witness.
- F-802 appears implemented as specified: `cd_styleguide_resolution` is runner context sourced from `production_envelope.latest_for_specialist("cd")`; no manifest/package-builder transport is introduced.
- AC-4 observability fence is represented in tests and code: the parity audit builds a receipt after `_normalized_gamma_settings`, logs based on trichotomy, and returns the receipt as a sibling output key.
- D5 appears implemented: `GARY_VARIANT_VOCABULARY` is a named constant and the test-level three-way pin imports it.

**Finding disposition:**

- **F-001 CLOSED.**
- **F-002 CLOSED.**
- **F-003 OPEN, but narrowed.** Code/tests have chosen the "no top-level `gary_ssot_digest`" design. The SSOT drift evidence is represented through `gary_bound_guides` and `detail.gary_view.ssot_digest`. However, the S3 spec still says the once-read SSOT sha feeds the receipt's `gary_ssot_digest`. The implementation is internally coherent; the spec prose remains stale.
- **F-004 OPEN until the spec is patched or SOP-009 explicitly ratifies this as an intentional schema choice.**
- **F-005 OPEN, same narrowing as F-003.** The RED contract is now green against the implementation, but still not lockstep with the prose.

**New findings:**

- **F-006 (process/tooling):** using bare `python` in this workspace can produce a false harness failure because it resolves to Python 3.10 (`datetime.UTC` missing). Dev/T11 verification commands should use `.\.venv\Scripts\python.exe` or the repo-approved Python runtime, not bare `python`, unless the environment has been proven to be 3.11+.

**Recommendations:**

1. Patch the S3 spec to close F-003/F-005 in the direction the implementation already took: receipt schema excludes top-level `gary_ssot_digest`; SSOT drift evidence lives in `gary_bound_guides` and `detail.gary_view.ssot_digest`.
2. SOP-009 should verify the broader changed-test set, especially `tests/orchestrator/test_gary_parity_payload_seam.py`, `tests/composition/test_gary_parity_walk_pin.py`, Ratchet-D/audit tests, and existing Gary dispatch regression tests. The two focused green suites are useful but not sufficient for dev-complete.
3. Use the repo `.venv` for verification to avoid false negatives from the system Python.

**Verdict:** `CONCUR-WITH-FINDINGS`. The core comparator and Gary receipt implementation are coherent and green in focused suites; the outstanding issue is now spec/test lockstep, not observed runtime behavior.

### POLL-007 - S3 seam/walk verification expanded (2026-07-06T20:20:25-04:00)

**Trigger:** heartbeat poll plus operator status request.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, still synced with origin.
- HEAD unchanged: `d049453b`.
- S3 implementation remains uncommitted and active across runner, CD, Gary, payload contract, audit-scope pins, and focused tests.
- New touched test since prior poll: `tests/integration/marcus/test_production_runner_resume_continues_execution.py`.

**Additional verification run by monitor (`.\.venv\Scripts\python.exe`):**

- `tests\orchestrator\test_gary_parity_payload_seam.py -q` -> **7 passed**.
- `tests\composition\test_gary_parity_walk_pin.py -q` -> **3 passed**.
- `tests\integration\marcus\test_package_builders.py::test_walker_builds_package_at_06_and_threads_briefs_to_gary tests\marcus\orchestrator\test_picker_cd_vocabulary_lockstep.py -q` -> **3 passed**.

**Assessment:**

- Runner seam looks correctly exercised: `cd_styleguide_resolution`, directive digest, and `trial_start_directive_digest` are tested through `_runner_payload_for_specialist`.
- Both-walk receipt coverage is present and green, including a continuation-walk `trial-start.json` non-null digest witness.
- F-802 legacy tolerance is tested through a clean legacy/pre-S3 envelope path.
- The package-builder exact pin was extended rather than weakened.
- The three-way vocabulary lockstep pin is green.

**Finding disposition:**

- **F-001 CLOSED.**
- **F-002 CLOSED.**
- **F-003 OPEN.** Still spec-prose stale: `canonical-arc-s3-gary-shadow-parity.md` continues to name a receipt `gary_ssot_digest` while the implemented and tested receipt schema excludes it.
- **F-004 OPEN but reduced.** The implementation chose a coherent shape and focused suites pass; the remaining process risk is stale spec text carrying forward into T11/closeout.
- **F-005 OPEN but reduced.** Tests and code agree; spec text is the outlier.
- **F-006 OPEN as an environment note.** Use `.venv`, not bare `python`.

**Recommendations:**

1. Claude dev should patch the S3 spec prose before dev-complete handoff so `gary_ssot_digest` is no longer named as a top-level receipt field.
2. SOP-009 should still verify broader touched suites: existing Gary dispatch regressions, additional-instructions channel, resume-continuation test, audit scope, import-linter, and ruff.
3. Do not treat the current green focused tests as dev-complete; they show the S3 core is shaping well, not that the story is closed.

**Verdict:** `CONCUR-WITH-FINDINGS`. Current S3 implementation trajectory is strong; the main monitor concern is documentation/spec lockstep, not the core runtime seam.

### POLL-008 - quiet cadence / no new S3 movement visible (2026-07-06T20:30:25-04:00)

**Trigger:** heartbeat poll.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, still synced with origin.
- HEAD unchanged: `d049453b`.
- Worktree shape unchanged from POLL-007:
  - S3 runtime implementation remains visible in `production_runner.py`, `cd/graph.py`, `gary/_act.py`, `gary/payload_contract.py`, and new `app/styleguide/parity.py`.
  - S3 tests remain visible across comparator, Gary receipt, runner seam, walk pin, package-builder exact pin, vocabulary lockstep, resume, audit, and Gary regression files.
  - No new evidence/dev-complete/SOP-009 artifact visible.

**Finding disposition:**

- **F-001 CLOSED.**
- **F-002 CLOSED.**
- **F-003 OPEN.** The S3 spec still contains the stale phrase that Gary's SSOT sha feeds the receipt's `gary_ssot_digest`, while code/tests exclude that top-level field.
- **F-004 OPEN but reduced.** Still a spec-closeout/process risk, not an observed runtime issue.
- **F-005 OPEN but reduced.** Same as F-003; test/code contract is coherent, spec prose is stale.
- **F-006 OPEN as verification-environment note.**

**Recommendations carried forward:**

1. Patch `canonical-arc-s3-gary-shadow-parity.md` before dev-complete/SOP-009 to remove or correct the `gary_ssot_digest` prose.
2. Next useful independent verification should be broader than the already-green focused core: Gary dispatch regression, additional-instructions channel, resume continuation, audit scope, import-linter, and ruff.
3. Keep AC-L pending; no live witness artifact is visible yet.

**Verdict:** `CONCUR-WITH-FINDINGS`. No new user action needed at this cadence tick; S3 remains on a good path with one stale-spec cleanup item.

### POLL-009 - SOP-009 dev-complete relay / F-003 closed (2026-07-06T20:40:26-04:00)

**Trigger:** heartbeat poll.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, still synced with origin.
- HEAD unchanged: `d049453b`.
- Canonical monitor ledger now includes **SOP-009 - S3 dev-complete independent verification**.
- S3 spec file changed since the prior poll and now corrects the SSOT-digest prose.
- Worktree still has active uncommitted S3 implementation and tests; no close commit yet.

**SOP-009 relay summary:**

- Mandatory verifications passed for F-801 and F-802.
- SOP-009 reports serial venv suites: **753 passed / 2 skipped / 4 failed**, with all 4 failures reproduced at baseline in a throwaway `d049453b` worktree and attributed to non-S3 baseline reds.
- Ruff all-pass on 16 touched/new files; lint-imports 16/0; `git diff --check` clean.
- SOP-009 findings are advisory:
  - **F-901:** AC-4 equivalence is within-tree A/B + resolver byte-identity, not cross-commit golden; judged honestly covered.
  - **F-902:** touched `.py` count is 16, not 15; close commit message should say 16.
- Story must not flip done until AC-L both-leg live PASS.

**External-monitor finding disposition:**

- **F-001 CLOSED.**
- **F-002 CLOSED.**
- **F-003 CLOSED.** The S3 spec now states the SSOT digest feeds `gary_view.ssot_digest` and surfaces via `gary_bound_guides`/`detail`, not a top-level `gary_ssot_digest`.
- **F-004 CLOSED.** The READY-FOR-DEV-with-stale-spec process risk is resolved by the spec patch and SOP-009 ratification.
- **F-005 CLOSED.** Tests/code/spec now agree on no top-level `gary_ssot_digest`.
- **F-006 OPEN as verification-environment note.** Continue using `.venv`, not bare `python`.

**Carry-forward watchpoints:**

- **F-901/F-902 are now the only monitor-visible S3 advisory findings**, inherited from SOP-009.
- AC-L remains the hard gate. It must include:
  - leg 1 matching-pick PASS with `clock_eligible: true`
  - leg 2 forced divergence by mutating a resolver-emitted field per F-806
  - cleanup receipts append, not overwrite (F-701)
  - clean git restore of the SSOT mutation
  - no story-done flip before both live legs pass

**Recommendations:**

1. Treat SOP-009 as a clean dev-complete handoff for offline S3, with AC-L and T11/remediation still ahead.
2. At SOP-010/close, verify commit integrity against the 16-file touched/new `.py` count, live evidence single-pass consistency, and that the SSOT mutation did not leak into the final worktree.
3. Keep this external ledger out of staging unless the operator explicitly wants it committed; SOP-009 already notes this monitor ledger is operator-owned/unstaged.

**Verdict:** `CONCUR-WITH-FINDINGS`. S3 offline implementation has crossed the main dev-complete bar; remaining risk is live-witness/closeout discipline.

### POLL-010 - T11 findings triaged / remediation queue visible (2026-07-06T20:50:26-04:00)

**Trigger:** heartbeat poll.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, still synced with origin.
- HEAD unchanged: `d049453b`.
- New tracked modification since prior poll: `_bmad-output/implementation-artifacts/deferred-work.md`.
- S3 story spec now includes a **Review Findings** section: T11 3-lane + SOP-009 triage = `0 decision-needed / 7 patch / 1 defer / 4 dismissed / 3 notes`.
- No close commit or AC-L evidence visible yet.

**Review findings now visible in the S3 spec:**

- **P1 (MED):** add producer-side `start_trial` test proving the real `trial-start.json` write feeds `_trial_start_directive_digest`.
- **P2 (LOW):** strict `schema_version` type gate; only `type(x) is int` is valid; bool/float/string are not v1/forward-compat.
- **P3 (LOW):** reason-keyed INFO logs for expected-ordering-gap; do not call directive drift "legacy".
- **P4 (LOW):** serialization-safe, decoupled receipt details; no aliasing live CD contribution; bounded repr for unserializable values; best-effort digests on crash fallback.
- **P5 (LOW):** warn when `trial-start.json` has present-but-empty/non-string `directive_digest`.
- **P6 (LOW):** strengthen AC-4 test canonicalizer; no `default=str`, assert Gamma calls non-empty.
- **P7 (LOW):** double-resume witness: a run already carrying a §07 receipt must not re-dispatch/re-audit; persisted receipt byte-unchanged.
- **E4 deferred:** S4 must decide whether parity clock eligibility requires full three-way attestation or whether a two-way match is acceptable. This is now routed in `deferred-work.md`.

**External-monitor finding disposition:**

- **F-001..F-005 CLOSED.**
- **F-006 OPEN as verification-environment note.**
- **F-901/F-902 remain advisory, inherited from SOP-009.**

**New findings:**

- **F-007 (material, remediation watch):** P1 is not just a test nicety. Without a producer-side `start_trial` witness, the F-801 fix can regress if `trial.py` renames/drops the persisted digest key while seam-level tests continue fabricating the expected file. P1 should be treated as the highest-value remediation patch.
- **F-008 (material, remediation watch):** P4 protects the "never raises / receipt rides persisted contribution" promise. If receipt `detail` aliases live objects or contains unserializable values, the comparator may classify correctly but persistence can still fail or mutate after capture. This is product-relevant because Gary's contribution is the operator-visible audit carrier.

**Recommendations:**

1. Remediation should prioritize P1 and P4 first, then P2/P3/P5/P6/P7.
2. After remediation, rerun the pure comparator, Gary receipt, runner seam, walk pin, resume-continuation, existing Gary dispatch regressions, ruff, and lint-imports. P4/P7 especially need persistence/resume coverage, not just unit tests.
3. Do not start AC-L until P1-P7 are closed RED-first and the story spec checkboxes are updated.
4. Carry E4 explicitly into S4; it affects when parity WARN can become fail-loud without admitting two-way/gateless evidence into the clock.

**Verdict:** `CONCUR-WITH-FINDINGS`. The review triage is healthy and concrete; S3 should remain in remediation until all seven patch items are closed and verified.

### POLL-011 - quiet cadence / remediation still pending (2026-07-06T21:00:26-04:00)

**Trigger:** heartbeat poll.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, still synced with origin.
- HEAD unchanged: `d049453b`.
- Worktree shape remains materially unchanged from POLL-010.
- No close commit, no AC-L evidence, and no new SOP-010 artifact visible.
- S3 spec still shows P1-P7 as unchecked.

**Finding disposition:**

- **F-001..F-005 CLOSED.**
- **F-006 OPEN as verification-environment note.**
- **F-007 OPEN.** P1 producer-side `start_trial` digest witness still pending.
- **F-008 OPEN.** P4 serialization-safe/decoupled receipt payload hardening still pending.
- **F-901/F-902** remain advisory from SOP-009.

**Recommendations carried forward:**

1. Keep S3 in remediation; do not proceed to AC-L until P1-P7 are patched RED-first and checkboxes updated.
2. Prioritize P1/P4 because they protect the two most product-relevant failure modes: silent producer contract drift and non-persistable/mutable audit receipts.
3. After remediation, rerun the focused-plus-regression set and then AC-L both legs.

**Verdict:** `CONCUR-WITH-FINDINGS`. No new user action needed; the monitor is waiting for remediation movement or AC-L evidence.

### POLL-012 - T11 remediation checkboxes closed / AC-L still pending (2026-07-06T21:10:26-04:00)

**Trigger:** heartbeat poll.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, still synced with origin.
- HEAD unchanged: `d049453b`.
- Worktree remains uncommitted; no S3 close commit visible yet.
- S3 story spec now marks **P1-P7 checked** and E4 deferred.
- No SOP-010 closeout artifact or AC-L live evidence visible yet.

**Remediation movement observed:**

- **P1 checked:** `tests/orchestrator/test_gary_parity_payload_seam.py` now includes `test_real_start_trial_write_feeds_the_seam_reader`, driving the real `start_trial` write and asserting `_trial_start_directive_digest(run_dir)` reads the persisted `trial-start.json` digest.
- **P2 checked:** `app/styleguide/parity.py` now gates schema claims with `type(schema_version) is int`, preserving `cd-schema-newer` only for integer versions above 1 and treating bool/float/string claims as contract violations.
- **P3 checked:** `app/specialists/gary/_act.py` now uses reason-specific `expected-ordering-gap` INFO messages, with `directive-drift` and `cd-schema-newer` no longer framed as legacy.
- **P4 checked:** `production_runner.py`, `gary/_act.py`, and `parity.py` now show the intended deep-copy / canonical-JSON / bounded-error-path hardening so receipt payloads do not alias live objects and remain persistable on comparator fallback.
- **P5 checked:** `_trial_start_directive_digest` now WARNs on malformed, non-object, non-string, or empty present digest content while preserving silent `None` for legitimate single-file trial shape.
- **P6 checked:** AC-4 canonicalization hardening is visible in `tests/specialists/gary/test_styleguide_parity_receipt.py`.
- **P7 checked:** `tests/composition/test_gary_parity_walk_pin.py` now includes a double-resume witness asserting no re-dispatch/re-audit and byte-unchanged persisted receipt.

**External-monitor finding disposition:**

- **F-001..F-005 CLOSED.**
- **F-006 OPEN as verification-environment note.** Continue using `.venv\Scripts\python.exe`; bare `python` remains the wrong interpreter for this repo.
- **F-007 CLOSED, pending normal dev verification.** The P1 producer-side `start_trial` witness is now present in code.
- **F-008 CLOSED, pending normal dev verification.** The P4 serialization-safe / decoupled receipt hardening is now present in code.
- **F-901/F-902** remain advisory from SOP-009 and must still be honored at closeout.

**Recommendations:**

1. Before AC-L, run the focused remediation battery under `.venv\Scripts\python.exe`, especially the runner seam, Gary receipt, parity comparator, and both-walk/resume tests touched by P1-P7.
2. AC-L remains the hard gate: matching-pick live PASS plus forced divergence by mutating a resolver-emitted field, with cleanup receipts appended and SSOT mutation restored cleanly.
3. SOP-010/close should verify commit integrity against the **16 touched/new `.py` files** count, not 15, and should cite live evidence single-pass consistency.

**Verdict:** `CONCUR-WITH-FINDINGS`. Remediation appears materially complete on inspection; S3 should not flip done until focused verification and both AC-L live legs pass.

### POLL-013 - AC-L evidence pack started / verdict pending (2026-07-06T21:20:26-04:00)

**Trigger:** heartbeat poll.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, still synced with origin.
- HEAD unchanged: `d049453b`; no close commit yet.
- Worktree remains active with the S3 implementation, spec, and tests uncommitted.
- New untracked evidence directory is present: `_bmad-output/implementation-artifacts/evidence/s3-acl-liveproof-20260707T011735Z/`.

**AC-L evidence status:**

- Evidence pack contains prewritten `judge1.py` and `judge2.py`, plus leg-1 driver scripts and logs.
- Leg 1 has started with trial id `a18c2a86-bbdb-48a2-ba63-fb1a653bfaf9`; the driver log records the scripted selection-code path and real `start_trial` launch.
- A repo `.venv` Python process for the leg is still running at poll time, and `walk-log-leg1.txt` is still receiving live HTTP request entries.
- No `leg1-start-result.json`, `leg1-resume-result.json`, judge output, leg-2 state/result, or PASS/FAIL verdict is visible yet.
- `state/config/gamma-style-guides.yaml` has no visible git diff at this poll, so there is no evidence yet of an un-restored leg-2 SSOT mutation.

**Finding disposition:**

- **F-001..F-005 CLOSED.**
- **F-006 OPEN as verification-environment note.** The active live leg is running under the repo `.venv`, which is the correct interpreter family for this repo.
- **F-007 CLOSED, pending normal dev verification.**
- **F-008 CLOSED, pending normal dev verification.**
- **F-901/F-902** remain closeout advisories.

**Recommendations:**

1. Treat AC-L as **in progress**, not passed. Do not flip S3 done until both judge scripts produce first-run PASS evidence for leg 1 and leg 2.
2. At the next poll, verify leg-1 result JSON plus judge output before accepting the matching-pick PASS claim.
3. For leg 2, specifically verify `resolution-mismatch`, WARN log capture, equal directive digests, both receipt envelopes, and clean restoration of `state/config/gamma-style-guides.yaml`.

**Verdict:** `MONITORING-IN-PROGRESS`. AC-L appears to have started correctly, but no live PASS evidence is complete yet.

### POLL-014 - AC-L leg 1 attempted / live proof blocked (2026-07-06T21:30:26-04:00)

**Trigger:** heartbeat poll.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, still synced with origin.
- HEAD unchanged: `d049453b`; no S3 close commit.
- Worktree now includes AC-L side effects:
  - `state/config/gamma-styleguide-picks.jsonl` has one new live pick event for trial `a18c2a86-bbdb-48a2-ba63-fb1a653bfaf9`.
  - A live run directory exists for the same trial.
  - The evidence pack has leg-1 start/resume results plus leg-2 preparation scripts, but no judge verdict files.

**AC-L evidence status:**

- Leg 1 phase 1 succeeded: real `start_trial` returned `paused-at-gate` after 142s, with directive digest `75271c67b7b74fd8ade4d44c08aabe7791c2e2f87a395476cec4e0fe34ad2453`.
- Leg 1 phase 2 did **not** produce the required matching-pick PASS. `leg1-resume-result.json` records `resume_status: paused-at-error` and `paused_error_tag: gamma.export.brief-unmatched`.
- `walk-log-leg1.txt` shows four Gamma generations/downloads total: initial attempt plus auto-retries 1/3, 2/3, and 3/3. The final error is `gamma export left briefed slide(s) unmatched for variant A: ['slide-07']; unmatched pages: ['Technologys-Promise-Requires-Clinical-Innovators']`.
- No `JUDGE-1 VERDICT: PASS` is visible; `judge1.py` exists but has not produced a passing verdict artifact.
- Leg 2 has not produced `leg2-state.json`, `leg2-prepare-result.json`, `leg2-recover-result.json`, walk log, or judge verdict yet.
- `state/config/gamma-style-guides.yaml` has no visible diff at this poll; no leaked leg-2 SSOT mutation is visible.

**Finding disposition:**

- **F-001..F-005 CLOSED.**
- **F-006 OPEN as verification-environment note.**
- **F-007 CLOSED, pending normal dev verification.**
- **F-008 CLOSED, pending normal dev verification.**
- **F-009 OPEN (AC-L blocker):** first AC-L leg-1 live attempt did not reach the required parity receipt / judge PASS because Gary/Gamma paused at `gamma.export.brief-unmatched` after exhausting automatic retries. This is not evidence against the S3 comparator itself, but it means the live AC-L gate is **not met**.
- **F-901/F-902** remain closeout advisories.

**Recommendations:**

1. Do not mark S3 done or claim AC-L passed from this evidence pack.
2. Preserve this failed live attempt honestly in the evidence trail; if a later attempt is run, label it as a subsequent attempt/recovery rather than overwriting the first-run outcome.
3. Before continuing leg 2, decide whether the `gamma.export.brief-unmatched` failure is an unrelated Gamma/export variance or a content/briefing mismatch worth a narrow product fix. Do not broaden S3 beyond the Marcus-SPOC parity goal just to make proofing mechanics easier.
4. Any eventual closeout must account for the new pick sidecar row and live run artifacts explicitly, plus the 16 touched/new `.py` count from F-902.

**Verdict:** `BLOCKED-ON-AC-L`. S3 remediation is still materially complete, but the required live PASS has not been achieved.

### POLL-015 - AC-L recover also failed / matcher fix landed, no new verdict yet (2026-07-06T21:40:27-04:00)

**Trigger:** heartbeat poll.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, still synced with origin.
- HEAD unchanged: `d049453b`; no S3 close commit.
- Worktree has expanded since the AC-L failure:
  - New/modified matcher surface: `skills/gamma-api-mastery/scripts/gamma_operations.py`.
  - New focused tests: `tests/specialists/gary/test_gamma_title_matching.py`.
  - Planning/governance artifacts now include updates to `deferred-inventory.md` and the green-light party record.
- The AC-L evidence pack now includes `PROOF.md`, `leg1_recover.py`, and `leg1-recover-result.json`.

**AC-L evidence status:**

- The documented single `trial recover` after the original leg-1 error also ended `paused-at-error` with `paused_error_tag: gamma.export.brief-unmatched`.
- `driver-log-leg1.txt` records:
  - attempt 1 resume: `paused-at-error`, `gamma.export.brief-unmatched`
  - attempt 2 recover: `paused-at-error`, `gamma.export.brief-unmatched`
- `walk-log-leg1.txt` shows the recover attempt repeated the same failure after another four Gamma generations/downloads.
- `PROOF.md` identifies the deterministic title matcher defect: brief title `Technology's Promise Requires Clinical Innovators` normalized as `technology s ...`, while Gamma export slug `Technologys-Promise-Requires-Clinical-Innovators` normalizes as `technologys ...`; containment fails.
- The working-tree fix deletes/joins a pinned apostrophe family in `normalize_title`, and tests pin the live pair, enumerated apostrophe variants, collision ambiguity, and deletion-not-space behavior.
- No `JUDGE-1 VERDICT: PASS`, `leg2-state.json`, leg-2 result, or `JUDGE-2 VERDICT` is visible yet.
- `state/config/gamma-style-guides.yaml` still has no visible diff; no leaked leg-2 SSOT mutation is visible.

**Finding disposition:**

- **F-001..F-005 CLOSED.**
- **F-006 OPEN as verification-environment note.**
- **F-007 CLOSED, pending normal dev verification.**
- **F-008 CLOSED, pending normal dev verification.**
- **F-009 OPEN (AC-L blocker):** leg 1 still has no live PASS. The first resume and the documented recover both halted at `gamma.export.brief-unmatched`.
- **F-010 OPEN (product-defect watch):** the AC-L run surfaced a real Marcus-SPOC production matcher defect in Gamma export title binding. The current fix appears appropriately product-scoped, not proofing-only, because it hardens deterministic matching of apostrophe-bearing titles in the production export path. It still needs RED-first verification and then a post-fix live recover/pass.
- **F-901/F-902** remain closeout advisories.

**Recommendations:**

1. Keep S3 blocked on AC-L until a post-fix live recover produces frozen-judge PASS evidence for leg 1, then leg 2 produces its forced-divergence PASS.
2. Treat the apostrophe matcher patch as a legitimate production fix if the focused test proves RED-before-GREEN or the review record captures the live failure as the RED witness; do not broaden it into a proofing-only accommodation.
3. Before closeout, verify the matcher fix does not weaken ambiguity/fail-loud behavior; the new collision test is the right guard to keep.
4. Preserve both failed live attempts in the evidence trail. A later post-fix recover should be recorded as post-remediation recovery, not first-run PASS.

**Verdict:** `BLOCKED-ON-AC-L`. The root cause is now narrowed and a product-scoped fix is visible, but the live gate is still unmet.

### POLL-016 - matcher fix committed locally / AC-L still not re-proven (2026-07-06T21:50:27-04:00)

**Trigger:** heartbeat poll.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, now **ahead of origin by 1**.
- New local HEAD: `59a9a48a fix(gamma-matcher): apostrophe-family deletion in normalize_title — party-ratified frozen-contract amendment (§10)`.
- This is a matcher-fix commit, not the S3 close commit.
- `59a9a48a` contains six files:
  - `_bmad-output/implementation-artifacts/deferred-work.md`
  - `_bmad-output/implementation-artifacts/spec-storyboard-correctness-cover-shift.md`
  - `_bmad-output/planning-artifacts/canonical-production-conversation-arc-greenlight-party-record-2026-07-06.md`
  - `_bmad-output/planning-artifacts/deferred-inventory.md`
  - `skills/gamma-api-mastery/scripts/gamma_operations.py`
  - `tests/specialists/gary/test_gamma_title_matching.py`
- The S3 implementation and live artifacts remain uncommitted in the worktree.

**AC-L evidence status:**

- Evidence pack has not advanced since the failed pre-fix recover:
  - latest leg-1 result remains `leg1-recover-result.json`
  - no `JUDGE-1 VERDICT: PASS`
  - no `leg2-state.json`, `leg2-prepare-result.json`, `leg2-recover-result.json`, or `JUDGE-2 VERDICT`
- `driver-log-leg1.txt` still ends with the second failed leg-1 recover at `gamma.export.brief-unmatched`.
- No fresh post-fix AC-L driver output is visible at this poll.
- No active repo-venv live leg process is visible beyond older/background Python processes.

**Finding disposition:**

- **F-001..F-005 CLOSED.**
- **F-006 OPEN as verification-environment note.**
- **F-007 CLOSED, pending normal dev verification.**
- **F-008 CLOSED, pending normal dev verification.**
- **F-009 OPEN (AC-L blocker):** unchanged. Leg 1 still lacks frozen-judge PASS evidence.
- **F-010 PARTIALLY CLOSED:** the product-scoped apostrophe matcher fix is now committed locally with focused tests and governance notes. It remains **open for live confirmation** because the post-fix recover/pass has not run or has not produced evidence yet.
- **F-901/F-902** remain closeout advisories.

**Recommendations:**

1. Do not treat `59a9a48a` as S3 completion; it removes the blocker cause but does not satisfy AC-L.
2. Next required evidence is a post-fix leg-1 recovery/run that reaches the frozen `judge1.py` PASS, followed by leg 2 forced-divergence PASS.
3. At S3 closeout, explicitly separate the matcher hotfix commit from the S3 parity implementation commit/evidence trail, since the former was discovered by AC-L but is not itself the S3 deliverable.

**Verdict:** `BLOCKED-ON-AC-L`. The blocker fix is committed locally; the live gate remains unmet until post-fix judge evidence appears.

### POLL-017 - post-fix leg 1 reached G2B / judge + leg 2 still pending (2026-07-06T22:00:27-04:00)

**Trigger:** heartbeat poll.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, now synced with origin at `59a9a48a`.
- HEAD remains the matcher hotfix commit: `fix(gamma-matcher): apostrophe-family deletion in normalize_title — party-ratified frozen-contract amendment (§10)`.
- No S3 parity close commit or SOP-010 closeout is visible.
- The S3 implementation and AC-L side effects remain active/uncommitted in the worktree.

**AC-L evidence status:**

- New post-fix evidence appeared after POLL-016:
  - `leg1_recover2.py`
  - `leg1-recover2-result.json`
  - updated `driver-log-leg1.txt`
  - updated `walk-log-leg1.txt`
- Post-fix leg-1 recovery ran through fixed matcher commit `59a9a48a` and returned cleanly:
  - `recover_status: paused-at-gate`
  - `paused_gate: G2B`
  - `paused_error_tag: null`
  - elapsed 94s
- Persisted run `state/config/runs/a18c2a86-bbdb-48a2-ba63-fb1a653bfaf9/run.json` now records a Gary `styleguide_parity` receipt with:
  - `outcome: ok`
  - `reason: match`
  - `clock_eligible: true`
  - equal `trial_start_directive_digest`, `cd_directive_digest`, and `gary_directive_digest`: `75271c67b7b74fd8ade4d44c08aabe7791c2e2f87a395476cec4e0fe34ad2453`
  - matching CD/Gary resolution digests
- The run is now `paused-at-gate` at `G2B` with no paused error tag.
- Formal judge evidence is still missing: only `judge1.py` and `judge2.py` are present; no captured `JUDGE-1 VERDICT: PASS` output file is visible.
- Leg 2 has not started materially: only `leg2_prepare.py` and `leg2_recover.py` exist; no `leg2-state.json`, `leg2-prepare-result.json`, `leg2-recover-result.json`, leg-2 walk log, or `JUDGE-2 VERDICT` is visible.
- `state/config/gamma-style-guides.yaml` still has no visible diff; no leaked forced-divergence SSOT mutation is visible.

**Finding disposition:**

- **F-001..F-005 CLOSED.**
- **F-006 OPEN as verification-environment note.**
- **F-007 CLOSED, pending normal dev verification.**
- **F-008 CLOSED, pending normal dev verification.**
- **F-009 PARTIALLY CLOSED:** leg 1 now has the substantive persisted receipt facts required for matching-pick PASS after the matcher fix, but the frozen judge PASS artifact is not present and leg 2 is not run. Keep AC-L open.
- **F-010 CLOSED for code fix, pending final AC-L confirmation:** matcher hotfix is committed/synced and the post-fix leg-1 recover validates the original blocker path. The remaining live gate is S3 AC-L completion, not the matcher defect itself.
- **F-901/F-902** remain closeout advisories.

**Recommendations:**

1. Capture or run the frozen `judge1.py` verdict against the now-clean leg-1 run so the evidence pack has the formal PASS artifact, not just the underlying receipt facts.
2. Proceed to leg 2 only after preserving the leg-1 post-fix recovery chronology: first two failed attempts, matcher hotfix `59a9a48a`, then clean recovery.
3. For leg 2, verify `resolution-mismatch`, WARN log capture, equal directive digests, both envelopes in the receipt, clean `G2B` pause, and clean restoration of `state/config/gamma-style-guides.yaml`.

**Verdict:** `AC-L-IN-PROGRESS`. Leg 1 appears substantively recovered and matching, but S3 is not done until judge output and leg 2 PASS evidence exist.

### POLL-018 - quiet cadence / AC-L still waiting on judge + leg 2 (2026-07-06T22:10:27-04:00)

**Trigger:** heartbeat poll.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, still synced with origin at `59a9a48a`.
- No new commit since the matcher hotfix.
- No SOP-010 closeout or S3 parity close commit visible.
- S3 implementation, live pick sidecar row, and AC-L evidence/run artifacts remain active in the worktree.

**AC-L evidence status:**

- Evidence pack is unchanged since POLL-017.
- Leg 1 remains substantively recovered after matcher hotfix `59a9a48a`:
  - `leg1-recover2-result.json` records `paused-at-gate`, `paused_gate: G2B`, `paused_error_tag: null`.
  - persisted Gary receipt still has `ok/match`, `clock_eligible: true`, and equal trial/CD/Gary directive digests.
- Formal frozen-judge evidence is still missing:
  - no captured `JUDGE-1 VERDICT: PASS`
  - no `leg2-state.json`
  - no `leg2-prepare-result.json`
  - no `leg2-recover-result.json`
  - no `JUDGE-2 VERDICT`
- `state/config/gamma-style-guides.yaml` still has no visible diff; no leaked leg-2 forced-divergence mutation is visible.

**Finding disposition:**

- **F-001..F-005 CLOSED.**
- **F-006 OPEN as verification-environment note.**
- **F-007 CLOSED, pending normal dev verification.**
- **F-008 CLOSED, pending normal dev verification.**
- **F-009 PARTIALLY CLOSED:** leg 1 has the substantive persisted match receipt, but AC-L remains open until judge evidence plus leg 2 PASS exist.
- **F-010 CLOSED for code fix, pending final AC-L confirmation.**
- **F-901/F-902** remain closeout advisories.

**Recommendations carried forward:**

1. Capture the frozen `judge1.py` PASS output for the recovered leg-1 run.
2. Run leg 2 forced-divergence and verify `resolution-mismatch`, WARN log capture, equal directive digests, both envelopes, clean gate pause, and clean SSOT restoration.
3. Do not flip S3 done or produce SOP-010 until both AC-L legs have formal PASS evidence.

**Verdict:** `AC-L-IN-PROGRESS`. No new user action needed; the monitor is waiting for judge/leg-2 evidence.

### POLL-019 - quiet cadence / no AC-L movement since leg-1 recovery (2026-07-06T22:20:27-04:00)

**Trigger:** heartbeat poll.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, still synced with origin at `59a9a48a`.
- No new commits since the matcher hotfix.
- No SOP-010 closeout or S3 parity close commit visible.
- Worktree shape is materially unchanged from POLL-018.

**AC-L evidence status:**

- Evidence directory remains unchanged since the post-fix leg-1 recovery.
- Leg 1 still has substantive recovery evidence:
  - `leg1-recover2-result.json` records clean `paused-at-gate` at `G2B`.
  - persisted Gary receipt remains `ok/match`, `clock_eligible: true`, with equal trial/CD/Gary directive digests.
- Still missing:
  - captured `JUDGE-1 VERDICT: PASS`
  - `leg2-state.json`
  - `leg2-prepare-result.json`
  - `leg2-recover-result.json`
  - leg-2 walk log
  - `JUDGE-2 VERDICT`
- No `state/config/gamma-style-guides.yaml` diff is visible; no leaked leg-2 SSOT mutation is visible.

**Finding disposition:**

- **F-001..F-005 CLOSED.**
- **F-006 OPEN as verification-environment note.**
- **F-007 CLOSED, pending normal dev verification.**
- **F-008 CLOSED, pending normal dev verification.**
- **F-009 PARTIALLY CLOSED:** leg 1 has substantive persisted match evidence, but formal AC-L remains incomplete.
- **F-010 CLOSED for code fix, pending final AC-L confirmation.**
- **F-901/F-902** remain closeout advisories.

**Recommendations carried forward:**

1. Add/capture the frozen judge-1 PASS artifact for leg 1.
2. Run leg 2 forced-divergence and capture judge-2 PASS.
3. Keep S3 open until both formal AC-L PASS artifacts exist and SOP-010 verifies closeout hygiene.

**Verdict:** `AC-L-IN-PROGRESS`. No new user action needed; waiting for formal judge and leg-2 evidence.

### POLL-020 - S3 close commit / AC-L both legs PASS (2026-07-06T22:30:27-04:00)

**Trigger:** heartbeat poll.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, now **ahead of origin by 1**.
- New local HEAD: `7630d091 feat(canonical-arc-S3): Gary shadow-parity receipt — LIVE-PROVEN both legs (ok/match + forced-divergence WARN)`.
- Prior matcher hotfix `59a9a48a` remains in history and is now the parent of the S3 close commit.
- Worktree after the close commit is clean for the S3 tracked surfaces; remaining untracked items are operator/external monitor ledgers, workbook artifacts, and the untracked live run directory.
- `state/config/gamma-style-guides.yaml` has no diff; leg-2 SSOT mutation was restored.
- `state/config/gamma-styleguide-picks.jsonl` has one committed live pick event from leg 1, recorded as product provenance.

**S3 closeout / commit integrity:**

- Close commit includes the S3 implementation, S3 spec, canonical monitor update, AC-L evidence pack, live pick sidecar row, and focused/regression tests.
- Commit message explicitly records **RED-first dev (16 `.py` files, F-902)**; total committed Python file count is 24 because the evidence pack also includes 8 driver/judge scripts.
- `canonical-arc-s3-gary-shadow-parity.md` now marks status **DONE** and records the full gate chain.
- `canonical-arc-claude-shadow-monitor-2026-07-06.md` now includes the S3 T11 remediation + AC-L live witness relay and points next to SOP-010 at close commit.

**AC-L evidence status:**

- Evidence pack: `_bmad-output/implementation-artifacts/evidence/s3-acl-liveproof-20260707T011735Z/`.
- `PROOF.md` records both legs pass and the validity protocol: judges frozen before legs, executed verbatim once each, real OpenAI/Gamma spend, `.venv` interpreter, stand-down/GO chronology for the matcher defect.
- **Leg 1 PASS:** `judge1-output.txt` records **JUDGE-1 VERDICT: PASS (0 failing: [])**, 13 assertions passing:
  - Gary contribution and receipt present
  - `outcome: ok`
  - `reason: match`
  - `clock_eligible: true`
  - `cd_status: resolved`
  - three directive digests non-null/equal and matching on-disk `trial-start.json`
  - CD contribution present, bound guide exactly `hil-2026-apc-crossroads-classic`
  - run paused cleanly at `G2B`
- **Leg 2 PASS:** `judge2-output.txt` records **JUDGE-2 VERDICT: PASS (0 failing: [])**, 10 assertions passing:
  - `outcome: divergence`
  - `reason: resolution-mismatch`
  - `detail` carries both `cd_block` and `gary_view`
  - three directive digests non-null/equal
  - CD/Gary resolution digests differ
  - WARN line captured in `walk-log-leg2.txt`
  - run did not halt; paused cleanly at `G2B`
- Leg 2 used rewind-recover trial `4d465677-188c-401c-ae37-1acb19658db0`, mutated resolver-emitted `prompt_configuration.text_content.amount: minimal -> concise`, then restored SSOT cleanly.

**Finding disposition:**

- **F-001..F-005 CLOSED.**
- **F-006 CLOSED for this story.** Closeout evidence and commit message use the repo `.venv` path/protocol; no bare-`python` verification issue remains for S3.
- **F-007 CLOSED.** P1 producer-side `start_trial` witness landed and S3 AC-L attested the real `trial-start.json` digest.
- **F-008 CLOSED.** P4 serialization-safe/decoupled receipt hardening landed and live receipts persisted through both legs.
- **F-009 CLOSED.** AC-L both legs now have formal frozen-judge PASS artifacts.
- **F-010 CLOSED.** The production matcher defect was fixed separately at `59a9a48a`, then the post-fix leg-1 recovery and judge PASS confirmed the product path.
- **F-901 CLOSED.** AC-4 equivalence note was recorded honestly; leg 1 provides the de-facto live cross-version confirmation.
- **F-902 CLOSED.** Close commit message explicitly records 16 `.py` dev files; evidence scripts explain the larger total Python count.

**Recommendations:**

1. Treat S3 as complete locally and live-proven.
2. Push `7630d091` when the operator is ready; origin currently lacks the S3 close commit.
3. Keep the external monitor ledger untracked unless the operator explicitly wants this independent shadow report committed.
4. Next story should respect the deferred E4/S4 decision: whether fail-loud parity eligibility requires full three-way attestation or two-way/gateless match can count.

**Verdict:** `CONCUR-CLOSED`. S3 is DONE locally: implementation, remediation, both AC-L live legs, and close commit are present.

### POLL-021 - SOP-010 relayed / S4 unblocked / push-state mismatch noted (2026-07-06T22:40:27-04:00)

**Trigger:** heartbeat poll.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, still **ahead of origin by 1**.
- HEAD remains `7630d091 feat(canonical-arc-S3): Gary shadow-parity receipt — LIVE-PROVEN both legs (ok/match + forced-divergence WARN)`.
- Origin still points at `59a9a48a`; the S3 close commit is not pushed from this local view.
- New tracked modifications after the S3 close commit:
  - `_bmad-output/implementation-artifacts/canonical-arc-claude-shadow-monitor-2026-07-06.md`
  - `docs/project-context.md`
- Remaining untracked items are external/operator monitor ledgers, workbook artifacts, and the untracked live run directory.

**SOP-010 relay:**

- Canonical monitor ledger now includes **SOP-010 — S3 story-close audit**.
- SOP-010 reports commit integrity clean for both commits:
  - `59a9a48a`: ratified 6-file matcher/governance set.
  - `7630d091`: exact S3 set; **16 dev `.py` files counted (F-902 honored)** + story + ledger + 27-file evidence pack + sidecar = 46 files.
- SOP-010 reverified:
  - F-802 fence holds: zero `pipeline-manifest` / `package_builders` changes.
  - sidecar is exactly one appended event; prior events byte-intact.
  - post-commit green reproduced: 215/215 touched-surface serial, lint-imports 16/0, ruff 0-new.
  - live evidence timeline: judges frozen before legs; no judge output predates matcher fix; both pre-fix attempts failed unjudged; both AC-L legs pass after the fix.
  - mutation hygiene clean: SSOT byte-identical to baseline after restore.
- SOP-010 findings are advisory:
  - F-1001: `PROOF.md` approximate `~02:19` timestamp vs authoritative 02:22 stamps.
  - F-1002: pre-existing 18 ruff findings in `gamma_operations.py`; recommended for next touch.
- SOP-010 verdict: **S3 DONE STANDS; S4 UNBLOCKS.**

**New monitor finding:**

- **F-1003 OPEN (wrap-up doc mismatch):** `docs/project-context.md` adds a session-17 update saying branch `dev/workbook-2026-07-06` is at `7630d091` “(+wrapup; pushed)”, but current `git status` shows `[ahead 1]` and `origin/dev/workbook-2026-07-06` remains at `59a9a48a`. This is a documentation/push-state mismatch, not an S3 code/evidence defect.

**Finding disposition:**

- **F-001..F-010 CLOSED.**
- **F-901/F-902 CLOSED.**
- **F-1001/F-1002 advisory accepted in SOP-010.**
- **F-1003 OPEN** until either `7630d091` is pushed or the wrap-up wording stops saying pushed.

**Recommendations:**

1. Treat S3 as complete and S4 unblocked, per SOP-010.
2. Push `7630d091` before relying on docs that say the branch is pushed, or amend the wrap-up wording.
3. For S4 SOP-011, verify the four carried obligations: E4 clock-attestation decision, S4 scope against §7, F-705 WARN-seed ownership transfer with byte-diff witness, and §10 deferred filings staying filed.

**Verdict:** `CONCUR-CLOSED-WITH-WRAPUP-NIT`. S3 is done locally and verified; only push-state/documentation alignment remains.

### POLL-022 - S4 kickoff / goal loaded, no canonical S4 spec artifact yet (2026-07-06T22:45:00-04:00)

**Trigger:** operator update: Claude agents have begun S4 work; monitor should continue.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, now synced with origin at `13792617`.
- Latest commit: `13792617 docs(session-17): WRAPUP — canonical-arc S3 CLOSED live-proven both legs; matcher contract amended §10; S4 unblocked (Class S)`.
- S3 close commit `7630d091` is now pushed via the wrap-up commit; the prior push-state mismatch is resolved.
- Remaining visible untracked items:
  - `_bmad-output/artifacts/workbooks-test/`
  - the external/workbook `claude-shadow-monitor-*` ledgers
  - `goal-canonical-arc-s4-onward-2026-07-07.txt`
  - `runs/a18c2a86-bbdb-48a2-ba63-fb1a653bfaf9/`

**S4 frame now active:**

- Active goal statement confirms canonical S4 scope:
  - `canonical-arc-s4-fail-loud-flip.md`
  - Gary `DEFAULT_VARIANT_PAIR` WARN-seed becomes a hard failure.
  - Parity `divergence` WARN becomes ERROR.
  - Authority S-flip remains deferred; S-flip parity clock is only tick 1.
- S4 spec must satisfy the four SOP-011 obligations:
  1. explicitly weigh E4: whether S-flip clock eligibility requires full three-way attestation or whether two-way/gateless match can count
  2. match party-record §7 S4 scope and cite committed v1 `styleguide_parity` receipt schema as input contract
  3. transfer F-705 WARN-seed ownership to S4 with a planned byte-diff witness
  4. keep §10 deferred filings filed, not silently absorbed
- The older `_bmad-output/implementation-artifacts/spec-braid-s4-marcus-capability-overlay.md` is a different Braid-arc S4 and is **not** the current canonical-production S4.

**Current artifact status:**

- No new `canonical-arc-s4-fail-loud-flip.md` artifact is visible yet.
- No S4 implementation diffs are visible yet.
- No S4 evidence directory, review section, or dev-complete marker is visible yet.
- `canonical-arc-claude-shadow-monitor-2026-07-06.md` already carries SOP-010 and says next poll is SOP-011 at S4 spec pre-dispatch.

**Finding disposition:**

- **F-001..F-010 CLOSED.**
- **F-901/F-902 CLOSED.**
- **F-1001/F-1002 advisory accepted in SOP-010.**
- **F-1003 CLOSED.** Branch is now synced at wrap-up commit `13792617`; docs saying S3 was pushed are consistent again.
- **F-1101 OPEN (S4 kickoff watch):** no canonical S4 spec artifact is visible yet, so the monitor cannot verify the SOP-011 obligations. Watch for the first `canonical-arc-s4-fail-loud-flip.md` draft and run pre-dispatch review before dev proceeds.

**Recommendations:**

1. Before S4 dev dispatch, require the new S4 spec to make the E4 clock-attestation decision explicit. This is the main design-risk item because fail-loud eligibility can accidentally admit weaker two-way/gateless evidence.
2. The S4 spec should include a byte-diff witness for the WARN-seed flip, not just behavioral tests, because S3 explicitly preserved that seed text/behavior for S4 ownership.
3. Keep §10 retry-taxonomy and runs-root split as deferred filings unless S4 truly needs them; absorbing them silently would broaden S4 beyond the FAIL-LOUD flip.

**Verdict:** `S4-KICKOFF-MONITORING`. S3 is closed/pushed; current monitor is waiting for the canonical S4 spec pre-dispatch artifact.

### POLL-023 - S4 kickoff quiet poll / no canonical spec yet (2026-07-06T22:51:28-04:00)

**Trigger:** heartbeat poll at `2026-07-07T02:51:28.147Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with origin at `13792617`.
- Latest commit remains `13792617 docs(session-17): WRAPUP - canonical-arc S3 CLOSED live-proven both legs; matcher contract amended §10; S4 unblocked (Class S)`.
- No tracked production/spec/test diffs are visible.
- Remaining visible untracked items are the expected strays: `_bmad-output/artifacts/workbooks-test/`, the `claude-shadow-monitor-*` ledgers, `goal-canonical-arc-s4-onward-2026-07-07.txt`, and `runs/a18c2a86-bbdb-48a2-ba63-fb1a653bfaf9/`.

**S4 artifact status:**

- No canonical `canonical-arc-s4-fail-loud-flip.md` spec artifact is visible yet.
- No S4 READY-FOR-DEV, SOP-011 pre-dispatch response, S4 dev-complete, S4 review, or live-witness evidence artifact is visible yet.
- The active S4 goal is visible in `goal-canonical-arc-s4-onward-2026-07-07.txt` and echoed by `next-session-start-here.md`.
- The existing Braid-arc S4 artifact remains out of scope for canonical-production S4.

**Finding disposition:**

- **F-001..F-010 CLOSED.**
- **F-901/F-902 CLOSED.**
- **F-1001/F-1002 advisory accepted in SOP-010.**
- **F-1003 CLOSED.**
- **F-1101 OPEN (S4 kickoff watch):** unchanged. No canonical S4 spec exists yet, so the monitor still cannot verify the four SOP-011 obligations before dev dispatch.

**Recommendations:**

1. Do not dispatch S4 substrate dev until the canonical S4 spec exists and explicitly satisfies all four SOP-011 obligations.
2. Keep the S4 scope narrow: fail-loud conversion for Gary's WARN-seed and parity WARN-to-ERROR, while the authority S-flip remains deferred at clock tick 1.
3. Treat the older Braid S4 artifact as irrelevant to this canonical arc unless Marcus explicitly cross-references it as non-authoritative background.

**Verdict:** `NO-NEW-S4-ARTIFACT-YET`. Monitoring remains active; first substantive review is blocked on the canonical S4 spec appearing.

### POLL-024 - SOP-011 S4 spec pre-dispatch review (2026-07-06T23:01:28-04:00)

**Trigger:** heartbeat poll at `2026-07-07T03:01:28.281Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, still synced with origin at `13792617`.
- Latest commit remains `13792617 docs(session-17): WRAPUP - canonical-arc S3 CLOSED live-proven both legs; matcher contract amended §10; S4 unblocked (Class S)`.
- No tracked production/spec/test diffs are visible.
- New untracked S4 artifact is now present: `_bmad-output/implementation-artifacts/canonical-arc-s4-fail-loud-flip.md` (READY-FOR-DEV; authored session 18; says it awaits SOP-011 before dev dispatch).
- Known untracked strays remain visible and must stay excluded from commits: `_bmad-output/artifacts/workbooks-test/`, the external/workbook `claude-shadow-monitor-*` ledgers, `goal-canonical-arc-s4-onward-2026-07-07.txt`, and `runs/a18c2a86-bbdb-48a2-ba63-fb1a653bfaf9/`.

**SOP-011 obligation check against the S4 spec:**

1. **E4 defer weighed:** PASS. The spec explicitly records the question, rejects a three-way prerequisite for S4 ERROR firing, adopts "TWO-WAY SUFFICES" for S4 fail-loud control, and keeps the three-way clock-strength decision deferred to S-flip. This is a clear design ruling, not an implicit omission.
2. **Scope equals party-record §7 S4 row + committed receipt schema cited:** PASS. The scope is exactly two action flips: Gary `DEFAULT_VARIANT_PAIR` WARN-seed to hard failure, and parity `divergence` WARN/proceed to ERROR. The spec keeps the authority S-flip deferred and cites the committed `app/styleguide/parity.py` 13-key receipt shape as the frozen input contract.
3. **F-705 ownership transfer + byte-diff witness planned:** PASS. The spec formally says S4 now owns the WARN-seed and AC-2 requires the localized byte-diff witness: WARN log absent, pinned raise tag present, `DEFAULT_VARIANT_PAIR` still defined, and success-path bytes untouched.
4. **§10 deferred filings stay FILED:** PASS. The retry taxonomy and runs-root split remain explicitly out of scope. The spec only pins that the two new tags are non-retryable deterministic error-pauses; it does not absorb the taxonomy overhaul.

**Code-grounding spot checks:**

- `app/specialists/gary/_act.py` still has the styleguide-less WARN-seed branch at the current `_normalized_gamma_settings` else branch, so Flip A is real and RED-firstable.
- `_styleguide_parity_receipt` still logs `divergence` as observability-only and `generate_gamma_variants` proceeds after receipt creation, so Flip B is real and RED-firstable.
- `generate_gamma_variants` computes normalized settings and parity before the variant dispatch loop, so both planned raises are positioned pre-spend if implemented at the cited sites.
- `app/styleguide/parity.py` currently exposes the 13-key receipt body the spec cites: `schema_version`, `outcome`, `reason`, `cd_status`, `clock_eligible`, the five digest fields, bound-guide fields, and `detail`.
- `app/marcus/orchestrator/production_runner.py` retry handling is allowlist-based (`_RETRYABLE_DISPATCH_TAGS`); the new S4 tags will be non-retryable unless someone wrongly adds them to that allowlist.

**Finding disposition:**

- **F-001..F-010 CLOSED.**
- **F-901/F-902 CLOSED.**
- **F-1001/F-1002 advisory accepted in SOP-010.**
- **F-1003 CLOSED.**
- **F-1101 CLOSED.** The canonical S4 spec now exists and discharges the four SOP-011 obligations at spec level.
- **F-1102 OPEN (procedural gate watch):** the spec says READY-FOR-DEV and awaits SOP-011, but this repo poll does not show a separate Marcus/party green-light or a canonical-monitor SOP-011 relay entry yet. Before substrate dev dispatch, Claude should relay this SOP-011 result verbatim into its canonical monitor flow and record the BMAD/Marcus gate decision, so the user-provided "BMAD-first / Marcus orchestrates" boundary is visible in the close trail.

**Recommendations:**

1. Approve S4 dev dispatch **after** the orchestrator relays this SOP-011 poll and records the BMAD/Marcus green-light. The spec obligations themselves are satisfied.
2. During dev, keep `app/styleguide/parity.py` byte-frozen. Any comparator, schema, or `clock_eligible` edit is an S-flip re-scope, not S4.
3. T11 should inspect especially for accidental addition of the new tags to `_RETRYABLE_DISPATCH_TAGS`, because that would silently violate the fail-loud intent while many unit tests could still pass.
4. Live AC-L must prove three legs, not just the two fail-loud teeth: no-pick fail-loud, parity-divergence fail-loud, and a valid-pick happy path that still dispatches a real deck.

**Verdict:** `CONCUR-WITH-PROCEDURAL-WATCH`. S4 spec is fit for dev dispatch on substance; do not cross the dev gate until the SOP-011 relay and BMAD/Marcus gate record are visible to the Claude lane.

### POLL-025 - SOP-011 relayed / S4 dev dispatch cleared, no code diff yet (2026-07-06T23:11:28-04:00)

**Trigger:** heartbeat poll at `2026-07-07T03:11:28.448Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, still synced with origin at `13792617`.
- No new commits since session-17 wrap-up.
- Tracked working-tree changes are currently documentation/governance only:
  - `_bmad-output/implementation-artifacts/canonical-arc-claude-shadow-monitor-2026-07-06.md`
  - `_bmad-output/planning-artifacts/deferred-inventory.md`
- S4 spec remains untracked at `_bmad-output/implementation-artifacts/canonical-arc-s4-fail-loud-flip.md`.
- No production code or test diffs are visible yet.
- Known untracked strays remain visible and must stay excluded from commits: `_bmad-output/artifacts/workbooks-test/`, the external/workbook `claude-shadow-monitor-*` ledgers, `goal-canonical-arc-s4-onward-2026-07-07.txt`, and `runs/a18c2a86-bbdb-48a2-ba63-fb1a653bfaf9/`.

**Canonical-lane movement:**

- The canonical monitor ledger now contains `SOP-011 - S4 spec pre-dispatch review`, relayed by the Claude lane.
- Canonical SOP-011 independently agrees that the four required obligations are honored:
  - E4/two-way ruling is sound for S4 and leaves clock-strength to S-flip.
  - S4 scope matches the §7 row, with the 13-key `app/styleguide/parity.py` receipt and 10-key CD emission contract as frozen inputs.
  - F-705 WARN-seed ownership transfers to S4 with byte-diff witness.
  - §10 retry taxonomy and runs-root split remain filed/out of scope.
- Canonical SOP-011 added material catches and disposition before dispatch:
  - **canonical F-1101:** Flip A only fires for a named `gamma_settings` variant lacking `styleguide`; empty/absent `gamma_settings` does not fire the branch. Spec now scopes AC-1/AC-L leg 1 to the named-variant path and files the empty/declined-pick default-A leg as `styleguide-mandatory-pick-trial-start-precheck`.
  - **canonical F-1102:** comparator self-crash folds into `divergence/contract-violation`; post-S4 that will halt. Spec now explicitly rules that halt intended and adds an AC-4 crash-fallback witness.
  - **canonical F-1103/F-1104:** Flip-B wording softened; `list_themes()` acknowledged as permitted non-generative pre-flip metadata read.
- `_bmad-output/planning-artifacts/deferred-inventory.md` now records:
  - `styleguide-retire-default-variant-pair-fail-loud-flip` reactivated under canonical S4.
  - new follow-on `styleguide-mandatory-pick-trial-start-precheck` for the empty/declined-pick leg.

**Finding disposition:**

- **F-001..F-010 CLOSED.**
- **F-901/F-902 CLOSED.**
- **F-1001/F-1002 advisory accepted in SOP-010.**
- **F-1003 CLOSED.**
- **F-1101 CLOSED.** The S4 spec exists and satisfies the four SOP-011 obligations.
- **F-1102 CLOSED (external procedural watch).** The SOP-011 relay is now visible in the canonical monitor, the dispatch-blocking findings were applied to the spec, and dev dispatch is explicitly cleared. Note: canonical SOP-011 uses `F-1102` for a different substantive comparator-crash finding; that canonical finding is also recorded as applied in the spec.

**Recommendations:**

1. Next monitor poll should be **SOP-012 at S4 dev-complete**, not another spec-gate review, unless the spec is materially rewritten again.
2. At SOP-012, verify the named-variant scope actually landed in tests and live setup; an empty `gamma_settings` AC-L leg would be a false negative.
3. Confirm `app/styleguide/parity.py` remains diff-empty and the new tags are absent from `_RETRYABLE_DISPATCH_TAGS`.
4. Treat the new `styleguide-mandatory-pick-trial-start-precheck` as a filed follow-on only; do not let it expand S4 dev scope.

**Verdict:** `S4-DISPATCH-CLEARED-WATCH-SOP012`. SOP-011 is relayed and applied; no S4 implementation diff is visible yet.

### POLL-026 - S4 RED-first tests visible / implementation not yet landed (2026-07-06T23:21:28-04:00)

**Trigger:** heartbeat poll at `2026-07-07T03:21:28.626Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, still synced with origin at `13792617`.
- No new commits since session-17 wrap-up.
- Tracked/untracked S4-related working-tree movement now includes:
  - modified `_bmad-output/implementation-artifacts/canonical-arc-claude-shadow-monitor-2026-07-06.md` with SOP-011 relay
  - modified `_bmad-output/planning-artifacts/deferred-inventory.md` with S4 reactivation + trial-start precheck follow-on
  - modified `tests/composition/test_gary_parity_walk_pin.py`
  - new `tests/specialists/gary/test_styleguide_fail_loud_flip.py`
  - new `tests/specialists/gary/test_styleguide_parity_error_flip.py`
  - new/untracked `_bmad-output/implementation-artifacts/canonical-arc-s4-fail-loud-flip.md`
- No production code diff is visible yet.
- Known excluded strays remain visible: `_bmad-output/artifacts/workbooks-test/`, the external/workbook `claude-shadow-monitor-*` ledgers, `goal-canonical-arc-s4-onward-2026-07-07.txt`, and `runs/a18c2a86-bbdb-48a2-ba63-fb1a653bfaf9/`.

**RED-first test review:**

- `tests/specialists/gary/test_styleguide_fail_loud_flip.py` appears aligned with amended SOP-011:
  - Flip A is pinned to a **named variant present in `gamma_settings` with no `styleguide` key**, not empty `gamma_settings`.
  - The companion negative preserves empty/absent `gamma_settings` as out-of-scope and proceeding via `ok/status-keyed-no-picks`.
  - AC-2 covers WARN absence, new `gamma.styleguide.unbound` tag, and `DEFAULT_VARIANT_PAIR` retention.
  - AC-3 golden-success bytes are pinned against the pre-flip path.
  - AC-7 asserts neither flip reads `clock_eligible`.
- `tests/specialists/gary/test_styleguide_parity_error_flip.py` appears aligned with amended SOP-011:
  - new tags are asserted absent from `_RETRYABLE_DISPATCH_TAGS`.
  - Flip B is parametrized over `resolution-mismatch`, `cd-unresolvable-but-gary-resolved`, `contract-violation`, and the comparator crash fallback.
  - divergence raises are checked as pre-generative-dispatch.
  - tolerated `ok/*`, `expected-ordering-gap/*`, and legacy/absent CD blocks still proceed.
- `tests/composition/test_gary_parity_walk_pin.py` adds AC-8 both-walk coverage:
  - start + continuation walk fail loud for Flip A on the named-variant styleguide-less path.
  - start + continuation walk fail loud for Flip B parity divergence.
  - happy path still dispatches and yields `ok/match`.

**SOP-012 readiness:**

- No `SOP-012`, `dev-complete`, review, remediation, or live-witness evidence marker is visible yet.
- Because no production implementation diff is visible, this remains a RED-first in-progress snapshot rather than a dev-complete gate.

**Finding disposition:**

- **F-001..F-010 CLOSED.**
- **F-901/F-902 CLOSED.**
- **F-1001/F-1002 advisory accepted in SOP-010.**
- **F-1003 CLOSED.**
- **F-1101 CLOSED.**
- **F-1102 CLOSED** for the external procedural watch; canonical F-1102 comparator-crash ruling is applied in the spec and now represented by tests.
- **F-1201 WATCH (S4 RED-first in progress):** tests look faithful to SOP-011 amendments, but implementation has not landed and SOP-012 is not yet available.

**Recommendations:**

1. Continue RED-first implementation, keeping production edits narrow to the Gary fail-loud call sites and any strictly necessary error-message/log adjustment.
2. At SOP-012, verify `app/styleguide/parity.py` is still diff-empty and no new tag was added to `_RETRYABLE_DISPATCH_TAGS`.
3. Preserve the empty/absent `gamma_settings` negative test. If dev broadens Flip A into a whole-dispatch no-styleguide chokepoint, that would re-open the W5-morph legacy-bundle false-fail risk the amended spec explicitly avoided.
4. Treat the success-path byte-golden as a hard invariant; if it fails, require a concrete byte-level explanation, not a loosened assertion.

**Verdict:** `S4-RED-FIRST-IN-PROGRESS`. The test harness is materially aligned with SOP-011; monitor waits for implementation + SOP-012 dev-complete evidence.

### POLL-027 - S4 implementation visible / pre-SOP-012 material triage-risk catch (2026-07-06T23:31:28-04:00)

**Trigger:** heartbeat poll at `2026-07-07T03:31:28.769Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, still synced with origin at `13792617`.
- No new commits since session-17 wrap-up.
- Implementation diffs are now visible:
  - `app/specialists/gary/_act.py`
  - `tests/composition/test_gary_parity_walk_pin.py`
  - `tests/specialists/gary/test_gary_studio_mode.py`
  - `tests/specialists/gary/test_normalized_gamma_settings_variant_projection.py`
  - `tests/specialists/gary/test_styleguide_parity_receipt.py`
  - new `tests/specialists/gary/_s4_seed.py`
  - new `tests/specialists/gary/test_styleguide_fail_loud_flip.py`
  - new `tests/specialists/gary/test_styleguide_parity_error_flip.py`
  - S4 spec + canonical SOP-011 docs/deferred-inventory changes remain in the worktree.
- No `SOP-012`, dev-complete marker, 3-lane review, remediation record, or live evidence is visible yet.
- Known excluded strays remain visible: `_bmad-output/artifacts/workbooks-test/`, the external/workbook `claude-shadow-monitor-*` ledgers, `goal-canonical-arc-s4-onward-2026-07-07.txt`, and `runs/a18c2a86-bbdb-48a2-ba63-fb1a653bfaf9/`.

**Implementation spot-checks:**

- Flip A is implemented narrowly in `_normalized_gamma_settings`: the named-variant styleguide-less `else` branch now raises `GaryActError(tag="gamma.styleguide.unbound")`; `DEFAULT_VARIANT_PAIR` remains defined.
- Flip B is implemented in `generate_gamma_variants` immediately after `_styleguide_parity_receipt(...)` and before the generative dispatch loop: `outcome == "divergence"` raises `GaryActError(tag="gamma.styleguide.parity-divergence")`.
- `_styleguide_parity_receipt` still returns a receipt and never raises, but now logs divergence at ERROR level and drops the stale "dispatch proceeds" wording.
- `app/styleguide/parity.py` has no diff.
- `app/marcus/orchestrator/production_runner.py` has no diff; the retry allowlist is not modified.
- Existing tests that depended on styleguide-less seeds are being moved to a synthetic canonical styleguide-bound seed helper (`tests/specialists/gary/_s4_seed.py`), preserving byte-equivalent defaults without weakening the new S4 fail-loud branch.

**New finding:**

- **F-1202 OPEN (material, pre-SOP-012): Flip B appears to lose the full parity receipt/envelopes on the error-pause path.** The S4 spec says the divergence `reason` plus the three digests and both-envelope `detail` must be reachable from the error context: the receipt is "already persisted on the contribution" if preserved, otherwise attach a compact digest summary to the error. Current code computes `styleguide_parity`, then raises before the function returns the Gary contribution containing `"styleguide_parity": styleguide_parity` (`_act.py` return block only runs after dispatch success). `act()` catches `GaryActError`, appends only a trail entry, and re-raises. `_pause_at_error` persists only `tag` and `message` plus run state, not the computed receipt. The raised message currently carries the reason but not both envelopes or the digest/detail fields. Unless another mechanism exists outside the inspected path, AC-4's "both envelopes remain reachable for triage" is under-specified/not yet satisfied.

**Finding disposition:**

- **F-001..F-010 CLOSED.**
- **F-901/F-902 CLOSED.**
- **F-1001/F-1002 advisory accepted in SOP-010.**
- **F-1003 CLOSED.**
- **F-1101 CLOSED.**
- **F-1102 CLOSED** for the external procedural watch; canonical F-1102 comparator-crash ruling remains represented in tests.
- **F-1201 WATCH (S4 RED-first/implementation in progress):** implementation now visible, but no SOP-012/dev-complete marker yet.
- **F-1202 OPEN** until Flip B either persists the full receipt on the error-pause path or attaches a compact, test-pinned triage summary to the error context.

**Recommendations:**

1. Before declaring SOP-012/dev-complete, add a test that exercises a parity-divergence error-pause and asserts the operator can recover the reason plus digest/envelope triage data from persisted error context or another explicit artifact.
2. The narrowest implementation fix is likely to include a compact JSON-safe summary in the `GaryActError` message or a structured error context if the dispatch error type supports it. Avoid changing `parity.py` for this; S4 is caller-action only.
3. Keep the current positives: `parity.py` remains diff-empty, retry tags remain non-retryable by default, and named-variant vs empty-settings scope is still correctly separated.
4. Do not treat current implementation as SOP-012-ready until F-1202 is either fixed or explicitly rebutted with a concrete persistence path.

**Verdict:** `S4-IMPLEMENTATION-IN-PROGRESS-WITH-F1202`. Core flips are present and scope looks mostly faithful, but Flip B triage preservation needs correction or proof before dev-complete.

### POLL-028 - S4 implementation still in progress / F-1202 remains open (2026-07-06T23:41:28-04:00)

**Trigger:** heartbeat poll at `2026-07-07T03:41:28.955Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, still synced with origin at `13792617`.
- No new commits since session-17 wrap-up.
- S4 implementation/test worktree is broader than the prior poll:
  - `app/specialists/gary/_act.py`
  - `tests/composition/test_gary_parity_walk_pin.py`
  - `tests/specialists/gary/test_gary_dimensions_override_removed.py`
  - `tests/specialists/gary/test_gary_gamma_dispatch.py`
  - `tests/specialists/gary/test_gary_studio_mode.py`
  - `tests/specialists/gary/test_normalized_gamma_settings_variant_projection.py`
  - `tests/specialists/gary/test_styleguide_parity_receipt.py`
  - new `tests/specialists/gary/_s4_seed.py`
  - new `tests/specialists/gary/test_styleguide_fail_loud_flip.py`
  - new `tests/specialists/gary/test_styleguide_parity_error_flip.py`
  - S4 spec + canonical SOP-011 docs/deferred-inventory changes remain in the worktree.
- No `SOP-012`, dev-complete marker, T11 review, remediation record, or live AC-L evidence is visible yet.
- Known excluded strays remain visible: `_bmad-output/artifacts/workbooks-test/`, the external/workbook `claude-shadow-monitor-*` ledgers, `goal-canonical-arc-s4-onward-2026-07-07.txt`, and `runs/a18c2a86-bbdb-48a2-ba63-fb1a653bfaf9/`.

**Implementation delta since prior poll:**

- More legacy Gary tests are adapted to the S4 world by binding named variants through the synthetic `_s4_seed` helper, preserving old packet/enum/studio/dimension assertions while avoiding the newly illegal named-variant/no-styleguide path.
- `tests/composition/test_gary_parity_walk_pin.py` now expects `paused-at-error` status and asserts the new error tags in `error-pause.json`.
- Flip A and Flip B code in `app/specialists/gary/_act.py` appears materially unchanged from POLL-027.
- `app/styleguide/parity.py` remains diff-empty.
- `app/marcus/orchestrator/production_runner.py` remains diff-empty; retry allowlist remains untouched.

**F-1202 re-check:**

- **Still OPEN.** The tests now assert that `error-pause.json["message"]` includes the divergence reason (`cd-unresolvable-but-gary-resolved` in the walk-pin case), but I still do not see a persisted full receipt, compact digest summary, or both-envelope triage data on the error path.
- The inspected execution shape remains:
  - `_styleguide_parity_receipt(...)` computes the full receipt.
  - `generate_gamma_variants(...)` raises `GaryActError` immediately on `outcome == "divergence"`.
  - The function does not reach the successful return block that would include `"styleguide_parity": styleguide_parity`.
  - `act()` catches `GaryActError`, appends only a model-resolution trail tag, and re-raises.
  - `_pause_at_error(...)` persists `tag`, `message`, and `run_state`; it does not persist the computed receipt.
- Therefore, the current implementation still appears to satisfy "reason visible" but not the spec's stronger requirement that the three digests and both-envelope `detail` remain reachable for triage, unless a different persistence path exists that was not visible in this poll.

**Finding disposition:**

- **F-001..F-010 CLOSED.**
- **F-901/F-902 CLOSED.**
- **F-1001/F-1002 advisory accepted in SOP-010.**
- **F-1003 CLOSED.**
- **F-1101 CLOSED.**
- **F-1102 CLOSED** for the external procedural watch; canonical F-1102 comparator-crash ruling remains represented in tests.
- **F-1201 WATCH:** implementation in progress; no SOP-012/dev-complete marker yet.
- **F-1202 OPEN:** parity-divergence triage preservation still needs a concrete persisted receipt/summary path or a rebuttal grounded in code.

**Recommendations:**

1. Do not mark S4 dev-complete until F-1202 is addressed. A test that only checks the error message reason is not enough for the spec's triage-data requirement.
2. Prefer a minimal caller-side fix: include a JSON-safe compact parity summary in the raised `GaryActError` message or in a structured error context if available. The summary should include at least outcome, reason, CD/Gary/trial-start digests, bound-guide summaries, and enough detail keys to locate both envelopes.
3. Keep `parity.py` and `production_runner.py` untouched unless the dev agent can justify a smaller, safer persistence mechanism there. Current S4 can likely remain a Gary caller-action change.
4. At SOP-012, require an explicit F-1202 disposition and verify it by reading the persisted `error-pause.json` or named evidence artifact, not just unit-level helper receipt tests.

**Verdict:** `S4-IN-PROGRESS-F1202-STILL-OPEN`. Implementation is moving, but the parity-divergence error-pause still lacks proven triage-data preservation.

### POLL-029 - S4 unchanged on F-1202 / downstream S6-if-time scope noted (2026-07-06T23:51:29-04:00)

**Trigger:** heartbeat poll at `2026-07-07T03:51:29.072Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, still synced with origin at `13792617`.
- No new commits since session-17 wrap-up.
- S4 implementation/test worktree remains active with the same broad surface:
  - `app/specialists/gary/_act.py`
  - `tests/composition/test_gary_parity_walk_pin.py`
  - Gary test adaptations under `tests/specialists/gary/`
  - new S4 test/helper files under `tests/specialists/gary/`
  - S4 spec + canonical SOP-011 docs/deferred-inventory changes
- No `SOP-012`, dev-complete marker, T11 review, remediation record, or live AC-L evidence is visible yet.
- Known excluded strays remain visible: `_bmad-output/artifacts/workbooks-test/`, the external/workbook `claude-shadow-monitor-*` ledgers, `goal-canonical-arc-s4-onward-2026-07-07.txt`, and `runs/a18c2a86-bbdb-48a2-ba63-fb1a653bfaf9/`.

**Scope note from operator:**

- The allowed downstream ordering is now: **S4 close → pre-S5 g0-battery → S5 G0 canonical → S6 Tracy if enough time remains**.
- S7 workbook remains later and keeps its operator review/edit/approval gate before dev dispatch.
- This does not change S4's close requirements: SOP-012, review/remediation, live AC-L PASS, commit/push, and close poll still gate completion.

**F-1202 re-check:**

- **Still OPEN.** Current visible code still raises `GaryActError(tag="gamma.styleguide.parity-divergence")` immediately after computing `styleguide_parity`, before the successful return path that would persist `"styleguide_parity"` in Gary's contribution.
- Current visible tests still assert the divergence reason in `error-pause.json["message"]`, but do not assert that the three digests, bound-guide summaries, or both-envelope detail are recoverable from persisted error context or a named evidence artifact.
- No production-runner persistence change is visible, and `app/styleguide/parity.py` remains diff-empty as desired.

**Finding disposition:**

- **F-001..F-010 CLOSED.**
- **F-901/F-902 CLOSED.**
- **F-1001/F-1002 advisory accepted in SOP-010.**
- **F-1003 CLOSED.**
- **F-1101 CLOSED.**
- **F-1102 CLOSED** for the external procedural watch; canonical F-1102 comparator-crash ruling remains represented in tests.
- **F-1201 WATCH:** implementation in progress; no SOP-012/dev-complete marker yet.
- **F-1202 OPEN:** unchanged. Parity-divergence error-pause triage-data preservation still needs a concrete persisted receipt/summary path or a code-grounded rebuttal.

**Recommendations:**

1. Keep S4 focused; do not start pre-S5/S5/S6 until S4 closes live-proven and committed.
2. Address F-1202 before SOP-012: reason-only error messages are not enough for the spec's "both envelopes remain reachable for triage" requirement.
3. At SOP-012, require explicit verification that `parity.py` is diff-empty, retry tags remain non-retryable, and the named-variant/empty-settings distinction survived implementation.
4. If time remains after S5, S6 Tracy can open, but only from a clean committed checkpoint.

**Verdict:** `S4-IN-PROGRESS-F1202-STILL-OPEN-S6-SCOPE-NOTED`. No new user action needed; monitor waits for a F-1202 fix or SOP-012 artifact.

### POLL-030 - SOP-012/T11 landed; F-1202 confirmed and remediation visible (2026-07-07T00:01:29-04:00)

**Trigger:** heartbeat poll at `2026-07-07T04:01:29.221Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, still synced with origin at `13792617`.
- No new commits since session-17 wrap-up.
- Worktree is still active and uncommitted across the S4 implementation surface:
  - `app/specialists/gary/_act.py`
  - `tests/composition/test_gary_parity_walk_pin.py`
  - Gary S4 test adaptations under `tests/specialists/gary/`
  - new `tests/specialists/gary/_s4_seed.py`
  - new S4 parity flip tests
  - S4 spec and canonical monitor/deferred-inventory artifacts
- Known excluded strays remain visible: `_bmad-output/artifacts/workbooks-test/`, the external/workbook `claude-shadow-monitor-*` ledgers, `goal-canonical-arc-s4-onward-2026-07-07.txt`, and `runs/a18c2a86-bbdb-48a2-ba63-fb1a653bfaf9/`.

**New canonical monitor signal:**

- The canonical monitor now includes **SOP-012 - S4 dev-complete verification** and a **T11 3-lane bmad-code-review** relay.
- SOP-012 reports the main S4 implementation checks passing:
  - `app/styleguide/parity.py` diff-empty.
  - Flip A raises `gamma.styleguide.unbound` only for named variants with no bound styleguide.
  - Empty or absent gamma settings still falls back to default-A and does not raise.
  - Flip B raises `gamma.styleguide.parity-divergence` after receipt computation and before the dispatch loop.
  - Tags remain non-retryable; `production_runner.py` diff-empty.
  - AC-8 walk-pin proves `paused-at-error` at node 07.
  - Touched suite rerun and ruff are reported clean, with two Texas-internal baseline reds reproduced from the baseline worktree.
- SOP-012 still does **not** close S4: AC-L live 3-leg PASS, remediation reverify, commit/push, and SOP close poll remain required.

**F-1202 disposition:**

- **RESOLVED-IN-REMEDIATION / PENDING-REVERIFY.**
- The T11 review independently confirmed the same material issue as F-1202: the Flip-B halt discarded the dispatch-time parity receipt, so the prior "both envelopes ride receipt" wording and AC-4/D2 triage story were not accurate.
- The current worktree now shows the intended remediation in `app/specialists/gary/_act.py`:
  - parity-divergence raises with a compact digest summary containing CD/Gary resolution digests plus CD/Gary/trial-start directive digests;
  - log/message wording now states that Gary's dispatch-time parity receipt is **not** persisted on the halt path;
  - the surviving halt context is explicitly tag, reason, and compact digest summary, with CD's own persisted contribution as the recovery source for the CD envelope.
- New R1-focused tests are visible in `tests/specialists/gary/test_styleguide_parity_error_flip.py`, including assertions that the divergence message carries the compact digests and removes the false "ride receipt" claim.
- This is a satisfactory remediation direction for F-1202, but I am not marking it fully closed until orchestrator reverify and the live AC-L evidence prove the compact summary survives the actual error-pause path.

**Finding disposition:**

- **F-001..F-010 CLOSED.**
- **F-901/F-902 CLOSED.**
- **F-1001/F-1002 advisory accepted in SOP-010.**
- **F-1003 CLOSED.**
- **F-1101 CLOSED.**
- **F-1102 CLOSED** for the external procedural watch; canonical F-1102 comparator-crash ruling remains represented in tests.
- **F-1201 WATCH:** baseline Texas-internal reds still carried explicitly by SOP-012.
- **F-1202 RESOLVED-IN-REMEDIATION / PENDING-REVERIFY:** confirmed by T11 and addressed in current worktree, but still needs live/error-pause proof before closure.

**Recommendations:**

1. In the remediation reverify, assert the compact digest summary is present in the persisted error-pause evidence, not only in the unit-level exception string.
2. Keep `app/styleguide/parity.py` and `production_runner.py` diff-empty through close unless a new review finding forces a scoped change.
3. AC-L should remain a first-run-stands, three-leg live witness: named-variant unbound at zero spend, parity divergence at zero spend, and happy-path real deck pass.
4. Do not move to pre-S5, S5, or S6 until S4 is live-proven, committed, pushed, and closed by SOP poll.

**Verdict:** `S4-REMEDIATION-IN-PROGRESS-F1202-PENDING-REVERIFY`. The prior material catch was accepted by the Claude review lane and the fix is visible, but S4 is still not close-ready.

### POLL-031 - R1-R6 remediation visible; no reverify/live/commit yet (2026-07-07T00:11:29-04:00)

**Trigger:** heartbeat poll at `2026-07-07T04:11:29.341Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, still synced with origin at `13792617`.
- No new commits since the S3/session-17 wrap-up.
- The worktree remains active and uncommitted on the S4 files already seen at the previous poll.
- The canonical monitor artifact has not advanced beyond **SOP-012** and the **T11 R1-R6 remediation queue**; no orchestrator reverify, AC-L live evidence, commit, or SOP-013 close poll is visible yet.
- Latest implementation-artifact timestamps show:
  - `canonical-arc-claude-shadow-monitor-2026-07-06.md` last updated around 23:54 local.
  - `canonical-arc-s4-fail-loud-flip.md` unchanged since 23:07 local.
  - this external ledger is the only monitor file touched by this poll.

**Remediation visibility check:**

- **R1 visible:** `app/specialists/gary/_act.py` now raises `gamma.styleguide.parity-divergence` with a compact digest summary containing `cd_resolution_digest`, `gary_resolution_digest`, `cd_directive_digest`, `gary_directive_digest`, and `trial_start_directive_digest`. The log/message/comments now explicitly say Gary's dispatch-time receipt is not persisted on the halt path.
- **R1 test visible:** `tests/specialists/gary/test_styleguide_parity_error_flip.py::test_r1_divergence_message_carries_digests_and_no_false_ride_claim` captures the actual receipt, asserts both resolution digest values and directive digest value are present in the raised message, preserves the reason, and asserts the false "ride/rides the receipt" claim is absent.
- **R2 visible:** two-way attestation test covers a `divergence` with `trial_start_directive_digest=None`, proving S4 did not accidentally impose the deferred three-way S-flip clock rule.
- **R3 visible:** mixed A-bound/B-unbound test proves a sibling styleguide binding does not license a named styleguide-less variant.
- **R4 visible:** `gamma_settings=[]` proceeds through default-A without `gamma.styleguide.unbound`, preserving the narrowed S4 scope.
- **R5 visible:** stale Studio-path comment in `_act.py` now states the old unbound direct-studio carve-out is dead post-Flip-A.
- **R6 visible:** both autouse seed fixtures (`test_gary_gamma_dispatch.py`, `test_gary_studio_mode.py`) now include explicit warnings that future Flip-A/styleguide-less tests must live in `test_styleguide_fail_loud_flip.py`, not inside the autouse-seeded modules.

**F-1202 disposition:**

- **Still RESOLVED-IN-REMEDIATION / PENDING-REVERIFY.**
- The code/test remediation now appears to cover the exact T11 R1-R6 queue, including the external F-1202 concern.
- I am not closing F-1202 yet because the current evidence is still worktree-level and unit/focused-test visible. The close proof should include orchestrator reverify and an actual error-pause/live artifact showing the compact digest summary survives the real halt path.

**Finding disposition:**

- **F-001..F-010 CLOSED.**
- **F-901/F-902 CLOSED.**
- **F-1001/F-1002 advisory accepted in SOP-010.**
- **F-1003 CLOSED.**
- **F-1101 CLOSED.**
- **F-1102 CLOSED** for the external procedural watch; canonical F-1102 comparator-crash ruling remains represented in tests.
- **F-1201 WATCH:** baseline Texas-internal reds still carried explicitly by SOP-012.
- **F-1202 RESOLVED-IN-REMEDIATION / PENDING-REVERIFY:** R1-R6 visible; await reverify/live close evidence.

**Recommendations:**

1. The next gate should be orchestrator reverify of R1-R6, with an explicit check that the compact digest summary appears in the persisted `error-pause.json` or named live evidence, not only in the raised exception string.
2. Keep the diff boundary stable: `app/styleguide/parity.py` and `production_runner.py` should remain diff-empty through S4 close unless a new material review finding forces a scoped exception.
3. Do not let the R6 autouse seed warnings become the only long-term defense; if future Gary tests are added to those modules, review whether they are genuinely seed-preserving or should move to the Flip-A test file.
4. Do not advance to pre-S5/S5/S6 until S4 is committed, pushed, live-proven, and SOP-013 closed.

**Verdict:** `S4-REMEDIATION-CODE-VISIBLE-NOT-CLOSED`. R1-R6 appear addressed in the worktree, but the story remains gated on reverify, live AC-L, commit/push, and close poll.

### POLL-032 - S4 AC-L live evidence present; awaiting canonical close/commit (2026-07-07T00:21:29-04:00)

**Trigger:** heartbeat poll at `2026-07-07T04:21:29.484Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, still synced with origin at `13792617`.
- No new commits since the S3/session-17 wrap-up.
- S4 worktree remains uncommitted.
- New live evidence is visible at `_bmad-output/implementation-artifacts/evidence/s4-acl-liveproof-20260707T041058Z/`.
- New run/evidence state is visible:
  - `runs/4fe6073f-c8e2-4836-bb94-759dc5b97bbf/`
  - appended live pick event in `state/config/gamma-styleguide-picks.jsonl` for run `4fe6073f-c8e2-4836-bb94-759dc5b97bbf`
- The canonical monitor file has not yet advanced beyond the T11 R1-R6 remediation queue; no SOP-013 close poll or close commit is visible.

**Live evidence spot-check:**

- **Judges frozen:** `judges-frozen.json` records freeze at `2026-07-07T04:13:57.364114+00:00` with hashes for `judge1.py`, `judge2.py`, and `judge3.py`.
- **Leg 1 named-variant unbound halt:** `judge1-output.txt` reports PASS, paused at `gamma.styleguide.unbound`, node `07`, specialist `gary`, with zero Gary contributions and no generation id. The message names variant `A` and states no bound styleguide.
- **Leg 2 parity-divergence halt:** `judge2-output.txt` reports PASS, paused at `gamma.styleguide.parity-divergence`, node `07`, specialist `gary`, with zero Gary contributions and CD contribution retained.
- **Leg 2 closes F-1202 substance:** persisted error context contains the compact digest summary:
  - `cd_resolution_digest=5f87200054af8699f9bdbf19608559eace7e9007c715d2210cc8dd2922db9463`
  - `gary_resolution_digest=83981ed00dc73cacef72724ebb4cf82b1bde496771c45b0dc3fd28567d8a651f`
  - matching CD/Gary/trial-start directive digests `ff90c166d8d574e00403dcbb98079e340dfa2ab6904f0498269dfadfda283e27`
  - explicit wording that Gary's dispatch-time parity receipt is not persisted because dispatch halts pre-contribution.
- **Leg 3 happy path:** `judge3-output.txt` reports PASS with real generation id `npkNxi1NwrKbfPj3NU61I`, 12 slide rows, 12 PNG exports, `styleguide_parity.outcome == ok`, `reason == match`, `clock_eligible == true`, and post-07 pause at `G2B`.
- **Sidecar:** the styleguide pick sidecar append for `4fe6073f-c8e2-4836-bb94-759dc5b97bbf` appears consistent with the happy-path live leg.

**F-1202 disposition:**

- **CLOSED-SUBSTANTIVELY / AWAITING-COMMIT-CLOSE.**
- The exact concern from F-1202 is now proven in live persisted evidence: the parity-divergence halt does not falsely claim the full Gary receipt survives, and the error-pause context carries the compact digest summary needed for triage.
- Final closure should be confirmed by the canonical SOP close poll after commit integrity is available.

**Finding disposition:**

- **F-001..F-010 CLOSED.**
- **F-901/F-902 CLOSED.**
- **F-1001/F-1002 advisory accepted in SOP-010.**
- **F-1003 CLOSED.**
- **F-1101 CLOSED.**
- **F-1102 CLOSED** for the external procedural watch; canonical F-1102 comparator-crash ruling remains represented in tests.
- **F-1201 WATCH:** baseline Texas-internal reds still carried explicitly by SOP-012.
- **F-1202 CLOSED-SUBSTANTIVELY / AWAITING-COMMIT-CLOSE:** live persisted error-pause evidence proves the compact digest summary survives the real halt path.

**Recommendations:**

1. Before committing, relay the AC-L evidence into the canonical monitor/close record and explicitly cite the three judge PASS files, frozen judge hashes, and the persisted digest-summary assertion from Leg 2.
2. Verify commit scope carefully: include S4 spec/code/tests/canonical evidence/sidecar append as intended, but keep protected strays excluded.
3. Re-check `app/styleguide/parity.py` and `production_runner.py` remain diff-empty at close.
4. Only after S4 is committed, pushed, and SOP-013 closed should the team advance to pre-S5 g0-battery.

**Verdict:** `S4-LIVE-PASS-EVIDENCE-SEEN-NOT-COMMITTED`. S4 appears live-proven at the artifact level, including the F-1202 fix, but it is not done until canonical close, commit/push, and SOP-013 audit land.

### POLL-033 - S4 committed/pushed; external close audit clean with one procedural note (2026-07-07T00:31:29-04:00)

**Trigger:** heartbeat poll at `2026-07-07T04:31:29.615Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with origin.
- HEAD is now `63369c99`:
  - `feat(canonical-arc-S4): FAIL-LOUD flip — styleguide-less->hard-fail + parity divergence->ERROR (LIVE-PROVEN 3-leg)`
- Worktree is clean except the known excluded/untracked paths:
  - `_bmad-output/artifacts/workbooks-test/`
  - the external/workbook `claude-shadow-monitor-*` ledgers
  - `goal-canonical-arc-s4-onward-2026-07-07.txt`
  - `runs/4fe6073f-c8e2-4836-bb94-759dc5b97bbf/`
  - `runs/a18c2a86-bbdb-48a2-ba63-fb1a653bfaf9/`

**Commit integrity spot-check:**

- Commit scope is coherent for S4:
  - S4 spec: `_bmad-output/implementation-artifacts/canonical-arc-s4-fail-loud-flip.md`
  - S4 live evidence pack: `_bmad-output/implementation-artifacts/evidence/s4-acl-liveproof-20260707T041058Z/`
  - canonical monitor ledger update
  - deferred inventory update
  - Gary caller-action flip in `app/specialists/gary/_act.py`
  - sidecar append in `state/config/gamma-styleguide-picks.jsonl`
  - focused composition/Gary tests and new S4 seed/test files
- Protected strays stayed out of the commit: external monitor ledger, workbook ledgers, workbook-test artifact, and run directories remain untracked.
- `app/styleguide/parity.py` and `app/marcus/orchestrator/production_runner.py` remain diff-empty at HEAD.
- Commit message records:
  - R1-R6 remediation;
  - orchestrator reverify `348 green`, `ruff 0-new`, `lint-imports 16/0`;
  - AC-L 3-leg witness with frozen judges and no anomalies;
  - spend of 1 deck plus approximately `$0.32`;
  - authority S-flip still deferred at parity clock tick 1.

**Close evidence spot-check:**

- S4 spec status is now `DONE`.
- Evidence pack from the previous poll remains consistent:
  - Leg 1 `judge1-output.txt`: PASS, `gamma.styleguide.unbound`, node `07`, zero Gary contributions, no generation id.
  - Leg 2 `judge2-output.txt`: PASS, `gamma.styleguide.parity-divergence`, persisted compact digest summary, zero Gary contributions, CD contribution retained.
  - Leg 3 `judge3-output.txt`: PASS, real Gamma generation `npkNxi1NwrKbfPj3NU61I`, `ok/match`, `clock_eligible=true`, post-07 pause at `G2B`.

**Procedural note:**

- The committed canonical monitor file still appears to stop at the T11 remediation queue and does not contain an explicit `SOP-013` section by name. The S4 spec and commit message carry the close facts, and this external monitor entry functions as the close audit, but the Claude lane should avoid ambiguity by either adding a canonical SOP-013 relay later or treating this external poll as the required shadow-monitor close corroboration.

**Finding disposition:**

- **F-001..F-010 CLOSED.**
- **F-901/F-902 CLOSED.**
- **F-1001/F-1002 advisory accepted in SOP-010.**
- **F-1003 CLOSED.**
- **F-1101 CLOSED.**
- **F-1102 CLOSED** for the external procedural watch; comparator-crash halt remains represented in S4.
- **F-1201 WATCH:** Texas-internal baseline reds remain a carried baseline issue, not an S4 blocker.
- **F-1202 CLOSED:** committed live evidence proves the persisted parity-divergence error-pause carries the compact digest summary and honest halt-path wording.

**Recommendations:**

1. Treat S4 as externally close-audited and safe to advance from a code/evidence standpoint.
2. Before starting pre-S5, have the Claude lane read this poll and explicitly acknowledge F-1202 closure plus the procedural note about the missing named `SOP-013` section in the canonical monitor.
3. Start the pre-S5 g0-battery story from the clean committed checkpoint `63369c99`, with the S5-open precondition front and center.
4. Continue excluding the run directories and external monitor ledgers from future commits.

**Verdict:** `S4-COMMITTED-PUSHED-EXTERNAL-CLOSE-CONCUR-WITH-PROCEDURAL-NOTE`. The S4 implementation/evidence/commit are clean; the only watch item is documentation hygiene around the absent named canonical SOP-013 relay.

### POLL-034 - S4 SOP-013 relayed; pre-S5 g0-battery spec opens (2026-07-07T00:41:29-04:00)

**Trigger:** heartbeat poll at `2026-07-07T04:41:29.753Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, still synced with origin at `63369c99`.
- No new commits after S4.
- Tracked/untracked changes now visible:
  - `M _bmad-output/implementation-artifacts/canonical-arc-claude-shadow-monitor-2026-07-06.md`
  - `?? _bmad-output/implementation-artifacts/canonical-arc-pre-s5-g0-battery-baseline.md`
  - known excluded strays remain untracked: workbook-test artifact, external/workbook monitor ledgers, goal launcher, and the two run dirs.

**S4 close status update:**

- The prior procedural note is now resolved in the working tree: the canonical monitor has an explicit **SOP-013 — S4 story-close audit** relay.
- SOP-013 reports clean commit integrity for `63369c99`, frozen `app/styleguide/parity.py` and `production_runner.py`, one sidecar append, first-run-stands live evidence, yaml restore, post-commit green, and no findings.
- Because the SOP-013 relay is currently an uncommitted modification after `63369c99`, make sure it is deliberately included in the next documentation/spec commit or otherwise not lost.

**Pre-S5 spec status:**

- New spec exists at `_bmad-output/implementation-artifacts/canonical-arc-pre-s5-g0-battery-baseline.md`.
- Spec status: `READY-FOR-DEV`.
- Scope is correctly framed as the binding S5-open precondition, not S5 itself:
  - create and track `course-content/courses/studio-smoke-min/lesson.md`;
  - refresh the stale `ACTIVE_TERMINAL_GATES` test pin;
  - no production-code change expected;
  - offline-only, because S5 owns the live G0 proof.

**Quick factual checks:**

- `course-content/courses/studio-smoke-min/lesson.md` is absent at this poll, matching the spec's fixture-absence premise.
- Runtime gate inventory includes `G0R` in `app/marcus/cli/gate_shims/_shim_parser.py`.
- `tests/unit/marcus/cli/test_shim_parser_factory.py::test_active_terminal_gates_canonical_inventory` still expects `("G0E", "G1", "G2B", "G2C", "G3", "G4A", "G4")`, confirming the stale-pin premise.
- The two named Irene tests exist and point at `studio-smoke-min`:
  - `test_ac_s3_6_wiring_reads_gate1_provisional_los_and_refines`
  - `test_full_two_gate_offline_refines_and_ratifies`
- The two out-of-scope residual drift tests also exist:
  - `test_front_door_selection_threading.py::test_run_summary_pack_hash_default_is_byte_identical_to_raw`
  - `test_run_summary_yaml_emit.py::test_clean_trial_run_summary_populated`

**Procedural watch:**

- The pre-S5 spec says **SOP-014 CONCUR-W-F** and dev dispatch cleared, but the canonical monitor file currently shows SOP-013 only; I do not see the named SOP-014 relay in the canonical ledger yet.
- This is not a scope objection because the spec text itself carries the SOP-014 findings/dispositions, but it should be cleaned up before or during dev dispatch so the "read latest ledger before gate crossing" rule has an actual SOP-014 ledger entry to read.

**Finding disposition:**

- **F-1202 CLOSED.**
- **S4 CLOSED / SOP-013 relayed.**
- **F-1401/F-1402 acknowledged as pre-S5 spec findings:** spec correctly incorporates the +2 Irene corpus-absence reds and names the 2 independent drift reds as expected residual out of scope.
- **Pre-S5 procedural watch OPEN:** named SOP-014 relay is not yet visible in the canonical monitor ledger, despite the spec citing it.

**Recommendations:**

1. Before the fresh dev agent starts, relay SOP-014 into the canonical monitor or explicitly record where the SOP-014 full text lives.
2. Keep the pre-S5 implementation exactly fixture + stale-pin refresh. A production-code diff should stop the story and trigger re-scope.
3. Verify the green result from a throwaway worktree/fresh clone: expected end state is 18 reds to exactly 2 residual drift reds.
4. Do not open S5 until the pre-S5 story is committed, pushed, and close-polled.

**Verdict:** `PRE-S5-SPEC-OPEN-FACTS-CHECKED-SOP014-RELAY-WATCH`. S4 is closed; pre-S5 is properly scoped, with a small procedural relay gap to close before dev proceeds.

### POLL-035 - pre-S5 g0-battery committed/pushed; S5 unblocked, not yet visibly open (2026-07-07T00:51:29-04:00)

**Trigger:** heartbeat poll at `2026-07-07T04:51:29.965Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with origin.
- HEAD is now `a1158385`:
  - `feat(canonical-arc-pre-S5): g0-enrichment battery baseline green — studio-smoke-min corpus + gate-inventory pin refresh (S5-open precondition SATISFIED)`
- Worktree is clean except the known excluded/untracked paths:
  - `_bmad-output/artifacts/workbooks-test/`
  - the external/workbook `claude-shadow-monitor-*` ledgers
  - `goal-canonical-arc-s4-onward-2026-07-07.txt`
  - `runs/4fe6073f-c8e2-4836-bb94-759dc5b97bbf/`
  - `runs/a18c2a86-bbdb-48a2-ba63-fb1a653bfaf9/`

**Canonical monitor update:**

- The prior SOP-014 relay watch is closed: the canonical monitor now includes **SOP-014** and **SOP-015**.
- SOP-015 reports all 7 close checks passing, no findings, and `pre-S5 g0-battery DONE`.
- The canonical close line states: `S5 (G0 canonical) UNBLOCKS`; next poll is SOP-016 at the S5 spec pre-dispatch.

**Commit integrity spot-check:**

- Commit scope is exactly the expected pre-S5 set:
  - `course-content/courses/studio-smoke-min/lesson.md`
  - `tests/unit/marcus/cli/test_shim_parser_factory.py`
  - `_bmad-output/implementation-artifacts/canonical-arc-pre-s5-g0-battery-baseline.md`
  - `_bmad-output/implementation-artifacts/canonical-arc-claude-shadow-monitor-2026-07-06.md`
  - `_bmad-output/planning-artifacts/deferred-inventory.md`
- No production app code, manifest, roster, or pipeline files are committed in this change.
- The new fixture is a minimal synthetic one-file outline with one H1 and three H2 sections, each H2 carrying one body line.
- The gate pin now asserts the full exact tuple including `G0R`:
  - `("G0E", "G0R", "G1", "G2B", "G2C", "G3", "G4A", "G4")`
- The commit message records the expected verification:
  - `18 -> 2` in `tests/integration/marcus/` + `tests/unit/marcus/cli/`;
  - residual reds exactly the two pre-existing drift reds (`pack_hash`, `roster_count`);
  - `466 passed`;
  - `app/` + manifest diff empty;
  - ruff `0-new`;
  - fresh-clone/throwaway-worktree green.

**S5 status:**

- I do **not** see a new S5 spec artifact yet in `_bmad-output/implementation-artifacts/`.
- Therefore this poll should be read as: **pre-S5 precondition complete; S5 may now open; S5 has not yet visibly crossed its spec pre-dispatch gate.**

**Finding disposition:**

- **S4 CLOSED.**
- **F-1202 CLOSED.**
- **pre-S5 g0-battery CLOSED.**
- **F-1401 CLOSED:** the +2 Irene corpus-absence reds were incorporated into the green battery.
- **F-1402 CLOSED-AS-FILED:** the two independent drift reds remain out of scope and are now filed as follow-ons in `deferred-inventory.md`.
- **S5 WATCH OPEN:** await S5 spec/SOP-016; enforce the green-light row boundaries before dev.

**Recommendations:**

1. Start S5 from clean checkpoint `a1158385`; do not treat the pre-S5 fixture story as S5 implementation.
2. At SOP-016, verify the S5 spec explicitly performs the required first-pause-G1 grep, pre-G1 resume-walk audit, and Tier-1-vs-Tier-2/default-flip ruling before dev opens.
3. Keep the two pre-S5 residual drift filings out of S5 unless they directly block S5's required evidence; they were intentionally filed as separate follow-ons.
4. Preserve the Marcus-SPOC product boundary: S5 should make G0 canonical in the production conversation arc, not optimize for proofing/concierge artifacts.

**Verdict:** `PRE-S5-CLOSED-S5-UNBLOCKED-AWAITING-SOP016`. The Claude team handled the prerequisite cleanly and can now open S5; no S5 implementation is visible yet.

### POLL-036 - S5-3a spec opens; SOP-016 caught missed offline suite (2026-07-07T01:02:55-04:00)

**Trigger:** heartbeat poll at `2026-07-07T05:01:30.063Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with origin.
- HEAD remains `a1158385`:
  - `feat(canonical-arc-pre-S5): g0-enrichment battery baseline green - studio-smoke-min corpus + gate-inventory pin refresh (S5-open precondition SATISFIED)`
- No production/test implementation diff is visible yet for S5:
  - `git diff --name-status` shows only `M _bmad-output/implementation-artifacts/canonical-arc-claude-shadow-monitor-2026-07-06.md`.
- New S5 spec artifact is present but untracked:
  - `_bmad-output/implementation-artifacts/canonical-arc-s5-3a-first-pause-migration.md`
- Known excluded/untracked paths remain outside commits:
  - `_bmad-output/artifacts/workbooks-test/`
  - the external/workbook `claude-shadow-monitor-*` ledgers
  - `goal-canonical-arc-s4-onward-2026-07-07.txt`
  - `runs/4fe6073f-c8e2-4836-bb94-759dc5b97bbf/`
  - `runs/a18c2a86-bbdb-48a2-ba63-fb1a653bfaf9/`

**Canonical monitor update:**

- The canonical monitor now includes **SOP-016 - S5-3a first-pause-migration spec pre-dispatch review**.
- SOP-016 independently re-derived the blast radius across all `tests/`, not just the originally listed integration/composition directories.
- Verdict is `CONCUR-WITH-FINDINGS`; dev dispatch is cleared only after applying F-1601 and F-1602 into the spec.

**S5-3a spec status:**

- Spec status: `READY-FOR-DEV`.
- This is S5 split part **3a** only: first-pause integration-suite migration.
- The S5 default flip stays out of scope for 3a:
  - no production-code change;
  - no manifest edit;
  - no default flip;
  - no live witness in 3a;
  - `MARCUS_G0_ENRICHMENT_ACTIVE` remains default-OFF at 3a close.
- 3a's acceptance surface is test migration/env explicitness so 3b can flip the unset-env default without breaking inherited first-pause-G1 tests.

**SOP-016 findings carried forward:**

- **F-1601 [HIGH, APPLIED / WATCH THROUGH DEV]:** the original grep scope missed `tests/marcus/orchestrator/test_start_walk_no_motion.py:90`, which asserts `paused_gate == "G1"` on the real `run_production_trial` in the offline default suite. It has been added to the 3a migration set, bringing the offline set to 8 suites.
- **F-1602 [MEDIUM, APPLIED / WATCH AT 3B]:** `tests/live/test_production_trial_smoke_with_gate.py:40` also asserts first pause `G1`; it does not block offline 3a, but 3b's live witness leg must migrate it.
- **F-1603..F-1608 [INFO, CONFIRMED]:** exclusions are sound, no shared first-pause helper exists, the 3a/3b split is justified, AC-1 is env-independence rather than forbidden both-worlds-green coverage, scope fence is clean, and parity-pin preservation is a legitimate watch.

**Eight offline first-pause suites now in 3a scope:**

1. `tests/integration/marcus/test_braid_s3_research_wiring.py`
2. `tests/integration/marcus/test_gate_bypass_refusal.py`
3. `tests/integration/marcus/test_pre_gate_marcus_langsmith_trace.py`
4. `tests/integration/marcus/test_production_runner_error_pause_recover.py`
5. `tests/integration/marcus/test_production_runner_invocation.py`
6. `tests/marcus/orchestrator/test_start_walk_no_motion.py`
7. `tests/composition/test_gary_parity_walk_pin.py`
8. `tests/composition/test_real_cd_graph_walk_pin.py`

**Finding disposition:**

- **S4 CLOSED.**
- **pre-S5 g0-battery CLOSED.**
- **F-1401 CLOSED.**
- **F-1402 CLOSED-AS-FILED.**
- **S5 WATCH moves from awaiting spec to `S5-3A-SPEC-OPEN / AWAITING DEV`.**
- **F-1601 WATCH:** ensure dev T1 re-greps across all `tests/` and the missed orchestrator suite is actually migrated.
- **F-1602 WATCH:** carry the live first-pause-G1 suite into S5-3b; do not let 3a completion erase it.

**Recommendations:**

1. Before dev edits, re-grep first-pause `G1` assertions across all `tests/`, exactly as the amended spec requires.
2. Keep 3a test-only. Any `app/`, `state/config/`, or manifest diff should stop the story and trigger re-scope.
3. In `test_gary_parity_walk_pin.py`, allow only first-pause env-expression changes; preserve the S3/S4 parity/fail-loud assertions.
4. Carry `tests/live/test_production_trial_smoke_with_gate.py:40` explicitly into S5-3b's live witness migration.
5. Do not call S5 done after 3a. This is the migration step before the default flip; 3b owns the canonical unset-env live proof.

**Verdict:** `S5-3A-SPEC-OPEN-CONCUR-WITH-FINDINGS-AWAITING-DEV`. The Claude team has started S5 in the right split form; no implementation is visible yet, and the main risk is ensuring the F-1601/F-1602 blast-radius corrections survive into dev and 3b.

### POLL-037 - S5-3a dev diff appears; eight expected suites pinned OFF, no production drift (2026-07-07T01:12:08-04:00)

**Trigger:** heartbeat poll at `2026-07-07T05:11:30.220Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with origin.
- HEAD remains `a1158385`; no new commit after pre-S5.
- S5-3a implementation is now visible in the working tree.
- `git diff --name-status` shows exactly the canonical monitor plus the eight expected test files:
  - `_bmad-output/implementation-artifacts/canonical-arc-claude-shadow-monitor-2026-07-06.md`
  - `tests/composition/test_gary_parity_walk_pin.py`
  - `tests/composition/test_real_cd_graph_walk_pin.py`
  - `tests/integration/marcus/test_braid_s3_research_wiring.py`
  - `tests/integration/marcus/test_gate_bypass_refusal.py`
  - `tests/integration/marcus/test_pre_gate_marcus_langsmith_trace.py`
  - `tests/integration/marcus/test_production_runner_error_pause_recover.py`
  - `tests/integration/marcus/test_production_runner_invocation.py`
  - `tests/marcus/orchestrator/test_start_walk_no_motion.py`
- Scope fence check: `git diff -- app/ state/config/ pipeline-manifest.yaml` is empty.
- `git diff --check` reports only a CRLF-normalization warning for `tests/composition/test_gary_parity_walk_pin.py`, not whitespace errors.

**Canonical monitor update:**

- The working-tree canonical monitor now includes SOP-015 and SOP-016 relays.
- I do not see SOP-017 yet, so this poll treats the S5-3a diff as in-progress dev, not dev-complete.

**Implementation shape observed:**

- Each of the eight expected suites now has an autouse fixture setting:
  - `MARCUS_G0_ENRICHMENT_ACTIVE=0`
- The previously missed F-1601 suite is included:
  - `tests/marcus/orchestrator/test_start_walk_no_motion.py`
- The modifications are additive comments/fixtures, with no observed assertion deletions in the diff.
- The two parity/composition files keep their G1 first-pause assertions and add only an explicit OFF env pin; this is consistent with AC-5 so far because parity/fail-loud teeth are not visibly weakened.
- The current implementation is OFF-pin based across all eight suites. That appears valid for dormant-path/orthogonal-subject coverage, but the close review should require the Completion Notes test-disposition ledger to justify each row as either kill-switch/escape-hatch or G0-irrelevant dormant-path coverage.

**Blast-radius grep spot-check:**

- Remaining real first-pause `paused_gate == "G1"` assertions are now in:
  - the eight migrated/off-pinned suites, plus
  - `tests/live/test_production_trial_smoke_with_gate.py`, the known F-1602 3b handoff.
- The grep also surfaces excluded/synthetic/resume/custom-manifest G1 references already called out by SOP-016; no new unaccounted offline first-pause suite is apparent from this spot-check.

**Finding disposition:**

- **F-1601 MOVING TOWARD CLOSED:** the missed orchestrator suite is now in the diff with an explicit OFF pin. Final closure needs SOP-017/dev-complete evidence and the forced-default-ON robustness run.
- **F-1602 STILL OPEN FOR 3B:** the live smoke-with-gate suite remains unchanged and must be migrated in 3b's live witness leg.
- **S5-3A WATCH:** no production-code drift observed; no commit yet; no SOP-017 yet.

**Recommendations:**

1. At SOP-017, require the dev-complete evidence to show the RED-first forced-ON failure before the pins, then default-OFF and forced-ON green after the pins.
2. Require the Completion Notes ledger to justify all eight OFF pins. The wording should not overclaim canonical G0E coverage; that belongs to 3b.
3. Keep `tests/live/test_production_trial_smoke_with_gate.py:40` as an explicit 3b handoff, not an accidental leftover.
4. Before commit, verify `git diff -- app/ state/config/ pipeline-manifest.yaml` remains empty and review the CRLF warning in `test_gary_parity_walk_pin.py` so the commit does not create noisy line-ending churn.

**Verdict:** `S5-3A-DEV-IN-PROGRESS-SCOPE-CLEAN-F1601-IN-DIFF`. The Claude team is executing the 3a split in the right files and has not breached production scope; closure still depends on SOP-017 evidence, the disposition ledger, and both-env robustness proof.

### POLL-038 - S5-3a committed/pushed; S5-3b default-flip spec opens (2026-07-07T01:22:10-04:00)

**Trigger:** heartbeat poll at `2026-07-07T05:21:30.331Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with origin.
- HEAD is now `721cce04`:
  - `test(canonical-arc-S5-3a): first-pause integration-suite migration - env-independence for the 8 offline first-pause-G1 suites (3b flip prep)`
- Tracked worktree is clean.
- Known excluded/untracked paths remain outside commits:
  - `_bmad-output/artifacts/workbooks-test/`
  - the external/workbook `claude-shadow-monitor-*` ledgers
  - `goal-canonical-arc-s4-onward-2026-07-07.txt`
  - `runs/4fe6073f-c8e2-4836-bb94-759dc5b97bbf/`
  - `runs/a18c2a86-bbdb-48a2-ba63-fb1a653bfaf9/`
- New untracked S5-3b spec artifact is present:
  - `_bmad-output/implementation-artifacts/canonical-arc-s5-3b-g0-default-flip.md`

**S5-3a commit integrity spot-check:**

- Commit scope is coherent and test-only:
  - S5-3a story spec added.
  - canonical monitor ledger updated.
  - the same eight first-pause-G1 offline suites were modified.
- Protected production scope held:
  - `git diff a1158385..721cce04 -- app/ state/config/ pipeline-manifest.yaml` is empty.
- Protected strays stayed out:
  - no run dirs, workbook-test artifacts, external monitor ledgers, or goal launcher appear in `git show --name-only HEAD`.
- Numstat shows additive-only test/spec changes, including 14 inserted lines in the previously missed F-1601 suite.

**S5-3a close evidence observed:**

- The commit message records:
  - forced-default-ON simulation produced 19 RED before migration;
  - both env states green after migration;
  - `696 passed / 4 pre-existing baseline reds, 0 new`;
  - `app/` + manifest diff empty;
  - `test_gary_parity_walk_pin.py` had 0 removed lines and parity/fail-loud teeth byte-intact;
  - 3b default flip + live G0E/G0R witness is unblocked.
- The S5-3a story status is now `DONE` and records the same evidence.
- The story status also explains the all-OFF disposition: forcing ON in 3a routes through directive composition requiring a corpus directory, while these offline suites pass README-file inputs; canonical G0E-first proof belongs to 3b.

**Procedural watch:**

- The canonical monitor file still visibly stops at **SOP-016**. I do not see an explicit **SOP-017** section by name in the canonical monitor, even though the S5-3a story status and commit message both cite `SOP-017 close poll`.
- The S5-3a story records a disposition summary, but I do not see a separate per-test Completion Notes table with one row per touched suite. The commit message has enough summary to understand the decision, but the original AC-2 asked for a ledger row per touched test.
- These are documentation/procedure watches, not evidence that the test-only migration is wrong. They should be reconciled before or during S5-3b pre-dispatch so the "read latest monitor ledger before gate crossing" rule has a canonical close relay to read.

**S5-3b spec status:**

- New spec: `_bmad-output/implementation-artifacts/canonical-arc-s5-3b-g0-default-flip.md`.
- Status: `READY-FOR-DEV`, but it explicitly awaits **SOP-018 monitor pre-dispatch poll**.
- Scope is materially broader than 3a:
  - flip `g0_enrichment_active()` default from unset->False to unset->True;
  - keep explicit falsy env values as kill-switch;
  - keep `g0_dispatch_live()` default-OFF for deterministic default tests;
  - run a full offline flip-and-sweep, not just the 3a eight;
  - add G0E/G0R narration/witness surface;
  - define/witness live dispatch arming discipline;
  - defer T6c by default to preserve Tier-1/no-manifest-edit scope.
- AC-L is correctly marked as live and required: canonical unset-env walk must prove G0E -> G0R -> G1 with assert-unset preamble, plus deterministic-vs-live dispatch witness.

**Finding disposition:**

- **F-1601 CLOSED for 3a:** the missed orchestrator suite is committed in the 3a migration set.
- **F-1602 OPEN / 3B-BLOCKING WATCH:** `tests/live/test_production_trial_smoke_with_gate.py:40` remains the named live-suite handoff and must be migrated/proven in 3b.
- **S5-3A CLOSED subject to procedural reconciliation:** code/evidence/commit scope are clean; explicit SOP-017 relay and per-test ledger formatting should be restored in canonical docs.
- **S5-3B WATCH OPEN:** await SOP-018 before dev dispatch.

**Recommendations:**

1. Before crossing S5-3b pre-dispatch, add or relay an explicit SOP-017 close section in the canonical monitor, or clearly state why the S5-3a story status/commit message is the close record.
2. Preserve the S5-3b D2 flip-and-sweep requirement. The first run after the default flip must enumerate the true residual across all `tests/`, not assume 3a found everything.
3. Treat F-1602 as a live-witness blocker for 3b: the old `paused_gate == "G1"` live smoke-with-gate assertion must move to the canonical G0E/G0R sequence.
4. Hold the Tier-1 fence unless the party explicitly reconsents: no `pipeline-manifest.yaml` edit and defer T6c by default.
5. For AC-L, require an assert-unset env preamble. A set-value ON run is not equivalent to proving the new default.

**Verdict:** `S5-3A-COMMITTED-PUSHED-SCOPE-CLEAN-S5-3B-SPEC-OPEN-AWAITING-SOP018`. The Claude team has closed the 3a migration cleanly at the code/commit level and is correctly opening 3b as the real default-flip/live-witness story; the main risks are canonical SOP-017 documentation hygiene and ensuring 3b does a real full-suite flip sweep before implementation proceeds.

### POLL-039 - SOP-017 relay lands; S5-3b still pre-dispatch awaiting SOP-018 (2026-07-07T01:31:58-04:00)

**Trigger:** heartbeat poll at `2026-07-07T05:31:30.480Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with origin.
- HEAD remains `721cce04`.
- No S5-3b code/test implementation diff is visible yet.
- Tracked diff is only:
  - `M _bmad-output/implementation-artifacts/canonical-arc-claude-shadow-monitor-2026-07-06.md`
- Untracked S5-3b spec remains present:
  - `_bmad-output/implementation-artifacts/canonical-arc-s5-3b-g0-default-flip.md`
- Known excluded strays remain untracked and outside scope.

**Canonical monitor update:**

- The prior procedural watch is now resolved in the working tree: the canonical monitor includes **SOP-017 - S5-3a dev-complete + CLOSE verification**.
- SOP-017 closes S5-3a cleanly:
  - commit `721cce04`;
  - exact 8 migrated test files + spec + ledger;
  - `app/`, `state/config/`, `parity.py`, and manifest untouched;
  - no deleted/weakened assertions;
  - 61 pass at default-OFF and forced-ON;
  - 19-RED load-bearing witness reproduced at base;
  - 696 passed / 4 pre-existing reds, 0 new.
- The canonical monitor now says: **S5-3a DONE STANDS. 3b UNBLOCKS. Next poll: SOP-018 at the 3b spec pre-dispatch.**

**S5-3b spec fact-check:**

- The spec's core flip premise matches current code:
  - `g0_enrichment_active()` currently returns true only for explicit truthy env values; unset is default-OFF.
  - `g0_dispatch_live()` currently returns true only for explicit truthy env values; unset is default-OFF.
  - `irene_refinement_active()` rides the same G0-enrichment activation path per prior SOP-016 finding.
- The T6c deferral anchor exists in `deferred-inventory.md` as `t6c-post-pass1-plan-review-wake`; the spec's recommendation to defer T6c is consistent with keeping S5-3b Tier-1/no-manifest-edit.
- The S3 deferred filings remain present:
  - `gamma-dispatch-retry-taxonomy-deterministic-variance`
  - `run-artifact-split-across-runs-roots`

**S5-3b status:**

- Spec status is still `READY-FOR-DEV`, but it explicitly awaits **SOP-018 monitor pre-dispatch poll**.
- No SOP-018 relay is visible yet.
- No dev-agent changes are visible yet.

**Finding disposition:**

- **S5-3a CLOSED:** SOP-017 relay now present, so the previous documentation hygiene watch is closed.
- **F-1601 CLOSED:** included and committed in S5-3a.
- **F-1602 OPEN / 3B WATCH:** live smoke-with-gate first-pause-G1 migration remains a 3b obligation.
- **S5-3B WATCH OPEN:** pre-dispatch only; await SOP-018 before treating dev as cleared.

**Recommendations:**

1. SOP-018 should explicitly verify the 3b spec's full-suite flip-and-sweep obligation, not just the known 3a eight.
2. SOP-018 should harden AC-L wording around the assert-unset preamble; set-value ON does not prove the new default.
3. Keep T6c deferred unless the party explicitly accepts a manifest-editing lockstep sub-story.
4. Carry F-1602 into the live witness design: the old live `G1` first-pause expectation must become a canonical G0E/G0R/G1 sequence or be retired with an explicit replacement witness.
5. Since the SOP-017 relay is currently an uncommitted canonical-monitor modification after `721cce04`, make sure it is deliberately included in the next documentation/spec commit and not lost.

**Verdict:** `SOP017-RELAYED-S5-3B-PRE-DISPATCH-AWAITING-SOP018`. The team has cleaned up the S5-3a close record; S5-3b has a coherent spec draft, but no implementation should proceed until SOP-018 validates the flip sweep, live default witness, and Tier-1 fence.

### POLL-040 - SOP-018 clears S5-3b; early default-flip code lands, broader 3b surfaces pending (2026-07-07T01:41:55-04:00)

**Trigger:** heartbeat poll at `2026-07-07T05:41:30.624Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with origin.
- HEAD remains `721cce04`.
- S5-3b dev has started; visible tracked diffs:
  - `M _bmad-output/implementation-artifacts/canonical-arc-claude-shadow-monitor-2026-07-06.md`
  - `M _bmad-output/planning-artifacts/deferred-inventory.md`
  - `M app/marcus/orchestrator/g0_enrichment_wiring.py`
- S5-3b spec remains untracked:
  - `_bmad-output/implementation-artifacts/canonical-arc-s5-3b-g0-default-flip.md`
- No test diff, production-runner diff, CLI/preset diff, mode-stamp diff, narration diff, or live evidence artifact is visible yet.
- `git diff --check` reports only the existing CRLF-normalization warning on `deferred-inventory.md`; no whitespace errors.

**Canonical monitor update:**

- **SOP-018** is now relayed.
- Verdict: `CONCUR-WITH-FINDINGS`; 3b spec amended and dev dispatch cleared.
- F-1801 was escalated to a focused 4-seat party round and resolved 4/4 for **Reading A**:
  - G0E/G0R HIL gate structure is canonical on every unset-env run.
  - Live LLM enrichment content remains operator-armed, not default-on.
  - `g0_dispatch_live` stays default-OFF.
  - Required riders: first-class `--g0-dispatch-live` product arm, resolved-mode stamp, fail-loud ambiguity handling, deterministic "live available" affordance, two-lane AC-L witness, and future Tier-2 filing.
- F-1802/F-1803/F-1804/F-1805 were applied into the spec:
  - explicit truth table;
  - sweep by breakage class;
  - assert-unset after dotenv load;
  - real CLI resume path for the live sequence.

**Current implementation observed:**

- `app/marcus/orchestrator/g0_enrichment_wiring.py` now flips `g0_enrichment_active()` to canonical default-ON by enumerating only explicit kill-switch values:
  - kill-switch set: `{"0", "false", "no", "off"}`;
  - unset/empty/whitespace/unrecognized/truthy all resolve ON by `not in G0_ENRICHMENT_KILL_SWITCH_VALUES`.
- The module comment now correctly records that S5-3a cashed the migration prerequisite and that `g0_dispatch_live` is not flipped.
- `g0_dispatch_live()` itself is unchanged/default-OFF.
- `irene_refinement_active()` delegates to `g0_enrichment_active()` through `irene_refinement_wiring.py`, so the one flip wakes G0R as expected.
- `deferred-inventory.md` adds the required future follow-on:
  - `g0-production-default-dispatch-live-decision`.

**Important in-progress red watch:**

- Existing committed tests still contain pre-flip expectations that unset env is dormant:
  - `tests/integration/marcus/test_g0_enrichment_brick.py`
  - `tests/integration/marcus/test_irene_refinement_brick.py`
- Because no test migration is visible yet, this implementation is likely red right now. That is expected mid-story, but SOP-019 must show RED-first evidence and then update/pin the truth-table and affected tests.

**Finding disposition:**

- **SOP-018 CLOSED:** pre-dispatch poll and party ratification are present; dev dispatch is cleared.
- **F-1801 CLOSED-IN-SPEC / WATCH-IN-DEV:** Reading A is ratified and future Tier-2 filing exists; dev still must implement CLI arm, mode stamp, fail-loud ambiguity, and live-available affordance.
- **F-1802 WATCH:** flip code appears to match the explicit falsy-set contract; tests are not visible yet.
- **F-1803 WATCH:** no full-suite flip-and-sweep evidence visible yet.
- **F-1804/F-1805 WATCH:** no AC-L evidence visible yet.
- **F-1602 STILL OPEN:** live smoke-with-gate handoff remains a 3b live-witness obligation.

**Recommendations:**

1. Treat the current `g0_enrichment_wiring.py` flip as only the first slice of 3b. Do not approach dev-complete until tests, sweep evidence, CLI arm, mode-stamp, narration/affordance, and AC-L artifacts exist.
2. Update the G0/Irene brick tests deliberately against the new truth table; the old `delenv -> False` assertions should become `delenv -> True` under AC-1.
3. SOP-019 should enumerate residual breakage by class, not raw count, and show the full-suite flip sweep did not hide a shared helper issue.
4. Keep `pipeline-manifest.yaml` untouched; any manifest edit would leave the ratified Tier-1 lane.
5. For AC-L, insist on both lanes: assert-unset deterministic default with receipt/affordance and real CLI `--g0-dispatch-live` armed live content.

**Verdict:** `S5-3B-DEV-IN-PROGRESS-FLIP-LANDED-BROADER-SURFACES-PENDING`. The team has crossed SOP-018 correctly and started the default flip in the right file; the main risk is now completing the full 3b surface instead of stopping at the env-function change.

### POLL-041 - S5-3b adds truth-table test + mode-stamp plumbing; CLI/live surfaces still absent (2026-07-07T01:52:22-04:00)

**Trigger:** heartbeat poll at `2026-07-07T05:51:30.786Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with origin.
- HEAD remains `721cce04`.
- Visible tracked diffs:
  - `M _bmad-output/implementation-artifacts/canonical-arc-claude-shadow-monitor-2026-07-06.md`
  - `M _bmad-output/maps/coverage-manifest/lesson-plan-envelope-coverage-manifest.json`
  - `M _bmad-output/planning-artifacts/deferred-inventory.md`
  - `M app/marcus/orchestrator/g0_enrichment_wiring.py`
- New untracked test:
  - `tests/unit/marcus/orchestrator/test_g0_enrichment_default_flip.py`
- S5-3b spec remains untracked:
  - `_bmad-output/implementation-artifacts/canonical-arc-s5-3b-g0-default-flip.md`
- No diff is visible in `production_runner.py`, CLI/preset files, `pipeline-manifest.yaml`, live evidence artifacts, or the 3a migrated suites.

**Current implementation observed:**

- `g0_enrichment_active()` remains default-ON using the explicit kill-switch set.
- `g0_dispatch_live()` remains default-OFF and documents the party-ratified Reading A.
- New mode-stamp constants/functions exist:
  - `G0_ENRICHMENT_MODE_LIVE = "live"`
  - `G0_ENRICHMENT_MODE_DETERMINISTIC = "deterministic-recorded"`
  - `ENRICHMENT_MODE_KEY = "enrichment_mode"`
  - `resolve_enrichment_mode(model_id)`
- `resolve_enrichment_mode()` maps the live model id to `live`, the deterministic marker to `deterministic-recorded`, and fail-loud raises on ambiguity.
- `run_g0_enrichment()` stamps `enrichment_mode` into the card payload and as a top-level contribution output key.
- The F-1801 future filing exists in `deferred-inventory.md`: `g0-production-default-dispatch-live-decision`.

**New test coverage observed:**

- `tests/unit/marcus/orchestrator/test_g0_enrichment_default_flip.py` covers the F-1802 truth table:
  - unset env -> active;
  - empty/whitespace/unrecognized/truthy -> active;
  - explicit falsy tokens -> dormant;
  - exact falsy set;
  - G0R delegation through `irene_refinement_active()`.
- This test file is currently untracked; if it remains part of the story, it must be staged/committed intentionally.

**Watches / gaps:**

- **SOP-019 not present.** This is still in-progress dev, not dev-complete.
- **F-1801 partial only:** mode-stamp plumbing and future filing are visible, but the first-class `marcus_spoc --g0-dispatch-live` product arm is not visible, and no production-runner or CLI/preset change is present.
- **D3 live-available affordance not visible:** code comments say the deterministic stamp drives Dan's affordance, but I do not see actual operator-facing G0E/G0R text yet.
- **F-1803 not evidenced:** no full-suite flip-and-sweep evidence or residual class ledger is visible.
- **F-1804/F-1805 not evidenced:** no AC-L artifacts, assert-unset-after-dotenv proof, or real CLI resume-path proof is visible.
- **F-1602 still open:** the live smoke-with-gate `G1` expectation remains a 3b live-witness handoff.
- **Coverage manifest timestamp-only churn:** `_bmad-output/maps/coverage-manifest/lesson-plan-envelope-coverage-manifest.json` currently changes only `generated_at`. Unless this is an intentional regen artifact for S5-3b, it should be excluded to avoid noisy metadata churn.

**Recommendations:**

1. Keep treating this as mid-story. Do not call SOP-019 until the CLI arm, operator-facing affordance, sweep ledger, and AC-L evidence exist.
2. Add focused tests for `resolve_enrichment_mode()` and the receipt/card stamp, including fail-loud ambiguity. The helper is load-bearing and currently only indirectly visible.
3. Implement and test the actual `--g0-dispatch-live` product surface; relying on the env seam alone would not satisfy the F-1801 party rider.
4. Implement/test the deterministic `live-available` affordance in the G0E/G0R operator surface, not just comments.
5. Resolve the timestamp-only coverage-manifest diff before commit unless the team deliberately wants to include a broader regen with rationale.

**Verdict:** `S5-3B-DEV-IN-PROGRESS-F1802-COVERED-F1801-PARTIAL`. The team is making real progress on the default flip and mode-stamp foundation, but the product-facing and live-proof portions of 3b are still outstanding.

### POLL-042 - CLI arm and G0R narration appear; still no SOP-019/live evidence (2026-07-07T02:02:46-04:00)

**Trigger:** heartbeat poll at `2026-07-07T06:01:30.904Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with origin.
- HEAD remains `721cce04`.
- Visible tracked diffs:
  - `M _bmad-output/implementation-artifacts/canonical-arc-claude-shadow-monitor-2026-07-06.md`
  - `M _bmad-output/maps/coverage-manifest/lesson-plan-envelope-coverage-manifest.json`
  - `M _bmad-output/planning-artifacts/deferred-inventory.md`
  - `M app/marcus/cli/marcus_spoc.py`
  - `M app/marcus/orchestrator/g0_enrichment_wiring.py`
- S5-3b spec and truth-table unit test remain untracked:
  - `_bmad-output/implementation-artifacts/canonical-arc-s5-3b-g0-default-flip.md`
  - `tests/unit/marcus/orchestrator/test_g0_enrichment_default_flip.py`
- No diff is visible in `app/marcus/orchestrator/production_runner.py`, `pipeline-manifest.yaml`, live evidence artifacts, or the 3a migrated integration suites.

**Canonical monitor update:**

- No SOP-019 entry is visible yet.
- Latest canonical monitor material remains SOP-018: dev dispatch cleared with F-1801/F-1802/F-1803/F-1804/F-1805 riders applied into the S5-3b spec.

**Current implementation observed:**

- `app/marcus/cli/marcus_spoc.py` now exposes the required product arm:
  - `--g0-dispatch-live` CLI flag;
  - when present, sets `G0_DISPATCH_LIVE_ENV` to `"1"` through the shared `g0_enrichment_wiring` constant.
- The CLI now adds S5-3b operator narration:
  - G0E Beat 2 material narration;
  - G0R Beat 3 contract narration;
  - deterministic-recorded "live available" affordance when `g0-enrichment.json` reports `enrichment_mode == "deterministic-recorded"`;
  - a G0R narration branch that reads `irene-refinement.json` and reports refined LO/delta/flag counts.
- `g0_enrichment_wiring.py` still carries the default-ON truth-table flip, the default-OFF `g0_dispatch_live()` contract, and the `enrichment_mode` resolver/stamp.
- `deferred-inventory.md` still contains the future `g0-production-default-dispatch-live-decision` filing required by the F-1801 party resolution.

**Finding disposition:**

- **SOP-018 CLOSED:** no regression; the pre-dispatch review remains relayed and applied.
- **F-1801 MOVING TO DEV-PROOF:** the mode stamp, CLI arm, deterministic affordance, and future filing now all appear in code. Remaining risk is verification: prove the CLI flag affects the real start/resume path and prove both AC-L lanes.
- **F-1802 WATCH:** truth-table code and unit test are present, but the unit test is untracked and not yet tied to SOP-019 evidence.
- **F-1803 OPEN:** no full-suite flip-and-sweep evidence or residual-class ledger is visible.
- **F-1804/F-1805 OPEN:** no assert-unset-after-dotenv witness and no real CLI resume-path/live-lane evidence is visible.
- **F-1602 OPEN:** no live smoke-with-gate migration/evidence artifact is visible yet.

**Recommendations:**

1. Add focused tests for the new CLI surface: `--g0-dispatch-live` should set the shared env seam and should be proven on the same real CLI path used by AC-L, not only by argument parsing.
2. Add tests for `resolve_enrichment_mode()` and for receipt/card stamping, including fail-loud ambiguity. The mode stamp is now a product contract.
3. Add tests for G0E/G0R narration and the deterministic-only live-available affordance; confirm live mode does not show the deterministic rerun prompt.
4. Before SOP-019, publish the full-suite flip sweep by breakage class and the two AC-L artifacts: unset deterministic lane and armed live lane.
5. Resolve or explicitly justify the timestamp-only coverage-manifest diff before commit; otherwise it remains noisy metadata churn.
6. Keep `pipeline-manifest.yaml` untouched unless the party explicitly reopens Tier-1 scope; current S5-3b remains a runtime-default flip story.

**Verdict:** `S5-3B-DEV-IN-PROGRESS-PRODUCT-SURFACE-APPEARS-EVIDENCE-PENDING`. The Claude team has now implemented most of the F-1801 product-facing surface, but S5-3b should not be considered close-ready until tests, sweep evidence, and live AC-L witnesses land.

### POLL-043 - S5-3b correctly STOPped; S5-3a.2 migration split opens (2026-07-07T02:13:21-04:00)

**Trigger:** heartbeat poll at `2026-07-07T06:11:31.112Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with origin.
- HEAD remains `721cce04`.
- Visible tracked diffs are now limited to governance/planning artifacts:
  - `M _bmad-output/implementation-artifacts/canonical-arc-claude-shadow-monitor-2026-07-06.md`
  - `M _bmad-output/planning-artifacts/deferred-inventory.md`
- No current diff is visible under `app/`, `tests/`, `state/config/`, or `pipeline-manifest.yaml`.
- Untracked active specs:
  - `_bmad-output/implementation-artifacts/canonical-arc-s5-3a2-file-corpus-migration.md`
  - `_bmad-output/implementation-artifacts/canonical-arc-s5-3b-g0-default-flip.md`
- Strays remain untracked and excluded from commit scope:
  - `_bmad-output/artifacts/workbooks-test/`
  - the operator monitor ledgers
  - `runs/4fe6073f-c8e2-4836-bb94-759dc5b97bbf/`
  - `runs/a18c2a86-bbdb-48a2-ba63-fb1a653bfaf9/`

**Canonical monitor update:**

- New material relayed after SOP-018: **S5-3b dev STOP + RE-SCOPE party round**.
- The 3b dev agent correctly hit the STOP gate during T1 flip-and-sweep.
- Actual flip blast radius was **24 tests / 9 suites beyond the S5-3a eight**, not the earlier estimated ~0-5.
- Root cause is one class: tests passing a README file as `corpus_path`, which only worked while G0E was dormant; with G0E awake, the real code expects a corpus directory and raises `DirectiveCompositionError`.
- Party re-scope consensus:
  - split out **S5-3a.2** as a migration-only story;
  - keep the default flip parked until 3a.2 is green;
  - file the real SPOC follow-on `g0-single-file-corpus-opaque-crash-legibility`;
  - return to S5-3b as a near-empty default-flip commit plus two-lane live witness.

**S5-3a.2 spec observed:**

- Status: `READY-FOR-DEV`; awaits SOP-019 monitor pre-dispatch poll.
- Scope is migration-only and test-only:
  - 22 downstream-subject tests get explicit per-suite `MARCUS_G0_ENRICHMENT_ACTIVE=0` pins, after confirming enrichment-orthogonality;
  - 2 feature-flag-contract tests are re-contracted, not mechanically pinned, because their old default-OFF premise is inverted by 3b.
- Binding acceptance points:
  - 24-row test-disposition ledger;
  - `git diff -- app/ state/config/` must remain empty;
  - forced-default-ON full-suite simulation must show zero remaining flip-caused reds;
  - no live witness for 3a.2 because it is test-only; S5-3b still owns live G0E/G0R.

**Deferred filings observed:**

- `g0-single-file-corpus-opaque-crash-legibility` is newly filed and correctly framed as a Marcus-SPOC product concern, not a proofing-run accommodation.
- `g0-production-default-dispatch-live-decision` is also filed as a future Tier-2 operator-vision decision, preserving the F-1801 Reading A boundary.

**Finding disposition:**

- **F-1801 still open-to-3b:** product-surface implementation remains parked with the flip; 3b still must prove CLI arm, mode stamp, affordance, and live/deterministic AC-L lanes.
- **F-1802 still open-to-3b:** truth-table default flip still belongs to the parked 3b commit.
- **F-1803 revised:** the earlier residual estimate was wrong; the new required migration story is an appropriate correction, not a process failure.
- **F-1804/F-1805 still open-to-3b:** live evidence remains pending after 3a.2.
- **New watch:** S5-3a.2 must not quietly become a broad autouse or directory-fixture rewrite; Murat's per-suite disposition is the safety rail.

**Recommendations:**

1. SOP-019 should verify the 24-test set independently before dev starts, including whether a 25th appears under forced-ON re-derivation.
2. Require the 24-row ledger before 3a.2 close. Each row should state class, disposition, rationale, and replacement/default-ON witness for the two re-contract tests.
3. Keep 3a.2 strictly test-only: no `app/`, `state/config/`, manifest, or production-runtime diffs.
4. For the 22 downstream tests, prefer explicit per-suite pins over broader fixtures; broad autouse would risk masking future canonical-path coverage.
5. For the 2 feature-flag tests, reject mechanical pin-only patches. They need an explicit ON/default-positive witness as specified.
6. Preserve the parked 3b patch discipline: re-apply only after 3a.2 closes, then rerun the default flip sweep and live AC-L witnesses from the migrated baseline.

**Verdict:** `S5-3A2-OPENED-BY-CORRECT-STOP-GATE`. The Claude team handled the 3b blast-radius surprise correctly by stopping, re-scoping, and isolating a migration story; the main risk now is over-broad test pinning or losing the 24-row disposition discipline.

### POLL-044 - S5-3a.2 still pre-dispatch; manifest timestamp churn returns (2026-07-07T02:23:02-04:00)

**Trigger:** heartbeat poll at `2026-07-07T06:21:31.229Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with origin.
- HEAD remains `721cce04`.
- No new commits since S5-3a close.
- Visible tracked diffs:
  - `M _bmad-output/implementation-artifacts/canonical-arc-claude-shadow-monitor-2026-07-06.md`
  - `M _bmad-output/maps/coverage-manifest/lesson-plan-envelope-coverage-manifest.json`
  - `M _bmad-output/planning-artifacts/deferred-inventory.md`
- No current diff is visible under `app/`, `tests/`, `state/config/`, or `pipeline-manifest.yaml`.
- Untracked active specs remain:
  - `_bmad-output/implementation-artifacts/canonical-arc-s5-3a2-file-corpus-migration.md`
  - `_bmad-output/implementation-artifacts/canonical-arc-s5-3b-g0-default-flip.md`

**Canonical monitor update:**

- No SOP-019 pre-dispatch poll is relayed yet.
- Latest canonical monitor material remains the S5-3b STOP + re-scope party round.
- The active next gate is still SOP-019 for **S5-3a.2**, not S5-3b dev-complete.

**S5-3a.2 spec status observed:**

- Still `READY-FOR-DEV`.
- The spec preserves the key re-scope boundaries:
  - migration-only, flag stays default-OFF;
  - 22 downstream tests get explicit kill-switch pins only after enrichment-orthogonality is confirmed;
  - 2 feature-flag tests require genuine re-contracts plus default-ON/explicit-ON witnesses;
  - 24-row disposition ledger is binding;
  - no production/runtime/manifest changes.

**Manifest churn observed:**

- `_bmad-output/maps/coverage-manifest/lesson-plan-envelope-coverage-manifest.json` changes only:
  - `generated_at: 2026-06-12T03:57:02.021632Z` -> `2026-07-07T06:17:25.458754Z`
- No semantic manifest content changed in this diff.
- This looks like timestamp-only regen noise unless the team intentionally ties it to a later evidence artifact.

**Finding disposition:**

- **S5-3a.2 not yet dispatched:** no evidence of implementation or pre-dispatch monitor relay yet.
- **F-1801/F-1802/F-1804/F-1805 remain parked for 3b:** no regression, but no closure progress this poll.
- **F-1803 revised and active through 3a.2:** the 24-test migration is now the blocker that must be closed before the flip can safely resume.
- **Metadata hygiene watch reopened:** coverage manifest timestamp-only churn is back in the working tree.

**Recommendations:**

1. Before dev dispatch, SOP-019 should independently re-derive or challenge the 24-test set and explicitly authorize any additions/removals.
2. Keep the 3a.2 commit test-only. Any `app/`, `state/config/`, or manifest change should stop the lane unless re-scoped by party consensus.
3. Exclude or revert the coverage-manifest timestamp-only diff unless a real semantic regen is documented.
4. For the 2 feature-flag tests, require explicit replacement witnesses; a renamed legacy assertion plus a pin is not enough.
5. Carry the `g0-single-file-corpus-opaque-crash-legibility` follow-on as filed, not absorbed into this migration story.

**Verdict:** `S5-3A2-PRE-DISPATCH-STABLE-MANIFEST-CHURN-WATCH`. No implementation progress is visible since the last poll; the lane is correctly staged for SOP-019, with metadata hygiene as the only new watch item.

### POLL-045 - SOP-019 relayed; S5-3a.2 set is 25 not 24 (2026-07-07T02:34:18-04:00)

**Trigger:** heartbeat poll at `2026-07-07T06:31:31.804Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with origin.
- HEAD remains `721cce04`.
- No new commits since S5-3a close.
- Visible tracked diffs:
  - `M SESSION-HANDOFF.md`
  - `M _bmad-output/implementation-artifacts/canonical-arc-claude-shadow-monitor-2026-07-06.md`
  - `M _bmad-output/maps/coverage-manifest/lesson-plan-envelope-coverage-manifest.json`
  - `M _bmad-output/planning-artifacts/deferred-inventory.md`
- No current diff is visible under `app/`, `tests/`, `state/config/`, or `pipeline-manifest.yaml`.
- Untracked active specs remain:
  - `_bmad-output/implementation-artifacts/canonical-arc-s5-3a2-file-corpus-migration.md`
  - `_bmad-output/implementation-artifacts/canonical-arc-s5-3b-g0-default-flip.md`

**Canonical monitor update:**

- **SOP-019 is now relayed** for S5-3a.2 pre-dispatch.
- Independent full-`tests/` causation-isolated sweep found the set is **25, not 24**.
- New missed test:
  - `tests/parity/test_trial_475_directive_composition_regression.py::test_start_trial_threads_composed_directive_to_texas_dispatch`
- This is not the file-corpus-crash mechanism. It uses a valid directory corpus and fails because first pause relocates to G0E before Texas dispatch, leaving `texas_payloads == []`.
- SOP-019 proves completeness by combining:
  - sweep-discovered 23 env-untouched tests;
  - exactly 2 tree-wide `delenv` feature-flag tests;
  - no conftest env manipulation.
- SOP-019 verdict: `CONCUR-WITH-FINDINGS`; dev dispatch cleared after applying F-1901/F-1902/F-1903/F-1904/F-1905.

**S5-3a.2 spec observed:**

- Status now says `READY-FOR-DEV` with SOP-019 applied and dev dispatch cleared.
- The residual section is materially improved:
  - 23 downstream-subject pins;
  - 2 feature-flag re-contracts;
  - two mechanisms tracked: file-corpus crash and first-pause relocation;
  - AC-6 scored by causation-isolation, not raw full-suite red count.
- The g0 feature-flag re-contract must use a directory corpus for the explicit `setenv("1")` witness.
- The irene feature-flag re-contract is correctly carried as skip-until-3b because only unset-default behavior proves the parity claim.

**New spec consistency watch:**

- The amended spec still contains stale 24-count references after the SOP-019 25-count correction:
  - RED-first plan step 4 says `Assemble the 24-row ledger`.
  - T11 gates say `verify the 24-set is complete`.
  - The historical "Why" paragraph still says all 24 share one root cause; this is now superseded by the residual section but easy for a dev to misread.
- AC-3 is correct at `25-row test-disposition ledger`; close review should treat AC-3 as authoritative and require stale references to be repaired before commit.

**SESSION-HANDOFF update observed:**

- `SESSION-HANDOFF.md` now has a new session-18 handoff block stating:
  - S4, pre-S5, and S5-3a closed;
  - S5-3b parked after STOP;
  - S5-3a.2 authored, SOP-019 relayed, and dev dispatched;
  - next action is to finish 3a.2, then unpark 3b.
- This looks like wrapup/handoff documentation, not production code, but it is a tracked file and should be included intentionally only if the team is actually closing or checkpointing the session.

**Manifest churn remains:**

- `_bmad-output/maps/coverage-manifest/lesson-plan-envelope-coverage-manifest.json` still changes only `generated_at`.
- No semantic manifest content changed.
- Recommendation from POLL-044 stands: exclude/revert unless the team documents why this timestamp-only regen belongs in the commit.

**Finding disposition:**

- **F-1901/F-1902/F-1903/F-1904/F-1905 opened-and-applied in spec:** material pre-dispatch improvements; good catch by the monitor gate.
- **S5-3a.2 now dispatch-cleared:** no implementation diff visible yet, so next meaningful gate is SOP-020 dev-complete/close.
- **Count-discipline watch upgraded:** the operative migration count is 25, not 24. Any 24-row ledger at close should be a block.
- **F-1801/F-1802/F-1804/F-1805 remain parked for 3b:** no regression.

**Recommendations:**

1. Before or during dev, fix the remaining stale `24-row` / `24-set` text in the S5-3a.2 spec. The closing ledger must have 25 rows.
2. SOP-020 should verify the new `tests/parity/test_trial_475...` pin specifically; it is a distinct first-pause-relocation mechanism, not a file-corpus crash.
3. Keep 3a.2 test-only. Any `app/`, `state/config/`, manifest, or production-runtime diff should stop the lane.
4. Score AC-6 by causation isolation exactly as SOP-019 states; do not fail the story on known non-flip full-suite noise.
5. Treat `SESSION-HANDOFF.md` as intentional wrapup/checkpoint scope only; if the story commit is meant to be migration-only, decide whether handoff belongs in that commit or a separate wrapup commit.
6. Remove or justify the timestamp-only coverage-manifest diff before commit.

**Verdict:** `S5-3A2-DISPATCH-CLEARED-COUNT-CORRECTED-TO-25`. SOP-019 materially improved the migration story and caught the second mechanism; the main risk now is stale 24-count wording or a 24-row close ledger slipping through.

### POLL-046 - S5-3a.2 dev diff appears; no SOP-020 yet (2026-07-07T02:44:56-04:00)

**Trigger:** heartbeat poll at `2026-07-07T06:42:01.546Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with origin.
- HEAD remains `721cce04`.
- No new commits since S5-3a close.
- Visible tracked diffs now include the S5-3a.2 test migration:
  - `M SESSION-HANDOFF.md`
  - `M _bmad-output/implementation-artifacts/canonical-arc-claude-shadow-monitor-2026-07-06.md`
  - `M _bmad-output/maps/coverage-manifest/lesson-plan-envelope-coverage-manifest.json`
  - `M _bmad-output/planning-artifacts/deferred-inventory.md`
  - `M tests/integration/composition/test_resume_rehydrates_selection.py`
  - `M tests/integration/marcus/test_front_door_selection_threading.py`
  - `M tests/integration/marcus/test_g0_enrichment_brick.py`
  - `M tests/integration/marcus/test_irene_refinement_brick.py`
  - `M tests/integration/marcus/test_production_clone_launch_evidence_discipline.py`
  - `M tests/integration/marcus/test_production_runner_gate_pause_resume.py`
  - `M tests/integration/marcus/test_run_summary_yaml_emit.py`
  - `M tests/integration/marcus/test_runner_threads_pre_fill_to_decision_card.py`
  - `M tests/integration/marcus/test_trial_cli.py`
  - `M tests/parity/test_trial_475_directive_composition_regression.py`
- No current diff is visible under `app/`, `state/config/`, or `pipeline-manifest.yaml`.

**Canonical monitor update:**

- No SOP-020 entry is visible yet.
- Latest canonical monitor material remains SOP-019: S5-3a.2 dispatch cleared with the corrected 25-test set.

**Current implementation observed:**

- The downstream migration is now in progress and appears test-only.
- Per-suite explicit OFF pins are present in the downstream suites using `monkeypatch.setenv("MARCUS_G0_ENRICHMENT_ACTIVE", "0")`.
- The newly discovered `tests/parity/test_trial_475_directive_composition_regression.py` case is explicitly pinned OFF with a comment documenting the distinct first-pause-relocation mechanism and its valid directory corpus.
- The g0 feature-flag test was genuinely re-contracted:
  - old `delenv` default-OFF assertion renamed to a kill-switch/OFF assertion;
  - new positive `setenv("1")` witness added using the directory `CORPUS`;
  - confirms first pause at `G0E` and materialized contribution.
- The irene feature-flag test was genuinely re-contracted:
  - old `delenv` premise replaced with explicit OFF/ON kill-switch parity;
  - new unset-default parity witness added with `@pytest.mark.skip(... un-skips at the 3b flip)`, matching F-1905.
- `git diff --check` reports only existing CRLF-normalization warnings, no whitespace errors.

**Open watches:**

- **No SOP-020 yet:** dev-complete/close evidence is not available.
- **Spec stale references remain:** the S5-3a.2 spec still contains:
  - `Assemble the 24-row ledger`;
  - `verify the 24-set is complete`;
  - historical "ALL 24 share ONE root cause" wording.
- **Coverage manifest churn remains:** the coverage manifest still appears to be timestamp-only.
- **SESSION-HANDOFF scope:** handoff update is present while 3a.2 is still in progress; include intentionally only if this is a checkpoint/wrapup commit, not a pure migration commit.

**Finding disposition:**

- **S5-3a.2 implementation started:** visible tests align with the SOP-019 shape so far.
- **Count-discipline watch remains open:** the implementation must close with 25 ledger rows, not 24.
- **Scope fence holds so far:** no production/runtime/config/manifest code diff is visible.
- **F-1801/F-1802/F-1804/F-1805 remain parked for S5-3b:** no regression this poll.

**Recommendations:**

1. SOP-020 should verify all 25 rows and specifically check the `test_trial_475...` row as `first-pause-relocation`, not file-corpus crash.
2. Repair the stale 24-count references in the S5-3a.2 spec before committing; otherwise the story text and close ledger can diverge.
3. Run/record the AC-6 forced-default-ON full-suite simulation with causation-isolated scoring; do not use raw full-suite reds as the pass/fail measure.
4. Keep this commit test-only apart from deliberate docs/ledger updates; no `app/`, `state/config/`, or manifest semantic diffs.
5. Remove or justify the timestamp-only coverage-manifest diff before commit.

**Verdict:** `S5-3A2-DEV-IN-PROGRESS-SHAPE-LOOKS-RIGHT-SOP020-PENDING`. The test migration is underway and appears scoped correctly; close should block on SOP-020 evidence, a 25-row ledger, stale-count cleanup, and metadata hygiene.

### POLL-047 - S5-3a.2 committed/pushed; SOP-020 relay gap remains (2026-07-07T02:56:04-04:00)

**Trigger:** heartbeat poll at `2026-07-07T06:52:01.694Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with origin.
- HEAD advanced to `3eff93da`:
  - `test(canonical-arc-S5-3a.2): file-corpus dormant-path migration — 25 tests env-independent (strangler-fig before the 3b flip)`
- Working tree after the commit has only:
  - `M SESSION-HANDOFF.md`
  - `M _bmad-output/maps/coverage-manifest/lesson-plan-envelope-coverage-manifest.json`
  - untracked strays/monitor ledgers/runs as before.
- No current uncommitted diff is visible under `app/`, `tests/`, `state/config/`, or `pipeline-manifest.yaml`.

**Commit contents observed (`3eff93da`):**

- Commit includes:
  - `_bmad-output/implementation-artifacts/canonical-arc-claude-shadow-monitor-2026-07-06.md`
  - `_bmad-output/implementation-artifacts/canonical-arc-s5-3a2-file-corpus-migration.md`
  - `_bmad-output/implementation-artifacts/canonical-arc-s5-3b-g0-default-flip.md`
  - `_bmad-output/planning-artifacts/deferred-inventory.md`
  - 10 migrated test files.
- Commit does **not** touch `app/`, `state/config/`, or `pipeline-manifest.yaml`.
- Commit message records the 25-test shape:
  - 22 file-corpus-crash tests;
  - 1 first-pause-relocation test in `tests/parity/test_trial_475...`;
  - 2 genuine feature-flag re-contracts.
- Commit message also records forced-ON verification with only three baseline-verified pre-existing reds.

**Canonical monitor update:**

- The committed canonical monitor ledger still appears to stop at **SOP-019**.
- I do **not** see a relayed `SOP-020` close-poll entry in `_bmad-output/implementation-artifacts/canonical-arc-claude-shadow-monitor-2026-07-06.md`.
- This conflicts with the committed story/commit-message language, which says `Full-tree AC-6 causation-isolation -> SOP-020` and marks S5-3a.2 `DONE`.

**S5-3a.2 story artifact observed:**

- The story is now committed and marked `DONE`.
- It records:
  - test-only scope;
  - 25 flip-caused tests env-independent;
  - trial_475 pinned;
  - 2 re-contracts genuine;
  - 3b unblocked.
- However, stale text remains committed:
  - RED-first plan step 4 still says `Assemble the 24-row ledger`.
  - T11 gates still say `verify the 24-set is complete`.
  - The historical "Why" paragraph still says all 24 share one root cause.
- AC-3 and the status line correctly say 25, so this is now a documentation consistency defect rather than an implementation-shape defect.

**Working-tree watches:**

- `SESSION-HANDOFF.md` remains modified but uncommitted; it looks like a session-18 handoff/checkpoint block.
- Coverage manifest remains timestamp-only churn:
  - semantic content unchanged;
  - only `generated_at` differs.

**Finding disposition:**

- **S5-3a.2 implementation/commit appears structurally clean:** no production code/config touched, and the commit scope matches a test migration.
- **POLL-046 implementation-shape watch mostly closed:** the expected test files are committed and pushed.
- **SOP-020 governance watch OPEN:** close-poll relay is missing from the canonical monitor ledger, despite the story/commit claiming DONE/SOP-020.
- **Count-discipline watch partially closed, partially open:** commit message and AC-3 use 25; stale 24 references remain in committed story text.
- **Metadata hygiene watch still open:** coverage manifest timestamp-only diff remains dirty after the commit.

**Recommendations:**

1. Before starting or closing S5-3b, relay or append the missing SOP-020 close poll in the canonical monitor ledger, or explicitly record why SOP-020 was satisfied without a relayed ledger entry.
2. Fix the stale `24-row` / `24-set` / `ALL 24` references in the committed S5-3a.2 story. The authoritative count is 25.
3. Keep `SESSION-HANDOFF.md` in a separate wrapup/checkpoint commit unless the team intentionally wants it coupled to the next story.
4. Remove or justify the timestamp-only coverage-manifest diff before the next commit.
5. S5-3b can be treated as technically unblocked only after the SOP-020 relay gap is resolved; otherwise the evidence chain has a documentation hole even if the code/test commit is good.

**Verdict:** `S5-3A2-COMMITTED-SCOPE-CLEAN-SOP020-RELAY-GAP`. The migration commit looks scoped and pushed, but the close evidence chain needs a canonical SOP-020 relay and stale-count cleanup before the lane safely advances into S5-3b.

### POLL-048 - No new movement; SOP-020 relay gap still open (2026-07-07T03:03:14-04:00)

**Trigger:** heartbeat poll at `2026-07-07T07:02:01.869Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with origin.
- HEAD remains `3eff93da`:
  - `test(canonical-arc-S5-3a.2): file-corpus dormant-path migration — 25 tests env-independent (strangler-fig before the 3b flip)`
- Working tree remains limited to:
  - `M SESSION-HANDOFF.md`
  - `M _bmad-output/maps/coverage-manifest/lesson-plan-envelope-coverage-manifest.json`
  - untracked protected strays/monitor ledgers/runs.
- No uncommitted diff is visible under `app/`, `tests/`, `state/config/`, or `pipeline-manifest.yaml`.

**Canonical monitor update:**

- No new SOP entry is visible after SOP-019.
- `SOP-020` is still not relayed in `_bmad-output/implementation-artifacts/canonical-arc-claude-shadow-monitor-2026-07-06.md`.
- The committed S5-3a.2 story and commit message still claim DONE / AC-6 / SOP-020 closure without a corresponding canonical monitor close-poll entry.

**Carry-forward findings:**

- **SOP-020 relay gap remains OPEN:** evidence chain is still missing the canonical close-poll relay for S5-3a.2.
- **Committed story stale-count text remains OPEN:** S5-3a.2 still contains stale `24-row`, `24-set`, and `ALL 24 share ONE root cause` wording despite the authoritative 25-test count.
- **Metadata hygiene remains OPEN:** coverage manifest still appears to be timestamp-only churn.
- **SESSION-HANDOFF scope remains OPEN:** handoff block is still dirty and should be committed only as deliberate wrapup/checkpoint scope.

**Recommendations:**

1. Do not treat S5-3b as governance-clean until the missing SOP-020 close-poll relay is recorded or explicitly explained in the canonical monitor ledger.
2. Patch the S5-3a.2 story text from 24 to 25 in the remaining stale sections before relying on it as handoff/spec source.
3. Remove or justify the timestamp-only coverage-manifest diff before the next commit.
4. Keep `SESSION-HANDOFF.md` separate from substrate/test commits unless this is an intentional wrapup commit.

**Verdict:** `NO-NEW-MOVEMENT-SOP020-GAP-CARRIED`. S5-3a.2 remains committed and pushed with clean implementation scope, but the close-governance/documentation issues from POLL-047 are still unresolved.

### POLL-049 - Still parked after S5-3a.2 commit; no S5-3b start visible (2026-07-07T03:13:19-04:00)

**Trigger:** heartbeat poll at `2026-07-07T07:12:02.022Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with origin.
- HEAD remains `3eff93da`.
- Working tree remains limited to:
  - `M SESSION-HANDOFF.md`
  - `M _bmad-output/maps/coverage-manifest/lesson-plan-envelope-coverage-manifest.json`
  - untracked protected strays/monitor ledgers/runs.
- No uncommitted diff is visible under `app/`, `tests/`, `state/config/`, or `pipeline-manifest.yaml`.
- No new commits or S5-3b implementation diffs are visible.

**Canonical monitor update:**

- No new SOP entry is visible after SOP-019.
- `SOP-020` remains absent from the canonical monitor ledger.
- Latest canonical monitor entry still points to SOP-020 as the next poll for S5-3a.2 dev-complete/close.

**Carry-forward findings:**

- **SOP-020 relay gap remains OPEN:** S5-3a.2 is committed/pushed and marked DONE, but the canonical close-poll relay is still missing.
- **Committed S5-3a.2 stale-count text remains OPEN:** stale `24-row`, `24-set`, and `ALL 24 share ONE root cause` text remains in the committed story, despite the authoritative 25-test count.
- **Metadata hygiene remains OPEN:** coverage-manifest timestamp-only diff remains dirty.
- **SESSION-HANDOFF scope remains OPEN:** session handoff remains dirty and should be handled as deliberate wrapup/checkpoint scope.
- **S5-3b remains PARKED:** no evidence yet of the default flip being re-applied after the 3a.2 migration.

**Recommendations:**

1. Relay or explicitly account for SOP-020 before crossing into S5-3b gates; this is now the main governance blocker.
2. Patch stale 24-count text in the S5-3a.2 story as a docs fix before relying on it as durable handoff context.
3. Keep the next S5-3b commit clean: default flip + required product surface/live evidence only, with no carried timestamp-only manifest churn.
4. Decide whether `SESSION-HANDOFF.md` is a wrapup checkpoint now or should wait for the next session boundary.

**Verdict:** `NO-NEW-MOVEMENT-S5-3B-NOT-YET-STARTED`. The repo remains stable after the S5-3a.2 commit; the next useful progress signal is either a SOP-020 relay cleanup or a visible, clean S5-3b re-application.

### POLL-050 - S5-3b implementation started; prior SOP-020 relay gap closed (2026-07-07T03:24:18-04:00)

**Trigger:** heartbeat poll at `2026-07-07T07:22:02.182Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with origin.
- HEAD advanced to `6961eeac`:
  - `docs(session-18): WRAPUP - S4 + pre-S5 g0-battery + S5-3a + S5-3a.2 CLOSED (4 stories, all pushed); S5-3b flip UNBLOCKED + parked`
- Commit `6961eeac` contains only:
  - `SESSION-HANDOFF.md`
  - `_bmad-output/implementation-artifacts/canonical-arc-claude-shadow-monitor-2026-07-06.md`
- Working tree now shows active S5-3b development:
  - `M app/marcus/orchestrator/g0_enrichment_wiring.py`
  - `M tests/integration/marcus/test_irene_refinement_brick.py`
  - `?? tests/integration/marcus/test_g0_enrichment_default_flip.py`
  - `?? scratchpad-s53b-fullsuite.log`
  - protected/untracked monitor ledgers, workbook-test artifacts, runs, and goal note remain outside commit scope.

**Canonical monitor update:**

- The canonical monitor now includes `SOP-020 - S5-3a.2 CLOSE verification`.
- SOP-020 records `CONCUR - S5-3a.2 DONE STANDS` and explicitly confirms:
  - 25 tests env-independent;
  - zero flip-caused reds remaining;
  - S5-3b unblocked;
  - `test_ac_s3_6_default_on_parity_with_s2` un-skip obligation carried into 3b.
- Prior external finding **SOP-020 relay gap is CLOSED**.
- Prior external findings for dirty `SESSION-HANDOFF.md` and timestamp-only coverage-manifest churn are also **CLOSED** by current status: handoff was committed in `6961eeac`, and the coverage manifest no longer appears dirty.

**S5-3b implementation observed:**

- `g0_enrichment_active()` has been flipped to DEFAULT-ON with an explicit falsy kill-switch set: `0`, `false`, `no`, `off` after strip/lower.
- `resolve_enrichment_mode()` was added as a fail-loud model-id-to-mode stamp:
  - `marcus` -> `live`
  - `deterministic-g0-enrichment-offline` -> `deterministic-recorded`
  - any unrecognized model id raises `ValueError`.
- `run_g0_enrichment()` now stamps `enrichment_mode` into both:
  - the on-disk card payload;
  - the bundle contribution output.
- The S5-3a.2 skip on `test_ac_s3_6_default_on_parity_with_s2` has been removed, cashing the un-skip obligation.
- New untracked S5-3b test file covers:
  - default-ON unset behavior;
  - empty/whitespace/unrecognized values defaulting active;
  - falsy kill-switch values inactive;
  - explicit truthy values active;
  - G0R delegation to the same predicate;
  - `MARCUS_G0_DISPATCH_LIVE` staying default-OFF;
  - `resolve_enrichment_mode()` live/deterministic/fail-loud behavior.

**Current watches / findings:**

- **S5-3b core flip shape is GOOD SO FAR:** the visible production diff matches the truth-table contract and includes the D4/F-1801 mode legibility stamp.
- **Product arming surface still NOT VISIBLE:** the S5-3b spec requires a first-class product surface for `MARCUS_G0_DISPATCH_LIVE` (for example `marcus_spoc --g0-dispatch-live` or preset-field equivalent). Current diff does not touch CLI/preset/runner code, so the production arming portion of D4/F-1801 is still open.
- **Live witness still NOT VISIBLE:** `scratchpad-s53b-fullsuite.log` exists and appears in progress/incomplete; it currently has only progress dots/early failures and no final summary. Running Python/pytest processes started around the same time are visible, so do not treat this as completed evidence yet.
- **Commit hygiene watch:** `tests/integration/marcus/test_g0_enrichment_default_flip.py` is still untracked. If S5-3b closes, this test must be deliberately staged with the S5-3b commit and protected strays must remain excluded.
- **Count-discipline docs watch remains LOW/OPEN:** the committed S5-3a.2 story still contains stale historical `24-row` / `24-set` / `ALL 24` wording even though SOP-020 and the status lines correctly use 25. This is no longer the main gate blocker, but it should be cleaned before a final handoff relies on that story as durable source text.

**Recommendations:**

1. Keep going on S5-3b, but do not close it on the core flip alone.
2. Add or verify the first-class product arm for live G0 dispatch (`--g0-dispatch-live` or preset equivalent), and ensure the run record makes that mode auditable.
3. Let the current full-suite/live evidence finish, then record a PASS/FAIL summary rather than using the partial scratchpad progress as a gate.
4. Before commit, verify the final staged set excludes protected strays and includes the new S5-3b test file.
5. Clean stale 24-count text in the S5-3a.2 story when the team next touches docs/handoff, or explicitly mark it as superseded historical context.

**Verdict:** `S5-3B-IN-PROGRESS-CORE-FLIP-GOOD-PRODUCT-ARMING-AND-LIVE-EVIDENCE-OPEN`. The team has moved from parked to active implementation, and the prior SOP-020 governance hole is now closed. The remaining risk is not the default flip predicate; it is completing the production-facing live-dispatch surface and first-run live witness before claiming S5-3b done.

### POLL-051 - S5-3b evidence sweep underway; product arm still absent (2026-07-07T03:35:09-04:00)

**Trigger:** heartbeat poll at `2026-07-07T07:32:02.370Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with origin.
- HEAD remains `6961eeac`.
- No new commit since POLL-050.
- Working tree now shows:
  - `M app/marcus/orchestrator/g0_enrichment_wiring.py`
  - `M tests/integration/marcus/test_irene_refinement_brick.py`
  - `M _bmad-output/maps/coverage-manifest/lesson-plan-envelope-coverage-manifest.json`
  - `?? tests/integration/marcus/test_g0_enrichment_default_flip.py`
  - `?? scratchpad-s53b-fullsuite.log`
  - `?? scratchpad-s53b-fullsuite-OFF.log`
  - `?? scratchpad-s53b-ON.txt`
  - existing protected/untracked monitor ledgers, workbook-test artifacts, runs, and goal note.

**Implementation delta since POLL-050:**

- No visible code/test delta beyond the S5-3b core flip already recorded in POLL-050.
- No visible CLI/preset/runner diff for a first-class `--g0-dispatch-live` or equivalent production arming surface.
- `rg` still finds `MARCUS_G0_DISPATCH_LIVE` wired only through the existing env seam and production runner gates; the S5-3b spec explicitly requires the real operator-facing production switch for AC-6/AC-L.

**Evidence artifacts observed:**

- `scratchpad-s53b-fullsuite.log` is now complete enough to show a final summary:
  - `80 failed, 6691 passed, 28 skipped, 67 deselected, 3 xfailed, 13 warnings in 445.28s`.
- `scratchpad-s53b-ON.txt` lists the 80 failed node IDs from the default/ON sweep.
- `scratchpad-s53b-fullsuite-OFF.log` has started but appears incomplete at this poll; it only shows progress through about 34%.
- Two `pytest tests/ -n 0 -q -p no:cacheprovider` Python processes started at `03:29:45` local are still running, consistent with the OFF comparison sweep still in progress.
- Current evidence therefore supports "baseline comparison underway", not "S5-3b live/evidence gate complete."

**Coverage manifest hygiene:**

- `_bmad-output/maps/coverage-manifest/lesson-plan-envelope-coverage-manifest.json` is dirty again.
- Diff is timestamp-only:
  - `generated_at` changed from `2026-06-12T03:57:02.021632Z` to `2026-07-07T07:28:29.664994Z`.
- This repeats the prior metadata-churn pattern and should not be included in an S5-3b substrate/test commit unless the team deliberately explains it.

**Carry-forward findings:**

- **S5-3b core flip shape remains GOOD SO FAR:** truth table, kill-switch semantics, mode stamp, and un-skip are still consistent with the spec.
- **Product arming surface remains OPEN/HIGH:** no real `marcus_spoc --g0-dispatch-live` or preset-equivalent surface is visible yet, despite AC-6/AC-L requiring the armed live leg to use the real production switch rather than a raw env/test seam.
- **Live/two-lane witness remains OPEN:** ON full-suite result exists, but OFF comparison and the real armed-live witness are not complete/visible.
- **Coverage-manifest timestamp churn REOPENED:** must be reverted/excluded/justified before commit.
- **New S5-3b test file still untracked:** ensure it is intentionally staged if/when S5-3b closes.
- **Stale S5-3a.2 historical 24-count text remains LOW/OPEN** as noted in POLL-050.

**Recommendations:**

1. Finish the OFF comparison sweep and explicitly compare ON vs OFF failures by causation; do not treat the 80-fail ON summary alone as a gate result.
2. Implement or surface the first-class production live-dispatch arm before claiming D4/F-1801 complete.
3. Keep the coverage-manifest timestamp-only diff out of the S5-3b commit unless the story explicitly owns a manifest regen.
4. Record the real AC-L two-lane witness separately: deterministic default receipt with `deterministic-recorded`, then armed production switch receipt with `live`.
5. Before commit, stage only the S5-3b-owned files and exclude all monitor ledgers, run dirs, scratchpads unless the team intentionally converts any evidence into a committed artifact.

**Verdict:** `S5-3B-EVIDENCE-SWEEP-IN-PROGRESS-NOT-CLOSEABLE-YET`. The team is doing the right comparison work, but S5-3b is not ready to close until the OFF sweep, real production arming surface, two-lane live witness, and commit hygiene are resolved.

### POLL-052 - Product live arm now visible; ON/OFF sweep has one ON-only failure (2026-07-07T03:47:31-04:00)

**Trigger:** heartbeat poll at `2026-07-07T07:42:02.473Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with origin.
- HEAD remains `6961eeac`; no new commit since POLL-051.
- Working tree now shows active S5-3b edits in:
  - `M app/marcus/cli/marcus_spoc.py`
  - `M app/marcus/orchestrator/g0_enrichment_wiring.py`
  - `M tests/integration/marcus/test_irene_refinement_brick.py`
  - `M _bmad-output/maps/coverage-manifest/lesson-plan-envelope-coverage-manifest.json`
  - `?? tests/integration/marcus/test_g0_enrichment_default_flip.py`
  - `?? scratchpad-s53b-ON.txt`
  - `?? scratchpad-s53b-OFF.txt`
  - `?? scratchpad-s53b-fullsuite.log`
  - `?? scratchpad-s53b-fullsuite-OFF.log`
  - existing protected/untracked monitor ledgers, workbook-test artifacts, run dirs, and goal note.

**Implementation movement since POLL-051:**

- `app/marcus/cli/marcus_spoc.py` now contains the missing S5-3b product-surface work:
  - imports `G0_DISPATCH_LIVE_ENV`, `G0_ENRICHMENT_MODE_DETERMINISTIC`, and `resolve_enrichment_mode`;
  - adds `_enrichment_mode_for_run()` to read `g0-enrichment.json` and derive/stamp mode fail-loud from `model_id` when needed;
  - adds `narrate_live_available_affordance()` so deterministic-recorded G0E/G0R narration tells the operator this is the deterministic scaffold and points to `--g0-dispatch-live`;
  - adds G0R narration and Beat 2/3 + Beat 3/3 framing for G0E/G0R;
  - adds first-class `marcus_spoc --g0-dispatch-live`, which sets `MARCUS_G0_DISPATCH_LIVE=1` for the run.
- The previously open **product arming surface** finding is therefore **PARTIALLY CLOSED in implementation shape**: the CLI flag now exists and is product-facing.
- It is not fully closed until verified by the AC-L armed-live witness using that real flag, with receipt mode `live`.

**Test/evidence movement:**

- The untracked S5-3b test file has expanded beyond truth-table checks and now also covers:
  - deterministic receipt stamping on disk and in bundle contribution;
  - G0E/G0R Beat narration and deterministic "live available" affordance;
  - absence of the affordance when mode is `live`;
  - `--g0-dispatch-live` arming `MARCUS_G0_DISPATCH_LIVE`;
  - default CLI path not arming the env var.
- ON/default full-suite artifact:
  - `scratchpad-s53b-fullsuite.log`: `80 failed, 6691 passed, 28 skipped, 67 deselected, 3 xfailed, 13 warnings`.
- OFF comparison artifact:
  - `scratchpad-s53b-fullsuite-OFF.log`: `79 failed, 6692 passed, 28 skipped, 67 deselected, 3 xfailed, 13 warnings`.
- ON/OFF failure-list compare shows one ON-only failure:
  - `tests/marcus/lesson_plan/test_workbook_producer.py::test_ac3_writes_both_md_and_docx`
- The ON-only failure stack shows `OSError: [Errno 22] Invalid argument` writing `_bmad-output/artifacts/workbooks-test/...@3.docx`. This looks tied to the protected untracked workbook-test artifact surface, but it is still an ON/OFF delta and needs explicit isolation or cleanup before claiming zero flip-caused reds.
- No active pytest process remains from the full-suite runs.

**Coverage manifest hygiene:**

- `_bmad-output/maps/coverage-manifest/lesson-plan-envelope-coverage-manifest.json` remains dirty and timestamp-only:
  - `generated_at` changed to `2026-07-07T07:36:23.217271Z`.
- This remains out-of-scope churn for S5-3b unless deliberately justified.

**Carry-forward findings:**

- **Product arming surface: PARTIALLY CLOSED / VERIFY REMAINS.** The CLI flag exists in diff, but AC-L must prove the real flag drives an armed live G0 pre-pass and stamps `live`.
- **ON/OFF causation isolation: OPEN.** The team now has a concrete 80-vs-79 delta; isolate the ON-only workbook-producer/docx failure before closing S5-3b.
- **AC-L two-lane witness: OPEN.** No visible evidence yet of deterministic default lane + real `--g0-dispatch-live` armed lane both passing through the production CLI/resume path.
- **Coverage-manifest timestamp churn: OPEN.** Exclude, revert, or explicitly justify before commit.
- **Commit hygiene: OPEN.** The expanded S5-3b test file is still untracked; scratchpads/run dirs/monitor ledgers/workbook-test artifacts must remain excluded unless intentionally converted into committed evidence.
- **Stale S5-3a.2 24-count historical text: LOW/OPEN** as before.

**Recommendations:**

1. Treat the new CLI flag and affordance as good progress, but do not mark D4/F-1801 closed until the real armed-live witness uses `--g0-dispatch-live` and records `enrichment_mode: live`.
2. Isolate the ON-only workbook-producer failure under a clean/protected-stray-free condition or document why it is unrelated to the default flip.
3. Re-run/record the focused S5-3b test file once tracked/staged; it now owns several important AC assertions and should not remain only as an untracked scratch artifact.
4. Remove the timestamp-only coverage-manifest diff from the story commit unless this story explicitly owns the regen.
5. Keep the final S5-3b commit tight: CLI flag/narration, g0 wiring, irene un-skip, S5-3b tests, and only deliberate evidence artifacts.

**Verdict:** `S5-3B-PRODUCT-ARM-IMPLEMENTED-EVIDENCE-STILL-BLOCKING-CLOSE`. The missing product surface has appeared and is shaped in line with the spec, but the story still needs ON/OFF delta isolation, a real two-lane AC-L PASS, and commit hygiene before it can safely close.

### POLL-053 - Manifest churn cleaned; ON-only leak remediation visible; final sweep still running (2026-07-07T03:56:16-04:00)

**Trigger:** heartbeat poll at `2026-07-07T07:52:02.598Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with origin.
- HEAD remains `6961eeac`; no new commit since POLL-052.
- Working tree now shows only S5-3b implementation/test-owned edits plus protected strays:
  - `M app/marcus/cli/marcus_spoc.py`
  - `M app/marcus/orchestrator/g0_enrichment_wiring.py`
  - `M tests/integration/marcus/test_irene_refinement_brick.py`
  - `?? tests/integration/marcus/test_g0_enrichment_default_flip.py`
  - `?? scratchpad-s53b-final.log`
  - existing protected/untracked monitor ledgers, workbook-test artifacts, run dirs, and goal note.
- `_bmad-output/maps/coverage-manifest/lesson-plan-envelope-coverage-manifest.json` is no longer dirty.

**Movement since POLL-052:**

- Prior **coverage-manifest timestamp churn is CLOSED** in the current worktree.
- The earlier ON/OFF scratchpads have been replaced by `scratchpad-s53b-final.log`.
- `scratchpad-s53b-final.log` is still incomplete at this poll, showing progress through roughly 72%.
- Two `pytest tests/ -n 0 -q -p no:cacheprovider` processes started at `03:46:56` local are still running, so this is an active final sweep, not completed evidence.

**Likely ON-only failure remediation observed:**

- The expanded S5-3b test file now wraps both CLI tests in `try/finally` and explicitly removes `MARCUS_G0_DISPATCH_LIVE` from `os.environ` after calling `marcus_spoc.main()`.
- This directly targets a plausible serial-suite env leak from `test_d4_cli_flag_arms_env`, which could explain the prior ON-only downstream workbook/docx failure.
- Good direction, but the active final sweep must finish before the ON-only delta can be considered closed.

**Implementation shape still observed:**

- Core default flip remains unchanged and aligned with the S5-3b truth-table contract.
- `--g0-dispatch-live` remains present in `marcus_spoc`, setting `MARCUS_G0_DISPATCH_LIVE=1`.
- Deterministic-mode affordance remains present for G0E/G0R narration.
- `enrichment_mode` stamping remains present in `run_g0_enrichment()`.
- Irene's default-ON parity witness remains un-skipped.

**Carry-forward findings:**

- **Product arming surface: IMPLEMENTED, VERIFY REMAINS.** The CLI flag is still present, but a real armed-live AC-L witness using that flag is not visible yet.
- **ON/OFF causation isolation: IN PROGRESS.** The likely env-leak fix is visible; final sweep still running.
- **AC-L two-lane witness: OPEN.** No visible deterministic-default + real armed-live PASS evidence yet.
- **Coverage-manifest hygiene: CLOSED for now.** No manifest diff currently appears.
- **Commit hygiene: OPEN.** The S5-3b test file remains untracked, and scratchpad/run/monitor/workbook-test strays must stay out of the final commit unless intentionally promoted.
- **Stale S5-3a.2 24-count historical text: LOW/OPEN** as before.

**Recommendations:**

1. Let `scratchpad-s53b-final.log` finish before declaring the ON-only failure resolved.
2. If the final sweep is green relative to the known baseline, record explicitly that the env-leak remediation closed the workbook/docx ON-only delta.
3. Do not close S5-3b until AC-L proves both lanes through the real product surface, including `--g0-dispatch-live` producing a live-mode receipt.
4. Keep the manifest clean through staging; it was corrected this poll and should not reappear as timestamp-only churn.
5. Stage the new S5-3b test file deliberately with the implementation if the story proceeds to commit.

**Verdict:** `S5-3B-REMEDIATION-IN-PROGRESS-FINAL-SWEEP-ACTIVE`. The team appears to have addressed the most likely ON-only failure mechanism and cleaned metadata churn, but S5-3b remains not closeable until the final sweep and two-lane AC-L evidence complete.

### POLL-054 - SOP-021 dev-complete relay landed; AC-L still pending (2026-07-07T04:07:18-04:00)

**Trigger:** heartbeat poll at `2026-07-07T08:02:02.730Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with origin.
- HEAD remains `6961eeac`; no new commit.
- Working tree now shows:
  - `M _bmad-output/implementation-artifacts/canonical-arc-claude-shadow-monitor-2026-07-06.md`
  - `M app/marcus/cli/marcus_spoc.py`
  - `M app/marcus/orchestrator/g0_enrichment_wiring.py`
  - `M tests/integration/marcus/test_irene_refinement_brick.py`
  - `?? tests/integration/marcus/test_g0_enrichment_default_flip.py`
  - existing protected/untracked monitor ledgers, workbook-test artifacts, run dirs, and goal note.
- The `scratchpad-s53b-*` files are no longer present in the repo root/status.
- No active pytest process is running.

**Canonical monitor update:**

- Canonical monitor now has `SOP-021 - S5-3b flip dev-complete verification`.
- SOP-021 records `CONCUR - no RED-first remediation before AC-L` on the applied working-tree diff.
- Key SOP-021 claims:
  - D1 truth table exact; 47/47 truth-table tests pass.
  - Tier-1 held: manifest + parity empty; exactly 3 files + 1 new test.
  - Mode stamp fail-loud: derived from `result.model_id`, stamped to both card payload and bundle output.
  - CLI arm `--g0-dispatch-live` sets `MARCUS_G0_DISPATCH_LIVE=1` only when passed; default remains OFF.
  - Deterministic affordance is gated to `mode == deterministic-recorded`; Beats 2-3 narration present.
  - Irene default-ON witness passes.
  - Integration default-ON evidence: `tests/integration/marcus/` = 417 passed / 2 skipped / 2 failed; both brick suites = 77/77; the 2 failures reproduce at dormant `=0`, so treated as flip-independent pre-existing drift.
- Prior external finding **product arming surface is implemented and independently relayed in SOP-021**.

**Findings / watches:**

- **S5-3b dev-complete governance advanced:** SOP-021 clears the diff to AC-L.
- **AC-L two-lane witness remains OPEN:** no visible deterministic-default + real `--g0-dispatch-live` armed-live PASS evidence yet; SOP-021 explicitly says AC-L is next.
- **Commit remains OPEN:** no S5-3b commit/push yet, and the new S5-3b test file is still untracked.
- **Prior full-tree ON/OFF scratchpad delta should be accounted for before close:** the earlier external artifacts showed 80 ON failures vs 79 OFF with one ON-only workbook/docx failure, then disappeared. SOP-021 now relies on focused integration/brick evidence. That may be proportionate for dev-complete, but the close record should explicitly state whether the earlier full-tree delta was caused by the CLI env leak and was superseded, or why it is non-gating.
- **Canonical monitor is tracked-modified:** expected as the SOP-021 relay, but it must be staged intentionally with the S5-3b close/ledger scope if included.
- **Coverage-manifest hygiene remains clean:** no manifest timestamp diff currently appears.
- **Stale S5-3a.2 24-count historical text remains LOW/OPEN** as before.

**Recommendations:**

1. Proceed to AC-L, but do not close S5-3b until both lanes pass through the real product path:
   deterministic default with `deterministic-recorded` + affordance, and armed live via `--g0-dispatch-live` with `enrichment_mode: live`.
2. In the close poll or evidence notes, explicitly retire the earlier 80-vs-79 full-tree scratchpad delta so it does not remain an unexplained monitor artifact.
3. Keep staging tight: S5-3b implementation files, the new test, and intentional canonical ledger/evidence only; exclude monitor ledgers, run dirs, workbook-test artifacts, and scratchpads.
4. Verify `git diff -- pipeline-manifest.yaml app/styleguide/parity.py` remains empty through commit.

**Verdict:** `S5-3B-DEV-COMPLETE-CONCUR-AC-L-PENDING`. The team has cleared dev-complete review and fixed the previously missing product-surface concern, but S5-3b is still not done until AC-L and commit/push close cleanly.

### POLL-055 - AC-L evidence pack started; lane A PASS, lane B not yet run (2026-07-07T04:18:42-04:00)

**Trigger:** heartbeat poll at `2026-07-07T08:12:02.884Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with origin.
- HEAD remains `6961eeac`; no new commit.
- Working tree remains the S5-3b working set plus canonical monitor relay:
  - `M _bmad-output/implementation-artifacts/canonical-arc-claude-shadow-monitor-2026-07-06.md`
  - `M app/marcus/cli/marcus_spoc.py`
  - `M app/marcus/orchestrator/g0_enrichment_wiring.py`
  - `M tests/integration/marcus/test_irene_refinement_brick.py`
  - `?? tests/integration/marcus/test_g0_enrichment_default_flip.py`
  - `?? _bmad-output/implementation-artifacts/evidence/s5-3b-acl-liveproof-20260707T080341Z/`
  - existing protected/untracked monitor ledgers, workbook-test artifacts, run dirs, and goal note.
- No new Python/pytest live-witness process is visible at poll time.

**AC-L evidence observed:**

- New evidence pack exists:
  - `_bmad-output/implementation-artifacts/evidence/s5-3b-acl-liveproof-20260707T080341Z/`
- Evidence pack currently contains 16 files:
  - lane A drivers, results, walk log, frozen judge, and `judge_a-facts.json`;
  - lane B driver scripts and `judge_b.py`;
  - no lane B result files and no `judge_b-facts.json` yet.
- `judges-frozen.json` says judges were frozen at `2026-07-07T08:05:33.522926+00:00` before lane execution, with first-run-stands protocol.

**Lane A evidence:**

- `judge_a-facts.json` verdict is `PASS`.
- Lane A trial used for the judge:
  - `7039838e-5477-4aba-9fcf-ab500f240588`
- Observed pause sequence:
  - `G0E -> G0R -> G1`
- Receipt mode:
  - `deterministic-recorded`
- Checks passing include:
  - `MARCUS_G0_ENRICHMENT_ACTIVE` absent after dotenv load;
  - `MARCUS_G0_DISPATCH_LIVE` unset;
  - first pause `G0E`;
  - G0E resume to `G0R`;
  - G0R resume to `G1`;
  - enrichment receipt has real typed components / provisional LO;
  - pre-pass model marker is deterministic/offline, so $0 live-LLM G0 pre-pass.

**Lane B status:**

- Lane B driver scripts exist (`lane_b_start.py`, `lane_b_resume_g0e.py`, `lane_b_resume_g0r.py`) and `judge_b.py` exists.
- No `driver-log-lane-b.txt`, `lane_b-start-result.json`, `lane_b-resume-*`, or `judge_b-facts.json` exists yet.
- Therefore the armed-live lane is **not yet evidenced** at this poll.

**Process watch:**

- `driver-log-lane-a.txt` contains an earlier lane A start attempt:
  - trial `24b66c17-4adc-48ee-94fb-ac3afd2b0c0b`
  - line records `=== LANE-a START NOT-OK paused_gate=G0E ===`
- The judged PASS uses the later lane A trial `7039838e-5477-4aba-9fcf-ab500f240588`.
- This may be a driver-status mismatch around CLI masked status versus persisted envelope status, but it is still a visible pre-judge attempt in a first-run-stands evidence pack. The close record should explicitly explain why this does not violate first-run-stands, or should mark the initial attempt as a failed lane and rerun under an approved recovery protocol.

**Carry-forward findings:**

- **AC-L lane A: PASS evidence visible.**
- **AC-L lane B: OPEN.** No armed-live result or judge facts yet.
- **First-run-stands clarification: OPEN.** Lane A has an earlier `START NOT-OK` line before the judged PASS; needs explanation before close.
- **Commit remains OPEN.** No S5-3b commit/push yet.
- **SOP-021 dev-complete status remains good.**
- **Earlier full-tree delta retirement remains OPEN** unless the close record explicitly supersedes it.
- **Stale S5-3a.2 24-count historical text remains LOW/OPEN** as before.

**Recommendations:**

1. Complete lane B through the real armed-live path and run `judge_b.py` once against the produced artifacts.
2. Before declaring AC-L PASS, explain the earlier lane A `START NOT-OK` attempt in first-run-stands terms.
3. Ensure the final evidence pack includes both judge fact files, both driver logs, both lane pause sequences, and receipt mode comparison (`deterministic-recorded` vs `live`).
4. Do not commit until the evidence pack is complete and the staged set is intentionally scoped.

**Verdict:** `S5-3B-ACL-PARTIAL-LANE-A-PASS-LANE-B-PENDING`. AC-L has started and lane A looks substantively good, but S5-3b remains open until lane B passes and the first-run-stands ambiguity is resolved.

### POLL-056 - S5-3b committed/pushed live-proven; external close poll concurs with wrapup watch (2026-07-07T04:28:44-04:00)

**Trigger:** heartbeat poll at `2026-07-07T08:22:03.065Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with origin.
- HEAD advanced to `3404dc1d` and is pushed:
  - `feat(canonical-arc-S5-3b): G0-enrichment default flip - canonical G0E/G0R on every run (LIVE-PROVEN two-lane)`
- Working tree after commit:
  - `M SESSION-HANDOFF.md`
  - protected/untracked monitor ledgers, workbook-test artifacts, historical run dirs, and goal note.
- No `app/`, `tests/`, story, evidence, canonical monitor, manifest, parity, or run-dir diffs remain dirty after the S5-3b commit.

**Commit scope:**

- Commit `3404dc1d` includes the expected S5-3b set:
  - `app/marcus/orchestrator/g0_enrichment_wiring.py`
  - `app/marcus/cli/marcus_spoc.py`
  - `tests/integration/marcus/test_irene_refinement_brick.py`
  - `tests/integration/marcus/test_g0_enrichment_default_flip.py`
  - S5-3b story/status update
  - canonical monitor SOP-021 relay
  - AC-L evidence pack under `_bmad-output/implementation-artifacts/evidence/s5-3b-acl-liveproof-20260707T080341Z/`
- Commit did **not** touch:
  - `pipeline-manifest.yaml`
  - `app/styleguide/parity.py`
  - `state/config/runs/`
  - untracked `runs/4fe...`, `runs/a18...`, or workbook-test strays.
- Protected strays remain excluded.

**AC-L evidence verification:**

- Evidence pack:
  - `_bmad-output/implementation-artifacts/evidence/s5-3b-acl-liveproof-20260707T080341Z/`
- `PROOF.md` records two-lane AC-L PASS with frozen judges and first-run-stands.
- Judges frozen:
  - `2026-07-07T08:05:33Z`, before the witnessed lane starts.
- Lane A:
  - trial `7039838e-5477-4aba-9fcf-ab500f240588`
  - `judge_a-facts.json` verdict `PASS`
  - sequence `G0E -> G0R -> G1`
  - `enrichment_mode = deterministic-recorded`
  - deterministic/offline marker, $0 live-LLM G0 pre-pass.
- Lane B:
  - trial `26d1dc94-61d4-4dac-8da9-224e6223a95d`
  - `judge_b-facts.json` verdict `PASS`
  - sequence `G0E -> G0R -> G1`
  - `enrichment_mode = live`
  - `receipt_model_id = marcus`
  - resolved model `gpt-5`
  - live response artifact present
  - divergence guard says lane A/B carrier structure and pause sequence are identical; content source is the intended delta.
- Total spend recorded:
  - `$0.0002844`.

**Prior findings disposition:**

- **AC-L lane B OPEN -> CLOSED.** Lane B now has result files and `judge_b-facts.json` PASS.
- **First-run-stands clarification OPEN -> CLOSED-WITH-NOTE.** `PROOF.md` explains the earlier lane A `START NOT-OK` line as CLI status masking (`registered-offline` returned while persisted envelope was `paused-at-gate` at early G0E). The driver was corrected before any judge ran, lane A was re-run fresh, judges were frozen before lane execution and each judge ran once. This is acceptable as a disclosed pre-judge driver correction, not retry-to-green of a failed judge.
- **Product arming surface CLOSED.** The committed code includes `--g0-dispatch-live`; live proof demonstrates the armed path produced a live/gpt-5 receipt.
- **Earlier full-tree 80-vs-79 delta CLOSED-BY-SUPERSEDING-EVIDENCE.** The committed SOP-021 focused integration/brick evidence and final committed tests show zero flip-induced reds in the owned surface; the transient full-tree scratchpad delta is no longer present and was likely the env-leak class remediated by explicit cleanup in the CLI-arm tests. No residual flip-caused red is visible in committed evidence.
- **Coverage-manifest hygiene CLOSED.** No manifest diff remains.
- **Commit hygiene CLOSED for S5-3b.** New test and evidence pack are tracked; protected strays are not.
- **Stale S5-3a.2 24-count historical text remains LOW/OPEN** if anyone later edits durable historical docs, but it no longer blocks S5-3b.

**Remaining watch:**

- `SESSION-HANDOFF.md` is now dirty and claims S5/S5-3b complete at `3404dc1d`. That is consistent with the commit/evidence, but it is uncommitted at this poll. Treat it as wrapup/handoff scope, not part of the S5-3b substrate commit.
- The committed canonical monitor appears to stop at SOP-021 dev-complete, while the story file and commit carry the live-proof close. This external poll serves as the close corroboration. If the team requires a numbered canonical close SOP entry, append it in wrapup before final done-signal.

**Recommendations:**

1. Proceed to S6 only after wrapup deliberately handles `SESSION-HANDOFF.md` and any required party done-signal.
2. If maintaining canonical SOP numbering strictly, add a concise canonical close entry for `3404dc1d` / AC-L PASS; otherwise reference this POLL-056 as the external close poll.
3. Keep protected strays excluded in the wrapup commit as well.

**Verdict:** `S5-3B-CLOSED-LIVE-PROVEN-PUSHED-CONCUR-WITH-WRAPUP-WATCH`. External close poll concurs that S5-3b is implemented, live-proven both lanes, committed, pushed, and scoped cleanly. The only active watch is uncommitted handoff/final done-signal hygiene.

### POLL-057 - S5 wrapup committed; SOP-022 close and handoff to S6 clean (2026-07-07T04:36:51-04:00)

**Trigger:** heartbeat poll at `2026-07-07T08:32:03.243Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with origin.
- HEAD advanced to `6529f76a`:
  - `docs(session-18): S5 (G0 canonical) COMPLETE - 3a+3a.2+3b all live-proven+pushed; SOP-022 close + handoff to S6`
- Working tree is clean except protected/untracked strays:
  - `_bmad-output/artifacts/workbooks-test/`
  - the three external/operator monitor ledgers
  - `goal-canonical-arc-s4-onward-2026-07-07.txt`
  - historical run dirs `runs/4fe...` and `runs/a18...`
- No `app/`, `tests/`, story, canonical monitor, handoff, manifest, parity, evidence, or run-dir tracked diffs remain.

**Wrapup commit scope:**

- Commit `6529f76a` contains exactly:
  - `SESSION-HANDOFF.md`
  - `_bmad-output/implementation-artifacts/canonical-arc-claude-shadow-monitor-2026-07-06.md`
- No production code/tests/story substrate changed in the wrapup commit.
- Prior external watch on dirty `SESSION-HANDOFF.md` is **CLOSED**.

**Canonical monitor update:**

- Canonical monitor now includes `SOP-022 - S5-3b STORY-CLOSE audit`.
- SOP-022 records:
  - `Commit 3404dc1d (base 6961eeac). CONCUR - S5-3b DONE STANDS; S5 (G0 canonical) COMPLETE.`
  - commit integrity clean: 31 in-scope files;
  - `pipeline-manifest.yaml` and `app/styleguide/parity.py` frozen/empty;
  - no protected strays committed;
  - flip semantics verified;
  - AC-L two-lane live evidence verified with frozen judge hashes;
  - lane A 8/8, lane B 4/4;
  - first-run/status-mask anomaly honest and non-blocking;
  - post-commit green 72 + 51 passed;
  - S5 split ancestry contiguous.
- The canonical close entry also states:
  - `S5 (G0 CANONICAL) COMPLETE`
  - next: `S6 Tracy -> S7 operator spec checkpoint -> S8 composed proof`.

**Finding disposition:**

- **S5-3b close corroboration: CLOSED.** External POLL-056 and canonical SOP-022 now agree.
- **Handoff/final done-signal hygiene: CLOSED.** The handoff update is committed and pushed in `6529f76a`.
- **Earlier first-run-stands concern: CLOSED.** SOP-022 and `PROOF.md` explain the CLI status-mask driver correction before any judge ran; frozen judges still ran once each.
- **Earlier full-tree delta concern: CLOSED/SUPERSEDED.** SOP-022's committed close evidence and post-commit green set are now the durable record.
- **Protected-stray exclusion: STILL CLEAN.** Strays remain untracked and excluded.
- **Stale S5-3a.2 historical 24-count text: LOW/RESIDUAL ONLY.** It remains a historical-doc cleanup opportunity, not an active gate concern.

**Recommendations:**

1. Treat S5 as complete and let the Claude team proceed into S6 Tracy under the normal gate rhythm.
2. At S6 start, verify they read the latest canonical monitor tail (`SOP-022`) before crossing the spec gate.
3. Keep the existing protected strays excluded from any S6 commits.
4. Carry KG/ONBOARDING regen as a wrapup obligation, not as a blocker to starting S6 unless the team touches broad onboarding-facing substrate.

**Verdict:** `S5-WRAPUP-CLEAN-S6-READY`. S5 is closed, live-proven, committed, pushed, and handoff-clean. The monitor lane should now watch for S6 Tracy spec/start artifacts.

### POLL-058 - S6 Tracy spec opened; SOP-023 concurs with safety findings (2026-07-07T04:42:03-04:00)

**Trigger:** heartbeat poll at `2026-07-07T08:42:03.382Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with origin.
- HEAD remains `6529f76a`:
  - `docs(session-18): S5 (G0 canonical) COMPLETE - 3a+3a.2+3b all live-proven+pushed; SOP-022 close + handoff to S6`
- Working tree now has:
  - modified canonical monitor: `_bmad-output/implementation-artifacts/canonical-arc-claude-shadow-monitor-2026-07-06.md`
  - new untracked S6 spec: `_bmad-output/implementation-artifacts/canonical-arc-s6-tracy-scite-canonical.md`
  - existing protected/untracked strays: `_bmad-output/artifacts/workbooks-test/`, the external monitor ledgers, `goal-canonical-arc-s4-onward-2026-07-07.txt`, and historical run dirs.
- No production code, tests, manifest, parity, handoff, or run evidence tracked diff is visible at this poll.

**S6 spec and canonical monitor state:**

- New S6 artifact is `Story S6 - Tracy/research Scite-canonical (live Scite dispatch on every production run)`.
- Status is `READY-FOR-DEV`.
- Canonical monitor appended `SOP-023 - S6 Tracy/Scite-canonical spec pre-dispatch review`.
- SOP-023 verdict is `CONCUR-WITH-FINDINGS`.
- The spec explicitly frames S6 as dispatch-canonicalization only:
  - `MARCUS_RESEARCH_DISPATCH_LIVE` default-ON with explicit falsy kill switch;
  - Scite-canonical provider selection;
  - Consensus provider live-enablement deferred with skip-witness;
  - resume idempotency;
  - visible recorded degrade when Scite credentials are absent;
  - live cited `research_entries` witnessed into the workbook DOI section.

**Findings carried forward:**

- **F-2301 active implementation requirement:** current selector behavior is a real bug. Sorted ready providers are `consensus`, `gamma_docs`, `scite`; `ready[:2]` excludes Scite and selects consensus/gamma_docs. S6 cannot reach its M-witness until dispatch is scoped to Scite.
- **F-2302 live feasibility confirmed:** Scite is ready/registered, credentials are present, and DOI/source_id threading is plausible. No hidden blocker is visible before dev starts.
- **F-2304 active safety watch:** one additional dormant real-walk test, `test_ac_d2_two_walk_parity_fires_on_real_continuation`, can reach node 04.55 with a research gap while only stubbing `ProductionDispatchAdapter`. After the default-ON flip, that shape can make a real paid Scite call or hang in an offline suite unless pinned off or routed through a fake retrieval adapter. The S6 spec now requires the S5-style full-tree causation-isolation sweep and says to migrate/pin known hazards before running the sweep.
- **F-2305 active implementation requirement:** absent-credential degrade belongs at `run_research_wiring` entry, before `_dispatch_intents_to_texas`, so missing credentials produce a visible recorded-empty outcome rather than a silent fail-soft drop.
- **Tier-1 watch remains open:** SOP-023 confirms `research_wiring.py` / `production_runner.py` are outside `block_mode_trigger_paths`; S6 should not edit `pipeline-manifest.yaml` or `app/styleguide/parity.py`.

**Recommendations:**

1. Let S6 dev proceed, but require T1 to pin/fake the known dormant real-walk hazards before any forced-ON full-tree sweep so offline tests do not touch live Scite.
2. At SOP-024, verify the full-tree sweep enumerated every real-walk-through-04.55 test, not only the two known examples.
3. Verify D2 by observing Scite selected and consensus/gamma_docs excluded; a green test that merely accepts any registered provider is insufficient.
4. Verify D4 with a forced-absent-creds lane that records an explicit envelope outcome and continues the walk.
5. Keep S6 Tier-1: no manifest/parity changes, no research-quality scope creep, and no workbook rebuild beyond the D6 threading witness.
6. Commit hygiene watch: S6 spec and canonical monitor are expected in the eventual story commit, but protected strays must remain excluded.

**Verdict:** `S6-SPEC-READY-FOR-DEV-CONCUR-WITH-SAFETY-WATCH`. The Claude team is correctly into S6 and the pre-dispatch monitor caught the right hard edges. The main next risk is accidental live Scite dispatch from offline tests during the default-ON migration sweep.

### POLL-059 - S6 dev started; first safety pins landed in working tree (2026-07-07T04:52:03-04:00)

**Trigger:** heartbeat poll at `2026-07-07T08:52:03.534Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with origin.
- HEAD remains `6529f76a`; no new commit since S5 wrapup.
- Working tree now includes one S6 test diff:
  - `tests/integration/marcus/test_braid_s3_research_wiring.py`
- Canonical monitor still carries the SOP-023 S6 pre-dispatch entry.
- S6 spec remains untracked and READY-FOR-DEV.
- No production code, manifest, parity, handoff, live evidence, or run-dir tracked diff is visible at this poll.

**Observed S6 dev diff:**

- `test_ac_d2_two_walk_parity_fires_on_real_continuation` now sets:
  - `MARCUS_RESEARCH_DISPATCH_LIVE=0`
- The added comment explicitly cites S6 safety / F-2304 and explains why the test must not use the post-flip default:
  - it walks a real continuation through node 04.55;
  - it has an in-scope research gap;
  - it stubs `ProductionDispatchAdapter`, not the retrieval adapter;
  - leaving the flag unpinned after default-ON could fire a real paid Scite call or hang inside the offline suite.
- `test_m1_toggle_off_by_default_threads_false_to_both_walks` was renamed to:
  - `test_m1_kill_switch_threads_false_to_both_walks`
- That test now uses `monkeypatch.setenv("MARCUS_RESEARCH_DISPATCH_LIVE", "0")` instead of `delenv(...)`, correctly re-contracting it from "unset is safe default" to "explicit falsy kill-switch is safe-off".

**Finding disposition:**

- **F-2304 known-test safety: PARTIALLY CLOSED.** The two named known hazards from SOP-023 are now addressed in the working tree:
  - `test_ac_d2_two_walk_parity_fires_on_real_continuation` pinned off;
  - former M1 unset-default test converted to explicit kill-switch semantics.
- **F-2304 full-tree sweep: STILL OPEN.** No evidence yet that the full `MARCUS_RESEARCH_DISPATCH_LIVE=1` versus `=0` causation-isolation sweep has been run or that every dormant real-walk-through-04.55 test has been enumerated.
- **F-2301 Scite selection bug: STILL OPEN.** No `research_wiring.py` or provider-selection diff yet.
- **D1 default-ON flip: STILL OPEN.** No `production_runner.py` diff yet.
- **D3 idempotency / D4 creds-absent degrade / D5 narration / D6 DOI witness: STILL OPEN.** No relevant implementation or evidence visible at this poll.
- **Tier-1 watch: CLEAN SO FAR.** No `pipeline-manifest.yaml` or `app/styleguide/parity.py` diff.

**Recommendations:**

1. Keep the current two test edits; they are directionally correct and preserve the Marcus-SPOC boundary.
2. Require the next S6 dev report to show the full-tree forced-ON/OFF sweep result before any default-ON production flip is considered complete.
3. During SOP-024, check that this test migration did not become the whole AC-5 proof; it is only the known-hazard pre-pin.
4. Continue to block any S6 close until Scite-only provider selection, absent-creds recorded degrade, resume idempotency, and the live DOI witness are all evidenced.

**Verdict:** `S6-DEV-STARTED-F2304-KNOWN-PINS-GOOD-FULL-SWEEP-OPEN`. Early S6 work is on the right risk first, but it is only the first migration step, not a dev-complete state.

### POLL-060 - S6 production diff present; D1/D2/D4 taking shape, D5 wiring gap (2026-07-07T05:02:03-04:00)

**Trigger:** heartbeat poll at `2026-07-07T09:02:03.736Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with origin.
- HEAD remains `6529f76a`; no S6 commit yet.
- Working tree now includes S6 production/test diffs:
  - `app/marcus/orchestrator/production_runner.py`
  - `app/marcus/orchestrator/research_wiring.py`
  - `app/marcus/cli/marcus_spoc.py`
  - `tests/integration/marcus/test_braid_s3_research_wiring.py`
  - canonical monitor SOP-023 entry
  - untracked S6 spec
- Frozen paths remain clean:
  - `state/config/pipeline-manifest.yaml` has no diff.
  - `app/styleguide/parity.py` has no diff.

**Observed implementation progress:**

- **D1 default-ON kill-switch is implemented in `production_runner.py`:**
  - `RESEARCH_DISPATCH_LIVE_KILL_SWITCH = {"0", "false", "no", "off"}`
  - `_research_dispatch_live()` now returns true for unset/empty/truthy/unrecognized values and false only for explicit falsy kill-switch values.
  - AC-1 truth-table tests were added.
- **D2 Scite-canonical selection is implemented in `research_wiring.py`:**
  - `LITERATURE_RESEARCH_PROVIDER = "scite"`
  - `DEFERRED_LITERATURE_PROVIDERS = {"consensus", "gamma_docs"}`
  - `DeterministicPostureSelector.select_posture()` now filters to Scite and raises if Scite is not ready/stub.
  - Consensus skip-witness test was added and names `consensus-provider-live-enablement`.
- **D3 idempotency is represented by a new test:**
  - double re-entry on an already research-completed envelope should not re-dispatch and should keep entries byte-stable.
  - Existing `run_research_wiring()` idempotency guard appears to support this.
- **D4 absent-creds degrade is implemented at `run_research_wiring()` entry:**
  - `_scite_creds_present()` checks Bearer token first, then Basic env vars.
  - absent creds + live dispatch + in-scope gaps short-circuits before `_dispatch_intents_to_texas`.
  - output carries present/empty `research_entries`, `research_degrade`, reason marker, and relogin offer.
  - tests include a tripwire that would fail if live dispatch is reached with forced-absent creds.
- **D6 witness test added:**
  - source-inspects workbook producer for the existing `ResearchEntry` DOI fields and `https://doi.org/` rendering path. This is acceptable as a contract-presence witness; the live content-inspection still belongs to AC-L.

**Material finding:**

- **F-2401 [MEDIUM, likely blocking for SOP-024 unless fixed]: D5 narration helper is not wired into the SPOC flow.**
  - `app/marcus/cli/marcus_spoc.py` adds `narrate_research_result(contribution_output)`.
  - `rg` shows the helper is only used by direct tests; there is no production call after `resume_production_trial(...)` in `run_marcus_spoc()`.
  - Current tests prove string formatting, not the acceptance criterion that "the SPOC narrates the dispatched/cited research result AFTER node 04.55".
  - Recommended fix: after each resume, inspect the returned envelope for the `research_wiring` contribution at node `04.55`; append `narrate_research_result(...)` exactly when that contribution appears newly relevant. Add an integration-style transcript assertion so this cannot pass as a dead helper.

**Other watch items:**

- **F-2304 full-tree sweep remains OPEN.** The known hazardous tests are pinned, but no sweep evidence is visible yet.
- **F-2301 / D2 implementation looks directionally correct, but needs SOP-024 evidence.** The Scite-only selection test is strong because it asserts exactly `{"scite"}` and excludes consensus/gamma_docs.
- **D4 implementation looks directionally correct, but SOP-024 should verify it does not mask a real provider-selection failure when creds are present.**
- **Hook-site comments in `production_runner.py` still say `MARCUS_RESEARCH_DISPATCH_LIVE` is default OFF at both research-wiring call sites.** The top-level predicate comments are updated to DEFAULT ON, so this is likely stale documentation, not behavior; clean it before commit to avoid future monitor/operator confusion.
- **Tier-1 clean so far.** No manifest or parity diff.

**Recommendations:**

1. Fix D5 wiring before declaring dev-complete; direct helper tests are insufficient.
2. Update the stale hook-site default-OFF comments in `production_runner.py`.
3. Produce and record the full-tree forced-ON/OFF sweep before SOP-024.
4. Keep AC-L expectations unchanged: live Scite DOI row, resolvable DOI, G2 citation-fidelity pass, workbook DOI-thread inspection, and forced-absent-creds degrade lane.

**Verdict:** `S6-DEV-IN-PROGRESS-D1-D2-D4-SHAPING-D5-WIRING-GAP`. The implementation is moving in the right direction, but it is not close-ready until D5 is wired into the actual SPOC transcript and sweep evidence exists.

### POLL-061 - S6 diff unchanged; D5 and sweep findings carried forward (2026-07-07T05:12:03-04:00)

**Trigger:** heartbeat poll at `2026-07-07T09:12:03.861Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with origin.
- HEAD remains `6529f76a`; no S6 commit yet.
- Working tree diff footprint is unchanged from POLL-060:
  - `_bmad-output/implementation-artifacts/canonical-arc-claude-shadow-monitor-2026-07-06.md`
  - `app/marcus/cli/marcus_spoc.py`
  - `app/marcus/orchestrator/production_runner.py`
  - `app/marcus/orchestrator/research_wiring.py`
  - `tests/integration/marcus/test_braid_s3_research_wiring.py`
- Untracked S6 spec remains present.
- No new S6 evidence directory, SOP-024 entry, live proof, or run artifact appears at this poll.
- Frozen paths remain clean: no diff in `state/config/pipeline-manifest.yaml` or `app/styleguide/parity.py`.

**Focused checks:**

- `narrate_research_result(...)` still appears only in:
  - its definition in `app/marcus/cli/marcus_spoc.py`
  - two direct tests in `tests/integration/marcus/test_braid_s3_research_wiring.py`
- There is still no production call after `resume_production_trial(...)` in `run_marcus_spoc()`.
- No full-tree forced-ON/OFF sweep evidence is visible in implementation artifacts.
- `production_runner.py` still contains stale hook-site comments saying the research live toggle is default OFF, despite the top-level predicate now being DEFAULT ON.

**Finding disposition:**

- **F-2401 D5 dead-helper gap: OPEN / unchanged.** The helper is still not wired into the real SPOC transcript.
- **F-2304 full-tree sweep: OPEN / unchanged.** Known hazards were pinned earlier, but no sweep result is visible.
- **D1/D2/D3/D4/D6 implementation progress: CARRY FORWARD.** No new evidence changes the POLL-060 assessment.
- **Tier-1 watch: CLEAN SO FAR.** No manifest/parity diff.

**Recommendations:**

1. Do not accept S6 dev-complete until D5 is wired into `run_marcus_spoc()` and covered by a transcript-level test.
2. Require recorded forced-ON/OFF full-tree sweep evidence before SOP-024.
3. Clean stale default-OFF comments at both research hook sites before commit.
4. Keep watching for AC-L proof artifacts: real Scite DOI row, resolvable DOI, G2 pass, workbook DOI thread, and forced-absent-creds degrade lane.

**Verdict:** `S6-NO-MATERIAL-CHANGE-F2401-OPEN`. The last material finding stands: S6 is still dev-in-progress, not close-ready.

### POLL-062 - SOP-024/T11 landed; S6 requires remediation before AC-L (2026-07-07T05:22:04-04:00)

**Trigger:** heartbeat poll at `2026-07-07T09:22:04.017Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with origin.
- HEAD remains `6529f76a`; no S6 commit yet.
- Code/test diff footprint is unchanged:
  - `app/marcus/cli/marcus_spoc.py`
  - `app/marcus/orchestrator/production_runner.py`
  - `app/marcus/orchestrator/research_wiring.py`
  - `tests/integration/marcus/test_braid_s3_research_wiring.py`
- Canonical monitor grew from SOP-023 only to include `SOP-024 + 3-lane T11 for S6`.
- S6 spec remains untracked.
- No S6 AC-L/live evidence directory or close commit is visible yet.
- Frozen paths remain clean: no manifest or parity diff.

**Canonical SOP-024/T11 state:**

- SOP-024 verdict: `CONCUR-WITH-FINDINGS`.
- It confirms the four load-bearing legs of the current dev diff:
  - D1 default-ON kill-switch truth table.
  - D2 Scite-canonical selector, consensus/gamma_docs excluded, `cross_validate` false.
  - D3 idempotency early-return behavior.
  - D4 absent-creds degrade precondition at `run_research_wiring` entry.
- It also records:
  - Tier-1/parity clean.
  - no new live dispatch call site.
  - no flip-caused reds.
  - live-leak bounded: only S6 fake adapter emits gaps; gap-bearing runner walks pin OFF or fake the adapter.

**Findings disposition:**

- **F-2401 / R2 D5 dead-helper: CONFIRMED BY T11, MUST-FIX.**
  - This external monitor raised it in POLL-060.
  - SOP-024 now independently confirms `narrate_research_result(...)` is defined and directly tested but never invoked in the SPOC flow.
  - Required remediation: wire it into resume flow by inspecting the 04.55 research contribution, add transcript/integration coverage, and reconcile the stale G1 "no gap-fill research was needed" line.
- **R1 degrade-resume bug: NEW MUST-FIX.**
  - Current D4 degrade records a 04.55 contribution.
  - The D3 idempotency guard treats any existing 04.55 contribution as complete.
  - Result: after operator re-auths and resumes, research cannot re-dispatch; the run keeps the empty degraded result despite the relogin offer.
  - Required remediation: a `degraded == True` contribution must be treated as not-complete / re-dispatchable after credentials are restored.
- **R3 Basic-creds gate: SHOULD-FIX.**
  - `_scite_creds_present()` currently accepts Basic env creds.
  - SOP-024 says canonical Scite MCP requires OAuth Bearer; Basic-only can produce a doomed call, silent empty, or uncaught continuation crash.
  - Recommended remediation: canonical live path should require Bearer, not Basic fallback.
- **R4 idempotency test env-coupling: SHOULD-FIX.**
  - Force creds-present in AC-3 so the test does not depend on ambient workstation credentials.
- **R5 cleanup: NIT.**
  - Update stale default-OFF hook comments.
  - Add the S6 files to the audit-test allowlist per live-dispatch-change convention.

**Recommendations:**

1. Do not proceed to AC-L until R1 and R2 are remediated RED-first and re-verified.
2. Take R3 before live witness if possible; live Scite proof should not rely on Basic fallback ambiguity.
3. Keep the existing Tier-1 constraint: no manifest/parity changes.
4. At the next poll, check for remediation diffs specifically in `research_wiring.py`, `marcus_spoc.py`, and transcript-level tests.

**Verdict:** `S6-SOP024-CONCUR-WITH-MUST-FIX-REMEDIATION-REQUIRED`. S6 dev-complete review happened, but the story is not AC-L-ready until degrade-resume and SPOC narration are fixed.

### POLL-063 - S6 remediation diff present; R1/R2/R3/R4/R5 look addressed, AC-L still pending (2026-07-07T05:32:04-04:00)

**Trigger:** heartbeat poll at `2026-07-07T09:32:04.186Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with origin.
- HEAD remains `6529f76a`; no S6 commit yet.
- Working tree now includes remediation diffs in:
  - `app/marcus/orchestrator/research_wiring.py`
  - `app/marcus/cli/marcus_spoc.py`
  - `app/marcus/orchestrator/production_runner.py`
  - `tests/integration/marcus/test_braid_s3_research_wiring.py`
  - `tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py`
  - canonical monitor SOP-023/SOP-024 entries
- No S6 AC-L evidence directory, SOP-025 close entry, or close commit is visible.
- Frozen paths remain clean: no `state/config/pipeline-manifest.yaml` or `app/styleguide/parity.py` diff.

**Remediation assessment:**

- **R1 degrade-resume MUST-FIX: APPEARS ADDRESSED.**
  - `research_wiring._is_degraded_contribution(...)` detects `research_degrade.degraded == True`.
  - `run_research_wiring()` now short-circuits only if an existing contribution is non-degraded.
  - Degraded contributions fall through so a post-re-auth resume can re-dispatch.
  - Storage semantics check: `ProductionEnvelope.add_contribution()` replaces the same `(specialist_id, node_id)` contribution in place, so a successful retry should replace the degraded 04.55 contribution rather than append a duplicate.
  - New test `test_ac3_resume_after_degrade_redispatches_when_creds_return` covers the R1 red path offline.
- **R2 D5 dead-helper MUST-FIX: APPEARS ADDRESSED.**
  - `run_marcus_spoc()` now inspects the resumed envelope for the 04.55 `research_wiring` contribution after `resume_production_trial(...)`.
  - It appends `narrate_research_result(...)` to the transcript exactly once when the contribution is present.
  - The stale G1 narration was replaced with a future-looking "right after this gate I run gap-fill research..." line.
  - New transcript-level test `test_ac5_spoc_narration_reaches_resumed_transcript` proves the narration reaches the operator transcript, not just the helper.
- **R3 Basic-creds SHOULD-FIX: APPEARS ADDRESSED.**
  - `_scite_creds_present()` is now Bearer-only.
  - Basic env vars alone return false in `test_ac4_scite_creds_absent_when_only_basic_env_set`.
  - This aligns with SOP-024's finding that the canonical Scite MCP path requires OAuth Bearer and should degrade visibly when Bearer is absent.
- **R4 idempotency test env-coupling: ADDRESSED.**
  - `test_ac3_resume_idempotency_no_double_dispatch` now forces `_scite_creds_present()` true so it cannot pass/fail based on ambient workstation credentials.
- **R5 cleanup: ADDRESSED.**
  - Research hook-site comments now describe default-ON behavior and visible degrade.
  - The live-dispatch audit allowlist now includes the S6 files with rationale.

**Residual watches:**

- **AC-L remains OPEN.** No live Scite DOI row, resolvable DOI proof, G2 citation-fidelity proof, workbook DOI-thread inspection, or forced-absent-creds live/degrade evidence is visible yet.
- **SOP-025 close remains OPEN.** No close entry or commit.
- **Spec reconciliation watch:** the untracked S6 spec still describes Basic fallback as live-reachable / credential-valid in the earlier D4 text. The code and SOP-024 remediation moved to Bearer-only. Before commit, reconcile the spec/story text or add a clear remediation note so the durable story does not contradict the shipped behavior.
- **Tier-1 still clean.** No manifest/parity change.

**Recommendations:**

1. Proceed to orchestrator re-verify if the remediation tests are green, then AC-L.
2. Before commit, reconcile the S6 spec with the Bearer-only R3 remediation.
3. AC-L should remain two-lane honest: real Scite cited DOI lane plus forced-absent-Bearer degrade lane.
4. At close, verify protected strays stay excluded and only intended S6 artifacts/code/tests/evidence are committed.

**Verdict:** `S6-REMEDIATION-DIFF-PRESENT-MUST-FIXES-LOOK-ADDRESSED-AC-L-PENDING`. The code now appears past the SOP-024 must-fix shape, but S6 is still not close-ready until live proof and close commit land.

### POLL-064 - S6 AC-L staged with frozen judges; no lane results yet (2026-07-07T05:42:04-04:00)

**Trigger:** heartbeat poll at `2026-07-07T09:42:04.316Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with origin.
- HEAD remains `6529f76a`; no S6 commit yet.
- Code/test diff footprint is materially unchanged from POLL-063.
- New untracked AC-L evidence directory appears:
  - `_bmad-output/implementation-artifacts/evidence/s6-acl-liveproof-20260707T093933Z/`
- Current evidence directory contains only:
  - `judge_a.py`
  - `judge_b.py`
  - `judges-frozen.json`
- No `PROOF.md`, lane facts, judge facts, drivers, run logs, DOI-resolution receipt, or close report exists yet.

**AC-L staging assessment:**

- `judges-frozen.json` records judges frozen at `2026-07-07T09:40:33Z` with sha256s:
  - `judge_a.py`: `10df7de0b0d3781bcbe7047a8cfd681def7803cc65ba4e08a39c440f3bc385b9`
  - `judge_b.py`: `8772907080ea0375de03aac01b5e78038ab4fc68a1e9acc2384442caf01429ea`
- Judge A criteria are strong and aligned with S6 AC-L:
  - real Scite dispatch;
  - provider exactly Scite, not consensus/gamma_docs;
  - at least one DOI-shaped `source_id`;
  - DOI resolves via `doi.org` with content-inspected title;
  - `source_ref == retrieval:scite:{DOI}`;
  - G2 citation-fidelity report/manifest present and unsourced count zero;
  - research narration appears in transcript;
  - walk proceeds past 04.55.
- Judge B criteria cover the honest-degrade lane:
  - creds precondition fired;
  - dispatch not reached;
  - present/empty `research_entries`;
  - visible credentials marker and relogin offer;
  - narration surfaces degrade;
  - $0 Scite spend;
  - walk proceeds.
- Judge B also includes a non-core bonus check for R1 re-dispatch after creds restore.

**Findings disposition:**

- **AC-L: STAGED, NOT PASSED.** The judges are frozen, but there are no `lane_a-facts.json`, `lane_b-facts.json`, `judge_a-facts.json`, `judge_b-facts.json`, or proof/log artifacts yet.
- **SOP-025 close: OPEN.** No close entry, no commit, no party concurrence.
- **R1/R2/R3/R4/R5 remediation: CARRY FORWARD as apparently addressed.** No new code changes alter POLL-063's assessment.
- **Spec reconciliation watch: STILL OPEN.** The untracked S6 spec still needs to reconcile Bearer-only Scite credentials with older Basic-fallback language before it becomes durable.
- **Tier-1: CLEAN SO FAR.** No manifest/parity diff.

**Recommendations:**

1. Treat AC-L as prepared only; do not accept close until both judges execute once and their output facts/proof are present.
2. At the next poll, verify judge hashes still match `judges-frozen.json` before trusting lane results.
3. Require `PROOF.md` or equivalent to record first-run-stands, exact commands, facts files, DOI inspected, and spend/degrade details.
4. Ensure S6 spec/story text is reconciled with Bearer-only behavior before commit.

**Verdict:** `S6-ACL-STAGED-JUDGES-FROZEN-NO-LANE-RESULTS`. The live proof harness is being prepared correctly, but there is no AC-L PASS evidence yet.

### POLL-065 - S6 lane A produced facts but no cited row; AC-L not passing yet (2026-07-07T05:52:04-04:00)

**Trigger:** heartbeat poll at `2026-07-07T09:52:04.457Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with origin.
- HEAD remains `6529f76a`; no S6 commit yet.
- Working tree code/test diff footprint remains the S6 remediation set.
- New untracked run directory appeared:
  - `runs/796a287d-719d-4be6-818c-6bbf5f6846af/`
- S6 evidence directory now contains lane-A staging/results:
  - `driver-log-lane-a.txt`
  - `lane_a_driver.py`
  - `lane_a-facts.json`
  - `walk-log-lane-a.txt`
  - frozen `judge_a.py`, `judge_b.py`, `judges-frozen.json`
- Still absent:
  - `judge_a-facts.json`
  - `lane_b-facts.json`
  - `judge_b-facts.json`
  - `PROOF.md`
  - SOP-025 close entry
  - S6 commit

**Lane A facts:**

- Trial: `796a287d-719d-4be6-818c-6bbf5f6846af`
- Corpus: `course-content/courses/tejal-apc-c1-m1-p2-trends`
- Default flip preconditions:
  - `MARCUS_RESEARCH_DISPATCH_LIVE` absent by name: true
  - `_research_dispatch_live()` true
  - `_scite_creds_present()` true
  - ready providers: `consensus`, `gamma_docs`, `scite`
- Walk proceeded:
  - pause sequence: `G0E -> G0R -> G1 -> G2B`
  - final status: `paused-at-gate`
  - final gate: `G2B`
  - research contribution present at node `04.55`
- But the M-witness did not materialize:
  - `research_entries: []`
  - `entries_count: 0`
  - `primary_doi: null`
  - `l2_citation_report: null`
  - `citation_manifest: null`
  - `g2_unsourced_citations: null`
  - narration line: "Research dispatch: no cited sources for this lesson..."
- Cost report shows model spend around `$0.30335995`, but the facts do not show a cited Scite row or DOI.

**Finding disposition:**

- **AC-L lane A: NOT PASSING YET.** The frozen Judge A criteria require at least one Scite cited entry with a real DOI, DOI resolution, source_ref shape, G2 citation-fidelity report/manifest, and cited-result narration. Current lane-A facts would fail those checks because the cited-entry set is empty.
- **Likely AC-L corpus/driver issue: OPEN.** The lane reached 04.55 but produced empty research entries. Either the selected corpus did not actually produce an in-scope research gap that dispatches, or the live Scite path returned no rows. In either case, this is not the required "literature-rich corpus" M-witness.
- **Judge execution: STILL OPEN.** No `judge_a-facts.json` exists, so the frozen judge has not recorded a formal pass/fail yet. The facts are enough to say it cannot honestly pass as-is.
- **Lane B: STILL OPEN.** No degrade lane facts yet.
- **SOP-025 / close / commit: OPEN.**
- **R1/R2/R3/R4/R5 remediation: CARRY FORWARD as apparently addressed.**
- **Spec reconciliation watch: STILL OPEN.**

**Recommendations:**

1. Do not claim AC-L lane A pass from this run. It produced zero cited sources and no DOI.
2. Before rerunning, confirm the corpus/plan actually creates at least one in-scope research-enrichment gap that routes through Tracy to Scite.
3. If Scite returned zero rows despite a valid gap, capture that as a live-path issue and adjust the witness corpus/query, not the acceptance bar.
4. Run the frozen judge only against a lane facts file expected to pass; if this facts file is judged, it should fail and remain on record under first-run-stands.
5. Continue to require lane B degrade facts, both judge outputs, and a proof file before close.

**Verdict:** `S6-ACL-LANE-A-RAN-BUT-M-WITNESS-MISSING`. The live lane reached 04.55, but it did not produce the required cited Scite DOI row, so S6 AC-L remains open.

### POLL-066 - S6 AC-L honest red documented; D7 research-goals bridge added to scope (2026-07-07T06:02:04-04:00)

**Trigger:** heartbeat poll at `2026-07-07T10:02:04.622Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with origin.
- HEAD remains `6529f76a`; no S6 commit yet.
- Code/test diff footprint is unchanged from POLL-065; no D7 implementation diff is visible yet.
- Canonical monitor now includes:
  - `S6 AC-L LIVE witness = HONEST RED`
  - `S6 research-bridge defect RE-SCOPE party`
- S6 evidence directory now includes:
  - `PROOF.md`
  - `judge_a-facts.json`
  - `defect-evidence.json`
  - diagnostics and cost reports
- Still no close commit, SOP-025 close entry, or lane-B pass evidence.

**Live witness result:**

- Lane A is now formally judged:
  - `judge_a-facts.json`: `FAIL`, `1/7`.
  - Only the walk-proceeded check passed.
  - All M-witness checks failed because `research_entries` was empty.
- `PROOF.md` honestly records:
  - lane A failed;
  - lane B was not run because it is blocked by the same root cause;
  - no fake gap injection;
  - no G1A workaround;
  - no retry-to-green.
- Spend recorded:
  - about `$0.30336` total LLM spend;
  - `$0` Scite spend because dispatch never fired.

**Root cause now documented:**

- Real Irene Pass-1 produced 5 `collateral.research_goals[]` on the live tejal trends corpus.
- All 11 in-scope `plan_units` had empty `identified_gaps` / `gaps`.
- Current research dispatch path reads only `identified_gaps` / `gaps`:
  - `has_research_goals()` and `IreneTracyBridge.process_plan_locked()` gate on that field.
- Real producer output and dispatch input are not bridged:
  - `collateral.research_goals[]` is emitted and schemaed, but not mapped into Tracy / Texas dispatch.
- Result:
  - default-ON flip is active;
  - Scite Bearer creds are present;
  - providers are ready;
  - 04.55 is reached;
  - but no Scite dispatch can fire on a canonical auto-approve production walk.

**Re-scope party disposition:**

- Winston / John / Murat unanimously selected Fix A:
  - consumer-side dual-read of `collateral.research_goals[]`;
  - in S6 scope;
  - recover the witness after fix.
- Binding limits:
  - mechanical field carry only;
  - carry `pedagogical_intent`, `binds_to_objective_id`, and `goal_id`;
  - do not synthesize `IdentifiedGap`;
  - do not decide research quality/type/relevance in S6.
- New S6 scope:
  - D7 bridge from real Irene `collateral.research_goals[]` to research dispatch.
  - AC-7 tests, including a real-Irene-shape bridge test where `research_goals` is populated and `identified_gaps` is asserted empty.
- New follow-on filed:
  - `research-quality-resolvable-doi-yield`, for the case where recovered dispatch fires but Scite returns no resolvable DOI.

**Finding disposition:**

- **POLL-065 lane-A empty witness: CLOSED AS HONEST RED, not fixed.** The team correctly did not claim pass.
- **New D7 bridge requirement: OPEN.** No implementation diff is visible yet for `collateral.research_goals[]` dual-read.
- **AC-L: RESET/OPEN pending D7 remediation and recovered witness.**
- **Lane B: OPEN.** Still blocked until the same reachability path is fixed.
- **Spec reconciliation watch: EXPANDED.** The durable S6 story now needs Bearer-only reconciliation plus D7/AC-7/recovered-witness amendments.
- **Tier-1: CLEAN SO FAR.** No manifest/parity diff.

**Recommendations:**

1. Watch next for D7 implementation in `research_wiring.py` and likely `skills/bmad_agent_tracy/scripts/irene_bridge.py`.
2. Verify tests do not use the smoke harness gap injection for the D7 bridge witness.
3. Keep Judge A/B thresholds frozen for the recovered witness; this was an honest structural red, not a pass.
4. If recovered dispatch fires but still yields no DOI, treat that under the filed quality/yield follow-on rather than weakening S6's dispatch-reachability fix.

**Verdict:** `S6-HONEST-RED-ROOT-CAUSE-FOUND-D7-OPEN`. The Claude team handled the failed AC-L correctly and found a real SPOC product defect; S6 remains open for the research-goals bridge and recovered live witness.

### POLL-067 - S6 D7 bridge diff present; recovered live witness still pending (2026-07-07T06:12:04-04:00)

**Trigger:** heartbeat poll at `2026-07-07T10:12:04.797Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with origin.
- HEAD remains `6529f76a`; no new commit yet.
- Working tree now shows the S6 D7 implementation/remediation footprint:
  - `app/marcus/cli/marcus_spoc.py`
  - `app/marcus/orchestrator/production_runner.py`
  - `app/marcus/orchestrator/research_wiring.py`
  - `skills/bmad_agent_tracy/scripts/irene_bridge.py`
  - `tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py`
  - `tests/integration/marcus/test_braid_s3_research_wiring.py`
- Diff stat: `7 files changed, 1056 insertions(+), 40 deletions(-)`.
- Untracked S6 spec/evidence remain visible:
  - `_bmad-output/implementation-artifacts/canonical-arc-s6-tracy-scite-canonical.md`
  - `_bmad-output/implementation-artifacts/evidence/s6-acl-liveproof-20260707T093933Z/`
- Still no SOP-025 close entry, recovered AC-L witness, or close commit.

**D7 implementation observed:**

- `app/marcus/orchestrator/research_wiring.py` now carries `collateral.research_goals[]` into the bridge plan dictionary.
- New `_research_goals_from_raw()` mechanically reads real Irene `collateral.research_goals[]` and carries:
  - `goal_id`
  - `pedagogical_intent`
  - `binds_to_objective_id`
- `has_research_goals()` now dual-reads:
  - existing unit `identified_gaps`
  - top-level bridge `research_goals`
- `run_research_wiring()` now treats either unit gaps or top-level research goals as an in-scope dispatch reason.
- `DeterministicPostureSelector.select_posture()` now carries `research_goal_id` as provider hint provenance when the brief includes it.
- `skills/bmad_agent_tracy/scripts/irene_bridge.py` now dual-reads both:
  - `units[].identified_gaps`
  - `research_goals[]`
- Research-goal briefs map:
  - `research_goal_id <- goal_id`
  - `gap_description <- pedagogical_intent`
  - `target_element <- binds_to_objective_id`
  - `scope_decision <- in-scope`

**Test coverage observed:**

- `tests/integration/marcus/test_braid_s3_research_wiring.py` now includes AC-7 coverage for the real Irene shape:
  - populated `collateral.research_goals[]`;
  - empty `plan_units[0].gaps`;
  - `has_research_goals(envelope) is True`;
  - dispatch reaches the fake provider path;
  - provider hint params include `research_goal_id == "rg-01"`;
  - resulting citation row is minted from the faked Scite response.
- Additional tests cover:
  - empty research goals do not dispatch;
  - union behavior when both identified gaps and research goals are present;
  - no smoke-harness gap injection import in the AC-7 module.

**Finding disposition:**

- **D7 bridge requirement: LIKELY ADDRESSED STRUCTURALLY.** The visible diff matches the re-scope party's mechanical dual-read requirement and avoids synthesizing `IdentifiedGap`.
- **AC-7 tests: PRESENT.** The new tests target the real-Irene shape that caused the honest red.
- **Recovered AC-L: STILL OPEN.** The only visible live evidence remains the honest-red directory from `20260707T093933Z`; no recovered lane facts, judge outputs, or close proof are visible yet.
- **Lane B: STILL OPEN.** No degrade-lane result is visible.
- **Spec reconciliation: STILL OPEN.** The untracked S6 story/spec needs the D7/AC-7/recovered-witness amendments, plus the earlier Bearer-only reconciliation.
- **Line-ending hygiene watch: OPEN.** Git warned that `skills/bmad_agent_tracy/scripts/irene_bridge.py` will be normalized from CRLF to LF on the next Git touch; verify this is acceptable before commit.
- **Tier-1: CLEAN SO FAR.** No manifest/parity diff is visible.

**Recommendations:**

1. Proceed to orchestrator re-verify and recovered AC-L only after the team records the D7/AC-7 spec update.
2. For the recovered live witness, keep the same acceptance threshold: at least one cited Scite row with resolvable DOI and the required citation manifest/report artifacts.
3. If the team uses fresh frozen judges for the recovered witness, confirm the criteria remain equivalent to the failed judge and that the honest-red first run remains preserved.
4. Before commit, inspect the Tracy bridge line-ending change so the commit does not hide unrelated formatting churn.

**Verdict:** `S6-D7-BRIDGE-DIFF-PRESENT-RECOVERED-WITNESS-PENDING`. The Claude team has produced the right-looking D7 bridge and AC-7 test shape; S6 still cannot close until the recovered live witness and close gate are present.

### POLL-068 - S6 recovered AC-L witness started; evidence not yet judgeable (2026-07-07T06:22:04-04:00)

**Trigger:** heartbeat poll at `2026-07-07T10:22:04.987Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with origin.
- HEAD remains `6529f76a`; no S6 commit yet.
- Working tree still carries the S6 D7/remediation footprint:
  - `app/marcus/cli/marcus_spoc.py`
  - `app/marcus/orchestrator/production_runner.py`
  - `app/marcus/orchestrator/research_wiring.py`
  - `skills/bmad_agent_tracy/scripts/irene_bridge.py`
  - `tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py`
  - `tests/integration/marcus/test_braid_s3_research_wiring.py`
- Diff stat is now `7 files changed, 1067 insertions(+), 40 deletions(-)`.
- Git still warns that `skills/bmad_agent_tracy/scripts/irene_bridge.py` will normalize from CRLF to LF on next touch.
- New evidence directory appeared:
  - `_bmad-output/implementation-artifacts/evidence/s6-acl-recover-liveproof-20260707T101919Z/`

**Recovered witness evidence observed:**

- Present in the recovered evidence directory:
  - `judge_a.py`
  - `judge_b.py`
  - `judges-frozen.json`
  - `lane_a_driver.py`
  - `lane_b_driver.py`
  - `driver-log-lane-a.txt`
  - `lane_a-stdout.txt`
  - `walk-log-lane-a.txt`
- Missing as of this poll:
  - `lane_a-facts.json`
  - `judge_a-facts.json`
  - `judge_b-facts.json`
  - `PROOF.md`
  - lane-A/lane-B facts or proof artifacts
- `judges-frozen.json` records judges frozen at `2026-07-07T10:20:23Z`, before lane A started.
- Lane A driver log records:
  - `MARCUS_RESEARCH_DISPATCH_LIVE` absent by name;
  - `_research_dispatch_live()=True`;
  - `_scite_creds_present()=True`;
  - ready providers `['consensus', 'gamma_docs', 'scite']`;
  - trial id `181c6621-d706-4f1f-807c-f51a7998657d`;
  - start on `tejal-apc-c1-m1-p2-trends`.
- `walk-log-lane-a.txt` shows live OpenAI calls continuing through at least `2026-07-07 06:23:28` local.
- A repo `.venv` Python process started at `2026-07-07 06:21:37` local was still active during this poll, consistent with the lane still running.

**Finding disposition:**

- **Recovered AC-L: IN PROGRESS / NOT JUDGEABLE YET.** The lane has started with frozen judges, but no facts file or judge result exists yet.
- **D7 bridge: CARRY FORWARD as structurally addressed.** No contrary evidence has appeared.
- **Lane B: STARTING / STILL OPEN.** A lane-B driver file appeared during the final check, but no degrade/re-auth lane facts or judge output is visible.
- **SOP-025 / close / commit: OPEN.**
- **Spec reconciliation: STILL OPEN.** No diff is visible for the untracked S6 spec, and no close entry has been added after the D7 recovery start.
- **Tier-1: CLEAN SO FAR.** No manifest/parity diff is visible.

**Recommendations:**

1. Do not infer pass/fail from the started recovered witness. Wait for `lane_a-facts.json`, frozen judge outputs, and `PROOF.md`.
2. Confirm lane A proves the new D7 condition explicitly: real `collateral.research_goals[]` present, in-scope `identified_gaps` empty, dispatch fires, and cited Scite DOI materializes.
3. Require lane B before S6 close, because R1 degrade-resume was a must-fix and cannot be closed by lane A.
4. Preserve the honest-red evidence directory and first-run narrative; the recovery should be framed as error-pause recovery, not a retry-to-green shortcut.

**Verdict:** `S6-RECOVERED-WITNESS-STARTED-NOT-YET-JUDGEABLE`. The Claude team has begun the recovered AC-L lane with frozen judges, but the evidence is incomplete and S6 remains open.

### POLL-069 - S6 recovered lane A PASS; lane B running (2026-07-07T06:32:05-04:00)

**Trigger:** heartbeat poll at `2026-07-07T10:32:05.156Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with origin.
- HEAD remains `6529f76a`; no S6 commit yet.
- Working tree still carries the same S6 D7/remediation diff:
  - `7 files changed, 1067 insertions(+), 40 deletions(-)`.
- New untracked run directory appeared for the recovered lane:
  - `runs/181c6621-d706-4f1f-807c-f51a7998657d/`
- Recovered evidence directory now includes:
  - `lane_a-facts.json`
  - `lane_a_resume.py`
  - `judge_a-facts.json`
  - `driver-log-lane-b.txt`
  - `walk-log-lane-b.txt`
  - `verify_freeze.py`
  - still no `lane_b-facts.json`, `judge_b-facts.json`, or `PROOF.md`.
- A lane-B repo witness process started at `2026-07-07 06:33:36` local was active during the final check.

**Lane A facts now visible:**

- Trial: `181c6621-d706-4f1f-807c-f51a7998657d`.
- Corpus: `course-content/courses/tejal-apc-c1-m1-p2-trends`.
- Dispatch mode:
  - `MARCUS_RESEARCH_DISPATCH_LIVE` absent by name.
  - `_research_dispatch_live() = true`.
  - `_scite_creds_present() = true`.
  - ready providers: `['consensus', 'gamma_docs', 'scite']`.
- Walk reached post-research gate:
  - final status `paused-at-gate`;
  - final gate `G2B`;
  - final error tag `null`.
- D7 reachability evidence is strong:
  - `locked_research_goals_count: 4`;
  - `in_scope_identified_gaps_count: 0`;
  - `shaped_intent_provenance` count `4`;
  - provider hints carry `research_goal_id` values `rg-01` through `rg-04`;
  - research contribution present at node `04.55`.
- Real Scite citation evidence is now present:
  - `entries_count: 5`;
  - all five `research_entries` are provider `scite`;
  - primary DOI: `10.1038/ijo.2010.252`;
  - primary source ref: `retrieval:scite:10.1038/ijo.2010.252`;
  - DOI resolution: HTTP 200 to `https://www.nature.com/articles/ijo2010252`;
  - `citation_manifest` present with five rows;
  - `g2_unsourced_citations: 0`;
  - `dropped_dispatch_failures.count: 0`.
- Narration now reports cited research completion:
  - "Research dispatch complete: 5 cited sources found..."
- Cost report is present:
  - total LLM cost about `$0.33139245`;
  - Scite-specific API spend not separately represented, but live dispatch produced Scite rows.

**Judge A result:**

- `judge_a-facts.json` landed during the final check.
- Verdict: `PASS`, `8/8`.
- Judge A confirms:
  - research goals present;
  - D7 provenance path is live with empty identified gaps;
  - all cited entries are Scite;
  - five real DOI rows exist;
  - primary DOI resolves with content inspection;
  - source ref shape is correct;
  - G2 citation manifest/gate passed with `unsourced_citations=0`;
  - narration surfaced;
  - walk proceeded to `G2B`.

**Evidence-integrity watch:**

- `driver-log-lane-a.txt` records `lane_a-facts.json` written twice:
  - first at `2026-07-07T10:28:21Z` with `entries=4`;
  - later at `2026-07-07T10:31:20Z` with `entries=5`.
- `lane_a-stdout.txt` still reflects the earlier `entries=4` write, while the current `lane_a-facts.json` reflects the later `entries=5` write.
- This may be a legitimate continuation/resume before any judge ran, but it must be explicitly explained before close because the recovery package is operating under first-run-stands rules.

**Spec/ledger reconciliation:**

- The untracked S6 story now includes D7, AC-7, and the recovered AC-L language.
- The S6 story header still says `READY-FOR-DEV`, so it has not yet been reconciled to dev-complete / AC-L-in-progress / close status.
- Canonical monitor still has no SOP-025 close entry after the D7 recovery start.

**Finding disposition:**

- **D7 bridge / recovered lane A: PASSED JUDGE A.** The frozen judge recorded 8/8 pass on the live facts: real `collateral.research_goals[]`, empty `identified_gaps`, Scite dispatch, cited entries, DOI resolution, G2 citation manifest, narration, and walk progression.
- **Evidence-integrity watch: STILL OPEN.** The lane-A facts overwrite should still be explained in `PROOF.md`, even though Judge A passed the final facts.
- **Lane B: RUNNING / STILL OPEN.** Lane B started with forced-absent creds (`creds_present(forced-absent)=False`) and live OpenAI calls are in progress, but no lane-B facts or judge output exists yet.
- **SOP-025 / close / commit: OPEN.**
- **Tier-1: CLEAN SO FAR.** No manifest/parity diff is visible.
- **Line-ending hygiene watch: OPEN.** The Tracy bridge CRLF-to-LF warning persists.

**Recommendations:**

1. Preserve/explain the earlier `entries=4` lane-A facts write in `PROOF.md` so first-run-stands remains auditable despite the later Judge-A-pass facts.
2. Complete lane B and `judge_b` before any S6 close claim; R1 degrade-resume was a must-fix and needs its own live/degrade witness.
3. Add `PROOF.md` that explicitly ties D7 to the live facts: research_goals present, identified_gaps empty, Scite dispatch fires, DOI resolves, and G2 citation evidence exists.
4. Reconcile the S6 story status and close ledger before commit; exclude the known strays and inspect the Tracy bridge line-ending churn.

**Verdict:** `S6-LANE-A-JUDGE-PASS-LANE-B-RUNNING`. The recovery has crossed the important technical threshold for D7 and Judge A passed; S6 is still open until lane B, Judge B, proof, close poll, and commit land cleanly.

### POLL-070 - S6 recovered AC-L both judges PASS; close artifacts still pending (2026-07-07T06:42:05-04:00)

**Trigger:** heartbeat poll at `2026-07-07T10:42:05.330Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with origin.
- HEAD remains `6529f76a`; no S6 commit yet.
- Working tree still carries the S6 implementation/test diff:
  - `7 files changed, 1067 insertions(+), 40 deletions(-)`.
- New untracked run directories now include:
  - `runs/181c6621-d706-4f1f-807c-f51a7998657d/` (lane A)
  - `runs/4579f59d-3a2f-4cb7-814e-b9027a848bbd/` (lane B)
- Recovered evidence directory now includes:
  - `lane_a-facts.json`
  - `judge_a-facts.json`
  - `lane_b-facts.json`
  - `judge_b-facts.json`
  - `witness-facts.json`
  - `PROOF.md`
  - both lane driver/log files
  - `judges-frozen.json`
- Still missing:
  - SOP-025 close entry in the canonical monitor
  - S6 close commit
- No active S6 witness Python process remained visible during the final process check.

**Lane A / Judge A:**

- Judge A verdict: `PASS`, `8/8`.
- Confirms:
  - real `collateral.research_goals[]` present;
  - `identified_gaps` empty;
  - D7 provenance path live;
  - all research entries are Scite;
  - five real DOI rows;
  - primary DOI `10.1038/ijo.2010.252` resolves with content inspection;
  - source-ref shape correct;
  - G2 citation manifest present with `unsourced_citations=0`;
  - narration surfaced;
  - walk proceeded to `G2B`.

**Lane B / Judge B:**

- Lane B trial: `4579f59d-3a2f-4cb7-814e-b9027a848bbd`.
- Forced-absent credentials were in effect:
  - `scite_creds_present: false`;
  - forced absent token path points inside the recovered evidence directory.
- Degrade path facts:
  - final status `paused-at-gate`;
  - final gate `G2B`;
  - `research_entries_present: true`;
  - `research_entries: []`;
  - `research_degrade.degraded: true`;
  - reason: `research enrichment skipped — credentials unavailable`;
  - relogin offer present;
  - `dispatch_reached: false`;
  - `scite_spend: 0`;
  - narration line surfaces the degrade and re-auth instructions.
- R1 re-dispatch bonus facts:
  - `attempted: true`;
  - `creds_restored: true`;
  - `redispatched: true`;
  - `entries_count: 5`;
  - primary DOI `10.3310/hsdr01140`.
- Judge B verdict: `PASS`, `4/4`.
- Judge B bonus R1: `PASS`.

**Evidence-integrity / close watches:**

- The lane-A facts overwrite is now explained in `witness-facts.json`:
  - `driver-log-lane-a.txt` recorded a first facts write with `entries=4`;
  - the final facts judged by Judge A show `entries=5`;
  - aggregate disclosure says two lane-A walks raced because the original background process did not die; both independently fired real Scite via D7, reached `G2B`, and shared the same primary DOI;
  - the judged facts were the intact later resume-walk facts with five entries, judged once.
- `PROOF.md` is now present and carries the same concurrency disclosure, freeze/run timing, judge pass table, and no-mutation attestation.
- Canonical monitor has no SOP-025 close audit after the D7 recovery.
- S6 story/spec exists and includes D7/AC-7/recovered AC-L language, but the story status still needs close reconciliation.
- The Tracy bridge CRLF-to-LF warning persists and should be inspected before commit.

**Finding disposition:**

- **Recovered AC-L lane A: PASS.**
- **Recovered AC-L lane B: PASS.**
- **R1 degrade-resume: PASS as Judge B bonus.**
- **D7 bridge: LIVE-PROVEN.**
- **S6 story close: STILL OPEN.** Both live lanes passed and the lane-A race is disclosed in aggregate facts plus `PROOF.md`, but SOP close, commit, and close/audit hygiene are not yet present.
- **Tier-1: CLEAN SO FAR.** No manifest/parity diff is visible.

**Recommendations:**

1. Treat S6 as live-proven but not closed until SOP-025, commit, and party concurrence/close poll land.
2. In the close audit, verify `PROOF.md` and `witness-facts.json` remain consistent on the lane-A concurrency disclosure and judged-facts selection.
3. Before commit, verify the evidence pack contains exactly the intended S6 artifacts and excludes the known strays/run directories unless deliberately scoped.
4. Inspect the Tracy bridge line-ending normalization so the commit does not hide unrelated churn.

**Verdict:** `S6-ACL-BOTH-JUDGES-PASS-CLOSE-PENDING`. The Claude team has recovered S6 technically: both lanes and both judges pass, including D7 and R1; the remaining work is close-package hygiene, SOP-025, commit, and concurrence.

### POLL-071 - S6 close commit pushed; SOP-025 concurs (2026-07-07T06:52:05-04:00)

**Trigger:** heartbeat poll at `2026-07-07T10:52:05.499Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with origin.
- HEAD is now `a55fd73d`:
  - `feat(canonical-arc-S6): Tracy/research Scite-canonical — live Scite dispatch on every run (LIVE-PROVEN via honest-RED->D7->recover)`
- `origin/dev/workbook-2026-07-06` is also at `a55fd73d`, so the S6 commit is pushed.
- Working tree after the S6 commit:
  - only `_bmad-output/implementation-artifacts/canonical-arc-claude-shadow-monitor-2026-07-06.md` is modified;
  - the modification is the appended SOP-025 close relay, not substrate code;
  - known strays remain untracked (`workbooks-test`, operator monitor ledgers, goal launcher, and run dirs).
- `git show a55fd73d -- pipeline-manifest.yaml app/styleguide/parity.py` is empty.

**Commit scope observed:**

- S6 commit includes:
  - canonical S6 story/spec;
  - both evidence packs:
    - honest-red first witness `s6-acl-liveproof-20260707T093933Z`;
    - recovered green witness `s6-acl-recover-liveproof-20260707T101919Z`;
  - production code changes:
    - `app/marcus/cli/marcus_spoc.py`;
    - `app/marcus/orchestrator/production_runner.py`;
    - `app/marcus/orchestrator/research_wiring.py`;
    - `skills/bmad_agent_tracy/scripts/irene_bridge.py`;
  - test/audit changes:
    - `tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py`;
    - `tests/integration/marcus/test_braid_s3_research_wiring.py`;
  - canonical monitor ledger.
- The previously untracked S6 spec/evidence directories are now tracked by the S6 commit.
- The known run directories remain untracked, including the lane A/B live run dirs; they were not committed.

**Canonical close relay:**

- The canonical monitor now has `SOP-025 — S6 STORY-CLOSE audit`.
- SOP-025 verdict:
  - `CONCUR`;
  - `S6 DONE STANDS`;
  - `arc substrate spine S0·S1·S2·S3·S4·S5·S6 COMPLETE + live-proven`;
  - all 6 checks pass;
  - findings `F-2501/F-2502` are INFO only.
- SOP-025 specifically records:
  - commit integrity clean;
  - Tier-1/parity frozen;
  - strays untracked;
  - default-ON research dispatch kill-switch committed;
  - Scite selector committed;
  - Bearer-only creds check committed;
  - D4 degrade entry path committed;
  - R1 degraded contribution falls through for re-dispatch;
  - D7 dual-read committed;
  - `narrate_research_result` wired;
  - Judge A 8/8 and Judge B 4/4 + R1 bonus;
  - AC-7 anti-regression committed;
  - post-commit green `64 passed / 1 skip`.

**Finding disposition:**

- **S6 close: CLOSED by commit `a55fd73d` and SOP-025 concurrence.**
- **D7 bridge: CLOSED / live-proven / committed.**
- **Recovered AC-L lane A/B: CLOSED / both judges pass.**
- **R1 degrade-resume: CLOSED / Judge B bonus pass.**
- **Tier-1/parity: CLOSED clean.**
- **Stray-exclusion: CLEAN.** Known strays remain untracked.
- **Monitor-ledger nuance: OPEN only as hygiene.** The canonical monitor's SOP-025 relay is currently an uncommitted local append after the S6 commit; this is not substrate risk, but it should be handled consistently with the team's ledger practice.

**Recommendations:**

1. Treat S6 as done and pushed; next substantive work can move to the operator checkpoint/S7 path.
2. Do not reopen S6 unless a later close-concurrence artifact contradicts SOP-025.
3. Keep excluding run dirs and the external monitor ledgers from follow-on commits.
4. If the canonical monitor is intended to remain committed exactly at S6 close, decide whether the post-commit SOP-025 relay should be rolled into the next docs/handoff commit or left as a transient monitor update.

**Verdict:** `S6-CLOSED-PUSHED-SOP025-CONCURS`. The Claude team completed S6: commit `a55fd73d` is pushed, both live lanes passed, D7/R1 are committed, Tier-1/parity stayed clean, and SOP-025 concurs.

### POLL-072 - DONE-SIGNAL met; wrapup commit pushed; monitor lane complete (2026-07-07T07:02:05-04:00)

**Trigger:** heartbeat poll at `2026-07-07T11:02:05.645Z`.

**Repo state:**

- Branch: `dev/workbook-2026-07-06`, synced with origin.
- HEAD is now `1c3df92d`:
  - `docs(session-18): WRAPUP — 🎯 Canonical Production Conversation arc COMPLETE, DONE-SIGNAL MET (S0-S6 all live-proven); S6 Tracy/Scite-canonical CLOSED`
- `origin/dev/workbook-2026-07-06` is also at `1c3df92d`.
- Working tree has no tracked modifications.
- Remaining untracked items are the known excluded/ambient artifacts:
  - `_bmad-output/artifacts/workbooks-test/`
  - external operator monitor ledgers
  - `goal-canonical-arc-s4-onward-2026-07-07.txt`
  - root `runs/<uuid>/` strays, including S6 live lane run dirs.

**Wrapup commit scope:**

- Commit `1c3df92d` is docs-only:
  - `SESSION-HANDOFF.md`
  - `_bmad-output/implementation-artifacts/canonical-arc-claude-shadow-monitor-2026-07-06.md`
- It does not modify `app/`, `skills/`, `tests/`, `pipeline-manifest.yaml`, or `app/styleguide/parity.py`.

**Canonical monitor / party close:**

- The canonical monitor now includes:
  - `S6 AC-L RECOVER witness (post-D7) = BOTH LANES GREEN`;
  - `SOP-025 — S6 STORY-CLOSE audit`;
  - `DONE-SIGNAL — fully-spawned party CONCURRENCE`.
- DONE-SIGNAL records:
  - final task in scope, S6 Tracy/research Scite-canonical, is accomplished and validated;
  - fully-spawned canonical-core party concurs unanimously, `4/4`;
  - SOP-025 corroborates;
  - branch pushed and origin synced;
  - Canonical Production Conversation arc `S0·S1·S2·S3·S4·S5·S6` is closed and live-proven.

**Session handoff:**

- `SESSION-HANDOFF.md` now front-loads:
  - DONE-SIGNAL met;
  - S6 closed via honest-red -> party -> D7 -> recover;
  - D7/R1/Bearer-only/degrade/narration fixes summarized;
  - next work is **S7 workbook**, with the party §9 operator spec review/edit/approval checkpoint before dev dispatch.
- It also records KG/ONBOARDING regen as owed.

**Finding disposition:**

- **S6: CLOSED.**
- **S4-onward goal: COMPLETE.**
- **DONE-SIGNAL: MET.**
- **Wrapup: PUSHED.**
- **Tracked worktree hygiene: CLEAN.**
- **Stray-exclusion: CLEAN.** Known run dirs, workbooks-test, and external monitor ledgers remain untracked.
- **Future work: S7 not started in repo at this poll.** The next substantive gate is the operator checkpoint, not autonomous substrate dev.

**Recommendations:**

1. Stop this S4-onward shadow-monitor heartbeat; its monitored goal is complete and further polls would only repeat a closed state.
2. Start a fresh monitor only when S7 is explicitly opened after the operator checkpoint, with S7-specific instructions.
3. Preserve the S7 guardrail: no workbook dev dispatch before operator spec review/edit/approval.
4. Carry KG/ONBOARDING regen into next wrapup/start hygiene.

**Verdict:** `GOAL-COMPLETE-DONE-SIGNAL-MET-MONITOR-CAN-RETIRE`. The Claude team completed the current goal and pushed the wrapup; no active S7 dev is visible yet.
