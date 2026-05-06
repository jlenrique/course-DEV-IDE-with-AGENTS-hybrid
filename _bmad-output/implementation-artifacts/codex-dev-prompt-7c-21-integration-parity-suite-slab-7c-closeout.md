# Codex dev-story prompt — Story 7c.21 (Slab 7c Integration Parity Suite + Closeout Ceremony; **dual-gate cross-agent MANDATORY**; cross-agent T11)

**Cycle:** Claude spec (lookahead_tier=3) → Codex T1-T10 → drops `_codex-handoff/7c-21.ready-for-review.md` → Claude T11 cross-agent (deepest review) → Gate-2 operator-driven ceremony → close commit.
**Wave:** 6 — strict-last ceremony.
**Pre-authored:** 2026-05-06.
**Dispatch state:** **DISPATCH-READY** post-AMELIA-P2 PASS — all 28 prerequisites done; AUDIT-AC trio CLEAN (TW-7c-1 not_fired); substrate verified.

**STOP-on-TW-7c-6-fire** binding=hard per AMEND-7d-iii. If 50-run firing breaches AMEND-7a budget, HALT and escalate per spec AC-B (no soft-skip; no retry without party-mode authorization).

---

```
Run bmad-dev-story on Story 7c.21 (Slab 7c Wave 6 closeout ceremony; dual-gate cross-agent MANDATORY; cross-agent T11).

Spec: `_bmad-output/implementation-artifacts/migration-7c-21-integration-parity-suite-slab-7c-closeout.md`.

## Required reading (in order)

1. Story spec (7 ACs A-G; T1-T12 task structure; **standard-tier T1 is HEAVIER than usual** — 17 required readings).
2. `_bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md` FR-7c-39..43 + FR-7c-47 + FR-7c-51 + NFR-7c-R7a + NFR-7c-R7b.
3. `_bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md §Decision D12` (cross-slab governance — three mandatory AC lines at slab close).
4. `_bmad-output/implementation-artifacts/migration-7c-0b-scaffold-foundation.md` (50-run harness scaffold + per-cell flake-rate calculator inheritance).
5. `_bmad-output/implementation-artifacts/migration-7c-20c-audit-ac-four-file-lockstep-tripwire-ledger.md` (LAST-CLOSER ledger-append pattern reference for TW-7c-6 entry; mirror).
6. **`app/audit/chain.py`** + **`app/models/tripwire_ledger.py`** (audit-chain integrity + ledger schema; READ-ONLY).
7. **`app/parity/contracts/_flake_rate.py`** + **`scripts/utilities/detect_tw_7c_6_parity_flake.py`** (50-run harness invocation; READ + INVOKE).
8. **`app/manifest/compiler.py::production_gate_ids`** (manifest-derived gate-ids source for Trial3Transcript closed-enum).
9. `_bmad-output/planning-artifacts/slab-7-legacy-migrated-mapping-checklist.md` (33-row floor; SG-2; READ-ONLY — do NOT flip rows; row-flips are operator Gate-2 work).
10. `tests/parity/test_mapping_checklist_status.py` (SG-2 integrity test reference).
11. `_bmad-output/planning-artifacts/deferred-inventory.md` (slab-7c-live-harness-evidence + trial-2-finding-1/2 entries; READ-ONLY for verification — closures are pre-existing).
12. `docs/dev-guide/langgraph-migration-guide.md` (D12-3 migration-guide §Slab 7c update target — APPEND a new section).
13. `docs/dev-guide/specialist-anti-patterns.md` (D12-2 anti-pattern catalog; APPEND ≥1 entry).
14. Governance JSON `7c-21` entry: gate_mode=dual-gate, K=1.4×, t11_tier=cross-agent, lookahead_tier=3, prerequisites=28 stories, tripwire_ownership=["TW-7c-6"], stop_on_tripwire_fire=hard.
15. `docs/dev-guide/specialist-anti-patterns.md::A18` (PowerShell BOM hardening for any schema regen).
16. `docs/dev-guide/pydantic-v2-schema-checklist.md` (apply to Trial3Transcript).
17. `_bmad-output/implementation-artifacts/sprint-status.yaml::tripwire_events` (existing TW-7c-1 + reservation entries TW-7c-2..6; append TW-7c-6 firing entry at AC-B).

## T1 hard checkpoints

- All 28 prerequisites done in sprint-status.
- AUDIT-AC trio TW-7c-1 verdict at `not_fired` (sprint-status.yaml::tripwire_events confirms).
- 50-run harness importable: `from app.parity.contracts._flake_rate import compute_flake_rates` (or analogous; Codex confirms exact import surface at T1).
- `production_gate_ids(manifest)` callable + returns `frozenset[str]` for Trial3Transcript closed-enum source.
- Mapping checklist exists at expected path; row-count = 33 (SG-2 floor confirmed).
- D12 architecture decision readable at architecture-langchain-langgraph-migration.md line 563.
- Migration guide exists at `docs/dev-guide/langgraph-migration-guide.md` (D12-3 target).
- Anti-pattern catalog exists at `docs/dev-guide/specialist-anti-patterns.md` (D12-2 target).
- Class-conformance baseline = 19 (UNCHANGED expected post-7c.21 since this story authors ceremony evidence + Trial3Transcript schema, NOT new HIL surfaces).
- Broad-regression baseline: re-run.

## Files in scope

**New (~8 files):**
- `app/models/trial3_transcript.py` (~120 LOC; Trial3Transcript + TrialEvent + GateId + TrialEventType Pydantic-v2 + Literals)
- `app/models/trial3_transcript.v1.schema.json` (regen via Path.write_text per A18)
- `tests/trial/__init__.py` (if not present; create empty namespace)
- `tests/trial/test_trial3_transcript_shape.py` (~80 LOC; schema-hash STABLE pin + closed-enum red-rejection + tz-aware + UUID4)
- `tests/trial/test_trial3_readiness.py` (~150 LOC; R7a + R7b + 11-HIL-class-conformance verification)
- `scripts/utilities/run_slab_close_50_run_parity.py` (~150 LOC; 50-run firing wrapper + AMEND-7a budget check + ledger append)
- `tests/audit/test_audit_ac_slab_7c_close_d12_protocol.py` (~150 LOC; D12 three-line set verification)
- `tests/audit/test_audit_ac_sg_aggregate_enforcement.py` (~120 LOC; SG-1+2+3+4 aggregated structural verification)
- `_bmad-output/implementation-artifacts/slab-7c-retrospective-evidence-pack.md` (~200 LOC markdown; consumed by operator at Gate-2)

**Modified (~4 files):**
- `_bmad-output/implementation-artifacts/sprint-status.yaml::tripwire_events` — APPEND TW-7c-6 firing-aggregate entry (deterministic byte append; LAST-CLOSER pattern from 7c.20c)
- `docs/dev-guide/langgraph-migration-guide.md` — APPEND §Slab 7c section (D12-3)
- `docs/dev-guide/specialist-anti-patterns.md` — APPEND ≥1 anti-pattern entry harvested from Slab 7c development (D12-2)
- `_bmad-output/planning-artifacts/epics-langchain-langgraph-migration.md` — APPEND Slab 7c invariant-preservation note (D12-1)

**Do NOT modify:**
- `app/parity/contracts/_flake_rate.py` (READ-ONLY; consumed via import)
- `app/audit/chain.py` + `app/models/tripwire_ledger.py` (READ-ONLY; consumed)
- Mapping checklist file `slab-7-legacy-migrated-mapping-checklist.md` (READ-ONLY; row-flips are operator Gate-2 work, NOT dev-agent)
- Deferred-inventory entries for `trial-2-finding-1` + `trial-2-finding-2` (already CLOSED-BY 7c.2 + 7c.3a; verify-only)
- Existing AUDIT modules under `tests/audit/` (READ-ONLY; sibling references)
- Closed §section packages, Marcus writers, AUDIT-AC trio modules (all READ-ONLY)
- `app/manifest/compiler.py` (READ-ONLY; consumed)
- `pyproject.toml` (no contract changes for 7c.21)

## Critical implementation notes

- **Trial3Transcript closed-enum gate-ids**: source from `production_gate_ids(manifest)` at runtime OR code-generate the Literal from the manifest at T1. Code-generated Literal is preferred for schema-stability (closed-enum semantics + sha256-stable schema hash). T1-T9 decision: pick approach + document at T10.
- **TrialEventType Literal**: `Literal["edit", "approve", "reject", "complete"]` per PRD line 928. NO widening; closed-enum strict.
- **50-run firing**: wrap `detect_tw_7c_6_parity_flake.py` cleanly. Per-cell flake-rate computed via `compute_flake_rates` (or analogous) from `_flake_rate.py`. AMEND-7a budget check: 7c-added cells <0.05% / pre-7c cells <0.1%.
- **TW-7c-6 STOP-on-fire** (AMEND-7d-iii hard binding): if budget breach, raise `GateError` (or analogous) + write tripwire-ledger entry with `fired_verdict: fired` + escalation context; do NOT proceed to subsequent ACs; HALT and escalate to party-mode.
- **TW-7c-6 not_fired path**: ledger entry with `fired_verdict: not_fired` + measured_value (per-cell flake rates summary); ceremony continues.
- **R7a + R7b precondition fixtures**: T1 LOCATES exact paths (likely under `tests/trial/` or `_bmad-output/implementation-artifacts/`); existence check only — do NOT ship fixtures (they should pre-exist from Slab-7a/7b body activation).
- **D12 three-line set**: physical files modified at:
  1. (D12-1) `_bmad-output/planning-artifacts/epics-langchain-langgraph-migration.md` — APPEND a "Slab 7c Invariant-Preservation Notes" subsection with bullet entries for SG-1+2+3+4 + key load-bearing files/tests.
  2. (D12-2) `docs/dev-guide/specialist-anti-patterns.md` — APPEND ≥1 anti-pattern entry (suggested: A19 = naive corpus-scan fallback discovered at Trial-2; A20 = class-definition-substring scanner staleness from `test_no_unauthorized_callers`; A18 PowerShell BOM is already cataloged so no new entry needed there).
  3. (D12-3) `docs/dev-guide/langgraph-migration-guide.md` — APPEND a "§Slab 7c — Marcus Orchestrational Tail" section (~50 lines) summarizing key learnings.
- **SG-aggregate AUDIT**: assert all 4 SGs structurally enforced. SG-2 row-flip evidence collection happens in retrospective evidence pack (item 6 below) — NOT a row-flip in the dev-agent diff (that's operator Gate-2 per `slab-7b-mapping-checklist-row-status-update` deferred-inventory governance).
- **Retrospective evidence pack (item 6)**: 8 sections per spec AC-F. Operator-readable markdown; structured for Gate-2 review. Do NOT trigger `bmad-retrospective` — that is operator-driven Gate-2 work.
- **No new parity_contract decorator** — class-conformance UNCHANGED at 19.
- **No pyproject.toml edit** — M1-M4 + C1-C6 contracts inherited.
- **K-target 1.4× ≈ 1.7K LOC ceiling.** Estimate ~1.2K LOC actual.
- **T11 cross-agent tier** (per governance): Claude T11 review covers all 7 ACs deeper than standard, with strict-last + dual-gate + cross-agent MANDATORY discipline.

## PARALLEL-DISPATCH GUARDRAILS

1. **AMEND-7d-i AST-scan compliance.** N/A.
2. **Pattern-replication discipline.** Mirror 7c.20c LAST-CLOSER ledger-append pattern (for TW-7c-6 entry) + Wave-3/4/5 schema-stability shape-pin discipline (for Trial3Transcript) + AUDIT-AC trio AUDIT-not-BUILD framing (for D12 + SG-aggregate AUDITs).
3. **Shared-file integration ordering.** `sprint-status.yaml::tripwire_events` append (single entry); `langgraph-migration-guide.md` + `specialist-anti-patterns.md` + `epics-langchain-langgraph-migration.md` append (each single section).
4. **Pattern-parity ratchet.** Pydantic-v2 ConfigDict + closed-enum Literal + UUID4 + tz-aware datetime + sha256-hex pattern + schema_version=1 + strip-then-non-empty.
5. **Class-conformance arithmetic.** UNCHANGED at 19.
6. **Broad-regression baseline shift with per-failure attribution.** Record T1 baseline; T9 delta ≤ 0.

## Verification battery (T9)

```bash
.venv/Scripts/python.exe -m pytest tests/trial/ tests/audit/test_audit_ac_slab_7c_close_d12_protocol.py tests/audit/test_audit_ac_sg_aggregate_enforcement.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/audit/ tests/parity/test_mapping_checklist_status.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/test_sprint_status_yaml.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest --smoke -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/
.venv/Scripts/lint-imports.exe
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-21-integration-parity-suite-slab-7c-closeout.md
.venv/Scripts/python.exe -m ruff check app/models/trial3_transcript.py tests/trial/ tests/audit/test_audit_ac_slab_7c_close_d12_protocol.py tests/audit/test_audit_ac_sg_aggregate_enforcement.py scripts/utilities/run_slab_close_50_run_parity.py
.venv/Scripts/python.exe scripts/utilities/run_slab_close_50_run_parity.py  # 50-run firing — STOP-on-fire if budget breached
```

## T10 + T11

T10: dropbox at `_codex-handoff/7c-21.ready-for-review.md`. Include:
- Trial3Transcript schema hash + closed-enum gate-ids source (manifest-derived vs code-generated)
- TW-7c-6 50-run firing verdict (`not_fired` / `fired`); per-cell flake-rate summary
- Tripwire-ledger entry written to sprint-status.yaml::tripwire_events
- R7a precondition fixtures verification (locations + existence)
- R7b 120/180-min forensic-evidence harness verification (location + minimal-invocation result)
- 11-HIL-class-conformance verdict
- D12 three-line set evidence (D12-1 + D12-2 + D12-3 file pointers)
- SG-aggregate AUDIT verdict (SG-1+2+3+4 all green)
- Retrospective evidence pack pointer + 8-section confirmation
- Deferred-inventory verifications (slab-7c-live-harness-evidence still-deferred + Trial-2 #1/#2 already-closed)
- Class-conformance UNCHANGED at 19
- Broad-regression delta with per-failure attribution

T11: Claude **cross-agent T11** (~40-60 min; deepest tier). Cross-agent MANDATORY per governance. Reviews all 7 ACs A-G with strict-last + dual-gate discipline. Verifies:
- AC-A Trial3Transcript schema-shape correctness + closed-enum integrity
- AC-B 50-run firing AMEND-7a budget verification + STOP-on-fire branch logic
- AC-C R7a/R7b/11-HIL precondition coverage
- AC-D D12 three-line set completeness + content quality
- AC-E SG-aggregate verdict accuracy
- AC-F retrospective evidence pack quality (8 sections; operator-readable)
- AC-G deferred-inventory verifications

## Boundary

HALT on:
- Any of 28 prerequisites not done
- TW-7c-6 fires (AMEND-7d-iii STOP-on-fire; escalate to party-mode for parity-budget mitigation; do NOT proceed)
- Class-conformance count != 19 baseline
- Broad-regression failure count > T1 baseline AND any new failure not git-log-verified-inherited
- D12 three-line set incomplete (any of D12-1/2/3 missing or empty)
- Mapping checklist row count != 33 (SG-2 floor breach — Slab 7c regression)
- Sanctum-alignment registry count <6 (SG-4 regression)
- 11-HIL-class-conformance gap (Trial-3 readiness predicate (d) breach)

DO NOT touch:
- Mapping checklist file (`slab-7-legacy-migrated-mapping-checklist.md`) — row-flips are operator Gate-2 work
- Existing tripwire-ledger entries (append-only; preserve all 4 Slab-7b + reservation TW-7c-1..6 entries)
- Deferred-inventory entries already CLOSED (trial-2-finding-1 + trial-2-finding-2)
- 50-run flake-rate calculator + harness scaffold (READ-ONLY; consumed)
- Any closed §section package, Marcus writer, AUDIT module
- pyproject.toml (no contract changes for 7c.21)

DO NOT introduce:
- New tripwire-ledger entry types (NFR-7c-OD2 schema is closed)
- New parity_contract decorators
- New top-level packages
- `bmad-retrospective` skill invocation (operator-driven Gate-2)
- Mapping-checklist row-flips in dev-agent diff
- Defensive widening on TrialEventType / GateId Literals
```

---

## Operator dispatch checklist

1. ☐ All 28 prerequisites done.
2. ☐ AUDIT-AC trio TW-7c-1 at `not_fired` (sprint-status.yaml::tripwire_events confirms).
3. ☐ AMELIA-P2 freshness check.
4. ☐ Sandbox-AC PASS.
5. ☐ Sprint-status: ready-for-dev (already flipped at lookahead_tier=3 pre-author).
6. ☐ Dispatch (strict-last; solo; dual-gate cross-agent MANDATORY).

## Post-Codex-T10 dropbox-watch

Spawn 1 T11 cross-agent review subagent (~40-60 min; deepest tier; covers all 7 ACs A-G + AMEND-4 fold integrity + STOP-on-fire branch logic). After T11 PASS:

## Operator-driven Gate-2 ceremony (NOT dev-agent)

1. Operator triggers `bmad-retrospective` skill via BMAD facilitator workflow (consumes the retrospective evidence pack from T7).
2. Mapping-checklist row-status flips per R15 / FR-7c-42 (party-mode-ratified at retrospective).
3. Final close commit + sprint-status flip review→done.

## Slab 7c retrospective (post-7c.21 close)

Pre-existing optional entry `migration-epic-slab-7c-orchestrational-tail-retrospective: optional`. The retrospective evidence pack from this story is the operator's reading material for that retrospective.

## Wave 6 strict-last (post-retrospective)

`7c.21a Epic 3 retirement + live-dispatch wiring` (already pre-authored at lookahead_tier=1; HARD predecessor relationship per governance JSON; closes deferred-inventory entry `slab-7c-live-harness-evidence`). Dispatches solo after 7c.21 retrospective close.
