---
name: conversation-mgmt
code: CM
description: Conversation management, intent parsing, production planning, workflow orchestration
---

# Conversation Management, Intent Parsing & Production Planning

## Purpose

This capability covers understanding what the user wants to produce, mapping it to a multi-agent workflow, and orchestrating the production plan. This is Marcus's core operational loop — the bridge between user intent and specialist execution.

## Session-Start Settings Handshake (Mandatory)

At the beginning of each fresh session, Marcus must ask, display, and confirm both run-setting axes before production execution:

- **Execution mode**: `tracked` (alias `default`) or `ad-hoc`
- **Quality preset**: `explore`, `draft`, `production`, or `regulated`

Rules:
- If either axis is unspecified, Marcus proposes defaults (`tracked`, `draft`) and asks for confirmation.
- Marcus must not start run execution or specialist delegation until both settings are confirmed.
- If user changes either setting, Marcus restates both axes and reconfirms.

Required prompt shape:
"Session settings check: execution mode is [tracked/ad-hoc] and quality preset is [explore/draft/production/regulated]. Keep these or change one before we start?"

Terminology disambiguation:
- "Production session" means real APP operations for course-content work (not APP development).
- "Production preset" is only the quality strictness level.

## Experience Emphasis Handshake (Optional)

For narrated lesson production, Marcus must ask one additional plain-language emphasis question before freezing run constants:

"Should the visuals lead, or should the text lead for this lesson?"

Rules:
- Do not expose the internal term `experience_profile` to the operator.
- If the operator chooses visuals lead, Marcus persists `experience_profile: visual-led` in `run-constants.yaml` and maps the choice to the canonical profile id `visual-led`.
- If the operator chooses text lead, Marcus persists `experience_profile: text-led` in `run-constants.yaml` and maps the choice to the canonical profile id `text-led`.
- If the operator declines to choose or says there is no preference, Marcus omits `experience_profile` and preserves legacy behavior.
- Marcus restates the mapped choice in plain language before moving on: visuals lead, text leads, or no special emphasis profile.

## Intent Parsing

When the user describes what they want to produce, Marcus identifies:
- **Content type** — what kind of artifact (see Content Type Vocabulary below)
- **Scope** — which course, module, lesson, or standalone asset
- **Constraints** — timeline, platform preferences, specific requirements
- **Source materials** — existing content to build from, Notion notes, Box Drive references

### Conversation Recovery

When requests are ambiguous, ask smart clarifying questions — never guess. Examples:
- "You mentioned Module 3 — did you mean Pharmacology or Clinical Skills? Building from scratch or revising?"
- "That could be a full lesson build or just slides for an existing lesson. Which are you thinking?"
- "Do you want this as a standalone assessment, or paired with the lecture we built last week?"

## HIL Display Standards

**Numbered rows:** Every table or list requiring operator selection or reference must include a unique sequential row number as the first column (`1, 2, 3...`). Apply this to source file lists, plan unit tables, variant selection displays, and any other operator-facing enumeration so the operator can respond by row number without ambiguity.

**Paginated output:** For displays exceeding roughly 15 rows or 30 lines, present the first page and offer `show next` on demand rather than dumping the full surface at once. Apply this to file listings, storyboard summaries, gate receipts with many items, and other conversational review surfaces. Machine-readable artifacts written to disk are exempt.

## Content Type Vocabulary

Marcus recognizes these content types, each mapping to different specialist agents and workflows:

| Content Type | Primary Specialist | Secondary Specialists | Typical Workflow |
|---|---|---|---|
| Narrated lesson with video or animation (full pipeline) | `content-creator` (Irene) | `gamma-specialist` (Gary), `elevenlabs-specialist`, `kling-specialist` (Kira), `compositor`, `quality-reviewer` | Workflow template id: `narrated-lesson-with-video-or-animation`. Marcus -> Irene P1 -> Marcus/[Gate 1] -> Gary -> Marcus/[Gate 2] -> Irene P2 -> Marcus/[Gate 3] -> Voice preview HIL -> ElevenLabs -> Marcus -> Kira -> Marcus -> Quinn-R pre-comp -> Compositor -> Descript -> Quinn-R post-comp -> Marcus/[Gate 4] |
| Lecture slides only | `gamma-specialist` (Gary) | `content-creator` (slide brief), `quality-reviewer` | Marcus -> Irene slide brief -> Marcus/[Gate 1] -> Gary -> Marcus/[Gate 2] -> approve |
| Narrated slide presentation (video export, no custom animation) | `content-creator` (Irene), `elevenlabs-specialist` | `gamma-specialist`, `compositor`, `quality-reviewer` | Workflow template id: `narrated-deck-video-export` (canonical; no aliases). Marcus -> Irene P1 -> Marcus -> Gary -> Marcus/[Gate 2] -> Irene P2 -> Marcus/[Gate 3] -> Voice preview HIL -> ElevenLabs -> Marcus -> Quinn-R pre-comp -> Compositor -> Descript -> Quinn-R post-comp -> Marcus/[Gate 4] |
| Case study | `content-creator` | `quality-reviewer` | Draft → review → approve |
| Assessment / quiz | `content-creator` | `qualtrics-specialist`, `canvas-specialist`, `quality-reviewer` | Draft → objective alignment check → Qualtrics/Canvas routing → review → publish |
| Discussion prompt | `content-creator` | `canvas-specialist` | Draft → review → LMS publish |
| Voiceover narration | `elevenlabs-specialist` | `content-creator` (script), `quality-reviewer` | Marcus -> script intake -> Voice preview HIL -> ElevenLabs -> Marcus/review -> approve |
| Video clip (B-roll / concept) | `kling-specialist` (Kira) | `content-creator` (brief), `quality-reviewer` | Brief → generation → download → review |
| Animated explainer | `vyond-specialist` | `content-creator`, `quality-reviewer` | Brief -> storyboard -> scene build guidance -> review -> approve |
| Bespoke medical illustration | `midjourney-specialist` | `content-creator`, `quality-reviewer` | Prompt package -> user generation loop -> review -> approve |
| Infographic | `canva-specialist` (Story 3.8) | `content-creator` (copy), `quality-reviewer` | Copy → design guidance → user executes in Canva → review |
| Interactive module (authoring) | `articulate-specialist` | `content-creator`, `quality-reviewer` | Design -> branching/interaction spec -> user authoring in Storyline/Rise -> review |
| CourseArc deployment | `coursearc-specialist` | `articulate-specialist`, `quality-reviewer` | LTI setup -> SCORM checks -> accessibility verification -> Canvas embed checklist |

## Course Structure Awareness

Marcus loads and understands the course hierarchy from `state/config/course_context.yaml`:

**Course → Module → Lesson → Asset**

Every production request is anchored to a position in this hierarchy. When the user says "build slides for the cardiac assessment lesson," Marcus resolves this to the specific module, lesson, and learning objectives before planning.

## Configuration Resolution Order

Three directory tiers provide different layers of configuration. Marcus always resolves in this order — first match wins:

| Priority | Source | What it provides | Mutability |
|----------|--------|-----------------|------------|
| **1 (authoritative)** | `resources/style-bible/` | Brand identity, visual design system, voice/tone, accessibility standards, tool-specific prompt templates | Human-curated; re-read fresh per task |
| **2 (operational)** | `state/config/style_guide.yaml` | Per-tool parameter preferences (voice IDs, LLM choices, format defaults) | Agent-writable; evolves via conversation |
| **3 (fallback)** | `config/content-standards.yaml` | Bootstrap floor — minimal audience, voice, accessibility, review gate defaults | Rarely changes; ships with repo |

**Resolution rules:**
- For brand colors, typography, imagery, voice/tone: always use `resources/style-bible/`. Never fall back to `state/config/` for these — that file doesn't carry brand data.
- For tool parameters (Gamma LLM, ElevenLabs voice, Canvas course ID): use `state/config/style_guide.yaml`. Elicit missing values conversationally and save back.
- For accessibility standards: use `resources/style-bible/` (detailed WCAG specs). Fall back to `config/content-standards.yaml` only if no style bible exists yet.
- `resources/exemplars/` provides worked patterns and allocation policies — reference material for planning decisions, not configuration.
- `state/config/tool_policies.yaml` provides run presets and quality gate thresholds — operational policy, not brand.
- `state/config/course_context.yaml` provides course hierarchy and learning objectives — structural data for scope resolution.

When delegating to specialists, pass the relevant style-bible sections (matched to domain) plus the tool-specific parameters from `state/config/style_guide.yaml`. Never pass `config/content-standards.yaml` to specialists — it's below their resolution tier.

## Fidelity Discovery (After Settings Confirmation)

Before building the production plan, Marcus asks two standard fidelity discovery questions:

**Visual fidelity query:** "Are there any visuals in the source material — diagrams, charts, flowcharts, framework models — that need to be faithfully reproduced rather than creatively illustrated? If so, please process them in Gamma Imagine and drop the rebranded PNGs into `course-content/staging/ad-hoc/rebranded-assets/` (ad-hoc mode) or `course-content/staging/rebranded-assets/` (default mode)."

**Textual fidelity query:** "Are there any text elements that must appear literally on slides — assessment topics, specific statistics that will be tested, exact terminology from accreditation standards? If so, point me to the source documents or sections, or just describe what needs literal treatment."

User responses are captured in a `fidelity_guidance` block passed to Irene in the context envelope:

```yaml
fidelity_guidance:
  literal_visuals:
    - description: "Dual-axis chart from page 7 of Tejal's notes"
      source_ref: "TEJAL_Notes.pdf#page7"
      rebranded_asset_path: "course-content/staging/ad-hoc/rebranded-assets/slide-03-chart.png"
  literal_text:
    - description: "Knowledge check teaser — exact 10 KC topics from Chapters 2 & 3"
      source_ref: "extracted.md#Chapter 2 Knowledge Check"
```

If the user has no fidelity needs, `fidelity_guidance` is omitted (all slides default to creative).

## Imagine Handoff Checkpoint

After Irene returns the slide brief with fidelity tags, Marcus surfaces `literal-visual` slides to the user:

1. Present tagged slides: "Irene flagged Slides N and M as needing rebranded visuals. Source images are from [source]. Are the rebranded PNGs ready?"
2. Confirm assets: user drops PNGs to designated location and provides hosted URLs (Phase 1: upload to Gamma workspace, get CDN URL)
3. Validate URLs: for each `diagram_cards[].image_url`, verify HTTPS-accessible with image content type (uses `validate_image_url()` from `skills/gamma-api-mastery/scripts/gamma_operations.py`)
4. Build `diagram_cards` block for Gary's envelope:
   ```yaml
   diagram_cards:
     - card_number: 3
       image_url: "https://gamma.app/hosted/..."
       placement_note: "Primary visual, full-width"
       required: true
   ```
5. Only unblock Gary delegation after all `diagram_cards` URLs are validated

**Imagine export specs:** Highest resolution, 16:9 aspect ratio, PNG format.

**Asset drop locations:** `course-content/staging/ad-hoc/rebranded-assets/` (ad-hoc) or `course-content/staging/rebranded-assets/` (default).

## Production Planning

After identifying intent and completing fidelity discovery, Marcus builds a production plan:

1. **Consult reference libraries** — Re-read `resources/style-bible/` for brand/visual standards and `resources/exemplars/` for platform allocation policies and pattern matching
2. **Map content type to workflow** — Use the Content Type Vocabulary table to identify the specialist sequence
3. **Check for exemplar matches** — If an exemplar exists for this content type, use it as the starting pattern
4. **Apply platform allocation** — Use the allocation policy from exemplars to determine Canvas vs CourseArc vs other platform routing
5. **Sequence stages** — Order specialist invocations with dependency awareness (e.g., script before voiceover, outline before slides)
6. **Insert checkpoint gates** — Place human review points at quality-critical junctures
7. **Present plan to user** — Show the planned workflow with stages, specialists, and checkpoints. Recommend the plan with rationale, invite adjustments

For skeleton plan generation from templates, invoke `./scripts/generate-production-plan.py` with a workflow template id or alias and the module structure. The script loads the canonical registry at `./references/workflow-templates.yaml`, so composite workflows and simpler asset workflows share one planning source.

## Platform Allocation Intelligence (Story G.1)

When a production plan includes deployment routing, Marcus invokes
`./scripts/platform_allocation.py` with a content profile and applies the
result as a recommendation, not a hard lock.

Required behavior:

1. Present recommendation with reasoning from the allocation matrix.
2. Offer conversational options: accept, modify, or override.
3. If user modifies or overrides, rerun or record the final decision.
4. Save final allocation rationale to Marcus sidecar patterns for learning.

Reference inputs:

- `resources/exemplars/_shared/platform-allocation-matrix.yaml`
- `state/config/course_context.yaml`
- `resources/exemplars/policies/canvas-coursearc-platform-allocation-policy.md`

## Specialist Delegation

When a production plan stage requires a specialist:

1. **Check availability** — Resolve specialist path from `skills/bmad-agent-marcus/references/specialist-registry.yaml`. If the specialist is missing from the registry or the resolved path does not exist, gracefully degrade (see `production-coordination/references/delegation-protocol.md`).
2. **Pack context envelope** — Build the outbound context from the current run state (see envelope spec below).
3. **Log delegation** — `log_coordination.py log --run-id {id} --agent {specialist} --action delegated --payload '{envelope}'`
4. **Invoke specialist** — Load the registry-resolved `SKILL.md` path for the target specialist and present the context envelope as the task.
5. **Receive results** — Specialist returns a mediated result payload: one or more artifact paths, quality assessment, parameter decisions, any specialist-specific payload fields, and explicit downstream routing notes.
6. **Log completion** — `log_coordination.py log --run-id {id} --agent {specialist} --action completed --payload '{result}'`
7. **Save parameter decisions** — If the specialist discovered effective parameters, note them for `patterns.md` (default mode).

If specialist status is `blocked`, Marcus must execute blocked recovery:

1. Summarize blocker cause and impact in user-facing language.
2. Offer recovery options: resolve input gap, skip stage, or reroute to alternate specialist.
3. If user chooses skip/reroute, log decision rationale in coordination and continue run.
4. If user chooses resolve, gather missing inputs and re-dispatch the same stage.

When specialist is unavailable: acknowledge the gap, suggest what can be done now (outline, planning), skip the stage, and continue the workflow.

## Specialist Handoff Protocol

When delegating to a specialist agent or skill, Marcus passes a **context envelope**:

**Outbound (to specialist):**
- Production run ID
- Content type and scope (course/module/lesson)
- Learning objectives for the target lesson
- User constraints (timeline, preferences, specific requirements)
- Relevant style bible sections (matched to specialist domain)
- Applicable exemplar references
- Any previous revision feedback
- Governance block with:
  - `invocation_mode` (`delegated` or `standalone`)
  - `current_gate` (active pipeline gate/stage)
  - `authority_chain` (ordered non-empty routing chain; first hop is escalation target)
  - `decision_scope` (judgment dimensions the specialist owns vs restricted)
  - `allowed_outputs` (artifact/output types the specialist may emit in this call)

Use canonical `decision_scope` values from `docs/governance-dimensions-taxonomy.md`.

Specialists must enforce governance constraints before work execution:
- planned output types must be contained in `governance.allowed_outputs`
- planned judgments must be contained in `governance.decision_scope.owned_dimensions`
- out-of-scope requests must be returned to `governance.authority_chain[0]` with a `scope_violation` payload

`authority_chain` routing rule:
- Specialists do not traverse the chain.
- Specialists always set `route_to = authority_chain[0]` and return control.
- Marcus owns all subsequent rerouting decisions.

**Inbound (from specialist):**

```yaml
status: completed|blocked|failed
artifact_paths:
  - "course-content/staging/..."
primary_artifact: "course-content/staging/..."
artifact_type: lesson_plan|slide_brief|narration_script|segment_manifest|slide_deck|audio_bundle|assembly_guide
quality_assessment:
  passed: true|false
  score: 0.0-1.0
  notes: ["...", "..."]
parameter_decisions:
  - key: "gamma.style"
    value: "professional-medical"
    rationale: "Matched style bible visual identity"
specialist_payload:
  gary_slide_output: []        # Gary -> Marcus -> Irene Pass 2
  segment_manifest: null       # Irene -> Marcus -> ElevenLabs/Kira/Compositor
  narration_outputs: []        # ElevenLabs -> Marcus -> Quinn-R/Compositor
recommendations: ["...", "..."]
downstream_routing:
  next_specialist: "content-creator"
  requires_hil_gate: true
  next_input_artifacts: ["course-content/staging/..."]
issues: ["...", "..."]  # empty if none
scope_violation: null       # object when request exceeds allowed outputs or decision scope
```

## Run Finalization

When all production stages are complete and the user approves the final checkpoint:

1. **Confirm delivery** — Verify all assets are in their target locations (staging or published)
2. **Update chronology** — Record the completed run in `chronology.md` with run ID, content type, module/lesson, timestamps, and outcome
3. **Capture patterns** — Extract parameter decisions and workflow sequences that worked well into `patterns.md`
4. **Archive run state** — Update the production run record in SQLite to `completed` status with `completed_at` timestamp
5. **Present summary** — "Run complete! Here's what we produced: [artifact list]. Everything's in [location]. Anything else, or shall we wrap up?"

In ad-hoc mode, steps 2-4 are skipped (no state writes). Step 5 still runs — the user always gets a summary.

## Run Execution

When the user approves a production plan and Marcus begins executing the workflow, Marcus uses the `production-coordination` skill to manage run state.

Precondition: Session-Start Settings Handshake has already confirmed both execution mode and quality preset.

Run using the confirmed settings:

1. **Create run** — `manage_run.py create --content-type {type} --course {code} --module {mod} --preset {preset} --mode {execution_mode} --stages-json '{stages}'`
   Returns a run ID. Marcus stores this for the session and reports: "Production run started — run ID [id]. First up: [stage description]."

2. **Advance through stages** — As each stage completes (specialist returns output), call `manage_run.py advance {run_id}`. Marcus reports the next stage conversationally.

3. **Human checkpoints** — When the workflow reaches a checkpoint stage, call `manage_run.py checkpoint {run_id}`. Marcus presents the work for review (see HC capability in `checkpoint-coord.md`).

4. **Record decisions** — When the user approves, call `manage_run.py approve {run_id}`. If revision is requested, note the feedback and re-engage the specialist.

5. **Finalize** — When all stages are approved, call `manage_run.py complete {run_id}`. Marcus runs the Run Finalization sequence below.

6. **Check status** — At any point, `manage_run.py status {run_id}` returns JSON with current stage, completion count, execution mode, and quality preset. Marcus translates this into natural reporting.

When specialist agents are unavailable (not yet built), Marcus reports the gap at step 2 and suggests alternatives — see graceful degradation in the Capabilities section of SKILL.md.

## Run Baton & Authority Contract

For every active production run, Marcus maintains a lightweight run baton in `state/runtime/` using `manage_baton.py`.

**Baton required fields:**
- `run_id`
- `orchestrator`
- `current_gate`
- `invocation_mode`
- `allowed_delegates`
- `escalation_target`
- `blocking_authority`

**Lifecycle discipline:**
1. At run start, initialize baton: `manage_baton.py init <run_id> ...`
2. At each gate transition, update gate: `manage_baton.py update-gate <run_id> <gate>`
3. On run completion/cancellation, baton clears automatically via `manage_run.py complete|cancel`

**Direct specialist invocation guardrail:**
If a user invokes a specialist directly during an active Marcus-run pipeline, specialists should respond:

"Marcus is running [run_id], currently at [gate]. Redirect, or enter standalone consult mode?"

If user explicitly chooses standalone consult mode, specialist may proceed in consult-only behavior and must not mutate active production run state.

## Full Pipeline Dependency Graph (Narrated Lesson)

```
User notes + guidance
    │
    ▼
Marcus -> Texas: wrangling directive → validated source bundle (extracted.md + extraction-report.yaml + metadata.json)
    │  (Texas validates extraction quality: proportionality check, cross-validation against reference assets, fallback chains)
    │  (Texas returns: complete / complete_with_warnings / blocked)
    ▼
Marcus -> Vera: G0 fidelity check (source bundle completeness)
    │  (Vera loads extracted.md + metadata.json, checks section coverage, provenance, PDF degradation)
    │  (Circuit breaker: critical/high → halt/retry to Texas; medium → warning)
    ▼  (PASS)
Marcus -> Irene Pass 1: Lesson Plan + Slide Brief
    │
    ▼
Marcus -> Vera: G1 fidelity check (lesson plan vs. source bundle)
    │  (Vera compares LOs to source themes, validates source_refs, checks structure)
    │  (Circuit breaker: critical/high → halt/retry to Irene; medium → warning)
    ▼  (PASS)
Marcus -> Vera: G2 fidelity check (slide brief vs. lesson plan)
    │  (Vera loads G2 L1 contract, compares slide brief to lesson plan)
    │  (Circuit breaker: critical/high → halt/retry to Irene; medium → warning)
    ▼  (PASS)
Marcus -> Quinn-R: G2 quality review
    │
    ▼  [HIL Gate 1 via Marcus: Review lesson plan + slide brief]
    │
Marcus -> Gary: Gamma slide deck -> PNGs + PPTX
    │  (Gary reads Irene's slide brief from Marcus's envelope; theme/template options routed back through Marcus)
    ▼
Marcus -> Vera: G3 fidelity check (generated slides vs. slide brief)
    │  (Vera invokes PPTX bridge + image bridge, compares to slide brief)
    │  (Circuit breaker: critical/high → halt/retry to Gary; medium → warning)
    ▼  (PASS)
Marcus -> Quinn-R: G3 quality review
    │
    ▼  [HIL Gate 2 via Marcus: Review slides — CRITICAL: narration cannot start until approved]
    │
Marcus -> Irene Pass 2: Narration Script + Segment Manifest
    │  (Irene reads Gary's actual PNGs via Marcus-carried gary_slide_output + perception_artifacts)
    ▼
Marcus -> Vera: G4 fidelity check (narration script vs. lesson plan + actual slides)
    │  (Vera verifies narration matches perceived slide content and lesson plan assessment items)
    │  (Circuit breaker: critical/high → halt/retry to Irene; medium → warning)
    ▼  (PASS)
Marcus -> Quinn-R: G4 quality review
    │
    ▼  [HIL Gate 3 via Marcus: Review script & manifest]
    │
Marcus -> Voice Director: preview-only catalog voice selection round
    │  (returns existing ElevenLabs sample links for current/default voice + alternatives,
    │   or three description-led recommendations; no synthesis spend here)
    ▼  [HIL Voice Selection via Marcus]
    │
Marcus -> ElevenLabs Agent: narration MP3 + VTT + SFX + music
    │  (reads manifest for narration_text, sfx, music cues, voice selection)
    │  (writes narration_duration, narration_file, narration_vtt back to manifest)
    ▼
Marcus -> Vera: G5 fidelity check (audio vs. narration script)
    │  (Vera invokes audio bridge for STT, compares transcript to script, checks WPM and pronunciation)
    │  (Circuit breaker: critical/high → halt/retry to ElevenLabs; medium → warning)
    ▼  (PASS)
Marcus -> Kira: silent video clips
    │  (runs only after Marcus has received narration_duration from ElevenLabs)
    │  (reads manifest for visual_source, visual_mode, narration_duration)
    │  (writes motion_asset_path/motion_duration_seconds and keeps visual_file bound to the approved still)
    ▼
Marcus -> Quinn-R: pre-composition validation
    │
    ▼
Marcus -> Compositor Skill: generate Descript Assembly Guide from completed manifest
    │
    ▼  [Human: assembles + tweaks in Descript -> exports MP4 + VTT]
    │
    ▼
Marcus -> Quinn-R: post-composition validation
    │
    ▼  [HIL Gate 4 via Marcus: Final video review]
    │
Done: asset ready for Canvas deployment
```

**Marcus orchestrates this entire flow.** Key invariants:
- No user-visible specialist-to-specialist communication. Specialists may depend on prior specialist artifacts, but Marcus always receives, validates, and re-packs those artifacts before the next delegation.
- **Vera before Quinn-R at every gate** — fidelity is a precondition for quality. If fidelity fails, Quinn-R never sees the artifact.
- Gary before Irene Pass 2 (narration complements actual slides)
- ElevenLabs before Kira (Kira needs `narration_duration` to set clip duration)
- Both before compositor (compositor needs complete manifest)
- Quinn-R pre-composition before Descript handoff
- Quinn-R post-composition before Gate 4

## Fidelity Assessor Delegation

When delegating to Vera (Fidelity Assessor), Marcus passes a fidelity context envelope:

**Outbound (to Vera):**
```yaml
gate: "G0"                     # G0 | G1 | G2 | G3 (more gates in future stories)
production_run_id: "{id}"
artifact_paths:
  # G0: source bundle directory
  bundle_dir: "course-content/staging/.../source-bundles/{bundle-name}/"
  # G1: lesson plan path
  lesson_plan: "course-content/staging/.../lesson-plan.md"
  # G2: slide brief path
  slide_brief: "course-content/staging/.../slide-brief.md"
  # G3: PPTX + PNG paths
  pptx: "course-content/staging/.../deck.pptx"
  pngs: ["course-content/staging/.../card-01.png", "..."]
source_of_truth_paths:
  # G0: original source material paths (from metadata.json provenance)
  source_materials: ["path/to/notion-export.md", "path/to/document.pdf"]
  # G1: source bundle
  bundle_dir: "course-content/staging/.../source-bundles/{bundle-name}/"
  # G2: lesson plan
  lesson_plan: "course-content/staging/.../lesson-plan.md"
  # G3: slide brief
  slide_brief: "course-content/staging/.../slide-brief.md"
fidelity_contracts_path: "state/config/fidelity-contracts/"
run_mode: "default"             # or "ad-hoc"
governance:
  invocation_mode: "delegated"
  current_gate: "G2"
  authority_chain: ["marcus", "quality-reviewer"]
  decision_scope:
    owned_dimensions: ["source_fidelity"]
    restricted_dimensions: ["quality_standards", "instructional_design"]
  allowed_outputs:
    - "fidelity_trace_report"
    - "fidelity_findings"
```

**Inbound (from Vera):**
```yaml
status: passed | failed | warning
gate: "G2"
verdict:
  pass: true | false
  fidelity_score: 0.0-1.0
  highest_severity: critical | high | medium | none
findings:
  omissions: [{...}]
  inventions: [{...}]
  alterations: [{...}]
circuit_breaker:
  triggered: true | false
  action: halt | retry | proceed
  remediation_target: "texas" | "irene" | "gary" | "elevenlabs-voice-director"
  remediation_guidance: "..."
```

**Marcus's circuit breaker handling:**
- `halt` → Stop pipeline, present full Fidelity Trace Report to user. No auto-retry. Human must review and either waive or request re-work.
- `retry` → Re-invoke producing agent (Irene at G2, Gary at G3) with Vera's remediation guidance in the envelope. After producing agent revises, re-delegate to Vera for fresh evaluation. If second failure → escalate to user.
- `proceed` → Pass Vera's findings as advisory attachment to Quinn-R's quality review envelope. Findings are visible at the HIL gate.

## Irene Two-Pass Delegation

Marcus must invoke Irene **twice** for full lesson builds:

**First delegation (Pass 1):**
```yaml
envelope:
  production_run_id: {id}
  content_type: "lesson-plan"
  module_lesson: {module}/{lesson}
  learning_objectives: [{...}]
  pass: 1
  governance:
    invocation_mode: "delegated"
    current_gate: "G1"
    authority_chain: ["marcus"]
    decision_scope:
      owned_dimensions: ["instructional_design"]
      restricted_dimensions: ["source_fidelity", "quality_standards"]
    allowed_outputs: ["lesson_plan", "slide_brief"]
```

**Second delegation (Pass 2 — after Gate 2 approval):**
```yaml
envelope:
  production_run_id: {id}
  content_type: "narration-script"
  module_lesson: {module}/{lesson}
  learning_objectives: [{...}]
  pass: 2
  governance:
    invocation_mode: "delegated"
    current_gate: "G4"
    authority_chain: ["marcus", "fidelity-assessor", "quality-reviewer"]
    decision_scope:
      owned_dimensions: ["instructional_design"]
      restricted_dimensions: ["source_fidelity", "quality_standards"]
    allowed_outputs: ["narration_script", "segment_manifest", "pairing_references"]
  gary_slide_output:
    - slide_id: "slide-01"
      file_path: "course-content/staging/{lesson_id}/slides/card-01.png"
      card_number: 1
      visual_description: "{Gary's description of what's on the slide}"
    # ... one entry per Gary PNG
  perception_artifacts:
    - slide_id: "slide-01"
      artifact_path: "course-content/staging/{lesson_id}/slides/card-01.png"
      modality: "image"
      confidence: "HIGH"
      extracted_text: "{text visible on the slide}"
      layout_description: "{visual layout description}"
      visual_elements: [{type, description, position}]
    # ... one perception result per Gary PNG (from sensory bridge cache)
```

**Note:** `perception_artifacts[]` is the canonical perception output from the shared sensory bridges — structured, confidence-scored, and auditable. Irene uses this as ground truth for what is visually on screen. `gary_slide_output[].visual_description` remains useful for creative context but is not the authoritative perception. The Fidelity Assessor at G4 can audit Irene's narration against the same `perception_artifacts[]`, creating a closed auditable loop.

## Compositor Delegation

The Compositor skill generates a Descript Assembly Guide from a completed manifest. Marcus invokes it after Quinn-R's pre-composition pass:

```yaml
envelope:
  production_run_id: {id}
  segment_manifest: "course-content/staging/{lesson_id}/manifest.yaml"
  output_path: "course-content/staging/{lesson_id}/descript-assembly-guide.md"
  governance:
    invocation_mode: "delegated"
    current_gate: "G5"
    authority_chain: ["marcus", "quality-reviewer"]
    decision_scope:
      owned_dimensions: ["tool_execution_quality.composition"]
      restricted_dimensions: ["source_fidelity", "quality_standards", "instructional_design"]
    allowed_outputs: ["artifact_paths", "recommendations"]
```

Until Story 3.5 is implemented, Marcus presents the completed manifest to the user and guides manual Descript assembly using the composition architecture decision record as reference.

## Descript Manual-Tool Handoff

Descript is the sole composition platform — a Tier 3 manual-tool. Marcus hands off to the user with:
1. The Descript Assembly Guide (from Compositor, or manually composed from manifest)
2. All asset file paths (narration MP3s, VTT, video clips, slide PNGs, SFX, music)
3. Track assignment instructions (V1: video/images, A1: narration, A2: music, A3: SFX)
4. Timing table (segment start times from manifest narration_duration values)
5. Music cue instructions (duck/swell/out timestamps)
6. Transition specs per segment

## Asset-Lesson Pairing Enforcement

Every educational artifact produced must be paired with instructional context. Before marking any production step complete, verify:
- The asset has a parent lesson in the course hierarchy
- Learning objectives are documented and traceable
- Assessment alignment is explicit (if applicable)

If pairing cannot be established, halt and surface the gap to the user. This invariant is never waived.
