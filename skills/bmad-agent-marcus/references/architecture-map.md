---
name: architecture-map
code: AM
description: How Marcus grounds in the live app — the GENERATED sources of truth, the routing-truth honesty rule, and the conversation-space-vs-deterministic-engine substrate boundary. Load at activation before any capability claim.
---

# Architecture Map — how you know the app, truthfully

You are reborn every session with no memory of the app's current shape. This reference tells you **where the truth lives** so you neither under-serve the operator nor over-promise. The rule that governs everything below: **trust GENERATED/derived artifacts; treat hand-authored docs as drift-prone color.**

## 1. The generated sources of truth (read these; do not guess)

| Question you're answering | Authority (read this) | What it is |
|---|---|---|
| "How is the system shaped? Who are the specialists? What are the layers?" | [`docs/ONBOARDING.md`](../../../docs/ONBOARDING.md) §2–§3 | **Generated** from the knowledge-graph scan of the codebase. Architecture + ~20-specialist roster + the Marcus duality. |
| "Is capability X actually **wired right now**?" | [`state/config/capability-overlay.yaml`](../../../state/config/capability-overlay.yaml) | **Generated** from the live substrate (manifest + dispatch-registry + on-disk not-stub + registry status). CI-parity-guarded; cannot say `wired` about something the dispatch graph doesn't route to. See [`./capability-overlay.md`](./capability-overlay.md). |
| "Which workflows / deliverables can I offer the operator?" | the workflow menu (when generated; today: one proven family, narrated-lesson) | Until a generated workflow registry exists, the proven workflow is the narrated-lesson manifest at `state/config/pipeline-manifest.yaml`. Do **not** hand-invent a menu. |

The hand-authored [`./specialist-registry.yaml`](./specialist-registry.yaml) and [`./external-specialist-registry.md`](./external-specialist-registry.md) are the **org-chart** (who exists, paths, delegation envelopes). They are NOT routing-truth and they rot — the canonical smoking gun is a months-stale roster line. Use them for *paths and envelopes*; use the overlay for *"is it wired."*

## 2. The honesty invariant (non-negotiable)

- **ONBOARDING tells you what EXISTS and how it's SHAPED. It does NOT tell you what's WIRED or PROVEN.** A specialist appearing in ONBOARDING means it's on disk — nothing more. Never convert "exists in ONBOARDING" into "I can do it."
- **The overlay is the routing authority.** Read each specialist's `capability_state`:

  | state | what you may say |
  |---|---|
  | `wired` | routed + dispatchable + real module — production-real |
  | `present-but-unrouted` | built but **no manifest node routes to it** — NOT on the production path (the Tracy bug class) |
  | `partial` | wired-shaped but a contract gap is flagged |
  | `shelf` | a skill on disk, never dispatchable |
  | `orchestrator` | you (`marcus`) — in-manifest, not a dispatched specialist |

- **Never assert `wired` or `proven` for anything the overlay doesn't mark `wired`.** If unsure, say "let me check the overlay" or "that's present but not on the proven path." Confident-wrong is the failure mode this whole system was built to prevent.
- **"Exists" ≠ "wired" ≠ "proven on the trial path."** Three different claims. Keep them distinct.

## 3. Two execution substrates — always know which one you're in

This is the boundary that keeps you both capable and safe. The same task can run two ways, and they are NOT equivalent.

### A. Conversation-space (YOU drive) — for spikes, exploration, ad-hoc, odd lesson plans

You orchestrate directly: invoke specialist skills, call MCP tools (Gamma, ElevenLabs, etc.) and `scripts/api_clients/`, chain results, decide next step. This is legitimate and valuable for **spiking a new idea, exploring an odd lesson plan, ad-hoc one-offs, and prototyping** before anything is formalized.

**Be honest about what this mode does NOT give you** (say so to the operator when output matters):
- **Not reproducible** — you make different micro-decisions each run; there's no frozen graph to replay.
- **Not tamper-evident / not gated** — "gates" are just you pausing to ask; there are no signed DecisionCards, no one-time nonces, no verdict digests.
- **Not durable** — run state lives in the conversation; lose the session, lose the run. No checkpoint/resume.
- **No deterministic guard** — here YOU hold the reins, so a mistake by you becomes an action directly. (In the engine that's structurally impossible.)
- **Fidelity caveat** — specialists have a skill-side and a production graph-side (`app/specialists/<name>/`). Driving the skill-side may not exercise the hardened production paths (contracts, fidelity audits, gate wiring). Spike output ≈ the capability; it is not guaranteed identical to production output.

Use this freely for exploration. **Never represent conversation-space output as a tracked or published production artifact.**

### B. The deterministic engine (`production_runner` drives) — for tracked / published production

Route to the engine via the trial CLI (`python -m app.marcus.cli trial start …` / resume) or the Marcus-SPOC surface (`app/marcus/cli/marcus_spoc.py`). This is where reproducibility, manifest-compiled LangGraph walks, tamper-evident DecisionCards, the deterministic guard (the human verdict — not the LLM — advances the run), the Postgres checkpointer, and the learning ledger all live. This is the product's whole value proposition; it is what the LangChain/LangGraph migration bought.

### The decision rule

> If the operator wants to **keep, ship, reproduce, or audit** the result → **the engine (B).**
> If the operator is **spiking, exploring, or doing a deliberate one-off** → **conversation-space (A) is fine — and name it as such.**

When in doubt, ask which they want. Defaulting a "real" lesson into conversation-space throws away every guarantee above; defaulting a quick spike into the full engine ceremony wastes their time.

## 4. Fully exercising capabilities in a spike (mode A)

1. **Check the overlay first.** Offer `wired` capabilities as production-real. You may still *poke* a `present-but-unrouted` / `shelf` capability for a spike, but say plainly "this isn't on the proven path — spike only."
2. **Resolve invocation from the org-chart:** `specialist-registry.yaml` for paths, `external-specialist-registry.md` for delegation envelopes.
3. **The real seams** are the MCP tools (Gamma, ElevenLabs, Notion, Box, Scite, etc.) and `scripts/api_clients/` on a shared `BaseAPIClient`. Those are how assets actually get produced outside the engine.
4. **Respect the gates anyway.** Quality/fidelity discipline is non-negotiable in any mode — a spike that skips fidelity checks is a spike whose output you cannot trust.

## 5. Freshness — the generated docs are only trustworthy if current

- **ONBOARDING:** trust it only if `.understand-anything/meta.json::gitCommitHash` is at/near HEAD. If it's well behind, say "my architecture map may be stale" and recommend `/understand` + `/understand-anything:understand-onboard`.
- **Overlay:** trust it if the CI parity test is green; if substrate changed, it must be regenerated: `python -m scripts.utilities.generate_capability_overlay`.
- If a generated source is stale, **disclose that** rather than asserting its contents as live fact.

## 6. Note on the tracked/ad-hoc axis (MM)

[`./mode-management.md`](./mode-management.md) (MM) governs a **different** axis — whether run state + learning are persisted (tracked) or suppressed (ad-hoc). That is orthogonal to the substrate boundary in §3. Caution: parts of MM describe **pre-migration** substrate (SQLite runs, `manage_mode.py`); treat its specific storage claims as possibly stale against the current LangGraph + Postgres runtime, and prefer this map for the current architecture.
