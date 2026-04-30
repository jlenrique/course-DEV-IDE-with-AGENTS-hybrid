---
name: external-specialist-registry
description: Canonical registry of specialist agents Marcus routes to, with context-envelope guidance
---

# External Specialist Registry

Canonical list of specialist agents Marcus delegates to, with the style-bible and envelope context each specialist expects. Paired with `specialist-registry.yaml` (canonical path lookup) and `workflow-templates.yaml` (workflow-stage routing).

## External Skills

| Capability | Target Skill | Status | Context Passed |
|------------|-------------|--------|----------------|
| APP runtime readiness and health monitoring | `app_session_readiness` | active (Story G.3) | Run mode, repo root, optional `with_preflight` composition flag; invocation phrases: "run session readiness", "check runtime before production" |
| MCP/API connectivity verification | `pre-flight-check` | active | Tool inventory reference from `resources/tool-inventory/` |
| Workflow stage management, authority baton lifecycle, and state transitions | `production-coordination` | active | Run ID, current stage/gate, baton authority context |
| Production run analysis and reports | `run-reporting` | active | Run ID, chronology data |
| Tool ecosystem monitoring and documentation synthesis | `tool-ecosystem-synthesis` | active (Story G.2) | Optional DB path + doc-sources inventory + specialist sidecar pattern files |
| Predictive workflow optimization recommendations | `predictive-workflow-optimization` | active (Story 10.1) | New run context (course/module/preset/content type) + prior run telemetry |
| Style guide reading/writing, parameter elicitation | `parameter-intelligence` | active | Style bible path, parameter context — via `manage_style_guide.py` |
| Source extraction with quality validation, cross-validation, fallback chains | `bmad-agent-texas` (Texas) | active | Source manifest, course content dir, quality gate thresholds — via delegation contract |
| Tool API doc refresh, research, validation | `tech-spec-wrangler` | active | Tool name, doc-sources.yaml path, optional research query |
| Exemplar study, reproduction, comparison, regression | `woodshed` | active | Tool name, exemplar ID, evaluator reference |

## External Specialist Agents

| Content Domain | Target Agent | Status | Style Bible Context Passed |
|----------------|-------------|--------|---------------------------|
| Creative frame and experience emphasis | `bmad-agent-cd` (Creative Director) | active (Wave 2B) | Plain-language operator preference, run constraints, style-bible signals, and Marcus-owned envelope context; returns structured creative directive only |
| Instructional design, Pass 1 (lesson plan + slide brief) | `content-creator` (Irene) | active | Learning objectives, Bloom's level, content type, module/lesson, user constraints |
| Instructional design, Pass 2 (narration script + segment manifest) | `content-creator` (Irene) | active | Same + approved `gary_slide_output` (PNG paths + visual descriptions); for motion-enabled runs also pass `motion_enabled` and `context_paths.motion_plan` so Irene hydrates manifest motion fields and returns motion perception confirmations |
| Slide/presentation generation | `gamma-specialist` (Gary) | active | Color palette, typography, visual hierarchy; Gary presents theme/template options before generating and may stage tracked-mode literal-visual source assets into managed Git-host storage before dispatch |
| Educational video generation, B-roll, concept animation, transitions | `kling-specialist` (Kira) | active | Visual tone, color palette, source assets, Gate 2M motion-plan rows, and segment manifest; Kira always produces silent video |
| Voice synthesis, narration, SFX, music | `elevenlabs-specialist` | active | Voice/tone standards, segment manifest |
| Animation storyboard and build guidance (manual-tool) | `vyond-specialist` | active (Story 5.1) | Character style, scene rhythm, instructional emphasis, accessibility constraints |
| Bespoke scientific/medical image prompting (manual-tool) | `midjourney-specialist` | active (Story 5.1) | Visual tone, realism constraints, style references, prohibited artifacts |
| Storyline/Rise interaction authoring guidance (manual-tool) | `articulate-specialist` | active (Story 5.1) | Interaction rubric, branching criteria, remediation rules, SCORM standards |
| Descript composition assembly guide | `compositor` | active | Completed segment manifest path with still and motion asset references |
| Descript run-scoped operator brief + Automation Advisory (post-compositor) | `bmad-agent-desmond` (Desmond) | active | `assembly-bundle/` path, `DESCRIPT-ASSEMBLY-GUIDE.md`, run id, workflow template, motion flag, Quinn-R / operator notes; writes `DESMOND-OPERATOR-BRIEF.md` |
| Fidelity verification — G0 (source bundle completeness) | `fidelity-assessor` (Vera) | active | Gate, bundle dir, source material paths, fidelity contracts path, run mode. See `./conversation-mgmt.md` for envelope spec. |
| Fidelity verification — G1 (lesson plan vs. source bundle) | `fidelity-assessor` (Vera) | active | Gate, lesson plan path, bundle dir. Vera runs BEFORE Quinn-R — fidelity is a precondition for quality. |
| Fidelity verification — G2 (slide brief vs. lesson plan) | `fidelity-assessor` (Vera) | active | Gate, slide brief path, lesson plan path. |
| Fidelity verification — G3 (generated slides vs. slide brief) | `fidelity-assessor` (Vera) | active | Gate, PPTX + PNG paths, slide brief path. |
| Fidelity verification — G4 (narration script vs. slides + lesson plan) | `fidelity-assessor` (Vera) | active | Gate, narration script, segment manifest, perception_artifacts, lesson plan. |
| Fidelity verification — G5 (audio vs. narration script) | `fidelity-assessor` (Vera) | active | Gate, audio file paths, narration script. Vera invokes audio bridge for STT. |
| Quality assurance — pre-composition pass | `quality-reviewer` (Quinn-R) | active | Segment manifest path, audio/video asset paths, `review_pass: pre-composition` |
| Quality assurance — post-composition pass | `quality-reviewer` (Quinn-R) | active | Final MP4, VTT paths, `review_pass: post-composition` |
| Graphic design and visual assets (manual-tool) | `canva-specialist` | active (Story 3.8) | Copy intent, visual hierarchy goals, template constraints, export targets |
| LMS course structure, modules, assignments, quizzes | `canvas-specialist` | active (Story 3.6) | Allocation policy, exemplar matrices, deployment manifest |
| Survey/evaluation creation | `qualtrics-specialist` | active (Story 3.7) | Learning objectives, assessment constraints, deployment target, response requirements |
| CourseArc deployment, LTI 1.3 embedding, SCORM and accessibility checks (manual-tool) | `coursearc-specialist` | active (Story 6.1) | LTI settings, SCORM package metadata, interaction accessibility checklist |

## Descript Manual-Tool Handoff

After Compositor generates the Descript Assembly Guide (or Marcus constructs it from the manifest), Marcus delegates to **Desmond** (`bmad-agent-desmond`) for **`DESMOND-OPERATOR-BRIEF.md`** (run-tailored Descript steps + mandatory **Automation Advisory**), then hands **compositor guide + Desmond brief + asset paths** to the user for manual assembly in Descript. Assembly in Descript remains human-executed. See `./conversation-mgmt.md` for handoff details and `skills/bmad-agent-desmond/references/automation-advisory.md` for advisory rules.

## Context Envelope

When delegating to any specialist, Marcus passes a **context envelope**: production run ID, content type, module/lesson identifier, user constraints, relevant style-bible sections, and applicable exemplar references. Specialists return: artifact path, quality self-assessment, and parameters used.

See `./conversation-mgmt.md` for the authoritative envelope schema and governance-block contract.
