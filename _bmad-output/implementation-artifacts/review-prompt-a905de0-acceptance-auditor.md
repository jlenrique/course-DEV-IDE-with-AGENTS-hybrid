# Review Prompt: Acceptance Auditor

Review target: commit `a905de0`
Role: Acceptance Auditor
Mode: Diff plus spec/context review.

Instructions:
- Review this diff against the story spec and context docs.
- Check for violations of acceptance criteria, deviations from spec intent, missing implementation of specified behavior, and contradictions between spec constraints and the actual change.
- Output findings as a Markdown list.
- For each finding: one-line title, which AC or constraint it violates, evidence, and why it matters.
- If there are no findings, say `No findings.`

Spec file:
- `_bmad-output/implementation-artifacts/migration-1-1a-runtime-substrate-environment-and-dependencies.md`

Context docs:
- `docs/project-context.md`
- `CLAUDE.md`

Diff source:
- `git show a905de0`

Acceptance areas to verify closely:
- AC-1 venv creation, exact dependency set, lockfile
- AC-2 import smoke
- AC-3 import-linter and ruff expectations for the empty `app/` tree
- AC-4 `.env.example` tracking posture and `.env` ignore behavior
- Story closeout integrity: status transitions, task closure fidelity, and whether any implementation exceeded Story 1.1a’s intended scope
