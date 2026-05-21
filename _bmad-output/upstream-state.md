# Upstream State

- Migration verdict: `unqualified SHIP` (promoted 2026-04-27 from prior `SHIP for bounded-MVP scope` after Slab 6.1 formal close resolved M5 condition #3; see `_bmad-output/implementation-artifacts/m5-decision.md`)
- Original 6-agent operator acceptance date: `2026-04-26`
- 3-agent reframe ratification date: `2026-04-27` (Winston + Murat + Quinn-R unanimous GREEN-WITH-CONCERNS; all riders honored before promotion landed)
- Final ship claim language: see `_bmad-output/implementation-artifacts/m5-decision.md` "Migration unconditionally shipped" section
- Original conditional window expiry: `2026-05-03` (REPLACED by reframe â€” original window applied to SHIP-CONDITIONAL verdict; the reframed SHIP-for-bounded-MVP-scope verdict has no window because the 3 unresolved conditions are operator-presence-only and the substrate-gap condition was reframed to Slab 6 opener)
- Primary repo posture: frozen reference only
- Frozen reference anchor: `upstream/master @ 3ed7c56`
- Backport posture: FR60 remains closed
- Forward-port posture: FR61 may proceed within the bounded-MVP claim set
- Demotion rule (HISTORICAL; superseded by reframe): if the 2026-05-03 window had lapsed unresolved, `migration-master-status` would have demoted from `shipped` to `iterate-pending`. Reframe to bounded-MVP scope removes the demotion trigger.

## Pre-Trial Defensibility Evidence

- Batch 2 B-trace (2026-04-27): `_bmad-output/implementation-artifacts/m5-fr-traceability-matrix.md` records 17 M5-relevant FR rows: 15 `TRACED`, 2 `PARTIAL`, 0 `GAP`.
- Batch 2 B-nfr (2026-04-27): `_bmad-output/implementation-artifacts/m5-nfr-assessment.md` records 11 M5 NFR assessments: 11 `MET`, 0 `NOT MET`.
- Batch 2 B-tr (2026-04-27): `_bmad-output/implementation-artifacts/5a-3-test-quality-audit.md` records 9 cost-engineering test files reviewed, overall score 80/100, and no file below 70.

## Open Conditions

1. **M2 Wondercraft live artifact/operator addendum — RESOLVED 2026-04-27.** Operator executed the Wondercraft live-artifact ceremony; M2 verdict promoted to GREEN-LIGHT and M5 condition #1 closed (M2 ceremony commit `c2065e9`).
2. **M3 Texas live retrieval â€” RESOLVED 2026-04-27.** Operator executed M3 ceremony via Notion locator-shape provider (`scripts/operator/m3_texas_ceremony_notion.py`); 1 real page returned (`Student_Onboarding`, ID `e436f889-ef5d-4018-af5d-fd1ec5c8bad4`); evidence at `tests/fixtures/specialists/texas/live_retrieval/2026-04-27/437e2b249286c035611933270ffe9216ac7329b30318022b036587a27e019953.json`; addendum pasted to `slab-3-m3-acceptance-verdict.md`; M3 verdict promoted CONDITIONAL-GREEN â†’ GREEN-LIGHT. Scite retrieval-shape execution deferred as `5a-2-scite-mcp-oauth-integration` (third A16 instance discovered same day; SciteProvider hardwired to HTTP Basic but real MCP requires OAuth 2.1; working ceremony script exists at `scripts/operator/m3_texas_ceremony_scite.py` for future use; production-class SciteProvider migration is the deferred follow-on).
3. **5a.2 production clone-launch equivalence — RESOLVED 2026-04-27.** Slab 6.0 closed 2026-04-27 (commits `072724c` + `7812d3e`); Slab 6.1 closed 2026-04-27 (commits `d5cfad8` + `6ca5f43` + `0f91e95` + `61fede4` + `e6787e3`). Operator-witnessed live gate-resume smoke passed in 30.54s; persistent live audit trial `b38f5350-0c35-4cd5-821f-29687725bb70` exists with real production-graph-runner evidence, contributions `[texas, irene]`, and `production_clone_launch_evidence=True`. M5 condition #3 close criteria are fully met. Migration verdict promotes from SHIP-for-bounded-MVP to unqualified SHIP.
4. **Plausible-Token Substrate Contamination â€” RESOLVED 2026-04-27.** Operator ran `pytest tests/live/test_openai_cascade_tiers_smoke.py -m live -v` with `OPENAI_API_KEY` set; all 3 cascade-tier pings PASSED in 7.00s (frontier=`gpt-5` + mid-tier=`gpt-5-mini` + narrow-task=`gpt-5-nano`). Each model_id resolves correctly at OpenAI. Anti-pattern A15 (Plausible-Token Substrate Contamination) is now empirically validated â€” referent-validity confirmed end-to-end, not just structurally. **Bonus discovery:** the smoke test as authored used `max_completion_tokens=1` and produced 400 BadRequestError on first run because GPT-5 family reasoning consumes token budget before visible output. Patched in same session to `max_completion_tokens=200` with explanatory comment citing A16 (Composition-vs-Component Audit Gap) â€” the smoke test was authored without ever running against real GPT-5, so referent-validity wasn't exercised end-to-end. The A16 prevention pattern caught this defect at first integration attempt, not in production. (Earlier remediation history preserved: defect surfaced 2026-04-26 post-vote per Winston + Mary party-mode synthesis; remediated via 4-agent party-mode-ratified plan substituting real OpenAI catalog IDs across ~25 production-code surfaces + lint guard + catalog-membership test + 3 live-OpenAI cascade-tier smoke pings as structural prevention; anti-pattern entries A15 + A16 filed under "Post-Cycle Harvest" subheading at `docs/dev-guide/specialist-anti-patterns.md`.)

Resolved 2026-04-26:
- `slab-3-m5-dispatch-registry-swap` is closed. The live dispatch registry and frozen `v42` snapshot were both promoted from `_status: interim` to `_status: production` after import-path verification across every registered specialist.
