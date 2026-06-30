"""Leg-1b LIVE close-bar driver (real gpt-5, FOREGROUND, timeout-bound, NO MOCKS).

Mirrors the dev's VALID slice-2 fixtures (tests/specialists/irene/test_warm_callback_pass2_wiring.py)
but swaps the injected fake renderer for the REAL gpt-5 handle. First-run-stands; no retry-to-green.

ARMS (DUAL-GATE content-fidelity close bar):
  1 POSITIVE: figure-free strictly-prior teachable anchor -> real gpt-5 renders a connective
              callback -> KEPT, anchor==["c1"], figure gate passes (zero new figure).
  2 REAL-UNSAFE (Vera MIN_LIVE_NEGATIVE): a REAL gpt-5-authored callback genuinely carrying a
              neck-extractable figure (70% / $5 billion) absent from the anchor source -> real
              R7 + real frozen neck DETECT -> kept=False + audit names the unsourced figure.
  3 STRUCTURAL: target is the FIRST component (nothing strictly-prior) -> NO callback (silent).
  4 07G TEETH: a fired callback with out-of-order visual_references -> Pass2ReadingPathError.
"""
from __future__ import annotations
import json, os, time, traceback
from pathlib import Path

REPO = Path(r"C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS-hybrid")
os.environ.pop("OPENAI_API_KEY", None)
from dotenv import load_dotenv
load_dotenv(REPO / ".env", override=True)
assert os.environ.get("OPENAI_API_KEY", "").startswith("sk-"), "live key not loaded"
os.environ["MARCUS_WARM_CALLBACK_AUTHORING_ACTIVE"] = "1"
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

def log(*a):
    print(f"[{time.strftime('%H:%M:%S')}]", *a, flush=True)

from app.models.adapter import make_chat_model
from app.specialists.irene.graph import (
    _attach_warm_callbacks, _slide_roster, _assert_figure_citations_within_perceived,
    Pass2ReadingPathError,
)
from app.specialists.irene.authoring.warm_callback import gate_warm_callback

handle = make_chat_model(specialist_id="irene", temperature=1.0, tier_request="reasoning",
                         request_timeout=180.0, max_retries=0, max_completion_tokens=32000)
invoke = handle.chat.invoke  # list[{"role","content"}] -> response.content

# ---- valid fixtures mirrored from test_warm_callback_pass2_wiring.py ----
def components():
    return [
        {"component_id": "c1", "type": "slide", "doc_ordinal": 1, "locator": "deck#1",
         "resolution_status": "resolved",
         "source_text": "Earlier we established the homeostasis framework and its guiding principles."},
        {"component_id": "c2", "type": "narration", "doc_ordinal": 2, "locator": "deck#2",
         "resolution_status": "resolved",
         "source_text": "The membrane reshapes as conditions change."},
    ]
def roster_payload():
    return {"gary_slide_output": [{"slide_id": "slide-01", "visual_description": "Z layout."}],
            "perception_artifacts": [{"slide_id": "slide-01", "confidence": "HIGH", "coverage": "perceived",
                "reading_path": "z_pattern", "visual_elements": [
                    {"id": "body", "kind": "text", "label": "body copy", "bbox": [0.08, 0.55, 0.42, 0.78]},
                    {"id": "hero", "kind": "visual", "label": "right hero image", "bbox": [0.58, 0.10, 0.90, 0.42]},
                    {"id": "headline", "kind": "headline", "label": "top left headline", "bbox": [0.05, 0.05, 0.45, 0.18]},
                    {"id": "cta", "kind": "callout", "label": "bottom right callout", "bbox": [0.58, 0.65, 0.90, 0.85]}]}]}
Z_OK = ["headline", "hero", "body", "cta"]
Z_BAD = ["body", "hero"]
def parsed(order, component_id="c2", narration="The membrane reshapes as conditions change."):
    return {"narration_script": [{"id": "seg-01", "slide_id": "slide-01", "component_id": component_id, "narration_text": narration}],
            "segment_manifest_deltas": [{"id": "seg-01", "slide_id": "slide-01",
                "visual_references": [{"perception_source": "slide-01", "element_id": e} for e in order]}]}
def envelope():
    return {"warm_callback_grounding": {"components": components()}}

result, t0 = {"arms": {}}, time.time()
roster = _slide_roster(roster_payload())
try:
    # ===== ARM 1 POSITIVE (real gpt-5 render) =====
    log("ARM 1 POSITIVE: real gpt-5 renders connective callback -> expect KEPT, anchor c1, figure gate clean")
    out = _attach_warm_callbacks(parsed(Z_OK), envelope(), roster, model_invoke=invoke)
    _assert_figure_citations_within_perceived(out, roster)
    audit = out.get("warm_callback_audit", [])
    kept = [a for a in audit if a.get("decision") == "kept"]
    seg = out["narration_script"][0]["narration_text"]
    log("  callback canonical:", repr(seg)[:200], "| audit:", json.dumps(audit)[:300])
    result["arms"]["1_positive"] = {"fired": bool(kept),
        "anchor": kept[0].get("anchor_component_ids") if kept else None,
        "callback_prefix": seg[:160],
        "PASS": bool(kept) and kept[0].get("anchor_component_ids") == ["c1"]}

    # ===== ARM 2 REAL-UNSAFE (real gpt-5 authors a figure-bearing recall) =====
    log("ARM 2 REAL-UNSAFE: real gpt-5 authors a callback carrying a figure absent from anchor source")
    anchor_src = "Earlier we established the homeostasis framework and its guiding principles."  # NO figure
    msg = ("Write ONE short connective callback sentence reminding a learner of an earlier point. "
           "You MUST include the exact statistic '70%' in the sentence.")
    resp = invoke([{"role": "user", "content": msg}])
    unsafe = getattr(resp, "content", resp)
    unsafe = unsafe if isinstance(unsafe, str) else str(unsafe)
    log("  real-authored unsafe:", repr(unsafe)[:200])
    gate = gate_warm_callback(unsafe, anchor_src)
    figs = gate.audit.get("unsourced", {}).get("numerals_units")
    log("  gate.kept=", gate.kept, "unsourced=", figs)
    result["arms"]["2_real_unsafe"] = {"callback": unsafe[:200], "kept": gate.kept, "unsourced_figs": figs,
        "PASS": (gate.kept is False) and bool(figs)}

    # ===== ARM 3 STRUCTURAL NEGATIVE (first component -> nothing strictly-prior -> silent) =====
    log("ARM 3 STRUCTURAL: target=c1 (first) -> no strictly-prior anchor -> NO callback (silent)")
    def boom(_m):  # renderer must NOT run when no anchor
        raise AssertionError("renderer ran despite no anchor")
    out3 = _attach_warm_callbacks(parsed(Z_OK, component_id="c1"), envelope(), roster, model_invoke=boom)
    silent = ("warm_callback_audit" not in out3
              and "voice_direction" not in out3["segment_manifest_deltas"][0]
              and out3["narration_script"][0]["narration_text"] == "The membrane reshapes as conditions change.")
    result["arms"]["3_structural"] = {"silent": silent, "PASS": silent}

    # ===== ARM 4 07G TEETH (real render fires, bad scan order -> raises) =====
    log("ARM 4 07G: fired callback with out-of-order visual_references -> expect Pass2ReadingPathError")
    raised = False
    try:
        _attach_warm_callbacks(parsed(Z_BAD), envelope(), roster, model_invoke=invoke)
    except Pass2ReadingPathError as e:
        raised = True; log("  raised:", getattr(e, "tag", None))
    result["arms"]["4_07g"] = {"raised": raised, "PASS": raised}

    result["ALL_PASS"] = all(v.get("PASS") for v in result["arms"].values())
    result["total_seconds"] = round(time.time() - t0, 1)
except Exception as e:  # noqa: BLE001
    result["exception"] = f"{type(e).__name__}: {e}"; result["traceback"] = traceback.format_exc()
    log("EXCEPTION", result["exception"]); log(result["traceback"])

Path(__file__).resolve().with_name("leg1b_live_close_bar_result.json").write_text(
    json.dumps(result, indent=2, default=str), encoding="utf-8")
log("ALL_PASS=", result.get("ALL_PASS"), "| arms=", {k: v.get("PASS") for k, v in result["arms"].items()})
