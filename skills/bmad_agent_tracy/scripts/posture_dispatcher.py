"""
Tracy Posture Dispatcher

Shapes RetrievalIntents for three postures: embellish, corroborate, gap-fill.
Production seam for intent shaping is ``DeterministicPostureSelector`` in
``research_wiring`` (Agentic Research Foundations R1). This class is a thin
façade so Epic 28 posture call sites and the Irene bridge share one shaping
path — no dual fantasy, no Tracy→HTTP bypass.
"""

from __future__ import annotations

from typing import Any


class PostureDispatcher:
    """Dispatcher for Tracy's three research postures."""

    def __init__(self, dispatcher: Any = None) -> None:
        """Accept an optional Texas retrieval dispatcher (wired for live fetch).

        Intent shaping does not require ``dispatcher``; live ``dispatch`` does.
        """
        self.dispatcher = dispatcher
        self._selector: Any | None = None

    def _posture_selector(self) -> Any:
        if self._selector is None:
            from app.marcus.orchestrator.research_wiring import (  # noqa: PLC0415
                DeterministicPostureSelector,
            )

            self._selector = DeterministicPostureSelector()
        return self._selector

    def select_posture(self, brief: dict[str, Any]) -> Any:
        """Shape a gap/goal brief into a ``RetrievalIntent`` (production seam)."""
        return self._posture_selector().select_posture(brief)

    def embellish(self, target_element: str, enrichment_type: str) -> Any:
        """
        Embellish posture: Add enrichment content.

        Input Shape: target_element (plan_unit/event), enrichment_type
        Output Shape: RetrievalIntent (shaped; live fetch via Texas when dispatched)
        Success Signal: intent shaped with posture=embellish (detective ON)
        Failure Mode: RetrievalProviderUnavailableError from selector
        """
        return self.select_posture(
            {
                "gap_type": "enrichment",
                "target_element": target_element,
                "enrichment_type": enrichment_type,
                "scope_decision": "in-scope",
                "posture": "embellish",
            }
        )

    def corroborate(
        self,
        claim: str,
        source_context: str,
        *,
        evidence_bolster: bool | None = None,
    ) -> Any:
        """
        Corroborate posture: Confirm/disconfirm claims.

        Input Shape: claim, source_context; optional evidence_bolster
        Output Shape: RetrievalIntent (shaped; live fetch via Texas when dispatched)
        Success Signal: intent shaped; bolster ON ⇒ scite+consensus cross_validate
        Failure Mode: RetrievalProviderUnavailableError from selector
        """
        brief: dict[str, Any] = {
            "gap_type": "evidence",
            "claim": claim,
            "source_context": source_context,
            "scope_decision": "in-scope",
            "posture": "corroborate",
        }
        if evidence_bolster is not None:
            brief["evidence_bolster"] = evidence_bolster
        return self.select_posture(brief)

    def gap_fill(self, gap_description: str, content_type: str, scope: str) -> Any:
        """
        Gap-Fill posture: Fill knowledge gaps.

        Input Shape: gap_description, content_type, scope
        Output Shape: RetrievalIntent (shaped; live fetch via Texas when dispatched)
        Success Signal: intent shaped with posture=gap_fill (detective ON)
        Failure Mode: RetrievalProviderUnavailableError from selector
        """
        return self.select_posture(
            {
                "gap_type": "missing_concept",
                "gap_description": gap_description,
                "content_type": content_type,
                "scope": scope,
                "scope_decision": "in-scope",
                "posture": "gap_fill",
            }
        )
