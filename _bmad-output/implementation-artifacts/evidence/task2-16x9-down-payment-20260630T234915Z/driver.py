"""TASK 2 live proof — real Gamma Classic generation with cardOptions.dimensions=16x9
exports a 16:9 PNG (aspect ~1.778). NO MOCKS. Foreground.

Proves Gamma honors the dimension our 16:9 down-payment now sends by default on the Classic
path. (The unit test proves a DEFAULT run dispatches cardOptions.dimensions=16x9; this proves
the Gamma side yields a 16:9 export.) first-run-stands.
"""
from __future__ import annotations
import io, json, os, re, time, traceback
from pathlib import Path

REPO = Path(r"C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS-hybrid")
os.environ.pop("OPENAI_API_KEY", None)
from dotenv import load_dotenv
load_dotenv(REPO / ".env", override=True)
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

def log(*a):
    print(f"[{time.strftime('%H:%M:%S')}]", *a, flush=True)

import requests
from PIL import Image
from scripts.api_clients.gamma_client import GammaClient

def find_png_urls(obj):
    found = []
    def walk(x):
        if isinstance(x, str):
            if re.search(r"https?://\S+\.png", x) or (x.startswith("http") and "export" in x.lower()):
                found.append(x.split()[0])
        elif isinstance(x, dict):
            for v in x.values(): walk(v)
        elif isinstance(x, (list, tuple)):
            for v in x: walk(v)
    walk(obj)
    return found

result, t0 = {}, time.time()
try:
    client = GammaClient()
    log("generate_deck Classic, cardOptions.dimensions=16x9, export png ...")
    completed = client.generate_deck(
        input_text="A concise single-slide overview titled 'Clinical Leadership in One Slide' with a short subtitle.",
        text_mode="generate",
        num_cards=1,
        export_as="png",
        card_options={"dimensions": "16x9"},
        wait=True,
    )
    result["completed_keys"] = sorted(completed.keys()) if isinstance(completed, dict) else str(type(completed))
    result["status"] = completed.get("status") if isinstance(completed, dict) else None
    log("status=", result["status"], "keys=", result["completed_keys"])
    urls = find_png_urls(completed)
    log("png urls found:", urls[:5])
    result["png_urls"] = urls[:5]
    if not urls:
        # dump a trimmed view to find the export field
        result["completed_sample"] = json.dumps(completed, default=str)[:1500]
        raise RuntimeError("no PNG export URL in completed generation (see completed_sample)")
    png = requests.get(urls[0], timeout=60).content
    im = Image.open(io.BytesIO(png))
    w, h = im.size
    aspect = round(w / h, 4)
    result.update({"png_url": urls[0], "width": w, "height": h, "aspect": aspect,
                   "is_16x9": abs(aspect - 16/9) < 0.05})
    log(f"PNG {w}x{h} aspect={aspect} (16:9={16/9:.4f}) -> is_16x9={result['is_16x9']}")
    result["PASS"] = result["is_16x9"]
    result["total_seconds"] = round(time.time() - t0, 1)
except Exception as e:  # noqa: BLE001
    result["exception"] = f"{type(e).__name__}: {e}"; result["traceback"] = traceback.format_exc()
    log("EXCEPTION", result["exception"]); log(result["traceback"])

out = Path(__file__).resolve().with_name("task2_16x9_live_proof_result.json")
out.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
log("PASS=", result.get("PASS"))
