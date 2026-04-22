# BMAD v6 Session Protocol: End-of-Session (Shutdown)

Companion to `bmad-session-protocol-session-START.md`. Together these two files guarantee reliable context transfer between sessions.

### Context transfer contract

The startup protocol **reads** certain files; the wrapup protocol **writes** them. Every read must have a corresponding write, or context is lost.

| File | Startup reads | Wrapup writes | Role |
|------|:---:|:---:|------|
| `next-session-start-here.md` | Step 1 | Draft 0c, finalize 7 | **Forward-looking hot-start** — next actions, branch, risks, gotchas |
| `docs/project-context.md` | Step 1 | Step 5 | Current state, key decisions, architecture summary |
| `docs/agent-environment.md` | Step 1 | Step 5 | MCP/API/tool/skill inventory for agents |
| `bmm-workflow-status.yaml` | Step 5 | Step 3 | BMAD phase and workflow transitions |
| `sprint-status.yaml` | Step 5 | Step 4a | Epic/story Kanban state |
| `SESSION-HANDOFF.md` | — | Draft 0c, finalize 8 | **Backward-looking record** — lessons, decisions, validation (permanent archive; startup does not read) |
| Guides (user/admin/dev) | Step 5 on-demand | Step 9a | Large stable docs — updated only when content changes |
| `reports/dev-coherence/<ts>/` | — | Step 0a | **Audit trail** — Audra L1/L2 evidence files; linked from SESSION-HANDOFF for permanent reference |

> **Key principle:** `next-session-start-here.md` is the sole ramp-up document for the next session. Any risk, blocker, or unresolved issue from the current session — including every deferred Audra finding from Step 0a and every pre-closure gap acknowledged-but-not-remediated in Step 0b — MUST be surfaced there (Step 7), not only in SESSION-HANDOFF. SESSION-HANDOFF is the permanent record; next-session-start-here is the action trigger.

---

## Steps

Execute these steps in order before ending a session.

### 0. Pre-wrapup coherence and closure (Cora-orchestrated)

Run this block **before** the quality gate and artifact updates so that Steps 1-13 operate against an already-harmonized, already-audited repo. Cora orchestrates; Audra does the deterministic judgment. All findings are warn-mode — nothing blocks, but unremediated findings must be surfaced in Step 7.

**Scope — session-work change window.** Unless a tripwire escalates (see below), Step 0a runs against the union of:
- Committed changes since the session-start anchor: `git diff --name-only <session-start-anchor>..HEAD`
- Uncommitted modifications: `git diff --name-only HEAD`
- Untracked files: `git ls-files --others --exclude-standard`

The session-start anchor is the commit that last modified `SESSION-HANDOFF.md`, resolved via `git log -1 --format=%H -- SESSION-HANDOFF.md`. It marks the last moment the prior session certified the repo as closed-out. Whole-repo invariant checks (parameter-directory <-> schema lockstep, gate-contract lockstep, lane-matrix coverage) run every time regardless of change window.

**Mode — soft-conditional.** Each sub-step below can be skipped when its precondition is not met (e.g., no doc changes in the window, no stories flipping to `done`). When a sub-step is skipped, Cora appends to her `chronology.md`: `YYYY-MM-DD HH:MM — Step 0<x> skipped: <reason>`. This preserves the audit trail.

**Tripwire — drift escalation.** Before running Step 0a, Cora reads her `chronology.md` and checks the most recent wrapup entry. If that wrapup recorded a skipped 0a, the current session's 0a auto-promotes to **full-repo scope** rather than the default change-window scope. One skip is absorbed by the next session; two consecutive skips force a full sweep. This closes the drift-accumulation gap that soft-conditional would otherwise open.

#### 0a. Harmonization sweep

Ask Cora to run `/harmonize` with scope `since-handoff` (default) or `full-repo` (if the tripwire fires, or on operator request). Cora creates a report home at `reports/dev-coherence/YYYY-MM-DD-HHMM/`, invokes Audra's L1 deterministic sweep against the resolved scope, and — if L1 exits clean — invokes Audra's L2 agentic sweep on the changed-docs subset.

Outcomes:
- **L1 + L2 both clean** -> proceed to Step 0b.
- **L1 findings** -> Cora relays findings to the operator with the choice: remediate now, queue for next session (findings recorded as outstanding in Step 7), or consciously defer (note recorded in Step 8). L2 does not run until L1 is clean.
- **L1 clean, L2 findings** -> same three-choice prompt; if remediation exceeds paragraph scope, Cora offers to route to Paige.

Skip condition: change window is empty and no whole-repo invariant has a pending known-drift flag. Log the skip reason.

#### 0b. Pre-closure audit for stories flipping to `done`

For each story the operator intends to flip from an in-progress state to `done` in `sprint-status.yaml` this session, ask Cora to run `/preclosure {story_id}`. Cora invokes Audra's closure-artifact audit (AC satisfied, automated verification logged, layered review present, remediated review record present) and writes evidence to `{report_home}/evidence/ca-<story_id>.md`.

Outcomes:
- **All four artifacts present** -> operator proceeds with the flip in Step 4a.
- **Any gap** -> Cora relays in warn-mode with the standard three-choice prompt (remediate, defer with note, flip anyway with explicit risk acknowledgement). Cora never writes `sprint-status.yaml` herself — the operator owns that write in Step 4a.

Skip condition: no stories are being flipped to `done` this session. Log the skip.

#### 0c. Cora SW — draft the hot-start pair

Ask Cora to run her Session-WRAPUP (SW) protocol. Cora reads git log since the session-start anchor, drafts `SESSION-HANDOFF.md` and `next-session-start-here.md` (including all unremediated Audra findings from 0a/0b as outstanding items), shows both drafts to the operator, and writes them on approval. Cora also appends a wrapup entry to her own `chronology.md` and updates her `index.md`.

Note: the files Cora writes here are *drafts*. Steps 1-9 may add artifacts (test results, guide edits, content-state changes) that need to flow into the hot-start pair. Steps 7 and 8 finalize these drafts against the post-closeout state.

Skip condition: none. Step 0c runs every session. If the operator requests a lighter wrapup, Cora writes a minimal `SESSION-HANDOFF.md` and marks `next-session-start-here.md` as "operator-deferred," per Cora's own SW protocol forcing-function clause.

### 1. Run quality gate

Run the project's quality/hygiene checks:
- **System development**: linter + type checker commands (e.g., `ruff check .`, `npm run lint`)
- **Course content**: content-standards.yaml compliance check, broken link validation
- **General**: `git diff --check` + manual review if no automation exists

Any L1 findings from Step 0a that haven't been remediated count as quality-gate failures for this purpose — the gate is not bypassable by ignoring Audra. Fix findings before proceeding, or record them explicitly as deferred in Steps 7 and 8. If no quality mechanism exists, note this as a gap to address in a future story.

### 2. Update BMAD planning and story artifacts

Update canonical BMAD artifacts in `_bmad-output/` to reflect the session's work. This step covers **content artifacts only** — status YAMLs are handled separately in Steps 3 and 4a.

- **Planning phase**: PRD, architecture, epics/stories files in `_bmad-output/planning-artifacts/`
- **Implementation phase**: story artifacts and task checklists in `_bmad-output/implementation-artifacts/` (excluding the two status YAMLs)
- **Brainstorming phase**: brainstorming session files in `_bmad-output/brainstorming/`
- **Content creation**: staging content status, review checklist updates

### 3. Update workflow status

Update `_bmad-output/implementation-artifacts/bmm-workflow-status.yaml` only for significant workflow phase changes or status transitions (e.g., story started, story completed, phase advanced). Do not update for minor in-session progress.

### 4a. Update sprint status

If `sprint-status.yaml` was edited this session, run:
- `.venv\Scripts\python.exe -m pytest -q tests/test_sprint_status_yaml.py`

Do not close the session with a modified sprint ledger unless that targeted regression check passes or the failure is explicitly recorded as an unresolved blocker.

Update `_bmad-output/implementation-artifacts/sprint-status.yaml` for epic and story Kanban state changes (e.g., `in-progress` -> `review` -> `done`).

### 4b. Interaction Testing: 
Confirm presence, if appropriate at this phase of the project work, of an 'Interaction test' for a newly created agent.  The test should be modeled on the interaction test guide now available in the project. If an agent or supporting skill has been modified, ensure the corresponding interaction test is updated, if warranted.

### 5. Update project context and agent environment

Update `docs/project-context.md` only if rules, phase, or architecture changed this session. Do not update for routine implementation progress.

Update `docs/agent-environment.md` if any of the following changed this session:
- MCP servers added, removed, or reconfigured
- API clients added or auth patterns changed
- Shared skills added, renamed, or retired
- Tool tier classifications changed in the tool inventory

Both files are read at startup Step 1 — stale content here means the next session starts with wrong assumptions.

### 6. Update course content state

**For content creation sessions**:
- Move completed content from `course-content/staging/` to `course-content/courses/` if human-approved
- Update content workflow status in `docs/workflow/` (and `workflows/` if your project later adds that directory)
- Log any platform integration results or issues

*Skip if no content creation occurred this session.*

### 7. Finalize next-session-start-here

Cora drafted `next-session-start-here.md` in Step 0c. In this step, reconcile the draft against anything that changed during Steps 1-6, and confirm the file is final. Specifically verify the draft includes:

- **Immediate next action** (concrete, unambiguous — the first thing the next session should do)
- **Unresolved issues or blockers** from this session that affect the next session's work (this MUST include every L1 or L2 finding from Step 0a that was deferred rather than remediated, and every pre-closure gap from Step 0b where the operator proceeded with the flip anyway — do not bury these only in SESSION-HANDOFF)
- Branch metadata and startup commands:
  - `Repository baseline branch` after closeout (commonly `master`)
  - `Next working branch` for implementation in the next session
  - Exact checkout/create commands for the next working branch
- Hot-start notes (key file paths, API references, gotchas discovered this session)
- **Course content context**: staging items pending review, workflow status, platform connection notes

If anything added in Steps 1-6 isn't reflected in Cora's draft, ask Cora to patch the draft; don't rewrite it yourself. This file is action-oriented and forward-looking. Its purpose is to give the next session's agent the fastest possible ramp-up to productive work. It is the **sole ramp-up document** — the next session reads this file first and may not read SESSION-HANDOFF at all.

### 8. Finalize session handoff

Cora drafted `SESSION-HANDOFF.md` in Step 0c. In this step, reconcile and confirm final. Verify the draft includes:

- What was completed this session (summary, not play-by-play)
- What is next (broader context than next-session-start-here)
- Unresolved issues or risks (must cite Audra findings deferred from Step 0a and any pre-closure gaps acknowledged-but-not-remediated from Step 0b)
- Key lessons learned
- Validation summary (what was tested, how, results — include Step 0a sweep results and Step 1 quality-gate results)
- **Content creation summary**: what content was created/reviewed, platform status, human review queue
- Artifact update checklist (which canonical files were updated)
- Link to the Step 0a report home under `reports/dev-coherence/YYYY-MM-DD-HHMM/`

This file is record-oriented and backward-looking. Its purpose is to preserve context, decisions, and lessons that would otherwise be lost between sessions. The linked dev-coherence report home is the permanent audit trail for this session's coherence posture.

### 9a. Update guides (if affected)

Update these only if the session changed something they document (new skill, new API client, new workflow, architecture change). Do not update for routine content creation.

- `docs/user-guide.md` — user-facing workflows, Marcus interactions, content organization
- `docs/admin-guide.md` — credentials, MCP config, environment setup, operational procedures
- `docs/dev-guide.md` — architecture, extension recipes, testing, coding standards

These are startup "read on demand" docs (Step 5). Stale guide content wastes context window when the next session loads them.

### 9b. Review reuse and pattern artifacts

If the project maintains reuse, pattern, or service tracking files, review and update them. Check for:
- Design patterns discovered or refined -> update `design-patterns.md`
- Services that should be cataloged -> update `service-catalog.md`
- **Course content patterns**: content templates, workflow improvements -> update `course-content/_templates/`
- **Tool integration patterns**: new MCP/API integrations -> update `resources/tool-inventory/`
- Reuse opportunities for future stories -> update `reuse-first-protocol.md`

*Skip if none of these files exist or no new patterns/services emerged.*

### 9c. Update structural-walk definitions if control structure changed

If the session changed any of the following, update the structural-walk configuration before shutdown:
- canonical workflow or control docs
- gate names or checkpoint sequencing
- required artifact contracts
- expected bundle assets or validation targets
- workflow families covered by the walk manifests

Touch the smallest required set:
- `state/config/structural-walk/standard.yaml`
- `state/config/structural-walk/motion.yaml`
- `docs/structural-walk.md`

Do not update the walks for routine content or code changes that do not alter what the walks are expected to validate.

### 10. Clean up stale files

Remove or archive any stale session tracking files, orphaned artifacts, or deprecated references that are no longer canonical. This prevents context pollution in future sessions.

**Course content cleanup**: Remove outdated staging content, broken workflow references, stale tool configurations.

*Skip if the workspace is already clean.*

### 10a. Dirty-worktree reconciliation (mandatory)

Before Git closeout, run:
- `git status --short`

Partition the worktree into:
- **Session-owned changes** to include in closeout
- **Collaborative in-scope changes** produced during the same session by the user or other active agents/browser contexts
- **Pre-existing unrelated changes** to leave untouched

Rules:
- Do not stage unrelated modified or untracked files into the session commit.
- Do not exclude same-session collaborative changes merely because they were authored by another active agent or browser context working on the same objective.
- Do not claim ownership of unrelated files in `next-session-start-here.md` or `SESSION-HANDOFF.md`.
- If unrelated changes remain after the session commit, list them explicitly as ambient worktree state so the next session does not confuse them with the just-closed work.

### 11. Verify artifact completeness

Cross-check that every artifact listed in `SESSION-HANDOFF.md` (artifact update checklist) is confirmed current. 

**Minimum verification**: story artifact, sprint-status, workflow-status, project-context, and next-session-start-here.

Also verify branch metadata consistency:
- `next-session-start-here.md` branch instructions match the intended post-closeout Git state
- Startup commands in `next-session-start-here.md` are executable as written

**Course content verification**: content-standards compliance, human review queue status, platform connectivity.

### 11a. Worktree hygiene closeout (mandatory)

Before Git closeout, run:
- `git worktree list`

If a temporary merge/investigation worktree was created during the session, remove it now:
- `git worktree remove <path-to-temporary-worktree>`

If a temporary worktree directory was deleted manually outside Git, clean stale metadata:
- `git worktree prune --verbose`

If you intentionally keep more than one worktree, record why and the exact paths in `next-session-start-here.md` Step 7.

### 12. Git closeout (default)

Default end-of-session flow is:
1. Finalize `next-session-start-here.md` branch metadata for expected post-closeout state (baseline + next working branch + startup commands)
2. Stage all intended changes (`git add ...`)
3. Commit session work on the working branch with a clear summary message
4. Resolve remotes by role before updating `master`:
   - **Source remote** (read-only upstream feed): prefer `upstream`; fallback `origin` only when `upstream` does not exist
   - **Publish remote** (where this repo pushes): prefer `origin`
   - Recommended check:
     - `git remote -v`
     - Confirm source remote is fetch-capable
     - Confirm publish remote is the intended writable destination for this repo
5. Checkout and update `master` from the **source remote** (`<source-remote>/master`)
6. Merge the working branch into `master`
7. Push `master` to the **publish remote** (`<publish-remote>`)
8. Create the **next working branch** from updated `master` (for the next session), and push with upstream
9. Re-run `git worktree list` and verify only intended worktrees remain registered
10. Re-verify `next-session-start-here.md` branch metadata matches reality. If it does not, make a small docs-only follow-up commit and push.

Example (hybrid clone topology):
- Source remote: `upstream`
- Publish remote: `origin`
- Commands:
  - `git fetch upstream`
  - `git switch master`
  - `git merge --ff-only upstream/master`
  - `git merge <working-branch>`
  - `git push origin master`

Maintenance note for one-way clones:
- After each pull from the primary project, quickly re-check this section still maps source=`upstream` and publish=`origin`.
- If upstream edits this protocol block, keep the remote-role model above when resolving merge conflicts.

If your team intentionally skips merge-to-master for a session, explicitly record that exception and the exact resume branch in both `next-session-start-here.md` and `SESSION-HANDOFF.md`.

Do not perform the merge-to-master flow when any of the following are true:
- unrelated pre-existing worktree changes remain
- the session produced a scoped checkpoint that should stay isolated on the working branch
- branch metadata or startup commands have not yet been reconciled

In those cases, commit the working branch only, record the exception, and leave the repo in a truthful resume state.

**Course content commit examples**:
- "Add lesson 3 presentation slides to staging with lesson plan scaffold"
- "Implement Canvas quiz API integration with working example"
- "Complete brainstorming Phase 2: clustered requirements into epic boundaries"

### 13. Optional: session close

Morale summary, party mode wrap-up, or any other team ritual.
