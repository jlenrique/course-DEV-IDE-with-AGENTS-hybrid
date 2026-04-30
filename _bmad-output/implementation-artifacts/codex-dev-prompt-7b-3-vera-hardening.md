# Codex dev-story prompt — Story 7b.3 Vera Hardening (Slab 7b Wave-1 parallel)

**Cycle:** Claude spec → Codex dev+tests → Claude bmad-code-review + commit + flip done.
**Wave:** 1 slot 3 — parallel with 7b.1, 7b.2 (Class-A hardening; Claude-authored).
**Gate:** **SINGLE-GATE** (`docs/dev-guide/migration-story-governance.json::stories.7b-3`).
**Round-(e) E5 binding:** **`prerequisite_stories: ["7b-1"]` with binding=hard.** Sprint runner MUST NOT open this story until 7b.1 T2 atomic CREATE-tasks land.

**STATUS:** ⚠️ **STUB — pending Claude spec authoring.** Spec at `_bmad-output/implementation-artifacts/migration-7b-3-vera-hardening.md` does not yet exist.

---

```
Run bmad-dev-story on Story 7b.3 (Slab 7b Wave-1; parallel with 7b.1, 7b.2; Class-A hardening; single-gate; Vera G0/G1/G3/G4 fidelity rubrics + sensory-bridges dispatch).

## Required reading (read in order)

1. **Story spec:** `_bmad-output/implementation-artifacts/migration-7b-3-vera-hardening.md` (pending Claude authoring).
2. **Round-(e) E5 unblock evidence:** verify 7b.1 T2 atomic-commit landed (substrate present).
3. **Slab 7b epics-and-stories §Story 7b.3:** `_bmad-output/planning-artifacts/epics-slab-7b-specialist-activation-eleven.md` lines 530-575.
4. **PRD §FR91:** Vera G0 6-dim evidence-sentence rubric on real Texas output + G1 ingestion-quality 6-dim verdicts + G3 fidelity check on real Storyboard A + G4 19-criterion rubric (G4-01..G4-19, codified in `g4-narration-script.yaml` per Epic 23 closure) + sensory-bridges dispatch on real motion + audio + circuit-breaker mechanism.
5. **Governance JSON:** `docs/dev-guide/migration-story-governance.json` story `7b-3` (single-gate; expected_pts=3; expected_k_target=1.3; prerequisite_stories=["7b-1"]).
6. **Epic 23 closure docs:** `g4-narration-script.yaml` codifies the 19 G4 criteria.
7. **7b.1 precedent (Class-A first body):** `_bmad-output/implementation-artifacts/migration-7b-1-texas-hardening.md`.
8. **Sensory-bridges skill:** verify location at T1 (universal perception protocol — image/audio/video).
9. **Slab 2a.2 precedent (AC-B 150-LOC):** `migration-2a-2-irene-pass-2-scaffold-migration.md`.
10. **CLAUDE.md** governance + **BMB sanctum alignment checklist (FR108)**.

## T1 hard checkpoints (HALT-AND-SURFACE if violated)

- Round-(e) governance JSON pin verified.
- 7b.1 T2 atomic-commit landed.
- Vera baseline: `app/specialists/vera/` exists + `_bmad/memory/bmad-agent-vera/` 6-file BMB pattern + `skills/bmad-agent-fidelity-assessor/SKILL.md` (NOT `skills/bmad-agent-vera/` — Vera's skill-dir uses `fidelity-assessor` per FR101 errata 2 path convention; verify at T1).
- `g4-narration-script.yaml` exists with 19 criteria (G4-01..G4-19) per Epic 23 closure.
- Sensory-bridges skill location verified.
- 7b.1's `tests/parity/_sanctum_parity_base.py` consumable.

## Files in scope (TBD per spec)

**New (expected ≥8 files):**
- `tests/parity/test_vera_activation_contract.py` — flat layout; inherits SanctumParityTestBase; Class-A template
- `tests/specialists/vera/test_vera_g0_evidence_sentence_rubric.py`
- `tests/specialists/vera/test_vera_g1_ingestion_quality_verdicts.py`
- `tests/specialists/vera/test_vera_g3_fidelity_storyboard_a.py`
- `tests/specialists/vera/test_vera_g4_19_criterion_rubric.py` — parametrized over 19 criteria
- `tests/specialists/vera/test_vera_sensory_bridges_dispatch.py`
- `tests/specialists/vera/test_vera_circuit_breaker.py` — HALT-AND-REMEDIATE on hard-fail O/I/A
- `tests/composition/test_vera_chain.py` — inherits ChainTestBase
- `_bmad-output/implementation-artifacts/7b-3-codex-self-review-2026-04-XX.md`

**Modified:**
- `app/specialists/vera/_act.py` — fidelity rubrics body (≤150 LOC AC-B ceiling); G0 + G1 + G3 + G4 + sensory-bridges dispatch + circuit-breaker.
- `skills/bmad-agent-fidelity-assessor/SKILL.md` — verify minimal frontmatter (option-a).

**Do NOT modify:**
- `app/marcus/orchestrator/dispatch_adapter.py:70-95`.
- 7b.1's CREATE-task substrate.
- 7a.1-7a.8 surfaces.
- `g4-narration-script.yaml` (consume only — Epic 23 owns).

## Critical implementation notes

- **G0 6-dim evidence-sentence rubric (FR91):** scores Texas's `extracted.md` against six dimensions; emits Fidelity Trace Report at `runs/<run_id>/fidelity/g0-vera-<timestamp>.json` with O/I/A taxonomy itemized.
- **O/I/A taxonomy:** Omissions / Inventions / Alterations — structural shape required in trace report.
- **G4 19-criterion rubric (FR91):** parametrize over 19 criteria from `g4-narration-script.yaml`; each criterion emits verdict with severity + description.
- **Sensory-bridges dispatch (FR91):** universal perception protocol invokes for image/audio/video; confidence rubric scores in trace report. Verify the skill location at T1 — exact path may need probing.
- **Circuit-breaker (per APP fidelity architecture):** on hard-fail O/I/A finding, HALT-AND-REMEDIATE; control returns to operator with verdict carrying failure reason. Behavioral contract — Vera does NOT silently advance.
- **AC-B 150-LOC ceiling:** Vera `_act` body ≤150 LOC.
- **Wave-1 close gate (Round-(a) Amelia A3):** if 7b.1/7b.2/7b.3 aggregate >2.7K LOC, K-aggregate tripwire fires — record at `sprint-status.yaml::tripwire_events` per Round-(e) E2 ledger. Tripwire status is logged by 7b.1 closer (per epic file convention) once all three Wave-1 stories close.
- **PyYAML, NOT ruamel.**

## Verification battery (T9)

```bash
.venv/Scripts/python.exe -m pytest tests/parity/test_vera_activation_contract.py tests/specialists/vera tests/composition/test_vera_chain.py tests/parity/test_skill_md_sanctum_alignment.py -q --tb=short
.venv/Scripts/python.exe -m pytest tests/unit/manifest tests/integration/marcus tests/composition tests/parity tests/structural tests/unit/marcus tests/specialists/texas tests/specialists/quinn_r tests/specialists/vera tests/specialists/_scaffold tests/cli tests/unit/models -q --tb=line --ignore=tests/integration/marcus/test_directive_confirm_or_edit_prompt.py
.venv/Scripts/python.exe scripts/utilities/check_pipeline_manifest_lockstep.py
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7b-3-vera-hardening.md
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/
.venv/Scripts/python.exe -m ruff check app/specialists/vera tests/parity tests/specialists/vera tests/composition
.venv/Scripts/lint-imports.exe
```

Expected: zero new failures vs post-7b.1-T2 baseline.

## T10 + T11 + T12

- **T10:** Codex G6 self-review; flip review.
- **T11 (Claude):** bmad-code-review + remediation cycle 1 if needed.
- **T12 (Claude):** sprint-status flip done; tripwire-events ledger updated if Wave-1 close fires; commit.

## Boundary

**HALT-AND-SURFACE on:** (a) Round-(e) pin mismatch; (b) 7b.1 T2 not committed; (c) AC-B 150-LOC exceeded; (d) substrate-frozen violation; (e) K-actual >1.7× target; (f) sandbox-AC violation; (g) `g4-narration-script.yaml` 19-criterion list drift from Epic 23; (h) sensory-bridges skill not located at T1 (need scope amendment); (i) circuit-breaker bypass — Vera silently advances on O/I/A hard-fail; (j) sanctum drift at `_bmad/memory/bmad-agent-vera/`.

**Do NOT:** touch substrate-frozen lines; modify 7b.1 substrate; introduce ruamel/new deps; author per_specialist/ subdir; bypass O/I/A circuit-breaker; skip 19-criterion full coverage on G4.
```
