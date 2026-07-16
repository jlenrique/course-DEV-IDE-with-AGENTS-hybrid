"""Consumer-side pin: ``reject_model_prior_topic`` vs the Ask-B packet (38.2 AC 4).

Deliberately a NEW module — NOT ``test_trends_w3.py`` — so 39-2's
``trends_inputs_from_run`` re-point opens conflict-free (A-4). This story
does NOT re-point any trends consumer; the boundary pin below proves it.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from app.marcus.lesson_plan.research_packet import resolve_for_hot_topics
from app.marcus.lesson_plan.trends_projection import (
    project_trends_from_packet,
    reject_model_prior_topic,
    trends_inputs_from_run,
)
from app.models.runtime.production_envelope import (
    ProductionEnvelope,
    SpecialistContribution,
)
from app.models.runtime.production_trial_envelope import ProductionTrialEnvelope
from tests.unit.marcus.lesson_plan.test_research_packet_w1 import _valid_ask_b_output


def _write_ask_b_run(run_dir: Path) -> None:
    trial_id = UUID("12345678-1234-4234-8234-123456789abc")
    envelope = ProductionEnvelope(
        trial_id=trial_id,
        contributions=(
            SpecialistContribution.from_output(
                specialist_id="ask_b_hot_topics",
                output=_valid_ask_b_output(),
                model_used="fixture",
                node_id="07W.4",
                provenance="fixture",
            ),
        ),
        fixture_run=True,
    )
    started = datetime(2026, 7, 16, 12, 0, tzinfo=UTC)
    trial = ProductionTrialEnvelope(
        trial_id=trial_id,
        preset="explore",
        corpus_path="fixture",
        operator_id="ask-b-consumer-pin",
        started_at=started,
        completed_at=started,
        status="completed",
        production_clone_launch_evidence=True,
        production_envelope=envelope,
    )
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "run.json").write_text(trial.model_dump_json(), encoding="utf-8")


def test_reject_model_prior_topic_marks_injected_topic_unusable(
    tmp_path: Path,
) -> None:
    """Matrix row 4: an ungrounded/injected topic against the minted Ask-B
    packet is marked ``unusable`` — never forecasting theater."""
    _write_ask_b_run(tmp_path)
    packet = resolve_for_hot_topics(tmp_path, require_usable=True)
    callout = reject_model_prior_topic("quantum blockchain teleportation", packet)
    assert callout.confidence == "unusable"
    assert "packet-grounded" in callout.rationale


def test_grounded_topic_is_not_marked_unusable(tmp_path: Path) -> None:
    _write_ask_b_run(tmp_path)
    packet = resolve_for_hot_topics(tmp_path, require_usable=True)
    callout = reject_model_prior_topic("model drift", packet)
    assert callout.confidence != "unusable"


def test_projection_over_ask_b_packet_flags_injected_topics(tmp_path: Path) -> None:
    _write_ask_b_run(tmp_path)
    packet = resolve_for_hot_topics(tmp_path, require_usable=True)
    brief = project_trends_from_packet(
        packet, injected_topics=("forecast theater topic",)
    )
    unusable = [h for h in brief.hot_topics if h.confidence == "unusable"]
    assert len(unusable) == 1
    assert unusable[0].topic == "forecast theater topic"


def test_trends_inputs_from_run_is_not_repointed_to_ask_b(tmp_path: Path) -> None:
    """Boundary pin (38-2 AC 8): ``trends_inputs_from_run`` still reads the
    generic ``04.55`` packet — the re-point belongs to 39.2, not this story."""
    _write_ask_b_run(tmp_path)  # ONLY an Ask-B contribution exists
    brief = trends_inputs_from_run(tmp_path)
    assert brief.trends == ()
    assert brief.empty_reason is not None
