from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from app.specialists.gary import _act as gary_act

from ._s4_seed import install_seed_resolver, seed_name


@pytest.fixture(autouse=True)
def _s4_seed(monkeypatch: pytest.MonkeyPatch) -> None:
    # Canonical-arc S4: a NAMED variant must be styleguide-bound (styleguide-less
    # now fails loud, Flip A). Tests below that name a variant bind it to the
    # byte-identical seed (see ._s4_seed) so the merged dispatch packet is
    # IDENTICAL to the pre-S4 styleguide-less seed path — the enum/theme/packet
    # surface under test is preserved, not weakened. Tests with no gamma_settings
    # (default-A path) are unaffected; a test with its OWN resolver monkeypatch
    # overrides this one in its body.
    #
    # R6 (NIT) — WARNING TO FUTURE AUTHORS: this fixture is AUTOUSE and blankets
    # ``resolve_styleguide`` module-wide via ``seed_name(vid)`` mappings. A NEW
    # test added to THIS file that wants to exercise the Flip-A fail-loud path
    # (a styleguide-less named variant) would be SILENTLY coerced onto the seed
    # path and NEVER raise ``gamma.styleguide.unbound``. To assert Flip A, either
    # give the variant a name NOT in the seed table (so ``resolve_styleguide``
    # KeyErrors — not what you want) or, correctly, write that test in
    # ``test_styleguide_fail_loud_flip.py`` (no autouse seed) instead of here.
    install_seed_resolver(monkeypatch)

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
                "styleguide": seed_name("A"),
                "theme": "theme-photo",
                "template": "template-smoke",
                "image_style": "photographic",
                "density": "balanced",
                "tone": "professional",
            },
            {
                "variant_id": "B",
                "styleguide": seed_name("B"),
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
    # ``styleguide`` is a BINDING directive, not a dispatch setting — it is
    # consumed by the resolver and never carried into the merged packet, so it
    # is excluded from the per-variant subset witness (S4).
    def _dispatch_keys(entry: dict) -> dict:
        return {k: v for k, v in entry.items() if k != "styleguide"}

    assert result["variant_gamma_settings"][0] | _dispatch_keys(
        payload["gamma_settings"][0]
    ) == result["variant_gamma_settings"][0]
    assert result["variant_gamma_settings"][1] | _dispatch_keys(
        payload["gamma_settings"][1]
    ) == result["variant_gamma_settings"][1]
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
            "gamma_settings": [
                {"variant_id": "A", "styleguide": seed_name("A"), "image_style": "photographic"}
            ],
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
            "gamma_settings": [
                {"variant_id": "A", "styleguide": seed_name("A"), "theme": "Photo"}
            ],
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
                "gamma_settings": [
                    {
                        "variant_id": "A",
                        "styleguide": seed_name("A"),
                        "theme": "theme-real-looking-absent",
                    }
                ],
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
                "gamma_settings": [
                    {"variant_id": "A", "styleguide": seed_name("A"), "amount": "minimalish"}
                ],
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
                "gamma_settings": [
                    {"variant_id": "A", "styleguide": seed_name("A"), key: value}
                ],
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
                "gamma_settings": [
                    {
                        "variant_id": "A",
                        "styleguide": seed_name("A"),
                        "image_style_preset": "custom",
                    }
                ],
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
                "gamma_settings": [
                    {"variant_id": "A", "styleguide": seed_name("A"), "keywords": "blueprint"}
                ],
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
                    "styleguide": seed_name("A"),
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
                    "styleguide": seed_name("A"),
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
            "gamma_settings": [
                {"variant_id": "A", "styleguide": seed_name("A"), "dimensions": "4x3"}
            ],
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
            self, template_id: str, prompt: str, export_as: str = "png", **kwargs: object
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
                    "styleguide": seed_name("A"),
                    "production_mode": "studio",
                    "studio_template_id": "g_nv5q4da69qiiu8q",
                },
                {
                    "variant_id": "B",
                    "styleguide": seed_name("B"),
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
                "gamma_settings": [
                    {"variant_id": "A", "styleguide": seed_name("A"), "image_style": "photographic"}
                ],
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


def test_style_additional_instructions_reaches_generation_kwargs(
    tmp_path: Path, monkeypatch
) -> None:
    """AC-7 (wire-level, NO live render): a style's ``additional_instructions``
    reaches ``generation_kwargs['additional_instructions']`` as its own concatenated
    part — style-FIRST, alongside the per-deck source-derived instructions, Gary's
    card rule, the keywords imagery, and the variant tail. Uses a SYNTHETIC resolved
    style (monkeypatched resolver) — no SSOT edit, no live call, no credit spend.
    """
    zpath = _titled_zip(tmp_path, ["1_Economic-Reality", "2_Leadership-Gap"])
    monkeypatch.setattr(
        gary_act, "download_export", lambda url, *, output_dir, filename: str(zpath)
    )
    synthetic = {
        "production_mode": "api",
        "theme": "njim9kuhfnljvaa",
        "text_mode": "condense",
        "image_source": "aiGenerated",
        "image_style_preset": "illustration",
        "dimensions": "fluid",
        "keywords": ["vector", "minimalist"],
        "additional_instructions": ["ZZ_STYLE_REGISTER_ZZ keep a calm clinical register."],
    }
    # S3 read-once seam: the fake accepts the resolver's `guides=` kwarg
    # (harness signature extension only — assertions untouched).
    monkeypatch.setattr(gary_act, "resolve_styleguide", lambda name, **_kw: dict(synthetic))
    client = FakeGammaClient()
    payload = {
        "slides": [
            {"slide_id": "s1", "title": "Economic Reality", "prompt": "Economic Reality — explain"},
            {"slide_id": "s2", "title": "Leadership Gap", "prompt": "Leadership Gap — explain"},
        ],
        "additional_instructions": "ZZ_PAYLOAD_SOURCE_ZZ per-deck source detail.",
        "gamma_settings": [{"variant_id": "A", "styleguide": "synthetic-guide"}],
        "export_dir": str(tmp_path),
    }

    gary_act.generate_gamma_variants(payload, client=client)

    ai = str(client.generate_calls[0]["additional_instructions"])
    # The style register and the per-deck source-derived instructions BOTH survive.
    assert "ZZ_STYLE_REGISTER_ZZ" in ai
    assert "ZZ_PAYLOAD_SOURCE_ZZ" in ai
    # Style-first: the persistent register precedes the per-deck source-derived block
    # (which thus stays intact and wins on specificity by coming after).
    assert ai.index("ZZ_STYLE_REGISTER_ZZ") < ai.index("ZZ_PAYLOAD_SOURCE_ZZ")
    # Nothing else dropped.
    assert "Emphasize this imagery: vector, minimalist." in ai
    assert "verbatim" in ai
    assert ai.rstrip().endswith("Variant A.")


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


def test_standard_a_crossroads_classic_text_mode_preserve_l1() -> None:
    """Fidelity L1 (operator 2026-07-09): approved classic stays condense; the named
    sibling hil-2026-apc-crossroads-classic-preserve carries preserve. Never mutate
    an approved registry guide ad hoc (trial 62308889 figure-contradiction).
    """
    from app.styleguide.resolver import resolve_styleguide

    classic = resolve_styleguide("hil-2026-apc-crossroads-classic")
    assert classic["text_mode"] == "condense"
    assert classic.get("amount") in {"minimal", "brief"}  # UI→API may translate

    preserve = resolve_styleguide("hil-2026-apc-crossroads-classic-preserve")
    assert preserve["text_mode"] == "preserve"
    assert not preserve.get("amount") or preserve.get("amount") in {None, "", "default"}
    # Identical visual triad except text mode.
    assert classic["theme"] == preserve["theme"]
    assert classic["image_model"] == preserve["image_model"]
    assert classic["image_style_preset"] == preserve["image_style_preset"]
    assert classic["dimensions"] == preserve["dimensions"]


# ---------------------------------------------------------------------------
# Irene literal-text supersedes styleguide truncation (T3–T8)
# Spec: _bmad-output/implementation-artifacts/spec-irene-literal-supersedes-styleguide-truncation.md
# ---------------------------------------------------------------------------


def _condense_minimal_gamma_settings(*variant_ids: str) -> list[dict[str, str]]:
    """Classic condense + Minimal (UI) — the S8 figure-contradiction failure mode."""
    return [
        {
            "variant_id": vid,
            "styleguide": seed_name(vid),
            "text_mode": "condense",
            "amount": "minimal",
        }
        for vid in variant_ids
    ]


def _download_by_call_index(monkeypatch, client: FakeGammaClient, zips: list[Path]) -> None:
    """Map the Nth generate_deck call to the Nth titled zip (cohort-split live seam)."""

    def _download(url: str, *, output_dir: Path, filename: str) -> str:
        idx = len(client.generate_calls) - 1
        return str(zips[idx])

    monkeypatch.setattr(gary_act, "download_export", _download)


def test_all_creative_styleguide_text_mode_amount_unchanged(tmp_path: Path, monkeypatch) -> None:
    """T3 — untagged/creative deck keeps styleguide condense + amount (no preserve bleed)."""
    zpath = _titled_zip(tmp_path, ["1_Creative-One", "2_Creative-Two"])
    monkeypatch.setattr(
        gary_act, "download_export", lambda url, *, output_dir, filename: str(zpath)
    )
    client = FakeGammaClient()
    payload = {
        "slides": [
            {"slide_id": "s1", "title": "Creative One", "fidelity": "creative"},
            {"slide_id": "s2", "title": "Creative Two"},  # missing → creative
        ],
        "export_dir": str(tmp_path),
        "gamma_settings": _condense_minimal_gamma_settings("A"),
    }

    gary_act.generate_gamma_variants(payload, client=client)

    assert len(client.generate_calls) == 1
    call = client.generate_calls[0]
    assert call["text_mode"] == "condense"
    text_options = call.get("text_options") or {}
    assert "amount" in text_options
    assert text_options["amount"] == "brief"  # Minimal UI → brief API
    assert call["num_cards"] == 2


def test_literal_cohort_force_preserve_amount_key_absent(tmp_path: Path, monkeypatch) -> None:
    """T4 — S8 figure-contradiction pin: literal + condense+Minimal → preserve, amount absent."""
    zpath = _titled_zip(tmp_path, ["1_Figure-Critical", "2_Literal-Visual-Card"])
    monkeypatch.setattr(
        gary_act, "download_export", lambda url, *, output_dir, filename: str(zpath)
    )
    client = FakeGammaClient()
    payload = {
        "slides": [
            {
                "slide_id": "s1",
                "title": "Figure Critical",
                "fidelity": "literal-text",
                "prompt": "Teaching-critical: spend reached $5.2 trillion.",
            },
            {
                "slide_id": "s2",
                "title": "Literal Visual Card",
                "fidelity": "literal-visual",
                "prompt": "Keep this SME figure caption verbatim.",
            },
        ],
        "export_dir": str(tmp_path),
        "gamma_settings": _condense_minimal_gamma_settings("A"),
    }

    gary_act.generate_gamma_variants(payload, client=client)

    assert len(client.generate_calls) == 1
    call = client.generate_calls[0]
    assert call["text_mode"] == "preserve"
    text_options = call.get("text_options") or {}
    assert "amount" not in text_options
    assert call["num_cards"] == 2


def test_mixed_deck_splits_and_rejoins_brief_order_by_slide_id(
    tmp_path: Path, monkeypatch
) -> None:
    """T5 — mixed deck: cohort-scoped calls; rejoin by slide_id (titles collide on purpose)."""
    (tmp_path / "creative").mkdir()
    (tmp_path / "literal").mkdir()
    creative_zip = _titled_zip(tmp_path / "creative", ["1_Shared-Title"])
    literal_zip = _titled_zip(tmp_path / "literal", ["1_Shared-Title"])
    client = FakeGammaClient()
    _download_by_call_index(monkeypatch, client, [creative_zip, literal_zip])

    payload = {
        "slides": [
            {
                "slide_id": "s1",
                "title": "Shared Title",
                "fidelity": "creative",
                "prompt": "Creative body one",
            },
            {
                "slide_id": "s2",
                "title": "Shared Title",
                "fidelity": "literal-text",
                "prompt": "Literal body $5.2T teaching-critical",
            },
        ],
        "export_dir": str(tmp_path),
        "gamma_settings": _condense_minimal_gamma_settings("A"),
    }

    result = gary_act.generate_gamma_variants(payload, client=client)

    assert len(client.generate_calls) == 2
    creative_call, literal_call = client.generate_calls
    assert creative_call["num_cards"] == 1
    assert literal_call["num_cards"] == 1
    assert creative_call["text_mode"] == "condense"
    assert "amount" in (creative_call.get("text_options") or {})
    assert literal_call["text_mode"] == "preserve"
    assert "amount" not in (literal_call.get("text_options") or {})
    # Cohort-scoped input: each call's prompt contains only its cohort title chunk once.
    assert str(creative_call["input_text"]).count("# Shared Title") == 1
    assert str(literal_call["input_text"]).count("# Shared Title") == 1
    assert "Creative body one" in str(creative_call["input_text"])
    assert "$5.2T" in str(literal_call["input_text"])
    assert "Creative body one" not in str(literal_call["input_text"])
    assert "$5.2T" not in str(creative_call["input_text"])

    rows = {row["slide_id"]: row for row in result["gary_slide_output"]}
    assert list(row["slide_id"] for row in result["gary_slide_output"]) == ["s1", "s2"]
    assert Path(rows["s1"]["file_path"]).read_bytes() == b"bytes::1_Shared-Title"
    assert Path(rows["s2"]["file_path"]).read_bytes() == b"bytes::1_Shared-Title"
    # Distinct export dirs prove each cohort bound its own page (not a single shared file).
    assert Path(rows["s1"]["file_path"]).resolve() != Path(rows["s2"]["file_path"]).resolve()


def test_literal_island_does_not_smear_neighbors(tmp_path: Path, monkeypatch) -> None:
    """T6 — literal island amid creative: preserve does not smear to neighbors."""
    (tmp_path / "c1").mkdir()
    (tmp_path / "lit").mkdir()
    (tmp_path / "c2").mkdir()
    # Binary cohorts → two calls (all creative together, all literal together), not three.
    creative_zip = _titled_zip(tmp_path / "c1", ["1_Alpha-Edge", "2_Gamma-Edge"])
    literal_zip = _titled_zip(tmp_path / "lit", ["1_Beta-Literal"])
    client = FakeGammaClient()
    _download_by_call_index(monkeypatch, client, [creative_zip, literal_zip])

    payload = {
        "slides": [
            {"slide_id": "s1", "title": "Alpha Edge", "fidelity": "creative", "prompt": "A"},
            {
                "slide_id": "s2",
                "title": "Beta Literal",
                "fidelity": "literal-text",
                "prompt": "KEEP VERBATIM",
            },
            {"slide_id": "s3", "title": "Gamma Edge", "fidelity": "creative", "prompt": "C"},
        ],
        "export_dir": str(tmp_path),
        "gamma_settings": _condense_minimal_gamma_settings("A"),
    }

    result = gary_act.generate_gamma_variants(payload, client=client)

    assert len(client.generate_calls) == 2
    creative_call = next(c for c in client.generate_calls if c["text_mode"] == "condense")
    literal_call = next(c for c in client.generate_calls if c["text_mode"] == "preserve")
    assert creative_call["num_cards"] == 2
    assert literal_call["num_cards"] == 1
    assert "KEEP VERBATIM" in str(literal_call["input_text"])
    assert "KEEP VERBATIM" not in str(creative_call["input_text"])
    assert "Alpha Edge" in str(creative_call["input_text"])
    assert "Gamma Edge" in str(creative_call["input_text"])
    assert "Alpha Edge" not in str(literal_call["input_text"])
    assert list(row["slide_id"] for row in result["gary_slide_output"]) == ["s1", "s2", "s3"]


def test_ab_double_dispatch_times_fidelity_cohorts(tmp_path: Path, monkeypatch) -> None:
    """T7 — double_dispatch × mixed fidelity → len(generate_calls) == variants × cohorts."""
    for name in ("a_c", "a_l", "b_c", "b_l"):
        (tmp_path / name).mkdir()
    zips = [
        _titled_zip(tmp_path / "a_c", ["1_Creative-Slide"]),
        _titled_zip(tmp_path / "a_l", ["1_Literal-Slide"]),
        _titled_zip(tmp_path / "b_c", ["1_Creative-Slide"]),
        _titled_zip(tmp_path / "b_l", ["1_Literal-Slide"]),
    ]
    client = FakeGammaClient()
    _download_by_call_index(monkeypatch, client, zips)

    payload = {
        "slides": [
            {"slide_id": "s1", "title": "Creative Slide", "fidelity": "creative"},
            {"slide_id": "s2", "title": "Literal Slide", "fidelity": "literal-text"},
        ],
        "export_dir": str(tmp_path),
        "double_dispatch": True,
        "gamma_settings": _condense_minimal_gamma_settings("A", "B"),
    }

    result = gary_act.generate_gamma_variants(payload, client=client)

    assert len(client.generate_calls) == 4  # 2 variants × 2 cohorts
    assert result["calls_made"] == 4
    preserve_calls = [c for c in client.generate_calls if c.get("text_mode") == "preserve"]
    condense_calls = [c for c in client.generate_calls if c.get("text_mode") == "condense"]
    assert len(preserve_calls) == 2
    assert len(condense_calls) == 2
    for call in preserve_calls:
        assert "amount" not in (call.get("text_options") or {})
    for call in condense_calls:
        assert "amount" in (call.get("text_options") or {})


def test_literal_honor_failure_raises_no_condense_fallback(
    tmp_path: Path, monkeypatch
) -> None:
    """T8 — studio + literal cannot honor preserve → raise; no Classic condense fallback."""
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
            self, template_id: str, prompt: str, export_as: str = "png", **kwargs: object
        ) -> dict[str, object]:
            self.template_calls.append(
                {"template_id": template_id, "prompt": prompt, "export_as": export_as}
            )
            return {"generationId": f"studio-{len(self.template_calls)}"}

        def wait_for_generation(self, generation_id: str) -> dict[str, object]:
            return {"exportUrl": "https://example.invalid/studio.png"}

    client = FakeStudioGammaClient()

    with pytest.raises(gary_act.GaryActError) as excinfo:
        gary_act.generate_gamma_variants(
            {
                "slides": [
                    {
                        "slide_id": "s1",
                        "title": "Literal Studio Conflict",
                        "fidelity": "literal-text",
                        "prompt": "Must preserve verbatim",
                    }
                ],
                "export_dir": str(tmp_path),
                "gamma_settings": [
                    {
                        "variant_id": "A",
                        "styleguide": seed_name("A"),
                        "production_mode": "studio",
                        "studio_template_id": "g_nv5q4da69qiiu8q",
                    }
                ],
            },
            client=client,
        )

    assert "literal" in str(excinfo.value).lower() or "preserve" in str(excinfo.value).lower()
    assert excinfo.value.tag == "gamma.fidelity.literal-honor-failure"
    # No silent Classic condense fallback, and Studio must not proceed either.
    assert client.generate_calls == []
    assert client.template_calls == []
