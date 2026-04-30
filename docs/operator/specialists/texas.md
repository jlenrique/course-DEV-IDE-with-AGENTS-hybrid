# Texas — Pass-1 Source Retrieval

## OPERATOR

Texas is your **Pass-1 source retrieval specialist**. You hand him a directive describing what to look for; he returns a six-canonical-artifacts retrieval bundle that downstream specialists (Tracy, Quinn-R, Vera, Irene, Gary) consume.

You invoke Texas implicitly through the trial pipeline at G0/G1 — after directive composition, the runner dispatches Texas to populate the bundle. You do NOT invoke Texas directly in normal operation. You CAN talk to Texas as an agent for retrieval-strategy questions or to inspect what's in a closed bundle.

**When you'd talk to Texas directly:** asking "how would you retrieve X?", "what's in `[bundle]/02-source-authority-map.md`?", or "is the retrieval contract honored for this directive?".

## INPUTS

- **Directive payload** (`directive_path`): the operator-confirmed-or-edited directive emitted by `app.marcus.orchestrator.directive_composer` at G0.
- **Bundle directory** (`bundle_dir`): the destination for the six canonical artifacts.
- **Retrieval contract** (`skills/bmad-agent-texas/references/retrieval-contract.md`): the canonical contract for Pass-1 retrieval shape; defines the six-artifact output schema and word-count belt-and-suspenders floor.
- **Provider directory** (via `run_wrangler.py --list-providers` or `retrieval.list_providers()`): authoritative for "what Texas can fetch" (corpus dirs / Notion / Box / Playwright / etc.).

## OUTPUTS

Texas writes the **six canonical artifacts** under `bundle_dir/`:

1. `01-bundle-manifest.yaml` — bundle metadata + provider trace.
2. `02-source-authority-map.md` — operator-readable source authority table (this is what you, the operator, review at the post-Pass-1 gate).
3. `03-evidence-log.jsonl` — JSONL evidence log with provenance + fingerprints.
4. `04-source-coverage-report.md` — coverage analysis vs directive scope.
5. `05-rubric-g0-results.json` — G0 6-dim rubric scores (PASS/under-floor verdict).
6. `06-resolution-trail.jsonl` — model-resolution + dispatch trail.

Word-count belt-and-suspenders: if any artifact under-floors the rubric, Texas raises `RetrievalScopeError` (no fixture-stub fallback per FR89 hardening at 7b.1).

## REFERENCE

- Persona SKILL.md: `skills/bmad-agent-texas/SKILL.md`
- Sanctum: `_bmad/memory/bmad-agent-texas/` (6-file BMB)
- Retrieval contract: `skills/bmad-agent-texas/references/retrieval-contract.md`
- Story spec: [`migration-7b-1-texas-hardening.md`](../../../_bmad-output/implementation-artifacts/migration-7b-1-texas-hardening.md)
- Code: `app/specialists/texas/` (9-node scaffold; `_act.py` body delegates from `graph.py`)
- Class: A (option-a sanctum-aligned; first-three-GREEN of Slab 7b)
