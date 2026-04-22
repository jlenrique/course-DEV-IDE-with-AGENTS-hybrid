# Admin Guide — System Configuration and Operations

**Audience:** System administrators and the project owner responsible for environment setup, tool connectivity, and operational health.
**Last Updated:** 2026-04-12 | **Project Phase:** Epics 1–14 complete; Wave 1 cluster features (Epics 19–24) complete; prompt-pack family: v4.1 / v4.2 / v4.3

---

## Table of Contents

> 2026-04-12 status: Epics 1–14 complete. Wave 1 cluster features (Epics 19–24) landed (stories 20b-3, 22-1, 21-5). Prompt packs: v4.1 (standard), v4.2 (motion), v4.3 (cluster + interstitial). G1.5 Cluster Plan gate added. New cluster configs: `prompting.yaml`, `dispatch.yaml`, `validation.yaml` in `state/config/`.

1. [Environment Setup](#environment-setup)
2. [API Keys and Credentials](#api-keys-and-credentials)
3. [MCP Server Configuration](#mcp-server-configuration)
4. [Python Environment](#python-environment)
5. [State Management](#state-management)
6. [Pre-Flight Checks and Health Monitoring](#pre-flight-checks-and-health-monitoring)
7. [Content Standards and Style Bible](#content-standards-and-style-bible)
8. [Security Posture](#security-posture)
9. [Backup and Recovery](#backup-and-recovery)
10. [Known Limitations and Workarounds](#known-limitations-and-workarounds)
11. [Operational Procedures](#operational-procedures)

---

## Environment Setup

### Prerequisites

| Requirement | Version | Notes |
|------------|---------|-------|
| **Cursor IDE** | Latest | Primary development and agent interaction environment |
| **Python** | 3.13+ | Virtual environment included in repo |
| **Node.js** | 18+ | Required for MCP servers and smoke-check scripts |
| **Git** | 2.x | Repository management |

### First-Time Setup

```bash
# 1. Clone the repository (primary = course-DEV-IDE-with-AGENTS; hybrid clone = course-DEV-IDE-with-AGENTS-hybrid)
git clone <repo-url>
cd <cloned-folder-name>

# 2. Create `.env` at the project root (gitignored — never committed)
# Add API keys using the tables in "API Keys and Credentials" below

# 3. Activate the Python virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 4. Install Python dependencies
pip install -r requirements.txt

# 5. Initialize state management (SQLite + verify YAML configs)
python -m scripts.state_management.init_state

# 6. Verify tool connectivity
node scripts/heartbeat_check.mjs
```

### Directory Structure (Admin-Relevant)

```
├── .env                    ← YOUR secrets (gitignored, never committed)
├── .mcp.json               ← MCP server definitions (committed, no secrets)
├── .cursor/mcp.json        ← Cursor-specific MCP config (committed, no secrets)
├── .cursor-plugin/
│   └── plugin.json         ← Cursor plugin manifest
├── config/
│   ├── content-standards.yaml   ← Bootstrap defaults (fallback)
│   └── platforms.example.yaml   ← Platform endpoint template
├── state/
│   ├── config/             ← YAML runtime configs (git-versioned)
│   │   ├── course_context.yaml
│   │   ├── style_guide.yaml
│   │   ├── tool_policies.yaml
│   │   ├── prompting.yaml            ← Cluster prompt engineering templates
│   │   ├── dispatch.yaml             ← Cluster dispatch sequencing policy
│   │   ├── validation.yaml           ← Cluster coherence validation rules
│   │   ├── narration-script-parameters.yaml  ← Irene Pass 2 tunable knobs
│   │   └── fidelity-contracts/   ← L1 fidelity contract YAML per gate (G0–G6 + G1.5 + G2.5)
│   └── runtime/            ← Ephemeral runtime (gitignored)
│       ├── coordination.db
│       ├── mode_state.json       ← default vs ad-hoc mode (manage_mode.py)
│       ├── run_baton.*.json      ← per-run baton files (manage_baton.py)
│       └── backup/
├── resources/
│   ├── style-bible/        ← Authoritative brand standards (human-curated)
│   ├── exemplars/          ← Worked production patterns
│   └── tool-inventory/
│       ├── tool-access-matrix.md  ← 17-tool audit
│       └── local-binary-paths.md  ← repo-local executable signposts (for example bundled ffmpeg)
├── hooks/
│   ├── hooks.json          ← Cursor event hooks
│   └── scripts/            ← Hook implementation scripts
├── scripts/
│   ├── api_clients/             ← REST clients (includes NotionClient for source wrangling)
│   ├── run_mcp_from_env.cjs     ← MCP wrapper (loads .env secrets at runtime)
│   ├── heartbeat_check.mjs      ← Baseline API connectivity check
│   ├── smoke_elevenlabs.mjs     ← Targeted ElevenLabs smoke test
│   └── smoke_qualtrics.mjs      ← Targeted Qualtrics smoke test
├── skills/production-coordination/scripts/
│   ├── manage_mode.py           ← CLI: read/set default vs ad-hoc mode → mode_state.json
│   └── manage_baton.py          ← CLI: init/update/close run baton JSON files
├── skills/bmad-agent-marcus/references/
│   └── workflow-templates.yaml  ← Canonical workflow template registry for planner IDs (template 1 is alias-free by policy)
└── _bmad/memory/           ← Agent memory sidecars
```

---

## API Keys and Credentials

All secrets live in `.env` at the project root. **Never commit this file.** Variable names and where to obtain keys are documented in this section (Tier 1–3 tables).

### Tier 1 — API + MCP (full programmatic access)

| Tool | Env Variable(s) | Where to Get Key |
|------|-----------------|------------------|
| **Gamma** | `GAMMA_API_KEY` | Settings → API Keys at developers.gamma.app (Pro+ plan) |
| **ElevenLabs** | `ELEVENLABS_API_KEY` | Profile → API Keys at elevenlabs.io (free tier: 10k credits/mo) |
| **Canvas LMS** | `CANVAS_API_URL`, `CANVAS_ACCESS_TOKEN`, `CANVAS_DOMAIN`, `CANVAS_SUBACCOUNT_ID` | Admin → Developer Keys at your Canvas instance |
| **Qualtrics** | `QUALTRICS_API_TOKEN`, `QUALTRICS_BASE_URL`, `QUALTRICS_DATA_CENTER_ID`, `QUALTRICS_OWNER_ID`, `QUALTRICS_ORGANIZATION_ID` | Account Settings → Qualtrics IDs |
| **Notion** | `NOTION_API_KEY`, `NOTION_ROOT_PAGE_ID` | Create internal integration at notion.so/my-integrations (free on all plans) |
| **GitHub Pages asset hosting** | `GITHUB_PAGES_TOKEN` | Fine-grained PAT scoped to `jlenrique/jlenrique.github.io` with repository **Contents: Read and write** (Metadata read access also recommended) for APP-managed public asset publishing |
| **Canva** | OAuth-based (handled by MCP) | Currently blocked — see Known Limitations |

### Tier 2 — API Only (no MCP)

| Tool | Env Variable(s) | Notes |
|------|-----------------|-------|
| **Botpress** | `BOTPRESS_API_KEY`, `BOTPRESS_BOT_ID` | Personal Access Token |
| **Wondercraft** | `WONDERCRAFT_API_KEY` | Paid plan required |
| **Kling** | `KLING_ACCESS_KEY`, `KLING_SECRET_KEY` | $1 free credits on signup |
| **Panopto** | `PANOPTO_BASE_URL`, `PANOPTO_CLIENT_ID`, `PANOPTO_CLIENT_SECRET` | OAuth2 credentials |

### Tier 3 — Limited API

| Tool | Env Variable(s) | Notes |
|------|-----------------|-------|
| **Descript** | `DESCRIPT_API_KEY` | Early access, import/export only; narrated-slide work uses **repo-local assembly bundles** (manifest + `audio/` + `captions/` + `visuals/` + `DESCRIPT-ASSEMBLY-GUIDE.md` + **`DESMOND-OPERATOR-BRIEF.md`** from prompt **14.5** / `bmad-agent-desmond`). Stills are copied into `visuals/` via compositor **`sync-visuals`** before editors import (see [Developer guide — Compositor assembly bundle CLI](dev-guide.md#compositor-assembly-bundle-cli)). |
| **Midjourney** | `MIDJOURNEY_API_KEY` | Third-party wrapper |
| **CapCut** | `CAPCUT_API_KEY` | Official API status unclear |

### Local Filesystem

| Tool | Env Variable | Notes |
|------|-------------|-------|
| **Box Drive** | `BOX_DRIVE_PATH` | Local sync folder path (e.g. `C:\Users\YourUser\Box`) |

### Notion Setup (Step-by-Step)

1. Go to [notion.so/my-integrations](https://notion.so/my-integrations)
2. Click "New integration" → name it (e.g. "Course Content Production")
3. Copy the Internal Integration Token → paste as `NOTION_API_KEY` in `.env`
4. In Notion, open each page/database you want agents to access → Share → Invite the integration
5. Copy the root page ID from its URL → paste as `NOTION_ROOT_PAGE_ID` in `.env`

Free on all Notion plans including free educator accounts. Rate limit: 3 requests/second.

---

## MCP Server Configuration

### How MCP Works in This Project

MCP (Model Context Protocol) servers give Cursor's AI agents direct tool access. This project uses a **wrapper script** (`scripts/run_mcp_from_env.cjs`) that loads API keys from `.env` at runtime, so config files can be safely committed without secrets.

### Active MCP Servers

Defined in `.mcp.json` (project-level) and `.cursor/mcp.json` (Cursor-specific):

| Server | Package | Status | Tools |
|--------|---------|--------|-------|
| **Gamma** | `@raydeck/gamma-app-mcp` | Active | 2 tools — generate content, browse themes |
| **Canvas LMS** | `canvas-mcp-server` | Active | 54 tools — full course/module/assignment management |
| **Notion** | `@notionhq/notion-mcp-server` | Configured | 22 tools — pages, databases, comments, search |

### The Wrapper Pattern

```json
{
  "mcpServers": {
    "gamma": {
      "command": "node",
      "args": ["scripts/run_mcp_from_env.cjs", "gamma"]
    }
  }
}
```

**Why?** Cursor's MCP `env` field does NOT resolve `${VAR}` from `.env` files. The wrapper script reads `.env`, maps the right variables to each server's expected environment variables, and spawns the MCP process. This keeps secrets out of committed config files.

### Adding a New MCP Server

1. Add the server mapping in `scripts/run_mcp_from_env.cjs`
2. Add the server entry in both `.mcp.json` and `.cursor/mcp.json`
3. Add required env vars to `.env` and document them in this guide if new
4. Restart Cursor to pick up the new MCP server
5. Verify with the pre-flight check

### User-Level MCPs (Already Available)

These are configured at the Cursor user level, not the project level:

| MCP | Purpose |
|-----|---------|
| **Playwright** | Browser automation — 22 tools for navigation, clicks, screenshots |
| **Ref** | Documentation search and URL reading — 2 tools |

---

## Python Environment

### Virtual Environment

```bash
# Activate (Windows)
.venv\Scripts\activate

# Activate (macOS/Linux)
source .venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Run tests
.venv\Scripts\python -m pytest tests/ -v
```

**Python version:** 3.13 (set up during Epic 1). The `.venv` directory is gitignored.

### Key Python Packages

| Package | Purpose |
|---------|---------|
| `requests` | HTTP client for all API integrations |
| `python-dotenv` | Environment variable loading |
| `pyyaml` | YAML config file parsing |
| `pytest` | Test framework |
| `ruff` | Linting |

### API Client Architecture

All API clients in `scripts/api_clients/` extend `BaseAPIClient`, which provides:

- Authenticated sessions (multiple auth patterns: Bearer, X-API-KEY, xi-api-key, X-API-TOKEN)
- Exponential backoff retry (3 attempts, 2s/4s/8s delays)
- Link-header pagination (Canvas-style)
- Structured error handling (`APIError`, `AuthenticationError`, `RateLimitError`)
- Raw response access for binary content (audio files, etc.)

Available clients: `GammaClient`, `ElevenLabsClient`, `CanvasClient`, `QualtricsClient`, `PanoptoClient`, `KlingClient`, `NotionClient`

---

## State Management

Three tiers of state serve different purposes. See [docs/directory-responsibilities.md](directory-responsibilities.md) for the full hierarchy.

### YAML Configuration (git-versioned)

| File | Purpose | Who Writes |
|------|---------|------------|
| `state/config/course_context.yaml` | Course hierarchy, modules, learning objectives | Marcus + user |
| `state/config/style_guide.yaml` | Per-tool parameter preferences (voice IDs, LLM choices, etc.) | Marcus (learned preferences) |
| `state/config/tool_policies.yaml` | Run presets, quality gate thresholds, retry policy | Admin (rarely changes) |
| `state/config/fidelity-contracts/` | Versioned L1 criteria per fidelity gate (G0–G6 + G1.5 + G2.5); referenced by Vera and docs | Maintained with architecture |

**Important:** These files contain tool *dial settings* and *fidelity contracts* — brand identity, colors, typography, and voice/tone live in `resources/style-bible/` (see below).

### SQLite Runtime Database (gitignored)

Located at `state/runtime/coordination.db`. Contains three tables:

| Table | Purpose |
|-------|---------|
| `production_runs` | Workflow progress, run IDs, timestamps |
| `agent_coordination` | Agent assignments, delegation tracking |
| `quality_gates` | Quality check results, approval status |

**Initialize:** `python -m scripts.state_management.init_state`

This database does NOT survive a fresh clone. It's operational state only.

### JSON files in `state/runtime/` (gitignored)

Alongside `coordination.db`, the runtime directory may contain:

| File | Purpose |
|------|---------|
| `mode_state.json` | Current **default** vs **ad-hoc** mode for the repo (read/write via `skills/production-coordination/scripts/manage_mode.py`) |
| `run_baton.{run_id}.json` | **Run baton** — authority contract for an active production run (`manage_baton.py`); specialists consult this for redirect vs standalone consult |

These files are created by tooling and agents; admins normally only inspect them when debugging coordination issues.

### BMad Memory Sidecars (git-versioned)

Located at `_bmad/memory/{agent}-sidecar/`. Each agent has:

| File | Purpose | Write Rules |
|------|---------|-------------|
| `index.md` | Active context, preferences, current mode | Default: full. Ad-hoc: transient section only |
| `access-boundaries.md` | Read/write/deny zones per agent | Set at build time, read-only |
| `patterns.md` | Learned workflow and parameter patterns | Default mode only (append) |
| `chronology.md` | Session and production run history | Default mode only (append) |

**In ad-hoc mode**, only the transient section of `index.md` is writable. All other sidecar files are read-only. This prevents experimental runs from polluting learned patterns.

---

## Pre-Flight Checks and Health Monitoring

### Running Pre-Flight

Three ways to invoke:

```bash
# 1. Through Marcus (conversational)
# In Cursor chat: "Run session readiness" or "Run pre-flight check"

# 2. Runtime readiness (Story G.3)
.venv/Scripts/python -m scripts.utilities.app_session_readiness

# 3. Runtime + tool ecosystem (two-phase)
.venv/Scripts/python -m scripts.utilities.app_session_readiness --with-preflight

# 4. Tool pre-flight only (Python)
.venv/Scripts/python -m skills.pre-flight-check.scripts.preflight_runner

# 5. Baseline heartbeat (Node.js — all tools)
node scripts/heartbeat_check.mjs

# 6. Targeted smoke tests
node scripts/smoke_elevenlabs.mjs
node scripts/smoke_qualtrics.mjs
```

### Runtime Readiness Scope (Story G.3)

`app_session_readiness.py` validates APP runtime prerequisites before long runs:

- `state/runtime/coordination.db` presence and schema sanity (auto-init when missing)
- critical state paths (`state/config`, `state/runtime`) existence and writeability
- `mode_state.json` readability when present
- import sanity for production observability/reporting modules

Use `--with-preflight` to compose runtime checks with the existing tool/API pre-flight sequence.

Exit codes:

- `0`: pass
- `1`: fail
- `2`: warn with `--strict`

### What Pre-Flight Checks

| Check Type | Tools | Method |
|-----------|-------|--------|
| **MCP Config** | Gamma, Canvas LMS, Notion | Verify `.mcp.json` entries present and well-formed |
| **API Heartbeat** | All Tier 1-2 tools | Read-only connectivity probes via `heartbeat_check.mjs` |
| **Targeted Smoke** | ElevenLabs, Qualtrics | Focused API validation scripts |
| **Notion API** | Notion | Python call to `/v1/users/me` to verify integration token |
| **Local FS** | Box Drive | Verify `BOX_DRIVE_PATH` exists and is readable |
| **Config Presence** | Kling, Panopto | Verify API keys are set in `.env` |
| **Static Classification** | Vyond, CourseArc, Articulate | Report as manual-only (no API to test) |
| **Blocker Reporting** | Canva | Report known MCP blockers with workaround guidance |

### Readiness Report Tiers

| Tier | Meaning |
|------|---------|
| **MCP-ready** | MCP configured AND API heartbeat passed |
| **API-ready** | API connectivity verified (MCP not available or deferred) |
| **Manual-only** | No programmatic access — agent provides specs, user executes in tool UI |
| **Blocked/deferred** | Known issue preventing connectivity — resolution guidance provided |

### Hooks (Event-Driven Automation)

Defined in `hooks/hooks.json`:

| Event | Script | Purpose |
|-------|--------|---------|
| `sessionStart` | `hooks/scripts/session-start.mjs` | **Placeholder** — reads hook stdin, returns JSON status; does not run pre-flight yet |
| `sessionEnd` | `hooks/scripts/session-end.mjs` | **Placeholder** — same pattern; run reporting not wired |

Hook-driven placeholders remain intentionally lightweight in the current implementation. Use conversational pre-flight (`skills/pre-flight-check/`) and the APP readiness utilities as the operational path of record.

---

## Content Standards and Style Bible

### Configuration Hierarchy (Priority Order)

| Priority | Location | What It Contains | Who Edits |
|----------|----------|-----------------|-----------|
| **1 (authoritative)** | `resources/style-bible/master-style-bible.md` | Brand identity, colors, typography, voice/tone, accessibility, tool prompts, QA checklists | Human only |
| **2 (operational)** | `state/config/` | Tool parameter preferences, course hierarchy, run presets | Marcus + admin |
| **3 (fallback)** | `config/content-standards.yaml` | Minimal defaults for audience, voice, accessibility | Ships with repo |

**Rule:** When a style bible exists, `config/content-standards.yaml` is superseded. Agents inside Marcus's workflow use the style bible as the authoritative source.

### Updating the Style Bible

Edit `resources/style-bible/master-style-bible.md` directly. Changes take effect immediately on the next production task — Marcus always re-reads it fresh from disk, never caches.

Current style bible covers:
- JCPH Medical Education brand (colors, typography, imagery)
- Voice characteristics (clear, direct, respectful, evidence-based)
- Content structure templates (learning module pattern, assessment guidelines)
- Tool-specific translation guidelines (Gamma prompts, Midjourney prompts, ElevenLabs voice profile)
- Quality assurance checklists

### Exemplar Library

`resources/exemplars/` contains worked patterns from past production decisions:
- `policies/` — Platform allocation decision frameworks
- `platform-matrices/` — Worked allocation examples

These are reference material, not configuration. Agents consult them for decision-making guidance.

---

## Security Posture

### Secrets Management

| Principle | Implementation |
|-----------|---------------|
| API keys never committed | `.env` is gitignored; key names documented in this guide |
| No secrets in MCP config | `run_mcp_from_env.cjs` wrapper loads keys at runtime |
| Keys never logged in plain text | `BaseAPIClient` does not log auth headers |
| Scoped access tokens | Use institution-scoped Canvas tokens per API policy |

### What's Gitignored

- `.env` (secrets)
- `.venv/` (Python virtual environment)
- `state/runtime/` (SQLite database, ephemeral state)
- `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`
- `course-content/courses/.../private/` (large binary assets)

### What's Git-Versioned (Safe to Commit)

- `.mcp.json`, `.cursor/mcp.json` (no secrets — uses wrapper)
- `state/config/*.yaml` (tool preferences, course context — no secrets)
- `_bmad/memory/` (agent learning patterns)
- `resources/` (style bible, exemplars, tool inventory)
- All Python code, skills, agents, tests

---

## Backup and Recovery

### SQLite Database

The coordination database at `state/runtime/coordination.db` is ephemeral — it tracks active production runs and agent coordination. Backup scripts are located at `state/runtime/backup/`.

**Recovery from fresh clone:** Run `python -m scripts.state_management.init_state` to recreate empty tables. Active production run state will be lost, but YAML configs and agent memory sidecars (git-versioned) survive.

### Memory Sidecars

Agent memory sidecars (`_bmad/memory/`) are git-versioned, so they survive clones and branch changes. Periodically review `patterns.md` files — they are append-only and may need condensation if they grow too large.

### YAML Configs

Git-versioned in `state/config/`. If corrupted, restore from git history: `git checkout HEAD -- state/config/`.

---

## Known Limitations and Workarounds

| Tool | Issue | Workaround |
|------|-------|------------|
| **ElevenLabs MCP** | Cursor filters surfaced tools — combined server/tool names exceed 60-char limit | Use REST API via `ElevenLabsClient` Python client |
| **Qualtrics MCP** | Not on npm — requires local build from GitHub source | Use REST API via `QualtricsClient` Python client |
| **Canva MCP** | OAuth redirect URL rejected by Cursor | Use Canva Connect API directly (when client is built) |
| **Fetch MCP** | No usable tools surfaced in Cursor | Use Ref MCP for doc reading, or Python `requests` |
| **Panopto** | Client code exists but no credentials configured (3 tests skipped) | Add credentials to `.env` when Panopto access is available |
| **ElevenLabs `/user`** | Returns 401 | Non-blocking — voice listing and TTS work fine |
| **PowerShell** | Doesn't support `&&` chaining | Use `;` instead, or use bash |

---

## Operational Procedures

### Trial run: narrated deck happy path (operator checklist)

Workflow-family additions:
- Use `docs/workflow/production-prompt-pack-v4.1-narrated-deck-video-export.md` for non-motion narrated runs.
- Use `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md` when `MOTION_ENABLED: true`.
- If `DOUBLE_DISPATCH: true`, require `variant-selection.json` and `authorized-storyboard.json` before Irene Pass 2.
- If `MOTION_ENABLED: true`, require Gate 2M, `motion-designations.json`, `motion_plan.yaml`, and Motion Gate closure before Irene Pass 2.

Before the instructional lead follows the **Happy-path walkthrough** in [`docs/user-guide.md`](user-guide.md) (section *Happy-path walkthrough: user + Marcus + “X-ray”*) with their own content, confirm:

1. **`.env`** — `GAMMA_API_KEY`, `ELEVENLABS_API_KEY`, and Kling keys as needed; no secrets committed.
2. **Pre-flight** — `node scripts/heartbeat_check.mjs` (or Marcus-driven pre-flight) green for the tools in scope.
3. **Mode** — `skills/production-coordination/scripts/manage_mode.py` reflects **default** vs **ad-hoc**; ad-hoc routes under `course-content/staging/ad-hoc/` per `docs/ad-hoc-contract.md`.
4. **Prompt pack family** — standard narrated runs use `docs/workflow/production-prompt-pack-v4.1-narrated-deck-video-export.md`; motion-enabled narrated runs use `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`.
5. **Double-dispatch** — if enabled, plan for `variant-selection.json` plus winner-only `authorized-storyboard.json` before downstream narration or motion work.
6. **Motion workflow** — if `MOTION_ENABLED` is true, require explicit motion budget inputs, Gate 2M coverage, `motion_plan.yaml`, and Motion Gate closure before Irene Pass 2.
7. **Canonical motion helpers** — for motion-enabled runs, prefer:
   - `py -3.13 skills/bmad-agent-marcus/scripts/build-pass2-inspection-pack.py --bundle <bundle-dir>`
   - `py -3.13 skills/bmad-agent-marcus/scripts/prepare-irene-pass2-handoff.py --bundle <bundle-dir>`
8. **Bundled ffmpeg discoverability** — if media tooling cannot find `ffmpeg` on `PATH`, check `resources/tool-inventory/local-binary-paths.md` and the resolver in `scripts/utilities/ffmpeg.py` before installing or patching around it.
9. **Literal-visual policy** — literal-visual slides are full-slide image-only. Dispatch payload content for literal-visual slides must be URL-only image references; supporting prose belongs in Irene Pass 2 narration/script.
10. **HTTPS assets** — Any `diagram_cards` images must be **publicly fetchable HTTPS URLs** (Gamma API); local-only files are not sufficient without hosting.
11. **Compositor** — Developers run `compositor_operations.py` (`sync-visuals`, `guide`) from the project `.venv` if Marcus does not invoke it; see [Developer guide — Compositor assembly bundle CLI](dev-guide.md#compositor-assembly-bundle-cli).

### Adding a New Tool Integration

1. **Research** — Classify the tool (Tier 1-4) using `resources/tool-inventory/tool-access-matrix.md` as the template
2. **API client** — If Tier 1-3: create a client in `scripts/api_clients/` extending `BaseAPIClient`
3. **Environment** — Add env vars to `.env` and update this guide if needed
4. **MCP** (if available) — Add server mapping to `run_mcp_from_env.cjs` and entries in `.mcp.json` / `.cursor/mcp.json`
5. **Pre-flight** — Update pre-flight check to include the new tool
6. **Tool matrix** — Update `resources/tool-inventory/tool-access-matrix.md`
7. **Tests** — Add integration test in `tests/`
8. **Style guide** — Add tool parameter section in `state/config/style_guide.yaml`

### Rotating API Keys

1. Generate new key in the tool's dashboard
2. Update `.env` with the new key
3. Restart Cursor (MCP servers read env on startup)
4. Run pre-flight check to verify connectivity

### Monitoring Agent Memory Growth

Memory sidecars (`_bmad/memory/*/patterns.md`) are append-only in default mode. Periodically:

1. Review `patterns.md` for each agent
2. Condense redundant or outdated patterns
3. Commit the condensed version

This prevents memory bloat and keeps agent context loading fast.

### Updating Run Presets

Edit `state/config/tool_policies.yaml`. Current presets:

| Preset | Quality Threshold | Human Review | Accessibility | Brand Check |
|--------|:-----------------:|:------------:|:------------:|:-----------:|
| explore | 0.6 | No | No | No |
| draft | 0.7 | Yes | Yes | No |
| production | 0.9 | Yes | Yes | Yes |
| regulated | 0.95 | Yes | Yes | Yes + audit trail |

Default preset: `draft`. Change the `default_preset` field to switch.

### Run mode and run baton (CLI)

For automation or debugging without opening Cursor chat:

- **Mode:** `python skills/production-coordination/scripts/manage_mode.py get` / `set default` / `set ad-hoc` — persists to `state/runtime/mode_state.json`.
- **Baton:** `python skills/production-coordination/scripts/manage_baton.py --help` — initialize, read, update gate, close baton files (`run_baton.{run_id}.json`).

Tests for these scripts live under `skills/production-coordination/scripts/tests/`.

Operational guardrail:
- Run `skills/bmad-agent-marcus/scripts/validate-gary-dispatch-ready.py` before Gate 2 approval; treat literal-visual non-URL prose findings as hard-stop contract violations.
