# Codex dev-story prompt — Story 7c.4a (Gate-Family Taxonomy Ratification — decision-only ADR)

**Cycle:** Claude spec → Codex T1-T6 + T10 self-review → Codex drops `_bmad-output/implementation-artifacts/_codex-handoff/7c-4a.ready-for-review.md` → Claude T11 `bmad-code-review` (single-gate; cross-agent NOT mandatory) → Claude commit + flip done.
**Wave:** 2 slot 1 (decision-tier; precedes 7c.4b foundation; gates 7c.5.G0..G6 per-gate stories).
**Pre-authored:** 2026-05-04 ahead of operator dispatch per `feedback_new_cycle_codex_dev_handoff.md` lookahead-discipline revision.

**🚨 DISPATCH HELD — PREDECESSOR-GATED.** Do NOT dispatch this prompt to Codex until **BOTH** of the following are TRUE:
- `migration-7c-0a-decision-foundation` status = `done` in BOTH the spec file AND `sprint-status.yaml`.
- `migration-7c-0b-scaffold-foundation` status = `done` in BOTH the spec file AND `sprint-status.yaml`.

7c.0a is currently in Codex dev (2026-05-04). 7c.0b spec authoring opens after 7c.0a closes. 7c.4a dispatch unblocks after 7c.0b closes. Estimated dispatch window: ~2-3 dev-days from this authoring date.

**AMELIA-P2 freshness check:** at dispatch time, Claude re-diffs `migration-7c-4a-gate-family-taxonomy-ratification.md` (spec) against this prompt; if spec hash changed, Claude regenerates this prompt before dispatch. Critical reasons spec might change before dispatch: 7c.0a's ADR resolved the alias-DSL syntax differently than recommended; 7c.0a re-numbered its ADR (cascading 7c.4a's slot from 0002 to next-free); the alias-count or PRODUCTION_GATE_IDS final-count discrepancy was resolved upstream.

---

```
Run bmad-dev-story on Story 7c.4a (Slab 7c Wave 2 slot 1; single-gate; gate-family taxonomy ratification = decision-only ADR + structural test).

## Required reading (read in order)

1. Story spec: `_bmad-output/implementation-artifacts/migration-7c-4a-gate-family-taxonomy-ratification.md` (status: ready-for-dev; 2 ACs A-B; 6 tasks T1-T6; you own T1-T5).
2. Slab 7c PRD: `_bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md` — alias decision LOCKED at PRD Step 11 per Amelia A3 (search the document for "alias decision" + "Step 11").
3. Slab 7c epics: `_bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md` (Story 7c.4a section starting at line 548; AMEND-5 fresh-author vs extend-and-audit split).
4. **Predecessor 7c.0a's ADR**: `docs/dev-guide/adr/0001-parity-contract-dsl.md` — alias-DSL clause specification. **READ THIS FIRST**; 7c.4a ratifies the taxonomy that consumes the alias-DSL clause from 7c.0a.
5. **Predecessor 7c.0b's deliverables** (informational): the executable parity-DSL scaffold under `app/parity/contracts/` (existence verifies 7c.0b closed cleanly).
6. Required readings:
   - `docs/dev-guide/story-cycle-efficiency.md` (K-discipline; single-gate review policy).
7. Governance JSON: `docs/dev-guide/migration-story-governance.json` story `7c-4a` (single-gate; expected_pts=1; expected_k_target=1.0; prerequisite_stories=[7c-0b]).
8. Sandbox-AC inventory: `docs/dev-guide/migration-ac-sandbox-inventory.json`.
9. FR-7c-6 enumeration of PRODUCTION_GATE_IDS post-expansion (read directly from PRD §FR-7c-6).
10. Pre-Slab-7c PRODUCTION_GATE_IDS: 4 gates {G1, G2C, G3, G4} per Slab 7a substrate (verify at `app/manifest/compiler.py` or analogous architecture path; 7a.2 manifest fold-flags substrate).

## T1 hard checkpoints (HALT-AND-SURFACE if violated)

- 7c.0a status `done` in spec file line 3 AND sprint-status.yaml::development_status['migration-7c-0a-decision-foundation']. **Both must be TRUE before T1 begins.**
- 7c.0b status `done` in spec file line 3 AND sprint-status.yaml::development_status['migration-7c-0b-scaffold-foundation']. **Both must be TRUE before T1 begins.** If either 7c.0a or 7c.0b is NOT done, HALT immediately and report to operator (this prompt should not have been dispatched).
- ADR slot `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` is FREE. If 7c.0a's ADR re-numbered (its own slot 0001 was occupied), 7c.4a's slot may have cascaded — pick next-free index (e.g., 0003 or 0004) and document.
- 7c.0a's ADR canonicalized the alias-DSL syntax (decorator vs YAML; per-surface declaration schema). If 7c.0a's ADR left this OPEN as a "downstream story implements" placeholder, surface as `decision_needed` and 7c.4a's ADR proposes the canonical syntax.
- Alias-count discrepancy resolution: epic Story 7c.4a section says "6 alias gates" but enumerates 10 mappings (G0A/G0B/G1A → G1; G2B/G2M/G2.5/G2F → G2C; G3B → G3; G4A/G4B → G4). RECOMMEND ratifying 10 explicit mappings; "6" is a stale count. Surface as `decision_needed`.
- PRODUCTION_GATE_IDS final-count: FR-7c-6 enumerates 18 IDs post-expansion (`{G0, G0A, G0B, G1, G1A, G1.5, G2, G2B, G2C, G2M, G2.5, G2F, G3, G3B, G4, G4A, G4B, G5}`); the FR title says "expansion 4 → 14". Reconcile in the ADR; recommend documenting BOTH the 18 enumerated IDs AND the framing "10 NEW IDs added on top of 4 pre-existing + reconciliation note that 4 of the 14 'new' are alias-collapsed".

## Files in scope

**New (2 files):**
- `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` — ADR with 5 required sub-sections (net-new families + alias gates + alias-DSL inheritance + PRODUCTION_GATE_IDS expansion + status line) + 1 worked example per AC-7c.4a-B (G0A → G1 alias inheritance demonstration). ~600-1.5K LOC structured markdown.
- `tests/structural/test_adr_0002_slab_7c_gate_taxonomy_present.py` — path-existence assertion + 5 sub-section heading assertions + worked-example heading assertion. Substantive-keyword regex (do NOT match exact heading strings). ~80-120 LOC.

**Modified (0 files):** 7c.4a is decision-only; no production code or pre-existing ADR is modified.

**Do NOT modify:**
- `docs/dev-guide/adr/0001-parity-contract-dsl.md` (7c.0a's ADR — reference only; 7c.4a consumes its alias-DSL clause but does NOT amend it).
- Any production code under `app/`.
- `pyproject.toml` (no import-linter changes).
- Any specialist body (`app/specialists/**`).
- Any HIL surface module (`app/gates/**`).
- `state/config/pipeline-manifest.yaml` (this is decision-tier; pipeline-manifest is unchanged at 7c.4a).
- Any AMELIA-P1 path-isolation forbidden-paths-set entry (the guard remains active; 7c.4a's ADR is on the SAFE side of the boundary).

## Critical implementation notes

- **K-target 1.0× ≈ ~1.1K LOC ceiling.** ADR ~1K + structural test ~100 = ~1.1K LOC. Comfortable.
- **Single-gate** — Claude T11 review is mandatory but cross-agent NOT mandatory. Codex T10 self-review is supplemental.
- **Decision-only artifact.** No Python code lands. The ADR is the deliverable.
- **Resolve count discrepancies in the ADR explicitly** — these are the 7c.4a story's reason for being. Downstream 7c.5.G0..G6 + 7c.20c need an unambiguous count.
- **Alias-DSL syntax MUST come from 7c.0a's ADR** (or be proposed in 7c.4a's ADR with forward-pointer if 7c.0a left it open).
- **Worked example for AC-7c.4a-B**: pick G0A → G1 alias mapping. Show the full DSL invocation pattern + how four-file-lockstep AUDIT routes from G0A to G1's four files + how runtime DecisionCard emission for G0A inherits G1's `DecisionCardMeta.cache_state`.
- **No new third-party deps.** Standard markdown + pytest.

## Verification battery (T9 — implicit at T4 in spec)

```bash
# Focused tests (1 new test file):
.venv/Scripts/python.exe -m pytest tests/structural/test_adr_0002_slab_7c_gate_taxonomy_present.py -p no:randomly -q --tb=short

# Broad regression slice (NFR-7c-R2; preserve ≥1403 deterministic baseline):
.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line

# Class-conformance validator (NFR-7c-R5; expect 11 conforming activation contracts; no regression):
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/

# Import-linter (KEPT count UNCHANGED from pre-7c.4a baseline; 7c.4a does NOT add or modify import-linter contracts):
.venv/Scripts/lint-imports.exe

# Sandbox-AC validator (NFR-7c-M5):
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-4a-gate-family-taxonomy-ratification.md

# Ruff hygiene on the touched files:
.venv/Scripts/python.exe -m ruff check tests/structural/test_adr_0002_slab_7c_gate_taxonomy_present.py
```

Expected post-7c.4a baseline:
- ≥1403 broad-regression deterministic baseline preserved (no test regression introduced).
- `lint-imports` KEPT count UNCHANGED (7c.4a does not modify contracts).
- `validate_parity_test_class_conformance.py` reports 11 conforming activation contracts.
- Sandbox-AC validator PASS.
- Ruff CLEAN on the 1 touched test file.

## T10 + T11

**T10:** Codex G6 self-review (Blind / Edge / Auditor) at `_bmad-output/implementation-artifacts/_codex-handoff/7c-4a.ready-for-review.md`. Per dropbox protocol — drop the completion notice. Flip story status `in-progress` → `review` in the spec file.

Critical content for the T10 self-review notice:
- File list (2 NEW files; 0 modified).
- Test counts (broad regression delta; structural test pass count).
- Sandbox-AC validator status.
- T1 resolutions: alias-count (recommend 10), PRODUCTION_GATE_IDS final count (recommend 18 enumerated), alias-DSL syntax (consumed from 7c.0a's ADR or proposed forward-pointer).
- Deferred follow-ons surfaced.

**T11:** Claude (separate cold context from Codex dev) does FINAL `bmad-code-review` (single-gate; cross-agent NOT mandatory but Claude review remains mandatory per BMAD sprint governance §3). Review verdict lands at `_bmad-output/implementation-artifacts/7c-4a-code-review-2026-05-NN.md`. Claude applies remediation cycles if HALT-AND-REMEDIATE; commits the diff (2 NEW files); flips `migration-7c-4a-gate-family-taxonomy-ratification: review → done` in sprint-status.yaml.

## Boundary

- **HALT and surface to operator on:**
  (a) 7c.0a OR 7c.0b status NOT `done` (this prompt was dispatched too early).
  (b) ADR slot 0002 collision unresolved.
  (c) 7c.0a's ADR did NOT canonicalize the alias-DSL syntax AND there is no clear "downstream proposes" forward-pointer — design ambiguity surface.
  (d) The alias-count discrepancy or PRODUCTION_GATE_IDS final-count cannot be resolved without an upstream PRD amendment — surface for party-mode adjudication.
  (e) K-actual exceeds 1.7× target (~1.9K LOC) — surface for K-budget renegotiation; ADR scope likely too broad.
  (f) ANY sandbox-AC violation — should not happen given dev-agent-only ACs.
  (g) Broad-regression delta < 0 (any pre-existing test regresses) — investigate.
  (h) `lint-imports` KEPT count changes from baseline — 7c.4a should NOT touch import-linter contracts.

- **Do NOT touch:**
  - Any production code under `app/` (decision-only story).
  - `docs/dev-guide/adr/0001-parity-contract-dsl.md` (7c.0a's ADR — read only).
  - `pyproject.toml`.
  - Any specialist body, HIL surface module, pipeline-manifest.

- **Do NOT introduce:**
  - New Pydantic models (those are 7c.4b's territory).
  - Executable DSL primitives (those are 7c.0b's territory).
  - Any code that imports from `app.parity.contracts` or `app.models.tripwire_ledger` (7c.4a is decision-only; no implementation).
  - New third-party deps.
```

---

## Operator dispatch checklist (before sending this prompt to Codex)

1. ☐ Verify `migration-7c-0a-decision-foundation: done` in BOTH spec file AND sprint-status.yaml.
2. ☐ Verify `migration-7c-0b-scaffold-foundation: done` in BOTH spec file AND sprint-status.yaml.
3. ☐ AMELIA-P2 freshness check: Claude re-diffs `migration-7c-4a-gate-family-taxonomy-ratification.md` against this prompt; if spec hash changed since 2026-05-04 authoring, regenerate this prompt before dispatch.
4. ☐ Run `.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-4a-gate-family-taxonomy-ratification.md` → expect PASS.
5. ☐ Verify governance JSON entry for 7c-4a is current (single-gate; K=1.0; pts=1; prerequisite_stories=[7c-0b]) — locked at v2026-05-04-slab7c-thirty-six-stories.
6. ☐ Confirm sprint-status.yaml shows `migration-7c-4a-gate-family-taxonomy-ratification: ready-for-dev`.
7. ☐ Verify ADR slot `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` is free at dispatch time.
8. ☐ Dispatch this prompt to Codex; Codex flips status `ready-for-dev → in-progress` at T1 start.

## Post-Codex-T10 dropbox-watch protocol

1. ☐ Codex drops `_bmad-output/implementation-artifacts/_codex-handoff/7c-4a.ready-for-review.md` upon T10 completion.
2. ☐ Claude (separate cold context) reads the dropbox notice + the 2-file diff; runs `bmad-code-review` (T11; single-gate).
3. ☐ Claude applies remediation cycles per HALT-AND-REMEDIATE if any.
4. ☐ Claude commits + flips `migration-7c-4a-gate-family-taxonomy-ratification: review → done` in sprint-status.yaml.
5. ☐ At 7c.4a close, **7c.4b unblocks** (foundation implementation; consumes the taxonomy ratified here). 7c.4b in turn unblocks 7c.5.G0..G6 (8 per-gate four-file-lockstep stories). The Wave 2 cascade opens.
