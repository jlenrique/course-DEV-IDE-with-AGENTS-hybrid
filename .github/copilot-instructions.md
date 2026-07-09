# BMAD sprint governance (VS Code / GitHub Copilot)

This file is the **VS Code equivalent** of always-on AI rules: it mirrors [`.cursor/rules/bmad-sprint-governance.mdc`](../.cursor/rules/bmad-sprint-governance.mdc) (Cursor) so GitHub Copilot Chat in VS Code picks up the same charter. VS Code loads [`.github/copilot-instructions.md`](https://code.visualstudio.com/docs/copilot/customization/custom-instructions) automatically for every chat in the workspace. See also [`AGENTS.md`](../AGENTS.md) and [`CLAUDE.md`](../CLAUDE.md).

**Solo operator — no formal PR framework:** one human committer; default closeout is branch → local verify → push (merge when asked). Do not open PRs or treat PR-gated CI as required unless the operator explicitly asks. Details: [`AGENTS.md`](../AGENTS.md) §Solo operator.

## ⛔ Critical design guardrail — the goal is the Marcus-SPOC PRODUCT, not the proofing vehicle (operator 2026-06-30)

The only product goal is the **Marcus-SPOC runtime orchestrator** (the operator-facing surface that drives a real *instance of the APP and its production runtime*). The BMAD-persona Marcus's **"concierge"/exploratory/trial/proofing runs are off-the-books discovery vehicles, NOT a design target** — they may surface real production-codebase defects, but **do NOT design, shape, or add to the production codebase merely to make those runs work.** Fix what a proofing run finds only because it improves the SPOC product, never to "make the concierge run pass." Full statement: [`CLAUDE.md`](../CLAUDE.md) §CRITICAL DESIGN GUARDRAIL + [`docs/STATE-OF-THE-APP.md`](../docs/STATE-OF-THE-APP.md) FRAMING PRINCIPLE.

## Charter

1. **Epics and stories** must be produced with BMAD workflows only (for example `bmad-create-epics-and-stories`, `bmad-create-story`, `bmad-create-prd` / architecture / UX chains as appropriate, or `bmad-quick-dev` when that is the right path). If unsure which variant to use, read **`bmad-help`**, run **`bmad --help`**, or convene **`bmad-party-mode`** and ask the team to recommend full planning vs quick-dev vs another module skill.
2. **Green-lighting** and **initial review** of completed work must use **`bmad-party-mode`** (multi-agent roundtable). Do not substitute a single improvised persona for those gates.
3. Before marking any story **done**, you must run **`bmad-code-review`** on the changes in scope (or honor the user’s explicit “run code review” / equivalent invocation).
4. Proceed by **BMAD team consensus** across the active workflow steps and party-mode rounds; keep a short written record of agreed decisions when it affects scope or quality.
5. **Do not** stop the run except when **(a)** every in-scope story is **done** according to `_bmad-output/implementation-artifacts/sprint-status.yaml`, or **(b)** **impasse**: after documented party-mode rounds the team still cannot agree on a path—then pause and escalate to the human.
6. **Impasse** means: relevant voices in party mode have had at least one full round, the disagreement is stated explicitly, and no consensus option remains acceptable to all; it does not mean routine questions or a single agent’s uncertainty.

Related skills: `bmad-help`, `bmad-party-mode`, `bmad-code-review`, `bmad-quick-dev`, `bmad-sprint-run-charter`.

## Lesson Planner governance enforcement

For Lesson Planner MVP stories (Epics 28-32), run
`python scripts/utilities/validate_lesson_planner_story_governance.py <story-file>`
at two gates:

1. before a story is finalized as `ready-for-dev`
2. before `bmad-dev-story` begins

If the validator fails, treat it as a governance failure that must be remediated before proceeding.

Default behavior is **self-remediate first, escalate second**:

- Automatically fix every policy-preserving issue you can correct in the story spec or adjacent workflow artifacts.
- Rerun the validator after remediation and continue without waiting for the human if the story reaches PASS.
- Escalate to the human only if the remaining failure requires:
  - a gate-mode change (`single-gate` vs `dual-gate`)
  - a K-policy or target-range policy change
  - an intentional update to `docs/dev-guide/lesson-planner-story-governance.json`
  - a deliberate policy exception
  - a true party-mode impasse on scope, architecture, or governance interpretation

This validator enforces story-specific gate mode, explicit `T1 Readiness`,
required readings, scaffold references for schema stories, story-status sync
against `sprint-status.yaml`, and K-range discipline.

Closeout hygiene remains required for Lesson Planner stories:

- update `sprint-status.yaml` first
- update `next-session-start-here.md` second
- update any top-level plan/status line that would otherwise mislead
