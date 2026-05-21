# Codex dev-story prompt — Story 7c.0b (Scaffold Foundation — DSL scaffold + sanctum-alignment DSL feature + self-registration audit harness + TW-7c-4/5/6 detection scaffolds + FR-7c-50 audit-chain executable scaffold)

**Cycle:** Claude spec → Codex T1-T9 + T10 self-review → Codex drops `_bmad-output/implementation-artifacts/_codex-handoff/7c-0b.ready-for-review.md` → **Claude T11 `bmad-code-review` (CROSS-AGENT MANDATORY per governance JSON)** → Claude commit + flip done.
**Wave:** 0 slot 2 (build-tier; consumes 7c.0a's frozen ADR + TripwireLedgerEntry; gates ALL Wave 1 stories except 7c.2; opens immediately after 7c.0a close).
**Pre-authored:** 2026-05-04 ahead of operator dispatch per `feedback_new_cycle_codex_dev_handoff.md` lookahead-discipline revision.
**Dispatch state:** **DISPATCHABLE NOW (re-dispatch after 2026-05-04 spec amendment).** Predecessor 7c.0a CLOSED `done` 2026-05-04 commit `f926867`. AMELIA-P2 freshness check at dispatch time. **2026-05-04 amendment:** Codex's first dispatch HALTED at T1.7 due to false-positive UTF-8 violations on binary files (`__pycache__/*.pyc`, generated `*.mp3`). Spec amended at AC-7c.0b-E + T1.7 to add the canonical binary-skip rule (git-ls-files restriction + extension blocklist + null-byte sniff). Codex re-dispatchable; HALT condition narrowed to genuine TEXT-FILE violations only.

---

```
Run bmad-dev-story on Story 7c.0b (Slab 7c Wave 0 slot 2; dual-gate; cross-agent code-review MANDATORY; Scaffold Foundation = executable DSL scaffold + sanctum-alignment DSL feature + self-registration audit harness skeleton + TW-7c-4/5/6 detection scaffolds + FR-7c-50 audit-chain executable test + FR-7c-46 UTF-8 lint pass + AMEND-7a-tightened per-cell flake-rate calculator).

## Required reading (read in order)

1. Story spec: `_bmad-output/implementation-artifacts/migration-7c-0b-scaffold-foundation.md` (status: ready-for-dev; 6 ACs A-F; 11 tasks T1-T11; you own T1-T10).
2. **Predecessor 7c.0a's FROZEN ADR**: `docs/dev-guide/adr/0001-parity-contract-dsl.md` — ALL 6 sub-sections + Appendix A. This ADR is the canonical contract surface for 7c.0b's DSL scaffold; consume directly. (`Status: ACCEPTED` per 7c.0a close commit `f926867`.)
3. **Predecessor 7c.0a's FROZEN schema**: `app/models/tripwire_ledger.py` — TripwireLedgerEntry + TripwireId + TripwireSeverity. Consumed by AC-7c.0b-D audit-chain test fixtures (do NOT mock).
4. 7c.0a T11 review verdict: `_bmad-output/implementation-artifacts/7c-0a-code-review-2026-05-04.md` — informational. The wildcard source-module pattern carries forward; 7c.0b begins populating C4 target list per AC-7c.0b-A.
5. Slab 7c PRD: `_bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md` — FR-7c-30..33/46/50/54 + NFR-7c-OD7 + AMEND-7a/7d-ii.
6. Slab 7c epics: `_bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md` (Story 7c.0b section starting at line 370).
7. Required readings:
   - `docs/dev-guide/pydantic-v2-schema-checklist.md` — 14 schema idioms (SurfaceTransportDeclaration + SanctumAlignmentDeclaration + AuditResult conform).
   - `docs/dev-guide/dev-agent-anti-patterns.md` — A11 Windows-portability + schema/test/review-ceremony anti-patterns.
   - `docs/dev-guide/story-cycle-efficiency.md` — K-discipline (target 1.4× for build-tier substrate-shape).
8. Governance JSON: `docs/dev-guide/migration-story-governance.json` story `7c-0b` (dual-gate; cross_agent_review_required=true; expected_pts=3; expected_k_target=1.4; prerequisite_stories=[7c-0a]).
9. Sandbox-AC inventory: `docs/dev-guide/migration-ac-sandbox-inventory.json`.
10. `state/config/pipeline-manifest.yaml::block_mode_trigger_paths` — for FR-7c-46 UTF-8 lint pass glob discovery (AC-7c.0b-E).

## T1 hard checkpoints (HALT-AND-SURFACE if violated)

- 7c.0a status `done` in BOTH spec file line 3 AND sprint-status.yaml::development_status['migration-7c-0a-decision-foundation']. **Both must be TRUE before T1 begins** (verified at spec authoring 2026-05-04 post-commit `f926867`).
- ADR exists at `docs/dev-guide/adr/0001-parity-contract-dsl.md` with all 6 sub-sections + Appendix A.
- TripwireLedgerEntry exists at `app/models/tripwire_ledger.py` with 9 fields + triple-layer red-rejection on tripwire_id.
- `app/parity/contracts/`, `app/audit/`, `tests/audit/` all do NOT yet exist (Codex creates).
- `tests/fixtures/frozen_paths/` exists (created by 7c.0a).
- `state/config/pipeline-manifest.yaml::block_mode_trigger_paths` exists (for FR-7c-46 lint pass glob).
- C4/C5/C6 contracts in `pyproject.toml::[tool.importlinter]` with empty `forbidden_modules` lists; lint-imports KEPT count = 12.
- Class-conformance validator: 11 conforming activation contracts.
- Broad regression baseline: 3990 passed / 37 failed (per 7c.0a-close baseline).
- **Pre-existing UTF-8 violations check (binary-skip rule mandatory):** dry-run AC-7c.0b-E TW-7c-5 detector against current repo state. **The detector MUST implement the binary-skip rule** (per AC-7c.0b-E spec amendment 2026-05-04 in response to Codex's first T1.7 HALT):
  - **(a) Source-set = `git ls-files` output**, NOT raw filesystem walk. This excludes `__pycache__/**`, `*.pyc`, untracked test cache-harness output, generated artifacts (gitignored).
  - **(b) Extension blocklist:** skip `.pyc`, `.pyo`, `.pyd`, `.so`, `.dll`, `.exe`, `.dylib`, `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.ico`, `.tif`, `.tiff`, `.pdf`, `.docx`, `.xlsx`, `.pptx`, `.odt`, `.ods`, `.odp`, `.mp3`, `.mp4`, `.wav`, `.ogg`, `.webm`, `.mov`, `.avi`, `.mkv`, `.zip`, `.tar`, `.tar.gz`, `.tgz`, `.gz`, `.bz2`, `.xz`, `.7z`, `.bin`, `.dat`, `.svgz`. (`.svg` IS text-XML — keep.)
  - **(c) Null-byte sniff:** for any file passing (a)+(b), read first 8KB; if `\x00` present, treat as binary and skip.
  HALT ONLY if genuine TEXT-FILE violations remain after (a)+(b)+(c). Binary false-positives (`__pycache__/*.pyc`, `tests/fixtures/specialists/wanda/live_artifacts/**/*.mp3`, etc.) are NOT halt conditions.
- **Reference-surface choice (AC-7c.0b-A T1.5):** RECOMMEND option B (brand-new placeholder module `app/parity/contracts/_reference_surface.py`); option A (existing test file) requires non-trivial decoration. Surface as `decision_needed` if Codex picks B and Claude prefers A or vice versa.
- **C4 forbidden_modules canonical list (AC-7c.0b-A T1.6):** RECOMMEND `["app.gates.resume_api", "app.marcus.orchestrator.write_api", "app.specialists.*"]`. Surface as `decision_needed` if Codex's read of graph-runtime module surface differs.

## Files in scope

**New (~15 files):**
- `app/parity/contracts/__init__.py` — public DSL surface exports.
- `app/parity/contracts/_declaration.py` — `SurfaceTransportDeclaration` Pydantic-v2 model per ADR §2.
- `app/parity/contracts/_registry.py` — surface registry + `register_surface` + `iter_registered_surfaces` + `DuplicateSurfaceError`.
- `app/parity/contracts/_decorator.py` — `parity_contract` decorator factory.
- `app/parity/contracts/_audit.py` — self-registration audit harness + `AuditResult` model + `emit_registration_manifest` + CLI entrypoint `python -m app.parity.contracts._audit --declared-floor N`.
- `app/parity/contracts/_sanctum.py` — `SanctumAlignmentDeclaration` Pydantic-v2 model + `declare_sanctum_alignment` + sanctum registry + `iter_sanctum_alignments` + `emit_sanctum_alignment_manifest`.
- `app/parity/contracts/_flake_rate.py` — per-cell flake-rate calculator with AMEND-7a tightened budget (<0.05% for 7c-added cells; <0.1% pre-7c grandfathered).
- `app/parity/contracts/_reference_surface.py` (per T1.5 RECOMMEND B) — placeholder for AC-7c.0b-A reference declaration.
- `app/audit/__init__.py` — package marker.
- `app/audit/errors.py` — `AuditChainIntegrityError` + `AuditChainOrderError` + `AuditChainParentLinkError` per ADR Appendix A.
- `app/audit/chain.py` — `verify_audit_chain(entries: list[TripwireLedgerEntry]) -> None` pure function.
- `tests/audit/__init__.py` (or omit per existing convention; verify at T1).
- `tests/audit/test_override_event_chain_integrity.py` — ≥7 test cases per AC-7c.0b-D.
- `tests/parity/test_dsl_primitive_contract.py` — 5 cases per AC-7c.0b-A test pin.
- `tests/parity/test_sanctum_alignment_dsl.py` — 6 cases per AC-7c.0b-B test pin.
- `tests/parity/test_self_registration_audit.py` — covers AC-7c.0b-C + AC-7c.0b-F.
- `tests/structural/test_tw_7c_4_5_6_detection_scaffolds_present.py` — 3-detector existence + invokability.
- `tests/structural/test_import_linter_c4_target_list_populated.py` — toml parse + non-empty assertion + lint-imports KEPT.
- `tests/unit/parity/test_per_cell_flake_rate_calculator.py` — 4 cases per AC-7c.0b-E test pin.
- `scripts/utilities/detect_tw_7c_4_live_dispatch_scope_creep.py` — TW-7c-4 detector script.
- `scripts/utilities/detect_tw_7c_5_utf8_violations.py` — TW-7c-5 detector script (FR-7c-46 lint pass).
- `scripts/utilities/detect_tw_7c_6_parity_flake.py` — TW-7c-6 50-run harness scaffold.

**Modified (1 file):**
- `pyproject.toml` — populate C4 `forbidden_modules` per T1.6 (recommend `["app.gates.resume_api", "app.marcus.orchestrator.write_api", "app.specialists.*"]` or surface as `decision_needed`). C5 + C6 remain empty (populated by 7c.3a + 7c.4b). KEPT count remains 12 (no new contracts; just target-list change on existing).

**Do NOT modify:**
- The 8 existing transport-parity test files per ADR §3 (refactor lands in 7c.1).
- Any specialist body (`app/specialists/**`).
- Any HIL surface module (`app/gates/**`).
- `state/config/pipeline-manifest.yaml`.
- 7c.0a's ADR (read only).
- 7c.0a's TripwireLedgerEntry (read only; do NOT add `revision`/`revision_history` fields — that's deferred to a post-7c.21 audit-chain hardening pass).
- C5 + C6 forbidden_modules (those are 7c.3a + 7c.4b territory).

## Critical implementation notes

- **K-target 1.4× ≈ ~3.5K LOC ceiling.** DSL package modules ~600-1000 LOC + sanctum DSL ~150 LOC + audit harness ~250 LOC + audit-chain ~150 LOC + 3 detection scripts ~300-500 LOC + 7 test files ~1.0-1.5K LOC + flake-rate calculator ~150 LOC = ~2.6-4K LOC. Possible upper-band approach. Surface for K-budget renegotiation if T1 surfaces decision-needed scope expansions.
- **Dual-gate cross-agent MANDATORY** at T11. Claude reviews FULL diff in fresh context. Codex T10 self-review is supplemental.
- **AMEND-7d-ii THREE separate PASS/FAIL flags** at done-status assertion (TW-7c-4 detection PASS/FAIL + TW-7c-5 detection PASS/FAIL + TW-7c-6 detection PASS/FAIL). Composite all-three-PASS required for done-flip; ANY one FAIL blocks done. Document each flag's status independently in T10 self-review notice + Completion Notes.
- **AMEND-7a tightened per-cell flake budget:** <0.05% for 7c-added cells (1 fail per 2000 runs); <0.1% pre-7c grandfathered (1 fail per 1000 runs). Cell-class distinction via manifest at `_bmad-output/implementation-artifacts/parity-cell-class-manifest.json` (or analogous; surface at T1).
- **Audit-chain test consumes real TripwireLedgerEntry** — do NOT mock. `model_validate(...)` round-trips with synthetic fixtures.
- **No new third-party deps.**
- **Windows portability per NFR-7c-X3** — `pathlib.Path.as_posix()` everywhere; UTF-8 explicit encoding everywhere; no `PYTHONIOENCODING=utf-8` workarounds.
- **Pre-existing UTF-8 violation HALT** — if T1.7 detects pre-existing violations in declared glob, HALT before any code is written. Operator decides whether 7c.2 must close first OR 7c.0b's lint pass starts advisory-only.
- **C4 forbidden_modules population is the highest-risk decision** — Codex's read of the graph-runtime module surface MAY differ from the recommended list. Surface as `decision_needed` at T1.6 if any doubt.
- **Sanctum DSL ships unused** in 7c.0b — NO actual writer registers a sanctum alignment until 7c.17a/17b at Wave 4. 7c.0b's tests exercise the DSL with synthetic declarations only.

## Verification battery (T9)

```bash
# Focused tests (7-8 new test files):
.venv/Scripts/python.exe -m pytest tests/audit/test_override_event_chain_integrity.py tests/parity/test_dsl_primitive_contract.py tests/parity/test_sanctum_alignment_dsl.py tests/parity/test_self_registration_audit.py tests/structural/test_tw_7c_4_5_6_detection_scaffolds_present.py tests/structural/test_import_linter_c4_target_list_populated.py tests/unit/parity/test_per_cell_flake_rate_calculator.py -p no:randomly -q --tb=short

# Plus 7c.0a's tests (regression check; should still pass):
.venv/Scripts/python.exe -m pytest tests/parity/test_tripwire_ledger_entry_shape.py tests/structural/test_adr_0001_parity_contract_dsl_present.py tests/structural/test_import_linter_contracts_c4_c5_c6_present.py -p no:randomly -q --tb=short

# Broad regression slice (NFR-7c-R2; preserve ≥1403 deterministic baseline; 7c.0a-close baseline 3990 passed / 37 failed pre-existing):
.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line

# Class-conformance validator (NFR-7c-R5; expect 11 conforming activation contracts; no regression):
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/

# Import-linter (KEPT count UNCHANGED at 12; C4 target-list populated but contract count is the same):
.venv/Scripts/lint-imports.exe

# Sandbox-AC validator (NFR-7c-M5):
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-0b-scaffold-foundation.md

# AMEND-7d-ii three-flag completeness check (RUN EACH; report each independently):
.venv/Scripts/python.exe scripts/utilities/detect_tw_7c_4_live_dispatch_scope_creep.py
.venv/Scripts/python.exe scripts/utilities/detect_tw_7c_5_utf8_violations.py
.venv/Scripts/python.exe scripts/utilities/detect_tw_7c_6_parity_flake.py --dry-run

# Self-registration audit (initially empty registries; floor=0 → trivially PASS):
.venv/Scripts/python.exe -m app.parity.contracts._audit --declared-floor 0

# Ruff hygiene on the touched files:
.venv/Scripts/python.exe -m ruff check app/parity/ app/audit/ tests/audit/ tests/parity/ tests/structural/ tests/unit/parity/ scripts/utilities/detect_tw_7c_*.py
```

Expected post-7c.0b baseline:
- ≥1403 broad-regression deterministic baseline preserved (no test regression vs 7c.0a-close baseline).
- `lint-imports` KEPT count = 12 (UNCHANGED; C4 target-list populated but contract count same).
- `validate_parity_test_class_conformance.py` reports 11 conforming activation contracts.
- All three TW detectors PASS at scaffold-completeness check.
- Self-registration audit PASS with floor=0.
- Sandbox-AC validator PASS.
- Ruff CLEAN on all touched files.

## T10 + T11

**T10:** Codex G6 self-review at `_bmad-output/implementation-artifacts/_codex-handoff/7c-0b.ready-for-review.md`. Per dropbox protocol — drop the completion notice. Flip story status `in-progress` → `review` in spec file.

**Critical T10 content (per AMEND-7d-ii):** explicitly enumerate THREE separate PASS/FAIL flags:
- TW-7c-4 detection PASS/FAIL
- TW-7c-5 detection PASS/FAIL
- TW-7c-6 detection PASS/FAIL

If ANY flag is FAIL, the story CANNOT advance to T11. Composite "all-three-PASS" is REQUIRED.

**T11:** Claude (separate cold context from Codex dev) does FINAL `bmad-code-review` (**CROSS-AGENT MANDATORY** per governance JSON cross_agent_review_required=true). Review verdict at `_bmad-output/implementation-artifacts/7c-0b-code-review-2026-05-NN.md`. Claude applies remediation cycles per HALT-AND-REMEDIATE; commits the diff (~15 NEW + 1 MODIFIED files); flips `migration-7c-0b-scaffold-foundation: review → done` in sprint-status.yaml.

## Boundary

- **HALT and surface to operator on:**
  (a) 7c.0a status NOT `done` (predecessor not closed; this prompt was dispatched too early).
  (b) Pre-existing UTF-8 violations in declared glob — operator decides recovery path.
  (c) ADR slot or TripwireLedgerEntry path collision — design ambiguity surface.
  (d) C4 forbidden_modules canonical list ambiguous — Codex's read of graph-runtime surface differs from recommended.
  (e) AMEND-7d-ii three-flag check returns ANY FAIL — DO NOT advance to T10 until all three PASS.
  (f) K-actual exceeds 1.7× target (~4.25K LOC) — surface for K-budget renegotiation; scaffold scope likely too broad.
  (g) ANY sandbox-AC violation — should not happen given dev-agent-only ACs.
  (h) Broad-regression delta < 0 vs 7c.0a-close baseline — investigate root cause; do NOT skip the test.
  (i) `lint-imports` KEPT count changes from 12 — 7c.0b should NOT add or remove contracts; only populate C4 target-list.
  (j) Class-conformance validator deviates from 11 contracts.

- **Do NOT touch:**
  - 8 existing transport-parity test files per ADR §3 (refactor is 7c.1).
  - Any specialist body (`app/specialists/**`).
  - Any HIL surface module (`app/gates/**`).
  - `state/config/pipeline-manifest.yaml`.
  - 7c.0a's ADR (`docs/dev-guide/adr/0001-parity-contract-dsl.md` — read only).
  - 7c.0a's TripwireLedgerEntry schema (`app/models/tripwire_ledger.py` — read only; do NOT add `revision`/`revision_history` fields).
  - C5 + C6 `forbidden_modules` (those are 7c.3a + 7c.4b territory).
  - Composition Spec (`docs/dev-guide/composition-specification.md` — DSL is below the spec layer per §3.5 invariant).

- **Do NOT introduce:**
  - New third-party deps.
  - Per-transport addendums (ADR §4 escape-hatch policy says addendum requires party-mode consensus; 7c.0b SHALL NOT introduce any).
  - New default-encoding sites (`open()` without `encoding="utf-8"`, etc.).
  - Mocking of TripwireLedgerEntry in audit-chain tests.
  - YAML registration mechanism (ADR §1 picked decorator; YAML is reserved for post-Slab-7c).
  - Entry-point registration (ADR §1; reserved for post-Slab-7c plugin extensibility).
```

---

## Operator dispatch checklist (before sending this prompt to Codex)

1. ☐ Verify `migration-7c-0a-decision-foundation: done` in BOTH spec file AND sprint-status.yaml. (Confirmed 2026-05-04 post-commit `f926867`.)
2. ☐ Run `.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-0b-scaffold-foundation.md` → expect PASS.
3. ☐ AMELIA-P2 freshness check: Claude re-diffs `migration-7c-0b-scaffold-foundation.md` against this prompt; if spec hash changed since 2026-05-04 authoring, regenerate this prompt before dispatch.
4. ☐ Verify governance JSON entry for 7c-0b is current (dual-gate; cross_agent_review_required=true; K=1.4; pts=3; prerequisite_stories=[7c-0a]).
5. ☐ Confirm sprint-status.yaml shows `migration-7c-0b-scaffold-foundation: ready-for-dev`.
6. ☐ Pre-flight TW-7c-5 dry-run on the current repo state to anticipate the T1.7 HALT condition. If pre-existing UTF-8 violations exist, decide recovery path BEFORE dispatch (close 7c.2 first OR 7c.0b advisory-only mode).
7. ☐ Dispatch this prompt to Codex; Codex flips status `ready-for-dev → in-progress` at T1 start.

## Post-Codex-T10 dropbox-watch protocol

1. ☐ Codex drops `_bmad-output/implementation-artifacts/_codex-handoff/7c-0b.ready-for-review.md` upon T10 completion.
2. ☐ Claude (separate cold context) reads the dropbox notice + the ~15-file diff; runs `bmad-code-review` (T11; **CROSS-AGENT MANDATORY**).
3. ☐ Claude verifies AMEND-7d-ii three-flag PASS status independently (each detector run + each flag confirmed PASS).
4. ☐ Claude applies remediation cycles per HALT-AND-REMEDIATE if any.
5. ☐ Claude commits + flips `migration-7c-0b-scaffold-foundation: review → done` in sprint-status.yaml.
6. ☐ At 7c.0b close, **Wave 1 stories 7c.1, 7c.3a, 7c.3b unblock** + **7c.4a unblocks** for dispatch (already ready-for-dev with dispatch held). Wave 2 follows after 7c.4a + 7c.4b close.
