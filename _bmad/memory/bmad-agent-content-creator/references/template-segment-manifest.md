---
name: template-segment-manifest
code: MG
description: Segment manifest generation — machine-readable production contract binding narration to visuals, SFX, music, composition metadata
---

# Segment Manifest Template (MG Capability)

The segment manifest is the **machine-readable production contract** for a lesson's multimedia assembly. It is produced in Pass 2 (after Gary's slides exist and the user has approved them at HIL Gate 2). It binds narration text to visual assets, SFX cues, music direction, and composition metadata. Downstream agents write back to it as they complete work.

**Canonical schema reference:** `_bmad-output/brainstorming/party-mode-composition-architecture.md`

---

## When to Produce

- Always paired with the narration script (never produced without it)
- Only in Pass 2 — requires `gary_slide_output` in the context envelope so segment IDs and `visual_file` can reference actual Gary-produced PNGs
- Optional Gary additive metadata (`literal_visual_publish`) may be present for audit context, but segment visuals still resolve from approved local `gary_slide_output` PNG paths
- Every segment in the narration script must have a corresponding manifest entry
- For segments mapped to Gary slides, populate `gary_slide_id`, `gary_card_number`, and `visual_file` from `gary_slide_output`

---

## Schema

```yaml
lesson_id: string           # e.g., C1-M1-L3
title: string               # Human-readable lesson title
music_bed: string | null    # Overall music direction: "ambient-reflective" | "upbeat-clinical" | "tense-diagnostic" | null
segments:
  - id: string              # e.g., seg-01, seg-02 (sequential, matches narration script markers)
    gary_slide_id: string | null      # slide_id from gary_slide_output when segment maps to a Gary slide
    gary_card_number: int | null      # card_number from gary_slide_output for ordering traceability
    source_ref: string      # Provenance chain: "lesson-plan.md#Block N" — traces this segment to its pedagogical origin
    narration_ref: string   # Pointer to narration script section, e.g., "narration-script.md#segment-1"
    narration_text: string  # Full narration text for this segment (copy from script)
    duration_estimate_seconds: float | null  # Irene estimate before ElevenLabs writes actual narration_duration
    timing_role: enum | null  # pedagogical role driving runtime: anchor | concept-build | evidence-walkthrough | framework-walkthrough | example | transition | reflection | checkpoint | summary | call-to-action
    content_density: enum | null  # light | medium | heavy
    visual_detail_load: enum | null  # light | medium | heavy
    duration_rationale: string | null  # concise explanation for why this slide should run shorter, average, or longer than neighbors
    onset_delay: float | null  # seconds to wait before narration starts for this segment (default 0.0)
    dwell: float | null  # seconds to hold after narration ends before transition (default 0.0)
    cluster_gap: float | null  # extra inter-segment spacing at cluster boundaries (default 0.0)
    transition_buffer: float | null  # minimum transition safety buffer in seconds (default 0.0)
    bridge_type: enum | null  # none | intro | outro | both | pivot | cluster_boundary
    behavioral_intent: string | null  # intended learner effect; when clustered it must serve master_behavioral_intent
    voice_id: string | null # ElevenLabs voice choice for this segment; null = use lesson default
    visual_cue: string      # Human-readable description of intended visual
    visual_mode: enum       # static-hold | video | text-frame | pause-beat
    visual_source: enum     # gary | kira | null
    sfx: string | null      # SFX cue name ("subtle-transition", "notification-ding") or null
    music: enum             # duck | swell | out | continue | null
    transition_in: enum     # fade | cross-dissolve | cut | none
    transition_out: enum    # fade | cross-dissolve | cut | none
     # ── Visual references from Irene Pass 2 (Story 13.3) ──
     visual_references:               # list of visual elements referenced in narration
       - element: string              # what is referenced (e.g., "comparison timeline")
         location_on_slide: string    # spatial description (e.g., "left panel")
         narration_cue: string        # exact narration phrase that references this element
         perception_source: string    # slide_id from perception_artifacts
     # ── Cluster fields from Irene Pass 2 (Story 19.1) ──
     cluster_id: string | null        # cluster identifier; null for non-clustered runs
     cluster_role: enum | null        # head | interstitial
     cluster_position: enum | null    # establish | develop | tension | resolve
     develop_type: enum | null        # deepen | reframe | exemplify (only when cluster_position == develop)
     parent_slide_id: string | null   # set on interstitials, references the head slide
     interstitial_type: enum | null   # reveal | emphasis-shift | bridge-text | simplification | pace-reset
     isolation_target: string | null  # specific element surfaced from the head slide
      narrative_arc: string | null     # one-sentence cluster arc, set on head and inherited by cluster members
      master_behavioral_intent: enum | null  # cluster-level behavioral directive (credible, alarming, provocative, reflective, moving, clear-guidance, attention-reset), set on head and inherited by cluster members
     cluster_interstitial_count: int | null  # recommended count for the cluster, 1-3
     selected_template_id: string | null     # selected cluster structure template id (e.g., deep-dive)
     double_dispatch_eligible: boolean | null  # default true, set false for interstitials in MVP
     # ── Written back by ElevenLabs agent ──
    narration_duration: float | null    # seconds
    narration_file: string | null       # relative path, e.g., "course-content/staging/C1-M1-L3/audio/seg-01.mp3"
    narration_vtt: string | null        # relative path, e.g., "course-content/staging/C1-M1-L3/captions/seg-01.vtt"
    sfx_file: string | null             # relative path to SFX clip or null
    # ── Written back by Gary or Kira ──
    visual_file: string | null          # relative path to approved still PNG (poster/reference frame)
    visual_duration: float | null       # seconds (for video segments; null for static-hold)

  # Duration precedence rule:
  # - Use duration_estimate_seconds for planning before audio generation.
  # - duration_estimate_seconds should be justified by timing_role, content_density,
  #   visual_detail_load, and duration_rationale. The estimate is not arbitrary.
  # - Once narration_duration is populated by ElevenLabs, downstream tools must treat narration_duration as authoritative.
```

---

## Field Reference

### Epic 14 Motion Addendum

Add these fields to each segment when the run uses the motion-enhanced pipeline:

```yaml
motion_type: static | video | animation
motion_asset_path: string | null
motion_source: kling | manual | null
motion_duration_seconds: float | null
motion_brief: string | null
motion_status: pending | generated | imported | approved | null
```

Default behavior remains additive and backward compatible:
- `motion_type: static`
- `motion_asset_path: null`
- `motion_source: null`
- `motion_duration_seconds: null`
- `motion_brief: null`
- `motion_status: null`

### `visual_mode` Values

| Value | Meaning | Who produces visual |
|-------|---------|---------------------|
| `static-hold` | Gary PNG displayed for narration duration | Gary |
| `video` | Animated clip (Gary PNG→Kira, or Kira original B-roll) | Kira |
| `text-frame` | Text card generated by compositor | null (compositor generates) |
| `pause-beat` | 1-2s silent visual emphasis between narration blocks | Gary or Kira (existing frame held) |

### `visual_source` Values

| Value | Meaning |
|-------|---------|
| `gary` | Gary's Gamma-generated PNG for this segment |
| `kira` | Kira-generated video clip (animation or B-roll) |
| `null` | No visual asset from an agent (text-frame, pause-beat using prior frame) |

### `timing_role` Values

| Value | Meaning | Usual runtime tendency |
|-------|---------|------------------------|
| `anchor` | Opening thesis, orientation, or identity claim | medium to long |
| `concept-build` | Introduces and unpacks a core idea | medium to long |
| `evidence-walkthrough` | Multi-part example, case, or comparison | long |
| `framework-walkthrough` | Explains a named model, sequence, or structure | medium to long |
| `example` | Concrete application or illustration | medium |
| `transition` | Moves the learner between ideas | short |
| `reflection` | Pause or interpretive beat | short to medium |
| `checkpoint` | Brief orienting recap or learner check | short |
| `summary` | Synthesis of prior ideas | short to medium |
| `call-to-action` | Closing invitation or forward pointer | short |

### `music` Values

| Value | Meaning |
|-------|---------|
| `duck` | Music present but ducked under narration (music at -30 LUFS) |
| `swell` | Music rises during visual-only or emotional beat |
| `out` | Music fades out for the segment |
| `continue` | Continue previous music behavior unchanged |
| `null` | No music for this segment |

### `motion_type` Values

| Value | Meaning | Motion asset expectation |
|-------|---------|--------------------------|
| `static` | Existing still-only pipeline | `motion_asset_path: null` |
| `video` | Kling/Kira-generated clip | approved video file required before Irene Pass 2 |
| `animation` | Manually produced animation clip | approved video file required before Irene Pass 2 |

### `motion_status` Values

| Value | Meaning |
|-------|---------|
| `pending` | Gate 2M designated, asset not ready yet |
| `generated` | Kling generated a candidate clip |
| `imported` | User imported a manual animation file |
| `approved` | Motion Gate approved the asset for Irene Pass 2 |
| `null` | Static segment, no motion lifecycle |

### Cluster Fields

| Field | Type | Nullability | Description |
|-------|------|-------------|-------------|
| `cluster_id` | string | nullable | Unique identifier for the cluster; null for non-clustered segments |
| `cluster_role` | enum | nullable | Membership role: `head` (first in cluster) or `interstitial` (supporting slides) |
| `cluster_position` | enum | nullable | Narrative position in cluster arc: `establish` (orient), `develop` (deepen/reframe/exemplify), `tension` (complicate), `resolve` (land meaning) |
| `develop_type` | enum | nullable | Sub-type for `develop` position: `deepen` (unpack), `reframe` (recontextualize), `exemplify` (illustrate) |
| `parent_slide_id` | string | nullable | For interstitials, references the head slide's `id` |
| `interstitial_type` | enum | nullable | Visual strategy: `reveal` (zoom/isolate), `emphasis-shift` (highlight one element), `bridge-text` (key phrase), `simplification` (reduce complexity), `pace-reset` (rest visual) |
| `isolation_target` | string | nullable | Specific element from head slide to surface (e.g., "working memory box") |
| `narrative_arc` | string | nullable | One-sentence emotional journey (e.g., "From confusion to clarity through progressive disclosure") |
| `master_behavioral_intent` | enum | nullable | Cluster-level behavioral directive inherited by cluster members: `credible`, `alarming`, `provocative`, `reflective`, `moving`, `clear-guidance`, or `attention-reset` |
| `cluster_interstitial_count` | int | nullable | Planned interstitial count for cluster (1-3) |
| `selected_template_id` | string | nullable | Selected cluster structure template for this cluster; copied to all cluster-member rows for traceability |
| `double_dispatch_eligible` | boolean | nullable | Whether segment can use double-dispatch; defaults true, false for interstitials in MVP |

Defaults: All null for non-clustered runs. `double_dispatch_eligible` defaults to true if null.

### Timing Buffer Fields (Story 20c-8)

| Field | Type | Nullability | Description |
|-------|------|-------------|-------------|
| `onset_delay` | float | nullable | Delay before narration starts for the segment. |
| `dwell` | float | nullable | Hold duration after narration ends before transitioning. |
| `cluster_gap` | float | nullable | Extra spacing applied when entering a new cluster boundary. |
| `transition_buffer` | float | nullable | Minimum safety buffer around transition operations. |

---

## Migration Notes (Story 19.1)

All cluster fields are additive and nullable. Existing manifests remain valid with all cluster fields absent (null). Non-clustered runs continue to work unchanged. Cluster fields are optional workflow-specific extensions, following the precedent of motion fields (Story 14.2).

---

## Eight Use Case Patterns

### UC1 — Narrated Slide Deck (most common)
```yaml
- id: seg-01
  narration_text: "The economic reality of physician practice..."
  behavioral_intent: "credible"
  voice_id: null
  visual_mode: static-hold
  visual_source: gary
  sfx: null
  music: duck
  transition_in: fade
  transition_out: cross-dissolve
```

### UC2 — Dialogue / Debate (conversation B-roll, no lip-sync)
```yaml
- id: seg-02
  narration_text: "[DR. A]: The evidence suggests consolidation improves outcomes..."
  behavioral_intent: "provocative"
  voice_id: "voice_dr_a"
  visual_mode: video
  visual_source: kira
  sfx: null
  music: duck
  transition_in: cut
  transition_out: cut
```
*Note: Multi-voice narration handled by ElevenLabs `voice_id` field per speaker.*

### UC3 — Step-by-Step Walkthrough (pause beats between steps)
```yaml
- id: seg-03
  narration_text: "First, assess the patient's chief complaint."
  behavioral_intent: "clear-guidance"
  voice_id: null
  visual_mode: static-hold
  visual_source: gary
  sfx: null
  music: duck
  transition_in: cross-dissolve
  transition_out: none
- id: seg-03-beat
  narration_text: ""        # empty — pause beat
  behavioral_intent: "attention-reset"
  voice_id: null
  visual_mode: pause-beat
  visual_source: null
  sfx: null
  music: continue
  transition_in: none
  transition_out: none
```

### UC4 — Case Study Narrative (continuous narration + music)
```yaml
- id: seg-04
  narration_text: "Meet Dr. Patel. She's reviewing a complex case..."
  behavioral_intent: "moving"
  voice_id: null
  visual_mode: video
  visual_source: kira
  sfx: null
  music: swell
  transition_in: fade
  transition_out: cross-dissolve
```

### UC5 — Assessment Prompt (deliberate silence for learner observation)
```yaml
- id: seg-05a
  narration_text: "Watch the following scenario and consider: what would you do next?"
  behavioral_intent: "provocative"
  voice_id: null
  visual_mode: static-hold
  visual_source: gary
  sfx: null
  music: out
  transition_in: cross-dissolve
  transition_out: cut
- id: seg-05b
  narration_text: ""        # deliberate silence — learner observes
  behavioral_intent: "reflective"
  voice_id: null
  visual_mode: video
  visual_source: kira
  sfx: null
  music: null
  transition_in: cut
  transition_out: cross-dissolve
```

### UC6 — Concept Explainer (tightly choreographed)
```yaml
- id: seg-06
  narration_text: "As more information pours in, the glass overflows..."
  behavioral_intent: "alarming"
  voice_id: null
  visual_mode: video
  visual_source: kira
  sfx: null
  music: duck
  transition_in: fade
  transition_out: fade
  # Advanced: sync_points populated if sub-segment timing required
  # sync_points:
  #   - word: "pours in"
  #     visual_event: water-rises
  #   - word: "overflows"
  #     visual_event: water-spills
```
*Note: sync_points is optional and used only when video is generated first (video-first timing exception).*

### UC7 — Module Bumper (template-based, short)
```yaml
- id: seg-bumper
  narration_text: "Module 3: Clinical Decision-Making."
  behavioral_intent: "attention-grabbing"
  voice_id: null
  visual_mode: video
  visual_source: kira
  sfx: "music-sting-logo"
  music: swell
  transition_in: fade
  transition_out: fade
```

### UC8 — Clustered Presentation (progressive disclosure)
```yaml
- id: seg-cluster-1-head
  narration_text: "Cognitive load theory explains how working memory limits learning..."
  behavioral_intent: "credible"
  voice_id: null
  visual_mode: static-hold
  visual_source: gary
  cluster_id: "cluster-1"
  cluster_role: "head"
  cluster_position: "establish"
  narrative_arc: "From overload awareness to capacity management through targeted interventions"
  cluster_interstitial_count: 2
  double_dispatch_eligible: true
  sfx: null
  music: duck
  transition_in: fade
  transition_out: none
- id: seg-cluster-1-int1
  narration_text: "The working memory box shows the core constraint..."
  behavioral_intent: "clear-guidance"
  voice_id: null
  visual_mode: static-hold
  visual_source: gary
  cluster_id: "cluster-1"
  cluster_role: "interstitial"
  cluster_position: "develop"
  develop_type: "deepen"
  parent_slide_id: "seg-cluster-1-head"
  interstitial_type: "emphasis-shift"
  isolation_target: "working memory capacity box"
  double_dispatch_eligible: false
  sfx: null
  music: continue
  transition_in: none
  transition_out: cross-dissolve
```
*Note: Cluster head establishes the topic; interstitials progressively disclose elements without introducing new concepts outside the head segment's instructional scope.*

---

## Downstream Consumer Notes

**ElevenLabs agent reads:**
- `narration_text` per segment — text to synthesize
- `behavioral_intent` — delivery cue for tone, pacing, and emphasis
- `timing_role`, `content_density`, `visual_detail_load`, `duration_rationale` — context for why the text was written at this length; use these for gentle delivery shaping, not for ad hoc copy rewriting
- `bridge_type` — whether the segment includes an explicit intro/outro or cluster-boundary beat that should be preserved naturally rather than flattened
- `voice_id` — per-segment voice override when present; otherwise use the lesson default from Marcus/style guide
- `sfx` — SFX cue to generate or look up
- `music` — music direction (swell/duck/out)
- Writes back: `narration_duration`, `narration_file`, `narration_vtt`, `sfx_file`

**Kira reads:**
- `visual_source: kira` segments only
- `visual_mode` — video type (animation of Gary PNG vs original B-roll)
- `narration_duration` (after ElevenLabs writes it) — clip duration target
- Writes back: motion asset fields; do not replace the approved still in `visual_file`

**Compositor reads:**
- Complete manifest (all fields populated) — generates Descript Assembly Guide
- `behavioral_intent` — assembly note so the human preserves the intended learner effect in pacing, transitions, and emphasis
- `music_bed` — overall music track to source
- `transition_in`/`transition_out` per segment — editing instructions
- `music` cues — ducking/swelling instructions

Motion-aware compositor note:
- When `motion_type != static`, compositor should use `motion_asset_path` and `motion_duration_seconds` as the assembly source for that segment instead of treating the segment as a still-only hold.
- Keep `visual_file` bound to the approved still PNG for review/poster-frame/reference use even when `motion_type != static`.

**Quinn-R reads (pre-composition validation):**
- `narration_duration` — validates WPM (130-170), checks monotonicity in VTT
- `visual_duration` vs `narration_duration` — validates ±0.5s tolerance
- Segment coverage — validates all segments have narration files
- `timing_role`, `content_density`, `visual_detail_load`, `duration_rationale` — validates whether runtime variance was pedagogically justified rather than arbitrary
- `bridge_type` — validates that explicit learner-facing intros/outros and cluster-boundary seams appear often enough to support orientation without making the lesson formulaic
- `behavioral_intent` — checks whether the artifact set appears to support the intended affective goal rather than fighting it

Quinn-R interpretation note:
- blocking findings should cover missing assets, missing coverage, non-monotonic VTT, unreadable motion assets, and material duration mismatch
- advisory findings should cover script-implied pacing variance, runtime-band drift, weak timing rationale, and bridge-cadence gaps the operator may explicitly accept

---

## Irene Production Notes

- Produce the manifest in the same task as the narration script — they are always paired
- Segment IDs must match `[SEGMENT: seg-XX]` markers in the narration script exactly
- `behavioral_intent` should be concise and action-guiding, not literary. Think "credible", "urgent", "attention-reset", "reflective", not long prose.
- In clustered runs, process segments in `cluster_id` order so the head slide establishes the frame before any interstitials elaborate it.
- In clustered runs, `behavioral_intent` must serve `master_behavioral_intent`; interstitials may modulate intensity but must not contradict the cluster's affective direction.
- `timing_role`, `content_density`, and `visual_detail_load` should explain why this slide deserves its runtime.
- `duration_rationale` must reference at least two of: pedagogical purpose, concept/detail load, visual burden.
- Use `bridge_type` sparingly but intentionally; it exists to enforce occasional connective tissue, not repetitive transition clutter.
- In clustered runs, use `cluster_boundary` on the head slide that opens a new cluster after a prior cluster; keep within-cluster interstitials at `none` unless a tension beat earns `bridge_type: pivot`.
- In clustered runs, interstitial narration should stay short, isolation-targeted, and bounded by the head segment's source-backed concept envelope.
- Do not make neighboring slides different lengths just to create variety. Runtime variance should come from content burden and rhetorical function.
- Use `voice_id` only when the segment truly needs an override (dialogue, quoted speaker, different narrator persona). Leave it `null` for the default lesson narrator.
- `visual_cue` should be descriptive enough for Gary or Kira to understand intent, but not so prescriptive that it overrides their judgment
- For `static-hold` segments referencing Gary PNGs: populate `visual_file` with the Gary-provided path from `gary_slide_output` immediately — don't leave it null
- Default every segment to `motion_type: static` unless Gate 2M explicitly designates otherwise
- For `motion_type != static`, leave `motion_asset_path` null until the motion asset is generated/imported and approved
- For `motion_type != static`, keep `visual_file` on the approved still PNG; the motion clip belongs in `motion_asset_path`, not `visual_file`
- Never replace `visual_file` with Git-host source URLs from `literal_visual_publish`; that receipt is provenance only, while composition uses approved local slide exports
- Leave ElevenLabs and Kira write-back fields (`narration_duration`, `narration_file`, etc.) as `null` — those agents populate them
- Save to `course-content/staging/{lesson_id}/manifest.yaml`
