"""S4 AC-L LEG-1 driver, phase 1: rewind-recover PREPARE + directive edit.

Same rewind-recover mechanics as leg-2 (copy leg-3's happy-path bundle, drop
gary@07 + downstream, keep CD, fabricate an error-pause repositioned to gary@07),
BUT instead of mutating the SSOT this leg edits the RECOVERED bundle's
directive.yaml so the NAMED variant A in gamma_settings has its `styleguide` key
REMOVED (variant still present, just styleguide-less — NOT empty gamma_settings).

On recover, gary reads gamma_settings from directive.yaml, hits the else branch of
the per-variant styleguide seed loop (a named variant with no bound styleguide),
and post-S4 Flip A raises gamma.styleguide.unbound PRE-SPEND. Flip A fires in
_normalized_gamma_settings BEFORE the parity receipt, so the directive-digest
change is irrelevant (no hard directive-integrity gate on recover).
"""
from __future__ import annotations

import json
import re
import shutil
import sys
import os
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import yaml

REPO = Path(r"C:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS-hybrid")
EVIDENCE = Path(__file__).resolve().parent
RUNS_ROOT = REPO / "state" / "config" / "runs"
GUIDE = "hil-2026-apc-crossroads-classic"
TAG = "s4.acl.leg1.rewind-reposition-to-gary"
OFFENDING_VARIANT = "A"

sys.path.insert(0, str(REPO))
os.chdir(REPO)
os.environ["PYTHONIOENCODING"] = "utf-8"

LOG = open(EVIDENCE / "driver-log-leg1.txt", "a", encoding="utf-8")


def log(msg: str) -> None:
    line = f"[{datetime.now(tz=UTC).isoformat()}] {msg}"
    print(line, flush=True)
    LOG.write(line + "\n")
    LOG.flush()


leg3 = json.loads((EVIDENCE / "leg3-state.json").read_text(encoding="utf-8"))
TRIAL1 = leg3["trial_id"]
TRIAL2 = str(uuid4())
src_dir = RUNS_ROOT / TRIAL1
new_dir = RUNS_ROOT / TRIAL2
if new_dir.exists():
    raise SystemExit(f"refusing to overwrite {new_dir}")

result: dict = {"leg": 1, "phase": "prepare", "trial1": TRIAL1, "trial2": TRIAL2,
                "offending_variant": OFFENDING_VARIANT}

from app.marcus.orchestrator.production_runner import compose_manifest, load_manifest  # noqa: E402

try:
    from app.models.runtime.component_selection import ComponentSelection  # type: ignore
except Exception:  # noqa: BLE001
    from app.marcus.orchestrator.production_runner import ComponentSelection  # type: ignore

manifest = compose_manifest(
    load_manifest(REPO / "state/config/pipeline-manifest.yaml"),
    ComponentSelection.production_default(),
)
node_index = {n.id: i for i, n in enumerate(manifest.nodes)}
idx07 = node_index["07"]
assert manifest.nodes[idx07].specialist_id == "gary", "node 07 is not gary"
log(f"composed manifest: node 07 (gary) at index {idx07}")

# ---- 1. copy ----------------------------------------------------------------
log(f"copy {src_dir} -> {new_dir}")
shutil.copytree(src_dir, new_dir)


def _drop_downstream(contribs: list) -> tuple[list, list]:
    kept, dropped = [], []
    for c in contribs:
        nid = c.get("node_id")
        if nid in node_index and node_index[nid] >= idx07:
            dropped.append(f"{c.get('specialist_id')}@{nid}")
        else:
            kept.append(c)
    return kept, dropped


# ---- 2. run.json surgical rewrite -------------------------------------------
run_path = new_dir / "run.json"
run = json.loads(run_path.read_text(encoding="utf-8"))
run["trial_id"] = TRIAL2
if run.get("langsmith_trace_id") == TRIAL1:
    run["langsmith_trace_id"] = TRIAL2
if isinstance(run.get("cost_report_path"), str):
    run["cost_report_path"] = run["cost_report_path"].replace(TRIAL1, TRIAL2)
if isinstance(run.get("artifact_paths"), list):
    run["artifact_paths"] = [
        p.replace(TRIAL1, TRIAL2) if isinstance(p, str) else p for p in run["artifact_paths"]
    ]
run["production_envelope"]["trial_id"] = TRIAL2
kept, dropped = _drop_downstream(run["production_envelope"]["contributions"])
assert any(d.startswith("gary@07") for d in dropped), f"expected gary@07 to drop, dropped={dropped}"
run["production_envelope"]["contributions"] = kept
run["status"] = "paused-at-error"
run["paused_gate"] = None
run["paused_error_tag"] = TAG
run_path.write_text(json.dumps(run, indent=2, default=str), encoding="utf-8")
result["dropped_contributions"] = dropped
result["remaining_contributions"] = [
    f"{c.get('specialist_id')}@{c.get('node_id')}" for c in kept
]
log(f"run.json rewritten: dropped={dropped}; remaining={result['remaining_contributions']}")

# ---- 3. fabricate error-pause.json from the copied checkpoint ----------------
checkpoint = json.loads((new_dir / "checkpoint.json").read_text(encoding="utf-8"))
assert checkpoint.get("gate_id") == "G2B", f"unexpected checkpoint gate {checkpoint.get('gate_id')}"
run_state = checkpoint["run_state"]
if run_state.get("run_id") == TRIAL1:
    run_state["run_id"] = TRIAL2
rspe = run_state.get("production_envelope")
if isinstance(rspe, dict):
    rspe["trial_id"] = TRIAL2
    if isinstance(rspe.get("contributions"), list):
        rspe["contributions"], _d2 = _drop_downstream(rspe["contributions"])
runner = dict(checkpoint.get("runner") or {})
for pk in ("directive_path", "bundle_dir"):
    if isinstance(runner.get(pk), str):
        runner[pk] = runner[pk].replace(TRIAL1, TRIAL2)
error_pause = {
    "trial_id": TRIAL2,
    "node_index": idx07,
    "node_id": "07",
    "specialist_id": "gary",
    "tag": TAG,
    "message": (
        "recover point repositioned to gary@07 for the S4 AC-L leg-1 "
        "named-variant-styleguide-less witness (rewind-recover of the leg-3 "
        "happy-path walk; CD's contribution retained, gary + downstream dropped)"
    ),
    "last_gate_crossed": "G1",
    "run_state": run_state,
    "runner": runner,
}
(new_dir / "error-pause.json").write_text(
    json.dumps(error_pause, indent=2, default=str), encoding="utf-8"
)
log(f"error-pause.json fabricated: node_index={idx07} node_id=07 specialist=gary")

# ---- trial-start.json: retarget id strings (digests are hex, untouched) ------
ts_path = new_dir / "trial-start.json"
ts = json.loads(ts_path.read_text(encoding="utf-8"))
ts = {k: (v.replace(TRIAL1, TRIAL2) if isinstance(v, str) else v) for k, v in ts.items()}
ts_path.write_text(json.dumps(ts, indent=2, sort_keys=True) + "\n", encoding="utf-8")

# ---- 4. DIRECTIVE EDIT: strip `styleguide` from named variant A --------------
# Targeted text removal within the gamma_settings block ONLY (leaves the
# styleguide_picker_provenance block and everything else byte-untouched).
dpath = new_dir / "directive.yaml"
dtext_before = dpath.read_text(encoding="utf-8")
loaded_before = yaml.safe_load(dtext_before)
gs_before = loaded_before.get("gamma_settings")
result["gamma_settings_before"] = gs_before
# locate the gamma_settings block extent
gm = re.search(r"^gamma_settings:\s*$", dtext_before, flags=re.MULTILINE)
assert gm is not None, "gamma_settings block not found in directive.yaml"
block_start = gm.end()
nextkey = re.search(r"^[A-Za-z0-9_]+:", dtext_before[block_start:], flags=re.MULTILINE)
block_end = block_start + nextkey.start() if nextkey else len(dtext_before)
block = dtext_before[block_start:block_end]
# remove the styleguide line naming the guide (2-space indented list-item key)
new_block, n = re.subn(
    r"\n[ ]+styleguide:[ ]*" + re.escape(GUIDE) + r"[ ]*(?=\n|$)",
    "",
    block,
)
assert n == 1, f"expected exactly ONE styleguide line to remove, removed {n}"
dtext_after = dtext_before[:block_start] + new_block + dtext_before[block_end:]
dpath.write_text(dtext_after, encoding="utf-8")

loaded_after = yaml.safe_load(dtext_after)
gs_after = loaded_after.get("gamma_settings")
result["gamma_settings_after"] = gs_after
# verify: variant A present, no styleguide key; provenance untouched
entry = next((e for e in (gs_after or []) if e.get("variant_id") == OFFENDING_VARIANT), None)
edit_ok = (
    isinstance(entry, dict)
    and "styleguide" not in entry
    and loaded_after.get("styleguide_picker_provenance")
    == loaded_before.get("styleguide_picker_provenance")
)
result["directive_edit_ok"] = edit_ok
result["variant_A_after"] = entry
log(f"directive edited: gamma_settings {gs_before} -> {gs_after}; edit_ok={edit_ok}")

(EVIDENCE / "leg1-prepare-result.json").write_text(
    json.dumps(result, indent=2, default=str) + "\n", encoding="utf-8"
)
(EVIDENCE / "leg1-state.json").write_text(
    json.dumps({"trial2": TRIAL2, "trial1": TRIAL1, "tag": TAG,
                "offending_variant": OFFENDING_VARIANT}, indent=2) + "\n",
    encoding="utf-8",
)
log(f"=== LEG1 PREPARE {'OK' if edit_ok else 'NOT-OK'} — trial2={TRIAL2} ===")
sys.exit(0 if edit_ok else 1)
