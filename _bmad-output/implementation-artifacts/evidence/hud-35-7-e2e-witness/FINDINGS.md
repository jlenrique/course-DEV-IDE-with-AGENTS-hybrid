# 35.7 Live E2E Witness — Findings (first live integration of the HUD stack)

Trial: 69338610-23bc-4889-9bfb-fb64f0142a95 · corpus tejal-c1m1-p4-assessments-bridge · narrated-deck-with-workbook · realtime · --hud on

## WORKING LIVE (witnessed)
- Pre-flight: all 10 items pass incl. live OpenAI + Gamma heartbeats (FR1/FR2). Projection preflight section populated.
- Assembler emits the projection live during the walk (seq/progress_seq advancing) — FIRST live integration of the emission seam (35.2).
- Zero-lie: projection envelope status == run.json status (paused-at-gate/G0E) — Murat item 4.
- HUD server (35.4) serves live: /healthz 200 {trial_id,nonce,mode}; /projection 200 ETag "v1:38"; If-None-Match -> 304; / -> 200 55KB.
- Render (35.5/35.9) live: page shows PAUSED AT GATE, G0E, gate_focus source_enrichment, operator_prompt, the command block. decision_card section populated (35.9 FR4) — gate_focus + operator_prompt rendered.

## FINDINGS (logged per amendment 9; first-run-stands; NOT fixed mid-run)
- **F-E2E-1 [HIGH] next_action command block is non-functional cross-process.** The HUD emits `gate decide --trial-id ... --gate-id G0E ...` (35.2 build_next_action). Pasted verbatim from a fresh shell -> `GateError: card_missing` (gate_cli reads in-memory _CARD_STORE, empty cross-process; resume_api.py:159). The working operator path is `trial resume --trial-id <id> --verdict-file <f>` / gate shims (disk rehydration). The HUD's #1 job (what-to-paste) is broken. 35.2 round-trip test only checked argparse acceptance, not execution. FIX (post-run): build_next_action must emit `trial resume`/shim form, not `gate decide`.
- **F-E2E-2 [MED] Ambient instrument sections not emitted during the walk.** Projection carries identity/envelope/next_action/steps/preflight/decision_card but NOT health/specialists/modalities/trace. Witness-mode lifecycle warning "status=in-flight requires the health section" fires on every emit. So the HUD health strip (FR9), specialist chips (FR7), modality chips (FR10), state-trace well (FR8) are EMPTY mid-run. 35.2 built the section-update APIs; the runner wires pre-flight (35.3) + core decision surfaces but never calls update_health/specialists/modalities/append_trace during the walk. FIX (post-run): wire the ambient section updates into the walk.

## UPDATE — error-class witness + production bug surfaced (node 07G)

### More WORKING LIVE (witnessed at the error pause)
- **Second pause class witnessed LIVE: paused-at-error.** HUD renders it correctly: error_message section populated (35.9) with VERBATIM message "Completions.create() got an unexpected keyword argument 'model_kwargs'", node_index 32, tag vision.provider.transport (FR5). Render page shows "PAUSED AT ERROR". Zero-lie holds (projection==run.json). ETag "v1:363".
- **F-E2E-1 REFINED:** the error-class next_action is CORRECT — `trial recover --trial-id ...` (works cross-process; recover needs no card). So the broken command block (gate decide, card_missing) is scoped to the GATE-pause class ONLY. build_next_action's gate branch is wrong; its error/batch branches are right.
- Gates witnessed live: G0E, G0R, G1, G2B, G2C (5). Pause classes witnessed live: gate + error (2 of 3; waiting_for_provider_batch not hit — realtime mode).

### F-E2E-3 [PRODUCTION BUG, not HUD] vision.provider.transport at node 07G — breaks ALL runs
`app/specialists/vision/provider.py:316`: `bind_kwargs["model_kwargs"] = {"prompt_cache_key": cache_key}` then `handle.chat.bind(**bind_kwargs)`. LangChain `.bind(model_kwargs=...)` forwards `model_kwargs` as a literal `Completions.create()` kwarg, which the OpenAI SDK rejects. Regression from the batch-era B5 prompt-cache work (resolve_vision_prompt_cache_key, realtime path). Correct fix: pass the cache key via `extra_body={"prompt_cache_key": cache_key}` (or a direct `prompt_cache_key=` bind if the SDK version accepts it), not `model_kwargs`. This is a genuine production defect the 35.7 proofing run surfaced — worthy of its own dev cycle (party + fresh dev agent per operator substrate-change discipline), NOT a Claude-direct mid-run hotfix. Blocks the run from reaching `completed` at node 07G (index 32).

### Run state at this juncture
paused-at-error, node 07G, cost ~$0.358. Deliverables NOT produced (blocked pre-motion/voice/workbook by the vision bug). Completed-state + G3/G4/G4A gate witnesses + deliverables render = live-witness DEBT.

## COMPLETED — full lifecycle witnessed live

Run reached **status=completed** (completed_at 2026-07-12T03:41:37, terminal_gate G4A, silent_bypass_events 0, cost $0.60). Recovered past the vision bug (fix 247cf72d), then G3→G4→G4A→completed with all 3 components (deck+motion+workbook; motion/slide-01.mp4 1.3MB on disk; deck gamma-export; workbook_producer ran).

### HUD completed-state witness
- deliverables section POPULATED (35.9): components{deck,motion,workbook all true}, total_cost_usd 0.599893, 5 export_paths (FR16). Render shows LANDED + deliverables + cost.
- zero-lie held at completion (projection==run.json). Assembler emitted throughout (seq 0 -> 872).

## Murat 10-item checklist scorecard (orchestrator's honest pre-party read; party ratifies)
1. Completed + deliverables exist — **PASS** (status completed; motion mp4 + deck export on disk; workbook component true/producer ran).
2. Pre-flight all items w/ state+latency+confidence; no green-unknown; spawn after all-green — **PASS** (10 items pass; live openai+gamma).
3. Every gate verdict pasted VERBATIM from the HUD command block accepted first try — **FAIL** (F-E2E-1: gate-class next_action is `gate decide` -> card_missing cross-process; drove via `trial resume`). The HUD's #1 job (paste-to-act) is broken for the gate pause class.
4. Zero-lie: projection status/index == run.json at each pause — **PASS** (verified G0E, G2B, error, G4A, completed).
5. Every health tile age-stamped; budget-exceeded -> STALE veil — **FAIL/N-A** (F-E2E-2: health section not emitted mid-walk; no health tiles).
6. Exactly one notification per event-class; >=1 phone-push receipt — **PARTIAL/DEBT** (notifier launch witnessed via pre-flight item; live push during THIS run not witnessed; 35.6 banked a separate real ntfy receipt).
7. Server post-cold-load only /projection 200/304, no full reload; disclosure/scroll survive update — **PARTIAL** (200/304 curl-witnessed; DOM-preservation not browser-witnessed — chrome->localhost blocked).
8. /healthz trial_id+nonce matched flight; no un-induced refuse-to-render — **PASS**.
9. Unhit pause classes enumerated w/ L3 debt — waiting_for_provider_batch NOT hit (realtime); DEBT: needs a `--llm-execution-mode batch` run (LiteLLM path) to witness it.
10. Projection snapshots promoted to L2 golden + committed — snapshots saved (G0E/G2B/error/G4A/completed); promotion = follow-up.

**Pause classes witnessed LIVE: 2 of 3** (paused-at-gate ✓, paused-at-error ✓; waiting_for_provider_batch = debt). Gates witnessed: 8 (G0E,G0R,G1,G2B,G2C,G3,G4,G4A).

**Net:** HUD's decision-support CORE proven live (where-am-I, why-stopped, deliverables, zero-lie, server/render, all briefing sections). TWO real defects: F-E2E-1 (gate paste-command non-functional — hits JTBD#1) and F-E2E-2 (ambient instruments empty mid-run). Scoped-verdict question for the party: is this "performed to spec on the witnessed surface" (PASS-with-fixes) given the #1 paste-command is broken for gate pauses?
