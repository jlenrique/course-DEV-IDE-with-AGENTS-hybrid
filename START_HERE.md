# Project Entry Point — course-DEV-IDE-with-AGENTS — hybrid implementation

Standard-Version: 1.0.0
Standard-Source: project-registry-maintenance/docs/standards/START_HERE_STANDARD.md
Standard-Revision: 3da386e2c0c65ae49c2beba21e9a3f8d5b9d0bfe
Status: Active
Project: PRJ-0006 — course-DEV-IDE-with-AGENTS — hybrid implementation

Collaborative agent-assisted course-content production, hybrid LangGraph/Marcus-SPOC implementation.

This is the project-owned entry map. Existing detailed instructions remain at
their sources. Discovery does not authorize live actions or agent activation.

[Shared standard](https://github.com/jlenrique/project-registry-maintenance/blob/3da386e2c0c65ae49c2beba21e9a3f8d5b9d0bfe/docs/standards/START_HERE_STANDARD.md) · [Audit procedure](https://github.com/jlenrique/project-registry-maintenance/blob/3da386e2c0c65ae49c2beba21e9a3f8d5b9d0bfe/docs/standards/START_HERE_AUDIT.md)

Location: repository/project root on the current host. Relative paths resolve
against this root, not a fixed username or drive. Git clones remain one project;
verify remote identity and local revision. Host deployment is verified separately.

## Resource map

| Resource role | Status | Existing resource(s) | Scope and authority |
|---|---|---|---|
| **Agents** | Mapped | [SKILL.md](<skills/bmad-agent-marcus/SKILL.md>); [specialist-registry.yaml](<skills/bmad-agent-marcus/references/specialist-registry.yaml>); [agent-environment.md](<docs/agent-environment.md>) | Marcus-SPOC/custom specialists and agent-environment rules; custom personas are separate from the stock BMAD manifest. Read AGENTS/CLAUDE distinctions before production or proofing. |
| **Resource Directory** | Mapped | [README.md](<README.md>); [directory-responsibilities.md](<docs/directory-responsibilities.md>); [parameter-directory.md](<docs/parameter-directory.md>) | README routes by audience and distinguishes current hybrid workflows from legacy guides. See Agents. |
| **Session Start** | Mapped | [AGENTS.md](<AGENTS.md>); [CLAUDE.md](<CLAUDE.md>); [bmad-session-protocol-session-START.md](<bmad-session-protocol-session-START.md>) | Existing hybrid startup/classification and agent-environment instructions apply; do not substitute the legacy checkout routine. |
| **Preflight** | Mapped | [trial-run-runbook.md](<docs/operator/trial-run-runbook.md>); [ready_for_trial.ps1](<scripts/setup/ready_for_trial.ps1>); [bmad-session-protocol-session-START.md](<bmad-session-protocol-session-START.md>) | Run trial readiness only for an authorized trial; dependencies and environment are host-specific. Documentation mapping does not run production. |
| **Session Handoff** | Mapped | [SESSION-HANDOFF.md](<SESSION-HANDOFF.md>); [next-session-start-here.md](<next-session-start-here.md>); [bmad-session-protocol-session-WRAPUP.md](<bmad-session-protocol-session-WRAPUP.md>) | Canonical authored handoff and immediate cache, with existing generators/upkeep controlled by WRAPUP. |
| **Role Guides** | Mapped | [trial-run-runbook.md](<docs/operator/trial-run-runbook.md>); [production-trial-playbook.md](<docs/operator/production-trial-playbook.md>); [admin-guide.md](<docs/admin-guide.md>); [dev-guide.md](<docs/dev-guide.md>); [langgraph-migration-guide.md](<docs/dev-guide/langgraph-migration-guide.md>) | Current hybrid operator/admin/developer routes. README labels docs/user-guide.md legacy pre-migration reference; do not use it as current production instructions. |

## Reading order

1. Confirm project identity, host, checkout/variant and task. Honor existing project instructions.
2. Read the Agents directory/contract before specialist routing. Verify the selected
   definition and runtime; directory presence does not authorize activation.
3. Follow Session Start and its complete required reads, current handoff, source
   precedence and task-appropriate Preflight. Do not run live operations merely to
   check this entry map. Select only the checks required for the authorized task.
4. Use Resource Directory and Role Guides; see Agents for role ownership. Close
   through the existing Session Handoff/WRAPUP and the rapid audit below.

## Rapid currency and quality audit

At every meaningful session close, inspect START_HERE and resources affected by
the session, plus known unresolved findings. Keep this rapid and bounded:

1. Check project/host/revision identity and affected links. Do not infer another
   clone has pulled changes or a cloud upload is synchronized with a local file.
2. Check currency against relevant code, source and workflow changes; age alone
   is not staleness. Check quality: authority, clarity, completeness for the task,
   usability, consistency and unnecessary duplication.
3. Check Agents ownership, capabilities, definitions/activation paths, runtime
   availability and shared-resource references. A skill is not an agent registry.
4. Recommend the smallest effective repair. Verify the actual environment can
   use a recommended skill/tool. For outdated graph-derived onboarding, suggest
   Understand Anything only if relevant and available; otherwise identify an
   existing capable environment, established alternative or targeted manual
   update. Installing a missing skill is a proposal, not an automatic action.
5. Record findings with evidence, impact, recommended action, prerequisites,
   availability, fallback and next action. Report scope not checked. Escalate
   broad drift to a separately scoped audit rather than an unbounded scan.

## Session-closeout rule

Follow the existing closeout procedure and perform the rapid audit above in all
session classes. Update authoritative catalogs/docs first, then this map only
when its pointers, scope, authority or reading order changes. Do not copy agent
rosters, procedures or session history here. Preserve unrelated user changes.

When available, run the shared `tools/check_start_here.py START_HERE.md --root .`
from the Registry maintenance checkout (use an absolute document/root path when
working elsewhere). Cloud-only sessions use the same checklist manually if no
Python/file access exists; record why automated validation was not run.

Record in the existing handoff, or the session's closing response if no durable
handoff exists: project ID; host/platform/revision; standard 1.0.0; structural
result or not-run reason; currency AND quality audit scope/findings; Agents check;
map unchanged/updated/blocked; recommendations, prerequisites/fallbacks and next
action. No unperformed check may be reported as passed. Unchanged mappings need
no timestamp-only edit. Update registry pointers only for changed entry location,
identity/access or deployment status, under its own update contract.

## Known mapping limitations

Same project purpose/lineage as PRJ-0006; this is the distinct hybrid implementation, with its own remote and diverged history. The README records the upstream separation. Do not treat BAMBOO legacy and Tower hybrid checkouts as interchangeable or merge/sync them automatically. Runtime availability and live trial readiness were not tested in this documentation rollout.

Deployment observation (2026-11-05): Git HEAD `67af77e77cae3c7d8ccaf88138dfaf89505311cc`; this is evidence, not a required dependency pin or proof of a clean worktree.
