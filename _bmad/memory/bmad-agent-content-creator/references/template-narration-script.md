# Narration Script Template

**Pass 2 artifact** - produced after Gary's slides are approved at HIL Gate 2. Always paired with a segment manifest (`template-segment-manifest.md`). Segment IDs in this script must exactly match the manifest entries.

Grounding rule: narration is grounded on approved Gary slide PNGs from `gary_slide_output` plus source references. If `literal_visual_publish` is present, treat it as provenance/audit context only (not as the visual truth source for narration).

## Header

- **Lesson Plan Reference:** LP-{module_id}{lesson_id}
- **Script ID:** NS-{module_id}{lesson_id}-{sequence}
- **Paired Slide Brief:** SB-{module_id}{lesson_id}-{sequence}
- **Paired Segment Manifest:** `course-content/staging/{lesson_id}/manifest.yaml`
- **Learning Objective:** {specific objective this narration serves}
- **Bloom's Level:** {level}
- **Pass:** 2 (written after Gary's slides reviewed and approved)

## Script Body

For each slide/segment - segment IDs must match `[SEGMENT: seg-XX]` markers exactly:

---

[SEGMENT: seg-01]

**[Gary Slide: {gary_slide_id} - {visual_description from gary_slide_output}]**
**Source Reference:** `source_ref: {lesson-plan.md#Block N}` | `slide_ref: SB-{id}#Slide {N}` - traces this narration segment to its source in the lesson plan and paired slide

**Stage Directions:**
- Tone: {conversational clinical | formal academic | empathetic narrative}
- Pacing: {measured/deliberate | conversational flow | building urgency}
- Emphasis: {key phrases to stress, marked with *asterisks*}
- Behavioral Intent: {credible | moving | alarming | urgent | reflective | attention-reset | provocative}
- Cluster Role: {none | head | interstitial}
- Cluster Position: {none | establish | develop | tension | resolve}
- Master Behavioral Intent: {nullable; when clustered, segment intent must serve this cluster-level directive}
- Timing Rationale: {why this slide should run shorter, average, or longer than nearby slides; tie to slide purpose, content density, and/or visual burden}
- Bridge Type: {none | intro | outro | both | pivot | cluster_boundary} — when not `none`, the **Narration** body below must include learner-heard connective language that matches the configured spoken-bridge patterns in `narration-script-parameters.yaml` (see `references/spoken-bridging-language.md`). `pivot` is reserved for brief tension turns inside a cluster; `cluster_boundary` is the two-sentence seam between clusters.

**Visual References** (Story 13.2 - from `visual_reference_injector`):
```yaml
visual_references:
  - element: "{description from perception_artifacts.visual_elements}"
    element_type: "{type - chart, table, diagram, image, text, etc.}"
    location_on_slide: "{position - left panel, center, top-right, etc.}"
    narration_cue: "{exact phrase in narration that references this element}"
    perception_source: "{slide_id from perception_artifacts}"
```

**Narration:**
{The actual narration text, written by Paige or Sophia, reviewed for pedagogical alignment.
Complement the visual - narrate the insight, not the structure. If Gary's slide shows a
three-column comparison, narrate "Notice how the revenue gap widens in each decade" not
"This slide shows three columns."
Weave `visual_references_per_slide` (default 2, +/-1 tolerance) explicit visual references
into the narration flow. Each reference must name a specific visual element from
perception_artifacts and include spatial context only when it helps the learner orient.
References guide the learner's eye - they do not annotate.
For clustered runs, head segments should carry the fuller explanation and establish the cluster frame.
Interstitials should stay terse, visually complementary, and isolation-targeted: assume the slide carries most of the meaning and the narration supplies the missing interpretation.
Do not introduce new concepts in an interstitial that are outside the head segment's instructional scope.
Keep the narration audience-directed. Prefer phrasing like "Notice how...", "Here, you can see...",
"What matters for clinicians is...", or direct role-address. Avoid production-meta phrasing such as
"the slide title", "the panel on the right", "the box on the left", or "the approved slide" unless
brief spatial disambiguation is genuinely necessary.
When **Bridge Type** is `intro`, `outro`, `both`, `pivot`, or `cluster_boundary`, this block must include natural spoken
bridging lines (section orient, handoff, summary stitch, or brief tonal turn) consistent with
`pedagogical_bridging.spoken_bridge_policy` — the manifest tag alone is not sufficient for TTS.}

**Transition to next segment:**
{How this segment connects to the next - pedagogical bridge}

---

[SEGMENT: seg-02]

**[Gary Slide: {gary_slide_id} - {visual_description}]** (or **[Kira B-roll: {description}]**)

...repeat for each segment...

---

## Downstream Consumption - ElevenLabs

- **Suggested Voice ID:** {voice from style guide or learned preference}
- **Estimated Duration:** {word count / 130-170 wpm = minutes (planning estimate only; narration_duration from ElevenLabs is authoritative)}
- **Pronunciation Guide:**
  | Term | Pronunciation |
  |------|--------------|
  | {medical term} | {phonetic guide} |
- **Audio Notes:** {voice style notes, SFX cues per segment, music bed direction}
- **Intent Note:** The delivery should reinforce the segment's `behavioral_intent`, not just read the words correctly.

## Downstream Consumption - Segment Manifest

Every `[SEGMENT: seg-XX]` marker must have a corresponding entry in the paired manifest.yaml.
Irene populates `narration_text` and `visual_cue` in the manifest from this script.
Irene should also preserve the segment's timing rationale in the paired manifest so runtime variance remains auditable downstream.
When a segment includes an explicit intro/outro, Irene should preserve that as `bridge_type` in the manifest so bridge cadence remains auditable downstream.
ElevenLabs writes back `narration_duration`, `narration_file`, `narration_vtt` after generation.
