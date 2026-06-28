# ONBOARDING — `course-dev-ide-with-agents`

> **One-line elevator:** Collaborative intelligence infrastructure for course-content production — a deterministic, manifest-compiled orchestrator (operator surface: **Marcus-SPOC**) drives a roster of ~20 LangGraph specialist agents through gated, human-in-the-loop production of narrated lessons (with video/animation), with tamper-evident operator verdicts, a learning ledger, and frozen-graph reproducibility.

**Languages:** Python (3.11+), Markdown, YAML, JSON, Jinja2, JavaScript, PowerShell, Shell, SQL
**Core frameworks:** LangChain, LangGraph, Pydantic v2 (plus FastAPI/Uvicorn, httpx, Pytest in the runtime/tooling layers)
**Branch (at analysis):** `dev/p5-downstream-consumption-2026-06-26` (severed from `upstream/master` since 2026-04-24)
**Graph baseline:** commit `85f27787` · 1820 nodes / 3274 edges / 8 layers · 781 files analyzed (`app/`, `scripts/`, `skills/`)

**Status (2026-06-28):** Migration SHIPPED (`97842ac`, 2026-04-27); Slab 7 orchestrational arc CLOSED. **Braid arc COMPLETE** (Marcus-SPOC conversational REPL with a deterministic guard; live Scite→Texas research-citation leg; Markdown→DOCX learner workbook). **Pre-planning / G0-enrichment cycle COMPLETE** and the **P5 downstream-consumption loop is CLOSED + live-proven**: the workbook, deck (Gary), and narration (Enrique) now consume the enriched corpus. **Directed-voice arc COMPLETE (this session):** a per-segment `voice_direction.v1` contract flows CD/Irene emission → Storyboard B (pre-spend review) → Enrique directed ElevenLabs TTS with per-segment receipts → deterministic acoustic verification → a live Descript publish; plus the **UDAC** (Universal Downstream Asset Contract) Run-Asset-Index providing fail-loud ACCESS + anti-tautology USE guarantees. **Next increment (ruled):** harden the directed voice so its per-role read is audible and fires on real clustered decks (content-grounded role→slide linkage + widened pace/stability gesture + `seed` graduation).

---

## Architecture Layers

The codebase is organized into 8 architectural layers (knowledge-graph-derived). Work flows top-to-bottom: an operator talks to **Marcus**, who compiles a manifest and routes typed state through **specialists** and **gates**, persisted by the **runtime**.

### 1. Marcus Orchestration (`app/marcus/`, 102 files)
The orchestrator, lesson-plan compilation, and the operator CLI that route work across specialists and gates.
- **Operator surface:** `cli/marcus_spoc.py` (scripted single-point-of-contact narrating each gate), `cli/marcus_interlocutor.py` (arc-finale **LLM stop-and-chat REPL** — the model proposes, a deterministic guard validates against gate-legal actions so the chatting model never drives the engine), `cli/front_door.py` (first turn presenting the bundle catalog), `cli/trial.py` (start/resume/recover trial runs), `facade.py` (the single Maya-facing facade).
- **The engine:** `orchestrator/production_runner.py` (~3,200 lines — the core LangGraph engine with **two node walks**: a START walk that stops at G1, and a CONTINUATION/recover walk handling all later gates; gate side-effects must be wired into BOTH).
- **Lesson-plan substrate:** `lesson_plan/g0_enrichment.py` (frozen, operator-confirmable source-manifest models), `lesson_plan/learning_objective.py` (provenance-anchored LO entity), `lesson_plan/irene_refinement.py` (signed LO-delta contract), `lesson_plan/pedagogy_annotation.py` (additive P3 pedagogy overlay), `lesson_plan/run_asset_index.py` (**UDAC** v1 — ACCESS+USE contract with a SHA256 digest chain), `lesson_plan/bundle_catalog.py`, `lesson_plan/workbook_enrichment.py`.
- **Consumption wiring:** `orchestrator/enrichment_consumption.py` (derives per-slide voice direction + deck enrichment hints from the G0 corpus), `orchestrator/udac_wiring.py`, `orchestrator/package_builders.py`, `orchestrator/g0_enrichment_wiring.py`, `orchestrator/conversation_persistence.py` (tamper-evident SHA256-chained turns).

### 2. Specialist Agents & Composers (`app/specialists/`, 182 files)
LangGraph specialist agents plus Marcus-authored directive composers that produce the artifacts.
- **Shared scaffold:** `_scaffold/graph.py` + `_scaffold/contract.py` — the **9-node lifecycle** (`receive → plan → act → verify → reflect → emit_spans → gate_decision → finalize → handoff`) every specialist is built from.
- **Shared helpers:** `_shared/voice_direction_map.py` (the pure-leaf 5-tier voice-direction → TTS-settings mapper), `_shared/figure_tokens.py` (single-source figure-citation tokenizer), `_shared/source_fidelity_audit.py`, `narration_join.py`, `dispatch_errors.py`.
- **Representative specialists:** **Irene** (`irene/graph.py` narration authoring + `irene/authoring/` pass-2 template & voice-direction annotation; `irene_pass1/` pedagogy), **Gary** (`gary/graph.py` + `gary/gamma_dispatch.py` deck via Gamma), **Enrique** (`enrique/graph.py` + `enrique/_act.py` + `enrique/elevenlabs_dispatch.py` directed-voice TTS), **Kira** (`kira/kling_dispatch.py` video), **motion_planner** (07D.5 deterministic motion), plus CD, Vision, Texas, Tracy, Desmond, Quinn-R, compositor, and more.

### 3. Domain Models (`app/models/`, 167 files)
Pydantic v2 domain/state models — the typed contracts every node passes through. `state/run_state.py` (the central RunState, highest fan-in), `state/component_selection.py`, the `decision_cards/` family, `operator_verdict*` sections, `perception/perception_artifact.py`, runtime envelopes.

### 4. Gates & Workflow Substrate (`app/gates/`, `app/manifest/`, `app/cora/`, `app/parity/`, `app/audit/`, 71 files)
Gate decision substrate (`gates/verdict.py`, `gates/resume_api.py`, per-section poll surfaces), the **manifest compiler** (`manifest/compiler.py` + `manifest/schema.py` — frozen-graph reproducibility), Cora block-mode dev-graph guards (`cora/graph.py`), transport-parity/lockstep contracts, and audit-chain integrity.

### 5. Runtime & Transport (`app/runtime/`, `app/http/`, `app/mcp_server/`, `app/ledger/`, `app/replay/`, 44 files)
Postgres checkpointer/retention/retry, the append-only **learning ledger** (`ledger/schema.sql`), trace-based economics (`runtime/economics.py`), the replay-regression harness (`replay/regression.py`, `replay/parity_comparison.py`), and the FastAPI/MCP transport bridges.

### 6. Operator & Developer Tooling (`scripts/`, 123 files)
Standalone scripts not part of the orchestrated graph: API clients (`api_clients/base_client.py` + concrete ElevenLabs/Gamma/Kling/Descript/Canvas/Notion/… clients), content generators, analysis/acoustics diagnostics (`analysis/directed_voice_acoustics.py`, `diagnostics/elevenlabs_api_sweep.py`), operator utilities, and governance validators.

### 7. BMAD Agent Skills (`skills/`, 88 files)
Operator-facing BMAD agent skill packages (`SKILL.md`, references, helper scripts) defining custom personas — Marcus, Texas, CD, Audra, the content/media specialists. Activation order for custom agents lives in each `skills/bmad-agent-<name>/SKILL.md` (+ sanctum under `_bmad/memory/`).

### 8. Project Root & Configuration (4 files)
Top-level config/metadata: `.env.example`, `.gitattributes`, `.understand-anything/.understandignore`.

---

## Key Concepts

- **Marcus-SPOC + deterministic guard.** Marcus is the single operator contact. The conversational REPL lets an LLM propose actions, but a deterministic guard validates every action against gate-legal options — the chatting model never drives the engine directly.
- **The two-walk production runner.** `production_runner.py` runs a START walk (stops at G1) and a CONTINUATION/recover walk (all later gates). Any gate side-effect (e.g. storyboard/chooser publish) must be added to BOTH walks or it silently never fires for G2B+.
- **The 9-node specialist scaffold.** Every specialist shares one LangGraph lifecycle (`receive→plan→act→verify→reflect→emit_spans→gate_decision→finalize→handoff`); the load-bearing logic lives in each specialist's `_act.py`/`*_dispatch.py`.
- **Gates + HIL DecisionCards.** Production pauses at gates (G1/G2C/G3/G4…) for human-in-the-loop verdicts; `resume_api.py` rehydrates and continues. Operator verdicts are tamper-evident.
- **Manifest compilation + frozen-graph reproducibility.** `manifest/compiler.py` compiles a deterministic pipeline manifest; the frozen graph + learning ledger make runs reproducible and auditable.
- **G0-enrichment → P5 consumption loop (CLOSED).** The pre-planning pipeline produces a frozen, typed `g0-enrichment.json` (source components, resolved citations, pedagogy annotations, refined LOs). Downstream consumers — workbook, Gary deck, Enrique narration — now READ that corpus, so deliverables are shaped by enrichment (anti-tautology tests prove changing the corpus changes the output).
- **Directed voice (`voice-direction.v1`).** A per-segment voice-direction contract (render_strategy, delivery_intent, emotional_tone, pace, energy, pauses, per-field ElevenLabs overrides) flows from CD/Irene emission → Storyboard B (pre-spend review) → Enrique via the shared 5-tier mapper → directed TTS with per-segment receipts (real request-ids), verified by a deterministic acoustic judge. **Grounding firewall:** direction strings never reach the figure-citation gate.
- **UDAC (Universal Downstream Asset Contract).** The Run Asset Index (`run_asset_index.py` + `udac_wiring.py`) gives downstream specialists an ACCESS guarantee (locate ratified assets) + USE guarantee (anti-tautology: changing assets changes outputs), failing loud on stale/missing ratified assets; written as a gate side-effect on both walks.
- **BMAD methodology.** Sprint governance, party-mode multi-agent green-lights, and `bmad-code-review` gate substrate changes (see `CLAUDE.md`).

---

## Guided Tour

A knowledge-graph-derived path through the system (11 steps):

1. **The Operator Surface: Marcus** — `skills/bmad-agent-marcus/SKILL.md`, `app/marcus/cli/__main__.py`, `app/marcus/cli/marcus_spoc.py`
2. **Core Domain Models & State** — `app/models/state/run_state.py`, `app/models/decision_cards/base.py`
3. **The Orchestration Engine** — `app/marcus/orchestrator/production_runner.py`, `orchestrator/supervisor.py` (the two-walk model)
4. **Manifest Compiler & Frozen Graph** — `app/manifest/compiler.py`
5. **The 9-Node Specialist Scaffold** — `app/specialists/_scaffold/graph.py`, `_scaffold/contract.py`
6. **Irene: Pedagogy & Narration Authoring** — `app/specialists/irene_pass1/graph.py`, `app/specialists/irene/graph.py`
7. **Gary: Slide Deck Generation** — `app/specialists/gary/graph.py`, `gary/gamma_dispatch.py`
8. **Enrique: Directed-Voice Narration (TTS)** — `app/specialists/enrique/graph.py`, `enrique/elevenlabs_dispatch.py`
9. **G0-Enrichment & Lesson-Plan Substrate** — `app/marcus/lesson_plan/g0_enrichment.py`, `lesson_plan/schema.py`, `orchestrator/enrichment_consumption.py`
10. **Gates & Human-in-the-Loop Verdicts** — `app/gates/verdict.py`, `app/gates/resume_api.py`
11. **API Clients, Ledger & Configuration** — `scripts/api_clients/base_client.py`, `app/ledger/schema.sql`, `.env.example`

---

## Complexity Hotspots (approach carefully)

The highest-complexity files — read these slowly, they carry the most load-bearing logic:

- `app/marcus/orchestrator/production_runner.py` — the ~3,200-line two-walk orchestration engine (run/resume/recover).
- `app/specialists/irene/graph.py` (~1,400 lines) & `app/specialists/gary/_act.py` (~900 lines) — the heaviest specialist logic.
- `app/marcus/orchestrator/g0_enrichment_wiring.py` (~1,170 lines) — G0 source-enrichment with offline/live LLM pre-passes.
- `app/marcus/cli/marcus_interlocutor.py` / `marcus_spoc.py` / `front_door.py` — the conversational SPOC surface + deterministic guard.
- `app/marcus/lesson_plan/run_asset_index.py` — UDAC v1 (digest chain, fail-loud resolution).
- `app/marcus/orchestrator/enrichment_consumption.py` — per-slide voice-direction + deck-enrichment projection (carries the EDGE-1 role-seed divergence guard).
- `app/marcus/lesson_plan/g0_enrichment.py` / `learning_objective.py` / `irene_refinement.py` / `pedagogy_annotation.py` — the frozen enrichment + LO contract family.
- `app/runtime/economics.py` — LangSmith trace-based trial cost measurement.
- `scripts/api_clients/*` — the live external-API clients (ElevenLabs/Gamma/Kling/Descript) where real spend happens.

> Gotchas worth internalizing early: the **two-walk** runner (side-effects on both walks); gpt-5 rejects `temperature=0` (bind at construction); the **grounding firewall** (narration figures ⊆ rendered-slide figures; voice-direction strings never reach the citation gate); the **EDGE-1** role-seed ordinal-join fragility on clustered decks; and `.venv/Scripts/python.exe` for all Python.

---

*Generated from the Understand-Anything knowledge graph at `.understand-anything/knowledge-graph.json` (commit `85f27787`). Regenerate with `/understand` then `/understand-anything:understand-onboard` after substantive substrate changes.*
