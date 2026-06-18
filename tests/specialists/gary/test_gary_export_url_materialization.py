"""Pin: §07 downloads the Gamma export and materializes per-slide PNGs.

Pre-S5 recon gap (2026-06-12): ``GammaClient.generate_deck`` waits for
completion but never downloads; completed generations carry only ``exportUrl``.
The download/materialize leg ensures every slide row lands with a real
``file_path`` (no G2C no-viewable-slides gap).

Re-blessed 2026-06-18 (storyboard-correctness fix): the export leg now binds
exported pages to briefs by TITLE (``materialize_exported_slide_paths_by_title``)
instead of positionally. ``_paths_from_generation`` was removed; this pins the
download→title-match→per-slide-path guarantee through ``generate_gamma_variants``.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

from app.specialists.gary import _act

_PNG_MAGIC = b"\x89PNG\r\n\x1a\n" + b"0" * 64


def _titled_zip(path: Path, stems: list[str]) -> Path:
    with zipfile.ZipFile(path, "w") as archive:
        for stem in stems:
            # Distinct per-page bytes so content identity proves WHICH page bound.
            archive.writestr(f"{stem}.png", _PNG_MAGIC + stem.encode())
    return path


class _Client:
    def __init__(self) -> None:
        self.generate_calls: list[dict[str, object]] = []

    def list_themes(self, limit: int = 20) -> list[dict[str, str]]:
        return [{"id": "theme-clean-grid", "name": "Clean Grid"}]

    def generate_deck(self, input_text: str, **kwargs: object) -> dict[str, object]:
        self.generate_calls.append({"input_text": input_text, **kwargs})
        return {"generationId": "gen-123", "status": "completed", "exportUrl": "https://x/fake.zip"}


def test_export_url_leg_downloads_and_materializes_per_slide_paths(
    tmp_path: Path, monkeypatch
) -> None:
    # Pages in REVERSE order vs briefs: a positional binder would map s1 -> the
    # System-Pressures page (wrong). Title matching must bind s1 -> Macro-Trends.
    zpath = _titled_zip(tmp_path / "export.zip", ["1_System-Pressures", "2_Macro-Trends"])
    monkeypatch.setattr(
        _act, "download_export", lambda url, *, output_dir, filename: str(zpath)
    )

    result = _act.generate_gamma_variants(
        {
            "slides": [
                {"slide_id": "s1", "title": "Macro Trends"},
                {"slide_id": "s2", "title": "System Pressures"},
            ],
            "export_dir": str(tmp_path),
        },
        client=_Client(),
    )

    rows = {r["slide_id"]: r for r in result["gary_slide_output"]}
    assert len(rows) == 2
    for row in rows.values():
        assert row["file_path"], "empty file_path row — the G2C no-viewable-slides gap is back"
        assert Path(row["file_path"]).is_file()
    # Content identity (NOT position): s1 bound to the Macro-Trends page even
    # though it was page 2 in export order; s2 to System-Pressures (page 1).
    assert Path(rows["s1"]["file_path"]).read_bytes() == _PNG_MAGIC + b"2_Macro-Trends"
    assert Path(rows["s2"]["file_path"]).read_bytes() == _PNG_MAGIC + b"1_System-Pressures"
