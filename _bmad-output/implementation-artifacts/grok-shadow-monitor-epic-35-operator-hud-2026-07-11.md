# Grok Shadow Monitor — Epic 35 Operator HUD v1 — 2026-07-11

Independent shadow ledger for **Epic 35 (Operator HUD v1 — Flight Deck)** on branch `dev/hud-revival-2026-07-11`.

**Monitor lane:** Grok 4.5 (Cursor). Read-only surveillance of the active Claude/BMAD production session. Writes **only** this ledger. Does not edit production code, tests, runtime state, commits, branches, or BMAD-owned decision records.

**Sibling ledger (earlier phase):** `_bmad-output/implementation-artifacts/claude-shadow-monitor-hud-revival-2026-07-11.md` (UX + architecture gates). This Grok ledger covers the **Epic 35 green-light → story specs → dev** arc and re-checks durability/governance that prior SOPs flagged.

**Poll cadence:** every 15 minutes until the operator stops the monitor.

**Operator directive (2026-07-11 ~20:25):** (A) **Cross-check completion-note / Kanban test claims against actual pytest tails** (venv) — never trust reported numbers alone. Prefer: claimed suite → run same paths → compare pass count + whether cited files are in the close commit. (B) **Adversarial design/spec review** on each poll when new party decisions, story ACs, contract widenings, or stopgaps appear — challenge AD alignment, sequencing, claim-fence risk, and “honest thin” vs silent product lie.

---

## Standing Watchpoints (Epic 35)

1. **Product boundary.** HUD serves Marcus-SPOC runtime only — not proofing/concierge vehicles.
2. **Zero-button / zero-lie.** GET-only; projection sole input; unrecognized stays unrecognized; no command composition in the HUD.
3. **Seven-status completeness.** All seven `ProductionTrialStatus` values render distinctly.
4. **Party green-light amendments bind.** `_bmad-output/planning-artifacts/epic-35-party-greenlight-2026-07-11.md` amendments 1–14 (+ KEY DECISION 2 / 35.9) are acceptance law for story specs and DoD.
5. **Sequencing pins.** 35.2→35.3 serial; **35.9 after 35.5, before 35.8**; 35.8 after render/contract stable (`run_hud.py`); 35.7 last; any two agents on runner/manifest/contract serialize.
6. **Tier-2 before first substrate edit.** Story 35.0 + party-ratified manifest bump before `app/hud/**`, assembler, etc. **35.9 re-touches trigger paths** — re-read regime at T1.
7. **Formal ceremony.** Per-story `bmad-dev-story` + regime doc at T1 + `bmad-code-review` before close; no thin 35.7 evidence (DoD-over-clock).
8. **Kanban honesty.** `sprint-status.yaml` must list Epic 35 / 35.0–35.9 with truthful states once dispatched.
9. **Durability.** Phase/story artifacts **and the tests cited in DoD** committed+pushed at safety checkpoints.
10. **Claim fence.** No “HUD performed to spec” without Murat 10-item checklist + scoped-verdict schema (amendment 2); SC5 keep-it-open is L4, not decidable at 35.7.
11. **No premature app/ edits.** Until 35.0 closes, no production HUD/assembler/notify trees.
12. **Ambient hygiene.** Do not sweep `runs/*`, `_tmp-regression*`, Meeting Recording, unrelated monitors into Epic 35 commits.
13. **Evidence verification.** Completion-note / Kanban numeric claims must match monitor-run pytest tails AND files present on the cited close SHA.
14. **Adversarial design.** New specs/party dispositions challenged for AD-1 (projection sole input), additive-v1 honesty, stopgap lifetime, and claim-fence leakage into 35.7.

---

## Poll Log

### SOP-E35-000 — initial surveillance / monitor armed — 2026-07-11T16:45:00-04:00

**Scope reviewed (read-only):** `git status` / `git log` on `dev/hud-revival-2026-07-11`; party green-light `epic-35-party-greenlight-2026-07-11.md`; epic breakdown `epics-operator-hud-2026-07-11.md`; Claude sibling shadow ledger through SOP-HUD002; architecture workspace presence (`ARCHITECTURE-SPINE.md`, `walkthrough.html`); `sprint-status.yaml` grep for epic-35/35.*; probes for `app/hud`, `app/notify`, `operator_surface.py`; active Claude terminal (story AC drafting for 35.3). No tests run by this monitor. This ledger is the only write.

**Branch / HEAD:** `dev/hud-revival-2026-07-11` @ `5f2524c8` (`docs(architecture): operator HUD architecture spine finalized — 19 ADs + walkthrough deck`), tracking `origin` (0 ahead at poll). Recent chain: brief `59349de2` → UX `6b312fea` → architecture `5f2524c8`.

**Phase location (inferred):** Planning chain brief → UX → architecture appears **committed**. Active work is **Epic 35 green-light + epic/story authoring**. Claude terminal shows live drafting of Story 35.3 ACs (heartbeat live set, AD-7 topology reconciliation) consistent with green-light amendments 10/12. No dedicated `35-*.md` story-spec files found under `_bmad-output/implementation-artifacts/`. No `app/hud`, `app/notify`, or `operator_surface.py` on disk — **correct for pre-35.0**.

**Positive signals:**
- Party green-light record exists with 14 binding amendments, claim-check (Level), and readiness disposition — strong governance artifact.
- Epic breakdown embeds party-amended story order and ACs aligned to amendments (coverage map FR1/FR2→35.3+35.5; 35.7 scoped-verdict language; serial pins).
- Architecture walkthrough deck now present and committed (`walkthrough.html` @ `5f2524c8`) — closes prior Claude finding **F-HUD-0008** from this checkout’s perspective.
- F-HUD-0007 durability pattern for architecture appears resolved at HEAD (architecture committed).

**Findings:**

**F-E35-0001 [P1] Epic 35 planning artifacts are not durable on origin.** `epic-35-party-greenlight-2026-07-11.md` and `epics-operator-hud-2026-07-11.md` are **untracked**. Green-light claims readiness and that story specs / sprint-status update at dispatch, but the green-light + epic breakdown themselves are still local-only. Same durability failure class as F-HUD-0001/0007. **Recommendation:** commit + push before first `bmad-dev-story` opens.

**F-E35-0002 [P1] Kanban ledger does not yet contain Epic 35.** Grep of `sprint-status.yaml` finds no `epic-35` / `35.0`–`35.8` rows. Green-light text asserts “sprint-status.yaml updated at dispatch” — **not corroborated** in the working tree. Opening 35.0 without Kanban rows would violate WP8 and make done-bar flips invisible.

**F-E35-0003 [P2] Story-spec files not yet filed.** Epic breakdown lives in the planning epic doc; no per-story implementation specs (`35-0-…md` etc.) under implementation-artifacts. Green-light amendment 6 requires formal `bmad-dev-story` against a real story spec file. **Watch:** next poll should show either story files appearing or an explicit interim “specs-in-epic-doc” disposition (discouraged).

**F-E35-0004 [P2] Dual shadow ledgers.** Claude ledger stopped at architecture SOP-HUD002; this Grok ledger owns Epic 35 production monitoring. No conflict if both stay append-only and do not edit BMAD artifacts. Driver should cite both at close if consulted.

**F-E35-0005 [P3] Carry-forward from Claude ledger (status check).** F-HUD-0008 walkthrough — **appear resolved** at `5f2524c8`. F-HUD-0010 spine `status: draft` flip — not re-verified this poll (architecture memlog may still say draft). F-HUD-0009 specialty-service briefing disposition — check whether epic text made it explicit (spot-check deferred to next poll).

**Watchpoint verdicts at baseline:** WP1–WP7, WP10–WP12 not violated by visible state (no app/ HUD code yet). **WP8 open** (Kanban missing). **WP9 open** (green-light/epic untracked). WP6 standing — Tier-2 not yet executed (expected).

**Active-driver note (Claude terminal):** drafting 35.3 ACs mid-epic-file — consistent with planning, not yet evidence of premature substrate edit. Continue watching for any `app/` or `pipeline-manifest.yaml` touch before 35.0 closes.

**Verdict: MONITOR INITIALIZED — Epic 35 at green-light / epic-authoring; durability + Kanban gaps are the load-bearing risks before 35.0 opens.**

**Next poll:** ~15 minutes (loop armed). Expect: commit of green-light/epic, sprint-status rows, and/or first story-spec files.

---

### SOP-E35-001 — 15m poll — 2026-07-11T17:00:08-04:00

**Scope reviewed:** `git log`/`status` on `dev/hud-revival-2026-07-11`; sprint-status Epic 35 block; `epic-35-stories-2026-07-11.md`; dirty 35.0 surface (`pipeline-manifest.yaml`, `progress_map.py`, `tests/test_run_hud.py`); untracked `evidence/hud-35-0-completion-notes.md`; Claude terminal (code-review 35.0). No tests run by this monitor. Ledger-only write.

**HEAD / sync:** `2f622629` = `origin` (0 ahead / 0 behind). Two commits since SOP-E35-000:
1. `faf81cfc` — party green-light + amended epic + sprint-status rows
2. `2f622629` — `epic-35-stories-2026-07-11.md` filed (explicitly cites Grok F-E35-0003)

**Finding resolutions:**
- **F-E35-0001 [P1] CLOSED** — green-light + epic committed/pushed.
- **F-E35-0002 [P1] CLOSED** — Kanban block present: `epic-35-operator-hud-v1: in-progress`; `hud-35-0`…`hud-35-8` rows with sequencing comments.
- **F-E35-0003 [P2] CLOSED (acceptable form)** — stories of record at `epic-35-stories-2026-07-11.md` (combined SSOT, not nine separate files). Formal `bmad-dev-story` evidence visible via completion notes.

**Active work — Story 35.0 (Tier-2 gate):**
- Working tree dirty (uncommitted): manifest +11 trigger paths matching amendment-5 list (incl. `production_runner.py`); `progress_map.py` WAVE_LABELS; `test_run_hud.py` skip/repoint; completion notes untracked.
- No `app/hud` / `app/notify` / `operator_surface*` trees yet — correct for 35.0-only.
- Claude terminal: **code-review of story 35.0 diff** in flight (+ re-running `test_run_hud`).

**New findings:**
**F-E35-0006 [P2] Kanban lag vs live 35.0 work.** `hud-35-0-tier2-manifest-bump-test-disposition` still `ready-for-dev` while implementation + code-review are visibly underway. Flip to `in-progress` (then `review`) when committing 35.0 so the ledger matches ceremony.
**F-E35-0007 [P2] 35.0 not yet durable.** Manifest/test/progress_map + completion notes exist only in the dirty tree. Safety-checkpoint: commit+push after code-review fold, before opening 35.1 substrate.
**F-E35-0008 [P3] Monitor self-hygiene.** This Grok ledger is still untracked; bank it when the next Epic 35 docs/commit lands (or a monitor-only commit) so poll history survives clones.

**Watchpoints:** WP6 partially discharging (Tier-2 rows present, unverified lockstep exit-0 by this monitor). WP8/WP9 satisfied at planning layer. WP11 still holds (no premature HUD package). WP9 durability now applies to **35.0 code**.

**Verdict: GREEN-LIGHT/PLANNING GAPS CLEARED — 35.0 IN CODE-REVIEW; HOLD 35.1 UNTIL 35.0 COMMITTED + KANBAN ADVANCED.**

**Next poll:** ~15m. Expect: 35.0 commit/push, Kanban `review`→`done`, possible 35.1 open.

---

### SOP-E35-002 — 15m poll — 2026-07-11T17:15:12-04:00

**Scope reviewed:** HEAD/`origin` sync; sprint-status Epic 35 rows; commit `0f3fee72`; untracked 35.1 surfaces (`operator_surface.py`, schema JSON, dual pin tests); Claude terminal. Ledger-only write.

**HEAD / sync:** `0f3fee72` = `origin` (0/0). Message: `feat(hud-35.0): Tier-2 lockstep trigger-path extension + 4-failure disposition — review APPROVE`.

**Finding resolutions:**
- **F-E35-0006 [P2] CLOSED** — Kanban `hud-35-0` → `done` in the same close push (driver explicitly acknowledged SOP-E35-001 ordering).
- **F-E35-0007 [P2] CLOSED** — 35.0 durable on origin before 35.1 substrate opened.

**Story state:**
| Story | Kanban | Evidence |
|-------|--------|----------|
| 35.0 | **done** | committed+pushed; review APPROVE; checker exit 0 noted in Kanban comment |
| 35.1 | **in-progress** | untracked: `app/models/runtime/operator_surface.py`, `operator-surface.v1.schema.json`, `tests/unit/models/test_operator_surface_shape_pin.py`, `tests/contracts/test_operator_surface_parity.py` |
| 35.2–35.8 | backlog | unchanged |

**Sequencing hygiene:** No `app/hud` / `app/notify` / assembler yet — 35.1-only surface matches WP5/WP11. Claude waiting on contract-package agent (“Verifying operator_…”) — consistent with 35.1 dispatch post-35.0-close.

**New findings:**
**F-E35-0009 [P2] 35.1 not yet durable.** Contract package + pin tests exist only as untracked files. Expect commit+push + Kanban `review`/`done` before 35.2 opens (same durability pattern as 35.0).
**F-E35-0008 [P3] still OPEN** — this Grok ledger remains untracked; driver said it will bank in the next commit.

**Watchpoints:** WP6 discharged for Tier-2 registration (35.0 done). WP8 honest at this poll. WP9 applies to 35.1 until committed. No zero-button/server claims yet (correct).

**Verdict: 35.0 CLOSED CLEAN — 35.1 CONTRACT PACKAGE UNDER CONSTRUCTION; HOLD 35.2 UNTIL 35.1 COMMITTED.**

**Next poll:** ~15m. Expect: 35.1 pin-green + review/close commit, or mid-flight RED/green evidence.

---

### SOP-E35-003 — 15m poll — 2026-07-11T17:30:12-04:00

**Scope reviewed:** HEAD/`origin`; Kanban Epic 35 block; commit `cd7e3e12`; presence of `app/hud`/`app/notify`/assembler; Claude terminal (parallel agents + usage-limit prompt). Ledger-only write.

**HEAD / sync:** `cd7e3e12` = `origin` (0/0). `feat(hud-35.1): operator-surface contract package — review APPROVE, S1/S2 folded` — contract + schema + dual pins + completion notes + **this Grok ledger banked**.

**Finding resolutions:**
- **F-E35-0009 [P2] CLOSED** — 35.1 durable on origin before parallel lanes flipped in-progress.
- **F-E35-0008 [P3] CLOSED** — shadow ledger included in `cd7e3e12` (local appends continue here).

**Story state:**
| Story | Kanban | Disk evidence |
|-------|--------|---------------|
| 35.0 | done | prior |
| 35.1 | **done** | committed; 108 passed; byte-pin `debe6224` noted |
| 35.2 | **in-progress** | assembler path **absent** (agents just launched) |
| 35.4 | **in-progress** | `app/hud` **absent** |
| 35.6 | **in-progress** | `app/notify` **absent** |
| 35.3/35.5/35.7/35.8 | backlog | — |

**Sequencing check:** Post-35.1, opening **35.2 + 35.4 + 35.6** together matches green-light pins (35.4 blocked-by 35.1; 35.6 blocked-by 35.1; 35.2 after 35.1; runner-serial vs new-tree lanes). Claude UI shows background agents for 35.2 assembler and 35.4 GET-only server. **No file surface yet** — expect next poll to show first trees or a stall.

**New findings:**
**F-E35-0010 [P2] Operator-lane stall risk — Claude Fable-5 weekly limit prompt.** Terminal shows usage-limit interrupt (“Continue with Fable 5” vs “Switch to Opus 4.8”) while 35.2/35.4 agents were launching. If the orchestrator is blocked on that modal, parallel lanes may idle with Kanban already `in-progress`. **Recommendation:** operator clears the prompt promptly; next poll should show either first `operator_surface_assembler.py` / `app/hud/` / `app/notify/` files or confirm stall.
**F-E35-0011 [P3] Kanban ahead of disk for 35.2/35.4/35.6.** Rows flipped `in-progress` at dispatch before any path exists — acceptable if agents are live; becomes a false-green smell if still empty next poll after the usage prompt clears.

**Watchpoints:** WP5 sequencing OK so far. WP9 durability OK for closed stories. Watch 35.2 vs 35.4 ownership (`production_runner` vs `server.py` only).

**Verdict: 35.1 CLOSED CLEAN — THREE PARALLEL LANES DISPATCHED; WATCH FOR USAGE-LIMIT STALL BEFORE FIRST SUBSTRATE LANDS.**

**Next poll:** ~15m. Expect: assembler and/or `app/hud`/`app/notify` trees, or explicit Fable-limit stall confirmation.

---

### SOP-E35-004 — 15m poll — 2026-07-11T17:45:13-04:00

**Scope reviewed:** dirty tree for 35.2/35.4/35.6; `app/hud/server.py` route inventory; `app/notify/*`; assembler + `production_runner.py` + `next_action.py`; 35.4 completion notes; `pyproject.toml` HUD1 import-linter; Claude terminal. Ledger-only write. HEAD still `cd7e3e12` = origin (0/0) — **no new commits since 35.1**.

**Finding resolutions:**
- **F-E35-0010 [P2] DOWNGRADED / PARTIAL** — Claude terminal still shows the Fable-5 usage modal, but substantial substrate landed anyway (agents may have finished before the interrupt, or work continued under credits). Not a hard stall at this poll.
- **F-E35-0011 [P3] CLOSED** — disk now matches Kanban `in-progress` for 35.2/35.4/35.6.

**Parallel-lane surface (all uncommitted):**
| Lane | Paths present | Notes |
|------|---------------|-------|
| **35.2** | `operator_surface_assembler.py`, `production_runner.py` (M), `next_action.py`, assembler+emission tests | Runner-serial ownership looks correct |
| **35.4** | `app/hud/{server,data,__init__}.py`, `tests/hud/**`, completion notes, HUD1 import-linter | Completion notes claim exactly 3 GET routes; spot-check confirms `@app.get` for `/`, `/projection`, `/healthz` only — **zero-button surface looks intact** |
| **35.6** | `app/notify/{service,__main__,__init__}.py`, `tests/notify/**`, `state/config/hud-config.yaml` | New-tree lane present |

**Ownership hygiene:** 35.4 notes explicitly deny touching `production_runner.py` / `app/notify` / contract module — matches green-light serial/parallel pins. No `app/hud/render/` yet (35.5 correctly still backlog).

**New findings:**
**F-E35-0012 [P1] Three in-progress lanes undurable — large uncommitted surface.** Assembler, HUD server, notifier, tests, pyproject HUD1, and 35.4 completion notes exist only in the working tree. Push-cadence / safety-checkpoint risk is high (exactly the F-HUD-0001/0007 / F-E35-0007 class). Prefer per-lane commit after each story’s code-review APPROVE rather than one mega-commit.
**F-E35-0013 [P2] 35.4 claims completion while Kanban still `in-progress` and uncommitted.** Notes say “no commit — orchestrator commits post-review.” Fair if review is pending; next poll should show either review APPROVE + commit or an open review finding. Do not flip Kanban `done` without durable SHA.
**F-E35-0014 [P3] Terminal modal may be stale vs disk progress.** UI still offers Fable/Opus continue; reconcile so the orchestrator is not blocked from folding reviews/commits.

**Watchpoints:** WP2 zero-button — provisional PASS on 35.4 route inventory (tests claim mutation→405; not executed by this monitor). WP5 ownership — looking clean. WP9 — open until commits land.

**Verdict: PARALLEL LANES PRODUCING REAL SUBSTRATE — DURABILITY IS NOW THE CRITICAL PATH.**

**Next poll:** ~15m. Expect: first lane commit(s) (likely 35.4 if review-ready), or 35.2/35.6 review activity.

---

### SOP-E35-005 — 15m poll — 2026-07-11T18:00:13-04:00

**Scope reviewed:** still HEAD `cd7e3e12` = origin (0/0); all three parallel-lane completion-note packs; ntfy L3 witness; Claude terminal modal; dirty-tree inventory. Ledger-only write. **No new commits since 35.1 (~45+ minutes of undurable substrate).**

**Finding escalations:**
- **F-E35-0012 [P1] ESCALATED** — 35.2, 35.4, and 35.6 each have completion notes claiming story-complete / post-review commit pending, plus a real **35.6 ntfy L3 witness** (`hud-35-6-ntfy-witness.md`, WITNESS CLOSED). Entire surface remains untracked/modified. This is now the dominant Epic-35 risk (single-disk / interrupted-orchestrator loss).
- **F-E35-0010 [P2] RE-RAISED as blocking** — Claude terminal **still** shows the Fable-5 weekly-limit continue/switch modal with no visible progress past it. Disk work may have finished under agents, but **orchestrator cannot fold reviews/commits while blocked on that prompt**. Operator action required to clear the modal.

**Lane status (disk vs Kanban):**
| Story | Kanban | Completion notes | Durable? |
|-------|--------|------------------|----------|
| 35.2 | in-progress | yes — assembler + runner emit + next_action | **NO** |
| 35.4 | in-progress | yes — GET-only server (prior poll) | **NO** |
| 35.6 | in-progress | yes — notifier + **live ntfy witness** | **NO** |
| 35.3/35.5 | backlog | — | blocked correctly |

**Spot checks (non-executing):** 35.2 notes claim emit-never-raises wrappers on `_persist_envelope` and unchanged `run.json` write semantics — aligns with amendment 8. 35.6 notes claim derivation-only via contract (`derive_event_transitions` / `stall_condition`) — aligns with AD-18. `app/hud/render` still absent — 35.5 correctly not started.

**New findings:**
**F-E35-0015 [P1] Orchestrator commit gate is stalled with three “ready for review/commit” packs.** Recommend: clear Fable modal → run/finish code-reviews → commit+push **per lane** (or one carefully partitioned commit) **before** opening 35.3/35.5. Do not start 35.3 (same runner region as 35.2) until 35.2 is durable.
**F-E35-0016 [P3] apprise dependency only in dirty `pyproject.toml`.** 35.6 adds `apprise` — until committed, fresh clones cannot reproduce the L3 witness.

**Verdict: IMPLEMENTATION AHEAD OF GOVERNANCE CLOSEOUT — CLEAR USAGE MODAL AND BANK 35.2/35.4/35.6 IMMEDIATELY.**

**Next poll:** ~15m. Expect: commits on origin past `cd7e3e12`, or continued stall with F-E35-0015 still open.

---

### SOP-E35-006 — 15m poll — 2026-07-11T18:15:11-04:00

**Scope reviewed:** HEAD still `cd7e3e12` = origin (0/0); dirty tree unchanged in shape from SOP-E35-005 (35.2/35.4/35.6 packs + completion notes + ntfy witness); Kanban unchanged; Claude terminal still on Fable-5 continue/switch modal. Ledger-only write.

**Delta since SOP-E35-005:** **None material.** No commits, no Kanban flips, no new story trees (`app/hud/render` still absent), terminal modal still blocking orchestrator closeout. Undurable window now **~60+ minutes** since 35.1.

**Finding status:**
- **F-E35-0010 / F-E35-0015 [P1] STILL OPEN — no progress.** Operator has not cleared the usage modal; reviews/commits cannot fold.
- **F-E35-0012 [P1] STILL OPEN** — three completion-noted lanes remain local-only.
- **F-E35-0016 [P3] STILL OPEN** — `apprise` only in dirty `pyproject.toml`.

**Clock note:** Goal window was cited as 16:30–20:30. At this poll ~1h45m remains. With 35.3 (serial after 35.2), 35.5 (after 35.2/35.4), and 35.7 E2E still ahead, **every minute of commit stall compresses the DoD-over-clock path** (greenlight amendment 7: stop at last DoD-complete story — currently that would be **35.1** if the session dies dirty).

**New finding:**
**F-E35-0017 [P1] Session-failure mode: only 35.0+35.1 are recoverable from origin.** If the machine/process fails now, 35.2/35.4/35.6 implementation + L3 ntfy witness are at risk despite completion notes. This is no longer a hygiene nit — it is the binding Epic-35 failure mode.

**Verdict: HARD STALL ON ORCHESTRATOR CLOSEOUT — OPERATOR MUST CLEAR FABLE MODAL AND BANK THE THREE LANES.**

**Next poll:** ~15m. Same expectation: commits past `cd7e3e12` or continued P1 stall.

---

### SOP-E35-007 — 15m poll — 2026-07-11T18:30:13-04:00

**Scope reviewed:** HEAD still `cd7e3e12` = origin (0/0); dirty tree still carries full 35.2/35.4/35.6 packs + completion notes + ntfy witness; Kanban unchanged (`35.2/35.4/35.6` in-progress); Claude terminal **unchanged** Fable-5 continue/switch modal. Ledger-only write.

**Delta since SOP-E35-006:** **None.** Third consecutive no-op poll on closeout. Undurable window now **~75+ minutes** since 35.1. Goal window remaining ≈ **2 hours**.

**Finding status (no change):**
- **F-E35-0010 / 0015 / 0017 [P1] OPEN** — orchestrator blocked; only 35.0–35.1 recoverable from origin.
- **F-E35-0012 [P1] OPEN** — three completion-noted lanes still local-only.
- **F-E35-0016 [P3] OPEN** — apprise dirty-only.

**Monitor note:** Repeating the same P1 without operator action does not create new technical debt, but it **does** burn the 16:30–20:30 clock against 35.3→35.5→35.7. Honest DoD-over-clock projection if stall continues: session stops with durable bar = **35.1**, and 35.2/35.4/35.6 risk becoming unpaid local loss.

**Verdict: HARD STALL CONTINUES — NO REPO MOVEMENT; OPERATOR INTERVENTION STILL REQUIRED.**

**Next poll:** ~15m.

---

### SOP-E35-008 — 15m poll — 2026-07-11T18:45:13-04:00

**Scope reviewed:** new HEAD `f63a8e78` (= origin); Kanban review-state rows; `epic-35-credit-wall-handoff-2026-07-11.md`; residual dirty `app/notify/*`; Claude terminal (credits resumed). Ledger-only write.

**Delta — STALL BROKEN:**
- Commit `f63a8e78` — `wip(hud-35.2/35.4/35.6): dev-complete lanes banked at credit wall — reviews open, NOT closed` (+4439 lines). Explicitly **not** a close.
- Handoff artifact banked; cites Grok **F-E35-0017** as the reason to bank before reviews finished — correct response to the monitor.
- Kanban: 35.2/35.4/35.6 → **`review`** (not done). Comments record interrupted/open MUST findings.
- Claude past the Fable modal (“Now using usage credits”); background 35.6 agent still listed; dirty diffs on `app/notify/service.py` + `__main__.py` suggest mid-fold or died-mid-edit (handoff warned of this).

**Finding resolutions:**
- **F-E35-0010 [P1] CLOSED** — usage modal cleared; credits path active.
- **F-E35-0012 / F-E35-0017 [P1] CLOSED for durability** — lanes are on origin (WIP). Residual: they are **not** DoD-closed.
- **F-E35-0015 [P1] SUPERSEDED** — closeout unblocked; next gate is review-fold, not “clear modal.”

**Open review debt (binding — do not claim done):**
| Story | Review state |
|-------|----------------|
| 35.2 | Review **interrupted**; re-run before close (incl. digest-source hunt on paste command per handoff) |
| 35.4 | **MUST:** identity-guard bypass when `Unrecognized` raw dict still has readable mismatched `trial_id` → must 409 |
| 35.6 | **MUST:** ack keys never cleared on resume; plus S1/S2/S3; verify notify tree matches committed tests after possible mid-edit death |

**New findings:**
**F-E35-0018 [P2] Ambient pollution in bank commit.** `f63a8e78` swept six `_tmp-regression-*.txt` into `evidence/` (driver already noted prune). Should be removed in a hygiene commit so evidence/ stays claim-clean.
**F-E35-0019 [P2] 35.6 working tree dirty vs banked SHA.** `app/notify/service.py` and `__main__.py` modified after `f63a8e78`. Either finish the MUST-fold and amend via new commit, or revert to HEAD before re-review — do not leave ambiguous mid-fix state.
**F-E35-0020 [P1] Do not open 35.3 until 35.2 closes.** Handoff checklist agrees (serial runner region). Kanban still correctly blocks 35.3.

**Watchpoints:** Claim hygiene good — commit message and Kanban refuse false “done.” Zero-button/35.4 MUST must land before 35.4 close. `app/hud/render` still absent (35.5 backlog OK).

**Verdict: DURABILITY RECOVERED — THREE LANES IN REVIEW WITH OPEN MUSTS; FOLD BEFORE 35.3.**

**Next poll:** ~15m. Expect: MUST folds + re-review, or continued review work on dirty notify.

---

### SOP-E35-009 — 15m poll — 2026-07-11T19:00:12-04:00

**Scope reviewed:** HEAD `9d8eb339` = origin (0/0); three new commits since SOP-E35-008; Kanban; dirty assembler; Claude terminal mid-35.2 fold. Ledger-only write.

**Commits since last poll:**
1. `c556508d` — **35.6 CLOSED** (M1 pause-episode reset + S1/S2/S3 + N4 folded; ntfy witness retained)
2. `4873b74c` — chore: untrack ambient `_tmp-regression*` (**F-E35-0018 addressed**; files may remain on disk untracked — OK)
3. `9d8eb339` — **35.4 CLOSED** (MUST-1 raw-identity 409 + RFC ETag + env exits + honest placeholder)

**Finding resolutions:**
- **F-E35-0018 [P2] CLOSED** — ambient regression files untracked from evidence/.
- **F-E35-0019 [P2] CLOSED** — notify dirty state resolved via 35.6 close commit (no residual notify M in status).
- Prior 35.4/35.6 MUST debt from handoff — **folded and stories marked done**.

**Story board now:**
| Story | Kanban | Notes |
|-------|--------|-------|
| 35.0 / 35.1 / **35.4** / **35.6** | **done** | |
| **35.2** | **review** | Still open; assembler file dirty; Claude actively editing assembler + tests (“Driving Epic 35 dev chain”) |
| 35.3 | backlog | Correctly blocked until 35.2 closes (**F-E35-0020** still binds) |
| 35.5 | backlog | Unblocked on 35.4 side; still needs 35.2 |
| 35.7 / 35.8 | backlog | |

**New findings:**
**F-E35-0021 [P2] 35.2 is the sole remaining parallel-lane gate.** With 35.4/35.6 closed, critical path is: finish 35.2 re-review folds → close → then 35.3 (serial) and 35.5 (needs 35.2+35.4). Dirty `operator_surface_assembler.py` indicates fold-in-progress — expect close commit next.
**F-E35-0022 [P3] Goal clock.** ~1h30m left in cited 16:30–20:30 window. De-scope ladder (handoff) may engage for 35.5 depth; DoD-over-clock still forbids thinning 35.7 evidence.

**Watchpoints:** Claim hygiene good on 35.4/35.6 close messages. Zero-button MUST on 35.4 folded. No premature 35.3/render tree (`app/hud/render` still false).

**Verdict: 35.4 + 35.6 CLOSED CLEAN — 35.2 RE-REVIEW/FOLD IN FLIGHT; THEN 35.3/35.5.**

**Next poll:** ~15m. Expect: 35.2 → done on origin, or continued assembler fold.

---

### SOP-E35-010 — 15m poll — 2026-07-11T19:15:13-04:00

**Scope reviewed:** HEAD `c1a4033f` = origin (0/0); Kanban; clean key surfaces; Claude terminal credit-wall again. Ledger-only write.

**Commits since last poll:**
1. `86292fdd` — **35.2 CLOSED** (tick-start guard + `reentered_from` + held-reader smoke; 585 green)
2. `c1a4033f` — handoff updated: wall recovered, **5 stories closed** (35.0/35.1/35.2/35.4/35.6)

**Finding resolutions:**
- **F-E35-0020 [P1] DISCHARGED** — 35.2 closed; serial gate to 35.3 is open.
- **F-E35-0021 [P2] CLOSED** — sole parallel-lane gate cleared.

**Story board now:**
| Story | Kanban | Notes |
|-------|--------|-------|
| 35.0 / 35.1 / **35.2** / 35.4 / 35.6 | **done** | Five closed on origin |
| **35.3** | **backlog** | Comment still says `blocked-by 35.2` — **stale** after 35.2 close |
| 35.5 | backlog | Unblocked on 35.2+35.4 deps |
| 35.7 / 35.8 | backlog | |

**Working tree:** key HUD/Marcus/notify paths clean. No `app/hud/render` yet (35.5 not opened).

**Active-driver / credit wall:**
Claude terminal: **monthly spend limit hit again** while spawning “Dev story 35.3 start-path integration” — background agent **failed** (API error / spend limit). Goal still shows ~2h active. Same failure class as earlier credit-wall arc, but after five-story close bank.

**New findings:**
**F-E35-0023 [P1] Credit wall re-hit mid-35.3 open.** 35.3 was correctly attempted after 35.2 close, then killed by spend limit. Operator must top up / switch model / hand off before 35.3 substrate lands. Do not treat “35.3 started” as durable without commit.
**F-E35-0024 [P2] Kanban stale block comment on 35.3.** Row still `backlog # blocked-by 35.2` after 35.2 `done`. Flip to `ready-for-dev`/`in-progress` when work resumes so WP8 stays honest.
**F-E35-0025 [P2] Clock vs remaining scope.** ~1h15m left in 16:30–20:30 window; remaining = 35.3 + 35.5 (+ optional depth) + 35.8 + 35.7. De-scope ladder for 35.5 likely; DoD-over-clock still binds 35.7.

**Verdict: FIVE STORIES CLOSED CLEAN — 35.3 UNBLOCKED BUT STALLED ON CREDIT WALL; OPERATOR ACTION REQUIRED.**

**Next poll:** ~15m. Expect: wall cleared + 35.3 in-progress, or idle/handoff-only.

---

### SOP-E35-011 — 15m poll — 2026-07-11T19:30:14-04:00

**Scope reviewed:** HEAD still `c1a4033f` = origin (0/0); Kanban unchanged; Claude terminal still spend-limited; no new Epic 35 commits since SOP-E35-010. Ledger-only write.

**Delta vs last poll:** **None on critical path.** No new commits (~27m since handoff `c1a4033f`). Five stories remain closed; 35.3–35.5/35.7/35.8 still backlog. Key HUD/Marcus/notify surfaces still clean of tracked diffs. `app/hud/render` still absent.

**Credit wall:** Claude terminal output **unchanged** — same spend-limit message; “Dev story 35.3…” agent still failed. Goal banner still active but no progress. **F-E35-0023 remains OPEN (P1).**

**Kanban:** 35.3 still `backlog # blocked-by 35.2` — **F-E35-0024 still OPEN** (stale after 35.2 done).

**Ambient:** working tree has ~28 dirty/untracked lines (monitor ledger + ambient evidence/tmp noise); none are production 35.3 substrate.

**Clock:** ~1h left in cited 16:30–20:30 window. Without operator credit/model recovery, remaining stories will miss the goal window; DoD-over-clock still prefers a clean last closed story over a thin rush.

**Verdict: STALLED — credit wall holds; no 35.3 progress; operator action still required.**

**Next poll:** ~15m. Expect: recovery + 35.3 open, or continued idle (possible session stop/handoff).

---

### SOP-E35-012 — 15m poll — 2026-07-11T19:45:14-04:00

**Scope reviewed:** HEAD still `c1a4033f` = origin (0/0); Kanban unchanged; Claude terminal still spend-limited; no alternate driver terminal active on Epic 35. Ledger-only write.

**Delta vs last poll:** **None.** ~42m since last Epic 35 commit. Five closed stories banked; 35.3–35.8 unchanged. Key production surfaces clean; no `app/hud/render`.

**Credit wall:** Same terminal freeze — spend limit + failed 35.3 agent. Goal banner now shows **~3h** elapsed (still “active” with no progress). **F-E35-0023 OPEN.** **F-E35-0024 OPEN** (35.3 Kanban still stale `blocked-by 35.2`).

**Clock:** ~45m left in cited 16:30–20:30 window. Realistic remaining scope (35.3+35.5+35.8+35.7) will not fit unless wall clears immediately and de-scope ladder engages hard. Prefer durable five-story bank over a thin incomplete 35.3.

**Verdict: STILL STALLED — third consecutive no-progress poll; credit wall remains the blocker.**

**Next poll:** ~15m. Expect: continued idle near goal-window end, or operator recovery/stop.

---

### SOP-E35-013 — event poll (Opus resume) — 2026-07-11T19:55:48-04:00

**Trigger:** Operator notice — story authoring recommenced with **Opus 4.8** as alternate model (post spend-limit). Out-of-cadence survey; ledger-only write.

**HEAD / sync:** `0c011fab` = origin (0/0). Message: `chore(sprint): 35.3 + 35.5 dispatched in parallel (Opus, post spend-limit switch)`.

**Finding resolutions:**
- **F-E35-0023 [P1] CLOSED** — credit wall cleared via model switch; work resumed.
- **F-E35-0024 [P2] CLOSED** — Kanban honesty restored: 35.3 and 35.5 both `in-progress` with accurate comments (35.3: runner free post-35.2; 35.5: de-scope ladder, `app/hud` only, disjoint from 35.3).

**Story board now:**
| Story | Kanban | Notes |
|-------|--------|-------|
| 35.0 / 35.1 / 35.2 / 35.4 / 35.6 | done | banked |
| **35.3** | **in-progress** | Opus; runner region |
| **35.5** | **in-progress** | Opus; parallel, de-scope ladder; no `app/hud/render` on disk yet at this poll |
| 35.7 / 35.8 | backlog | |

**Driver note (Claude terminal):** Waiting on **2 background agents**; processing as they report. Operator asked to revise goal from clock deadline → **complete when all Epic stories fully authored** (~4 remaining). Driver acknowledged DoD-over-clock / no thin 35.7: will bank 35.3/35.5 as dev-complete-pending-review if needed and re-gate 35.7/35.8 rather than force a “performed to spec” verdict.

**Sequencing hygiene:** Parallel 35.3∥35.5 matches green-light (disjoint regions: runner vs `app/hud`). **Watch:** no shared-file collision; 35.8 still strictly after 35.5; 35.7 last with scoped-verdict claim fence.

**New findings:**
**F-E35-0026 [P2] Goal contract flipped from 4h window to epic-complete.** Clock 16:30–20:30 is no longer the stop criterion; authorship completeness is. Monitor will track story closes + claim hygiene rather than “minutes left.” Prior F-E35-0025 clock pressure is **superseded** for stop-decision purposes (still useful as pacing context only).
**F-E35-0027 [P3] Dual Opus lanes in flight — durability lag expected.** Substrate may appear dirty before the next bank commit; do not treat agent progress as closed until Kanban → review/done + origin.

**Verdict: RECOVERED — 35.3 + 35.5 DISPATCHED IN PARALLEL ON OPUS; MONITOR RESUMES ACTIVE WATCH.**

**Next poll:** ~15m (cadence). Expect: dirty/render trees and/or first 35.3 or 35.5 bank commit.

---

### SOP-E35-014 — 15m poll — 2026-07-11T20:00:12-04:00

**Scope reviewed:** HEAD `456d7719` = origin (0/0); Kanban; dirty 35.3/35.5 substrate; Claude terminal still waiting on 2 Opus agents. Ledger-only write.

**Commits since SOP-E35-013:**
1. `456d7719` — handoff: goal revised — **no deadline**; complete when all 4 remaining stories authored (**F-E35-0026 corroborated on origin**).

**Kanban:** unchanged — 35.3 + 35.5 still `in-progress`; 35.7/35.8 backlog. Epic comment still mentions old 4h window (cosmetic lag vs handoff; not a WP8 lie while stories themselves are accurate).

**Substrate (dirty / untracked — not yet durable):**
- 35.3: `M app/marcus/orchestrator/production_runner.py`; `?? preflight.py`; `?? evidence/hud-35-3-completion-notes.md`
- 35.5: `?? app/hud/render/` (so far `styles.py` only — render package started)
- Regions still disjoint — sequencing hygiene OK so far.

**Driver:** Still waiting on 2 background agents; stated close path = code-review → fold → commit/push → Kanban → shadow poll → 35.8 after 35.5 → 35.7 last with scoped-verdict. One visible agent: “Adding PreflightGate…” (~9m).

**Findings:**
- **F-E35-0027 [P3] still OPEN** — durability lag expected; substrate present but uncommitted.
- **F-E35-0028 [P3]** Epic Kanban header comment still cites `16:30-20:30` after goal flip — refresh when convenient so epic-row matches handoff (story rows already fine).

**Verdict: BOTH LANES BUILDING — RENDER + PREFLIGHT APPEARING; AWAIT BANK COMMITS + REVIEW.**

**Next poll:** ~15m. Expect: more render modules and/or 35.3/35.5 review/close commits.

---

### SOP-E35-015 — 15m poll — 2026-07-11T20:15:11-04:00

**Scope reviewed:** HEAD still `456d7719` = origin (0/0); Kanban epic-row refresh; expanded dirty 35.3/35.5 trees; Claude mid code-review + party. Ledger-only write.

**Commits:** none since SOP-E35-014 (still pre-bank). **F-E35-0027 durability lag remains OPEN.**

**Kanban:** 35.3/35.5 still `in-progress`. Epic header comment now says goal REVISED (no deadline) — **F-E35-0028 CLOSED**.

**Substrate growth (uncommitted):**
- **35.3:** `preflight.py`, `production_runner.py`, `trial.py`, unit tests (`test_preflight`, `test_start_path_sequence`), completion notes + **preflight live witness** evidence.
- **35.5:** `app/hud/render/` now `{__init__,client,page,styles}.py`; `server.py` + `test_server_routes.py`; render fixtures/units/goldens; `pyproject.toml`; 35.5 completion notes.
- Regions still look disjoint (marcus orchestrator/cli vs app/hud) — good.

**Driver ceremony:** 35.5 agent finished enough to start **code-review** (backgrounded) **in parallel with a focused party** on a “contract-gap” key decision (Winston/John + Splinter/Level). Monitor watch: party outcome must not invent product surface just to unblock review; claim fence still binds for 35.7.

**New findings:**
**F-E35-0029 [P2] Large dual-lane dirty bank without origin commit.** Both stories appear near/at completion-notes stage while HEAD is still the goal-revision doc. Prefer bank WIP or close commits soon (credit-wall lesson) before opening 35.8.
**F-E35-0030 [P2] Contract-gap party in flight on 35.5.** Track whether disposition is fold-into-35.5, defer-to-follow-on, or scope cut under de-scope ladder — and that Kanban/evidence match the decision.

**Verdict: DEV SUBSTANTIALLY ADVANCED — 35.5 IN REVIEW + CONTRACT PARTY; 35.3 EVIDENCE PRESENT; AWAIT FOLDS + DURABLE CLOSES.**

**Next poll:** ~15m. Expect: review findings / party memo / first close commit(s).

---

### SOP-E35-016 — event + claim-audit poll — 2026-07-11T20:25:45-04:00

**Trigger:** Operator directive to (1) verify completion-note numbers against pytest tails, (2) be more adversarial on design/spec. Also catches closes that landed since SOP-E35-015. Ledger-only write; monitor ran `.venv` pytest read-only.

**HEAD / sync:** `20cd0744` = origin (0/0). Commits since SOP-E35-015:
1. `6f7df143` — **35.3 CLOSED** (review APPROVE)
2. `20cd0744` — **35.5 CLOSED** + party KEY DECISION 2 files **35.9** (stories + greenlight + Kanban)

**Board:** 35.0–35.6 done; **35.9 `ready-for-dev`**; 35.8/35.7 backlog. Driver: 35.9 building on Opus.

**Finding resolutions:**
- **F-E35-0029** partially closed (closes committed) — see **F-E35-0031** for remaining durability hole.
- **F-E35-0030 CLOSED** — party disposition = new story **35.9** (widen contract + Projection-Demands parity pin); 35.5 labeled stopgap for deliverables-from-`last_artifact`.

---

#### Claim audit (operator directive A)

| Claim source | Claim | Monitor verification | Verdict |
|---|---|---|---|
| 35.3 notes | story tests 21 passed | `pytest test_preflight.py test_start_path_sequence.py` → **21 passed** | **MATCH** |
| 35.3 notes / Kanban | `tests/unit/marcus` 514 passed | `pytest tests/unit/marcus` → **514 passed** (collect 514/517, 3 deselected) | **MATCH** |
| 35.5 notes | `pytest tests/hud` → 33+29=**62** green | Disk (incl. untracked render tests): **61 passed** | **MISMATCH (−1)** vs notes; Kanban says 61 |
| 35.5 Kanban | “61 tests” | Disk: 61 passed | MATCH disk / **NOT on close SHA** |
| 35.5 close `20cd0744` DoD | implies render goldens/units shipped | `git ls-tree 20cd0744 tests/hud/` = only `_helpers`, `conftest`, `test_data`, `test_server_routes`. **Untracked:** `_render_fixtures.py`, `test_render_goldens.py` (23 `test_`), `test_render_units.py` (5 `test_`) | **FAIL** |
| 35.5 close SHA only | — | `pytest` on tracked `tests/hud/*.py` only → **33 passed** | Origin proves server-route suite only, **not** the golden matrix cited in notes |

**F-E35-0031 [P1] 35.5 closed without committing its render test suite.** Completion notes and Kanban cite ~61 hud tests / golden matrix; those files remain **untracked**. A fresh clone at `20cd0744` only has **33** `tests/hud` passes. This is exactly the fabricated-green class the operator flagged — numbers were true on a dirty tree, false as durable evidence. **Recommendation:** immediate follow-up commit adding the three render test/fixture files (or reopen 35.5 until they land); do not treat 35.5 DoD as durable until then.

**F-E35-0032 [P3] Notes arithmetic drift.** Notes claim 62; live tail and Kanban say 61. Minor, but reinforces “don’t trust the prose count.”

**F-E35-0033 [P3 info]** 35.3 numeric claims **reproduced**. Live witness doc is honest about deferred full trial-start L3 → 35.7.

---

#### Adversarial design/spec (operator directive B)

**KEY DECISION 2 / Story 35.9** (greenlight + `epic-35-stories`):
- **Good:** names the AD-1 breach (consumer-side `last_artifact` deliverables synthesis); tickets a parity pin the dual-pin never covered; additive optional sections + no version bump argued under AD-4; sequence 35.9→35.8→35.7 keeps claim fence last.
- **Challenge — F-E35-0034 [P2] Stopgap shipped as `done`.** `page.py` still builds deliverables from `specialists[].last_artifact` (grep confirmed ~L656). Labeled + superseded-by-35.9 is better than silent, but **AD-1 is green-light law now**, not after 35.9. If 35.9 slips, 35.7 must not claim FR16/projection-sole-input without the stopgap called out in the scoped verdict.
- **Challenge — F-E35-0035 [P2] 35.9 blast radius.** Owns closed 35.1 contract + 35.2 assembler + 35.5 render + new fence — all `block_mode_trigger_paths` candidates. Regime T1 + serialize vs any parallel agent required. “No schema_version bump” needs the byte-pin/parity regenerate discipline explicit in DoD (present) — watch for silent golden edits without lockstep.
- **Challenge — F-E35-0036 [P2] Kanban sequencing lag on 35.8.** Row still `# strictly after 35.5` while 35.9 is inserted before 35.8. Stories/greenlight say 35.9→35.8; refresh 35.8 comment to `after 35.9` to prevent a premature legacy-retirement open.
- **Challenge — F-E35-0037 [P3]** Close commit `20cd0744` also banked this Grok shadow ledger (WP12 ambient). Prefer monitor-only or docs commits; not blocking.

**Render design (35.5) adversarial skim:** zone-scoped innerHTML + dual Python/JS renderers = classic drift risk; notes correctly park live JS preservation on 35.7 — keep that claim fence tight. De-scope ladder cuts look amendment-aligned; never-cut command blocks claimed — not re-proved this poll beyond notes.

**Verdict: 35.3 CLOSE CLAIMS HOLD; 35.5 CLOSE IS UNDURABLE ON TEST EVIDENCE (P1); 35.9 SPEC PLAUSIBLE BUT AD-1 STOPGAP + SEQ/REGIME RISKS OPEN; MONITOR CHARTER HARDENED.**

**Next poll:** ~15m. Expect: render-test bank commit and/or 35.9 in-progress substrate.

---

### SOP-E35-017 — 15m poll — 2026-07-11T20:30:11-04:00

**Scope reviewed:** HEAD still `20cd0744` = origin; Kanban; dirty 35.9 contract package; re-ran pytest claim audit; Claude waiting on 35.9 agent. Ledger-only.

**Delta:** No new commits. **F-E35-0031 still OPEN** — render test trio still `??` untracked.

**Claim re-audit (WP13):**
| Suite | Result |
|---|---|
| `tests/hud` tracked-only (close SHA surface) | **33 passed** |
| `tests/hud` disk incl. untracked render tests | **61 passed** |
| Closing claim “61 tests” durable on origin? | **NO** |

**35.9 progress (dirty, Kanban still `ready-for-dev`):**
- `operator_surface.py` + schema JSON + parity test modified (+458 lines) — `DecisionCardSection` / `ErrorMessageSection` / `DeliverablesSection` optional on projection; `schema_version` still `Literal["v1"]`.
- No assembler/render edits visible yet this poll.
- Agent mid “Verifying test_opera…” (~7m).

**Adversarial (WP14):**
- Additive optional sections match KEY DECISION 2 shape so far — good.
- **F-E35-0036 still OPEN** — 35.8 comment still `after 35.5`.
- **F-E35-0038 [P2] Epic Kanban header stale.** Still lists remaining as `(35.3/35.5/35.8/35.7)` though 35.3/35.5 are done and **35.9** is the live remaining contract story. Misleading for anyone reading only the epic row.
- **F-E35-0039 [P2] 35.9 Kanban lag.** Substrate clearly in-progress while row says `ready-for-dev` — flip when next bank lands.
- Watch: schema +290 without assembler populate yet = half-built contract; do not close 35.9 until emit + render delete-stopgap + parity pin all land together (story DoD).

**Verdict: P1 RENDER-TEST GAP UNFIXED; 35.9 CONTRACT EDIT IN FLIGHT; SEQ/KANBAN HYGIENE STILL LAGGING.**

**Next poll:** ~15m. Expect: 35.9 bank or render-test fix commit; Kanban flips.

---

### SOP-E35-018 — 15m poll — 2026-07-11T20:45:16-04:00

**Scope reviewed:** HEAD still `20cd0744`; 35.9 agent finished with completion notes; full dirty substrate (contract+assembler+render+tests); claim-audit via `.venv` pytest; Claude dispositioning the 2 “pre-existing” failures before review. Ledger-only.

**Commits:** none. Durability lag continues for entire 35.9 bank + still-untracked render suite.

---

#### Claim audit (WP13)

| Claim | Monitor tail | Verdict |
|---|---|---|
| 35.9 notes: `pytest tests/unit/models tests/contracts tests/hud tests/unit/marcus/orchestrator` → **981 passed, 1 skipped, 2 failed** | **981 passed, 1 skipped, 2 failed** (same two nodes) | **MATCH** (honest about fails) |
| Named fails: `test_30_1_zero_test_edits` + `test_transform_registry_lockstep` | Confirmed in summary | **MATCH** |
| AD-1: deliverables no longer from `last_artifact` synthesis | `page.py` `_ctx_completed` reads `projection.deliverables`; remaining `last_artifact` only on specialist chip (~L480) | **MATCH on dirty tree** (uncommitted) |
| New parity pin present | `tests/contracts/test_operator_surface_projection_demands_parity.py` exists (untracked) | **present** |
| Contracts+parity subset | `test_operator_surface_parity` + projection-demands → **111 passed**; assembler unit → **21 passed** earlier poll segment | supportive |
| **35.5 / F-E35-0031** still | tracked `tests/hud` → **33 passed**; disk → **65 passed** (was 61; +35.9 goldens) | **P1 STILL OPEN** — origin still lacks render tests |

**Adversarial note on the “2 pre-existing” framing:** transform-registry fail looks unrelated (agree). `test_30_1_zero_test_edits` is a **commit-range** pin that will fire because Epic 35 already modified tests on branch — driver terminal now says “one of them is genuinely mine to fix.” Treat notes’ “unrelated to 35.9” as **partially overstated** until disposition lands (allowlist vs fix vs documented waive). Do not let a red L1 hide inside “pre-existing.”

---

#### Design/spec adversarial (WP14)

- **F-E35-0034** progress: stopgap deletion present on dirty tree — closes only when committed + greppable on SHA.
- Health-budget “fold” = read missing field → default 60 (notes deviation #1). Honest, but **does not implement** the 35.5 SHOULD as a real projection field — ensure review does not claim the SHOULD fully folded.
- `pick_context`/`evidence` as pre-summarized `list[str]` (deviation #2): bounded display projection — acceptable if review agrees it is not state derivation; watch 35.7 claim language.
- Parity pin + single 35.7-dated waiver matches KEY DECISION 2 on paper — good fence if the demand→field map is not rubber-stamped (monitor did not re-diff EXPERIENCE.md bullets line-by-line this poll).
- **F-E35-0031 ∩ 35.9:** notes list `_render_fixtures` / goldens / units as 35.9 test files. Closing 35.9 **without** adding them would repeat the 35.5 evidence hole. Closing **with** them remediates 0031 — prefer that in the close commit.
- **F-E35-0036 / 0038 / 0039** still OPEN (35.8 “after 35.5”; epic header lists closed stories; 35.9 still `ready-for-dev` while completion notes exist).

**Driver:** 35.9 agent done (~21m); orchestrator checking the two failures before code-review.

**Verdict: 35.9 DEV-COMPLETE ON DISK — AGGREGATE COUNT VERIFIED; 2 REDS NEED HONEST DISPOSITION; RENDER-TEST P1 UNFIXED; AWAIT REVIEW + DURABLE CLOSE THAT BANKS TESTS.**

**Next poll:** ~15m. Expect: failure disposition, code-review, and/or close commit including render tests.

---
