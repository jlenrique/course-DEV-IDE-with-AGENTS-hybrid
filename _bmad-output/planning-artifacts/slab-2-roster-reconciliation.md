# Slab 2 Roster Reconciliation — Named vs. Actual

**Authored:** 2026-04-24 at session START (pre-Slab-2 open).
**Reason:** direct codebase study revealed that the Slab 2 roster named in
[`epics-langchain-langgraph-migration.md` §Epic 2b](epics-langchain-langgraph-migration.md)
enumerates 14 specialists by name, but several of those names are roadmap
placeholders (empty sidecar stubs only, no skill directory, no prompts, no
code). You cannot migrate what does not exist.

This artifact is the ground-truth reconciliation: **named roster → actual
migratable count.** Each Slab 2b story authoring reads this file to confirm
that its target specialist is in the migratable list.

**Governance:** per-entry classification is frozen at Slab 2 open. If a
specialist transitions between categories during Slab 2 (e.g., operator
fills a roadmap-only shell with a real prompt on primary), an entry is
appended to §Reclassification Log below; the original row stays historical.

---

## Category A — Fully mature, migration-ready

Skill directory with substantial prompt content + scripts + references.
Expected 2b.N work: read the skill dir at pinned upstream SHA, author the
9-node scaffold body under `app/specialists/<name>/`, wire the model cascade,
create the hybrid sanctum directory, close.

| # | Role name | Skill dir | Size | Notes |
|---|---|---|---|---|
| 1 | Gary (Gamma slides) | [`skills/bmad-agent-gamma/`](../../skills/bmad-agent-gamma/) | 108 KB / 13 files | Template for 2b.N per Epic 2b spec |
| 2 | Vera (fidelity assessor) | [`skills/bmad-agent-fidelity-assessor/`](../../skills/bmad-agent-fidelity-assessor/) | 72 KB / 7 files | Prompt-heavy; G0–G5 gates |
| 3 | Quinn-R (quality reviewer) | [`skills/bmad-agent-quality-reviewer/`](../../skills/bmad-agent-quality-reviewer/) | 48 KB / 6 files | Two-pass validation (pre-composition / post-composition) |
| 4 | Desmond (Descript specialist) | [`skills/bmad-agent-desmond/`](../../skills/bmad-agent-desmond/) | 565 KB / 19 files | Reference-heavy (9 references + 4 scripts); memory-backed |
| 5 | Tracy (research intent shaper) | [`skills/bmad_agent_tracy/`](../../skills/bmad_agent_tracy/) | — / — | Snake-case path (post-Epic-28 sanctum bundle); 3-posture contract |
| 6 | Dan / CD (creative director) | [`skills/bmad-agent-cd/`](../../skills/bmad-agent-cd/) | 61 KB / 13 files | 2026-04-14 addition; creative framing + parameter orchestration |
| 7 | Kira (Kling video) | [`skills/bmad-agent-kling/`](../../skills/bmad-agent-kling/) | 48 KB / 7 files | Prompt-heavy (197L SKILL.md); script-light |
| 8 | ElevenLabs (voice + audio) | [`skills/bmad-agent-elevenlabs/`](../../skills/bmad-agent-elevenlabs/) | 19 KB / 6 files | Prompt-heavy; owns all audio per composition architecture |
| 9 | **Wondercraft (podcast production)** — absorbed 2026-04-24 | [`skills/bmad-agent-wondercraft/`](../../skills/bmad-agent-wondercraft/) | ~19+ files (BOND/CAPABILITIES/CREED/INDEX/MEMORY/PERSONA templates + 6 capability references + SKILL.md + init-sanctum.py) | **New on hybrid as of severance absorption.** Was planned in Epic 2c as "from-scratch via `bmad-create-specialist` to prove generator + <1 dev-day metric." Now that Wondercraft arrived on primary as a real first-breath scaffold, Slab 2c.1's scope needs a decision at Slab 2 kickoff — see §Wondercraft Decision below. |

**Category A + B total: 9 specialists** (8 original + Wondercraft absorbed).

### Wondercraft Decision (flagged for Slab 2 kickoff party-mode)

Wondercraft now exists on hybrid as a real first-breath scaffold with 6 capability references (audio-assembly-handoff / audio-summary-produce / chapter-markers-emit / music-bed-apply / podcast-dialogue-produce / podcast-episode-produce). Epic 2c was originally designed around regenerating Wondercraft from scratch via `bmad-create-specialist` to validate the generator's "<1 dev-day from open to first real artifact" claim. Two options:

- **Path A — Migrate as 2b.N.** Treat Wondercraft as a Category-A/B specialist. Node body + model cascade + scaffold-conformance. Generator validation in Slab 2c shifts to a different specialist (one of the Category E roadmap names when it becomes needed, or a synthetic test specialist).
- **Path B — Keep 2c.1 from-scratch.** Absorb Wondercraft as reference-only; Slab 2c.1 still generates Wondercraft from scratch via the generator and compares the generated output against the absorbed reference (acts as an end-to-end validation rather than pure from-scratch).

**Default pending kickoff consensus:** Path A (simplest; minimal work duplication). Revisit at Slab 2 kickoff party-mode.

### Open question — Irene placement

Irene lives at [`skills/bmad-agent-content-creator/`](../../skills/bmad-agent-content-creator/)
(1017 KB / 83 files — heaviest non-orchestrator specialist). She is tightly
coupled to Marcus via the Lesson Planner MVP (Epics 28–32 on the primary
roster, which on hybrid sits inside Slab 3 Marcus orchestration).

**Default placement (pending Slab 2 kickoff consensus):** Slab 2 migrates
Irene's *node body* (Pass 1 + Pass 2 prompts, narration schema consumer,
fidelity-assessor coordinator). Slab 3 handles the Marcus-side dispatch
rewiring that makes Irene fully integrated with Lesson Planner MVP flows.

If Slab 2 kickoff party-mode flags the coupling as too tight for a
node-only migration, Irene moves to Slab 3 alongside Marcus. This is
acceptable — Irene-dependent downstream specialists in Slab 2 (Gary,
Kira, ElevenLabs) can migrate against the primary-repo Irene contract
and re-integrate at Slab 3 close.

---

## Category C — Tier-4 manual-tool thin nodes

Specialists that wrap manual-only tools (Tier 4 per [`tool-access-matrix.md`](../../resources/tool-inventory/tool-access-matrix.md))
or very-limited-API tools (Tier 3). No meaningful API dispatch; the node's
job is to generate operator-step instructions, not invoke a service. Migration
is **fast** — mostly envelope + `return SpecialistReturn(...operator_steps=...)`
with minimal prompt surface.

| # | Role name | Skill dir | Size | Migration shape |
|---|---|---|---|---|
| 9 | CourseArc (LMS authoring) | [`skills/bmad-agent-coursearc/`](../../skills/bmad-agent-coursearc/) | 36 KB / 7 files | Operator-instructions node; no API |
| 10 | Vyond (animation) | [`skills/bmad-agent-vyond/`](../../skills/bmad-agent-vyond/) | 7 KB / 4 files | Operator-instructions node |
| 11 | Articulate (Storyline/Rise) | [`skills/bmad-agent-articulate/`](../../skills/bmad-agent-articulate/) | 14 KB / 5 files | Operator-instructions node |
| 12 | Midjourney (image generation) | [`skills/bmad-agent-midjourney/`](../../skills/bmad-agent-midjourney/) | 10 KB / 4 files | Limited-API stub; operator-instructions dominant |
| 13 | Canva (design) | [`skills/bmad-agent-canva/`](../../skills/bmad-agent-canva/) | 4 KB / 1 file | Pure shell per 2026-03-26 capability audit (Canva API cannot edit elements). Migration is an envelope + "guidance only" return. |

**Category C total: 5 specialists.**

---

## Category D — Dissolved (replaced by LangGraph CI + BMAD session protocols)

Per 2026-04-24 operator ratification: these two specialists' code-invariant
functions are fully covered by the LangGraph + LangGraph CI stack already
landed in Slab 1 (import-linter 3 contracts, scaffold-conformance framework,
Pydantic shape-pin tests, LangSmith tracing, checkpoint retention health).
Their session-ritual governance functions are covered by existing BMAD
session-START / session-WRAPUP protocols and CLI tooling — neither becomes
a LangGraph runtime node.

| # | Role name | Skill dir | Replacement |
|---|---|---|---|
| 14 | Audra (audit / coherence evidence) | [`skills/bmad-agent-audra/`](../../skills/bmad-agent-audra/) | Fully absorbed by LangGraph CI artifacts: import-linter output + scaffold-conformance pytest reports + LangSmith trace replay + [`deferred-inventory.md`](deferred-inventory.md) audit trail + existing `reports/dev-coherence/<ts>/` session-protocol archive pattern. **No migration; skill dir becomes an archival remnant.** |
| 15 | Cora (harmonize / session triage) | [`skills/bmad-agent-cora/`](../../skills/bmad-agent-cora/) | Code-invariant side absorbed by LangGraph CI (same stack as Audra). Session-triage + `/harmonize` CLI wrapper is already scoped in **Slab 4 Epic E4** "Lockstep + Gates + Cora" as a CLI tool + hook, **not a LangGraph runtime node**. Category D classification just confirms she is not a Slab 2 dispatch-path specialist. |

**Rationale (operator directive 2026-04-24):** LangGraph CI verifies production-pipeline structural invariants. BMAD session protocols + CLI tools cover cross-session governance. Neither needs a conversational-agent surface on the hybrid runtime. Retain the skill dirs as historical artifacts; do not port.

---

## Category E — Roadmap-only (deferred to post-M5 greenfield)

Named in the Epic 2b roster (*"Mike, Dan, Eli, Enrique, Mira, Sally, Kim, CD"* —
Dan + CD already handled as Category A entry #6) but with **no skill directory
on disk**. Some have empty sidecar stubs under `_bmad/memory/<name>-sidecar/`
that were reserved at planning time but never populated.

| # | Role name | Skill dir | Sidecar stub | Treatment |
|---|---|---|---|---|
| 16 | Mike | ❌ none | `_bmad/memory/mike-sidecar/` (empty) | **Deferred to post-M5 greenfield mini-epic.** Generate via `bmad-create-specialist` on hybrid when role is actually needed. |
| 17 | Eli | ❌ none | (none) | Same |
| 18 | Enrique | ❌ none | `_bmad/memory/enrique-sidecar/` (empty) | Same |
| 19 | Mira | ❌ none | `_bmad/memory/mira-sidecar/` (empty) | Same |
| 20 | Sally | ❌ none | (none; BMad stock agent exists for UX design) | Same — may turn out to be BMad stock re-use rather than a custom specialist |
| 21 | Kim | ❌ none | `_bmad/memory/kim-sidecar/` (empty) | Same |
| 22 | Paige | ❌ none (BMad stock) | (none) | BMad stock agent; Epic 2b spec explicitly hedges with "Paige-as-runtime-specialist-if-scoped". **Not migrated as custom specialist.** |

**Category E total: 7 names, 0 migrated in Slab 2.**

**Post-M5 greenfield mini-epic:** generate any of these directly on hybrid
via `bmad-create-specialist` (the generator from Story 2a.1) when the
operational need for each becomes concrete. No migration; pure greenfield
on the migrated platform. Filed to
[`deferred-inventory.md`](deferred-inventory.md) §Backlog Epics as
"Post-M5 Greenfield Specialists."

---

## Summary — reconciled Slab 2 migratable count

| Category | Count | Slab 2 work |
|---|---|---|
| A + B — Mature + moderate | 9 (incl. Wondercraft absorbed 2026-04-24) | Real 2b.N stories, template from 2b.1 Gary |
| C — Tier-4 manual thin | 5 | Thin 2b.N stories (minutes per node) |
| D — Dissolved | 0 | No migration; skill dirs archival |
| E — Roadmap-only | 0 in Slab 2 | Post-M5 greenfield epic |
| **Slab 2 total migratable nodes** | **14** | |
| Plus 2a.1 generator + 2c.1 scope TBD (Path A vs Path B above) | +1 to +2 | Scaffold infra + generator validation |
| **Slab 2 total story count** | **~15–16** | Under original planning envelope (Epic 2b = 17 stories) |

**M2 acceptance bar** ("17-specialist scaffold + Wondercraft pilot <1 dev-day")
remains achievable: scaffold-conformance coverage lands on all 13 real nodes;
Wondercraft validates the generator end-to-end; the 7 roadmap-only names
were never real specialists and do not block M2.

---

## Reclassification Log

*(Append one entry per reclassification event during Slab 2. Format: date, role, old category, new category, rationale.)*

---

## Cross-references

- [`docs/dev-guide/langgraph-migration-guide.md §8.1`](../../docs/dev-guide/langgraph-migration-guide.md#81-upstream-severance-slab-2) — upstream severance protocol (replaces FR60 forward-port freeze)
- [`_bmad-output/implementation-artifacts/upstream-severance-log.md`](../implementation-artifacts/upstream-severance-log.md) — absorption + severance audit trail (2026-04-24)
- [`_bmad-output/planning-artifacts/epics-langchain-langgraph-migration.md` §Epic 2b](epics-langchain-langgraph-migration.md) — authoritative migration-epic spec (now supplemented by this reconciliation)
- [`_bmad-output/planning-artifacts/deferred-inventory.md`](deferred-inventory.md) — post-M5 greenfield specialists entry + Audra/Cora dissolution entry
