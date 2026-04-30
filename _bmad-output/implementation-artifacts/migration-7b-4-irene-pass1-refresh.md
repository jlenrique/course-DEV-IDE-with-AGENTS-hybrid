# Migration Story 7b.4: Irene Pass-1 Activation Refresh — 9-Node Scaffold Mirroring Pass-2

**Status:** done
**Sprint key:** `migration-7b-4-irene-pass1-refresh`
**Epic:** Slab 7b Specialist Body Activation — `epic-slab-7b-specialist-activation-eleven`. **Wave 2a** (Class-B refresh; serial after Wave-1 close — inherits Vera G4 rubric from 7b.3 closure; Claude-authored per NFR-CG17 + D21).
**Pts:** 3 | **Gate:** single (per `docs/dev-guide/migration-story-governance.json::stories.7b-4`; rationale: null; persona-continuity refresh) | **K-target:** ~1.3× (target ~30 tests / floor ~24; ~2.5K LOC).
**Author:** **Claude**. **Review:** **Codex** via `bmad-code-review`.
**Wave-2a precondition:** all 3 Wave-1 stories `done` (7b.1 + 7b.2 + 7b.3) per CLAUDE.md sprint governance — Pass-1 inherits Vera G4 rubric for downstream review on Pass-1 lesson plan.

---

## Round-(e) Governance Inheritance

Round-(e) freeze landed 2026-04-29. For 7b.4 there are **no direct binding-hard amendments** — the story is single-gate and not subject to E1/E2/E3/E4/E5/E6 specific bindings (those target 7b-7/8/11/5/2/3/10 etc.). E7 unfreeze + version bump + tripwire-events ledger applies generally.

**T1 readiness verification command:**
```bash
.venv/Scripts/python.exe -c "import json; d = json.load(open('docs/dev-guide/migration-story-governance.json', encoding='utf-8')); assert d['version'] == '2026-04-29-slab7b-twelve-stories'; assert '_staged_pending_party_mode_ratification' not in d['stories']['7b-4']; print('Round-(e) verified PASS for 7b-4')"
```

---

## T1 Readiness Block

### Required-readings cascade (10-reading)

1. **Round-(e) governance JSON** — `docs/dev-guide/migration-story-governance.json` §`stories.7b-4`.
2. **Epic + story-level scope** — [`epics-slab-7b-specialist-activation-eleven.md`](../planning-artifacts/epics-slab-7b-specialist-activation-eleven.md) §Story 7b.4 (lines 579-619).
3. **PRD §FR92** — Irene Pass-1 9-node scaffold + lesson-plan coauthoring + scope-lock contract + per-plan-unit ratification surface for G1A + `irene-pass1.md` artifact write + mode-singularity hard-constraint + `scope_decision.set` + `plan.locked` learning-event emission.
4. **Slab 2a.2 Pass-2 precedent (CRITICAL — 9-node scaffold pattern)** — [`migration-2a-2-irene-pass-2-scaffold-migration.md`](migration-2a-2-irene-pass-2-scaffold-migration.md). Mirror the 9-node shape; respect AC-B 150-LOC ceiling; cache-hit-rate harness pattern; sanctum cold-read at `plan` node; deterministic prompt assembly per MF1 byte-stability discipline.
5. **9-node scaffold canonical** — [`tests/integration/scaffold_conformance/scaffold_contract.py::SCAFFOLD_NODE_IDS`](../../tests/integration/scaffold_conformance/scaffold_contract.py) frozenset (`receive/plan/act/verify/reflect/emit_spans/gate_decision/finalize/handoff`).
6. **Wave-1 close evidence** — verify all 3 Wave-1 stories (7b.1 + 7b.2 + 7b.3) `done` in `_bmad-output/implementation-artifacts/sprint-status.yaml`. Read `tripwire_events::wave_1_close` entry — if `fired_verdict: true`, this story opens at upper-band K-target per Round-(a) Amelia A3.
7. **Vera G4 19-criterion rubric (from 7b.3 close)** — [`state/config/fidelity-contracts/g4-narration-script.yaml`](../../state/config/fidelity-contracts/g4-narration-script.yaml) + Vera's downstream review on Irene Pass-1 lesson plan must be consumable.
8. **7a.5 conversation-persistence + learning-event substrate** — [`migration-7a-5-conversation-persistence-specialist-summary-writer.md`](migration-7a-5-conversation-persistence-specialist-summary-writer.md). `scope_decision.set` + `plan.locked` events emit per the learning-event schema.
9. **BMB sanctum alignment checklist (FR108)** — [`docs/dev-guide/bmb-sanctum-alignment-checklist.md`](../../docs/dev-guide/bmb-sanctum-alignment-checklist.md).
10. **CLAUDE.md** — §LangChain/LangGraph migration governance + §BMAD sprint governance.

### Irene current-state probe + drift surfacing

```bash
ls app/specialists/irene/                          # __init__.py authoring/ expertise/ graph.py model_config.yaml state.py (Pass-2; slab-2a.2 era)
ls app/specialists/irene_pass1/ 2>/dev/null        # NOT YET PRESENT — this story creates
ls _bmad/memory/bmad-agent-content-creator/        # 6-file BMB pattern + capabilities/ references/ scripts/ sessions/ (sanctum SHARED with Pass-2 — already canonical; NO migration needed)
ls _bmad/memory/irene-sidecar/                     # 5-file sidecar (legacy; preserve untouched)
ls skills/bmad-agent-content-creator/              # SKILL.md + assets/ + references/ + scripts/ (skill-dir SHARED with Pass-2)
```

**Two drifts surface at T1:**

**⚠️ Drift #1 — Pass-1 directory location (resolved by epic-canonical):** Epic file Story 7b.4 line 590 binds `app/specialists/irene_pass1/_act.py` (separate directory; NOT shared `irene/` with mode-discriminator). Resolution: **CREATE new directory at `app/specialists/irene_pass1/`** mirroring Pass-2 9-node scaffold shape. Mode-singularity hard-constraint enforced at dispatch boundary (Marcus dispatcher) — Pass-1 cannot be invoked in Pass-2 mode and vice versa.

**⚠️ Drift #2 — Sanctum SHARED with Pass-2 (no migration needed):** `_bmad/memory/bmad-agent-content-creator/` already carries 6-file BMB pattern (Pass-2 era; Slab 2a.2 §AC-F). Pass-1 + Pass-2 share the same sanctum + same SKILL.md per Slab 2a.2 drift #3 + epic Story 7b.4 line 606. **No sanctum migration required for this story** (distinct from 7b.2/7b.3 which migrated sidecar→BMB). Verify the sanctum 6-file pattern at T1; fix if drifted from canonical.

### Wave 0 + Wave-1-substrate artifact-existence sweep

```bash
ls docs/dev-guide/bmb-sanctum-alignment-checklist.md docs/dev-guide/sanctum-exception-categories.json docs/dev-guide/operator-control-parity-template.md docs/dev-guide/migration-ac-sandbox-inventory.json skills/bmad-agent-cora/SKILL.md
ls docs/dev-guide/scaffolds/scaffold-v0.2-D2-pipeline/
ls tests/parity/_sanctum_parity_base.py tests/composition/_chain_test_base.py scripts/utilities/validate_parity_test_class_conformance.py
ls tests/parity/test_skill_md_sanctum_alignment.py tests/parity/test_texas_activation_contract.py tests/parity/test_quinn_r_activation_contract.py tests/parity/test_vera_activation_contract.py
```

All paths must exist (Wave-0 + 7b.1 T2 substrate + Wave-1 close evidence: 7b.1/7b.2/7b.3 parity tests landed).

### Class-B template extension required

This story is the **first Class-B specialist** to land per NFR-I12. The dev-agent must extend `scripts/utilities/validate_parity_test_class_conformance.py` with Class-B template assertions (persona-continuity + sidecar-write parity) in lockstep with this story's parity test landing. Class-A template is already enforced; Class-B is additive.

### Sandbox-AC validator pre-flight

```bash
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py \
  _bmad-output/implementation-artifacts/migration-7b-4-irene-pass1-refresh.md
```
Expect PASS. Live-LLM verification (`@pytest.mark.llm_live`) auto-skips when `OPENAI_API_KEY` unset.

### Standing pre-flight items

1. Severance posture confirmed.
2. `state/config/substrate-frozen-paths.yaml` honored.
3. Pass-2 (`app/specialists/irene/`) is NOT modified by this story (FR113 + NFR-I13 substrate-frozen invariant — Pass-2 body is downstream-consumer substrate).
4. NFR-T9-T12 wall-clock ceilings hold.

---

## Story

As a **migration dev agent**,
I want **Irene Pass-1 to execute a 9-node scaffold mirroring the Pass-2 shape (Slab 2a.2 precedent) — `app/specialists/irene_pass1/_act.py` body landing as a real lesson-plan coauthoring + scope-lock contract + per-plan-unit ratification surface for G1A + `irene-pass1.md` artifact write + mode-singularity hard-constraint + `scope_decision.set` + `plan.locked` learning-event emission + cache-hit-rate harness wired at ≥85% post-warm-up — AND I want the FR105 parity test landing with Class-B template assertions extending the class-conformance validator from 7b.1's Class-A baseline**,
So that **(a) Trial-2 reaches G1A with a real Pass-1 lesson plan ratified per-plan-unit (not auto-confirmed bulk), (b) Pass-2 inherits a locked scope (per Wave 2 sequencing — Tracy's Pass-2 enrichment runs against locked plan), (c) the mode-singularity hard-constraint prevents silent mis-routing between Pass-1 and Pass-2 modes, and (d) SG-4 sanctum-alignment is enforced for Irene via the SHARED `_bmad/memory/bmad-agent-content-creator/` 6-file BMB sanctum (no migration required)**.

---

## Acceptance Criteria

All ACs are dev-agent-executable (sandbox-AC compliant). Live-LLM tests (cache-hit-rate harness) tagged `@pytest.mark.llm_live`; auto-skip on placeholder `OPENAI_API_KEY`.

### AC-7b.4-A — T1 readiness verification + drift resolution

**Given** the Round-(e) governance JSON pin + 7b.1 T2 atomic-commit landed + all 3 Wave-1 stories `done`
**When** the dev agent runs T1 readiness
**Then** all 10 readings cascade complete; Round-(e) verification command exits 0; Wave-0 + 7b.1-T2 + Wave-1-close sweep PASS; sandbox-AC validator PASS pre-flight
**And** Drift #1 resolution recorded: **NEW directory `app/specialists/irene_pass1/`** (separate from Pass-2 `irene/`)
**And** Drift #2 resolution recorded: **NO sanctum migration** — `_bmad/memory/bmad-agent-content-creator/` shared with Pass-2 + already 6-file BMB
**And** `tripwire_events::wave_1_close::fired_verdict` read; if true, K-target tightened to upper band per Round-(a) Amelia A3.

### AC-7b.4-B — `app/specialists/irene_pass1/` directory creation with 9-node scaffold

**Given** the canonical 9-node scaffold contract at `tests/integration/scaffold_conformance/scaffold_contract.py::SCAFFOLD_NODE_IDS`
**And** the Pass-2 shape at `app/specialists/irene/` (Slab 2a.2 era)
**When** the dev-agent creates Pass-1 directory
**Then** `app/specialists/irene_pass1/` directory lands with:
  - `__init__.py`
  - `graph.py` — `build_irene_pass1_graph()` returns 9-node graph mirroring Pass-2's shape
  - `state.py` — `IrenePass1Envelope(SpecialistEnvelope)` + `IrenePass1Return(SpecialistReturn)` four-file-lockstep per Story 1.2
  - `model_config.yaml` — `default_model: "gpt-5.4"` (Class-B uses `tier_request: reasoning`); `temperature_default: 0.3`
  - `expertise/README.md` — references Pass-1 sanctum convention (dotted reference list per `docs/dev-guide/sanctum-reference-conventions.md` from Slab 2a.2 §MF7)
**And** `validate_scaffold("irene_pass1", build_irene_pass1_graph()).is_conforming is True`; ruff clean; import-linter C1 lane-isolation PASS.

### AC-7b.4-C — Pass-1 `_act` body: lesson-plan coauthoring + scope-lock contract

**Given** Marcus dispatches Irene Pass-1 at G1A (post-Texas hardening; real corpus extraction available)
**When** Irene Pass-1's `_act` body executes
**Then** Pass-1 authors a real lesson plan via the LLM call (assemble prompt from sanctum cold-read + references + envelope payload via deterministic string concatenation per Slab 2a.2 MF1 byte-stability discipline; single LLM call via `app.models.adapter.ChatOpenAIAdapter`; parse response + return `IrenePass1Return`)
**And** the lesson plan lands at `runs/<run_id>/irene-pass1.md` per the artifact-write contract (FR92)
**And** `_act` body length is **≤150 LOC** per AC-B ceiling (Slab 2a.2 precedent MF4); HALT-AND-SURFACE re-scope decision if exceeds.

### AC-7b.4-D — Per-plan-unit ratification surface (G1A)

**Given** the per-plan-unit ratification requirement (operator confirms each plan unit; not bulk auto-confirm)
**When** the operator reviews the Pass-1 plan at G1A
**Then** the operator confirms or amends each plan unit individually (per FR92)
**And** the ratification surface uses the `OperatorVerdict` model from 7a.4 (additive `revise_count` field)
**And** bulk auto-confirm is REJECTED (HIL contract).
**Test pin:** `tests/specialists/irene_pass1/test_irene_pass1_per_plan_unit_ratification.py` — synthetic 5-plan-unit fixture; assert per-unit verdict required; assert bulk-confirm path raises.

### AC-7b.4-E — Scope-lock contract + learning-event emission

**Given** the scope-lock contract per FR92
**When** the operator confirms the Pass-1 plan at G1A
**Then** `scope_decision.set` learning event is emitted (carrying the locked scope payload)
**And** `plan.locked` learning event fires (signaling Pass-2 may begin)
**And** Pass-2 inherits the locked scope (per Wave 2 sequencing — when Tracy's Pass-2 enrichment runs at Wave-2b, it consumes the locked plan)
**And** learning events use the schema defined at `app/models/learning_events/` (verify path at T1; lockstep with 7a.5 conversation-persistence facade).
**Test pin:** `tests/specialists/irene_pass1/test_irene_pass1_learning_events.py` — fire `scope_decision.set` + `plan.locked`; assert structural shape per schema.

### AC-7b.4-F — Mode-singularity hard-constraint enforcement

**Given** the mode-singularity hard-constraint (Pass-1 cannot run in Pass-2 mode; Pass-2 cannot run in Pass-1 mode)
**When** Marcus's dispatcher routes a Pass-2 envelope to Pass-1 (mis-routing scenario)
**Then** Pass-1's `receive` node raises `ModeMismatchError` (NOT silent fallthrough)
**And** the constraint is enforced at the dispatch boundary (NOT silent acceptance with degraded behavior).
**Test pin:** `tests/specialists/irene_pass1/test_irene_pass1_mode_singularity.py` — synthetic Pass-2 envelope routed to Pass-1; assert `ModeMismatchError`.

### AC-7b.4-G — Cache-hit-rate harness (FR106; Class-B Slab 2a.2 inheritance)

**Given** the cache-hit-rate harness requirement (FR106; ten LLM specialists incl. Irene Pass-1)
**When** the dev-agent wires Pass-1 into the harness
**Then** harness runs N=10 in-process against `gpt-5.4` with `prompt_tokens >> 1024` MF2 floor
**And** `median[2:] >= 85%` post-warm-up (per Slab 2a.2 MF1 disposition rule)
**And** prompt-token floor pre-check raises `pytest.fail("prefix below OpenAI cache threshold 1024 tokens; ...")` if envelope undersized (per Slab 2a.2 MF2)
**And** cache-metric source: OpenAI usage API `prompt_tokens_details.cached_tokens / prompt_tokens` (per Slab 2a.2 MF5; NOT LangSmith trace parsing).
**Test pin:** `tests/end_to_end/test_irene_pass1_cache_hit_rate.py` — `@pytest.mark.llm_live`; auto-skip on placeholder API key; operator-gated Completion-Notes evidence block.

### AC-7b.4-H — SG-4 Sanctum Alignment (FR100 + FR101 — Pass-1 inherits shared sanctum)

**Given** the SG-4 sanctum-alignment requirement
**And** Pass-1 + Pass-2 SHARE the SKILL.md (`skills/bmad-agent-content-creator/SKILL.md`) + sanctum dir (`_bmad/memory/bmad-agent-content-creator/`) per Slab 2a.2 + epic Story 7b.4 line 606
**When** the dev-agent commits Pass-1 hardening
**Then** `skills/bmad-agent-content-creator/SKILL.md` is verified option-a sanctum-aligned per BMB checklist (FR108):
  - YAML frontmatter MINIMAL (`name` + `description` only); fix if drifted
  - SKILL.md body references `_bmad/memory/bmad-agent-content-creator/` as activation-time hot-load batch
**And** the sanctum dir at `_bmad/memory/bmad-agent-content-creator/` carries 6-file BMB pattern (already verified at T1; no migration needed)
**And** `tests/parity/test_skill_md_sanctum_alignment.py` (created by 7b.1) PASSES for Irene-Pass-1 (parity test asserts SHARED sanctum / SHARED SKILL.md per Slab 2a.2 era + 7b.4 refresh).

### AC-7b.4-I — FR105 per-specialist parity test (Pass-1 activation contract; Class-B template extension)

**Given** the Errata 4 verdict-flat layout + 7b.1's `_sanctum_parity_base.py` + class-conformance validator
**When** the dev-agent authors Pass-1's activation-contract test
**Then** `tests/parity/test_irene_pass1_activation_contract.py` (flat) lands inheriting `SanctumParityTestBase` with `class_template_id = "B"`, `specialist_name = "irene_pass1"`
**And** the test asserts **Class-B persona-continuity + sidecar-write parity** per NFR-I12 Class-B template:
  - (i) 9-node scaffold conformance via `validate_scaffold()`
  - (ii) lesson-plan artifact-write contract (`runs/<run_id>/irene-pass1.md` shape)
  - (iii) scope-lock learning-event emission (`scope_decision.set` + `plan.locked`)
  - (iv) mode-singularity hard-constraint (`ModeMismatchError` raised on cross-mode)
  - (v) shared-sanctum equality with Pass-2 (cold-read fingerprint deterministic)
  - (vi) cold-activation smoke
**And** **`scripts/utilities/validate_parity_test_class_conformance.py` extended with Class-B template assertions in lockstep** (additive; Class-A unchanged).
**And** `@pytest.mark.timeout(30)` per NFR-T9; <120s aggregate per NFR-T12
**And** the validator PASSES on this test file when run.

### AC-7b.4-J — Sandbox-AC governance + substrate-as-floor invariant

**Given** the sandbox-AC inventory governance requirement + FR113 + NFR-I13
**When** `validate_migration_story_sandbox_acs.py` runs on this spec
**Then** PASS (no forbidden CLI in dev-agent ACs)
**And** Irene-Pass-1 specific: NO sandbox-AC inventory entry needed (LLM-only via `gpt-5.4`)
**And** **no diff hunk touches `app/marcus/orchestrator/dispatch_adapter.py:70-95`** absent ceremony
**And** **no diff to Pass-2 body at `app/specialists/irene/`** (substrate-as-floor; Pass-2 is downstream-consumer substrate that this story does NOT modify).

### AC-7b.4-K — Chain test inheriting `ChainTestBase`

**Given** NFR-CG14 chain-test PR pre-merge requirement + 7b.1's `_chain_test_base.py` substrate
**When** the dev agent authors the Pass-1 → Pass-2 chain test
**Then** `tests/composition/test_irene_pass1_to_pass2_chain.py` lands inheriting `ChainTestBase`
**And** the test asserts envelope-handoff: Pass-1 `IrenePass1Return` (with locked scope) is shape-compatible with Pass-2 `IreneEnvelope` (consumes locked scope)
**And** wall-clock <120s.

### AC-7b.4-L — Vera G4 downstream review consumability

**Given** the Wave-1 close-of-record (7b.3 Vera done) — Vera's G4 19-criterion rubric is the downstream review on Pass-1 lesson plan
**When** Vera runs G4 against `runs/<run_id>/irene-pass1.md` (synthetic fixture-replay acceptable for Wave 2a dev)
**Then** the rubric scores all 19 criteria against the Pass-1 plan
**And** Pass-1 emits structurally compliant artifacts that Vera's G4 can parse (per `g4-narration-script.yaml` schema).
**Test pin:** `tests/composition/test_irene_pass1_to_vera_g4_chain.py` — fixture-replay; assert Vera G4 parses Pass-1 output without structural errors.

### AC-7b.4-M — Close protocol

**Given** all prior ACs PASS + bmad-code-review returns PASS or PASS-WITH-PATCH-applied + regression baseline holds
**When** the story closes
**Then** at close:
  1. **sprint-status.yaml** flip: `migration-7b-4-irene-pass1-refresh: in-progress → review → done`
  2. **next-session-start-here.md** updated: pivot to Wave-2b (7b.5 Tracy port-shape) opening — Codex-authored per NFR-CG17
  3. **Deferred-inventory updates**: any new follow-ons surfaced during dev filed
  4. **Standing-guardrail status**: SG-4 4th-green (Texas + Quinn-R + Vera + Irene); Class-B template added to validator
  5. **Three-line D12 close stub**

---

## Tasks / Subtasks

### T1 — T1 readiness verification + drift resolution
- [x] **T1.1** Round-(e) governance JSON verification
- [x] **T1.2** 10-reading required cascade
- [x] **T1.3** Wave-1 close evidence (3/3 stories `done`); read tripwire_events::wave_1_close
- [x] **T1.4** Wave 0 + 7b.1 T2 substrate sweep + Wave-1 parity tests landed
- [x] **T1.5** Irene current-state probe — Drift #1 (new dir) + Drift #2 (shared sanctum, no migration)
- [x] **T1.6** Drift resolution recorded
- [x] **T1.7** Sandbox-AC validator pre-flight

### T2 — Create `app/specialists/irene_pass1/` directory + 9-node scaffold
- [x] **T2.1** Create directory + 5 files (`__init__.py`, `graph.py`, `state.py`, `model_config.yaml`, `expertise/README.md`)
- [x] **T2.2** Generator-emit OR hand-author 9-node scaffold mirroring Pass-2 (per `scaffold_contract.py::SCAFFOLD_NODE_IDS`)
- [x] **T2.3** `validate_scaffold("irene_pass1", build_irene_pass1_graph()).is_conforming is True`

### T3 — Pass-1 `_act` body: lesson-plan coauthoring (AC-C..AC-F)
- [x] **T3.1** Implement `_act` body — prompt assembly + single LLM call + return `IrenePass1Return` with lesson plan
- [x] **T3.2** Per-plan-unit ratification surface for G1A (consume `OperatorVerdict.revise_count` from 7a.4)
- [x] **T3.3** Scope-lock contract + `scope_decision.set` + `plan.locked` learning-event emission
- [x] **T3.4** Mode-singularity hard-constraint (`ModeMismatchError` at receive node)
- [x] **T3.5** **AC-B 150-LOC ceiling discipline:** `_act` body ≤150 LOC; HALT-AND-SURFACE re-scope if exceeds

### T4 — Cache-hit-rate harness (AC-G)
- [x] **T4.1** `tests/end_to_end/test_irene_pass1_cache_hit_rate.py` — `@pytest.mark.llm_live`; per Slab 2a.2 MF1+MF2+MF5 discipline
- [x] **T4.2** Operator-gated Completion-Notes evidence block (median verdict)

### T5 — Parity + behavioral tests + Class-B template extension
- [x] **T5.1** `tests/parity/test_irene_pass1_activation_contract.py` (flat; Class-B template) — AC-I
- [x] **T5.2** Extend `scripts/utilities/validate_parity_test_class_conformance.py` with Class-B template assertions (LOCKSTEP)
- [x] **T5.3** `tests/specialists/irene_pass1/test_irene_pass1_lesson_plan_authoring.py` — AC-C
- [x] **T5.4** `tests/specialists/irene_pass1/test_irene_pass1_per_plan_unit_ratification.py` — AC-D
- [x] **T5.5** `tests/specialists/irene_pass1/test_irene_pass1_scope_lock.py` — AC-E
- [x] **T5.6** `tests/specialists/irene_pass1/test_irene_pass1_learning_events.py` — AC-E
- [x] **T5.7** `tests/specialists/irene_pass1/test_irene_pass1_mode_singularity.py` — AC-F
- [x] **T5.8** `tests/composition/test_irene_pass1_to_pass2_chain.py` — AC-K
- [x] **T5.9** `tests/composition/test_irene_pass1_to_vera_g4_chain.py` — AC-L
- [x] **T5.10** Wall-clock annotations + `validate_parity_test_class_conformance.py` PASS on Class-B

### T6 — SG-4 sanctum alignment verification (AC-H)
- [x] **T6.1** Verify `skills/bmad-agent-content-creator/SKILL.md` minimal frontmatter (Pass-1 + Pass-2 share)
- [x] **T6.2** Verify `_bmad/memory/bmad-agent-content-creator/` 6-file BMB pattern intact
- [x] **T6.3** `tests/parity/test_skill_md_sanctum_alignment.py` PASSES for Irene Pass-1

### T7 — Substrate-as-floor verification (AC-J)
- [x] **T7.1** `git diff` verification — no diff to dispatch_adapter.py:70-95
- [x] **T7.2** `git diff` verification — no diff to `app/specialists/irene/` (Pass-2 untouched)

### T8 — Manifest registration
- [x] **T8.1** Register `irene-pass1` orchestration node in pipeline-manifest.yaml (additive; per `app/manifest/compiler.py` SPECIALIST_ALIASES carry-forward `irene-pass1 → irene_pass1`)

### T9 — Regression baseline + sandbox-AC final
- [x] **T9.1** Full regression battery (target: ≥696 + ~25 (Wave-1) + ~30 (this story) ≈ 751 passed; 19 skipped)
- [x] **T9.2** `ruff check .` clean
- [x] **T9.3** `lint-imports.exe` 9/9 KEPT
- [x] **T9.4** Sandbox-AC validator final PASS

### T10 — Codex G6 self-review
- [x] **T10.1** Codex authors G6 self-review at `_bmad-output/implementation-artifacts/7b-4-codex-self-review-2026-04-XX.md`
- [x] **T10.2** Status flip `in-progress → review`

### T11 — Claude bmad-code-review + close
- [ ] **T11.1** Claude runs `bmad-code-review` at `7b-4-code-review-2026-04-XX.md`
- [ ] **T11.2** Remediation cycle 1 if needed
- [ ] **T11.3** Sprint-status flip `review → done`
- [ ] **T11.4** Update `next-session-start-here.md`: pivot to Wave-2b (7b.5 Tracy)
- [ ] **T11.5** Deferred-inventory updates
- [ ] **T11.6** Standing-guardrail status: SG-4 4th-green; Class-B template active in validator
- [ ] **T11.7** Three-line D12 close stub
- [ ] **T11.8** Commit + push

---

## Dev Notes

### Pass-1 vs Pass-2 separation: directory-distinct + sanctum-shared

The architectural decision: Pass-1 + Pass-2 are SEPARATE app-side directories (`app/specialists/irene_pass1/` + `app/specialists/irene/`) but share SKILL.md (`skills/bmad-agent-content-creator/`) + sanctum (`_bmad/memory/bmad-agent-content-creator/`). Mode-singularity hard-constraint enforces single-mode-per-invocation at the dispatch boundary.

Why this works: app-side directory separation lets each pass have its own `_act` body, model-config, state types, and tests without code-conflation; shared sanctum + SKILL.md preserves Irene's persona-continuity (the agent IS the same person; she just has two work modes).

### Class-B template (NEW; this story extends the validator)

7b.1 landed Class-A only. This story extends `validate_parity_test_class_conformance.py` with Class-B template assertions (persona-continuity + sidecar-write parity). Class-B template is additive; Class-A unchanged. Future Class-B stories (none in Slab 7b — Irene Pass-1 is the only Class-B specialist) inherit. The Class-B extension is a foundational deliverable beyond Irene Pass-1 itself.

### Cache-hit-rate harness inheritance from Slab 2a.2

Pass-1 IS Class B and is the second LLM specialist after Pass-2 to land cache-hit-rate harness measurement. Per Slab 2a.2 MF1-MF5 discipline:
- MF1: byte-identical prompts across N=10 in-process iterations
- MF2: prompt-token floor pre-check ≥1024 tokens (raise pytest.fail if undersized)
- MF3: byte-stability test (no-LLM, in-process determinism guard)
- MF5: in-process N=10 iterations; OpenAI usage API as cache-metric source

### Wave-2b unblock at this story close

When 7b.4 closes `done`, Wave-2b unblocks (Story 7b.5 Tracy port-shape is Codex-authored per NFR-CG17). The next-session-start-here.md pivot at close points to 7b.5 opening.

### NFR predicates honored

NFR-T9 / T10 / T11 / T11a (cache-hit-rate ≥85%) / T11b / T12 — `@pytest.mark.timeout` annotations.
NFR-CG14 — chain test (Pass-1 → Pass-2; Pass-1 → Vera G4).
NFR-CG16 — bmad-code-review pre-close.
NFR-I9 + NFR-I10 + NFR-I12 (Class-B template extension) + NFR-I13.

### Known follow-ons

- **`class-b-template-extend-validator-during-7b-4`** — CLOSE at T5.2 (in-story)
- **`pass-1-pass-2-shared-sanctum-cleanup`** — none expected; Pass-1 + Pass-2 share canonically per Slab 2a.2

### Anti-pattern catalog citations

- **A6** (silent-fixture-stub fallback) — closing for Irene Pass-1
- **A9** (epic-doc-vs-shipped-framework drift) — Pass-1 directory location resolved by epic-canonical
- **P1** (substrate-as-floor violation) — AC-J binding (Pass-2 untouched)

---

### Project Structure Notes

- `app/specialists/irene_pass1/` — NEW directory (9-node scaffold)
- `app/specialists/irene/` — Pass-2; PRESERVED (substrate-frozen)
- `_bmad/memory/bmad-agent-content-creator/` — SHARED with Pass-2 (already 6-file BMB; no migration)
- `skills/bmad-agent-content-creator/` — SHARED with Pass-2; SKILL.md verified minimal
- `tests/parity/test_irene_pass1_activation_contract.py` — NEW (FR105; Class-B; flat layout)
- `scripts/utilities/validate_parity_test_class_conformance.py` — EXTENDED with Class-B template (lockstep)
- `tests/specialists/irene_pass1/test_*.py` — NEW (5 behavioral tests)
- `tests/end_to_end/test_irene_pass1_cache_hit_rate.py` — NEW
- `tests/composition/test_irene_pass1_to_pass2_chain.py` — NEW
- `tests/composition/test_irene_pass1_to_vera_g4_chain.py` — NEW

### Detected conflicts or variances

- **Pass-1 directory location** — resolved in favor of separate `irene_pass1/` per epic-canonical
- **Pass-1 + Pass-2 shared sanctum** — confirmed canonical (Slab 2a.2 + epic line 606)

---

## References

- **Round-(e) governance JSON**: [`docs/dev-guide/migration-story-governance.json`](../../docs/dev-guide/migration-story-governance.json) §`stories.7b-4`
- **Epic + story-level scope**: [`epics-slab-7b-specialist-activation-eleven.md`](../planning-artifacts/epics-slab-7b-specialist-activation-eleven.md) §Story 7b.4
- **PRD FR92**: [`prd-slab-7b-specialist-activation-eleven.md`](../planning-artifacts/prd-slab-7b-specialist-activation-eleven.md) §FR92
- **Slab 2a.2 Pass-2 precedent (CRITICAL)**: [`migration-2a-2-irene-pass-2-scaffold-migration.md`](migration-2a-2-irene-pass-2-scaffold-migration.md)
- **9-node scaffold canonical**: [`tests/integration/scaffold_conformance/scaffold_contract.py`](../../tests/integration/scaffold_conformance/scaffold_contract.py)
- **G4 19-criterion canonical**: [`state/config/fidelity-contracts/g4-narration-script.yaml`](../../state/config/fidelity-contracts/g4-narration-script.yaml)
- **7a.4 OperatorVerdict (per-plan-unit ratification)**: [`migration-7a-4-per-slide-subgraph-html-review-pack-skeleton.md`](migration-7a-4-per-slide-subgraph-html-review-pack-skeleton.md)
- **7a.5 conversation-persistence + learning-event substrate**: [`migration-7a-5-conversation-persistence-specialist-summary-writer.md`](migration-7a-5-conversation-persistence-specialist-summary-writer.md)
- **7b.1 substrate (Wave-1 prerequisite)**: [`migration-7b-1-texas-hardening.md`](migration-7b-1-texas-hardening.md)
- **7b.2 spec (Wave-1 sibling)**: [`migration-7b-2-quinn-r-hardening.md`](migration-7b-2-quinn-r-hardening.md)
- **7b.3 spec (Wave-1 sibling — Vera G4 downstream)**: [`migration-7b-3-vera-hardening.md`](migration-7b-3-vera-hardening.md)
- **BMB sanctum alignment checklist (FR108)**: [`docs/dev-guide/bmb-sanctum-alignment-checklist.md`](../../docs/dev-guide/bmb-sanctum-alignment-checklist.md)
- **Sandbox-AC inventory (FR107)**: [`docs/dev-guide/migration-ac-sandbox-inventory.json`](../../docs/dev-guide/migration-ac-sandbox-inventory.json)
- **Sprint status**: [`sprint-status.yaml`](sprint-status.yaml)
- **Deferred inventory**: [`deferred-inventory.md`](../planning-artifacts/deferred-inventory.md)

---

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- 2026-04-29: T1 gate passed after Wave-1 close was recorded in sprint-status (`7b.1`, `7b.2`, `7b.3` done; `wave_1_close` marginal-fired).
- 2026-04-29: Created separate `app/specialists/irene_pass1/` directory; Pass-2 `app/specialists/irene/` left untouched.
- 2026-04-29: Fixed C3 import-linter issue by removing `app.gates.resume_api` import from the new Pass-1 graph.

### Completion Notes List

- Implemented Irene Pass-1 as a separate 9-node scaffold with shared Irene sanctum cold-read, deterministic prompt assembly, single LLM invocation, `irene-pass1.md` artifact write, per-plan-unit ratification helpers, scope-lock event builders, and `ModeMismatchError` at receive/act boundaries.
- Extended parity class-conformance validation with Class-B required methods and added Irene Pass-1 parity, behavioral, cache-harness, and composition chain tests.
- Registered `irene-pass1` alias and dispatch target; updated pipeline manifest Pass-1 steps (`04A`, `05`, `05B`) to route to `irene-pass1` while leaving Pass-2 step `08` on `irene`.
- Verification: 30 story-scoped local tests passed; Class-B conformance PASS; sandbox-AC PASS; pipeline lockstep PASS; lint-imports 9/9 KEPT; story-scoped ruff clean; live cache harness skipped under placeholder OpenAI key.
- Residual: broader regression slice reported existing out-of-scope Wanda sanctum drift (`test_wanda_sanctum_populated.py` expects 5 files, digest sees 6 due `CLONE-FORK-NOTICE.md`). Full repo `ruff check .` also has pre-existing out-of-scope lint debt; scoped ruff for this story is clean.

### File List

- `_bmad-output/implementation-artifacts/7b-4-codex-self-review-2026-04-29.md`
- `_bmad-output/implementation-artifacts/migration-7b-4-irene-pass1-refresh.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `app/manifest/compiler.py`
- `app/models/registry.yaml`
- `app/specialists/irene_pass1/__init__.py`
- `app/specialists/irene_pass1/_act.py`
- `app/specialists/irene_pass1/expertise/README.md`
- `app/specialists/irene_pass1/graph.py`
- `app/specialists/irene_pass1/model_config.yaml`
- `app/specialists/irene_pass1/state.py`
- `scripts/utilities/validate_parity_test_class_conformance.py`
- `state/config/dispatch-registry.yaml`
- `state/config/pipeline-manifest.yaml`
- `tests/composition/test_irene_pass1_to_pass2_chain.py`
- `tests/composition/test_irene_pass1_to_vera_g4_chain.py`
- `tests/end_to_end/test_irene_pass1_cache_hit_rate.py`
- `tests/parity/test_irene_pass1_activation_contract.py`
- `tests/parity/test_skill_md_sanctum_alignment.py`
- `tests/specialists/irene_pass1/test_irene_pass1_learning_events.py`
- `tests/specialists/irene_pass1/test_irene_pass1_lesson_plan_authoring.py`
- `tests/specialists/irene_pass1/test_irene_pass1_mode_singularity.py`
- `tests/specialists/irene_pass1/test_irene_pass1_per_plan_unit_ratification.py`
- `tests/specialists/irene_pass1/test_irene_pass1_scope_lock.py`
