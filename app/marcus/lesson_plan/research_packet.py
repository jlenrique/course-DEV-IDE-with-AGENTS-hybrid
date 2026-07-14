"""W1 — coordinate-selected shared research packet reader (shape-pin).

M3-safe facade for workbook / trends / SPOC consumers. Reads the exact requested
Generic, Ask-A enrichment, or Ask-B hot-topics contribution from ``run.json``
through the existing lesson-plan disk seam — **no** ``app.marcus.orchestrator``
import and **no** packet builder.

Named consumer resolvers share one validation and digest path so every consumer
of the same packet identity witnesses the same ``packet_digest``.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, Literal

from app.marcus.lesson_plan.ask_a_enrichment import AskAContributionOutputV1
from app.marcus.lesson_plan.workbook_enrichment import (
    RunEnvelopeCorruptError,
    load_run_envelope,
)

# LOCAL literals — deliberately not imported from research_wiring (M3).
GENERIC_RESEARCH_SPECIALIST_ID: Final[str] = "research_wiring"
GENERIC_RESEARCH_NODE_ID: Final[str] = "04.55"
ASK_A_ENRICHMENT_SPECIALIST_ID: Final[str] = "ask_a_enrichment"
ASK_A_ENRICHMENT_NODE_ID: Final[str] = "07W.2"
ASK_B_HOT_TOPICS_SPECIALIST_ID: Final[str] = "ask_b_hot_topics"
ASK_B_HOT_TOPICS_NODE_ID: Final[str] = "07W.4"
_RESEARCH_ENTRIES_KEY: Final[str] = "research_entries"
_RESEARCH_INTAKE_KEY: Final[str] = "research_intake"
_TRIANGULATION_RECEIPT_KEY: Final[str] = "triangulation_receipt"

SCHEMA_VERSION: Final[str] = "research-packet.v1"

# R4 credibility shape — every usable row must carry these keys.
REQUIRED_ENTRY_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "citation_id",
        "source_ref",
        "provider",
        "source_id",
        "source_hash",
        "evidence_hierarchy_tier",
        "peer_reviewed",
        "provider_provenance",
        "triangulation_status",
    }
)

ConsumerId = Literal[
    "glossary_writer",
    "trends_projector",
    "irene_intake",
    "spoc_receipt",
    "future_collateral",
    "enrichment_pool",
    "hot_topics",
]

PacketStatus = Literal["absent", "empty", "ready", "degraded"]


class ResearchPacketShapeError(ValueError):
    """Raised when a consumer requires usable rows but the packet is unusable."""


@dataclass(frozen=True)
class ResearchPacket:
    """Durable run-scoped research packet for named consumers."""

    schema_version: str
    status: PacketStatus
    entries: tuple[dict[str, Any], ...]
    known_losses: tuple[str, ...]
    research_intake: dict[str, Any] | None
    triangulation_receipt: dict[str, Any] | None
    packet_digest: str
    node_id: str
    specialist_id: str

    @property
    def usable(self) -> bool:
        """True when at least one shape-valid entry is present."""
        return self.status in {"ready", "degraded"} and bool(self.entries)


def _digest_payload(payload: dict[str, Any]) -> str:
    canonical = json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _entry_shape_ok(entry: Any) -> bool:
    if not isinstance(entry, dict):
        return False
    for key in REQUIRED_ENTRY_FIELDS:
        if key not in entry:
            return False
    provenance = entry.get("provider_provenance")
    if not isinstance(provenance, list) or not provenance:
        return False
    tier = entry.get("evidence_hierarchy_tier")
    if not isinstance(tier, str) or not tier.strip():
        return False
    for required_str in ("citation_id", "source_ref", "provider", "source_id", "source_hash"):
        value = entry.get(required_str)
        if not isinstance(value, str) or not value.strip():
            return False
    return True


def _empty_packet(
    *,
    status: PacketStatus,
    specialist_id: str,
    node_id: str,
    known_losses: tuple[str, ...] = (),
) -> ResearchPacket:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "entries": [],
        "known_losses": list(known_losses),
        "research_intake": None,
        "triangulation_receipt": None,
    }
    return ResearchPacket(
        schema_version=SCHEMA_VERSION,
        status=status,
        entries=(),
        known_losses=known_losses,
        research_intake=None,
        triangulation_receipt=None,
        packet_digest=_digest_payload(payload),
        node_id=node_id,
        specialist_id=specialist_id,
    )


def load_research_packet(
    run_dir: Path,
    *,
    specialist_id: str = GENERIC_RESEARCH_SPECIALIST_ID,
    node_id: str = GENERIC_RESEARCH_NODE_ID,
) -> ResearchPacket:
    """Load the shared research packet from ``<run_dir>/run.json``.

    - Missing ``run.json`` / missing contribution → ``status=absent`` or ``empty``
      (honest empty; never fabricate).
    - Corrupt ``run.json`` → :class:`RunEnvelopeCorruptError` (fail-loud).
    - Malformed entries → dropped into ``known_losses``; remaining usable rows
      yield ``ready`` or ``degraded``.
    """
    if node_id is None:
        raise ResearchPacketShapeError(
            "node_id must identify an exact research-packet contribution"
        )

    envelope = load_run_envelope(run_dir)
    if envelope is None:
        return _empty_packet(
            status="absent",
            specialist_id=specialist_id,
            node_id=node_id,
            known_losses=("run_json_absent",),
        )

    contribution = envelope.get_contribution(specialist_id, node_id=node_id)
    if contribution is None:
        missing_loss = (
            "research_wiring_contribution_absent"
            if (
                specialist_id == GENERIC_RESEARCH_SPECIALIST_ID
                and node_id == GENERIC_RESEARCH_NODE_ID
            )
            else f"packet_contribution_absent:{specialist_id}@{node_id}"
        )
        return _empty_packet(
            status="empty",
            specialist_id=specialist_id,
            node_id=node_id,
            known_losses=(missing_loss,),
        )

    output = contribution.output if isinstance(contribution.output, dict) else {}
    if (
        specialist_id == ASK_A_ENRICHMENT_SPECIALIST_ID
        and node_id == ASK_A_ENRICHMENT_NODE_ID
    ):
        try:
            strict_output = AskAContributionOutputV1.model_validate_json(
                json.dumps(output, separators=(",", ":")), strict=True
            )
        except ValueError as exc:
            raise ResearchPacketShapeError(
                f"Ask-A contribution contract is invalid: {exc}"
            ) from exc
        output = strict_output.model_dump(mode="json")
    raw_entries = output.get(_RESEARCH_ENTRIES_KEY)
    if raw_entries is None:
        return _empty_packet(
            status="empty",
            specialist_id=specialist_id,
            node_id=node_id,
            known_losses=("research_entries_key_absent",),
        )
    if not isinstance(raw_entries, list):
        raise ResearchPacketShapeError(
            f"research_entries must be a list, got {type(raw_entries).__name__}"
        )

    producer_losses: list[str] = []
    if "known_losses" in output:
        raw_losses = output["known_losses"]
        if not isinstance(raw_losses, list):
            raise ResearchPacketShapeError("known_losses must be an ordered list")
        for index, loss in enumerate(raw_losses):
            if (
                not isinstance(loss, str)
                or not loss.strip()
                or loss != loss.strip()
                or any(mark in loss for mark in ("\r", "\n", "\u2028", "\u2029"))
            ):
                raise ResearchPacketShapeError(
                    f"known_losses[{index}] must be a nonblank single-line string"
                )
            if loss not in producer_losses:
                producer_losses.append(loss)

    usable: list[dict[str, Any]] = []
    reader_losses: list[str] = []
    for index, entry in enumerate(raw_entries):
        if _entry_shape_ok(entry):
            usable.append(dict(entry))
        else:
            reader_losses.append(f"entry_shape_invalid:{index}")

    intake = output.get(_RESEARCH_INTAKE_KEY)
    intake_dict = intake if isinstance(intake, dict) else None
    receipt = output.get(_TRIANGULATION_RECEIPT_KEY)
    receipt_dict = receipt if isinstance(receipt, dict) else None

    if not usable and not raw_entries:
        status: PacketStatus = "empty"
        reader_losses.append("research_entries_empty")
    elif not usable:
        status = "empty"
        reader_losses.append("research_entries_all_invalid")
    elif producer_losses or reader_losses:
        status = "degraded"
    else:
        status = "ready"

    losses = list(producer_losses)
    for loss in reader_losses:
        if loss not in losses:
            losses.append(loss)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "entries": usable,
        "known_losses": losses,
        "research_intake": intake_dict,
        "triangulation_receipt": receipt_dict,
    }
    return ResearchPacket(
        schema_version=SCHEMA_VERSION,
        status=status,
        entries=tuple(usable),
        known_losses=tuple(losses),
        research_intake=intake_dict,
        triangulation_receipt=receipt_dict,
        packet_digest=_digest_payload(payload),
        node_id=node_id,
        specialist_id=specialist_id,
    )


def resolve_for_consumer(
    run_dir: Path,
    consumer_id: ConsumerId,
    *,
    require_usable: bool = False,
    specialist_id: str = GENERIC_RESEARCH_SPECIALIST_ID,
    node_id: str = GENERIC_RESEARCH_NODE_ID,
) -> ResearchPacket:
    """Resolve the shared packet for a named consumer (same digest for all).

    ``require_usable=True`` fails closed when no shape-valid entries exist
    (glossary/trends writers that must not invent scholarship).
    """
    packet = load_research_packet(
        run_dir,
        specialist_id=specialist_id,
        node_id=node_id,
    )
    if require_usable and not packet.usable:
        raise ResearchPacketShapeError(
            f"consumer {consumer_id!r} requires usable research rows; "
            f"status={packet.status} known_losses={list(packet.known_losses)}"
        )
    return packet


def resolve_for_glossary_writer(
    run_dir: Path, *, require_usable: bool = False
) -> ResearchPacket:
    """Glossary encyclopedia writer consumer."""
    return resolve_for_consumer(
        run_dir, "glossary_writer", require_usable=require_usable
    )


def resolve_for_trends_projector(
    run_dir: Path, *, require_usable: bool = False
) -> ResearchPacket:
    """Research-trends / hot-topics projector consumer."""
    return resolve_for_consumer(
        run_dir, "trends_projector", require_usable=require_usable
    )


def resolve_for_enrichment_pool(
    run_dir: Path, *, require_usable: bool = False
) -> ResearchPacket:
    """Resolve only the Ask-A enrichment packet."""
    return resolve_for_consumer(
        run_dir,
        "enrichment_pool",
        require_usable=require_usable,
        specialist_id=ASK_A_ENRICHMENT_SPECIALIST_ID,
        node_id=ASK_A_ENRICHMENT_NODE_ID,
    )


def resolve_for_hot_topics(
    run_dir: Path, *, require_usable: bool = False
) -> ResearchPacket:
    """Resolve only the Ask-B hot-topics packet."""
    return resolve_for_consumer(
        run_dir,
        "hot_topics",
        require_usable=require_usable,
        specialist_id=ASK_B_HOT_TOPICS_SPECIALIST_ID,
        node_id=ASK_B_HOT_TOPICS_NODE_ID,
    )


__all__ = [
    "ASK_A_ENRICHMENT_NODE_ID",
    "ASK_A_ENRICHMENT_SPECIALIST_ID",
    "ASK_B_HOT_TOPICS_NODE_ID",
    "ASK_B_HOT_TOPICS_SPECIALIST_ID",
    "GENERIC_RESEARCH_NODE_ID",
    "GENERIC_RESEARCH_SPECIALIST_ID",
    "REQUIRED_ENTRY_FIELDS",
    "SCHEMA_VERSION",
    "ConsumerId",
    "PacketStatus",
    "ResearchPacket",
    "ResearchPacketShapeError",
    "RunEnvelopeCorruptError",
    "load_research_packet",
    "resolve_for_consumer",
    "resolve_for_enrichment_pool",
    "resolve_for_glossary_writer",
    "resolve_for_trends_projector",
    "resolve_for_hot_topics",
]
