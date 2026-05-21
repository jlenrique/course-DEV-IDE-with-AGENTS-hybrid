# Cowork Project Setup Guide — course-DEV-IDE-with-AGENTS

How to wire up a Cowork Project for ongoing development on this repo, using the three artifacts in this folder.

## Artifact map

| File | Destination in Cowork Project | Purpose |
|---|---|---|
| `cowork-project-instructions.md` | **Instructions** field (paste the fenced content) | Directive that governs every chat in the project — sources of truth, lane discipline, default branch, protocols. |
| `cowork-project-seed.md` | **Files** section (upload the whole file) | Condensed orientation always in context so new chats start warm. |
| `cowork-project-setup-guide.md` (this file) | No destination — stays in the repo as the setup reference. | How to do the setup and maintain it. |

## One-time setup

1. **Update Claude Desktop.** Cowork Projects require the latest desktop build; older versions may lack the Files surface.
2. **Create the project.**
   - Left navigation → **Projects** → click **+**.
   - Choose *Start from scratch* (or *Use an existing folder* if offered).
   - Name it something like `course-DEV-IDE-with-AGENTS — pipeline dev`.
   - Pick a local save location for project data (per-machine; no cloud sync).
3. **Connect the repo folder.**
   - When prompted for a folder, or via the project's folder setting, point it at the local repo root (e.g., `C:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS-hybrid` for the hybrid clone, or `...\course-DEV-IDE-with-AGENTS` for primary).
   - Connecting the folder is what gives Claude read/write access to the whole repo. You do not need to upload repo docs into Files — they're already reachable.
4. **Paste the Instructions.**
   - Open `maintenance/cowork-project-instructions.md`.
   - Copy everything between `--- BEGIN INSTRUCTIONS ---` and `--- END INSTRUCTIONS ---`.
   - Paste into the project's **Instructions** field.
5. **Upload the seed to Files.**
   - Inside the project page, find the **Files** section.
   - Click **+** → upload `maintenance/cowork-project-seed.md`.
   - This is the only file that benefits from being "pinned" — everything else is accessible via the connected folder.
6. **Confirm memory is on.** Cowork Projects default to memory-enabled. Verify in the project settings so context accumulates across chats.

## What NOT to upload to Files

Because the folder is connected, do not upload copies of repo docs into Files. Specifically, skip:

- Anything under `docs/` (project-context, structural-walk, fidelity-gate-map, lane-matrix, directory-responsibilities, parameter-directory).
- `SESSION-HANDOFF.md` and `next-session-start-here.md`.
- `_bmad-output/implementation-artifacts/sprint-status.yaml`.
- Any skill `SKILL.md`, any `state/config/*.yaml`, any script or test.

Claude reads these live, always current. Uploading stale copies into Files would fight the source-of-truth hierarchy.

## What else to consider adding to Files (optional)

Only add files to the **Files** section when they meet one of these criteria:

- **External to the repo** — e.g., a branding PDF on OneDrive, a vendor API spec, a client brief you don't want committed to git.
- **High-signal always-pin** — a small, condensed doc that benefits from being first-read on every chat. `cowork-project-seed.md` already covers this; add more sparingly.
- **URL references** — paste URLs (e.g., Anthropic docs, prompting guides) for Claude to consult.

## Maintaining the project over time

- **After an epic closure or wave completion:** refresh `cowork-project-seed.md` (update "Current momentum" section and "Last refreshed" date), then re-upload to Files, replacing the previous version.
- **After an architecture shift** (new orchestrator, new parameter family, new gate): refresh both the seed and the Instructions, then re-paste Instructions and re-upload the seed.
- **After a branch change:** update the default-branch line in the Instructions content.
- **After protocol changes** (new doc-review prompt version, new session protocol): point the Instructions at the new filename.

Treat `cowork-project-instructions.md` and `cowork-project-seed.md` as **living repo artifacts**. Edit them here in the repo, commit, and re-sync the Cowork Project surfaces when they change. The repo copies are canonical; the Cowork fields are mirrors.

## When to use Cowork vs. Cursor + Claude Code

- **Cowork Project:** day-to-day conversational development, file reads/edits, quick studies, drafting reports, small refactors, answering "how does X work?" questions.
- **Cursor + Claude Code (optionally 1M context mode):** full BMAD party-mode runs with real multi-agent rituals, repo-wide harmonization passes that need many docs resident at once, deep structural walks with follow-on edits, anything that benefits from the IDE's native file tree and addressable `.claude/.cursor/` skills.

If a task requires true party mode or heavy cross-file harmonization, flag the limitation and run it from Cursor. The Instructions already tell Claude to do this.

## Sanity check after setup

Start a new chat in the project and ask: *"What is the current active branch, last closed epic, and next operator action?"*

A correctly configured project will answer `DEV/slides-redesign`, `Epic 23`, and `fresh trial with prompt pack v4.2f` — all drawn from the connected repo plus the seed. If those aren't right, the folder connection or seed upload didn't take.
