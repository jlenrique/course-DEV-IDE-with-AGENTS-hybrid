from __future__ import annotations

from pathlib import Path

from app.specialists.gary import _act as gary_act


class FakeGammaClient:
    def __init__(self, exported_paths: list[str]) -> None:
        self.exported_paths = exported_paths
        self.theme_calls = 0
        self.generate_calls: list[dict[str, object]] = []

    def list_themes(self, limit: int = 20) -> list[dict[str, str]]:
        self.theme_calls += 1
        return [{"id": "theme-clean-grid", "name": "Clean Grid"}]

    def generate_deck(self, input_text: str, **kwargs: object) -> dict[str, object]:
        self.generate_calls.append({"input_text": input_text, **kwargs})
        return {
            "generation_id": f"gen-{len(self.generate_calls)}",
            "exported_slide_paths": self.exported_paths,
        }


def test_gary_gamma_dispatch_happy_path_uses_theme_handshake(tmp_path: Path) -> None:
    paths = [str(tmp_path / "slide-01.png"), str(tmp_path / "slide-02.png")]
    client = FakeGammaClient(paths)
    payload = {
        "slides": [{"prompt": "Title"}, {"prompt": "Comparison"}],
        "export_dir": str(tmp_path),
    }

    result = gary_act.generate_gamma_variants(payload, client=client)

    assert client.theme_calls == 1
    assert len(client.generate_calls) == 1
    assert client.generate_calls[0]["theme_id"] == "theme-clean-grid"
    assert result["gary_slide_output"][0]["file_path"] == paths[0]
    assert result["vera_g3_invocation"]["artifact_paths"] == paths


def test_gary_double_dispatch_generates_per_slide_variants(tmp_path: Path) -> None:
    paths = [str(tmp_path / "slide-01.png"), str(tmp_path / "slide-02.png")]
    client = FakeGammaClient(paths)
    payload = {
        "slides": [{"slide_id": "s1", "prompt": "A"}, {"slide_id": "s2", "prompt": "B"}],
        "double_dispatch": True,
        "export_dir": str(tmp_path),
    }

    result = gary_act.generate_gamma_variants(payload, client=client)

    assert result["generation_mode"] == "double-dispatch"
    assert result["calls_made"] == 2
    assert len(result["gary_slide_output"]) == 4
    assert {row["dispatch_variant"] for row in result["gary_slide_output"]} == {"A", "B"}


def test_gary_png_export_normalization_materializes_single_slide(tmp_path: Path) -> None:
    downloaded = tmp_path / "gamma-export.png"
    downloaded.write_bytes(b"png-bytes")
    client = FakeGammaClient([])

    def _generate_deck(input_text: str, **kwargs: object) -> dict[str, object]:
        client.generate_calls.append({"input_text": input_text, **kwargs})
        return {"generation_id": "gen-png", "downloaded_path": str(downloaded)}

    client.generate_deck = _generate_deck  # type: ignore[method-assign]
    result = gary_act.generate_gamma_variants(
        {"slides": [{"slide_id": "s1", "prompt": "Only"}], "export_dir": str(tmp_path)},
        client=client,
    )

    normalized = Path(result["gary_slide_output"][0]["file_path"])
    assert normalized.name == "gary_slide_01.png"
    assert normalized.read_bytes() == b"png-bytes"
