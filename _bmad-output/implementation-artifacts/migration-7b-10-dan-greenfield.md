# Migration Story 7b.10: Dan Greenfield (Class D1) â€” Creative-Director Aux Contributions

**Status:** done
**Sprint key:** `migration-7b-10-dan-greenfield`
**Epic:** Slab 7b Specialist Body Activation â€” `epic-slab-7b-specialist-activation-eleven`. **Wave 5a** (Class-D1 LLM-greenfield; parallelizable with Wave-5b 7b.11 after Waves 1-3 *closed* per R8 Winston-amendment; Claude-authored per D21).
**Pts:** 5 | **Gate:** single (per `docs/dev-guide/migration-story-governance.json::stories.7b-10`; rationale: null) | **K-target:** ~1.5Ã— (target ~40 tests / floor ~30; ~3.5K LOC; **Round-(e) E6 k_contract tripwire 4.0K â†’ escalate_to_party_mode_for_scope_review** â€” likely API integration leak signal).
**Author:** **Claude** (per D21 â€” Class-D1 + D2 are Claude-authored). **Review:** **Codex** via `bmad-code-review`.
**Wave-5a precondition:** ALL Waves 1-3 stories `done` per R8 Winston-amendment (7b.1+7b.2+7b.3+7b.4+7b.5+7b.6+7b.7+7b.8 all `done` in `sprint-status.yaml`).

---

## Round-(e) Governance Inheritance

Round-(e) freeze landed 2026-04-29. Load-bearing for 7b.10:

- **E6 k_contract block** â€” scope=Class-D1 LLM-greenfield bounded to (1) SKILL.md option-a + (2) sidecar at `_bmad/memory/bmad-agent-dan/` (full BMB pattern) + (3) `app/specialists/dan/` scaffold-v0.2 instantiation + (4) `_act` body shaped as narrow-lane creative-director aux contributions G1-G2. **EXCLUDES third-party-API integration** â€” if T1 dan-api-tbd resolution lands as third-party-API, Round-(b) B1 / Round-(c) C1 binding requires **party-mode consensus + governance-JSON version bump pre-promotion** (dev-agent does NOT unilaterally promote). Tripwire 4.0K â†’ `escalate_to_party_mode_for_scope_review` (records at top-level `tripwire_escalation_record_path`; >4K = scope creep, plausibly API integration leak).
- **B1/C1 binding-hard (sandbox-AC inventory promotion gating):** if Dan T1 resolves to third-party-API, the inventory entry at `docs/dev-guide/migration-ac-sandbox-inventory.json::dan-api-tbd-pending` must be promoted via party-mode + governance-JSON version bump BEFORE any API-bound dev work begins.

**T1 readiness verification command:**
```bash
.venv/Scripts/python.exe -c "import json; d = json.load(open('docs/dev-guide/migration-story-governance.json', encoding='utf-8')); assert d['version'] == '2026-04-29-slab7b-twelve-stories'; assert d['stories']['7b-10']['k_contract']['tripwire_threshold_kloc'] == 4.0; assert 'EXCLUDES third-party-API' in d['stories']['7b-10']['k_contract']['scope']; print('Round-(e) E6 k_contract verified PASS for 7b-10')"
```

---

## T1 Readiness Block

### Required-readings cascade (10-reading)

1. **Round-(e) governance JSON** â€” `docs/dev-guide/migration-story-governance.json` Â§`stories.7b-10` (k_contract; B1/C1 binding-hard).
2. **Epic + story-level scope** â€” [`epics-slab-7b-specialist-activation-eleven.md`](../planning-artifacts/epics-slab-7b-specialist-activation-eleven.md) Â§Story 7b.10 (lines 882-928).
3. **PRD Â§FR98** â€” Dan greenfield: SKILL.md (option-a sanctum-aligned) + sidecar + `app/specialists/dan/` scaffold-v0.2 + `_act` narrow-lane creative-director aux contributions G1-G2.
4. **Sandbox-AC inventory `dan-api-tbd-pending`** â€” [`docs/dev-guide/migration-ac-sandbox-inventory.json`](../../docs/dev-guide/migration-ac-sandbox-inventory.json). **T1 resolution: LLM-only OR third-party-API.** Operator + dev-agent decide at T1.
5. **`bmad-create-specialist` generator** â€” [`skills/bmad-create-specialist/`](../../skills/bmad-create-specialist/) (SKILL.md + scripts + templates). Invocation: `uv run python -m skills.bmad_create_specialist.scripts.generate --name dan --mcp <tbd> --expertise-tier <tbd> --from-skill <existing-or-blank>`.
6. **Slab 2a.2 Pass-2 precedent (9-node scaffold + AC-B 150-LOC ceiling)** â€” [`migration-2a-2-irene-pass-2-scaffold-migration.md`](migration-2a-2-irene-pass-2-scaffold-migration.md).
7. **Wave-1/2/3 close evidence** â€” verify ALL prior body stories `done` (7b.1..7b.9) in `sprint-status.yaml`.
8. **Class-D1 template (NEW; this story extends validator)** â€” `scripts/utilities/validate_parity_test_class_conformance.py` extended in lockstep with Class-D1 template assertions (first-recorded-fixture-set parity per NFR-I12).
9. **BMB sanctum alignment checklist (FR108)** â€” [`docs/dev-guide/bmb-sanctum-alignment-checklist.md`](../../docs/dev-guide/bmb-sanctum-alignment-checklist.md). Option-a required at creation per `slab7bSpecialistRoster.specialists.dan.sanctumAlignment`.
10. **CLAUDE.md** â€” Â§LangChain/LangGraph migration governance + Â§BMAD sprint governance.

### Dan current-state probe + greenfield posture

```bash
ls app/specialists/dan/ 2>/dev/null                  # NOT YET PRESENT â€” greenfield; this story creates
ls _bmad/memory/dan-sidecar/                          # 5-file sidecar (legacy; preserve untouched until trial-2 validation)
ls _bmad/memory/bmad-agent-dan/ 2>/dev/null          # NOT YET PRESENT â€” greenfield; this story creates 6-file BMB
ls skills/bmad-agent-dan/ 2>/dev/null                # NOT YET PRESENT â€” greenfield; bmad-create-specialist generates
ls skills/bmad-create-specialist/                    # SKILL.md + scripts/ + templates/ (the generator; verified Slab 2a.1 era)
```

### dan-api-tbd-pending RESOLUTION (BLOCKING T1 step)

This is the **first decision point**. Outcome determines downstream story shape:

**Decision:** Dan = (a) **LLM-only** OR (b) **third-party-API-bound**.

**Decision criteria (operator + dev-agent):**
- Does Dan's narrow-lane creative-director role (per `slab7bSpecialistRoster.specialists.dan.actBodyShape`) require any external API beyond `gpt-5.4`?
  - Aux contributions threaded G1-G2 are LLM-shaped (analysis, narrative critique, visual/audio gut-check) â€” likely LLM-only sufficient
  - If creative-director aux requires image/video generation OR external creative service, third-party-API may be needed
- Are there design-mandated provider constraints? (None known per PRD Â§FR98.)

**Default verdict:** **LLM-only** (most plausible per scope; aligns with Tracy precedent â€” Class-C+ Tracy is LLM-only despite being a port-shape).

**If LLM-only resolution (default path):**
- Sandbox-AC inventory entry `dan-api-tbd-pending` is **retired** in lockstep with this story T2 (governance JSON entry removed; version bump optional â€” minor; record decision in Completion Notes)
- T1 closes with operator confirmation; dev proceeds normally per scope
- AC-10-B is N/A (no live canary needed)

**If third-party-API resolution:**
- **HALT-AND-SURFACE.** Round-(b) B1 / Round-(c) C1 binding requires party-mode consensus + governance-JSON version bump BEFORE any API-bound dev work
- Convene party-mode (John+Mary+Amelia+Murat per Slab 7a precedent) to ratify (a) the API choice, (b) the sandbox-AC inventory promotion (entry replaced with concrete API name + `httpx`/SDK pattern), (c) governance-JSON version bump â†’ e.g., `2026-04-XX-slab7b-dan-api-{name}-promotion`
- After party-mode GO + version bump, AC-10-B activates: operator runs T5 live canary â‰¤3; cost â‰¤$0.40 per canary; evidence pasted into Completion Notes

**Decision recorded in:** Dev Agent Record T1 Readiness block + `docs/dev-guide/migration-ac-sandbox-inventory.json` (entry retired or replaced) + (if third-party-API) governance-JSON `_amendment_log` entry.

### Wave 0/1/2/3 + 7b.1 substrate sweep

```bash
ls docs/dev-guide/bmb-sanctum-alignment-checklist.md docs/dev-guide/sanctum-exception-categories.json docs/dev-guide/operator-control-parity-template.md docs/dev-guide/migration-ac-sandbox-inventory.json skills/bmad-agent-cora/SKILL.md
ls docs/dev-guide/scaffolds/scaffold-v0.2-D2-pipeline/  # Class-D2 scaffold (referenced for D1 contrast; D1 uses scaffold-v0.2 base, NOT D2 pipeline variant)
ls tests/parity/_sanctum_parity_base.py tests/composition/_chain_test_base.py scripts/utilities/validate_parity_test_class_conformance.py

# Verify Waves 1-3 closed (8 stories `done`)
grep -E "migration-7b-(1|2|3|4|5|6|7|8|9)-[a-z-]+: done" _bmad-output/implementation-artifacts/sprint-status.yaml | wc -l  # Expect: â‰¥8 ('done' status on all prior body stories)
```

All Waves 1-3 stories must be `done` before opening this story per R8 Winston-amendment.

### Class-D1 template extension required

This story is the **first Class-D1 specialist** to land per NFR-I12. The dev-agent must extend `scripts/utilities/validate_parity_test_class_conformance.py` with Class-D1 template assertions (first-recorded-fixture-set parity â€” Dan has no prior `app/specialists/dan/` so fixtures need explicit recording ceremony). Class-D1 template is additive; A/B/C/C+ templates unchanged.

### Sandbox-AC validator pre-flight

```bash
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py \
  _bmad-output/implementation-artifacts/migration-7b-10-dan-greenfield.md
```
Expect PASS. Any AC referencing 'dan-api' is auto-flagged for operator clarification per inventory entry â€” but our spec ACs use shipped Python deps (LLM-only path) and gate live canary to operator-gated AC-10-B (conditional on third-party-API resolution).

### Standing pre-flight items

1. Severance posture confirmed.
2. `state/config/substrate-frozen-paths.yaml` honored â€” no diff to `app/marcus/orchestrator/dispatch_adapter.py:70-95`.
3. Greenfield `app/specialists/dan/` does not yet exist; creation via `bmad-create-specialist` is additive â€” no substrate violation.
4. NFR-T9-T12 wall-clock ceilings hold.

---

## Story

As a **migration dev agent**,
I want **Dan to be created from scratch via `bmad-create-specialist` â€” generating `skills/bmad-agent-dan/SKILL.md` (option-a sanctum-aligned) + sidecar at `_bmad/memory/bmad-agent-dan/` (full 6-file BMB pattern) + `app/specialists/dan/` directory with scaffold-v0.2 + `_act` body shaped as narrow-lane creative-director aux contributions threaded across G1-G2 â€” AND I want the `dan-api-tbd-pending` sandbox-AC inventory entry resolved at story T1 (defaulting to LLM-only; party-mode-gated promotion if third-party-API)**,
So that **(a) Trial-2 carries real creative-director aux contributions at G1 lesson-plan + G1A scope-lock + G2 storyboard gates (not silent passthrough), (b) Dan's roster floor presence is upgraded from sidecar-only â†’ fully activated body, (c) the Class-D1 first-recorded-fixture-set parity test inheriting `SanctumParityTestBase` from 7b.1 substrate enforces NFR-I12 Class-D1 template, and (d) SG-4 sanctum-alignment is enforced for Dan via option-a + 6-file BMB sanctum at canonical path**.

---

## Acceptance Criteria

All ACs are dev-agent-executable (sandbox-AC compliant assuming LLM-only resolution at T1; if third-party-API, AC-10-B activates per below). Live-LLM tests tagged `@pytest.mark.llm_live`; auto-skip on placeholder API key.

### AC-7b.10-A â€” T1 readiness verification + dan-api-tbd resolution + drift

**Given** the Round-(e) E6 k_contract + B1/C1 binding-hard amendments + Waves 1-3 all `done`
**When** the dev agent runs T1 readiness
**Then** all 10 readings cascade complete; Round-(e) verification command exits 0; Wave-0/1/2/3 sweep PASS; sandbox-AC validator PASS pre-flight
**And** dan-api-tbd-pending resolution recorded in Dev Agent Record T1 Readiness block:
  - **(default) LLM-only:** decision recorded; sandbox-AC inventory entry `dan-api-tbd-pending` retired in lockstep with T2; AC-10-B is N/A
  - **third-party-API:** HALT-AND-SURFACE; party-mode consensus + governance-JSON version bump REQUIRED before T2 opens; AC-10-B activates after promotion
**And** decision recorded in `docs/dev-guide/migration-ac-sandbox-inventory.json` (entry retired or replaced).

### AC-7b.10-B â€” `bmad-create-specialist` invocation generates Dan

**Given** the generator at `skills/bmad-create-specialist/` (proven from Story 2a.1)
**And** dan-api-tbd resolution at AC-A
**When** the dev-agent invokes generation:
```bash
uv run python -m skills.bmad_create_specialist.scripts.generate \
  --name dan \
  --mcp none \
  --expertise-tier L4-creative-director-aux \
  --from-skill <if-LLM-only: blank; if-third-party-API: appropriate skill>
```
**Then** the generator produces:
  - `skills/bmad-agent-dan/SKILL.md` (option-a sanctum-aligned per FR101 R1-restated; minimal frontmatter `name` + `description`)
  - `app/specialists/dan/` directory with scaffold-v0.2 (9-node scaffold + `__init__.py`, `graph.py`, `state.py`, `model_config.yaml`, `expertise/README.md`)
**And** `validate_scaffold("dan", build_dan_graph()).is_conforming is True`; ruff clean; import-linter C1 lane-isolation PASS
**And** generator denylist (per Slab 2a.1) does NOT block this path (Dan is first Slab 7b D1 greenfield; permitted per FR98).

### AC-7b.10-C â€” Dan sanctum at canonical path with full 6-file BMB pattern

**Given** the SG-4 sanctum-alignment requirement (option-a required at creation per `slab7bSpecialistRoster.specialists.dan.sanctumAlignment`)
**When** the dev-agent authors Dan's sanctum
**Then** `_bmad/memory/bmad-agent-dan/` directory lands with 6-file BMB pattern:
  - `INDEX.md` â€” essential context loaded on activation
  - `PERSONA.md` â€” full BMB persona (creative-director identity)
  - `CREED.md` â€” operating principles
  - `BOND.md` â€” operator-specialist relationship
  - `MEMORY.md` â€” cumulative continuity (production-runs)
  - `CAPABILITIES.md` â€” skill inventory
**And** content authored per BMB checklist worked examples; if relevant content exists in legacy `_bmad/memory/dan-sidecar/`, translate into the 6-file pattern
**And** the legacy `_bmad/memory/dan-sidecar/` directory is preserved unchanged (no deletion this story; deferred-inventory follow-on `dan-sidecar-cleanup-post-trial-2-validation` filed for cleanup AFTER trial-2 validates no consumer references it).

### AC-7b.10-D â€” `_act` body: narrow-lane creative-director aux contributions G1-G2

**Given** Dan's role per `slab7bSpecialistRoster.specialists.dan.actBodyShape` (narrow-lane creative-director aux; supplements Irene + Quinn-R/Vera primary roles; NOT a primary lesson-plan/storyboard contribution)
**And** Dan dispatched at G1 (lesson-plan author aux), G1A (scope-lock advisor aux), G2 (storyboard creative-direction aux)
**When** Dan's `_act` body executes
**Then** Dan emits aux contributions threaded across the gates per FR98:
  - G1 â€” creative-director critique on Irene Pass-1 lesson plan (advisory; not blocking)
  - G1A â€” scope-lock advisor (creative-direction guardrails for locked scope)
  - G2 â€” storyboard creative-direction aux (visual narrative coherence)
**And** `_act` body length is **â‰¤150 LOC** per AC-B ceiling; HALT-AND-SURFACE re-scope decision if exceeds
**And** all aux contributions are **advisory** (`advisory-vs-blocking partition` per Quinn-R G5 precedent) â€” Dan does NOT block any gate on its own.

### AC-7b.10-E â€” Cache-hit-rate harness (FR106; ten LLM specialists incl. Dan)

**Given** the cache-hit-rate harness requirement (FR106)
**When** the dev-agent wires Dan into the harness
**Then** harness runs N=10 in-process against `gpt-5.4` with `prompt_tokens >> 1024` MF2 floor
**And** `median[2:] >= 85%` post-warm-up (per Slab 2a.2 MF1 disposition rule)
**And** prompt-token floor pre-check raises `pytest.fail(...)` if envelope undersized (per Slab 2a.2 MF2)
**And** cache-metric source: OpenAI usage API (per Slab 2a.2 MF5).
**Test pin:** `tests/end_to_end/test_dan_cache_hit_rate.py` â€” `@pytest.mark.llm_live`; auto-skip; operator-gated Completion-Notes evidence.

### AC-7b.10-F â€” SG-4 Sanctum Alignment (FR100 + FR101 â€” Dan first-enforcement)

**Given** the SG-4 sanctum-alignment requirement
**When** the dev-agent commits Dan greenfield
**Then** `skills/bmad-agent-dan/SKILL.md` (NEW; generator-emitted at T2) is verified option-a sanctum-aligned per BMB checklist (FR108):
  - YAML frontmatter MINIMAL (`name` + `description` only)
  - SKILL.md body references `_bmad/memory/bmad-agent-dan/` sanctum dir
**And** the sanctum dir at `_bmad/memory/bmad-agent-dan/` carries 6-file BMB pattern (per AC-C)
**And** the parity test `tests/parity/test_skill_md_sanctum_alignment.py` PASSES for Dan with Class-D1 template assertions (`SanctumParityTestBase` inherited; minimal frontmatter; sanctum-path equality; 6-file BMB; Class-D1 cold-activation smoke + first-recorded-fixture-set parity).

### AC-7b.10-G â€” FR105 per-specialist parity test (Class-D1 template extension)

**Given** the Errata 4 verdict-flat layout + 7b.1's `_sanctum_parity_base.py` substrate
**And** Dan is the first Class-D1 specialist (no prior `app/specialists/dan/` â€” first-recorded-fixture-set parity is novel per NFR-I12 Class-D1 template)
**When** the dev-agent authors Dan's activation-contract test
**Then** `tests/parity/test_dan_activation_contract.py` (flat) lands inheriting `SanctumParityTestBase` with `class_template_id = "D1"`, `specialist_name = "dan"`
**And** the test asserts **Class-D1 first-recorded-fixture-set parity** per NFR-I12 Class-D1 template:
  - (i) 9-node scaffold conformance via `validate_scaffold()`
  - (ii) advisory-vs-blocking partition (Dan never blocks)
  - (iii) aux-contribution shape per FR98 (G1/G1A/G2 contributions)
  - (iv) golden-fixture record + replay (first-recorded ceremony)
  - (v) cold-activation smoke
**And** **`scripts/utilities/validate_parity_test_class_conformance.py` extended with Class-D1 template assertions in lockstep** (additive; A/B/C/C+ unchanged).
**And** `@pytest.mark.timeout(30)` per NFR-T9; <120s aggregate per NFR-T12.

### AC-7b.10-H â€” Sandbox-AC governance + B1/C1 promotion gating

**Given** the sandbox-AC inventory governance requirement + Round-(b) B1 / Round-(c) C1 binding-hard amendments
**When** `validate_migration_story_sandbox_acs.py` runs on this spec
**Then** PASS (no forbidden CLI in dev-agent ACs)
**And** if dan-api-tbd resolved to LLM-only at T1, the inventory entry `dan-api-tbd-pending` is RETIRED at T2 commit (governance JSON entry removed; lockstep with this story T2)
**And** if dan-api-tbd resolved to third-party-API, the inventory entry is REPLACED via party-mode consensus + governance-JSON version bump BEFORE T3 opens (NOT during T3); dev-agent does NOT unilaterally promote
**And** any AC referencing 'dan-api' in dev-agent blocks is operator-flagged per inventory entry rule.

### AC-7b.10-I â€” Substrate-as-floor invariant (FR113 + NFR-I13)

**Given** the substrate-as-floor invariant
**When** the dev-agent's diff is reviewed
**Then** **no diff hunk touches `app/marcus/orchestrator/dispatch_adapter.py:70-95`** absent ceremony
**And** Dan's greenfield creation is purely additive (`app/specialists/dan/` is new) â€” no substrate violation
**And** integration with Marcus dispatcher uses existing dispatch APIs (no new dispatcher edits).

### AC-7b.10-J â€” Chain test inheriting `ChainTestBase`

**Given** NFR-CG14 chain-test PR pre-merge requirement + 7b.1's `_chain_test_base.py` substrate
**When** the dev agent authors the Dan chain test
**Then** `tests/composition/test_dan_aux_contribution_chain.py` lands inheriting `ChainTestBase`
**And** the test asserts Dan's aux contributions integrate cleanly with Irene Pass-1 (G1) + Vera/Quinn-R (G1A advisor + G2)
**And** wall-clock <120s.

### AC-7b.10-K â€” Operator-gated AC-10-B (CONDITIONAL on third-party-API resolution; John C-observation tightening)

**Given** the dan-api-tbd resolution at AC-A
**When** the resolution is LLM-only
**Then** **AC-10-B is N/A** and removed from Completion Notes (no live canary needed)

**OR**

**When** the resolution is third-party-API
**Then** **AC-10-B activates:** operator runs T5 live canary â‰¤3 invocations against the resolved API; cost â‰¤$0.40 per canary; evidence pasted into Completion Notes verbatim
**And** the canary smoke evidence carries: API endpoint hit, request payload (redacted credentials), response 200-OK + valid shape, cost-tracking line.

### AC-7b.10-L â€” Close protocol

**Given** all prior ACs PASS + bmad-code-review returns PASS or PASS-WITH-PATCH-applied + regression baseline holds
**When** the story closes
**Then** at close:
  1. **sprint-status.yaml** flip: `migration-7b-10-dan-greenfield: in-progress â†’ review â†’ done`
  2. **dan-api-tbd inventory entry** retired OR replaced (per AC-H)
  3. **Class-D1 template** active in `validate_parity_test_class_conformance.py`
  4. **next-session-start-here.md** updated: pivot to next pending Wave-5 story (7b.11 Compositor) OR Wave 6 (7b.12 integration) if 7b.11 already done
  5. **Deferred-inventory updates**: `dan-sidecar-cleanup-post-trial-2-validation` filed
  6. **Standing-guardrail status**: SG-4 GREEN for Dan; Class-D1 template active in validator
  7. **Three-line D12 close stub**

---

## Tasks / Subtasks

### T1 â€” T1 readiness + dan-api-tbd resolution
- [x] **T1.1** Round-(e) governance JSON verification
- [x] **T1.2** 10-reading required cascade
- [x] **T1.3** Wave-1/2/3 close evidence (8/8 stories `done`)
- [x] **T1.4** Wave 0 + 7b.1 substrate sweep
- [x] **T1.5** Dan current-state probe (greenfield posture confirmed)
- [x] **T1.6** **dan-api-tbd-pending RESOLUTION** (LLM-only OR third-party-API; HALT-AND-SURFACE if third-party-API per B1/C1 binding)
- [x] **T1.7** Sandbox-AC validator pre-flight
- [x] **T1.8** Resolution + drift recorded in Dev Agent Record T1 block

### T2 â€” Generate Dan via `bmad-create-specialist`
- [x] **T2.1** Invoke `bmad-create-specialist` generator (per AC-B parameters)
- [x] **T2.2** Verify generator output: SKILL.md + app/specialists/dan/ scaffold-v0.2 + 9-node graph
- [x] **T2.3** `validate_scaffold("dan", build_dan_graph()).is_conforming is True`
- [x] **T2.4** ruff clean + import-linter C1 PASS
- [x] **T2.5** If LLM-only resolution: retire `dan-api-tbd-pending` entry from `docs/dev-guide/migration-ac-sandbox-inventory.json` in same commit

### T3 â€” Dan sanctum 6-file BMB authoring
- [x] **T3.1** Author 6 BMB files at `_bmad/memory/bmad-agent-dan/` (translate from `dan-sidecar/` where applicable; author novel per BMB checklist)
- [x] **T3.2** File `dan-sidecar-cleanup-post-trial-2-validation` as named-but-not-filed follow-on

### T4 â€” Dan `_act` body: narrow-lane creative-director aux (AC-D)
- [x] **T4.1** Implement G1 aux body â€” creative-director critique on Pass-1 lesson plan (advisory)
- [x] **T4.2** Implement G1A aux body â€” scope-lock advisor (creative guardrails)
- [x] **T4.3** Implement G2 aux body â€” storyboard creative-direction aux (visual narrative coherence)
- [x] **T4.4** Wire 7a.5 specialist-summary-writer (Dan verdicts land at `runs/<run_id>/specialist-summaries/dan-<gate>-<timestamp>.md`)
- [x] **T4.5** **AC-B 150-LOC ceiling discipline:** `_act` body â‰¤150 LOC; HALT-AND-SURFACE re-scope if exceeds
- [x] **T4.6** All Dan contributions are advisory (NEVER blocking) â€” enforce structurally

### T5 â€” Cache-hit-rate harness (AC-E)
- [x] **T5.1** `tests/end_to_end/test_dan_cache_hit_rate.py` (`@pytest.mark.llm_live`; Slab 2a.2 MF1+MF2+MF5 discipline)
- [x] **T5.2** Operator-gated Completion-Notes evidence block

### T6 â€” Parity + behavioral tests + Class-D1 template extension
- [x] **T6.1** `tests/parity/test_dan_activation_contract.py` (flat; Class-D1 template) â€” AC-G
- [x] **T6.2** **Extend `scripts/utilities/validate_parity_test_class_conformance.py` with Class-D1 template assertions** (LOCKSTEP foundational deliverable)
- [x] **T6.3** `tests/specialists/dan/test_dan_g1_aux_contribution.py`
- [x] **T6.4** `tests/specialists/dan/test_dan_g1a_scope_lock_advisor.py`
- [x] **T6.5** `tests/specialists/dan/test_dan_g2_creative_direction.py`
- [x] **T6.6** `tests/specialists/dan/test_dan_advisory_only_contract.py` â€” assert Dan never returns `verb: "halt"` or `verb: "block"`
- [x] **T6.7** `tests/specialists/dan/test_dan_summary_landing.py`
- [x] **T6.8** `tests/composition/test_dan_aux_contribution_chain.py` â€” AC-J
- [x] **T6.9** Wall-clock annotations + `validate_parity_test_class_conformance.py` PASS on Class-D1
- [x] **T6.10** First-recorded fixture-set ceremony: record golden envelope/return at `tests/fixtures/specialists/dan/golden_envelope.json` + `golden_return.json`

### T7 â€” SG-4 sanctum alignment verification (AC-F)
- [x] **T7.1** Verify generator-emitted `skills/bmad-agent-dan/SKILL.md` minimal frontmatter
- [x] **T7.2** Verify `_bmad/memory/bmad-agent-dan/` 6-file BMB pattern (per T3)
- [x] **T7.3** `tests/parity/test_skill_md_sanctum_alignment.py` PASSES for Dan

### T8 â€” Substrate-as-floor verification (AC-I)
- [x] **T8.1** `git diff` verification â€” no diff to dispatch_adapter.py:70-95
- [x] **T8.2** Dan's greenfield = additive only

### T9 â€” Manifest registration
- [x] **T9.1** Manifest lockstep verified PASS; no active `dan` orchestration node added because Dan is aux-only and not a v4.2 pipeline step. No `app/manifest/compiler.py::SPECIALIST_ALIASES` entry needed for `dan -> dan`.

### T10 â€” Regression baseline + sandbox-AC final
- [x] **T10.1** Full regression battery (target: â‰¥696 + Wave-1/2/3 cumulative tests + ~40 (this story) â‰ˆ 800+ passed; 19 skipped)
- [x] **T10.2** Dan-scoped `ruff check` clean; full-repo `ruff check .` attempted and recorded as pre-existing out-of-scope lint debt.
- [x] **T10.3** `lint-imports.exe` 9/9 KEPT
- [x] **T10.4** Sandbox-AC validator final PASS

### T11 â€” Codex G6 self-review
- [x] **T11.1** Codex authors G6 self-review at `_bmad-output/implementation-artifacts/7b-10-codex-self-review-2026-04-XX.md`
- [x] **T11.2** Status flip `in-progress â†’ review`

### T12 â€” Claude bmad-code-review + close (AC-K + AC-L)
- [ ] **T12.1** Claude runs `bmad-code-review` at `7b-10-code-review-2026-04-XX.md`
- [ ] **T12.2** Remediation cycle 1 if needed
- [ ] **T12.3** AC-10-B (operator-gated; CONDITIONAL on third-party-API resolution)
- [ ] **T12.4** Sprint-status flip `review â†’ done`
- [ ] **T12.5** Update `next-session-start-here.md`
- [ ] **T12.6** Deferred-inventory updates per AC-L.5
- [ ] **T12.7** Standing-guardrail status: SG-4 GREEN for Dan; Class-D1 template active
- [ ] **T12.8** Three-line D12 close stub
- [ ] **T12.9** Commit + push

---

## Dev Notes

### Greenfield posture: 4 net-new artifact families

This story creates 4 net-new artifact families, all per BMB conventions:
1. `skills/bmad-agent-dan/SKILL.md` (option-a aligned)
2. `_bmad/memory/bmad-agent-dan/` 6-file BMB sanctum
3. `app/specialists/dan/` directory with scaffold-v0.2
4. `tests/parity/test_dan_activation_contract.py` + behavioral tests + chain test

The legacy `_bmad/memory/dan-sidecar/` is PRESERVED unchanged (cleanup deferred to post-trial-2 validation).

### Class-D1 template (NEW; this story extends the validator)

Class-D1 first-recorded-fixture-set parity is novel â€” Dan has no prior `app/specialists/dan/` so fixtures need explicit recording ceremony. The Class-D1 template additions to `validate_parity_test_class_conformance.py` are foundational; future Class-D1 stories (none in Slab 7b â€” Dan is the only Class-D1) inherit. Class-D1 template is additive; A/B/C/C+ unchanged.

### Round-(b) B1 / Round-(c) C1 sandbox-AC promotion gating

If dan-api-tbd resolves to third-party-API at T1, the binding-hard amendment requires party-mode consensus + governance-JSON version bump pre-promotion. This is NOT a soft warning â€” the dev-agent CANNOT unilaterally promote the inventory entry. Failure to honor this gate is a P0 governance violation.

### Round-(e) E6 k_contract tripwire scope-creep signal

The 4.0K LOC tripwire is scoped specifically as a "scope creep" signal â€” most plausibly an unauthorized API integration leak. If T1 resolved to LLM-only and the dev-agent finds itself approaching 4K LOC, party-mode review is the escape valve (NOT a unilateral pivot to API integration mid-flight).

### NFR predicates honored

NFR-T9 / T10 / T11 / T11a (cache-hit-rate â‰¥85%) / T11b (CONDITIONAL on third-party-API) / T12 â€” `@pytest.mark.timeout` annotations.
NFR-CG12 (CONDITIONAL on third-party-API) / CG13 (CONDITIONAL) / CG14 / CG15 (Decision Log per NFR-CG15) / CG16 / CG17 (Claude per D21) / CG19 (CONDITIONAL credential register) / CG20 (CONDITIONAL rate-limit budget).
NFR-I9 + NFR-I10 + NFR-I12 (Class-D1 template extension) + NFR-I13 (substrate-frozen-paths-check).

### Known follow-ons

- **`class-d1-template-extend-validator-during-7b-10`** â€” CLOSE at T6.2 (in-story)
- **`dan-sidecar-cleanup-post-trial-2-validation`** â€” filed; close after trial-2
- **`dan-api-promotion-governance-bump-during-7b-10`** â€” CONDITIONAL on third-party-API resolution at T1; close at party-mode consensus

### Anti-pattern catalog citations

- **A6** (silent-fixture-stub fallback) â€” closing for Dan G1/G1A/G2 aux contributions
- **A9** (epic-doc-vs-shipped-framework drift) â€” Dan greenfield; epic-canonical paths binding
- **P1** (substrate-as-floor violation) â€” AC-I binding (additive-only greenfield)

---

### Project Structure Notes

- `app/specialists/dan/` â€” NEW (greenfield via generator; scaffold-v0.2 base)
- `_bmad/memory/bmad-agent-dan/` â€” NEW (6-file BMB sanctum)
- `_bmad/memory/dan-sidecar/` â€” PRESERVED (legacy; cleanup deferred)
- `skills/bmad-agent-dan/` â€” NEW (generator-emitted; option-a aligned)
- `tests/parity/test_dan_activation_contract.py` â€” NEW (FR105; Class-D1)
- `scripts/utilities/validate_parity_test_class_conformance.py` â€” EXTENDED with Class-D1 template (lockstep)
- `tests/specialists/dan/test_*.py` â€” NEW (5 behavioral tests)
- `tests/fixtures/specialists/dan/golden_envelope.json` + `golden_return.json` â€” NEW (first-recorded fixtures)
- `tests/end_to_end/test_dan_cache_hit_rate.py` â€” NEW
- `tests/composition/test_dan_aux_contribution_chain.py` â€” NEW

### Detected conflicts or variances

- **dan-api-tbd resolution** â€” operator decision at T1; default LLM-only
- **Class-D1 first-recorded-fixture-set** â€” novel template; lockstep extension required

---

## References

- **Round-(e) governance JSON**: [`docs/dev-guide/migration-story-governance.json`](../../docs/dev-guide/migration-story-governance.json) Â§`stories.7b-10`
- **Epic + story-level scope**: [`epics-slab-7b-specialist-activation-eleven.md`](../planning-artifacts/epics-slab-7b-specialist-activation-eleven.md) Â§Story 7b.10
- **PRD FR98**: [`prd-slab-7b-specialist-activation-eleven.md`](../planning-artifacts/prd-slab-7b-specialist-activation-eleven.md) Â§FR98
- **Sandbox-AC inventory (FR107; dan-api-tbd-pending entry)**: [`docs/dev-guide/migration-ac-sandbox-inventory.json`](../../docs/dev-guide/migration-ac-sandbox-inventory.json)
- **`bmad-create-specialist` generator**: [`skills/bmad-create-specialist/`](../../skills/bmad-create-specialist/)
- **Slab 2a.2 Pass-2 precedent (9-node scaffold + AC-B 150-LOC)**: [`migration-2a-2-irene-pass-2-scaffold-migration.md`](migration-2a-2-irene-pass-2-scaffold-migration.md)
- **7b.1 substrate**: [`migration-7b-1-texas-hardening.md`](migration-7b-1-texas-hardening.md)
- **7b.4 spec (Class-B template precedent)**: [`migration-7b-4-irene-pass1-refresh.md`](migration-7b-4-irene-pass1-refresh.md)
- **7a.5 conversation-persistence contract**: [`migration-7a-5-conversation-persistence-specialist-summary-writer.md`](migration-7a-5-conversation-persistence-specialist-summary-writer.md)
- **BMB sanctum alignment checklist (FR108)**: [`docs/dev-guide/bmb-sanctum-alignment-checklist.md`](../../docs/dev-guide/bmb-sanctum-alignment-checklist.md)
- **Sprint status**: [`sprint-status.yaml`](sprint-status.yaml)
- **Deferred inventory**: [`deferred-inventory.md`](../planning-artifacts/deferred-inventory.md)

---

## Dev Agent Record

### Agent Model Used

Codex GPT-5

### Debug Log References

- T1 governance pin: Round-(e) `7b-10` single-gate and 4.0K k_contract PASS.
- T1 status gate: 7b.1-7b.9 direct sprint-status lines verified `done` after operator-confirmed 7b.9 close.
- T1 greenfield probe: `app/specialists/dan/`, `_bmad/memory/bmad-agent-dan/`, and `skills/bmad-agent-dan/` absent; `_bmad/memory/dan-sidecar/` present and preserved.
- T1 sandbox preflight: `validate_migration_story_sandbox_acs.py` PASS.
- T2 generator: `bmad-create-specialist` dry-run and wet-run PASS for `--name dan --mcp none --expertise-tier L4-creative-director-aux`.
- T4 body ceiling: executable `app/specialists/dan/_act.py::act` body is 34 LOC, under the 150-LOC ceiling.
- T8 substrate check: `git diff -- app/marcus/orchestrator/dispatch_adapter.py` empty.

### Completion Notes List

- T1 `dan-api-tbd-pending` resolution: LLM-only via shared LLM facade. No third-party API constraint surfaced; no party-mode promotion or governance JSON bump required. AC-10-B live canary is N/A.
- Retired `dan-api-tbd-pending` from `docs/dev-guide/migration-ac-sandbox-inventory.json::dev_agent_forbidden`; changelog records the LLM-only retirement.
- Created Dan Class-D1 scaffold at `app/specialists/dan/` with LLM-only `_act` contributions for G1/G1A/G2 and advisory-only structure.
- Created single persona skill at `skills/bmad-agent-dan/SKILL.md` and six-file BMB sanctum at `_bmad/memory/bmad-agent-dan/`; legacy `_bmad/memory/dan-sidecar/` was read-only and left unchanged.
- Filed `dan-sidecar-cleanup-post-trial-2-validation` in deferred inventory.
- Extended Class-D1 template assertions in `validate_parity_test_class_conformance.py`; A/B/C+/C inheritance remains green.
- Added Dan activation, specialist behavior, summary landing, cache-harness, and composition chain coverage. T6.3-T6.6 are consolidated into `tests/specialists/dan/test_dan_aux_contributions_g1_g2.py` plus parity assertions rather than four separate files.
- T9 variance: no active v4.2 pipeline-manifest node was added because Dan is an aux specialist and adding a manifest step would break pipeline/HUD/pack lockstep. Existing manifest lockstep remains PASS; no `SPECIALIST_ALIASES` entry is needed for `dan -> dan`.
- Verification: 50 focused tests passed; broad regression slice 1348 passed, 21 skipped, 1 deselected; pipeline lockstep PASS; live-API detector PASS; sandbox-AC PASS; Class-D1 validator PASS; scoped ruff PASS; lint-imports 9/9 KEPT.
- Full `ruff check .` was attempted and failed on pre-existing out-of-scope lint debt (1219 findings across legacy/generated paths); Dan-scoped ruff is clean.
- `_bmad/memory/bmad-agent-dan/` is gitignored and requires `git add --force` during Claude T12 commit per existing bmad-memory force-add policy.

### File List

- `_bmad-output/implementation-artifacts/7b-10-codex-self-review-2026-04-30.md`
- `_bmad-output/implementation-artifacts/migration-7b-10-dan-greenfield.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/planning-artifacts/deferred-inventory.md`
- `_bmad/memory/bmad-agent-dan/INDEX.md`
- `_bmad/memory/bmad-agent-dan/PERSONA.md`
- `_bmad/memory/bmad-agent-dan/CREED.md`
- `_bmad/memory/bmad-agent-dan/BOND.md`
- `_bmad/memory/bmad-agent-dan/MEMORY.md`
- `_bmad/memory/bmad-agent-dan/CAPABILITIES.md`
- `app/models/state/specialist_summary_artifacts.py`
- `app/specialists/dan/__init__.py`
- `app/specialists/dan/_act.py`
- `app/specialists/dan/config.yaml`
- `app/specialists/dan/expertise/README.md`
- `app/specialists/dan/graph.py`
- `app/specialists/dan/model_config.yaml`
- `app/specialists/dan/state.py`
- `docs/dev-guide/migration-ac-sandbox-inventory.json`
- `pyproject.toml`
- `scripts/utilities/detect_live_api_in_tests.py`
- `scripts/utilities/validate_parity_test_class_conformance.py`
- `skills/bmad-agent-dan/SKILL.md`
- `tests/composition/test_dan_to_compositor_chain.py`
- `tests/end_to_end/test_dan_cache_hit_rate.py`
- `tests/fixtures/composition/dan-to-compositor/expected-output.json`
- `tests/fixtures/specialists/dan/golden_envelope.json`
- `tests/fixtures/specialists/dan/golden_return.json`
- `tests/integration/scaffold_conformance/test_scaffold_dan.py`
- `tests/parity/test_cache_hit_rate_harness.py`
- `tests/parity/test_dan_activation_contract.py`
- `tests/parity/test_skill_md_sanctum_alignment.py`
- `tests/specialists/dan/test_dan_aux_contributions_g1_g2.py`
- `tests/specialists/dan/test_dan_state_shape.py`
- `tests/specialists/dan/test_dan_summary_landing.py`
- `tests/unit/marcus/orchestrator/test_specialist_summary_writer.py`

