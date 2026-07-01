# VERDICT — Leg-4 UDAC anti-tautology broken-asset HALT (independent live validation)

- **Date (UTC):** 2026-07-01T02:58Z
- **Branch:** dev/concierge-production-substrate-2026-06-29
- **Driver:** scratchpad/leg4_udac_halt_driver.py (pre-validated OFFLINE-OK; run live here)
- **Flag:** MARCUS_UDAC_ACTIVE=1 (set by driver); OPENAI_API_KEY present (sk-proj...oc0A, len 164)
- **Protocol:** FIRST-RUN-STANDS honored — both arms passed on the FIRST honest live attempt; NO retry-to-green, NO infra re-run needed. Arms run SEQUENTIALLY. No mocks. Judged independently from runner-emitted artifacts (not the driver exit code).

## Arms

| Arm | trial_id | runner status | tag | node/specialist | outcome |
|-----|----------|---------------|-----|-----------------|---------|
| HALT | `08b5ff0f-a84c-4bd8-bd6c-3d0ca66cef64` | paused-at-error | `udac.asset-stale` | 07 / gary | halted BEFORE dispatch, $0 |
| CONTROL | `938e1680-c182-421c-8a00-33b626310295` | paused-at-gate (G2B) | none (clean) | 07 / gary re-dispatched | real paid Gamma call, walk advanced |

## Per-bar verdict (independently verified against runner-emitted artifacts)

| Bar | Requirement | Verdict | Evidence |
|-----|-------------|---------|----------|
| **BAR 1** | HALT run.json status == paused-at-error; real runner-emitted error-pause.json exists | **PASS** | halt/run.json `status="paused-at-error"`; halt/error-pause.json present with runner fields (`runner`,`run_state`,`node_index`) |
| **BAR 2** | RAI pins g0-enrichment RATIFIED with a real digest | **PASS** | both trials' run-asset-index.json: `entries.g0-enrichment.authority_status="ratified"`, `digest=c23a37c5e56f...`, `digest_algo=canonical_sha256`, `produced_by_node=G0E` |
| **BAR 3** | error-pause tag == udac.asset-stale at node 07 / gary — NOT coverage/gamma-flake/other (vacuity guard) | **PASS** | halt/error-pause.json `tag="udac.asset-stale"`, `node_id="07"`, `specialist_id="gary"`; message cites stale digest `a8fd457155ae…` != RAI `c23a37c5e56f…` |
| **BAR 4** | $0 before paid: gary contribution absent, zero mp3/wav, no ElevenLabs/Descript | **PASS** | halt/run.json contributions=13, **gary@07 count=0** (no dispatch record); mp3=0 wav=0; the 13 gary PNGs on disk are **byte-identical copies of the golden** (copytree artifact) — NO new generation fired |
| **BAR 5** | discriminating control: clean recover did NOT halt on udac.asset-stale; gary@07 re-dispatched real paid Gamma; walk advanced | **PASS** | control/run.json `status="paused-at-gate"` (no udac error); contributions=14, **gary@07 present** with fresh `generation_id="AKvfIPLarpZeBHp3fReNU"`, `calls_made=1`, `contributed_at=02:55:50`; all 13 control PNGs differ in bytes from golden (freshly generated); proves the corruption CAUSED the halt |
| **BAR 6** | digest not presence: corruption = content mutation of still-present, still-valid-JSON asset → TAG_STALE on digest mismatch | **PASS** | added benign key `_leg4_udac_corruption_marker`; file still valid JSON on disk; digest `c23a37c5→a8fd457155ae` (see digest-note.md) |

## OVERALL: **PASS**

The UDAC anti-tautology broken-asset HALT fires live, through the real production_runner continuation walk, for the RIGHT reason (`udac.asset-stale`) at the RIGHT node (07/gary), BEFORE any paid consumer dispatch ($0), and is DISCRIMINATING — the clean control sails past the guard and re-dispatches a real paid Gamma call. No wiring gap; no wrong-tag halt; no false positive.

## Live spend
- **HALT arm:** $0 (no Gamma/OpenAI/ElevenLabs call fired — halted at asset resolution).
- **CONTROL arm:** one real Gamma generation (generation_id `AKvfIPLarpZeBHp3fReNU`, 13 slide PNGs + composite `gary_A.png` ~9.4MB). Gamma is credit-based (~a handful of credits for a re-dispatch); `cost_usd` field = 0.0 (Gamma spend is not USD-tracked in the envelope). No ElevenLabs/Descript spend.

## Integrity
- **No commit, no push, no source-code edit.** Only new trial dirs under state/config/runs/ + this evidence bundle written.
- **Golden untouched:** run 8d819b8d g0-enrichment.json canonical_sha256 still `c23a37c5` after both arms.
