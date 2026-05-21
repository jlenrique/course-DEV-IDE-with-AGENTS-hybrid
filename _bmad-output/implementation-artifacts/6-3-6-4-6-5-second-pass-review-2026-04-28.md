# Slab 6 Trial Experience Bundle Second-Pass Code Review - 2026-04-28

Review target:
- Story 6.3 verification-only re-trace: commit `61c21c4`
- Story 6.4 full review: commit `c2df610`
- Story 6.5 verification-only re-trace: commit `77a86e0`

Method:
- 6.3: Acceptance Auditor re-trace only.
- 6.4: full Blind Hunter + Edge Case Hunter + Acceptance Auditor review, with first-pass finding re-trace.
- 6.5: Acceptance Auditor re-trace only.

Review posture:
- Operator-ratified DN dispositions were treated as binding and were not re-litigated.
- This review did not modify code or story status. The only file written by this pass is this review record.
- Focused verification run during this pass:
  - `.\.venv\Scripts\python.exe -m pytest tests/integration/marcus/test_step_02a_prior_run_directives_as_defaults.py -q --tb=short` -> `13 passed, 1 skipped`
  - `.\.venv\Scripts\python.exe -m pytest tests/unit/specialists/irene/test_pass_2_template_strict.py tests/integration/specialists/irene/test_pass_2_template_validator_alignment.py tests/composition/test_irene_pass_2_template_composition_smoke.py -q --tb=short` -> `30 passed`
  - `.\.venv\Scripts\python.exe -m pytest tests/unit/hud/test_per_step_summary_derivation.py tests/integration/hud/test_per_step_summary_rendering.py -q --tb=short` -> `19 passed`
  - `.\.venv\Scripts\python.exe scripts\utilities\check_pipeline_manifest_lockstep.py` -> PASS
  - `.\.venv\Scripts\python.exe -m scripts.utilities.check_pipeline_manifest_lockstep` -> PASS
  - `.\.venv\Scripts\python.exe -m scripts.utilities.validate_migration_story_sandbox_acs ...6-3... ...6-4... ...6-5...` -> PASS across 3 story files
  - `.\.venv\Scripts\python.exe -m ruff check ...focused touched files...` -> PASS

## Story 6.3 - Step 02A Prior-Run Directives As Defaults

Verdict: re-trace clean. No new patch, defer, dismiss, or decision_needed items surfaced.

### Per-Finding Re-Trace

| First-pass finding | Verdict | Evidence |
|---|---|---|
| 6.3-DN-1 - accept prior defaults | PASS | `write_operator_directives_from_choice(..., choice="accept")` now calls `_current_run_accept_content(...)` for prior defaults, writing current `run_id`, current UTC timestamps, and `source_attribution.prior_run_id`, `source_attribution.prior_bundle_path`, `source_attribution.accepted_at` (`scripts/utilities/operator_directives_defaults.py:178`, `:191`). Test assertions pin current-run metadata and prior attribution (`tests/integration/marcus/test_step_02a_prior_run_directives_as_defaults.py:119`, `:144`). |
| 6.3-DN-2 - invalid current directives halt | PASS | `discover_step_02a_directives_default(...)` validates current bundle first and raises `InvalidCurrentBundleDirectivesError` before sibling discovery (`scripts/utilities/operator_directives_defaults.py:231`, `:235`). Test exists at `tests/integration/marcus/test_step_02a_prior_run_directives_as_defaults.py:208`. |
| 6.3-BH-2 - write-then-validate destruction | PASS | `_write_validated(...)` writes to a temp file, validates the temp, then `os.replace(...)` atomically replaces target only after pass (`scripts/utilities/operator_directives_defaults.py:201`, `:206`, `:212`). Failure preservation test exists at `tests/integration/marcus/test_step_02a_prior_run_directives_as_defaults.py:226`. |
| 6.3-BH-4 - symlink boundary | PASS | Resolved candidate paths must remain relative to the resolved bundle parent before acceptance (`scripts/utilities/operator_directives_defaults.py:128`, `:259`). Test exists at `tests/integration/marcus/test_step_02a_prior_run_directives_as_defaults.py:251`. |
| 6.3-BH-5 - race conditions | PASS | Validation, constants load, candidate resolve/stat/read paths catch `FileNotFoundError`, `PermissionError`, and `OSError` and treat IO failure as absent (`scripts/utilities/operator_directives_defaults.py:71`, `:86`, `:107`, `:253`). Race test exists at `tests/integration/marcus/test_step_02a_prior_run_directives_as_defaults.py:268`. |
| 6.3-EH-1 - search_root scope | PASS | Helper signature is now only `(bundle_root: Path, lesson_slug: str)`; no `search_root` parameter remains (`scripts/utilities/operator_directives_defaults.py:219`). |
| 6.3-EH-2 - tracked/default bundle filter | PASS | Prior candidates pass `require_tracked=True` and `_default_from_bundle(...)` rejects non-`tracked/default` execution modes (`scripts/utilities/operator_directives_defaults.py:93`, `:103`, `:261`). Ad-hoc exclusion test exists at `tests/integration/marcus/test_step_02a_prior_run_directives_as_defaults.py:295`. |

### N-Item Re-Trace

| N-item | Verdict | Evidence |
|---|---|---|
| N1 | N/A | No provider IDs, models, endpoints, regions, auth, or provider catalogs changed. |
| N2 | N/A | No composition-shape substrate decision or vote introduced. |
| N3 | N/A | No live external API path introduced. |
| N4 | PASS | 6.3 remains isolated to Step 02A helper/docs/tests and generated pack projection; no `ProductionEnvelope`, runner, adapter, or manifest topology change. |
| N5 | PASS | Output remains the existing `operator-directives.md` contract and still validates through `validate_operator_directives(...)`. |
| N6 | N/A | No gate hierarchy or blocking semantics changed. |
| N7 | N/A | No replay-regression execution path changed. |
| N8 | N/A | No cost machinery or trace attribution changed. |
| N9 | PASS-PENDING-OPERATOR | Dev-side accept/modify/replace behavior is pinned by tests; operator readability evidence remains a Gate 6 close item. |
| N10 | N/A | Process evidence, not an implementation substrate item for this re-trace. |
| N11 | N/A | No composed/isolated execution mode contract introduced. |
| N12 | N/A | No external auth model or provider probe introduced. |

Story 6.3: re-trace verifies all 5 patches + 2 DN dispositions addressed correctly; N-item trace clean. Story 6.3 ready for `review → done` flip pending operator confirmation.

## Story 6.4 - Irene Pass 2 Authoring Template

Verdict: not clean. Full review found three patch items. Two are direct re-trace failures of first-pass structural findings; one is a remaining closed-enum audit gap. No defer or decision_needed item surfaced.

### Blind Hunter Findings

| ID | Disposition | Finding | Evidence |
|---|---|---|---|
| 6.4-SP2-BH-1 | patch | JSON Schema still accepts remote PNG URLs that Pydantic rejects, so schema consumers remain weaker than the Pydantic model for local PNG path shape. | `LOCAL_PNG_PATH_PATTERN = r"^.+[.][Pp][Nn][Gg]$"` permits `https://example.com/slide.png` (`app/specialists/irene/authoring/pass_2_template.py:10`). Pydantic field validators reject remote only at runtime (`:61`, `:67`), but generated JSON Schema contains only the suffix pattern. Local probe during review: `jsonschema.validate(...)` accepted remote `.png` values for `gary_slide_output.file_path`, `perception_artifacts.source_image_path`, and `segment_manifest.visual_file`. This is a re-trace FAIL for 6.4-EH-4. |

### Edge Case Hunter Findings

| ID | Disposition | Finding | Evidence |
|---|---|---|---|
| 6.4-SP2-EH-1 | patch | Validator-oracle alignment is still not full: the alignment test covers the six modeled `procedural_rules`, not every currently enforced validator rule, and it gives no explicit skip rationale for the remaining validator checks. | `validate-irene-pass2-handoff.py` contains 39 `errors.append(...)` enforcement points and 11 `warnings.append(...)` points; the alignment parametrization contains six `lambda path:` procedural cases (`tests/integration/specialists/irene/test_pass_2_template_validator_alignment.py:310`). The test neither imports an authoritative rule list from the validator nor enumerates validator rules with cross-reference comments. This is a re-trace FAIL for M-R3 / 6.4-AA-4. |

### Acceptance Auditor Findings

| ID | Disposition | Finding | Evidence |
|---|---|---|---|
| 6.4-SP2-AA-1 | patch | Closed-enum three-surface audit omits the `ProceduralRule` enum. | `ProceduralRule = Literal[...]` is a closed enum in `app/specialists/irene/authoring/pass_2_template.py:17`. The red-rejection parametrization covers `schema_version`, `composition_mode`, `visual_detail_load`, `content_density`, `bridge_type`, `cluster_role`, and `cluster_position`, but no `procedural_rules` unknown-value case (`tests/unit/specialists/irene/test_pass_2_template_strict.py:103`). The partial/order test at `:178` does not pin Pydantic Literal rejection + JSON Schema enum rejection + explicit shape-pin for an unknown procedural rule. This is a re-trace FAIL for the complete closed-enum audit portion of 6.4-AA-1. |

### Per-First-Pass-Finding Re-Trace

| First-pass finding | Verdict | Evidence |
|---|---|---|
| 6.4-BH-1 / 6.4-AA-2 - conflicting Markdown contracts | PASS | Prompt-facing template now points to `pass_2_template.py`, generated JSON Schema, and procedural validator; old `20260419B` examples and old envelope-field prose are gone (`skills/bmad-agent-content-creator/references/pass-2-authoring-template.md:1`). |
| 6.4-BH-2 - `_StrictModel` strict mode | PASS | `_StrictModel` uses `ConfigDict(extra="forbid", validate_assignment=True, strict=True)` (`app/specialists/irene/authoring/pass_2_template.py:47`). Coercion rejection test exists (`tests/unit/specialists/irene/test_pass_2_template_strict.py:57`). |
| 6.4-BH-3 - partial `procedural_rules` | PASS | `procedural_rules` has min/max length equal to `REQUIRED_PROCEDURAL_RULES` and validator requires exact ordered match (`app/specialists/irene/authoring/pass_2_template.py:128`, `:152`). Partial/order rejection test exists (`tests/unit/specialists/irene/test_pass_2_template_strict.py:178`). |
| 6.4-BH-4 - non-UTC aware datetime | PASS | `_ensure_utc_aware(...)` rejects non-UTC offsets (`app/specialists/irene/authoring/pass_2_template.py:35`). Test exists at `tests/unit/specialists/irene/test_pass_2_template_strict.py:65`. |
| 6.4-BH-5 / W-R2 - whole-template field-name lockstep | PASS | Test reads entire Markdown body and extracts backticked field names, then asserts subset of all Pydantic model fields (`tests/unit/specialists/irene/test_pass_2_template_strict.py:218`). |
| 6.4-EH-1 - segment binding to Gary output | PASS | Cross-artifact validator checks perception path, segment `visual_file`, and segment `card_number` against Gary slide output (`app/specialists/irene/authoring/pass_2_template.py:163`, `:181`, `:212`, `:223`). Tests exist at `tests/unit/specialists/irene/test_pass_2_template_strict.py:191`. |
| 6.4-EH-2 - cluster arc under-modeled | PASS | `cluster_role` is present, closed to `head`/`interstitial`, required when `cluster_id` is present, and present in golden fixture (`app/specialists/irene/authoring/pass_2_template.py:16`, `:104`, `:234`; `tests/fixtures/specialists/irene/pass_2_template_golden.json:48`). |
| 6.4-EH-3 - bridge cadence and cluster arc procedural examples | PASS | Schema-valid/procedural-failing bridge cadence and cluster-arc tests exist (`tests/integration/specialists/irene/test_pass_2_template_validator_alignment.py:372`, `:385`). |
| 6.4-EH-4 - JSON Schema weaker than Pydantic | FAIL | JSON Schema now has PNG suffix patterns, but still accepts remote `.png` URLs that Pydantic rejects; no JSON Schema red test covers this remote-path gap. Patch 6.4-SP2-BH-1 required. |
| 6.4-AA-1 - Pydantic checklist closed-enum surfaces | FAIL | Strict mode and UTC checks pass, and most enums are pinned, but `ProceduralRule` lacks the required three-surface unknown-value rejection test. Patch 6.4-SP2-AA-1 required. |
| 6.4-AA-3 / P-R1 - B-Run Section 08 worked examples | PASS | Markdown contains three worked examples (`skills/bmad-agent-content-creator/references/pass-2-authoring-template.md:114`) and each maps to actual B-Run Section 08 categories recorded in `_bmad-output/implementation-artifacts/trial-run-c1m1-tejal-20260419.md:246`: envelope empty/path drift (`:252`), invalid visual-detail values (`:254`), and cluster arc plus bridge cadence (`:255`, `:258`). |
| 6.4-AA-4 / M-R3 - validator oracle alignment full | FAIL | Parametrized test covers six procedural labels but not every validator-enforced rule or an explicit rule inventory with rationale. Patch 6.4-SP2-EH-1 required. |
| 6.4-AA-5 - no intake/orchestrator leak grep | PASS | `test_no_intake_orchestrator_leak_pass_2_template` asserts old contract/leak terms absent across the template (`tests/unit/specialists/irene/test_pass_2_template_strict.py:236`). |

### 6.4 BINDING Rider Re-Satisfaction

| Rider | Verdict | Evidence |
|---|---|---|
| W-R1 | FAIL | Pydantic is the named source of truth, but generated JSON Schema does not fully mirror Pydantic local-path semantics for remote `.png` rejection. |
| W-R2 | PASS | Whole-template Markdown field-name lockstep test scans the entire template. |
| M-R3 | FAIL | Validator-oracle alignment is not parametrized across every validator-enforced rule and lacks an explicit skip/rationale inventory. |
| P-R1 | PASS | Three B-Run Section 08 worked examples map to the run log categories cited above. |
| QR-R1 | PASS | Composition smoke through `ProductionDispatchAdapter` passes; contribution shape unchanged and interrupt present. |
| QR-R2 | PASS | N4 and N11 remain PASS. |

### Mary Harvest-Gate Evidence

| Rule group | Current placement | Rationale / evidence |
|---|---|---|
| Required authoring envelope shape, `schema_version`, `run_id`, `composition_mode`, generated UTC timestamp | Schema/Pydantic | Structurally expressible and pinned by `IrenePass2AuthoringEnvelope` fields. |
| Gary slide output identity: `slide_id`, contiguous card numbers, local PNG path, `source_ref` | Mixed | Pydantic covers non-empty fields, card number lower bound, PNG suffix, and source ref; the post-hoc validator still owns file existence and contiguous sequence. Schema/Pydantic local path is incomplete for remote URL exclusion until 6.4-SP2-BH-1 is patched. |
| Perception artifact presence and Gary path parity | Schema/Pydantic | `perception_artifacts` min length plus cross-artifact `source_image_path` equality are modeled. |
| Segment identity, narration marker membership, visual file/card parity | Schema/Pydantic | Cross-artifact validator binds segment IDs to markers and segment visual/card values to Gary output. |
| Closed values: visual detail, content density, bridge type, cluster role, cluster position, composition mode | Schema/Pydantic | Literal enums and JSON Schema enum/const surfaces exist; `procedural_rules` enum test gap remains. |
| Behavioral-intent parity | Procedural | Requires narration-script parsing and comparison with segment manifest prose. |
| Bridge cadence and spoken bridge cues | Procedural | Depends on sequence, runtime cadence configuration, and learner-facing narration text. |
| Cluster arc continuity and new-concept token containment | Procedural | Requires ordered cluster state and narration-token comparison; this is the A18 candidate evidence base. |
| Narration cue presence and traceable visual references | Procedural | Requires perception lineage and narration text matching. |
| Motion perception confirmation and approved motion asset binding | Procedural | Requires motion plan, motion assets, and motion perception artifacts. |
| Runtime policy strictness, word-range warnings, rationale strength | Procedural | Depends on narration parameters and can promote warnings to runtime policy violations. |

A18 candidate evaluation: the `cluster_role` + `cluster_position` model additions materially improve the cluster-arc validation surface, but the validator alignment gap means the evidence is not clean enough to file the anti-pattern catalog entry from this review. Keep "State-machine modeling rescues seemingly-procedural validation" as a Mary/operator harvest candidate only.

### N-Item Re-Trace

| N-item | Verdict | Evidence |
|---|---|---|
| N1 | N/A | No provider IDs, models, endpoints, regions, auth, or provider catalogs changed. |
| N2 | N/A | QR-R1 composition smoke is traced under story-specific riders, not a composition-shape vote. |
| N3 | N/A | No live API/provider integration introduced. |
| N4 | PASS | Irene isolated prompt/reference flow remains functional; no runner, adapter, or envelope schema change. |
| N5 | FAIL | Pass 2 contract is more explicit, but lockstep is not clean because JSON Schema remains weaker than Pydantic for remote PNG URLs and validator-oracle alignment is not full. |
| N6 | N/A | No gate hierarchy or gate precedence behavior changed. |
| N7 | PASS | Focused validator/template/composition suite passed: `30 passed`. Existing validator fixture suite was not rerun in this second-pass command set but was not modified by the remediation commit. |
| N8 | N/A | No cost or trace machinery touched. |
| N9 | PASS-PENDING-OPERATOR | Gate 5 operator-side dual-gate evidence still required before close. |
| N10 | N/A | Process evidence, not an implementation substrate item for this review artifact. |
| N11 | PASS | `composition_mode` remains declared; composition smoke exercises composed path through `ProductionDispatchAdapter`. |
| N12 | N/A | No external auth model or provider probe introduced. |

Story 6.4: re-trace surfaced 3 new patch items; remediation cycle 2 needed before close.

## Story 6.5 - HUD Per-Step Expandable Summaries

Verdict: re-trace clean. No new patch, defer, dismiss, or decision_needed items surfaced.

### Per-Finding Re-Trace

| First-pass finding | Verdict | Evidence |
|---|---|---|
| 6.5-DN-1 - auto-expand override | PASS | Urgent step summaries render `open` plus `data-auto-open="urgent"` (`scripts/utilities/run_hud.py:411`). JS forces urgent details open before applying saved collapse state (`scripts/utilities/run_hud.py:1292`). HUD guide documents override and manual-collapse semantics (`docs/operator/hud-guide.md:31`). |
| 6.5-BH-2 - pack-version mismatch reference | PASS | Locked pack version is read from selected bundle `pack-version.txt` or run constants metadata (`scripts/utilities/hud_per_step_summary.py:68`) and used as expected version (`:529`). Test exists at `tests/unit/hud/test_per_step_summary_derivation.py:98`. |
| 6.5-BH-4 - hardcoded step map | PASS | Step IDs derive from manifest `hud_steps(...)` (`scripts/utilities/hud_per_step_summary.py:51`); per-step derivation functions are individually pinned (`tests/unit/hud/test_per_step_summary_derivation.py:50`). |
| 6.5-BH-5 / EH-1 / EH-2 - O(N) memoization | PASS | HUD render scans once into `SummaryArtifactIndex` and reuses O(1) indexes (`scripts/utilities/run_hud.py:301`; `scripts/utilities/hud_per_step_summary.py:111`). Matching checks pattern tuples against dictionaries, not every artifact (`scripts/utilities/hud_per_step_summary.py:143`). Complexity test exists at `tests/unit/hud/test_per_step_summary_derivation.py:112`. |
| 6.5-BH-6 - Windows path escaping false positive | PASS | Rendering tests place path-like data in summary source/fields and assert escaping through actual HTML summary rendering (`tests/integration/hud/test_per_step_summary_rendering.py:70`). |
| 6.5-EH-3 - sessionStorage corruption | PASS | `JSON.parse(sessionStorage.getItem('hud_details') || '{}')` is wrapped in `try/catch`; corrupt state logs warning and continues (`scripts/utilities/run_hud.py:1285`). Test asserts the guard text exists (`tests/integration/hud/test_per_step_summary_rendering.py:67`). |
| 6.5-AA-2 - per-step derivation functions pinned | PASS | Derivation functions exist for all 33 manifest HUD steps and missing function auto-fails (`tests/unit/hud/test_per_step_summary_derivation.py:42`, `:50`). |
| 6.5-AA-3 - AC-6.5-G direct invocation | PASS | Direct script path now inserts project root into `sys.path` when `__package__` is empty (`scripts/utilities/check_pipeline_manifest_lockstep.py:14`). Direct and module invocation both exited 0 during this review. Test exists at `tests/unit/hud/test_per_step_summary_derivation.py:150`. |
| 6.5-AA-4 - disable-auto-expand docs | PASS | HUD guide documents that current/warning/blocker auto-expand overrides saved collapse, manual collapse can happen after seeing urgent state, and clearing sessionStorage resets non-urgent expansion state (`docs/operator/hud-guide.md:31`). |

### N-Item Re-Trace

| N-item | Verdict | Evidence |
|---|---|---|
| N1 | N/A | No provider IDs, models, endpoints, auth, or regions changed. |
| N2 | N/A | HUD-only change; no composition-shape vote or substrate introduced. |
| N3 | N/A | No live provider path introduced. |
| N4 | PASS | Touched surfaces remain HUD/doc/test/lockstep utility; no runtime execution, specialist isolation, envelope, adapter, or manifest topology change. |
| N5 | N/A | No envelope/state accumulator or dependency-map contract changed. |
| N6 | N/A | No gate hierarchy or production interrupt behavior changed. |
| N7 | N/A | No replay, envelope, output digest, or execution-path contract changed. |
| N8 | N/A | No cost rollup, pricing, LangSmith trace, or attribution changed. |
| N9 | PASS-PENDING-OPERATOR | Dev-side rendering and derivation tests pass; operator readability evidence remains a Gate 6 close item. |
| N10 | N/A | Process evidence, not an implementation substrate item for this review artifact. |
| N11 | N/A | No composed/isolated execution mode contract introduced. |
| N12 | N/A | No external auth integration introduced. |

Story 6.5: re-trace verifies all 11 patches + 1 DN disposition addressed correctly; AC-6.5-G direct invocation works; N-item trace clean. Story 6.5 ready for `review → done` flip pending operator confirmation.

## Bundle-Level Summary

| Story | Patch | Defer | Dismiss | Decision needed | Close posture |
|---|---:|---:|---:|---:|---|
| 6.3 | 0 | 0 | 0 | 0 | Clean re-trace; ready for operator confirmation and `review → done` flip. |
| 6.4 | 3 | 0 | 0 | 0 | HALT: remediation cycle 2 required before Gate 5 / close. |
| 6.5 | 0 | 0 | 0 | 0 | Clean re-trace; ready for operator confirmation and `review → done` flip. |

Halt-and-surface status:
- HALT fires for Story 6.4 because re-trace FAIL surfaced on first-pass findings 6.4-EH-4, 6.4-AA-1, and 6.4-AA-4/M-R3.
- No new decision_needed item surfaced.
- No Composition Spec Section 11 migration trigger was detected.
- No substrate disagreement beyond the 6.4 contract/test/schema patch items above was detected.
- Story statuses remain `review`; no close protocol steps were executed.
