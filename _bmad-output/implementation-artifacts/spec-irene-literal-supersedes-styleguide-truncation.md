---
title: 'Irene literal-text supersedes styleguide truncation'
type: 'feature'
created: '2026-07-09'
status: 'done'
baseline_commit: 'c6871da057934bc54f559466817cf1656849c699'
context:
  - '{project-root}/_bmad-output/planning-artifacts/deferred-inventory.md'
  - '{project-root}/_bmad-output/implementation-artifacts/s8-close-letter-claim-envelope-2026-07-08.md'
  - '{project-root}/goal-irene-literal-preserve-2026-07-09.txt'
---

<!-- Party green-light 2026-07-09 (skill-activated BMAD seats):
     John / Winston / Amelia / Murat = 4/4 GO-WITH-AMENDMENTS.
     MUST amendments folded below. Impasse chain: Quinn first, then John.
     Prior generalPurpose-only round VOIDED per operator. -->

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** When Irene tags a slide `fidelity: literal-text` (or `literal-visual`), the Marcus-SPOC Gary path still applies the run styleguide's deck-level `text_mode` / `amount`, so a classic `condense` + Minimal guide can silently shorten teaching-critical copy (S8 Part-4 Irene figure-contradiction).

**Approach:** Carry per-slide `fidelity` from the lesson-plan package into Gary slides; for the **literal cohort** (`literal-text` ∪ `literal-visual`), force Gamma `text_mode=preserve` and omit condensing `text_options.amount` (key absent, not null); split the deck into separate Gamma calls when creative and literal slides coexist (binary cohorts this slice — not three legacy fidelity calls). Never mutate approved styleguide registry records.

## Boundaries & Constraints

**Always:**
- Contract field: slide/plan-unit key `fidelity` with values `creative` | `literal-text` | `literal-visual` (missing/unknown → creative cohort).
- Binary cohorts this slice: creative vs literal (`literal-text` and `literal-visual` share one preserve call).
- Literal cohort → Gary API `text_mode=preserve`; condensing `amount` key **absent** on that call (strip amount only — leave tone/audience/language unless proven to reflow).
- Each Gamma call receives **cohort-scoped** `_input_text` + `num_cards=len(cohort)` (never full-deck prompt with split kwargs).
- Creative / untagged cohort still honors the selected styleguide `text_mode`/`amount` (no whole-deck preserve bleed).
- Production seam is mandatory DoD: `build_gary_briefs` + `generate_gamma_variants`. Legacy `generate_deck_mixed_fidelity` is reference only.
- If `fidelity` is literal but the dispatch path cannot honor preserve → **fail loud** (raise), never silent fallback to condense. Concrete in-scope case: any literal slide + variant `production_mode=studio` → raise (Studio remains out of behavior change).
- Intra-call export binding stays today’s title-matcher; **inter-cohort** reassembly is by brief order / stable `slide_id` only.
- Named styleguide variants only — never ad-hoc-edit approved guides.
- Product goal remains Marcus-SPOC runtime correctness (not proofing convenience).
- Claim envelope: this closes styleguide-condense-overrides-Irene-literal. It does **not** close `fidelity-L1-per-slide-text-mode` broadly. Inventory MET language must leave L1 yellow/open with residual note.

**Ask First:**
- Extending `PlanUnit` Pydantic schema with a formal `fidelity` field (dict path is enough this slice).
- Changing Studio (`production_mode=studio`) path behavior beyond fail-loud when literal is present.
- Retiring vs keeping the `hil-2026-apc-crossroads-classic-preserve` sibling after land (one disposition sentence at close).

**Never:**
- Mutate `state/config/gamma-style-guides.yaml` approved records in place.
- Silent whole-deck preserve as the durable fix.
- Claim “L1-per-slide text_mode closed” in closeout/PR/inventory MET prose.
- Langsmith receipt work, workbook prose uplift, or flag-retirement in this slice.
- Image URL injection for `literal-visual` (text preserve only this slice).
- Empty `text_options` wholesale on literal (amount-only strip).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Carry-through | Plan unit has `fidelity: literal-text` | `build_gary_briefs` slide row includes `fidelity: literal-text` | Missing/unknown → creative |
| All creative / untagged | Styleguide `condense` + Minimal | Single Gamma call; styleguide `text_mode`/`amount` unchanged | N/A |
| All literal | Styleguide `condense` + Minimal | Single Gamma call; `text_mode=preserve`; `amount` key absent | N/A |
| Mixed deck | Creative + literal-text slides | Two Gamma calls; cohort-scoped input; creative keeps styleguide; literal forced preserve; output reassembled in brief order by `slide_id` | Title-match / export errors unchanged (fail loud) |
| S8 figure-contradiction pin | Irene `literal-text` + styleguide `condense`+Minimal (teaching-critical / figure-adjacent copy) | Literal cohort preserve + amount absent — the silent-shorten failure mode cannot win | N/A |
| literal-visual | `fidelity: literal-visual` | Same preserve + amount-omit as literal-text (same literal cohort) | Image/URL injection out of scope |
| Boundary adjacency | Literal island amid creative | Preserve does not smear to neighbors | N/A |
| A/B × fidelity | `double_dispatch` + mixed fidelity | Call count = `variants × cohorts`; same split per variant | Fail loud on export/unmaterialized as today |
| Honor failure / Studio+literal | Literal tagged + studio variant (or preserve cannot be applied) | Raise (contract violation); no condense call | No silent condense fallback |

</frozen-after-approval>

## Code Map

- `app/marcus/orchestrator/package_builders.py` -- `build_gary_briefs` copies unit `fidelity` onto `slides[]`
- `app/specialists/gary/_act.py` -- `generate_gamma_variants` partitions binary cohorts + forces preserve on literal
- `app/specialists/gary/payload_contract.py` -- no new top-level keys (`fidelity` rides inside `slides[]`)
- `skills/gamma-api-mastery/scripts/gamma_operations.py` -- legacy pattern reference only (do not three-way call)
- `tests/integration/marcus/test_package_builders.py` -- T1–T2
- `tests/specialists/gary/test_gary_gamma_dispatch.py` -- T3–T8 via FakeGammaClient.generate_calls
- `_bmad-output/planning-artifacts/deferred-inventory.md` -- MET Irene-literal; L1 residual explicit

## Tasks & Acceptance

**Execution (RED first — T1–T8 must fail for the right reason before prod edits):**
- [x] T1 `test_build_gary_briefs_carries_unit_fidelity` — `tests/integration/marcus/test_package_builders.py`
- [x] T2 `test_build_gary_briefs_unknown_fidelity_defaults_creative` — same
- [x] T3 `test_all_creative_styleguide_text_mode_amount_unchanged` — `tests/specialists/gary/test_gary_gamma_dispatch.py`
- [x] T4 `test_literal_cohort_force_preserve_amount_key_absent` — same (S8 figure-contradiction pin: literal + condense+Minimal)
- [x] T5 `test_mixed_deck_splits_and_rejoins_brief_order_by_slide_id` — same (collide titles so title-fuzzy would fail)
- [x] T6 `test_literal_island_does_not_smear_neighbors` — same
- [x] T7 `test_ab_double_dispatch_times_fidelity_cohorts` — same (`len(generate_calls) == variants × cohorts`)
- [x] T8 `test_literal_honor_failure_raises_no_condense_fallback` — same (studio+literal or blocked preserve → raise; no condense call)
- [x] `app/marcus/orchestrator/package_builders.py` -- copy recognized `fidelity` onto brief slides
- [x] `app/specialists/gary/_act.py` -- binary partition; cohort-scoped input; force preserve + strip amount; split when mixed; reassemble by brief order/`slide_id`; studio+literal fail-loud
- [x] Live-exercise each seam as authored/edited (FakeGammaClient wire asserts + focused pytest/ruff) — session-goal DoD; not mocks-only
- [x] `_bmad-output/planning-artifacts/deferred-inventory.md` -- MET `irene-text-literal-supersedes-styleguide-truncation`; rewrite so MET cannot be misread as L1 closure; leave `fidelity-L1-per-slide-text-mode` yellow/open with residual note
- [x] Closeout note: classic-preserve sibling disposition Ask-First (keep as optional whole-deck escape hatch until party dispositions)

**Acceptance Criteria:**
- Given a plan unit with `fidelity: literal-text`, when `build_gary_briefs` runs, then the matching slide carries that fidelity.
- Given an all-creative/untagged deck, when Gary dispatches, then styleguide text_mode/amount are unchanged (no preserve bleed).
- Given literal slides under a condense+Minimal styleguide, when Gary dispatches the literal cohort, then API `text_mode=preserve` and `"amount" not in text_options`.
- Given a mixed creative+literal deck, when Gary dispatches, then separate cohort-scoped Gamma calls run and `gary_slide_output` is reassembled in brief order by `slide_id`.
- Given `double_dispatch` + mixed fidelity, when Gary dispatches, then `len(generate_calls) == variants × cohorts`.
- Given literal tagged where preserve cannot be honored (incl. studio variant), when Gary dispatches, then raise; never silent condense fallback.
- Given this change set, when inspected, then no approved styleguide registry record was edited in place.
- Given closeout/inventory prose, when reviewed, then it does not claim `fidelity-L1-per-slide-text-mode` fully closed.

## Design Notes

Gamma `textMode` is deck-level; per-slide override requires binary cohort split on `generate_gamma_variants`.

Rejoin by stable `slide_id` / brief order — not title fuzzy match across cohorts.

`amount` must be **absent** on literal calls, not `None`/`0`.

## Verification

**Commands:**
- `.\.venv\Scripts\python.exe -m pytest -q tests/integration/marcus/test_package_builders.py tests/specialists/gary/test_gary_gamma_dispatch.py --tb=short` -- expected: all pass (incl. T1–T8)
- `.\.venv\Scripts\python.exe -m ruff check app/marcus/orchestrator/package_builders.py app/specialists/gary/_act.py` -- expected: clean

**Process DoD:** focused suite green **and** seams live-exercised as authored (session goal); Codex shadow-monitor notes consulted when that ledger is in play.

## Suggested Review Order

**Fidelity carry (entry)**

- Plan-unit `fidelity` copied onto Gary slides; unknown omitted → creative.
  [`package_builders.py:137`](../../app/marcus/orchestrator/package_builders.py#L137)

**Binary cohort dispatch**

- Normalize + partition creative vs literal (`literal-text`∪`literal-visual`).
  [`_act.py:1121`](../../app/specialists/gary/_act.py#L1121)

- Literal cohort forces `text_mode=preserve` and strips `amount` key.
  [`_act.py:1179`](../../app/specialists/gary/_act.py#L1179)

- Studio + literal fail-loud before any Studio spend.
  [`_act.py:1285`](../../app/specialists/gary/_act.py#L1285)

- Mixed decks: cohort-scoped calls, rejoin by brief-order/`slide_id`.
  [`_act.py:1316`](../../app/specialists/gary/_act.py#L1316)

**Claim envelope / inventory**

- MET Irene-literal; L1 residual stays yellow/open.
  [`deferred-inventory.md:118`](../../_bmad-output/planning-artifacts/deferred-inventory.md#L118)

**Tests (T1–T8)**

- Builder carry + unknown omit.
  [`test_package_builders.py:221`](../../tests/integration/marcus/test_package_builders.py#L221)

- Dispatch preserve / split / island / A×B / Studio honor-failure.
  [`test_gary_gamma_dispatch.py:852`](../../tests/specialists/gary/test_gary_gamma_dispatch.py#L852)
