from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

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
        return [
            {"id": "theme-clean-grid", "name": "Clean Grid"},
            {"id": "theme-photo", "name": "Photo"},
            {"id": "theme-diagram", "name": "Diagram"},
            {"id": "njim9kuhfnljvaa", "name": "2026 HIL APC (Nejal)"},
            {"id": "e8tz1vxb9v1urqp", "name": "Blueprint Editorial"},
        ]

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
    assert result["variant_gamma_settings"][0] | payload["gamma_settings"][0] == result[
        "variant_gamma_settings"
    ][0]
    assert result["variant_gamma_settings"][1] | payload["gamma_settings"][1] == result[
        "variant_gamma_settings"
    ][1]
    assert client.generate_calls[0]["theme_id"] == "theme-photo"
    assert client.generate_calls[0]["image_options"] == {
        "source": "aiGenerated",
        "stylePreset": "illustration",
    }
    assert client.generate_calls[1]["theme_id"] == "theme-diagram"
    assert client.generate_calls[1]["image_options"] == {
        "source": "aiGenerated",
        "model": "recraft-v3-svg",
        "stylePreset": "lineArt",
    }
    assert client.generate_calls[1]["text_options"] == {
        "amount": "brief",
        "audience": (
            "Faculty and instructional designers familiar with Canvas and course "
            "design, American English"
        ),
        "language": "en",
        "tone": "technical",
    }
    rows = result["gary_slide_output"]
    assert {row["variant_id"] for row in rows} == {"A", "B"}
    assert {
        row["gamma_settings"]["image_style"]
        for row in rows
        if row["gamma_settings"] is not None
    } == {"photographic", "diagrammatic"}


def test_gary_variant_arc_single_named_variant_dispatches_one(
    tmp_path: Path, monkeypatch
) -> None:
    # Retired the ``[A,B]`` padding (styleguide-retire-default-variant-pair 2026-07-01):
    # a payload naming ONE variant dispatches exactly that variant. Previously this
    # padded an unbound fixture-B deck from DEFAULT_VARIANT_PAIR (a phantom PAID deck).
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

    assert result["calls_made"] == 1
    assert len(result["variant_gamma_settings"]) == 1
    assert result["variant_gamma_settings"][0]["variant_id"] == "A"
    assert result["variant_gamma_settings"][0]["image_style"] == "photographic"
    assert len(client.generate_calls) == 1  # no fixture-seeded B deck


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
    # Styleguide library is now the SOLE determinant of dimensions (Leg-A 2026-07-01):
    # the former unconditional cardOptions.dimensions="16x9" override is REMOVED. A
    # default Classic run (no gamma_settings) carries NO card_options at all; the
    # Descript anti-crop OUTCOME moves to a publication-time policy follow-on.
    assert "card_options" not in client.generate_calls[0]
    assert client.generate_calls[0] == {
        "input_text": "# Only Topic Here",
        "num_cards": 1,
        "theme_id": "theme-clean-grid",
        "card_split": "inputTextBreaks",
        "additional_instructions": (
            "Use each section's leading heading as that card's title verbatim; "
            "produce exactly one card per section; do not add a cover, agenda, "
            "divider, or summary card; do not merge or split sections. Variant A."
        ),
        "export_as": "png",
    }


def test_gary_theme_validation_resolves_name_before_generation(
    tmp_path: Path, monkeypatch
) -> None:
    zpath = _titled_zip(tmp_path, ["1_Alpha-Topic"])
    monkeypatch.setattr(
        gary_act, "download_export", lambda url, *, output_dir, filename: str(zpath)
    )
    client = FakeGammaClient()

    gary_act.generate_gamma_variants(
        {
            "slides": [{"slide_id": "s1", "title": "Alpha Topic"}],
            "export_dir": str(tmp_path),
            "gamma_settings": [{"variant_id": "A", "theme": "Photo"}],
        },
        client=client,
    )

    assert client.generate_calls[0]["theme_id"] == "theme-photo"


def test_gary_theme_validation_blocks_bad_theme_before_generation(tmp_path: Path) -> None:
    client = FakeGammaClient()

    try:
        gary_act.generate_gamma_variants(
            {
                "slides": [{"slide_id": "s1", "title": "Alpha Topic"}],
                "export_dir": str(tmp_path),
                "gamma_settings": [{"variant_id": "A", "theme": "theme-real-looking-absent"}],
            },
            client=client,
        )
    except gary_act.GaryActError as exc:
        assert exc.tag == "gamma.theme.invalid"
    else:  # pragma: no cover - assertion branch
        raise AssertionError("bad theme must fail loud")

    assert client.generate_calls == []


def test_gary_enum_validation_blocks_bad_amount_before_generation(tmp_path: Path) -> None:
    client = FakeGammaClient()

    with pytest.raises(gary_act.GaryActError, match="amount"):
        gary_act.generate_gamma_variants(
            {
                "slides": [{"slide_id": "s1", "title": "Alpha Topic"}],
                "export_dir": str(tmp_path),
                "gamma_settings": [{"variant_id": "A", "amount": "minimalish"}],
            },
            client=client,
        )

    assert client.generate_calls == []


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("amount", "minimalish"),
        ("image_style_preset", "painterly"),
        ("image_model", "balanced"),
        ("image_source", "stockpile"),
        ("dimensions", "auto"),
        ("language", "balanced"),
        ("text_mode", "auto"),
    ],
)
def test_gary_enum_validation_blocks_bad_knobs_before_generation(
    key: str, value: str, tmp_path: Path, monkeypatch
) -> None:
    zpath = _titled_zip(tmp_path, ["1_Alpha-Topic"])
    monkeypatch.setattr(
        gary_act, "download_export", lambda url, *, output_dir, filename: str(zpath)
    )
    client = FakeGammaClient()

    with pytest.raises(gary_act.GaryActError) as exc_info:
        gary_act.generate_gamma_variants(
            {
                "slides": [{"slide_id": "s1", "title": "Alpha Topic"}],
                "export_dir": str(tmp_path),
                "gamma_settings": [{"variant_id": "A", key: value}],
            },
            client=client,
        )

    assert exc_info.value.tag == "gamma.settings.invalid"
    assert client.generate_calls == []


def test_gary_custom_style_preset_requires_non_empty_style(tmp_path: Path, monkeypatch) -> None:
    zpath = _titled_zip(tmp_path, ["1_Alpha-Topic"])
    monkeypatch.setattr(
        gary_act, "download_export", lambda url, *, output_dir, filename: str(zpath)
    )
    client = FakeGammaClient()

    with pytest.raises(gary_act.GaryActError) as exc_info:
        gary_act.generate_gamma_variants(
            {
                "slides": [{"slide_id": "s1", "title": "Alpha Topic"}],
                "export_dir": str(tmp_path),
                "gamma_settings": [{"variant_id": "A", "image_style_preset": "custom"}],
            },
            client=client,
        )

    assert exc_info.value.tag == "gamma.settings.invalid"
    assert client.generate_calls == []


def test_gary_keywords_must_be_a_list_before_generation(tmp_path: Path, monkeypatch) -> None:
    zpath = _titled_zip(tmp_path, ["1_Alpha-Topic"])
    monkeypatch.setattr(
        gary_act, "download_export", lambda url, *, output_dir, filename: str(zpath)
    )
    client = FakeGammaClient()

    with pytest.raises(gary_act.GaryActError) as exc_info:
        gary_act.generate_gamma_variants(
            {
                "slides": [{"slide_id": "s1", "title": "Alpha Topic"}],
                "export_dir": str(tmp_path),
                "gamma_settings": [{"variant_id": "A", "keywords": "blueprint"}],
            },
            client=client,
        )

    assert exc_info.value.tag == "gamma.settings.invalid"
    assert client.generate_calls == []


def test_gary_control_layer_emits_named_style_preset_without_style(
    tmp_path: Path, monkeypatch
) -> None:
    zpath = _titled_zip(tmp_path, ["1_Alpha-Topic"])
    monkeypatch.setattr(
        gary_act, "download_export", lambda url, *, output_dir, filename: str(zpath)
    )
    client = FakeGammaClient()

    gary_act.generate_gamma_variants(
        {
            "slides": [{"slide_id": "s1", "title": "Alpha Topic"}],
            "export_dir": str(tmp_path),
            "gamma_settings": [
                {
                    "variant_id": "A",
                    "image_style_preset": "illustration",
                    "image_style": "ignored named tile prompt",
                    "amount": "brief",
                    "audience": "Faculty",
                    "language": "en",
                    "image_source": "aiGenerated",
                    "dimensions": "16x9",
                }
            ],
        },
        client=client,
    )

    call = client.generate_calls[0]
    assert call["image_options"] == {
        "source": "aiGenerated",
        "stylePreset": "illustration",
    }
    assert "style" not in call["image_options"]
    assert call["text_options"] == {
        "amount": "brief",
        "audience": "Faculty",
        "language": "en",
        "tone": "Clear, professional, engaging in American English",
    }
    assert call["card_options"] == {"dimensions": "16x9"}


def test_gary_control_layer_emits_custom_style_without_style_preset(
    tmp_path: Path, monkeypatch
) -> None:
    zpath = _titled_zip(tmp_path, ["1_Alpha-Topic"])
    monkeypatch.setattr(
        gary_act, "download_export", lambda url, *, output_dir, filename: str(zpath)
    )
    client = FakeGammaClient()

    gary_act.generate_gamma_variants(
        {
            "slides": [{"slide_id": "s1", "title": "Alpha Topic"}],
            "export_dir": str(tmp_path),
            "gamma_settings": [
                {
                    "variant_id": "A",
                    "image_style_preset": "custom",
                    "image_style": "Clean black ink blueprint lines.",
                }
            ],
        },
        client=client,
    )

    assert client.generate_calls[0]["image_options"]["stylePreset"] == "custom"
    assert client.generate_calls[0]["image_options"]["style"] == (
        "Clean black ink blueprint lines."
    )


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


# --- 16:9 down-payment (party-ratified: Gamma Styleguide Library consensus) -----
# Bug (root cause, verified): build_gary_briefs never emits a `gamma_settings`
# key, so `_normalized_gamma_settings` returns [] and a DEFAULT orchestrator run
# sent NO cardOptions -> Gamma fell back to its non-16:9 default -> slides reached
# Descript title-cropped. Fix: EVERY Classic dispatch carries
# cardOptions.dimensions, defaulting to "16x9" unless a variant overrides it.


def test_gary_default_classic_dispatch_omits_forced_16x9_dimensions(
    tmp_path: Path, monkeypatch
) -> None:
    """Leg-A override removal (AC#4): a DEFAULT Classic run (no gamma_settings) must
    NOT force cardOptions={"dimensions": "16x9"}. The styleguide library's resolved
    dimensions is the sole determinant; with no styleguide/variant dimensions, no
    card_options is sent (the unconditional 16:9 down-payment is gone)."""
    zpath = _titled_zip(tmp_path, ["1_Only-Topic-Here"])
    monkeypatch.setattr(
        gary_act, "download_export", lambda url, *, output_dir, filename: str(zpath)
    )
    client = FakeGammaClient()

    gary_act.generate_gamma_variants(
        {"slides": [{"slide_id": "s1", "title": "Only Topic Here"}], "export_dir": str(tmp_path)},
        client=client,
    )

    assert "card_options" not in client.generate_calls[0]


def test_gary_per_variant_dimensions_override_wins_over_16x9_default(
    tmp_path: Path, monkeypatch
) -> None:
    """An explicit per-variant `dimensions` drives cardOptions directly (A -> 4x3),
    now that the baked-in 16:9 override is gone. Only the named variant dispatches
    (styleguide-retire-default-variant-pair 2026-07-01) — no fixture-seeded B deck."""
    zpath = _titled_zip(tmp_path, ["1_Alpha-Topic"])
    monkeypatch.setattr(
        gary_act, "download_export", lambda url, *, output_dir, filename: str(zpath)
    )
    client = FakeGammaClient()

    gary_act.generate_gamma_variants(
        {
            "slides": [{"slide_id": "s1", "title": "Alpha Topic"}],
            "export_dir": str(tmp_path),
            "gamma_settings": [{"variant_id": "A", "dimensions": "4x3"}],
        },
        client=client,
    )

    # Variant A's explicit 4x3 override survives the default-fill.
    assert client.generate_calls[0]["card_options"] == {"dimensions": "4x3"}
    # Padding retired: naming only A dispatches only A.
    assert len(client.generate_calls) == 1


def test_gary_studio_path_unchanged_no_card_options(tmp_path: Path, monkeypatch) -> None:
    """Regression: the Studio (from-template) path is untouched by the 16:9
    down-payment — it dispatches via generate_from_template with NO cardOptions
    (Studio 16:9 stays enforced by the template + the aspect guard), and never
    touches the Classic generate_deck path."""
    repo = Path(__file__).resolve().parents[3]
    studio_png = (
        repo
        / "_bmad-output"
        / "implementation-artifacts"
        / "studio-mode-evidence"
        / "STUDIO-success-1-innovators-mindset.png"
    )
    assert studio_png.exists(), "real Studio fixture missing"
    monkeypatch.setattr(
        gary_act, "download_export", lambda url, *, output_dir, filename: str(studio_png)
    )

    class FakeStudioGammaClient(FakeGammaClient):
        def __init__(self) -> None:
            super().__init__()
            self.template_calls: list[dict[str, object]] = []

        def generate_from_template(
            self, template_id: str, prompt: str, export_as: str = "png"
        ) -> dict[str, object]:
            self.template_calls.append(
                {"template_id": template_id, "prompt": prompt, "export_as": export_as}
            )
            return {"generationId": f"studio-{len(self.template_calls)}"}

        def wait_for_generation(self, generation_id: str) -> dict[str, object]:
            return {"exportUrl": "https://example.invalid/studio.png"}

    client = FakeStudioGammaClient()

    gary_act.generate_gamma_variants(
        {
            "slides": [{"slide_id": "s1", "title": "Only Topic Here"}],
            "export_dir": str(tmp_path),
            # Both variants studio so no Classic deck dispatch occurs at all;
            # the assertion below then cleanly proves the Studio path carries
            # no cardOptions (a Classic B variant would itself carry 16x9).
            "gamma_settings": [
                {
                    "variant_id": "A",
                    "production_mode": "studio",
                    "studio_template_id": "g_nv5q4da69qiiu8q",
                },
                {
                    "variant_id": "B",
                    "production_mode": "studio",
                    "studio_template_id": "g_nv5q4da69qiiu8q",
                },
            ],
        },
        client=client,
    )

    # Studio dispatched via from-template (one per variant), NOT the Classic deck.
    assert len(client.template_calls) == 2
    # The Classic generate_deck (the only carrier of card_options) was never called
    # for the studio variant -> no cardOptions on the Studio path.
    assert client.generate_calls == []


def test_double_dispatch_with_single_named_variant_warns_but_dispatches_one(
    tmp_path: Path, monkeypatch, caplog
) -> None:
    """R3 (Edge Case Hunter SHOULD-FIX) [RED before fix]. When double_dispatch is
    requested BUT the explicit gamma_settings names <2 variants, the explicit list
    WINS (single-variant-binds-one is the story intent) — dispatch behavior is
    unchanged (exactly 1 call). But the contradiction must be SURFACED, not silent:
    a WARNING is emitted noting double_dispatch was requested yet only the named
    variant(s) dispatch."""
    import logging

    zpath = _titled_zip(tmp_path, ["1_Alpha-Topic"])
    monkeypatch.setattr(
        gary_act, "download_export", lambda url, *, output_dir, filename: str(zpath)
    )
    client = FakeGammaClient()

    with caplog.at_level(logging.WARNING, logger="app.specialists.gary._act"):
        result = gary_act.generate_gamma_variants(
            {
                "slides": [{"slide_id": "s1", "title": "Alpha Topic"}],
                "export_dir": str(tmp_path),
                "double_dispatch": True,
                "gamma_settings": [{"variant_id": "A", "image_style": "photographic"}],
            },
            client=client,
        )

    # Dispatch behavior UNCHANGED: explicit single-variant list wins, one call.
    assert result["calls_made"] == 1
    assert len(client.generate_calls) == 1
    # Contradiction surfaced.
    warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert any(
        "double_dispatch" in r.getMessage() for r in warnings
    ), "double_dispatch vs single-variant contradiction must WARN"


def test_double_dispatch_with_empty_gamma_settings_falls_to_ab_fallback(
    tmp_path: Path, monkeypatch
) -> None:
    """R4 (Acceptance Auditor) consumer companion — an EXPLICIT-EMPTY gamma_settings
    with double_dispatch=True composes with the A/B fallback (2 dispatches), proving
    explicit-empty is documented compose-with-fallback behavior, NOT zero-dispatch."""
    zpath = _titled_zip(tmp_path, ["1_Alpha-Topic", "2_Beta-Topic"])
    monkeypatch.setattr(
        gary_act, "download_export", lambda url, *, output_dir, filename: str(zpath)
    )
    client = FakeGammaClient()

    result = gary_act.generate_gamma_variants(
        {
            "slides": [
                {"slide_id": "s1", "title": "Alpha Topic"},
                {"slide_id": "s2", "title": "Beta Topic"},
            ],
            "export_dir": str(tmp_path),
            "gamma_settings": [],
            "double_dispatch": True,
        },
        client=client,
    )

    assert result["calls_made"] == 2
    assert {row["dispatch_variant"] for row in result["gary_slide_output"]} == {"A", "B"}


def test_variant_a_text_mode_preserve_l1_fidelity() -> None:
    """Fidelity L1 (party 4/4 + Dr. Quinn synthesis 2026-06-24): variant A must use
    text_mode=preserve so Gamma cannot re-mint source numbers ($5.2T->$4.5T). Both
    variants now preserve source text; A/B distinctness is theme + imagery, not prose.
    """
    variant_a = dict(gary_act.DEFAULT_VARIANT_PAIR[0])
    variant_b = dict(gary_act.DEFAULT_VARIANT_PAIR[1])
    assert variant_a["variant_id"] == "A"
    assert variant_a["text_mode"] == "preserve"
    assert variant_b["text_mode"] == "preserve"
    # A/B differentiation survives: different theme + image style.
    assert variant_a["theme"] != variant_b["theme"]
    assert variant_a["image_style_preset"] != variant_b["image_style_preset"]
