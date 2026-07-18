# ONBOARDING — `course-dev-ide-with-agents`

> **One-line elevator:** Collaborative intelligence infrastructure for course-content production — a deterministic, manifest-compiled orchestrator (operator surface: **Marcus-SPOC**) drives a roster of 14+ LangGraph specialist agents through gated, human-in-the-loop production of narrated lessons (with video/animation) and learner workbooks, with tamper-evident operator verdicts, a learning ledger, a live operator HUD, and frozen-graph reproducibility.

**Languages:** Python (3.11+), Markdown, JSON, Jinja2 (`.j2`), YAML, JavaScript, PowerShell, Shell, SQL
**Core frameworks:** LangChain, LangGraph, Pydantic v2, FastAPI, Uvicorn (plus httpx, Pytest in the runtime/tooling layers)
**Branch (at analysis):** `trial/c1m1-p1-2026-07-17` (cut off consolidated `master` `12775df6`)
**Graph baseline:** commit `bfefcc1b` · **2699 nodes / 5164 edges / 7 layers · 894 files** analyzed (`app/`, `scripts/`, `skills/`)
**Regenerated:** 2026-07-17 (full re-scan at HEAD after the Epics 41/42/43 wave landed and master consolidated — the resume-walk dispatch-integrity, operator-surface next-pass, and HIL-surface tabular-coverage substrate is now in-graph, incl. `hil_tabular_projector`, the HUD render package, `operator_surface`, the G_SETTINGS pre-walk gate, and the SPOC anti-drift parity guard).

> This guide is generated from the `/understand` knowledge graph. It is a **map, not the territory** — file summaries are LLM-derived and occasionally reflect one representative symbol in a file. When a summary and the code disagree, the code wins. Re-run `/understand` after significant changes and `/understand-onboard` to refresh this file.

---

## 1. Project Overview

The system turns source course material into finished, narrated lessons and companion workbooks through a **single deterministic pipeline that is compiled from a manifest, not hand-wired**. A human operator talks to one conversational surface — **Marcus-SPOC** — which drives the production runtime, pauses at each human-in-the-loop (HIL) gate to surface a **DecisionCard**, and resumes once the operator records a verdict. Under the hood, specialist agents (each a small LangGraph built from one canonical scaffold) do the real work: authoring narration, building slides, retrieving cited research, synthesizing voice, perceiving rendered slides, planning motion, and producing learner workbooks.

Three design commitments run through everything:

- **Determinism & reproducibility** — the pipeline topology is compiled from a YAML manifest into a frozen LangGraph; the same manifest yields the same graph, and a learning ledger records what happened.
- **Human-in-the-loop by construction** — the runtime is built to pause. Gates are first-class, verdicts are tamper-evident, DecisionCards are contract-pinned by versioned JSON Schema, and every operator-reviewed gate surface renders as a purpose-built **table**, never raw JSON.
- **State threaded on one carrier** — a single `RunState` Pydantic model flows through every node, and a `ProductionEnvelope` side-car accumulates every specialist contribution append-only, so downstream consumers never lose upstream detail.

Recent substrate milestones reflected in this graph scan:

- **✅ HIL Surface Tabular Coverage — Epic 43 (2026-07-17, CLOSED)** — every operator-reviewed gate surface now renders a bespoke, paginated markdown table instead of a dense JSON blob. `app/marcus/cli/hil_tabular_projector.py` re-shapes gate pause material (gate identity, enrichment metrics, ungrounded advisories, learning objectives, per-gate content) through a **content-type renderer registry** with a generic fallback; a `GATE_TO_CONTENT_TYPE` bridge resolves each gate to its renderer, and a **RED-first coverage ratchet** (canonical `GATE_CONTENT_TYPES` + shrink-only allowlist, now **empty**) makes "closed on a subset of surfaces" mechanically impossible. 14 operator-reviewed content types → 14 renderers. A **SPOC↔projector anti-drift parity guard** pins the two surfaces together.
- **✅ Operator Surface Next-Pass — Epic 42 (2026-07-17)** — the flight-deck operator HUD and the pre-walk settings gate. `app/marcus/orchestrator/operator_surface_assembler.py` is the single writer of the `operator-surface.json` projection (`app/models/runtime/operator_surface.py` — strict producer / lenient consumer / contract-owned event derivation); `app/hud/` serves it two ways — a GET-only localhost flight deck (`server.py` + the `render/` page/client/styles package) that **survives pause** and launches windowless (`CREATE_NO_WINDOW`), and a separate tunnel-facing **public read-only overlay** (`public.py`) that serves only a positive-allowlist-scrubbed view (never `launch_nonce`, decision-card internals, error text, or export paths). The new **G_SETTINGS** pre-walk gate (`app/models/decision_cards/g_settings.py`, "G0S") presents run settings for confirm-or-change before the walk begins and is **default-ON**. The `app/notify/` service polls the projection and pushes stall/event notifications via Apprise, swallowing every failure.
- **✅ Resume-Walk Dispatch Integrity — Epic 41 (2026-07-17)** — the fix for the `bc747b51` frozen-run defect. The real root cause was **budget starvation** (`max_specialist_calls=1`), not keyless resume: the throttle was **removed**, resume/recover now runs a live-env preflight, silent specialist skips **fail loud** in both walks, and `MARCUS_TRIAL_BUDGET_USD` became an **enforced-stop brake** rather than a passive gauge.
- **✅ Presentation-Support Workbook — Epics 36-40 (live gate PASSED 2026-07-15)** — a generalized workbook-producer chain (`app/specialists/workbook_producer/`, `app/marcus/lesson_plan/workbook_producer.py`, `app/marcus/orchestrator/workbook_wiring.py`) composes learner-workbook sections from the enriched lesson-plan run: prework frame plus scene / deep-dive / reflection / review / promise / check-on-learning projections; Ask-A research enrichment; a research packet/demand reader; Pass-1 authority / call-journal / source-span-catalog / slide-authority stores; live 07W.1 semantic writers; and the **Quinn-R quality gate**. Verified through a delegated, HIL-preserving live-test runner (`scripts/utilities/marcus_spoc_live_test_runner.py`) whose **verdict is honest** — it asserts a real conformant MD+DOCX workbook exists before granting `success: true`. ⚠️ Known open defect: the LO-overlay bridge (`_unit_to_enrichment_lo_map` in `app/specialists/workbook_producer/_act.py`) is fragile under live LO variance and can render Learning-Objectives placeholders.
- **Operator HUD Revival — Epic 35 (2026-07-11)** — the flight-deck HUD foundation (data sources, server, render package) reading the per-run `operator-surface.v1` projection, with the `app/notify/` ntfy service and `scripts/utilities/hud_data_sources.py` / `run_hud.py` / `progress_map.py` operator tooling. Parity is contract-pinned and the emit seam lives in `production_runner.py`.
- **Agentic Research Foundations (R0–R7) + Workbook Research Products (W0–W4)** — the research leg is governed, not ad hoc: Tracy's posture runtime (`app/specialists/tracy/`), evidence-hierarchy credibility classification (`research_credibility.py`, closed tier set T1 systematic-review → unclassified), anti-fabrication research intake (`app/specialists/_shared/research_intake.py`, re-exported to Irene so specialists never import the orchestrator), the **R7 research-detective hard-pause gate** (`research_detective_gate.py`) blocking Irene Pass-2 until an operator disposition receipt lands, and research-grounded workbook sections (`research_packet.py` → `glossary_projection.py` / `trends_projection.py`) with **empty-honesty** (empty packet → sections omitted, never fabricated).
- **Batch LLM Execution Mode v1** — opt-in LiteLLM Batch transport (`app/runtime/llm_batch/`) trading latency for ~50% provider cost; per-node realtime/batch transport profiles (`llm_execution_config.py`), an A3 eligibility matrix (`llm_batch_eligibility.py`), a vision batch route, and a `WaitingForProviderBatchError` pause/resume seam.
- **Course-source registry (S7 Phase-2)** — `app/marcus/course_source/` makes source material a first-class validated citizen: canonical processed-source layout, deterministic manifest scan + drift detection, SME registry, and syllabus metadata parsers (DOCX/MHTML).
- **Section 02A composer + G0 poll-surface gate** — `app/composers/section_02a/` classifies corpus files into a typed directive (LLM-driven, SHA256-cached) and `app/gates/section_02a/` guards it with a digest-matched HIL verdict ceremony over cli/http/mcp-stdio transports.

> ⚠️ **Design guardrail (read before touching production code):** the product goal is the **Marcus-SPOC runtime**. "Concierge"/proofing/trial runs of the BMAD-persona Marcus are **off-the-books discovery vehicles** — fix what they surface only when it genuinely improves the SPOC product, never to make a proofing run pass. See `CLAUDE.md` §"CRITICAL DESIGN GUARDRAIL" and `docs/STATE-OF-THE-APP.md`.

---

## 2. Architecture Layers

The graph assigns all 894 file-level nodes to seven layers (the root catch-all layer from the prior scan is gone — top-level config now folds into the tooling layer). Roughly top-to-bottom:

| Layer | Nodes | What lives here |
|---|---:|---|
| **Orchestration Core** | 184 | `app/marcus/` — Marcus-SPOC CLI + interlocutor, trial driver, production runner, dispatch adapter, lesson-plan compilation (incl. drill/quiz/workbook producers + research-packet/glossary/trends projections + the 07W prework/deep-dive/Ask-A families), course-source registry, styleguide picker/publisher, G0/research/coverage wiring incl. credibility scoring + the R7 detective gate, plus `app/manifest/` (the compiler). The layer that *drives* a production run. |
| **Specialist Agents** | 184 | `app/specialists/` — the 14+ per-specialist LangGraph agents (Irene, Gary, Vera, Texas, Tracy, Enrique, Vision, Wanda, Kira, Motion-Planner, Quinn-R, Workbook-Producer, …) built on the 9-node scaffold, plus `_shared` audits/research-intake, and `app/composers/` (incl. the Section 02A directive composer). |
| **Gates, HIL & Governance** | 72 | `app/gates/`, `app/parity/`, `app/cora/`, `app/audit/`, `app/replay/`, `app/ledger/` — HIL gate decision modules + resume APIs (incl. Section 02A G0 poll surface), the parity-contract DSL + SPOC anti-drift guard, Cora block-mode dev-graph enforcement, audit, resume-and-recover replay, and the learning ledger. |
| **Contracts & Models** | 171 | `app/models/` — Pydantic v2 domain & runtime-state models + emitted JSON schemas: RunState, decision-cards (G0–G6 + G0E/G0R/G_SETTINGS), operator verdicts, contributions side-cars, the operator-surface projection contract. Highest-fan-in layer; everything imports it. |
| **Runtime Substrate & Observability** | 65 | `app/runtime/` (incl. the `llm_batch/` LiteLLM Batch transport + eligibility/execution/cascade config, economics), `app/http/`, `app/mcp_server/`, `app/hud/` flight-deck + public overlay, `app/notify/`, `app/styleguide/`, and `runtime_server.py`. |
| **Scripts, Tool Clients & Generators** | 130 | `scripts/` — API clients (Gamma, Descript, ElevenLabs, Kling, Notion, Canvas), content generators (v4.2 templates), diagnostics, operator/live-proof drivers, Marcus-capability tooling — plus top-level project config files. |
| **Skills & Agent Personas** | 88 | `skills/` — operator-facing BMAD agent skill packages (`SKILL.md` persona files, reference contracts, sanctum asset templates) for the custom personas Marcus routes to. |

> Scope note: `docs/`, `tests/`, `state/`, `_bmad-output/`, and `scripts/utilities/` are intentionally outside the graph scan (`.understand-anything/.understandignore`). Dangling edges into those subtrees are dropped by design.

---

## 3. Key Concepts & Patterns

**Manifest-compiled graph.** The runner does not hard-code the pipeline. `app/manifest/loader.py` + `compiler.py` + `schema.py` read a YAML manifest describing nodes/edges/gates, validate it, and compile a LangGraph `StateGraph` — with compile-time contract lint over gate codes, model-config references, and the frozen-graph version. "Manifest-as-graph-config" is what makes runs deterministic and reproducible.

**The two-walk production runner.** `app/marcus/orchestrator/production_runner.py` executes a trial as **two LangGraph walks**: the *start walk* runs until the first human gate (G1) and pauses; the *continuation walk* resumes and handles every later gate. Gate-pause side effects (storyboard/chooser/picker publish, coverage gate, tabular projection) must be wired into **both** walks or they silently never fire for G2B+.

**The 9-node specialist scaffold.** Every specialist is built from one canonical shape defined in `app/specialists/_scaffold/contract.py` + `graph.py`: `receive → plan → act → verify → reflect → emit_spans → gate_decision → finalize → handoff`, wired through a reachability-asserted transition table. The `dispatch_adapter.py` builds each specialist's input state and invokes its compiled sub-graph uniformly. Understanding this one shape unlocks all 14+ specialists — they differ only in what their `act` and `verify` nodes do.

**RunState + the return contract.** `app/models/state/run_state.py` is the single state aggregate threaded through every node, encoding the five reproducibility invariants (byte-for-byte replay, frozen graph version, sanctum snapshot identity, model-selection trail, documented temperature variance). Its shared `_base.py` centralizes the Pydantic-v2 idioms (tz-aware datetimes, UUID4 pins) the whole state family reuses. `specialist_envelope.py` / `specialist_return.py` pin the request/response spine, so the runner treats every specialist identically; `dispatch_errors.py` lets a transient failure become a recoverable error-pause instead of killing the trial.

**HIL gates & DecisionCards.** At each gate the pipeline pauses and surfaces a **DecisionCard** for an operator verdict; `app/gates/resume_api.py` registers each issued card with a SHA-256 digest + a one-time server nonce, then converts a digest-matched, nonce-valid operator verdict into a LangGraph resume `Command`. Each gate (G0–G6+, plus G0E/G0R/G_SETTINGS) is contract-pinned by a versioned JSON Schema under `app/models/decision_cards/schema/`. `OperatorVerdict` is a frozen value object (approve/edit/reject) carrying the digest — the chatting LLM narrates, but only the operator's verdict advances the run.

**Tabular HIL surfaces (Epic 42/43).** `app/marcus/cli/hil_tabular_projector.py` re-shapes every gate pause into paginated markdown tables via a **content-type renderer registry** — replacing the old unreviewable dense-JSON dump. `GATE_TO_CONTENT_TYPE` resolves a gate to its renderer; a RED-first coverage ratchet (`GATE_CONTENT_TYPES` + a shrink-only allowlist, now empty) makes closing on a subset of surfaces mechanically impossible. `app/styleguide/parity.py` doubles as the **SPOC anti-drift parity guard** that keeps the projector and the SPOC narration from diverging.

**Operator HUD & the surface projection (Epic 35/42).** `operator_surface_assembler.py` is the *single writer* of `operator-surface.json`; `app/models/runtime/operator_surface.py` owns the contract (strict producer / lenient consumer / event derivation / `HudConfig`). `app/hud/server.py` serves a GET-only localhost flight deck (three routes, ETag/304, `launch_nonce` identity-pinned) rendered by the `app/hud/render/` package (page/client/styles, which never import the orchestrator — import-linter HUD1); `app/hud/public.py` is a **separate** tunnel-facing app serving only an allowlist-scrubbed view. `app/notify/service.py` polls the projection and pushes event/stall notifications, swallowing every failure.

**Pre-walk settings gate (G_SETTINGS / "G0S").** `app/models/decision_cards/g_settings.py` presents the resolved run settings for confirm-or-change **before** the production walk begins; it is a convention-conforming manifest HEAD gate (DecisionCard + manifest wiring + binding semantics) and defaults ON.

**Budget as a brake.** `MARCUS_TRIAL_BUDGET_USD` is an **enforced-stop** — the production runner halts a trial that would exceed it (Epic 41-4), rather than merely reporting spend. `app/runtime/economics.py` measures per-trial spend and per-agent cost drift against history.

**ProductionEnvelope carrier.** `app/models/runtime/production_envelope.py` is the append-only side-car that collects every `SpecialistContribution` with content-addressed provenance digests. It is deliberately the **most robust structure in the system** — schema-validated, versioned, fail-loud, and append-only.

**Styleguide binding & parity.** `app/styleguide/resolver.py` + `parity.py` implement CD-owned styleguide resolution with observability receipts; Gary's dispatch consumes the resolved base layer. The picker persists operator choices into the trial directive at interactive trial-start.

**G0 enrichment & research wiring.** `g0_enrichment_wiring.py` + `app/marcus/lesson_plan/g0_enrichment.py` author real, source-grounded learning objectives when `MARCUS_G0_DISPATCH_LIVE=1` (OFF yields deterministic boilerplate); the wiring mandates ≥1 grounded LO per file, retries once, then **fails loud on zero LOs**. At manifest node **04.55** `research_wiring.py` runs the Irene→Tracy→Texas bridge and lands the research contribution on the envelope.

**Coverage fail-loud gate.** `app/marcus/lesson_plan/coverage_gate.py` + `coverage_gate_wiring.py` (flag-gated, default OFF, both-walks seam) BLOCK before audio spend iff a must-cover point is missing or verbatim-absent with no planned surface, derived from the `CoverageReceipt`.

**Agentic research runtime (R0–R7).** **Tracy** dispatches retrieval under a declared research posture; `research_credibility.py` classifies every retrieved row onto a closed evidence-hierarchy tier set; `research_citation.py` mints cited entries with deterministic `source_ref` provenance; `_shared/research_intake.py` converts wrangled entries into specialist-safe intake with an **anti-fabrication guard**; and the **R7 detective gate** hard-pauses before Irene Pass-2 until the operator files a disposition receipt.

**Workbook production leg (07W band — live-gate PASSED 2026-07-15).** `workbook_wiring.py` is the deterministic orchestration seam for the four-node 07W band; `app/specialists/workbook_producer/` + `workbook_producer.py` compose learner workbooks from Irene collateral specs (`workbook_enrichment.py` is a resolution overlay, not the authority). Prework/deep-dive/review/reflection sections are deterministic projections over the authenticated run, with live 07W.1 semantic writers in `workbook_prework_writers.py`. Research-grounded sections ride the same chain with **empty-honesty**. ⚠️ The LO-overlay bridge (`_unit_to_enrichment_lo_map`) is the #1 open defect.

**Specialist state-threading contracts.** Two integration contracts recur when adding a specialist: it must be handed the **real run dir** (not a default), and it must receive/return state on the **`production_envelope` carrier**. Both are documented in `docs/dev-guide/how-to-add-a-specialist.md` — read that before wiring any new node.

**Runner verdict honesty.** `scripts/utilities/marcus_spoc_live_test_runner.py` asserts the deliverable actually exists and conforms (real MD+DOCX workbook) before granting `success: true` — a run that "completes" without its terminal deliverable is a FAILURE, never a false-green.

**Sanctum-lock.** Specialists that carry curated references (e.g. Texas) assert their references manifest is unchanged and raise a `SanctumLockViolation` on drift.

**Model cascade as data.** Specialists don't choose LLMs in code. Per-specialist `model_config.yaml` declares the tier; `app/runtime/cascade_config.py` validates pricing entries and **fails loud** otherwise.

**Batch LLM execution mode (opt-in, v1).** `llm_execution_config.py` declares per-node realtime vs. batch transport; `llm_batch_eligibility.py` is the A3 matrix. In batch mode, `app/runtime/llm_batch/` submits the work and raises `WaitingForProviderBatchError` — a control-flow exception the runner catches to pause until the provider batch completes (`trial resume-batch`). Vision is the first opt-in consumer.

**Learning ledger.** `app/ledger/emitter.py` writes verdict/override events idempotently to Postgres `ledger_events` (append-only, deduped by idempotency key); this is how the system remembers operator decisions across trials.

**Parity-contract DSL.** `app/parity/contracts/` is a self-registering DSL (`@parity_contract` decorator + surface registry + sanctum-alignment API) that pins which transports (cli/http/mcp) each gate surface must support, so surfaces cannot silently diverge.

**Protected invariants (do not regress).** VO ↔ on-screen alignment and source-detail → Gamma conveyance are enforced by `_shared` audits (`voice_provider_text.py`, `source_fidelity_audit.py`).

---

## 4. Guided Tour (recommended reading order)

A 14-stop walk from the operator's-eye view inward to the substrate (from the knowledge-graph `tour`, refreshed 2026-07-17):

1. **The Operator Surface** — `app/marcus/cli/marcus_spoc.py`, `cli/trial.py`. Marcus-SPOC is the conversational single-point-of-contact over the whole engine; the trial CLI is the plumbing that launches / resumes / recovers / batch-runs production-clone trials. Read them together: a chat surface backed by a deterministic pipeline the operator drives through explicit commands.
2. **Chatting at the Gate** — `app/marcus/cli/marcus_interlocutor.py`. The LLM-driven stop-and-chat REPL that runs at every paused gate: it narrates the real decision card in persona and holds a free-form turn, but only ever *confirms* a validated gate verdict rather than inventing one. This is the boundary the whole system defends.
3. **Compiling the Deterministic Graph** — `app/manifest/compiler.py`. A validated `PipelineManifest` is compiled into a LangGraph `StateGraph`: add nodes/edges, resolve specialist dispatch builders, run compile-time contract lint over gate codes / model-config refs / frozen-graph version. Pipeline is data first, executable graph second.
4. **Walking the Production Pipeline** — `production_runner.py` (highest fan-out in the codebase), `orchestrator/dispatch_adapter.py`. Walks the compiled manifest node by node: dispatch specialists, pause at gates with decision cards, checkpoint, resume/recover under budget + preflight guards. **Two node walks** — the start walk stops at G1; any gate-pause side effect must be handled in both.
5. **The Run State Contract** — `app/models/state/run_state.py` (highest fan-in of any file), `state/_base.py`. The top-level state model encoding the five reproducibility invariants; the shared base centralizes the tz-aware / UUID4 Pydantic-v2 idioms the whole state family reuses.
6. **Specialist Envelope & Return Contracts** — `state/specialist_envelope.py`, `state/specialist_return.py`, `specialists/dispatch_errors.py`, `app/parity/contracts/__init__.py`. Every invocation is wrapped in a `SpecialistEnvelope` (UUID4 `request_id` + tz-aware timestamp) so async outputs pair back to inputs; every reply is a `SpecialistReturn` with a verb (accept/edit/reject) + cross-field consistency check; typed dispatch errors convert transient failures to recoverable pauses; the parity DSL pins these surfaces.
7. **The 9-Node Specialist Scaffold** — `app/specialists/_scaffold/contract.py`, `_scaffold/graph.py`. The canonical scaffold (`receive → plan → act → verify → reflect → emit_spans → gate_decision → finalize → handoff`) through a reachability-asserted transition table. The contract file is the production-side authority; the scaffold graph is the generator stub.
8. **Ingestion & Lesson-Planning Specialists** — `specialists/texas/graph.py`, `specialists/irene/graph.py`. Two real scaffold instantiations at the front of the pipeline: Texas ingests source under a **sanctum lock** (digest-pinned references); Irene's Pass-2 graph assembles the deterministic narration prompt, invokes the LLM, then enforces the figure-fidelity and reading-path invariants. Same 9 nodes; the discipline lives in their `verify` steps.
9. **Slide Dispatch & the Lesson Plan Schema** — `specialists/gary/graph.py`, `app/marcus/lesson_plan/schema.py`. Gary is the slide-generation specialist (dispatch-trail, envelope decode, strict receipt parsing, handoff to the Gamma deck generator). The Lesson Plan schema is the shared vocabulary — `LessonPlan`, `PlanUnit`, the `ScopeDecision` state machine, `BlueprintSignoff`, the `FitReport` family — that lets every specialist agree on what the lesson is.
10. **The HIL Verdict Machinery** — `app/gates/resume_api.py`, `state/operator_verdict.py`, `decision_cards/_base.py`. The tamper-evident heart: each issued card is registered with a SHA-256 digest + one-time nonce, and only a digest-matched, nonce-valid `OperatorVerdict` (approve/edit/reject) converts to a resume `Command`. Closes the loop from Step 2.
11. **Media-Tool API Clients** — `scripts/api_clients/base_client.py`, `gamma_client.py`, `elevenlabs_client.py`. The pipeline reaches the outside world through HTTP clients extending one foundation (auth session, exponential-backoff retry with Retry-After, Link-header pagination, structured errors); the Gamma client (warm-401 burst-throttle retry) and ElevenLabs client sit on top.
12. **Runtime Observability: HUD, Notifier & Economics** — `app/hud/public.py`, `app/notify/service.py`, `app/runtime/economics.py`. The public HUD serves an allowlist-scrubbed projection view (never raw bytes, `launch_nonce`, or card internals); the notifier polls the surface file, derives event classes only through the contract, and runs a stall watchdog; economics measures per-trial spend + per-agent cost drift.
13. **The Learning Ledger** — `app/ledger/schema.sql` (`ledger_events`), `app/ledger/emitter.py`. The append-only Postgres table (event_id, trial_id, gate_id, kind, payload, idempotency_key) backing gate accountability; the idempotent emitter ensures the schema, dedupes by idempotency key, tracks emission-failure counters. Makes the Step-5 reproducibility invariants auditable after the fact.
14. **Skills & Agent Personas** — `skills/bmad-agent-marcus/SKILL.md`, `skills/README.md`. The persona layer: the Marcus `SKILL.md` is the activation contract for the Creative Production Orchestrator (routes work through the capability registry, honors fidelity gates), alongside the whole BMAD persona/sanctum tree. Closes the tour where it began — the SPOC surface, now understood as a persona-shaped orchestrator atop the deterministic, contract-governed pipeline.

---

## 5. File Map — key entry points by layer

**Orchestration Core** (`app/marcus/`, `app/manifest/`)
- `cli/marcus_spoc.py` — operator conversational entry point (the SPOC surface)
- `cli/marcus_interlocutor.py`, `cli/trial.py` — stop-and-chat REPL + trial driver
- `cli/hil_tabular_projector.py` — tabular HIL surface projector (content-type renderer registry)
- `orchestrator/production_runner.py` — two-walk trial engine (start / continue / resume / recover) + budget brake
- `orchestrator/dispatch_adapter.py` — builds specialist state, compiles & invokes specialist sub-graphs
- `orchestrator/operator_surface_assembler.py` — single writer of the `operator-surface.json` projection
- `orchestrator/preflight.py` — start-path pre-flight (phase-01 local checks + phase-02 live heartbeats)
- `orchestrator/styleguide_picker.py`, `chooser_publisher.py`, `storyboard_publisher.py`, `picker_publisher.py`, `gh_pages_publish.py` — gate-artifact publishing surfaces
- `orchestrator/g0_enrichment_wiring.py`, `research_wiring.py`, `coverage_gate_wiring.py`, `ask_a_research_wiring.py` — canonical-walk enrichment + research legs
- `orchestrator/research_credibility.py`, `research_citation.py`, `research_detective_gate.py` — evidence-tier classification, deterministic citation minting, R7 hard-pause gate
- `orchestrator/workbook_wiring.py`, `workbook_prework_writers.py` — 07W band orchestration seam + live 07W.1 semantic writers
- `lesson_plan/schema.py`, `learning_objective.py`, `planning_context.py`, `coverage_manifest.py`, `coverage_gate.py` — lesson-plan compilation + fail-loud coverage gate
- `lesson_plan/workbook_producer.py`, `workbook_enrichment.py`, `collateral_spec.py`, `research_packet.py`, `glossary_projection.py`, `trends_projection.py` — workbook + research-product producers
- `lesson_plan/{prework_artifact,prework_projection,deep_dive_projection,reflection_projection,review_projection,promise_projection,check_on_learning_projection}.py` — deterministic workbook-section projections
- `lesson_plan/pass1_authority.py`, `pass1_call_journal.py`, `pass1_source_span_catalog.py`, `slide_authority.py`, `quinn_r_gate.py` — Pass-1 durable authority + Quinn-R gate
- `lesson_plan/quiz_producer.py`, `drill_producer.py` (+ `*_enrichment.py`) — quiz + drill modality producers
- `course_source/registry.py`, `canonical_processed_source.py`, `manifest_scan.py`, `manifest_drift.py`, `sme_registry.py`, `syllabus_metadata.py` — course corpus registry ("SOURCE+LOs are KING")
- `manifest/compiler.py`, `loader.py`, `schema.py`, `gate_topology.py` — the deterministic neck

**Specialist Agents** (`app/specialists/`, `app/composers/`)
- `_scaffold/contract.py`, `_scaffold/graph.py` — the canonical 9-node scaffold
- `irene/graph.py` — two-pass narration engine + Pass-2 id-integrity gate (VO↔on-screen invariant)
- `gary/graph.py`, `gary/_act.py`, `gary/styleguide_library.py` — Gamma variant dispatch/normalization
- `texas/graph.py`, `texas/_act.py` — retrieval + sanctum-lock; `tracy/posture_dispatch.py` — research-posture dispatch
- `enrique/_act.py` — directed ElevenLabs TTS assembly; `vision/provider.py`, `vision/batch_route.py`
- `workbook_producer/_act.py`, `graph.py` — in-graph workbook specialist (node 07W)
- `quinn_r/`, `motion_planner/_act.py`, `kira/_act.py`, `wanda/_act.py`, `vera/`
- `_shared/research_intake.py`, `voice_provider_text.py`, `source_fidelity_audit.py`, `narration_join.py`, `figure_tokens.py` — intake + protected-invariant enforcers
- `composers/section_02a/composer.py`, `directive_model.py`, `cli_adapter.py` — LLM corpus classification → typed directive (SHA256-cached)

**Gates, HIL & Governance** (`app/gates/`, `app/parity/`, `app/cora/`, `app/ledger/`, `app/replay/`, `app/audit/`)
- `gates/resume_api.py`, `errors.py`, `verdict.py`, `party_mode_as_interrupt.py`; `gates/section_02a/` — G0 corpus-directive gate (cli/http/mcp-stdio parity)
- `parity/contracts/` — the parity-contract DSL (`@parity_contract`, registry, sanctum-alignment); `app/styleguide/parity.py` — SPOC anti-drift guard
- `cora/graph.py`, `block_mode_node.py` — Cora block-mode dev-graph enforcement
- `ledger/emitter.py`, `events.py`, `schema.sql`; `replay/parity_comparison.py`

**Contracts & Models** (`app/models/`)
- `state/run_state.py`, `state/_base.py`, `state/operator_verdict.py`, `state/specialist_return.py`, `state/specialist_envelope.py`, `state/model_resolution_entry.py`
- `runtime/production_envelope.py`, `runtime/operator_surface.py`
- `decision_cards/` (G0–G6 + `g0e.py`, `g0r.py`, `g_settings.py`) + `decision_cards/schema/*.v1.schema.json`
- `adapter.py`, `marcus/lesson_plan/schema/*.v1.schema.json`

**Runtime Substrate & Observability** (`app/runtime/`, `app/hud/`, `app/notify/`, `app/styleguide/`, `app/http/`, `app/mcp_server/`)
- `runtime/cascade_config.py`, `economics.py`, `compiled_graph_digest.py`, `override_api.py`, `checkpointer.py`
- `runtime/llm_execution_config.py`, `llm_batch_eligibility.py`, `llm_batch/` (Files+Batches adapter, JSONL budget, custom_id join, `BatchReceipt`, cost report, `WaitingForProviderBatchError`)
- `hud/server.py`, `public.py`, `render/{page,client,styles}.py`; `notify/service.py`; `styleguide/resolver.py`, `parity.py`

**Scripts, Tool Clients & Generators** (`scripts/`)
- `api_clients/base_client.py` + concrete clients (Canvas, Descript, ElevenLabs, Kling, Notion, Gamma, …)
- `operator/scite_oauth_login_auto.py`, `build_descript_narrated_lesson.py`; `generators/v42/` template packs

---

## 6. Complexity Hotspots — approach carefully

The graph flags **165** file-level nodes as `complex`. The ones a new developer is most likely to touch:

| File | Why it's a hotspot |
|---|---|
| `app/marcus/orchestrator/production_runner.py` | Two-walk engine + primary import hub + budget brake; central to almost everything. |
| `app/marcus/orchestrator/dispatch_adapter.py` | Specialist-invocation seam (state build → compile → invoke → extract). |
| `app/marcus/cli/hil_tabular_projector.py` | The content-type renderer registry every gate surface flows through; a gap here regresses an operator-reviewed surface to raw JSON. |
| `app/marcus/orchestrator/operator_surface_assembler.py` | Single writer of the projection every HUD/notifier reads; atomic Windows-safe writes + seq/progress semantics + a freshness daemon thread. |
| `app/models/runtime/operator_surface.py` | The projection contract (strict producer / lenient consumer / event derivation); a producer-model break silently corrupts every observer. |
| `app/specialists/irene/graph.py` | Two-pass narration authoring + slide-join id-integrity gate (VO↔on-screen protected invariant). |
| `app/specialists/gary/_act.py` | Gamma variant dispatch + normalization; styleguide-resolution consumer. |
| `app/models/state/run_state.py` | Highest fan-in module; changes ripple through every node. |
| `app/models/runtime/production_envelope.py` | Protected-invariant carrier; must stay schema-validated / append-only. |
| `app/manifest/compiler.py` | Pipeline topology compilation; errors break determinism for the whole run. |
| `app/marcus/cli/marcus_spoc.py` | Operator surface + deterministic guard (chatting LLM never drives engine). |
| `app/styleguide/parity.py` | SPOC anti-drift parity guard + three-way digest attestation; load-bearing for surface coherence. |
| `app/hud/render/page.py` + `client.py` | Projection→HTML renderer + poll client; must never import the orchestrator (import-linter HUD1). |
| `app/hud/public.py` | Public overlay; a scrub-allowlist miss leaks gate secrets over the tunnel. |
| `app/specialists/workbook_producer/_act.py` | Generalized workbook adapter; ⚠️ contains the fragile LO-overlay bridge (`_unit_to_enrichment_lo_map`) — #1 open defect. |
| `app/marcus/orchestrator/workbook_wiring.py` | 07W-band seam: slide-authority under dispatch lock, journaled exactly-once Deep Dive dispatch, envelope reconciliation. |
| `app/marcus/orchestrator/ask_a_research_wiring.py` | Exactly-once journaled Ask-A dispatch; a broken journal check double-spends provider calls. |
| `app/marcus/orchestrator/research_detective_gate.py` | R7 hard-pause gate; a wrong receipt check silently unblocks ungoverned research. |
| `app/marcus/orchestrator/g0_enrichment_wiring.py` | G0E/G0R canonical enrichment wiring (structure always; live LLM operator-armed, fail-loud on zero LOs). |
| `app/runtime/llm_batch/adapter.py` | Batch transport seam — submit/pause/resume/join control flow crosses the runner's two-walk boundary. |
| `app/marcus/course_source/syllabus_metadata.py` | Large DOCX/MHTML parser; corpus-facing input hardening. |
| `app/marcus/lesson_plan/log.py` | Append-only JSONL log with a single-writer matrix. |
| `scripts/api_clients/base_client.py` | Shared base for concrete API clients (retry/backoff/error hierarchy). |

---

## 7. Getting Started Checklist

1. **Read the guardrail** in `CLAUDE.md` and `docs/STATE-OF-THE-APP.md` — the SPOC-is-the-goal framing governs every change.
2. **Follow the guided tour** (§4) in order — it's designed to build the mental model from operator surface to substrate.
3. **Trace one run** — start at `marcus_spoc.py`, follow `production_runner.py` → `dispatch_adapter.py` → one specialist's `build_<name>_graph`, and watch `RunState` thread through.
4. **Understand a gate** — read `gates/resume_api.py` with a DecisionCard schema (`decision_cards/schema/g1.v1.schema.json`) open beside it, then see how `hil_tabular_projector.py` renders it for the operator.
5. **BMAD methodology** — production/dev work runs through BMAD workflows + party-mode + a dev agent (see `CLAUDE.md` §"BMAD sprint governance"). Activate **Marcus first** for anything production-shaped (`skills/bmad-agent-marcus/SKILL.md`).
6. **Adding a gate renderer or a specialist** — read `docs/dev-guide/how-to-add-a-gate-renderer.md` and `docs/dev-guide/how-to-add-a-specialist.md` first; both encode conventions the coverage ratchet and state-threading contracts enforce.
7. **Explore interactively** — run `/understand-dashboard` to browse the graph, or `/understand-chat` to ask questions about specific components.

---

*Generated from `.understand-anything/knowledge-graph.json` (commit `bfefcc1b`, 2026-07-17). Regenerate with `/understand` (incremental) or `/understand --full`, then `/understand-onboard`.*
