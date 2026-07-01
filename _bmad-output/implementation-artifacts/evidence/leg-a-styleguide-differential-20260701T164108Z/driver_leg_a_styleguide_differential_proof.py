"""Leg-A AC#5 live differential proof — styleguide library produces measurably
different real Gamma output. Two styles (Classic classic-freeform-x-cards +
Studio hil-2026-apc-studio-image-card) over 3 C1M1 Part-3 slides spanning the
source-detail spectrum (LOW / MEDIUM / HIGH). Terminates at the deck render
(Storyboard-B-equivalent); NO Descript. First-run-stands; no retry-to-green.

Run: .venv/Scripts/python.exe scratchpad/leg_a_styleguide_differential_proof.py
"""
from __future__ import annotations
import hashlib, json, sys, traceback
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(override=True)

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from app.specialists.gary import _act as gary_act  # noqa: E402
from app.specialists.gary.styleguide_library import resolve_styleguide  # noqa: E402
from scripts.api_clients.gamma_client import GammaClient  # noqa: E402

TS = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
EV = REPO / "_bmad-output/implementation-artifacts/evidence" / f"leg-a-styleguide-differential-{TS}"
EV.mkdir(parents=True, exist_ok=True)
LOG = EV / "run.log"

def log(msg: str) -> None:
    line = f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")

# --- The 3 Part-3 slides, spanning source-detail LOW/MED/HIGH ---------------
SLIDES = [
    {  # LOW detail — Part 3 Summary Slide (bulleted recap, no visual prescription)
        "slide_id": "p3-low-summary",
        "detail_level": "LOW",
        "title": "From Ideas to Opportunities",
        "brief": (
            "You are already equipped: clinical skills (empathy, diagnosis) map "
            "directly to innovation frameworks (Design Thinking). Your arena: "
            "intrapreneurship is driving entrepreneurial change from within your "
            "existing health system. Your goal: move past generating Ideas "
            "(value = zero) to rigorously defining actionable Opportunities."
        ),
    },
    {  # MEDIUM detail — Slide 1 Physicianship = Innovation Leadership (image prompt)
        "slide_id": "p3-med-physicianship",
        "detail_level": "MEDIUM",
        "title": "Physicianship and Innovation Leadership",
        "brief": (
            "A clean, modern Venn diagram: left circle 'Physicianship', right "
            "circle 'Innovation Leadership'; the overlapping center lists Empathy, "
            "Curiosity, Analytical Prowess, Resiliency, Comfort with Ambiguity. "
            "Professional healthcare palette of navy blue and bright teal. Clinicians "
            "already hold the core traits of innovators; apply existing clinical "
            "traits to operational and systemic problems."
        ),
    },
    {  # HIGH detail — Design Brief "The Intrapreneur's Maze" (composition+palette+labels)
        "slide_id": "p3-high-maze",
        "detail_level": "HIGH",
        "title": "The Intrapreneur Maze",
        "brief": (
            "A 50/50 split-screen. LEFT (The Entrepreneur): a figure in a wide-open "
            "empty green field under a blue sky, easily building a small house from "
            "scratch; bright, airy, simple (green and light blue); label "
            "'Entrepreneur: Building on a blank canvas.' RIGHT (The Intrapreneur): a "
            "figure inside a highly complex glowing neon-blue architectural blueprint "
            "of a massive hospital, trying to remodel a single room, surrounded by "
            "thick immovable load-bearing pillars; dark background with glowing "
            "cyan/dark-blue/stark-white blueprint lines; pillars labeled 'Legacy IT', "
            "'Compliance', 'Hospital Politics', 'Operating Budgets.' Core message: "
            "intrapreneurship is harder than entrepreneurship because you must "
            "innovate without destroying existing load-bearing institutional structures."
        ),
    },
]

STYLE_A = "classic-freeform-x-cards"          # Classic (Tejal illustration, fluid)
STYLE_B_STUDIO = "hil-2026-apc-studio-image-card"   # Studio (full-bleed template)
STYLE_B_FALLBACK = "hil-2026-apc-blueprint-classic"  # Classic (Blueprint lineArt, 16x9)

def png_meta(path: str) -> dict:
    p = Path(path)
    out = {"file": p.name, "exists": p.exists()}
    if not p.exists():
        return out
    data = p.read_bytes()
    out["bytes"] = len(data)
    out["sha256"] = hashlib.sha256(data).hexdigest()[:16]
    try:
        from PIL import Image
        with Image.open(p) as im:
            w, h = im.size
        out["dims"] = f"{w}x{h}"
        out["aspect"] = round(w / h, 4) if h else None
    except Exception as e:
        out["dims_error"] = str(e)[:120]
    return out

def render(style_name: str, mode_label: str) -> dict:
    log(f"--- RENDER variant [{mode_label}] styleguide={style_name} ---")
    export_dir = EV / f"render-{mode_label}"
    export_dir.mkdir(exist_ok=True)
    payload = {
        "slides": SLIDES,
        "export_dir": str(export_dir),
        "gamma_settings": [{"variant_id": "A", "styleguide": style_name}],
        "additional_instructions": (
            "Use each slide's source detail faithfully; do not invent or drop "
            "labeled elements described in the brief."
        ),
    }
    resolved = resolve_styleguide(style_name)
    log(f"  resolved settings: {json.dumps(resolved, sort_keys=True)}")
    result = gary_act.generate_gamma_variants(payload, client=GammaClient())
    rows = result.get("gary_slide_output") or result.get("slide_content") or []
    per_slide = []
    for row in rows:
        fp = row.get("file_path") or row.get("visual_file") or ""
        per_slide.append({
            "slide_id": row.get("slide_id"),
            "generation_id": row.get("generation_id"),
            "png": png_meta(fp) if fp else {"exists": False},
        })
    log(f"  rendered {len(per_slide)} slides")
    return {"styleguide": style_name, "mode": mode_label, "resolved_settings": resolved,
            "per_slide": per_slide}

def main() -> int:
    log(f"EVIDENCE DIR: {EV}")
    report = {"ts": TS, "slides": [{k: s[k] for k in ('slide_id','detail_level','title')} for s in SLIDES]}

    # Arm A — Classic
    try:
        arm_a = render(STYLE_A, "A-classic")
    except Exception as e:
        log(f"ARM A FAILED (fatal — no proof without it): {type(e).__name__}: {e}")
        traceback.print_exc()
        report["error"] = f"arm_a: {e}"
        (EV / "result.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        return 2

    # Arm B — Studio, fallback to Blueprint Classic on studio failure
    studio_ok = True
    try:
        arm_b = render(STYLE_B_STUDIO, "B-studio")
    except Exception as e:
        studio_ok = False
        log(f"ARM B (studio) FAILED: {type(e).__name__}: {e} -> FALLBACK to {STYLE_B_FALLBACK}")
        report["studio_fallback_reason"] = f"{type(e).__name__}: {str(e)[:200]}"
        arm_b = render(STYLE_B_FALLBACK, "B-classic-fallback")

    report["arm_a"] = arm_a
    report["arm_b"] = arm_b
    report["studio_spanned"] = studio_ok

    # --- Differential judge (deterministic, per-slide) ---
    diffs = []
    a_by = {r["slide_id"]: r for r in arm_a["per_slide"]}
    b_by = {r["slide_id"]: r for r in arm_b["per_slide"]}
    for s in SLIDES:
        sid = s["slide_id"]
        a, b = a_by.get(sid, {}), b_by.get(sid, {})
        ap, bp = a.get("png", {}), b.get("png", {})
        distinct_sha = ap.get("sha256") and bp.get("sha256") and ap["sha256"] != bp["sha256"]
        distinct_dims = ap.get("dims") and bp.get("dims") and ap["dims"] != bp["dims"]
        diffs.append({
            "slide_id": sid, "detail_level": s["detail_level"],
            "a_png": ap, "b_png": bp,
            "distinct_sha": bool(distinct_sha), "distinct_dims": bool(distinct_dims),
            "measurably_different": bool(distinct_sha or distinct_dims),
        })
    report["differential"] = diffs
    settings_differ = arm_a["resolved_settings"] != arm_b["resolved_settings"]
    report["resolved_settings_differ"] = settings_differ

    low_med = [d for d in diffs if d["detail_level"] in ("LOW", "MEDIUM")]
    no_vacuous_green = settings_differ and all(d["measurably_different"] for d in low_med) and len(low_med) >= 2
    report["AC5_no_vacuous_green_PASS"] = bool(no_vacuous_green)

    (EV / "result.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    log("=== DIFFERENTIAL SUMMARY ===")
    log(f"  resolved_settings_differ: {settings_differ}")
    for d in diffs:
        log(f"  {d['detail_level']:6} {d['slide_id']}: different={d['measurably_different']} "
            f"(sha={d['distinct_sha']} dims={d['distinct_dims']}) "
            f"A={d['a_png'].get('dims')} B={d['b_png'].get('dims')}")
    log(f"  studio_spanned: {studio_ok}")
    log(f"  AC#5 no-vacuous-green PASS: {no_vacuous_green}")
    log(f"RESULT JSON: {EV / 'result.json'}")
    return 0 if no_vacuous_green else 1

if __name__ == "__main__":
    sys.exit(main())
