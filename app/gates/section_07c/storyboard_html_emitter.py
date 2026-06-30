"""Deterministic HTML emitter for Section 07C storyboard review artifacts."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

from app.models.operator_verdict_section_07c import StoryboardBuildPayload


def _slide_block(slide: dict[str, Any]) -> list[str]:
    slide_index = escape(str(slide.get("slide_index", "")))
    title = escape(str(slide.get("title", "")))
    body = escape(str(slide.get("body", "")))
    caption = slide.get("caption")
    lines = [
        '<section class="storyboard-slide">',
        f"  <h2>Slide {slide_index}: {title}</h2>",
        f"  <p>{body}</p>",
    ]
    if caption is not None:
        lines.append(f'  <p class="caption">{escape(str(caption))}</p>')
    lines.append("</section>")
    return lines


def render_storyboard_html(
    payload: StoryboardBuildPayload,
    *,
    plan_unit_id: str,
    slide_content: list[dict[str, Any]],
) -> str:
    """Render deterministic storyboard review HTML with LF line endings."""

    lines = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '  <meta charset="utf-8">',
        f"  <title>Storyboard - {escape(plan_unit_id)} / {escape(payload.target_section)}</title>",
        "</head>",
        "<body>",
        f"  <h1>Storyboard - {escape(plan_unit_id)}</h1>",
        f"  <p>Target section: {escape(payload.target_section)}</p>",
    ]
    for slide in sorted(slide_content, key=lambda row: int(row.get("slide_index", 0))):
        lines.extend(f"  {line}" for line in _slide_block(slide))
    lines.extend(["</body>", "</html>", ""])
    return "\n".join(lines)


def render_coverage_section(receipt: dict[str, Any]) -> str:
    """Render the operator-facing COVERAGE RECEIPT section (per-slide, pre-spend).

    Additive (concierge-coverage-assurance-interlock AC10): a deterministic HTML
    block appended to the Storyboard-B review surface. Columns: source-point
    (slide_key + human label) · intent-set · coverage status · containment verdict +
    ``vouch_level``. The report DECLARES its ``segmentation`` grain on its face
    (Irene caveat — load-bearing, never dropped). Passing an empty/None receipt
    yields ``""`` so the existing render is byte-identical when coverage is off.

    Accepts the receipt as a plain dict (``CoverageReceipt.model_dump``) to keep
    this gate module free of an ``app.marcus`` import (lane isolation).
    """
    if not receipt:
        return ""
    rows = receipt.get("rows") or []
    grain = escape(str(receipt.get("segmentation", "")))
    lines = [
        '<section class="coverage-receipt">',
        "  <h2>Source-note coverage receipt</h2>",
        f'  <p class="coverage-grain">Segmentation grain: <strong>{grain}</strong> '
        f"({len(rows)} source point(s))</p>",
        '  <table class="coverage-table">',
        "    <thead><tr>"
        "<th>Source point</th><th>Intent</th><th>Coverage</th>"
        "<th>Containment</th><th>Vouch</th>"
        "</tr></thead>",
        "    <tbody>",
    ]
    for row in sorted(rows, key=lambda r: str(r.get("source_point_id", ""))):
        label = escape(str(row.get("human_label", row.get("slide_key", ""))))
        point_id = escape(str(row.get("source_point_id", "")))
        intents = escape(", ".join(row.get("intent_set", []) or []))
        status = escape(str(row.get("coverage_status", "")))
        verdict = row.get("containment_verdict")
        verdict_txt = escape(str(verdict)) if verdict is not None else "&mdash;"
        vouch = escape(str(row.get("vouch_level", "")))
        flag = ' class="must-cover"' if row.get("must_cover") else ""
        lines.append(
            f"      <tr{flag}><td>{label} <code>{point_id}</code></td>"
            f"<td>{intents}</td><td>{status}</td>"
            f"<td>{verdict_txt}</td><td>{vouch}</td></tr>"
        )
    lines.extend(["    </tbody>", "  </table>", "</section>"])
    return "\n".join(lines)


def emit_storyboard_html(
    payload: StoryboardBuildPayload,
    output_path: Path,
    *,
    plan_unit_id: str,
    slide_content: list[dict[str, Any]],
) -> Path:
    """Write deterministic storyboard review HTML and return the path."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        render_storyboard_html(
            payload,
            plan_unit_id=plan_unit_id,
            slide_content=slide_content,
        ),
        encoding="utf-8",
        newline="\n",
    )
    return output_path


__all__ = ["emit_storyboard_html", "render_coverage_section", "render_storyboard_html"]
