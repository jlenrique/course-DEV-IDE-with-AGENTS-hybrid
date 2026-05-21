# Dials Spec — Companion to `marcus/lesson_plan/schema.py`

> **Authority of record**: `schema.py` is authoritative for shape + validators; this doc is authoritative for operator-facing wording + interaction prose. If they drift, the schema wins structurally; this doc wins on user-facing language.

This companion artifact documents the two operator-set dials carried on every
in-scope (or delegated) plan unit, their default behaviour, and how they
interact with the source-fitness signal. Ship date: 2026-04-18, story 31-1.

Dials are the course author's voice inside the Lesson Plan. They tell the
production pipeline "lean in this much" without requiring a form picker — the
course author's own sentence becomes the rationale, and these two dials
capture the numeric dimension of that lean.

## Dial: enrichment

**Range:** 0.0 (no enrichment) to 1.0 (maximum depth beyond source).
**Default:** `default: null` — when the dial is unset, the production-side
counterparty treats the unit as "source-faithful" with no aspirational
depth added. A value of 0.0 means the course author explicitly said
"stick to the source." A value near 1.0 means "go deep — we want
context beyond what the source alone carries."

Enrichment is the **aspirational depth** parameter family. It is NOT
gap-filling (which is a separate operation, expressed via
`IdentifiedGap.suggested_posture == "gap_fill"`). It is NOT evidence-bolster
(which is the corroboration dial below).

**Example:** an instructor teaching Robert Gagné's event-3 ("stimulate recall
of prior learning") sets `enrichment: 0.65` because the SME outline mentions
prior-learning recall in passing but the course author wants richer
examples — e.g. two analogies per core concept instead of one.

## Dial: corroboration

**Range:** 0.0 (no corroboration) to 1.0 (heavy cross-validation).
**Default:** `default: null` — when the dial is unset, production treats
existing source claims as-is without seeking evidence beyond what the SME
provided. A value of 0.5 means "spot-check the strongest claims"; a value
near 1.0 means "cross-validate every assertion that a learner might
push back on."

Corroboration is the **evidence-bolster** parameter family. It is about
strengthening existing claims with secondary sources, not adding new
content. Tracy dispatches corroborate queries for this dial via the
scite.ai provider (supporting / contrasting / mentioning classification);
contrasting results are returned as evidence within the corroborate
surface, not as a separate posture.

**Example:** a statistics unit sets `corroboration: 0.8` because the
original SME claims rely on a single textbook. e.g. the production
pipeline will fetch 3–5 independent supporting citations per claim and
surface any contrasting findings for the course author to review.

## Interactions

The two dials are independent but not unrelated.

- **Both unset (`default: null` for each)**: production treats the unit as
  source-faithful and evidence-as-given. This is the calmest default.
  Example: a course author who trusts their SME outline and needs no
  augmentation for this unit.
- **Enrichment set, corroboration unset**: production expands depth
  (more analogies, more examples, more context) but does not add
  cross-validating citations. Example: a storytelling-heavy unit where
  richer narrative matters more than citation density.
- **Corroboration set, enrichment unset**: production preserves the SME
  depth as-is but cross-validates the existing claims. Example: a
  statistics unit where the claims must be ironclad but no new
  concepts need to be introduced.
- **Both set**: production goes deep AND cross-validates. Example: a
  keystone-concept unit in a health-sciences program where both
  aspirational depth and ironclad evidence matter.

The weather_band signal is orthogonal to both dials: a gold unit (source
strongly supports the event) with `enrichment: 0.9` means the author
asked for depth BEYOND what a strong source already provides — legitimate;
a gray unit (default: Marcus leans in more) with `enrichment: 0.0` means
the author explicitly chose source-faithful minimalism even on a sparse
source — also legitimate, and typically paired with a delegation or
blueprint scope decision.

## Operator-facing wording

The weather_band semantics (gold / green / amber / gray) surface to the
course author as abundance-framed phrases, never as deficit framing. This
is the single most important operator-experience rule in the lesson planner.

- **gold — "you've got this cold."** The source strongly supports the event.
  Default scope is auto-in-scope with `enrichment: null` and
  `corroboration: null`. Example: the course author's SME outline has two
  pages of detail on this event — no lean required.
- **green — "we're in step."** The source supports the event with light
  enrichment likely to help. Default scope is in-scope; Marcus may propose
  `enrichment: 0.3` as a starting point. e.g. an event where the outline
  has a paragraph and the author wants an extra analogy.
- **amber — "your call."** The source partially supports the event; the
  course author's judgment is what matters. Default scope is unset;
  Marcus surfaces a one-sentence diagnosis and asks. Example: an event
  where the SME mentions the concept in one sentence and the author must
  decide whether to lean in (delegation) or accept the minimal coverage.
- **gray — "Marcus leans in more."** Marcus proposes additional support —
  delegation to a specialized modality or a blueprint hand-off — for
  this unit. Default scope is `delegated` or `blueprint`. e.g. an event
  where the SME outline is silent and Marcus suggests a blueprint
  deliverable for the author to validate.

No deficit language appears anywhere in this surface: never "insufficient,"
never "failed," never "low quality." The course author did not fail —
the source is what it is, and the dials plus scope decision are how the
plan adapts to what is there.
