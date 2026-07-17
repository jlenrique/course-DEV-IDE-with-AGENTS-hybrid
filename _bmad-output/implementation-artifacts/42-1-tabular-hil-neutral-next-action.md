---
id: 42-1
epic: 42
status: ready-for-dev
depends_on: null   # independent; can open first in Epic 42
gate_mode: single-gate
anchor_provenance: HEAD 23480353
baseline_commit: 72a15de5  # dev-open baseline 2026-07-17 (post-42-2)
---

# Story 42.1: Tabular HIL projection + neutral next-action verb

Status: done  # 2026-07-17 dev complete (fresh Claude dev agent) + review PASS; single-gate; replayed vs real bc747b51 artifacts (64/12/14)

## Dev Agent Record

**Dev complete 2026-07-17 (fresh Claude dev agent). Baseline `72a15de5`. Status → review → done.**

### File List
- `app/marcus/cli/hil_tabular_projector.py` (A) — pure stdlib module: `render_hil_tables` + section renderers (gate identity / enrichment metrics / one-row-per-ungrounded-flag w/ "advisory (speaker notes) — adjudicate at G0E" caption / one-row-per-LO); `build_gate_surface` + `emit_gate_surface` (thin CLI printer); pagination `PAGE_SIZE=15` (Marcus HIL Display Standards).
- `app/marcus/cli/next_action.py` (M) — `_read_card_fields` now returns `(card_id, digest, allowed_verbs)` threaded from the card (default canonical `approve|edit|reject`); `_render_neutral_gate_next_action` emits one `trial resume … --verb <v>` line per allowed verb, no preselection, card-id+digest on every line, "Marcus proposes; you decide" header. No `--verb approve` hardcode.
- `app/marcus/cli/trial.py` (M) — `_emit_gate_surface_if_paused()` routes both gate-print paths through the projector on **stderr** (stdout stays dense machine JSON → `json.loads` consumers untouched); best-effort try/except; AC-6 handoff cue (PowerShell context + "don't type c/approve").
- `tests/marcus/cli/test_hil_tabular_projector.py` (A), `tests/marcus/cli/test_next_action_neutral_verb.py` (A), `tests/marcus/cli/fixtures/g0-enrichment.trimmed.json` (A), `tests/unit/marcus/cli/test_next_action.py` (M — round-trips adapted to per-verb line), `tests/audit/…tw_7c_4…` (M — allowlist).

### Completion Notes
- **Authentic replay:** against the frozen `bc747b51/g0-enrichment.json` — **64 typed / 12 ungrounded advisories (all narration speaker-notes) / 14 provisional LOs**, pinned vs `reconcile.n_ungrounded=12`; neutral next-action replayed vs real `decision-card-G0R.json` (real card-id `5eb79d3e…` + digest `f697a34c…`, presents approve|edit|reject). Committed trimmed portable fixture (skip-if-absent).
- Machine JSON on disk / `NextActionSection.command` shape unchanged; verdict still advances only via `trial resume --verb <chosen>`.

### Change Log
- 2026-07-17: tabular HIL projector (stderr) + neutral next-action verb; replay vs real bc747b51 (64/12/14); done.

## Senior Developer Review (AI) — 2026-07-17

**Reviewer:** orchestrator, inline (hermetic story, no windows). **Outcome: APPROVE.**

**Correctness:** neutral-verb fix verified — no `--verb approve` hardcode remains; allowed-verb set threaded from the card with a canonical default; presentation order ≠ preference. Projector is a pure function (testable, no side effects); the one IO seam (`emit_gate_surface`) routes to stderr so stdout machine JSON is preserved — clean separation, which is why integration `json.loads(out)` consumers are unbroken (baseline-diff net-new=0). AC-6 handoff cue directly fixes the witnessed `c`-at-PowerShell gotcha.

**Verification:** 27 new tests + adapted next_action round-trips pass; ruff clean; diff scope = `next_action.py` + `trial.py` + new projector/tests/fixture — **zero trigger-path files, no operator_surface/assembler/HUD** (projector stayed CLI-side per fence); import-linter 18/0; TW-7c-4 pass; real-data replay pins 64/12/14.

**Findings:** none. The stderr routing is a good call (operator sees tables; machine JSON stays pipeable).

## Story

As the operator reviewing a gate during a live paid run,
I want every HIL review surface projected into tables/containers, and the "what do I do next" surface to NOT preselect a verdict,
so that I can actually read the material and decide — instead of scrolling a YAML blob, decoding `NOT grounded` log sheaves, and being nudged toward Approve by a pre-filled `--verb approve` command.

## Provenance & Dependencies (BINDING)

- **Epic authority:** `epics-operator-surface-next-pass-2026-07-16.md` §42-1 (E42-AC1).
- **Green-light:** party record P-4 (C+G are the same trust violation on the same object — merge), P-5 (replay vs the real 64-component `bc747b51` enrichment, not toy fixtures).
- **Requirement capture:** `evidence/operator-hil-display-requirements-2026-07-16.md` §1 (tabular HIL, with the worked exemplar tables) + §5 (next_action must not preselect approve; code pin `next_action.py::build_next_action` L75 `" --verb approve"`).
- **Inventory rows filed as this story:** `hil-operator-surfaces-must-be-tabular`, `next-action-must-not-preselect-approve`.

## T1 Readiness (BINDING readings before any code)

1. `evidence/operator-hil-display-requirements-2026-07-16.md` §1 exemplars (gate identity table, enrichment-metrics table, one-row-per-flag advisory table, one-row-per-LO table) — these ARE the target output shapes; §5 (do/don't table for the verb).
2. `app/marcus/cli/next_action.py` — `build_next_action` (L58), the `" --verb approve"` interpolation (L75). Understand the DecisionCard verb contract per gate (G0R = `approve | edit | reject`).
3. The CLI gate-print path — where `trial start`/`trial resume` emit the gate summary / enrichment advisories / decision-card prompt to the terminal (locate the printer(s); the anti-pattern was a JSON blob + `NOT grounded` log lines).
4. Frozen `bc747b51` artifacts as the replay corpus: `g0-enrichment.json` (64 typed components, 12 ungrounded advisories, provisional LOs), `operator-surface.json`, `decision-card-G0E.json`/`decision-card-G0R.json`.
5. Marcus HIL Display Standards (pagination >~15 rows) — cite the source; if none exists, this story establishes it as a small shared projector contract.

## Acceptance Criteria

1. **Tabular gate projector.** A shared projector renders operator-facing HIL surfaces as tables/containers: (a) gate identity (trial / status / gate / ask); (b) enrichment summary metrics (typed components, ungrounded-advisory count, provisional-LO count); (c) ungrounded advisories as **one row per flag** (#, component_id, parent, kind); (d) provisional/ratified LOs as **one row per LO** (#, statement). Machine JSON on disk stays dense; only the operator-facing DISPLAY projects to tables. Paginate at >~15 rows per the Display Standards.
2. **Replay against the real trial (P-5).** The projector is exercised against the frozen `bc747b51` `g0-enrichment.json` (64 components) + `operator-surface.json` and produces reviewable tables without truncation-to-illegibility — the acceptance fixture IS the real trial artifact, not a toy. Pin the row counts (64 typed / 12 advisory / N LOs) against the frozen file.
3. **Enrichment advisories are tabular, not a log sheaf.** The post-G0 `... NOT grounded ...` advisory output renders as the one-row-per-flag table (AC-1c) with an explicit "advisory (speaker notes) — adjudicate at G0E" caption, never as free-scroll log lines.
4. **Neutral next-action (G).** `build_next_action` no longer hardcodes `--verb approve`. For a `paused-at-gate` it emits a NEUTRAL next-step surface: the allowed verbs for that gate (from the DecisionCard contract) presented without bias, with a per-verb paste line (`trial resume … --verb approve|edit|reject`) or placeholder — the concrete command is completed only after the operator picks. The card id + digest remain available for whichever verb is chosen. **Never** ship one approve-prefilled command as THE next action.
5. **No verdict implied anywhere.** Neither the projector nor `next_action` text implies Marcus/HUD has decided; copy honors "Marcus proposes; you decide." A test asserts no operator-facing next-action string contains a single pre-selected `--verb <x>` as the sole option for a multi-verb gate.
6. **Handoff-cue fix (advisory).** Where the CLI returns to the shell after emitting a gate surface, the surface states the shell context and the exact resume affordance (so the operator doesn't type `c`/`approve` at PowerShell). This is copy on the tabular surface, not a shell change.

## Scope Fences (hard NO)

- **NO change to gate SEMANTICS / verdict flow** — only how surfaces are DISPLAYED and how the next-action is phrased. The verdict still advances only via `trial resume --verb <chosen>`.
- **NO change to machine JSON on disk** (`decision-card-*.json`, `operator-surface.json` shape) — display-layer only. (If a shared projector wants a typed model, it reads existing artifacts; it does not mutate the emitted contract — that would be a lockstep concern for 42-3.)
- **NO "fix by documentation"** for G — do not merely note that approve is a template; the emitted command must not preselect.
- **NO HUD card redesign** — HUD decision-card rendering is Epic-35 substrate; if the same projector is reused by the HUD, that reuse must not alter `operator_surface` shape (defer any assembler change to 42-3).

## Lockstep declaration

| Scoped file | Trigger-path entry? | Touched? |
|---|---|---|
| `app/marcus/cli/next_action.py` | not listed | yes (neutral verb surface) |
| CLI gate-print module(s) | not listed | yes (tabular projector) |
| `app/hud/render/*` | **`app/hud/**` trigger** | **NO this pass** (projector is CLI-side; HUD reuse deferred to avoid lockstep) |
| `app/marcus/orchestrator/operator_surface_assembler.py` | **trigger** | **NO** (42-3) |

**Verdict: keep the projector CLI-side ⇒ zero trigger paths touched.** If dev finds the projector MUST live where the HUD reuses it (trigger glob), STOP and re-scope with the party (lockstep).

## Dev Notes

- Build the projector as a pure function `render_hil_tables(surface_dict) -> str` (markdown tables) with a thin CLI printer — reusable, testable against the frozen artifacts, no side effects.
- For G, thread the gate's allowed-verb set from the DecisionCard rather than assuming `approve|edit|reject` universally (some gates differ, e.g. G0 confirm).
- Tests: `tests/marcus/cli/test_hil_tabular_projector.py` + `tests/marcus/cli/test_next_action_neutral_verb.py` — replay vs `state/config/runs/bc747b51-…/{g0-enrichment.json,operator-surface.json,decision-card-G0R.json}` (skip-if-absent + a committed trimmed fixture); row-count pins; no-preselected-verb pin.

## References

- `evidence/operator-hil-display-requirements-2026-07-16.md` §1 + §5
- `epics-operator-surface-next-pass-2026-07-16.md`
- `party-greenlight-post-trial-bc747b51-arc-2026-07-16.md` (P-4, P-5)
- `state/config/runs/bc747b51-7009-4742-9f65-8de6abc29ca4/`

## Green-Light Round Record (2026-07-16)

**Verdict: 5/5 GREEN** — Sally led (the operator's underlined ask); Amelia/Winston pushed the C+G merge rationale (illegible-and-leading is one surface); Murat bound acceptance to the real 64-component artifact (P-5). Folded: P-4 (merge C+G), P-5 (real-artifact replay), the "no fix-by-doc" fence, the handoff-cue copy. Status → ready-for-dev.
