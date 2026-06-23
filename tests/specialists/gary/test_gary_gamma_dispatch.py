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


def test_gary_variant_arc_dispatches_per_variant_gamma_settings(
    tmp_path: Path, monkeypatch
) -> None:
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
        "export_dir": str(tmp_path),
        "gamma_settings": [
            {
                "variant_id": "A",
                "theme": "theme-photo",
                "template": "template-smoke",
                "image_style": "photographic",
                "density": "balanced",
                "tone": "professional",
            },
            {
                "variant_id": "B",
                "theme": "theme-diagram",
                "template": "template-smoke",
                "image_style": "diagrammatic",
                "density": "dense",
                "tone": "technical",
            },
        ],
    }

    result = gary_act.generate_gamma_variants(payload, client=client)

    assert result["generation_mode"] == "double-dispatch"
    assert result["calls_made"] == 2
    assert result["variant_gamma_settings"] == payload["gamma_settings"]
    assert client.generate_calls[0]["theme_id"] == "theme-photo"
    assert client.generate_calls[0]["image_options"] == {"style": "photographic"}
    assert client.generate_calls[1]["theme_id"] == "theme-diagram"
    assert client.generate_calls[1]["image_options"] == {"style": "diagrammatic"}
    assert client.generate_calls[1]["text_options"] == {
        "amount": "dense",
        "tone": "technical",
    }
    rows = result["gary_slide_output"]
    assert {row["variant_id"] for row in rows} == {"A", "B"}
    assert {
        row["gamma_settings"]["image_style"]
        for row in rows
        if row["gamma_settings"] is not None
    } == {"photographic", "diagrammatic"}


def test_gary_variant_arc_partial_settings_fall_back_to_default_pair(
    tmp_path: Path, monkeypatch
) -> None:
    zpath = _titled_zip(tmp_path, ["1_Alpha-Topic"])
    monkeypatch.setattr(
        gary_act, "download_export", lambda url, *, output_dir, filename: str(zpath)
    )
    client = FakeGammaClient()

    result = gary_act.generate_gamma_variants(
        {
            "slides": [{"slide_id": "s1", "title": "Alpha Topic"}],
            "export_dir": str(tmp_path),
            "gamma_settings": [{"variant_id": "A", "image_style": "photographic"}],
        },
        client=client,
    )

    assert result["calls_made"] == 2
    assert result["variant_gamma_settings"][0]["image_style"] == "photographic"
    assert result["variant_gamma_settings"][1] == dict(gary_act.DEFAULT_VARIANT_PAIR[1])
    assert client.generate_calls[1]["image_options"] == {"style": "diagrammatic"}


def test_gary_no_gamma_settings_preserves_single_dispatch_shape(
    tmp_path: Path, monkeypatch
) -> None:
    zpath = _titled_zip(tmp_path, ["1_Only-Topic-Here"])
    monkeypatch.setattr(
        gary_act, "download_export", lambda url, *, output_dir, filename: str(zpath)
    )
    client = FakeGammaClient()

    result = gary_act.generate_gamma_variants(
        {"slides": [{"slide_id": "s1", "title": "Only Topic Here"}], "export_dir": str(tmp_path)},
        client=client,
    )

    assert result["generation_mode"] == "single-dispatch"
    assert result["calls_made"] == 1
    assert result["variant_gamma_settings"] == []
    assert len(result["gary_slide_output"]) == 1
    assert result["gary_slide_output"][0]["dispatch_variant"] == "A"
    assert result["gary_slide_output"][0]["gamma_settings"] is None
    assert "image_options" not in client.generate_calls[0]


def test_gary_generation_pins_titles_and_card_split(tmp_path: Path, monkeypatch) -> None:
    """Storyboard-correctness follow-on (2026-06-19): the generation call must
    (a) pass cardSplit=inputTextBreaks so Gamma cannot merge/split briefed
    slides, and (b) lead every `\\n---\\n` chunk with the exact briefed title as
    a heading so Gamma adopts it as the card title and the export title-matcher
    binds bijectively (the slide-05/06 brief-unmatched failure)."""
    zpath = _titled_zip(tmp_path, ["1_Economic-Reality", "2_Leadership-Gap"])
    monkeypatch.setattr(
        gary_act, "download_export", lambda url, *, output_dir, filename: str(zpath)
    )
    client = FakeGammaClient()
    payload = {
        "slides": [
            {"slide_id": "s1", "title": "Economic Reality", "prompt": "Economic Reality — explain"},
            {"slide_id": "s2", "title": "Leadership Gap", "prompt": "Leadership Gap — explain"},
        ],
        "additional_instructions": "Experience profile: balanced.",
        "export_dir": str(tmp_path),
    }

    gary_act.generate_gamma_variants(payload, client=client)

    call = client.generate_calls[0]
    # (a) card count is pinned to the input-text breaks, not Gamma's discretion.
    assert call["card_split"] == "inputTextBreaks"
    # (b) each chunk leads with the exact briefed title as a heading, joined by
    #     the `\n---\n` break inputTextBreaks splits on.
    input_text = str(call["input_text"])
    assert input_text.startswith("# Economic Reality")
    assert "\n---\n# Leadership Gap" in input_text
    assert input_text.count("\n---\n") == 1  # exactly N-1 breaks for N slides
    # the title used as the heading is the SAME string the matcher keys on.
    assert gary_act._slide_title(payload["slides"][0], 1) == "Economic Reality"
    # builder instructions are preserved and the title-preservation guidance +
    # variant marker are appended.
    instructions = str(call["additional_instructions"])
    assert "Experience profile: balanced." in instructions
    assert "verbatim" in instructions
    assert "do not merge or split" in instructions
    assert instructions.rstrip().endswith("Variant A.")


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
