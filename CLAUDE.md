# Claude Code — project instructions

This repository uses BMAD methodology. For sprint-style runs, follow the **BMAD sprint governance** checklist below (mirrors `.cursor/rules/bmad-sprint-governance.mdc` and `.github/copilot-instructions.md` for VS Code / GitHub Copilot).

## Operator preference: run shell commands autonomously (minimal permission prompts)

**The operator strongly prefers that you execute bash/shell/PowerShell commands without stopping to ask for approval on every invocation.** Per-command permission dialogs are disruptive during BMAD sprints, migration work, and test loops. Default to **proceeding**: run `pytest`, `ruff`, `uv`, `python`, `git` (read-only and normal workflow: status, diff, add, commit when asked), `npm`/`npx` when the task requires it, linters, formatters, and one-off diagnostics **as the story or task requires**, and **batch** related commands (`&&` or a small script) when that reduces round-trips.

- **Do not** ask the human to confirm every trivial or repetitive command. Reserve explicit confirmation for **destructive or irreversible** operations you genuinely cannot do safely without them (e.g. force push to `main`, mass `rm -rf` outside obvious build artifacts, production credential use—use judgment).
- **Cursor / Claude Code:** the operator wants **auto-approve** / **Run everything**-style behavior for this workspace when the product offers it; this section documents the **same intent** for any agent reading project instructions. (Product-level settings still may need to be enabled in the editor; this file is the project signal.)

This preference does **not** override **migration sandbox-AC** rules later in this file: story specs must still avoid forbidden operator-only CLIs in *dev-agent* AC blocks. It **does** mean: when implementation is in scope, **run the allowed tooling freely** to verify and close work.

## Push cadence policy — push at least once every 2 hours of active work

**Local commits alone are NOT durable storage.** A single-disk failure or accidental data loss between commits and a push wipes out unpushed work. The operator also needs to access this repo from remote locations and machines, which is impossible while commits live only on one disk. **Mitigation: push to `origin` at least once every 2 hours of active session work**, and ALWAYS push at session-WRAPUP Step 12 (no longer deferred by default).

Operating rules:

- **Proactive push triggers:** push to `origin/<current-branch>` whenever any of the following holds:
  - **≥ 2 hours** have elapsed since the last push (estimate from commit timestamps via `git log -1 --format=%ci HEAD` vs the timestamp of `git log -1 --format=%ci origin/<branch>`)
  - **≥ 5 commits** have accumulated ahead of origin (rough commit-count proxy when timestamps are ambiguous)
  - **A meaningful safety checkpoint just landed** — e.g., a story-close batch commit, a governance-amendment ratification, a session-START state-anchoring commit, or any commit the operator would not want to redo
  - **The operator is about to step away from the machine** for any meaningful interval (announce + push first)
- **Session-WRAPUP Step 12 default is now PUSH (not defer).** The "merge-to-master deferred per Slab 7c PRD scope" exception still applies for the Slab 7c branch (push to `origin/dev/langchain-langgraph-foundation` only; do NOT merge to master), but **a working-branch push at session-close is mandatory**, not deferred.
- **Force-pushes remain forbidden** absent explicit operator authorization. Standard `git push origin <branch>` only.
- **Hooks must not be bypassed.** No `--no-verify` unless the operator explicitly authorizes; if a pre-push hook fails, investigate the underlying issue before re-pushing.
- **Track the trigger explicitly.** When proactively pushing mid-session, surface a one-line note to the operator: "pushed N commits to origin/<branch> at <commit-sha> per push-cadence policy (trigger: <2h-elapsed | 5-commit-threshold | safety-checkpoint>)." This keeps the operator informed without interrupting the work loop.

This policy supersedes the prior "push deferred per session-protocol Step 12 default — operator authorizes" pattern. Implementation: agents reading this file proactively push at the triggers above without per-push permission prompts (per the operator-preference section earlier in this file). The standard `git push origin <branch>` is non-destructive when strictly ahead; permission-gate it only if a force-push or unusual remote arrangement applies.

Ratified 2026-05-05 post-session-close after observing that 40 commits sat unpushed for ~7-8 hours of active work — single-machine-failure risk realized in policy gap. Codified at `408b868` predecessor (HEAD at `408b868` before this codification).

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

4. **Every multi-slab retrospective close** (Mary AM-7 codified at S5 Tier-1 2026-05-07; closes the gap pre-Trial-3 cleanup S1 P0-IH discovered). At the close of every retrospective spanning multiple slabs (e.g., Slab 7a+7b+7c retrospective; future multi-slab retros), execute a hygiene pass: archive closed entries to bottom-of-file §"Closed Entries — Archived"; refresh stale "reactivate at Slab N" triggers where Slab N has now closed; merge duplicate framings; update Inventory Summary count. Without this, inventory accumulates 60%+ noise overhead per arc (per S1 P0-IH discovery: 24 closed entries clogging a 41-active register).

Maintenance: the inventory is updated at (a) each Epic retrospective close, (b) each story closure that names a new follow-on, (c) any session-wrapup where the operator flags a new deferred item.

**Direction-of-cleanup-may-flip-with-substrate-evolution caveat (Mary post-S2 amendment; codified at S6 2026-05-08):** when a deferred-inventory entry declares a CLEANUP DIRECTION (e.g., "delete X; keep Y"), the entry MUST carry an explicit "direction may flip if substrate evolves" caveat. Reactivation review re-validates direction before dispatch. Precedent: `migration-tech-debt-app-marcus-stub-disposition` filed 2026-04-26 with direction "delete app/marcus/, keep marcus/"; by S2 dispatch (2026-05-07), Slab 6/7 production runtime had landed in app/marcus/, inverting the canonical-vs-shim direction. Direction was correctly flipped at S2; without the caveat, dispatch could have executed the original direction-of-cleanup blindly.

## Trial-postmortem governance (S6 2026-05-08; per methodology.md §9)

Trial-run postmortems consult `docs/trials/cross-trial-learnings.md` AND file their harvest entries per the four-question routing discipline at `docs/trials/methodology.md §7`. Reactivation-trigger firings are recorded bidirectionally (inventory entry strikethrough cites cross-trial entry; cross-trial entry cites inventory entry). Cross-trial pattern synthesis fires every 3 trials OR at Epic-close. Methodology updates per `methodology.md §8` lifecycle protocol.

## Party-mode impasse-resolution chain (2026-05-19; operator-ratified)

When `bmad-party-mode` reaches a documented impasse on a substantive decision (one full round of party-mode complete; disagreement explicitly stated; no consensus option remains acceptable to all relevant voices per sprint-governance §6), the orchestrator follows this escalation chain **before** escalating to the human operator:

1. **Dr. Quinn synthesis round.** Spawn Dr. Quinn (`bmad-cis-agent-creative-problem-solver`) via the Task tool with the FULL impasse context: every voice's position verbatim, the disposition options on the table, the project context relevant to the choice, and an explicit ask to either (a) find a systems-level synthesis option that resolves the contradiction the four voices stepped past, or (b) declare honest failure. Quinn may NOT just vote one of the existing options — that's not synthesis. Quinn must also predict each voice's reaction to the proposed synthesis so the orchestrator can judge consensus viability.
2. **John (PM) tiebreaker round.** ONLY if Dr. Quinn explicitly declares synthesis failure. Spawn John (`bmad-agent-pm`) with the same impasse context plus Quinn's synthesis attempt, and authorize John to make the final decision + declare next steps unilaterally as PM. The orchestrator executes John's decision verbatim.
3. **Escalate to human operator** ONLY if both Quinn and John fail to produce an actionable verdict (rare; reserved for true strategic impasses).

Precedent established at Slice A R1-vs-R2-vs-R3 impasse 2026-05-19 during pre-Trial-3 housekeeping arc; Dr. Quinn succeeded with R5 "Probe-Capture" synthesis (3-of-4 voice consensus with named dissent). Full session record at `_bmad-output/planning-artifacts/sprint-change-proposal-2026-05-19.md` and `SESSION-HANDOFF.md`.

The chain is binding for orchestrator-facilitated party-mode rounds during multi-story BMAD work (per sprint-governance §§2/4/5/6). Operator authority overrides at any link in the chain.

## Cleanup-arc execution mode (S6 2026-05-08)

## Cleanup-arc execution mode (S6 2026-05-08)

Multi-session cleanup arcs (e.g., the pre-Trial-3 cleanup arc 2026-05-07/08; future post-Trial-N cleanup arcs) execute **Claude-direct** by default. The NEW CYCLE Codex hand-off pattern (Claude pre-author → Codex T1-T10 → Claude T11) is reserved for **formal `bmad-dev-story` discipline** on substrate-impacting stories ratified by party-mode. Cleanup work in multi-session arcs is Claude-direct to avoid P3 anti-pattern (operator-as-bridge friction with no payoff). Operator authority overrides this default.

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
