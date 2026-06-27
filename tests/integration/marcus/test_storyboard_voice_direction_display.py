"""P5 Step 3 — Storyboard B DISPLAYS per-segment voice direction before spend.

Authority:
`_bmad-output/planning-artifacts/p5-directed-voice-audition-rubric-2026-06-27.md`
§8 (display checklist) + §5 (delivery_tag rules) + §7 (precedence);
control-cards Card 2 (Must-Show); strawman §F MUR-3 (display↔dispatch parity).

These pins drive the REAL legacy ``generate-storyboard.py`` routine (loaded the
same way the publisher loads it) end-to-end: a segment manifest carrying
``voice_direction`` flows through ``load_narration_by_slide_id`` →
``build_manifest`` → ``render_index_html_v2``. We assert:

* the assembled manifest (storyboard.json) carries per-slide ``voice_direction``;
* the rendered HTML shows the §8 direction fields for a DIRECTED segment, plus
  the RESOLVED TTS settings Enrique will actually send;
* MUR-3 parity: the displayed resolved settings are computed by the SAME shared
  ``map_voice_direction_to_tts`` mapper Enrique uses;
* an UNDIRECTED segment shows the explicit "global/default settings" text;
* ``delivery_tag`` renders as a DISTINCT generation cue and NEVER inside the
  learner-facing narration text block;
* a global voice-direction-defaults header is present.
"""

from __future__ import annotations

import json
import re
from argparse import Namespace
from pathlib import Path

from app.marcus.orchestrator import storyboard_publisher

MODULE = storyboard_publisher._load_generator_module()

# A directed voice_direction (rubric §4 reflective synthesis) with a delivery
# tag and an explicit elevenlabs override — exercises every §8 display item.
DIRECTED_VD = {
    "schema_version": "voice-direction.v1",
    "render_strategy": "tts",
    "delivery_intent": "reflective debrief, let it settle",
    "emotional_tone": "reflective",
    "pace": "slower",
    "energy": "low",
    "delivery_tag": "[thoughtfully]",
    "pause_after_seconds": 0.6,
    "elevenlabs": {"similarity_boost": 0.8},
    "source": "cd-authored",
}


def _build_storyboard_b(tmp_path: Path, *, directed: bool = True) -> tuple[dict, str]:
    """Run the REAL cmd_generate over a 2-slide payload + a segment manifest in
    which slide-01 is DIRECTED and slide-02 is UNDIRECTED. With ``directed=False``
    NEITHER segment carries a voice_direction (flag-OFF shape). Returns
    (storyboard.json manifest, index.html text)."""
    seg01 = {
        "id": "seg-01",
        "slide_id": "slide-01",
        "narration_text": "Plain narration body for slide one.",
        "timing_role": "concept-build",
    }
    if directed:
        seg01["voice_direction"] = DIRECTED_VD
    png1 = tmp_path / "slide-01.png"
    png2 = tmp_path / "slide-02.png"
    for png in (png1, png2):
        png.write_bytes(b"\x89PNG\r\n\x1a\n" + b"0" * 32)
    payload_path = tmp_path / "gary-dispatch-payload.json"
    payload_path.write_text(
        json.dumps(
            {
                "generation_id": "gen-vd",
                "status": "complete",
                "gary_slide_output": [
                    {
                        "slide_id": "slide-01",
                        "card_number": 1,
                        "dispatch_variant": "A",
                        "file_path": str(png1),
                        "generation_id": "gen-vd",
                        "visual_description": "Directed sample",
                    },
                    {
                        "slide_id": "slide-02",
                        "card_number": 2,
                        "dispatch_variant": "A",
                        "file_path": str(png2),
                        "generation_id": "gen-vd",
                        "visual_description": "Undirected sample",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    manifest_path = tmp_path / "segment-manifest-storyboard-b.yaml"
    manifest_path.write_text(
        MODULE.yaml.safe_dump(
            {
                "segments": [
                    seg01,
                    {
                        "id": "seg-02",
                        "slide_id": "slide-02",
                        "narration_text": "Plain narration body for slide two.",
                        "timing_role": "concept-build",
                        # NO voice_direction — undirected segment.
                    },
                ]
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    out_dir = tmp_path / "pack-b"
    rc = MODULE.cmd_generate(
        Namespace(
            payload=payload_path,
            out_dir=out_dir,
            asset_base=None,
            print_summary=False,
            strict=True,
            segment_manifest=manifest_path,
            related_assets=None,
            run_id="vd-display-test",
            cluster_coherence_report=None,
            pass2_envelope=None,
        )
    )
    assert rc == 0
    manifest = json.loads(
        (out_dir / "storyboard" / "storyboard.json").read_text(encoding="utf-8")
    )
    html_text = (out_dir / "storyboard" / "index.html").read_text(encoding="utf-8")
    return manifest, html_text


def _slide_by_id(manifest: dict, slide_id: str) -> dict:
    return next(s for s in manifest["slides"] if s.get("slide_id") == slide_id)


# --------------------------------------------------------------------------- #
# Data assembly: storyboard.json carries per-slide voice_direction.
# --------------------------------------------------------------------------- #
def test_manifest_carries_voice_direction_for_directed_slide(tmp_path: Path) -> None:
    manifest, _ = _build_storyboard_b(tmp_path)
    directed = _slide_by_id(manifest, "slide-01")
    vds = directed.get("voice_directions")
    assert isinstance(vds, list) and len(vds) == 1
    assert vds[0]["voice_direction"]["emotional_tone"] == "reflective"
    # Undirected slide: additive discipline — the key is ABSENT, not null.
    undirected = _slide_by_id(manifest, "slide-02")
    assert "voice_directions" not in undirected


def test_flag_off_storyboard_json_has_no_voice_direction_key(tmp_path: Path) -> None:
    """Blind #7 additive-only: when NO segment is directed, storyboard.json must
    carry no voice-direction key anywhere (matches the publisher's
    missing-stays-missing discipline)."""
    manifest, _ = _build_storyboard_b(tmp_path, directed=False)
    for slide in manifest["slides"]:
        assert "voice_directions" not in slide
    assert "voice_direction" not in json.dumps(manifest["slides"])


# --------------------------------------------------------------------------- #
# MUR-3 parity: the resolution helper IS the shared mapper.
# --------------------------------------------------------------------------- #
def test_resolved_settings_match_shared_mapper() -> None:
    from app.specialists._shared.voice_direction_map import map_voice_direction_to_tts
    from app.specialists.irene.authoring.pass_2_template import VoiceDirection

    expected = map_voice_direction_to_tts(VoiceDirection.model_validate(DIRECTED_VD))
    assert MODULE.resolve_voice_direction_settings(DIRECTED_VD) == expected


def test_resolution_helper_returns_none_for_missing_and_invalid() -> None:
    assert MODULE.resolve_voice_direction_settings(None) is None
    assert MODULE.resolve_voice_direction_settings({}) is None
    # A non-empty-but-invalid direction also degrades to None (never crashes).
    invalid = {"schema_version": "voice-direction.v1", "pause_after_seconds": 9.0}
    assert MODULE.resolve_voice_direction_settings(invalid) is None


# --------------------------------------------------------------------------- #
# Display (§8): directed segment shows direction + resolved settings.
# --------------------------------------------------------------------------- #
def _resolved_blocks(html_text: str) -> list[str]:
    # Scope to the resolved-settings <dl> (no nested <dl>), so the dt/dd rows are
    # captured whole — a <div>-based capture truncates at the first nested </div>.
    return re.findall(
        r'<dl class="voice-direction-resolved-list">(.*?)</dl>',
        html_text,
        re.S,
    )


def test_directed_segment_renders_direction_fields(tmp_path: Path) -> None:
    _, html_text = _build_storyboard_b(tmp_path)
    assert "Voice direction" in html_text
    # Exact enum value shown in the TONE field specifically (not just anywhere).
    assert "<dd>reflective</dd>" in html_text
    assert "<dd>slower</dd>" in html_text
    # delivery_intent shown as review/provenance metadata (not script).
    assert "reflective debrief, let it settle" in html_text
    # populated elevenlabs override shown.
    assert "similarity_boost" in html_text
    # source provenance shown.
    assert "cd-authored" in html_text


def test_directed_segment_renders_resolved_parity_settings(tmp_path: Path) -> None:
    """The RESOLVED TTS settings (what Enrique sends) are displayed — proven by
    the exact mapper-derived numbers appearing INSIDE the resolved-settings block
    (scoped, so CSS like 0.86rem cannot fake-green the assertion).
    reflective+slower+low → speed 0.94 (pace=slower), stability 0.75 / style 0.1
    (energy=low), similarity_boost 0.8 (explicit override)."""
    from app.specialists._shared.voice_direction_map import map_voice_direction_to_tts
    from app.specialists.irene.authoring.pass_2_template import VoiceDirection

    _, html_text = _build_storyboard_b(tmp_path)
    resolved = map_voice_direction_to_tts(VoiceDirection.model_validate(DIRECTED_VD))
    blocks = _resolved_blocks(html_text)
    assert len(blocks) >= 1
    block = "\n".join(blocks)
    assert f"<dd>{resolved['speed']}</dd>" in block  # 0.94
    assert f"<dd>{resolved['stability']}</dd>" in block  # 0.75
    assert f"<dd>{resolved['style']}</dd>" in block  # 0.1
    assert f"<dd>{resolved['similarity_boost']}</dd>" in block  # 0.8 (override)


# --------------------------------------------------------------------------- #
# Step-4 carry: effective-voice-source line + honest tier-3/4/5 header.
# --------------------------------------------------------------------------- #
def test_effective_voice_source_line_present_for_explicit_voice_id() -> None:
    panel = MODULE._render_voice_direction_panel(
        {
            "schema_version": "voice-direction.v1",
            "render_strategy": "tts",
            "emotional_tone": "reflective",
            "elevenlabs": {"voice_id": "explicit-voice-9"},
        }
    )
    assert 'data-role="effective-voice-source"' in panel
    assert "Effective voice source" in panel
    assert "explicit-voice-9" in panel


def test_effective_voice_source_line_present_for_default_voice() -> None:
    panel = MODULE._render_voice_direction_panel(
        {
            "schema_version": "voice-direction.v1",
            "render_strategy": "tts",
            "emotional_tone": "warm",
        }
    )
    assert 'data-role="effective-voice-source"' in panel
    # No explicit override -> names the lower-tier resolution honestly.
    assert "voice-selection.json selected default" in panel


def test_resolved_header_qualifies_lower_tier_resolution() -> None:
    panel = MODULE._render_voice_direction_panel(
        {
            "schema_version": "voice-direction.v1",
            "render_strategy": "tts",
            "emotional_tone": "reflective",
        }
    )
    # The strong "display matches dispatch" claim is now qualified so it stays
    # literally true once Enrique applies tier-3/4/5 defaults at synthesis.
    assert "tier-1/2 exact; lower tiers resolved at synthesis" in panel


# --------------------------------------------------------------------------- #
# delivery_tag is a DISTINCT generation cue, NEVER inside the narration block.
# --------------------------------------------------------------------------- #
def test_delivery_tag_rendered_distinct_not_in_narration(tmp_path: Path) -> None:
    _, html_text = _build_storyboard_b(tmp_path)
    # The tag appears in the page (as a generation cue)...
    assert "[thoughtfully]" in html_text
    # ...but NEVER inside a learner-facing narration <pre class="script-text">.
    pres = re.findall(r'<pre class="script-text[^"]*">(.*?)</pre>', html_text, re.S)
    # The selector MUST have matched at least one narration block — otherwise the
    # loop below is vacuous and the test fake-greens on selector drift (Blind #2).
    assert len(pres) >= 1
    for pre in pres:
        assert "[thoughtfully]" not in pre
    # ...and it is marked as a distinct delivery-tag cue.
    assert "delivery-tag" in html_text


# --------------------------------------------------------------------------- #
# Missing direction is EXPLICIT, not blank.
# --------------------------------------------------------------------------- #
def test_undirected_segment_shows_explicit_default_text(tmp_path: Path) -> None:
    _, html_text = _build_storyboard_b(tmp_path)
    assert "using global/default settings" in html_text


# --------------------------------------------------------------------------- #
# Global voice-direction defaults header present.
# --------------------------------------------------------------------------- #
def test_global_voice_direction_defaults_header_present(tmp_path: Path) -> None:
    _, html_text = _build_storyboard_b(tmp_path)
    assert "voice-direction-defaults" in html_text


# --------------------------------------------------------------------------- #
# MUST-FIX 1 — an INVALID (operator-edited) direction renders a VISIBLE warning
# at the review gate, not a silent omission (Edge #1).
# --------------------------------------------------------------------------- #
def test_invalid_direction_renders_visible_warning() -> None:
    invalid = {
        "schema_version": "voice-direction.v1",
        "render_strategy": "tts",
        "emotional_tone": "reflective",
        "pause_after_seconds": 9.0,  # > 5.0 — strict VoiceDirection rejects it.
    }
    panel = MODULE._render_voice_direction_panel(invalid)
    assert 'data-vd-state="invalid"' in panel
    assert "INVALID voice direction" in panel
    # The offending field is named so the operator can fix it.
    assert "pause_after_seconds" in panel
    # It is NOT silently shown as the default/global state, and NOT a blank panel.
    assert "using global/default settings" not in panel
    assert "Resolved TTS settings — what Enrique will send" not in panel


# --------------------------------------------------------------------------- #
# SHOULD-FIX 3 — app-not-importable degrades EXPLICITLY (banner + panel note),
# never a silent vanish of every resolved block (Edge #2).
# --------------------------------------------------------------------------- #
def test_app_unavailable_renders_explicit_panel_note(monkeypatch) -> None:
    monkeypatch.setattr(
        MODULE, "_resolve_voice_direction", lambda vd: ("app-unavailable", None, None)
    )
    panel = MODULE._render_voice_direction_panel(DIRECTED_VD)
    assert 'data-vd-state="app-unavailable"' in panel
    assert "Resolved TTS settings unavailable (app not importable)" in panel
    # The directed fields still render — only the resolved block degrades.
    assert "<dd>reflective</dd>" in panel


def test_parity_banner_when_app_unavailable(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(MODULE, "_voice_direction_app_importable", lambda: False)
    monkeypatch.setattr(
        MODULE, "_resolve_voice_direction", lambda vd: ("app-unavailable", None, None)
    )
    _, html_text = _build_storyboard_b(tmp_path)
    assert "vd-parity-banner" in html_text
    assert "Resolved TTS settings unavailable (app not importable)" in html_text


# --------------------------------------------------------------------------- #
# SHOULD-FIX 2 — a MULTI-SEGMENT slide surfaces EVERY segment's direction, not
# just the first (Edge #3): each spend-incurring direction must be reviewable.
# --------------------------------------------------------------------------- #
def test_multi_segment_slide_surfaces_every_direction(tmp_path: Path) -> None:
    png = tmp_path / "slide-01.png"
    png.write_bytes(b"\x89PNG\r\n\x1a\n" + b"0" * 32)
    payload_path = tmp_path / "gary-dispatch-payload.json"
    payload_path.write_text(
        json.dumps(
            {
                "generation_id": "gen-multi",
                "status": "complete",
                "gary_slide_output": [
                    {
                        "slide_id": "slide-01",
                        "card_number": 1,
                        "dispatch_variant": "A",
                        "file_path": str(png),
                        "generation_id": "gen-multi",
                        "visual_description": "Multi-segment sample",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    manifest_path = tmp_path / "segment-manifest-storyboard-b.yaml"
    manifest_path.write_text(
        MODULE.yaml.safe_dump(
            {
                "segments": [
                    {
                        "id": "seg-01",
                        "slide_id": "slide-01",
                        "narration_text": "First segment narration.",
                        "voice_direction": {
                            "schema_version": "voice-direction.v1",
                            "render_strategy": "tts",
                            "emotional_tone": "reflective",
                            "delivery_tag": "[thoughtfully]",
                            "source": "cd-authored",
                        },
                    },
                    {
                        "id": "seg-02",
                        "slide_id": "slide-01",
                        "narration_text": "Second segment narration.",
                        "voice_direction": {
                            "schema_version": "voice-direction.v1",
                            "render_strategy": "tts",
                            "emotional_tone": "warm",
                            "delivery_tag": "[warmly]",
                            "source": "cd-authored",
                        },
                    },
                ]
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    out_dir = tmp_path / "pack-multi"
    rc = MODULE.cmd_generate(
        Namespace(
            payload=payload_path,
            out_dir=out_dir,
            asset_base=None,
            print_summary=False,
            strict=True,
            segment_manifest=manifest_path,
            related_assets=None,
            run_id="vd-multi-test",
            cluster_coherence_report=None,
            pass2_envelope=None,
        )
    )
    assert rc == 0
    manifest = json.loads(
        (out_dir / "storyboard" / "storyboard.json").read_text(encoding="utf-8")
    )
    html_text = (out_dir / "storyboard" / "index.html").read_text(encoding="utf-8")

    slide = _slide_by_id(manifest, "slide-01")
    vds = slide["voice_directions"]
    assert len(vds) == 2
    assert {v["voice_direction"]["emotional_tone"] for v in vds} == {"reflective", "warm"}
    # BOTH directions render (not just segment-A): both tones + both tags visible.
    assert "<dd>reflective</dd>" in html_text and "<dd>warm</dd>" in html_text
    assert "[thoughtfully]" in html_text and "[warmly]" in html_text
    # Each segment's panel is labelled so the operator can tell them apart.
    assert "voice-direction-seg" in html_text
    assert html_text.count('data-role="voice-direction"') >= 2
