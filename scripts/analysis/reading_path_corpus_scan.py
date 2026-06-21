"""Reading-path corpus scan — Phase 2b + first-pass Phase 2c EVIDENCE tool.

This is an ANALYSIS / EVIDENCE script, NOT production substrate. It does NOT
author the patterns catalog, make admission decisions, name new patterns, or
write narration-deltas — that is Phase 3, the orchestrator's job. It produces
DATA the orchestrator consumes:

1. Enumerates the 54 WORKING slides (the 68-slide corpus MINUS the 14 held-out
   from `reading-path-holdout-split-2026-06-21.md`). Hard-excludes the held-out
   by filename and asserts count == 54 (fails loud otherwise). The 14 held-out
   are NEVER perceived, featured, fitted, or clustered here.
2. LIVE-perceives each working slide via the real gpt-5.5 perceiver
   (`app.specialists.vision.provider.perceive_png`). NO mocks/fixtures.
   First-run-stands. A per-slide error is recorded + tagged and the scan
   CONTINUES (never silently skipped, never re-run to "improve" the spread).
3. Captures each raw PerceptionArtifact to JSON with provenance.
4. Computes the content-blind feature vector (design-decisions D4) — derived
   ONLY from the PERCEIVER output, never from the classifier label (two-source
   rule, Murat).
5. FITS each slide to the existing patterns via `classify_reading_path`
   (catch `ReadingPathClassificationError` -> residue) and records the
   position-order scan via `ordered_element_keys_for_reading_path`.
6. FIRST-PASS clusters the RESIDUE ONLY on the feature vector (emits candidate
   groupings — id, members, centroid). Does NOT decide which become patterns.
7. Emits an evidence report markdown.

Run:
    PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe \
        scripts/analysis/reading_path_corpus_scan.py

Reads OPENAI_API_KEY from .env (the adapter reads it from env at invocation).
"""

from __future__ import annotations

import json
import os
import sys
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]

# Ensure the repo root is importable regardless of cwd / invocation (the live
# `app.*` and `scripts.*` packages resolve from here).
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
CORPUS_DIR = Path(r"C:\Users\juanl\OneDrive\Desktop\z-2026-06-21")
OUT_DIR = REPO_ROOT / "_bmad-output" / "implementation-artifacts" / "reading-path-corpus-scan"
PERCEPTIONS_DIR = OUT_DIR / "perceptions"
EVIDENCE_REPORT = OUT_DIR / "evidence-report.md"

# Provenance constant — captured-at is fixed for the whole run (the scan is one
# atomic evidence-production event; first-run-stands).
CAPTURED_AT = datetime.now(timezone.utc).isoformat()
MODEL_ID = "gpt-5.5"

# The 14 HELD-OUT slides (reading-path-holdout-split-2026-06-21.md). These are
# HARD-EXCLUDED by filename and MUST NOT be perceived/featured/fitted/clustered.
HELD_OUT: frozenset[str] = frozenset(
    {
        "1_Diagnosis-Innovation.png",
        "3_Achieving-the-Ideal-State.png",
        "5_Check-Your-Understanding.png",
        "6_All-of-them-belong-to-BOTH.png",
        "8_Decision-Making-Foundations.png",
        "9_Comparing-Expected-Value-and-Expected-Utility.png",
        "11_Value-Creation-in-Innovation.png",
        "13_Effective-Problem-Solving-Approach.png",
        "15_Types-of-Motivation.png",
        "17_Examples-of-Effective-Leadership-in-Public-Health.png",
        "18_The-Future-of-Public-Health-Leadership.png",
        "20_Resources-for-Entrepreneurship-and-Innovation.png",
        "21_Key-Takeaways.png",
        "22_Next-Steps-Your-Path-Forward.png",
    }
)

EXPECTED_WORKING_COUNT = 54

# ---------------------------------------------------------------------------
# .env loading (no python-dotenv installed; minimal parser)
# ---------------------------------------------------------------------------


def _load_dotenv() -> None:
    """Populate os.environ from the repo .env for keys not already set."""
    env_path = REPO_ROOT / ".env"
    if not env_path.is_file():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


# ---------------------------------------------------------------------------
# Feature vector (design-decisions D4) — derived ONLY from perceiver output.
# ---------------------------------------------------------------------------
#
# Two-source rule (Murat): every feature is computed from the raw
# PerceptionArtifact (the independent perceiver), NEVER from the
# classifier-under-test's label.


def _parse_bbox(raw: dict[str, Any]) -> tuple[float, float, float, float] | None:
    """Mirror the classifier's bbox normalization so geometry features align."""
    source = raw.get("bbox") or raw.get("bounds") or raw.get("position")
    try:
        if isinstance(source, dict):
            if {"x", "y", "width", "height"} <= set(source):
                x = float(source["x"])
                y = float(source["y"])
                return (x, y, x + float(source["width"]), y + float(source["height"]))
            keys = ("x1", "y1", "x2", "y2")
            if set(keys) <= set(source):
                return tuple(float(source[k]) for k in keys)  # type: ignore[return-value]
        if isinstance(source, (list, tuple)) and len(source) == 4:
            return tuple(float(item) for item in source)  # type: ignore[return-value]
    except (ValueError, TypeError):
        return None
    return None


def _positioned_elements(artifact_dump: dict[str, Any]) -> list[dict[str, Any]]:
    """Return visual_elements that carry a usable bbox, with derived geometry."""
    out: list[dict[str, Any]] = []
    for raw in artifact_dump.get("visual_elements", []) or []:
        bbox = _parse_bbox(raw)
        if bbox is None:
            continue
        x1, y1, x2, y2 = bbox
        out.append(
            {
                "kind": str(raw.get("kind") or raw.get("type") or "").strip().lower(),
                "text": " ".join(
                    str(raw.get(f) or "")
                    for f in ("label", "text", "title", "name", "description")
                ).strip(),
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "cx": (x1 + x2) / 2,
                "cy": (y1 + y2) / 2,
                "area": max(0.0, (x2 - x1)) * max(0.0, (y2 - y1)),
            }
        )
    return out


def _h_band(cx: float) -> str:
    """Horizontal third: left / center / right."""
    return ("left", "center", "right")[min(2, max(0, int(cx * 3)))]


def _v_band(cy: float) -> str:
    """Vertical third: top / middle / bottom."""
    return ("top", "middle", "bottom")[min(2, max(0, int(cy * 3)))]


def compute_feature_vector(artifact_dump: dict[str, Any]) -> dict[str, Any]:
    """Content-blind feature vector per design-decisions D4.

    Derivation (all from the perceiver, two-source rule):

    - primary_anchor_position: the v-band/h-band of the largest-area element
      (the dominant fixation target). 'none' if no positioned elements.
    - anchor_count: count of positioned visual_elements (real bounding boxes).
    - reading_vector: coarse estimate of eye travel from the spatial spread of
      element centers — 'diagonal' (spread on both axes), 'vertical'
      (top-bottom dominant), 'horizontal' (left-right dominant), 'point'
      (single anchor / no spread).
    - text_density_band: low / medium / high from total legible character count
      (extracted_text length) — Z-vs-F discriminator axis.
    - focal_singularity: True if one element's area dominates (>= 0.45 of total
      element area AND >= 2x the next largest) — single-hero signal.
    - cta_presence: True if any element kind/text or extracted_text carries a
      call-to-action token. A content-genre TAG, not a path (rides on top).
    - whitespace_dominance: True if positioned elements cover < 0.30 of the
      slide area (sparse) — the Z/headline sparsity signal.
    """
    elements = _positioned_elements(artifact_dump)
    extracted_text = str(artifact_dump.get("extracted_text") or "")
    title = str(artifact_dump.get("slide_title") or "")
    layout = str(artifact_dump.get("layout_description") or "")
    all_text = " ".join([title, extracted_text, layout]).lower()

    anchor_count = len(elements)

    # primary anchor = largest-area positioned element
    primary_anchor_position = "none"
    largest = None
    if elements:
        largest = max(elements, key=lambda e: e["area"])
        primary_anchor_position = f"{_v_band(largest['cy'])}-{_h_band(largest['cx'])}"

    # reading vector from center spread
    reading_vector = "point"
    if anchor_count >= 2:
        cxs = [e["cx"] for e in elements]
        cys = [e["cy"] for e in elements]
        x_spread = max(cxs) - min(cxs)
        y_spread = max(cys) - min(cys)
        if x_spread >= 0.25 and y_spread >= 0.25:
            reading_vector = "diagonal"
        elif y_spread >= 0.25 and y_spread > x_spread:
            reading_vector = "vertical"
        elif x_spread >= 0.25 and x_spread > y_spread:
            reading_vector = "horizontal"
        else:
            reading_vector = "point"

    # text density band from legible character count
    char_count = len(extracted_text)
    if char_count < 120:
        text_density_band = "low"
    elif char_count < 400:
        text_density_band = "medium"
    else:
        text_density_band = "high"

    # focal singularity: one element dominates the visual area
    focal_singularity = False
    if elements:
        areas = sorted((e["area"] for e in elements), reverse=True)
        total_area = sum(areas) or 1e-9
        top = areas[0]
        second = areas[1] if len(areas) > 1 else 0.0
        focal_singularity = (top / total_area) >= 0.45 and (
            second == 0.0 or top >= 2.0 * second
        )

    # CTA presence (genre TAG, not a path)
    cta_tokens = (
        "cta",
        "call to action",
        "sign up",
        "signup",
        "get started",
        "learn more",
        "join",
        "contact",
        "next steps",
        "take action",
        "schedule",
        "register",
        "download",
        "subscribe",
        "your turn",
    )
    kinds_text = " ".join(f"{e['kind']} {e['text']}" for e in elements).lower()
    cta_presence = any(t in all_text or t in kinds_text for t in cta_tokens)

    # whitespace dominance: elements cover little of the slide
    coverage_area = sum(e["area"] for e in elements)
    whitespace_dominance = coverage_area < 0.30

    return {
        "primary_anchor_position": primary_anchor_position,
        "anchor_count": anchor_count,
        "reading_vector": reading_vector,
        "text_density_band": text_density_band,
        "focal_singularity": focal_singularity,
        "cta_presence": cta_presence,
        "whitespace_dominance": whitespace_dominance,
        # derived numerics retained for clustering / centroid math
        "_char_count": char_count,
        "_coverage_area": round(coverage_area, 4),
    }


# ---------------------------------------------------------------------------
# Clustering of residue (first-pass, on the feature vector)
# ---------------------------------------------------------------------------


def _feature_signature(fv: dict[str, Any]) -> tuple:
    """Categorical signature used to group residue slides bottom-up.

    Uses the qualitative feature fields (not the private numerics) so clusters
    are geometry/structure-shaped, not content-shaped. anchor_count is bucketed
    coarsely (1 / 2-3 / 4-6 / 7+) to avoid singleton fragmentation.
    """
    n = fv["anchor_count"]
    if n <= 1:
        n_bucket = "1"
    elif n <= 3:
        n_bucket = "2-3"
    elif n <= 6:
        n_bucket = "4-6"
    else:
        n_bucket = "7+"
    return (
        fv["reading_vector"],
        fv["text_density_band"],
        bool(fv["focal_singularity"]),
        bool(fv["whitespace_dominance"]),
        n_bucket,
    )


def cluster_residue(residue: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Group residue slides by feature signature; emit candidate clusters.

    First-pass only: emits {cluster_id, members, signature, centroid, rough
    character}. Does NOT decide admission, name patterns, or author deltas.
    """
    groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for row in residue:
        groups[_feature_signature(row["feature_vector"])].append(row)

    clusters: list[dict[str, Any]] = []
    # stable ordering: largest groups first, then by signature
    ordered = sorted(groups.items(), key=lambda kv: (-len(kv[1]), str(kv[0])))
    for idx, (sig, members) in enumerate(ordered, start=1):
        reading_vector, density, focal, whitespace, n_bucket = sig
        # centroid of the categorical/numeric features
        char_counts = [m["feature_vector"]["_char_count"] for m in members]
        coverage = [m["feature_vector"]["_coverage_area"] for m in members]
        anchor_counts = [m["feature_vector"]["anchor_count"] for m in members]
        cta_frac = sum(1 for m in members if m["feature_vector"]["cta_presence"]) / len(members)
        centroid = {
            "reading_vector": reading_vector,
            "text_density_band": density,
            "focal_singularity": focal,
            "whitespace_dominance": whitespace,
            "anchor_count_bucket": n_bucket,
            "mean_anchor_count": round(sum(anchor_counts) / len(anchor_counts), 2),
            "mean_char_count": round(sum(char_counts) / len(char_counts), 1),
            "mean_coverage_area": round(sum(coverage) / len(coverage), 3),
            "cta_fraction": round(cta_frac, 2),
        }
        # rough character label (descriptive only — NOT a pattern name)
        character = _rough_character(centroid)
        clusters.append(
            {
                "cluster_id": f"RC{idx:02d}",
                "signature": list(sig),
                "size": len(members),
                "members": sorted(m["slide_id"] for m in members),
                "centroid": centroid,
                "rough_character": character,
            }
        )
    return clusters


def _rough_character(centroid: dict[str, Any]) -> str:
    """Descriptive (non-naming) character sketch for the orchestrator."""
    parts = []
    if centroid["focal_singularity"]:
        parts.append("single-focal-element")
    if centroid["whitespace_dominance"]:
        parts.append("sparse/whitespace-heavy")
    parts.append(f"{centroid['text_density_band']}-text-density")
    parts.append(f"{centroid['reading_vector']}-spread")
    parts.append(f"~{centroid['mean_anchor_count']}-anchors")
    if centroid["cta_fraction"] >= 0.5:
        parts.append("CTA-prevalent")
    return ", ".join(parts)


# ---------------------------------------------------------------------------
# Main scan
# ---------------------------------------------------------------------------


def enumerate_working_slides() -> list[Path]:
    """All corpus PNGs MINUS the 14 held-out. Asserts count == 54."""
    if not CORPUS_DIR.is_dir():
        raise SystemExit(f"FATAL: corpus dir not found: {CORPUS_DIR}")
    all_pngs = sorted(p for p in CORPUS_DIR.glob("*.png"))
    # sanity: corpus should be 68
    if len(all_pngs) != 68:
        raise SystemExit(
            f"FATAL: expected 68 corpus PNGs, found {len(all_pngs)} in {CORPUS_DIR}"
        )
    working = [p for p in all_pngs if p.name not in HELD_OUT]
    # also assert all 14 held-out are actually present (so exclusion is real)
    present_held = {p.name for p in all_pngs if p.name in HELD_OUT}
    missing_held = HELD_OUT - present_held
    if missing_held:
        raise SystemExit(
            f"FATAL: held-out manifest names slides not in corpus: {sorted(missing_held)}"
        )
    if len(working) != EXPECTED_WORKING_COUNT:
        raise SystemExit(
            f"FATAL: expected {EXPECTED_WORKING_COUNT} working slides, "
            f"got {len(working)} (held-out excluded={len(HELD_OUT)})"
        )
    return working


def scan() -> dict[str, Any]:
    # lazy imports so the count-assertion / env wiring can fail fast first
    from app.models.perception.perception_artifact import PerceptionArtifact
    from app.specialists.vision.provider import VisionProviderError, perceive_png
    from scripts.utilities.reading_path_classifier import (
        ReadingPathClassificationError,
        classify_reading_path,
        ordered_element_keys_for_reading_path,
    )

    working = enumerate_working_slides()
    PERCEPTIONS_DIR.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    for idx, png in enumerate(working, start=1):
        slide_id = png.stem
        print(f"[{idx:2d}/{len(working)}] perceiving {slide_id} ...", flush=True)
        try:
            response = perceive_png(png, slide_id=slide_id, model_id=MODEL_ID)
        except VisionProviderError as exc:
            tag = getattr(exc, "tag", "vision.provider.error")
            print(f"    ! ERROR ({tag}): {exc}", flush=True)
            errors.append({"slide_id": slide_id, "tag": tag, "error": str(exc)})
            # record an error stub so the report still lists the slide
            rows.append(
                {
                    "slide_id": slide_id,
                    "source_png": str(png),
                    "perceived_title": "",
                    "element_count": 0,
                    "feature_vector": None,
                    "fitted_pattern": "ERROR",
                    "scan_order": [],
                    "confidence_proxy": "n/a",
                    "residue": True,
                    "looks_z_overclaim": False,
                    "error": {"tag": tag, "message": str(exc)},
                }
            )
            continue
        except Exception as exc:  # noqa: BLE001 — record unexpected, continue
            print(f"    ! UNEXPECTED ERROR: {exc}", flush=True)
            errors.append(
                {
                    "slide_id": slide_id,
                    "tag": "unexpected",
                    "error": f"{exc}\n{traceback.format_exc()}",
                }
            )
            rows.append(
                {
                    "slide_id": slide_id,
                    "source_png": str(png),
                    "perceived_title": "",
                    "element_count": 0,
                    "feature_vector": None,
                    "fitted_pattern": "ERROR",
                    "scan_order": [],
                    "confidence_proxy": "n/a",
                    "residue": True,
                    "looks_z_overclaim": False,
                    "error": {"tag": "unexpected", "message": str(exc)},
                }
            )
            continue

        # Capture raw perception with provenance.
        artifact = PerceptionArtifact.model_validate(response.model_dump())
        artifact_dump = artifact.model_dump()
        capture = {
            "provenance": {
                "captured_at": CAPTURED_AT,
                "model_id": MODEL_ID,
                "source_png": str(png),
                "scan_tool": "scripts/analysis/reading_path_corpus_scan.py",
            },
            "perception_artifact": artifact_dump,
        }
        (PERCEPTIONS_DIR / f"{slide_id}.json").write_text(
            json.dumps(capture, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        # Feature vector — from the PERCEIVER output only (two-source rule).
        fv = compute_feature_vector(artifact_dump)

        # Fit to existing patterns (classifier). Catch unclassifiable -> residue.
        fitted_pattern: str
        residue: bool
        scan_order: list[str] = []
        try:
            fitted_pattern = classify_reading_path(artifact)
            residue = False
        except ReadingPathClassificationError as exc:
            fitted_pattern = "UNCLASSIFIABLE"
            residue = True
            errors_note = str(exc)
            # still try the position-order default for the record
            scan_order = []
        # position-order / canonical scan order via the classifier helper
        try:
            scan_order = ordered_element_keys_for_reading_path(artifact)
        except ReadingPathClassificationError:
            scan_order = []

        # _looks_z over-claim flag: classifier says z_pattern but the feature
        # vector suggests a headline/image/free-form-dominant slide instead
        # (single dominant fixation OR sparse whitespace with point/vertical
        # reading vector — i.e. NOT a genuine diagonal sweep). These are prime
        # residue candidates the orchestrator should re-examine.
        looks_z_overclaim = bool(
            fitted_pattern == "z_pattern"
            and (
                fv["focal_singularity"]
                or fv["reading_vector"] in {"point", "vertical"}
                or (fv["whitespace_dominance"] and fv["anchor_count"] <= 3)
            )
        )

        # If the slide ONLY fit via the over-eager _looks_z (flagged), treat it
        # as a residue CANDIDATE for clustering per the task spec ("fit only via
        # the over-eager _looks_z"). We keep fitted_pattern as recorded but mark
        # residue_for_clustering True so it enters the residue cluster pass.
        residue_for_clustering = residue or looks_z_overclaim

        # confidence proxy: the perceiver's own confidence_score (independent
        # of the classifier) — a rough fit-confidence stand-in.
        conf = artifact_dump.get("confidence_score")
        confidence_proxy = conf if conf is not None else artifact_dump.get("confidence", "n/a")

        rows.append(
            {
                "slide_id": slide_id,
                "source_png": str(png),
                "perceived_title": artifact_dump.get("slide_title", ""),
                "element_count": fv["anchor_count"],
                "feature_vector": fv,
                "fitted_pattern": fitted_pattern,
                "scan_order": scan_order,
                "confidence_proxy": confidence_proxy,
                "residue": residue,
                "residue_for_clustering": residue_for_clustering,
                "looks_z_overclaim": looks_z_overclaim,
            }
        )
        z_note = " [Z-OVERCLAIM]" if looks_z_overclaim else ""
        print(
            f"    -> fitted={fitted_pattern} elems={fv['anchor_count']} "
            f"vec={fv['reading_vector']} dens={fv['text_density_band']}{z_note}",
            flush=True,
        )

    # Cluster the residue (residue OR _looks_z-overclaim).
    residue_rows = [r for r in rows if r.get("residue_for_clustering") and r["feature_vector"]]
    clusters = cluster_residue(residue_rows)

    return {
        "rows": rows,
        "errors": errors,
        "clusters": clusters,
        "perceived_count": sum(1 for r in rows if r["fitted_pattern"] != "ERROR"),
        "working_count": len(working),
    }


# ---------------------------------------------------------------------------
# Evidence report
# ---------------------------------------------------------------------------


def _fv_brief(fv: dict[str, Any] | None) -> str:
    if not fv:
        return "—"
    flags = []
    if fv["focal_singularity"]:
        flags.append("focal")
    if fv["cta_presence"]:
        flags.append("cta")
    if fv["whitespace_dominance"]:
        flags.append("ws")
    flag_str = ("+" + "/".join(flags)) if flags else ""
    return (
        f"anchor={fv['primary_anchor_position']}; n={fv['anchor_count']}; "
        f"vec={fv['reading_vector']}; dens={fv['text_density_band']}{flag_str}"
    )


def write_report(result: dict[str, Any]) -> None:
    rows = result["rows"]
    errors = result["errors"]
    clusters = result["clusters"]

    # distribution histogram
    hist = Counter(r["fitted_pattern"] for r in rows)
    residue_count = sum(1 for r in rows if r["residue"])
    z_overclaim = [r["slide_id"] for r in rows if r.get("looks_z_overclaim")]
    bare_rows = [r for r in rows if r["slide_id"].split("_", 1)[-1] == ""]

    lines: list[str] = []
    lines.append("# Reading-Path Corpus Scan — Evidence Report (Phase 2b + first-pass 2c)")
    lines.append("")
    lines.append(f"**Captured:** {CAPTURED_AT}  ")
    lines.append(f"**Model:** `{MODEL_ID}` (live, no mocks; first-run-stands)  ")
    lines.append(f"**Corpus:** `{CORPUS_DIR}`  ")
    lines.append(
        f"**Working set:** {result['working_count']} slides "
        f"(68 corpus MINUS 14 held-out; held-out NOT perceived).  "
    )
    lines.append(
        f"**Perceived OK:** {result['perceived_count']} / {result['working_count']}; "
        f"**errors:** {len(errors)}."
    )
    lines.append("")
    lines.append(
        "This is an EVIDENCE artifact (data for the orchestrator's Phase 2c admission + "
        "Phase 3 catalog draft). It does NOT author the catalog, decide admission, name "
        "patterns, or write narration-deltas."
    )
    lines.append("")

    # Feature-vector derivation note
    lines.append("## Feature vector — derivation (D4; two-source rule)")
    lines.append("")
    lines.append("All features derived from the PERCEIVER output ONLY, never the classifier label:")
    lines.append("")
    lines.append("- **primary_anchor_position** — v-band/h-band (thirds) of the largest-area positioned element (dominant fixation target).")
    lines.append("- **anchor_count** — count of `visual_elements` carrying a usable bbox.")
    lines.append("- **reading_vector** — `diagonal`/`vertical`/`horizontal`/`point` from the spatial spread of element centers (x_spread/y_spread vs 0.25).")
    lines.append("- **text_density_band** — `low`(<120) / `medium`(<400) / `high` from `extracted_text` char count (Z-vs-F axis).")
    lines.append("- **focal_singularity** — one element's area ≥0.45 of total AND ≥2× the next (single-hero signal).")
    lines.append("- **cta_presence** — CTA token in text/kinds (content-genre TAG, not a path).")
    lines.append("- **whitespace_dominance** — positioned elements cover <0.30 of slide area (sparsity signal).")
    lines.append("")

    # Distribution summary
    lines.append("## Distribution summary — fit-to-existing-patterns")
    lines.append("")
    lines.append("| fitted pattern | count |")
    lines.append("|---|---|")
    for pattern, count in sorted(hist.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"| `{pattern}` | {count} |")
    lines.append(f"| **residue (UNCLASSIFIABLE)** | **{residue_count}** |")
    lines.append("")
    lines.append(
        f"**`_looks_z` over-claim flags ({len(z_overclaim)}):** "
        + (", ".join(f"`{s}`" for s in z_overclaim) if z_overclaim else "none")
        + "."
    )
    lines.append("")
    lines.append(
        "These are slides where the geometry classifier returned `z_pattern` but the "
        "feature vector indicates a headline/image/free-form-dominant slide (focal "
        "singularity, point/vertical reading vector, or sparse-with-≤3-anchors) — i.e. "
        "no genuine diagonal sweep. They are prime residue candidates and are folded "
        "into the residue clustering pass below."
    )
    lines.append("")

    # Bare slides
    lines.append("## Bare `N_.png` slides (likely section dividers)")
    lines.append("")
    if bare_rows:
        lines.append("| slide_id | title | n | fitted | feature vector |")
        lines.append("|---|---|---|---|---|")
        for r in sorted(bare_rows, key=lambda r: r["slide_id"]):
            lines.append(
                f"| `{r['slide_id']}` | {r['perceived_title'][:40]} | {r['element_count']} | "
                f"`{r['fitted_pattern']}` | {_fv_brief(r['feature_vector'])} |"
            )
    else:
        lines.append("_(none in the working set)_")
    lines.append("")

    # Per-slide table
    lines.append("## Per-slide table")
    lines.append("")
    lines.append("| slide_id | perceived title | n | feature vector | fitted | conf | residue? |")
    lines.append("|---|---|---|---|---|---|---|")
    for r in sorted(rows, key=lambda r: r["slide_id"]):
        title = (r["perceived_title"] or "").replace("|", "/")[:48]
        resflag = "Y" if r["residue"] else ("z?" if r.get("looks_z_overclaim") else "n")
        lines.append(
            f"| `{r['slide_id']}` | {title} | {r['element_count']} | "
            f"{_fv_brief(r['feature_vector'])} | `{r['fitted_pattern']}` | "
            f"{r['confidence_proxy']} | {resflag} |"
        )
    lines.append("")

    # Residue clusters
    lines.append("## Candidate residue clusters (first-pass — DATA, not decisions)")
    lines.append("")
    lines.append(
        "Clustered on the feature-vector signature (reading_vector, text_density_band, "
        "focal_singularity, whitespace_dominance, anchor-count bucket). Includes slides "
        "that did not fit OR fit only via the over-eager `_looks_z`. The orchestrator "
        "decides admission (N≥4, ≥2 genres, behavioral-distinctness, stability) — this "
        "tool does NOT."
    )
    lines.append("")
    if clusters:
        for c in clusters:
            lines.append(
                f"### {c['cluster_id']} — size {c['size']} — {c['rough_character']}"
            )
            lines.append("")
            lines.append(f"- **signature:** `{c['signature']}`")
            lines.append(f"- **centroid:** `{json.dumps(c['centroid'])}`")
            lines.append("- **members:** " + ", ".join(f"`{m}`" for m in c["members"]))
            lines.append("")
    else:
        lines.append("_(no residue — every working slide fit an existing pattern cleanly)_")
        lines.append("")

    # Errors
    lines.append("## Per-slide errors")
    lines.append("")
    if errors:
        lines.append("| slide_id | tag | error |")
        lines.append("|---|---|---|")
        for e in errors:
            msg = e["error"].replace("|", "/").splitlines()[0][:80]
            lines.append(f"| `{e['slide_id']}` | `{e['tag']}` | {msg} |")
    else:
        lines.append("_(none — all 54 working slides perceived successfully)_")
    lines.append("")

    EVIDENCE_REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    _load_dotenv()
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("FATAL: OPENAI_API_KEY not set (and not found in .env)")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    result = scan()
    write_report(result)

    # machine-readable summary alongside the markdown
    summary = {
        "captured_at": CAPTURED_AT,
        "model_id": MODEL_ID,
        "working_count": result["working_count"],
        "perceived_count": result["perceived_count"],
        "errors": result["errors"],
        "distribution": dict(Counter(r["fitted_pattern"] for r in result["rows"])),
        "residue_count": sum(1 for r in result["rows"] if r["residue"]),
        "z_overclaim": [r["slide_id"] for r in result["rows"] if r.get("looks_z_overclaim")],
        "clusters": result["clusters"],
    }
    (OUT_DIR / "scan-summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print("\n=== SCAN COMPLETE ===")
    print(f"perceived: {result['perceived_count']}/{result['working_count']}")
    print(f"errors: {len(result['errors'])}")
    print(f"distribution: {summary['distribution']}")
    print(f"residue: {summary['residue_count']}  z-overclaim: {len(summary['z_overclaim'])}")
    print(f"clusters: {len(result['clusters'])}")
    print(f"report: {EVIDENCE_REPORT}")


if __name__ == "__main__":
    main()
