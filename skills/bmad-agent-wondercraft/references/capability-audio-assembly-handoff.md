---
name: audio-assembly-handoff
code: AH
description: Emit Descript project import + assembly guide for manual finish
---

# Capability AH — audio_assembly_handoff

Emit a Descript-compatible project import plus a markdown assembly guide that walks the operator through the manual-finish step (paralleling Story 24-2 for video-post).

## Inbound shape (input_packet)

Required:
- `audio_path` — produced episode audio.
- `script_path` — episode script (used for Descript transcript alignment).
- `chapters_path` — chapter list (from CM capability).

Optional:
- `target_deliverable` — `"full-polish"` / `"cuts-only"` / `"dialogue-cleanup"` — shapes the assembly-guide recommendations.
- `voice_identity_note` — single-line reminder of voice continuity when operator will be re-recording.

## Dispatch logic

1. Build a Descript-import JSON sidecar containing script + audio-path + chapter-marker list.
2. Render an assembly-guide markdown walking through:
   - Descript project opening steps.
   - Recommended cuts (filler words, long pauses).
   - Voice-match touchpoints when re-recording a segment.
   - Expected export specs (MP3 at -16 LUFS for speech content).
3. Round-trip contract: when the operator finishes in Descript and exports, the output flows back into Vera's G5 gate like any other audio artifact.

## Outbound shape

- `descript_project_path` — JSON import sidecar.
- `assembly_guide_path` — markdown guide.

## Non-goals (explicit)

- Direct Descript API integration — the round-trip is intentionally manual because it's a human-judgment surface (filler removal, pacing) that does NOT benefit from automation in v1.
- Automated cut recommendations from ASR — deferred; v1 uses script-structure cues only.

## Test coverage

- Happy path: project JSON + guide MD emitted with correct references.
- `target_deliverable` variations produce differently-shaped guides.
- Missing chapters: guide still valid, notes chapter list was omitted.
