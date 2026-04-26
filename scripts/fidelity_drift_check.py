"""Cumulative fidelity drift checker.

Operational utility invoked by Vera during G3+ gate evaluation to perform
global drift checks against the original source bundle (G0).

Uses resolve_source_ref for provenance chain resolution.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from scripts.resolve_source_ref import (
    resolve_source_ref,  # noqa: F401 — re-exported for Vera's gate evaluation
)


def extract_source_themes(extracted_md_path: str) -> list[dict[str, str]]:
    """Extract major themes (top-level headings) from the source bundle.

    Args:
        extracted_md_path: Path to extracted.md from the source bundle.

    Returns:
        List of dicts with 'heading' and 'content_preview' (first 200 chars).
    """
    path = Path(extracted_md_path)
    if not path.exists():
        return []

    content = path.read_text(encoding="utf-8")
    themes: list[dict[str, str]] = []
    current_heading = None
    current_lines: list[str] = []

    for line in content.split("\n"):
        stripped = line.strip()
        if stripped.startswith("## ") and not stripped.startswith("### "):
            if current_heading:
                body = "\n".join(current_lines).strip()
                themes.append({
                    "heading": current_heading,
                    "content_preview": body[:200],
                })
            current_heading = stripped.lstrip("#").strip()
            current_lines = []
        elif current_heading:
            current_lines.append(line)

    if current_heading:
        body = "\n".join(current_lines).strip()
        themes.append({
            "heading": current_heading,
            "content_preview": body[:200],
        })

    return themes


def check_theme_representation(
    theme_heading: str,
    artifact_text: str,
) -> bool:
    """Check whether a source theme is represented in the output artifact.

    Uses keyword matching: extracts significant words from the theme heading
    and checks if they appear in the artifact text.

    Args:
        theme_heading: The source theme heading (e.g., "Regulatory Compliance Framework").
        artifact_text: The full text of the output artifact being checked.

    Returns:
        True if the theme appears to be represented.
    """
    stop_words = {"the", "a", "an", "and", "or", "of", "in", "to", "for", "is", "are", "was", "were", "on", "at", "by", "with"}
    words = [w.lower() for w in re.findall(r'\w+', theme_heading) if w.lower() not in stop_words and len(w) > 2]

    if not words:
        return True

    artifact_lower = artifact_text.lower()
    matched = sum(1 for w in words if w in artifact_lower)
    return matched / len(words) >= 0.5


def compute_global_drift(
    source_bundle_path: str,
    artifact_text: str,
    gate: str,
    threshold_mode: str = "production",
) -> dict[str, Any]:
    """Compute cumulative fidelity drift for an artifact against the source bundle.

    Args:
        source_bundle_path: Path to extracted.md from G0 source bundle.
        artifact_text: Full text content of the artifact being evaluated.
        gate: Current gate identifier (e.g., "G3").
        threshold_mode: "ad-hoc" | "production" | "regulated".

    Returns:
        Drift assessment dict with score, verdict, and missing themes.
    """
    thresholds = {
        "ad-hoc": {"warning": 0.20, "failure": 0.40},
        "production": {"warning": 0.10, "failure": 0.20},
        "regulated": {"warning": 0.05, "failure": 0.10},
    }

    mode_thresholds = thresholds.get(threshold_mode, thresholds["production"])

    themes = extract_source_themes(source_bundle_path)
    if not themes:
        return {
            "gate": gate,
            "source_bundle": source_bundle_path,
            "total_source_themes": 0,
            "themes_represented": 0,
            "global_fidelity_score": 1.0,
            "drift": 0.0,
            "threshold_mode": threshold_mode,
            "verdict": "pass",
            "missing_themes": [],
        }

    missing: list[dict[str, str]] = []
    represented = 0

    for theme in themes:
        if check_theme_representation(theme["heading"], artifact_text):
            represented += 1
        else:
            missing.append({
                "theme": theme["heading"],
                "source_ref": f"{Path(source_bundle_path).name}#{theme['heading']}",
            })

    total = len(themes)
    score = represented / total if total > 0 else 1.0
    drift_val = 1.0 - score

    if drift_val >= mode_thresholds["failure"]:
        verdict = "failure"
    elif drift_val >= mode_thresholds["warning"]:
        verdict = "warning"
    else:
        verdict = "pass"

    return {
        "gate": gate,
        "source_bundle": source_bundle_path,
        "total_source_themes": total,
        "themes_represented": represented,
        "global_fidelity_score": round(score, 3),
        "drift": round(drift_val, 3),
        "threshold_mode": threshold_mode,
        "threshold_warning": mode_thresholds["warning"],
        "threshold_failure": mode_thresholds["failure"],
        "verdict": verdict,
        "missing_themes": missing,
    }


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 3:
        print(
            "Usage: python fidelity_drift_check.py <source_bundle_extracted_md> "
            "<artifact_file> [gate] [mode]"
        )
        print("  gate: G3, G4, G5 (default: G3)")
        print("  mode: ad-hoc, production, regulated (default: production)")
        sys.exit(1)

    bundle_path = sys.argv[1]
    artifact_path = sys.argv[2]
    gate = sys.argv[3] if len(sys.argv) > 3 else "G3"
    mode = sys.argv[4] if len(sys.argv) > 4 else "production"

    artifact_text = Path(artifact_path).read_text(encoding="utf-8")
    result = compute_global_drift(bundle_path, artifact_text, gate, mode)

    print(json.dumps(result, indent=2))
    sys.exit(0 if result["verdict"] != "failure" else 1)
