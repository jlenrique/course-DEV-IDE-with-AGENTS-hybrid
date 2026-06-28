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
