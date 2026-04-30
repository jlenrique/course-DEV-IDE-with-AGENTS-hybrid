# Runtime Variability Framework for Irene Pass 2

Runtime variation across slides must be intentional and defensible.
Irene should not distribute narration time by instinct alone, and should not
equalize scripts when the lesson plan calls for meaningful variation.

## Core Rule

Longer slides must earn their time through instructional need.
Shorter slides must stay short because their role is lighter.

The primary driver of runtime variability is the writing itself.
Voice direction and TTS pacing are secondary refinements, not the main source
of slide-length differences.

## Decision Inputs Per Slide

For each slide, Irene should assess all of the following before she delegates
or approves prose:

1. `timing_role`
   What rhetorical job the slide performs in the lesson.

2. `content_density`
   How much conceptual or procedural material must be unpacked for the learner.

3. `visual_detail_load`
   How much meaning is carried by the slide itself and therefore needs guided
   narration rather than a quick pass.

4. `duration_rationale`
   A brief statement explaining why this slide should be shorter, average, or
   longer than neighboring slides.

5. `bridge_type`
   Whether this slide carries an explicit learner-facing intro, outro, both,
   or none. When non-`none`, the **spoken narration** (not only YAML) must
   include matching connective language; see `spoken-bridging-language.md`
   and `pedagogical_bridging.spoken_bridge_policy` in `narration-script-parameters.yaml`.

## Timing Role Definitions

Use one primary role per slide.

| Role | Typical Use | Runtime Bias |
|------|-------------|--------------|
| `anchor` | opening claim, identity shift, thesis setup | medium to long |
| `concept-build` | unpacking a central idea learners must carry forward | medium to long |
| `evidence-walkthrough` | multi-part examples, cases, or comparisons | long |
| `framework-walkthrough` | stepwise explanation of a named model or structure | medium to long |
| `example` | illustrative application or concrete scenario | medium |
| `transition` | bridge between ideas or sections | short |
| `reflection` | pause, invitation, or interpretive beat | short to medium |
| `checkpoint` | orienting recap, learner check, or framing marker | short |
| `summary` | synthesis of already-covered material | short to medium |
| `call-to-action` | closing prompt or forward pointer | short |

## Density Scale

| Level | Meaning |
|-------|---------|
| `light` | single idea, minimal unpacking needed |
| `medium` | one important idea with supporting explanation or comparison |
| `heavy` | layered concepts, multiple steps, or dense abstraction requiring careful narration |

## Visual Detail Load Scale

| Level | Meaning |
|-------|---------|
| `light` | simple hero image, sparse text, or low visual decoding burden |
| `medium` | some labels, a moderate number of elements, or a meaningful visual comparison |
| `heavy` | complex illustration, diagram, roadmap, text-heavy slide, or multi-part visual logic |

## Authoring Rule

When two slides have similar source importance, the one with heavier
conceptual or visual decoding burden should usually receive the longer script.

Do not add words just to hit a clock target.
Instead, add the right kind of language:
- concept unpacking
- clinical implication
- guided comparison
- interpretive framing
- transitions that help the learner make meaning

Do not bloat short slides with filler just to create superficial variance.

## Required Rationale Pattern

Each segment should include a concise `duration_rationale` that references at
least two of the following:
- the slide's pedagogical purpose
- the amount of conceptual detail being unpacked
- the amount of visual detail or illustration burden on the slide

Good examples:
- "Longer than average because this framework-walkthrough slide introduces a new model and the roadmap graphic carries multiple labeled steps that need guided unpacking."
- "Shorter transition slide because its purpose is only to pivot from examples to the underlying principle; the visual is simple and does not need extended explanation."
- "Medium-length reflection beat because the idea is emotionally important, but the slide is visually sparse and should leave room for the learner to absorb the point."

Weak examples:
- "Long slide because it feels important."
- "Short because not much to say."
- "Average timing."

## Bridge Cadence

Learners benefit from periodic connective tissue, but not from robotic
transition language on every slide.

Use a configurable cadence rule (authoritative values live in
`runtime_variability.bridge_cadence` inside `narration-script-parameters.yaml`):
- include at least one brief explicit slide intro or outro every `X` minutes
- or after every `Y` slides
- when clustered presentations are active and `cluster_bridge_cadence_override`
  is true, prefer `bridge_type: cluster_boundary` at seams between clusters;
  the slide/minute caps remain upper bounds if no seam occurs in time

Recommended default:
- every `3.0` minutes or `5` slides

Cadence caps may change per production run; Irene must read the active YAML
each Pass 2. **Verbosity** of each bridge (short clause vs fuller beat) is
modulated separately via `pedagogical_bridging.bridge_frequency_scale`.

Use explicit bridges when they help the learner:
- re-orient after several dense slides
- shift from examples to framework
- move from concept to application
- mark a new instructional phase

Do not force a bridge on every slide.
Too much connective language can make the lesson sound formulaic.

`bridge_type` values:
- `none`
- `intro`
- `outro`
- `both`
- `cluster_boundary`

Clustered-run rule:
- cluster heads may use `cluster_boundary` when entering a new cluster after a
  prior cluster or flat segment
- within-cluster interstitials default to `bridge_type: none`
- only `cluster_position: tension` may carry a brief pivot beat inside a
  cluster; do not normalize that into routine bridge language

Good uses:
- a brief intro when a new slide reframes the previous idea
- a brief outro when the current slide needs to hand the learner cleanly into a new section
- `both` only when the segment truly performs both jobs without sounding mechanical

## Review Rule

When reviewing delegated prose, Irene should ask:
- Does the word budget fit the slide's role?
- Is this detail level justified by learner need?
- Is the slide visually dense enough to warrant more guided narration?
- If this slide is longer than its neighbors, can I explain why in one sentence?

If not, revise the delegation brief or the script before handoff.
