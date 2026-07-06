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
The runner supplies CD's dispatch with `runner_supplied_payload={"directive_projection": {...}}` using the existing mechanism (`dispatch_adapter.py:108-120`; Texas `directive_path`/`bundle_dir` precedent). Contents: `gamma_settings` (verbatim list from the run's `directive.yaml`), `styleguide_picker_provenance` (verbatim block if present), `directive_digest` (sha256 of the directive file bytes).

**Wiring altitude (SOP-002 F-203, binding):** do NOT add per-walk wiring. Both walk bodies call the single shared `_dispatch_specialist_at_node` (`production_runner.py:1924` — the S4-part-2 refactor exists precisely to forbid per-walk copies). The correct implementation is **one `cd` branch in `_runner_payload_for_specialist` (`production_runner.py:1386`)**, reusing the existing precedents: `_gamma_settings_from_directive` (`:1593` — gary already receives directive-derived `gamma_settings` through this exact seam) and the directive-sha256 pattern (`:852-854`). Continuation-walk `directive_path` availability is already solved (`_resolve_resume_directive_path`, resume `:2775` / recover `:2850`). While there, **extend the seam docstring's runner-context enumeration** (`:1405-1412`) to name `directive_projection` — do not silently ignore its "content delivery forbidden" clause; directive-derived styleguide context is chartered runner context per the gary precedent. Note (F-204): the adapter docstring at `dispatch_adapter.py:65-71` ("runner keys WIN") is STALE — the code RAISES on collision (`:108-120`); design against the code. CD never opens the directive file; the adapter is untouched (a one-line docstring fix is a permitted NIT if the T11 reviewer allows).

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

Rules: produced by the deterministic neck — **a sibling pure function called beside `_canonicalize_cd_directive`** (SOP-002 2(b): the existing neck is called from `_parse_cd_directive` and never sees the envelope payload; the projection is only reachable in `_act` via `_decode_envelope_payload` — so emit via a new pure sibling, same determinism discipline). **The LLM never touches resolution**; **unconditionally present** — projection absent or empty picks ⇒ `status: no_picks_at_authoring` with the **base-layer default resolution still emitted**. **Default-guide pin (SOP-002 F-202, binding):** the no-picks default resolution binds the X5-ratified standard-A guide **`hil-2026-apc-crossroads-classic`**, with provenance string explicitly stating `"authoring-time default; gary runtime seeds DEFAULT_VARIANT_PAIR until S2/S4"` — do NOT attempt to reproduce gary's `DEFAULT_VARIANT_PAIR` (a gary-internal smoke-fixture constant, not a library record); S3's parity comparator keys on `status`, not `resolved` content, for this case. An unknown/deprecated/malformed pick ⇒ `status: unresolvable_pick` carrying the resolver error (do NOT raise — CD is load-bearing; §06 must keep working mid-arc); `CdReturn` (`app/specialists/cd/state.py`) gains the optional field if the state-shape pins require it (`SpecialistReturn` is `extra="forbid"` — SOP-002 2(c); extend pins, NEVER weaken equality assertions, F-205).

### D4 — Registry + overlay staleness fix
Rewrite `skills/bmad-agent-marcus/references/specialist-registry.yaml:87-93` and `:211-216` to the monitor-verified truth (live, load-bearing at §06, styleguide-resolution audit emission per this story; drop "routes around CD"/"activation pending"). Regenerate `state/config/capability-overlay.yaml` via `scripts/utilities/generate_capability_overlay.py` (it is a lockstep trigger path — **read `docs/dev-guide/pipeline-manifest-regime.md` at T1**; this is a Tier-1 regeneration of a generated artifact; CI parity test must be green).

### D5 — F-103 closure: real-CD-graph-in-walk pin
A committed walk-level test where the `_FakeAdapter` canned-cd shim is replaced by the REAL 9-node CD graph (fake LLM per the `tests/composition/test_texas_to_cd_chain.py` pattern) driven through the real dispatch path, asserting the §06 builder consumes the real graph's canonicalized output including `styleguide_resolution`.

## Acceptance criteria

- **AC-1 (determinism pin):** fixed `directive_projection` + fixed SSOT yaml ⇒ byte-stable `styleguide_resolution` across repeated neck invocations. Resolution provably LLM-free (vary the fake LLM's creative output; block unchanged).
- **AC-2 (presence, all three statuses):** `resolved` / `no_picks_at_authoring` / `unresolvable_pick` each emitted correctly; the block is present in EVERY CD contribution; never a missing key, never a raise on bad picks.
- **AC-3 (fence, byte-stable):** `cd_directive` shape and §06 rendering are byte-identical pre/post (regression pin on the §06 builder fold output for a fixed fixture). The load-bearing flow is untouched.
- **AC-4 (dispatch-path witness / F-102 rider):** the block is present when CD is invoked **through the production dispatch adapter** (not the graph directly). Zero new logic in `gate_decision`/`finalize`/`handoff`.
- **AC-5 (both walks + persisted survival):** the projection is supplied and the block lands in the contribution in the start walk AND the continuation walk (parametrized walk test). The continuation-walk case must assert on the **RE-LOADED envelope** (pause → persist → resume → read from disk), not an in-memory walker state (SOP-002 witness-gap note).
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
6. `tests/composition/test_real_cd_graph_walk_pin.py::test_walk_475_with_real_cd_graph_emits_resolution` (AC-4/D5) — RED by construction (F-103). **Anti-vacuity (SOP-002):** the test must obtain the projection through `_runner_payload_for_specialist` — NEVER by hand-feeding `runner_supplied_payload` in the harness, or it greens without proving the runner wiring.
7. §06 fence regression pin (AC-3) — GREEN before, must STAY green after (golden-parity style).

## Out of scope (explicit non-goals)

Gary parity audit + §06 fold of the new block (S3) · WARN→FAIL flips (S4) · authority flip (`styleguide-authority-flip`, deferred) · picker trial-start wiring (S2) · the experience-profile §06 flow (FENCED, AC-3) · F-102 adapter fix (`specialist-interrupt-dead-ceremony`, deferred) · the orchestrator's Leg-C floor read (chartered exception).

## T11 gates

3-lane `bmad-code-review` (Blind Hunter / Edge Case Hunter / Acceptance Auditor) on the diff; ruff 0-new on touched files; focused suites green + `tests/specialists/cd` + gary styleguide suites + composition chain tests; shadow-monitor SOP poll at dev-complete and at story close (ledger: `canonical-arc-claude-shadow-monitor-2026-07-06.md`); story flips done only after live witness AC-L.
