---
baseline_commit: e40a893a
---

# Story Q3.4: Calibration dimension — REPORT-ONLY

Status: ready-for-dev

<!-- Epic Q3 (Partial + report-only siblings). DISPATCH #4 (LAST of Q3 — closing this closes Epic Q3 + the whole Project Quality Scorecard, all 8 dimensions). Source epic: epics-project-quality-scorecard-2026-07-19.md. Follows the Q1 engine + ALL sibling learnings. ⚠️ REPORT-ONLY + the phasing flag: this dimension REPORTS the calibration posture; it does NOT build the fresh-holdout harness (that stays the separate owed epic reading-path-fresh-naive-holdout-pre-trial = DID Leak-4). -->

## Story

As **the project quality scorecard**,
I want **a Calibration dimension that HONESTLY REPORTS the calibration posture of the project's intelligent necks — surfacing "fresh naive holdout OWED / unmeasured" for the reading-path and the single pinned resubstitution metric+dataset+commit**,
so that **the operator sees an honest read of what is calibrated vs owed — and an owed/unmeasured neck is scored as UNCALIBRATED, never as passing, and the dimension NEVER implies a fresh-holdout number was measured when it was not.**

## Scope fence (read FIRST)

Q3.4 adds ONE new dimension (`calibration`). It is **REPORT-ONLY**. It does **NOT**:

- **Touch the prior 7 dims** (all done) — read-only.
- **⛔ Build the fresh-naive-holdout harness / measure a fresh number.** That is the separate owed epic `reading-path-fresh-naive-holdout-pre-trial` (DID Leak-4). Q3.4 REPORTS the OWED posture; it does not build it, does not run a live measurement, does not fabricate a fresh number.
- **Double-count DID Leak-4.** The reading-path calibration OWED is DID Leak-4's home; Q3.4 cross-links it (distinct slug/namespace), NOT a second count of the same substrate (the Q2.3-fidelity / Q3.1-capability cross-link precedent).
- **Add module-scope `app.*` to `app/quality`** (GL-3); **wire into production_runner** (E2E rides R2, GL-10).
- Extend the Q1 machinery **only additively**.

## Honest baseline (verified — from Q1.5 + the deferred entry; do NOT re-derive)

- **Reading-path is UNCALIBRATED.** Per `reading-path-fresh-naive-holdout-pre-trial` (DID Leak-4) + `p2-4b-honest-measurement-and-recalibration-2026-06-23.md`: the ONLY measured number is the **built-classifier RESUBSTITUTION** — `subject=built-classifier(S1/S2/S3), substrate=fresh@2026-06-23: primary-key 0.071 (1/14)` — on the CONSUMED-14 held-out (now a non-naive dev set → resubstitution/upper-bound only). The `0.93` was catalog-approach (Claude-labels), NOT the built classifier. The **fresh NAIVE holdout is OWED / UNMEASURED**; a fresh naive number has NOT been measured, and NONE may be implied (Mary, binding — firm dissent against claiming trial-ready off the consumed-14).
- **Mary's metric-citation rule (binding):** every reading-path accuracy number carries `(subject=built-classifier|catalog-approach, substrate=fresh|stale@date)`.
- So the calibration posture for the reading-path neck = **UNCALIBRATED (fresh naive holdout OWED)** → scored as uncalibrated, NOT passing.

## Acceptance Criteria

**AC1 — New `## Dimension 8 — Calibration (report-only)` section + machine-block entry**, mirroring the prior dimensions (why-load-bearing → rubric → assessment table → ranked leaks → cadence). Machine block gains a `calibration` dimension with the full field-set. Band+leaks+trend. The §Cadence + band_note state this dimension is REPORT-ONLY (it does not build the holdout harness).

**AC2 — Signal reader (fail-soft, read-only, clean-leaf) that reports the OWED posture honestly:**
- **CAL1 reading-path calibration posture (SIGNAL-DERIVED, the owed/uncalibrated read):** a reader that reports whether a fresh-naive-holdout MEASUREMENT exists for the reading-path neck. Honest today: it does NOT (the artifact/harness is owed) → **uncalibrated → weak** (an owed/unmeasured neck scored as uncalibrated, NOT passing). The reader surfaces the single pinned resubstitution fact (`subject=built-classifier, substrate=fresh@2026-06-23, primary-key 0.071`, dataset=consumed-14, report=`honest-built-classifier-measurement.json`) as EVIDENCE of what WAS run — clearly labeled resubstitution/upper-bound, never as generalization. Consult the REAL owed state (does the fresh-holdout artifact exist?), not mere presence of a resubstitution number; nothing-checkable → unavailable, never "calibrated".
- **Report-only:** the reader does NOT run any measurement; it reads the recorded posture (the deferred entry / the report metadata). Do NOT let a resubstitution/unverified number award a "calibrated" level (the anti-believed-green invariant — resubstitution ≠ calibrated).

**AC3 — The dimension's own honesty pin (GL-6 meta-ratchet REQUIRES it) + the "never imply measured" pin (the epic's signature pin).** Register a `calibration` pin in `_HONESTY_PIN_REGISTRY` + add `calibration` to `_EXPECTED_CANONICAL_DIMENSION_KEYS` + CAL1 to `_SIGNAL_DERIVED_READERS`. Two pins:
- **(a) never-imply-measured pin (the epic AC)** — the dimension's prose + machine block + signal MUST NEVER imply a fresh-naive holdout number was measured (assert the calibration text carries the OWED/unmeasured framing + Mary's `(subject, substrate@date)` citation on every reading-path number, and NEVER a bare fresh-naive figure). RED-under-seeded: seed the prose to imply a fresh number ("fresh-holdout accuracy: 0.93") → RED.
- **(b) uncalibrated-not-passing pin** — the CAL1 level FAILS if it claims "calibrated"/clean while the fresh holdout is owed (a resubstitution number can never award a calibrated level). RED-under-seeded (GL-9) + the isolating pin (Q2.3 FT2 — consult the real owed-state, not the presence of a resubstitution number).

**AC4 — GL-13 leak registration + DID-Leak-4 cross-link (NO double-count).** Register the reading-path calibration OWED as a `calibration` leak (an EIGHTH `## Calibration Scorecard Leak Registry` / `cal_leak:` namespace, disjoint from the other seven). `cross-link DID Leak-4` (`reading-path-fresh-naive-holdout-pre-trial`) — same substrate, distinct slug/namespace, NOT double-counted (the Q2.3/Q3.1 cross-link precedent). `len(leaks) == open_leaks == 1` (lane learner-trust — calibration = trust in the neck's measured quality). reconcile-by-identity; `ranked_project_leaks` aggregates all 8 dims; `leak_coverage_gaps` clean.

**AC5 — Mirror + trend + history.** Append a `calibration` snapshot to `scorecard-history.jsonl` (mirror pin); trend baseline; projector NO code change. **THIS CLOSES THE SCORECARD** — the 8th and final dimension; confirm the projector renders all 8 cleanly.

**AC6 — Tests (hermetic + real) + honest Band + the never-imply-measured proof.** CAL1 against the real recorded posture (uncalibrated/owed → weak) AND a fixture where a fresh-holdout measurement exists (→ can improve — the close-path); the never-imply-measured pin RED-under-seeded (seed a fresh number → red); the uncalibrated-not-passing pin + isolating pin; meta-ratchet green; mirror/arithmetic/leak-identity (8 namespaces)/coverage all green. **Band honesty:** the band_note states this is REPORT-ONLY, the reading-path is uncalibrated (fresh holdout OWED), and cites the resubstitution number with Mary's `(subject, substrate@date)` — never a fresh-naive number. **E2E:** deferred to R2 (GL-10 — file the obligation). Prior 7 dims pins + numbers unchanged.

## Tasks / Subtasks
- [x] **T1 — Readiness.** Re-read the scope fence (⛔ REPORT-ONLY, do NOT build the harness / measure) + honest baseline + Mary's metric-citation rule + ALL sibling review learnings (consult-real-state/nothing-checked→unavailable; isolating pin; never-imply-measured wording; band honesty; the coverage-unverified/OWED-as-leak precedent from Q3.3/DID-Leak-4) + the 4 Q2-retro action items. Confirm no pipeline-lockstep trigger path edited.
- [x] **T2 — CAL1 reader** (AC2): report the reading-path OWED posture (fresh-holdout artifact absent → uncalibrated) + surface the resubstitution fact as labeled evidence; report-only, no measurement; fail-soft; clean leaf.
- [x] **T3 — Rubric + assessment + machine block** (AC1); uncalibrated=weak; the resubstitution-vs-fresh-holdout framing; report-only note.
- [x] **T4 — Honesty pins + registry** (AC3): the never-imply-measured pin + the uncalibrated-not-passing pin; RED-under-seeded both.
- [x] **T5 — GL-13 leaks + cal_leak registry (8th namespace) + DID-Leak-4 cross-link (no double-count)** (AC4).
- [x] **T6 — History mirror** (AC5) + honest band_note. Confirm all 8 dimensions render.
- [x] **T7 — Tests + R2 obligation** (AC6).
- [x] **T8 — Verify.** `pytest tests/quality/ -q`; ruff; import-linter 18/0; clean-leaf green; prior 7 dims unchanged; ALL prior pins green.

## Dev Notes

### Verified calibration seams (from Q1.5 + the deferred entry — report-only)
- `deferred-inventory.md` `reading-path-fresh-naive-holdout-pre-trial` (DID Leak-4) — the OWED entry + the resubstitution evidence.
- `p2-4b-honest-measurement-and-recalibration-2026-06-23.md` + `honest-built-classifier-measurement.json` — the single pinned resubstitution metric (0.071 primary-key, built-classifier, fresh@2026-06-23, consumed-14).
- The DID §1.6 C5 + Leak-4 prose (Q1.5) already carry the honest framing — mirror its wording; do NOT contradict it.
- Read the recorded posture as plain data / the deferred entry text — NO measurement, NO live run.

### The "never imply measured" pin is the signature honesty guard
This dimension exists to REPORT calibration honesty; its own pin must ensure it never fabricates the very thing it reports as owed. The pin asserts the OWED framing + Mary's `(subject, substrate@date)` citation, and reds if any prose implies a fresh-naive number was measured. This is the Q1.5 reading-path discipline, now a dimension-level pin.

### DID-Leak-4 cross-link, NO double-count (the established precedent)
Q2.3 (fidelity FT1) cross-linked DID Leak-2; Q3.1 (capability CH1) cross-linked DID Leak-5 — distinct slug + distinct namespace, counted once each. Q3.4 does the same for DID Leak-4: the `cal_leak:` reading-path-calibration-OWED entry cross-links `reading-path-fresh-naive-holdout-pre-trial` (did_leak) — same substrate, distinct slug/namespace, no double-count. Verify the 8-namespace disjointness + no cross-count.

### Sibling learnings + the 4 Q2 action items + Q3.1/Q3.2/Q3.3 learnings (BINDING)
consult-real-state (not presence of a resubstitution number); nothing-checked→unavailable; isolating pin; resubstitution≠calibrated (over-claim-clean); band honesty; OWED-as-leak (Q3.3/DID-Leak-4); GL-13 registration; reconcile-by-identity (8 namespaces); GL-9 RED-under-seeded; R2 witness. Equal-weight kept.

### This closes the scorecard
Q3.4 is the 8th and final dimension. After it lands, the Project Quality Scorecard is complete: DID + 3 Q2 ready-siblings + 4 Q3 partial/report-only. Confirm the projector renders all 8 + the honest cross-dimensional ranked-leak list.

### References
- [Source: epics-project-quality-scorecard-2026-07-19.md#Story Q3.4] + [#GL-13 / GL-15 / GL-6 / GL-9 / GL-10 + the report-only phasing] + FR13.
- [Source: deferred-inventory.md `reading-path-fresh-naive-holdout-pre-trial` (DID Leak-4) · p2-4b-honest-measurement-2026-06-23.md] — the OWED posture + resubstitution evidence.
- [Source: docs/quality/project-quality-scorecard.md §1.6 C5 + Leak-4 (Q1.5 framing) + the prior 7 dimensions] — the exemplars + the honest reading-path wording to mirror.
- [Source: q1-5 (DID reauthor, the reading-path discipline) + q2.3/q3.1 (cross-link precedent) + q3.3 (OWED-as-leak) stories] — the learnings.
- [Source: app/quality/{signals,scorecard,history,report}.py · tests/quality/test_scorecard_honesty_pins.py] — the engine + registry to extend.

## Dev Agent Record

### Agent Model Used

Claude Opus 4.8 (1M context) — fresh BMAD dev agent, `bmad-dev-story` workflow, RED-first discipline.

### Debug Log References

- Full quality suite: `pytest tests/quality/ -q` → **504 passed** (was 496+8-updated-siblings).
- Calibration + meta-ratchet pins (verbose): **21 passed** — incl. the never-imply-measured RED-under-seeded proof, the uncalibrated-not-passing RED proof, the isolating pin, the 8-namespace disjointness, the meta-ratchet.
- Ruff: `ruff check app/quality/ tests/quality/` → **All checks passed!**
- Import-linter: `importlinter.api` `create_report` → **kept 18 / broken 0** (LD1 unchanged; clean-leaf test green in-suite).

### Completion Notes List

**CAL1 reader (`app/quality/signals.py::reading_path_calibration_signal`)** — REPORT-ONLY, clean leaf (NO `app.*` import). Reads the RECORDED posture (`_READING_PATH_CALIBRATION_POSTURE` — a curated module constant, mirroring the capability curated-evidence pattern) and reports whether a fresh-naive-holdout MEASUREMENT exists. Today it does NOT (`fresh_naive_holdout_measured=False` — OWED) → `reading_path_calibrated=False` → uncalibrated → **weak**. Consults the REAL owed-state, NOT the presence of a resubstitution number (`resubstitution ≠ calibrated`). Surfaces the single pinned resubstitution fact (`subject=built-classifier(S1/S2/S3)`, `substrate=fresh@2026-06-23`, primary-key `0.071` (1/14), `dataset=consumed-14`, `report=honest-built-classifier-measurement.json`, `measurement_kind='resubstitution/upper-bound'`, `is_generalization=False`) as LABELED evidence — never a generalization, never a fresh-naive number. Fail-soft: non-mapping posture / missing-or-non-bool owed-state (nothing-checkable) → `unavailable`, never calibrated. `_level_cal_reading_path`: calibrated→strong, uncalibrated→weak, else unavailable. Close-path reachable (report-only) via the injectable `posture` arg.

**Rubric / assessment / machine block (`docs/quality/project-quality-scorecard.md` §Dimension 8 + `calibration:` machine block)** — single signal-derived criterion CAL1; score 1/4 = 25 → **Band D** (honest: reading-path uncalibrated). `band_note` states REPORT-ONLY + reading-path uncalibrated (fresh holdout OWED) + cites the resubstitution number with Mary's `(subject, substrate@date)`, never a fresh-naive number. Equal-weight kept. Band ceiling B disclosed.

**Honesty pins (`tests/quality/test_scorecard_honesty_pins.py`)** — `calibration` registered in `_EXPECTED_CANONICAL_DIMENSION_KEYS` (scorecard.py), CAL1 in `_SIGNAL_DERIVED_READERS`, and 5 pins in `_HONESTY_PIN_REGISTRY[_CALIBRATION_KEY]`: (a) uncalibrated-not-passing (the epic's exact pin — claim calibrated while owed → RED), (a') isolating (hold resubstitution present, vary owed-state → owed stays weak, measured→strong, proving it consults owed-state not the resub number), (a'') **never-imply-measured** (the signature — asserts OWED framing + Mary's citation + NO fresh-holdout figure; seed `fresh-holdout accuracy: 0.93` → RED via `_FRESH_NAIVE_NUMBER_RE`), (b) leak-count + slug identity, (c) arithmetic. Meta-ratchet (GL-6) now covers calibration; all prior pins green.

**GL-13 leak + cross-link (`_bmad-output/planning-artifacts/deferred-inventory.md`)** — new `## Calibration Scorecard Leak Registry` (EIGHTH `cal_leak:` namespace) with `cal_leak: calibration-reading-path-fresh-naive-holdout-owed`, lane learner-trust. CROSS-LINKS **DID Leak-4** (`did_leak: reading-path-fresh-naive-holdout-pre-trial`, already tagged in the DID registry) — same substrate, distinct slug/namespace, counted ONCE per namespace (no double-count). `len(leaks)==open_leaks==calibration_leak_count_signal()==1`. Eight-namespace disjointness proven (`test_eight_leak_namespaces_are_disjoint_and_dont_cross_count`).

**Mirror + history + projector (`docs/quality/scorecard-history.jsonl`)** — appended the `calibration` snapshot (score 25, band D, `{reading_path_calibration_posture: 1}`, open_leaks 1); mirror pin green; trend baseline. **Projector NO code change** — `render_scorecard_final_report` renders all 8 dimensions cleanly; cross-dimensional ranked-leak total now **13** (was 12). This CLOSES the 8-dimension Project Quality Scorecard.

**R2 witness + owed-epic obligations filed** to `deferred-work.md` (`q3-4-r2-calibration-witness` + the owed-epic `reading-path-fresh-naive-holdout-pre-trial`).

**Scope fence honored:** REPORT-ONLY — no harness built, no measurement run, no fresh number fabricated; prior 7 dims untouched (read-only; their numbers/pins unchanged — the 8 updated sibling assertions are cross-dimensional aggregate totals + the canonical-keys tuple, which legitimately grow with the 8th dimension, exactly as each prior story updated them); no `production_runner` edit; no pipeline-lockstep trigger path touched; Q1 machinery extended additively only.

**Honesty judgment call:** made CAL1 single-criterion (mirroring lane_discipline) with the level keyed purely on `fresh_naive_holdout_measured` (the owed-state) — the resubstitution number never influences the level. This keeps "resubstitution ≠ calibrated" mechanical, not merely documented.

Status left `ready-for-dev` and NOT committed, per the launching agent's explicit instruction (overrides the workflow's Step-9 `review` transition).

### File List

- `app/quality/signals.py` (M) — CAL1 reader `reading_path_calibration_signal` + `calibration_leak_count_signal` + `_level_cal_reading_path` + `level_from_signal` wiring + `_CALIBRATION_LEAK_LINE_RE` / `_CALIBRATION_SRC` / `_READING_PATH_RESUBSTITUTION` / `_READING_PATH_CALIBRATION_POSTURE`.
- `app/quality/scorecard.py` (M) — `_CALIBRATION_KEY` + added to `_EXPECTED_CANONICAL_DIMENSION_KEYS`.
- `docs/quality/project-quality-scorecard.md` (M) — §Dimension 8 prose + `calibration:` machine-block entry.
- `docs/quality/scorecard-history.jsonl` (M) — appended the `calibration` snapshot.
- `_bmad-output/planning-artifacts/deferred-inventory.md` (M) — new `## Calibration Scorecard Leak Registry` (cal_leak, cross-links DID Leak-4).
- `_bmad-output/implementation-artifacts/deferred-work.md` (M) — Q3.4 owed-epic + R2 witness obligations.
- `tests/quality/test_calibration_dimension.py` (A) — the dimension reader/integration tests.
- `tests/quality/test_scorecard_honesty_pins.py` (M) — calibration pins (5 registered) + RED-under-seeded proofs + 8-namespace + slug helper + registry wiring.
- `tests/quality/test_scorecard_reader.py` (M) — canonical-keys tuple → 8 dims.
- `tests/quality/test_scorecard_final_report.py` (M) — cross-dim total 12→13.
- `tests/quality/test_capability_honesty_dimension.py`, `test_coverage_honesty_dimension.py`, `test_cost_efficiency_dimension.py`, `test_fidelity_trust_dimension.py`, `test_tracker_coherence_dimension.py`, `test_lane_discipline_dimension.py` (M) — cross-dimensional aggregate dims-set / total updated for the 8th dimension.
