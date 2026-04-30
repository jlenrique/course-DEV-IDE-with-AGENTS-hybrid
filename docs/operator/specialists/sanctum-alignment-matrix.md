# Specialist Sanctum-Alignment Matrix (operator-facing twin)

This is the operator-facing twin of the dev-doc at [`docs/dev-guide/specialist-sanctum-alignment-matrix.md`](../../dev-guide/specialist-sanctum-alignment-matrix.md). It records, for each of the 11 active specialists, where their persona memory lives, where their skill activation contract lives, and what each operator should know to invoke them or trust their outputs.

If you're new to the system: each specialist has a **sanctum** (a directory of persona-continuity files at `_bmad/memory/bmad-agent-{name}/` — these are the agent's "memory" between sessions) and one or more **SKILL.md** files (the agent's activation contract; tells Claude how to embody them). For most specialists there's a single SKILL.md. For Class-C API-bound specialists (Gary/Kira/Enrique/Wanda), there are **two**: one for persona, one for the API the specialist drives.

## What each entry means

- **Sanctum path** — where the persistent memory + persona files for this specialist live. Contents are markdown; you can read them directly to understand "what this specialist knows about you and prior runs."
- **Persona SKILL.md** — the entry point for invoking the specialist as an agent. This is what Claude reads first when you say "talk to {specialist}".
- **API-mastery SKILL.md** (Class-C only) — the reference material for the third-party API the specialist drives (Gamma slides / Kling motion / ElevenLabs voice / Wondercraft audio). Not invoked directly by you; the specialist consults it lazily.

## Matrix

| # | Specialist | Class | Sanctum path (memory) | Persona SKILL.md (activation) | API-mastery SKILL.md (reference; Class-C only) |
|---|---|---|---|---|---|
| 1 | Texas | A | `_bmad/memory/bmad-agent-texas/` | `skills/bmad-agent-texas/SKILL.md` | — |
| 2 | Quinn-R | A | `_bmad/memory/bmad-agent-quinn-r/` | `skills/bmad-agent-quality-reviewer/SKILL.md` | — |
| 3 | Vera | A | `_bmad/memory/bmad-agent-vera/` | `skills/bmad-agent-fidelity-assessor/SKILL.md` | — |
| 4 | Irene Pass-1 | B | `_bmad/memory/bmad-agent-content-creator/` (shared with Pass-2) | `skills/bmad-agent-content-creator/SKILL.md` | — |
| 5 | Tracy | C+ | `_bmad/memory/bmad-agent-tracy/` (4-file sidecar) | `skills/bmad-agent-tracy/SKILL.md` | — |
| 6 | Gary | C | `_bmad/memory/bmad-agent-gary/` | `skills/bmad-agent-gary/SKILL.md` | `skills/bmad-agent-gamma/SKILL.md` |
| 7 | Kira | C | `_bmad/memory/bmad-agent-kira/` | `skills/bmad-agent-kira/SKILL.md` | `skills/bmad-agent-kling/SKILL.md` |
| 8 | Enrique | C | `_bmad/memory/bmad-agent-enrique/` | `skills/bmad-agent-enrique/SKILL.md` | `skills/bmad-agent-elevenlabs/SKILL.md` |
| 9 | Wanda | C | `_bmad/memory/bmad-agent-wanda/` | `skills/bmad-agent-wanda/SKILL.md` | `skills/bmad-agent-wondercraft/SKILL.md` |
| 10 | Dan | D1 | `_bmad/memory/bmad-agent-dan/` | `skills/bmad-agent-dan/SKILL.md` | — (LLM-only; no third-party API) |
| 11 | Compositor | D2 | `_bmad/memory/bmad-agent-compositor/` (4-file operational metadata) | `skills/compositor/SKILL.md` | — (deterministic pipeline; no API; no LLM) |

## How to invoke a specialist

Cold-start, operator says "{specialist}" or "talk to {specialist}":

1. Read the persona SKILL.md listed above for that specialist.
2. Follow its activation hot-load batch (the SKILL.md tells you which sanctum files to read in what order).
3. For Class-C specialists, the persona SKILL.md will also point to the API-mastery SKILL.md for reference material — load it lazily only when API operations are needed.

If the sanctum directory doesn't exist (clean checkout), the SKILL.md falls back to a "first-breath" posture documented in each SKILL.md.

## Cross-references

- Per-specialist OPERATOR/INPUTS/OUTPUTS/REFERENCE docs: `docs/operator/specialists/{name}.md` (one per specialist; this matrix lists where; that doc tells you what they DO).
- Operator-control parity table (legacy lever → migrated lever per specialist): [`../legacy-vs-langgraph-control-parity.md`](../legacy-vs-langgraph-control-parity.md).
- Dev-doc twin (with structural enforcement details): [`../../dev-guide/specialist-sanctum-alignment-matrix.md`](../../dev-guide/specialist-sanctum-alignment-matrix.md).
