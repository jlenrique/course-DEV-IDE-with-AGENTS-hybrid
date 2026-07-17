# Story 43-1 — G0 directive source-inventory table (kill the raw dump)

**Epic:** 43 · **Slab:** 1 · **Status:** ready-for-dev
**Dispatch position:** after 43-2 (registry) + 43-10 (allowlist). This is the FIRST allowlist→registry move.
**Gate mode:** dual-gate (touches the G0 confirm path — the operator's first-felt surface — and the projector registry).

## Story

As the **operator**, at the **G0 directive confirm** — the very first review surface of every trial — I want the composed directive shown as a **scannable source-inventory table** instead of a raw YAML dump, so I can actually review the material partition (which sources, what roles, what floors) before I confirm. Raw YAML stays one keystroke away via `[e]dit`.

This is the surface that cost a paid trial's trust (run `5169a872`, 2026-07-17). It is `trial.py:364` `_confirm_or_edit_directive` doing `print_fn(directive_path.read_text())`.

## T1 required readings

- `_bmad-output/planning-artifacts/epic-43-hil-surface-tabular-coverage.md` — §3 (the 3 pins), §4b riders (R5 raw-access, R7 additive).
- `app/marcus/cli/trial.py` — `_confirm_or_edit_directive` (:333–377) and `_g0_prompt_text` (:226–237). The `c/e/s/x` loop + the pure-IO seam (`input_fn`/`edit_fn`/`isatty_fn`/`print_fn`) you MUST preserve.
- `app/marcus/cli/hil_tabular_projector.py` — the 43-2 registry (`register_renderer`, `render_gate_content`, `_md_table`, `_truncate_cell`) and 43-10's `GATE_CONTENT_TYPES` + `KNOWN_UNRENDERED_ALLOWLIST`. Study `render_generic_gate_content` as the pattern for a bespoke renderer.
- Fixtures: `tests/fixtures/hil_projector/directive-5169a872.yaml` (14 sources: 12 primary / 2 supporting / 0 excluded) and `directive-bc747b51.yaml`. Your replay inputs (zero spend).

## Operator-approved table shape (BINDING — do not redesign)

```
G0 — Directive review   run <run_id> · corpus <corpus-basename>
Variants:  A <styleguide-A> · B <styleguide-B>

| ref     | role       | locator                            | min-words | excl | description        |
| src-003 | primary    | slides/slide-1-welcome-on-camera.md|        80 | —    | Welcome/on-camera… |
| …       | …          | …                                  |         … | …    | …                  |
| src-001 | supporting | assessments/chapter-1-knowledge-…  |       300 | —    | Chapter 1 Knowled… |

14 sources · 12 primary · 2 supporting · 0 excluded
```

- Columns: `ref_id · role · locator · expected_min_words · excluded · description(truncated brief)`.
- **Sorted primary-first** (role=primary before supporting; stable/lexical within a role).
- Header line: `run_id · corpus` (corpus_dir basename) `· gamma variants` (A/B styleguide slugs from `gamma_settings`).
- Counts footer: `N sources · P primary · S supporting · X excluded`.
- Description column is truncated brief + **fixed-width** (reuse `_truncate_cell`, rider R5) — no ugly wrap at 80 cols.

## Acceptance criteria

**AC-1 — Bespoke directive renderer (pin 2), registered.** A `render_directive_sources(content, *, title, page_size)` in `hil_tabular_projector.py`, **registered under `content_type="directive"`** via `register_renderer`. Produces the operator-approved shape above from a directive mapping (`sources[]` + `run_id`/`corpus_dir`/`gamma_settings`). Reuses `_md_table` + `_truncate_cell`. Projector stays **stdlib-pure** — it receives an already-parsed mapping; no `yaml` import in the projector.

**AC-2 — Kill the raw dump (pin 1), table is the default.** `trial.py::_confirm_or_edit_directive` STOPS `print_fn(directive_path.read_text())`. Instead it loads the directive (`yaml.safe_load` — yaml import lives in trial.py, which already imports yaml) and prints `render_gate_content(directive_dict, content_type="directive")`. The table is the default view at G0.

**AC-3 — Raw stays available (pin 1 / rider R5), `c/e/s/x` preserved.** The `[e]dit` path still opens the raw `directive.yaml` in the editor (raw one keystroke away). The `c/e/s/x` contract and the pure-IO seam are preserved exactly. `_g0_prompt_text` mentions that `[e]dit` shows/edits the raw YAML.

**AC-4 — First allowlist→registry move (pin 3 / 43-10).** Remove `"directive"` from `KNOWN_UNRENDERED_ALLOWLIST`. The 43-10 disjoint invariant (`registered ∩ allowlist == ∅`) now REQUIRES this — the coverage ratchet stays green with `directive` registered, not waived. Run 43-10's test to prove it.

**AC-5 — Names the surface (pin 3).** At least one AC/test **names "G0 directive composition"** so a G0E-only replay corpus can never re-close it.

**AC-6 — Replay tests (zero spend).** Against `directive-5169a872.yaml`: the rendered table carries the header (run_id + corpus + A/B variants), **primary-first order**, all 14 `ref_id`s, the description column truncated, and the `14 sources · 12 primary · 2 supporting · 0 excluded` footer; and assert the raw-`read_text` dump is GONE from the confirm path. Assert `c/e/s/x` still routes (confirm/edit/save/cancel) via injected `input_fn`/`print_fn`. Repeat header/footer assertions on `directive-bc747b51.yaml`.

## Constraints

- Pure-render + one CLI wiring change. Additive-within-v1 (rider R7). Projector stdlib-pure.
- ruff + import-linter clean. Confirm no manifest touch.
- Run ONLY touched test files. Do NOT commit or stash — leave the tree for orchestrator review (the orchestrator will render the real table for an operator witness before marking done).

## Definition of done

`directive` renderer registered + producing the approved table; the G0 raw dump gone (table default, raw via `[e]dit`); `c/e/s/x` intact; `directive` moved allowlist→registry with 43-10 green; replay tests green; ruff/import-linter clean; ready for orchestrator review + operator witness, then `bmad-code-review` (dual-gate).
