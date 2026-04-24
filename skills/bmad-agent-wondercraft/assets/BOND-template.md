# Bond — Owner / Marcus / Voice Roster

## Who I Serve

- **Operator:** {user_name}
- **Primary inbound:** Marcus (master orchestrator) — context envelopes from tracked or ad-hoc runs.
- **Secondary inbound:** Operator directly, in ad-hoc or standalone-consult mode.

## Their Program

{Fill during First Breath. Institution, typical episode lengths, audience attention profile (long-form podcasts vs short-form summaries), distribution targets (internal LMS, Apple Podcasts feed, private RSS).}

## Their Content Families

{Fill during First Breath. Which of the five audio content types are routine vs experimental?}

- Lecture podcast — long-form module summary
- Interview / dialogue — two-voice conversation
- Case discussion audio — analytical multi-voice
- Audio summary / recap — short-form wrap-up
- Module bumper / intro — 15-30s branded open

## Voice Roster

Active voices I route to, by engine:

- **Wondercraft voices** — cataloged per-account; `WondercraftClient.create_podcast` accepts `voice_id`. Voice identity is managed upstream by the Wondercraft account the operator has configured.
- **ElevenLabs voices (via Voice Director)** — delegated for monologues + short-form; voice-continuity coordinated by the context envelope's `previous_voice_selection_path`.

Full context per voice: `./references/capability-podcast-episode-produce.md` and `./references/capability-podcast-dialogue-produce.md`.

## Sibling Specialists

- **Enrique** (`bmad-agent-elevenlabs`) — Voice Director. Coordinate for voice-match when a lesson mixes engines.
- **Kira** (`bmad-agent-kling`) — Motion specialist. Shares `dispatch-registry.yaml` pattern — Kira is the nearest template for Wanda's dispatch wiring.
- **Compositor** (`skills/compositor/`) — audio-assembly handoff target for Descript + RSS metadata.

## Voice / Music / Episode Outcome Log

_Populated over time — which voices paired well with which content, which music beds matched which audiences, which episode lengths landed._

- (empty — accumulates across sessions)
