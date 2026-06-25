"""Gamma Studio spike — heartbeat harness (standalone, zero app coupling).

PURPOSE (party-green-lit 2026-06-25): de-risk the single biggest unknown for the
`production_mode: studio` B-variant feature — can we drive gamma.app's Generate UI
to a **Studio** card-design export via Playwright, and (SC-7a) **where does the card
title live in that export** (extractable text/metadata vs. rasterized pixels)? The
answer decides whether the integration reuses the by-title materializer (Amelia) or
needs positional matching (Winston).

This is the FIRST slice of the eventual standalone `gamma_studio_client.py`. It is
deliberately decoupled from the app: it only drives a browser and characterizes the
export. The contract round-trip (running the real `materialize_exported_slide_paths_
by_title` against the captured export) is a SEPARATE dev-runnable step against the
frozen fixture this script produces — keep that separation (Murat: freeze the real
artifact once; test mapping deterministically).

DESIGN (Murat's rules): role/text locators (not CSS/XPath), assert-state-not-sleep,
screenshot every step + on failure, first-run-stands. AUTO-WITH-MANUAL-FALLBACK:
each brittle UI step is attempted; on miss it screenshots, explains, and lets the
operator complete that step by hand in the visible browser, then continue. So the
first run always makes progress and harvests the real DOM for selector refinement.

AUTH: persistent browser context — you log into gamma.app ONCE in the headed window;
the session is reused on later runs. No credentials in code (mirrors
scripts/operator/scite_oauth_login_auto.py). The profile dir holds your session, so
it lives under secrets/ (gitignored).

PREREQS (operator, one-time):
    pip install playwright
    playwright install chromium

RUN (headed, 1 card heartbeat):
    python scripts/ui_clients/gamma_studio_spike.py --cards 1

Escalate later: --cards 3  (then 10) once the heartbeat is green.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# The Studio-B recipe, read off the operator's 2026-06-23 config screenshot
# (resources/Gamma-visuals/Variant B with STUDIO look-feel configuration ...png).
# For the 1-card heartbeat the ONLY must-have is card-design = Studio; the rest is
# best-effort (skip-with-note if a control isn't found).
STUDIO_B_RECIPE = {
    "text_mode": "Generate",
    "amount": "Minimal text",
    "write_for": "Faculty and instructional designers familiar with Canvas and course design, American English",
    "tone": "Clear, professional, engaging in American English",
    "output_language": "English (US)",
    "theme": "2026 HIL APC",
    "image_source": "AI images",
    "image_model": "Auto-select",
    "image_art_style": "Illustration",
    "keywords": ["minimalist", "bold", "flat", "geometric"],
    "format": "Presentation",
    "format_substyle": "Traditional",
    "card_design_mode": "Studio",  # <-- THE feature-defining lever
}

# A tiny single-card brief for the heartbeat (health-sciences, Tejal-adjacent).
DEFAULT_BRIEF = """\
The Innovator's Mindset

What separates a constrained system-follower from an innovator. On the left,
a clinician boxed in by SYSTEM RULES, PROCEDURES, and LIMITS. On the right,
an innovator pulling threads of CREATIVITY, FREEDOM, and GROWTH toward a NEW SYSTEM.
"""


def log(msg: str) -> None:
    print(f"[studio-spike] {msg}", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser(prog="gamma_studio_spike")
    ap.add_argument("--cards", type=int, default=1, help="number of cards to request (heartbeat: 1)")
    ap.add_argument("--brief", type=Path, default=None, help="path to a slide-brief text file (default: built-in 1-card brief)")
    ap.add_argument("--start-url", default="https://gamma.app/create", help="gamma.app entry URL")
    ap.add_argument("--profile-dir", type=Path, default=REPO_ROOT / "secrets" / "gamma_studio_profile",
                    help="persistent browser context dir (holds your login session; gitignored)")
    ap.add_argument("--out", type=Path, default=REPO_ROOT / "runs" / "gamma-studio-spike",
                    help="spike report + frozen-fixture output dir")
    ap.add_argument("--headless", action="store_true", help="(NOT recommended; gamma bot-check needs headed)")
    args = ap.parse_args()

    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
    except ImportError:
        log("Playwright not installed. Run:  pip install playwright  &&  playwright install chromium")
        return 2

    brief = args.brief.read_text(encoding="utf-8") if args.brief else DEFAULT_BRIEF
    args.profile_dir.mkdir(parents=True, exist_ok=True)
    args.out.mkdir(parents=True, exist_ok=True)
    shots = args.out / "screenshots"
    shots.mkdir(exist_ok=True)
    fixture = args.out / "export-fixture"
    fixture.mkdir(exist_ok=True)

    findings: dict = {"cards_requested": args.cards, "recipe": STUDIO_B_RECIPE, "steps": []}
    step_n = [0]

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(args.profile_dir),
            headless=args.headless,
            accept_downloads=True,
            args=["--start-maximized"],
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        def shot(name: str) -> str:
            step_n[0] += 1
            path = shots / f"{step_n[0]:02d}-{name}.png"
            try:
                page.screenshot(path=str(path), full_page=False)
            except Exception as e:  # noqa: BLE001
                log(f"(screenshot failed: {e})")
            return str(path.relative_to(args.out))

        def step(name: str, instruction: str, auto=None) -> None:
            """Attempt `auto()`; on failure/None, fall back to operator-manual.

            `auto` is a zero-arg callable that performs the step via Playwright and
            returns truthy on success, or raises / returns falsy to trigger fallback.
            """
            log(f"STEP: {name}")
            ok, mode, err = False, "manual", None
            if auto is not None:
                try:
                    ok = bool(auto())
                    mode = "auto" if ok else "manual"
                except Exception as e:  # noqa: BLE001
                    err = repr(e)
                    log(f"  auto attempt failed: {err}")
            if not ok:
                shot(f"{name}-before-manual")
                print(f"\n  >>> MANUAL: {instruction}")
                print("      Do it in the visible browser window, then press Enter here (or type 's' to skip)...")
                resp = input("      > ").strip().lower()
                mode = "skipped" if resp == "s" else "manual"
            findings["steps"].append({"name": name, "mode": mode, "error": err, "screenshot": shot(name)})

        # --- SC-1: authenticated, controllable browser -------------------------
        log(f"Opening {args.start_url} (persistent profile: {args.profile_dir})")
        try:
            page.goto(args.start_url, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:  # noqa: BLE001
            log(f"navigation issue (continue manually): {e}")
        step(
            "login",
            "If not already signed in, log into gamma.app now (your session will be reused next time).",
            auto=lambda: page.get_by_role("button", name="Create new").is_visible(timeout=8000)
            or page.get_by_text("Create new", exact=False).first.is_visible(timeout=4000),
        )

        # --- SC-2: start a Generate / Freeform doc + paste the brief -----------
        step(
            "open-generate-freeform",
            "Start a new Generate flow and choose 'Paste in text' / Freeform (the Prompt editor with a text box).",
        )
        step(
            "paste-brief",
            f"Paste this {args.cards}-card brief into the Freeform text area:\n\n{brief}\n",
        )

        # --- SC-3: the recipe — Studio is the must-have ------------------------
        step(
            "set-recipe",
            ("Set the left Settings to the recipe (best-effort): "
             f"Text={STUDIO_B_RECIPE['text_mode']}/{STUDIO_B_RECIPE['amount']}; "
             f"Theme={STUDIO_B_RECIPE['theme']}; Art style={STUDIO_B_RECIPE['image_art_style']}; "
             f"keywords={STUDIO_B_RECIPE['keywords']}; Format={STUDIO_B_RECIPE['format']}/{STUDIO_B_RECIPE['format_substyle']}."),
        )
        step(
            "set-card-design-STUDIO",
            "CRITICAL: in Format → Card design mode, select **Studio** (not Classic). Confirm it is selected.",
            auto=lambda: (page.get_by_text("Studio", exact=True).first.click(timeout=8000) or True),
        )
        step(
            "set-card-count",
            f"Set the card count to {args.cards}.",
        )

        # --- SC-4/5: generate + export ----------------------------------------
        step(
            "generate",
            "Click Generate and wait for generation to fully complete.",
            auto=lambda: (page.get_by_role("button", name="Generate").first.click(timeout=8000) or True),
        )
        print("\n  >>> When generation is COMPLETE, press Enter to continue to export...")
        input("      > ")
        shot("post-generate")

        step(
            "export-png",
            "Export the deck as PNG (Share/Export → PNG). Save it where you can find it.",
        )

        # --- SC-5/7a: capture + characterize the export -----------------------
        print("\n  >>> Enter the full path to the exported file(s) — a PNG, a folder, or a ZIP/PDF:")
        export_in = input("      > ").strip().strip('"')
        src = Path(export_in) if export_in else None
        captured = []
        if src and src.exists():
            if src.is_dir():
                for f in src.iterdir():
                    if f.is_file():
                        dst = fixture / f.name
                        shutil.copy2(f, dst)
                        captured.append(f.name)
            else:
                dst = fixture / src.name
                shutil.copy2(src, dst)
                captured.append(src.name)
            log(f"Captured {len(captured)} file(s) into frozen fixture: {fixture}")
        else:
            log("No export path captured — you can copy the export into the fixture dir manually.")

        # SC-7a characterization: what is each captured artifact, and does it carry
        # a title TEXT layer (decides title-matching vs positional).
        sc7a = []
        for name in captured:
            f = fixture / name
            ext = f.suffix.lower()
            entry = {"file": name, "ext": ext, "bytes": f.stat().st_size, "title_text_layer": "unknown"}
            if ext == ".pdf":
                entry["note"] = "PDF — check for an embedded text layer (titles extractable) vs image-only pages."
            elif ext in {".png", ".jpg", ".jpeg"}:
                entry["title_text_layer"] = "NO (raster image — title is pixels)"
                entry["note"] = "Single rasterized image — title not extractable as text → favors POSITIONAL matching."
            captured_titles = entry
            sc7a.append(captured_titles)
        findings["sc7a_export_characterization"] = sc7a
        findings["captured_files"] = captured

        report = args.out / "spike-findings.json"
        report.write_text(json.dumps(findings, indent=2), encoding="utf-8")
        log(f"Wrote findings: {report}")
        log("SC-7a (where the title lives) is the headline result — see sc7a_export_characterization.")

        print("\n  >>> Heartbeat complete. Press Enter to close the browser...")
        input("      > ")
        ctx.close()

    log("Done. Report back: the screenshots/ dir, spike-findings.json, and whether the exported card")
    log("is single-image-with-embedded-text (SC-6) matching resources/Gamma-visuals/ goldens.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
