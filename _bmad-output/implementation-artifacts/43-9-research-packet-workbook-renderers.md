# Story 43-9 — Research-packet + workbook content (render OR de-scope honestly)

**Epic:** 43 · **Slab:** 3 (sequenced LAST — rider R6) · **Status:** ready-for-dev · **Gate mode:** dual-gate.

**This story is different:** `research_packet` and `workbook` have **no poll_surface** (per the static-validation audit). So the first job is to determine whether they are even **operator-reviewed HIL surfaces** — if yes, render them; if no, **remove them from the canonical `GATE_CONTENT_TYPES`** with rationale (the coverage set should only contain content types the operator actually reviews at a gate). Do the honest thing, not a phantom renderer.

## T1 required readings / investigation

- `app/marcus/cli/hil_tabular_projector.py` — `GATE_CONTENT_TYPES`, `KNOWN_UNRENDERED_ALLOWLIST`, the registry + bridge, the landed renderers (pattern).
- Determine whether research packets and the workbook are presented to the operator at a **paused gate** for review:
  - Research: trace where the research packet is produced (node `04.55`) and whether any gate pauses to show it to the operator (check `app/gates/**`, the manifest gate list, `ProductionGateId`, and on-disk evidence cards). G0R / enrichment may already surface research via existing renderers.
  - Workbook: trace the `07W.1`–`07W`/`07W` band (`app/marcus/orchestrator/workbook_wiring.py`) — does any 07W node pause for operator HIL, or does the band run post-G5 without an operator review gate?
- `_bmad-output/planning-artifacts/epic-43-hil-surface-tabular-coverage.md` §2; `tests/marcus/cli/test_build_target_renderers_43_6.py`; TW-7c-4 Epic-43 block.

## Acceptance criteria (branch on the investigation)

**If a content type HAS an operator-reviewed paused-gate surface:**
- **AC-R1** — a bespoke renderer registered under its canonical key (`"research_packet"` / `"workbook"`), built from the real reviewed content; bridge entry; synthetic fixture; routing test; moved allowlist→registry. (Same pattern as 43-6/43-8.)

**If a content type has NO operator-reviewed gate surface (expected likely for at least one):**
- **AC-D1** — REMOVE it from `GATE_CONTENT_TYPES` (and from `KNOWN_UNRENDERED_ALLOWLIST`) with a clear code comment + rationale ("`workbook` runs post-G5 with no operator review gate; not a HIL surface"). Update the ratchet state-pin so the canonical set is now accurate. This is an honest correction of 43-10's provisional set, not a skip.

**Either way:**
- **AC-2** — after this story, `KNOWN_UNRENDERED_ALLOWLIST` contains ONLY the still-open motion types (if 43-7 not yet done) — i.e. `research_packet`/`workbook` are resolved (rendered OR removed). Document the disposition of each in the story completion notes + fixtures README.
- **AC-3** — invariants: stdout/stderr split; additive-within-v1; projector stdlib-pure; TW-7c-4 register any new test .py; ruff + import-linter clean; no manifest touch; ratchet green.

## Test / process

- New test file (if rendering) or ratchet/canonical-set test updates (if de-scoping). Use `-n 0`. Do NOT run the full suite. Do NOT commit or stash.

## Definition of done

Each of `research_packet` and `workbook` is resolved — rendered (registered + fixture + routing) OR removed from the canonical set with rationale; ratchet green with the corrected canonical set; disposition documented; ruff/import-linter clean; ready for orchestrator review → `bmad-code-review`.
