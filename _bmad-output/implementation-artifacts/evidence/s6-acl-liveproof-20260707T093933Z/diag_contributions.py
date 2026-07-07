import json, os, sys
from pathlib import Path
REPO = Path(r"C:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS-hybrid")
sys.path.insert(0, str(REPO)); os.chdir(REPO)
os.environ["PYTHONIOENCODING"]="utf-8"
facts = json.loads((Path(sys.argv[1])/"lane_a-facts.json").read_text(encoding="utf-8"))
trial = facts["trial_id"]
from app.runtime.economics import RUNS_ROOT
run_dir = RUNS_ROOT/trial
run = json.loads((run_dir/"run.json").read_text(encoding="utf-8"))
pe = run.get("production_envelope", {})
contribs = pe.get("contributions", [])
print("=== contributions (specialist_id @ node_id) ===")
for c in contribs:
    print(f"  {c.get('specialist_id')} @ {c.get('node_id')}  output_keys={sorted((c.get('output') or {}).keys())}")
# research_wiring contribution
rw = [c for c in contribs if c.get("specialist_id")=="research_wiring"]
print("\n=== research_wiring output ===")
for c in rw:
    print(json.dumps(c.get("output"), indent=2, default=str)[:2000])
# irene lesson plan
ir = [c for c in contribs if c.get("specialist_id")=="irene_pass1"]
print("\n=== irene_pass1 lesson_plan plan_units (scope + gaps) ===")
for c in ir:
    lp = (c.get("output") or {}).get("lesson_plan")
    if isinstance(lp, dict):
        pus = lp.get("plan_units") or []
        print(f"  node {c.get('node_id')}: {len(pus)} plan_units")
        for u in pus:
            sd = u.get("scope_decision")
            scope = sd.get("scope") if isinstance(sd, dict) else sd
            gaps = u.get("gaps") or []
            print(f"    unit={u.get('unit_id')} scope={scope} n_gaps={len(gaps)}")
            for gp in gaps:
                print(f"        gap: posture={gp.get('suggested_posture')} desc={str(gp.get('description'))[:80]!r}")
