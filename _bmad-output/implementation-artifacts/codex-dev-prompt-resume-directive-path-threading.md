# Codex Dev Prompt — Resume-Path directive_path Threading (NEW CYCLE)

**You are Codex (T1–T10).** Claude runs T11. Tight cycle. Authority: this prompt + the live trial harvest below. Do NOT relitigate scope.

## The bug (production-real, harvested from a live trial 2026-06-24)
In `production_runner.py`, the **resume walk** loses `directive_path`. At trial start it's known and written to `trial-start.json`, but it is **NOT** carried into the resumable runner/checkpoint state — so on resume `directive_path_raw = runner.get("directive_path")` (~:2064) is `None`. Consequence: `_gamma_settings_from_directive(None)` (:1089) returns nothing, so **Gary's payload never receives the directive's `gamma_settings`**, and Gary single-dispatches default variant A — the operator's treatment/variant config is silently ignored in **every** real run (Gary always runs on a resume). Texas's directive-driven retrieval (:1075) has the same `directive_path`-on-resume gap.

**Live evidence:** trial `08782175-f3eb-4227-ae89-ab368619f408` — `trial-start.json` has `directive_path`; `run.json`/`checkpoint.json` do not (`runner.directive_path = None`). Gary emitted only `A_*` PNGs; the deck-wide filter then correctly fail-loud'd `selected_variant_id='B' matched zero Gary rows`. (The filter + control-layer + injection seam are all CORRECT — do not touch them; this is the upstream wire that feeds them.)

## T1 PRECONDITION (report in Dev Notes)
Confirm: (a) where `directive_path` is (not) persisted between start and resume (trial-start.json vs run.json/checkpoint); (b) the resume read site (`resume_production_trial`/`_continue_production_walk`, ~:2064–2081); (c) the directive is ALWAYS at the canonical path `runs_root / <trial_id> / "directive.yaml"` (the start composes it there); (d) none of the touched files are on `block_mode_trigger_paths` (they aren't).

## The change
Make `directive_path` available on resume. Two layers (do both):
1. **Canonical reconstruction (robust):** at the resume read site, when `runner.get("directive_path")` is falsy, set `directive_path = runs_root / str(trial_id) / "directive.yaml"` **if that file exists** (else None). Deterministic — the directive always lives there.
2. **Persist at source (correct):** carry `directive_path` into the runner/checkpoint state at start (and on each pause) so it round-trips through resume, not just reconstructed.
Both Gary (`_gamma_settings_from_directive`, :1089) and Texas (:1075) then receive a real `directive_path` on resume.

## Tests (RED-first; BINDING)
1. **Real resume path threads gamma_settings (the load-bearing test — "wired ≠ proven"):** start a trial whose `directive.yaml` carries `gamma_settings: [{variant_id:A},{variant_id:B}]`, drive past Gary on the RESUME path (not the payload-builder unit), and assert Gary's payload received the `gamma_settings` (→ both A and B dispatched). RED-first: today the resume yields `directive_path=None` → no gamma_settings → single variant. Pin the RED.
2. **directive_path present on resume:** after a start+pause+resume, assert the resolved `directive_path` is the canonical `runs/<tid>/directive.yaml` (not None), via both the persisted value and the reconstruction fallback (test the fallback by clearing the persisted value).
3. **Legacy byte-identity:** a run with NO `gamma_settings` in the directive is unchanged (Gary single-dispatches as before; no behavior change beyond directive_path now being non-None).

## Fences / governance
Data-plane; `production_runner.py` is NOT on `block_mode_trigger_paths` (the trigger is `workflow_runner.py`); no pack/manifest/lockstep, no new top-level payload key. ruff + lint-imports + focused tests green; baseline-diff attest the ambient contract set is unchanged (zero new reds). Codex T1–T10 → Claude T11.

## Handoff → Claude T11
`_codex-handoff/resume-directive-path-threading-ready-for-review.md`: T1 report; the RED transcript for the resume-threading test; before/after; all 3 test results; baseline-diff attestation; confirmation that Gary (and Texas) receive a real directive_path on resume.

## NOTE
After T11 closes, Claude re-runs a FRESH demo trial — Gary should now dispatch BOTH A and B, the deck-wide filter routes the picked one, and the run completes (or harvests the next real failure). This is the wire that makes the whole variant/treatment capability work in true production runs.
