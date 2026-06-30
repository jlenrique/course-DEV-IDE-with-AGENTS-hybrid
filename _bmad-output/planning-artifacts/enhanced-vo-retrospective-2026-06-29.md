# Enhanced-VO arc — retrospective (2026-06-29)

**Arc:** "make the directed voice REAL" (v3 text-driven). Epic `enhanced-vo`. Branch `dev/p5-downstream-consumption-2026-06-26`. **Outcome: DONE.** Both stories party-CLOSED; operator blind A/B verdict = **B (directed read audible → v3 tag channel promoted)**.

## What shipped
- **enhanced-vo-1** (`d4455e4f`) — `slide_key` role→slide **identity join** replacing the fail-open ordinal-set join; deterministic primary(`slide_briefs`)+fallback(`lesson_plan`+roster) with cross-consistency fail-loud guard; M3-clean; byte-identical OFF; live-proven on real `c2c6dcbf`.
- **enhanced-vo-2** (`077d68e2`) — TAG-ONLY v3 provider-text compiler (`app/specialists/_shared/voice_provider_text.py`), frozen 8-tag allowlist, byte-exact `strip_tags(provider)==canonical` firewall, four sha256'd channels (canonical/provider/display/captions), captions zero-leak + cross-channel mutation gate, skip-if-exists on provider sha, model-aware branch on `effective_model==eleven_v3`, deferred-role fail-loud, Storyboard-B "WILL FAIL AT DISPATCH" surfacing.
- **Live A/B** (`0eac3a12` + Descript `1385ad93…`) — two arms via real eleven_v3 (Sarah, seed 73219), ASR no-leak PASS, published to Descript; operator verdict **B**.

## What went well
1. **The pre-registered "operator ear, NOT a numeric metric" bar was vindicated** — the two arms were byte-identical in duration (10.397s); a numeric/duration metric would have falsely scored "indistinguishable," but the operator's ear detected the directed prosody (B). This is the single most important methodological win and confirms Murat's "no energy→rms proxy" insistence.
2. **3-layer adversarial review caught real defects the dev's own green run missed** — Story A: a silent fail-open mis-seed + a whole-run hard-stop on carrier drift. Story B: a **bracket-in-canonical regression** that would have crashed on `[1]`/`[CO2]` clinical citations, a silent deferred-role downgrade, and a Storyboard-swallows-the-failure honesty bug. All remediated RED-first before close.
3. **Dr. Quinn's "separate the conflated channels" synthesis** (identity/plumbing/rhetoric/tone) shaped the whole arc and pre-empted the energy→rms trap (a warm_callback A/B would have measured rhetoric while claiming to measure the tag → drove the contrast_emphasis tonal-probe choice).
4. **Tag-only firewall** (`strip_tags==canonical`) gave a mechanically-enforced fidelity guarantee; the allowlist-aware fix also *strengthened* fidelity (citations/chemical notation preserved verbatim) rather than pressuring authors to mangle clinical text.

## What to improve / carry
- **Irene does not yet EMIT `rhetorical_role`** — the A/B probe set it via override. Wiring Irene's Pass-2 to emit roles on real clustered decks is the next real-deck step.
- **Live A/B was clip-level audio in Descript, not the full assembled-lesson mix** (slides+bed-music). Dan's "opening night" cross-confirm + a 2nd deck remain for a stronger claim.
- **Process:** the goal's Stop-hook fired repeatedly on the operator-gated terminal (blind A/B). Lesson: a success bar whose final gate is an operator perceptual judgment cannot be auto-satisfied; the agent must drive to the artifact then hold — confirmed correct behavior, but the goal phrasing could mark the operator step explicitly terminal.

## Deferred-inventory consultation (governance #1)
- **FILED this arc:** `directed-voice-vera-r7-wire-clinical-lexicon` (hard 3-way reactivation: wire R7 audit + span/dependency-aware negation detector + real clinical lexicon, before any role with NEW Irene-authored clinical wording ships).
- **Named follow-ons (to file at next planning):** widen populated role taxonomy beyond {warm_callback, contrast_emphasis}; Irene rhetorical_role emission on real decks; Shannon voice for grave/reflective roles; 2nd-deck + full-Descript-mix cross-confirm of the B verdict.
- **Branch-consolidation owed** before the NEXT arc ([[project_branch_consolidation_owed]]) — review all branches + update master; we've stayed on `dev/p5-downstream-consumption-2026-06-26` across multiple arcs.

## Validation
Story A 65 tests; Story B 47 tests; consolidated 672 green; ruff clean; import-linter M3 KEPT (only pre-existing C3). Live: real eleven_v3 (2 arms), real Descript publish, ASR no-leak PASS. NO MOCKS for any production claim.
