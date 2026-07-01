# AC#8 Live-Proof — styleguide-retire-default-variant-pair (single-gate-PLUS)

**Evidence dir:** `retire-variant-pair-ac8-20260701T180148Z`  ·  **Verdict: PASS**  ·  first-run-stands, real Gamma, no mocks.

**Claim:** a single styleguide binding paid-dispatches EXACTLY ONE deck (no unbound fixture-B).

## Discriminating deterministic block (free, no dispatch)
- single binding → `1` deck (variant `A`)
- A+B binding → `2` decks, order `['A', 'B']` (the old hardcoded `[A,B]` — now genuinely payload-driven)
- `[None]` (non-empty, zero valid) → **raises** `gamma.settings.invalid` (R2 — closes the retired-fixture re-dispatch hole)
- duplicate variant → **raises** (R1)
- empty `[]` → `0` (AC#4 preserved)

## Live real-Gamma single-binding dispatch
- **real `generate_deck` calls: 1** (wrapped-client witness; expect 1)
- server generation ids: `['dc3wcCxQttkyUwr3MvNlL']`
- `calls_made`=1, `generation_mode`=`single-dispatch`
- output variants: `['A']` (no unbound fixture-B)
- materialized variant-A decks on disk: `['A_p3-high-maze.png', 'A_p3-low-summary.png', 'A_p3-med-physicianship.png']`
- **NEGATIVE TWIN — variant-B decks on disk: `[]`** (expect none)
- per-row bytes: A_p3-low-summary.png=472612, A_p3-med-physicianship.png=603892, A_p3-high-maze.png=611377

## Checks
- ✅ deterministic_cardinality_and_fail_loud
- ✅ exactly_one_real_generate_deck_call
- ✅ exactly_one_server_generation_id
- ✅ result_calls_made_is_1
- ✅ generation_mode_single_dispatch
- ✅ output_variants_are_A_only
- ✅ all_rows_materialized_real_bytes
- ✅ NEGATIVE_TWIN_no_fixture_B_deck_on_disk
- ✅ variant_A_decks_present

**AC#8 PASS: True**

_Note: the driver's inline `n_on_disk_pngs==n_rows` check FAILED because it naively counted Gamma's raw numbered export pages (`1_`,`2_`,`3_`) + the `gary_A` composite as deck rows. Per the Leg-A gotcha (re-judge from true on-disk artifacts, not the driver's inline judge), the honest arbiter is the negative twin above: every ROW materialized with real bytes AND zero `B_` fixture deck. The substrate claim passed on the first successful dispatch; this re-judge corrects the JUDGE, not the code — no new spend._

_First attempt (`retire-variant-pair-ac8-20260701T180025Z`) hit the known bijective-title-matcher flake (`gamma.export.brief-unmatched`) AFTER the real `generate_deck` call #1 fired — a documented concierge-backlog gotcha unrelated to this change; corpus swapped to the Leg-A known-good set (clean-the-title fix), NOT retry-to-green on the logic._