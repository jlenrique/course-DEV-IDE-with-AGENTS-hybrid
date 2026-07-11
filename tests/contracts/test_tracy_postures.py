"""
Tests for Tracy postures and contracts.

Tests the four-part contracts for embellish, corroborate, gap-fill postures.
"""

import sys
from unittest.mock import Mock

import pytest

sys.path.insert(0, ".")

from scripts.utilities.tracy_vocab_lockstep import validate_suggested_resources
from skills.bmad_agent_tracy.scripts.posture_dispatcher import PostureDispatcher


class TestPostureDispatcher:
    """Test the PostureDispatcher class (R1: shapes RetrievalIntents)."""

    @pytest.fixture
    def dispatcher(self):
        """Create a dispatcher (Texas fetch optional; shaping is local)."""
        mock_dispatcher = Mock()
        return PostureDispatcher(mock_dispatcher)

    def test_embellish_shapes_intent(self, dispatcher, monkeypatch):
        """Embellish emits a Scite RetrievalIntent (no NotImplementedError)."""
        monkeypatch.setenv("MARCUS_RESEARCH_DETECTIVE_LIVE", "1")
        intent = dispatcher.embellish("target", "examples")
        assert intent.provider_hints[0].provider == "scite"
        assert intent.provider_hints[0].params["posture"] == "embellish"

    def test_corroborate_shapes_intent(self, dispatcher, monkeypatch):
        """Corroborate emits a Scite RetrievalIntent (no NotImplementedError)."""
        monkeypatch.setenv("MARCUS_RESEARCH_DETECTIVE_LIVE", "1")
        intent = dispatcher.corroborate("claim", "context")
        assert intent.provider_hints[0].provider == "scite"
        assert intent.provider_hints[0].params["posture"] == "corroborate"

    def test_gap_fill_shapes_intent(self, dispatcher, monkeypatch):
        """Gap-fill emits a Scite RetrievalIntent (no NotImplementedError)."""
        monkeypatch.setenv("MARCUS_RESEARCH_DETECTIVE_LIVE", "1")
        intent = dispatcher.gap_fill("gap", "type", "scope")
        assert intent.provider_hints[0].provider == "scite"
        assert intent.provider_hints[0].params["posture"] == "gap_fill"


class TestTracyVocabLockstep:
    """Test schema validation for Tracy outputs."""

    def test_valid_embellish_output(self):
        """Test validation of valid embellish output."""
        data = {
            "status": "success",
            "posture": "embellish",
            "intent_class": "narration_citation",
            "intent_detail": "Provides examples",
            "editorial_note": "Added because it illustrates the concept perfectly.",
            "provider_metadata": {"scite": {}},
            "input": {
                "target_element": "plan_unit_1",
                "enrichment_type": "examples",
            },
            "output": {
                "content_added": True,
                "content": "Example content here",
                "sources": ["source1", "source2"],
            },
            "provenance": {
                "retrieval_provider": "scite.ai",
                "query_terms": ["example", "query"],
                "timestamp": "2026-04-18T23:00:00Z",
            },
        }
        assert validate_suggested_resources(data)

    def test_valid_corroborate_output(self):
        """Test validation of valid corroborate output."""
        data = {
            "status": "success",
            "posture": "corroborate",
            "intent_class": "supporting_evidence",
            "intent_detail": "Validates the claim",
            "editorial_note": "Strongly corroborates the finding with recent study.",
            "provider_metadata": {"scite": {}},
            "input": {
                "claim": "Test claim",
                "source_context": "Context here",
            },
            "output": {
                "evidence_found": True,
                "classification": "supporting",
                "confidence_score": 0.8,
                "sources": ["source1"],
            },
            "provenance": {
                "retrieval_provider": "scite.ai",
                "query_terms": ["claim", "verification"],
                "timestamp": "2026-04-18T23:00:00Z",
            },
        }
        assert validate_suggested_resources(data)

    def test_valid_gap_fill_output(self):
        """Test validation of valid gap-fill output."""
        data = {
            "status": "success",
            "posture": "gap-fill",
            "intent_class": "background_primary",
            "intent_detail": "Fills the context gap",
            "editorial_note": "A highly cited overview to fill the unit gap.",
            "provider_metadata": {"scite": {}},
            "input": {
                "gap_description": "Missing background",
                "content_type": "explanation",
                "scope": "unit",
            },
            "output": {
                "gap_filled": True,
                "content": "Gap filler content",
                "relevance_score": 0.9,
                "sources": ["source1"],
            },
            "provenance": {
                "retrieval_provider": "scite.ai",
                "query_terms": ["background", "gap"],
                "timestamp": "2026-04-18T23:00:00Z",
            },
        }
        assert validate_suggested_resources(data)

    def test_invalid_posture(self):
        """Test validation fails for invalid posture."""
        data = {
            "status": "success",
            "posture": "invalid_posture",
            "input": {},
            "output": {},
        }
        assert not validate_suggested_resources(data)

    def test_missing_required_fields(self):
        """Test validation fails when required fields are missing."""
        data = {
            "status": "success",
            "posture": "embellish",
            "input": {},
            # Missing output and editorial metadata
        }
        assert not validate_suggested_resources(data)

    def test_valid_failure_mode(self):
        """Test validation of failed status."""
        data = {
            "status": "failed",
            "reason": "API timeout",
            "posture": "embellish",
            "input": {
                "target_element": "plan_unit_1",
                "enrichment_type": "examples",
            },
        }
        assert validate_suggested_resources(data)
