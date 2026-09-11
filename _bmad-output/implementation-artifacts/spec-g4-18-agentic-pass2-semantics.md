---
title: 'G4-18 and Pass 2 spoken-bridge quality become Vera-agentic'
type: 'feature'
created: '2026-09-11'
status: 'in-review'
review_loop_iteration: 0
context:
  - '{project-root}/state/config/fidelity-contracts/g4-narration-script.yaml'
  - '{project-root}/skills/bmad-agent-fidelity-assessor/references/gate-evaluation-protocol.md'
---

<frozen-after-approval reason="operator-owned intent 2026-09-11 — GO tonight; proof is greening LP-PHS620-W03-BOXV02">

## Intent

**Problem:** The Pass 2 handoff validator treats G4-18 (“no new concepts in interstitials”) and `cluster_boundary` spoken-bridge quality as bag-of-words / exact-substring exams. That fails honest faculty-seminar VO (`here`, `must`, `does`; missing `in this section`) and is the wrong mechanism for semantic judgment.

**Approach:** Recast those two judgments as Vera-agentic, same split as G4-11 (structure) vs G4-15 (meaning). Keep `validate-irene-pass2-handoff.py` a replayable structural oracle. Prove the swap by greening the current PHS 620 W03 Pass 2 packet.

## Boundaries & Constraints

**Always:**
- Handoff validator stays CI-deterministic: no live LLM inside `validate-irene-pass2-handoff.py`.
- G4-18 and cluster-boundary *quality* fail closed only on Vera’s structured finding, not on token/phrase lists.
- Thin structure stays fail-closed: closed `bridge_type` list, resolve/develop interstitials use `none` unless a tension pivot, word-count bands, join/IDs, duration_rationale field shape.
- Conversation-space and engine use the same Vera entrypoint (`make_chat_model` / `vera.act`).
- `cluster_boundary` is a two-part seam, not `bridge_type: both`.

**Ask First:** Changing G4-16/G4-17/G4-19 off deterministic; inventing a second judge specialist beside Vera.

**Never:** Expanding stopword lists as the destination. Cursor-authored VO. Shaping production code only to make the concierge packet pass — this recast is a product oracle fix.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Token-heuristic interstitial | Interstitial uses `here`/`must` not in head VO | Handoff validator does not fail-closed on G4-18 | Advisory detail only |
| Exact-phrase cluster_boundary | Head tagged `cluster_boundary` without `in this section` | Validator does not fail-closed on spoken-bridge substrings | Vera judges seam quality |
| Real new teaching concept | Interstitial teaches a domain idea absent from head + Pass 1 scope | Vera G4-18 fails high-confidence | Structured finding, not a token dump |
| Structural closed-list | Resolve interstitial `bridge_type` is not `none` | Handoff validator still fail-closed | Unchanged |

</frozen-after-approval>

## Code Map

- `state/config/fidelity-contracts/g4-narration-script.yaml` -- G4-18 evaluation_type + check text
- `skills/bmad-agent-fidelity-assessor/references/gate-evaluation-protocol.md` -- move G4-18 to agentic; spoken-bridge quality under G4-12
- `skills/bmad-agent-marcus/scripts/validate-irene-pass2-handoff.py` -- demote token/phrase exams from strict errors
- `app/specialists/vera/pass2_semantic_judge.py` -- frozen rubric + live Vera call
- `app/specialists/vera/_act.py` -- overlay G4-18 when `pass2_semantic_judge` is set
- `skills/bmad-agent-marcus/scripts/judge-irene-pass2-semantics.py` -- official bundle entrypoint
- `skills/bmad-agent-content-creator/references/spoken-bridging-language.md` -- seam rule + phrase lists as authoring help, not fail-closed oracle

## Tasks & Acceptance

**Execution:**
- [x] Recast G4-18 to agentic in the contract and protocol
- [x] Demote G4-18 token dump and spoken-bridge substring promotion from strict handoff errors
- [x] Stop treating `cluster_boundary` as `both` in the deterministic cue helper
- [x] Add Vera `pass2_semantic_judge` (flag-gated so existing G4 stub tests stay offline)
- [x] Official Marcus script to judge a prepared envelope
- [x] Green LP-PHS620-W03-BOXV02: handoff validator pass + Vera semantic receipt

**Acceptance Criteria:**
- Given a clustered interstitial whose only “new concepts” are function words, when the handoff validator runs strict, then it does not fail on G4-18.
- Given `pass2_semantic_judge: true` and Pass 2 surfaces, when Vera `act` runs G4, then G4-18 is a real model judgment, not an auto-pass stub.
- Given the current PHS 620 W03 packet, when the official script + validator run, then the handoff is pass and a Vera receipt exists on disk.

## Verification

**Commands:**
- `.\.venv\Scripts\python.exe -m pytest skills/bmad-agent-marcus/scripts/tests/test_validate_irene_pass2_handoff.py tests/specialists/vera/test_vera_g4_19_criterion_rubric.py skills/bmad-agent-marcus/scripts/tests/test-narration-config-schemas.py -q --tb=short` -- expected: pass
- Official judge script against `course-content/staging/tracked/source-bundles/phs-620-w03-box-v02-20260910/pass2-envelope.json` -- expected: receipt on disk; handoff validator `status=pass`
