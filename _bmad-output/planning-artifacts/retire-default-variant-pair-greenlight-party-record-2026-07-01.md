# GREEN-LIGHT Party Record — `styleguide-retire-default-variant-pair`

**Date:** 2026-07-01 · **Arc:** Gamma Styleguide Library · **Branch:** `dev/gamma-styleguide-library-2026-07-01` · **Phase:** 4-implementation
**Item:** RIPE Leg-A follow-on `styleguide-retire-default-variant-pair` (filed at Leg-A dual-gate CLOSE, Murat "RIPE NOW, next dev item not backlog drift").
**Verdict:** **RATIFY-WITH-AMENDMENTS, 6/6.** No impasse (Quinn/John chain not needed).

## Party composition (canonical core + ≤2 specialists)
Winston (architect), John (PM), Murat (TEA) + Amelia (dev) — canonical core. Gary (Gamma specialist, owns `_act.py`) + Dan (CD, owns the styleguide library) — specialists. Fully-spawned independent subagents.

## The defect (code-confirmed)
`app/specialists/gary/_act.py::_normalized_gamma_settings` seeds `by_variant` from `DEFAULT_VARIANT_PAIR` (A+B) and ends with a hardcoded `return [by_variant["A"], by_variant["B"]]` (`:523`) — always emits both variants regardless of what the payload's `gamma_settings` list named. A single-styleguide binding pads in fixture-B → an unbound fixture-B deck is paid-dispatched to real Gamma. Edge#8/Blind#2, reproduced live in the Leg-A AC#5 differential. Pre-authorization ("retire after one green live differential") SATISFIED by AC#5.

## Per-decision consensus

**1. SCOPE — 6/6 GREEN.** Return only payload-present variants; retire the `[A,B]` padding at `:523`. Direction-stable; backward-safe (two-variant A/B flow names both → still 2).

**2. DEFAULT_VARIANT_PAIR DISPOSITION — 6/6 (reconciled).** Nobody deletes. **Retain as the per-variant base seed** for a present-but-styleguide-less variant (`else: merged = dict(by_variant[variant_id])`, ~`:445`). The contention (Gary/Dan: retaining fixture theme+imagery for a styleguide-less variant is a *smaller* hidden-default) reconciles to **Dan's synthesis**: keep the seed as-is (no output-behavior change → backward-compat safe; the legacy concierge A/B default path names variants without binding a guide and must keep rendering), add a **loud WARN** when a present variant seeds without a bound styleguide, and **file the fail-loud flip as the `cd-envelope-authoring` teeth-arming follow-on**. Gary's "strip-to-neutral-seed now" folded into that deferred teeth-flip (strip-now would change proven production output — out of scope). This item honestly claims only "kills the padding defect," NOT "library is sole determinant for styleguide-less variants."

**3. EMPTY-LIST EDGE — 6/6 GREEN.** `gamma_settings == []` → `[]` (today wrongly pads to `[A,B]`). Pair with a dispatch-boundary assertion that `[]` ⇒ zero Gamma calls, logged not silently swallowed. Shape-pin test.

**4. GATE MODE — 6/6 GREEN, single-gate PLUS.** Pure dispatch-count representation; no authored words, no source-detail→Gamma conveyance touched → Dan's content-fidelity gate adds no signal. Murat structural gate is sufficient **but must carry a spend/dispatch-count assertion** (single-gate-PLUS) because the change alters PAID dispatch count. John/Dan condition: live-proof confirms the surviving deck's bound-styleguide field-set is intact/byte-unchanged (a structural assertion Murat owns).

**5. SEQUENCING — 6/6 GREEN.** Standalone now; Leg-B (dependency enforcement) opens fresh. Folding in would couple a clean defect-retirement to Leg-B scope.

**6. LIVE-PROOF BAR — 6/6 GREEN.** Deterministic driver, real Gamma (no mocks), single-styleguide binding → exactly ONE deck. **Discriminating**: prove the same binding would have dispatched 2 before / dispatches 1 after (delta anchored to real artifacts, not asserted by fiat). Arbiter = on-disk manifest/PNGs — **the driver's inline judge is BANNED** (Leg-A row-parse gotcha). Assert **Gamma generation call-count == 1** and **no second fixture-seeded deck on disk** (Dan's negative twin). Run the single-variant path **end-to-end through the emitter/compose-manifest** (Amelia).

## Binding amendments → story ACs
- **A1 (Amelia, #1 risk):** downstream 2-variant-assumption AUDIT — grep/read every consumer of `_normalized_gamma_settings` (callers ~`:800`, `generate_gamma_variants`, storyboard emitters, compose-manifest) for `[0]`/`[1]` indexing, `a, b =` destructuring, `len(...)==2`. Run single-variant end-to-end through the emitter in the live-proof.
- **A2 (Winston):** output order = payload list order (`dict.fromkeys`, not `set`); "present" = named in payload list; unknown `variant_id` → fail loud (already at `:411`, keep + pin).
- **A3 (Murat) RED-first test set:** (1) single-variant → `len==1` + named variant [RED before fix]; (2) two-variant → `len==2`, A before B [regression pin, never red]; (3) variant-order determinism; (4) `[] → []` + zero-dispatch/logged; (5) present-but-unknown variant_id → fail loud; (6) base-seed does not resurrect padding (present-but-styleguide-less → `len==1`); (7) live discriminator 2→1 anchored to on-disk artifacts + dispatch-count assertion.
- **A4 (Gary/Dan):** WARN-log on styleguide-less seeding + file `styleguide-retire-default-variant-pair-fail-loud-flip` (a.k.a. fold into `cd-envelope-authoring-ceremony`) as the teeth-arming successor in deferred-inventory.

## Gate designation
**SINGLE-GATE (Murat structural, PLUS spend assertion).** Live-proof: real Gamma, no mocks, first-run-stands. Shadow-monitor consulted (aligned; serves the "no hidden defaults masking the CD-owned library" boundary).
