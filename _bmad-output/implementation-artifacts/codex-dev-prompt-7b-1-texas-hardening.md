# Codex dev-story prompt — Story 7b.1 Texas Hardening (Slab 7b Wave-1 SLAB-OPENER)

**Cycle:** Claude spec → Codex dev+tests → Claude bmad-code-review + commit + flip done.
**Wave:** 1 slot 1 — SLAB-OPENER (Class-A hardening; first body-activation in Slab 7b).
**Gate:** **SINGLE-GATE** (per `docs/dev-guide/migration-story-governance.json::stories.7b-1`; rationale: null; rubric-semantics work, not schema-shape, not lane-boundary).
**Round-(e) E5 binding:** **T2 atomic-commit is the Wave-1 substrate gate** — 7b.2 (Quinn-R) + 7b.3 (Vera) carry `prerequisite_stories: ["7b-1"]` with `binding=hard`. Sprint runner MUST NOT open them until your T2 lands all 4 atomic CREATE-tasks.

**Strict prereq:** Round-(e) governance JSON freeze RATIFIED 2026-04-29 (verified — see T1 below). Wave 0 foundational artifacts LANDED commit `9ed6fcb`. Slab 7a Epic CLOSED done with all 8 stories at `done` (substrate complete; Texas's upstream — directive-composer at `app/marcus/orchestrator/directive_composer.py` — is production-ready per 7a.1).

---

```
Run bmad-dev-story on Story 7b.1 (Slab 7b Wave-1 SLAB-OPENER; Class-A hardening; single-gate; Texas live retrieval against real directive composer + 4 atomic Wave-1 substrate CREATE-tasks + SG-4 first-enforcement + AC-B 150-LOC ceiling discipline).

## Required reading (read in order)

1. **Story spec:** `_bmad-output/implementation-artifacts/migration-7b-1-texas-hardening.md` (status: ready-for-dev; 14 ACs A-N; 12 tasks T1-T12; you own T1-T10 + T12 closeout draft; Claude owns T11 final code-review + remediation + commit + status flip)
2. **Round-(e) governance JSON freeze RATIFIED 2026-04-29:** `docs/dev-guide/migration-story-governance.json` story `7b-1` (single-gate; expected_pts=3; expected_k_target=1.3; no `_staged_pending_party_mode_ratification`). Top-level `tripwire_escalation_record_path` field present. Stories `7b-2` + `7b-3` carry `prerequisite_stories: ["7b-1"]` with `binding=hard`.
3. **Slab 7b PRD §FR89:** `_bmad-output/planning-artifacts/prd-slab-7b-specialist-activation-eleven.md` line 789. Six-canonical-artifacts contract. Errata addendum 1-4 (especially Errata 3 SanctumParityTestBase mandate + Errata 4 subdir-vs-flat decision deferred to this story T1).
4. **Slab 7b epics-and-stories §Story 7b.1:** `_bmad-output/planning-artifacts/epics-slab-7b-specialist-activation-eleven.md` lines 427-483 (R(a)-R(d) ratified scope; 8 amendments folded inline; Murat A4 amendment is the operative T1 CREATE-task source).
5. **Slab 2a.2 precedent (Class-A nearest analog):** `_bmad-output/implementation-artifacts/migration-2a-2-irene-pass-2-scaffold-migration.md` (9-node scaffold + AC-B 150-LOC ceiling discipline + sanctum cold-read pattern + cache-hit-rate harness pattern). Note: AC-B 150-LOC ceiling is the binding scope-discipline rule for Texas `_act` body; if exceeds, HALT + raise re-scope decision.
6. **Slab 7a 7a.1 NEW CYCLE precedent + Texas upstream substrate:** `_bmad-output/implementation-artifacts/migration-7a-1-directive-composer.md` + the dispatch_retrieval invocation surface verified at `app/specialists/texas/retrieval_dispatch.py:23` (slab-2a.4 era; `dispatch_retrieval(*, directive_path, bundle_dir)` keyword-only signature is stable substrate).
7. **BMB sanctum alignment checklist (FR108; canonical FR101 authority):** `docs/dev-guide/bmb-sanctum-alignment-checklist.md`.
8. **Sanctum exception categories (FR109 closed allowlist):** `docs/dev-guide/sanctum-exception-categories.json`.
9. **Specialist anti-patterns + migration template:** `docs/dev-guide/specialist-anti-patterns.md` (A1-A17 + P1-P3) + `docs/dev-guide/specialist-migration-template.md` (R1-R14).
10. **Sandbox-AC inventory:** `docs/dev-guide/migration-ac-sandbox-inventory.json` (FR107; LANDED Wave 0; +5 entries gamma/kling/elevenlabs/wondercraft/dan-api-tbd-pending; Texas does NOT need new entry — retrieval-orchestration not third-party-API).
11. **CLAUDE.md** — §LangChain/LangGraph migration governance + §BMAD sprint governance + §Pipeline lockstep regime + §Deferred-inventory governance.

## T1 hard checkpoints (HALT-AND-SURFACE if violated)

- **Round-(e) governance verified:** run `.venv/Scripts/python.exe -c "import json; d=json.load(open('docs/dev-guide/migration-story-governance.json',encoding='utf-8')); assert d['version']=='2026-04-29-slab7b-twelve-stories'; assert '_staged_pending_party_mode_ratification' not in d['stories']['7b-1']; assert d['stories']['7b-2']['prerequisite_stories']==['7b-1']; assert 'tripwire_escalation_record_path' in d; print('Round-(e) PASS')"` — exit 0 expected.
- **Wave 0 artifacts present:** `ls docs/dev-guide/bmb-sanctum-alignment-checklist.md docs/dev-guide/sanctum-exception-categories.json docs/dev-guide/operator-control-parity-template.md docs/dev-guide/migration-ac-sandbox-inventory.json skills/bmad-agent-cora/SKILL.md docs/dev-guide/scaffolds/scaffold-v0.2-D2-pipeline/` — all paths exist.
- **Slab 7a Epic CLOSED done:** `migration-epic-slab-7a-inter-gate-orchestration: done` in sprint-status.yaml + all 8 stories `done`.
- **Texas baseline at slab-2a.4 era:** `app/specialists/texas/{graph.py,state.py,model_config.yaml,retrieval_dispatch.py,expertise/}` exist; `_bmad/memory/bmad-agent-texas/` has 6-file BMB pattern (`INDEX.md`, `PERSONA.md`, `CREED.md`, `BOND.md`, `MEMORY.md`, `CAPABILITIES.md`); `skills/bmad-agent-texas/SKILL.md` exists.
- **dispatch_retrieval signature stable:** `.venv/Scripts/python.exe -c "from app.specialists.texas.retrieval_dispatch import dispatch_retrieval; import inspect; sig=inspect.signature(dispatch_retrieval); assert 'directive_path' in sig.parameters and 'bundle_dir' in sig.parameters; print('FR89 signature OK')"` — exit 0 expected.
- **`tests/parity/` flat layout confirmed:** no `tests/parity/per_specialist/` subdir present (verified flat at codebase head — Errata 4 verdict-flat aligns with reality).
- **Sandbox-AC validator pre-flight:** `.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7b-1-texas-hardening.md` — PASS expected.

## T2 atomic-commit gate (Wave-1 SUBSTRATE — Round-(e) E5 binding)

**T2 is the Wave-1 substrate gate.** All 4 CREATE-tasks below land in a SINGLE atomic commit. After this commit, 7b.2 + 7b.3 unblock per Round-(e) E5 `prerequisite_stories: ["7b-1"]` binding-hard contract.

### CREATE-task #1 (AC-7b.1-A): Errata 4 ratification — `tests/parity/README.md`

Author or augment `tests/parity/README.md` with §"FR105 + Errata 4 layout decision":
- VERDICT: **flat** (`test_<specialist_name>_activation_contract.py` at `tests/parity/` top-level)
- Rationale: "embrace boring technology" (Winston) + matches existing flat convention + reduces import-graph complexity
- Ratified-at: Story 7b.1 T1 (commit `<this-commit-sha>`)
- Inventory follow-on: `fr105-tests-parity-per-specialist-subdir-decision` → CLOSED at this story T1; update `_bmad-output/planning-artifacts/deferred-inventory.md` §Named-But-Not-Filed Follow-Ons in same commit.

### CREATE-task #2 (AC-7b.1-B): `tests/parity/_sanctum_parity_base.py`

Author class `SanctumParityTestBase` providing reusable assertion harness for sanctum-vs-shipped-paths invariants:
- Class attributes: `specialist_name: str` + `class_template_id: str` (`"A"` / `"B"` / `"C"` / `"C+"` / `"D1"` / `"D2"`); subclasses override.
- Method `assert_skill_md_minimal_frontmatter()` — parses `skills/bmad-agent-{specialist_name}/SKILL.md` YAML frontmatter via PyYAML; asserts ONLY `name` + `description` keys (per FR101 R1-restated contract via Errata 2; option-a alignment shape).
- Method `assert_sanctum_path_equality()` — derives sanctum directory at `_bmad/memory/bmad-agent-{specialist_name}/`; asserts existence + 6-file BMB pattern (`INDEX.md` / `PERSONA.md` / `CREED.md` / `BOND.md` / `MEMORY.md` / `CAPABILITIES.md`). EXEMPT for Class-D2 sidecar variant.
- Method `assert_class_template_conformance()` — calls `validate_parity_test_class_conformance.py` (CREATE-task #4) AST-walker on the calling subclass; asserts class-shape conforms to one of 5 templates per NFR-I12.
- Abstract hook `cold_activation_smoke()` — subclasses implement to run `from app.specialists.{specialist_name}.graph import build_{specialist_name}_graph` import + node-list smoke (per FR101 SR-T8 amended contract).
- **Pythonic-OOP design:** does NOT inherit `unittest.TestCase` (framework is pytest); subclasses are pytest-style classes that mix-in via composition or expose `assert_*` helpers as static-friendly methods. Document the mixin pattern in module docstring with worked example.

### CREATE-task #3 (AC-7b.1-C): `tests/composition/_chain_test_base.py`

Author class `ChainTestBase` providing reusable assertion harness for cross-specialist chain tests (per NFR-CG14 chain-test PR pre-merge requirement):
- Class attributes: `upstream_specialist: str` + `downstream_specialist: str` + `gate_id: str` + `cassette_path: str`.
- Method `assert_envelope_handoff()` — asserts upstream's `SpecialistReturn` shape-compatible with downstream's `SpecialistEnvelope` (per `app/models/state/` four-file-lockstep).
- Method `assert_no_cross_specialist_substrate_drift()` — asserts no diff in `app/marcus/orchestrator/dispatch_adapter.py` substrate between upstream and downstream invocations within the chain (FR113 + NFR-I13 binding).
- Method `replay_chain_from_cassette()` — replays a fixture cassette (under `tests/fixtures/specialist-replay/{upstream}-to-{downstream}/`) and asserts deterministic chain output.
- Wall-clock budget: per-chain-test <120s aggregate (NFR-CG14a budget; subclass annotates `@pytest.mark.timeout(120)`).
- **DO NOT modify** existing chain test at `tests/composition/test_texas_to_cd_chain.py` (substrate-frozen-paths invariant; future chain-tests inherit, existing test stands).

### CREATE-task #4 (AC-7b.1-D): `scripts/utilities/validate_parity_test_class_conformance.py`

Scaffold the validator:
- CLI `python scripts/utilities/validate_parity_test_class_conformance.py [test_file_or_dir]` (defaults to `tests/parity/`).
- AST-walk: parses each `test_*_activation_contract.py` file under `tests/parity/`; identifies the test class; asserts the class derives (directly or transitively) from `SanctumParityTestBase`; asserts required class-attributes (`specialist_name`, `class_template_id`); asserts required hooks present (per template; Class-A: rubric-semantics hooks; Classes B/C/C+/D1/D2 = stub assertions extensible by Wave 2-5 stories).
- Initial 7b.1 implementation: enforce ONLY Class-A template (rubric-semantics: must override `cold_activation_smoke`; class_template_id must be `"A"` or `"a"` case-insensitive). Stories 7b.4/7b.5/7b.10/7b.11 extend the validator with B/C/C+/D1/D2 template assertions in lockstep.
- Exit codes: 0 = all parity tests conform; 1 = one or more violations (named per file + line). Block-mode finding per NFR-I12.
- CI wiring to `.github/workflows/specialist-parity.yml` job `class-conformance` is OPTIONAL at this story (the workflow may not yet exist; if absent, file as 7b.12 closeout deliverable in deferred-inventory).

**T2 commit message (mandatory format):**
```
feat(slab-7b-wave-1-substrate): T1 CREATE-tasks atomic land — Errata 4 ratification + SanctumParityTestBase + chain-test base + class-conformance validator scaffold

Wave-1 substrate gate per Round-(e) E5 prerequisite_stories binding-hard.
After this commit: 7b.2 + 7b.3 unblock for parallel open via bmad-create-story.

- AC-7b.1-A: Errata 4 verdict-flat ratified in tests/parity/README.md
- AC-7b.1-B: SanctumParityTestBase at tests/parity/_sanctum_parity_base.py
- AC-7b.1-C: ChainTestBase at tests/composition/_chain_test_base.py
- AC-7b.1-D: validate_parity_test_class_conformance.py scaffold (Class-A only)
- Closes deferred-inventory follow-on fr105-tests-parity-per-specialist-subdir-decision
```

## Files in scope (T3-T9 — Texas hardening proper)

**New (≥9 files; final list at T9):**
- `tests/parity/test_skill_md_sanctum_alignment.py` — sanctum alignment for Texas (Class-A template; SG-4 first enforcement) per AC-7b.1-G
- `tests/parity/test_texas_activation_contract.py` — flat layout per Errata 4 verdict; inherits `SanctumParityTestBase`; Class-A template per AC-7b.1-H
- `tests/parity/test_trial_475_texas_hardening_regression.py` — trial-475 root-cause regression (DISTINCT from existing `tests/parity/test_trial_475_directive_composition_regression.py` which captures 7a.1 Gap-2) per AC-7b.1-K
- `tests/specialists/texas/test_texas_live_retrieval_against_real_directive.py` — AC-7b.1-E
- `tests/specialists/texas/test_texas_g0_evidence_sentence_rubric.py` — AC-7b.1-F
- `tests/specialists/texas/test_texas_word_count_belt_and_suspenders.py` — parametrized 100/499/500/600 — AC-7b.1-F
- `tests/specialists/texas/test_texas_cross_validation_hint_application.py` — parametrized hints-supplied vs empty — AC-7b.1-F
- `tests/composition/test_slab_7b_wave_1_opener_composition_smoke.py` — Composition Smoke at slab-opener per AC-7b.1-L (NFR-CG2 inherited from Slab 7a 7a.1)
- `_bmad-output/implementation-artifacts/migration-7b-1-texas-hardening-composition-smoke.md` — Composition Smoke evidence file per AC-7b.1-L
- `_bmad-output/implementation-artifacts/7b-1-codex-self-review-2026-04-XX.md` — T10 G6 self-review

**Modified:**
- `app/specialists/texas/_act.py` — replace fixture-stub fallback with live retrieval; six-canonical-artifacts contract emission; G0 6-dim rubric in `verify` node; word-count belt-and-suspenders raising `RetrievalScopeError`; cross-validation hint application logged to `extraction-report.yaml`. **AC-B 150-LOC ceiling: `_act` body ≤150 LOC; HALT-AND-SURFACE if exceeds.**
- `tests/parity/README.md` — augment with §"FR105 + Errata 4 layout decision" per CREATE-task #1 (T2)
- `_bmad-output/planning-artifacts/deferred-inventory.md` — close `fr105-tests-parity-per-specialist-subdir-decision` follow-on (T2)
- `skills/bmad-agent-texas/SKILL.md` — verify YAML frontmatter is minimal (only `name` + `description`); fix if drifted per AC-7b.1-G

**Do NOT modify:**
- `app/marcus/orchestrator/dispatch_adapter.py` lines 70-95 (substrate-frozen-paths; FR113 + NFR-I13 binding; AC-7b.1-J).
- 7a.1-7a.8 surfaces (only consume; the 8 prior stories' interfaces are stable).
- `_bmad/memory/bmad-agent-texas/` 6-file BMB pattern (verify only — already populated at slab-2a.4 era).
- `tests/composition/test_texas_to_cd_chain.py` (existing chain test stands; future chain-tests inherit `ChainTestBase`).
- `state/config/pipeline-manifest.yaml` (no manifest changes in 7b.1 scope).
- v4.2 prompt pack.

## Critical implementation notes

- **Six-canonical-artifacts contract (AC-7b.1-E):** `extracted.md` / `metadata.json` / `extraction-report.yaml` / `manifest.json` / `ingestion-evidence.md` / `result.yaml` ALL written under `<bundle_dir>/` per FR89. Use canonical PyYAML for YAML emit (NOT ruamel). Mirror existing artifact-emission patterns from `app/specialists/texas/retrieval_dispatch.py` if any precedent exists.

- **G0 6-dim evidence-sentence rubric (AC-7b.1-F):** every claim in `extracted.md` carries an evidence-sentence anchor traceable to corpus source-of-truth. The 6 dimensions are codified in FR89 prose; consult `docs/dev-guide/g0-evidence-sentence-rubric-guide.md` if exists OR derive from PRD FR89.

- **Word-count belt-and-suspenders (AC-7b.1-F):** `len(extracted.md.split()) >= floor` per directive scope. Floor parameterized per `RetrievalIntent.expected_corpus_size`. Raise `RetrievalScopeError` (NOT `pytest.fail` — domain error) on under-floor. Define `RetrievalScopeError(Exception)` in `app/specialists/texas/_act.py` if not already present.

- **Cross-validation hint application (AC-7b.1-F):** conditional on `RetrievalIntent.cross_validation_hints: list[str]` non-empty. If empty, log to `extraction-report.yaml §cross_validation` as `{ applied: false, reason: "no hints supplied by directive" }`. If non-empty, log applied hints + per-hint outcomes.

- **AC-B 150-LOC ceiling discipline (per Slab 2a.2 precedent MF4):** Texas `_act` body must remain ≤150 LOC. If exceeds at T4, HALT and raise to operator a re-scope decision (split-to-7b.1a vs re-scope-up). The 3pt budget holds ONLY under bounded-scope discipline.

- **Substrate-as-floor invariant (AC-7b.1-J):** NO diff in `app/marcus/orchestrator/dispatch_adapter.py` lines 70-95 absent `substrate-amendment:` trailer + Marcus-Winston co-sign in commit message. Verify via `git diff master...HEAD app/marcus/orchestrator/dispatch_adapter.py` returning nothing in 70-95 range.

- **SG-4 first-enforcement (AC-7b.1-G):** `skills/bmad-agent-texas/SKILL.md` must be option-a sanctum-aligned per FR101 R1-restated contract — minimal frontmatter (`name` + `description` only). The `_bmad/memory/bmad-agent-texas/` sanctum dir has 6-file BMB pattern already (verify only). The new parity test `tests/parity/test_skill_md_sanctum_alignment.py` (this story creates) must PASS for Texas with Class-A template assertions.

- **Trial-475 regression test (AC-7b.1-K):** distinct from existing `tests/parity/test_trial_475_directive_composition_regression.py` (which is 7a.1 Gap-2 closure on the directive-composer side). New file `tests/parity/test_trial_475_texas_hardening_regression.py` is the Texas-side companion: trial-475 input (deterministic cassette) replays against new Texas hardening; asserts six-canonical-artifacts contract honored. Wrap with `pytest.skip(...)` if cassette unavailable.

- **Composition Smoke at Wave-1 slab-opener (AC-7b.1-L):** required per NFR-CG2 inherited from Slab 7a 7a.1 (every slab-opener emits Composition Smoke evidence at story-open with PASS verdict). New file `tests/composition/test_slab_7b_wave_1_opener_composition_smoke.py` asserts: (i) Texas import path stable; (ii) directive-composer ↔ Texas chain handoff envelope shape-compatible; (iii) sanctum cold-read smoke (Texas `plan` node loads `_bmad/memory/bmad-agent-texas/INDEX.md` deterministically per fingerprint stability rule from Slab 2a.2 §AC-F). Evidence at `_bmad-output/implementation-artifacts/migration-7b-1-texas-hardening-composition-smoke.md` (PASS verdict per NFR-CG2 contract).

- **Wave-1 close tripwire ledger (AC-7b.1-M):** at story close, append entry to `sprint-status.yaml::tripwire_events` (lockstep schema landed at Round-(e) E2). Schema:
```yaml
tripwire_events:
  - tripwire_id: wave_1_close
    story_owner: 7b-1
    fired_at: <YYYY-MM-DD>
    fired_verdict: <true|false>
    measured_value:
      kloc_aggregate: <N.NN>
      per_story:
        7b-1: <N.NN>
        7b-2: not-yet-evaluated
        7b-3: not-yet-evaluated
    escalation_action_taken: <none|wave_2_irene_at_upper_band_k_target_only>
    decision_record_link: _bmad-output/implementation-artifacts/migration-7b-1-texas-hardening.md§dev-agent-record-completion-notes
```
If `fired_verdict: true`, escalation per Round-(a) Amelia A3: Wave-2a (Story 7b.4 Irene Pass-1) opens at upper-band K-target — record this as a follow-on action in `next-session-start-here.md` at story close.

- **PyYAML, NOT ruamel.**
- **No new third-party deps.**

## Verification battery (T9)

```bash
.venv/Scripts/python.exe -m pytest tests/parity/test_skill_md_sanctum_alignment.py tests/parity/test_texas_activation_contract.py tests/parity/test_trial_475_texas_hardening_regression.py tests/specialists/texas tests/composition/test_slab_7b_wave_1_opener_composition_smoke.py -q --tb=short
.venv/Scripts/python.exe -m pytest tests/unit/manifest tests/integration/marcus tests/composition tests/parity tests/structural tests/unit/marcus tests/specialists/texas tests/specialists/_scaffold tests/cli tests/unit/models -q --tb=line --ignore=tests/integration/marcus/test_directive_confirm_or_edit_prompt.py
.venv/Scripts/python.exe scripts/utilities/check_pipeline_manifest_lockstep.py
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7b-1-texas-hardening.md
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/
.venv/Scripts/python.exe -m ruff check app/specialists/texas/_act.py tests/parity tests/specialists/texas tests/composition scripts/utilities/validate_parity_test_class_conformance.py
.venv/Scripts/lint-imports.exe
```

Expected: zero new failures vs post-Round-(e) baseline (696 + ~25-new = ~721 passed, 19 skipped).

## T10 + T11 + T12

- **T10:** Codex G6 self-review (Blind / Edge / Auditor) at `_bmad-output/implementation-artifacts/7b-1-codex-self-review-2026-04-XX.md`. Flip story status `in-progress` → `review`. Hand to Claude.
- **T11 (Claude):** FINAL bmad-code-review at `_bmad-output/implementation-artifacts/7b-1-code-review-2026-04-XX.md`. Adversarial + edge-case + acceptance-auditor. PASS / PASS-WITH-PATCH / HALT-AND-REMEDIATE. Remediation cycle 1 if needed.
- **T12 (Claude):** sprint-status flip `migration-7b-1-texas-hardening: review → done`; epic stays `in-progress` until 7b.12 close; tripwire-events ledger entry per AC-7b.1-M; `next-session-start-here.md` pivot to Wave-1 parallel openings (7b.2 + 7b.3 ready); deferred-inventory updates; commit + push.

## Boundary

**HALT-AND-SURFACE on:**
- (a) Round-(e) governance JSON pin mismatch (T1 first command non-zero exit).
- (b) Wave 0 artifact missing (any of 6 paths absent).
- (c) Slab 7a Epic NOT closed-done OR any 7a.X story not at `done`.
- (d) `dispatch_retrieval` keyword-only signature drift.
- (e) **Texas `_act` body exceeds AC-B 150-LOC ceiling at T4** — re-scope party-mode required.
- (f) Substrate-frozen-paths violation: any diff to `app/marcus/orchestrator/dispatch_adapter.py:70-95`.
- (g) K-actual exceeds 1.7× target (~3.4K LOC OR ~37 active tests) — K-target is at CEILING per Slab 2a.2 + Round-(a) Amelia A3 tripwire framework. **Wave-1 close tripwire fires at >2.7K LOC aggregate across 7b.1 + 7b.2 + 7b.3 — your 7b.1 portion alone exceeding 2.7K is already a Wave-1 escalation signal.**
- (h) Any sandbox-AC violation (fail validator).
- (i) FR101 parity-test contract drift from BMB checklist canonical (FR108).
- (j) Sanctum 6-file BMB pattern missing or drifted at `_bmad/memory/bmad-agent-texas/`.

**Do NOT:**
- Touch `app/marcus/orchestrator/dispatch_adapter.py` lines 70-95.
- Touch existing `tests/composition/test_texas_to_cd_chain.py` (substrate-frozen).
- Touch v4.2 prompt pack OR `state/config/pipeline-manifest.yaml`.
- Introduce ruamel.yaml or new third-party deps.
- Author `tests/parity/per_specialist/` subdir (Errata 4 verdict-flat per AC-7b.1-A; existing flat layout is canonical).
- Modify 7a.1-7a.8 surfaces (only consume; their interfaces are stable).
- Modify `OperatorVerdict` model (7a.4 owns).
- Skip the T2 atomic-commit discipline — Wave-1 parallelism unblock depends on it.

**Round-(e) E5 reminder:** at T2 atomic-commit, sprint runner can open 7b.2 + 7b.3 in parallel via bmad-create-story. Do NOT wait until 7b.1 fully closes — T2 commit is the unblock signal per binding-hard contract.
```
