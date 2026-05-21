# Migration Story 7b.6: Gary Port-Shape — Gamma API Live Invocation + Per-Slide Variant Generation

**Status:** done
**Sprint key:** `migration-7b-6-gary-port-shape`
**Epic:** Slab 7b Specialist Body Activation — `epic-slab-7b-specialist-activation-eleven`. **Wave 3 first port-shape** (Class-C API-bound; serial after Wave-2b 7b.5 close; **PARALLEL with 7b.7 Kira + 7b.8 Enrique** once 7b.6 itself opens; Claude-authored spec / Codex dev per NFR-CG17 + D21 dev-cycle ownership).
**Pts:** 4 | **Gate:** single (per `docs/dev-guide/migration-story-governance.json::stories.7b-6`; rationale: null; per Slab 2b.1 TEMPLATE pattern) | **K-target:** ~1.4× (target ~33 tests / floor ~25; ~2.9K LOC).
**Author:** **Claude** spec / **Codex** dev. **Review:** **Claude** T11 `bmad-code-review`.
**Wave-3 precondition:** 7b.5 (Wave-2b Tracy) `done`. **Wave-3 first-port tripwire (Round-(e) E3 keyed):** if 7b.6 closes >2.7K LOC, Round-(e) E3 `conditional_gate_override` on 7b.7 (Kira) + 7b.8 (Enrique) fires (binding=hard) — both flip to dual-gate.

---

## Round-(e) Governance Inheritance

Round-(e) freeze landed 2026-04-29. Load-bearing for 7b.6:

- **E3 binding-hard upstream trigger:** 7b.6 close LOC measurement is the trigger condition for `conditional_gate_override` on 7b.7 + 7b.8. Sprint runner reads this story's close-verdict at 7b.7/7b.8 story-open via `tripwire_escalation_record_path` (records to `sprint-status.yaml::tripwire_events::wave_3_first_port_tripwire`).
- **No direct binding** on 7b.6 itself (single-gate; default Class-C K-target).

**T1 readiness verification command:**
```bash
.venv/Scripts/python.exe -c "import json; d = json.load(open('docs/dev-guide/migration-story-governance.json', encoding='utf-8')); assert d['version'] == '2026-04-29-slab7b-twelve-stories'; assert d['stories']['7b-6']['expected_gate_mode'] == 'single-gate'; assert d['stories']['7b-7']['conditional_gate_override']['trigger_story'] == '7b-6'; assert d['stories']['7b-8']['conditional_gate_override']['trigger_story'] == '7b-6'; print('Round-(e) E3 trigger-story verified PASS for 7b-6')"
```

---

## T1 Readiness Block

### Required-readings cascade (10-reading)

1. **Round-(e) governance JSON** — `docs/dev-guide/migration-story-governance.json` §`stories.7b-6` + §`stories.7b-7.conditional_gate_override` + §`stories.7b-8.conditional_gate_override`. Confirm 7b.6 single-gate; 7b.7+7b.8 keyed to 7b.6 tripwire.
2. **Epic + story-level scope** — [`epics-slab-7b-specialist-activation-eleven.md`](../planning-artifacts/epics-slab-7b-specialist-activation-eleven.md) §Story 7b.6 (lines 674-731).
3. **PRD §FR94** — [`prd-slab-7b-specialist-activation-eleven.md`](../planning-artifacts/prd-slab-7b-specialist-activation-eleven.md) §FR94. Gamma API live invocation + per-slide variant generation (DOUBLE_DISPATCH branch) + theme-handshake + PNG export normalization (`_materialize_exported_slide_paths` carry-forward) + Vera G3 invocation hooks.
4. **Sandbox-AC inventory entry `gamma` (FR107; Wave 0 LANDED)** — [`docs/dev-guide/migration-ac-sandbox-inventory.json`](../../docs/dev-guide/migration-ac-sandbox-inventory.json) §`gamma`. "Live invocation NOT assumed on dev-agent session PATH; invoke via httpx + Gamma API client at `scripts/api_clients/gamma_client.py` with `pytest.skip(...)` when `GAMMA_API_KEY` not set. Live evidence belongs in operator-gated AC-*-B blocks."
5. **Slab 2b.1 TEMPLATE precedent (CRITICAL — Gary IS the original 2b.1 specialist; this is Wave-1-hardening of the same)** — [`migration-2b-1-gary-scaffold-migration.md`](migration-2b-1-gary-scaffold-migration.md). 9-node scaffold + AC-B 150-LOC ceiling + REST-API tool-dispatch pattern + sandbox-AC governance. **Note:** Slab 2b.1 used `_bmad/memory/bmad-agent-gamma/` sanctum path (skill-dir convention). Slab 7b epic Story 7b.6 binds `_bmad/memory/bmad-agent-gary/` (specialist-name convention). **Resolution at T1 (binding):** specialist-name path per Slab 7b convention; see Drift #1 below.
6. **Specialist migration template (R1-R14)** — [`docs/dev-guide/specialist-migration-template.md`](../../docs/dev-guide/specialist-migration-template.md).
7. **Wave-2b close evidence** — verify 7b.5 (Tracy) `done` in `sprint-status.yaml`; read `tripwire_events::wave_2b_close::fired_verdict`; if fired, this story opens at upper-band K-target per Round-(a) Amelia A3 + Round-(e) E6 escalation chain.
8. **Class-C+ template precedent (from 7b.5)** — `validate_parity_test_class_conformance.py` extended with Class-C+ template at 7b.5 close. **This story extends with Class-C template** in lockstep with the parity test landing (LOCKSTEP foundational deliverable). Class-C template inherits most of Class-C+ but asserts third-party API binding (vs LLM-only) + VCR cassettes + operator-gated live-canary.
9. **`scripts/api_clients/gamma_client.py`** + **`skills/gamma-api-mastery/scripts/gamma_operations.py::execute_generation`** — Gary's runtime production entry point (per Slab 2b.1 close; Gary dispatches to `gamma_operations.execute_generation` via thin wrapper around the HTTPS API surface). Read both before authoring Wave-1 hardening.
10. **CLAUDE.md** — §LangChain/LangGraph migration governance + §BMAD sprint governance + NFR-CG13 (no live-API in CI; strict prohibition) + NFR-CG19 (credential-rotation register) + NFR-CG20 (rate-limit budget).

### Gary current-state probe + drift surfacing

```bash
ls app/specialists/gary/                              # __init__.py expertise/ gamma_dispatch.py graph.py model_config.yaml state.py (Slab 2b.1 era; Gamma API dispatch wrapper present)
ls _bmad/memory/bmad-agent-gary/ 2>/dev/null          # NOT YET PRESENT — sanctum greenfield (Slab 7b convention; specialist-name path)
ls _bmad/memory/bmad-agent-gamma/ 2>/dev/null         # NOT YET PRESENT either — Slab 2b.1 era expected this path but never populated
ls skills/bmad-agent-gamma/                           # SKILL.md + references/ (Slab 2b.1 era Gamma API-mastery skill; **CANONICAL SKILL.md per epic Story 7b.6 line 708 SG-4 binding** — Gary persona skill at API-name path, NOT specialist-name)
ls skills/bmad-agent-gary/ 2>/dev/null                # **DOES NOT EXIST** — earlier spec draft incorrectly assumed dual-skill-dir; reality: only `bmad-agent-gamma/` exists for Gary's persona-skill surface
ls skills/gamma-api-mastery/                          # SKILL.md + scripts/ (the API client; gamma_operations.py::execute_generation)
ls scripts/api_clients/gamma_client.py 2>/dev/null    # httpx-based Gamma API client (sandbox-AC inventory consumer)
```

**Three drifts surface at T1:**

**⚠️ Drift #1 — Sanctum dir path: Slab 2b.1 (`bmad-agent-gamma/`) vs Slab 7b epic (`bmad-agent-gary/`):** Two coexisting conventions. Slab 2b.1 used skill-dir-based path (matched the API-mastery skill name); Slab 7b epic Story 7b.6 line 708 binds specialist-name path. **Resolution at T1 (binding):** path = `_bmad/memory/bmad-agent-gary/` per Slab 7b convention. Rationale: epic-file canonical (Round-(d) ratified close); matches Wave-1 specialist-name precedent (Texas/Quinn-R/Vera all use `bmad-agent-{specialist}/`). Filed as deferred-inventory follow-on `gary-sanctum-path-slab-2b-vs-7b-resolution` — CLOSED at this story T2 with verdict-specialist-name. The Slab 2b.1 era had written the path as `bmad-agent-gamma/` but never populated it, so no migration cost.

**⚠️ Drift #2 — SKILL.md path is the API-name (Gamma) skill-dir, NOT specialist-name (Gary):** Reality verified 2026-04-29 (post-Codex-7b.6-T1-HALT): `skills/bmad-agent-gary/` does NOT exist on disk; only `skills/bmad-agent-gamma/` exists (with `SKILL.md` + `references/`). Per epic Story 7b.6 line 708, the canonical SKILL.md per SG-4 IS `skills/bmad-agent-gamma/SKILL.md` (API-name path). **Class-C API-bound specialists use API-name skill-dirs, distinct from Class-A specialist-name pattern.** This mirrors 7b.7 Kira (`bmad-agent-kling/`) + 7b.8 Enrique (`bmad-agent-elevenlabs/`) + 7b.9 Wanda (`bmad-agent-wondercraft/`). Sanctum dir at `_bmad/memory/bmad-agent-gary/` (specialist-name) STAYS as Slab 7b convention — only the SKILL.md path follows API-name. **Resolution at T1 (binding):** SKILL.md canonical = `skills/bmad-agent-gamma/SKILL.md`. Filed as deferred-inventory follow-on `class-c-api-bound-skill-dir-naming-convention` documenting the Class-C pattern (API-name skill-dir + specialist-name sanctum-dir; mirrors A11 dual-naming pattern).

**⚠️ Drift #3 — Existing `gamma_dispatch.py` legacy module at `app/specialists/gary/`:** Slab-2b.1 era carry-forward; the dispatch wrapper around `gamma_operations.execute_generation`. Wave-3 hardening should consume it (NOT replace) per substrate-as-floor invariant. Verify import-stability + that `_materialize_exported_slide_paths` carry-forward at `skills/gamma-api-mastery/scripts/gamma_operations.py:1338` is import-stable.

### Wave 0 + 7b.1 substrate + Wave-1 + Wave-2a + Wave-2b sweeps

```bash
# Wave 0 (commit 9ed6fcb)
ls docs/dev-guide/bmb-sanctum-alignment-checklist.md docs/dev-guide/sanctum-exception-categories.json docs/dev-guide/operator-control-parity-template.md docs/dev-guide/migration-ac-sandbox-inventory.json skills/bmad-agent-cora/SKILL.md
ls docs/dev-guide/scaffolds/scaffold-v0.2-D2-pipeline/

# 7b.1 T2 substrate
ls tests/parity/_sanctum_parity_base.py tests/composition/_chain_test_base.py scripts/utilities/validate_parity_test_class_conformance.py
grep -c "FR105 + Errata 4 layout decision" tests/parity/README.md  # >=1 expected

# Wave-1 close (3 stories `done`); Wave-2a close (7b.4 done); Wave-2b close (7b.5 done)
.venv/Scripts/python.exe -c "
import yaml
d = yaml.safe_load(open('_bmad-output/implementation-artifacts/sprint-status.yaml', encoding='utf-8'))
done = lambda k: d['development_status'][k].startswith('done')
assert all(done(k) for k in ('migration-7b-1-texas-hardening','migration-7b-2-quinn-r-hardening','migration-7b-3-vera-hardening','migration-7b-4-irene-pass1-refresh','migration-7b-5-tracy-port-shape-sidecar'))
print('Wave 1 + 2a + 2b all closed OK')
"

# FR107 sandbox-AC inventory entry `gamma` present
.venv/Scripts/python.exe -c "import json; d = json.load(open('docs/dev-guide/migration-ac-sandbox-inventory.json', encoding='utf-8')); assert 'gamma' in d['notes']; print('gamma entry present')"

# Class-C+ template active in validator (from 7b.5)
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/  # PASS expected
```

All paths must exist + all wave gates closed. If any absent → HALT.

### Class-C template extension required (LOCKSTEP)

This story is the **first Class-C specialist** to land per NFR-I12. The dev-agent (Codex) must extend `scripts/utilities/validate_parity_test_class_conformance.py` with Class-C template assertions in lockstep with this story's parity test landing. Class-C template asserts:
- 6-file BMB sanctum pattern (Class-A canonical inheritance — distinct from Class-C+ 4-file)
- third-party API live invocation (NOT LLM-only)
- VCR cassettes for CI tests (NFR-CG13 strict prohibition on live-API-in-CI)
- operator-gated AC-N-B for T5 live canary (≤3 invocations; cost ≤$0.40/canary; pasted into Completion Notes)
- credential-rotation register entry (NFR-CG19) + rate-limit budget (NFR-CG20)

### Sandbox-AC validator pre-flight

```bash
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py \
  _bmad-output/implementation-artifacts/migration-7b-6-gary-port-shape.md
```
Expect PASS. All Gamma API verification wraps via shipped `httpx` + `scripts/api_clients/gamma_client.py` with `pytest.skip(...)` when `GAMMA_API_KEY` not set. Live canary belongs ONLY in operator-gated AC-6-B Completion-Notes block.

### Standing pre-flight items

1. Severance posture confirmed.
2. `state/config/substrate-frozen-paths.yaml` honored — no diff to `app/marcus/orchestrator/dispatch_adapter.py:70-95`.
3. NFR-T9-T12 wall-clock ceilings hold.
4. **Wave-3 first-port discipline:** this story's K-actual at close is the trigger for Round-(e) E3 conditional_gate_override on 7b.7+7b.8. Codex flags pre-T2 if K-projection trends >2.7K (party-mode awareness; NOT auto-escalation — tripwire fires AT close measurement).

---

## Story

As a **migration dev agent**,
I want **Gary to execute a Class-C port-shape — Gamma API live invocation via `gamma_client.py` + per-slide variant generation (DOUBLE_DISPATCH branch when applicable) + theme-handshake + PNG export normalization (`_materialize_exported_slide_paths` carry-forward) + Vera G3 invocation hooks fired with real Gamma artifacts as input — AND I want Gary's sanctum greenfield at `_bmad/memory/bmad-agent-gary/` (6-file BMB pattern) AND I want the Class-C template extension to `validate_parity_test_class_conformance.py` landing in lockstep**,
So that **(a) Trial-2 reaches G2B with real Gamma slide variants generated per slide and the operator can choose variants in the per-slide review pack, (b) Vera's G3 fidelity check runs on real Gamma artifacts (not fixture-stub), (c) the Class-C template is established as canonical for Wave-3 + Wave-4 inheritance (7b.7 Kira / 7b.8 Enrique / 7b.9 Wanda), and (d) SG-4 sanctum-alignment is enforced for Gary via 6-file BMB sanctum + FR101 parity test inheriting `SanctumParityTestBase` from 7b.1 substrate**.

---

## Acceptance Criteria

All ACs are dev-agent-executable (sandbox-AC compliant). Live-API verification wraps via `httpx` + `gamma_client.py` with `pytest.skip(...)`; live canary deferred to operator-gated AC-6-B Completion-Notes.

### AC-7b.6-A — T1 readiness verification + drift resolution

**Given** the Round-(e) E3 trigger-story binding + Wave-1/2a/2b all closed + sandbox-AC inventory `gamma` entry LANDED
**When** the dev agent runs T1 readiness
**Then** all 10 readings cascade complete; Round-(e) verification command exits 0; Wave-0 + 7b.1-T2 + Wave-1 + Wave-2a + Wave-2b sweeps PASS; sandbox-AC validator PASS pre-flight
**And** Drift #1 resolution recorded: sanctum path = `_bmad/memory/bmad-agent-gary/` (Slab 7b specialist-name convention; Slab 2b.1 era `bmad-agent-gamma/` superseded)
**And** Drift #2 resolution recorded: SKILL.md canonical = `skills/bmad-agent-gamma/SKILL.md` (specialist-name); `skills/bmad-agent-gamma/` remains for API-mastery reference (NOT modified by this story)
**And** Drift #3 acknowledged: legacy `gamma_dispatch.py` consumed (NOT replaced).

### AC-7b.6-B — 9-node scaffold port-shape per Slab 2b.1 TEMPLATE

**Given** the canonical 9-node scaffold contract + Slab 2b.1 TEMPLATE pattern (Gary IS the original 2b.1 specialist)
**When** the dev-agent (Codex) authors Gary's Wave-3 port-shape
**Then** `app/specialists/gary/_act.py` lands with bounded body (≤150 LOC AC-B ceiling) + `app/specialists/gary/graph.py` builds the 9-node scaffold (already established in Slab 2b.1; this story REFINES the body, KEEPS the scaffold)
**And** `validate_scaffold("gary", build_gary_graph()).is_conforming is True`; ruff clean; import-linter C1 lane-isolation PASS.

### AC-7b.6-C — Gamma API live invocation + per-slide variant generation

**Given** the FR94 contract: Gamma API live invocation + per-slide variant generation
**When** Gary dispatched at G2B
**Then** Gary's `_act` body invokes `GammaClient.generate_deck(...)` (via thin wrapper around `scripts/api_clients/gamma_client.py`)
**And** the DOUBLE_DISPATCH branch fires when applicable (per Gamma API mastery module §DOUBLE_DISPATCH)
**And** theme-handshake performed via `GammaClient.list_themes()` (live-tested 2026-03-30 era; carry-forward)
**And** PNG export normalization via `_materialize_exported_slide_paths` (carry-forward from `skills/gamma-api-mastery/scripts/gamma_operations.py:1338`)
**And** `_act` body length ≤150 LOC per AC-B ceiling.
**Test pin:** `tests/specialists/gary/test_gary_gamma_dispatch.py` — VCR cassette at `tests/fixtures/specialist-replay/gary/gamma_dispatch_happy_path.yaml`; assert deck generation invocation shape.

### AC-7b.6-D — Vera G3 invocation hooks fire with real Gamma artifacts

**Given** Vera's G3 fidelity check requirement (per FR91 hardening from 7b.3 close)
**When** Gary completes per-slide variant generation
**Then** Vera G3 invocation hooks fire with real Gamma artifacts as input (FR94 + FR91 cross-cut)
**And** the integration is verified via chain test (AC-7b.6-K) inheriting `ChainTestBase`.
**Test pin:** `tests/composition/test_gary_to_vera_g3_chain.py` — fixture-replay; assert Vera G3 receives Gamma artifact paths in shape it expects.

### AC-7b.6-E — Live-API-on-CI strict prohibition (NFR-CG13)

**Given** the NFR-CG13 strict prohibition on live-API in CI
**When** the dev-agent (Codex) authors tests
**Then** `tests/specialists/gary/` use VCR cassettes under `tests/fixtures/specialist-replay/gary/` per NFR-T10
**And** `scripts/utilities/detect_live_api_in_tests.py` AST-scan PASSES (no `from gamma_client import` patterns in CI test files at file-scope; only inside `if not pytest.skip(...)` guards or operator-gated test files)
**And** dev-agent ACs reference live-API only via shipped `httpx` + `gamma_client.py` with `pytest.skip(...)` when `GAMMA_API_KEY` not set.

### AC-7b.6-F — Class-C 6-file BMB sanctum greenfield at canonical path

**Given** the SG-4 sanctum-alignment requirement + epic Story 7b.6 line 708 binding 6-file BMB pattern at `_bmad/memory/bmad-agent-gary/`
**When** the dev-agent (Codex) authors Gary's sanctum
**Then** `_bmad/memory/bmad-agent-gary/` directory lands with 6-file BMB pattern (Texas/Quinn-R/Vera precedent):
  - `INDEX.md` / `PERSONA.md` / `CREED.md` / `BOND.md` / `MEMORY.md` / `CAPABILITIES.md`
**And** content authored per BMB checklist; consume relevant content from `skills/bmad-agent-gamma/` references where applicable (Gary persona-skill surface; API-name path per epic-canonical)
**And** `skills/bmad-agent-gamma/SKILL.md` is verified option-a sanctum-aligned per BMB checklist (FR108):
  - YAML frontmatter MINIMAL (`name` + `description` only)
  - SKILL.md body references `_bmad/memory/bmad-agent-gary/` as activation-time hot-load batch
**And** `skills/bmad-agent-gamma/` is NOT modified by this story (API-mastery reference; out-of-scope).

### AC-7b.6-G — FR105 per-specialist parity test (Class-C template extension; LOCKSTEP)

**Given** the Errata 4 verdict-flat layout + 7b.1 substrate + 7b.4 Class-B + 7b.5 Class-C+ template extensions
**When** the dev-agent (Codex) authors Gary's activation-contract test + extends the validator
**Then** `tests/parity/test_gary_activation_contract.py` (flat) lands inheriting `SanctumParityTestBase` with `class_template_id = "C"`, `specialist_name = "gary"`
**And** the test asserts **Class-C live-API + cache-hit-rate-N/A + VCR-cassette + operator-gated-canary parity** per NFR-I12 Class-C template:
  - (i) 9-node scaffold conformance via `validate_scaffold()`
  - (ii) 6-file BMB sanctum pattern present at `_bmad/memory/bmad-agent-gary/`
  - (iii) Gamma API binding via `gamma_client.py` (NOT inline httpx)
  - (iv) VCR cassettes present under `tests/fixtures/specialist-replay/gary/`
  - (v) credential-rotation register entry for Gamma at `state/config/credential-rotation-register.yaml` (NFR-CG19)
  - (vi) rate-limit budget declared in `app/specialists/gary/config.yaml` (NFR-CG20)
  - (vii) cold-activation smoke
**And** **`scripts/utilities/validate_parity_test_class_conformance.py` extended with Class-C template assertions in lockstep** (additive; A + B + C+ unchanged). Class-C inherits Class-C+ for live-API binding + VCR cassettes; differs in sanctum pattern (6-file vs 4-file) + LLM-only (Class-C+ is LLM-only; Class-C is third-party-API).
**And** `@pytest.mark.timeout(30)` per NFR-T9; <120s aggregate per NFR-T12.

### AC-7b.6-H — Cache-hit-rate N/A for Class-C (no LLM at specialist layer)

**Given** Gary is REST-API tool-dispatch (no LLM at the Gary layer; per Slab 2b.1 close)
**And** the cache-hit-rate harness requirement (FR106) applies only to LLM specialists
**When** the dev-agent considers FR106 wiring
**Then** **NO cache-hit-rate harness for Gary** — REST-API tool-dispatch specialists have no LLM prefix to cache at the specialist layer (same as Texas/Slab 2a.4 + Slab 2b.1 era).
**Note:** the FR106 measurement category does NOT generalize to Class-C per Slab-2a-retrospective §FR54-doesn't-generalize. Documented in Class-C template.

### AC-7b.6-I — Credential-rotation register (NFR-CG19) + rate-limit budget (NFR-CG20)

**Given** the NFR-CG19 credential-rotation register + NFR-CG20 rate-limit budget requirements
**When** the dev-agent commits Gary port-shape
**Then** `state/config/credential-rotation-register.yaml` carries a row for Gamma API: `{provider: "gamma", owner: "operator", rotation_cadence_days: 90, last_rotated: "<YYYY-MM-DD>", next_due: "<YYYY-MM-DD+90d>", secret_store_reference: "operator-machine .env GAMMA_API_KEY"}`
**And** per-specialist rate-limit budget declared in `app/specialists/gary/config.yaml` (or `model_config.yaml` extension): `{rate_limit_per_minute: <N>, daily_budget_usd: <X>, per_invocation_cap_usd: <Y>}`.

### AC-7b.6-J — Sandbox-AC governance + substrate-as-floor invariant

**Given** the sandbox-AC inventory governance requirement + FR113 + NFR-I13
**When** `validate_migration_story_sandbox_acs.py` runs on this spec
**Then** PASS (no forbidden CLI in dev-agent ACs; `gamma` references all wrap via shipped Python deps)
**And** **no diff hunk touches `app/marcus/orchestrator/dispatch_adapter.py:70-95`** absent ceremony.

### AC-7b.6-K — Chain test inheriting `ChainTestBase`

**Given** NFR-CG14 chain-test PR pre-merge requirement + 7b.1's `_chain_test_base.py` substrate
**When** the dev agent authors the Gary chain test
**Then** `tests/composition/test_gary_to_vera_g3_chain.py` lands inheriting `ChainTestBase`
**And** the test asserts Gary→Vera G3 envelope-handoff (Gary's `GaryReturn` carries `gary_slide_output: list[dict]` with PNG paths; Vera G3 consumes via fixture-replay)
**And** wall-clock <120s.

### AC-7b.6-L — 7a.5 specialist-summary-writer integration

**Given** the Slab 7a 7a.5 conversation-persistence contract
**When** Gary `_act` completes
**Then** Gary invokes `summary_writer.emit_summary(specialist_id="gary", gate_id="G2B", payload=<verdict>)` per the 7a.5 facade
**And** the summary file lands at `runs/<run_id>/specialist-summaries/gary-g2b-<timestamp>.md` with 15-25 line envelope.

### AC-7b.6-M — Operator-gated AC-6-B (Completion Notes evidence)

**Given** the operator-gated AC-6-B requirement (NFR-T11b T5 live canary; NFR-CG13 splits live invocation to operator-gated blocks)
**When** the operator runs T5 live canary against real Gamma API
**Then** ≤3 canary invocations; cost ≤$0.40 per canary (per NFR-T11b cap)
**And** evidence pasted into Completion Notes verbatim: API endpoint hit, request payload (redacted credentials), response 200-OK + valid response shape (deck-id + slide URLs), cost-tracking line per canary
**And** `(operator-gated)` block discipline: AC-6-B is NOT in dev-agent AC scope; sandbox-AC validator does NOT check this block.

### AC-7b.6-N — Wave-3 first-port tripwire ledger (Round-(e) E3 trigger record)

**Given** the Round-(e) E2 amendment landed `tripwire_events: []` schema slot at `sprint-status.yaml`
**And** Round-(e) E3 binding-hard `conditional_gate_override` on 7b.7 + 7b.8 keyed to 7b.6 first-port tripwire
**When** this story closes (post-T11 review)
**Then** the dev-agent appends a NEW `wave_3_first_port_tripwire` entry to `sprint-status.yaml::tripwire_events`:
```yaml
tripwire_events:
  # ... existing wave_1_close, wave_2b_close entries ...
  - tripwire_id: wave_3_first_port_tripwire
    story_owner: 7b-6
    fired_at: <YYYY-MM-DD>
    fired_verdict: <true|false>          # true if 7b-6 LOC > 2.7K threshold
    measured_value:
      kloc: <N.NN>
      tests_added: <N>
      act_body_loc: <N>
      ceiling_breach: false              # AC-B 150-LOC ceiling honored
    escalation_action_taken: |
      <none|7b-7+7b-8_conditional_gate_override_fires_per_round_e_e3_binding_hard_BOTH_FLIP_DUAL_GATE>
    decision_record_link: <links to story spec + code-review report>
```
**And** if `fired_verdict: true`, **7b.7 + 7b.8 BOTH flip to dual-gate** at their story-open per Round-(e) E3 binding-hard `conditional_gate_override` (sprint runner reads this ledger entry at 7b.7/7b.8 story-open and applies override).

### AC-7b.6-O — Composition Spec Decision Log entry (NFR-CG15)

**Given** the NFR-CG15 Decision Log entry requirement
**When** Gary lands the Class-C template + 6-file BMB sanctum
**Then** Decision Log entry filed at `docs/dev-guide/composition-specification.md` §10:
  - Decision: Class-C canonical sanctum pattern is **6-file BMB** (same as Class-A); distinct from Class-C+ 4-file pattern
  - Rationale: Class-C API-bound specialists need full persona-continuity (operator review at G2B/G2F/G2 gates); 6-file pattern matches the Class-A persona-driven hardening shape
  - Inheritance: Gary is the seed exemplar; 7b.7 Kira / 7b.8 Enrique / 7b.9 Wanda inherit the Class-C 6-file pattern

### AC-7b.6-P — Close protocol

**Given** all prior ACs PASS + bmad-code-review returns PASS or PASS-WITH-PATCH-applied + regression baseline holds
**When** the story closes
**Then** at close:
  1. **sprint-status.yaml** flip: `migration-7b-6-gary-port-shape: in-progress → review → done`
  2. **Wave-3 first-port tripwire ledger entry** appended per AC-N (FINAL `fired_verdict` evaluated here)
  3. **next-session-start-here.md** updated: pivot to Wave 3 PARALLEL (7b.7 Kira + 7b.8 Enrique opens; gate-mode read from `conditional_gate_override` per tripwire verdict)
  4. **Deferred-inventory updates**: any new follow-ons surfaced; `gary-sanctum-path-slab-2b-vs-7b-resolution` CLOSED at T2
  5. **Standing-guardrail status**: SG-4 GREEN for Gary; Class-C template active in validator; Composition Spec §10 Decision Log entry filed
  6. **Three-line D12 close stub**

---

## Tasks / Subtasks

### T1 — T1 readiness verification + drift resolution
- [x] **T1.1** Round-(e) E3 trigger-story verification
- [x] **T1.2** 10-reading cascade
- [x] **T1.3** Wave-1 + 2a + 2b close evidence
- [x] **T1.4** FR107 sandbox-AC `gamma` entry verified
- [x] **T1.5** Gary current-state probe — 3 drift items
- [x] **T1.6** Drift resolution recorded
- [x] **T1.7** Sandbox-AC validator pre-flight

### T2 — Class-C template extension to validator (LOCKSTEP foundational deliverable)
- [x] **T2.1** Extend `scripts/utilities/validate_parity_test_class_conformance.py` with Class-C template assertions
- [x] **T2.2** Verify validator PASSES on existing Class-A/B/C+ tests post-extension
- [x] **T2.3** Close `gary-sanctum-path-slab-2b-vs-7b-resolution` follow-on with verdict-specialist-name

### T3 — Gary sanctum greenfield 6-file BMB authoring (AC-F)
- [x] **T3.1** Author 6 BMB files at `_bmad/memory/bmad-agent-gary/`
- [x] **T3.2** Update `skills/bmad-agent-gary/SKILL.md` — minimal frontmatter + sanctum-aware activation order
- [x] **T3.3** Verify `skills/bmad-agent-gamma/` is NOT modified (out-of-scope; API-mastery reference)

### T4 — Gary `_act` body Wave-3 hardening (AC-B + AC-C + AC-D + AC-E)
- [x] **T4.1** Refine `app/specialists/gary/_act.py` (or extract from existing `gamma_dispatch.py` if pattern requires) — bounded body invoking `gamma_client.py`
- [x] **T4.2** Wire DOUBLE_DISPATCH branch + theme-handshake + PNG export normalization
- [x] **T4.3** Wire Vera G3 invocation hooks
- [x] **T4.4** Wire 7a.5 specialist-summary-writer (AC-L)
- [x] **T4.5** Consume legacy `gamma_dispatch.py` as helper (NOT replace)
- [x] **T4.6** **AC-B 150-LOC ceiling discipline**

### T5 — VCR cassettes + sandbox-AC discipline (AC-E)
- [x] **T5.1** Author VCR cassettes at `tests/fixtures/specialist-replay/gary/` for Gamma API responses
- [x] **T5.2** `tests/specialists/gary/test_gary_gamma_dispatch.py` — happy path + DOUBLE_DISPATCH + theme-handshake + PNG normalization
- [x] **T5.3** `tests/specialists/gary/test_gary_no_live_api_in_ci.py` — `detect_live_api_in_tests.py` AST-scan PASS

### T6 — Parity + behavioral tests (AC-G)
- [x] **T6.1** `tests/parity/test_gary_activation_contract.py` (flat; Class-C template) — AC-G
- [x] **T6.2** `tests/specialists/gary/test_gary_summary_landing.py` — AC-L
- [x] **T6.3** `tests/composition/test_gary_to_vera_g3_chain.py` — AC-K
- [x] **T6.4** Wall-clock annotations + `validate_parity_test_class_conformance.py` PASS on Class-C

### T7 — Credential register + rate-limit budget (AC-I)
- [x] **T7.1** `state/config/credential-rotation-register.yaml` row for Gamma API
- [x] **T7.2** `app/specialists/gary/config.yaml` rate-limit budget declaration

### T8 — SG-4 sanctum alignment verification (AC-F)
- [x] **T8.1** `tests/parity/test_skill_md_sanctum_alignment.py` PASSES for Gary with Class-C template

### T9 — Substrate-as-floor verification (AC-J)
- [x] **T9.1** `git diff` verification — no diff to dispatch_adapter.py:70-95

### T10 — Composition Spec Decision Log entry (AC-O)
- [x] **T10.1** File NFR-CG15 Decision Log entry at composition-specification.md §10

### T11 — Regression baseline + sandbox-AC final
- [x] **T11.1** Full regression battery (target: cumulative + ~33 tests = ~880-900 passed; Wanda flake known)
- [x] **T11.2** `ruff check` story-scoped clean
- [x] **T11.3** `lint-imports.exe` 9/9 KEPT
- [x] **T11.4** Sandbox-AC validator final PASS

### T12 — Codex G6 self-review
- [x] **T12.1** Codex authors G6 self-review at `_bmad-output/implementation-artifacts/7b-6-codex-self-review-2026-04-XX.md`
- [x] **T12.2** Status flip `in-progress → review`

### T13 — Claude bmad-code-review + close (AC-M + AC-N + AC-P)
- [ ] **T13.1** Claude `bmad-code-review` at `7b-6-code-review-2026-04-XX.md`
- [ ] **T13.2** Remediation cycle 1 if needed
- [ ] **T13.3** Operator-gated AC-6-B live canary (if operator window opens; otherwise filed as deferred follow-on)
- [ ] **T13.4** Append Wave-3-first-port tripwire ledger entry per AC-N (FINAL fired_verdict)
- [ ] **T13.5** Sprint-status flip `review → done`
- [ ] **T13.6** Update `next-session-start-here.md`: pivot to Wave 3 PARALLEL (7b.7 + 7b.8); gate-mode applied per E3 conditional_gate_override
- [ ] **T13.7** Deferred-inventory updates per AC-P.4
- [ ] **T13.8** Standing-guardrail status: SG-4 GREEN for Gary; Class-C template active
- [ ] **T13.9** Three-line D12 close stub
- [ ] **T13.10** Commit + push (note: `_bmad/memory/bmad-agent-gary/` likely gitignored — `git add --force`)

---

## Dev Notes

### Wave-3 first-port discipline + Round-(e) E3 binding-hard upstream trigger

This story's K-actual at close IS the trigger for Round-(e) E3 `conditional_gate_override` on 7b.7 (Kira) + 7b.8 (Enrique). Specifically:
- Tripwire fires at LOC > 2.7K
- If fired: 7b.7 + 7b.8 BOTH flip to dual-gate at story-open (binding=hard; sprint runner enforces; NOT advisory)
- Rationale (per Round-(e) E3): Slab 2b.1 TEMPLATE pattern proves out via 7b.6; if it doesn't amortize cleanly, cross-port failure-mode risk justifies escalating downstream sibling stories' gate mode

Codex flags pre-T2 K-projection if trending >2.7K (party-mode awareness; NOT auto-escalation — the tripwire fires AT close measurement, not predictively).

### Class-C template (NEW; this story extends the validator)

7b.1 → Class-A; 7b.4 → Class-B; 7b.5 → Class-C+; this story → Class-C. Class-C inherits Class-C+ for live-API + VCR + operator-gated-canary; differs in: 6-file vs 4-file sanctum pattern; third-party API vs LLM-only. Future Class-C stories (7b.7/7b.8/7b.9) inherit. Class-C+ template stays as-is.

### Live-API discipline (NFR-CG13 + sandbox-AC inventory)

CRITICAL: NO live Gamma API calls in CI test files. All Gary tests use VCR cassettes under `tests/fixtures/specialist-replay/gary/`. Live canary belongs ONLY in operator-gated AC-6-B Completion-Notes block. Per `docs/dev-guide/migration-ac-sandbox-inventory.json::gamma`: invoke via `httpx` + `gamma_client.py` with `pytest.skip(...)` when `GAMMA_API_KEY` not set.

### NFR predicates honored

NFR-T9 / T10 (VCR cassettes; ≤90s) / T11b (≤3 live canaries; ≤$0.40/canary) / T12.
NFR-CG12 (sandbox-AC inventory consumed) / CG13 (NO live-API in CI; strict) / CG14 / CG15 (Decision Log) / CG16 (bmad-code-review pre-close) / CG17 (Codex dev) / CG19 (credential register — AC-I) / CG20 (rate-limit budget — AC-I).
NFR-I9 + NFR-I10 + NFR-I12 (Class-C template extension) + NFR-I13.

### Known follow-ons

- **`class-c-template-extend-validator-during-7b-6`** — CLOSE at T2 (in-story; lockstep)
- **`gary-sanctum-path-slab-2b-vs-7b-resolution`** — CLOSE at T2 with verdict-specialist-name
- **`bmad-memory-gitignore-force-add-policy`** — recurring; affects Gary sanctum at commit
- **Class-C-distinct vs Class-C+ inheritance refinement** — file as named-but-not-filed if 7b.7/7b.8/7b.9 surface significant divergence from Gary's pattern

### Anti-pattern catalog citations

- **A6** (silent-fixture-stub fallback) — closing for Gary G2B
- **A11** (sanctum/sidecar contract drift) — Gary's Slab 2b.1 vs Slab 7b path resolution; harvest as A11 third example
- **P1** (substrate-as-floor violation) — AC-J binding

---

### Project Structure Notes

- `app/specialists/gary/` — already populated (Slab 2b.1 era); this story REFINES `_act.py`, KEEPS `gamma_dispatch.py` helper
- `_bmad/memory/bmad-agent-gary/` — NEW (sanctum greenfield; 6-file BMB Class-C pattern)
- `_bmad/memory/bmad-agent-gamma/` — Slab 2b.1 era expected path; NEVER populated; superseded by specialist-name path
- `skills/bmad-agent-gamma/SKILL.md` — UPDATED (minimal frontmatter + sanctum-aware activation order; API-name skill-dir per epic Story 7b.6 line 708 Class-C convention)
- `skills/bmad-agent-gary/` — does NOT exist on disk; DO NOT create
- `skills/bmad-agent-gamma/` — NOT MODIFIED (API-mastery reference; out-of-scope)
- `tests/parity/test_gary_activation_contract.py` — NEW (FR105; Class-C; flat layout)
- `scripts/utilities/validate_parity_test_class_conformance.py` — EXTENDED with Class-C template (lockstep)
- `tests/specialists/gary/test_*.py` — NEW + UPDATED (3 behavioral tests: gamma_dispatch, no_live_api_in_ci, summary_landing)
- `tests/composition/test_gary_to_vera_g3_chain.py` — NEW (chain test; AC-K)
- `tests/fixtures/specialist-replay/gary/` — NEW VCR cassettes
- `state/config/credential-rotation-register.yaml` — UPDATED (Gamma row added)
- `app/specialists/gary/config.yaml` — NEW or EXTENDED (rate-limit budget)
- `docs/dev-guide/composition-specification.md` §10 — NEW Decision Log entry (Class-C 6-file pattern)

### Detected conflicts or variances

- **Sanctum path: Slab 2b.1 vs Slab 7b** — resolved in favor of Slab 7b convention (specialist-name; `bmad-agent-gary/`)
- **SKILL.md skill-dir** — resolved 2026-04-29 post-T1-HALT: `skills/bmad-agent-gamma/SKILL.md` is canonical per epic Story 7b.6 line 708 Class-C convention (API-name path). `skills/bmad-agent-gary/` does NOT exist on disk; do NOT create. `skills/bmad-agent-gamma/references/` consumed (NOT modified) for API-mastery content.

---

## References

- **Round-(e) governance JSON**: [`docs/dev-guide/migration-story-governance.json`](../../docs/dev-guide/migration-story-governance.json) §`stories.7b-6` + §`stories.7b-7.conditional_gate_override` + §`stories.7b-8.conditional_gate_override`
- **Epic + story-level scope**: [`epics-slab-7b-specialist-activation-eleven.md`](../planning-artifacts/epics-slab-7b-specialist-activation-eleven.md) §Story 7b.6
- **PRD FR94**: [`prd-slab-7b-specialist-activation-eleven.md`](../planning-artifacts/prd-slab-7b-specialist-activation-eleven.md) §FR94
- **Sandbox-AC inventory `gamma` (FR107)**: [`docs/dev-guide/migration-ac-sandbox-inventory.json`](../../docs/dev-guide/migration-ac-sandbox-inventory.json) §`gamma`
- **Slab 2b.1 TEMPLATE precedent (Gary's own original migration)**: [`migration-2b-1-gary-scaffold-migration.md`](migration-2b-1-gary-scaffold-migration.md)
- **7b.5 Class-C+ template precedent**: [`migration-7b-5-tracy-port-shape-sidecar.md`](migration-7b-5-tracy-port-shape-sidecar.md)
- **7b.1 substrate**: [`migration-7b-1-texas-hardening.md`](migration-7b-1-texas-hardening.md)
- **7a.5 conversation-persistence contract**: [`migration-7a-5-conversation-persistence-specialist-summary-writer.md`](migration-7a-5-conversation-persistence-specialist-summary-writer.md)
- **BMB sanctum alignment checklist (FR108)**: [`docs/dev-guide/bmb-sanctum-alignment-checklist.md`](../../docs/dev-guide/bmb-sanctum-alignment-checklist.md)
- **Gamma API client**: [`scripts/api_clients/gamma_client.py`](../../scripts/api_clients/gamma_client.py)
- **Gamma API mastery skill**: [`skills/gamma-api-mastery/`](../../skills/gamma-api-mastery/) (`gamma_operations.py::execute_generation`)
- **Composition Spec (NFR-CG15 Decision Log)**: [`docs/dev-guide/composition-specification.md`](../../docs/dev-guide/composition-specification.md)
- **Sprint status**: [`sprint-status.yaml`](sprint-status.yaml)
- **Deferred inventory**: [`deferred-inventory.md`](../planning-artifacts/deferred-inventory.md)
- **CLAUDE.md** — §LangChain/LangGraph migration governance + §BMAD sprint governance + NFR-CG13/19/20

---

## Dev Agent Record

### Agent Model Used

GPT-5

### Debug Log References

- 2026-04-29 T1 restart: Round-(e) E3 trigger binding verified PASS; 7b.5 done and `wave_2b_close.fired_verdict == false`; sandbox-AC preflight PASS; Class-A/B/C+ validator preflight PASS.
- 2026-04-29 T1 drift: `skills/bmad-agent-gary/` was still absent at restart while `skills/bmad-agent-gamma/` existed. Per operator restart instruction, treating Gary persona skill as greenfield drift resolution in-story; `skills/bmad-agent-gamma/` remains unmodified.
- 2026-04-29 focused Gary battery: 64 passed; Class-C validator PASS; live-API detector PASS; `act()` body 37 LOC.
- 2026-04-29 story gates: pipeline lockstep PASS; sandbox-AC final PASS; story-scoped ruff PASS; lint-imports 9/9 KEPT; dispatch_adapter.py diff empty.
- 2026-04-29 broad regression: 1284 passed / 21 skipped / 1 deselected / 2 failed. Residual failures are out-of-scope Desmond live-LLM smoke output shape and known Wanda sanctum drift.

### Completion Notes List

- Drift resolution recorded: Gary sanctum path is `_bmad/memory/bmad-agent-gary/`; canonical persona skill is `skills/bmad-agent-gary/SKILL.md`; `skills/bmad-agent-gamma/` remains API-reference material and was not modified.
- Class-C template extension landed in `validate_parity_test_class_conformance.py`; Class-C requires six-file BMB, Gamma API client binding, VCR cassettes, credential register, rate-limit budget, operator-gated canary documentation, and cold activation smoke.
- Gary `_act.py` invokes `GammaClient.generate_deck(...)`, performs `list_themes()` handshake, supports DOUBLE_DISPATCH variants, normalizes PNG exports via `_materialize_exported_slide_paths`, and emits Vera G3 invocation hooks.
- 7a.5 summary facade wired through Gary `emit_spans` with `gate_id="G2B"`.
- AC-6-B live Gamma canary not run by Codex; remains operator-gated for T13.
- Wave-3 first-port tripwire final `fired_verdict` is Claude/T13 close scope; Codex did not append the final close ledger entry.

### File List

- `_bmad/memory/bmad-agent-gary/INDEX.md`
- `_bmad/memory/bmad-agent-gary/PERSONA.md`
- `_bmad/memory/bmad-agent-gary/CREED.md`
- `_bmad/memory/bmad-agent-gary/BOND.md`
- `_bmad/memory/bmad-agent-gary/MEMORY.md`
- `_bmad/memory/bmad-agent-gary/CAPABILITIES.md`
- `_bmad-output/implementation-artifacts/7b-6-codex-self-review-2026-04-29.md`
- `_bmad-output/implementation-artifacts/migration-7b-6-gary-port-shape.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `app/specialists/gary/_act.py`
- `app/specialists/gary/config.yaml`
- `app/specialists/gary/graph.py`
- `docs/dev-guide/composition-specification.md`
- `scripts/api_clients/gamma_client.py`
- `scripts/utilities/detect_live_api_in_tests.py`
- `scripts/utilities/validate_parity_test_class_conformance.py`
- `skills/bmad-agent-gary/SKILL.md`
- `state/config/credential-rotation-register.yaml`
- `tests/composition/test_gary_to_vera_g3_chain.py`
- `tests/fixtures/composition/gary-to-vera-g3/expected-output.yaml`
- `tests/fixtures/specialist-replay/gary/gamma_dispatch_double_dispatch.yaml`
- `tests/fixtures/specialist-replay/gary/gamma_dispatch_happy_path.yaml`
- `tests/parity/test_gary_activation_contract.py`
- `tests/parity/test_skill_md_sanctum_alignment.py`
- `tests/specialists/gary/test_gary_gamma_dispatch.py`
- `tests/specialists/gary/test_gary_no_live_api_in_ci.py`
- `tests/specialists/gary/test_gary_sanctum_cold_read.py`
- `tests/specialists/gary/test_gary_summary_landing.py`
