# EPIC SPEC — Run-Start Batch LLM Execution Mode + Node-Level Model/Profile Registry

**Status:** SPEC (ready-to-activate draft; NOT yet built). **Authored:** 2026-07-01 (Opus 4.8) from the operator handoff brief `openai-batch-mode-run-option-brief-2026-07-01.md`. **Governance:** the formal epic (`bmad-create-epics-and-stories`) + party GREEN-LIGHT fire at the **optimal juncture** (below) BEFORE build; Fable 5 (next session) may refine this draft. **Boundary (binding, from the brief):** product work ONLY if it improves the Marcus-SPOC runtime orchestrator; proofing runs inform defects/constraints, never the target [[feedback_spoc_is_goal_not_concierge_proofing_runs]].

## The one binding invariant (what makes this surgical)
**Batch is TRANSPORT, not SEMANTICS.** A run-start `execution_mode` switch (`realtime | batch`) changes transport + timing for *eligible request sites only*; node inputs and outputs stay **contract-equivalent** to realtime. Downstream nodes must not know or care which transport produced an artifact — same schema, same validation. This clean adapter seam (zero downstream contract change) is precisely why the lift is "not especially heavy but must be surgical."

## The planning insight — TWO tranches by dependency + timing
The brief bundles 7 stories. They split cleanly into a **foundational, Fable-coupled tranche to pull forward** and the **async batch machinery to run at a clean runtime boundary**. This split is the whole "optimal juncture" answer.

### TRANCHE A — Node-level model/profile registry + quality-eval harness (FOUNDATIONAL; pull forward; Fable-coupled)
Decoupled from the async machinery — small, surgical, no pause/resume risk. It is the **shared substrate for THREE goals at once**, which is why it earns being pulled forward:
1. the batch feature (Tranche B depends on A1);
2. the **Fable-5 adoption** (the standing P1 opportunity — wire Fable 5 into the pipeline) [[project_fable5_regained_opportunity_scan]];
3. the **Leg-C D1 GO/NO-GO** (evaluate whether a more capable model makes Irene Pass-1 emit the sub-structure + roles the cluster-floor honoring needs) [[project_gamma_styleguide_arc_leg_a_done]].

- **A1 — Node-level model/profile registry.** Each LLM node declares `provider/model/reasoning_effort/text_verbosity/max_output_tokens` via a profile (`llm_execution.nodes.<node>`), `default_mode: realtime`. Wire Fable 5 (`claude-fable-5`) + the gpt-5 family into the registry/cascade/pricing — **mirror the existing `gpt-5.5` `vision-perceiver-real` wiring** (registry/pricing/cascade rows + config). AC: a node's model/profile is declaratively selectable; default behavior byte-preserved; Fable 5 selectable for perception AND Pass-1. Surgical; no runtime-orchestration change.
- **A2 — Perception (+ Pass-1) quality-evaluation harness.** A FROZEN slide set; run current/default + `gpt-5`/`gpt-5-mini`/`gpt-5-nano` + **Fable 5** (+ Opus/Sonnet baseline if useful); score: schema validity, OCR/extracted-text fidelity, visual-element coverage, layout/reading-path quality, figure/numeric fidelity, downstream Irene Pass-2 usefulness, 07G pass/fail, cost + turnaround. AC: a reproducible comparison across ≥ full `gpt-5` + `gpt-5-mini` + Fable 5. **This harness IS the vehicle for the Fable-5 P1 evaluation AND the Leg-C D1 Pass-1-quality question — one build, three payoffs.** Reuse the smoke sidecar `scratchpad/anthropic-batch-perception-smoke/openai_batch_smoke.py`.

### TRANCHE B — Batch execution adapter + async run machinery (the actual batch feature; own small epic; later juncture)
Heavier only because it touches the runtime orchestrator (pause/resume, cost reporting). Do it at a clean boundary so it stays surgical.
- **B1 — Batch execution adapter scaffold.** OpenAI Batch client wrapper; JSONL builder, submit/poll/cancel/result-download; persistent receipts + input manifest + row-level parsing; join by stable `custom_id`. AC: submit → poll → download → join-by-custom_id → per-row schema validation.
- **B2 — Perception node batch route.** One row per slide (`custom_id = <run_id>:<slide_id>`), `/v1/responses`, stable schema/instructions first + slide image/content last; same `PerceptionArtifact` shape as realtime; strict JSON parse + schema validation; per-slide failure isolation (fail-loud or retry per existing gate policy). AC: batch perception → schema-equivalent artifacts, robust to out-of-order rows.
- **B3 — Run pause/resume for batch wait.** A clear "waiting for provider batch" run state; **idempotent** poll/resume (repeated polls must not duplicate artifacts or alter downstream state); operator-visible status + 24h-window/expiry behavior. **Builds on the existing `production_runner` error-pause/recover + rewind-recover substrate — lower lift.** ⚠️ the two-walks gotcha applies: the batch side-effect (submit vs resume-consume) must fire in the walk that OWNS the post-pause resume [[project_production_runner_two_walks]]. AC: a batch-mode run pauses + resumes with zero duplicate downstream execution.
- **B4 — Cost + latency reporting.** Final report: batch ids, turnaround, input/cached/output/reasoning tokens, failed rows, retries, estimated cost; **three scenarios — conservative (no cache), observed (actual cached-token accounting), projected (recent avg cache-hit ratio by node/model/profile).** AC: report breaks down realtime vs batch + the three cost scenarios.
- **B5 — Prompt-caching optimization.** Stable-prefix prompt layout (stable schema/rubric/shared-context first, dynamic slide payload last); stable `prompt_cache_key` per node/profile/prompt-VERSION (never per-slide); track `usage.input_tokens_details.cached_tokens`; **regression pin on the stable prefix** (drift = red). AC: cached_tokens measured not assumed; a prefix-drift regression pin.
- **B6 — Run-start `execution_mode` switch (the operator-facing product surface).** Marcus-SPOC exposes `realtime | batch` at run start; routes ELIGIBLE nodes per the selected mode + node profiles (non-eligible nodes stay realtime); explicit operator wording ("batch may reduce cost/improve throughput but can pause the run…"). AC: operator chooses realtime vs batch at run start; eligible nodes route accordingly. **Do NOT promote to normal production until B3 (pause/resume) + B4 (cost accounting) land** (brief's binding caution).

## ⭐ Optimal-juncture recommendation
- **Tranche A → PULL FORWARD; fold into the Fable-5 adoption spike at the NEXT session.** A1 + A2 are the Fable-5 adoption vehicle AND directly answer the Leg-C D1 gate ("does a better model make Pass-1 emit the needed sub-structure + roles?"). They're small, surgical, async-free, and don't fragment the Gamma arc — they're the substrate the arc's D1 question needs anyway. This is "involve Fable sooner rather than later," concretely.
- **Tranche B → its own small epic, at the FIRST clean runtime boundary — recommended AFTER the Gamma Styleguide arc closes** (Phase-1 machinery done, likely + Phase-2), when the runtime-orchestration surface (`production_runner` pause/resume, cost reporting) can get focused surgical attention without mid-arc fragmentation. Earlier only if perception cost/throughput becomes a live pain point (then B1/B2 can land opportunistically on A1). Depends on A1.
- **Why optimal:** (1) A serves three goals at once → maximal leverage, pulled forward at near-zero marginal cost; (2) B's async/pause-resume touches the runtime orchestrator currently mid-Gamma-arc — an arc boundary keeps it surgical and reuses the proven concierge/two-walks pause substrate; (3) Fable is involved immediately via A, exactly as the operator wants.

## Dependencies / sequencing
`A1 (registry)` → prerequisite for `B1/B2/B6` and for Fable-5 wiring anywhere. `A2 (harness)` is independent + immediately useful (P1 Fable eval + D1). `B3` reuses the existing pause/resume substrate. `B4/B5` are additive. `B6` is the product-surface capstone, gated on B3+B4.

## Guardrails / binding invariants
- **SPOC-is-the-goal** (the brief's own boundary) — every element earns its place by improving the SPOC runtime.
- **Transport-only / contract-equivalent** — downstream is transport-blind; same schema validation realtime vs batch.
- **Adapter isolation** — provider-specific mechanics behind an adapter; LangGraph lets each node choose its own LLM resource/profile; non-eligible nodes untouched.
- **Idempotent pause/resume** — no duplicate artifacts; the two-walks side-effect discipline applies.
- **Calibrate `max_output_tokens`** — avoid hidden-reasoning starvation (observed in tiny gpt-5 heartbeats).
- **Measure, don't assume** — `cached_tokens` measured per row; join by `custom_id` never order; validate per row; don't fail a run for slow turnaround alone (only expiry/failure/operator-policy).
- **No-mocks live testing per component** [[feedback_no_mocks_real_live_apis]] [[feedback_incremental_live_testing_not_deferred]]; smoke evidence already exists (scratchpad sidecar).

## Evidence already in hand (from the brief)
Working smoke: `gpt-4.1-mini` 2-slide vision batch (usable JSON), `gpt-5` heartbeat (~41 min), `gpt-5-nano` shared-prefix cache probe (5248 cached tokens one row). Realtime prompt caching proven for gpt-5/mini/nano (~5248-5376 / 5312-5392 cached). Batch cache is per-row variable (row1 5248, row2 0) → measure, don't assume. Turnaround variable (1–41 min observed; 24h window) → design for pause.

## Placement in the development path
1. **Next session (Fable 5):** Tranche A folded into the Fable-5 adoption spike + the Leg-C live baseline (A1 registry wiring + A2 harness = the Pass-1 gpt-vs-Fable A/B that answers D1). Formal mini-green-light for Tranche A if it grows beyond the spike.
2. **Gamma arc continues** (Leg-C live proof → CLOSE → Leg-D/E → Phase-2) — unaffected; Tranche A is the substrate it already needs.
3. **At Gamma-arc close (or a live cost pain point):** formal `bmad-create-epics-and-stories` + party GREEN-LIGHT for Tranche B (the batch machinery epic), then build B1→B6 surgically.
