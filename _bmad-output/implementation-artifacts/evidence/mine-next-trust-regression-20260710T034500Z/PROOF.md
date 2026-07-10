# PROOF — Trust-hardening regression gate (pre-E2E)

**Stamp:** 2026-07-10T03:45:00Z (approx; local session)  
**Branch:** `dev/lesson-planning-2026-07-09`  
**Python:** `.venv` 3.12.13  
**Purpose:** Full regression before trust E2E / fresh-asset validation.

## Suites

| Lane | Result | Notes |
|------|--------|-------|
| Trust-hardening targeted (post-fix) | **92 passed** | fidelity + join + recover + UDAC + storyboard voice + figure_tokens + dispatch retry + CD projection |
| `trial_critical` | **159 passed**, 2 xfailed | pre-trial confidence bar |
| Marcus + specialists subset | **3164 passed**, 4 failed ambient | see ambient list |
| Default full suite (`not live/serial/quarantined`) | **7435 passed**, 83 failed | mostly ambient pin/lockstep/replay; 4 trust-caused fixed below |
| `serial` | 1 passed, 1 failed ambient | `marcus.facade` ModuleNotFoundError (legacy path) |

## Trust-caused failures found + fixed in this gate

1. **T3 join-collapse** — `test_duplicate_id_deltas_do_not_misroute_voice_direction` now expects fail-loud `storyboard.join.collapsed-segment-ids` (was last-write-wins withhold).
2. **T4a figure_tokens `__all__`** — frozen-neck audit accepts additive `PERCENT_TOLERANCE_PP` / `_figure_near_match` while requiring original trio ⊆ `__all__`.
3. **Dispatch retry pin** — `gamma.export.brief-unmatched` is intentionally retryable; non-retryable case uses `cd.directive.malformed`; added positive retryability test.
4. **`SpecialistDispatchError` UnboundLocalError** — removed shadowed local re-import inside `_runner_payload_for_specialist` irene-pass1 branch (broke CD directive raise sites).

## Ambient failures (NOT introduced by trust batch; still fail with trust diffs stashed)

Examples: schema pins, HUD rename, WAVE_LABELS, sanctum/pack replay fingerprints, import-linter Windows cp1252, `test_pass_2_template_strict` golden schema lockstep, `specialist_roster_count` 17≠12, TW-7c-4 audit scope, etc.

## Gate verdict for E2E proceed

**GO for trust-hardening E2E** on the claim envelope (Wave 1 + T4a/T4b/T4c fidelity path), with ambient full-suite debt fenced as out-of-scope for this batch.  
Do **not** claim repo-wide green.
