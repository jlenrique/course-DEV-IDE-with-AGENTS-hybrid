# Enhanced VO arc — party-mode consensus record (2026-06-29)

**Status:** GREEN-LIGHT CONSENSUS REACHED (Dr. Quinn synthesis; no impasse; John/PM tiebreak not needed).
**Arc:** "make the directed voice REAL" (v3 text-driven) — the post-P5-directed-voice next increment "E".
**Branch:** `dev/p5-downstream-consumption-2026-06-26`. **Class S, phase 4-implementation. Epic key: `enhanced-vo`.**
**Goal file:** `goal-enhanced-vo-2026-06-29.txt`.
**SSOT inputs:** Marcus brief `_bmad-output/implementation-artifacts/claude-code-brief-enhanced-vo-v3-generation-2026-06-29.md`; arc strawman `_bmad-output/planning-artifacts/p5-directed-voice-arc-strawman-2026-06-27.md` §S; 27 live eleven_v3 audition clips at `evidence/elevenlabs-v3-rhetorical-audition-20260629/` + operator ear-notes.

## Workflow spine (confirmed via bmad-help)

Per story: `bmad-party-mode` GREEN-LIGHT → `bmad-create-story`(+`validate`) → optional `bmad-testarch-atdd` (RED scaffolds) → `bmad-dev-story` (RED-first) → `bmad-code-review` (3-layer) → `bmad-party-mode` CLOSE. `bmad-retrospective` at arc close. Sprint plan already exists (update `sprint-status.yaml`, no fresh sprint-planning). Not a migration story (Slabs 1-5) and not a Lesson-Planner Epic (28-32) — those validators do not apply.

## Two planning rounds

**Round 1 (reconciliation, 6 voices: Marcus, Winston, Murat, Irene, Vera, CD-Dan).** Established: the Marcus brief re-targets the increment from v2-numeric to v3 text-driven, keeping E's gate. Leg (a) role→slide linkage survives as the first hard gate; v2 leg (b) widen-pace retired; leg (c) seed kept as test-hygiene; four-channel separation + tag-only firewall is the substance.

**Round 2 (GREEN-LIGHT gate, canonical core + ≤2 specialty + Dr. Quinn synthesis).** Composition corrected per operator rule: CORE = canonical BMAD agents (John/PM, Winston/architect, Amelia/dev, Murat/test); ≤2 specialty (Marcus production-planning persona — author of the brief, NOT the langGraph Marcus-SPOC runtime; Vera/fidelity); Dr. Quinn synthesizes consensus; John/PM is the impasse tiebreaker.

### Six verdicts — all GREEN-WITH-AMENDMENTS (no hand-back)

- **John (PM):** spine + slice GREEN; nothing gold-plated. Binding acceptance question: pre-register the Descript-final pass/fail SIGNAL (judge, exact prompt, what "indistinguishable" means for the gate), first-run-stands.
- **Winston (Architect):** Slice 0 is its OWN story (a seam). Carried slide-key beats ordinal matcher (clustering mutates position → ordinal join born broken). M3 pre-condition: slide-key travels as DATA on the manifest; compiler/join read from the shared contract, never import clustering code. Four-channel + `rhetorical_role` = additive, dev-agent authority (not a version bump) if additivity is test-pinned; pipeline-manifest regime applies if `render_strategy:v3` touches a `block_mode_trigger_path`.
- **Amelia (Dev):** mandatory split — Story A (Slice 0 join) + Story B (Slice 1). RED order 1→9, live clip LAST + CI-deselected (`@pytest.mark.live`). Pin: exact field names, slide_key emit/read sites (gotcha: enrique reads irene deltas from `cache_prefix` at graph.py:993, not `contributions[]`), one authoritative closed tag allowlist, skip-if-exists key formula. Highest ambiguity = the slide_key emit/read contract + stability across re-clustering.
- **Murat (Test Architect):** Slice 0 join own-RED first, build-breaking, no v3 spend until green. Build-breaking offline gates: strip_tags==canonical, captions zero-tag-leak, four-channel goldens, skip-if-exists invalidation, containment firewall. Live: audio-transcript no-tag-leak proxy + ear blind A/B. NO numeric expressiveness assertion on v3 (rebuilds energy→rms honest-fail). HAND-BACK unless a cross-channel tag-bleed MUTATION test exists (plant a tag in captions → gate turns red).
- **Marcus (production-planning persona; brief author):** the blind A/B must ISOLATE THE TAG — identical canonical WORDS both arms (A=strip_tags, B=[tag]) — else it tests Irene's sentence, not the v3 channel. "Inaudible with words constant" = a fundable finding, build it so the negative can return and still count as success. HIL: operator must SEE Storyboard B render the literal provider bytes + captions zero-leak before any live cent.
- **Vera (Fidelity):** tag-only earns sign-off because `strip_tags(provider)==canonical` byte-exact collapses containment to one deterministic equality. PRE-CONDITION: closed eleven_v3 tag allowlist enumerated/pinned (not enumerable → HAND-BACK). NEW R7: Irene-authored rhetorical wording now enters fidelity risk → must be source-contained vs the ORIGINAL source narration (numerals/units/clinical-terms/negations/comparators ZERO-tolerance traceable). HAND-BACK if strip_tags==canonical is softened to a tolerance, or the allowlist ships open-ended.

### Dr. Quinn synthesis (the systems-level seam)

Every amendment is the SAME move — separating channels the slice silently conflated: **identity / plumbing-containment / rhetoric / tone**. It is the energy→rms honest-fail in a new coat (a warm_callback A/B would measure *rhetoric* while claiming to measure the *tag*). Cure: route each channel onto its own element so each result is attributable and honest, including the negatives.

## Resolved decisions

- **Fork 1 (role count) → TWO roles, content-corrected:** `warm_callback` is STRUCTURAL (its win is the words, held constant in both A/B arms) → its A/B is a rhetoric-vs-tag *decomposition*, not a tag test. To prove the v3 TAG channel you need a TONAL role where the tag does the work on identical words → **`contrast_emphasis`**. `curious_pivot` deferred to a later slice. The 2nd role is the experiment's CONTROL, not gold-plating.
- **Fork 2 (firewall) → TAG-ONLY**, made safe by one invariant: `strip_tags(provider) == canonical` BYTE-EXACT, ASSERTED, keyed to a closed eleven_v3 tag allowlist. Downstream rhetorical rewriting deferred to a later slice behind the firewall.
- **Live A/B is a NON-FAILING, pre-registered finding** — both outcomes valued; "indistinguishable" = tag is plumbing-only = a fundable finding (redirect to rhetoric+voice), NOT a failure. Only the offline deterministic gates + the live transcript no-tag-leak proxy can FAIL a story.

## Consensus shape — two stories

**Story A — `enhanced-vo-1-role-slide-linkage` (Slice 0; ZERO live TTS spend; GATES B):**
- A1. `slide_key` emitted as DATA on the manifest/handoff contract at Irene's clustering output (M3 fence: read from the shared contract, never import clustering code; mirror the cache_prefix read pattern at graph.py:993).
- A2. Deterministic source→final slide-map fixture on a REAL clustered Gary deck.
- A3. Identity join (role→final slide) via `slide_key` — RED-first, build-breaking, no fuzzy-ordinal fallback.
- A4. Stability-across-re-clustering assertion (same source slide → same key).

**Story B — `enhanced-vo-2-v3-provider-text-compiler` (depends on A green; RED order, live LAST + CI-deselected):**
- REUSE proven `scripts/api_clients/elevenlabs_client.py::text_to_speech_with_request_id` (v3 model_id, tags-via-text, seed, request-ids, normalization) — do NOT reinvent the ElevenLabs call.
- B1. `strip_tags(provider)==canonical` byte-exact ASSERTED, keyed to the closed allowlist.
- B2. Closed eleven_v3 tag allowlist enumerated + frozen (story PRE-CONDITION; not enumerable → HAND-BACK).
- B3. Four channels (canonical/provider/display/captions) + `*_sha256`; additivity test-pinned (v2 byte-identical off); pipeline-manifest regime at T1 if `render_strategy:v3` touches a `block_mode_trigger_path`.
- B4. Captions zero-tag-leak HARD assertion.
- B5. Cross-channel tag-bleed MUTATION test (absent → HAND-BACK).
- B6. skip-if-exists re-keyed on provider sha (existing key + `sha256(provider_text)`; fallback canonical sha when provider absent).
- B7. Fidelity containment firewall, RED-first.
- B8. Vera R7 authoring-gate: Irene's rhetorical wording source-contained vs original narration (numerals/units/clinical-terms/negations/comparators zero-tolerance).
- B9. `render_strategy:v3` additive enum + `rhetorical_role` closed enum; field names + seed-as-test-hygiene pinned.
- Roles: `warm_callback` (structural; Irene authors the callback sentence as canonical, compiler adds `[warm]`) + `contrast_emphasis` (tonal probe). One voice: Sarah.
- HIL: Storyboard B renders literal provider bytes + captions zero-leak BEFORE any live spend → live transcript no-tag-leak proxy → pre-registered isolated-tag blind A/B on the Descript final (tonal-role slide, identical words both arms, operator judge, first-run-stands, 2nd-deck cross-confirm).

## Predicted reactions (Dr. Quinn): all six ACCEPT. CONSENSUS REACHED.

## Owed
- Commit the working-tree 4-voice slate (Sarah default) with this arc.
- Branch-consolidation owed before the NEXT arc (not this one).

---

## Live leg (AC-B11) — INTERIM: two arms produced; operator blind A/B PENDING (2026-06-29)

Both stories party-CLOSED + committed + pushed (A `d4455e4f`, B `077d68e2`; origin synced). The arc's terminal step is operator-gated.

**Arms produced (real `eleven_v3`, no mocks)** at `_bmad-output/implementation-artifacts/evidence/enhanced-vo-ab-20260629/`:
- Canonical (identical both arms): "Access can improve, cost can rise, and continuity can fracture. When all three move at once, the next decision changes the patient's path."
- Role `contrast_emphasis` → compiler tag `[slow]`; voice Sarah (`EXAVITQu4vr4xnSDxMaL`); model `eleven_v3`; seed `73219` (fixed).
- **Arm A** (no tag) = canonical → `arm-A-no-tag.mp3`, req `YZtPNO2O6tuNXDycP4uM`, sha `c6dba26d…`.
- **Arm B** (`[slow]` + canonical) = compiler output → `arm-B-slow-tag.mp3`, req `KmlU972zmZbyWCg7OcDZ`, sha `f366737e…`.

**Live firewall held:** `strip_tags(provider)==canonical` True; `captions_text==canonical` True (the `[slow]` tag never reaches captions).

**Objective observation (NOT the verdict):** both arms are **10.397s, identical byte length (166391)** but **different sha** — the `[slow]` tag changed the waveform but not the pacing/duration at this seed+voice. A numeric/duration metric would read "no delta" — which is exactly why the pre-registered bar is the operator's EAR, not a metric. This pre-suggests the "indistinguishable = plumbing-only = FUNDABLE FINDING (redirect to rhetoric+voice)" outcome, consistent with the operator's audition note that Sarah is subtle on directive tags — BUT the verdict is the operator's blind A/B.

**REMAINING for arc DONE (operator-gated):** blind A/B (which clip carries the intended directed read?), first-run-stands; Vera live fidelity spot-check (both arms speak the SAME words, captions clean — confirmed offline; ear-confirm the synth didn't hallucinate lexical content from the tag); optionally cross-confirm on a 2nd voice/deck and/or via the full Descript-final mix (Dan's "opening night" — subtle reads can wash out in the mix). Record the finding (either outcome) → epic-enhanced-vo done.

### Live no-leak proxy (ASR) — PASS (2026-06-29)

Transcribed both arms via OpenAI ASR (`gpt-4o-transcribe`). BOTH transcripts == canonical text verbatim; Arm B (`[slow]`) spoke **no** stray tag word — the tag steered delivery, never became a spoken token. Artifact: `evidence/enhanced-vo-ab-20260629/noleak-transcripts.json`.
- **Live no-leak proxy: PASS** (the one remaining deterministic live gate that COULD fail — it didn't).
- **Vera fidelity spot-check (ASR-level): PASS** — both arms speak identical words == canonical; no hallucinated lexical content from the tag (the byte-exact offline guarantee confirmed in the actual audio).

**Net gate status: every FAILABLE gate PASSES** (offline 47 tests + byte-exact firewall; live ASR no-leak; fidelity identical-transcripts). The ONLY remaining element is the operator's blind perceptual A/B verdict — a NON-FAILING finding (either outcome = success). Arc DONE the moment the operator records that verdict.
