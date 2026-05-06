# Codex dev-story prompt — Story 7c.20a (AUDIT-AC ≥20 Shape-Pins + ≥11 Class-Conformance; single-gate; standard T11)

**Cycle:** Claude spec (lookahead_tier=2) → Codex T1-T10 → drops `_codex-handoff/7c-20a.ready-for-review.md` → Claude T11 standard → commit + flip done.
**Wave:** 5 — AUDIT-AC trio slot 1 of 3.
**Pre-authored:** 2026-05-06.
**Dispatch state:** **DISPATCH-READY** post-AMELIA-P2 PASS.

**Parallel-dispatch context:** Path-disjoint with 7c.20b + 7c.20c (each AUDIT-AC authors a separate `tests/audit/test_audit_ac_*.py` module). All three share TW-7c-1 ownership; if any single AUDIT trips firing threshold, all three should STOP and escalate per AMEND-7c.

---

```
Run bmad-dev-story on Story 7c.20a (Slab 7c Wave 5 AUDIT-AC trio slot 1; single-gate; standard T11).

Spec: `_bmad-output/implementation-artifacts/migration-7c-20a-audit-ac-shape-pins-class-conformance.md`.

## Required reading (in order)

1. Story spec (4 ACs A-D; T1-T10 task structure).
2. `_bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md` FR-7c-34 + FR-7c-36 + AMEND-7c percentage threshold (Murat).
3. **`tests/parity/test_decision_card_*.py`** (existing shape-pin inventory; READ-ONLY).
4. **`tests/schemas/operator_verdict/`** (existing OperatorVerdict shape-pins; READ-ONLY).
5. **`scripts/utilities/validate_parity_test_class_conformance.py`** (activation + decision-card classification).
6. `_bmad-output/implementation-artifacts/sprint-status.yaml::tripwire_events` (ledger schema; existing 4 Slab-7b entries as precedent).
7. Governance JSON `7c-20a` entry: gate_mode=single-gate, K=1.2×, t11_tier=standard, lookahead_tier=2, R3, tripwire_ownership=["TW-7c-1"].
8. `docs/dev-guide/specialist-anti-patterns.md::A18` (PowerShell BOM hardening).

## T1 hard checkpoints

- 7c.1 + 7c.4b + 7c.5.G0..G6 done in sprint-status.
- Class-conformance baseline observed = 19 (11 activation + 8 decision-card shape-pin) per current validator.
- Combined floor 31 = 20 shape-pins + 11 class-conformance.
- AMEND-7c firing threshold = ≥4 gaps (10% of 31).
- Broad-regression baseline: re-run.

## Files in scope

**New (1 file):**
- `tests/audit/__init__.py` (create if not present)
- `tests/audit/test_audit_ac_shape_pins_class_conformance.py` (~200 LOC; AUDIT module + gap-discovery helper + TW-7c-1 firing path)

**Modified (0 files normally; 1 modified IF gap-rate trips):**
- `_bmad-output/implementation-artifacts/sprint-status.yaml::tripwire_events` — APPEND-ONLY entry IF TW-7c-1 fires for THIS story (≥4 gaps); deterministic byte append; preserves all existing entries.

**Do NOT modify:**
- Any production code under `app/` (AUDIT is read-only against substrate)
- Any existing shape-pin tests (read-only references)
- `scripts/utilities/validate_parity_test_class_conformance.py` (read-only)
- Any closed §section package, Wave-3/4/5 deliverable, or Marcus writer (read-only)

## Critical implementation notes

- **AUDIT-not-BUILD framing**: AUDIT verifies coverage floors. NO new shape-pin tests authored by 7c.20a (those would be gap-fill follow-ons filed AS NEEDED via TW-7c-1 firing). The single new file is THE AUDIT itself.
- **Shape-pin discovery**: use pytest collection (`pytest --collect-only -q tests/parity/ tests/schemas/operator_verdict/`) to enumerate existing shape-pin tests; map to (family, dimension) pairs.
- **Class-conformance discovery**: invoke `scripts/utilities/validate_parity_test_class_conformance.py tests/parity/` via subprocess; parse PASS line for activation + decision-card-shape-pin counts.
- **Gap-fill descriptors**: enumerate (family ∈ {G1, G2C, G3, G4, Override}, dimension ∈ {field-presence, closed-enum-red-reject, JSON-Schema-emission, golden-fixture-round-trip}) = 5×4 = 20 expected pairs. For each pair, check if a corresponding shape-pin test file exists. Missing pairs are gaps.
- **TW-7c-1 firing path**: if discovered_gaps ≥ 4, append a tripwire-ledger entry to `sprint-status.yaml::tripwire_events` per the existing schema (tripwire_id + story_owner + fired_at + fired_verdict + measured_value + escalation_action_taken + decision_record_link). Test FAILS hard.
- **Deterministic AUDIT output**: sort discovery results lexicographically (family then dimension); twice-run byte-identical pass/fail counts.
- **Read-only invariant on substrate**: the AUDIT does NOT modify any production code or shipped tests. ONLY allowed write target: `sprint-status.yaml::tripwire_events` for the firing-path entry.
- **No parity_contract decorator**: the AUDIT is NOT registered as an HIL surface; class-conformance count UNCHANGED at 19.
- **No pyproject.toml edit**.
- **K-target 1.2× ≈ 480 LOC ceiling.** Estimate ~250 LOC actual.
- **T11 standard tier**: AUDIT-AC discipline + tripwire ownership + gap-discovery rigor; deeper review than lite.

## PARALLEL-DISPATCH GUARDRAILS

1. **AMEND-7d-i AST-scan compliance.** N/A.
2. **Pattern-replication discipline.** Read existing AUDIT precedent at `tests/audit/test_override_event_chain_integrity.py` (7c.0b deliverable; FR-7c-50 audit-chain integrity scaffold).
3. **Shared-file integration ordering.** `sprint-status.yaml::tripwire_events` is shared with 7c.20b + 7c.20c — first-mover-appends; subsequent rebases. Single-entry-per-story-per-fire discipline.
4. **Pattern-parity ratchet.** N/A (no Pydantic models authored).
5. **Class-conformance arithmetic.** UNCHANGED.
6. **Broad-regression baseline shift with per-failure attribution.** Record T1 baseline; T9 delta ≤ 0.

## Verification battery (T3)

```bash
.venv/Scripts/python.exe -m pytest tests/audit/test_audit_ac_shape_pins_class_conformance.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/gates/section_02a/ tests/gates/section_04a/ tests/gates/section_04_5/ tests/gates/section_04_55/ tests/gates/section_05_5/ tests/gates/section_07b/ tests/gates/section_07d/ tests/gates/section_07f/ tests/gates/section_08b/ tests/gates/section_11/ tests/gates/section_06b/ tests/gates/section_07c/ tests/gates/section_11b/ tests/gates/section_15/ -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/marcus/orchestrator/writers/ tests/marcus/orchestrator/test_section_09_lock.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest --smoke -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/
.venv/Scripts/lint-imports.exe
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-20a-audit-ac-shape-pins-class-conformance.md
.venv/Scripts/python.exe -m ruff check tests/audit/test_audit_ac_shape_pins_class_conformance.py
```

## T10 + T11

T10: dropbox at `_codex-handoff/7c-20a.ready-for-review.md`. Include: shape-pin count discovered + class-conformance count + per-gap descriptors (if any) + TW-7c-1 fire/no-fire verdict + AUDIT determinism evidence.

T11: Claude standard tier (~25-40 min; deeper review than lite — coverage floors verified; gap-fill descriptors reviewed).

## Boundary

HALT on: 7c.1 / 7c.4b / 7c.5.G0..G6 not done; class-conformance count != 19 baseline; broad-regression failure count > T1 baseline AND any new failure not git-log-verified-inherited; TW-7c-1 fires AND gap count > 5 (escalates to party-mode impasse per AUDIT-AC cap).

DO NOT touch: production code under `app/`; existing shape-pin tests; class-conformance validator script; any closed §section package or Marcus writer.

DO NOT introduce: new shape-pin tests as part of 7c.20a (those are gap-fill follow-on stories, NOT this story's scope); new parity_contract decorators; new dependencies.
```

---

## Operator dispatch checklist

1. ☐ Predecessors (7c.1 + 7c.4b + 7c.5.G0..G6) all done.
2. ☐ AMELIA-P2 freshness check.
3. ☐ Sandbox-AC validator PASS.
4. ☐ Sprint-status: ready-for-dev (already flipped at lookahead_tier=2 pre-author commit).
5. ☐ If parallel-dispatching with 7c.20b + 7c.20c: confirm Codex understands `sprint-status.yaml::tripwire_events` first-mover-appends rule + AMEND-7c STOP-and-escalate posture if any AUDIT trips.
6. ☐ Dispatch.

## Post-Codex-T10 dropbox-watch

Spawn 1 T11 standard review subagent (~25-40 min). If 7c.20b + 7c.20c land concurrently, all three can be batched per Day-3 close-batch precedent — but T11 reviews remain individual (standard-tier) reads, not lite-batchable.
