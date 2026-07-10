# ONBOARDING — `course-dev-ide-with-agents`

> **One-line elevator:** Collaborative intelligence infrastructure for course-content production — a deterministic, manifest-compiled orchestrator (operator surface: **Marcus-SPOC**) drives a roster of LangGraph specialist agents through gated, human-in-the-loop production of narrated lessons (with video/animation) and learner workbooks, with tamper-evident operator verdicts, a learning ledger, and frozen-graph reproducibility.

**Languages:** Python (3.11+), Markdown, YAML, JSON, JavaScript, Shell, PowerShell, SQL
**Core frameworks:** LangChain, LangGraph, Pydantic v2 (plus httpx, FastAPI/Uvicorn, Pytest in the runtime/tooling layers)
**Branch (at analysis):** `dev/batch-mode-2026-07-10`
**Graph baseline:** commit `bfe5a02a` · **2630 nodes / 5344 edges / 8 layers · 838 files** analyzed (`app/`, `scripts/`, `skills/`)
**Regenerated:** 2026-07-10 (incremental update at HEAD; node count dropped vs. the 2026-07-07 build because re-analyzed files now carry stricter sub-node significance filtering — coverage of files is unchanged)

> This guide is generated from the `/understand` knowledge graph. It is a **map, not the territory** — file summaries are LLM-derived and occasionally reflect one representative symbol in a file. When a summary and the code disagree, the code wins. Re-run `/understand` after significant changes and `/understand-onboard` to refresh this file.

---

## 1. Project Overview

The system turns source course material into finished, narrated lessons and companion workbooks through a **single deterministic pipeline that is compiled from a manifest, not hand-wired**. A human operator talks to one conversational surface — **Marcus-SPOC** — which drives the production runtime, pauses at each human-in-the-loop (HIL) gate to surface a **DecisionCard**, and resumes once the operator records a verdict. Under the hood, specialist agents (each a small LangGraph built from one canonical scaffold) do the real work: authoring narration, building slides, retrieving cited research, synthesizing voice, perceiving rendered slides, planning motion, and producing learner workbooks.

Three design commitments run through everything:

- **Determinism & reproducibility** — the pipeline topology is compiled from a YAML manifest into a frozen LangGraph; the same manifest yields the same graph, and a learning ledger records what happened.
- **Human-in-the-loop by construction** — the runtime is built to pause. Gates are first-class, verdicts are tamper-evident, and DecisionCards are contract-pinned by versioned JSON Schema.
- **State threaded on one carrier** — a single `RunState` Pydantic model flows through every node, and a `ProductionEnvelope` side-car accumulates every specialist contribution append-only, so downstream consumers never lose upstream detail.

Recent substrate milestones reflected in this graph scan:

- **Batch LLM Execution Mode v1 (2026-07-10)** — opt-in LiteLLM Batch transport (`app/runtime/llm_batch/`) trading latency for ~50% provider cost on eligible call sites; per-node realtime/batch transport profiles (`llm_execution_config.py`), an A3 eligibility matrix (`llm_batch_eligibility.py`), a vision batch route (`app/specialists/vision/batch_route.py`), and a `WaitingForProviderBatchError` pause/resume seam in the production runner.
- **Course-source registry (S7 Phase-2)** — `app/marcus/course_source/` makes source material a first-class validated citizen: canonical processed-source layout, deterministic manifest scan + drift detection, SME registry, and syllabus metadata parsers (DOCX/MHTML).
- **Section 02A composer + G0 poll-surface gate** — `app/composers/section_02a/` classifies corpus files into a typed directive (LLM-driven, SHA256-cached) and `app/gates/section_02a/` guards it with a digest-matched HIL verdict ceremony over cli/http/mcp-stdio transports.
- **Canonical Production Conversation arc (S0–S6) + S7 workbook generalization** — styleguide picker/CD resolution/Gary parity, G0 enrichment, Tracy/Scite research dispatch, and the generalized `workbook_producer` leg (first composed walk to node 07W on Tejal Part 3) are standing properties of a normal Marcus-SPOC run.

> ⚠️ **Design guardrail (read before touching production code):** the product goal is the **Marcus-SPOC runtime**. "Concierge"/proofing/trial runs of the BMAD-persona Marcus are **off-the-books discovery vehicles** — fix what they surface only when it genuinely improves the SPOC product, never to make a proofing run pass. See `CLAUDE.md` §"CRITICAL DESIGN GUARDRAIL" and `docs/STATE-OF-THE-APP.md`.

---

## 2. Architecture Layers

The graph assigns all 839 file-level nodes to eight layers. Roughly top-to-bottom:

| Layer | Nodes | What lives here |
|---|---:|---|
| **Marcus Orchestration** | 143 | `app/marcus/` — Marcus-SPOC CLI, trial driver, production runner, dispatch adapter, lesson-plan compilation (incl. drill/quiz/workbook producers), course-source registry, styleguide picker/publisher, G0/research/coverage wiring. The layer that *drives* a production run. |
| **Specialist Agents & Composers** | 189 | `app/specialists/` — per-specialist LangGraph agents (irene, gary, texas, enrique, vision, wanda, kira, motion_planner, quinn_r, workbook_producer, …) + `_shared` audits and composer nodes (incl. the Section 02A directive composer). |
| **Gates & Workflow Substrate** | 59 | `app/gates/`, `app/manifest/`, `app/cora/` — HIL gate decision modules (incl. Section 02A G0 poll surface), pipeline-manifest compiler, Cora block-mode dev-graph enforcement. |
| **Domain Models** | 167 | `app/models/` — Pydantic v2 domain & runtime-state models + emitted JSON schemas: decision-cards, lesson-plan envelopes, contributions side-cars, collateral specs. |
| **Runtime & Transport** | 65 | `app/runtime/` (incl. the new `llm_batch/` LiteLLM Batch transport package + eligibility/execution config), `app/replay/`, `app/http/`, `app/ledger/`, `app/mcp_server/`, `app/parity/`, `app/audit/` — Postgres checkpointer/retention, resume-and-recover replay, HTTP/MCP transport, parity checks, audit plumbing. |
| **Operator & Developer Tooling** | 124 | `scripts/` — API clients, content generators, diagnostics, operator utilities, live-proof drivers. |
| **BMAD Agent Skills** | 88 | `skills/` — operator-facing BMAD agent skill packages (`SKILL.md` persona files, reference contracts) for custom personas Marcus routes to. |
| **Project Root & Configuration** | 4 | Top-level env templates, git/coverage attributes, tooling artifacts. |

---

## 3. Key Concepts & Patterns

**Manifest-compiled graph.** The runner does not hard-code the pipeline. `app/manifest/loader.py` + `compiler.py` + `schema.py` read a YAML manifest describing nodes/edges/gates, validate it, and compile a LangGraph `StateGraph`. "Manifest-as-graph-config" is what makes runs deterministic and reproducible.

**The two-walk production runner.** `app/marcus/orchestrator/production_runner.py` executes a trial as **two LangGraph walks**: the *start walk* runs until the first human gate (G1) and pauses; the *continuation walk* resumes and handles every later gate. Gate-pause side effects (storyboard/chooser/picker publish) must be wired into **both** walks or they silently never fire for G2B+.

**The 9-node specialist scaffold.** Every specialist is built from one canonical shape defined in `app/specialists/_scaffold/contract.py` + `graph.py` (`receive → plan → act → verify → reflect → gate → finalize → handoff` + a `build_<name>_graph` factory). The `dispatch_adapter.py` builds each specialist's input state and invokes its compiled sub-graph uniformly.

**RunState + the return contract.** `app/models/state/run_state.py` is the single state aggregate threaded through every node. `specialist_return.py` defines the shape every specialist hands back, so the runner treats them all identically.

**HIL gates & DecisionCards.** At each gate the pipeline pauses and surfaces a **DecisionCard** for an operator verdict; `app/gates/resume_api.py` rebuilds run state from the stored card + verdict and resumes the walk. Each gate (G1–G6+) is contract-pinned by a versioned JSON Schema under `app/models/decision_cards/schema/`.

**ProductionEnvelope carrier.** `app/models/runtime/production_envelope.py` is the append-only side-car that collects every `SpecialistContribution` with content-addressed provenance digests. It is deliberately the **most robust structure in the system** — schema-validated, versioned, fail-loud, and append-only.

**Styleguide binding & parity.** `app/styleguide/resolver.py` + `parity.py` implement CD-owned styleguide resolution with observability receipts; Gary's dispatch consumes the resolved base layer. The picker (`styleguide_picker.py`) persists operator choices into the trial directive at interactive trial-start.

**G0 enrichment & research wiring.** `g0_enrichment_wiring.py` and `research_wiring.py` thread deterministic G0 enrichment and live Scite research dispatch into the canonical production walk (flag-gated, fail-loud on creds absence).

**Workbook production leg.** `app/specialists/workbook_producer/` + `app/marcus/lesson_plan/workbook_producer.py` compose learner workbooks from Irene collateral specs; enrichment (`workbook_enrichment.py`) is a resolution overlay, not the authority source.

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
2. **Marcus-SPOC CLI Entry** — `app/marcus/cli/__main__.py`, `marcus_spoc.py`. `python -m app.marcus.cli` argparse tree (trial start/resume/recover/batch, gate, ask, plan-dialogue, plan-ratify); narration layer where the chatting LLM never drives engine state.
3. **Trial and Run Lifecycle** — `app/marcus/cli/trial.py`. Start / resume / recover a tracked production run.
4. **Production Runner: Two Walks** — `app/marcus/orchestrator/production_runner.py`, `gate_runner.py`. Heart of the runtime, highest fan-out file (43 imports); start walk stops at G1, continuation walk handles every later gate.
5. **Manifest Compiler** — `app/manifest/schema.py`, `loader.py`, `compiler.py`. YAML manifest → frozen `StateGraph`.
6. **Gates, Verdicts, and the Ledger** — `app/gates/resume_api.py` (fan-in 28), `app/models/state/operator_verdict.py`, `app/ledger/schema.sql::ledger_events`. Operator-trust loop + append-only memory.
7. **Lesson Plan Model Layer** — `app/marcus/lesson_plan/schema.py` (fan-in 19), `composition.py`, frozen `lesson_plan.v1` schema. The lesson before slides/narration exist.
8. **Course-Source Registry** *(new)* — `app/marcus/course_source/`: canonical processed source, manifest scan/drift, SME registry, syllabus metadata, frozen `canonical_asset_record.v0_1` schema.
9. **Section 02A Composer and G0 Gate** *(new)* — `app/composers/section_02a/composer.py`, `directive_model.py`, `app/gates/section_02a/poll_surface.py`. First LLM step over the corpus + its digest-guarded HIL gate.
10. **State Substrate and Specialist Contract** — `app/models/state/_base.py` (fan-in 55, most-depended-upon file), `run_state.py`, `specialist_envelope.py`, `specialist_return.py`, `app/specialists/_scaffold/contract.py`.
11. **Specialist LangGraph Roster** — `irene/graph.py` (highest specialist fan-out, 17), `gary/graph.py`, `texas/graph.py`, `enrique/graph.py`. One 9-node scaffold, different act bodies.
12. **Runtime Persistence and Economics** — `app/runtime/checkpointer.py`, `economics.py`. Pause Tuesday, resume Thursday; cost accounting.
13. **Batch LLM Execution Mode** *(new)* — `app/runtime/llm_execution_config.py`, `llm_batch_eligibility.py`, `llm_batch/jsonl.py`, `llm_batch/adapter.py`, `app/specialists/vision/batch_route.py`. Opt-in ~50%-cost batch transport with pause/resume control flow.
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
- `enrique/_act.py` — directed ElevenLabs TTS narration assembly
- `workbook_producer/_act.py`, `graph.py` — in-graph workbook specialist (node 07W)
- `vision/provider.py`, `quinn_r/`, `motion_planner/_act.py`, `kira/_act.py`, `wanda/_act.py`
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

The graph flags **130** file-level nodes as `complex`. The ones a new developer is most likely to touch:

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
| `app/marcus/orchestrator/research_wiring.py` | Live Scite dispatch bridge from Irene `collateral.research_goals`. |
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

*Generated from `.understand-anything/knowledge-graph.json` (commit `bfe5a02a`, 2026-07-10). Regenerate with `/understand` (incremental) or `/understand --full`, then `/understand-onboard`.*
