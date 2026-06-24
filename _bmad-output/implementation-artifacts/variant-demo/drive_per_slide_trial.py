"""Drive a paused trial to completion, clicking the REAL gh-pages chooser at G2B via Playwright.

Usage: python drive_per_slide_trial.py <trial_id> <picks>
  <picks> = comma list of A/B per slide in slide order, e.g. A,B,A,B,A,B
The trial must already be started (paused at G1). Approves every gate except G2B, where it
opens the published chooser URL, clicks each slide's pick, copies the selection code, parses
it to a per-slide map, and submits it as the G2B `select` verdict.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from uuid import UUID

from dotenv import load_dotenv

load_dotenv()

from app.gates.verdict import OperatorVerdict  # noqa: E402
from app.marcus.orchestrator.production_runner import resume_production_trial  # noqa: E402
from app.marcus.orchestrator.slide_variant_selection import parse_selection_code  # noqa: E402
from app.runtime.economics import RUNS_ROOT  # noqa: E402


def _click_chooser(url: str, picks: list[str]) -> str:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="load", timeout=60000)
        page.wait_for_selector('.variant-card[data-slide="1"]', timeout=60000)
        for idx, variant in enumerate(picks, start=1):
            sel = f'.variant-card[data-slide="{idx}"][data-variant="{variant}"]'
            page.click(sel)
            print(f"   clicked slide {idx} -> {variant}", flush=True)
        page.click("#copy-selections")
        code = page.inner_text("#selection-code").strip()
        browser.close()
    return code


def _click_with_retry(url: str, picks: list[str]) -> str:
    last = None
    for attempt in range(1, 25):  # gh-pages CDN can take a couple minutes to go live
        try:
            code = _click_chooser(url, picks)
            if code:
                return code
        except Exception as exc:  # noqa: BLE001
            last = exc
            print(f"   chooser not ready (attempt {attempt}): {str(exc)[:90]}", flush=True)
            time.sleep(12)
    raise RuntimeError(f"chooser never became clickable: {last}")


def main() -> int:
    trial_id = UUID(sys.argv[1])
    picks = [p.strip().upper() for p in sys.argv[2].split(",") if p.strip()]
    runs_root = RUNS_ROOT
    run_dir = runs_root / str(trial_id)
    print(f"DRIVE trial {trial_id} picks={picks}", flush=True)

    for _ in range(40):
        run = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
        status, gate = run.get("status"), run.get("paused_gate")
        print(f"STATE: status={status} gate={gate} err={run.get('paused_error_tag')}", flush=True)
        if status == "completed":
            print("RUN COMPLETED - all assets delivered (Descript-ready).", flush=True)
            return 0
        if status == "paused-at-error":
            print(f"RUN ERROR-PAUSED: {run.get('paused_error_tag')}", flush=True)
            return 2
        if status != "paused-at-gate" or not gate:
            print(f"UNEXPECTED STATE: {status}", flush=True)
            return 3

        card = json.loads((run_dir / f"decision-card-{gate}.json").read_text(encoding="utf-8"))
        kwargs = {
            "trial_id": trial_id,
            "gate_id": gate,
            "card_id": UUID(card["card"]["card_id"]),
            "operator_id": "operator_juan",
            "decision_card_digest": card["digest"],
            "verb": "approve",
        }
        if gate == "G2B":
            chooser = json.loads(
                (run_dir / "chooser-publish-G2B.json").read_text(encoding="utf-8")
            )
            url = chooser["publish_url"]
            print(f"   G2B chooser URL: {url}", flush=True)
            code = _click_with_retry(url, picks)
            print(f"   SELECTION CODE (from real button clicks): {code}", flush=True)
            opts = [
                e
                for e in card["card"].get("pick_context", [])
                if e.get("kind") == "variant-options"
            ]
            slide_ids = sorted(s["slide_id"] for s in opts[0]["slides"])
            selections = parse_selection_code(code, slide_ids)
            print(f"   PER-SLIDE SELECTIONS: {selections}", flush=True)
            kwargs["verb"] = "select"
            kwargs["edit_payload"] = {"slide_variant_selections": selections}

        env = resume_production_trial(
            trial_id=trial_id,
            verdict=OperatorVerdict(**kwargs),
            runs_root=runs_root,
            max_specialist_calls=30,
        )
        print(f"   -> {env.status}, next: {env.paused_gate}", flush=True)
    print("DRIVE loop exhausted without completion", flush=True)
    return 4


if __name__ == "__main__":
    raise SystemExit(main())
