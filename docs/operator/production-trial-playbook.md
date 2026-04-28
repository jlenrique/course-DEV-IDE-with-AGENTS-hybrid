# Production Trial Playbook — start-to-stop, action-by-action

**Status:** SKELETON (sections + structure ready; data-entry-by-data-entry blocks marked `<!-- FIRST-TRIAL-FILL -->` are populated from observation during first tracked trial run; do NOT speculate the operator inputs/outputs in advance).

**Authoring mode:** the playbook is meant to be open during the first tracked trial. As the operator runs each step, the corresponding `<!-- FIRST-TRIAL-FILL -->` block gets populated with: the actual command typed, the actual output observed, the actual decision made. Action-by-action accuracy comes from observation, not from speculation.

**Audience:** operator running a production trial on the migrated LangGraph runtime. Replaces the legacy "production prompt-pack v4.x" + "operator cheat sheet" pattern with a single end-to-end runbook.

**Last updated:** 2026-04-28 (skeleton authored post-Slab-6 close; first-trial fill pending).

---

## How to use this playbook

1. **Read top to bottom before your first run.** Get oriented on the phase structure + decision points + escape hatches.
2. **Open this file in a separate editor pane while running the trial.** As you complete each `<!-- FIRST-TRIAL-FILL -->` block, paste the actual command + output + decision into the placeholder.
3. **After first trial completes,** the populated playbook becomes the canonical operator reference for subsequent trials. Variations across trials get added as alternative paths within sections.
4. **Halt-and-investigate** if any phase produces output you don't recognize OR steps fail. The phases below are arranged so a halt at phase N preserves all work from phases 1..N-1.

---

## Phase 1 — Environment confirmation

**Goal:** verify the local environment is ready before any trial work begins.

### 1.1 Activate venv

**Command:**
```
.venv\Scripts\activate
```

**Expected:** prompt prefix changes to `(.venv)`. If venv doesn't exist, run `python -m venv .venv` then re-activate.

<!-- FIRST-TRIAL-FILL: paste actual prompt before/after activation -->

### 1.2 Verify dependencies installed

**Command:**
```
.venv\Scripts\python.exe -c "import langgraph, langchain, pydantic, fastapi; print('OK')"
```

**Expected:** `OK` on success. If ImportError, run `.venv\Scripts\pip install -e .` to install per `pyproject.toml`.

<!-- FIRST-TRIAL-FILL: paste actual stdout -->

### 1.3 Verify required environment variables

**Command:**
```
.venv\Scripts\python.exe scripts\operator\check_keys.py
```

**Expected:** all REQUIRED keys (per `.env.example`) marked PRESENT; OPTIONAL keys may be absent. Required for production trial: `OPENAI_API_KEY`, `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`, `DATABASE_URL`.

<!-- FIRST-TRIAL-FILL: paste actual key-status table -->

**If any REQUIRED key is missing:** add to `.env` BEFORE proceeding. Restart shell to pick up new env vars.

### 1.4 Verify Postgres reachable

**Command:**
```
.venv\Scripts\python.exe -c "import psycopg, os; psycopg.connect(os.environ['DATABASE_URL']); print('OK')"
```

**Expected:** `OK`. If connection refused, see `docs/dev-guide/local-postgres-setup.md`.

<!-- FIRST-TRIAL-FILL: paste actual stdout/stderr -->

---

## Phase 2 — Pre-flight health check

**Goal:** confirm the migrated substrate is healthy before queuing real work.

### 2.1 Full migration health check

**Command:**
```
.venv\Scripts\python.exe scripts\operator\migration_full_health_check.py
```

**Expected:** ~213 passed + 1 skipped across 11/11 slices in ~28 seconds. All slices PASS.

<!-- FIRST-TRIAL-FILL: paste full output -->

**If any slice FAILS:** STOP. Do NOT proceed to trial. Surface to operator session for diagnosis. Common causes: pre-existing test fixture drift; environment dep version mismatch; transient flake (re-run before declaring fail).

### 2.2 Slab 6.0 substrate dual-gate (re-runnable confidence)

**Command:**
```
.venv\Scripts\python.exe scripts\operator\dual_gate_slab_6_0.py
```

**Expected:** 18 passed in ~1.5 seconds. PASS.

<!-- FIRST-TRIAL-FILL: paste actual output -->

### 2.3 Slab 6.1 dual-gate live ceremony (OPTIONAL; live API; ~$0.10–$0.30 cost)

**Skip this for first trial UNLESS** you want explicit confidence in the production-graph runner before queuing real work. The live smoke is the same flow your trial will use, in miniature.

**Command:**
```
.venv\Scripts\python.exe scripts\operator\dual_gate_slab_6_1.py
```

**Expected:** 1 passed in ~30s–5min (depending on OpenAI response + LangSmith trace upload). Cost ~$0.10–$0.30.

<!-- FIRST-TRIAL-FILL: paste actual output if run -->

---

## Phase 3 — Bundle preparation

**Goal:** create the corpus bundle that the trial will consume.

### 3.1 Choose `lesson_slug`

**Decision:** name for this lesson's content. Convention: kebab-case; descriptive; includes audience + topic. Example: `intro-to-cell-biology-undergrad`.

<!-- FIRST-TRIAL-FILL: actual lesson_slug used + rationale -->

### 3.2 Prepare source materials

**Decision:** which source materials feed the lesson? Common sources:
- PDFs (textbook chapters; papers)
- DOCX / pptx (existing slide decks; lecture notes)
- Markdown (existing course content)
- URL list (web articles; YouTube transcripts)

Place under a directory of your choosing — typical: `course-content/sources/<lesson_slug>/`.

<!-- FIRST-TRIAL-FILL: corpus directory path + files included -->

### 3.3 Bundle initialization

**Command:**
```
<!-- FIRST-TRIAL-FILL: actual bundle init command — needs first-trial discovery; CLI surface TBD -->
```

**Expected:** `state/config/runs/<run_id>/` directory created with `run-constants.yaml` containing `lesson_slug` + `run_id` (UUID).

<!-- FIRST-TRIAL-FILL: actual run_id assigned + directory contents -->

### 3.4 (Optional) Pull prior-run defaults via Step 02A (Slab 6.3)

**If you've run a trial for the same `lesson_slug` before,** Step 02A surfaces prior `operator-directives.md` as named defaults (per `docs/operator/step-02a-prior-run-defaults.md`).

<!-- FIRST-TRIAL-FILL: capture prior-run-defaults UI/CLI surface during first repeat-run trial -->

---

## Phase 4 — Trial launch

**Goal:** start the trial; verify it's running on the production graph.

### 4.1 Launch command

**Command:**
```
.venv\Scripts\python.exe -m app.marcus.cli trial start --preset production --input <corpus-path>
```

Replace `<corpus-path>` with the directory from §3.2.

<!-- FIRST-TRIAL-FILL: actual launch command -->

### 4.2 First-screen output verification

**Expected:** trial registration confirmation; trial_id assignment; production-graph compilation; first specialist invocation begins.

<!-- FIRST-TRIAL-FILL: paste first ~30 lines of trial output -->

### 4.3 (Optional) Open HUD in second pane

**Command (in separate terminal):**
```
.venv\Scripts\python.exe scripts\utilities\run_hud.py --watch
```

**Expected:** browser opens to live HUD; per-step expandable summaries (Slab 6.5) visible; current step auto-expanded.

<!-- FIRST-TRIAL-FILL: HUD URL + initial state -->

---

## Phase 4.5 — Where the prompts come from (HIL prompt sources reference)

**This playbook is structural** (it tells you WHEN gates fire, WHERE artifacts land, WHICH validation scripts to run). **It does NOT contain the conversational prompts Marcus delivers to you at each step** — those live in dedicated SSOTs and are loaded by Marcus the runtime as it walks the pipeline.

**Open the legacy prompt pack in a separate editor pane during your trial.** Marcus is delivering its prose to you in conversational form; you're reading along to know what's coming + what to enter.

### The 8 prompt sources

| # | Source | Path | Purpose |
|---|---|---|---|
| 1 | **Full v4.2 prompt pack** (legacy "prompt packet") | `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md` | Per-step prose Marcus reads to you; questions Marcus asks; data-entry surfaces. The single biggest reference document during a trial. |
| 2 | **Per-step Jinja templates** | `scripts/generators/v42/templates/sections/*.j2` | Source-of-truth templates that generate the v4.2 pack. Edit these (NOT the rendered pack) to change a step's prompts. |
| 3 | **DecisionCard schemas** | `app/models/decision_cards.py` (`G1Card`, `G2CCard`, `G3Card`, `G4Card`, `DecisionCardMeta`) | Structured format of what you see at each gate. Each card type has explicit fields (artifact summary, cost, override trail, sanctum warnings) you read + decide on. |
| 4 | **Marcus PR-\* capability references** | `skills/bmad-agent-marcus/references/` | Marcus's conversational capabilities: CM (conversation management), PR (prompt routing), HC (hot-context), MM (memory management), SP (status protocol), SM (session management), SB (status board), PR-R / PR-RC / PR-4A / etc. (per-procedure prompt routes). |
| 5 | **Marcus capabilities doc** | `docs/dev-guide/marcus-capabilities.md` | High-level catalog of all PR-\* capabilities + their operator-facing prompt patterns. |
| 6 | **Marcus persona + sanctum** | `_bmad/memory/bmad-agent-marcus/PERSONA.md` + cross-references in `_bmad/memory/bmad-agent-marcus/INDEX.md` | Marcus's persistent voice + conversational style; loaded at runtime activation. |
| 7 | **Step 02A prior-run defaults** (Slab 6.3) | `scripts/utilities/operator_directives_defaults.py` + `docs/operator/step-02a-prior-run-defaults.md` + Step 02A pack section | Slab 6.3 surfaces prior-run `operator-directives.md` as named defaults at Step 02A. |
| 8 | **Operator op docs** (gate addenda) | `docs/operator/conditional-gate-addendum-playbook.md` + `docs/operator/post-m5-runbook.md` | Per-gate operator action patterns; conditional addenda for M-gates that needed extra evidence. |

### Per-step prompt source (Phase 5 cross-reference)

When you reach each Phase 5 step:
- Look up the step number in the v4.2 pack (Source #1) — that section's prose IS the prompt set Marcus delivers
- Cross-check the matching `.j2` template (Source #2) if the rendered pack appears stale
- At gate steps (G1/G2C/G3/G4): the DecisionCard schema (Source #3) defines the card structure you read

For Step 02A specifically: prior-run defaults surface per Source #7 BEFORE the standard pack prose displays.

### Quick-open commands (Windows)

```
:: Open the v4.2 prompt pack
start docs\workflow\production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md

:: Open Marcus's capability references directory
explorer skills\bmad-agent-marcus\references\

:: Open the DecisionCard schema
start app\models\decision_cards.py
```

### A note on prompt length + future evolution

The v4.2 pack is large (hundreds of pages) because it's a legacy "script of prompts as prose" inherited from the pre-migration primary-repo workflow. The migrated platform ARCHITECTURALLY does not need so much prose-as-script — Marcus + the specialists internalize substantive guidance via skills, sanctum personas, and `_act` body knowledge. The pack persists for: (a) operator-facing reference of what to expect; (b) backward-compat to the prompt-pack-driven primary-repo workflow.

**Future direction (deferred work):** prompt-pack reduction / internalization initiative — gradually migrate prompt content from prose-script into specialist skills + Marcus PR-\* capability references, so operator interaction becomes more conversational and less prompt-feeding. Filed as a candidate post-trial substrate-evolution effort. See deferred-inventory entry `prompt-pack-reduction-internalization` if filed (or surface to operator at first-trial post-run review per Phase 8.3).

---

## Phase 5 — Steps 01–33 walkthrough

**Goal:** per pipeline step, document what runner shows + what operator inputs (if any) + what artifacts get locked.

### Phase 5.A — Pre-content steps (01–03)

#### Step 01 — Preflight receipt + run constants
<!-- FIRST-TRIAL-FILL: artifacts emitted; expected duration; operator action (typically none) -->

#### Step 02 — Source authority map
<!-- FIRST-TRIAL-FILL: source quality evidence emitted; operator review point if any -->

#### Step 02A — Operator directives (Slab 6.3 prior-run defaults surface here)
<!-- FIRST-TRIAL-FILL: prior-defaults UI; accept/modify/replace decision; resulting operator-directives.md -->

#### Step 03 — Extraction + ingestion
<!-- FIRST-TRIAL-FILL: extraction report; ingestion evidence; common pitfalls -->

### Phase 5.B — Content production (04–08)

#### Step 04 — Ingestion quality + Irene packet
<!-- FIRST-TRIAL-FILL: Irene packet shape; quality threshold check -->

#### Step 04A — Maya HIL ratification (Production intake_callable; deferred per inventory; may not fire in first trial)
<!-- FIRST-TRIAL-FILL: Maya UI surface OR deferred-skip notice -->

#### Step 05–07 — (intermediate; placeholder)
<!-- FIRST-TRIAL-FILL: per-step artifacts + operator actions -->

#### Step 08 — Narration script + segment manifest + perception artifacts (Irene Pass 2; Slab 6.4 authoring template now applies)
<!-- FIRST-TRIAL-FILL: Pass 2 artifact set; validator run; common errors -->

### Phase 5.C — G1 Production gate

#### Step G1 (post-pipeline) — DecisionCard

**Expected:** runner pauses; emits `G1Card` with: pipeline summary; cost report; per-specialist contribution count; envelope state.

<!-- FIRST-TRIAL-FILL: actual G1Card content shape; verdict submission CLI -->

**Operator action:** review card; submit verdict (continue / revise / halt).

**Verdict submission command:**
```
<!-- FIRST-TRIAL-FILL: exact verdict CLI from app/marcus/cli/trial.py resume subcommand -->
```

**Resume verification:** runner resumes; remaining specialist work fires.

<!-- FIRST-TRIAL-FILL: post-resume output -->

### Phase 5.D — Composition + production (09–17)

#### Step 09 — Locked Pass 2 package status
#### Steps 10–17 — Compositor + Gary motion + Kira + Texas + downstream
<!-- FIRST-TRIAL-FILL: per-step artifacts + operator actions for each -->

### Phase 5.E — G2C Compositor gate
<!-- FIRST-TRIAL-FILL: G2CCard shape; edit_payload submission for revisions; operator workflow -->

### Phase 5.F — Audio + final (18–32)

#### Steps 18–24 — ElevenLabs / Wondercraft / audio pipeline
<!-- FIRST-TRIAL-FILL: per-step artifacts -->

### Phase 5.G — G3 Audio gate
<!-- FIRST-TRIAL-FILL: G3Card content; verdict workflow -->

#### Steps 25–32 — Final assembly + publish + handoff
<!-- FIRST-TRIAL-FILL: per-step artifacts -->

### Phase 5.H — G4 Final gate
<!-- FIRST-TRIAL-FILL: G4Card content; verdict workflow; trial-close artifacts -->

### Step 33 — Trial completion
<!-- FIRST-TRIAL-FILL: terminal-state artifacts; final cost report; envelope persistence verification -->

---

## Phase 6 — Mid-run troubleshooting

**Common situations + recovery actions.** First trial reveals which are common; placeholder list per anti-pattern catalog + Composition Spec §11 trigger detection.

### 6.1 Specialist halts with `MissingUpstreamContributionError`

**Cause:** dependency_map declared upstream that didn't run. See Composition Spec §3.6.

**Recovery:** verify upstream specialist actually fired (HUD or LangSmith trace); check pipeline manifest dependency declaration matches actual specialist topology.

<!-- FIRST-TRIAL-FILL: actual incident if surfaced; otherwise speculation removed at first-trial close -->

### 6.2 Gate verdict rejected (signature/anti-replay/digest binding failure)

**Cause:** verdict tampering detected per Story 3.3 W-R1-3.3-2 anti-replay tuple.

**Recovery:** verify verdict was submitted via authorized transport (CLI/MCP/FastAPI); regenerate verdict with current decision-card-digest.

<!-- FIRST-TRIAL-FILL: actual handling sequence -->

### 6.3 Live API rate limit / OpenAI throttle

**Cause:** burst calls exceeded API rate limit.

**Recovery:** automatic retry with exponential backoff likely triggers; if persistent, check OpenAI account dashboard.

<!-- FIRST-TRIAL-FILL -->

### 6.4 LangSmith trace upload stalled

**Cause:** network blip OR LangSmith ingestion delay.

**Recovery:** trial continues regardless; trace shows up later (typically <5 min). For per-trial trace lookup: query LangSmith manually for spans where `extra.metadata.trial_id == <trial_id>` per Slab 6.1 known limitation.

<!-- FIRST-TRIAL-FILL -->

### 6.5 HUD shows blocker or warning state

**Recovery:** expand the affected step's per-step summary (Slab 6.5; auto-expanded for blocker/warning per DN-1); read the artifact details; decide continue / revise / halt.

<!-- FIRST-TRIAL-FILL -->

---

## Phase 7 — Trial completion

**Goal:** verify trial reached terminal state cleanly.

### 7.1 Terminal-state recognition

**Expected:** runner exits 0; `state/config/runs/<trial-id>/trial_envelope.json` contains complete envelope with all specialist contributions + `production_clone_launch_evidence: true`.

<!-- FIRST-TRIAL-FILL: actual trial-close output + envelope summary -->

### 7.2 Cost report inspection

**Command:**
```
type state\config\runs\<trial-id>\cost-report.md
```

**Expected:** human-readable cost breakdown by specialist + tier; total within budget.

<!-- FIRST-TRIAL-FILL -->

### 7.3 LangSmith trace inspection

Manual: open LangSmith dashboard; filter by `metadata.trial_id == <trial_id>`; verify all specialist invocations appear as child runs of the trial root span; per-call cost matches cost report.

<!-- FIRST-TRIAL-FILL -->

---

## Phase 8 — Post-run review

### 8.1 Composition Spec §11 trigger evidence capture

For each of the 6 §11 migration triggers, record evidence from this trial:
- Trigger 1 (fan-out / parallel dispatch): did the trial expose any need?
- Trigger 2 (partial state mid-execution): did any specialist need partial upstream output?
- Trigger 3 (gate precedence complexity): did gate_overrides need to be set?
- Trigger 4 (adapter LOC growth / refactor cost): not applicable per single-trial; track over time
- Trigger 5 (new act-body category): did the trial reveal a new specialist shape?
- Trigger 6 (Composition Spec §10 Decision Log entry rate): not applicable per single-trial

<!-- FIRST-TRIAL-FILL: per-trigger evidence -->

### 8.2 Mary harvest-gate review

Did anything surprising surface that should be filed as a new anti-pattern? If so, propose to Mary harvest-gate (operator decision; format per `docs/dev-guide/specialist-anti-patterns.md`).

<!-- FIRST-TRIAL-FILL -->

### 8.3 Deferred-inventory updates

If trial surfaced needs that don't fit existing scope, file as deferred-inventory entries per CLAUDE.md §"Deferred inventory governance."

<!-- FIRST-TRIAL-FILL: list of new entries filed -->

### 8.4 Learning-event ledger entry

When Epic 15 (Learning & Compound Intelligence) lands, this trial becomes input to the learning-event ledger. Until then, the trial close artifact serves as the canonical record.

<!-- FIRST-TRIAL-FILL: TBD when Epic 15 unblocks per its hard-dependency on first tracked trial completing -->

---

## Phase 9 — Quick-reference card (legacy "cheat sheet" equivalent)

### Critical commands
- Health check: `.venv\Scripts\python.exe scripts\operator\migration_full_health_check.py`
- Trial start: `.venv\Scripts\python.exe -m app.marcus.cli trial start --preset production --input <corpus-path>`
- Trial resume: <!-- FIRST-TRIAL-FILL exact CLI -->
- HUD: `.venv\Scripts\python.exe scripts\utilities\run_hud.py --watch`
- Validation scripts catalog: `.venv\Scripts\python.exe scripts\operator\<script-name>.py` (see `docs/operator/validation-scripts.md`)

### Key paths
- Corpus: `course-content/sources/<lesson_slug>/` (or operator-chosen)
- Run artifacts: `state/config/runs/<trial-id>/`
- Pipeline manifest: `state/config/pipeline-manifest.yaml`
- Frozen graph: `runtime/graphs/v42/`
- LangSmith trace: query by `metadata.trial_id == <trial_id>`

### Emergency commands
- Halt trial: <!-- FIRST-TRIAL-FILL -->
- Kill stuck process: `Ctrl+C` (graceful) or `Ctrl+Break` (force; Windows)
- Investigate stuck state: `.venv\Scripts\python.exe scripts\operator\check_keys.py` + manifest health check
- Reset checkpointer (NUCLEAR; data loss): <!-- FIRST-TRIAL-FILL with strong warning -->

### Common error codes / symbols
<!-- FIRST-TRIAL-FILL: dictionary populated as errors surface during first trial -->

---

## Phase 10 — Appendix: when this playbook drifts

**This document is a living playbook.** Keep it current by:

1. **After every trial,** review which `<!-- FIRST-TRIAL-FILL -->` blocks got populated; verify accuracy; promote to canonical text (remove the marker).
2. **When a new specialist is added,** update Phase 5 step coverage.
3. **When a new operator-validation script lands,** update Phase 1.3 + 2.1–2.3 + Phase 9 quick-reference.
4. **When pipeline-manifest pack version bumps** (Tier-2+ per `docs/dev-guide/pipeline-manifest-regime.md`), update Phase 3.3 bundle init + Phase 5 step coverage.
5. **At Composition Spec §11 trigger evaluation,** update Phase 8.1 evidence capture + escalate if Option C migration territory.

**Maintenance protocol:** dev-agent authority for new sections + step coverage updates; party-mode required for structural changes (phase reordering; major scope changes); operator authority for trial-evidence integration after each run.

---

## See also

- `docs/operator/trial-run-runbook.md` — first-trial step-by-step (more concise; this playbook is the action-by-action expansion)
- `docs/operator/production-run-swimlane.md` — at-a-glance swimlane (best high-level entry point)
- `docs/operator/conditional-gate-addendum-playbook.md` — per-gate addendum patterns
- `docs/operator/post-m5-runbook.md` — post-M5 (now post-SHIP) operations
- `docs/operator/hud-guide.md` — HUD reading guide
- `docs/operator/step-02a-prior-run-defaults.md` — Slab 6.3 prior-run directives
- `docs/operator/validation-scripts.md` — operator-run validation scripts catalog
- `docs/operator/adhoc-mode.md` — Marcus ad-hoc CLI mode
- `docs/dev-guide/composition-specification.md` — composition substrate (Option B / Path A-prime)
- `docs/dev-guide/sources-of-truth.md` — comprehensive SSOT registry
- `docs/dev-guide/pipeline-manifest-regime.md` — pipeline lockstep regime
- `README.md` — top-of-repo orientation
