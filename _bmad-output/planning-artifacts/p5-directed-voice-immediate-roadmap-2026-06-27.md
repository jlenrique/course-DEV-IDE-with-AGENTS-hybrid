# P5 Directed Voice Immediate Roadmap

Date: 2026-06-27

## Intent

Complete the P5 arc as the next shippable product slice, but promote directed synthesized voice from a later enhancement into the immediate release path. P5 is not complete unless enriched deck/narration consumption and per-clip voice direction are both visible in the learner-facing terminal bundle.

## Governance

- Use BMAD workflows for story creation, implementation, reviews, and closure.
- Use fully spawned, tailored `bmad-party-mode` teams for all major green-light, review, approval, and next-step decisions.
- Run `bmad-code-review` before any story is marked done.
- Prefer RED-first tests, live proofs for production claims, and no-mock final evidence.

## Immediate Steps And Completion States

| Step | Work | Completion state |
|---:|---|---|
| 1 | Define per-segment `voice_direction` contract. | Contract documented and schema/model/test fixtures updated; supports `render_strategy`, delivery intent, tone, pace, energy, pauses, optional ElevenLabs settings, and optional dialogue turns. |
| 2 | Extend CD/Irene/script output. | Pass-2 narration/segment-manifest generation can emit `voice_direction` per segment without breaking existing manifests. |
| 3 | Upgrade Storyboard B. | Storyboard B displays each segment's approved script plus voice direction before any ElevenLabs spend; header still shows global defaults. |
| 4 | Update Enrique/ElevenLabs consumption. | Enrique reads segment-level direction, maps it to TTS settings/tags, preserves existing `voice_id` overrides, and keeps global defaults as fallback. |
| 5 | Add directed-audio tests. | Unit/integration tests prove two adjacent segments can generate with different voice settings and receipts without mutating locked source artifacts. |
| 6 | Live directed-audio proof. | One live small-slice run produces multiple clips with materially different approved delivery directions and captured receipts. |
| 7 | P5-S2 deck/narration enrichment consumption. | Gary/enriched deck path and Enrique narration consume `G0EnrichmentResult` fields such as `teaches_after`, `pedagogical_role`, and `lo_refs`; default deck path remains regression-safe/flag-gated. |
| 8 | Terminal Descript enriched bundle. | One honest enriched bundle reaches the proven Descript path using enriched deck/narration/workbook plus directed audio; real spend evidence is captured. |
| 9 | CF-A true E2E runner. | `run_g0_enrichment -> 07W` and the P5 consumption path run through the production runner continuation walk, preserving enrichment and voice-direction metadata. |

## Near-Term Follow-Ons

- Add `render_strategy: dialogue` for true multi-speaker cases using ElevenLabs Text-to-Dialogue.
- Add a separate media-placement decision for standalone/module videos versus deck motion clips.
- Include directed-voice outcomes in later Epic 15 learning ledger work so Marcus/CD can learn from operator-approved direction choices.

