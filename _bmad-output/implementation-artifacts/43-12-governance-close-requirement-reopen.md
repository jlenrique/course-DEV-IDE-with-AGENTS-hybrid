# Story 43-12 — Governance close: reopen the requirement, assert the ratchet empty, retrospective

**Epic:** 43 · **Slab:** 4 · **Status:** ready-for-dev · **Gate mode:** single-gate (governance/docs + one assertion). **Executed by the orchestrator** (governance work, not a dev-agent code story).

## Purpose

Close Epic 43 honestly: prove the coverage ratchet is fully drained, reopen/correct the falsely-closed requirement with per-surface ACs, and run the retrospective.

## Acceptance criteria

**AC-1 — ratchet drained (allowlist empty).** Confirm `KNOWN_UNRENDERED_ALLOWLIST == frozenset()` (43-9 drains the last two entries). The coverage-ratchet test (43-10) with the empty-allowlist assertion is green — this is the mechanical proof that EVERY gate content type in the canonical set is registered (or was honestly de-scoped). Add/confirm an explicit `test_allowlist_is_empty_at_epic_close` (the 43-12 hook 43-10 documented).

**AC-2 — reopen/split `hil-operator-surfaces-must-be-tabular`.** In `_bmad-output/planning-artifacts/deferred-inventory.md`, update the entry (currently marked ✅ FILED as 42-1): record that the requirement's "Apply to" list was satisfied by Epic 43 across ALL named surfaces (G0 directive, G0E/G0R enrichment, every gate content type), each now its own registered renderer or honest de-scope. Correct the 42-1 record HONESTLY — not a retroactive edit of 42-1's scope, but a truthful "42-1 delivered the G0/G0E slice; Epic 43 completed the requirement across all ~15 surfaces." Cross-reference the party record + the static-validation S-2.

**AC-3 — Epic 43 retrospective.** Run `bmad-retrospective` (or author the retrospective artifact) — lessons: the gate→content_type bridge; the RED-first coverage ratchet as the anti-subset-regression mechanism; the synthetic-fixture-from-real-model discipline; the two production observations surfaced (section-11-display-voice-candidates-model-binding-mismatch; the G1A/G1.5/G4B/G5 gates not being in the woken pause set). Consult the deferred-inventory per the retrospective governance.

**AC-4 — close the epic.** Mark `epic-43-hil-surface-tabular-coverage: done` in sprint-status.yaml with the closure summary. Update the epic spec Status to CLOSED.

## Definition of done

Allowlist empty + asserted; requirement reopened/corrected honestly with per-surface coverage; retrospective done; epic marked done. Ready for `bmad-code-review` on the (governance-only) diff if any code changed.
