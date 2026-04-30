---
name: extract-and-validate
description: Extract source content and validate quality before delivery
code: EV
---

# Extract & Validate

## What Success Looks Like

Every source in the wrangling directive produces a Material result — either verified content ready for downstream consumption, or a clear report explaining why it couldn't be extracted and what alternatives exist. The 30-line-stub-from-24-pages disaster never happens again because quality is checked *immediately* after extraction, not downstream.

## Your Approach

For each source in the directive:

1. **Extract** using the method appropriate for the source type. Load `./references/transform-registry.md` for the extraction method hierarchy per format. Start with the default; you'll fallback if needed.

2. **Validate immediately** — run `./scripts/extraction_validator.py` against the output. The validator classifies into four tiers:
   - **Tier 1 (Full Fidelity)**: Content complete, structure preserved. Proceed.
   - **Tier 2 (Adequate with Gaps)**: Mostly complete, known losses documented. Proceed with warnings.
   - **Tier 3 (Degraded)**: Significant content loss. Trigger fallback chain — try the next extraction method.
   - **Tier 4 (Failed)**: Near-empty or nonsensical. Exhaust fallbacks, then escalate.

3. **Cross-validate** when reference assets are available. Run `./scripts/cross_validator.py` comparing the extraction against any sources with `role: validation`. Multiple validation assets may exist with different coverage scopes — weight each by its relevance.

4. **Fallback** if the primary extraction degrades. The transform registry defines ordered fallback chains per source type. If all automated methods fail, evaluate whether a validation-role asset can substitute as the primary source. Document the substitution decision.

5. **Report** — produce a quality manifest alongside every extraction. The manifest includes tier classification, word/line/heading counts, completeness ratio, cross-validation results, known losses, and recommendations.

## The Proportionality Check

This is your non-negotiable. After every extraction, compare actual output against expected output:
- A 24-page PDF should yield roughly 4,800-7,200 words (200-300 words/page floor)
- If actual < 50% of expected → Tier 3 minimum, trigger fallback
- If actual < 20% of expected → Tier 4, exhaust fallbacks then escalate

The validator script handles the arithmetic. Your job is to never skip it and to act on its verdict.

## Memory Integration

Check MEMORY.md for known extraction patterns — have you seen this source type before? Did a particular fallback work well for similar sources? Have you learned baseline metrics for this course's content?

After the session, record what worked: which extraction methods succeeded, which failed, what the actual word counts were for this source. Future runs benefit from your experience.

## After the Session

Log the extraction results in your session record: sources processed, tiers assigned, fallbacks triggered, cross-validation outcomes. Flag any sources that required unusual handling — these become learned patterns.
