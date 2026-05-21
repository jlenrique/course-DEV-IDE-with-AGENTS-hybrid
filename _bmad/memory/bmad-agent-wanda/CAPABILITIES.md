---
kind: wanda-capabilities
status: operator-population-pending
created: 2026-04-29
---

# Wanda Capabilities

<!-- TODO: operator-populate via First Breath ceremony -->

## Runtime Capability

Wanda generates Wondercraft-backed podcast and music-bed artifacts for the
storyboard audio track. Story 7b.9 binds runtime execution to
`app/specialists/wanda/` and uses `scripts/api_clients/wondercraft_client.py`
through the specialist act body.

## Wondercraft Reference Inventory

Reference-only API and production guidance lives in
`skills/bmad-agent-wondercraft/references/`:

- `capability-audio-assembly-handoff.md`
- `capability-audio-summary-produce.md`
- `capability-chapter-markers-emit.md`
- `capability-music-bed-apply.md`
- `capability-podcast-dialogue-produce.md`
- `capability-podcast-episode-produce.md`
- `context-envelope-schema.md`
- `first-breath.md`
- `init.md`
- `memory-system.md`
- `save-memory.md`
- `L5-podcast-production/storytelling-framework.md`
- `L5-podcast-production/audio-production-patterns.md`
- `L5-podcast-production/narration-length-vs-engagement.md`

## Folded Operational Context

The legacy `L6-operational/wondercraft-context.md` content is preserved here.

### Voice-ID catalog

1. `voice_a_narrator`: TODO operator selects production narrator voice.
2. Usage context: TODO define narration role and lesson format fit.
3. Register: TODO define warm, formal, conversational, or dramatic range.
4. Sample-rate cap: TODO record Wondercraft/export constraint.
5. `voice_b_expert`: TODO operator selects expert or guest voice.
6. Usage context: TODO define explanatory or interview role.
7. Register: TODO define authority, texture, and pacing expectations.
8. Sample-rate cap: TODO record Wondercraft/export constraint.
9. `voice_c_student`: TODO operator selects learner or contrast voice.
10. Usage context: TODO define question, misconception, or reflection role.
11. Register: TODO define curiosity, hesitation, and energy level.
12. Sample-rate cap: TODO record Wondercraft/export constraint.

### Episode-template skeleton

1. Hook, 0:00-0:30: TODO define opening move and stakes.
2. Context, 0:30-2:00: TODO define course placement and prior knowledge.
3. Body, 2:00-7:00: TODO define concept sequence and example cadence.
4. Call to action, 7:00-8:00: TODO define learner action and transition.
5. `dispatch_episode` cue: TODO define single-narrator payload pattern.
6. `dispatch_dialogue` cue: TODO define two-voice script handoff pattern.
7. Music intro cue: TODO define allowed intro length and fade-in behavior.
8. Segment break cue: TODO define chapter marker naming convention.
9. Safety cue: TODO define when to stop for operator review.
10. Metadata cue: TODO define title, summary, and artifact naming rules.

### Style-guide overrides

1. Music-bed-volume default: TODO confirm -18 LUFS or operator override.
2. Pause-after-question default: TODO confirm 1.2 seconds or override.
3. Segue-tone preference: TODO map voice pair to transition style.
4. Narration speed: TODO define words-per-minute band.
5. Emphasis rule: TODO define how technical terms are introduced.
6. Silence rule: TODO define pauses around reflection prompts.
7. Sound-design rule: TODO define what not to add.
8. Accessibility rule: TODO define transcript and caption expectations.
9. Review rule: TODO define when operator listens before commit.
10. Cost rule: TODO define abort condition for pricing or duration drift.
