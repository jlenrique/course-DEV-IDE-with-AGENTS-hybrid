---
title: Slab 7c Velocity Amendments
date: 2026-05-04
status: ratified
ratifiedBy: operator (single-vote ratification post-party-mode consultation)
partyModeConsultation:
  date: 2026-05-04
  voices: [John (PM), Murat (TEA), Amelia (Dev), Winston (Architect)]
  topic: "Slab 7c velocity acceleration — 36-story decomposition, 32 stories remaining over 5.5-7 day NEW CYCLE budget"
  outcome: 5 amendments ratified; scope-cut option declined by operator (full 36-story commitment preserved)
amendmentCount: 5
estimatedSavings: ~5-8 hours wall-clock across remaining 32 stories
revisedBudget: "5.5-7 days → 3.5-5 days realistic if all 5 amendments compose"
---

# Slab 7c Velocity Amendments — 2026-05-04

## Executive Summary

After 4 stories closed (7c.0a + 7c.2 done; 7c.0b in-progress; 7c.4a held), operator convened party-mode consultation (John+Murat+Amelia+Winston) on velocity acceleration for the remaining 32 stories. Operator declined scope-cut option (preserving full 36-story slab commitment) and ratified 5 amendments targeting (a) pytest cost reduction, (b) review-tier compression, (c) substrate-freeze cleanup. Estimated combined savings: ~5-8 hours wall-clock across the remainder; revised budget 3.5-5 days from the original 5.5-7.

## Ratified Amendments

### AMEND-V1: Pytest-xdist classification spike (Murat A1; John #3 spike)

**Action:** File new diagnostic story **7c.0c** at `_bmad-output/implementation-artifacts/migration-7c-0c-pytest-xdist-classification.md`. Pts ~3; single-gate; dev-agent-only; dispatched immediately after 7c.0b closes (ahead of 7c.4a — highest amortization leverage; every subsequent T9 benefits).

**Deliverables (per spec):**
1. Run `pytest -n auto --dist loadfile` against full suite; capture wall-clock + pass/fail delta vs serial baseline (3990 passed).
2. For any test that fails under xdist but passes serial, classify failure mode: DB-shared-state / Filesystem collisions / Port-binding / LangSmith trace coupling / Random-seed coupling.
3. Add `@pytest.mark.serial` marker for non-parallel-safe tests; xdist worker count for serial = 1, parallel = auto.
4. Land `pytest.ini` change: default to `-n auto --dist loadfile -m "not serial"` for the parallel pass, then `-n0 -m serial` for the serial pass.
5. Document the safe invocation in `docs/dev-guide/pytest-xdist-classification.md` (or extend existing test-discipline doc).

**Risk delta:** if 50% of suite parallelizes safely on 4-core, 7 min → 3-4 min (~90 min saved across slab); 8-core potentially 2 min. Asymmetric upside even if classification finds 100+ tests need `serial` marker — narrowing the parallel pool still wins.

**Hard precedent:** No "just run xdist on Codex's T9 and hope it works." The classification story is the gate; one-shot diagnostic before adoption.

**Skipped by:** stories that must stay under `-p no:randomly` deterministic baseline (NFR-7c-R2) — those flag `serial` marker.

---

### AMEND-V2: Risk-tiered regression (Murat A2; Amelia/John convergence)

**Action:** Add `r_tier: R1 | R2 | R3` field to `docs/dev-guide/migration-story-governance.json` per-story entries + spec front-matter. Designate at spec-author time; T11 review verifies tier was honored; downgrading R-tier requires party-mode consensus (no ad-hoc downgrades).

**Tier definitions (canonical; copy into governance JSON `r_tier_legend`):**

| Tier | Scope | Wall-clock | Story types |
|---|---|---|---|
| **R1** | Story's own tests + tests in directories the story touches + lint-imports + class-conformance | ~30-90 sec | cp1252-style fixes, single-file scope, prose-only edits, ADR-only stories (7c.4a), structural-test-only stories |
| **R2** | R1 + curated ~200-test smoke suite covering substrate-shape, retrieval contract, party-mode loop, gate-loop kernel, schema validators | ~2-3 min | Most single-gate stories with code changes; HIL surface stories (7c.6..15); Marcus-bound writers (7c.17a/17b); §06B/§07C/§09 surface stories |
| **R3** | Current default — full broad regression (4000+ tests) | ~7 min | dual-gate-cross-agent-CONTRACT-EVOLUTION (7c.5 series), substrate-shape stories (7c.0a/0b/3a), parity-baseline stories (7c.4b), AUDIT-AC stories (7c.20a/b/c), slab-close (7c.21), Epic 3 retirement (7c.21a) |

**Smoke-suite curation (R2 enabling pass-precondition):** file as a one-shot story OR fold into 7c.0c (recommend: fold into 7c.0c — both are diagnostic + add ~1pt). Curate by `pytest --durations=0 --cov` against full suite; take top-200 tests by coverage-per-second; verify they hit substrate, retrieval, party-mode, gate-loop, schema validators. Manifest-pinned at `tests/_smoke_suite_manifest.json` or analogous.

**Provisional R-tier assignments for remaining 32 stories** (operator may amend):

| Story key | r_tier | Rationale |
|---|---|---|
| 7c-0b | R3 | Substrate-shape; dual-gate cross-agent MANDATORY |
| 7c-0c (NEW) | R3 | Diagnostic against full suite is its DELIVERABLE |
| 7c-1 | R3 | DSL refactor; dual-gate substrate-shape |
| 7c-3a | R3 | §02A composer body; dual-gate cross-agent MANDATORY |
| 7c-3b | R2 | Canonical HIL pattern; dual-gate but pattern-author |
| 7c-4a | R1 | Decision-only ADR; no code |
| 7c-4b | R3 | Gate-family base classes; dual-gate cross-agent MANDATORY |
| 7c-5-g0 / g2a / g5 / g6 (4 fresh-author) | R2 | Per-gate four-file-lockstep; new but template-pattern |
| 7c-5-g1 / g2c / g3 / g4 (4 extend-and-audit) | R3 | CONTRACT-EVOLUTION; substrate change |
| 7c-6 / 7 / 8 / 9 / 10 / 11 / 12 / 13 / 14 / 15 (10 HIL surfaces) | R2 | Surface authoring; pattern-replication |
| 7c-17a / 17b | R2 | Marcus-bound writers; sanctum-alignment |
| 7c-18a / 18b / 19 | R2 | §06B/§07C/§09 surfaces |
| 7c-20a / 20b / 20c (3 AUDIT-AC) | R3 | AUDIT verifies shipped substrate; full breadth required |
| 7c-21 | R3 | Slab-close ceremony + 50-run zero-flake |
| 7c-21a | R2 | Epic 3 retirement + live-dispatch wiring |

**Estimated savings:** ~12 stories at R1 (×6 min saved) + ~12 at R2 (×4 min saved) + remainder R3 = ~120 min wall-clock back. Composes multiplicatively with AMEND-V1 if xdist parallelism reduces R3 base cost.

---

### AMEND-V3: T11 review tiering (John #4; Murat T1/T2; Amelia 2-batch)

**Action:** Add `t11_tier: lite | standard | cross-agent` field to governance JSON + spec front-matter. Designate at spec-author time.

**Tier definitions (canonical):**

| Tier | Approach | Wall-clock | Eligibility |
|---|---|---|---|
| **lite** | Spec-checklist review + diff-skim + status flip; reviewer reads Codex T10 self-review notice + AC-by-AC checkbox + diff stats. Layered Blind/Edge/Auditor compressed to a single pass with explicit named checks. | ~10-15 min | AC count ≤5; single-file or sibling-files only; no schema/contract/governance touch; Codex T10 self-review clean (no PATCH/DECISION-NEEDED items raised by Codex); story is single-gate (NOT dual-gate or cross-agent) |
| **standard** | Current 3-layer review shape (Blind / Edge / Auditor); full diff read; verdict artifact at `7c-X-code-review-YYYY-MM-DD.md` | ~25-40 min | Single-gate or dual-gate (NOT cross-agent); fails any lite-eligibility criterion |
| **cross-agent** | MANDATORY full-fresh-context review per governance JSON `cross_agent_review_required: true`. Blind/Edge/Auditor explicitly tagged in verdict artifact. NEVER batched. | ~30-50 min | governance JSON `cross_agent_review_required: true` |

**Batching rule (Amelia AMEND-Velocity-7):** Two `lite`-tier reviews CAN be batched in one Claude session IF (a) the two stories' `files_touched` are path-disjoint, (b) the second review starts with an explicit context-reset prompt ("New review. Prior story closed. Story key: 7c.X. Files: ..."), (c) verdict artifacts are written separately. Cap at 2-per-session; 3+ risks reviewer drift. NEVER batch standard or cross-agent.

**Provisional t11_tier assignments:**
- **cross-agent (5 stories):** 7c-0a (closed), 7c-0b (in-progress), 7c-3a, 7c-4b, 7c-21
- **standard (most others; default):** 7c-1, 7c-3b, 7c-4a, 7c-5.G* (8 stories), 7c-15 (heavier; AMEND-4 dual-FR), 7c-21a, 7c-20a/b/c
- **lite (likely-eligible; verify per story at spec-author time):** 7c-2 (already done; would have been lite in retrospect), 7c-6/7/8 (HIL pattern-replication), 7c-17a/17b (sanctum-alignment templated), 7c-18a/18b/19, possibly 7c-9-12 G2C-aliased Wave-3 if their AC counts are tight

**Estimated savings:** ~10-15 stories qualify lite at ~25-30 min saved each = **4-7 hrs reclaimed**. Batching saves additional ~10 min per batched pair on context-spin-up.

---

### AMEND-V4: AMELIA-P3 staggering — auto-satisfied under single-Codex (Winston)

**Action:** AMELIA-P3 dispatch_staggering blocks (currently `binding=hard`, `minimum_offset_minutes=30`) on 7c-9 / 7c-10 / 7c-11 / 7c-12 are MARKED AUTO-SATISFIED under single-Codex execution mode. The block stays structurally present in governance JSON for forward-compatibility; an `auto_satisfied_under: "single_codex_dispatch"` annotation indicates the constraint is non-binding under current execution model.

**Reinstatement trigger:** if multi-Codex parallelism is later adopted (currently declined as Tier-A skip per operator), AMELIA-P3 reactivates with the original 30-min stagger.

**Rationale (Winston):** Codex single-thread dispatch automatically serializes the four G2C-aliased stories at ~Codex-cycle-time (≥30 min in practice given T9 broad-regression + T10 self-review costs); the explicit gate is non-binding and a coordination cost that costs nothing to drop.

**Net:** No wall-clock saved directly; removes governance friction + clarifies operator dispatch decision-making.

---

### AMEND-V5: Spec-author lookahead — Tier 1/2/3 (Winston AMEND-Velocity-4; Amelia N+2 cap)

**Action:** Codify lookahead authoring discipline. Add `lookahead_tier: 1 | 2 | 3` field to governance JSON per-story entries.

**Tier definitions:**

| Tier | When safe to author | Authoring depth | Examples |
|---|---|---|---|
| **1 — Author-ahead-aggressively** | Spec depends only on closed substrate; PRD-locked OR known-pattern-replication | Full spec + Codex dev-prompt; mark dispatch HELD until predecessor closes | 7c.4a (PRD-locked taxonomy); 7c.6/7/8 (G1-aliased HIL pattern from 7c.3b); 7c.17a/17b (Marcus-bound writers; sanctum-alignment from 7c.0b) |
| **2 — Author-skeleton-ahead** | Spec depends on substrate currently in dev | AC scaffolding + T-task structure + dispatch criteria with `<TBD-when-7c.X-closes>` placeholders for substrate-dependent signatures | 7c.5.G* extend-and-audit stories (depend on 7c.4b base classes); 7c.20a/b/c AUDIT-ACs (depend on 7c.0b/0a substrate confirmation) |
| **3 — Hold** | AC shape genuinely contingent on unresolved substrate semantics | Do NOT pre-author beyond placeholder spec key in governance JSON | 7c.4b (depends on 7c.4a's exact taxonomy resolution); cross-agent MANDATORY stories where party-mode contract negotiation has not occurred |

**Hard cap:** Pre-author N+2 max (where N = current in-flight Codex story); N+3 only if path-disjoint AND cites zero in-flight artifacts in Required Readings. Prevents rework cost on stale spec exceeding spec-author cost.

**Cross-agent MANDATORY pre-flight (Amelia AMEND-Velocity-5):** For the 5 cross-agent MANDATORY stories (7c.0a/0b/3a/4b/21), conduct a 15-min Claude-internal contract-negotiation pass at spec-author time (not full party-mode; lighter-touch). Goal: lock contract shape BEFORE Codex T1 dispatch. T11 cross-agent review then collapses to verification, not negotiation. Saves ~1 review cycle per cross-agent story.

**Net:** No direct wall-clock savings; eliminates "Codex waiting on Claude" gaps between stories. Codifies de facto practice (7c.4a was authored ahead) for consistency.

---

## Summary table

| Amend | Action | Saved (per story / total) | Risk | Status |
|---|---|---|---|---|
| V1 | xdist diagnostic story 7c.0c | ~3-5 min/story × 30 = 1.5-2.5 hrs | Medium (state-coupling discovery) | RATIFIED |
| V2 | R-tier regression (R1/R2/R3) | ~4-6 min/story on R1/R2 stories = ~2 hrs | Low (conservative defaults) | RATIFIED |
| V3 | T11 tiering (lite/standard/cross-agent) + 2-batch | ~25-30 min on lite stories = 4-7 hrs | Low (batching trial-revert if drift) | RATIFIED |
| V4 | P3 auto-satisfied annotation | governance cleanup; ~0 wall-clock | Zero | RATIFIED |
| V5 | Lookahead Tier 1/2/3 + cross-agent pre-flight | reclaims Codex-wait gaps; ~0-30 min/story | Low (rework cap = N+2) | RATIFIED |

**Combined estimated savings:** ~5-8 hrs wall-clock across remaining 32 stories.
**Revised budget:** 5.5-7 days → **3.5-5 days realistic** if amendments compose as expected.

## Skipped (declined by operator OR mid-priority)

- **Scope-cut triage** (John AMEND-Velocity-1): operator declined; full 36-story commitment preserved.
- **Multi-Codex parallelism** (Amelia AMEND-Velocity-2 / John AMEND-Velocity-7): risk > reward without scope cut; collision-debug cost on shared files (sprint-status.yaml writes, governance JSON, deferred-inventory) higher than xdist + R-tier savings. Re-evaluate ONLY if Tier A+B underdelivers.
- **Rolling parity canary toward 7c.21 cumulative credit** (Murat AMEND-Velocity-3): worth landing but mid-priority; doesn't accelerate next 30 stories' close cycle. File as Slab-Close-Required follow-on if 7c.21 budget tightens.
- **Cross-agent MANDATORY relaxation** (Winston AMEND-Velocity-6): re-examine 7c.3a + 7c.21 at each story's spec-author time; not pre-emptively.
- **Gate-mode demotion audit** (John AMEND-Velocity-9): naturally happens during scope review; deferred since scope is preserved.

## Governance JSON delta (applied 2026-05-04)

```yaml
# new top-level fields:
r_tier_legend:
  R1: "Focused + impact-zone (~30-90 sec)"
  R2: "Focused + impact-zone + cross-cutting smoke (~2-3 min)"
  R3: "Full broad regression (~7 min)"

t11_tier_legend:
  lite: "Spec-checklist + diff-skim + status flip (~10-15 min); single-gate ≤5 ACs single-file no schema/contract/governance touch"
  standard: "3-layer Blind/Edge/Auditor (~25-40 min)"
  cross-agent: "MANDATORY full-fresh-context (~30-50 min); never batched"

lookahead_tier_legend:
  1: "Author-ahead-aggressively; PRD-locked or known-pattern"
  2: "Author-skeleton-ahead; substrate-in-flight; placeholders OK"
  3: "Hold; AC contingent on unresolved substrate"

velocity_amendment_record:
  date: 2026-05-04
  party_mode_consultation: "John+Murat+Amelia+Winston"
  ratified: [V1, V2, V3, V4, V5]
  declined: [scope-cut, multi-Codex, rolling-canary, gate-mode-demotion-audit]
  estimated_savings_hours: "5-8"
  budget_revision: "5.5-7d → 3.5-5d"

# per-story:
stories:
  7c-X:
    r_tier: R1 | R2 | R3        # NEW field
    t11_tier: lite | standard | cross-agent  # NEW field
    files_touched: [path1, path2, ...]   # NEW field; declared at spec-author time
    lookahead_tier: 1 | 2 | 3   # NEW field
    # ... existing fields ...
```

## Spec-author template updates

Every NEW Slab 7c spec authored from 2026-05-04 forward MUST include in front-matter:

```markdown
**R-tier (regression scope):** R1 / R2 / R3 — rationale: ...
**T11-tier (review approach):** lite / standard / cross-agent — rationale: ...
**Files touched (declared):**
- path/1
- path/2
- ...
**Lookahead tier:** 1 / 2 / 3 (at spec-author time)
```

`files_touched` is the source-of-truth for AMEND-V3 batching eligibility (path-disjoint check) AND replaces AMELIA-P1 hash-allowlist enforcement (deleted at 7c.2 T11 close per `7c-2-code-review-2026-05-04.md` patch P-1).

## Codex-dev-prompt template updates

Every NEW codex-dev-prompt authored from 2026-05-04 forward MUST include in T9 verification battery section:

```bash
# T9 verification battery — R-tier dependent:
# R1 (focused + impact-zone):
.venv/Scripts/python.exe -m pytest <focused-tests> <impact-zone-tests> -p no:randomly -q --tb=short
.venv/Scripts/lint-imports.exe
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/

# R2 (R1 + smoke suite):
.venv/Scripts/python.exe -m pytest @tests/_smoke_suite_manifest.json -p no:randomly -q --tb=short
# (then R1 commands above)

# R3 (full broad regression):
.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line
# (post-7c.0c xdist adoption: defaults shift to -n auto --dist loadfile -m "not serial" + serial pass)
```

## Memory entry updates

- New: `feedback_velocity_amendments_slab_7c_2026_05_04.md` — codifies r_tier + t11_tier + lookahead_tier conventions; supersedes/refines NEW CYCLE feedback entry where applicable.
- Update: `project_slab_7c_amelia_p3_auto_satisfied.md` — records P3 marked auto-satisfied under single-Codex.

## Execution order (immediate)

1. ✅ This artifact authored (2026-05-04).
2. Apply governance JSON delta (add 3 legends + velocity record + per-story field schema; bump version to `2026-05-04-velocity-amendments-bundle`).
3. Backfill 7c.4a spec front-matter with new fields (r_tier=R1, t11_tier=standard or lite per AC count audit, files_touched declared, lookahead_tier=1).
4. Author 7c.0c xdist-classification spec + Codex prompt; flip to ready-for-dev with dispatch held until 7c.0b closes.
5. Update memory entries.
6. Commit bundle.
7. (Future) Codex 7c.0c is the FIRST story dispatched after 7c.0b closes — ahead of 7c.4a per highest amortization leverage; xdist learnings amortize across ALL subsequent T9 runs.

---

## V6 + V7 Amendments — Party-Mode 2026-05-05 (3-round resolution post-G1-close)

Convened mid-Slab-7c after 14 stories closed (G0+G2A+G5+G6 fresh-author batches; G1 first extend-and-audit). Two open questions surfaced by G1 T11 review (process-finding) and forward-cadence planning. Voices: John+Winston+Murat+Amelia. Orchestrator: Claude. Three rounds; cross-flip dynamic in R3 (Winston conceded to Murat's R2 epistemic argument; Murat simultaneously flipped to Winston's R2 risk-math argument). Final tally: Q1 UNANIMOUS; Q2 majority 3-1 with documented Murat dissent.

### AMEND-V6: AMELIA-P5 DROP-row Heavy gate + Winston per-row audit_method qualifier composition (Q1 UNANIMOUS)

**Trigger:** G1 T6 reversal on `drafted_proposal` + `evidence` — T1 audit declared "drop because no audited consumer reads after construction"; T6 broad regression revealed live consumers exercised at smoke/integration time (composition tests + replay regression + integration runner threads). Codex correctly reversed mid-flight; both fields preserved as direct G1 fields. Static-grep-only audits are blind to `**common` splat propagation, adapter dispatch via `getattr(target, field_name)`, and runtime-typed registries — the 20% tail where production incidents live.

**Action:** Codify in `docs/dev-guide/migration-story-governance.json::extend_and_audit_t1_audit_method` (binding=hard validator rule).

**Schema:** Contract-diff §2 (Legacy DecisionCard Base Field Disposition) carries per-row `audit_method: heavy|light` qualifier. DROP rows REQUIRE `audit_method=heavy` with smoke-pass evidence against `tests/composition/` + `tests/integration/marcus/` + `tests/integration/replay/`. ADD-only / RENAME-only rows can use `audit_method=light` freely. Validator REJECTS DROP+light/missing combination.

**T1 smoke-pass protocol:** `pytest tests/composition/ tests/integration/marcus/ tests/integration/replay/ -k <field_name> --co -q` collect-only run lists tests exercising the field name. Zero collected → DROP confirmed. ≥1 collected → execute; pass → confirmed; fail → DROP REJECTED, field must preserve-via-re-declaration. Generic field names supplemented by targeted grep for `card\.<field_name>` or `getattr\(.*, ['"]<field_name>\b` patterns.

**Cost:** ~6-13 min added per DROP-bearing T1 (vs flat-BOTH 30-45 min). Cost amortizes to where risk lives.

**Composition with Winston's per-row qualifier:** AMELIA-P5 + audit_method are **orthogonal axes** — AMELIA-P5 decides WHETHER Heavy fires (DROP-gated); audit_method qualifier decides WHAT SHAPE the audit takes (heavy=smoke-verified; light=static-grep-only). One rule, two compositions.

**Discarded:**
- John's R1 reviewer-discretion + common-token flag list (John conceded R2: "reviewer-discretion + hand-curated tokens is more brittle than DROP-row automation").
- Murat's R1 flat-BOTH (Murat conceded R2: "I withdraw flat-BOTH and adopt AMELIA-P5 as my Q1 position. Strong opinion weakly held — Amelia's gating is structurally better").

**Winston-rider (instrumentation):** Track DROP-row prevalence across next 5-8 G2C/G3/G4 T1s. Threshold: 0.60. If aggregated prevalence > 60%, AMELIA-P5 collapses into uniform-tax territory and warrants v2 audit-method policy.

**Ratification:** UNANIMOUS (John+Winston+Murat+Amelia, R3 close).

### AMEND-V7: Wave-3 lookahead-cap policy v1 + v2 promotion rule (Q2 majority 3-1; documented Murat dissent)

**Trigger:** Forward-cadence planning post-G1-close. 3 extend-and-audit remaining (G2C/G3/G4 serial); 10 Wave-3 HIL stories largely path-disjoint via C6 import-linter contract; 8+ Wave-4/5/6 stories. Question: should Wave-3 entry bump cap from N+2 (V5) to N+3 immediately, or wait for empirical baseline?

**Action:** Codify in `docs/dev-guide/migration-story-governance.json::wave_3_lookahead_policy` (compose with V5 hard_cap).

**v1 (immediate, ratified now):**
- `default_cap: 2` (status quo from V5)
- `elevation_gate: "P2_clean_x3_at_G4_close"` — after Slab 7c.5.G4 closes (last extend-and-audit) AND AMELIA-P2 freshness check has run clean on three consecutive consumed pre-auths under N+2 cap, elevation to N+3 unlocks
- `elevated_cap: 3`
- 7c.6 dispatches under N+2 cap (ratified by majority 3-1; Murat dissent documented)

**v2 (steady-state, post-baseline ≥3 Wave-3 closures):**
- Murat's triple-condition (C6 ∧ lookahead_tier=1 ∧ t11_tier=lite) replaces P2_clean_x3 as steady-state cap-elevation predicate. At slab-open or wave-open, evaluate the triple; if true, default cap is N+3 for that wave/slab.
- Ratification path: Requires party-mode consensus + version bump per CLAUDE.md gate-mode-change rule. Empirical baseline (≥3 Wave-3 closures under v1) is the input; party-mode validates whether triple-condition holds against the observed coupling pattern.

**Documented Murat dissent (R3 final):** Risk math 3.5 min expected staleness rework (0.175 coupling-probability × ~20 min spec-patch) vs 40-60 min deterministic foregone parallelism across 7c.6/7c.7/7c.8 under N+2 default. Murat flipped to Winston's R2 a-priori-entry position based on the cost asymmetry. Strong opinions weakly held. **Revisit trigger:** if empirical N+2 conservatism produces >40 min net cost across 7c.6/7c.7/7c.8 closures, operator can exercise (E)-elasticity to bump to N+3 case-by-case OR retroactively ratify Murat's R3 position as v1.5.

**Operator (E)-elasticity authority retained:** All 4 voices (UNANIMOUS) ratified (E) operator-elasticity as the umbrella framework. Operator may override the N+2 default at slab-opener party-mode for path-disjoint waves with clear C6/lookahead_tier=1/t11_tier=lite triple. This is Murat's risk-math argument operationalized as escape valve.

**R3 cross-flip dynamic (process-noteworthy):**
- Winston (R3) conceded to Murat's R2 epistemic argument: "Murat's epistemic frame is correct... evaluable a-priori ≠ calibrated... policy follows data."
- Murat (R3) flipped to Winston's R2 risk-math argument: "I withdraw the empirical-first objection... 3.5 min expected vs 40-60 min deterministic. Not close."
- John + Amelia held empirical-first; final tally 3-1 for empirical-first.

**Ratification:** Majority 3-1 (John + Winston + Amelia for empirical-first; Murat for a-priori-entry). Documented dissent + revisit trigger.

### Execution at this commit

1. ✅ Governance JSON updated (V6 + V7 blocks added; version → `2026-05-05-amelia-p5-and-wave-3-lookahead-policy`).
2. ✅ G2C + G3 Codex prompts updated with AMELIA-P5 §audit_method requirement at T1 (smoke-pass protocol embedded).
3. ✅ G2C + G3 specs updated with AC-A bullet 1 contract-diff §2 row schema (audit_method qualifier per row).
4. ✅ Deferred-inventory follow-on `audit-pattern-T1-smoke-elaboration-for-extend-and-audit` marked CLOSED via V6 ratification.
5. ✅ This artifact appended (V6 + V7 history).
6. ✅ Commit bundle.

Codex G2C dispatch is unblocked post-this-commit.
