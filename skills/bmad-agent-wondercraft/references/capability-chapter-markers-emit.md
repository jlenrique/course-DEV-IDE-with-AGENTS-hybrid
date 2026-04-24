---
name: chapter-markers-emit
code: CM
description: Generate chapter-marked output + metadata
---

# Capability CM — chapter_markers_emit

Emit chapter markers for an episode based on script structure.

## Inbound shape (input_packet)

Required:
- `audio_path` — produced episode audio.
- `script_path` — the episode script (used to derive chapter boundaries from structure).

Optional:
- `chapter_policy_mode` — `"derive-from-beats"` (default) / `"explicit"` (requires `explicit_markers`) / `"none"`.
- `explicit_markers` — operator-supplied list of `{title, start_seconds}` when mode is `"explicit"`.
- `emit_m4a` — if `true`, re-container the audio as M4A with embedded chapter metadata (Apple-Podcasts-friendly); default `true` for dialogue-heavy content.

## Dispatch logic

1. Parse script for structure cues: `[beats]` / `[sections]` / `## H2` headings.
2. Compute `start_seconds` for each chapter from cumulative narration duration (summing per-beat word counts / speech rate).
3. Emit a chapter-list JSON alongside the audio.
4. If `emit_m4a`, re-container MP3 as M4A with `ffmpeg` + chapter metadata.

## Outbound shape

- `chapters_path` — JSON list of `{title, start_seconds, end_seconds}`.
- `audio_m4a_path` — optional M4A with embedded metadata.
- `diagnostics.chapter_markers` — echoed into the receipt.

## Non-goals

- Reading chapter markers from audio itself (ASR chapter detection) — deferred; chapters are structural, not acoustic.

## Test coverage

- Happy path: 5-beat dialogue script → 5 chapters, monotonic `start_seconds`.
- Explicit-markers path: operator-supplied list preserved verbatim.
- `mode: "none"` path: capability returns `outcome=complete` with empty chapter list.
- M4A emission toggle.
