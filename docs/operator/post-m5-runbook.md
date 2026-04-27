# Operator Post-M5 Runbook

**Status:** Re-authored 2026-04-26 — M5 verdict is now decided. Active path is **SHIP-CONDITIONAL** (see "Active Path" section below). Other path sections remain as reference for the demotion case + future migrations.

**Purpose:** Per-verdict-path operational guide. The 5a.5 6-agent party-mode produced one of 5 consensus-level verdicts; this runbook tells you what to do for each, with the active path highlighted.

---

## ACTIVE PATH (as of 2026-04-26): SHIP-CONDITIONAL

**Operator-accepted verdict:** SHIP-CONDITIONAL with named 7-day window through **2026-05-03**.
**Migration-master-status:** `shipped` (with trailing comment naming window expiry).
**Source-of-truth artifacts:**
- `_bmad-output/implementation-artifacts/m5-decision.md` — 6-agent verbatim record + accepted window text.
- `_bmad-output/upstream-state.md` — frozen-reference posture + 4 open conditions + demotion rule.
- `_bmad-output/planning-artifacts/deferred-inventory.md` — `5a-5-m5-conditional-window-2026-05-03` entry.

### What you do during the conditional window

The 4 open conditions, each with its closure path:

1. **M2 Wondercraft live-artifact** — operator-window ceremony (~10-15 min + render). Run Wanda's `create_scripted_podcast` capability live ($5 ceiling, $1-2 simple-fallback). Artifact lands at `tests/fixtures/specialists/wanda/live_artifacts/2026-04-26/<sha256>.mp3`. Paste "Operator-Window Addendum" into `_bmad-output/implementation-artifacts/slab-2c-m2-acceptance-verdict.md`. Flip `2c-3-m2-verdict-conditional-on-2c-2-live-artifact` to RESOLVED. See [`conditional-gate-addendum-playbook.md`](conditional-gate-addendum-playbook.md) for the addendum template.

2. **M3 Texas live-retrieval** — operator-window ceremony (~5-10 min). Run Texas retrieval flow against a real source authority (per `skills/bmad-agent-texas/references/retrieval-contract.md` provider directory). Capture evidence; paste addendum to M3 verdict artifact. Flip `2a.4-followon-ac-b-op-live-retrieval` to RESOLVED.

3. **5a.2 production clone-launch equivalence** — closes by running ONE real trial against live OpenAI through the migrated runtime using `python -m app.marcus.cli trial start --preset production --input <corpus-path>`. The run must register under `state/config/runs/<trial-id>/`, upload or expose LangSmith trace metadata when configured, and write a cost report.

4. **Plausible-Token Substrate Contamination live verification** — code remediation is complete. Closes when the operator runs `pytest tests/live/test_openai_cascade_tiers_smoke.py -m live -q` with `OPENAI_API_KEY` set and all three real cascade IDs (`gpt-5`, `gpt-5-mini`, `gpt-5-nano`) return non-zero token usage.

Resolved provenance: **`slab-3-m5-dispatch-registry-swap`** closed on 2026-04-26. Both `state/config/dispatch-registry.yaml` and `runtime/graphs/v42/dispatch-registry-snapshot.yaml` are `_status: production`.

### Demotion rule (if window lapses)

If on **2026-05-03** any of conditions 1-4 remain unresolved AND the operator does not extend the window via explicit ratification:
- `migration-master-status` flips from `shipped` to `iterate-pending`.
- Convene short 3-agent party-mode (Winston + Murat + Amelia) to ratify demotion + name remediation path.
- Continue with **Path D — ITERATE** below.

### Pre-trial preparation work

Codex pre-trial batches maximize readiness before the operator window:
- **Batch 1 tail / post-remediation batch** — live-API smoke scaffolds, doc actualization, ready-for-trial harness, production-clone launcher, and final code review.
- **Batch 2** (`codex-handoff-pre-trial-defensibility-batch-dev.md`) — FR traceability + NFR assessment + test-quality audit (defensibility evidence, no code changes).
- **Batch 3** (`codex-handoff-pre-trial-adhoc-and-hud-batch-dev.md`) — ad-hoc CLI subcommand + HUD modernization for migrated runtime.

After all three batches close: operator-presence work is M2 ceremony + M3 ceremony + one real trial. That session, properly executed, closes the conditional window with verdict promotion to unconditional SHIP.

---

## Reference: per-verdict path documentation

---

## At-a-glance: M5 verdicts → operational paths

| Verdict | Operational consequence | Migration-master-status enum |
|---|---|---|
| **SHIP** | Forward-port playbook activates per FR61; primary marked frozen-reference; Slab 5b polish opens | `shipped` |
| **SHIP-WITH-RIDERS** | SHIP path + named riders tracked at `m5-ship-riders.md` for immediate-post-ship work | `shipped` |
| **SHIP-CONDITIONAL** | SHIP path conditional on named window for inherited M2/M3/M4 conditional resolution; window-watch active | `shipped` (with trailing-comment naming the window) |
| **ITERATE** | Remediation stories open as Slab 5a extensions; M5 target date renamed; Slab 5b defers | `iterate-pending` |
| **ROLLBACK** | FR62 rollback plan executes; migration clone archived; primary repo continues production | `rolled-back` |

---

## Path A — SHIP

**Per epic 5a.5 + FR60/FR61:**

1. **Update `migration-master-status` in sprint-status.yaml** to `shipped`
2. **Mark primary repo as frozen-reference** at `_bmad-output/upstream-state.md` with the snapshot SHA (`3ed7c56` per current severance) + the M5 ship date
3. **Backport channel REMAINS CLOSED per FR60** — do NOT open backport channel; the migration's LangChain/LangGraph re-platform IS the replacement
4. **Activate forward-port playbook per FR61:**
   - Inventory primary's post-`3ed7c56` commits (since 2026-04-24 severance)
   - Categorize each: `class-a-no-port` (replaced by migration architecture) / `class-b-port-needed` (genuine forward-port required) / `class-c-defer` (operator decides later)
   - Author per-capability forward-port stories per `docs/dev-guide/langgraph-migration-guide.md §8 reconciliation checklist`
   - Track at `_bmad-output/implementation-artifacts/forward-port-status.yaml` (NEW; created at first SHIP verdict)
5. **Slab 5b polish stories may open** per PRD MVP cuttable table:
   - 5b.1 Fork UX Polish (CLI → IDE-integrated MCP)
   - 5b.2 Economics Dashboard
   - 5b.3 Migration Guide Final
   - 5b.4 Generator Polish + Second-Specialist Generalization Test
6. **Operator-facing guides re-anchored:**
   - `docs/user-guide.md` re-authored against migration-shipped surfaces (Marcus orchestration UX; transport choice; DecisionCard verdict flow)
   - `docs/admin-guide.md` updated for production deployment (Postgres scale config; MCP server hardening; LangSmith production tracing)
7. **Tag the release:**
   ```bash
   git tag -a v0.1.0-migration-shipped -m "M5 SHIP verdict; migration complete"
   git push origin v0.1.0-migration-shipped
   ```
8. **Slab 6+ planning** (post-MVP roadmap) — operator's call: production hardening / new course-content domains / multi-operator support / etc.

---

## Path B — SHIP-WITH-RIDERS

Same as SHIP path, PLUS:

1. **Author `_bmad-output/implementation-artifacts/m5-ship-riders.md`** with each named rider:
   - Rider provenance (which agent named it; which finding it addresses)
   - Rider scope (what changes; what doesn't)
   - Rider window (target completion date)
   - Rider-resolution sign-off (operator + party-mode at completion)
2. **Track riders in sprint-status.yaml** as `migration-5a-5-rider-<n>-<short-name>: in-progress` rows under a NEW `# RIDERS` block

Riders are typically narrow scope (1-2 days each). Common rider categories from prior precedent:
- Documentation-prose tweaks
- Single-test additions
- Lint cleanup remaining after auto-fix sweep
- Operator-facing string improvements

---

## Path C — SHIP-CONDITIONAL

Same as SHIP path, PLUS:

1. **Named window MUST be specified in m5-decision.md verdict text:**
   - Example: `Consensus verdict: SHIP-CONDITIONAL pending M2 operator-window addendum within 7 days; if window lapses, ship-state demotes to ITERATE.`
2. **Auto-file `5a-5-m5-conditional-window-<expiry-date>` deferred-inventory entry** with reactivation gate "operator addendum landed" OR "window lapsed → demote to ITERATE"
3. **Operator window-watch responsibility:**
   - Daily check: has the conditional resolved?
   - At window expiry: convene SHORT party-mode (3-agent: Winston + Murat + Amelia) to ratify ship-state stays SHIP OR demotes to ITERATE
4. **`migration-master-status: shipped`** with trailing comment naming the window expiry + condition

---

## Path D — ITERATE

**Per epic 5a.5 ITERATE clause:**

1. **Update `migration-master-status` in sprint-status.yaml** to `iterate-pending`
2. **Operator names ≥1 specific finding** in m5-decision.md §"Iterate Findings"
3. **Per-finding remediation stories file in sprint-status as Slab 5a extensions:**
   - `migration-5a-5-iter-1-<short-name>: ready-for-dev`
   - `migration-5a-5-iter-2-<short-name>: ready-for-dev`
   - ...
4. **M5 target date renamed** in PRD §Acceptance Criteria + `next-session-start-here.md`
5. **Slab 5b polish stories DEFER** until ship verdict re-converges
6. **At remediation completion:** re-convene 5a.5 party-mode for re-vote; verdict path may converge to SHIP / SHIP-WITH-RIDERS / etc.

**Common iterate triggers from precedent:**
- Parity score below threshold at 5a.2 (head-to-head <60% structural-match)
- Cost reduction below ≥50% bar at 5a.3 (PRD §Cost Projection auto-defaults to Revise on <50%)
- Cache-hit-rate median <80% at 5a.3 (triggers prefix-stability audit; remediation needed)
- Invariant violation at 5a.4 matrix (any of 15 invariants flagged VIOLATED)
- Operator-acceptance reservation at 5a.5 vote

---

## Path E — ROLLBACK

**Per epic 5a.5 ROLLBACK clause + FR62:**

1. **Update `migration-master-status` in sprint-status.yaml** to `rolled-back`
2. **Operator names rollback reason** in m5-decision.md §"Rollback Rationale"
3. **Activate FR62 rollback plan:**
   - Migration clone branch (`dev/langchain-langgraph-foundation`) is **archived** (NOT deleted; preserved for forensic review)
   - Tag the archive: `git tag -a v0.1.0-migration-rolled-back -m "M5 ROLLBACK verdict per <reason>"`
   - Primary repo (upstream/master) continues production
   - Remove migration-shipped expectations from operator-facing surfaces
4. **Capture rollback learnings in retrospective:**
   - `_bmad-output/implementation-artifacts/migration-rollback-retrospective.md`
   - Format: 4 §-headers (Pre-Audit Bundle / Rollback Triggers / Slab-by-Slab Lessons / Future-Migration Recommendations)
   - 6-agent party-mode lessons-learned round
5. **Restore primary's session-protocol** as the operator's working environment:
   - Re-activate primary's `bmad-session-protocol-session-START.md` flows
   - Re-orient operator to primary's prompt-pack v4.x workflow

**Common rollback triggers (rare; reserved for fundamental misalignment):**
- Cost reduction <30% at 5a.3 (PRD §Cost Projection auto-defaults to Revise or Rollback)
- Invariant violation at 5a.4 that cannot be remediated within reasonable scope
- Operator strategic decision (LangChain/LangGraph platform no longer aligns with org direction)

**Rollback is NOT failure** — it's a disciplined exit per FR62. The migration's planning + execution captured as institutional learning regardless of ship outcome.

---

## Standing post-M5 housekeeping (all verdict paths)

1. **`next-session-start-here.md` final update** per CLAUDE.md §closeout hygiene:
   - Active-slab line transitions per verdict
   - Deferred-inventory status line reflects final post-5a.5 counts
   - M5 milestone status reflects verdict
   - Hot-start guidance for next operator session
2. **15-invariant audit matrix locked** at `_bmad-output/implementation-artifacts/15-invariant-audit-matrix.md` per 5a.4 close
3. **Anti-patterns catalog migration-complete annotation** per 5a.5 AC-E migration-final
4. **TEMPLATE doc migration-complete annotation** per 5a.5 AC-F (specialist-migration-template.md gains close-of-migration note)
5. **Schema-changelog roll-up** at `SCHEMA_CHANGELOG.md` consolidated index of all migration-shipped Pydantic v2 models
6. **Sprint-status.yaml** archived snapshot at `_bmad-output/implementation-artifacts/sprint-status-m5-snapshot-<date>.yaml`

---

## See also

- [`docs/operator/trial-run-runbook.md`](trial-run-runbook.md) — first-trial step-by-step
- [`docs/operator/conditional-gate-addendum-playbook.md`](conditional-gate-addendum-playbook.md) — pre-M5 conditional-gate operator windows
- [`_bmad-output/planning-artifacts/prd-langchain-langgraph-migration.md`](../../_bmad-output/planning-artifacts/prd-langchain-langgraph-migration.md) §FR60 / §FR61 / §FR62
- Story spec: [`_bmad-output/implementation-artifacts/migration-5a-5-m5-ship-decision-and-slab-close.md`](../../_bmad-output/implementation-artifacts/migration-5a-5-m5-ship-decision-and-slab-close.md)
