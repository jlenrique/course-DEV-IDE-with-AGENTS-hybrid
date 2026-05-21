from __future__ import annotations

import json
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import UUID

from app.marcus.orchestrator.dispatch_adapter import ProductionDispatchAdapter
from app.models.runtime.production_envelope import ProductionEnvelope
from app.models.state.model_resolution_entry import ModelResolutionEntry


def valid_cd_directive() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "experience_profile": "visual-led",
        "slide_mode_proportions": {
            "literal-text": 0.15,
            "literal-visual": 0.25,
            "creative": 0.60,
        },
        "narration_profile_controls": {
            "narrator_source_authority": "source-grounded",
            "slide_content_density": "adaptive",
            "elaboration_budget": "medium",
            "connective_weight": "balanced",
            "callback_frequency": "moderate",
            "visual_narration_coupling": "balanced",
            "rhetorical_richness": "balanced",
            "vocabulary_register": "professional",
            "arc_awareness": "medium",
            "narrative_tension": "medium",
            "emotional_coloring": "neutral",
        },
        "creative_rationale": "Favor rich visual storytelling for this profile.",
    }


class _FakeChat:
    def invoke(self, messages: list[dict[str, str]]) -> SimpleNamespace:
        assert messages
        return SimpleNamespace(
            content=json.dumps({"cd_directive": valid_cd_directive()}),
            usage_metadata={"input_tokens": 10, "output_tokens": 8},
        )


def fake_make_chat_model(specialist_id: str, **kwargs: object) -> SimpleNamespace:
    del kwargs
    return SimpleNamespace(
        chat=_FakeChat(),
        entry=ModelResolutionEntry(
            level="per_specialist",
            requested=None,
            resolved="gpt-5-nano",
            reason=f"composition fixture {specialist_id}",
            timestamp=datetime.now(UTC),
            cache_prefix_hash="c" * 64,
        ),
    )


class ComposedSpecialistChainHarness:
    """Run real scaffolded specialists through the production dispatch adapter."""

    def __init__(self, trial_id: UUID) -> None:
        self.adapter = ProductionDispatchAdapter()
        self.envelope = ProductionEnvelope(trial_id=trial_id)
        self.cd_input_payload: dict[str, object] | None = None

    def run_texas_to_cd(self) -> ProductionEnvelope:
        self.envelope = self.adapter.invoke_specialist(
            specialist_id="texas",
            envelope=self.envelope,
            dependency_map={},
            cost_usd=0.0,
        )
        self.envelope = self.adapter.invoke_specialist(
            specialist_id="cd",
            envelope=self.envelope,
            dependency_map={"source_bundle": "texas"},
            cost_usd=0.0,
        )
        self.cd_input_payload = self.adapter.last_input_payload
        return self.envelope
