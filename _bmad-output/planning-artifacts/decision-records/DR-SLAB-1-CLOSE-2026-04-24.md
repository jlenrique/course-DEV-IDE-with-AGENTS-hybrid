# Decision Record — Slab 1 Close Ceremony

**Record type:** Formal decision record matching D1–D13 architecture-of-record pattern.
**Ratified:** 2026-04-24 via party-mode round 3 (5/5 GOLDEN-WITH-CAVEATS).
**Scope:** Slab 1 closure decisions not captured in D1–D13 at architecture-authoring time.
**Authority:** Operator (Juanl) + standing party-mode team (Winston / Amelia / Murat / Paige / Mary).
**Status:** Binding governance.

---

## DR-1: Slab 1 ratified as GOLDEN foundation

**Decision:** Slab 1 substrate (Stories 1.1a through 1.7, commits `a905de0` → `9526a6c`) is ratified as the immutable golden foundation upon which all Slab 2+ work builds.

**Binding consequence — "spec yields to code on conflict":** when any Slab 2+ story spec disagrees with Slab 1 shipped code (state-model paths, exception class names, import pathways, test-tree conventions, scaffold contract shapes, or any other substrate claim), the story spec gets amended to match code. Code is NOT changed to satisfy speculative spec assumptions.

**Exception:** a genuine defect discovered in Slab 1 code opens a named bug-fix story with its own dev-agent execution + G5/G6 party-mode review + re-ratification of any affected substrate invariant. See DR-4 for defect-rollback protocol (Slab-2-opening ceremony hardening item).

**Ratification vote (2026-04-24 party-mode round 3):**
- 🏗️ Winston — GOLDEN-WITH-CAVEATS
- 💻 Amelia — GOLDEN-WITH-CAVEATS
- 🧪 Murat — GOLDEN-WITH-CAVEATS
- 📚 Paige — GOLDEN-WITH-CAVEATS
- 📊 Mary — GOLDEN-WITH-CAVEATS
- Operator (Juanl) — ACCEPTED

**Rationale:** per-story G5+G6 reviews completed across all 10 Slab-1 stories; operator M1 ACCEPT-WITH-GAP ratified 2026-04-24; upstream severed at commit `835e650` leaving hybrid as sole APP-development source of truth. Without formal slab-wide ratification, spec-vs-code conflicts would require case-by-case party-mode escalation, silently increasing substrate-assumption drift risk across 46 remaining migration stories. This record closes that gap.

---

## DR-2: Audra and Cora dissolution

**Decision:** `skills/bmad-agent-audra/` and `skills/bmad-agent-cora/` are **DISSOLVED** as APP-runtime specialists on the hybrid migration branch. Neither migrates as a LangGraph runtime node in Slab 2+. Their skill directories are retained as historical-archive artifacts on hybrid; no new invocation pathways will be added post-severance.

**Replacement surface:**
- **Audra's code-invariant function** (L1/L2 coherence evidence under `reports/dev-coherence/<ts>/`) is fully absorbed by the LangGraph CI stack shipped in Slab 1:
  - `import-linter` 3 contracts (C1 lane-isolation + C2 gates-no-scheduler + C3 bridge-module-only) kept at every commit
  - Scaffold-conformance framework (`tests/integration/scaffold_conformance/`) shipped at Story 1.7
  - Pydantic v2 shape-pin tests across 8 state models (Story 1.2)
  - LangSmith tracing wired in Story 1.1c
  - Existing `scripts/utilities/check_learning_event_lockstep.py` + `scripts/utilities/check_pipeline_manifest_lockstep.py` from pre-migration substrate
- **Audra's session-ritual function** (hot-start triage + deferred-findings ledger carry-forward) is covered by existing BMAD `bmad-session-protocol-session-START.md` + `bmad-session-protocol-session-WRAPUP.md` + `next-session-start-here.md` hot-start + `CLAUDE.md §Deferred inventory governance`.
- **Cora's `/harmonize` + session-triage function** remains scoped to **Slab 4 Epic E4** (*"Lockstep + Gates + Cora"*) as a CLI wrapper + optional session hook, **NOT** as a LangGraph runtime node.
- **Dev-coherence report generator** (hybrid-native Audra replacement producing new `reports/dev-coherence/<ts>/` entries) filed as ~1–2 pt Slab 4 deferred follow-on per [`_bmad-output/planning-artifacts/deferred-inventory.md` §Named-But-Not-Filed Follow-Ons](../deferred-inventory.md).

**Out of scope for this decision:** primary-repo `skills/bmad-agent-audra/` + `skills/bmad-agent-cora/` remain as operator-initiated agents on primary if the operator ever returns to primary-repo APP work. Post-severance, primary is effectively deprecated for APP development per DR-1; but this record does not retire their primary-repo presence.

**Roster reconciliation impact:** the named Epic 2b roster drops from 14 → 12 migratable specialists (9 Category A+B + 5 Category C − 2 Category D dissolved). Detail at [`slab-2-roster-reconciliation.md §Category D`](../slab-2-roster-reconciliation.md).

**Ratification:** operator (Juanl) ratified 2026-04-24 during Slab-2 roster reconciliation authoring. Party-mode round 3 Mary-caveat-H4 explicitly names this decision as requiring a stamped DECISION-RECORD artifact matching D1–D13; THIS document satisfies that caveat.

**Reversal protocol:** post-M5 re-resurrection of Audra or Cora as LangGraph runtime nodes requires: (a) fresh FR/NFR coverage claim + architecture decision amendment; (b) party-mode consensus with full standing team; (c) version bump of this DR; (d) explicit operator sign-off. Not a dev-agent-authority path.

**Safeguard (landed at 2a.1 per round-2 rider Mary-R11 / round-3 SP-code):** Story 2a.1's `bmad-create-specialist` generator ships a **Category D denylist** (`skills/bmad-agent-audra/` + `skills/bmad-agent-cora/`) with a named refusal error message pointing back to this DR. Prevents accidental re-resurrection via the generator path.

---

## DR-3: Post-M5 greenfield specialists deferral

**Decision:** seven named specialists from the Epic 2b roster — **Mike, Eli, Enrique, Mira, Sally, Kim, Paige-as-runtime-specialist-if-scoped** — are **DEFERRED** to a post-M5 greenfield mini-epic. They do NOT migrate in Slab 2+. Their empty sidecar stubs under `_bmad/memory/<name>-sidecar/` (where present) are retained as historical scaffolding.

**Rationale:** codebase study at 2026-04-24 confirmed these seven names have NO skill directory on disk — they are roadmap placeholders reserved at planning time but never implemented. Migrating an empty placeholder produces an empty LangGraph node with no domain content. Generating them post-M5 via the `bmad-create-specialist` generator (landed at Story 2a.1) directly on the migrated platform is strictly simpler: the operator picks the right moment (operational need) and the generator produces a scaffold-conformant node from scratch.

**Reactivation trigger:** operational need per role materializes + generator proven at M2 close. File one story per greenfield specialist as need arises.

**Ratification:** operator (Juanl) ratified 2026-04-24 during Slab-2 roster reconciliation authoring. Filed to [`_bmad-output/planning-artifacts/deferred-inventory.md` §Backlog Epics](../deferred-inventory.md) as "Post-M5 Greenfield Specialists" epic.

---

## DR-4 (FORWARD): Defect-in-Slab-1-code change-approval protocol — TO BE RATIFIED AT SLAB-2 OPENING

**Status:** Named but not yet ratified. Party-mode round 3 Mary-caveat-H1 raised this governance gap. Text below is the proposed shape; ratification occurs at Slab 2 opening ceremony before first dev-story.

**Proposed rule:** if a defect is discovered in Slab-1-shipped code during Slab 2+ dev-story execution or G5/G6 review, the fix requires:

1. Named defect-story (e.g., `migration-fix-1-X-Y-<description>`) with full dev-agent T1–T9 execution
2. Full G5 party-mode review + G6 layered code-review pass
3. Re-ratification of any architecture decision (D1–D13) whose substrate claim is affected
4. Update to [DR-1](#dr-1-slab-1-ratified-as-golden-foundation) "spec yields to code" rule IF the affected substrate was load-bearing for downstream Slab 2+ specs (may flip spec-yields-to-code direction for affected surface)
5. Deferred-inventory entry noting any Slab 2+ story whose T1 readiness block references the fixed substrate (requires re-verification at those stories)

**NOT covered by this protocol:** cosmetic polish (docstring improvements, ruff auto-fixes, comment clarifications) — those land via normal story-cycle hygiene without DR amendment.

---

## DR-5 (FORWARD): Severance-reversal protocol teeth — TO BE RATIFIED BEFORE M5

**Status:** Named but not yet ratified. Party-mode round 3 Mary-caveat-H5 raised this as the highest-priority governance gap. Text below is the proposed shape; ratification occurs before M5 (Slab 5 acceptance).

**Proposed rule:** pulling any content from `upstream/master` into hybrid after commit `835e650` (severance cutoff) requires:

1. Party-mode consensus with full standing team (5+ voices)
2. Version bump of [`docs/dev-guide/langgraph-migration-guide.md §8.1`](../../docs/dev-guide/langgraph-migration-guide.md#81-upstream-severance-slab-2) documenting the exception
3. Explicit operator sign-off
4. Audit entry appended to [`_bmad-output/implementation-artifacts/upstream-severance-log.md`](../implementation-artifacts/upstream-severance-log.md) naming: commits pulled, scope, rationale, affected substrate

**Enforcement mechanism (to be decided at ratification):**
- Option A: pre-commit hook scanning for commits whose parent chain includes `upstream/master` commits post-severance
- Option B: GitHub branch protection rule (if applicable)
- Option C: CLAUDE.md line making the reversal protocol explicit + relying on dev-agent discipline

**Why forward-ratified:** today the severance is declared (prose in migration-guide §8.1) but not enforced. A tired operator at 11pm could cherry-pick a "quick fix" and silently undo severance discipline. The enforcement teeth need to land before M5 when migration work is complete enough that a primary-repo critical fix becomes tempting.

---

## Hardening backlog (captured from party-mode round 3; not decisions per se — tracking artifacts)

From round 3 consensus (22 items total; most are not decisions but hardening tasks). See [`_bmad-output/implementation-artifacts/round-3-hardening-backlog.md`](../implementation-artifacts/round-3-hardening-backlog.md) — filed at Commit B of 2026-04-24 session.

---

## Amendment history

- **2026-04-24 — Initial publication.** DR-1 + DR-2 + DR-3 ratified. DR-4 + DR-5 named as forward-ratified.
