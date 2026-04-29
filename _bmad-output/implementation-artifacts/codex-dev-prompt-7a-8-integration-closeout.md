# Codex dev-story prompt — Story 7a.8 (integration + parity-test suite + Slab 7a closeout)

**Cycle:** Claude spec → Codex dev+tests → Claude bmad-code-review + commit + flip done.
**Wave:** 5 slot 2 (strict-last; parallel start with 7a.7).
**Gate:** **DUAL-GATE** — operator-witnessed Gate-2 evidence ceremony required at T10/T11 boundary.
**Strict prereq:** ALL 7 prior Slab 7a stories must be `done` before 7a.8 dev opens.

---

```
Run bmad-dev-story on Story 7a.8 (Slab 7a Wave 5 strict-last; DUAL-GATE; integration + 33-row parity-test suite + Composition Spec invariant test suite + calibration-tripwire + engagement-decay report + Marcus-duality boundary + NFR-CG block aggregated + Slab 7a CLOSEOUT).

## Required reading (read in order)

1. Story spec: `_bmad-output/implementation-artifacts/migration-7a-8-integration-parity-test-suite-slab-7a-closeout.md` (status: ready-for-dev; 12 ACs A-L; 12 tasks T1-T12; you own T1-T11)
2. ALL 7 prior Slab 7a stories MUST be `done` in BOTH spec status + sprint-status.yaml: 7a.1, 7a.2, 7a.3, 7a.4, 7a.5, 7a.6, 7a.7. **Verify all 7 at T1.**
3. Mapping checklist (READ-ONLY; 33 rows): `_bmad-output/planning-artifacts/slab-7-legacy-migrated-mapping-checklist.md`
4. Composition Spec (all 7 §§ tested): `docs/dev-guide/composition-specification.md` §3.1, §3.5, §3.6, §6, §9, §10, §11
5. Governance JSON: `docs/dev-guide/migration-story-governance.json` story `7a-8` (DUAL-GATE; expected_pts=4; expected_k_target=1.6; rationale=`operator_acceptance_gate + invariant_preservation`)
6. PRD §Success Criteria A-1..A-7 (the 7 acceptance clauses for trial-2 readiness predicate BS-2)
7. PRD §NFR-CG1-CG11 (the closeout governance gate block)
8. CLAUDE.md §BMAD sprint governance + §Deferred-inventory governance (both apply at closeout)
9. Sandbox-AC inventory: `docs/dev-guide/migration-ac-sandbox-inventory.json`
10. Slab 6.5 retrospective at `_bmad-output/implementation-artifacts/migration-6-5-hud-per-step-expandable-summaries.md` (precedent for retrospective shape)

## T1 hard checkpoints (HALT-AND-SURFACE if violated)

- ALL 7 prior Slab 7a stories `done` in BOTH spec status + sprint-status.yaml. **No story may be in `review` or `in-progress`.**
- 7a.6's `tests/parity/test_operator_control_parity.py` exists with 33 test functions (the SG-2 floor scaffold; 7a.8 populates the per-row test bodies if 7a.6 left them as placeholders, OR aggregates them with REFERENCES_FRS + MAPPING_CHECKLIST_ROW headers).
- 7a.4's `OperatorVerdict.revise_count` field exists (max-3 oscillation invariant).
- 7a.2's `production_gate_ids(manifest)` returns `{G1, G2C, G3, G4}` (the 4 active terminal gates).
- 7a.1/7a.5's `runs/<trial_id>/run_summary.yaml` shape exists (silent_bypass_events: 0 invariant from 7a.2).

## Files in scope

**New:** `tests/parity/test_mapping_checklist_row_NN.py` (or 33 individual files OR consolidated single file with 33 test functions per AC-7.8-A — operator-decision; mirror 7a.6's parity-suite shape); `tests/parity/test_composition_spec_invariants.py` per AC-7.8-B; `tests/parity/test_nfr_cg_block_aggregated.py` per AC-7.8-H; `tests/integration/marcus/test_{calibration_tripwire,engagement_decay_report,marcus_duality_boundary}.py`; `_bmad-output/implementation-artifacts/slab-7a-retrospective.md` (per `bmad-retrospective` skill); `_bmad-output/implementation-artifacts/7a-8-codex-self-review-2026-04-XX.md`.

**Modified:** `app/marcus/orchestrator/gate_runner.py` (extend or create — additive — for tripwire substrate + Marcus-duality runtime assertion); `_bmad-output/implementation-artifacts/sprint-status.yaml` + `bmm-workflow-status.yaml` + `next-session-start-here.md` + `_bmad-output/planning-artifacts/deferred-inventory.md` (Claude T11/T12 close protocol).

**Do NOT modify:** specialist bodies; 7a.1-7a.7 surfaces (only consume); manifest; v4.2 prompt pack.

## Critical implementation notes

- **DUAL-GATE — operator-witnessed Gate-2 evidence ceremony at T10:** operator runs the full focused + wider regression battery + sandbox-AC + lockstep + ruff + lint-imports + Composition Smoke + trial-2 (or trial-2 dry-run); pastes verbatim stdout into Completion Notes. **Codex prepares the script; operator runs it.**
- **33-row parity-test suite (AC-7.8-A):** mirror the 7a.6 scaffold shape; each test header declares `REFERENCES_FRS = [...]` + `MAPPING_CHECKLIST_ROW = NN`. Many will be `@pytest.mark.skip` placeholders awaiting Slab 7b activations; that's expected.
- **Composition Spec invariant test suite (AC-7.8-B):** all 7 §§ tested in one file `tests/parity/test_composition_spec_invariants.py`; one test function per §.
- **Calibration-tripwire (AC-7.8-C):** wire into `app/marcus/orchestrator/gate_runner.py` (extend or create); rolling N-run window over operator-override-rate; auto-lock at affected gate for next 3 trials; log fire AND quiet events at `_artifacts/trial-2/calibration_tripwire_log.jsonl`; FM-5 inverse — silence is NOT assumed healthy; quiet must be witnessed.
- **Synthetic-disagreement injection fixture:** ≥3-axis disagreement triggers tripwire; consensus stays quiet; ≥1 fire + ≥1 quiet captured in trial-2.
- **Engagement-decay report (AC-7.8-E):** auto-emit `_artifacts/trial-2/engagement_decay_report.md` at trial close; SM-4 threshold (last-quartile ratio ≥ 0.30 × first-quartile) breach triggers C1 calibration-tripwire.
- **Marcus-duality boundary (AC-7.8-G):** runtime-asserted boundary in dispatch adapter — orchestrator-mode state never mixes with operator-handoff state. Reviewer (Claude) confirms in code-review.
- **NFR-CG block aggregated test (AC-7.8-H):** `tests/parity/test_nfr_cg_block_aggregated.py` — 11 cases (one per NFR-CG); each asserts the relevant artifact exists + meets the criterion.
- **Slab 7a retrospective (AC-7.8-J):** author at `_bmad-output/implementation-artifacts/slab-7a-retrospective.md` per `bmad-retrospective` skill; mirror `_bmad-output/implementation-artifacts/slab-2a-retrospective.md` shape.
- **Golden-trace fixtures (AC-7.8-K):** if trial-2 has run by 7a.8 close, commit fixtures under `_bmad-output/trial-fixtures/<trial-2-id>/`; if NOT, defer to Slab 7b kickoff (Slab 7b inherits as input, does NOT block on them) — file in deferred-inventory under `slab-7a-trial-2-golden-trace-fixtures-deferred-to-slab-7b`.
- **PyYAML, NOT ruamel.**
- **No new third-party deps.**

## Verification battery (T10)

```bash
.venv/Scripts/python.exe -m pytest tests/parity/test_{mapping_checklist_row_NN,composition_spec_invariants,nfr_cg_block_aggregated}.py tests/integration/marcus/test_{calibration_tripwire,engagement_decay_report,marcus_duality_boundary}.py -q --tb=short
.venv/Scripts/python.exe -m pytest tests/unit/manifest tests/integration/marcus tests/composition tests/parity tests/structural tests/unit/marcus tests/specialists/texas tests/specialists/_scaffold tests/cli tests/unit/models -q --tb=line
.venv/Scripts/python.exe scripts/utilities/check_pipeline_manifest_lockstep.py
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7a-8-integration-parity-test-suite-slab-7a-closeout.md
.venv/Scripts/python.exe -m ruff check app/marcus/orchestrator/gate_runner.py tests/parity tests/integration/marcus
.venv/Scripts/lint-imports.exe
```

**Operator dual-gate ceremony (T10) — operator runs and pastes verbatim stdout:**
- Full battery as above + `webbrowser`-mediated trial-2 (or trial-2 dry-run) + paste close-artifact paths.

Expected: zero new failures; trial-2 (or dry-run) completes through G3 cleanly with all 11 specialists active per BS-2 readiness predicate.

## T11 + T12

T11: Codex G6 self-review (Blind / Edge / Auditor) at `_bmad-output/implementation-artifacts/7a-8-codex-self-review-2026-04-XX.md`. Flip story status to `review`. Hand to Claude.

T12: Claude does FINAL bmad-code-review + DUAL-GATE Gate-2 ceremony confirmation + remediation + commit + flips `migration-7a-8-integration-parity-test-suite-slab-7a-closeout` review → done. Claude also executes the closeout checklist per AC-7.8-J: sprint-status update; bmm-workflow-status.yaml update; next-session-start-here.md update; deferred-inventory.md updates; retrospective convened.

## Boundary

- HALT and surface on: (a) ANY of the 7 prior Slab 7a stories not `done`, (b) trial-2 readiness predicate BS-2 fails (any of A-1..A-7 not green), (c) Composition Spec §11 trigger fires (it shouldn't — additive parity tests + aggregating substrate; if it fires, that's a real substrate evolution beyond 7a.8 scope), (d) K-actual exceeds 1.7× target (~5.1K LOC OR ~44 active tests excluding skipped placeholders) — close round + party-mode triage, (e) calibration-tripwire fires on consensus path (false positive — broken implementation), (f) Marcus-duality boundary breached at runtime (orchestrator-mode state mixes with operator-handoff state), (g) any sandbox-AC violation.
- Do NOT touch specialist bodies or 7a.1-7a.7 surfaces (only consume).
- Do NOT introduce ruamel.yaml or new third-party deps.
- DUAL-GATE means operator MUST witness the Gate-2 ceremony; Codex prepares the battery + script; operator executes + pastes; Claude verifies + closes.
```
