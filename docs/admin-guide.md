# Admin Guide — System Configuration and Operations

## Current Status - Marcus-SPOC Workbook Production (2026-07-15)

Operate this repository as the Marcus-SPOC local runtime. Marcus is the single operator-facing orchestrator for real APP production runs; proofing sessions are useful diagnostics, not a deployment target. This block covers the 2026-07-09 Phase-2 lesson-planning baseline, the Batch LLM Execution Mode v1 close (2026-07-10), the Agentic Research Foundations promote (R0–R7, 2026-07-10), the Workbook Research Products close (W0–W4, 2026-07-10), the Operator HUD arc (Epic 35, 2026-07-11/12 — HUD authorized for real operator use), and the Presentation-Support Workbook arc (Epics 36–40, 2026-07-12 → 07-15 — **live gate PASSED**).

### Current Operating Branch And Evidence

- Active branch: `codex/workbook-enhanced-epics-36-40` (successor to `dev/hud-revival-2026-07-11` → `dev/agentic-research-foundations-2026-07-10` → `dev/batch-mode-2026-07-10` → `dev/lesson-planning-2026-07-09`). On this branch: the Presentation-Support Workbook pipeline (Epics 36–40) ran **end-to-end for the first time on 2026-07-15** — governed trial `a940c5eb` reached `status: completed` / `success: true` and emitted a runner-verified workbook (`runs/a940c5eb…/exports/workbooks/u01@1.{md,docx}`). Epic 36 done; Stories 38.1 + 38.3a live-gate-passed with closure pending the LO-overlay bridge fix (the completed workbook rendered its Learning Objectives section as placeholders — known #1 defect) + party green-light + code review. Four negative first-run-stands witnesses preserved immutable. Master merge deferred until the acceptance arc closes.
- Standing from predecessor branches: Operator HUD Epic 35 (all 10 stories closed; unanimous party re-verdict "performed to spec"; HUD authorized for real operator use — see `docs/operator/hud-guide.md`), Agentic Research Foundations R0–R7 (`MARCUS_RESEARCH_DETECTIVE_LIVE` default OFF), Workbook Research Products W0–W4, TRAIL trio, and Batch LLM Execution Mode v1 (opt-in vision batch transport; default realtime).
- Durable baseline: live bespoke Irene Pass-1 Claim B is closed through `fa48fb5b`; preceding durable closes include the Phase-2 bridge (`20246475`), Irene planning-context handoff (`b69aa2de`), and plan-ratify surface (`318b6b0f`).
- Evidence and run artifacts are banked under `_bmad-output/implementation-artifacts/evidence/` and `runs/<uuid>/`. Treat active product-gap evidence as provisional until it is committed and pushed.

### Operational Readiness

- `.env` must contain the keys needed for the claimed path. Live Irene/OpenAI proof requires OpenAI access; Gamma or published-deck access is required only when explicitly claimed.
- Use the repo virtual environment and local scripts for validation. Do not stage ambient run/evidence strays as durable evidence without a matching story, verdict, and close note.
- For current status, consult [`docs/STATE-OF-THE-APP.md`](STATE-OF-THE-APP.md), [`SESSION-HANDOFF.md`](../SESSION-HANDOFF.md), and [`next-session-start-here.md`](../next-session-start-here.md).

### Marcus-SPOC Lesson-Planning Pre-Start

1. Prepare a curated lesson leaf or course-source input bundle. Real HAI/PHS ingestion remains story/operator gated.
2. Run the durable `plan-ratify` path, or the branch-visible `plan-dialogue` path only when that product-gap work is accepted on the branch.
3. Confirm run-dir artifacts before starting production: `planning-ratification.json`, `ratified-collateral-intent.yaml`, optional `ratified-los.json`, and optional `marcus-planning-dialogue.md`.
4. Start the trial through `python -m app.marcus.cli trial start`, using `--lesson-plan-collateral-intent` for the durable ratified path. Use `--lesson-plan-json` only after the automatic lesson-plan-collateral product-gap close is durable.
5. Treat `--allow-offline-cost-report` and `scripts/utilities/bank_mine*.py` as harness/evidence utilities, not normal production proof.

Operational state to watch:

- `runs/<uuid>/`: planning companions, transcripts, Irene lesson-plan artifacts, trial receipts.
- `_bmad-output/implementation-artifacts/evidence/`: proof packs and verdict JSON for claimed slices.
- `state/config/sme-registry.yaml`: branch-visible SME voice/styleguide/attribution/approval routing; unknown or unbound SMEs must fail or surface an explicit gap rather than silently borrowing Tejal.

### Batch Execution Mode — Operational Checklist

Batch LLM execution is opt-in; the default execution mode is realtime. Scope is vision/07G perception only — all other nodes stay realtime even with the flag on, and the workbook is not batch-eligible. The eligibility authority is `app/runtime/llm_batch_eligibility.py` (A3 matrix); consult it and the dev guide's batch seams section rather than re-deriving eligibility here.

1. Invoke with `python -m app.marcus.cli trial start ... --llm-execution-mode batch`. The flag lives on `trial start` and defaults to `realtime`; batch is operator-invoked per trial.
2. Expect the run to pause with envelope status `waiting_for_provider_batch` when an eligible perception node submits to the provider's batch service. This is a documented pause state — not a hang and not a failure. No provider turnaround time is promised.
3. Resume with `python -m app.marcus.cli trial resume-batch --trial-id <uuid>`. Resume discipline: resume-batch never re-uploads; it acts only on runs whose envelope status is `waiting_for_provider_batch`; if the provider job is still non-terminal, the run simply remains `waiting_for_provider_batch` — safe to re-run as idempotent polling.
4. After the vision join (and after resume-batch completes), check `runs/<uuid>/llm_batch/cost-report.json`. It is an accounting/estimate artifact — not the provider invoice; live invoice accuracy is not claimed. Prompt-cache-hit variance also moves run-to-run cost deltas, so do not misread deltas as pricing or model drift.
5. Model expectation: batch submits the realtime product model `gpt-5.5`; if the provider Batch API rejects that model, the route falls back to the nearest GPT-5-family model.
6. Keys: hermetic batch tests require no API keys; any live batch leg requires live OpenAI access in `.env` per the Operational Readiness rules above.

Non-claims (hold these lines when reporting status):

- Batch is NOT the production default and is not a "recommended for production" path; realtime remains the default.
- The batch done-bar is hermetic-only as of the 2026-07-10 epic close: hermetic test green does not prove live quality, and live provider batch turnaround plus resume-batch behavior under provider-job failure/expiry are not yet characterized live.
- No batch-turnaround SLA numbers exist, and no cost-savings outcome is asserted or measured; any discount is the provider's advertised batch pricing, not a proven outcome.
- The workbook is not batch-eligible.

### Research Foundations — Operational Checklist

The research leg (node 04.55 Irene→Tracy→Texas bridge) runs inside a normal trial; the operational surface is the detective flag and the retrieval-provider credentials.

1. `MARCUS_RESEARCH_DETECTIVE_LIVE` is **default OFF** and stays OFF unless you set it per run. Flag-OFF runs are bit-identical to pre-research-foundations behavior. Default-ON is a party policy decision that has not been taken — do not flip it as routine ops.
2. With the flag ON, expect a hard pause before Irene Pass-2 (node 08): the run blocks until an operator disposition receipt (approve | reject | defer per finding) lands via the research-detective gate. Approval unlocks the walk. Resume/recover atomicity across this pause is NOT yet claimed (TRAIL) — prefer disposing in-session rather than parking a paused run.
3. Provider credentials:
   - **Scite** — OAuth (not Basic); headed Playwright login via `scripts/operator/scite_oauth_login_auto.py`, refresh token reused headlessly afterward.
   - **Consensus** — MCP OAuth smoke evidence at `evidence/consensus-mcp-oauth-smoke-20260710/`.
   - **OpenAlex** — public API, no key required; DOI metadata + OA link discovery only.
   - **Jefferson library** — live retrieval fenced on `chrome_running_quit_required`: it needs an available Chrome SSO session (probe scripts `scripts/utilities/run_jefferson_*_probe*.py`). Hermetic path works without it.
   - Provider roster authority: `run_wrangler.py --list-providers`.
4. Workbook research sections operate themselves: glossary and trends appear only when the research packet has rows (empty-honesty). If a workbook lacks the sections, first check whether the run's research packet was empty before suspecting a defect.
5. Live evidence drivers (`scripts/utilities/run_research_r{1–7}_live_evidence.py`, `run_workbook_w{1–4}_live_evidence.py`, `run_openalex_live_evidence.py`) write timestamped packs under `_bmad-output/implementation-artifacts/evidence/` — first-run-stands; do not retry-to-green.

Non-claims (hold these lines when reporting status):

- The detective gate, Consensus, and Jefferson are NOT default-ON.
- The Research Glossary is not human SME-reviewed (visible capability note by design); the semantic tripwire is WARN-only and does not gate production or catch all weak claims.
- OpenAlex does not download PDF bytes, perform institutional SSO, or score credibility (`authority_tier` is deliberately `None`).
- Jefferson live retrieval beyond the fenced probe evidence is not claimed.

### Workbook Live Authoring — Operational Checklist

The governed workbook live run (Epics 36–40) is driven by the delegated HIL harness `scripts/utilities/marcus_spoc_live_test_runner.py` (it does not bypass HIL; it exercises the production G0 confirm + resume seam under the versioned `tests/fixtures/marcus_spoc/workbook_live_hil_policy.json` policy, `approved_by: Juanl`). **Status 2026-07-15: the pipeline has completed end-to-end once** (trial `a940c5eb`); the runner's verdict is honest — it asserts a real conformant MD+DOCX workbook exists before granting `success: true`, so a run that "completes" without its deliverable reports FAILURE, not false-green. **Known open defect:** the completed workbook's Learning Objectives section rendered 6/6 placeholders (LO-overlay bridge, `_unit_to_enrichment_lo_map`) — a completed run is not yet a shippable deliverable until that fix lands.

1. `MARCUS_G0_DISPATCH_LIVE` is **default OFF**. **OFF authors deterministic boilerplate learning objectives** (`"Understand the material introduced by src-NNN…"`) — do NOT judge LO/workbook quality from an OFF run. **Set `MARCUS_G0_DISPATCH_LIVE=1` for any real workbook run** so G0 (and Irene refinement) author real, source-grounded LOs via live gpt-5. Requires a live OpenAI key in `.env` (`_has_live_openai()` AND-gates the toggle).
2. Live LO authoring is **non-deterministic** — the same prompt can author a full LO set on one run and (rarely) return zero. The G0 pre-pass now guards this: on zero LOs from a non-empty corpus it **retries the live call once, then fails loud AT G0** (`G0EnrichmentParseError`) rather than cascading to an opaque 07W.1 error. A fail-loud at G0 means the model refused to author LOs — re-run (a fresh trial), do not force.
3. Standard governed invocation (fresh immutable trial id every run; never reuse a failed witness): `start --trial-id <fresh-uuid> --policy tests/fixtures/marcus_spoc/workbook_live_hil_policy.json --runs-root runs --evidence-root _bmad-output/implementation-artifacts/evidence/workbook-live-hil --input <corpus-dir> --course-source-root <corpus-dir> --encounter-mode recorded`, with `MARCUS_G0_DISPATCH_LIVE=1` exported. Deck+workbook ON / motion+HUD OFF is runner-enforced.
4. **First-run-stands, no retry-to-green.** If a run pauses at error, freeze and diagnose; do not re-fire hoping for a better roll. Ratified LOs are digest-bound (`ratified-los.json`) — you cannot hand-patch them; regeneration happens inside a fresh run and is re-ratified at G0R.

### Do Not Operate As If

- Do not treat the legacy Trial-3 or prompt-pack migration banners below as the current operating plan.
- Do not ingest real HAI/PHS content remotely or into production paths without explicit story/operator authorization.
- Do not ad-hoc-edit approved styleguide registry guides; route SME/styleguide changes through the registry and approval contracts.

## Legacy Context

> **Migration Status (refreshed 2026-05-07 at pre-Trial-3 cleanup S5 Tier-2):** Migration unconditionally SHIPPED 2026-04-27. Slab 7 orchestrational arc COMPLETE (7a+7b+7c closed 2026-05-01 / 2026-05-01 / 2026-05-07). Pre-Trial-3 cleanup arc S1-S6 currently in progress (S1+S2+S3+S4 closed; S5+S6 in flight). **First tracked trial (Trial-3) launches post-cleanup-close** against v5 canonical pack + post-Slab-7c substrate. v5 canonical pack: `docs/workflow/production-prompt-pack-v5-narrated-lesson-with-video-or-animation.md`. Trial methodology: `docs/trials/methodology.md`. Legacy v4.2 retained as mapping-checklist legacy-axis frozen authority.


> ## MIGRATION STATUS BANNER (refreshed 2026-04-28)
>
> **This guide reflects the PRE-MIGRATION primary-repo workflow** (Cursor IDE + prompt-pack v4.x + per-Epic-1-24 architectural model). The hybrid clone on `dev/langchain-langgraph-foundation` has **MIGRATED**: migration unconditionally SHIPPED 2026-04-27 (commit `97842ac`); Slab 6 trial-experience bundle 3/3 CLOSED 2026-04-28; first tracked trial UNBLOCKED.
>
> **For migration-native admin operations (post-SHIP), see:**
> - **[`docs/operator/production-trial-playbook.md`](operator/production-trial-playbook.md)** — start-to-stop production-run playbook including environment confirmation + pre-flight + health-check sections at action-by-action granularity (in-progress fill during first tracked trial).
> - **[`docs/operator/validation-scripts.md`](operator/validation-scripts.md)** — operator-run validation script catalog (5 validation + 4 ceremony scripts; check_keys + dual-gate re-runs + bundle health + full health check + M2/M3 ceremonies).
> - **[`docs/operator/trial-run-runbook.md`](operator/trial-run-runbook.md)** — first-trial setup + transport choice + verdict workflow.
> - **[`README.md`](../README.md)** — top-of-repo project orientation + status + quick-start.
> - **[`.env.example`](../.env.example)** — REQUIRED/RECOMMENDED/OPTIONAL env-var categorization.
> - **[`scripts/utilities/trial_run_preflight.py`](../scripts/utilities/trial_run_preflight.py)** — 12-point readiness sweep.
> - **[`scripts/setup/first_clone_bootstrap.{ps1,sh}`](../scripts/setup/)** — one-command operator setup.
> - **[`docs/dev-guide/local-postgres-setup.md`](dev-guide/local-postgres-setup.md)** — native Postgres setup (NOT Dockerized per operator preference).
> - **[Migration Admin Appendix](#migration-admin-appendix)** below — migration-specific admin ops added post-Slab-3 close.
>
> **Scope of this legacy content (post-SHIP):** environment setup + API-key management + MCP server config + Python env + content directory layout sections described below are HISTORICAL REFERENCE for the pre-migration primary-repo. Some sections (Python env; .env management; MCP transport) carry forward to migration; others (prompt-pack management; per-Epic admin) are pre-migration only. For migration-native admin, consult the see-also list above.

---

**Audience:** System administrators and the project owner responsible for environment setup, tool connectivity, and operational health.
**Last Updated:** 2026-04-12 (migration banner actualized 2026-04-26) | **Project Phase:** Epics 1–14 complete (primary); hybrid clone is M5 SHIP-CONDITIONAL through 2026-05-03.

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

## Public Read-Only HUD Overlay (Story 42-4)

The operator HUD is served from `localhost` as the authority (GET-only, zero-mutation — see `docs/operator/hud-guide.md`). Story 42-4 adds an **optional, additive** outbound overlay so the operator can watch a live run from any browser or phone at one stable URL, **while no secret ever crosses the wire and localhost stays the authority**.

**What the app provides vs. what you configure.** The app ships:

- A **separate** public read-only app (`app/hud/public.py`, `python -m app.hud.public`) bound to its own local port (default `8792`, `HUD_PUBLIC_PORT`). It is a **positive-allowlist projection** of the same live run file — it serves only status, gate, progress/steps, ambient roster, health tiles, the 42-3 run-settings readout, and trace timings. It **never** serves the launch nonce, resume commands/digests, decision-card evidence, verbatim error/source text, credentials, or export paths (enforced in code + pinned by `tests/hud/test_public_surface_readonly_and_nonleak.py`).
- The **tunnel launcher** (`launch_public_overlay` in `app/marcus/orchestrator/preflight.py`), which reads tunnel config from `.env`/environment, launches the public app + a **named** tunnel child, and couples both to the run lifecycle (survives gate pauses; torn down after a short grace on terminal status — reuses the Story 42-2 status-aware owner). It **refuses** to open an anonymous quick-tunnel; if no tunnel is configured the overlay is simply absent and the run is unaffected.

**You configure** (operator-gated live evidence): the actual Cloudflare Tunnel + Access (preferred) or Tailscale Serve (fallback), the identity policy, and the stable hostname. The overlay is inert until these env vars are present.

### Preferred path — Cloudflare Tunnel + Access (named, identity-aware)

1. **Create a named tunnel** in the Cloudflare Zero Trust dashboard (Networks → Tunnels → *Create a tunnel* → **Cloudflared**). Name it something stable, e.g. `marcus-hud`. Copy the **tunnel token** it shows.
2. **Route a stable hostname to the tunnel.** In the tunnel's *Public Hostname* tab, add e.g. `hud.yourdomain.com` → **Service** `http://localhost:8792` (the overlay port). This hostname is reserved and stable run-to-run; a fresh run reuses the same hostname.
3. **Restrict with Cloudflare Access.** In Zero Trust → Access → Applications, add a *Self-hosted* app for `hud.yourdomain.com` with a policy that **allows only your identity** — an *Emails* rule listing your address (one-time PIN by email) or an IdP login with MFA. Do **not** use a reusable shared password / Basic-Auth. Set a short session duration.
4. **Set the env vars** in `.env` (gitignored — the token is a secret):

   ```
   HUD_TUNNEL_MODE=cloudflare
   HUD_TUNNEL_TOKEN=<the tunnel token from step 1>
   HUD_TUNNEL_HOSTNAME=hud.yourdomain.com
   HUD_PUBLIC_PORT=8792
   ```

   (Locally-managed alternative: instead of `HUD_TUNNEL_TOKEN`, set `HUD_TUNNEL_NAME=marcus-hud` with a `~/.cloudflared/config.yml` ingress mapping the hostname to `http://localhost:8792`.) Install `cloudflared` and confirm it is on `PATH` (or set `HUD_TUNNEL_CLOUDFLARED_BIN`).

### Fallback — Tailscale Serve (private, tailnet-only)

1. Install Tailscale and join the operator's tailnet on the run machine; give the machine a stable name (its `*.ts.net` name is intrinsic and stable).
2. Set:

   ```
   HUD_TUNNEL_MODE=tailscale
   HUD_PUBLIC_PORT=8792
   ```

   The launcher runs `tailscale serve --bg http://127.0.0.1:8792`; the page is reachable at `https://<machine>.<tailnet>.ts.net` to your tailnet devices only. Identity is enforced by your tailnet ACL — no anonymous access. (Teardown between runs, if desired: `tailscale serve --https=443 off`.)

### ngrok reserved domain — one stable, no-login public URL (Story 42-8)

The operator directed a **plain, stable, no-login** public URL for this HUD: nothing proprietary is shown and the surface is read-only, so an anonymous public URL is acceptable here. `ngrok` with a **reserved domain** gives you ONE unchanging `https://` URL you can open from any device, run after run. (The non-leak positive-allowlist scrub still applies — free belt-and-suspenders.)

Everything is configured from `.env` — **no separate `ngrok config add-authtoken` step is required** (though it still works if you prefer it):

1. **Install ngrok** on the run machine (the `ngrok` binary must be on `PATH`, or set `HUD_TUNNEL_NGROK_BIN` to its full path). See <https://ngrok.com/download>.
2. **Reserve a domain** in the ngrok dashboard (Universal Gateway → Domains → *New Domain*). A free static domain looks like `something.ngrok-free.app`; a paid plan lets you use a custom domain. This reserved domain is what keeps the URL **stable run-to-run** (without it, ngrok would hand out a random per-run URL).
3. **Copy your authtoken** from the ngrok dashboard (Getting Started → Your Authtoken).
4. **Set the env vars** in `.env` (gitignored — the authtoken is a secret):

   ```
   HUD_TUNNEL_MODE=ngrok
   HUD_TUNNEL_NGROK_DOMAIN=something.ngrok-free.app
   HUD_TUNNEL_NGROK_AUTHTOKEN=<your ngrok authtoken>
   HUD_PUBLIC_PORT=8792
   ```

   That's it. The launcher runs `ngrok http --domain=something.ngrok-free.app 8792` and hands the authtoken to the ngrok child **through its process environment** (`NGROK_AUTHTOKEN`) — so the secret never appears on the command line, in a log, or on the wire. The stable URL `https://something.ngrok-free.app` is logged at launch and written to `.hud-public-url` in the run dir.

   - **Authtoken source is your choice.** If you omit `HUD_TUNNEL_NGROK_AUTHTOKEN`, the launcher leaves authentication to ngrok's own config — so a prior `ngrok config add-authtoken <token>` on the run machine also works. The `.env` path is preferred (one place, no extra CLI step).
   - **Bin override:** set `HUD_TUNNEL_NGROK_BIN` if `ngrok` is not on `PATH`.
   - If `HUD_TUNNEL_NGROK_DOMAIN` is absent, the ngrok overlay is **inert** (the launcher refuses to open a random per-run quick-tunnel) and the run is unaffected — exactly like the other modes when unconfigured.

> **ngrok-free interstitial note.** On the free tier, an anonymous visitor first sees a one-click **"You are about to visit …"** ngrok warning page before the HUD loads. This is expected and harmless for a self-viewed read-only HUD — just click through. To skip it, either send the `ngrok-skip-browser-warning` request header (any value) or use a paid ngrok plan. It does **not** affect the stability of the reserved-domain URL.

### Validation checklist (operator-gated live leg)

- [ ] With no `HUD_TUNNEL_MODE`, start a run: local HUD works at `http://localhost:8791`; no overlay child spawns (overlay absence never affects the run).
- [ ] With Cloudflare config set, start a run: `hud.yourdomain.com` prompts for identity (login/MFA or emailed PIN); an un-allowlisted identity is denied.
- [ ] With ngrok config set (`HUD_TUNNEL_MODE=ngrok` + reserved `HUD_TUNNEL_NGROK_DOMAIN` + `HUD_TUNNEL_NGROK_AUTHTOKEN`), start a run: the reserved `https://<domain>` is reachable (no login) and is the **same** URL on a second run; a free-tier visitor clicks through the ngrok interstitial once. Confirm the authtoken appears in **no** log line.
- [ ] After authenticating, the page renders status/gate/progress/roster/settings/trace and updates live.
- [ ] Open the page from a **second device** (phone) — reachable at the same URL under identity.
- [ ] **Non-leak spot check**: view-source / DevTools on the public page and on `GET /projection` — confirm no launch nonce, no `resume`/paste command, no decision-card evidence, no file paths. (The hermetic test enforces this in code; this is the live confirmation.)
- [ ] Pause at a gate: the public page stays live across the pause (Story 42-2 coupling). Reach a terminal status: the overlay tears down after the grace; the stable hostname then honestly shows offline.
- [ ] Idle (no active run): the overlay app, if running, shows **"HUD offline — no active run"**; it never renders a stale/foreign run.

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

---

## Migration Admin Appendix

> **Authored 2026-04-26 (post-Slab-3 close).** Companion to the legacy admin-guide content above. Documents migration-specific admin operations introduced by the LangChain/LangGraph re-platform.

### Quick-start for migration ops

```bash
# 1. Fresh-clone bootstrap (Windows PowerShell)
pwsh scripts/setup/first_clone_bootstrap.ps1
# OR (Linux / macOS)
bash scripts/setup/first_clone_bootstrap.sh

# 2. Daily health audit
.venv/Scripts/python.exe scripts/utilities/migration_health_dashboard.py

# 3. Pre-trial preflight
.venv/Scripts/python.exe scripts/utilities/trial_run_preflight.py --trial-corpus <path>
```

### Postgres setup (per CLAUDE.md `project_no_docker` operator preference)

Postgres runs **natively on the host** (NOT Dockerized). Required for:
- LangGraph checkpointer (per-trial state persistence; Slab 1 substrate)
- Learning ledger (Slab 4.4 ledger_events table)

**Setup:**
```bash
# 1. Install Postgres natively (e.g., via brew on macOS, apt on Linux, installer on Windows)
# 2. Create database
createdb course_dev_ide_migration

# 3. Set DATABASE_URL in .env (.env.example carries the template)
# 4. Load ledger schema (Slab 4.4)
psql $DATABASE_URL -f app/ledger/schema.sql

# 5. Verify via preflight
.venv/Scripts/python.exe scripts/utilities/trial_run_preflight.py --skip-env
```

### MCP server config (.mcp.json + env-routed)

The migration consumes MCP servers via `.mcp.json` at repo root. Currently configured: `gamma`, `canvas-lms`, `notion`, `scite`, `consensus`. Server credentials sourced from environment per `scripts/run_mcp_from_env.cjs`.

**Adding a new MCP server:** edit `.mcp.json` + add corresponding env var to `.env.example` + document in this section.

### Sanctum population (per-agent BMAD memory)

Each migrated specialist + Marcus has a sanctum directory under `_bmad/memory/`:
- `_bmad/memory/bmad-agent-marcus/` — Marcus orchestrator persona + access boundaries + chronology
- `_bmad/memory/wanda-sidecar/` — Wanda (podcast production) sidecar
- ... (plus per-specialist sidecars per Slab 2 close)

**Cold-read discipline (FR30):** Marcus's `_init_marcus()` reads sanctum fresh on each session-open via allowlist-based `_read_marcus_sanctum_digest()`; fingerprint stored as `(sha256, session_id)` in RunState.

**Operator content authoring per A-R5-2c.2:** dev-agent skeleton-only; operator populates persona/access-boundaries/chronology content via First Breath ceremony. Skeleton placeholders carry `<!-- TODO: operator-populate -->` markers.

### Frozen-graph v42 ceremony (Slab 4.5)

Runtime/graphs/v42/ holds reproducibility-ceremony artifacts: manifest-snapshot + dev-graph-manifest-snapshot + pack-version + dispatch-registry-snapshot + compiled-graph-digest. Tier-1/2/3 bump policy per `docs/dev-guide/frozen-graph-version-ceremony.md` (post-Slab-4.5 close).

### Sanctum-watcher (Slab 4.6 FR59)

`app/runtime/sanctum_watcher.py` (post-4.6 close) wraps `watchdog.observers.Observer` against `_bmad/memory/**/*.md`. File-mutation triggers ledger SanctumMutationEvent emission + DecisionCardMeta `sanctum_warnings` enrichment at next gate fire (NFR-O3 non-fatal).

**Admin config:** debounce-ms via `SANCTUM_WATCHER_DEBOUNCE_MS` env var (default 500ms). Disable per-trial via runtime flag if needed for performance.

### Daily admin checklist (post-Slab-4 expectations)

```bash
# Health snapshot
.venv/Scripts/python.exe scripts/utilities/migration_health_dashboard.py

# Lockstep contracts
.venv/Scripts/lint-imports.exe --config pyproject.toml

# Pre-existing test failures (should be 0 post-Codex-Slab-4 close)
.venv/Scripts/python.exe -m pytest --collect-only -q 2>&1 | tail -3

# Conditional gate watch (M2 Wondercraft / M3 Texas / M4 if conditional)
# See docs/operator/conditional-gate-addendum-playbook.md for resolution paths

# Deferred inventory consultation (refresh per CLAUDE.md §1)
grep -c "^| \*\*" _bmad-output/planning-artifacts/deferred-inventory.md  # row count
```

### Forward-port playbook (post-M5 SHIP verdict per FR61)

If M5 verdict at 5a.5 = SHIP, see `docs/operator/post-m5-runbook.md` for the FR61 forward-port playbook activating per-capability forward-port from primary repo (frozen at upstream/master @ 3ed7c56 per `MEMORY.md::project_upstream_severance`).
