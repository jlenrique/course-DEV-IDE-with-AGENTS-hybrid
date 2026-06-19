# Codex dev-story prompt — P1 (G5 WPM check → voice-agnostic intelligibility band)

**Cycle:** Claude spec (LOCKED 2026-06-19) → Codex T1-T9 + T10 self-review → Codex handoff at `_bmad-output/implementation-artifacts/_codex-handoff/p1-voice-agnostic-wpm-floor.ready-for-review.md` → Claude T11 `bmad-code-review` → Claude commit + flip done.
**Workflow:** `bmad-quick-dev` · **gate-mode:** single · **K-target:** small (~1 source file + 1 test file; estimate <150 LOC).
**Authority:** `_bmad-output/planning-artifacts/beta-phase-1-closure-ratification-2026-06-19.md §5` (Murat ruling, operator-ratified). The design is LOCKED — do not re-litigate floor/ceiling values or re-introduce a per-voice table.

---

```
Run bmad-quick-dev on P1 (voice-agnostic G5 WPM intelligibility band; single-gate).

Spec: `_bmad-output/implementation-artifacts/spec-p1-voice-agnostic-wpm-floor.md`
The spec's <frozen-after-approval> Intent / Boundaries / Edge-Case Matrix / Ratified band values are CONTRACT. Honor them verbatim.

## Required reading (T1, before any code)

1. The spec (whole file), especially "Ratified band values" and the I/O & Edge-Case Matrix.
2. `_bmad-output/planning-artifacts/beta-phase-1-closure-ratification-2026-06-19.md` §5 (WPM ruling) — the WHY.
3. `app/specialists/quinn_r/_act.py:134-163` — `run_g5_checks`. The exact lines you change.
4. `app/specialists/quinn_r/quality_control_dispatch.py:17-35` — how `WpmThresholdError` is built (dual base `SpecialistDispatchError, ValueError`; tag `quinn_r.g5.wpm-threshold`). Do NOT change the error class.
5. `app/specialists/quinn_r/graph.py:299-303` — the re-exports the tests import through. Verify intact; do not break them.
6. `tests/specialists/quinn_r/test_quinn_r_g5_qa_body.py` — the test you edit + extend.

## T1 hard checkpoints

- Baseline commit `78c8753` is an ancestor of HEAD; branch is `fidelity-perception-arc-2026-06-19`.
- `run_g5_checks` blocking predicate today is exactly `if abs(observed - target_wpm) > tolerance and not payload.get("wpm_durations_estimated"):` (`_act.py:142`).
- The spec path `app/specialists/quinn_r/_act.py` is NOT on `state/config/pipeline-manifest.yaml::block_mode_trigger_paths` (confirm via grep; if it IS, STOP and surface — the pipeline-lockstep regime would apply).
- Confirm the three "no change expected" payloads each produce observed ≈ 120 WPM (in-band): run those suites green BEFORE your edit as the pre-change baseline.

## Files in scope

**Modified:**
- `app/specialists/quinn_r/_act.py` — the band logic (see "Implementation notes").
- `tests/specialists/quinn_r/test_quinn_r_g5_qa_body.py` — repoint the wpm mutation case + add 4 regression twins.

**Do NOT modify:**
- `app/specialists/quinn_r/quality_control_dispatch.py` (error class — READ ONLY).
- `app/specialists/quinn_r/graph.py` (re-exports — READ ONLY; verify intact).
- `tests/specialists/test_audio_segment_grounding.py`, `tests/specialists/quinn_r/test_quinn_r_two_mode_dispatch.py`, `tests/specialists/quinn_r/test_quinn_r_act_node_dispatch.py`, `tests/parity/test_quinn_r_activation_contract.py`, `tests/contracts/test_specialist_error_taxonomy.py` — these MUST stay green WITHOUT edits. If any goes red, you changed behavior you should not have — STOP and surface.
- Any `target_wpm` consumer outside Quinn-R (`scripts/utilities/slide_count_runtime_estimator.py`, `skills/bmad-agent-marcus/scripts/generate-storyboard.py`, `.../validate-irene-pass2-handoff.py`).

## Critical implementation notes

- **Add two module-level constants** near the top of `_act.py` (after imports), with a comment block citing `beta-phase-1-closure-ratification-2026-06-19.md §5`, the Sarah-128-WPM-measured-2026-06-19 datum, and the gate's purpose (catch PATHOLOGICAL rate — runaway-fast/broken-slow — not natural cadence):
  - `WPM_INTELLIGIBILITY_FLOOR = 110.0`
  - `WPM_INTELLIGIBILITY_CEILING = 200.0`
- **Replace the blocking predicate.** The new blocking condition is `not (WPM_INTELLIGIBILITY_FLOOR <= observed <= WPM_INTELLIGIBILITY_CEILING)`. PRESERVE the `and not payload.get("wpm_durations_estimated")` clause verbatim (estimated durations remain advisory — Winston's self-referential note). The `WpmThresholdError` message must name the observed rate AND which bound it breached (floor vs ceiling), e.g. `f"WPM {observed:.1f} below intelligibility floor {WPM_INTELLIGIBILITY_FLOOR:.0f}"` / `f"...above ceiling {WPM_INTELLIGIBILITY_CEILING:.0f}"`.
- **`target_wpm` / `tolerance` no longer gate.** You may keep reading them (harmless / message parity) or drop them from `run_g5_checks` — your call, but do NOT remove them from the YAML or other consumers. If you drop the local reads, ruff must stay clean (no unused vars).
- **Logged break-glass override (ratified, never-default).** Before raising on a real breach, check `payload.get("wpm_breach_override")`. If truthy: do NOT raise; instead append to the `advisory` list a witness dict `{"reason": "wpm-breach-operator-override", "observed_wpm": round(observed, 1), "floor": WPM_INTELLIGIBILITY_FLOOR, "ceiling": WPM_INTELLIGIBILITY_CEILING}`. This is the ONLY override path — it requires the explicit flag; the default path still raises. Note the `advisory` list is built later in the function (line ~157); structure your code so the override witness reaches it (e.g., compute the breach early, defer the raise/advisory decision, or initialize `advisory` before the WPM check). Keep the diff clean and readable.
- **Test edits:**
  - Repoint `test_g5_blocking_failures_raise[wpm]`: the current mutation `payload["narration_profile_controls"]["target_wpm"] = 60` will NO LONGER trip (observed 120 ∈ band). Instead drive observed out of band — e.g., set the two segments' `duration_seconds` to make total observed > 200 (shrink duration) or < 110 (grow duration). Keep it raising `WpmThresholdError`.
  - Add `test_g5_slow_but_intelligible_voice_passes`: construct a measured payload (NO `wpm_durations_estimated`) whose observed ≈ 128 WPM (e.g., 32 words over 15s). Assert `run_g5_checks` returns with `blocking == []` and does NOT raise. This is the Sarah regression guard — the actual bug.
  - Add `test_g5_runaway_fast_trips_ceiling` (observed > 200 → raises `WpmThresholdError`) and `test_g5_broken_slow_trips_floor` (observed < 110 → raises).
  - Add `test_g5_operator_break_glass_downgrades_breach`: a breaching payload + `wpm_breach_override: True` → no raise, and `advisory` contains an entry with `reason == "wpm-breach-operator-override"`.
- **Watch the happy-path payload:** `_payload()` in the test file yields 20 words / 10s = 120 WPM, which stays in-band — the existing happy-path + duration-advisory tests stay green unmodified. Confirm.

## T9 self-G6 + T10 ready-for-review handoff (standard pattern)

Run the full Verification command block from the spec. In the handoff note record: the observed-WPM for each new test, confirmation the 5 do-not-modify test files stayed green unmodified, lint-imports (13/0), ruff clean, and lockstep exit 0.

## Cycle-close discipline

After Claude T11 commits + flips done: per the ratification DoD gate (Mary, binding), the closer strikes/updates the `beta-voice-select-wpm-qa-interaction` deferred-inventory entry and harvests any cross-trial learning. P1 runs in parallel with the P2 detector arc — no dispatch dependency.
```

---

**Authored 2026-06-19 by Claude orchestrator. Ready for Codex dispatch (no predecessor dependency — P1 is parallel to P2).**
