# Migration Story 7b.11: Compositor Greenfield (Class-D2 Sidecar Variant) — Deterministic Assembly Pipeline

**Status:** done
**Sprint key:** `migration-7b-11-compositor-greenfield`
**Epic:** Slab 7b Specialist Body Activation — `epic-slab-7b-specialist-activation-eleven`. **Wave 5b** (Class-D2 pipeline-greenfield, sidecar variant per D20; parallelizable with Wave 5a 7b.10 Dan AFTER Waves 1-3 closed; Claude-authored spec / Codex dev per D21).
**Pts:** 5 | **Gate:** **single (DEFAULT) → dual (CONDITIONAL via Round-(e) E1 binding-hard `conditional_dual_gate_escalation` at pre-T1 K-projection >4.0K)** | **K-target:** ~1.5× (target ~40 tests / floor ~30; ~3.5K LOC; **Round-(e) E6 k_contract tripwire 4.0K → escalate_to_dual_gate (mandatory; binding=hard)**).
**Author:** **Claude** spec / **Codex** dev. **Review:** **Claude** T11 `bmad-code-review`.
**Wave-5b precondition:** ALL Waves 1-3 stories `done` per R8 Winston-amendment (7b.1+7b.2+7b.3+7b.4+7b.5+7b.6+7b.7+7b.8 all `done` in `sprint-status.yaml`); 7b.9 Wave 4 `done` is preferred but not strict precondition.

---

## Round-(e) Governance Inheritance

Round-(e) freeze landed 2026-04-29. Load-bearing for 7b.11:

- **E1 binding-hard `conditional_dual_gate_escalation`:** trigger_condition = `pre_t1_k_projection_kloc > 4.0`; trigger_check_owner = dev-agent at story T1 (BEFORE any code is written); escalation_action = `story_gate_mode := dual-gate; record decision in _amendment_log + tripwire_escalation_record_path; downstream Gate-2 operator-witnessed ceremony added to story workflow`; binding = hard. **Dev-agent T1 K-projection >4K is a NON-DISCRETIONARY trigger; gate mode flips before any code is written.**
- **E6 k_contract block:** scope=Class-D2 sidecar variant per D20 + scaffold-v0.2-D2-pipeline (FR111) consumption + pipeline-determinism harness ≥99%; tripwire 4.0K → escalate_to_dual_gate (mandatory; binds to E1 above; Round-(b) Amelia B2 / Round-(c) C2 / Round-(e) E1 binding-hard chain).

**Class-D2 is EXEMPT from FR101.iv sanctum-path-equality clause per D20** (canonical first-class taxonomy bin; sidecar variant is intentional, NOT an exception).

**Class-D2 NOT subject to Class-C two-SKILL.md ratification** (Round-(f) party-mode ratified two-SKILL.md for Class-C specifically; D2 has its own scaffold-v0.2-D2-pipeline contract per FR111).

**T1 readiness verification command:**
```bash
.venv/Scripts/python.exe -c "import json; d = json.load(open('docs/dev-guide/migration-story-governance.json', encoding='utf-8')); entry = d['stories']['7b-11']; assert entry['k_contract']['tripwire_threshold_kloc'] == 4.0; assert entry['conditional_dual_gate_escalation']['binding'] == 'hard'; assert entry['conditional_dual_gate_escalation']['trigger_condition'].startswith('pre_t1_k_projection_kloc'); print('Round-(e) E1+E6 verified PASS for 7b-11')"
```

---

## T1 Readiness Block

### Required-readings cascade (10-reading)

1. **Round-(e) governance JSON** — `docs/dev-guide/migration-story-governance.json` §`stories.7b-11` (single-gate default; conditional_dual_gate_escalation binding=hard at K>4.0; k_contract tripwire 4.0K).
2. **Epic + story-level scope** — [`epics-slab-7b-specialist-activation-eleven.md`](../planning-artifacts/epics-slab-7b-specialist-activation-eleven.md) §Story 7b.11 (lines 932-987).
3. **PRD §FR99** — Compositor Class-D2 sidecar variant (canonical, NOT exception per D20); persona artifacts as sidecar with operational-metadata content (`contract.md` / `version.md` / `chronology.md` / `access-boundaries.md`); EXEMPT from FR101.iv sanctum-path-equality. **Pipeline-determinism harness ≥99%** (bytes-identical for sync-visuals; field-masked-hash for DESCRIPT-ASSEMBLY-GUIDE.md modulo {generated_at, run_id, build_timestamp}).
4. **PRD §FR111 + Wave 0 scaffold-v0.2-D2-pipeline (LANDED)** — [`docs/dev-guide/scaffolds/scaffold-v0.2-D2-pipeline/`](../../docs/dev-guide/scaffolds/scaffold-v0.2-D2-pipeline/). 7 files: `README.md` + `scaffold.yaml` + `field-mask.yaml` + 5 templates (`contract.md.template` + `version.md.template` + `chronology.md.template` + `access-boundaries.md.template` + `pipeline-determinism.md.template`). **Compositor is the seed exemplar for Class-D2; templates land here at first activation.**
5. **D17 Pipeline-determinism harness contract (per Slab 7b PRD)** — bytes-identical for sync-visuals (PNG localized stills + motion clips routed; output filename + bytes deterministic across runs given fixed inputs); field-masked-hash for DESCRIPT-ASSEMBLY-GUIDE.md modulo declared-nondeterministic fields per `field-mask.yaml`.
6. **Wave-1/2a/2b/3 close evidence** — verify all 8 prior body stories (7b.1-7b.8) `done` per R8 Winston-amendment hard precondition.
7. **7b.10 Dan parallel sibling (Wave 5a)** — [`migration-7b-10-dan-greenfield.md`](migration-7b-10-dan-greenfield.md). Wave 5a + 5b parallel; no direct binding between them.
8. **Class-A/B/C/C+ template precedents in validator** — `scripts/utilities/validate_parity_test_class_conformance.py` already supports A/B/C+/C; this story extends with **Class-D2 template** in lockstep with the parity test landing (LOCKSTEP foundational deliverable).
9. **Slab 7a 7a.5 conversation-persistence contract** — [`migration-7a-5-conversation-persistence-specialist-summary-writer.md`](migration-7a-5-conversation-persistence-specialist-summary-writer.md). Specialist-summary-writer integration at G3.
10. **CLAUDE.md** — §LangChain/LangGraph migration governance + §BMAD sprint governance + Round-(e) E1 binding-hard discipline.

### Compositor current-state probe + greenfield posture

```bash
ls app/specialists/compositor/ 2>/dev/null              # NOT YET PRESENT — greenfield body; this story creates
ls _bmad/memory/bmad-agent-compositor/ 2>/dev/null      # NOT YET PRESENT — sidecar greenfield (Class-D2 4-file operational-metadata pattern; per D20 NOT 6-file BMB persona)
ls _bmad/memory/compositor-sidecar/ 2>/dev/null         # NOT PRESENT
ls skills/bmad-agent-compositor/ 2>/dev/null            # NOT PRESENT
ls skills/compositor/                                   # SKILL.md + references/ + scripts/ (existing skill at non-bmad-agent-prefixed path; **CANONICAL SKILL.md per epic Story 7b.11 line 974**; NOT subject to Class-C two-SKILL.md convention)
ls docs/dev-guide/scaffolds/scaffold-v0.2-D2-pipeline/  # 7 files LANDED Wave 0; Compositor is first consumer
```

### Pre-T1 K-projection check (Round-(e) E1 binding-hard)

**BEFORE any code is written**, dev-agent estimates K-projection from spec scope:
- 9-node scaffold instantiation: ~400 LOC (template-driven from scaffold-v0.2-D2-pipeline)
- `_act.py` body (deterministic assembly pipeline; sync-visuals + DESCRIPT-ASSEMBLY-GUIDE regen): ~150 LOC (AC-B ceiling)
- Sidecar 4-file authoring: ~300 LOC (operational-metadata content per templates)
- Pipeline-determinism harness: ~500 LOC (bytes-identical comparison + field-masked-hash + ≥99% rate)
- Parity test (Class-D2 template): ~200 LOC + validator extension ~150 LOC
- Behavioral tests (sync-visuals + DESCRIPT-ASSEMBLY-GUIDE + determinism): ~600 LOC
- Chain tests (Compositor consumes Gary slides + Kira motion + Enrique audio + Wanda beds): ~400 LOC
- Operator-control parity row + NFR-CG15 Decision Log entry + scaffold-v0.2-D2-pipeline first-instance documentation: ~300 LOC
- **Estimated total: ~3.0-3.5K LOC** (under 4.0K threshold; single-gate default holds)

**If T1 K-projection trends ≥4.0K:** HALT; record `conditional_dual_gate_escalation` fired in Dev Agent Record + tripwire ledger; story flips dual-gate at story-open per Round-(e) E1 binding-hard. Operator-witnessed Gate-2 ceremony added to T11/T12.

### Wave 0 + 7b.1 substrate + Waves 1-3 closure sweep

```bash
# Wave 0 + 7b.1 substrate
ls docs/dev-guide/bmb-sanctum-alignment-checklist.md docs/dev-guide/sanctum-exception-categories.json docs/dev-guide/operator-control-parity-template.md docs/dev-guide/migration-ac-sandbox-inventory.json skills/bmad-agent-cora/SKILL.md
ls docs/dev-guide/scaffolds/scaffold-v0.2-D2-pipeline/  # 7 files
ls tests/parity/_sanctum_parity_base.py tests/composition/_chain_test_base.py scripts/utilities/validate_parity_test_class_conformance.py

# All 8 prior body stories closed (Waves 1-3; 7b.4 Wave-2a; 7b.5 Wave-2b; 7b.9 Wave-4 preferred)
.venv/Scripts/python.exe -c "
import yaml
d = yaml.safe_load(open('_bmad-output/implementation-artifacts/sprint-status.yaml', encoding='utf-8'))
done = lambda k: d['development_status'][k].startswith('done')
required = ['migration-7b-1-texas-hardening','migration-7b-2-quinn-r-hardening','migration-7b-3-vera-hardening','migration-7b-4-irene-pass1-refresh','migration-7b-5-tracy-port-shape-sidecar','migration-7b-6-gary-port-shape','migration-7b-7-kira-port-shape','migration-7b-8-enrique-port-shape']
assert all(done(k) for k in required), f'Waves 1-3 not fully closed: {[k for k in required if not done(k)]}'
print('Waves 1-3 fully closed; Wave-5b OK to open')
"

# A/B/C/C+ templates active in validator
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/  # PASS expected with 7+ activation contracts
```

### Sandbox-AC validator pre-flight

```bash
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py \
  _bmad-output/implementation-artifacts/migration-7b-11-compositor-greenfield.md
```
Expect PASS. Compositor is pipeline-deterministic (NO LLM call at the Compositor layer; NO third-party API; deterministic assembly only). NO sandbox-AC inventory entry needed.

### Standing pre-flight items

1. Severance posture confirmed.
2. `state/config/substrate-frozen-paths.yaml` honored — Compositor calls *across* the Marcus dispatcher boundary using existing dispatch APIs; **no diff to `app/marcus/orchestrator/dispatch_adapter.py:70-95`**.
3. Compositor is greenfield additive — no existing `app/specialists/compositor/` to preserve.
4. NFR-T9-T12 wall-clock ceilings hold.

---

## Story

As a **migration dev agent**,
I want **Compositor to be activated as the first Class-D2 specialist (canonical sidecar variant per D20) — `app/specialists/compositor/` greenfield directory consumes scaffold-v0.2-D2-pipeline (FR111; LANDED Wave 0) + sidecar at `_bmad/memory/bmad-agent-compositor/` with 4-file operational-metadata pattern (`contract.md` / `version.md` / `chronology.md` / `access-boundaries.md`) + `_act` body shaped as deterministic assembly pipeline (sync-visuals operation + DESCRIPT-ASSEMBLY-GUIDE.md regeneration; NO LLM call) + pipeline-determinism harness ≥99% rate + Class-D2 template extension to `validate_parity_test_class_conformance.py` (LOCKSTEP)**,
So that **(a) Trial-2 reaches G3 with a deterministic Compositor `DESCRIPT-ASSEMBLY-GUIDE.md` regenerated against real assets and the operator can hand off to Descript without per-run drift, (b) Compositor establishes Class-D2 as canonical first-class taxonomy bin (per D20; sidecar variant is the convention, not the exception), (c) the scaffold-v0.2-D2-pipeline becomes the substrate template for any future D2 specialists (none currently in Slab 7b), and (d) SG-4 sanctum-alignment is enforced via the Class-D2 template (FR101.iv exempt; sanctum-path-equality replaced by sidecar-variant contract per D20)**.

---

## Acceptance Criteria

All ACs are dev-agent-executable (sandbox-AC compliant). NO third-party API; NO LLM call at Compositor layer; deterministic assembly only.

### AC-7b.11-A — T1 readiness + K-projection check + drift resolution

**Given** Round-(e) E1 + E6 amendments + Waves 1-3 fully closed + Class-A/B/C/C+ templates active
**When** the dev agent runs T1 readiness
**Then** all 10 readings cascade complete; Round-(e) E1+E6 verification command exits 0; Wave-0 + 7b.1-T2 + Waves-1-3 sweep PASS; sandbox-AC validator PASS pre-flight
**And** **pre-T1 K-projection recorded** (estimated ~3.0-3.5K LOC; under 4.0K threshold → single-gate holds)
**And** if K-projection ≥4.0K: HALT-AND-SURFACE; record `conditional_dual_gate_escalation` fired; story flips dual-gate per Round-(e) E1 binding-hard
**And** Class-D2 sidecar variant (NOT 6-file BMB persona-continuity) acknowledged per D20.

### AC-7b.11-B — `app/specialists/compositor/` greenfield directory consuming scaffold-v0.2-D2-pipeline

**Given** the canonical 9-node scaffold contract + scaffold-v0.2-D2-pipeline (FR111; LANDED Wave 0)
**When** the dev-agent (Codex) creates Compositor's greenfield body
**Then** `app/specialists/compositor/` directory lands with:
  - `__init__.py`
  - `graph.py` — `build_compositor_graph()` returns 9-node scaffold per `SCAFFOLD_NODE_IDS` frozenset
  - `state.py` — `CompositorEnvelope(SpecialistEnvelope)` + `CompositorReturn(SpecialistReturn)` four-file-lockstep per Story 1.2
  - `model_config.yaml` — minimal (Compositor has NO LLM call; FR16 resolution-trail entry recorded at `_plan` per scaffold convention but chat handle never invoked at runtime)
  - `expertise/README.md` — references scaffold-v0.2-D2-pipeline templates per FR111 + sanctum dotted-reference convention
  - `_act.py` — bounded body (≤150 LOC AC-B ceiling) implementing the deterministic assembly pipeline
**And** `validate_scaffold("compositor", build_compositor_graph()).is_conforming is True`; ruff clean; import-linter C1 lane-isolation PASS.

### AC-7b.11-C — Class-D2 sidecar at canonical path with 4-file operational-metadata pattern

**Given** the Class-D2 sidecar variant per D20 + scaffold-v0.2-D2-pipeline templates
**When** the dev-agent authors Compositor's sidecar
**Then** `_bmad/memory/bmad-agent-compositor/` directory lands with EXACTLY 4 files (NOT 6-file BMB persona-continuity):
  - `contract.md` — operational contract (consume from `scaffold-v0.2-D2-pipeline/contract.md.template`)
  - `version.md` — version-pinning (consume from `version.md.template`)
  - `chronology.md` — pipeline-runs history (consume from `chronology.md.template`)
  - `access-boundaries.md` — read/write/deny zones (consume from `access-boundaries.md.template`; READ: `assembly-bundle/`, storyboard manifest, narration package; WRITE: `assembly-bundle/visuals/`, `assembly-bundle/motion/`, DESCRIPT-ASSEMBLY-GUIDE.md; DENY: `app/marcus/orchestrator/dispatch_adapter.py`)
**And** content is operational-metadata-shaped (NOT persona-continuity per D20; NO PERSONA.md / CREED.md / BOND.md / MEMORY.md / CAPABILITIES.md)
**And** `_bmad/memory/bmad-agent-compositor/` is EXEMPT from FR101.iv sanctum-path-equality clause per D20.

### AC-7b.11-D — Deterministic assembly pipeline `_act` body

**Given** Compositor dispatched at G3 (post-Gary slides + post-Kira motion + post-Enrique narration + post-Wanda audio beds; storyboard locked)
**When** Compositor's `_act` body executes
**Then** `app/specialists/compositor/_act.py` runs the deterministic assembly pipeline:
  - **sync-visuals operation:** localized PNG stills land at `[BUNDLE_PATH]/assembly-bundle/visuals/<slide_id>.png`; motion clips land at `[BUNDLE_PATH]/assembly-bundle/motion/<slide_id>.{mp4|webm}`. **Bytes-identical across runs given fixed inputs** (D17 H-Pipeline contract).
  - **DESCRIPT-ASSEMBLY-GUIDE.md regeneration:** assembly-guide regenerated with field-masked-hash determinism modulo `{generated_at, run_id, build_timestamp}` per R3 Amelia-amendment (per `field-mask.yaml` from scaffold-v0.2-D2-pipeline)
**And** **NO LLM call at the Compositor layer** (deterministic assembly only; FR16 resolution-trail entry recorded at `_plan` for substrate-contract preservation but chat handle never invoked)
**And** `_act` body length ≤150 LOC per AC-B ceiling.
**Test pin:** `tests/specialists/compositor/test_compositor_sync_visuals.py` — fixture-replay; assert bytes-identical output across 2 runs.

### AC-7b.11-E — Pipeline-determinism harness ≥99% rate (FR106 H-Pipeline)

**Given** the FR106 H-Pipeline contract (NOT cache-hit-rate; Class-D2 has NO LLM)
**When** the dev-agent wires Compositor into the harness
**Then** `tests/end_to_end/test_compositor_pipeline_determinism.py` runs N=10 iterations of Compositor's `_act` against fixture inputs:
  - **Bytes-identical for sync-visuals:** SHA256(visuals/<slide>.png) identical across all 10 runs
  - **Field-masked-hash for DESCRIPT-ASSEMBLY-GUIDE.md:** parse markdown; mask `{generated_at, run_id, build_timestamp}` per `field-mask.yaml`; SHA256 of masked content identical across all 10 runs
**And** ≥99% rate (9-of-10 minimum per H-Pipeline contract; documented per D17)
**And** failure is **hard-block** (no flake tolerance per D17); single failure → story HALTS; party-mode escalation required.

### AC-7b.11-F — `skills/compositor/SKILL.md` alignment per scaffold-v0.2-D2-pipeline contract

**Given** the SG-4 sanctum-alignment requirement + epic Story 7b.11 line 974 binding `skills/compositor/SKILL.md` (NOT bmad-agent-prefixed path; D2 first-class taxonomy bin)
**When** the dev-agent commits Compositor greenfield
**Then** `skills/compositor/SKILL.md` is verified aligned per scaffold-v0.2-D2-pipeline contract (FR111):
  - YAML frontmatter MINIMAL (`name: compositor` + persona-focused description)
  - Body references `_bmad/memory/bmad-agent-compositor/` 4-file operational-metadata sidecar as activation-time hot-load
  - **NO `# Sanctum exception` block required** per D20 (D2 first-class taxonomy bin)
**And** Class-D2 is **NOT subject to Class-C two-SKILL.md convention** (Round-(f) party-mode ratification was Class-C-specific).

### AC-7b.11-G — FR105 per-specialist parity test (Class-D2 template extension; LOCKSTEP)

**Given** the Errata 4 verdict-flat layout + 7b.1's `_sanctum_parity_base.py` substrate + A/B/C+/C templates active
**When** the dev-agent (Codex) authors Compositor's activation-contract test + extends the validator
**Then** `tests/parity/test_compositor_activation_contract.py` (flat) lands inheriting `SanctumParityTestBase` with `class_template_id = "D2"`, `specialist_name = "compositor"`
**And** the test asserts **Class-D2 pipeline-determinism + sidecar-operational-metadata parity** per NFR-I12 Class-D2 template:
  - (i) 9-node scaffold conformance via `validate_scaffold()`
  - (ii) 4-file operational-metadata sidecar pattern at `_bmad/memory/bmad-agent-compositor/` (NOT 6-file BMB; NOT 4-file Class-C+ persona pattern; specifically `contract.md` + `version.md` + `chronology.md` + `access-boundaries.md`)
  - (iii) NO LLM call at `_act` body (AST-scan; assert no `ChatOpenAIAdapter` invocation in `_act`)
  - (iv) NO third-party API client import (gamma/kling/elevenlabs/wondercraft); deterministic assembly only
  - (v) pipeline-determinism harness wired (`tests/end_to_end/test_compositor_pipeline_determinism.py` exists)
  - (vi) field-mask.yaml consumed for DESCRIPT-ASSEMBLY-GUIDE hash-mask
  - (vii) SKILL.md at `skills/compositor/SKILL.md` (NOT bmad-agent-prefixed; D2 convention)
  - (viii) sidecar EXEMPT from FR101.iv sanctum-path-equality clause per D20
  - (ix) cold-activation smoke
**And** **`scripts/utilities/validate_parity_test_class_conformance.py` extended with Class-D2 template assertions in lockstep** (additive; A + B + C+ + C unchanged).
**And** `@pytest.mark.timeout(30)` per NFR-T9; <120s aggregate per NFR-T12.

### AC-7b.11-H — Sandbox-AC governance + substrate-as-floor invariant (FR113 + NFR-I13)

**Given** sandbox-AC + FR113 + NFR-I13
**When** validator runs
**Then** PASS — Compositor has NO third-party API + NO LLM call; sandbox-AC scope is empty
**And** **no diff hunk touches `app/marcus/orchestrator/dispatch_adapter.py:70-95`** absent ceremony
**And** Compositor's greenfield is purely additive; integration with Marcus dispatcher uses existing dispatch APIs.

### AC-7b.11-I — Chain test inheriting `ChainTestBase` (4-input integration)

**Given** NFR-CG14 + 7b.1's `_chain_test_base.py` substrate
**And** Compositor consumes outputs from 4 upstream specialists at G3: Gary slides + Kira motion + Enrique narration + Wanda audio beds
**When** the dev agent authors the Compositor chain test
**Then** `tests/composition/test_compositor_4input_chain.py` lands inheriting `ChainTestBase`
**And** the test asserts envelope-handoff shape compatibility for 4-input integration (Gary's `gary_slide_output` + Kira's motion artifacts + Enrique's `assembly-bundle/audio/` + Wanda's `assembly-bundle/audio/beds/`) all consume cleanly into Compositor's pipeline-determinism harness inputs
**And** wall-clock <120s.

### AC-7b.11-J — 7a.5 specialist-summary-writer integration

**Given** the 7a.5 conversation-persistence contract
**When** Compositor `_act` completes (at G3)
**Then** Compositor invokes `summary_writer.emit_summary(specialist_id="compositor", gate_id="G3", payload=<verdict>)` per 7a.5 facade
**And** the summary file lands at `runs/<run_id>/specialist-summaries/compositor-g3-<timestamp>.md` with 15-25 line envelope.

### AC-7b.11-K — Composition Spec Decision Log entry (NFR-CG15)

**Given** the NFR-CG15 Decision Log entry requirement at `docs/dev-guide/composition-specification.md` §10
**When** Compositor lands the Class-D2 template + scaffold-v0.2-D2-pipeline first-instance
**Then** Decision Log entry filed:
  - Date: 2026-04-XX
  - Decision: Class-D2 sidecar variant (canonical per D20) — 4-file operational-metadata sidecar at `_bmad/memory/bmad-agent-compositor/` (NOT 6-file BMB persona); SKILL.md at `skills/compositor/SKILL.md` (NOT bmad-agent-prefixed); EXEMPT from FR101.iv sanctum-path-equality
  - Rationale: D2 pipeline-greenfield specialists are deterministic-assembly-only (no LLM, no third-party API); operational-metadata sidecar matches the role; persona-continuity is irrelevant
  - Inheritance: Compositor is the seed exemplar for Class-D2; future Class-D2 specialists (none in Slab 7b) inherit
  - Related artifacts: `validate_parity_test_class_conformance.py::Class-D2 template`; scaffold-v0.2-D2-pipeline (FR111)

### AC-7b.11-L — Operator-control parity table row (FR104)

**Given** the FR104 operator-control parity table at `docs/operator/legacy-vs-langgraph-control-parity.md`
**When** the dev-agent commits Compositor greenfield
**Then** a NEW row is added per FR110 template: legacy lever (Descript GUI + Manual file selection) → migrated lever (`run_compositor.py` CLI / Marcus G3 dispatch) → back-compat shim status → end-to-end test pointer (`tests/end_to_end/test_compositor_pipeline_determinism.py`).

### AC-7b.11-M — Wave-5b pre-T1 K-projection tripwire ledger (Round-(e) E1 + E6 record)

**Given** the Round-(e) E2 amendment landed `tripwire_events: []` schema slot at `sprint-status.yaml`
**And** Round-(e) E1 binding-hard `conditional_dual_gate_escalation` keyed to pre-T1 K-projection >4.0K
**When** this story's T1 K-projection check runs
**Then** the dev-agent appends a NEW `wave_5b_pre_t1_compositor` entry to `sprint-status.yaml::tripwire_events`:
```yaml
tripwire_events:
  # ... existing entries ...
  - tripwire_id: wave_5b_pre_t1_compositor
    story_owner: 7b-11
    fired_at: <YYYY-MM-DD>
    fired_verdict: <true|false>          # true if pre-T1 K-projection >4.0K
    measured_value:
      k_projection_kloc: <N.NN>
      method: "dev-agent T1 LOC estimate (per E1 binding-hard discipline; BEFORE any code written)"
    escalation_action_taken: <none|story_gate_mode_flipped_to_dual_gate_per_round_e_e1_binding_hard>
    decision_record_link: <links to story spec + dev-agent T1 readiness block>
```
**And** if `fired_verdict: true`, **gate mode flips dual-gate at story-open** per Round-(e) E1 binding-hard; operator-witnessed Gate-2 ceremony added to T11/T12 close.

### AC-7b.11-N — Close protocol

**Given** all prior ACs PASS + bmad-code-review returns PASS or PASS-WITH-PATCH-applied + regression baseline holds + pipeline-determinism harness ≥99% rate
**When** the story closes
**Then** at close:
  1. **sprint-status.yaml** flip: `migration-7b-11-compositor-greenfield: in-progress → review → done` (single-gate path) OR `review → operator-acceptance-pending → done` (dual-gate path with operator-witnessed Gate-2)
  2. **Wave-5b pre-T1 K-projection tripwire ledger entry** appended per AC-M
  3. **next-session-start-here.md** updated: pivot to Wave 6 (7b.12 integration; dual-gate; strict-last) opening
  4. **Deferred-inventory updates**: any new follow-ons surfaced filed; scaffold-v0.2-D2-pipeline first-instance documentation closed
  5. **Standing-guardrail status**: SG-4 GREEN for Compositor; **Class-D2 template active in validator**; Composition Spec §10 Decision Log entry filed; FR104 operator-control parity row added
  6. **Three-line D12 close stub** per Slab 7a precedent

---

## Tasks / Subtasks

### T1 — T1 readiness + K-projection check + drift resolution
- [x] **T1.1** Round-(e) E1+E6 governance JSON verification
- [x] **T1.2** 10-reading cascade
- [x] **T1.3** Waves 1-3 closed verification (8 stories `done`)
- [x] **T1.4** Wave 0 + 7b.1 substrate sweep + scaffold-v0.2-D2-pipeline 7-file presence
- [x] **T1.5** Compositor current-state probe (full greenfield)
- [x] **T1.6** **Pre-T1 K-projection check** — record estimate; if ≥4.0K, flip dual-gate per E1 binding-hard
- [x] **T1.7** Sandbox-AC validator pre-flight

### T2 — Class-D2 template extension to validator (LOCKSTEP foundational deliverable)
- [x] **T2.1** Extend `scripts/utilities/validate_parity_test_class_conformance.py` with Class-D2 template assertions (9 assertions per AC-G)
- [x] **T2.2** Verify validator PASSES on existing Class-A/B/C+/C tests post-extension

### T3 — Compositor greenfield body via scaffold-v0.2-D2-pipeline (AC-B)
- [x] **T3.1** Create `app/specialists/compositor/` directory + 6 files (`__init__.py`, `graph.py`, `state.py`, `model_config.yaml`, `expertise/README.md`, `_act.py`)
- [x] **T3.2** 9-node scaffold per `SCAFFOLD_NODE_IDS` (template-driven from scaffold-v0.2-D2-pipeline)
- [x] **T3.3** `validate_scaffold("compositor", build_compositor_graph()).is_conforming is True`

### T4 — Class-D2 sidecar 4-file authoring (AC-C)
- [x] **T4.1** Author `_bmad/memory/bmad-agent-compositor/contract.md` (consume from scaffold template)
- [x] **T4.2** Author `version.md` (consume template)
- [x] **T4.3** Author `chronology.md` (consume template)
- [x] **T4.4** Author `access-boundaries.md` (consume template; READ/WRITE/DENY zones documented)

### T5 — `_act.py` body: deterministic assembly pipeline (AC-D)
- [x] **T5.1** Implement sync-visuals operation (PNG stills + motion clips routing; bytes-identical)
- [x] **T5.2** Implement DESCRIPT-ASSEMBLY-GUIDE.md regeneration (field-masked-hash determinism per `field-mask.yaml`)
- [x] **T5.3** Wire 7a.5 specialist-summary-writer (AC-J)
- [x] **T5.4** **AC-B 150-LOC ceiling discipline:** `_act` body ≤150 LOC; HALT if exceeds
- [x] **T5.5** **NO LLM call** + **NO third-party API client import** — verified via AST-scan in T6

### T6 — Pipeline-determinism harness (AC-E)
- [x] **T6.1** `tests/end_to_end/test_compositor_pipeline_determinism.py` — N=10 runs; bytes-identical sync-visuals + field-masked-hash DESCRIPT-ASSEMBLY-GUIDE; ≥99% rate; hard-block on failure

### T7 — SKILL.md alignment (AC-F)
- [x] **T7.1** `skills/compositor/SKILL.md` minimal frontmatter + body references `_bmad/memory/bmad-agent-compositor/` activation-time hot-load (NO `# Sanctum exception` block)

### T8 — Parity + behavioral + chain tests (AC-G + AC-I)
- [x] **T8.1** `tests/parity/test_compositor_activation_contract.py` (flat; Class-D2 template; 9 assertions)
- [x] **T8.2** `tests/specialists/compositor/test_compositor_sync_visuals.py` (AC-D)
- [x] **T8.3** `tests/specialists/compositor/test_compositor_assembly_guide_regen.py` (AC-D field-masked-hash)
- [x] **T8.4** `tests/specialists/compositor/test_compositor_no_llm_no_third_party_api.py` (AC-G structural assertion)
- [x] **T8.5** `tests/specialists/compositor/test_compositor_summary_landing.py` (AC-J)
- [x] **T8.6** `tests/composition/test_compositor_4input_chain.py` — 4-input integration (Gary+Kira+Enrique+Wanda) (AC-I)
- [x] **T8.7** Wall-clock annotations + `validate_parity_test_class_conformance.py` PASS on Class-D2

### T9 — SG-4 sanctum alignment verification
- [x] **T9.1** `tests/parity/test_skill_md_sanctum_alignment.py` PASSES for Compositor with Class-D2 branch (4-file sidecar pattern; FR101.iv exempt)

### T10 — Substrate-as-floor verification (AC-H)
- [x] **T10.1** `git diff` empty on dispatch_adapter.py:70-95

### T11 — Composition Spec Decision Log entry + Operator-control parity row (AC-K + AC-L)
- [x] **T11.1** File NFR-CG15 Decision Log entry at composition-spec §10 (Class-D2 sidecar variant decision)
- [x] **T11.2** Add FR104 operator-control parity row at `docs/operator/legacy-vs-langgraph-control-parity.md`

### T12 — Manifest registration
- [x] **T12.1** Register `compositor` orchestration node in pipeline-manifest.yaml (additive; per `app/manifest/compiler.py::SPECIALIST_ALIASES` carry-forward `compositor → compositor` no alias needed)

### T13 — Regression baseline + sandbox-AC final
- [x] **T13.1** Full regression battery (target: cumulative + ~40 tests; including pipeline-determinism N=10)
- [x] **T13.2** ruff story-scoped clean
- [x] **T13.3** lint-imports 9/9 KEPT
- [x] **T13.4** Sandbox-AC validator final PASS

### T14 — Codex G6 self-review
- [x] **T14.1** G6 self-review at `7b-11-codex-self-review-2026-04-XX.md`
- [x] **T14.2** Status flip `in-progress → review`

### T15 — Claude bmad-code-review + close (AC-M + AC-N)
- [ ] **T15.1** `bmad-code-review` at `7b-11-code-review-2026-04-XX.md`
- [ ] **T15.2** Remediation cycle 1 if needed
- [ ] **T15.3** **IF dual-gate (per E1 binding-hard fired):** operator-witnessed Gate-2 ceremony at T15.3-bis (operator runs full focused + wider regression battery + pipeline-determinism N=10 + commits canary evidence into Completion Notes)
- [ ] **T15.4** Wave-5b pre-T1 K-projection tripwire ledger entry per AC-M
- [ ] **T15.5** Sprint-status flip `review → done` (single-gate) OR `review → operator-acceptance-pending → done` (dual-gate)
- [ ] **T15.6** next-session-start-here.md update: pivot to Wave 6 (7b.12 integration; dual-gate strict-last)
- [ ] **T15.7** Deferred-inventory updates per AC-N.4
- [ ] **T15.8** Standing-guardrail status: SG-4 GREEN for Compositor; Class-D2 template active in validator
- [ ] **T15.9** Three-line D12 close stub
- [ ] **T15.10** Commit + push (force-add gitignored sanctum if applicable)

---

## Dev Notes

### Round-(e) E1 binding-hard discipline at T1

If T1 K-projection lands ≥4.0K LOC, gate mode FLIPS to dual-gate BEFORE any code is written. This is non-discretionary; dev-agent does NOT proceed to T2 with single-gate assumptions if K-projection is over threshold. Operator-witnessed Gate-2 ceremony added to T15 close.

### Class-D2 is canonical per D20 (NOT exception)

The 4-file operational-metadata sidecar pattern is the FIRST-CLASS taxonomy bin for D2 specialists per D20. NO `# Sanctum exception` block needed in SKILL.md. FR101.iv sanctum-path-equality clause is EXEMPT for Class-D2 by design.

### Class-D2 NOT subject to Class-C two-SKILL.md

The Round-(f) party-mode 4/4 unanimous ratification of two-SKILL.md was Class-C-specific. Class-D2 has its own SKILL.md path (`skills/compositor/`; NOT bmad-agent-prefixed) per epic Story 7b.11 line 974 + scaffold-v0.2-D2-pipeline contract.

### Pipeline-determinism harness ≥99% is HARD-BLOCK

Per D17 H-Pipeline contract: ≥99% rate (9-of-10 minimum) is hard-block; single failure → story HALTS; party-mode escalation required. NO flake tolerance — pipeline-determinism is a load-bearing invariant for trial-2 Descript handoff readiness.

### NFR predicates honored

NFR-T9 / T10 / T12 — `@pytest.mark.timeout` annotations (no T11/T11a/T11b — Class-D2 has no third-party API or LLM canary).
NFR-CG14 + NFR-CG14a — chain test inheriting ChainTestBase.
NFR-CG15 — Decision Log entry at composition-spec §10.
NFR-CG16 — bmad-code-review pre-close.
NFR-I9 (D2 branch) + NFR-I10 + NFR-I11 (mapping-checklist) + NFR-I12 (Class-D2 template extension) + NFR-I13 (substrate-frozen-paths).

### Known follow-ons

- **`class-d2-template-extend-validator-during-7b-11`** — CLOSE at T2 (in-story; lockstep)
- **`scaffold-v0-2-d2-pipeline-first-instance-documentation`** — CLOSE at T11.1 with Decision Log entry
- **`bmad-memory-gitignore-force-add-policy`** — recurring; affects Compositor sidecar at commit
- **`compositor-7b-12-integration-parity-suite`** — file as named-but-not-filed; closes at 7b.12 Wave-6 integration

### Anti-pattern catalog citations

- **A6** (silent-fixture-stub fallback) — closing for Compositor G3
- **A11** (sanctum/sidecar pattern divergence) — Class-D2 4-file operational-metadata sidecar is a NEW pattern; harvest as A11 fifth example (after A11 first=Irene `bmad-agent-content-creator`; A11 second=Gary skill-dir naming; A11 third=Class-C two-SKILL.md; A11 fourth=Wanda 5+1 sidecar→6-file BMB; A11 fifth=Compositor 4-file operational-metadata)
- **P1** (substrate-as-floor violation) — AC-H binding (additive-only greenfield)

---

### Project Structure Notes

- `app/specialists/compositor/` — NEW (greenfield via scaffold-v0.2-D2-pipeline)
- `_bmad/memory/bmad-agent-compositor/` — NEW (Class-D2 sidecar; 4-file operational-metadata; NOT 6-file BMB persona)
- `skills/compositor/` — UPDATED SKILL.md (alignment per scaffold-v0.2-D2-pipeline contract; minimal frontmatter)
- `tests/parity/test_compositor_activation_contract.py` — NEW (FR105; Class-D2)
- `scripts/utilities/validate_parity_test_class_conformance.py` — EXTENDED with Class-D2 template (lockstep)
- `tests/specialists/compositor/test_*.py` — NEW (5 behavioral tests)
- `tests/end_to_end/test_compositor_pipeline_determinism.py` — NEW (FR106 H-Pipeline ≥99%)
- `tests/composition/test_compositor_4input_chain.py` — NEW (4-input chain)
- `docs/dev-guide/composition-specification.md` §10 — NEW Decision Log entry (Class-D2 canonical sidecar)
- `docs/operator/legacy-vs-langgraph-control-parity.md` — NEW row (FR104)

### Detected conflicts or variances

- **Pre-T1 K-projection >4K** — resolved at T1.6 (binding=hard gate-mode flip if exceeds)
- **Class-D2 sidecar variant vs 6-file BMB persona** — resolved per D20 canonical (4-file operational-metadata is intentional; FR101.iv exempt)
- **NOT subject to Class-C two-SKILL.md** — resolved per epic Story 7b.11 line 974 binding `skills/compositor/` path

---

## References

- **Round-(e) governance JSON**: [`docs/dev-guide/migration-story-governance.json`](../../docs/dev-guide/migration-story-governance.json) §`stories.7b-11`
- **Epic + story-level scope**: [`epics-slab-7b-specialist-activation-eleven.md`](../planning-artifacts/epics-slab-7b-specialist-activation-eleven.md) §Story 7b.11
- **PRD FR99 + FR111**: [`prd-slab-7b-specialist-activation-eleven.md`](../planning-artifacts/prd-slab-7b-specialist-activation-eleven.md)
- **Scaffold-v0.2-D2-pipeline (FR111; Wave 0 LANDED)**: [`docs/dev-guide/scaffolds/scaffold-v0.2-D2-pipeline/`](../../docs/dev-guide/scaffolds/scaffold-v0.2-D2-pipeline/)
- **D17 H-Pipeline determinism contract**: PRD §H-Pipeline (≥99% rate; hard-block; bytes-identical + field-masked-hash)
- **D20 Class-D2 first-class taxonomy bin**: PRD §D20 (sidecar variant canonical, NOT exception)
- **Wave-3 Class-C precedents (for chain test inputs)**: [`migration-7b-6-gary-port-shape.md`](migration-7b-6-gary-port-shape.md) + [`migration-7b-7-kira-port-shape.md`](migration-7b-7-kira-port-shape.md) + [`migration-7b-8-enrique-port-shape.md`](migration-7b-8-enrique-port-shape.md) + [`migration-7b-9-wanda-port-shape-onto-scaffold.md`](migration-7b-9-wanda-port-shape-onto-scaffold.md)
- **Wave-5a Dan parallel sibling**: [`migration-7b-10-dan-greenfield.md`](migration-7b-10-dan-greenfield.md)
- **7b.1 substrate**: [`migration-7b-1-texas-hardening.md`](migration-7b-1-texas-hardening.md)
- **7a.5 conversation-persistence**: [`migration-7a-5-conversation-persistence-specialist-summary-writer.md`](migration-7a-5-conversation-persistence-specialist-summary-writer.md)
- **BMB sanctum alignment checklist (FR108)**: [`docs/dev-guide/bmb-sanctum-alignment-checklist.md`](../../docs/dev-guide/bmb-sanctum-alignment-checklist.md)
- **Composition Spec (NFR-CG15 Decision Log)**: [`docs/dev-guide/composition-specification.md`](../../docs/dev-guide/composition-specification.md)
- **Operator-control parity table (FR104)**: [`docs/operator/legacy-vs-langgraph-control-parity.md`](../../docs/operator/legacy-vs-langgraph-control-parity.md)
- **CLAUDE.md** governance + Round-(e) E1 binding-hard discipline

---

## Dev Agent Record

### Agent Model Used

Codex (GPT-5)

### Implementation Plan

1. Extend Class-D2 parity conformance without changing inherited A/B/C+/C/D1 templates.
2. Instantiate Compositor as deterministic Class-D2 body with 4-file operational sidecar and refreshed `skills/compositor/SKILL.md`.
3. Add deterministic fixture tests, 10-iteration H-Pipeline harness, 4-input chain coverage, summary landing, registry/manifest wiring, and governance docs.
4. Run focused validation, story-scoped lint, sandbox/lockstep checks, and broad regression battery before review handoff.

### Debug Log

- 2026-04-30: T1.1 Round-(e) E1/E6 command PASS.
- 2026-04-30: T1.3 Waves 1-3 plus 7b.9 verified done; 7b.10 treated done per operator instruction.
- 2026-04-30: T1.4 scaffold-v0.2-D2-pipeline 7-file presence PASS.
- 2026-04-30: T1.5 greenfield probes PASS: no `app/specialists/compositor/`, no `_bmad/memory/bmad-agent-compositor/`, no `skills/bmad-agent-compositor/`; existing `skills/compositor/SKILL.md` will be refreshed.
- 2026-04-30: T1.6 pre-code K-projection recorded at 3.45K LOC; below 4.0K threshold, so `conditional_dual_gate_escalation` did not fire and single-gate holds.
- 2026-04-30: T1.7 sandbox-AC preflight PASS.
- 2026-04-30: Focused compositor/parity/composition battery PASS: 50 passed.
- 2026-04-30: Broad story-specified regression PASS: 1368 passed, 21 skipped, 1 deselected.
- 2026-04-30: Final validators PASS: pipeline lockstep, live-API detector, sandbox-AC, Class-D2 conformance, ruff story scope, lint-imports 9/9.
- 2026-04-30: `dispatch_adapter.py` diff empty; `_act.py` body 139 LOC.

### Completion Notes List

- T1 readiness complete. Pre-code K-projection: 3.45K LOC, with projected breakdown recorded in `sprint-status.yaml::tripwire_events::wave_5b_pre_t1_compositor`; fired_verdict=false; no dual-gate escalation.
- Class-D2 Compositor body landed as deterministic-only greenfield scaffold with no LLM/provider imports.
- Four-file operational sidecar landed at `_bmad/memory/bmad-agent-compositor/`; no six-file BMB/persona continuity files.
- H-Pipeline determinism harness landed and passed; Class-D2 validator extension active with 11 activation contracts conforming.
- Composition Spec decision log and operator-control parity row updated for Class-D2 canonical sidecar variant.
- G6 self-review written at `_bmad-output/implementation-artifacts/7b-11-codex-self-review-2026-04-30.md`; story moved to review for Claude `bmad-code-review`.

### File List

- _bmad-output/implementation-artifacts/migration-7b-11-compositor-greenfield.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- _bmad-output/implementation-artifacts/7b-11-codex-self-review-2026-04-30.md
- _bmad/memory/bmad-agent-compositor/access-boundaries.md
- _bmad/memory/bmad-agent-compositor/chronology.md
- _bmad/memory/bmad-agent-compositor/contract.md
- _bmad/memory/bmad-agent-compositor/version.md
- app/models/state/specialist_summary_artifacts.py
- app/specialists/compositor/__init__.py
- app/specialists/compositor/_act.py
- app/specialists/compositor/config.yaml
- app/specialists/compositor/expertise/README.md
- app/specialists/compositor/graph.py
- app/specialists/compositor/model_config.yaml
- app/specialists/compositor/state.py
- docs/dev-guide/composition-specification.md
- docs/operator/legacy-vs-langgraph-control-parity.md
- scripts/utilities/validate_parity_test_class_conformance.py
- skills/compositor/SKILL.md
- state/config/dispatch-registry.yaml
- tests/composition/test_compositor_4_input_chain.py
- tests/end_to_end/test_compositor_pipeline_determinism.py
- tests/fixtures/specialists/compositor/source/bed-01.mp3
- tests/fixtures/specialists/compositor/source/narration-01.mp3
- tests/fixtures/specialists/compositor/source/slide-01.mp4
- tests/fixtures/specialists/compositor/source/slide-01.png
- tests/fixtures/specialists/compositor/source/slide-02.png
- tests/parity/test_compositor_activation_contract.py
- tests/parity/test_pipeline_determinism_harness.py
- tests/parity/test_skill_md_sanctum_alignment.py
- tests/specialists/compositor/_fixtures.py
- tests/specialists/compositor/test_compositor_assembly_guide_field_masked_hash.py
- tests/specialists/compositor/test_compositor_no_llm_no_third_party_api.py
- tests/specialists/compositor/test_compositor_summary_landing.py
- tests/specialists/compositor/test_compositor_sync_visuals_deterministic.py
- tests/unit/marcus/orchestrator/test_specialist_summary_writer.py
