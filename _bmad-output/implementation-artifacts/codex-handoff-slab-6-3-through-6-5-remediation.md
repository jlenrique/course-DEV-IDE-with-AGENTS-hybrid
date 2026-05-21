# Codex dispatch: Slab 6 trial-experience bundle remediation (per-story focused attention)

**Session:** 2026-04-28 (operator-authorized post-bmad-code-review triage)
**Branch:** `dev/langchain-langgraph-foundation`
**Predecessor state:**
- Bundle implementation landed in commit `162d129` (3 stories bundled)
- bmad-code-review completed at review artifact `_bmad-output/implementation-artifacts/6-3-6-4-6-5-code-review-2026-04-28.md`
- Triage outcome: NOT clean. 27 patch items (5/11/11) + 3 decision_needed across the bundle
- 6.4 specifically has multiple BINDING rider trace failures (W-R1, W-R2, M-R3, P-R1 all flagged)
- Operator ratified 3 decision_needed dispositions 2026-04-28 (named below)

**Operator-ratified BINDING dispositions (2026-04-28):**

1. **6.3-DN-1 → Option A.** "Accept prior defaults unchanged" means: copy ONLY the directive sections into a NEW current-run artifact with CURRENT metadata (`run_id`, timestamps, source-bundle reference). Do NOT byte-copy the prior artifact. Provenance integrity > literal "unchanged" interpretation. Current-bundle artifacts always reflect current run's identity.

2. **6.3-DN-2 → Option A.** Invalid current-bundle `operator-directives.md` MUST halt-and-surface for repair before considering older defaults. Fail-loud per Composition Spec §3.6 discipline. Silent fallthrough to prior would mask current-bundle corruption (same defect class as A15/A16/A17).

3. **6.5-DN-1 → Option A.** Auto-expand for current/warning/blocker steps ALWAYS overrides saved `sessionStorage` collapse state. Operator can manually re-collapse after seeing the urgent state; cannot see urgent states if stale collapse honored. Document the rule in `docs/operator/hud-guide.md`.

**Mission:** focused per-story remediation. **Per-story commits REQUIRED (not bundled).** Stories close independently. 6.4 receives priority attention because BINDING rider trace failures indicate the dual-gate / highest-friction story under-delivered against the party-mode-ratified contract.

**Operator preference (binding, unchanged):** "do it right, no band-aids, only rational trade-offs that get named in writing." Halt-and-surface if substrate disagrees with spec. Same pattern as 3.1 + 5a.3 + A15-A17 + Slab 6.0/6.1/6.2 instances.

## Sequencing rule (BINDING)

**Complete each story end-to-end before starting the next.** No bundled work this time. Order:

1. **6.3 first** — smallest scope; DN-1 + DN-2 dispositions to wire; 5 patches; ~3-4 hr
2. **6.4 SECOND (priority focus)** — 11 patches with multiple BINDING rider trace failures; deserves dedicated attention; ~6-9 hr
3. **6.5 LAST** — 11 patches; DN-1 disposition to wire; ~4-6 hr

For each story:
- All patches addressed before commit
- Themed commit per story (e.g., `fix(slab-6.3): remediate code-review patches + wire ratified DN dispositions`)
- Final report per story before starting next

Total estimated wall-clock: ~13-19 hr Codex; expect 1-2 halt-and-adapt cycles given 6.4's scope.

## Governance discipline (BINDING)

Read `_bmad-output/implementation-artifacts/slab-6-trial-experience-bundle-governance-discipline.md` at T1. Six-gate sequence applies — this dispatch operates at Gate 4 (triage + dispositions wired) → returning to Gate 3 review surface for second-pass verification, then formal close per Gate 6.

- **Composition Spec normative** — honor §3 invariants throughout remediation; §11 trigger detection active; HALT-and-surface if any fire
- **Substrate Inventory Checklist N-items** — re-trace per applicable N-item per story at second review pass
- **Anti-pattern catalog** read at T1 of each story; A8/A9/A11/A12/A6/P3 + Mary harvest-gate A18 candidate evaluation at 6.4 close
- **Halt-and-surface triggers** per discipline doc §6: substrate disagreement; §11 trigger fire; new decision_needed surfaces beyond the 3 ratified above; N-item FAIL exceeding story budget; new anti-pattern; cross-cutting impact beyond IN-SCOPE list

---

## Story 6.3 remediation — Step 02A prior-run directives as defaults

**Patch surface (5 items + 2 ratified DN dispositions wired):**

### 6.3 Required code changes

**6.3-DN-1 wiring (Option A):**
- Modify `accept` path in `scripts/utilities/operator_directives_defaults.py` (around line 178): instead of writing prior artifact byte-for-byte, extract the three directive sections from prior artifact + write them into a NEW current-run artifact with CURRENT `run_id`, current timestamps, current source-bundle reference. Add `source_attribution: prior_run_id`, `source_attribution: prior_bundle_path`, `source_attribution: accepted_at` metadata fields so the current artifact carries audit trail of where directives came from.
- Update test at `tests/integration/marcus/test_step_02a_prior_run_directives_as_defaults.py:137` — assert current-run `run_id` is in current artifact (NOT `RUN-PRIOR`); assert `source_attribution.prior_run_id == "RUN-PRIOR"` (audit trail preserved).

**6.3-DN-2 wiring (Option A):**
- Modify discovery path at `scripts/utilities/operator_directives_defaults.py:88-106`: when current bundle has `operator-directives.md` that exists but FAILS validator, raise `InvalidCurrentBundleDirectivesError` (new exception class) with explicit file path + validator failure reason. Do NOT proceed to prior-bundle discovery.
- Add test `test_invalid_current_directives_halts_for_repair` — current artifact malformed; expect `InvalidCurrentBundleDirectivesError`; verify message names file path + validator failure reason; verify NO prior-bundle scan attempted.

**6.3-BH-2 patch (write-then-validate-then-delete destroys valid artifact):**
- Refactor `modify` and `replace` write paths at `scripts/utilities/operator_directives_defaults.py:194-199`: write to TEMP file first; validate; only on validation PASS atomically rename to `operator-directives.md`. On validation FAIL, leave existing valid current-run artifact intact + raise `InvalidNewDirectivesError` with validator failure reason.
- Add test `test_modify_failure_preserves_existing_valid_current_artifact` — start with valid current artifact; submit invalid `modify`; expect existing artifact unchanged + exception raised.

**6.3-BH-4 patch (symlink boundary leak):**
- In sibling discovery at `scripts/utilities/operator_directives_defaults.py:112-124`: after `Path.resolve()`, verify resolved candidate path remains UNDER `bundle_root` (use `Path.is_relative_to(bundle_root)` Python 3.9+; OR string-prefix check). Reject candidates resolving outside.
- Add test `test_symlinked_candidate_outside_bundle_root_rejected` — create symlink in bundle_root pointing to outside-root directory containing `operator-directives.md`; expect helper does NOT surface that file.

**6.3-BH-5 patch (race conditions in stat/read):**
- Wrap stat + read operations at `scripts/utilities/operator_directives_defaults.py:66-82` and `:130` in try/except `(FileNotFoundError, PermissionError, OSError)`; treat any IO failure as candidate-absent (skip + continue scan, do not crash).
- Add test `test_candidate_removed_mid_scan_does_not_crash` — use mock that raises FileNotFoundError on stat; assert helper continues + returns next valid candidate or None.

**6.3-EH-1 patch (search_root scope too permissive):**
- Remove `search_root` parameter from `discover_step_02a_directives_default(...)` at line 86; the helper signature is `(bundle_root: Path, lesson_slug: str)` only per W-R1 BINDING bounded-scope rider. `search_root` allows callers to scan arbitrary paths, violating "scan sibling tracked source bundles" intent.
- Update tests + callers accordingly.

**6.3-EH-2 patch (no tracked/default bundle filter):**
- Add filter at candidate acceptance path (around `scripts/utilities/operator_directives_defaults.py:120-126`): require candidate bundle's `run-constants.yaml` to declare `execution_mode: "tracked"` (or equivalent). Reject ad-hoc / scratch bundles.
- Add test `test_adhoc_bundle_not_surfaced_as_default` — create same-lesson ad-hoc bundle; expect helper does NOT surface it; falls through to next valid tracked candidate or None.

### 6.3 Verification + close

- Re-run `pytest tests/integration/marcus/test_step_02a_prior_run_directives_as_defaults.py -q --tb=short`
- Verify K-floor: was 4 → 6 per M-R3 NON-BLOCKING + 4 new tests above = ~10 tests minimum
- Sandbox-AC validator PASS
- Ruff PASS on touched files
- Themed commit: `fix(slab-6.3): remediate code-review patches + wire ratified DN-1 + DN-2 dispositions`
- Sprint-status flip: keep `review` until second-pass review verifies (do NOT flip to done from this dispatch)

---

## Story 6.4 remediation — Irene Pass 2 authoring template (PRIORITY FOCUS)

**This is the priority remediation.** 11 patches with multiple BINDING rider trace failures. Implementation under-delivered against the 9 BINDING + 5 NON-BLOCKING party-mode-ratified contract. Each BINDING rider trace failure must be explicitly re-satisfied with concrete evidence.

**Patch surface (11 items; 0 DN — operator decisions don't apply to 6.4):**

### 6.4 BINDING rider re-satisfaction (most important section)

**W-R1 re-satisfy (Pydantic authoritative source-of-truth):**
- 6.4-AA-2: Markdown still names old segment-manifest schema + old envelope fields as authoritative. Strip ALL legacy schema references from `skills/bmad-agent-content-creator/references/pass-2-authoring-template.md`. Markdown must reference ONLY the new Pydantic model field names + descriptions.
- 6.4-BH-1: Two conflicting contracts in template (new Pydantic + old segment-manifest schema/prose) at `:7-15` and `:46-54`. Remove old contract; new Pydantic is THE contract.
- 6.4-AA-5: Add `test_no_intake_orchestrator_leak_pass_2_template` (or equivalent grep test) verifying old contract terms do NOT appear in template body.
- Verify: parse Markdown; extract all referenced field names; assert subset of Pydantic model fields (W-R2 test alignment).

**W-R2 re-satisfy (Markdown-Pydantic alignment test):**
- 6.4-BH-5: Current alignment test `tests/unit/specialists/irene/test_pass_2_template_strict.py:102-116` only scans the special marker block; misses stale legacy field references elsewhere in template body. Extend test to scan ENTIRE template body, not just marker block.

**M-R3 re-satisfy (validator oracle alignment full test):**
- 6.4-AA-4: Test at `tests/integration/specialists/irene/test_pass_2_template_validator_alignment.py:129, :162-166` is overclaimed — not parametrized across each currently-validator-enforced rule. Refactor to parametrize over EVERY rule in `validate-irene-pass2-handoff.py` (extract rule list from validator OR enumerate explicitly with cross-reference); per rule, assert new template enforces same behavior (schema OR procedural; whichever).
- 6.4-EH-3: Add schema-valid failing examples for bridge cadence + cluster-arc procedural rules (`test_schema_valid_but_procedural_rejected_*`). Currently the procedural rules are named but not exercised with failing examples.

**P-R1 re-satisfy (3 worked examples from B-Run §08):**
- 6.4-AA-3: Markdown lacks 3 worked examples drawn from actual 2026-04-20 trial run B-Run §08 friction. Existing 2 examples (`20260419B` static/motion) are from a DIFFERENT prior trial; do NOT count. Pull actual B-Run §08 errors from operator session evidence (the highest-friction post-hoc repair instances) + author 3 worked examples showing how the new schema/template prevents each. If B-Run §08 evidence not directly accessible, surface as decision_needed (operator can paste the friction examples).

### 6.4 Pydantic checklist hardening

**6.4-BH-2 (`_StrictModel` missing `strict=True`):**
- Update `app/specialists/irene/authoring/pass_2_template.py:34` `ConfigDict(extra="forbid", validate_assignment=True, strict=True)` per Pydantic v2 checklist + W-R1 BINDING.
- Add test `test_strict_mode_rejects_implicit_coercion` — pass int where str expected; assert validation error.

**6.4-BH-3 (`procedural_rules` accepts partial/empty):**
- Update field declaration at `app/specialists/irene/authoring/pass_2_template.py:110-117` to require complete population (e.g., `min_length=N` if known minimum count; OR each procedural rule field is REQUIRED in nested model).
- Add test `test_procedural_rules_partial_rejected`.

**6.4-BH-4 (`generated_at_utc` accepts non-UTC aware datetimes):**
- Add validator at `app/specialists/irene/authoring/pass_2_template.py:23-26, :119-122` enforcing `tzinfo == datetime.timezone.utc`. Non-UTC aware datetimes must reject.
- Add test `test_generated_at_utc_rejects_non_utc_aware`.

**6.4-AA-1 (closed-enum red-rejection surfaces incomplete):**
- For each closed enum (currently `visual_detail_load`; verify others), ensure THREE red-rejection surfaces per Pydantic checklist: (1) Pydantic `Literal` rejects unknown value; (2) JSON Schema `enum` rejects unknown value; (3) explicit shape-pin test asserts unknown value raises `ValidationError`.
- Audit all enums in pass_2_template.py for compliance.

### 6.4 Cross-artifact + schema constraint hardening

**6.4-EH-1 (segment `visual_file`/`card_number` not bound to Gary slide output):**
- Extend cross-artifact validation at `app/specialists/irene/authoring/pass_2_template.py:124-160` to validate `visual_file` matches a Gary slide output path AND `card_number` matches the slide's card_number. Add to procedural validator alignment per M-R1 BINDING enumeration.

**6.4-EH-2 (cluster-arc procedural under-modeled):**
- Add `cluster_role` field to segment model at `app/specialists/irene/authoring/pass_2_template.py:86`; required when `cluster_id` present; closed enum (e.g., `Literal["opener", "body", "closer", "transition"]` or whatever the validator's role taxonomy is).
- Update golden fixture `tests/fixtures/specialists/irene/pass_2_template_golden.json:47` to include `cluster_role`.
- Verify validator cluster-arc path can now succeed with role information from contract.

**6.4-EH-4 (Pydantic-generated JSON Schema weaker than model):**
- Add explicit `Field(...)` constraints for fields like local PNG path shape (e.g., `Field(..., pattern=r"^.*\.png$")` if PNG required). JSON Schema consumers should see the same constraints Pydantic enforces.
- Audit all stringly-typed fields for missing pattern/format constraints.

### 6.4 Verification + close

- Re-run `pytest tests/unit/specialists/irene/test_pass_2_template_strict.py tests/integration/specialists/irene/test_pass_2_template_validator_alignment.py tests/composition/test_irene_pass_2_template_composition_smoke.py -q --tb=short`
- Verify K-floor: was 12 → 14 per M-R4 NON-BLOCKING + new tests above
- Sandbox-AC validator PASS
- Ruff PASS on touched files
- Themed commit: `fix(slab-6.4): remediate code-review patches + re-satisfy W-R1/W-R2/M-R3/P-R1 BINDING riders`
- Sprint-status flip: keep `review` until second-pass review verifies + Gate 5 operator-side dual-gate evidence (separate; operator runs before formal close)
- **Mary harvest-gate (NON-BLOCKING):** at re-implementation, evaluate whether cluster-arc continuity + cross-artifact validation work surfaced an A18 candidate ("State-machine modeling rescues seemingly-procedural validation"). If yes, file under "Post-Cycle Harvest" section.

---

## Story 6.5 remediation — HUD per-step expandable summaries

**Patch surface (11 items + 1 ratified DN-1 disposition wired):**

### 6.5 Required code changes

**6.5-DN-1 wiring (Option A):**
- Modify HUD JS at `scripts/utilities/run_hud.py:1265-1268`: for steps with `current` OR `warning` OR `blocker` status, ALWAYS render with `<details open>` + JS code prevents `sessionStorage` from collapsing them on render. Manual operator collapse persists for that session UNTIL status changes back to non-urgent OR sessionStorage cleared.
- Update `docs/operator/hud-guide.md` per P-R2 BINDING + DN-1 documentation: explicitly document the rule "current/warning/blocker steps auto-expand; saved collapse state ignored for those steps; operator can manually collapse after seeing urgent state."

**6.5-BH-2 patch (pack-version mismatch compares to wrong reference):**
- Update `scripts/utilities/hud_per_step_summary.py:180`: instead of comparing artifact metadata to LIVE manifest pack version, compare to the SELECTED bundle's locked pack version (read from bundle's `pack-version.txt` or equivalent at scan time).
- Add test `test_pack_version_mismatch_compares_to_bundle_locked_not_live_manifest` — historical bundle with old pack version; live manifest has new version; bundle's artifacts at old version; mismatch annotation should NOT fire (artifacts match bundle's locked version).

**6.5-BH-4 patch (hardcoded step-to-artifact map):**
- AC-6.5-F forbids hand-maintained parallel step names. Refactor `_STEP_ARTIFACT_PATTERNS` at `scripts/utilities/hud_per_step_summary.py:37-72` to derive step IDs from `pipeline_manifest.hud_steps()` directly. Per-step artifact pattern can stay hardcoded BUT step ID list must come from manifest.
- Update test at `tests/unit/hud/test_per_step_summary_derivation.py:36-41` accordingly.

**6.5-BH-5 + 6.5-EH-1 + 6.5-EH-2 patch (W-R1 O(N) memoization not satisfied):**
- This is the core W-R1 BINDING re-satisfaction. Refactor scan + match logic at `scripts/utilities/hud_per_step_summary.py:91-103, :112-130, :181-187`:
  - Single bundle scan per HUD render (not two; remove the second `rglob("*")`)
  - Build `Dict[step_id, Artifact]` lookup once
  - Per-step matching is O(1) lookup, not loop over `artifacts.items()` per step
  - Total derivation O(N) over manifest steps + O(M) over artifacts; memoized per render
- Add test `test_derivation_o_n_complexity` — measure lookup count per render; assert no nested loops; assert single scan per render.
- Add bound on scan depth + race-resilience (BH-5): wrap scan in try/except for FileNotFoundError; bound recursive scan to `bundle_root` direct children only (avoid traversing checkout/symlink trees).

**6.5-BH-6 patch (Windows path-escaping test false positive):**
- Update `tests/integration/hud/test_per_step_summary_rendering.py:70-74`: write path-like strings into actual artifact path/metadata fields, not into markdown body content. Test should exercise the rendering path that summary derivation actually uses.

**6.5-EH-3 patch (corrupt sessionStorage breaks HUD JS):**
- Wrap `JSON.parse(sessionStorage.hud_details)` at `scripts/utilities/run_hud.py:1265` in try/catch; on parse failure, treat sessionStorage as empty + continue render. Log to console for debug.
- Add JS test (or static analysis check) verifying try/catch wrapping.

**6.5-AA-2 patch (M-R2 weaker than rider — per-step derivation functions not pinned individually):**
- Refactor `_STEP_ARTIFACT_PATTERNS` table to be REPLACED by per-step-id derivation FUNCTIONS (`derive_step_01_summary(...)`, `derive_step_02_summary(...)`, etc.). Each function pure (per A-R1 BINDING).
- Update `tests/unit/hud/test_per_step_summary_derivation.py` to parametrize over each derivation function explicitly + assert each function exists + missing-function auto-FAIL.

**6.5-AA-3 patch (AC-6.5-G direct script invocation FAILS):**
- Fix `scripts/utilities/check_pipeline_manifest_lockstep.py` to support BOTH `python -m scripts.utilities.check_pipeline_manifest_lockstep` AND direct `python scripts/utilities/check_pipeline_manifest_lockstep.py` invocation forms. Likely needs `sys.path` adjustment at script entry point OR conditional import path resolution.
- Add test `test_check_pipeline_manifest_lockstep_runs_via_direct_invocation` — invoke via subprocess with direct script path; assert exit 0.

**6.5-AA-4 patch (P-R2 disable-auto-expand trace incomplete in docs):**
- Update `docs/operator/hud-guide.md:27` with explicit "disable auto-expand" semantics: explain that auto-expand for current/warning/blocker overrides saved collapse (per DN-1); operator can manually collapse after; clearing sessionStorage resets all expand/collapse state to defaults.

### 6.5 Verification + close

- Re-run `pytest tests/unit/hud/ tests/integration/hud/ -q --tb=short`
- Verify K-floor: was 13 → 15 per M-R3 NON-BLOCKING + new tests above
- Pipeline lockstep PASS via BOTH `python -m` AND direct script forms (AC-6.5-G)
- Sandbox-AC validator PASS
- Ruff PASS on touched files
- Themed commit: `fix(slab-6.5): remediate code-review patches + wire ratified DN-1 disposition + restore AC-6.5-G direct invocation`
- Sprint-status flip: keep `review` until second-pass review verifies

---

## Cross-story closeout requirements

**After all 3 per-story commits land:**
1. Final report covering: per-story tests passing; per-story files changed; per-story BINDING rider re-trace evidence (especially 6.4 W-R1/W-R2/M-R3/P-R1); ratified DN dispositions wired correctly; any new decision_needed items surfaced (should be zero given the 3 ratified above); Mary harvest-gate disposition for 6.4 A18 candidate
2. Working tree clean
3. **Stop. Do NOT flip any story to done.** Operator authors second-pass bmad-code-review dispatch verifying patches + BINDING rider re-trace; once that clears, formal closes proceed per discipline doc Gate 6 (with Gate 5 operator-side dual-gate evidence required for 6.4 only).

## Halt-and-surface triggers (BINDING per discipline doc §6)

HALT if any of:
- Substrate disagreement — patch requires substrate change beyond IN-SCOPE
- Composition Spec §11 migration trigger fires
- New `decision_needed` item surfaces beyond the 3 ratified above
- 6.4 BINDING rider re-satisfaction is structurally infeasible (e.g., B-Run §08 evidence not accessible for P-R1 worked examples)
- N-item FAIL during remediation auto-promotes to in-story patch; if budget exceeded, surface
- Cross-cutting impact beyond per-story IN-SCOPE list

## What this dispatch does NOT do

- Does NOT touch Slab 6.0/6.1/6.2 substrate (out of scope)
- Does NOT skip sequencing rule (per-story commits required; no bundling)
- Does NOT flip any story to done (second-pass review fires before close)
- Does NOT replace operator's Gate 5 dual-gate evidence for 6.4 (operator runs after second-pass review)
- Does NOT re-litigate operator-ratified party-mode BINDING riders or the 3 ratified DN dispositions (apply correctness; do not re-decide)
- Does NOT modify anti-pattern catalog (Mary harvest-gate evaluates A18 at 6.4 close)
