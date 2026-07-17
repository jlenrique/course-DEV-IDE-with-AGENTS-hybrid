---
id: 42-5
epic: 42
status: ready-for-dev
depends_on: 42-3   # needs the full 16-toggle readout to project into the confirm surface
gate_mode: dual-gate   # new HIL pause in the flow of execution + assembler/surface adjacency
anchor_provenance: HEAD 23480353
baseline_commit: 482cf78a  # dev-open baseline 2026-07-17 (post-42-3)
lockstep: true   # start-path HIL pause + operator_surface projection
---

# Story 42.5: Pre-walk settings confirm-or-change gate

Status: done  # 2026-07-17 dev complete (convention-conforming G0S gate) + dual-gate review PASS; LIVE segment-witness owed; wake-policy follow-on filed

## Dev Agent Record

**Dev complete 2026-07-17 (fresh Claude dev agent). Baseline `482cf78a`. Convention-conforming Option A (operator-authorized). Status → review → done (live segment-witness owed).**

### Approach — a real manifest HEAD gate (guide-conforming)
Mirrors the established **G0E/G0R content-free confirm-gate** precedent (marcus-emitted, `specialist_id: null`, pack/HUD-invisible, wake-flag-gated). Convention (`dev-guide.md §Adding a new gate`) satisfied: (1)+(4) real `GSettingsCard` DecisionCard subclass (`app/models/decision_cards/g_settings.py`, gate_id `G0S`) in the discriminated union + shape-pin; (2) manifest HEAD gate node `pre-walk-settings-gate`/`G0S` edge-chained `__start__ → G0S → g0-enrichment-gate`; (3) adapted — no specialist (pre-pipeline), emitted orchestrator/runner-side using the canonical production gate pause → `OperatorVerdict` → `resume_from_verdict` machinery per `gate-decision-binding-semantics.md`.

### File List
- `app/models/decision_cards/g_settings.py` (A) + `__init__.py` (M, union); `state/config/pipeline-manifest.yaml` (M, HEAD gate — pack byte-identical); `app/manifest/compiler.py`, `app/marcus/cli/gate_shims/_shim_parser.py`, `app/models/runtime/production_trial_envelope.py` (M, G0S in the derivation Literals); `app/marcus/orchestrator/production_runner.py` (M, both-walk G0S branch via shared `_prewalk_settings_gate_disposition` + `_pause_at_prewalk_settings` + override projection at `_continue_production_walk` entry); `app/marcus/orchestrator/operator_surface_assembler.py` (M, `run-settings-overrides.json` write-back + `resolve_run_settings` overlay); `docs/conversational-gates/g0s.j2` (A). Tests: `test_pre_walk_settings_gate.py` (A, 15+ incl. the WALK test), `test_g_settings_card_shape.py` (A), `test_marcus_duality_boundary.py`+`test_shim_parser_factory.py` (M, G0S), TW-7c-4 allowlist.

### Completion Notes
- Pre-G0 pause BEFORE any spend; 16-toggle readout (consumes 42-3's `RUN_SETTINGS_TOGGLES`/`resolve_run_settings`); confirm=approve / change=edit (neutral `allowed_verbs`, 42-1 surface); change writes to ONE resolution point (`run-settings-overrides.json`), reflected in the 42-3 readout + projected onto env/directive at every walk entry (re-applied each resume). Opt-out (non-interactive/offline) explicit + traced.
- **Wake-flag:** G0S is operator-woken via `MARCUS_PREWALK_SETTINGS_CONFIRM_ACTIVE` (default OFF → traversed byte-identically), mirroring G0E/G0R. NOT auto-set in `start_trial` (would leak into 13 start_trial test files). → follow-on `g0s-runner-default-wake-policy` filed.

## Senior Developer Review (AI) — 2026-07-17 — DUAL-GATE

**Reviewer:** orchestrator, inline adversarial (hermetic; no windows). **Outcome: APPROVE (live segment-witness owed).**

**Convention conformance:** VERIFIED against `dev-guide.md §Adding a new gate` + `gate-decision-binding-semantics.md` — real DecisionCard subclass + shape-pin; manifest head-gate (the G0E/G0R content-free precedent is the right model for a specialist-less pre-pipeline gate); canonical pause/`OperatorVerdict`/resume (no bespoke pause); reuses 42-3's readout (no duplicate toggle collection); one resolution point (no shadow state); neutral verbs (no preselect).

**Manifest handling:** VERIFIED — baseline manifest was already **51 nodes** (vs the stale hardcoded `test_compiler.py::==45` pin), so the 9 `tests/unit/manifest/` structural-pin failures are **pre-existing** (net-new=0, confirmed by node-count 51→52 vs the 45-pin). 42-5 correctly added G0S to all DYNAMIC derivation Literals, FIXING `test_production_gate_id_literal_stays_in_sync_with_manifest`. The enforced lockstep gate (`check_pipeline_manifest_lockstep.py`) passes exit 0. The stale hardcoded-count pins are pre-existing debt (filed as `manifest-structural-pins-stale-vs-live`), not 42-5's to fix.

**Verification:** 42-5 walk tests + shape-pin **18 passed** (WALK test exercises pause-before-G0 → change → re-present → confirm → walk-observes-new-value); combined touched surface 93 pass/1 skip; HUD/notify/gates 281 pass; lockstep exit 0; ruff clean; import-linter 18/0; TW-7c-4 pass; consumer-wide baseline-diff net-new=0; pack byte-identical. Completeness re-proven after a stash mishap (18 tests pass, all 7 G0S files present).

**Findings:** none blocking. **(1)** wake-policy: G0S default-OFF means the pre-walk surface is NOT shown by default on a real operator run — the operator must export `MARCUS_PREWALK_SETTINGS_CONFIRM_ACTIVE=1`, OR the `g0s-runner-default-wake-policy` follow-on (per-run persisted wake sentinel set by start_trial for operator-steered runs) makes it the default. Operator/party ruling owed. **(2)** stale manifest pins = pre-existing debt, filed. **Owed:** a live segment run (`MARCUS_PREWALK_SETTINGS_CONFIRM_ACTIVE=1` `trial start`) to witness G0S pausing pre-G0 on the HUD + a change round-trip (cheap — pauses before spend; also live-witnesses 42-2's no-window HUD spawn + 42-3's readout render).

## Story

As the operator about to spend money on a run,
I want a pre-walk surface at the BEGINNING of a real run that shows all ~16 run-defining toggles and lets me confirm — or change — them before the walk proceeds,
so that I never discover a wrong setting (wrong preset, detective off, budget mis-set) three gates and several dollars in.

## Provenance & Dependencies (BINDING)

- **Epic authority:** `epics-operator-surface-next-pass-2026-07-16.md` §42-5 (E42-AC3 completeness, part b — the pre-walk confirm-or-change gate).
- **Green-light:** party record P-7 (F splits: this is the HIL pause needing a WALK test; sequenced AFTER 42-3 the deterministic readout).
- **Requirement:** `deferred-inventory.md` §Named-But-Not-Filed `hud-pre-run-settings-confirmation-surface` (part b) — "surfaced at the BEGINNING of a real run as a settings-confirmation surface the operator can confirm or CHANGE before the walk proceeds — a requirement on BOTH the HUD and the app's flow of execution (pre-walk settings pause/card)." Marked RED priority by the operator.
- **Depends on 42-3:** the 16-toggle readout (`run_settings` section) is the content this gate projects; 42-5 adds the PAUSE + confirm/change verbs on top of it.

## Gate convention (BINDING — operator directive 2026-07-17: review guides before adding a gate)

**Operator-authorized approach = CONVENTION-CONFORMING (a real gate, not an ad-hoc pause).** Follow `docs/dev-guide.md §"Adding a new gate (post-M5; rare)"` (≈L1169): (1) a real **DecisionCard subclass in `app/models/decision_cards/`** (settings-gate card carrying the 42-3 16-toggle readout; follow g0*.py + `DecisionCardMeta`); (2) wire into **`pipeline-manifest.yaml`** as a HEAD gate before G0 (`nodes[*].gate_id` + `edges[*].decision_card_schema` — LOCKSTEP; pick a non-colliding gate_id e.g. `G0S`); (3) step-3 adapted — a pre-G0 gate has NO specialist, so it is emitted **orchestrator/marcus-side** (like pre-gate-marcus), documented; (4) **schema-shape story** discipline for the new card (shape-pin per `docs/dev-guide/scaffolds/schema-story/`). PLUS `docs/dev-guide/gate-decision-binding-semantics.md` — pause via `interrupt(...)` with `verdict_verb_options`, resume via `OperatorVerdict`; import `resume_from_verdict` (C3 binding) but don't invoke at node time. Verbs: confirm→approve / change→edit (reuse `DecisionCardVerb`), no bespoke pause.

## T1 Readiness (BINDING readings before any code)

1. **Lockstep gate FIRST:** `docs/dev-guide/pipeline-manifest-regime.md` — this touches the start-path (`production_runner.py`) + `pipeline-manifest.yaml` (the head-gate wiring) + the operator-surface projection; all trigger rows. Cora block-mode hook. **Also read the gate convention above** (`dev-guide.md §Adding a new gate` + `gate-decision-binding-semantics.md`) BEFORE any code.
2. 42-3's `run_settings` section (the readout content) — this gate reprojects it as a confirm surface.
3. The start-path in `production_runner.py` / `app/marcus/cli/trial.py` — where the walk begins, to insert a pre-G0 settings pause that halts the walk until the operator confirms (mirror the existing DecisionCard gate pause/resume mechanics — do NOT invent a new pause primitive).
4. Existing gate/DecisionCard machinery (G0 confirm etc.) — the pre-walk gate reuses the same pause → operator verdict → resume contract (`trial resume --verb …`), presenting `confirm | change` (and the tabular projector from 42-1 for readability).
5. The 16 settings' actual set-points (env vars, CLI flags, directive) — "change" must write back to the effective run config the walk reads, at the ONE place each setting is resolved (no shadow copies).

## Acceptance Criteria

1. **Pre-walk settings pause.** At the beginning of a real run (before G0/the first spend), the walk PAUSES on a settings-confirmation surface showing all 16 toggles (via 42-3's readout) in tabular form (via 42-1's projector). The walk does not proceed until the operator confirms.
2. **Confirm-or-change verbs.** The surface presents `confirm` and `change` neutrally (no preselected verdict — honors 42-1's neutrality). `confirm` proceeds; `change` lets the operator alter a toggle and re-presents the updated readout before proceeding.
3. **Change writes to the ONE resolution point.** A changed setting updates the effective run config the walk actually reads (the single resolution point per setting — no shadow/duplicate state), and the change is reflected in the standing readout (42-3) for the rest of the run. Pin: change budget/preset/a live-toggle → the walk observes the new value.
4. **Reuses the gate pause primitive.** The pre-walk gate uses the existing DecisionCard pause → verdict → resume mechanics (`trial resume --verb confirm|change`), not a new bespoke pause. It persists/rehydrates like any gate (survives a process boundary; both-walk-safe).
5. **Walk test (Murat).** Acceptance is a WALK test: the run halts before G0, the surface carries all 16 toggles, a `change` mutates a setting and the walk proceeds with the new value, a `confirm` proceeds unchanged. Not a snapshot — the pause/resume/change round-trip is exercised.
6. **Opt-out honesty (if any).** If a non-interactive/delegated-HIL mode skips the pause, that is explicit and logged (never a silent skip of a spend-gating confirm) — and the default for an operator-steered real run is PAUSE.

## Scope Fences (hard NO)

- **NO re-implementation of the readout** — consume 42-3's `run_settings` section; do not duplicate the toggle collection.
- **NO new pause primitive** — reuse the DecisionCard gate mechanics.
- **NO change to what the settings MEAN or their defaults** — only add a confirm/change surface over the resolved values.
- **NO preselected verb** (42-1 neutrality applies to this gate too).
- **NO silent spend past an unconfirmed settings surface** in operator-steered mode.
- Drift into other trigger rows beyond the start-path pause insertion + surface projection is a STOP.

## Lockstep declaration

| Scoped file | Trigger-path entry? | Touched? |
|---|---|---|
| `app/marcus/orchestrator/production_runner.py` | **trigger** | yes (pre-G0 settings pause insertion — start path; both-walk-safe) |
| `app/marcus/orchestrator/operator_surface_assembler.py` | **trigger** | possibly (surface the confirm card) |
| `app/marcus/cli/trial.py` | not listed | yes (confirm/change verb handling on resume) |
| `app/hud/**` | **trigger glob** | yes (render the confirm surface on the HUD too) |

**Verdict: lockstep regime TRIGGERED** (start-path + operator surface). Read `pipeline-manifest-regime.md` at T1; Cora block-mode hook; lockstep checker exit 0 before review. Dual-gate (new HIL pause in the spend path).

## Dev Notes

- Model the pre-walk gate as an ordinary DecisionCard gate placed before G0 in the composed walk, with verbs `confirm | change`. The "change" round-trip can re-emit the card with the updated readout (loop until confirm) — keep it within the existing pause/resume envelope so it persists across a process boundary like every other gate.
- Write-back: for each of the 16 settings, thread the change to the single place the walk resolves it (env-derived toggles need a run-config override the walk reads FIRST, not a re-export of process env after start). Document the resolution point per setting.
- Tests: `tests/marcus/orchestrator/test_pre_walk_settings_gate.py` (walk test — pause before G0, all 16 present, change→proceed with new value, confirm→proceed); reuse-of-gate-primitive pin; both-walk persistence pin; neutrality pin (no preselected verb). Coordinate with 42-3's readout fixtures.

## References

- `deferred-inventory.md` §Named-But-Not-Filed `hud-pre-run-settings-confirmation-surface` (part b)
- `evidence/operator-hil-display-requirements-2026-07-16.md` §4
- `epics-operator-surface-next-pass-2026-07-16.md` (P-7 split)
- `_bmad-output/implementation-artifacts/42-3-full-run-settings-standing-readout.md` (the readout this gate projects)
- memory `feedback_operator_run_toggle_requirements`, `feedback_operator_hil_elicitation_cadence` (one question at a time — the change flow honors native-surface in-flow decisions)
- `docs/dev-guide/pipeline-manifest-regime.md`

## Green-Light Round Record (2026-07-16)

**Verdict: 5/5 GREEN** — John bound this by SEQUENCE to 42-3 (readout first, gate second) rather than merging (P-7); Murat required a WALK test (pause/change/confirm round-trip), not a snapshot; Sally kept the operator's "confirm or change before you spend" promise as a shipped pair with 42-3; Amelia flagged the write-back-to-one-resolution-point risk (no shadow state). Dual-gate (new HIL pause in the spend path). Status → ready-for-dev.
