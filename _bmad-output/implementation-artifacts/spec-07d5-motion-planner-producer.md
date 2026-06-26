# Spec — 07D.5 Motion-Plan Producer Node (composition-catalog B2)

**Status:** ready-for-dev (NEW CYCLE: dev T1–T10 → Claude T11 → live segment run → party verification)
**Class:** S (substrate — pipeline-manifest topology + new specialist + composer fragment). Tier-2 *within-lineage* topology refinement (witness-regen, NOT a v4.3 file — see §Pack Version).
**Branch:** `fidelity-perception-arc-2026-06-19`
**Party green-light:** GREEN-WITH-AMENDMENTS 4/4 (Winston/Murat/John/Amelia), no impasse, 2026-06-26. Amendments A–J below are binding.

## 1. Goal & scope

Build the missing in-graph **motion-plan producer** so a COMPOSED B2 (deck+motion) run **self-feeds** kira's 07E a real `motion_plan` instead of a hand-set `KIRA_MOTION_PLAN_PATH` env seed. Today kira (07E) is `wired` and live-proven (3 real Kling `.mp4`s across 3 models, 2026-06-26), but nothing produces its plan.

**In scope:** a new deterministic `motion_planner` specialist node `07D.5` between 07D and 07E; rewire 07E to consume its `motion_plan` projection; register it in the composer's `motion` component; regenerate the determinism witness; RED-first tests; absorb the live-found Kling fixes + wire the kling-video registry/sample library.

**Out of scope (deferred, named follow-ons):** LLM-authored "smart" motion direction (John's stop-the-line — the producer is DETERMINISTIC); per-slide motion A/B; a full G0→done pipeline run (we run *just the motion segment*).

## 2. Design — deterministic ADAPTER over the existing Epic-14 engine + library

The producer is **deterministic, NO LLM in the critical path** (John + Amelia + Murat) and **REUSES existing stockpile code** (operator directive) rather than reinventing:

**Reuse (the deterministic core):** `skills/production-coordination/scripts/motion_plan.py` (Epic 14):
- `build_motion_plan_from_authorized_storyboard(authorized_storyboard, motion_enabled, motion_budget)` → per-slide deterministic recommendation engine (`_build_recommendation`: fidelity + content-cue scoring → static/video/animation + rationale + confidence + `motion_brief`/`guidance_notes` + credits). NO LLM.
- `apply_motion_designations(motion_plan, designations)` → applies the Gate-2M choices.
- `scripts/utilities/motion_budgeting.py` → deterministic credit/cost estimate.

**The 07D.5 node is a thin ADAPTER:** (1) build the Epic-14 plan from the authorized storyboard; (2) apply the 07D designation (or auto-designate the engine's recommended video/animation slides for a no-HIL segment run); (3) **project the video-designated rows into kira's `motion_plan` shape**, sourcing the `motion_prompt` from the Epic-14 `motion_brief`/`guidance_notes` **fused with a proven `skills/kling-video/references/video-style-catalog.yaml` `prompt_template`**, the `model_name` from `model-capabilities.yaml` (a CURRENTLY-VALID id — not the stale `kling-v2-6`), and `estimated_cost_usd` from the budgeter. This is how determinism + client-facing quality + library-reuse reconcile.

**Producer emits** (kira `payload_contract.CONSUMED_PAYLOAD_KEYS` reserves `motion_plan`):
```
motion_plan = {"slides": [
  {"slide_id": <video-designated slide>, "model_name": <valid id from model-capabilities>,
   "duration": "5", "aspect_ratio": "16:9", "mode": "std",
   "motion_prompt": <Epic-14 motion_brief fused with a video-style-catalog prompt_template>,
   "image_url": <slide image if image2video; else omit for text2video>,
   "estimated_cost_usd": <from motion_budgeting>, "style_id": <catalog style chosen deterministically>}
] }
```
- Emits ONLY video/animation-designated slides, **sorted by `slide_id`** (amendment F). `est_cost` excluded-from / quantized-in the witness comparison (amendment F).
- **Operation choice:** prefer **image2video** of the approved slide PNG (library "production-safe default" → best client-facing quality) when a slide image is available; fall back to **text2video** (live-proven 2026-06-26). Both supported.

**RATIFIED behavior (Murat C2, 2026-06-26):** the AUTO recommendation path is **intentionally conservative** — the Epic-14 engine errs toward `static` and only designates `video`/`animation` when slide content carries strong scene/process cues. A deck the engine scores all-static yields an empty plan by design; the operator's **07D Gate-2M designation is the override** that adds motion. This is intended, not a producer defect (proven both ways: `test_auto_designation_recommends_motion_without_an_explicit_designation` shows AUTO firing on motion-worthy slides; the live 6a103b6c deck scored all-static → operator designation supplied).

**07D output shape (RESOLVED):** 07D "Gate 2M Motion Designation" is a marcus **gate** (HIL), not a structured producer — there is no orchestrator code emitting designated-slides today (grep clean). The designation is the `apply_motion_designations` **`designations` dict** (`{slide_id: {motion_type, motion_brief, ...}}`). For the live SEGMENT run, the producer **auto-designates from the Epic-14 recommendations** (deterministic) so no HIL is required; a provided designation overrides. The producer reads the **authorized storyboard** (winner deck) + optional perception; it does NOT depend on a structured 07D artifact that doesn't exist.

## 3. Absorbed fixes (live-found 2026-06-26, fold into this story with RED-first tests)

1. **`sound` fix (already applied to `app/specialists/kira/_act.py`)** — only send `sound` when a slide explicitly enables native audio; the former unconditional `"sound": false` is rejected by Kling (HTTP 400 code=1201). Add the RED-first test pinning "`sound` absent from the request unless explicitly enabled" (mirror the old skill's `assert "sound" not in kwargs`).
2. **Default model fix** — `_call_generate_motion` default `model_name="kling-v2-6"` is "model is not supported" on the account; change the default to a valid id sourced from the library SSOT (`kling-v1-6` proven). Better: the producer always emits an explicit valid `model_name`, so the default is a fallback only — still fix it.
3. **Library wiring (operator binding directive)** — the producer consumes `skills/kling-video/references/` as SSOT: `video-style-catalog.yaml` (prompt templates), `model-capabilities.yaml`/`model-feature-matrix.md` (valid model ids + per-model constraints), and writes receipts to the `receipt-contract.md` shape. Refresh the matrix's valid-id set (it's stale since 2026-04-07; v2-6 deprecated; current valid: `kling-v1-6`/`kling-v2-1-master`/`kling-v2-master`/`kling-v1`). `<<MAP: confirm library schemas — fill from surface map item 5>>`

## 4. Manifest changes (`state/config/pipeline-manifest.yaml`)

**Add node 07D.5** (modeled on 07G/vision — the within-lineage producer precedent):
```yaml
  - id: "07D.5"
    label: "Motion Planning"
    specialist_id: "motion_planner"     # <<MAP: confirm canonical id form vs dispatch-registry>>
    scaffold_node: "act"
    model_config_ref: null               # deterministic, NO LLM
    dependencies:
      upstream_output: "quinn_r"          # reads the authorized winner deck (the
                                          # storyboard) — exactly what kira's old
                                          # tolerated edge pointed at; it moves UP
                                          # one level to the producer.
    gate: false
    sub_phase_of: "07"
    insertion_after: "07D"
    hud_tracked: true
    pack_section_anchor: "7D5)"
    pack_version: "v4.2"
    rationale: >-
      Deterministic motion-plan producer. The motion_plan it emits is an internal
      producer→consumer envelope consumed by kira (07E), not a learner-facing
      pack-lineage deliverable, so this is a topology refinement within the v4.2
      lineage (mirrors 07G). The generated -gen witness regenerates; frozen v4.2
      is untouched.
```
**Rewire 07E** — replace `dependencies: {upstream_output: quinn_r}` with a projection reading the producer's `motion_plan` (amendment C: remove the tolerated quinn_r edge entirely; single declared source; fail-closed):
```yaml
    dependency_projections:
      motion_plan:
        from: motion_planner          # <<MAP: confirm projection form>>
        key: motion_plan
```
**Edges** — replace `{from: "07D", to: "07E"}` with `{from: "07D", to: "07D.5"}` + `{from: "07D.5", to: "07E"}`. Verify the sort key handles `"07D.5"` between `07D` and `07E` (amendment G — no float-parse).

## 5. Composer change (`app/marcus/lesson_plan/composition.py`)

Add `"07D.5"` to the **`motion` `ComponentFragment.manifest_node_ids`** (currently `frozenset({"07D","07E","07F"})` → add `"07D.5"`). This puts 07D.5 in the motion prune-group, so deselecting motion drops all four as a unit and **deck-default stays a byte-identical no-op** (`compose_manifest` early-return, composition.py:380). The producer→consumer edge (07D.5→07E) is **intra-component** (both in `motion`), so no `OPTIONAL_PROJECTION_KEYS` entry is needed.

## 6. Pack version (Murat-adjudicated: within-lineage witness regen)

NOT a literal v4.3. Keep `pack_version` UNIFORM across all nodes (amendment E — the single-value `step.pack_version in (None, active)` filter silently drops a half-flipped node). Regenerate the `-gen` determinism witness only; frozen v4.2 mapping-axis untouched. **RESOLVED paths/commands:**
- Witness (determinism-target, regenerate): `docs/workflow/production-prompt-pack-v4.2-gen-narrated-lesson-with-video-or-animation.md`
- Frozen mapping-axis (NEVER touch; sha `dcb8b8…`): `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`
- production-canonical v5 (hand-authored, `generated:false`, sha `dde6df…`; NEVER machine-regenerate): `docs/workflow/production-prompt-pack-v5-…md`
- Regen: `.venv/Scripts/python.exe -m scripts.generators.v42.render --manifest state/config/pipeline-manifest.yaml --output docs/workflow/production-prompt-pack-v4.2-gen-narrated-lesson-with-video-or-animation.md`
- L1: `.venv/Scripts/python.exe scripts/utilities/check_pipeline_manifest_lockstep.py` (assert exit 0; check 9 witness↔manifest + check 10 frozen-SHAs intact)
- **Mirror node 07G/vision end-to-end** for the pack-section/template + witness mechanics (it is the in-lineage producer precedent with `pack_section_anchor`).

L1 checks 9 AND 10 must both be green in the SAME commit. Manifest + templates + regenerated witness + composer + producer + tests + dispatch-registry + specialist-registry land as ONE commit.

**Registration (resolved):** add `motion_planner: app.specialists.motion_planner.graph:build_motion_planner_graph` to `state/config/dispatch-registry.yaml::specialists`; add a `motion_planner` row to `skills/bmad-agent-marcus/references/specialist-registry.yaml` (deterministic producer — minimal row; update kira's role from "motion-plan + Kling video generation (§07D/§07E)" to "Kling video generation (§07E)"); regenerate `state/config/capability-overlay.yaml` (`.venv/Scripts/python.exe scripts/utilities/generate_capability_overlay.py`) so motion_planner shows `wired`.

## 7. Binding amendments (party A–J)

- **A.** Producer is DETERMINISTIC — no model client touched (pin as a test invariant, not a comment).
- **B.** Reads 07D's designated-slide output + perception; does NOT re-run designation; emits ONLY designated slides; kira treats the projection as authoritative slide set.
- **C.** Legacy `upstream_output: quinn_r` on 07E fully REMOVED; single motion source; fail-closed (no plan → kira errors, never degrades).
- **D.** Composer prune test: motion deselected ⇒ 07D/07D.5/07E/07F all absent AND deck-default byte/hash-identical to the B1 baseline.
- **E.** pack_version uniformity assertion (RED-first half-flip guard) + L1 checks 9 & 10 green in one CI run; all changes ONE commit.
- **F.** Slides emitted in deterministic sorted order; `est_cost` deterministic, excluded-from/quantized-in the witness comparison.
- **G.** 07D.5 numbering verified against the runner's actual node sort (no float-parse of "07D.5").
- **H.** **Two-walk wiring** (`[[project_production_runner_two_walks]]`): the 07D.5 edge + any gate-pause side-effect wired into BOTH the start and continuation walks; the live segment test must traverse the **continuation** walk, not just a fresh start.
- **I.** kira `_act` normalizes `{motion_plan dict, motion_plan_path file}` into one internal plan object; ingestion-equivalence test gates retiring the `production_runner` env-seed shim (keep `motion_plan_path` as explicit dev/replay override).
- **J.** Pre-run sanity: confirm the compositor/kira render a coherent clip from a library-templated directive before locking "minimal."

## 8. RED-first test floors (minimum)

1. **Producer determinism** — same 07D designation + perception in → exact `motion_plan` out; one row per designated slide; library-sourced prompt + valid model; **no LLM client touched** (assert model client never called).
2. **Contract satisfaction** — emitted `motion_plan` passes kira `payload_contract` for the reserved `motion_plan` key.
3. **Composer prune symmetry** (amendment D) — deselect motion → 07D/07D.5/07E/07F absent; deck-default byte-identical to B1 baseline.
4. **kira ingestion equivalence** (amendment I) — dict-fed == path-fed internal plan object.
5. **07E edge rewire** — kira resolves motion source from the projection ONLY; quinn_r tolerance gone; dual-source fails-closed.
6. **`sound` omitted** (absorbed fix 1) — request has no `sound` unless explicitly enabled.
7. **pack_version uniformity** (amendment E) — all nodes share one pack_version; half-flip fails RED.
8. **L1 lockstep** checks 9 + 10 green; **continuation-walk** segment test (amendment H).

## 9. Definition of done (goal gate)

A **live composed motion-segment run** (07D designation → 07D.5 producer → 07E kira → real Kling video, with logs) completes, and a **fully-spawned tailored party-mode team reviews the results + logs** and verifies: (a) the resulting video is **production / client-facing quality**, and (b) the **routine executed per spec**. Until the party confirms both, NOT done.

## 10. Surface-map fill-ins (ALL RESOLVED)
- **Scaffold:** 9-node scaffold (`app/specialists/_scaffold/contract.py`). Deterministic producer mirrors **kira**'s pattern — `plan()` records the model-resolution trail via `make_chat_model(...)` but does NOT call it; `act()` is pure deterministic. Files: `app/specialists/motion_planner/{__init__,graph,state,_act,payload_contract,model_config.yaml,config.yaml}`. `state.py` Envelope+Return with `_SPECIALIST_ID="motion_planner"` pin. `model_config.yaml` records a default model for trail uniformity (never invoked).
- **07D output:** RESOLVED in §2 — 07D is an HIL gate, not a structured producer; the producer auto-designates deterministically from the Epic-14 engine over the authorized winner deck (read via `upstream_output: quinn_r`).
- **Deterministic core (REUSE):** `skills/production-coordination/scripts/motion_plan.py` (`build_motion_plan_from_authorized_storyboard`, `apply_motion_designations`, `_build_recommendation`) + `scripts/utilities/motion_budgeting.py`. The node ADAPTS its output into kira's `motion_plan` shape (§2).
- **Library schemas:** `video-style-catalog.yaml` (style_id, operation, model, mode, duration, prompt_template, tags) → prompt source; `model-capabilities.yaml` (per-model support/durations/audio) → valid model id + constraints; `validation-cases.yaml` → known-good config validation. Deterministic selection (no LLM): map slide fidelity/cue → a catalog style_id (stable default acceptable), fill prompt_template with the Epic-14 motion_brief, pick a currently-valid model id.
- **Witness/L1/registration:** RESOLVED in §6 (paths, regen + L1 commands, dispatch/specialist registry + overlay regen). Mirror node 07G/vision.
- **Regression surface (tests to keep green):** `tests/test_integration_kira_motion.py`, `tests/test_motion_pipeline_integration.py`, `tests/composition/test_kira_to_compositor_chain.py`, `tests/specialists/kira/test_kira_motion_generation.py`, `tests/specialists/kira/test_kira_motion_plan_fail_loud.py`, `tests/parity/test_kira_activation_contract.py`, `tests/contracts/test_ratchet_d_projection_vocabulary.py` (the new 07D.5 must declare `CONSUMED_PAYLOAD_KEYS` matching its projected inputs).
- **Landmines:** two-walk (amendment H); ComponentSelection must rehydrate on resume (never re-default); frozen-SHA check 10 (never touch v4.2/v5 packs); composer fail-closed; Ratchet-D vocabulary sync.
