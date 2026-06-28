# P5-S2 (Step 6) — Deck + Narration Enrichment Consumption — Green-Light Strawman

Date: 2026-06-27 · Branch `dev/p5-downstream-consumption-2026-06-26` · after Step-5 close.
Parent: the directed-voice arc strawman (`p5-directed-voice-arc-strawman-2026-06-27.md`) Step 6 + deferred-inventory `p5-s2-deck-narration-enrichment-consumption` ("own party round, RED-first, live, flag-gated deck-byte-identical default — the BULK of remaining P5 value").

DONE (operator goal Step 6): **a learner-facing deck/narration artifact CHANGES from enrichment, not constants**, proven by anti-tautology tests (mutate an enrichment sentinel → output changes), while proven deck defaults stay regression-safe.

## Substrate (mapped)
- `G0EnrichmentResult` frozen at `<run_dir>/g0-enrichment.json`; read read-only via the PROVEN `workbook_enrichment.load_enrichment_card(run_dir)` pattern (P5-S1). `PedagogyAnnotation` (per `component_id`) carries `pedagogical_role` ∈ {definition, motivation, worked_example, synthesis, assessment, practice}, `teaches_after: tuple[component_id]`, `lo_refs`, `bloom`, `teachable`, `assessment_link`.
- Narration delivery hook: `annotate_segments_with_voice_direction(..., role_derived_seeds=)` is the STUBBED Step-2 hook; precedence = explicit override > CD/pass-2 defaults > **role-derived seed** > built-in. Call site `irene/graph.py:1057` does NOT pass it today.
- Gary deck seam: `per_slide_directives` (in `CONSUMED_PAYLOAD_KEYS`); byte-identity guards `gamma_settings` roster + `text_mode="preserve"` + `_STUDIO_LOCK_WRAPPER` MUST NOT be touched.

## A. Proposed scope (3 consumers, tiered by determinism/risk)

**Consumer A — Narration DELIVERY via the role-seed (HEADLINE; deterministic, provable, Track E×V capstone).**
Load the frozen card; per segment, find its enrichment component (by slide locator + excerpt/position) → its `pedagogical_role` → a `role_derived` `voice_direction` default via a **frozen role→voice map**. Wire that dict into `role_derived_seeds`. The directed DELIVERY of the narration then changes by pedagogical role — a deterministic, byte-exact learner-facing change. Honors Step-5 ruling: the map sets `pace` (the GUARANTEED dial) + `emotional_tone` (best-effort) as DEFAULTS (overridable; pace carries the reliable signal). Proposed `PEDAGOGICAL_ROLE_TO_VOICE`:

| role | pace (guaranteed) | emotional_tone (best-effort) | energy |
|---|---|---|---|
| definition | neutral | neutral | medium |
| motivation | neutral | warm | medium |
| worked_example | slower | neutral | medium |
| synthesis | slower | reflective | low |
| assessment | neutral | concerned | medium |
| practice | neutral | encouraging | high |

**Consumer B — Gary DECK directive hint (deterministic at the directive level; regression-guarded).**
Load the frozen card → inject a pedagogical-role/LO hint into `per_slide_directives` (an OPTIONAL additive field), so the directive/prompt SENT to Gamma is enrichment-shaped. Anti-tautology proven at the DIRECTIVE level (the prompt text changes deterministically) — NOT at the rendered PNG (Gamma is an LLM; we don't claim deterministic pixels). Do NOT touch `gamma_settings`/`text_mode`/Studio guards; flag-OFF or card-absent ⇒ deck directive byte-identical. **OQ-B1:** is "the directive changes" a sufficient learner-facing-deck proof, or must we also show a rendered-deck difference (a live Gamma render)? Strawman: directive-level for the deterministic test + ONE live render in the live leg as confirmation (not a deterministic gate).

**Consumer C — `teaches_after` narration CALLBACKS (Irene Pass-2 text; OPTIONAL/scoped — party rules).**
Use `teaches_after` to ground connective phrases ("now that we've seen X…") ONLY to a prior GROUNDED segment (Irene's green-light constraint); fail-safe SILENT if no matched prior grounded segment. Higher risk (LLM narration authoring + grounding). **OQ-C1:** include in Step 6, or defer to a follow-on so Step 6 stays the two deterministic consumers (A+B)? Strawman: DEFER C to a follow-on (it's LLM-authoring + grounding-sensitive; A+B already satisfy DONE deterministically and carry the bulk of value); the figure-citation gate stays the non-negotiable if C is ever built.

## B. Regression safety + flag-gating
- Mirror `workbook_enrichment.py`: read-only, zero network/model calls, load the frozen card, byte-exact values.
- Narration role-seed gated by the existing `MARCUS_NARRATION_VOICE_DIRECTION_ACTIVE` (+ enrichment card present); flag-OFF ⇒ byte-identical (role_derived_seeds=None as today).
- Gary deck gated by an additive optional payload key (card present) ⇒ no-op when absent; deck-default byte-identical.
- The role→voice map is a **frozen table** (shape-pin test), like `voice_direction_map.yaml`.

## C. Anti-tautology tests (the DONE bar; mirror P5-S1 `test_workbook_enriched_consumption.py`)
- **A (narration):** mutate a component's `pedagogical_role` in the card → that segment's emitted `voice_direction` has `source="role-derived"` + the mapped pace/tone; a DIFFERENT role → different mapped values; flag-OFF / card-absent ⇒ no role-derived seed (byte-identical). The role-seed is overridden by an explicit per-segment override (precedence preserved).
- **B (deck):** mutate `pedagogical_role` → the per-slide directive/prompt string sent to Gamma changes (sentinel-bearing); card-absent ⇒ directive byte-identical; `gamma_settings`/`text_mode` untouched.
- Grounding: the role-seed sets DELIVERY metadata only (never narration text) — the Step-2 grounding firewall + figure gate stay intact (re-assert).

## D. Live leg (§L policy)
A real run consuming a REAL enrichment card: narration segments get role-derived `voice_direction` from real `pedagogical_role`, AND Gary's per-slide directives carry the real enrichment hint. Capture: the role→voice mapping applied per segment + the enriched directive. Optionally ONE live Gamma render to confirm the deck is enrichment-shaped (confirmation, not a deterministic gate). Reuse a real run dir with a real `g0-enrichment.json` (e.g. the workbook live-close run, or a fresh tiny slice).

## E. Asks of the green-light party
1. **Ratify the scope:** A (narration role-seed) + B (deck directive) IN; C (teaches_after callbacks) DEFERRED (OQ-C1) — agree or pull C in?
2. **Ratify the `PEDAGOGICAL_ROLE_TO_VOICE` map** (§A) — pedagogically sound? Honors Step-5 (pace guaranteed, tone best-effort)?
3. **OQ-B1:** directive-level deterministic proof for the deck + one live render as confirmation — sufficient, or require more?
4. **Regression posture:** confirm flag-gating + byte-identity guards (gamma_settings/text_mode/Studio untouched; flag-OFF byte-identical) are right.
5. **Dual-gate** confirmed (proven-live producers).

Proposed team: **Gary** (deck regression-safe seam), **Irene** (narration grounding + teaches_after), **CD** (role→voice map), **Murat** (anti-tautology + regression), **Winston** (flag-gating + workbook-pattern reuse + the LLM-render proof boundary). Quinn-R folds in at CLOSE (role-map pedagogical soundness).

---

## F. GREEN-LIGHT PARTY VERDICT (2026-06-27) — RATIFIED, no impasse

**Team:** Gary 🎨 / Irene ✍️ / CD 🎬 / Murat 🧪 / Winston 🏗️ — all **GREEN-WITH-AMENDMENTS/CONDITIONS, no impasse.** Scope ratified: **A (narration role-seed) + B (deck directive) IN; C (teaches_after callbacks) DEFERRED** to a follow-on. **Dual-gate** confirmed.

### F.1 Ratified `PEDAGOGICAL_ROLE_TO_VOICE` map (CD-amended)
| role | emotional_tone (best-effort) | pace (GUARANTEED) | energy (best-effort) |
|---|---|---|---|
| definition | neutral | neutral | medium |
| motivation | warm | neutral | medium |
| worked_example | neutral | **slower** | medium |
| synthesis | reflective | **slower** | low |
| assessment | neutral | **slower** | medium |  *(CD: was concerned/neutral — `concerned` is reserved for safety/risk; signal moved to the guaranteed pace dial)* |
| practice | encouraging | neutral | high |

(worked_example/synthesis/assessment carry pace=slower → satisfies Murat's two-role-on-pace differential; energy stays best-effort-labeled, never advertised audible — Step-5 §12.)

### F.2 Binding amendments (all accepted)
- **Gary (GARY-A1..A7):** the enrichment hint routes **ONLY into `additional_instructions`** (deck-level) — STRUCTURALLY BARRED from the `text_mode="preserve"` card body (`_input_text`) and the Studio lock (`_studio_slide_content`/`_STUDIO_LOCK_WRAPPER`); Studio path no-ops the hint (+ byte-identity test); **short structured role/LO token, not prose** (no reflow); **explicit deck feature flag** (kill-switch parity, in addition to card-presence); the one live Gamma render **re-asserts the L2 source-fidelity/figure audit** (confirmation, not a gate); regression test pins `gamma_settings` roster + `text_mode` defaults + `_STUDIO_LOCK_WRAPPER` unchanged AND flag-OFF/card-absent ⇒ directive byte-identical; contract bookkeeping (`CONSUMED_PAYLOAD_KEYS` + Ratchet-D).
- **Irene (IR-A1/A2):** firewall is a **BLOCKING test** — `narration_text` byte-identical after annotation; `voice_direction` consumed ONLY by the render/TTS layer, never concatenated into / re-fed as narration; figure gate runs on the pre-annotation frozen manifest. Linkage **fail-safe:** no-match OR ambiguous-multi-match ⇒ NO seed (built-in default); the wiring **pre-filters seed keys to manifest-present segment ids** (do NOT lean on the module's fail-loud unmatched-id raise as a routine no-match path).
- **Murat (MUR-1..6):** **§C-B mutates a SENTINEL-bearing enrichment field** (e.g. an LO statement/id), NOT the 6-value role enum (too low-entropy) — assert the sentinel byte-exact in the `additional_instructions` payload, absent when card-absent. **§C-A two-role differential on PACE** (the guaranteed dial) + explicit per-segment override beats the role seed. **Narration-text firewall test** (= IR-A1). **Byte-identity vs a recorded baseline** for BOTH producers at flag-OFF AND card-absent; the deck test pins `gamma_settings`/`text_mode`/`_STUDIO_LOCK_WRAPPER` **by name** as their own assertions. **B's language:** "directive byte-deterministic; the render is confirmation, NOT a gate" — no overstated "deck deterministically changes." **C filed** with the figure-gate as its precondition.
- **CD (map):** `assessment`→neutral/slower (above); **energy leashed best-effort** (keep values/receipts, never advertise audible); **Storyboard B renders `source="role-derived"` as a visibly-distinct "auto/default" badge** + the pace-guaranteed/tone-energy-best-effort tier label (ties §12). Live leg uses a **role-DIVERSE slice** so differentiation is visible.
- **Winston (A1..A6):** **no third loader** — narration + deck project **orchestrator-side** via `load_enrichment_result` (`g0_enrichment_wiring.py`); workbook keeps `load_enrichment_card`; loader chosen by projection side; specialists consume a **passed-in dict** (mirror how `voice_direction_defaults` arrive — NO `app.marcus` import in the specialist). **Single-source the `g0-enrichment.json` basename** constant. **Map + segment→component matcher live orchestrator-side** (specialist does zero matching). **Pin the segment→component join key now** (segment_id or slide-locator+position — don't discover live). Projector **pure/deterministic + card-absent byte-identical**; **shape-pin `PEDAGOGICAL_ROLE_TO_VOICE`**. **Both-walks asset-index:** deck/narration fire post-G1 (continuation/recover walk) — assert `g0-enrichment.json` is threaded into the run-asset index on BOTH walks (ties UDAC 8.5) + a **continuation/recover-walk test** proving the consumer still finds the card (closes the silent-no-op-on-resume trap).

## G. STEP-6 CLOSE (2026-06-27/28) — SIGNED OFF, no impasse

**Party CLOSE:** Gary 🎨 **CLOSE** (GARY-A1..A7 verified; deck path regression-safe; live render drift_rate=0.0), Quinn-R 🔎 **CLOSE** (role→voice map pedagogically SOUND; CD's assessment→neutral/slower is a real test-anxiety removal; guaranteed pace on the comprehension-critical roles; honest best-effort labeling), Winston 🏗️ **CLOSE** (A1-A6 landed verbatim; EDGE-1 fail-open architecturally correct; both-walks guaranteed at the single shared dispatch site; disk-read ≡ formal asset index pending UDAC), Murat 🧪 **CLOSE-WITH-CONDITIONS** (EDGE-1 the correct call; anti-tautology/regression PASS no fake-green; DONE met live by Consumer B; Consumer A = deterministic-on-real-card + Step-5-live seed→audio). **Unanimous, no impasse.**

**What shipped (DONE — a learner-facing artifact changes from enrichment, not constants):**
- **Consumer B (deck) — FULLY LIVE-PROVEN:** the enrichment LO sentinel lands verbatim in the Gamma `additional_instructions` directive (firewalled out of the preserve body + Studio lock); real Gamma render `GAyK0cUFhYeRwy2H0fo9W` (completed, exportUrl) re-asserted L2 source-fidelity `drift_rate=0.0`.
- **Consumer A (narration delivery) — deterministic + Step-5-live composed:** enrichment `pedagogical_role` → role-seed → `voice_direction` (pace=slower for worked_example/synthesis/assessment) is new+deterministic and proven over the REAL live-enriched card; the seed→materially-different-AUDIO leg is unchanged from Step 5 (MUR-4 PASS, live).
- 44 focused + 289 broader tests green; ruff clean; M3 KEPT (only pre-existing C3); flag-OFF/card-absent byte-identical for both producers; TW-7c-4 roster passes.
- `bmad-code-review` 3 layers (Acceptance Auditor PASS 10/10) + MUST/SHOULD-FIX remediation: **EDGE-1 divergence guard** (the headline), EDGE-2 exhaustiveness, EDGE-3 teachable=False skip, EDGE-4 anchored parser, BLIND-1/2 byte-identity+precedence tests, EDGE-5 hint sanitization, TW-7c-4 allowlist, cosmetics.

**⚠️ HONEST DISCLOSURE (Murat condition 2 — binding sprint record):** **Consumer A (the "headline" Track-E×V narration role-seed) is INTENTIONALLY INERT (fail-open neutral) on production-NORMAL clustered decks.** The G0 card numbers the SOURCE corpus (`Slide N`) while the final deck is renumbered by Pass-1 clustering/split/drop/reorder, so the divergence guard applies role-seeds ONLY on 1:1-aligned (non-clustered) decks; on clustered decks it fails open to the proven neutral baseline (never mis-paces). So the **bulk of Step-6 enrichment value today lands on Consumer B (deck)**; Consumer A's narration-delivery-from-enrichment is real but conditional on aligned enumerations until the durable fix. The content-grounded source→final join `p5-s2-role-seed-robust-source-to-final-slide-linkage` stays LIVE in the deferred inventory and MUST be reactivation-reviewed before any trial that wants role-paced narration on a clustered deck.

**Conditions (non-code-blocking, tracked):** (1) the aligned-deck Consumer-A live TTS confirmation receipt (seg synthesis/slower vs definition/neutral, distinct request IDs, deterministic pace-delta judge, first-run-stands) lands in the evidence dir when the ElevenLabs account cooldown lifts — external infra, in-flight; (2) the above honest-disclosure recorded (done, here + commit message).

### F.3 Deferred (C)
`p5-s2-teaches-after-narration-callbacks` filed → deferred-inventory, with IR-C1 binding constraint (a callback may reference a prior component ONLY if `teaches_after`-before AND that component's `teachable is True`; introduces NO new numeral/figure/claim; generated by a pass through the SAME figure-citation gate; fail-safe SILENT when no matched prior grounded segment) + Murat MUR-6 figure-gate precondition.
