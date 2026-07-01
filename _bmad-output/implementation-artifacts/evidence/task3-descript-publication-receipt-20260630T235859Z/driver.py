"""TASK 3 live proof — Descript publication-receipt on REAL durable composition + fail-loud branch.

Real GET on the assembled Part-1 project (no credits) → feed the real composition.duration
through build_publication_receipt → published receipt within 1s of expected. Then prove the
detachment case (duration 0) FAILS LOUD. NO MOCKS. first-run-stands.
"""
from __future__ import annotations
import json, os, time, traceback
from pathlib import Path

REPO = Path(r"C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS-hybrid")
os.environ.pop("OPENAI_API_KEY", None)
from dotenv import load_dotenv
load_dotenv(REPO / ".env", override=True)
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

def log(*a):
    print(f"[{time.strftime('%H:%M:%S')}]", *a, flush=True)

from scripts.api_clients.descript_client import DescriptClient
from scripts.operator.descript_publication_receipt import (
    DescriptPublicationError, build_publication_receipt,
)

PROJECT = "d4c69938-751c-458f-be93-036874eaa81b"
COMPOSITION = "e4a0d038-f16a-424b-a39c-51ea62b1ba75"
EXPECTED = 486.034  # enrique-synthesis-receipt.json::attestation.total_audio_duration_seconds

result, t0 = {}, time.time()
try:
    # 1) REAL get_project on the durable assembled composition
    log("get_project (real Descript GET) ...")
    proj = DescriptClient().get_project(PROJECT)
    comps = proj.get("compositions", [])
    actual = comps[0].get("duration") if comps else None
    log("real composition duration =", actual)
    result["real_duration"] = actual

    # 2) REAL duration through the helper -> published receipt
    receipt = build_publication_receipt(
        project_id=PROJECT, composition_id=COMPOSITION,
        composition_duration_s=actual, expected_audio_total_s=EXPECTED,
    )
    log("PUBLISHED receipt:", json.dumps(receipt, default=str)[:400])
    result["receipt"] = receipt
    published_ok = (receipt.get("published") is True
                    and receipt.get("duration_within_1s") is True
                    and abs(receipt.get("duration_delta_s", 9) ) <= 1.0)

    # 3) fail-loud branch: detachment (duration 0) -> raises
    raised_zero = False
    try:
        build_publication_receipt(project_id=PROJECT, composition_id=COMPOSITION,
                                  composition_duration_s=0, expected_audio_total_s=EXPECTED)
    except DescriptPublicationError as e:
        raised_zero = True; log("fail-loud(duration=0) raised:", str(e)[:160])
    # 4) fail-loud branch: drift > tolerance -> raises
    raised_drift = False
    try:
        build_publication_receipt(project_id=PROJECT, composition_id=COMPOSITION,
                                  composition_duration_s=100.0, expected_audio_total_s=EXPECTED)
    except DescriptPublicationError as e:
        raised_drift = True; log("fail-loud(drift) raised:", str(e)[:160])

    result.update({"published_ok": published_ok, "raised_on_zero": raised_zero,
                   "raised_on_drift": raised_drift})
    result["PASS"] = bool(published_ok and raised_zero and raised_drift)
    result["total_seconds"] = round(time.time() - t0, 1)
except Exception as e:  # noqa: BLE001
    result["exception"] = f"{type(e).__name__}: {e}"; result["traceback"] = traceback.format_exc()
    log("EXCEPTION", result["exception"]); log(result["traceback"])

Path(__file__).resolve().with_name("task3_descript_receipt_live_proof_result.json").write_text(
    json.dumps(result, indent=2, default=str), encoding="utf-8")
log("PASS=", result.get("PASS"))
