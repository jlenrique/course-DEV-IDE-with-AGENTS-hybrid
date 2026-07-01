"""Leg-4 TEETH WITNESS (offline, REAL Pass-2 artifacts; no live regen).

Bundle:  scratchpad/leg3-c-u03-persubslide-bundle/  (real gpt-5.5 Pass-2 run)
Source:  extracted.md (real corpus)   Narration: pass2-output.json (real)

(i)  real narration as-authored + real source + real deck -> gate SAILS (flag ON).
(ii) same real narration with ONE synthetic digit-form figure injected -> RAISES:
       (ii-a) unsourced confabulation ($4.6B, source has no money)  -> figure-unsourced
       (ii-b) source-vs-deck conflict (deck confabulates 60%, source 66%) -> figure-source-deck-conflict
Flag OFF control: the injected-defect narration is INERT (proves the firewall).

"Wired isn't accepted until it rejects something."
"""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path

os.environ["MARCUS_NARRATION_FIGURE_FIDELITY_ACTIVE"] = "1"  # flag ON for the witness

from app.specialists._shared.figure_tokens import _figures  # noqa: E402
from app.specialists.irene.graph import (  # noqa: E402
    Pass2GroundingError,
    _assert_figure_citations_within_perceived,
    _assert_narration_figures_sourced,
    _slide_roster,
    narration_figure_fidelity_active,
)

BUNDLE = Path("scratchpad/leg3-c-u03-persubslide-bundle")
SOURCE = (BUNDLE / "extracted.md").read_text(encoding="utf-8")
PARSED = json.loads((BUNDLE / "pass2-output.json").read_text(encoding="utf-8"))
ARTIFACTS = json.loads((BUNDLE / "perception-artifacts.json").read_text(encoding="utf-8"))

# Reconstruct a minimal-but-real envelope so the REAL _slide_roster computes REAL
# perceived (deck) figures from the REAL perception artifacts.
envelope = {
    "bundle_reference": str(BUNDLE),
    "lesson_plan": {"title": "AI in Clinical Practice (real c-u03 probe)"},
    "gary_slide_output": [
        {"slide_id": a["slide_id"], "visual_description": a.get("slide_title", "")}
        for a in ARTIFACTS
    ],
    "perception_artifacts": ARTIFACTS,
}
roster = _slide_roster(envelope)

lines: list[str] = []
def log(msg: str) -> None:
    print(msg)
    lines.append(msg)

log(f"flag active: {narration_figure_fidelity_active()}")
log(f"SOURCE in-scope digit figures: {sorted(_figures(SOURCE))}")
for e in roster:
    log(f"  deck perceived[{e['slide_id']}] = {sorted(e.get('perceived_figures') or [])}")
narr_all = " ".join(s.get("narration_text", "") for s in PARSED["narration_script"])
log(f"REAL narration in-scope digit figures: {sorted(_figures(narr_all))}")
log("")

# ---- (i) real narration SAILS both gates (flag ON) ----
_assert_figure_citations_within_perceived(PARSED, roster)  # deck-direction (always on)
_assert_narration_figures_sourced(PARSED, roster, source_text=SOURCE)  # source-direction
log("(i)   REAL narration as-authored: SAILS both deck- and source-direction gates. OK")

# ---- (ii-a) inject an UNSOURCED confabulation into the REAL narration ----
defect_a = copy.deepcopy(PARSED)
defect_a["narration_script"][0]["narration_text"] += (
    " The addressable market is $4.6B this year."  # source has NO money figure
)
try:
    _assert_narration_figures_sourced(defect_a, roster, source_text=SOURCE)
    log("(ii-a) FAILED TO RAISE on $4.6B confabulation — WITNESS BROKEN")
    raise SystemExit(2)
except Pass2GroundingError as exc:
    log(f"(ii-a) injected $4.6B -> RAISED tag={exc.value if False else exc.tag}: {exc}")

# ---- (ii-b) simulate Gamma confabulating 60% on card-01 (deck) vs source 66% ----
# Add 60% to the REAL card-01 deck perceived set (deck confabulation), then narrate 60%.
roster_conflict = copy.deepcopy(roster)
roster_conflict[0]["perceived_figures"] = sorted(
    set(roster_conflict[0].get("perceived_figures") or []) | {"percent:60"}
)
defect_b = copy.deepcopy(PARSED)
defect_b["narration_script"][0]["narration_text"] = (
    "Adoption is already here — 60% of physicians report using some form of AI."
)
try:
    _assert_narration_figures_sourced(defect_b, roster_conflict, source_text=SOURCE)
    log("(ii-b) FAILED TO RAISE on source-vs-deck conflict — WITNESS BROKEN")
    raise SystemExit(2)
except Pass2GroundingError as exc:
    log(f"(ii-b) deck 60% vs source 66% -> RAISED tag={exc.tag}: {exc}")

# ---- flag-OFF firewall: the defect narration is INERT ----
os.environ.pop("MARCUS_NARRATION_FIGURE_FIDELITY_ACTIVE", None)
_assert_narration_figures_sourced(defect_a, roster, source_text=SOURCE)  # no raise
log(f"flag OFF firewall: injected-defect narration INERT (active={narration_figure_fidelity_active()}). OK")

log("")
log("VERDICT: PASS — gate SAILS on real narration and REJECTS both an unsourced")
log("confabulation and a source-vs-deck conflict injected into the REAL artifacts;")
log("flag-OFF firewall holds. The gate has teeth on real production output.")

Path(__file__).with_name("witness-output.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
