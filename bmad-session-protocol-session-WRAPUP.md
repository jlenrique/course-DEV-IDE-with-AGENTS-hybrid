# BMAD v6 Session Protocol: End-of-Session (Shutdown)

Companion to `bmad-session-protocol-session-START.md`. Together these two files guarantee reliable context transfer between sessions.

## Context transfer contract

The startup protocol **reads** certain files; the wrapup protocol **writes** them. Every read must have a corresponding write, or context is lost.

| File | Startup reads | Wrapup writes | Role |
|------|:---:|:---:|------|
| `SESSION-HANDOFF.md` | Always (canonical) | Step 8 | **Cross-machine canonical record** — tracked. Survives across clones. Lessons, decisions, validation, permanent archive. |
| `next-session-start-here.md` | If present (per-clone cache) | Step 7 | **Local hot-start cache** — gitignored per hybrid-clone policy. Action-oriented. If absent on a fresh clone, reconstruct from SESSION-HANDOFF.md + recent commits. |
| `docs/ONBOARDING.md` | Once per fresh agent context | Step 9 if regenerated | **Architectural mental model** — knowledge-graph-derived structural ramp. |
| `docs/project-context.md` | Step 1 | Step 5 | Current state, key decisions, architecture summary. |
| `docs/agent-environment.md` | Step 1 | Step 5 | MCP / API / tool / skill inventory for agents. |
| `bmm-workflow-status.yaml` | Step 4 | Step 3 | BMAD phase and workflow transitions. |
| `sprint-status.yaml` | Step 4 | Step 4a | Epic / story Kanban state. |
| Guides (user/admin/dev) | Step 4 on-demand | Step 9 | Large stable docs — updated only when content changes. |
| `reports/dev-coherence/<ts>/` | — | Step 0 (Class S only) | Audit trail for Cora-orchestrated sweeps. |

> **Key principle:** `SESSION-HANDOFF.md` is the cross-machine source-of-truth (tracked). `next-session-start-here.md` is the local hot-start cache (gitignored). Every risk, blocker, or unresolved finding MUST appear in SESSION-HANDOFF.md (Step 8); next-session-start-here.md mirrors what's needed for the fastest next-session ramp.

---

## Session class — declare at WRAPUP open

Before running the steps below, name the session class. This determines which steps engage. Light sessions are a legitimate work shape the protocol explicitly supports — not a failure mode to apologize for.

| Class | Pattern | Steps engaged |
|---|---|---|
| **S — Substrate** | Story/epic dispatch; schema, pipeline-manifest, runtime, or test edits; content production | **All 13 steps.** Cora orchestrates Step 0. |
| **D — Docs / Tooling** | Markdown-only edits, lint refactors, knowledge-graph refresh, tool/plugin install, session-meta edits | **Minimum-viable: Steps 1, 7, 8, 12.** All others default-SKIP with one-line rationale in Step 8. |
| **P — Planning** | PRD, architecture, epics/stories authoring; party-mode rounds; retrospectives | **Steps 1, 2, 7, 8, 12.** Step 0 only if invariant files touched (pipeline-manifest, structural-walk, governance JSON, schemas). |

**Upgrade-only rule:** A session that opens as Class D or P but touches a substrate file mid-session UPGRADES to Class S. Once upgraded, downgrade is forbidden — the full ceremony engages. A session that opens as Class S stays as Class S.

**Class-drift self-check (Step 11):** WRAPUP verifies the declared class matches the actual diff. If the diff contains files outside the class envelope, upgrade and re-engage the missed steps before close.

### How session class is communicated

Three handoff points, in order:

1. **Forecast** — This WRAPUP's Step 7 writes the **expected class for the next session** at the top of `next-session-start-here.md` (one line: `**Expected class for next session:** <S|D|P> — <one-line reason tied to the immediate next action>`). The forecast is informed by the next session's stated immediate-next-action.
2. **Confirm at open** — At session open, the next session's agent reads the forecast and announces the operating class to the operator (e.g., "Opening as Class D per next-session-start-here.md forecast and your stated objective"). The operator confirms or overrides in plain text. If `next-session-start-here.md` is missing (fresh clone), the agent infers class from SESSION-HANDOFF.md's last session-close section header and the user's stated objective, then announces for confirmation the same way.
3. **Verify at close** — This WRAPUP's Step 11 runs the class-drift self-check; Step 8 records this session's **final class** (after any mid-session upgrade) in the SESSION-HANDOFF.md section header (one line: `**Final class:** <S|D|P>` with a note if the class drifted upward from the open).

---

## Steps

### 0. Pre-wrapup coherence (Class S only)

**Skip if Class D or P** (unless Class P touched invariant files).

For Class S sessions, ask Cora to run her Session-WRAPUP (SW) protocol:

- **0a Harmonization sweep:** `/harmonize` with scope `since-handoff` (default) or `full-repo` (on tripwire or operator request). Cora invokes Audra L1 deterministic + L2 agentic sweeps; report home at `reports/dev-coherence/YYYY-MM-DD-HHMM/`.
- **0b Pre-closure audit** for any story flipping to `done` this session. Cora invokes Audra's closure-artifact audit; evidence at `{report_home}/evidence/ca-<story_id>.md`.
- **0c Hot-start drafts:** Cora reads git log since the session-start anchor and drafts the hot-start pair (Steps 7 + 8) for operator review.

Outcomes for 0a/0b: remediate, queue for next session (record in Step 7), or proceed-with-acknowledged-gap (record in Step 8). L2 does not run until L1 is clean.

**For Class D/P sessions:** record the skip in Step 8 with one-line rationale (e.g., "Class D — docs-only window; no substrate/schema/workflow files touched"). Cora's tripwire still fires per her chronology — two consecutive skips force a full sweep on the next session, even Class D.

### 1. Run quality gate

Quality / hygiene checks scoped to what was touched:
- **System development:** linter + type checker (e.g., `ruff check .`, `lint-imports`).
- **Course content:** content-standards.yaml compliance + broken-link validation.
- **General fallback:** `git diff --check` + manual review.

Any L1 findings from Step 0 not remediated count as quality-gate failures — record explicitly as deferred in Steps 7 + 8 if proceeding.

### 2. Update BMAD planning and story artifacts

**Skip if no PRD / architecture / epic / story content edits this session.**

Update content artifacts in `_bmad-output/`:
- Planning: `_bmad-output/planning-artifacts/`
- Implementation: `_bmad-output/implementation-artifacts/` (excluding the two status YAMLs in Steps 3 + 4a)
- Brainstorming: `_bmad-output/brainstorming/`
- Content creation: staging status + review checklists

### 3. Update workflow status

**Skip if no phase / workflow transition this session.**

Update `_bmad-output/implementation-artifacts/bmm-workflow-status.yaml` only for significant transitions (story started/completed, phase advanced). Do not update for minor in-session progress.

### 4a. Update sprint status

**Skip if `sprint-status.yaml` was not edited this session.**

Otherwise: update Epic and story Kanban state, then run:
- `.venv\Scripts\python.exe -m pytest -q tests/test_sprint_status_yaml.py`

Do not close the session with a modified sprint ledger unless that targeted test passes or the failure is explicitly recorded as an unresolved blocker.

### 4b. Interaction testing

**Skip if no agent or supporting skill created or modified this session.**

For new or modified agents/skills, confirm an Interaction test exists per the project's interaction-test guide, or update the existing one if warranted.

### 5. Update project context and agent environment

**Skip if no rules / phase / architecture / MCP / API / shared-skill / tool-tier changes this session.**

- `docs/project-context.md` — update if rules, phase, or architecture changed.
- `docs/agent-environment.md` — update if MCP servers, API clients, shared skills, or tool tier classifications changed.

Both files are read at startup Step 1 — stale content means the next session starts with wrong assumptions.

### 6. Update course content state

**Skip if no content creation this session.**

- Move human-approved content from `course-content/staging/` to `course-content/courses/`.
- Update workflow status in `docs/workflow/`.
- Log platform integration results.

### 7. Finalize `next-session-start-here.md` (local hot-start cache)

For Class S: Cora drafted this in Step 0c — reconcile against anything added in Steps 1–6 and confirm final.

For Class D/P: author or update directly.

Required content:
- **Expected class for next session** (one line near the top): `**Expected class for next session:** <S|D|P> — <one-line reason tied to the immediate next action>`. Forecast only — the next session's agent confirms at open and the operator can override.
- **Immediate next action** (concrete, unambiguous — the first thing the next session should do).
- **Unresolved issues or blockers** affecting the next session — including every Audra finding deferred from Step 0a and every pre-closure gap acknowledged-but-not-remediated from Step 0b.
- Branch metadata: baseline branch + next working branch + exact checkout/create commands.
- Hot-start notes (key file paths, gotchas discovered this session).
- Course-content context (staging items pending review, workflow status, platform connection notes).

This file is gitignored — local-only. It accelerates the next session's ramp but is NOT the cross-machine source-of-truth.

### 8. Finalize `SESSION-HANDOFF.md` (cross-machine canonical record)

This file is the tracked record that survives across clones. Append a new session-close section (preserve prior sessions as archive). Required content:
- **Section header includes the final class** for this session (one line): `**Final class:** <S|D|P>` — with a note if the class drifted upward from the session-open declaration (e.g., `**Final class:** S (upgraded from D at HH:MM when <file> was touched)`).
- What was completed (summary, not play-by-play).
- What is next (broader than next-session-start-here; preserves multi-session context).
- Unresolved issues or risks (must cite Step 0a deferrals and Step 0b acknowledged gaps).
- Key lessons learned.
- Validation summary (Step 0 results, Step 1 quality-gate results, focused-suite results).
- Content creation summary.
- Artifact update checklist.
- For Class S: link to `reports/dev-coherence/YYYY-MM-DD-HHMM/`.

If `next-session-start-here.md` is missing on a fresh clone next session, the next session's agent can reconstruct it from this file's last section + recent commit messages.

### 9. Update guides, reuse patterns, structural walks, knowledge graph (consolidated)

**Skip if none of the following changed this session.**

Touch the smallest required set:
- **Guides** (`docs/user-guide.md` / `admin-guide.md` / `dev-guide.md`) — update if the session changed something they document (new skill, new API client, new workflow, architecture change).
- **Reuse + pattern artifacts** — `design-patterns.md`, `service-catalog.md`, `course-content/_templates/`, `resources/tool-inventory/`, `reuse-first-protocol.md`.
- **Structural-walk definitions** — `state/config/structural-walk/standard.yaml` + `motion.yaml` + `docs/structural-walk.md`, only if canonical workflow / gate names / artifact contracts / bundle assets / walk-covered families changed.
- **Knowledge graph + ONBOARDING.md** — if substantive substrate changes landed (≥10 files in app/scripts/skills/ OR pipeline-manifest/schema/manifest changes OR Epic close), recommend the operator regenerate `.understand-anything/knowledge-graph.json` via `/understand` and re-emit `docs/ONBOARDING.md` via `/understand-anything:understand-onboard`. Staleness anchor: `.understand-anything/meta.json::gitCommitHash` vs HEAD. **Incremental-update gotcha:** the merge step's filename regex only matches `batch-<N>.json` / `batch-<N>-part-<K>.json`, so the carried-over `batch-existing.json` for unchanged files is silently dropped (every unchanged-file node lost) — rename it to a numeric batch (e.g. `batch-9000.json`) before merging, or run `/understand --full`.

### 10. Clean stale files + dirty-worktree reconciliation

**Skip cleanup if workspace already clean.**

Remove or archive stale session tracking files, orphaned artifacts, deprecated references.

**Worktree reconciliation (mandatory):** run `git status --short`. Partition into:
- Session-owned changes to include in closeout.
- Collaborative in-scope changes from the user or other active agents during the same session.
- Pre-existing unrelated changes to leave untouched.

Rules: do not stage unrelated modifications; do not exclude same-session collaborative changes just because another agent authored them; do not claim ownership of unrelated files in the hot-start docs; if unrelated changes remain after the session commit, list them explicitly as ambient worktree state.

### 11. Verify artifact completeness + class-drift self-check

Cross-check that every artifact in Step 8's checklist is current. Minimum verification: story artifact, sprint-status, workflow-status, project-context, next-session-start-here.

**Class-drift self-check:** does the declared session class still match the actual diff?
- Declared Class D and `git diff` shows app/scripts/skills/ Python edits → upgrade to Class S; re-engage missed steps.
- Declared Class P and any non-planning-artifact substrate file was touched → upgrade to Class S.
- Record any drift + re-engagement in Step 8.

**Worktree hygiene:** run `git worktree list`. Remove temporary investigation worktrees (`git worktree remove <path>`) and prune stale metadata (`git worktree prune --verbose`). If keeping multiple worktrees intentionally, record why in Step 7.

Verify branch metadata in `next-session-start-here.md` matches the intended post-closeout Git state; verify startup commands are executable as written.

### 12. Git closeout — push MANDATORY

**Working-branch push at session-WRAPUP is MANDATORY per CLAUDE.md push-cadence policy (ratified 2026-05-05).** Do NOT defer. The session ends with `origin/<working-branch>` at the local HEAD.

For mid-session triggers (≥ 2h elapsed since last push, ≥ 5 commits ahead, safety-checkpoint commit, operator stepping away), see CLAUDE.md "Push cadence policy" — proactive pushes are also required.

Default flow:
1. Finalize `next-session-start-here.md` branch metadata for expected post-closeout state.
2. Stage intended changes (`git add ...`).
3. Commit with clear summary message.
4. Resolve remotes by role: source remote `upstream` (read-only feed), publish remote `origin` (writable). Verify with `git remote -v`.
5. **`git push origin <working-branch>`** — mandatory safety gate. If a pre-push hook fails, investigate and fix; do not bypass with `--no-verify`.
6. **Optional** (only if team's workflow merges to master at session-close): checkout master, fast-forward-merge from `upstream/master`, merge the working branch, push master to `origin`. Skip for scoped-work branches (e.g., trial branches).
7. **Optional** (only if creating the next working branch this WRAPUP): create from updated master, push with upstream tracking.
8. Re-run `git worktree list` — confirm only intended worktrees registered.
9. Re-verify `next-session-start-here.md` branch metadata matches reality. If not, make a small docs-only follow-up commit + push.

If your team intentionally skips the master-merge for a session, explicitly record the exception in Steps 7 + 8. **The working-branch push (step 5) is still mandatory** — only the master-merge step is skipped.

### 13. Optional: session close

Morale summary, party-mode wrap-up, or any other team ritual.
