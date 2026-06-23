# P2-4c S3 — Claude T11 Code Review + Close Record (2026-06-23)

**Outcome:** **CLOSE-WITH-RIDERS** (party-mode 5/5, no impasse). S3 build flips done. The riders are doc/governance corrections + filed follow-ons (Claude T11 authority) — NOT a Codex code hand-back; the S3 mechanism is sound.
**Story:** P2-4c S3 (triggered gpt-5.5 escalation tuple-delta call). **Base HEAD:** `70a5bf9`.

## S3 build — meets all 8 ACs, additive, LIVE-PROVEN
New `scripts/utilities/reading_path_escalation.py` + `state/config/reading-path-escalation-lexicons.yaml` + test; S1/S2 untouched (callers invoke `run_s3_escalation()` after the tuple). Upstream-frozen escalation predicate; always-on `escalation_ledger`; single-shot `make_chat_model(gpt-5.5)` call (test injects a double via the `client=` **DI param**, NOT a production mock); parse-seam + merge; malformed→degrade; call-count fence (1/escalated-slide); no-gold/top-1 conditioning. Battery 115/129 green; lockstep 0; ruff; lint 15/0; contracts 14-ambient (zero new reds). **Live smoke RAN** (Claude has the key Codex lacked): the live gpt-5.5 path works end-to-end — **0 degraded rows** over the held-out escalations. No-mocks proof-of-live satisfied (not a believed-green fixture-backed contract).

## What the LIVE dry-run exposed (the synthetic tests hid these)
Running the built classifier + live S3 over the 14 held-out (post-S1/S2 classify):
1. **Escalation rate = 13/14 = 0.93** — `callout_kind_present` fires on 13/14 (most slides have a callout element). Far over the 20% ceiling. The over-escalation tripwire is a TEST on a synthetic ledger — NOT wired to the real runtime rate.
2. **Built deterministic classifier vs gold = primary-key 0.071** (macro 50%, image_role 21%) — BUT on **STALE perceptions** captured 2026-06-22, before S2's `role_tier` prompt existed → no perceiver tiers → crude geometry backfill (defaults decorative photos to tier-2; gold says tier-1). An un-fair number; a fair P2-4b needs **fresh re-perception**.
3. **S3 escalation changed 0 primary keys** — by design it only does `two_pane`-upgrade + callout/process/role-override; it CANNOT repair a wrong macro_layout (multi_column↔card_grid↔single_text_block). Geometry macro at 50% + no general macro-override = a hybrid coverage gap (owned by S1-geometry; adding macro-override to S3 would invert hybrid-(c) → architecture-tier change — Winston).
4. **🔴 BELIEVED-GREEN: the "0.93 PASS" measured the catalog-approach (Claude-in-loop labels), NOT the built classifier.** It had propagated into STATE-OF-THE-APP + the P2-4b spec + the gold doc as "0.93 / one-command." Corrected this session (R3).

## Party-mode CLOSE gate — 5/5 (no impasse): CLOSE the S3 build + binding riders
Winston/Murat/Mary/Amelia/John. S3-the-mechanism is sound + meets spec; the findings are spec-deferred calibration ("permissive start, calibrate after Trial-1"), S1-geometry, and a believed-green doc error — none are S3-build defects. Binding riders:
- **R1** — de-mask the over-escalation tripwire test as predicate-arithmetic-only (annotated); file runtime-rate-wiring as a P2-4b follow-on.
- **R2** — file follow-ons: P2-4b = a real **4-leg calibration** (re-perceive under role_tier → recalibrate predicate → measure honest built-classifier accuracy → contingent macro/image_role improve); `reading-path-s1-geometry-macro-accuracy` (the 50% macro floor owns finding #3); `reading-path-s3-escalation-recalibration` (tighten `callout_kind_present` + wire the ≤20% ceiling to the real ledger); macro-override = an architecture-tier follow-on (party-gated if pursued).
- **R3** — retire the believed-green "0.93 / one-command" claim everywhere; bind every metric to `(subject, substrate-freshness)`. Done: STATE-OF-THE-APP, P2-4b spec, gold doc corrected.
- Anti-pattern **H3** harvested (validation metric measures the human/LLM-in-loop approach, not the built artifact).
- Named build-state (not blockers): 93%-real-escalation; 0.071-on-stale.

## Disposition
S3 flips done. **P2 epic is NOT closed** — P2-4b (the real 4-leg calibration) is now the live frontier, gated on fresh re-perception. The reading-path tuple classifier is BUILT (S1+S2+S3) but its honest accuracy is UNMEASURED.
