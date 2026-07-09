import json, os, sys
from pathlib import Path
REPO = Path(r"C:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS-hybrid")
sys.path.insert(0, str(REPO)); os.chdir(REPO)
facts = json.loads((Path(sys.argv[1])/"lane_a-facts.json").read_text(encoding="utf-8"))
from app.runtime.economics import RUNS_ROOT
run = json.loads((RUNS_ROOT/facts["trial_id"]/"run.json").read_text(encoding="utf-8"))
contribs = run["production_envelope"]["contributions"]
ir = [c for c in contribs if c.get("specialist_id")=="irene_pass1" and c.get("node_id")=="04A"][0]
lp = ir["output"]["lesson_plan"]
pus = lp.get("plan_units") or []
print("=== full first 2 plan_units (all keys) ===")
for u in pus[:2]:
    print(json.dumps(u, indent=2, default=str)[:2500])
    print("----")
print("=== lesson_plan top-level keys ===")
print(sorted(lp.keys()))
