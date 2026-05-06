# Migration Story 7c.20a: AUDIT-AC ≥20 Shape-Pins + ≥11 Class-Conformance (FR-7c-34 + FR-7c-36)

**Status:** ready-for-dev *(spec authored 2026-05-06 lookahead_tier=2 per governance JSON; predecessors 7c.1 + 7c.4b + 7c.5.G0..G6 all DONE — story fully unblocked at this commit. Story is verification-only — runs the AUDIT against shipped substrate; files gaps as TW-7c-1 follow-ons if gap-rate exceeds AMEND-7c threshold.)*
**Sprint key:** `migration-7c-20a-audit-ac-shape-pins-class-conformance`
**Epic:** Slab 7c — Marcus Orchestrational Tail
**Pts:** 2
**K-target:** 1.2×
**Estimated LOC:** ~250 (AUDIT test module ~150 + gap-discovery helper ~50 + tripwire-ledger entry on TW-7c-1 fire ~50; AUDIT-not-BUILD framing — minimal new code surface)
**Gate-mode:** single-gate
**Cross-agent review:** false
**R-tier:** R3 (broader regression discipline; AUDIT touches structural test surface)
**T11-tier:** standard (per governance JSON entry `7c-20a`; AUDIT-AC discipline + tripwire-ownership + gap-discovery rigor)
**Lookahead-tier:** 2
**files_touched:** 1 new + 0 modified (single AUDIT test module under `tests/audit/`)
**Tripwire ownership:** TW-7c-1 (gap-fill detection)

---

## Story

As the test-architect,
I want to verify that ≥20 shape-pin tests on parity-DSL surfaces + ≥11 class-conformance assertions are green at slab-close, verifying original Epic 3 stories 3.2 + 3.4 against the shipped Slab 7c substrate,
So that AUDIT-AC compresses Slab 7c's net-new build to coverage-only audit per the AUDIT-not-BUILD framing — confirming the substrate already shipped + filing gap-fill follow-ons for any deficits via TW-7c-1.

This is **NOT a net-new-build story** — it runs the AUDIT against existing tests + asserts coverage floors. If gap-rate exceeds the AMEND-7c percentage threshold (≥4 gaps = 10% of combined floor 31), TW-7c-1 fires (high severity); STOP; party-mode-consensus on absorb-vs-defer per gap; gap-fill follow-ons file as `7c.X.<descriptor>` entries.

---

## Predecessor / Dependency Context

- **7c.1** (CLOSED `2026-05-04`): parity-contract DSL foundation — 8 transport-parity test files registered via parity_contract DSL with sentinel pattern; structural pins.
- **7c.4b** (CLOSED `2026-05-05`): gate-family foundation implementation — D1-D8 contract compliance verified line-by-line; D5 C6 contract type pivot to `independence` (post-P-1 patch); 12 KEPT lint-imports.
- **7c.5.G0..G6** (ALL CLOSED `2026-05-05`): 7-DecisionCard family migration to DecisionCardBase — G0/G1/G2A/G2C/G3/G4/G5/G6; 4-class-regime taxonomy; class-conformance baseline at 19 (11 activation + 8 decision-card shape-pin).
- **Wave 3-5 closes** (ALL CLOSED `2026-05-05/06`): HIL surfaces (7c.6/7/8/9/10/11/12/13/14 + 7c.18a/b + 7c.15 §11B/§15 dual-FR fold) shipped 11+ §section packages; OperatorVerdict variants per family; 3-transport schema-stability shape-pins.
- **`tests/parity/test_decision_card_*.py` (existing)**: shape-pin tests on G0/G1/G2A/G2C/G3/G4/G5/G6 DecisionCard families. Pre-7c.20a count (per shipped class-conformance validator): 8 decision-card shape-pin files + 11 activation contracts = 19 total.
- **Combined floor 31** = 20 shape-pins on parity-DSL surfaces (G1/G2C/G3/G4/Override × {field-presence, closed-enum red-reject, JSON-Schema emission, golden-fixture round-trip}) + 11 class-conformance assertions per current activation-contract validator floor.

---

## Acceptance Criteria

### AC-7c.20a-A — Shape-pin coverage AUDIT (FR-7c-34; ≥20)

**Given** the shipped substrate (DecisionCard families + Override + 5 schemas) + existing shape-pin tests under `tests/parity/test_decision_card_*.py` and `tests/schemas/operator_verdict/`
**When** the dev-agent authors `tests/audit/test_audit_ac_shape_pins_class_conformance.py` + runs the AUDIT
**Then**:
1. The AUDIT discovers parity-DSL shape-pin tests via pytest collection (introspection or filesystem-glob — T1-T9 decision; preferred: `pytest --collect-only -q tests/parity/ tests/schemas/operator_verdict/` parsing).
2. The AUDIT asserts the shape-pin count ≥ **20** (G1/G2C/G3/G4/Override × {field-presence, closed-enum red-reject, JSON-Schema emission, golden-fixture round-trip} = 5 × 4 = 20 minimum).
3. Gap-fill discovery for any (family, dimension) pair NOT covered by an existing shape-pin file is reported in the AUDIT verdict (per-gap descriptor + family + dimension).

### AC-7c.20a-B — Class-conformance coverage AUDIT (FR-7c-36; ≥11)

**Given** the activation-contract validator at `scripts/utilities/validate_parity_test_class_conformance.py`
**When** the AUDIT runs
**Then**:
1. The AUDIT asserts class-conformance count ≥ **11** activation contracts (per current Slab-7b body-activation deliverables: Texas + Quinn-R + Vera + Irene-Pass1 + Tracy + Gary + Kira + Wanda + Enrique + Dan + Compositor = 11).
2. The AUDIT confirms the validator's PASS line (current state: `PASS: 19 parity contract file(s) conform (11 activation + 8 decision-card shape-pin)`).

### AC-7c.20a-C — TW-7c-1 firing on gap-rate threshold (AMEND-7c)

**Given** combined floor 31 = 20 shape-pins + 11 class-conformance
**When** the AUDIT discovers gaps
**Then**:
1. If discovered gap count is **≥4** (10% gap-rate against floor 31): TW-7c-1 (high severity) fires + tripwire-ledger entry written to `sprint-status.yaml::tripwire_events` per AMEND-7c percentage threshold.
2. Test FAILS hard (no soft-skip); party-mode-consensus required to absorb-vs-defer per gap; gap-fill follow-ons filed as `7c.X.<descriptor>` (cap 5; >5 escalates to party-mode impasse).
3. If gap count <4: AUDIT PASSES (gaps within tolerance); per-gap notes recorded in the AUDIT test output for visibility but NO tripwire fire.

### AC-7c.20a-D — AUDIT determinism + read-only invariant

**Then** the AUDIT module:
1. Is read-only against the substrate (does NOT modify any production code or shipped tests).
2. Produces deterministic AUDIT output — running the test twice produces byte-identical pass/fail counts (use `pytest --collect-only` deterministic ordering; sort discovery results).
3. Surfaces gap-fill descriptors in a stable order (sorted by family then dimension).

---

## Tasks / Subtasks

- [ ] **T1 — Readiness checks**
  - [ ] T1.1 Confirm 7c.1 + 7c.4b + 7c.5.G0..G6 done in sprint-status.
  - [ ] T1.2 Read `tests/parity/test_decision_card_*.py` to inventory existing shape-pin tests (count + family + dimension coverage).
  - [ ] T1.3 Read `scripts/utilities/validate_parity_test_class_conformance.py` to understand the current activation + decision-card-shape-pin classification.
  - [ ] T1.4 Read AMEND-7c percentage-threshold logic from PRD + governance JSON for TW-7c-1 firing rule.
  - [ ] T1.5 Read `sprint-status.yaml::tripwire_events` ledger schema (per Slab-7b precedent: tripwire_id + story_owner + fired_at + fired_verdict + measured_value + escalation_action_taken + decision_record_link).
  - [ ] T1.6 Refresh broad-regression baseline + record current class-conformance baseline (expected 19 — 11 activation + 8 decision-card shape-pin).

- [ ] **T2 — Author AUDIT test module**
  - [ ] T2.1 Author `tests/audit/__init__.py` (empty namespace; create if not present).
  - [ ] T2.2 Author `tests/audit/test_audit_ac_shape_pins_class_conformance.py` per ACs A-D. Use pytest collection for shape-pin discovery + subprocess-call to validator script for class-conformance count.
  - [ ] T2.3 Implement gap-discovery helper: enumerate (family, dimension) pairs vs discovered tests; report missing pairs as gap descriptors.
  - [ ] T2.4 Implement TW-7c-1 firing path: on gap-rate ≥10%, write tripwire-ledger entry to `sprint-status.yaml::tripwire_events` (append-only — preserve existing entries; add new entry).

- [ ] **T3 — Verification battery (R-tier R3; T11-tier standard)**
  - [ ] T3.1 Focused: `.venv/Scripts/python.exe -m pytest tests/audit/test_audit_ac_shape_pins_class_conformance.py -p no:randomly -q --tb=short` PASS (assuming no gap-rate trip; if trips, follow STOP-and-escalate AMEND-7c protocol).
  - [ ] T3.2 §02A non-regression PASS UNCHANGED.
  - [ ] T3.3 Wave-3/4/5 closed-section non-regression sweep PASS UNCHANGED.
  - [ ] T3.4 Wave-4 Marcus-writer non-regression PASS UNCHANGED.
  - [ ] T3.5 R3 broad regression: failure count ≤ T1 baseline (delta ≤ 0); per-failure git-log-attribution.
  - [ ] T3.6 Class-conformance: T1-baseline UNCHANGED (AUDIT does NOT register new parity_contract; class-conformance count stable at 19).
  - [ ] T3.7 Lint-imports: 12 KEPT UNCHANGED (no pyproject.toml edit).
  - [ ] T3.8 Sandbox-AC: PASS.
  - [ ] T3.9 Ruff: clean.

- [ ] **T10 — Codex self-review dropbox**
  - [ ] T10.1 Drop `_codex-handoff/7c-20a.ready-for-review.md` with: shape-pin count discovered + class-conformance count + per-gap descriptors (if any) + TW-7c-1 fire/no-fire verdict + AUDIT determinism evidence (twice-run byte-identical).

---

## Required Readings (T1)

1. This story spec.
2. `_bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md` FR-7c-34 + FR-7c-36 + AMEND-7c (Murat percentage threshold).
3. `_bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md §Story 7c.20a` (epic-level scope authority).
4. `tests/parity/test_decision_card_*.py` (existing shape-pin inventory).
5. `tests/schemas/operator_verdict/` (existing OperatorVerdict shape-pins).
6. `scripts/utilities/validate_parity_test_class_conformance.py` (activation + decision-card classification).
7. `_bmad-output/implementation-artifacts/sprint-status.yaml::tripwire_events` (ledger schema; precedent entries for wave_1_close + wave_2b_close + wave_3_first_port + wave_3_parallel_close_kira).
8. Governance JSON `7c-20a` entry: gate_mode=single-gate, K=1.2×, t11_tier=standard, lookahead_tier=2, prerequisites=10 stories all done, tripwire_ownership=["TW-7c-1"].
9. `docs/dev-guide/specialist-anti-patterns.md::A18` (PowerShell BOM; if any artifact regen happens — likely none for AUDIT).

## Sandbox-AC validator status

Spec contains zero forbidden CLIs in dev-agent AC blocks. PASS expected at AMELIA-P2.

---

## Dispatch state

**DISPATCH-READY** post-AMELIA-P2 PASS — all predecessors closed. Per governance JSON, this story has 10 prerequisites (7c.1 + 7c.4b + 7c.5.G0..G6) all DONE.

**Lookahead-tier=2 rationale:** spec is pre-authored at deeper lookahead per governance. Codex can dispatch immediately; the deeper tier reflects the AUDIT-AC framing (verification of substrate that has settled across multiple waves) rather than predecessor-chain depth.

**Parallel-dispatch viable with 7c.20b + 7c.20c** — three AUDIT-AC siblings; path-disjoint at file level (each authors a separate `tests/audit/test_audit_ac_*.py` module). All three share TW-7c-1 ownership; if any single AUDIT trips the firing threshold, all three should STOP and escalate per AMEND-7c (party-mode-consensus on absorb-vs-defer).

---

## Dev Agent Record

### Agent Model Used

Codex GPT-5 (bmad-dev-story discipline).

### Debug Log References

(populated by Codex at T1-T3)

### Completion Notes List

(populated by Codex at T10; include shape-pin count discovered + class-conformance count + per-gap descriptors + TW-7c-1 fire/no-fire verdict)

### File List

(populated by Codex at T10)

### Change Log

- 2026-05-06: Spec pre-authored by Claude (lookahead_tier=2) for Wave-5 AUDIT-AC trio dispatch.
