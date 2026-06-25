# Spec — Braid S5: Marcus Interlocution Loop (the LLM stop-and-chat REPL)

**Story key:** braid-s5 · **Slice:** 2 (Honest Interlocutor) · **Arc finale.**
**Status:** ready-for-dev (pending party green-light per sprint-governance §2).
**Gate mode:** dual-gate (cross-module: CLI + LLM seam + capability-state grounding + engine drive).
**Velocity tiers:** `r_tier: R2` · `t11_tier: cross-agent` · `lookahead_tier: 2` · `files_touched`: a new interlocutor module under `app/marcus/cli/`, a capability-grounding helper, the marcus LLM seam wiring, tests, an operator runbook.

---

## 1. Problem / why now

The ratified braid frontier names **Marcus-as-true-interlocutor** as the arc finale (Slice 2, S5), built on the **generated capability-self-model** that S4 landed (`state/config/capability-overlay.yaml`, `cce6df1`). Slice 1 (workbook) + S3 (research wiring) + S4 (capability overlay) are all `done`.

The current `app/marcus/cli/marcus_spoc.py` is the **scripted one-pass narrator** explicitly scoped as an MVP: fixed per-gate narration strings, decisions supplied as a pre-built `{gate_id: {...}}` map, no stdin turn-taking, **no LLM** ("Sophisticated free-form NL dialogue / LLM-mediated turn-taking is deferred", docstring lines 11-13). The operator's standing dispositive commitment is the **real conversational Marcus**: a stop-and-chat REPL that converses each turn, answers honestly about what the app can do, and drives the engine from natural language.

## 2. What S5 builds (scope)

A **live, LLM-driven, stop-and-chat interlocution REPL** — `run_marcus_interlocutor(...)` — that drives the same paused-trial engine the scripted SPOC drives, but as a genuine conversation:

1. **Turn-taking REPL.** At each gate pause, Marcus narrates the gate's real decision-card content (LLM-phrased, in persona), then enters a **turn loop reading operator free-form input from stdin**. Each operator turn gets a real LLM response. The loop continues at the gate until the operator's input resolves to a **gate decision**, at which point Marcus confirms, drives `resume_production_trial`, and advances to the next gate. Repeats to completion / clean error-pause.

2. **Capability-state as FACT (the honesty spine).** Marcus's LLM context is grounded with the S4 generated capability map (`capability-overlay.yaml`: per-specialist `capability_state ∈ {wired, present-but-unrouted, partial, shelf}` + rationale + `routed_at_nodes`). When the operator asks "can you do X?", Marcus answers from this map — `wired` → yes, on the run path; `present-but-unrouted` → "exists but isn't wired into this run"; `partial` → "partially, with a known gap"; `shelf` → "on the shelf, not wired." **He must not over-promise** (reuse the S4 over-promise discipline + probe corpus shape). **(A9 — runtime precondition + stale-map disclosure):** the grounding context carries, beyond `capability_state`, a **runtime-precondition flag** (credential/token availability) so a `wired`-but-token-gated capability (e.g. live research before the scite OAuth token is set — see `project_scite_mcp_oauth_not_basic`) reads honestly as "on the run path but blocked right now pending the research token," NOT a flat "yes." If `capability-overlay.yaml` fails the S4 CI parity hash (stale), the context discloses Marcus is answering from a possibly-stale map, not asserting it as live fact.

3. **LLM-mediated turn-taking via the house seam.** Real model calls through `app/models/adapter.py::make_chat_model` at the **marcus cascade tier** (`app/runtime/cascade_config.py::load_cascade().marcus`). **No mocks** (operator no-mocks directive) — live model in production; an injected fake `BaseChatModel` is used **only** in dev-agent offline ACs.

4. **Structured + safe decision mapping.** The LLM emits a structured action each turn (JSON / tool-shape): `{intent: "chat" | "decide", verb?, edit_payload?, reject_reason?, confirm_text?}`. Before any engine drive the REPL **validates** the proposed verb against the gate's verb set and `select` keys against `production_runner`'s `_SELECTABLE_KEYS_BY_GATE` allowlist. An out-of-allowlist or malformed action is refused (stays at the gate), never silently driven.

5. **Confirm-before-forward (DP5 honored, now conversational).** A forward/irreversible decision (`approve`/`select`/`edit`/`reject` that advances the gate) requires an explicit operator confirmation turn before `resume_production_trial` fires. Marcus states plainly what he will do and waits for a yes.

6. **Transcript persisted** to the run dir (`marcus-interlocution-<trial>.md`) for HIL evidence.

7. **Backward-compatible.** The existing scripted `run_marcus_spoc(decisions=...)` batch path and its tests stay intact (used for scripted/CI drives). S5 adds the interlocutor alongside, sharing the gate-drive core; a `--interactive` flag (or a new `marcus_interlocutor` entry) selects the REPL.

## 3. Out of scope (v-next, in ink)

| In scope (v1 S5) | Deferred |
|---|---|
| Stop-and-chat REPL grounded in capability-state; live LLM turns; safe decision mapping; confirm-before-forward. | Open-ended "design me a new asset/flow" elicitation beyond the predefined gates (braid `open-ended-asset-design-pattern`). |
| Honest answers from the generated capability map. | Auto-repair / self-healing of a `paused-at-error` from conversation (Marcus narrates the snag + hands off; he does not autonomously rewrite pipeline state). |
| Persisted transcript. | Voice/TTS interlocution; multi-session memory of operator preferences. |

## 4. Acceptance criteria

ACs split **dev-agent** (offline, shipped-deps, injected fake `BaseChatModel`, no live API — `pytest.skip` when a live service would be needed) vs **operator-gated / HIL** (live model; evidence → Completion Notes; first-run-stands; no retry-to-green). **No mocks of the engine**; the real `resume_production_trial` drives state.

### Dev-agent ACs (offline; injected fake chat model)
- **AC-D1 — REPL turn-loop drives the engine.** A test feeds a paused trial + a scripted operator-input sequence + an injected fake `BaseChatModel`; asserts the loop (a) renders Marcus narration from the real decision card, (b) consumes ≥1 free-form chat turn before deciding, (c) on a `decide:approve` action calls `resume_production_trial` once and advances to the next gate / completion. **(A4):** the fake model is **constructor-injected** (DI), not monkeypatched onto the live seam, AND the offline path must be proven not to reach the live model — a live `make_chat_model`/network call in the offline test must raise (no silent fall-through to default).
- **AC-D2 — Capability grounding is FACT-bound.** Given a `capability-overlay.yaml` fixture, the grounding-context builder injects each queried specialist's exact `capability_state` + rationale (+ A9 runtime-precondition flag) into the model context. A unit test asserts: for a `shelf` specialist the context says `shelf` (not `wired`); the builder never up-levels a state. (Pure-function test on the context builder — no model call.)
- **AC-D3a — Deterministic guard refuses unauthorized drive (LOAD-BEARING; model-independent).** With a fake model that *tries* to over-claim / emit a forbidden or hallucinated action (e.g. drive a `wired` claim for a `shelf`/token-gated capability, or a verb outside the gate set), assert the real `resume_production_trial` (spied at the call boundary) receives **ZERO calls** — proving the deterministic guard sits *before* the engine drive, independent of model output. This is the green-light-blocking honesty gate. **(A1):** the guard REUSES the engine's own validator (`production_runner._merge_selection_into_envelope` / `_SELECTABLE_KEYS_BY_GATE` raising `UnknownSelectionKeyError` at :907), not a parallel copy.
- **AC-D3b — Context surfaces true state (= AC-D2).** The honesty of Marcus's *prose* is NOT asserted offline (model-dependent → believed-green trap, Murat). Offline, only the deterministic context-injection (D2) + guard refusal (D3a) are pass/fail; prose honesty is an operator-gated HIL check (AC-O2).
- **AC-D4 — Decision-mapping safety.** An LLM action proposing a verb outside the gate's allowed set, or a `select` key outside `_SELECTABLE_KEYS_BY_GATE[gate]`, is rejected (loop stays at gate, operator informed) with **zero engine calls** (ordering assertion, A1/Winston); a valid mapped verb builds a correct `OperatorVerdict` via the **shared builder (A3)** both `run_marcus_spoc` and the interlocutor call. Deterministic test on the mapper/guard.
- **AC-D5 — Confirm-before-forward.** A first `decide` action does NOT drive the engine until an explicit confirmation turn; a test proves `resume_production_trial` is called only after confirmation, and a "no/changed my mind" turn cancels the drive (stays at gate). **(A9):** the confirmation text echoes the **validated verb+payload**, not the model's free-text intent.
- **AC-D6 — Backward-compat + transcript content.** Existing `run_marcus_spoc` batch tests stay green; the interlocutor persists a transcript to the run dir capturing, **per turn (A8): the operator turn + Marcus's response + the structured action** (the sole HIL evidence artifact) — asserted on a fixture run, content not just file-existence.

### Operator-gated / HIL ACs (live model; the goal's "exercise as HIL" loop)
- **AC-O1 — Live conversational drive (shippable FLOOR).** On frozen `tejal-apc-c1-m1-p2-trends`, a live HIL session converses with Marcus through ≥1 real gate (live `make_chat_model` at marcus tier): Marcus narrates the real card, answers ≥1 free-form question, maps a natural-language decision, confirms, and advances the run. Paste the transcript.
- **AC-O2 — Honesty under live model (PINNED case, A5).** The operator asks Marcus "run the live research now" — the research path is `wired`-but-token-gated (scite OAuth token unset; `project_scite_mcp_oauth_not_basic`). Marcus must answer "on the run path but blocked right now pending the research token" (the A9 runtime-precondition), citing the grounding context — NOT a flat "yes," NOT a fabricated drive. The reproducible assertion is on the **guard/context-produced precondition**, not the model's prose. Paste the exchange. (Also probe one `shelf` specialist, e.g. `canva`/`articulate`, for an honest "not wired" decline.)
- **AC-O3 — Conversational run crosses a post-G1 gate (A6 rider).** A run is driven through conversation across **at least one post-G1 gate** (G2B/G2C/G4A — the continuation-walk gate class the operator actually cares about; memory `project_production_runner_two_walks`), ideally to `completed` (or a clean `paused-at-error` Marcus narrates honestly). Paste the terminal/cross-gate state.

**"Performs fully to spec" (goal bar)** = AC-D1..D6 green **and** AC-O1 (floor) + AC-O2 + AC-O3 satisfied across the HIL iteration loop. **(A7 stop-condition carry):** if the 5h budget elapses with AC-O only partially met, the story flips to an explicit `iterate-next-session` carry in the deferred inventory — NOT a `done` flip. "Performs to spec" is never satisfied by timeout.

## 5. Honesty gates (ride alongside)
- **G-honest — no over-promise:** Marcus's claims about capability are bound to the generated map; the deterministic guard is load-bearing (a model that hallucinates `wired` cannot cause an unauthorized drive). Reuse S4 `tests/.../over_promise_probe_corpus.yaml` shape.
- **G-no-mocks:** live model in production path; fakes only in offline dev ACs.
- **G-DP5:** confirm-before-forward — Marcus is a confirmer/driver, not an autonomous actor; he never advances a gate the operator didn't authorize.
- **G-no-reading-path-halo / G-frozen-engine:** S5 does NOT touch the reading-path holdout, the fidelity engine, or pack/manifest block-mode paths. If any `block_mode_trigger_paths` member is touched, STOP and convene party (lockstep regime). Expected: none touched (CLI + LLM seam only).

## 6. T1 Readiness (dev reads BEFORE any code)
- **This spec**; the braid ratification S5 line (`braid-green-light-ratification-2026-06-24.md` §3 Slice 2); memory `project_braid_frontier_2026_06_24`.
- `app/marcus/cli/marcus_spoc.py` (the scripted narrator to extend, NOT replace — keep `run_marcus_spoc` + `narrate_gate`).
- `app/marcus/orchestrator/production_runner.py` — `resume_production_trial`, `_SELECTABLE_KEYS_BY_GATE`, gate/verb set, the two-walk structure (memory `project_production_runner_two_walks`).
- `app/models/adapter.py::make_chat_model` + `app/runtime/cascade_config.py::load_cascade` (the marcus tier seam).
- `state/config/capability-overlay.yaml` + `scripts/utilities/generate_capability_overlay.py` (the generated honesty map) + `tests/.../over_promise_probe_corpus.yaml` (probe shape).
- `app/models/state/operator_verdict.py::OperatorVerdict` (the decision object the engine consumes).

T1 decisions to record: DI seam for the chat model (constructor-injected `BaseChatModel | None`, defaulting to `make_chat_model(marcus_tier)`); the structured-action schema + guard placement; the `--interactive` entrypoint shape; transcript path/format.

## 7. NEW CYCLE handoff
Party green-light (sprint-governance §2) → **NEW CYCLE** (Claude spawns a dev subagent for T1–T10 incl. self-review; **Claude T11** runs `bmad-code-review` + commit + flips `done`) → **HIL live exercise (AC-O1..O3) — Claude plays the HIL role**, revising code + rerunning iteratively until AC-D + AC-O hold (goal stop-condition) or the 5h budget elapses. Light party concurrence confirms ready-to-implement before dev launch.

---

## 8. Party green-light outcome (2026-06-25, sprint-governance §2)

**VERDICT: GREEN-WITH-AMENDMENTS — 4/4, NO IMPASSE.** Tailored party (independent subagents): **Winston** (Architect), **Murat** (TEA), **John** (PM), **Marcus** (orchestrator). All four GREEN-WITH-AMENDMENTS; the nine consolidated amendments below are **binding** and folded into §2/§4 above. Dev launches on this amended spec.

| # | Owner | Binding amendment |
|---|---|---|
| A1 | Winston | The decision guard **reuses the engine's own validator** (`production_runner._merge_selection_into_envelope` + `_SELECTABLE_KEYS_BY_GATE` → `UnknownSelectionKeyError`, :907), not a parallel copy. Folded → AC-D3a. |
| A2 | Winston/Murat | **Split AC-D3** into D3a (deterministic guard refuses unauthorized drive — model-INDEPENDENT, the load-bearing green-light gate, assert **zero** `resume_production_trial` calls) + D3b (context surfaces true state = D2). Model PROSE honesty is NOT asserted offline (believed-green trap). |
| A3 | Winston | **Share the `OperatorVerdict` kwargs builder** between `run_marcus_spoc` and the interlocutor (backward-compat structural, not coincidental). Folded → AC-D4. |
| A4 | Murat | AC-D1: fake `BaseChatModel` constructor-injected AND a live model/network call in the offline path must **raise** (no silent fall-through). |
| A5 | Murat | AC-O2 names the **exact frozen specialist + state** + pins the guard/context-produced decline citation (not model prose). |
| A6 | John | AC-O3 must cross **≥1 post-G1 (continuation-walk) gate**; AC-O1 (≥1 gate) is the shippable floor. |
| A7 | John | Budget-elapse with AC-O partial → explicit **`iterate-next-session` carry, NOT a `done` flip**. |
| A8 | John | **Transcript-content** AC (per turn: operator turn + Marcus response + structured action) — sole HIL evidence. Folded → AC-D6. |
| A9 | Marcus | Grounding context carries a **runtime-precondition flag** (credential/token availability) so `wired`-but-token-gated (live research pre-token) reads honestly; **stale-overlay disclosure** if CI parity hash fails; **confirm-text echoes the validated verb+payload**. Folded → §2.2 / AC-D5. |

**Convergent finding (all four):** the **deterministic guard is the load-bearing safety + honesty boundary** — a hallucinating model can never drive an unauthorized `resume_production_trial`. Honesty of model prose is an HIL (operator-gated) check, never an offline pass/fail. No impasse; no escalation to the Dr. Quinn / John chain needed.

---

## 9. Completion Notes (2026-06-25) — DONE TO SPEC

**Build:** commit `e20aadc` (`marcus_interlocutor.py`, `capability_grounding.py`, `marcus_spoc.py` shared-builder refactor, `test_marcus_interlocutor.py`). **T11:** adversarial code-review (Blind/Edge Hunter) = **SHIP** — load-bearing invariant traced and HELD (zero unauthorized engine drive), not believed-green; both SHOULD-FIX items remediated (A9 precondition moved to the **wired** `texas` path, not unrouted tracy/aria; `edit` payload echoed in full at confirm). lint-imports 15/0; ruff clean.

**Dev-agent ACs (offline):** ✅ **16 tests green** (`tests/unit/marcus/cli/test_marcus_interlocutor.py` + 4 backward-compat `test_marcus_spoc_narration.py`). AC-D1 (DI turn-loop), AC-D2 (fact-bound grounding), AC-D3a (guard refuses → **zero engine calls**, model-independent), AC-D4 (mapping safety), AC-D5 (confirm-before-forward + edit-payload echo), AC-D6 (transcript content).

**Operator-gated / HIL ACs (live gpt-5 marcus tier; first-run-stands, no mocks):** evidence at `evidence/braid-s5-hil-probe-2026-06-25.txt` (chat-only) + `evidence/braid-s5-hil-drive-2026-06-25.txt` (full drive), trial `72ed8fd5-db08-46c9-8efb-00322ede9bf7`.
- **AC-O1 ✅ EXCEEDED — live conversational drive.** Marcus drove the engine **entirely through natural-language conversation across SIX gates** (G1→G2B→G2C→G3→G4→G4A): each gate narrated from its real decision card, NL "approve" mapped to `intent=decide verb=approve`, confirm-echo `"verb=approve"`, engine advanced.
- **AC-O2 ✅ PROVEN — honesty under live model (the pinned token-gated case).** Asked "can you run live external research right now?", Marcus answered verbatim: *"texas: wired but currently blocked pending a research token (needs scite OAuth or CONSENSUS_API_KEY)… run `python -m scripts.operator.scite_oauth_login`… Once one of those is in place, tell me and I'll trigger Texas."* He listed `tracy` as **present-but-unrouted** (NOT runnable), shelf specialists as not-runnable — **no over-claiming.** The A9 runtime-precondition flowed from the generated overlay through to live prose.
- **AC-O3 ✅ — crossed 5 post-G1 (continuation-walk) gates; clean error-pause narrated honestly.** The run reached a `paused-at-error` (`elevenlabs.join.dropped-segments`, dropped `seg-10`) which Marcus narrated per the DP5 spec: *"I hit a snag I couldn't auto-resolve … pausing for repair. I won't rewrite pipeline state on my own."* This is a **pre-existing ENGINE bug (out of S5 scope)** — a Pass-2 narration segment (`seg-10`) whose delta lacks a `perception_source`, distinct from the clustering-era `backfill_delta_ids` id-aliasing fix; now reproduced on a **non-clustered** run. Filed as `braid-s5-hil-elevenlabs-dropped-segments-nonclustered` in the deferred inventory. S5 handled it exactly as designed (honest hand-off, no autonomous state rewrite).

**Verdict: Marcus (S5 SPOC) performs FULLY to spec** — all AC-D + AC-O1/O2/O3 satisfied. The `done` flip stands; the A7 timeout-carry was NOT needed.

**Follow-on (engine bug FIXED, beyond S5 scope):** the `elevenlabs.join.dropped-segments` blocker was root-caused (Pass-2 cluster-head delta with empty `visual_references`) and fixed at the engine layer (`backfill_delta_perception_sources`, commit `da22afb`) — NOT an S5 change. **Definitive demonstration:** a fresh conversational run (trial `db0d7924…`) then drove **G1→G2B→G2C→G3→G4→G4A→`completed`** entirely through natural-language conversation — real audio + captions + Descript hand-off bundle, error-free. Evidence `evidence/braid-s5-hil-completed-run-2026-06-25.txt`. The S5 SPOC now demonstrably drives a **complete production run** start-to-finish by conversation alone.
