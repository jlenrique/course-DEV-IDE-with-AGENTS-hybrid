from __future__ import annotations

import zipfile
from pathlib import Path

from app.specialists.gary import _act as gary_act

# Re-blessed 2026-06-18 (storyboard-correctness fix): these tests previously
# asserted POSITIONAL page->slide binding (file_path == paths[index]) — which
# was the bug. They now exercise the title-matched contract: Gamma returns an
# exportUrl + a zip of titled pages, and pages bind to briefs by title.


def _titled_zip(tmp_path: Path, stems: list[str]) -> Path:
    zpath = tmp_path / "gamma-export.zip"
    with zipfile.ZipFile(zpath, "w") as archive:
        # DISTINCT per-page bytes so a content-identity assertion can prove the
        # CORRECT page bound (a wrong/positional binding would fail) — not just
        # that some file with the right name exists (blind review SHOULD-FIX).
        for stem in stems:
            archive.writestr(f"{stem}.png", f"bytes::{stem}".encode())
    return zpath


class FakeGammaClient:
    def __init__(self) -> None:
        self.theme_calls = 0
        self.generate_calls: list[dict[str, object]] = []

    def list_themes(self, limit: int = 20) -> list[dict[str, str]]:
        self.theme_calls += 1
        return [{"id": "theme-clean-grid", "name": "Clean Grid"}]

    def generate_deck(self, input_text: str, **kwargs: object) -> dict[str, object]:
        self.generate_calls.append({"input_text": input_text, **kwargs})
        return {
            "generation_id": f"gen-{len(self.generate_calls)}",
            "exportUrl": "https://example.invalid/export.zip",
        }


def test_gary_gamma_dispatch_happy_path_uses_theme_handshake(tmp_path: Path, monkeypatch) -> None:
    zpath = _titled_zip(tmp_path, ["1_Title-One", "2_Comparison-View"])
    monkeypatch.setattr(
        gary_act, "download_export", lambda url, *, output_dir, filename: str(zpath)
    )
    client = FakeGammaClient()
    payload = {
        "slides": [
            {"slide_id": "s1", "title": "Title One"},
            {"slide_id": "s2", "title": "Comparison View"},
        ],
        "export_dir": str(tmp_path),
    }

    result = gary_act.generate_gamma_variants(payload, client=client)

    assert client.theme_calls == 1
    assert len(client.generate_calls) == 1
    assert client.generate_calls[0]["theme_id"] == "theme-clean-grid"
    rows = {row["slide_id"]: row for row in result["gary_slide_output"]}
    # Title-matched (NOT positional): content-identity proves s1 bound to the
    # Title-One page and s2 to the Comparison-View page (distinct bytes).
    assert Path(rows["s1"]["file_path"]).read_bytes() == b"bytes::1_Title-One"
    assert Path(rows["s2"]["file_path"]).read_bytes() == b"bytes::2_Comparison-View"
    # Observation A: the real title flows to display_title (not the slide_id).
    assert rows["s1"]["display_title"] == "Title One"


def test_gary_double_dispatch_generates_per_slide_variants(tmp_path: Path, monkeypatch) -> None:
    zpath = _titled_zip(tmp_path, ["1_Alpha-Topic", "2_Beta-Topic"])
    monkeypatch.setattr(
        gary_act, "download_export", lambda url, *, output_dir, filename: str(zpath)
    )
    client = FakeGammaClient()
    payload = {
        "slides": [
            {"slide_id": "s1", "title": "Alpha Topic"},
            {"slide_id": "s2", "title": "Beta Topic"},
        ],
        "double_dispatch": True,
        "export_dir": str(tmp_path),
    }

    result = gary_act.generate_gamma_variants(payload, client=client)

    assert result["generation_mode"] == "double-dispatch"
    assert result["calls_made"] == 2
    assert len(result["gary_slide_output"]) == 4
    assert {row["dispatch_variant"] for row in result["gary_slide_output"]} == {"A", "B"}
    # Every row title-bound to a real artifact (no empty/positional fill).
    assert all(
        row["file_path"].endswith(f"_{row['slide_id']}.png")
        for row in result["gary_slide_output"]
    )


def test_gary_single_slide_deck_title_matches(tmp_path: Path, monkeypatch) -> None:
    zpath = _titled_zip(tmp_path, ["1_Only-Topic-Here"])
    monkeypatch.setattr(
        gary_act, "download_export", lambda url, *, output_dir, filename: str(zpath)
    )
    client = FakeGammaClient()

    result = gary_act.generate_gamma_variants(
        {"slides": [{"slide_id": "s1", "title": "Only Topic Here"}], "export_dir": str(tmp_path)},
        client=client,
    )

    row = result["gary_slide_output"][0]
    materialized = Path(row["file_path"])
    assert materialized.name.endswith("_s1.png")
    assert materialized.read_bytes() == b"bytes::1_Only-Topic-Here"
