---
name: interstitial-brief-specification
code: IB
description: Interstitial brief specification standard — constrained 6-field briefs for Gamma cluster interstitials preserving head-slide lineage
---

# Interstitial Brief Specification Standard

**Purpose:** This document defines the strict contract for interstitial briefs sent to Gary during cluster production. Interstitials are supporting slides that remove, isolate, enlarge, or simplify content from the head slide rather than introducing new imagery or concepts. This standard ensures Gamma receives constrained, coherent instructions that preserve head-slide lineage.

**Scope:** Applies to all cluster interstitial briefs in C1M1 MVP and future cluster implementations. This is the authoritative contract that Irene Pass 1 cluster planning (Epic 20b), Gary dispatch work (Epic 21), and cluster narration (Epic 23) must honor.

## Required Brief Fields

Every interstitial brief must specify all six fields with concrete, actionable values. Vague or missing fields render the brief unusable.

### 1. `interstitial_type`

**Acceptable Values:** `reveal` | `emphasis-shift` | `bridge-text` | `simplification` | `pace-reset`

**Intent:** Classifies the form of the interstitial slide. This value determines the visual grammar and the constraints Gary applies during Gamma generation. It is the same field defined in the segment manifest schema.

| Value | Visual Form | When to Use |
|-------|------------|-------------|
| `reveal` | One element from head surfaced at larger scale or with annotation; same visual DNA as head | Head content is too dense to read; one element deserves full-frame treatment |
| `emphasis-shift` | One point isolated with typographic weight; others fade or disappear | Head lists multiple points; cluster develops exactly one of them |
| `bridge-text` | Single phrase, statistic, or quote in large type; atmospheric background from head only; no new imagery | A key claim needs to land before the next narrative beat |
| `simplification` | Strip information-dense head to one data series or element; cognitive load deliberately drops | Head slide is information-dense; interstitial provides visual relief |
| `pace-reset` | Near-blank or icon-only visual rest; used after dense clusters or before next head | Learner needs a breath before the next concept; pacing demands a pause |

**Quality Bar:** Must be one of the five enumerated values. Do not invent new types or use operational verbs (`isolate`, `remove`, `enlarge`) — those describe what the visual operation does; `interstitial_type` classifies what kind of slide the interstitial is.

**Failure Example:** `interstitial_type: "isolate"` — not a valid value. If the intent is to surface one element from the head, use `reveal`.

### 2. `isolation_target`

**Acceptable Values:** Specific string description of element/concept from head slide (e.g., "the working memory box in the cognitive load diagram", "the third process step", "the 47% statistic in the bar chart").

**Intent:** Identifies the exact content from the head slide that the interstitial focuses on or transforms.

**Quality Bar:** Must point to actual content present in the head brief or head slide concept. Adjectives alone ("the important part", "the main idea") fail — use positional or named references.

**Failure Example:** "The important part" — generic, does not specify which element.

### 3. `visual_register_constraint`

**Acceptable Values:** String list of specific elements to remove/suppress/deemphasize (e.g., `["suppress intrinsic and germane load components", "remove surrounding labels"]`).

**Intent:** Defines what must be eliminated or reduced to achieve the interstitial's purpose. Operations are subtractive — the constraint removes or suppresses, it does not add.

**Quality Bar:** Must list specific named elements. "Clean it up" or "simplify" are not constraints.

**Failure Example:** `["make it nice"]` — doesn't specify what to remove.

### 4. `content_scope`

**Acceptable Values:** `minimal` (1–2 elements) | `focused` (3–4 elements) | `reduced` (simplified version of head, more than 4 elements removed).

**Intent:** Limits the maximum on-screen content burden so Gary knows the density ceiling for the slide.

**Quality Bar:** Must specify scope level, preventing overcrowding. `minimal` is the default target for `reveal` and `pace-reset` types.

**Failure Example:** Undefined — allows unlimited elements, defeating the interstitial's purpose.

### 5. `narration_burden`

**Acceptable Values:** `low` | `medium` | `high` — measures how much of the explanatory burden falls on narration.

| Value | Meaning | Narration feels like... |
|-------|---------|------------------------|
| `low` | Visuals carry most meaning; narration is light and commentarial | One clause, a rhetorical question, or a single observation *(target for interstitials: visual ~70%, narration ~30%)* |
| `medium` | Both channels share the work; neither can be removed without loss | Two to three sentences; visual and voice are equal partners |
| `high` | Narration carries most explanatory load; visuals are minimal or ambient | Dense explanation over a sparse or atmospheric visual — appropriate for `bridge-text` and `pace-reset` types |

**Intent:** Determines the visual-audio explanatory division so Gary knows how much semantic weight the slide must carry on its own.

**Quality Bar:** Must be one of the three values. Default for `reveal`, `emphasis-shift`, and `simplification` types: `low` — the visual should do most of the work. `bridge-text` and `pace-reset` may use `high`.

**Failure Example:** Unspecified — leaves visual-audio balance ambiguous, producing slides that are over-labeled or under-designed.

### 6. `relationship_to_head`

**Acceptable Values:** `zoom` (closer view of one element) | `isolate` (extract element, suppress context) | `simplify` (remove distractions, reduce density) | `reframe` (different compositional angle) | `rest` (complementary visual breath).

**Intent:** Describes the spatial/compositional relationship between this interstitial and the head slide. Independent of `interstitial_type` — the type classifies the slide form; this field describes its stance relative to the head.

**Quality Bar:** Must specify one of the five relationships. "Continue the topic" fails — it describes content, not composition.

**Failure Example:** "Continue the topic" — does not define the slide's compositional relationship to the head.

---

## Interstitial Principles

- **Lineage Preservation:** Interstitials transform existing head content; they do not introduce new concepts, imagery, or iconography.
- **Simplification Focus:** Operations are subtractive (remove/isolate) or focused (enlarge/simplify/reframe), not additive.
- **Pedagogical Intent:** Each interstitial must serve a clear explanatory purpose in the cluster sequence.

---

## Examples

### Pass/Fail Examples by Type

#### `reveal`

**Pass:**
```
interstitial_type: "reveal"
isolation_target: "the working memory box in the cognitive load diagram"
visual_register_constraint: ["suppress intrinsic and germane load components", "remove surrounding labels", "enlarge isolated element to full-frame"]
content_scope: "minimal"
narration_burden: "low"
relationship_to_head: "zoom"
```

**Fail:** `interstitial_type: "reveal"`, `isolation_target: "something important"`, `visual_register_constraint: ["make it bigger"]` — target is non-specific and not traceable to head content; constraint is vague.

---

#### `emphasis-shift`

**Pass:**
```
interstitial_type: "emphasis-shift"
isolation_target: "the third process step in the six-step workflow"
visual_register_constraint: ["fade steps 1–2 and 4–6 to 20% opacity", "suppress step labels except step 3", "remove surrounding decorative icons"]
content_scope: "focused"
narration_burden: "low"
relationship_to_head: "isolate"
```

**Fail:** `interstitial_type: "emphasis-shift"`, `isolation_target: "the key step"`, `visual_register_constraint: ["make others less prominent"]` — target is relative, not positional; constraint is not measurable.

---

#### `bridge-text`

**Pass:**
```
interstitial_type: "bridge-text"
isolation_target: "the central claim from the head slide: 'Extraneous load is the only load we can control'"
visual_register_constraint: ["remove all diagrams and data tables", "remove all icons", "use head slide atmospheric background only — no new imagery"]
content_scope: "minimal"
narration_burden: "high"
relationship_to_head: "reframe"
```

**Fail:** `interstitial_type: "bridge-text"`, `isolation_target: "a quote"` — no source specified; which quote, from which slide element? Constraints missing entirely.

---

#### `simplification`

**Pass:**
```
interstitial_type: "simplification"
isolation_target: "the extraneous load column in the cognitive load comparison table"
visual_register_constraint: ["remove intrinsic load and germane load columns", "suppress row headers", "retain only the extraneous load data series and its axis label"]
content_scope: "reduced"
narration_burden: "low"
relationship_to_head: "simplify"
```

**Fail:** `interstitial_type: "simplification"`, `visual_register_constraint: ["make it simpler"]` — `isolation_target` missing entirely; constraint is generic and non-subtractive.

---

#### `pace-reset`

**Pass:**
```
interstitial_type: "pace-reset"
isolation_target: "single icon representing the module theme (e.g., the agent network glyph used in the head slide)"
visual_register_constraint: ["remove all text", "remove all diagrams and data", "use head slide color palette undertone only — no new hues"]
content_scope: "minimal"
narration_burden: "high"
relationship_to_head: "rest"
```

**Fail:** `interstitial_type: "pace-reset"`, `isolation_target: "the slide content"` — too broad; a pace-reset by definition has near-zero content. An isolation target this vague gives Gary no guidance on what single visual anchor to retain.

---

### C1M1 MVP Example

**Head Slide Context:** C1M1 slide showing a complex agent interaction diagram with multiple components, labels, and connecting arrows.

**Interstitial Brief:**
```
interstitial_type: "reveal"
isolation_target: "the central agent communication loop"
visual_register_constraint: ["remove all component labels", "suppress peripheral agents", "eliminate connecting arrows outside the central loop"]
content_scope: "minimal"
narration_burden: "low"
relationship_to_head: "zoom"
```

**Purpose:** Focuses Storyboard A review on the core interaction pattern without visual overload, helping viewers understand the fundamental communication mechanism before adding complexity in subsequent slides. The visual does the work — narration adds a single observation at most.

---

## Implementation Contract

This standard is binding for:
- Irene Pass 1 cluster planning (Epic 20b) — Irene must produce briefs that meet this standard before Gary dispatch fires
- Gary dispatch contract extensions (Epic 21)
- Cluster coherence validation (Epic 21)
- Irene Pass 2 narration integration (Epic 23)
- All future cluster implementations

Any deviation requires explicit approval and standard updates.
