"""Glossary emitter tests for Story 7a.6."""

from __future__ import annotations

from pathlib import Path

from app.models.glossary_emit import emit_glossary, render_glossary


def test_emit_produces_expected_sections(tmp_path: Path) -> None:
    output = tmp_path / "glossary.md"
    emit_glossary(output_path=output)
    text = output.read_text(encoding="utf-8")
    assert "# Conversational Gate Vocabulary Glossary" in text
    assert "## gates" in text
    assert "## specialists" in text
    assert "## shared" in text
    assert "`quinn_r`" in text


def test_emit_is_idempotent(tmp_path: Path) -> None:
    output = tmp_path / "glossary.md"
    emit_glossary(output_path=output)
    first = output.read_text(encoding="utf-8")
    emit_glossary(output_path=output)
    assert output.read_text(encoding="utf-8") == first


def test_render_is_byte_stable_across_two_runs() -> None:
    registry = {
        "schema_version": "1.0",
        "namespaces": {
            "sample": {
                "description": "Sample namespace.",
                "tokens": {"decision": ["confirm"]},
            }
        },
    }
    assert render_glossary(registry) == render_glossary(registry)
