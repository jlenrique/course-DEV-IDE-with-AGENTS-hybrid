---
title: Production Prompt Pack v4.3 — Narrated Lesson with Video/Animation
status: superseded-by-v5 (2026-05-07; pre-Trial-3 cleanup S4 close)
superseded-by: production-prompt-pack-v5-narrated-lesson-with-video-or-animation.md
original-status: ready (2026-04-11; Storyboard A C1M1 trial run; paused before completion)
note: |
  **SUPERSEDED.** This pack's cluster-mode content (cluster prompt engineering 21-2 / dispatch sequencing 21-3
  / cluster coherence validation 21-4) was already absorbed into v4.2 §05B / §6.2 / §6.3 / §7.5. v5 inherits
  v4.2's full content (with migrated runtime paths + post-Slab-7c roster); v4.3 has no v4.3-only content beyond
  what already lives in v4.2/v5. Preserved here for git-history reference only — DO NOT EDIT or use for production runs.
  Use `docs/workflow/production-prompt-pack-v5-narrated-lesson-with-video-or-animation.md` (canonical-for-production).
---

# Overview
v4.3 reflects the current pipeline with cluster-aware prompt engineering (21-2), dispatch sequencing (21-3), and cluster coherence validation (21-4), plus the ffmpeg remediation and Marcus upgrades from the interstitial slides epic. Use this pack for narrated lessons with optional motion.

# Pre-flight (run before anything else)
1) Activate env (pyenv acceptable; .venv present):  
   `python -m pip install -r requirements.txt`
2) FFmpeg resolution: handled via `scripts/utilities/ffmpeg.py` (checks .venv/Scripts/bin, bin/ffmpeg.exe, PATH, imageio-ffmpeg). No manual override needed unless custom path (`FFMPEG_BINARY`).
3) Session readiness (with preflight checks):  
   `python scripts/utilities/app_session_readiness.py --with-preflight`
4) Confirm credentials in `.env` for Gamma, ElevenLabs, Canvas/Notion/Box if used.

# Source Materials (Storyboard A)
- Primary: `course-content/courses/APC C1-M1 Tejal 2026-03-29.pdf`
- Secondary: `course-content/courses/APC Content Roadmap.jpg`
- Optional .docx companion: `course-content/courses/APC C1-M1 Tejal 2026-03-29.docx`

# Run Constants (drop-in exemplar for trial)
Save as `run-constants.yaml` in your bundle directory (e.g., `course-content/staging/storyboard-a-trial/`):
```yaml
run_id: "SB-A-TRIAL-001"
lesson_slug: "c1m1-tejal"
bundle_path: "course-content/staging/storyboard-a-trial"
primary_source_file: "course-content/courses/APC C1-M1 Tejal 2026-03-29.pdf"
optional_context_assets:
  - "course-content/courses/APC Content Roadmap.jpg"
theme_selection: "theme-a"
theme_paramset_key: "preset-a"
execution_mode: "tracked/default"
quality_preset: "production"
cluster_density: "sparse"
double_dispatch: false
motion_enabled: false
```

# Pipeline Gates (ordered)
1) **G0 Pre-flight**: `app_session_readiness --with-preflight`
2) **G1.5 Cluster Plan Gate**: `python skills/bmad-agent-marcus/scripts/run-g1.5-cluster-gate.py --bundle-dir <bundle>`
3) **21-2 Prompt Engineering**: `python skills/bmad-agent-marcus/scripts/cluster_prompt_engineering.py --cluster <cluster.json>`
4) **21-3 Dispatch Sequencing**: `python skills/bmad-agent-marcus/scripts/cluster_dispatch_sequencing.py --clusters <clusters.json>`
5) **Gamma Generation**: use Marcus orchestration as normal (prompt output feeds dispatch plan).
6) **21-4 Coherence Validation**: `python skills/bmad-agent-marcus/scripts/cluster_coherence_validation.py --manifest <manifest.yaml> --outputs <generated.yaml>`
7) **HIL Review (Storyboard A)**: operator review + approvals; then finalize.

# Operator Prompt Sequence (Marcus-led)
Use these in order during the run:
1) **Initialization**  
   “Marcus, start Storyboard A trial run SB-A-TRIAL-001 using the bundle at `course-content/staging/storyboard-a-trial` with run-constants.yaml loaded. Confirm preflight status.”
2) **Cluster Plan Check (G1.5)**  
   “Marcus, run the G1.5 cluster gate on the current bundle and report PASS/FAIL with errors.”
3) **Prompt Engineering (21-2)**  
   “Marcus, render cluster-aware prompts for all clusters in Storyboard A using prompting.yaml. Return prompt_ids, hashes, and token budgets.”
4) **Dispatch Plan (21-3)**  
   “Marcus, build the dispatch plan with dispatch.yaml policy (priority_size_id, batch_size=2, max_concurrency=4). Return plan_hash and batch schedule.”
5) **Gamma Generation**  
   “Marcus, execute Gamma generation per dispatch plan. Use interstitial visual constraints and respect cluster metadata.”
6) **Coherence Validation (21-4)**  
   “Marcus, run cluster coherence validation with validation.yaml. Report decision, report_hash, and any violations.”
7) **HIL Decision**  
   “Marcus, prepare the HIL packet for Storyboard A with outputs, validations, and operator checklists. Await my approval.”

# Notes & Updates vs v4.2
- Added 21-2/21-3/21-4 steps and commands.
- ffmpeg resolution hardened (no manual path required if in .venv/bin or bin/ffmpeg.exe).
- Marcus current definition (post interstitial epic): baton/authority checks unchanged; new constraints, dispatch, validation steps reflected above.

# Quick Reference Paths
- Prompting config: `state/config/prompting.yaml`
- Dispatch config: `state/config/dispatch.yaml`
- Validation config: `state/config/validation.yaml`
- Cluster gate: `skills/bmad-agent-marcus/scripts/run-g1.5-cluster-gate.py`
- Prompt renderer: `skills/bmad-agent-marcus/scripts/cluster_prompt_engineering.py`
- Dispatch sequencer: `skills/bmad-agent-marcus/scripts/cluster_dispatch_sequencing.py`
- Coherence validator: `skills/bmad-agent-marcus/scripts/cluster_coherence_validation.py`

# HIL Checklist (Storyboard A)
- Cluster gate PASS recorded
- Prompt hashes recorded
- Dispatch plan hash recorded
- Coherence report hash recorded
- All violations resolved or accepted with rationale
- Final operator approval logged
