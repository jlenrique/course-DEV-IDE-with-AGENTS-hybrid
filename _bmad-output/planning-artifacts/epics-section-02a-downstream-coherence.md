---
stepsCompleted: ["step-01-validate-prerequisites"]
inputDocuments:
  - "_bmad-output/planning-artifacts/phase-b-consensus-2026-05-22-section-02a-downstream-coherence.md"
  - "_bmad-output/planning-artifacts/phase-a-probe-2026-05-22-section-02a-downstream-coherence.md"
  - "_bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md"
  - "_bmad-output/planning-artifacts/epics-langchain-langgraph-migration.md"
  - "CLAUDE.md"
  - "next-session-start-here.md"
  - "_bmad-output/planning-artifacts/deferred-inventory.md"
---

# course-DEV-IDE-with-AGENTS — Epic 34 Breakdown: §02A Downstream-Consumer Schema Coherence

## Overview

This document captures Epic 34 — the focused substrate-coherence Epic that resolves the §02A composer ↔ Texas wrangler ↔ downstream-consumer schema drift surfaced by Trial-3 attempt-2's hard-crash on 2026-05-21 (`BundleDispatchError`, run-id `6a3393f8-...`).

Epic 34 is **single-Epic, Trial-3-blocking**, sequenced before Trial-3 attempt-3 launch from `course-content/courses/tejal-apc-c1-m1-p2-trends/`. Phase A probe (drift inventory D1-D6 + cleanup-class C1) + Phase B party-mode Round 1 (4-voice impasse) + Dr. Quinn synthesis Round 2 (Option 5: "Round-Trip First, Then Harmonize") ratified by operator 2026-05-22.

**Governance:** authored via `bmad-create-epics-and-stories` per CLAUDE.md §BMAD sprint governance rule #1. Sprint Change Proposal authoring (substrate amendment + TW-7c-4 allowlist extension) follows via `bmad-correct-course` in a separate workflow.

## Requirements Inventory

### Functional Requirements

FR-E34-1: §02A composer's `DirectiveSource` field MUST rename `src_id` → `ref_id` (Winston amendment A2 binding; downstream uniqueness invariant rooted in wrangler at `run_wrangler.py:316`).

FR-E34-2: Texas wrangler input validator MUST extend role enum from current 5-role set to 6-role union: `{primary, supporting, ignored, validation, visual-primary, visual-supplementary}` (Winston amendment A1 binding; preserves Stories 27-2/27-3 substrate alongside §02A taxonomy).

FR-E34-3: Texas wrangler input validator MUST accept and handle `excluded_reason` field for sources with `role=ignored`, preserving §02A's 4-value `ExcludedReason` enum: `{git-marker-file, macos-metadata, windows-metadata, llm-classified-out-of-scope}`.

FR-E34-4: Texas wrangler MUST emit `sme_refs[]` ADDITIVELY in `metadata.json` alongside existing `provenance[]` array (Murat amendment M-Murat-3 binding: do NOT remove `provenance`; forensic-trail consumers depend on it).

FR-E34-5: `sme_refs[]` entries MUST match `pre_packet.SourceRef` shape: `{source_id, path, content_digest}`; wrangler computes per-source `content_digest` at extraction time (closes D5/D6 soft-degrade).

FR-E34-6: Cross-field invariants from §02A `directive_model.py:80-106` (`role=ignored` ↔ `excluded_reason` MUST/MUST-NOT rules; `role=supporting` + binary extensions → MUST-NOT `expected_min_words` per Trial-2 anti-pattern guard) MUST migrate into the wrangler validator.

FR-E34-7: `app/marcus/orchestrator/directive_composer.py` (legacy 7a.1-era composer) MUST be deleted; 7 dependent test files MUST be rewired to §02A composer or deleted if they assert dead-code behavior. **Direction-may-flip caveat** per CLAUDE.md §Deferred inventory governance: revalidate at story-authoring time; if a missed consumer surfaces, keep + harmonize instead of delete.

FR-E34-8: J-A1(a) resolution — operator-supplied `run_id` UUID MUST win over §02A composer's internally-generated `uuid4()`. §02A composer accepts a `run_id` parameter; `cli_adapter.compose_and_write` threads the trial CLI's `effective_trial_id` through. Closes the two-UUIDs-in-one-run divergence observed in Trial-3 attempt-2 (stdout `c9f8c16a-...` vs run-dir path `6a3393f8-...`).

FR-E34-9: J-A1(b) resolution — `cli_adapter` MUST append the NFR-X4 `ModelResolutionEntry` from `ChatModelHandle.entry` to the run's resolution trail (audit-trail completion). §02A composer LLM calls become tracked in the run's reproducibility trail.

### NonFunctional Requirements

NFR-E34-1: **Integration-coverage tests MUST be MANDATORY per story** — NOT unit tests with mocks. Real subprocess §02A → wrangler → bundle round-trip against fixture corpus. (Winston BINDING substrate invariant #7; Murat M-Murat-1; non-negotiable per Murat's code-review dissent clause.)

NFR-E34-2: Pydantic-v2 closed-enum discipline preserved both ends. Wrangler role validation stays closed list (grows from 5 → 6 members); no string-comparison drift like `o.role == "primary"` proliferating downstream.

NFR-E34-3: Pydantic-v2 hygiene: `extra="forbid"` + `validate_assignment=True` on every Pydantic model touched per `docs/dev-guide/pydantic-v2-schema-checklist.md`.

NFR-E34-4: LLM-judged role classification NOT destroyed (§02A's `ignored` + `excluded_reason` taxonomy survives Epic as first-class downstream vocabulary). Operators retain visibility into LLM filtering decisions.

NFR-E34-5: Stories 27-2/27-3 substrate NOT destroyed (`validation`, `visual-primary`, `visual-supplementary` roles preserved through the role-vocab union).

NFR-E34-6: `run_id` UUID4-validated tz-aware at every boundary (composer accepts caller-supplied UUID; tz-aware datetime invariant per `app/models/state/_base.py::enforce_tz_aware`).

NFR-E34-7: Round-trip integration test MUST assert against the actual Trial-3 attempt-2 forensic directive (sha256 `351a57fbe12aff4a49349c4a646618d92ae38a798ec53eee61668f74f8bbd703`) to prove the exact seam crash that triggered this Epic is closed (Murat M-Murat-5 anticipated amendment).

NFR-E34-8: TW-7c-4 freeze-safety preserved: BOTH predicates honored on any `PERMITTED_PYTHON_DIFFS` allowlist amendment per Murat dual-predicate binding from SCP-2026-05-19. Current predicate structure (post-SCP-2026-05-21 C1b refactor): line-79 `app_scope = sorted(...)` bind + L84 `assert app_scope == []` (filters `app/`-prefixed Python NOT in allowlist) AND line-89 `unexpected = sorted(...)` bind + L96 `assert unexpected == []` (filters all other touched Python excluding `.venv/` and `runs/`). Citation lockstep with SCP-2026-05-22 §4.1 per Murat M-Murat-SCP-2 amendment (prior draft cited stale L65; current discipline names both bind site AND predicate assertion line).

NFR-E34-9: Anti-pattern entries A23 + P5 filed at Epic close in `docs/dev-guide/specialist-anti-patterns.md`:
- **A23:** "Two-source-of-truth vocab fork latent across N-year-old integration boundary."
- **P5:** "Schema-coherence Epic without integration-boundary green test is governance failure."

NFR-E34-10: **Temporary in-tree translator scaffolding** (Quinn synthesis Option 5) MUST carry a delete-at-Epic-close hard AC. Epic's FINAL story removes the translator file; round-trip test (Story 34-1) stays green without it. This is the C1-deletion-class discipline applied to the scaffold itself; distinguishes Option 5 from Murat's permanent-adapter Option 3.

NFR-E34-11: NEW CYCLE single-Codex discipline preserved (Claude pre-author → Codex T1-T10 → Claude T11) per CLAUDE.md §Cleanup-arc execution mode reservation. Each story's spec lands as `_bmad-output/implementation-artifacts/migration-34-<key>.md` + `codex-dev-prompt-34-<key>.md`.

NFR-E34-12: Sandbox-AC discipline preserved per CLAUDE.md §LangChain/LangGraph migration — sandbox-AC + gate-mode governance. Every dev-agent AC block avoids forbidden operator-only CLIs; live-service evidence is operator-gated and pastes into Completion Notes.

NFR-E34-13: Each story spec MUST run `python scripts/utilities/validate_migration_story_sandbox_acs.py <story-file>` at `ready-for-dev` finalization AND at `bmad-dev-story` open per CLAUDE.md governance enforcement.

### Additional Requirements

Architecture-derived (Phase A surface inventory):

- D1/D2/D3 hard-crash boundary substrate change site: `skills/bmad-agent-texas/scripts/run_wrangler.py` lines 280-394 (input validator) and 1660-1738 (result.yaml writer)
- D5/D6 metadata.json shape boundary: `run_wrangler.py` lines 1240-1266 (metadata writer) ↔ `app/marcus/intake/pre_packet.py` lines 175-207 (sme_refs consumer)
- §02A composer baseline: `app/composers/section_02a/directive_model.py` lines 36-128; `composer.py`; `cli_adapter.py`
- C1 cleanup target: `app/marcus/orchestrator/directive_composer.py` (entire file; 270 LOC; runtime-dead post-§02A wiring per SCP-2026-05-21-trial3-wiring)
- C1 test surface to rewire/delete: `tests/unit/marcus/orchestrator/test_directive_composer_*.py`, `tests/parity/test_trial_475_*.py`, `tests/specialists/texas/test_texas_live_retrieval_against_real_directive.py`, `tests/composition/test_texas_to_cd_chain.py`, `tests/composition/test_slab_7b_wave_1_opener_composition_smoke.py`
- Integration test landing site (NEW): `tests/integration/test_section_02a_to_wrangler_subprocess_roundtrip.py`
- Trial-3 forensic anchor (NFR-E34-7 assertion target): `state/config/runs/6a3393f8-f369-4a30-b7c1-b50c60c1d1a2/directive.yaml` (gitignored; sha256 `351a57fbe12aff4a49349c4a646618d92ae38a798ec53eee61668f74f8bbd703`)
- Temporary in-tree translator landing site (Quinn Option 5 scaffolding): `app/composers/section_02a/_wrangler_translator.py` (NEW; deleted at Epic's final story)
- TW-7c-4 allowlist file: `pyproject.toml::PERMITTED_PYTHON_DIFFS` + `_ALLOWED_MODIFIED_PATHS_UNDER_TESTS`
- Migration sandbox-AC inventory: `docs/dev-guide/migration-ac-sandbox-inventory.json`
- Pipeline-manifest lockstep: `state/config/pipeline-manifest.yaml::block_mode_trigger_paths` (likely fires on `app/composers/section_02a/` touches per Epic 33 Standing Regime)

### UX Design Requirements

Not applicable. Epic 34 is a backend substrate-coherence Epic; no operator-facing UI changes. Trial-3 G0 verb-set + verb glossary remain unchanged (deferred to post-Trial-3 docs-cleanup batch).

### FR Coverage Map

| Requirement | Covered by Story | Notes |
|---|---|---|
| FR-E34-1 (`src_id` → `ref_id`) | Story 34-3 | Substrate-before-cosmetic order: lands AFTER role-vocab union |
| FR-E34-2 (6-role union) | Story 34-2 | Substrate change; first harmonization story |
| FR-E34-3 (`excluded_reason` handling) | Story 34-2 | Folded with FR-E34-2 (same wrangler validator surface) |
| FR-E34-4 (`sme_refs` additive) | Story 34-4 | metadata.json shape; separate file region from validator |
| FR-E34-5 (`SourceRef` shape match) | Story 34-4 | Folded with FR-E34-4 |
| FR-E34-6 (cross-field invariants) | Story 34-2 | Folded with FR-E34-2 (wrangler validator gets §02A's cross-field rules) |
| FR-E34-7 (C1 legacy composer delete) | Story 34-6 | Penultimate story; before translator-deletion |
| FR-E34-8 (J-A1(a) run_id thread-through) | Story 34-3 | Folded with FR-E34-1 (cli_adapter touch surface overlap) |
| FR-E34-9 (J-A1(b) trail append) | Story 34-3 | Folded with FR-E34-1/8 (cli_adapter touch surface overlap) |
| NFR-E34-1, 7 (integration test) | Story 34-1 | The round-trip test IS Story 34-1 |
| NFR-E34-10 (translator deletion) | Story 34-7 | Final story; hard AC removes scaffolding |
| NFR-E34-9 (A23 + P5 anti-pattern entries) | Story 34-7 | Filed at Epic close alongside translator deletion |
| NFR-E34-8 (TW-7c-4 dual-predicate) | All stories | Every story honors the allowlist discipline at SCP authoring |
| NFR-E34-2, 3, 4, 5, 6, 11, 12, 13 | All stories | Cross-cutting governance; satisfied per-story |

## Epic List

**Epic 34: §02A Downstream-Consumer Schema Coherence** (Trial-3-blocking; this Epic is the entire scope of this artifact)

This document contains exactly one Epic. The deferred-inventory entry `section-02a-downstream-consumer-compatibility-systemic-drift` closes when Epic 34 closes.

---

## Epic 34: §02A Downstream-Consumer Schema Coherence

**Epic Goal:** Resolve the schema-drift between the §02A composer (Story 7c.3a deliverable) and the Texas wrangler input/output + downstream consumers (Stories 7b.1 substrate + Marcus intake pre_packet) so that Trial-3 attempt-3 launches cleanly on canonical contract. Substrate harmonization sequenced behind a load-bearing integration-boundary green test (Quinn synthesis Option 5: "Round-Trip First, Then Harmonize") that gates every harmonization story.

**Trial-3-PASS gate (per John PM verdict, Phase B consensus):**
1. D1+D2+D3 resolved (wrangler accepts `ref_id` field name + 6-role union + `excluded_reason` for `ignored` rows)
2. Story 34-1 round-trip test green, asserting against forensic directive sha256 `351a57f...`
3. §02A composer 12-test suite + M-A1 wiring-contract 4-test suite stay GREEN unchanged
4. `bmad-code-review` + Murat-tier review GREEN on each story
5. TW-7c-4 freeze preserved (both predicates)

**Estimated scope (Amelia forecast + Quinn synthesis adjustments):** 7 stories, ~26-32 pts. 2-3 sessions to Trial-3 attempt-3 launch.

**Risk-acknowledgment notes (Quinn-named at ratification):**
- Translator scope creep → permanent Option-3 adapter by accident. **Mitigation:** delete-translator final-story AC filed AT EPIC AUTHORING (Story 34-7 below).
- Trial-3 attempt-3 slip ~0.5-1 session vs original 2-session forecast. Acceptable.
- Round-trip test fixture mock-surface vacuity. **Mitigation:** M-Murat-4-equivalent audit at Story 34-1 code review.

### Story 34-1: Integration round-trip test + temporary in-tree translator (RED→GREEN)

As the orchestrator (Claude, on behalf of operator),
I want a real subprocess-level §02A → Texas wrangler round-trip test landed FIRST,
So that every subsequent harmonization story moves canonical contract with a green integration ratchet underneath it (Quinn synthesis Option 5; Murat M-Murat-1 binding; closes the "tested module, untested integration" anti-pattern that has fired twice in this trial-launch arc).

**Estimated:** 5 pts. Gate-mode: dual-gate (substrate-touching; introduces new test surface + temporary in-tree translator scaffold). R-tier: R2. Lookahead-tier: Tier 2.

**Acceptance Criteria:**

**AC-34-1-A** (test landing — Story-34-1-substrate-only assertions):
**Given** the §02A composer produces directives via `app/composers/section_02a/composer.compose()` and the Texas wrangler validates input via `skills/bmad-agent-texas/scripts/run_wrangler.py` lines 280-394
**When** I author `tests/integration/test_section_02a_to_wrangler_subprocess_roundtrip.py`
**Then** the test composes a §02A `Directive` via the actual composer entry point (LLM call mocked with deterministic fixture corpus is acceptable; the composer-to-wrangler boundary MUST be real),
**And** writes the directive YAML to a real `tmp_path/directive.yaml`,
**And** invokes `run_wrangler.py` as a REAL subprocess (NOT in-process import) via `subprocess.run([sys.executable, "skills/bmad-agent-texas/scripts/run_wrangler.py", "--directive", str(directive_yaml), "--bundle-dir", str(bundle_dir), "--json"], capture_output=True, text=True, check=False)`,
**And** asserts `result.returncode == 0`,
**And** asserts `len(result.yaml::materials) >= 1` BEFORE asserting per-row shape (Murat new-A9-surface mitigation: prevents vacuous-pass on empty-materials case),
**And** asserts at least one row with `role=primary` carrying `word_count` + `content_path` exists in `result.yaml::materials[]`.

**Scope discipline (post-Round-2 amendment 2026-05-22; Codex T1 surface):** Story 34-1 SHALL NOT assert `metadata.json::sme_refs[]` shape here — Story 34-4 owns wrangler `sme_refs[]` emission, and a translator that only changes directive INPUT shape cannot make the wrangler emit a new metadata.json OUTPUT key. The sme_refs forward-contract assertion is moved to Story 34-4 AC-34-4-A as a "test extension" deliverable (Story 34-4 EXTENDS Story 34-1's round-trip test to add the new assertion in lockstep with the new emission). This honors Quinn-synthesis Option 5's "one drift dimension per story" sequencing.

**AC-34-1-B** (forensic-anchor assertion — Murat M-Murat-5):
**Given** the Trial-3 attempt-2 forensic directive at `state/config/runs/6a3393f8-f369-4a30-b7c1-b50c60c1d1a2/directive.yaml` (sha256 `351a57fbe12aff4a49349c4a646618d92ae38a798ec53eee61668f74f8bbd703`; gitignored — fixture-copy MUST land under `tests/fixtures/integration/section_02a/`)
**When** the same round-trip test feeds this exact forensic directive to the wrangler subprocess
**Then** the test asserts `result.returncode == 0` (proving the exact seam crash that triggered this Epic is closed by translator + harmonization).

**AC-34-1-C** (temporary translator scaffolding):
**Given** Story 34-2/34-3/34-4 substrate harmonization has not yet landed
**When** the test runs at Story 34-1 close
**Then** a temporary in-tree translator at `app/composers/section_02a/_wrangler_translator.py` (NEW file) maps §02A's `Directive` output → wrangler-acceptable shape (renames `src_id` → `ref_id`; maps `supporting` → `supplementary`; filters out `ignored` rows OR maps with a wrangler-acceptable role surrogate),
**And** the translator carries a top-of-file docstring marker `# DELETE-AT-EPIC-34-CLOSE — SCAFFOLDING` plus a `__epic_34_scaffolding__ = True` module-level constant for grep-based deletion verification,
**And** the round-trip test imports + invokes the translator at directive-write time.

**AC-34-1-D** (mock-surface audit — M-Murat-4 equivalent):
**Given** the LLM call inside the §02A composer is mocked in this integration test
**When** the test is reviewed at T11 / G6 code-review
**Then** every mock the test uses MUST be listed in test docstring with the rationale "this mock does NOT bypass the §02A → wrangler boundary; only the upstream LLM call is bounded for determinism."

**AC-34-1-E** (verification):
**Given** Story 34-1 close
**When** the operator runs `.\.venv\Scripts\python.exe -m pytest tests/integration/test_section_02a_to_wrangler_subprocess_roundtrip.py -v`
**Then** all assertions pass; exit 0; test reports >=3 assertion lines (one for AC-A round-trip; one for AC-B forensic-anchor; one for AC-C translator-invocation).

**AC-34-1-F** (sandbox-AC governance — operator-gated, separate AC block per CLAUDE.md sandbox-AC discipline):
**Given** AC-A through AC-E are dev-agent verifiable
**When** operator runs the live-LLM variant of Story 34-1 against the real Tejal corpus
**Then** operator pastes the live-LLM evidence block into Completion Notes per CLAUDE.md §LangChain/LangGraph migration sandbox-AC discipline. (Dev-agent does NOT exercise live LLM; only the LLM-mocked path is dev-agent ACed.)

### Story 34-2: Wrangler input validator — 6-role union + excluded_reason + cross-field invariants

As Texas (wrangler-side substrate),
I want my input validator to accept the §02A composer's `supporting` and `ignored` roles alongside my existing `{primary, validation, supplementary, visual-primary, visual-supplementary}` set,
So that the §02A directive shape no longer hard-crashes my validation at D1/D2/D3 (Winston A1 binding: 6-role union, not rename; Story 27-2/27-3 substrate preserved).

**Estimated:** 5 pts. Gate-mode: single-gate (focused substrate edit; same-file boundary; backed by Story 34-1 ratchet). R-tier: R2. Lookahead-tier: Tier 1.

**Acceptance Criteria:**

**AC-34-2-A** (role enum union):
**Given** `skills/bmad-agent-texas/scripts/run_wrangler.py` lines 328-338 currently validates role against the 5-element set
**When** Story 34-2 lands
**Then** the validator MUST accept the 6-element union `{primary, supporting, ignored, validation, supplementary, visual-primary, visual-supplementary}` — extending, not replacing, the existing set,
**And** the closed-list shape is preserved (no string-comparison drift; NFR-E34-2),
**And** any source with `role=ignored` MUST have `excluded_reason` populated with a member of `{git-marker-file, macos-metadata, windows-metadata, llm-classified-out-of-scope}` (FR-E34-3 + FR-E34-6),
**And** any source with `role=primary | supporting | supplementary | visual-*` MUST NOT have `excluded_reason` (FR-E34-6 cross-field invariant migrated from §02A `directive_model.py:90-91`).

**AC-34-2-B** (ignored-row filtering — downstream behavior):
**Given** a directive carries one or more `role=ignored` sources alongside `role=primary | supporting | visual-*` sources
**When** the wrangler proceeds past validation into materialization
**Then** `role=ignored` rows MUST be filtered out before extraction (not propagated into `materials[]`, `provenance[]`, `extracted.md`, or `result.yaml::materials[]`),
**And** an audit-log line MUST be emitted per filtered-out row with the source's `ref_id` + `excluded_reason` + locator.

**AC-34-2-C** (primary-presence invariant preserved):
**Given** the wrangler's existing rule at `run_wrangler.py:389-394` requires at least one `role in {primary, visual-primary}` source
**When** Story 34-2 lands
**Then** the primary-presence rule is unchanged in behavior,
**And** counts `role=primary` from §02A's vocabulary as primary-presence (`primary` is identical between vocabularies after the union),
**And** `role=ignored` rows do NOT satisfy primary-presence (cannot be the only role in a directive).

**AC-34-2-D** (translator shrinkage):
**Given** Story 34-1's `_wrangler_translator.py` previously mapped `supporting → supplementary` and filtered `ignored`
**When** Story 34-2 lands
**Then** the translator's `supporting → supplementary` mapping MUST be deleted (wrangler now accepts `supporting` natively),
**And** the translator's `ignored`-filtering MUST be deleted (wrangler now handles it natively),
**And** the round-trip test from Story 34-1 stays GREEN with the reduced translator.

**AC-34-2-E** (regression sentinel):
**Given** the existing §02A composer 12-test suite + M-A1 wiring-contract 4-test suite
**When** Story 34-2 lands
**Then** ALL 16 upstream tests stay GREEN unchanged,
**And** new wrangler-side tests assert the union + cross-field invariants per Pydantic-v2 closed-enum red-rejection discipline (NFR-E34-3).

**AC-34-2-F** (Story-34-1 ratchet preserved):
**Given** Story 34-1's round-trip test is green
**When** Story 34-2 lands
**Then** Story 34-1's round-trip test MUST remain green (no regression on the integration boundary).

### Story 34-3: §02A `src_id` → `ref_id` rename + J-A1(a)+(b) cli_adapter completion

As the §02A composer (upstream substrate),
I want my `DirectiveSource.src_id` field renamed to `ref_id` to match the wrangler's downstream-rooted identifier vocabulary,
So that the wrangler-side identifier (39 downstream sites; cross-validation hint application; result.yaml materialization) stays stable per Winston A2 binding. Folds in J-A1(a) (operator-supplied run_id wins) and J-A1(b) (cli_adapter appends ModelResolutionEntry to trail).

**Estimated:** 5 pts. Gate-mode: dual-gate (§02A substrate edit + cli_adapter behavior change). R-tier: R2. Lookahead-tier: Tier 2.

**Acceptance Criteria:**

**AC-34-3-A** (§02A field rename):
**Given** `app/composers/section_02a/directive_model.py::DirectiveSource.src_id`
**When** Story 34-3 lands
**Then** the field is renamed to `ref_id`,
**And** all §02A composer internals (`composer.py`, `_prompt.py`, `_cache.py`, `cli_adapter.py`) reference `ref_id` exclusively,
**And** the LLM prompt template at `docs/conversational-gates/section-02a-composer.j2` (if it references the field name) is updated to emit `ref_id`,
**And** Pydantic-v2 hygiene preserved (`extra="forbid"`, `validate_assignment=True`).

**AC-34-3-B** (§02A test suite migration):
**Given** the 12-test §02A composer suite + 4 M-A1 wiring-contract tests reference `src_id`
**When** Story 34-3 lands
**Then** all 16 tests are migrated to `ref_id`,
**And** all 16 tests stay GREEN.

**AC-34-3-C** (J-A1(a) — operator-supplied run_id):
**Given** `Directive.run_id` is currently generated internally as `uuid4()` in §02A composer per [`directive_model.py:114`](../../app/composers/section_02a/directive_model.py)
**When** Story 34-3 lands
**Then** `composer.compose()` accepts a `run_id: UUID` parameter (required; uuid4-validated; tz-naive-equivalent invariant inapplicable since UUID has no tz),
**And** `cli_adapter.compose_and_write()` threads the trial CLI's `effective_trial_id` through as the `run_id` argument,
**And** the §02A composer no longer generates its own UUID,
**And** the trial CLI's `effective_trial_id` matches `Directive.run_id` matches the run-dir path UUID end-to-end (closes the two-UUIDs-in-one-run divergence per J-A1(a) deferred-inventory entry).

**AC-34-3-D** (J-A1(b) — model_resolution_trail append):
**Given** `cli_adapter.compose_and_write` currently calls `make_chat_model("marcus")` which returns `ChatModelHandle(chat, entry)` and discards `.entry`
**When** Story 34-3 lands
**Then** the adapter MUST persist the `entry: ModelResolutionEntry` to the run's audit-trail surface (sidecar JSON in `run_dir/model_resolution_trail.json` per the deferred-inventory entry's resolution-shape note),
**And** the sidecar JSON shape matches NFR-X4 `ModelResolutionEntry` Pydantic model,
**And** a regression test asserts the sidecar lands at the expected path with the expected fields.

**AC-34-3-E** (translator shrinkage — Quinn Option 5 ratchet):
**Given** Story 34-1's translator previously mapped `src_id` → `ref_id`
**When** Story 34-3 lands
**Then** the translator's `src_id → ref_id` mapping MUST be deleted (§02A now emits `ref_id` natively),
**And** Story 34-1's round-trip test stays GREEN with the further-reduced translator.

**AC-34-3-F** (closes deferred-inventory entries):
**Given** deferred-inventory entries `trial-cli-effective-trial-id-vs-section-02a-composer-run-id-divergence` (J-A1(a)) and `trial-cli-model-resolution-trail-not-appended-from-adapter` (J-A1(b))
**When** Story 34-3 lands
**Then** both entries are marked CLOSED in `_bmad-output/planning-artifacts/deferred-inventory.md`,
**And** the close-out cites Story 34-3 commit + commit SHA.

### Story 34-4: Wrangler metadata.json — `sme_refs[]` additive emission

As Texas (wrangler-side metadata writer),
I want to emit `sme_refs[]` in `metadata.json` ADDITIVELY alongside my existing `provenance[]` array, matching `pre_packet.SourceRef` shape `{source_id, path, content_digest}` with per-source `content_digest`,
So that the soft-degrade where `pre_packet._build_sme_refs` falls back to `source_id="unknown"` (D5/D6) is closed without removing the `provenance[]` forensic-trail consumer surface (Murat M-Murat-3 binding).

**Estimated:** 3 pts. Gate-mode: single-gate (focused metadata-writer edit; same-file boundary as Story 34-2; well-scoped). R-tier: R1. Lookahead-tier: Tier 1.

**Acceptance Criteria:**

**AC-34-4-A** (additive sme_refs):
**Given** `skills/bmad-agent-texas/scripts/run_wrangler.py` lines 1240-1266 currently emit `metadata.json` with `{run_id, generated_at, provenance, primary_consumption_path}`
**When** Story 34-4 lands
**Then** the metadata writer ALSO emits `metadata["sme_refs"]: list[dict]` (additive — `provenance` is preserved unchanged per FR-E34-4),
**And** each `sme_refs[]` entry is `{source_id: str, path: str | None, content_digest: str}`,
**And** `source_id` matches the source's `ref_id` (one-to-one mapping; field-name fork D6 closure),
**And** `path` is the source's locator if `provider == "local_file"` else `null`,
**And** `content_digest` is `sha256(extracted-bytes-for-this-source)` (per-source digest, NOT whole-bundle digest).

**AC-34-4-A-EXT** (integration-test extension — INHERITED FROM AC-34-1-A AT 2026-05-22 ROUND-2 AMENDMENT post Codex T1 surface):
**Given** Story 34-1 landed `tests/integration/test_section_02a_to_wrangler_subprocess_roundtrip.py` WITHOUT the `sme_refs[]` assertion (deferred per scope discipline)
**When** Story 34-4 lands
**Then** Story 34-4 MUST EXTEND the round-trip test to add the following assertion block:
- asserts `metadata.json::sme_refs[]` exists with `len(sme_refs) >= 1` BEFORE asserting per-row shape (Murat new-A9-surface mitigation parallel to AC-34-1-A's materials assertion),
- asserts each entry matches `{source_id: str, path: str | None, content_digest: str}` shape,
- asserts `len(sme_refs) == len([m for m in materials if m["role"] in {"primary","supporting","supplementary","visual-primary","visual-supplementary"}])` (i.e., one sme_refs entry per non-ignored material per AC-34-4-D ignored-row exclusion),
- asserts each `sme_refs[i].source_id` equals the corresponding `materials[i].ref_id` (FR-E34-5 one-to-one mapping verification).

This extension is what makes Story 34-4 "ratchet-extending" per Quinn-synthesis Option 5: the integration test grows as substrate harmonizes; the new assertion validates the new substrate behavior in lockstep.

**AC-34-4-B** (pre_packet contract satisfaction):
**Given** `app/marcus/intake/pre_packet.py::_build_sme_refs` reads `metadata["sme_refs"]` with the preferred branch
**When** Story 34-4 lands
**Then** pre_packet's preferred branch MUST fire on a real wrangler-written `metadata.json` (no fallback to `primary_source="unknown"`),
**And** the constructed `SourceRef` carries the wrangler-computed per-source `content_digest` (NOT the pre_packet-fallback whole-`extracted.md` sha256).

**AC-34-4-C** (translator shrinkage):
**Given** Story 34-1's translator did NOT touch metadata.json (D5/D6 was out-of-scope for translator)
**When** Story 34-4 lands
**Then** the round-trip test from Story 34-1 (AC-34-1-A `assert "sme_refs" in metadata`) MUST flip from soft-failing forward-contract to GREEN.

**AC-34-4-D** (ignored-row metadata exclusion):
**Given** Story 34-2 filters `role=ignored` rows out of `materials[]`/`provenance[]`
**When** Story 34-4 lands
**Then** `sme_refs[]` ALSO excludes `role=ignored` rows (consistent with primary/supporting-only audit trail).

### Story 34-5: §02A composer + translator scaffolding sequence-test landed (carrier story)

As the orchestrator,
I want a sequence-test that asserts the §02A→wrangler integration boundary remains GREEN at EACH intermediate state (post-34-1; post-34-2; post-34-3; post-34-4),
So that the Quinn synthesis "continuous green-gate ratchet" property is enforceable at every story close, not just at Epic close.

**Estimated:** 3 pts. Gate-mode: single-gate (test-only addition; no production substrate touched). R-tier: R1. Lookahead-tier: Tier 1.

**Acceptance Criteria:**

**AC-34-5-A** (parametrized translator-state test + production-load-bearing constant):
**Given** the translator at `app/composers/section_02a/_wrangler_translator.py` exposes a documented `TRANSLATOR_ACTIVE_MAPPINGS: frozenset[str]` constant naming which mappings are still active (e.g., `{"role-supporting-to-supplementary"}` post-34-1; empty set post-34-N)
**When** Story 34-5 lands `tests/integration/test_section_02a_translator_shrinkage_sequence.py`
**Then** the test asserts `TRANSLATOR_ACTIVE_MAPPINGS` shrinks monotonically across story landings (the test gets parametrized with the expected state per Story-N close),
**And** the translator's `compose_and_write` (or equivalent production-path invocation function) MUST read `TRANSLATOR_ACTIVE_MAPPINGS` at runtime and skip absent mappings (Murat new-A9-surface-2 mitigation: make the constant load-bearing in production, NOT just test-observable; prevents vacuous-shrinkage-test where the constant could be set to empty without any production-behavior change),
**And** a sibling assertion verifies that the translator's production-path invocation grep-confirms a reference to `TRANSLATOR_ACTIVE_MAPPINGS` (not just import, actual read).

**AC-34-5-B** (Story-34-1 ratchet preserved):
**Given** the round-trip test from Story 34-1
**When** Story 34-5 lands
**Then** Story 34-1's round-trip test MUST remain green (no regression on integration boundary).

**AC-34-5-C** (carrier story discipline):
**Given** Story 34-5 is a carrier story (test-only; no production code)
**When** the dev-agent verifies AC blocks
**Then** every AC is dev-agent-verifiable (`pytest exit 0`; no live-service evidence required).

### Story 34-6: Legacy `directive_composer.py` deletion + 7-file test rewire (C1)

As the orchestrator,
I want the legacy `app/marcus/orchestrator/directive_composer.py` (Story 7a.1-era broken-fallback corpus-scan composer) DELETED and its 7 dependent test files either rewired to the §02A composer or deleted entirely (where they assert dead-code behavior),
So that no future author re-wires the dead-code path through accidental archaeology, and the test suite stops blocking C1 cleanup via test-only imports (Winston BINDING; consensus per all 4 voices; John flagged this for post-Trial-3 but Quinn synthesis Option 5 absorbs the late stages of Epic 34 to land it pre-Trial-3-attempt-3 with stable translator-deleted substrate).

**Estimated:** 5 pts. Gate-mode: dual-gate (production code deletion + test rewire surface). R-tier: R2. Lookahead-tier: Tier 2. **Direction-may-flip caveat:** if Phase A-revisit at story-authoring time reveals a runtime consumer the probe missed, story SHALL flip to "harmonize legacy composer to Option-5 vocab" instead of "delete."

**Acceptance Criteria:**

**AC-34-6-A** (direction revalidation — runs at story-authoring time, NOT story-close):
**Given** the Phase A probe inventoried `app/marcus/orchestrator/directive_composer.py` as runtime-dead post §02A wiring SCP
**When** Story 34-6 is authored (T1 readiness)
**Then** the spec author MUST re-grep for `compose_directive\|materialize_directive\|orchestrator\.directive_composer` across `app/` (NOT tests) and confirm zero runtime callers,
**And** if any runtime caller surfaces, the story flips to "harmonize legacy composer to Option-5 vocab" with a documented amendment block (direction-may-flip per CLAUDE.md §Deferred inventory governance).

**AC-34-6-B** (legacy composer deletion):
**Given** AC-A confirms zero runtime callers
**When** Story 34-6 lands
**Then** `app/marcus/orchestrator/directive_composer.py` MUST be deleted,
**And** any references to it from sibling modules MUST be cleaned up (e.g., `__init__.py` re-exports if any).

**AC-34-6-C** (7-file test rewire / delete):
**Given** 7 test files reference the legacy composer:
- `tests/unit/marcus/orchestrator/test_directive_composer_pure.py`
- `tests/unit/marcus/orchestrator/test_directive_composer_materialization.py`
- `tests/specialists/texas/test_texas_live_retrieval_against_real_directive.py`
- `tests/parity/test_trial_475_texas_hardening_regression.py`
- `tests/parity/test_trial_475_directive_composition_regression.py`
- `tests/composition/test_texas_to_cd_chain.py`
- `tests/composition/test_slab_7b_wave_1_opener_composition_smoke.py`

**When** Story 34-6 lands
**Then** each file is classified per the spec into {REWIRE-TO-§02A | DELETE-DEAD-CODE-ASSERTION | PRESERVE-WITH-NEW-COMPOSER},
**And** the classification rationale per file is documented in the story spec,
**And** the resulting test surface stays GREEN (no skipped tests; no orphaned imports).

**AC-34-6-D** (Story-34-1 ratchet preserved):
**Given** the round-trip test from Story 34-1
**When** Story 34-6 lands
**Then** Story 34-1's round-trip test MUST remain green.

**AC-34-6-E** (Trial-3-PASS gate readiness check):
**Given** Story 34-6 closes
**When** the operator inspects Trial-3 readiness
**Then** D1+D2+D3 are fully resolved, integration test green, all §02A upstream tests green, legacy composer gone, and the only remaining Epic-34 substrate scaffolding is the temporary translator (which Story 34-7 deletes).

### Story 34-7: Temporary translator deletion + A23/P5 anti-pattern entries + Epic close

As the orchestrator,
I want the temporary in-tree translator at `app/composers/section_02a/_wrangler_translator.py` DELETED with the round-trip test (Story 34-1) staying GREEN without it, and the A23 + P5 anti-pattern entries filed at `docs/dev-guide/specialist-anti-patterns.md`,
So that no two-source-of-truth substrate drift survives Epic 34 close (Quinn synthesis Option 5 NFR-E34-10 binding; distinguishes Option 5 from Murat's feared permanent-adapter Option 3).

**Estimated:** 3 pts. Gate-mode: dual-gate (production code deletion + doctrine surface edit). R-tier: R2. Lookahead-tier: Tier 1.

**Acceptance Criteria:**

**AC-34-7-A** (translator deletion):
**Given** Stories 34-2, 34-3, 34-4 have shrunk the translator's `TRANSLATOR_ACTIVE_MAPPINGS` to the empty frozenset
**When** Story 34-7 lands
**Then** the file `app/composers/section_02a/_wrangler_translator.py` MUST be deleted entirely,
**And** `cli_adapter.compose_and_write` no longer imports or invokes the translator,
**And** any test importing the translator is updated to no longer reference it (or deleted).

**AC-34-7-B** (round-trip test stays GREEN without translator):
**Given** Story 34-1's `tests/integration/test_section_02a_to_wrangler_subprocess_roundtrip.py` previously invoked the translator at directive-write time
**When** Story 34-7 lands
**Then** the test's translator-invocation step is removed,
**And** the test runs §02A → wrangler subprocess directly (no translator in the middle),
**And** the test stays GREEN (exit 0; same assertion shape).

**AC-34-7-C** (Trial-3 forensic-anchor assertion stays GREEN):
**Given** Story 34-1 AC-B asserts against the Trial-3 attempt-2 forensic directive (sha256 `351a57f...`)
**When** Story 34-7 lands
**Then** the forensic-anchor assertion ALSO stays GREEN with no translator (since substrate has been harmonized).

**AC-34-7-D** (A23 + P5 anti-pattern entries filed):
**Given** Murat amendment M-Murat-2
**When** Story 34-7 lands
**Then** `docs/dev-guide/specialist-anti-patterns.md` gains two new entries:
- **A23: "Two-source-of-truth vocab fork latent across N-year-old integration boundary."** *Pattern statement: When two modules share a data contract but have never round-tripped through a green test, vocabulary forks accumulate silently and are discovered at first integration attempt; the cost of harmonization grows linearly with the number of downstream consumers minted against either side's vocab.* Sibling-to-A17 (substrate hostile to composition) but distinct: A17 is shape-hostile; A23 is vocab-forked.
- **P5: "Schema-coherence Epic without integration-boundary green test is governance failure."** *Process-tier. Triggers a hard requirement at Epic-author time: any Epic touching a producer-consumer contract MUST include an integration-boundary green test as its first story.*

**AC-34-7-E** (deferred-inventory close-out):
**Given** the deferred-inventory entry `section-02a-downstream-consumer-compatibility-systemic-drift` (CRITICAL Trial-3-blocking)
**When** Story 34-7 lands
**Then** the entry is moved to `_bmad-output/planning-artifacts/deferred-inventory.md §Closed Entries — Archived` with strikethrough + close-marker citing Story 34-7 commit SHA,
**And** the close-out cross-references Epic 34's full story chain.

**AC-34-7-F** (Trial-3 attempt-3 launch readiness):
**Given** all 7 Epic-34 stories have closed
**When** the operator inspects readiness
**Then** the launch command `.\.venv\Scripts\python.exe -m app.marcus.cli trial start --preset production --input course-content/courses/tejal-apc-c1-m1-p2-trends/` MUST be ready to fire (no Epic-34 substrate work remaining); attempt-3 is unblocked.

**AC-34-7-G** (anti-pattern audit — M-Murat-4):
**Given** Murat amendment M-Murat-4 (if party-mode overrides to Option 1, audit vacuous-test surface)
**When** Story 34-7 lands
**Then** since Quinn synthesis ratified Option 5 (not Option 1), M-Murat-4 audit is REFRAMED as: audit every test mocking `run_wrangler` subprocess across the repo, validate each mock is documented per the AC-34-1-D pattern, and file follow-on if any vacuous-test surface persists.

**AC-34-7-H** (forensic-sweep for translator-scaffold residue — Murat SCP-ratification new-A23-adjacent-surface mitigation):
**Given** Story 34-1's translator scaffold carried a `__epic_34_scaffolding__ = True` module-level constant + `# DELETE-AT-EPIC-34-CLOSE — SCAFFOLDING` docstring marker (AC-34-1-C grep-detection hooks)
**When** Story 34-7 closes
**Then** a repo-wide grep MUST return ZERO results for both markers: `grep -rn "__epic_34_scaffolding__" .` returns nothing AND `grep -rn "DELETE-AT-EPIC-34-CLOSE" .` returns nothing,
**And** Story 34-7's commit message includes the grep evidence (`zero hits across N files searched`) as forensic proof of complete scaffold deletion,
**And** if either grep returns >0 hits, Story 34-7 is NOT done — investigate residue, complete deletion, re-run grep.

---

**Confirm the Requirements are complete and correct to [C] continue:**
