# UDAC v1 — CF-A exercise (MT-7), deterministic over the Step-8 live run-dir substrate

Date: 2026-06-28 (UTC). Dev-agent run. **No git commit. No vision tests. No fixtures mutated.
No live API spend** (UDAC v1 is offline/deterministic; this exercise reuses the recorded
Step-8 CF-A live substrate).

## Substrate (real, live-produced)

The surviving Step-8 CF-A live run dir
`…/scratchpad/p5s8-runs/8a997d43-8f9c-4b2e-a8ae-1e7fb883f78b/g0-enrichment.json` — produced by a
**real `production_runner` two-walk** run with `model_id=marcus` (live gpt-5) + live scite (the same
run recorded in `p5-directed-voice-s8-cfa-e2e-20260628T0137Z.md`). The frozen card:
`corpus_fingerprint=c7d0b1279c1c…`, 20 typed components, 6 provisional LOs, 2 citation resolutions
(1 **live scite-resolved** JAMA DOI `10.1001/jama.2019.13978`), 7 pedagogy annotations.

The frozen `g0-enrichment.json` was copied into a fresh CF-A run dir; the RAI was built + resolved on
that real substrate deterministically (no runner re-run; no live API). Harness:
`…/scratchpad/udac_cfa_exercise.py`; log: `…/scratchpad/udac_cfa_log.txt`.

> Honesty note: a full live `production_runner` re-run is heavy + would incur gpt-5/scite spend; per
> the story's "exercise the RAI build+resolve+one-consumer-USE on a real run dir deterministically (no
> live API) and say so honestly" allowance, this exercises the EXACT gate-writer + dispatch-reader +
> consumer-USE code paths over a real live-frozen asset. The runner integration itself is covered by the
> production_runner integration suite (70 passed) + the both-walks parity tests.

## Results (all assertions PASSED)

| Leg | Evidence | Result |
|---|---|---|
| **RAI build at the gate** (`record_gate_ratification(gate_code="G0E")`) | g0-enrichment RATIFIED; `digest=5db4569474b63773…` **== disk-recomputed digest**; `derived_from=c7d0b1279c1c…` (TX-4 trust chain = live corpus fp); `produced_by_node=G0E`; `<run_dir>/run-asset-index.json` written | **PASS** |
| **Resolve at the dispatch guard** (`resolve_consumed_assets(specialist_id="workbook")`) | resolved g0-enrichment; `legacy_mode=none`; digest matches disk | **PASS** |
| **Consumer USE on the live substrate** (workbook projection) | `further_reading=['https://doi.org/10.1001/jama.2019.13978']` (the **live scite-resolved** citation) + 6 learning objectives projected | **PASS** |
| **USE anti-tautology on the live substrate** | mutate live citation `src-001-c010` access_url → sentinel **PRESENT** in projection AND pre-mutation URL **ABSENT** | **PASS** |
| **Fail-loud** (corrupt the on-disk asset AFTER ratification) | `resolve_consumed_assets` → `AssetResolutionError` tag=**`udac.asset-stale`** (routes through the runner's recoverable `_pause_at_error`) | **PASS** |
| **Both-walks parity** (re-cross G0E on a resume) | `ratified_at` **stable** across the re-cross (rehydrate-from-disk-then-reconcile-monotonic, M-3/M-5) | **PASS** |

`ALL CF-A UDAC v1 ASSERTIONS PASSED (deterministic; no live API)`.

The ACCESS spine (RAI built at the gate, asset located by id not path), the USE guarantee (the workbook
consumer's output follows the live asset's bytes), and the fail-loud + both-walks-parity guarantees are
all proven end-to-end on real live-produced CF-A substrate.
