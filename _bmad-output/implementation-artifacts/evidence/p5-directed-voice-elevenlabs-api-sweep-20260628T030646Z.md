# ElevenLabs API exploration sweep — P5 directed-voice arc (§10 item 5)

**UTC stamp:** 20260628T030646Z
**Lane:** BROADER API-exploration sweep — deliberately DISTINCT from the production heartbeat (the v1 product contract).
**Goal:** exercise every locally-available ElevenLabs request parameter at least once with a REAL live call, or record precisely why it is unavailable. No mocks. First-run-stands honesty.

**Script:** `scripts/diagnostics/elevenlabs_api_sweep.py`
**Raw per-call log:** `_bmad-output/implementation-artifacts/evidence/p5-directed-voice-elevenlabs-api-sweep-20260628T030646Z.calls.json`
**Machine summary:** `_bmad-output/implementation-artifacts/evidence/p5-directed-voice-elevenlabs-api-sweep-20260628T030646Z.summary.json`
**Captured audio:** `_bmad-output/implementation-artifacts/evidence/elevenlabs-sweep-audio/` (`baseline.mp3` 22,613 B; `mp3_44100_64.mp3` 11,328 B; `pcm_16000.pcm` 46,068 B)

---

## Header summary (account / environment)

| Field | Value |
|---|---|
| **Account tier / quota** | **UNAVAILABLE** — the API key is permission-scoped and is MISSING the `user_read` permission. `GET /user` and `GET /user/subscription` both return `401 missing_permissions: "The API key you used is missing the permission user_read to execute this operation."` Tier and character quota could not be read. |
| **Models the account may use (`can_do_text_to_speech`)** | `eleven_v3`, `eleven_multilingual_v2`, `eleven_flash_v2_5`, `eleven_turbo_v2_5`, `eleven_turbo_v2`, `eleven_flash_v2`, `eleven_monolingual_v1`, `eleven_multilingual_v1` |
| **Voice used (constant across the sweep)** | `Roger - Laid-Back, Casual, Resonant` — `voice_id = CwhRBWXzGAHq8TQ4Fs17` (premade); 45 voices total available |
| **Default model exercised** | `eleven_multilingual_v2` (client default) |
| **Alternate model exercised** | `eleven_turbo_v2_5` (for `model_id`, `language_code`) |
| **Sweep text** | `"Hello from the sweep."` (~21 chars) — short to bound cost |
| **Provisioned pronunciation dictionary?** | YES — a real dictionary exists in the workspace (`id=S9kBtj1zC1Y4JhZ7sX8p`, `version_id=azkfwg2CGGfczBEaS9nd`), so the locator parameter was exercised for real, not faked. |

---

## Parameter table — one row per locally-available TTS parameter

| Parameter | Value(s) exercised | Live result | request_id(s) or error | Note |
|---|---|---|---|---|
| `model_id` | `eleven_turbo_v2_5` (vs default `eleven_multilingual_v2`) | **ACCEPTED** | `ERRAL1aop75pUfdhJ0b8` (baseline `nrH0cerR1P0KSJM9ufz4`) | Alternate model produced different audio (24,285 B vs 22,613 B). 8 TTS-capable models available. |
| `stability` | `0.3` | **ACCEPTED** | `0c8RuxCL9iyHhfDkF7o6` | voice_settings field; accepted. |
| `similarity_boost` | `0.9` | **ACCEPTED** | `jWpuLXUbyAOXF58Gh9DX` | voice_settings field; accepted. |
| `style` | `0.6` | **ACCEPTED** | `Y19rPRpkPqTazIKfBBJD` | voice_settings field; accepted (note `eleven_v3` reports `can_use_style:false`, but default multilingual_v2 accepted it). |
| `speed` | `1.15` | **ACCEPTED** | `BwpADDS1Baa5VY2Uhj6j` | Faster playback → smaller payload (19,688 B). |
| `use_speaker_boost` | `True` | **ACCEPTED** | `FyZ0LAqlQg2ScgwDnzsI` | voice_settings field; accepted. |
| `output_format` | `mp3_44100_128` (default), `mp3_44100_64`, `pcm_16000` | **ACCEPTED** (all 3) | `f6ddKlQx64cnzaYAf7mB` / `NqVx8kpKq9W6JL0T1A4m` / `ULvtfs1TMTBPy0Fpl20b` | Sizes scale as expected: 128k MP3=24,285 B; 64k MP3=11,328 B; raw PCM16k=46,068 B. |
| `language_code` | `"en"` on `eleven_turbo_v2_5` | **ACCEPTED** | `ur68ab9yKDLJ8KwoGcCI` | Exercised on a turbo model (which honors it). |
| `pronunciation_dictionary_locators` | real locator `{id:S9kBtj1zC1Y4JhZ7sX8p, version_id:azkfwg2CGGfczBEaS9nd}` | **ACCEPTED** | `ySrScCe6zdSh2iJ4LFYq` | A real provisioned dictionary exists in the workspace, so this was a genuine locator, not a stub. |
| `seed` | `12345`, run TWICE identically | **ACCEPTED + DETERMINISTIC** | `HdYlqWv7oqIm4MDPjvNx` / `3qUy7U6EbAUmISZKfZDL` | Both calls returned **BYTE-IDENTICAL** audio (same MD5). Seed is real, reproducible determinism. |
| `previous_text` | `"This is the prior sentence."` | **ACCEPTED** | `oB9Gb8rHjaGcI3UpuuXZ` | Continuity context accepted. |
| `next_text` | `"And this follows after."` | **ACCEPTED** | `C08KkeDy2Lb9f64CTsJN` | Continuity context accepted. |
| `previous_request_ids` | `[nrH0cerR1P0KSJM9ufz4]` (real baseline id) | **ACCEPTED** | `oJ1oKhHwRfTv9I4k8TeG` | Stitching with a REAL prior request_id accepted. |
| `next_request_ids` | `[nrH0cerR1P0KSJM9ufz4]` (real baseline id) | **ACCEPTED** | `NiK0OxmZgI3qoVrGK36M` | Stitching accepted. |
| `use_pvc_as_ivc` | `True` | **ACCEPTED** | `mkKMTN7u26O3rp2eApCe` | Accepted (no PVC voice in play, but parameter not rejected). |
| `apply_text_normalization` | `"auto"`, `"on"`, `"off"` | **ACCEPTED** (all 3) | `l0wzROipPTCzQxzwKOOl` / `psBeB09TcURSnT9qt4vC` / `A73W73W3c4650LDSPyqi` | All three enum values accepted. |
| `apply_language_text_normalization` | `True` (no language_code); `True`+`language_code="ja"`; `True`+`en`/`zh` | **PARTIAL** — ACCEPTED only with a supported language | ACCEPTED `ja`: `9LNNNF9HdzVNRHtiXs7g` (turbo), `APQZUwjKIVylakbYMBDN` (multilingual). REJECTED w/o lang: `400 language_text_normalization_not_supported` (request_id `825223dd…`). REJECTED `en`/`zh`: same `400`. | Requires a `language_code` AND that language to be in the supported subset. Japanese works; English/Chinese explicitly rejected by the API. |
| `text_to_speech_with_timestamps` (endpoint) | default params | **ACCEPTED** | `f44gVEdbctdfPpG261rq` | Returned 21 character-level timestamps (`alignment.characters` = `['H','e','l','l','o',' ','f','r', …]`) with start/end times. Character timestamps confirmed live. |

### Non-TTS endpoints

| Endpoint | Result | Note |
|---|---|---|
| `get_user` | **UNAVAILABLE (401)** | Missing `user_read` key permission (see header). |
| `list_models` | **ACCEPTED** | 8 TTS-capable models enumerated. |
| `list_voices` | **ACCEPTED** | 45 voices. |
| `get_voice` | **ACCEPTED** | Detail fetched for the sweep voice. |

---

## Findings vs the v1 production contract (EXPLORATION findings — not contract changes)

These are exploration observations about which explored parameters are *candidates* to graduate into the product contract beyond pace (`speed`). **Nothing here changes the v1 contract; it is input for a future contract decision.**

- **`seed` (determinism) — strong graduation candidate.** Two identical seeded calls returned byte-identical audio. If the directed-voice path ever needs reproducible re-renders (cache validation, regression diffing, deterministic re-runs of a fixed script), `seed` is the lever and it provably works on this account.
- **`output_format` — graduation candidate.** Real, predictable control over codec/bitrate (`mp3_44100_64` ≈ half the bytes of `mp3_44100_128`; `pcm_16000` for downstream DSP). Useful for bandwidth/quality trade-offs and for feeding tools that want raw PCM.
- **`apply_text_normalization` (`auto`/`on`/`off`) — graduation candidate.** All three values accepted; relevant wherever numerals/abbreviations in narration need controlled spoken expansion (ties to the VO figure-grounding bar).
- **`previous_text` / `next_text` and `previous_request_ids` / `next_request_ids` — candidates for multi-segment narration continuity.** Accepted with real ids; the natural fit for stitching consecutive narration segments without prosody seams.
- **`language_code` — conditional.** Honored on turbo/flash models; pair with model selection if multilingual narration is ever in scope.
- **`apply_language_text_normalization` — narrow / English-irrelevant.** Only works for a supported-language subset (Japanese accepted; English and Chinese explicitly rejected). Not useful for an English v1 contract.
- **`use_pvc_as_ivc` — not actionable without a PVC voice.** Accepted but inert in this account context.
- **Operational caveat for the product contract:** the in-use API key is **scoped without `user_read`**, so any product code that calls `get_user` for quota/tier introspection will 401. The synthesis endpoints themselves are fully authorized; only account-introspection is gated. Worth noting if the product ever wants to surface remaining-quota.

---

## Cost & call accounting

- **Live calls made:** ~39 total live HTTP calls — of which ~31 were billable TTS generations (23 in the main sweep + 1 timestamps + 6 follow-up `apply_language_text_normalization` probes + 1 standalone 401-diagnostic batch). The rest were `list_voices`/`list_models`/`get_voice` (free) and `get_user` 401s (free).
- **Characters generated:** ~31 generations × ~21 chars ≈ **~650 characters** of TTS.
- **Approximate cost:** **negligible — well under $0.05**, far under the ~$1 ceiling. (Exact quota consumption could NOT be confirmed via `get_user` because the key lacks `user_read`; the estimate is from character count × generation count.)

## Honest surprises (first-run-stands)

1. **`get_user` is 401 by key-scope, not a bad key** — the same key that successfully drives ~31 live TTS generations cannot read `/user`. The key is deliberately permission-scoped (`user_read` withheld). This is the one genuinely "UNAVAILABLE" item and it's an account/key-scope fact, not a parameter limitation.
2. **`seed` really is byte-identical-deterministic** on this account — I half-expected provider-side nondeterminism; two identical seeded calls produced the same MD5.
3. **`apply_language_text_normalization` is not a simple boolean** — it 400s unless a *supported* `language_code` accompanies it (Japanese passed; English/Chinese were explicitly rejected with `language_text_normalization_not_supported`).
4. **A real pronunciation dictionary was already provisioned** in the workspace, so that locator parameter got a genuine ACCEPTED rather than the expected "no dictionary" rejection.
