---
name: pass-2-grammar-riders-examples
description: Per-pattern narration-grammar worked examples for the reading-path repertoire
---

# Pass 2 narration-grammar riders — examples

This companion to [pass-2-authoring-template.md](./pass-2-authoring-template.md) carries one worked example per reading-path pattern in the v1.1 repertoire. Each example shows (a) the pattern's canonical scan order, (b) the expected narration cadence tokens, and (c) a sample `narration_text` that passes the `pass_2_emission_lint.py` pattern-aware shape check.

**Three-way parity:** the pattern headings below must stay aligned with the enum in [state/config/reading-path-patterns.yaml](../../../state/config/reading-path-patterns.yaml) and the JSON Schema enum in [state/config/schemas/segment-manifest.schema.json](../../../state/config/schemas/segment-manifest.schema.json). A parity test asserts the three stay in lockstep.

---

## Narration voice (overarching — governs every pattern below)

The reading-path pattern tells you the **order** and **emphasis** to speak in. Use that knowledge **invisibly**: narrate *about the content* like a teacher explaining the idea, in the pattern's scan order — do **not** recite the slide's geography or describe the act of looking. The listener should learn *what is true*, not *where it sits on the slide*.

- ❌ **Spatial meta-commentary (avoid):** "At the title we see…", "On the right there's an image of…", "The leftmost column shows…", "In the top-left quadrant…", "The text side carries the message…". This narrates the *map*, not the *territory*, and breaks the conversational voice.
- ✅ **Content-first voice (use):** say what the thing *means*, in the order the eye would take it, letting conceptual transitions carry the flow — "first… then…", "this builds on…", "by contrast…", "the takeaway is…". The geometry is the script writer's private guide, never spoken aloud.

**Worked contrast (same left-to-right scan order; only the second speaks to the audience):**

```text
❌  At the title we see "The Real Barrier." Below it are three boxes. The box on
    the left says clinicians have ideas; the middle box says they lack process;
    the box on the right says they lack a safe space to experiment.

✅  The real barrier isn't a shortage of ideas — clinicians generate those every
    day. What's missing is the structure to pursue them, and the psychological
    safety to experiment without fear.
```

The per-pattern **cadence tokens** below name each pattern's *ordering signature* — honor the order, but render it in this content-first voice, and **prefer the non-spatial token options** where a pattern lists them (e.g. "first/then", "by contrast", "this builds on") over the spatial ones ("the column to the right", "the text side"). Images obey their **role tier**: a *decorative* image is never narrated; an *illustrative* image is referenced only if it carries the claim; an *instructional* diagram is walked through by its **logic**, not its coordinates.

---

## Pattern: z_pattern

**Canonical scan:** top-left → top-right → bottom-left → bottom-right
**Cadence tokens (any of):** to begin / the frame / which leads to / the upshot / the takeaway / headline / body / visual
**Lint:** warning

**When to choose it:** quadrant-balanced slide with a headline, a body block, a supporting visual, and a call to action.

**Sample narration:**

```text
The headline frames the problem: clinician burnout is a systems signal. The
body beneath walks through three drivers: cognitive load, moral injury,
misaligned incentives. The visual on the right anchors the frame — a
hallway scene with the weight of the day visible. The call to action
closes: design one system-level experiment this week.
```

Cadence token hit: `headline` + `body` + `visual` + `call to action`.

---

## Pattern: f_pattern

**Canonical scan:** left-column top-down → selective right-side scan on evidence markers
**Cadence tokens (any of):** evidence / drill into / as shown / note the / data shows / callout
**Lint:** warning

**When to choose it:** text-heavy handouts, reference documents, dense prose columns with right-side evidence callouts.

**Sample narration:**

```text
Reading top-to-bottom, the left column lays out the clinical reasoning
chain. Note the second paragraph — the evidence for early diuretic
discontinuation is strong but context-sensitive. The callout at the right
margin highlights the two trials that inform this. Data shows a 19%
reduction in length-of-stay when the protocol is followed as specified.
```

Cadence token hit: `note the` + `evidence` + `callout` + `data shows`.

---

## Pattern: center_out

**Canonical scan:** establish-hero → orbit-annotations clockwise → return-to-hero
**Cadence tokens (any of):** returning to the center / back to the hero / circling back / center again / back to the main / returning to the heart
**Lint:** warning

**When to choose it:** hero graphic with orbital annotations; central concept with radial supports.

**Sample narration:**

```text
Start at the center of the graphic — the patient at the heart of the
clinical workflow. Clockwise from the top, the first annotation names the
clinician's time; the second names the EHR burden; the third names the
billing cycle; the fourth names the hand-off boundary. Each orbits the
central patient figure for a reason. Returning to the center, notice the
patient is the anchor of every upstream decision — not the product of it.
```

Cadence token hit: `returning to the center`.

---

## Pattern: top_down

**Canonical scan:** single sweep top-to-bottom following the spine
**Cadence tokens (any of):** next item / continuing down / further down / proceeding through / step by step / in order
**Lint:** warning

**When to choose it:** vertical spine; ordered lists; process ladders.

**Sample narration:**

```text
The spine runs top to bottom: intake, triage, work-up, disposition. Intake
is where the clinician first encounters the patient context. Continuing
down, triage sets the acuity and the urgency of intervention. Next item,
work-up, orders and interprets the studies that distinguish between the
top differentials. Finally, disposition commits to a path — admit,
observe, discharge.
```

Cadence token hit: `continuing down` + `next item`.

---

## Pattern: multi_column

**Canonical scan:** column-major — each column top-to-bottom before advancing right
**Cadence tokens (any of):** another facet / a separate thread / the next grouping / in parallel / a distinct angle / turning next to / separately
**Lint:** warning

**When to choose it:** 2-4 column layouts where each column is self-contained.

**Sample narration:**

```text
The diagnostic reasoning comes first: what the history suggests, what the
exam confirmed, what the imaging narrowed. A separate thread is the
treatment plan — the first-line intervention, the monitoring checkpoints,
and the stop rules. A distinct angle closes the encounter: the safety-net
plan, with return precautions, the follow-up window, and the shared
decision the patient and family make together.
```

Cadence token hit: `a separate thread` + `a distinct angle`.

---

## Pattern: grid_quadrant

**Canonical scan:** declared sweep order (row-major default; column-major if axis labels demand)
**Cadence tokens (any of):** compared to / contrast / whereas / whilst / on the other hand / vs / versus / by contrast / different from / in comparison
**Lint:** warning

**When to choose it:** 2×2 or 3×3 matrices (comparison frameworks, decision grids).

**Sample narration:**

```text
The matrix sets benefit on the vertical axis and effort on the horizontal
axis. The top-left quadrant captures the high-benefit, low-effort
interventions — the obvious starting point. Whereas the top-right
captures high-benefit, high-effort work — worth doing, but only after the
easier wins land. By contrast, the bottom-left is low-benefit, low-effort
— only worth doing if the team needs the practice. In contrast to all
three, the bottom-right is a trap: high-effort for low-benefit. Avoid it.
```

Cadence token hit: `whereas` + `by contrast` + `in contrast`.

---

## Pattern: sequence_numbered

**Canonical scan:** follow ordinal order, ignore spatial layout
**Cadence tokens (any of):** first / second / third / fourth / next / then / finally / step 1 / step 2 / step 3 / step a / step b / step c
**Lint:** **FAIL-CLOSED** — ordinal-marker absence is a contract violation

**When to choose it:** explicit ordinal markers are visible on the artifact.

**Sample narration:**

```text
Step 1 confirms the diagnosis with a focused history and exam. Step 2
initiates the first-line treatment within the 30-minute window. Step 3
orders the monitoring labs that tell you whether step 2 is working.
Finally, step 4 reassesses at the 2-hour checkpoint — escalate if the
response is inadequate, hold steady if the labs trend correctly.
```

Cadence token hit: `step 1` + `step 2` + `step 3` + `finally` + `step 4`.

---

## Pattern: split_image_text

**Canonical scan:** title-anchor on text side -> walk text structure -> reference image only by role
**Cadence tokens (any of):** the main message / the core claim / the takeaway / visual context
**Lint:** warning

**When to choose it:** side-by-side image and text where the message lives in the text and the image is contextual unless its role tier says otherwise.

**Sample narration:**

```text
The main message is the claim itself: clinicians already solve ambiguous
problems every day. The image is only visual context — it sets the scene,
so we touch it lightly and return to the point.
```

Cadence token hit: `the main message` + `visual context`.

---

## Pattern: two_up_comparison

**Canonical scan:** establish frame -> side A -> side B -> synthesis
**Cadence tokens (any of):** compared with / by contrast / on one side / on the other side
**Lint:** warning

**When to choose it:** explicit oppositional panes or nested comparison pairs.

**Sample narration:**

```text
On one side, clinical reasoning narrows uncertainty at the bedside. On the
other side, design thinking tests a solution with users. Compared with a linear
checklist, the contrast is the point: both loops learn from evidence.
```

Cadence token hit: `on one side` + `on the other side` + `compared with`.

---

## Pattern: text_hero_divider

**Canonical scan:** single-impression headline or divider beat
**Cadence tokens (any of):** pause on / single message / transition / section opener
**Lint:** warning

**When to choose it:** section openers, poster slides, and sparse CTA cards.

**Sample narration:**

```text
Pause on the single message here: this is the inflection point. As a section
opener, it gives the audience a transition before the next example.
```

Cadence token hit: `pause on` + `single message` + `section opener` + `transition`.

---

## Pattern: enumerated_process

**Canonical scan:** transform-sequence in load-bearing order
**Cadence tokens (any of):** first / then / produces / feeds / launch / iterate
**Lint:** **FAIL-CLOSED** -- process-marker absence is a contract violation

**When to choose it:** genuine process slides where the order changes meaning; numerals alone are not enough.

**Sample narration:**

```text
First, the team frames the need. That feeds a small pilot, which produces
evidence. Then the group can launch the stronger version and iterate from the
data it just created.
```

Cadence token hit: `first` + `feeds` + `produces` + `then` + `launch` + `iterate`.

---

## Pattern: diagram_driven

**Canonical scan:** establish framework -> walk load-bearing relationships -> return to claim
**Cadence tokens (any of):** framework / diagram / flow / structure / canvas
**Lint:** warning

**When to choose it:** foreground, opaque, instructional diagrams that are structurally load-bearing.

**Sample narration:**

```text
The framework starts with the learner need, moves through the canvas, and
follows the flow into the course decision. The diagram matters because the
structure shows how each choice constrains the next one.
```

Cadence token hit: `framework` + `canvas` + `flow` + `diagram` + `structure`.

---

## Parity discipline

Adding, removing, or renaming a pattern in this file requires a matching change in:

1. [state/config/reading-path-patterns.yaml](../../../state/config/reading-path-patterns.yaml) — the enum registry.
2. [state/config/schemas/segment-manifest.schema.json](../../../state/config/schemas/segment-manifest.schema.json) — the JSON Schema enum inside the `reading_path` sub-object.
3. [scripts/validators/pass_2_emission_lint.py](../../../scripts/validators/pass_2_emission_lint.py) — the `_check_reading_path_pattern` lookup.
4. [scripts/utilities/reading_path_classifier.py](../../../scripts/utilities/reading_path_classifier.py) — the `_SCORERS` mapping and `READING_PATH_PATTERNS` tuple.
5. This file — add the matching `## Pattern: <name>` heading + worked example.

The three-way parity test (`tests/contracts/test_reading_path_parity.py`) asserts registry ↔ schema ↔ headings stay in lockstep.
