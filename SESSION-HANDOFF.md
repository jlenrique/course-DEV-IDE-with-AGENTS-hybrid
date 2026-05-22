# Session Handoff — 2026-05-21 (Trial-3 wiring SCP execution + attempt-2 launch + Epic-scope schema-drift discovery)

**Session date:** 2026-05-21 (single intensive session under operator directive "get the core wiring working and move through a CLI-only trial ASAP — then build out the promised but not delivered Marcus 'interactive' experience")
**Branch:** `trial/3-2026-05-21`
**Session-start anchor:** `0234783` (prior session's Path-B-decision handoff commit)
**HEAD at session-end:** WRAPUP commit landing at `<sha-resolves-at-push>`
**Commits this session:** 7 + WRAPUP (8 total)
**Branch state at session-end:** Origin in sync at HEAD. Working tree CLEAN.

---

## What was completed

**🎯 Three layered outcomes:** Trial-3-blocking wiring fix landed cleanly; Trial-3 attempt-2 verified the §02A composer is now invoked at G0 against a real corpus; attempt-2 surfaced a SECOND integration-drift gap (§02A→Texas wrangler schema mismatch) — operator-directed halt to batch the systemic fix rather than play whack-a-mole.

### Commits landed (in order)

1. **`371db9e` — `docs(scp): authoring + Round-1 ratification of Trial-3-blocking wiring SCP`**
   - SCP file authored at `_bmad-output/planning-artifacts/sprint-change-proposal-2026-05-21-trial3-wiring.md` (~330 lines including Round-1 verdicts).
   - Party-mode Round-1 ratification: 4-of-4 APPROVE-with-amendments (Winston W-A1/W-A2; Amelia AM-A1..AM-A5; Murat M-A1 CRITICAL + M-A2..M-A5; John J-A1/J-A2). No impasse; Quinn → John chain not invoked.
   - Marcus-interactive-experience-not-delivered-by-slab-7c deferred-inventory entry filed concurrently (Epic-scope post-Trial-3 architecture follow-on; surfaced when operator asked why the trial CLI bypasses Marcus-the-persona despite Slab-7c work).

2. **`12453bc` — `chore(tw-7c-4): allowlist +2 paths for §02A wiring fix substrate amendment (C1)`**
   - TW-7c-4 `PERMITTED_PYTHON_DIFFS` extended by 2 paths: `app/marcus/cli/trial.py` + `app/composers/section_02a/cli_adapter.py` (W-A1 placement).

3. **`6c060f4` — `chore(tw-7c-4): line-65 predicate now honors PERMITTED_PYTHON_DIFFS (C1b)`**
   - **Substantive party-mode-missed fold-in.** The 2026-05-19 SCP and the 2026-05-21 Round-1 ratification both reasoned about TW-7c-4's `unexpected == []` predicate (allowlist-aware, line 92) but missed that the `app_scope == []` predicate (line 65) was a hard ban on ALL `app/` Python edits with no allowlist override. Fold-in makes line-65 honor `PERMITTED_PYTHON_DIFFS`. Defense-in-depth preserved.

4. **`42ae4ec` — `fix(trial-cli): UTF-8 launcher hardening — close Trial-2 finding #1 cp1252 vector (C2b)`**
   - `_ensure_utf8_io()` helper at trial.py top of `start_trial`; closes the cmd.exe invocation-path gap surfaced at 2026-05-21T19:51 launch attempt. Idempotent. Ruff SIM105 nit recorded as deferred (filed to deferred-inventory as `trial-cli-sim105-utf8-io-try-except-pass`).

5. **`d15921f` — `chore(tw-7c-4): allowlist +2 paths for C2a's M-A1 wiring-contract tests (C1c)`**
   - Second party-mode-missed fold-in. The M-A1 amendment specified `tests/marcus_cli/test_compose_section_02a_directive_adapter.py` as a new test path but didn't surface that the new files would also require allowlisting. C1c folds in `tests/marcus_cli/__init__.py` + the test module.

6. **`ab5562d` — `fix(trial-cli): wire §02A composer into trial.py at G0 (C2a; close Trial-3 blocker)`**
   - NEW `app/composers/section_02a/cli_adapter.py` — public `compose_and_write(corpus_dir, run_dir, *, llm=None) -> tuple[Path, str]`. Default-resolves llm via `make_chat_model("marcus").chat` when None. Inline comments flag two known seams (`effective_trial_id` vs `Directive.run_id`; `ChatModelHandle.entry` discard).
   - `app/marcus/cli/trial.py`: legacy `directive_composer` import removed; call site at `start_trial` swaps to `compose_and_write(...)`.
   - NEW `tests/marcus_cli/test_compose_section_02a_directive_adapter.py` (Murat M-A1) — 4 wiring-contract test functions mocking `make_chat_model` + `compose` + `write_directive_yaml`. Asserts: adapter calls `make_chat_model("marcus")` exactly once when `llm=None`; `.chat` is what's passed as `llm` kwarg; return value is `(path, sha256_hex_digest)` tuple; injected `llm` skips `make_chat_model`.
   - AM-A4 grep audit verdict (clean): 7 test files reference `compose_directive` / `materialize_directive` via direct imports; no mocks that would silently break.
   - Pre-push verification: AM-11 token 52/52 GREEN; §02A composer suite 12/12 GREEN; TW-7c-4 line-65 + line-74 GREEN; new adapter tests 4/4 GREEN; collection-success (M-A5 replacement).

7. **`<this commit>` — `docs(handoff + deferred-inventory): session 2026-05-21 closeout + §02A-downstream-consumer-compatibility Epic-scope finding`**
   - Closes both trial-3-blocker entries with strikethrough + closure markers citing this session's commit chain.
   - Files NEW high-priority entry: `section-02a-downstream-consumer-compatibility-systemic-drift` — Epic-scope, blocking Trial-3 re-launch.
   - Files J-A1 follow-on entries: `trial-cli-effective-trial-id-vs-section-02a-composer-run-id-divergence` + `trial-cli-model-resolution-trail-not-appended-from-adapter`.
   - Files 5 doc-currency drift entries from operator-requested resource-audit pre-attempt-2.
   - Files SIM105 ruff nit as `trial-cli-sim105-utf8-io-try-except-pass`.
   - Writes this `SESSION-HANDOFF.md` + rewrites `next-session-start-here.md` with the new immediate action.

### Trial-3 attempt-2 evidence (preserved gitignored; local-only)

- **Run-id:** `6a3393f8-f369-4a30-b7c1-b50c60c1d1a2`
- **Run-dir:** `state/config/runs/6a3393f8-f369-4a30-b7c1-b50c60c1d1a2/`
- **directive.yaml:** sha256 `351a57fbe12aff4a49349c4a646618d92ae38a798ec53eee61668f74f8bbd703`; size 4192 bytes; 11 sources; LLM-judged role classifications (3 primary slides, 3 supporting slides, 5 other supporting). Compared to attempt-1's broken-fallback digest (`777d385b...`), the new digest confirms the §02A wiring took.
- **run.json:** `status: in-flight`, `completed_at: null`, `production_clone_launch_evidence_reason: registered-no-specialist-fired` — captures the trial envelope at the moment of Texas-dispatch crash.
- **bundle/:** empty — Texas wrangler wrote nothing.
- **Texas wrangler error (reproduced manually):** `[run_wrangler] directive error: sources[0] missing required field: ref_id`

### Party-mode + governance precedents established this session

- **Round 1 of the impasse-resolution chain governance (ratified 2026-05-19) successfully prevented escalation to human operator** — 4 voices each returned APPROVE-with-amendments; no Quinn → John tiebreaker needed.
- **Two party-mode-missed fold-ins (C1b + C1c) surfaced during execution** — the four voices each read the test file but none traced the dual-predicate scope through to the actual diff. Worth flagging in cross-trial-learnings as a process finding: "party-mode-reviewers-each-read-but-collectively-miss-a-dual-predicate-tripwire."

---

## What is next

**Operator directive 2026-05-21T22:30 (verbatim):** *"Stop the trial here. Save our work, and start next session with a BMAD sprint to correct and address as many related issues as can be identified now and corrected proactively."*

**Next session opens with a §02A-downstream-consumer-compatibility audit + Epic-authoring** rather than re-launching Trial-3 immediately. Rationale: the trial just exposed the SECOND "tested module, untested integration" gap in the same arc. Patching field-name drift one-at-a-time will likely surface more drift downstream (Texas bundle → Irene Pass-1, Irene packet → §04 G1, etc.). Better to inventory the full §02A→downstream integration surface, then batch the fix in a single Epic.

**Selected path:** Phase A probe (~30-45 min) → Phase B batched fix Epic (1-2 sessions) → Phase C Trial-3 attempt-3 re-launch from the same Tejal corpus. See `next-session-start-here.md` for the concrete first-action sequence and the probe checklist.

**Deferred to post-Trial-3 (unchanged):**
- 2026-05-19 SCP queued for post-Trial-3 housekeeping (broad-regression cleanup; −12 delta).
- `marcus-interactive-experience-not-delivered-by-slab-7c` Epic (Marcus-conversational-mediation gap).
- Doc-currency cleanup batch (5 entries this session).

---

## Unresolved issues / risks

**Critical (Trial-3-blocking; Epic-scope):**

- **`section-02a-downstream-consumer-compatibility-systemic-drift`** — three known §02A↔Texas-wrangler incompatibilities documented (`src_id`↔`ref_id`; `supporting`↔`supplementary`; `ignored`↔no-equivalent). Likely more drift at deeper §02A→downstream surfaces never probed by this trial. Resolution requires comprehensive probe + Epic-scope batched fix via substrate amendment (new SCP). Per operator directive, this is the next session's primary work.

**Tracked (non-blocking but in scope for the next session):**

- **J-A1 follow-ons (2 entries)** — `effective_trial_id` vs `Directive.run_id` divergence + `model_resolution_trail` audit-record discard. Both predicted in cli_adapter.py W-A2 inline comments and surfaced literally in attempt-2's stdout (the two-UUID divergence appeared). Recommended fold-in into the §02A-downstream-consumer Epic Phase B.

- **5 doc-currency drift entries** (g0-directive-composition-doc-stale-post-c2a; hil-verb-legend-s5-stub-paths-never-landed; hil-verb-legend-section-path-dot-vs-dash-syntax-drift; v5-pack-motion-enabled-flag-stale-across-launch-commands; g0-verb-set-mismatch-legend-vs-cli). Surfaced by operator-requested resource-audit pre-attempt-2. Non-blocking but sibling-class to the integration-drift Epic (same root cause: substrate evolved post-Slab-7c without lockstep doc updates).

- **`trial-cli-sim105-utf8-io-try-except-pass`** — single ruff nit on C2b's `_ensure_utf8_io`; recorded as deferred at Step 1 quality gate per the discipline. Trivial 4-line fix; should land alongside the next substrate-amendment touching trial.py.

**Carry-forward (still tracked from prior sessions; not Trial-3-blocking):**

- **`sprint-change-proposal-2026-05-19`** — ratified-but-not-executed post-Trial-3 housekeeping SCP. Murat M1-M4 + John J1-J2 amendment refinements still required pre-C1 dispatch.
- **`marcus-interactive-experience-not-delivered-by-slab-7c`** — Epic-scope post-Trial-3 architecture follow-on. Filed this session.
- **`s2-test-cleanup-residual-37`**, **`s6-tier-3-post-trial-3-housekeeping-batch`**, **`winston-post-s2-followon-architecture-currency`** — pre-existing trackers, not Trial-3-blocking.

---

## Key lessons learned

1. **Second occurrence of "tested module, untested integration" in one arc is a pattern, not a fluke.** The first occurrence (§02A composer not wired into trial CLI) was caught by Trial-3 attempt-1. The second occurrence (§02A composer schema drifts from Texas wrangler input schema) was caught by Trial-3 attempt-2. Both were Slab-7c deliverables that shipped with unit-test-only coverage and no end-to-end integration verification. **Recommend:** add "end-to-end integration smoke against the next downstream consumer" as a mandatory T11 review item for ANY new specialist module shipped via the `bmad-dev-story` cycle. Codify in `docs/dev-guide/dev-agent-anti-patterns.md` (or sibling).

2. **Party-mode-readers can each read a tripwire test file but collectively miss a dual-predicate scope.** C1b + C1c fold-ins surfaced because all four voices (Winston + Amelia + Murat + John) reasoned about line-74 `unexpected == []` but none traced line-65 `app_scope == []` through to the actual diff. **Recommend:** at any party-mode round reviewing tripwire-scope amendments, the chairperson should explicitly call out "does ANYONE see a second predicate in this test file?" as a sentinel question. Codify in CLAUDE.md or the impasse-chain governance.

3. **Operator's "weed-clearing" posture during pre-Marcus-interactive trials is a real, durable preference** worth honoring throughout the arc. Saved as a memory feedback entry; means accept-defaults at every gate; harvest quality nits to postmortem, not at-gate edits. Does NOT mean lowering bars permanently — flips once Trial-3 passes and Marcus-interactive lands.

4. **Operator's resource-audit-before-launch instinct caught real drift.** Five doc-currency findings surfaced because the operator asked for verification before re-launching. Without that ask, the operator could have copy-pasted the v5 pack's `--motion-enabled` launch command and crashed differently. Worth establishing as a session-START habit: "verify cited resources before consuming them."

5. **Dr. Quinn's impasse-resolution chain governance worked exactly as designed when not needed.** 4-of-4 APPROVE-with-amendments at Round 1 means the chain stays dormant. Governance amendment from 2026-05-19 succeeded by REDUCING orchestrator load (no second round; no escalation).

6. **The `bmad-correct-course` SCP workflow + party-mode ratification is a reliable substrate-amendment pattern.** Worked for both the 2026-05-19 SCP (queued) and the 2026-05-21-trial3-wiring SCP (executed this session). Total wall-clock from authoring → ratification → execution: ~3 hours including two party-mode-missed fold-ins. Tighter than expected.

---

## Validation summary

- **Quality gate (Step 1):** ruff clean on transient-edit surface EXCEPT 1 known SIM105 nit (filed deferred as `trial-cli-sim105-utf8-io-try-except-pass`)
- **TW-7c-4 freeze:** PRESERVED (both line-65 and line-74 predicates intact; allowlist-aware fold-ins C1b + C1c make app/ edits ratifiable via SCP without breaking the freeze for other paths)
- **§02A composer suite:** 12/12 GREEN unchanged
- **AM-11 launch-permission token:** 52/52 GREEN unchanged
- **New M-A1 adapter wiring-contract tests:** 4/4 GREEN (NEW coverage closing the gate-blind-spot)
- **Collection-success check (M-A5 replacement for the misleading collection-count check):** 4563 tests collected, 48 deselected, no collection errors
- **§02A composer end-to-end against Texas wrangler:** **FAIL** by design (this is the new finding) — verified manually that the wrangler exits 30 with `sources[0] missing required field: ref_id`
- **Trial-3 attempt-1 (legacy composer wired):** halted at G0 by operator with verb `x`; forensic evidence preserved at `state/config/runs/bef9a2c6-.../`
- **Trial-3 attempt-2 (§02A composer wired):** halted at first specialist dispatch (Texas exit 30); forensic evidence preserved at `state/config/runs/6a3393f8-.../`
- **Origin sync:** 7 commits pushed pre-WRAPUP at `ab5562d`; WRAPUP commit pushes at session-close
- **Party-mode rounds executed:** 1 substantive round (Round 1 SCP ratification) + zero impasse-resolution-chain invocations
- **Operator decisions captured as memory:** `feedback_weed_clearing_trial_posture` saved (pre-Marcus-interactive trial-run posture)

**Step 0a/0b skipped:** Cora not deployed in this repo. Step 0c (Cora SW draft) self-executed via direct authoring of `SESSION-HANDOFF.md` + `next-session-start-here.md`. No `reports/dev-coherence/` entries this session.

---

## Artifact update checklist

| Artifact | Updated this session | Verified at WRAPUP |
|---|---|---|
| `_bmad-output/planning-artifacts/sprint-change-proposal-2026-05-21-trial3-wiring.md` | ✓ NEW (~330 lines; ratified + executed; trial outcome captured in §6 closure status) | ✓ |
| `_bmad-output/planning-artifacts/deferred-inventory.md` | ✓ 2 trial-3-blocker entries CLOSED + 1 Epic-scope `section-02a-downstream-consumer-compatibility-systemic-drift` filed + 2 J-A1 follow-ons + 5 doc-currency drift entries + 1 SIM105 nit + 1 Marcus-interactive entry (earlier this session) | ✓ |
| `app/composers/section_02a/cli_adapter.py` | ✓ NEW (W-A1 placement) | ✓ |
| `app/marcus/cli/trial.py` | ✓ legacy directive_composer import swapped; UTF-8 helper added; call site updated | ✓ |
| `tests/marcus_cli/__init__.py` + `test_compose_section_02a_directive_adapter.py` | ✓ NEW (M-A1) | ✓ |
| `tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py` | ✓ allowlist +2 paths for C1; line-65 predicate now allowlist-aware (C1b); allowlist +2 more paths for test files (C1c) | ✓ |
| `CLAUDE.md` | NOT this session (no governance amendments) | N/A |
| `next-session-start-here.md` | ✓ rewritten with §02A-downstream-consumer-compatibility Epic as immediate action | ✓ |
| `SESSION-HANDOFF.md` | ✓ this file (replaces prior session's handoff) | ✓ |
| `_bmad-output/implementation-artifacts/sprint-status.yaml` | NOT this session (no story state transitions; SCP execution is governance-tracked, not story-tracked) | N/A |
| `_bmad-output/implementation-artifacts/bmm-workflow-status.yaml` | NOT this session (no phase transitions) | N/A |
| `docs/project-context.md` | NOT this session (no architecture/phase changes) | N/A |
| `docs/agent-environment.md` | NOT this session (no MCP/API/skill changes) | N/A |
| User-memory: `feedback_weed_clearing_trial_posture` | ✓ NEW (operator posture for pre-Marcus-interactive trials) | ✓ |

**Forensic evidence artifacts (gitignored; local-only; preserved for next session):**

- `state/config/runs/bef9a2c6-8305-44db-9194-9204f684f25e/` — Trial-3 attempt-1 forensic record (broken-fallback directive + cancellation record)
- `state/config/runs/6a3393f8-f369-4a30-b7c1-b50c60c1d1a2/` — Trial-3 attempt-2 forensic record (§02A-composed directive + crash-state run.json + empty bundle/)

---

## Session arc closure

The operator opened the session against a known Trial-3 blocker (§02A composer not wired into the trial CLI; surfaced 2026-05-21T19:51) and closed with a Trial-3 RE-launch that reached a SECOND blocker class (§02A schema drifts from Texas wrangler input). Net progress: blocker-1 ratified-fixed-executed-verified; blocker-2 identified-scoped-deferred-to-next-session-as-Epic. Substrate gained a working §02A composer wiring + 4 new integration-contract tests + 2 SCP-authored amendment commits. Doc surface gained a comprehensive resource-currency audit (~5 drift findings filed). Governance gained one successful round of the impasse-resolution chain (dormant by design when consensus held).

The operator's choice to **halt at the second blocker rather than play whack-a-mole** is the disciplined call: it banks attempt-2's value (§02A wiring proven; downstream-integration scope sized) without burning another 2 hours patch-cycle on what may be one of N integration-drift gaps. Next session opens with the systemic fix.

**`origin/trial/3-2026-05-21` is the resume point.** No master-merge this session — trial branch remains isolated until Trial-3 closes.
