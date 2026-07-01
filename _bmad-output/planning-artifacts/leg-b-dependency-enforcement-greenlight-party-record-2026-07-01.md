# GREEN-LIGHT Party Record — Leg-B (dependency enforcement)

**Date:** 2026-07-01 · **Arc:** Gamma Styleguide Library · **Branch:** `dev/gamma-styleguide-library-2026-07-01` · **Phase:** 4-implementation
**Verdict:** **RATIFY-WITH-AMENDMENTS, 6/6. Mandatory SPLIT B1/B2.** No impasse (Decision-7 resolved by scoping).
**Party:** Winston, John, Murat, Amelia (core) + Gary (Gamma specialist) + Dan (CD). Fully-spawned independent subagents.

## Decision 1 — SPLIT (6/6)
**B1 = documented dependency rules** (static, offline, high-certainty — ship now). **B2 = learned-store scaffold** (stateful, governance-heavy — sequenced AFTER B1; depends on B1's rule-id namespace). Do not fuse: bundling hides B2's cost/governance behind B1's easy green.

## Decision 2 — Documented rules (B1). Gary's Gamma-truth corrections are BINDING.
Leg-A already covers rules 1 (custom-preset⇒custom_style), 4 (studio surface-violation+template), 8 (theme-existence `--check-existence`). B1 adds:
- **Rule 2 — `image_model` honored only under `image_source=aiGenerated`.** GREEN, accurate (model string is a no-op under unsplash/webAllImages/giphy/pictographic). **Hard BLOCK.**
- **Rule 3 — named `stylePreset` + conflicting top-level `image_style`.** CORRECTED (Gary): preset and `imageOptions.style` are **merged** channels — preset dominates the card theme while `imageOptions.style` still steers image generation; it is NOT a global "style ignored." Encode as **WARN on a CONFLICTING `image_style`**, evaluated on the **RAW record** (Amelia — the resolved surface has already dropped/overridden it), **LOUD/visible, never a silent drop** (Dan). Must stay consistent with the `gamma-keywords-to-imageoptions-style-channel` route (that channel survives). Assert the diagnostic + disposition in the fixture.
- **Rule 5 — `numCards` + `card_split`.** CORRECTED (Gary): the real conflict is `numCards` present AND `card_split` = an **explicit break-set** (numCards is then dropped) — NOT "card_split=auto required." Encode the explicit-split+numCards conflict.
- **Rule 6 — `dimensions` non-Classic.** GREEN but **DEDUP** with the Leg-A studio-surface union (Winston/Gary): implement as a union-membership assertion, ONE error message, no double-fire for dimensions+studio.
- **Rule 7 — one `export_as` per request.** CONDITIONAL (John): keep in B1 ONLY if `export_as` is a **styleguide-YAML-authored** field; if it's runtime-request-assembly shape, DROP from B1 (guards the wrong surface). Confirm at T1.
- **NEW Rule — `from-template` path forbids `theme_id`** (Gary): the template carries the theme; supplying both is a conflict Gamma resolves unpredictably. **Add — static pair BLOCK.**
- **Candidate (lower priority, Gary):** `text_mode=preserve` requires author-supplied card text (empty inputText → empty cards) → WARN candidate; file or fold-if-cheap.

## Decision 3 — Learned store (B2). AMENDED to a scaffold; promotion machinery DEFERRED.
- **Two-store split (Winston/Dan/Amelia, load-bearing):** raw OBSERVATIONS = runtime append-only **asset-ledger = SSOT** (`{run_id, observed_at, output_digest, source_component}`; digest-collision-rejecting = structurally append-only, no live fetch) + BMAD memory sidecar = a **read-optimized projection, rebuildable from the ledger, never a second writable store**. Promoted RULES = CD-authored `learned_dependencies` YAML block via the **envelope ONLY**, provenance-cited, validator-gated. An observation reaching the YAML by any non-envelope route breaks the advisory boundary.
- **Promotion authority (Dan, BINDING):** automation **PROPOSES** a candidate into the ledger; **CD RATIFIES-and-authors it via the envelope** (same ceremony as any CD write). Automation never holds the pen. NOT operator (doesn't scale), NOT auto-write (boundary breach).
- **Identity-manifest pin (Murat, BINDING):** `learned-rules.lock` = sorted manifest of `{rule_id, provenance-run-ref, fixture-path, predicate-hash}`. CI asserts live-store rule-id set **⊇ manifest** (superset — append-only, never equality-that-drops); per-entry **predicate-hash** match (no in-place mutation); count = secondary tripwire only. A drop OR a swap both go RED, naming the dropped id + its birthing-run.
- **Provenance triple (Dan):** every `learned_dependencies` entry carries (a) birthing-run/evidence id, (b) committed fixture path, (c) promotion timestamp + CD-authoring commit. Fixture-or-it's-not-learned. A rule whose fixture was deleted goes RED, not quietly persists.
- **Schema (Amelia):** declarative `{rule_id, antecedent(field+predicate), consequent(field+expected), severity(fail|warn), provenance, status(active|candidate)}` — the validator interprets it identically to the hardcoded rules; no free-form logic.
- **SCOPE (John/Murat/Amelia — DEFER promotion machinery):** **B2-lite** = schema + append-only ledger (the write-target Leg-E fills) + memory-sidecar projection + identity-manifest pin + validator interpretation. The 3 learned candidates (model UI-name≠API-string; **burst-throttle 401≠429** [Gary: "gold"]; parallel-task cap) are seeded as **WARN-only OBSERVATIONS in the ledger, NOT promoted rules.** The automation-proposes/CD-ratifies live promotion + envelope authoring = a bounded gated FOLLOW-ON, post-Leg-E (once real observations prove a candidate would have caught a failure).
- **Anti-vacuous-green guard (Murat, BLOCKING):** the manifest **starts empty by design** (seeded candidates are observations, not learned; they do NOT count toward the pin). Every manifest entry must resolve to a committed RED-proven birthing fixture (without-rule fails / with-rule passes). A non-empty store with no fixtures = RED. An empty claimed-learned set is honest only when the manifest is explicitly declared empty.

## Decision 4 — Audit/validator boundary (6/6)
Leg-B adds **ZERO live fetch**; the static validator stays hermetic/offline/BLOCKING (the write-gate). Live `--check-existence` = Leg-E / an operator-gated alerting job, NEVER a build gate. CI reads a committed **recorded-fetch snapshot**. Add a **no-network guard test** (the validator refuses network in CI mode) — the thing that rots first (Murat/Amelia).

## Decision 5 — Gate mode
**B1 dual-gate** (Murat structural + Gary/Dan content — rule ACCURACY is a Gamma-truth + false-block-risk concern that needs a content seat; John dissented toward single-gate but the enum/union touch + over-block risk carry dual). **B2 dual-gate** (Murat structural + Dan/CD authoring-boundary + learned-rule provenance — Dan claims the CD seat; B2 changes what can enter the CD YAML).

## Decision 6 — Live-proof bar
- **Per-rule RED-first failing-case fixture (teeth) + a known-GOOD styleguide per rule that must PASS (Gary — anti-false-positive, more important than teeth given rules 3/5).** Assert the diagnostic id/string, not just exit code.
- Live `--check-existence` (real `list_themes`) = operator-gated evidence for rule 8/Leg-E, NOT a B1 ship-gate.
- **B2:** append-only pin RED-proof (mutate/drop a ledger row → red build); anti-vacuous manifest-empty honesty.
- **HONESTY DISCLAIMER (Dan, BINDING):** B2 must explicitly state the **live CD envelope-authoring ceremony is validated-by-fixture, NOT exercised-live** (inherits Leg-A's AC#6 gap). It proves (a) rules enforce, (b) promotion criteria + provenance schema correct, (c) append-only pin bites — it does NOT exercise the live envelope write. Defer the live ceremony to `styleguide-cd-envelope-authoring-ceremony`. Don't half-exercise. "The guardrail shrinks the claim to the truth."

## Decision 7 — Non-contradiction validator (scoped synthesis, no impasse)
Fold ONLY the **narrow deterministic** form into B1 as a WARN (prose contains a literal enum token that contradicts a structured param — pure string/enum, closed-enum/keyword-anchored, no LLM), IF tractable with a RED + known-good fixture (Winston/Murat/Amelia/Gary). The **general semantic** prose-vs-param validator (paraphrase/intent, needs model-in-loop) stays the FILED follow-on `gamma-prose-vs-param-noncontradiction-validator`, tagged to the Leg-E live-audit lane (Dan/John — their objection applies only to the fuzzy form, which we keep out of the hermetic write-gate). If the narrow subset proves untractable within B1's cycle, it graduates to its own item rather than blocking B1.

## Next
Open **B1** (documented rules) via the spine now: `bmad-create-story` → dev RED-first → dual-gate. Then **B2** (learned-store scaffold). The non-contradiction general validator + the CD envelope-authoring live ceremony remain filed follow-ons.
