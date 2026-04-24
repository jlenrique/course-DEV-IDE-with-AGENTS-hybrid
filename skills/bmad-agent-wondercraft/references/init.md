---
name: init
description: Activation / initialization path when sanctum exists
---

# Activation

1. Check for sanctum at `{project-root}/_bmad/memory/bmad-agent-wondercraft/`.
2. If **absent**, route to `./first-breath.md` and run the scaffold:
   `python skills/bmad-agent-wondercraft/scripts/init-sanctum.py`
   (thin forwarder to `scripts/bmb_agent_migration/init_sanctum.py`).
3. If **present**, batch-load from the sanctum: `INDEX.md`, `PERSONA.md`, `CREED.md`, `BOND.md`, `MEMORY.md`, `CAPABILITIES.md`. Become yourself again.
4. Re-read `state/config/style_guide.yaml` fresh before every production task.
5. If the operator is running a tracked production, check active baton with `skills/production-coordination/scripts/manage_baton.py check-specialist wondercraft-specialist` before accepting direct work.
