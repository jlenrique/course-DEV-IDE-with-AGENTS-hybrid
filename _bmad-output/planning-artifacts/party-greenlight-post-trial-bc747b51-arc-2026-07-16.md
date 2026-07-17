# Party-Mode Green-Light Record — Post-Trial bc747b51 Arc (2026-07-16)

**Trigger:** Marcus-SPOC production trial `bc747b51-7009-4742-9f65-8de6abc29ca4` (corpus `tejal-apc-c1m1-p1-call`) error-paused at node 06 (`builder.gary.upstream-missing` — `§06 builder missing upstream contribution(s): cd`). Diagnosis (this session, Class S) proved the §06 error is a **misattributed downstream symptom**; seven findings were harvested. This record green-lights the story decomposition to fix them.

**Seats:** Winston (Architect), John (PM), Amelia (Dev), Murat (TEA), Sally (UX). **Verdict: UNANIMOUS 5/5 GREEN — no impasse** (Quinn→John escalation not triggered). Per the ratified party-consensus-=-approval policy (CLAUDE.md §Solo operator), consensus + orchestrator concurrence = approval; no redundant human hold.

---

## Root-cause diagnosis (frozen-run evidence)

The two "CD" defects are one root cause with a defense-in-depth companion:

- `node-enter 4.75` fired (`operator-surface.json`) — the walk **reached** the CD node.
- CD made **zero LLM calls** (`cost-report.json` lists only g0_enrichment, irene_pass1, texas, irene_refinement). Budget was fine ($0.34 / $10, under-budget) — **not** a budget/`max_specialist_calls` skip.
- Envelope contributions stop at `research_wiring @ 04.55`; nothing at 4.75/05/05B (`run.json`). Nodes 05/05B are **gates** (G2/G1.5), not specialist producers — **4.75 (cd) is the only specialist node between 04.55 and 06**.
- `allow_offline_cost_report=False` (persisted `runner`) → the dispatch guard reduces to pure `_has_live_openai()`.

**Mechanism:** the resume walk (`_continue_production_walk`) ran after the operator approved gates from a fresh PowerShell that had no `OPENAI_API_KEY` exported. `start_trial` (`app/marcus/cli/trial.py:390`) hard-requires the key; **`resume_trial_cli`/`recover_trial_cli` do not**. So `_has_live_openai()` was `False`, and the specialist-dispatch branch (`production_runner.py` ~4587–4627 resume / ~3595–3637 start) sets `graph_step_completed = True` **unconditionally** even when dispatch is skipped — CD silently no-opped, 05/05B (approved gates) passed, and 06 fail-louded on the first hard dep it checks (`cd`), three nodes downstream of the actual skip.

---

## Findings → story map (the decomposition)

| Finding | Story | Gate | Root notes |
|---|---|---|---|
| A — resume/recover lack the live-env preflight `start_trial` enforces | **41-1** | single | `trial.py`; not lockstep; ships first |
| B — specialist-dispatch silent-advance on skipped required node (both walks) | **41-2** | dual | `production_runner.py` **block_mode/lockstep**; RED-first vs `bc747b51` |
| C — HIL surfaces must be tabular + G — next_action must not preselect `--verb approve` | **42-1** | single | same trust surface (the decision card); replay vs real trial artifacts |
| D — HUD lifecycle must survive gate pause | **42-2** | single | app-code, hermetic |
| F.a — full ~16-toggle standing readout | **42-3** | dual | `operator_surface` assembler **block_mode/lockstep** |
| E — public read-only HUD at a stable URL, any browser | **42-4** | dual | own security/non-leak bar; Cloudflare Tunnel+Access / Tailscale fallback |
| F.b — pre-walk settings confirm-or-change gate | **42-5** | dual | new HIL pause; **depends on 42-3** |

**Two epics:**
- **Epic 41 — Resume-Walk Dispatch Integrity** (`epics-resume-walk-dispatch-integrity-2026-07-16.md`) — BLOCKING; unblocks any further paid walk past G1 on the composed selection. Sequence **41-1 → 41-2**.
- **Epic 42 — Operator Surface Next-Pass** (`epics-operator-surface-next-pass-2026-07-16.md`) — the honest Epic 35 successor. 42-1/42-2 independent; 42-3 → 42-5 sequenced; 42-4 parallel with its own security bar.

---

## Amendments folded (from the roundtable)

| Id | Seat | Substance | Landed in |
|---|---|---|---|
| **P-1** | Winston/Amelia/Murat | A and B are one *defect* but two *stories* — implement coherently, ship separately; B is lockstep + load-bearing and carries the RED-first bar, A is an 8-line guardrail | Epic 41 sequence; 41-1/41-2 split |
| **P-2 (invariant)** | Winston | 41-2 spec sentence: *"In a production run (`allow_offline_cost_report=False`), a specialist node that is entered and is not already-carrying MUST emit a contribution or fail loud at that node. Silent advance is forbidden."* Must land in **both** walk copies (two-walk trap) | 41-2 AC-1/AC-2 + Scope Fence |
| **P-3** | Murat | 41-2 acceptance replays a reconstructed keyless-resume walk against the frozen `bc747b51` run and asserts the fail-loud fires at 4.75 (`dispatch.live-unavailable`), NOT `builder.gary.upstream-missing` at 06 | 41-2 AC-3 |
| **P-4** | Sally/Amelia | C + G are the same trust violation on the same object (the decision card) — merge into 42-1; a readable table that still ships `approve` pre-filled is illegible-and-leading | 42-1 |
| **P-5** | Murat | 42-1 acceptance replays tables against **this trial's real** `g0-enrichment.json` + `operator-surface.json` (64-component enrichment), not toy fixtures | 42-1 AC + evidence bar |
| **P-6** | Winston/Murat | E (public URL) is a different failure domain (infra + identity + secrets) — **split from D**; D is a hermetic app-code lifecycle fix that must not be held hostage to tunnel plumbing; E carries an explicit non-leak AC (no resume nonces/digests/source text/credentials cross the tunnel) | 42-2 / 42-4 split |
| **P-7** | Amelia/John | F splits into 42-3 (standing readout, deterministic/lockstep, shape-pinnable offline) and 42-5 (pre-walk confirm gate, a real HIL pause needing a walk test); bound by **sequence** (42-5 depends on 42-3), not merged | Epic 42; 42-3/42-5 |
| **P-8** | Murat | Dev posture: **fresh-Claude-dev-agent**, per-story fresh context (not the Codex hand-off — reserved for formal heaviest-substrate `bmad-dev-story`). Lockstep stories (41-2, 42-3) get the pipeline-manifest-regime T1 read + Cora block-mode hook | Both epics §Dev posture |

---

## Governance

- **Lockstep:** `app/marcus/orchestrator/production_runner.py` (41-2) and `app/marcus/orchestrator/operator_surface_assembler.py` + `app/models/runtime/operator_surface.py` (42-3, and 42-2/42-5 read/adjacent) are `block_mode_trigger_paths`. Those stories run under the pipeline-manifest-regime; Cora's block-mode hook gates. `trial.py`, `app/hud/**`, `app/notify/**` — 42-2/42-4 touch `app/hud/**` + `app/notify/**` which ARE trigger globs → lockstep applies there too.
- **Guardrail (SPOC-is-the-goal):** every story fixes a genuine production-runtime/operator-surface correctness or usability defect that improves the SPOC product. None is shaped to "make the concierge run pass." A resume that silently stops producing content, and a HIL surface the operator can't read or reach, are real product bugs.
- **Deferred-inventory:** the six operator-requirement rows (`hil-operator-surfaces-must-be-tabular`, `hud-lifecycle-survives-gate-pause`, `hud-stable-public-live-url`, `hud-pre-run-settings-confirmation-surface`, `next-action-must-not-preselect-approve`, `cd-contribution-missing-before-06-builder`) are now **FILED as the stories above** — annotate each row with its story id (governance §3: the inventory is SSOT for what's queued).

## Next

Draft the 8 story specs to `ready-for-dev` (this session), open `bmad-dev-story` on **41-1** first (BLOCKING, unblocks resuming trials), then 41-2. Epic 42 stories dispatch after (or in parallel where DAG-independent).
