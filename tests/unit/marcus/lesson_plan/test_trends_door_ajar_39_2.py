"""Story 39.2 — Door-Ajar re-point + empty-honesty + render-honesty pins.

Deterministic-consume only (no dispatch, no network). Matrix rows covered
here: 1 (real frozen pack + digest witness), 4 (no ``run.json``), 5 (strict
``completed_empty``, class b), 6 (all-rows-unusable at projection, class c),
7 (post-re-point ``reject_model_prior_topic``, J-3 obligation 2), 8 (legacy
resolver still generic, A-5), 13 (W-1/M-2 strictness upgrade reaching the
production seam), 15 (M-3 byte-determinism), plus AC 4/5 render-honesty pins
(caps/losses, anti-theater line, marker stripping, no fabrication in empty
renders). Rows 2/3 are the two CONSCIOUS FLIPS and live on the flipped
modules themselves (``test_ask_b_trends_consumer_pin_38_2.py`` /
``test_trends_w3.py``); rows 9-12, 14, 16 and the W-2 defaults-drift pin
live in ``tests/unit/scripts/test_workbook_deliverable_bar_39_2.py``.

Fixture grounding (M-5): row 1 derives from the REAL frozen 79f1920e pack
(digest-bound extract via ``tests.helpers.trends_39_2``); the hermetic unit
pins reuse the shared ``_valid_ask_b_output`` idiom (never re-derived).
"""

from __future__ import annotations

import hashlib
import re
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

import pytest
import yaml

from app.marcus.lesson_plan import research_packet as rp
from app.marcus.lesson_plan.ask_a_enrichment import canonical_digest
from app.marcus.lesson_plan.ask_b_hot_topics import (
    SCENE_IDENTITY_ABSENT_LOSS,
    AskBContributionOutputV1,
    AskBExecutionReceiptV1,
    AskBResearchIntakeV1,
    AskBRetrievalScopeV1,
)
from app.marcus.lesson_plan.deep_dive_projection import DeepDiveAbilityInput
from app.marcus.lesson_plan.research_packet import (
    ResearchPacket,
    ResearchPacketShapeError,
    resolve_for_hot_topics,
    resolve_for_trends_projector,
)
from app.marcus.lesson_plan.trends_projection import (
    TRENDS_WRITER_REQUIRED_MARKER,
    project_trends_from_packet,
    render_trends_markdown,
    trends_inputs_from_run,
)
from app.models.runtime.production_envelope import (
    ProductionEnvelope,
    SpecialistContribution,
)
from app.models.runtime.production_trial_envelope import ProductionTrialEnvelope
from tests.helpers.trends_39_2 import frozen_ask_b_output
from tests.unit.marcus.lesson_plan.test_research_packet_w1 import (
    _valid_ask_b_output,
    _valid_entry,
)

_ASK_B_CITE_RE = re.compile(r"ask-b-cite-[0-9]{3,}")


def _write_contributions(
    run_dir: Path, contributions: list[tuple[str, str, dict]]
) -> None:
    trial_id = UUID("12345678-1234-4234-8234-123456789abc")
    envelope = ProductionEnvelope(
        trial_id=trial_id,
        contributions=tuple(
            SpecialistContribution.from_output(
                specialist_id=specialist_id,
                output=output,
                model_used="fixture",
                node_id=node_id,
                provenance="fixture",
            )
            for specialist_id, node_id, output in contributions
        ),
        fixture_run=True,
    )
    started = datetime(2026, 7, 16, 12, 0, tzinfo=UTC)
    trial = ProductionTrialEnvelope(
        trial_id=trial_id,
        preset="explore",
        corpus_path="fixture",
        operator_id="trends-39-2",
        started_at=started,
        completed_at=started,
        status="completed",
        production_clone_launch_evidence=True,
        production_envelope=envelope,
    )
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "run.json").write_text(trial.model_dump_json(), encoding="utf-8")


def _completed_empty_ask_b_output() -> dict:
    """A strict ``completed_empty`` Ask-B contribution (class b): scene-absent
    scope loss leads, zero rows — the M-5/J-2 designed honest outcome."""
    scope_raw = {
        "schema_version": "ask-b-retrieval-scope.v1",
        "demand_digest": "sha256:" + "1" * 64,
        "workbook_brief_payload_digest": "sha256:" + "2" * 64,
        "abilities": (
            DeepDiveAbilityInput(ability_id="lo-1", text="Explain model drift"),
        ),
        "scene_digest": None,
        "scene_text": None,
        "query": "hot topics: [lo-1] Explain model drift",
        "query_digest": None,
        "posture": "hot_topics",
        "provider_config_fingerprint": "sha256:" + "4" * 64,
        "association_algorithm": "ask-b-association.v1",
        "known_scope_losses": (SCENE_IDENTITY_ABSENT_LOSS,),
    }
    scope_raw["query_digest"] = canonical_digest(scope_raw["query"])
    scope_raw["scope_digest"] = canonical_digest(
        {k: v for k, v in scope_raw.items() if k != "scope_digest"}
    )
    scope = AskBRetrievalScopeV1.model_validate(scope_raw, strict=True)
    receipt = AskBExecutionReceiptV1.build(
        scope=scope,
        dispatcher_invocations=1,
        provider_iterations=(1,),
        refinement_logs=(),
        provider_outcomes=("accepted",),
        provider_receipts=({"provider": "scite"},),
    )
    intake = AskBResearchIntakeV1.build(
        scope=scope, execution_receipt=receipt, entries=()
    )
    return AskBContributionOutputV1.build_completed(
        disposition="completed_empty",
        intake=intake,
        entries=(),
        known_losses=(SCENE_IDENTITY_ABSENT_LOSS,),
    ).model_dump(mode="json")


def _generic_packet(entries: list[dict], *, status: str = "ready") -> ResearchPacket:
    """Packet-object fixture (coordinate-agnostic projection surface)."""
    payload = {
        "schema_version": rp.SCHEMA_VERSION,
        "status": status,
        "entries": entries,
        "known_losses": [],
        "research_intake": None,
        "triangulation_receipt": None,
    }
    return ResearchPacket(
        schema_version=rp.SCHEMA_VERSION,
        status=status,  # type: ignore[arg-type]
        entries=tuple(entries),
        known_losses=(),
        research_intake=None,
        triangulation_receipt=None,
        packet_digest=rp._digest_payload(payload),
        node_id="07W.4",
        specialist_id="ask_b_hot_topics",
    )


# ---------------------------------------------------------------------------
# Row 1 — the re-point on the REAL frozen pack + the digest witness (M-5)
# ---------------------------------------------------------------------------


def test_row1_repointed_path_consumes_real_frozen_ask_b_pack(tmp_path: Path) -> None:
    """Matrix row 1: the re-pointed path yields a USABLE brief off the REAL
    79f1920e extract; every trend citation_id is ``ask-b-cite-###`` and lives
    in the packet's entry set."""
    _write_contributions(
        tmp_path, [("ask_b_hot_topics", "07W.4", frozen_ask_b_output())]
    )
    brief = trends_inputs_from_run(tmp_path)
    packet = resolve_for_hot_topics(tmp_path, require_usable=True)
    assert brief.usable
    assert brief.trends
    packet_ids = {entry["citation_id"] for entry in packet.entries}
    for claim in brief.trends:
        assert _ASK_B_CITE_RE.fullmatch(claim.citation_id)
        assert claim.citation_id in packet_ids


def test_row1_digest_witness_one_witness_rule(tmp_path: Path) -> None:
    """Matrix row 1 (digest witness): the brief the re-pointed path yields is
    exactly the projection of the packet a direct ``resolve_for_hot_topics``
    load witnesses (same ``packet_digest`` authority), and that digest is
    distinct from the generic ``04.55`` digest on the same run (extends the
    standing three-digest distinctness pin)."""
    generic = _valid_entry(citation_id="generic", source_hash="sha256:generic")
    _write_contributions(
        tmp_path,
        [
            ("research_wiring", "04.55", {"research_entries": [generic]}),
            ("ask_b_hot_topics", "07W.4", frozen_ask_b_output()),
        ],
    )
    direct = resolve_for_hot_topics(tmp_path, require_usable=True)
    reload = resolve_for_hot_topics(tmp_path, require_usable=True)
    assert direct.packet_digest == reload.packet_digest
    assert trends_inputs_from_run(tmp_path) == project_trends_from_packet(direct)
    generic_packet = resolve_for_trends_projector(tmp_path)
    assert generic_packet.packet_digest != direct.packet_digest
    # And the re-pointed brief is grounded in Ask-B rows, not the generic row.
    brief = trends_inputs_from_run(tmp_path)
    assert all(_ASK_B_CITE_RE.fullmatch(t.citation_id) for t in brief.trends)


# ---------------------------------------------------------------------------
# Row 8 — the legacy resolver stays generic (A-5; extends the resolver
# baseline pin at test_research_packet_w1.py L332)
# ---------------------------------------------------------------------------


def test_row8_resolve_for_trends_projector_still_resolves_generic(
    tmp_path: Path,
) -> None:
    """Matrix row 8: on a two-packet run the legacy resolver STILL resolves
    ``research_wiring@04.55`` — the re-point did not drag it along (its
    frozen live-evidence consumers keep their generic read)."""
    generic = _valid_entry(citation_id="generic", source_hash="sha256:generic")
    _write_contributions(
        tmp_path,
        [
            ("research_wiring", "04.55", {"research_entries": [generic]}),
            ("ask_b_hot_topics", "07W.4", _valid_ask_b_output()),
        ],
    )
    packet = resolve_for_trends_projector(tmp_path)
    assert (packet.specialist_id, packet.node_id) == ("research_wiring", "04.55")
    assert packet.entries[0]["citation_id"] == "generic"


# ---------------------------------------------------------------------------
# Rows 4/5/6 — the three empty classes (AC 4)
# ---------------------------------------------------------------------------


def test_row4_no_run_json_is_empty_honest_absent(tmp_path: Path) -> None:
    """Matrix row 4 / empty class (a, absent variant): a cold dir (no
    ``run.json``) projects an empty-honest brief off an ``absent`` packet;
    the render is the explicit-empty branch with zero fabrication.
    (``test_workbook_w4_empty_honesty`` pins the same coordinate unchanged —
    regression-proven, not flipped.)"""
    brief = trends_inputs_from_run(tmp_path)
    assert not brief.usable
    assert brief.trends == ()
    assert brief.empty_reason is not None
    assert "run_json_absent" in brief.known_losses
    rendered = render_trends_markdown(brief)
    assert f"*({brief.empty_reason})*" in rendered
    assert "#### Research trends" not in rendered
    assert "ask-b-cite-" not in rendered
    assert "Provenance:" not in rendered
    assert "https://doi.org/" not in rendered


def test_row5_completed_empty_is_designed_honest_outcome(tmp_path: Path) -> None:
    """Matrix row 5 / empty class (b): a strict ``completed_empty`` Ask-B
    contribution (zero rows, typed losses — "we asked, nothing usable came
    back") projects an empty-honest brief whose producer scope losses LEAD;
    the render is explicit-empty. This is the M-5/J-2 DESIGNED honest
    outcome — never treated as a defect (timeless defense pin per A-2)."""
    _write_contributions(
        tmp_path, [("ask_b_hot_topics", "07W.4", _completed_empty_ask_b_output())]
    )
    packet = resolve_for_hot_topics(tmp_path)
    assert packet.status == "empty"
    assert packet.known_losses[0] == SCENE_IDENTITY_ABSENT_LOSS
    assert "research_entries_empty" in packet.known_losses
    brief = trends_inputs_from_run(tmp_path)
    assert not brief.usable
    assert brief.trends == ()
    assert brief.empty_reason is not None
    assert brief.known_losses[0] == SCENE_IDENTITY_ABSENT_LOSS
    rendered = render_trends_markdown(brief)
    assert f"*({brief.empty_reason})*" in rendered
    assert "ask-b-cite-" not in rendered
    assert "https://doi.org/" not in rendered


def test_row6_all_rows_unusable_projection_layer_empty(tmp_path: Path) -> None:
    """Matrix row 6 / empty class (c): packet present but zero trends-eligible
    rows survive projection — the "research packet present but no
    trends-eligible rows" branch, with injected topics surfaced under the
    Rejected block.

    Substrate-honest note (defense-in-depth, NOT a plausible live-mint
    outcome): a contract-valid strict Ask-B entry always carries
    ``source_ref``/``citation_id``/provenance, so ``_confidence_for_entry``
    cannot return ``unusable`` for a live strict mint — this class is
    exercised at the projection layer with a packet-object fixture whose rows
    lack provenance."""
    no_provenance = {
        "citation_id": "ask-b-cite-001",
        "source_ref": "",  # blank source_ref: trends-ineligible
        "provider": "scite",
        "source_id": "10.1000/y",
        "title": "Model drift trends",
        "source_hash": "sha256:abc",
        "evidence_hierarchy_tier": "T4_peer_other",
        "peer_reviewed": True,
        "provider_provenance": ["scite"],
        "triangulation_status": "single_provider",
    }
    packet = _generic_packet([no_provenance], status="ready")
    brief = project_trends_from_packet(packet, injected_topics=("forecast theater",))
    assert not brief.usable
    assert brief.trends == ()
    assert brief.empty_reason is not None
    assert "no trends-eligible rows" in brief.empty_reason
    rendered = render_trends_markdown(brief)
    assert "#### Rejected / unusable topics" in rendered
    assert "forecast theater" in rendered
    assert "#### Research trends" not in rendered


# ---------------------------------------------------------------------------
# Row 7 — reject_model_prior_topic through the RE-POINTED path (J-3 obl. 2)
# ---------------------------------------------------------------------------


def test_row7_injected_ungrounded_topic_unusable_through_repointed_path(
    tmp_path: Path,
) -> None:
    """Matrix row 7: through ``trends_inputs_from_run(injected_topics=...)``
    against an Ask-B-only run, an ungrounded/injected topic is marked
    ``unusable``, renders ONLY under the Rejected block, contributes zero
    supporting citations, and never upgrades the brief on its own."""
    _write_contributions(tmp_path, [("ask_b_hot_topics", "07W.4", _valid_ask_b_output())])
    brief = trends_inputs_from_run(
        tmp_path, injected_topics=("quantum blockchain teleportation",)
    )
    unusable = [h for h in brief.hot_topics if h.confidence == "unusable"]
    assert len(unusable) == 1
    assert unusable[0].topic == "quantum blockchain teleportation"
    assert unusable[0].supporting_citation_ids == ()
    assert unusable[0].source_refs == ()
    rendered = render_trends_markdown(brief)
    rejected_at = rendered.find("#### Rejected / unusable topics")
    assert rejected_at != -1
    assert rendered.find("quantum blockchain teleportation") > rejected_at
    # The injected topic alone never upgrades usability: usable here comes
    # from the packet-grounded rows, not the injection.
    only_injected = project_trends_from_packet(
        _generic_packet([], status="empty"),
        injected_topics=("quantum blockchain teleportation",),
    )
    assert not only_injected.usable


def test_row7_grounded_topic_not_marked_unusable_through_repointed_path(
    tmp_path: Path,
) -> None:
    """Matrix row 7 (grounded half): a packet-grounded topic (title-matched
    against Ask-B entry titles) survives the coordinate change NOT-unusable —
    the grounded/ungrounded discrimination is intact post-re-point."""
    _write_contributions(tmp_path, [("ask_b_hot_topics", "07W.4", _valid_ask_b_output())])
    brief = trends_inputs_from_run(tmp_path, injected_topics=("model drift",))
    grounded = [h for h in brief.hot_topics if h.topic == "model drift"]
    assert grounded
    assert all(h.confidence != "unusable" for h in grounded)


# ---------------------------------------------------------------------------
# Row 13 — the W-1/M-2 strictness upgrade (fail-loud to the production seam)
# ---------------------------------------------------------------------------


def test_row13_forged_ask_b_contribution_fails_loud_through_consumer(
    tmp_path: Path,
) -> None:
    """Matrix row 13 (W-1 + M-2): a forged/malformed Ask-B contribution at
    ``ask_b_hot_topics@07W.4`` consumed through ``trends_inputs_from_run``
    raises ``ResearchPacketShapeError`` — the strict-reader fail-loud the
    re-pointed path inherits (the retired lenient generic read degraded
    silently). The story's ONLY new production failure mode."""
    _write_contributions(
        tmp_path,
        [("ask_b_hot_topics", "07W.4", {"research_entries": [_valid_entry()]})],
    )
    with pytest.raises(ResearchPacketShapeError, match="Ask-B"):
        trends_inputs_from_run(tmp_path)


def test_row13_forged_ask_b_reaches_production_call_at_act_seam(
    tmp_path: Path,
) -> None:
    """Matrix row 13 (production-seam half): the exception reaches the
    ``_act.py`` L1217 production call — ``build_workbook_inputs`` on a run
    whose Ask-B coordinate is forged propagates ``ResearchPacketShapeError``
    uncaught (nothing between the consumer and the seam swallows it)."""
    from app.marcus.lesson_plan.prework_artifact import read_workbook_brief
    from app.specialists.workbook_producer import _act as wb_act
    from tests.helpers.deep_dive_enrichment_37_2b import install_brief
    from tests.specialists.workbook_producer._run_fixture import (
        collateral_present,
        section,
    )

    run_dir = tmp_path / "run"
    (run_dir / "exports").mkdir(parents=True)
    (run_dir / "bundle").mkdir()
    (run_dir / "exports" / "segment-manifest-storyboard-b.yaml").write_text(
        yaml.safe_dump(
            {
                "segments": [
                    {
                        "segment_id": "seg-01",
                        "id": "seg-01",
                        "slide_id": "slide-01",
                        "narration_text": "Administrative waste is 25% of spend.",
                    }
                ]
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    (run_dir / "bundle" / "extracted.md").write_text(
        "Administrative waste is roughly 25% of total spend.\n", encoding="utf-8"
    )
    install_brief(run_dir)
    _write_contributions(
        run_dir,
        [
            (
                "irene_pass1",
                "03",
                {
                    "lesson_plan": {
                        "lesson_summary": "row 13 seam rig",
                        "plan_units": [],
                        "collateral": collateral_present(
                            [
                                section(
                                    "sec-u01",
                                    "u01",
                                    title="Reading the structural shift",
                                    deferred_depth="Row-13 seam rig depth.",
                                )
                            ]
                        ),
                    }
                },
            ),
            ("ask_b_hot_topics", "07W.4", {"research_entries": [_valid_entry()]}),
        ],
    )
    brief = read_workbook_brief(run_dir)
    with pytest.raises(ResearchPacketShapeError, match="Ask-B"):
        wb_act.build_workbook_inputs(run_dir, run_id="row13", validated_brief=brief)


# ---------------------------------------------------------------------------
# Row 15 — byte-determinism (M-3)
# ---------------------------------------------------------------------------


def test_row15_recompute_and_render_are_byte_deterministic(tmp_path: Path) -> None:
    """Matrix row 15 (M-3): the same ``run.json`` recomputed + rendered twice
    yields an identical packet digest, an equal brief, and a byte-identical
    rendered section."""
    _write_contributions(
        tmp_path, [("ask_b_hot_topics", "07W.4", frozen_ask_b_output())]
    )
    packet_a = resolve_for_hot_topics(tmp_path)
    packet_b = resolve_for_hot_topics(tmp_path)
    assert packet_a.packet_digest == packet_b.packet_digest
    brief_a = trends_inputs_from_run(tmp_path)
    brief_b = trends_inputs_from_run(tmp_path)
    assert brief_a == brief_b
    render_a = render_trends_markdown(brief_a).encode("utf-8")
    render_b = render_trends_markdown(brief_b).encode("utf-8")
    assert hashlib.sha256(render_a).hexdigest() == hashlib.sha256(render_b).hexdigest()
    assert render_a == render_b


# ---------------------------------------------------------------------------
# AC 4/5 render honesty — caps, anti-theater phrasing, marker stripping
# ---------------------------------------------------------------------------


def test_ac4_caps_are_bounded_with_visible_loss() -> None:
    """AC 4 bounded: the existing caps (``max_trends=5``, ``max_hot_topics=3``)
    hold with the visible ``trends_capped_at_5`` loss — no new knobs."""
    entries = [
        {
            "citation_id": f"ask-b-cite-{index:03d}",
            "source_ref": f"retrieval:scite:10.1000/t{index}",
            "provider": "scite",
            "source_id": f"10.1000/t{index}",
            "title": f"Trend topic number {index}",
            "source_hash": f"sha256:t{index}",
            "evidence_hierarchy_tier": "T4_peer_other",
            "peer_reviewed": True,
            "provider_provenance": ["scite"],
            "triangulation_status": "single_provider",
            "reliability_score": 0.5,
        }
        for index in range(1, 8)
    ]
    brief = project_trends_from_packet(_generic_packet(entries))
    assert len(brief.trends) == 5
    assert len([h for h in brief.hot_topics if h.confidence != "unusable"]) == 3
    assert "trends_capped_at_5" in brief.known_losses


def test_ac5_anti_theater_line_and_no_forecast_template(tmp_path: Path) -> None:
    """AC 5: the non-empty render carries the anti-theater sentinel line
    byte-identical, and the claim template's "not a forecast" honesty text
    survives; the ``TRENDS_WRITER_REQUIRED`` marker stays in the rationale
    FIELD and never reaches the rendered MD (``_strip_inline_comments``)."""
    _write_contributions(
        tmp_path, [("ask_b_hot_topics", "07W.4", frozen_ask_b_output())]
    )
    brief = trends_inputs_from_run(tmp_path)
    assert brief.usable
    rendered = render_trends_markdown(brief)
    assert (
        "*Bounded callout from wrangled evidence — not trend-forecasting theater.*"
        in rendered
    )
    assert "not a forecast" in rendered
    usable_topics = [h for h in brief.hot_topics if h.confidence != "unusable"]
    assert usable_topics
    assert all(
        TRENDS_WRITER_REQUIRED_MARKER in topic.rationale for topic in usable_topics
    )
    assert "TRENDS-WRITER-REQUIRED" not in rendered
    assert "<!--" not in rendered
