# Migration Story 7b.2: Quinn-R Hardening — Two-Mode Rubric + G2C Storyboard-Bound + G5 Pre-Composition QA

**Status:** done
**Sprint key:** `migration-7b-2-quinn-r-hardening`
**Epic:** Slab 7b Specialist Body Activation — `epic-slab-7b-specialist-activation-eleven`. **Wave 1 parallel** (Class-A hardening; parallelizable with 7b.1, 7b.3; Claude-authored per NFR-CG17 + D21).
**Pts:** 3 | **Gate:** single (per `docs/dev-guide/migration-story-governance.json::stories.7b-2`; rationale: null; rubric-semantics work) | **K-target:** ~1.3× (target ~25 tests / floor 19; ~2K LOC).
**Author:** **Claude**. **Review:** **Codex** via `bmad-code-review`.
**Round-(e) E5 binding-hard:** `prerequisite_stories: ["7b-1"]`. **Sprint runner MUST NOT open this story until 7b.1 lands T2 atomic CREATE-tasks** (`SanctumParityTestBase` + `_chain_test_base.py` + `validate_parity_test_class_conformance.py` + Errata 4 ratification). T1 readiness verifies all four substrate artifacts present.

---

## Round-(e) Governance Inheritance

Round-(e) freeze landed 2026-04-29 (commit pending). For 7b.2 the load-bearing binding is **E5** — `prerequisite_stories: ["7b-1"]` with binding=hard. The other E1-E7 amendments do not directly load-bear on 7b.2 dev work but signal the Slab 7b structural-enforcement regime.

**T1 readiness verification command:**
```bash
.venv/Scripts/python.exe -c "import json; d = json.load(open('docs/dev-guide/migration-story-governance.json', encoding='utf-8')); assert d['version'] == '2026-04-29-slab7b-twelve-stories'; assert '_staged_pending_party_mode_ratification' not in d['stories']['7b-2']; assert d['stories']['7b-2']['prerequisite_stories'] == ['7b-1']; assert d['stories']['7b-2']['prerequisite_rationale'].startswith('Round-(e) E5'); print('Round-(e) verified PASS for 7b-2')"
```

---

## T1 Readiness Block

### Required-readings cascade (10-reading)

1. **Round-(e) governance JSON** — `docs/dev-guide/migration-story-governance.json` §`stories.7b-2`. Confirm `expected_gate_mode: "single-gate"`, `expected_k_target: 1.3`, `prerequisite_stories: ["7b-1"]`, no `_staged_pending_party_mode_ratification`.
2. **Epic + story-level scope** — [`_bmad-output/planning-artifacts/epics-slab-7b-specialist-activation-eleven.md`](../planning-artifacts/epics-slab-7b-specialist-activation-eleven.md) §Story 7b.2 (lines 487-526). 4 R(a)-R(d) party-mode rounds RATIFIED; 8 amendments folded inline.
3. **PRD §FR90** — [`_bmad-output/planning-artifacts/prd-slab-7b-specialist-activation-eleven.md`](../planning-artifacts/prd-slab-7b-specialist-activation-eleven.md) §FR90: two-mode (pre-composition / post-composition) rubric semantics; G2C storyboard-bound shape (`authorized-storyboard.json` write contract); G5 pre-composition QA body (WPM review + VTT monotonicity + coverage completeness + motion-vs-narration duration coherence + advisory-vs-blocking partition).
4. **7b.1 Wave-1 substrate landed (T2 atomic-commit)** — verify ALL FOUR CREATE-task artifacts present:
   - `tests/parity/_sanctum_parity_base.py` (SanctumParityTestBase class) — Class-A template active per NFR-I12
   - `tests/composition/_chain_test_base.py` (ChainTestBase class)
   - `scripts/utilities/validate_parity_test_class_conformance.py` (Class-A template assertions)
   - `tests/parity/README.md` §"FR105 + Errata 4 layout decision" (verdict-flat ratified)
5. **PRD errata addendum** — same PRD §Errata 1-4. Errata 4 verdict-flat closed at 7b.1 T2; this story's parity test lands flat at `tests/parity/test_quinn_r_activation_contract.py`.
6. **Slab 7a 7a.5 conversation-persistence contract** — [`migration-7a-5-conversation-persistence-specialist-summary-writer.md`](migration-7a-5-conversation-persistence-specialist-summary-writer.md). Verdicts land at `runs/<run_id>/specialist-summaries/quinn-r-<gate>-<timestamp>.md` with 15-25 line envelope per FR-O19.
7. **BMB sanctum alignment checklist (FR108)** — [`docs/dev-guide/bmb-sanctum-alignment-checklist.md`](../../docs/dev-guide/bmb-sanctum-alignment-checklist.md). Canonical authority for FR101 parity-test contract.
8. **Specialist anti-patterns** — [`docs/dev-guide/specialist-anti-patterns.md`](../../docs/dev-guide/specialist-anti-patterns.md) (A1-A17 + P1-P3).
9. **Slab 2a.2 precedent (AC-B 150-LOC ceiling)** — [`migration-2a-2-irene-pass-2-scaffold-migration.md`](migration-2a-2-irene-pass-2-scaffold-migration.md).
10. **CLAUDE.md** — §LangChain/LangGraph migration governance + §BMAD sprint governance.

### Quinn-R current-state probe + drift surfacing

```bash
ls app/specialists/quinn_r/                  # __init__.py expertise/ graph.py model_config.yaml quality_control_dispatch.py sensory_bridges_dispatch.py state.py
ls _bmad/memory/quinn-r-sidecar/             # CLONE-FORK-NOTICE.md access-boundaries.md chronology.md index.md patterns.md (5 files; sidecar variant — DRIFT FROM 6-file BMB target)
ls skills/bmad-agent-quality-reviewer/       # SKILL.md references/ (note: skill-dir name follows legacy `quality-reviewer` convention, NOT `quinn-r`)
ls state/config/schemas/                     # creative-directive.{schema.json,schema.yaml}, gate-result-schema.yaml, suggested-resources.schema.json (NO authorized-storyboard.schema.json — to be created by this story per AC-7b.2-G NFR-CG4 lockstep)
```

Three drifts surface at T1 (analogous to Slab 2a.2 §T1 Readiness three-drift sweep):

**⚠️ Drift #1 — Sanctum dir path convention (BLOCKING for AC-7b.2-J SG-4 first-enforcement on Quinn-R):**

Epic file Story 7b.2 line 509 specifies `_bmad/memory/bmad-agent-quinn-r/` (specialist-name-based path). Reality: only `_bmad/memory/quinn-r-sidecar/` exists (5-file sidecar pattern). Two-axis ambiguity:

- **Axis A (path):** `bmad-agent-quinn-r/` (epic-stated; mirrors Texas `bmad-agent-texas/`) vs `bmad-agent-quality-reviewer/` (mirrors Irene's `bmad-agent-content-creator/` skill-dir-based per Slab 2a.2 drift #3 + project memory `project_corpus_path_convention.md` precedent for skill-dir-name convention).
- **Axis B (pattern):** 6-file BMB (`INDEX.md` / `PERSONA.md` / `CREED.md` / `BOND.md` / `MEMORY.md` / `CAPABILITIES.md` — Texas precedent; Class-A canonical) vs current 5-file sidecar (`index.md` / `access-boundaries.md` / `chronology.md` / `patterns.md` / `CLONE-FORK-NOTICE.md`).

**Resolution at T1 (binding):** **path = `_bmad/memory/bmad-agent-quinn-r/` + pattern = 6-file BMB.** Rationale: epic-file is canonical (Round-(d) ratified close); skill-dir-name vs specialist-name divergence is a Quinn-R-specific quirk where `quality-reviewer` is the legacy skill name and `quinn-r` is the canonical specialist short-name (per `app/manifest/compiler.py::SPECIALIST_ALIASES` carry-forward `quinn-r → quinn_r`). The Cora-sidecar precedent (FR112) uses `bmad-agent-cora/` (specialist-name), supporting this pattern. **CREATE task at T2 below: author 6 BMB files at the new path; OR translate-and-promote from `quinn-r-sidecar/` if content recoverable.** Filed as deferred-inventory follow-on `quinn-r-sanctum-sidecar-to-bmb-migration` — CLOSED at this story T2.

If party-mode disagreement surfaces during dev (e.g., `quality-reviewer/` path is preferred), HALT-AND-SURFACE; resolution requires party-mode + one-line spec amendment at the epic file.

**⚠️ Drift #2 — `authorized-storyboard.schema.json` does not yet exist (AC-7b.2-D requires creation).** This is a CREATE task; lockstep with NFR-CG4 carry-forward. Author at `state/config/schemas/authorized-storyboard.schema.json`; emit script at `scripts/utilities/regenerate_authorized_storyboard_schema.py` (or extend existing schema-regen utility if present). Quinn-R's G2C write-contract (`authorized-storyboard.json` artifact) validates against this schema.

**⚠️ Drift #3 — Existing `quality_control_dispatch.py` + `sensory_bridges_dispatch.py` legacy modules at `app/specialists/quinn_r/`.** These are slab-2a.4 era carry-forwards. Wave-1 hardening should consume them as helpers (NOT replace) per substrate-as-floor invariant. Verify at T1 that the dispatchers are import-stable + offer the contract surfaces Quinn-R `_act` needs.

### Wave 0 + Wave-1-substrate artifact-existence sweep

```bash
# Wave 0 (commit 9ed6fcb)
ls docs/dev-guide/bmb-sanctum-alignment-checklist.md docs/dev-guide/sanctum-exception-categories.json docs/dev-guide/operator-control-parity-template.md docs/dev-guide/migration-ac-sandbox-inventory.json skills/bmad-agent-cora/SKILL.md
ls docs/dev-guide/scaffolds/scaffold-v0.2-D2-pipeline/

# Wave 1 substrate (7b.1 T2 atomic-commit)
ls tests/parity/_sanctum_parity_base.py tests/composition/_chain_test_base.py scripts/utilities/validate_parity_test_class_conformance.py
grep -c "FR105 + Errata 4 layout decision" tests/parity/README.md  # >=1 expected
```

All paths must exist. If any absent → HALT — Wave-0 or 7b.1-T2 substrate is missing; cannot proceed.

### Sandbox-AC validator pre-flight

```bash
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py \
  _bmad-output/implementation-artifacts/migration-7b-2-quinn-r-hardening.md
```
Expect PASS. No forbidden CLI in dev-agent ACs. Quinn-R is rubric-semantics work, not API-bound; no live-API verification needed.

### Standing pre-flight items

1. Severance posture confirmed — hybrid working tree is sole input surface (per memory `project_upstream_severance.md`).
2. `state/config/substrate-frozen-paths.yaml` (FR108-derived) — diffs touching `app/marcus/orchestrator/dispatch_adapter.py:70-95` require `substrate-amendment:` trailer + Marcus-Winston co-sign; this story does NOT touch substrate (FR113 + NFR-I13).
3. `app/manifest/compiler.py::SPECIALIST_ALIASES` confirms `quinn-r → quinn_r` mapping (verified at T1).
4. NFR-T9-T12 wall-clock ceilings hold per `@pytest.mark.timeout` annotation.

---

## Story

As a **migration dev agent**,
I want **Quinn-R's `_act` body hardened to execute two-mode rubric semantics on real upstream artifacts — pre-composition mode at G2C emitting `authorized-storyboard.json` per FR90 write contract; post-composition mode at G3B emitting forensic verdict on assembled artifacts; G5 pre-composition QA body covering five sub-checks (WPM + VTT monotonicity + coverage + motion-vs-narration duration coherence + advisory-vs-blocking partition) — AND I want Quinn-R's sanctum migrated from sidecar (5 files) to canonical 6-file BMB pattern at `_bmad/memory/bmad-agent-quinn-r/` AND I want the `authorized-storyboard.schema.json` lockstep landed**,
So that **(a) Trial-2's G2C/G5/G3B gates carry real Quinn-R quality verdicts (not scaffold-stubbed), (b) operator-actionable findings appear in the per-slide review pack, (c) SG-4 sanctum-alignment is structurally enforced for Quinn-R via the FR101 parity test inheriting `SanctumParityTestBase` from 7b.1 substrate, and (d) the FR90 G2C write-contract is structurally validated against a canonical schema (NFR-CG4 carry-forward)**.

---

## Acceptance Criteria

All ACs are dev-agent-executable (sandbox-AC compliant). No third-party API live-binding required. Live-substrate verification wraps via shipped Python deps with `pytest.skip(...)` when service unreachable.

### AC-7b.2-A — T1 readiness verification + drift resolution

**Given** the Round-(e) governance JSON pin + 7b.1 T2 atomic-commit landed
**And** the three drift items surfaced at T1 (sanctum path/pattern; schema absence; legacy dispatcher modules)
**When** the dev agent runs T1 readiness
**Then** all 10 readings cascade complete; Round-(e) verification command exits 0; Wave-0 + 7b.1-T2 substrate sweep PASS; sandbox-AC validator PASS pre-flight
**And** Drift #1 resolution recorded in Dev Agent Record T1 Readiness block: **path = `_bmad/memory/bmad-agent-quinn-r/`; pattern = 6-file BMB.**
**And** Drift #2 + #3 acknowledged + folded into T2/T3 task plan.

### AC-7b.2-B — Sanctum migration: sidecar (5 files) → BMB (6 files) at canonical path

**Given** Quinn-R's existing sanctum at `_bmad/memory/quinn-r-sidecar/` (5-file sidecar pattern)
**And** Drift #1 resolution at AC-A binding `_bmad/memory/bmad-agent-quinn-r/` + 6-file BMB pattern
**When** the dev agent migrates the sanctum
**Then** `_bmad/memory/bmad-agent-quinn-r/` directory lands with 6 files: `INDEX.md` (essential context loaded on activation) + `PERSONA.md` (full BMB persona) + `CREED.md` (operating principles) + `BOND.md` (operator-specialist relationship) + `MEMORY.md` (cumulative continuity) + `CAPABILITIES.md` (skill inventory) — per Texas precedent + BMB checklist (FR108)
**And** content is translated from `quinn-r-sidecar/` where applicable (chronology, access-boundaries, patterns content folds into MEMORY.md + CAPABILITIES.md as appropriate; specialist invokes `bmad-agent-builder` skill if available, otherwise manual authoring per the BMB checklist worked example)
**And** the legacy `_bmad/memory/quinn-r-sidecar/` directory is preserved unchanged (no deletion in this story; deferred-inventory follow-on `quinn-r-sidecar-cleanup-post-trial-2-validation` filed for cleanup AFTER trial-2 validates no consumer references it)
**And** deferred-inventory follow-on `quinn-r-sanctum-sidecar-to-bmb-migration` → CLOSED at this story T2.

### AC-7b.2-C — Two-mode body shape: pre-composition (G2C) + post-composition (G3B)

**Given** Marcus dispatches Quinn-R at G2C (storyboard-bound; pre-composition) AND at G3B (post-Storyboard-B HIL review; post-composition)
**When** Quinn-R's `_act` body executes
**Then** `app/specialists/quinn_r/_act.py` mode-discriminates on `gate_id` carried in the envelope; pre-composition branch emits `authorized-storyboard.json` per FR90 write contract; post-composition branch produces forensic verdict on assembled artifacts (post-Compositor)
**And** `_act` body length is **≤150 LOC** per AC-B ceiling (Slab 2a.2 precedent MF4); HALT-AND-SURFACE re-scope decision if exceeds
**And** mode-singularity hard-constraint enforced — Quinn-R cannot mis-route (e.g., pre-composition body invoked at G3B raises `ModeMismatchError`, NOT silent fallthrough)
**And** existing helper modules `quality_control_dispatch.py` + `sensory_bridges_dispatch.py` are CONSUMED (NOT replaced) per substrate-as-floor invariant.

### AC-7b.2-D — G2C write contract: `authorized-storyboard.json` + schema lockstep

**Given** the FR90 G2C write contract requires Quinn-R to emit `authorized-storyboard.json` per a structurally validated shape
**When** the dev agent authors the schema (Drift #2 resolution)
**Then** `state/config/schemas/authorized-storyboard.schema.json` lands with JSON Schema (Draft 2020-12) defining the artifact shape: `slides[]` (array; each slide carries `slide_id`, `title`, `narration_pointer`, `motion_pointer`, `quinn_r_verdict: {advisory|blocking|approved}`, `evidence_block`)
**And** Quinn-R's pre-composition `_act` writes `runs/<run_id>/quinn-r/g2c/authorized-storyboard.json` validating against this schema (use `jsonschema` shipped Python dep)
**And** schema-regen lockstep wired (NFR-CG4 carry-forward) — `scripts/utilities/regenerate_authorized_storyboard_schema.py` (or extend existing schema-regen utility if present); emitted JSON validates against shipped schema on every PR.

### AC-7b.2-E — G5 pre-composition QA body: five sub-checks

**Given** Quinn-R running G5 pre-composition QA on real Enrique narration + real Kira motion (post-7b.7 + 7b.8 close — for Wave 1 dev, fixture-replay against cassettes is acceptable; live-substrate smoke pasted to operator Completion Notes if exercised)
**When** the QA body executes
**Then** five sub-checks fire in order:
  1. **WPM review** — words-per-minute against `narration_profile_controls.target_wpm`; raise `WpmThresholdError` if outside tolerance band
  2. **VTT monotonicity** — captions track timestamps strictly increasing; raise `VttMonotonicityError` if regression detected
  3. **Coverage completeness** — every storyboard slide has narration; raise `CoverageGapError` if any slide unmapped
  4. **Motion-vs-narration duration coherence** — per-segment delta within tolerance (e.g., ±10% of declared duration); raise `DurationCoherenceError` if exceeds
  5. **Advisory-vs-blocking partition** — block-mode failures (1-3) vs advisory warnings (4); structured verdict carries both partitions
**And** each sub-check has a parametrized test pin under `tests/specialists/quinn_r/test_quinn_r_g5_*.py` (one file per sub-check OR one parametrized file with five cases — author decides at T4).

### AC-7b.2-F — Verdict landing per 7a.5 conversation-persistence contract

**Given** the Slab 7a 7a.5 conversation-persistence contract — verdicts land at `runs/<run_id>/specialist-summaries/quinn-r-<gate>-<timestamp>.md` with 15-25 line envelope per FR-O19
**When** Quinn-R `_act` completes (G2C, G3B, or G5)
**Then** Quinn-R invokes `app.marcus.orchestrator.specialist_summary_writer.emit_summary(specialist="quinn-r", gate=<gate>, payload=<verdict>)` per the 7a.5 facade
**And** the summary file lands at the canonical path with timestamped filename + 15-25 lines + canonical specialist_id mapping (`quinn-r → quinn_r` per `app/manifest/compiler.py::SPECIALIST_ALIASES`)
**And** SHA256 tamper-evident chain integrity preserved (per 7a.5 contract); `verify_chain(trial_id, runs_root)` PASSES.

### AC-7b.2-G — SG-4 Sanctum Alignment (FR100 + FR101 — first-enforcement on Quinn-R)

**Given** the SG-4 sanctum-alignment requirement (PRD §FR-7b-sanctum FR100-FR103)
**When** the dev agent commits Quinn-R hardening
**Then** `skills/bmad-agent-quality-reviewer/SKILL.md` is verified option-a sanctum-aligned per BMB checklist (FR108):
  - YAML frontmatter MINIMAL — keys `name` + `description` ONLY (per Errata 2 contract); fix if drifted (existing SKILL.md may carry legacy keys)
  - SKILL.md body references `_bmad/memory/bmad-agent-quinn-r/` sanctum dir (NEW canonical path) as activation-time hot-load batch
**And** the new sanctum dir at `_bmad/memory/bmad-agent-quinn-r/` (per AC-B) carries the 6-file BMB pattern
**And** the parity test `tests/parity/test_skill_md_sanctum_alignment.py` (created by 7b.1 per FR101) PASSES for Quinn-R with Class-A template assertions (`SanctumParityTestBase` inherited from 7b.1 substrate; minimal frontmatter; sanctum-path equality; 6-file BMB pattern; Class-A cold-activation smoke)
**And** `bmad-code-review` (T11) confirms `# SG-4 Sanctum Alignment` AC verbatim in this story planning artifact (per FR100).

### AC-7b.2-H — FR105 per-specialist parity test (Quinn-R activation contract)

**Given** the Errata 4 verdict-flat layout ratified at 7b.1 T2
**When** the dev-agent authors Quinn-R's activation-contract test
**Then** `tests/parity/test_quinn_r_activation_contract.py` (flat — NOT under `per_specialist/` subdir) lands
**And** the test class inherits `SanctumParityTestBase` (from 7b.1 substrate) with `class_template_id = "A"` and `specialist_name = "quinn-r"`
**And** the test asserts Class-A rubric-semantics parity:
  - (i) two-mode dispatch (pre/post-composition; mode-singularity)
  - (ii) `authorized-storyboard.json` write-contract structural validity (against schema from AC-D)
  - (iii) G5 five-sub-check structured verdict shape (advisory-vs-blocking partition present)
  - (iv) verdict-landing at canonical 7a.5 summary path
  - (v) cold-activation smoke
**And** `@pytest.mark.timeout(30)` per NFR-T9; contributes to <120s aggregate per NFR-T12
**And** `validate_parity_test_class_conformance.py` (from 7b.1 substrate) PASSES on this test file when run.

### AC-7b.2-I — Sandbox-AC governance (CLAUDE.md + FR107)

**Given** the sandbox-AC inventory governance requirement
**When** `validate_migration_story_sandbox_acs.py` runs on this spec
**Then** PASS (no forbidden CLI in dev-agent ACs)
**And** Quinn-R-specific note: NO sandbox-AC inventory entry needed (rubric-semantics work, not API-bound; distinct from 7b.6/7b.7/7b.8/7b.9 which consume API entries).

### AC-7b.2-J — Substrate-as-floor invariant (FR113 + NFR-I13)

**Given** the substrate-as-floor invariant
**When** the dev-agent's diff is reviewed
**Then** **no diff hunk touches `app/marcus/orchestrator/dispatch_adapter.py:70-95`** absent `substrate-amendment:` trailer + Marcus-Winston co-sign
**And** verification command:
```bash
git diff master...HEAD app/marcus/orchestrator/dispatch_adapter.py | head -30
# Expect: no output OR only outside 70-95 range
```

### AC-7b.2-K — Wave-1 close tripwire ledger (Round-(e) E2 contribution)

**Given** the Round-(e) E2 amendment landed `tripwire_events: []` schema slot at `sprint-status.yaml`
**When** this story closes (post-T11 review)
**Then** the dev-agent appends OR amends the existing `wave_1_close` entry at `sprint-status.yaml::tripwire_events`:
```yaml
tripwire_events:
  - tripwire_id: wave_1_close
    story_owner: <7b-1|7b-2|7b-3 closer-of-record>
    fired_at: <YYYY-MM-DD>
    fired_verdict: <true|false>          # true if K-actual >2.7K LOC across 7b.1+7b.2+7b.3 aggregate
    measured_value:
      kloc_aggregate: <N.NN>
      per_story:
        7b-1: <N.NN>
        7b-2: <N.NN>           # this story's contribution
        7b-3: <N.NN or not-yet-evaluated>
    escalation_action_taken: <none|wave_2_irene_at_upper_band_k_target_only>
    decision_record_link: <links to all three Wave-1 stories' Completion Notes>
```
**And** if `fired_verdict: true`, escalation per Round-(a) Amelia A3: Wave-2a (Story 7b.4 Irene Pass-1) opens at upper-band K-target.

### AC-7b.2-L — Chain test inheriting `ChainTestBase` from 7b.1 substrate

**Given** NFR-CG14 chain-test PR pre-merge requirement + 7b.1's `_chain_test_base.py` substrate
**When** the dev agent authors the Quinn-R chain test
**Then** `tests/composition/test_quinn_r_chain.py` lands inheriting `ChainTestBase` (from 7b.1 substrate)
**And** the test asserts envelope-handoff shape compatibility for upstream (Marcus directive composer) → Quinn-R AND Quinn-R → downstream (Marcus gate-runner)
**And** wall-clock <120s (NFR-CG14a budget; `@pytest.mark.timeout(120)`).

### AC-7b.2-M — Close protocol

**Given** all prior ACs PASS + bmad-code-review (Codex) returns PASS or PASS-WITH-PATCH-applied + regression baseline holds
**When** the story closes
**Then** at close:
  1. **sprint-status.yaml** flip: `migration-7b-2-quinn-r-hardening: in-progress → review → done`
  2. **Wave-1 close tripwire ledger entry** appended/amended per AC-K
  3. **next-session-start-here.md** updated if Wave-1 close is the last of three (7b.1 + 7b.2 + 7b.3 all done): pivot to Wave-2a (7b.4 Irene Pass-1) opening
  4. **Deferred-inventory updates**: `quinn-r-sanctum-sidecar-to-bmb-migration` → CLOSED at T2; `quinn-r-sidecar-cleanup-post-trial-2-validation` filed as named-but-not-filed follow-on
  5. **Standing-guardrail status**: SG-4 second-green (after 7b.1) — Quinn-R sanctum BMB-aligned + parity test passes
  6. **Three-line D12 close stub** per Slab 7a precedent

---

## Tasks / Subtasks

### T1 — T1 readiness verification + drift resolution

- [x] **T1.1** Round-(e) governance JSON verification (1-line Python command)
- [x] **T1.2** Required-readings cascade (10 readings)
- [x] **T1.3** 7b.1 T2 substrate sweep — verify all 4 CREATE-task artifacts present + accessible from this story
- [x] **T1.4** Wave 0 artifact sweep (6 paths)
- [x] **T1.5** Quinn-R current-state probe — surface 3 drift items
- [x] **T1.6** Drift resolution recorded in Dev Agent Record T1 block: path + pattern + schema-create-task + legacy-dispatcher-consume-don't-replace
- [x] **T1.7** Sandbox-AC validator pre-flight (PASS expected)
- [x] **T1.8** Standing pre-flight items

### T2 — Sanctum migration + schema lockstep (CREATE atomicity within this story)

- [x] **T2.1** Author 6 BMB files at `_bmad/memory/bmad-agent-quinn-r/` (INDEX.md / PERSONA.md / CREED.md / BOND.md / MEMORY.md / CAPABILITIES.md). Translate content from `quinn-r-sidecar/` where applicable; author novel content per BMB checklist worked examples
- [x] **T2.2** Author `state/config/schemas/authorized-storyboard.schema.json` (JSON Schema Draft 2020-12)
- [x] **T2.3** Author `scripts/utilities/regenerate_authorized_storyboard_schema.py` (OR extend existing schema-regen utility)
- [x] **T2.4** File `quinn-r-sanctum-sidecar-to-bmb-migration` follow-on as CLOSED at T2 in `_bmad-output/planning-artifacts/deferred-inventory.md`
- [x] **T2.5** File `quinn-r-sidecar-cleanup-post-trial-2-validation` as named-but-not-filed follow-on in deferred-inventory

### T3 — Quinn-R `_act` body hardening (AC-C + AC-D + AC-E + AC-F)

- [x] **T3.1** Replace passthrough/stub body in `app/specialists/quinn_r/_act.py` with two-mode dispatch (pre-composition / post-composition; mode-singularity)
- [x] **T3.2** Implement G2C pre-composition branch — emit `authorized-storyboard.json` per write contract
- [x] **T3.3** Implement G3B post-composition branch — forensic verdict on assembled artifacts
- [x] **T3.4** Implement G5 pre-composition QA body — five sub-checks (WPM, VTT, coverage, duration, advisory-vs-blocking)
- [x] **T3.5** Wire 7a.5 specialist-summary-writer integration (verdict landing)
- [x] **T3.6** Consume `quality_control_dispatch.py` + `sensory_bridges_dispatch.py` as helpers (NOT replace)
- [x] **T3.7** **AC-B 150-LOC ceiling discipline:** `_act` body ≤150 LOC; HALT-AND-SURFACE re-scope if exceeds

### T4 — Parity test + behavioral tests

- [x] **T4.1** Author `tests/parity/test_quinn_r_activation_contract.py` — flat layout; inherits SanctumParityTestBase; Class-A template (AC-H)
- [x] **T4.2** Author `tests/specialists/quinn_r/test_quinn_r_two_mode_dispatch.py` (AC-C)
- [x] **T4.3** Author `tests/specialists/quinn_r/test_quinn_r_g2c_write_contract.py` (AC-D; validates against schema)
- [x] **T4.4** Author `tests/specialists/quinn_r/test_quinn_r_g5_qa_body.py` — parametrized over 5 sub-checks (AC-E)
- [x] **T4.5** Author `tests/specialists/quinn_r/test_quinn_r_g3b_post_composition.py` (AC-C)
- [x] **T4.6** Author `tests/specialists/quinn_r/test_quinn_r_summary_landing.py` (AC-F)
- [x] **T4.7** Author `tests/composition/test_quinn_r_chain.py` — inherits ChainTestBase (AC-L)
- [x] **T4.8** Wall-clock annotations: `@pytest.mark.timeout(30)` on parity test; `@pytest.mark.timeout(120)` on chain test
- [x] **T4.9** `validate_parity_test_class_conformance.py` PASS on new test file

### T5 — SG-4 sanctum alignment verification (AC-G)

- [x] **T5.1** Verify `skills/bmad-agent-quality-reviewer/SKILL.md` YAML frontmatter is minimal — fix if drifted
- [x] **T5.2** Update SKILL.md body to reference `_bmad/memory/bmad-agent-quinn-r/` (new canonical path)
- [x] **T5.3** `tests/parity/test_skill_md_sanctum_alignment.py` (created by 7b.1) PASSES for Quinn-R

### T6 — Substrate-as-floor verification (AC-J)

- [x] **T6.1** `git diff master...HEAD app/marcus/orchestrator/dispatch_adapter.py` — assert no diff in lines 70-95

### T7 — Schema regen lockstep verification

- [x] **T7.1** Run schema-regen utility; assert emitted schema matches shipped + emitted JSON validates against schema

### T8 — Regression baseline + sandbox-AC validator final pass

- [x] **T8.1** Full regression battery (per CLAUDE.md hot-start command). Expected: ≥696 + ~25-new ≈ 721 passed; 19 skipped; 0 failed
- [x] **T8.2** `ruff check .` clean
- [x] **T8.3** `lint-imports.exe` 9/9 KEPT
- [x] **T8.4** Sandbox-AC validator final PASS

### T9 — Codex G6 self-review (NEW CYCLE T10 by Codex)

- [x] **T9.1** Codex authors G6 self-review at `_bmad-output/implementation-artifacts/7b-2-codex-self-review-2026-04-XX.md`
- [x] **T9.2** Status flip `in-progress → review`; hand to Claude

### T10 — Claude bmad-code-review

- [ ] **T10.1** Claude runs `bmad-code-review` (adversarial + edge-case + acceptance/spec) at `_bmad-output/implementation-artifacts/7b-2-code-review-2026-04-XX.md`
- [ ] **T10.2** PASS / PASS-WITH-PATCH / HALT-AND-REMEDIATE; remediation cycle 1 if needed

### T11 — Close (AC-K + AC-M)

- [ ] **T11.1** Append/amend Wave-1-close tripwire ledger entry per AC-K
- [ ] **T11.2** Sprint-status flip `review → done`
- [ ] **T11.3** Update `next-session-start-here.md` if Wave-1 close
- [ ] **T11.4** Deferred-inventory updates per AC-M.4
- [ ] **T11.5** Standing-guardrail status snapshot — SG-4 second-green
- [ ] **T11.6** Three-line D12 close stub
- [ ] **T11.7** Commit + push (Codex T11 → Claude review → Claude commits)

---

## Dev Notes

### Round-(e) E5 prerequisite_stories binding

This story carries `prerequisite_stories: ["7b-1"]` with `binding=hard`. **Sprint runner MUST NOT open this story until 7b.1 lands T2 atomic-commit.** T1.3 verifies all 4 substrate artifacts present.

### Class-A rubric-semantics scope

Quinn-R is Class A — rubric-semantics work, not schema-shape, not lane-boundary. Single-gate per `migration-story-governance.json::stories.7b-2`.

### Sanctum migration (sidecar → BMB) is a CREATE task not a refactor

The legacy sidecar at `_bmad/memory/quinn-r-sidecar/` is preserved (no deletion) until trial-2 validates no consumer references it. Two-source state during the transition is acceptable; the new `_bmad/memory/bmad-agent-quinn-r/` is the canonical source going forward.

### NFR predicates honored

NFR-T9 / T10 / T11 / T11a / T11b / T12 — `@pytest.mark.timeout` annotations.
NFR-CG14 + NFR-CG14a — chain test inheriting ChainTestBase from 7b.1 substrate.
NFR-CG16 — bmad-code-review pre-close (T10).
NFR-I9 + NFR-I10 + NFR-I12 — parity test + activation contract + class-shaped template (Class-A).
NFR-I13 — substrate-frozen-paths-check (T6).
NFR-CG4 — schema lockstep on `authorized-storyboard.schema.json`.

### Known follow-ons

- **`quinn-r-sanctum-sidecar-to-bmb-migration`** — CLOSE at T2
- **`quinn-r-sidecar-cleanup-post-trial-2-validation`** — file as named-but-not-filed follow-on; close after trial-2 confirms no consumer references the legacy sidecar
- **`authorized-storyboard-schema-evolution`** — file as named-but-not-filed if downstream stories surface schema-extension needs

### Anti-pattern catalog citations

- **A6** (silent-fixture-stub fallback) — closing for Quinn-R G2C/G5/G3B
- **A9** (epic-doc-vs-shipped-framework drift) — sanctum path drift surfaced at T1; harvest entry if novel
- **P1** (substrate-as-floor violation) — AC-J binding

---

### Project Structure Notes

- `app/specialists/quinn_r/` — already populated (slab-2a era + slab-2a.4 dispatchers); this story ADVANCES `_act.py`, KEEPS dispatcher helpers
- `_bmad/memory/bmad-agent-quinn-r/` — NEW (sanctum migration target; 6-file BMB)
- `_bmad/memory/quinn-r-sidecar/` — PRESERVED (legacy; cleanup deferred to post-trial-2)
- `skills/bmad-agent-quality-reviewer/` — verified; minimal frontmatter; reference path updated
- `state/config/schemas/authorized-storyboard.schema.json` — NEW (schema lockstep)
- `tests/parity/test_quinn_r_activation_contract.py` — NEW (FR105; flat layout)
- `tests/specialists/quinn_r/test_quinn_r_*.py` — NEW (6 behavioral tests per T4)
- `tests/composition/test_quinn_r_chain.py` — NEW (chain test)

### Detected conflicts or variances

- **Sanctum path-convention ambiguity** — resolved at T1 in favor of `bmad-agent-quinn-r/` per epic-file canonical + Cora-sidecar precedent.
- **Sidecar 5-file vs BMB 6-file pattern** — resolved by sanctum migration at T2.
- **`authorized-storyboard.schema.json` does not yet exist** — created at T2.

---

## References

- **Round-(e) governance JSON**: [`docs/dev-guide/migration-story-governance.json`](../../docs/dev-guide/migration-story-governance.json) §`stories.7b-2`
- **Epic + story-level scope**: [`epics-slab-7b-specialist-activation-eleven.md`](../planning-artifacts/epics-slab-7b-specialist-activation-eleven.md) §Story 7b.2
- **PRD FR90**: [`prd-slab-7b-specialist-activation-eleven.md`](../planning-artifacts/prd-slab-7b-specialist-activation-eleven.md)
- **7b.1 substrate (Wave-1 prerequisite)**: [`migration-7b-1-texas-hardening.md`](migration-7b-1-texas-hardening.md)
- **7a.5 conversation-persistence contract**: [`migration-7a-5-conversation-persistence-specialist-summary-writer.md`](migration-7a-5-conversation-persistence-specialist-summary-writer.md)
- **BMB sanctum alignment checklist (FR108)**: [`docs/dev-guide/bmb-sanctum-alignment-checklist.md`](../../docs/dev-guide/bmb-sanctum-alignment-checklist.md)
- **Specialist anti-patterns**: [`docs/dev-guide/specialist-anti-patterns.md`](../../docs/dev-guide/specialist-anti-patterns.md)
- **Slab 2a.2 precedent (AC-B 150-LOC ceiling)**: [`migration-2a-2-irene-pass-2-scaffold-migration.md`](migration-2a-2-irene-pass-2-scaffold-migration.md)
- **Sandbox-AC inventory (FR107)**: [`docs/dev-guide/migration-ac-sandbox-inventory.json`](../../docs/dev-guide/migration-ac-sandbox-inventory.json)
- **Sprint status**: [`sprint-status.yaml`](sprint-status.yaml)
- **Deferred inventory**: [`deferred-inventory.md`](../planning-artifacts/deferred-inventory.md)
- **CLAUDE.md** — §LangChain/LangGraph migration governance + §BMAD sprint governance

---

## Dev Agent Record

### Agent Model Used

Codex (GPT-5)

### Debug Log References

- T1 readiness passed: Round-(e) pin verified, 7b.1 substrate artifacts present, Wave 0 artifacts present, sandbox-AC preflight PASS.
- T1 drift resolution recorded: canonical Quinn-R sanctum path is `_bmad/memory/bmad-agent-quinn-r/`; pattern is six-file BMB; `authorized-storyboard.schema.json` created; legacy dispatchers consumed.
- T8 verification: focused 7b.2 suite 59 passed; broad regression slice 767 passed / 19 skipped; pipeline lockstep PASS; class-conformance PASS; sandbox-AC PASS; ruff PASS; lint-imports 9/9 KEPT.

### Completion Notes List

(populated at close — must include T11.1-T11.7 evidence + drift-resolution evidence + tripwire-ledger entry)

- Implemented bounded Quinn-R `_act` body with gate-driven G2C, G5, and G3B branches at 150 logical lines.
- G2C emits schema-valid `authorized-storyboard.json`; G5 returns advisory/blocking partitions; G3B consumes sensory and quality-control dispatch helpers.
- Migrated Quinn-R sanctum to `_bmad/memory/bmad-agent-quinn-r/` six-file BMB pattern and preserved legacy sidecar unchanged.
- Updated `skills/bmad-agent-quality-reviewer/SKILL.md` to hot-load the new canonical sanctum path.
- Authored Codex self-review at `_bmad-output/implementation-artifacts/7b-2-codex-self-review-2026-04-29.md`.
- Claude-owned T10 code review and T11 close remain pending.

### File List

- `_bmad-output/implementation-artifacts/7b-2-codex-self-review-2026-04-29.md`
- `_bmad-output/implementation-artifacts/migration-7b-2-quinn-r-hardening.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/planning-artifacts/deferred-inventory.md`
- `_bmad/memory/bmad-agent-quinn-r/INDEX.md`
- `_bmad/memory/bmad-agent-quinn-r/PERSONA.md`
- `_bmad/memory/bmad-agent-quinn-r/CREED.md`
- `_bmad/memory/bmad-agent-quinn-r/BOND.md`
- `_bmad/memory/bmad-agent-quinn-r/MEMORY.md`
- `_bmad/memory/bmad-agent-quinn-r/CAPABILITIES.md`
- `app/specialists/quinn_r/_act.py`
- `app/specialists/quinn_r/graph.py`
- `scripts/utilities/regenerate_authorized_storyboard_schema.py`
- `skills/bmad-agent-quality-reviewer/SKILL.md`
- `state/config/schemas/authorized-storyboard.schema.json`
- `tests/composition/test_quinn_r_chain.py`
- `tests/fixtures/composition/quinn_r_chain/expected-output.json`
- `tests/parity/test_quinn_r_activation_contract.py`
- `tests/parity/test_skill_md_sanctum_alignment.py`
- `tests/specialists/quinn_r/test_quinn_r_act_node_dispatch.py`
- `tests/specialists/quinn_r/test_quinn_r_g2c_write_contract.py`
- `tests/specialists/quinn_r/test_quinn_r_g3b_post_composition.py`
- `tests/specialists/quinn_r/test_quinn_r_g5_qa_body.py`
- `tests/specialists/quinn_r/test_quinn_r_sanctum_cold_read.py`
- `tests/specialists/quinn_r/test_quinn_r_summary_landing.py`
- `tests/specialists/quinn_r/test_quinn_r_two_mode_dispatch.py`

(populated by dev-agent — list all NEW + modified files per T2-T7)
