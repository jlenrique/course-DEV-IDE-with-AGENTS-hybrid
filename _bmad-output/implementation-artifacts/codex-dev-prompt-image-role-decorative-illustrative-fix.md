# Codex Dev Prompt — image_role: sharpen the DECORATIVE-vs-ILLUSTRATIVE rubric (surgical)

**You are Codex (T1–T10).** Claude T11 (independent re-measure + review). Small, surgical iteration on the just-landed LLM-primary reading-path classifier (`with_llm_primary_reading_path` in `scripts/utilities/reading_path_classifier.py`). **Do NOT touch macro/text/cadence logic — they're strong** (macro 0.857, text 0.929, cadence 0.857). This iteration moves ONLY the image_role axis.

## The measured gap (subject=llm-primary, substrate=fresh@2026-06-23, first-run-stands)
primary-key 0.500 (7/14); per-axis: macro 0.857, **image_role 0.643 (9/14 — the bottleneck)**, text 0.929, cadence 0.857. Per-slide diagnosis of the 5 image_role misses:
- **4 of 5 are the SAME error: a DECORATIVE image is tagged ILLUSTRATIVE** (emitted tier `2`, gold tier `1`). The LLM prompt's image-role rubric isn't sharp on the tier-1-vs-tier-2 boundary.
- 1 of 5: the dominant image_role came back `None` on a slide that has a decorative image (a separate dominant-assignment miss).

Every one of these 5 slides already has CORRECT macro → each image_role fix becomes a primary-key hit. Projected: decorative-vs-illustrative fix → image_role ~0.93, **primary-key ~0.786**; + the dominant-when-None fix → image_role ~1.0, **primary-key ~0.857 (clears 0.85)**.

## The fix (prompt rubric, generalizable — NOT slide-specific)
Sharpen the image-role tier rubric in the LLM-primary classifier prompt with the operator-ratified 4-tier spectrum, making the **tier-1-vs-tier-2 boundary explicit**:

- **Tier 1 — DECORATIVE / evocative:** sets tone, mood, or theme. A photo/illustration is tier 1 — **even if it is a rich, prominent, full-bleed photograph** — when it has **no internal labels/text**, is **not a technical or instructional graphic**, and the slide's text does **not reference it as content**. The narrator should give it NO comment. *(This is the boundary being missed — default a prominent mood/subject photo to tier 1 unless it meets the tier-2 test below.)*
- **Tier 2 — ILLUSTRATIVE:** the image carries content the narration **may reference** (it depicts a specific thing the text/claim points at), but it is still **not** a technical/instructional diagram needing a walk-through.
- **Tier 3 — INSTRUCTIONAL:** a diagram/canvas/chart/framework with internal structure the narrator must walk through (already handled well — keep).
- **Tier 4 — POINTER / iconographic:** small icons that type/label a message unit; not narrated.

**Dominant-when-None:** when ≥1 image element is present but no dominant tier resolves, assign the slide-level `dominant_image_role` from the **largest image element's** tier (do not return `None` when an image exists).

## HARD fences (T11 rejects on violation)
- **NO slide-id special-casing.** No `if slide_id == ...`, no gold-keyed lookups, no tuning to the specific 14. The rubric must be a general RULE. (You're told the error *pattern* — decorative over-tiered — not "make slide 1 return 1.")
- **Gold frozen** — never re-labeled. Gold SHA must match at T11.
- **No-peeking:** tune to the aggregate image_role rate, not per-slide pass/fail.
- No mocks; live gpt-5.5; first-run-stands. Macro/text/cadence must NOT regress.

## Acceptance (re-measure over the SAME 14 frozen fresh perceptions)
`.venv\Scripts\python.exe scripts\analysis\reading_path_p2_4b_measure_fresh.py` → report honest, subject/substrate-tagged numbers. Target: **image_role ≥0.85 AND primary-key ≥0.78** (ideally ≥0.85 with the dominant-when-None fix), macro/text/cadence unchanged (±0), degraded 0, hard_blocks 0. Re-run the focused reading-path/vision/perception test suite green; ruff-clean touched files.

## Handoff → Claude T11
`_codex-handoff/image-role-decorative-illustrative-fix-ready-for-review.md`: the before/after per-axis numbers (subject/substrate-tagged), the rubric diff, gold SHA, baseline-diff attestation. Claude re-measures independently (fresh roll for the pattern; the scored number first-run-stands), audits the diff for slide-id special-casing, confirms macro/text/cadence held.
