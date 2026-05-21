# Codex T11 cross-agent bmad-code-review prompt — Story 7b.12 Integration + Parity-Suite + Closeout

**Cycle:** Claude **in-session-developed** T1-T12 → Claude G6 self-review → Claude in-session bmad-party-mode T13 (GO-WITH-CONCERN majority 3-of-4) → **YOU (Codex T11 cross-agent review NOW)** → operator-witnessed DUAL-GATE Gate-2 ceremony at next session → Claude T14 close + retrospective + atomic commit.

**Polarity context (POLARITY DEVIATION; one-time):** Slab 7b 7b.1-7b.11 closed via NEW CYCLE end-to-end (Claude spec → Codex T1-T11 dev+tests + G6 self-review → Claude T11 bmad-code-review + T12 close; 11× iterations). For 7b.12 ONLY, operator authorized Claude to run T1-T12 in-session because Codex's budget refresh was 30 min away and the operator did not want to wait. **YOUR T11 cross-agent review is the deferred NEW CYCLE polarity preservation.** Without your review, the integration close lacks the cross-agent independence that's bound 11× across this slab. The DUAL-GATE operator-witnessed Gate-2 ceremony binds the close, but your T11 is a structural prerequisite to the operator running that ceremony with confidence.

**Story:** `migration-7b-12-integration-parity-suite-closeout` — Wave-6 strict-last DUAL-GATE Slab 7b closer (mirrors Slab 7a 7a.8 precedent; k_contract tripwire 4.8K; 18 ACs A-R; FR88/FR101/FR102/FR103/FR104/FR105/FR106/FR107 aggregation + NFR-CG12-CG20 + NFR-I9-I13 + NFR-OD3-OD6 closeout blocks).

**STATUS:** Status flipped `review` 2026-04-30. Spec at `_bmad-output/implementation-artifacts/migration-7b-12-integration-parity-suite-closeout.md`. Claude G6 self-review at `_bmad-output/implementation-artifacts/7b-12-codex-self-review-2026-04-30.md` (file is named `codex-self-review-...` for filename-pattern consistency with 7b.1-7b.11; CONTENT is Claude's G6 layered review). Working tree carries the 22 files Claude developed in-session 2026-04-30 PLUS the cross-specialist retrofit from 7b.8-7b.11 closes (intermingled; close commit at retrospective lands everything atomically per `bmad-memory-gitignore-force-add-policy` retirement at 2026-04-30 `.gitignore` update).

---

```
Run bmad-code-review on Story 7b.12 (Slab 7b Wave-6 strict-last DUAL-GATE integration story; Claude in-session-developed 2026-04-30; YOU are the cross-agent T11 reviewer per NEW CYCLE polarity preservation).

## Required reading (read in order)

1. **Story spec:** `_bmad-output/implementation-artifacts/migration-7b-12-integration-parity-suite-closeout.md` (status: review; 18 ACs A-R; 15 task blocks T1-T15; Claude-authored 2026-04-29; in-session-developed 2026-04-30).
2. **Claude G6 self-review:** `_bmad-output/implementation-artifacts/7b-12-codex-self-review-2026-04-30.md` (filename-pattern consistency; CONTENT is Claude's G6 layered review; lists all 22 files in scope + verification matrix + residual risk + party-mode T13 verdict).
3. **In-session bmad-party-mode T13 verdict (recorded in Claude G6 review):** GO-WITH-CONCERN majority 3-of-4 (John GO-WITH-CONCERN, Mary GO-WITH-CONCERN, Amelia GO, Murat GO-WITH-CONCERN; no NO-GO). Remediations 1+2+3 applied; remediation #4 filed as deferred-inventory entry `slab-7b-spec-language-row-improvement-vs-party-mode-gating-clarification` for retrospective close.
4. **Round-(e) governance JSON** — `docs/dev-guide/migration-story-governance.json` §`stories.7b-12`:
   - `expected_gate_mode == "dual-gate"`
   - `k_contract.tripwire_threshold_kloc == 4.8`
   - **Verify with:** `.venv/Scripts/python.exe -c "import json; d = json.load(open('docs/dev-guide/migration-story-governance.json', encoding='utf-8')); entry = d['stories']['7b-12']; assert entry['expected_gate_mode'] == 'dual-gate'; assert entry['k_contract']['tripwire_threshold_kloc'] == 4.8; print('Round-(e) E6 verified PASS for 7b-12')"`
5. **Slab 7a 7a.8 precedent** — `_bmad-output/implementation-artifacts/migration-7a-8-integration-parity-test-suite-slab-7a-closeout.md` + `_bmad-output/implementation-artifacts/7a-8-code-review-2026-04-29.md`. **PRIMARY TEMPLATE.** 7b.12 mirrors 7a.8 patterns: parity-test final form + Composition Spec invariant suite + NFR-CG block aggregator + closeout deliverables + Gate-2 evidence script + retrospective draft.
6. **All 11 prior Slab 7b T11 reviews** for inheritance audit — `7b-1-code-review-2026-04-29.md` through `7b-11-code-review-2026-04-30.md` (11 review reports). Spot-check that 7b.12's aggregation honors what each prior close ratified.
7. **PRD §FR88 + §FR101-FR107 + §NFR-CG12-CG20 + §NFR-I9-I13 + §NFR-OD3-OD6 + §Success Criteria (BS-2/BS-3)** at `_bmad-output/planning-artifacts/prd-slab-7b-specialist-activation-eleven.md`.
8. **CLAUDE.md** §LangChain/LangGraph migration governance + §Deferred inventory governance binding consultation point + 2026-04-30 `.gitignore` update note retiring `bmad-memory-gitignore-force-add-policy`.
9. **Round-(f) Class-C two-SKILL.md ratification** — recorded in `sprint-status.yaml::tripwire_events::wave_3_first_port_tripwire::notes`. Sanctum-alignment matrix (AC-C) MUST list both skill paths for Class-C specialists (persona at `bmad-agent-{specialist}/SKILL.md` + API-mastery at `bmad-agent-{api-name}/SKILL.md`).
10. **bmad-code-review skill** at `.claude/skills/bmad-code-review/` (or canonical equivalent). Apply the standard layered review protocol; emit findings classified PATCH / OBSERVATION / NIT / DISMISS.

## Files in scope (22 files Claude developed in-session 2026-04-30)

**New tests (4 files):**
- `tests/parity/test_eleven_specialists_addressable.py` (T3; AC-B; SG-1 aggregator; 3 test methods — roster floor + count + class_template_id declaration)
- `tests/parity/test_mapping_checklist_status.py` (T7; AC-F; SG-2 row-status invariant; 4 test methods — file present + legend intact + deferred-rows preserved + count >= floor)
- `tests/parity/test_nfr_cg_slab7b_block_aggregated.py` (T11; AC-M; 9 parametrized cases CG12/CG13/CG14/CG14a/CG15/CG16/CG17/CG19/CG20)
- `tests/parity/test_rate_limit_budgets_declared.py` (T9; AC-K; 4 test methods — register present + 4 third-party providers + register row keys + 5-specialist budget keys)

**New CI workflows (5 files):**
- `.github/workflows/specialist-parity.yml` (T2; AC-A binding; FR101+FR102+NFR-I9; bound to SG-4 sanctum-alignment + class-conformance)
- `.github/workflows/activation-contract.yml` (T3; AC-B binding; FR105+NFR-I10; bound to SG-1 11-specialist roster + per-specialist contracts)
- `.github/workflows/mapping-checklist.yml` (T7; AC-F binding; NFR-I11)
- `.github/workflows/substrate-frozen-paths-check.yml` (T8; AC-J binding; FR113+NFR-I13; awk-based hunk-header parser detecting diffs in `dispatch_adapter.py:70-95`; requires `[substrate-ceremony]` commit token if frozen-range touched)
- `.github/workflows/codex-scope-audit.yml` (T10; AC-L binding; NFR-OD6; static check on `.github/workflows/*.yml` for unauthorized `codex` references; allowlists self-reference)

**New docs (13 files):**
- `docs/dev-guide/specialist-sanctum-alignment-matrix.md` (T4; AC-C dev-doc; 11 rows; Class-C two-SKILL.md per Round-(f); Class-D2 EXEMPT per D20)
- `docs/operator/specialists/sanctum-alignment-matrix.md` (T4; AC-C operator twin)
- `docs/operator/specialists/{texas,quinn-r,vera,irene,tracy,gary,kira,enrique,wanda,dan,compositor}.md` (T6; AC-E; 11 docs; OPERATOR/INPUTS/OUTPUTS/REFERENCE four-section per Slab 7a 7a.7 precedent)

**New artifacts (2 files):**
- `_bmad-output/implementation-artifacts/7b-12-gate2-evidence-commands.ps1` (T12; AC-N; PS script for next-session operator ceremony — focused + wider regression + 12-spec sandbox-AC + class-conformance + live-API + ruff + lint-imports + 4 operator-gated AC blocks: AC-G cache-hit + pipeline-determinism harnesses, AC-H trial-2 cost-projection, AC-I 5-API smoke, AC-O+P MVP Exit + Slab Close gates)
- `_bmad-output/implementation-artifacts/7b-12-codex-self-review-2026-04-30.md` (T12; Claude G6 layered review; filename-pattern consistency; content is Claude's, NOT Codex's)

**Modified (2 files):**
- `tests/parity/test_skill_md_sanctum_alignment.py` (T2; cleanup of silent-shadowing duplicate `TestTracySkillMdSanctumAlignment` class definition that was overwriting the canonical Class-C+ test at line 102 via pytest namespace race; canonical test count now 33)
- `docs/operator/legacy-vs-langgraph-control-parity.md` (T5; appended `## Slab 7b Body Activation Rows (FR104; +11 rows)` section with B1-B11 rows; SG-2 33-row floor PRESERVED — the +11 are a distinct supplement, NOT counted into the 33-row floor)

**Net stat:** 22 files added/modified; +~2200 LOC docs/tests/workflows; -~30 LOC duplicate cleanup.

## Areas of attention (party-mode T13 surfaced concerns YOU must adjudicate)

### CRITICAL — AC-G/H/I script skeleton authoring gap (Mary substantive concern)

**The 4 Python utilities named in `7b-12-gate2-evidence-commands.ps1` AC-G/H/I sections DO NOT EXIST ON DISK YET:**
- `scripts/utilities/run_cache_hit_harness.py` (AC-G; 10-LLM cache-hit-rate aggregation; threshold ≥85% post-warm-up)
- `scripts/utilities/run_pipeline_determinism_harness.py` (AC-G; H-Pipeline ≥99% rate; bytes-identical sync-visuals + field-masked-hash assembly-guide)
- `scripts/utilities/project_trial_2_cost.py` (AC-H; trial-2 cost-projection per Round-(a) John A1; SR-T6 mitigation)
- `scripts/utilities/run_5_api_smoke.py` (AC-I; ≤3 canaries/API × 5 APIs × ≤$0.40/canary; total spend ceiling $6.00)

**Operator running Gate-2 ceremony at next-session-start WILL HIT "no such file" errors on those AC blocks unless these scripts exist first.** Mary's concern at T13: "if operator's Gate-2 ceremony fails because scripts aren't authored, who carries the close-attempt cost?"

**Your T11 disposition options (pick one):**
- **(a; PREFERRED if budget allows)** Author skeleton scripts as part of cycle-1 remediation — each ~50-100 LOC; argparse + YAML/JSON evidence emission + structured stdout matching the spec's evidence-block format. Skeletons should run + emit minimum-viable evidence even on placeholder data; full implementations can land at retrospective close OR within next-session operator ceremony.
- **(b)** Specify the skeleton shape with sufficient precision (AC-G/H/I framing in the PS script + Claude G6 self-review residual-risk section is the starting point) so that Claude or operator can author them at next session before Gate-2 ceremony.
- **(c)** Flag as PATCH cycle-1; cycle-1 remediation belongs to whichever agent the operator dispatches at next session. NO-GO on close until skeletons land.

### NIT — `tests/parity/test_mapping_checklist_status.py` deferred-row regex precision (Murat NIT)

The regex `re.compile(rf"\b{re.escape(token)}\)?\s")` matches `05B` / `7.5` / `14.5` / `15` row-anchor tokens cleanly but **`§6.2` and `§6.3` are sub-rows in the prose preamble that the table-row-anchor pattern doesn't match.** Test passes vacuously for those 2 of 6 deferred-row tokens. False-positive risk: regression on §6.2 or §6.3 wouldn't be caught. NIT-grade because those rows are sub-rows unlikely to flip without explicit author attention. Already filed as `mapping-checklist-deferred-row-detection-strengthening` deferred-inventory entry. **Your call:** is the filing sufficient OR should this strengthen now?

### OBSERVATION — substrate-frozen-paths awk hunk-parser off-by-one risk (Amelia gimlet-eye request)

`.github/workflows/substrate-frozen-paths-check.yml` lines parsing the `@@ -<start>,<count> +<start>,<count> @@` hunk header use:
```awk
match($0, /\+([0-9]+),?([0-9]*)/, arr)
start = arr[1]
count = arr[2] == "" ? 1 : arr[2]
end = start + count - 1
if ((start <= 95 && end >= 70)) { print "TOUCHED"; exit }
```
Visual inspection: looks correct (single-line edit case `+72` becomes `start=72, count=1, end=72`; multi-line `+70,5` becomes `start=70, count=5, end=74`). **Amelia at T13 specifically asked for off-by-one gimlet-eye on single-line edits at the boundary** (e.g., `+70`, `+95`, `+69`, `+96`). Verify; flag PATCH if any boundary edge case fails.

### AC-F INTERPRETATION — mapping-checklist row improvements (John PRD-fidelity concern)

Spec AC-F asks for "asserts ~28 row improvements" — Claude resolved this as integrity-invariant test + party-mode-gated retrospective close commit (deferred-inventory `slab-7b-mapping-checklist-row-status-update` filed). The mapping-checklist file's own preamble forbids dev-agent row-status flips: "Adding or removing rows requires party-mode consensus, NOT dev-agent authority." John's verdict at T13: acceptable resolution because it surfaces a latent contradiction in spec language and routes through the party-mode-gated retrospective. **Your call:** confirm John's interpretation OR flag as cycle-1 PATCH (if you think the dev-agent CAN authoritatively flip rows under post-close evidence rules; this would re-open a scope question).

### POLARITY-DEVIATION — Claude in-session dev (operator authorization)

This is the FIRST 7b.x story Claude developed end-to-end (vs Codex). Operator authorized 2026-04-30. NEW CYCLE polarity is preserved at integration close because (a) party-mode T13 provided in-session cross-agent review (Solo mode roleplay); (b) YOUR T11 cross-agent review is the deferred independence gate; (c) operator-witnessed Gate-2 ceremony binds close. **Your T11 should evaluate whether the 22-file deliverable meets the same quality bar as Codex's 7b.1-7b.11 dev work.** If you find systematic differences in code quality / test patterns / docs structure / conventions, flag them — that's the cross-agent independence gate paying off.

## Verification battery (re-run independently to confirm Claude's results)

```bash
.venv/Scripts/python.exe -m pytest tests/parity/test_skill_md_sanctum_alignment.py tests/parity/test_eleven_specialists_addressable.py tests/parity/test_mapping_checklist_status.py tests/parity/test_nfr_cg_slab7b_block_aggregated.py tests/parity/test_rate_limit_budgets_declared.py tests/parity/test_pipeline_determinism_harness.py -q --tb=short
.venv/Scripts/python.exe -m pytest tests/parity/test_*_activation_contract.py -q --tb=short    # All 11 per-specialist contracts
.venv/Scripts/python.exe -m pytest tests/unit/manifest tests/integration/marcus tests/composition tests/parity tests/structural tests/unit/marcus tests/specialists tests/cli tests/unit/models -q --tb=line --ignore=tests/integration/marcus/test_directive_confirm_or_edit_prompt.py -p no:randomly
.venv/Scripts/python.exe scripts/utilities/check_pipeline_manifest_lockstep.py
.venv/Scripts/python.exe scripts/utilities/detect_live_api_in_tests.py
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7b-12-integration-parity-suite-closeout.md
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/    # MUST pass with 11 contracts (UNCHANGED from 7b.11; integration story does NOT introduce 12th)
.venv/Scripts/python.exe -m ruff check tests/parity/test_eleven_specialists_addressable.py tests/parity/test_mapping_checklist_status.py tests/parity/test_nfr_cg_slab7b_block_aggregated.py tests/parity/test_rate_limit_budgets_declared.py
.venv/Scripts/lint-imports.exe
```

**Claude's reported results:** 5 new parity tests = 33+3+4+9+4 = 53 PASS. 11 activation contracts conform (UNCHANGED from 7b.11). Sandbox-AC PASS. Lockstep PASS. Live-API detector PASS (81 files). Lint-imports 9/9 KEPT. `dispatch_adapter.py:70-95` empty diff. Wider regression: 1368 PASS / 21 skipped / 1 deselected (deterministic order) — same baseline as 7b.11 close (no new tests at body level; 7b.12 is aggregator).

## T11 deliverable

Author T11 review report at `_bmad-output/implementation-artifacts/7b-12-code-review-2026-04-XX.md` per `bmad-code-review` skill output format. Verdict one of: PASS / PASS-WITH-OBSERVATION / PASS-WITH-PATCH / NO-GO. Findings classified PATCH (must-fix; cycle-1 remediation; blocks close) / OBSERVATION (acknowledged limitation; non-blocking) / NIT (cosmetic; defer or DISMISS) / DISMISS (false positive or out-of-scope).

If PASS-WITH-PATCH: cycle-1 remediation may be authored by you OR specified for Claude to author at next session before operator Gate-2 ceremony. Either path preserves NEW CYCLE polarity at integration close. Most likely PATCH candidates per T13 surface:
- AC-G/H/I script skeletons (Mary substantive)
- substrate-frozen-paths awk parser off-by-one boundary cases (Amelia gimlet-eye)
- mapping-checklist deferred-row regex strengthening for §6.2/§6.3 (Murat NIT — likely DEFER not PATCH)

If PASS or PASS-WITH-OBSERVATION: 7b.12 is cleared for the 4 deferred next-session steps documented in `next-session-start-here.md`:
1. T12.5 pre-Gate-2 script-skeleton authoring (BLOCKING; if not handled in cycle-1 PATCH, claude or operator authors at next session)
2. operator-witnessed DUAL-GATE Gate-2 ceremony via `7b-12-gate2-evidence-commands.ps1`
3. MVP Exit Gate AC-O + Slab Close Gate AC-P verification (operator runs Trial-2 or dry-run)
4. Slab 7b retrospective (T15) per `bmad-retrospective` skill + atomic close commit (`feat(slab-7b): close Slab 7b — 11 body specialists + integration + parity-suite + closeout`)

## Boundary

**HALT-AND-SURFACE on:**
- (a) Round-(e) governance pin mismatch (E6 assertion FAIL)
- (b) ANY of 11 prior body stories not `done` in spec status + sprint-status.yaml — strict prereq violated
- (c) substrate-frozen-paths violation (any diff to `dispatch_adapter.py:70-95` absent ceremony commit)
- (d) sandbox-AC violation (re-run on this spec + all 11 prior body specs)
- (e) live-API import detected by AST scan in CI test files (NFR-CG13 strict)
- (f) k_contract tripwire 4.8K exceeded — HALT, party-mode for scope reduction per E6
- (g) Class-A/B/C+/C/D1/D2 templates fail in validator post-aggregation
- (h) Round-(f) Class-C two-SKILL.md convention not honored in sanctum-alignment matrix (AC-C; Gary/Kira/Enrique/Wanda must list both skill paths)
- (i) any of 5 CI workflows fail to land OR fail to bind correctly (path filters / timeouts / job structure)

**Do NOT:**
- Touch substrate-frozen lines (`dispatch_adapter.py:70-95`)
- Modify specialist body files (read-only consumers; aggregating substrate built by 11 prior stories)
- Modify 7b.1-7b.11 substrate (parity base, chain base, validator A/B/C+/C/D1/D2 templates, body specs)
- Modify scaffold-v0.2-D2-pipeline templates at `docs/dev-guide/scaffolds/scaffold-v0.2-D2-pipeline/` (consume only)
- Run live API in CI (NFR-CG13 strict; AC-G/H/I are operator-gated only; do NOT exercise live calls during T11)
- Author Trial-2 evidence (operator's job at Gate-2; AC-O+P)
- Skip Gate-2 evidence ceremony (DUAL-GATE binding; operator cannot flip done without verbatim stdout in Completion Notes — your T11 PASS verdict is a structural prereq to the operator running Gate-2)

**Operator visibility:** if your T11 verdict is PASS-WITH-PATCH and the patches require >30 min of remediation work, surface explicitly so operator decides whether to (a) authorize you to remediate now (if budget allows), (b) defer remediation to next session start (Claude T12.5 task), or (c) re-scope the integration close. Default: surface; let operator decide.
```
