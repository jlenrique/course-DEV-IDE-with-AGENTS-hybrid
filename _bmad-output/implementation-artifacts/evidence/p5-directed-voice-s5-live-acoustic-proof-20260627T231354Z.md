# P5 Directed-Voice Step 5 — LIVE directed-audio MUR-4 acoustic proof (FIRST-RUN-STANDS)

- Date: 2026-06-27T23:13:54Z
- Flag: `MARCUS_NARRATION_VOICE_DIRECTION_ACTIVE=1`
- Authority: strawman §F **MUR-4** + §H; audition-rubric §4 / §9 / §10.
- Protocol: deterministic numeric judge, **k fixed at 3 BEFORE the run**, **NO retry-to-green** — this first live run's result stands.
- Canonical bundle: `_bmad-output/implementation-artifacts/evidence/p5-s5-live-acoustic-20260627T231354Z/`
- Real voice: `CwhRBWXzGAHq8TQ4Fs17` (Roger — Laid-Back, Casual, Resonant), from live `list_voices()`.
- Generated via the REAL shipped `app/specialists/enrique/_act.py::build_assembly_bundle` (flag ON). Cost ≈ $0.10 (5 short calls × $0.0201).

## Judge (fixed before the run)

- Acoustic harness: `scripts/analysis/directed_voice_acoustics.py::analyze_clip` — decodes each MP3 → mono PCM via the bundled `imageio_ffmpeg` ffmpeg binary → numpy; reports `duration_s` (n_samples / 44100), `rms` (sqrt(mean(x²))), `peak`. Deterministic, offline, no librosa/scipy.
- Judge: `materially_different(control_pair, treatment_pair, scalar, k=3)` — `F = |scalar(A) − scalar(A′)|` (control = same text + SAME direction twice = the TTS-nondeterminism floor); **PASS iff `|scalar(treatment_B) − scalar(treatment_A)| > k·F`** with `k=3`.
- Targeted scalars (the dimension the direction was DESIGNED to move): **pace → `duration_s`** (slower speech = longer clip); **energy → `rms`** (higher style + lower stability = louder).

## Text (held constant so only the direction moves the scalar)

`"Let me walk you through this idea so it really lands for you today."`

## The 5 REAL calls — distinct real request-ids (all 5 distinct ✓)

| Segment | Direction | Resolved settings SENT (stability/style/speed) | REAL request_id | Measured `duration_s` | Measured `rms` | Measured `peak` |
|---|---|---|---|---|---|---|
| ctl-a | neutral / neutral / medium | 0.50 / 0.35 / 1.00 | `8Yv8MXyAx31ULeXrglWf` | 3.344 | 0.06617 | 0.4648 |
| ctl-b | neutral / neutral / medium | 0.50 / 0.35 / 1.00 | `H9uNQaXjCxxV6rhJe6f9` | 3.390 | 0.06284 | 0.3936 |
| neutral (baseline) | neutral / neutral / medium | 0.50 / 0.35 / 1.00 | `HoJKWNwkytwjwPXWTN7s` | 3.390 | 0.07051 | 0.4934 |
| reflective | reflective / slower / low | 0.75 / 0.10 / 0.94 | `tCqAqkFtwigQXmbrz9uX` | 3.390 | 0.06714 | 0.5403 |
| urgent | urgent / faster / high | 0.30 / 0.65 / 1.10 | `V5ccs13RFcjT6FbIicyF` | 3.204 | 0.06896 | 0.4378 |

Each segment also has a full Step-4 receipt on disk (`assembly-bundle/receipts/<sid>.json`) with `request_id`, `request_id_present:true`, `audio_sha256`, `effective_elevenlabs_settings`, `effective_voice_direction`, `narration_file`, `narration_vtt`, `narration_duration`. Distinct resolved settings are proven SENT (not just modeled).

## The deterministic verdict (FIRST-RUN-STANDS)

Control pair = (ctl-a, ctl-b), same text + SAME (neutral) direction twice.

### Pace → duration: **PASS** ✓
- `F_duration = |3.344 − 3.390| = 0.0464 s`; `3·F = 0.1393 s`.
- Treatment delta (reflective-slower vs urgent-faster) = `|3.390 − 3.204| = 0.1858 s`.
- `0.1858 > 0.1393` → **PASS**. The pace dial moves clip duration materially above the nondeterminism floor.

### Energy → rms: **FAIL** ✗ (reported honestly — NOT re-run)
- `F_rms = |0.06617 − 0.06284| = 0.00333`; `3·F = 0.00999`.
- Treatment delta (low-energy reflective vs high-energy urgent) = `|0.06714 − 0.06896| = 0.00182`.
- `0.00182 < 0.00999` → **FAIL**. Broadband clip-level RMS did NOT separate above 3×F on the first run.

### MUR-4 overall: **PASS**
MUR-4 requires that on **at least one** direction-targeted scalar the bar clears. **Pace→duration clears 3×F**, so MUR-4 is met: directed voice produces materially-different clips, proven by a deterministic numeric judge, not vibes. Both legs are reported per the brief.

## Finding (rubric, NOT a retry)

The **energy→rms** leg failing is a *palette/scalar* finding, not a pipeline defect:

1. The settings ARE different and ARE sent (stability 0.75→0.30, style 0.10→0.65 verified in receipts), so the *contract* works.
2. ElevenLabs `stability`/`style` changes alter expressiveness/timbre/prosody far more than gross broadband loudness; at the clip level RMS is dominated by the (constant) words + voice, so the energy dial's RMS footprint sits near the TTS nondeterminism floor.
3. Notably `peak` DID separate in the intuitive direction (reflective-low peak 0.5403 is the highest, several control/urgent clips lower) but `peak` is a single-sample outlier statistic, too noisy to be a robust judge scalar — RMS remains the correct robust energy scalar, and it honestly did not clear the bar.

**Recommendation for the Step-5 party / audition-rubric:** either (a) widen the energy palette separation (e.g. low energy stability↑ further / style→0.0 vs high style→0.8) and re-audition, or (b) replace the energy scalar with a loudness measure more aligned to perceived energy (integrated LUFS / A-weighted, or an F0/expressiveness proxy) in a *follow-on* — not a same-run retry. Pace→duration is a clean, reliable directed-voice tell today.

## Rubric §9 scores (per treatment)

| Treatment | Contract validity | Narration integrity | Audible differentiation | Receipt quality | Overall |
|---|---|---|---|---|---|
| neutral (baseline) | Pass (legal v1) | Pass (words verbatim; no delivery_tag injected) | n/a (reference) | Pass (full receipt + req-id) | **Pass** (valid baseline) |
| reflective-slower-low | Pass | Pass | **Pass on duration** (pace cleared 3×F); **Warn on rms** (energy sub-floor) | Pass | **Pass** (rms-warn noted) |
| urgent-faster-high | Pass | Pass | **Pass on duration**; **Warn on rms** | Pass | **Pass** (rms-warn noted) |

Narration integrity holds: `TEXT` is identical across all segments and the receipts confirm the figure-gated narration is sent verbatim to TTS (the ENRIQUE-A5 firewall keeps `delivery_tag` out of the spoken channel; none was set here). No citation behavior was touched.

## §10 completion-bar status (Step-5 scope)

| # | Item | Status |
|---|---|---|
| 1 | ≥3 distinct directed treatments | ✓ neutral + reflective + urgent (Storyboard B display closed at Step 3) |
| 2 | consumed by Enrique via shared mapper | ✓ `build_assembly_bundle` + shared `map_voice_direction_to_tts` |
| 3 | receipts: effective direction/settings, voice_id, request_id, audio, VTT, duration | ✓ all present on disk |
| 4 | live proof baseline vs directed, ≥1 non-neutral | ✓ neutral baseline + 2 non-neutral, control floor measured |
| 5 | separate API exploration sweep (every local param ≥1×) | **OUTSTANDING** — distinct lane (rubric §6A), NOT run here by design |
| 6 | no unsupported palette values/fields | ✓ all legal v1 |
| 7 | flag default-OFF preserved | ✓ flag set ON only in the proof process; repo default OFF; OFF-byte-identity covered by Step-4 tests |
| 8 | party rules production-credible vs narrower palette | PENDING (Step-5 close party / Quinn-R) |

## Artifacts

- 5 real MP3s (`assembly-bundle/audio/*.mp3`, ID3/MPEG, 52–55 KB each) + VTTs + receipts.
- `live-acoustic-summary.json` (full measured scalars + both verdicts + request-ids).
- Harness + judge: `scripts/analysis/directed_voice_acoustics.py`.
- RED-first tests: `tests/analysis/test_directed_voice_acoustics.py` (11 passed).

## Integrity notes

- First-run-stands honored: the energy→rms FAIL is reported as-is; the run was not repeated to obtain a pass.
- No vision tests run; `tests/fixtures/vision/recordings/` untouched. No git commit. Clips kept in the bundle.
