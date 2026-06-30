"""Coverage interlock LIVE slice (T8) — REAL gpt-5 segmentation + receipt + the
ablated-must-cover NEGATIVE case (gate blocks before audio). Timeout-bound client
(per-request 60s, max_retries=0) injected via chat_model_factory — no hang.
"""
from __future__ import annotations
import functools, json, os, re, sys
from datetime import UTC, datetime
from pathlib import Path
from dotenv import load_dotenv

print = functools.partial(print, flush=True)
REPO = Path(r"C:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS-hybrid")
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
SLIDES = REPO / "course-content/courses/tejal-apc-c1-m1-p2-trends/slides"
EVID = REPO / "_bmad-output/implementation-artifacts/evidence"

os.environ.pop("OPENAI_API_KEY", None)
load_dotenv(REPO / ".env", override=True)
from openai import OpenAI

from app.marcus.lesson_plan.coverage_annotation import build_coverage_annotations
from app.marcus.lesson_plan.coverage_receipt import (
    AnchorResolution, derive_coverage_receipt, coverage_plan_view,
)
from app.marcus.lesson_plan.coverage_gate import assert_coverage_gate, evaluate_coverage_gate, CoverageAssuranceError

NOTES_RE = re.compile(r"\*\*Narration \(Speaker Notes\):\*\*\s*[\"“]?(.+?)[\"”]?\s*$", re.MULTILINE)
VISUAL_RE = re.compile(r"\*\*(?:Visual Format|Prompt to Generate Image):\*\*\s*(.+)", re.IGNORECASE)


# --- timeout-bound chat-model shim (the pass calls handle.chat.invoke([...]) -> .content) ---
class _Resp:
    def __init__(self, content): self.content = content
class _Chat:
    def __init__(self, client): self.client = client
    def invoke(self, messages):
        r = self.client.chat.completions.create(
            model="gpt-5",
            messages=[{"role": m["role"], "content": m["content"]} for m in messages],
            max_completion_tokens=8000, reasoning_effort="low",
        )
        return _Resp(r.choices[0].message.content or "")
class _Handle:
    def __init__(self, client): self.chat = _Chat(client)
def factory(model_name: str):
    return _Handle(OpenAI(timeout=60.0, max_retries=0))


def slide_parts(p: Path) -> tuple[str, str]:
    txt = p.read_text(encoding="utf-8")
    notes = (m.group(1).strip() if (m := NOTES_RE.search(txt)) else "")
    visual = " ".join(VISUAL_RE.findall(txt))  # the on-slide gist surface
    return notes, visual


def main() -> int:
    files = sorted(SLIDES.glob("slide-*.md"))[:3]
    components, parts = [], {}
    for i, p in enumerate(files, start=1):
        notes, visual = slide_parts(p)
        cid = f"src-c{i:02d}"
        components.append({"component_id": cid, "type": "narration",
                           "locator": f"Course 1 > Module 1 > Part 2 > Slide {i}", "excerpt": notes})
        parts[f"Slide {i}"] = {"cid": cid, "notes": notes, "visual": visual}

    print(f"[live] {len(components)} real note-bearing components → REAL gpt-5 segmentation ...")
    anns = build_coverage_annotations(components, dispatch_live=True, chat_model_factory=factory)
    total_pts = sum(len(a.source_points) for a in anns)
    print(f"[live] {len(anns)} annotations, {total_pts} source points")
    for a in anns:
        mc = sum(1 for sp in a.source_points if (sp.verbatim_required or 'detail_in_narration' in sp.coverage_intents))
        print(f"  {a.component_id} ({a.slide_key}): {len(a.source_points)} pts, grain={a.segmentation}, ~{mc} must-cover")
        for sp in a.source_points[:3]:
            print(f"     - [{','.join(sp.risk_flags) or 'none'}] verbatim_req={sp.verbatim_required} :: {sp.verbatim_text[:80]}")
    assert anns, "no annotations from live pass"
    assert all(a.segmentation == "assertion_level" for a in anns), "grain not assertion_level"
    assert all(a.is_v1_shippable() for a in anns), "not v1-shippable"

    # --- COVERED receipt: slide-1 is a content slide (shows its text -> 'both'); slide-2/3 gist+narration ---
    covered_anchors = {}
    for skey, d in parts.items():
        slide_text = (d["notes"] + " " + d["visual"]) if skey == "Slide 1" else d["visual"]
        covered_anchors[skey] = AnchorResolution(
            slide_key=skey, slide_present=True, slide_text=slide_text,
            narration_present=True, narration_text=d["notes"], narration_ambiguous=False)
    covered = derive_coverage_receipt(anns, covered_anchors)
    statuses = {}
    for r in covered.rows:
        statuses[r.coverage_status] = statuses.get(r.coverage_status, 0) + 1
    print(f"\n[live] COVERED receipt: {len(covered.rows)} rows, status histogram = {statuses}")
    block_covered = evaluate_coverage_gate(covered)
    print(f"[live] gate on COVERED receipt: {len(block_covered)} blocking (expect 0)")
    on_slide = sum(statuses.get(s, 0) for s in ("covered_on_slide", "both"))
    in_narr = sum(statuses.get(s, 0) for s in ("covered_in_narration", "both"))
    assert on_slide >= 1, f"no covered_on_slide/both rows (got {statuses})"
    assert in_narr >= 1, f"no covered_in_narration/both rows (got {statuses})"
    assert len(block_covered) == 0, f"covered receipt should not block, got {len(block_covered)}"

    # --- ABLATED receipt: slide 3 DROPPED from the deck (no surfaces) -> its must-cover points BLOCK ---
    ablated_anchors = dict(covered_anchors)
    ablated_anchors["Slide 3"] = AnchorResolution(
        slide_key="Slide 3", slide_present=False, slide_text=None,
        narration_present=False, narration_text=None, narration_ambiguous=False)
    ablated = derive_coverage_receipt(anns, ablated_anchors)
    blocking = evaluate_coverage_gate(ablated)
    print(f"\n[live] ABLATED (slide-3 dropped): {len(blocking)} blocking must-cover rows (expect >=1)")
    raised = False
    try:
        assert_coverage_gate(ablated)
    except CoverageAssuranceError as e:
        raised = True
        print(f"[live] ✅ gate BLOCKED before audio spend: tag={e.tag}; {len(e.blocking_rows)} rows")
        print(f"        e.g. {[r.source_point_id for r in e.blocking_rows][:5]}")
    assert raised and blocking, "ABLATED receipt must trip the fail-loud gate"

    ts = datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%SZ")
    evidence = {
        "story": "concierge-coverage-assurance-interlock", "leg": "T8 live slice", "timestamp_utc": ts,
        "model": "gpt-5", "real_api": True, "n_components": len(components),
        "n_source_points": total_pts, "segmentation": "assertion_level",
        "covered_status_histogram": statuses,
        "covered_on_slide_or_both": on_slide, "covered_in_narration_or_both": in_narr,
        "covered_receipt_blocking": len(block_covered),
        "ablated_blocking_rows": [r.source_point_id for r in blocking],
        "gate_raised_before_audio": raised,
        "plan_view_n_points": coverage_plan_view(anns)["n_points"],
        "verdict": "PASS",
    }
    EVID.mkdir(parents=True, exist_ok=True)
    out = EVID / f"coverage-live-slice-{ts}.json"
    out.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    print(f"\n[live] ALL ASSERTIONS PASS. evidence -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
