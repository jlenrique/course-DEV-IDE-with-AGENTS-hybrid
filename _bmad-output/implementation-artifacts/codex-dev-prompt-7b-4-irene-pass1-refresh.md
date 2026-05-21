# Codex dev-story prompt — Story 7b.4 Irene Pass-1 Refresh (Slab 7b Wave-2a)

**Cycle:** Claude spec → Codex dev+tests → Claude bmad-code-review + commit + flip done.
**Wave:** 2a — strict after Wave 1 closes (Vera G4 inheritance from 7b.3).
**Gate:** **SINGLE-GATE** (`docs/dev-guide/migration-story-governance.json::stories.7b-4`; persona-continuity refresh; mirrors Pass-2 shape).
**Class:** B refresh; Claude-authored.

**STATUS:** ⚠️ **STUB — pending Claude spec authoring.** Spec at `_bmad-output/implementation-artifacts/migration-7b-4-irene-pass1-refresh.md` does not yet exist.

---

```
Run bmad-dev-story on Story 7b.4 (Slab 7b Wave-2a; serial after Wave-1 close; Class-B refresh; single-gate; Irene Pass-1 9-node scaffold mirroring Pass-2 + lesson-plan coauthoring + scope-lock contract).

## Required reading (read in order)

1. **Story spec:** `_bmad-output/implementation-artifacts/migration-7b-4-irene-pass1-refresh.md` (pending Claude authoring).
2. **Wave-1 close evidence:** verify 7b.1 + 7b.2 + 7b.3 all `done` in sprint-status.yaml; tripwire-events ledger entry for `wave_1_close` recorded (fired or not-fired).
3. **Slab 7b epics-and-stories §Story 7b.4:** `_bmad-output/planning-artifacts/epics-slab-7b-specialist-activation-eleven.md` lines 579-619.
4. **PRD §FR92:** Irene Pass-1 9-node scaffold + lesson-plan coauthoring + scope-lock contract + per-plan-unit ratification surface for G1A + `irene-pass1.md` artifact write + mode-singularity hard-constraint + `scope_decision.set` + `plan.locked` learning-event emission.
5. **Slab 2a.2 Pass-2 precedent (CRITICAL — 9-node scaffold pattern):** `_bmad-output/implementation-artifacts/migration-2a-2-irene-pass-2-scaffold-migration.md`. Mirror the 9-node shape; respect AC-B 150-LOC ceiling.
6. **Governance JSON:** `docs/dev-guide/migration-story-governance.json` story `7b-4` (single-gate; expected_pts=3; expected_k_target=1.3).
7. **Vera G4 19-criterion rubric (from 7b.3 close):** Pass-1 plan must be reviewable by Vera G4 downstream — verify rubric is consumable.
8. **Cache-hit-rate harness (FR106):** `gpt-5.4`; `prompt_tokens >> 1024` MF2 floor; `median[2:] >= 85%` post-warm-up; N=10.
9. **7b.1 precedent (substrate consumers):** SanctumParityTestBase + ChainTestBase + class-conformance validator.
10. **CLAUDE.md** governance + **BMB sanctum alignment checklist (FR108)**.

## T1 hard checkpoints (HALT-AND-SURFACE if violated)

- Wave-1 stories ALL `done` (7b.1 + 7b.2 + 7b.3).
- Wave-1 close tripwire status read from `sprint-status.yaml::tripwire_events` — if `wave_1_close` fired, K-target tightening may apply.
- Irene Pass-2 baseline at `app/specialists/irene/` (note: Pass-1 + Pass-2 share `irene` skill-dir + `bmad-agent-content-creator` skill convention — verify at T1; per Slab 2a.2 era structure).
- 9-node scaffold canonical at `tests/integration/scaffold_conformance/scaffold_contract.py::SCAFFOLD_NODE_IDS`.
- `_bmad/memory/bmad-agent-irene/` (or `_bmad/memory/bmad-agent-content-creator/` — verify hybrid path) sanctum 6-file BMB pattern present.
- Vera G4 rubric consumable (7b.3 closure provides).

## Files in scope (TBD per spec)

**New:**
- `app/specialists/irene_pass1/` directory with 9-node scaffold (per Pass-2 shape) — OR an integrated `app/specialists/irene/` with mode-singularity branching. Spec author decides at T1.
- `tests/parity/test_irene_pass1_activation_contract.py` — Class-B template
- `tests/specialists/irene_pass1/test_irene_pass1_lesson_plan_coauthoring.py`
- `tests/specialists/irene_pass1/test_irene_pass1_scope_lock_contract.py`
- `tests/specialists/irene_pass1/test_irene_pass1_per_plan_unit_ratification.py`
- `tests/specialists/irene_pass1/test_irene_pass1_mode_singularity.py` — mode-singularity hard-constraint
- `tests/specialists/irene_pass1/test_irene_pass1_learning_events.py` — `scope_decision.set` + `plan.locked`
- `tests/end_to_end/test_irene_pass1_cache_hit_rate.py` — harness N=10; @pytest.mark.llm_live
- `_bmad-output/implementation-artifacts/7b-4-codex-self-review-2026-04-XX.md`

**Modified:**
- `skills/bmad-agent-content-creator/SKILL.md` — verify minimal frontmatter (option-a; Pass-1 + Pass-2 share)
- `app/manifest/...` — Irene Pass-1 manifest registration if not already present from Slab 2a.2 era

**Do NOT modify:**
- Pass-2 body at `app/specialists/irene/` (consume mode shape only)
- substrate-frozen-paths
- 7b.1-7b.3 substrate

## Critical implementation notes

- **9-node scaffold mirroring Pass-2 (CRITICAL):** `receive/plan/act/verify/reflect/emit_spans/gate_decision/finalize/handoff` — canonical SCAFFOLD_NODE_IDS frozenset. Mirror Pass-2 byte-for-byte except for the body of `_act` and the mode-discriminator.
- **Mode-singularity hard-constraint:** Pass-1 cannot run in Pass-2 mode (and vice versa). Enforce at the dispatch boundary; raise `ModeMismatchError` if invoked under wrong mode. Fail-loud, not fail-silent.
- **Lesson-plan coauthoring + scope-lock:** Irene Pass-1 authors `irene-pass1.md` lesson plan; operator reviews per-plan-unit (NOT bulk auto-confirm); on confirmation, emit `scope_decision.set` + `plan.locked` learning events. Pass-2 inherits locked scope (per Wave 2 sequencing — Tracy's Pass-2 enrichment runs against locked plan).
- **Per-plan-unit ratification surface (G1A):** operator confirms each plan unit; surfaces are operator-touchable (NOT bulk-confirm). HIL contract.
- **AC-B 150-LOC ceiling:** Irene Pass-1 `_act` body ≤150 LOC.
- **Cache-hit-rate harness (FR106):** Class-B uses `gpt-5.4`; deterministic prompt assembly (per Slab 2a.2 MF1 byte-stability discipline); `median[2:] >= 85%`; N=10 in-process.
- **Sanctum dir convention:** `_bmad/memory/bmad-agent-irene/` (skill-dir name follows hybrid path convention — verify at T1 per Slab 2a.2 drift #3).
- **PyYAML, NOT ruamel.**

## Verification battery (T9)

```bash
.venv/Scripts/python.exe -m pytest tests/parity/test_irene_pass1_activation_contract.py tests/specialists/irene_pass1 tests/end_to_end/test_irene_pass1_cache_hit_rate.py tests/parity/test_skill_md_sanctum_alignment.py -q --tb=short
.venv/Scripts/python.exe -m pytest tests/unit/manifest tests/integration/marcus tests/composition tests/parity tests/structural tests/unit/marcus tests/specialists tests/cli tests/unit/models -q --tb=line --ignore=tests/integration/marcus/test_directive_confirm_or_edit_prompt.py
.venv/Scripts/python.exe scripts/utilities/check_pipeline_manifest_lockstep.py
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7b-4-irene-pass1-refresh.md
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/
.venv/Scripts/python.exe -m ruff check app/specialists/irene_pass1 tests/parity tests/specialists/irene_pass1
.venv/Scripts/lint-imports.exe
```

Expected: zero new failures vs post-Wave-1-close baseline.

## T10 + T11 + T12

- **T10:** Codex G6 self-review; flip review.
- **T11 (Claude):** bmad-code-review + remediation if needed.
- **T12 (Claude):** sprint-status flip done; commit + push; Wave-2b (7b.5 Tracy) UNBLOCKS.

## Boundary

**HALT-AND-SURFACE on:** (a) Wave-1 not all `done`; (b) 9-node scaffold drift from Pass-2 (any node missing or renamed); (c) AC-B 150-LOC exceeded; (d) mode-singularity violation (Pass-1 invokable in Pass-2 mode); (e) substrate-frozen violation; (f) cache-hit-rate harness `median[2:] < 85%` (investigate prompt byte-stability per Slab 2a.2 MF1); (g) sandbox-AC violation; (h) sanctum dir drift; (i) Vera G4 rubric not consumable.

**Do NOT:** touch Pass-2 body; modify substrate-frozen lines; introduce ruamel/new deps; bulk-auto-confirm plan units (per-plan-unit HIL required); skip mode-singularity enforcement.
```
