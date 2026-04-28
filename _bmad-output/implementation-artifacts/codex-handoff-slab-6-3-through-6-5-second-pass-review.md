# Codex dispatch: Second-pass bmad-code-review on Slab 6 trial-experience bundle remediation (hybrid: full review on 6.4; verification-only re-trace on 6.3 + 6.5)

**Session:** 2026-04-28 (operator-authorized post-remediation)
**Branch:** `dev/langchain-langgraph-foundation`
**Predecessor state:**
- Bundle implementation `162d129` → bmad-code-review `6-3-6-4-6-5-code-review-2026-04-28.md` → operator-ratified 3 DN dispositions → remediation dispatch `codex-handoff-slab-6-3-through-6-5-remediation.md` → 3 per-story remediation commits
- Codex remediation commits: `61c21c4` (6.3 patches + DN-1/DN-2 wired); `c2df610` (6.4 patches + W-R1/W-R2/M-R3/P-R1 re-satisfaction); `77a86e0` (6.5 patches + DN-1 wired + AC-6.5-G fix)
- Codex-side verification: 137 passed + 1 skipped focused regression; ruff PASS; sandbox-AC PASS across 3 story files; 6.5 lockstep BOTH invocation forms PASS
- Codex rider trace claim: all 3 ratified DN dispositions wired; all 6.4 BINDING rider re-satisfactions complete; no new decision_needed surfaced; Mary harvest-gate A18 candidate left as candidate (no catalog modification — correct disposition)
- Story statuses: all three remain `review` (correctly held per remediation dispatch closeout instruction)

**Operator-ratified BINDING dispositions (carried forward; do NOT re-litigate):**
- 6.3-DN-1 → Option A (copy directive sections into new current-run artifact with current metadata)
- 6.3-DN-2 → Option A (halt-for-repair on invalid current-bundle directives)
- 6.5-DN-1 → Option A (auto-expand for current/warning/blocker overrides saved collapse)

**Mission:** second-pass bmad-code-review verifying remediation patches addressed correctly + BINDING rider re-satisfaction is structurally complete. **Hybrid shape:**
- **6.4 = FULL REVIEW** — three layers (Blind Hunter + Edge Case Hunter + Acceptance Auditor) on diff `c2df610`. Reason: first-pass surfaced structural BINDING failures (W-R1/W-R2/M-R3/P-R1); structural re-satisfaction deserves full re-pass to verify completeness, not just verification.
- **6.3 = VERIFICATION-ONLY RE-TRACE** — Acceptance Auditor only on diff `61c21c4`. Trace each first-pass finding against its addressing patch; verify ratified DN-1 + DN-2 dispositions wired correctly.
- **6.5 = VERIFICATION-ONLY RE-TRACE** — Acceptance Auditor only on diff `77a86e0`. Trace each first-pass finding against its addressing patch; verify ratified DN-1 disposition wired correctly; verify AC-6.5-G direct invocation works.

This shape saves ~2-3 hr Codex vs full second-pass while preserving structural review attention where it matters (6.4).

**Operator preference (binding):** "do it right, no band-aids, only rational trade-offs that get named in writing." Aggressive DISMISS rubric for cosmetic NITs per `docs/dev-guide/story-cycle-efficiency.md`.

## Disposition rules

Standard:
- **`patch` items (NEW findings):** addressed in commits before declaring done
- **`defer` items:** filed as deferred-inventory entries with explicit reactivation gates
- **`dismiss` items:** justified inline; aggressive DISMISS for cosmetic NITs
- **`decision_needed` items:** HALT and surface to operator
- **`re-trace PASS`:** first-pass finding addressed correctly by remediation patch
- **`re-trace FAIL`:** first-pass finding NOT addressed correctly; auto-promote to NEW patch

Operator-ratified BINDING riders + DN dispositions are BINDING; do NOT re-litigate. Verify implementation matches.

---

## Story 6.3 — VERIFICATION-ONLY RE-TRACE

**Diff input:** commit `61c21c4` (`fix(slab-6.3): remediate code-review patches + wire ratified DN-1 + DN-2 dispositions`)

**Acceptance Auditor scope:** verify each first-pass finding addressed correctly per remediation dispatch §"Story 6.3 remediation".

### Per-finding re-trace (PASS / FAIL)

| First-pass finding | Re-trace verification |
|---|---|
| **6.3-DN-1 (accept prior defaults)** | Verify `accept` path writes NEW current-run artifact with CURRENT `run_id` (not `RUN-PRIOR`) + `source_attribution.prior_run_id` + `source_attribution.prior_bundle_path` + `source_attribution.accepted_at` audit fields. Test `tests/integration/marcus/test_step_02a_prior_run_directives_as_defaults.py:137` should now assert current `run_id` in current artifact + audit trail in source_attribution. |
| **6.3-DN-2 (invalid current directives halt)** | Verify discovery path raises `InvalidCurrentBundleDirectivesError` with file path + validator failure reason; verify NO prior-bundle scan attempted. Test `test_invalid_current_directives_halts_for_repair` should exist. |
| **6.3-BH-2 (write-then-validate destruction)** | Verify `modify` and `replace` write to TEMP file first; validate; only on PASS atomically rename. On FAIL, existing valid artifact preserved + `InvalidNewDirectivesError` raised. Test `test_modify_failure_preserves_existing_valid_current_artifact` should exist. |
| **6.3-BH-4 (symlink boundary)** | Verify resolved candidates checked to remain under `bundle_root` (e.g., `Path.is_relative_to(bundle_root)`). Test `test_symlinked_candidate_outside_bundle_root_rejected` should exist. |
| **6.3-BH-5 (race conditions)** | Verify stat/read operations wrapped in try/except `(FileNotFoundError, PermissionError, OSError)`; treat IO failure as candidate-absent. Test `test_candidate_removed_mid_scan_does_not_crash` should exist. |
| **6.3-EH-1 (search_root scope)** | Verify `search_root` parameter REMOVED from `discover_step_02a_directives_default(...)`. Helper signature: `(bundle_root: Path, lesson_slug: str)` only. |
| **6.3-EH-2 (tracked/default bundle filter)** | Verify candidate acceptance filters to `execution_mode: "tracked"` (or equivalent); ad-hoc/scratch bundles not surfaced. Test `test_adhoc_bundle_not_surfaced_as_default` should exist. |

### 6.3 N-item re-trace

Verify N4 + N5 + N9 still PASS per first-pass; no regression introduced. (N1, N2, N3, N6, N7, N8, N10, N11, N12 remain N/A.)

### 6.3 Deliverable

Section in second-pass review record at `_bmad-output/implementation-artifacts/6-3-6-4-6-5-second-pass-review-2026-04-28.md` with:
- Per-finding re-trace verdict (PASS / FAIL)
- Any new findings classified per disposition rules
- N-item re-trace summary
- Final sentence: "Story 6.3: re-trace verifies all 5 patches + 2 DN dispositions addressed correctly; N-item trace clean. Story 6.3 ready for `review → done` flip pending operator confirmation."

---

## Story 6.4 — FULL REVIEW (PRIORITY FOCUS)

**Diff input:** commit `c2df610` (`fix(slab-6.4): remediate code-review patches + re-satisfy W-R1/W-R2/M-R3/P-R1 BINDING riders`)

**Three-layer review:** Blind Hunter + Edge Case Hunter + Acceptance Auditor. Full discovery + verification.

**Why full review:** first-pass surfaced 11 patches including multiple structural BINDING failures (W-R1, W-R2, M-R3, P-R1). Remediation re-satisfaction needs verification that:
- Markdown contradictions actually purged (not just claimed)
- Validator alignment test actually parametrized over EVERY rule (extracted from validator OR enumerated explicitly with cross-reference)
- B-Run §08 worked examples are actually from B-Run §08 (not synthetic OR re-labeled `20260419B`)
- Pydantic checklist gaps actually closed (strict=True; closed-enum 3-surface red-rejection; tz-aware UTC enforcement)

### Specific things to verify substantively (Acceptance Auditor focus + 3-layer)

1. **W-R1 + W-R2 re-satisfaction (Markdown purge + alignment test):**
   - Grep `skills/bmad-agent-content-creator/references/pass-2-authoring-template.md` for ALL legacy schema references (segment-manifest schema names; old envelope field names). Should be ZERO.
   - Verify `test_markdown_template_field_names_match_pydantic_model` scans ENTIRE template body (not just marker block); test should assert no field names appear that aren't in Pydantic model
   - Verify new `test_no_intake_orchestrator_leak_pass_2_template` (or equivalent) grep test exists + asserts old contract terms absent

2. **M-R3 re-satisfaction (validator oracle alignment full):**
   - Verify `tests/integration/specialists/irene/test_pass_2_template_validator_alignment.py` parametrizes over EVERY rule in `validate-irene-pass2-handoff.py`. How? Either: (a) test imports rule list from validator dynamically; OR (b) test enumerates rules explicitly with comment cross-reference per rule.
   - Verify schema-valid failing examples for bridge cadence + cluster-arc procedural rules — both test cases should exist + pass procedurally-valid+structurally-failing AND structurally-valid+procedurally-failing inputs
   - Count: extract rule count from `validate-irene-pass2-handoff.py`; verify alignment test parametrize count matches (or has explicit rationale for any skipped rule)

3. **P-R1 re-satisfaction (3 worked examples from B-Run §08):**
   - Verify Markdown contains 3 worked examples
   - Verify each example references actual B-Run §08 friction (operator session 2026-04-20). Indicators: example labels (e.g., "B-Run §08 #1", not "20260419B"); error descriptions match Pass 2 post-hoc repair instances from operator session
   - If examples are synthetic or relabeled from `20260419B`, that's a re-trace FAIL (P-R1 still not satisfied)
   - **Decision_needed if uncertain:** if B-Run §08 evidence accessibility is unclear, surface — operator may need to paste the friction examples directly

4. **6.4-BH-2 (`_StrictModel` strict=True):**
   - Verify `app/specialists/irene/authoring/pass_2_template.py:34` `ConfigDict(extra="forbid", validate_assignment=True, strict=True)`
   - Verify `test_strict_mode_rejects_implicit_coercion` exists + passes int-where-str-expected case

5. **6.4-BH-3 (`procedural_rules` partial):**
   - Verify field declaration requires complete population (min_length OR per-rule-required)
   - Verify `test_procedural_rules_partial_rejected` exists

6. **6.4-BH-4 (tz-aware non-UTC):**
   - Verify validator enforces `tzinfo == datetime.timezone.utc`; non-UTC aware datetimes reject
   - Verify `test_generated_at_utc_rejects_non_utc_aware` exists

7. **6.4-AA-1 (closed-enum 3-surface red-rejection):**
   - Audit ALL closed enums in `pass_2_template.py` (not just `visual_detail_load`); each should have: Pydantic Literal rejection + JSON Schema enum rejection + explicit shape-pin test
   - Per-enum audit table in re-trace

8. **6.4-EH-1 (segment binding to Gary slide output):**
   - Verify cross-artifact validation at `app/specialists/irene/authoring/pass_2_template.py:124-160` validates `visual_file` matches Gary slide output path AND `card_number` matches slide's card_number
   - Verify integration test exists exercising both happy path + mismatch case

9. **6.4-EH-2 (cluster-arc under-modeled):**
   - Verify `cluster_role` field added to segment model; required when `cluster_id` present; closed enum
   - Verify golden fixture `tests/fixtures/specialists/irene/pass_2_template_golden.json` includes `cluster_role`
   - Verify validator cluster-arc path now succeeds with role information from contract

10. **6.4-EH-4 (JSON Schema weaker than Pydantic):**
    - Verify explicit `Field(...)` constraints for stringly-typed fields (PNG path patterns; etc.)
    - Audit JSON Schema output for missing pattern/format constraints

11. **Mary harvest-gate A18 candidate evaluation:**
    - Codex's report: "A18 remains a candidate only; I did not modify the anti-pattern catalog." (Correct disposition — catalog modification is operator + Mary harvest-gate authority.)
    - Acceptance Auditor: enumerate which validator rules went schema vs procedural with rationale per rule (becomes A18 evaluation evidence base per MA-R2 NON-BLOCKING). Surface evidence for operator + Mary to evaluate at close.

12. **Composition smoke + N4 + N11 (QR-R1 + QR-R2 BINDING):**
    - Verify `tests/composition/test_irene_pass_2_template_composition_smoke.py` still PASSES; envelope contribution shape unchanged; Composition Smoke gate fires GREEN
    - Verify N4 (per-component isolation invariant preserved) + N11 (composition mode declared) both PASS at re-trace

### 6.4 N-item re-trace

Verify N4 + N5 + N7 + N9 + N11 verdicts updated based on re-trace evidence. N5 was FAIL at first pass (Pass 2 contract not lockstep due to Markdown contradictions); re-trace should now PASS if W-R1/W-R2 fully re-satisfied. N1/N2/N3/N6/N8/N10/N12 remain N/A.

### 6.4 Deliverable

Section in second-pass review record with:
- Per-layer findings (Blind Hunter / Edge Case Hunter / Acceptance Auditor) — full discovery
- Per-finding triage (patch / defer / dismiss / decision_needed)
- Per-first-pass-finding re-trace verdict (PASS / FAIL)
- N-item re-trace summary
- Mary harvest-gate evidence summary (which rules went schema vs procedural with rationale; A18 candidate evaluation)
- Final sentence: "Story 6.4: full review verifies all 11 patches + 4 BINDING rider re-satisfactions structurally complete; N-item trace shows N5 PASS (was FAIL); composition smoke GREEN; Mary harvest-gate evidence captured. Story 6.4 ready for Gate 5 operator-side dual-gate evidence ceremony, then `review → done` flip."

OR (if NEW patches surface): "Story 6.4: re-trace surfaced X new patch items; remediation cycle 2 needed before close."

---

## Story 6.5 — VERIFICATION-ONLY RE-TRACE

**Diff input:** commit `77a86e0` (`fix(slab-6.5): remediate code-review patches + wire ratified DN-1 disposition + restore AC-6.5-G direct invocation`)

**Acceptance Auditor scope:** verify each first-pass finding addressed correctly per remediation dispatch §"Story 6.5 remediation".

### Per-finding re-trace (PASS / FAIL)

| First-pass finding | Re-trace verification |
|---|---|
| **6.5-DN-1 (auto-expand override)** | Verify HUD JS at `scripts/utilities/run_hud.py:1265-1268`: current/warning/blocker steps render `<details open>` + JS prevents sessionStorage from collapsing them on render. Verify `docs/operator/hud-guide.md` documents the rule. |
| **6.5-BH-2 (pack-version mismatch reference)** | Verify comparison uses SELECTED bundle's locked pack version (not LIVE manifest). Test `test_pack_version_mismatch_compares_to_bundle_locked_not_live_manifest` should exist. |
| **6.5-BH-4 (hardcoded step map)** | Verify step IDs derived from `pipeline_manifest.hud_steps()` (not hardcoded `_STEP_ARTIFACT_PATTERNS` keys). Per-step artifact pattern can stay hardcoded but step ID list must come from manifest. |
| **6.5-BH-5 + 6.5-EH-1 + 6.5-EH-2 (W-R1 O(N) memoization)** | Verify single bundle scan per HUD render (not two; second `rglob("*")` removed); verify `Dict[step_id, Artifact]` lookup built once; verify per-step matching is O(1) lookup not loop. Test `test_derivation_o_n_complexity` should exist. |
| **6.5-BH-6 (Windows path-escaping false positive)** | Verify test at `tests/integration/hud/test_per_step_summary_rendering.py:70-74` writes path-like strings into actual artifact path/metadata fields, not markdown body. |
| **6.5-EH-3 (sessionStorage corruption)** | Verify `JSON.parse(sessionStorage.hud_details)` wrapped in try/catch; on parse failure, treat as empty + continue render. |
| **6.5-AA-2 (per-step derivation functions pinned individually)** | Verify `_STEP_ARTIFACT_PATTERNS` table REPLACED by per-step-id derivation functions; tests parametrize over each function explicitly. |
| **6.5-AA-3 (AC-6.5-G direct invocation FAILS)** | Verify direct `python scripts/utilities/check_pipeline_manifest_lockstep.py` exits 0. Test `test_check_pipeline_manifest_lockstep_runs_via_direct_invocation` should exist. |
| **6.5-AA-4 (P-R2 disable-auto-expand docs incomplete)** | Verify `docs/operator/hud-guide.md` documents "disable auto-expand" semantics: auto-expand for current/warning/blocker overrides saved collapse (per DN-1); operator can manually collapse after; clearing sessionStorage resets state. |

### 6.5 N-item re-trace

Verify N4 + N9 still PASS per first-pass; no regression introduced. (N1, N2, N3, N5, N6, N7, N8, N10, N11, N12 remain N/A.)

### 6.5 Deliverable

Section in second-pass review record with:
- Per-finding re-trace verdict (PASS / FAIL)
- Any new findings classified per disposition rules
- N-item re-trace summary
- Final sentence: "Story 6.5: re-trace verifies all 11 patches + 1 DN disposition addressed correctly; AC-6.5-G direct invocation works; N-item trace clean. Story 6.5 ready for `review → done` flip pending operator confirmation."

---

## Required deliverable section

Triaged second-pass review record at `_bmad-output/implementation-artifacts/6-3-6-4-6-5-second-pass-review-2026-04-28.md` with:

- **Per-story sections** (3 sections)
- **Per-story re-trace verdicts** per first-pass finding (PASS / FAIL)
- **6.4 full-review findings** per layer (Blind / Edge / Auditor) with disposition (patch / defer / dismiss / decision_needed)
- **Per-story N-item trace summary** (12-row table per story; concrete trace evidence per row)
- **Bundle-level summary table** (per-story patch / defer / dismiss / decision_needed counts; close posture per story)

## Closeout protocol per story (per discipline doc Gate 6)

When second-pass review verifies clean (zero new patch / decision_needed) per story:

**6.3 close (operator runs):**
1. Sprint-status flip `review → done` with summary annotation citing remediation commit + second-pass review record
2. NON-BLOCKING items per spec (M-R3 K-target preserved; P-R3 Marcus skill cross-link; A-R2 Phase 1 layout pre-flight evidence)
3. Composition Spec §10 Decision Log entry — N/A (no substrate change)
4. Deferred-inventory `Last refreshed:` line update

**6.4 close (operator runs; DUAL-GATE):**
1. Operator runs Gate 5 dual-gate live evidence ceremony per spec — pastes evidence into Dev Agent Record §"Operator dual-gate gate-2 evidence"
2. Sprint-status flip `review → done` with summary annotation citing remediation commit + second-pass review record + Gate 5 evidence
3. NON-BLOCKING items per spec (M-R4 K-target preserved; P-R3 docs/dev-guide companion; A-R3 effort-estimate phasing)
4. **Mary harvest-gate disposition (NON-BLOCKING per MA-R1):** if cluster-arc + cross-artifact work surfaced clean state-machine pattern, file as A18 candidate ("State-machine modeling rescues seemingly-procedural validation") in `docs/dev-guide/specialist-anti-patterns.md` Post-Cycle Harvest section. Operator + Mary review the second-pass evidence (per MA-R2) and decide.
5. Composition Spec §10 Decision Log entry — N/A (no substrate change; Irene `_act` body category unchanged per A-R1 BINDING)
6. Deferred-inventory `Last refreshed:` line update

**6.5 close (operator runs):**
1. Sprint-status flip `review → done` with summary annotation citing remediation commit + second-pass review record
2. NON-BLOCKING items per spec (M-R3 K-target preserved; P-R3 screenshots; A-R3 effort estimate)
3. Composition Spec §10 Decision Log entry — N/A (HUD-only; no substrate change)
4. Deferred-inventory `Last refreshed:` line update

**At ALL three closes:**
1. Update `_bmad-output/planning-artifacts/deferred-inventory.md` `Last refreshed:` per close
2. **UNBLOCK FIRST TRACKED TRIAL:** with all three closed, the substrate-polish tail of the migration is complete; operator queues first tracked trial run per Composition Spec §11 evidence-harvest discipline

## Halt-and-surface triggers (BINDING)

HALT if any of:
- Second-pass surfaces NEW patch item that wasn't in first-pass triage (means remediation introduced new defect)
- Re-trace FAIL on any first-pass finding (means remediation didn't address it correctly)
- Second-pass surfaces decision_needed beyond the 3 ratified above
- Composition Spec §11 migration trigger fires
- N-item FAIL during re-trace
- Cross-cutting impact beyond per-story IN-SCOPE list
- Substrate disagreement (out-of-scope file modified)

If HALT fires, surface to operator with concrete evidence + recommended path forward.

## What this dispatch does NOT do

- Does NOT touch any code (review-only; new patches if surfaced are separate commits per finding)
- Does NOT flip any story to done (operator runs Gate 6 close protocol after review verifies)
- Does NOT replace operator's Gate 5 dual-gate evidence for 6.4 (operator runs after second-pass clears)
- Does NOT modify anti-pattern catalog (Mary harvest-gate evaluates A18 candidate at 6.4 close; operator + Mary file)
- Does NOT re-litigate operator-ratified party-mode BINDING riders or the 3 ratified DN dispositions
- Does NOT trigger first tracked trial (post-bundle-close operator action)
