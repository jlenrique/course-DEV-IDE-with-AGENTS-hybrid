---
id: 42-3
epic: 42
status: ready-for-dev
depends_on: null   # independent; but 42-5 depends on THIS
gate_mode: dual-gate   # operator_surface assembler is block_mode/lockstep
anchor_provenance: HEAD 23480353
lockstep: true   # app/marcus/orchestrator/operator_surface_assembler.py + app/models/runtime/operator_surface.py
---

# Story 42.3: Full run-settings standing readout — all ~16 toggles

Status: ready-for-dev  # green-lit 5/5 2026-07-16; dual-gate; LOCKSTEP (operator_surface assembler)

## Story

As the operator running Marcus-SPOC,
I want the HUD to show ALL ~16 run-defining toggles as a standing readout for the whole run,
so that I can see the exact settings that define this run at a glance — not the thin `modalities` slice (llm_execution_mode + a styleguide string) witnessed tonight, with the other ~14 knobs invisible in env vars and CLI flags.

## Provenance & Dependencies (BINDING)

- **Epic authority:** `epics-operator-surface-next-pass-2026-07-16.md` §42-3 (E42-AC3 completeness, part a — the standing readout).
- **Green-light:** party record P-7 (F splits: 42-3 = deterministic/shape-pinnable standing readout; 42-5 = the pre-walk confirm gate; sequenced, not merged).
- **Requirement:** `evidence/operator-hil-display-requirements-2026-07-16.md` §4 (the 16-toggle table) + `deferred-inventory.md` §Named-But-Not-Filed `hud-pre-run-settings-confirmation-surface` (part a = standing-visible readout; part b = pre-walk confirm → 42-5).
- **Substrate:** extends the Epic-35 operator-surface projection contract (`operator_surface.py` + `operator_surface_assembler.py` are trigger rows → lockstep, party green-light required — satisfied by this record).

## The toggle set (keep in sync when new knobs appear)

| # | Toggle / setting | Source |
|---|---|---|
| 1-3 | Component selection — deck / motion / workbook | `run_summary.component_selection` |
| 4 | Preset (`production`/`explore`/…) | runner / directive |
| 5 | Encounter mode (`recorded`/`live`) | directive |
| 6 | LLM execution mode (`realtime`/`batch`) | run_state |
| 7 | `MARCUS_G0_DISPATCH_LIVE` | env |
| 8 | `MARCUS_RESEARCH_DISPATCH_LIVE` | env |
| 9 | `MARCUS_RESEARCH_DETECTIVE_LIVE` | env |
| 10 | `MARCUS_NARRATION_FIGURE_FIDELITY_ACTIVE` | env |
| 11 | Voice-direction | run config |
| 12 | `MARCUS_DECK_ENRICHMENT_ACTIVE` | env |
| 13 | `MARCUS_UDAC_ACTIVE` | env |
| 14 | Coverage-gate family | config |
| 15 | `MARCUS_TRIAL_BUDGET_USD` | env/runner |
| 16 | Treatment slots A/B (+ styleguide picks when known) | picker / directive |

## T1 Readiness (BINDING readings before any code)

1. **Lockstep gate FIRST:** `docs/dev-guide/pipeline-manifest-regime.md` + the shape-pin contract for `operator_surface.py` (dual pins + §Projection-Demands parity pin per Epic 35); `tests/unit/models/test_operator_surface_shape_pin.py`, `tests/contracts/test_operator_surface_parity.py`. Bumping the schema is governance.
2. `app/models/runtime/operator_surface.py` — `ModalitiesSection` and the operator-surface schema/JSON (`app/models/schemas/operator-surface.v1.schema.json`). A new/extended settings section is a schema change → shape-pin + parity + version discipline.
3. `app/marcus/orchestrator/operator_surface_assembler.py` — `_read_component_selection` (L492), the ambient-sections emission (`_persist_envelope` / L695-765 `modalities` build), the sole-writer contract (assembler is the ONLY writer of the surface).
4. Where each of the 16 settings actually lives at run time (env vars vs run_state vs directive vs runner) — the assembler must collect them at emission WITHOUT reaching outside its sole-writer lane.
5. `app/hud/render/page.py` — where the HUD renders the modalities panel today (the render consumer of the new section).

## Acceptance Criteria

1. **Complete settings section in the operator surface.** The operator-surface schema gains a `run_settings` section (or an expanded `modalities`) carrying ALL 16 toggles with their resolved values at emission, sourced deterministically. Schema version bumped per the lockstep contract; shape-pin + parity pin updated in the same diff (governance-tracked).
2. **Standing readout on the HUD for the whole run.** The HUD renders the full 16-toggle readout as a persistent panel (not a thin slice), visible from launch through every gate to terminal. The panel labels each toggle and shows its resolved value (env-derived values shown as on/off/value, never hidden).
3. **Deterministic + shape-pinned.** The section is a pure projection of resolved run settings (no wall-clock beyond `as_of`); double-emit on identical run state yields an identical section (pinned). Env-absent toggles render an explicit resolved default (e.g. `MARCUS_UDAC_ACTIVE: off`), never a missing key.
4. **Sole-writer + parity preserved.** The assembler remains the sole writer; the new section flows through `_persist_envelope` in BOTH walks (two-walk trap — the readout must be present on start-walk emission AND continuation emission). Parity pin (§Projection-Demands) covers the new section.
5. **Keep-in-sync guard.** A test pins the 16-toggle set against a canonical list so a future new knob that isn't added to the readout fails loudly (the readout can't silently drift behind new settings). New knob → add here in lockstep.
6. **Back-compat.** Existing HUD consumers and the `--hud off` path are unaffected; a run with only the old `modalities` fields (pre-migration frozen surface) still parses (additive, tolerant read).

## Scope Fences (hard NO)

- **NO pre-walk confirm/change gate** — that's 42-5 (this story is READOUT ONLY; display, not a new HIL pause).
- **NO change to how settings are SET** — the readout reflects resolved values; it does not add new ways to configure them.
- **NO schema bump without the shape-pin + parity + version discipline** in the same diff (lockstep governance).
- **NO second writer of the operator surface** — assembler stays sole writer.
- Drift into `production_runner.py` walk logic beyond the assembler emission call is a STOP.

## Lockstep declaration

| Scoped file | Trigger-path entry? | Touched? |
|---|---|---|
| `app/models/runtime/operator_surface.py` | **trigger** | yes (new `run_settings` section + schema) |
| `app/models/schemas/operator-surface.v1.schema.json` | **trigger** | yes (version bump) |
| `app/marcus/orchestrator/operator_surface_assembler.py` | **trigger** | yes (collect + emit the 16 toggles) |
| `tests/unit/models/test_operator_surface_shape_pin.py` | **trigger** | yes (pin update) |
| `tests/contracts/test_operator_surface_parity.py` | **trigger** | yes (parity update) |
| `app/hud/render/page.py` (+ `app/hud/**`) | **trigger glob** | yes (readout panel) |

**Verdict: lockstep regime TRIGGERED — schema bump is governance.** Party green-light (this record) authorizes the operator-surface projection extension. Read `pipeline-manifest-regime.md` at T1; Cora block-mode hook; lockstep checker exit 0 + parity/shape pins green before review.

## Dev Notes

- The assembler collects env-derived toggles at emission through a small deterministic resolver (one place that maps each of the 16 to its resolved value), so the "keep-in-sync" list (AC-5) and the resolver share one source of truth.
- Emit through the SAME `_persist_envelope` path both walks already call, so the readout is present on start-walk and continuation emission without a second seam.
- Tests: extend the operator-surface shape-pin + parity suites (lockstep); `tests/hud/test_settings_readout_panel.py` for the render; a 16-toggle canonical-list pin (AC-5); a determinism double-emit pin (AC-3); a back-compat tolerant-read pin (AC-6).

## References

- `evidence/operator-hil-display-requirements-2026-07-16.md` §4 (toggle table)
- `deferred-inventory.md` §Named-But-Not-Filed `hud-pre-run-settings-confirmation-surface`
- `epics-operator-surface-next-pass-2026-07-16.md` (P-7 split)
- `epics-operator-hud-2026-07-11.md` (Epic 35 projection contract)
- `docs/dev-guide/pipeline-manifest-regime.md`

## Green-Light Round Record (2026-07-16)

**Verdict: 5/5 GREEN** — Amelia forced the F split (P-7: readout is deterministic/pinnable, the confirm gate is a real HIL pause — different risk); Winston bound the schema bump to the shape-pin/parity governance; Murat added the keep-in-sync canonical-list guard; Sally held the "whole-run standing visibility" requirement. Dual-gate (assembler lockstep). 42-5 sequenced after this. Status → ready-for-dev.
