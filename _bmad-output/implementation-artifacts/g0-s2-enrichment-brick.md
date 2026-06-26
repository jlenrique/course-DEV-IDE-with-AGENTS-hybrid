# Story G0-S2 — G0-Enrichment Brick + Operator Confirm-Gate #1

**Epic:** G0 Source-Content Enrichment (v1) — `_bmad-output/planning-artifacts/epics-g0-enrichment.md`
**Authority:** `lo-schema-ratification-2026-06-26.md` (entity from S1; §3.1 adequacy-advisory; §4 A3/A4/A10 artifacts); `g0-enrichment-cycle-charter-2026-06-26.md` (D1 10-type enum + `other:` escape hatch; D2 operator-confirms-manifest; A1/A2/A4/A6/A10/A11).
**Class:** S · **Type:** brick (orchestration node + gate) · **Gate mode:** single-gate · **Status:** ready-for-dev (blocked by S1 commit)
**Closes:** A1, A2, A3, A4, A6, A10, D1, D2. **Depends on:** S1 (`app/marcus/lesson_plan/learning_objective.py` — `LearningObjective`, `SourceRef`, `SourceAdequacy`, `advance_lo`, the enums).
**Required dev readings (T1):** the S2 substrate map below; `[[project_production_runner_two_walks]]`; `app/marcus/orchestrator/pre_gate_marcus.py`; `app/composers/section_02a/{composer,_prompt,_cache,directive_model}.py`; the 07D.5/07W brick precedents (`docs/dev-guide/` + the motion/workbook producer nodes).

## Goal
A new in-graph orchestration step at the G0 front door that (1) **types every source span** into the closed 10-type enum + `other:<label>` escape hatch, (2) **extracts candidate Learning Objectives** as `status=provisional` `LearningObjective`s with resolvable `SourceRef` provenance — both via a **Marcus-SPOC LLM pre-pass OFF the deterministic critical path** (result cached keyed to corpus fingerprint for replay determinism) — then (3) **pauses at operator confirm-gate #1** where Marcus-SPOC presents the typed manifest + provisional LOs + enumeration-provenance/traversal-roots, and the operator's verdict (never the model) advances the run. Marcus only ALERTS/PROPOSES; the operator decides.

## Substrate map (verified read-only)
- **Directive model:** `app/composers/section_02a/directive_model.py` — `DirectiveRole` (PRIMARY/SUPPORTING/IGNORED, L36-41), `DirectiveSource` (L53-128), `Directive` (L131-158). TYPE is net-new and ORTHOGONAL to role (operator binding) — add it alongside, do not overload role.
- **Composer / corpus enumeration:** `app/composers/section_02a/composer.py` — `_walk_corpus_files()` (L34-43, the deterministic ALL-sources set for A6), `compose()` (L127-172), `_classify_with_llm()` (L103-124, existing per-file LLM role classification — the typing pre-pass is a sibling, reuse the prompt/cache plumbing).
- **Existing LLM seam (REUSE — no bespoke path):** `app/marcus/orchestrator/pre_gate_marcus.py::invoke_pre_gate_marcus` (L53-68) → `make_chat_model("marcus")` + Jinja2 templates in `docs/conversational-gates/<gate>.j2` → structured JSON → `PreFillProposal`.
- **Cache:** `app/composers/section_02a/_cache.py::ComposerCache` + `_prompt.py::cache_key_for_prompt` (SHA256(normalized_prompt)). Re-key the enrichment cache to a **corpus fingerprint** (SHA256 of concatenated per-file content hashes + model id) so graph replays read the frozen result.
- **production_runner TWO walks** (`app/marcus/orchestrator/production_runner.py`): START `run_production_trial()` (L1838-2216; gate side-effects L1943-1954; `_pause_at_gate` L1977); CONTINUATION `_continue_production_walk()` (L2414-2791; DUPLICATE gate side-effects L2510-2526; `_pause_at_gate` L2549); resume L2219-2333; recover L2336-2411. Orchestration-node side-effects fire via `node.id in <NODE_IDS>` checks at BOTH walks (research_wiring L2051-2099/L2619-2667; package_builders L2001-2041/L2573-2612 are the templates). **Wiring the new node + gate into only one walk is the classic silent-no-op bug — do both.**
- **Marcus-SPOC:** `app/marcus/cli/marcus_spoc.py::narrate_gate` (L152-188), `run_marcus_spoc` (L191-240); decision-card loaded L218; `resume_production_trial` called L232.
- **Registration:** `state/config/pipeline-manifest.yaml` nodes; `app/manifest/compiler.py::_orchestration_node` (L181-193) for null-specialist nodes; `CANONICAL_SPECIALIST_IDS` in `app/models/state/specialist_summary_artifacts.py` (L17-46 — add the new id or hit the emit_spans crash both prior bricks hit).

## Acceptance Criteria

### AC-S2-1 — TYPE taxonomy (closed enum + escape hatch), ORTHOGONAL to role
A closed `SourceType` enum: `slide, quiz, workbook, narration, reference_citation, rubric, exercise_lab, motion_script_storyboard, discussion_forum, assignment_instructions` + an `other:<label>` escape-hatch shape (a structured `{kind:"other", label:str}` with mandatory provenance, surfaced FLAGGED as unconsumed/ad-hoc, never silently routed to generation). pydantic-v2 closed-enum 3-surface red-rejection. TYPE is recorded INDEPENDENTLY of `DirectiveRole` (a `discussion_forum`/`quiz` span may still be `supporting`). RED-first tests incl. an `other:` round-trip + a consumer-map flag (per A10: types with no generator today = quiz/rubric/exercise_lab/reference_citation/discussion_forum/assignment_instructions are flagged classification-only).

### AC-S2-2 — Candidate-LO extraction emitting `provisional` with provenance
The pre-pass emits `LearningObjective`s at `status=provisional` (via S1's `advance_lo(mint→provisional, actor="g0")`) each carrying ≥0 `SourceRef`s (provisional allows 0, but every emitted ref MUST be a structured locator with a `source_id` ∈ the enumerated corpus set and a verbatim `quoted_span` — A9; a fabricated `source_id` is RED). Provenance-less LO findings are advisory but flagged (A2). `confidence` populated (advisory). RED-first: a fabricated source_id is rejected; a provisional LO with 0 refs is allowed.

### AC-S2-3 — LLM pre-pass OFF the deterministic critical path + corpus-keyed cache
Typing + LO extraction run via `make_chat_model("marcus")` (reuse the `pre_gate_marcus` seam + a new `docs/conversational-gates/g0-enrichment.j2` template), NOT inside the deterministic composer. The frozen, operator-confirmed result is cached keyed to the corpus fingerprint (+model id); a graph replay with unchanged corpus reads the cache (determinism). Offline/test runs bypass the live LLM via the existing `_has_live_openai()`-style guard and use a recorded/fixture pre-pass result — BUT the story's live-segment proof (below) exercises the REAL LLM on real corpus.

### AC-S2-4 — Independent-parse-first (A4) + dissent scaffold (A3/A11)
Marcus's own typing/LO analysis is written to an audit sidecar `independent_parse{proposal, ts}` BEFORE any operator suggestion is merged (`operator_merge{suggestion, ts}`); deterministic guard `independent_parse.ts < operator_merge.ts` or reject pre-surface. A per-LO/per-span `dissent{against, marcus_position, operator_position, disposition}` field + a **run-level invariant: ≥1 real dissent** across the corpus (independent-parse-sourced; must show run-to-run variance — a never-varying field is theater). Internal audit fields use `Field(exclude=True)+SkipJsonSchema` (checklist §5).

### AC-S2-5 — Operator confirm-gate #1 wired into BOTH production_runner walks
Register a `g0-enrichment` orchestration node (after `directive-composer`, before node `01`) + a confirm-gate (gate_code e.g. `G0E`) in `pipeline-manifest.yaml`; compile via `_orchestration_node`; add the new id to `CANONICAL_SPECIALIST_IDS`. The gate-pause side-effect (publishing the decision-card: typed manifest + provisional LOs + A10 enumeration-provenance/traversal-roots + the reconcilable count view) MUST be wired into BOTH `run_production_trial` AND `_continue_production_walk` (and reachable via resume + recover). Marcus-SPOC `narrate_gate` presents it; the operator verdict advances. Deterministic guard (S5 SPOC pattern): the model's typing/LO proposal NEVER auto-advances — operator-confirm is final.

### AC-S2-6 — A10 enumeration-provenance + traversal-roots; A1 RED on unreachable
The decision-card surfaces, per source, HOW it entered the set (which traversal/connector/root) AND the traversal roots themselves (corpus dir / Notion page IDs / Box folder IDs / URL-list walked) — not just the leaf file list. Source enumeration stays the deterministic composer's job (A6 — LLM advises type/LO, never gates a file out; `ignored` stays operator-confirmed). Unreachable/unextractable source = RED (A1), never silently absent.

### AC-S2-7 — Regression + blast-radius guard
Deck-default / existing pipeline behavior byte-identical when the enrichment node is present but the run is a normal trial (the node is additive; existing gates unchanged). Full relevant suites + ruff + lint-imports green. NO new Gamma/video/audio — the live-segment proof runs G0 → enrichment → gate #1 and STOPS (upstream of Gary).

### AC-S2-8 — LIVE-segment proof (no mocks)
A REAL Marcus-SPOC run on a real corpus (`course-content/courses/tejal-c1m1-fresh-outline/` or `studio-smoke-min`): the pre-pass types the spans + emits provisional LOs with resolvable provenance; gate #1 pauses; Marcus narrates the typed manifest + LOs + traversal-roots; a real dissent artifact is present; the operator-confirm advances. Captured as evidence. (Operator-gated live legs may be executed by an independent verification subagent per `[[feedback_operator_cost_not_constraint_run_gated_validation]]`.)

## Definition of Done
All ACs green; the brick registered in both walks (no silent-no-op); LLM pre-pass off the critical path + corpus-keyed cache; A3/A4/A10 artifacts real; adequacy NOT introduced here (S3) but TYPE+provisional-LO are; live-segment proof captured; full suite + ruff + lint-imports green; T11 `bmad-code-review` clean; party-close. NO new expensive assets.

## Open implementation choice (dev decides, document in Dev Notes)
Gate #1 as a NEW graph pause-gate (recommended — Marcus-SPOC narrates it, two-walk consistent, conversational-SPOC pattern) vs extending the existing CLI-side directive confirm (`app/marcus/cli/trial.py` L109-180). The goal's "real trial through Marcus-SPOC to the Gary gate" favors the graph pause-gate.
