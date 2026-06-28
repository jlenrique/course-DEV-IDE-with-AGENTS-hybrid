# UDAC — Universal Downstream Asset Contract (Step 8.5) — Design Strawman

Date: 2026-06-28 · Branch `dev/p5-downstream-consumption-2026-06-26`.
Operator-mandated 2026-06-27 (see directed-voice arc strawman §J). Placement: at/after Step 8 (CF-A E2E gives the live substrate to enforce against), before Step 9.

## Intent (operator)
Two guarantees, enforced UNIVERSALLY (not bespoke per consumer):
- **ACCESS:** every downstream specialist can LOCATE the ratified assets (source bundle, locked lesson plan, LOs, `g0-enrichment.json`, `authorized-storyboard.json`, `pass2-envelope.json`, `segment-manifest.yaml`, voice-selection, motion plan, …) — no ad-hoc path rediscovery.
- **USE:** changing those assets changes downstream outputs — proven by anti-tautology tests per major consumer.
Plus: **fail loud** on stale/missing ratified assets past the ratification boundary; fallback constants become an **explicit legacy-mode marker**, never silent.

## What already exists (do NOT reinvent — generalize)
- `g0-enrichment.json` frozen + cached at the run dir (P5 substrate); read read-only via `load_enrichment_result`/`load_enrichment_card`.
- `workbook_enrichment.py` + the Step-6 enrichment consumers = real Use-proven consumption (anti-tautology tests: mutate sentinel → output changes).
- Content-addressed digest machinery: `compiled_graph_digest.py` (v2.0), `corpus_fingerprint`, `content_fingerprint`.
- The prompt pack names downstream inputs; `production_runner` threads payloads at the single shared dispatch site (both walks).
- Per-specialist `emit_spans` + receipts (Step-4 Enrique receipts: asset-ish declarations).

## A. Proposed design

### A.1 Run Asset Index (RAI) — the Access spine
Build a **Run Asset Index** at the ratification boundary: a single in-run manifest (`<run_dir>/run-asset-index.json`) listing, per ratified asset:
`{ asset_id, path (run-relative), digest (reuse content-fingerprint), revision/run id, authority_status (ratified | provisional | absent), produced_by_node, ratified_at }`.
- Built deterministically from what the run has produced/ratified at each gate; UPDATED as assets ratify (append-only / monotonic).
- **Threaded through BOTH `production_runner` walks** (start + continuation/recover) — at the single shared dispatch site (the Step-6 A6 precedent: build at `_runner_payload_for_specialist`/the shared dispatch, so it's walk-invariant by construction). This subsumes the Step-6 `directed-voice-flag-capture-once-into-runstate` + the disk-read-vs-formal-index notes.
- A pure helper `resolve_asset(index, asset_id) -> {path, digest, authority_status}` that specialists call (passed-in, M3-clean — orchestrator builds the index, specialists consume it) instead of guessing paths.
- **OQ-A1:** is a separate `run-asset-index.json` the right home, or should it live inside the existing `ProductionEnvelope`/run state? Strawman: a dedicated artifact mirrored into run state (so it survives resume + is auditable on disk), reusing `load_*` read patterns.

### A.2 Per-specialist asset declaration — the Use/audit spine
Each specialist declares consumed assets in its input/receipt: `{ asset_id, path, digest, used: bool | available_only }` (`used` = the consumer actually read it and it shaped output; `available_only` = present but not consumed this run). Composes with `emit_spans` + the Step-4 receipt shape (which already carries asset-ish fields). Generalize the receipt format so UDAC reads it uniformly.

### A.3 Anti-tautology per consumer — the Use guarantee
A test harness per major downstream consumer (**Gary / Irene / Enrique / workbook / compositor / motion**): mutate an enriched-LO / source / pedagogy / citation / `voice_direction` sentinel in the upstream asset → assert the consumer's output changes where expected (mirror the P5-S1 `test_workbook_enriched_consumption.py` + Step-6 patterns). Where a consumer is currently constants-only (no enrichment consumption), the test asserts that explicitly (a documented "does not consume X yet" — surfaced, not hidden).

### A.4 Fail-loud past the ratification boundary
Once a run passes the ratification boundary (G1?), a specialist that requires a ratified asset which is **missing/stale** (digest mismatch vs the RAI) RAISES a tagged recoverable error (kira `_load_motion_plan` fail-loud precedent). **Fallback constants become an explicit `legacy_mode` marker** in the receipt (never a silent substitution) — so an operator/audit can SEE that a consumer fell back. **OQ-A4:** where exactly is the ratification boundary per asset (G1 for lesson plan/LOs; G2C for storyboard; etc.)? Strawman: per-asset ratified_at recorded in the RAI; fail-loud applies once an asset is marked ratified and a consumer downstream of that gate can't resolve it.

## B. Scope / phasing (UDAC is sizeable — propose a v1 cut)
- **v1 (this story):** the RAI (A.1) for the P5 asset set + threading through both walks + `resolve_asset` + the per-consumer asset declaration (A.2) for the P5 consumers (Gary/Irene/Enrique/workbook) + the anti-tautology harness (A.3) generalizing the existing P5-S1/Step-6 tests + fail-loud-with-legacy-marker (A.4) for the ratified P5 assets.
- **Deferred (follow-ons):** extending declarations/anti-tautology to compositor/motion/all specialists; a formal cross-run asset registry; the digest-revision history. (The operator framed UDAC as "a story"; v1 covers the P5 path it was motivated by, with the generalization hooks.)
- **OQ-B1:** is v1 = "the P5 asset set enforced" sufficient, or must UDAC cover ALL specialists' assets in one story? Strawman: v1 = P5 set + the universal RAI mechanism (so adding a consumer is a declaration, not new plumbing).

## C. Governance / risk
- Highest-blast-radius story in the arc (touches both walks + every consumer contract). **Dual-gate.** Own green-light party + RED-first + a live E2E (Step 8's CF-A run is the substrate UDAC enforces against — UDAC v1 should be exercised by the CF-A E2E).
- Reuse content-fingerprint/digest machinery (no new digest scheme).
- M3: orchestrator builds the RAI; specialists consume passed-in resolved assets (the Step-6 pattern).

## D. Asks of the (later) green-light party
1. Ratify the RAI shape (A.1) + its home (OQ-A1) + the ratification-boundary model (OQ-A4).
2. Ratify the per-consumer declaration format (A.2) generalizing the Step-4 receipt.
3. Ratify the v1 scope cut (B / OQ-B1) — P5 asset set + universal mechanism, compositor/motion deferred.
4. Confirm fail-loud + explicit legacy-mode marker (A.4) — no silent fallback.
5. Confirm UDAC v1 is exercised by the Step-8 CF-A E2E.

Proposed team: **Winston** (the RAI architecture + both-walks + M3), **Murat** (anti-tautology harness + fail-loud rigor), **Marcus/orchestrator voice** (the ratification boundary + run-state home), **Gary/Irene/Enrique** (the per-consumer declaration realism), **Texas** (asset provenance / digest). Convene at/after Step 8.

> NOTE: this strawman is authored ahead of its green-light (during an ElevenLabs-cooldown window) so the design is ready; the green-light party + dev run at/after Step 8 per the operator's placement.

---

## G. UDAC v1 CLOSE (2026-06-28) — SIGNED OFF, no impasse

**Built:** the universal **Run Asset Index** Access spine + USE-anti-tautology + fail-loud enforcement. `app/marcus/lesson_plan/run_asset_index.py` (NEUTRAL, M3-clean — models + the FAIL-LOUD `resolve_asset` + digest-from-disk + `GATE_ASSET_MAP` + `CONSUMER_REGISTRY` + `mark_ratified`/`repin_additive`), `app/marcus/orchestrator/udac_wiring.py` (gate WRITER both walks + dispatch READER guard), `AssetResolutionError(SpecialistDispatchError)` → existing `_pause_at_error`. Behind `MARCUS_UDAC_ACTIVE` (default OFF ⇒ byte-identical, gated ahead of `_run_dir`).
**Code-review (3 layers, Acceptance Auditor ACCEPT 10/10 §F):** flag-OFF byte-identical, but flag-ON enforcement bugs found + remediated — **F1** wired `repin_additive` (own-gate growth → re-pin) + made the gate writer **crash-proof** (never raises into the walk; stale-raise reserved for the consumer guard → recoverable pause); **F2** corrupt/zero-byte/non-utf8 asset + corrupt RAI → tagged `udac.asset-corrupt`/`udac.index-corrupt` (not a crash); **F3** ratify on all 7 gate-crossing sites (M-5 parity); atomic write; eager-arg gated; honest `GATE_ASSET_MAP` trim (G0E/G0R only — verifiably-on-disk); schema-version refusal. 42 UDAC + 459 broader tests green; ruff clean; M3 KEPT; CF-A exercise on the real Step-8 live run dir holds.
**Party CLOSE:** Murat 🧪 **CLOSE** (F1/F2 real+RED-first+correctly-split; MT-1..7 met w/ the positive-control non-vacuity guard; no fake-green), Winston 🏗️ **CLOSE** (RAI arch landed; crash-proof-writer/loud-consumer split correct, doesn't mask corruption; deviations bounded+M1-respecting; atomic write sound), Marcus-orchestrator ⚙️ **CLOSE** (M-1..5 realized; honest disk-verified map trim; fail-loud via _pause_at_error; both-walks parity; flag-OFF genuinely byte-identical). **Unanimous, no impasse.**
**DONE at ratified v1 scope:** universal RAI Access spine + `resolve_asset` fail-loud resolver (neutral, M3) + registry-driven USE anti-tautology (workbook/gary/irene USE-proven; enrique/compositor/kira declared `available_only` w/ byte-identical tripwire; earned-`used` parity) + fail-loud matrix → recoverable pause + flag-OFF byte-identical safe / flag-ON correct. **Follow-ons filed (honest deferrals, not buried):** `udac-v1-fail-loud-on-gate-crossed-absent-asset` (the fail-open residual — retire first), `udac-v1-universality-complete-gate-asset-map` (extend to the full M-2 set + payload-injection plumbing). Evidence: `evidence/p5-udac-v1-cfa-exercise-20260628T0214Z.md`.

## F. GREEN-LIGHT PARTY VERDICT (2026-06-28) — RATIFIED, no impasse

**Team:** Winston 🏗️ / Murat 🧪 / Marcus-orchestrator ⚙️ / Texas 🤠 — all GREEN-WITH-AMENDMENTS/CONDITIONS, no impasse. **Dual-gate, RED-first.** Ratified v1 design (binding):

### F.1 RAI (Access spine) — universal in v1
`<run_dir>/run-asset-index.json` — **disk-primary; run state mirrors only a POINTER + content-digest** (survives cold resume; the index grows monotonically so do NOT serialize it whole into RunState — M-3). **Universal:** lists ALL assets (P5 + deferred storyboard/segment-manifest/voice-selection/motion-plan) as `authority_status` entries even where consumers are deferred (Winston). Per entry: `{asset_id, path, digest, digest_algo, digest_schema_version, revision, ratified_at, produced_by_node, authority_status: ratified|provisional|absent, derived_from (source corpus_fingerprint/input closure)}`.

### F.2 Writer (mark-ratified) = GATE side-effect (both walks); Reader (resolve_asset) = shared dispatch site (M-1, load-bearing)
- **WRITE:** marking an asset ratified is a **gate-crossing side-effect** (an asset is ratified only when the operator clears its gate), so it fires in BOTH walk bodies (start reaches G1; continuation owns G2B+), idempotent + monotonic, exactly where `storyboard_publisher`/`chooser_publisher`/`run_g0_enrichment` already sit. Stamp `ratified_at` + `produced_by_node` off **`last_gate_crossed`** per the gate→asset map (M-2): **G0E**→`g0-enrichment.json`, **G0R**→`ratified-los.json`, **G1**→locked lesson plan + ratified LOs, **G2B**→variant/component_selection, **G2C**→`authorized-storyboard.json`, **G3/G4/G4A**→voice-selection/pass2-envelope/synthesis. (This RECONCILES Winston's RAI-WRITER-SEPARATION: index *assembly* is the gate event, not the per-specialist payload helper.)
- **READ:** `resolve_asset(index, asset_id)` + the fail-loud check live at the **shared dispatch site** (`_dispatch_specialist_at_node`, walk-invariant), passed-into specialists (M3-clean).
- **TWO-LOADERS-NOT-ONE (Winston):** keep the existing FAIL-SOFT `load_enrichment_card`/`load_enrichment_result` for the pre-ratification/backward-compat path; `resolve_asset` is a NEW FAIL-LOUD resolver. **RESOLVE-ASSET-LIVES-NEUTRAL (Winston):** `resolve_asset` + the RAI model live in a NEUTRAL `lesson_plan`/models module both sides import (the workbook local-read precedent) — NEVER an orchestrator module (M3).

### F.3 Digest/provenance (Texas TX-1..5)
- **TX-1:** pin `digest_algo` per asset — `canonical_sha256` for structured (canonicalize first), `file_content_hash` for opaque binary; digest the **PUBLIC serialized projection** (`to_card_payload`/`model_dump(mode="json")`), NEVER the audit-laden in-memory model. **TX-5 (MT-5):** RAI digest RECOMPUTED FROM DISK bytes by the orchestrator, never the producer's self-report (corrupt-on-disk → stale-raise test).
- **TX-2:** per-entry `digest_schema_version`; the stale-check REFUSES to compare across schema/algo (RAISE, not "stale"); RAI carries `rai_schema_version`.
- **TX-3 (critical):** `g0-enrichment.json` is ADDITIVELY enriched after G0 (P2 citations @ pass-0, P3 pedagogy @ pass-1 onto the SAME artifact after its gate). A naive stale-check would FALSE-FIRE on every P5 run. **stale = mismatch vs the digest at the asset's CURRENT `revision`; each additive layer bumps `revision` + re-pins `{digest, ratified_at}`.**
- **TX-4:** each derived asset records the `corpus_fingerprint`/input closure it was produced under (`derived_from`) — trust chains to SOURCE-is-KING. **TX-5:** `absent` carries null digest (never compared); authority orthogonal to content-address + monotonic.

### F.4 Fail-loud + USE (Murat MT-1..7 + Marcus-orchestrator M-4)
- **Fail-loud (data-driven, M-4 + RATIFICATION-IS-DATA):** RAI marks X ratified AND consumer downstream of `produced_by_node` AND can't resolve/digest-match → RAISE a **`SpecialistDispatchError`-family** error → routes through the existing `_pause_at_error` recoverable error-pause (kira `_load_motion_plan` precedent; no parallel channel). **MT-3 RED matrix:** (before/after boundary) × (present/missing/stale-digest), parametrized. **LEGACY-MODE-IS-TYPED (Winston):** `legacy_mode` is a TYPED receipt enum field, provisional-window-ONLY — raises post-boundary for a REQUIRED asset (the marker is not a badge for silent fallback).
- **USE anti-tautology (MT-1/2):** consumer-agnostic harness parametrized over a consumer REGISTRY, generalizing P5-S1/Step-6. Every USE test asserts **mutated-present AND constant/pre-mutation-absent** (no append-passes-green). "does not consume X" = a **byte-identical-under-mutation tripwire** test, never a comment.
- **`used` is EARNED (MT-4):** a coverage-parity test FAILS CI if any declared `used` lacks a passing anti-tautology test (and any `available_only` lacks a byte-identical test).
- **MT-5/Both-walks (M-5):** RAI digest identical across both walks; a both-walks parity test asserts identical `ratified_at` whether the gate crossed on the start (G0E/G1) or continuation (G2C) walk (the chooser_publisher 2026-06-24 bug class).

### F.5 v1 scope (ratified — Murat/Winston)
**v1 = the universal RAI (Access over the FULL asset set) + `resolve_asset` fail-loud resolver in a neutral module + the consumer-agnostic declaration format + anti-tautology harness for the 4 P5 consumers (≥1 USE-proven positive, ≥1 explicit `available_only` negative) + compositor/motion DECLARED-non-consuming-with-MT-2-tripwire (declaration NOT deferrable; only the plumbing is) + typed `legacy_mode` + data-driven ratification boundary + disk-recomputed schema-pinned revision-aware digests — exercised end-to-end by the Step-8 CF-A live substrate (MT-7).** Compositor/motion *plumbing* deferred; their *declaration* is in v1.
