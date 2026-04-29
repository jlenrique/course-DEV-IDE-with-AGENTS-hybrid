# Codex dev-story prompt — Story 7a.8 (integration + parity-test suite + Slab 7a closeout) — REFRESHED 2026-04-29

**Cycle:** Claude spec → Codex dev+tests → Claude bmad-code-review + commit + flip done.
**Wave:** 5 slot 2 — STRICT-LAST.
**Gate:** **DUAL-GATE** (operator-witnessed Gate-2 evidence ceremony required at T10/T11 boundary).
**Strict prereq:** ALL 7 prior Slab 7a stories CLOSED done as of 2026-04-29 (verified — see T1 below).

**This prompt supersedes any earlier 7a.8 prompt.** Refresh reflects current sprint-status with all 7 prior stories closed + the 7a.5 facade-module convention (`app.models.state.specialist_summary_artifacts`).

---

```
Run bmad-dev-story on Story 7a.8 (Slab 7a Wave 5 strict-last; DUAL-GATE; integration + 33-row parity-test suite + Composition Spec invariant test suite + calibration-tripwire + engagement-decay report + Marcus-duality boundary + NFR-CG block aggregated + Slab 7a CLOSEOUT).

## Required reading (read in order)

1. **Story spec:** `_bmad-output/implementation-artifacts/migration-7a-8-integration-parity-test-suite-slab-7a-closeout.md` (status: ready-for-dev; 12 ACs A-L; 12 tasks T1-T12; you own T1-T11)
2. **All 7 prior Slab 7a stories CLOSED done as of 2026-04-29:**
   - 7a.1 directive-composer (commit 05bb2aa)
   - 7a.2 manifest fold-flags + compiler ext (commit 70042fa)
   - 7a.6 vocabulary registry + parity-table (commit 70042fa)
   - 7a.3 pre-gate-marcus shared LLM node (commit 526fc95)
   - 7a.4 per-slide subgraph + HTML review-pack (commit 8929637)
   - 7a.7 A2 single-decision shims (commit 8472146; Claude developed directly)
   - 7a.5 conversation persistence + specialist-summary writer (commit 8e74028)
3. Prior code-review reports under `_bmad-output/implementation-artifacts/7a-{1,2,3,4,5,6,7}-code-review-2026-04-29.md` (PASS / PASS-WITH-PATCH outcomes; remediation cycles documented).
4. Mapping checklist (READ-ONLY; 33 rows per operator-ratified Option B amendment 2026-04-29): `_bmad-output/planning-artifacts/slab-7-legacy-migrated-mapping-checklist.md`
5. Composition Spec (all 7 §§ tested): `docs/dev-guide/composition-specification.md` §3.1, §3.5, §3.6, §6, §9, §10, §11
6. Governance JSON: `docs/dev-guide/migration-story-governance.json` story `7a-8` (DUAL-GATE; expected_pts=4; expected_k_target=1.6; rationale=`operator_acceptance_gate + invariant_preservation`)
7. PRD §Success Criteria A-1..A-7 (the 7 acceptance clauses for trial-2 readiness predicate BS-2)
8. PRD §NFR-CG1-CG11 (the closeout governance gate block)
9. CLAUDE.md §BMAD sprint governance + §Deferred-inventory governance (both apply at closeout)
10. Sandbox-AC inventory: `docs/dev-guide/migration-ac-sandbox-inventory.json`
11. **Slab 6.5 retrospective at `_bmad-output/implementation-artifacts/migration-6-5-hud-per-step-expandable-summaries.md`** (precedent for retrospective-shape reference)
12. **Slab 2a retrospective at `_bmad-output/implementation-artifacts/slab-2a-retrospective.md`** (closer precedent for slab-closing retrospective shape)

## T1 hard checkpoints (HALT-AND-SURFACE if violated)

- ALL 7 prior Slab 7a stories `done` in BOTH spec status + sprint-status.yaml. **Verified 2026-04-29.** No story may be in `review` or `in-progress`.
- 7a.6's `tests/parity/test_operator_control_parity.py` exists with 33 test functions (verified — `grep -c "^def test_row_"` returns 33; 19 are @pytest.mark.skip placeholders awaiting Slab 7a/7b activations per AC-7.6-D).
- 7a.4's `OperatorVerdict.revise_count` field exists (max-3 oscillation invariant; verified at `app/models/state/operator_verdict.py`).
- 7a.2's `production_gate_ids(manifest)` returns `{G1, G2C, G3, G4}` (4 active terminal gates).
- 7a.1/7a.5's `runs/<trial_id>/run_summary.yaml` shape exists (silent_bypass_events: 0 invariant from 7a.2; emit per `_emit_run_summary_yaml` in `app/marcus/orchestrator/production_runner.py`).
- 7a.5's specialist-summary writer facade at `app/marcus/orchestrator/specialist_summary_writer.py` + implementation at `app/models/state/specialist_summary_artifacts.py` (Codex's facade-module convention to satisfy M3 import contract).

## Files in scope

**New:**
- `tests/parity/test_mapping_checklist_row_NN.py` (or 33 individual files OR consolidated single file with 33 test functions per AC-7.8-A — your decision; mirror 7a.6's parity-suite shape since 7a.6 ALREADY scaffolded the 33 placeholders. **PREFERRED:** flesh out the existing 7a.6 placeholders rather than authoring a parallel suite. Keep `MAPPING_CHECKLIST_ROW = NN` + `REFERENCES_FRS = [...]` headers per row.)
- `tests/parity/test_composition_spec_invariants.py` per AC-7.8-B (one test function per § from the 7 sections {§3.1, §3.5, §3.6, §6, §9, §10, §11}).
- `tests/parity/test_nfr_cg_block_aggregated.py` per AC-7.8-H (11 cases; one per NFR-CG{1..11}).
- `tests/integration/marcus/test_calibration_tripwire.py` per AC-7.8-C.
- `tests/integration/marcus/test_engagement_decay_report.py` per AC-7.8-E.
- `tests/integration/marcus/test_marcus_duality_boundary.py` per AC-7.8-G.
- `_bmad-output/implementation-artifacts/slab-7a-retrospective.md` per AC-7.8-J (use `bmad-retrospective` skill OR mirror `slab-2a-retrospective.md` shape).
- `_bmad-output/implementation-artifacts/7a-8-codex-self-review-2026-04-29.md` (T11 deliverable).

**Modified:**
- `app/marcus/orchestrator/gate_runner.py` (extend or create — additive — for tripwire substrate + Marcus-duality runtime assertion). If `gate_runner.py` does not yet exist as a separate module, create it; otherwise extend.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` + `_bmad-output/implementation-artifacts/bmm-workflow-status.yaml` + `next-session-start-here.md` + `_bmad-output/planning-artifacts/deferred-inventory.md` per AC-7.8-J close protocol — Claude T12 owns these flips; you may DRAFT the proposed content in your self-review.

**Do NOT modify:**
- specialist bodies (substrate-isolation invariant N4 per Slab 7a-wide convention).
- 7a.1-7a.7 surfaces (only consume; the 7 prior stories' interfaces are stable).
- `state/config/pipeline-manifest.yaml` (no manifest changes in 7a.8 scope).
- `scripts/utilities/check_pipeline_manifest_lockstep.py` (no lockstep changes).
- v4.2 prompt pack.

## Critical implementation notes

- **DUAL-GATE — operator-witnessed Gate-2 evidence ceremony at T10:** operator runs the full focused + wider regression battery + sandbox-AC + lockstep + ruff + lint-imports + Composition Smoke (all 4: 7a.1 slab-opener + 7a.7 A2-shims + per-7a.4 HTML pack + per-7a.5 chain integrity) + trial-2 (or trial-2 dry-run). Codex prepares the evidence-collection script + runs everything achievable headlessly; operator runs the trial-2 portion + pastes verbatim stdout into Completion Notes.

- **33-row parity-test suite (AC-7.8-A):** the existing 7a.6 scaffold at `tests/parity/test_operator_control_parity.py` has 33 test functions; 19 are `@pytest.mark.skip` placeholders. Your job is NOT to author a parallel suite — instead, EITHER (a) flesh out the existing 19 placeholders by removing skip + implementing per-row assertions per the 33 mapping-checklist rows, OR (b) author a parallel `test_mapping_checklist_row_NN.py` family (one file per row) with `MAPPING_CHECKLIST_ROW` + `REFERENCES_FRS` headers. **Prefer option (a)** for tightness; only fall back to option (b) if the placeholder shape can't accommodate REFERENCES_FRS headers cleanly. Surface the choice at T1 (no decision_needed; proceed with your preferred shape and document in self-review).

- **Composition Spec invariant test suite (AC-7.8-B):** one test function per §; covers §3.1 (envelope append-only + SHA256), §3.5 (gate precedence non-blocking), §3.6 (manifest-declared dependencies), §6 (chain-test-per-PR), §9 (Composition Smoke gate at slab-opener), §10 (Decision Log entries present for substrate-shape evolutions — the 2026-04-29 entry for `runner_supplied_payload` from 7a.1 is the canonical example), §11 (migration triggers tracked).

- **Calibration-tripwire substrate (AC-7.8-C):** wire into `app/marcus/orchestrator/gate_runner.py` (extend or create). Rolling N-run window over operator-override-rate; auto-lock at affected gate for next 3 trials; log fire AND quiet events at `_artifacts/trial-2/calibration_tripwire_log.jsonl`. **FM-5 inverse: silence is NOT assumed healthy; quiet must be witnessed.**

- **Synthetic-disagreement injection fixture:** ≥3-axis disagreement triggers tripwire; consensus stays quiet; ≥1 fire + ≥1 quiet captured.

- **Engagement-decay report (AC-7.8-E):** auto-emit `_artifacts/trial-2/engagement_decay_report.md` at trial close; SM-4 threshold (last-quartile ratio ≥ 0.30 × first-quartile) breach triggers C1 calibration-tripwire.

- **Marcus-duality boundary (AC-7.8-G):** runtime-asserted boundary in dispatch adapter — orchestrator-mode state never mixes with operator-handoff state. Reviewer (Claude) confirms in code-review.

- **NFR-CG block aggregated test (AC-7.8-H):** 11 cases (one per NFR-CG); each asserts the relevant artifact exists + meets the criterion. Mirror the structural-test pattern from 7a.6's parity-table-row-count + 7a.5's chain-integrity tests.

- **Slab 7a retrospective (AC-7.8-J):** author at `_bmad-output/implementation-artifacts/slab-7a-retrospective.md`. Mirror `_bmad-output/implementation-artifacts/slab-2a-retrospective.md` shape. Cover: NEW CYCLE proven (Claude spec → Codex dev → Claude review) over 6 stories; SG-2 floor amendment 34→33; Codex's facade-module fix for M3 contract violation in 7a.5; cycle pattern lessons (PATCH-cycle frequencies; halt-and-adapt patterns; deferred-inventory growth). Per CLAUDE.md §Deferred-inventory governance #2, the retrospective MUST review `deferred-inventory.md` against Slab 7a's new substrate/evidence/learnings; flag now-ready-to-reactivate entries to next sprint planning.

- **Golden-trace fixtures (AC-7.8-K):** if trial-2 has run by 7a.8 close, commit fixtures under `_bmad-output/trial-fixtures/<trial-2-id>/`. If NOT (likely the operator hasn't run trial-2 yet — substrate is just now complete), defer to Slab 7b kickoff. File deferred-inventory entry `slab-7a-trial-2-golden-trace-fixtures-deferred-to-slab-7b`.

- **PyYAML, NOT ruamel** (per 7a.1 finding).
- **No new third-party deps.**

## Verification battery (T10 — Codex prepares; operator runs Gate-2 ceremony)

```bash
# Focused 7a.8 slice
.venv/Scripts/python.exe -m pytest tests/parity/test_mapping_checklist_row_NN.py tests/parity/test_composition_spec_invariants.py tests/parity/test_nfr_cg_block_aggregated.py tests/integration/marcus/test_calibration_tripwire.py tests/integration/marcus/test_engagement_decay_report.py tests/integration/marcus/test_marcus_duality_boundary.py -q --tb=short

# Wider regression slice (post-Slab-7a; ALL 7 prior closed)
.venv/Scripts/python.exe -m pytest tests/unit/manifest tests/integration/marcus tests/composition tests/parity tests/structural tests/unit/marcus tests/specialists/texas tests/specialists/_scaffold tests/cli tests/unit/models -q --tb=line

# Substrate gates
.venv/Scripts/python.exe scripts/utilities/check_pipeline_manifest_lockstep.py
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7a-8-integration-parity-test-suite-slab-7a-closeout.md

# Code quality
.venv/Scripts/python.exe -m ruff check app/marcus/orchestrator/gate_runner.py tests/parity tests/integration/marcus
.venv/Scripts/lint-imports.exe

# All 4 Composition Smokes (7a.1 slab-opener + 7a.7 A2-shims; verify both still PASS)
.venv/Scripts/python.exe _bmad-output/implementation-artifacts/migration-7-1-directive-composer-composition-smoke.py
.venv/Scripts/python.exe _bmad-output/implementation-artifacts/migration-7-7-a2-shims-composition-smoke.py
```

**Operator-witnessed Gate-2 ceremony (T10):**
- Operator runs full battery above + trial-2 (or trial-2 dry-run with `--allow-offline-cost-report`); pastes verbatim stdout.
- Operator confirms BS-2 readiness predicate (A-1..A-7 from PRD §Success Criteria green).
- Operator confirms `silent_bypass_events: 0` in trial run_summary.yaml.

Expected: zero new failures vs the post-7a.5-close baseline (667 passed/20 skipped on the wider slice as of 2026-04-29 8e74028 commit).

## T11 + T12

T11: Codex G6 self-review (Blind / Edge / Auditor) at `_bmad-output/implementation-artifacts/7a-8-codex-self-review-2026-04-29.md`. Flip story status to `review`. Hand to Claude with paths to your developed code + self-review + (when present) operator's pasted Gate-2 evidence.

T12 (Claude-owned closeout):
- Final bmad-code-review + DUAL-GATE Gate-2 ceremony confirmation + remediation cycles if needed.
- Commit.
- Flip `migration-7a-8-integration-parity-test-suite-slab-7a-closeout` review → done in sprint-status.yaml.
- Execute the closeout checklist per AC-7.8-J:
  - sprint-status.yaml: Slab 7a stories all closed; Slab 7b queued.
  - bmm-workflow-status.yaml: Slab 7a PRD entry done; Slab 7a epic entry done.
  - next-session-start-here.md: immediate-next-action = Slab 7b PRD authoring OR trial-2 dry-run.
  - deferred-inventory.md: file Slab 7a-named follow-ons (Doc-7-D harvest items; structural polish-pass deferrals; sanctum-reference-conventions verification; trial-2 golden-trace fixtures if not yet captured).
- Convene retrospective (Codex authored draft; Claude refines + party-mode-style sign-off if operator wants).

## Boundary

- HALT and surface to operator on: (a) ANY of the 7 prior Slab 7a stories not `done` (verify at T1; all are done as of 2026-04-29), (b) trial-2 readiness predicate BS-2 fails (any of A-1..A-7 not green) — only diagnoseable when operator runs trial-2, so report at T10 ceremony, (c) Composition Spec §11 trigger fires (it shouldn't — additive parity tests + aggregating substrate; if it fires, that's a real substrate evolution beyond 7a.8 scope), (d) K-actual exceeds 1.7× target (~5.1K LOC OR ~44 active tests excluding skipped placeholders) — close round + party-mode triage, (e) calibration-tripwire fires on consensus path (false positive — broken implementation), (f) Marcus-duality boundary breached at runtime (orchestrator-mode state mixes with operator-handoff state), (g) any sandbox-AC violation.
- Do NOT touch specialist bodies or 7a.1-7a.7 surfaces (only consume).
- Do NOT introduce ruamel.yaml or new third-party deps.
- DUAL-GATE means operator MUST witness the Gate-2 ceremony; Codex prepares the battery + script; operator executes + pastes; Claude verifies + closes.
- 7a.8 is the SLAB 7A CLOSING STORY — extra care on closeout artifacts (retrospective convening; deferred-inventory consolidation; sprint-status hygiene). Mirror Slab 2a's closing-story discipline (`migration-2a-4-migrate-texas-to-9-node-scaffold.md` + `slab-2a-retrospective.md` precedent).
```
