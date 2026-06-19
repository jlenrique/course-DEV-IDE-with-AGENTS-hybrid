---
title: 'P1 — G5 WPM check becomes a voice-agnostic intelligibility band'
type: 'bugfix'
created: '2026-06-19'
baseline_commit: '78c8753'
status: 'done'
governance:
  workflow: 'bmad-quick-dev'
  gate_mode: 'single'
  cycle: 'NEW CYCLE — Claude pre-author → Codex T1-T10 → Claude T11'
  authority: '_bmad-output/planning-artifacts/beta-phase-1-closure-ratification-2026-06-19.md §5 (Murat ruling, operator-ratified)'
context:
  - '{project-root}/_bmad-output/planning-artifacts/beta-phase-1-closure-ratification-2026-06-19.md'
  - '{project-root}/_bmad-output/planning-artifacts/deferred-inventory.md'
  - '{project-root}/docs/STATE-OF-THE-APP.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Quinn-R's G5 WPM check asserts the wrong invariant. `run_g5_checks` (`app/specialists/quinn_r/_act.py:134-143`) blocks when `abs(observed - target_wpm) > tolerance` with defaults `target_wpm=150`, `tolerance=20` — an effective band of **[130, 170]** centered on an arbitrary target. A NON-default voice pick (`beta-voice-select-wpm-qa-interaction`) trips it: Sarah's natural, fully-intelligible measured cadence of **128 WPM** falls below the 130 floor, so a non-default-voice run cannot complete error-free. The default voice (Roger) happens to land in-band, which is why approve-path runs pass — masking the defect. The check conflates "this voice's natural cadence differs from 150" with "this narration is pathologically fast/broken." It is the same disease as the §3 fidelity regression in a smaller dose: a gate enforcing an invariant that does not match reality.

**Approach (party-ratified §5 — do not re-litigate the design):** Replace the symmetric deviation-from-target invariant with an explicit, **voice-agnostic intelligibility band** — a low floor set at the slowest observed natural voice minus margin, and a high ceiling that catches genuinely runaway/garbled TTS. The gate exists to catch *pathological* narration rate, not natural cadence. The band is a pair of module-level constants with a code comment citing the ruling and the empirical datum (Sarah, 128 WPM measured 2026-06-19). `target_wpm` / `wpm_tolerance` no longer gate (they remain in config for estimator use elsewhere — untouched). The existing `wpm_durations_estimated` advisory escape is preserved verbatim. A **logged break-glass operator override** is retained (never the default path) per the ruling: an explicit payload flag downgrades a breach to an advisory witness rather than blocking.

This is the P1 deliverable of the ratified forward path; it unblocks capability-(e)-voice-to-completion on a non-default voice.

## Boundaries & Constraints

**Always:** Surgical diff confined to `run_g5_checks` + its test twins. Band is voice-agnostic (one universal floor/ceiling), NOT a per-voice table (Murat: "N gates drift"). Floor/ceiling are named module constants with a citing comment. Existing non-WPM G5 checks (VTT monotonicity, coverage, duration-coherence advisory) stay byte-identical. The `wpm_durations_estimated` advisory path stays verbatim. `WpmThresholdError` keeps its dual base + `quinn_r.g5.wpm-threshold` tag.

**Ask First:** Any change to the WPM check beyond floor/ceiling + the named break-glass (e.g., re-targeting per voice, removing `target_wpm` from config, touching the estimators that consume `target_wpm`). Any change to the floor/ceiling *values* beyond the ratified rationale below. Promoting the break-glass to a default-on path.

**Never:** Do NOT make the override a blanket/default-on bypass (ruling: "never the default path"). Do NOT build a per-voice WPM table. Do NOT weaken VTT/coverage/duration checks. Do NOT touch pipeline manifest / fold semantics / gate engine. Do NOT remove the `wpm_durations_estimated` escape. Do NOT change `target_wpm` consumers outside Quinn-R (`slide_count_runtime_estimator.py`, `generate-storyboard.py`, `validate-irene-pass2-handoff.py`).

## Ratified band values (rationale + provenance)

> **Party-mode green-light 2026-06-19 (Winston/John/Murat/Mary/Amelia, APPROVE-WITH-AMENDMENTS): the citing comment must disclose provenance AND arbitrariness — not present these numbers as derived fact.** The constant comment in `_act.py` MUST carry the wording below verbatim-in-substance.

- `WPM_INTELLIGIBILITY_FLOOR = 110.0` — **PROVISIONAL, n=1, INTERIM.** Derived from the single slowest *measured* natural voice observed to date: **Sarah, ~128 WPM, run `710684c0` (T5a voice-select rerun), 2026-06-19** (the run whose 128 WPM tripped the old band and motivated `beta-voice-select-wpm-qa-interaction`). `110 = 128 − ~14%`, where the ~14% is a **deliberate intelligibility buffer** (NOT reverse-derived from a round number): no observed natural professional voice lands below it, and a rate under 110 indicates truncated / silent / broken narration, not cadence. **Re-validation trigger (Mary/Murat):** revisit the floor when a second natural voice is measured below 130 WPM, OR at the next perception-arc retrospective — whichever first. The citing comment must state "n=1, interim" so a future reader does not mistake 110 for an established constant.
- `WPM_INTELLIGIBILITY_CEILING = 200.0` — **no natural-voice basis; a runaway-detection ceiling, NOT a cadence target.** Reuses the documented plausible-human-narration ceiling already asserted at `skills/bmad-agent-marcus/scripts/tests/test-narration-config-schemas.py:120` (`100 <= target_wpm <= 200`). Its job is solely to catch runaway/garbled TTS: it need only sit above any plausible natural maximum and below garbage-fast. The citing comment must say "200 = no natural-voice datum; runaway-detection ceiling, not a cadence target" so the asymmetry of evidence between floor and ceiling is disclosed, not hidden.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Default voice (in-band) | observed ≈ 150 WPM, measured | PASS (advisory empty) | N/A |
| **Sarah / slow-but-intelligible** (the bug) | observed ≈ 128 WPM, measured (not estimated) | **PASS** — inside [110, 200] | N/A — no raise (regression guard) |
| Broken-slow | observed < 110 (e.g., 60 WPM), measured | BLOCK | `WpmThresholdError`, tag `quinn_r.g5.wpm-threshold`, message names observed + floor |
| Runaway-fast | observed > 200 (e.g., 400 WPM), measured | BLOCK | `WpmThresholdError` names observed + ceiling |
| Estimated durations | breach, but `wpm_durations_estimated` truthy | advisory only (self-referential) | No raise (existing escape, verbatim) |
| Operator break-glass | breach + `wpm_breach_override` truthy | advisory + logged witness, no raise | `advisory` gains `{reason: "wpm-breach-operator-override", observed, floor, ceiling}` |
| Zero duration | no measurable duration | `observed` falls back to in-band sentinel; PASS | N/A (existing `if duration else` branch) |

</frozen-after-approval>

## Code Map

- `app/specialists/quinn_r/_act.py:134-143` — `run_g5_checks`. Add module constants `WPM_INTELLIGIBILITY_FLOOR`/`WPM_INTELLIGIBILITY_CEILING` (near top of module, with citing comment). Replace the `abs(observed - target_wpm) > tolerance` blocking condition with `not (floor <= observed <= ceiling)`. Preserve the `and not payload.get("wpm_durations_estimated")` advisory escape. Add the `wpm_breach_override` break-glass branch (downgrade-to-advisory + witness). `target_wpm`/`tolerance` reads may stay for the message/estimator-parity but no longer gate.
- `app/specialists/quinn_r/graph.py:299,303` — re-exports `WpmThresholdError` + `run_g5_checks` from `_act`; no change needed (verify intact).
- `tests/specialists/quinn_r/test_quinn_r_g5_qa_body.py` — repoint the `wpm` mutation case (currently sets `target_wpm=60` expecting observed 120 to trip — under the band model 120 is intelligible and will NOT trip, so this case must produce a pathological observed rate). Add regression twins (slow-but-intelligible passes; broken-slow trips; runaway-fast trips; break-glass downgrades).
- `tests/specialists/test_audio_segment_grounding.py:189,218` — VERIFY unaffected (line 189 hits the `wpm_durations_estimated` advisory path; line 218 raises `CoverageGapError`, not WPM). No change expected.
- `tests/specialists/quinn_r/test_quinn_r_two_mode_dispatch.py`, `tests/specialists/quinn_r/test_quinn_r_act_node_dispatch.py`, `tests/parity/test_quinn_r_activation_contract.py` — VERIFY unaffected (all three produce observed ≈ 120 WPM, in-band). No change expected.
- `tests/contracts/test_specialist_error_taxonomy.py:138,145,164` — error-class hierarchy/tag pins, band-independent. No change expected.
- NOT on `state/config/pipeline-manifest.yaml::block_mode_trigger_paths` (verified) — no manifest-regime tier applies.

## Tasks & Acceptance

**Execution:**
- [x] `app/specialists/quinn_r/_act.py` — add `WPM_INTELLIGIBILITY_FLOOR = 110.0` + `WPM_INTELLIGIBILITY_CEILING = 200.0` module constants with a comment citing `beta-phase-1-closure-ratification-2026-06-19.md §5` + the Sarah-128-WPM datum + the gate's pathological-rate purpose.
- [x] `app/specialists/quinn_r/_act.py` — in `run_g5_checks`, replace the blocking predicate with `not (FLOOR <= observed <= CEILING)`; keep the `and not payload.get("wpm_durations_estimated")` escape; `WpmThresholdError` message names the observed rate + the breached bound.
- [x] `app/specialists/quinn_r/_act.py` — add the logged break-glass: when `payload.get("wpm_breach_override")` is truthy AND a breach would otherwise raise, append a witness dict to `advisory` (`reason: "wpm-breach-operator-override"`, observed, floor, ceiling) and do NOT raise (never default; only on explicit flag).
- [x] `tests/specialists/quinn_r/test_quinn_r_g5_qa_body.py` — repoint `test_g5_blocking_failures_raise[wpm]` to a pathological observed rate (shrink duration so observed > 200, or grow it so observed < 110) — still raises `WpmThresholdError`.
- [x] `tests/specialists/quinn_r/test_quinn_r_g5_qa_body.py` — add `test_g5_slow_but_intelligible_voice_passes` (observed ≈ 128 WPM, measured, no estimate flag → no raise) — the regression guard for the Sarah bug being fixed.
- [x] `tests/specialists/quinn_r/test_quinn_r_g5_qa_body.py` — add `test_g5_runaway_fast_trips_ceiling` (observed > 200 → raises) + `test_g5_broken_slow_trips_floor` (observed < 110 → raises).
- [x] `tests/specialists/quinn_r/test_quinn_r_g5_qa_body.py` — add `test_g5_operator_break_glass_downgrades_breach` (breach + `wpm_breach_override` → advisory witness, no raise).

**Acceptance Criteria:**
- Given a measured narration cadence of ~128 WPM (Sarah) with no `wpm_durations_estimated` flag, when `run_g5_checks` runs, then it does NOT raise (the band [110, 200] admits it) and `blocking == []`.
- Given a measured observed rate above 200 WPM (runaway TTS), when `run_g5_checks` runs, then `WpmThresholdError` (tag `quinn_r.g5.wpm-threshold`) raises naming the observed rate and the ceiling.
- Given a measured observed rate below 110 WPM (broken-slow), when `run_g5_checks` runs, then `WpmThresholdError` raises naming the observed rate and the floor.
- Given a breach with `wpm_durations_estimated` truthy, when `run_g5_checks` runs, then it does NOT raise (existing advisory escape preserved byte-for-byte).
- Given a breach with `wpm_breach_override` truthy, when `run_g5_checks` runs, then it does NOT raise and `advisory` contains a witness entry `reason == "wpm-breach-operator-override"`.
- Given the unchanged G5 happy-path / dispatch / parity payloads (observed ≈ 120 WPM), when their suites run, then all stay green WITHOUT modification (observed 120 ∈ [110, 200]).
- The floor/ceiling are voice-agnostic module constants (no per-voice table) with a comment citing the §5 ruling.
- **(Explicit, John):** the default (non-override) path STILL RAISES on a breach — the break-glass downgrade fires *only* when `wpm_breach_override` is truthy. This is a testable AC, not prose.

## Party-mode amendments — binding T11 review gates (2026-06-19)

Codex completed T1-T10 against the pre-amendment spec. These five amendments are the **green-light conditions the T11 reviewer (Claude) MUST verify are satisfied** in Codex's diff; any not met is a T11 must-fix.

1. **Refactor safety (Amelia, binding):** the break-glass MUST be implemented by hoisting `advisory = []` to the TOP of `run_g5_checks` and appending the witness only in the override branch — leaving every existing append site (duration-coherence at ~line 157) and the `checks[]` build in place. Do NOT restructure the VTT/coverage ordering to "defer the raise." T11 verifies the happy-path return shape is byte-identical for the 3 do-not-modify payloads.
2. **Boundary tests (Murat + Amelia, binding — kills the `<=`→`<` mutant):** pin `observed == 110` and `observed == 200` → PASS (in-band, inclusive), and `observed == 109` / `observed == 201` → RAISE. Deep-tail values (60 / 400) alone under-verify the edges; the just-inside/just-outside companions are mandatory.
3. **Mutant-proof assertions (Murat + Amelia):** (a) the Sarah-128 guard asserts band-membership *shape* / no-raise, not merely a single sentinel; (b) a **negative-control** test — a breach WITHOUT `wpm_breach_override` → RAISES (kills the "override becomes default" mutant); (c) an **estimate-suppression regression** — a breach WITH `wpm_durations_estimated` truthy → no raise (kills the dropped-escape mutant); (d) the break-glass test asserts the witness is **emitted/logged** (assert by witness *content/membership*, not list index), not merely that the raise is suppressed.
4. **Happy-path shape-pin (Amelia):** at least one assertion that the 3 do-not-modify payloads return `blocking == []` AND `advisory` equal to its pre-change content (no spurious witness) — the regression guard for the reorder.
5. **Repoint integrity (Amelia):** `test_g5_blocking_failures_raise[wpm]` must change the *fixture* to an out-of-band observed rate, not merely the param id.

**§6 DoD gate (Mary/John, binding gating checkbox):**
- [ ] On flip-to-done: **strike/update** the `beta-voice-select-wpm-qa-interaction` entry in `deferred-inventory.md` (mark resolved-by P1) — not "unblocks" in prose.
- [ ] **Harvest** the P1 outcome to `docs/trials/cross-trial-learnings.md` (the "gate asserting the wrong invariant" lesson), with bidirectional citation to the struck inventory entry.

## Review Findings (T11 bmad-code-review, 2026-06-19 — 3-lane: Blind/Edge/Auditor)

**Verdict: PASS** — Acceptance Auditor confirms all 8 ACs + 5 binding T11 gates green. 0 decision-needed, 2 patch, 2 defer, 4 dismissed. No CRITICAL/HIGH genuine defect (Blind's HIGH "fixed band replaces target-relative band" IS the ratified §5 fix).

- [x] [Review][Patch] Stale QA guide band reference [`tests/agents/bmad-agent-quality-reviewer/interaction-test-guide.md`] — updated 130-170 → [110,200]; Scenario-15 example (200 WPM "too fast") corrected to 240 WPM (200 now in-band/inclusive).
- [x] [Review][Patch] §6 DoD governance — struck `beta-voice-select-wpm-qa-interaction` in deferred-inventory + harvested to cross-trial-learnings (bidirectional citation).
- [x] [Review][Defer] Zero-duration→`target_wpm` fallback could mis-gate IF a profile's `target_wpm` were outside [110,200] [`app/specialists/quinn_r/_act.py:153`] — pre-existing line; NOT reachable via dispatch (Edge Case Hunter: `run_g5_grounding` floors durations at `max(1.0, len/14)`; starved rosters raise first); benign at default `target_wpm=150` (in-band). Accepted known-LOW.
- [x] [Review][Defer] `duration-coherence` advisory `slide_id` can be `None` [`_act.py:176`] — pre-existing, cosmetic; no consumer indexes advisory by `slide_id` (verdict stored opaquely).
- Dismissed (4): advisory schema heterogeneity (Edge verified safe — opaque consumer); float-edge brittleness (verified exact 110.0/200.0 IEEE-754); 108/204-vs-109/201 (equivalent mutant coverage); estimated+override combined-case (correct precedence, each path covered).

## Verification

**Commands:**
- `.\.venv\Scripts\python.exe -m pytest tests/specialists/quinn_r/ tests/specialists/test_audio_segment_grounding.py tests/parity/test_quinn_r_activation_contract.py tests/contracts/test_specialist_error_taxonomy.py -q` — expected: all pass incl. new regression twins; the three dispatch/parity payloads green unmodified
- `.\.venv\Scripts\python.exe -m pytest tests/audit/ -q` — expected: pass (taxonomy ratchet unaffected)
- `.\.venv\Scripts\python.exe -m pytest tests/integration/marcus/ -q -p no:randomly` — expected: no new failures vs ambient roster
- `.\.venv\Scripts\python.exe scripts/utilities/check_pipeline_manifest_lockstep.py` — expected: exit 0
- `.\.venv\Scripts\lint-imports.exe` — expected: 13 kept, 0 broken
- `.\.venv\Scripts\ruff.exe check app/specialists/quinn_r/_act.py tests/specialists/quinn_r/test_quinn_r_g5_qa_body.py` — expected: clean

## Spec Change Log

- **2026-06-19 — party-mode §2 green-light (Winston/John/Murat/Mary/Amelia): APPROVE-WITH-AMENDMENTS.** Applied: band-value provenance + n=1/INTERIM/PROVISIONAL floor disclosure + re-validation trigger + ceiling "no-natural-basis" disclosure (§Ratified band values); five binding T11 review gates (refactor-safety, boundary tests, mutant-proof assertions incl. negative-control + estimate-suppression + logged-witness, happy-path shape-pin, repoint integrity); explicit "default still raises" AC; §6 DoD gating checkboxes. Codex had completed T1-T10 against the pre-amendment spec → these are enforced at T11.

## Suggested Review Order

**The new invariant — voice-agnostic band**

- Module constants + citing comment (§5 ruling + Sarah datum + pathological-rate purpose)
  [`_act.py`](../../app/specialists/quinn_r/_act.py)

- Blocking predicate replaced: `not (FLOOR <= observed <= CEILING)`; advisory escape preserved
  [`_act.py:142`](../../app/specialists/quinn_r/_act.py#L142)

- Logged break-glass: explicit-flag-only downgrade to advisory witness (never default)
  [`_act.py:142`](../../app/specialists/quinn_r/_act.py#L142)

**Pins (tests)**

- Regression guard: slow-but-intelligible 128 WPM PASSES (the Sarah bug)
  [`test_quinn_r_g5_qa_body.py`](../../tests/specialists/quinn_r/test_quinn_r_g5_qa_body.py)

- Runaway-fast trips ceiling; broken-slow trips floor
  [`test_quinn_r_g5_qa_body.py`](../../tests/specialists/quinn_r/test_quinn_r_g5_qa_body.py)

- Break-glass downgrades a breach to a logged advisory witness
  [`test_quinn_r_g5_qa_body.py`](../../tests/specialists/quinn_r/test_quinn_r_g5_qa_body.py)
