"""Render DrillSpec to a Markdown artifact family (Mine 5).

Distinct from workbook: no REVOICE, no DOCX, no depth-delta sections — short
practice items only.
"""

from __future__ import annotations

from pathlib import Path

from app.marcus.lesson_plan.drill_spec import DrillSpec


class DrillProducerError(ValueError):
    """Raised when drill render cannot proceed honestly."""


def render_drill_markdown(spec: DrillSpec) -> str:
    """Render a schema-validated drill to Markdown (canonical artifact)."""
    if not spec.items:
        raise DrillProducerError(
            "empty drill: refusing silent zero-byte success "
            "(project empty source as warning upstream; do not claim render)"
        )
    lines = [
        f"# {spec.title}",
        "",
        f"<!-- kind: {spec.kind} -->",
        f"<!-- schema_version: {spec.schema_version} -->",
        "",
        "Short practice items linked to learning objectives.",
        "",
    ]
    for item in spec.items:
        lines.extend(
            [
                f"## {item.item_id}",
                "",
                f"**Learning objective:** `{item.learning_objective_id}`",
                "",
                f"**Prompt:** {item.prompt}",
                "",
                f"**Expected focus:** {item.expected_focus}",
                "",
            ]
        )
        if item.source_refs:
            lines.append("**Source refs:**")
            for ref in item.source_refs:
                lines.append(f"- `{ref.ref_id}` @ {ref.locator}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_drill_artifact(spec: DrillSpec, output_path: Path) -> Path:
    """Write non-empty drill Markdown to ``output_path``."""
    body = render_drill_markdown(spec)
    if not body.strip():
        raise DrillProducerError("rendered drill body is empty")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(body, encoding="utf-8")
    if output_path.stat().st_size == 0:
        raise DrillProducerError("wrote zero-byte drill artifact")
    return output_path


__all__ = [
    "DrillProducerError",
    "render_drill_markdown",
    "write_drill_artifact",
]
