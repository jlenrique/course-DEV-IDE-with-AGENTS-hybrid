# Codex dispatch: bmad-code-review on Slab 6 trial-experience bundle (6.3 + 6.4 + 6.5)

**Session:** 2026-04-28 (operator-authorized post-bundle-implementation)
**Branch:** `dev/langchain-langgraph-foundation`
**Predecessor state:**
- Bundle implementation landed in commit `162d129` ("Implement Slab 6 trial experience bundle")
- Codex-side verification: 168 focused-regression passed in 17.61s; sandbox-AC validator PASS across all 3 spec files; pipeline lockstep PASS; ruff PASS; `git diff --check` clean
- All three story specs flipped to `review` (not done)
- No decision_needed items surfaced; no halt-and-adapt cycles
- 6.4 Gate 5 operator-side dual-gate evidence pending (per spec; dual-gate story requires operator-witnessed acceptance)

**Operator dispositions (BINDING; informs Acceptance Auditor):**
- All 22 BINDING + 12 NON-BLOCKING party-mode riders ratified 2026-04-28 across the three stories per `0ba6bd7`. Acceptance Auditor traces correctness; does NOT re-litigate.
- Per-story rider counts: 6.3 = 6 BINDING + 3 NON-BLOCKING; 6.4 = 9 BINDING + 5 NON-BLOCKING (6-voice panel for dual-gate); 6.5 = 7 BINDING + 4 NON-BLOCKING.

**Mission:** independent multi-layer code review on the bundle diff per discipline doc Gate 3. Three layers per story (Blind Hunter + Edge Case Hunter + Acceptance Auditor) + per-story N-item trace deliverable section. Bundled review (one dispatch covering all three diffs) is operator-authorized for efficiency — but per-story triage sections required so each story closes independently.

## Why this dispatch exists

Slab 6 trial-experience bundle is the post-MIGRATION-SHIPPED substrate-polish work that prepares for first tracked trial. Three operator-flagged friction surfaces (B-Run §08 Irene Pass 2 friction → 6.4; Step 02A re-entry burden → 6.3; Step 03 HUD inspection workflow → 6.5). Implementation must clear bmad-code-review per CLAUDE.md §3 + discipline doc Gate 3 before formal close.

**Operator preference (binding):** "do it right, no band-aids, only rational trade-offs that get named in writing." Three-layer review with aggressive DISMISS rubric for cosmetic NITs per `docs/dev-guide/story-cycle-efficiency.md`.

## Scope

**Diff input:** Slab 6 trial-experience bundle implementation in commit `162d129`. Compute file list at run time via `git show 162d129 --stat`.

NOT in scope (treat any modification as substantive finding):
- `app/models/runtime/production_envelope.py` (Slab 6.0 substrate)
- `app/marcus/orchestrator/dispatch_adapter.py` (Slab 6.0 substrate)
- `app/marcus/orchestrator/production_runner.py` core invocation logic (Slab 6.1 close shape; only Slab-6.5 may touch HUD's read of `state/config/runs/<trial-id>/` artifacts but NOT the runner)
- `app/manifest/compiler.py` core compile logic (Slab 6.2 close shape; 6.5 may read the compiled manifest for hud_tracked traversal but not modify)
- 14 × `app/specialists/<name>/graph.py` — specialists unchanged (6.4 may extend Irene's `_act` ONLY for new template loading per A-R1 BINDING with halt-and-surface if act-body category shifts)
- `marcus/orchestrator/m3_trial.py` (deterministic harness preserved)
- Anti-pattern catalog (no new entries expected; A6/A8/A9/A11/A12/P3 + A18 candidate evaluated at Mary harvest-gate close)

**Spec inputs (Acceptance Auditor reads these):**
- `_bmad-output/implementation-artifacts/migration-6-3-step-02a-prior-run-directives-as-defaults.md` (BINDING riders in Party-mode green-light section)
- `_bmad-output/implementation-artifacts/migration-6-4-irene-pass-2-authoring-template.md` (9 BINDING; dual-gate)
- `_bmad-output/implementation-artifacts/migration-6-5-hud-per-step-expandable-summaries.md` (BINDING riders)
- `_bmad-output/implementation-artifacts/codex-handoff-slab-6-3-through-6-5-trial-experience-bundle.md` (parent dispatch)
- `_bmad-output/implementation-artifacts/slab-6-trial-experience-bundle-governance-discipline.md` (BINDING governance)
- `docs/dev-guide/composition-specification.md` (particularly §3 invariants + §11 trigger detection)
- `docs/dev-guide/substrate-inventory-checklist.md` (N1–N12)
- `docs/dev-guide/specialist-anti-patterns.md` (A1–A17 + P1–P3)
- `docs/dev-guide/pydantic-v2-schema-checklist.md` (for 6.4 four-file-lockstep)

**Mode:** `"full"` (Acceptance Auditor activates).

## Disposition rules

Standard:
- **`patch` items:** addressed in commits before declaring done
- **`defer` items:** filed as deferred-inventory entries with explicit reactivation gates
- **`dismiss` items:** justified inline (1-2 sentences); aggressive DISMISS for cosmetic NITs
- **`decision_needed` items:** HALT and surface to operator with each option's tradeoff

Important: party-mode-ratified BINDING riders are BINDING; do NOT re-litigate. Trace whether the diff CORRECTLY implements them (different from re-deciding).

---

## Per-story substantive review focus

### 6.3 Step 02A prior-run directives as defaults — substantive review focus

1. **Helper bounded scope (W-R1 BINDING)** — verify the helper does ONE thing: find latest valid `operator-directives.md` for same `lesson_slug`. Grep helper module for any scoring/ranking/multi-candidate logic; flag as substantive finding if found.
2. **Architectural invariant (W-R2 BINDING)** — verify spec language explicitly names "helper does NOT call into Marcus PR-* surface"; verify code does not import or invoke any Marcus PR-* module from the helper.
3. **Invalid-prior fallthrough test (M-R1 BINDING)** — verify `test_invalid_prior_directives_falls_through_to_no_prior_path` exists; assert behavior matches spec (validator-rejected file → NOT surfaced as default).
4. **Deterministic tiebreak test (M-R2 BINDING)** — verify `test_deterministic_tiebreak_on_identical_mtime` exists; tiebreak rule is deterministic (suggested: lexicographic `run_id` descending).
5. **Additive template change (P-R1 BINDING)** — verify Step 02A template change is ADDITIVE (new section block); NO modification to existing prose; in-flight bundles using older pack still parse.
6. **Operator-facing doc (P-R2 BINDING)** — verify `docs/operator/step-02a-prior-run-defaults.md` exists with the new behavior + manual-disable instructions.
7. **Helper signature (A-R1 BINDING)** — verify helper signature accepts `bundle_root: Path` parameter (testable in isolation; not hardcoded path).

### 6.4 Irene Pass 2 authoring template — substantive review focus (DUAL-GATE)

1. **Pydantic authoritative source-of-truth (W-R1 BINDING)** — verify Pydantic model is THE source; JSON Schema regenerated via `model_json_schema()` (NOT hand-authored); Markdown references field names from model. Grep for any JSON Schema lines that don't appear in Pydantic field definitions.
2. **Markdown-Pydantic alignment test (W-R2 BINDING)** — verify `test_markdown_template_field_names_match_pydantic_model` exists + parses Markdown + asserts subset of Pydantic fields.
3. **Unidirectional schema-first validation (W-R3 BINDING)** — verify code documents validation order as contractual; schema validation happens FIRST; procedural runs SECOND on schema-valid output. Grep for any reverse-order paths.
4. **Procedural-rules enumeration (M-R1 BINDING)** — verify spec explicitly enumerates procedural-only rules (cluster arc continuity; spoken bridge cadence; narration cue presence; etc.) + names equivalence test per rule.
5. **Schema-valid-procedural-reject test (M-R2 BINDING)** — verify `test_schema_valid_but_procedural_rejected_fails_loud` exists; proves layered validation order.
6. **Validator-oracle alignment full test (M-R3 BINDING)** — verify `test_validator_oracle_alignment_full` exists + parametrized across each currently-validator-enforced rule; pins schema OR procedural coverage per rule.
7. **Worked examples from B-Run §08 (P-R1 BINDING)** — verify Markdown contains 3 worked examples drawn from actual 2026-04-20 trial run B-Run §08 friction (the operator-flagged-HIGHEST-friction evidence). Examples must reference actual B-Run §08 errors, not synthetic.
8. **Bidirectional cross-link (P-R2 BINDING)** — verify template ↔ `validate-irene-pass2-handoff.py` cross-links in BOTH directions; both tested.
9. **Phase 1 act-body-category pre-flight (A-R1 BINDING)** — verify Codex performed pre-flight check that template loading pattern matches existing pure-LLM `_act` category. If shift was detected (act-body category change), Codex should have HALTED-and-surfaced per Composition Spec §11 trigger 5. No silent expansion.
10. **Composition smoke test (QR-R1 BINDING)** — verify `tests/composition/test_irene_pass_2_template_composition_smoke.py` exists + exercises template through `ProductionDispatchAdapter` + verifies envelope contribution shape unchanged + Composition Smoke gate fires GREEN.
11. **N4 + N11 PASS verification (QR-R2 BINDING)** — Substrate Inventory Checklist N4 (per-component isolation invariant preserved) AND N11 (composition mode declared alongside isolated mode) both PASS at trace; cite concrete evidence per N-item.
12. **Pydantic v2 strict per checklist** — `model_config = ConfigDict(extra="forbid", validate_assignment=True, strict=True)`; tz-aware datetimes; closed enums with 3 red-rejection surfaces; four-file-lockstep (model + JSON Schema + golden fixture + shape-pin tests).
13. **Cluster-arc continuity disposition** — per A-R2 BINDING, if state-machine modeling was needed, Codex should have surfaced as decision_needed at Phase 2. Verify either (a) cluster-arc covered by simple procedural check (no state machine needed), OR (b) decision_needed was raised. If state-machine landed without surfacing, that's a substantive finding.

### 6.5 HUD per-step expandable summaries — substantive review focus

1. **O(N) derivation memoization (W-R1 BINDING)** — verify per-step summary derivation is O(N); bundle artifact scan happens ONCE per HUD render (not per-step); artifact lookups memoized by step id within a single render pass. Grep for nested loops over steps that would suggest O(N²).
2. **Pack-version-mismatch test (M-R1 BINDING)** — verify `test_per_step_summary_handles_pack_version_mismatch` exists; artifact at older pack-version renders with explicit `[pack version mismatch]` annotation; does NOT crash.
3. **33-step parametrize coverage (M-R2 BINDING)** — verify AC-A test pin parametrizes across ALL 33 hud_tracked steps; per-step derivation function existence pinned individually; missing-derivation auto-FAIL.
4. **Summary style guide compliance (P-R1 BINDING)** — verify spec contains style guide (sentence length cap ~30 words; "locked" not "frozen"; "artifact" not "file"; "no locked artifact yet" verbatim per AC-B). Tests assert per-step summary compliance.
5. **hud-guide.md operator section (P-R2 BINDING)** — verify `docs/operator/hud-guide.md` updated with new section: expand/collapse semantics + sessionStorage behavior + warning/blocker auto-expand + manual-disable instructions.
6. **Pure-function discipline (A-R1 BINDING)** — verify per-step derivation functions are PURE: no side effects; no IO outside reading artifact bytes; no logging from derivation function. Side effects + IO live at calling layer. Grep derivation module for any `print`, `logging`, file-writes outside read.
7. **Phase 1 artifact-coverage pre-flight (A-R2 BINDING)** — verify Codex enumerated all 33 hud_tracked steps + identified which have known artifact-derivation source vs which fall to "no locked artifact yet" path. If >5 steps fell to no-artifact path, Codex should have surfaced as decision_needed (suggests scope deferral or new-emitter discussion). Verify either (a) ≤5 steps fell through OR (b) decision_needed was raised.

---

## Required deliverable section (BINDING per Slab 6.0 governance + discipline doc Gate 3)

Triaged punch list at `_bmad-output/implementation-artifacts/6-3-6-4-6-5-code-review-2026-04-28.md` with:

- **Per-story sections** (3 sections; one per story for independent close)
- **Per-layer findings within each story** (Blind Hunter / Edge Case Hunter / Acceptance Auditor)
- **Per-finding triage classification** (patch / defer / dismiss / decision_needed)
- For each `patch`: which commit addresses it
- For each `defer`: which deferred-inventory entry was filed
- For each `dismiss`: justification (1-2 sentences max)
- For each `decision_needed`: option list + tradeoffs surfaced to operator
- **Required §Substrate Inventory Checklist Trace section per story** (3 separate trace tables) — each story gets its own 12-row N-item table with verdict (PASS / FAIL / N/A / decision_needed) + concrete trace evidence per row.

Per-story N-item applicability pre-populated:

**6.3 N-item trace:** N4 + N5 + N9 applicable; N1, N2, N3, N6, N7, N8, N10, N11, N12 N/A with rationale.

**6.4 N-item trace:** N4 + N5 + N7 + N9 + N11 applicable per QR-R2 BINDING; N1, N2, N3, N6, N8, N10, N12 N/A with rationale.

**6.5 N-item trace:** N4 + N9 applicable; N1, N2, N3, N5, N6, N7, N8, N10, N11, N12 N/A with rationale.

- Final sentence per story: "Story 6.X: All `patch` items addressed; all `defer` items filed; all `dismiss` items justified; `decision_needed` items surfaced to operator (or zero); substrate inventory trace complete with N-items 1–12 verdicts recorded. Story 6.X ready for `review → done` flip pending [operator confirmation / operator-side dual-gate gate-2 for 6.4 only]."

## Things NOT to flag

- Pre-existing replay-regression pack-hash drift (`replay-regression-pack-hash-drift-pre-slab-6.1` already deferred)
- Slab 6.0 + 6.1 + 6.2 substrate (out of scope; flag only if accidentally modified)
- Anti-pattern catalog absence of new entries (Mary harvest-gate evaluates A18 candidate at 6.4 close; not at code review)
- Pre-existing dirty working-tree state (none currently)
- Cosmetic NITs that don't change behavior, schema, or contract — apply aggressive DISMISS per `docs/dev-guide/story-cycle-efficiency.md`
- The 22 operator-ratified BINDING riders themselves (Auditor traces correctness; does not re-decide)
- Single-gate vs dual-gate designation per story (already pinned in governance JSON)

## Sequencing

Same as prior reviews:
1. Three layers run in parallel per story (~9 layer-passes total across 3 stories)
2. Triage merges + classifies per story
3. Codex addresses `patch` items in commits
4. Codex files `defer` items in deferred-inventory
5. Codex documents `dismiss` justifications
6. Codex surfaces `decision_needed` items to operator (do NOT silently choose)

Stories close independently — operator can flip 6.3 to done while 6.4 still awaits Gate 5 dual-gate evidence.

## Closeout protocol per story

When triage clears for a given story (per discipline doc Gate 6):

**6.3 close:**
1. Codex flips `migration-6-3-step-02a-prior-run-directives-as-defaults: review → done` with summary annotation
2. P-R3 NON-BLOCKING: Marcus skill SKILL.md cross-link
3. M-R3 NON-BLOCKING: K-target/floor annotations preserved (already in spec)
4. A-R2 NON-BLOCKING: Phase 1 layout pre-flight evidence cited

**6.4 close (DUAL-GATE):**
1. Codex flips `migration-6-4-irene-pass-2-authoring-template: review → done` ONLY AFTER Gate 5 operator-side dual-gate evidence pasted into Dev Agent Record (operator runs the spec's dual-gate evidence command + pastes result)
2. M-R4 NON-BLOCKING: K-target/floor annotations preserved (already in spec)
3. P-R3 NON-BLOCKING: `docs/dev-guide/irene-pass-2-authoring.md` operator-facing companion
4. A-R3 NON-BLOCKING: effort-estimate phasing preserved
5. **MA-R1 NON-BLOCKING (Mary harvest-gate):** if cluster-arc continuity required state-machine modeling that worked cleanly, file as **A18 candidate** ("State-machine modeling rescues seemingly-procedural validation") in `docs/dev-guide/specialist-anti-patterns.md` Post-Cycle Harvest section
6. **MA-R2 NON-BLOCKING:** spec author enumerates which validator rules went schema vs procedural with rationale per rule (becomes A18 evaluation evidence base)

**6.5 close:**
1. Codex flips `migration-6-5-hud-per-step-expandable-summaries: review → done` with summary annotation
2. M-R3 NON-BLOCKING: K-target/floor annotations preserved (already in spec)
3. P-R3 NON-BLOCKING: screenshots or mock layouts in `docs/operator/hud-guide.md`
4. A-R3 NON-BLOCKING: effort estimate adjusted

**At ALL three closes:**
1. Update `_bmad-output/planning-artifacts/deferred-inventory.md` `Last refreshed:` line per close
2. **UNBLOCK FIRST TRACKED TRIAL:** with all three closed, the substrate-polish tail of the migration is complete; operator can queue first tracked trial run per Composition Spec §11 evidence-harvest discipline

## Substrate Inventory Checklist availability

Per Slab 6.0 governance + discipline doc, every Codex slab dispatch from this point forward must:
1. Read the checklist at T1
2. Identify which N-items apply
3. Have the Acceptance Auditor verify each applicable N-item is honored
4. File N13+ extensions if a NEW substrate concern surfaces

For this review: per-story applicability pre-populated above; Auditor verifies + updates verdicts independently.

## What this dispatch does NOT do

- Does NOT touch any code (review-only; patches happen as separate commits per finding)
- Does NOT modify Slab 6.0 + 6.1 + 6.2 substrate (out of scope; flag if accidentally modified)
- Does NOT modify anti-pattern catalog (Mary harvest-gate evaluates A18 candidate at 6.4 close, not at review)
- Does NOT trigger first tracked trial (post-bundle-close operator action)
- Does NOT re-litigate operator-ratified party-mode BINDING riders (Auditor traces correctness)
- Does NOT replace operator's Gate 5 dual-gate witness for 6.4 (operator runs live evidence; Codex cannot)
