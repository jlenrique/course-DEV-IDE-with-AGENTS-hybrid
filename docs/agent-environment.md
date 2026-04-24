# Agent environment (Cursor + Claude Code)

## Repository layout

| Path | Purpose |
|------|---------|
| `course-content/courses/` | Versioned **source** per course (modules, lessons, slide decks as Markdown/Marp/reveal notes, scripts). |
| `course-content/staging/` | **Human-in-the-loop queue**: agent drafts awaiting your approval before promotion to `courses/` or export. |
| `course-content/_templates/` | Reusable outlines (lesson, module, rubric, slide deck skeleton). |
| `config/content-standards.yaml` | Voice, audience, accessibility defaults for agents. |
| `config/platforms.example.yaml` | Template for Canvas/CourseArc endpoints; copy and adapt locally if needed. |
| `integrations/canvas/` | Scripts, small clients, or notes for Canvas REST usage. |
| `integrations/coursearc/` | LTI/SCORM notes, export checklists, any vendor-specific helpers. |
| `scripts/` | One-off or repeatable deploy/publish commands. |
| `docs/` | Workflow and integration reference (this file, `workflow/`). |
| `_bmad/` + `_bmad-output/` | BMad Method artifacts (PRD, architecture, sprint planning) when you use that track. |
| `.cursor/skills/` | Installed agent skills (BMad, CIS, etc.). |
| `skills/` | Custom project skills (woodshed, mastery skills, production-coordination, pre-flight-check). |
| `resources/exemplars/` | Per-tool exemplar libraries for agent skill development and validation. |

## MCPs (project and user-level)

| MCP | Level | Role for this project | Health Check |
|-----|-------|------------------------|--------------|
| **Gamma** | project | Slide/presentation generation (`generate`, `get_themes`, `get_folders`) | Pre-flight: MCP config + API heartbeat |
| **Canvas LMS** | project | Course/module/assignment management (54 tools) | Pre-flight: MCP config + API heartbeat |
| **Notion** | project | Source wrangling — pull course development notes (22 tools) | Pre-flight: API `/v1/users/me` |
| **Ref** | user | `ref_search_documentation` + `ref_read_url` — primary tool for tech-spec-wrangler doc refresh. Critical for woodshed doc refresh cycles before exemplar reproduction. | Pre-flight: verify callable |
| **Playwright** | user | Browser automation — preview slides, render JS-heavy docs, smoke-test pages | Pre-flight: verify responsive |
| **Perplexity (future)** | user | Deep research, working examples, community patterns — extends tech-spec-wrangler | Deferred until API key configured |

There is no universal "Canvas MCP" in the wild; treat **Canvas as HTTPS + token** via small scripts in `integrations/canvas/` or your existing Python tooling. CourseArc is primarily **LTI 1.3 / SCORM** for delivery into Canvas, not a substitute for Canvas's content APIs.

## Manual-tool specialists (active)

- `skills/bmad-agent-vyond/` — animation storyboard and Vyond Studio build guidance
- `skills/bmad-agent-midjourney/` — bespoke visual prompt packages for Discord/web workflows
- `skills/bmad-agent-articulate/` — Storyline/Rise interaction and SCORM authoring guidance
- `skills/bmad-agent-coursearc/` — CourseArc LTI 1.3 embedding and SCORM deployment guidance

These specialists are guidance-only (manual-tool pattern): no API runtime, no woodshed execution path.

## Shared Skills (available to all agents)

| Skill | Path | Purpose | Status |
|-------|------|---------|--------|
| **Creative Director (CD)** | `skills/bmad-agent-cd/` | Contract-first creative directive generation scaffolding for Wave 2B (`slide_mode_proportions`, experience-profile targets, directive contract refs) | Active |
| **Desmond** | `skills/bmad-agent-desmond/` | Descript finishing: assembly-handoff instructions, doc cache refresh, mandatory **Automation Advisory** (REST vs MCP vs manual); sanctum `_bmad/memory/bmad-agent-desmond/` (local) | Active |
| **Pre-flight check** | `skills/pre-flight-check/` | MCP/API/doc-sources connectivity verification before production runs | Active |
| **Woodshed** | `skills/woodshed/` | Exemplar-driven agent skill development — study, reproduce, compare, reflect, regress (faithful + creative modes) | Active |
| **Production coordination** | `skills/production-coordination/` | Workflow stages, delegation, mode management, style guide | Active |
| **Tech spec wrangler** | `skills/tech-spec-wrangler/` | Tool API doc refresh, research, validation via Ref MCP; ensures agents always have current API knowledge | Active |
| **Texas (Source Wrangler)** | `skills/bmad-agent-texas/` | Source extraction with quality validation, cross-validation against reference assets, fallback chains, proportionality checks. Memory agent (evolvable). Replaces legacy `skills/source-wrangler/`. **Runtime entry point**: `python skills/bmad-agent-texas/scripts/run_wrangler.py --directive <path> --bundle-dir <path>` — orchestrates fetch + extract + validate + cross-validate + emits 6 bundle artifacts per `references/extraction-report-schema.md` (Epic 25 Story 25-1, 2026-04-17). **2026-04-18 (Story 27-0)**: Shape 3-Disciplined retrieval foundation package shipped at `scripts/retrieval/` (contracts / base ABC / dispatcher / hand-rolled MCP client / provider directory / FakeProvider). Operator directory surface: `python skills/bmad-agent-texas/scripts/run_wrangler.py --list-providers [--shape retrieval\|locator] [--status ready\|stub\|ratified\|backlog] [--json]` — canonical answer to "what can Texas fetch?" See `references/retrieval-contract.md` (audience-segmented — Tracy / operators / dev-agents) + `_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md` for schema v1.1. Auth contracts: scite MCP uses `SCITE_USER_NAME` + `SCITE_PASSWORD` (basic auth, default URL `https://api.scite.ai/mcp`); Consensus MCP accepts `CONSENSUS_API_KEY` (bearer) or `CONSENSUS_USER_NAME` + `CONSENSUS_PASSWORD` (basic auth, default URL `https://mcp.consensus.app/mcp`). Unblocks 27-2 scite + 27-2.5 Consensus. | Active |
| **Source wrangler (legacy)** | `skills/source-wrangler/` | Legacy extraction scripts — being migrated to Texas. Retained for backward compatibility during transition. | Deprecated |
| **Sensory bridges** | `skills/sensory-bridges/` | Multimodal perception: PPTX, image, audio (ElevenLabs STT), PDF, video bridges with canonical schema, confidence rubric, and universal perception protocol | Active |
| **Fidelity Assessor (Vera)** | `skills/bmad-agent-fidelity-assessor/` | Forensic fidelity verification at G0-G5. O/I/A taxonomy, Fidelity Trace Reports, circuit breaker. Runs before Quinn-R at every gate. | Active |
| **APP Maturity Audit** | `skills/app-maturity-audit/` | Repeatable four-pillar audit (L1 contracts, L2 evaluation, L3 memory, perception) with heat map, leaky neck, sensory horizon, and drift reports | Active |

## APIs and credentials

- **Canvas**: REST API with access token; store `CANVAS_API_URL` and `CANVAS_ACCESS_TOKEN` in `.env` (see `docs/admin-guide.md`). Use scoped tokens and institution API policies.
- **Gamma**: REST API with X-API-KEY header; store `GAMMA_API_KEY` in `.env`. Pro/Ultra/Teams/Business plan required.
- **ElevenLabs**: REST API with xi-api-key header; store `ELEVENLABS_API_KEY` in `.env`.
- **Qualtrics**: REST API with X-API-TOKEN header; store `QUALTRICS_API_TOKEN` and `QUALTRICS_DATACENTER` in `.env`.
- **CourseArc**: Confirm with your account team whether any **content export or REST** access exists beyond the UI; plan on **LTI embedding in Canvas** and/or **SCORM** for delivery workflows.
- **Descript**: REST API `https://descriptapi.com/v1` — Bearer token; store `DESCRIPT_API_KEY` in `.env` (see `docs/admin-guide.md`). Remote MCP for assistants: `https://api.descript.com/v2/mcp` (OAuth/connector per Descript help). Doc snapshots: `skills/bmad-agent-desmond/references/cache/` via `scripts/refresh_descript_reference.py`.

Secrets stay in `.env` or your password manager; never commit tokens.

## Test execution profiles

- Default local verification excludes tests marked `live_api`:
	- `.venv\Scripts\python -m pytest tests -v`
- Live integration checks require explicit opt-in:
	- `.venv\Scripts\python -m pytest tests -v --run-live`
- Live tests still skip when required credentials are missing.

## BMad alignment

- **Ideation / requirements**: CIS skills (`bmad-product-brief`, `bmad-brainstorming`, design thinking) or full BMM **PRD → UX → Architecture → Epics**.
- **Build content**: `bmad-quick-dev` or story-driven `bmad-dev-story` once you add sprint artifacts under `_bmad-output/`.
- **Review**: `bmad-editorial-review-prose`, `bmad-review-adversarial-general`, CIS **Presentation** agent for slide narratives.
- **Agent creation**: `bmad-agent-builder` with Party Mode coaching for specialist agents; `woodshed` skill for exemplar-driven mastery validation.

Use a **fresh chat** per major skill run, as BMad recommends.
