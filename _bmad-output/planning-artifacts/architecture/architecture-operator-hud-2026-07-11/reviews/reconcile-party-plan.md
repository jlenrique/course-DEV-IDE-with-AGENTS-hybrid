# Reconcile — Party Assessment & Plan vs ARCHITECTURE-SPINE.md

Input: `_bmad-output/planning-artifacts/hud-revival-party-assessment-and-plan-2026-07-11.md` (§5.3 a–d mandates, §5 evidence strategy, §4 collision resolutions)
Spine: `_bmad-output/planning-artifacts/architecture/architecture-operator-hud-2026-07-11/ARCHITECTURE-SPINE.md`
Reviewer pass: 2026-07-11 (input-reconciliation).

## §5.3 architecture mandates (a–d)

| Mandate | Verdict | Notes |
|---|---|---|
| (a) Runtime-owned operator-surface projection contract — one versioned document, written by **BOTH walks** (two-walk gotcha), shared Pydantic model + dual JSON-Schema shape-pins so producer changes fail producer tests | **LANDED** | AD-1 (single versioned document, Pydantic, sole input), AD-2 (`_persist_envelope` choke-point covers both walks by construction, and closes the ~line-3501 bypass — stronger than the mandate), AD-4 (dual pins: byte-identical schema pin + producer↔consumer parity, additive-only within v1). |
| (b) Served-vs-static — v1 default static + mtime/etag 2–5s poll; SSE only as Tier-1 follow-on IF gate-verdict flow independently justifies a served operator API | **LANDED** (with a noted, justified supersession) | AD-6 adopts the poll cadence, ETag gating, and preserves the SSE deferral condition verbatim (Deferred §). The spine chose a **served GET-only FastAPI page** over the party's static-file default — a deviation, but one the brief itself authorizes (Principle 3: "local server approved; its readiness is itself a pre-flight item", operator-pinned), and AD-6's no-mutation rule keeps Splinter's served-API concern fenced. Recorded as resolved-by-later-input, not drift. |
| (c) Retire-path for legacy bundle-gate/coordination.db readers + the silent wrong-run fallback | **LANDED** | AD-8: coordination.db reader, `_find_latest_bundle`, and the bundle-gate yaml pipeline are **deleted, not bypassed**, as their own retire story; wrong-run fallback replaced by explicit binding + REFUSE-TO-RENDER. |
| (d) Perf/traps budget — 525KB run.json mtime-gating, LangSmith call out of the data path | **PARTIAL** | The *consumer-side* traps are resolved by construction, stronger than mandated: AD-3 bans run.json parsing, coordination.db, and LangSmith calls from the data path entirely (trace URL rides in the projection). But the mandate said perf/traps **budget**, and two budget halves never landed: (1) **producer-emission cost** — the projection is assembled and atomically rewritten on *every* state transition in both walks, sourcing cost-report, roster activity, health, and state-trace data; no ceiling, no lazy-section rule, no statement that emission must not slow the runner. (2) **projection file-size budget** — with per-reading history and append-only state-trace events riding inside it (EXPERIENCE §Projection Demands), the single document grows unboundedly across an hours-long run; the spine risks re-creating the 525KB-run.json trap in the very file meant to escape it (cross-ref reconcile-ux.md). Also unstated: the L2 golden-fixture strategy silently requires an injectable run-dir root in the new reader (`read_operator_surface()`), i.e., the party's named "injection-seam fix" — dissolved by the rewrite in spirit but never pinned as a requirement on the new seam. |

## §5 evidence strategy

| Item | Verdict | Notes |
|---|---|---|
| L1 enum contract test — set-equality against envelope status vocabulary | LANDED | AD-5 (explicit set-equality vs `production_trial_envelope.py`), AD-13. |
| Reverse tripwire — envelope status-model files added to `block_mode_trigger_paths` | LANDED | AD-5 + AD-14: Tier-2 manifest edit, party-gated, bundled as its own pre-dev story — exactly the plan's governance shape. |
| L2 golden run-dir fixtures per pause class + one legacy-shaped dir rendering "unrecognized" | LANDED | AD-13, verbatim including the legacy-dir fixture. |
| L3 one first-run-stands live witness per pause class, promoted into the L2 golden set (rewind-recover golden-bundle pattern) | LANDED | AD-13, including promotion. |
| DoD per story names its witness set | LANDED | AD-13 final clause; plus xdist hygiene (serial/live marks) added beyond the plan. |
| Risk R1 — wrong-but-plausible state during a live paused run (High/High), mitigated by L1+L2+zero-lie | LANDED | AD-13 "Prevents" header cites R1 by name; AD-3/AD-4/AD-5 carry the zero-lie leg. |

## §4 collision resolutions

| Resolution | Verdict | Notes |
|---|---|---|
| **Retarget-not-rebuild** — keep render shell + ~98 pins; replace data layer | LANDED | AD-12: render shell + urgency auto-expand carried forward; thin `read_operator_surface()` replaces retired readers; Dev-Cycle/M5 retired with pins; render stays a pure seam. |
| **Contract-is-the-product** (Splinter-via-Winston: data layer = thin consumer of runtime-owned projection ≈ 80% of the honest-thin-view) | LANDED | The spine's entire paradigm statement (single-writer projected read model) + AD-1/AD-3; the contract package is the dependency root of the layer diagram. |
| **Split-brain absorption** — HUD read-only confession; **any future actionable affordance requires a fresh party gate** | **PARTIAL** | The structural half is over-delivered: AD-6 makes any mutation route a defect "regardless of intent". But the *governance rider* — a fresh party gate before any future actionable affordance — is not restated; the Deferred SSE/served-operator-API bullet gates on the gate-verdict flow justifying it, without naming the party gate as the mechanism. One clause in Deferred ("requires a fresh party gate per plan §4") preserves the ratified escalation path. |
| **"Essential" disposition (Level)** — usage-witness criterion: operator completes a full trial using only HUD + verdict CLI; **v1 pays for itself in the very next production trial or we cut deeper** | **PARTIAL** | Same finding as reconcile-brief.md SC5: the AD-13 evidence ladder has no arc-level witness slot; neither the usage witness nor the next-trial payoff test appears in the spine. Correctly an epics/DoD concern in part, but the spine defined the evidence ladder and stopped one rung short of the criterion that settled the party's hardest challenge. |
| PRD→brief; UX two-spine; architecture non-negotiable | CORRECTLY-DEFERRED | Process-chain decisions, already executed upstream; no spine residue expected. |

## §5.4 named stories (context check only — epics-phase property)

Manifest-lockstep update (AD-14, pre-dev story), M5 panel retirement (AD-12), legacy-reader retirement (AD-8) all pre-carried in the spine. 4-failure test disposition: correctly left to epics. Injection-seam fix: see §5.3(d) PARTIAL — dissolved by the rewrite but the equivalent requirement on the new reader is unstated.

## Tally

LANDED 10 · PARTIAL 3 (§5.3(d) perf/size budget + seam; split-brain party-gate rider; usage-witness/next-trial payoff) · DROPPED 0 · CORRECTLY-DEFERRED 2.
