# ONBOARDING — `course-dev-ide-with-agents`

> **One-line elevator:** Collaborative intelligence platform for course content production — a multi-agent orchestrator (**Marcus**) drives ~14 LangGraph specialist agents through gated, human-in-the-loop production of narrated lessons with video/animation, with tamper-evident operator verdicts and a learning ledger.

**Languages:** Python (3.11+), Markdown, JSON, Jinja2, YAML, JavaScript, PowerShell, Shell, SQL
**Core frameworks:** LangChain, LangGraph, FastAPI, Pydantic v2, Pytest, Uvicorn, Jinja2
**Branch:** `dev/langchain-langgraph-foundation` (severed from `upstream/master` since 2026-04-24)
**Status (2026-05-25):** Migration SHIPPED (commit `97842ac`, 2026-04-27); Slab 7 orchestrational arc CLOSED; **first tracked trial (Trial-3) imminent** against the v5 canonical pack.

---

## 1. Read this first

Before touching any code:

1. **README.md** — repo orientation table; pick the row that matches your role.
2. **CLAUDE.md** — project-level agent/operator instructions, sprint governance, push cadence, deferred inventory governance.
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
       │   (CLI today; MCP/FastAPI on deck)
       ▼
┌─────────────────┐      compile_run_graph()       ┌────────────────────────────┐
│  Marcus runtime │ ──────────────────────────────▶│  pipeline-manifest.yaml    │
│  (app/marcus/)  │                                │  → LangGraph StateGraph    │
└────────┬────────┘                                └────────────┬───────────────┘
         │                                                      │
         │ ProductionDispatchAdapter.invoke_specialist(...)     │
         ▼                                                      ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  17 specialists, each a 9-node LangGraph subgraph                        │
│  receive → plan → act → verify → reflect → emit_spans →                  │
│  gate_decision (LangGraph interrupt) → finalize → handoff                │
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

Everything else (Pydantic contracts, JSON schemas, sanctum templates, BMAD skills, tooling) is scaffolding around this loop.

---

## 3. Architecture — eight layers

The codebase is organized into eight architectural layers. The relationship is roughly **bottom-up**: domain-models is the foundation; orchestration + specialists + gates do the work; runtime-infra is persistence/transport; tooling, agent-skills, and project-root are auxiliary.

### 3.1 `layer:domain-models` — Pydantic v2 source-of-truth (160 nodes)

The single source of truth for what flows through the system. Every contract change starts here.

- `app/models/state/run_state.py` — **RunState** Pydantic root; the `state_schema` for every LangGraph instance.
- `app/models/state/specialist_envelope.py` + `specialist_return.py` — base classes every specialist's I/O extends.
- `app/models/dispatch/` — typed `*DispatchInput` / `*DispatchReceipt` / `*DispatchError` triplets per specialist.
- `app/models/decision_cards/` — G0/G1/G2a/G2c/G3/G4/G5/G6 DecisionCard models + JSON Schemas.
- `app/models/operator_verdict_section_*.py` — 14 per-section OperatorVerdict envelopes with closed-enum verb constraints.
- `app/models/registry.py` + `app/models/selector.py` — model-resolution cascade (NFR-X4 audit trail).
- `app/models/trial3_transcript.py` — Trial-3 gate-event transcript schema.

### 3.2 `layer:orchestration` — Marcus LangGraph (72 nodes)

Marcus is the runtime orchestrator process. *Not* the BMAD persona — the production-runtime engine.

- `app/marcus/cli/__main__.py` + `cli/trial.py` — operator entry point (`python -m app.marcus.cli trial start`).
- `app/marcus/orchestrator/production_runner.py` — drives the manifest, handles gate-pause/resume, persists envelopes. ⚠️ **complex**.
- `app/marcus/orchestrator/dispatch_adapter.py` — bridges `ProductionEnvelope` → specialist `RunState`; compiles per-specialist subgraphs.
- `app/marcus/orchestrator/loop.py` — the **4A loop** (intake → tune → reassess → plan-lock). ⚠️ **complex**.
- `app/marcus/lesson_plan/` — lesson-plan domain: schema, blueprint authoring, Gagne diagnosis, fit reports, Quinn-R gate.
- `app/marcus/facade.py` — single-process aggregator for step dispatch, ad-hoc ask, 4A workflow, sanctum/conversation persistence.
- `app/marcus/orchestrator/writers/section_15_bundle.py` — G5 final-handoff bundle (Descript assembly guide).

### 3.3 `layer:specialists` — 14 specialist LangGraph agents (142 nodes)

Each specialist lives in `app/specialists/<name>/` with the same shape:
- `graph.py` — builds the 9-node `StateGraph` via `build_<name>_graph()`.
- `_act.py` (heavy specialists) — the LLM-calling work; the only non-trivial node.
- `state.py` — `<Name>Envelope` + `<Name>Return` Pydantic models.
- `__init__.py` — package barrel re-exporting the builder.

The canonical 9-node pattern lives in `app/specialists/_scaffold/graph.py` — read this once and you've read 80% of every specialist.

| Role | Specialist | Heavy `_act.py`? |
|---|---|---|
| Operator-instructions parsing | Aria, Cd (Dan), Kim, Mira, Tamara, Vyx | parser-only, no `_act.py` |
| Retrieval / verification | **Texas** (retrieval), **Tracy** (intent planner), **Vera** (verification) | yes |
| Authoring | **Irene** (prose, 2-pass), **Irene-Pass1** | yes |
| Content emission | **Gary** (slides), **Kira** (motion), **Quinn-R** (quality review), **Wanda** (audio), **Enrique** (voice/TTS) | yes |
| Section composer | `app/composers/section_02a/composer.py` | composer, not specialist |

### 3.4 `layer:gates-workflow` — gates, Cora dev-graph, parity contracts (67 nodes)

The HIL gate substrate that makes LangGraph `interrupt`/`Command` work:

- `app/gates/resume_api.py` — `register_decision_card`, `compute_decision_card_digest`, `resume_from_verdict`. **This is the entire gate API.**
- `app/gates/party_mode_as_interrupt.py` — wraps multi-agent party-mode consensus as a LangGraph interrupt.
- `app/gates/section_*/poll_surface.py` — per-section operator gate surfaces. Each loads directives, computes digests, builds DecisionCards. ⚠️ several are **complex**.
- `app/manifest/compiler.py` — **the bridge** — declarative `PipelineManifest` (YAML) → `LangGraph StateGraph`. Owns three responsibilities: topology compile, compile-time contract lint, lane validation (`run_graph` vs `dev_graph`). ⚠️ **complex**.
- `app/manifest/schema.py` — `PipelineManifest` / `NodeSpec` / `EdgeSpec`. ⚠️ **complex**.
- `app/cora/graph.py` — **Cora dev-graph**: separate LangGraph instance for story handlers (plan/implement/review/test/close). ⚠️ **complex**.
- `app/parity/contracts/` — parity-contracts framework (declaration, decorator, registry, sanctum alignment, audit).

### 3.5 `layer:runtime-infra` — persistence + transport (48 nodes)

- `app/runtime/checkpointer.py` — `AsyncPostgresSaver` factory for LangGraph checkpointer (`make_checkpointer()`).
- `app/runtime/override_api.py` — in-process override registry + cache-invalidation. ⚠️ **complex**.
- `app/runtime/sanctum_watcher.py` — watchdog-based filesystem watcher for sanctum mutations during runs. ⚠️ **complex**.
- `app/runtime/economics.py` — walks LangSmith traces; computes per-agent cost reports. ⚠️ **complex**.
- `app/runtime/cascade_config.py` — pricing/cascade YAML loader.
- `app/runtime/retry_policy.py` + `retention_policy.py` — operational hardening.
- **Transport layer (three surfaces, same gate API):**
  - `app/http/gate_endpoint.py` — FastAPI HTTP transport.
  - `app/mcp_server/` — MCP stdio server (scaffold; `gate_decide` tool defined but not yet wired to a chat front-end).
  - CLI shims at `app/marcus/cli/gate_shims/g*_shim.py`.
- `app/ledger/` — learning-event ledger emitter + Postgres queries.
- `app/audit/chain.py` — append-only audit chain.
- `app/replay/regression.py` + `parity_comparison.py` — replay harness for closed trials. ⚠️ **complex**.

### 3.6 `layer:tooling` — operator + developer scripts (105 nodes)

- `scripts/setup/first_clone_bootstrap.{ps1,sh}` + `ready_for_trial.{ps1,sh}` — first-clone + trial-readiness preflight.
- `scripts/marcus_capabilities/` — capability registry + per-capability scripts (`pr_pf.py` Preflight ✓, `pr_rc.py` Run-Constants ✓, `pr_hc.py` Health-Check **stub**, `pr_rs.py` Run-Selection **stub**).
- `scripts/api_clients/` — Gamma, Kling, ElevenLabs, Wondercraft, Canvas, Notion, Qualtrics, Panopto, Scite — all on a shared `BaseAPIClient`. Several are ⚠️ **complex**.
- `scripts/generators/v42/` — Jinja2 v4.2 prompt-pack generator package (`pack.md.j2` + 19 section templates + macros/partials).
- `scripts/dev/check_orphans.py`, `check_mojibake.py`, `check_co_commit.py`, `flake_measure_1_1d.py` — dev-time lint/measurement.
- `scripts/operator/m{2,3}_*.py` — milestone ceremonies (Wondercraft, Texas-via-Scite/Notion).
- `scripts/state_management/db_init.py` + `init_state.py` — SQLite coordination DB.
- `scripts/heartbeat_check.mjs` — Node-based env-var + service-reachability check.

### 3.7 `layer:agent-skills` — BMAD personas (88 nodes)

Two coexisting layouts (see CLAUDE.md "Custom agents vs registered BMAD personas"):

- **Skill-quarantine tree:** `skills/bmad-agent-<name>/SKILL.md` per persona — operator-facing activation contract.
- **Sanctum tree (BMB):** `_bmad/memory/bmad-agent-<name>/` — persistent persona + continuity. *(Out of this analysis's scope.)*

Notable personas: **Marcus** (orchestrator), Irene/Gary/Vera/Texas/Quinn-R/Wanda/Dan/Enrique/etc. (specialists), Kira (Kling video), Wondercraft (Wanda), Mary (analyst), Murat (TEA), Amelia (dev).

Sanctum scaffold templates (BOND/CAPABILITIES/CREED/INDEX/MEMORY/PERSONA) live as `*-template.md` files under each agent's `assets/`.

### 3.8 `layer:project-root` — top-level config (4 nodes)

`.env.example`, `.gitattributes`, etc. Read `.env.example` before any local run.

---

## 4. Guided tour (12 steps, 30-45 min)

The recommended reading path the knowledge graph generated:

1. **Project Orientation: Skills Index and Environment** — `README.md` + `skills/` index + `.env.example`.
2. **Operator Entry Point: The Marcus CLI** — `app/marcus/cli/__main__.py` + `cli/trial.py`.
3. **Marcus Orchestrator: Driving Trials Through Gates** — `orchestrator/production_runner.py` + `orchestrator/loop.py`.
4. **The Pipeline Manifest: Declarative Graph Assembly** — `state/config/pipeline-manifest.yaml` + `app/manifest/{schema,compiler}.py`.
5. **The Specialist Scaffold: 9-Node RPAVRSGFH Pattern** — `app/specialists/_scaffold/graph.py` + `_scaffold/contract.py`.
6. **Three Specialists in Practice** — Irene (`irene/graph.py` + `authoring/pass_2_template.py`), Quinn-R (`quinn_r/_act.py`), Compositor.
7. **Gates, HIL, and Party-Mode-as-Interrupt** — `app/gates/resume_api.py` + `gates/party_mode_as_interrupt.py` + a representative `section_*/poll_surface.py`.
8. **Decision Cards: Tamper-Evident Operator Verdicts** — `app/models/decision_cards/g{1,2c,3,4}.py` + `models/state/operator_verdict.py`.
9. **RunState and Envelopes: The Pydantic Source-of-Truth** — `app/models/state/run_state.py` + `models/state/specialist_envelope.py`.
10. **Parity Contracts and the Cora Dev-Graph** — `app/parity/contracts/_audit.py` + `app/cora/graph.py`.
11. **Runtime Infrastructure: Checkpointer, Ledger, FastAPI, MCP** — `app/runtime/checkpointer.py` + `app/ledger/emitter.py` + `app/http/gate_endpoint.py` + `app/mcp_server/server.py`.
12. **BMAD Skills and the v4.2 Pack Generator** — `skills/bmad-agent-marcus/SKILL.md` + `scripts/generators/v42/`.

---

## 5. Key concepts new contributors must internalize

| Concept | Where to look | Why it matters |
|---|---|---|
| **Pipeline manifest is the source of truth** | `state/config/pipeline-manifest.yaml` + `app/manifest/compiler.py` | Topology is data; never hardcoded. Add a specialist via manifest edit + entry in `dispatch-registry.yaml`. |
| **Specialists have a fixed 9-node shape** | `app/specialists/_scaffold/graph.py` | Conformance is enforced by `_scaffold/contract.py`; deviations fail at compile time. |
| **Gates use LangGraph `interrupt`** | `app/gates/resume_api.py` + any `gate_decision` node | All HIL = `interrupt({...})`; resume = `Command(resume=verdict)`. There is no "manual" gate pattern. |
| **Decision cards are tamper-evident** | `compute_decision_card_digest` in `resume_api.py` | SHA-256 over canonical-JSON; nonces consumed once; verdict envelopes signed. |
| **Two LangGraph lanes exist** | `app/manifest/compiler.py::compile_run_graph` vs `app/cora/graph.py` | Run-lane and dev-lane (Cora) are *separate* `StateGraph` instances. D4 invariant. |
| **Pack version bumps are governance, not technical** | CLAUDE.md "Pipeline lockstep regime" + `docs/dev-guide/pipeline-manifest-regime.md` | Tier-2/Tier-3 bumps need party-mode consensus BEFORE dev opens. |
| **Schema-shape stories use a scaffold** | `docs/dev-guide/scaffolds/schema-story/` | Don't re-derive Pydantic shapes from precedent; extend the scaffold stubs. |
| **Verify via shipped deps, not operator CLIs** | `docs/dev-guide/migration-ac-sandbox-inventory.json` | Dev-agent tests use `psycopg` / `httpx`; only operator-gated ACs can call `docker` / `psql` / `gh`. |
| **BMAD Marcus ≠ runtime Marcus** | `skills/bmad-agent-marcus/SKILL.md` (BMAD persona) vs `app/marcus/` (runtime) | Same name, two systems. The BMAD persona plans; the runtime dispatches. |

---

## 6. Complexity hotspots — read carefully, change cautiously

The graph flagged **119 file-level nodes as `complex`** (≥ ~250 LOC with non-trivial logic). The ones a new contributor most often needs to touch (and where most regressions originate):

### Critical path — touched by almost every change
- `app/manifest/compiler.py` — manifest → StateGraph compiler; lint failures here block all trials.
- `app/marcus/orchestrator/production_runner.py` — the production trial loop.
- `app/marcus/orchestrator/dispatch_adapter.py` — envelope ↔ specialist state translation.
- `app/specialists/_scaffold/graph.py` — canonical 9-node pattern + conformance asserts.
- `app/gates/resume_api.py` — gate digest + resume logic.

### Domain hotspots — change with schema-story scaffold
- `app/marcus/lesson_plan/{schema,blueprint_coauthor,blueprint_producer,gagne_diagnostician,quinn_r_gate,coverage_manifest,log}.py` — lesson-plan domain. Touching any of these usually means a coordinated edit across several.
- `app/models/decision_cards/g{0..6}.py` + their `schema/*.v1.schema.json` artifacts.
- `app/models/operator_verdict_section_*.py` — 14 envelopes; verb-payload consistency is enforced by cross-field validators.

### Specialist hotspots — `_act.py` is where the work happens
- `app/specialists/{gary,quinn_r,texas,vera,wanda,kira,enrique,dan,tracy,irene_pass1}/_act.py` and `irene/graph.py`.
- `app/specialists/irene/authoring/pass_2_template.py` — 253-line Pydantic source-of-truth with cross-artifact `model_validator`.

### Composer / poll surface hotspots — Trial-3 surface
- `app/composers/section_02a/composer.py` + `directive_model.py` — corpus → directive composition (G0).
- `app/gates/section_02a/poll_surface.py` + `gates/section_04a/poll_surface.py`.

### Runtime / replay hotspots
- `app/runtime/{override_api,sanctum_watcher,economics,cascade_config}.py`.
- `app/replay/{regression,parity_comparison}.py`.

### Trust-but-verify hotspots
- `app/parity/contracts/_audit.py` — self-registration audit; failures here block builds.
- `app/audit/chain.py` — append-only with monotonic-timestamp + parent-trace invariants.

---

## 7. Your first contribution — recommended path

1. **Set up the env** — Python 3.11+, `python -m venv .venv`, `.venv/Scripts/pip install -e .`, copy `.env.example` → `.env`, install Postgres natively (no Docker per `memory/project_no_docker.md`).
2. **Run preflight** — `scripts/setup/ready_for_trial.ps1` (Windows) or `.sh` (POSIX). Confirm green.
3. **Read the tour** — work through §4 above, file by file.
4. **Run the test suite** — `.venv/Scripts/pytest` (excluded from this analysis's scope but lives under `tests/`).
5. **Pick up a deferred-inventory item** — `_bmad-output/planning-artifacts/deferred-inventory.md` is the authoritative backlog. Cross-reference against the next-session pointer at `_bmad-output/implementation-artifacts/next-session-start-here.md`.
6. **Follow the BMAD sprint governance discipline** — CLAUDE.md §"BMAD sprint governance". Spec → party-mode green-light → dev → bmad-code-review → done.
7. **For dev-stories on Lesson Planner work (Epics 28-32):** read `docs/dev-guide/pydantic-v2-schema-checklist.md` + `dev-agent-anti-patterns.md` + `story-cycle-efficiency.md` before opening.

---

## 8. Operator quick-start (Trial-3 run)

```powershell
# Pre-flight
$env:PYTHONIOENCODING="utf-8"
.\.venv\Scripts\python.exe scripts/heartbeat_check.mjs   # API reachability

# Launch
.\.venv\Scripts\python.exe -m app.marcus.cli trial start `
    --preset production `
    --input course-content/courses/<lesson-slug>/ `
    --operator-id <your-id>

# At each gate: review DecisionCard JSON, file an OperatorVerdict JSON, then
.\.venv\Scripts\python.exe -m app.marcus.cli trial resume `
    --trial-id <uuid> --verdict-file <path-to-verdict.json>
```

Full operator playbook: `_bmad-output/implementation-artifacts/trial-3-readiness-checklist.md`.

---

## 9. References

- **Architectural authority:** `_bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md`
- **Epic backlog:** `_bmad-output/planning-artifacts/epics-langchain-langgraph-migration.md` + `epics.md`
- **Sprint state:** `_bmad-output/implementation-artifacts/sprint-status.yaml`
- **Deferred inventory:** `_bmad-output/planning-artifacts/deferred-inventory.md`
- **Migration guide:** `docs/dev-guide/langgraph-migration-guide.md`
- **Pipeline manifest regime:** `docs/dev-guide/pipeline-manifest-regime.md`
- **Trial methodology:** `docs/trials/methodology.md`
- **Knowledge graph (this analysis):** `.understand-anything/knowledge-graph.json` (1,937 nodes, 3,472 edges, 8 layers, 12-step tour)
- **Interactive dashboard:** run `/understand-anything:understand-dashboard` to launch the Vite-served visualizer (requires the token printed at startup).

---

*Generated 2026-05-25 from `.understand-anything/knowledge-graph.json` at commit `61aaf03`. Code-only scope: `app/` + `scripts/` + `skills/` (685 files). Refresh by running `/understand` after substantive changes.*
