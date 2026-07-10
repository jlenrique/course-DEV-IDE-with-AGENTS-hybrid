"""Render QuizSpec to Markdown (Mine-next N3)."""

from __future__ import annotations

from pathlib import Path

from app.marcus.lesson_plan.quiz_spec import QuizSpec


class QuizProducerError(ValueError):
    """Raised when quiz render cannot proceed honestly."""


def render_quiz_markdown(spec: QuizSpec) -> str:
    """Render a schema-validated quiz to Markdown."""
    if not spec.items:
        raise QuizProducerError(
            "empty quiz: refusing silent zero-byte success"
        )
    lines = [
        f"# {spec.title}",
        "",
        f"<!-- kind: {spec.kind} -->",
        f"<!-- schema_version: {spec.schema_version} -->",
        "",
        "Short quiz items linked to learning objectives.",
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
            ]
        )
        if item.choices:
            lines.append("**Choices:**")
            for choice in item.choices:
                lines.append(f"- {choice}")
            lines.append("")
        lines.extend(
            [
                f"**Expected answer focus:** {item.expected_answer_focus}",
                "",
            ]
        )
        if item.source_refs:
            lines.append("**Source refs:**")
            for ref in item.source_refs:
                lines.append(f"- `{ref.ref_id}` @ {ref.locator}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_quiz_artifact(spec: QuizSpec, output_path: Path) -> Path:
    """Write non-empty quiz Markdown to ``output_path``."""
    body = render_quiz_markdown(spec)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(body, encoding="utf-8")
    if output_path.stat().st_size == 0:
        raise QuizProducerError("wrote zero-byte quiz artifact")
    return output_path


__all__ = [
    "QuizProducerError",
    "render_quiz_markdown",
    "write_quiz_artifact",
]
