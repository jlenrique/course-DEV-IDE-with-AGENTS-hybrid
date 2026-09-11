# Gate Evaluation Protocol

Step-by-step protocol for evaluating a fidelity gate. Follow this sequence for every assessment.

## Evaluation Flow

```
1. Receive context envelope from Marcus
2. Load L1 contract for the target gate
3. Load source of truth artifact(s)
4. Load output artifact(s)
5. Perceive output artifacts (if perception required)
6. Evaluate each criterion
7. Compile Fidelity Trace Report
8. Determine circuit breaker action
9. Return report to Marcus
```

## Step 1: Receive Context Envelope

Marcus passes a context envelope when delegating fidelity evaluation:

```yaml
gate: "G3"
production_run_id: "C1-M1-P2S1-VID-001"
artifact_paths:
  pptx: "course-content/staging/.../deck.pptx"
  pngs:
    - "course-content/staging/.../card-01.png"
    - "course-content/staging/.../card-02.png"
source_of_truth_paths:
  slide_brief: "course-content/staging/.../slide-brief.md"
fidelity_contracts_path: "state/config/fidelity-contracts/"
run_mode: "default"
governance:
  invocation_mode: "delegated"      # delegated | standalone
  current_gate: "G3"
  authority_chain: ["marcus", "quality-reviewer"]
  decision_scope:
    owned_dimensions:
      - "source_fidelity"
    restricted_dimensions:
      - "quality_standards"
      - "instructional_design"
      - "tool_execution_quality.slides"
      - "tool_execution_quality.video"
      - "tool_execution_quality.audio"
  allowed_outputs:
    - "fidelity_trace_report"
    - "fidelity_findings"
    - "circuit_breaker"
```

Validate that all required paths are present and files are accessible. If any critical path is missing, HALT and report to Marcus.

Validate governance boundaries before evaluation:
- Planned outputs must be in `governance.allowed_outputs`
- Planned judgments must remain in `governance.decision_scope.owned_dimensions` (canonical values in `docs/governance-dimensions-taxonomy.md`)

If out-of-scope work is requested, return a scope violation payload to `governance.authority_chain[0]` and stop processing that request.

`scope_violation.route_to` must equal `governance.authority_chain[0]`.

## Step 2: Load L1 Contract

Read the gate contract from `{fidelity_contracts_path}/g{n}-*.yaml`. Parse the `criteria[]` array.

For each criterion, note:
- `evaluation_type`: deterministic (structural check) or agentic (judgment-based)
- `requires_perception`: whether a sensory bridge is needed
- `perception_modality`: which bridge to invoke
- `fidelity_class`: which fidelity classifications this criterion applies to

Reference: `state/config/fidelity-contracts/_schema.yaml` for the contract schema.

## Step 3: Load Source of Truth

Read the source artifact(s) identified by the gate's `source_of_truth` and the context envelope.

For **G0**: The source of truth is the original SME materials. Since originals may not be fully available to Vera, the comparison is structural — verify `extracted.md` against `metadata.json` provenance entries and section expectations.
For **G1**: Read the source bundle (`extracted.md`). Extract major themes, section headings, and key content.
For **G2**: Read the lesson plan. Extract all LOs, content blocks, assessment hooks.
For **G3**: Read the slide brief. Extract all slides with their fidelity classifications, content items, visual guidance, and learning purpose.
For **G4**: Read the lesson plan (assessment hooks, LOs) AND the `perception_artifacts[]` from the context envelope (confirmed visual content of actual slides). Both are sources of truth — narration must align with both.
For **G5**: Read the narration script (exact text, pronunciation guides, duration estimates). This is the single source of truth for what should have been spoken.

## Step 4: Load Output Artifact

Read the artifact(s) produced by the producing agent.

For **G0**: Read `extracted.md` and `metadata.json` from the source bundle directory (see `skills/source-wrangler/references/bundle-format.md`).
For **G1**: Read the lesson plan produced by Irene (see `skills/bmad-agent-content-creator/references/template-lesson-plan.md` for structure).
For **G2**: Read the slide brief produced by Irene.
For **G3**: Read the generated slide data (PNGs + PPTX if available).
For **G4**: Read the narration script and segment manifest produced by Irene Pass 2.
For **G5**: Read the audio files (MP3/WAV) produced by ElevenLabs Voice Director.

## Step 5: Perceive Output (When Required)

For criteria with `requires_perception: true`, invoke the sensory bridge specified by the criterion's `perception_modality` field. Follow the universal perception protocol from `skills/sensory-bridges/references/perception-protocol.md`:

1. **Receive** — Identify the artifact path and the criterion's `perception_modality`
2. **Perceive** — Invoke via the shared bridge interface: `perceive(artifact_path, modality, gate, requesting_agent)` (see `skills/sensory-bridges/SKILL.md` for the canonical invocation pattern). Within a production run, perception results are cached per `(artifact_path, modality)` — if both Vera and Quinn-R need the same perception, the bridge runs once (see `skills/sensory-bridges/references/validator-handoff.md`).
3. **Confirm** — State interpretation with confidence: "PPTX bridge extracted 12 slides, 47 text frames. Confidence: HIGH."
4. **Proceed** — If confidence meets threshold (HIGH or MEDIUM), continue evaluation
5. **Escalate** — If confidence is LOW, flag to Marcus for human clarification

### G0 PDF Bridge for Degraded Source Detection

G0-05 requires PDF perception. When `metadata.json` provenance entries include `kind: local_pdf`:

1. Locate the PDF file via the provenance `ref` path
2. Invoke: `perceive(pdf_path, "pdf", "G0", "fidelity-assessor")`
3. Check response `pages[].is_scanned` — pages with `is_scanned: true` indicate scanned/OCR content
4. If any pages are scanned: report a `degraded_source` finding (severity: high) with affected page numbers
5. The finding's `suggested_remediation` should advise the human to provide manual transcription or alternative machine-readable source for the affected pages

This does not halt the pipeline automatically — it is a high-severity finding that triggers the circuit breaker. The human decides whether to proceed with an incomplete baseline or provide better source material.

### G3 Dual-Bridge Strategy

At G3, the L1 contract specifies the correct perception modality per criterion. Follow the contract — do not override it:

| Contract Modality | Criteria | Bridge | Purpose |
|-------------------|----------|--------|---------|
| `pptx` | G3-02 (literal text), G3-04 (creative coverage), G3-05 (invention detection) | `pptx_to_agent.py` | Deterministic text extraction — exact text objects from slide data |
| `image` | G3-03 (literal visual) | `png_to_agent.py` | Visual layout, image presence, visual element verification |

If PPTX is unavailable for a `pptx`-modality criterion, fall back to image bridge with `degraded_evaluation` warning (lower confidence for text extraction via OCR vs. deterministic PPTX extraction).

## Step 6: Evaluate Each Criterion

For each criterion in the L1 contract, evaluate against the source of truth:

### Deterministic Criteria (`evaluation_type: deterministic`)

Apply structural checks: count matching, field presence, schema compliance, parameter coherence. These are pass/fail — no judgment, no severity adjustment.

**G0 deterministic checks:**
- **G0-02 (Media capture notation):** `metadata.json` contains `media_references[]` with entries for each image/diagram/table found in source materials
- **G0-03 (Metadata completeness):** Every `provenance[]` entry has non-empty `kind` (url|notion_page|box_file|playwright_html|local_pdf), `ref`, and `fetched_at` (ISO-8601)
- **G0-05 (Degraded source detection, modality: pdf):** For each PDF source in provenance, invoke PDF bridge and check `pages[].is_scanned`. Emit `degraded_source` warning with affected page numbers if any pages are scanned.

**G1 deterministic checks:**
- **G1-02 (LO structure completeness):** Every LO entry has non-empty `bloom_level`; every LO is referenced by at least one content block's Objective Served field
- **G1-03 (Content block completeness):** Every Block N section contains non-empty Objective Served, Content Type, Writer Delegation, and Behavioral/Affective Goal fields
- **G1-04 (Assessment alignment):** Every LO appears in at least one row of the assessment hooks table
- **G1-05 (No orphaned content):** Every content block's Objective Served field references a valid LO from the lesson plan header

**G4 deterministic checks:**
- **G4-01 (Slide correspondence):** Every narration segment's `[Gary Slide: {id}]` reference maps to a valid slide in `gary_slide_output[]`
- **G4-06 (Segment manifest alignment):** `count(narration_segments) == count(manifest_segments)` and `narration_ref` linkages are valid
- **G4-08 (Perception lineage binding):** For each slide_id, `perception_artifacts.source_image_path` equals `gary_slide_output.file_path` and references a local `.png`
- **G4-10 (Runtime plan coherence):** Segment runtime decisions align with the approved runtime plan controls (`parent_slide_count`, `target_total_runtime_minutes`, `estimated_total_slides`, `avg_slide_seconds`, per-slide targets). Unjustified drift is a failure.
- **G4-11 (Timing rationale completeness):** Every segment includes valid `timing_role`, `content_density`, `visual_detail_load`, `duration_rationale`, and `bridge_type` per `narration-script-parameters.yaml` runtime_variability policy.
- **G4-16 (Cluster narration coherence):** For each cluster, every interstitial segment's `behavioral_intent` must serve the cluster's `master_behavioral_intent` using the compatibility rules in `cluster-narrative-arc-schema.md`. Any contradictory or divergent interstitial intent is a high-severity deterministic failure.
- **G4-17 (Cluster word budget):** In clustered runs, head narration uses `cluster_head_word_range` and interstitial narration uses `interstitial_word_range`, each with a ±5 word tolerance. Segments outside the tolerated band are high-severity deterministic failures.
- **G4-18 (No new concepts in interstitials):** Moved to the agentic list. The handoff validator may still *report* a token heuristic as an advisory detail; it must not fail-closed on function words.
- **G4-19 (Cluster arc integrity):** Cluster positions must remain in canonical order and the resolve segment must callback to establish concepts via meaningful keyword overlap. Disordered positions, missing middle beats before resolve, or a resolve with no callback are high-severity deterministic failures.

**G5 deterministic checks:**
- **G5-02 (WPM compliance):** Audio bridge `wpm` is between 130 and 170 WPM for instructional narration
- **G5-05 (Duration alignment):** Audio bridge `total_duration_ms` is within ±15% of narration script's estimated duration

**G2 deterministic checks:**
- **G2-01 (LO traceability):** Every slide section with `cluster_role` `null` or `head` has a non-empty Learning Purpose that references a valid LO from the lesson plan. `cluster_role == interstitial` inherits LO coverage from its head and is exempt from standalone LO tracing.
- **G2-02 (Content item completeness):** Every slide has Content, Visual Guidance (Layout, Hero Element, Visual Density), and Learning Purpose populated
- **G2-04 (Downstream parameter coherence):** literal-text slides specify textMode: preserve; literal-visual specify textMode: preserve + imageOptions.source; creative may use any textMode
- **G2-06 (Fidelity-control vocabulary):** Literal slides use deterministic vocabulary (text_treatment, image_treatment, layout_constraint, content_scope) — no free-text additionalInstructions

**G3 deterministic checks:**
- **G3-01 (Slide count match):** `count(generated_slides) == count(slide_brief.slides where cluster_role in (null, head)) + sum(cluster_interstitial_count for each cluster head)`; this reduces to the legacy flat-deck count rule when cluster metadata is absent.
- **G3-06 (Provenance manifest):** provenance[] has one entry per card with card_number, source_call, generation_id, fidelity class

### Agentic Criteria (`evaluation_type: agentic`)

Apply judgment-based evaluation. Current L2 approach:
- **Keyword/item matching:** Extract key terms from source, verify they appear in output
- **Item counting:** Count source items (LOs, content blocks, assessment criteria), verify all appear
- **Structural comparison:** Compare section structure between source and output
- **Semantic assessment:** Verify meaning preservation, not just word presence

**G0 agentic checks:**
- **G0-01 (Section coverage):** For each top-level section in the source material (inferred from `metadata.json` provenance and `extracted.md` heading structure), a corresponding section exists in `extracted.md`. Compare the heading structure of the extracted document against what the source material structure implies.
- **G0-04 (No content invention):** Look for agent-generated summaries, interpretations, or editorial additions that are not present in the sources. Extraction should be faithful reproduction, not paraphrase. **L2 evaluation constraint:** The current bundle format (`extracted.md` + `metadata.json`) provides per-source provenance but NOT per-paragraph source mapping. Vera can verify: (1) structural alignment — sections in `extracted.md` correspond to sources listed in `provenance[]`, (2) obvious inventions — paragraphs containing editorial framing ("This document covers...", "In summary...") or content topics absent from all listed sources. Vera CANNOT do exact paragraph-to-source tracing without per-paragraph provenance — flag uncertain cases as `resolution_confidence: approximate`. Deeper per-section provenance mapping is a future enhancement to the source-wrangler bundle format.

**G1 agentic checks:**
- **G1-01 (Source theme coverage):** For each major section/theme in `extracted.md`, at least one LO addresses that theme. When `source_ref` annotations are present on LOs, resolve them and verify the cited section exists. Themes with no LO coverage are Omissions.
- **G1-06 (No content invention):** Domain-specific factual assertions in the lesson plan (drug names, dosages, statistics, clinical recommendations, assessment criteria) can be traced to corresponding content in `extracted.md`. Claims with no source basis are Inventions.

**G4 agentic checks:**
- **G4-02 (Visual accuracy, modality: image):** For each narration segment, the described visual elements match the `perception_artifacts[]` extracted text and layout for that slide number. Irene should have written narration that complements what is actually on the slide — not what was planned in the slide brief.
- **G4-03 (Assessment reference exactness):** Knowledge check topics, assessment questions, or testable items mentioned in narration appear verbatim in the lesson plan assessment hooks table. Any deviation is an Alteration.
- **G4-04 (Terminology consistency):** Clinical terms (drug names, procedure names, condition names) are spelled and used identically across narration, slides, and lesson plan. Inconsistencies are Alterations.
- **G4-05 (No narration invention):** Domain-specific factual assertions in narration can be traced to the lesson plan or generated slide content. Invented claims are Inventions with critical severity.
- **G4-09 (Audience-directed visual grounding, modality: image):** For each `visual_references[]` entry in the segment manifest, verify: (1) `perception_source` matches a valid slide_id in `perception_artifacts[]`, (2) `element` description matches a `visual_elements[].description` in that perception artifact, (3) `narration_cue` phrase appears in the corresponding narration segment text, (4) narration remains audience-directed (no forbidden meta slide language), and (5) for non-static segments (`motion_type` ≠ `static`, `visual_mode: video`), narration emphasizes the dynamic visual content of the approved motion clip rather than describing only the static slide layout — motion-first narration should reference movement, change, process, or temporal progression visible in the clip; a video segment whose narration reads as if the static slide is still on screen is a high-severity finding.
- **G4-07 (Source depth utilization, modality: image):** For each creative-fidelity slide, verify that the narration segment incorporates at least one substantive claim from the corresponding `source_ref` anchors that goes beyond what is visible on the slide PNG. Evaluation method: (1) Load `narration-grounding-profiles.yaml` — creative profile requires `source_role: primary` and `min_source_claims: 1`. (2) Resolve the slide's `source_ref` to its extraction text. (3) Load `perception_artifacts[]` for that slide to determine what is visually on screen. (4) Check that the narration segment contains at least one factual claim from the source extraction that is NOT present in the perception artifact's visual description. Narration that merely describes the slide visual without teaching the source content behind it is a failure. Severity: high.
- **G4-12 (Script-parameter policy adherence, modality: image):** Verify narration and segment behavior conform to script-level controls in `narration-script-parameters.yaml` (density, visual references, bridge cadence, and meta-language policy). Unintended policy drift is a medium-severity finding.
- **Bridge language enforcement note:** Exact-substring intro/outro cues remain authoring help and advisory validator details. They are not a fail-closed exam. Vera judges spoken-bridge *quality* under G4-12: `intro`/`outro`/`both` should be hearable connective language; `cluster_boundary` is a two-part seam (synthesize the prior cluster, then pull forward) — not `bridge_type: both` and not a required `in this section` substring.
- **G4-18 (No new concepts in interstitials):** For each clustered interstitial, judge whether the spoken narration opens a new teaching idea outside the head's instructional scope, the cluster's Pass 1 teaching terms (`title`, `learning_objective`, `source_refs`, `narrative_arc`), and this card's own source_ref / perceived detail. Do **not** treat function words or ordinary connective English as new concepts. A high-confidence new teaching idea is a high-severity finding. Token-heuristic dumps from the handoff validator are evidence to consider, not the verdict.
- **G4-13 (Behavioral intent validation):** For each segment with a `behavioral_intent` field, verify: (1) the stated intent is specific to the segment's content, not generic boilerplate repeated across consecutive segments, (2) the narration text's instructional approach plausibly supports the claimed behavioral/affective effect, (3) consecutive segments sharing identical `behavioral_intent` text are flagged as under-differentiated (medium severity). Narration that contradicts its stated intent (e.g., claiming "inspire confidence" on a purely definitional reading) is a high-severity finding.
- **G4-14 (Motion brief fidelity, modality: image):** For each non-static segment with a `motion_brief`, verify that the brief's described visual action is consistent with the motion perception confirmation for that segment's `motion_asset_path`. A `motion_brief` that describes action not present in the perceived clip is an Invention. Severity: high.
- **G4-15 (Duration rationale semantic correctness):** Beyond the structural completeness checked by G4-11, assess whether each segment's `duration_rationale` provides a genuine, segment-specific justification. Evaluation: (1) rationale must reference at least two of three runtime dimensions (purpose/timing role, content density, visual detail load/burden), (2) rationale must be unique across consecutive segments — identical rationale on 3+ consecutive segments is a high-severity finding, (3) purely formulaic rationales ("standard density, standard timing") with no segment-specific reasoning are medium-severity findings. This criterion is the agentic companion to G4-11's deterministic field-presence check.

**G5 agentic checks (all require audio perception):**
- **G5-01 (Script accuracy, modality: audio):** STT transcript word sequence matches narration script text with word-error-rate < 5%. Invoke audio bridge: `perceive(audio_path, "audio", "G5", "fidelity-assessor")`. Compare `transcript_text` against narration script segment by segment.
- **G5-03 (Pronunciation accuracy, modality: audio):** Terms listed in the narration script's pronunciation guide are spoken correctly per STT transcript. Phonetic mismatches where meaning changes (e.g., "hypertension" vs "hypotension") are critical Alterations.
- **G5-04 (No audio invention, modality: audio):** STT transcript contains no words, phrases, or sentences absent from the narration script. Hallucinated audio content is an Invention with critical severity.

**G2 agentic checks:**
- **G2-03 (Fidelity classification accuracy):** For slide sections with `cluster_role` `null` or `head`, literal-text slides contain verifiable exact-match content; literal-visual reference existing SME images; creative slides have no content requiring verbatim preservation. `cluster_role == interstitial` inherits fidelity from its head and is exempt from standalone classification. Over-tagging literal on renderable slides is a violation.
- **G2-05 (No content loss):** For each content block in the lesson plan, at least one slide's Content addresses that block's material

**G3 agentic checks (require perception — modality per L1 contract):**
- **G3-02 (Literal text preservation, modality: pptx):** For literal-text slides, all content_items appear verbatim in PPTX extracted text (`slides[].text_frames[]`)
- **G3-03 (Literal visual placement, modality: image):** Image bridge confirms image present + surrounding text matches slide brief
- **G3-04 (Creative content coverage, modality: pptx):** For creative slides, all content_items themes are semantically present in PPTX extracted text — creative reframing acceptable, theme omission is not
- **G3-05 (No harmful invention, modality: pptx):** PPTX extracted text does not contain domain-specific factual assertions absent from the slide brief (drug names, dosages, statistics, clinical recommendations)

### Source_ref Resolution

When evaluating source_ref annotations, apply basic resolution:
1. Split on first `#` — left is filename, right is path expression
2. Read the referenced file
3. Find the section (heading match or line range per `docs/source-ref-grammar.md`)
4. Extract the content slice
5. If file not found or section not found → report as "broken source_ref" (severity: high)

Capture the resolved slice in the finding's `evidence` block.

## Step 6b: Cumulative Drift Check (G3 and later gates)

At G3 or any later gate, perform BOTH a **local** check (this gate's output vs. this gate's input — already done in Step 6) AND a **global** drift check (this gate's output vs. the original source bundle at G0).

### Global Drift Process

1. Identify the source bundle (`extracted.md`) path from the production run context
2. Use `scripts/resolve_source_ref.py` to resolve `source_ref` annotations in the current artifact back to the original source sections
3. For each major source theme identified at G0, check whether it is still faithfully represented in the current gate's output
4. Score global fidelity as: `themes_still_represented / total_source_themes`

### Drift Thresholds (configurable per run mode)

| Run Mode | Warning Threshold | Failure Threshold |
|----------|:-:|:-:|
| **Ad-hoc** | 20% drift | 40% drift |
| **Production** | 10% drift | 20% drift |
| **Regulated** | 5% drift | 10% drift |

Drift = `1.0 - global_fidelity_score`. A warning is logged as a medium finding. A failure triggers the circuit breaker.

### Evidence Retention for Global Drift

Each global drift check captures a self-contained evidence record:

```yaml
global_drift:
  gate: "G3"
  source_bundle: "path/to/extracted.md"
  total_source_themes: 8
  themes_represented: 7
  global_fidelity_score: 0.875
  drift: 0.125
  threshold_mode: "production"
  threshold_warning: 0.10
  threshold_failure: 0.20
  verdict: "warning"
  missing_themes:
    - theme: "Regulatory Compliance Framework"
      source_ref: "extracted.md#Chapter 4 > Regulatory"
      last_seen_at: "G1"
```

### Source_ref Resolver

Use `scripts/resolve_source_ref.py` for all provenance resolution. The resolver implements the grammar from `docs/source-ref-grammar.md`:

- Parses `{filename}#{path_expression}` — heading hierarchy (`>`), line range (`L{n}-L{m}`), heading anchor (`## text`)
- Returns `(content_slice, confidence)` where confidence is `exact`, `approximate`, or `broken`
- Cache resolved content per production run to avoid redundant file reads

### Drift Check Invocation

To perform the global drift check, invoke the drift checker CLI:

```bash
python scripts/fidelity_drift_check.py <source_bundle_extracted_md> <artifact_file> <gate> <mode>
```

Example:
```bash
python scripts/fidelity_drift_check.py \
  course-content/staging/ad-hoc/source-bundles/trial2/extracted.md \
  course-content/staging/ad-hoc/slide-brief.md \
  G3 \
  production
```

The script returns JSON with `verdict` (pass/warning/failure), `drift` score, `missing_themes`, and evidence. Exit code 1 on failure. The `resolve_source_ref` resolver is called internally for each missing theme's `source_ref` — the full chain (`compute_global_drift` → `extract_source_themes` → `check_theme_representation` → `resolve_source_ref`) executes as one operation.

## Step 7: Compile Fidelity Trace Report

Assemble all findings into the Fidelity Trace Report format defined in `./fidelity-trace-report.md`.

Calculate:
- `fidelity_score` = criteria_passed / criteria_evaluated
- `highest_severity` = max severity among all findings (critical > high > medium > none)
- `pass` = true if no critical or high findings; false otherwise

## Step 8: Determine Circuit Breaker Action

Based on the highest severity finding and the operating policy from `docs/fidelity-gate-map.md`:

| Highest Severity | Run Mode | Action |
|------------------|----------|--------|
| Critical | Any | `halt` — pipeline stops, no auto-retry |
| High | Default | `retry` — re-invoke producing agent with remediation guidance |
| High | Ad-hoc | `proceed` — downgrade to warning, continue pipeline |
| Medium | Any | `proceed` — attach findings as advisory |
| None | Any | `proceed` — clean pass |

Set `circuit_breaker.remediation_target` to the producing agent for this gate (source-wrangler at G0, Irene at G1/G2/G4, Gary at G3, elevenlabs-voice-director at G5).
Set `circuit_breaker.remediation_guidance` to a specific, actionable instruction for the producing agent.

## Step 9: Return Report to Marcus

Return the complete Fidelity Trace Report payload. Marcus routes based on the circuit breaker action.

If circuit breaker triggered, also trigger a memory save (Save Memory capability) to record the event.
