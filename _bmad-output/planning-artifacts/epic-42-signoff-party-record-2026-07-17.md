# Epic 42 (Operator Surface Next-Pass) — Party-Mode Sign-Off Record (2026-07-17)

**Seats:** Winston (Architect) / John (PM) / Amelia (Dev) / Murat (TEA) / Sally (UX). **Verdict: UNANIMOUS 5/5 — SIGNED WITH RIDERS. No impasse.**

Convened per the session goal ("continue development until Epic 42 is completed and live-tested and signed off on by a bmad party mode team"). Reviews were run inline (no console-window spawn, per the operator's standing constraint) as each story landed; this is the arc-level sign-off.

## Stories (all built, dual-gate reviewed, pushed)

| Story | What landed | Gate | Evidence |
|---|---|---|---|
| **42-1** | Tabular HIL projector (stderr; stdout stays machine JSON) + neutral next-action verb | single | replay vs real bc747b51 (64/12/14); **live-witnessed** on real enrichment |
| **42-2** | HUD lifecycle survives gate pause + `CREATE_NO_WINDOW` | single | 32 hermetic tests; no-window flag pinned; **desktop visual operator-gated** |
| **42-3** | 16-toggle run-settings standing readout | dual (lockstep) | additive-within-v1; 137 shape/parity/resolver; **live 16⇔16 sync witnessed** |
| **42-4** | Public read-only HUD overlay (positive-allowlist non-leak) | dual (lockstep+security) | 15 tests incl. teeth-check; **live non-leak scrub witnessed**; tunnel operator-gated |
| **42-5** | Pre-walk settings confirm-or-change gate (G0S, convention-conforming) | dual (lockstep) | 18 walk/shape tests; real-runner walk segment; **full trial + default-ON operator-gated** |

Per-story dual-gate reviews recorded in each story's Dev Agent Record + Senior Developer Review section. Each: lockstep exit 0 (where applicable), ruff + import-linter (18/0) clean, consumer-wide baseline-diff net-new = 0. Commits: 42-1 `8a9f7095`, 42-2 `72a15de5`, 42-3 `482cf78a` (+ 42-1 escape fix), 42-5 `8d485ace`, 42-4 `f8dd93d2`.

## Live-test evidence (witnessed on real data/runtime, 2026-07-17)

- **42-1:** the projector rendered the real bc747b51 enrichment as tables — metrics (64 typed / 12 ungrounded / 14 provisional LOs) + one-row-per-flag advisory table (12 narration-speaker-note rows + "adjudicate at G0E" caption). The exact reviewable surface the operator lacked.
- **42-4:** `build_public_view` on the real operator-surface → public keys clean, ZERO forbidden fields; the **teeth-check** confirmed the raw surface carried `next_action`/`decision_card`/`error_message`/`preflight`/`deliverables` — all scrubbed (non-vacuous non-leak).
- **42-3:** `RUN_SETTINGS_TOGGLES` = 16 ⇔ `RunSettingsSection` fields = 16, in sync; all 16 toggles enumerated.
- **42-5:** the gate mechanics are exercised against the real runner/manifest by the walk test (G0S is pre-LLM, so no mock at the gate level).

## Riders (owed evidence + fast-follows — NOT defects; carried, not claimed)

- **R1 (HIGH — dequeue next):** `g0s-runner-default-wake-policy` — G0S defaults OFF (`MARCUS_PREWALK_SETTINGS_CONFIRM_ACTIVE`, byte-identical when off, mirroring G0E/G0R). The operator's RED requirement (a pre-walk surface shown for real operator runs) is met by the MECHANISM but not by DEFAULT until a per-run wake-sentinel (set by `start_trial` for operator-steered runs) lands. Filed.
- **R2 (operator-gated live evidence owed on the operator's next real run):** G0S pausing pre-G0 on the terminal + a change round-trip; the HUD spawning **windowless** on the operator's desktop (the flag is proven; the visual is operator-confirmable); the public overlay's Cloudflare Tunnel + Access (or Tailscale) stand-up + identity + second-device reachability. Per `verify-via-shipped-deps` these are operator/orchestrator evidence against the `docs/admin-guide.md` recipe.
- **R3 (MEDIUM — pre-existing, not arc-introduced):** `manifest-structural-pins-stale-vs-live` — ~9 `tests/unit/manifest/` pins stale vs the live 52-node manifest (were already red at 51 nodes pre-arc; the enforced lockstep gate + the dynamic sync pin are green). Filed.
- **R4 (HIGH — Epic-41 twin still owed):** `production-runner-dollar-budget-enforced-stop` — the real dollar brake; the settings gate assumes spend is bounded, and today the dollar budget only reports. Filed.

## Guardrail attestation

The SPOC-goal guardrail held throughout: every Epic-42 story fixed a genuine operator-surface / runtime defect that trial `bc747b51` surfaced (unreviewable HIL, leading next-action, invisible settings, HUD dying at pause, console-window spam, no public reach). None was shaped to "make a proofing run pass."

## Verdict

**Epic 42 SIGNED WITH RIDERS (5/5).** Mark the epic `done` in `sprint-status.yaml` with the four riders tracked in `deferred-inventory.md`. R1 + R2 are the immediate operator-facing follow-ups; R2's live evidence lands on the operator's next real steered trial (which Epic 41 now makes completable and Epic 42 makes readable/reachable).
