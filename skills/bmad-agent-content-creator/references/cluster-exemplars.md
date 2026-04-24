# Cluster Exemplar Library (C1-M1 Retrofit)

This library captures applied cluster decisions from C1-M1 runs, with complete interstitial contracts and rationale.

## Source Runs Used

- Primary post-run evidence: `C1-M1-PRES-20260419B` (`g2-slide-brief.md`, `cluster-plan.yaml`, `cluster-plan-review.md`, `gary-slide-content.json`, `gary-cluster-outputs.json`)
- Supporting pre-run context: `apc-c1m1-tejal-20260409/g2-slide-brief.md`

## Candidate Scoring Matrix (Task 1 Output)

Scoring rubric uses `cluster-decision-criteria.md`:
- Concept Density: High / Medium / Low
- Visual Complexity: High / Medium / Low
- Pedagogical Weight: High / Medium / Low
- Operator Input: Support / Neutral / Oppose

| Slide | Topic | Concept Density | Visual Complexity | Pedagogical Weight | Operator Input | Decision |
|---|---|---|---|---|---|---|
| S01 | The Modern Clinician's Dilemma | High | Medium | High | Support | Selected |
| S04 | The Innovator's Hero's Journey | High | High | High | Support | Selected |
| S07 | You Are Stepping Into a Lineage | High | High | High | Support | Selected |
| S10 | The Mental Frameworks You Will Operate With | Medium | Medium | High | Support | Selected |
| S13 | Part 1 - What We Established | Medium | Medium | High | Support | Selected |
| S12 | The 3-Course Series Roadmap | Medium | High | High | Oppose (no-overlay literal-visual policy) | Rejected strong candidate |
| S03 | Part 1 Learning Objectives | Medium | Low | Medium | Neutral | Not selected |

Selected for full exemplar treatment: S01, S04, S07, S10, S13.

Rejected strong candidate exemplar: S12.

---

## Exemplar 1: Motion Hook to Identity Pivot (c-u01)

**Source:** RUN_ID `C1-M1-PRES-20260419B`, Slides S01-S02
**Head Topic:** The Modern Clinician's Dilemma

**Cluster Decision Scores:**
- Concept Density: High - introduces practitioner identity, systems gap, and role shift in one opening beat
- Visual Complexity: Medium - motion + title card + conceptual pivot text can overload without isolation
- Pedagogical Weight: High - opening frame sets the learner contract for the full lesson
- Operator Input: Support - visual-led profile and motion-enabled run both favor a staged open

**Decision:** Single interstitial

**Cluster Plan:**
- `narrative_arc`: "From overwhelmed clinician to empowered system designer through explicit role reframing"
- `master_behavioral_intent`: `clear-guidance`
- `cluster_interstitial_count`: 1

**Interstitial 1:**
- `cluster_position`: tension
- `develop_type`: n/a
- `interstitial_type`: emphasis-shift
- `isolation_target`: "the role transition phrase 'Clinical Reactor -> Systemic Innovator'"
- `visual_register_constraint`: ["suppress all hallway and EHR scene detail", "remove non-transition labels", "retain only transition typography and directional motif"]
- `content_scope`: minimal
- `narration_burden`: low
- `relationship_to_head`: isolate

**Production Notes:**
- Executed in post-run cluster flow (`cluster-plan.yaml`: c-u01 head + 1 interstitial; `cluster-plan-review.md`: PASS).
- `gary-cluster-outputs.json` confirms S01 as head and S02 as interstitial in c-u01.

---

## Exemplar 2: Three-Course Journey Decomposition (c-u02)

**Source:** RUN_ID `C1-M1-PRES-20260419B`, Slides S04-S06
**Head Topic:** The Innovator's Hero's Journey

**Cluster Decision Scores:**
- Concept Density: High - 3 waypoints each carry a different learner responsibility
- Visual Complexity: High - roadmap contains multiple directional and semantic anchors
- Pedagogical Weight: High - central orienting structure for the full course trilogy
- Operator Input: Support - roadmap was intentionally selected for staged progression

**Decision:** Full cluster (2 interstitials)

**Cluster Plan:**
- `narrative_arc`: "From clinical practitioner to innovation journey navigator through staged waypoint focus"
- `master_behavioral_intent`: `clear-guidance`
- `cluster_interstitial_count`: 2

**Interstitial 1 (S05):**
- `cluster_position`: develop
- `develop_type`: deepen
- `interstitial_type`: reveal
- `isolation_target`: "Waypoint 1 ('Sparking Innovation') node and left-third roadmap segment"
- `visual_register_constraint`: ["de-emphasize Waypoints 2 and 3", "remove non-Waypoint-1 labels", "keep only first-waypoint highlight ring"]
- `content_scope`: minimal
- `narration_burden`: low
- `relationship_to_head`: zoom

**Interstitial 2 (S06):**
- `cluster_position`: resolve
- `develop_type`: n/a
- `interstitial_type`: reveal
- `isolation_target`: "the final destination artifact concept ('Executive One-Pager')"
- `visual_register_constraint`: ["suppress roadmap path geometry", "remove intermediate waypoint detail", "retain only destination artifact framing"]
- `content_scope`: focused
- `narration_burden`: low
- `relationship_to_head`: reframe

**Production Notes:**
- Executed and reviewed (`cluster-plan.yaml`: c-u02 with 2 interstitials; `cluster-plan-review.md`: PASS).
- `gary-cluster-outputs.json` confirms S04 head with S05/S06 as interstitials.

---

## Exemplar 3: Archetype Lineage Expansion (c-u04)

**Source:** RUN_ID `C1-M1-PRES-20260419B`, Slides S07-S09
**Head Topic:** You Are Stepping Into a Lineage

**Cluster Decision Scores:**
- Concept Density: High - four archetypes require meaningful separation to avoid cognitive collision
- Visual Complexity: High - 4-quadrant composition is rich but dense for first exposure
- Pedagogical Weight: High - identity transfer from clinician to innovator is a core transformation in Part 1
- Operator Input: Support - split-panel treatment was explicitly briefed

**Decision:** Full cluster (2 interstitials)

**Cluster Plan:**
- `narrative_arc`: "From passive clinician to active inheritor of an innovation lineage through archetype disaggregation"
- `master_behavioral_intent`: `provocative`
- `cluster_interstitial_count`: 2

**Interstitial 1 (S08):**
- `cluster_position`: develop
- `develop_type`: exemplify
- `interstitial_type`: reveal
- `isolation_target`: "Device + Process archetypes (Fogarty + Pronovost)"
- `visual_register_constraint`: ["suppress Technology and Organizational quadrants", "remove central lineage label", "retain only two left-side archetype frames"]
- `content_scope`: focused
- `narration_burden`: low
- `relationship_to_head`: isolate

**Interstitial 2 (S09):**
- `cluster_position`: resolve
- `develop_type`: n/a
- `interstitial_type`: emphasis-shift
- `isolation_target`: "Technology + Organizational archetypes plus 'Your archetype?' prompt"
- `visual_register_constraint`: ["suppress Device and Process panels", "remove redundant iconography", "retain only right-side archetype contrast and learner prompt"]
- `content_scope`: focused
- `narration_burden`: medium
- `relationship_to_head`: reframe

**Production Notes:**
- Executed and reviewed (`cluster-plan.yaml`: c-u04 with 2 interstitials; `cluster-plan-review.md`: PASS).
- `gary-cluster-outputs.json` confirms S07 head with S08/S09 interstitials.

---

## Exemplar 4: Framework Pair to Third-Framework Pivot (c-u05)

**Source:** RUN_ID `C1-M1-PRES-20260419B`, Slides S10-S11
**Head Topic:** The Mental Frameworks You Will Operate With

**Cluster Decision Scores:**
- Concept Density: Medium - two formal definitions plus a third framework pivot
- Visual Complexity: Medium - dual-column definitional head would overload if all three frameworks stayed on one surface
- Pedagogical Weight: High - framework stack underpins diagnostic and action phases in Part 2
- Operator Input: Support - interstitial planned to isolate the first-principles pivot

**Decision:** Single interstitial

**Cluster Plan:**
- `narrative_arc`: "From fixed mindset assumptions to first-principles agency through explicit framework chaining"
- `master_behavioral_intent`: `clear-guidance`
- `cluster_interstitial_count`: 1

**Interstitial 1 (S11):**
- `cluster_position`: resolve
- `develop_type`: n/a
- `interstitial_type`: bridge-text
- `isolation_target`: "the chain Growth Mindset -> Psychological Safety -> First Principles -> Your Clinical Problem"
- `visual_register_constraint`: ["remove dense definitional prose blocks", "retain only named framework nodes and directional arrows", "suppress non-sequential decorative text"]
- `content_scope`: reduced
- `narration_burden`: high
- `relationship_to_head`: reframe

**Production Notes:**
- Executed and reviewed (`cluster-plan.yaml`: c-u05 head + 1 interstitial; `cluster-plan-review.md`: PASS).
- `gary-cluster-outputs.json` confirms S10 head with S11 interstitial.

---

## Exemplar 5 (Rejected Strong Candidate): Full-Series Roadmap Decomposition (S12)

**Source:** RUN_ID `C1-M1-PRES-20260419B`, Slide S12
**Topic:** The 3-Course Series Roadmap - Your Full Arc

**Cluster Decision Scores:**
- Concept Density: Medium - image carries multiple course-level waypoints and progression logic
- Visual Complexity: High - full roadmap image is dense and potentially decomposable
- Pedagogical Weight: High - series-level orientation is critical
- Operator Input: Oppose - explicit literal-visual policy required full-frame source fidelity with no overlay decomposition

**Decision:** Rejected (remain singleton)

**Rejection Rationale:**
- The slide is an operator-confirmed source artifact (`src-004`) with a no-rebrand, no-overlay requirement.
- Clustering this slide would trade source authority for visual manipulation and increase pacing load late in Part 1.
- End-of-part flow favored continuity into S13/S14 rather than additional decomposition.

**Counterfactual Cluster Plan (not executed):**
- `narrative_arc`: "From static roadmap awareness to actionable series orientation through waypoint spotlighting"
- `master_behavioral_intent`: `reflective`
- `cluster_interstitial_count`: 1

**Counterfactual Interstitial 1:**
- `cluster_position`: develop
- `develop_type`: reframe
- `interstitial_type`: simplification
- `isolation_target`: "the Part 1 segment of the full-series roadmap"
- `visual_register_constraint`: ["suppress Part 2/3 labels", "remove peripheral callouts", "retain only Part 1 path segment and current-position anchor"]
- `content_scope`: reduced
- `narration_burden`: low
- `relationship_to_head`: simplify

**Production Notes:**
- Not executed by design. `cluster-plan.yaml` keeps S12 as singleton with `cluster_id: null`.
- Serves as a negative-control exemplar for future runs where operator policy differs.

---

## Reuse Notes for Irene Pass 1

- Prefer Exemplar 2 and Exemplar 3 when concept density and visual complexity are both High.
- Prefer Exemplar 4 when definitional heads need a single conceptual pivot interstitial.
- Use Exemplar 5 as a guardrail for "technically clusterable but strategically wrong" cases.
