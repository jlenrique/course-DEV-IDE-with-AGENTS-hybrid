# Story S2 — Styleguide picker canonical at trial-start (WARN-preserving)

**Arc:** Canonical Production Conversation (party record §1 S2 row + amendments; SOP-004 F-403/F-404 inherited constraints).
**Status:** ready-for-dev · **Size:** S/M · **Gate mode:** single-gate structural (3-lane review at T11) · **Branch:** `dev/workbook-2026-07-06` (S1 landed @ `c24308f7`).
**Execution convention:** FRESH dev agent, RED-first, `PYTHONIOENCODING=utf-8`, xdist rule (`-n 0` confirm before triaging new parallel reds). Do not commit.

## Context (landed substrate — verified)

- `run_picker_preflight` (`app/marcus/cli/marcus_spoc.py:206`) is the hardened publish→narrate→decode→echo→confirm→commit ceremony with **zero production callers**. `commit_picker_pick` → `write_pick_to_directive` (`app/marcus/orchestrator/styleguide_picker.py:974-1105`) patches the directive's `gamma_settings[]` (validate/normalize/dedupe/fail-loud) + writes the `styleguide_picker_provenance` block; `append_pick_event` writes the JSONL sidecar with `(run_tag, code)` dedup.
- Trial start (`app/marcus/cli/trial.py` `start_trial_cli`:386) composes the directive via `compose_and_write` → operator confirm/edit gate (`_confirm_or_edit_directive`; non-interactive requires `--auto-confirm-directive`) → run record. `--gamma-settings-file` already threads a `gamma_settings` list into composition.
- **S1's CD audit seam reads ONLY the directive** both walks resolve (`_runner_payload_for_specialist` cd branch → `gamma_settings[]` + `styleguide_picker_provenance` + digest). **F-404 (binding):** the persisted pick MUST land in that directive via `write_pick_to_directive` — never a sidecar the projection can't see, never a reimplementation. A pick CD can't see manufactures a false S3 parity divergence.
- **F-403 (binding):** picker `_VARIANT_IDS` and CD `_PICK_VARIANT_VOCABULARY` are two independent `{A,B}` constants; production import coupling is structurally forbidden (S1 lint contract + AST guard). S2 adds the **test-level lockstep pin** (a test may import both; production code may not) and touches vocabulary nowhere.
- Gary's styleguide-less WARN-seed (`_act.py:519-528`) is **UNTOUCHED** — the FAIL-LOUD flip is S4. Mid-arc, a pickless non-interactive run keeps today's behavior.

## Deliverables

### D1 — Interactive trial-start runs the ceremony (the canonical front door)
In the interactive start path: after `compose_and_write` produces the directive and **before the operator's directive confirm gate / run-record creation / any dispatch**, invoke `run_picker_preflight` against the composed directive (run_tag derived from the trial context; T1 verifies the exact insertion point and run_tag source). The confirmed pick is committed into the directive by the existing `commit_picker_pick` path (F-404 satisfied by construction). No confirmed pick within `max_attempts` ⇒ the existing `PickerError` aborts the start — **no run record, no run-dir walk, zero spend**. Resume (`resume_trial_cli`) and recover NEVER invoke the preflight — they read the persisted directive (witness: zero `input_fn` calls on resume of a picked run).

### D2 — Programmatic/scripted paths stay byte-stable (WARN-preserving staging)
Non-interactive starts (`--auto-confirm-directive` and the programmatic `start` API used by tests/smoke) do NOT run the interactive ceremony and behave exactly as today. Additive: an optional `--selection-code SGP-...` CLI arg lets a scripted start commit a pick non-interactively through the SAME decode→validate→`commit_picker_pick` path (no prompt; invalid/stale code fails the start loudly). Every existing walk/integration test passes untouched.

### D3 — Beat-1 kickoff narration + publish-flake degrade (Marcus X1/X4, Dan D4)
The interactive ceremony narrates as the kickoff meeting's first beat: framing line (names all three intake sign-offs and the known end), numbered options, **recommendation with last-used-per-course provenance** when a prior pick event exists for this course (source: the picks JSONL sidecar; display provenance = guide + picked_at + run; **explicit confirm still required — no auto-accept, no timeout, no bypass**), versions default (A/B on a corpus's first run, single on re-runs — derive from prior pick events; overridable). Publish failure (gh-pages flake) degrades per the ratified narration: numbered options = retry publish / **inline text list from the SSOT** (same guides, same selection-code grammar, honest about missing thumbnails) / reuse last pick with provenance. The inline-list path commits through the SAME `commit_picker_pick` shape. All narration text lives beside the existing `narrate_picker_preflight` helpers; injectable `publish_fn`/`input_fn`/`print_fn` keep every path offline-testable.

### D4 — Bitrot audit (Winston) — T1
Before wiring: audit `run_picker_preflight` + `narrate_picker_preflight` + `commit_picker_pick` against the CURRENT marcus_spoc/trial surfaces (zero callers since 2026-07-03 — signatures, SSOT paths, events-path defaults, run_tag validation still coherent?). Fix drift found; report it.

### D5 — F-403 lockstep pin
New test importing BOTH `styleguide_picker._VARIANT_IDS` and `cd.graph._PICK_VARIANT_VOCABULARY`, asserting set equality, with a comment naming the structural no-production-import rule.

## Acceptance criteria

- **AC-1 (ceremony canonical, fail-closed):** interactive start with no confirmed pick after max attempts ⇒ `PickerError`, NO run record/run-dir walk, zero paid dispatch (witness: filesystem + zero dispatch calls).
- **AC-2 (persistence + no re-prompt):** the confirmed pick lands in the directive's `gamma_settings[]` + `styleguide_picker_provenance` (via `write_pick_to_directive`, asserted by shape not reimplementation); `resume`/`recover` of a picked run make ZERO input calls and preserve the pick byte-identically.
- **AC-3 (byte-stable programmatic path):** every pre-existing trial/walk/integration test passes UNTOUCHED; a pickless non-interactive start behaves exactly as at `c24308f7` (WARN-seed staging preserved).
- **AC-4 (S1-seam consumption, F-404 loop closed):** a walk started through the ceremony (offline: fake-LLM real-CD-graph harness from S1's D5 pin) yields a CD `styleguide_resolution` block with `status: resolved` and `bound_guides` naming exactly the picked guide(s).
- **AC-5 (degrade honesty):** injectable-`publish_fn` failure ⇒ the inline-list path completes a valid pick committing the SAME directive shape; the narration presents the three numbered options with a recommendation.
- **AC-6 (F-403 pin):** the lockstep test exists and is green; no production import between the two modules (existing guards stay green).
- **AC-7 (provenance-rich pre-selection, no silent selection):** with a prior pick event for the course, the narration displays it with provenance and still requires explicit confirmation; `--selection-code` scripted path validates/commits identically.
- **AC-L (live witness — orchestrator runs it):** one REAL trial started through the interactive ceremony with a REAL gh-pages picker publish and a REAL selection-code round-trip; the run proceeds into the walk and pauses at G1; the persisted directive carries the pick; the CD contribution (when the walk later crosses 4.75 on resume, or via the offline AC-4 witness against the SAME persisted directive) attests it. `syncing_files` flake handling: publisher fails loud → empty-commit retrigger (known recipe) or the inline-list degrade — either outcome is a valid witness of the designed behavior. First-run-stands.

## RED-first plan
1. `tests/unit/marcus/cli/test_trial_start_picker_preflight.py::test_interactive_start_requires_confirmed_pick` — RED (no ceremony wired).
2. `::test_no_pick_after_max_attempts_aborts_before_run_record` — RED.
3. `::test_resume_and_recover_never_prompt` — RED-by-construction (assert zero input calls).
4. `::test_selection_code_arg_commits_noninteractively` — RED (arg absent).
5. `::test_publish_failure_degrades_to_inline_list_pick` — RED.
6. `tests/marcus/orchestrator/test_picker_cd_vocabulary_lockstep.py::test_variant_vocabularies_identical` — RED or GREEN-by-luck; pin regardless (D5).
7. AC-4 witness extension on the S1 walk-pin harness — RED until D1 threads the pick.
8. AC-3: existing suites green UNTOUCHED (golden constraint, not a new test).

## Out of scope
Gary WARN-seed flip (S4) · parity comparator (S3) · G0 enrichment beats (S5) · picker HTML/emitter changes (the page is already hardened) · manifest edits (none needed) · variant vocabulary changes (F-403 forbids without lockstep ceremony).

## T11 gates
3-lane `bmad-code-review` on the diff; SOP-005 monitor poll pre-dispatch (must verify F-403/F-404 present in this spec — they are, above); SOP-006 at dev-complete; ruff 0-new; focused suites + full pre-existing trial/walk battery green; story flips done only after the live AC-L.
