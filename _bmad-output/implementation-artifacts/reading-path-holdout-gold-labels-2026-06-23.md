# Held-Out 14 — Operator-Confirmed Gold Labels (P2-4b conformance-finalize)

**Date:** 2026-06-23. **Author:** Claude (P2-4b pre-stage). **Status:** GOLD — operator-confirmed.
**Provenance:** operator confirm/deny verdicts 2026-06-22 (`holdout-confirm-deny-kit-2026-06-22.md` RESULTS section: 12 CONFIRM / 2 DENY [17_, 21_]) + the 3 ratified decisions D1–D3 (catalog v1.1 §11) folded in. This file is the **scoring gold** the P2-4b harness scores emitted tuples against once S2/S3 land.

## Purpose + scope

These 14 are the **consumed held-out reserve** — labeled by Claude via catalog v1, then operator-confirmed (the methodology flip; see the P2-4b spec). They are no longer naive for any future independent-label scoring; they are now the frozen gold for conformance measurement.

**Per-slide gold tuple recorded below:**
- `macro_layout` (AXIS 1)
- `image_role` — the **dominant** per-element tier in the LIVE-scored set {1, 2, 4} (2.5→2 folded; tier 3 quarantined/excluded). `none` when the slide carries no scored image element.
- `text_substructure` (AXIS 3) — per-axis vector, NOT folded into the primary-key top-1.
- `narration_cadence` (AXIS 4) — per-axis vector, NOT folded into the primary-key top-1.
- `callout_intent` (AXIS 5) — orthogonal probationary sibling; OUT of the primary-key + full-tuple top-1.
- **derived `primary` reading_path name** (from `macro_layout × dominant text_substructure`, per catalog §0.1 / §4.6 reconciliation).

**Scoring contract (A6, per gap-resolution G2/G3):**
- **PRIMARY KEY (scored top-1)** = `macro_layout × image_role∈{1,2,4}`. STRICT exact match, no partial credit. Threshold ≥0.85.
- **OUT of top-1 / full-tuple:** `callout_intent`, tier-2.5 (folds→2), tier-3 (quarantined).
- **per-axis vectors (reported, not folded):** `text_substructure`, `narration_cadence`.

---

## The 2 DENY corrections (D1 / D3 — judgment calls applied)

The operator denied **17_** and **21_**; both corrections are applied to the gold below and are ratified in catalog v1.1 §11.

- **17_Examples-of-Effective-Leadership-in-Public-Health** — kit proposed `two_pane` / `two_up_comparison`. **Operator:** the two side-by-side panels (Global Leaders | Local Champions) are **parallel-coordinate peers, not oppositional** (no vs/before-after/pro-con/✓✗ cue). Under **D1** (`multi_column` generalized to N≥2 coordinate peers; `two_pane`/`two_up_comparison` reserved for oppositional-with-explicit-cue), the macro flips. **GOLD: macro_layout = `multi_column`, derived primary = `multi_column`.** `image_role` stays tier 2 illustrative (the two leadership photos). 17_ stays in the top-1 denominator (D1 rider: no metric laundering).

- **21_Key-Takeaways** — kit proposed `enumerated_process` (4 numbered takeaways). **Operator:** this is **a list, not a transform-sequence** — the 4 takeaways are permutable (reordering loses no meaning), and "Key Takeaways" is a directive callout. Under **D3** (`enumerated_process` tightened to transform-sequence via the permutability test; numbered summary lists → `peer_boxes`), the text_substructure flips; under **D2** the directive nature is captured by `callout_intent`. **GOLD: text_substructure = `peer_boxes` (NOT enumerated_process); callout_intent = `takeaway_imperative`.** The **macro_layout stays `split_image_text`** (compass photo right + numbered list left) and so does the derived **primary = `split_image_text`** — the primary KEY (`macro × image_role`) for 21_ is unchanged by the denial, which is why the held-out top-1 was 13/14 = 0.93 rather than 12/14: the 21_ denial moved only the `text_substructure` per-axis vector + added a `callout_intent`, not the scored primary key. (17_'s denial DID move the macro, hence macro per-axis = 13/14.)

> Note on `takeaway_imperative`: per catalog v1.1 §2 AXIS 5 governance, `takeaway_imperative` is a **harvest hypothesis NOT shipped to the frozen `callout_intent` enum** (only the 3 evidenced values — `invite_response`, `challenge_quiz`, `directive_cta` — are seeded). It is recorded here as the operator's correction note + routed to the `callout-intent-speech-act-axis-harvest` follow-on. Because `callout_intent` is OUT of every scored top-1, this does not affect the A6 numbers.

---

## Gold-label table (all 14, operator-confirmed 2026-06-22)

| # | slide_id | macro_layout | image_role (dominant, scored {1,2,4}) | text_substructure | narration_cadence | callout_intent | derived primary | verdict |
|---|---|---|---|---|---|---|---|---|
| 1 | `1_Diagnosis-Innovation` | `split_image_text` | 1 | `hero_message` | `moderate` | `inform` (null) | `split_image_text` | CONFIRM |
| 2 | `3_Achieving-the-Ideal-State` | `single_text_block` | 4 | `enumerated_process` | `dense` | `inform` (null) | `enumerated_process` | CONFIRM |
| 3 | `5_Check-Your-Understanding` | `single_text_block` | 1 | `peer_boxes` | `moderate` | `challenge_quiz` | `top_down` | CONFIRM |
| 4 | `6_All-of-them-belong-to-BOTH` | `split_image_text` | 1 | `hero_message` | `sparse_slow` | `inform` (null) | `split_image_text` | CONFIRM |
| 5 | `8_Decision-Making-Foundations` | `split_image_text` | 1 | `comparison_pair` | `moderate` | `inform` (null) | `two_up_comparison` | CONFIRM |
| 6 | `9_Comparing-Expected-Value-and-Expected-Utility` | `two_pane` | none | `comparison_pair` | `dense` | `inform` (null) | `two_up_comparison` | CONFIRM |
| 7 | `11_Value-Creation-in-Innovation` | `multi_column` | none | `enumerated_process` | `dense` | `inform` (null) | `enumerated_process` | CONFIRM |
| 8 | `13_Effective-Problem-Solving-Approach` | `multi_column` | 1 | `enumerated_process` | `dense` | `inform` (null) | `enumerated_process` | CONFIRM |
| 9 | `15_Types-of-Motivation` | `split_image_text` | 2 | `comparison_pair` | `moderate` | `inform` (null) | `two_up_comparison` | CONFIRM |
| 10 | `17_Examples-of-Effective-Leadership-in-Public-Health` | **`multi_column`** | 2 | `peer_boxes` | `dense` | `inform` (null) | **`multi_column`** | DENY → D1 |
| 11 | `18_The-Future-of-Public-Health-Leadership` | `single_text_block` | none | `dense_exposition` | `dense` | `invite_response` | `top_down` | CONFIRM |
| 12 | `20_Resources-for-Entrepreneurship-and-Innovation` | `card_grid` | none | `peer_boxes` | `dense` | `inform` (null) | `grid_quadrant` | CONFIRM |
| 13 | `21_Key-Takeaways` | `split_image_text` | 1 | **`peer_boxes`** | `moderate` | **`takeaway_imperative`** | `split_image_text` | DENY → D3 |
| 14 | `22_Next-Steps-Your-Path-Forward` | `card_grid` | 4 | `peer_boxes` | `dense` | `directive_cta` | `grid_quadrant` | CONFIRM |

**Folding/exclusion applied:** no held-out slide carried a tier-2.5 or tier-3 image element, so the {1,2,4} scored set is fully populated by the dominant tiers above. `none` (slides 6, 7, 11, 12) means the slide carries no scored image element; the primary key for those slides is `macro_layout × none`.

**Derived-primary notes:**
- 12_ (`20_`) and 14_ (`22_`) are `card_grid` macro → derived primary **`grid_quadrant`** (NOT `top_down`), per catalog §4.6 RECONCILIATION (card_grid must not collapse into the DEFAULT bucket).
- 5_, 8_, 15_ carry `comparison_pair` text_substructure → the human-readable primary name is `two_up_comparison` even when the macro is `split_image_text` (nested comparison) — comparison composes with any macro (catalog §4.2). The scored PRIMARY KEY is still `macro_layout × image_role`, independent of the derived name.

---

## A6 numbers these gold labels reproduce (held-out round, 2026-06-22)

Scoring emitted-vs-gold with this gold (the held-out confirm/deny round, which IS the P2-4b dry run on Claude's v1 labels as "emitted"):

- **primary-key `{macro_layout × image_role}` top-1 = 13/14 = 0.93** (≥0.85 ✅). The single miss is 17_ (macro flipped `two_pane`→`multi_column` under D1).
- **derived-primary-name 12/14 = 0.857** (≥0.85 ✅) — the operator's 12-CONFIRM count (17_ + 21_ denied at the slide level).
- **per-axis:** image_role 14/14 · narration_cadence 14/14 · macro_layout 13/14 (17_) · text_substructure 13/14 (21_).
- `callout_intent` is OUT of the scored top-1 (D2), so it does not move these numbers.

These are reproduced by the P2-4b harness self-test (`tests/analysis/test_reading_path_p2_4b_score.py`) using a synthetic emitted-set that mirrors the held-out round (13/14 primary-key → 0.93).

---

## Provenance / governance

- **Tag:** operator-confirmed 2026-06-22 (verdicts) + D1–D3 ratified (catalog v1.1 §11).
- **Reserve status:** CONSUMED — these 14 are no longer naive (operator-accepted methodology flip).
- **Authority chain:** `holdout-confirm-deny-kit-2026-06-22.md` (verdicts) → `reading-path-gap-resolution-G2-G3-2026-06-22.md` (A6 IN/OUT contract) → `reading-path-patterns-catalog.md` v1.1 §9.4 / §11 (build + metric contract) → this file (frozen gold).
- **Follow-ons:** `callout-intent-speech-act-axis-harvest` (D2; `takeaway_imperative` promotion evidence); tier-2.5/tier-3 promotion probes (none triggered by these 14).
