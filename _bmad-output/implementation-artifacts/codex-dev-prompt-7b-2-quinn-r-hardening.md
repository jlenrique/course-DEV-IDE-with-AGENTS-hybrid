# Codex dev-story prompt — Story 7b.2 Quinn-R Hardening (Slab 7b Wave-1 parallel)

**Cycle:** Claude spec → Codex dev+tests → Claude bmad-code-review + commit + flip done.
**Wave:** 1 slot 2 — parallel with 7b.1, 7b.3 (Class-A hardening; Claude-authored).
**Gate:** **SINGLE-GATE** (`docs/dev-guide/migration-story-governance.json::stories.7b-2`; rationale: null; rubric-semantics work).
**Round-(e) E5 binding:** **`prerequisite_stories: ["7b-1"]` with binding=hard.** Sprint runner MUST NOT open this story until 7b.1 lands T2 atomic CREATE-tasks (SanctumParityTestBase + chain-test base + class-conformance validator + Errata 4 ratification).

**STATUS:** ⚠️ **STUB — pending Claude spec authoring.** Spec at `_bmad-output/implementation-artifacts/migration-7b-2-quinn-r-hardening.md` does not yet exist. This prompt is a pre-staged readings + boundary file; finalize after Claude runs `bmad-create-story` for 7b.2.

---

```
Run bmad-dev-story on Story 7b.2 (Slab 7b Wave-1; parallel with 7b.1, 7b.3; Class-A hardening; single-gate; Quinn-R two-mode rubric + G2C storyboard-bound + G5 pre-composition QA).

## Required reading (read in order)

1. **Story spec:** `_bmad-output/implementation-artifacts/migration-7b-2-quinn-r-hardening.md` (status: ready-for-dev — pending Claude authoring; expected ACs A-N follow 7b.1 shape).
2. **Round-(e) E5 unblock evidence:** verify 7b.1 T2 atomic-commit landed (`tests/parity/_sanctum_parity_base.py` + `tests/composition/_chain_test_base.py` + `scripts/utilities/validate_parity_test_class_conformance.py` + `tests/parity/README.md` §"FR105 + Errata 4 layout decision" all present). HALT-AND-SURFACE if absent — 7b.2 cannot open until T2 commits.
3. **Slab 7b epics-and-stories §Story 7b.2:** `_bmad-output/planning-artifacts/epics-slab-7b-specialist-activation-eleven.md` lines 487-526.
4. **PRD §FR90:** `_bmad-output/planning-artifacts/prd-slab-7b-specialist-activation-eleven.md` — Quinn-R two-mode (pre-composition / post-composition) rubric semantics + G2C storyboard-bound shape (`authorized-storyboard.json` write contract) + G5 pre-composition QA body (WPM + VTT monotonicity + coverage + motion-vs-narration coherence + advisory-vs-blocking partition).
5. **Governance JSON:** `docs/dev-guide/migration-story-governance.json` story `7b-2` (single-gate; expected_pts=3; expected_k_target=1.3; prerequisite_stories=["7b-1"]).
6. **Slab 7a 7a.5 conversation-persistence contract:** specialist-summary writer + 15-25 line envelope at `runs/<run_id>/specialist-summaries/quinn-r-<gate>-<timestamp>.md`.
7. **7b.1 precedent (Class-A first body):** `_bmad-output/implementation-artifacts/migration-7b-1-texas-hardening.md` + landed test bases (SanctumParityTestBase + ChainTestBase + class-conformance validator).
8. **BMB sanctum alignment checklist (FR108):** `docs/dev-guide/bmb-sanctum-alignment-checklist.md`.
9. **Slab 2a.2 precedent (AC-B 150-LOC ceiling discipline):** `_bmad-output/implementation-artifacts/migration-2a-2-irene-pass-2-scaffold-migration.md`.
10. **CLAUDE.md** governance.

## T1 hard checkpoints (HALT-AND-SURFACE if violated)

- Round-(e) governance JSON pin = `2026-04-29-slab7b-twelve-stories`; `_staged_pending_party_mode_ratification` absent on 7b-2.
- 7b.1 T2 atomic-commit landed — all 4 CREATE-task artifacts present at canonical paths.
- 7b-2 `prerequisite_stories: ["7b-1"]` satisfied (7b.1 status ≥ ready-for-dev with T2 commit; need NOT be `done`).
- Wave 0 artifacts present (6 paths).
- Quinn-R baseline at slab-2a era: `app/specialists/quinn_r/` directory + `_bmad/memory/bmad-agent-quinn-r/` 6-file BMB pattern + `skills/bmad-agent-quality-reviewer/SKILL.md` (note: SKILL.md uses `quality-reviewer` not `quinn-r` per FR101 errata 2 path convention — verify this is the correct dir at T1).
- `state/config/schemas/authorized-storyboard.schema.json` exists OR is to-be-created (lockstep regen via NFR-CG4).

## Files in scope (TBD per spec; expected list)

**New (pending spec finalization; expected ≥7 files):**
- `tests/parity/test_quinn_r_activation_contract.py` — flat layout per Errata 4; inherits SanctumParityTestBase; Class-A template
- `tests/specialists/quinn_r/test_quinn_r_two_mode_rubric.py` — pre/post-composition mode dispatch
- `tests/specialists/quinn_r/test_quinn_r_g2c_storyboard_bound.py` — `authorized-storyboard.json` write contract
- `tests/specialists/quinn_r/test_quinn_r_g5_pre_composition_qa.py` — five sub-checks (WPM/VTT/coverage/duration/advisory-vs-blocking)
- `tests/specialists/quinn_r/test_quinn_r_g3b_post_composition.py` — post-Compositor forensic verdict
- `tests/composition/test_quinn_r_chain.py` — chain test inheriting `ChainTestBase`
- `_bmad-output/implementation-artifacts/7b-2-codex-self-review-2026-04-XX.md` — T10 G6 self-review

**Modified:**
- `app/specialists/quinn_r/_act.py` — implement two-mode rubric body (≤150 LOC AC-B ceiling)
- `state/config/schemas/authorized-storyboard.schema.json` — additive lockstep regen (NFR-CG4)
- `skills/bmad-agent-quality-reviewer/SKILL.md` — verify minimal frontmatter (option-a)

**Do NOT modify:**
- `app/marcus/orchestrator/dispatch_adapter.py:70-95` (substrate-frozen).
- 7b.1's CREATE-task substrate (consume only).
- 7a.1-7a.8 surfaces.

## Critical implementation notes

- **Two-mode rubric:** Quinn-R dispatches at G2C (pre-composition; storyboard-bound) AND G3B (post-composition; forensic verdict on assembled artifacts). Mode is determined by Marcus dispatch context (the `gate_id` carried in the envelope). Same `_act` body, two branches.
- **G2C write contract (FR90):** emit `authorized-storyboard.json` per pre-composition contract; structurally validate against `state/config/schemas/authorized-storyboard.schema.json` (lockstep regen via NFR-CG4 carry-forward — schema is authoritative; emitted JSON validates).
- **G5 pre-composition QA five sub-checks (FR90):** (i) WPM review against `narration_profile_controls.target_wpm`; (ii) VTT monotonicity across captions track; (iii) coverage completeness (every storyboard slide has narration); (iv) motion-vs-narration duration coherence (per-segment delta within tolerance); (v) advisory-vs-blocking partition (block-mode failures vs advisory warnings).
- **Verdict landing:** all rubric verdicts land in `runs/<run_id>/specialist-summaries/quinn-r-<gate>-<timestamp>.md` per 7a.5 contract.
- **AC-B 150-LOC ceiling:** Quinn-R `_act` body ≤150 LOC; HALT-AND-SURFACE re-scope if exceeds.
- **SG-3 §3.5 gate precedence:** Quinn-R is per-specialist non-blocking by default under production composition; advisory-vs-blocking partition is the structural enforcement here.
- **PyYAML, NOT ruamel.** No new third-party deps.

## Verification battery (T9)

```bash
.venv/Scripts/python.exe -m pytest tests/parity/test_quinn_r_activation_contract.py tests/specialists/quinn_r tests/composition/test_quinn_r_chain.py tests/parity/test_skill_md_sanctum_alignment.py -q --tb=short
.venv/Scripts/python.exe -m pytest tests/unit/manifest tests/integration/marcus tests/composition tests/parity tests/structural tests/unit/marcus tests/specialists/texas tests/specialists/quinn_r tests/specialists/_scaffold tests/cli tests/unit/models -q --tb=line --ignore=tests/integration/marcus/test_directive_confirm_or_edit_prompt.py
.venv/Scripts/python.exe scripts/utilities/check_pipeline_manifest_lockstep.py
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7b-2-quinn-r-hardening.md
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/
.venv/Scripts/python.exe -m ruff check app/specialists/quinn_r tests/parity tests/specialists/quinn_r tests/composition
.venv/Scripts/lint-imports.exe
```

Expected: zero new failures vs post-7b.1-T2 baseline.

## T10 + T11 + T12

- **T10:** Codex G6 self-review at `_bmad-output/implementation-artifacts/7b-2-codex-self-review-2026-04-XX.md`. Flip status `in-progress → review`.
- **T11 (Claude):** bmad-code-review at `7b-2-code-review-2026-04-XX.md`; remediation cycle 1 if PASS-WITH-PATCH.
- **T12 (Claude):** sprint-status flip → done; commit + push.

## Boundary

**HALT-AND-SURFACE on:** (a) Round-(e) governance pin mismatch; (b) 7b.1 T2 not yet committed (prerequisite_stories binding); (c) AC-B 150-LOC ceiling exceeded; (d) substrate-frozen-paths violation; (e) K-actual >1.7× target (~3.4K LOC); (f) sandbox-AC violation; (g) authorized-storyboard schema lockstep break (NFR-CG4); (h) sanctum 6-file BMB pattern missing/drifted at `_bmad/memory/bmad-agent-quinn-r/`.

**Do NOT:** touch dispatch_adapter.py:70-95; modify 7b.1 substrate; introduce ruamel/new deps; author tests/parity/per_specialist/ (flat per Errata 4); skip Quinn-R's two-mode shape (both pre + post composition modes required).
```
