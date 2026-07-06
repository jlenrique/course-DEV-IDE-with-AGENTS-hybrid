# ONBOARDING — `course-dev-ide-with-agents`

> **One-line elevator:** Collaborative intelligence infrastructure for course-content production — a deterministic, manifest-compiled orchestrator (operator surface: **Marcus-SPOC**) drives a roster of ~20 LangGraph specialist agents through gated, human-in-the-loop production of narrated lessons (with video/animation), with tamper-evident operator verdicts, a learning ledger, and frozen-graph reproducibility.

**Languages:** Python (3.11+), Markdown, YAML, JSON, Jinja2, JavaScript, PowerShell, Shell, SQL
**Core frameworks:** LangChain, LangGraph, Pydantic v2 (plus httpx, FastAPI/Uvicorn, Pytest in the runtime/tooling layers)
**Branch (at analysis):** `dev/gamma-styleguide-phase2-2026-07-02` (severed from `upstream/master` since 2026-04-24)
**Graph baseline:** commit `b3ab2137` · **2031 nodes / 3710 edges / 8 layers · 834 files** analyzed (`app/`, `scripts/`, `skills/`)
**Regenerated:** 2026-07-05 (incremental update from the `85f2778` / 1820-node baseline)

> This guide is generated from the `/understand` knowledge graph. It is a **map, not the territory** — file summaries are LLM-derived and occasionally reflect one representative symbol in a file. When a summary and the code disagree, the code wins. Re-run `/understand` after significant changes and `/understand-onboard` to refresh this file.

---

## 1. Project Overview

The system turns source course material into finished, narrated lessons through a **single deterministic pipeline that is compiled from a manifest, not hand-wired**. A human operator talks to one conversational surface — **Marcus-SPOC** — which drives the production runtime, pauses at each human-in-the-loop (HIL) gate to surface a **DecisionCard**, and resumes once the operator records a verdict. Under the hood, ~20 **specialist agents** (each a small LangGraph built from one canonical scaffold) do the real work: authoring narration, building slides, retrieving cited research, synthesizing voice, perceiving rendered slides, planning motion, and assembling the workbook.

Three design commitments run through everything:

- **Determinism & reproducibility** — the pipeline topology is compiled from a YAML manifest into a frozen LangGraph; the same manifest yields the same graph, and a learning ledger records what happened.
- **Human-in-the-loop by construction** — the runtime is built to pause. Gates are first-class, verdicts are tamper-evident, and DecisionCards are contract-pinned by versioned JSON Schema.
- **State threaded on one carrier** — a single `RunState` Pydantic model flows through every node, and a `ProductionEnvelope` side-car accumulates every specialist contribution append-only, so downstream consumers never lose upstream detail.

> ⚠️ **Design guardrail (read before touching production code):** the product goal is the **Marcus-SPOC runtime**. "Concierge"/proofing/trial runs of the BMAD-persona Marcus are **off-the-books discovery vehicles** — fix what they surface only when it genuinely improves the SPOC product, never to make a proofing run pass. See `CLAUDE.md` §"CRITICAL DESIGN GUARDRAIL" and `docs/STATE-OF-THE-APP.md`.

---

## 2. Architecture Layers

The graph assigns all 822 file-level nodes to eight layers. Roughly top-to-bottom:

| Layer | Nodes | What lives here |
|---|---:|---|
| **Marcus Orchestration** | 116 | `app/marcus/` — the Marcus-SPOC orchestrator, conversational CLI surface, lesson-plan compilation, UDAC / enrichment-consumption wiring. The layer that *drives* a production run. |
| **Specialist Agents & Composers** | 188 | `app/specialists/` — per-specialist LangGraph agents (irene, gary, texas, enrique, vision, wanda, kira, motion_planner, quinn_r, …) + `_shared` audits and composer nodes that assemble decks, motion, and workbook artifacts. |
| **Gates & Workflow Substrate** | 59 | `app/gates/`, `app/manifest/`, `app/cora/` — HIL gate decision modules, the pipeline-manifest compiler, and Cora block-mode dev-graph enforcement that gate and sequence the walk. |
| **Domain Models** | 167 | `app/models/` — Pydantic v2 domain & runtime-state models + emitted JSON schemas: decision-cards, lesson-plan envelopes, contributions side-cars, the data contracts every specialist reads/writes. |
| **Runtime & Transport** | 53 | `app/runtime/`, `app/replay/`, `app/http/`, `app/ledger/`, `app/mcp_server/`, `app/parity/`, `app/audit/` — Postgres checkpointer/retention, resume-and-recover replay, HTTP/MCP transport, parity checks, audit plumbing. |
| **Operator & Developer Tooling** | 147 | `scripts/` — `BaseAPIClient` + concrete API clients, content generators, diagnostics, operator utilities, plus `scratchpad/` live-proofing drivers. |
| **BMAD Agent Skills** | 88 | `skills/` — operator-facing BMAD agent skill packages (`SKILL.md` persona files, reference contracts, helper scripts) for the custom personas Marcus routes to. |
| **Project Root & Configuration** | 4 | Top-level env templates, git/coverage attributes, tooling artifacts. |

---

## 3. Key Concepts & Patterns

**Manifest-compiled graph.** The runner does not hard-code the pipeline. `app/manifest/loader.py` + `compiler.py` + `schema.py` read a YAML manifest describing nodes/edges/gates, validate it, and compile a LangGraph `StateGraph`. "Manifest-as-graph-config" is what makes runs deterministic and reproducible.

**The two-walk production runner.** `app/marcus/orchestrator/production_runner.py` executes a trial as **two LangGraph walks**: the *start walk* runs until the first human gate (G1) and pauses; the *continuation walk* resumes and handles every later gate. ⚠️ **Gate-pause side effects (storyboard/chooser/picker publish) must be wired into BOTH walks** or they silently never fire for G2B+ (a known, real gotcha).

**The 9-node specialist scaffold.** Every specialist is built from one canonical shape defined in `app/specialists/_scaffold/contract.py` + `graph.py` (`receive → plan → act → verify → reflect → gate → finalize → handoff` + a `build_<name>_graph` factory). Understand it once and every agent reads the same way. The `dispatch_adapter.py` builds each specialist's input state and invokes its compiled sub-graph uniformly.

**RunState + the return contract.** `app/models/state/run_state.py` is the single state aggregate threaded through every node — the most depended-upon module in the codebase. `specialist_return.py` defines the shape every specialist hands back, so the runner treats them all identically.

**HIL gates & DecisionCards.** At each gate the pipeline pauses and surfaces a **DecisionCard** for an operator verdict; `app/gates/resume_api.py` rebuilds run state from the stored card + verdict and resumes the walk. `OperatorVerdict` records the decision with tamper-forbidding validators. Each gate (G1–G6+) is contract-pinned by a versioned JSON Schema under `app/models/decision_cards/schema/`.

**ProductionEnvelope carrier.** `app/models/runtime/production_envelope.py` is the append-only side-car that collects every `SpecialistContribution` with content-addressed provenance digests. It is deliberately the **most robust structure in the system** — every future consumer (enrichment, workbook, multi-asset) reads from it, so it is schema-validated, versioned, fail-loud, and append-only. Treat it as a protected invariant.

**Sanctum-lock.** Specialists that carry curated references (e.g. Texas) assert their references manifest is unchanged and raise a `SanctumLockViolation` on drift — reproducibility protection against silent reference tampering.

**Model cascade as data.** Specialists don't choose LLMs in code. A per-specialist `model_config.yaml` declares the model tier; `app/runtime/cascade_config.py` validates that every referenced model has a pricing entry and **fails loud** otherwise. Model/cost policy stays auditable data, not buried logic.

**Learning ledger.** `app/ledger/emitter.py` writes verdict/override events **idempotently** to the Postgres `ledger_events` table (`app/ledger/schema.sql`); `events.py` defines their shape. This is how the system remembers operator decisions across trials so patterns (per-gate reject rates, overrides) can be mined later.

**Protected invariants (do not regress).** Two are emphasized in the codebase and enforced by `_shared` audits: **VO ↔ on-screen alignment** and **source-detail → Gamma conveyance**. `voice_provider_text.py` audits that voice/rhetorical annotations stay *contained within* the source narration and never introduce new content.

---

## 4. Guided Tour (recommended reading order)

A 12-stop walk from the operator's-eye view inward to the substrate:

1. **Marcus-SPOC operator surface** — `app/marcus/cli/marcus_spoc.py`. The single thing a course author talks to: a conversational CLI that narrates each gate, runs the styleguide picker, and drives the runtime.
2. **The two-walk production runner** — `app/marcus/orchestrator/production_runner.py`, `dispatch_adapter.py`. The core engine Marcus drives; start-walk-to-G1 then continuation walk; dispatch adapter hands work to specialists.
3. **The manifest-compiled graph** — `app/manifest/compiler.py`, `loader.py`, `schema.py`, `README.md`. How the pipeline is compiled from YAML, not hard-coded.
4. **RunState & shared state models** — `app/models/state/run_state.py`, `_base.py`, `specialist_return.py`. The one model everything is threaded on, and the uniform return shape.
5. **The 9-node specialist scaffold** — `app/specialists/_scaffold/contract.py`, `graph.py`. The canonical lifecycle that makes a dozen agents feel like one system.
6. **The specialists at work** — `irene/graph.py` (narration, two-pass), `gary/graph.py` (Gamma slides), `texas/graph.py` (cited retrieval), `enrique/graph.py` (TTS), `vision/graph.py` (slide perception).
7. **Model cascade & per-specialist config** — `app/runtime/cascade_config.py`, `app/specialists/gary/model_config.yaml`. Model tier and cost policy as auditable YAML.
8. **Human-in-the-loop gates** — `app/gates/resume_api.py`, `errors.py`, `app/models/state/operator_verdict.py`, `decision_cards/_base.py`. Where the two-walk design earns its shape.
9. **Gate DecisionCard schemas** — `app/models/decision_cards/schema/g1..g4.v1.schema.json`. The frozen, versioned contracts between emitter and rendering surface.
10. **The ProductionEnvelope carrier** — `app/models/runtime/production_envelope.py`, `production_trial_envelope.py`. The append-only, provenance-stamped side-car.
11. **The learning ledger** — `app/ledger/emitter.py`, `events.py`, `schema.sql:ledger_events`. Append-only Postgres event log for reproducibility.
12. **Cost accounting & the operator picker** — `app/runtime/economics.py`, `trial_economics_report.py`, `styleguide_picker.py`. Per-agent trial cost from LangSmith traces, and the pre-spend styleguide choice.

---

## 5. File Map — key entry points by layer

**Marcus Orchestration** (`app/marcus/`)
- `cli/marcus_spoc.py` — operator conversational entry point (the SPOC surface)
- `cli/marcus_interlocutor.py`, `cli/trial.py` — stop-and-chat REPL + trial driver
- `orchestrator/production_runner.py` — two-walk trial engine (start / continue / resume / recover)
- `orchestrator/dispatch_adapter.py` — builds specialist state, compiles & invokes specialist sub-graphs
- `orchestrator/styleguide_picker.py`, `chooser_publisher.py`, `storyboard_publisher.py`, `picker_publisher.py`, `gh_pages_publish.py` — gate-artifact publishing surfaces
- `lesson_plan/` — G0 enrichment, coverage annotation/gate/receipt, Irene refinement, blueprint co-author, workbook producer
- `facade.py` — orchestration facade

**Specialist Agents** (`app/specialists/`)
- `_scaffold/contract.py`, `_scaffold/graph.py` — the canonical 9-node scaffold
- `irene/graph.py` (2.3k-line two-pass narration engine) + `irene_pass1/` (clustering + min-cluster-floor)
- `gary/_act.py` (~1.1k-line Gamma dispatch/normalization), `styleguide_library.py`, `learned_dependencies.py`
- `texas/graph.py`, `texas/_act.py` — retrieval + sanctum-lock
- `enrique/_act.py` — directed ElevenLabs TTS narration assembly
- `vision/provider.py`, `quinn_r/` (quality-control/grounding), `motion_planner/_act.py`, `kira/_act.py`, `wanda/_act.py`
- `_shared/voice_provider_text.py`, `voice_direction_map.py`, `source_fidelity_audit.py` — protected-invariant enforcers

**Gates & Workflow Substrate**
- `app/gates/resume_api.py`, `errors.py`, `app/gates/section_*/poll_surface.py` (per-section HIL poll surfaces)
- `app/manifest/compiler.py`, `loader.py`, `schema.py` — manifest → StateGraph
- `app/cora/graph.py` — Cora block-mode dev-graph enforcement

**Domain Models** (`app/models/`)
- `state/run_state.py`, `state/_base.py`, `state/operator_verdict.py`, `state/specialist_return.py`
- `runtime/production_envelope.py`, `runtime/production_trial_envelope.py`, `runtime/trial_economics_report.py`
- `decision_cards/` (G0–G6 Pydantic models) + `decision_cards/schema/*.v1.schema.json`

**Runtime & Transport**
- `runtime/cascade_config.py`, `economics.py`, `compiled_graph_digest.py`, `override_api.py`, `sanctum_watcher.py`
- `ledger/emitter.py`, `events.py`, `schema.sql`; `replay/parity_comparison.py`, `regression.py`

**Operator & Developer Tooling** (`scripts/`)
- `api_clients/base_client.py` (`BaseAPIClient` retry/backoff/pagination) + concrete clients (Canvas, Descript, ElevenLabs, Kling, Notion, Panopto, Qualtrics, Wondercraft, Gamma)
- `operator/build_descript_narrated_lesson.py`, `operator/m3_texas_ceremony*.py`, `operator/scite_oauth_login*.py`

---

## 6. Complexity Hotspots — approach carefully

The graph flags 139 file-level nodes as `complex`. The ones a new developer is most likely to touch and should read slowly:

| File | Why it's a hotspot |
|---|---|
| `app/marcus/orchestrator/production_runner.py` | ~3.2k lines, 67 functions; the two-walk engine + primary import hub. Central to almost everything. |
| `app/marcus/orchestrator/dispatch_adapter.py` | The specialist-invocation seam (state build → compile → invoke → extract). |
| `app/specialists/irene/graph.py` | 2.3k-line two-pass narration authoring engine with figure-fidelity / reading-path / warm-callback gates. |
| `app/specialists/gary/_act.py` | ~1.1k-line Gamma variant dispatch + normalization; CD-owned styleguide resolution. |
| `app/models/state/run_state.py` | The most depended-upon module; changes ripple through every node. |
| `app/models/runtime/production_envelope.py` | Protected-invariant carrier; must stay schema-validated / versioned / append-only. |
| `app/specialists/_shared/voice_provider_text.py` | Enforces the VO-containment protected invariant; subtle correctness constraints. |
| `app/manifest/compiler.py` + `schema.py` | Pipeline topology compilation; errors here break determinism for the whole run. |
| `app/marcus/cli/marcus_spoc.py` / `marcus_interlocutor.py` | Operator surface + deterministic guard so the chatting LLM never drives the engine. |
| `scripts/api_clients/base_client.py` | Shared base for 10 concrete API clients (retry/backoff/error hierarchy). |
| `app/runtime/economics.py` | LangSmith-trace cost accounting; external-dependency sensitive. |
| `app/marcus/lesson_plan/*` (blueprint, coverage, g0_enrichment, irene_refinement) | Dense pre-planning/enrichment logic feeding the downstream consumption loop. |

---

## 7. Getting Started Checklist

1. **Read the guardrail** in `CLAUDE.md` and `docs/STATE-OF-THE-APP.md` — the SPOC-is-the-goal framing governs every change.
2. **Follow the guided tour** (§4) in order — it's designed to build the mental model from operator surface to substrate.
3. **Trace one run** — start at `marcus_spoc.py`, follow `production_runner.py` → `dispatch_adapter.py` → one specialist's `build_<name>_graph`, and watch `RunState` thread through.
4. **Understand a gate** — read `gates/resume_api.py` with a DecisionCard schema (`decision_cards/schema/g1.v1.schema.json`) open beside it.
5. **BMAD methodology** — production/dev work runs through BMAD workflows + party-mode + a dev agent (see `CLAUDE.md` §"BMAD sprint governance"). Activate **Marcus first** for anything production-shaped (`skills/bmad-agent-marcus/SKILL.md`).
6. **Explore interactively** — run `/understand-dashboard` to browse the graph, or `/understand-chat` to ask questions about specific components.

---

*Generated from `.understand-anything/knowledge-graph.json` (commit `b3ab2137`, 2026-07-05). Regenerate with `/understand` then `/understand-onboard`.*
