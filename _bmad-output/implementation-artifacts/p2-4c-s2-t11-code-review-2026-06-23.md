# P2-4c S2 — Claude T11 Code Review + Close Record (2026-06-23)

**Outcome:** HAND BACK to Codex (party-mode 5/5, no impasse). S2 did NOT flip done. Codex's S2 dev code stays UNCOMMITTED for re-work; Claude's T11 diff is review/governance docs only.
**Story:** P2-4c S2 (per-element image-role tier emission). **Base HEAD:** `e75c700`.

## Battery (independently reproduced)
- S2 + reading-path slice: 99 passed. Lockstep exit 0. ruff clean. lint-imports 15/0.
- **Contracts: 14 failed = SAME ambient set** on clean HEAD (baseline-diff holds; zero new reds from S2). Enum/fields additive (image_roles/image_role_flags/role_tier nullable; nothing removed).
- Spot-checks: `fold_scored_tier("2_5")→"2"`, `("3")→None` (quarantine); κ + soft-middle κ + confusion matrix present; `role_tier` closed-Literal validated at the payload boundary; `image_roles` populated.

## 3-layer review (deduplicated)
**Acceptance Auditor: PASS-WITH-NITS** (all 8 ACs met empirically; tier-3 excluded from scored top-1; role_tier None-not-defaulted; **kind:diagram-≠-instructional gate holds — overrides even an explicit perceiver `role_tier=3`**, the S1 lesson). But the Hunters found defects the green suite never exercises:

**MUST-FIX (3):**
- **MF-A** — `image_roles` drops bbox-less elements → index-misaligned with `visual_elements`; S3 role-override consumes positionally → mis-maps every element after a gap. Live-path, silent wrong-data. (Both hunters MUST.)
- **MF-B** — the κ agreement harness DROPS all tier-3 pairs → tier-3 disagreement (3↔2 over-call) invisible to κ + confusion matrix; violates AC-5/T6; a systematically-wrong perceiver reports κ=1.0.
- **MF-C** — κ returns 1.0/`passes=True` on empty or all-quarantined scored sets (vacuous false-green in the promotion gate). Same class as the S1 vacuous-gate hand-back.

**SHOULD-FIX:** SF-1 perceiver `role_tier` bypasses geometry gates (only size-lock + tier-3-no-label gate perceiver values); SF-2 invalid `role_tier` silently dropped (no flag); SF-3 non-empty all-bbox-less still raises (empty-elements degradation half-closed); SF-4 icon-set cue unimplemented → icons >0.05 mis-tier to 2 (pollutes the scored key). **NITs:** borderline-stability fixture asserts a value; dead `_has_opposition_cue` tail (pre-existing S1); magic constant; substring icon match.

## Party-mode CLOSE gate — 5/5 HAND BACK (no impasse)
Winston/Murat/Mary/Amelia/John. All 5: **MF-A blocks close + needs a Codex fix** (live-path contract violation). MF-B/MF-C fold into THIS hand-back **3–2** (Murat/Amelia/Winston: same vacuous-gate class as S1, near-zero marginal cost, "won't bless deferring a vacuous-pass on an acceptance harness") over deferring (Mary/John: harness not-yet-wired) — dominant, not an impasse (folding satisfies the defer camp's "must-fix-before-promotion" earlier). SF-2 folds; SF-4 defers to P2-4b; SF-1/SF-3 documented.

## Disposition
NEXT = operator dispatches Codex on `codex-remediation-prompt-p2-4c-s2-t11.md` (one cohesive 2-file diff, RED-first) → Claude re-T11. Binding pass-bar = 4 RED-first fixtures (index-alignment / tier-3-disagreement-visible / empty→passes=False / invalid-tier-flagged) + baseline-diff attestation. Governance: anti-pattern **H2** harvested (`dev-agent-anti-patterns`); SF-4 + κ-harness-NOT-WIRED status filed to deferred-inventory.
