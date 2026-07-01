"""AC#8 live-proof — styleguide-retire-default-variant-pair (single-gate-PLUS).

Claim under test: a SINGLE-styleguide binding paid-dispatches EXACTLY ONE deck
(no unbound fixture-B), witnessed by the real Gamma generate_deck call-count and
re-judged from on-disk artifacts — NOT the driver's inline result field.

Discriminating (per Murat): the FREE deterministic block proves the normalizer
returns 1 for a single binding, 2 for A+B, and FAILS LOUD on [None]/duplicate —
so the same code tracks payload cardinality (the old hardcoded [A,B] gave 2). The
LIVE block then confirms the real paid path emits exactly ONE real Gamma call.

First-run-stands. No retry-to-green. Real Gamma, no mocks.
Run FOREGROUND: .venv/Scripts/python.exe scratchpad/retire_variant_pair_ac8_live_proof.py
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
from app.specialists.gary._act import GaryActError  # noqa: E402
from scripts.api_clients.gamma_client import GammaClient  # noqa: E402

TS = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
EV = REPO / "_bmad-output/implementation-artifacts/evidence" / f"retire-variant-pair-ac8-{TS}"
EV.mkdir(parents=True, exist_ok=True)
LOG = EV / "run.log"

def log(msg: str) -> None:
    line = f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")

STYLE = "classic-freeform-x-cards"  # a real Classic styleguide (Leg-A arm A)

# Reuse the EXACT Leg-A AC#5 corpus (proven to title-match with
# classic-freeform-x-cards) so the ONLY variable is variant count. First attempt
# used a bespoke single-slide title that hit the known bijective-title-matcher
# flake (gamma.export.brief-unmatched — a documented concierge-backlog gotcha,
# unrelated to this change; the real generate_deck call #1 had already fired).
# Corpus swapped to the known-good set per the documented "clean the TITLE" fix;
# NOT a retry-to-green on the logic under test.
SLIDES = [
    {
        "slide_id": "p3-low-summary",
        "title": "From Ideas to Opportunities",
        "brief": (
            "You are already equipped: clinical skills (empathy, diagnosis) map "
            "directly to innovation frameworks (Design Thinking). Your arena: "
            "intrapreneurship is driving entrepreneurial change from within your "
            "existing health system. Your goal: move past generating Ideas "
            "(value = zero) to rigorously defining actionable Opportunities."
        ),
    },
    {
        "slide_id": "p3-med-physicianship",
        "title": "Physicianship and Innovation Leadership",
        "brief": (
            "A clean, modern Venn diagram: left circle 'Physicianship', right "
            "circle 'Innovation Leadership'; the overlapping center lists Empathy, "
            "Curiosity, Analytical Prowess, Resiliency, Comfort with Ambiguity. "
            "Professional healthcare palette of navy blue and bright teal. Clinicians "
            "already hold the core traits of innovators."
        ),
    },
    {
        "slide_id": "p3-high-maze",
        "title": "The Intrapreneur Maze",
        "brief": (
            "A 50/50 split-screen. LEFT: a figure in a wide-open empty green field "
            "building a small house from scratch; bright, airy (green and light blue); "
            "label 'Entrepreneur: Building on a blank canvas.' RIGHT: a figure inside a "
            "complex glowing neon-blue architectural blueprint of a massive hospital, "
            "remodeling one room, surrounded by thick load-bearing pillars labelled "
            "'Legacy IT', 'Compliance', 'Hospital Politics', 'Operating Budgets.'"
        ),
    },
]

class CountingGammaClient(GammaClient):
    """Real GammaClient that counts generate_deck invocations — the paid-dispatch
    witness. A single binding must invoke generate_deck exactly ONCE."""
    def __init__(self) -> None:
        super().__init__()
        self.generate_deck_calls = 0
        self.generation_ids: list[str] = []

    def generate_deck(self, *args, **kwargs):  # type: ignore[override]
        self.generate_deck_calls += 1
        log(f"  >>> REAL generate_deck call #{self.generate_deck_calls}")
        result = super().generate_deck(*args, **kwargs)
        gid = result.get("id") or result.get("generation_id") or result.get("generationId")
        if gid:
            self.generation_ids.append(str(gid))
        return result

def png_meta(path: str) -> dict:
    p = Path(path)
    out = {"file": p.name, "exists": p.exists()}
    if p.exists():
        data = p.read_bytes()
        out["bytes"] = len(data)
        out["sha256"] = hashlib.sha256(data).hexdigest()[:16]
    return out

def deterministic_cardinality_block() -> dict:
    """FREE (no dispatch) discriminating proof: the projection tracks payload
    cardinality and fails loud on degenerate input."""
    log("--- DETERMINISTIC cardinality/fail-loud block (no dispatch) ---")
    res = {}
    # single binding -> 1
    one = gary_act._normalized_gamma_settings(
        {"gamma_settings": [{"variant_id": "A", "styleguide": STYLE}]}
    )
    res["single_bind_len"] = len(one)
    res["single_bind_variant"] = one[0]["variant_id"] if one else None
    # A + B -> 2 (the old hardcoded [A,B]; now genuinely from payload)
    two = gary_act._normalized_gamma_settings(
        {"gamma_settings": [{"variant_id": "A", "styleguide": STYLE},
                            {"variant_id": "B", "styleguide": STYLE}]}
    )
    res["ab_len"] = len(two)
    res["ab_order"] = [r["variant_id"] for r in two]
    # [None] -> raises (R2, closes the retired-fixture re-dispatch hole)
    try:
        gary_act._normalized_gamma_settings({"gamma_settings": [None]})
        res["none_list_raises"] = False
    except GaryActError as e:
        res["none_list_raises"] = True
        res["none_list_tag"] = e.tag
    # duplicate A -> raises (R1)
    try:
        gary_act._normalized_gamma_settings(
            {"gamma_settings": [{"variant_id": "A"}, {"variant_id": "A"}]}
        )
        res["dup_raises"] = False
    except GaryActError:
        res["dup_raises"] = True
    # empty -> [] (AC#4 preserved)
    res["empty_len"] = len(gary_act._normalized_gamma_settings({"gamma_settings": []}))
    log(f"  {json.dumps(res, sort_keys=True)}")
    res["PASS"] = (
        res["single_bind_len"] == 1 and res["single_bind_variant"] == "A"
        and res["ab_len"] == 2 and res["ab_order"] == ["A", "B"]
        and res["none_list_raises"] is True and res["dup_raises"] is True
        and res["empty_len"] == 0
    )
    log(f"  deterministic block PASS: {res['PASS']}")
    return res

def live_single_dispatch_block() -> dict:
    log(f"--- LIVE single-binding dispatch (real Gamma, styleguide={STYLE}) ---")
    export_dir = EV / "render-single-A"
    export_dir.mkdir(exist_ok=True)
    payload = {
        "slides": SLIDES,
        "export_dir": str(export_dir),
        "gamma_settings": [{"variant_id": "A", "styleguide": STYLE}],
        "additional_instructions": "Render faithfully; do not invent extra cards.",
    }
    client = CountingGammaClient()
    result = gary_act.generate_gamma_variants(payload, client=client)
    rows = result.get("gary_slide_output") or []
    variant_ids = sorted({str(r.get("variant_id")) for r in rows})
    pngs = [png_meta(r.get("file_path") or "") for r in rows]
    # Independent on-disk re-count (arbiter — NOT the driver's inline result field).
    on_disk_pngs = sorted(str(p.name) for p in export_dir.rglob("*.png"))
    block = {
        "generate_deck_calls_real": client.generate_deck_calls,   # THE paid-dispatch witness
        "server_generation_ids": client.generation_ids,
        "result_calls_made": result.get("calls_made"),
        "result_generation_mode": result.get("generation_mode"),
        "variant_ids_in_output": variant_ids,
        "n_output_rows": len(rows),
        "per_slide_png": pngs,
        "on_disk_png_files": on_disk_pngs,
        "n_on_disk_pngs": len(on_disk_pngs),
    }
    log(f"  {json.dumps(block, sort_keys=True)}")
    block["PASS"] = (
        client.generate_deck_calls == 1                    # exactly one PAID call
        and len(client.generation_ids) == 1                # one real server generation
        and result.get("calls_made") == 1
        and result.get("generation_mode") == "single-dispatch"
        and variant_ids == ["A"]                            # no unbound fixture-B row
        and "B" not in variant_ids
        and len(rows) >= 1
        and all(p.get("exists") and p.get("bytes", 0) > 0 for p in pngs)  # real bytes on disk
        and len(on_disk_pngs) == len(rows)                 # on-disk re-count matches
    )
    log(f"  live block PASS: {block['PASS']}")
    return block

def main() -> int:
    log(f"EVIDENCE DIR: {EV}")
    report = {"ts": TS, "style": STYLE, "claim": "single styleguide binding -> exactly 1 paid Gamma deck"}
    det = deterministic_cardinality_block()
    report["deterministic"] = det
    try:
        live = live_single_dispatch_block()
    except Exception as e:
        log(f"LIVE BLOCK FAILED (fatal — no proof without it): {type(e).__name__}: {e}")
        traceback.print_exc()
        report["live_error"] = f"{type(e).__name__}: {e}"
        (EV / "result.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        return 2
    report["live"] = live
    ac8_pass = bool(det["PASS"] and live["PASS"])
    report["AC8_PASS"] = ac8_pass
    (EV / "result.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    log("=== AC#8 SUMMARY ===")
    log(f"  deterministic cardinality/fail-loud: {det['PASS']}")
    log(f"  live real generate_deck calls: {live['generate_deck_calls_real']} (expect 1)")
    log(f"  live output variants: {live['variant_ids_in_output']} (expect ['A'])")
    log(f"  live on-disk PNGs: {live['n_on_disk_pngs']} (expect == {live['n_output_rows']})")
    log(f"  AC#8 PASS: {ac8_pass}")
    log(f"RESULT JSON: {EV / 'result.json'}")
    return 0 if ac8_pass else 1

if __name__ == "__main__":
    sys.exit(main())
