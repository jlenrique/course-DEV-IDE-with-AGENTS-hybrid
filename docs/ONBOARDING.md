# ONBOARDING — `course-dev-ide-with-agents`

> **One-line elevator:** Collaborative intelligence infrastructure for course content production — a deterministic, manifest-compiled orchestrator (operator surface: **Marcus-SPOC**) drives a roster of ~20 LangGraph specialist agents through gated, human-in-the-loop production of narrated lessons (with video/animation), with tamper-evident operator verdicts and a learning ledger.

**Languages:** Python (3.11+), Markdown, Jinja2, JSON, YAML, JavaScript, PowerShell, Shell, SQL
**Core frameworks:** LangChain, LangGraph, Pydantic v2 (plus FastAPI/Uvicorn, httpx, Pytest in the runtime/tooling layers)
**Branch (at analysis):** `dev/p5-downstream-consumption-2026-06-26` (severed from `upstream/master` since 2026-04-24)
**Status (2026-06-27):** Migration SHIPPED (commit `97842ac`, 2026-04-27); Slab 7 orchestrational arc CLOSED. **Braid arc COMPLETE:** the **Marcus-SPOC** conversational surface (stop-and-chat LLM REPL with a deterministic guard so the chatting model never drives the engine), the research-citation leg (live Scite OAuth → Texas retrieval → cited references), and the learner-workbook companion (Markdown→DOCX) are all proven live; the clustered + per-sub-slide A/B run is published to Descript, and the **Vision** slide-perception specialist has landed. **Most recent substrate (pre-planning / G0-enrichment cycle):** LO canonicalization + Irene pass-1 LO refinement, P2 pedagogy annotation, the **07D.5 motion-planner producer** (deterministic, between 07D and 07E), and the **P5 downstream-consumption loop** — the workbook producer now consumes the enriched corpus (loop CLOSED, live-proven at `f07e89c`).

> This guide is generated from `.understand-anything/knowledge-graph.json` (commit `0a9fc95`, analyzed 2026-06-27, incremental refresh — 377 files re-analyzed across 18 batches). **Code-only scope:** `app/` + `scripts/` + `skills/` per `.understand-anything/.understandignore`; `docs/`, `_bmad*/`, `tests/`, `runs/` are intentionally excluded from the graph.

---

## 1. Read this first

Before touching any code:

1. **README.md** — repo orientation table; pick the row that matches your role.
2. **CLAUDE.md** — project-level agent/operator instructions, sprint governance, push cadence, deferred-inventory governance.
3. **This guide** — architectural mental model.
4. Then go to the role-specific doc the README points you at:
   - **Operator** → `docs/operator/trial-run-runbook.md`
   - **Developer** → `docs/dev-guide.md` + `docs/dev-guide/langgraph-migration-guide.md`
   - **Admin** → `docs/admin-guide.md` + `.env.example`
   - **Agent embodying a BMAD persona** → `docs/agent-environment.md` + the persona's `skills/bmad-agent-<name>/SKILL.md`

---

## 2. Mental model in 90 seconds

```
    operator
       │
       │   Marcus-SPOC (LLM stop-and-chat REPL) · CLI · MCP/FastAPI
       ▼
┌─────────────────┐      compile_run_graph()       ┌────────────────────────────┐
│ runtime orch.   │ ──────────────────────────────▶│  pipeline-manifest.yaml    │
│  (app/marcus/)  │                                │  → LangGraph StateGraph    │
└────────┬────────┘                                └────────────┬───────────────┘
         │                                                      │
         │ ProductionDispatchAdapter.invoke_specialist(...)     │
         ▼                                                      ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  ~20 specialists, each a 9-node LangGraph subgraph                        │
│  receive → plan → act → verify → reflect → emit_spans →                   │
│  gate_decision (LangGraph interrupt) → finalize → handoff                 │
└────────────────────────────┬─────────────────────────────────────────────┘
                             │ interrupt({"gate_id": ...})
                             ▼
              ┌─────────────────────────────────┐
              │  Operator HIL gate              │
              │  - DecisionCard issued          │
              │  - operator picks verb          │
              │  - OperatorVerdict signed       │
              │  - resume_from_verdict() →      │
              │    Command(resume=…) into graph │
              └─────────────────────────────────┘
```

Everything else (Pydantic contracts, JSON schemas, sanctum templates, BMAD skills, tooling) is scaffolding around this loop. The deterministic guard at the SPOC layer is the load-bearing safety property: the **human's verdict**, never the LLM's narration, advances the run.

---

## 3. Architecture — eight layers

The codebase is organized into eight architectural layers (773 file-level nodes total). The relationship is roughly **bottom-up**: domain-models is the foundation; orchestration + specialists + gates do the work; runtime/transport is persistence + serving; tooling, agent-skills, and project-root are auxiliary.

### 3.1 Domain Models — Pydantic v2 source-of-truth (167 files) · `layer:domain-models`

The single source of truth for what flows through the system. Every contract change starts here.

- `app/models/state/run_state.py` — **RunState**, the Pydantic root threaded through every specialist LangGraph as shared run context (**the single most depended-upon file**).
- `app/models/state/_base.py` — reusable validators (timezone-aware datetimes, UUID4 enforcement) every model reuses (the #2 most depended-upon file).
- `app/models/state/specialist_envelope.py` + `specialist_return.py` — base classes every specialist's I/O extends (`<Name>Envelope` / `<Name>Return`).
- `app/models/decision_cards/` — G0–G6 DecisionCard models + their `schema/*.v1.schema.json` pins.
- `app/models/operator_verdict_section_*.py` + `app/models/schemas/operator_verdict.schema.json` — per-section OperatorVerdict envelopes with closed-enum verb constraints and verb↔payload consistency validators.
- `app/models/perception/perception_artifact.py` — slide-perception artifact contract consumed by the Vision specialist (fidelity-perception arc).
- `app/models/registry.yaml` + `app/models/runtime/production_trial_envelope.py` — model-resolution catalog + the production trial's data spine (edge-key projection, vocabulary version, provenance, builder identity).
- `app/models/trial3_transcript.py` — Trial-3 gate-event transcript schema.

### 3.2 Specialist Agents & Composers — the working agents (188 files) · `layer:specialist-agents-composers`

Per-specialist LangGraph agents, the Cora block-mode sidecar, and section composers. Each specialist lives in `app/specialists/<name>/` with the same shape:
- `graph.py` — builds the 9-node `StateGraph` via `build_<name>_graph()`.
- `_act.py` (heavy specialists) — the LLM-calling work; usually the only non-trivial node.
- `state.py` — `<Name>Envelope` + `<Name>Return` models (each pins `specialist_id` and subclasses the shared base classes in `app/models/state`).
- `payload_contract.py` (Gary, Quinn-R, Vera, Vision) — governance contract enumerating consumed payload keys.
- `__init__.py` — package barrel re-exporting the builder.

**The canonical 9-node pattern lives in `app/specialists/_scaffold/graph.py` — read this once and you've read 80% of every specialist.** Conformance is enforced by `_scaffold/contract.py`.

| Role | Specialists |
|---|---|
| Operator-instruction parsing | Aria, Cd (Dan), Kim, Mira, Tamara, Vyx |
| Retrieval / verification | **Texas** (disciplined retrieval, sanctum lock), **Tracy** (retrieval-intent planner), **Vera** (multimodal G0–G4 verification) |
| Authoring | **Irene** + **Irene-Pass1** (two-pass figure-grounded narration) |
| Content emission | **Gary** (Gamma decks), **Kira** (Kling motion video), **Enrique** (ElevenLabs voice/TTS), **Wanda** (Wondercraft audio), **motion_planner** (deterministic 07D.5 motion-plan producer that self-feeds Kira) |
| Quality / fidelity | **Quinn-R** (G5 fidelity-QA review), **Vision** (slide-perception over rendered PNGs) |
| Consumption | **workbook_producer** (the P5 leg — consumes the enriched corpus into the Markdown→DOCX learner workbook) |
| Composition | `app/composers/section_02a/` (corpus → directive), `app/specialists/compositor/_act.py` (asset assembly), `app/specialists/narration_join.py` |

Shared helpers live in `app/specialists/_shared/` — notably `figure_tokens.py` (numeric/figure-token extraction) and `source_fidelity_audit.py`, the mechanism that keeps narration honest by checking that voiceover only speaks figures actually present on the slide.

### 3.3 Marcus Orchestration — the conductor (99 files) · `layer:marcus-orchestration`

Marcus is the runtime orchestrator process (*not* the BMAD persona — the production-runtime engine).

- `app/marcus/cli/marcus_interlocutor.py` + `marcus_spoc.py` — **Marcus-SPOC**, the operator-facing conversational surface: an LLM-driven stop-and-chat REPL that (in the planned front-door) picks the workflow, then narrates each gate's DecisionCard and lets the operator converse, plus the scripted gate-by-gate production trial. A deterministic guard ensures the chatting model drives the engine zero times. (Operator-facing callsign only; the package, function names, and `"marcus"` model tier are unchanged.)
- `app/marcus/cli/trial.py` + `gate_shims/` — CLI trial entry points and per-gate shims (G1–G4a).
- `app/marcus/orchestrator/production_runner.py` — the trial engine that walks the compiled LangGraph, pauses at each gate, and resumes after the operator's verdict. ⚠️ **complex** (~3,200 lines; highest fan-out in the project). **Note the two distinct node walks** — the start walk (runs to G1) and the resume/recover continuation (handles every later gate) — both of which must fire gate side-effects (storyboard/chooser publish), or G2B+ side-effects silently never fire.
- `app/marcus/orchestrator/dispatch_adapter.py` — bridges `ProductionEnvelope` → specialist `RunState`; compiles per-specialist subgraphs. ⚠️ **complex**.
- `app/marcus/orchestrator/gate_runner.py` — enforces the Marcus duality boundary, calibration tripwire, and engagement-decay reporting at each gate. ⚠️ **complex**.
- `app/marcus/orchestrator/storyboard_publisher.py` + `chooser_publisher.py` — publish storyboard/segment-manifest + A/B chooser artifacts at gate pauses (clustering the narration arc). ⚠️ **complex**.
- `app/marcus/orchestrator/research_wiring.py` + `research_citation.py` — select a retrieval posture, dispatch Texas, then mint citation IDs / hash sources / gate entries so claims are backed by real, auditable references.
- `app/marcus/orchestrator/loop.py` — the **4A loop** (intake → tune → reassess → plan-lock). ⚠️ **complex**.
- `app/marcus/lesson_plan/` — lesson-plan domain: `schema.py`, `log.py` (append-only event log + `assert_plan_fresh` freshness gate), Gagne diagnosis, fit reports, `quinn_r_gate.py`, `collateral_spec.py`.
- **Pre-planning / G0-enrichment substrate (most recent arc):**
  - `app/marcus/lesson_plan/g0_enrichment.py` + `app/marcus/orchestrator/g0_enrichment_wiring.py` — G0 corpus enrichment: enumerate the corpus, split + typed-classify components, derive provisional learning objectives. ⚠️ **complex**.
  - `app/marcus/lesson_plan/learning_objective.py` — the canonical, provenance-anchored, lifecycle-aware LearningObjective domain model (source-adequacy assessment + lifecycle state machine). ⚠️ **complex**.
  - `app/marcus/lesson_plan/irene_refinement.py` — Irene pass-1 LO refinement engine (offline-deterministic or live-LLM). ⚠️ **complex**.
  - `app/marcus/lesson_plan/pedagogy_annotation.py` — P2 pedagogy annotation: teachable ordering + teaches-after dependency derivation. ⚠️ **complex**.
  - `app/marcus/lesson_plan/workbook_enrichment.py` + `workbook_producer.py` — **the P5 consumption loop**: projects the enriched corpus (further-reading, exercises, Bloom-mapped LOs, authoritative citations) into the learner workbook (Markdown + DOCX), with numeric/citation fidelity audit.
- `app/marcus/facade.py` — single-process aggregator: bootstraps run state; exposes ask / run_step / run_4a; resolves the sanctum activation digest. ⚠️ **complex**.

### 3.4 Gates & Workflow Substrate — HIL machinery (70 files) · `layer:gates-workflow-substrate`

The HIL gate substrate that makes LangGraph `interrupt`/`Command` work:

- `app/gates/resume_api.py` — `register_decision_card`, `compute_decision_card_digest`, `resume_from_verdict`. **This is the entire gate API.** ⚠️ **complex**.
- `app/gates/section_*/poll_surface.py` — per-section operator gate surfaces; each loads directives, computes digests, builds DecisionCards, and validates/replays the operator verdict across CLI/HTTP/MCP transports.
- `app/gates/section_07c/chooser_html_emitter.py` — renders the A/B chooser HTML surfaced at the variant gate.
- `app/manifest/compiler.py` — **the bridge**: declarative `PipelineManifest` (YAML) → LangGraph `StateGraph`. Owns topology compile, compile-time contract lint, and lane validation (`run_graph` vs `dev_graph`). ⚠️ **complex**.
- `app/manifest/schema.py` — `PipelineManifest` / `NodeSpec` / `EdgeSpec`.
- `app/parity/contracts/` — parity-contracts framework (declaration, decorator, registry, sanctum alignment, self-registration audit).
- `app/cora/` — the **Cora dev-graph**: a separate LangGraph instance for story handlers (a D4 invariant — run-lane and dev-lane are distinct graphs).
- `app/ledger/` + `app/audit/` — learning-event ledger + append-only audit chain.

### 3.5 Runtime & Transport — persistence + serving (36 files) · `layer:runtime-transport`

- `app/runtime/server.py` — FastAPI runtime exposing an invoke endpoint with a Postgres status probe over the minimal graph.
- `app/runtime/checkpointer.py` — `AsyncPostgresSaver` factory for the LangGraph checkpointer.
- `app/runtime/override_api.py`, `economics.py`, `cascade_config.py`, `retry_policy.py`, `retention_policy.py` — override registry, LangSmith cost reporting, pricing/cascade loader, and operational hardening.
- `app/mcp_server/server.py` — MCP server scaffold surfacing gate-decision tools to MCP clients.
- `app/http/gate_endpoint.py` — FastAPI HTTP gate transport.
- `app/replay/regression.py` + `parity_comparison.py` — replay/parity harness for closed trials. ⚠️ **complex**.

### 3.6 Operator & Developer Tooling — scripts (121 files) · `layer:operator-developer-tooling`

- `scripts/api_clients/` — Gamma, Kling, ElevenLabs, Wondercraft, Descript, Canvas, Notion, Qualtrics, Panopto — all on a shared `BaseAPIClient` with a common error hierarchy.
- `scripts/operator/` — operator ceremonies, including `build_descript_narrated_lesson.py` and the `scite_oauth_login*.py` flows (headed-Playwright OAuth → reusable refresh token) that closed the research live-leg.
- `scripts/analysis/reading_path_*.py` — the reading-path / slide-perception measurement suite (corpus scan, holdout perceive, P2-4b run/score/measure).
- `scripts/generators/v42/` — the Jinja2 v4.2 prompt-pack generator (`manifest.py` + section/partial templates).
- `scripts/validators/pass_2_emission_lint.py`, `scripts/fidelity_drift_check.py`, `scripts/source_fidelity_report.py` — fidelity/emission validators.
- `scripts/dev/` — dev-time guardrails (orphan/mojibake/co-commit checks, flakiness measurement, `init_postgres.sql`).

### 3.7 BMAD Agent Skills — personas (88 files) · `layer:bmad-agent-skills`

Two coexisting layouts (see CLAUDE.md "Custom agents vs registered BMAD personas"):

- **Skill-quarantine tree:** `skills/bmad-agent-<name>/SKILL.md` per persona — the operator-facing activation contract.
- **Sanctum tree (BMB):** `_bmad/memory/bmad-agent-<name>/` — persistent persona + continuity. *(Out of this analysis's code-only scope.)*

Notable personas: **Marcus** (orchestrator), Irene/Gary/Vera/Texas/Quinn-R/Wanda/Dan/Enrique/Desmond/Tracy/Tamara (specialists), Kira (Kling video), Cora (dev-graph), plus BMAD stock personas (Mary, Murat, Amelia). On a cold start, read `skills/bmad-agent-marcus/SKILL.md` first when production is in scope.

### 3.8 Project Root & Configuration (4 files) · `layer:project-root-configuration`

`.env.example`, `.gitattributes`, and tooling-ignore files. Read `.env.example` before any local run — it documents every API key and connection setting (OpenAI, ElevenLabs, Gamma, Postgres, Scite).

---

## 4. Guided tour (12 steps, ~45 min)

The recommended reading path the knowledge graph generated — a course-production run, end to end:

1. **Marcus: The Operator Surface** — `app/marcus/cli/__main__.py` + `app/marcus/facade.py` + `app/marcus/cli/marcus_spoc.py`. The single operator-facing entry; the conversational SPOC narration layer.
2. **The Production Engine** — `app/marcus/orchestrator/production_runner.py` + `supervisor.py` + `routing.py`. The trial loop; mind the two node walks.
3. **The Manifest Compiler** — `app/manifest/compiler.py` + `loader.py` + `lanes.py` + its README. Declarative `PipelineManifest` → LangGraph `StateGraph`.
4. **Shared State & Domain Contracts** — `app/models/state/run_state.py` + `_base.py` + `specialist_envelope.py` + README. The two most depended-upon files; read them early and everything unlocks.
5. **Decision Cards & Schema Pins** — `app/models/decision_cards/base.py` + the `decision_card_base` / `g1` JSON Schema pins + README. The frozen-hash artifacts the operator produces at each pause.
6. **Human-in-the-Loop Gates** — `app/gates/resume_api.py` + `verdict.py` + `guardrails.py`. What makes a run pausable at G1/G2C/G3/G4 and resumable on operator verdict.
7. **The Specialist Scaffold** — `app/specialists/_scaffold/graph.py` + `contract.py` + expertise README. The canonical 9-node lifecycle; the single most important abstraction.
8. **Pedagogy & Retrieval Specialists** — `app/specialists/irene/graph.py` + `irene_pass1/graph.py` + `texas/graph.py`. Two-pass figure-grounded authoring + disciplined retrieval.
9. **Media Production Specialists** — `app/specialists/{gary,vera,kira,motion_planner}/graph.py`. Decks, fidelity gates, Kling video, and the deterministic 07D.5 motion planner — scaffolds that differ only in their `act` integration.
10. **Enrichment & Workbook Consumption (P5)** — `app/marcus/lesson_plan/g0_enrichment.py` + `app/specialists/workbook_producer/_act.py` + `lesson_plan.v1.schema.json`. How the enriched corpus is built and then *consumed* downstream.
11. **Audit Ledger & Persistence** — `app/ledger/` (`ledger_events` table) + `app/ledger/emitter.py` + `scripts/dev/init_postgres.sql`. The system's durable, queryable memory in Postgres.
12. **Runtime, MCP & Operator Tooling** — `app/runtime/server.py` + `app/mcp_server/server.py` + `scripts/api_clients/base_client.py`. How the system is hosted, served, and integrated with external vendors.

---

## 5. Key concepts new contributors must internalize

| Concept | Where to look | Why it matters |
|---|---|---|
| **Pipeline manifest is the source of truth** | `state/config/pipeline-manifest.yaml` + `app/manifest/compiler.py` | Topology is data, never hardcoded. Add a specialist via manifest edit + dispatch-registry entry. |
| **Specialists have a fixed 9-node shape** | `app/specialists/_scaffold/graph.py` | Conformance is enforced by `_scaffold/contract.py`; deviations fail at compile time. |
| **Gates use LangGraph `interrupt`** | `app/gates/resume_api.py` + any `gate_decision` node | All HIL = `interrupt({...})`; resume = `Command(resume=verdict)`. There is no "manual" gate pattern. |
| **The SPOC's deterministic guard** | `app/marcus/cli/marcus_interlocutor.py` | The chatting LLM narrates but must drive the engine zero times; only the human verdict advances the run. |
| **Decision cards are tamper-evident** | `compute_decision_card_digest` in `resume_api.py` | SHA-256 over canonical-JSON; nonces consumed once; verdict envelopes signed. |
| **Two LangGraph lanes exist** | `app/manifest/compiler.py` vs `app/cora/graph.py` | Run-lane and dev-lane (Cora) are *separate* `StateGraph` instances (D4 invariant). |
| **production_runner has TWO node walks** | `app/marcus/orchestrator/production_runner.py` | Gate-pause side-effects (storyboard/chooser publish) must be added to BOTH the start walk and the resume/recover walk, or they silently never fire for G2B+. |
| **Figure-grounding bar is lenient by design** | `app/specialists/_shared/{figure_tokens,source_fidelity_audit}.py` | VO may speak any numeral present anywhere on the chosen slide; only a numeral nowhere on the slide is a violation. |
| **Pack version bumps are governance, not technical** | CLAUDE.md "Pipeline lockstep regime" + `docs/dev-guide/pipeline-manifest-regime.md` | Tier-2/Tier-3 bumps need party-mode consensus BEFORE dev opens. |
| **Verify via shipped deps, not operator CLIs** | `docs/dev-guide/migration-ac-sandbox-inventory.json` | Dev-agent tests use `psycopg` / `httpx`; only operator-gated ACs may call `docker` / `psql` / `gh`. |
| **BMAD-persona Marcus ≠ Marcus-SPOC** | `skills/bmad-agent-marcus/SKILL.md` vs `app/marcus/` | Two systems that share no memory. **BMAD-persona Marcus** (skill + sanctum) plans and talks *about* the project with no connection to a live run. **Marcus-SPOC** (`app/marcus/cli/marcus_interlocutor.py`) is the operator-facing surface of the runtime: it converses *only inside a live trial*, backed by a runtime LLM grounded on the generated capability overlay (not the persona) — and the human's confirmed verdict, never the chatting LLM, advances the run. The orchestration *engine* itself (`production_runner` + manifest compiler) is deterministic, not an agent. |

---

## 6. Complexity hotspots — read carefully, change cautiously

The graph flags **127 file-level nodes as `complex`**. The ones a new contributor most often needs to touch (and where most regressions originate):

### Critical path — touched by almost every change
- `app/manifest/compiler.py` — manifest → StateGraph compiler; lint failures here block all trials.
- `app/marcus/orchestrator/production_runner.py` — the production trial loop (two node walks).
- `app/marcus/orchestrator/dispatch_adapter.py` — envelope ↔ specialist state translation.
- `app/marcus/orchestrator/gate_runner.py` — duality boundary + calibration tripwire at each gate.
- `app/specialists/_scaffold/graph.py` — canonical 9-node pattern + conformance asserts.
- `app/gates/resume_api.py` — gate digest + resume logic.

### Orchestration & lesson-plan hotspots
- `app/marcus/facade.py`, `orchestrator/{loop,fanout,storyboard_publisher,conversation_persistence}.py`.
- `app/marcus/lesson_plan/{schema,log,blueprint_coauthor,gagne_diagnostician,quinn_r_gate,coverage_manifest,collateral_spec,workbook_producer}.py` — touching one usually means a coordinated edit across several.
- **Pre-planning substrate:** `app/marcus/lesson_plan/{g0_enrichment,learning_objective,irene_refinement,pedagogy_annotation,workbook_enrichment}.py` + `app/marcus/orchestrator/g0_enrichment_wiring.py`.
- `app/marcus/orchestrator/{maya_walkthrough,trial_smoke_harness,m3_trial}.py` — demo/smoke harnesses.

### Specialist hotspots — `_act.py` is where the work happens
- `app/specialists/{gary,texas,enrique,kira,quinn_r,tracy,irene_pass1,compositor,dan}/_act.py`.
- Flagged graphs: `{irene,gary,quinn_r,texas,tamara,desmond,cd,aria}/graph.py`.
- `app/specialists/irene/authoring/pass_2_template.py` — Pydantic source-of-truth with cross-artifact `model_validator`.
- `app/specialists/quinn_r/quality_control_dispatch.py` — G5 grounding + dynamically loaded validators.

### Runtime / replay hotspots
- `app/runtime/{override_api,economics,cascade_config}.py`.
- `app/replay/{regression,parity_comparison}.py`.

### Trust-but-verify hotspots
- `app/parity/contracts/_audit.py` — self-registration audit; failures here block builds.
- `app/audit/chain.py` — append-only with monotonic-timestamp + parent-trace invariants.

---

## 7. Your first contribution — recommended path

1. **Set up the env** — Python 3.11+, `python -m venv .venv`, `.venv/Scripts/pip install -e .`, copy `.env.example` → `.env`, install Postgres natively (no Docker per `memory/project_no_docker.md`).
2. **Run preflight** — `scripts/setup/ready_for_trial.ps1` (Windows) or `.sh` (POSIX). Confirm green.
3. **Read the tour** — work through §4 above, file by file.
4. **Run the test suite** — `.venv/Scripts/pytest` (tests live under `tests/`, excluded from this code-only analysis scope).
5. **Pick up a deferred-inventory item** — `_bmad-output/planning-artifacts/deferred-inventory.md` is the authoritative backlog. Cross-reference the next-session pointer at `_bmad-output/implementation-artifacts/next-session-start-here.md`.
6. **Follow BMAD sprint governance** — CLAUDE.md §"BMAD sprint governance": spec → party-mode green-light → dev → bmad-code-review → done.
7. **For Lesson Planner dev-stories (Epics 28-32):** read `docs/dev-guide/pydantic-v2-schema-checklist.md` + `dev-agent-anti-patterns.md` + `story-cycle-efficiency.md` before opening.

---

## 8. Operator quick-start (conversational trial)

```powershell
# Pre-flight
$env:PYTHONIOENCODING="utf-8"
node scripts/heartbeat_check.mjs   # API reachability

# Conversational SPOC (stop-and-chat at each gate)
.\.venv\Scripts\python.exe -m app.marcus.cli.marcus_spoc `
    --input course-content/courses/<lesson-slug>/ `
    --operator-id <your-id>

# Or the scripted CLI trial:
.\.venv\Scripts\python.exe -m app.marcus.cli trial start `
    --preset production --input course-content/courses/<lesson-slug>/ --operator-id <your-id>
# At each gate: review the DecisionCard, file an OperatorVerdict, then `trial resume --trial-id <uuid> --verdict-file <path>`.
```

Full operator playbook: `docs/operator/trial-run-runbook.md`.

---

## 9. References

- **Architectural authority:** `_bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md`
- **Epic backlog:** `_bmad-output/planning-artifacts/epics-langchain-langgraph-migration.md` + `epics.md`
- **Sprint state:** `_bmad-output/implementation-artifacts/sprint-status.yaml`
- **Deferred inventory:** `_bmad-output/planning-artifacts/deferred-inventory.md`
- **Migration guide:** `docs/dev-guide/langgraph-migration-guide.md`
- **Pipeline manifest regime:** `docs/dev-guide/pipeline-manifest-regime.md`
- **Trial methodology:** `docs/trials/methodology.md`
- **Knowledge graph (this analysis):** `.understand-anything/knowledge-graph.json` (1,747 nodes, 3,157 edges, 8 layers, 12-step tour)
- **Interactive dashboard:** run `/understand-anything:understand-dashboard` to launch the Vite-served visualizer (requires the token printed at startup).

---

*Generated 2026-06-27 from `.understand-anything/knowledge-graph.json` at commit `0a9fc95` (incremental refresh; 377 files re-analyzed across 18 batches, 740 unchanged-file nodes preserved). Code-only scope: `app/` + `scripts/` + `skills/` (773 files). Refresh by running `/understand` after substantive changes, then regenerate this guide with `/understand-anything:understand-onboard`.*
