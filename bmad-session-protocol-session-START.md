# BMAD v6 Session Protocol: Start-of-Session

Companion to `bmad-session-protocol-session-WRAPUP.md`. Together these two files guarantee reliable context transfer between sessions.

## Canonical session protocol set

The canonical BMAD session protocol is this pair:
- `bmad-session-protocol-session-START.md`
- `bmad-session-protocol-session-WRAPUP.md`

If a user or older note refers to a literal "session xyz" document and no such file exists, treat that as a stale label and use this START/WRAPUP pair instead. Record the assumption in session notes if it affects execution.

## §0: Project purpose TL;DR (for unfamiliar agents)

**Purpose:** Persistent collaborative intelligence infrastructure for systematically scaling creative expertise in online course content production. A deterministic, manifest-compiled runtime orchestrator coordinates a roster of LangGraph specialist agents (current roster + count: [`docs/ONBOARDING.md`](docs/ONBOARDING.md) §3.2) that manipulate professional media tools through skills backed by Python scripts; its operator-facing conversational surface — **Marcus-SPOC** — picks the workflow at the front door and narrates each human-in-the-loop gate, with the operator's confirmed verdict (never the chatting LLM) advancing the run. This is distinct from the BMAD-persona **Marcus** under `skills/bmad-agent-marcus/` (planning persona, has the sanctum; no connection to a live run). BMAD memory sidecars capture creative decision-making patterns for refinement and reuse.

> **⛔ DESIGN GUARDRAIL (operator-stated 2026-06-30; binding):** The **only product goal is the Marcus-SPOC runtime orchestrator** driving a real APP instance. The BMAD-persona Marcus's **"concierge"/exploratory/trial/proofing runs are off-the-books discovery vehicles, NOT a goal** — they may surface real production-codebase defects worth fixing on their own merits, but **we do NOT design or shape the production codebase to make those proofing runs work.** Fix what a proofing run finds only because it improves the product (the SPOC runtime), never to "make the concierge run pass." Full statement in [`CLAUDE.md` §CRITICAL DESIGN GUARDRAIL](CLAUDE.md) + the FRAMING PRINCIPLE banner in [`docs/STATE-OF-THE-APP.md`](docs/STATE-OF-THE-APP.md).

**Architecture:** See [`docs/ONBOARDING.md`](docs/ONBOARDING.md) for the structural mental model (8 layers, 14-step guided tour, derived from a knowledge-graph scan of the codebase). Read this once per fresh agent context.

**Repo contract:**
```
course-content/courses/     # Published content
course-content/staging/     # Agent drafts (human review queue)
skills/                     # Agent skill directories (auto-discovered)
_bmad/                      # BMad Method artifacts
docs/                       # Architecture + agent guides
scripts/                    # Python infrastructure
state/                      # YAML configs + SQLite runtime
```

## Context transfer contract

The startup protocol **reads** certain files; the WRAPUP protocol **writes** them. Every read must have a corresponding write, or context is lost.

| File | Startup reads | Wrapup writes | Role & SSOT status |
|------|:---:|:---:|------|
| `SESSION-HANDOFF.md` | Always (canonical) | WRAPUP Step 8 (+ roll-down) | **Authored SSOT — chronology.** Tracked; survives across clones. Current arc + 1 prior hot; older → `SESSION-HANDOFF.history.md`. |
| `docs/STATE-OF-THE-APP.md` | §0 guardrail + on-demand | WRAPUP Step 9 | **Authored SSOT — product truth.** Current + 1 prior banners hot; older → `STATE-OF-THE-APP.history.md`. FRAMING PRINCIPLE banner stays permanently. |
| `sprint-status.yaml` | Step 4 | WRAPUP Step 4a | **Authored SSOT — Kanban.** Value-reconcile only (line-regex + `tripwire_events` parsers); done blocks → `sprint-status.history.md`. |
| `deferred-inventory.md` | Step 4 (governance) | governance events | **Authored register — governance.** Closed entries → `## Closed Entries — Archived` at retrospective milestones. |
| `bmm-workflow-status.yaml` | Step 4 | WRAPUP Step 3 | BMAD phase (structured YAML). Comment history → `bmm-workflow-status.history.md`. |
| `next-session-start-here.md` | If present (per-clone cache) | WRAPUP Step 7 = **GENERATED** | **Generated view (fail-loud)** via `generate_next_session.py`; gitignored. Falls back to SESSION-HANDOFF. |
| `docs/project-context.md` | Step 1 | WRAPUP Step 5 = **GENERATED** | **Generated view (thin header)** via `generate_project_context.py`; base doc below the `<!-- BASE-DOC -->` marker is hand-authored; addendum history → `project-context.history.md` (generator-fed). Glob-loaded by ~59 skills — never move it. |
| `docs/ONBOARDING.md` | Once per fresh agent context | WRAPUP Step 9 if regenerated | **Architectural mental model** — knowledge-graph-derived. |
| `docs/agent-environment.md` | Step 1 | WRAPUP Step 5 | MCP / API / tool / skill inventory. |
| Guides (user/admin/dev) | Step 4 on-demand | WRAPUP Step 9 | Large stable living docs. |

> **Key principle:** `SESSION-HANDOFF.md` is the cross-machine source-of-truth. The **status-surface SSOT & retention contract** (three authored SSOTs — Kanban / chronology / product-truth — plus the deferred-inventory register; `next-session-start-here.md` + `project-context.md` are fail-loud generated views; cold history rolls to dated `*.history.md` siblings at arc close) is defined in [`bmad-session-protocol-session-WRAPUP.md`](bmad-session-protocol-session-WRAPUP.md) and [`spec-status-surface-consolidation.md`](_bmad-output/implementation-artifacts/spec-status-surface-consolidation.md). If `next-session-start-here.md` is missing (fresh clone), regenerate it (`generate_next_session.py`) or reconstruct from the latest SESSION-HANDOFF.md section + recent commits, and record it in WRAPUP Step 8.

---

## First Session Setup (cold start)

Use this the first time you open this BMAD project in a new tool context. Once confirmed, proceed directly to the Start-of-Session sequence below for all subsequent sessions.

1. Confirm root paths exist: `_bmad/`, `_bmad-output/`, `docs/`, `course-content/staging/`, `course-content/courses/`, `config/content-standards.yaml`, `.env`, and the IDE skill folder (`.cursor/skills/` or `.claude/skills/`). If any path is missing, install or initialize BMAD before continuing.
2. Read [`docs/ONBOARDING.md`](docs/ONBOARDING.md) (~230 lines) for the architectural mental model + complexity hotspots + 14-step guided tour. This is the fastest cold-start ramp asset; the knowledge-graph scan it derives from is at `.understand-anything/knowledge-graph.json`.
3. If the session involves production orchestration, content production, or APP runs: read [`skills/bmad-agent-marcus/SKILL.md`](skills/bmad-agent-marcus/SKILL.md) and follow its activation sequence (sanctum batch under `_bmad/memory/bmad-agent-marcus/`) before any specialist invocation. Per CLAUDE.md "Marcus first" cold-start rule.
4. Skim [`docs/agent-environment.md`](docs/agent-environment.md) for the MCP/API/skill inventory, and [`CLAUDE.md`](CLAUDE.md) for project rules (sprint governance, push cadence, deferred-inventory governance).
5. **Cursor dual-agent-family check (when opening in Cursor):** confirm `.cursor/rules/bmad-dual-agent-families.mdc` is present (alwaysApply). Know which family this session needs:
   - **Family A (native BMAD stock)** — party green-lights / workflow seats: use **Agent** mode; spawn independent subagents; optional stubs under `.cursor/agents/` (john/winston/amelia/murat/quinn) redirect into BMAD skills. Do **not** use `/multitask` as the party switch.
   - **Family B (custom skill+sanctum)** — Marcus / Irene / Gary / …: activate via `skills/bmad-agent-{name}/SKILL.md` + `_bmad/memory/bmad-agent-{name}/`. Absence from `agent-manifest.csv` is intentional.
   Details: [`AGENTS.md`](AGENTS.md) §Dual agent families + the Cursor rule above.

> **Gitignore caveat:** `.env`, `state/runtime/*.db`, binary media under `course-content/`, and `next-session-start-here.md` are all gitignored. File-search tools (glob, find, ripgrep) that respect `.gitignore` will not see them. Always verify gitignored files by **reading the file directly**, never by pattern search.

---

## Session class — declare at session open

Before running the steps below, name the expected session class. This determines step engagement at WRAPUP. Mid-session upgrade is allowed; downgrade is not.

| Class | Pattern | Steps engaged |
|---|---|---|
| **S — Substrate** | Story/epic dispatch; schema, pipeline-manifest, runtime, or test edits; content production | All steps including Step 1a (Cora outstanding-findings gate). |
| **D — Docs / Tooling** | Markdown-only edits, lint refactors, knowledge-graph refresh, tool/plugin install, session-meta edits | Steps 1, 2, 3, 10, 12. Step 1a SKIPPED — read `next-session-start-here.md` unresolved-issues block directly. |
| **P — Planning** | PRD, architecture, epics/stories authoring; party-mode rounds; retrospectives | Steps 1, 2, 3, 7, 10, 11, 12. Step 1a only if prior session left invariant-touching findings. |

If the session unexpectedly touches a substrate file, upgrade to Class S and run the missed Step 1a check before continuing.

### How session class is communicated

Three handoff points, in order:

1. **Forecast** — The prior session's WRAPUP (Step 7) writes the expected class at the top of `next-session-start-here.md` (one line: `**Expected class for next session:** <S|D|P> — <reason>`).
2. **Confirm at open** — During Step 1 of this protocol, the agent reads the forecast and announces the operating class to the operator: *"Opening as Class D (docs/tooling) per next-session-start-here.md forecast and your stated objective `<X>`."* The operator confirms or overrides in plain text. If `next-session-start-here.md` is missing (fresh clone), infer class from SESSION-HANDOFF.md's last session-close section header (which carries the prior session's **final class**) + the user's stated objective, then announce the same way.
3. **Verify at close** — WRAPUP Step 11 runs the class-drift self-check against the actual diff; WRAPUP Step 8 records this session's **final class** (after any mid-session upgrade) in the new SESSION-HANDOFF.md section header.

---

## Start-of-Session (hot start)

Execute these steps in order at the beginning of every session.

### 1. Load session context

**Always read:**
- `SESSION-HANDOFF.md` — the latest session-close section (cross-machine canonical).
- `next-session-start-here.md` — if present (local cache); if absent, reconstruct from SESSION-HANDOFF.md per the contract note above.
- `docs/project-context.md`
- `docs/agent-environment.md`

**Read once per fresh agent context** (new chat / new Claude or Cursor session in this project for the first time):
- `docs/ONBOARDING.md` — architectural mental model. Check freshness: compare `.understand-anything/meta.json::gitCommitHash` against HEAD; if it is behind by the WRAPUP Step 9 regeneration threshold (≥10 files changed in `app/`/`scripts/`/`skills/`, or pipeline-manifest/schema/manifest changes, or an Epic close), treat the doc as stale and flag at WRAPUP Step 9.

### 1a. Outstanding-findings gate

**Class S only.** Skip for Class D and Class P (unless Class P inherits invariant-touching findings from the prior session).

For Class S sessions, ask Cora to run her Session-START (SS) protocol: scan `next-session-start-here.md` (and `SESSION-HANDOFF.md` if referenced) for deferred Step 0a Audra L1/L2 findings and acknowledged-but-not-remediated Step 0b pre-closure gaps. Cora presents the list with three choices:
- **Remediate first** — make findings the opening anchor; defer the originally-intended anchor.
- **Run `/harmonize` full-repo now** — re-verify against whole-repo invariants + full change window since handoff anchor; recommended when the prior session's audit trail is incomplete.
- **Proceed with original anchor, carrying findings forward** — findings must reappear in this session's WRAPUP Step 7.

If `next-session-start-here.md` cites findings but no `reports/dev-coherence/` report exists for the prior session, treat as missing-audit-trail and recommend the full-repo sweep.

**Tripwire pre-check:** if the most recent WRAPUP entry in Cora's `chronology.md` recorded a skipped Step 0, any `/harmonize` invoked in this session (mid-session or at WRAPUP) auto-promotes default scope from since-handoff to full-repo.

**For Class D / P sessions:** read the unresolved-issues block of `next-session-start-here.md` directly and decide whether to remediate, carry forward, or proceed. Log the decision; Cora's tripwire still applies on the second consecutive skip.

### 2. Confirm branch + worktree alignment

Run all of: `git status --short`, `git branch --show-current`, `git rev-parse --show-toplevel`, `git worktree list`. Compare against the branch instructions in `next-session-start-here.md`.

Reconciliation rules:
- If the current branch is a plausible successor to the recorded target (e.g., post-WRAPUP docs commits landed), treat the current branch as authoritative and reconcile the docs at this session's WRAPUP Step 7.
- If the current branch is clearly unrelated to intended next work, checkout the recorded target.
- If unexplained mismatch, treat `next-session-start-here.md` as stale and record a reconciliation note for WRAPUP Step 7.
- If a stale worktree appears (manually-removed directory), run `git worktree prune --verbose`.

**Dirty-worktree scope fence (mandatory):** classify uncommitted changes before any work:
- **Session-owned** — files this session is expected to touch.
- **Collaborative in-scope** — same-session changes by user or other active agents/browser contexts.
- **Pre-existing unrelated** — modified or untracked files outside session scope.

Rules: do not revert, normalize, or silently absorb unrelated changes; do not misclassify same-session collaborative changes; record any conflict immediately and plan around it.

### 3. Identify session target and BMAD phase

State a single session objective. Determine the applicable BMAD phase:
- **1-analysis** — brainstorming, research, ideation
- **2-planning** — PRD, UX, architecture
- **3-solutioning** — epics/stories, implementation readiness
- **4-implementation** — story development, code review, testing

Identify the target artifact (PRD / story / epic / module / lesson / content type) and acceptance criteria where applicable.

For the **APP agent team & skills catalog** and **BMAD glossary**, see [`docs/agent-environment.md`](docs/agent-environment.md) and [`docs/ONBOARDING.md`](docs/ONBOARDING.md) §3 (architectural layers). Do not duplicate those catalogs in this protocol.

### 4. Review BMAD status artifacts

**Skip for Class D unless tooling-status YAMLs are in scope.**

Always read (small, frequently changing):
- `_bmad-output/implementation-artifacts/bmm-workflow-status.yaml`
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — **canonical Kanban ledger** for epic/story progression through BMAD workflows. Treat it as the authoritative "where are we?" signal for story status; if it disagrees with a story file or hot-start note, reconcile at WRAPUP Step 4a (do not let the hot-start cache outrun this ledger).

Scan for relevance (read listing or headers, not full content):
- `_bmad-output/planning-artifacts/`
- `_bmad-output/brainstorming/`

Read on demand (large, stable; read only when session objective requires the detail):
- `docs/user-guide.md` (~260 lines)
- `docs/admin-guide.md` (~475 lines)
- `docs/dev-guide.md` (~730 lines)

**Interaction testing:** for any new agent / supporting skill, confirm presence of an Interaction test per the project's test guide.

### 5. Check content creation state (course-content sessions)

**Skip if session is pure system development.**

- Review `course-content/staging/` for pending human-review items.
- Check `config/content-standards.yaml` for current voice / accessibility requirements.
- Verify `.env` has required platform credentials (read the file directly — gitignored).
- Review active workflow docs in `docs/workflow/` (at minimum `human-in-the-loop.md`).

### 6. Open implementation files

**Class S only.** Skip for Class D and Class P.

Open primary implementation files for the target acceptance criteria, plus any existing tests for the target scope. Coding entry points are documented in [`docs/ONBOARDING.md`](docs/ONBOARDING.md) §3 (architectural layers) and §6 (complexity hotspots).

### 7. Review recent history

Review recent commits and unresolved TODOs/FIXMEs in the target scope.

### 8. Run a validation checkpoint (Class S)

Run the smallest relevant validation for the feature slice:
- **System development:** automated tests, linter / type checks, or manual verification.
- **Course content:** review staging content against content-standards.yaml; check platform connectivity.

Skip for Class D and Class P (no implementation surface to validate).

### 9. State definition of done

State one explicit definition of done for THIS session. A session DoD is scoped to the session, not the story — a story may span multiple sessions.

Course-content session examples:
- "Draft lesson 3 slides in staging/ with paired lesson plan, ready for human review."
- "Complete Canvas API integration for quiz deployment with one working example."
- "Generate Gamma prompt templates for presentation workflow with tool inventory entry."

### 10. Scope guard

Confirm the session objective is achievable in a single session. If multi-session, decompose to a single-session slice before proceeding.

### 11. Reuse-first pre-check (Class S + content-creation P)

Run a reuse-first check against the service catalog, design patterns, existing code, and `course-content/_templates/` + `resources/exemplars/` for content sessions.

### 12. Route via BMAD

Invoke `bmad-help` (`.cursor/skills/bmad-help/SKILL.md` or `.claude/skills/bmad-help/SKILL.md`) with your objective and current phase/story:

> Route me for this objective: <objective>. Current phase: <1-analysis | 2-planning | 3-solutioning | 4-implementation>. Current story: <id if applicable>.

`bmad-help` analyzes completed artifacts and recommends the next workflow or agent for the current phase. Follow only the routed workflow or agent.

Course-content routing examples:
- Ideation: `bmad-brainstorming`, `bmad-product-brief`, CIS skills.
- Content creation: `bmad-quick-dev`, content-focused custom skills.
- Review: `bmad-editorial-review-prose`, `bmad-review-adversarial-general`.

---
