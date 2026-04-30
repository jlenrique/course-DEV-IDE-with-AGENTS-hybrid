# Codex dev-story prompt — Story 7b.12 Slab 7b Integration + Parity-Test Suite + Closeout (Wave-6)

**Cycle:** Claude spec → Codex dev+tests → Claude bmad-code-review + commit + flip done. **Operator-witnessed Gate-2 ceremony at T12 boundary (DUAL-GATE).**
**Wave:** 6 — strict-last; opens only after ALL 11 prior Slab 7b body stories `done` (7b.1 through 7b.11). 7b.12 is the Slab 7b closer.
**Gate:** **DUAL-GATE** (per Round-(e) governance JSON `7b-12`; rationale: `operator_acceptance_gate + invariant_preservation`; mirrors Slab 7a 7a.8 precedent + Murat integration-tier risk argument).
**Class:** Integration (NOT specialist class; aggregates SG-1/2/3/4 across 11 specialists).

**K-contract tripwire 4.8K binding-hard (Round-(e) E6/Murat):**
- If LOC count >4.8K, party-mode review for scope reduction; four named remediation paths from Round-(a) John A1: scope-cut / budget-exception / trial-redesign / Slab-7c precondition deferral. Records at `tripwire_escalation_record_path`.

**Round-(a) John A1 trial-2 cost-projection AC binding (SR-T6 mitigation):**
- AC-12-H: projected Trial-2 cost ≤ BS-3 ceiling per Journey 5 fork. If exceeded, four named remediation paths.

**STATUS:** Spec READY-FOR-DEV at `_bmad-output/implementation-artifacts/migration-7b-12-integration-parity-suite-closeout.md` (Claude-authored 2026-04-29; sandbox-AC validator PASS; 18 ACs A-R + 15 task blocks T1-T15). 4pt budget. Dev opens only at 7b.11 close.

---

```
Run bmad-dev-story on Story 7b.12 (Slab 7b Wave-6 strict-last; Integration + parity-suite aggregation + closeout; DUAL-GATE per governance JSON; mirrors Slab 7a 7a.8 precedent — final form parity tests + 5 CI workflows + sanctum-alignment matrix doc + 11 operator-reference docs + +11 operator-control parity rows + ~28 mapping-checklist row improvements + 5-API live-binding smoke (operator-gated) + trial-2 cost-projection dry-run + credential-rotation register + per-specialist rate-limit budgets + Slab 7b retrospective + closeout artifacts).

## Required reading (read in order)

1. **Story spec:** `_bmad-output/implementation-artifacts/migration-7b-12-integration-parity-suite-closeout.md` (status: ready-for-dev; 18 ACs A-R; 15 tasks; you own T1-T13; Claude owns T14-T15 close).
2. **Round-(e) governance JSON** — `docs/dev-guide/migration-story-governance.json` §`stories.7b-12`:
   - `expected_gate_mode == "dual-gate"`
   - `k_contract.tripwire_threshold_kloc == 4.8`
   - **Verify with:** `.venv/Scripts/python.exe -c "import json; d = json.load(open('docs/dev-guide/migration-story-governance.json', encoding='utf-8')); entry = d['stories']['7b-12']; assert entry['expected_gate_mode'] == 'dual-gate'; assert entry['k_contract']['tripwire_threshold_kloc'] == 4.8; print('Round-(e) E6 verified PASS for 7b-12')"`
3. **Slab 7a 7a.8 precedent** — `_bmad-output/implementation-artifacts/migration-7a-8-integration-parity-test-suite-slab-7a-closeout.md` + `_bmad-output/implementation-artifacts/7a-8-code-review-2026-04-29.md`. **PRIMARY TEMPLATE.** Mirror structure: parity-test final form + Composition Spec invariant suite + NFR-CG block aggregator + closeout deliverables + Gate-2 evidence script + retrospective draft. 7b.12 mirrors 7a.8 patterns.
4. **All 11 prior Slab 7b body stories** — `_bmad-output/implementation-artifacts/migration-7b-{1..11}-*.md`. Confirm ALL `done` in spec status + sprint-status.yaml at T1 hard checkpoint.
5. **PRD** — `_bmad-output/planning-artifacts/prd-slab-7b-specialist-activation-eleven.md` §FR88 + §FR101-FR107 + §NFR-CG12-CG20 + §NFR-I9-I13 + §NFR-OD3-OD6 + §Success Criteria (BS-2 trial-2 readiness; BS-3 cost ceiling; SG-1/2/3/4 aggregated).
6. **Epic Story 7b.12** — `_bmad-output/planning-artifacts/epics-slab-7b-specialist-activation-eleven.md` §Story 7b.12 (lines 990-1067).
7. **bmad-retrospective skill** — `.claude/skills/bmad-retrospective/` for T15 retrospective authoring.
8. **CLAUDE.md** — §LangChain/LangGraph migration governance + §Deferred inventory governance (binding consultation point at Epic retrospective per CLAUDE.md) + bmad-memory-gitignore-force-add-policy.
9. **`docs/dev-guide/bmb-sanctum-alignment-checklist.md`** (FR108) — SG-4 source of truth for sanctum-alignment matrix doc.
10. **Round-(f) Class-C two-SKILL.md ratification** — recorded in `sprint-status.yaml::tripwire_events::wave_3_first_port_tripwire::notes`. **Sanctum-alignment matrix (AC-C) MUST list both skill paths for Class-C specialists** (persona at `bmad-agent-{name}/` + API-mastery at `bmad-agent-{api-name}/`).

## T1 hard checkpoints (HALT-AND-SURFACE if violated)

- Round-(e) governance pin verified (one-liner above; assertions PASS).
- **ALL 11 prior Slab 7b body stories `done` in BOTH spec status + sprint-status.yaml** — strict prereq. If ANY story not-done (e.g., 7b.11 Compositor still in `review`), HALT.
- All 6 Wave-N close ledger entries present at `sprint-status.yaml::tripwire_events`: `wave_1_close`, `wave_2a_close` (or absent if 7b.4 didn't fire tripwire), `wave_2b_close`, `wave_3_first_port_tripwire`, `wave_3_parallel_close_kira`, `wave_3_parallel_close_enrique`, `wave_4_close`, `wave_5a_close`, `wave_5b_close`.
- All 11 specialist parity tests + 11 chain tests already authored by prior stories (consume; aggregate; verify all PASS).
- Class-A/B/C+/C/D1/D2 templates active in validator (6 classes; verified via `validate_parity_test_class_conformance.py tests/parity/` PASS).
- Sandbox-AC validator pre-flight PASS on this spec + on all 11 prior body specs (re-run per NFR-CG12).
- 5 API client modules present at `scripts/api_clients/` (gamma_api_client.py, kling_client.py, elevenlabs_client.py, wondercraft_client.py, dan-api-tbd-resolved client if applicable per 7b.10 T1 resolution).

## Files in scope

**New (tests; ≥4 files):**
- `tests/parity/test_eleven_specialists_addressable.py` — SG-1 aggregator (AC-B)
- `tests/parity/test_mapping_checklist_status.py` — SG-2 aggregator; ~28 row-improvements assertion (AC-F)
- `tests/parity/test_nfr_cg_slab7b_block_aggregated.py` — 9-case NFR-CG aggregator mirrors 7a.8 NFR-CG block test (AC-M)
- `tests/parity/test_rate_limit_budgets_declared.py` — 5-specialist rate-limit-budget aggregator (AC-K)

**New (CI workflows; 5 files):**
- `.github/workflows/specialist-parity.yml` — bound to FR101 + FR102 (AC-A; NFR-I9)
- `.github/workflows/activation-contract.yml` — bound to FR105 (AC-B; NFR-I10)
- `.github/workflows/mapping-checklist.yml` — bound to NFR-I11 (AC-F)
- `.github/workflows/substrate-frozen-paths-check.yml` — bound to FR113 + NFR-I13 (AC-J)
- `.github/workflows/codex-scope-audit.yml` — bound to NFR-OD6 (AC-L)

**New (docs; ≥13 files):**
- `docs/dev-guide/specialist-sanctum-alignment-matrix.md` (AC-C dev-doc; 11 rows)
- `docs/operator/specialists/sanctum-alignment-matrix.md` (AC-C operator-doc twin)
- `docs/operator/specialists/{texas,quinn-r,vera,irene,tracy,gary,kira,wanda,enrique,dan,compositor}.md` (AC-E; 11 docs; OPERATOR/INPUTS/OUTPUTS/REFERENCE four-section per Slab 7a 7a.7 precedent)

**New (state):**
- `state/config/credential-rotation-register.yaml` (AC-K; 5 rows: gamma/kling/elevenlabs/wondercraft/dan-api-tbd-resolved)

**New (scripts):**
- `scripts/utilities/run_5_api_smoke.py` (AC-I; operator-gated; ≤3 canaries/API; cost ≤$0.40/canary)
- `scripts/utilities/project_trial_2_cost.py` (AC-H; trial-2 cost-projection per Round-(a) John A1; SR-T6 mitigation)
- (`scripts/utilities/run_cache_hit_harness.py` and `run_pipeline_determinism_harness.py` may be pre-existing from 7b.10 + 7b.11; reuse if so; create only if absent)

**New (artifacts):**
- `_bmad-output/implementation-artifacts/7b-12-gate2-evidence-commands.ps1` (AC-N; operator Gate-2 ceremony script)
- `_bmad-output/implementation-artifacts/7b-12-codex-self-review-2026-04-XX.md` (T13 G6 self-review)
- `_bmad-output/implementation-artifacts/slab-7b-retrospective.md` (T15; per `bmad-retrospective` skill)

**Modified (extensions; ≥3 files):**
- `tests/parity/test_skill_md_sanctum_alignment.py` — extend to 11-specialist final form (AC-A); add Class-D2 Compositor branch per D20 (sanctum-path-equality EXEMPT)
- `docs/operator/legacy-vs-langgraph-control-parity.md` — +11 rows aggregated from body stories (AC-D)
- `app/specialists/{gary,kira,enrique,wanda,dan}/config.yaml` — verify rate-limit-budget keys present (added by body stories; this story aggregates verification)

**Closeout (D12 protocol):**
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — flip 7b.12 to done; epic flip in-progress→done
- `next-session-start-here.md` — pivot to Trial-2 launch (or Slab 7c precondition) hot-start
- `_bmad-output/planning-artifacts/deferred-inventory.md` — file Slab 7b-closing follow-ons per CLAUDE.md §Deferred inventory governance Epic-retrospective consultation

**Do NOT modify:**
- `app/marcus/orchestrator/dispatch_adapter.py` lines 70-95 (substrate-frozen per FR113).
- 7b.1-7b.11 substrate (consume only; aggregating).
- Specialist body files (`app/specialists/<name>/_act.py`) — read-only consumers.
- `_bmad/memory/bmad-agent-{name}/` sanctum dirs (read-only consumers).
- Manifest, pack, v4.2 prompt pack.
- scaffold-v0.2-D2-pipeline templates at `docs/dev-guide/scaffolds/scaffold-v0.2-D2-pipeline/` (consume; refinements via post-trial-2 follow-on).

## Critical implementation notes

- **Mirror Slab 7a 7a.8 patterns:** parity-test final form + NFR-CG block aggregator + 5 CI workflow bindings + sanctum-alignment matrix + closeout deliverables + Gate-2 evidence script + retrospective draft. The Codex's 7a.8 implementation in `Dev Agent Record` is a goldmine of reusable patterns — consult for harness, aggregator, and CI-binding shape. **DO NOT re-derive from scratch.**
- **AC-A 11-specialist final form (sanctum-alignment matrix):** the parity test was extended at each body story close (7b.1 = first row; 7b.2 = +row; ...; 7b.11 = 11th row). 7b.12 verifies all 11 PASS as final form. Class-D2 Compositor branch: sanctum-path-equality EXEMPT per D20 (verifies sidecar 4-file pattern instead of 6-file BMB equality).
- **AC-B SG-1 aggregator:** `len(roster) == 11`; name-set equality `{texas, quinn_r, vera, irene, tracy, gary, kira, wanda, enrique, dan, compositor}`. Bind workflow at `.github/workflows/activation-contract.yml`.
- **AC-C sanctum-alignment matrix (Class-C two-SKILL.md per Round-(f)):** for Class-C specialists (Gary/Kira/Enrique/Wanda), list BOTH `skills/bmad-agent-{specialist}/SKILL.md` (persona) AND `skills/bmad-agent-{api-name}/SKILL.md` (API-mastery). For Class-A/B/D1: single SKILL.md at `skills/bmad-agent-{name}/SKILL.md`. For Class-D2 Compositor: SKILL.md at `skills/compositor/SKILL.md` (no persona-skill at `bmad-agent-compositor`); EXEMPT from FR101.iv per D20.
- **AC-F mapping-checklist row-status (~28 improvements):** test asserts ~28 row improvements vs pre-Slab-7b baseline; deferred rows (§05B/§6.2/§6.3/§7.5/§14.5/§15) retain pre-Slab-7b status legend (NOT regressed). Bind workflow at `.github/workflows/mapping-checklist.yml`.
- **AC-G + AC-H + AC-I (operator-gated):** these three ACs run via Gate-2 ceremony at T12 (operator-only). Codex authors the runner scripts at T8-T9; operator runs them at T12 + pastes verbatim stdout/JSON into Completion Notes.
- **5-API live-binding smoke cost ceiling (AC-I):** $6.00 total ceiling (5 APIs × ≤3 canaries × ≤$0.40/canary). If exceeded, story HALTs + party-mode escalation. Document spend in evidence JSON.
- **Trial-2 cost-projection (AC-H; Round-(a) John A1; SR-T6 mitigation):** project Trial-2 cost from per-specialist token counts × per-specialist rate × volume estimate (cite PRD §Journey 5). If projection > BS-3 ceiling, HALT + four named remediation paths (scope-cut / budget-exception / trial-redesign / Slab-7c precondition deferral) + party-mode escalation per Round-(a) A1.
- **AC-J substrate-frozen-paths-check workflow:** assert no diff hunk touches `app/marcus/orchestrator/dispatch_adapter.py:70-95` (substrate-as-floor per FR113) absent ceremony commit pattern. Ceremony pattern: commit message MUST contain `[substrate-ceremony]` token + party-mode-consensus link in body. Workflow runs at PR-merge as required check.
- **AC-K credential register (NFR-CG19) + rate-limit budgets (NFR-CG20):** 5 rows in `state/config/credential-rotation-register.yaml`; per-specialist rate-limit declared in 5 API-bound specialists' config.yaml; aggregator test PASS.
- **AC-L codex-scope-audit workflow:** static check on `.github/workflows/*.yml` files; no workflow file references `codex` or invokes Codex CLI absent governance-JSON `7b-{N}` entry naming Codex as author. Violation blocks PR merge.
- **AC-M NFR-CG block aggregator:** mirrors 7a.8 `tests/parity/test_nfr_cg_block_aggregated.py` pattern. 9 cases (CG12/CG13/CG14/CG14a/CG15/CG16/CG17/CG18/CG19/CG20). Each asserts artifact-exists + criterion-met.
- **AC-O MVP Exit Gate (G2 + 9-of-11):** verify Trial-2 reaches G2 cleanly with real content from ≥9-of-11 specialists (≥3 per class); no fixture-stub fallback; no silent gate-bypass; SG-1/SG-2/SG-3 green (SG-4 verified at AC-P Slab Close).
- **AC-P Slab Close Gate (G3 + 11 cascade-reading):** Trial-2 reaches G3 with all 11 specialists; cascade-reading verified per R8 Mary clarification (Wanda + Tracy contribute via Pass-2 cascade audit logs; not standalone rows). DO NOT conflate AC-O and AC-P — different evidence requirements.
- **AC-Q closeout deliverables (D12 protocol):** sprint-status flip + next-session-start-here pivot + deferred-inventory file + retrospective. Per CLAUDE.md §Deferred inventory governance, run `bmad-retrospective` consultation point during retrospective.
- **K-contract tripwire 4.8K binding-hard:** if cumulative LOC count >4.8K, HALT and surface to operator + party-mode for scope reduction per Round-(e) E6/Murat. Four named remediation paths per Round-(a) A1.
- **DUAL-GATE Gate-2 ceremony (operator-witnessed):** Codex authors `7b-12-gate2-evidence-commands.ps1` at T12 (similar to 7a.8 Gate-2 script); operator runs full battery + 5-API smoke + trial-2 cost-projection at T12 boundary; pastes verbatim stdout into Completion Notes; verifies all 14 evidence blocks PASS (one per AC).
- **PyYAML, NOT ruamel.** No new third-party deps for dev-agent path. httpx allowed (operator-gated 5-API smoke).

## Verification battery (T11)

```bash
.venv/Scripts/python.exe -m pytest tests/parity/test_skill_md_sanctum_alignment.py tests/parity/test_eleven_specialists_addressable.py tests/parity/test_mapping_checklist_status.py tests/parity/test_nfr_cg_slab7b_block_aggregated.py tests/parity/test_rate_limit_budgets_declared.py -q --tb=short
.venv/Scripts/python.exe -m pytest tests/unit/manifest tests/integration/marcus tests/composition tests/parity tests/structural tests/unit/marcus tests/specialists tests/cli tests/unit/models -q --tb=line --ignore=tests/integration/marcus/test_directive_confirm_or_edit_prompt.py
.venv/Scripts/python.exe scripts/utilities/check_pipeline_manifest_lockstep.py
.venv/Scripts/python.exe scripts/utilities/detect_live_api_in_tests.py
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7b-12-integration-parity-suite-closeout.md
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/    # MUST pass with ALL 6 classes (A/B/C+/C/D1/D2)
.venv/Scripts/python.exe -m ruff check tests/parity scripts/utilities/run_5_api_smoke.py scripts/utilities/project_trial_2_cost.py
.venv/Scripts/lint-imports.exe
```

Expected: zero new failures vs post-7b.11 baseline. **All 11 specialists addressable** (SG-1 aggregated). **~28 mapping-checklist rows improved** (SG-2 aggregated). **All 6 Composition Spec invariants green** (SG-3 aggregated; carry-forward from 7a.8). **All 11 SKILL.md sanctum-alignment rows PASS** (SG-4 aggregated).

## T12 + T13 + T14 + T15

- **T12 (Codex):** author Gate-2 evidence script `_bmad-output/implementation-artifacts/7b-12-gate2-evidence-commands.ps1`; **operator runs Gate-2 ceremony** (full battery + 5-API smoke + trial-2 cost-projection); pastes verbatim stdout into Completion Notes; verifies AC-G + AC-H + AC-I + AC-N evidence blocks PASS.
- **T13 (Codex):** G6 self-review at `_bmad-output/implementation-artifacts/7b-12-codex-self-review-2026-04-XX.md`. Flip status `in-progress → review`.
- **T14 (Claude):** bmad-code-review at `7b-12-code-review-2026-04-XX.md`; remediation cycle 1 if PASS-WITH-PATCH; verify 18 ACs all PASS; verify all 5 CI workflows landed + bound; verify Gate-2 ceremony evidence in Completion Notes; sprint-status flip done; epic flip in-progress→done; next-session-start-here.md pivot to Trial-2 launch (or Slab 7c precondition).
- **T15 (Claude):** Slab 7b retrospective per `bmad-retrospective` skill; consult `_bmad-output/planning-artifacts/deferred-inventory.md` for next-Epic preparation per CLAUDE.md §Deferred inventory governance binding consultation point. Author `_bmad-output/implementation-artifacts/slab-7b-retrospective.md`. **Slab 7b is now CLOSED.** Force-add gitignored sanctum dirs (`_bmad/memory/bmad-agent-{name}/` for the 11 specialists if any not yet committed).

## Boundary

**HALT-AND-SURFACE on:**
- (a) ANY of 11 prior body stories not `done` in spec status + sprint-status.yaml — strict prereq violated
- (b) Round-(e) governance pin mismatch (E6 assertion FAIL)
- (c) substrate-frozen-paths violation (any diff to dispatch_adapter.py:70-95 absent ceremony)
- (d) sandbox-AC violation (re-run on this spec + all 11 prior body specs at T11)
- (e) live-API import detected by AST scan in CI test files (NFR-CG13 strict; live calls operator-gated only)
- (f) k_contract tripwire 4.8K exceeded — HALT, party-mode for scope reduction per E6
- (g) trial-2 cost-projection exceeds BS-3 ceiling at AC-H (operator-gated check) — HALT + four named remediation paths
- (h) 5-API smoke any API FAIL OR total spend >$6.00 (operator-gated check) — HALT + party-mode escalation
- (i) Class-A/B/C+/C/D1/D2 templates fail in validator post-aggregation
- (j) `silent_bypass_events != 0` in Trial-2 run_summary (carry-forward from 7a.8 AC-D verification)
- (k) MVP Exit Gate AC-O fails (Trial-2 doesn't reach G2 with real content from ≥9-of-11) — operator must run Trial-2 (or dry-run) to verify
- (l) Slab Close Gate AC-P fails (Trial-2 doesn't reach G3 with 11 cascade-reading) — operator must run Trial-2 to verify
- (m) Round-(f) Class-C two-SKILL.md convention not honored in sanctum-alignment matrix (AC-C; Gary/Kira/Enrique/Wanda must list both skill paths)
- (n) any of 5 CI workflows fail to land OR fail to bind as required check at PR merge

**Do NOT:**
- Touch substrate-frozen lines
- Modify specialist body files (read-only consumers; aggregating substrate built by 11 prior stories)
- Modify 7b.1-7b.11 substrate (parity base, chain base, validator A/B/C+/C/D1/D2 templates, body specs)
- Modify scaffold-v0.2-D2-pipeline templates (consume only)
- Run live API in CI (NFR-CG13 strict; AC-G + AC-H + AC-I are operator-gated only)
- Skip Gate-2 evidence ceremony at T12 (DUAL-GATE binding; cannot flip done without operator stdout in Completion Notes)
- Skip retrospective deferred-inventory consultation at T15 (CLAUDE.md §Deferred inventory governance binding consultation point)
- Skip Class-D2 Compositor branch in sanctum-alignment matrix (D20 EXEMPT must be explicitly recorded)
- Conflate AC-O (MVP Exit G2 + 9-of-11) and AC-P (Slab Close G3 + 11 cascade-reading) — different evidence requirements
- Author retrospective without consulting `deferred-inventory.md` per CLAUDE.md binding
- Force-add operator-gated evidence into Completion Notes (operator pastes verbatim; do NOT fabricate)
- Defer the 5 CI workflow landings to a follow-on (all 5 must land + be bound at 7b.12 close)
```
