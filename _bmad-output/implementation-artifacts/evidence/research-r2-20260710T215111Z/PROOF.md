# PROOF R2 — Consensus evidence-bolster live (PASS)

**Evidence:** `_bmad-output/implementation-artifacts/evidence/research-r2-20260710T215111Z/`  
**Auth:** Cursor mcp-remote OAuth token → Texas Bearer (no separate enterprise API key required for this witness)

## Result

- detective ON + `evidence_bolster=True`
- intent providers: `['scite', 'consensus']` `cross_validate=True`
- dual_dispatch=True total_rows=21 (scite=1, consensus=20)
- overall **PASS=True**

## Notes

- Identity keys did not overlap (Scite DOI vs Consensus paper-hash from markdown) → convergence `single_source_only` per provider. Dual **dispatch** still proven; DOI-merge triangulation is R3 follow-through when Consensus returns DOIs.
- Prior fail was wrong MCP host (`api.consensus.app` 404) + empty markdown parse.
