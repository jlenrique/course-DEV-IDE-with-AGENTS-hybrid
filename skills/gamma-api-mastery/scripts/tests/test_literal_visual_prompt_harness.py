"""Live API prompt experiment for literal-visual slide reliability.

Runs three candidate prompts (plus the current prompt and a baseline) against
the Gamma ``/generations/from-template`` endpoint using template
``g_gior6s13mvpk8ms`` with ``imageOptions.source: noImages``.

Each test case:
1. Calls the template endpoint with one prompt variant.
2. Waits for generation to complete.
3. Downloads the exported PNG.
4. Runs ``validate_visual_fill()`` on the PNG.
5. Saves the PNG and a per-run markdown summary to a timestamped output dir.

Usage::

    pytest test_literal_visual_prompt_harness.py --run-live-e2e -v -s

All tests require ``GAMMA_API_KEY`` in the environment and internet access.
Each test consumes Gamma credits (expect ~1-3 credits per call).

Reference: https://developers.gamma.app/llms-full.txt
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
import requests

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
_SCRIPTS_DIR = Path(__file__).resolve().parents[1]
_QC_SCRIPTS = _PROJECT_ROOT / "skills" / "quality-control" / "scripts"
sys.path.insert(0, str(_PROJECT_ROOT))
sys.path.insert(0, str(_SCRIPTS_DIR))
sys.path.insert(0, str(_QC_SCRIPTS))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(_PROJECT_ROOT / ".env")

from visual_fill_validator import validate_visual_fill  # noqa: E402

from scripts.api_clients.gamma_client import GammaClient  # noqa: E402

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────
TEMPLATE_ID = "g_gior6s13mvpk8ms"
EXPORT_SETTLE_SECONDS = 10

# Production GitHub Pages images — known good, used in real dispatches.
# card-02: large 5.4MB slide image (landscape, 16:9 production export)
# card-09: smaller 1.2MB slide image (landscape, 16:9 production export)
_GITHUB_PAGES_IMAGE_1 = (
    "https://jlenrique.github.io/assets/gamma/"
    "apc-c1m1-tejal-20260403/card-02.png"
)
_GITHUB_PAGES_IMAGE_2 = (
    "https://jlenrique.github.io/assets/gamma/"
    "apc-c1m1-tejal-20260403/card-09.png"
)
# Generic test image for variety
_HTTPBIN_IMAGE = "https://httpbin.org/image/png"

# Rotate images across prompt variants for broader coverage
TEST_IMAGES = [_GITHUB_PAGES_IMAGE_1, _GITHUB_PAGES_IMAGE_2, _HTTPBIN_IMAGE]

# Output directory for human review
_HARNESS_OUTPUT_DIR = (
    _PROJECT_ROOT / "tests" / "prompt-harness-results"
)


# ── Prompt Variants ────────────────────────────────────────────

def _current_prompt(url: str) -> str:
    """The prompt currently in production (gamma_operations.py lines 1400-1408)."""
    return (
        "Replace the image in this card with the image at the "
        "following URL. Keep the image card layout — the image "
        "must fill the entire slide with no text overlay.\n"
        f"{url}\n"
        "\n"
        "Title: PROMPT-HARNESS Slide 01"
    )


def _prompt_a(url: str) -> str:
    """Prompt A: direct replacement instruction, full-screen foreground."""
    return (
        "Replace the image in this card with the image at the "
        "following URL. The image must fill the entire slide as a "
        "full-screen foreground element. No text overlay.\n"
        f"{url}"
    )


def _prompt_b(url: str) -> str:
    """Prompt B: display-only instruction, edge-to-edge, no extras."""
    return (
        "Display only this image, filling the entire card edge-to-edge. "
        "No text, no accents, no decorative elements.\n"
        f"{url}"
    )


def _prompt_c(url: str) -> str:
    """Prompt C: sole visual, stretched, no title."""
    return (
        "Use this image stretched edge-to-edge as the sole visual. "
        "No title, no text, no additional imagery.\n"
        f"{url}"
    )


PROMPT_VARIANTS: dict[str, Any] = {
    "current_gh1": {
        "builder": _current_prompt,
        "image_url": _GITHUB_PAGES_IMAGE_1,
        "description": "Current production prompt + GitHub Pages card-02 (5.4MB)",
    },
    "current_gh2": {
        "builder": _current_prompt,
        "image_url": _GITHUB_PAGES_IMAGE_2,
        "description": "Current production prompt + GitHub Pages card-09 (1.2MB)",
    },
    "prompt_a_gh1": {
        "builder": _prompt_a,
        "image_url": _GITHUB_PAGES_IMAGE_1,
        "description": "Full-screen foreground + GitHub Pages card-02",
    },
    "prompt_b_gh2": {
        "builder": _prompt_b,
        "image_url": _GITHUB_PAGES_IMAGE_2,
        "description": "Display-only edge-to-edge + GitHub Pages card-09",
    },
    "prompt_c_gh1": {
        "builder": _prompt_c,
        "image_url": _GITHUB_PAGES_IMAGE_1,
        "description": "Sole visual stretched + GitHub Pages card-02",
    },
    "prompt_a_httpbin": {
        "builder": _prompt_a,
        "image_url": _HTTPBIN_IMAGE,
        "description": "Full-screen foreground + httpbin test image",
    },
}


# ── Helpers ────────────────────────────────────────────────────

def _ensure_output_dir() -> Path:
    """Create timestamped output directory for this harness run."""
    timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    out = _HARNESS_OUTPUT_DIR / f"run-{timestamp}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def _download_export(export_url: str, dest: Path) -> None:
    """Download a Gamma export file to local path."""
    resp = requests.get(export_url, timeout=60)
    resp.raise_for_status()
    dest.write_bytes(resp.content)
    logger.info("Downloaded export to %s (%d bytes)", dest.name, len(resp.content))


def _run_template_generation(
    client: GammaClient,
    prompt: str,
) -> dict[str, Any]:
    """Run a single template generation and wait for completion."""
    # NOTE: template endpoint rejects imageOptions.source (400 validated 2026-04-05).
    # Template g_gior6s13mvpk8ms uses image source: placeholder.
    # The prompt is the only lever for image placement on template calls.
    result = client.generate_from_template(
        gamma_id=TEMPLATE_ID,
        prompt=prompt,
        export_as="png",
    )
    gen_id = result.get("generationId") or result.get("id", "")
    logger.info("Generation started: %s", gen_id)

    completed = client.wait_for_generation(gen_id)
    return completed


def _write_summary(output_dir: Path, results: list[dict[str, Any]]) -> Path:
    """Write a markdown summary of all prompt results."""
    summary_path = output_dir / "SUMMARY.md"
    lines = [
        "# Literal-Visual Prompt Harness Results\n",
        f"**Template:** `{TEMPLATE_ID}` (image source: placeholder)\n",
        "**imageOptions:** not sent (template endpoint rejects source param)\n",
        f"**Run time:** {datetime.now(UTC).isoformat()}\n",
        "**API reference:** https://developers.gamma.app/llms-full.txt\n",
        "",
        "| Variant | Image | Fill Valid | Gen Time (s) | Credits | File |",
        "|---------|-------|-----------|-------------|---------|------|",
    ]
    for r in results:
        fill_icon = "PASS" if r["fill_passed"] else "FAIL"
        img_short = r.get("image_url", "?").split("/")[-1]
        lines.append(
            f"| {r['variant']} | {img_short} | {fill_icon} | {r['gen_time_s']:.1f} "
            f"| {r.get('credits_used', '?')} | {r['filename']} |"
        )
    lines.extend([
        "",
        "## Prompt Text Used\n",
    ])
    for r in results:
        lines.append(f"### {r['variant']}\n")
        lines.append(f"**Description:** {r['description']}\n")
        lines.append("```")
        lines.append(r["prompt_text"])
        lines.append("```\n")
        if r.get("fill_details"):
            lines.append(f"**Fill validation details:** `{json.dumps(r['fill_details'])}`\n")

    summary_path.write_text("\n".join(lines), encoding="utf-8")
    return summary_path


# ── Shared state for collecting results across tests ───────────
_harness_results: list[dict[str, Any]] = []
_harness_output_dir: Path | None = None


# ── Fixtures ───────────────────────────────────────────────────

@pytest.fixture(scope="module")
def gamma_client() -> GammaClient:
    api_key = os.environ.get("GAMMA_API_KEY", "")
    if not api_key:
        pytest.skip("GAMMA_API_KEY not set")
    return GammaClient(api_key=api_key)


@pytest.fixture(scope="module")
def output_dir() -> Path:
    global _harness_output_dir
    if _harness_output_dir is None:
        _harness_output_dir = _ensure_output_dir()
    return _harness_output_dir


# ── Test Cases ─────────────────────────────────────────────────

@pytest.mark.live_api_e2e
class TestLiteralVisualPromptHarness:
    """Run each prompt variant against the live Gamma API."""

    @pytest.mark.parametrize(
        "variant_key",
        list(PROMPT_VARIANTS.keys()),
        ids=list(PROMPT_VARIANTS.keys()),
    )
    def test_prompt_variant(
        self,
        variant_key: str,
        gamma_client: GammaClient,
        output_dir: Path,
    ) -> None:
        variant = PROMPT_VARIANTS[variant_key]
        image_url = variant["image_url"]
        prompt_text = variant["builder"](image_url)

        logger.info("=== Running variant: %s ===", variant_key)
        logger.info("Prompt:\n%s", prompt_text)

        start = time.monotonic()
        completed = _run_template_generation(gamma_client, prompt_text)
        gen_time = time.monotonic() - start

        # Wait for export renderer to finish baking
        time.sleep(EXPORT_SETTLE_SECONDS)

        # Download the exported PNG
        export_url = completed.get("exportUrl", "")
        filename = f"{variant_key}.png"
        png_path = output_dir / filename

        if export_url:
            _download_export(export_url, png_path)
        else:
            pytest.fail(f"No exportUrl in completed response for {variant_key}")

        # Validate fill
        fill_result = validate_visual_fill(str(png_path))
        fill_passed = bool(fill_result.get("passed"))

        # Collect credits info
        credits_info = completed.get("credits", {})
        credits_used = credits_info.get("deducted", "?")

        result_record = {
            "variant": variant_key,
            "description": variant["description"],
            "image_url": image_url,
            "prompt_text": prompt_text,
            "fill_passed": fill_passed,
            "fill_details": fill_result,
            "gen_time_s": gen_time,
            "credits_used": credits_used,
            "filename": filename,
            "generation_id": completed.get("generationId", ""),
            "gamma_url": completed.get("gammaUrl", ""),
        }
        _harness_results.append(result_record)

        # Save individual result JSON for debugging
        result_json = output_dir / f"{variant_key}.json"
        result_json.write_text(
            json.dumps(result_record, indent=2, default=str),
            encoding="utf-8",
        )

        logger.info(
            "Variant %s: fill=%s, time=%.1fs, credits=%s",
            variant_key, fill_passed, gen_time, credits_used,
        )

        # The test always passes — we're collecting data, not gating.
        # Human reviews the SUMMARY.md and PNGs to pick the winner.


@pytest.mark.live_api_e2e
def test_write_summary(output_dir: Path) -> None:
    """Write the consolidated summary after all variants complete.

    This test runs last (alphabetically after TestLiteralVisualPromptHarness).
    """
    if not _harness_results:
        pytest.skip("No harness results to summarize")

    summary_path = _write_summary(output_dir, _harness_results)
    assert summary_path.exists()
    logger.info("Summary written to: %s", summary_path)
    print(f"\n{'='*60}")
    print(f"HARNESS SUMMARY: {summary_path}")
    print(f"PNGs saved to:   {output_dir}")
    print(f"{'='*60}\n")
    print(summary_path.read_text(encoding="utf-8"))
