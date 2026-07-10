import json
from pathlib import Path

run = Path("state/config/runs/22b27500-6e67-4dd7-8308-fd89defe3d99")
r = json.loads((run / "run.json").read_text(encoding="utf-8"))
pe = r.get("production_envelope") or {}
contribs = pe.get("contributions") or []
print("status", r.get("status"), "err", r.get("paused_error_tag"))
print("contrib count", len(contribs))
for c in contribs:
    print(f"  node={c.get('node_id')} specialist={c.get('specialist_id')}")
gary = list((run / "exports" / "gary").glob("*")) if (run / "exports" / "gary").exists() else []
print("gary exports", [p.name for p in gary])
print("motion", [p.name for p in (run / "motion").glob("*")] if (run / "motion").exists() else [])
# error message fields
for k in sorted(r):
    if "error" in k.lower() or "pause" in k.lower():
        v = r[k]
        if isinstance(v, str) and len(v) > 200:
            v = v[:200] + "..."
        print(f"{k}={v!r}")
