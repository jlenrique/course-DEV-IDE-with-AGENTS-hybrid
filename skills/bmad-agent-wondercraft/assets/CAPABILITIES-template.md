# Capabilities

_(Note: This template is overwritten by the scaffold with an auto-generated listing derived from `references/*.md` frontmatter. Hand-authored Tools section below survives scaffold runs.)_

## Built-in

| Code | Name | Description | Source |
|------|------|-------------|--------|
| EP | podcast_episode_produce | Single-host monologue episode from narration script | `./references/capability-podcast-episode-produce.md` |
| DP | podcast_dialogue_produce | Multi-voice dialogue / interview / case-discussion format | `./references/capability-podcast-dialogue-produce.md` |
| AS | audio_summary_produce | Short-form recap / summary audio | `./references/capability-audio-summary-produce.md` |
| MB | music_bed_apply | Apply background music bed to existing audio | `./references/capability-music-bed-apply.md` |
| CM | chapter_markers_emit | Generate chapter-marked output with metadata | `./references/capability-chapter-markers-emit.md` |
| AH | audio_assembly_handoff | Emit Descript project + assembly guide | `./references/capability-audio-assembly-handoff.md` |
| ENV | context-envelope-schema | Marcus → Wanda dispatch envelope schema | `./references/context-envelope-schema.md` |
| SM | save-memory | Session-context persistence | `./references/save-memory.md` |

## Tools

- **Wondercraft API client** — `scripts/api_clients/wondercraft_client.py` (NOT refactored by this agent; thin wrapper only).
- **Voice Director coordination** — delegation-protocol handoff when lesson mixes ElevenLabs + Wondercraft.
- **Compositor audio-assembly** — target for Descript handoff emission.
- **Pre-flight-check** — Wondercraft API key surfaced via `WONDERCRAFT_API_KEY` readiness check.

## Learned Capabilities

_Populated over time as owner teaches capability prompts. See `./capabilities/` directory._

- (empty at birth)
