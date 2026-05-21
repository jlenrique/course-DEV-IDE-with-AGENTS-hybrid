---
name: cluster-decision-criteria
code: CD
description: Cluster decision criteria — evaluate slides for clustering using concept density, visual complexity, pedagogical weight, operator input
---

# Cluster Decision Criteria

This document defines the framework Irene uses to decide which slides in a presentation should become cluster heads, warranting supporting interstitial slides for progressive disclosure.

## Overview

Clusters are used when a single slide cannot effectively communicate a concept without overwhelming the learner or when progressive disclosure would significantly improve comprehension. The decision framework evaluates each slide against four criteria to determine if clustering is appropriate.

## Decision Criteria

### 1. Concept Density

**Definition:** The number of distinct explanatory beats or sub-concepts that must be communicated for the topic to be understood.

**High Concept Density Indicators:**
- Topic requires multiple examples or cases to illustrate
- Concept has prerequisite knowledge that needs separate explanation
- Topic involves sequential steps or processes
- Multiple perspectives or interpretations need presentation

**Low Concept Density Indicators:**
- Single, self-contained idea
- Factual information without elaboration needed
- Visual metaphor that stands alone

**Clustering Threshold:** If a slide requires 3+ distinct explanatory beats, consider clustering.

### 2. Visual Complexity

**Definition:** Whether the current slide design would benefit from decomposition, isolation, or reduction to improve comprehension.

**High Visual Complexity Indicators:**
- Multiple distinct visual elements competing for attention
- Dense text blocks that could be broken into digestible chunks
- Complex diagrams that hide important details
- Overloaded slides where elements reinforce rather than clarify
nciple
**Low Visual Complexity Indicators:**
- Clean, focused visual hierarchy
- Single dominant element with supporting context
- Well-balanced composition without cognitive overload

**Clustering Threshold:** If visual decomposition would surface important details currently hidden in complexity, consider clustering.

### 3. Pedagogical Weight

**Definition:** The concept's centrality to the learning objective and the learner burden if left undersupported.

**High Pedagogical Weight Indicators:**
- Core concept fundamental to the course/module
- Misunderstanding would block subsequent learning
- Topic represents a major transition in understanding
- High-stakes concept requiring careful scaffolding

**Low Pedagogical Weight Indicators:**
- Supporting or illustrative information
- Nice-to-know rather than need-to-know
- Concepts already familiar to the target audience
- Peripheral information that could be omitted

**Clustering Threshold:** If misunderstanding this concept would significantly impact learning outcomes, consider clustering.

### 4. Operator Input

**Definition:** Explicit direction from the content creator about clustering preferences.

**Types of Input:**
- Direct clustering request for specific slides
- Density preferences (e.g., "keep this presentation concise")
- Audience considerations (e.g., "novice learners need more support")
- Time constraints (e.g., "limit to essential clusters only")

**Framework Role:** Operator input can override algorithmic recommendations but should be evaluated against pedagogical merit. The framework should note when overrides align with or contradict the other criteria.

**Implementation:** Operator input is quantified through `CLUSTER_DENSITY` run constant and per-slide overrides. See [cluster-density-controls.md](cluster-density-controls.md) for the complete operator control schema.

## Decision Framework

### Step 1: Evaluate Each Criterion
For each slide, score against the four criteria:
- **Concept Density:** High/Medium/Low
- **Visual Complexity:** High/Medium/Low
- **Pedagogical Weight:** High/Medium/Low
- **Operator Input:** Support/Neutral/Oppose

### Step 2: Determine Clustering Level

| Criteria Combination | Recommended Action |
|---------------------|-------------------|
| 2+ High scores | Full cluster (2-3 interstitials) |
| 1 High + 2 Medium scores | Single interstitial |
| All Medium/Low scores | Remain flat |
| Operator opposes clustering | Remain flat (with rationale) |
| Operator strongly requests clustering | Single interstitial (minimum viable) |

### Step 3: Validate Cluster Fit
Before finalizing, ensure:
- The concept genuinely benefits from progressive disclosure
- Interstitials would change learner understanding, not just add decoration
- The cluster fits the overall presentation arc

## C1M1 MVP Context

For the initial three-cluster Storyboard-A proof:
- Target exactly 3 clusters for beginning, middle, and end positions
- Prioritize clusters that create a clear narrative arc: "From confusion to clarity"
- Focus on visual proof rather than narration optimization
- Select clusters that demonstrate pedagogical value of progressive disclosure

## Examples

### Cluster Head Candidate (High Scores)
**Slide:** "Cognitive Load Theory Principles"
- **Concept Density:** High (intrinsic, extraneous, germane loads)
- **Visual Complexity:** High (multiple interacting principles)
- **Pedagogical Weight:** High (fundamental to instructional design)
- **Operator Input:** Support
- **Decision:** Full cluster with interstitials isolating each load type

### Flat Slide Candidate (Low Scores)
**Slide:** "Welcome to Module 1"
- **Concept Density:** Low (single orientation message)
- **Visual Complexity:** Low (clean title slide)
- **Pedagogical Weight:** Low (administrative, not conceptual)
- **Operator Input:** Neutral
- **Decision:** Remain flat

### Borderline Case
**Slide:** "Research Methodology Steps"
- **Concept Density:** Medium (6 steps, but sequential)
- **Visual Complexity:** Medium (numbered list with icons)
- **Pedagogical Weight:** Medium (important but not core concept)
- **Operator Input:** Support
- **Decision:** Single interstitial for detailed examples

## Integration with Existing Frameworks

This criteria extends the existing pedagogical framework by adding clustering as a decomposition strategy. It complements runtime variability decisions and should be considered alongside existing timing and sequencing guidance.

## Next Step

After confirming cluster head decisions, assign narrative arc and behavioral intent per [cluster-narrative-arc-schema.md](cluster-narrative-arc-schema.md).

## Future Extensions

As clustering matures:
- Add quantitative scoring for automation
- Include audience-specific weighting
- Integrate with motion workflow decisions
- Add cluster density controls for runtime adaptation
