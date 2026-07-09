# Shadow Monitor - `irene-text-literal-supersedes-styleguide-truncation` (Grok 4.5 Cursor-led session)

Started: 2026-07-09T13:58:46-04:00
Branch: `dev/lesson-planning-2026-07-09` - baseline HEAD `c6871da0`.
Driver lane: Grok 4.5 in Cursor.

## Monitor Lane (read-only, independent)

This is an independent shadow-monitoring lane for the Grok-led dev session. Each poll reads the current repository state and appends a time-stamped report with findings (`SOP-NNN`). The monitor writes only this log. It does not modify production code, tests, runtime state, commits, branches, Grok/Cursor-owned artifacts, or BMAD-owned decision records.

The lane's job is to catch regressions, unratified drift, vacuous-green, claim-envelope overreach, and SPOC product-boundary violations before the active driver claims a gate or done-bar.

## Product Boundary (binding)

The only product goal is the Marcus-SPOC runtime orchestrator and its production Gary dispatch path. This story is valid only because Irene literal fidelity must be honored by the real SPOC Gary path. Do not design for proofing convenience, do not mutate approved styleguide registry records as a workaround, and do not claim broader `fidelity-L1-per-slide-text-mode` closure from this slice.

## Standing Watchpoints (this arc)

1. **Spec approval and party governance.** The visible goal requires operator approve/edit on the draft spec and a fully spawned BMAD party-mode round using real personas before further design/green-light concurrence. General-purpose stand-ins do not satisfy the gate.
2. **No styleguide-registry mutation workaround.** Approved guide records, including the classic condense guide and the classic-preserve sibling, must not be edited in place to make the symptom disappear.
3. **Production seam only.** The implementation must affect `build_gary_briefs` and `generate_gamma_variants`; legacy mixed-fidelity helpers are reference only.
4. **Literal cohort contract.** `literal-text` and `literal-visual` form one literal cohort for this slice: API `text_mode=preserve`, and `text_options.amount` is absent, not `null`, `0`, or an empty placeholder.
5. **Creative cohort isolation.** Creative and untagged slides must keep the selected styleguide `text_mode` and `amount`; no whole-deck preserve bleed.
6. **Cohort-scoped dispatch.** Mixed decks require separate Gamma calls with cohort-scoped `_input_text` and `num_cards=len(cohort)`, then reassembly by stable `slide_id` / original brief order, not fuzzy title matching across cohorts.
7. **Fail-loud honor failure.** If a literal-tagged slide cannot be dispatched with preserve, including the in-scope studio+literal case, the path must raise before sending a condense fallback.
8. **RED-first tests are load-bearing.** T1-T8 should fail for the intended pre-fix reasons before production edits, then pass against next-layer observable behavior such as carried slide fields and captured Gamma-client kwargs.
9. **Literal-visual scope discipline.** This slice is text-preserve only for `literal-visual`; image URL injection and broader literal-visual payload policy remain out of scope.
10. **Claim envelope.** Closeout may mark `irene-text-literal-supersedes-styleguide-truncation` met only if the focused behavior is proven. It must leave `fidelity-L1-per-slide-text-mode` open/yellow with residual scope explicit.
11. **Live/seam validation.** Focused pytest/ruff is necessary but not sufficient if the active story claims live seam exercise; the evidence must show each authored seam was exercised honestly.
12. **Stray hygiene.** Existing untracked goal/spec/session artifacts must be deliberately banked or explicitly left local; do not sweep unrelated runtime/evidence strays into this story.

## Poll Log

### SOP-000 - baseline / first shadow report - 2026-07-09T13:58:46-04:00

**Scope reviewed:** `git status --short --branch`, recent git log, canonical shadow-monitor examples in `_bmad-output/implementation-artifacts/`, `goal-irene-literal-preserve-2026-07-09.txt`, draft spec `_bmad-output/implementation-artifacts/spec-irene-literal-supersedes-styleguide-truncation.md`, and repo references to `irene-text-literal-supersedes-styleguide-truncation` / `fidelity-L1-per-slide-text-mode`. No tests were run. No production/test/runtime files were edited by this monitor; this ledger entry is the only write.

**Current repo state:** branch `dev/lesson-planning-2026-07-09` is at `c6871da0` (`Merge branch 'dev/workbook-2026-07-06'`) and tracks `origin/dev/lesson-planning-2026-07-09`. The only visible untracked session files before this ledger were:

- `_bmad-output/implementation-artifacts/spec-irene-literal-supersedes-styleguide-truncation.md`
- `goal-irene-literal-preserve-2026-07-09.txt`

No tracked production-code or test diff is visible yet (`git diff --stat` empty at this poll).

**Positive baseline signal:** the draft spec is already strong and aligned with the S8 close envelope: binary creative/literal cohorting, preserve + amount-absent for literal slides, cohort-scoped input, stable `slide_id` reassembly, studio+literal fail-loud, no approved styleguide registry mutation, and no claim that `fidelity-L1-per-slide-text-mode` is fully closed. The goal file also correctly requires BMAD workflows, fully spawned party gates, live/seam validation, shadow-monitor consultation, and final party concurrence.

**Main risk at baseline:** the repo has a spec-shaped and goal-shaped start, not an implementation. There is no evidence yet of operator approve/edit, no new party record beyond the spec's embedded comment, no RED-first test output, no production seam edit, no focused green output, no ruff output, and no closeout/inventory disposition. This is expected for a first poll, but it means no implementation claim is currently scoreable.

**F-0001 [P1] Governance evidence is ambiguous until the operator approval and real-party record are externally visible.** The spec contains an HTML comment saying a 4-seat party green-light happened and that a prior generalPurpose-only round was voided, while the goal says the immediate next task is still operator approve/edit and a fully spawned BMAD party before further green-light/design concurrence. That may be a harmless sequencing artifact, but the active driver should make the gate state explicit before dev dispatch: either mark the spec operator-approved and cite the fully spawned party record, or keep it in draft and stop before implementation.

**F-0002 [P2] The S7 Phase-2 monitor ledger referenced in `SESSION-HANDOFF.md` is not present in this checkout.** The handoff names `_bmad-output/implementation-artifacts/claude-shadow-monitor-s7-phase2-2026-07-08.md` as active/untracked, but this file is absent locally. This does not block the Irene literal story, but any closeout that says all relevant shadow-monitor notes were consulted should either cite this new ledger and the canonical-arc ledger actually present, or explain that the referenced S7 Phase-2 ledger was unavailable in this checkout.

**Watchpoint verdicts at baseline:** WP2, WP3, WP4, WP5, WP6, WP7, WP8, WP9, WP10, and WP12 are not violated by current visible state. WP1 is open pending explicit approval/party evidence. WP11 is open pending seam/test/live evidence.

**Recommendation to Grok/Cursor lane:** before production edits, resolve the spec approval state and party-record ambiguity, then proceed RED-first on T1-T8. The first implementation poll should show failing tests for the intended reasons and no styleguide registry mutation. Do not claim progress beyond "spec/green-light preparation" from the current repo state.

**Verdict: MONITOR INITIALIZED / WAITING ON GATE EVIDENCE.** The story direction is product-valid and the draft spec has the right constraints, but the implementation is not yet visible or scoreable.
