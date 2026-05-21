# Slab 6 trial-experience bundle — governance discipline (BINDING)

**Purpose:** standing reference for the governance gates that fire at every story in the Slab 6 trial-experience bundle (6.2 + 6.3 + 6.4 + 6.5). Authored 2026-04-27 to codify the discipline that worked through Slab 6.0 + 6.1 close so future stories inherit the pattern without operator having to enforce it manually each dispatch.

**Source authority:**
- CLAUDE.md §1 (BMAD workflows for spec authoring)
- CLAUDE.md §2 (party-mode for green-lighting + initial review)
- CLAUDE.md §3 (bmad-code-review before any story flips to done)
- CLAUDE.md §4 (BMAD team consensus across active workflow steps)
- `docs/dev-guide/composition-specification.md` §10 Decision Log + §11 Migration Triggers + §14 Maintenance Protocol
- `docs/dev-guide/substrate-inventory-checklist.md` (N1–N12 standing pre-flight)
- `docs/dev-guide/specialist-anti-patterns.md` (A1–A17 + P1–P3 catalog)

**Scope:** binding for stories 6.2, 6.3, 6.4, 6.5, and any future Slab 6.x stories filed under `migration-epic-6-post-mvp-production` epic.

---

## 1. Per-story gate sequence (BINDING)

Every Slab 6.x story passes through SIX gates. None may be skipped without explicit operator party-mode ratification + amendment to this discipline doc.

```
Gate 0 — Spec authoring (bmad-create-story OR direct authoring)
   ↓
Gate 1 — bmad-party-mode green-light (Winston + Murat + Paige + Amelia minimum)
   ↓ (status: ready-for-party-mode-greenlight → ready-for-dev)
Gate 2 — bmad-dev-story implementation (Codex)
   ↓
Gate 3 — bmad-code-review (3-layer: Blind Hunter + Edge Case Hunter + Acceptance Auditor)
         + N-item trace section (BINDING per Slab 6.0 governance)
   ↓
Gate 4 — Triage (patch / defer / dismiss / decision_needed)
         + Operator dispositions on any decision_needed items
   ↓ (status: review)
Gate 5 — Operator-side dual-gate gate-2 (FOR DUAL-GATE STORIES ONLY)
         OR single-gate dev-side acceptance (single-gate stories)
   ↓
Gate 6 — Formal close (sprint-status flip → done; deferred-inventory updates;
         Composition Spec §10 Decision Log entry IF substrate-affecting;
         m5-decision close annotation IF migration-claim-affecting)
```

### Gate 1 details — bmad-party-mode green-light

**Mandatory voices** for every Slab 6.x story:
- 🏗 **Winston** (architect) — substrate-shape + Composition Spec §11 trigger detection
- 🧪 **Murat** (test architect) — K-target rationality + N-item trace coverage
- 📝 **Paige** (tech writer) — spec clarity + cross-reference correctness
- 💻 **Amelia** (dev) — implementation feasibility + halt-and-adapt budget realism

**Optional additional voices** if story specifically warrants:
- 🔍 **Quinn-R** — for any story that touches gate semantics or composition smoke
- 🎯 **Mary** — for any story that lands an anti-pattern catalog entry (harvest-gate)
- 📊 **Dr. Quinn** — for any story that touches replay-regression discipline

**Output of Gate 1:** ratified spec + applied riders + version-stamped party-mode record. Sprint-status flips from `ready-for-party-mode-greenlight` to `ready-for-dev`.

**HALT rule:** if party-mode round impasses on architecture, halt that story; surface to operator for re-scope decision; do NOT silently proceed.

### Gate 3 details — bmad-code-review N-item trace section (BINDING)

Per Slab 6.0 governance (codified in `codex-handoff-slab-6-0-code-review.md` + reaffirmed per Slab 6.1 review), every bmad-code-review deliverable MUST include a `§Substrate Inventory Checklist Trace` section as first-class deliverable. Schema:

| N-item | Applicability to <story> | Trace evidence | Verdict |
|---|---|---|---|
| N1 — External-provider resource ID validity | applicable / not-applicable | concrete artifact citation OR rationale | PASS / FAIL / N/A / decision_needed |
| ... (N2 through N12) | ... | ... | ... |

**Rules:**
- All twelve N-items present; N/A explicitly named with rationale
- Trace evidence must cite concrete artifacts (test paths, AC IDs, commit SHAs)
- FAIL verdicts auto-promote to `patch` items in main triage; bidirectional linkage required
- N13+ extensions follow the substrate-inventory-checklist.md extension protocol (propose, don't unilaterally add; operator ratification required before becoming standing)

**Verdict variants** (used during Slab 6.1 review): PASS-WITH-DEFER, PASS-PENDING-OPERATOR are valid where the underlying disposition is recorded explicitly.

### Gate 5 details — Operator-side acceptance

For **dual-gate stories** (currently only 6.4 in this bundle): operator runs the live evidence command per spec; pastes evidence into Dev Agent Record §"Operator dual-gate gate-2 evidence"; only then proceeds to Gate 6.

For **single-gate stories** (6.2, 6.3, 6.5): operator confirms dev-side verification at code-review triage close; no separate operator-witnessed live ceremony required (per `docs/dev-guide/story-cycle-efficiency.md` single-gate vs dual-gate policy).

### Gate 6 details — Formal close

Per-story formal close protocol:
1. Sprint-status flip `review → done` with summary annotation
2. Deferred-inventory updates (any new entries from triage; status flips for resolved entries)
3. Composition Spec §10 Decision Log entry — REQUIRED if any substrate-affecting decision was made (substrate-affecting = any change to envelope, adapter, dependency_map mechanism, gate precedence, persistence shape, composition-test discipline, or §11 migration trigger detection)
4. m5-decision close annotation — REQUIRED if the story changes the migration claim shape or scope
5. `next-session-start-here.md` update IF tracked by repo policy (currently untracked per Slab 6.0 + 6.1 close findings — skip if untracked)

---

## 2. Composition Specification adherence (BINDING throughout dev)

`docs/dev-guide/composition-specification.md` is **normative for Option B evolution**. Every Slab 6.x story dispatch MUST:

1. **Read at T1** alongside spec, anti-pattern catalog, and substrate inventory checklist
2. **Honor §3 invariants** during implementation:
   - §3.1 envelope immutability (Path Z "first contribution wins")
   - §3.5 gate precedence (per-specialist non-blocking under production by default; `gate_overrides` opt-in)
   - §3.6 dependency_map sourcing (manifest-declared post-6.2; runner-layer fallback for backward-compat)
   - §3.7 persistence shape (full-embed `production_envelope` in `ProductionTrialEnvelope`)
3. **Detect §11 migration trigger conditions during dev** — if any of the six triggers fires (fan-out / partial state / gate precedence complexity / adapter LOC / new act-body category / Decision Log rate), HALT and surface to operator. Do NOT silently absorb the trigger into Option B work.
4. **File §10 Decision Log entry** at story close if any substrate-affecting decision was made (per Gate 6 above)
5. **Fall back to operator party-mode** for any §11 migration trigger surfacing — Composition Spec §11 evaluation is operator + party-mode authority, not dev-agent authority

**Rationale:** Composition Spec §11 triggers were authored to make B→C escalation evidence-based. Detection is everyone's responsibility (dev + reviewer + operator); decision is operator + party-mode.

---

## 3. Anti-pattern catalog adherence (BINDING throughout dev)

`docs/dev-guide/specialist-anti-patterns.md` (A1–A17 + P1–P3) is the harvest-and-prevention catalog. Every Slab 6.x story dispatch MUST:

1. **Read catalog at T1** — identify which entries apply to the story's surface
2. **Honor counter-patterns** named per applicable entry
3. **File harvest candidates** if a NEW pattern surfaces during dev — propose to Mary (or operator if Mary not available); do NOT silently ignore
4. **Cross-link to N-items** where the catalog entry has an N-item counterpart (e.g., A15 ↔ N1; A16/A17 ↔ N2; P3 ↔ N9)

**Rationale:** the catalog is the operationalized harvest of every substrate gap surfaced through Slabs 1–6.1. Each new entry was earned by an A-class incident. New stories should consume the catalog at design time, not re-discover its lessons in production.

---

## 4. bmad-code-review dispatch shape (per-story; BINDING)

Every Slab 6.x story's bmad-code-review dispatch MUST include:

1. **Predecessor state** section naming all relevant commits + Codex-side verification numbers
2. **Operator dispositions** section naming any pre-ratified decisions that inform the Acceptance Auditor (Auditor traces correctness; does NOT re-litigate)
3. **Mission** statement framed around the dual-gate or single-gate rationale per the spec's gate designation
4. **Scope** with explicit IN-SCOPE + NOT-IN-SCOPE lists (treat any modification to NOT-IN-SCOPE as substantive finding)
5. **Spec inputs** (Acceptance Auditor reads these) including: primary spec, Composition Spec, Substrate Inventory Checklist, anti-pattern catalog
6. **Specific things to review for substantively** — itemized list with specific Acceptance Auditor focus points; should number ~6-12 items per story
7. **Things NOT to flag** — anti-cosmetic-NIT discipline per `story-cycle-efficiency.md`; explicit out-of-scope items; pre-existing dirty state
8. **Sequencing** — three layers in parallel; triage merge; patch / defer / dismiss / decision_needed
9. **Required deliverable section: §Substrate Inventory Checklist Trace** — per Gate 3 schema above; BINDING; not optional
10. **Disposition rules** — patch / defer / dismiss / decision_needed semantics
11. **Closeout protocol** — per Gate 6 above; explicit list of files to update at close

Template references: `codex-handoff-slab-6-0-code-review.md` (canonical shape for substrate stories); `codex-handoff-slab-6-1-runner-code-review.md` (canonical shape for runner stories).

---

## 5. Story-specific party-mode focus areas (recommended)

### 6.2 — Promote dependency_map into manifest
- Winston: manifest schema-extension correctness; backward-compat preservation; runner-layer fallback retention rationale
- Murat: K-floor 7 sufficient? Test surface covers manifest-declared + fallback-resolved + missing-upstream cases?
- Paige: Composition Spec §3.6 update language; cross-references to deferred-inventory
- Amelia: implementation feasibility (~4-6 hr realistic? halt-and-adapt budget?)

### 6.3 — Step 02A prior-run directives as defaults
- Winston: architecture decision — Marcus PR-* extension vs Step 02A pack amendment? Operator preference for surface that minimizes cross-Marcus regression risk
- Murat: K-floor + test coverage for present-prior-bundle / no-prior-bundle / explicit-accept-modify-replace
- Paige: docs/operator/ surface clarity
- Amelia: feasibility against existing Marcus PR-* surface

### 6.4 — Irene Pass 2 authoring template (DUAL-GATE; HIGHEST priority)
- Winston: schema-shape (Pydantic v2 + JSON Schema vs Markdown vs both?); template location decision
- Murat: K-target adequacy (target ~16 / floor ~12); replay-regression preservation under new template; existing validator alignment test
- Paige: docs/dev-guide/irene-pass-2-authoring.md operator-facing clarity
- Amelia: feasibility — validator contract may not cleanly express in schema (cluster arc continuity rules)
- Quinn-R: template usable in BOTH M3 harness and production runner contexts (per N11 composition-mode-declared)
- Mary: harvest-gate review — does this template work surface a NEW anti-pattern? (A6 implicit-validator-contract counter-pattern is already named; verify no NEW pattern emerges)

### 6.5 — HUD per-step expandable summaries
- Winston: summary derivation source (existing artifacts vs new emitter); HUD interaction model
- Murat: 14 step types covered; per-step derivation function tests
- Paige: docs/operator/hud-guide.md interaction model documentation
- Amelia: feasibility against existing `scripts/run_hud.py` + Batch 3 hud-modernization story integration

---

## 6. Halt-and-surface triggers (BINDING throughout dev)

Codex MUST HALT and surface to operator if any of the following occur during Gate 2 (bmad-dev-story) or Gate 3 (bmad-code-review):

1. **Substrate disagreement** — story spec assumes a substrate shape that doesn't exist or doesn't behave as specified
2. **Composition Spec §11 migration trigger** — any of the six triggers fires (per §2 above)
3. **Decision_needed surfaces** — multi-option choice where Codex can't reasonably pick without operator judgment
4. **N-item FAIL during dev** — auto-promote to in-story `patch` (don't defer N-item failures); but if patch effort exceeds story budget, surface
5. **NEW anti-pattern emerges** — propose to Mary harvest-gate; don't silently absorb
6. **Cross-cutting impact** — story scope expands to touch substrate not in spec's IN-SCOPE list

The halt-and-surface discipline is the same pattern used across A15 / A16 / A17 / P3 / Slab 6.1 strict-AC HALT instances. Halting is the right move; silently expanding scope is the wrong move.

---

## 7. Composition Spec §10 Decision Log — what counts as substrate-affecting

Story authors + dev-agents + reviewers should default to "yes, it's substrate-affecting" if any of the following:

- Envelope shape changes (model + JSON Schema + golden + shape-pin tests)
- Adapter contract changes (input/output signatures of `ProductionDispatchAdapter.invoke_specialist(...)`)
- Dependency_map mechanism changes (sourcing, resolution rule, fail-loud semantics)
- Gate precedence rule changes (per-specialist + production-level relationships)
- Persistence shape changes (`ProductionTrialEnvelope` shape; trial close artifact structure)
- Composition-test discipline changes (chain-test-per-PR rule; fixture shape)
- Composition Smoke gate changes (slab-opener template amendment)
- Any §11 migration trigger threshold change

For Slab 6.x trial-experience bundle:
- 6.2 IS substrate-affecting (dependency_map sourcing change) → §10 entry REQUIRED
- 6.3 likely NOT substrate-affecting (Marcus surface enhancement; doesn't touch composition substrate) → §10 entry not required unless dev surfaces unexpected coupling
- 6.4 likely NOT substrate-affecting (Irene authoring template; per-specialist surface; doesn't touch composition substrate) → §10 entry not required unless dev surfaces unexpected coupling
- 6.5 likely NOT substrate-affecting (HUD enhancement; doesn't touch runtime substrate) → §10 entry not required

**Default to file an entry; remove if obviously not substrate-affecting.** Cheap to file; expensive to miss.

---

## 8. Maintenance protocol for this document

This document extends naturally as new Slab 6.x stories are filed (or as the discipline evolves). Update at:

1. **Each new Slab 6.x story filed** — add story-specific party-mode focus areas to §5 if non-trivial
2. **Each new anti-pattern catalog entry** — verify §3 application discipline still covers the new entry
3. **Each substrate inventory checklist N13+ extension** — verify Gate 3 schema accommodates the new N-item
4. **Composition Spec §11 trigger fire** — discipline doc should reflect the trigger evaluation outcome
5. **At Slab 6 epic close** — retire this doc OR repurpose as Slab 7 governance template depending on operator decision

Decisions to remove or contract this document require party-mode ratification. Decisions to extend it are dev-agent authority.

---

## 9. Quick reference — what every Slab 6.x dispatch MUST contain

Authoring checklist for any future Slab 6.x story dispatch:

- [ ] Read at T1: spec + Composition Spec + Substrate Inventory Checklist + anti-pattern catalog + this discipline doc
- [ ] Identify applicable N-items per substrate inventory checklist
- [ ] Identify applicable anti-pattern catalog entries (counter-patterns to honor)
- [ ] Honor Composition Spec §3 invariants throughout dev
- [ ] Detect §11 migration trigger conditions; HALT if fired
- [ ] File §10 Decision Log entry at close IF substrate-affecting (default yes; remove if obviously not)
- [ ] Run bmad-party-mode (Winston + Murat + Paige + Amelia minimum) BEFORE flipping to ready-for-dev
- [ ] Run bmad-code-review (3-layer + N-item trace deliverable) BEFORE flipping to done
- [ ] For dual-gate stories: operator-side dual-gate gate-2 evidence pasted in Dev Agent Record before close
- [ ] Formal close protocol per Gate 6 above
- [ ] Halt-and-surface per §6 if any of six triggers fire

This is the standing pattern. It is not optional. Operator ratification + party-mode amendment required to deviate.
