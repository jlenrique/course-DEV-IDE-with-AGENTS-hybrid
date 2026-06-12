"""Pin: §07 materializes local slide PNGs from a completed generation.

Pre-S5 recon gap (2026-06-12, found minutes after the operator's live Gamma
micro-smoke): ``GammaClient.generate_deck`` waits for completion but never
downloads, and ``_paths_from_generation`` had no ``exportUrl`` leg — every
``gary_slide_output`` row landed with ``file_path: ""`` and Storyboard A at
G2C would have had no viewable slides (the kira-empty-URL class, sitting on
the S5 acceptance path). The download/materialize machinery existed in
gamma_operations but was wired only into the standalone lane.
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

from app.specialists.gary import _act

_PNG_MAGIC = b"\x89PNG\r\n\x1a\n" + b"0" * 64


def _fake_zip_bytes(card_count: int) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for index in range(1, card_count + 1):
            archive.writestr(f"slide-{index:02d}.png", _PNG_MAGIC)
    return buffer.getvalue()


def test_export_url_leg_downloads_and_materializes_per_slide_paths(
    tmp_path: Path, monkeypatch
) -> None:
    slides = [{"slide_id": "s1"}, {"slide_id": "s2"}]
    export_dir = tmp_path / "exports"
    export_dir.mkdir()

    def _fake_download(export_url, output_dir=None, filename=None, *, run_id=None):
        target = Path(output_dir) / (filename or "export.zip")
        target.write_bytes(_fake_zip_bytes(len(slides)))
        return target

    monkeypatch.setattr(_act, "download_export", _fake_download)
    generation = {
        "generationId": "gen-123",
        "status": "completed",
        "exportUrl": "https://assets.api.gamma.app/export/image/fake.zip",
    }

    paths = _act._paths_from_generation(
        generation, slides=slides, export_dir=export_dir, label="A"
    )

    assert len(paths) == 2
    for path in paths:
        assert path, "empty file_path row — the G2C no-viewable-slides gap is back"
        assert Path(path).is_file()
        assert Path(path).suffix == ".png"


def test_completed_generation_without_export_url_still_falls_through(
    tmp_path: Path,
) -> None:
    """No exportUrl and no downloaded_path → legacy fallbacks unchanged."""
    paths = _act._paths_from_generation(
        {"generationId": "gen-456", "status": "completed"},
        slides=[{"slide_id": "s1"}],
        export_dir=tmp_path,
        label="A",
    )
    assert paths == []
