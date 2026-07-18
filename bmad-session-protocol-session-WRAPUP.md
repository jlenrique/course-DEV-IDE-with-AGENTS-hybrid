# BMAD v6 Session Protocol: End-of-Session (Shutdown)

Companion to `bmad-session-protocol-session-START.md`. Together these two files guarantee reliable context transfer between sessions.

## Context transfer contract

The startup protocol **reads** certain files; the wrapup protocol **writes** them. Every read must have a corresponding write, or context is lost.

| File | Startup reads | Wrapup writes | Role & SSOT status |
|------|:---:|:---:|------|
| `SESSION-HANDOFF.md` | Always (canonical) | Step 8 (+ roll-down) | **Authored SSOT — chronology.** Cross-machine, tracked. Current arc + 1 prior stay hot; older sections → `SESSION-HANDOFF.history.md`. |
| `docs/STATE-OF-THE-APP.md` | §0 guardrail + on-demand | Step 9 | **Authored SSOT — product truth.** Current + 1 prior banners stay hot; older → `STATE-OF-THE-APP.history.md`. The FRAMING PRINCIPLE guardrail banner stays permanently (START §0 references it). |
| `sprint-status.yaml` | Step 4 | Step 4a | **Authored SSOT — Kanban.** Value-reconcile only (line-regex + `tripwire_events` parsers — never structurally reformat); fully-done epic blocks may archive to `sprint-status.history.md`. |
| `_bmad-output/planning-artifacts/deferred-inventory.md` | Step 4 (governance) | governance events | **Authored register — governance.** Closed entries roll to its `## Closed Entries — Archived` section at retrospective / multi-slab milestones (its own hygiene rule). |
| `bmm-workflow-status.yaml` | Step 4 | Step 3 | BMAD phase (structured YAML — zero parsers). Append-only comment history → `bmm-workflow-status.history.md`; keep title + newest-1-prior entry. |
| `next-session-start-here.md` | If present (per-clone cache) | Step 7 = **GENERATED** | **Generated view (fail-loud)** — `scripts/utilities/generate_next_session.py`. Gitignored. Falls back to SESSION-HANDOFF if generation fails; do not hand-maintain as source of truth. |
| `docs/project-context.md` | Step 1 | Step 5 = **GENERATED** | **Generated view (thin header)** — `scripts/utilities/generate_project_context.py`. The base doc below the `<!-- BASE-DOC … -->` marker is hand-authored + preserved. Addendum history → `project-context.history.md` (generator-fed, not manual). Glob-loaded as a persistent-fact by ~59 skills — NEVER move/rename it, never create a second `project-context.md`. |
| `docs/ONBOARDING.md` | Once per fresh agent context | Step 9 if regenerated | **Architectural mental model** — knowledge-graph-derived structural ramp. |
| `docs/agent-environment.md` | Step 1 | Step 5 | MCP / API / tool / skill inventory for agents. |
| Guides (user/admin/dev/specialist) | Step 4 on-demand | Step 9 | **Living docs — evolve WITH the app.** Reviewed for currency every Class S session; MUST update when a change (especially a bug / live-run insight) alters how the app is used, operated, developed, or how agents/services/functions integrate. |
| `reports/dev-coherence/<ts>/` | — | Step 0 (Class S only) | Audit trail for Cora-orchestrated sweeps. |

> **Key principle:** `SESSION-HANDOFF.md` is the cross-machine source-of-truth (tracked). Every risk, blocker, or unresolved finding MUST appear in SESSION-HANDOFF.md (Step 8); the generated `next-session-start-here.md` mirrors what's needed for the fastest next-session ramp.

### Status-surface SSOT & retention contract (established 2026-07-17)

The status surfaces are **three authored SSOTs + one governance register + generated/trimmed views** — one authority per question, everyone else reads. Do not re-accrete history into the hot files. (Full rationale + machine-consumer constraints: [`spec-status-surface-consolidation.md`](_bmad-output/implementation-artifacts/spec-status-surface-consolidation.md).)

- **Authored SSOTs (hand-maintained):** `sprint-status.yaml` = Kanban · `SESSION-HANDOFF.md` = chronology · `docs/STATE-OF-THE-APP.md` = product truth. Plus `deferred-inventory.md` = governance register.
- **Generated views (fail-loud, never the source of truth):** `next-session-start-here.md` and `docs/project-context.md`. Regenerate them (Steps 7, 5); if a generator fails it exits non-zero and does NOT overwrite — fall back to the authored SSOT.
- **Retention = current arc + 1 prior stays hot.** Older content rolls to a dated `*.history.md` sibling via the **arc-close roll-down** (Step 8). Each trimmed hot file carries a `> History archived to <sibling>` pointer. Archive == move, never delete.
- **Never structurally reformat `sprint-status.yaml`** — three consumers are line-regex (2-space indent, `epic-*` prefixes, `#`-comment stripping) and `tripwire_events` is a written+hashed ledger. Value edits + whole-block moves only.

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

Update `_bmad-output/implementation-artifacts/bmm-workflow-status.yaml` only for significant transitions (story started/completed, phase advanced). Do not update for minor in-session progress. Edit only the **structured YAML** and, if you prepend a dated `#` comment entry, keep only the title + newest-1-prior entry at the top — the older comment history lives in `bmm-workflow-status.history.md` (roll any demoted entry down there, do not let the blob re-accrete).

### 4a. Update sprint status

**Canonical Kanban ledger:** `_bmad-output/implementation-artifacts/sprint-status.yaml` is the single most responsible doc for tracking progression through BMAD workflows (epic/story status). Wrapup must keep it honest.

**Skip only if no epic/story Kanban state changed this session** (no story advanced, completed, blocked, deferred, or newly filed; no epic status change). Do **not** skip merely because the file was left untouched during the session — if BMAD work progressed and the ledger was not updated yet, update it now.

Otherwise (or when catching up a missed mid-session edit):
1. Update Epic and story Kanban state in `sprint-status.yaml` to match what actually closed or advanced this session.
2. Run: `.venv\Scripts\python.exe -m pytest -q tests/test_sprint_status_yaml.py`

Do not close the session with a modified sprint ledger unless that targeted test passes or the failure is explicitly recorded as an unresolved blocker. For Class S sessions that closed stories, prefer updating `sprint-status.yaml` before `next-session-start-here.md` (Step 7) so the hot-start cache cannot outrun the Kanban ledger.

### 4b. Interaction testing

**Skip if no agent or supporting skill created or modified this session.**

For new or modified agents/skills, confirm an Interaction test exists per the project's interaction-test guide, or update the existing one if warranted.

### 5. Update project context and agent environment

**Skip if no rules / phase / architecture / MCP / API / shared-skill / tool-tier changes this session.**

- `docs/project-context.md` — **GENERATED view.** Regenerate with `.venv/Scripts/python.exe scripts/utilities/generate_project_context.py` (rewrites the thin current-state header above the `<!-- BASE-DOC … -->` marker from the latest SESSION-HANDOFF section + SOTA §11.1). **Run this AFTER Step 8** — the header sources from the newest SESSION-HANDOFF section, so regenerate once that section exists (same ordering as the Step 7 next-session regen). Edit the file **by hand only** to change the hand-authored base doc *below* the marker (genuine rules / architecture / tool-universe changes). Never move the file — ~59 skills glob-load it.
- `docs/agent-environment.md` — update if MCP servers, API clients, shared skills, or tool tier classifications changed.
- **Cursor dual-agent surfaces (when touched):** if `.cursor/rules/bmad-dual-agent-families.mdc`, `.cursor/agents/*.md`, or the Family A vs B note in `AGENTS.md` changed, record that in the handoff so the next Cursor session does not rediscover the dual-path cold-start. Custom agents remain `skills/bmad-agent-*` + sanctums (not installer `.cursor/skills/` mirrors).

Both files are read at startup Step 1 — stale content means the next session starts with wrong assumptions.

### 6. Update course content state

**Skip if no content creation this session.**

- Move human-approved content from `course-content/staging/` to `course-content/courses/`.
- Update workflow status in `docs/workflow/`.
- Log platform integration results.

### 7. Finalize `next-session-start-here.md` (GENERATED local hot-start cache)

**This is a generated view.** After Step 8's SESSION-HANDOFF section is written, regenerate it: `.venv/Scripts/python.exe scripts/utilities/generate_next_session.py`. It lifts the Immediate-Next-Action / Key-Risks content from the latest SESSION-HANDOFF section + branch/HEAD + deferred counts. If it exits non-zero (missing/malformed latest handoff section), fix the handoff section — do not hand-write the cache as a workaround.

Then **hand-set the one thing the generator cannot infer** — the `**Expected class for next session:**` forecast line (tied to the immediate next action) — and spot-check the output. The required content below is the validation checklist the generated file must satisfy:
- **Expected class for next session** (one line near the top): `**Expected class for next session:** <S|D|P> — <one-line reason tied to the immediate next action>`. Forecast only — the next session's agent confirms at open and the operator can override.
- **Immediate next action** (concrete, unambiguous — the first thing the next session should do).
- **Unresolved issues or blockers** affecting the next session — including every Audra finding deferred from Step 0a and every pre-closure gap acknowledged-but-not-remediated from Step 0b.
- Branch metadata: baseline branch + next working branch + exact checkout/create commands.
- Hot-start notes (key file paths, gotchas discovered this session).
- Course-content context (staging items pending review, workflow status, platform connection notes).

This file is gitignored — local-only. It accelerates the next session's ramp but is NOT the cross-machine source-of-truth.

### 8. Finalize `SESSION-HANDOFF.md` (cross-machine canonical record)

This file is the tracked record that survives across clones. **Prepend** a new session-close section at the top (newest-first). Required content:
- **Section header includes the final class** for this session (one line): `**Final class:** <S|D|P>` — with a note if the class drifted upward from the session-open declaration (e.g., `**Final class:** S (upgraded from D at HH:MM when <file> was touched)`).
- What was completed (summary, not play-by-play).
- What is next (broader than next-session-start-here; preserves multi-session context).
- Unresolved issues or risks (must cite Step 0a deferrals and Step 0b acknowledged gaps).
- Key lessons learned.
- Validation summary (Step 0 results, Step 1 quality-gate results, focused-suite results).
- Content creation summary.
- Artifact update checklist.
- For Class S: link to `reports/dev-coherence/YYYY-MM-DD-HHMM/`.

If `next-session-start-here.md` is missing on a fresh clone next session, the next session's agent can reconstruct it from this file's latest section + recent commit messages.

**Arc-close roll-down (retention discipline).** At an **arc/epic close** — not every session — roll cold history out of the hot SSOTs so they stay small (the "current arc + 1 prior stays hot" rule from the retention contract above). A practical boundary for "current arc": the sections since the **last epic/retrospective close marker** (plus the one immediately prior) stay hot; everything older rolls down.
- `SESSION-HANDOFF.md` → move session sections older than the current arc + 1 prior to the TOP of `SESSION-HANDOFF.history.md`; leave a `> History archived to SESSION-HANDOFF.history.md` pointer in the hot file.
- `docs/STATE-OF-THE-APP.md` → move superseded top-banners + §11.1/§11.5 you-are-here snapshots older than current + 1 prior to `STATE-OF-THE-APP.history.md` (keep the FRAMING PRINCIPLE banner permanently).
- `bmm-workflow-status.yaml` → demote any comment entry beyond newest-1-prior to `bmm-workflow-status.history.md`.
- `docs/project-context.md` → its dated addendum history is demoted to `project-context.history.md` **automatically by `generate_project_context.py`** (Step 5), NOT by manual roll-down — the generator archives everything above the `<!-- BASE-DOC -->` marker. Do not hand-roll it.
- `deferred-inventory.md` closed-entry sweep and `sprint-status.yaml` done-block archival happen on their own governance cadence (retrospective milestone; value-only reconcile), not as a routine roll-down.

Do the roll-down **only** at arc close; a per-session roll-down would churn the files needlessly.

### 9. Update guides, reuse patterns, structural walks, knowledge graph (consolidated)

**Skip if none of the following changed this session.**

Touch the smallest required set:
- **Guides — living docs that evolve WITH the app.** Review them for currency **every Class S session** (not just "when convenient") and update the smallest required set. The four guide surfaces:
  - `docs/user-guide.md` — operator-facing behavior/expectations of the product surface.
  - `docs/admin-guide.md` — operational/runtime knobs and how to run things (e.g. live toggles like `MARCUS_G0_DISPATCH_LIVE=1`, governed live-run posture).
  - `docs/dev-guide.md` + the `docs/dev-guide/` tree — builder mechanics (new skill, API client, workflow, architecture change).
  - **Specialist guide** — `docs/dev-guide/how-to-add-a-specialist.md` (+ the `specialist-*.md` family) — how a new specialist is correctly integrated.
  - **MANDATORY trigger (operator directive 2026-07-15):** when a change — **especially a bug or live-run defect** — reveals how future **agents, services, or functions must be integrated** into the app (dispatch/state-threading contracts, required-output validation, authority / source-of-truth rules, a new runtime knob), update the relevant guide in THIS closeout so the next builder does not rediscover it the hard way. Fold the guide update into the same commit as the fix.
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

Cross-check that every artifact in Step 8's checklist is current. Minimum verification: story artifact, **`sprint-status.yaml` (must reflect every epic/story status change from this session — re-run Step 4a if it does not)**, workflow-status, project-context, next-session-start-here.

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
