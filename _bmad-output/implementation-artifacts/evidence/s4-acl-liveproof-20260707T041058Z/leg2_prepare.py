"""S4 AC-L LEG-2 driver, phase 1: rewind-recover PREPARE + SSOT mutation.

Adapted VERBATIM from the S3 leg-2 prepare (same rewind-recover mechanics):
  1. COPY leg-3's happy-path run dir -> a fresh trial id (leg-3 dir untouched).
  2. run.json: surgical id rewrite; DROP gary@07 and every contribution at/after
     manifest index of node 07 (first-wins re-dispatches §07 onward). CD@4.75
     STAYS (authored against ORIGINAL SSOT bytes) -> pins CD-before ordering.
     Flip status paused-at-gate -> paused-at-error.
  3. FABRICATE error-pause.json from the copied G2B checkpoint, repositioned to
     node 07 / gary, last_gate_crossed=G1.
  4. Validate the plumbing offline.
  5. ONLY THEN mutate state/config/gamma-style-guides.yaml: ONE resolver-emitted
     field (amount: minimal -> concise) so ssot_digest AND base-resolution digest
     BOTH diverge; directive NEVER touched -> genuine same-bytes divergence.

S3 WARN-proceeded to G2B on this setup. S4 must HALT (phase 2).
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
import os
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

REPO = Path(r"C:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS-hybrid")
EVIDENCE = Path(__file__).resolve().parent
RUNS_ROOT = REPO / "state" / "config" / "runs"
SSOT = REPO / "state" / "config" / "gamma-style-guides.yaml"
GUIDE = "hil-2026-apc-crossroads-classic"
TAG = "s4.acl.leg2.rewind-reposition-to-gary"

sys.path.insert(0, str(REPO))
os.chdir(REPO)
os.environ["PYTHONIOENCODING"] = "utf-8"

LOG = open(EVIDENCE / "driver-log-leg2.txt", "a", encoding="utf-8")


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

result: dict = {"leg": 2, "phase": "prepare", "trial1": TRIAL1, "trial2": TRIAL2}

# ---- manifest index of node 07 (gary) --------------------------------------
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
        "recover point repositioned to gary@07 for the S4 AC-L leg-2 "
        "forced-divergence witness (rewind-recover of the leg-3 happy-path "
        "walk; CD's contribution retained, gary + downstream dropped)"
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
digest_before = ts.get("directive_digest")
ts = {
    k: (v.replace(TRIAL1, TRIAL2) if isinstance(v, str) else v) for k, v in ts.items()
}
assert ts.get("directive_digest") == digest_before
ts_path.write_text(json.dumps(ts, indent=2, sort_keys=True) + "\n", encoding="utf-8")
result["trial_start_directive_digest"] = digest_before

# ---- 4. offline validation ----------------------------------------------------
from app.models.runtime.production_trial_envelope import ProductionTrialEnvelope  # noqa: E402

env = ProductionTrialEnvelope.model_validate_json(
    (new_dir / "run.json").read_text(encoding="utf-8"),
    context={"anomaly_sink": new_dir / "anomalies.jsonl"},
)
checks = {
    "envelope_loads": True,
    "status_paused_at_error": env.status == "paused-at-error",
    "gary_dropped": env.production_envelope.latest_for_specialist("gary") is None,
    "cd_present_resolved": (
        (env.production_envelope.latest_for_specialist("cd") or None) is not None
        and (env.production_envelope.latest_for_specialist("cd").output or {})
        .get("styleguide_resolution", {})
        .get("status")
        == "resolved"
    ),
    "directive_bytes_match_trial_start_digest": hashlib.sha256(
        (new_dir / "directive.yaml").read_bytes()
    ).hexdigest()
    == digest_before,
}
result["offline_checks"] = checks
log(f"offline checks: {checks}")
if not all(checks.values()):
    (EVIDENCE / "leg2-prepare-result.json").write_text(
        json.dumps(result, indent=2, default=str) + "\n", encoding="utf-8"
    )
    raise SystemExit("offline validation FAILED — aborting before mutation")

# ---- 5. SSOT mutation (AFTER validation; CD-before/gary-after ordering pinned) --
from app.styleguide.parity import canonical_resolution_digest  # noqa: E402
from app.styleguide.resolver import load_style_guides, resolve_styleguide  # noqa: E402

ssot_before = SSOT.read_bytes()
resolved_before = {
    name: resolve_styleguide(name, guides=load_style_guides(SSOT)["style_guides"])
    for name in load_style_guides(SSOT)["style_guides"]
}
text = ssot_before.decode("utf-8")
anchor = text.index(f"{GUIDE}:")
needle = "amount: minimal"
pos = text.index(needle, anchor)
import re  # noqa: E402

next_guide = re.search(r"\n  [a-z0-9][a-z0-9-]*:\s*(\n|$)", text[anchor + len(GUIDE) + 1 :])
next_guide_pos = (anchor + len(GUIDE) + 1 + next_guide.start()) if next_guide else len(text)
assert anchor < pos < next_guide_pos, "mutation target escaped the picked guide's block"
mutated = text[:pos] + "amount: concise" + text[pos + len(needle) :]
SSOT.write_text(mutated, encoding="utf-8")
ssot_after = SSOT.read_bytes()

resolved_after = {
    name: resolve_styleguide(name, guides=load_style_guides(SSOT)["style_guides"])
    for name in load_style_guides(SSOT)["style_guides"]
}
changed = [n for n in resolved_before if resolved_before[n] != resolved_after.get(n)]
mutation = {
    "field": "prompt_configuration.text_content.amount",
    "from": "minimal",
    "to": "concise",
    "ssot_sha256_before": hashlib.sha256(ssot_before).hexdigest(),
    "ssot_sha256_after": hashlib.sha256(ssot_after).hexdigest(),
    "picked_guide_resolution_digest_before": canonical_resolution_digest(
        {"A": resolved_before[GUIDE]}
    ),
    "picked_guide_resolution_digest_after": canonical_resolution_digest(
        {"A": resolved_after[GUIDE]}
    ),
    "resolver_amount_before": resolved_before[GUIDE].get("amount"),
    "resolver_amount_after": resolved_after[GUIDE].get("amount"),
    "guides_with_changed_resolution": changed,
}
result["ssot_mutation"] = mutation
log(f"SSOT mutated: {mutation}")
ok = (
    mutation["ssot_sha256_before"] != mutation["ssot_sha256_after"]
    and mutation["picked_guide_resolution_digest_before"]
    != mutation["picked_guide_resolution_digest_after"]
    and mutation["resolver_amount_after"] == "concise"
    and changed == [GUIDE]
)
result["mutation_ok_f806"] = ok
(EVIDENCE / "leg2-prepare-result.json").write_text(
    json.dumps(result, indent=2, default=str) + "\n", encoding="utf-8"
)
(EVIDENCE / "leg2-state.json").write_text(
    json.dumps({"trial2": TRIAL2, "trial1": TRIAL1, "tag": TAG}, indent=2) + "\n",
    encoding="utf-8",
)
log(f"=== LEG2 PREPARE {'OK' if ok else 'NOT-OK'} — trial2={TRIAL2} ===")
sys.exit(0 if ok else 1)
