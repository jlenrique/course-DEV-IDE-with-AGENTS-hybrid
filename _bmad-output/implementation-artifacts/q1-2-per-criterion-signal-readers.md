---
baseline_commit: 0fdc442b
---

# Story Q1.2: Per-criterion signal readers (judgment vs computed line)

Status: ready-for-dev

<!-- Epic Q1 (Scorecard Engine + DID Reframe, FOUNDATION). DISPATCH #3 of the binding GL-1 order: Q1.1 (done) → Q1.4a (done) → **Q1.2** → Q1.3 → Q1.5 → Q1.4b. Source epic: _bmad-output/planning-artifacts/epics-project-quality-scorecard-2026-07-19.md. -->

## Story

As **the DID dimension**,
I want **the mechanically-checkable criteria (C2 bone-determinism, C3 fence-enforcement, C4 lock/contract, leak-count) backed by real signal readers, with each such criterion's LEVEL derived from its signal rather than hand-assigned**,
so that **a human cannot hand-score what the code already knows — the score can only move when the underlying reality moves**.

## Scope fence (read FIRST)

Q1.2 builds the **signal readers** and the **signal→level derivation rule**, and wires the *mechanically-derivable* criteria to their signals. It does **NOT**:

- **Reauthor DID prose / enumerated per-node checklists / the C1 re-checkable artifact / the 0.071 correction / Band+leaks+trend reporting** — that is **Q1.5**. Q1.2 changes machine-block *signal* fields + *derived* levels only; it does not rewrite §1.6 prose or the reporting shape.
- **Add the honesty-pin ratchet tests / the GL-6 meta-ratchet** — that is **Q1.3**. Q1.2 ships component tests for the readers + the derivation rule; the RED-first *anti-believed-green pins* are Q1.3.
- **Tag the 5 `did_leak:` entries in deferred-inventory** — that is **Q1.5**. Per **GL-14**, 0 `did_leak:` tags exist today, so the leak-count reader honestly returns 0 and is tested against a **fixture** with seeded tags; it does **not** yet overwrite the hand-carried `open_leaks: 5` (Q1.5 lands the tags, then the count derives).
- **Build the run-summary `fence_state` / projector** — Q1.4a (done) / Q1.4b. Q1.2 *consumes* Q1.4a's honest `silent_bypass_events` for C4; it emits nothing per-run.
- **Import `app.*` at module scope inside `app/quality`** — GL-3 clean-leaf invariant. All `app.*` touches are **deferred local imports** inside reader functions; Q1.1's recursive + module-scope leaf-guard (now covering `app/quality/**`) must stay green.

If you find yourself rewriting §1.6 prose, adding a `did_leak:` tag, writing a ratchet pin test, or adding a module-scope `app.*` import in `app/quality`, **stop — that is a different story.**

## Acceptance Criteria

**AC1 — Signal readers implemented (fail-soft, read-only) in `app/quality/signals.py`.** A new module in the clean-leaf package; **module scope stays stdlib + yaml only**; every `app.*` touch is a deferred local import inside a function. Each reader NEVER raises (returns an honest `{"status": "unavailable", ...}` / sentinel on any failure):
- **C3 — `fences_enabled_signal()`** → `{fidelity: bool, coverage: bool, udac: bool}` answering the **binary "is this fence wired ON under `--preset production`?"** The three gates (`narration_figure_fidelity_active()` in irene.graph, `coverage_gate_active()` in coverage_gate_wiring, `udac_active()` in udac_wiring) are pure env-toggles **default-OFF**, and the production preset does **not** set their env keys → the honest signal today is all-`False`. Deferred-import the three gate fns; determine the default/preset-wired state (a gate is "wired on" only if the production preset actually enables it, which none do today).
- **C2 — `bone_inventory_signal()`** → the deterministic-spine roster: read `state/config/pipeline-manifest.yaml` (**plain YAML, no app import**), count nodes with `model_config_ref: null` in the render/assemble/publish band, and assert no LLM `model_config_ref` appears in the compose/render/publish band — **naming the roster** (which nodes are LLM-free) as the fact.
- **C4 — `lock_contract_signal()`** → digest-binding presence + `silent_bypass_events` (consumes Q1.4a's honest run-summary `fence_state.silent_bypass_events`; `"undetected"` is a first-class value, never coerced to 0).
- **leak-count — `open_leak_count_signal()`** → count of `did_leak:`-tagged **open** entries in `_bmad-output/planning-artifacts/deferred-inventory.md` (plain `.md` read). Honest **0** today (GL-14).

**AC2 — Signal→level derivation + the "no hand-score" rule.** A documented `level_from_signal(criterion_key, signal)` maps each mechanical signal to its 0–4 level per a rubric-encoded rule (e.g. all-three-fences-OFF → C3 `weak`; all-spine-nodes-LLM-free → C2 `strong`, with the Gary export "determinism-pretending-to-be-intelligence" gap tracked as **Leak 3**, not a bone-inventory failure — the bone-inventory checks LLM-freeness, and the Gary matcher is deterministic, so it does not reduce the bone-inventory count; C4 digest-binding present + `silent_bypass_events` honest → `strong`, but `"undetected"` **caps** the top level per GL-8's spirit — the *pin* that enforces the cap is Q1.3, here just ensure the derivation cannot award the clean-uniform level on an unchecked bypass state).
- **Rule (enforced in design + a test):** a criterion that HAS a signal MUST NOT carry a hand-assigned level — its `level` in the machine block equals `level_from_signal(...)`. The human authors **only** C1 (neck-placement — judgment, `signal: null`, its evidence is a re-checkable artifact authored in Q1.5) and the calibration *magnitude* (part of C5/honesty, also Q1.5). C2/C3/C4 become signal-derived here.

**AC3 — Wire the mechanically-derivable criteria in the machine block.** In `docs/quality/project-quality-scorecard.md`'s v2 machine block, populate the `signal` field for C2/C3/C4 from the readers (replacing Q1.1's `signal: null`) and make their `level` the **derived** value. **This must not change the numbers today** — the derivations are defined so C2=`strong`, C3=`weak`, C4=`strong` reproduce the honest hand-carried values (proving the hand-values were already faithful to reality). If a derivation surfaces a genuine discrepancy, that is a real mechanical correction — surface it explicitly in Completion Notes, do **not** silently paper over it. C1 stays `signal: null` (judgment). **leak-count / `open_leaks` stays hand-carried at 5** (GL-14; the reader returns 0 today, wired to override only after Q1.5 tags the leaks) — add a machine-block note recording this transitional state.

**AC4 — Component tests (hermetic + real-repo).** Per the testing doctrine:
- Each reader against a fixture **and** real repo state.
- **Monkeypatch each fence gate on/off → the asserted `fences_enabled` dict matches** (the signal can never drift from the flag — this is the C3 anti-drift guarantee).
- C2 reader against a fixture manifest (seeded LLM-in-spine node → the roster/assertion flips) and the real manifest.
- C4 reader against a fixture run-summary carrying `fence_state.silent_bypass_events` = `"undetected"` / a real int.
- leak-count reader against a **fixture** deferred-inventory with seeded `did_leak:` entries (GL-14) → returns the seeded count; against the real file → 0 today.
- **Derivation-rule test:** `level_from_signal` is total over each criterion's signal domain; and a test asserts the machine-block C2/C3/C4 levels equal `level_from_signal(reader_output)` (the "no hand-score" rule — a hand-edit contradicting the signal is caught). Note: the RED-first *believed-green* pin (bump a level without moving the flag → red) is **Q1.3**; here, assert positive agreement.
- Clean-leaf guard (Q1.1's `test_scorecard_clean_leaf`) stays green over the new `signals.py` (it recursively covers `app/quality/**`; confirm the new module trips it if a module-scope `app.*` import is seeded, then reverted).

## Tasks / Subtasks

- [x] **T1 — Readiness.** Re-read the scope fence + consensus rule #2 (honor the fence: the tool that scores determinism must not itself hand-score what it can compute) + GL-3/GL-6(foreshadow)/GL-14/NFR4. Confirm the pipeline-lockstep regime: this story READS `pipeline-manifest.yaml` but does not modify it or any `block_mode_trigger_paths` code path → regime does not trigger (confirm by inspection).
- [x] **T2 — `app/quality/signals.py`** with the 4 readers (AC1). Deferred local imports for the 3 gate fns; plain yaml/stdlib for manifest + deferred-inventory reads; fail-soft per reader (per-field, per the Q1.4a learning). (AC1)
- [x] **T3 — `level_from_signal` derivation + the no-hand-score rule** (AC2). Document each mapping; make it total; encode the `"undetected"`-doesn't-award-clean-level guard for C4.
- [x] **T4 — Wire C2/C3/C4 signals + derived levels into the machine block** (AC3); keep numbers unchanged; note the leak-count transitional state.
- [x] **T5 — Tests** in `tests/quality/` (AC4): reader matrix (fixture + real), fence monkeypatch anti-drift, manifest fixture, C4 fence_state fixture, leak-count fixture (GL-14), derivation totality + machine-block agreement, clean-leaf still green over signals.py.
- [x] **T6 — Verify.** `pytest tests/quality/ -q`; `ruff`; `lint-imports` (18/0); confirm the DID headline numbers are unchanged in the doc.

## Dev Notes

### Seam facts (verified)
- **Gate fns are pure env-toggles, default OFF** (`app/specialists/irene/graph.py:180` `narration_figure_fidelity_active` reads `MARCUS_NARRATION_FIGURE_FIDELITY_ACTIVE`; `app/marcus/orchestrator/coverage_gate_wiring.py:70` `coverage_gate_active` reads `COVERAGE_GATE_ACTIVE_ENV`; `app/marcus/orchestrator/udac_wiring.py:50` `udac_active` reads `MARCUS_UDAC_ACTIVE_ENV`). The production preset (`app/marcus/cli/trial.py`, `app/marcus/orchestrator/m3_trial.py`, supervisor) does **not** set these env keys (grep-verified) → all three fences are OFF under `--preset production` today → C3 = `weak` honestly.
- **`model_config_ref: null`** appears on the deterministic nodes in `state/config/pipeline-manifest.yaml` (e.g. `:117/:145/:167`). C2's bone-inventory is a plain YAML read of that file — the roster of LLM-free render/assemble/publish nodes.
- **Q1.4a `fence_state.silent_bypass_events`** is the C4 bypass signal — honest `"undetected"` today (no caller sets the detector). C4 must treat `"undetected"` as "not-clean-verified", never as 0.
- **0 `did_leak:` tags** in deferred-inventory today (grep-verified) → leak-count reader returns 0; GL-14 fixture-tests the seeded path; `open_leaks: 5` stays hand-carried until Q1.5 tags.

### GL-3 clean-leaf discipline (the load-bearing constraint)
`app/quality/` must import zero `app.*` at **module scope**. Put every gate-fn call behind a **deferred local import** inside the reader function (the pattern `production_runner._quality_scorecard_ref` used, and the pattern Q1.4a used for the gate reads). Q1.1's `test_scorecard_clean_leaf` is now recursive over `app/quality/**` and exempts function-local imports + `if TYPE_CHECKING:` — so `signals.py` is automatically guarded; do not weaken that test. The manifest + deferred-inventory reads need **no** app import (plain file reads), so only the 3 gate fns are deferred-imported.

### Scope boundary vs Q1.5 (critical — do not over-reach)
Q1.2 wires SIGNALS + DERIVED LEVELS for the mechanical criteria and proves they reproduce today's honest numbers. Q1.5 reauthors the PROSE, adds the enumerated per-node checklists, authors the C1 re-checkable artifact, applies Mary's 0.071 correction, reshapes reporting to Band+leaks+trend, and tags the 5 `did_leak:` entries. If a derivation *cannot* be defined to match today's value without a judgment call, that criterion is not purely mechanical — capture the fact as the `signal` + `evidence_ref` and leave the level to Q1.5's judgment, documenting why (prefer a clean derivation; the epic intends C2/C3/C4 signal-driven).

### Q1.1 + Q1.4a learnings carried forward
- **Per-field fail-soft** (not top-level): each reader degrades independently to an honest marker.
- **`"undetected"`/`"unavailable"` are first-class values** — never coerce to 0/False; a derivation must handle them explicitly (they cannot award a clean level).
- **RED-first the anti-drift assertions** (fence monkeypatch; seeded manifest LLM-node; seeded did_leak fixture).
- **Hold the scope fence exactly** — Q1.1 and Q1.4a both did; the split only works if each story stays in its lane.

### Testing standards
- Hermetic where possible (fixtures in tmp/committed fixture files); real-repo reads for the manifest + deferred-inventory + (clean-env) gate defaults. No live calls; no `--run-live`.
- Reuse `tests/quality/` (Q1.1's dir). Follow the existing fixture-doc pattern.

### References
- [Source: epics-project-quality-scorecard-2026-07-19.md#Story Q1.2] + [#Green-light amendments GL-3/GL-6/GL-14] + consensus rule #2.
- [Source: app/specialists/irene/graph.py:180 · app/marcus/orchestrator/coverage_gate_wiring.py:70 · udac_wiring.py:50] — the 3 gate fns (deferred-import targets).
- [Source: state/config/pipeline-manifest.yaml] — C2 bone-inventory (model_config_ref).
- [Source: docs/quality/project-quality-scorecard.md §1.6 + machine block] — the criteria to wire.
- [Prev stories: q1-1-…(schema/reader/leaf-guard) · q1-4a-…(fence_state.silent_bypass_events C4 consumes)] — both done.
- [Source: app/quality/scorecard.py] — `dimension_ref`/`read_scorecard_block` the signal wiring reads; keep the leaf clean.

## Dev Agent Record

### Agent Model Used

Opus 4.8 (1M context) — fresh BMAD dev agent, RED-first TDD, `bmad-dev-story` workflow.

### Debug Log References

- Baseline (HEAD 0fdc442b): `pytest tests/quality/ -q` → 18 passed; ruff clean; `lint-imports` → 18 kept / 0 broken.
- RED-first: authored `tests/quality/test_signal_readers.py` before `signals.py` → `ModuleNotFoundError: No module named 'app.quality.signals'` (collection RED). Implemented `signals.py` → 38/39 pass; the 1 residual (`test_c2c3c4_signal_fields_populated_in_machine_block`) was the intended pre-AC3 RED (doc `signal: null` not yet wired) → green after the T4 machine-block edit.
- Two seeded-manifest tests initially failed on a `textwrap.dedent` indentation mismatch (4-space fields, not 8) — test-side fix, implementation unchanged.
- **Clean-leaf guard covers `signals.py` (seed+revert proof):** seeded a module-scope `import app.marcus` into `signals.py` → `test_scorecard_clean_leaf` FAILED naming `{'signals.py': ['import app.marcus (line 30)']}`; reverted → PASS. Q1.1's recursive `app/quality/**` guard catches the new module.
- First-pass final: `pytest tests/quality/ -q` → 57 passed; ruff clean; `lint-imports` 18/0.
- **Post code-review honesty REWORK (believed-green kill).** The 3-layer review found the first pass tuned the C2/C4 derivations to REPRODUCE the hand-values — the exact believed-green this story kills. RED-first rework: rewrote `test_signal_readers.py` to the honest semantics first → **24 RED** against the old impl (C2 renamed fields, C4 `undetected`→partial + `unavailable`→unavailable, C3 env-independence, the 8 edge cases, the judgment-with-evidence machine-block shape); reworked `signals.py` → down to 2 RED (the pre-doc-edit machine-block tests); reclassified the doc machine block (added `derivation`; C2/C4 → judgment-with-evidence) → **94 passed**.
- **Clean-leaf guard re-confirmed over the reworked `signals.py` (seed+revert):** seeded a module-scope `import app.marcus` → `test_scorecard_clean_leaf` FAILED naming `{'signals.py': ['import app.marcus (line 44)']}`; reverted → PASS.
- Final: `pytest tests/quality/ -q` → **94 passed**; ruff → All checks passed; `lint-imports` → **18 kept / 0 broken**; `test_run_summary_fence_state.py` → 31 passed (no regression); CLI `--check` → OK. DID headline unchanged (65/B-; strong/strong/weak/strong/partial; open_leaks 5).

### Completion Notes List

**Post-review honesty rework (supersedes the first pass where noted):**
- **The core fix — only C3 is mechanical; C2/C4 are judgment-with-evidence.** The first pass falsely mechanized proxies. Corrected per the governing principle (a level is never mechanically awarded clean/strong from a proxy/unverified/unknown/malformed signal):
  - **REWORK-1 (C4 BLOCKER):** `_level_c4` now returns `partial` for `"undetected"` (cannot confirm clean discipline), `unavailable` for `"unavailable"`/unknown/malformed/non-`(int>=0)`, `weak` if digest absent, `strong` ONLY on a real detector-observed `int == 0`. `digest_binding_present` renamed → **`digest_module_present_on_disk`** and annotated as file-existence only (NOT proof of runtime wiring). C4 reclassified JUDGMENT-with-evidence: machine-block `level: strong` stays (from the §1.6 durable basis — digest-binding + contribution contracts + HIL-before-spend + Epic-41 fail-loud, which do NOT depend on runtime bypass-counting); `level_from_signal` today = **partial**; the undetected runtime-bypass axis is a documented known gap (part of why C4 is 3/4).
  - **REWORK-2 (C2 HIGH×2):** every field renamed to what it measures — `model_config_ref_null_count` / `_null_nodes` / `model_config_ref_set_nodes` / `gates_all_model_config_ref_null` (+ new `model_config_ref_absent_nodes`). C2 reclassified JUDGMENT-with-evidence: the signal carries the config-ref roster fact + an explicit proxy caveat (naming node 08 Irene Pass-2 + Pass-1 gate nodes as LLM-with-null-ref counterexamples); `_level_c2` can only DOWNGRADE (`partial` on an LLM ref on a gate) or return `unavailable` — it NEVER awards strong. `level_from_signal` today = **unavailable**; `level: strong` is the §1.6 architecture judgment. Fixed the old note that overclaimed "49 = the LLM-free spine" → "49/52 carry model_config_ref:null (a determinism PROXY, not proof)".
  - **REWORK-3 (C3 env-independence MED):** `fences_enabled_signal` now reads the gate fns inside a `_production_preset_env()` context that clears the three fence env keys, so a polluted ambient shell (`MARCUS_UDAC_ACTIVE=1` exported) cannot change the reported production-preset posture. Proven by `test_fence_env_pollution_ignored` (env set ON → signal still all-False). Anti-drift now patches the gate FUNCTIONS (the source of truth), which remains env-independent. C3 stays purely mechanical + weak (`derivation: signal-derived`).
  - **REWORK-4 (8 edge cases):** (1) missing `model_config_ref` KEY → `model_config_ref_absent_nodes`, not counted null; (2) truthy-non-`True` `gate` (e.g. `gate: 1`) caught via `bool(...)`; (3) stringified `"3"` → int 3; (4) float `2.0` → int 2 (real count, never floored to undetected); (5) `_level_c4` catch-all → unavailable; (6) `did_leak:` anchored to line-start + fenced code blocks stripped; (7) archive detection matches the EXACT `## Closed Entries …` header, not any `## ` containing the phrase; (8) `run_summary` as a `str` path is coerced to `Path` and read.
- **Anti-believed-green invariant asserted:** `test_no_clean_level_from_degenerate_signal` is parametrized over C2/C3/C4 × 8 degenerate inputs — every unavailable/undetected/unknown/malformed signal maps to a NON-clean level (never strong/uniform); `level_from_signal` is total (never raises).
- **No number was forced to move by honesty.** The DID score/levels are unchanged (65/B-; C1/C2 strong, C3 weak, C4 strong, C5 partial; open_leaks 5). What changed is the JUSTIFICATION label: C2/C4 strong is now explicitly human judgment-with-evidence, not a false mechanical claim. No place where honesty forced a number to move.

**Original first-pass notes (still accurate except where the rework above supersedes the C2/C4 derivation semantics and field names):**

- **AC1 — 4 fail-soft readers in `app/quality/signals.py` (clean leaf).** Module scope is stdlib + `yaml` only; the 3 gate fns are reached by deferred local imports inside `fences_enabled_signal()`; manifest + deferred-inventory reads are plain file reads (no `app` import). Real-repo outputs today:
  - `fences_enabled_signal()` (clean/preset env) → `{fidelity: False, coverage: False, udac: False}` (all default-OFF; `--preset production` sets none of the env keys).
  - `bone_inventory_signal()` → 52 nodes, **49** `model_config_ref: null`, LLM-config roster **{07G vision, 07W.1, 07W.3}**, `gates_all_deterministic=True`.
  - `lock_contract_signal()` → `digest_binding_present=True` (`app/runtime/compiled_graph_digest.py` exists), `silent_bypass_events="undetected"` (no run observed; consumes Q1.4a `run_summary.fence_state.silent_bypass_events` when a run-summary dict/path is passed; never coerced to 0).
  - `open_leak_count_signal()` → **0** today (GL-14; 0 `did_leak:` tags in deferred-inventory). Archived-section tags are excluded (open entries only).
- **AC2 — `level_from_signal` derivation ("no hand-score").** Total over each mechanical criterion's signal domain; judgment criteria (C1/C5) return `None`. Mapping:
  - **C3 (fence_enforcement_default_on):** 0/3 ON → `weak`; 1–2 → `partial`; 3 → `strong`; any non-`bool` fence value → `unavailable`. (Today 0/3 → **weak**.)
  - **C2 (bone_determinism):** `gates_all_deterministic` False → `partial`; else deterministic spine present → `strong` (capped — `uniform` needs Leak-3 closed, a judgment the bone-inventory cannot certify). (Today → **strong**.)
  - **C4 (lock_and_contract_discipline):** digest absent → `weak`; present + `silent_bypass_events` int > 0 → `partial`; present + (0 | `"undetected"` | `"unavailable"`) → `strong` (capped — an unverified/undetected bypass state can NEVER award a clean/uniform level; GL-8 pin is Q1.3). (Today → **strong**.)
  - No mechanical derivation ever returns `uniform` (proven by `test_no_mechanical_derivation_awards_uniform`).
- **AC3 — machine block wired; numbers unchanged.** C2/C3/C4 `signal: null` → structured `{reader, derived_level, note}`; their `level` is the signal-derived value and reproduces the hand-carried **strong/weak/strong** (proving the hand values were already faithful). C1 stays `signal: null` (judgment). `open_leaks: 5` stays hand-carried with a machine-block transitional note (GL-14). Headline unchanged: `did_score_ref()` → score 65 / max 100 / band B-. `test_machine_block_levels_equal_derived` pins level == `level_from_signal(reader())` for C2/C3/C4.
- **Genuine finding surfaced (does NOT change the score):** `model_config_ref` is a **declarative config pointer, not a runtime-LLM flag.** Irene Pass-2 (node `08`) uses an LLM yet carries `model_config_ref: null`; the workbook writer seams `07W.1`/`07W.3` carry a writer `model_config_ref` while being *deterministic stubs* today (per their manifest rationale); the real workbook producer `07W` is `null` ("deterministic, NO LLM"). Therefore the bone-inventory names config-pointer nodes and its honest ceiling for C2 is `strong`, never `uniform`. This is recorded in the `bone_inventory_signal` `note`, the machine-block C2 `signal.note`, and does not alter C2=strong=3/4.
- **Scope fence held.** No §1.6 prose reauthor; no `did_leak:` tag added (GL-14 — fixture-tested only); no ratchet/GL-6 meta-ratchet pin (Q1.3); no run_summary/fence_state emission change (Q1.4a); no module-scope `app.*` in `app/quality`; `open_leaks` left at 5 (Q1.5 tags then derives). No scope-fence temptations acted on.
- **Status left `ready-for-dev` and NOT committed**, per the dispatch instruction (overrides the workflow's auto-`review` + sprint-status update).

### File List

- `app/quality/signals.py` (new) — 4 fail-soft signal readers + `level_from_signal` derivation (clean leaf; deferred gate imports).
- `tests/quality/test_signal_readers.py` (new) — reader matrix (fixture + real), fence anti-drift monkeypatch, seeded-manifest, C4 run-summary fixture, seeded `did_leak` fixture, derivation totality + machine-block agreement.
- `docs/quality/project-quality-scorecard.md` (modified) — machine block: C2/C3/C4 `signal` populated + signal-derived `level` (numbers unchanged); leak-count transitional note; updated block-comment.
