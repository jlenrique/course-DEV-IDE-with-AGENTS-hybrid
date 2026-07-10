# PROOF — Tejal P4 continue after Desmond rebase

**Trial:** `22b27500-6e67-4dd7-8308-fd89defe3d99`  
**Evidence:** `tejal-p4-continue-desmond-20260710T060700Z`  
**Prior claim:** Pass-2 speakable-contract fix already PASS-WITH-FENCES at reenter08 pack.

## Desmond substrate fix

| Change | Why |
| --- | --- |
| `HandoffParseError` → `SpecialistDispatchError` | Bare RuntimeError killed the walk (uncaught) instead of recoverable pause |
| `handoff.parsed.advisory-missing` retryable | LLM heading variance — same class as Pass-2 slide-join |
| Accept `## Automation Advisory:` | Common trailing-colon slip |
| Retire taxonomy EXCLUSIONS row | Shrink-only ratchet |

**Unit:** 33 passed (`test_desmond_act_node_authoring`, taxonomy, dispatch_retry).

## Field result

| Check | Result |
| --- | --- |
| Resume G4A | → **completed** |
| Desmond `14.5` | landed; `## Automation Advisory` present |
| Workbook `07W` | landed → `_bmad-output/artifacts/workbooks/u01@1.docx` + `.md` |
| Enrique audio | 9× mp3 under `enrique-narration/assembly-bundle/audio/` |
| Deck PNGs | present under `exports/gary/` |
| Motion | `motion/slide-01.mp4` (partial motion set — known earlier scope) |
| Descript publish | **not** attempted (per success metrics) |

## Verdict

**PASS** for Desmond rebase + walk completion through Desmond + workbook.

Fence (carry from earlier walk, not this patch): motion coverage is slide-01 only, not full-deck motion — score as PARTIAL on motion if metrics require all slides.
