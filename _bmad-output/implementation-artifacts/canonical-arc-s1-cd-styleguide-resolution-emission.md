# Story S1 — CD styleguide-resolution emission

**Arc:** Canonical Production Conversation (party record: `_bmad-output/planning-artifacts/canonical-production-conversation-arc-greenlight-party-record-2026-07-06.md`, esp. **§7 RE-SCOPE ADDENDUM**; W2 contract as amended: `styleguide-binding-cd-contract-2026-07-06.md`).
**Status:** ready-for-dev · **Size:** M · **Gate mode:** single-gate structural (3-lane `bmad-code-review` at T11) · **Branch:** `dev/workbook-2026-07-06`.
**Execution convention:** FRESH dev agent, RED-first, no mocks for live legs, `PYTHONIOENCODING=utf-8` on any subprocess that prints unicode, xdist rule: any new parallel-run red gets one `-n 0` confirmation before triage.

## Context (read before code — all monitor-verified, SOP-001)

CD is **live and load-bearing**: dispatched generically at manifest node `4.75` in BOTH runner walks; its `_act` (inside `app/specialists/cd/graph.py:388-459` — there is no separate `_act.py`) invokes the model cascade and writes `cd_directive` `{schema_version, experience_profile, slide_mode_proportions, narration_profile_controls, creative_rationale}` via the deterministic neck `_canonicalize_cd_directive` (graph.py:295-302). §06's `package_builders.py:221-236` **fails loud** without the cd contribution and folds the profile/rationale into Gary's briefs. CD does NOT touch styleguides today: the seam runs picker→directive `gamma_settings[]`→Gary `resolve_styleguide()` (`app/specialists/gary/_act.py:501-517`, library at `app/specialists/gary/styleguide_library.py`, SSOT `state/config/gamma-style-guides.yaml`), with the styleguide-less WARN-seed at `_act.py:519-528` ("fail-loud deferred to cd-envelope-authoring").

**F-102 (binding design constraint):** production dispatch NEVER resumes specialist sub-graphs — `gate_decision`/`finalize`/`handoff` never execute; interrupts land in write-only `last_interrupts`. ALL S1 work must live in the `_act`/neck path and be visible in the contribution output.

**This story makes CD the styleguide-resolution AUDIT point (data emission only).** Gary's authority is untouched. The parity consumer is S3; the FAIL-LOUD flip is S4 (gated S1∧S2∧S3); the authority flip is the deferred `styleguide-authority-flip` story.

## Deliverables

### D1 — Shared pure resolver, re-homed
Extract the deterministic resolution core (`resolve_styleguide` / `load_style_guides` / `expand_record` and their private helpers as needed) from `app/specialists/gary/styleguide_library.py` into a neutral shared module — preferred home `app/styleguide/resolver.py` (new package) or `app/specialists/_shared/styleguide_resolver.py`. **T1 task: check the import-linter contracts (lint-imports config) and pick the home that passes them.** Hard requirements: importable from `app/specialists/cd`, `app/specialists/gary`, and `app/marcus/orchestrator` without any of them importing `app.specialists.gary`; pure functions, no run-state, no I/O beyond the yaml read; `app/specialists/gary/styleguide_library.py` becomes a **thin re-export preserving its full public API byte-compatibly** (every existing import site and test untouched and green).

### D2 — Orchestrator-side `directive_projection` at the §4.75 dispatch site
The runner supplies CD's dispatch with `runner_supplied_payload={"directive_projection": {...}}` using the existing mechanism (`dispatch_adapter.py:108-120`; Texas `directive_path`/`bundle_dir` precedent). Contents: `gamma_settings` (verbatim list from the run's `directive.yaml`), `styleguide_picker_provenance` (verbatim block if present), `directive_digest` (sha256 of the directive file bytes). Wired at the 4.75 dispatch site **in BOTH walk bodies** (start `production_runner.py:~2557` branch AND continuation `~3284` branch — exact call sites verified at T1; the two-walks gotcha is real). CD never opens the directive file; the adapter is untouched.

### D3 — CD emits the sibling `styleguide_resolution` block (deterministic neck only)
`_act` output (the cache_prefix JSON) gains a **sibling** key next to `cd_directive` — NEVER inside it:

```yaml
styleguide_resolution:
  schema_version: 1
  status: resolved | no_picks_at_authoring | unresolvable_pick
  input_picks: <verbatim echo of gamma_settings[] styleguide entries + provenance, or null>
  bound_guides: [ {name, ssot_digest} ]          # per variant; two entries on A/B
  resolved: <full resolver output per bound guide — the frozen base-layer field set>
  layering_manifest:
    base_layer: styleguide_defaults
    composition_rule: source_derived_wins        # 🔒 protected invariant, explicit
  resolution_digest: <sha256 of canonical-JSON of `resolved`>
  directive_digest: <echoed from the projection, or null>
```

Rules: produced by the deterministic neck (extend `_canonicalize_cd_directive` or a sibling pure function called beside it) — **the LLM never touches resolution**; **unconditionally present** — projection absent or empty picks ⇒ `status: no_picks_at_authoring` with the **base-layer default resolution still emitted** (exercises the resolver every run; explicit provenance string, never a missing key); an unknown/deprecated/malformed pick ⇒ `status: unresolvable_pick` carrying the resolver error (do NOT raise — CD is load-bearing; §06 must keep working mid-arc); `CdReturn` (`app/specialists/cd/state.py`) gains the optional field if the state-shape pins require it.

### D4 — Registry + overlay staleness fix
Rewrite `skills/bmad-agent-marcus/references/specialist-registry.yaml:87-93` and `:211-216` to the monitor-verified truth (live, load-bearing at §06, styleguide-resolution audit emission per this story; drop "routes around CD"/"activation pending"). Regenerate `state/config/capability-overlay.yaml` via `scripts/utilities/generate_capability_overlay.py` (it is a lockstep trigger path — **read `docs/dev-guide/pipeline-manifest-regime.md` at T1**; this is a Tier-1 regeneration of a generated artifact; CI parity test must be green).

### D5 — F-103 closure: real-CD-graph-in-walk pin
A committed walk-level test where the `_FakeAdapter` canned-cd shim is replaced by the REAL 9-node CD graph (fake LLM per the `tests/composition/test_texas_to_cd_chain.py` pattern) driven through the real dispatch path, asserting the §06 builder consumes the real graph's canonicalized output including `styleguide_resolution`.

## Acceptance criteria

- **AC-1 (determinism pin):** fixed `directive_projection` + fixed SSOT yaml ⇒ byte-stable `styleguide_resolution` across repeated neck invocations. Resolution provably LLM-free (vary the fake LLM's creative output; block unchanged).
- **AC-2 (presence, all three statuses):** `resolved` / `no_picks_at_authoring` / `unresolvable_pick` each emitted correctly; the block is present in EVERY CD contribution; never a missing key, never a raise on bad picks.
- **AC-3 (fence, byte-stable):** `cd_directive` shape and §06 rendering are byte-identical pre/post (regression pin on the §06 builder fold output for a fixed fixture). The load-bearing flow is untouched.
- **AC-4 (dispatch-path witness / F-102 rider):** the block is present when CD is invoked **through the production dispatch adapter** (not the graph directly). Zero new logic in `gate_decision`/`finalize`/`handoff`.
- **AC-5 (both walks):** the projection is supplied and the block lands in the contribution in the start walk AND the continuation walk (parametrized walk test).
- **AC-6 (shared resolver, API-stable):** gary's `styleguide_library` public API byte-compatible (existing gary/styleguide tests green untouched); no module among cd/orchestrator imports `app.specialists.gary`; lint-imports green.
- **AC-7 (protected invariant):** `layering_manifest.composition_rule == source_derived_wins` asserted; the block introduces NO change to Gary's runtime composition (S1 changes zero Gary behavior).
- **AC-8 (legacy tolerance):** an envelope-absent (pre-S1 / rewind-recovered) bundle passes all readers; `schema_version` discriminates.
- **AC-9 (registry/overlay):** registry prose corrected; overlay regenerated; CI parity green; overlay `cd.capability_state` no longer `partial` on the stale ground (regenerate honestly — if it stays partial for a REAL residual reason, record it).
- **AC-L (live witness, small-$):** one REAL live dispatch of the texas→cd chain (or CD with a real corpus payload) under `--run-live`: `styleguide_resolution` present with `status` matching the projection; the neck re-run on the captured inputs reproduces the block byte-identically. First-run-stands.

## RED-first plan (write these failing tests FIRST)

1. `tests/specialists/cd/test_styleguide_resolution_emission.py::test_contribution_carries_resolution_block` (AC-2 resolved-path) — RED: no block exists.
2. `::test_no_picks_emits_presence_record` (AC-2) — RED.
3. `::test_unresolvable_pick_recorded_not_raised` (AC-2) — RED.
4. `::test_neck_determinism_byte_stable` (AC-1) — RED.
5. `tests/orchestrator/test_cd_dispatch_payload_projection.py::test_475_payload_carries_directive_projection` (AC-5/D2, against a directive patched by `write_pick_to_directive`) — RED.
6. `tests/composition/test_real_cd_graph_walk_pin.py::test_walk_475_with_real_cd_graph_emits_resolution` (AC-4/D5) — RED by construction (F-103).
7. §06 fence regression pin (AC-3) — GREEN before, must STAY green after (golden-parity style).

## Out of scope (explicit non-goals)

Gary parity audit + §06 fold of the new block (S3) · WARN→FAIL flips (S4) · authority flip (`styleguide-authority-flip`, deferred) · picker trial-start wiring (S2) · the experience-profile §06 flow (FENCED, AC-3) · F-102 adapter fix (`specialist-interrupt-dead-ceremony`, deferred) · the orchestrator's Leg-C floor read (chartered exception).

## T11 gates

3-lane `bmad-code-review` (Blind Hunter / Edge Case Hunter / Acceptance Auditor) on the diff; ruff 0-new on touched files; focused suites green + `tests/specialists/cd` + gary styleguide suites + composition chain tests; shadow-monitor SOP poll at dev-complete and at story close (ledger: `canonical-arc-claude-shadow-monitor-2026-07-06.md`); story flips done only after live witness AC-L.
