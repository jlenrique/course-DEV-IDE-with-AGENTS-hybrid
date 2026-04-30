# Codex dev-story prompt — Story 7b.11 Compositor Greenfield (Slab 7b Wave-5b)

**Cycle:** Claude spec → Codex dev+tests → Claude bmad-code-review + commit + flip done.
**Wave:** 5b — strict-after-Wave-3 closed; parallelizable with 7b.10 Dan; opens after 7b.10 if serialized.
**Gate:** **SINGLE-GATE (DEFAULT) → DUAL-GATE (CONDITIONAL via Round-(e) E1 binding-hard at pre-T1 K-projection >4.0K)** — non-discretionary T1 trigger; gate flips BEFORE any code is written if K-projection ≥4.0K.
**Class:** D2 sidecar variant (canonical, NOT exception per D20; EXEMPT from FR101.iv sanctum-path-equality).

**T1 BLOCKING DECISION — pre-T1 K-projection check (Round-(e) E1 binding-hard):**
- **T1.6 mandatory:** project total LOC for all in-scope files (sanctum 4-file + scaffold consumption + `_act` body + 9 parity-test assertions + harness wiring + chain test + summary integration). If projection ≥4.0K, HALT, record `conditional_dual_gate_escalation` fired in Dev Agent Record + tripwire ledger, flip story to dual-gate per E1, add Gate-2 ceremony to T11/T12.
- Default expected: ~3.5K LOC (per epic); single-gate proceeds.
- **Class-D2 NOT subject to Class-C two-SKILL.md ratification** — D2 has its own scaffold-v0.2-D2-pipeline contract per FR111. Single SKILL.md at `skills/compositor/SKILL.md` (NOT at `skills/bmad-agent-compositor/`).

**Class-D2 introduces NEW template extension to validator (LOCKSTEP foundational deliverable):**
- This is the FIRST + ONLY Class-D2 specialist in Slab 7b. Class-D2 template assertions added to `scripts/utilities/validate_parity_test_class_conformance.py` in this story.
- After 7b.11 close, validator supports A/B/C+/C/D1/D2 (6 classes total; FULL coverage per SG-4).

**STATUS:** Spec READY-FOR-DEV at `_bmad-output/implementation-artifacts/migration-7b-11-compositor-greenfield.md` (Claude-authored 2026-04-29; sandbox-AC validator PASS; 14 ACs A-N + 14 task blocks; Round-(e) E1 + E6 binding-hard). 5pt budget (NOT 4pt — Class-D2 sidecar variant + harness + new template extension).

---

```
Run bmad-dev-story on Story 7b.11 (Slab 7b Wave-5b; Class-D2 sidecar variant; SINGLE-GATE default → DUAL-GATE conditional at pre-T1 K-projection >4.0K; Compositor greenfield consuming scaffold-v0.2-D2-pipeline (FR111); 4-file operational-metadata sidecar at `_bmad/memory/bmad-agent-compositor/`; deterministic assembly pipeline _act body — sync-visuals + DESCRIPT-ASSEMBLY-GUIDE.md regeneration; pipeline-determinism harness ≥99%).

## Required reading (read in order)

1. **Story spec:** `_bmad-output/implementation-artifacts/migration-7b-11-compositor-greenfield.md` (status: ready-for-dev; 14 ACs A-N; 14 tasks; you own T1-T12; Claude owns T13 close).
2. **Round-(e) governance JSON** — `docs/dev-guide/migration-story-governance.json` §`stories.7b-11`:
   - `expected_gate_mode == "single-gate"` (default)
   - `conditional_dual_gate_escalation.binding == "hard"` (E1; trigger_condition starts with `pre_t1_k_projection_kloc`; trigger_check_owner = dev-agent at story T1)
   - `k_contract.tripwire_threshold_kloc == 4.0` (E6; binds to E1)
   - **Verify with:** `.venv/Scripts/python.exe -c "import json; d = json.load(open('docs/dev-guide/migration-story-governance.json', encoding='utf-8')); entry = d['stories']['7b-11']; assert entry['k_contract']['tripwire_threshold_kloc'] == 4.0; assert entry['conditional_dual_gate_escalation']['binding'] == 'hard'; print('Round-(e) E1+E6 verified PASS for 7b-11')"`
3. **Wave-5a close-state** — read `sprint-status.yaml::tripwire_events::wave_5a_close` + 7b.10 Dan status (must be `done` before 7b.11 opens IF serialized; OR parallelizable with 7b.10 per operator preference).
4. **PRD §FR99** — Compositor Class-D2 sidecar variant (canonical, NOT exception per D20); persona artifacts as sidecar with operational-metadata content (`contract.md` / `version.md` / `chronology.md` / `access-boundaries.md`); EXEMPT from FR101.iv sanctum-path-equality. Pipeline-determinism harness ≥99% (bytes-identical for sync-visuals; field-masked-hash for DESCRIPT-ASSEMBLY-GUIDE.md modulo `{generated_at, run_id, build_timestamp}`).
5. **PRD §FR111 + Wave 0 scaffold-v0.2-D2-pipeline (LANDED)** — `docs/dev-guide/scaffolds/scaffold-v0.2-D2-pipeline/`. 7 files: `README.md` + `scaffold.yaml` + `field-mask.yaml` + 5 templates (`contract.md.template` + `version.md.template` + `chronology.md.template` + `access-boundaries.md.template` + `pipeline-determinism.md.template`). **Compositor is the seed exemplar for Class-D2; templates are consumed here at first activation.**
6. **D20 Class-D2 ratification** — `_bmad-output/planning-artifacts/prd-slab-7b-specialist-activation-eleven.md` §D20 (sidecar variant as canonical class, NOT exception).
7. **D17 H-Pipeline contract** — pipeline-determinism rate ≥99% (9-of-10 minimum; bytes-identical for sync-visuals; field-masked-hash for DESCRIPT-ASSEMBLY-GUIDE.md per scaffold field-mask.yaml).
8. **Slab 2c.1 era Compositor precedent (if any)** — search `app/specialists/compositor/` (likely greenfield; this story is FIRST landing). If pre-existing partial scaffold exists, surface drift at T1.5.
9. **Specialist migration template (R1-R14)** — `docs/dev-guide/specialist-migration-template.md`.
10. **CLAUDE.md** — §LangChain/LangGraph migration governance + NFR-CG13/19/20 + bmad-memory-gitignore-force-add-policy + Round-(e) E1 conditional dual-gate escalation procedure.

## T1 hard checkpoints (HALT-AND-SURFACE if violated)

- Round-(e) governance pin verified (one-liner above; assertions PASS).
- Waves 1+2a+2b+3 all `done` (8 stories; 7b.1 through 7b.8) + 7b.9 Wanda `done` (Wave-4).
- 7b.10 Dan status either `done` (serialized after) OR not-yet-opened (parallelizable; document choice in Dev Agent Record).
- Class-A/B/C+/C/D1 templates active in validator from 7b.1-7b.10 closes (verified via `validate_parity_test_class_conformance.py tests/parity/` PASS).
- Compositor baseline: `app/specialists/compositor/` does NOT yet exist (greenfield posture confirmed) OR partial existing scaffold surfaces drift (record at T1.5).
- `_bmad/memory/bmad-agent-compositor/` does NOT yet exist (sidecar greenfield).
- `skills/compositor/SKILL.md` does NOT yet exist (or exists pre-Slab-2b stub; verify and refresh per FR111).
- scaffold-v0.2-D2-pipeline 7 files all present at `docs/dev-guide/scaffolds/scaffold-v0.2-D2-pipeline/` (Wave 0 LANDED verification).
- Sandbox-AC validator pre-flight PASS.
- **T1.6 K-projection check (BLOCKING):** project total LOC; record value. If ≥4.0K, flip dual-gate per E1 binding-hard. Default expected ~3.5K → single-gate.

## Files in scope

**New (≥14 files; greenfield posture):**
- `_bmad/memory/bmad-agent-compositor/contract.md` (consume from `scaffold-v0.2-D2-pipeline/contract.md.template`)
- `_bmad/memory/bmad-agent-compositor/version.md` (from `version.md.template`)
- `_bmad/memory/bmad-agent-compositor/chronology.md` (from `chronology.md.template`)
- `_bmad/memory/bmad-agent-compositor/access-boundaries.md` (from `access-boundaries.md.template`)
  — 4-file operational-metadata sidecar pattern (Class-D2 canonical per D20; NOT 6-file BMB)
- `app/specialists/compositor/__init__.py` + `_act.py` + `graph.py` + `state.py` + `model_config.yaml` + `expertise/README.md` + `config.yaml` — scaffold-v0.2 instantiation per FR111 templates
- `tests/parity/test_compositor_activation_contract.py` — flat layout; **NEW Class-D2 template** (`class_template_id = "D2"`; `specialist_name = "compositor"`; sanctum-path-equality EXEMPT per D20)
- `tests/specialists/compositor/test_compositor_sync_visuals_deterministic.py` — bytes-identical assertion across runs (D17 H-Pipeline contract)
- `tests/specialists/compositor/test_compositor_assembly_guide_field_masked_hash.py` — field-masked-hash assertion modulo `{generated_at, run_id, build_timestamp}`
- `tests/specialists/compositor/test_compositor_summary_landing.py` — 7a.5 facade integration
- `tests/parity/test_pipeline_determinism_harness.py` — 10-iteration harness aggregator; ≥9-of-10 rate
- `tests/composition/test_compositor_4_input_chain.py` — chain-test extending `ChainTestBase`; 4-input integration (Quinn-R + Tracy + Enrique + Wanda inputs → Compositor output)
- `_bmad-output/implementation-artifacts/7b-11-codex-self-review-2026-04-XX.md` — T12 G6 self-review

**Modified:**
- `scripts/utilities/validate_parity_test_class_conformance.py` — **NEW Class-D2 template assertions (9 per AC-G)** (LOCKSTEP foundational deliverable; first D2 close):
  - (i) sidecar at `_bmad/memory/bmad-agent-compositor/` with 4-file operational-metadata pattern
  - (ii) skill at `skills/compositor/SKILL.md` aligned per scaffold-v0.2-D2-pipeline contract
  - (iii) scaffold-v0.2 conformance via `validate_scaffold`
  - (iv) `_act` body invokes deterministic pipeline (no LLM; bytes-identical sync-visuals + field-masked-hash assembly-guide)
  - (v) sanctum-path-equality EXEMPT per D20 (no `bmad-agent-compositor` SKILL.md alongside)
  - (vi) pipeline-determinism harness wired
  - (vii) 4-input chain test present
  - (viii) operator-control parity row landed
  - (ix) Composition Spec §10 Decision Log entry filed
- `skills/compositor/SKILL.md` — refresh or NEW per FR111 contract (operational-metadata pointers; NOT persona-skill — Class-D2 has NO persona)
- `app/specialists/compositor/config.yaml` — declare deterministic-pipeline rate-limit budget (CPU/memory; NOT API-rate)

**Do NOT modify:**
- `app/marcus/orchestrator/dispatch_adapter.py` lines 70-95 (substrate-frozen).
- 7b.1-7b.10 substrate (consume only; class A/B/C+/C/D1 templates inherited).
- Class-A/B/C+/C/D1 template assertions in validator (extend ONLY for D2; do not modify A/B/C+/C/D1).
- scaffold-v0.2-D2-pipeline templates at `docs/dev-guide/scaffolds/scaffold-v0.2-D2-pipeline/` (CONSUME; do not modify; refinements come post-trial-2).

## Critical implementation notes

- **T1.6 K-projection check (BLOCKING; Round-(e) E1 binding-hard):** record total-LOC estimate in Dev Agent Record T1 block. If ≥4.0K, halt + flip dual-gate. Document the math (per-file LOC × file count). Default expected: ~3.5K → single-gate proceeds.
- **Class-D2 sidecar variant (D20; canonical NOT exception):** NO `_bmad/memory/bmad-agent-compositor/INDEX.md` / `PERSONA.md` / `CREED.md` / `BOND.md` / `MEMORY.md` / `CAPABILITIES.md` 6-file BMB. Instead 4-file operational-metadata: `contract.md` / `version.md` / `chronology.md` / `access-boundaries.md` (per scaffold-v0.2-D2-pipeline templates). Compositor is operational pipeline, NOT persona — no persona-skill at `skills/bmad-agent-compositor/`.
- **Single SKILL.md at `skills/compositor/SKILL.md` (NOT `bmad-agent-compositor`):** Class-D2 has its own scaffold-v0.2-D2-pipeline contract per FR111. Two-SKILL.md is Class-C-only per Round-(f).
- **scaffold-v0.2-D2-pipeline consumption (FR111):** consume the 5 templates at scaffold instantiation. Field-mask per `field-mask.yaml` (modulo `{generated_at, run_id, build_timestamp}` for DESCRIPT-ASSEMBLY-GUIDE.md). Compositor is the seed exemplar — templates may need polishing during dev; if so, file `scaffold-v0-2-d2-pipeline-template-polish-from-7b-11-dev` follow-on.
- **Deterministic assembly pipeline `_act` body (FR99 primary; D17 H-Pipeline):**
  - **sync-visuals operation:** localized PNG stills land at `[BUNDLE_PATH]/assembly-bundle/visuals/<slide_id>.png`; motion clips land at `[BUNDLE_PATH]/assembly-bundle/motion/<slide_id>.{mp4|webm}`. **Bytes-identical across runs given fixed inputs.**
  - **DESCRIPT-ASSEMBLY-GUIDE.md regeneration:** template-driven from manifest + bundle inputs; `{generated_at, run_id, build_timestamp}` field-masked at hash-comparison time per scaffold's `field-mask.yaml`.
  - **NO LLM call — deterministic only.** Class-D2 has NO LLM at Compositor layer.
- **AC-B 150-LOC ceiling on `_act` body** (carry-forward from prior body stories; Compositor body is bounded compute, not creative).
- **Pipeline-determinism harness (FR106 H-Pipeline; AC-E):** 10-iteration harness; rate ≥99% (9-of-10 minimum); bytes-identical for visuals + motion; field-masked-hash for assembly-guide. Authored at `tests/parity/test_pipeline_determinism_harness.py`.
- **Cache-hit-rate N/A for Class-D2:** no LLM; H-Pipeline is the harness contract instead.
- **Live-API discipline (NFR-CG13 strict):** N/A — Compositor has no API. Pure deterministic pipeline.
- **Credential register (NFR-CG19):** N/A — no third-party credentials.
- **Rate-limit budget (NFR-CG20):** declare CPU/memory budget in `app/specialists/compositor/config.yaml` (NOT API-rate); concurrency ceiling per scaffold.
- **K-contract tripwire 4.0K binding-hard (E6) + conditional dual-gate (E1):** if cumulative LOC count >4.0K mid-development, HALT and surface to operator + flip dual-gate per E1 binding-hard. Likely signals pipeline scope creep.
- **Class-D2 template extension (LOCKSTEP):** add D2 assertions to `validate_parity_test_class_conformance.py`. Pattern (9 assertions per AC-G; see Files in scope above).
- **Composition Spec §10 Decision Log entry (AC-K; NFR-CG15):** file an entry naming Class-D2 sidecar variant as canonical-not-exception per D20; cite FR111 + 7b.11 close.
- **PyYAML, NOT ruamel.** No new third-party deps. Sanctum gitignored — Claude T13 commit uses `git add --force` for `_bmad/memory/bmad-agent-compositor/`.

## Verification battery (T11)

```bash
.venv/Scripts/python.exe -m pytest tests/parity/test_compositor_activation_contract.py tests/specialists/compositor tests/composition/test_compositor_4_input_chain.py tests/parity/test_pipeline_determinism_harness.py tests/parity/test_skill_md_sanctum_alignment.py -q --tb=short
.venv/Scripts/python.exe -m pytest tests/unit/manifest tests/integration/marcus tests/composition tests/parity tests/structural tests/unit/marcus tests/specialists tests/cli tests/unit/models -q --tb=line --ignore=tests/integration/marcus/test_directive_confirm_or_edit_prompt.py
.venv/Scripts/python.exe scripts/utilities/check_pipeline_manifest_lockstep.py
.venv/Scripts/python.exe scripts/utilities/detect_live_api_in_tests.py
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7b-11-compositor-greenfield.md
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/    # MUST pass with NEW D2 template active (6 classes total)
.venv/Scripts/python.exe -m ruff check app/specialists/compositor tests/parity/test_compositor_activation_contract.py tests/specialists/compositor tests/composition/test_compositor_4_input_chain.py
.venv/Scripts/lint-imports.exe
```

Expected: zero new failures vs post-7b.10 baseline. **Class-D2 template now active in validator** (6 classes total: A/B/C+/C/D1/D2). **Pipeline-determinism harness reports ≥99% rate.**

## T12 + T13

- **T12 (Codex):** G6 self-review at `_bmad-output/implementation-artifacts/7b-11-codex-self-review-2026-04-XX.md`. Flip status `in-progress → review`. **If conditional dual-gate fired at T1.6, also author Gate-2 evidence script `7b-11-gate2-evidence-commands.ps1` for operator ceremony.**
- **T13 (Claude):** bmad-code-review at `7b-11-code-review-2026-04-XX.md`; remediation cycle 1 if PASS-WITH-PATCH; **append `wave_5b_close` ledger entry** (Wave-5b single-story close) to `sprint-status.yaml::tripwire_events`; if k_contract tripwire fired (>4.0K) OR conditional dual-gate fired at T1.6, record both events in ledger; sprint-status flip done; commit + push (force-add gitignored sanctum); next-session-start-here.md pivot to 7b.12 Wave-6 Integration open. **Slab 7b is now ready for closeout** (all 11 body stories done; only 7b.12 integration remains).

## Boundary

**HALT-AND-SURFACE on:**
- (a) 7b.9 Wanda not `done` in sprint-status (Wave-4 close incomplete) — strict prereq
- (b) 7b.10 Dan not `done` AND operator did NOT explicitly authorize parallel start with Wave-5a — record decision in T1.6
- (c) Round-(e) governance pin mismatch (E1 + E6 assertions FAIL)
- (d) **T1.6 K-projection ≥4.0K** — flip dual-gate per E1 binding-hard; record in ledger; add Gate-2 ceremony to T11/T12 — DO NOT proceed at single-gate
- (e) AC-B 150-LOC ceiling exceeded
- (f) substrate-frozen-paths violation
- (g) sandbox-AC violation
- (h) live-API import detected by AST scan in CI test files (Class-D2 has NO API; should be zero hits)
- (i) sidecar 4-file operational-metadata pattern drift from canonical (must match `contract.md` / `version.md` / `chronology.md` / `access-boundaries.md` exactly per scaffold-v0.2-D2-pipeline)
- (j) Class-D2 template extension breaks A/B/C+/C/D1 inheritance (validator must PASS for ALL existing classes + NEW D2)
- (k) Pipeline-determinism harness reports rate <99% — investigate non-determinism source (likely field-mask drift or unmasked timestamp leak); rate <99% is not acceptable per D17
- (l) k_contract tripwire 4.0K exceeded mid-dev (post-T1.6 K-projection) — HALT, record in ledger, flip dual-gate per E6 binding to E1
- (m) scaffold-v0.2-D2-pipeline 7-file presence FAIL at T1.4 (Wave 0 LANDED contract violated)
- (n) any LLM call in `_act` body (Class-D2 is deterministic-pipeline only; no LLM)

**Do NOT:**
- Touch substrate-frozen lines
- Modify scaffold-v0.2-D2-pipeline templates at `docs/dev-guide/scaffolds/scaffold-v0.2-D2-pipeline/` (consume only; refinements post-trial-2 via follow-on `scaffold-v0-2-d2-pipeline-template-polish-from-7b-11-dev`)
- Modify 7b.1-7b.10 substrate (parity base, chain base, validator A/B/C+/C/D1 templates, prior story scaffolds)
- Author 6-file BMB sanctum at `bmad-agent-compositor/` (Class-D2 is 4-file sidecar per D20; NOT 6-file BMB)
- Author persona-skill at `skills/bmad-agent-compositor/` (Class-D2 has NO persona; SKILL.md lives at `skills/compositor/`)
- Apply Class-C two-SKILL.md ratification (Class-D2 NOT subject to it per FR99 + Round-(f) Class-C-only ratification)
- Introduce ruamel.yaml or new third-party deps
- Author `tests/parity/per_specialist/` subdir (Errata 4 verdict-flat)
- Add LLM invocation to `_act` body (deterministic only; D17 H-Pipeline contract violated by LLM call)
- Skip the pre-T1 K-projection check (E1 binding-hard; non-discretionary)
- Skip the pipeline-determinism harness wiring (FR106 H-Pipeline; AC-E binding)
- Skip the Class-D2 template extension to validator (LOCKSTEP foundational deliverable; SG-4 closeout depends on it)
```
