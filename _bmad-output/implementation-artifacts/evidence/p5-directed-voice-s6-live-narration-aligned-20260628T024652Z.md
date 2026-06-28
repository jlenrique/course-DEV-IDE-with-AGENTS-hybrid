# P5 Directed-Voice Step-6 — Consumer-A LIVE narration receipt (ALIGNED deck) — 20260628T024652Z

The owed Step-6 **Consumer-A live confirmation**: drive the REAL enrichment chain on a
**1:1-ALIGNED deck** (so the EDGE-1 divergence guard ALLOWS seeding) and produce real
ElevenLabs clips whose delivery SETTINGS differ by `pedagogical_role`. ElevenLabs cooldown
cleared (list_voices → 45 voices). Voice: `CwhRBWXzGAHq8TQ4Fs17` (Roger, same as S5).
Flag `MARCUS_NARRATION_VOICE_DIRECTION_ACTIVE=1`. First-run-stands; SEQUENTIAL calls.

## The REAL chain (no shims)

1. **Constructed ALIGNED g0-enrichment card** — 3 narration `typed_components` on `Slide 1/2/3`
   carrying DIFFERENT roles: `synthesis` (slide 1), `definition` (slide 2), `worked_example`
   (slide 3). Each `teachable=True`.
2. **Orchestrator** `enrichment_consumption.project_role_derived_voice_by_slide` →
   `by_slide = {"1": {tone:reflective, pace:slower, energy:low}, "2": {tone:neutral, pace:neutral, energy:medium}, "3": {tone:neutral, pace:slower, energy:medium}}`;
   `source_slide_ordinals = [1, 2, 3]`.
3. **Irene seam** `graph._attach_voice_direction` / `_role_derived_seeds_for_deltas` re-keyed the
   per-slide table onto this pass's segment deltas. EDGE-1 guard: source `{1,2,3}` == final `{1,2,3}`
   → **seeds APPLY (NOT fail-open)**:

| segment | slide | applied source | applied pace | tone | energy |
|---|---|---|---|---|---|
| seg-01 | slide-01 | **role-derived** | **slower** | reflective | low |
| seg-02 | slide-02 | **role-derived** | neutral | neutral | medium |
| seg-03 | slide-03 | **role-derived** | **slower** | neutral | medium |

   Asserted in-run: seg-01 & seg-03 `source=role-derived, pace=slower`; seg-02 `role-derived, neutral`.
   This is the proof the seeds are APPLIED, not the EDGE-1 fail-open neutral.
4. **Enrique** `_act.build_assembly_bundle` (flag ON) synthesized REAL clips via the shared
   `map_voice_direction_to_tts`. The role-derived direction resolved to DISTINCT ElevenLabs
   settings, verified in each on-disk receipt:
   - seg-01 (synthesis/slower): **speed=0.94**, stability=0.75, style=0.10
   - seg-02 (definition/neutral): **speed=1.00**, stability=0.50, style=0.35
   - seg-03 (worked_example/slower): **speed=0.94**, stability=0.50, style=0.35

## Run-1 (short held text — 67 chars: "Let me walk you through this idea so it really lands for you today.")

REAL request IDs (all distinct), durations via `directed_voice_acoustics.analyze_clip`:

| segment | role/pace | speed sent | REAL request_id | audio_sha256 (12) | duration_s |
|---|---|---|---|---|---|
| seg-01 | synthesis/slower | 0.94 | `l1iYUlsswU9Vts7Ge1wW` | b7fdc1a4531b | 3.344 |
| seg-02 | definition/neutral | 1.00 | `nAzNOI8W3UoY7tRfIw7V` | e59fe58f4160 | 3.483 |
| seg-03 | worked_example/slower | 0.94 | `QKd0BHYEndTDqAh0Lgaw` | ced198de27c6 | 3.437 |

**Anti-tautology control** — the SAME 3 segments with NO enrichment (empty seed table) →
all `cd-authored neutral` (no role pace). Distinct request IDs
`HoWvVsvlbJg1weIh99TS / 6EA9bwcGliJwpp78vS4g / BkS4SnANt2ZNnxjcxSfo`;
durations 3.390 / 3.437 / 3.344 → control spread 0.093s (no role separation, as expected).

Deterministic judge (k=3, floor F = |enr.seg02 − ctl.seg02| = 0.0464s, 3F = 0.139s):
synthesis-slower vs neutral = 0.139s **not > 3F**; worked_example-slower vs neutral = 0.046s
**not > 3F**. **Duration verdict: does NOT clear the bar at short length.**

## Run-2 (power-corrected, 212-char held passage — to fairly detect a 6% speed delta)

Same real chain, longer held text so a nominal 6% slower speed should yield ≈0.7s on ~12s clips:

| segment | role/pace | speed | REAL request_id | duration_s |
|---|---|---|---|---|
| seg-01 | synthesis/slower | 0.94 | `I3DZ3iMdCcTIeXmXqIYQ` | 11.889 |
| seg-02 | definition/neutral | 1.00 | `549Lv7UwYGDnilywfdGY` | 11.796 |
| seg-03 | worked_example/slower | 0.94 | `qTrkczTdS9gXaqusxdUC` | 11.331 |
| floor (neutral re-synth, same text+dir) | neutral | 1.00 | `fkcCweURTooiRw3pXAnw` | 11.378 |

Floor F = |seg-02 neutral − neutral re-synth| = **0.418s** (two IDENTICAL neutral clips differ
by 0.418s); 3F = 1.254s. synthesis-slower vs neutral = 0.093s; worked_example-slower vs neutral
= 0.464s — **neither clears 3F. Duration verdict (run-2): does NOT clear the bar.**

## Honest finding (first-run-stands, NOT a defect)

The role→voice contract WORKS and is byte-proven: `pedagogical_role` deterministically drives
DISTINCT ElevenLabs settings (`speed=0.94` for synthesis/worked_example vs `1.00` for
definition), verified in every receipt. **But ElevenLabs `speed=0.94` does NOT reliably
lengthen `eleven_multilingual_v2` output vs neutral** — the run-to-run duration variance
(±0.418s measured between two identical neutral clips) swamps the nominal 6% delta. This is
CONSISTENT with the S5 acoustic proof, where the slower pole (0.94) was duration-IDENTICAL to
neutral and the pace→duration PASS came SOLELY from the **faster** pole (speed 1.10). The frozen
`PEDAGOGICAL_ROLE_TO_VOICE` table maps slower-roles to 0.94 and everything else to 1.00 — **no
pedagogical_role emits a faster pace**, so role-derived pacing has no duration-separable pole.

**Recommendation (follow-on, NOT a same-run retry):** if a measurable/audible role-pace tell is
required, the role table's "slower" pace should map to a lower speed (e.g. 0.85) or add a prosody
dial; or accept that role-derived delivery is a settings-level (timbre/stability/style) change,
not a duration change. The enrichment-driven role-paced narration is PROVEN at the contract +
effective-settings level; the duration tell is acoustically underpowered by the table's value.

## Integrity

- Seeds proven APPLIED (role-derived), not EDGE-1 fail-open. Anti-tautology control proven (no
  enrichment → neutral).
- Real distinct request IDs + audio_sha256 + effective settings on disk per clip
  (`run2-enriched/assembly-bundle/receipts/*.json`, `enriched/.../receipts/*.json`).
- First-run-stands honored for BOTH designs; the negative duration result is reported as-is, not
  re-run to green.
- No vision tests run; `tests/fixtures/vision/recordings/` untouched. No git commit.
- ElevenLabs cost: run-1 6×$0.0201 + run-2 4×$0.0636 ≈ **$0.38** (run-2 longer text to fairly
  test the tell; cost-not-a-constraint per project posture).

Artifacts under `_bmad-output/implementation-artifacts/evidence/p5-s7-aligned-20260628T024652Z/`:
`partA-summary.json`, `partA-run2-summary.json`, `enriched/`, `control/`, `run2-enriched/`,
`run2-floor/`.
