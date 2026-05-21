"""Automated style bible brand compliance checking.

Loads brand markers from the master style bible and scans artifact content
for compliance. Returns structured JSON with per-dimension scores.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

DEFAULT_BRAND_MARKERS = {
    "colors": {
        "JCPH_Navy": "#1e3a5f",
        "Medical_Teal": "#4a90a4",
        "Clean_White": "#ffffff",
    },
    "fonts": {
        "headlines": "Montserrat",
        "body": "Source Sans Pro",
    },
}


def extract_brand_markers(style_bible_path: Path) -> dict:
    """Extract brand markers from the master style bible.

    Args:
        style_bible_path: Path to master-style-bible.md.

    Returns:
        Dict with colors and fonts extracted from the style bible.
    """
    if not style_bible_path.exists():
        return DEFAULT_BRAND_MARKERS

    content = style_bible_path.read_text(encoding="utf-8")
    markers = {"colors": {}, "fonts": {}}

    hex_pattern = re.compile(r'hex:\s*"(#[0-9a-fA-F]{6})"')
    for match in hex_pattern.finditer(content):
        hex_val = match.group(1).lower()
        context_start = max(0, match.start() - 100)
        context = content[context_start:match.start()]
        name_match = re.search(r'(\w[\w_]+):', context)
        if name_match:
            markers["colors"][name_match.group(1)] = hex_val

    if not markers["colors"]:
        markers["colors"] = DEFAULT_BRAND_MARKERS["colors"]

    if "Montserrat" in content:
        markers["fonts"]["headlines"] = "Montserrat"
    if "Source Sans Pro" in content:
        markers["fonts"]["body"] = "Source Sans Pro"

    if not markers["fonts"]:
        markers["fonts"] = DEFAULT_BRAND_MARKERS["fonts"]

    return markers


def check_color_compliance(content: str, brand_colors: dict[str, str]) -> list[dict]:
    """Check artifact content for non-palette color references."""
    findings = []
    hex_pattern = re.compile(r'#[0-9a-fA-F]{6}')
    palette_values = {v.lower() for v in brand_colors.values()}

    for match in hex_pattern.finditer(content):
        hex_val = match.group(0).lower()
        if hex_val not in palette_values:
            line_num = content[:match.start()].count('\n') + 1
            findings.append({
                "severity": "medium",
                "dimension": "brand_color",
                "location": f"Line {line_num}",
                "description": f"Non-palette color {hex_val} detected",
                "fix_suggestion": f"Replace with a palette color: {', '.join(f'{k}={v}' for k, v in brand_colors.items())}",
            })
    return findings


def check_font_compliance(content: str, brand_fonts: dict[str, str]) -> list[dict]:
    """Check artifact for non-brand font references."""
    findings = []
    font_pattern = re.compile(r'(?:font|typeface|typography)[:\s]+["\']?(\w[\w\s]+)', re.IGNORECASE)
    brand_font_names = {v.lower() for v in brand_fonts.values()}

    for match in font_pattern.finditer(content):
        font_name = match.group(1).strip().lower()
        if font_name and font_name not in brand_font_names:
            line_num = content[:match.start()].count('\n') + 1
            findings.append({
                "severity": "medium",
                "dimension": "brand_typography",
                "location": f"Line {line_num}",
                "description": f"Non-brand font reference: '{match.group(1).strip()}'",
                "fix_suggestion": f"Use brand fonts: {', '.join(f'{k}={v}' for k, v in brand_fonts.items())}",
            })
    return findings


def run_brand_validation(
    content: str,
    style_bible_path: Path | None = None,
) -> dict:
    """Run brand compliance checks and return structured results.

    Args:
        content: Artifact content to validate.
        style_bible_path: Path to master-style-bible.md. Uses defaults if missing.

    Returns:
        Structured dict with compliance score and findings.
    """
    if style_bible_path and style_bible_path.exists():
        markers = extract_brand_markers(style_bible_path)
    else:
        markers = DEFAULT_BRAND_MARKERS

    findings: list[dict] = []
    findings.extend(check_color_compliance(content, markers["colors"]))
    findings.extend(check_font_compliance(content, markers["fonts"]))

    score = 1.0
    for f in findings:
        if f["severity"] == "critical":
            score -= 0.3
        elif f["severity"] == "high":
            score -= 0.15
        elif f["severity"] == "medium":
            score -= 0.1
        elif f["severity"] == "low":
            score -= 0.02
    score = max(round(score, 2), 0.0)

    return {
        "checker": "brand_validation",
        "status": "pass" if score >= 0.7 else "fail",
        "compliance_score": score,
        "brand_markers_used": markers,
        "findings": findings,
        "summary": {
            "total": len(findings),
            "critical": sum(1 for f in findings if f["severity"] == "critical"),
            "high": sum(1 for f in findings if f["severity"] == "high"),
            "medium": sum(1 for f in findings if f["severity"] == "medium"),
            "low": sum(1 for f in findings if f["severity"] == "low"),
        },
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: brand_validator.py <file_path> [--style-bible PATH]")
        sys.exit(2)

    file_path = Path(sys.argv[1])
    bible_path = None
    if "--style-bible" in sys.argv:
        idx = sys.argv.index("--style-bible")
        bible_path = Path(sys.argv[idx + 1])

    content = file_path.read_text(encoding="utf-8")
    result = run_brand_validation(content, style_bible_path=bible_path)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["status"] == "pass" else 1)
