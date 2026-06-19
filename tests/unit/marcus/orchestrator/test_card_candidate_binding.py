"""S0.3 / T4-F6: G2B/G4A cards carry STRUCTURED candidates from the producer
envelope, not empty lists.

Trial-4: G4A had `voice_candidates: []` while enrique's voice_preview.voices held
3 real options with sample URLs; G2B had `variant_candidates: []`. The card now
projects the producer's options so the picker (and Marcus) has data to surface.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

from app.marcus.orchestrator import production_runner as pr


def _envelope(*contribs: SimpleNamespace) -> SimpleNamespace:
    return SimpleNamespace(contributions=list(contribs))


def test_g4a_card_projects_voice_candidates(tmp_path: Path) -> None:
    env = _envelope(
        SimpleNamespace(
            specialist_id="enrique",
            output={
                "voice_preview": {
                    "recommended_voice_id": "v1",
                    "voices": [
                        {"voice_id": "v1", "voice_name": "Roger", "sample_audio_url": "http://a"},
                        {"voice_id": "v2", "voice_name": "Sarah", "sample_audio_url": "http://b"},
                    ],
                }
            },
        )
    )
    card = pr._build_decision_card(
        gate_id="G4A",
        trial_id=uuid4(),
        node_id="11-gate",
        operator_id="operator_test",
        pending_nodes=[],
        artifact_paths=[],
        production_envelope=env,
        runs_root=tmp_path,
    )
    assert card.voice_candidates == ["v1", "v2"]
    voice_opts = [e for e in card.pick_context if e.get("kind") == "voice-options"]
    assert voice_opts and len(voice_opts[0]["voices"]) == 2
    assert voice_opts[0]["voices"][0]["sample_audio_url"] == "http://a"


def test_g2b_card_projects_variant_candidates(tmp_path: Path) -> None:
    env = _envelope(
        SimpleNamespace(
            specialist_id="gary",
            output={
                "gary_slide_output": [
                    {"slide_id": "slide-01", "dispatch_variant": "A", "file_path": "a1.png"},
                    {"slide_id": "slide-01", "dispatch_variant": "B", "file_path": "b1.png"},
                    {"slide_id": "slide-02", "dispatch_variant": "A", "file_path": "a2.png"},
                ]
            },
        )
    )
    card = pr._build_decision_card(
        gate_id="G2B",
        trial_id=uuid4(),
        node_id="07B-gate",
        operator_id="operator_test",
        pending_nodes=[],
        artifact_paths=[],
        production_envelope=env,
        runs_root=tmp_path,
    )
    assert card.variant_candidates == ["A", "B"]
    slide_opts = [e for e in card.pick_context if e.get("kind") == "variant-options"]
    assert slide_opts
    slides = {s["slide_id"]: s for s in slide_opts[0]["slides"]}
    assert len(slides["slide-01"]["variants"]) == 2


def test_card_candidates_empty_without_producer_output(tmp_path: Path) -> None:
    card = pr._build_decision_card(
        gate_id="G4A",
        trial_id=uuid4(),
        node_id="11-gate",
        operator_id="operator_test",
        pending_nodes=[],
        artifact_paths=[],
        production_envelope=_envelope(),
        runs_root=tmp_path,
    )
    assert card.voice_candidates == []
