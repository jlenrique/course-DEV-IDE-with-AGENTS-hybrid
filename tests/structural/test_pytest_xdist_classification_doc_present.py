from __future__ import annotations

import re
from pathlib import Path

DOC = Path(__file__).resolve().parents[2] / "docs" / "dev-guide" / "pytest-xdist-classification.md"


def test_pytest_xdist_classification_doc_exists_with_required_sections() -> None:
    body = DOC.read_text(encoding="utf-8")
    for keyword in [
        "background",
        "classification methodology",
        "markers registry",
        "project-default invocation",
        "smoke-suite manifest",
        "maintenance",
    ]:
        assert re.search(rf"^## .*{re.escape(keyword)}", body, re.IGNORECASE | re.MULTILINE)


def test_pytest_xdist_classification_doc_cross_references_velocity_amendment() -> None:
    body = DOC.read_text(encoding="utf-8")
    assert "_bmad-output/planning-artifacts/slab-7c-velocity-amendments-2026-05-04.md" in body
