# Claude Code — project instructions

This repository uses BMAD methodology. For sprint-style runs, follow the **BMAD sprint governance** checklist below (mirrors `.cursor/rules/bmad-sprint-governance.mdc` and `.github/copilot-instructions.md` for VS Code / GitHub Copilot).

## Custom agents vs. “registered” BMAD personas (cold start)

**Do not treat `_bmad/_config/agent-manifest.csv` as the full roster of invocable agents.** That file lists BMAD stock personas used by party mode (Mary, Amelia, Murat, etc.). Custom production agents for this repo — including **Marcus** — are **intentionally absent** from that manifest. If the operator says “talk to Marcus” (or another custom name), do **not** reply that they are “unregistered” based only on that CSV or on Claude Code’s native agent list.

**Two layouts coexist by design:**

- **Legacy / skill-quarantine tree:** Operator-facing `SKILL.md`, scripts, and references for many custom agents live under `skills/bmad-agent-{name}/`. This keeps them separate from BMAD stock paths under `_bmad/bmm/` and similar.
- **Sanctum tree (BMAD Method Builder / BMB):** Migrated agents keep persistent persona and continuity artifacts under `_bmad/memory/bmad-agent-{name}/`. For Marcus, that directory is `_bmad/memory/bmad-agent-marcus/`. Activation order is defined in [`skills/bmad-agent-marcus/SKILL.md`](skills/bmad-agent-marcus/SKILL.md) (read the skill first; then load sanctum files such as `INDEX.md`, `PERSONA.md`, per that skill).

On a cold session, **read the relevant `skills/bmad-agent-<name>/SKILL.md` (and sanctum per that skill)** to embody the agent — do not require a manifest row.

## Marcus first (APP production cold start)

For **course-content production**, orchestration, or anything that sounds like an APP run: **activate Marcus before other custom agents.** He is the operator-facing orchestrator; specialists (Irene, Gary, Vera, Texas, etc.) are normally **delegated through him**, not jumped to ad hoc unless the operator names one.

**Cold start, operator says “Marcus” / production / orchestration:** Immediately read [`skills/bmad-agent-marcus/SKILL.md`](skills/bmad-agent-marcus/SKILL.md) and follow its activation sequence (config load → sanctum batch under `_bmad/memory/bmad-agent-marcus/` or First Breath if sanctum is absent). Do not wait for `agent-manifest.csv` or a Claude Code “registered agent” list.

**Why Marcus first:** Once Marcus is correctly embodied and has loaded his skill + sanctum, he routes work using his references (for example `skills/bmad-agent-marcus/references/specialist-registry.yaml`) and conversation protocols. That keeps a single point of contact and avoids fragmented cold-start guesses about which specialist to impersonate.

For full session ramp (docs, handoff, deferred inventory), the operator may also use [`bmad-session-protocol-session-START.md`](bmad-session-protocol-session-START.md); Marcus activation still applies when production is in scope.

## BMAD sprint governance

1. **Epics and stories** must be produced with BMAD workflows only (for example `bmad-create-epics-and-stories`, `bmad-create-story`, `bmad-create-prd` / architecture / UX chains as appropriate, or `bmad-quick-dev` when that is the right path). If unsure which variant to use, read **`bmad-help`**, run **`bmad --help`**, or convene **`bmad-party-mode`** and ask the team to recommend full planning vs quick-dev vs another module skill.
2. **Green-lighting** and **initial review** of completed work must use **`bmad-party-mode`** (multi-agent roundtable). Do not substitute a single improvised persona for those gates.
3. Before marking any story **done**, you must run **`bmad-code-review`** on the changes in scope (or honor the user’s explicit “run code review” / equivalent invocation).
4. Proceed by **BMAD team consensus** across the active workflow steps and party-mode rounds; keep a short written record of agreed decisions when it affects scope or quality.
5. **Do not** stop the run except when **(a)** every in-scope story is **done** according to `_bmad-output/implementation-artifacts/sprint-status.yaml`, or **(b)** **impasse**: after documented party-mode rounds the team still cannot agree on a path—then pause and escalate to the human.
6. **Impasse** means: relevant voices in party mode have had at least one full round, the disagreement is stated explicitly, and no consensus option remains acceptable to all; it does not mean routine questions or a single agent’s uncertainty.

Related skills: `bmad-help`, `bmad-party-mode`, `bmad-code-review`, `bmad-quick-dev`, `bmad-sprint-run-charter`.

## Pipeline lockstep regime

For ANY story whose diff touches a path listed in `state/config/pipeline-manifest.yaml::block_mode_trigger_paths` (manifest itself, L1 check script, run_hud.py, progress_map.py, workflow_runner.py, v4.2 pack, v4.2 generator package, learning-event schema/capture, etc.), the dev agent reads [`docs/dev-guide/pipeline-manifest-regime.md`](docs/dev-guide/pipeline-manifest-regime.md) at T1 before any code. That document is the operational cheatsheet for the seven-component regime Epic 33 established; [`_bmad-output/planning-artifacts/epics.md §Epic 33 — Standing Regime`](_bmad-output/planning-artifacts/epics.md) is the Epic-scope authority.

**Pack version bumps are governance, not technical.** Any Tier-2 (minor, e.g., new pipeline step) or Tier-3 (major, e.g., new pack family) change per [`docs/dev-guide/pipeline-manifest-regime.md §Pack Versioning Policy`](docs/dev-guide/pipeline-manifest-regime.md) requires party-mode consensus BEFORE dev opens. Tier-1 (patch; prose/connective-tissue) proceeds under dev-agent authority gated by Cora's block-mode hook. Frozen-at-ship discipline: once a pack ships + a tracked trial-run completes, subsequent structural edits bump the version; the frozen prior-version pack stays on disk for audit.

Related stories (sprint reference): Epic 33 stories 33-1, 33-2, 33-1a, 33-3, 33-4, plus the 15-1-lite-marcus meta-test.

## Deferred inventory governance

The canonical register of deferred epics, deferred stories, and named-but-not-filed follow-ons lives at [`_bmad-output/planning-artifacts/deferred-inventory.md`](_bmad-output/planning-artifacts/deferred-inventory.md). It exists so deferred work does not drift out of view after an Epic closes.

Binding consultation points (all three are mandatory, not advisory):

1. **Every Epic retrospective (per `bmad-retrospective` skill).** During the "Next Epic Preparation" phase of the retrospective (per the skill's two-part format), the facilitator MUST review `deferred-inventory.md` against the closing Epic's new substrate / evidence / learnings. Flag now-ready-to-reactivate entries to the next sprint-planning round. Record which entries were consulted + the reactivation verdict per entry in the retrospective artifact.
2. **Every session hot-start.** `next-session-start-here.md` carries a standing "Deferred inventory status" line with current counts (backlog epics / deferred stories / follow-ons). Operator sees it every session open; serves as the "don't overlook" standing reminder.
3. **Every new story spec that names a follow-on.** The story author adds the follow-on to `deferred-inventory.md` §Named-But-Not-Filed Follow-Ons (not in the parent story spec alone — the inventory is the single source of truth for "what's queued but not filed yet"). Examples: 15-1-lite-marcus names 15-1-lite-irene + 15-1-lite-gary; 33-1a names §4.55 body-polish as a conditional follow-on. Both live in the inventory.

Maintenance: the inventory is updated at (a) each Epic retrospective close, (b) each story closure that names a new follow-on, (c) any session-wrapup where the operator flags a new deferred item.

## Texas retrieval

Shape 3-Disciplined retrieval contract lives at [`skills/bmad-agent-texas/references/retrieval-contract.md`](skills/bmad-agent-texas/references/retrieval-contract.md). The provider directory (`run_wrangler.py --list-providers`, or `retrieval.list_providers()`) is authoritative for "what Texas can fetch." Schema v1.1 changelog at [`_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md`](_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md).

## Lesson Planner MVP — dev-agent references

For any Lesson Planner MVP story (Epics 28-32), the dev agent reads the following references at T1 before any code is written:

- [`docs/dev-guide/pydantic-v2-schema-checklist.md`](docs/dev-guide/pydantic-v2-schema-checklist.md) — the 14 schema idioms that prevent the G6 MUST-FIX findings seen on Story 31-1 (`validate_assignment=True`, timezone-aware datetimes, UUID4 validation, triple-layer red-rejection on closed enums, `Field(exclude=True) + SkipJsonSchema` for internal audit fields, etc.).
- [`docs/dev-guide/dev-agent-anti-patterns.md`](docs/dev-guide/dev-agent-anti-patterns.md) — catalog of traps harvested from 27-0, 27-2, 31-1 Dev Notes and G6 code-review findings. Organized by category (schema, test-authoring, review-ceremony, refinement-iteration, Marcus-duality).
- [`docs/dev-guide/story-cycle-efficiency.md`](docs/dev-guide/story-cycle-efficiency.md) — governance rules for K-floor discipline (target 1.2-1.5× K, not 5×), single-gate vs dual-gate review policy with per-story designation, aggressive DISMISS rubric for G6 cosmetic NITs, T-task parallelism, and scaffold-adoption enforcement.

**Schema-shape stories** (31-2, 31-3, 29-1, 32-2, and any future story whose deliverable is a Pydantic-v2 model family + emitted JSON Schema + shape-pin tests) default to the scaffold at [`docs/dev-guide/scaffolds/schema-story/`](docs/dev-guide/scaffolds/schema-story/). Pre-instantiated stubs live at the story's target paths before `bmad-dev-story` begins; the dev agent extends those stubs rather than re-deriving from the 31-1 precedent. Scaffold updates and Pydantic-checklist updates land in lockstep.

## Lesson Planner governance enforcement

For Lesson Planner MVP stories (Epics 28-32), guidance is not enough; run the repo validator at the workflow gates:

- Before a story is finalized as `ready-for-dev`, run
  `python scripts/utilities/validate_lesson_planner_story_governance.py <story-file>`.
- Before `bmad-dev-story` begins on a Lesson Planner story, run the same validator again.
- Treat a non-zero result as a governance failure that must be remediated before proceeding.

Default behavior is **self-remediate first, escalate second**:

- If the validator fails, automatically fix every policy-preserving issue you can correct in the story spec or adjacent workflow artifacts.
- Rerun the validator after remediation and continue the run without waiting for the human if the story reaches PASS.
- Escalate to the human only if the remaining failure requires one of the following:
  - a gate-mode change (`single-gate` vs `dual-gate`)
  - a K-policy or target-range policy change
  - an intentional edit to
    [`docs/dev-guide/lesson-planner-story-governance.json`](docs/dev-guide/lesson-planner-story-governance.json)
  - a deliberate policy exception
  - a true party-mode impasse on scope, architecture, or governance interpretation

The validator currently enforces:

- expected `single-gate` vs `dual-gate` mode per story
- explicit `T1 Readiness` block presence
- required readings citation
- scaffold reference on schema-shape stories
- story-status vs `sprint-status.yaml` sync
- K-floor / target-range rules, including any story-specific K contract encoded in the policy file

Closeout hygiene remains mandatory:

- update `sprint-status.yaml` first
- update `next-session-start-here.md` second
- update any top-level plan or status line that would otherwise drift

## LangChain/LangGraph migration — sandbox-AC + gate-mode governance

For migration stories (Slab 1–5 under `_bmad-output/planning-artifacts/epics-langchain-langgraph-migration.md`), two additional validators run at workflow gates to prevent the two failure modes seen in Slab 1 kickoff (unexpected CLI-on-PATH assumptions, relitigated gate-mode decisions).

### Sandbox-AC validator — "verify via shipped deps, not operator CLIs"

- **Before a migration story is finalized as `ready-for-dev`**, run:
  `python scripts/utilities/validate_migration_story_sandbox_acs.py <story-file>`
- **Before `bmad-dev-story` begins on a migration story**, run the same validator again.
- The validator scans `## Acceptance Criteria` sections for shell invocations in **dev-agent** AC blocks (as opposed to `(operator-gated)` / `AC-*-B` blocks, which are allowed to invoke any CLI) and fails if any forbidden CLI appears. Inventory at [`docs/dev-guide/migration-ac-sandbox-inventory.json`](docs/dev-guide/migration-ac-sandbox-inventory.json). Forbidden set currently includes `docker`, `docker-compose`, `psql`, `pg_dump`, `aws`, `gcloud`, `az`, `gh`, `kubectl`, `helm`, `redis-cli`, `mongo`, `mysql`, `curl`, `wget`. `ffmpeg` warns.
- **Remediation is structural, not cosmetic:** either (a) split the AC into dev-agent (verified via shipped Python dep — `psycopg` / `boto3` / `PyGithub` / `httpx` — with `pytest.skip(...)` when service unreachable) + operator-gated (evidence pasted into Completion Notes once), or (b) replace the CLI invocation with the shipped dep. Do **not** suppress the warning.
- Inventory additions to `dev_agent_available` require party-mode consensus; additions to `dev_agent_forbidden` can be dev-agent authority (strictly expanding the forbidden set is safe).

### Gate-mode governance

- Authoritative gate-mode designation per migration story lives in [`docs/dev-guide/migration-story-governance.json`](docs/dev-guide/migration-story-governance.json) (freeze date 2026-04-22).
- `bmad-create-story` on a migration story **reads that file for the gate mode** — do not relitigate at story-authoring time.
- Changing a story's gate mode requires party-mode consensus and a version bump in the governance JSON.
- Slab 2b stories 2b.2–2b.14 are pre-designated single-gate (they follow the 2b.1 TEMPLATE scaffold pattern) — do not escalate to dual without a scaffold-breaking reason.
