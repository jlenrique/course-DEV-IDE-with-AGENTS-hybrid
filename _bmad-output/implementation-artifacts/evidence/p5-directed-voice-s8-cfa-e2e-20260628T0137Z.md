# P5 directed-voice — Step 8 CF-A true E2E through `production_runner` (continuation walk)

Date: 2026-06-28 (UTC). Validation agent run. **No git commit. No vision tests. No fixtures mutated.**
Live legs: real gpt-5 (`make_chat_model("marcus")`) + real scite (OAuth, `secrets/scite_oauth_token.json`).
Runs root (scratchpad, disposable): `…/scratchpad/p5s8-runs/`. Harness: `…/scratchpad/p5s8_cfa_e2e.py`.
Corpus (purpose-built, disposable): `C:\tmp\p5s8-cfa-corpus\source-outline.md` (clean `### Slide 1/3/6`
grounded narration; resolvable JAMA DOI; deliberate fail-probe DOI; non-narration A4 ungrounded probes).

## STEP-0 — the real run path that was driven

The CF-A path is the **two-walk** `production_runner` flow, not staged fixtures:

- **START walk** — `production_runner.run_production_trial(corpus, …, component_selection=deck+motion+workbook)`.
  With `MARCUS_G0_ENRICHMENT_ACTIVE=1` + `MARCUS_G0_DISPATCH_LIVE=1` + a real key, the `g0-enrichment`
  orchestration node fires `g0_enrichment_wiring.run_g0_enrichment` → **`build_enrichment_result(dispatch_live=True)`
  in ONE process** (P1 component extraction → P2 Texas pass-0 live scite citation resolution → P3 pedagogy
  annotation), freezes `<run_dir>/g0-enrichment.json` (+ corpus-fingerprint cache), and pauses at gate **G0E**.
- **CONTINUATION walk** — `production_runner.resume_production_trial(G0E approve verdict)` →
  `_continue_production_walk` (the same body `recover_production_trial` uses). Driven per-gate
  (approve verdict built from each `decision-card-<gate>.json`) through **G0E→G0R→G1→G2B→G2C→G3→G4→G4A→completed**.
  The P5 consumers fire on THIS walk: the irene **node 08** narration payload gets the role-derived
  voice seed via `production_runner._runner_payload_for_specialist` (irene branch reads
  `g0_enrichment_wiring.load_enrichment_result(run_dir)` → `enrichment_consumption.project_role_derived_voice_by_slide`),
  and the **07W** `workbook_producer` node (composed in because `workbook=True`) is reached.

Scope note (disclosed, honest): specialist **bodies** that call external APIs (Gamma / Kling / ElevenLabs)
were replaced by a deterministic **recording dispatch adapter** — the deliverable is METADATA preservation, not
deck/audio synthesis, and **ElevenLabs is in a rate-limit cooldown** (audio leg skipped, see below). The runner's
**continuation-walk code ran for real**: gate machinery, two-walk `component_selection` rehydration,
`g0-enrichment.json` threading, and the `_runner_payload_for_specialist` voice-seed projection. Out-of-scope
branches patched to no-op/passthrough (each is NOT the P5 metadata path): pre-gate-marcus draft,
storyboard/chooser review-surface publish, §06 Gary-brief package builder, research-wiring fetch, the G0R
irene-refinement (G0-S3 LO pass), and trial-economics cost recording (the stub model has no pricing row).

## Binding P2 conditions — DISCHARGED on one live `build_enrichment_result` output

`p2-condition1-wired-live-run` + `p2-condition3-live-a4` (deferred-inventory, Murat BINDING).

**Trial `0118a772-aeb7-4467-9a57-5c40d68b7d6b`** (`run_g0_enrichment` START walk, live; 133.4 s; model_id=`marcus`,
corpus_fp `b5518e054f19`). The single live output shows **resolved AND failed AND ungrounded together**:

- **P2-cond1 (resolved + failed in ONE live output): PASS.**
  - `resolved` — `src-001-c009`, DOI `10.1001/jama.2019.13978` (JAMA waste study) → live scite dereference returned a hit.
  - `failed` — `src-001-c012`, DOI `10.9999/jihs.2099.deadbeef` (deliberate fail-probe) → live scite returned no hit.
- **P2-cond3 (A4 ungrounded path on live output): PASS.** `reconcile.n_ungrounded=1`, 1 `flagged_ungrounded`
  component: `src-001-c003` (`Course 1, Module 1 > Learning Objectives > Course Goal`) — the live model dropped
  the raw `***…***` markdown markers when it "quoted", so its excerpt is not a verbatim substring after
  md-normalization → `flag_ungrounded_components` flagged it (live log line emitted:
  `g0-enrichment: component 'src-001-c003' excerpt is NOT grounded in parent 'src-001' after markdown normalization`).
- **Real provider request evidence (scite):** 2 live `retrieval.dispatcher.dispatch` calls captured, both
  `provider='scite'` with DOI-dereference params — `{'mode':'search','dois':['10.1001/jama.2019.13978'],'max_results':1}`
  and `{… 'dois':['10.9999/jihs.2099.deadbeef'] …}`. The resolution split (JAMA→resolved, deadbeef→failed) is the
  authoritative outcome evidence; DOI-less citations fail without a scite call (resolver only dispatches on a parseable DOI).

Corroboration — trial `394ce491-2f70-427c-aa45-717ff3a6d361` (earlier live START walk) independently produced
`resolved=1 (JAMA), failed=8, reconcile.n_ungrounded=2` (`src-001-c001` + `src-001-c024`), incl. a citation-level
`resolution_status='ungrounded'` with the live pass0 log
`pass0: component 'src-001-c024' excerpt is NOT grounded in its parent source (A4); marking ungrounded, not resolving a DOI off it`.

## Continuation-walk metadata preservation — DISCHARGED

**Trial `8a997d43-8f9c-4b2e-a8ae-1e7fb883f78b`** (START + full CONTINUATION walk, live; START 128.1 s).
Per-gate approve loop walked **G0E→G0R→G1→G2B→G2C→G3→G4→G4A→`completed`** (8 real `_continue_production_walk`
segments); nodes dispatched on the continuation walk:
`02,03,04A,4.75,05,05B,07,7.5,07B,07D.5,07E,07F,07G,08,08B,11,11B,12,13,14,14.5,07W`.

| Assertion | Where checked | Result |
|---|---|---|
| **Enrichment preserved** — `g0-enrichment.json` present + **byte-identical** (sha before==after) through the walk | run_dir on disk | **PASS** |
| Enrichment contribution carried | `resumed.production_envelope.get_contribution("g0_enrichment", node_id="g0-enrichment")` | **PASS** (not None) |
| **Two-walk selection rehydrated, not re-defaulted** | `resume-command.json::run_state.component_selection` | **PASS** = `{deck:true, motion:true, workbook:true}` (the NON-default selection survived) |
| **voice_direction metadata projected on the continuation walk** | recorded `runner_supplied_payload` at irene **node 08** | **PASS** — `role_derived_voice_by_slide = {by_slide:{"1":{pace:neutral},"3":{pace:slower},"6":{pace:slower}}, source_slide_ordinals:[1,3,6]}` |
| Voice seed **matches the live enrichment** | `project_role_derived_voice_by_slide(g0-enrichment.json)` vs projected payload | **PASS** (identical) |
| **`run_g0_enrichment → 07W`** — workbook consumer reached on the continuation walk | recorded node `07W` dispatch | **PASS** |

The voice_direction role-seed (slides 1/3/6, pace per pedagogical role) was produced by the live P3 pedagogy
annotation, frozen in `g0-enrichment.json` on the START walk, and **threaded onto irene node 08 on the CONTINUATION
walk** — the exact "metadata survives the second walk" property the standing two-walk gotcha breaks.

## Honest notes / limitations

- **Single-run all-in-one is gated by the known EDGE-1 narration-locator fragility**
  (`p5-s2-role-seed-robust-source-to-final-slide-linkage`, deferred). `slide_ordinal_from_locator` requires the
  narration component's locator terminal segment to be **exactly `Slide N`**; the live model non-deterministically
  appends `> Narration` (~half of runs across 5 live runs), in which case the runner **correctly** projects a
  fail-safe `None` (no mis-seed). Voice-seed projection is therefore proven on trial `8a99…`; the binding P2
  ungrounded leg is proven on trials `0118…`/`394…`. Both are the SAME real `production_runner` START+continuation
  flow on the same corpus family — they did not co-occur in one run only because the two model-variance points
  (ungrounded trigger AND `Slide N` locator suffix) did not both land in a single sampling. No criterion is
  unproven; the runner code is correct in every case.
- **ElevenLabs audio synthesis NOT run** — out of scope for a metadata proof and ElevenLabs is in a rate-limit
  cooldown. The continuation walk's enrique/elevenlabs node bodies were recorded by the stub adapter; no audio
  was synthesized. Recorded honestly per instructions.
- **No failed-attempt-free blocker claims:** gpt-5 and scite were both live and responsive on every run (5/5
  START walks completed the live enrichment; 2/2 scite DOI dereferences per run).
- **No vision tests executed; `tests/fixtures/vision/recordings/` untouched; no git commit.** Only scratchpad,
  `C:\tmp\p5s8-cfa-corpus`, and this evidence file were written.

## Artifacts (scratchpad, disposable)

- Harness: `…/scratchpad/p5s8_cfa_e2e.py`
- Per-run machine-readable results: `…/scratchpad/p5s8-runs/p5s8-cfa-result-*.json`
  (voice proof: `…012036Z.json` = trial 8a99; P2 proof: `…013347Z.json` = trial 0118)
- Live run dirs (g0-enrichment.json, decision cards, checkpoints, run.json): `…/scratchpad/p5s8-runs/<trial_id>/`
