# Story 7b.9 Codex Self-Review - 2026-04-29

## Scope

Wanda was port-shaped onto the Class-C scaffold for Wondercraft audio-bed
generation. The legacy Wanda sidecar was migrated into the canonical six-file
BMB sanctum, `skills/bmad-agent-wanda/SKILL.md` was created, and
`skills/bmad-agent-wondercraft/SKILL.md` was preserved without modification.

## Findings

No blocking self-review findings.

## Checks

- Focused Wanda/parity/composition battery: `71 passed, 1 skipped, 1 deselected`.
- Broad regression slice: `1325 passed, 21 skipped, 1 deselected`.
- `validate_parity_test_class_conformance.py tests/parity/`: PASS with 9 activation contracts.
- `validate_migration_story_sandbox_acs.py` on Story 7b.9: PASS.
- `detect_live_api_in_tests.py`: PASS, scanned 75 test files.
- Story-scoped ruff: PASS.
- Pipeline manifest lockstep: PASS.
- Import-linter: 9/9 contracts KEPT.

## Notes For Review

- T1 baseline differed from the spec: Wanda's legacy sanctum was present at
  `_bmad/memory/wanda-sidecar/`, not `_bmad/memory/bmad-agent-wanda/`.
  The sidecar content was folded into the new canonical BMB files and the
  legacy sidecar path was removed.
- `WondercraftClient.generate_audio_bed` is invoked when available on the
  client object; the shipped client fallback uses the existing
  `create_scripted_podcast` path because `scripts/api_clients/wondercraft_client.py`
  is story-frozen.
- Operator-gated live canary evidence is not executed by Codex and remains for
  Claude/operator close.
