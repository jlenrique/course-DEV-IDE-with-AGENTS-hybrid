# Codex dev-story prompt — Story 7b.6 Gary Port-Shape (Slab 7b Wave-3 first port)

**Cycle:** Claude spec → Codex dev+tests → Claude bmad-code-review + commit + flip done.
**Wave:** 3 first-port — strict serial after 7b.5 (Wave-2b Tracy) close. PARALLEL with 7b.7 Kira + 7b.8 Enrique once 7b.6 itself opens.
**Gate:** **SINGLE-GATE** (`docs/dev-guide/migration-story-governance.json::stories.7b-6`; per Slab 2b.1 TEMPLATE pattern).
**Class:** C API-bound (Gamma API; third-party).
**Round-(e) E3 binding-hard upstream trigger:** **7b.6 K-actual at close IS the trigger condition for `conditional_gate_override` on 7b.7 (Kira) + 7b.8 (Enrique).** If 7b.6 closes >2.7K LOC, BOTH 7b.7 and 7b.8 flip to dual-gate at story-open (binding=hard; sprint runner enforces). NO direct binding on 7b.6 itself; 7b.6 stays single-gate.
**No k_contract block on 7b-6.** K-target ~1.4× / ~33 tests / ~2.9K LOC; AC-B 150-LOC ceiling on `_act` body.

**STATUS:** Spec READY-FOR-DEV at `_bmad-output/implementation-artifacts/migration-7b-6-gary-port-shape.md` (Claude-authored 2026-04-29; sandbox-AC validator PASS; 16 ACs A-P + 13 task blocks T1-T13).

---

```
Run bmad-dev-story on Story 7b.6 (Slab 7b Wave-3 first-port; Class-C API-bound; single-gate per Slab 2b.1 TEMPLATE; Gamma API live invocation + per-slide variant generation + theme-handshake + PNG export normalization + Vera G3 invocation hooks).

## Required reading (read in order)

1. **Story spec:** `_bmad-output/implementation-artifacts/migration-7b-6-gary-port-shape.md` (status: ready-for-dev; 16 ACs A-P; 13 tasks T1-T13; you own T1-T12; Claude owns T13 close).
2. **Round-(e) governance JSON** — `docs/dev-guide/migration-story-governance.json` §`stories.7b-6` (single-gate; expected_pts=4; expected_k_target=1.4; NO k_contract block on 7b-6) + §`stories.7b-7.conditional_gate_override` + §`stories.7b-8.conditional_gate_override` (both keyed to 7b.6 first-port tripwire).
3. **Wave-2b close evidence** — verify 7b.5 (Tracy) `done` in `sprint-status.yaml`; read `tripwire_events::wave_2b_close::fired_verdict`. If fired, 7b.6 opens at upper-band K-target per Round-(a) Amelia A3 + Round-(e) E6 escalation chain.
4. **Slab 7b epics-and-stories §Story 7b.6** — `_bmad-output/planning-artifacts/epics-slab-7b-specialist-activation-eleven.md` lines 674-731.
5. **PRD §FR94** — `_bmad-output/planning-artifacts/prd-slab-7b-specialist-activation-eleven.md` §FR94. Gamma API live invocation + per-slide variant generation (DOUBLE_DISPATCH branch) + theme-handshake + PNG export normalization (`_materialize_exported_slide_paths` carry-forward) + Vera G3 invocation hooks.
6. **Sandbox-AC inventory entry `gamma` (FR107; Wave 0 LANDED)** — `docs/dev-guide/migration-ac-sandbox-inventory.json` §`gamma`. "Live invocation NOT assumed on dev-agent session PATH; invoke via httpx + Gamma API client at `scripts/api_clients/gamma_client.py` with `pytest.skip(...)` when `GAMMA_API_KEY` not set. Live evidence belongs in operator-gated AC-*-B blocks."
7. **Slab 2b.1 TEMPLATE precedent (CRITICAL — Gary IS the original 2b.1 specialist; Wave-1-hardening of the same)** — `_bmad-output/implementation-artifacts/migration-2b-1-gary-scaffold-migration.md`. 9-node scaffold + AC-B 150-LOC ceiling + REST-API tool-dispatch pattern + sandbox-AC governance. **Note:** Slab 2b.1 used `_bmad/memory/bmad-agent-gamma/` sanctum path (skill-dir convention); Slab 7b epic line 708 binds `_bmad/memory/bmad-agent-gary/` (specialist-name convention). **Resolution at T1 (binding):** specialist-name path per Slab 7b convention; see Drift #1 below.
8. **`scripts/api_clients/gamma_client.py`** + **`skills/gamma-api-mastery/scripts/gamma_operations.py::execute_generation`** — Gary's runtime production entry point. Read both before authoring Wave-3 hardening.
9. **7b.5 Class-C+ template precedent (immediate predecessor)** — `_bmad-output/implementation-artifacts/migration-7b-5-tracy-port-shape-sidecar.md`. Class-C+ template active in validator at 7b.5 close. **You extend with Class-C template** in lockstep with this story's parity test landing (LOCKSTEP foundational deliverable). Class-C inherits Class-C+ for live-API + VCR + operator-gated-canary; differs in: 6-file vs 4-file sanctum pattern; third-party API vs LLM-only.
10. **CLAUDE.md** — §LangChain/LangGraph migration governance + NFR-CG13 (no live-API in CI; strict prohibition) + NFR-CG19 (credential-rotation register) + NFR-CG20 (rate-limit budget).

## T1 hard checkpoints (HALT-AND-SURFACE if violated)

- Round-(e) E3 trigger-story binding verified (`d['stories']['7b-7']['conditional_gate_override']['trigger_story'] == '7b-6'` AND same for 7b-8; binding=hard).
- 7b.5 (Wave-2b Tracy) status `done` in sprint-status.yaml.
- Wave-1 + Wave-2a + Wave-2b tripwire ledgers readable; Wave-2b close fired_verdict known.
- Class-C+ template active in validator from 7b.5 close (verified via `validate_parity_test_class_conformance.py tests/parity/` PASS).
- Gary baseline at `app/specialists/gary/`: `__init__.py expertise/ gamma_dispatch.py graph.py model_config.yaml state.py` (Slab 2b.1 era; Gamma API dispatch wrapper present).
- `_bmad/memory/bmad-agent-gary/` does NOT yet exist (sanctum greenfield; this story creates 6-file BMB Class-C pattern).
- `_bmad/memory/bmad-agent-gamma/` does NOT yet exist either (Slab 2b.1 era expected this path but never populated; superseded by specialist-name path).
- **Canonical Gary persona-skill surface = `skills/bmad-agent-gamma/`** (verified exists on disk; API-name path per epic Story 7b.6 line 708 SG-4 binding). Class-C API-bound stories use API-name skill-dirs by convention (mirrors 7b.7 Kira's `bmad-agent-kling/` + 7b.8 Enrique's `bmad-agent-elevenlabs/` + 7b.9 Wanda's `bmad-agent-wondercraft/`). **`skills/bmad-agent-gary/` is OUT-OF-SCOPE — does NOT exist, DO NOT create. The original prompt draft erroneously listed it as a hard-checkpoint requirement; that requirement is RESCINDED 2026-04-29 post-Codex-7b.6-T1-HALT.** The only skill-dir hard-checkpoint for 7b.6 is that `skills/bmad-agent-gamma/` exists (verified) — proceed with that as the SG-4 SKILL.md target.
- `skills/gamma-api-mastery/scripts/gamma_operations.py::execute_generation` is import-stable + `_materialize_exported_slide_paths` at `gamma_operations.py:1338` is import-stable (carry-forward).
- `scripts/api_clients/gamma_client.py` exists.
- FR107 sandbox-AC `gamma` entry present in inventory.
- 7b.1 substrate consumable + Class-A/B/C+ templates active in validator.
- Sandbox-AC validator pre-flight PASS on this spec.

## Files in scope

**New (≥10 files):**
- `_bmad/memory/bmad-agent-gary/INDEX.md` + `PERSONA.md` + `CREED.md` + `BOND.md` + `MEMORY.md` + `CAPABILITIES.md` — 6-file BMB sanctum (Class-C canonical; Class-A inheritance pattern; NOT 4-file Class-C+ pattern)
- `tests/parity/test_gary_activation_contract.py` — flat layout; inherits SanctumParityTestBase; **Class-C template** (`class_template_id = "C"`)
- `tests/specialists/gary/test_gary_gamma_dispatch.py` — VCR cassette; happy path + DOUBLE_DISPATCH + theme-handshake + PNG normalization
- `tests/specialists/gary/test_gary_no_live_api_in_ci.py` — AST-scan via `detect_live_api_in_tests.py`
- `tests/specialists/gary/test_gary_summary_landing.py` — 7a.5 facade integration
- `tests/composition/test_gary_to_vera_g3_chain.py` — Vera G3 invocation chain (FR94 + FR91 cross-cut)
- `tests/fixtures/specialist-replay/gary/*.yaml` — VCR cassettes
- `_bmad-output/implementation-artifacts/7b-6-codex-self-review-2026-04-XX.md` — T12 G6 self-review
- (NO cache-hit-rate harness — Class-C is REST-API tool-dispatch; FR106 doesn't generalize)

**Modified:**
- `app/specialists/gary/_act.py` — extract from existing `gamma_dispatch.py` if pattern requires OR refine in-place; bounded body invoking `gamma_client.py` (≤150 LOC AC-B ceiling)
- `app/specialists/gary/graph.py` — additive delegation pattern (mirror Texas/Quinn-R/Vera/Irene-Pass-1 precedent: `_act = _gary_act_impl.act`)
- `skills/bmad-agent-gamma/SKILL.md` — minimal frontmatter (`name` + `description` only) + body referencing `_bmad/memory/bmad-agent-gary/` activation-time hot-load
- `scripts/utilities/validate_parity_test_class_conformance.py` — **EXTEND with Class-C template assertions LOCKSTEP** (additive; A + B + C+ unchanged). Class-C asserts: 6-file BMB sanctum + Gamma API client binding + VCR cassettes present + credential register entry + rate-limit budget declared + cold-activation smoke.
- `state/config/credential-rotation-register.yaml` — ADD Gamma API row (provider/owner/rotation_cadence/last_rotated/next_due/secret_store_reference)
- `app/specialists/gary/config.yaml` — NEW or EXTENDED (rate-limit budget per NFR-CG20: `{rate_limit_per_minute, daily_budget_usd, per_invocation_cap_usd}`)
- `docs/dev-guide/composition-specification.md` §10 — NFR-CG15 Decision Log entry: Class-C canonical 6-file BMB pattern (same as Class-A; distinct from Class-C+ 4-file)

**Do NOT modify:**
- `app/marcus/orchestrator/dispatch_adapter.py` lines 70-95 (substrate-frozen).
- 7b.1-7b.5 substrate (consume only).
- `skills/bmad-agent-gamma/references/` (API-mastery reference content; consume only). **Note:** `skills/bmad-agent-gamma/SKILL.md` IS in scope per AC-7b.6-F (SG-4 alignment update); only the `references/` subdir is out-of-scope. Earlier prompt-draft incorrectly listed the entire `bmad-agent-gamma/` dir as do-not-modify; that has been corrected 2026-04-29 post-T1-HALT.
- Legacy `gamma_dispatch.py` semantics (consume as helper; substrate-as-floor).
- `skills/gamma-api-mastery/` (the API client; consume only).

## Critical implementation notes

- **9-node scaffold per Slab 2b.1 TEMPLATE:** Gary IS the original 2b.1 specialist; this is Wave-3 hardening of the same. Scaffold already established; refine `_act` body, KEEP scaffold.
- **Drift resolution at T1 — three drifts:**
  - **#1 Sanctum path:** Slab 2b.1 era used `bmad-agent-gamma/` (skill-dir-name); Slab 7b epic binds `bmad-agent-gary/` (specialist-name). **Resolution: specialist-name canonical** per Slab 7b. File `gary-sanctum-path-slab-2b-vs-7b-resolution` follow-on as CLOSED at T2.
  - **#2 SKILL.md skill-dir is API-name (NOT specialist-name):** `skills/bmad-agent-gamma/SKILL.md` is canonical per epic Story 7b.6 line 708 (Class-C API-bound pattern uses API-name path; distinct from Class-A specialist-name pattern). `skills/bmad-agent-gary/` does NOT exist; do NOT create.
  - **#3 Existing `gamma_dispatch.py`:** Slab-2b.1 era carry-forward; consume (NOT replace).
- **Gamma API live invocation:** `_act` body invokes `GammaClient.generate_deck(...)` via thin wrapper around `scripts/api_clients/gamma_client.py`. DOUBLE_DISPATCH branch fires when applicable (per Gamma API mastery module §DOUBLE_DISPATCH); theme-handshake via `GammaClient.list_themes()` (live-tested 2026-03-30 era; carry-forward); PNG export normalization via `_materialize_exported_slide_paths` carry-forward from `skills/gamma-api-mastery/scripts/gamma_operations.py:1338`.
- **Vera G3 invocation hooks (FR94 + FR91 cross-cut):** Gary completes per-slide variant generation → Vera G3 invocation hooks fire with real Gamma artifacts (PNG paths) as input. Verified via chain test at `test_gary_to_vera_g3_chain.py`.
- **AC-B 150-LOC ceiling:** Gary `_act` body ≤150 LOC. HALT-AND-SURFACE re-scope party-mode if exceeds.
- **Live-API discipline (NFR-CG13 strict):** All Gary tests use VCR cassettes under `tests/fixtures/specialist-replay/gary/`. NO `from gamma_client import` patterns at file-scope in CI test files (only inside `if not pytest.skip(...)` guards or operator-gated test files). Live canary belongs ONLY in operator-gated AC-6-B Completion-Notes block.
- **Cache-hit-rate N/A for Class-C:** Gary is REST-API tool-dispatch (no LLM at the Gary layer; per Slab 2b.1 close). FR106 measurement category does NOT generalize to Class-C per Slab-2a-retrospective §FR54-doesn't-generalize. Documented in Class-C template assertions.
- **Credential register (NFR-CG19):** add Gamma row at `state/config/credential-rotation-register.yaml`: `{provider: "gamma", owner: "operator", rotation_cadence_days: 90, last_rotated: "<YYYY-MM-DD>", next_due: "<YYYY-MM-DD+90d>", secret_store_reference: "operator-machine .env GAMMA_API_KEY"}`.
- **Rate-limit budget (NFR-CG20):** declare in `app/specialists/gary/config.yaml` (or model_config.yaml extension): `{rate_limit_per_minute: <N>, daily_budget_usd: <X>, per_invocation_cap_usd: <Y>}`.
- **Class-C template extension to validator (LOCKSTEP):** extend `validate_parity_test_class_conformance.py` Class-C template assertions in same commit as the parity test. Class-A + B + C+ unchanged. Class-C inherits most of Class-C+ (live-API + VCR + operator-gated-canary) but asserts 6-file BMB pattern (vs Class-C+ 4-file) + third-party API binding (vs Class-C+ LLM-only).
- **NFR-CG15 Decision Log entry:** file at `docs/dev-guide/composition-specification.md` §10 — Class-C canonical 6-file BMB pattern (same as Class-A; distinct from Class-C+ 4-file). Future Class-C stories (7b.7 Kira / 7b.8 Enrique / 7b.9 Wanda) inherit.
- **Wave-3 first-port tripwire (Round-(e) E3 trigger record):** at story close, append a NEW `wave_3_first_port_tripwire` entry to `sprint-status.yaml::tripwire_events`. The fired_verdict is the trigger that 7b.7 + 7b.8 sprint-runner reads at THEIR story-open. If LOC > 2.7K, fired_verdict: true → BOTH 7b.7 + 7b.8 flip dual-gate at their open per Round-(e) E3 binding-hard.
- **Operator-gated AC-6-B (NFR-T11b T5 live canary):** ≤3 invocations; cost ≤$0.40 per canary; evidence pasted into Completion Notes. Operator-gated ONLY; sandbox-AC validator does NOT check this block.
- **PyYAML, NOT ruamel.**
- **No new third-party deps.**
- **Sanctum gitignore:** `_bmad/memory/bmad-agent-gary/` will be gitignored at commit per `bmad-memory-gitignore-force-add-policy`; Claude T13 commit uses `git add --force`.

## Verification battery (T9)

```bash
.venv/Scripts/python.exe -m pytest tests/parity/test_gary_activation_contract.py tests/specialists/gary tests/composition/test_gary_to_vera_g3_chain.py tests/parity/test_skill_md_sanctum_alignment.py -q --tb=short
.venv/Scripts/python.exe -m pytest tests/unit/manifest tests/integration/marcus tests/composition tests/parity tests/structural tests/unit/marcus tests/specialists tests/cli tests/unit/models -q --tb=line --ignore=tests/integration/marcus/test_directive_confirm_or_edit_prompt.py
.venv/Scripts/python.exe scripts/utilities/check_pipeline_manifest_lockstep.py
.venv/Scripts/python.exe scripts/utilities/detect_live_api_in_tests.py
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7b-6-gary-port-shape.md
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/
.venv/Scripts/python.exe -m ruff check app/specialists/gary tests/parity/test_gary_activation_contract.py tests/specialists/gary tests/composition/test_gary_to_vera_g3_chain.py scripts/utilities/validate_parity_test_class_conformance.py
.venv/Scripts/lint-imports.exe
```

Expected: zero new failures vs post-7b.5 baseline (pre-existing `wanda-sanctum-test-expected-files-constant-drift` flake remains; not Gary-introduced).

## T10 + T11 + T12 + T13

- **T10 (Codex):** wire credential register + rate-limit budget; file Decision Log entry at composition-spec §10.
- **T11 (Codex):** regression baseline + sandbox-AC final + ruff/lint-imports.
- **T12 (Codex):** G6 self-review at `_bmad-output/implementation-artifacts/7b-6-codex-self-review-2026-04-XX.md`. Flip status `in-progress → review`.
- **T13 (Claude):** bmad-code-review at `7b-6-code-review-2026-04-XX.md`; remediation cycle 1 if PASS-WITH-PATCH; operator-gated AC-6-B if window opens; **append wave_3_first_port_tripwire ledger entry with FINAL fired_verdict** per AC-7b.6-N (this is the upstream trigger 7b.7+7b.8 read at their open); sprint-status flip done; commit + push (force-add gitignored sanctum); next-session-start-here.md pivot to Wave 3 PARALLEL (7b.7 + 7b.8) with gate-mode applied per E3 conditional_gate_override.

## Boundary

**HALT-AND-SURFACE on:**
- (a) Round-(e) E3 trigger-story binding pin mismatch
- (b) 7b.5 not `done`
- (c) AC-B 150-LOC ceiling exceeded on Gary `_act` body
- (d) substrate-frozen-paths violation (dispatch_adapter.py:70-95 diff)
- (e) **K-actual >1.7× target (~4.9K LOC OR >40 active tests)** — 7b.6 has NO k_contract block but pre-fires K-aggregate concern given Wave-3 first-port discipline; flag pre-T2 if K-projection trends >2.7K (party-mode awareness; tripwire fires AT close measurement)
- (f) sandbox-AC violation
- (g) live-API import detected by AST scan in CI test files (NFR-CG13 strict prohibition; only `pytest.skip(...)`-guarded OR operator-gated blocks may reference)
- (h) sanctum 6-file BMB pattern drifts from Class-A precedent (must match Texas/Quinn-R/Vera/Irene 6 files: `INDEX.md` / `PERSONA.md` / `CREED.md` / `BOND.md` / `MEMORY.md` / `CAPABILITIES.md`)
- (i) Class-C template extension to validator breaks Class-A or B or C+ backward compat (validator must PASS on existing Texas/Quinn-R/Vera/Irene-Pass-1/Tracy tests post-extension)
- (j) Composition Spec §10 Decision Log entry for Class-C 6-file pattern not filed
- (k) credential register + rate-limit budget entries missing (NFR-CG19/CG20)

**Do NOT:**
- Touch substrate-frozen lines (dispatch_adapter.py:70-95)
- Modify `skills/bmad-agent-gamma/` or `skills/gamma-api-mastery/` (out-of-scope; consume only)
- Modify legacy `gamma_dispatch.py` semantics (consume as helper; substrate-as-floor)
- Modify 7b.1-7b.5 substrate (parity base, chain base, validator A/B/C+ templates, prior story scaffolds)
- Introduce ruamel.yaml or new third-party deps
- Author `tests/parity/per_specialist/` subdir (Errata 4 verdict-flat per 7b.1 T2)
- Add cache-hit-rate harness (FR106 N/A for Class-C; explicitly documented in Class-C template)
- Skip the Class-C template extension lockstep (foundational deliverable for 7b.7/7b.8/7b.9 inheritance)
- Skip the Composition Spec §10 Decision Log entry (NFR-CG15)
- Run live Gamma API in CI (NFR-CG13 strict; live canary ONLY in operator-gated AC-6-B Completion-Notes)
```
