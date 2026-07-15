"""Shared 37.2b test substrate — every shape derives from the two real runs.

Live-shape-fixtures-only (protocol plank 2): the skeleton comes verbatim from
``runs/a940c5eb…/workbook-brief.v1.json`` and the pool from that run's
completed Ask-A journal output; mutants are mutated COPIES of those frozen
shapes, never hand-invented structures.
"""

from __future__ import annotations

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.marcus.lesson_plan.ask_a_enrichment import AskAKnowledgeEntryV1
from app.marcus.lesson_plan.deep_dive_enrichment import (
    DeepDiveEnrichedWriterResult,
    DeepDiveEnrichmentRequestV1,
    DeepDiveOverlayCoveredInputV1,
    DeepDiveSkeletonBindingV1,
    EnrichedDeepDiveClaim,
    EnrichedDeepDiveSection,
    enrichment_request_digest,
    skeleton_binding_from_result,
)
from app.marcus.lesson_plan.prework_artifact import read_workbook_brief
from app.models.runtime.production_envelope import (
    ProductionEnvelope,
    SpecialistContribution,
)
from app.models.runtime.production_trial_envelope import ProductionTrialEnvelope

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "deep_dive_enrichment_37_2b"
BRIEF_FIXTURE = FIXTURE_DIR / "workbook-brief.v1.json"
ASK_A_OUTPUT_FIXTURE = FIXTURE_DIR / "ask-a-contribution-output.v1.json"
RENDERED_WORKBOOK_FIXTURE = FIXTURE_DIR / "u01@1.rendered-workbook.md"
FIXTURE_MANIFEST = FIXTURE_DIR / "fixture-manifest.json"

LIVE_CITATION_ID = "ask-a-cite-001"


def _validate_json(model: type, payload: object) -> Any:
    return model.model_validate_json(
        json.dumps(payload, separators=(",", ":"), ensure_ascii=False), strict=True
    )


def ask_a_output_payload() -> dict[str, Any]:
    return json.loads(ASK_A_OUTPUT_FIXTURE.read_text(encoding="utf-8"))


def live_pool_entry() -> AskAKnowledgeEntryV1:
    return _validate_json(
        AskAKnowledgeEntryV1, ask_a_output_payload()["research_entries"][0]
    )


def live_skeleton_binding() -> DeepDiveSkeletonBindingV1:
    brief = read_workbook_brief(FIXTURE_DIR)
    skeleton = brief.payload.deep_dive_skeleton
    assert skeleton is not None
    return skeleton_binding_from_result(skeleton)


def mutated_pool_entry(**overrides: Any) -> AskAKnowledgeEntryV1:
    """A mutated COPY of the frozen live pool row (never a hand-invented shape)."""
    payload = live_pool_entry().model_dump(mode="json")
    payload.update(overrides)
    return _validate_json(AskAKnowledgeEntryV1, payload)


def empty_overlay() -> DeepDiveOverlayCoveredInputV1:
    return DeepDiveOverlayCoveredInputV1(
        card_present=False,
        covered_learning_objectives=(),
        covered_exercise_facts=(),
    )


def make_request(
    *,
    skeleton: DeepDiveSkeletonBindingV1 | None = None,
    pool_rows: tuple[AskAKnowledgeEntryV1, ...] | None = None,
    pool_status: str | None = None,
    pool_scope_digest: str | None = "from-rows",
    pool_known_losses: tuple[str, ...] = (),
    excluded_citation_ids: tuple[str, ...] = (),
    overlay: DeepDiveOverlayCoveredInputV1 | None = None,
    pool_packet_digest: str = "a" * 64,
) -> DeepDiveEnrichmentRequestV1:
    skeleton = skeleton or live_skeleton_binding()
    if pool_rows is None:
        pool_rows = (live_pool_entry(),)
    if pool_status is None:
        pool_status = "ready" if pool_rows else "empty"
    if pool_scope_digest == "from-rows":
        pool_scope_digest = pool_rows[0].scope_digest if pool_rows else None
    intake = ask_a_output_payload()["research_intake"]
    payload: dict[str, Any] = {
        "schema_version": "deep-dive-enrichment-request.v1",
        "skeleton": skeleton.model_dump(mode="json"),
        "pool_packet_digest": pool_packet_digest,
        "pool_status": pool_status,
        "pool_scope_digest": pool_scope_digest,
        "pool_rows": [row.model_dump(mode="json") for row in pool_rows],
        "pool_known_losses": list(pool_known_losses),
        "excluded_citation_ids": list(excluded_citation_ids),
        "intake_covered_ability_ids": (
            list(intake["covered_ability_ids"]) if pool_rows else []
        ),
        "intake_uncovered_ability_ids": (
            list(intake["uncovered_ability_ids"]) if pool_rows else []
        ),
        "overlay_covered": (overlay or empty_overlay()).model_dump(mode="json"),
    }
    payload["request_digest"] = enrichment_request_digest(payload)
    return _validate_json(DeepDiveEnrichmentRequestV1, payload)


ENRICHMENT_SENTENCE = (
    "Digital health tools still face many challenges and hurdles on the path "
    "to healthcare quality."
)
ENRICHMENT_ABILITY = "lo-g0-005"  # the live row supports this ability


def enriched_candidate(
    request: DeepDiveEnrichmentRequestV1,
    *,
    enrichment_ability: str = ENRICHMENT_ABILITY,
    enrichment_text: str | None = None,
    citation_refs: tuple[str, ...] = (LIVE_CITATION_ID,),
    drop_skeleton_claims_for: str | None = None,
    extra_enrichment_claims: tuple[tuple[str, tuple[str, ...]], ...] = (),
) -> DeepDiveEnrichedWriterResult:
    """Verbatim-preserving enriched candidate + one cited sentence (live-shape).

    Bold-term metadata is derived from the constructed prose (what an honest
    writer emits), so gate-side bold checks are reachable without bypassing the
    candidate model. ``extra_enrichment_claims`` appends further
    ``(text, citation_refs)`` enrichment claims under the same ability (for
    multi-claim mutants such as the R16 cross-claim laundering pin).
    """
    if enrichment_text is None:
        markers = " ".join(f"[{ref}]" for ref in citation_refs)
        enrichment_text = f"{ENRICHMENT_SENTENCE} {markers}".strip()
    sections: list[EnrichedDeepDiveSection] = []
    counter = 0
    for section in request.skeleton.sections:
        claims: list[EnrichedDeepDiveClaim] = []
        if section.ability_id != drop_skeleton_claims_for:
            for claim in section.claims:
                claims.append(
                    EnrichedDeepDiveClaim(
                        enriched_claim_id=f"en:{counter}",
                        text=claim.text,
                        role="skeleton",
                        source_claim_refs=claim.source_claim_refs,
                        citation_refs=(),
                    )
                )
                counter += 1
        if section.ability_id == enrichment_ability or (
            section.ability_id == drop_skeleton_claims_for and not claims
        ):
            claims.append(
                EnrichedDeepDiveClaim(
                    enriched_claim_id=f"en:{counter}",
                    text=enrichment_text,
                    role="enrichment",
                    source_claim_refs=(),
                    citation_refs=citation_refs,
                )
            )
            counter += 1
            if section.ability_id == enrichment_ability:
                for extra_text, extra_refs in extra_enrichment_claims:
                    claims.append(
                        EnrichedDeepDiveClaim(
                            enriched_claim_id=f"en:{counter}",
                            text=extra_text,
                            role="enrichment",
                            source_claim_refs=(),
                            citation_refs=extra_refs,
                        )
                    )
                    counter += 1
        sections.append(
            EnrichedDeepDiveSection(
                ability_id=section.ability_id,
                prose=" ".join(claim.text for claim in claims),
                claims=tuple(claims),
            )
        )
    from app.marcus.lesson_plan.deep_dive_enrichment import strip_citation_markers
    from app.marcus.lesson_plan.deep_dive_projection import (
        BoldTermMarker,
        _marked_terms,
    )

    bold_terms = tuple(
        BoldTermMarker(term=term)
        for term in _marked_terms(
            tuple(strip_citation_markers(section.prose) for section in sections)
        )
    )
    return DeepDiveEnrichedWriterResult(
        status="enriched",
        sections=tuple(sections),
        bold_terms=bold_terms,
        known_losses=(),
        marker=None,
    )


def degraded_candidate(loss: str) -> DeepDiveEnrichedWriterResult:
    from app.marcus.lesson_plan.deep_dive_enrichment import (
        DEEP_DIVE_ENRICHMENT_DEGRADED_MARKER,
        DEEP_DIVE_ENRICHMENT_UNAVAILABLE_MARKER,
    )

    degraded = loss in {
        "deep_dive_enrichment_pool_empty",
        "deep_dive_enrichment_pool_unused",
    }
    return DeepDiveEnrichedWriterResult(
        status="degraded" if degraded else "unavailable",
        sections=(),
        bold_terms=(),
        known_losses=(loss,),
        marker=(
            DEEP_DIVE_ENRICHMENT_DEGRADED_MARKER
            if degraded
            else DEEP_DIVE_ENRICHMENT_UNAVAILABLE_MARKER
        ),
    )


def install_brief(run_dir: Path) -> None:
    shutil.copy2(BRIEF_FIXTURE, run_dir / "workbook-brief.v1.json")


def install_run_json(
    run_dir: Path,
    *,
    ask_a_output: dict[str, Any] | None = None,
    extra_contributions: tuple[tuple[str, str, dict[str, Any], str], ...] = (),
) -> ProductionTrialEnvelope:
    """Write a minimal ``run.json`` carrying the real Ask-A contribution."""
    production = ProductionEnvelope(trial_id=uuid4())
    if ask_a_output is not None:
        production.add_contribution(
            SpecialistContribution.from_output(
                specialist_id="ask_a_enrichment",
                node_id="07W.2",
                output=ask_a_output,
                model_used="deterministic-ask-a-research-wiring",
            )
        )
    for specialist_id, node_id, output, model_used in extra_contributions:
        production.add_contribution(
            SpecialistContribution.from_output(
                specialist_id=specialist_id,
                node_id=node_id,
                output=output,
                model_used=model_used,
            )
        )
    trial = ProductionTrialEnvelope(
        trial_id=production.trial_id,
        preset="production",
        corpus_path="fixture",
        operator_id="operator_test",
        started_at=datetime(2026, 7, 15, tzinfo=UTC),
        status="in-flight",
        production_clone_launch_evidence=True,
        production_envelope=production,
    )
    (run_dir / "run.json").write_text(trial.model_dump_json(indent=2) + "\n", "utf-8")
    return trial
