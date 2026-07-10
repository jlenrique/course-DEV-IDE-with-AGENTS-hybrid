---
title: 'Irene Pass-1 fidelity emit recovery (literal-text first)'
type: 'bugfix'
created: '2026-07-09'
status: 'done'
baseline_commit: 'f30c88c93d99687a96d264dd6783d5e6bf3fc674'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/spec-irene-literal-supersedes-styleguide-truncation.md'
  - '{project-root}/skills/bmad-agent-content-creator/references/template-slide-brief.md'
  - '{project-root}/_bmad/memory/bmad-agent-marcus/references/conversation-mgmt.md'
---

<!-- Party green-light 2026-07-09 (independent BMAD seats):
     John / Winston / Amelia / Murat = 4/4 GO-WITH-AMENDMENTS.
     MUST amendments folded below. Impasse chain: Quinn first, then John.
     Dirty-tree: ignore unstaged monitor/evidence/styleguide-picks (not in scope). -->

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Pre-migration Irene Pass-1 classified per-slide `literal-text` and `literal-visual` needs. Post-migration Pass-1’s JSON emission contract never requests `fidelity`, so live `plan_units` omit it; the already-shipped Gary preserve path never fires. Operator rejected G1 stamp workarounds.

**Approach:** Restore Pass-1 emission of per-unit `fidelity` (`creative` | `literal-text` | `literal-visual`) on the dict-shaped plan-unit path, honor optional envelope `fidelity_guidance`, soft-normalize unknowns, and surface tags in `irene-pass1.md`. This slice prioritizes the **literal-text** end-to-end path with existing Gary preserve; classification may still emit `literal-visual` as metadata, but literal-image production streamlining is deferred brainstorm — not claimed shipped.

## Boundaries & Constraints

**Always:**
- Contract field: `plan_units[].fidelity` ∈ {`creative`, `literal-text`, `literal-visual`} on Pass-1 dict units (not Lesson Planner `PlanUnit` Pydantic).
- Emission instructions explicitly request fidelity classification for both literal-text and literal-visual; default `creative`; do not over-tag.
- When envelope carries `fidelity_guidance`, Irene must honor it (supplements, does not replace judgment for unmarked units).
- Soft normalize: recognized values kept; unknown/empty → omit key (Gary treats missing as creative). Never invent fidelity from prose-only “guidance theater.”
- `write_lesson_plan` surfaces a fidelity line per unit when present.
- Additive prompt/parse pattern (sibling of cluster/collateral emission); Gary consumption unchanged.
- Claim envelope: closes **Pass-1 fidelity emit recovery** (classification + carry into artifact). Does **not** close literal-visual production streamline, §06B image injection, L1-per-slide broadly, or liveproof (liveproof is post-implement, no stamp).
- Product goal remains Marcus-SPOC runtime correctness.

**Ask First:**
- Extending Lesson Planner `PlanUnit` with a formal `fidelity` field.
- Wiring/changing HIL mode-approval (`hil-mode-approval.json`) as a hard gate in this slice.
- New fidelity enum values beyond the three recognized modes.
- Treating `literal-visual` emit as proof that visual production is streamlined.

**Never:**
- G1 / AFK-driver fidelity stamps or mock injection for “proof.”
- Claiming “literal-visual production streamlined” or “L1-per-slide closed.”
- Mutating approved styleguide registry records.
- Image URL injection / §06B operator-build redesign in this slice.
- Failing the walk solely because `literal-visual` is classified while production streamline is still deferred (Gary’s existing literal-cohort preserve for text remains OK).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Emission contract | Assemble Pass-1 prompt | User prompt requests per-unit `fidelity` + classification guidance (both literal modes) | N/A |
| Structured literal-text | LLM JSON unit has `fidelity: literal-text` | Parse/normalize keeps it; artifact line present; Gary brief can carry | N/A |
| Structured literal-visual | LLM JSON unit has `fidelity: literal-visual` | Tag preserved as classification metadata; no new image-production path | N/A |
| Missing fidelity | Unit omits field | Omit key; plan still succeeds; creative cohort downstream | N/A |
| Unknown value | `fidelity: "strict"` / null | Soft-omit key; do not invent | No raise |
| Guidance present | Envelope `fidelity_guidance` with literal_text items | Prompt includes guidance; model expected to honor (unit test: guidance visible in assembled prompt) | N/A |
| Guidance theater | Prose mentions “fidelity” but structured field absent/unknown | No manufactured tag | N/A |
| Refinement carry | Incoming plan units already tagged | Carry recognized tags forward unless model re-emits; do not strip recognized values in normalize | N/A |

</frozen-after-approval>

## Code Map

- `app/specialists/irene_pass1/_act.py` — emission instructions, `normalize_fidelity`, `parse_pass1_response` chain, `write_lesson_plan`
- `skills/bmad-agent-content-creator/references/template-slide-brief.md` — classification guide (reference; update only if wording drifts from restored contract)
- `app/marcus/orchestrator/package_builders.py` — already copies unit fidelity (no behavior change expected)
- `tests/specialists/irene_pass1/test_irene_pass1_fidelity_emission.py` — RED-first suite (new)
- `_bmad-output/planning-artifacts/deferred-inventory.md` — file `literal-visual-production-streamline` follow-on

## Tasks & Acceptance

**Execution:**
- [x] `app/specialists/irene_pass1/_act.py` -- Add fidelity emission guidance (additive) + soft `normalize_fidelity` in parse chain + artifact lines -- restore pre-migration classification contract on dict path
- [x] `tests/specialists/irene_pass1/test_irene_pass1_fidelity_emission.py` -- RED then green for matrix cases -- prove emit/normalize/artifact without LLM
- [x] `_bmad-output/planning-artifacts/deferred-inventory.md` -- File named follow-on for literal-visual production streamline brainstorm -- operator-requested; not this slice
- [x] `_bmad-output/implementation-artifacts/deferred-work.md` -- Mirror one-line pointer to the inventory entry -- quick-dev hygiene

**Acceptance Criteria:**
- Given Pass-1 prompt assembly, when inspected, then the user prompt explicitly requests per-unit `fidelity` with the three recognized modes and anti-over-tag guidance.
- Given a frozen LLM JSON fixture with `literal-text` (and separately `literal-visual`) on units, when parsed + written, then tags survive normalize and appear in `irene-pass1.md`.
- Given omitted or unknown fidelity, when parsed, then the key is omitted and the plan still succeeds.
- Given envelope `fidelity_guidance`, when prompt is assembled, then guidance content is present in the model-visible payload/prompt (no stamp; no fake tags from prose alone).
- Given existing Gary carry tests, when this slice lands, then they remain green without requiring production streamline for `literal-visual`.

## Spec Change Log

## Design Notes

Pre-migration: Irene assigned modes in Pass 1; v4.2 pack still says “Exactly one mode per slide.” Migration left the slide-brief *docs* but dropped the Pass-1 JSON field — Gary later learned to honor tags that never arrive.

This slice restores **classification emit**. Gary already maps literal cohort → `text_mode=preserve`. Literal-**image** production (rebrand PNG drop, §06B, URL injection) stays cumbersome by operator report — file brainstorm follow-on; do not pretend emit equals streamlined production.

Prefer asserting required field names / phrases in prompts, not full prompt golden blobs.

## Verification

**Commands:**
- `.\.venv\Scripts\python.exe -m pytest tests/specialists/irene_pass1/test_irene_pass1_fidelity_emission.py tests/specialists/irene_pass1/test_irene_pass1_cluster_emission.py tests/integration/marcus/test_package_builders.py -q` -- expected: all green
- `.\.venv\Scripts\ruff.exe check app/specialists/irene_pass1/_act.py tests/specialists/irene_pass1/test_irene_pass1_fidelity_emission.py` -- expected: clean

**Manual checks (if no CLI):**
- Post-implement (separate): authentic AFK Tejal P4 classic-condense liveproof with **no** fidelity stamp; claim only if real Pass-1 artifacts show structured `fidelity`.

## Suggested Review Order

**Emission contract**

- Additive fidelity block between cluster and collateral instructions
  [`_act.py:287`](../../../app/specialists/irene_pass1/_act.py#L287)

- Wired into Pass-1 prompt assembly
  [`_act.py:217`](../../../app/specialists/irene_pass1/_act.py#L217)

**Soft normalize**

- Alias coerce + unknown omit (never invent tags)
  [`_act.py:593`](../../../app/specialists/irene_pass1/_act.py#L593)

- Parse chain applies normalize after collateral
  [`_act.py:665`](../../../app/specialists/irene_pass1/_act.py#L665)

**Artifact surface**

- Normalize-before-write so aliases still print; fidelity line when recognized
  [`_act.py:676`](../../../app/specialists/irene_pass1/_act.py#L676)

**Tests + deferrals**

- RED-first emit/normalize/artifact suite (8 tests)
  [`test_irene_pass1_fidelity_emission.py:1`](../../../tests/specialists/irene_pass1/test_irene_pass1_fidelity_emission.py#L1)

- Literal-visual production streamline filed (emit ≠ production)
  [`deferred-inventory.md`](../../planning-artifacts/deferred-inventory.md)
