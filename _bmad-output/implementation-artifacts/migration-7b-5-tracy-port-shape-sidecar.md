# Migration Story 7b.5: Tracy Port-Shape + Sidecar Creation (Class C+) â€” Pass-2 Research Enrichment Companion

**Status:** done
**Sprint key:** `migration-7b-5-tracy-port-shape-sidecar`
**Epic:** Slab 7b Specialist Body Activation â€” `epic-slab-7b-specialist-activation-eleven`. **Wave 2b** (Class-C+ port-shape + sidecar emission BUNDLE; serial after Wave-2a 7b.4 close; Claude-authored spec / Codex-authored implementation per NFR-CG17 + D21 â€” *spec author is Claude per uniform Slab 7b workflow; "Codex-authored" in epic prose refers to dev-cycle ownership only*).
**Pts:** 5 | **Gate:** single (per `docs/dev-guide/migration-story-governance.json::stories.7b-5`; rationale: null; per Slab 2b.1 TEMPLATE pattern) | **K-target:** ~1.5Ã— (target ~36 tests / floor ~28; ~3.3K LOC; **Round-(e) E6 k_contract tripwire 2.7K â†’ Wave-2b close K-aggregate escalation**).
**Author:** **Claude** spec / **Codex** dev. **Review:** **Claude** T11 `bmad-code-review`.
**Wave-2b precondition:** 7b.4 (Wave-2a Irene Pass-1) `done`. **Note:** Wave-1 close tripwire fired marginal at 2026-04-29 (~2.85K aggregate); Wave-2a opens at upper-band K-target per Round-(a) Amelia A3; Wave-2b inherits the upper-band signal but is a separate evaluation per Round-(e) E6 k_contract.

---

## Round-(e) Governance Inheritance

Round-(e) freeze landed 2026-04-29. Load-bearing for 7b.5:

- **E4 binding-hard:** `required_ac_reference_paths: ["skills/bmad-agent-texas/references/retrieval-contract.md"]` â€” story AC must explicitly cite Texas retrieval-contract; AC coverage of the Tracyâ†”Texas retrieval-shape interface is required (not optional). bmad-create-story reads this file at T1 (this spec authoring honored it).
- **E6 k_contract block:** scope=Pass-2 enrichment + sidecar 4-file BMB; tripwire 2.7K â†’ Wave-2b close K-aggregate escalation; if exceeds, Wave-3 first-port (7b.6 Gary) opens at upper-band K-target + 7b.7 Kira + 7b.8 Enrique pre-authorized for dual-gate escalation via Round-(e) E3 conditional_gate_override hooks.

**T1 readiness verification command:**
```bash
.venv/Scripts/python.exe -c "import json; d = json.load(open('docs/dev-guide/migration-story-governance.json', encoding='utf-8')); assert d['version'] == '2026-04-29-slab7b-twelve-stories'; entry = d['stories']['7b-5']; assert entry['k_contract']['tripwire_threshold_kloc'] == 2.7; assert entry['required_ac_reference_paths'] == ['skills/bmad-agent-texas/references/retrieval-contract.md']; print('Round-(e) E4+E6 verified PASS for 7b-5')"
```

---

## T1 Readiness Block

### Required-readings cascade (10-reading)

1. **Round-(e) governance JSON** â€” `docs/dev-guide/migration-story-governance.json` Â§`stories.7b-5`. Confirm `single-gate`, `expected_k_target: 1.5`, `k_contract.tripwire_threshold_kloc: 2.7`, `required_ac_reference_paths` present.
2. **Epic + story-level scope** â€” [`epics-slab-7b-specialist-activation-eleven.md`](../planning-artifacts/epics-slab-7b-specialist-activation-eleven.md) Â§Story 7b.5 (lines 623-670).
3. **PRD Â§FR93** â€” [`prd-slab-7b-specialist-activation-eleven.md`](../planning-artifacts/prd-slab-7b-specialist-activation-eleven.md) Â§FR93. Tracy research-shaped intent enrichment for Pass-2 + sidecar greenfield + 4-file BMB pattern + 9-node scaffold per Slab 2b.1 TEMPLATE + live LLM-only binding.
4. **Texas retrieval-contract (Round-(e) E4 binding-hard reference)** â€” [`skills/bmad-agent-texas/references/retrieval-contract.md`](../../skills/bmad-agent-texas/references/retrieval-contract.md). Tracy emits `RetrievalIntent` objects with `intent: str` + `provider_hints: list[ProviderHint]` (REQUIRED v1; no auto-discovery) + `acceptance_criteria` three-tier (`mechanical` / `provider_scored` / `semantic_deferred`). Tracy does NOT translate provider DSLs â€” that's the per-provider `RetrievalAdapter` adapter's responsibility. Cross-validation first-class via `cross_validate: true` flag. Tracy's research-shaped enrichment in Pass-2 produces `RetrievalIntent` artifacts that Texas dispatches.
5. **Slab 2b.1 TEMPLATE precedent (CRITICAL â€” 9-node scaffold + Class-C-shaped pattern)** â€” [`migration-2b-1-gary-scaffold-migration.md`](migration-2b-1-gary-scaffold-migration.md). 9-node scaffold + AC-B 150-LOC ceiling discipline + bounded-scope acts + sandbox-AC governance. Tracy adapts this for Class-C+ (port-shape WITH sidecar greenfield emission, LLM-only).
6. **Specialist migration template (R1-R14)** â€” [`docs/dev-guide/specialist-migration-template.md`](../../docs/dev-guide/specialist-migration-template.md). Seven (now expanded to fourteen) TEMPLATE rules; this story extends the rule corpus with R15 if novel patterns surface (else inheritor only).
7. **Wave-2a close evidence** â€” verify 7b.4 (Irene Pass-1) `done` in `sprint-status.yaml`. Read `tripwire_events::wave_1_close::fired_verdict` (already known: `marginal-fired`); upper-band K-target signal carries forward.
8. **7b.1 substrate (Wave-1 prerequisite)** â€” verify all 4 CREATE-task artifacts present: `tests/parity/_sanctum_parity_base.py` + `tests/composition/_chain_test_base.py` + `scripts/utilities/validate_parity_test_class_conformance.py` + `tests/parity/README.md` Â§"FR105 + Errata 4 layout decision".
9. **Class-B template precedent (from 7b.4)** â€” `validate_parity_test_class_conformance.py` extended with Class-B template at 7b.4 close. This story extends with **Class-C+ template** in lockstep with the parity test landing (LOCKSTEP foundational deliverable).
10. **CLAUDE.md** â€” Â§LangChain/LangGraph migration governance + Â§BMAD sprint governance + Â§NFR-CG17 + D21 (Codex dev-cycle ownership for Class-C/C+ port-shape stories).

### Tracy current-state probe + drift surfacing

```bash
ls app/specialists/tracy/                           # __init__.py expertise/ graph.py model_config.yaml posture_dispatch.py state.py (slab-2b era; passthrough body)
ls _bmad/memory/bmad-agent-tracy/ 2>/dev/null       # NOT YET PRESENT â€” sidecar greenfield; this story creates 4-file BMB pattern
ls _bmad/memory/tracy-sidecar/ 2>/dev/null          # NOT PRESENT either â€” Tracy is a fresh greenfield (no legacy sidecar)
ls skills/bmad-agent-tracy/                         # SKILL.md (placeholder; minimal â€” needs sanctum-aware activation order on update)
```

**Two drifts surface at T1:**

**âš ï¸ Drift #1 â€” Sanctum greenfield (Class-C+ 4-file pattern; NOT 6-file BMB):** Tracy is the FIRST Class-C+ specialist; sanctum at `_bmad/memory/bmad-agent-tracy/` is greenfield. Per epic Story 7b.5 line 642 + PRD Â§FR93, the 4-file pattern is canonical for Class-C+:
- `INDEX.md` â€” essential context loaded on activation
- `PERSONA.md` â€” full BMB persona
- `chronology.md` â€” session and production-run history
- `access-boundaries.md` â€” read/write/deny zones

**Distinct from Class-A 6-file BMB pattern (Texas/Quinn-R/Vera).** Class-C+ pattern is intentionally lighter (matches port-shape role; no `CREED.md`/`BOND.md`/`MEMORY.md`/`CAPABILITIES.md` files). The class-conformance validator's Class-C+ template (CREATE task at T2) asserts the 4-file pattern.

**âš ï¸ Drift #2 â€” Existing `posture_dispatch.py` legacy module at `app/specialists/tracy/`:** Slab-2b era carry-forward. Wave-2b hardening should consume it as a helper (NOT replace) per substrate-as-floor invariant. Verify import-stability at T1.

### Wave 0 + 7b.1 substrate + Wave-1 + Wave-2a sweeps

```bash
# Wave 0 (commit 9ed6fcb)
ls docs/dev-guide/bmb-sanctum-alignment-checklist.md docs/dev-guide/sanctum-exception-categories.json docs/dev-guide/operator-control-parity-template.md docs/dev-guide/migration-ac-sandbox-inventory.json skills/bmad-agent-cora/SKILL.md
ls docs/dev-guide/scaffolds/scaffold-v0.2-D2-pipeline/

# 7b.1 T2 substrate
ls tests/parity/_sanctum_parity_base.py tests/composition/_chain_test_base.py scripts/utilities/validate_parity_test_class_conformance.py
grep -c "FR105 + Errata 4 layout decision" tests/parity/README.md  # >=1 expected

# Wave-1 close (7b.1+7b.2+7b.3 all `done`)
.venv/Scripts/python.exe -c "import yaml; d = yaml.safe_load(open('_bmad-output/implementation-artifacts/sprint-status.yaml', encoding='utf-8')); assert all(d['development_status'][k].startswith('done') for k in ('migration-7b-1-texas-hardening','migration-7b-2-quinn-r-hardening','migration-7b-3-vera-hardening')); print('Wave-1 closed OK')"

# Wave-2a close (7b.4 Irene Pass-1 done)
.venv/Scripts/python.exe -c "import yaml; d = yaml.safe_load(open('_bmad-output/implementation-artifacts/sprint-status.yaml', encoding='utf-8')); assert d['development_status']['migration-7b-4-irene-pass1-refresh'].startswith('done'); print('Wave-2a closed OK')"
```

All paths must exist + all four wave gates closed. If any absent â†’ HALT.

### Class-C+ template extension required (LOCKSTEP)

This story is the **first Class-C+ specialist** to land per NFR-I12. The dev-agent (Codex) must extend `scripts/utilities/validate_parity_test_class_conformance.py` with Class-C+ template assertions in lockstep with this story's parity test landing. Class-C+ template asserts:
- 4-file BMB sidecar pattern (NOT 6-file)
- live-LLM binding (no third-party API)
- cache-hit-rate harness wired (FR106; â‰¥85% post-warm-up)
- sidecar-emission parity (sidecar present + activation-order in SKILL.md)

### Sandbox-AC validator pre-flight

```bash
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py \
  _bmad-output/implementation-artifacts/migration-7b-5-tracy-port-shape-sidecar.md
```
Expect PASS. Tracy is LLM-only (no third-party API; no sandbox-AC inventory entry needed per R5 Amelia-scope-amendment). Live-LLM verification via `@pytest.mark.llm_live` auto-skip on placeholder API key.

### Standing pre-flight items

1. Severance posture confirmed.
2. `state/config/substrate-frozen-paths.yaml` honored â€” no diff to `app/marcus/orchestrator/dispatch_adapter.py:70-95`.
3. Tracy is Class-C+ (port-shape WITH sidecar emission + LLM-only); distinct dev-cycle ownership: spec authored by Claude (uniform Slab 7b workflow), implementation by Codex per NFR-CG17 + D21.
4. NFR-T9-T12 wall-clock ceilings hold.

---

## Story

As a **migration dev agent**,
I want **Tracy to execute a Class-C+ port-shape â€” research-shaped intent enrichment for Pass-2 (emitting `RetrievalIntent` artifacts per Texas retrieval-contract) + sidecar greenfield at `_bmad/memory/bmad-agent-tracy/` with full 4-file BMB pattern + 9-node scaffold per Slab 2b.1 TEMPLATE + live LLM-only binding (`gpt-5.4` via `app.models.adapter`; no third-party API) + cache-hit-rate harness â‰¥85% post-warm-up â€” AND I want the Class-C+ template extension to `validate_parity_test_class_conformance.py` landing in lockstep**,
So that **(a) Pass-2 narration carries real research enrichment (not passthrough), (b) Tracy's research enrichment respects the Texas retrieval-contract interface (RetrievalIntent shape; provider_hints required; acceptance_criteria three-tier), (c) the BMB sidecar pattern is established as canonical for Class-C+ class (4-file pattern), (d) SG-4 sanctum-alignment is enforced for Tracy via the FR101 parity test inheriting `SanctumParityTestBase` from 7b.1 substrate with Class-C+ template assertions, and (e) Wave-3 first-port (7b.6 Gary) inherits the Class-C+ template substrate**.

---

## Acceptance Criteria

All ACs are dev-agent-executable (sandbox-AC compliant). No third-party API live-binding. Live-LLM tests tagged `@pytest.mark.llm_live`; auto-skip on placeholder `OPENAI_API_KEY`.

### AC-7b.5-A â€” T1 readiness verification + drift resolution

**Given** the Round-(e) E4 + E6 amendments + Wave-1 close (marginal-fired) + Wave-2a close (7b.4 done)
**When** the dev agent runs T1 readiness
**Then** all 10 readings cascade complete; Round-(e) E4+E6 verification command exits 0; Wave-0 + 7b.1-T2 + Wave-1 + Wave-2a sweeps PASS; sandbox-AC validator PASS pre-flight
**And** Drift #1 resolution recorded: sanctum at `_bmad/memory/bmad-agent-tracy/` (greenfield); pattern = **4-file BMB** (Class-C+ canonical; NOT 6-file)
**And** Drift #2 acknowledged: legacy `posture_dispatch.py` consumed (NOT replaced).

### AC-7b.5-B â€” 9-node scaffold port-shape per Slab 2b.1 TEMPLATE

**Given** the canonical 9-node scaffold contract at `tests/integration/scaffold_conformance/scaffold_contract.py::SCAFFOLD_NODE_IDS`
**And** the Slab 2b.1 TEMPLATE pattern (`receive/plan/act/verify/reflect/emit_spans/gate_decision/finalize/handoff`)
**When** the dev-agent (Codex) authors Tracy's port-shape
**Then** `app/specialists/tracy/_act.py` lands with the bounded body + `app/specialists/tracy/graph.py` builds the 9-node scaffold mirroring 2b.1 TEMPLATE shape
**And** `_act` body length is **â‰¤150 LOC** per AC-B ceiling (Slab 2a.2 + 2b.1 precedent); HALT-AND-SURFACE re-scope decision if exceeds
**And** `validate_scaffold("tracy", build_tracy_graph()).is_conforming is True`; ruff clean; import-linter C1 lane-isolation PASS.

### AC-7b.5-C â€” Research-shaped intent enrichment per Texas retrieval-contract

**Given** Tracy dispatched at Pass-2 enrichment phase (post-Irene Pass-1 lesson plan locked at G1A; pre-Irene Pass-2)
**And** the Texas retrieval-contract at [`skills/bmad-agent-texas/references/retrieval-contract.md`](../../skills/bmad-agent-texas/references/retrieval-contract.md) (Round-(e) E4 binding-hard reference)
**When** Tracy's `_act` body executes
**Then** Tracy emits one or more `RetrievalIntent` objects with required v1 fields:
  - `intent: str` (natural-language description of what's being researched)
  - `provider_hints: list[ProviderHint]` REQUIRED â€” no auto-discovery (each entry `{provider: <id>, params: <dict>}`; provider IDs from `provider_directory.list_providers(shape="retrieval", status_in={ready, stub})`)
  - `acceptance_criteria` three-tier (`mechanical` / `provider_scored` / `semantic_deferred`)
  - optional `cross_validate: true` for first-class cross-provider fan-out
**And** Tracy does NOT translate per-provider DSLs â€” that's the adapter's responsibility (knowledge-locality discipline per Dr. Quinn)
**And** the emitted `RetrievalIntent` is shape-compatible with what Texas dispatches downstream (verified via chain test).
**Test pin:** `tests/specialists/tracy/test_tracy_retrieval_intent_emission.py` â€” synthetic Pass-2 directive; assert RetrievalIntent shape per retrieval-contract; parametrize over `cross_validate` true/false.

### AC-7b.5-D â€” Class-C+ sidecar greenfield: 4-file BMB pattern at canonical path

**Given** the FR93 sidecar emission requirement + epic Story 7b.5 line 642 binding 4-file pattern
**When** the dev-agent (Codex) authors Tracy's sidecar
**Then** `_bmad/memory/bmad-agent-tracy/` directory lands with 4-file BMB pattern:
  1. `INDEX.md` â€” essential context loaded on activation (per `docs/dev-guide/sanctum-reference-conventions.md`)
  2. `PERSONA.md` â€” full BMB persona (research-enrichment voice; consume from existing `skills/bmad-agent-tracy/SKILL.md` placeholder + author novel content per BMB checklist)
  3. `chronology.md` â€” session and production-run history (initial entry: "2026-04-XX â€” Tracy Wave-2b activation; first-breath ceremony deferred to operator")
  4. `access-boundaries.md` â€” read/write/deny zones (READ: course-content/, retrieval-contract spec, lesson-plan locked artifacts; WRITE: state/runs/<run_id>/tracy/; DENY: app/marcus/, dispatch_adapter.py)
**And** `skills/bmad-agent-tracy/SKILL.md` is updated to reference `_bmad/memory/bmad-agent-tracy/` as activation-time hot-load batch (replaces placeholder body; minimal frontmatter `name` + `description` per FR101 R1-restated contract)
**And** Class-C+ sidecar pattern documented in `docs/dev-guide/sanctum-reference-conventions.md` (lockstep doc update if needed; first Class-C+ enshrines the 4-file pattern as canonical).

### AC-7b.5-E â€” Live LLM-only binding (no third-party API)

**Given** Tracy's live LLM-only requirement (no third-party API; sandbox-AC inventory entry NOT required per R5 Amelia-scope-amendment)
**When** Tracy invokes its `_act` body
**Then** the LLM call is made against `gpt-5.4` via `app.models.adapter.ChatOpenAIAdapter` with `tier_request: reasoning` (research enrichment is reasoning-class workload)
**And** `scripts/utilities/detect_live_api_in_tests.py` AST-scan PASSES â€” no `from gamma_client/kling_client/elevenlabs_client/wondercraft_client import` patterns in Tracy's CI test files
**And** `model_config.yaml` declares `default_model: "gpt-5.4"` + `temperature_default: 0.3` (research enrichment creativity tolerance) + per-node override map.
**Test pin:** `tests/specialists/tracy/test_tracy_no_third_party_api_imports.py` â€” AST-scan assertion; FAIL if any third-party adapter import detected.

### AC-7b.5-F â€” Cache-hit-rate harness (FR106; Class-C+ inheritance from 7b.4 pattern)

**Given** the cache-hit-rate harness requirement (FR106; ten LLM specialists incl. Tracy)
**When** the dev-agent wires Tracy into the harness
**Then** harness runs N=10 in-process against `gpt-5.4` with `prompt_tokens >> 1024` MF2 floor (per Slab 2a.2 MF2 + 7b.4 inheritance)
**And** `median[2:] >= 85%` post-warm-up (per Slab 2a.2 MF1 disposition rule)
**And** prompt-token floor pre-check raises `pytest.fail("prefix below OpenAI cache threshold 1024 tokens; ...")` if envelope undersized
**And** cache-metric source: OpenAI usage API `prompt_tokens_details.cached_tokens` (per Slab 2a.2 MF5; NOT LangSmith trace parsing).
**Test pin:** `tests/end_to_end/test_tracy_cache_hit_rate.py` â€” `@pytest.mark.llm_live`; auto-skip on placeholder API key; operator-gated Completion-Notes evidence block.

### AC-7b.5-G â€” SG-4 Sanctum Alignment (FR100 + FR101 â€” Tracy first-Class-C+-enforcement)

**Given** the SG-4 sanctum-alignment requirement (option-a required at port per `slab7bSpecialistRoster.specialists.tracy.sanctumAlignment`)
**When** the dev-agent commits Tracy port-shape
**Then** `skills/bmad-agent-tracy/SKILL.md` is verified option-a sanctum-aligned per BMB checklist (FR108):
  - YAML frontmatter MINIMAL (`name` + `description` only)
  - SKILL.md body references `_bmad/memory/bmad-agent-tracy/` sanctum dir as activation-time hot-load batch
**And** the sanctum dir at `_bmad/memory/bmad-agent-tracy/` carries 4-file BMB pattern (per AC-D; Class-C+ canonical)
**And** the parity test `tests/parity/test_skill_md_sanctum_alignment.py` PASSES for Tracy with **Class-C+ template assertions** (4-file pattern; NOT 6-file). The base class `SanctumParityTestBase::assert_sanctum_path_equality()` accepts a `class_template_id` discriminator; Class-C+ branch asserts 4-file (`INDEX.md` / `PERSONA.md` / `chronology.md` / `access-boundaries.md`).

### AC-7b.5-H â€” FR105 per-specialist parity test (Class-C+ template extension; LOCKSTEP)

**Given** the Errata 4 verdict-flat layout + 7b.1's `_sanctum_parity_base.py` substrate + 7b.4's Class-B template extension
**When** the dev-agent (Codex) authors Tracy's activation-contract test + extends the validator
**Then** `tests/parity/test_tracy_activation_contract.py` (flat) lands inheriting `SanctumParityTestBase` with `class_template_id = "C+"` (or `"Cplus"` if symbol-safe), `specialist_name = "tracy"`
**And** the test asserts **Class-C+ live-API + cache-hit-rate + sidecar-emission parity** per NFR-I12 Class-C+ template:
  - (i) 9-node scaffold conformance via `validate_scaffold()`
  - (ii) 4-file BMB sidecar pattern present (NOT 6-file) at `_bmad/memory/bmad-agent-tracy/`
  - (iii) live LLM-only binding (no third-party API import; `detect_live_api_in_tests.py` AST-scan PASS)
  - (iv) cache-hit-rate harness wired (`tests/end_to_end/test_tracy_cache_hit_rate.py` exists + `@pytest.mark.llm_live`)
  - (v) RetrievalIntent emission shape per Texas retrieval-contract
  - (vi) SKILL.md activation-order references the sanctum
  - (vii) cold-activation smoke
**And** **`scripts/utilities/validate_parity_test_class_conformance.py` extended with Class-C+ template assertions in lockstep** (additive; Class-A + B unchanged).
**And** `@pytest.mark.timeout(30)` per NFR-T9; <120s aggregate per NFR-T12.
**And** the validator PASSES on this test file when run.

### AC-7b.5-I â€” Sandbox-AC governance + substrate-as-floor invariant

**Given** the sandbox-AC inventory governance requirement + FR113 + NFR-I13
**When** `validate_migration_story_sandbox_acs.py` runs on this spec
**Then** PASS (no forbidden CLI in dev-agent ACs)
**And** Tracy-specific: NO sandbox-AC inventory entry needed (LLM-only via `gpt-5.4`; per R5 Amelia-scope-amendment)
**And** **no diff hunk touches `app/marcus/orchestrator/dispatch_adapter.py:70-95`** absent ceremony.

### AC-7b.5-J â€” Chain test inheriting `ChainTestBase` (Tracyâ†”Texas retrieval-shape)

**Given** NFR-CG14 chain-test PR pre-merge requirement + 7b.1's `_chain_test_base.py` substrate
**And** Round-(e) E4 binding-hard requires explicit AC coverage of Tracyâ†”Texas retrieval-shape interface
**When** the dev agent authors the Tracy chain test
**Then** `tests/composition/test_tracy_to_texas_chain.py` lands inheriting `ChainTestBase`
**And** the test asserts: (i) Tracy's `RetrievalIntent` emission is shape-compatible with Texas's `dispatch_retrieval(directive_path, bundle_dir)` signature; (ii) provider_hints structurally validate against `provider_directory.list_providers()` shape; (iii) acceptance_criteria three-tier shape preserved across handoff
**And** wall-clock <120s (NFR-CG14a budget; `@pytest.mark.timeout(120)`).

### AC-7b.5-K â€” Wave-2b close tripwire ledger (Round-(e) E2 + E6 binding)

**Given** the Round-(e) E2 amendment landed `tripwire_events: []` schema slot at `sprint-status.yaml`
**And** Round-(e) E6 k_contract on 7b-5 (tripwire 2.7K â†’ Wave-2b close K-aggregate escalation)
**When** this story closes (post-T11 review)
**Then** the dev-agent appends a NEW `wave_2b_close` entry to `sprint-status.yaml::tripwire_events` (separate from `wave_1_close` already-fired entry):
```yaml
tripwire_events:
  # ... existing wave_1_close entry ...
  - tripwire_id: wave_2b_close
    story_owner: 7b-5
    fired_at: <YYYY-MM-DD>
    fired_verdict: <true|false>          # true if 7b-5 LOC > 2.7K threshold
    measured_value:
      kloc: <N.NN>
      tests_added: <N>
      act_body_loc: <N>
      ceiling_breach: false              # AC-B 150-LOC ceiling honored
    escalation_action_taken: |
      <none|wave_3_first_port_gary_at_upper_band_k_target+7b-7+7b-8_pre_authorized_dual_gate_via_E3_hooks>
    decision_record_link: <links to story spec + code-review report>
```
**And** if `fired_verdict: true`, escalation per Round-(e) E6: Wave-3 first-port (7b.6 Gary) opens at upper-band K-target; 7b.7 Kira + 7b.8 Enrique conditional_gate_override hooks (Round-(e) E3) pre-authorized to flip dual-gate.

### AC-7b.5-L â€” Codex deployment binding (NFR-CG17)

**Given** the Codex deployment binding (NFR-CG17 + D21) for Class-C/C+ port-shape stories
**When** this story is implemented
**Then** **Codex authors the implementation** (T1-T9 dev + T10 G6 self-review) per Slab 2b.1 TEMPLATE pattern
**And** **Claude reviews via `bmad-code-review`** at T11 (mutual-handoff per Slab 7a NEW CYCLE precedent; CLAUDE.md sprint governance)
**And** the spec was authored by Claude (uniform Slab 7b workflow per operator clarification 2026-04-29 mid-Wave-1).

### AC-7b.5-M â€” Composition Spec Decision Log entry (NFR-CG15)

**Given** the NFR-CG15 Decision Log entry requirement at `docs/dev-guide/composition-specification.md` Â§10
**When** Tracy lands the Class-C+ template + 4-file BMB sidecar pattern
**Then** Decision Log entry filed with:
  - Date: 2026-04-XX
  - Decision: Class-C+ canonical sanctum pattern is **4-file BMB** (`INDEX.md` / `PERSONA.md` / `chronology.md` / `access-boundaries.md`); distinct from Class-A 6-file BMB pattern
  - Rationale: Class-C+ port-shape role is lighter than Class-A persona-driven hardening; 4-file pattern matches the role
  - Inheritance: Tracy is the seed exemplar; future Class-C+ specialists (none currently in Slab 7b â€” Tracy is the only Class-C+) inherit
  - Related artifacts: `validate_parity_test_class_conformance.py::Class-C+ template`; `docs/dev-guide/sanctum-reference-conventions.md`

### AC-7b.5-N â€” Close protocol

**Given** all prior ACs PASS + bmad-code-review returns PASS or PASS-WITH-PATCH-applied + regression baseline holds
**When** the story closes
**Then** at close:
  1. **sprint-status.yaml** flip: `migration-7b-5-tracy-port-shape-sidecar: in-progress â†’ review â†’ done`
  2. **Wave-2b close tripwire ledger entry** appended per AC-K
  3. **next-session-start-here.md** updated: pivot to Wave 3 (7b.6 Gary first-port-shape) opening
  4. **Deferred-inventory updates**: any new follow-ons surfaced during dev filed; `bmad-memory-gitignore-force-add-policy` follow-on may need Class-C+ note appended
  5. **Standing-guardrail status**: SG-4 GREEN for Tracy; Class-C+ template active in validator; Composition Spec Â§10 Decision Log entry filed
  6. **Three-line D12 close stub** per Slab 7a precedent

---

## Tasks / Subtasks

### T1 â€” T1 readiness verification + drift resolution
- [x] **T1.1** Round-(e) E4+E6 governance JSON verification
- [x] **T1.2** 10-reading required cascade
- [x] **T1.3** Wave-1 close + Wave-2a close evidence (4 stories `done`)
- [x] **T1.4** Wave 0 + 7b.1 substrate sweep
- [x] **T1.5** Tracy current-state probe â€” 2 drift items
- [x] **T1.6** Drift resolution recorded
- [x] **T1.7** Sandbox-AC validator pre-flight

### T2 â€” Class-C+ template extension to validator (LOCKSTEP foundational deliverable)
- [x] **T2.1** Extend `scripts/utilities/validate_parity_test_class_conformance.py` with Class-C+ template assertions (4-file BMB sidecar; LLM-only AST-scan; cache-hit-rate harness wired; RetrievalIntent shape) â€” additive; A + B unchanged
- [x] **T2.2** Verify validator PASSES on existing Class-A (Texas/Quinn-R/Vera) + Class-B (Irene Pass-1) tests post-extension

### T3 â€” Tracy sanctum greenfield + sidecar 4-file authoring (AC-D)
- [x] **T3.1** Author 4 BMB files at `_bmad/memory/bmad-agent-tracy/` (`INDEX.md` / `PERSONA.md` / `chronology.md` / `access-boundaries.md`) per BMB checklist
- [x] **T3.2** Update `skills/bmad-agent-tracy/SKILL.md` â€” minimal frontmatter + activation-order body referencing sanctum
- [x] **T3.3** Update `docs/dev-guide/sanctum-reference-conventions.md` if Class-C+ 4-file pattern needs canonical documentation (lockstep)

### T4 â€” Tracy `_act` body + 9-node scaffold (AC-B + AC-C + AC-E)
- [x] **T4.1** Author `app/specialists/tracy/_act.py` â€” bounded body emitting `RetrievalIntent` per Texas retrieval-contract (AC-C)
- [x] **T4.2** Update `app/specialists/tracy/graph.py` â€” 9-node scaffold per Slab 2b.1 TEMPLATE; delegate to `_act.py::act` (per Texas/Quinn-R/Vera precedent)
- [x] **T4.3** Wire `gpt-5.4` LLM binding via `app.models.adapter.ChatOpenAIAdapter` (`tier_request: reasoning`)
- [x] **T4.4** Consume legacy `posture_dispatch.py` as helper (NOT replace) per substrate-as-floor
- [x] **T4.5** Wire 7a.5 specialist-summary-writer (Tracy verdicts land at `runs/<run_id>/specialist-summaries/tracy-<gate>-<timestamp>.md`)
- [x] **T4.6** **AC-B 150-LOC ceiling discipline:** `_act` body â‰¤150 LOC; HALT-AND-SURFACE re-scope if exceeds

### T5 â€” Cache-hit-rate harness (AC-F)
- [x] **T5.1** `tests/end_to_end/test_tracy_cache_hit_rate.py` â€” `@pytest.mark.llm_live`; per Slab 2a.2 MF1+MF2+MF5 discipline + 7b.4 Class-B precedent
- [x] **T5.2** Operator-gated Completion-Notes evidence block

### T6 â€” Parity + behavioral tests (AC-G + AC-H)
- [x] **T6.1** `tests/parity/test_tracy_activation_contract.py` (flat; Class-C+ template) â€” AC-H
- [x] **T6.2** `tests/specialists/tracy/test_tracy_retrieval_intent_emission.py` â€” AC-C
- [x] **T6.3** `tests/specialists/tracy/test_tracy_no_third_party_api_imports.py` â€” AC-E
- [x] **T6.4** `tests/specialists/tracy/test_tracy_sidecar_4_file_pattern.py` â€” AC-D
- [x] **T6.5** `tests/specialists/tracy/test_tracy_summary_landing.py` â€” 7a.5 facade
- [x] **T6.6** `tests/composition/test_tracy_to_texas_chain.py` â€” inherits ChainTestBase (AC-J)
- [x] **T6.7** Wall-clock annotations + `validate_parity_test_class_conformance.py` PASS on Class-C+

### T7 â€” SG-4 sanctum alignment verification (AC-G)
- [x] **T7.1** Verify `skills/bmad-agent-tracy/SKILL.md` minimal frontmatter
- [x] **T7.2** `tests/parity/test_skill_md_sanctum_alignment.py` PASSES for Tracy with Class-C+ template

### T8 â€” Substrate-as-floor verification (AC-I)
- [x] **T8.1** `git diff` verification â€” no diff to dispatch_adapter.py:70-95

### T9 â€” Composition Spec Decision Log entry (AC-M)
- [x] **T9.1** File NFR-CG15 Decision Log entry at `docs/dev-guide/composition-specification.md` Â§10 with Class-C+ pattern decision

### T10 â€” Regression baseline + sandbox-AC final
- [x] **T10.1** Full regression battery (target: â‰¥696 + cumulative Wave-1/2a/2b â‰ˆ 800-850 passed; 19 skipped + Wanda known-flake)
- [x] **T10.2** `ruff check` story-scoped clean
- [x] **T10.3** `lint-imports.exe` 9/9 KEPT
- [x] **T10.4** Sandbox-AC validator final PASS

### T11 â€” Codex G6 self-review (NEW CYCLE T10 by Codex per AC-L)
- [x] **T11.1** Codex authors G6 self-review at `_bmad-output/implementation-artifacts/7b-5-codex-self-review-2026-04-XX.md`
- [x] **T11.2** Status flip `in-progress â†’ review`

### T12 â€” Claude bmad-code-review + close
- [ ] **T12.1** Claude runs `bmad-code-review` at `7b-5-code-review-2026-04-XX.md`
- [ ] **T12.2** Remediation cycle 1 if needed
- [ ] **T12.3** Append Wave-2b-close tripwire ledger entry per AC-K
- [ ] **T12.4** Sprint-status flip `review â†’ done`
- [ ] **T12.5** Update `next-session-start-here.md`: pivot to Wave 3 (7b.6 Gary)
- [ ] **T12.6** Deferred-inventory updates per AC-N.4
- [ ] **T12.7** Standing-guardrail status: SG-4 GREEN for Tracy; Class-C+ template active in validator
- [ ] **T12.8** Three-line D12 close stub
- [ ] **T12.9** Commit + push (note: `_bmad/memory/bmad-agent-tracy/` likely gitignored â€” `git add --force` per `bmad-memory-gitignore-force-add-policy` follow-on)

---

## Dev Notes

### Round-(e) E4 binding-hard reference

This story has the unique distinction of being the only Slab 7b story with a `required_ac_reference_paths` binding in the governance JSON. The Texas retrieval-contract at `skills/bmad-agent-texas/references/retrieval-contract.md` is canonical-required reading; AC-C explicitly cites the path. The chain test at AC-J operationally validates the interface compatibility.

### Class-C+ template (NEW; this story extends the validator)

7b.1 landed Class-A; 7b.4 extended with Class-B; this story extends with Class-C+. Class-C+ template is additive; Class-A + B unchanged. The Class-C+ template will be inherited by 7b.6/7b.7/7b.8/7b.9 (Class-C; same 4-file sidecar pattern) â€” Class-C is structurally a subset of Class-C+ (no sidecar emission requirement, but still 4-file pattern if sanctum exists). Future stories may further extend with Class-C-only template if Class-C diverges meaningfully from Class-C+.

### Wave-2b open at upper-band K-target (Round-(a) Amelia A3 escalation from Wave-1 close)

Wave-1 close tripwire fired marginal at 2026-04-29; Wave-2a opened at upper-band; Wave-2b inherits the upper-band signal. K-target ~1.5Ã— / 36 tests / floor 28 / 3.3K LOC stays as-is at story open; if T1 K-projection trends >2.7K aggregate (closer to 3.5K upper-band), Codex flags pre-T2 for party-mode awareness (NOT auto-escalation; Round-(e) E6 tripwire fires at 2.7K threshold per spec).

### Live LLM-only â€” Tracy is NOT third-party-API

Tracy uses `gpt-5.4` for research enrichment. NO third-party API. Sandbox-AC inventory entry NOT required per R5 Amelia-scope-amendment. The `detect_live_api_in_tests.py` AST-scan at AC-E enforces this structurally.

### NFR predicates honored

NFR-T9 / T10 / T11 / T11a (cache-hit-rate â‰¥85%) / T11b / T12 â€” `@pytest.mark.timeout` annotations.
NFR-CG13 (no live-API in CI; trivial since LLM-only) / CG14 / CG14a / CG15 (Decision Log entry â€” AC-M) / CG16 (bmad-code-review pre-close) / CG17 (Codex dev) / CG20 (rate-limit budget â€” N/A, LLM-only).
NFR-I9 + NFR-I10 + NFR-I12 (Class-C+ template extension) + NFR-I13.

### Known follow-ons

- **`class-c-plus-template-extend-validator-during-7b-5`** â€” CLOSE at T2 (in-story; lockstep)
- **`bmad-memory-gitignore-force-add-policy`** â€” recurring; affects Tracy sanctum at commit; track at this story T12 and aggregate observations across Slab 7b
- **Class-C template sub-discrimination** â€” file as named-but-not-filed if Wave-3 Class-C stories (7b.6/7b.7/7b.8/7b.9) need a Class-C-distinct template (vs current plan to inherit Class-C+)

### Anti-pattern catalog citations

- **A6** (silent-fixture-stub fallback) â€” closing for Tracy passthrough
- **A9** (epic-doc-vs-shipped-framework drift) â€” Tracy greenfield; epic-canonical paths binding
- **A11** (sanctum/sidecar contract drift) â€” Tracy is greenfield; no drift expected
- **P1** (substrate-as-floor violation) â€” AC-I binding (additive-only)

---

### Project Structure Notes

- `app/specialists/tracy/` â€” already populated (slab-2b era passthrough); this story REPLACES `_act.py` body, KEEPS `posture_dispatch.py` helper
- `_bmad/memory/bmad-agent-tracy/` â€” NEW (sidecar greenfield; 4-file BMB pattern)
- `skills/bmad-agent-tracy/SKILL.md` â€” UPDATED (minimal frontmatter + sanctum-aware activation order)
- `tests/parity/test_tracy_activation_contract.py` â€” NEW (FR105; Class-C+; flat layout)
- `scripts/utilities/validate_parity_test_class_conformance.py` â€” EXTENDED with Class-C+ template (lockstep)
- `tests/specialists/tracy/test_*.py` â€” NEW (5 behavioral tests)
- `tests/end_to_end/test_tracy_cache_hit_rate.py` â€” NEW
- `tests/composition/test_tracy_to_texas_chain.py` â€” NEW (Round-(e) E4 binding-hard interface coverage)
- `docs/dev-guide/composition-specification.md` Â§10 â€” NEW Decision Log entry (NFR-CG15)
- `docs/dev-guide/sanctum-reference-conventions.md` â€” possibly UPDATED with Class-C+ 4-file canonical pattern

### Detected conflicts or variances

- **Sanctum greenfield** â€” Tracy has no legacy sidecar; spec creates 4-file BMB per epic-canonical
- **Class-C+ vs Class-A pattern divergence** â€” 4-file vs 6-file; intentional per spec; class-conformance validator discriminates

---

## References

- **Round-(e) governance JSON**: [`docs/dev-guide/migration-story-governance.json`](../../docs/dev-guide/migration-story-governance.json) Â§`stories.7b-5`
- **Epic + story-level scope**: [`epics-slab-7b-specialist-activation-eleven.md`](../planning-artifacts/epics-slab-7b-specialist-activation-eleven.md) Â§Story 7b.5
- **PRD FR93**: [`prd-slab-7b-specialist-activation-eleven.md`](../planning-artifacts/prd-slab-7b-specialist-activation-eleven.md) Â§FR93
- **Texas retrieval-contract (Round-(e) E4 binding-hard)**: [`skills/bmad-agent-texas/references/retrieval-contract.md`](../../skills/bmad-agent-texas/references/retrieval-contract.md)
- **Slab 2b.1 TEMPLATE precedent (Gary)**: [`migration-2b-1-gary-scaffold-migration.md`](migration-2b-1-gary-scaffold-migration.md)
- **Specialist migration template (R1-R14)**: [`docs/dev-guide/specialist-migration-template.md`](../../docs/dev-guide/specialist-migration-template.md)
- **7b.1 substrate**: [`migration-7b-1-texas-hardening.md`](migration-7b-1-texas-hardening.md)
- **7b.4 Class-B template precedent**: [`migration-7b-4-irene-pass1-refresh.md`](migration-7b-4-irene-pass1-refresh.md)
- **7a.5 conversation-persistence contract**: [`migration-7a-5-conversation-persistence-specialist-summary-writer.md`](migration-7a-5-conversation-persistence-specialist-summary-writer.md)
- **BMB sanctum alignment checklist (FR108)**: [`docs/dev-guide/bmb-sanctum-alignment-checklist.md`](../../docs/dev-guide/bmb-sanctum-alignment-checklist.md)
- **Sanctum reference conventions**: [`docs/dev-guide/sanctum-reference-conventions.md`](../../docs/dev-guide/sanctum-reference-conventions.md)
- **Composition Spec (NFR-CG15 Decision Log)**: [`docs/dev-guide/composition-specification.md`](../../docs/dev-guide/composition-specification.md)
- **Sandbox-AC inventory (FR107)**: [`docs/dev-guide/migration-ac-sandbox-inventory.json`](../../docs/dev-guide/migration-ac-sandbox-inventory.json)
- **Sprint status**: [`sprint-status.yaml`](sprint-status.yaml)
- **Deferred inventory**: [`deferred-inventory.md`](../planning-artifacts/deferred-inventory.md)
- **CLAUDE.md** â€” Â§LangChain/LangGraph migration governance + Â§BMAD sprint governance + Â§NFR-CG17 + D21

---

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- T1 gates: Round-(e) E4+E6 governance pin PASS; sandbox-AC preflight PASS;
  Wave-1 + Wave-2a statuses verified done after operator-closed 7b.4.
- Drift resolutions: Tracy sidecar greenfield established at
  `_bmad/memory/bmad-agent-tracy/` with Class-C+ four-file pattern; existing
  `posture_dispatch.py` consumed as helper, not replaced.
- Verification:
  - Focused 7b.5 battery: `62 passed, 1 skipped`.
  - Broad regression slice: `1265 passed, 22 skipped, 1 deselected, 1 failed`
    with the lone failure matching the pre-existing Wanda sanctum drift.
  - `detect_live_api_in_tests.py`: PASS.
  - `validate_migration_story_sandbox_acs.py`: PASS.
  - `validate_parity_test_class_conformance.py tests/parity/`: PASS.
  - `check_pipeline_manifest_lockstep.py`: PASS.
  - Story-scoped `ruff check`: PASS.
  - `lint-imports.exe`: 9 kept, 0 broken.
  - `app/marcus/orchestrator/dispatch_adapter.py` diff: 0 lines.
  - Tracy `_act.act` body: 34 logical lines.

### Completion Notes List

- T1.6 drift-resolution: Class-C+ sidecar is greenfield and intentionally
  four-file; Tracy legacy `posture_dispatch.py` remains in place as helper.
- T2.2 validator-passed-on-existing-tests: Class-C+ branch added to
  `validate_parity_test_class_conformance.py`; validator passes across 5
  activation-contract files (Class-A, Class-B, Class-C+).
- T9.1 Decision Log: Composition Spec section 10 now records Class-C+
  four-file BMB pattern; `sanctum-reference-conventions.md` documents the same
  pattern.
- Cache-hit-rate harness: `@pytest.mark.llm_live` harness is present and
  operator-gated behind `TRACY_LLM_LIVE_CACHE_HARNESS=1` to avoid spending live
  OpenAI calls during default story verification.
- T12.3 tripwire-ledger entry remains Claude-owned at formal close.

### File List

- `_bmad/memory/bmad-agent-tracy/INDEX.md`
- `_bmad/memory/bmad-agent-tracy/PERSONA.md`
- `_bmad/memory/bmad-agent-tracy/chronology.md`
- `_bmad/memory/bmad-agent-tracy/access-boundaries.md`
- `_bmad-output/implementation-artifacts/7b-5-codex-self-review-2026-04-29.md`
- `_bmad-output/implementation-artifacts/migration-7b-5-tracy-port-shape-sidecar.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `app/specialists/tracy/_act.py`
- `app/specialists/tracy/graph.py`
- `app/specialists/tracy/model_config.yaml`
- `app/specialists/tracy/state.py`
- `docs/dev-guide/composition-specification.md`
- `docs/dev-guide/sanctum-reference-conventions.md`
- `scripts/utilities/detect_live_api_in_tests.py`
- `scripts/utilities/validate_parity_test_class_conformance.py`
- `skills/bmad-agent-tracy/SKILL.md`
- `tests/composition/test_tracy_to_texas_chain.py`
- `tests/end_to_end/test_tracy_cache_hit_rate.py`
- `tests/parity/test_skill_md_sanctum_alignment.py`
- `tests/parity/test_tracy_activation_contract.py`
- `tests/specialists/tracy/test_tracy_act_node_dispatch.py`
- `tests/specialists/tracy/test_tracy_model_cascade.py`
- `tests/specialists/tracy/test_tracy_no_third_party_api_imports.py`
- `tests/specialists/tracy/test_tracy_resolution_trail.py`
- `tests/specialists/tracy/test_tracy_retrieval_intent_emission.py`
- `tests/specialists/tracy/test_tracy_sidecar_4_file_pattern.py`
- `tests/specialists/tracy/test_tracy_summary_landing.py`
