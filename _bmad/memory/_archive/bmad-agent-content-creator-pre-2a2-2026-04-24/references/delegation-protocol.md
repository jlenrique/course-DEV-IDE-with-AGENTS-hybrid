---
name: delegation-protocol
code: WD
description: Writer delegation protocol — select writer, compose brief, review returns, manage revision rounds
---

# Writer Delegation Protocol

How Irene selects writers, composes briefs, reviews returns, and manages revision rounds.

## Writer Selection Matrix

Select the BMad writer based on content type and pedagogical purpose:

| Content Type | Pedagogical Purpose | Writer | Rationale |
|-------------|-------------------|--------|-----------|
| Procedure steps, protocol explanations | Structured comprehension (Remember/Understand) | **Paige** | Precision and clarity for technical material |
| Data-driven explanations, mechanism descriptions | Technical understanding (Understand/Apply) | **Paige** | Accuracy and structured logic for complex data |
| Case study dialogues, patient vignettes | Clinical reasoning engagement (Analyze/Evaluate) | **Sophia** | Narrative tension and emotional engagement |
| First-person clinical explainers | Expert perspective immersion (Apply/Analyze) | **Sophia** | Authentic voice and experiential storytelling |
| Scenario-based decision points | Evaluative judgment (Evaluate/Create) | **Sophia** | Dramatic structure around choice moments |
| Slide narrative design, visual flow advice | Visual communication (any Bloom's level) | **Caravaggio** | Visual hierarchy and audience attention expertise |
| Slide-script pairing, presentation structure | Multi-modal coherence (any Bloom's level) | **Caravaggio** | Cross-medium design integration |

When content spans multiple types (e.g., a lesson plan with both technical procedures and case narratives), split into separate delegation briefs — one per writer. Irene assembles the pieces after review.

## Delegation Brief Structure

Every brief to a BMad writer includes ALL of the following:

### Required Fields

- **Learning Objective** — The specific measurable objective this content serves. Verbatim from course context.
- **Bloom's Level** — Which cognitive level: Remember, Understand, Apply, Analyze, Evaluate, Create. Determines tone and depth.
- **Audience Profile** — Who reads/hears this: attending physician, resident, medical student, nursing professional. Determines vocabulary and assumed knowledge.
- **Pedagogical Intent** — WHY this content exists in the learning arc. What cognitive shift should the learner experience?
- **Format Constraints** — Structure requirements: word count range, section count, paragraph density, whether dialogue or narration, etc.
- **Key Terminology** — Medical/clinical terms that MUST appear in the output. These are non-negotiable vocabulary anchors.
- **Source Reference** — `source_ref` citation tracing this brief to its origin in the source bundle or lesson plan. Format: `{filename}#{path_expression}` (see `docs/source-ref-grammar.md`). Required for every content field that carries pedagogical assertions.
- **Runtime Intent** — For Pass 2 narration, specify the slide's timing role, expected detail density, and whether the visual is light, medium, or heavy to decode.

### Optional Fields

- **Emotional Arc** (Sophia only) — Tension → resolution pattern, empathy anchors, character development beats.
- **Character Profiles** (Sophia only) — Patient demographics, clinician specialty, relationship dynamics for case studies.
- **Visual Hierarchy** (Caravaggio only) — Hero element per slide, attention flow, density targets.
- **Slide-Script Pairing** (Caravaggio only) — Which narration script this pairs with, synchronization requirements.
- **Length Constraints** — Estimated word count, slide count, or duration target.
- **Timing Rationale** — Why this piece should be shorter, average, or longer than neighboring slides, tied to purpose, detail load, or visual complexity.
- **Tone Guidance** — From style bible voice standards. Formal academic vs. clinical conversational vs. empathetic narrative.
- **Existing Content Refs** — Related artifacts already produced for cross-reference consistency.

## Review Process

### Step 1: Receive drafted prose from writer

### Step 2: Invoke editorial review
- `bmad-editorial-review-prose` on individual pieces (every time)
- `bmad-editorial-review-structure` on assembled multi-piece artifacts (when combining)

### Step 3: Pedagogical quality review (PQ capability)
Check the edited draft against these criteria:
- Does it serve the stated learning objective?
- Is the Bloom's level appropriate for the content's cognitive demand?
- Does the cognitive load fit within working memory constraints?
- Does it flow correctly in the content sequence?
- Does it enforce the asset-lesson pairing invariant (every artifact paired with instructional context)?

### Step 4: Accept or revise
- **Aligned:** Incorporate into the output artifact template. Add downstream consumption annotations.
- **Misaligned:** Provide constructive pedagogical feedback specifying WHAT is misaligned, WHY it matters for learning, and HOW to adjust. Re-delegate to the same writer with the feedback.

### Revision Limits
- Maximum 2 revision rounds per content piece per writer
- After 2 rounds: escalate to Marcus with misalignment details and suggest alternative writer or direct user input
- Never silently accept misaligned content to avoid delays

## Downstream Consumption Annotations

After assembly, annotate each artifact with consumption notes for the downstream specialist:

| Artifact Type | Consumer | Annotations Required |
|--------------|----------|---------------------|
| Narration Script | ElevenLabs | Suggested voice ID, estimated duration (word count ÷ 150 wpm), pronunciation guides for medical terms, pacing/emphasis stage directions |
| Dialogue Script | ElevenLabs | Speaker labels with voice assignments, turn timing, emotional tone per line |
| Slide Brief | Gary (Gamma) | Suggested numCards, textMode, visual density, image guidance, additionalInstructions hints |
| Assessment Brief | Qualtrics | Question type (MC, matching, ordering), Bloom's level tag, distractor rationale |
| Lesson Plan | All specialists | Module/lesson position, learning objective map, content sequence, timing estimates |
| First-Person Explainer | ElevenLabs | Voice character profile, pacing notes, clinical terminology pronunciation |

For Pass 2 narration, Irene should also preserve a slide-level runtime rationale in the paired segment manifest so downstream review can tell whether runtime variance was earned by pedagogy rather than improvised.

## Cluster Interstitial Briefs

When producing briefs for Gary's cluster interstitials (not standard slide briefs), Irene must follow the interstitial brief specification standard (`./references/interstitial-brief-specification.md`). These briefs are structured contracts with 6 required fields (`interstitial_type`, `isolation_target`, `visual_register_constraint`, `content_scope`, `narration_burden`, `relationship_to_head`) to ensure Gamma receives constrained, coherent instructions that preserve head-slide lineage. Vague briefs lead to decorative slides; use the standard's examples and quality bars to maintain pedagogical intent.
