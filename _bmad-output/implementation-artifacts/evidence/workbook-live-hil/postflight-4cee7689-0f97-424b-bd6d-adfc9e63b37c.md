# Story 38.3a / 38.1 governed live-acceptance postflight

- Trial ID: `4cee7689-0f97-424b-bd6d-adfc9e63b37c`
- Authorized action consumed: exactly one fresh `start`
- Terminal result: `paused-at-error` / `stopped-paused-at-error`
- Passing claim: **NO**
- Workbook emitted: **NO**
- Deep Dive reached: **NO**
- Ask-A reached: **NO**
- Retry, attach, recover, re-entry, or second start after stop: **NO**

## Stop boundary

The production runtime stopped at manifest node `04A`, specialist `irene_pass1`, with tag `irene-pass1.authority-invalid`:

> unit u03i1 anchor must match exactly one source slide file

The strict validator behaved correctly. LangSmith trace inspection showed that Irene's candidate for `u03i1` included the anchor `cannot rely on static training`. The authoritative Slide 3 sentence is `We can no longer rely on static training.` The candidate therefore supplied a near-paraphrase rather than a literal source span and matched zero source slide files. The other inspected anchors for that unit matched Slide 3 exactly.

This is a Marcus-SPOC product defect under the repository's hourglass rule: literal source authority is a deterministic constraint, but the current seam delegates the literal wording to unconstrained LLM generation. This record does not authorize weakening the validator, fuzzy matching, prompt-only accommodation, or a proofing-run-only workaround.

## Frozen attempt evidence

- Run-tree files: `29`
- `error-pause.json` SHA-256: `bb51b89226c38acf5d4bb0850d72bed21c152d78c6633c7af422c49ccd54f6b0`
- `run.json` SHA-256: `98002059775be3612c636d9283c6c6f111034de91edbb72c8011df5f51da23a4`
- HIL journal events: `8`
- Gate actions: `3`
- Recorded local cost: `$0.0000105` for two Texas `gpt-5-nano` calls
- Cost-report limitation: the failed Irene provider call is visible in the LangSmith trace but is not represented in the local cost report's per-agent breakdown.

## Frozen prior evidence recheck

| Trial | Files | `error-pause.json` SHA-256 | `run.json` SHA-256 |
|---|---:|---|---|
| `a28aa15a-fc80-46ae-b05a-09ac864829bb` | 67 | `4d9bc6f4c1c4ef5f662f6607326402dc741f1e845dd5ec1034f49283cc4fa6bc` | `3935b017d343bfd5c8bcdd1b7998d07ef82238ab74fa5031b6a1df60b90bc50f` |
| `c1c7135f-5b0d-4c59-bd5e-0bd58580b54b` | 28 | `1899c8fda1f7d3e233c410449b23536ae06f7a172679da3796f807906f2698ad` | `94eb23e055a5cafa6e720d04fb4045ca77bbb001997dc3c4cdbf56a818616d04` |

Both prior failed witnesses remained byte-identical at postflight.

## Identity-control finding

The preflight claimed `8839` runtime/config/prompt files with digest `83885c68a526515f79734c687ab5221edce3ee024fb343ffc6b88e25f7e59b07`. A post-run scan found `8841` files. The two additional files are normal production receipts written during this run under `state/config/runs/4cee7689-0f97-424b-bd6d-adfc9e63b37c/specialist-summaries/`, a location included by the preflight's broad `state/config/` identity root.

The preflight retained only an aggregate digest and count, not its per-file manifest. Consequently the original aggregate digest cannot be independently reconstructed or used to prove exact postflight equality; the attempt makes no exact-tree-equality claim. The course-source files themselves show no run-time write and the literal authoritative sentence remains present in Slide 3. A subsequent governed attempt must use an identity manifest that records every file line and excludes explicitly expected run-output namespaces from the immutable input tree.

## Disposition

The attempt is frozen as negative acceptance evidence. Story 38.3a and Story 38.1 remain open. The next action is a native BMAD party correction decision for a production-grade deterministic anchor-projection/selection seam, forensic persistence and cost-accounting behavior, and auditable per-file preflight identity evidence. No further live run is authorized by this postflight.
