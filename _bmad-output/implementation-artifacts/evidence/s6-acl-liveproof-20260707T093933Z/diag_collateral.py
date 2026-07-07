import json, os, sys
from pathlib import Path
REPO = Path(r"C:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS-hybrid")
sys.path.insert(0, str(REPO)); os.chdir(REPO)
facts = json.loads((Path(sys.argv[1])/"lane_a-facts.json").read_text(encoding="utf-8"))
from app.runtime.economics import RUNS_ROOT
run = json.loads((RUNS_ROOT/facts["trial_id"]/"run.json").read_text(encoding="utf-8"))
contribs = run["production_envelope"]["contributions"]
for nid in ("04A","05","05B"):
    ir = [c for c in contribs if c.get("specialist_id")=="irene_pass1" and c.get("node_id")==nid]
    if not ir: continue
    lp = ir[0]["output"]["lesson_plan"]
    coll = lp.get("collateral")
    print(f"=== node {nid} collateral ===")
    print(json.dumps(coll, indent=2, default=str)[:1800])
    print()
