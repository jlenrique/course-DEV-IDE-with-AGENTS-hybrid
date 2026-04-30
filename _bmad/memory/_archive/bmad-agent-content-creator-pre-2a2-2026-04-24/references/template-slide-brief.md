# Slide Brief Template

**Pass 1 artifact** — produced before Gary generates slides. This brief tells Gary what each slide needs to accomplish pedagogically. Irene writes narration *after* Gary generates slides (Pass 2), ensuring narration complements Gary's actual output. Do not pre-write narration in this brief.

## Header

- **Lesson Plan Reference:** LP-{module_id}{lesson_id}
- **Brief ID:** SB-{module_id}{lesson_id}-{sequence}
- **Narration Script (Pass 2 — produced after Gary):** NS-{module_id}{lesson_id}-{sequence}
- **Learning Objective:** {specific objective this slide serves}
- **Bloom's Level:** {level}
- **Pass:** 1 (input to Gary's generation; narration written after Gary's output reviewed)

## Slide Specifications

### Slide {N}

**Fidelity:** {creative | literal-text | literal-visual} — default is `creative`. See Fidelity Classification below.
**Fidelity Rationale:** {why this classification — required for literal-text and literal-visual only}
**Source Image:** {path to SME source image — required for literal-visual only, e.g., "TEJAL_Notes.pdf#page7"}
**Visual Treatment:** {user-rebranded — for literal-visual only. User processes in Gamma Imagine, exports 16:9 PNG}

**Content:**
{Primary text content for this slide — what appears on screen}

**Source Reference:** `source_ref: {lesson-plan.md#Block N}` — traces this slide's content to its origin in the lesson plan

**Visual Guidance:**
- Layout: {two-column parallel | title-plus-body | three-column cards | data visualization | full-bleed image}
- Hero Element: {what draws the eye first}
- Visual Density: {minimal/sparse | balanced | data-rich}
- Image Guidance: {description of needed visual, or "no image — text focus"}

**Learning Purpose:**
{Why this slide exists in the sequence — what cognitive step it serves}

**Behavioral / Affective Intent:**
{What the slide should make the learner feel or do next — credible, sobering, urgent, attention-grabbing, reflective, reassuring, etc.}

## Fidelity Control (per slide — deterministic vocabulary for literal slides)

For `literal-text` and `literal-visual` slides, these fields replace free-text `additionalInstructions`:

- `text_treatment`: {generate | preserve | preserve-strict} — maps to Gamma `textMode`
- `image_treatment`: {ai-generated | no-images | theme-accent | user-provided} — maps to Gamma `imageOptions.source`
- `layout_constraint`: {single-column | two-column | full-bleed-image | data-table | unconstrained} — maps to structured `additionalInstructions` templates
- `content_scope`: {exact-input-only | guided-enhancement | creative-freedom} — controls embellishment behavior

For `creative` slides, `additionalInstructions` free-text remains available. For literal slides, `additionalInstructions` must be empty — constraints are expressed through the vocabulary above.

## Downstream Consumption — Gary (Gamma)

- **Suggested Parameters:**
  - `numCards`: {count}
  - `textMode`: {derived from text_treatment vocabulary above, or explicit for creative slides}
  - `textOptions.amount`: {brief | medium | detailed}
  - `additionalInstructions`: {creative guidance only — prohibited for literal slides; use fidelity-control vocabulary instead}
  - `imageOptions.source`: {derived from image_treatment vocabulary above, or explicit for creative slides}
- **Format:** presentation
- **Export:** PNG (production) or PDF (review)
- **Pairing Note:** Narration script NS-{id} is produced in Pass 2 *after* Gary's slides are approved. Gary uses this brief to generate slides; Irene then writes narration that complements what Gary actually produced.
- **Intent Note:** Gary should explicitly assess whether the generated slide matches the intended behavioral/affective effect before recommending approval at Gate 2.
- **Downstream Kira:** segments that need video animation should note `visual_mode: video` suggestion here so Kira knows which slides to animate after ElevenLabs provides durations.
  - `visual_mode`: static-hold | video (suggestion for segment manifest)
  - `visual_source`: gary | kira (suggestion)

## Fidelity Classification Guide

Irene assigns fidelity class per slide based on source material analysis and user `fidelity_guidance` (from Marcus's production-start interview). Default is `creative`. Do not over-apply literal tagging — most slides should be creative.

| Class | When to Apply | Examples | Gamma Treatment |
|-------|--------------|---------|----------------|
| **creative** (default) | Content can be creatively enhanced by Gamma | Concept explanations, thematic overviews, narrative slides | `textMode: generate`, standard AI images |
| **literal-text** | Exact text/data must appear as written on the slide | Assessment topic lists, specific statistics, accreditation terminology, drug dosage tables | `textMode: preserve`, `imageOptions.source: noImages`, strict embellishment constraints |
| **literal-visual** | A specific SME-provided image must be faithfully placed on the slide | Clinical flowcharts, data visualizations with labeled data series, framework diagrams, rebranded SME diagrams | `textMode: preserve`, user-provided image URL inline in `inputText` |

**Source signals for literal classification:**
- "Knowledge Check" or "Assessment" headings → likely `literal-text`
- Tables with specific numbers, dates, or dosages → likely `literal-text`
- Figures with labeled axes, named data series, or process steps → likely `literal-visual`
- Accreditation standards or regulatory text that must be quoted → `literal-text`

**User `fidelity_guidance` overrides Irene's defaults.** If the user explicitly marks content as literal or creative during Marcus's fidelity discovery, Irene follows the user's classification. Irene may independently identify additional literal needs from her own analysis — user guidance supplements, not replaces, Irene's judgment.
