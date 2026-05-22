from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from app.composers.section_02a import (
    Directive,
    DirectiveRole,
    DirectiveSource,
    write_directive_yaml,
)


def test_write_directive_yaml_preserves_utf8_without_pythonioencoding(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.delenv("PYTHONIOENCODING", raising=False)
    locator = "differential diagnosis Screenshot 2026-02-10 at 5.38.36\u202fPM.png"
    directive = Directive(
        run_id=uuid4(),
        corpus_dir=tmp_path.as_posix(),
        sources=[
            DirectiveSource(
                ref_id="src-001",
                locator=locator,
                role=DirectiveRole.SUPPORTING,
                description="Visual reference with macOS screenshot filename.",
            )
        ],
        composed_at=datetime.now(tz=UTC),
    )

    output = write_directive_yaml(directive, tmp_path / "directive.yaml")
    raw = output.read_bytes()

    assert b"\xe2\x80\xaf" in raw
    assert raw.decode("utf-8")
