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


__all__ = ["emit_storyboard_html", "render_storyboard_html"]
