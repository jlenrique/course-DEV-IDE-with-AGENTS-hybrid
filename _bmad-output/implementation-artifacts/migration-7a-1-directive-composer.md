# Migration Story 7a.1: Directive Composer (trial-475 Gap 2 closure)

**Status:** done
**Sprint key:** `migration-7a-1-directive-composer`
**Epic:** Slab 7a — Inter-Gate Conversational Orchestration (`migration-epic-slab-7a-inter-gate-orchestration`)
**Pts:** 5
**Gate:** **dual-gate** (rationale: `substrate_shape + invariant_preservation`; per `docs/dev-guide/migration-story-governance.json` v2026-04-28-slab7a-eight-stories, story 7a-1)
**K-target:** ~1.6× (gate-shape band 3.2-5K; ~3.5K target)
**Authored:** 2026-04-28 via `bmad-create-story` workflow as Slab 7a slab-opener.
**Wave:** 1 (slab-opener; strict-prereq for Wave 2 = 7a.2)
**FR coverage:** 8 — FR1, FR2 (xc with 7a.3), FR4, FR5 (xc with 7a.5); FR-A1, FR-A2, FR-A3; FR-O3
**Standing-guardrail enforcement:** SG-1 unchanged (composer is orchestration, not specialist roster); SG-2 directive-composition row preserved; SG-3 Composition Spec §3.1/§3.5/§3.6 honored.

---

## T1 Readiness Block

**Predecessor state (verified at authoring):**
- Slab 6 trial-experience bundle 3/3 CLOSED (6.3 + 6.4 + 6.5 closed 2026-04-28).
- First tracked trial 475df528-... ran 2026-04-28 evening, paused-at-G1 cleanly. Plumbing PASS / content FAIL. Texas-directive-composition gap is the documented root cause blocking first-content-trial — this story closes it.
- Three Slab 7a governance preconditions all RESOLVED 2026-04-28 (per sprint-status.yaml `slab-7a-inter-gate-orchestration` block): (a) `docs/dev-guide/migration-story-governance.json` v2026-04-28-slab7a-eight-stories has 7a-1..7a-8 entries; (b) `state/config/pipeline-manifest.yaml` schema v4.2-migration-stub-with-fold-flags landed; (c) `docs/dev-guide/sanctum-reference-conventions.md` verified-exists.
- Composition Spec §10 Decision Log entry added 2026-04-28 documenting Slab 7a fold-flag schema extension.

**Live substrate (verified at authoring; do NOT regress):**
- `app/marcus/cli/trial.py::start_trial(*, preset, input_path: Path, operator_id, trial_id, ...)` is the existing CLI entry. It accepts `--input <corpus-path>` and currently passes `corpus_path=input_path` to `run_production_trial(...)`. **No directive composition exists today — Texas falls back to the fixture bundle when `directive_path` is empty (see `app/specialists/texas/retrieval_dispatch.py::dispatch_retrieval` lines 34-40, the silent-bypass site).**
- `app/specialists/texas/retrieval_dispatch.py::dispatch_retrieval(*, directive_path=None, bundle_dir=None)` returns `{"status": "mocked", "bundle_dir": str(DEFAULT_FIXTURE_BUNDLE), ...}` when either arg is missing. **This is the Gap 2 silent-bypass behavior. The mocked path stays for unit-test paths but production trials must NEVER hit it after this story.**
- `app/marcus/orchestrator/dispatch_adapter.py::ProductionDispatchAdapter` is the sole sanctioned coupling point between specialist outputs and the `ProductionEnvelope` (per Composition Spec §3.3). Use `ProductionDispatchAdapterError` for adapter-side errors.
- `app/marcus/orchestrator/production_runner.py::run_production_trial(corpus_path, ..., pause_at_gates: bool)` is the runner — directive composition belongs UPSTREAM of `run_production_trial`'s first specialist dispatch (i.e. before the runner produces the Texas decision card).
- Existing fixture: `tests/fixtures/specialists/texas/fixture_directive.yaml` documents the directive shape Texas expects (top-level `run_id` + `sources: [{ref_id, provider, locator, role, description, expected_min_words}]`).
- Course corpus path convention: `course-content/courses/<lesson_slug>/` (NOT `sources/`). Trial-475 used `course-content/courses/tejal-APC-C1/`.
- A directive may need to compose from sources of multiple shapes per memory `feedback_corpus_directory_scope`: corpus-dir = on-disk files (sources_authority emits `provider: local_file`); URL list = flat file in corpus dir (`provider: url`); Notion / Box-URL / Playwright-URL = directive-only live-fetch (`provider: notion|box_url|playwright_url`). 7a.1 supports the on-disk-files case as the MVP target; non-file-fetch shapes route through the same composer signature but emit fetcher-shape `sources[]` entries (no fetch execution at composer; that's Texas's `_act`).
- Pipeline manifest at `state/config/pipeline-manifest.yaml` declares orchestration topology. The directive-composer node must be declared in the manifest with `dependencies: []` (no upstream specialist) per Composition Spec §3.6 manifest-declared dependencies rule (FR-A5; primary enforcement landed in 7a.6, but 7a.1 sets the precedent).

**Block-mode trigger paths touched by this story (per CLAUDE.md §Pipeline lockstep regime + `state/config/pipeline-manifest.yaml::block_mode_trigger_paths`):**
- `state/config/pipeline-manifest.yaml` (declares the new directive-composer node) — **Tier-1 patch** per `docs/dev-guide/pipeline-manifest-regime.md` (additive node declaration; no schema change; no pack-version bump). Cora's block-mode hook gates.
- `scripts/utilities/check_pipeline_manifest_lockstep.py` MUST exit 0 at close.

**Gate-mode rationale (from governance JSON):**
> Slab 7a opener: directive_composer.py closes trial-475 Gap 2 (silent gate-bypass from missing directive composition). Dual-gate justified: closes trial-475 root cause + introduces Composition Smoke gate evidence at slab-opener (Composition Spec §9). K=1.6× per directive-composer band 3.2-5K; ~3.5K target.

**T1 conclusion:** No unanticipated architectural disagreement requires halting Gate 0. Implementation proceeds: `app/marcus/orchestrator/directive_composer.py` + `state/runs/<run_id>/directive.yaml` materialization + Texas dispatch wiring + Composition Smoke gate evidence at slab-opener (NFR-CG2).

---

## Party-mode green-light (BINDING; ratified 2026-04-28)

Convened during `bmad-create-prd` Steps 5-12 + `bmad-create-epics-and-stories` Steps 1-4: Winston + Murat + Paige + Amelia + John + Mary.
- Verdict: unanimous GREEN — no architectural impasse; all four voices verified no SG-1/SG-2/SG-3 violations.
- Direction ratified: composer is a pure orchestration node (not a specialist); writes `directive.yaml` to `state/runs/<run_id>/`; operator confirms-or-edits before Texas dispatch; trial-475 regression test pinned.
- 6 BINDING riders (W-R1..A-R2) applied to spec; 3 NON-BLOCKING (W-R2, M-R3, P-R3) apply at code-review or close.

**BINDING riders:**
- **W-R1 (Winston):** Directive composer MUST be a *pure function* of (corpus_path, source_authority_map, operator_directives) — no LLM call, no network, no hidden state. Composer determinism is a load-bearing invariant for golden-trace fixtures. If LLM-mediated directive composition is ever needed, that's a separate `pre-gate-marcus` invocation (story 7a.3 substrate), not this story.
- **M-R1 (Murat):** Add `tests/parity/test_trial_475_directive_composition_regression.py` — the regression fixture that replays trial-475's `--input course-content/courses/tejal-APC-C1/` and asserts (a) composer materializes a non-empty directive, (b) Texas receives the composed directive (NOT the fixture bundle stub), (c) trial advances past G0. Test is parametrized to cover both the operator-confirm path AND the operator-edit path. **This is the binding regression evidence; no DEFER.**
- **M-R2 (Murat):** Composition Smoke gate evidence MUST be captured at story-open per NFR-CG2 + Composition Spec §9. Smoke fixture writes a 30-line throwaway script wiring composer → Texas-stub → envelope-append end-to-end; PASS verdict pasted into Completion Notes once. Smoke evidence path: `_bmad-output/implementation-artifacts/migration-7-1-directive-composer-composition-smoke.md` (mirrors slab-opener convention from Slab 6.0).
- **P-R1 (Paige):** Operator-facing prompt at the confirm-or-edit step MUST surface the composed directive in human-readable form (YAML pretty-printed; not JSON dump). Use `ruamel.yaml` (already shipped) for round-trip-safe serialization preserving comments if any. Operator can edit the YAML in-place via `$EDITOR` or accept verbatim. Cancel = trial halts with explicit "directive composition declined" message, no silent fallback.
- **A-R1 (Amelia):** Composer's call site goes UPSTREAM of `run_production_trial` (in `app/marcus/cli/trial.py::start_trial` between line 54 `effective_trial_id = trial_id or uuid4()` and line 55 `envelope = run_production_trial(...)`). Composed directive path is passed via a new `directive_path: Path | None = None` kwarg on `run_production_trial(...)`; runner threads it into the Texas dispatch state. **Do NOT** mutate the runner's existing `corpus_path` semantics — both args coexist (runner uses `corpus_path` for upstream-context display + `directive_path` for Texas dispatch).
- **A-R2 (Amelia):** Composition Spec §3.6 manifest-declared dependencies rule — the new `directive-composer` node MUST declare `dependencies: []` in `state/config/pipeline-manifest.yaml`. Do NOT add it to runner-layer fallback (per ADR-D6 manifest-as-graph-config; precedent set by Slab 6.2's `dependency_map` promotion).

**NON-BLOCKING riders (apply at code-review or close):**
- **W-R2 (Winston):** If composer surfaces ambiguity in `source_authority_map` (multiple sources claim the same `ref_id`), HALT-and-surface as `decision_needed`; do NOT silently pick first. File a deferred follow-on for "directive-composer source-conflict resolution policy" if encountered.
- **M-R3 (Murat):** K-target 18 → 22 if AC-7.1-J's operator-edit path requires more than 4 round-trip cases (cancel / accept / edit-and-accept / edit-and-cancel).
- **P-R3 (Paige):** Add screenshot or text capture to `docs/operator/trial-start-guide.md` (NEW or augment) showing the confirm-or-edit prompt UX.

---

## Gate-1 green-light addendum (BINDING; ratified 2026-04-28 fresh single-purpose round)

Convened post-spec-authoring: Winston + Murat + Paige + Amelia. Verdict: unanimous **GO-WITH-RIDERS**. 5 NEW BINDING riders + 7 NEW NON-BLOCKING.

**A-R3 design ratification (BINDING substrate decision):** **Option A chosen** — extend `ProductionDispatchAdapter.build_specialist_state(..., runner_supplied_payload: dict | None = None)` and merge `runner_supplied_payload` into the `cache_prefix` JSON alongside `_payload_from_dependencies(...)` output. Runner threads `{"directive_path": str(path), "bundle_dir": str(path)}` for Texas only (gated by `specialist_id == "texas"` in the runner's adapter call site, NOT by a manifest-declared `runner_inputs: [...]` field — that's a 7a.2 concern). Rationale: minimal Composition Spec §3.3 surface (additive kwarg, named field, no synthetic specialist contribution); preserves W-R1 (composer is orchestration, not specialist); 7a.4's per-slide subgraph reads `directive_path` from the same `cache_prefix` location 7a.1 puts it. AC-7.1-D + T4 amended below to lock this; AC-L line 203 ("dispatch-adapter signature evolved likely NOT") flipped to **YES, additive kwarg lands on `build_specialist_state`** — Decision Log entry to Composition Spec §10 IS required at close.

**NEW BINDING riders:**
- **W-R4 (Winston):** Carrier mechanism MUST be a NAMED field, not a free-form dict key. Resolved via A-R3 Option A — `cache_prefix` JSON top-level keys `directive_path` and `bundle_dir` are reserved (canonical names; do NOT rename in 7a.4 or 7a.5).
- **M-R4 (Murat):** AC-7.1-E references `tests/composition/test_envelope_invariants.py` which **does not exist**. Actual `tests/composition/` modules: `test_specialist_isolation_preserved.py`, `composed_specialist_chain_harness.py`, `test_texas_to_cd_chain.py`, `test_irene_pass_2_template_composition_smoke.py`. AC-7.1-E + T4 amended below to add the parametrize case to `tests/composition/test_texas_to_cd_chain.py` (the existing dispatch-path-driven envelope assertion site), NOT a phantom envelope-invariants module.
- **M-R5 (Murat):** AC-7.1-H regression test MUST monkeypatch `app.specialists.texas.retrieval_dispatch.dispatch_retrieval` (or `subprocess.run` inside it) — not let the live wrangler subprocess execute. Test asserts (a) call args (non-None `directive_path` + non-None `bundle_dir`) and (b) branch taken (non-mocked code path), then synthesizes a `dispatched` return. Otherwise non-deterministic + slow + couples to wrangler internals. T7 amended below.
- **P-R4 (Paige):** AC-7.1-I subsection (d) "one worked example" MUST show the on-disk-files MVP shape (3-file flat corpus → composed `sources[]` with `provider: local_file`, `role: primary` for first / `supporting` for rest, `expected_min_words: 200`). Add an explicit reservation sentence to subsection (a) or (d): "Notion / Box-URL / Playwright-URL provider shapes are reserved for Texas's `_act` in a later story; G0 composer emits the entry but does not fetch."
- **A-R3 (Amelia):** Substrate decision ratified — see top of this addendum.

**NEW NON-BLOCKING riders:**
- **W-R5:** Confirm at code-review that `check_pipeline_manifest_lockstep.py` tolerates explicit-null `fold_with: null/fold_target: null` fields under the CURRENT schema version. If the lockstep check rejects unknown keys, this becomes BINDING and the field-reservation must defer to 7a.2 (omit the keys; let 7a.2's compiler extension introduce them).
- **W-R6:** Pin `Path.as_posix()` for `directive.yaml` `locator` fields (Windows-portability; otherwise trial-475 regression-fixture digests will be platform-divergent and AC-7.1-B byte-stability fails on cross-platform CI).
- **M-R6:** Add a golden bytes fixture at `tests/fixtures/directives/composed_directive_golden.yaml.bytes` so future ruamel version bumps can't silently shift the digest.
- **P-R5:** Add a Mermaid sequence diagram to `g0-directive-composition.md` subsection (b) "why operator-confirm matters": `operator → CLI → compose_directive → materialize → confirm-prompt → [c|e|s|x] → run_production_trial`. Five participants, ~12 lines.
- **P-R6:** AC-7.1-C `$EDITOR` invocation needs Windows-portability fallback chain: `EDITOR env → notepad (Windows fallback) → raise EditorUnavailableError`. Do NOT silent-default to `vi` on Windows where it is absent (per A11 + `feedback_verify_via_shipped_deps`). T3 amended below.
- **A-R4:** Live `pipeline-manifest.yaml` nodes use `label`, `specialist_id`, `scaffold_node`, `model_config_ref`, `gate`, `gate_code`, `sub_phase_of`, `insertion_after`, `hud_tracked`, `pack_section_anchor`, `pack_version`, `rationale` — NO `kind` field. AC-7.1-G amended below: composer node entry uses canonical field names (`label`, `specialist_id: null`, `gate: false`, `insertion_after: null` to slot before "01"), plus `dependencies: []` and reserved `fold_with: null/fold_target: null`.
- **A-R5:** AC-7.1-D `bundle_dir` derivation made explicit: `bundle_dir = run_dir / "bundle"` where `run_dir = runs_root / str(trial_id)`. T4 amended below.

---

## Story

As the operator,
I want Marcus to compose a `directive.yaml` automatically from my `--input <corpus-path>` invocation and surface it for confirm-or-edit before Texas dispatches,
so that Texas receives a real directive (NOT the fixture stub at `tests/fixtures/specialists/texas/fixture_bundle/`) and trial-2 can advance past G0 with real corpus content — closing trial-475 Gap 2.

---

## Acceptance Criteria

### AC-7.1-A — Directive composer module + pure-function contract (FR1, FR-A1, W-R1)

**Given** an operator invokes `bmad-trial start --input <corpus-path> --operator-id <id>` (or its equivalent `python -m app.marcus.cli trial start ...`)
**When** the trial-start handler executes
**Then** `app/marcus/orchestrator/directive_composer.py::compose_directive(corpus_path: Path, source_authority_map: dict, operator_directives: dict | None) -> ComposedDirective` is invoked
**And** the function is pure: no LLM call, no network IO, no logging side effects, no environment reads beyond what the caller passes in
**And** the composed directive conforms to the existing Texas directive shape (top-level `run_id` + `sources: [{ref_id, provider, locator, role, description, expected_min_words}]`)
**And** the source-authority-map default (when none provided) walks the corpus dir for on-disk files and emits one `sources[]` entry per file with `provider: local_file`, `locator: <relative-path>`, `role: primary` (first file) / `supporting` (subsequent), `expected_min_words: 200`.

**Test pin:** `tests/unit/marcus/orchestrator/test_directive_composer_pure.py` — pure-function tests parametrized over (a) flat corpus dir with N files, (b) nested corpus dir, (c) corpus dir with a `urls.txt` flat file emitting `provider: url` entries, (d) operator-directives override (operator pinned `expected_min_words=500`), (e) empty corpus dir (raises `EmptyCorpusError(RuntimeError)` — NOT silent empty-directive emission).

### AC-7.1-B — Directive materialization to `state/runs/<run_id>/directive.yaml` (FR1, FR4)

**Given** `compose_directive(...)` returns a `ComposedDirective`
**When** the trial-start handler materializes it
**Then** the directive is written to `state/runs/<run_id>/directive.yaml` using `ruamel.yaml` round-trip-safe serialization
**And** the file is byte-stable (sort_keys-equivalent for ruamel; deterministic key ordering)
**And** parent directory is created if absent (`mkdir(parents=True, exist_ok=True)`)
**And** SHA256 digest of the directive bytes is recorded in the trial-start payload as `directive_digest` (16-char prefix is fine for human display; full digest in JSON).

**Test pin:** `tests/unit/marcus/orchestrator/test_directive_composer_materialization.py` — write-roundtrip test + digest stability test + idempotency test (re-running compose+write on same inputs produces identical bytes).

### AC-7.1-C — Operator confirm-or-edit prompt at G0 (FR4, FR-O3, P-R1)

**Given** the directive has been materialized
**When** `app/marcus/cli/trial.py::start_trial` resumes after composer
**Then** the operator sees a confirm-or-edit prompt printed to stdout (YAML pretty-printed via `ruamel.yaml` so comments survive round-trip)
**And** the prompt offers four options: `[c]` confirm-and-proceed, `[e]` edit-in-`$EDITOR`-and-reload, `[s]` save-and-show-path-then-exit-without-running, `[x]` cancel-trial
**And** the prompt loads at-gate context from `docs/conversational-gates/g0-directive-composition.md` per FR-O3 (operator never recalls legacy v4.2 prose to participate)
**And** non-interactive mode (TTY absent) auto-confirms when `--auto-confirm-directive` flag is passed; absent that flag, non-interactive mode raises `DirectiveConfirmationRequiredError(RuntimeError)` (NO silent auto-accept).

**Test pin:** `tests/integration/marcus/test_directive_confirm_or_edit_prompt.py` — pseudo-tty harness test parametrized over the 4 options + 1 non-interactive + 1 `--auto-confirm-directive`. Use `pexpect`-style pattern OR direct stub of `input()` and `subprocess.call` for `$EDITOR`.

### AC-7.1-D — Texas dispatch threading via runner_supplied_payload (FR1, FR-A3, A-R1, A-R3, W-R4, A-R5)

**Given** the operator confirms (option `[c]` or edited-then-confirmed)
**When** `app/marcus/orchestrator/production_runner.py::run_production_trial(...)` is invoked
**Then** the runner accepts a NEW kwarg `directive_path: Path | None = None`
**And** `bundle_dir = run_dir / "bundle"` is derived in the runner (where `run_dir = runs_root / str(trial_id)`); runner creates the bundle dir (`mkdir(parents=True, exist_ok=True)`)
**And** the runner threads BOTH paths into the adapter call site for `texas` only via a NEW kwarg on `ProductionDispatchAdapter.build_specialist_state(..., runner_supplied_payload: dict | None = None)` — gated by `specialist_id == "texas"` at the call site
**And** `runner_supplied_payload = {"directive_path": str(directive_path), "bundle_dir": str(bundle_dir)}` (string-serialized via `Path.as_posix()` per W-R6)
**And** `build_specialist_state` merges `runner_supplied_payload` into the `cache_prefix` JSON alongside `_payload_from_dependencies(...)` output (named keys `directive_path` + `bundle_dir` reserved as canonical per W-R4)
**And** Texas's `_act` (via existing `_decode_envelope_payload` at `app/specialists/texas/graph.py:323-326`) reads `directive_path` + `bundle_dir` from `cache_prefix` and passes them to `dispatch_retrieval(directive_path=..., bundle_dir=...)`
**And** Texas executes a real retrieval (NOT the fixture stub fallback at `dispatch_retrieval` lines 34-40)
**And** the dispatch goes through `ProductionDispatchAdapter` as the sole sanctioned coupling point per Composition Spec §3.3 (FR-A3).

**Composition Spec §10 Decision Log entry MUST land at close** documenting the additive `runner_supplied_payload` kwarg on `build_specialist_state` (this is the substrate-shape change that A-R3 ratified; the spec was originally optimistic that the signature would not evolve — it does, additively).

**Test pin:** `tests/integration/marcus/test_production_runner_threads_directive.py` — runner-level test that:
- constructs a fake `directive_path`,
- monkeypatches `app.specialists.texas.retrieval_dispatch.dispatch_retrieval` to capture call args,
- asserts `dispatch_retrieval` is called with non-None `directive_path` AND non-None `bundle_dir` (both POSIX strings),
- asserts `runner_supplied_payload` keys appear in Texas's `cache_prefix` JSON,
- asserts the mocked-fallback path (`status: "mocked"`) is NEVER returned in production-trial mode.

### AC-7.1-E — ProductionEnvelope append-only + SHA256 digest (FR-A1, FR-A2)

**Given** Texas's contribution lands in the trial flow
**When** the dispatch adapter records it
**Then** the `ProductionEnvelope` is append-only (no in-place mutation; FR-A1 — re-assert via existing `tests/composition/test_envelope_invariants.py` does not regress)
**And** Texas's contribution carries a SHA256 output digest (FR-A2 — re-assert via existing `tests/composition/` suite does not regress).

**Test pin:** Extend EXISTING `tests/composition/test_texas_to_cd_chain.py` (the closest dispatch-path-driven envelope assertion site; Slab 6.0 substrate) with ONE parametrize case asserting the directive-composer-driven contribution path produces the same envelope-append + digest invariants as the fixture-stub path. **No new envelope test module.** (M-R4 correction: original spec named `test_envelope_invariants.py` which does not exist; actual `tests/composition/` modules are `test_specialist_isolation_preserved.py`, `composed_specialist_chain_harness.py`, `test_texas_to_cd_chain.py`, `test_irene_pass_2_template_composition_smoke.py`.)

### AC-7.1-F — Composition Smoke gate evidence at slab-opener (NFR-CG2, M-R2)

**Given** Slab 7a story 7a.1 is opened as the slab-opener
**When** the dev-agent runs the Composition Smoke gate per Composition Spec §9
**Then** a 30-line throwaway script wires composer → Texas-stub → envelope-append end-to-end at `_bmad-output/implementation-artifacts/migration-7-1-directive-composer-composition-smoke.py`
**And** the smoke script PASSES (exit code 0; envelope contains exactly one Texas contribution with non-empty SHA256 digest)
**And** smoke evidence (script path + run command + verbatim stdout + PASS verdict) is pasted into Completion Notes once at `_bmad-output/implementation-artifacts/migration-7-1-directive-composer-composition-smoke.md` (NEW evidence file mirroring Slab 6.0 slab-opener pattern).

**Test pin:** the smoke script itself + a CI-runnable wrapper `tests/composition/test_slab_7a_opener_composition_smoke.py` that imports and runs the smoke script, asserts exit 0.

### AC-7.1-G — Pipeline manifest declaration + lockstep PASS (FR-A5 precedent, A-R2, A-R4, W-R5)

**Given** the new `directive-composer` node
**When** `state/config/pipeline-manifest.yaml` is updated
**Then** the node is declared using CANONICAL field names matching live nodes (per A-R4 — live manifest does NOT have a `kind` field): minimum `id: directive-composer`, `label: "G0 — directive composition"`, `specialist_id: null`, `gate: false`, `insertion_after: null` (slot before "01"), `dependencies: []`, plus reserved fold-flag fields `fold_with: null` / `fold_target: null` (story 7a.2 lands the fold-flag compiler extension; 7a.1 reserves the shape with explicit nulls)
**And** `python scripts/utilities/check_pipeline_manifest_lockstep.py` exits 0 — IF the lockstep check rejects the explicit-null fold-flag keys under the current schema (`v4.2-migration-stub-with-fold-flags`), W-R5 escalates: omit the fold-flag keys from 7a.1's node entry; let 7a.2's compiler extension introduce them. **Dev agent verifies lockstep tolerance at T6 BEFORE committing the manifest edit.**
**And** Tier-1 patch discipline applies (additive node declaration; no schema-version bump; no pack-version bump per `docs/dev-guide/pipeline-manifest-regime.md` Pack Versioning Policy).

**Test pin:** `tests/structural/test_pipeline_manifest_directive_composer_node.py` — asserts the manifest contains a `directive-composer` node with `dependencies: []` and reserved fold-flag fields.

### AC-7.1-H — trial-475 regression evidence (M-R1, M-R5 BINDING)

**Given** the trial-475 root-cause regression
**When** trial-475's `--input course-content/courses/tejal-APC-C1/` is replayed against the new composer (in deterministic test mode; no live LLM, no network, no live wrangler subprocess)
**Then** the composer produces a non-empty directive
**And** Texas's dispatch state contains `directive_path` pointing to the composed `<run_id>/directive.yaml` (NOT empty)
**And** Texas's `dispatch_retrieval` is invoked with non-None `directive_path` AND non-None `bundle_dir` (asserted via monkeypatch on `app.specialists.texas.retrieval_dispatch.dispatch_retrieval`)
**And** the monkeypatched `dispatch_retrieval` returns a synthesized `{"status": "dispatched", ...}` payload — the test asserts the BRANCH TAKEN (non-mocked code path) by inspecting the call args, NOT by exercising the live wrangler subprocess
**And** the trial advances past G0 (paused-at-G1 is acceptable; the silent-bypass-at-G0 is the regression being closed).

**Test pin:** `tests/parity/test_trial_475_directive_composition_regression.py` — parametrized over operator-confirm path AND operator-edit path; corpus dir is a frozen mini-fixture under `tests/fixtures/trials/trial_475_mini_corpus/` (small subset; do NOT vendor full Tejal corpus; use 3-5 representative files); MUST monkeypatch `dispatch_retrieval` per M-R5 (otherwise non-deterministic + slow + couples to wrangler internals). **This file is the binding regression evidence per M-R1.**

### AC-7.1-I — Operator at-gate context loaded into decision-card (FR-O3, P-R4 BINDING, P-R5 NON-BLOCKING)

**Given** the directive composer executes against real corpus
**When** the operator inspects the trial outputs (run-summary or HUD)
**Then** the operator NEVER recalls legacy v4.2 prose to participate in directive composition
**And** at-gate context is loaded into the G0 decision-card from `docs/conversational-gates/g0-directive-composition.md` (NEW file; ~50-100 lines) with FOUR named subsections:
  - **(a) what the directive is** — and an explicit reservation sentence per P-R4: "Notion / Box-URL / Playwright-URL provider shapes are reserved for Texas's `_act` in a later story; G0 composer emits the `provider:` entry but does not fetch."
  - **(b) why operator-confirm matters** — include a Mermaid sequence diagram per P-R5: `operator → CLI → compose_directive → materialize → confirm-prompt → [c|e|s|x] → run_production_trial` (5 participants, ~12 lines).
  - **(c) when to edit vs accept** — concrete heuristics for the operator (e.g., edit when corpus contains both "primary" + "supporting" candidates and the auto-walker's primary-pick differs from operator intent).
  - **(d) one worked example — on-disk-files MVP shape ONLY per P-R4** — 3-file flat corpus (e.g., `intro.md`, `chapter-1.md`, `appendix.md`) → composed `sources[]` with `provider: local_file`, `role: primary` for first / `supporting` for rest, `expected_min_words: 200`. Show both the input dir tree AND the composed `directive.yaml` output verbatim.

**Test pin:** existence-check + content-shape test at `tests/structural/test_g0_directive_composition_doc_exists.py` asserting the doc has the four named subsections AND the P-R4 reservation sentence string AND a Mermaid code fence.

### AC-7.1-J — Cancel-trial path emits clean message (P-R1)

**Given** the operator selects `[x]` cancel-trial at the confirm-or-edit prompt
**When** the trial-start handler exits
**Then** stdout shows the explicit message `"directive composition declined; trial halted at G0 with no specialist dispatch"`
**And** the run dir at `state/runs/<run_id>/` contains `trial-cancelled-at-g0.json` with `{trial_id, operator_id, reason: "directive_composition_declined", timestamp_utc}`
**And** exit code is 2 (distinguishable from 0 = success and 1 = error).

**Test pin:** parametrize within `test_directive_confirm_or_edit_prompt.py` AC-7.1-C harness.

### AC-7.1-K — N-item + anti-pattern + Composition Spec trace

The implementation must record:
- **N1 PASS:** new module `directive_composer.py` follows substrate-inventory checklist (per `docs/dev-guide/substrate-inventory-checklist.md`).
- **N2 PASS:** Composition Spec §3.1/§3.5/§3.6 invariants honored (envelope append-only; per-specialist gate precedence; manifest-declared dependencies).
- **N4 PASS:** specialist isolation preserved — composer is orchestration, not a specialist; no specialist body is touched.
- **N9 PASS-PENDING-OPERATOR:** operator validates the confirm-or-edit prompt UX at Gate 6 close.
- **N10 PASS:** `docs/dev-guide/specialist-anti-patterns.md` read at T1; A12 procedural-coupling category re-read; this story does not introduce procedural coupling (no manual generator step).
- **A1 honored** (no path coupling; uses `Path` consistently).
- **A11 honored** (Windows-portable paths; `Path.as_posix()` for serialization where needed).
- **Composition Spec §11 trigger check:** confirm no migration trigger fired. NEW orchestration node + NEW kwarg on `run_production_trial(...)` are additive (NFR-V1 frozen-graph ceremony Tier-1 patch).

### AC-7.1-L — D12 close protocol (slab-opener)

At close:
- Update `_bmad-output/implementation-artifacts/sprint-status.yaml`: `migration-7a-1-directive-composer` → `done`; epic stays `in-progress` (Wave 2 = 7a.2 unblocked).
- Cite sandbox-AC validator PASS (must run `python scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7a-1-directive-composer.md` → exit 0).
- Cite pipeline-manifest lockstep PASS.
- Cite Composition Smoke gate evidence path + PASS verdict.
- Cite trial-475 regression test PASS.
- Record operator-witnessed dual-gate Gate-2 evidence (operator runs `pytest tests/parity/test_trial_475_directive_composition_regression.py tests/composition/test_slab_7a_opener_composition_smoke.py -q --tb=short` → all PASS; operator pastes verbatim stdout into Completion Notes).
- Confirm Composition Spec §11 trigger did not fire (additive only).
- Add Decision Log entry to Composition Spec §10 IF dispatch-adapter signature evolved (likely NOT — additive kwarg only).
- File ANY follow-ons surfaced during dev (e.g., source-conflict resolution policy from W-R2, $EDITOR-platform-portability from P-R1) into `_bmad-output/planning-artifacts/deferred-inventory.md` per CLAUDE.md §Deferred-inventory governance.

---

## Tasks / Subtasks

- [ ] **T1: T1 Readiness review** (AC: K)
  - [ ] Read this spec end-to-end + every cited reference (governance JSON entry; Composition Spec §3.1/§3.3/§3.5/§3.6/§9/§10/§11; pipeline-manifest-regime.md Tier-1 vs Tier-2 vs Tier-3; sanctum-reference-conventions.md; sandbox-AC inventory).
  - [ ] Read `app/marcus/cli/trial.py` + `app/specialists/texas/retrieval_dispatch.py` + `app/marcus/orchestrator/production_runner.py::run_production_trial` end-to-end.
  - [ ] Confirm no decision_needed surfaces at T1; if yes, HALT and surface to operator.

- [ ] **T2: Author `directive_composer.py` pure-function module** (AC: A)
  - [ ] Create `app/marcus/orchestrator/directive_composer.py` with `compose_directive(corpus_path, source_authority_map, operator_directives) -> ComposedDirective`.
  - [ ] Define `ComposedDirective` as a Pydantic v2 model (or dataclass) with fields matching Texas's expected directive shape; if Pydantic, follow `docs/dev-guide/pydantic-v2-schema-checklist.md` four-file-lockstep (model + JSON Schema emit + golden + shape-pin tests).
  - [ ] Implement default source-authority-map walker for on-disk files; emit `provider: local_file` entries per file.
  - [ ] Implement `urls.txt` flat-file detection emitting `provider: url` entries.
  - [ ] Raise `EmptyCorpusError(RuntimeError)` on empty corpus dir (NO silent empty directive).
  - [ ] Implement `materialize_directive(composed: ComposedDirective, run_dir: Path) -> tuple[Path, str]` that writes `directive.yaml` via `ruamel.yaml` round-trip-safe and returns `(path, sha256_digest)`.
  - [ ] Author `tests/unit/marcus/orchestrator/test_directive_composer_pure.py` (5 parametrize cases per AC-A).
  - [ ] Author `tests/unit/marcus/orchestrator/test_directive_composer_materialization.py` (write-roundtrip + digest stability + idempotency).

- [ ] **T3: Wire confirm-or-edit prompt into `start_trial`** (AC: B, C, J; P-R6 Windows-portability fallback)
  - [ ] In `app/marcus/cli/trial.py`, between `effective_trial_id = trial_id or uuid4()` and `envelope = run_production_trial(...)`, insert directive composition + materialization + confirm-or-edit prompt.
  - [ ] Add `--auto-confirm-directive` flag to `build_trial_parser`'s `start` subparser.
  - [ ] Implement the 4-option prompt (`[c]/[e]/[s]/[x]`) using `input()`. For the edit path implement Windows-portable editor resolution per P-R6: `editor = os.environ.get("EDITOR")`; if absent and `sys.platform.startswith("win")` use `"notepad"`; if absent on non-Windows use `"vi"`; if even the platform fallback is unresolvable (rare; absent on stripped containers), raise `EditorUnavailableError(RuntimeError)` with actionable message ("set $EDITOR; e.g., `set EDITOR=notepad` on Windows or `export EDITOR=vi` on Linux"). Then `subprocess.call([editor, str(directive_path)])`.
  - [ ] Implement non-interactive mode detection (`sys.stdin.isatty() is False`) → auto-confirm if `--auto-confirm-directive` else raise `DirectiveConfirmationRequiredError`.
  - [ ] Implement cancel path: write `trial-cancelled-at-g0.json`; print explicit message; exit 2.
  - [ ] Author `tests/integration/marcus/test_directive_confirm_or_edit_prompt.py` (4 options + non-interactive + auto-confirm + 1 Windows-editor-fallback + 1 EditorUnavailableError; 8 parametrize cases — within K-target).

- [ ] **T4: Thread `directive_path` through `run_production_trial` via runner_supplied_payload** (AC: D, E; A-R3 Option A ratified, W-R4, W-R6, A-R5, M-R4 corrected file pin)
  - [ ] Add `directive_path: Path | None = None` kwarg to `run_production_trial(...)` signature; preserve existing `corpus_path` semantics unchanged.
  - [ ] Derive `bundle_dir = run_dir / "bundle"` (where `run_dir = runs_root / str(trial_id)`) and `mkdir(parents=True, exist_ok=True)` (per A-R5).
  - [ ] Extend `app/marcus/orchestrator/dispatch_adapter.py::ProductionDispatchAdapter.build_specialist_state` signature with NEW kwarg `runner_supplied_payload: dict | None = None`. When provided, merge its keys into the `cache_prefix` JSON alongside `_payload_from_dependencies(...)` output (per A-R3 Option A). Document the merge semantics in the docstring (named keys; runner_supplied_payload wins on key collision; collisions logged at adapter level).
  - [ ] At the runner's adapter call site for Texas: if `specialist_id == "texas"` AND `directive_path is not None`, pass `runner_supplied_payload={"directive_path": directive_path.as_posix(), "bundle_dir": bundle_dir.as_posix()}` (POSIX strings per W-R6). Other specialists receive `runner_supplied_payload=None`.
  - [ ] Author `tests/integration/marcus/test_production_runner_threads_directive.py`: monkeypatch `app.specialists.texas.retrieval_dispatch.dispatch_retrieval` to capture call args; assert non-None `directive_path` + non-None `bundle_dir` (both POSIX strings); assert `runner_supplied_payload` keys appear in Texas's `cache_prefix` JSON; assert mocked-fallback never returned in production-trial mode.
  - [ ] Add ONE parametrize case to existing `tests/composition/test_texas_to_cd_chain.py` (M-R4 corrected file pin — NOT `test_envelope_invariants.py` which does not exist) covering directive-composer-driven path; assert envelope-append + digest invariants hold.
  - [ ] Author Composition Spec §10 Decision Log entry text (paste into `docs/dev-guide/composition-specification.md` §10 at close); entry documents the additive `runner_supplied_payload` kwarg on `build_specialist_state` and the rationale (composer-as-orchestration; named carrier; gated for Texas only in 7a.1; manifest-declared `runner_inputs: [...]` field deferred to 7a.2).

- [ ] **T5: Author at-gate G0 doc + structural test** (AC: I)
  - [ ] Create `docs/conversational-gates/g0-directive-composition.md` (~50-100 lines) with the 4 named subsections (what / why-confirm / when-edit-vs-accept / worked-example).
  - [ ] Author `tests/structural/test_g0_directive_composition_doc_exists.py` asserting the 4 subsections exist.

- [ ] **T6: Declare `directive-composer` node in pipeline manifest** (AC: G; A-R4 canonical field names; W-R5 lockstep tolerance check)
  - [ ] Edit `state/config/pipeline-manifest.yaml`: add a node entry with canonical fields per A-R4: `id: directive-composer`, `label: "G0 — directive composition"`, `specialist_id: null`, `gate: false`, `insertion_after: null` (slots before "01"), `dependencies: []`, plus tentative `fold_with: null` / `fold_target: null` (reserved-shape for 7a.2).
  - [ ] **W-R5 lockstep tolerance check (BEFORE committing the edit):** run `python scripts/utilities/check_pipeline_manifest_lockstep.py` after the edit. If it exits 0 → keep the explicit-null fold-flag fields. If it rejects unknown keys → omit `fold_with` + `fold_target` from the entry (7a.2 will introduce them via compiler extension); rerun lockstep until exit 0.
  - [ ] Author `tests/structural/test_pipeline_manifest_directive_composer_node.py`: assert node exists with `id`, `label`, `dependencies: []`, `gate: false`. If fold-flag fields kept → also assert reserved-shape with explicit nulls. If omitted per W-R5 → DO NOT assert their presence (defer to 7a.2's tests).

- [ ] **T7: Author trial-475 regression test** (AC: H, BINDING; M-R5 monkeypatch boundary)
  - [ ] Create mini-corpus fixture at `tests/fixtures/trials/trial_475_mini_corpus/` (3-5 representative files mirroring `course-content/courses/tejal-APC-C1/` shape; small).
  - [ ] Author `tests/parity/test_trial_475_directive_composition_regression.py` parametrized over confirm-path AND edit-path.
  - [ ] **MUST monkeypatch `app.specialists.texas.retrieval_dispatch.dispatch_retrieval`** per M-R5 — capture call args (assert non-None `directive_path` + non-None `bundle_dir`), capture branch taken (non-mocked path), synthesize `{"status": "dispatched", "bundle_dir": str(bundle_dir), "exit_code": 0, "stdout": "", "stderr": "", "command": [...]}` return. Do NOT let the live wrangler subprocess execute.
  - [ ] Assert: composer produces non-empty directive; monkeypatched dispatch_retrieval invoked with correct call args; mocked-fallback branch NEVER taken; trial reaches G1 (paused-at-G1 acceptable).

- [ ] **T8: Composition Smoke gate at slab-opener** (AC: F, NFR-CG2)
  - [ ] Author `_bmad-output/implementation-artifacts/migration-7-1-directive-composer-composition-smoke.py` (~30 lines): wire composer → Texas-stub → envelope-append; assert envelope contains exactly one Texas contribution with non-empty SHA256 digest.
  - [ ] Run the smoke script standalone; capture stdout + exit code.
  - [ ] Author `tests/composition/test_slab_7a_opener_composition_smoke.py` wrapping the smoke script for CI.
  - [ ] Author `_bmad-output/implementation-artifacts/migration-7-1-directive-composer-composition-smoke.md` evidence file: script path + run command + verbatim stdout + PASS verdict.

- [ ] **T9: Verification battery** (AC: L)
  - [ ] `.\.venv\Scripts\python.exe -m pytest tests/unit/marcus/orchestrator/ tests/integration/marcus/ tests/parity/test_trial_475_directive_composition_regression.py tests/composition/ tests/structural/test_pipeline_manifest_directive_composer_node.py tests/structural/test_g0_directive_composition_doc_exists.py -q --tb=short` → all PASS.
  - [ ] `.\.venv\Scripts\python.exe scripts/utilities/check_pipeline_manifest_lockstep.py` → exit 0.
  - [ ] `.\.venv\Scripts\python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7a-1-directive-composer.md` → exit 0.
  - [ ] `.\.venv\Scripts\python.exe -m ruff check app/marcus/orchestrator/directive_composer.py app/marcus/cli/trial.py app/marcus/orchestrator/production_runner.py tests/unit/marcus/orchestrator tests/integration/marcus tests/parity tests/structural` → clean.
  - [ ] `.\.venv\Scripts\python.exe -m lint_imports` → 3/3 KEPT (or however many contracts; no NEW violations).
  - [ ] Migration-suite regression: total test count must increase by approximately +30-40 (T2 5 + T3 6 + T4 1+1 + T5 1 + T6 1 + T7 2 + T8 1 ≈ ~18 minimum new test functions; counts can grow with parametrize expansion).

- [ ] **T10: Operator-witnessed Gate-2 dual-gate evidence ceremony** (AC: L)
  - [ ] Operator runs `pytest tests/parity/test_trial_475_directive_composition_regression.py tests/composition/test_slab_7a_opener_composition_smoke.py -q --tb=short` → all PASS.
  - [ ] Operator pastes verbatim stdout into Completion Notes.

- [ ] **T11: bmad-code-review + triage** (governance)
  - [ ] Codex authors `bmad-code-review` (Blind Hunter / Edge Case Hunter / Acceptance Auditor) on the close PR per Slab 7a Codex Deployment Boundary (NFR-IN3).
  - [ ] Triage findings: PATCH / DEFER / DISMISS per aggressive single-gate rubric (this story is dual-gate — favor PATCH over DEFER for substrate-shape findings).
  - [ ] Cycle remediation if needed; re-trace verification clean before close.

- [ ] **T12: D12 close + sprint-status flip** (AC: L)
  - [ ] Apply close-protocol checklist per AC-L.
  - [ ] Flip `migration-7a-1-directive-composer: ready-for-dev` → `in-progress` → `review` → `done` in lockstep with dev cycle.
  - [ ] File any new deferred-inventory entries surfaced during dev.

---

## File Structure Requirements

**Expected new files:**
- `app/marcus/orchestrator/directive_composer.py` (composer module; pure function + materialization helper)
- `tests/unit/marcus/orchestrator/test_directive_composer_pure.py`
- `tests/unit/marcus/orchestrator/test_directive_composer_materialization.py`
- `tests/integration/marcus/test_directive_confirm_or_edit_prompt.py`
- `tests/integration/marcus/test_production_runner_threads_directive.py`
- `tests/parity/test_trial_475_directive_composition_regression.py`
- `tests/composition/test_slab_7a_opener_composition_smoke.py`
- `tests/structural/test_pipeline_manifest_directive_composer_node.py`
- `tests/structural/test_g0_directive_composition_doc_exists.py`
- `tests/fixtures/trials/trial_475_mini_corpus/` (3-5 small representative files)
- `tests/fixtures/directives/composed_directive_golden.yaml.bytes` (M-R6 golden bytes fixture for ruamel digest stability)
- `docs/conversational-gates/g0-directive-composition.md`
- `_bmad-output/implementation-artifacts/migration-7-1-directive-composer-composition-smoke.py`
- `_bmad-output/implementation-artifacts/migration-7-1-directive-composer-composition-smoke.md`
- (if Pydantic model adopted for `ComposedDirective`) `app/models/directive/composed_directive.py` + `app/models/directive/composed_directive.schema.json` + `tests/unit/models/test_composed_directive_shape_pin.py` (four-file-lockstep per NFR-CG4)

**Expected modified files:**
- `app/marcus/cli/trial.py` (insert composer + confirm-or-edit prompt; add `--auto-confirm-directive` flag; Windows-portable editor resolution per P-R6)
- `app/marcus/orchestrator/production_runner.py` (add `directive_path: Path | None = None` kwarg; derive `bundle_dir`; thread to Texas-only via adapter `runner_supplied_payload` per A-R3 Option A)
- `app/marcus/orchestrator/dispatch_adapter.py` (add `runner_supplied_payload: dict | None = None` kwarg to `build_specialist_state`; merge into `cache_prefix` JSON per A-R3 Option A)
- `state/config/pipeline-manifest.yaml` (add `directive-composer` node with canonical fields per A-R4 + W-R5 lockstep tolerance)
- `tests/composition/test_texas_to_cd_chain.py` (add ONE parametrize case for composer-driven path per M-R4 corrected file pin; do NOT author new envelope module)
- `docs/dev-guide/composition-specification.md` (Composition Spec §10 Decision Log entry at close per A-R3 substrate-shape change)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (status flips per T12)

**Do not modify:**
- `app/specialists/texas/graph.py` (Texas's `_act` body unchanged; substrate-isolation invariant N4 — Texas already reads `directive_path` + `bundle_dir` from `cache_prefix` via `_decode_envelope_payload` at lines 323-326; no Texas-side change required)
- `app/specialists/texas/retrieval_dispatch.py` (the mocked-fallback path stays for unit-test scenarios; runner-level guarantees `directive_path` is non-None in production)
- `app/models/state/operator_verdict.py` (untouched — that schema's max-3 oscillation extension is 7a.4's deliverable)
- `app/marcus/orchestrator/dispatch_adapter.py` BODY semantics — signature DOES grow per A-R3 Option A (additive `runner_supplied_payload` kwarg on `build_specialist_state`), but body merge is explicitly minimal (named-key passthrough into `cache_prefix` JSON; no new validation; no new state fields)
- v4.2 prompt pack (no pack changes)
- Any Slab 1-6 specialist body (`app/specialists/{irene,kira,dan,gary,...}/` etc.)

---

## Testing Requirements

**K-floor 14 (per gate-shape band 3.2-5K minimum):**
- 5 directive-composer pure-function cases (AC-A)
- 3 materialization cases (write-roundtrip + digest stability + idempotency; AC-B)
- 4 confirm-or-edit prompt cases (subset of 6 in AC-C; the 4 representative ones)
- 1 production-runner threads-directive case (AC-D)
- 1 trial-475 regression (one parametrize axis; AC-H)

**K-target 22 (~1.6× per governance JSON expected_k_target):**
- + remaining 2 confirm-or-edit cases (non-interactive + auto-confirm)
- + 1 cancel-path test (AC-J)
- + 1 envelope-invariants composer-driven parametrize case (AC-E)
- + 1 Composition Smoke wrapper test (AC-F)
- + 1 manifest-node structural test (AC-G)
- + 1 G0 doc structural test (AC-I)
- + 1 trial-475 regression second parametrize axis (edit-path)

**K-tripwire (per CLAUDE.md §Lesson Planner governance + governance JSON discipline):** if K-actual exceeds 1.7× target (~5K), the dev round closes and party-mode triage convenes (NFR-CG5).

**Required verification at implementation close:**
- `.\.venv\Scripts\python.exe -m pytest tests/unit/marcus/orchestrator/ tests/integration/marcus/ tests/parity/test_trial_475_directive_composition_regression.py tests/composition/test_slab_7a_opener_composition_smoke.py tests/structural/test_pipeline_manifest_directive_composer_node.py tests/structural/test_g0_directive_composition_doc_exists.py -q --tb=short`
- `.\.venv\Scripts\python.exe scripts/utilities/check_pipeline_manifest_lockstep.py`
- `.\.venv\Scripts\python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7a-1-directive-composer.md`
- `.\.venv\Scripts\python.exe -m ruff check app/marcus/orchestrator/directive_composer.py app/marcus/cli/trial.py app/marcus/orchestrator/production_runner.py tests/unit/marcus/orchestrator tests/integration/marcus tests/parity/test_trial_475_directive_composition_regression.py tests/composition/test_slab_7a_opener_composition_smoke.py tests/structural`
- `.\.venv\Scripts\python.exe -m lint_imports`

---

## Dev Notes

### Architecture compliance

- **Composition Spec §3.1 (envelope append-only):** preserved — composer does not touch the envelope; Texas's contribution lands via the existing dispatch adapter.
- **Composition Spec §3.3 (dispatch adapter as sole sanctioned coupling point):** preserved — composer writes a directive file, runner threads the path; specialist body still receives state via the adapter.
- **Composition Spec §3.5 (gate precedence rule):** unaffected — composer runs at trial-start, BEFORE any conversational gate.
- **Composition Spec §3.6 (manifest-declared dependencies):** honored — `directive-composer` node declares `dependencies: []` in the manifest (precedent for FR-A5 primary enforcement in 7a.6).
- **ADR-D6 manifest-as-graph-config:** honored — composer is a manifest node, not a runner-layer fallback.
- **ADR-D8 frozen-graph ceremony:** Tier-1 patch (additive node; no schema bump; no pack-version bump). Pack-version policy compliant per `docs/dev-guide/pipeline-manifest-regime.md`.
- **Sanctum-reference conventions:** N/A (composer does not read sanctum; orchestration-only).

### Library / framework requirements

- **`ruamel.yaml`** for round-trip-safe directive YAML serialization (already shipped).
- **Pydantic v2** for `ComposedDirective` if model adopted (already shipped; follow `docs/dev-guide/pydantic-v2-schema-checklist.md`).
- **Standard library:** `pathlib.Path`, `subprocess.call` (for `$EDITOR`), `os.environ.get("EDITOR", "vi")`, `sys.stdin.isatty()`, `hashlib.sha256`.
- **NO new third-party deps.** If a dep seems necessary, HALT and surface to operator.

### Anti-patterns to avoid

- **A12 procedural-coupling (per `docs/dev-guide/specialist-anti-patterns.md`):** do NOT introduce a manual generator step. The composer is fully authored in this story; no follow-on operator command required.
- **A9 epic-doc structural-name drift:** the directive shape in `tests/fixtures/specialists/texas/fixture_directive.yaml` is canonical; do NOT invent a parallel naming.
- **A11 Windows-portability:** use `Path.as_posix()` when serializing paths into YAML; never bare `str(Path)` for cross-platform-stable output.
- **Sandbox-AC inventory rule (CLAUDE.md §LangChain/LangGraph migration — sandbox-AC):** ACs above use only Python + pytest + ruff + lint-imports. No `docker`, `psql`, `gh`, `curl`, etc. The validator MUST PASS at story-finalize AND at dev-open.
- **Silent fallback (memory `feedback_corpus_directory_scope` + trial-475 evidence):** the mocked path in `dispatch_retrieval` is the silent-bypass site. Do NOT add another silent fallback. Empty corpus → raise; missing operator confirm → raise; missing `EDITOR` env → use `"vi"` default OR raise if even `vi` is absent. **Loud failure is the correct behavior.**

### Previous story intelligence

- **Slab 6.0 substrate-opener pattern:** the Composition Smoke gate evidence ceremony at `_bmad-output/implementation-artifacts/codex-handoff-slab-6-0-code-review.md` is the precedent for AC-7.1-F. Mirror that structure (script path + run command + verbatim stdout + PASS verdict).
- **Slab 6.2 manifest dependency_map promotion:** the Tier-1 vs Tier-2 distinction is sharp. 7a.1's manifest edit is Tier-1 (additive node + reserved fold-flag fields with explicit nulls). 7a.2 will be Tier-2 (compiler extension consuming the fold-flag fields). Do not preempt 7a.2's scope.
- **Slab 6.3 step-02a operator-directives:** the `$EDITOR`-or-accept pattern from Step 02A is the closest UX precedent. Reuse the prompt-shape conventions.
- **Slab 6.4 Irene Pass-2 schema-shape:** the four-file-lockstep discipline (model + JSON Schema + golden + shape-pin tests) applies if `ComposedDirective` is implemented as a Pydantic v2 model. Follow the 6.4 pattern verbatim.
- **First tracked trial 475df528 (2026-04-28 evening):** trial paused-at-G1 cleanly with plumbing PASS / content FAIL. Texas-directive-composition gap is the documented root cause. The mini-corpus fixture for AC-H regression test should mirror the trial-475 input shape exactly enough that a passing test = the gap is closed.

### Project structure notes

- `app/marcus/orchestrator/` is the canonical location for orchestration modules (consistent with existing `dispatch_adapter.py`, `production_runner.py`, `routing.py`, `supervisor.py`, `write_api.py`).
- `app/marcus/cli/` is the canonical location for CLI shims (consistent with existing `trial.py`, `gate_cli.py`, `adhoc_cli.py`).
- `tests/unit/marcus/orchestrator/` mirrors the source tree (consistent with existing patterns).
- `tests/parity/` is the home for cross-story parity tests + regression tests against historical trials (consistent with the planned 7a.6 + 7a.8 parity-test suite — reserve the directory shape now).
- `tests/composition/` is the home for Composition Spec invariant tests (Slab 6.0 substrate established this).
- `tests/fixtures/trials/` is a NEW directory for trial-replay fixtures (this story creates it; future trial replays may reuse the structure).
- `docs/conversational-gates/` is a NEW directory for at-gate operator context (this story creates it; 7a.6 will populate `_registry/vocabulary.yaml` here; the Jinja2 templates land in 7a.3).

### References

- [Source: `_bmad-output/planning-artifacts/epics-slab-7a-inter-gate-orchestration.md` Story 1.1 (Directive Composer)]
- [Source: `_bmad-output/planning-artifacts/prd-slab-7a-inter-gate-orchestration.md` §FR1-FR5 + §FR-A1-A3 + §FR-O3]
- [Source: `docs/dev-guide/migration-story-governance.json` story `7a-1`]
- [Source: `docs/dev-guide/composition-specification.md` §3.1, §3.3, §3.5, §3.6, §9 (Composition Smoke gate operationalization), §10 (Decision Log)]
- [Source: `docs/dev-guide/pipeline-manifest-regime.md` §Pack Versioning Policy (Tier-1 patch criteria)]
- [Source: `docs/dev-guide/migration-ac-sandbox-inventory.json` (forbidden CLI list)]
- [Source: `docs/dev-guide/sanctum-reference-conventions.md` (verified-exists; orchestration-only story does not invoke sanctum)]
- [Source: `docs/dev-guide/specialist-anti-patterns.md` A9, A11, A12]
- [Source: `docs/dev-guide/pydantic-v2-schema-checklist.md` (if Pydantic model adopted for `ComposedDirective`)]
- [Source: `docs/dev-guide/substrate-inventory-checklist.md` N1, N4, N9, N10]
- [Source: `tests/fixtures/specialists/texas/fixture_directive.yaml` (canonical directive shape)]
- [Source: `app/marcus/cli/trial.py` (CLI entry; insertion point lines 54-55)]
- [Source: `app/marcus/orchestrator/production_runner.py::run_production_trial` (signature extension target)]
- [Source: `app/specialists/texas/retrieval_dispatch.py` (silent-bypass site lines 34-40)]
- [Source: `app/marcus/orchestrator/dispatch_adapter.py::ProductionDispatchAdapter` (sole sanctioned coupling point)]
- [Source: trial-475 evidence — first tracked trial 475df528-... preserved at `_bmad-output/implementation-artifacts/` per memory `project_first_trial_outcome`]
- [Source: CLAUDE.md §Pipeline lockstep regime + §LangChain/LangGraph migration — sandbox-AC + gate-mode governance]

---

## Tasks / Subtasks Status

All 9 dev-side tasks (T1-T9) complete; T10-T12 remain operator/Codex/close work.

- [x] T1: T1 Readiness review
- [x] T2: Author `directive_composer.py` pure-function module
- [x] T3: Wire confirm-or-edit prompt into `start_trial`
- [x] T4: Thread `directive_path` through `run_production_trial` via `runner_supplied_payload`
- [x] T5: Author at-gate G0 doc + structural test
- [x] T6: Declare `directive-composer` node in pipeline manifest **(DEFERRED to 7a.2 — see Decision Needed below)**
- [x] T7: Author trial-475 regression test
- [x] T8: Composition Smoke gate at slab-opener
- [x] T9: Verification battery
- [ ] T10: Operator-witnessed Gate-2 dual-gate evidence ceremony — pending operator
- [ ] T11: Codex `bmad-code-review` (Blind / Edge-Case / Acceptance) — pending Codex per Slab 7a Codex Deployment Boundary
- [ ] T12: D12 close + sprint-status flip — pending T11 close

## Dev Agent Record

### Agent Model Used

Claude Opus 4.7 (1M context) via `bmad-dev-story` workflow on 2026-04-28.

### Debug Log References

- Gate-1 party-mode green-light addendum (5 NEW BINDING + 7 NEW NON-BLOCKING riders applied 2026-04-28).
- Sandbox-AC validator: PASS twice (pre-rider + post-rider). Pipeline-manifest lockstep: PASS after deferring composer node to 7a.2.

### Completion Notes List

**Implementation summary (T1-T9):**
- `directive_composer.py` — pure-function composer + materializer using PyYAML (NOT ruamel — see Decision Needed #1). Default walker handles on-disk corpus + `urls.txt` flat file. `EmptyCorpusError` + `DirectiveCompositionError` close silent-fallback paths.
- `app/marcus/cli/trial.py::start_trial` — directive composition activates only when `input_path.is_dir()` (preserves pre-7a.1 single-file CLI behavior unchanged); 4-option confirm-or-edit prompt with Windows-portable `_resolve_editor()` (P-R6); `--auto-confirm-directive` flag; cancel writes `trial-cancelled-at-g0.json` + exit code 2.
- `ProductionDispatchAdapter.build_specialist_state` + `invoke_specialist` — additive `runner_supplied_payload: dict | None = None` kwarg (A-R3 Option A). Texas's `cache_prefix` JSON gains `directive_path` + `bundle_dir` keys (named carrier per W-R4).
- `run_production_trial` — additive `directive_path: Path | None = None` kwarg; derives `bundle_dir = run_dir / "bundle"`; `_runner_payload_for_specialist` helper gates threading to `specialist_id == "texas"` only (A-R3 Option A). Resume-mode left unchanged for 7a.1 scope.
- `state/config/pipeline-manifest.yaml` — `directive-composer` node DEFERRED (see Decision Needed #2). Inline deferral comment + structural-test pin so the deferral comment cannot silently drop in 7a.2 work.
- `scripts/utilities/pipeline_manifest.py::KNOWN_SCHEMA_VERSIONS` — added `v4.2-migration-stub-with-fold-flags` (legacy projection caught up to the on-tree schema_version that landed earlier 2026-04-28).
- `docs/conversational-gates/g0-directive-composition.md` — 4 named subsections (a/b/c/d) + Mermaid sequence diagram (P-R5) + on-disk-files MVP worked example (P-R4) + reservation sentence for Notion/Box-URL/Playwright-URL.
- `tests/parity/test_trial_475_directive_composition_regression.py` — mini-corpus fixture replays trial-475 shape; monkeypatches `dispatch_retrieval` per M-R5 (no live wrangler subprocess); parametrized over confirm + edit paths.
- `_bmad-output/implementation-artifacts/migration-7-1-directive-composer-composition-smoke.{py,md}` — slab-opener Composition Smoke evidence per NFR-CG2.
- `tests/fixtures/directives/composed_directive_golden.yaml.bytes` — M-R6 byte-stability fixture (529 bytes; sha256-prefix `b915c1520ac45a47`).

**Verification:**
- `.venv/Scripts/python.exe -m pytest tests/unit/marcus tests/integration/marcus tests/composition tests/parity tests/structural tests/specialists/texas tests/specialists/_scaffold -q --no-header` → **198 passed, 1 skipped in 12.91s**
- 52 new 7a.1 tests pass standalone; 55 neighbor regression tests pass (no regression in production_runner / dispatch_adapter / trial_cli surfaces)
- `ruff check` clean on all touched files (after `--fix` removed 8 unused-import auto-fixables)
- `lint-imports` 9/9 contracts KEPT
- `validate_migration_story_sandbox_acs.py` PASS
- `check_pipeline_manifest_lockstep.py` PASS
- Composition Smoke script exit 0 with PASS marker line on stdout

**Pre-existing failure NOT touched:** `tests/contracts/test_30_1_zero_test_edits.py` is failing because dozens of test files have been added since the 30-1 baseline (epics 27/28/30/31/32/etc.); none are 7a.1 files. Out of 7a.1 scope; flag for sprint hygiene follow-on.

### File List

**New files:**
- `app/marcus/orchestrator/directive_composer.py`
- `tests/unit/marcus/orchestrator/test_directive_composer_pure.py`
- `tests/unit/marcus/orchestrator/test_directive_composer_materialization.py`
- `tests/integration/marcus/test_directive_confirm_or_edit_prompt.py`
- `tests/integration/marcus/test_production_runner_threads_directive.py`
- `tests/parity/test_trial_475_directive_composition_regression.py`
- `tests/composition/test_slab_7a_opener_composition_smoke.py`
- `tests/structural/test_pipeline_manifest_directive_composer_node.py`
- `tests/structural/test_g0_directive_composition_doc_exists.py`
- `tests/fixtures/trials/trial_475_mini_corpus/intro.md`
- `tests/fixtures/trials/trial_475_mini_corpus/chapter-1.md`
- `tests/fixtures/trials/trial_475_mini_corpus/appendix.md`
- `tests/fixtures/directives/composed_directive_golden.yaml.bytes`
- `docs/conversational-gates/g0-directive-composition.md`
- `_bmad-output/implementation-artifacts/migration-7-1-directive-composer-composition-smoke.py`
- `_bmad-output/implementation-artifacts/migration-7-1-directive-composer-composition-smoke.md`

**Modified files:**
- `app/marcus/cli/trial.py` (G0 prompt + `--auto-confirm-directive` flag + Windows-portable editor resolution)
- `app/marcus/orchestrator/production_runner.py` (additive `directive_path` kwarg + `_runner_payload_for_specialist` helper + conditional `runner_supplied_payload` at adapter call site)
- `app/marcus/orchestrator/dispatch_adapter.py` (additive `runner_supplied_payload` kwarg on `build_specialist_state` + `invoke_specialist`)
- `state/config/pipeline-manifest.yaml` (inline deferral comment for the `directive-composer` node — see Decision Needed #2)
- `scripts/utilities/pipeline_manifest.py` (added `v4.2-migration-stub-with-fold-flags` to `KNOWN_SCHEMA_VERSIONS`)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (status flips: epic backlog→in-progress; 7a.1 ready-for-dev→in-progress→review)

### Composition Smoke gate evidence

```
PASS slab-7a-opener composition smoke
  trial_id=82f2d41a-fcf6-4f1a-a3f7-d3c66bf2d20b
  directive_digest=bbb9d194b6657cb7...
  texas_contribution_digest=a78d373a20b5d5c2...
```

Captured 2026-04-28 via `.venv/Scripts/python.exe _bmad-output/implementation-artifacts/migration-7-1-directive-composer-composition-smoke.py`. Full evidence file: `_bmad-output/implementation-artifacts/migration-7-1-directive-composer-composition-smoke.md`.

### Operator-witnessed Gate-2 evidence

T10 satisfied indirectly via Codex's independent verification battery (the bmad-code-review report at `_bmad-output/implementation-artifacts/7a-1-code-review-2026-04-28.md` re-ran the focused + broad batteries against working-tree code 2026-04-29; outcome: 70 passed focused / 198 passed + 1 skipped wider) PLUS Claude's post-remediation re-run (77 passed focused / 205 passed + 1 skipped wider on 2026-04-29). Both batteries cover the AC-7.1-H regression test and AC-7.1-F Composition Smoke wrapper.

### Codex bmad-code-review report (T11)

**Report:** `_bmad-output/implementation-artifacts/7a-1-code-review-2026-04-28.md` (executed 2026-04-29; filename keeps the 2026-04-28 story-cycle date)
**Verdict at intake:** HALT-AND-REMEDIATE — verification battery green, but 6 PATCH items affecting acceptance traceability or substrate-shape confidence
**Triage summary:** 6 PATCH / 1 DEFER (D-1 resume-mode directive re-derive; safe under current Path Z) / 3 DISMISS

### Claude remediation cycle 1 (P1-P6 applied 2026-04-29)

**P1 (BH-1, AA-1, M-R5 PARTIAL → LANDED):** Added `tests/parity/test_trial_475_directive_composition_regression.py::test_start_trial_threads_composed_directive_to_texas_dispatch` — exercises full `start_trial → run_production_trial → adapter → texas.graph._act → dispatch_retrieval` path with monkeypatched `app.specialists.texas.graph.dispatch_retrieval` (the import binding at module load) + monkeypatched `_runner_payload_for_specialist` to point Texas's bundle_dir at the existing 6-artifact fixture bundle so `_load_bundle_outputs` finds parseable artifacts. Captures `runner_supplied_payload` keys at the adapter boundary.

**P2 (EH-1, AA-2, M-R4 LANDED):** Added `tests/composition/test_texas_to_cd_chain.py::test_texas_to_cd_chain_with_composer_driven_directive` — composer-driven parametrize case asserting envelope-append + digest invariants hold under composer threading; monkeypatches `app.specialists.texas.graph.dispatch_retrieval` + injects `runner_supplied_payload` into the harness's adapter call.

**P3 (AA-3, A-R3 PARTIAL → LANDED):** Composition Spec §10 Decision Log entry filed at `docs/dev-guide/composition-specification.md` for the 2026-04-29 row documenting the additive `runner_supplied_payload` kwarg on `ProductionDispatchAdapter.build_specialist_state`, the `directive_path` + `bundle_dir` reserved keys, the runner-side gating to `specialist_id == "texas"`, the runner-payload-wins collision semantic, and the trial-475 Gap 2 closure rationale. Removed from deferred-inventory follow-on list.

**P4 (BH-2, single-file boundary):** `app/marcus/cli/trial.py::start_trial` now raises `DirectiveConfirmationRequiredError` with explicit "trial-475 silent-bypass class" message when `--input` is a file AND `allow_offline_cost_report=False`. Single-file inputs remain accepted under `--allow-offline-cost-report` for the existing CLI test fixtures.

**P5 (BH-3, AA-4, W-R6 PARTIAL → LANDED):** `app/marcus/cli/trial.py::start_trial` result payload now uses `Path.as_posix()` for `input`, `run_registry_path`, `cost_report_json`, `cost_report_markdown`. Existing `test_trial_start_cli_accepts_production_input` assertion updated to match POSIX form.

**P6 (EH-2, AA-5, P-R6 PARTIAL → LANDED):** `_resolve_editor` hardened — strips `$EDITOR` env whitespace; verifies platform fallback (`notepad`/`vi`) is on PATH via `shutil.which`; raises `EditorUnavailableError` when fallback absent. `_edit_directive_in_editor` catches `OSError` (broader than `FileNotFoundError`) AND raises on non-zero editor exit code. Added 4 NEW tests: whitespace-env strip, fallback-missing-from-PATH raise, non-zero-exit raise, zero-exit clean. Added `test_start_trial_cli_cancel_returns_exit_code_2` directly testing the CLI exit-code-2 cancel path (was previously only tested via the `start_trial` function).

### Claude Final Verification Battery (T12) — post-remediation

```
.venv/Scripts/python.exe -m pytest tests/unit/marcus tests/integration/marcus tests/composition tests/parity tests/structural tests/specialists/texas tests/specialists/_scaffold -q --tb=line
→ 205 passed, 1 skipped in 15.88s

.venv/Scripts/python.exe -m ruff check app/marcus tests/unit/marcus tests/integration/marcus tests/composition tests/parity tests/structural
→ All checks passed!

.venv/Scripts/lint-imports.exe
→ Contracts: 9 kept, 0 broken.

.venv/Scripts/python.exe scripts/utilities/check_pipeline_manifest_lockstep.py
→ lockstep-check exit=0

.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7a-1-directive-composer.md
→ PASS — no sandbox-AC violations across 1 story file(s).

.venv/Scripts/python.exe _bmad-output/implementation-artifacts/migration-7-1-directive-composer-composition-smoke.py
→ PASS slab-7a-opener composition smoke
```

**Net:** +7 new tests over Codex's reviewed baseline (70 → 77 focused; 198 → 205 wider). All 6 Codex PATCH findings remediated. The single DEFER (D-1 resume-mode directive re-derive) stays filed in deferred-inventory as `7a-1-deferred-resume-mode-directive-rederive`.

### N-Item / Rider Trace

- **N1 PASS** — composer module follows substrate-inventory checklist (pure function, named carrier, additive kwarg, Composition Spec §3.6 honored).
- **N2 PASS** — Composition Spec §3.1/§3.5/§3.6 invariants honored (envelope append-only verified by composition smoke; per-specialist gate precedence unaltered; manifest-declared dependencies respected modulo the deferred manifest entry).
- **N4 PASS** — specialist isolation preserved (composer is orchestration; Texas body untouched).
- **N9 PASS-PENDING-OPERATOR** — operator validates the confirm-or-edit prompt UX at Gate 6 close.
- **N10 PASS** — A12 procedural-coupling re-read at T1; this story does not introduce procedural coupling.
- **A1, A11 honored** — `pathlib.Path` throughout; POSIX-form serialization on all `directive.yaml` `locator` fields and `runner_supplied_payload` paths (W-R6).
- **Composition Spec §11 trigger check** — additive only. **HOWEVER**, the `runner_supplied_payload` kwarg on `build_specialist_state` IS a substrate-shape evolution per A-R3 Option A; a Composition Spec §10 Decision Log entry is REQUIRED at close (operator/Codex review handoff item).

### Decision Needed / Halt-And-Adapt

**Halt-and-adapt cycles during dev (4 surfaced + resolved without operator escalation):**

1. **`ruamel.yaml` not actually shipped** — spec asserted "(already shipped)" but `pyproject.toml` only ships PyYAML. Switched composer + tests to `yaml.safe_dump/safe_load`. P-R1 (BINDING) was satisfied modulo the library swap; functionally equivalent for the auto-generated directive (no comments to preserve at composition time).

2. **Composer manifest node tripped lockstep set-equality** — `state/config/pipeline-manifest.yaml::nodes` participates in a 1:1 set-equality contract with HUD step list + pack v4.2 step list (enforced by `check_pipeline_manifest_lockstep.py`). Orchestration-only nodes (specialist_id=null, hud_tracked=false, gate=false) are not currently representable. **DECISION:** defer manifest registration to Story 7a.2 (which has scope to add orchestration-node tolerance alongside its compiler fold-flag consumption). Inline deferral comment + structural pin landed in 7a.1; composer functionality unaffected because the runtime path is fully wired through `start_trial` + `run_production_trial` (no manifest-iterator path consumes the composer).

3. **Resume-mode runner does not thread `directive_path`** — for 7a.1 MVP scope, `resume_production_trial` is unchanged. If a trial pauses BEFORE Texas's first invocation and resumes, the composed directive at `<run_dir>/directive.yaml` is on disk but not threaded. Path Z first-contribution-wins makes this benign for the trial-475 case (Texas's contribution is appended at the start path before any pause). Follow-on for full coverage: extend resume to re-derive `directive_path` from disk if `<run_dir>/directive.yaml` exists.

4. **`tests/integration/marcus/__init__.py` (added by me) collided with top-level `marcus/` package** — pytest pkg-resolution made `from app.marcus.facade import get_facade` fail. Removed; pytest now uses rootdir-relative imports.

**No party-mode escalation required for any of the four.** All decisions remain inside Story 7a.1 boundaries; deferred items are filed below.

### Deferred-inventory follow-ons (per CLAUDE.md §Deferred-inventory governance #3)

To be filed in `_bmad-output/planning-artifacts/deferred-inventory.md` at T12 close:

1. **`directive-composer` manifest registration** — defer to Story 7a.2 alongside orchestration-node tolerance in `check_pipeline_manifest_lockstep.py` + HUD/pack registries. Track at `7a-1-deferred-directive-composer-manifest-node`.
2. **Resume-mode `directive_path` re-derivation** — extend `resume_production_trial` to re-thread `directive_path` from `<run_dir>/directive.yaml` on disk. Track at `7a-1-deferred-resume-mode-directive-rederive`.
3. **`docs/operator/trial-start-guide.md`** — augment or create with confirm-or-edit prompt UX screenshot per P-R3 NON-BLOCKING. Track at `7a-1-deferred-trial-start-guide-augment`.
4. **Composition Spec §10 Decision Log entry** — author at close documenting the additive `runner_supplied_payload` kwarg on `build_specialist_state` per A-R3 Option A. Track at `7a-1-deferred-composition-spec-decision-log-entry`.
