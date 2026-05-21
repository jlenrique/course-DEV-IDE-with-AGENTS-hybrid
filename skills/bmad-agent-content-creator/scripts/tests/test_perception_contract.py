# /// script
# requires-python = ">=3.10"
# ///
"""Tests for Irene Pass 2 mandatory perception contract (Story 13.1).

Covers all 6 acceptance criteria:
  AC1: Validate perception_artifacts presence
  AC2: Inline generation via image bridge when absent
  AC3: Confirmation logged per slide
  AC4: LOW-confidence retry (one attempt)
  AC5: Persistent LOW escalation to Marcus
  AC6: Perception confirmed before narration begins (ordering via enforce)
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is on sys.path for imports
ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from skills.bmad_agent_content_creator.scripts.perception_contract import (
    build_motion_perception_confirmation,
    build_perception_confirmation,
    check_escalation_needed,
    enforce_motion_perception_contract,
    enforce_perception_contract,
    generate_inline_perception,
    retry_low_confidence,
    validate_perception_presence,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_slide(card_number: int, slide_id: str = "") -> dict:
    sid = slide_id or f"s-{card_number}"
    return {
        "slide_id": sid,
        "card_number": card_number,
        "file_path": f"course-content/staging/card-{card_number:02d}.png",
        "source_ref": f"slide-brief.md#Slide {card_number}",
        "visual_description": f"Slide {card_number} description",
    }


def _make_perception(
    card_number: int,
    slide_id: str = "",
    confidence: str = "HIGH",
) -> dict:
    sid = slide_id or f"s-{card_number}"
    return {
        "schema_version": "1.0",
        "modality": "image",
        "artifact_path": f"course-content/staging/card-{card_number:02d}.png",
        "confidence": confidence,
        "confidence_rationale": f"Test perception for slide {card_number}",
        "perception_timestamp": "2026-04-05T12:00:00Z",
        "extracted_text": f"Text from slide {card_number}",
        "layout_description": "Two-column layout",
        "visual_elements": [
            {"type": "chart", "description": "Bar chart", "position": "left"},
            {"type": "text", "description": "Caption", "position": "right"},
        ],
        "slide_title": f"Slide {card_number} Title",
        "text_blocks": [f"Block {card_number}"],
        "visual_complexity_level": "moderate",
        "visual_complexity_summary": "Moderate visual complexity: balanced slide needing selective detail.",
        "slide_id": sid,
        "card_number": card_number,
        "source_image_path": f"course-content/staging/card-{card_number:02d}.png",
    }


def _mock_perceive_high(**kwargs):
    """Perceive function that always returns HIGH confidence."""
    path = kwargs.get("artifact_path", "unknown")
    return {
        "schema_version": "1.0",
        "modality": "image",
        "artifact_path": str(path),
        "confidence": "HIGH",
        "confidence_rationale": "Mock: all elements clearly visible",
        "perception_timestamp": "2026-04-05T12:00:00Z",
        "extracted_text": "Mock extracted text",
        "layout_description": "Clear layout",
        "visual_elements": [
            {"type": "diagram", "description": "Flow diagram", "position": "center"},
        ],
        "slide_title": "Mock Title",
        "text_blocks": ["Mock block"],
        "visual_complexity_level": "moderate",
        "visual_complexity_summary": "Moderate visual complexity: balanced slide needing selective detail.",
    }


def _mock_perceive_low(**kwargs):
    """Perceive function that always returns LOW confidence."""
    path = kwargs.get("artifact_path", "unknown")
    return {
        "schema_version": "1.0",
        "modality": "image",
        "artifact_path": str(path),
        "confidence": "LOW",
        "confidence_rationale": "Mock: image corrupt or blank",
        "perception_timestamp": "2026-04-05T12:00:00Z",
        "extracted_text": "",
        "layout_description": "",
        "visual_elements": [],
        "slide_title": "",
        "text_blocks": [],
        "visual_complexity_level": "low",
        "visual_complexity_summary": "Low visual complexity: minimal orientation needed.",
    }


def _mock_perceive_medium(**kwargs):
    """Perceive function that returns MEDIUM confidence."""
    path = kwargs.get("artifact_path", "unknown")
    return {
        "schema_version": "1.0",
        "modality": "image",
        "artifact_path": str(path),
        "confidence": "MEDIUM",
        "confidence_rationale": "Mock: partial extraction",
        "perception_timestamp": "2026-04-05T12:00:00Z",
        "extracted_text": "Some text",
        "layout_description": "Ambiguous layout",
        "visual_elements": [{"type": "unknown", "description": "unclear", "position": "?"}],
        "slide_title": "",
        "text_blocks": ["Partial"],
        "visual_complexity_level": "moderate",
        "visual_complexity_summary": "Moderate visual complexity: some orientation required.",
    }


class _PerceiveTracker:
    """Track calls to perceive for assertion in tests."""

    def __init__(self, return_confidence: str = "HIGH"):
        self.calls: list[dict] = []
        self.return_confidence = return_confidence

    def __call__(self, **kwargs):
        self.calls.append(kwargs)
        if self.return_confidence == "HIGH":
            return _mock_perceive_high(**kwargs)
        elif self.return_confidence == "LOW":
            return _mock_perceive_low(**kwargs)
        else:
            return _mock_perceive_medium(**kwargs)


class _PerceiveLowThenHigh:
    """Returns LOW on first call per slide, HIGH on retry (second call)."""

    def __init__(self):
        self.call_count: dict[str, int] = {}

    def __call__(self, **kwargs):
        path = str(kwargs.get("artifact_path", "unknown"))
        self.call_count[path] = self.call_count.get(path, 0) + 1
        if self.call_count[path] <= 1:
            return _mock_perceive_low(**kwargs)
        return _mock_perceive_high(**kwargs)


# ===========================================================================
# AC1: Validate perception_artifacts presence
# ===========================================================================

class TestValidatePerceptionPresence:

    def test_present_when_artifacts_exist(self):
        envelope = {
            "gary_slide_output": [_make_slide(1)],
            "perception_artifacts": [_make_perception(1)],
        }
        result = validate_perception_presence(envelope)
        assert result["present"] is True
        assert result["errors"] == []

    def test_absent_when_artifacts_missing(self):
        envelope = {
            "gary_slide_output": [_make_slide(1)],
        }
        result = validate_perception_presence(envelope)
        assert result["present"] is False
        assert result["errors"] == []

    def test_absent_when_artifacts_empty_list(self):
        envelope = {
            "gary_slide_output": [_make_slide(1)],
            "perception_artifacts": [],
        }
        result = validate_perception_presence(envelope)
        assert result["present"] is False

    def test_error_when_gary_missing(self):
        envelope = {}
        result = validate_perception_presence(envelope)
        assert any("gary_slide_output" in e for e in result["errors"])

    def test_error_when_gary_not_array(self):
        envelope = {"gary_slide_output": "not-a-list"}
        result = validate_perception_presence(envelope)
        assert any("must be an array" in e for e in result["errors"])

    def test_error_when_perception_not_array(self):
        envelope = {
            "gary_slide_output": [_make_slide(1)],
            "perception_artifacts": "not-a-list",
        }
        result = validate_perception_presence(envelope)
        assert any("must be an array" in e for e in result["errors"])


# ===========================================================================
# AC2: Inline generation via image bridge when absent
# ===========================================================================

class TestGenerateInlinePerception:

    def test_generates_one_artifact_per_slide(self):
        slides = [_make_slide(1), _make_slide(2), _make_slide(3)]
        tracker = _PerceiveTracker("HIGH")

        artifacts = generate_inline_perception(slides, perceive_fn=tracker)

        assert len(artifacts) == 3
        assert len(tracker.calls) == 3

    def test_artifacts_carry_slide_metadata(self):
        slides = [_make_slide(1, slide_id="slide-alpha")]
        artifacts = generate_inline_perception(
            slides, perceive_fn=_mock_perceive_high,
        )

        assert artifacts[0]["slide_id"] == "slide-alpha"
        assert artifacts[0]["card_number"] == 1
        assert "card-01.png" in artifacts[0]["source_image_path"]

    def test_skips_slides_without_file_path(self):
        slides = [{"slide_id": "s-1", "card_number": 1}]  # no file_path
        tracker = _PerceiveTracker("HIGH")

        artifacts = generate_inline_perception(slides, perceive_fn=tracker)

        assert len(artifacts) == 0
        assert len(tracker.calls) == 0

    def test_handles_perceive_exception_gracefully(self):
        def failing_perceive(**kwargs):
            raise RuntimeError("Bridge crashed")

        slides = [_make_slide(1)]
        artifacts = generate_inline_perception(slides, perceive_fn=failing_perceive)

        assert len(artifacts) == 1
        assert artifacts[0]["confidence"] == "LOW"
        assert "Bridge error" in artifacts[0]["confidence_rationale"]

    def test_passes_run_id_to_perceive(self):
        slides = [_make_slide(1)]
        tracker = _PerceiveTracker("HIGH")

        generate_inline_perception(slides, run_id="RUN-001", perceive_fn=tracker)

        assert tracker.calls[0]["run_id"] == "RUN-001"

    def test_uses_correct_modality_and_gate(self):
        slides = [_make_slide(1)]
        tracker = _PerceiveTracker("HIGH")

        generate_inline_perception(slides, perceive_fn=tracker)

        assert tracker.calls[0]["modality"] == "image"
        assert tracker.calls[0]["gate"] == "G4"
        assert tracker.calls[0]["requesting_agent"] == "irene"

    def test_ignores_non_dict_slides(self):
        slides = [_make_slide(1), "not-a-dict", None, _make_slide(2)]
        artifacts = generate_inline_perception(slides, perceive_fn=_mock_perceive_high)
        assert len(artifacts) == 2


# ===========================================================================
# AC3: Perception confirmation logged per slide
# ===========================================================================

class TestBuildPerceptionConfirmation:

    def test_high_confidence_confirmation(self):
        perception = _make_perception(1, confidence="HIGH")
        conf = build_perception_confirmation(1, perception)

        assert conf["confidence"] == "HIGH"
        assert conf["modality"] == "image"
        assert conf["gate"] == "G4"
        assert conf["action"] == "proceeding"
        assert "Slide 1" in conf["summary"]

    def test_low_confidence_triggers_escalating_action(self):
        perception = _make_perception(1, confidence="LOW")
        conf = build_perception_confirmation(1, perception)

        assert conf["confidence"] == "LOW"
        assert conf["action"] == "escalating"

    def test_medium_confidence_proceeds(self):
        perception = _make_perception(1, confidence="MEDIUM")
        conf = build_perception_confirmation(1, perception)

        assert conf["action"] == "proceeding"

    def test_summary_includes_title_and_elements(self):
        perception = _make_perception(1)
        perception["slide_title"] = "Revenue Trends"
        perception["visual_elements"] = [{"type": "chart"}, {"type": "table"}]
        perception["layout_description"] = "split layout"

        conf = build_perception_confirmation(1, perception)

        assert "Revenue Trends" in conf["summary"]
        assert "2 visual element" in conf["summary"]
        assert "visual complexity" in conf["summary"]

    def test_empty_perception_has_no_details_summary(self):
        perception = {
            "confidence": "LOW",
            "artifact_path": "slide.png",
            "visual_elements": [],
        }
        conf = build_perception_confirmation(1, perception)
        assert "no details extracted" in conf["summary"]


# ===========================================================================
# AC4: LOW-confidence retry (one attempt)
# ===========================================================================

class TestRetryLowConfidence:

    def test_retry_returns_new_result(self):
        slide = _make_slide(1)
        original = _make_perception(1, confidence="LOW")

        retried = retry_low_confidence(
            slide, original, perceive_fn=_mock_perceive_high,
        )

        assert retried["confidence"] == "HIGH"

    def test_retry_carries_slide_metadata(self):
        slide = _make_slide(1, slide_id="s-alpha")
        original = _make_perception(1, confidence="LOW")

        retried = retry_low_confidence(
            slide, original, perceive_fn=_mock_perceive_high,
        )

        assert retried["slide_id"] == "s-alpha"
        assert retried["card_number"] == 1

    def test_retry_records_retry_of_timestamp(self):
        slide = _make_slide(1)
        original = _make_perception(1, confidence="LOW")
        original["perception_timestamp"] = "2026-04-05T11:00:00Z"

        retried = retry_low_confidence(
            slide, original, perceive_fn=_mock_perceive_high,
        )

        assert retried["retry_of"] == "2026-04-05T11:00:00Z"

    def test_retry_bypasses_cache(self):
        slide = _make_slide(1)
        original = _make_perception(1, confidence="LOW")
        tracker = _PerceiveTracker("HIGH")

        retry_low_confidence(slide, original, perceive_fn=tracker)

        assert tracker.calls[0]["use_cache"] is False

    def test_retry_returns_original_on_exception(self):
        def failing_perceive(**kwargs):
            raise RuntimeError("Bridge crashed on retry")

        slide = _make_slide(1)
        original = _make_perception(1, confidence="LOW")

        retried = retry_low_confidence(
            slide, original, perceive_fn=failing_perceive,
        )

        # Should return original unchanged
        assert retried["confidence"] == "LOW"
        assert retried is original


# ===========================================================================
# AC5: Persistent LOW escalation to Marcus
# ===========================================================================

class TestCheckEscalationNeeded:

    def test_no_escalation_when_all_high(self):
        results = [_make_perception(1, confidence="HIGH"), _make_perception(2, confidence="HIGH")]
        esc = check_escalation_needed(results)

        assert esc["needs_escalation"] is False
        assert esc["low_confidence_slides"] == []
        assert esc["escalation_payload"] == {}

    def test_no_escalation_when_medium(self):
        results = [_make_perception(1, confidence="MEDIUM")]
        esc = check_escalation_needed(results)
        assert esc["needs_escalation"] is False

    def test_escalation_when_low_present(self):
        results = [
            _make_perception(1, confidence="HIGH"),
            _make_perception(2, confidence="LOW"),
        ]
        esc = check_escalation_needed(results)

        assert esc["needs_escalation"] is True
        assert len(esc["low_confidence_slides"]) == 1
        assert esc["low_confidence_slides"][0]["slide_id"] == "s-2"

    def test_escalation_payload_structure(self):
        low_result = _make_perception(3, confidence="LOW")
        low_result["retry_of"] = "2026-04-05T11:00:00Z"  # was retried

        esc = check_escalation_needed([low_result])

        payload = esc["escalation_payload"]
        assert payload["escalation_type"] == "perception_low_confidence"
        assert payload["requesting_agent"] == "irene"
        assert payload["gate"] == "G4"
        assert payload["slide_count"] == 1
        assert payload["low_confidence_slides"][0]["was_retried"] is True

    def test_multiple_low_slides_all_reported(self):
        results = [
            _make_perception(1, confidence="LOW"),
            _make_perception(2, confidence="LOW"),
            _make_perception(3, confidence="HIGH"),
        ]
        esc = check_escalation_needed(results)

        assert esc["needs_escalation"] is True
        assert len(esc["low_confidence_slides"]) == 2


# ===========================================================================
# AC6: Perception confirmed before narration (enforce_perception_contract)
# ===========================================================================

class TestEnforcePerceptionContract:

    def test_ready_when_perception_present_and_high(self):
        envelope = {
            "gary_slide_output": [_make_slide(1), _make_slide(2)],
            "perception_artifacts": [
                _make_perception(1, confidence="HIGH"),
                _make_perception(2, confidence="HIGH"),
            ],
        }

        result = enforce_perception_contract(envelope, perceive_fn=_mock_perceive_high)

        assert result["status"] == "ready"
        assert len(result["perception_artifacts"]) == 2
        assert len(result["confirmations"]) == 2
        assert result["errors"] == []

    def test_generates_inline_when_absent(self):
        envelope = {
            "gary_slide_output": [_make_slide(1), _make_slide(2)],
        }
        tracker = _PerceiveTracker("HIGH")

        result = enforce_perception_contract(envelope, perceive_fn=tracker)

        assert result["status"] == "ready"
        assert len(result["perception_artifacts"]) == 2
        # perceive called twice (once per slide)
        assert len(tracker.calls) == 2

    def test_retries_low_confidence_once(self):
        envelope = {
            "gary_slide_output": [_make_slide(1)],
        }
        # First call LOW, second call (retry) HIGH
        perceive_fn = _PerceiveLowThenHigh()

        result = enforce_perception_contract(envelope, perceive_fn=perceive_fn)

        assert result["status"] == "ready"
        # slide perceived twice: initial + retry
        path = "course-content/staging/card-01.png"
        assert perceive_fn.call_count[path] == 2
        assert result["perception_artifacts"][0]["confidence"] == "HIGH"

    def test_escalation_when_still_low_after_retry(self):
        envelope = {
            "gary_slide_output": [_make_slide(1)],
        }
        # Always returns LOW even after retry
        result = enforce_perception_contract(
            envelope, perceive_fn=_mock_perceive_low,
        )

        assert result["status"] == "escalation_needed"
        assert result["escalation"]["needs_escalation"] is True
        assert len(result["escalation"]["low_confidence_slides"]) == 1

    def test_error_when_gary_missing(self):
        envelope = {}

        result = enforce_perception_contract(envelope, perceive_fn=_mock_perceive_high)

        assert result["status"] == "error"
        assert any("gary_slide_output" in e for e in result["errors"])

    def test_mixed_confidence_slides(self):
        """Two slides: one HIGH, one persistently LOW."""
        call_results = {}

        def mixed_perceive(**kwargs):
            path = str(kwargs.get("artifact_path", ""))
            if "card-01" in path:
                return _mock_perceive_high(**kwargs)
            return _mock_perceive_low(**kwargs)

        envelope = {
            "gary_slide_output": [_make_slide(1), _make_slide(2)],
        }

        result = enforce_perception_contract(envelope, perceive_fn=mixed_perceive)

        assert result["status"] == "escalation_needed"
        # Slide 1 is fine, slide 2 is LOW
        assert result["perception_artifacts"][0]["confidence"] == "HIGH"
        assert result["perception_artifacts"][1]["confidence"] == "LOW"
        assert len(result["escalation"]["low_confidence_slides"]) == 1

    def test_confirmations_match_artifact_count(self):
        envelope = {
            "gary_slide_output": [_make_slide(1), _make_slide(2), _make_slide(3)],
        }

        result = enforce_perception_contract(
            envelope, perceive_fn=_mock_perceive_high,
        )

        assert len(result["confirmations"]) == 3
        for conf in result["confirmations"]:
            assert conf["modality"] == "image"
            assert conf["gate"] == "G4"
            assert conf["action"] == "proceeding"

    def test_does_not_mutate_original_envelope(self):
        original_artifacts = [_make_perception(1)]
        envelope = {
            "gary_slide_output": [_make_slide(1)],
            "perception_artifacts": original_artifacts,
        }

        result = enforce_perception_contract(envelope, perceive_fn=_mock_perceive_high)

        # Original list should not be mutated
        assert result["perception_artifacts"] is not original_artifacts

    def test_passes_run_id_through(self):
        envelope = {
            "gary_slide_output": [_make_slide(1)],
        }
        tracker = _PerceiveTracker("HIGH")

        enforce_perception_contract(
            envelope, run_id="RUN-TEST-42", perceive_fn=tracker,
        )

        assert tracker.calls[0]["run_id"] == "RUN-TEST-42"

    def test_empty_gary_output_returns_ready_with_no_artifacts(self):
        envelope = {
            "gary_slide_output": [],
        }

        result = enforce_perception_contract(
            envelope, perceive_fn=_mock_perceive_high,
        )

        assert result["status"] == "ready"
        assert result["perception_artifacts"] == []
        assert result["confirmations"] == []

    def test_pre_existing_low_perception_triggers_retry(self):
        """If envelope already has perception but at LOW, retry is attempted."""
        low_perception = _make_perception(1, confidence="LOW")
        envelope = {
            "gary_slide_output": [_make_slide(1)],
            "perception_artifacts": [low_perception],
        }

        result = enforce_perception_contract(
            envelope, perceive_fn=_mock_perceive_high,
        )

        # The pre-existing LOW should be retried via the retry path
        assert result["perception_artifacts"][0]["confidence"] == "HIGH"
        assert result["status"] == "ready"

    def test_partial_pre_existing_perception_generates_missing_slides(self):
        envelope = {
            "gary_slide_output": [_make_slide(1), _make_slide(2)],
            "perception_artifacts": [_make_perception(1, confidence="HIGH")],
        }
        tracker = _PerceiveTracker("HIGH")

        result = enforce_perception_contract(envelope, perceive_fn=tracker)

        assert result["status"] == "ready"
        assert len(result["perception_artifacts"]) == 2
        assert {artifact["slide_id"] for artifact in result["perception_artifacts"]} == {"s-1", "s-2"}
        assert len(tracker.calls) == 1
        assert tracker.calls[0]["artifact_path"].endswith("card-02.png")

    def test_missing_slide_coverage_fails_closed_when_generation_cannot_fill_gap(self):
        envelope = {
            "gary_slide_output": [_make_slide(1), {"slide_id": "s-2", "card_number": 2}],
            "perception_artifacts": [_make_perception(1, confidence="HIGH")],
        }

        result = enforce_perception_contract(envelope, perceive_fn=_mock_perceive_high)

        assert result["status"] == "error"
        assert any("s-2" in error for error in result["errors"])


class TestMotionPerceptionContract:

    def test_build_motion_perception_confirmation_mentions_motion_type(self):
        segment = {
            "id": "seg-02",
            "gary_slide_id": "s-2",
            "gary_card_number": 2,
            "motion_type": "video",
        }
        perception = _make_perception(2, confidence="HIGH")
        perception["temporal_event_density_summary"] = (
            "Moderate temporal event density: 4 keyframes across 12.0s. "
            "Narration should track the main transitions without calling every frame."
        )
        conf = build_motion_perception_confirmation(segment, perception)
        assert conf["modality"] == "video"
        assert "motion (video)" in conf["summary"]
        assert "temporal event density" in conf["summary"]

    def test_ready_for_mixed_static_and_motion_segments(self, tmp_path: Path):
        motion_asset = tmp_path / "slide-02_motion.mp4"
        motion_asset.write_bytes(b"video-bytes")
        segments = [
            {
                "id": "seg-01",
                "gary_slide_id": "s-1",
                "gary_card_number": 1,
                "motion_type": "static",
            },
            {
                "id": "seg-02",
                "gary_slide_id": "s-2",
                "gary_card_number": 2,
                "motion_type": "video",
                "motion_asset_path": str(motion_asset),
                "motion_status": "approved",
            },
            {
                "id": "seg-03",
                "gary_slide_id": "s-3",
                "gary_card_number": 3,
                "motion_type": "animation",
                "motion_asset_path": str(motion_asset),
                "motion_status": "approved",
            },
        ]

        result = enforce_motion_perception_contract(
            segments,
            perceive_motion_fn=_mock_perceive_high,
        )

        assert result["status"] == "ready"
        assert len(result["motion_perception_artifacts"]) == 2
        assert len(result["confirmations"]) == 2

    def test_fail_closed_when_motion_asset_missing(self):
        segments = [
            {
                "id": "seg-02",
                "gary_slide_id": "s-2",
                "gary_card_number": 2,
                "motion_type": "video",
                "motion_asset_path": "",
                "motion_status": "approved",
            }
        ]

        result = enforce_motion_perception_contract(
            segments,
            perceive_motion_fn=_mock_perceive_high,
        )

        assert result["status"] == "error"
        assert any("motion_asset_path" in error for error in result["errors"])

    def test_fail_closed_when_motion_asset_not_approved(self, tmp_path: Path):
        motion_asset = tmp_path / "slide-02_motion.mp4"
        motion_asset.write_bytes(b"video-bytes")
        segments = [
            {
                "id": "seg-02",
                "gary_slide_id": "s-2",
                "gary_card_number": 2,
                "motion_type": "video",
                "motion_asset_path": str(motion_asset),
                "motion_status": "generated",
            }
        ]

        result = enforce_motion_perception_contract(
            segments,
            perceive_motion_fn=_mock_perceive_high,
        )

        assert result["status"] == "error"
        assert any("motion_status 'approved'" in error for error in result["errors"])

    def test_motion_bridge_failure_returns_structured_error(self, tmp_path: Path):
        motion_asset = tmp_path / "slide-02_motion.mp4"
        motion_asset.write_bytes(b"video-bytes")
        segments = [
            {
                "id": "seg-02",
                "gary_slide_id": "s-2",
                "gary_card_number": 2,
                "motion_type": "video",
                "motion_asset_path": str(motion_asset),
                "motion_status": "approved",
            }
        ]

        def failing_perceive(**kwargs):
            raise RuntimeError("video bridge offline")

        result = enforce_motion_perception_contract(
            segments,
            perceive_motion_fn=failing_perceive,
        )

        assert result["status"] == "error"
        assert len(result["motion_perception_artifacts"]) == 1
        assert result["motion_perception_artifacts"][0]["confidence"] == "LOW"
        assert len(result["confirmations"]) == 1
        assert any("video bridge offline" in error for error in result["errors"])
