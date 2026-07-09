"""FROZEN JUDGE-a — S6 lane (a): real cited resolvable-DOI row (the M-wit).

Executed VERBATIM exactly once against the on-disk lane_a-facts.json. First-run-
stands; NO retry-to-green. Reads facts the driver emitted; renders 7 checks.

JUDGE-a (frozen):
 1. a REAL Scite dispatch fired at 04.55; selected provider == 'scite'
    (NOT consensus/gamma_docs — D2 live): >=1 cited entry, ALL provider=='scite',
    dispatch-live fn True, scite creds present, no entry from a deferred provider.
 2. >=1 cited TexasRow minted into research_entries with source_id == a real DOI.
 3. the DOI RESOLVES — GET https://doi.org/{source_id} returns 200/redirect to a
    real paper (content-inspected title).
 4. source_ref == 'retrieval:scite:{DOI}'.
 5. the G2 citation-fidelity gate PASSED (unsourced_citations == 0; report present
    — the gate RAN, not bypassed).
 6. narrate_research_result surfaced the cited result in the operator transcript.
 7. walk proceeded (paused-at-gate at a node past 04.55; not error/halt).
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

# 1 — real Scite dispatch, provider == scite (not consensus/gamma_docs)
c1 = (
    len(entries) >= 1
    and all(p == "scite" for p in providers)
    and not any(p in DEFERRED for p in providers)
    and FACTS.get("research_dispatch_live_fn") is True
    and FACTS.get("scite_creds_present") is True
)
check("1_real_scite_dispatch_provider_scite", c1,
      f"entries={len(entries)} providers={sorted(set(providers))} "
      f"dispatch_live_fn={FACTS.get('research_dispatch_live_fn')} "
      f"creds={FACTS.get('scite_creds_present')} "
      f"ready_providers={FACTS.get('ready_providers')}")

# 2 — >=1 entry with source_id == a real DOI
real_dois = [d for d in dois if isinstance(d, str) and DOI_RE.match(d)]
check("2_cited_entry_real_doi", len(real_dois) >= 1,
      f"real_dois={real_dois}")

# 3 — DOI resolves via doi.org (200/redirect) + content-inspected title
res = FACTS.get("doi_resolution") or {}
c3 = (
    res.get("status_code") == 200
    and bool(res.get("final_url"))
    and bool(res.get("resolved_title_snippet"))
)
check("3_doi_resolves_content_inspected", c3,
      f"status={res.get('status_code')} final_url={res.get('final_url')!r} "
      f"title_snippet={str(res.get('resolved_title_snippet'))[:120]!r}")

# 4 — source_ref == retrieval:scite:{DOI}
primary_doi = FACTS.get("primary_doi")
primary_ref = FACTS.get("primary_source_ref")
c4 = (
    isinstance(primary_ref, str)
    and isinstance(primary_doi, str)
    and primary_ref == f"retrieval:scite:{primary_doi}"
)
check("4_source_ref_shape", c4,
      f"primary_source_ref={primary_ref!r} expected=retrieval:scite:{primary_doi}")

# 5 — G2 citation-fidelity gate PASSED (ran, not bypassed)
l2 = FACTS.get("l2_citation_report") or {}
c5 = (
    FACTS.get("g2_unsourced_citations") == 0
    and isinstance(l2, dict)
    and "unsourced_citations" in l2
    and l2.get("unsourced_citations") == 0
    and FACTS.get("citation_manifest") is not None
)
check("5_g2_gate_passed_not_bypassed", c5,
      f"g2_unsourced={FACTS.get('g2_unsourced_citations')} "
      f"l2_report_unsourced={l2.get('unsourced_citations')} "
      f"manifest_len={len(FACTS.get('citation_manifest') or [])}")

# 6 — narrate_research_result surfaced the cited result in the transcript
narr = FACTS.get("narration_line") or ""
c6 = (
    isinstance(narr, str)
    and "cited source" in narr.lower()
    and str(len(entries)) in narr
)
check("6_narration_surfaced", c6, f"narration_line={narr!r}")

# 7 — walk proceeded (paused-at-gate past 04.55; not error/halt)
c7 = (
    FACTS.get("final_status") == "paused-at-gate"
    and FACTS.get("final_paused_gate") in PAST_0455_GATES
    and FACTS.get("research_contribution_node_id") == "04.55"
)
check("7_walk_proceeded", c7,
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
