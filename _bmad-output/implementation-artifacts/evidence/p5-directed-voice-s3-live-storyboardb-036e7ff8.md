# P5 Directed Voice — Step 3 LIVE Storyboard B evidence

Date: 2026-06-27
Step: 3 (Storyboard B displays per-segment `voice_direction` before audio spend)
Mode: OFFLINE (no external API). Flag `MARCUS_NARRATION_VOICE_DIRECTION_ACTIVE=1`.

## Source run (REAL, read-only)

`state/config/runs/036e7ff8-b079-4051-bb78-0f739ad62125` — the canonical run used
by the workbook live-close. Its production envelope carries a REAL Irene Pass-2
contribution (`contributions[12].output`): 6 segments (`seg-01..seg-06`) with real
`narration_script` + `segment_manifest_deltas`. The committed run dir was NOT
mutated; all output was written to a scratch copy + this evidence dir.

## Real chain exercised end-to-end (flag ON)

1. **Step-1 contract + Step-2 emission (REAL):**
   `annotate_segments_with_voice_direction(deltas, defaults={"emotional_tone":"warm"},
   per_segment_overrides=...)` with the audition-rubric §4 palette —
   `seg-01` neutral baseline, `seg-02` reflective/slower/low (+`[thoughtfully]`
   delivery_tag + delivery_intent), `seg-03` warm, `seg-04` concerned/slower with an
   explicit `elevenlabs.similarity_boost=0.8` override. `seg-06` left UNDIRECTED to
   exercise the explicit missing-direction path. Result: 5 directed + 1 undirected,
   each directed segment a valid `VoiceDirection` round-trip.
2. **Publisher seam (REAL):** `_write_segment_manifest_for_b(...)` re-attached
   `voice_direction` onto the joined segments after the frozen `join_narration_segments`
   neck — produced a real `segment-manifest-storyboard-b.yaml` carrying voice_direction.
3. **Storyboard B render (REAL):** the legacy `generate-storyboard.py` `cmd_generate`
   ran against the run's real `gary-dispatch-payload.json` + the directed manifest →
   real `index.html` (56,734 bytes, 6 voice-direction panels, rc=0).

## What the rendered Storyboard B actually showed

Six per-segment **Voice direction** panels rendered, each VISUALLY SEPARATE from the
learner-facing narration `<pre>`. The reflective directed panel (seg-02) showed:
`source: operator-override`; render strategy `tts`; emotional tone `reflective`; pace
`slower`; energy `low`; delivery intent flagged "review metadata, not script"; the
`[thoughtfully]` delivery_tag as a distinct **generation-only cue (NOT narrated, never
captioned)** — confirmed absent from every narration `<pre class="script-text">`; and a
**Resolved TTS settings — what Enrique will send** block reading stability `0.75`, style
`0.1`, speed `0.94` with voice_id/model_id/similarity_boost shown as "global/default
(resolved at synthesis)". Those resolved numbers are computed by the SAME shared
`map_voice_direction_to_tts` mapper Enrique uses (MUR-3 display↔dispatch parity). The
undirected seg-06 panel showed the explicit "Voice direction: using global/default
settings". A global **Voice direction defaults** header (tts / neutral / neutral /
medium baseline + variability) rendered in the run-summary banner.

## Live verification probes (all PASS)

panel present · reflective enum shown · delivery_intent shown · delivery_tag distinct ·
tag NOT in narration `<pre>` · resolved speed 0.94 · resolved stability 0.75 ·
similarity_boost override 0.8 · missing-explicit default text · global defaults header.

Baseline-vs-deliberate disambiguation verified separately: a `cd-authored` all-neutral
direction renders "baseline default (conservative built-in)"; an `operator-override`
neutral (a deliberate choice) correctly renders `source: operator-override` instead.

## Artifacts

- `p5-directed-voice-s3-live-storyboardb-036e7ff8-b079-4051-bb78-0f739ad62125.yaml` —
  the directed segment manifest carrying voice_direction.
- `p5-directed-voice-s3-live-storyboardb-036e7ff8-b079-4051-bb78-0f739ad62125.html` —
  the rendered Storyboard B.

## Code-review remediation re-render (2026-06-27)

Re-ran the live Storyboard B render after the code-review fixes, with one segment
(`seg-05`) deliberately edited in the review YAML to an out-of-contract value
(`pause_after_seconds: 9.0` > 5.0) — the Edge #1 operator-edit scenario. The rendered
HTML now shows an explicit, visually-distinct "⚠ INVALID voice direction — will fail
synthesis" note on that segment (naming the offending `pause_after_seconds` field)
instead of a silent omission, while the other segments still render their resolved TTS
settings (reflective 0.94/0.75/0.1), the undirected segment still shows "using
global/default settings", and the global defaults header still renders. The `.yaml` +
`.html` artifacts above were overwritten with this remediation render.
