# Agent instructions

**Sprint governance:** Multi-story BMAD work in this repo follows the same BMAD sprint run charter everywhere it applies:

| Environment | Mechanism |
| --- | --- |
| **Cursor** | [`.cursor/rules/bmad-sprint-governance.mdc`](.cursor/rules/bmad-sprint-governance.mdc) (`alwaysApply`) |
| **VS Code — GitHub Copilot Chat** | [`.github/copilot-instructions.md`](.github/copilot-instructions.md) (always-on workspace instructions) |
| **Claude Code CLI** | [`CLAUDE.md`](CLAUDE.md) |

Optional explicit load (skills): **`bmad-sprint-run-charter`**. In VS Code you can also use **Chat: Open Chat Customizations** (Command Palette) to confirm which instruction files are active.

**VS Code notes:** Custom instructions apply to chat (not inline completions as you type). File-scoped rules can live under `.github/instructions/` as `*.instructions.md` with `applyTo` in frontmatter; see [Use custom instructions in VS Code](https://code.visualstudio.com/docs/copilot/customization/custom-instructions).

**`.github/agents/` vs. `.github/instructions/` — sibling-but-distinct mechanisms.** `.github/agents/*.agent.md` are GitHub Copilot Chat **chat-agent persona stubs** emitted by the BMAD installer (one stub per stock persona; 5-line redirect into the `.agents/skills/<skill-name>/SKILL.md` tree). They are an IDE-surface mirror — installer-managed and gitignored alongside `.agents/`, `.claude/`, `.cline/`, `.github/skills/`, `.cursor/skills/`. `.github/instructions/*.instructions.md`, by contrast, are **file-scoped operator-authored rules** with `applyTo` frontmatter and remain tracked. Stock-persona chat stubs regenerate on every BMAD installer bump; custom personas (Marcus and the 11-specialist body) live at `skills/bmad-agent-{name}/SKILL.md` + `_bmad/memory/bmad-agent-{name}/` and are operator-tracked.
