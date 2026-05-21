# Codex dev-story prompt — Story 7c.0a (Decision Foundation — parity-contract DSL ADR + import-linter contracts C4/C5/C6 + TripwireLedgerEntry schema + audit-chain conceptual design)

**Cycle:** Claude spec → Codex T1-T9 + T10 self-review → Codex drops `_bmad-output/implementation-artifacts/_codex-handoff/7c-0a.ready-for-review.md` → **Claude T11 `bmad-code-review` (CROSS-AGENT MANDATORY per governance JSON)** → Claude commit + flip done.
**Wave:** 0 slot 1 (architecture-tier; precedes 7c.0b Scaffold Foundation per Winston W1 hard precedence; gates 7c.0b + ALL Wave 1 stories EXCEPT 7c.2 which carries an AMELIA-P1 path-isolation guard).
**Pre-authored:** 2026-05-04 ahead of operator dispatch per `feedback_new_cycle_codex_dev_handoff.md` lookahead-discipline revision.
**AMELIA-P2 freshness check:** Claude re-diffs `migration-7c-0a-decision-foundation.md` (spec) against this prompt at operator dispatch time; if spec hash changed, Claude regenerates this prompt before dispatch.

---

```
Run bmad-dev-story on Story 7c.0a (Slab 7c Wave 0 slot 1; dual-gate; cross-agent code-review MANDATORY; Decision Foundation = parity-contract DSL ADR + 3 import-linter contracts with empty target lists + TripwireLedgerEntry Pydantic-v2 model spec + FR-7c-50 audit-chain integrity conceptual design).

## Required reading (read in order)

1. Story spec: `_bmad-output/implementation-artifacts/migration-7c-0a-decision-foundation.md` (status: ready-for-dev; 4 ACs A-D; 11 tasks T1-T11; you own T1-T10).
2. Slab 7c PRD: `_bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md` — FR-7c-30..33 (DSL design) + FR-7c-50 (audit-chain integrity) + FR-7c-53 C4/C5/C6 + NFR-7c-OD2 (TripwireLedgerEntry).
3. Slab 7c epics: `_bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md` (Story 7c.0a section starting at line 336; Winston W1/W2/W4/W6 + Murat AMEND-7d-ii amendment record).
4. Required readings (cite by reference; do NOT re-derive):
   - `docs/dev-guide/pydantic-v2-schema-checklist.md` — 14 schema idioms; primary enforcement for TripwireLedgerEntry.
   - `docs/dev-guide/dev-agent-anti-patterns.md` — A11 Windows-portability + schema/review-ceremony anti-pattern catalog.
   - `docs/dev-guide/story-cycle-efficiency.md` — K-floor discipline (target 1.2-1.5×, not 5×).
5. Governance JSON: `docs/dev-guide/migration-story-governance.json` story `7c-0a` (dual-gate; cross_agent_review_required=true; expected_pts=3; expected_k_target=1.3; no prerequisite_stories).
6. Sandbox-AC inventory: `docs/dev-guide/migration-ac-sandbox-inventory.json`.
7. `app/models/override_event.py` — sibling reference for the TripwireLedgerEntry placement convention (sibling under `app/models/`, NOT inside `app/models/decision_cards/`).
8. `pyproject.toml::[tool.importlinter]` current state — sibling reference for adding C4/C5/C6 contracts (existing contracts ≥9 KEPT post-Slab-7b).
9. Existing ADRs under `docs/dev-guide/adr/` — verify `0001-` slot is free; if collision, surface as `decision_needed` and pick next-free index.
10. Sprint-status: `_bmad-output/implementation-artifacts/sprint-status.yaml` — `tripwire_events` block carries TW-7c-1..6 in `not_yet_evaluated`; TripwireLedgerEntry is the schema this YAML conforms to.

## T1 hard checkpoints (HALT-AND-SURFACE if violated)

- ADR slot `docs/dev-guide/adr/0001-parity-contract-dsl.md` MUST be free. If `0001-` is occupied, surface as `decision_needed` and pick next-free index (e.g., `0003-`); update spec references via in-story addendum + Dev Notes.
- `tests/fixtures/frozen_paths/` directory MUST exist at T1, OR Codex creates it at T1.2 (document creation in Dev Notes).
- `app/audit/` directory existence: ADR Appendix A names `app/audit/errors.py` for the FR-7c-50 error class hierarchy. If `app/audit/` does not exist at T1, this is FINE for 7c.0a (the appendix is conceptual-design-only; the actual `errors.py` lands in 7c.0b); document the forward-pointer in Dev Notes.
- `lint-imports` (i.e. `.venv/Scripts/lint-imports.exe`) MUST be invokable. If absent, surface as `decision_needed`.
- Pydantic v2 + `pydantic.ConfigDict` + `field_validator` available (current project baseline).
- `pyproject.toml` parses via `tomllib` (ships with Python 3.12).

## Files in scope

**New (5 files):**
- `docs/dev-guide/adr/0001-parity-contract-dsl.md` — ADR with 6 required sub-sections + Appendix A (FR-7c-50 audit-chain integrity conceptual design). ~1.5-2.5K LOC of structured markdown.
- `app/models/tripwire_ledger.py` — TripwireLedgerEntry Pydantic-v2 model + TripwireId + TripwireSeverity closed enums + field_validator on `fired_at`. ~120-180 LOC.
- `tests/parity/test_tripwire_ledger_entry_shape.py` — shape-pin with ≥7 named-field assertions + closed-enum red-rejection + AUDIT round-trip across 6 TW IDs × 2 severity tiers (12 round-trips). ~200-280 LOC.
- `tests/structural/test_adr_0001_parity_contract_dsl_present.py` — path-existence + 6 sub-section heading assertions + Appendix A heading assertion. Substantive-keyword regex (do NOT match exact heading strings). ~80-120 LOC.
- `tests/structural/test_import_linter_contracts_c4_c5_c6_present.py` — `tomllib` parse + name assertions + `lint-imports` subprocess + KEPT-count delta assertion. ~120-180 LOC.

**Modified (2 files):**
- `pyproject.toml` — add 3 import-linter contracts C4/C5/C6 with empty `forbidden_modules` lists + inline comment block citing 7c.0a + Winston W2 + downstream populating stories.
- `app/models/__init__.py` — export TripwireLedgerEntry + TripwireId + TripwireSeverity (3 new exports).

**Do NOT modify:** any specialist body (`app/specialists/**`); any HIL surface module (`app/gates/**` — those are populated by 7c.4b's C6 target list); any pipeline-manifest path (`state/config/pipeline-manifest.yaml`; this is a DECISION-tier story, not pipeline-manifest-touching); any prior ADR (`docs/dev-guide/adr/0001-*` if pre-existing — re-number per T1 instead); any composition-spec section (Composition Spec §3.5 UNALTERED).

## Critical implementation notes

- **K-target 1.3× = ~3.25K LOC ceiling.** ADR ~2K + tripwire_ledger.py ~150 + 3 test files ~600 + pyproject.toml diff ~30 + __init__.py diff ~5 = ~2.8K LOC. Comfortable headroom under K-target. If T-shape ceiling approached, surface as `decision_needed` and consider deferring ADR sub-section depth.
- **Dual-gate cross-agent MANDATORY** at T11 — DO NOT compress the review at T11. Claude reviews the FULL diff in fresh context with ZERO prior-context bleed. Codex T10 self-review is NOT a substitute.
- **Pydantic v2 14-idiom checklist** is non-negotiable for TripwireLedgerEntry. `validate_assignment=True` + `extra="forbid"` + closed-enum on `tripwire_id` with triple-layer red-rejection (Enum + Literal pattern + custom validator on coercion path) + timezone-aware datetime (`field_validator` raising on naive) + UUID4 with format validation (Pydantic v2 native UUID type validates by default). The 7-field minimum is canonical; severity is the 8th field added by Murat A5 (do NOT omit).
- **`frozen=False` is intentional.** Per spec Dev Notes, the append-only invariant lives at the FILE level, not the object level. Do NOT set `frozen=True` (would break the validator pattern).
- **Empty target list for import-linter contracts is structurally KEPT.** No violations possible against an empty `forbidden_modules`. Test pin asserts KEPT count delta = +3 (C4 + C5 + C6) post-7c.0a vs pre-7c.0a baseline.
- **ADR `0001-` collision handling:** If the slot is occupied, pick next-free (e.g., `0003-` or `0004-` — note `0002-slab-7c-gate-taxonomy.md` is RESERVED for 7c.4a; do NOT collide). Update spec references via in-story addendum.
- **No new third-party deps.** Pydantic v2 + tomllib + jinja2 (already shipped).
- **Windows portability (NFR-7c-X1; A11):** `pathlib.Path.as_posix()` for all path strings; UTF-8 explicit encoding everywhere; no `PYTHONIOENCODING=utf-8` workaround.

## Verification battery (T9)

```bash
# Focused tests (3 new test files):
.venv/Scripts/python.exe -m pytest tests/parity/test_tripwire_ledger_entry_shape.py tests/structural/test_adr_0001_parity_contract_dsl_present.py tests/structural/test_import_linter_contracts_c4_c5_c6_present.py -p no:randomly -q --tb=short

# Broad regression slice (NFR-7c-R2; preserve ≥1403 deterministic baseline):
.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line

# Class-conformance validator (NFR-7c-R5; expect 11 conforming activation contracts; no regression):
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/

# Import-linter (KEPT count = pre-7c.0a baseline + 3):
.venv/Scripts/lint-imports.exe

# Sandbox-AC validator (NFR-7c-M5):
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-0a-decision-foundation.md

# Ruff hygiene on the touched files:
.venv/Scripts/python.exe -m ruff check app/models/tripwire_ledger.py app/models/__init__.py tests/parity/test_tripwire_ledger_entry_shape.py tests/structural/test_adr_0001_parity_contract_dsl_present.py tests/structural/test_import_linter_contracts_c4_c5_c6_present.py
```

Expected post-7c.0a baseline:
- ≥1403 broad-regression deterministic baseline preserved (no test regression introduced by Slab 7c.0a).
- `lint-imports` KEPT count ticks up by exactly 3 (C4 + C5 + C6).
- `validate_parity_test_class_conformance.py` reports 11 conforming activation contracts (TripwireLedgerEntry shape-pin is NOT an activation contract; no class-conformance change).
- Sandbox-AC validator PASS.
- Ruff CLEAN on the 5 touched files.

## T10 + T11

**T10:** Codex G6 self-review (Blind / Edge / Auditor) at `_bmad-output/implementation-artifacts/_codex-handoff/7c-0a.ready-for-review.md`. Per `feedback_new_cycle_codex_dev_handoff.md` 2026-05-04 dropbox protocol — drop the completion notice into the Claude-watched dropbox path; do NOT also write a `7c-0a-codex-self-review-*.md` artifact (that pattern is retired). Flip story status `in-progress` → `review` in the spec file. Hand to Claude via the dropbox.

**T11:** Claude (separate cold context from Codex dev) does FINAL `bmad-code-review` (**CROSS-AGENT MANDATORY** per governance JSON cross_agent_review_required=true). Review verdict lands at `_bmad-output/implementation-artifacts/7c-0a-code-review-2026-05-04.md` (or actual review-date). Claude applies remediation cycles if HALT-AND-REMEDIATE; commits the diff (5 NEW + 2 MODIFIED files); flips `migration-7c-0a-decision-foundation: review → done` in sprint-status.yaml.

## Boundary

- **HALT and surface to operator on:**
  (a) ADR slot `0001-` collision unresolved — Codex picks next-free + surfaces in T10 self-review for cross-agent review.
  (b) `lint-imports` not invokable from `.venv/Scripts/`.
  (c) `app/models/tripwire_ledger.py` already exists with conflicting content (highly unlikely; 7c.0a is the introducer).
  (d) Pydantic v2 idiom check fails — TripwireLedgerEntry violates ANY of the 14 idioms in `pydantic-v2-schema-checklist.md`.
  (e) K-actual exceeds 1.7× target (~5.5K LOC) — surface for K-budget renegotiation.
  (f) ANY sandbox-AC violation — should not happen given dev-agent-only ACs.
  (g) Broad-regression delta < 0 (any pre-existing test regresses) — investigate root cause; do NOT skip the test.
  (h) Pre-7c.0a `lint-imports` KEPT count + 3 ≠ post-7c.0a count (e.g., a contract collapses or a target-list inadvertently fills) — investigate.

- **Do NOT touch:**
  - Any specialist body (`app/specialists/**`).
  - `state/config/pipeline-manifest.yaml` (this is decision-tier; pipeline-manifest does NOT change).
  - Pre-existing ADRs (re-number 7c.0a's ADR if collision; do NOT modify older ADR content).
  - `docs/dev-guide/composition-specification.md` (Composition Spec §3.5 UNALTERED).
  - Any pyproject.toml block OTHER than `[tool.importlinter]` contract additions + the inline comment.

- **Do NOT introduce:**
  - New third-party deps.
  - New Pydantic models in `app/models/decision_cards/` (TripwireLedgerEntry is a SIBLING of `decision_cards/`, NOT a member).
  - Executable DSL primitives (those land in 7c.0b — 7c.0a is conceptual-design-only for the DSL).
  - Executable test scaffolds for FR-7c-50 audit-chain integrity (the test scaffold lands in 7c.0b; 7c.0a only writes the conceptual design in the ADR appendix).
  - Manifest-touching changes (pipeline-manifest, fold-flags — those are 7a substrate, untouched here).
```

---

## Operator dispatch checklist (before sending this prompt to Codex)

1. ☐ Run `.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-0a-decision-foundation.md` → expect PASS.
2. ☐ Verify governance JSON entry for 7c-0a is current (gate-mode, K-target, pts, cross_agent_review_required=true) — should be locked at v2026-05-04-slab7c-thirty-six-stories.
3. ☐ AMELIA-P2 freshness check: Claude re-diffs `migration-7c-0a-decision-foundation.md` against this prompt; if spec hash changed since 2026-05-04 authoring, regenerate this prompt before dispatch.
4. ☐ Confirm sprint-status.yaml shows `migration-7c-0a-decision-foundation: ready-for-dev` and `migration-epic-slab-7c-orchestrational-tail: in-progress`.
5. ☐ Dispatch this prompt to Codex; Codex flips status `ready-for-dev → in-progress` at T1 start.

## Post-Codex-T10 dropbox-watch protocol

1. ☐ Codex drops `_bmad-output/implementation-artifacts/_codex-handoff/7c-0a.ready-for-review.md` upon T10 completion.
2. ☐ Claude (separate cold context) reads the dropbox notice + the 5-file diff; runs `bmad-code-review` (T11; **CROSS-AGENT MANDATORY**).
3. ☐ Claude applies remediation cycles per HALT-AND-REMEDIATE if any.
4. ☐ Claude commits + flips `migration-7c-0a-decision-foundation: review → done` in sprint-status.yaml.
5. ☐ At 7c.0a close, 7c.0b + Wave 1 stories (except 7c.2 already-parallel) UNBLOCK; next session opens 7c.0b under same NEW CYCLE protocol.
