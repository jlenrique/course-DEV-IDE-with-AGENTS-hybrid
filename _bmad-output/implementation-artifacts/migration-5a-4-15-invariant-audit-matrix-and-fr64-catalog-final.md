# Migration Story 5a.4: 15-Invariant Audit Matrix Roll-Up + FR64 Catalog Final

**Status:** ready-for-dev
**Sprint key:** `migration-5a-4-15-invariant-audit-matrix-and-fr64-catalog-final`
**Epic:** Slab 5a — M5 acceptance gate.
**Pts:** 3 | **Gate:** single (per governance JSON `5a-4.expected_gate_mode = "single-gate"`, rationale: null). **K-target:** ~1.2× (target 8 / floor 7).

**Predecessor:** 5a.1 + 5a.2 + 5a.3 done. **HARD INHERITANCE BINDING:** 2c.3 A-R1 BLOCKER B1 RESOLVED-BY-DEFERRAL filed matrix creation to Slab 5a; absorbs `slab-2c-wondercraft-invariant-stub.md` + `slab-3-marcus-invariant-stub.md` (from 3.6 AC-G) at this story.

---

## T1 Readiness Block

1. Governance: `5a-4.expected_gate_mode = "single-gate"`.
2. **Substrate inheritance (BINDING):**
   - `_bmad-output/implementation-artifacts/slab-2c-wondercraft-invariant-stub.md` per 2c.3 AC-D close (verified 2026-04-26 via Codex 21b5bf6 commit).
   - `_bmad-output/implementation-artifacts/slab-3-marcus-invariant-stub.md` per 3.6 AC-G close (verify post-Slab-3-close).
   - Per-slab D12 close-stubs across Slabs 1-5a — invariant preservation entries are scattered across `migration-1-*.md` + `migration-2a-*.md` + `migration-2b-*.md` + `migration-2c-*.md` + `migration-3-*.md` + `migration-4-*.md` + `migration-5a-{1,2,3}-*.md` close notes.
3. **15 invariants list** — per architecture decision-of-record (verify exact list at `_bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md`); typically includes Marcus SPOT, cold-start sanctum-read, HIL-paused, Marcus-first activation, specialist registry, deterministic neck (manifest CI), learning events, ledger side-effect, lane separation, etc.
4. **Anti-patterns catalog** — current state at `docs/dev-guide/specialist-anti-patterns.md` post-Slab-4 close (catalog has Slab-2 + Slab-3 + Slab-4 harvest annotations; FR64 requires ≥5 entries with slab-of-discovery + real example + counter-pattern).
5. **Migration-guide §1 OR §12 anchor** — matrix lands in migration-guide per epic 5a.4 wording.
6. Severance posture.

### TEMPLATE scope decisions

**Decision #1 — Bounded scope:** (a) `_bmad-output/implementation-artifacts/15-invariant-audit-matrix.md` CREATION (deferred from 2c.3 + scoped to Slab 5a); (b) per-invariant entry roll-up from per-slab D12 close-stubs + 2c.3 + 3.6 stub absorption; (c) cross-references from migration-guide §1 OR new §12 "Invariant Audit" appendix; (d) FR64 catalog final assertion (≥5 entries with named file/test references); (e) migration-guide §Anti-Patterns Appendix cross-references finalized. NOT in scope: M5 ship verdict (5a.5).

**Decision #2 — Matrix table format:** 15 rows (one per invariant) × N columns: `invariant_name | slab_of_introduction | slab_of_close | named_files | named_tests | preservation_evidence | status`. Status enum: `PRESERVED / DEFERRED / VIOLATED`. Conditional-states (e.g., M2 conditional / M3 conditional from 2c.4 + 3.6) noted in `preservation_evidence` column.

**Decision #3 — Stub absorption mechanism:** read `slab-2c-wondercraft-invariant-stub.md` + `slab-3-marcus-invariant-stub.md` + per-slab D12 close-stubs; map each entry to one of the 15 invariants; if multiple stubs map to same invariant, merge entries with provenance preservation. If a stub references an invariant NOT in the canonical 15, file as candidate 16th invariant (party-mode consensus required to expand the list).

**Decision #4 — Anti-patterns catalog FR64 final assertion (mirror 2c.4 + 3.6 + 4.7 cycle-complete pattern):** add catalog header annotation `"Slab 1+2+3+4+5a harvest cycle complete; ≥5 entries A1-A<final> per FR64; cross-references in migration-guide §Anti-Patterns Appendix; format-freeze v1 preserved."` Per Mary harvest-gate: NO preemption of harvest-verdicts at story-author; 5a.4 dev-time runs final harvest-gate evaluation.

---

## Story

As an **operator closing M5 ship verdict per FR63+FR64**,
I want **the 15-invariant audit matrix CREATED at `_bmad-output/implementation-artifacts/15-invariant-audit-matrix.md` rolled up from slab-by-slab D12 entries + 2c.3 + 3.6 stub absorption + anti-patterns catalog finalized with ≥5 entries (validated harvested-not-invented per Mary harvest-gate)**,
So that **FR63 + FR64 are met and M5 acceptance has full invariant-preservation evidence**.

---

## Acceptance Criteria

### AC-5a.4-A — `15-invariant-audit-matrix.md` CREATION

- **Given** 2c.3 A-R1 BLOCKER B1 RESOLVED-BY-DEFERRAL filed matrix creation to this story
- **When** dev authors `_bmad-output/implementation-artifacts/15-invariant-audit-matrix.md` per Decision #2 format
- **Then** matrix has 15 rows (one per invariant) × N columns; each row carries named file/test references + status enum + preservation evidence per Decision #3 absorption.
- **Test pin:** `tests/migration/test_15_invariant_audit_matrix_present.py` — 1 test asserting (a) file exists; (b) ≥15 invariant rows; (c) each row has all required column fields populated (regex per Decision #2).

### AC-5a.4-B — Stub absorption per Decision #3

- **Given** stubs at `slab-2c-wondercraft-invariant-stub.md` + `slab-3-marcus-invariant-stub.md`
- **When** dev maps each stub entry to one of the 15 invariants
- **Then** each stub entry resolved (PRESERVED / DEFERRED / VIOLATED status); merged-with-provenance for multi-stub entries; ≥16th-invariant candidates filed for party-mode if any.
- **Test pin:** `tests/migration/test_15_invariant_stub_absorption.py` — 1 test asserting matrix references both stub files in §"Provenance" + has ≥1 entry sourced from each stub.

### AC-5a.4-C — Anti-patterns catalog FR64 final per Decision #4

- **Given** catalog at A1-A<N> post-Slab-4 close
- **When** dev runs final harvest-gate evaluation at 5a.4 dev-time + adds cycle-complete header annotation
- **Then** catalog has ≥5 entries with slab-of-discovery + real example + counter-pattern fields populated; cycle-complete annotation present per Decision #4 wording.
- **Test pin:** `tests/migration/test_anti_patterns_catalog_fr64_final.py` — 1 test asserting (a) ≥5 entries; (b) each entry has 4-field-format (name + example + counter-pattern + slab-of-discovery per format-freeze v1); (c) header contains "Slab 1+2+3+4+5a harvest cycle complete" annotation.

### AC-5a.4-D — Migration-guide cross-references

- **Given** matrix at `_bmad-output/implementation-artifacts/15-invariant-audit-matrix.md` + anti-patterns at `docs/dev-guide/specialist-anti-patterns.md`
- **When** dev cross-references from migration-guide §1 OR new §12 "Invariant Audit" appendix
- **Then** migration-guide contains link to matrix + anti-patterns; appendix has at-a-glance summary.
- **Test pin:** `tests/migration/test_migration_guide_invariant_audit_xref.py` — 1 test asserting migration-guide contains regex match for matrix path + anti-patterns path.

### AC-5a.4-E — Anti-pattern catalog harvest cycle complete

NO new entries expected at this story (this IS the cycle-complete annotation story).

### AC-5a.4-F — TEMPLATE compliance

R1, R6, R8 honored.

### AC-5a.4-G — D12 close protocol (single-gate; FOUR-line)

1. Invariant preservation: FR63 + FR64 met; matrix created at long-deferred location.
2. Anti-pattern harvest: per AC-C cycle-complete annotation.
3. Migration-guide update: §1 OR new §12 appendix added per AC-D.
4. TEMPLATE compliance: R1, R6, R8.

### AC-5a.4-H — Sprint-status state-flips at filing AND close.

---

## File Structure Requirements

### NEW files

- `_bmad-output/implementation-artifacts/15-invariant-audit-matrix.md`
- `tests/migration/{test_15_invariant_audit_matrix_present, test_15_invariant_stub_absorption, test_anti_patterns_catalog_fr64_final, test_migration_guide_invariant_audit_xref}.py`

### MODIFIED files

- `docs/dev-guide/specialist-anti-patterns.md` — cycle-complete annotation per AC-C.
- `docs/dev-guide/langgraph-migration-guide.md` — §1 OR §12 appendix per AC-D.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — per AC-H.

---

## Testing Requirements

**K-target ~1.2× (target 8 / floor 7).** AC-A:1 + AC-B:1 + AC-C:1 + AC-D:1 = **4 K-floor**. RIDER: AC-A adds per-row-shape strict assertion (regex per all required column fields) → +1; AC-B adds candidate-16th-invariant detection test → +1; AC-C adds 4-field-format strict assertion per format-freeze v1 → +1 = honest **7 K-floor (meets floor)**.

Sandbox-AC PASS.

---

## Dev Agent Record

_(Populated during T1–T9 execution.)_
