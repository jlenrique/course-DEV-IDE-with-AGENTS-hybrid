# Kira Sidecar

**Agent:** Kira (Video Director)
**Role:** Kling AI video generation specialist; B-roll, concept visualizations, slide-to-video transitions, lip-sync overlays, section-bridge clips
**Status:** Active
**Skill path:** `skills/bmad-agent-kling/`

## Active Context

- Kira is invoked primarily through Marcus's envelope; interactive mode available for prompt tuning and capability exploration
- Production posture: `kling-v2-6` is the validated path; silent production omits native-audio field entirely
- `image2video` from approved static visuals is the highest-priority instructional motion strategy
- For Gate 7E production runs: use `skills/production-coordination/scripts/run_motion_generation.py`; for exploratory work: use `skills/kling-video/scripts/kling_validation_runner.py`
- Reads `resources/style-bible/` fresh every task for visual tone and professional medical aesthetic
- Canonical quick-start shortlist lives in `skills/kling-video/references/successful-look-playbook.md`

## Files in This Sidecar

- `index.md` — this file
- `patterns.md` — durable learnings about prompts-that-work, source-asset combinations, cost-aware model/mode/duration defaults per content type, prompt signatures that produce clean image2video transitions
- `chronology.md` — append-only log of video generations performed and their outcomes
- `access-boundaries.md` — read/write/deny zones for Kira

## Creation History

- **2026-04-16:** Sidecar created as part of the 2026-04-16 sidecar-gap pass. Kira had a fully-developed SKILL.md but no memory sidecar; this file closes that gap. Persona name "Kira" was already in place — no rename.

## Preferences / Standing Guidance

- Always prefer image2video from approved static visuals over text-to-video for instructional content — reuse Gary/Gamma outputs and Irene's briefs when they are the strongest inputs
- Production state is only patched after local MP4 validation succeeds
- Progress receipts are authoritative for resume and duplicate-prevention — never re-generate without checking
- Singapore 3.0 surface is exploratory until separately integrated; do not promote it into production runs
