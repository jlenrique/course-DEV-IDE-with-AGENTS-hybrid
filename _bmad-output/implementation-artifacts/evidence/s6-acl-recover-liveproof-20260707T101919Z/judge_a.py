"""FROZEN JUDGE-a — S6 AC-L RECOVER lane (a): real cited resolvable-DOI row via D7.

Executed VERBATIM exactly once against the on-disk lane_a-facts.json. First-run-
stands; NO retry-to-green. Reads facts the driver emitted; renders 8 checks.

JUDGE-a (frozen), per the recover-witness spec:
 1. >=1 collateral.research_goals in the LOCKED plan (the Murat precondition —
    Irene-Pass-1 emitted real dispatchable intent).
 2. a REAL Scite dispatch fired at 04.55, provider == 'scite' (NOT
    consensus/gamma_docs), AND the dispatched intent's provenance traces to
    collateral.research_goals (the D7 path, NOT identified_gaps): the locked plan
    carried ZERO in-scope identified_gaps, >=1 research_goal, and every shaped
    intent from the SAME locked plan carries a research_goal_id provenance stamp
    on a scite-only provider hint.
 3. >=1 cited TexasRow in research_entries with source_id == a real DOI.
 4. the DOI RESOLVES — GET https://doi.org/{source_id} returns 200 to a real
    paper (content-inspected title snippet present).
 5. source_ref == 'retrieval:scite:{DOI}'.
 6. the G2 citation-fidelity gate PASSED (unsourced_citations == 0; report +
    manifest present — the gate RAN, not bypassed).
 7. narrate_research_result surfaced the cited result in the operator transcript.
 8. walk proceeded (paused-at-gate at a node past 04.55; not error/halt).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

EVID = Path(__file__).resolve().parent
FACTS = json.loads((EVID / "lane_a-facts.json").read_text(encoding="utf-8"))

DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")
DEFERRED = {"consensus", "gamma_docs"}
PAST_0455_GATES = {"G2B", "G2", "G2C", "G3", "G4", "G4A", "G5", "G1.5", "G2A"}

results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str) -> None:
    results.append((name, bool(ok), detail))


entries = FACTS.get("research_entries") or []
providers = [e.get("provider") for e in entries]
dois = [e.get("source_id") for e in entries]

# 1 — >=1 collateral.research_goals in the locked plan (precondition)
goals = FACTS.get("locked_research_goals") or []
c1 = FACTS.get("locked_research_goals_count", 0) >= 1 and len(goals) >= 1
check("1_precondition_research_goals_present", c1,
      f"research_goals_count={FACTS.get('locked_research_goals_count')} "
      f"goal_ids={[g.get('goal_id') for g in goals]}")

# 2 — real Scite dispatch, provider==scite, provenance to research_goals (D7)
shaped = FACTS.get("shaped_intent_provenance") or []
all_shaped_scite = bool(shaped) and all(
    all(h.get("provider") == "scite" for h in s.get("provider_hints", []))
    for s in shaped
)
all_shaped_have_goal_id = bool(shaped) and all(
    all(bool(h.get("research_goal_id")) for h in s.get("provider_hints", []))
    for s in shaped
)
c2 = (
    len(entries) >= 1
    and all(p == "scite" for p in providers)
    and not any(p in DEFERRED for p in providers)
    and FACTS.get("research_dispatch_live_fn") is True
    and FACTS.get("scite_creds_present") is True
    # provenance: the ONLY reachable dispatch path was research_goals (D7) —
    # zero in-scope identified_gaps, >=1 research_goal, shaped intents carry the
    # research_goal_id stamp on scite-only hints.
    and FACTS.get("in_scope_identified_gaps_count") == 0
    and FACTS.get("locked_research_goals_count", 0) >= 1
    and all_shaped_scite
    and all_shaped_have_goal_id
)
check("2_real_scite_dispatch_provenance_d7", c2,
      f"entries={len(entries)} providers={sorted(set(providers))} "
      f"dispatch_live_fn={FACTS.get('research_dispatch_live_fn')} "
      f"creds={FACTS.get('scite_creds_present')} "
      f"in_scope_identified_gaps={FACTS.get('in_scope_identified_gaps_count')} "
      f"research_goals={FACTS.get('locked_research_goals_count')} "
      f"shaped_all_scite={all_shaped_scite} shaped_all_have_goal_id={all_shaped_have_goal_id}")

# 3 — >=1 entry with source_id == a real DOI
real_dois = [d for d in dois if isinstance(d, str) and DOI_RE.match(d)]
check("3_cited_entry_real_doi", len(real_dois) >= 1, f"real_dois={real_dois}")

# 4 — DOI resolves via doi.org (200) + content-inspected title
res = FACTS.get("doi_resolution") or {}
c4 = (
    res.get("status_code") == 200
    and bool(res.get("final_url"))
    and bool(res.get("resolved_title_snippet"))
)
check("4_doi_resolves_content_inspected", c4,
      f"status={res.get('status_code')} final_url={res.get('final_url')!r} "
      f"title_snippet={str(res.get('resolved_title_snippet'))[:140]!r}")

# 5 — source_ref == retrieval:scite:{DOI}
primary_doi = FACTS.get("primary_doi")
primary_ref = FACTS.get("primary_source_ref")
c5 = (
    isinstance(primary_ref, str)
    and isinstance(primary_doi, str)
    and primary_ref == f"retrieval:scite:{primary_doi}"
)
check("5_source_ref_shape", c5,
      f"primary_source_ref={primary_ref!r} expected=retrieval:scite:{primary_doi}")

# 6 — G2 citation-fidelity gate PASSED (ran, not bypassed)
l2 = FACTS.get("l2_citation_report") or {}
c6 = (
    FACTS.get("g2_unsourced_citations") == 0
    and isinstance(l2, dict)
    and "unsourced_citations" in l2
    and l2.get("unsourced_citations") == 0
    and FACTS.get("citation_manifest") is not None
)
check("6_g2_gate_passed_not_bypassed", c6,
      f"g2_unsourced={FACTS.get('g2_unsourced_citations')} "
      f"l2_report_unsourced={l2.get('unsourced_citations')} "
      f"manifest_len={len(FACTS.get('citation_manifest') or [])}")

# 7 — narrate_research_result surfaced the cited result
narr = FACTS.get("narration_line") or ""
c7 = (
    isinstance(narr, str)
    and "cited source" in narr.lower()
    and str(len(entries)) in narr
)
check("7_narration_surfaced", c7, f"narration_line={narr!r}")

# 8 — walk proceeded (paused-at-gate past 04.55; not error/halt)
c8 = (
    FACTS.get("final_status") == "paused-at-gate"
    and FACTS.get("final_paused_gate") in PAST_0455_GATES
    and FACTS.get("research_contribution_node_id") == "04.55"
)
check("8_walk_proceeded", c8,
      f"final_status={FACTS.get('final_status')} "
      f"final_gate={FACTS.get('final_paused_gate')} "
      f"contrib_node={FACTS.get('research_contribution_node_id')}")

all_ok = all(ok for _, ok, _ in results)
out = {
    "judge": "a",
    "verdict": "PASS" if all_ok else "FAIL",
    "n_pass": sum(1 for _, ok, _ in results if ok),
    "n_total": len(results),
    "checks": [{"name": n, "ok": ok, "detail": d} for n, ok, d in results],
    "primary_doi": primary_doi,
    "primary_title": FACTS.get("primary_title"),
}
(EVID / "judge_a-facts.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
for n, ok, d in results:
    print(f"[{'PASS' if ok else 'FAIL'}] {n}: {d}")
print(f"=== JUDGE-a {out['verdict']} ({out['n_pass']}/{out['n_total']}) ===")
sys.exit(0 if all_ok else 1)
