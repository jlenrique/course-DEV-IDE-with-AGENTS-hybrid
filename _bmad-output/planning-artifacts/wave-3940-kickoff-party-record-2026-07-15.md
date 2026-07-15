# Epics-39/40 Wave Kickoff — Party Record (2026-07-15)

**Round:** Winston / John / Amelia / Murat — **unanimous APPROVE-WITH-AMENDMENTS on all three decisions**; orchestrator concurred; operator (Juanl) pre-approved the agenda and the governing directive ("optimize paid run cycles — but not leave ourselves open to the believed-green gotchas"). Per CLAUDE.md party-consensus-=-approval, decisions are binding for the wave.

---

## D1 — RATIFIED: Story 38.2 re-homed into the Epic-39 wave; Epic 38 CLOSED

Ordering-conformance, not scope-drop: the ratified build-order DAG already sequences 38.2 (`… 37.2b → 39.1 → 38.2 → 39.2 → 40.1`) adjacent to its sole consumer (39.2 Door-Ajar). Amendments folded:

- **Key stays verbatim** `38-2-ask-b-hot-topics-wiring` — never renumbered (cross-referenced in the DAG, retro, closure record, inventory). Re-home = move under the Epic-39 wave grouping with a note (John F1 / Amelia F1).
- **FR re-point pinned (Murat M-D1-1):** FR16's Ask-B leg + FR9 travel with 38.2 and are asserted at the **Epic-39-wave close bar**. Epic 38's close claim = "Ask-A + graph reorder delivered; Ask-B re-homed" — never "FR16 fully delivered."
- **Contracts travel with specialist/node identity (Murat M-D1-2, Winston D1-1):** 38.2's story spec MUST cite at T1: the ratified Epic-38 graph-shape record (`ask_b_hot_topics`, node `07W.4`, own witnessed digest, 39.2 sole consumer), Tier-2 lockstep + regime doc, and 38.2's original ACs (separate late Tracy call; `reject_model_prior_topic`; empty-honesty). These key on specialist_id + node id, not the story number.
- **Single coherence batch (Winston D1-2, John F2):** sprint-status move + epic flip · FR-coverage-map annotation in the epics doc · one-line cross-ref on the Epic-38 retro · deferred-inventory note. Executed with this record.

## D2 — RATIFIED: MERGE for overlay-exercise composition (replaces REPLACE)

Both exercise families are different authorities with different pedagogical jobs (Irene bespoke practice vs authentic course-check instruments); the trial pair proved REPLACE forces a false choice. Design, all amendments folded:

1. **Seam:** the attach loop in `app/specialists/workbook_producer/_act.py` (~L863-874) — collateral exercises first, overlay appended. `project_enrichment_to_workbook_inputs` stays a pure single-source projector (Winston D2-1, Amelia).
2. **Provenance is a field, not a position:** explicit `origin: Literal["collateral","enrichment"]` on the exercise model (back-compat default); the renderer groups per unit as **"Practice" (collateral) → "Course Check — drawn from this course's own assessments" (overlay)**; the Answer Key carries the same labels (Winston D2-1, John F2).
3. **Collision guard:** overlay exercise ids prefixed (`g0-<component_id>`) at attach; any residual cross-source `exercise_id` collision fails loud via `assert_unique_collateral_ids` — never silent-dropped (Amelia A1, Winston D2-2).
4. **Dedup synthesis (John F1 × Murat M-D2 determinism bar):** NO machine semantic dedup (non-deterministic — rejected). Learner-visible duplication is handled at **authoring time**: Irene's collateral authoring (37-2b/39-wave stories) receives the overlay's covered-LO/fact list as INPUT and flexes around it; the residual is an **operator spot-check at the checkpoint governed run** (declared honestly, not claimed machine-caught). John's concrete duplicate pairs (admin-cost %, 73-day doubling, digital front door) seed the authoring-flex AC.
5. **Cap + loss visibility:** target total ≤12 per workbook, per-unit collateral cap 2, overlay items never trimmed; ANY dropped/trimmed collateral recorded in a visible `exercise_overlay_loss` structure (mirror of `lo_overlay_loss`) — never silent (John F2, Murat).
6. **Five deterministic floors as I/O-matrix rows before dev opens (Murat M-D2-1):** collision identity · total ordering (unit → provenance class → stable id) · cap + visible truncation loss · provenance labels · answer-key mapping under mixed keyed/unkeyed exercises. Plus: extend the real-run replay probe to `runs/8b275e5b…` pinning the chosen composition (M-D2-2); existing 47 bridge/normalization pins re-run.
7. **Hard precondition:** the answer-leak strip (`_project_exercises` must never emit `Correct Answer:` in prompts; `answer_keys` is the channel) lands FIRST or in the same story, with a no-answer-in-prompt pin (all seats).

Implementation home: the 39-wave story that owns exercise rendering (39.1 grooming encodes these as ACs); blast radius ~1 source file + ~5 test-expectation flips + 1 new module (Amelia).

## D3 — RATIFIED: Paid-Run Economy Protocol (binding for the wave)

Six planks + seven amendments. **Rationale: variance discipline, not cost-saving — the scarce resource is signal per run** (John).

**Planks:** (1) witness-replay pre-flight before every paid run; (2) live-shape fixtures only for consume-side tests; (3) component live probes as each new LLM surface lands — governed runs are batch confirmation, never first contact; (4) batched governed runs at DAG checkpoints (after 37-2b+39-1 · after 38-2+39-2+40-1 · off-frozen-lesson re-proof finale = full-DAG E2E); (5) machine-asserted deliverable bars extended **in the same story diff** that adds a section (Winston D3-2 — per-story DoD, never "next touch"); (6) variance-first LLM seam design (digest-bound joins; observable normalization of provably-empty shapes only; fail-loud ambiguity).

**Amendments:**
- **Zero-witness rule (Winston D3-1):** a new/changed LLM path with no frozen witness cannot claim replay-green — sequence is **probe → freeze (probe output becomes the path's first witness fixture) → replay → spend**.
- **Standing replay suite (Murat M-D3-1a, Amelia a):** `tests/live_witness_replay/` with a `witnesses.yaml` registry (auto-enrolling; one-line adds) and per-artifact-family modules (Pass-1 raw responses; G0 cards; authority maps; Ask journals — Ask-B family added when 38.2 lands). Enrollment is automatic, not remembered.
- **Skip ≠ green (Amelia F1, binding):** `runs/` is gitignored — the pre-flight runs in STRICT mode (`WITNESS_REPLAY_STRICT=1`: skip ⇒ fail) and the pre-run authorization records "replay GREEN, N witnesses, 0 skipped."
- **Drift flags (Murat M-D3-1b):** the pre-flight report carries prompt-text digest + model id + config identity vs each witness's capture-time values (generalize `preflight-input-identity.v1`), with an explicit "confidence downgraded — corpus predates prompt/model change" line on mismatch. Live-shape fixtures digest-bind to their `schema_version` with a bump tripwire.
- **Probe honesty contract (Murat M-D3-2a):** a probe is registered BEFORE it runs (probe id + the exact claim it licenses + deterministic machine judge + frozen evidence pack with input digests and raw outputs) and is first-run-stands. A probe green licenses only its declared claim — never "the pipeline works."
- **Bars carry negative-witness pins (Murat M-D3-2b):** every machine-asserted bar (incl. `_assert_completed_workbook_deliverable` + its M-R3 fold) is fed known-bad artifacts from the frozen negative witnesses and must REJECT; bar modules get Blind+Edge review on change. M-R3 asserts the **structured** `lo_overlay_loss` record off run.json, not rendered-prose grep (Amelia F2).
- **Batch attribution (Murat M-D3-3, John F1):** each batched run's evidence pack carries **per-story verdict lines** keyed to the node/gate each story claims — REACHED+PASS = witness; NOT-REACHED = claim stays OPEN (no-evidence, never pass, never fail); "aboard" ≠ tested. Boarding rule: only fixes independently greened offline may join a batch. No story crosses two batch boundaries unwitnessed — pull the run forward if it would.
- **Status vocabulary (John F2):** `done-awaiting-live-witness  # deterministic+review green; component probe <id> green; full-run witness owed by batch run <N>` — flip to `done` cites the witnessing run id. Never overload `in-progress`; never early-`done`.

**Wave run plan:** component probes continuously (37-2b writer probe via the `run_deep_dive_38_3a_live_evidence.py` clone; Ask-B probe via a new `run_ask_b_38_2_live_evidence.py`) → governed run A after 37-2b+39-1 → governed run B after 38-2+39-2+40-1 → off-frozen-lesson re-proof (`tejal-c1m1-p3-opportunity`) as the finale certifying the FINISHED product. First-run-stands throughout.

---

**Immediate execution order (operator-approved):** (i) this record + D1 coherence batch ✅ · (ii) master consolidation · (iii) answer-leak strip (fresh dev agent; party authority = this record §D2.7) · (iv) 37-2b story authoring + dispatch under the protocol.
