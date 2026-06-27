# P5 Directed Voice Implementation Control Cards

Date: 2026-06-27
Authoring source: BMAD Marcus advisory guidance, transported by Codex
Audience: Claude Code implementation agent, its active BMAD workflow / party-mode team, reviewers, and operator

## Purpose

This addendum sharpens the active P5 directed-voice goal as complementary advisory input. It is not a replacement for `goal-p5-directed-voice-next-product.txt`, Claude Code's active BMAD workflow, or the decisions of Claude's tailored party-mode team.

If Claude's team finds newer implementation evidence, a better local path, or a necessary schema change, their reviewed BMAD decision governs. This file is meant to reduce ambiguity and make review easier, not to overwrite live engineering judgment.

Directed synthesized voice is a must-ship condition for the next product slice. It must not be deferred behind P5-S2, terminal Descript, or future learning/autonomy work.

## Governance

- Use BMAD workflows for any new story/spec decomposition.
- Use fully spawned, tailored `bmad-party-mode` teams for major green-light, review, approval, and next-step decisions.
- Run `bmad-code-review` before marking implementation done.
- Keep Text-to-Dialogue out of the critical path unless the selected proof genuinely requires multi-speaker dialogue.
- Preserve existing non-directed narration behavior as a backward-compatible fallback.

## Control Card 1: Voice Direction Contract

### Must

Define a per-segment `voice_direction` contract that can live beside `narration_text`, `voice_id`, `behavioral_intent`, `bridge_type`, timing metadata, and cluster metadata.

Minimum shape:

```yaml
voice_direction:
  render_strategy: tts
  delivery_intent: reflective
  emotional_tone: concerned
  pace: slower
  energy: medium
  delivery_tag: "[thoughtfully]"
  pause_before_seconds: 0.3
  pause_after_seconds: 0.6
  elevenlabs:
    stability: 0.48
    style: 0.15
    speed: 0.94
```

Allowed `render_strategy` values for this slice:

- `tts`: implemented now; default.
- `dialogue`: schema-tolerated or deferred stub only, unless a specific proof requires it.

Required precedence:

1. Segment-level `voice_direction.elevenlabs.*`
2. Segment-level `voice_id`
3. Pass-2 `voice_direction_defaults`
4. `voice-selection.json` selected default voice
5. `state/config/style_guide.yaml` defaults

### Should

- Keep enum values small and plain-language: `neutral`, `warm`, `concerned`, `urgent`, `reflective`, `encouraging`; `slower`, `neutral`, `faster`; `low`, `medium`, `high`.
- Preserve unknown/additive fields if existing manifest patterns allow forward compatibility.
- Treat missing `voice_direction` as valid and equivalent to legacy/global-default behavior.

### Defer

- Learned automatic voice-direction selection.
- Full multi-speaker Text-to-Dialogue orchestration.
- Fine-grained phoneme/prosody control beyond fields supported by current ElevenLabs calls.

### Complete When

Old manifests still pass; new fixtures with per-segment `voice_direction` pass; precedence rules are documented and tested.

## Control Card 2: Storyboard B Review Checklist

### Must Show Before Audio Spend

For each narrated segment/slide, Storyboard B must show:

- Segment id and slide id.
- Narration text.
- `voice_direction` summary.
- Effective render strategy.
- Effective delivery intent/tone/pace/energy.
- Any delivery tag.
- Any segment-level ElevenLabs overrides.
- Effective voice source: segment `voice_id`, `voice-selection.json`, or fallback default.
- Timing context: runtime target, duration estimate, timing role, bridge type.
- Pedagogical context: behavioral intent, cluster role/position when present.

Missing segment-level direction must be explicit, for example: `Voice direction: using global/default settings`.

### Should

- Keep the display operator-readable, not raw JSON first.
- Preserve existing Storyboard B script, timing, bridge, cluster, motion, and provenance panels.
- Make segment-level overrides visually distinguishable from defaults.

### Defer

- In-browser editing of voice direction.
- Audio preview playback inside Storyboard B.

### Complete When

An operator can approve or challenge intended voice treatment from Storyboard B without opening the raw manifest.

## Control Card 3: Enrique Consumption Checklist

### Must

Enrique must consume segment-level direction during manifest-driven narration generation.

Required behavior:

- Read `voice_direction` per segment.
- Preserve existing `voice_id` override behavior.
- Merge segment-level ElevenLabs settings over pass/global defaults.
- Map `emotional_tone`, `pace`, `energy`, and `delivery_intent` to concrete TTS settings or safe textual/delivery tags.
- Continue passing prior request ids where current continuity logic does so.
- Write receipts that expose effective settings per segment.
- Preserve no-direction legacy behavior.

Required receipt fields per segment:

- `segment_id`
- `voice_id`
- `render_strategy`
- `effective_voice_direction`
- `effective_elevenlabs_settings`
- `request_id`
- `narration_file`
- `narration_vtt`
- `narration_duration`

### Should

- Keep TTS as the critical-path strategy.
- Treat delivery tags conservatively; do not inject tags that would pollute learner-facing text unless the implementation explicitly isolates generation text from displayed script.
- Fail loud on unsupported `render_strategy` values if they would cause silent wrong output.

### Defer

- Full dialogue turn rendering unless explicitly selected.
- Automated perceptual scoring of audio quality.

### Complete When

Tests prove adjacent segments can receive different effective settings, and generated manifest/receipts show those differences without mutating locked root artifacts incorrectly.

## Control Card 4: Directed-Audio Proof Plan

### RED-First Tests

At minimum, add tests for:

1. Legacy manifest without `voice_direction` remains valid and uses defaults.
2. Segment `voice_direction.elevenlabs.speed` overrides global speed.
3. Segment `voice_direction.elevenlabs.stability` overrides global stability.
4. Segment `voice_id` remains honored.
5. Storyboard B displays voice direction when present.
6. Storyboard B explicitly shows default/fallback state when absent.
7. Enrique receipt records effective segment settings.
8. Unsupported critical `render_strategy` fails loud or is explicitly deferred.

### Live Proof

Run a small slice with at least three approved treatments:

- Neutral baseline.
- Reflective or concerned.
- Warm or encouraging.

Evidence must include:

- Storyboard B review surface or JSON proving direction was visible before spend.
- Manifest segment rows carrying direction.
- Enrique receipts with distinct effective settings.
- Generated audio files and VTTs.
- Operator or reviewer note that the clips are perceptibly different in the intended direction.

### Party-Mode Review Team

Recommended tailored team:

- Irene: script and instructional intent.
- CD: directorial/theatrical direction.
- Enrique: synthesis feasibility and settings.
- Quinn-R: learner-facing quality and coherence.
- Murat: test/proof sufficiency.
- Winston: contract stability and maintainability.

### Complete When

The team signs off that the implementation proves product value, not only field plumbing.

## Definition Of Done For P5 Directed Voice Slice

The slice is done only when:

1. `voice_direction` is typed/documented and backward compatible.
2. CD/Irene can emit it per segment.
3. Storyboard B exposes it before audio spend.
4. Enrique consumes it with segment-level precedence.
5. Tests cover legacy, override, display, and receipt behavior.
6. A live proof produces at least three intentionally different delivery treatments.
7. P5-S2 remains aligned: enriched deck/narration consumption is not displaced by voice work.
8. BMAD party-mode signs off with no impasse.
9. `bmad-code-review` passes before done.
