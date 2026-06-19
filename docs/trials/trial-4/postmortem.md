# Trial-4 Postmortem

> Run `d7ad4dac-7e65-4bde-9cb2-88a13fed2adc` · 2026-06-19 · branch `trial/4-2026-06-12`.
> Detailed gate-by-gate ledger (every card digest, verdict, command, artifact): `_bmad-output/implementation-artifacts/trial-4-run-log-d7ad4dac.md`. This file is the §7-routed harvest of record.

---

## Verdict

**Verdict:** `PASS` (reached completion — full pipeline G0 → `status: completed`, per `methodology.md §5`).

**One-line summary:** First operator-in-the-loop Trial-4 ran the full pipeline to completion (6 gates crossed, 6/6 real ElevenLabs narration segments, assembly bundle built, $0.24) after 2 substrate fixes + 1 LLM re-roll cleared live-only gaps the offline suites hid.

---

## SHAPE A — Reflection

### Q1: Did we reach completion?
Yes — `status: completed`, no remaining pause, no error. All six gates (G1/G2B/G2C/G3/G4/G4A) crossed; narration synthesized; compositor assembly bundle + Descript hand-off produced.

### Q2: The single moment this trial felt different
_(operator to confirm/amend — synthesis:)_ The first time a fix landed mid-trial and the **same trial recovered past the exact node it had crashed on** (Gary deck export → quinn-r 07B → G2B), rather than relaunching from scratch. The error-pause/recover loop turned "doomed run" into "fix-and-continue."

### Q3: What the runtime did that I didn't expect
_(operator to confirm/amend — synthesis:)_ Good surprise: the taxonomy re-base held — Gary's brief-unmatched and irene's slide-join failures **error-paused recoverably instead of crashing** (the quinn-r 07B `ModeMismatchError` was the one that still crashed, because it's outside the dispatch-error family). Also good: G4A surfaced **real voice options with playable samples**, beyond the empty G2B candidates.

### Q4: If I had to halt, would I have? Where, and why didn't I?
_(operator to confirm/amend — synthesis:)_ The decision point was the 2nd Gary recover failing worse (5/6 slides orphaned). That justified halting-to-fix rather than re-rolling — and we did pause the walk, land the title-pinning fix, then recover. Never halted the campaign; the weed-clearing posture (accept substrate-probe gates, fix blockers, harvest nits) held throughout.

### Q5: One line for cross-trial-learnings
**A downstream fail-loud guard that hardens correctly can still mask an under-constrained upstream producer — the cure is upstream (Gamma title-pinning), not the guard.**

---

## SHAPE B — Structured findings

#### Finding T4-F1: G1 drafted-reject false-negative + specialist-summary artifact-list reporting gap
| Field | Content |
|---|---|
| Surface | G1 (trial_open) drafted_proposal; Texas/quinn-r/vera/enrique specialist-summaries |
| Trigger | Real bundle on disk (manifest lists 5 artifacts) but specialist-summary "Emitted artifacts: none" + a double Texas dispatch (exit-10) |
| Failure mode | G1 auto-recommendation = `reject`/halt-for-repair on confidence signals (`artifact_paths_empty`, `dispatch_exit_code_10`, `duplicate_output_digest`) over genuinely-present content |
| Anti-pattern mapping | candidate: "specialist-summary 'emitted artifacts' list not wired to the on-disk bundle/output manifest" |
| Workaround | Operator (Claude) investigated, confirmed real content, approved |
| Permanent-fix shape | Wire specialist-summary artifact lists to the bundle/output manifest; de-dupe / explain the Texas exit-10 double dispatch; have G1 drafted-proposal read the manifest, not just the summary |
| Filing target | deferred-inventory (Q2) — `trial-4-specialist-summary-artifact-list-reporting-gap` |

#### Finding T4-F2: Gamma deck export brief-unmatched (storyboard-correctness) — FIXED
| Field | Content |
|---|---|
| Surface | Gary node 07 deck export (`gamma.export.brief-unmatched`) |
| Trigger | Gamma free-generated card count + titles (no `card_split`, no title pinning) → merged 6 briefs → 5 pages, invented titles; bijective title-matcher correctly refused |
| Failure mode | Error-pause on slides 5/6 unmatched (1st roll), 2/3/4/5/6 (2nd roll — worse); systematic, not transient |
| Anti-pattern mapping | candidate: "downstream fail-loud guard hardened, upstream producer left under-constrained" |
| Workaround | FIXED `10befac` — `card_split=inputTextBreaks` + title-led chunks via shared `_slide_title`; spec `spec-gamma-title-pinning-card-split.md` |
| Permanent-fix shape | Landed. |
| Filing target | cross-trial (D) closure record + Q1 candidate flag |

#### Finding T4-F3: G2B variant pick is accept/review, not a binding pick-from-N selector
| Field | Content |
|---|---|
| Surface | G2B (07B-gate) `G2BCard` |
| Trigger | Operator expected per-slide pick-from-N variant selection routing downstream |
| Failure mode | `variant_candidates: []`, `selected_variant_id` write-only, `edit` non-binding; run was single-dispatch (one variant/slide) |
| Anti-pattern mapping | n/a (known deferred scope) |
| Workaround | Operator approved (reviewed published Storyboard A at G2C) |
| Permanent-fix shape | Build the binding pick-from-N variant selector (re-route per slide) — the "big leap" |
| Filing target | deferred-inventory (Q2) — `trial-4-binding-variant-voice-picker` (with T4-F6) |

#### Finding T4-F4: node 07B quinn-r dispatched without gate_id → ModeMismatchError crash — FIXED
| Field | Content |
|---|---|
| Surface | quinn-r `_act._mode` at node 07B (variant eval) |
| Trigger | Arc-1a moved `gate_code: G2B` off node 07B onto the content-free `07B-gate`, stripping 07B's quinn-r mode signal |
| Failure mode | `ModeMismatchError: gate_id ''` — a CRASH (outside `SpecialistDispatchError`), not a recoverable error-pause |
| Anti-pattern mapping | candidate: "waking/splitting a gate off a specialist prep-node strips the specialist's mode-derivation; the wake must re-home it" |
| Workaround | FIXED `1b629f3` — `_effective_quinn_r_gate_code` derives the mode gate_code from the following content-free gate; spec `spec-quinn-r-07b-variant-gate-id.md` |
| Permanent-fix shape | Landed. Deferred hardening: put `ModeMismatchError` in the `SpecialistDispatchError` family so a mode-miss error-pauses instead of crashing |
| Filing target | cross-trial (D) closure + Q1 candidate flag; deferred-inventory for the recoverable-family hardening |

#### Finding T4-F5: irene pass-2 slide-join-failed (LLM variance) — cleared by re-roll
| Field | Content |
|---|---|
| Surface | irene node 08 (`irene.pass2.slide-join-failed`) |
| Trigger | One roll of irene pass-2 produced narration whose `visual_references[].perception_source` referenced no roster slide |
| Failure mode | Recoverable error-pause; the guard (`_assert_narration_joins_roster`) is correct |
| Anti-pattern mapping | n/a (LLM output variance; prompt already mandates perception_source) |
| Workaround | One `trial recover` re-roll → conforming output |
| Permanent-fix shape | If recurs: tighten pass-2 output-schema enforcement of `perception_source`. Watch-item |
| Filing target | cross-trial (D) run-shape learning |

#### Finding T4-F6: G4A voice options not wired to card.voice_candidates
| Field | Content |
|---|---|
| Surface | G4A (11-gate) `G4ACard` vs enrique `voice_preview.voices` |
| Trigger | Enrique emitted 3 real voices (with sample_audio_url) but `card.voice_candidates: []` |
| Failure mode | Structured candidates absent from the card (only in the enrique output); selection non-binding |
| Anti-pattern mapping | n/a (structured-parsing follow-on) |
| Workaround | Claude surfaced the 3 samples from the enrique output; operator approved default (Roger) |
| Permanent-fix shape | Wire `voice_preview.voices` → `card.voice_candidates` (prereq for the binding voice picker) |
| Filing target | deferred-inventory (Q2) — folded into `trial-4-binding-variant-voice-picker` |

---

## Implications

### What was PROVED
- Full production pipeline G0 → completion is operator-runnable end-to-end with HIL pauses at all 6 active gates (G1/G2B/G2C/G3/G4/G4A), real verdicts, clean cross-process resume.
- The taxonomy re-base works: Gary brief-unmatched + irene slide-join failures **error-paused recoverably** (fix-and-continue on the SAME trial), not crash-and-relaunch.
- The Gamma title-pinning fix makes the deck export deterministic-matchable (6/6 bound, slide-05 that orphaned twice now correct).
- Storyboard A + B publish online; G4A surfaces real voice previews with samples; narration synthesizes 6/6 real segments.

### What was SURFACED
- Gate auto-recommendations + specialist summaries read thin/false-negative because summaries aren't wired to on-disk manifests (T4-F1).
- The woken G2B/G4A gates are accept/review checkpoints, not the binding pick-from-N selectors the operator wants (T4-F3/F6) — the headline gap for the next trial.
- `ModeMismatchError` is outside the recoverable family (T4-F4) — a mode-miss crashes rather than error-pauses.
- Arc-1a's gate-wake split left a latent dispatch gap (07B mode signal) invisible to offline tests.

### Decisions ratified
- **Filed (deferred-inventory):** `trial-4-binding-variant-voice-picker` (F3+F6); `trial-4-specialist-summary-artifact-list-reporting-gap` (F1); `trial-4-modemismatch-recoverable-family` (F4 hardening).
- **Closed/fixed this session:** T4-F2 (`10befac`), T4-F4 primary (`1b629f3`) — both pushed, spec'd, 3-lane reviewed.
- **Cross-trial (D):** §Trial-4 entries appended; 2 Q1 anti-pattern candidates flagged for Mary harvest-gate.

---

## Cycle metrics

| Metric | Value |
|---|---|
| Wall-clock (launch → close) | ~04:50 → 06:08 UTC (~1h20, incl. 2 fix-and-recover loops) |
| Number of attempts | 1 campaign; 4 recovers (2 Gary, 1 quinn-r-post-fix, 1 irene) |
| Total cost (LLM + APIs) | $0.24 |
| Tripwire firings | none (the error-pauses are guard fail-louds, not tripwires) |
| Broad-regression delta | 0 new failures from the 2 fixes (57 gary + 303 marcus/quinn_r/gary + new tests green; lint-imports 13) |
| Specialists exercised | texas, cd, irene_pass1, irene (pass-2), quinn_r, vera, gary, kira, enrique, desmond, compositor |
| Gates reached | G0, G1, G2B, G2C, G3, G4, G4A → completion |
| Operator attention-quality | _(operator to fill)_ |

---

## Harvest discipline (§7 four-question routing)

### Anti-patterns surfaced (candidates → `specialist-anti-patterns.md`; Mary harvest-gate ratifies)
- **Candidate:** "Downstream fail-loud guard hardened while the upstream producer stays under-constrained — the guard correctly refuses, but the cure is upstream" (T4-F2, Gamma title-pinning). 1st occurrence.
- **Candidate:** "Waking/splitting a HIL gate off a specialist prep-node strips that specialist's mode-derivation signal; the wake must re-home it" (T4-F4, 07B). 1st occurrence.

### Deferred-inventory triggers fired (→ `deferred-inventory.md`)
- `trial-4-binding-variant-voice-picker` (F3+F6) — the big-leap selector. NEW.
- `trial-4-specialist-summary-artifact-list-reporting-gap` (F1). NEW.
- `trial-4-modemismatch-recoverable-family` (F4 hardening). NEW.

### Architecture decisions shifted (→ architecture §10)
- None.

### Cross-trial patterns emerging (→ `cross-trial-learnings.md`)
- §Trial-4 by-gate symptoms + run-shape learnings appended; the 2 fixes recorded as closures.

### Routing summary
| Findings filed → | A: anti-patterns | B: inventory | C: architecture | D: cross-trial |
|---|---|---|---|---|
| Count | 2 (candidates) | 3 | 0 | run-shape + 2 closures |

**Confirmation:** Each finding routed once. F2/F4 = fixed-this-session (cross-trial closure + Q1 candidate); F1/F3/F6 = inventory; F5 = cross-trial run-shape. No double-filings; no unfiled findings.

---

## Forensic evidence pointers (do-not-delete)
- `state/config/runs/d7ad4dac-7e65-4bde-9cb2-88a13fed2adc/` — full runtime artifacts (6 decision cards, 6 verdicts, bundle, exports, fidelity, enrique-narration/assembly-bundle with 6 mp3s, cost report, trace-fixture).
- `_bmad-output/implementation-artifacts/trial-4-run-log-d7ad4dac.md` — detailed ledger.
- `_bmad-output/implementation-artifacts/spec-gamma-title-pinning-card-split.md` + `spec-quinn-r-07b-variant-gate-id.md` — fix specs.
- LangSmith trace: https://smith.langchain.com/traces/d7ad4dac-7e65-4bde-9cb2-88a13fed2adc

---

## References
- `docs/trials/methodology.md`, `docs/trials/cross-trial-learnings.md`
- `_bmad-output/planning-artifacts/deferred-inventory.md`
- `TRIAL-4-URLS.txt` (project root — storyboard + voice-sample + artifact links)
