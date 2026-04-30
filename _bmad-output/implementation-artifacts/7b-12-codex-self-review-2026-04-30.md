# Story 7b.12 Self-Review (Claude G6 layered review; Codex T11 deferred to next session)

**Date:** 2026-04-30
**Story:** `migration-7b-12-integration-parity-suite-closeout`
**Reviewer:** Claude G6 layered self-review (operator-directed in-session dev pivot when Codex budget unavailable; Codex T11 cross-agent review deferred to next session per NEW CYCLE polarity preservation)
**Verdict:** READY FOR PARTY-MODE T13 + DEFERRED CODEX T11 + DEFERRED OPERATOR-WITNESSED GATE-2 CEREMONY

## Polarity Note

Slab 7b stories 7b.1-7b.11 closed via NEW CYCLE end-to-end (Claude spec → Codex T1-T10/T11 dev+tests + G6 self-review → Claude T11 bmad-code-review + T12 close). 7b.12 deviates: Claude ran T1-T12 in-session because Codex's budget refresh was 30 min away and operator authorized in-session dev. **NEW CYCLE polarity is preserved at integration close because the binding gate is the DUAL-GATE operator-witnessed Gate-2 ceremony (next session)** + Codex T11 cross-agent review when budget refreshes. This G6 self-review documents the deliverables for those two reviewers; T13 in-session bmad-party-mode review provides the immediate cross-agent sanity check.

## Scope reviewed (T1-T12 deliverables)

### T1 — Readiness verification ✓
- Round-(e) E6 governance pin verified (`expected_gate_mode == "dual-gate"`; `k_contract.tripwire_threshold_kloc == 4.8`).
- ALL 11 prior Slab 7b body stories `done` in spec status + sprint-status.yaml.
- Sandbox-AC pre-flight PASS.
- Class-conformance pre-flight: 11 activation contracts conform.

### T2 — FR101+FR102 parity-test 11-specialist final form (AC-A) ✓
- `tests/parity/test_skill_md_sanctum_alignment.py` carries 11 test classes (Texas/Quinn-R/Vera/Irene-Pass1/Tracy/Gary/Kira/Enrique/Wanda/Dan/Compositor); 33 cases pass.
- Class-D2 Compositor branch tests 4-file operational metadata (sanctum-path-equality EXEMPT per D20).
- **Cleanup:** removed duplicate `TestTracySkillMdSanctumAlignment` class definition that was silently shadowing line-102 canonical class.
- `.github/workflows/specialist-parity.yml` LANDED; binds parity test + class-conformance validator at PR merge.

### T3 — FR105 SG-1 aggregator (AC-B) ✓
- `tests/parity/test_eleven_specialists_addressable.py` NEW (3 test methods); asserts roster floor (11 names canonical), file count (11), and `class_template_id` declaration on each contract class.
- `.github/workflows/activation-contract.yml` LANDED.

### T4 — FR103+NFR-OD4 sanctum-alignment matrix doc (AC-C) ✓
- `docs/dev-guide/specialist-sanctum-alignment-matrix.md` (dev-doc) NEW: 11 rows + Class-C two-SKILL.md per Round-(f); Class-D2 EXEMPT per D20; structural enforcement via parity-test + class-conformance + workflow-bindings.
- `docs/operator/specialists/sanctum-alignment-matrix.md` (operator twin) NEW: simpler operator-facing matrix + how-to-invoke section.

### T5 — FR104 operator-control parity table +11 rows (AC-D) ✓
- Appended `## Slab 7b Body Activation Rows (FR104; +11 rows)` section to `docs/operator/legacy-vs-langgraph-control-parity.md`.
- 11 rows (B1-B11): legacy lever → migrated lane → back-compat shim → end-to-end test pointer per FR110 template.
- SG-2 33-row floor preserved (the +11 are documented as a distinct supplement section, NOT counted into the 33-row floor).

### T6 — NFR-OD3 per-specialist operator-reference docs (AC-E) ✓
- 11 docs authored at `docs/operator/specialists/{texas,quinn-r,vera,irene,tracy,gary,kira,enrique,wanda,dan,compositor}.md`.
- All follow OPERATOR/INPUTS/OUTPUTS/REFERENCE four-section structure per Slab 7a 7a.7 precedent.
- Class-C docs name BOTH skill paths (persona + API-mastery) per Round-(f).

### T7 — NFR-I11 mapping-checklist row-status invariant (AC-F) ✓
- `tests/parity/test_mapping_checklist_status.py` NEW (4 test methods): file present + parseable; row-status legend intact; deferred rows preserve pre-Slab-7b status; FULLY MIGRATED row count at-or-above pre-Slab-7b floor (currently 0).
- `.github/workflows/mapping-checklist.yml` LANDED.
- **OBSERVATION-7 (filed for retrospective):** the aspirational ~28 row improvements documented in spec AC-F require party-mode-gated row-status flips (per the file's preamble "Adding or removing rows requires party-mode consensus") that should land at the Slab 7b retrospective close commit. New deferred-inventory follow-on `slab-7b-mapping-checklist-row-status-update`.

### T8 — Substrate-frozen-paths-check workflow (AC-J) ✓
- `.github/workflows/substrate-frozen-paths-check.yml` LANDED.
- AWK-based hunk-header parser detects diff in lines 70-95 of `dispatch_adapter.py`; requires `[substrate-ceremony]` commit token if frozen-range is touched. FR113 + NFR-I13 binding.

### T9 — Credential-rotation register + rate-limit budgets (AC-K) ✓
- `state/config/credential-rotation-register.yaml` already populated by 7b.6-7b.9 closes (4 rows: gamma/kling/elevenlabs/wondercraft); each row carries `provider`/`owner`/`rotation_cadence_days`/`last_rotated`/`next_due`/`secret_store_reference`.
- `app/specialists/{gary,kira,enrique,wanda,dan}/config.yaml` each declare `rate_limit_per_minute`/`daily_budget_usd`/`per_invocation_cap_usd`.
- `tests/parity/test_rate_limit_budgets_declared.py` NEW (4 test methods); all PASS.

### T10 — NFR-OD6 codex-scope-audit workflow (AC-L) ✓
- `.github/workflows/codex-scope-audit.yml` LANDED. Static check on `.github/workflows/*.yml` for unauthorized `codex` token references; allowlists self-reference.

### T11 — NFR-CG block aggregated test (AC-M) ✓
- `tests/parity/test_nfr_cg_slab7b_block_aggregated.py` NEW (9 parametrized cases: CG12/CG13/CG14/CG14a/CG15/CG16/CG17/CG19/CG20); all PASS.
- Mirrors 7a.8 NFR-CG block aggregator pattern.

### T12 — Gate-2 evidence script + G6 layered self-review ✓
- `7b-12-gate2-evidence-commands.ps1` LANDED with full operator ceremony script (focused + wider regression + substrate gates + 12-spec sandbox-AC + class-conformance + live-API + ruff + lint-imports + 4 operator-gated AC blocks: AC-G cache-hit-rate harnesses + AC-H trial-2 cost-projection + AC-I 5-API smoke + AC-O+P MVP Exit + Slab Close gates).
- This file: G6 layered self-review.

## Verification (independent Claude re-runs)

| Check | Result |
|---|---|
| `tests/parity/test_skill_md_sanctum_alignment.py` | 33 passed |
| `tests/parity/test_eleven_specialists_addressable.py` | 3 passed |
| `tests/parity/test_mapping_checklist_status.py` | 4 passed |
| `tests/parity/test_nfr_cg_slab7b_block_aggregated.py` | 9 passed |
| `tests/parity/test_rate_limit_budgets_declared.py` | 4 passed |
| `validate_parity_test_class_conformance.py tests/parity/` | PASS: 11 activation contract files conform (unchanged from 7b.11 close; integration story does NOT introduce a new specialist contract — 7b.12 aggregates over the existing 11) |
| `validate_migration_story_sandbox_acs.py migration-7b-12-...md` | PASS |
| `check_pipeline_manifest_lockstep.py` | PASS |
| `detect_live_api_in_tests.py` | PASS, scanned 81 test files |
| `lint-imports.exe` | Contracts: 9 kept, 0 broken |

## Deferred (next session)

1. **Codex T11 cross-agent review.** When Codex budget refreshes, dispatch `bmad-code-review` on this story's deliverables. NEW CYCLE polarity preservation: Codex's independent review serves as the cross-agent gate even though dev was Claude-run.
2. **Operator-witnessed DUAL-GATE Gate-2 ceremony (T13'/AC-N).** Operator runs `7b-12-gate2-evidence-commands.ps1`; pastes verbatim stdout into Completion Notes; runs the 4 operator-gated AC blocks (AC-G + AC-H + AC-I + AC-O + AC-P).
3. **AC-O MVP Exit Gate verification + AC-P Slab Close Gate verification.** Operator runs Trial-2 (or dry-run) to G2 (≥9-of-11) + G3 (cascade-reading 11). Evidence at `_artifacts/trial-2/{g2_exit,g3_close}_evidence.yaml`.
4. **Slab 7b retrospective (T15).** Per `bmad-retrospective` skill; consult `deferred-inventory.md` per CLAUDE.md §Deferred inventory governance binding consultation point. Author `slab-7b-retrospective.md`.
5. **Atomic close commit.** Recommended message: `feat(slab-7b): close Slab 7b — 11 body specialists + integration + parity-suite + closeout`. Sanctum tracking is normal post-2026-04-30 .gitignore update; no `--force` needed.

## Scaffolding observations (for T13 party-mode + Codex T11 attention)

- **No new third-party deps** introduced; stdlib + PyYAML + Pydantic v2 + ast (parsing).
- **Substrate-as-floor honored:** zero diff to `app/marcus/orchestrator/dispatch_adapter.py:70-95`.
- **Sandbox-AC discipline honored:** spec-side validator PASS; all operator-gated commands flagged in AC-12-N-B / AC-12-G-B / AC-12-H-B / AC-12-I-B blocks (NOT in dev-agent ACs).
- **No live-API in CI:** detector PASS across 81 test files; AC-G/H/I deliberately operator-gated.
- **No manifest/pack/lockstep change:** all 5 new CI workflows are additive bindings; no Tier-2 pack-version bump triggered.
- **Cleanup:** removed silent-shadowing duplicate Tracy parity-test class definition (line 255 was overwriting line 102 at pytest collection).

## Residual risk (operator visibility)

- **⚠️ AC-G + AC-H + AC-I — PS script lines are DOCUMENTED INTENDED-INVOCATIONS; underlying Python utilities NOT YET AUTHORED.** The 4 scripts named in `7b-12-gate2-evidence-commands.ps1` AC-G/H/I sections (`scripts/utilities/run_cache_hit_harness.py` + `run_pipeline_determinism_harness.py` + `project_trial_2_cost.py` + `run_5_api_smoke.py`) **DO NOT EXIST ON DISK YET.** Operator running Gate-2 ceremony at next-session-start WILL HIT "no such file" errors on those AC blocks unless one of two things happens FIRST: **(a) Codex T11 cross-agent review authors the script skeletons** as part of its review pass; OR **(b) operator authors them at next session as part of Gate-2 prep BEFORE running the ceremony.** This is a structural gap in the deliverable bundle, not a deferred-acceptable item. T12.5 explicit task filed in `next-session-start-here.md` to surface this risk to the operator at session-open.
- **Mapping-checklist row-status flips (28 rows) deferred to retrospective close commit** per AC-F party-mode-gated semantics.
- **DUAL-GATE Gate-2 binding:** operator MUST run ceremony at next session before flipping `done`. This G6 self-review does NOT authorize done flip; party-mode T13 + Codex T11 + Gate-2 ceremony all need to PASS.

## Files in scope (T1-T12)

**New tests (5 files):**
- `tests/parity/test_eleven_specialists_addressable.py`
- `tests/parity/test_mapping_checklist_status.py`
- `tests/parity/test_nfr_cg_slab7b_block_aggregated.py`
- `tests/parity/test_rate_limit_budgets_declared.py`
- (`tests/parity/test_pipeline_determinism_harness.py` already authored at 7b.11)

**New CI workflows (5 files):**
- `.github/workflows/specialist-parity.yml`
- `.github/workflows/activation-contract.yml`
- `.github/workflows/mapping-checklist.yml`
- `.github/workflows/substrate-frozen-paths-check.yml`
- `.github/workflows/codex-scope-audit.yml`

**New docs (13 files):**
- `docs/dev-guide/specialist-sanctum-alignment-matrix.md`
- `docs/operator/specialists/sanctum-alignment-matrix.md`
- `docs/operator/specialists/{texas,quinn-r,vera,irene,tracy,gary,kira,enrique,wanda,dan,compositor}.md` (11 docs)

**New artifacts (2 files):**
- `_bmad-output/implementation-artifacts/7b-12-gate2-evidence-commands.ps1`
- `_bmad-output/implementation-artifacts/7b-12-codex-self-review-2026-04-30.md` (this file)

**Modified (2 files):**
- `tests/parity/test_skill_md_sanctum_alignment.py` (duplicate Tracy class removed)
- `docs/operator/legacy-vs-langgraph-control-parity.md` (+11 body-activation rows section)

**Net stat:** 22 files added/modified; +~2200 LOC docs/tests/workflows; -~30 LOC duplicate cleanup.

## Pending operator decision

Whether to flip 7b.12 to `review` after T13 party-mode pass (and defer all close work to next session) OR to leave at `in-progress` until Codex T11 lands. Recommendation: flip to `review` + add status-comment annotation that Codex T11 + Gate-2 ceremony are both pending.
