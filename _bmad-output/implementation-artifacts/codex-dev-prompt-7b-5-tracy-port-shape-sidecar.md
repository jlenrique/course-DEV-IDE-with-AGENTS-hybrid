# Codex dev-story prompt — Story 7b.5 Tracy Port-Shape + Sidecar Creation (Slab 7b Wave-2b)

**Cycle:** Claude spec → Codex dev+tests → Claude bmad-code-review + commit + flip done.
**Wave:** 2b — strict serial after 7b.4 (Wave-2a Irene Pass-1) close.
**Gate:** **SINGLE-GATE** (`docs/dev-guide/migration-story-governance.json::stories.7b-5`; per Slab 2b.1 TEMPLATE pattern).
**Class:** C+ port-shape + sidecar emission BUNDLE (LLM-only; no third-party API).
**Round-(e) E4 binding-hard:** `required_ac_reference_paths: ["skills/bmad-agent-texas/references/retrieval-contract.md"]` — Tracy's research-shaped intent enrichment touches Texas retrieval-lane interface; AC coverage of the Tracy↔Texas interface required, NOT optional.
**Round-(e) E6 k_contract:** scope=Pass-2 enrichment + sidecar 4-file BMB; tripwire 2.7K → Wave-2b close K-aggregate escalation; if fired: Wave-3 first-port (7b.6 Gary) opens at upper-band K-target + 7b.7 Kira + 7b.8 Enrique pre-authorized for dual-gate via Round-(e) E3 hooks.

**STATUS:** Spec READY-FOR-DEV at `_bmad-output/implementation-artifacts/migration-7b-5-tracy-port-shape-sidecar.md` (Claude-authored 2026-04-29; sandbox-AC validator PASS; 14 ACs A-N + 12 task blocks T1-T12).

---

```
Run bmad-dev-story on Story 7b.5 (Slab 7b Wave-2b; Class-C+ port-shape + sidecar BUNDLE; single-gate per Slab 2b.1 TEMPLATE; LLM-only research-shaped intent enrichment).

## Required reading (read in order)

1. **Story spec:** `_bmad-output/implementation-artifacts/migration-7b-5-tracy-port-shape-sidecar.md` (status: ready-for-dev; 14 ACs A-N; 12 tasks T1-T12; you own T1-T11; Claude owns T12 close).
2. **Round-(e) governance JSON** — `docs/dev-guide/migration-story-governance.json` §`stories.7b-5` (single-gate; expected_pts=5; expected_k_target=1.5; `k_contract` block + `required_ac_reference_paths` present).
3. **Wave-2a close evidence** — verify 7b.4 (Irene Pass-1) `done` in sprint-status.yaml. Read `tripwire_events::wave_1_close::fired_verdict` (already known: marginal-fired); upper-band K-target signal carries forward.
4. **Slab 7b epics-and-stories §Story 7b.5** — `_bmad-output/planning-artifacts/epics-slab-7b-specialist-activation-eleven.md` lines 623-670.
5. **PRD §FR93** — `_bmad-output/planning-artifacts/prd-slab-7b-specialist-activation-eleven.md` §FR93. Tracy research-shaped intent enrichment for Pass-2 + sidecar greenfield + 4-file BMB pattern + 9-node scaffold per Slab 2b.1 TEMPLATE + live LLM-only binding (no third-party API).
6. **Texas retrieval-contract (Round-(e) E4 binding-hard)** — `skills/bmad-agent-texas/references/retrieval-contract.md`. Tracy emits `RetrievalIntent` objects with `intent: str` + `provider_hints: list[ProviderHint]` REQUIRED v1 + `acceptance_criteria` three-tier (`mechanical` / `provider_scored` / `semantic_deferred`). Tracy does NOT translate provider DSLs — adapter responsibility (knowledge-locality discipline).
7. **Slab 2b.1 TEMPLATE precedent (Gary; original 9-node scaffold pattern)** — `_bmad-output/implementation-artifacts/migration-2b-1-gary-scaffold-migration.md`. AC-B 150-LOC ceiling discipline + bounded-scope acts + sandbox-AC governance.
8. **Specialist migration template** — `docs/dev-guide/specialist-migration-template.md` (R1-R14).
9. **Class-B template precedent (from 7b.4)** — `scripts/utilities/validate_parity_test_class_conformance.py` extended with Class-B template at 7b.4 close. **You extend with Class-C+ template** in lockstep with this story's parity test landing (LOCKSTEP foundational deliverable). Class-C+ asserts: 4-file BMB sidecar pattern (NOT 6-file); live-LLM binding; cache-hit-rate harness wired; sidecar-emission parity.
10. **CLAUDE.md** — §LangChain/LangGraph migration governance + §BMAD sprint governance.

## T1 hard checkpoints (HALT-AND-SURFACE if violated)

- Round-(e) E4+E6 governance JSON pin verified (`version == "2026-04-29-slab7b-twelve-stories"`; `k_contract.tripwire_threshold_kloc == 2.7`; `required_ac_reference_paths` present).
- 7b.4 (Wave-2a Irene Pass-1) status `done` in sprint-status.yaml.
- Wave-1 + Wave-2a tripwire ledgers readable; Wave-1 close `fired_verdict: marginal-fired` known.
- Tracy baseline at `app/specialists/tracy/`: `__init__.py expertise/ graph.py model_config.yaml posture_dispatch.py state.py` (slab-2b era passthrough; 9-node scaffold present).
- `_bmad/memory/bmad-agent-tracy/` does NOT yet exist (sidecar greenfield; this story creates 4-file BMB pattern).
- `_bmad/memory/tracy-sidecar/` also does NOT exist (Tracy is fresh greenfield; no legacy sidecar to preserve).
- `skills/bmad-agent-tracy/SKILL.md` exists (placeholder; needs sanctum-aware activation order on update).
- 7b.1 substrate consumable: `tests/parity/_sanctum_parity_base.py` + `tests/composition/_chain_test_base.py` + `scripts/utilities/validate_parity_test_class_conformance.py` (Class-A + B templates active).
- Texas retrieval-contract verified accessible at `skills/bmad-agent-texas/references/retrieval-contract.md` (Round-(e) E4 binding).
- `gpt-5.4` model registry entry present (LLM-only binding).
- Sandbox-AC validator pre-flight PASS on this spec.

## Files in scope

**New (≥10 files):**
- `_bmad/memory/bmad-agent-tracy/INDEX.md` + `PERSONA.md` + `chronology.md` + `access-boundaries.md` — 4-file BMB sidecar (Class-C+ canonical; NOT 6-file)
- `tests/parity/test_tracy_activation_contract.py` — flat layout; inherits SanctumParityTestBase; **Class-C+ template** (`class_template_id = "C+"` or `"Cplus"` if symbol-safe)
- `tests/specialists/tracy/test_tracy_retrieval_intent_emission.py` — RetrievalIntent shape per Texas retrieval-contract; parametrized over `cross_validate` true/false
- `tests/specialists/tracy/test_tracy_no_third_party_api_imports.py` — AST-scan via `detect_live_api_in_tests.py`; FAIL if any third-party adapter import detected
- `tests/specialists/tracy/test_tracy_sidecar_4_file_pattern.py` — 4-file presence + content shape
- `tests/specialists/tracy/test_tracy_summary_landing.py` — 7a.5 facade integration
- `tests/composition/test_tracy_to_texas_chain.py` — Round-(e) E4 binding-hard interface coverage; inherits ChainTestBase
- `tests/end_to_end/test_tracy_cache_hit_rate.py` — `@pytest.mark.llm_live`; Slab 2a.2 MF1+MF2+MF5 discipline + 7b.4 inheritance
- `_bmad-output/implementation-artifacts/7b-5-codex-self-review-2026-04-XX.md` — T11 G6 self-review

**Modified:**
- `app/specialists/tracy/_act.py` — replace passthrough body with bounded RetrievalIntent emission body (≤150 LOC AC-B ceiling); invoke `gpt-5.4` via `app.models.adapter.ChatOpenAIAdapter` with `tier_request: reasoning`
- `app/specialists/tracy/graph.py` — additive delegation pattern (mirror Texas/Quinn-R/Vera precedent: `_act = _tracy_act_impl.act`)
- `app/specialists/tracy/model_config.yaml` — `default_model: "gpt-5.4"` + `temperature_default: 0.3` (research-enrichment creativity)
- `skills/bmad-agent-tracy/SKILL.md` — minimal frontmatter (`name` + `description` only) + body referencing `_bmad/memory/bmad-agent-tracy/` activation-time hot-load
- `scripts/utilities/validate_parity_test_class_conformance.py` — **EXTEND with Class-C+ template assertions LOCKSTEP** (additive; A + B unchanged)
- `docs/dev-guide/composition-specification.md` §10 — NFR-CG15 Decision Log entry: Class-C+ canonical 4-file BMB sidecar pattern (distinct from Class-A 6-file)
- `docs/dev-guide/sanctum-reference-conventions.md` — possibly UPDATE if 4-file Class-C+ pattern needs canonical doc entry

**Do NOT modify:**
- `app/marcus/orchestrator/dispatch_adapter.py` lines 70-95 (substrate-frozen).
- 7b.1-7b.4 substrate (consume only).
- Texas retrieval-contract at `skills/bmad-agent-texas/references/retrieval-contract.md` (consume only — Round-(e) E4 binding-hard interface).
- Legacy `posture_dispatch.py` at `app/specialists/tracy/` (consume as helper; substrate-as-floor).
- `tests/parity/_sanctum_parity_base.py` body (extend via Class-C+ branch in validator if needed; base class stays).

## Critical implementation notes

- **9-node scaffold per Slab 2b.1 TEMPLATE:** `receive/plan/act/verify/reflect/emit_spans/gate_decision/finalize/handoff` canonical SCAFFOLD_NODE_IDS frozenset.
- **RetrievalIntent emission per Texas retrieval-contract (Round-(e) E4 BINDING-HARD):** Tracy's `_act` body emits one or more `RetrievalIntent` objects with REQUIRED v1 fields:
  - `intent: str` (natural-language; NOT pre-translated to provider DSL)
  - `provider_hints: list[ProviderHint]` REQUIRED — no auto-discovery; each `{provider: <id>, params: <dict>}`; provider IDs from `provider_directory.list_providers(shape="retrieval", status_in={ready, stub})`
  - `acceptance_criteria` three-tier: `mechanical` (Texas filters) / `provider_scored` (provider filters) / `semantic_deferred` (Tracy's downstream pass)
  - optional `cross_validate: true` for first-class cross-provider fan-out
  Tracy does NOT translate per-provider DSLs (adapter responsibility per knowledge-locality discipline).
- **Sidecar 4-file BMB pattern (NOT 6-file Class-A):** Class-C+ uses `INDEX.md` / `PERSONA.md` / `chronology.md` / `access-boundaries.md` (4 files). Distinct from Class-A 6-file (`INDEX.md` / `PERSONA.md` / `CREED.md` / `BOND.md` / `MEMORY.md` / `CAPABILITIES.md`).
- **AC-B 150-LOC ceiling:** Tracy `_act` body ≤150 LOC. HALT-AND-SURFACE re-scope party-mode if exceeds.
- **LLM-only (no third-party API):** Tracy uses `gpt-5.4` via `ChatOpenAIAdapter`; no `from gamma_client/kling_client/elevenlabs_client/wondercraft_client import` patterns. AST-scan via `detect_live_api_in_tests.py` enforces. NO sandbox-AC inventory entry needed (per R5 Amelia-scope-amendment).
- **Cache-hit-rate harness (FR106):** N=10 in-process; `prompt_tokens >> 1024` MF2 floor; `median[2:] >= 85%` post-warm-up; OpenAI usage API as cache-metric source (per Slab 2a.2 MF1+MF2+MF5 + 7b.4 inheritance). `@pytest.mark.llm_live` auto-skip on placeholder API key.
- **Class-C+ template extension to validator (LOCKSTEP):** extend `validate_parity_test_class_conformance.py` Class-C+ template assertions in same commit as the parity test. Class-A + B unchanged.
- **NFR-CG15 Decision Log entry:** file at `docs/dev-guide/composition-specification.md` §10 — Class-C+ canonical 4-file BMB sidecar pattern; distinct from Class-A 6-file.
- **Wave-2b close tripwire (Round-(e) E6):** if 7b.5 LOC > 2.7K, K-aggregate tripwire fires → record at `sprint-status.yaml::tripwire_events::wave_2b_close`; Wave-3 first-port (7b.6 Gary) opens at upper-band K-target + 7b.7+7b.8 conditional_gate_override pre-authorized via Round-(e) E3 hooks.
- **PyYAML, NOT ruamel.**
- **No new third-party deps.**
- **Sanctum gitignore:** `_bmad/memory/bmad-agent-tracy/` will be gitignored at commit per `bmad-memory-gitignore-force-add-policy` follow-on; Claude T12 commit uses `git add --force`.

## Verification battery (T9)

```bash
.venv/Scripts/python.exe -m pytest tests/parity/test_tracy_activation_contract.py tests/specialists/tracy tests/end_to_end/test_tracy_cache_hit_rate.py tests/composition/test_tracy_to_texas_chain.py tests/parity/test_skill_md_sanctum_alignment.py -q --tb=short
.venv/Scripts/python.exe -m pytest tests/unit/manifest tests/integration/marcus tests/composition tests/parity tests/structural tests/unit/marcus tests/specialists tests/cli tests/unit/models -q --tb=line --ignore=tests/integration/marcus/test_directive_confirm_or_edit_prompt.py
.venv/Scripts/python.exe scripts/utilities/check_pipeline_manifest_lockstep.py
.venv/Scripts/python.exe scripts/utilities/detect_live_api_in_tests.py
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7b-5-tracy-port-shape-sidecar.md
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/
.venv/Scripts/python.exe -m ruff check app/specialists/tracy tests/parity/test_tracy_activation_contract.py tests/specialists/tracy tests/composition/test_tracy_to_texas_chain.py tests/end_to_end/test_tracy_cache_hit_rate.py scripts/utilities/validate_parity_test_class_conformance.py
.venv/Scripts/lint-imports.exe
```

Expected: zero new failures vs post-7b.4 baseline (pre-existing `wanda-sanctum-test-expected-files-constant-drift` flake remains; not Tracy-introduced).

## T10 + T11 + T12

- **T10 (Codex):** G6 self-review at `_bmad-output/implementation-artifacts/7b-5-codex-self-review-2026-04-XX.md`. Flip status `in-progress → review`.
- **T11 (Claude):** bmad-code-review at `7b-5-code-review-2026-04-XX.md`; remediation cycle 1 if PASS-WITH-PATCH.
- **T12 (Claude):** sprint-status flip done; Wave-2b close tripwire-events ledger entry per AC-7b.5-K (Round-(e) E2 + E6 binding); commit + push (force-add gitignored sanctum); Wave 3 (7b.6 Gary) UNBLOCKS at this close.

## Boundary

**HALT-AND-SURFACE on:**
- (a) Round-(e) E4+E6 governance pin mismatch
- (b) 7b.4 not `done`
- (c) Texas retrieval-contract path not accessible (Round-(e) E4 binding)
- (d) AC-B 150-LOC ceiling exceeded
- (e) substrate-frozen-paths violation (dispatch_adapter.py:70-95 diff)
- (f) K-actual >1.7× target (~5.6K LOC OR >36 active tests + escalation per k_contract)
- (g) sandbox-AC violation
- (h) live-API import detected by AST scan (Tracy is LLM-only — NO `from gamma_client/kling_client/elevenlabs_client/wondercraft_client import` patterns)
- (i) sidecar 4-file pattern drifts to 6-file BMB (Class-C+ violation; check INDEX/PERSONA/chronology/access-boundaries are the ONLY 4 files at `_bmad/memory/bmad-agent-tracy/`)
- (j) Class-C+ template extension to validator breaks Class-A or Class-B backward compat (validator must PASS on existing Texas/Quinn-R/Vera/Irene-Pass-1 tests post-extension)
- (k) Composition Spec §10 Decision Log entry for Class-C+ 4-file pattern not filed

**Do NOT:**
- Introduce third-party API client for Tracy (LLM-only via gpt-5.4 only)
- Touch substrate-frozen lines (dispatch_adapter.py:70-95)
- Modify Texas retrieval-contract at `skills/bmad-agent-texas/references/retrieval-contract.md` (consume only)
- Modify 7b.1-7b.4 substrate (parity base, chain base, validator Class-A/B templates, prior story scaffolds)
- Introduce ruamel.yaml or new third-party deps
- Author `tests/parity/per_specialist/` subdir (Errata 4 verdict-flat per 7b.1 T2)
- Skip the Class-C+ template extension lockstep (foundational deliverable for Wave 3 inheritance)
- Skip the Composition Spec §10 Decision Log entry (NFR-CG15)
```
