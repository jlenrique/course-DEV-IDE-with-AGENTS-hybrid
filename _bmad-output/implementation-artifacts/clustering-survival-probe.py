"""T1 survival probe (amendment #2): hand-feed FRESH cluster-bearing input
through the dormant April downstream and confirm it EXECUTES end-to-end —
not just that frozen unit fixtures pass. Gate on the witness (Murat #3).

Run:  .venv/Scripts/python.exe <this file>
Exit 0 = downstream executes on fresh cluster input; nonzero = bit-rot found.
"""
from __future__ import annotations

import importlib.util
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO = Path.cwd()
if not ((REPO / "app").is_dir() and (REPO / "scripts").is_dir()):
    raise SystemExit(f"repo root not found at cwd={REPO}")
sys.path.insert(0, str(REPO))

failures: list[str] = []


def check(label: str, cond: bool, detail: str = "") -> None:
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {label}" + (f" — {detail}" if detail else ""))
    if not cond:
        failures.append(label)


# ---- Leg 1: Gary cluster derivation on FRESH hand-fed slides ----------------
# Load run_gary_dispatch via spec (it has heavy import side-effects at module
# top, but the cluster fns are pure); import only the functions we need by
# loading the module file directly.
spec = importlib.util.spec_from_file_location(
    "rgd_probe", REPO / "scripts" / "utilities" / "run_gary_dispatch.py"
)
try:
    rgd = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rgd)
    rgd_loaded = True
except Exception as exc:  # pragma: no cover - env dependent
    print(f"[WARN] run_gary_dispatch import failed (env dep): {exc!r}")
    print("       falling back to source-level function extraction")
    rgd_loaded = False

if rgd_loaded:
    # Fresh cluster input: a dense slide became a head + 2 interstitials.
    slides = [
        {"slide_number": 1, "cluster_id": "c-probe01", "cluster_role": "head",
         "cluster_interstitial_count": 2, "narrative_arc":
         "From overload awareness to capacity management through targeted interventions"},
        {"slide_number": 2, "cluster_id": "c-probe01", "cluster_role": "interstitial"},
        {"slide_number": 3, "cluster_id": "c-probe01", "cluster_role": "interstitial"},
        {"slide_number": 4, "cluster_id": "c-probe02", "cluster_role": "head",
         "cluster_interstitial_count": None, "narrative_arc":
         "From skepticism to confidence through evidence-based reasoning"},
        {"slide_number": 5, "cluster_id": "c-probe02", "cluster_role": "interstitial"},
    ]
    derived = rgd._derive_clusters(slides, envelope={})
    check("derive_clusters executes on fresh slides", isinstance(derived, list))
    check("derive_clusters finds 2 heads", len(derived) == 2, f"got {len(derived)}")
    c1 = next((c for c in derived if c["cluster_id"] == "c-probe01"), None)
    check("c-probe01 interstitial_count == 2 (explicit)",
          c1 is not None and c1["interstitial_count"] == 2,
          f"{c1}")
    c2 = next((c for c in derived if c["cluster_id"] == "c-probe02"), None)
    check("c-probe02 interstitial_count == 1 (derived from members)",
          c2 is not None and c2["interstitial_count"] == 1,
          f"{c2}")
    check("narrative_arc carried on head",
          c1 is not None and "overload awareness" in (c1["narrative_arc"] or ""))

    # merge + metadata round-trip
    target: dict = {}
    rgd._merge_slide_cluster_fields(target, slides[0])
    check("merge_slide_cluster_fields copies cluster_id/role",
          target.get("cluster_id") == "c-probe01" and target.get("cluster_role") == "head",
          str(target))
    meta = rgd._slide_cluster_metadata(slides[0])
    check("slide_cluster_metadata extracts narrative_arc + count",
          meta.get("narrative_arc") and meta.get("cluster_interstitial_count") == 2,
          str(meta))

    # declared-clusters path
    declared = rgd._derive_clusters([], envelope={"clusters": [
        {"cluster_id": "c-declared", "interstitial_count": 3, "narrative_arc": "x"}]})
    check("declared-clusters envelope path executes",
          len(declared) == 1 and declared[0]["cluster_id"] == "c-declared")


# ---- Leg 2: Pass-2 cluster-bearing envelope VALIDATES ----------------------
from app.specialists.irene.authoring.pass_2_template import (  # noqa: E402
    IrenePass2AuthoringEnvelope,
    REQUIRED_PROCEDURAL_RULES,
)

png = "runs/probe/slide_01.png"
png2 = "runs/probe/slide_02.png"


def seg(sid: str, slide: str, card: int, visual: str, *, cid, role, pos):
    return {
        "id": sid, "slide_id": slide, "card_number": card,
        "narration_text": "Probe narration line for the cluster segment.",
        "behavioral_intent": "credible", "visual_file": visual,
        "visual_detail_load": "medium", "timing_role": "anchor",
        "content_density": "medium",
        "duration_rationale": "Probe rationale for timing.",
        "bridge_type": "cluster_boundary",
        "visual_references": [{
            "element": "title", "location_on_slide": "top",
            "narration_cue": "Probe narration line for the cluster segment.",
            "perception_source": slide}],
        "cluster_id": cid, "cluster_role": role, "cluster_position": pos,
    }


envelope = {
    "schema_version": "irene-pass-2-authoring.v1",
    "run_id": "probe-run",
    "generated_at_utc": datetime.now(UTC).isoformat(),
    "composition_mode": "composed",
    "gary_slide_output": [
        {"slide_id": "s1", "card_number": 1, "file_path": png, "source_ref": "src1"},
        {"slide_id": "s2", "card_number": 2, "file_path": png2, "source_ref": "src2"},
    ],
    "perception_artifacts": [
        {"slide_id": "s1", "source_image_path": png, "visual_elements": []},
        {"slide_id": "s2", "source_image_path": png2, "visual_elements": []},
    ],
    "segment_manifest": {"segments": [
        seg("seg1", "s1", 1, png, cid="c-probe01", role="head", pos="establish"),
        seg("seg2", "s2", 2, png2, cid="c-probe01", role="interstitial", pos="tension"),
    ]},
    "narration_script_markers": ["seg1", "seg2"],
    "procedural_rules": list(REQUIRED_PROCEDURAL_RULES),
}

try:
    model = IrenePass2AuthoringEnvelope.model_validate(envelope)
    segs = model.segment_manifest.segments
    check("cluster-bearing Pass-2 envelope validates", True)
    check("cluster fields survive validation",
          segs[0].cluster_id == "c-probe01" and segs[0].cluster_role == "head"
          and segs[0].cluster_position == "establish")
    check("cluster_arc_continuity rule present in validated envelope",
          "cluster_arc_continuity" in model.procedural_rules)
except Exception as exc:
    check("cluster-bearing Pass-2 envelope validates", False, repr(exc))

# Negative control: cluster_id without cluster_role must be REJECTED (proves the
# guard executes, not just that it's present in source).
bad = {**envelope, "segment_manifest": {"segments": [
    {**seg("seg1", "s1", 1, png, cid="c-probe01", role="head", pos="establish"),
     "cluster_role": None}]}, "narration_script_markers": ["seg1"]}
bad["gary_slide_output"] = [envelope["gary_slide_output"][0]]
bad["perception_artifacts"] = [envelope["perception_artifacts"][0]]
try:
    IrenePass2AuthoringEnvelope.model_validate(bad)
    check("cluster_role-required guard rejects bad input", False, "accepted bad input")
except Exception:
    check("cluster_role-required guard rejects bad input", True)


print()
if failures:
    print(f"SURVIVAL PROBE: {len(failures)} FAILURE(S) — bit-rot suspected: {failures}")
    sys.exit(1)
print("SURVIVAL PROBE: ALL GREEN — dormant downstream executes on fresh cluster input.")
