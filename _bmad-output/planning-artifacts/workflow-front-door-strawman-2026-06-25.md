# Strawman — Marcus-SPOC Workflow-Selection Front-Door (2026-06-25)

**Status:** STRAWMAN for party-mode green-light + sequencing. Operator-set direction (2026-06-25: "advance the Marcus-SPOC experience to the front-door workflow picker"). NOT yet ratified.
**Purpose:** Give the tailored party a concrete artifact to pressure-test so the round produces a LOCK (registry shape + selection-surface attach-point + reproducibility contract + minimal first slice + sequence), not an open brainstorm. Mirrors the braid-strawman method that produced a clean 6/6 lock.
**Authorities:** operator architectural signal 2026-06-25 (Marcus duality discussion); `deferred-inventory.md` §"Workflow registry + Marcus-SPOC selection front-door"; Epic 18-7 (workflow-family framework) + Epic 18-5 (podcast pack family) + PR-RS/story-26-10 (selection step); `docs/dev-guide/pipeline-manifest-regime.md` (Pack Versioning Policy); STATE-OF-THE-APP §11; the braid S4/S5 deterministic-guard precedent (LLM advises, human decides, engine executes).

---

## 1. The capability (operator vision, verbatim-faithful)

The app will run MANY production types — narrated-slides-with-motion-video is one core example; a **podcast** is another. Before a run executes deterministically, **Marcus-SPOC interacts at the FRONT DOOR** to **(a) pick the workflow from a registry** and **(b) seed initial guidance** (theme, source content, research scope, lesson-plan contents). The run then executes DETERMINISTICALLY; SPOC narrates each gate and threads operator choices to specialists as guidance.

**Load-bearing constraint (operator + architecture):** this requires **NO autonomous orchestrator.** Selection is a bounded, operator-confirmed choice over a KNOWN registry. The existing deterministic-guard pattern (LLM advises/narrates → human decides → engine executes) extends to the front door. Determinism-after-selection preserves frozen-graph replay + tamper-evident HIL authority.

---

## 2. Reuse map — this is mostly wiring + ONE new declarative artifact + ONE new turn

| Need | Already exists (recon-confirmed) | Gap |
|---|---|---|
| Workflow definition | The manifest IS the workflow: `state/config/pipeline-manifest.yaml` → `app/manifest/compiler.py:compile_run_graph()` → LangGraph StateGraph. Rich metadata per manifest (schema_version, lane, entrypoint, frozen_graph_version, pack_version, generator_ref, nodes[]). | There is exactly ONE real workflow manifest today; no registry over manifests. |
| Selection step | `scripts/marcus_capabilities/pr_rs.py` (PR-RS) — registered capability, pinned invocation/return envelopes, returns `NOT_YET_IMPLEMENTED` (story 26-10). Planned `args.action`: inspect\|start_new\|continue\|cancel_orphans. | The capability body is unbuilt; not wired to a real registry or surface. |
| Conversational surface | `app/marcus/cli/marcus_interlocutor.py::InterlocutorREPL` (LLM turn-taking, deterministic guard) + scripted `marcus_spoc.py` (gate narration a–g). | Neither has a front-door **workflow-selection turn**; the narrated-lesson workflow is hard-assumed. Entry = `trial.py:start_trial(preset, input, operator-id)`. |
| Reproducibility | `RunState` (graph_version, sanctum_fingerprint, model_resolution_trail, temperature) + `ProductionTrialEnvelope` (preset, corpus_path, operator_id) → `runs/<trial_id>/run.json`. | NO `workflow_id`, NO `manifest_content_hash`, NO `seed_choices` frozen. |
| Capability honesty | The braid S4 GENERATED capability-overlay (`wired\|partial\|orphaned\|shelf` vs live graph) + CI parity — the pattern that stops Marcus over-promising. | Registry must be similarly GENERATED/validated against the manifests it points to, not hand-maintained (drift risk). |
| Second content type | Podcast = GREENFIELD: `18-5-discovery-podcasts-audio-content.md` (discovery only); reusable infra exists (`elevenlabs_client.py`, `wondercraft_client.py`, content-creator, quinn-r). | No podcast manifest, no podcast specialist wiring. A real second workflow is a separate large arc. |

**Net-new build is small and localized:** a **workflow registry** (declarative + generated/validated) + a **front-door selection turn** on the Marcus-SPOC surface (realizing PR-RS `start_new`) + a **reproducibility freeze** (3 envelope fields). Everything else is connect-and-extend. The actual *second workflow* (podcast) is explicitly downstream.

---

## 3. DECISION POINTS the party must resolve (strawman recommendation in **bold**)

**DP1 — Registry: where it lives + its shape + source of truth.**
- Strawman: a declarative **`state/config/workflow-registry.yaml`** — one entry per workflow: `{id, display_name, content_type, manifest_path, required_inputs[], specialist_roster_ref, status}`. **GENERATED/validated against the referenced manifests with CI parity** (reuse the braid S4 capability-overlay discipline) so the menu cannot list a workflow whose manifest is absent/orphaned, and cannot hide a real one. This is the single source of truth for "what workflows exist." **Recommend: schema-shape NEW CYCLE story (scaffold per `docs/dev-guide/scaffolds/schema-story/`).**

**DP2 — Selection surface + interaction posture.**
- Strawman: a front-door **selection TURN on `marcus_interlocutor.py` (InterlocutorREPL)**, inserted BEFORE `trial.py:start_trial()` deterministic run. Posture = the existing **deterministic guard**: Marcus narrates the registry menu, optionally *advises* a pick from the operator's stated goal (frontier model, advisory only), the **operator confirms**, the engine proceeds. NO autonomous selection; the LLM never picks unilaterally. **Recommend: this is the interaction-heaviest piece — its own NEW CYCLE story, reusing the S5 guard.**

**DP3 — Reproducibility: what gets frozen, and when.**
- Strawman: extend `RunState` + `ProductionTrialEnvelope` with **`workflow_id`** + **`manifest_content_hash`** (sha256 of the *selected* manifest at selection-time) + **`seed_choices`** (theme/source/research-scope/lesson-plan seeds the operator confirmed). Freeze at selection-time, before the deterministic walk. Preserves frozen-graph replay + tamper-evident HIL. **Recommend: additive schema change folded into DP2's story OR its own thin story — party to decide granularity.**

**DP4 — Relationship to the PR-RS stub (story 26-10).**
- Strawman: realize the front-door selection AS PR-RS `args.action="start_new"` — closing the 26-10 stub for the selection path. `continue`/`cancel_orphans`/`inspect` (run-lifecycle management) are **orthogonal and deferred** — v1 does selection only. **Recommend: scope v1 to `start_new`; file the other PR-RS actions as a follow-on.**

**DP5 — v1 scope / proof slice (THE load-bearing decision).**
- Options: **(a) machinery-only** — ship the registry + selection turn + freeze with the EXISTING single narrated-lesson workflow (a degenerate menu of 1: the turn runs, picks it, freezes the envelope, run proceeds unchanged → no regression; proves the front door end-to-end without a second workflow); **(b) machinery + a real second workflow** — also build the podcast manifest + specialist wiring so the menu has ≥2 real choices (proves multi-workflow but is a MUCH larger arc — pulls in Epic 18-5 greenfield).
- Strawman: **(a) machinery-only for v1.** Prove the front door on the 1 existing workflow + a registry SHAPE that already accommodates N. Podcast (a genuine 2nd type) becomes the v-next arc that exercises the now-built front door. Reason: decouples the *selection capability* (small, high-leverage) from *building a new content type* (large, separate). **Recommend (a).**

**DP6 — Required-inputs contract at the door.**
- Strawman: each registry entry declares **`required_inputs[]`** (narrated-lesson → corpus_path; podcast → script-source + voice-cast, when it exists). The front-door turn collects + validates required inputs for the chosen workflow before `start_trial`. Additive; degenerate for the single current workflow (corpus_path, already collected). **Recommend: fold into DP1's registry schema.**

**DP7 — Sequencing + NEW CYCLE story breakdown.**
- Strawman sequence (each: party green-light → NEW CYCLE dev T1–T10 → Claude T11 → small-scale live run → iterate):
  1. **Story W1** — workflow registry schema + `workflow-registry.yaml` + generator/CI-parity check (schema-shape; scaffold).
  2. **Story W2** — front-door selection turn on `marcus_interlocutor` (realizes PR-RS `start_new`); deterministic guard; operator-confirmed; required-inputs collection.
  3. **Story W3** — reproducibility freeze (`workflow_id` + `manifest_content_hash` + `seed_choices` into RunState/envelope) + replay witness.
  - **Live v1 proof:** a Marcus-SPOC session that opens at the front door, presents the menu (1 entry), the operator picks narrated-lesson + seeds guidance, the envelope freezes the workflow id + manifest hash, and the existing trial runs to completion unchanged.
  - **Out of v1 (downstream):** the podcast workflow (Epic 18-5) and the other PR-RS actions (continue/cancel_orphans/inspect).

---

## 4. Honesty carry-forwards / risks

- **Registry drift is the believed-green trap.** A hand-maintained menu will over-promise (list workflows that don't really compile). Mitigation = GENERATE/validate against manifests with CI parity (DP1), same as the S4 overlay.
- **The LLM must not pick.** The front door is a guarded, operator-confirmed choice; Marcus advises only. Same load-bearing rule as S5.
- **v1 menu-of-1 is honest, not a cheat.** It proves the machinery; it does NOT claim multi-workflow until a real second workflow (podcast) lands. Say so in the §11 update.
- **Determinism after selection is the whole point** — freeze the chosen workflow id + manifest content-hash so a run is replayable and the HIL authority chain is tamper-evident.
- **Does not advance** the reading-path fresh-naive-holdout gate (still owed) or any fidelity gate.

---

## 5. The single question for the party

> Ratify the front-door capability as a **machinery-only v1** (registry + guarded selection turn + reproducibility freeze, menu-of-1 narrated-lesson, podcast deferred), sequenced W1→W2→W3 — or amend the render of any DP1–DP7 decision? Specifically pressure-test **DP1 (generated-registry source-of-truth)**, **DP5 (machinery-only vs build-a-second-workflow)**, and **DP3 (what to freeze for replay)**.
