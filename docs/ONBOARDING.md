# ONBOARDING — `course-dev-ide-with-agents`

> **One-line elevator:** Collaborative intelligence infrastructure for course-content production — a deterministic, manifest-compiled orchestrator (operator surface: **Marcus-SPOC**) drives a roster of LangGraph specialist agents through gated, human-in-the-loop production of narrated lessons (with video/animation) and learner workbooks, with tamper-evident operator verdicts, a learning ledger, and frozen-graph reproducibility.

**Languages:** Python (3.11+), Markdown, YAML, JSON, JavaScript, Shell, PowerShell, SQL
**Core frameworks:** LangChain, LangGraph, Pydantic v2 (plus httpx, FastAPI/Uvicorn, Pytest in the runtime/tooling layers)
**Branch (at analysis):** `codex/workbook-enhanced-epics-36-40` (⚠️ **not** master — see note)
**Graph baseline:** commit `102b32a3` · **3076 nodes / 5977 edges / 8 layers · 884 files** analyzed (`app/`, `scripts/`, `skills/`)
**Regenerated:** 2026-07-14 (incremental update at HEAD; **navigation-aid refresh on the codex branch** to map the in-progress Epics 36-40 workbook substrate. ⚠️ This substrate's live gate is still OPEN and it is not merged to master — this graph will be re-run at post-merge master consolidation.)

> This guide is generated from the `/understand` knowledge graph. It is a **map, not the territory** — file summaries are LLM-derived and occasionally reflect one representative symbol in a file. When a summary and the code disagree, the code wins. Re-run `/understand` after significant changes and `/understand-onboard` to refresh this file.

---

## 1. Project Overview

The system turns source course material into finished, narrated lessons and companion workbooks through a **single deterministic pipeline that is compiled from a manifest, not hand-wired**. A human operator talks to one conversational surface — **Marcus-SPOC** — which drives the production runtime, pauses at each human-in-the-loop (HIL) gate to surface a **DecisionCard**, and resumes once the operator records a verdict. Under the hood, specialist agents (each a small LangGraph built from one canonical scaffold) do the real work: authoring narration, building slides, retrieving cited research, synthesizing voice, perceiving rendered slides, planning motion, and producing learner workbooks.

Three design commitments run through everything:

- **Determinism & reproducibility** — the pipeline topology is compiled from a YAML manifest into a frozen LangGraph; the same manifest yields the same graph, and a learning ledger records what happened.
- **Human-in-the-loop by construction** — the runtime is built to pause. Gates are first-class, verdicts are tamper-evident, and DecisionCards are contract-pinned by versioned JSON Schema.
- **State threaded on one carrier** — a single `RunState` Pydantic model flows through every node, and a `ProductionEnvelope` side-car accumulates every specialist contribution append-only, so downstream consumers never lose upstream detail.

Recent substrate milestones reflected in this graph scan:

- **⚠️ Presentation-Support Workbook — Epics 36-40 (2026-07-12/14, IN PROGRESS on branch `codex/workbook-enhanced-epics-36-40`; live gate OPEN — not product-accepted)** — a generalized workbook-producer chain (`app/specialists/workbook_producer/`, `app/marcus/lesson_plan/workbook_producer.py`, `app/marcus/orchestrator/workbook_wiring.py`) composes learner-workbook sections from the enriched lesson-plan run: prework frame, plus scene / deep-dive / reflection / review / promise / check-on-learning projections (`app/marcus/lesson_plan/{prework_artifact,prework_projection,scene_extraction,deep_dive_projection,reflection_projection,review_projection,promise_projection,check_on_learning_projection}.py`); Ask-A research enrichment wiring (`ask_a_enrichment.py`, `app/marcus/orchestrator/ask_a_research_wiring.py`); a research packet/demand reader (`research_packet.py`, `research_demand.py`); Pass-1 authority / call-journal / source-span-catalog and slide-authority stores (`pass1_authority.py`, `pass1_call_journal.py`, `pass1_source_span_catalog.py`, `slide_authority.py`, `app/pass1_generation_lock.py`); and the **Quinn-R quality gate** (`quinn_r_gate.py`). Verified through a delegated, HIL-preserving live-test runner (`scripts/utilities/marcus_spoc_live_test_runner.py`). **NOTE:** stories 38.1 / 38.3a remain `in-progress` and the fresh governed *paid* workbook live gate has not yet passed (all 10 prior HIL attempts non-passing) — treat this substrate as in-flux, not accepted.
- **Operator HUD Revival — Epic 35 (2026-07-11, merged to master)** — a flight-deck operator HUD surface (`app/hud/` — data sources, server, and `render/` page/client/styles) reads a per-run operator-surface projection assembled by `app/marcus/orchestrator/operator_surface_assembler.py` from the run's `operator-surface.v1` schema (`app/models/schemas/operator-surface.v1.schema.json`, `app/models/runtime/operator_surface.py`), with an `app/notify/` ntfy notification service and `scripts/utilities/hud_data_sources.py` / `run_hud.py` / `progress_map.py` operator tooling. Parity is contract-pinned (`tests/contracts/test_operator_surface_parity.py`, `test_operator_surface_projection_demands_parity.py`) and the emit seam lives in `production_runner.py`.
- **Agentic Research Foundations (R0–R7, 2026-07-10)** — the research leg grows from "one Scite dispatch" into a governed research runtime: Tracy's posture runtime (`app/specialists/tracy/` — posture dispatch over the research charter), evidence-hierarchy credibility classification (`app/marcus/orchestrator/research_credibility.py`, closed tier set T1 systematic-review → unclassified per `docs/dev-guide/research-evidence-hierarchy.md`), anti-fabrication research intake for specialists (`app/specialists/_shared/research_intake.py`, re-exported to Irene via `app/specialists/irene/retrieval_intake.py` so specialists never import the orchestrator), and the **R7 research-detective hard-pause gate** (`research_detective_gate.py`) that blocks Irene Pass-2 dispatch until an operator disposition receipt lands.
- **Workbook Research Products (W0–W4, 2026-07-10)** — research-grounded workbook sections: a thin shared research-packet reader over the node-04.55 research contribution (`app/marcus/lesson_plan/research_packet.py`), glossary and trends projections (`glossary_projection.py`, `trends_projection.py`) that turn tier-labeled research rows into encyclopedia-style glossary articles and a grounded `ResearchTrendsBrief`, composed into the workbook by the generalized `workbook_producer` chain with empty-honesty behavior (sections are omitted, never fabricated, when the packet is empty).
- **Batch LLM Execution Mode v1 (2026-07-10)** — opt-in LiteLLM Batch transport (`app/runtime/llm_batch/`) trading latency for ~50% provider cost on eligible call sites; per-node realtime/batch transport profiles (`llm_execution_config.py`), an A3 eligibility matrix (`llm_batch_eligibility.py`), a vision batch route (`app/specialists/vision/batch_route.py`), and a `WaitingForProviderBatchError` pause/resume seam in the production runner.
- **Course-source registry (S7 Phase-2)** — `app/marcus/course_source/` makes source material a first-class validated citizen: canonical processed-source layout, deterministic manifest scan + drift detection, SME registry, and syllabus metadata parsers (DOCX/MHTML).
- **Section 02A composer + G0 poll-surface gate** — `app/composers/section_02a/` classifies corpus files into a typed directive (LLM-driven, SHA256-cached) and `app/gates/section_02a/` guards it with a digest-matched HIL verdict ceremony over cli/http/mcp-stdio transports.
- **Canonical Production Conversation arc (S0–S6) + S7 workbook generalization** — styleguide picker/CD resolution/Gary parity, G0 enrichment, Tracy/Scite research dispatch, and the generalized `workbook_producer` leg (first composed walk to node 07W on Tejal Part 3) are standing properties of a normal Marcus-SPOC run.

> ⚠️ **Design guardrail (read before touching production code):** the product goal is the **Marcus-SPOC runtime**. "Concierge"/proofing/trial runs of the BMAD-persona Marcus are **off-the-books discovery vehicles** — fix what they surface only when it genuinely improves the SPOC product, never to make a proofing run pass. See `CLAUDE.md` §"CRITICAL DESIGN GUARDRAIL" and `docs/STATE-OF-THE-APP.md`.

---

## 2. Architecture Layers

The graph assigns all 863 file-level nodes to eight layers. Roughly top-to-bottom:

| Layer | Nodes | What lives here |
|---|---:|---|
| **Marcus Orchestration** | 146 | `app/marcus/` — Marcus-SPOC CLI, trial driver, production runner, dispatch adapter, lesson-plan compilation (incl. drill/quiz/workbook producers + research-packet/glossary/trends projections), course-source registry, styleguide picker/publisher, G0/research/coverage wiring incl. credibility scoring and the R7 detective gate. The layer that *drives* a production run. |
| **Specialist Agents & Composers** | 184 | `app/specialists/` — per-specialist LangGraph agents (irene, gary, texas, tracy, enrique, vision, wanda, kira, motion_planner, quinn_r, workbook_producer, …) + `_shared` audits/research intake and composer nodes (incl. the Section 02A directive composer). |
| **Gates & Workflow Substrate** | 39 | `app/gates/`, `app/manifest/`, `app/cora/` — HIL gate decision modules (incl. Section 02A G0 poll surface), pipeline-manifest compiler, Cora block-mode dev-graph enforcement. |
| **Domain Models** | 170 | `app/models/` — Pydantic v2 domain & runtime-state models + emitted JSON schemas: decision-cards, lesson-plan envelopes, contributions side-cars, collateral specs. |
| **Runtime & Transport** | 39 | `app/runtime/` (incl. the `llm_batch/` LiteLLM Batch transport package + eligibility/execution config), the new `app/hud/` flight-deck operator HUD, `app/notify/` ntfy service, `app/replay/`, `app/http/`, `app/ledger/`, `app/mcp_server/`, `app/parity/`, `app/audit/` — Postgres checkpointer/retention, resume-and-recover replay, HTTP/MCP transport, parity checks, audit plumbing. |
| **Operator & Developer Tooling** | 124 | `scripts/` — API clients, content generators, diagnostics, operator utilities, live-proof drivers. |
| **BMAD Agent Skills** | 88 | `skills/` — operator-facing BMAD agent skill packages (`SKILL.md` persona files, reference contracts) for custom personas Marcus routes to. |
| **Project Root & Configuration** | 73 | Top-level env templates, git/coverage attributes, `state/` runtime config (incl. `hud-config.yaml`, `pipeline-manifest.yaml`), and tooling artifacts. |

---

## 3. Key Concepts & Patterns

**Manifest-compiled graph.** The runner does not hard-code the pipeline. `app/manifest/loader.py` + `compiler.py` + `schema.py` read a YAML manifest describing nodes/edges/gates, validate it, and compile a LangGraph `StateGraph`. "Manifest-as-graph-config" is what makes runs deterministic and reproducible.

**The two-walk production runner.** `app/marcus/orchestrator/production_runner.py` executes a trial as **two LangGraph walks**: the *start walk* runs until the first human gate (G1) and pauses; the *continuation walk* resumes and handles every later gate. Gate-pause side effects (storyboard/chooser/picker publish) must be wired into **both** walks or they silently never fire for G2B+.

**The 9-node specialist scaffold.** Every specialist is built from one canonical shape defined in `app/specialists/_scaffold/contract.py` + `graph.py` (`receive → plan → act → verify → reflect → gate → finalize → handoff` + a `build_<name>_graph` factory). The `dispatch_adapter.py` builds each specialist's input state and invokes its compiled sub-graph uniformly.

**RunState + the return contract.** `app/models/state/run_state.py` is the single state aggregate threaded through every node. `specialist_return.py` defines the shape every specialist hands back, so the runner treats them all identically.

**HIL gates & DecisionCards.** At each gate the pipeline pauses and surfaces a **DecisionCard** for an operator verdict; `app/gates/resume_api.py` rebuilds run state from the stored card + verdict and resumes the walk. Each gate (G1–G6+) is contract-pinned by a versioned JSON Schema under `app/models/decision_cards/schema/`.

**ProductionEnvelope carrier.** `app/models/runtime/production_envelope.py` is the append-only side-car that collects every `SpecialistContribution` with content-addressed provenance digests. It is deliberately the **most robust structure in the system** — schema-validated, versioned, fail-loud, and append-only.

**Styleguide binding & parity.** `app/styleguide/resolver.py` + `parity.py` implement CD-owned styleguide resolution with observability receipts; Gary's dispatch consumes the resolved base layer. The picker (`styleguide_picker.py`) persists operator choices into the trial directive at interactive trial-start.

**G0 enrichment & research wiring.** `g0_enrichment_wiring.py` and `research_wiring.py` thread deterministic G0 enrichment and live research dispatch into the canonical production walk (flag-gated, fail-loud on creds absence). At manifest node **04.55** `research_wiring.py` runs the Irene→Tracy→Texas bridge and lands the research contribution on the envelope.

**Agentic research runtime (R0–R7).** Research is governed, not ad hoc: **Tracy** (`app/specialists/tracy/posture_dispatch.py`) dispatches retrieval under a declared research posture; `research_credibility.py` classifies every retrieved row onto a **closed evidence-hierarchy tier set** (T1 systematic review → unclassified); `research_citation.py` mints cited entries with deterministic `source_ref` provenance; `_shared/research_intake.py` converts wrangled entries into specialist-safe intake with an **anti-fabrication guard** (specialists consume via `irene/retrieval_intake.py` and never import the orchestrator); and the **R7 detective gate** (`research_detective_gate.py`) hard-pauses the walk before Irene Pass-2 until the operator files a disposition receipt (approve/reject/defer per finding).

**Workbook production leg.** `app/specialists/workbook_producer/` + `app/marcus/lesson_plan/workbook_producer.py` compose learner workbooks from Irene collateral specs; enrichment (`workbook_enrichment.py`) is a resolution overlay, not the authority source. Research-grounded sections ride the same chain: `research_packet.py` (W1 shape-pinned reader) feeds `glossary_projection.py` (W2) and `trends_projection.py` (W3), with **empty-honesty** (W4) — an empty research packet omits the sections rather than fabricating content.

**Sanctum-lock.** Specialists that carry curated references (e.g. Texas) assert their references manifest is unchanged and raise a `SanctumLockViolation` on drift.

**Model cascade as data.** Specialists don't choose LLMs in code. Per-specialist `model_config.yaml` declares the model tier; `app/runtime/cascade_config.py` validates pricing entries and **fails loud** otherwise.

**Batch LLM execution mode (opt-in, v1).** `app/runtime/llm_execution_config.py` declares per-node realtime vs. batch transport profiles; `llm_batch_eligibility.py` is the A3 eligibility matrix. When a node runs in batch mode, `app/runtime/llm_batch/` (LiteLLM Files+Batches adapter, JSONL row budget, custom_id join, `BatchReceipt` persistence, hermetic cost report, prompt-cache keys) submits the work and raises `WaitingForProviderBatchError` — a control-flow exception the production runner catches to pause the walk until the provider batch completes (`trial resume-batch`). Vision perception is the first opt-in consumer (`app/specialists/vision/batch_route.py`).

**Course-source registry.** `app/marcus/course_source/` owns "SOURCE+LOs are KING": `canonical_processed_source.py` enforces the ratified lesson-leaf layout, `manifest_scan.py`/`manifest_drift.py` detect corpus drift deterministically, `sme_registry.py` resolves SME profiles, and `syllabus_metadata.py` parses DOCX/MHTML syllabi. Asset records are pinned by the frozen `canonical_asset_record.v0_1` schema.

**Section 02A directive composer.** `app/composers/section_02a/composer.py` is the first LLM-driven step over a corpus leaf — rule-based exclusions, then typed role classification with prompt-normalized SHA256 caching — guarded by the `app/gates/section_02a/` G0 poll-surface gate (digest-matched `display_directive` → `submit_verdict` → `resume_from_verdict` ceremony, parity-pinned across cli/http/mcp-stdio transports).

**Learning ledger.** `app/ledger/emitter.py` writes verdict/override events idempotently to Postgres `ledger_events`; this is how the system remembers operator decisions across trials.

**Protected invariants (do not regress).** VO ↔ on-screen alignment and source-detail → Gamma conveyance are enforced by `_shared` audits (`voice_provider_text.py`, `source_fidelity_audit.py`).

---

## 4. Guided Tour (recommended reading order)

A 15-stop walk from the operator's-eye view inward to the substrate (from the knowledge-graph `tour`):

1. **Runtime Platform Overview** — `app/models/README.md`, `app/manifest/README.md`, `app/runtime/README.md`. The three pillars: shared model catalog, manifest compiler, execution substrate.
2. **Marcus-SPOC CLI and Run Lifecycle** — `app/marcus/cli/__main__.py`, `marcus_spoc.py`, `trial.py`. `python -m app.marcus.cli` argparse tree (trial start/resume/recover/batch, gate, ask, plan-dialogue, plan-ratify); narration layer where the chatting LLM never drives engine state.
3. **Production Runner: Two Walks** — `app/marcus/orchestrator/production_runner.py`, `gate_runner.py`. Heart of the runtime, highest fan-out file (44 imports); start walk stops at G1, continuation walk handles every later gate.
4. **Manifest Compiler** — `app/manifest/schema.py`, `loader.py`, `compiler.py`. YAML manifest → frozen `StateGraph`.
5. **Gates, Verdicts, and the Ledger** — `app/gates/resume_api.py` (fan-in 28), `app/models/state/operator_verdict.py`, `app/ledger/schema.sql::ledger_events`. Operator-trust loop + append-only memory.
6. **Lesson Plan Model Layer** — `app/marcus/lesson_plan/schema.py` (fan-in 19), `composition.py`, frozen `lesson_plan.v1` schema. The lesson before slides/narration exist.
7. **Course-Source Registry** — `app/marcus/course_source/`: canonical processed source, manifest scan/drift, SME registry, syllabus metadata, frozen `canonical_asset_record.v0_1` schema.
8. **Section 02A Composer and G0 Gate** — `app/composers/section_02a/composer.py`, `directive_model.py`, `app/gates/section_02a/poll_surface.py`. First LLM step over the corpus + its digest-guarded HIL gate.
9. **State Substrate and Specialist Contract** — `app/models/state/_base.py` (fan-in 55, most-depended-upon file), `run_state.py`, `specialist_envelope.py`, `specialist_return.py`, `app/specialists/_scaffold/contract.py`.
10. **Specialist LangGraph Roster** — `irene/graph.py` (highest specialist fan-out, 17), `gary/graph.py`, `texas/graph.py`, `tracy/graph.py` (research-posture specialist), `enrique/graph.py`. One 9-node scaffold, different act bodies.
11. **Agentic Research Foundations** *(new)* — `app/marcus/orchestrator/research_wiring.py`, `research_credibility.py`, `research_citation.py`, `research_detective_gate.py`, `app/specialists/_shared/research_intake.py`. Governed research: posture dispatch → tiered credibility → cited entries → anti-fabrication intake → R7 hard-pause disposition gate.
12. **Workbook and Research Projections** *(new)* — `app/marcus/lesson_plan/research_packet.py`, `glossary_projection.py`, `trends_projection.py`, `workbook_producer.py`, `app/specialists/workbook_producer/graph.py` (node 07W). Research-grounded glossary + trends sections with empty-honesty.
13. **Persistence, Economics, and Batch Execution** — `app/runtime/checkpointer.py`, `economics.py`, `llm_execution_config.py`, `llm_batch_eligibility.py`, `llm_batch/adapter.py`, `app/specialists/vision/batch_route.py`. Pause Tuesday, resume Thursday; cost accounting; opt-in ~50%-cost batch transport with pause/resume control flow.
14. **Styleguide Resolution** — `app/styleguide/resolver.py`, `parity.py`, `app/marcus/orchestrator/styleguide_picker.py`. Visual identity resolved, not hard-coded.
15. **BMAD Agent Skills Layer** — `skills/README.md`, `skills/bmad-agent-marcus/SKILL.md`, `capabilities/registry.yaml`. The human-facing persona layer beside the runtime.

---

## 5. File Map — key entry points by layer

**Marcus Orchestration** (`app/marcus/`)
- `cli/marcus_spoc.py` — operator conversational entry point (the SPOC surface)
- `cli/marcus_interlocutor.py`, `cli/trial.py` — stop-and-chat REPL + trial driver
- `orchestrator/production_runner.py` — two-walk trial engine (start / continue / resume / recover)
- `orchestrator/dispatch_adapter.py` — builds specialist state, compiles & invokes specialist sub-graphs
- `orchestrator/styleguide_picker.py`, `chooser_publisher.py`, `storyboard_publisher.py`, `picker_publisher.py`, `gh_pages_publish.py` — gate-artifact publishing surfaces
- `orchestrator/g0_enrichment_wiring.py`, `research_wiring.py`, `coverage_gate_wiring.py` — canonical-walk enrichment + research legs
- `orchestrator/research_credibility.py`, `research_citation.py`, `research_detective_gate.py` — evidence-tier classification, deterministic citation minting, R7 hard-pause disposition gate
- `lesson_plan/research_packet.py`, `glossary_projection.py`, `trends_projection.py` — W1 research-packet reader + W2/W3 glossary/trends projections
- `lesson_plan/workbook_producer.py`, `workbook_enrichment.py`, `collateral_spec.py` — workbook schema + producer + enrichment overlay
- `lesson_plan/quiz_producer.py`, `quiz_enrichment.py`, `drill_producer.py`, `drill_enrichment.py` — quiz + drill modality producers (same producer/enrichment split as workbook)
- `lesson_plan/planning_context.py`, `planning_ratification.py` — Irene planning-context handoff + ratified planning decisions
- `course_source/registry.py`, `canonical_processed_source.py`, `manifest_scan.py`, `manifest_drift.py`, `sme_registry.py`, `syllabus_metadata.py` — course corpus registry (source-of-truth for "SOURCE+LOs are KING")
- `facade.py` — orchestration facade

**Styleguide substrate** (`app/styleguide/`)
- `resolver.py` — shared styleguide resolution (Gary thin re-export)
- `parity.py` — pure comparator for CD/Gary/picker digest attestation

**Specialist Agents** (`app/specialists/`)
- `_scaffold/contract.py`, `_scaffold/graph.py` — the canonical 9-node scaffold
- `irene/graph.py` — two-pass narration engine + Pass-2 id-integrity gate
- `gary/_act.py` — Gamma variant dispatch/normalization; `styleguide_library.py`, `learned_dependencies.py`
- `texas/graph.py`, `texas/_act.py` — retrieval + sanctum-lock
- `tracy/graph.py`, `tracy/posture_dispatch.py` — research-posture specialist (dispatches retrieval under the declared research posture)
- `enrique/_act.py` — directed ElevenLabs TTS narration assembly
- `workbook_producer/_act.py`, `graph.py` — in-graph workbook specialist (node 07W)
- `vision/provider.py`, `quinn_r/`, `motion_planner/_act.py`, `kira/_act.py`, `wanda/_act.py`
- `_shared/research_intake.py` (+ `irene/retrieval_intake.py` barrel) — anti-fabrication research intake; specialists never import the orchestrator
- `_shared/voice_provider_text.py`, `source_fidelity_audit.py`, `narration_join.py` — protected-invariant enforcers

**Gates & Workflow Substrate**
- `app/gates/resume_api.py`, `errors.py`, `app/gates/section_*/poll_surface.py`
- `app/gates/section_02a/` — G0 corpus-directive gate (digest-matched verdict ceremony; cli/http/mcp-stdio parity)
- `app/manifest/compiler.py`, `loader.py`, `schema.py`
- `app/cora/graph.py` — Cora block-mode dev-graph enforcement

**Composers** (`app/composers/`)
- `section_02a/composer.py`, `directive_model.py`, `cli_adapter.py` — LLM corpus classification → typed directive (SHA256-cached)

**Domain Models** (`app/models/`)
- `state/run_state.py`, `state/_base.py`, `state/operator_verdict.py`, `state/specialist_return.py`
- `runtime/production_envelope.py`, `runtime/production_trial_envelope.py`
- `decision_cards/` (G0–G6 Pydantic models) + `decision_cards/schema/*.v1.schema.json`
- `marcus/lesson_plan/schema/*.v1.schema.json` — collateral spec, lesson plan, coverage manifests

**Runtime & Transport**
- `runtime/cascade_config.py`, `economics.py`, `compiled_graph_digest.py`, `override_api.py`
- `runtime/llm_execution_config.py`, `llm_batch_eligibility.py` — per-node transport profiles + batch eligibility matrix
- `runtime/llm_batch/` — LiteLLM Batch transport package: `adapter.py` (Files+Batches SDK), `jsonl.py` (row building/size budget), `join.py` (custom_id join), `receipts.py` (`BatchReceipt` persistence), `cost_report.py`, `prompt_cache.py`, `errors.py` (`WaitingForProviderBatchError`)
- `ledger/emitter.py`, `events.py`, `schema.sql`; `replay/parity_comparison.py`

**Operator & Developer Tooling** (`scripts/`)
- `api_clients/base_client.py` + concrete clients (Canvas, Descript, ElevenLabs, Kling, Notion, Gamma, …)
- `operator/scite_oauth_login_auto.py`, `build_descript_narrated_lesson.py`

---

## 6. Complexity Hotspots — approach carefully

The graph flags **135** file-level nodes as `complex`. The ones a new developer is most likely to touch:

| File | Why it's a hotspot |
|---|---|
| `app/marcus/orchestrator/production_runner.py` | Two-walk engine + primary import hub; central to almost everything. |
| `app/marcus/orchestrator/dispatch_adapter.py` | Specialist-invocation seam (state build → compile → invoke → extract). |
| `app/specialists/irene/graph.py` | Two-pass narration authoring + slide-join id-integrity gate (`_assert_join_id_integrity`). |
| `app/specialists/gary/_act.py` | Gamma variant dispatch + normalization; styleguide resolution consumer. |
| `app/models/state/run_state.py` | Most depended-upon module; changes ripple through every node. |
| `app/models/runtime/production_envelope.py` | Protected-invariant carrier; must stay schema-validated / append-only. |
| `app/manifest/compiler.py` + `schema.py` | Pipeline topology compilation; errors break determinism for the whole run. |
| `app/marcus/cli/marcus_spoc.py` | Operator surface + deterministic guard (chatting LLM never drives engine). |
| `app/styleguide/parity.py` | Pure comparator for three-way digest attestation; observability-only but load-bearing for S-flip clock. |
| `app/specialists/workbook_producer/_act.py` | Generalized workbook adapter (was tejal-hardcoded); consumes Irene collateral authority. |
| `app/marcus/orchestrator/research_wiring.py` | Node-04.55 Irene→Tracy→Texas research bridge; lands the research contribution the W1–W4 projections read. |
| `app/marcus/orchestrator/research_detective_gate.py` | R7 hard-pause gate — blocks Irene Pass-2 until operator disposition; a wrong receipt check silently unblocks ungoverned research. |
| `app/marcus/orchestrator/g0_enrichment_wiring.py` | G0E/G0R canonical enrichment wiring (structure always; live LLM operator-armed). |
| `app/specialists/_shared/narration_join.py` | Shared join policy; silent-collapse here corrupts downstream audio/G5/07W. |
| `app/runtime/llm_batch/adapter.py` + `batch_route.py` | Batch transport seam — submit/pause/resume/join control flow crosses the runner's two-walk boundary. |
| `app/marcus/course_source/syllabus_metadata.py` | 620-line DOCX/MHTML parser; corpus-facing input hardening. |
| `app/marcus/lesson_plan/log.py` | 798-line append-only JSONL log with a single-writer matrix. |
| `scripts/api_clients/base_client.py` | Shared base for concrete API clients (retry/backoff/error hierarchy). |

---

## 7. Getting Started Checklist

1. **Read the guardrail** in `CLAUDE.md` and `docs/STATE-OF-THE-APP.md` — the SPOC-is-the-goal framing governs every change.
2. **Follow the guided tour** (§4) in order — it's designed to build the mental model from operator surface to substrate.
3. **Trace one run** — start at `marcus_spoc.py`, follow `production_runner.py` → `dispatch_adapter.py` → one specialist's `build_<name>_graph`, and watch `RunState` thread through.
4. **Understand a gate** — read `gates/resume_api.py` with a DecisionCard schema (`decision_cards/schema/g1.v1.schema.json`) open beside it.
5. **BMAD methodology** — production/dev work runs through BMAD workflows + party-mode + a dev agent (see `CLAUDE.md` §"BMAD sprint governance"). Activate **Marcus first** for anything production-shaped (`skills/bmad-agent-marcus/SKILL.md`).
6. **Explore interactively** — run `/understand-dashboard` to browse the graph, or `/understand-chat` to ask questions about specific components.

---

*Generated from `.understand-anything/knowledge-graph.json` (commit `fcaca8e7`, 2026-07-12). Regenerate with `/understand` (incremental) or `/understand --full`, then `/understand-onboard`.*
