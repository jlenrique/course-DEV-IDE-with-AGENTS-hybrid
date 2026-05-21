"""Validate that literal-visual slide PNGs occupy the full slide area.

Checks for large empty borders or unfilled regions that indicate the image
did not render at full-bleed.  Returns structured JSON with a pass/fail
result and dimensional scores.

Requires Pillow (``pip install Pillow``).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None  # type: ignore[assignment,misc]


# Percentage of edge pixels that must be non-white to pass.
_FILL_THRESHOLD = 0.90
# Luminance above which a pixel is considered "empty/white".
_WHITE_LUMINANCE = 245
# Minimum per-channel standard deviation to consider a slide "not blank".
# Blank slides ~0, faded ~12, real content >25.  Validated against harness
# results 2026-04-05 across 17 test PNGs.
_MIN_CONTENT_STDDEV = 25.0
# Faded images fall between blank and real content.
_FADED_STDDEV_CEIL = 25.0


def _edge_fill_ratio(img: Image.Image, band_px: int = 8) -> dict[str, float]:
    """Measure the ratio of non-white pixels along each edge band."""
    rgb = img.convert("RGB")
    width, height = rgb.size
    pixels = rgb.load()

    def _scan_band(coords: list[tuple[int, int]]) -> float:
        if not coords:
            return 1.0
        filled = 0
        for x, y in coords:
            r, g, b = pixels[x, y]
            luminance = 0.299 * r + 0.587 * g + 0.114 * b
            if luminance < _WHITE_LUMINANCE:
                filled += 1
        return filled / len(coords)

    top = [(x, y) for y in range(min(band_px, height)) for x in range(width)]
    bottom = [(x, y) for y in range(max(0, height - band_px), height) for x in range(width)]
    left = [(x, y) for x in range(min(band_px, width)) for y in range(height)]
    right = [(x, y) for x in range(max(0, width - band_px), width) for y in range(height)]

    return {
        "top": round(_scan_band(top), 4),
        "bottom": round(_scan_band(bottom), 4),
        "left": round(_scan_band(left), 4),
        "right": round(_scan_band(right), 4),
    }


def _content_stddev(img: Image.Image) -> float:
    """Average per-channel standard deviation — measures image content level.

    Returns ~0 for blank/white slides, ~12 for faded, >25 for real content.
    """
    from PIL import ImageStat

    stat = ImageStat.Stat(img.convert("RGB"))
    return sum(stat.stddev) / 3


def validate_visual_fill(
    png_path: str | Path,
    *,
    threshold: float = _FILL_THRESHOLD,
    band_px: int = 8,
) -> dict[str, Any]:
    """Check whether a PNG fills the full slide area.

    Uses two complementary signals:

    1. **Edge-band sampling** — detects blank borders (original check).
    2. **Content variance** — detects blank or faded slides even when the
       source image has light-colored edge content that fools the edge
       check.  A slide with stddev > ``_MIN_CONTENT_STDDEV`` contains
       real content; below ``_FADED_STDDEV_CEIL`` the image is faded
       or blank.

    A slide passes if it has sufficient content variance AND either passes
    the edge-band check or has content variance well above the faded
    threshold (indicating full-opacity content that happens to have
    light-colored edges).

    Args:
        png_path: Path to the exported slide PNG.
        threshold: Minimum fill ratio per edge (0.0–1.0).
        band_px: Pixel width of edge band to sample.

    Returns:
        Structured result with pass/fail, edge ratios, and overall score.
    """
    path = Path(png_path)
    if Image is None:
        return {
            "passed": False,
            "error": "Pillow not installed — cannot perform visual fill validation.",
            "png_path": str(path),
        }

    if not path.is_file():
        return {
            "passed": False,
            "error": f"File not found: {path}",
            "png_path": str(path),
        }

    img = Image.open(path)
    edges = _edge_fill_ratio(img, band_px=band_px)
    overall = round(min(edges.values()), 4)
    edges_pass = all(v >= threshold for v in edges.values())

    stddev = round(_content_stddev(img), 2)
    has_content = stddev >= _MIN_CONTENT_STDDEV
    is_faded = stddev < _FADED_STDDEV_CEIL

    # Pass conditions:
    # 1. Edges pass AND has real content (classic full-bleed)
    # 2. Has strong content variance even if edges are light-colored
    #    (handles images with inherently light edges, e.g. infographics)
    passed = has_content and (edges_pass or stddev > 40.0)

    failures = []
    if not has_content:
        if stddev < 5.0:
            failures.append(f"blank slide (stddev {stddev:.1f} < {_MIN_CONTENT_STDDEV})")
        else:
            failures.append(f"faded/degraded (stddev {stddev:.1f} < {_MIN_CONTENT_STDDEV})")
    if not edges_pass and not (stddev > 40.0):
        failures.extend(
            f"{edge} edge fill {ratio:.1%} < {threshold:.0%}"
            for edge, ratio in edges.items()
            if ratio < threshold
        )

    return {
        "passed": passed,
        "png_path": str(path),
        "dimensions": {"width": img.size[0], "height": img.size[1]},
        "edge_fill_ratios": edges,
        "overall_fill": overall,
        "content_stddev": stddev,
        "threshold": threshold,
        "failures": failures,
    }


def validate_literal_visual_slides(
    slide_output: list[dict[str, Any]],
    *,
    threshold: float = _FILL_THRESHOLD,
    preintegration_sources: dict[int, str | Path] | None = None,
) -> dict[str, Any]:
    """Validate all literal-visual slides in a gary_slide_output list.

    Args:
        slide_output: The ``gary_slide_output`` list from dispatch results.
        threshold: Minimum fill ratio per edge.
        preintegration_sources: Optional mapping of card_number → source PNG
            path.  Retained for interface compatibility but no longer used
            for byte-match validation since all literal-visual slides are
            now Gamma-rendered.  Edge-band sampling is always applied.

    Returns:
        Aggregate result with per-slide details and overall pass/fail.
    """
    lv_slides = [
        s for s in slide_output if s.get("fidelity") == "literal-visual"
    ]
    if not lv_slides:
        return {"passed": True, "checked": 0, "details": []}

    details = []
    all_passed = True
    for slide in lv_slides:
        card_number = slide.get("card_number")
        file_path = slide.get("file_path", "")

        # All literal-visual slides use edge-band sampling (Gamma-rendered).
        result = validate_visual_fill(file_path, threshold=threshold)
        result["card_number"] = card_number
        result["slide_id"] = slide.get("slide_id")
        result["validation_mode"] = "edge-band-sampling"
        details.append(result)
        if not result["passed"]:
            all_passed = False

    return {
        "passed": all_passed,
        "checked": len(details),
        "details": details,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: visual_fill_validator.py <png_path> [threshold]")
        sys.exit(1)
    target = sys.argv[1]
    thresh = float(sys.argv[2]) if len(sys.argv) > 2 else _FILL_THRESHOLD
    result = validate_visual_fill(target, threshold=thresh)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["passed"] else 1)
