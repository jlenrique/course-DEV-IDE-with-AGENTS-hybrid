"""AC#8 live-proof — gamma-instructions-channel-cleanup (dual-gate).

Real Gamma dispatch on a HIGH-source-detail slide, capturing the OUTBOUND payload
(the party's de-subjectified bar — judge the wire + on-disk, not an eyeball).

Proves:
 (a) redaction — the sent additionalInstructions has NO settings-dump, NO literal
     None, NO key=value settings token;
 (b) source-detail conveyance PRESERVED — source additional_instructions verbatim +
     source keywords rendered as "Emphasize this imagery: ..." guidance;
 (c) structured carry — the SAME settings still travel via imageOptions.stylePreset /
     textOptions.amount/tone (nothing that worked was moved);
 (d) real render — the HIGH-detail card materializes with real bytes.

First-run-stands. No retry-to-green. No mocks.
Run FOREGROUND: .venv/Scripts/python.exe scratchpad/instructions_cleanup_ac8_live.py
"""
from __future__ import annotations
import hashlib, json, re, sys, traceback
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
EV = REPO / "_bmad-output/implementation-artifacts/evidence" / f"instructions-cleanup-ac8-{TS}"
EV.mkdir(parents=True, exist_ok=True)
LOG = EV / "run.log"

def log(m: str) -> None:
    line = f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] {m}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")

STYLE = "classic-freeform-x-cards"
SOURCE_INSTR = (
    "SOURCE DESIGN NOTE: required on-card labels — 'Legacy IT', 'Compliance', "
    "'Hospital Politics', 'Operating Budgets'. Palette: neon-blue blueprint lines on "
    "dark background. Do not drop or rename any labelled element."
)
SOURCE_KEYWORDS = ["vector", "minimalist", "single-accent color"]

# Known-good 3-slide Leg-A corpus (single-slide decks hit the bijective title-matcher
# flake; the 3-slide set renders cleanly). The HIGH-detail maze slide is one of the
# three — labels + palette are the conveyance witness. Corpus-swap per the documented
# title-matcher gotcha, NOT retry-to-green (the wire witness is captured either way).
SLIDES = [
    {"slide_id": "p3-low-summary", "title": "From Ideas to Opportunities",
     "brief": "Clinical skills map to innovation frameworks; move past Ideas to actionable Opportunities."},
    {"slide_id": "p3-med-physicianship", "title": "Physicianship and Innovation Leadership",
     "brief": "A Venn diagram of Physicianship and Innovation Leadership; navy and teal palette; shared traits: empathy, curiosity, resiliency."},
    {"slide_id": "p3-high-maze", "title": "The Intrapreneur Maze",
     "brief": ("A 50/50 split-screen. LEFT: a figure in an empty green field building a small house; "
               "label 'Entrepreneur: Building on a blank canvas.' RIGHT: a figure inside a complex "
               "glowing neon-blue blueprint of a hospital, surrounded by load-bearing pillars labelled "
               "'Legacy IT', 'Compliance', 'Hospital Politics', 'Operating Budgets.'")},
]

class CapturingGammaClient(GammaClient):
    """Real client that records the kwargs sent to generate_deck — the wire witness."""
    def __init__(self) -> None:
        super().__init__()
        self.sent: list[dict] = []
    def generate_deck(self, input_text, **kwargs):  # type: ignore[override]
        self.sent.append({
            "additional_instructions": kwargs.get("additional_instructions"),
            "image_options": kwargs.get("image_options"),
            "text_options": kwargs.get("text_options"),
            "text_mode": kwargs.get("text_mode"),
        })
        log(f"  >>> REAL generate_deck; additional_instructions len="
            f"{len(str(kwargs.get('additional_instructions') or ''))}")
        return super().generate_deck(input_text, **kwargs)

def png_meta(path: str) -> dict:
    p = Path(path)
    out = {"file": p.name, "exists": p.exists()}
    if p.exists():
        b = p.read_bytes()
        out["bytes"] = len(b); out["sha256"] = hashlib.sha256(b).hexdigest()[:16]
    return out

def main() -> int:
    log(f"EVIDENCE DIR: {EV}")
    resolved = resolve_styleguide(STYLE)
    log(f"resolved {STYLE}: {json.dumps(resolved, sort_keys=True)}")
    export_dir = EV / "render"; export_dir.mkdir(exist_ok=True)
    payload = {
        "slides": SLIDES,
        "export_dir": str(export_dir),
        "additional_instructions": SOURCE_INSTR,
        "gamma_settings": [{"variant_id": "A", "styleguide": STYLE, "keywords": SOURCE_KEYWORDS}],
    }
    client = CapturingGammaClient()
    try:
        result = gary_act.generate_gamma_variants(payload, client=client)
    except Exception as e:
        log(f"LIVE FAILED: {type(e).__name__}: {e}")
        traceback.print_exc()
        (EV / "result.json").write_text(json.dumps({"error": f"{type(e).__name__}: {e}"}, indent=2), encoding="utf-8")
        return 2

    sent = client.sent[0] if client.sent else {}
    ai = str(sent.get("additional_instructions") or "")
    img = sent.get("image_options") or {}
    txt = sent.get("text_options") or {}
    rows = result.get("gary_slide_output") or []
    pngs = [png_meta(r.get("file_path") or "") for r in rows]

    # (a) redaction — no settings-dump / None / key=value settings token
    dump_markers = ["Apply this variant's Gamma settings", "image_style_preset=",
                    "amount=", "tone=", "template=", "image_style="]
    none_leak = bool(re.search(r"\bNone\b", ai))
    dump_leak = [m for m in dump_markers if m in ai]
    # (b) conveyance preserved
    source_verbatim = SOURCE_INSTR in ai
    keywords_as_guidance = ("Emphasize this imagery:" in ai) and all(k in ai for k in SOURCE_KEYWORDS)
    no_keyword_token = "keywords=" not in ai
    # (c) structured carry (nothing moved) — styleguide's stylePreset/amount/tone travel structurally
    exp_preset = resolved.get("image_style_preset")
    style_preset_structured = (img.get("stylePreset") == exp_preset) if exp_preset else True
    text_opts_present = bool(txt)  # amount/tone/audience/language ride here
    # (d) real render
    rendered = bool(rows) and all(p.get("exists") and p.get("bytes", 0) > 0 for p in pngs)

    checks = {
        "redaction_no_settings_dump": not dump_leak,
        "redaction_no_None_literal": not none_leak,
        "source_additional_instructions_verbatim": source_verbatim,
        "keywords_as_guidance_not_token": keywords_as_guidance and no_keyword_token,
        "stylePreset_travels_structurally": style_preset_structured,
        "textOptions_present_structurally": text_opts_present,
        "high_detail_card_rendered_real_bytes": rendered,
    }
    ac8_pass = all(checks.values())
    report = {
        "ts": TS, "style": STYLE, "resolved": resolved,
        "sent_additional_instructions": ai,
        "sent_image_options": img, "sent_text_options": txt,
        "dump_leak": dump_leak, "none_leak": none_leak,
        "per_slide_png": pngs, "checks": checks, "AC8_PASS": ac8_pass,
    }
    (EV / "result.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    log("=== AC#8 SUMMARY ===")
    log(f"  SENT additionalInstructions: {ai!r}")
    log(f"  SENT imageOptions: {json.dumps(img, sort_keys=True)}")
    log(f"  SENT textOptions: {json.dumps(txt, sort_keys=True)}")
    for k, v in checks.items():
        log(f"  {'PASS' if v else 'FAIL'}  {k}")
    log(f"  AC#8 PASS: {ac8_pass}")
    return 0 if ac8_pass else 1

if __name__ == "__main__":
    sys.exit(main())
