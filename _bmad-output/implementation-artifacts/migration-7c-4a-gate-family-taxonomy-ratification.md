# Migration Story 7c.4a: Gate Family Taxonomy Ratification (Decision-Only)

**Status:** done  <!-- 2026-05-05 T11 lite review PASS (zero patches; zero deferred); ADR 0002 ratifies 8 family + 10 alias + 18 runtime IDs + alias_of forward syntax. Verdict at 7c-4a-code-review-2026-05-05.md --> *(spec authored 2026-05-04; predecessor 7c.0b closed; Codex T1-T5 complete 2026-05-05; ready for Claude T11 lite code review.)*
**Sprint key:** `migration-7c-4a-gate-family-taxonomy-ratification`
**Epic:** Slab 7c — Marcus Orchestrational Tail (`migration-epic-slab-7c-orchestrational-tail`)
**Pts:** 1
**Gate:** **single-gate** (per `docs/dev-guide/migration-story-governance.json` v2026-05-04-slab7c-thirty-six-stories, story 7c-4a; rationale: null — decision artifact only; no schema-shape / lane-boundary / invariant-preservation / operator-acceptance surface)
**K-target:** ~1.0× (decision-tier band; ~1 pt; bounded surface = 1 ADR markdown file + 1 structural test asserting heading set)
**R-tier (regression scope):** **R1** — focused-test + impact-zone only; the 1 new structural test + lint-imports + class-conformance are sufficient verification for a decision-only ADR (no production code lands). Per AMEND-V2 2026-05-04 velocity-amendments-bundle.
**T11-tier (review approach):** **lite** — single-gate AND AC count = 2 (well ≤5) AND single-file or sibling-files only AND no schema/contract/governance touch AND Codex T10 expected clean. ~10-15 min Claude review. Per AMEND-V3 2026-05-04 velocity-amendments-bundle.
**Files touched (declared at spec-author time):**
- `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` (NEW; or next-free index per T1.2 if 0002 collides)
- `tests/structural/test_adr_0002_slab_7c_gate_taxonomy_present.py` (NEW)
**Lookahead tier:** **1** — author-ahead-aggressively (PRD-locked taxonomy per Amelia A3 PRD Step 11; spec authored 2026-05-04 ahead of 7c.0a/0b dispatch); dispatch HELD until 7c.0b closes per `prerequisite_stories: [7c-0b]`.
**Authored:** 2026-05-04 via `bmad-create-story` workflow (lookahead-discipline; spec authored ahead of dispatch while Codex devs 7c.0a). Velocity-amendment fields backfilled 2026-05-04 post-amendment-bundle ratification.
**Wave:** 2 — slot 1 (decision-tier; precedes 7c.4b foundation; 7c.5.G0..G6 per-gate stories also depend on this taxonomy lock).

**FR coverage:** **None direct** (decision artifact only). 7c.4a ratifies the taxonomy that downstream FRs operate against:
- FR-7c-6 (Marcus dispatches DecisionCards at every gate code in expanded `PRODUCTION_GATE_IDS`).
- FR-7c-7 (each new gate emits typed Pydantic-v2 DecisionCard four-file-lockstep).
- FR-7c-37 (14/14 four-file-lockstep co-commit AUDIT at 7c.20c).

**NFR coverage:** **None direct.** Enables NFR-7c-M1 (four-file-lockstep) + NFR-7c-R6 (pipeline-manifest lockstep) + NFR-7c-OD7 (parity-DSL self-registration audit) downstream. NFR-7c-M5 (sandbox-AC validator PASS).

**Standing-guardrail enforcement:** SG-1/2/3/4 unchanged (decision artifact only).

**Implementation cycle (NEW CYCLE per memory entry `feedback_new_cycle_codex_dev_handoff.md` 2026-05-04):**
- **Claude (Opus 4.7):** authored this spec ahead of dispatch (lookahead discipline); sandbox-AC validator PASS confirmed; governance JSON entry verified.
- **DISPATCH HELD until predecessor closes:** the dispatch chain is **7c.0a → 7c.0b → 7c.4a**. Operator does NOT dispatch this Codex prompt until both 7c.0a AND 7c.0b have closed `done`. At that point, AMELIA-P2 freshness check re-diffs spec vs prompt; regenerate if drift.
- **Codex (Sonnet 4.5 or later):** develops the ADR + structural test per the ACs and tasks below; reaches `review` status; produces a self-conducted T10 layered review at `_bmad-output/implementation-artifacts/_codex-handoff/7c-4a.ready-for-review.md`.
- **Claude:** does the FINAL `bmad-code-review` (T11; single-gate; cross-agent NOT mandatory but Claude review remains mandatory per BMAD sprint governance §3); applies remediation cycles; commits; flips `migration-7c-4a-gate-family-taxonomy-ratification` review → done in sprint-status.

---

## T1 Readiness Block

**Required readings (cite by reference; do NOT re-derive at T1):**
- `docs/dev-guide/story-cycle-efficiency.md` — K-discipline (target 1.0× for decision-only artifacts).
- `_bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md` — alias decision LOCKED at PRD Step 11 per Amelia A3 (8 net-new + N alias).
- `_bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md` (Story 7c.4a section starting at line 548) — taxonomy decision content.
- `docs/dev-guide/adr/0001-parity-contract-dsl.md` — 7c.0a's ADR; documents the **alias-DSL clause** that 7c.4a's taxonomy invokes for alias inheritance.

**Predecessor state (verified at dispatch — NOT at authoring; the dispatch chain is 7c.0a → 7c.0b → 7c.4a):**
- 7c.0a status = `done` in BOTH the spec file AND `sprint-status.yaml::development_status['migration-7c-0a-decision-foundation']`.
- 7c.0b status = `done` in BOTH the spec file AND sprint-status.
- ADR `docs/dev-guide/adr/0001-parity-contract-dsl.md` exists (or alternate path if 7c.0a re-numbered) and contains the alias-DSL clause specification.
- TripwireLedgerEntry at `app/models/tripwire_ledger.py` exists (informational — not consumed by 7c.4a but confirms 7c.0a closed cleanly).
- Import-linter contracts C4/C5/C6 exist in `pyproject.toml::[tool.importlinter]` (informational).

**Live substrate (verified at dispatch):**
- ADR slot `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` is RESERVED for THIS story (per Slab 7c epic Story 7c.0a Dev Notes); MUST be free at dispatch. If 7c.0a re-numbered its ADR (7c.0a's own slot was occupied), 7c.4a's slot may have shifted too — surface as `decision_needed` at T1 and pick the next-free index.
- Pre-Slab-7c `PRODUCTION_GATE_IDS` is 4 gates (G1, G2C, G3, G4) per Slab 7a substrate; the taxonomy expansion ratified here brings the total to 14.

**Gate-mode rationale (from governance JSON):**
> Slab 7c Wave 2 (decision artifact only; no code). Gate-family taxonomy ratification: 8 net-new gate families (G0/G1/G2A/G2C/G3/G4/G5/G6) + 6 alias gates (G0A/G0B/G1A->G1; G2B/G2M/G2.5/G2F->G2C; G3B->G3; G4A/G4B->G4) via alias-DSL clause inheritance. Lands at docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md. K-target 1.0x (decision ADR; no implementation). Predecessor: 7c.0b (alias-DSL clause defined there).

**Taxonomy count reconciliation (raise at T1 as `decision_needed` if discrepancy persists):** the epic Story 7c.4a section says "8 net-new gate families" + "6 alias gates" but enumerates 10 alias mappings (G0A, G0B, G1A, G2B, G2M, G2.5, G2F, G3B, G4A, G4B). FR-7c-6 says expansion is 4 → 14, implying 10 NEW IDs added. Possible reconciliations: (a) "6 alias gates" is a stale count from an earlier draft; the canonical alias count is 10 (matching PRODUCTION_GATE_IDS expansion). (b) Some alias mappings collapse under the alias-DSL clause (e.g., G0A and G0B both → G1, treated as one alias entry). Codex SHALL surface this as `decision_needed` at T1 and the ADR documents the canonical count + reasoning. Recommend (a) — list all 10 alias mappings explicitly.

**T1 conclusion:** No unanticipated architectural disagreement. Implementation proceeds: ADR authoring + structural test. **Hard checkpoints at T1:** confirm ADR slot 0002 free; confirm 7c.0a + 7c.0b both `done`; resolve alias-count discrepancy (recommend 10).

---

## Story

As the architect (downstream-story author),
I want one decision-tier story that ratifies the gate-family taxonomy decision (8 net-new gate families + N alias gates per the PRD-locked alias map) as a decision-only ADR without implementation,
so that 7c.4b foundation (gate shared base classes + class-conformance validator extension) and 7c.5.G0..G6 per-gate stories (eight four-file-lockstep authoring stories) proceed against an unambiguous, frozen taxonomy with no relitigation at story-author time.

---

## Acceptance Criteria

### AC-7c.4a-A — ADR `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` lands with all required sub-sections (FR-7c-6 / FR-7c-7 enabling)

**Given** the PRD §Gate Taxonomy LOCK at PRD Step 11 (per Amelia A3) + the epic Story 7c.4a section
**When** the dev-agent authors `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` (or the next-free ADR slot if 0002 is occupied — surface as `decision_needed` at T1)
**Then** the ADR documents **all five required sub-sections** in order:

1. **Net-new gate families (8 entries):**
   - **G0** — trial-open / corpus-confirm gate. Net-new (no prior shipped contract). 7c.5.G0 fresh-author.
   - **G1** — directive-ratification gate. ALREADY SHIPPED at 7a substrate. 7c.5.G1 extend-and-audit per Winston W3.
   - **G2A** — plan-unit-ratification gate. Net-new. 7c.5.G2A fresh-author.
   - **G2C** — pre-composition QA gate. ALREADY SHIPPED. 7c.5.G2C extend-and-audit per Winston W3.
   - **G3** — motion-clip approval gate. ALREADY SHIPPED. 7c.5.G3 extend-and-audit per Winston W3.
   - **G4** — fidelity gate. ALREADY SHIPPED. 7c.5.G4 extend-and-audit per Winston W3.
   - **G5** — final operator handoff gate. Net-new. 7c.5.G5 fresh-author.
   - **G6** — slab-close ceremony gate. Net-new. 7c.5.G6 fresh-author.
   - *(Reconciliation: per AMEND-5 Round-2 split, fresh-author = G0/G2A/G5/G6 (4); extend-and-audit = G1/G2C/G3/G4 (4); total = 8 four-file-lockstep families.)*

2. **Alias gates (10 mappings; canonical count to be ratified at T1):**
   - **G0A → G1** — operator-corrects-corpus surface alias.
   - **G0B → G1** — operator-edits-directive surface alias.
   - **G1A → G1** — per-plan-unit ratification alias (consumed by §04A surface 7c.6).
   - **G2B → G2C** — per-slide mode alias (consumed by §05.5 surface 7c.9).
   - **G2M → G2C** — per-slide A/B variant alias (consumed by §07B surface 7c.10).
   - **G2.5 → G2C** — motion-plan polling alias (consumed by §07D surface 7c.11).
   - **G2F → G2C** — motion gate alias (consumed by §07F surface 7c.12).
   - **G3B → G3** — Storyboard B + live-URL alias (consumed by §08B surface 7c.13).
   - **G4A → G4** — voice-selection alias (consumed by §11 surface 7c.14).
   - **G4B → G4** — input-package + §15 final operator handoff alias (consumed by §11B surface 7c.15).
   - *(Note: epic Story 7c.4a section says "6 alias gates" but enumerates these 10. Codex resolves at T1: recommend ratifying 10 explicit mappings; "6" was a stale count from an earlier draft. ADR records the resolution.)*

3. **Alias-DSL clause inheritance (consumes 7c.0a ADR):** an alias gate (e.g., G0A) inherits the parent G1's four-file-lockstep contract via the **alias-DSL clause** defined in 7c.0a's `docs/dev-guide/adr/0001-parity-contract-dsl.md`. **No separate four-file-lockstep stories needed for the 10 aliases.** FR-7c-37 14/14 co-commit AUDIT at 7c.20c verifies the gate's lockstep for the gate itself + alias inheritance via the clause.

4. **PRODUCTION_GATE_IDS expansion 4 → 14:**
   - Pre-Slab-7c (Slab 7a substrate): 4 gates — `{G1, G2C, G3, G4}`.
   - Post-Slab-7c (after 7c.4b foundation + 7c.5.G0..G6 four-file-lockstep + alias-DSL clause): 14 gates — pre-existing 4 + 4 net-new (G0, G2A, G5, G6) + 6 alias-DSL-resolved (G0A→G1, G0B→G1, G1A→G1, G3B→G3, G4A→G4, G4B→G4). Of the 10 enumerated aliases, 4 (G2B, G2M, G2.5, G2F) all resolve to G2C — these are alias **labels** that share G2C's family, but in the PRODUCTION_GATE_IDS list they may either (a) appear as separate IDs that resolve to G2C at runtime, or (b) collapse to G2C. ADR documents the resolution. Recommend (a) — separate IDs for runtime introspection, all routing to G2C's four-file-lockstep.
   - Final canonical PRODUCTION_GATE_IDS list: `{G0, G0A, G0B, G1, G1A, G1.5, G2, G2B, G2C, G2M, G2.5, G2F, G3, G3B, G4, G4A, G4B, G5}` per FR-7c-6 list (18 IDs — note FR-7c-6 enumerates 18, NOT 14; AMEND-1-style reconciliation at T1).

5. **Status line + cross-references:** "Status: ACCEPTED — 2026-05-NN by single-gate dev-round (Story 7c.4a). Predecessor: 7c.0b done. Cross-references: PRD §Gate Taxonomy LOCK (Step 11; Amelia A3); epic Story 7c.4a section; governance JSON 7c-4a entry; downstream consumers 7c.4b + 7c.5.G0..G6."

**Test pin:** `tests/structural/test_adr_0002_slab_7c_gate_taxonomy_present.py` — asserts the ADR file exists at the canonical (or surfaced-at-T1-decision_needed) path AND contains all five required sub-section headings via substantive-keyword regex (e.g., `net-new`, `alias`, `inheritance`, `PRODUCTION_GATE_IDS expansion`, `status line`).

> **Notes for 7c.4a-A.** This AC is **dev-agent-executable** (markdown authoring + structural test). Codex resolves the count discrepancies (8 vs 8, 6 vs 10, 14 vs 18) at T1 and the ADR records the canonical numbers. The structural test pin matches against substantive keywords, not exact heading strings.

### AC-7c.4a-B — Alias-DSL clause inheritance demonstrated for at least one alias mapping (cross-validates 7c.0a's ADR)

**Given** 7c.0a's ADR specifies the alias-DSL clause shape (registration mechanism + transport declaration schema + per-surface declaration)
**When** the 7c.4a ADR documents alias inheritance for a representative mapping (e.g., G0A → G1)
**Then** the documentation includes a worked example showing:

1. The DSL invocation pattern that registers G0A as an alias of G1 (e.g., `@parity_contract(alias_of="G1")` decorator OR YAML registration entry — pick whatever 7c.0a's ADR canonicalized).
2. How the alias-DSL clause routes G0A's four-file-lockstep AUDIT (from FR-7c-37 14/14 co-commit) to G1's four files (`app/models/decision_cards/g1.py`, `g1.v1.schema.json`, `test_decision_card_g1_shape.py`, `g1_golden.json`).
3. How runtime DecisionCard emission for G0A inherits G1's `DecisionCardMeta.cache_state` invariant.

**And** the example uses the canonical alias-DSL syntax from 7c.0a's ADR; if the 7c.0a ADR did NOT explicitly canonicalize the syntax (i.e., left it open as a "downstream story implements" placeholder), 7c.4a's ADR proposes the syntax in this AC and records the proposal as a forward-pointer for 7c.0b's executable scaffold.

**Test pin:** the structural test from AC-7c.4a-A SHALL be extended to assert the worked-example heading is present.

> **Notes for 7c.4a-B.** This AC is **dev-agent-executable** (markdown authoring). The demonstration is documentation-only; no Python code lands in 7c.4a. The actual DSL primitives that implement the alias-DSL clause live in 7c.0b; 7c.4a is the canonical specification of how downstream stories use them.

---

## Tasks / Subtasks

- [x] **T1 — Readiness checks (AC: T1 Readiness Block)**
  - [x] T1.1 Verify 7c.0a + 7c.0b both `done` in spec files AND sprint-status.yaml.
  - [x] T1.2 Confirm ADR slot `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` is free (or pick next-free if 7c.0a's ADR re-numbered cascaded).
  - [x] T1.3 Resolve alias-count discrepancy (recommend 10 explicit mappings).
  - [x] T1.4 Resolve PRODUCTION_GATE_IDS final-count discrepancy (FR-7c-6 enumerates 18; epic says expansion is 4 → 14; ADR records canonical resolution).
  - [x] T1.5 Confirm 7c.0a's ADR canonicalized alias-DSL syntax (decorator vs YAML); if not, 7c.4a's ADR proposes via forward-pointer.
  - [x] T1.6 Run sandbox-AC validator on this spec; expect PASS.

- [x] **T2 — Author ADR `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` (AC: 7c.4a-A + 7c.4a-B)**
  - [x] T2.1 Five required sub-sections (net-new families + alias gates + alias-DSL inheritance + PRODUCTION_GATE_IDS expansion + status line).
  - [x] T2.2 Worked example for one alias mapping (G0A → G1).
  - [x] T2.3 Cross-references to PRD + epic + governance JSON + 7c.0a's ADR.

- [x] **T3 — Author structural test `tests/structural/test_adr_0002_slab_7c_gate_taxonomy_present.py` (AC: 7c.4a-A + 7c.4a-B)**
  - [x] T3.1 Path-existence assertion + 5 sub-section heading assertions + worked-example heading assertion. Substantive-keyword regex.

- [x] **T4 — CI hygiene clean (NFR-7c-R5 / NFR-7c-X4 / NFR-7c-M5)**
  - [x] T4.1 Run focused tests: `pytest tests/structural/test_adr_0002_slab_7c_gate_taxonomy_present.py -p no:randomly` — pass.
  - [x] T4.2 Run broad regression: `pytest -p no:randomly` — ≥1403 baseline preserved.
  - [x] T4.3 Sandbox-AC validator PASS (re-run from T1.6).
  - [x] T4.4 Class-conformance validator: 11 conforming activation contracts (no regression).
  - [x] T4.5 `lint-imports` clean (KEPT count unchanged; 7c.4a does not modify import-linter contracts).

- [x] **T5 — Codex self-review (NEW CYCLE T10)**
  - [x] T5.1 Codex authors `_bmad-output/implementation-artifacts/_codex-handoff/7c-4a.ready-for-review.md` summarizing: file list (ADR + 1 structural test = 2 NEW files), test counts, ruff status, broad-regression delta, sandbox-AC validator status, alias-count + PRODUCTION_GATE_IDS resolution at T1, alias-DSL syntax resolution at T1, deferred follow-ons surfaced.

- [ ] **T6 — Claude `bmad-code-review` (single-gate; cross-agent NOT mandatory)**
  - [ ] T6.1 Claude (separate cold context from Codex dev) runs `bmad-code-review` against the 2-file diff; produces verdict at `_bmad-output/implementation-artifacts/7c-4a-code-review-2026-05-NN.md`; applies remediation cycles if HALT-AND-REMEDIATE; commits + flips `migration-7c-4a-gate-family-taxonomy-ratification: review → done` in sprint-status.

---

## Dev Notes

**Architecture decisions inherited from PRD + epic-decomposition party-mode 2026-05-04:**
- **Amelia A3** — Alias decision LOCKED at PRD Step 11. Not deferred to 7c.4 sprint-planning. Taxonomy is frozen at PRD time.
- **Winston W3** — Per-gate AMEND-5 split: 4 fresh-author (G0/G2A/G5/G6) + 4 extend-and-audit (G1/G2C/G3/G4 already shipped). 7c.4a documents this; 7c.5.G0..G6 carry the implementation.
- **Winston W4** — Decision-then-Foundation pattern: 7c.4a → 7c.4b mirrors 7c.0a → 7c.0b. Both instances are documented in 7c.0a's ADR.

**Taxonomy reconciliations to surface at T1:**
- "8 net-new + 6 alias gates" (epic Story 7c.4a) vs 10 enumerated alias mappings — recommend 10 explicit.
- FR-7c-6 enumerates 18 PRODUCTION_GATE_IDS but FR-7c-6's name says "expansion 4 → 14" — recommend 18 final IDs with the count framed as "10 new IDs added on top of pre-existing 4 + 4 dropped during reconciliation" OR "14 new IDs added including 4 already present" — ADR records the canonical math.
- These reconciliations are LOW-RISK (just bookkeeping) but MUST be documented so 7c.20c's 14/14 four-file-lockstep AUDIT has a clear target count.

**File / module placement:**
- `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` — NEW ADR; ~600-1.5K LOC structured markdown.
- `tests/structural/test_adr_0002_slab_7c_gate_taxonomy_present.py` — NEW structural test; ~80-120 LOC.

**K-discipline (from `story-cycle-efficiency.md`):**
- K-target 1.0× = decision-tier band. ADR ~1K LOC + structural test ~100 LOC = ~1.1K LOC. Comfortable.
- If T1 surfaces additional decisions (e.g., the alias-DSL syntax canonicalization is incomplete), surface for K-budget renegotiation; the ADR may grow to ~1.5K but should not exceed.

**Testing standards:**
- Pytest with `-p no:randomly` for deterministic-baseline preservation.
- Structural test only (no unit / integration tests; this is a decision artifact, not implementation).

### Project Structure Notes

- **Alignment with unified project structure:** ADR placement under `docs/dev-guide/adr/<NNNN>-<slug>.md` matches the convention from 7c.0a + prior ADRs. Structural test placement under `tests/structural/` matches existing convention.
- **Detected variances:** None at authoring time. T1.2 verifies ADR slot 0002 is free (or picks next-free).

### References

- [Source: docs/dev-guide/migration-story-governance.json#stories.7c-4a]
- [Source: docs/dev-guide/story-cycle-efficiency.md] (K-discipline; single-gate review policy)
- [Source: _bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md] (alias decision LOCKED at PRD Step 11; FR-7c-6 PRODUCTION_GATE_IDS expansion)
- [Source: _bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md#Story-7c.4a] (Story 7c.4a section starting at line 548)
- [Source: docs/dev-guide/adr/0001-parity-contract-dsl.md] (7c.0a's ADR; alias-DSL clause specification)
- [Source: _bmad-output/implementation-artifacts/migration-7c-0a-decision-foundation.md] (7c.0a spec; predecessor-precedessor)
- [Source: _bmad-output/implementation-artifacts/migration-7c-0b-scaffold-foundation.md] (7c.0b spec — to be authored after 7c.0a closes; predecessor for 7c.4a)

---

## Dev Agent Record

### Agent Model Used

Codex Sonnet 4.5 or later (NEW CYCLE T1-T9 + T10 self-review per `feedback_new_cycle_codex_dev_handoff.md`).

### Debug Log References

- 2026-05-05: Verified 7c.0a and 7c.0b `done` in spec files and `sprint-status.yaml`; ADR slot `0002-slab-7c-gate-taxonomy.md` was free.
- 2026-05-05: Confirmed ADR 0001 / 7c.0b fixed decorator registration but did not expose executable `alias_of`; ADR 0002 therefore ratifies `alias_of` as a forward-compatible clause for 7c.4b.
- 2026-05-05: Ran sandbox-AC validator on 7c.4a spec: PASS.
- 2026-05-05: Ran focused structural test: 5 passed.
- 2026-05-05: Ran ruff on touched structural test: clean.
- 2026-05-05: Ran class-conformance validator: PASS, 11 activation contract files conform.
- 2026-05-05: Ran `lint-imports`: 12 kept, 0 broken.
- 2026-05-05: Ran broad regression: 39 failed, 4063 passed, 27 skipped, 2 xfailed, 11 warnings; failures match the known checkout-level broad-regression red state from stacked prior stories, with no 7c.4a-focused failures.

### Completion Notes List

- Authored ADR 0002 as a decision-only taxonomy lock with five required sections plus G0A -> G1 worked example.
- Resolved alias-count discrepancy by ratifying 10 explicit alias mappings; the older "6 alias gates" count is documented as stale.
- Resolved PRODUCTION_GATE_IDS discrepancy by making the PRD's explicit 18 runtime IDs canonical while keeping the eight family contracts as the four-file-lockstep authoring target.
- Separated runtime IDs from family-story contracts: `G2A` and `G6` remain Wave 2 family contract targets, while FR-7c-6's runtime list remains the explicit 18-ID list.
- Documented `alias_of` syntax as a 7c.4b forward executable addition because 7c.0a/0b did not yet implement an alias clause.
- No production code, pyproject, pipeline manifest, specialist body, or pre-existing ADR was modified.

### File List

- `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` (NEW)
- `tests/structural/test_adr_0002_slab_7c_gate_taxonomy_present.py` (NEW)
