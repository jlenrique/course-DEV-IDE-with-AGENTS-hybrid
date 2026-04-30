# Migration Story 7b.3: Vera Hardening — G0/G1/G3/G4 Fidelity Rubrics on Real Content + Sensory Bridges Dispatch

**Status:** done
**Sprint key:** `migration-7b-3-vera-hardening`
**Epic:** Slab 7b Specialist Body Activation — `epic-slab-7b-specialist-activation-eleven`. **Wave 1 parallel** (Class-A hardening; parallelizable with 7b.1, 7b.2; Claude-authored per NFR-CG17 + D21).
**Pts:** 3 | **Gate:** single (per `docs/dev-guide/migration-story-governance.json::stories.7b-3`; rationale: null; rubric-semantics work) | **K-target:** ~1.3× (target ~25 tests / floor 19; ~2K LOC).
**Author:** **Claude**. **Review:** **Codex** via `bmad-code-review`.
**Round-(e) E5 binding-hard:** `prerequisite_stories: ["7b-1"]`. **Sprint runner MUST NOT open this story until 7b.1 lands T2 atomic CREATE-tasks.**

---

## Round-(e) Governance Inheritance

Round-(e) freeze landed 2026-04-29. Load-bearing for 7b.3: **E5** — `prerequisite_stories: ["7b-1"]` binding=hard. Other E1-E7 amendments are not directly load-bearing on 7b.3 dev work.

**T1 readiness verification command:**
```bash
.venv/Scripts/python.exe -c "import json; d = json.load(open('docs/dev-guide/migration-story-governance.json', encoding='utf-8')); assert d['version'] == '2026-04-29-slab7b-twelve-stories'; assert '_staged_pending_party_mode_ratification' not in d['stories']['7b-3']; assert d['stories']['7b-3']['prerequisite_stories'] == ['7b-1']; print('Round-(e) verified PASS for 7b-3')"
```

---

## T1 Readiness Block

### Required-readings cascade (10-reading)

1. **Round-(e) governance JSON** — `docs/dev-guide/migration-story-governance.json` §`stories.7b-3`. Confirm `single-gate`, `expected_k_target: 1.3`, `prerequisite_stories: ["7b-1"]`.
2. **Epic + story-level scope** — [`epics-slab-7b-specialist-activation-eleven.md`](../planning-artifacts/epics-slab-7b-specialist-activation-eleven.md) §Story 7b.3 (lines 530-575). Wave-1 close gate (Round-(a) Amelia A3): if any of 7b.1/7b.2/7b.3 lands >2.7K LOC, K-aggregate tripwire fires.
3. **PRD §FR91** — Vera G0 6-dim evidence-sentence rubric on real Texas output + G1 ingestion-quality 6-dim verdicts + G3 fidelity check on real Storyboard A + G4 19-criterion rubric (G4-01..G4-19) + sensory-bridges dispatch on real motion + audio + circuit-breaker mechanism.
4. **7b.1 Wave-1 substrate (T2 atomic-commit)** — verify all 4 CREATE-task artifacts present (`tests/parity/_sanctum_parity_base.py` + `tests/composition/_chain_test_base.py` + `scripts/utilities/validate_parity_test_class_conformance.py` + `tests/parity/README.md` §"FR105 + Errata 4 layout decision").
5. **G4 19-criterion canonical source** — [`state/config/fidelity-contracts/g4-narration-script.yaml`](../../state/config/fidelity-contracts/g4-narration-script.yaml) (Epic 23 closure; codifies G4-01..G4-19 with severity + description).
6. **Sensory-bridges skill** — [`skills/sensory-bridges/`](../../skills/sensory-bridges/) (universal perception protocol — image/audio/video).
7. **7a.5 conversation-persistence** — verdicts land at `runs/<run_id>/specialist-summaries/vera-<gate>-<timestamp>.md` (7a.5 facade).
8. **BMB sanctum alignment checklist (FR108)** — [`docs/dev-guide/bmb-sanctum-alignment-checklist.md`](../../docs/dev-guide/bmb-sanctum-alignment-checklist.md).
9. **Slab 2a.2 precedent (AC-B 150-LOC ceiling)** — [`migration-2a-2-irene-pass-2-scaffold-migration.md`](migration-2a-2-irene-pass-2-scaffold-migration.md).
10. **CLAUDE.md** — §LangChain/LangGraph migration governance + §BMAD sprint governance.

### Vera current-state probe + drift surfacing

```bash
ls app/specialists/vera/                        # __init__.py expertise/ graph.py model_config.yaml sensory_bridges_dispatch.py state.py
ls _bmad/memory/vera-sidecar/                   # CLONE-FORK-NOTICE.md access-boundaries.md chronology.md index.md patterns.md (5-file sidecar — DRIFT)
ls skills/bmad-agent-fidelity-assessor/         # SKILL.md references/ (skill-dir name follows legacy `fidelity-assessor` convention)
ls skills/sensory-bridges/                      # sensory-bridges skill (universal perception protocol)
ls state/config/fidelity-contracts/g4-narration-script.yaml  # 19-criterion canonical source
```

Two drifts surface at T1 (parallel to 7b.2 §Drift #1):

**⚠️ Drift #1 — Sanctum dir path convention (BLOCKING for AC-7b.3-J SG-4 first-enforcement on Vera):** Epic file Story 7b.3 line 560 specifies `_bmad/memory/bmad-agent-vera/`. Reality: only `_bmad/memory/vera-sidecar/` (5-file sidecar). **Resolution at T1:** path = `_bmad/memory/bmad-agent-vera/` + pattern = 6-file BMB (`INDEX.md` / `PERSONA.md` / `CREED.md` / `BOND.md` / `MEMORY.md` / `CAPABILITIES.md`). Same rationale as 7b.2 (epic-canonical; Cora-sidecar precedent at `bmad-agent-cora/`). Filed as deferred-inventory follow-on `vera-sanctum-sidecar-to-bmb-migration` — CLOSED at this story T2.

**⚠️ Drift #2 — Existing `sensory_bridges_dispatch.py` shared between Vera + Quinn-R.** Slab-2a.4 era carry-forward; substrate-as-floor invariant. Wave-1 hardening consumes the dispatcher (NOT replaces). At T1, verify the dispatcher is import-stable + offers the contract surfaces Vera `_act` needs for sensory-bridges invocation.

### Wave 0 + Wave-1-substrate artifact-existence sweep

```bash
ls docs/dev-guide/bmb-sanctum-alignment-checklist.md docs/dev-guide/sanctum-exception-categories.json docs/dev-guide/operator-control-parity-template.md docs/dev-guide/migration-ac-sandbox-inventory.json skills/bmad-agent-cora/SKILL.md
ls docs/dev-guide/scaffolds/scaffold-v0.2-D2-pipeline/
ls tests/parity/_sanctum_parity_base.py tests/composition/_chain_test_base.py scripts/utilities/validate_parity_test_class_conformance.py
grep -c "FR105 + Errata 4 layout decision" tests/parity/README.md  # >=1 expected
```

All paths must exist. If any absent → HALT.

### Sandbox-AC validator pre-flight

```bash
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py \
  _bmad-output/implementation-artifacts/migration-7b-3-vera-hardening.md
```
Expect PASS. No forbidden CLI in dev-agent ACs. Vera is rubric-semantics + sensory-bridges work, not third-party-API-bound; no live-API verification needed.

### Standing pre-flight items

1. Severance posture confirmed — hybrid working tree is sole input surface.
2. `state/config/substrate-frozen-paths.yaml` — diffs touching `app/marcus/orchestrator/dispatch_adapter.py:70-95` require ceremony; this story does NOT touch substrate.
3. NFR-T9-T12 wall-clock ceilings hold.

---

## Story

As a **migration dev agent**,
I want **Vera's `_act` body hardened to execute fidelity rubrics on real upstream artifacts — G0 6-dim evidence-sentence rubric on Texas output, G1 ingestion-quality 6-dim verdicts, G3 fidelity check on real Storyboard A, G4 19-criterion rubric (G4-01..G4-19 from `g4-narration-script.yaml`), sensory-bridges dispatch on real motion + audio, AND circuit-breaker mechanism that HALTs the run on hard-fail O/I/A findings — AND I want Vera's sanctum migrated from sidecar (5 files) to canonical 6-file BMB pattern at `_bmad/memory/bmad-agent-vera/`**,
So that **(a) Vera's Fidelity Trace Reports carry forensic findings (Omissions/Inventions/Alterations) on real content (not scaffold-stubbed), (b) the circuit-breaker activates against real failure modes returning operator control with explicit verdict, (c) Quinn-R's downstream rubric runs on Vera-cleared artifacts, and (d) SG-4 sanctum-alignment is structurally enforced for Vera via the FR101 parity test inheriting `SanctumParityTestBase` from 7b.1 substrate**.

---

## Acceptance Criteria

All ACs are dev-agent-executable (sandbox-AC compliant). No third-party API live-binding required. Live-substrate verification wraps via shipped Python deps with `pytest.skip(...)` when service unreachable.

### AC-7b.3-A — T1 readiness verification + drift resolution

**Given** the Round-(e) governance JSON pin + 7b.1 T2 atomic-commit landed
**When** the dev agent runs T1 readiness
**Then** all 10 readings cascade complete; Round-(e) verification command exits 0; Wave-0 + 7b.1-T2 sweep PASS; sandbox-AC validator PASS pre-flight
**And** Drift #1 resolution recorded: path = `_bmad/memory/bmad-agent-vera/`; pattern = 6-file BMB
**And** Drift #2 acknowledged: legacy `sensory_bridges_dispatch.py` consumed (NOT replaced).

### AC-7b.3-B — Sanctum migration: sidecar (5 files) → BMB (6 files) at canonical path

**Given** Vera's existing sanctum at `_bmad/memory/vera-sidecar/` (5-file sidecar pattern)
**And** Drift #1 resolution at AC-A binding `_bmad/memory/bmad-agent-vera/` + 6-file BMB
**When** the dev agent migrates the sanctum
**Then** `_bmad/memory/bmad-agent-vera/` directory lands with 6 files: `INDEX.md` + `PERSONA.md` + `CREED.md` + `BOND.md` + `MEMORY.md` + `CAPABILITIES.md` (per Texas precedent + BMB checklist FR108)
**And** content is translated from `vera-sidecar/` where applicable
**And** the legacy `_bmad/memory/vera-sidecar/` directory is preserved unchanged (cleanup deferred to post-trial-2; deferred-inventory follow-on `vera-sidecar-cleanup-post-trial-2-validation` filed)
**And** deferred-inventory follow-on `vera-sanctum-sidecar-to-bmb-migration` → CLOSED at T2.

### AC-7b.3-C — G0 6-dim evidence-sentence rubric on real Texas output

**Given** Vera running G0 against Texas's `extracted.md` (post-7b.1 hardening; six-canonical-artifacts contract in place)
**When** Vera's `_act` body executes the G0 rubric
**Then** the rubric scores `extracted.md` against six dimensions per FR91 contract
**And** a Fidelity Trace Report lands at `runs/<run_id>/fidelity/g0-vera-<timestamp>.json` with O/I/A taxonomy (Omissions / Inventions / Alterations) itemized
**And** each finding carries: `category: O|I|A`, `severity: critical|warning|advisory`, `evidence_anchor: <source-of-truth-pointer>`, `description: <forensic-note>`.

### AC-7b.3-D — G1 ingestion-quality 6-dim verdicts

**Given** Vera running G1 ingestion-quality on the post-Texas extraction bundle
**When** Vera's `_act` body executes the G1 rubric
**Then** six-dim verdicts emit covering ingestion completeness, ingestion fidelity, source-mapping coverage, manifest hash integrity, evidence-anchor traceability, and cross-validation hint application
**And** verdicts land in the same Fidelity Trace Report file (G0 + G1 both emitted; partition by gate-id).

### AC-7b.3-E — G3 fidelity check on real Storyboard A + sensory-bridges dispatch

**Given** Vera running G3 fidelity check on real Storyboard A (post-7b.6 Gary slides + post-7b.7 Kira motion + post-7b.8 Enrique audio — for Wave 1 dev, fixture-replay via cassettes is acceptable)
**When** the G3 body executes
**Then** sensory-bridges skill at `skills/sensory-bridges/` is INVOKED for image/audio/video perception per universal perception protocol
**And** confidence rubric scores per modality (visual / audio / motion) land in the Fidelity Trace Report
**And** the existing `sensory_bridges_dispatch.py` helper is consumed (NOT replaced) per substrate-as-floor invariant.

### AC-7b.3-F — G4 19-criterion rubric on real Irene Pass-2 narration

**Given** Vera running G4 against real Irene Pass-2 narration script (post-7b.4 close — fixture-replay via cassettes for Wave 1)
**And** the canonical 19-criterion source at `state/config/fidelity-contracts/g4-narration-script.yaml` (Epic 23 closure)
**When** the G4 body executes
**Then** all 19 criteria (G4-01 through G4-19) are evaluated parametrically (one verdict per criterion)
**And** each verdict carries `criterion_id`, `severity`, `description`, `evidence_anchor` per FR91
**And** verdicts emit to the Fidelity Trace Report partitioned by gate-id (G4 section).

### AC-7b.3-G — Circuit-breaker mechanism on hard-fail O/I/A

**Given** the circuit-breaker mechanism per APP fidelity architecture
**When** Vera detects a hard-fail O/I/A finding (per circuit-breaker rule — `severity: critical` on Omission OR Invention OR Alteration)
**Then** the run halts at the gate with `HALT-AND-REMEDIATE` verdict
**And** control returns to operator with Vera's verdict carrying explicit failure reason (NOT silent advance)
**And** the verdict landing at `runs/<run_id>/specialist-summaries/vera-<gate>-<timestamp>.md` carries `verb: "halt"` (per 7a.5 SpecialistReturn shape; NOT `verb: "proceed"`).
**Test pin:** `tests/specialists/vera/test_vera_circuit_breaker.py` — synthetic hard-fail O/I/A injection; assert HALT verdict; assert NO silent fallthrough.

### AC-7b.3-H — `_act` body length ≤150 LOC per AC-B ceiling

**Given** the AC-B 150-LOC ceiling discipline (Slab 2a.2 precedent MF4)
**When** the dev-agent commits Vera `_act` body
**Then** `app/specialists/vera/_act.py` body length ≤150 LOC
**And** if exceeds, dev-agent HALTS and raises party-mode re-scope decision (split-to-7b.3a vs re-scope-up).

### AC-7b.3-I — Verdict landing per 7a.5 conversation-persistence contract

**Given** the Slab 7a 7a.5 conversation-persistence contract
**When** Vera `_act` completes (G0, G1, G3, G4)
**Then** Vera invokes `app.marcus.orchestrator.specialist_summary_writer.emit_summary(specialist="vera", gate=<gate>, payload=<verdict>)` per 7a.5 facade
**And** the summary file lands at canonical path with timestamped filename + 15-25 lines + canonical specialist_id mapping
**And** SHA256 tamper-evident chain integrity preserved.

### AC-7b.3-J — SG-4 Sanctum Alignment (FR100 + FR101 — Vera enforcement)

**Given** the SG-4 sanctum-alignment requirement
**When** the dev-agent commits Vera hardening
**Then** `skills/bmad-agent-fidelity-assessor/SKILL.md` is verified option-a sanctum-aligned per BMB checklist (FR108):
  - YAML frontmatter MINIMAL (`name` + `description` only); fix if drifted
  - SKILL.md body references `_bmad/memory/bmad-agent-vera/` (NEW canonical path) as activation-time hot-load batch
**And** the new sanctum dir at `_bmad/memory/bmad-agent-vera/` carries 6-file BMB pattern
**And** the parity test `tests/parity/test_skill_md_sanctum_alignment.py` (created by 7b.1) PASSES for Vera with Class-A template assertions
**And** `bmad-code-review` (T11) confirms `# SG-4 Sanctum Alignment` AC verbatim in this story planning artifact.

### AC-7b.3-K — FR105 per-specialist parity test (Vera activation contract)

**Given** the Errata 4 verdict-flat layout ratified at 7b.1 T2
**When** the dev-agent authors Vera's activation-contract test
**Then** `tests/parity/test_vera_activation_contract.py` (flat) lands inheriting `SanctumParityTestBase` with `class_template_id = "A"`, `specialist_name = "vera"`
**And** the test asserts Class-A rubric-semantics parity: (i) G0/G1/G3/G4 four-gate dispatch shape; (ii) O/I/A taxonomy structural shape in trace report; (iii) circuit-breaker behavioral contract (HALT on hard-fail); (iv) sensory-bridges invocation on G3; (v) verdict-landing at canonical 7a.5 summary path; (vi) cold-activation smoke
**And** `@pytest.mark.timeout(30)` per NFR-T9; <120s aggregate per NFR-T12
**And** `validate_parity_test_class_conformance.py` PASSES on this test file.

### AC-7b.3-L — Sandbox-AC governance (CLAUDE.md + FR107)

**Given** the sandbox-AC inventory governance requirement
**When** `validate_migration_story_sandbox_acs.py` runs on this spec
**Then** PASS (no forbidden CLI in dev-agent ACs)
**And** Vera-specific: NO sandbox-AC inventory entry needed (rubric-semantics + sensory-bridges work, not API-bound).

### AC-7b.3-M — Substrate-as-floor invariant (FR113 + NFR-I13)

**Given** the substrate-as-floor invariant
**When** the dev-agent's diff is reviewed
**Then** **no diff hunk touches `app/marcus/orchestrator/dispatch_adapter.py:70-95`** absent ceremony
**And** legacy `app/specialists/vera/sensory_bridges_dispatch.py` consumed (NOT modified — except optionally additive helpers; if substantive changes, halt and surface).

### AC-7b.3-N — Wave-1 close tripwire ledger (Round-(e) E2 contribution)

**Given** the Round-(e) E2 amendment landed `tripwire_events: []` schema slot
**When** this story closes
**Then** the dev-agent appends OR amends the existing `wave_1_close` entry at `sprint-status.yaml::tripwire_events`:
```yaml
tripwire_events:
  - tripwire_id: wave_1_close
    story_owner: <7b-1|7b-2|7b-3 closer-of-record>
    fired_at: <YYYY-MM-DD>
    fired_verdict: <true|false>
    measured_value:
      kloc_aggregate: <N.NN>
      per_story:
        7b-1: <N.NN>
        7b-2: <N.NN>
        7b-3: <N.NN>           # this story's contribution
    escalation_action_taken: <none|wave_2_irene_at_upper_band_k_target_only>
    decision_record_link: <links>
```
**And** if `fired_verdict: true`, escalation per Round-(a) Amelia A3.

### AC-7b.3-O — Chain test inheriting `ChainTestBase`

**Given** NFR-CG14 chain-test PR pre-merge requirement + 7b.1's `_chain_test_base.py` substrate
**When** the dev agent authors the Vera chain test
**Then** `tests/composition/test_vera_chain.py` lands inheriting `ChainTestBase`
**And** the test asserts envelope-handoff shape compatibility for upstream (Texas → Vera G0; Irene Pass-2 → Vera G4 — fixture-replay) AND Vera → downstream (Marcus gate-runner)
**And** wall-clock <120s.

### AC-7b.3-P — Close protocol

**Given** all prior ACs PASS + bmad-code-review returns PASS or PASS-WITH-PATCH-applied + regression baseline holds
**When** the story closes
**Then** at close:
  1. **sprint-status.yaml** flip: `migration-7b-3-vera-hardening: in-progress → review → done`
  2. **Wave-1 close tripwire ledger entry** appended/amended per AC-N
  3. **next-session-start-here.md** updated if Wave-1 close is the last of three: pivot to Wave-2a (7b.4 Irene Pass-1)
  4. **Deferred-inventory updates**: `vera-sanctum-sidecar-to-bmb-migration` CLOSED at T2; `vera-sidecar-cleanup-post-trial-2-validation` filed
  5. **Standing-guardrail status**: SG-4 GREEN for Vera (3rd specialist after Texas + Quinn-R if 7b.2 closed prior)
  6. **Three-line D12 close stub**

---

## Tasks / Subtasks

### T1 — T1 readiness verification + drift resolution
- [x] **T1.1** Round-(e) governance JSON verification
- [x] **T1.2** 10-reading required cascade
- [x] **T1.3** 7b.1 T2 substrate sweep
- [x] **T1.4** Wave 0 artifact sweep
- [x] **T1.5** Vera current-state probe — surface 2 drift items
- [x] **T1.6** Drift resolution recorded in Dev Agent Record T1 block
- [x] **T1.7** Sandbox-AC validator pre-flight (PASS expected)

### T2 — Sanctum migration (sidecar → BMB)
- [x] **T2.1** Author 6 BMB files at `_bmad/memory/bmad-agent-vera/` (translate from `vera-sidecar/`)
- [x] **T2.2** File `vera-sanctum-sidecar-to-bmb-migration` follow-on as CLOSED
- [x] **T2.3** File `vera-sidecar-cleanup-post-trial-2-validation` as named-but-not-filed follow-on

### T3 — Vera `_act` body hardening (AC-C..AC-G)
- [x] **T3.1** Implement G0 6-dim evidence-sentence rubric (against real Texas output)
- [x] **T3.2** Implement G1 ingestion-quality 6-dim verdicts
- [x] **T3.3** Implement G3 fidelity check + sensory-bridges dispatch (image/audio/video; consume `sensory_bridges_dispatch.py` helper)
- [x] **T3.4** Implement G4 19-criterion rubric (parametrize over `g4-narration-script.yaml`)
- [x] **T3.5** Implement circuit-breaker mechanism (HALT on hard-fail O/I/A)
- [x] **T3.6** Wire 7a.5 specialist-summary-writer integration
- [x] **T3.7** **AC-B 150-LOC ceiling discipline:** `_act` body ≤150 LOC

### T4 — Parity + behavioral tests
- [x] **T4.1** `tests/parity/test_vera_activation_contract.py` (flat; SanctumParityTestBase; Class-A) — AC-K
- [x] **T4.2** `tests/specialists/vera/test_vera_g0_evidence_sentence_rubric.py` — AC-C
- [x] **T4.3** `tests/specialists/vera/test_vera_g1_ingestion_quality.py` — AC-D
- [x] **T4.4** `tests/specialists/vera/test_vera_g3_fidelity_storyboard_a.py` — AC-E
- [x] **T4.5** `tests/specialists/vera/test_vera_g4_19_criterion_rubric.py` — parametrize over 19 criteria — AC-F
- [x] **T4.6** `tests/specialists/vera/test_vera_sensory_bridges_dispatch.py` — AC-E
- [x] **T4.7** `tests/specialists/vera/test_vera_circuit_breaker.py` — synthetic hard-fail injection — AC-G
- [x] **T4.8** `tests/specialists/vera/test_vera_summary_landing.py` — AC-I
- [x] **T4.9** `tests/composition/test_vera_chain.py` — inherits ChainTestBase — AC-O
- [x] **T4.10** Wall-clock annotations + `validate_parity_test_class_conformance.py` PASS

### T5 — SG-4 sanctum alignment verification (AC-J)
- [x] **T5.1** Verify `skills/bmad-agent-fidelity-assessor/SKILL.md` minimal frontmatter — fix if drifted
- [x] **T5.2** Update SKILL.md body to reference `_bmad/memory/bmad-agent-vera/`
- [x] **T5.3** `tests/parity/test_skill_md_sanctum_alignment.py` PASSES for Vera

### T6 — Substrate-as-floor verification (AC-M)
- [x] **T6.1** `git diff` verification on dispatch_adapter.py:70-95 (no diff)

### T7 — Regression baseline + sandbox-AC final
- [x] **T7.1** Full regression battery (target ≥696 + ~25-new ≈ 721 passed; 19 skipped)
- [x] **T7.2** Story-scoped ruff clean per T9 battery; full repo `ruff check .` attempted and failed on pre-existing out-of-scope lint debt
- [x] **T7.3** `lint-imports.exe` 9/9 KEPT
- [x] **T7.4** Sandbox-AC validator final PASS

### T8 — Codex G6 self-review (NEW CYCLE T10)
- [x] **T8.1** Codex authors G6 self-review at `_bmad-output/implementation-artifacts/7b-3-codex-self-review-2026-04-XX.md`
- [x] **T8.2** Status flip `in-progress → review`

### T9 — Claude bmad-code-review
- [ ] **T9.1** Claude runs `bmad-code-review` at `7b-3-code-review-2026-04-XX.md`
- [ ] **T9.2** PASS / PASS-WITH-PATCH / HALT-AND-REMEDIATE; remediation cycle 1 if needed

### T10 — Close (AC-N + AC-P)
- [ ] **T10.1** Append/amend Wave-1-close tripwire ledger entry per AC-N
- [ ] **T10.2** Sprint-status flip `review → done`
- [ ] **T10.3** Update `next-session-start-here.md` if Wave-1 close
- [ ] **T10.4** Deferred-inventory updates per AC-P.4
- [ ] **T10.5** Standing-guardrail status snapshot — SG-4 Vera enforcement
- [ ] **T10.6** Three-line D12 close stub
- [ ] **T10.7** Commit + push

---

## Dev Notes

### Round-(e) E5 prerequisite_stories binding

This story carries `prerequisite_stories: ["7b-1"]` with `binding=hard`. T1.3 verifies all 4 substrate artifacts present before opening.

### Class-A rubric-semantics scope

Vera is Class A — fidelity rubrics + sensory-bridges work. Single-gate.

### 19-criterion canonical source is OUT OF SCOPE for amendment

`state/config/fidelity-contracts/g4-narration-script.yaml` is owned by Epic 23 closure. This story CONSUMES it, does NOT amend. If Vera's G4 body surfaces a missing or mis-codified criterion, file as deferred-inventory follow-on `g4-narration-script-criterion-amendment-{N}` for separate scope.

### Circuit-breaker is behavioral contract, not test-only

The circuit-breaker mechanism is the production HALT-AND-REMEDIATE path. Test `test_vera_circuit_breaker.py` injects synthetic hard-fail to verify the contract; production runs trigger the same mechanism on real O/I/A findings.

### NFR predicates honored

NFR-T9 / T10 / T11 / T11a / T11b / T12 — `@pytest.mark.timeout` annotations.
NFR-CG14 + NFR-CG14a — chain test inheriting ChainTestBase.
NFR-CG16 — bmad-code-review pre-close.
NFR-I9 + NFR-I10 + NFR-I12 — parity test + activation contract + class-shaped template (Class-A).
NFR-I13 — substrate-frozen-paths-check.

### Known follow-ons

- **`vera-sanctum-sidecar-to-bmb-migration`** — CLOSE at T2
- **`vera-sidecar-cleanup-post-trial-2-validation`** — filed; close after trial-2
- **`g4-narration-script-criterion-amendment-{N}`** — only if surfaced during dev

### Anti-pattern catalog citations

- **A6** (silent-fixture-stub fallback) — closing for Vera G0/G1/G3/G4
- **A9** (epic-doc-vs-shipped-framework drift) — sanctum path drift; harvest entry if novel
- **P1** (substrate-as-floor violation) — AC-M binding

---

### Project Structure Notes

- `app/specialists/vera/` — already populated; this story ADVANCES `_act.py`, KEEPS `sensory_bridges_dispatch.py` helper
- `_bmad/memory/bmad-agent-vera/` — NEW (sanctum migration target)
- `_bmad/memory/vera-sidecar/` — PRESERVED
- `skills/bmad-agent-fidelity-assessor/` — verified; minimal frontmatter; reference path updated
- `skills/sensory-bridges/` — consumed (universal perception protocol)
- `state/config/fidelity-contracts/g4-narration-script.yaml` — consumed (NOT modified)
- `tests/parity/test_vera_activation_contract.py` — NEW
- `tests/specialists/vera/test_vera_*.py` — NEW (8 behavioral tests)
- `tests/composition/test_vera_chain.py` — NEW

### Detected conflicts or variances

- **Sanctum path-convention** — resolved in favor of `bmad-agent-vera/` per epic-canonical
- **Sidecar 5-file vs BMB 6-file** — resolved by sanctum migration at T2

---

## References

- **Round-(e) governance JSON**: [`docs/dev-guide/migration-story-governance.json`](../../docs/dev-guide/migration-story-governance.json) §`stories.7b-3`
- **Epic + story-level scope**: [`epics-slab-7b-specialist-activation-eleven.md`](../planning-artifacts/epics-slab-7b-specialist-activation-eleven.md) §Story 7b.3
- **PRD FR91**: [`prd-slab-7b-specialist-activation-eleven.md`](../planning-artifacts/prd-slab-7b-specialist-activation-eleven.md) §FR91
- **G4 19-criterion canonical**: [`state/config/fidelity-contracts/g4-narration-script.yaml`](../../state/config/fidelity-contracts/g4-narration-script.yaml)
- **Sensory-bridges skill**: [`skills/sensory-bridges/`](../../skills/sensory-bridges/)
- **7b.1 substrate**: [`migration-7b-1-texas-hardening.md`](migration-7b-1-texas-hardening.md)
- **7b.2 spec (parallel sibling)**: [`migration-7b-2-quinn-r-hardening.md`](migration-7b-2-quinn-r-hardening.md)
- **7a.5 conversation-persistence contract**: [`migration-7a-5-conversation-persistence-specialist-summary-writer.md`](migration-7a-5-conversation-persistence-specialist-summary-writer.md)
- **BMB sanctum alignment checklist (FR108)**: [`docs/dev-guide/bmb-sanctum-alignment-checklist.md`](../../docs/dev-guide/bmb-sanctum-alignment-checklist.md)
- **Specialist anti-patterns**: [`docs/dev-guide/specialist-anti-patterns.md`](../../docs/dev-guide/specialist-anti-patterns.md)
- **Slab 2a.2 precedent (AC-B 150-LOC)**: [`migration-2a-2-irene-pass-2-scaffold-migration.md`](migration-2a-2-irene-pass-2-scaffold-migration.md)
- **Sandbox-AC inventory (FR107)**: [`docs/dev-guide/migration-ac-sandbox-inventory.json`](../../docs/dev-guide/migration-ac-sandbox-inventory.json)
- **Sprint status**: [`sprint-status.yaml`](sprint-status.yaml)
- **Deferred inventory**: [`deferred-inventory.md`](../planning-artifacts/deferred-inventory.md)

---

## Dev Agent Record

### Agent Model Used

Codex (GPT-5)

### Debug Log References

- 2026-04-29 T1: Round-(e) governance JSON verified for `stories.7b-3` (`single-gate`, `expected_pts=3`, `expected_k_target=1.3`, `prerequisite_stories=["7b-1"]`).
- 2026-04-29 T1: 7b.1 T2 substrate files verified present and tracked at HEAD (`tests/parity/_sanctum_parity_base.py`, `tests/composition/_chain_test_base.py`, class-conformance validator, parity README Errata marker).
- 2026-04-29 T1: Wave-0 artifacts, Vera app baseline, `skills/bmad-agent-fidelity-assessor/SKILL.md`, `skills/sensory-bridges/`, and `g4-narration-script.yaml` verified present.
- 2026-04-29 T1: G4 canonical source verified at 19 criteria (`G4-01` through `G4-19`); sandbox-AC validator preflight PASS.
- 2026-04-29 T1: Drift #1 confirmed: only `_bmad/memory/vera-sidecar/` exists pre-T2; resolved by T2 migration to `_bmad/memory/bmad-agent-vera/`. Drift #2 confirmed: existing `app/specialists/vera/sensory_bridges_dispatch.py` is consumed, not replaced.
- 2026-04-29 T7: Focused Vera battery PASS (`76 passed`); broad regression PASS (`837 passed, 19 skipped`); pipeline lockstep PASS; sandbox-AC PASS; parity class conformance PASS; lint-imports 9/9 KEPT; dispatch_adapter.py diff empty. Story-scoped ruff PASS. Full repo `ruff check .` was attempted and failed on pre-existing out-of-scope lint debt, not on Vera story scope.

### Completion Notes List

- Migrated Vera from legacy `_bmad/memory/vera-sidecar/` to canonical six-file BMB sanctum at `_bmad/memory/bmad-agent-vera/`, preserving the legacy sidecar unchanged.
- Split Vera's bounded act body into `app/specialists/vera/_act.py`; graph `_act` now delegates while keeping the scaffold node shape stable.
- Implemented G0/G1/G3/G4 Fidelity Trace Report emission with O/I/A taxonomy, G3 sensory-bridges image/audio/video dispatch, G4 19-criterion verdicts from the canonical YAML source, and HALT-AND-REMEDIATE circuit breaker behavior on critical O/I/A findings.
- Updated `skills/bmad-agent-fidelity-assessor/SKILL.md` activation prose to hot-load `_bmad/memory/bmad-agent-vera/`.
- Added Vera activation, behavior, summary, circuit-breaker, G4 parametrized, and chain-test coverage. T9/T10 remain for Claude review and close protocol.

### File List

- `_bmad-output/implementation-artifacts/7b-3-codex-self-review-2026-04-29.md`
- `_bmad-output/implementation-artifacts/migration-7b-3-vera-hardening.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/planning-artifacts/deferred-inventory.md`
- `_bmad/memory/bmad-agent-vera/INDEX.md`
- `_bmad/memory/bmad-agent-vera/PERSONA.md`
- `_bmad/memory/bmad-agent-vera/CREED.md`
- `_bmad/memory/bmad-agent-vera/BOND.md`
- `_bmad/memory/bmad-agent-vera/MEMORY.md`
- `_bmad/memory/bmad-agent-vera/CAPABILITIES.md`
- `app/specialists/vera/_act.py`
- `app/specialists/vera/graph.py`
- `skills/bmad-agent-fidelity-assessor/SKILL.md`
- `tests/composition/test_vera_chain.py`
- `tests/fixtures/composition/vera_chain/expected-output.json`
- `tests/parity/test_skill_md_sanctum_alignment.py`
- `tests/parity/test_vera_activation_contract.py`
- `tests/specialists/vera/_act_helpers.py`
- `tests/specialists/vera/test_vera_act_node_dispatch.py`
- `tests/specialists/vera/test_vera_circuit_breaker.py`
- `tests/specialists/vera/test_vera_g0_evidence_sentence_rubric.py`
- `tests/specialists/vera/test_vera_g1_ingestion_quality_verdicts.py`
- `tests/specialists/vera/test_vera_g3_fidelity_storyboard_a.py`
- `tests/specialists/vera/test_vera_g4_19_criterion_rubric.py`
- `tests/specialists/vera/test_vera_sanctum_cold_read.py`
- `tests/specialists/vera/test_vera_summary_landing.py`
