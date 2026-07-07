"""Re-check judge sha256 against the frozen manifest immediately before running a
judge. Exits non-zero if a judge was mutated after freeze (first-run-stands guard).
"""
import hashlib
import json
import sys
from pathlib import Path

EVID = Path(__file__).resolve().parent
manifest = json.loads((EVID / "judges-frozen.json").read_text(encoding="utf-8"))
ok = True
for name, frozen in manifest["judges"].items():
    now = hashlib.sha256((EVID / name).read_bytes()).hexdigest()
    match = now == frozen
    ok = ok and match
    print(f"{'MATCH' if match else 'MUTATED'} {name}: frozen={frozen[:16]}… now={now[:16]}…")
print("frozen_at:", manifest["frozen_at"])
sys.exit(0 if ok else 1)
