---
title: 'dp-v1.2 review-rider hygiene mini-batch (Winston R1/R2, Amelia R2, Murat R1/R2, John R1)'
type: 'chore'
created: '2026-06-12'
status: 'done'
baseline_commit: 'ebe0c3f'
checkpoint_1: 'approved via operator standing directive 2026-06-12 ("proceed directly to address the next rider, and push all after successful remediation")'
context:
  - '{project-root}/_bmad-output/planning-artifacts/deferred-inventory.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The dp-v1.2 review (4× APPROVE) left six rider rows in `dp-v1.2-review-riders-bundle` whose ratified resolution shape is "execute as a hygiene mini-batch at next substrate touch of the respective files" — and the phantom-delta fix just touched several of them. Each row is a small honesty/robustness defect: a self-comparing test that can never fail, a repo-root default path that produced stray `runs/enrique-narration/` artifacts, 42 lines of dead code that looks load-bearing, an evadeable audit regex, exclusion keys a name-reuse would inherit, and an allowlist row with no retirement trigger.

**Approach:** Execute all six rows as one batch (party-ratified bundling; operator directed proceed). Test/audit-surface strengthening + dead-code deletion only — zero live-path behavior change except converting enrique's unreachable default-path fallback into a fail-loud typed raise (production always injects a run-scoped `bundle_path` at `_act.py:343`; verified by direct-caller audit).

## Boundaries & Constraints

**Always:** Engine FROZEN for Trial A — deletions and test strengthening only; any raise added must be a typed recoverable `EnriqueActError` with a stable tag. Shrink-only discipline on EXCLUSIONS (qualifying keys must not widen what's excluded). Existing test semantics preserved except where a rider explicitly names the test as defective.

**Ask First:** Touching kira/wanda `DEFAULT_BUNDLE_PATH` (same pattern, NOT in this rider — taxonomy re-base territory). Any change to the join policy or grounding semantics. Removing the (11B, elevenlabs) allowlist row itself (only its retirement TIE is in scope).

**Never:** No gate-engine/fold-semantics changes (voice-HIL fold is Wave 1). No pipeline-manifest edits. No re-litigating the rider dispositions.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Enrique payload without `bundle_path` (direct caller) | voice or synthesis leg | Fail loud, no repo-root writes | `EnriqueActError`, tag `elevenlabs.bundle.path-missing` |
| Production dispatch (node 11/11B/12) | `act()` injects run-scoped path | Unchanged | N/A |
| Inline roster literal with whitespace/renamed id in app/ | `[ { 'slide_id' : 'intro-1' } ]` | Ninth-seam ratchet catches it | audit test fails naming module |
| New error class reusing an excluded bare name in another module | e.g. second `GaryActError` | NOT excluded — must be dispatch-family | taxonomy test fails |
| voice-HIL rider closes/archives in deferred-inventory | (11B, elevenlabs) row still allowlisted | linkage test fails demanding row retirement | assertion message cites both artifacts |

</frozen-after-approval>

## Code Map

- `tests/specialists/test_narration_join_shared.py:33-36,61-79` -- W-R1: vacuous self-compare; publisher test asserts substrings not bytes
- `app/specialists/enrique/_act.py:25,122,255,343` -- W-R2: `DEFAULT_BUNDLE_PATH` def + 2 fallback sites; line 343 proves production always injects
- `app/specialists/quinn_r/graph.py:333-374` -- A-R2: `_act_with_trail` — zero callers repo-wide (grep-verified), exception policy looks load-bearing
- `tests/audit/test_no_silent_fixture_fallbacks.py:34` -- M-R1: ninth-seam regex pins exact spacing + literal `slide-1`
- `tests/contracts/test_specialist_error_taxonomy.py:34-51,78` -- M-R2: bare-name EXCLUSIONS; 18 module-qualified entries enumerated (5× OperatorInstructionsParseError across aria/kim/mira/tamara/vyx; ManifestParseError = tracy alias)
- `tests/contracts/test_manifest_grounding_contract.py:33-63` -- J-R1: (11B, elevenlabs) row; precedent for tests reading planning artifacts: `tests/parity/test_mapping_checklist_status.py`
- `_bmad-output/planning-artifacts/deferred-inventory.md` -- J-R1 reciprocal: voice-HIL entry gains the retirement instruction

## Tasks & Acceptance

**Execution:**
- [x] `tests/specialists/test_narration_join_shared.py` -- replace self-compare with explicit empty-script row expectation; publisher test compares full file text to canonical `yaml.safe_dump` of the shared-join output -- tests can now actually fail
- [x] `app/specialists/enrique/_act.py` -- delete `DEFAULT_BUNDLE_PATH`; both fallback sites raise `EnriqueActError` tag `elevenlabs.bundle.path-missing` when `bundle_path` absent -- no silent repo-root artifact writes
- [x] `tests/specialists/test_audio_segment_grounding.py` -- pin the bundle-path-missing raise (both voice + synthesis legs) -- PIN per batch discipline
- [x] `app/specialists/quinn_r/graph.py` -- delete `_act_with_trail` -- dead code with load-bearing-looking exception policy
- [x] `tests/audit/test_no_silent_fixture_fallbacks.py` -- generalize ninth-seam regex (whitespace-tolerant, any literal id) + add direct regex-shape assertions for evasion variants -- rename/whitespace no longer escapes
- [x] `tests/contracts/test_specialist_error_taxonomy.py` -- module-qualify EXCLUSIONS (18 entries) and match on `{module}.{name}` -- bare-name reuse no longer inherits exclusion
- [x] `tests/contracts/test_manifest_grounding_contract.py` -- add linkage test: while (11B, elevenlabs) is allowlisted, `voice-selection-hil-fold-defect` must be an ACTIVE deferred-inventory entry (above the archived section) -- row cannot outlive its rationale
- [x] `_bmad-output/planning-artifacts/deferred-inventory.md` -- append reciprocal retirement instruction to the voice-HIL entry -- bidirectional citation per trial-postmortem governance

**Acceptance Criteria:**
- Given a payload lacking `bundle_path`, when any enrique output builder runs, then a typed `EnriqueActError` (tag `elevenlabs.bundle.path-missing`) raises and nothing is written to `runs/`
- Given `[ { 'slide_id' :  'anything' } ]` in an app/ module source, when the fixture ratchet scans, then it fails
- Given a hypothetical tagged `GaryActError` defined outside `app.specialists.gary._act`, then the taxonomy test reports it (exclusion no longer matches by bare name)
- Given the current deferred-inventory state, when the grounding-contract suite runs, then the new linkage test passes; given the voice-HIL entry struck/archived, then it fails
- Given the full battery (focused + audit + contracts + marcus integration + lockstep + lint-imports), then all green with zero behavior change on the production walk

## Spec Change Log

## Verification

**Commands:**
- `.\.venv\Scripts\python.exe -m pytest tests/specialists/ tests/contracts/ tests/audit/ tests/integration/marcus/ -q` -- expected: all green
- `.\.venv\Scripts\python.exe scripts/utilities/check_pipeline_manifest_lockstep.py` -- expected: exit 0
- `.\.venv\Scripts\lint-imports.exe` -- expected: 13 kept, 0 broken
- `.\.venv\Scripts\ruff.exe check <touched files>` -- expected: clean

## Suggested Review Order

**Fail-loud bundle path (the one live-path change)**

- Presence guard replacing the repo-root default; typed recoverable tag
  [`_act.py:36`](../../app/specialists/enrique/_act.py#L36)

- Pin: all three builders refuse without bundle_path, zero TTS spend
  [`test_audio_segment_grounding.py:142`](../../tests/specialists/test_audio_segment_grounding.py#L142)

**Dead-code excision (quinn_r)**

- Five private functions deleted (`_act_with_trail` + its orphaned helper chain); `QRRParseError` and the exported pre/post-composition bodies remain
  [`graph.py:67`](../../app/specialists/quinn_r/graph.py#L67)

**Audit-surface hardening**

- Ninth-seam regex now whitespace-tolerant / any-literal-id, with evasion-variant pins
  [`test_no_silent_fixture_fallbacks.py:85`](../../tests/audit/test_no_silent_fixture_fallbacks.py#L85)

- EXCLUSIONS module-qualified (18 entries) so bare-name reuse can't inherit exclusion
  [`test_specialist_error_taxonomy.py:36`](../../tests/contracts/test_specialist_error_taxonomy.py#L36)

- Reverse-existence pin: stale exclusion rows must retire (review patch)
  [`test_specialist_error_taxonomy.py:99`](../../tests/contracts/test_specialist_error_taxonomy.py#L99)

- Linkage test: (11B, elevenlabs) allowlist row cannot outlive the voice-HIL rider; strikethrough-aware, fail-loud anchor (review MUST-FIX applied)
  [`test_manifest_grounding_contract.py:84`](../../tests/contracts/test_manifest_grounding_contract.py#L84)

**Test honesty (Winston R1)**

- Self-compare replaced with literal expected rows
  [`test_narration_join_shared.py:39`](../../tests/specialists/test_narration_join_shared.py#L39)

- Publisher manifest: byte-equality + retained literal content anchors (review patch)
  [`test_narration_join_shared.py:96`](../../tests/specialists/test_narration_join_shared.py#L96)

**Bookkeeping**

- Voice-HIL entry retirement tie + bundle-entry EXECUTED strike
  [`deferred-inventory.md:590`](../planning-artifacts/deferred-inventory.md#L590)
