---
baseline_commit: cd48acd1
---

# Story Q2.3: Fidelity-trust dimension (source→output faithfulness)

Status: ready-for-dev

<!-- Epic Q2 (Ready siblings). DISPATCH #3 (LAST of Q2). Closing this story closes Epic Q2. Source epic: _bmad-output/planning-artifacts/epics-project-quality-scorecard-2026-07-19.md. Follows the Q2.1/Q2.2 sibling EXEMPLARS + ALL their review learnings. Honors the GL-13 authoring contract + the 5 Q1-retro action items. -->

## Story

As **the project quality scorecard**,
I want **a Fidelity-trust dimension scored from the EXISTING Vera fidelity trace + the `source_fidelity_audit` semantic tripwire, with its own honesty pin**,
so that **the operator sees an honest read of source→output faithfulness — and the WARN-only-that-never-gates semantic fence is scored as the measured GAP, not as "gating."**

## Scope fence (read FIRST)

Q2.3 adds ONE new dimension (`fidelity_trust`) reusing the Q1 engine + the Q2.1/Q2.2 pattern. It does **NOT**:

- **Touch DID / cost_efficiency / coverage_honesty** (all done) — their numbers + prose + machine blocks are read-only.
- **Change the fidelity runtime / audit / Vera trace / production_runner** — CONSUME `SEMANTIC_TRIPWIRE`, `source_fidelity_audit`, the Vera Omissions/Inventions/Alterations trace read-only; NO parallel plumbing (GL-15/NFR3).
- **Touch Q3** — fidelity_trust only.
- **Add module-scope `app.*` to `app/quality`** (GL-3) — fidelity types via deferred local import / plain data read.
- **Wire into production_runner's live emit** — E2E rides R2 (GL-10).
- Extend the Q1 machinery **only additively**.

## Honest baseline (verified — the assessment must match this)

- **The semantic-fidelity audit is WARN-ONLY and does NOT gate production.** `app/specialists/_shared/source_fidelity_audit.py::SEMANTIC_TRIPWIRE = {"mode": "warn_only", "gates_production": False, ...}`. It reports candidate unsourced-framing but never FAILS a production run → **a WARN that never gates = the measured gap** (the epic AC: "the WARN-only / default-OFF posture IS the measured gap; a WARN that never gates = a capped level"). This is DID Leak-2 (`braid-workbook-semantic-claim-citation-audit`) — cross-link it; do NOT double-count.
- **The Vera fidelity trace detects Omissions / Inventions / Alterations** (`app/specialists/irene/graph.py`, `voice_provider_text.py`) — real detection machinery exists (its honesty is a criterion), but the semantic-claim fence is WARN-only.

## Acceptance Criteria

**AC1 — New `## Dimension 4 — Fidelity-trust` section + machine-block entry**, mirroring the DID §1 / cost §2 / coverage §3 structure (why-load-bearing → rubric → assessment table `{level, derivation, signal, evidence_ref, score, max}` → ranked leaks → cadence). Machine block gains a `fidelity_trust` dimension with the full field-set (`rubric_version/as_of/as_verified/score/max/band/band_note/criteria/open_leaks/leaks/trend`). Band+leaks+trend.

**AC2 — Signal readers over the EXISTING fidelity emitters** (fail-soft, read-only, clean-leaf). Criteria (follow the signal-vs-judgment partition — retro AI-Q4):
- **semantic-fence gating (SIGNAL-DERIVED, the leak):** does the semantic-fidelity audit GATE production? Read `SEMANTIC_TRIPWIRE["gates_production"]` (a real module constant). Honest today: `False` (WARN-only) → **weak / capped** (the leak). **Reachable close-path** (if `gates_production` is genuinely flipped True, the reader reports gating=True → the criterion can earn strong — the pin must NOT block the honest upgrade); **read-only** (just read the constant — no mutation; simpler than CV1/CE1 since it's a constant not an env toggle, but keep the same discipline).
- **fidelity-trace honesty (Omissions/Inventions/Alterations):** the Vera trace detects O/I/A. A signal that claims "fidelity clean" MUST consult the real fail condition (O/I/A present), not just trace presence (the Q2.2 CV2 `is_clean_pass` learning — do NOT report clean on a real fidelity FAIL). (judgment-with-evidence.)
- **audit honesty (WARN transparency):** the audit honestly labels itself `warn_only` / advisory rather than silently passing unsourced framing (judgment-with-evidence).
- Do NOT let an unverified/unknown signal award a clean level.

**AC3 — The dimension's own honesty pin (GL-6 meta-ratchet REQUIRES it).** Register a `fidelity_trust` pin in `_HONESTY_PIN_REGISTRY` + add `fidelity_trust` to `_EXPECTED_CANONICAL_DIMENSION_KEYS` + the gating reader to `_SIGNAL_DERIVED_READERS`. The gates-claim pin is doc↔code: **the score FAILS if it claims "gating" while `SEMANTIC_TRIPWIRE["gates_production"]` is `False`** (the epic's exact honesty-pin). RED-under-seeded (GL-9): bump the fidelity-fence level to strong while `gates_production` is False → RED.

**AC4 — GL-13 leak registration + cross-dimensional integration.**
- `fidelity_trust` `leaks:` list (`{rank, criterion, slug, lane}`; `len == open_leaks`); ≥1 = the WARN-only-semantic-fence leak (lane `learner-trust` — fidelity = source→output trust; use judgment per §rubric). Slug → a FOURTH namespace registry (e.g. `## Fidelity-Trust Scorecard Leak Registry` / `fid_leak:`), disjoint from `did_leak:`/`cost_leak:`/`cov_leak:` (verify all FOUR readers don't cross-count). **Cross-link DID Leak-2** (`braid-workbook-semantic-claim-citation-audit`) in the registry note — do NOT double-count (the DID leak counts under `did_leak:`; the fidelity leak is its own `fid_leak:` framing).
- reconcile-by-identity (retro AI-Q2) covers fidelity.
- `ranked_project_leaks` now aggregates DID + cost + coverage + fidelity; `leak_coverage_gaps` stays clean (add fidelity_trust to the real-repo coverage assertion).

**AC5 — Mirror + trend + history.** Append a `fidelity_trust` snapshot to `scorecard-history.jsonl` (mirror pin, per-dimension); trend baseline; projector picks it up NO code change.

**AC6 — Tests (hermetic + real) + honest Band.** Trace-shape signal readers against fixture Vera traces (O/I/A present + clean) AND real state; **the `gates_production` boolean pin** RED-under-seeded (GL-9 — claims gating while gates_production False → red); the fidelity-trace-honesty signal must report NOT-clean on a real O/I/A fail (the Q2.2 CV2 learning); meta-ratchet green; mirror/arithmetic/leak-identity (4 namespaces)/coverage all green. **Band honesty:** if the semantic-fence (thesis) is weak while trace/audit-honesty criteria are strong, the band_note states the headline is trace-honesty-lifted while the semantic fence is WARN-only — do not read the Band as "fidelity is gated." **E2E:** deferred to R2 (GL-10 — file the obligation). DID/cost/coverage pins + numbers unchanged.

## Tasks / Subtasks
- [x] **T1 — Readiness.** Re-read the scope fence + honest baseline + the Q2.1/Q2.2 exemplars + ALL their review learnings (fence reader reachable/read-only; band honesty; the CV2 is_clean_pass/FAIL-consulting lesson; non-empty guards; status consistency; injectable-env fail-soft; predicate-not-field-presence; JSON-str-vs-path; anti-drift vocab pin) + GL-13/GL-6/GL-9 + the 5 retro action items. Confirm no pipeline-lockstep trigger path edited.
- [x] **T2 — Signal readers** (AC2) — semantic-fence-gating (read the real `gates_production`), fidelity-trace-honesty (consult the real O/I/A fail condition, not just presence), audit-honesty; fail-soft; clean leaf.
- [x] **T3 — Rubric + assessment + machine block** (AC1); honest levels; the WARN-only leak; signal-vs-judgment.
- [x] **T4 — Honesty pin + registry** (AC3); the gates_production pin; RED-under-seeded.
- [x] **T5 — GL-13 leaks + fid_leak registry (4th namespace) + identity + ranked/coverage + DID-Leak-2 cross-link** (AC4).
- [x] **T6 — History mirror** (AC5) + honest band_note.
- [x] **T7 — Tests + R2 obligation** (AC6).
- [x] **T8 — Verify.** `pytest tests/quality/ -q`; ruff; import-linter 18/0; clean-leaf green; DID/cost/coverage unchanged; ALL prior pins green.

## Dev Notes

### Verified fidelity seams (GL-15 — reuse, do NOT rebuild)
- `app/specialists/_shared/source_fidelity_audit.py`: `SEMANTIC_TRIPWIRE` (`mode: warn_only`, `gates_production: False`, `claim_fence`), `audit_semantic_framing`, the audit that reports candidate unsourced-framing (WARN-only).
- Vera fidelity trace (Omissions/Inventions/Alterations): `app/specialists/irene/graph.py`, `app/specialists/_shared/voice_provider_text.py` — find the trace model/shape.
- Read the audit/trace as plain data or deferred-import — NO module-scope `app.*` in `app/quality`.

### Follow the Q2.1/Q2.2 EXEMPLARS + ALL their review learnings (do NOT repeat any prior bug)
The two prior siblings (`cost_efficiency`, `coverage_honesty`) are the pattern. Apply their review fixes preemptively:
- Fence reader: reachable close-path + read-only (Q2.1 FIX-1/FIX-6). Here the source is a constant (`gates_production`) not an env toggle → simpler, but keep the discipline (read the real source; reachable when flipped).
- **The Q2.2 CV2 lesson (most relevant here):** the fidelity-trace-honesty signal must consult the REAL fidelity FAIL condition (O/I/A present) — do NOT report a "clean" fidelity on a real Omission/Invention/Alteration. Add a test that a fail trace → not-clean, and assert it (not a toothless test).
- Band honesty (Q2.1 FIX-2); non-empty guards (Q2.1 FIX-3); status:unavailable on missing import (Q2.1 FIX-4); predicate-not-field-presence (Q2.2 FIX-3); injectable-env fail-soft (Q2.2 FIX-2) if any env path; anti-drift vocab pin (Q2.2 FIX-5) if any duplicated set.
- Equal-weight scoring kept (consistent with DID/cost/coverage); honest reading via band_note.

### The 5 Q1-retro action items (BINDING)
GL-13 registration; reconcile-by-IDENTITY (fidelity slug set-compare, 4 namespaces); GL-9 (green-by-reality + RED-under-seeded); signal-vs-judgment honesty; R2 witness filed.

### Honesty is the bar (+ closes Epic Q2)
The semantic-fidelity audit is real but WARN-ONLY (gates_production False) → it never fails a production run → the WARN-that-never-gates is the leak. Say so plainly (a real audit, advisory-only) → the measured gap. A real Omission/Invention/Alteration must not read as clean fidelity. Do not overclaim "gating"; do not understate the audit/trace machinery as absent.

### Testing standards
Reuse `tests/quality/`. Hermetic fixture traces + real reads; the gates_production pin. No live calls; no `--run-live`.

### References
- [Source: epics-project-quality-scorecard-2026-07-19.md#Story Q2.3] + [#GL-13/GL-15/GL-6/GL-9/GL-10] + FR9.
- [Source: docs/dev-guide/quality-scorecard-dimension-authoring.md] — the GL-13 contract.
- [Source: app/specialists/_shared/source_fidelity_audit.py:51-53 (SEMANTIC_TRIPWIRE gates_production:False) · irene/graph.py · voice_provider_text.py] — the fidelity seams.
- [Source: q2-1 + q2-2 stories (done) + their review remediations] — the sibling exemplars + ALL learnings (esp. Q2.2 CV2 FAIL-consulting).
- [Source: docs/quality/project-quality-scorecard.md §1/§2/§3 + machine block; §1.6 DID Leak-2] — the exemplars + the cross-linked leak.
- [Source: app/quality/{signals,scorecard,history,report}.py · tests/quality/test_scorecard_honesty_pins.py] — the engine + registry to extend.

## Dev Agent Record

### Agent Model Used

Claude Opus 4.8 (1M context) — fresh BMAD dev agent, RED-first, via `bmad-dev-story`.

### Debug Log References

- Baseline `pytest tests/quality/ -q`: 254 passed (pre-change green).
- Final `pytest tests/quality/ -q`: **295 passed** (254 baseline + 41 new).
- `ruff check app/quality/ tests/quality/`: All checks passed.
- `lint-imports`: **18 kept, 0 broken.**
- `pytest tests/quality/test_scorecard_clean_leaf.py`: 1 passed (GL-3 clean-leaf green — the two deferred imports `SEMANTIC_TRIPWIRE` / `vera._act._hard_fail` are function-local).
- RED-under-seeded proofs fired GREEN (each detects its seeded violation): `test_fidelity_gates_claim_reds_on_dishonest_level` (gating-claim while `gates_production` False), `test_fidelity_gates_claim_reds_on_any_inflated_level[strong|partial|uniform]`, `test_trace_honesty_real_oia_fail_is_not_clean` (the Q2.2 CV2 FAIL-consulting lesson), `test_fidelity_slug_identity_reds_on_seeded_typo_while_count_stays_green`, `test_four_leak_namespaces_are_disjoint_and_dont_cross_count`, `test_every_dimension_has_a_honesty_pin` (GL-6 meta-ratchet now covers fidelity_trust).

### Completion Notes List

Implementation COMPLETE (all 6 ACs). Status intentionally left `ready-for-dev` per the dispatch instruction (awaiting party green-light + `bmad-code-review` gates); do NOT read as un-started.

- **AC1** — added `## Dimension 4 — Fidelity-trust` prose (why-load-bearing → §4.0 rule → §4.5 rubric → §4.6 assessment table `{level, derivation, signal, evidence_ref, score, max}` → ranked leaks → cadence) + a `fidelity_trust` machine-block entry (full field-set). Band **C** (58/100 = Σ 7/12); FT1 weak / FT2 strong / FT3 strong.
- **AC2** — three fail-soft, read-only, clean-leaf readers in `app/quality/signals.py`: `semantic_fence_gating_signal` (FT1, SIGNAL-DERIVED — reads the REAL `SEMANTIC_TRIPWIRE["gates_production"]` constant; reachable close-path via injectable `tripwire` + strict-bool guard), `fidelity_trace_honesty_signal` (FT2, judgment-with-evidence — **consults the REAL `vera._act._hard_fail` predicate** over a trace's O/I/A findings + verdict; the Q2.2 CV2 lesson: a real critical O/I/A → NOT clean), `fidelity_audit_honesty_signal` (FT3, judgment-with-evidence — `mode=="warn_only"` + claim-fence transparency). Plus `fidelity_leak_count_signal`. `level_from_signal` gains `semantic_fence_gating_on` → `_level_ft_semantic_fence` (strong/weak/unavailable).
- **AC3** — registered `fidelity_trust` in `_HONESTY_PIN_REGISTRY` (3 pins), added `fidelity_trust` to `_EXPECTED_CANONICAL_DIMENSION_KEYS`, added `semantic_fence_gating_on` to `_SIGNAL_DERIVED_READERS`. The **gates-claim pin is the epic's exact pin** — the score FAILS if FT1 claims `strong`/gating while `SEMANTIC_TRIPWIRE["gates_production"]` is False (RED-under-seeded proven; GL-9 green-by-reality today = weak).
- **AC4** — FT1 `leaks:` list `{rank:1, criterion:FT1, slug:fidelity-trust-semantic-fence-warn-only-never-gates, lane:learner-trust}` (`len==open_leaks==1`). Added the FOURTH `## Fidelity-Trust Scorecard Leak Registry` (`fid_leak:` namespace), disjoint from `did_leak:`/`cost_leak:`/`cov_leak:` (four-namespace disjointness pin green: counts 5/1/1/1, pairwise-disjoint slug sets). **DID Leak-2 (`braid-workbook-semantic-claim-citation-audit`) cross-linked** in the registry note + §4.6 + machine-block comment — SAME substrate, counted ONCE per namespace, NOT double-counted. `ranked_project_leaks` aggregates DID(5)+cost(1)+coverage(1)+fidelity(1)=8; `leak_coverage_gaps` clean; identity-reconcile pin green.
- **AC5** — appended a `fidelity_trust` snapshot to `scorecard-history.jsonl` (mirror pin green; trend baseline). **Projector needs NO code change** (`test_projector_renders_fidelity_dimension_with_no_code_change` green).
- **AC6** — hermetic fixture traces (clean / real critical-O/I/A FAIL / warn-only / empty) + real reads. Band honesty: band_note states the headline is **trace-honesty-lifted while the semantic fence is WARN-only** — do NOT read C as "fidelity gated." Equal-weight kept. **E2E deferred to R2** — obligation filed to `deferred-work.md` (`q2-3-r2-fidelity-trust-witness`).
- **Scope fence honored:** DID 65/B-, cost 62/B-, coverage 58/C UNCHANGED (numbers/prose/machine-blocks additive-only, 0 deletions in the doc); fidelity runtime (`source_fidelity_audit.py`, `vera/_act.py`, `irene/graph.py`, `production_runner.py`) UNTOUCHED (GL-15 — reuse, no parallel plumbing); no pipeline-lockstep trigger path edited; Q1 machinery extended additively only.
- **All prior pins green:** DID/cost/coverage signal-derived + leak-count + slug-identity + arithmetic + mirror + trend + GL-6 meta-ratchet (now covers fidelity_trust) all pass in the 295-green suite.

### File List

- `app/quality/signals.py` — MODIFIED (FT1/FT2/FT3 readers + `fidelity_leak_count_signal` + `_read_semantic_tripwire`/`_read_fidelity_trace` helpers + `_level_ft_semantic_fence` + `level_from_signal` registration).
- `app/quality/scorecard.py` — MODIFIED (`_FIDELITY_KEY` + `_EXPECTED_CANONICAL_DIMENSION_KEYS`).
- `docs/quality/project-quality-scorecard.md` — MODIFIED (Dimensions list line 4; `## Dimension 4 — Fidelity-trust` prose; `fidelity_trust` machine-block entry). Additive-only (0 deletions).
- `docs/quality/scorecard-history.jsonl` — MODIFIED (appended `fidelity_trust` baseline snapshot).
- `_bmad-output/planning-artifacts/deferred-inventory.md` — MODIFIED (`## Fidelity-Trust Scorecard Leak Registry` + `fid_leak:` tag + DID-Leak-2 cross-link note).
- `_bmad-output/implementation-artifacts/deferred-work.md` — MODIFIED (R2 witness obligation `q2-3-r2-fidelity-trust-witness`).
- `tests/quality/test_fidelity_trust_dimension.py` — NEW (readers hermetic+real; FT1 reachable/read-only; FT2 FAIL-consulting; GL-13 aggregation; projector).
- `tests/quality/test_scorecard_honesty_pins.py` — MODIFIED (fidelity imports + `_FIDELITY_LEAK_SLUG_RE`/`_registry_fidelity_leak_slugs`; FT1 in `_SIGNAL_DERIVED_READERS`; `fidelity_trust` pin registry; 3 registered pins + RED proofs + four-namespace disjointness + reader-grounding).
- `tests/quality/test_scorecard_reader.py` — MODIFIED (canonical-keys tuple → 4 dims).
- `tests/quality/test_cost_efficiency_dimension.py` — MODIFIED (cross-dim set → 4 dims).
- `tests/quality/test_coverage_honesty_dimension.py` — MODIFIED (cross-dim set → 4 dims).
- `tests/quality/test_scorecard_final_report.py` — MODIFIED (ranked total 7 → 8).
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — MODIFIED (q2-3 → in-progress).

### Change Log

- 2026-07-19 — Q2.3 fidelity_trust dimension implemented (RED-first). 41 new tests; 295 quality tests green; ruff clean; import-linter 18/0; clean-leaf green. Status left `ready-for-dev` per dispatch (awaiting review gates); no commit.
- 2026-07-19 — Code-review (3-layer) remediation applied RED-first to the FT2 fidelity-trace reader (`app/quality/signals.py` + `tests/quality/test_fidelity_trust_dimension.py`):
  - **FIX-1(a)** clean-guard hardened `len(findings) > 0` → `oia_finding_count > 0` (a no-O/I/A trace can no longer certify clean — the CV2 over-claim this reader prevents). RED-first: OLD guard returned `is_clean=True`.
  - **FIX-1(b)** added the ISOLATING pin on the story's own thesis — critical O/I/A finding + NON-halt (PROCEED) verdict → `verdict_halts False` AND `is_clean_fidelity False`, proving `_hard_fail` ALONE drives not-clean (a verdict-status-only regression is now caught). RED-first vs a regressed verdict-only impl.
  - **FIX-2** pass DICT-FILTERED findings to `_hard_fail` so a non-dict entry before a real critical O/I/A no longer masks the fail as `unavailable`. RED-first: OLD raw-list path → `status=unavailable`.
  - **FIX-3** validate `schema_version == "fidelity-trace.v1"` before certifying clean; a foreign/missing-schema dict → `unavailable`, never clean. RED-first: OLD (no check) → `is_clean=True` on a foreign O-bearing dict.
  - **FIX-4** anti-drift pin ties `_OIA_CATEGORIES`/`_FIDELITY_HALT_STATUS`/`_FIDELITY_TRACE_SCHEMA` to Vera's real `OIA` + the `act()` source strings, so a future Vera rename reds the test.
  - Result: 301 quality tests green (+6); ruff clean; import-linter 18/0; clean-leaf green; four-namespace disjoint; DID 65/B-, cost 62/B-, coverage 58/C UNCHANGED; all prior pins green. Status still `ready-for-dev`; no commit.
