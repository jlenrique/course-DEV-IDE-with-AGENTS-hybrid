"""Marcus SPOC narration surfaces the a-g capabilities in persona (BETA)."""

from __future__ import annotations

import json
from pathlib import Path

from app.marcus.cli.marcus_spoc import narrate_gate


def _card(gate_id: str, **inner) -> dict:
    return {"card": {"card_id": "x", "gate_id": gate_id, **inner}, "digest": "d"}


def test_g2b_narration_surfaces_creative_treatment_e() -> None:
    card = _card(
        "G2B",
        variant_candidates=["A", "B"],
        pick_context=[
            {
                "kind": "variant-options",
                "slides": [
                    {"slide_id": "slide-01", "variants": [{"variant": "A"}, {"variant": "B"}]}
                ],
            }
        ],
    )
    text = narrate_gate("G2B", card, Path("."))
    assert "Marcus" in text
    assert "capability e" in text
    assert "['A', 'B']" in text or "A" in text  # variant count surfaced
    assert "slide-01" in text


def test_g4a_narration_surfaces_voice_options_e() -> None:
    card = _card(
        "G4A",
        voice_candidates=["v1", "v2"],
        pick_context=[{"kind": "voice-options", "voices": [
            {"voice_id": "v1", "voice_name": "Roger", "sample_audio_url": "http://a"},
            {"voice_id": "v2", "voice_name": "Sarah", "sample_audio_url": "http://b"},
        ]}],
    )
    text = narrate_gate("G4A", card, Path("."))
    assert "capability e/voice" in text
    assert "Roger" in text and "Sarah" in text
    assert "http://a" in text  # playable sample surfaced


def test_g1_narration_surfaces_ingestion_b(tmp_path: Path) -> None:
    (tmp_path / "bundle").mkdir()
    (tmp_path / "bundle" / "manifest.json").write_text(
        json.dumps({"artifacts": [{"path": "extracted.md", "size_bytes": 6814}]}),
        encoding="utf-8",
    )
    (tmp_path / "directive.yaml").write_text(
        "sources:\n- ref_id: src-001\n  locator: lesson.docx\n  role: primary\n",
        encoding="utf-8",
    )
    text = narrate_gate("G1", _card("G1"), tmp_path)
    assert "capability b" in text  # ingestion report
    assert "extracted.md" in text
    assert "capability a" in text  # sources + treatment
    assert "primary" in text


def test_g3_narration_surfaces_motion_f() -> None:
    text = narrate_gate("G3", _card("G3"), Path("."))
    assert "capability f" in text
    assert "motion" in text.lower()
