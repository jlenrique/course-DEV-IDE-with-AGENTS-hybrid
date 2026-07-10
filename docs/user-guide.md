# User Guide — Course Content Production System

## Current Status - Marcus-SPOC Lesson Planning (2026-07-09)

This guide now starts from the Marcus-SPOC local runtime: Marcus is the operator-facing orchestrator for a real APP production run, not a concierge/proofing vehicle. Proofing sessions can reveal product defects, but they are not the product target.

### What Works Now

- The durable Phase-2 baseline includes S7 course-source assessment/bundles, the S8 planning-to-selection bridge, the Irene planning-context handoff, and Marcus `plan-ratify` Claim A/B through the live bespoke Irene Pass-1 close at `fa48fb5b`.
- Operators can ratify planning context for purpose, audience, learning objectives, source assessment, and collateral intent. Irene Pass-1 can receive that context as framing while the source corpus remains the topic authority.
- The ratified collateral-intent path can drive local W5 composition on the Marcus-SPOC runtime. The active product-gap frontier is automatic `lesson_plan["collateral"]` to `ComponentSelection`, interactive planning dialogue, SME routing, ingestion hardening, and additional collateral projectors.

### What Is Still Fenced

- Do not treat S8 as open work. New work should build on the bridge rather than replacing the selection contract.
- Full free-form SPOC planning, Gamma/published-walk claims, HAI/PHS real ingestion, per-SME voice/styleguide routing, projector-family expansion, and workbook prose uplift remain residual or in-flight until committed close evidence says otherwise.
- Never ad-hoc-edit approved styleguide registry guides. Non-Tejal production must not silently borrow Tejal voice or approval routing.

### How To Read The Rest Of This Guide

Use this current-status block first, then use the older sections below for workflow vocabulary and historical operator patterns. Current project status lives in [`docs/STATE-OF-THE-APP.md`](STATE-OF-THE-APP.md), [`SESSION-HANDOFF.md`](../SESSION-HANDOFF.md), and [`next-session-start-here.md`](../next-session-start-here.md).

## Legacy Context

> **Migration Status (refreshed 2026-05-07 at pre-Trial-3 cleanup S5 Tier-2):** Migration unconditionally SHIPPED 2026-04-27. Slab 7 orchestrational arc COMPLETE (7a+7b+7c closed 2026-05-01 / 2026-05-01 / 2026-05-07). Pre-Trial-3 cleanup arc S1-S6 currently in progress (S1+S2+S3+S4 closed; S5+S6 in flight). **First tracked trial (Trial-3) launches post-cleanup-close** against v5 canonical pack + post-Slab-7c substrate. v5 canonical pack: `docs/workflow/production-prompt-pack-v5-narrated-lesson-with-video-or-animation.md`. Trial methodology: `docs/trials/methodology.md`. Legacy v4.2 retained as mapping-checklist legacy-axis frozen authority.


> ## MIGRATION STATUS BANNER (refreshed 2026-04-28)
>
> **This guide reflects the PRE-MIGRATION primary-repo workflow** (Cursor IDE chat + prompt-pack v4.x). The hybrid clone on `dev/langchain-langgraph-foundation` has **MIGRATED**: migration unconditionally SHIPPED 2026-04-27 (commit `97842ac`); Slab 6 trial-experience bundle 3/3 CLOSED 2026-04-28 (Step 02A prior-run defaults + Irene Pass 2 authoring template + HUD per-step expandable summaries); first tracked trial UNBLOCKED. Marcus orchestrator runs the production-graph runner against the manifest; specialists invoke through ProductionDispatchAdapter; DecisionCards fire at G1/G2C/G3/G4 with HIL operator verdict via CLI/MCP/FastAPI; checkpoint pause/resume verified end-to-end.
>
> **For migration-native user workflow (post-SHIP), see:**
> - **[`docs/operator/production-trial-playbook.md`](operator/production-trial-playbook.md)** — start-to-stop production-run playbook at action-by-action granularity (in-progress fill during first tracked trial). The migration-native equivalent of legacy prompt-pack + cheat-sheet.
> - **[`docs/operator/production-run-swimlane.md`](operator/production-run-swimlane.md)** — at-a-glance swimlane for typical animated-slides + video production runs (HIL gates G1/G2C/G3/G4 highlighted; cumulative pace + watch-for rubric). Best high-level entry point.
> - **[`docs/operator/trial-run-runbook.md`](operator/trial-run-runbook.md)** — first-trial step-by-step (transport choice + corpus + DecisionCard inspection + verdict flow + override + replay).
> - **[`docs/operator/hud-guide.md`](operator/hud-guide.md)** — HUD reading guide including Slab 6.5 per-step expandable summaries.
> - **[`docs/operator/step-02a-prior-run-defaults.md`](operator/step-02a-prior-run-defaults.md)** — Slab 6.3 prior-run directives surfacing.
> - **[`docs/operator/validation-scripts.md`](operator/validation-scripts.md)** — operator-run validation script catalog (5 validation scripts + 4 ceremony scripts).
> - **[`README.md`](../README.md)** — top-of-repo project orientation + status-by-slab + quick-start.
>
> **Scope of this legacy content (post-SHIP):** the prompt-pack v4.x workflow described below is HISTORICAL REFERENCE for the pre-migration primary-repo. It is preserved to keep audit-trail continuity from pre- to post-migration. For active production-content workflow, consult the migration-native see-also list above.

---

**Audience:** Course creators and instructional designers using the system to produce educational content.
**Last Updated:** 2026-04-12 (migration banner actualized 2026-04-26) | **Project Phase:** Epics 1–14 complete (primary); hybrid clone is M5 SHIP-CONDITIONAL through 2026-05-03.

---

## Quick Start

Get from zero to your first content artifact in under 15 minutes.

### Prerequisites

- **Cursor IDE** installed with this repository open
- API keys configured (ask your admin — see the [Admin Guide](admin-guide.md) for setup)
- Pre-flight check passed (green status for your target tools)

### Your First Session

1. **Open Cursor IDE** and open a new agent chat (Cmd/Ctrl+L)
2. **Activate Marcus** — type: *"Talk to Marcus"* or *"I'd like to produce some content"*
3. Marcus greets you by name, reports system status, and asks what you'd like to create
4. **Tell Marcus what you need** — for example:
   - *"Create a presentation for Module 2, Lesson 3 on clinical trial design"*
   - *"Draft a knowledge check quiz for the pharmacology module"*
   - *"Help me plan the assessment strategy for Module 4"*
5. Marcus handles the rest — tool selection, specialist coordination, quality checks — and presents you with work at **checkpoint gates** for your review and approval
6. **Review and approve** — Marcus stages all drafts in `course-content/staging/` for your review before anything goes to `course-content/courses/`

That's it. Everything else is depth you discover as you work with Marcus.

---

## How the System Works (What You Need to Know)

### Marcus is Your Single Point of Contact

Marcus is a veteran executive producer for medical education content. You talk to Marcus; Marcus handles everything else. You never need to think about which tools, APIs, or agents are involved — Marcus coordinates all of that behind the scenes.

Think of Marcus as your **general contractor**: you describe what you want built, Marcus assembles the right specialists, manages the work, and brings you results for approval at every stage.

### Run Setting Axis 1: Execution Mode (Tracked/Default vs Ad-Hoc)

| Execution Mode | Purpose | Assets Go To | State Tracking |
|------|---------|-------------|----------------|
| **Tracked (default)** | Full production operations with persistent run records | `course-content/staging/` → your review → `course-content/courses/` | Full — preferences learned, patterns captured |
| **Ad-Hoc** | Experimentation and quick exploration | Scratch/staging area | Paused — nothing permanent saved |

Switch modes by telling Marcus:
- *"Switch to ad-hoc mode"* — for experimenting without committing
- *"Switch to tracked mode"* or *"Switch to default mode"* — resume full tracking (same setting)
- *"What mode am I in?"* — Marcus confirms your current mode

**Quality checks always run in both modes.** The difference is only whether the system remembers your preferences for next time.

### Run Setting Axis 2: Quality Preset (Explore vs Draft vs Production)

Marcus uses run presets that control how strictly quality is enforced:

| Preset | When to Use | Human Review | Quality Level |
|--------|------------|:------------:|:-------------:|
| **explore** | Quick experiments, idea generation | No | Minimal |
| **draft** | Working drafts, iterative development | Yes | Standard |
| **production** | Publication-ready artifact strictness | Yes | Full pipeline |
| **regulated** | Compliance-grade (accreditation) | Yes | Strictest + audit trail |

The default preset is **draft**. Tell Marcus: *"Use production preset for this run."*

Important terminology:
- "Production session" can mean operating the APP for real course work (not developing the APP).
- "Production preset" is the quality strictness level on the preset axis.

These are related but not the same setting.

### The Content Workflow

Every piece of content follows this path:

```
Your Intent → Marcus Plans → Specialists Create → Fidelity + Quality Review → Your Approval → Published
```

1. **Intent** — You describe what you want: learning objectives, audience, constraints, content type
2. **Planning** — Marcus consults the style bible, checks exemplars, and builds a production plan
3. **Creation** — Specialist agents generate content (slides, audio, assessments, etc.)
4. **Fidelity check (Vera)** — For pipeline artifacts, the **Fidelity Assessor (Vera)** checks whether outputs stay faithful to their source of truth (traceability; omissions, inventions, and alterations). Serious issues can stop the run before routine quality review.
5. **Quality review (Quinn-R)** — The **Quality Guardian (Quinn-R)** checks brand, accessibility, instructional soundness, learner-effect alignment, and related quality dimensions. This is separate from source-faithfulness.
6. **Your review** — Marcus presents the work at a checkpoint gate. You approve, request changes, or redirect
7. **Staging** — Drafts land in `course-content/staging/` for your edit and signoff
8. **Promotion** — You (or Marcus at your direction) move approved content to `course-content/courses/`
9. **Publishing** — Content is deployed to Canvas, CourseArc, or other platforms using the supported specialist or manual path for that platform (see [Tools in the Ecosystem](#tools-in-the-ecosystem))

Gate order and automated assessment flow are summarized in [`docs/fidelity-gate-map.md`](fidelity-gate-map.md). Which role may judge what (orchestration, pedagogy, tool execution, fidelity) is summarized in [`docs/lane-matrix.md`](lane-matrix.md).

### Workflow Templates

Marcus now routes narrated production through two explicit workflow templates:

- `narrated-deck-video-export`
  - Standard narrated deck workflow
  - Uses [production-prompt-pack-v4.1-narrated-deck-video-export.md](workflow/production-prompt-pack-v4.1-narrated-deck-video-export.md)
- `narrated-lesson-with-video-or-animation`
  - Motion-enabled narrated workflow
  - Uses [production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md](workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md)

`DOUBLE_DISPATCH` is an optional branch inside either workflow. It does not create a third workflow family.

**Experience profiles + clusters (v4.2+):**
- If `EXPERIENCE_PROFILE` is set, Marcus runs a **Creative Directive** step (Prompt 4.75) before Irene Pass 1 and persists `narration_profile_controls`.
- If `CLUSTER_DENSITY` is enabled, Marcus adds cluster prompt engineering (6.2), dispatch sequencing (6.3), and the G2.5 coherence gate before Storyboard A.

### Narrated Workflow Templates

Marcus selects between two narrated workflow templates:

- `narrated-deck-video-export` for standard narrated slide production with static approved slide PNGs through Irene Pass 2
- `narrated-lesson-with-video-or-animation` for motion-enabled narrated production with Gate 2M, motion generation/import, and Motion Gate before Irene Pass 2

Prompt-pack family:
- standard/non-motion runs use `docs/workflow/production-prompt-pack-v4.1-narrated-deck-video-export.md`
- motion-enabled runs use `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`

`DOUBLE_DISPATCH` is an optional Gary-stage branch inside either workflow. Gary produces A/B variants, you select winners, and Marcus collapses the canonical deck before narration or motion proceeds.

For motion-enabled narrated runs, Marcus now has two canonical utility steps before Irene Pass 2:
- `skills/bmad-agent-marcus/scripts/build-pass2-inspection-pack.py` builds reviewer-facing slide and motion inspection artifacts under `recovery/inspection/`
- `skills/bmad-agent-marcus/scripts/prepare-irene-pass2-handoff.py` refreshes `pass2-envelope.json`, archives stale rerun outputs, and writes `pass2-prep-receipt.json`

In both narrated workflows, Irene Pass 2 now carries explicit timing metadata in the segment manifest so slide-length variation is explainable rather than accidental:
- `timing_role`
- `content_density`
- `visual_detail_load`
- `duration_rationale`
- `bridge_type`

Marcus's Pass 2 validator treats these as auditable handoff expectations and warns when runtime-band drift, weak timing rationale, or intro/outro bridge cadence gaps suggest the script is becoming mechanically uniform.

### Production run authority (baton)

When Marcus is running a **production run**, the system may hold an active **run baton** (a small JSON file under `state/runtime/`). If you open a **specialist agent directly** (for example Gary or Irene) while that run is active, the specialist should prompt you: continue with Marcus for the run, or enter **standalone consult mode** for a side conversation that does not change the active run. You do not need to edit baton files yourself; Marcus and the specialists follow the contract in the implementation skills.

### Checkpoint Gates (Human-in-the-Loop)

You stay the instructor of record. Marcus **never** publishes content without your approval. At every significant production stage, Marcus pauses and presents:

- What was created
- How it aligns with learning objectives
- Fidelity findings (when Vera has run) and quality findings (when Quinn-R has run), when relevant
- Any quality concerns or decisions that need your input
- A clear recommendation with rationale

You can:
- **Approve** — move forward
- **Request changes** — Marcus sends it back to the specialist with your feedback
- **Redirect** — change direction entirely
- **Override** — Marcus respects your creative judgment even when it differs from standard patterns

### Source Materials

Marcus can pull your reference materials into the production context:

- **Notion** — Course development notes, syllabi, design documents. Tell Marcus: *"Pull my Module 3 notes from Notion"*
- **Box Drive** — Locally synced files. Tell Marcus: *"Check Box Drive for the pharmacology references"*
- **Web exemplars** — Share a URL, or save a page with Playwright in Cursor and point Marcus at the HTML file; **Texas** (source wrangler agent) extracts, validates, and delivers `extracted.md` bundles for Irene and Gary

Marcus proactively offers to pull source materials before starting production tasks. Context enrichment before creation beats revision after.

---

## What You Can Ask Marcus To Do

### Content Creation
- *"Create a presentation on [topic] for [module/lesson]"*
- *"Draft a knowledge check for [learning objective]"*
- *"Generate a voiceover script for [presentation]"*
- *"Build a discussion board prompt for [topic]"*

### Planning and Strategy
- *"Help me plan the content for Module 5"*
- *"What's the best content type for teaching [concept]?"*
- *"Show me how this lesson maps to course learning objectives"*

### Review and Quality
- *"Review [content] for accessibility compliance"*
- *"Check brand consistency on these slides"*
- *"Run an editorial review on the Module 2 lesson plan"*

### System Operations
- *"Run a pre-flight check"* — verify all tools are working
- *"What's the status of the current production run?"*
- *"Switch to ad-hoc mode"*
- *"Show me what's in staging"*
- *"Refresh tool knowledge"* — ask Marcus to refresh current API/tool documentation before a production task

### Source Materials
- *"Pull my notes from Notion for this module"*
- *"Check Box Drive for the case study files"*

---

## Content Standards

### Style Bible

All content follows the standards in your **Master Style Bible** (`resources/style-bible/master-style-bible.md`). This is human-curated — you control it. Marcus and all specialists read it fresh for every task. Key elements:

- **Brand colors:** JCPH Navy (#1e3a5f), Medical Teal (#4a90a4)
- **Typography:** Montserrat (headlines), Open Sans (body), Source Sans Pro (data)
- **Voice:** Clear, direct, respectful of physician expertise, evidence-based
- **Accessibility:** WCAG 2.1 AA compliance, 4.5:1 contrast ratio, alt text on all visuals

To update the style bible, edit the file directly. Changes take effect on the next production task — no restart needed.

### Run Presets

Run presets are the quality-strictness axis (separate from execution mode). If no preset is specified, Marcus uses **draft**.

---

## Content Organization

### Where Your Content Lives

```
course-content/
├── staging/              ← Agent drafts awaiting your review
│   └── m03-intro-ai/    ← One folder per active module
├── courses/              ← Approved, published content
│   └── course-slug/
│       └── module-01-topic/
│           ├── lessons/          ← Narrative Markdown
│           ├── presentations/    ← Slide source files
│           └── assets/           ← Images, diagrams
└── _templates/           ← Reusable outlines and scaffolds
```

### The Staging → Courses Workflow

1. Agents always write to `course-content/staging/`
2. You review and edit for accuracy, examples, and institutional policy
3. You promote approved material to `course-content/courses/`
4. Platform publishing follows from the `courses/` directory

**Never edit directly in `courses/` during production.** Use staging as your review buffer.

### Definition of Done (per lesson or deck)

Before promoting content from staging:

- [ ] Learning objectives stated and aligned to activities
- [ ] You personally verified facts and institution-specific policy
- [ ] Accessibility checklist considered (contrast, alt text, captions)
- [ ] Visible in target platform (Canvas page / LTI link) in preview mode

### Narrated slide assembly (Descript)

Current workflow family:
- Standard narrated runs use `docs/workflow/production-prompt-pack-v4.1-narrated-deck-video-export.md`.
- Motion-enabled narrated runs use `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`.
- `DOUBLE_DISPATCH` is optional in either workflow and always collapses back to a single authorized winner deck in `authorized-storyboard.json`.
- For the motion-enabled + double-dispatch happy path, use `tests/happy-path-simulation-motion-double-dispatch-20260405.md`.

For narrated slide packs, the team assembles in **Descript** using a single **assembly bundle** folder under `course-content/staging/…`: segment manifest, narration audio and WebVTT captions, ElevenLabs summaries, the Descript Assembly Guide, **`DESMOND-OPERATOR-BRIEF.md`** (run-tailored Descript steps and **Automation Advisory**, prompt **14.5** in the prompt packs; skill `bmad-agent-desmond`), and **copies** of Gate-approved slide stills under `visuals/`. Before ElevenLabs synthesis begins, Marcus can also run a preview-only voice-selection checkpoint that gives you catalog sample links for the carry-forward/default voice plus alternatives, or three description-led recommendations if you describe the ideal narrator. Automation runs **`sync-visuals`** on the manifest so those PNGs sit beside the other assets (not only under the Gary export tree) before you import into Descript. You normally do not run commands yourself—Marcus or the developer does; exact steps live in the [Developer guide — Compositor assembly bundle CLI](dev-guide.md#compositor-assembly-bundle-cli).

The ElevenLabs path now preserves script-led pacing as the primary driver. The system can pass mild voice-direction controls like `speed`, `emotional_variability`, and `pace_variability`, but those are refinements, not substitutes for Irene's writing judgment.

If a motion/perception step reports missing `ffmpeg`, do not assume the binary is absent just because it is not on `PATH`. The repo records the bundled location in [local-binary-paths.md](resources/tool-inventory/local-binary-paths.md), and repo scripts should resolve it automatically through `scripts/utilities/ffmpeg.py`.

### Happy-path walkthrough: user + Marcus + “X-ray” (planner / checklist)

This section is **one coherent story for the standard narrated deck workflow**: a **narrated slide presentation exported as video** with **HTTPS-hosted custom images** on selected slides (literal cards), **creative** Gamma for the rest, **ElevenLabs** audio, then **compositor → Descript**. In the workflow template registry this path is `narrated-deck-video-export` (canonical, no aliases), and it maps to `docs/workflow/production-prompt-pack-v4.1-narrated-deck-video-export.md`. The motion-enabled sibling path is `narrated-lesson-with-video-or-animation`, which maps to `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md` and inserts Gate 2M, motion generation/import, and Motion Gate before Irene Pass 2. Use this walkthrough as (1) a **narrative walkthrough**, (2) a **trial-run planner**, and (3) a **step checklist**—same steps, three roles.

If you enable motion for a narrated run:
- Gate 2M happens after the authorized winner deck exists
- motion generation/import and Motion Gate happen before Irene Pass 2
- `DOUBLE_DISPATCH`, if enabled, still happens earlier as a Gary-only branch before winner authorization

**Is this clear and doable?** Yes: it matches how the repo is designed (Irene two-pass, mixed-fidelity Gamma + `diagram_cards`, manifest SSOT, compositor bundle). **What to watch anyway:**

- **Chat vs state:** Marcus should persist mode via `manage_mode.py` / `mode_state.json`, not only say “we’re in ad-hoc” in chat.
- **New Cursor thread:** Paste **run id** + lesson slug + paths so context isn’t lost.
- **Two Gamma jobs** (creative + literal): ensure exports are **mapped to `card_number`** and `gary_slide_output[].file_path` is real before Pass 2.
- **Costs:** In the standard workflow, meaningful spend ramps after Gate 3 once the voice-preview checkpoint is closed and ElevenLabs/downstream assembly begin. In the motion-enabled workflow, motion spend is introduced earlier via Gate 2M and Motion Gate controls.
- **All-literal decks** with only `diagram_cards`: confirm `execute_generation` path with devs (mixed creative+literal is the well-wired happy path here).
- **URLs:** Custom images must pass **`validate_image_url`** (HTTPS, image content-type)—see Marcus **Imagine handoff** in `skills/bmad-agent-marcus/references/conversation-mgmt.md`.

**Hypothetical run identifiers**

| Item | Example value |
|------|----------------|
| Production run id | `APP-RUN-C1M3L2-HTN-20260330` |
| Lesson slug (folder) | `C1-M3-L2-ambulatory-bp` |
| Topic | Ambulatory blood-pressure patterns in resistant hypertension |
| Custom diagrams (HTTPS for `diagram_cards`) | Slide 4: `https://media.university.example/course-assets/htn-renal-diagram.png` — Slide 7: `https://media.university.example/course-assets/abpm-48h-grid.png` |

**Phase 1 vs Phase 2 — what you review (instructor checkpoints)**

| Phase | Blueprint you own | Open / edit these (typical names) | You are checking |
|-------|-------------------|-------------------------------------|------------------|
| **Irene Pass 1** (before Gary) | Lesson plan + **slide brief** | `lesson-plan.md`, `slide-brief.md` under lesson staging | LOs, sequence, **which slides are `creative` vs `literal-text` / `literal-visual`**, where custom URLs will land, voice of content |
| **Irene Pass 2** (after Gate 2, before heavy audio/composition spend) | **Paired** narration script + **segment manifest** | `narration-script.md`, `segment-manifest.yaml` | Spoken copy matches **approved slide PNGs** (including embedded custom art), segment IDs line up, and downstream audio/composition intent is coherent. In the motion-enabled workflow, motion fields are hydrated from `motion_plan.yaml` before this phase. |

Always edit **script + manifest together** so segment IDs and copy do not drift.
The Gate 4 fidelity contract treats them as a pair too, so any Pass 2 template change must keep both contract references aligned before the run proceeds.

**Where control docs and assets live (default mode happy path)**

Path roots follow `skills/bmad-agent-marcus/references/mode-management.md`. **Ad-hoc:** prefix lesson and bundle paths with `course-content/staging/ad-hoc/` (and use `ad-hoc/source-bundles/…` for wrangler); no durable ledger/sidecar learning (`docs/ad-hoc-contract.md`).

```
course-content/staging/
├── source-bundles/APP-RUN-C1M3L2-HTN-20260330/     # optional G0: extracted.md, metadata.json
└── C1-M3-L2-ambulatory-bp/                         # lesson workspace
    ├── lesson-plan.md
    ├── slide-brief.md                              # fidelity_per_slide; drives Gary
    ├── gamma-export/                               # Gary exports: PNG/PDF; unified order by card_number
    ├── narration-script.md
    ├── segment-manifest.yaml                       # SSOT for assembly; filled in downstream
    └── assembly-bundle/                            # single folder for Descript handoff
        ├── segment-manifest.yaml                   # copy or canonical; paths updated after sync-visuals
        ├── DESCRIPT-ASSEMBLY-GUIDE.md
        ├── audio/
        ├── captions/
        ├── video/                                  # optional motion assets for motion-enabled runs only
        └── visuals/                                # after compositor sync-visuals: slide stills localized here
```

`state/runtime/mode_state.json` — default vs ad-hoc. `resources/style-bible/master-style-bible.md` — authoritative look/feel (read fresh each run).

**Custom images → Gary (happy path = mixed deck)**

Deck includes **both** creative slides and **literal** slides 4 & 7. Marcus builds **`diagram_cards`** for those card numbers; `skills/gamma-api-mastery/scripts/gamma_operations.py` **`generate_deck_mixed_fidelity`** runs two Gamma calls, then **`reassemble_slide_output`** sorts by **`card_number`**. In tracked/default mode, literal-visual cards may start as local preintegration PNGs and APP will stage them to managed Git hosting before dispatch. In ad-hoc mode, Gary still requires already-hosted HTTPS image URLs.

Literal-visual policy: those slides are full-slide image-only. Any explanatory/supporting text belongs in Irene Pass 2 narration/script, not on the slide payload.

**Walkthrough table — user view, X-ray, review, paths**

The **model prompts** for each step (what to type to Marcus) are in the next subsection—use them with the same step numbers.

| # | You ↔ Marcus (summary) | X-ray — APP behind the scenes | Review ✓ (planner tick) | Paths / artifacts (default mode) |
|---|-------------------------|----------------------------------|-------------------------|-----------------------------------|
| 0 | Open the run: mode, run id, pre-flight | `read-mode-state.py`, `manage_mode.py` → `mode_state.json`; pre-flight skill checks MCP/API | ☐ Mode is default (or ad-hoc if you intend trial scratch) ☐ Tools green for Gamma and EL; include Kling only if this is the motion-enabled workflow | `state/runtime/mode_state.json` |
| 1 | Answer fidelity questions (literal slides, exact text) | Marcus fills `fidelity_guidance` for Irene; tracked mode may stage local preintegration PNGs later, ad-hoc still requires pre-hosted URLs | ☐ You listed slides needing **literal** treatment ☐ For tracked mode: local source PNGs identified; for ad-hoc: HTTPS URLs ready before Gary | Optional PNG drop: `course-content/staging/rebranded-assets/` |
| 2 (opt.) | Optional source pull | Source wrangler → Notion client | ☐ Bundle usable for Irene | `source-bundles/APP-RUN-C1M3L2-HTN-20260330/extracted.md` |
| 3 | Kick off Irene Pass 1; review outputs | Irene Pass 1: `bmad-agent-content-creator` | **☐ PHASE 1 REVIEW:** `lesson-plan.md` + `slide-brief.md` — LOs, order, **fidelity per slide** | `…/C1-M3-L2-ambulatory-bp/lesson-plan.md`, `slide-brief.md` |
| 4 | **HIL Gate 1** — approve or revise pedagogy | Human checkpoint; no API spend for slides yet | ☐ Gate 1 sign-off | — |
| 5 | Supply literal-visual assets; build operator packet | Marcus compiles literal-visual list + per-slide build instructions from Irene cards and diagram mapping, then blocks dispatch until all required cards are operator-ready | ☐ `literal-visual-operator-packet.md` reviewed ☐ Operator confirms each required PNG is created and downloaded | `literal-visual-operator-packet.md`, `gary-diagram-cards.json` |
| 5B | Pre-dispatch confirmation + Gary run | `validate_image_url` for hosted refs or tracked-mode preintegration publish/substitution; explicit pre-dispatch confirmation; Gary envelope: `fidelity_per_slide` + `diagram_cards`; literal-visual payloads are URL-only (no support prose); `execute_generation` → mixed fidelity → reorder by `card_number` | ☐ Hosted URLs validated or tracked-mode staging receipt clean ☐ Explicit confirmation captured before publish/dispatch side effects | `gamma-export/` (exports + `gary_slide_output` metadata; optional `literal_visual_publish`) |
| 6 | **HIL Gate 2** — approve deck | PDF for human review per Gary SKILL; PNG for pipeline | ☐ Visuals on-brand ☐ Literal slides match supplied art ☐ Order matches lesson | Slide PNGs under `gamma-export/` (representative) |
| 7 | Irene Pass 2 after Gate 2 | Irene sees **`gary_slide_output`** and narrates from approved local slide PNGs; any `literal_visual_publish` receipt is provenance only | **☐ PHASE 2 REVIEW:** `narration-script.md` + `segment-manifest.yaml` — copy matches **approved** slides | Same lesson folder |
| 7B | Storyboard review with script context | Marcus regenerates storyboard using `gary-dispatch-result.json` + `segment-manifest.yaml` before audio finalization | ☐ Storyboard row order and script alignment approved explicitly | `storyboard/storyboard.json`, `storyboard/index.html`, `authorized-storyboard.json` |
| 8 | **HIL Gate 3** — approve script / audio plan | Locks manifest before ElevenLabs and downstream assembly spend | ☐ Gate 3 sign-off | — |
| 9 | Confirm fidelity + quality runs (or ask Marcus to run them) | `bmad-agent-fidelity-assessor`, `bmad-agent-quality-reviewer`, optional `quality-control` scripts, sensory bridges | ☐ No critical blockers (or you accept override) | Reports per governance; ad-hoc: transient observability |
| 10 | HIL voice preview before audio spend | `elevenlabs_operations.py` → catalog preview recommendations | ☐ `voice-selection.json` approved | `voice-preview-options.json`, `voice-selection.json` |
| 11 | Delegate ElevenLabs from approved manifest | `elevenlabs_operations.py` → manifest write-back (`narration_duration`, paths). When `--voice-selection` is provided, the tool verifies locked-artifact hashes before any API spend and auto-resolves the approved voice. | ☐ Audio paths populated on manifest | `assembly-bundle/audio/`, `captions/` |
| 11 | Motion-enabled extension only | Use the motion-specific workflow template and prompt pack instead of inserting Kling into the standard path here | ☐ Motion handled via Gate 2M → Motion Gate before Irene Pass 2 | `motion_plan.yaml`, motion asset paths |
| 12 | Quinn-R pre-composition (or ask Marcus to invoke) | `review_pass: pre-composition` | ☐ Pre-composition OK | — |
| 13 | Run compositor bundle | `compositor_operations.py` | ☐ `visuals/` populated ☐ Guide readable | `assembly-bundle/` |
| 14 | Descript assembly (you) | Manual; follow `DESCRIPT-ASSEMBLY-GUIDE.md` | ☐ Final export matches intent | User-chosen export location |

**Model prompts for Marcus (copy-paste — happy path)**

Replace bracketed bits with your lesson; keep **run id** and **paths** consistent across a single trial.

**Step 0 — Mode, run id, pre-flight**

```
Marcus, I’m starting a production run. Use default mode and the draft preset unless I say otherwise.
Run id: APP-RUN-C1M3L2-HTN-20260330. Lesson folder slug: C1-M3-L2-ambulatory-bp.
Topic: ambulatory BP patterns in resistant hypertension for advanced learners.
Please persist mode with manage_mode if needed, confirm mode_state.json, run pre-flight for Gamma and ElevenLabs, and include Kling only if this run is using the motion-enabled workflow template. Then report status.
Also run `.\.venv\Scripts\python.exe -m scripts.utilities.venv_health_check`; if `overall_status` is `fail`, stop and report `one_step_repair` before any delegation.
```

*Ad-hoc trial variant:* same text but ask for **ad-hoc mode** and paths under `course-content/staging/ad-hoc/…`.

**Step 1 — Fidelity discovery**

```
Marcus, run your standard fidelity discovery for this run.
For visuals: slides 4 and 7 must be literal-visual with fixed diagrams. In tracked/default mode I may supply local preintegration PNGs for APP-managed staging; in ad-hoc mode I’ll supply HTTPS URLs. All other slides are creative Gamma.
For text: [e.g. no exact exam items on slides / or list what must be literal].
Capture this in fidelity_guidance for Irene.
```

**Step 2 — Source material (optional)**

```
Marcus, pull my Module 3 hypertension development notes from Notion into a source bundle for run APP-RUN-C1M3L2-HTN-20260330 and point Irene at extracted.md for context.
```

**Step 3 — Irene Pass 1**

```
Marcus, delegate Irene Pass 1 for lesson C1-M3-L2-ambulatory-bp. Use the style bible and fidelity_guidance.
Produce lesson-plan.md and slide-brief.md under course-content/staging/C1-M3-L2-ambulatory-bp/ with fidelity per slide (creative vs literal-text vs literal-visual).
```

**Step 4 — HIL Gate 1 (Phase 1 review)**

```
Gate 1: I’ve reviewed lesson-plan.md and slide-brief.md in staging. APPROVED — proceed to Imagine URL handoff and Gary.
```
*Or for changes:* `Gate 1: REVISION — [specific edits to objectives, slide order, or fidelity tags]. Please have Irene update the briefs before we generate slides.`

**Step 5 — Literal-visual assets + Gary (diagram_cards)**

```
Marcus, here are the literal-visual assets for diagram_cards (literal slides only):
- card_number 4: https://media.university.example/course-assets/htn-renal-diagram.png
- card_number 7: course-content/staging/rebranded-assets/abpm-48h-grid.png
First, produce literal-visual-operator-packet.md with per-slide source context, Irene constraints, and expected preintegration_png_path values, then wait for my explicit confirmation that required local PNGs are ready. After confirmation: if the run is tracked/default, stage any local preintegration PNGs to the managed Git-host destination before Gary dispatch; if the run is ad-hoc, stop and ask me for HTTPS-hosted URLs instead. Then build diagram_cards for Gary’s envelope and delegate Gary to generate the full deck (mixed creative + literal) with PNG + PDF export into course-content/staging/C1-M3-L2-ambulatory-bp/gamma-export/. Return gary_slide_output with file_path filled after download and include literal_visual_publish if staging occurred.
```

**Step 6 — HIL Gate 2 (deck review)**

```
Gate 2: I’ve reviewed the PDF and PNGs. APPROVED — slides match style bible; literal slides 4 and 7 match my supplied art; card order is correct. Proceed to Irene Pass 2.
```
*Or:* `Gate 2: REVISION — [slide numbers and requested changes]. Regenerate or adjust before Pass 2.`

**Step 7 — Irene Pass 2**

```
Marcus, delegate Irene Pass 2 using the approved gary_slide_output. If Gary returned literal_visual_publish, pass it as provenance only; Irene should still ground narration on the approved slide PNGs in gary_slide_output. Write narration-script.md and segment-manifest.yaml in course-content/staging/C1-M3-L2-ambulatory-bp/, paired by segment id. Include downstream audio and composition intent per the manifest template. If this is a motion-enabled run, follow the separate motion workflow template and hydrate motion fields from motion_plan.yaml before Pass 2.
```

**Step 8 — HIL Gate 3 (script + manifest)**

```
Gate 3: I’ve reviewed narration-script.md and segment-manifest.yaml together. APPROVED — proceed to Vera, Quinn-R, then ElevenLabs and downstream assembly per the locked manifest.
```
*Or:* `Gate 3: REVISION — [segment ids and edits]. Update both files before audio generation.`

**Step 8A — Storyboard review before audio finalization**

```
Marcus, regenerate storyboard using gary-dispatch-result.json plus segment-manifest.yaml and present the manifest-derived summary. I will approve slide+script alignment here before ElevenLabs generation.
```

**Step 9 — Fidelity + quality (after Gate 3)**

```
Marcus, run the pipeline fidelity and quality checks on the current artifacts per fidelity-gate-map (Vera then Quinn-R as applicable). Summarize blockers before we spend on ElevenLabs.
```

**Step 9A — Voice preview before ElevenLabs**

```
Marcus, before ElevenLabs synthesis, have the Voice Director return catalog preview links for the previously used lesson voice (or the default voice for a new presentation) plus two APP-selected alternatives. If I instead describe the ideal voice, return three description-led recommendations. After I approve one, write voice-selection.json and use that selection for synthesis.
```

**Step 10 — ElevenLabs**

```
Marcus, delegate the Voice Director to run manifest-driven narration (and any specified SFX/music) from elevenlabs-audio, writing outputs under course-content/staging/C1-M3-L2-ambulatory-bp/assembly-bundle/ and updating segment-manifest.yaml with narration_duration, narration_file, and narration_vtt paths.
```

**Step 11 — Motion-enabled extension only**

```
For motion-enabled runs, do not insert Kling here into the standard path. Use the motion-specific prompt pack and execute Gate 2M → motion generation/import → Motion Gate before Irene Pass 2. The standard narrated deck workflow skips this step.
```

If this is the standard narrated deck workflow: skip this step.

**Step 12 — Quinn-R pre-composition**

```
Marcus, invoke Quinn-R pre-composition review on the assembly bundle and manifest. Report pass/fail before compositor.
```

**Step 13 — Compositor**

```
Marcus, run compositor sync-visuals on course-content/staging/C1-M3-L2-ambulatory-bp/assembly-bundle/segment-manifest.yaml (or the canonical manifest path you’re using), then regenerate DESCRIPT-ASSEMBLY-GUIDE.md in the same folder. Confirm visuals/ contains Gate-2-approved stills.
```

**Step 14 — Descript (you)**

No Marcus prompt required. Open **`DESCRIPT-ASSEMBLY-GUIDE.md`** in `assembly-bundle/`, import assets from **`audio/`**, **`captions/`**, **`video/`**, **`visuals/`**, and export your final program.

### Consolidated prompt sequence (reusable for similar runs)

Use these prompts in order. Keep placeholders (`[ ... ]`) consistent across the full run.

**Prompt 1 — Open run + enforce settings handshake**

```
Marcus, start a production operations run.
Run id: [RUN_ID]. Lesson slug: [LESSON_SLUG]. Topic: [TOPIC].
Confirm both settings before execution: execution mode [tracked/ad-hoc] and quality preset [explore/draft/production/regulated].
Run pre-flight for required tools and report pass/fail.
```

**Prompt 2 — Source ingest guardrail (no ad-hoc scripts)**

```
Marcus, for all source ingest in this run, use only official skill entrypoints and no temporary custom scripts.
For each ingest, report: entrypoint used, output bundle path, and provenance metadata.
```

**Prompt 3 — Wrangle primary PDF source**

```
Marcus, delegate PDF ingestion to Texas and write a validated source bundle:
[PDF_PATH]
Return extracted.md + metadata.json path and page coverage confirmation.
```

**Prompt 4 — Wrangle roadmap image source**

```
Marcus, ingest this roadmap image through the existing image-capable path (sensory-bridges route), then write a standard source bundle:
[ROADMAP_IMAGE_PATH]
Return extracted text summary and provenance in metadata.
```

**Prompt 5 — Consolidate sources into study brief**

```
Marcus, produce one merged study brief from all source bundles for [RUN_ID].
Call out any conflicts, ambiguities, or missing context and give a go/no-go recommendation for Irene Pass 1.
```

**Prompt 6 — Fidelity discovery**

```
Marcus, run standard fidelity discovery and capture fidelity_guidance for Irene.
Mark which slides are creative vs literal-text vs literal-visual.
```

**Prompt 7 — Irene Pass 1**

```
Marcus, delegate Irene Pass 1 for [LESSON_SLUG] using style bible + merged study brief + fidelity_guidance.
Produce lesson-plan.md and slide-brief.md in staging.
```

**Prompt 8 — Gate 1 decision**

```
Gate 1 decision: [APPROVED or REVISION].
If revision, apply only the listed changes and re-present lesson-plan.md and slide-brief.md.
```

**Prompt 9 — Gary deck generation with literal visuals**

```
Marcus, build diagram_cards for these literal slides:
- card_number [N]: [HTTPS URL or local preintegration PNG path]
- card_number [N]: [HTTPS URL or local preintegration PNG path]
If the run is tracked/default, stage any local preintegration PNGs before Gary dispatch; if the run is ad-hoc, stop unless every card is already HTTPS-hosted. Then delegate Gary for mixed-fidelity generation and return gary_slide_output with file_path populated.
```

**Prompt 10 — Gate 2 decision**

```
Gate 2 decision: [APPROVED or REVISION].
If revision, list slide-level edits and regenerate before Pass 2.
```

**Prompt 11 — Irene Pass 2**

```
Marcus, delegate Irene Pass 2 using approved gary_slide_output.
Produce narration-script.md + segment-manifest.yaml with stable segment IDs.
```

**Prompt 12 — Gate 3 decision**

```
Gate 3 decision: [APPROVED or REVISION].
If revision, update script and manifest together before audio/video generation.
```

**Prompt 13 — Fidelity + quality before spend**

```
Marcus, run Vera then Quinn-R on current artifacts and summarize blockers before ElevenLabs and downstream assembly spend.
```

**Prompt 14 — ElevenLabs execution**

```
Marcus, before synthesis, run the preview-only voice-selection checkpoint and write voice-selection.json. After approval, run manifest-driven ElevenLabs generation and update segment-manifest.yaml with narration_duration, narration_file, and narration_vtt.
```

**Prompt 15 — Motion-enabled workflow branch**

```
If this lesson requires motion, switch to the motion-enabled workflow template and use the dedicated motion prompt pack. Do not branch from the standard narrated deck workflow here.
If no video segments exist, explicitly confirm skip.
```

**Prompt 16 — Pre-composition quality + compositor bundle**

```
Marcus, run Quinn-R pre-composition review, then run compositor sync-visuals and regenerate DESCRIPT-ASSEMBLY-GUIDE.md.
Confirm assembly-bundle has manifest, guide, audio, captions, visuals, and optional video.
```

**Prompt 17 — Trial log update at each milestone**

```
Marcus, append this run update to the trial running log as Success or Failure with one-line cause and corrective action.
```

**Prompt 18 — Shift close**

```
CLOSE SHIFT. Execute docs/workflow/production-session-wrapup.md fully and output one completed Shift Close Record.
```

**Trial-run checklist (copy — same steps as # column)**  
☐ 0 Mode + pre-flight ☐ 1 Fidelity + URLs ready ☐ 2 Source (opt.) ☐ **3 Phase 1 files** ☐ 4 Gate 1 ☐ 5 Gary + diagram_cards ☐ 6 Gate 2 ☐ **7 Phase 2 files** ☐ 8 Gate 3 ☐ 9 Vera/Quinn-R ☐ 9A Voice preview ☐ 10 ElevenLabs ☐ 11 Motion branch only if using the motion workflow template ☐ 12 Quinn-R pre-comp ☐ 13 Compositor ☐ 14 Desmond operator brief (`DESMOND-OPERATOR-BRIEF.md`) ☐ 15 Descript assembly

**Trial-run running log (active)**

- 2026-03-29 | Failure | When attempting to study course material, Marcus created an ad-hoc PDF-reading script instead of routing through source wrangler and existing PDF-reading skills.
- 2026-03-30 | Success | APC C1-M1 SME PDF ingested via **official** `source-wrangler`: `wrangle_local_pdf` + `write_source_bundle` → `course-content/staging/ad-hoc/source-bundles/apc-c1m1-tejal-2026-03-29/` (`extracted.md`, `metadata.json`, provenance `local_pdf`, pypdf 24/24).
- 2026-03-30 | Success | `APC Content Roadmap.jpg` ingested via **official** sensory-bridges path: `bridge_utils.perceive(modality=image, gate=G0)` → canonical perception validated with `validate_response`, then **official** `write_source_bundle` → `course-content/staging/ad-hoc/source-bundles/apc-content-roadmap-image/` (includes `raw/perception.json`). Vision transcription supplied per `png_to_agent` / SKILL contract (IDE vision on scaled derivative; **MEDIUM** confidence — verify fine print on full-resolution JPG).
- 2026-03-30 | Deliverable | Merged planning brief for Irene / Pass 1: `course-content/staging/ad-hoc/source-bundles/apc-c1m1-merged-study-brief.md` (PDF + roadmap synthesis, mismatches, Pass 1 recommendation).
- 2026-03-30 | Note | Repro CLI for image→bundle (optional): `scripts/utilities/build_image_source_bundle.py` — **thin wrapper only**; it does not replace skill logic and requires a JSON payload with vision fields (`_perception_input.json` pattern).
- 2026-03-30 | Policy | `scripts/utilities/build_image_source_bundle.py` is a **provisional helper**. Default production ingestion remains Marcus → Source Wrangler (+ sensory-bridges where needed). Use the helper only for reproducible replay when a validated perception payload already exists.

**Assembly-bundle deliverable (before Descript):** One **`assembly-bundle/`** folder: `segment-manifest.yaml`, `DESCRIPT-ASSEMBLY-GUIDE.md`, **`DESMOND-OPERATOR-BRIEF.md`**, `audio/`, `captions/`, optional `video/`, **`visuals/`** after `sync-visuals`, plus **`motion/`** when the motion workflow applies — ready for Descript.

---

## Tools in the Ecosystem

Current support note:
- Treat the table below as capability-oriented, not a backlog snapshot.
- Canvas, Qualtrics, and Canva all have usable repo paths today, but the exact specialist/script/manual route still depends on your institution and credentials.
- Ask Marcus which path is currently approved for your run before you begin platform deployment or assessment work.

You don't need to know how these tools work — Marcus and the specialist agents handle them. But here's what's available:

| What | Tool | How It's Used |
|------|------|--------------|
| **Slides/Presentations** | Gamma | AI-generated professional slides (specialist **Gary**) |
| **Voiceover/Audio** | ElevenLabs | Natural-sounding narration synthesis (Voice Director specialist) |
| **Video** | Kling | Text/image-to-video and related flows (specialist **Kira**) |
| **LMS Management** | Canvas LMS | Course structure, modules, assignments, quizzes (API + MCP in repo; use Marcus to route through the current Canvas path for your institution) |
| **Surveys/Assessments** | Qualtrics | Professional survey and assessment creation (availability depends on the active specialist/manual path in your environment) |
| **Course Dev Notes** | Notion | Pull reference materials into production context (Texas agent + API) |
| **Source Files** | Box Drive | Access locally synced cloud files |
| **Design/Graphics** | Canva | Design-guidance and Canva-specific workflow support; some programmatic paths still depend on current API/MCP constraints |
| **Composition** | Descript (manual) | Final assembly of narrated decks; compositor skill produces assembly guides and syncs stills |
| **Hosting** | Panopto | Video hosting (API client in repo; credential-dependent) |

Some tools (Vyond, CourseArc, Articulate) require manual operation — Marcus provides detailed specs and you execute in the tool's own interface.

**Support note:** Tool support varies by current specialist coverage, API credentials, and MCP constraints. Ask Marcus which path is active today for your institution before starting a production run.

---

## Tips for Working with Marcus

1. **Be specific about learning objectives** — Marcus uses them to align everything. "Create slides about pharmacology" is okay; "Create slides covering drug interaction mechanisms aligned to CLO-3 at Bloom's application level" is much better.

2. **Front-load your constraints** — Tell Marcus early about time limits, modality requirements, platform targets, or special audience considerations.

3. **Use ad-hoc mode for exploration** — When you're brainstorming or trying ideas, switch to ad-hoc. Switch back to default when you're ready to produce.

4. **Review checkpoint outputs carefully** — Your domain expertise is irreplaceable. Marcus handles production quality; you handle instructional accuracy and clinical correctness.

5. **Update the style bible when standards evolve** — If you decide Medical Teal should be used differently, or you want a new voice style for a specific audience, update `resources/style-bible/master-style-bible.md` directly.

6. **Trust the staging workflow** — Resist the urge to edit published content directly. Staging exists to protect your students from seeing in-progress work.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Marcus says a tool isn't responding | Ask: *"Run pre-flight check"* — Marcus will diagnose and suggest fixes |
| Content doesn't match your style expectations | Check `resources/style-bible/master-style-bible.md` — is it up to date? |
| Quality review flags something you disagree with | You can override any quality decision — tell Marcus your reasoning |
| Marcus seems to have forgotten context | Sessions are independent. Start with: *"Here's where we left off..."* |
| Staging content looks wrong in Canvas | Run a platform smoke test first — *"Preview this in Canvas student view"* |

For system setup issues, see the [Admin Guide](admin-guide.md). For technical questions, see the [Developer Guide](dev-guide.md).

---

## Glossary

| Term | Meaning |
|------|---------|
| **APP** | **Agentic Production Platform** — this environment: IDE-hosted agents, tools, memory, and governance together |
| **Marcus** | The master orchestrator agent — your single point of contact |
| **Vera** | The **Fidelity Assessor** — source-faithfulness and provenance checks (typically before Quinn-R on pipeline artifacts) |
| **Quinn-R** | The **Quality Guardian** — brand, accessibility, instructional soundness, learner-effect quality, and related standards |
| **Checkpoint gate** | A pause point where Marcus presents work for your review |
| **Style bible** | The authoritative brand and content standards document |
| **Staging** | The review area where agent-created content waits for your approval |
| **Run preset** | A quality enforcement level (explore, draft, production, regulated) |
| **Ad-hoc mode** | Experimental mode — assets go to scratch, state tracking paused |
| **Default mode** | Production mode — full state tracking and learning |
| **HIL** | Human-in-the-loop — you review and approve before publication |
| **Specialist agent** | A focused expert (e.g. Gary for Gamma, Irene for instructional design) that Marcus delegates to |
| **Memory sidecar** | Where agents remember preferences and patterns between sessions |
| **Woodshed** | Exemplar-driven practice workflow agents use to prove tool mastery (optional unless you choose to run it) |
