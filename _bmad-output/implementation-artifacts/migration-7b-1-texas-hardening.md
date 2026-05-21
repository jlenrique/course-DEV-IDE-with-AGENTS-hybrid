# Migration Story 7b.1: Texas Hardening â€” Live Retrieval Against Real Directive Composer

**Status:** done
**Sprint key:** `migration-7b-1-texas-hardening`
**Epic:** Slab 7b Specialist Body Activation â€” `epic-slab-7b-specialist-activation-eleven`. **Wave 1 slab-opener** (Class-A hardening; first body-activation story in Slab 7b; bears 4 T1 CREATE-tasks for Wave-1 substrate that 7b.2 + 7b.3 inherit via `prerequisite_stories: ["7b-1"]` in `docs/dev-guide/migration-story-governance.json`).
**Pts:** 3 | **Gate:** single (per `docs/dev-guide/migration-story-governance.json::stories.7b-1` â€” single-gate; rationale: null; rubric-semantics work, not schema-shape, not lane-boundary) | **K-target:** ~1.3Ã— (target ~25 tests / floor 19; ~2K LOC; Wave-1 close tripwire fires at >2.7K LOC per Round-(a) Amelia A3)
**Author:** **Claude** (per NFR-CG17 + D21 â€” Class A is Claude-authored). **Review:** **Codex** via `bmad-code-review` (mutual-handoff per Slab 7a NEW CYCLE precedent; CLAUDE.md sprint governance).

---

## Round-(e) Governance Just Landed (2026-04-29 â€” binding for this story)

The party-mode round-(e) governance-JSON freeze closed **GO unanimous (4/4) on consolidated amendment block E1-E7** earlier this session (voices: John + Mary + Amelia + Murat). Six structural amendments ratified into `docs/dev-guide/migration-story-governance.json`:

- **E2** â€” top-level `tripwire_escalation_record_path` slot designated â†’ `_bmad-output/implementation-artifacts/sprint-status.yaml::tripwire_events` (lockstep `tripwire_events: []` schema landed in same commit; this story's Wave-1 close tripwire records here per AC-7b.1-M).
- **E5** â€” 7b.2 + 7b.3 carry `prerequisite_stories: ["7b-1"]` with `binding=hard`. **Sprint runner MUST NOT open 7b.2 or 7b.3 until this story's 4 T1 CREATE-tasks land atomically.** This story is the Wave-1 substrate gate.
- **E6** â€” `k_contract` blocks added to 7b-5/10/11/12 per 7a-4 precedent. Not directly load-bearing on 7b.1 but signals the K-discipline regime; this story's Wave-1 close tripwire (>2.7K LOC) is recorded at the top-level tripwire ledger.
- E1, E3, E4 are 7b-7/8/11/5-scoped (downstream stories); not load-bearing on 7b.1 dev work.
- **E7** â€” version bump â†’ `2026-04-29-slab7b-twelve-stories`; this story consumed staged-no-more entry; lockstep test `tests/parity/test_nfr_cg_block_aggregated.py::test_nfr_cg_block_structural_evidence[NFR-CG6]` updated in same commit (now PASSING against new version pin).

**T1 readiness verification command:**
```bash
.venv/Scripts/python.exe -c "import json; d = json.load(open('docs/dev-guide/migration-story-governance.json', encoding='utf-8')); assert d['version'] == '2026-04-29-slab7b-twelve-stories'; assert '_staged_pending_party_mode_ratification' not in d['stories']['7b-1']; assert d['stories']['7b-2']['prerequisite_stories'] == ['7b-1']; print('Round-(e) verified PASS')"
```

---

## T1 Readiness Block

**Before writing any production code, dev-agent reads + verifies in order:**

### Required-readings cascade (CLAUDE.md Â§Lesson Planner MVP â€” Slab-7b dev-agent references inherited)

1. **Round-(e) governance freeze** â€” `docs/dev-guide/migration-story-governance.json` Â§`stories.7b-1`. Confirm `expected_gate_mode: "single-gate"`, `expected_k_target: 1.3`, no `_staged_pending_party_mode_ratification` flag (must be absent post-Round-(e)).
2. **Epic + story-level scope** â€” [`_bmad-output/planning-artifacts/epics-slab-7b-specialist-activation-eleven.md`](../planning-artifacts/epics-slab-7b-specialist-activation-eleven.md) Â§Epic 1 Story 7b.1 (lines 427â€“483). 4 R(a)-R(d) party-mode rounds RATIFIED; 8 amendments folded inline; 0 re-opens. Murat A4 (Round-(a)) is the operative T1 CREATE-task amendment.
3. **PRD FR89 contract** â€” [`_bmad-output/planning-artifacts/prd-slab-7b-specialist-activation-eleven.md`](../planning-artifacts/prd-slab-7b-specialist-activation-eleven.md) Â§FR89 (line 789): live-retrieval-against-real-directive-composer; six-canonical-artifacts contract enforcement (`extracted.md` / `metadata.json` / `extraction-report.yaml` / `manifest.json` / `ingestion-evidence.md` / `result.yaml`); G0 6-dim evidence-sentence rubric; word-count belt-and-suspenders check; cross-validation hint application.
4. **PRD errata addendum** â€” same PRD Â§Errata 1-4. Errata 3 mandates `SanctumParityTestBase` as Wave-1 deliverable (CREATE-task #2 below). Errata 4 mandates this story's T1 ratifies subdir-vs-flat layout for `tests/parity/per_specialist/` (CREATE-task #1 below; recommendation: flat â€” codebase already uses flat under `tests/parity/`).
5. **BMB sanctum alignment checklist (FR108; SG-4 substrate)** â€” [`docs/dev-guide/bmb-sanctum-alignment-checklist.md`](../../docs/dev-guide/bmb-sanctum-alignment-checklist.md). Canonical authority for FR101 parity-test contract; references option-a/option-b per FR109 closed allowlist at [`docs/dev-guide/sanctum-exception-categories.json`](../../docs/dev-guide/sanctum-exception-categories.json).
6. **Specialist anti-patterns** â€” [`docs/dev-guide/specialist-anti-patterns.md`](../../docs/dev-guide/specialist-anti-patterns.md) (A1-A17 + P1-P3).
7. **Specialist migration template** â€” [`docs/dev-guide/specialist-migration-template.md`](../../docs/dev-guide/specialist-migration-template.md) (R1-R14 rules).
8. **Slab 2a.2 precedent (closest Class-A analog)** â€” [`migration-2a-2-irene-pass-2-scaffold-migration.md`](migration-2a-2-irene-pass-2-scaffold-migration.md). 9-node scaffold + AC-B 150-LOC ceiling discipline; sanctum cold-read at `plan` node; cache-hit-rate baseline harness pattern.
9. **Slab 7a 7a.1 NEW CYCLE precedent** â€” [`migration-7a-1-directive-composer.md`](migration-7a-1-directive-composer.md). Directive composer is the upstream substrate this story consumes; T1 verifies `app/marcus/orchestrator/directive_composer.py` honors `dispatch_retrieval(directive_path, bundle_dir)` keyword-only signature (already verified in PRD errata addendum line 1212).
10. **CLAUDE.md governance sections** â€” `Â§LangChain/LangGraph migration â€” sandbox-AC + gate-mode governance`, `Â§BMAD sprint governance`, `Â§Pipeline lockstep regime`, `Â§Deferred inventory governance`.

### Wave 0 artifact-existence sweep

Confirm Wave-0 deliverables (commit `9ed6fcb`) present + addressable:
```bash
ls docs/dev-guide/bmb-sanctum-alignment-checklist.md \
   docs/dev-guide/sanctum-exception-categories.json \
   docs/dev-guide/operator-control-parity-template.md \
   docs/dev-guide/migration-ac-sandbox-inventory.json \
   skills/bmad-agent-cora/SKILL.md
ls docs/dev-guide/scaffolds/scaffold-v0.2-D2-pipeline/
```
All six paths must exist. If any absent, HALT â€” Wave-0 substrate is missing; cannot proceed.

### Texas current-state probe (pre-existing baseline at Slab 2a.4 era)

```bash
ls app/specialists/texas/                  # graph.py state.py model_config.yaml retrieval_dispatch.py expertise/
ls _bmad/memory/bmad-agent-texas/          # BOND.md CAPABILITIES.md CREED.md INDEX.md MEMORY.md PERSONA.md (+ CLONE-FORK-NOTICE.md + capabilities/ references/ scripts/ sessions/)
ls skills/bmad-agent-texas/                # SKILL.md assets/ references/ scripts/
.venv/Scripts/python.exe -c "from app.specialists.texas.retrieval_dispatch import dispatch_retrieval; import inspect; sig = inspect.signature(dispatch_retrieval); assert 'directive_path' in sig.parameters and 'bundle_dir' in sig.parameters; print('FR89 dispatch_retrieval signature OK')"
```

Expected: passthrough scaffold + 6-file BMB sanctum + retrieval_dispatch.py at slab-2a.4 era. Texas hardening advances the `_act` body from this baseline â€” it does NOT introduce new file paths under `app/specialists/texas/` (the scaffold is already there).

### Sandbox-AC validator pre-flight (CLAUDE.md governance)

```bash
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py \
  _bmad-output/implementation-artifacts/migration-7b-1-texas-hardening.md
```
Expect PASS. No forbidden CLI (`docker`, `psql`, `gh`, `aws`, `gcloud`, `az`, `kubectl`, `helm`, `redis-cli`, `mongo`, `mysql`, `curl`, `wget`) appears in dev-agent AC blocks. Live-API verification (none expected for 7b.1; Texas is rubric-semantics + retrieval-orchestration, not third-party-API-bound) is split to operator-gated `(operator-gated)` AC blocks if any surface; this story does not require any.

### Standing pre-flight items (every Slab 7b story)

1. Severance posture confirmed â€” hybrid working tree is sole input surface; no `git show upstream/master:â€¦` (per memory `project_upstream_severance.md`).
2. `state/config/substrate-frozen-paths.yaml` (FR108-derived; substrate-as-floor closed-list) â€” diffs touching `app/marcus/orchestrator/dispatch_adapter.py:70-95` require `substrate-amendment:` trailer + Marcus-Winston co-sign; this story does NOT touch substrate (FR113 + NFR-I13 binding).
3. NFR-CG14a chain-test base class is a CREATE-task in this story (#3 below); 7b.2 + 7b.3 chain-tests inherit from it.
4. NFR-T9-T12 wall-clock ceilings hold per individual test annotation (`@pytest.mark.timeout`).

---

## Story

As a **migration dev agent**,
I want **Texas's `_act` body hardened to execute live retrieval against the Slab 7a directive composer's output (no fixture-stub fallback) â€” emitting the six-canonical-artifacts contract per FR89 (G0 6-dim evidence-sentence rubric + word-count belt-and-suspenders + cross-validation hint application) â€” AND I want the four Wave-1 substrate CREATE-tasks landed atomically (Errata 4 ratification + `SanctumParityTestBase` + `_chain_test_base.py` + `validate_parity_test_class_conformance.py` scaffold)**,
So that **(a) Trial-2 advances past G0 with real corpus extractions reviewed against the 33-row mapping checklist's G0 row, (b) Trial-475's pause-at-G1 fixture-stub failure mode cannot recur, (c) the SG-4 sanctum-alignment substrate is verified end-to-end on the first Wave-1 body-activation, and (d) 7b.2 (Quinn-R) + 7b.3 (Vera) Wave-1 parallel openings are unblocked per Round-(e) E5 `prerequisite_stories: ["7b-1"]` binding-hard contract**.

---

## Acceptance Criteria

All ACs are dev-agent-executable (sandbox-AC compliant). No third-party API live-binding required (Texas is retrieval-orchestration, not API-bound). Live-substrate verification (the directive composer end-to-end smoke) wraps via shipped Python deps (no operator-only CLIs).

### AC-7b.1-A â€” T1 CREATE-Task #1: Errata 4 subdir-vs-flat ratification recorded

**Given** PRD Errata 4 (commit `ddcd1b1`) leaves the `tests/parity/per_specialist/` subdir vs flat-named layout decision pending at Wave-1 first-story T1
**And** the existing `tests/parity/` directory uses flat naming (no subdirs; e.g., `test_composition_spec_invariants.py` flat at top level â€” verified at this story T1)
**When** the dev agent records the ratification decision in `tests/parity/README.md`
**Then** `tests/parity/README.md` exists or is augmented with a Â§"FR105 + Errata 4 layout decision" section recording: **VERDICT â€” flat naming** (`test_<specialist_name>_activation_contract.py` at `tests/parity/` top-level; NOT `tests/parity/per_specialist/test_<specialist>.py`); rationale: "embrace boring technology" (Winston) + matches existing flat convention + reduces import-graph complexity
**And** the deferred-inventory follow-on `fr105-tests-parity-per-specialist-subdir-decision` is updated in [`_bmad-output/planning-artifacts/deferred-inventory.md`](../planning-artifacts/deferred-inventory.md) Â§Named-But-Not-Filed Follow-Ons â†’ **CLOSED at Story 7b.1 T1 with verdict-flat**.

### AC-7b.1-B â€” T1 CREATE-Task #2: `SanctumParityTestBase` (Errata 3 + FR101 + NFR-I9 + NFR-I12)

**Given** PRD Errata 3 mandates `SanctumParityTestBase` as a Wave-1 deliverable (does not pre-exist) AND the FR101 parity-test contract restated at PRD errata is canonical (per BMB sanctum alignment checklist)
**When** the dev agent authors `tests/parity/_sanctum_parity_base.py`
**Then** the file lands with a class `SanctumParityTestBase` providing reusable assertion harness for sanctum-vs-shipped-paths invariants â€” minimal contract:
  - `class SanctumParityTestBase` (abstract; subclasses provide `specialist_name` + `class_template_id` class attributes + override hooks)
  - Method `assert_skill_md_minimal_frontmatter()` â€” parses `skills/bmad-agent-{specialist_name}/SKILL.md` YAML frontmatter via PyYAML; asserts only `name` + `description` keys (per FR101 R1-restated contract via Errata 2; option-a alignment shape).
  - Method `assert_sanctum_path_equality()` â€” derives sanctum directory at `_bmad/memory/bmad-agent-{specialist_name}/`; asserts existence + 6-file BMB pattern present (`INDEX.md` / `PERSONA.md` / `CREED.md` / `BOND.md` / `MEMORY.md` / `CAPABILITIES.md`). EXEMPT for Class-D2 sidecar variant (Compositor only â€” not load-bearing in this story).
  - Method `assert_class_template_conformance()` â€” calls `validate_parity_test_class_conformance.py` (CREATE-task #4) AST-walker on the calling subclass; asserts class-shape conforms to one of 5 templates (A/B/C/C+/D1/D2 per NFR-I12). 7b.1 itself asserts Class A conformance.
  - Cold-activation smoke hook (per FR101 SR-T8 amended contract) â€” abstract `cold_activation_smoke()` method that subclasses implement to run a `from app.specialists.{specialist_name}.graph import build_{specialist_name}_graph` import + node-list smoke.
**And** Pythonic-OOP design rules apply: `SanctumParityTestBase` does NOT itself inherit from `unittest.TestCase` (the framework is pytest); subclasses are pytest-style classes that mix-in via composition or expose `assert_*` helpers as static-friendly methods. Document the mixin pattern in the file's module docstring with a worked example.

### AC-7b.1-C â€” T1 CREATE-Task #3: `_chain_test_base.py` (NFR-CG14a)

**Given** NFR-CG14a mandates a chain-test base class precondition; PRD errata Resolution: First Wave-1 story authors the base
**When** the dev agent authors `tests/composition/_chain_test_base.py`
**Then** the file lands with class `ChainTestBase` providing reusable assertion harness for cross-specialist chain tests (per NFR-CG14 chain-test PR pre-merge requirement) â€” minimal contract:
  - `class ChainTestBase` (abstract; subclasses provide `upstream_specialist`, `downstream_specialist`, `gate_id`, `cassette_path` attributes)
  - Method `assert_envelope_handoff()` â€” asserts upstream's `SpecialistReturn` is shape-compatible with downstream's `SpecialistEnvelope` (per `app/models/state/` four-file-lockstep).
  - Method `assert_no_cross_specialist_substrate_drift()` â€” asserts no diff in `app/marcus/orchestrator/dispatch_adapter.py` substrate between upstream and downstream invocations within the chain (FR113 + NFR-I13 binding).
  - Method `replay_chain_from_cassette()` â€” replays a fixture cassette (under `tests/fixtures/specialist-replay/{upstream}-to-{downstream}/`) and asserts deterministic chain output.
  - Wall-clock budget: per-chain-test <120s aggregate (NFR-CG14a budget; subclass annotates `@pytest.mark.timeout(120)`).
**And** the existing chain test at `tests/composition/test_texas_to_cd_chain.py` (Slab 2a.4 era) is **NOT modified by this story** (substrate-frozen-paths invariant; if it must be migrated to inherit `ChainTestBase`, that's a follow-on filed in deferred-inventory). Future Wave-1 chain tests inherit; existing tests stand.

### AC-7b.1-D â€” T1 CREATE-Task #4: `validate_parity_test_class_conformance.py` scaffold (NFR-I12)

**Given** NFR-I12 (R7 Murat) mandates per-PR validation that every per-specialist parity test conforms to one of 5 class templates (A/B/C/C+/D1/D2)
**When** the dev agent scaffolds `scripts/utilities/validate_parity_test_class_conformance.py`
**Then** the script lands with:
  - CLI `python scripts/utilities/validate_parity_test_class_conformance.py [test_file_or_dir]` (defaults to `tests/parity/`)
  - AST-walk: parses each `test_*_activation_contract.py` file under `tests/parity/`; identifies the test class; asserts the class derives (directly or transitively) from `SanctumParityTestBase`; asserts required class-attributes (`specialist_name`, `class_template_id`); asserts required hooks present (per template; e.g., Class-A: rubric-semantics hooks; Class-B: persona-continuity hooks; Class-C/C+: cache-hit-rate hook; Class-D1: greenfield-scaffold hook; Class-D2: pipeline-determinism hook).
  - Stub assertions extensible by Wave 2-5 stories â€” initial 7b.1 implementation only enforces Class-A template (rubric-semantics: must override `cold_activation_smoke`; class_template_id must be `"A"` or `"a"` case-insensitive). Stories 7b.4/7b.5/7b.10/7b.11 extend the validator with B/C/C+/D1/D2 template assertions in lockstep with their per-class first-test landings.
  - Exit codes: 0 = all parity tests conform; 1 = one or more violations (named per file + line). Block-mode finding per NFR-I12.
**And** the script is wired to `.github/workflows/specialist-parity.yml` (job: `class-conformance`) as a required check (or, if the workflow doesn't yet exist, the wiring is a 7b.12 closeout deliverable per Round-(c) â€” file the wiring as Story 7b.1 follow-on if needed).

### AC-7b.1-E â€” Texas live retrieval against real directive composer (FR89 primary)

**Given** the Slab 7a directive composer at `app/marcus/orchestrator/directive_composer.py` (production substrate; verified at T1 per Wave-0 sweep)
**And** Texas's existing scaffold at `app/specialists/texas/_act.py` (passthrough or fixture-stub fallback â€” slab-2a.4 era baseline)
**When** the operator invokes `bmad-trial start --input course-content/courses/<lesson-slug>/`
**Then** Marcus emits `state/runs/<run_id>/directive.yaml` per 7a.1 contract
**And** Texas's `dispatch_retrieval(directive_path=<run_id>/directive.yaml, bundle_dir=<run_id>/bundle/)` is invoked against `app/specialists/texas/_act.py` (verified via Slab 7a 7a.1 directive-composer signature: `dispatch_retrieval(*, directive_path, bundle_dir)`)
**And** Texas executes a real retrieval (NOT the fixture stub at `tests/fixtures/specialists/texas/fixture_bundle/`)
**And** the six-canonical-artifacts contract is honored â€” all six files written under `<bundle_dir>/`:
  1. `extracted.md` â€” corpus extractions per directive scope
  2. `metadata.json` â€” extraction-trace metadata (source paths, extraction timestamps, retrieval-method per directive)
  3. `extraction-report.yaml` â€” structured retrieval report (per-claim provenance + scoring)
  4. `manifest.json` â€” bundle manifest (file inventory + checksums)
  5. `ingestion-evidence.md` â€” operator-readable evidence summary
  6. `result.yaml` â€” terminal Texas verdict envelope per `SpecialistReturn`
**Test pin:** `tests/specialists/texas/test_texas_live_retrieval_against_real_directive.py` â€” 1 test using shipped `httpx` and shipped fixtures, NO operator-only CLIs. Wraps live composition with `pytest.skip(...)` if `state/runs/` substrate unavailable (e.g., post-clean-checkout state); operator-gated full-trial smoke is captured at AC-7b.1-K below.

### AC-7b.1-F â€” G0 6-dim evidence-sentence rubric + word-count check + cross-validation hint (FR89 secondary)

**Given** Texas's `_act` body running against real corpus (post-AC-E)
**When** Vera (downstream; verified via fixture replay until Story 7b.3 lands) applies the G0 6-dim evidence-sentence rubric to `extracted.md`
**Then** every claim carries an evidence-sentence anchor traceable to corpus source-of-truth (per FR89 G0 6-dim contract)
**And** the word-count belt-and-suspenders check enforces `len(extracted.md.split()) >= floor` per directive scope (the floor is parameterized per `RetrievalIntent` shape â€” derived from directive's `expected_corpus_size` field; the check is a Python assertion in Texas's `verify` node)
**And** cross-validation hint application is logged to `extraction-report.yaml Â§cross_validation`. The hint application is conditional on the `RetrievalIntent` carrying a non-empty `cross_validation_hints: list[str]` field; if empty, the section is written `cross_validation: { applied: false, reason: "no hints supplied by directive" }`.
**Test pins (3 tests total):**
  1. `tests/specialists/texas/test_texas_g0_evidence_sentence_rubric.py` â€” synthetic corpus + synthetic directive; asserts every claim in fixture `extracted.md` carries an evidence anchor.
  2. `tests/specialists/texas/test_texas_word_count_belt_and_suspenders.py` â€” synthetic directive with explicit `expected_corpus_size: 500`; asserts Texas raises `RetrievalScopeError` (NOT `pytest.fail` â€” a domain error) when extraction word-count <500 (parameterized: 100 / 499 / 500 / 600).
  3. `tests/specialists/texas/test_texas_cross_validation_hint_application.py` â€” two parametrized cases (hints supplied vs empty); asserts `extraction-report.yaml` cross_validation section structure.

### AC-7b.1-G â€” SG-4 Sanctum Alignment (FR100 + FR101 + FR108 â€” first body-activation enforcement)

**Given** the SG-4 sanctum-alignment requirement (PRD Â§FR-7b-sanctum FR100-FR103) â€” every body-activation story carries SKILL.md alignment-or-exception AC; this story is the first; option-a alignment expected for Texas (Class-A roster member)
**When** the dev-agent commits Texas hardening changes
**Then** `skills/bmad-agent-texas/SKILL.md` is verified option-a sanctum-aligned per BMB checklist (FR108):
  - YAML frontmatter MINIMAL â€” keys `name` + `description` only (per Errata 2 contract); no `tools:` / `allowed-tools:` / `model:` / etc.
  - SKILL.md body references `_bmad/memory/bmad-agent-texas/` sanctum dir as activation-time hot-load batch (per Marcus precedent + Cora-sidecar exception path).
**And** the sanctum dir at `_bmad/memory/bmad-agent-texas/` carries the 6-file BMB pattern (`INDEX.md` / `PERSONA.md` / `CREED.md` / `BOND.md` / `MEMORY.md` / `CAPABILITIES.md` â€” already present at slab-2a.4 era; this story verifies, does not create).
**And** the new parity test `tests/parity/test_skill_md_sanctum_alignment.py` (created in this story per FR101) passes for Texas with Class-A template assertions (`SanctumParityTestBase` inherited; minimal frontmatter; sanctum-path equality; 6-file BMB pattern; Class-A cold-activation smoke).
**And** `bmad-code-review` (T11 task below) confirms `# SG-4 Sanctum Alignment` AC verbatim in this story planning artifact (per FR100). The verbatim heading must be present â€” reviewer does an AST-grep for the exact heading string before accepting close.

### AC-7b.1-H â€” FR105 per-specialist parity test (Texas activation contract; flat layout per Errata 4 verdict)

**Given** the Errata 4 layout verdict ratified at AC-A above (flat naming under `tests/parity/`)
**When** the dev-agent authors Texas's activation-contract test
**Then** `tests/parity/test_texas_activation_contract.py` (flat â€” NOT under `per_specialist/` subdir) lands
**And** the test class inherits `SanctumParityTestBase` (per AC-B contract) with `class_template_id = "A"` and `specialist_name = "texas"`
**And** the test asserts Class-A rubric-semantics parity: (i) `dispatch_retrieval(*, directive_path, bundle_dir)` keyword-only signature stable; (ii) six-canonical-artifacts contract honored; (iii) G0 6-dim rubric evidence-anchor invariant; (iv) `RetrievalScopeError` raised on word-count under-floor; (v) cross-validation section structurally correct.
**And** the test runs <30s wall-clock per NFR-T9 + contributes to <120s aggregate per NFR-T12; annotated `@pytest.mark.timeout(30)`.
**And** `validate_parity_test_class_conformance.py` (per AC-D) PASSES on this test file when run.

### AC-7b.1-I â€” Sandbox-AC governance (CLAUDE.md + FR107)

**Given** the sandbox-AC inventory governance requirement at [`docs/dev-guide/migration-ac-sandbox-inventory.json`](../../docs/dev-guide/migration-ac-sandbox-inventory.json) (FR107 LANDED Wave 0)
**When** `scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7b-1-texas-hardening.md` runs
**Then** PASS (no forbidden CLI in dev-agent ACs â€” `docker`, `psql`, `gh`, `aws`, `gcloud`, `az`, `kubectl`, `helm`, `redis-cli`, `mongo`, `mysql`, `curl`, `wget`)
**And** any live-substrate verification is wrapped via shipped Python deps (e.g., `httpx` for HTTP smoke; `psycopg` for DB smoke if relevant â€” Texas is not DB-bound) with `pytest.skip(...)` when service unreachable
**And** Texas-specific note: 7b.1 has NO sandbox-AC inventory entry needed (Texas is retrieval-orchestration, not third-party-API-bound â€” distinct from Class-C stories 7b.6/7b.7/7b.8/7b.9 which consume `gamma`/`kling`/`elevenlabs`/`wondercraft` entries). FR107 inventory does NOT need an extension for this story.

### AC-7b.1-J â€” Substrate-as-floor invariant (FR113 + NFR-I13)

**Given** the substrate-as-floor invariant â€” `app/marcus/orchestrator/dispatch_adapter.py:70-95` (FR-A24 Marcus-duality boundary; Slab 7a 7a.5 close evidence) is frozen substrate
**When** the dev-agent's diff is reviewed
**Then** **no diff hunk touches `app/marcus/orchestrator/dispatch_adapter.py` lines 70-95** absent a `substrate-amendment:` trailer + Marcus-Winston co-sign in the commit message
**And** `.github/workflows/substrate-frozen-paths-check.yml` (or its functional substitute â€” `state/config/substrate-frozen-paths.yaml` referenced manually by reviewer if workflow not yet wired) PASSES at PR merge
**And** the dev-agent's commit history for this story is grep-clean for `git diff app/marcus/orchestrator/dispatch_adapter.py | grep "^[-+]"` returning zero lines under the 70-95 range. Verification command:
```bash
git diff master...HEAD app/marcus/orchestrator/dispatch_adapter.py | head -30
# Expect: no output OR only documentation/whitespace lines OUTSIDE 70-95 range
```

### AC-7b.1-K â€” Trial-475 root-cause regression test (closes Trial-475 Gap 1 + Gap 2 follow-on per Slab 7a 7a.1 closure)

**Given** Trial-475 paused-at-G1 cleanly on 2026-04-28 (per memory `project_first_trial_outcome.md`); root-cause was Texas's silent-fixture-stub fallback when directive-composition was absent (Gap 2 closed by 7a.1; Gap 1 closes here)
**When** trial-475's input replays against the new Texas hardening
**Then** Texas receives a real directive AND advances past G0 with real extractions
**And** the regression evidence is captured in `tests/parity/test_trial_475_texas_hardening_regression.py` (note: this is DISTINCT from the existing `tests/parity/test_trial_475_directive_composition_regression.py` which captures 7a.1 Gap-2 closure; the 7b.1 file is a downstream Texas-side companion)
**And** the test fixture for trial-475 is deterministic (no live LLM; replays cassette) â€” wrapped via `pytest.skip(...)` if cassette unavailable.
**Test pin:** `tests/parity/test_trial_475_texas_hardening_regression.py` â€” 1 test asserting six-canonical-artifacts contract honored on trial-475 input.

### AC-7b.1-L â€” Composition Smoke at Wave-1 slab-opener (NFR-CG2 inherited from 7a.1)

**Given** the Composition Smoke gate at slab-openers is inherited from Slab 7a 7a.1 (NFR-CG2) â€” every slab-opener emits Composition Smoke evidence at story-open with PASS verdict
**When** the dev-agent runs Composition Smoke at this story open
**Then** `pytest tests/composition/test_slab_7a_opener_composition_smoke.py -q` PASSES (Slab 7a substrate intact post-Slab-7b-Wave-1 hardening)
**And** a NEW file `tests/composition/test_slab_7b_wave_1_opener_composition_smoke.py` lands asserting: (i) Texas import path stable (`from app.specialists.texas.graph import build_texas_graph` succeeds); (ii) directive-composer â†” Texas chain handoff envelope shape-compatible; (iii) sanctum cold-read smoke (Texas's `plan` node loads `_bmad/memory/bmad-agent-texas/INDEX.md` deterministically per fingerprint stability rule from Slab 2a.2 Â§AC-F)
**And** evidence captured at `_bmad-output/implementation-artifacts/migration-7b-1-texas-hardening-composition-smoke.md` (PASS verdict per NFR-CG2 contract).

### AC-7b.1-M â€” Wave-1 close tripwire ledger entry (Round-(e) E2/Mary structural binding)

**Given** the Round-(e) E2 amendment landed `tripwire_events: []` schema slot at `_bmad-output/implementation-artifacts/sprint-status.yaml` AND named the four Slab 7b tripwires (Wave-1 close, Wave-2b close, Wave-3 first-port, Wave-5b pre-T1)
**When** this story closes (post-T11 review)
**Then** at story close, the dev-agent appends a Wave-1-close-tripwire entry to `sprint-status.yaml::tripwire_events`:
```yaml
tripwire_events:
  - tripwire_id: wave_1_close
    story_owner: 7b-1
    fired_at: <YYYY-MM-DD>
    fired_verdict: <true|false>          # true if K-actual >2.7K LOC across 7b.1+7b.2+7b.3 aggregate
    measured_value:
      kloc_aggregate: <N.NN>
      per_story:
        7b-1: <N.NN>
        7b-2: not-yet-evaluated   # Wave-1 may close before 7b-2 if 7b-1 lands solo first; aggregate evaluates at Wave-1 final close
        7b-3: not-yet-evaluated
    escalation_action_taken: <none|wave_2_irene_at_upper_band_k_target_only>
    decision_record_link: _bmad-output/implementation-artifacts/migration-7b-1-texas-hardening.mdÂ§dev-agent-record-completion-notes
```
**And** if `fired_verdict: true`, the escalation action per Round-(a) Amelia A3 ratified set fires: Wave-2a (Story 7b.4 Irene Pass-1) opens at upper-band K-target â€” record this as a follow-on action in `next-session-start-here.md` at story close.

### AC-7b.1-N â€” Close protocol + Wave-1 parallelism unblock

**Given** this story is the Wave-1 slab-opener and bears 4 T1 CREATE-tasks that 7b.2 + 7b.3 prerequisite-block on
**When** all prior ACs PASS + bmad-code-review (Codex) returns PASS or PASS-WITH-PATCH-applied + regression baseline holds (target: 696 + new-tests passing; 19 skipped per pre-7b.1 baseline; new-tests count: ~25 per K-target)
**Then** at close:
  1. **sprint-status.yaml** flip: `migration-7b-1-texas-hardening: queued` â†’ `done` (with closeout notes); `migration-epic-slab-7b-specialist-activation-eleven: backlog` â†’ `in-progress` (first story open trigger)
  2. **next-session-start-here.md** flip: hot-start pivot from "Step 1 â†’ Step 2 (bmad-create-story 7b.1)" â†’ "Wave-1 parallel openings unblocked: 7b.2 (Quinn-R) + 7b.3 (Vera) ready for bmad-create-story OR bmad-dev-story per operator preference"
  3. **Round-(e) E5 unblock confirmation**: `prerequisite_stories: ["7b-1"]` for 7b.2/7b.3 satisfied â€” sprint runner may now open them in parallel
  4. **Composition Smoke evidence** at `_bmad-output/implementation-artifacts/migration-7b-1-texas-hardening-composition-smoke.md` filed (per AC-L)
  5. **Tripwire ledger entry** at `sprint-status.yaml::tripwire_events` (per AC-M)
  6. **Deferred-inventory updates**: `fr105-tests-parity-per-specialist-subdir-decision` â†’ CLOSED with verdict-flat (per AC-A); any new follow-ons surfaced during dev (e.g., from Codex code-review patches) filed
  7. **Standing-guardrail status snapshot**: SG-1 (11-roster) GREEN; SG-2 (33-row mapping) GREEN with G0 row improved; SG-3 (Composition Spec invariants) GREEN; **SG-4 (sanctum alignment) FIRST GREEN â€” first body-activation enforcement landed via Texas + parity-test scaffold + class-conformance validator + chain-test base** (per FR100-FR103 + NFR-I9 + NFR-I12).

---

## Tasks / Subtasks

### T1 â€” T1 readiness verification

- [x] **T1.1** Verify Round-(e) governance JSON (version pin = `2026-04-29-slab7b-twelve-stories`; no `_staged_pending_party_mode_ratification` in `7b-1`; `prerequisite_stories: ["7b-1"]` present on `7b-2` + `7b-3`)
- [x] **T1.2** Required-readings cascade (10 readings per T1 Readiness Block above)
- [x] **T1.3** Wave 0 artifact-existence sweep (6 paths)
- [x] **T1.4** Texas current-state probe (`app/specialists/texas/`, `_bmad/memory/bmad-agent-texas/`, `skills/bmad-agent-texas/`, `dispatch_retrieval` signature)
- [x] **T1.5** Sandbox-AC validator pre-flight on this story file (expect PASS)
- [x] **T1.6** Standing pre-flight (severance posture; substrate-frozen-paths; chain-test base CREATE-task awareness; NFR-T9-T12 ceilings)

### T2 â€” Land 4 T1 CREATE-tasks atomically (AC-A through AC-D)

- [x] **T2.1** Errata 4 ratification â€” author/augment `tests/parity/README.md` Â§"FR105 + Errata 4 layout decision" with verdict-flat + rationale (AC-A)
- [x] **T2.2** Update `_bmad-output/planning-artifacts/deferred-inventory.md` Â§Named-But-Not-Filed Follow-Ons â€” close `fr105-tests-parity-per-specialist-subdir-decision` with verdict-flat (AC-A)
- [x] **T2.3** Author `tests/parity/_sanctum_parity_base.py` â€” `SanctumParityTestBase` class with assertion harness + 5-template class-shape contract (AC-B)
- [x] **T2.4** Author `tests/composition/_chain_test_base.py` â€” `ChainTestBase` class with envelope-handoff + cross-specialist substrate-drift assertions (AC-C)
- [x] **T2.5** Scaffold `scripts/utilities/validate_parity_test_class_conformance.py` â€” AST-walk + Class-A template assertions stub (AC-D)
- [x] **T2.6** **Atomic-commit discipline**: T2.1-T2.5 land in a SINGLE commit BEFORE Wave-1 parallelism opens. Commit message format: `feat(slab-7b-wave-1-substrate): T1 CREATE-tasks atomic land â€” Errata 4 ratification + SanctumParityTestBase + chain-test base + class-conformance validator scaffold`. After this commit, 7b.2 + 7b.3 can open in parallel per Round-(e) E5 binding.

### T3 â€” Texas hardening implementation (AC-E + AC-F)

- [x] **T3.1** Replace fixture-stub fallback in `app/specialists/texas/_act.py` with live retrieval against `dispatch_retrieval(directive_path, bundle_dir)` (AC-E)
- [x] **T3.2** Implement six-canonical-artifacts contract emission â€” write all six files to `<bundle_dir>/` (AC-E)
- [x] **T3.3** Implement G0 6-dim evidence-sentence rubric in `verify` node (AC-F)
- [x] **T3.4** Implement word-count belt-and-suspenders check; raise `RetrievalScopeError` on under-floor (AC-F)
- [x] **T3.5** Implement cross-validation hint application in `extraction-report.yaml Â§cross_validation` (AC-F)
- [x] **T3.6** **AC-B 150-LOC ceiling discipline (per Slab 2a.2 precedent MF4)**: `_act` body must remain â‰¤150 LOC; if exceeds, dev-agent STOPS and raises party-mode re-scope decision (split-to-7b.1a vs re-scope-up). The 3pt budget holds ONLY under bounded-scope discipline.

### T4 â€” Parity tests (AC-G + AC-H)

- [x] **T4.1** Author `tests/parity/test_skill_md_sanctum_alignment.py` â€” sanctum alignment for Texas (Class-A template; SG-4 first enforcement) (AC-G)
- [x] **T4.2** Author `tests/parity/test_texas_activation_contract.py` â€” flat layout per Errata 4 verdict; inherits `SanctumParityTestBase`; Class-A template (AC-H)
- [x] **T4.3** Wall-clock annotation: `@pytest.mark.timeout(30)` per NFR-T9 (AC-H)
- [x] **T4.4** Run `validate_parity_test_class_conformance.py` (CREATE-task #4) on the new test file â€” PASS expected (AC-D + AC-H)

### T5 â€” Per-specialist behavioral tests (AC-F supplementary)

- [x] **T5.1** Author `tests/specialists/texas/test_texas_live_retrieval_against_real_directive.py` (AC-E)
- [x] **T5.2** Author `tests/specialists/texas/test_texas_g0_evidence_sentence_rubric.py` (AC-F)
- [x] **T5.3** Author `tests/specialists/texas/test_texas_word_count_belt_and_suspenders.py` â€” parametrized 100/499/500/600 (AC-F)
- [x] **T5.4** Author `tests/specialists/texas/test_texas_cross_validation_hint_application.py` â€” parametrized hints-supplied vs empty (AC-F)

### T6 â€” Trial-475 regression test (AC-K)

- [x] **T6.1** Author `tests/parity/test_trial_475_texas_hardening_regression.py` â€” Texas-side companion to 7a.1's Gap-2-closure regression test (AC-K)

### T7 â€” SG-4 sanctum alignment verification (AC-G)

- [x] **T7.1** Verify `skills/bmad-agent-texas/SKILL.md` YAML frontmatter is minimal (only `name` + `description`) â€” fix if drifted (AC-G)
- [x] **T7.2** Verify `_bmad/memory/bmad-agent-texas/` 6-file BMB pattern present (already present per slab-2a.4 era; verify only) (AC-G)

### T8 â€” Substrate-as-floor verification (AC-J)

- [x] **T8.1** `git diff master...HEAD app/marcus/orchestrator/dispatch_adapter.py` â€” assert no diff in lines 70-95 absent `substrate-amendment:` trailer (AC-J)

### T9 â€” Composition Smoke at slab-opener (AC-L)

- [x] **T9.1** Author `tests/composition/test_slab_7b_wave_1_opener_composition_smoke.py` (AC-L)
- [x] **T9.2** Capture evidence at `_bmad-output/implementation-artifacts/migration-7b-1-texas-hardening-composition-smoke.md` (AC-L)

### T10 â€” Regression baseline + sandbox-AC validator final pass

- [x] **T10.1** Run regression baseline post-implementation:
```bash
.venv/Scripts/python.exe -m pytest tests/unit/manifest tests/integration/marcus tests/composition tests/parity tests/structural tests/unit/marcus tests/specialists/texas tests/specialists/_scaffold tests/cli tests/unit/models -q --tb=line --ignore=tests/integration/marcus/test_directive_confirm_or_edit_prompt.py
```
Expected: â‰¥696 + ~25-new = ~721 passed; 19 skipped (pre-7b.1 baseline preserved); 0 failed.
- [x] **T10.2** Story-scoped `ruff check` battery â€” clean; full-repo `ruff check .` still reports pre-existing out-of-scope findings
- [x] **T10.3** `lint-imports --config pyproject.toml` â€” 9/9 KEPT (Slab 7a baseline preserved)
- [x] **T10.4** Sandbox-AC validator final pass on this story file â€” PASS

### T11 â€” Codex bmad-code-review handoff

- [ ] **T11.1** Compose code-review handoff prompt for Codex per CLAUDE.md sprint governance NEW CYCLE
- [ ] **T11.2** Codex runs `bmad-code-review` (adversarial + edge-case + acceptance/spec); landings: PASS / PASS-WITH-PATCH / HALT-AND-REMEDIATE
- [ ] **T11.3** If PASS-WITH-PATCH or HALT-AND-REMEDIATE: Claude applies patches in cycle 1 (per 7a.1 precedent), re-runs T10 verifications, re-submits to Codex for confirmation

### T12 â€” Close (AC-M + AC-N)

- [ ] **T12.1** Append Wave-1-close tripwire ledger entry to `sprint-status.yaml::tripwire_events` (AC-M)
- [ ] **T12.2** Flip sprint-status: `migration-7b-1-texas-hardening` â†’ `done`; `migration-epic-slab-7b-specialist-activation-eleven` â†’ `in-progress` (AC-N.1)
- [ ] **T12.3** Update `next-session-start-here.md` â€” Wave-1 parallelism unblock + 7b.2/7b.3 ready (AC-N.2)
- [ ] **T12.4** Confirm Round-(e) E5 prerequisite_stories satisfied (AC-N.3)
- [ ] **T12.5** File any follow-ons surfaced during dev to `_bmad-output/planning-artifacts/deferred-inventory.md` (AC-N.6)
- [ ] **T12.6** Standing-guardrail snapshot recorded in Completion Notes â€” SG-4 first GREEN (AC-N.7)
- [ ] **T12.7** Three-line D12 close stub per Slab 7a precedent: invariant preservation + anti-pattern harvest disposition + migration-guide Â§12 update (if any divergence from spec found during dev)

---

## Dev Notes

### Round-(e) governance summary (binding)

This story's Wave-1 substrate work (T2.1-T2.5) is the **gating precondition for 7b.2 + 7b.3 opens**. Round-(e) E5 (just-ratified) makes this structural: `prerequisite_stories: ["7b-1"]` with `binding=hard` on both stories. The atomic-commit discipline at T2.6 is non-negotiable.

### Class-A rubric-semantics scope

Texas is Class-A â€” rubric-semantics work, not schema-shape, not lane-boundary. Single-gate per `migration-story-governance.json::stories.7b-1`. Dev-agent does not relitigate gate mode; Round-(e) governance freeze is canonical.

### NFR predicates honored

- **NFR-T9** (<30s parity test): annotated per-test `@pytest.mark.timeout(30)`
- **NFR-T10** (<90s fixture-replay): `tests/fixtures/specialist-replay/texas/` cassette use; not load-bearing for this story (Texas is retrieval-orchestration, not API-bound â€” fixture-replay is mostly directive-cassette playback)
- **NFR-T11** (T3 canary live-substrate smoke; operator-gated): out of scope for 7b.1 dev-agent ACs; would surface in 7b.12 closeout if at all
- **NFR-T11a** (T4 cache-hit-rate harness): partially relevant â€” Texas does invoke LLM for evidence-sentence rubric scoring; cache-hit-rate measurement candidate for follow-on if surfaces. Not a 7b.1 close gate.
- **NFR-T11b** (T5 live canary; Class-C/C+/D1 only): NOT applicable to Texas (Class-A)
- **NFR-T12** (parity-test wall-clock <120s aggregate): contributed by `test_texas_activation_contract.py` (~10s budget)
- **NFR-CG14** + **NFR-CG14a** (chain-test PR pre-merge + chain-test base CREATE-task): T2.4 lands the base; existing `tests/composition/test_texas_to_cd_chain.py` is NOT migrated by this story (substrate-frozen-paths posture)
- **NFR-CG16** (BMAD code-review pre-close): T11 task
- **NFR-I9** (sanctum-parity invariant): T4.1 lands the test
- **NFR-I10** (per-specialist activation contract): T4.2 lands the test
- **NFR-I12** (class-shaped template conformance): T2.5 + T4.4 land the validator + first-test conformance
- **NFR-I13** (substrate-frozen-paths-check): T8.1 verification

### Known follow-ons + filings (file at story close to `deferred-inventory.md`)

- **`fr105-tests-parity-per-specialist-subdir-decision`** â€” CLOSE at story T1 (per AC-A; verdict-flat ratified)
- **`tests-composition-test-texas-to-cd-chain-migrate-to-base`** â€” open for follow-on if Codex review surfaces drift; otherwise stand on existing chain test
- **`class-conformance-validator-extend-templates-b-c-cplus-d1-d2`** â€” file as named-but-not-filed follow-on; closure at 7b.4 (Class-B) / 7b.5 (Class-C+) / 7b.6 (Class-C) / 7b.10 (Class-D1) / 7b.11 (Class-D2) per per-class first-landings

### Testing standards summary

- Pytest pattern: per-specialist behavioral tests under `tests/specialists/texas/`; parity tests at `tests/parity/` (FLAT per Errata 4 verdict at AC-A); chain tests at `tests/composition/`
- Fixtures: `tests/fixtures/specialists/texas/` for cassettes/golden envelopes; `tests/fixtures/directive-composer/` for upstream replay
- LLM-live tests: `@pytest.mark.llm_live` (auto-skip on placeholder `OPENAI_API_KEY`); evidence pasted to Completion Notes if exercised on operator machine
- Wall-clock: per-test `@pytest.mark.timeout(30)` for parity; aggregate <120s for full-suite parity

### Anti-pattern catalog citations (per Slab 2a.2 standing protocol)

Watch for anti-patterns A1-A17 + P1-P3 from `docs/dev-guide/specialist-anti-patterns.md`. Particular relevance for 7b.1:
- **A6** (silent-fixture-stub fallback) â€” closing this is the story's primary purpose
- **A9** (epic-doc-vs-shipped-framework drift) â€” node names + paths; if discovered, harvest as anti-pattern entry per Slab 2a.2 Â§D12 precedent
- **P1** (substrate-as-floor violation) â€” AC-J binding

---

### Project Structure Notes

- `app/specialists/texas/` â€” already populated at slab-2a.4 era; this story ADVANCES `_act.py` body, does NOT introduce new top-level files in this dir
- `_bmad/memory/bmad-agent-texas/` â€” already populated with 6-file BMB pattern + extras (CLONE-FORK-NOTICE.md + 4 dirs); this story VERIFIES, does NOT create
- `skills/bmad-agent-texas/` â€” already populated; this story may need to verify SKILL.md frontmatter is minimal per FR101 R1-restated contract â€” fix if drifted
- `tests/parity/_sanctum_parity_base.py` â€” NEW (CREATE-task #2)
- `tests/parity/test_skill_md_sanctum_alignment.py` â€” NEW (per FR101)
- `tests/parity/test_texas_activation_contract.py` â€” NEW (FR105; flat layout per Errata 4)
- `tests/parity/test_trial_475_texas_hardening_regression.py` â€” NEW (AC-K)
- `tests/parity/README.md` â€” augmented with Â§"FR105 + Errata 4 layout decision" (CREATE-task #1)
- `tests/composition/_chain_test_base.py` â€” NEW (CREATE-task #3)
- `tests/composition/test_slab_7b_wave_1_opener_composition_smoke.py` â€” NEW (AC-L)
- `tests/specialists/texas/test_texas_*.py` â€” NEW (4 behavioral tests per T5.1-T5.4)
- `scripts/utilities/validate_parity_test_class_conformance.py` â€” NEW (CREATE-task #4)
- `_bmad-output/implementation-artifacts/migration-7b-1-texas-hardening-composition-smoke.md` â€” NEW evidence file at close (AC-L)

### Detected conflicts or variances

- **Errata 4 layout drift**: PRD draft cited `tests/parity/per_specialist/test_<specialist>_activation_contract.py` (subdir convention). Reality: `tests/parity/` ships flat. Resolution: AC-A ratifies flat; spec yields to code per DR-1.
- **PRD R1-restated FR101 contract** vs original FR101 prose: the BMB sanctum alignment checklist (FR108) is canonical. If FR101 prose drifts, the checklist is authoritative â€” amend FR101 at this story's planning artifact rather than re-litigating PRD.

---

## References

- **Round-(e) governance JSON (just-ratified)**: [`docs/dev-guide/migration-story-governance.json`](../../docs/dev-guide/migration-story-governance.json) Â§`stories.7b-1`
- **Epic + story-level scope (R(a)-R(d) ratified)**: [`_bmad-output/planning-artifacts/epics-slab-7b-specialist-activation-eleven.md`](../planning-artifacts/epics-slab-7b-specialist-activation-eleven.md) Â§Story 7b.1 (lines 427â€“483)
- **PRD FR89 + errata addendum**: [`_bmad-output/planning-artifacts/prd-slab-7b-specialist-activation-eleven.md`](../planning-artifacts/prd-slab-7b-specialist-activation-eleven.md) Â§FR89 + Â§Errata 1-4
- **BMB sanctum alignment checklist (FR108; canonical FR101 authority)**: [`docs/dev-guide/bmb-sanctum-alignment-checklist.md`](../../docs/dev-guide/bmb-sanctum-alignment-checklist.md)
- **Sanctum exception categories (FR109 closed allowlist)**: [`docs/dev-guide/sanctum-exception-categories.json`](../../docs/dev-guide/sanctum-exception-categories.json)
- **Specialist anti-patterns (A1-A17 + P1-P3)**: [`docs/dev-guide/specialist-anti-patterns.md`](../../docs/dev-guide/specialist-anti-patterns.md)
- **Specialist migration template (R1-R14)**: [`docs/dev-guide/specialist-migration-template.md`](../../docs/dev-guide/specialist-migration-template.md)
- **Slab 2a.2 precedent (Class-A nearest analog; 9-node scaffold + AC-B 150-LOC + sanctum cold-read)**: [`migration-2a-2-irene-pass-2-scaffold-migration.md`](migration-2a-2-irene-pass-2-scaffold-migration.md)
- **Slab 7a 7a.1 NEW CYCLE precedent (directive-composer upstream substrate)**: [`migration-7a-1-directive-composer.md`](migration-7a-1-directive-composer.md)
- **Slab 7a 7a.5 NEW CYCLE precedent (latest Claude-authored single-gate)**: [`migration-7a-5-conversation-persistence-specialist-summary-writer.md`](migration-7a-5-conversation-persistence-specialist-summary-writer.md)
- **Sandbox-AC inventory (FR107)**: [`docs/dev-guide/migration-ac-sandbox-inventory.json`](../../docs/dev-guide/migration-ac-sandbox-inventory.json)
- **Substrate-frozen-paths (FR108-derived)**: [`state/config/substrate-frozen-paths.yaml`](../../state/config/substrate-frozen-paths.yaml)
- **Composition Spec (SG-3)**: [`docs/dev-guide/composition-specification.md`](../../docs/dev-guide/composition-specification.md)
- **Sprint status (authority for status flips)**: [`sprint-status.yaml`](sprint-status.yaml)
- **Workflow status**: [`bmm-workflow-status.yaml`](bmm-workflow-status.yaml)
- **Deferred inventory**: [`_bmad-output/planning-artifacts/deferred-inventory.md`](../planning-artifacts/deferred-inventory.md)
- **Mapping checklist (33-row; G0 row improvement target for SG-2)**: [`_bmad-output/planning-artifacts/slab-7-legacy-migrated-mapping-checklist.md`](../planning-artifacts/slab-7-legacy-migrated-mapping-checklist.md)
- **CLAUDE.md** (project root) â€” Â§LangChain/LangGraph migration governance + Â§BMAD sprint governance + Â§Pipeline lockstep regime + Â§Deferred-inventory governance

---

## Dev Agent Record

### Agent Model Used

Codex (GPT-5)

### Debug Log References

- 2026-04-29: T1 hard gates PASS: Round-(e) governance pin, Wave 0 artifacts, Slab 7a done, Texas baseline, dispatch signature, flat parity layout, sandbox-AC preflight.
- 2026-04-29: T2 atomic substrate commit landed: `82e5607`.
- 2026-04-29: `_act.py::act` body measured at 106 LOC, below 150 LOC ceiling.
- 2026-04-29: Focused story battery PASS: 50 passed. Broad regression slice PASS: 711 passed / 19 skipped.

### Completion Notes List

- Implemented T1-T10 and moved story to review for Claude T11/T12.
- T2 substrate gate landed atomically in commit `82e5607`, unblocking 7b.2 + 7b.3 opening per Round-(e) E5.
- Texas hardening added six-artifact enforcement, G0 6-dim evidence-sentence rubric logging, word-count floor with `RetrievalScopeError`, and cross-validation hint logging.
- SG-4 first enforcement is green for Texas: minimal SKILL.md frontmatter + six-file BMB sanctum pattern + Class-A activation contract test.
- Substrate-as-floor preserved for this work: no working-tree diff to `app/marcus/orchestrator/dispatch_adapter.py`.
- Full-repo `ruff check .` still has pre-existing out-of-scope findings; required story-scoped ruff is clean.
- T12 closeout draft for Claude: append `wave_1_close` with `fired_verdict: false`, `measured_value.kloc_aggregate: 1.35` (Codex draft estimate before review patches), `per_story.7b-1: 1.35`, `per_story.7b-2: not-yet-evaluated`, `per_story.7b-3: not-yet-evaluated`, `escalation_action_taken: none`, and pivot next-session note to "7b.2 + 7b.3 openable because T2 commit 82e5607 satisfies Round-(e) E5"; `next-session-start-here.md` was not present in this checkout at Codex handoff.

### File List

NEW:
- `_bmad-output/implementation-artifacts/7b-1-codex-self-review-2026-04-29.md`
- `_bmad-output/implementation-artifacts/migration-7b-1-texas-hardening-composition-smoke.md`
- `app/specialists/texas/_act.py`
- `scripts/utilities/validate_parity_test_class_conformance.py`
- `tests/composition/_chain_test_base.py`
- `tests/composition/test_slab_7b_wave_1_opener_composition_smoke.py`
- `tests/parity/README.md`
- `tests/parity/_sanctum_parity_base.py`
- `tests/parity/test_skill_md_sanctum_alignment.py`
- `tests/parity/test_texas_activation_contract.py`
- `tests/parity/test_trial_475_texas_hardening_regression.py`
- `tests/specialists/texas/test_texas_cross_validation_hint_application.py`
- `tests/specialists/texas/test_texas_g0_evidence_sentence_rubric.py`
- `tests/specialists/texas/test_texas_live_retrieval_against_real_directive.py`
- `tests/specialists/texas/test_texas_word_count_belt_and_suspenders.py`

MODIFIED:
- `_bmad-output/implementation-artifacts/migration-7b-1-texas-hardening.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/planning-artifacts/deferred-inventory.md`
- `app/specialists/texas/graph.py`
