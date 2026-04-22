# Kling Validation Lane

This document defines the exploratory Kling lane for this repo.

## Purpose

The validation lane exists to answer:

- what Kling features are publicly documented
- what the current repo client actually supports
- what request shapes, models, and asset inputs are safe to reuse in production

It is intentionally separate from Gate `7E` production motion generation.

## Separation From Production

### Production lane

- authoritative runner: `skills/production-coordination/scripts/run_motion_generation.py`
- authority source: run-scoped `motion_plan.yaml`
- artifacts live in the active source bundle
- fail-closed behavior is required

### Validation lane

- exploratory runner: `skills/kling-video/scripts/kling_validation_runner.py`
- authority source: checked-in validation cases + live receipts
- artifacts live outside active production bundles
- purpose is learning, not advancing the active lesson state

## Default Validation Output

Validation artifacts should be written under:

`reports/kling-validation/<run-label>/`

Expected files:

- `summary.json`
- `receipts/<case-id>.json`
- generated MP4s in the run root or a subfolder

## Current Policy

Canonical operational references:

- [receipt-contract.md](../../skills/kling-video/references/receipt-contract.md)
- [production-decision-tree.md](../../skills/kling-video/references/production-decision-tree.md)
- [model-feature-matrix.md](../../skills/kling-video/references/model-feature-matrix.md)
- [live-validation-findings-2026-04-07.md](../../skills/kling-video/references/live-validation-findings-2026-04-07.md)

### Silent production

For instructional production work:

- `requested_audio_mode: silent`
- Kling native-audio field is omitted from the API request
- ElevenLabs remains the audio owner

### Native audio / SFX probes

For validation-only exploration:

- selected cases may intentionally request Kling native ambience / SFX
- these probes belong only on the exploratory validation lane
- they do not change the production rule that lesson audio remains owned by ElevenLabs / post
- Singapore-surface `3.0` probes are the preferred place to test this behavior, not the stable `2.6` production lane

### Exploratory Audio Probes vs Production Audio Policy

- production policy remains `silent-by-omission`
- ElevenLabs owns narration and intentional audio for production content
- the validation lane may run bounded probes for Kling native audio or SFX-capable surfaces when the purpose is capability discovery, not production advancement
- success in the validation lane does not promote native audio into production by default
- native-audio or `3.0` probes must write structured receipts and remain non-promoting until separately approved and documented as repo-safe

### Image-to-video

Preferred current pattern:

- use a public Git-hosted slide PNG
- run `image2video`
- preserve composition rather than redesigning the slide
- treat approved stills as the first-choice instructional motion source when they already communicate the lesson clearly

### Kling 3.0

Treat `3.0` as researched but not yet repo-safe until a dedicated client path is added for the newer Singapore API surface.

The repo now carries that exploratory Singapore-surface client in validation-only mode. Keep production decisions pinned to the validated `2.6` lane until the Singapore-surface receipts prove stable for your account and the exact provider-exposed `3.0` model id is confirmed.

### Start Here

For reproducible success patterns, begin with:

- `skills/kling-video/references/successful-look-playbook.md`

Use the `Top Validated Kling Looks` section there as the current shortlist of patterns worth repeating before inventing new prompt families.

## Suggested Commands

List available validation cases:

```powershell
python skills/kling-video/scripts/kling_validation_runner.py list
```

Run one case:

```powershell
python skills/kling-video/scripts/kling_validation_runner.py run `
  --case-id I1-image2video-std-silent `
  --image-url https://example.com/slide.png
```

Run multiple cases into a labeled report folder:

```powershell
python skills/kling-video/scripts/kling_validation_runner.py run `
  --case-id I1-image2video-std-silent `
  --case-id I2-image2video-pro-silent `
  --image-url https://example.com/slide.png `
  --run-label 20260407-slide01-comparison
```

## Current Planned Suites

- baseline provider capability probes in `skills/kling-video/references/validation-cases.yaml`
- the broader slate in [kling-mini-production-roadmap.md](../../skills/kling-video/references/kling-mini-production-roadmap.md)
- dedicated static-to-life Gamma sub-suite using selected visuals from [labels.md](../../resources/Gamma-visuals/labels.md)
