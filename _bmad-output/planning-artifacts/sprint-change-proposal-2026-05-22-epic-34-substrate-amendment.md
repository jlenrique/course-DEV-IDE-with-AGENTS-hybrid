# Sprint Change Proposal — Epic 34 §02A Downstream-Consumer Coherence Substrate Amendment

**Authored at:** 2026-05-22 (Phase B Quinn-synthesis ratified verdict; Epic 34 + 7-story decomposition landed at `8ffd99f`)
**Skill:** `bmad-correct-course` (Batch mode; template-of-record = sprint-change-proposal-2026-05-21-trial3-wiring.md)
**Operator strategic approval:** GRANTED 2026-05-22 (Phase B verdict ratified Option 5 "Round-Trip First, Then Harmonize" per Quinn synthesis; impasse-chain governance applied)
**Branch:** `trial/3-2026-05-21` @ `8ffd99f` (working tree clean post-Epic-34-commit; origin synced)
**Scope classification:** **Moderate-to-Major** (substrate-amendment to TW-7c-4 tripwire allowlist across ~9 paths spanning 7 Epic-34 stories + new integration-test path + new translator-scaffold path with sunset-deletion AC)
**Sibling artifacts:**
- `_bmad-output/planning-artifacts/sprint-change-proposal-2026-05-21-trial3-wiring.md` (ratified + executed 2026-05-21; established the §02A composer wiring at G0 — the parent context this Epic builds on)
- `_bmad-output/planning-artifacts/sprint-change-proposal-2026-05-19.md` (ratified 2026-05-19; REMAINS queued for post-Trial-3 dispatch — NOT folded into this SCP)

---

## Section 1: Issue Summary

**Problem statement.** Trial-3 attempt-2 re-launch 2026-05-21T22:00 (post the wiring SCP at `ab5562d`) crashed at the first specialist dispatch with `BundleDispatchError('texas wrangler reported hard error (exit 30); bundle not trusted')` — the §02A composer's output schema diverges from Texas wrangler's input schema along multiple field/enum boundaries. **Second occurrence of "tested module, untested integration" anti-pattern in same trial-launch arc** (the wiring SCP closed the first occurrence; this Epic closes the second).

**Phase A probe** ([`_bmad-output/planning-artifacts/phase-a-probe-2026-05-22-section-02a-downstream-coherence.md`](phase-a-probe-2026-05-22-section-02a-downstream-coherence.md)) inventoried 6 drift items across 10 surfaces:
- **D1-D3 hard-crash:** §02A emits `src_id` (wrangler wants `ref_id`); `role: supporting` (wrangler wants `supplementary`); `role: ignored` (wrangler has no equivalent)
- **D4-D6 soft-degrade:** hardcoded role compare (LOW); `metadata.json` shape mismatch (wrangler writes `provenance`, pre_packet reads `sme_refs`/`primary_source` — neither matches; soft-degrades to `source_id="unknown"`)
- **C1 cleanup:** legacy `app/marcus/orchestrator/directive_composer.py` (Story 7a.1-era; runtime-dead post §02A wiring; 7 test files reference it)

**Surprise finding:** §02A→wrangler integration boundary has been exercised **exactly zero times in any green test** prior to Trial-3 attempt-2. Both directive composers (legacy + §02A) emit `supporting` which the wrangler rejects. The §02A 12-test composer suite mocks the wrangler boundary. The 4 M-A1 wiring-contract tests (landed at C2a in SCP-2026-05-21) mock `compose()` itself. AM-11 launch-permission token tests preflight, NOT specialist dispatch.

**Phase B party-mode verdict** ([`_bmad-output/planning-artifacts/phase-b-consensus-2026-05-22-section-02a-downstream-coherence.md`](phase-b-consensus-2026-05-22-section-02a-downstream-coherence.md)):
- Round 1 closed at impasse: 3 voices APPROVE Option 1 (harmonize-downstream-to-§02A) with amendments; Murat OBJECTED on grounds of zero-evidence integration seam (broad-regression forecast +15 to +25 vs Option 3's −2 to +2)
- Impasse-chain fired per `CLAUDE.md §Party-mode impasse-resolution chain` (ratified 2026-05-19)
- Dr. Quinn synthesis produced **Option 5: "Round-Trip First, Then Harmonize"** — single Epic, integration-test-first sequencing, temporary in-tree translator scaffolding with delete-at-Epic-close hard AC
- Operator ratified Option 5 as Round-2 verdict 2026-05-22

**Epic 34 authored** ([`_bmad-output/planning-artifacts/epics-section-02a-downstream-coherence.md`](epics-section-02a-downstream-coherence.md)) — 9 FRs + 13 NFRs + 7-story decomposition (~29 pts). Committed at `8ffd99f` and pushed.

**SCP trigger.** Epic 34's story dispatch requires extending the TW-7c-4 substrate-freeze allowlist across ~27 paths (6 `app/` paths + 1 non-`app/` Python wrangler + 2 new integration-test paths + 7 existing legacy-composer tests for Story 34-6 rewire/delete + 8 §02A test-surface paths Story 34-3 will migrate for `src_id → ref_id` rename + 2 fixture-dir defensive entries + 1 carry-forward from SCP-2026-05-21). Without this SCP, Story 34-1 dispatch immediately trips the dual-predicate tripwire (line-79 `app_scope` bind + L84 `app_scope == []` predicate for `app/composers/section_02a/_wrangler_translator.py` + line-89 `unexpected` bind + L96 `unexpected == []` predicate for `skills/bmad-agent-texas/scripts/run_wrangler.py` + the new test-paths). Substrate-freeze is preserved for all other paths. (Citation harmonized post-Round-1 Murat M-Murat-SCP-1 amendment: prior draft referenced stale `line-65` from pre-SCP-2026-05-21-C1b structure; replaced with current bind-site + predicate-line pairs.)

**Forensic evidence preserved.**
- Trial-3 attempt-2 run dir: `state/config/runs/6a3393f8-f369-4a30-b7c1-b50c60c1d1a2/{directive.yaml,run.json}` (gitignored; per `next-session-start-here.md` hot-start notes)
- Directive sha256 (NFR-E34-7 forensic-anchor assertion target): `351a57fbe12aff4a49349c4a646618d92ae38a798ec53eee61668f74f8bbd703`
- Reproducible wrangler error: `[run_wrangler] directive error: sources[0] missing required field: ref_id`

**Trigger category (per `bmad-correct-course` checklist 1.2):** Technical limitation discovered during implementation — schema-drift between authored modules at the integration boundary. Sibling-class to the wiring SCP's defect; second occurrence in same arc warrants Epic-scope substrate amendment rather than per-finding patch.

---

## Section 2: Impact Analysis

### Epic impact

**Yes — Epic 34 is born from this work.** This SCP authorizes the substrate-freeze envelope for the entire Epic. No other Epics are scope-affected.

- **Epic 33 (Standing Regime):** UNCHANGED. The seven-component pipeline-lockstep regime continues to apply to Epic 34 stories per `CLAUDE.md §Pipeline lockstep regime`. Pack-version-bump governance (Tier-1/2/3 per `docs/dev-guide/pipeline-manifest-regime.md §Pack Versioning Policy`) applies if any Epic 34 story touches pipeline-manifest trigger paths — Story 34-2 (wrangler validator) does NOT; Story 34-4 (wrangler metadata writer) does NOT; the pack-version-bump is NOT triggered by Epic 34's substrate changes.

- **Epic 15 (Learning) reactivation:** UNAFFECTED. Reactivation trigger remains "post-Trial-3 PASS" per `next-session-start-here.md`. Epic 34 sequence-positions BEFORE Trial-3 attempt-3 launch; closes that path.

- **Marcus-interactive-experience Epic** (post-Trial-3 architecture follow-on per `deferred-inventory.md`): UNAFFECTED. Sequenced strictly after Trial-3 PASS.

- **2026-05-19 SCP (TW-7c-4 broader substrate amendment):** UNAFFECTED. Remains queued for post-Trial-3 dispatch as a separate motion. Epic 34 lands BEFORE the 2026-05-19 SCP; broad-regression baseline at 88 remains the Epic 34 forensic-comparison reference.

### PRD impact

None. Epic 34 is a focused substrate-coherence Epic; no PRD amendments required.

### Architecture impact

**Yes, scoped to the §02A composer ↔ Texas wrangler ↔ pre_packet integration chain.**

- `app/composers/section_02a/` package gains a NEW temporary scaffolding file (`_wrangler_translator.py`) with a delete-at-Epic-close hard AC; field-rename `src_id` → `ref_id` lands at Story 34-3; cross-field invariants migrate to the wrangler at Story 34-2.
- `skills/bmad-agent-texas/scripts/run_wrangler.py` — input validator extends role enum to 6-role union; metadata writer emits `sme_refs[]` additively alongside `provenance[]`.
- `app/marcus/intake/pre_packet.py` — possibly minor touch in Story 34-4 to align with new `sme_refs[]` shape (or no touch if wrangler-side change satisfies pre_packet's existing contract).
- `app/marcus/orchestrator/directive_composer.py` (legacy 7a.1) — DELETED at Story 34-6 (direction-may-flip caveat re-validated at story-authoring time).
- 7 test files referencing the legacy composer — REWIRED to §02A OR DELETED (Story 34-6).
- NEW integration test path: `tests/integration/test_section_02a_to_wrangler_subprocess_roundtrip.py` (Story 34-1) — the load-bearing seam green-gate ratchet.
- NEW translator-shrinkage-sequence test: `tests/integration/test_section_02a_translator_shrinkage_sequence.py` (Story 34-5).
- M5 import-linter contracts — UNCHANGED.
- `state/config/pipeline-manifest.yaml` — UNCHANGED (no pipeline step added/renamed; no new orchestration node).

### UI/UX impact

Trial-3 G0 operator surface UNCHANGED. Verb-set (`[c/e/s/x]`) preserved. The §02A LLM-judged directive's operator-visible shape changes (rich `excluded_reason` for `role=ignored` rows; per-source `expected_min_words` for prose vs binary files) — but the surface mechanic (operator confirms/edits at G0) is identical. The Marcus-interactive-experience gap remains a SEPARATE post-Trial-3 follow-on.

### Other artifacts

- **Deferred-inventory:**
  - `section-02a-downstream-consumer-compatibility-systemic-drift` (CRITICAL Trial-3-blocking; the load-bearing finding) — CLOSES at Story 34-7 per AC-34-7-E
  - `trial-cli-effective-trial-id-vs-section-02a-composer-run-id-divergence` (J-A1(a)) — CLOSES at Story 34-3 per AC-34-3-F
  - `trial-cli-model-resolution-trail-not-appended-from-adapter` (J-A1(b)) — CLOSES at Story 34-3 per AC-34-3-F

- **`docs/dev-guide/specialist-anti-patterns.md`:** Story 34-7 files A23 + P5 entries (Murat M-Murat-2 binding from Phase B consensus).

- **`docs/dev-guide/migration-ac-sandbox-inventory.json`:** UNCHANGED (Epic 34 stories use shipped Python deps + subprocess for verification; no new operator-only CLIs introduced).

- **`docs/dev-guide/migration-story-governance.json`:** Epic 34 stories will be registered with gate-mode designations per CLAUDE.md §Gate-mode governance at story-authoring time (Stories 34-1, 34-3, 34-6, 34-7 = dual-gate; Stories 34-2, 34-4, 34-5 = single-gate).

- **`next-session-start-here.md`:** post-Epic-34 dispatch the "Immediate next action" block updates to reflect Trial-3 attempt-3 launch readiness.

### Trial-3 launch impact

This SCP directly unblocks Epic 34 dispatch, which in turn unblocks Trial-3 attempt-3 re-launch. Post-Epic-34-close, Trial-3 attempt-3 launches against the committed corpus at `7d3fab2` (`course-content/courses/tejal-apc-c1-m1-p2-trends/`) on canonical substrate (no temporary translator; harmonized vocabulary; integration ratchet green) per Story 34-7 AC-F.

### Broad-regression baseline impact

Epic 34 substrate changes land BEFORE the queued SCP-2026-05-19 dispatches. The 88-failure baseline at `_bmad-output/implementation-artifacts/broad-regression-baseline-2026-05-07.md` is the Epic 34 forensic-comparison reference. Murat's Phase B forecast under Option 5: per-story delta closer to `−2 to +2` (Option-3 range) because every harmonization story moves contract with a green integration ratchet underneath it. **Per-story abort tripwire:** broad-regression delta > +10 OR new failure ID not in 88 baseline → revert the story, KEEP all prior Epic 34 commits.

---

## Section 3: Recommended Approach

**Selected path:** **Direct Adjustment with bounded substrate amendment across 7 stories**, per Phase B Quinn-synthesis ratified Option 5. Single SCP authorizes the substrate-freeze envelope for the entire Epic; each story dispatch operates within the envelope without re-amending allowlist mid-Epic.

**Rejected alternatives:**
- **Per-story SCPs (one amendment per story):** rejected — administrative overhead × 7; loses the coherent-envelope discipline; risks per-story drift in allowlist comment quality. Single SCP with story-attributed comments per allowlist entry is cleaner.
- **Defer Stories 34-5/34-6/34-7 to a separate Epic post-Trial-3:** rejected at Phase B — Quinn synthesis explicitly absorbs the late-stage cleanup (translator deletion + C1 deletion + anti-pattern entries) into Epic 34 to land Trial-3 attempt-3 on FULLY harmonized substrate, not on temporary-adapter substrate.
- **Skip the Epic-34 SCP and rely on per-story bmad-dev-story sandbox-AC discipline:** rejected per `CLAUDE.md §LangChain/LangGraph migration sandbox-AC + gate-mode governance` — the TW-7c-4 freeze is a separate substrate-stability mechanism from the sandbox-AC validator; both must be honored.

**Effort estimate:** Moderate (~2-3 sessions: this SCP authoring + dispatch + Story 34-1 dispatch + Stories 34-2/34-3/34-4 dispatch + Story 34-5 carrier + Stories 34-6/34-7 close). Per Quinn synthesis Risk #2: ~0.5-1 session slip from the original 2-session forecast.

**Risk level:** Low-to-Moderate.
- **Low for the substrate amendment** itself — allowlist extension is bounded; freeze predicate preserved for all other paths.
- **Moderate for the Epic-34 story dispatch chain** — multi-story Epic with cross-story dependencies. Story 34-1's round-trip test acts as continuous green-gate ratchet between each story (Quinn synthesis Option 5 mechanism); abort-and-revert is bounded to the failing story.

**Trade-off accepted:** Trial-3 attempt-3 launch slips by ~0.5-1 session vs the original Phase B 2-session forecast. This is acceptable per Phase B consensus — we've burned more than 0.5 session twice to "tested module, untested integration" already.

---

## Section 4: Detailed Change Proposals

### 4.1 — TW-7c-4 allowlist amendment (substrate-freeze envelope for Epic 34)

**File:** [`tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py`](../../tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py)

**Change:** Extend `PERMITTED_PYTHON_DIFFS` (lines 13-31) with Epic-34-attributed paths:

```python
PERMITTED_PYTHON_DIFFS = {
    *HARNESS_PATHS,
    "scripts/utilities/detect_tw_7c_4_live_dispatch_scope_creep.py",
    "tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py",
    "tests/trial/test_trial3_readiness.py",
    # Trial-3-blocking wiring fix 2026-05-21 (sprint-change-proposal-2026-05-21-trial3-wiring.md):
    # ... [existing 2026-05-21 carryforward comment unchanged] ...
    "app/marcus/cli/trial.py",
    "app/composers/section_02a/cli_adapter.py",
    # SCP 2026-05-21 §7 M-A1: new adapter wiring-contract tests authored as
    # part of C2a; allowlisting per same C1 substrate-amendment scope.
    "tests/marcus_cli/__init__.py",
    "tests/marcus_cli/test_compose_section_02a_directive_adapter.py",
    # Epic 34 §02A downstream-consumer coherence amendment 2026-05-22
    # (sprint-change-proposal-2026-05-22-epic-34-substrate-amendment.md):
    # Phase B Quinn-synthesis ratified Option 5 "Round-Trip First, Then Harmonize."
    # 7-story Epic resolving §02A→wrangler→pre_packet schema drift surfaced by
    # Trial-3 attempt-2 (run-id 6a3393f8-...). Bounded extension across the
    # §02A composer package + Texas wrangler script + Marcus intake + new
    # integration-test paths + temporary translator scaffolding. Freeze
    # predicates (line-79 app_scope + line-89 unexpected) remain enforced
    # for all non-allowlisted paths.
    #
    # Story 34-1 — NEW temporary in-tree translator scaffolding (deleted at
    # Story 34-7 per NFR-E34-10 hard AC); integration-test ship-proof.
    "app/composers/section_02a/_wrangler_translator.py",
    "tests/integration/test_section_02a_to_wrangler_subprocess_roundtrip.py",
    # Story 34-1 fixture-dir defensive (Murat seam): pre-bind in case Codex T1-T9
    # emits any .py under fixture dir (__init__.py / conftest.py). Fixture data
    # files (.yaml/.md/.txt) escape the *.py-scoped predicate at audit-file L64.
    "tests/fixtures/integration/section_02a/__init__.py",
    "tests/fixtures/integration/section_02a/conftest.py",
    # Story 34-2 — wrangler input validator: 6-role union + excluded_reason
    # + cross-field invariants (Winston A1 + Murat M-Murat-3 bindings).
    "skills/bmad-agent-texas/scripts/run_wrangler.py",
    # Story 34-3 — §02A composer src_id → ref_id rename + J-A1(a)/(b)
    # cli_adapter completion (Winston A2 binding).
    "app/composers/section_02a/directive_model.py",
    "app/composers/section_02a/composer.py",
    "app/composers/section_02a/_prompt.py",
    "app/composers/section_02a/_cache.py",
    # Story 34-3 / 34-7 — §02A package __init__.py re-export surface
    # (Winston W-SCP-A1 + Amelia A-A2 2-voice consensus); covers both
    # field-rename ripple AND translator-deletion re-export prune.
    "app/composers/section_02a/__init__.py",
    # Story 34-3 — §02A test surface migration for `src_id → ref_id` rename
    # (Amelia A-A1 grep-verified hits across both composer + gate test trees).
    "tests/composers/section_02a/_helpers.py",
    "tests/composers/section_02a/__init__.py",
    "tests/composers/section_02a/test_composer_cache_key_normalization.py",
    "tests/composers/section_02a/test_composer_classification.py",
    "tests/composers/section_02a/test_composer_directive_model_shape.py",
    "tests/composers/section_02a/test_composer_trial_2_finding_2_regression.py",
    "tests/composers/section_02a/test_composer_utf8_write.py",
    "tests/gates/section_02a/_helpers.py",
    "tests/gates/section_02a/test_g0_poll_surface_field_level_edit.py",
    # Story 34-4 — wrangler metadata.json sme_refs additive emission;
    # pre_packet possibly minor touch (consumer side).
    "app/marcus/intake/pre_packet.py",
    # Story 34-5 — translator-shrinkage sequence test (carrier story).
    "tests/integration/test_section_02a_translator_shrinkage_sequence.py",
    # Story 34-6 — legacy directive_composer.py DELETION; 7 test files
    # rewired or deleted (existing tests; deletion still counts as
    # `git diff` touch for the line-79/L84 + line-89/L96 predicates).
    "app/marcus/orchestrator/directive_composer.py",
    "tests/unit/marcus/orchestrator/test_directive_composer_pure.py",
    "tests/unit/marcus/orchestrator/test_directive_composer_materialization.py",
    "tests/specialists/texas/test_texas_live_retrieval_against_real_directive.py",
    "tests/parity/test_trial_475_texas_hardening_regression.py",
    "tests/parity/test_trial_475_directive_composition_regression.py",
    "tests/composition/test_texas_to_cd_chain.py",
    "tests/composition/test_slab_7b_wave_1_opener_composition_smoke.py",
}
```

**Rationale.** 27 new path entries (post-Round-1 amendment fold; original draft was 16 + 11 ratified additions from Round-1 amendments W-SCP-A1 / A-A1 / A-A2 / A-A3 / Murat-fixture-defensive). Composition:
- 6 new `app/` Python paths (subject to line-79 `app_scope` bind / L84 `app_scope == []` predicate): `_wrangler_translator.py`, `directive_model.py`, `composer.py`, `_prompt.py`, `_cache.py`, `__init__.py`, plus `pre_packet.py` + `directive_composer.py` for Stories 34-4 / 34-6
- 1 non-`app/` Python (wrangler; subject to line-89 `unexpected` bind / L96 `unexpected == []` predicate)
- 2 new integration-test paths (Story 34-1 + Story 34-5)
- 2 fixture-dir defensive entries (Murat seam: pre-bind in case Codex emits any `.py` under fixture dir)
- 8 existing §02A test-surface paths for Story 34-3's `src_id → ref_id` migration (Amelia A-A1 grep-verified)
- 7 existing legacy-composer test paths for Story 34-6 rewire/delete

Each path carries an inline story-attribution comment so subsequent auditing can trace which Epic-34 story authorized which path.

**Freeze preservation invariant.** Both predicates remain enforced for ALL paths NOT in `PERMITTED_PYTHON_DIFFS`:
- Line-79 binds `app_scope = sorted(...)`; L84 asserts `app_scope == []` for `app/`-prefixed Python NOT in allowlist
- Line-89 binds `unexpected = sorted(...)`; L96 asserts `unexpected == []` for all other touched Python (excluding `.venv/` and `runs/`) NOT in allowlist

Citation harmonized post-Round-1 Murat M-Murat-SCP-1: cite both bind sites (L79/L89) AND predicate assertions (L84/L96). The prior draft cited the bind-line only ("line-79"/"line-89"); current discipline names both so future audits can trace assertion failure modes precisely.

Epic 34 dispatch operates strictly within the envelope above; any story touching a path outside the envelope must amend the SCP first.

### 4.2 — Story 34-1 author + dispatch (integration ship-proof + translator scaffold)

**Story:** [Epic 34 §"Story 34-1"](epics-section-02a-downstream-coherence.md) — Integration round-trip test + temporary in-tree translator (RED→GREEN).

**Author location:** `_bmad-output/implementation-artifacts/migration-34-1-section-02a-wrangler-integration-roundtrip-test.md` + `_bmad-output/implementation-artifacts/codex-dev-prompt-34-1-section-02a-wrangler-integration-roundtrip-test.md` (NEW CYCLE single-Codex per `CLAUDE.md §NEW CYCLE Codex dev-handoff prompt`).

**Author rigor:** dual-gate (R-tier R2; lookahead-tier 2). Spec MUST pass:
- `python scripts/utilities/validate_lesson_planner_story_governance.py` — N/A (Lesson Planner-specific; Epic 34 is NOT Lesson Planner)
- `python scripts/utilities/validate_migration_story_sandbox_acs.py` — REQUIRED at ready-for-dev finalization AND at `bmad-dev-story` open per CLAUDE.md §LangChain/LangGraph migration governance enforcement

**Dispatch chain:**
1. Claude (this agent) pre-authors spec + codex-dev-prompt
2. Codex T1-T9 implementation + T10 self-review
3. Claude T11 `bmad-code-review` + commit + flip done

**Verification gates per Trial-3-PASS gate (Epic 34 header):**
- Story 34-1 round-trip test PASS (subprocess; forensic-directive assertion green)
- §02A 12-test composer suite stay GREEN unchanged
- M-A1 4-test wiring-contract suite stay GREEN unchanged
- AM-11 launch-permission token 52/52 GREEN
- TW-7c-4 PASS post-allowlist amendment (this SCP §4.1)
- `bmad-code-review` GREEN
- Broad-regression delta within Murat per-story tripwire range (≤ +10; no new failure IDs outside the 88 baseline)

### 4.3 — Stories 34-2 through 34-7 sequencing

**Story landing order (Winston A3 binding: substrate-change before cosmetic):**

| # | Story | Sequence rationale |
|---|---|---|
| 34-1 | Integration round-trip test + translator scaffold | FIRST — establishes the green-gate ratchet (Quinn synthesis Option 5) |
| 34-2 | Wrangler 6-role union + excluded_reason + cross-field invariants | Substrate change — accepts §02A's vocabulary additively |
| 34-3 | §02A `src_id` → `ref_id` rename + J-A1(a)/(b) cli_adapter completion | Cosmetic rename + audit-trail completion; runs after Story 34-2's substrate change |
| 34-4 | Wrangler `metadata.json` additive `sme_refs[]` emission | Closes D5/D6 soft-degrade; consumer-contract satisfaction |
| 34-5 | Translator-shrinkage sequence test | Carrier story — enforces Quinn's monotonic-shrinkage property |
| 34-6 | Legacy `directive_composer.py` deletion + 7-file test rewire | Direction-may-flip caveat re-validated at authoring time |
| 34-7 | Translator deletion + A23/P5 anti-pattern entries + Epic close | Final story — sunset gate; deferred-inventory closure |

Each story spec lands as a paired `migration-34-<key>.md` + `codex-dev-prompt-34-<key>.md` artifact. Pre-author by Claude; Codex T1-T10; Claude T11.

### 4.4 — Trial-3 attempt-3 re-launch (operator-driven, post-Epic-34-close)

After Story 34-7 closes (Epic 34 close; translator deleted; A23+P5 filed; deferred-inventory `section-02a-downstream-consumer-compatibility-systemic-drift` strikethrough'd):

```
.\.venv\Scripts\python.exe -m app.marcus.cli trial start --preset production --input course-content/courses/tejal-apc-c1-m1-p2-trends/
```

**Expected at G0 (post-Epic-34):** §02A directive on harmonized substrate:
- `ref_id` field present (Story 34-3)
- 6-role union acceptable to wrangler (Story 34-2)
- `excluded_reason` populated for any `ignored` rows (Story 34-2)
- LLM-judged classification (carried from §02A composer; unchanged)

**Expected at first specialist dispatch (post-Epic-34):** Texas wrangler accepts directive WITHOUT TRANSLATOR (translator deleted at Story 34-7); writes bundle with `sme_refs[]` in metadata.json (Story 34-4); pre_packet reads `sme_refs[]` correctly (no fallback to `source_id="unknown"`); Irene Pass-1 receives well-formed envelope; trial proceeds past D1-D6 drift surface.

### 4.5 — Deferred-inventory closure markers (post-Epic-34-close docs commit)

After Story 34-7 close, add closure markers to [`_bmad-output/planning-artifacts/deferred-inventory.md`](deferred-inventory.md):

- `section-02a-downstream-consumer-compatibility-systemic-drift` → strikethrough + `CLOSED 2026-05-2N via Epic 34 (sprint-change-proposal-2026-05-22-epic-34-substrate-amendment.md; stories 34-1..34-7 at commits <range>)`
- `trial-cli-effective-trial-id-vs-section-02a-composer-run-id-divergence` (J-A1(a)) → strikethrough + `CLOSED via Story 34-3`
- `trial-cli-model-resolution-trail-not-appended-from-adapter` (J-A1(b)) → strikethrough + `CLOSED via Story 34-3`

The `marcus-interactive-experience-not-delivered-by-slab-7c` entry remains OPEN (post-Trial-3-PASS reactivation).

---

## Section 5: Implementation Handoff

**Scope classification:** **Moderate-to-Major.** Bounded substrate amendment (16 path entries) + 7-story dispatch chain + new integration test surface + temporary scaffold with sunset-deletion AC. Multi-session execution under NEW CYCLE single-Codex discipline.

**Sequencing (multi-commit; Quinn-synthesis Option 5 ordering):**

1. **Commit C1 — Substrate amendment.** This SCP's §4.1 allowlist extension. Single commit; HEREDOC message referencing this SCP. Verify TW-7c-4 PASSES on clean tree before proceeding.
2. **Commit C2 — Story 34-1 spec author** (`migration-34-1-...md` + `codex-dev-prompt-34-1-...md`). Docs-only. Triggers Codex T1-T10 dispatch.
3. **Codex T1-T10** for Story 34-1 → produces:
   - NEW `app/composers/section_02a/_wrangler_translator.py` (temporary scaffolding)
   - NEW `tests/integration/test_section_02a_to_wrangler_subprocess_roundtrip.py`
   - NEW `tests/fixtures/integration/section_02a/<fixture-files>` (forensic-directive copy + Tejal corpus subset)
4. **Claude T11** — bmad-code-review + commit + flip Story 34-1 done. Verify Story 34-1 round-trip test GREEN.
5. **Stories 34-2 through 34-7** — same NEW CYCLE pattern, story-by-story. Each story close MUST satisfy:
   - Story 34-1 round-trip test stays GREEN (continuous green-gate ratchet)
   - Translator's `TRANSLATOR_ACTIVE_MAPPINGS` shrinks monotonically (Story 34-5 sequence test)
   - §02A 12-test + M-A1 4-test suite stay GREEN
   - bmad-code-review GREEN
6. **Trial-3 attempt-3 re-launch** (operator-driven; post-Epic-34-close) per §4.4 above.
7. **Commit Cn — Deferred-inventory closures + next-session-start-here refresh.** Docs-only.
8. **Push** at multiple checkpoints per `CLAUDE.md §Push cadence policy` (≥2hr interval OR ≥5 commits ahead OR safety-checkpoint trigger).

**Verification gates (binding; A-John-2 split substrate-readiness from launch-readiness):**

*Per-checkpoint gates:*
- After C1 (allowlist amendment): TW-7c-4 PASS on clean tree.
- After EACH story close: Story 34-1 round-trip test PASS + §02A 12-test + M-A1 4-test + AM-11 token GREEN.
- After Story 34-7 close: translator file deleted; round-trip test GREEN without translator; A23+P5 entries filed; Epic 34 closure conditions met.

*Pre-Trial-3 attempt-3 launch — two-checkbox green-light (A-John-2 split):*

**(a) Substrate-readiness gate (Epic 34 header Trial-3-PASS gate, 5 sub-checks):**
1. D1+D2+D3 resolved (Stories 34-2 + 34-3 closed)
2. Story 34-1 round-trip test GREEN (asserts against forensic directive sha256 `351a57f...` per Murat M-Murat-5 / AC-34-1-B)
3. §02A 12-test composer suite + M-A1 4-test wiring-contract suite stay GREEN unchanged
4. `bmad-code-review` GREEN on every Epic-34 story
5. TW-7c-4 PASS (both predicates: line-79 bind / L84 assert + line-89 bind / L96 assert)

**(b) Launch-readiness gate:**
1. Working tree clean (`git status --short` empty)
2. Origin synced (`git log -1 --format='%H' HEAD` == `git log -1 --format='%H' origin/<branch>`)
3. Corpus present at `7d3fab2` reference (`course-content/courses/tejal-apc-c1-m1-p2-trends/` unchanged from Trial-3 attempt-2 anchor)

Operator confirms BOTH checkboxes green before firing the launch command. If either is red, do NOT launch — investigate and remediate first.

**Abort tripwire during execution:** per Murat dual-predicate discipline + Murat tightening + John A-John-1:
- Any test surface that was GREEN at SCP-ratification time drops to FAIL → revert the failing story's commits ONLY (KEEP all prior Epic 34 commits AND the C1 allowlist amendment)
- **Story 34-1 round-trip test stays GREEN → BINDING abort trigger if it drops to RED (Murat tightening: not just a verification gate; if ratchet breaks, abort + revert the failing story is mandatory; the Quinn-synthesis "continuous green-gate ratchet" property is preserved by making ratchet-break an abort trigger, not a flag).**
- Broad-regression delta > +10 OR new failure ID outside the 88 baseline → same revert discipline
- TW-7c-4 trip on any path NOT in PERMITTED_PYTHON_DIFFS → revert the story; investigate allowlist gap; amend SCP if path is legitimately in Epic-34 scope

**Abort-revert exit-state assertion (John A-John-1, BINDING):** post-abort-revert, the Story-34-1 round-trip test MUST stay GREEN on whatever Epic-34 commits remain. **If revert leaves the round-trip test RED, the abort cascades to revert the prior story too — fail-back ratchet, not single-story rollback.** This protects the Quinn-synthesis "continuous green-gate ratchet" property under failure conditions. The fail-back ratchet continues cascading until either (a) the round-trip test is GREEN again, or (b) the cascade reaches C1 itself (in which case the entire Epic 34 dispatch is rolled back and the SCP is re-opened for amendment).

**Handoff recipients:**
- **Orchestrator (this agent / Claude)** executes C1 + pre-authors Story-N specs + Claude T11 commits + ratification updates.
- **Codex** executes Story-N T1-T10 per NEW CYCLE single-Codex per `CLAUDE.md §NEW CYCLE Codex dev-handoff prompt`.
- **Operator** approves this SCP before C1 lands AND drives Trial-3 attempt-3 re-launch interactively post-Epic-34-close.
- **Party-mode (Winston + Amelia + Murat + John)** has ALREADY ratified the underlying Phase B verdict (Quinn synthesis Option 5) — this SCP is the substrate-amendment mechanical implementation of that ratified verdict per CLAUDE.md §BMAD sprint governance §2/§4.

**Success criteria:**
- TW-7c-4 PASS post-amendment AND after EACH story close
- Story 34-1 round-trip test GREEN at landing AND stays GREEN through Story 34-7
- §02A 12-test + M-A1 4-test stay GREEN unchanged
- AM-11 launch-permission token 52/52 GREEN unchanged
- Translator file `app/composers/section_02a/_wrangler_translator.py` exists at Story 34-1 close; DELETED at Story 34-7 close
- A23 + P5 anti-pattern entries filed in `docs/dev-guide/specialist-anti-patterns.md` at Story 34-7 close
- Trial-3 attempt-3 re-launch produces a directive at G0 that round-trips through Texas wrangler WITHOUT translator (substrate harmonized)
- Origin synced; working tree clean post-Epic-34; push-cadence honored throughout
- Deferred-inventory: `section-02a-downstream-consumer-compatibility-systemic-drift` + J-A1(a) + J-A1(b) entries CLOSED with commit-SHA markers

---

## Section 6: Approval + Routing

**Operator approval status:** GRANTED 2026-05-22 (Phase B Quinn-synthesis Option 5 ratified as Round-2 verdict per impasse-chain). The underlying decision is ratified; this SCP authorizes the mechanical substrate-freeze amendment to execute Epic 34 stories within the ratified envelope.

**Party-mode ratification status:** **PRE-RATIFIED via Phase B 4-voice Round 1 + Dr. Quinn synthesis Round 2.** All 4 voices' load-bearing amendments are absorbed into the Epic 34 spec (already committed at `8ffd99f`). This SCP does NOT re-open the Phase B decision; it is the mechanical substrate-envelope amendment that implements the ratified decision.

**Per CLAUDE.md §BMAD sprint governance §2:** "Green-lighting and initial review of completed work must use bmad-party-mode (multi-agent roundtable)." The party-mode ratification already occurred at Phase B; the SCP authorship + execution is direct orchestrator action under the ratified envelope.

**Post-ratification action:**
1. Operator explicitly approves this SCP (per Step 5 of `bmad-correct-course` workflow)
2. Orchestrator commits C1 (allowlist amendment)
3. Orchestrator pre-authors Story 34-1 spec + codex-dev-prompt
4. Operator hand-offs Story 34-1 to Codex for T1-T10
5. Iterate through Stories 34-2 .. 34-7
6. Trial-3 attempt-3 re-launch

---

## Section 7: Round 1 Verdicts + Phase B Amendments (Carry-forward from Quinn synthesis ratification)

**Convened:** 2026-05-22 Phase B Round 1 + Dr. Quinn synthesis Round 2 (impasse-chain fired; resolved at Quinn step; John tiebreaker NOT invoked).

| Voice | Round 1 verdict | Quinn-synthesis-predicted Round 2 verdict | Amendments folded into Epic 34 |
|---|---|---|---|
| 🏗️ Winston (Architect) | APPROVE Option 1 with amendments A1/A2/A3 | APPROVE-with-amendments | A1 (6-role union not rename) + A2 (`src_id` → `ref_id` in §02A) + A3 (substrate-before-cosmetic story order) survive as Epic-34 story-level constraints; 7 BINDING substrate invariants codified as NFR-E34-1..7 |
| 💻 Amelia (Dev) | OBJECT, hybrid Option 1+ | APPROVE-with-amendments | 39-site `ref_id` wrangler-stays-put concern absorbed by Winston A2 (§02A renames, wrangler keeps); 6-story decomposition forecast maps 1:1 onto Epic 34 (+1 carrier story = 7 stories total); Story 34-1 integration ship-proof = her Story 34-6 reordered to first per Quinn |
| 🧪 Murat (TEA) | OBJECT Option 1; APPROVE Option 3 with M-Murat-1..4 | APPROVE-with-amendments | M-Murat-1 satisfied as Story 34-1 (FIRST; integration test against real subprocess + forensic-directive assertion); M-Murat-2 filed at Story 34-7 (A23 + P5 anti-pattern entries); M-Murat-3 (sme_refs additive alongside provenance) = Story 34-4 AC; M-Murat-4 absorbed as carrier discipline; M-Murat-5 anticipated (forensic-directive assertion) codified at NFR-E34-7 + AC-34-1-B |
| 📋 John (PM) | APPROVE Option 1 with scope amendments + pre-stated tiebreaker | APPROVE | Trial-3-PASS gate codified at Epic 34 header (D1+D2+D3 resolved + Story 34-1 green + §02A 12-test + M-A1 4-test + bmad-code-review + TW-7c-4 dual-predicate); D5/D6 IN-EPIC-34 not conditional (Quinn synthesis ratifies fold-in); C1 IN-EPIC-34 (Story 34-6) not deferred-post-Trial-3 (Quinn synthesis sequences cleanup after substrate stable but inside Epic) |

**Round 2 (Quinn synthesis) verdict:** Option 5 "Round-Trip First, Then Harmonize" — single Epic, integration-test-first sequencing, temporary in-tree translator with delete-at-Epic-close hard AC. Predicted 4-of-4 APPROVE/APPROVE-with-amendments per Quinn's voice-reaction model. **Operator ratified 2026-05-22.**

### Quinn-synthesis risks acknowledged at Round-2 ratification (carry-forward)

1. **Translator scope creep** → permanent Option-3 adapter by accident. **Mitigation:** delete-translator final-story AC filed AT EPIC AUTHORING (Story 34-7 AC-34-7-A); not deferred.
2. **Trial-3 attempt-3 slip ~0.5-1 session** vs original 2-session forecast. **Accepted** trade-off — we've burned more than 0.5 session twice to "tested module, untested integration."
3. **Round-trip test fixture mock-surface vacuity** (Tejal corpus + LLM-mocked composer). **Mitigation:** M-Murat-4-equivalent audit at Claude T11 `bmad-code-review` step on Story 34-1 (AC-34-1-D).

### SCP-ratification Round 1 (2026-05-22; 4-of-4 APPROVE-with-amendments; NO impasse)

Convened post-SCP-authoring per CLAUDE.md §BMAD sprint governance §2 (operator directive: "invoke bmad party mode team to give final review and approval by consensus before development of the SCP"). Same 4-voice roster; impasse-chain NOT invoked.

| Voice | Round-1 SCP verdict | Amendments folded |
|---|---|---|
| 🏗️ Winston | APPROVE-with-amendments | W-SCP-A1 (add `app/composers/section_02a/__init__.py`) |
| 💻 Amelia | APPROVE-with-amendments | A-A1 (~8 §02A test-surface paths Story 34-3 migrates) + A-A2 (= W-SCP-A1 convergent) + A-A3 (fixture-dir defensive) |
| 🧪 Murat | APPROVE-with-amendments | M-Murat-SCP-1 (line-number citation L79/L84 + L89/L96) + M-Murat-SCP-2 (Epic NFR-E34-8 lockstep fix) + M-Murat-SCP-3 (T11 bmad-code-review wording) + Story-34-1-ratchet abort-trigger tightening + 2 new A9-surface mitigations (vacuous-pass AC-34-1-A + production-load-bearing AC-34-5-A) + post-Epic forensic sweep for `Epic-34 scaffold marker constant` |
| 📋 John | APPROVE-with-amendments | A-John-1 (abort-revert exit-state assertion; fail-back ratchet) + A-John-2 (split Pre-Trial-3 launch into substrate-readiness + launch-readiness two-checkbox green-light) |

**Ratified amendment set (BINDING; all folded into this SCP body + Epic 34 lockstep):**

1. §4.1 allowlist extended from 16 → 27 paths (11 new entries with story-attribution comments)
2. §1 + §4.1 line-number citations harmonized (L79 + L84 / L89 + L96; stale L65 reference removed)
3. §5 abort tripwire tightened (Story 34-1 ratchet stay-green is BINDING abort trigger)
4. §5 abort-revert exit-state assertion (fail-back ratchet cascade until ratchet-green or C1 revert)
5. §5 Pre-Trial-3 launch split into (a) substrate-readiness + (b) launch-readiness two-checkbox gates
6. SCP-wide "Story 34-1 code review" → "Claude T11 `bmad-code-review` step on Story 34-1"
7. Epic 34 NFR-E34-8 lockstep citation fix (separate file edit)
8. Epic 34 AC-34-1-A vacuous-pass mitigation (`len(materials) >= 1` before row-shape assertion)
9. Epic 34 AC-34-5-A production-load-bearing requirement (`compose_and_write` must read `TRANSLATOR_ACTIVE_MAPPINGS`)
10. Epic 34 Story 34-7 forensic-sweep AC (post-Story-34-7 grep for `Epic-34 scaffold marker constant` returns 0)
11. §8 dispositions resolved (single C1 commit + FULL Story 34-1 codex-dev-prompt)

**Consensus discipline observed:** all 4 amendments are CONVERGENT (no contradictions across voices). Winston caught the `app/`-surface single-path; Amelia caught the test-surface 8-path expansion; Murat caught the citation drift + A9 vigilance; John caught PM-scope + sequencing tightening. Each voice operated strictly within their lane. No re-litigation of Phase B. No impasse.

**Operator approval status:** **GRANTED 2026-05-22** following Round-1 SCP-ratification consensus presentation. C1 execution authorized.

---

## Section 8: Operator dispositions — RESOLVED at Round-1 ratification (2026-05-22)

Both dispositions ratified 4-of-4 by Round-1 SCP-ratification party-mode round:

1. **C1 commit message scope:** **SINGLE commit** covering all 27 allowlist path additions. Rationale (4-voice consensus): the SCP envelope is one ratified decision unit; splitting fragments the audit trail when the 27 paths form ONE Quinn-synthesis Option-5 mechanism. Path-attribution comments inline at §4.1 provide per-story traceability without commit-boundary archaeology. Single HEREDOC commit message citing this SCP. (Murat additional rationale: easier full-Epic revert if abort tripwire fires mid-Epic and substrate-amendment itself needs rollback.)

2. **Story 34-1 codex-dev-prompt content depth:** **FULL spec + assertion-shape detail + fixture-file copy instructions.** Rationale (4-voice consensus): Murat M-Murat-1 binding (real subprocess + real fixture corpus + forensic-anchor sha256 `351a57f...` assertion) requires Codex T1-T9 to land precise assertion shapes; pointer-style risks the "vacuous mock surface" failure mode AC-34-1-D was authored to prevent. Story 34-1 is the load-bearing integration ratchet for all 6 downstream stories — efficiency at the prompt is false economy if the ratchet ships soft. R2/lookahead-tier-2 story-shape per `feedback_velocity_amendments_slab_7c.md` matches FULL-spec prompt depth. (Amelia additional binding: enumerate "mock the LLM, do NOT mock the wrangler subprocess, do NOT mock the directive write path" prescriptively.)

Both dispositions are now BINDING for C1 execution + Story 34-1 codex-dev-prompt authoring.

---

**End of Sprint Change Proposal — Epic 34 §02A Downstream-Consumer Coherence Substrate Amendment.**

Cross-references:
- `_bmad-output/planning-artifacts/phase-a-probe-2026-05-22-section-02a-downstream-coherence.md` (the drift inventory)
- `_bmad-output/planning-artifacts/phase-b-consensus-2026-05-22-section-02a-downstream-coherence.md` (Quinn synthesis + Round-2 ratification record)
- `_bmad-output/planning-artifacts/epics-section-02a-downstream-coherence.md` (Epic 34 + 7-story decomposition; committed at `8ffd99f`)
- `_bmad-output/planning-artifacts/sprint-change-proposal-2026-05-21-trial3-wiring.md` (parent SCP this builds on)
- `_bmad-output/planning-artifacts/sprint-change-proposal-2026-05-19.md` (sibling SCP queued for post-Trial-3 dispatch; NOT folded)
- `_bmad-output/planning-artifacts/deferred-inventory.md §CRITICAL Trial-3-blocking — §02A composer downstream-consumer schema-drift` (the Epic-scope finding entry this SCP enables Epic 34 to close)
- `CLAUDE.md §Party-mode impasse-resolution chain` (the governance under which Phase B Round 1 → Quinn synthesis → Round 2 ratification operated)
- `CLAUDE.md §Pipeline lockstep regime` + `§LangChain/LangGraph migration — sandbox-AC + gate-mode governance` (the standing-regime envelope Epic 34 operates within)
