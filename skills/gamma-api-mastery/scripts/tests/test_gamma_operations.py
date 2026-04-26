"""Tests for gamma_operations module."""

from __future__ import annotations

import logging
import sys
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_PROJECT_ROOT = str(Path(__file__).resolve().parents[4])
sys.path.insert(0, _PROJECT_ROOT)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import gamma_operations  # noqa: E402
from gamma_operations import (  # noqa: E402
    download_export,
    execute_generation,
    generate_deck_mixed_fidelity,
    generate_from_template,
    generate_slide,
    list_style_presets,
    list_themes_and_templates,
    load_style_guide_gamma,
    load_style_preset,
    merge_parameters,
    merge_slide_content,
    normalize_slides_payload,
    publish_preintegration_literal_visuals,
    resolve_style_preset,
    validate_dispatch_ready,
    validate_outbound_contract,
    validate_theme_mapping_handshake,
)


def _valid_theme_resolution() -> dict[str, object]:
    return {
        "requested_theme_key": "hil-2026-apc-nejal-A",
        "resolved_theme_key": "theme_abc",
        "resolved_parameter_set": "hil-2026-apc-nejal-A",
        "mapping_source": "state/config/gamma-style-presets.yaml",
        "mapping_version": "1",
        "user_confirmation": True,
    }


class TestLoadStyleGuideGamma:
    """Tests for style guide loading."""

    def test_returns_empty_when_file_missing(self, tmp_path: Path) -> None:
        with patch.object(
            gamma_operations, "STYLE_GUIDE_PATH",
            tmp_path / "nonexistent.yaml",
        ):
            result = load_style_guide_gamma()
        assert result == {}

    def test_returns_gamma_section(self, tmp_path: Path) -> None:
        style_file = tmp_path / "style_guide.yaml"
        style_file.write_text(
            "tool_parameters:\n  gamma:\n    default_llm: gpt-4o\n    style: medical\n"
        )
        with patch.object(
            gamma_operations, "STYLE_GUIDE_PATH",
            style_file,
        ):
            result = load_style_guide_gamma()
        assert result["default_llm"] == "gpt-4o"
        assert result["style"] == "medical"

    def test_returns_empty_when_no_gamma_section(self, tmp_path: Path) -> None:
        style_file = tmp_path / "style_guide.yaml"
        style_file.write_text("tool_parameters:\n  elevenlabs:\n    voice: Roger\n")
        with patch.object(
            gamma_operations, "STYLE_GUIDE_PATH",
            style_file,
        ):
            result = load_style_guide_gamma()
        assert result == {}


class TestMergeParameters:
    """Tests for parameter cascade merge."""

    def test_later_sources_override_earlier(self) -> None:
        result = merge_parameters(
            {"format": "document", "numCards": 5},
            {"format": "presentation"},
            {"numCards": 1},
        )
        assert result["format"] == "presentation"
        assert result["numCards"] == 1

    def test_empty_values_do_not_override(self) -> None:
        result = merge_parameters(
            {"format": "presentation"},
            {"format": ""},
            {},
        )
        assert result["format"] == "presentation"

    def test_none_values_do_not_override(self) -> None:
        result = merge_parameters(
            {"themeId": "abc123"},
            {"themeId": None},
            {},
        )
        assert result["themeId"] == "abc123"

    def test_all_sources_contribute(self) -> None:
        result = merge_parameters(
            {"format": "presentation"},
            {"numCards": 1},
            {"exportAs": "pdf"},
        )
        assert result == {"format": "presentation", "numCards": 1, "exportAs": "pdf"}


class TestNormalizeSlidesPayload:
    def test_accepts_list_payload_unchanged_when_complete(self) -> None:
        payload = [
            {
                "slide_number": 1,
                "fidelity": "creative",
                "content": "Slide 1 content",
                "source_ref": "extracted.md#Page 1",
            }
        ]
        result = normalize_slides_payload(payload)
        assert len(result) == 1
        assert result[0]["content"] == "Slide 1 content"
        assert result[0]["source_ref"] == "extracted.md#Page 1"

    def test_accepts_object_with_slides_and_derives_source_ref(self) -> None:
        payload = {
            "run_id": "R1",
            "slides": [
                {
                    "slide_number": 2,
                    "fidelity": "literal-text",
                    "source_anchors": ["extracted.md#Page 2", "extracted.md#Page 3"],
                }
            ],
        }
        with pytest.raises(ValueError, match="Slides payload missing required content"):
            normalize_slides_payload(payload)

    def test_allows_placeholders_only_with_explicit_debug_override(self) -> None:
        payload = {
            "slides": [
                {
                    "slide_number": 2,
                    "fidelity": "literal-text",
                    "source_anchors": ["extracted.md#Page 2", "extracted.md#Page 3"],
                }
            ]
        }
        result = normalize_slides_payload(payload, allow_placeholder_content=True)
        assert len(result) == 1
        assert result[0]["source_ref"] == "extracted.md#Page 2; extracted.md#Page 3"
        assert "placeholder derived from pre-dispatch artifacts" in result[0]["content"]

    def test_invalid_payload_raises(self) -> None:
        with pytest.raises(ValueError, match="Expected list or object with 'slides' array"):
            normalize_slides_payload({"slides": "not-a-list"})


class TestMergeSlideContent:
    def test_merges_content_rows_into_fidelity_rows(self) -> None:
        fidelity_payload = {
            "slides": [
                {
                    "slide_number": 1,
                    "fidelity": "creative",
                    "source_anchors": ["extracted.md#Page 1"],
                },
                {
                    "slide_number": 2,
                    "fidelity": "literal-text",
                    "source_anchors": ["extracted.md#Page 2"],
                },
            ]
        }
        content_payload = {
            "slides": [
                {
                    "slide_number": 1,
                    "content": "Creative content",
                    "source_ref": "extracted.md#Page 1",
                },
                {
                    "slide_number": 2,
                    "content": "Literal content",
                    "source_ref": "extracted.md#Page 2",
                },
            ]
        }

        merged = merge_slide_content(fidelity_payload, content_payload)

        assert len(merged) == 2
        assert merged[0]["fidelity"] == "creative"
        assert merged[0]["content"] == "Creative content"
        assert merged[1]["fidelity"] == "literal-text"
        assert merged[1]["content"] == "Literal content"
        assert "placeholder derived from pre-dispatch artifacts" not in merged[1]["content"]

    def test_missing_content_in_merged_payload_fails_without_debug_override(self) -> None:
        fidelity_payload = {
            "slides": [
                {
                    "slide_number": 1,
                    "fidelity": "creative",
                    "source_anchors": ["extracted.md#Page 1"],
                }
            ]
        }
        content_payload = {"slides": []}

        with pytest.raises(ValueError, match="Slides payload missing required content"):
            merge_slide_content(fidelity_payload, content_payload)


class TestGenerateSlide:
    """Tests for text-based generation."""

    def test_calls_client_with_correct_params(self) -> None:
        mock_client = MagicMock()
        mock_client.generate.return_value = {"id": "gen-123"}
        mock_client.wait_for_generation.return_value = {
            "id": "gen-123",
            "status": "completed",
            "gammaUrl": "https://gamma.app/docs/gen-123",
        }

        params = {
            "input_text": "Test content",
            "text_mode": "preserve",
            "format": "presentation",
            "num_cards": 1,
            "export_as": "pdf",
        }
        result = generate_slide(params, client=mock_client)

        mock_client.generate.assert_called_once_with(
            "Test content",
            "preserve",
            format="presentation",
            num_cards=1,
            export_as="pdf",
        )
        mock_client.wait_for_generation.assert_called_once_with("gen-123")
        assert result["status"] == "completed"

    def test_log_includes_run_id_when_provided(self, caplog: pytest.LogCaptureFixture) -> None:
        mock_client = MagicMock()
        mock_client.generate.return_value = {"id": "gen-runid"}
        mock_client.wait_for_generation.return_value = {"id": "gen-runid", "status": "completed"}
        params = {"input_text": "x", "text_mode": "generate"}
        with caplog.at_level(logging.INFO, logger="gamma_operations"):
            generate_slide(params, client=mock_client, run_id="RUN-ABC-99")
        assert any("RUN-ABC-99" in r.message for r in caplog.records)
        assert any("generation_id=" in r.message for r in caplog.records)

    def test_handles_camelcase_params(self) -> None:
        mock_client = MagicMock()
        mock_client.generate.return_value = {"id": "gen-456"}
        mock_client.wait_for_generation.return_value = {"status": "completed"}

        params = {
            "inputText": "CamelCase input",
            "textMode": "generate",
            "numCards": 3,
            "exportAs": "pptx",
        }
        generate_slide(params, client=mock_client)

        mock_client.generate.assert_called_once()
        call_args = mock_client.generate.call_args
        assert call_args[0][0] == "CamelCase input"
        assert call_args[0][1] == "generate"

    def test_strips_internal_image_option_helper_keys(self) -> None:
        mock_client = MagicMock()
        mock_client.generate.return_value = {"id": "gen-789"}
        mock_client.wait_for_generation.return_value = {"status": "completed"}

        params = {
            "input_text": "Deck content",
            "text_mode": "generate",
            "imageOptions": {
                "source": "aiGenerated",
                "model": "gemini-3.1-flash-image-mini",
                "stylePreset": "illustration",
                "_keywordsHint": "vector, minimalist",
                "referenceImagePath": "course-content/staging/ad-hoc/ref.png",
            },
            "additionalInstructions": "Keep style uniform.",
        }

        generate_slide(params, client=mock_client)

        _, kwargs = mock_client.generate.call_args
        image_options = kwargs["image_options"]
        assert "_keywordsHint" not in image_options
        assert "referenceImagePath" not in image_options
        assert image_options["source"] == "aiGenerated"
        assert image_options["model"] == "gemini-3.1-flash-image-mini"

    def test_promotes_keywords_hint_to_additional_instructions(self) -> None:
        mock_client = MagicMock()
        mock_client.generate.return_value = {"id": "gen-790"}
        mock_client.wait_for_generation.return_value = {"status": "completed"}

        params = {
            "input_text": "Deck content",
            "text_mode": "generate",
            "imageOptions": {
                "source": "aiGenerated",
                "_keywordsHint": "vector, minimalist",
            },
            "additionalInstructions": "Keep style uniform.",
        }

        generate_slide(params, client=mock_client)

        _, kwargs = mock_client.generate.call_args
        ai_text = kwargs["additional_instructions"]
        assert "Keep style uniform." in ai_text
        assert "Visual keyword cues: vector, minimalist." in ai_text


class TestGenerateFromTemplate:
    """Tests for template-based generation."""

    def test_calls_client_with_template_params(self) -> None:
        mock_client = MagicMock()
        mock_client.generate_from_template.return_value = {"id": "tpl-789"}
        mock_client.wait_for_generation.return_value = {"status": "completed"}

        result = generate_from_template(
            "gamma_abc123",
            "Replace content with clinical case",
            {"export_as": "pdf", "theme_id": "theme_xyz"},
            client=mock_client,
        )

        mock_client.generate_from_template.assert_called_once_with(
            "gamma_abc123",
            "Replace content with clinical case",
            theme_id="theme_xyz",
            export_as="pdf",
        )
        assert result["status"] == "completed"


class TestDownloadExport:
    """Tests for artifact download."""

    def test_downloads_to_specified_dir(self, tmp_path: Path) -> None:
        with patch.object(gamma_operations, "requests") as mock_req:
            mock_resp = MagicMock()
            mock_resp.content = b"PDF content here"
            mock_resp.raise_for_status = MagicMock()
            mock_req.get.return_value = mock_resp

            result = download_export(
                "https://example.com/export/slide.pdf?token=abc",
                output_dir=tmp_path,
                filename="test-slide.pdf",
            )

        assert result == tmp_path / "test-slide.pdf"
        assert result.read_bytes() == b"PDF content here"

    def test_auto_derives_filename(self, tmp_path: Path) -> None:
        with patch.object(gamma_operations, "requests") as mock_req:
            mock_resp = MagicMock()
            mock_resp.content = b"data"
            mock_resp.raise_for_status = MagicMock()
            mock_req.get.return_value = mock_resp

            result = download_export(
                "https://cdn.gamma.app/exports/my-deck.pdf?sig=xyz",
                output_dir=tmp_path,
            )

        assert result.name == "my-deck.pdf"


# ---------------------------------------------------------------------------
# Style Preset Tests
# ---------------------------------------------------------------------------

_SAMPLE_PRESETS_YAML = """\
presets:
  - name: hil-2026-apc-nejal-A
    description: HIL branded deck Approach A
    approach: A
    scope: "*"
    theme_id: njim9kuhfnljvaa
    theme_name: "2026 HIL APC Nejal"
    parameters:
      textMode: generate
      textOptions:
        amount: detailed
        language: en
      imageOptions:
        source: aiGenerated
        model: nano-banana-2-mini
        stylePreset: illustration
        keywords:
          - vector
          - minimalist
          - flat-color
      cardOptions:
        dimensions: "16x9"
      format: presentation
      formatVariant: classic
      numCards: 10
      additionalInstructions: "Keep the style of all the images uniform."
    provenance:
      source: exemplar-match
      established: "2026-03-27"
    version: 1
  - name: hil-2026-apc-nejal-B
    description: HIL branded deck Approach B
    approach: B
    scope: "*"
    theme_id: njim9kuhfnljvaa
    theme_name: "2026 HIL APC Nejal"
    parameters:
      textMode: generate
      imageOptions:
        source: aiGenerated
        model: flux-kontext-pro
        stylePreset: custom
        style: "Line drawing illustration. Clean black ink on white."
        keywords:
          - vector
          - minimalist
        referenceImagePath: "course-content/staging/ad-hoc/ref.png"
      numCards: 10
      additionalInstructions: "Keep the style of all the images uniform."
    provenance:
      source: gary-proposed
      established: "2026-03-27"
    version: 1
  - name: startup-bold
    description: Bold startup style
    approach: A
    scope: "C2"
    theme_id: theme_startup_xyz
    theme_name: "Startup Bold"
    parameters:
      textMode: generate
      imageOptions:
        source: aiGenerated
        model: flux-2-pro
        stylePreset: photorealistic
    provenance:
      source: user-defined
      established: "2026-03-28"
    version: 1
"""


def _write_presets(tmp_path: Path) -> Path:
    p = tmp_path / "gamma-style-presets.yaml"
    p.write_text(_SAMPLE_PRESETS_YAML, encoding="utf-8")
    return p


class TestListStylePresets:
    """Tests for listing style presets."""

    def test_returns_all_presets(self, tmp_path: Path) -> None:
        path = _write_presets(tmp_path)
        presets = list_style_presets(path=path)
        assert len(presets) == 3  # A, B, startup-bold

    def test_filters_by_scope_wildcard(self, tmp_path: Path) -> None:
        path = _write_presets(tmp_path)
        presets = list_style_presets(scope="C1", path=path)
        # Only wildcard presets match C1 (A and B are both scope="*")
        names = [p["name"] for p in presets]
        assert "hil-2026-apc-nejal-A" in names
        assert "hil-2026-apc-nejal-B" in names
        assert "startup-bold" not in names

    def test_filters_by_scope_exact(self, tmp_path: Path) -> None:
        path = _write_presets(tmp_path)
        presets = list_style_presets(scope="C2", path=path)
        # Wildcard (A + B) and C2 match
        assert len(presets) == 3

    def test_filters_by_scope_prefix(self, tmp_path: Path) -> None:
        path = _write_presets(tmp_path)
        presets = list_style_presets(scope="C2 > M1", path=path)
        # Wildcard (A + B) and C2 all match
        assert len(presets) == 3

    def test_returns_empty_when_file_missing(self, tmp_path: Path) -> None:
        presets = list_style_presets(path=tmp_path / "nonexistent.yaml")
        assert presets == []


class TestLoadStylePreset:
    """Tests for loading a single preset by name."""

    def test_loads_by_name(self, tmp_path: Path) -> None:
        path = _write_presets(tmp_path)
        params = load_style_preset("hil-2026-apc-nejal-A", path=path)
        assert params is not None
        assert params["textMode"] == "generate"
        assert params["imageOptions"]["model"] == "nano-banana-2-mini"

    def test_returns_none_for_unknown_name(self, tmp_path: Path) -> None:
        path = _write_presets(tmp_path)
        assert load_style_preset("nonexistent", path=path) is None


class TestResolveStylePreset:
    """Tests for multi-strategy preset resolution."""

    def test_resolve_by_name(self, tmp_path: Path) -> None:
        path = _write_presets(tmp_path)
        result = resolve_style_preset("startup-bold", path=path)
        assert result["textMode"] == "generate"
        assert result["imageOptions"]["model"] == "flux-2-pro"

    def test_resolve_by_theme_id_returns_first_match(self, tmp_path: Path) -> None:
        # Both A and B share the same theme_id; first in file wins
        path = _write_presets(tmp_path)
        result = resolve_style_preset(theme_id="njim9kuhfnljvaa", path=path)
        assert result["themeId"] == "njim9kuhfnljvaa"
        assert result["imageOptions"]["model"] == "nano-banana-2-mini"  # A comes first

    def test_resolve_by_scope_most_specific(self, tmp_path: Path) -> None:
        path = _write_presets(tmp_path)
        result = resolve_style_preset(scope="C2 > M1", path=path)
        # C2 is more specific than * for scope "C2 > M1"
        assert result["textMode"] == "generate"

    def test_resolve_returns_empty_when_no_match(self, tmp_path: Path) -> None:
        path = _write_presets(tmp_path)
        result = resolve_style_preset(name="totally-unknown", path=path)
        assert result == {}

    def test_resolve_returns_empty_when_file_missing(self, tmp_path: Path) -> None:
        result = resolve_style_preset(
            name="hil-2026-apc-nejal",
            path=tmp_path / "gone.yaml",
        )
        assert result == {}

    def test_flatten_includes_theme_id(self, tmp_path: Path) -> None:
        path = _write_presets(tmp_path)
        result = resolve_style_preset("hil-2026-apc-nejal-A", path=path)
        assert result["themeId"] == "njim9kuhfnljvaa"


class TestMergeParametersWithPreset:
    """Tests for the updated merge_parameters with style_preset layer."""

    def test_preset_overrides_style_guide(self) -> None:
        result = merge_parameters(
            {"textMode": "generate"},
            {},
            {},
            style_preset={"textMode": "condense"},
        )
        assert result["textMode"] == "condense"

    def test_content_template_overrides_preset(self) -> None:
        result = merge_parameters(
            {},
            {"textMode": "preserve"},
            {},
            style_preset={"textMode": "condense"},
        )
        assert result["textMode"] == "preserve"

    def test_envelope_overrides_all(self) -> None:
        result = merge_parameters(
            {"textMode": "generate"},
            {"textMode": "condense"},
            {"textMode": "preserve"},
            style_preset={"textMode": "condense"},
        )
        assert result["textMode"] == "preserve"

    def test_preset_contributes_new_keys(self) -> None:
        result = merge_parameters(
            {"format": "presentation"},
            {},
            {},
            style_preset={"imageOptions": {"model": "recraft-v3"}},
        )
        assert result["format"] == "presentation"
        assert result["imageOptions"]["model"] == "recraft-v3"

    def test_backward_compatible_without_preset(self) -> None:
        result = merge_parameters(
            {"format": "presentation"},
            {"numCards": 1},
            {"exportAs": "pdf"},
        )
        assert result == {"format": "presentation", "numCards": 1, "exportAs": "pdf"}


class TestFlattenPresetKeywords:
    """Tests for keyword handling in _flatten_preset_params."""

    def test_approach_a_keywords_become_hint(self, tmp_path: Path) -> None:
        """Approach A: keywords stored as _keywordsHint, not in style."""
        path = _write_presets(tmp_path)
        result = resolve_style_preset("hil-2026-apc-nejal-A", path=path)
        img = result["imageOptions"]
        # stylePreset preserved as named value
        assert img["stylePreset"] == "illustration"
        # keywords become hint, not appended to style
        assert "_keywordsHint" in img
        assert "vector" in img["_keywordsHint"]
        # no 'style' key sent (API ignores it for named stylePreset)
        assert "style" not in img
        # keywords list removed
        assert "keywords" not in img

    def test_approach_a_no_reference_image_path(self, tmp_path: Path) -> None:
        path = _write_presets(tmp_path)
        result = resolve_style_preset("hil-2026-apc-nejal-A", path=path)
        assert "referenceImagePath" not in result["imageOptions"]

    def test_approach_b_keywords_appended_to_style(self, tmp_path: Path) -> None:
        """Approach B: keywords appended to style prompt string."""
        path = _write_presets(tmp_path)
        result = resolve_style_preset("hil-2026-apc-nejal-B", path=path)
        img = result["imageOptions"]
        assert img["stylePreset"] == "custom"
        style = img["style"]
        assert "Line drawing" in style
        assert "vector" in style
        assert "minimalist" in style
        assert "keywords" not in img

    def test_approach_b_reference_image_path_preserved(self, tmp_path: Path) -> None:
        """Approach B: referenceImagePath kept for Gary to study."""
        path = _write_presets(tmp_path)
        result = resolve_style_preset("hil-2026-apc-nejal-B", path=path)
        assert "referenceImagePath" in result["imageOptions"]
        assert "ref.png" in result["imageOptions"]["referenceImagePath"]

    def test_approach_a_preset_includes_new_fields(self, tmp_path: Path) -> None:
        path = _write_presets(tmp_path)
        result = resolve_style_preset("hil-2026-apc-nejal-A", path=path)
        assert result["numCards"] == 10
        assert result["format"] == "presentation"
        assert result["formatVariant"] == "classic"
        assert "Keep the style" in result["additionalInstructions"]


class TestMergeAdditionalInstructionsConcatenation:
    """Tests for additionalInstructions concatenation across layers."""

    def test_preset_base_plus_content_type(self) -> None:
        result = merge_parameters(
            {},
            {"additionalInstructions": "One concept per card."},
            {},
            style_preset={"additionalInstructions": "Keep style uniform."},
        )
        ai = result["additionalInstructions"]
        assert "Keep style uniform." in ai
        assert "One concept per card." in ai
        # Preset comes before content template
        assert ai.index("Keep style uniform.") < ai.index("One concept per card.")

    def test_all_three_layers_concatenated(self) -> None:
        result = merge_parameters(
            {"additionalInstructions": "Base."},
            {"additionalInstructions": "Content-type."},
            {"additionalInstructions": "Envelope."},
            style_preset={"additionalInstructions": "Preset."},
        )
        ai = result["additionalInstructions"]
        assert ai == "Base. Preset. Content-type. Envelope."

    def test_empty_fragments_skipped(self) -> None:
        result = merge_parameters(
            {"additionalInstructions": ""},
            {},
            {"additionalInstructions": "Only this."},
            style_preset={"additionalInstructions": ""},
        )
        assert result["additionalInstructions"] == "Only this."

    def test_no_additional_instructions_anywhere(self) -> None:
        result = merge_parameters(
            {"format": "presentation"},
            {},
            {},
            style_preset={"textMode": "generate"},
        )
        assert "additionalInstructions" not in result

    def test_other_params_still_override(self) -> None:
        """Non-AI params still use last-wins, only AI concatenates."""
        result = merge_parameters(
            {"textMode": "preserve"},
            {"textMode": "condense"},
            {},
            style_preset={
                "textMode": "generate",
                "additionalInstructions": "Preset base.",
            },
        )
        # textMode: content template wins (later in cascade)
        assert result["textMode"] == "condense"
        # additionalInstructions: concatenated
        assert result["additionalInstructions"] == "Preset base."


class TestListThemesAndTemplates:
    """Tests for TP capability in gamma_operations."""

    def test_returns_themes_and_templates(self, tmp_path: Path) -> None:
        style_file = tmp_path / "style_guide.yaml"
        style_file.write_text(
            """
tool_parameters:
  gamma:
    templates:
      - name: C1 lesson template
        gamma_id: gamma_tpl_1
        scope: C1
        content_type: lecture-slides
      - name: Global fallback
        gamma_id: gamma_tpl_2
        scope: "*"
        content_type: "*"
""".strip(),
            encoding="utf-8",
        )

        mock_client = MagicMock()
        mock_client.list_themes.return_value = [{"id": "theme_abc", "name": "Theme A"}]

        result = list_themes_and_templates(
            scope="C1 > M1",
            content_type="lecture-slides",
            client=mock_client,
            style_guide_path=style_file,
        )

        assert len(result["themes"]) == 1
        assert len(result["templates"]) == 2
        names = [t.get("name") for t in result["templates"]]
        assert "C1 lesson template" in names
        assert "Global fallback" in names

    def test_api_failure_degrades_to_templates_only(self, tmp_path: Path) -> None:
        style_file = tmp_path / "style_guide.yaml"
        style_file.write_text(
            "tool_parameters:\n  gamma:\n    templates:\n      - name: fallback\n        gamma_id: t1\n        scope: '*'\n        content_type: '*'\n",
            encoding="utf-8",
        )
        mock_client = MagicMock()
        mock_client.list_themes.side_effect = RuntimeError("Gamma unavailable")

        result = list_themes_and_templates(
            scope="C1",
            content_type="lecture-slides",
            client=mock_client,
            style_guide_path=style_file,
        )

        assert result["themes"] == []
        assert len(result["templates"]) == 1


class TestExecuteGenerationThemeEnforcement:
    """Regression tests for execute_generation theme handshake behavior."""

    def test_slides_path_requires_theme_handshake(self) -> None:
        with pytest.raises(ValueError, match="Theme mapping handshake failed"):
            execute_generation(
                {"input_text": "hello", "textMode": "generate"},
                slides=[{"slide_number": 1, "content": "A", "fidelity": "creative"}],
            )

    def test_slides_path_enforces_handshake_before_generate(self) -> None:
        mock_client = MagicMock()
        mock_client.generate.return_value = {"id": "gen-1"}
        mock_client.wait_for_generation.return_value = {"id": "gen-1", "status": "completed"}

        result = execute_generation(
            {
                "input_text": "hello",
                "textMode": "generate",
                **_valid_theme_resolution(),
                "themeId": "theme_abc",
            },
            slides=[{"slide_number": 1, "content": "A", "fidelity": "creative"}],
            client=mock_client,
        )

        assert result["status"] == "completed"


class TestGaryOutboundContract:
    """Tests for Story 11.2 outbound contract enforcement."""

    @staticmethod
    def _write_png_archive(path: Path, names: list[str]) -> Path:
        with zipfile.ZipFile(path, "w") as archive:
            for name in names:
                archive.writestr(name, b"png-bytes")
        return path

    def test_mixed_fidelity_output_contains_required_fields(self) -> None:
        slides = [
            {"slide_number": 1, "content": "Creative card", "fidelity": "creative"},
            {"slide_number": 2, "content": "Literal card", "fidelity": "literal-text"},
        ]

        with patch.object(gamma_operations, "generate_slide") as mock_generate:
            mock_generate.side_effect = [{"id": "gen-creative"}, {"id": "gen-literal"}]
            result = generate_deck_mixed_fidelity(
                slides,
                {
                    "themeId": "theme_abc",
                    "exportAs": "png",
                    **_valid_theme_resolution(),
                },
                "C1-M1-PRES-ADHOC-20260330",
                run_id="C1-M1-PRES-ADHOC-20260330",
            )

        for required_key in (
            "gary_slide_output",
            "quality_assessment",
            "parameter_decisions",
            "recommendations",
            "flags",
        ):
            assert required_key in result

        assert result["flags"]["run_validation_artifact_pointer"].startswith(
            "run://C1-M1-PRES-ADHOC-20260330/"
        )
        assert result["calls_made"] == 2

    def test_visual_description_policy_avoids_pending_export_placeholders(self) -> None:
        slides = [{"slide_number": 1, "content": "Creative card", "fidelity": "creative"}]

        with patch.object(gamma_operations, "generate_slide") as mock_generate:
            mock_generate.return_value = {"id": "gen-creative"}
            result = generate_deck_mixed_fidelity(
                slides,
                {
                    "themeId": "theme_abc",
                    **_valid_theme_resolution(),
                },
                "C1-M1-PRES-ADHOC-20260330",
                run_id="C1-M1-PRES-ADHOC-20260330",
            )

        desc = result["gary_slide_output"][0]["visual_description"].lower()
        assert "pending export" not in desc

    def test_mixed_fidelity_file_path_populated_from_generation_urls(self) -> None:
        slides = [
            {"slide_number": 1, "content": "Creative card", "fidelity": "creative"},
            {"slide_number": 2, "content": "Literal card", "fidelity": "literal-text"},
        ]

        with patch.object(gamma_operations, "generate_slide") as mock_generate:
            mock_generate.side_effect = [
                {"id": "gen-creative", "gammaUrl": "https://gamma.app/docs/creative"},
                {"id": "gen-literal", "gammaUrl": "https://gamma.app/docs/literal"},
            ]
            result = generate_deck_mixed_fidelity(
                slides,
                {
                    "themeId": "theme_abc",
                    **_valid_theme_resolution(),
                },
                "C1-M1-PRES-ADHOC-20260330",
                run_id="C1-M1-PRES-ADHOC-20260330",
            )

        output = result["gary_slide_output"]
        assert len(output) == 2
        assert output[0]["file_path"] == "https://gamma.app/docs/creative"
        assert output[1]["file_path"] == "https://gamma.app/docs/literal"

    def test_mixed_fidelity_with_literal_visual_uses_three_calls(self) -> None:
        slides = [
            {"slide_number": 1, "content": "Creative card", "fidelity": "creative"},
            {"slide_number": 2, "content": "Literal text card", "fidelity": "literal-text"},
            {"slide_number": 3, "content": "Literal visual card", "fidelity": "literal-visual"},
        ]
        diagram_cards = [
            {
                "card_number": 3,
                "image_url": "https://example.com/diagram.png",
                "required": True,
            }
        ]

        with (
            patch.object(gamma_operations, "generate_slide") as mock_generate,
            patch.object(gamma_operations, "generate_from_template") as mock_template,
            patch.object(gamma_operations, "validate_image_url", return_value=(True, "OK")),
            patch.object(gamma_operations, "validate_visual_fill", return_value={"passed": True}),
        ):
            mock_generate.side_effect = [
                {"id": "gen-creative", "gammaUrl": "https://gamma.app/docs/creative"},
                {"id": "gen-literal-text", "gammaUrl": "https://gamma.app/docs/literal-text"},
            ]
            mock_template.return_value = {
                "id": "gen-literal-visual", "gammaUrl": "https://gamma.app/docs/literal-visual",
            }
            result = generate_deck_mixed_fidelity(
                slides,
                {
                    "themeId": "theme_abc",
                    **_valid_theme_resolution(),
                },
                "C1-M1-PRES-ADHOC-20260330",
                diagram_cards=diagram_cards,
                run_id="C1-M1-PRES-ADHOC-20260330",
            )

        assert mock_generate.call_count == 2
        assert mock_template.call_count == 1
        assert result["calls_made"] == 3
        assert {p["source_call"] for p in result["provenance"]} == {
            "creative",
            "literal-text",
            "literal-visual",
        }


class TestExecuteGenerationDeliberateDispatch:
    """Tests for deliberate variant strategies in double dispatch."""

    @patch("gamma_operations.validate_outbound_contract")
    def test_applies_deliberate_variant_strategies(self, _mock_validate: MagicMock) -> None:
        """Happy path: variant_strategies applied to A/B params."""
        mock_client = MagicMock()
        mock_client.generate.return_value = {"id": "gen-a"}
        mock_client.wait_for_generation.side_effect = [
            {"id": "gen-a", "status": "completed", "gammaUrl": "url-a"},
            {"id": "gen-b", "status": "completed", "gammaUrl": "url-b"},
        ]

        slides = [
            {"slide_number": 1, "content": "Test content", "fidelity": "creative"},
        ]

        params = {
            "input_text": "Test content",
            "textMode": "generate",
            "double_dispatch": True,
            "variant_strategies": {
                "A": {"additionalInstructions": "Focus on data."},
                "B": {"additionalInstructions": "Focus on narrative."},
            },
            "theme_resolution": _valid_theme_resolution(),
            "themeId": "theme_abc",
        }

        result = execute_generation(params, slides=slides, client=mock_client)

        # Verify A call got A's diffs (key_map converts to snake_case)
        a_call = mock_client.generate.call_args_list[0]
        a_instr = a_call[1].get("additional_instructions") or a_call[1].get("additionalInstructions", "")
        assert "Focus on data." in a_instr

        # Verify B call got B's diffs
        b_call = mock_client.generate.call_args_list[1]
        b_instr = b_call[1].get("additional_instructions") or b_call[1].get("additionalInstructions", "")
        assert "Focus on narrative." in b_instr

        assert result["generation_mode"] == "double-dispatch"
        # gary_slide_output may be empty with mocks — the key assertion
        # is that variant strategies were applied to the API calls above.

    @patch("gamma_operations.validate_outbound_contract")
    def test_fallback_on_invalid_variant_strategies(self, _mock_validate: MagicMock, caplog: pytest.LogCaptureFixture) -> None:
        """Invalid strategies: log warning, fallback to uniform."""
        mock_client = MagicMock()
        mock_client.generate.return_value = {"id": "gen-uniform"}
        mock_client.wait_for_generation.side_effect = [
            {"id": "gen-uniform", "status": "completed", "gammaUrl": "url-uniform"},
        ] * 2

        slides = [
            {"slide_number": 1, "content": "Test content", "fidelity": "creative"},
        ]

        params = {
            "input_text": "Test content",
            "textMode": "generate",
            "double_dispatch": True,
            "variant_strategies": "not-a-dict",
            "theme_resolution": _valid_theme_resolution(),
            "themeId": "theme_abc",
        }

        with caplog.at_level(logging.WARNING, logger="gamma_operations"):
            result = execute_generation(params, slides=slides, client=mock_client)

        assert "variant_strategies not a dict, falling back to uniform stochastic" in caplog.text

    @patch("gamma_operations.validate_outbound_contract")
    def test_fallback_on_no_variant_strategies(self, _mock_validate: MagicMock, caplog: pytest.LogCaptureFixture) -> None:
        """No strategies: log info, fallback to uniform."""
        mock_client = MagicMock()
        mock_client.generate.return_value = {"id": "gen-uniform"}
        mock_client.wait_for_generation.side_effect = [
            {"id": "gen-uniform", "status": "completed", "gammaUrl": "url-uniform"},
        ] * 2

        slides = [
            {"slide_number": 1, "content": "Test content", "fidelity": "creative"},
        ]

        params = {
            "input_text": "Test content",
            "textMode": "generate",
            "double_dispatch": True,
            "deliberate_dispatch": True,
            "theme_resolution": _valid_theme_resolution(),
            "themeId": "theme_abc",
        }

        with caplog.at_level(logging.INFO, logger="gamma_operations"):
            result = execute_generation(params, slides=slides, client=mock_client)

        assert "No variant_strategies provided" in caplog.text

    def test_literal_visual_call_uses_template_api(self) -> None:
        slides = [
            {"slide_number": 1, "content": "Creative card", "fidelity": "creative"},
            {"slide_number": 2, "content": "Literal text card", "fidelity": "literal-text"},
            {"slide_number": 3, "content": "Literal visual card", "fidelity": "literal-visual"},
        ]
        diagram_cards = [
            {
                "card_number": 3,
                "image_url": "https://example.com/diagram.png",
                "placement_note": "Use roadmap crop with title-safe top margin.",
                "required": True,
            }
        ]

        with (
            patch.object(gamma_operations, "generate_slide") as mock_generate,
            patch.object(gamma_operations, "generate_from_template") as mock_template,
            patch.object(gamma_operations, "validate_image_url", return_value=(True, "OK")),
            patch.object(gamma_operations, "validate_visual_fill", return_value={"passed": True}),
        ):
            mock_generate.side_effect = [
                {"id": "gen-creative", "gammaUrl": "https://gamma.app/docs/creative"},
                {"id": "gen-literal-text", "gammaUrl": "https://gamma.app/docs/literal-text"},
            ]
            mock_template.return_value = {
                "id": "gen-literal-visual", "gammaUrl": "https://gamma.app/docs/literal-visual",
            }
            generate_deck_mixed_fidelity(
                slides,
                {
                    "themeId": "theme_abc",
                    "imageOptions": {
                        "source": "aiGenerated",
                        "model": "gemini-3.1-flash-image-mini",
                        "stylePreset": "illustration",
                    },
                    "additionalInstructions": "Keep style uniform.",
                    **_valid_theme_resolution(),
                },
                "C1-M1-PRES-ADHOC-20260330",
                diagram_cards=diagram_cards,
                run_id="C1-M1-PRES-ADHOC-20260330",
            )

        literal_text_params = mock_generate.call_args_list[1].args[0]
        assert literal_text_params["themeId"] == "theme_abc"
        assert literal_text_params["image_options"]["source"] == "noImages"

        # Template call passes gammaId, prompt, and params dict
        tpl_args = mock_template.call_args
        assert tpl_args.args[0] == "g_gior6s13mvpk8ms"  # template gammaId
        assert "https://example.com/diagram.png" in tpl_args.args[1]
        assert "full opacity" in tpl_args.args[1].lower()  # anti-fade language required
        assert "not as background" in tpl_args.args[1].lower()  # anti-fade language required
        assert "image_options" not in tpl_args.args[2]  # template endpoint rejects imageOptions.source (400 validated 2026-04-05)
        assert "roadmap crop" in tpl_args.args[1].lower()

    def test_literal_preserve_calls_do_not_prefix_doc_title_into_input_text(self) -> None:
        slides = [
            {"slide_number": 1, "content": "Creative card", "fidelity": "creative"},
            {"slide_number": 2, "content": "Literal text card", "fidelity": "literal-text"},
            {"slide_number": 3, "content": "Literal visual card", "fidelity": "literal-visual"},
        ]
        diagram_cards = [
            {
                "card_number": 3,
                "image_url": "https://example.com/diagram.png",
                "placement_note": "Use roadmap crop with title-safe top margin.",
                "required": True,
            }
        ]

        with (
            patch.object(gamma_operations, "generate_slide") as mock_generate,
            patch.object(gamma_operations, "generate_from_template") as mock_template,
            patch.object(gamma_operations, "validate_image_url", return_value=(True, "OK")),
            patch.object(gamma_operations, "validate_visual_fill", return_value={"passed": True}),
        ):
            mock_generate.side_effect = [
                {"id": "gen-creative", "gammaUrl": "https://gamma.app/docs/creative"},
                {"id": "gen-literal-text", "gammaUrl": "https://gamma.app/docs/literal-text"},
            ]
            mock_template.return_value = {
                "id": "gen-literal-visual", "gammaUrl": "https://gamma.app/docs/literal-visual",
            }
            generate_deck_mixed_fidelity(
                slides,
                {
                    "themeId": "theme_abc",
                    **_valid_theme_resolution(),
                },
                "C1-M1-PRES-ADHOC-20260330",
                diagram_cards=diagram_cards,
                run_id="C1-M1-PRES-ADHOC-20260330",
            )

        literal_text_params = mock_generate.call_args_list[1].args[0]
        assert not literal_text_params["input_text"].startswith("C1-M1-PRES-ADHOC")
        assert literal_text_params["input_text"].startswith("Literal text card")

        # Literal-visual now uses template API — prompt contains the URL
        tpl_prompt = mock_template.call_args.args[1]
        assert "https://example.com/diagram.png" in tpl_prompt

    def test_creative_call_does_not_prefix_doc_title_into_input_text(self) -> None:
        slides = [
            {"slide_number": 1, "content": "Creative card one", "fidelity": "creative"},
            {"slide_number": 2, "content": "Creative card two", "fidelity": "creative"},
        ]

        with patch.object(gamma_operations, "generate_slide") as mock_generate:
            mock_generate.return_value = {"id": "gen-creative", "gammaUrl": "https://gamma.app/docs/creative"}
            generate_deck_mixed_fidelity(
                slides,
                {
                    "themeId": "theme_abc",
                    **_valid_theme_resolution(),
                },
                "C1-M1-PRES-ADHOC-20260330",
                run_id="C1-M1-PRES-ADHOC-20260330",
            )

        creative_params = mock_generate.call_args_list[0].args[0]
        assert not creative_params["input_text"].startswith("C1-M1-PRES-ADHOC")
        assert creative_params["input_text"].startswith("Creative card one")

    def test_multiple_literal_visual_slides_are_generated_in_separate_calls(self) -> None:
        slides = [
            {"slide_number": 1, "content": "Creative card", "fidelity": "creative"},
            {"slide_number": 2, "content": "Literal text card", "fidelity": "literal-text"},
            {"slide_number": 15, "content": "Bridge card A", "fidelity": "literal-visual"},
            {"slide_number": 16, "content": "Bridge card B", "fidelity": "literal-visual"},
        ]
        diagram_cards = [
            {
                "card_number": 15,
                "image_url": "https://example.com/bridge-a.png",
                "placement_note": "Crop to transition from Course 1 to Course 2.",
                "required": True,
            },
            {
                "card_number": 16,
                "image_url": "https://example.com/bridge-b.png",
                "placement_note": "Closing crop anchored on leadership identity.",
                "required": True,
            },
        ]

        with (
            patch.object(gamma_operations, "generate_slide") as mock_generate,
            patch.object(gamma_operations, "generate_from_template") as mock_template,
            patch.object(gamma_operations, "validate_image_url", return_value=(True, "OK")),
            patch.object(gamma_operations, "validate_visual_fill", return_value={"passed": True}),
        ):
            mock_generate.side_effect = [
                {"id": "gen-creative", "gammaUrl": "https://gamma.app/docs/creative"},
                {"id": "gen-literal-text", "gammaUrl": "https://gamma.app/docs/literal-text"},
            ]
            mock_template.side_effect = [
                {"id": "gen-visual-15", "gammaUrl": "https://gamma.app/docs/literal-visual-15"},
                {"id": "gen-visual-16", "gammaUrl": "https://gamma.app/docs/literal-visual-16"},
            ]
            result = generate_deck_mixed_fidelity(
                slides,
                {
                    "themeId": "theme_abc",
                    "imageOptions": {
                        "source": "aiGenerated",
                        "model": "gemini-3.1-flash-image-mini",
                        "stylePreset": "illustration",
                    },
                    **_valid_theme_resolution(),
                },
                "C1-M1-PRES-ADHOC-20260330",
                diagram_cards=diagram_cards,
                run_id="C1-M1-PRES-ADHOC-20260330",
            )

        assert mock_generate.call_count == 2
        assert mock_template.call_count == 2
        assert result["calls_made"] == 4
        assert [p["source_call"] for p in result["provenance"] if p["source_call"] == "literal-visual"] == ["literal-visual", "literal-visual"]
        first_tpl = mock_template.call_args_list[0].args[1]
        second_tpl = mock_template.call_args_list[1].args[1]
        assert "bridge-a.png" in first_tpl.lower()
        assert "bridge-b.png" in second_tpl.lower()

    def test_literal_visual_prompt_uses_raw_image_url_not_markdown_image_syntax(self) -> None:
        slides = [
            {"slide_number": 1, "content": "Literal visual card", "fidelity": "literal-visual"},
        ]
        diagram_cards = [
            {
                "card_number": 1,
                "image_url": "https://example.com/roadmap.png",
                "placement_note": "Use roadmap crop.",
                "required": True,
            }
        ]

        with (
            patch.object(gamma_operations, "generate_slide"),
            patch.object(gamma_operations, "generate_from_template") as mock_template,
            patch.object(gamma_operations, "validate_image_url", return_value=(True, "OK")),
            patch.object(gamma_operations, "validate_visual_fill", return_value={"passed": True}),
        ):
            mock_template.return_value = {"id": "gen-literal-visual", "gammaUrl": "https://gamma.app/docs/literal-visual"}
            generate_deck_mixed_fidelity(
                slides,
                {
                    "themeId": "theme_abc",
                    **_valid_theme_resolution(),
                },
                "C1-M1-PRES-ADHOC-20260330",
                diagram_cards=diagram_cards,
                run_id="C1-M1-PRES-ADHOC-20260330",
            )

        tpl_prompt = mock_template.call_args.args[1]
        assert "https://example.com/roadmap.png" in tpl_prompt
        assert "![diagram](https://example.com/roadmap.png)" not in tpl_prompt

    def test_literal_visual_slide_fails_closed_without_diagram_card(self) -> None:
        slides = [
            {"slide_number": 1, "content": "Literal visual card", "fidelity": "literal-visual"},
        ]

        with (
            patch.object(gamma_operations, "generate_slide"),
            patch.object(gamma_operations, "generate_from_template"),
            pytest.raises(ValueError, match="requires a diagram_cards entry"),
        ):
            generate_deck_mixed_fidelity(
                slides,
                {
                    "themeId": "theme_abc",
                    **_valid_theme_resolution(),
                },
                "C1-M1-PRES-ADHOC-20260330",
                diagram_cards=[],
                run_id="C1-M1-PRES-ADHOC-20260330",
            )

    def test_literal_visual_with_preintegration_routes_through_gamma_api(
        self, tmp_path: Path,
    ) -> None:
        """When a preintegration PNG exists, it is published and then Gamma renders the hosted URL."""
        from PIL import Image as _Image

        preintegration_dir = tmp_path / "preint"
        preintegration_dir.mkdir()
        png_file = preintegration_dir / "card-03.png"
        # Create a valid 100x56 PNG so Pillow can open it for post-processing.
        _img = _Image.new("RGB", (100, 56), color=(30, 60, 120))
        _img.save(png_file, format="PNG")

        export_dir = tmp_path / "export"
        export_dir.mkdir()

        slides = [
            {"slide_number": 1, "content": "Creative card", "fidelity": "creative"},
            {"slide_number": 3, "content": "Literal visual card", "fidelity": "literal-visual"},
        ]
        diagram_cards = [
            {
                "card_number": 3,
                "image_url": "https://example.com/diagram.png",
                "preintegration_png_path": str(png_file),
                "required": True,
            }
        ]

        mock_publish_result = {
            "repo_url": "https://github.com/test/test.github.io",
            "target_subdir": "assets/gamma/test-module",
            "preintegration_ready": True,
            "copied_count": 1,
            "pushed": True,
            "url_base": "https://test.github.io/assets/gamma/test-module",
            "substituted_cards": [3],
            "skipped": [],
            "url_map": {3: "https://test.github.io/assets/gamma/test-module/card-03.png"},
        }

        with (
            patch.object(gamma_operations, "generate_slide") as mock_generate,
            patch.object(gamma_operations, "generate_from_template") as mock_template,
            patch.object(
                gamma_operations,
                "publish_preintegration_literal_visuals",
                return_value=mock_publish_result,
            ),
            patch.object(gamma_operations, "validate_image_url", return_value=(True, "OK")),
            patch.object(gamma_operations, "validate_visual_fill", return_value={"passed": True}),
        ):
            mock_generate.return_value = {
                "id": "gen-creative",
                "gammaUrl": "https://gamma.app/docs/creative",
            }
            mock_template.return_value = {
                "id": "gen-literal-visual",
                "gammaUrl": "https://gamma.app/docs/literal-visual",
            }
            result = generate_deck_mixed_fidelity(
                slides,
                {
                    "themeId": "theme_abc",
                    "export_dir": str(export_dir),
                    "export_as": "png",
                    "site_repo_url": "https://github.com/test/test.github.io",
                    **_valid_theme_resolution(),
                },
                "test-module",
                diagram_cards=diagram_cards,
                run_id="TEST-GAMMA-ROUTE",
            )

        # 2 calls: creative via generate_slide + literal-visual via template (no bypass).
        assert mock_generate.call_count == 1
        assert mock_template.call_count == 1
        assert result["calls_made"] == 2

        # Literal-visual template call should use the published hosted URL.
        tpl_prompt = mock_template.call_args.args[1]
        assert "https://test.github.io/assets/gamma/test-module/card-03.png" in tpl_prompt

        # Provenance should NOT show bypass.
        lv_provenance = [p for p in result["provenance"] if p["card_number"] == 3]
        assert lv_provenance[0]["generation_id"] != "preintegration-bypass"
        assert lv_provenance[0]["fidelity"] == "literal-visual"

        # call_mode metadata should be per-card, not bypass.
        assert result["parameter_decisions"]["image_options"]["literal_visual_call_mode"] == "per-card"

    def test_literal_visual_template_prompt_includes_layout_guidance_for_injected_image(self) -> None:
        slides = [
            {"slide_number": 1, "content": "Creative card", "fidelity": "creative"},
            {"slide_number": 2, "content": "Literal visual card", "fidelity": "literal-visual"},
        ]
        diagram_cards = [
            {
                "card_number": 2,
                "image_url": "https://example.com/roadmap.png",
                "placement_note": "Crop to highlight Course 1 to Course 2 bridge.",
                "required": True,
            }
        ]

        with (
            patch.object(gamma_operations, "generate_slide") as mock_generate,
            patch.object(gamma_operations, "generate_from_template") as mock_template,
            patch.object(gamma_operations, "validate_image_url", return_value=(True, "OK")),
            patch.object(gamma_operations, "validate_visual_fill", return_value={"passed": True}),
        ):
            mock_generate.return_value = {
                "id": "gen-creative", "gammaUrl": "https://gamma.app/docs/creative",
            }
            mock_template.return_value = {
                "id": "gen-literal-visual", "gammaUrl": "https://gamma.app/docs/literal-visual",
            }
            generate_deck_mixed_fidelity(
                slides,
                {
                    "themeId": "theme_abc",
                    **_valid_theme_resolution(),
                },
                "C1-M1-PRES-ADHOC-20260330",
                diagram_cards=diagram_cards,
                run_id="C1-M1-PRES-ADHOC-20260330",
            )

        tpl_prompt = mock_template.call_args.args[1]
        assert "full opacity" in tpl_prompt.lower()  # anti-fade language
        assert "crop to highlight course 1 to course 2 bridge" in tpl_prompt.lower()
        assert "https://example.com/roadmap.png" in tpl_prompt

    def test_literal_visual_template_prompt_ignores_slide_body_text_and_uses_only_image_url(self) -> None:
        slides = [
            {
                "slide_number": 2,
                "content": "This explanatory copy must not be sent to on-slide literal-visual generation.",
                "fidelity": "literal-visual",
            },
        ]
        diagram_cards = [
            {
                "card_number": 2,
                "image_url": "https://example.com/only-image.png",
                "placement_note": "Use full-bleed composition.",
                "required": True,
            }
        ]

        with (
            patch.object(gamma_operations, "generate_slide"),
            patch.object(gamma_operations, "generate_from_template") as mock_template,
            patch.object(gamma_operations, "validate_image_url", return_value=(True, "OK")),
            patch.object(gamma_operations, "validate_visual_fill", return_value={"passed": True}),
        ):
            mock_template.return_value = {
                "id": "gen-literal-visual",
                "gammaUrl": "https://gamma.app/docs/literal-visual",
            }
            generate_deck_mixed_fidelity(
                slides,
                {
                    "themeId": "theme_abc",
                    **_valid_theme_resolution(),
                },
                "C1-M1-PRES-ADHOC-20260330",
                diagram_cards=diagram_cards,
                run_id="C1-M1-PRES-ADHOC-20260330",
            )

        tpl_prompt = mock_template.call_args.args[1]
        assert "https://example.com/only-image.png" in tpl_prompt
        assert "This explanatory copy" not in tpl_prompt

    def test_mixed_fidelity_png_export_assigns_per_slide_paths_from_gamma_artifacts(self, tmp_path: Path) -> None:
        slides = [
            {"slide_number": 1, "content": "Creative card 1", "fidelity": "creative"},
            {"slide_number": 2, "content": "Creative card 2", "fidelity": "creative"},
            {"slide_number": 3, "content": "Literal text 1", "fidelity": "literal-text"},
            {"slide_number": 4, "content": "Literal text 2", "fidelity": "literal-text"},
            {"slide_number": 5, "content": "Literal visual", "fidelity": "literal-visual"},
        ]
        diagram_cards = [
            {
                "card_number": 5,
                "image_url": "https://example.com/diagram.png",
                "placement_note": "Use the supplied diagram only.",
                "required": True,
            }
        ]
        creative_archive = self._write_png_archive(
            tmp_path / "creative-export.zip",
            ["card-01.png", "card-02.png"],
        )
        literal_text_archive = self._write_png_archive(
            tmp_path / "literal-text-export.zip",
            ["card-03.png", "card-04.png"],
        )
        literal_visual_png = tmp_path / "literal-visual-05.png"
        literal_visual_png.write_bytes(b"png-bytes")

        with (
            patch.object(gamma_operations, "generate_slide") as mock_generate,
            patch.object(gamma_operations, "generate_from_template") as mock_template,
            patch.object(gamma_operations, "validate_image_url", return_value=(True, "OK")),
            patch.object(gamma_operations, "validate_visual_fill", return_value={"passed": True}),
            patch.object(gamma_operations, "download_export") as mock_download,
        ):
            mock_generate.side_effect = [
                {"id": "gen-creative", "exportUrl": "https://gamma.app/export/creative"},
                {"id": "gen-literal-text", "exportUrl": "https://gamma.app/export/literal-text"},
            ]
            mock_template.return_value = {
                "id": "gen-literal-visual", "exportUrl": "https://gamma.app/export/literal-visual",
            }
            mock_download.side_effect = [creative_archive, literal_text_archive, literal_visual_png]

            result = generate_deck_mixed_fidelity(
                slides,
                {
                    "themeId": "theme_abc",
                    "exportAs": "png",
                    "export_dir": str(tmp_path),
                    **_valid_theme_resolution(),
                },
                "C1-M1-PRES-ADHOC-20260330",
                diagram_cards=diagram_cards,
                run_id="C1-M1-PRES-ADHOC-20260330",
            )

        output = result["gary_slide_output"]
        assert [item["file_path"] for item in output] == [
            str(tmp_path / "C1-M1-PRES-ADHOC-20260330_slide_01.png"),
            str(tmp_path / "C1-M1-PRES-ADHOC-20260330_slide_02.png"),
            str(tmp_path / "C1-M1-PRES-ADHOC-20260330_slide_03.png"),
            str(tmp_path / "C1-M1-PRES-ADHOC-20260330_slide_04.png"),
            str(tmp_path / "C1-M1-PRES-ADHOC-20260330_slide_05.png"),
        ]

    def test_mixed_fidelity_png_export_fails_when_archive_card_count_mismatches(self, tmp_path: Path) -> None:
        slides = [
            {"slide_number": 1, "content": "Creative card 1", "fidelity": "creative"},
            {"slide_number": 2, "content": "Creative card 2", "fidelity": "creative"},
        ]
        creative_archive = self._write_png_archive(
            tmp_path / "creative-export.zip",
            ["card-01.png"],
        )

        with (
            patch.object(gamma_operations, "generate_slide") as mock_generate,
            patch.object(gamma_operations, "download_export", return_value=creative_archive),
        ):
            mock_generate.return_value = {
                "id": "gen-creative",
                "exportUrl": "https://gamma.app/export/creative",
            }

            with pytest.raises(ValueError, match="expected 2 PNG artifacts"):
                generate_deck_mixed_fidelity(
                    slides,
                    {
                        "themeId": "theme_abc",
                        "exportAs": "png",
                        "export_dir": str(tmp_path),
                        **_valid_theme_resolution(),
                    },
                    "C1-M1-PRES-ADHOC-20260330",
                    run_id="C1-M1-PRES-ADHOC-20260330",
                )

    def test_mixed_fidelity_png_export_ignores_stale_extracted_images_from_prior_runs(self, tmp_path: Path) -> None:
        slides = [
            {"slide_number": 1, "content": "Creative card 1", "fidelity": "creative"},
            {"slide_number": 2, "content": "Creative card 2", "fidelity": "creative"},
        ]
        creative_archive = self._write_png_archive(
            tmp_path / "creative-export.zip",
            ["card-01.png", "card-02.png"],
        )
        stale_extract_dir = tmp_path / "C1-M1-PRES-ADHOC-20260330_creative"
        stale_extract_dir.mkdir(parents=True, exist_ok=True)
        (stale_extract_dir / "stale-card-99.png").write_bytes(b"old")

        with (
            patch.object(gamma_operations, "generate_slide") as mock_generate,
            patch.object(gamma_operations, "download_export", return_value=creative_archive),
        ):
            mock_generate.return_value = {
                "id": "gen-creative",
                "exportUrl": "https://gamma.app/export/creative",
            }

            result = generate_deck_mixed_fidelity(
                slides,
                {
                    "themeId": "theme_abc",
                    "exportAs": "png",
                    "export_dir": str(tmp_path),
                    **_valid_theme_resolution(),
                },
                "C1-M1-PRES-ADHOC-20260330",
                run_id="C1-M1-PRES-ADHOC-20260330",
            )

        assert [item["file_path"] for item in result["gary_slide_output"]] == [
            str(tmp_path / "C1-M1-PRES-ADHOC-20260330_slide_01.png"),
            str(tmp_path / "C1-M1-PRES-ADHOC-20260330_slide_02.png"),
        ]

    def test_validate_outbound_contract_raises_on_missing_required_field(self) -> None:
        payload = {
            "gary_slide_output": [],
            "quality_assessment": {},
            "parameter_decisions": {},
            "recommendations": [],
            "flags": {},
            "theme_resolution": _valid_theme_resolution(),
        }
        payload.pop("quality_assessment")
        with pytest.raises(ValueError, match=r"Missing required field\(s\): quality_assessment"):
            validate_outbound_contract(payload)

    def test_validate_outbound_contract_requires_source_ref_when_slide_present(self) -> None:
        payload = {
            "gary_slide_output": [
                {
                    "slide_id": "s-1",
                    "file_path": "course-content/staging/card-01.png",
                    "card_number": 1,
                    "visual_description": "desc",
                    "source_ref": "",
                }
            ],
            "quality_assessment": {},
            "parameter_decisions": {},
            "recommendations": [],
            "flags": {},
            "theme_resolution": _valid_theme_resolution(),
        }
        with pytest.raises(ValueError, match=r"source_ref must be a non-empty string"):
            validate_outbound_contract(payload)

    def test_validate_outbound_contract_strict_mode_requires_file_path(self) -> None:
        payload = {
            "gary_slide_output": [
                {
                    "slide_id": "s-1",
                    "file_path": None,
                    "card_number": 1,
                    "visual_description": "desc",
                    "source_ref": "slide-brief.md#Slide 1",
                }
            ],
            "quality_assessment": {},
            "parameter_decisions": {},
            "recommendations": [],
            "flags": {},
            "theme_resolution": _valid_theme_resolution(),
        }
        with pytest.raises(ValueError, match=r"file_path must be a non-empty string"):
            validate_outbound_contract(payload, require_dispatch_paths=True)

    def test_validate_dispatch_ready_uses_strict_file_path_mode(self) -> None:
        payload = {
            "gary_slide_output": [
                {
                    "slide_id": "s-1",
                    "file_path": None,
                    "card_number": 1,
                    "visual_description": "desc",
                    "source_ref": "slide-brief.md#Slide 1",
                }
            ],
            "quality_assessment": {},
            "parameter_decisions": {},
            "recommendations": [],
            "flags": {},
            "theme_resolution": _valid_theme_resolution(),
        }
        with pytest.raises(ValueError, match=r"file_path must be a non-empty string"):
            validate_dispatch_ready(payload)

    def test_validate_outbound_contract_allows_empty_slide_output(self) -> None:
        payload = {
            "gary_slide_output": [],
            "quality_assessment": {},
            "parameter_decisions": {},
            "recommendations": [],
            "flags": {},
            "theme_resolution": _valid_theme_resolution(),
        }
        validate_outbound_contract(payload)

    def test_validate_outbound_contract_requires_theme_resolution(self) -> None:
        payload = {
            "gary_slide_output": [],
            "quality_assessment": {},
            "parameter_decisions": {},
            "recommendations": [],
            "flags": {},
        }
        with pytest.raises(ValueError, match=r"Missing required field\(s\): theme_resolution"):
            validate_outbound_contract(payload)

    def test_validate_outbound_contract_rejects_invalid_theme_resolution(self) -> None:
        payload = {
            "gary_slide_output": [],
            "quality_assessment": {},
            "parameter_decisions": {},
            "recommendations": [],
            "flags": {},
            "theme_resolution": {
                "requested_theme_key": "a",
                "resolved_theme_key": "b",
                # missing required fields
            },
        }
        with pytest.raises(ValueError, match="Theme mapping handshake failed"):
            validate_outbound_contract(payload)


class TestThemeMappingHandshake:
    """Tests for Story 11.4 theme-selection -> parameter mapping gate."""

    def test_theme_handshake_missing_fields_fails(self) -> None:
        with pytest.raises(ValueError, match=r"Missing required field\(s\):"):
            validate_theme_mapping_handshake(
                {
                    "requested_theme_key": "hil-2026-apc-nejal-A",
                    "resolved_theme_key": "theme_abc",
                    # missing resolved_parameter_set, mapping_source,
                    # mapping_version, user_confirmation
                }
            )

    def test_theme_handshake_requires_explicit_confirmation(self) -> None:
        with pytest.raises(ValueError, match="user_confirmation must be explicit"):
            validate_theme_mapping_handshake(
                {
                    "requested_theme_key": "hil-2026-apc-nejal-A",
                    "resolved_theme_key": "theme_abc",
                    "resolved_parameter_set": "hil-2026-apc-nejal-A",
                    "mapping_source": "state/config/gamma-style-presets.yaml",
                    "mapping_version": "1",
                    "user_confirmation": False,
                }
            )

    def test_mixed_fidelity_requires_theme_handshake(self) -> None:
        slides = [
            {"slide_number": 1, "content": "Creative", "fidelity": "creative"},
            {"slide_number": 2, "content": "Literal", "fidelity": "literal-text"},
        ]
        with pytest.raises(ValueError, match="Theme mapping handshake failed"):
            generate_deck_mixed_fidelity(
                slides,
                {"themeId": "theme_abc"},
                "C1-M1-PRES-ADHOC-20260330",
                run_id="C1-M1-PRES-ADHOC-20260330",
            )

    def test_mixed_fidelity_theme_handshake_in_payload(self) -> None:
        slides = [
            {"slide_number": 1, "content": "Creative", "fidelity": "creative"},
            {"slide_number": 2, "content": "Literal", "fidelity": "literal-text"},
        ]

        with patch.object(gamma_operations, "generate_slide") as mock_generate:
            mock_generate.side_effect = [{"id": "gen-creative"}, {"id": "gen-literal"}]
            result = generate_deck_mixed_fidelity(
                slides,
                {
                    "themeId": "theme_abc",
                    **_valid_theme_resolution(),
                },
                "C1-M1-PRES-ADHOC-20260330",
                run_id="C1-M1-PRES-ADHOC-20260330",
            )

        assert result["theme_resolution"]["requested_theme_key"] == "hil-2026-apc-nejal-A"
        assert result["theme_resolution"]["resolved_theme_key"] == "theme_abc"
        assert result["parameter_decisions"]["resolved_parameter_set"] == "hil-2026-apc-nejal-A"
        assert result["flags"]["theme_mapping_verified"] is True


class TestDoubleDispatch:
    def test_execute_generation_double_dispatch_builds_variant_pairs(self) -> None:
        slides = [
            {"slide_number": 1, "content": "Creative", "fidelity": "creative"},
            {"slide_number": 2, "content": "Literal", "fidelity": "literal-text"},
        ]

        payload_a = {
            "gary_slide_output": [
                {
                    "slide_id": "C1-M1-card-01",
                    "file_path": "course-content/staging/slide_01.png",
                    "card_number": 1,
                    "source_ref": "src#1",
                    "fidelity": "creative",
                },
                {
                    "slide_id": "C1-M1-card-02",
                    "file_path": "course-content/staging/slide_02.png",
                    "card_number": 2,
                    "source_ref": "src#2",
                    "fidelity": "literal-text",
                },
            ],
            "quality_assessment": {
                "overall_score": 0.82,
                "dimensions": {
                    "layout_integrity": 0.85,
                    "parameter_confidence": 0.80,
                    "embellishment_risk_control": 0.81,
                },
                "embellishment_detected": False,
                "embellishment_details": [],
            },
            "parameter_decisions": {},
            "recommendations": [],
            "flags": {},
            "theme_resolution": _valid_theme_resolution(),
            "calls_made": 2,
        }
        payload_b = {
            "gary_slide_output": [
                {
                    "slide_id": "C1-M1-card-01",
                    "file_path": "course-content/staging/slide_01.png",
                    "card_number": 1,
                    "source_ref": "src#1",
                    "fidelity": "creative",
                },
                {
                    "slide_id": "C1-M1-card-02",
                    "file_path": "course-content/staging/slide_02.png",
                    "card_number": 2,
                    "source_ref": "src#2",
                    "fidelity": "literal-text",
                },
            ],
            "quality_assessment": {
                "overall_score": 0.76,
                "dimensions": {
                    "layout_integrity": 0.79,
                    "parameter_confidence": 0.74,
                    "embellishment_risk_control": 0.75,
                },
                "embellishment_detected": False,
                "embellishment_details": [],
            },
            "parameter_decisions": {},
            "recommendations": [],
            "flags": {},
            "theme_resolution": _valid_theme_resolution(),
            "calls_made": 2,
        }

        with patch.object(gamma_operations, "generate_deck_mixed_fidelity") as mock_mixed:
            mock_mixed.side_effect = [payload_a, payload_b]
            result = execute_generation(
                {
                    "themeId": "theme_abc",
                    "double_dispatch": True,
                    **_valid_theme_resolution(),
                },
                slides=slides,
                module_lesson_part="C1-M1",
            )

        assert mock_mixed.call_count == 2
        assert result["generation_mode"] == "double-dispatch"
        assert result["double_dispatch"]["enabled"] is True
        assert result["double_dispatch"]["selection_progress"]["total"] == 2
        assert result["calls_made"] == 4

        output = result["gary_slide_output"]
        assert len(output) == 4
        assert {row["dispatch_variant"] for row in output} == {"A", "B"}
        assert all(row["selected"] is False for row in output)
        assert any("_variant_A" in str(row["file_path"]) for row in output)
        assert any("_variant_B" in str(row["file_path"]) for row in output)


class TestLiteralVisualPreintegrationPublish:
    """Focused tests for publish helper paths that require no network."""

    def test_publish_noop_in_adhoc_mode(self, tmp_path: Path) -> None:
        source = tmp_path / "literal-visual.png"
        source.write_bytes(b"png")

        result = publish_preintegration_literal_visuals(
            {5: source},
            "C1-M1-PART",
            site_repo_url="https://github.com/jlenrique/jlenrique.github.io",
            mode="ad-hoc",
            run_id="RUN-ADHOC-NOOP-1",
        )

        assert result["preintegration_ready"] is False
        assert result["pushed"] is False
        assert result["copied_count"] == 0
        assert result["substituted_cards"] == []

    def test_publish_skips_missing_paths_without_token_requirement(self, tmp_path: Path) -> None:
        missing = tmp_path / "does-not-exist.png"

        result = publish_preintegration_literal_visuals(
            {9: missing},
            "C1-M1-PART",
            site_repo_url="https://github.com/jlenrique/jlenrique.github.io",
            mode="default",
            run_id="RUN-SKIP-1",
        )

        assert result["preintegration_ready"] is False
        assert result["pushed"] is False
        assert result["copied_count"] == 0
        assert result["skipped"] == [{"card_number": 9, "reason": "missing_local_path"}]

    def test_mixed_fidelity_local_literal_visual_requires_site_repo(self, tmp_path: Path) -> None:
        source = tmp_path / "local-literal-visual.png"
        source.write_bytes(b"png")
        slides = [
            {"slide_number": 1, "content": "Literal visual card", "fidelity": "literal-visual"},
        ]
        diagram_cards = [
            {
                "card_number": 1,
                "image_url": str(source),
                "placement_note": "Use local image",
                "required": True,
            }
        ]

        with (
            patch.object(gamma_operations, "generate_slide"),
            pytest.raises(RuntimeError, match="site_repo_url"),
        ):
            generate_deck_mixed_fidelity(
                slides,
                {
                    "themeId": "theme_abc",
                    **_valid_theme_resolution(),
                },
                "C1-M1-PART",
                diagram_cards=diagram_cards,
                run_id="RUN-LOCAL-MISSING-REPO",
            )


class TestGoldenPathDispatch:
    """Integration test: merge_slide_content → execute_generation → validate_dispatch_ready.

    Locks in the full proven dispatch path (content-agnostic):
      fidelity payload (metadata only) + content payload →
      merge_slide_content() → execute_generation() → validate_dispatch_ready().

    This catches regressions to the routing logic that selects merge_slide_content()
    over normalize_slides_payload() when both content sources are present. The test
    uses minimal representative rows matching the production fidelity split pattern
    (creative / literal-text / literal-visual) but carries no course-specific content.
    """

    def _fidelity_payload(self) -> dict:
        return {
            "slides": [
                {
                    "slide_number": 1,
                    "fidelity": "creative",
                    "queue": "creative",
                    "source_anchors": ["extracted.md#Page 1"],
                },
                {
                    "slide_number": 2,
                    "fidelity": "literal-text",
                    "queue": "literal",
                    "source_anchors": ["extracted.md#Page 2"],
                },
                {
                    "slide_number": 3,
                    "fidelity": "literal-visual",
                    "queue": "literal",
                    "source_anchors": ["extracted.md#Page 3"],
                },
            ]
        }

    def _content_payload(self) -> dict:
        return {
            "slides": [
                {
                    "slide_number": 1,
                    "content": "Clinicians run a problem-solving loop every day.",
                    "source_ref": "extracted.md#Page 1",
                },
                {
                    "slide_number": 2,
                    "content": "Healthcare costs and administrative waste continue to rise.",
                    "source_ref": "extracted.md#Page 2",
                },
                {
                    "slide_number": 3,
                    "content": "The roadmap from clinician to innovator.",
                    "source_ref": "extracted.md#Page 3",
                },
            ]
        }

    def test_merge_to_execute_to_validate_dispatch_ready(self) -> None:
        """Full data path: merge_slide_content → execute_generation → validate_dispatch_ready."""
        fidelity_payload = self._fidelity_payload()
        content_payload = self._content_payload()
        params = {
            "themeId": "theme_golden",
            **_valid_theme_resolution(),
        }
        diagram_cards = [
            {
                "card_number": 3,
                "image_url": "https://example.com/golden-path-literal-visual.png",
                "placement_note": "Full-slide image composition.",
                "required": True,
            }
        ]

        # Step 1: merge — must produce content-bearing rows aligned to fidelity metadata
        merged = merge_slide_content(fidelity_payload, content_payload)

        assert len(merged) == 3
        assert merged[0]["fidelity"] == "creative"
        assert merged[0]["content"] == "Clinicians run a problem-solving loop every day."
        assert merged[1]["fidelity"] == "literal-text"
        assert merged[2]["fidelity"] == "literal-visual"
        assert all(
            "placeholder derived from pre-dispatch artifacts" not in s.get("content", "")
            for s in merged
        ), "no slide may carry placeholder text after merge"

        # Step 2: dispatch — mocked at generate_slide + generate_from_template boundaries
        with (
            patch.object(gamma_operations, "generate_slide") as mock_gen,
            patch.object(gamma_operations, "generate_from_template") as mock_tpl,
            patch.object(gamma_operations, "validate_image_url", return_value=(True, "OK")),
            patch.object(gamma_operations, "validate_visual_fill", return_value={"passed": True}),
        ):
            mock_gen.side_effect = [
                {"id": "gen-creative", "gammaUrl": "https://gamma.app/docs/creative"},
                {"id": "gen-literal-text", "gammaUrl": "https://gamma.app/docs/literal-text"},
            ]
            mock_tpl.return_value = {
                "id": "gen-literal-visual", "gammaUrl": "https://gamma.app/docs/literal-visual",
            }
            result = execute_generation(
                params,
                slides=merged,
                module_lesson_part="GOLDEN-PATH-01",
                diagram_cards=diagram_cards,
                run_id="GOLDEN-PATH-01",
            )

        assert mock_gen.call_count == 2, "mixed fidelity: 2 generate_slide calls (creative + literal-text)"
        assert mock_tpl.call_count == 1, "mixed fidelity: 1 generate_from_template call (literal-visual)"

        # Step 3: validate output shape
        assert "gary_slide_output" in result
        output = result["gary_slide_output"]
        assert len(output) == 3
        assert result["calls_made"] == 3
        assert all(s.get("file_path") for s in output), "every slide must have file_path"
        assert all(s.get("source_ref") for s in output), "every slide must have source_ref"

        # Step 4: Gate 2 dispatch contract must pass (low-level validator)
        validate_dispatch_ready(result)


class TestLiteralVisualRetryOnBlank:
    """Tests for the retry-on-blank-fill quality gate in template dispatch."""

    def _base_slides_and_cards(self) -> tuple[list[dict], list[dict]]:
        slides = [
            {"slide_number": 1, "content": "Literal visual card", "fidelity": "literal-visual"},
        ]
        diagram_cards = [
            {
                "card_number": 1,
                "image_url": "https://example.com/diagram.png",
                "placement_note": "Full-bleed composition.",
                "required": True,
            }
        ]
        return slides, diagram_cards

    def test_first_failure_triggers_retry_before_fallback(self) -> None:
        """One failed template render gets one retry before composite fallback."""
        slides, diagram_cards = self._base_slides_and_cards()

        with (
            patch.object(gamma_operations, "generate_slide"),
            patch.object(gamma_operations, "generate_from_template") as mock_template,
            patch.object(gamma_operations, "validate_image_url", return_value=(True, "OK")),
            patch.object(gamma_operations, "validate_visual_fill", return_value={
                "passed": False, "failures": ["faded/degraded"],
            }),
            patch.object(gamma_operations.requests, "get") as mock_download,
        ):
            mock_template.return_value = {
                "id": "gen-lv", "gammaUrl": "https://gamma.app/docs/lv",
            }
            # Mock the URL download for composite fallback
            mock_download.side_effect = Exception("download blocked in test")
            result = generate_deck_mixed_fidelity(
                slides,
                {"themeId": "theme_abc", **_valid_theme_resolution()},
                "SINGLE-ATTEMPT-TEST",
                diagram_cards=diagram_cards,
                run_id="SINGLE-ATTEMPT-TEST",
            )

        assert mock_template.call_count == 2
        assert result["calls_made"] == 2

    def test_retries_exhaust_and_falls_back_to_composite(self, tmp_path: Path) -> None:
        """All template attempts fail → composite fallback from preintegration PNG."""
        from PIL import Image as _Image

        preint_dir = tmp_path / "preint"
        preint_dir.mkdir()
        preint_png = preint_dir / "card-01.png"
        _Image.new("RGB", (1376, 768), color=(30, 60, 120)).save(preint_png, format="PNG")

        export_dir = tmp_path / "export"
        export_dir.mkdir()
        # Create a blank PNG that the template "returns"
        blank_png = export_dir / "blank.png"
        _Image.new("RGB", (2400, 1350), color=(255, 255, 255)).save(blank_png, format="PNG")

        slides, diagram_cards = self._base_slides_and_cards()
        diagram_cards[0]["preintegration_png_path"] = str(preint_png)

        publish_return = {
            "preintegration_ready": True,
            "url_map": {1: "https://example.com/published/card-01.png"},
        }

        with (
            patch.object(gamma_operations, "generate_slide"),
            patch.object(gamma_operations, "generate_from_template") as mock_template,
            patch.object(gamma_operations, "validate_image_url", return_value=(True, "OK")),
            patch.object(gamma_operations, "validate_visual_fill", return_value={"passed": False, "failures": ["blank"]}),
            patch.object(gamma_operations, "download_export", return_value=blank_png),
            patch.object(gamma_operations, "publish_preintegration_literal_visuals", return_value=publish_return),
        ):
            mock_template.return_value = {
                "id": "gen-lv", "exportUrl": "https://gamma.app/export/blank",
            }
            result = generate_deck_mixed_fidelity(
                slides,
                {
                    "themeId": "theme_abc",
                    "exportAs": "png",
                    "export_dir": str(export_dir),
                    **_valid_theme_resolution(),
                },
                "FALLBACK-TEST",
                diagram_cards=diagram_cards,
                site_repo_url="https://github.com/test/repo",
                run_id="FALLBACK-TEST",
            )

        assert mock_template.call_count == 2
        lv_output = [s for s in result["gary_slide_output"] if s["fidelity"] == "literal-visual"]
        assert len(lv_output) == 1
        # The composite fallback should have written a non-blank image.
        composited_path = Path(lv_output[0]["file_path"])
        assert composited_path.is_file()
        with _Image.open(composited_path) as img:
            assert img.size == (2400, 1350)
        # Provenance: composite from preintegration PNG
        assert lv_output[0]["literal_visual_source"] == "composite-preintegration"

    def test_retries_exhaust_no_fallback_logs_error(self) -> None:
        """All attempts fail and no preintegration source — graceful degradation."""
        slides, diagram_cards = self._base_slides_and_cards()
        # No preintegration_png_path in diagram_cards

        with (
            patch.object(gamma_operations, "generate_slide"),
            patch.object(gamma_operations, "generate_from_template") as mock_template,
            patch.object(gamma_operations, "validate_image_url", return_value=(True, "OK")),
            patch.object(gamma_operations, "validate_visual_fill", return_value={"passed": False, "failures": ["blank"]}),
        ):
            mock_template.return_value = {
                "id": "gen-lv", "gammaUrl": "https://gamma.app/docs/lv",
            }
            result = generate_deck_mixed_fidelity(
                slides,
                {"themeId": "theme_abc", **_valid_theme_resolution()},
                "NO-FALLBACK",
                diagram_cards=diagram_cards,
                run_id="NO-FALLBACK",
            )

        assert mock_template.call_count == 2
        # Output still has the literal-visual slide (graceful degradation).
        lv = [s for s in result["gary_slide_output"] if s["fidelity"] == "literal-visual"]
        assert len(lv) == 1

    def test_no_retry_when_first_attempt_passes(self) -> None:
        """Successful first render = exactly 1 API call."""
        slides, diagram_cards = self._base_slides_and_cards()

        with (
            patch.object(gamma_operations, "generate_slide"),
            patch.object(gamma_operations, "generate_from_template") as mock_template,
            patch.object(gamma_operations, "validate_image_url", return_value=(True, "OK")),
            patch.object(gamma_operations, "validate_visual_fill", return_value={"passed": True}),
        ):
            mock_template.return_value = {
                "id": "gen-lv", "gammaUrl": "https://gamma.app/docs/lv",
            }
            result = generate_deck_mixed_fidelity(
                slides,
                {"themeId": "theme_abc", **_valid_theme_resolution()},
                "NO-RETRY",
                diagram_cards=diagram_cards,
                run_id="NO-RETRY",
            )

        assert mock_template.call_count == 1
        assert result["calls_made"] == 1
        # Provenance: successful template render
        lv = [s for s in result["gary_slide_output"] if s["fidelity"] == "literal-visual"]
        assert lv[0]["literal_visual_source"] == "template"

    def test_prompt_starts_with_image_instruction_not_title(self) -> None:
        """Title must appear at END of prompt, not beginning, to prevent Gamma misinterpretation."""
        slides, diagram_cards = self._base_slides_and_cards()

        with (
            patch.object(gamma_operations, "generate_slide"),
            patch.object(gamma_operations, "generate_from_template") as mock_template,
            patch.object(gamma_operations, "validate_image_url", return_value=(True, "OK")),
            patch.object(gamma_operations, "validate_visual_fill", return_value={"passed": True}),
        ):
            mock_template.return_value = {
                "id": "gen-lv", "gammaUrl": "https://gamma.app/docs/lv",
            }
            generate_deck_mixed_fidelity(
                slides,
                {"themeId": "theme_abc", **_valid_theme_resolution()},
                "PROMPT-ORDER",
                diagram_cards=diagram_cards,
                run_id="PROMPT-ORDER",
            )

        tpl_prompt = mock_template.call_args.args[1]
        # Prompt must start with the image replacement instruction, not the title.
        assert tpl_prompt.startswith("Replace the placeholder image")
        # Title must appear at the end.
        assert "Title: PROMPT-ORDER Slide 01" in tpl_prompt
        lines = tpl_prompt.strip().split("\n")
        title_line = [l for l in lines if l.startswith("Title:")]
        assert title_line, "Title line must be present"
        # Title must be the last non-empty line.
        non_empty_lines = [l for l in lines if l.strip()]
        assert non_empty_lines[-1].startswith("Title:")

    def test_download_composite_fallback_when_no_local_png(self, tmp_path: Path) -> None:
        """Template fails, no preintegration PNG — download from URL triggers composite."""
        import io
        from unittest.mock import MagicMock

        from PIL import Image as _Image

        export_dir = tmp_path / "export"
        export_dir.mkdir()
        # Create a blank PNG that the template "returns"
        blank_png = export_dir / "blank.png"
        _Image.new("RGB", (2400, 1350), (255, 255, 255)).save(blank_png, format="PNG")

        slides, diagram_cards = self._base_slides_and_cards()
        # No preintegration_png_path — only image_url

        # Create a valid PNG for the mocked download
        source_img = _Image.new("RGB", (1376, 768), (30, 60, 120))
        buf = io.BytesIO()
        source_img.save(buf, format="PNG")
        mock_response = MagicMock()
        mock_response.content = buf.getvalue()
        mock_response.raise_for_status = MagicMock()

        with (
            patch.object(gamma_operations, "generate_slide"),
            patch.object(gamma_operations, "generate_from_template") as mock_template,
            patch.object(gamma_operations, "validate_image_url", return_value=(True, "OK")),
            patch.object(gamma_operations, "validate_visual_fill", return_value={
                "passed": False, "failures": ["faded/degraded"],
            }),
            patch.object(gamma_operations, "download_export", return_value=blank_png),
            patch.object(gamma_operations.requests, "get", return_value=mock_response),
        ):
            mock_template.return_value = {
                "id": "gen-lv", "exportUrl": "https://gamma.app/export/lv",
            }
            result = generate_deck_mixed_fidelity(
                slides,
                {
                    "themeId": "theme_abc",
                    "exportAs": "png",
                    "export_dir": str(export_dir),
                    **_valid_theme_resolution(),
                },
                "DOWNLOAD-FALLBACK",
                diagram_cards=diagram_cards,
                run_id="DOWNLOAD-FALLBACK",
            )

        assert mock_template.call_count == 2
        lv = [s for s in result["gary_slide_output"] if s["fidelity"] == "literal-visual"]
        assert len(lv) == 1
        assert lv[0]["literal_visual_source"] == "composite-download"
