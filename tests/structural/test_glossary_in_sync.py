"""Glossary sync check for Story 7a.6."""

from __future__ import annotations

from pathlib import Path

from app.models.glossary_emit import GLOSSARY_PATH, REGISTRY_PATH, emit_glossary


def test_glossary_is_in_sync(tmp_path: Path) -> None:
    candidate = tmp_path / "glossary.md"
    emit_glossary(REGISTRY_PATH, candidate)
    assert candidate.read_text(encoding="utf-8") == GLOSSARY_PATH.read_text(encoding="utf-8")
