# Variant Selection — Downstream Consumption Gap (forensic finding + scoped fix, 2026-06-23)

**Severity:** HIGH for any 2-variant trial (latent until `gamma_settings` is present; single-variant runs unaffected). **Trigger:** the new variant arc (`45b7724`) now emits A/B rows per slide; nothing downstream consumes the operator's pick. **Owner of fix:** NEW CYCLE (substrate: `production_runner.py` + possibly the G2B card / select-verb).

## What I traced (ground truth)
1. **`selected_variant_id` is SET but never CONSUMED.** Every reference in `app/` (grep): it's a G2B card field (`g2b.py:54`), initialized `None` (`production_runner.py:613`), whitelisted as the G2B selectable key (`:818`), and surgically merged onto the envelope when the operator picks (`:854–855`). **No code reads it to filter slides.** The pick is recorded and ignored.
2. **No variant filter anywhere downstream.** Irene Pass-2 `_slide_roster` (`graph.py:118`) iterates **every** `gary_slide_output` row and appends each by `slide_id` — no variant awareness. With A/B present, a 6-slide deck yields **12 roster rows** (each slide twice). → duplicate/doubled narration + a malformed deck.
3. **The gap cascades upstream of Pass-2 too.** Vision perception (node 07F) + reading-path + the compositor all assume **one PNG per `slide_id`**. With 2 unfiltered variant PNGs sharing a `slide_id`, perception/reading-path/composition are ambiguous about which render they describe. So the selected variant must be resolved **before perception**, not just before Pass-2.
4. **Selection model mismatch (per-slide vs deck-wide).** `_variant_candidates` (`:443`) builds **per-slide** options (`per_slide[slide_id] = [variant rows]`; `options = [{slide_id, variants}]`), so Storyboard A surfaces a per-slide A/B choice. But `selected_variant_id` is a **single deck-wide string** — it can't express "slide 1 → A, slide 2 → B." The operator's stated intent ("pick the favored choice from each pair") is **per-slide**, which the current single field cannot carry.

## Net behavior today, with 2 variants
Picking a variant at G2B does nothing; **both** variants flow through perception → narration → composition, doubling/duplicating every slide. A 2-variant trial would produce a broken deck. (This is why the single-variant smoke `242b859f` was clean — 1 row/slide, gap not triggered.)

## The fix (scoped) — one chokepoint + a model decision

### Part A — the variant FILTER (load-bearing; required either way)
Immediately **after the G2B/G2C selection is recorded and before the vision-perception node (07F)**, filter the envelope's `gary_slide_output` so exactly **one row per `slide_id`** survives — the row whose `variant_id`/`dispatch_variant` matches the operator's pick. Drop the rest. If no selection / single-variant (`selected_variant_id is None` and ≤1 row/slide) → no-op (preserves today's behavior). This makes the pick route the chosen PNG through perception → reading-path → Pass-2 → compositor, and removes the doubling. **This is the chokepoint that closes the gap.**

### Part B — the SELECTION MODEL (operator decision; sets the fix size)
- **Option 1 — Deck-wide (minimal):** keep the single `selected_variant_id`; the filter keeps that variant for the whole deck (pick one consistent look, A or B). Smallest change: consume the existing field in the Part-A filter + a test. Does NOT match per-slide intent.
- **Option 2 — Per-slide (matches operator intent; recommended):** replace/augment `selected_variant_id` with a **per-slide selection map** `{slide_id: variant_id}`. Changes: the G2B card carries the per-slide picks (the per-slide options already exist), the select-verb merges the map (extend `_SELECTABLE_KEYS_BY_GATE` handling), and the Part-A filter applies per-slide. Bigger but coherent — and it's what "pick the favored choice from each pair at Storyboard A" means.

### Acceptance
A 2-variant trial: pick (deck-wide or per-slide) → exactly the picked render(s) flow downstream (roster has N slides not 2N; perception/narration/composition use the selected PNG) → final deck has the chosen variants, no duplication. Backward-compat: single-variant / no-pick runs unchanged. RED-first test pinning the doubling-bug + the filter.

## Governance
NEW CYCLE (substrate). Party green-light (the per-slide-vs-deck-wide model decision is a real scope choice) → Codex T1–T10 → Claude T11. File to deferred-inventory; this is a **pre-2-variant-trial blocker** (a 2-variant trial must NOT run before this lands; single-variant trial is unaffected).
