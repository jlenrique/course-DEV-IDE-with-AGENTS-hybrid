"""W3 — project research-packet rows into trends + hot-topics backmatter.

Produce-time only (not CollateralSpec). Trend claims and hot-topic callouts
MUST be grounded in wrangled packet rows — model-prior-only topics are rejected
or marked ``unusable`` (never polished fabricate). Bounded hot-topics callout
(not forecasting theater).

M3-safe: imports ``research_packet`` (lesson_plan), not ``marcus.orchestrator``.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from app.marcus.lesson_plan.research_packet import (
    ResearchPacket,
    resolve_for_trends_projector,
)

TRENDS_WRITER_REQUIRED_MARKER = "<!-- TRENDS-WRITER-REQUIRED -->"

Confidence = Literal["high", "medium", "low", "unusable"]

_STOPWORDS = frozenset(
    {
        "a",
        "an",
        "the",
        "and",
        "or",
        "of",
        "for",
        "to",
        "in",
        "on",
        "with",
        "from",
        "by",
        "as",
        "at",
        "into",
        "vs",
        "versus",
        "study",
        "effect",
        "effects",
        "using",
        "based",
    }
)


@dataclass(frozen=True)
class ResearchTrendClaim:
    """One packet-grounded research-trend claim for workbook backmatter."""

    claim_text: str
    citation_id: str
    source_ref: str
    source_id: str
    title: str
    confidence: Confidence
    evidence_hierarchy_tier: str
    peer_reviewed: bool | None
    provider_provenance: tuple[str, ...]
    triangulation_status: str
    reliability_score: float | None = None


@dataclass(frozen=True)
class HotTopicCallout:
    """Bounded hot-topic callout grounded in packet evidence."""

    topic: str
    rationale: str
    supporting_citation_ids: tuple[str, ...]
    source_refs: tuple[str, ...]
    confidence: Confidence


@dataclass(frozen=True)
class ResearchTrendsBrief:
    """Backmatter trends section payload (trends + hot-topics)."""

    trends: tuple[ResearchTrendClaim, ...]
    hot_topics: tuple[HotTopicCallout, ...]
    known_losses: tuple[str, ...]
    empty_reason: str | None = None

    @property
    def usable(self) -> bool:
        """True when at least one non-unusable trend or hot-topic is present."""
        trends_ok = any(t.confidence != "unusable" for t in self.trends)
        topics_ok = any(h.confidence != "unusable" for h in self.hot_topics)
        return trends_ok or topics_ok


def _topic_phrase(title: str, *, fallback: str) -> str:
    cleaned = re.sub(r"\s+", " ", (title or "").strip())
    if not cleaned:
        return fallback
    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9\-']*", cleaned)
    content = [w for w in words if w.lower() not in _STOPWORDS]
    if not content:
        return cleaned[:72]
    phrase = " ".join(content[:5])
    if len(phrase) > 64:
        phrase = phrase[:61].rstrip() + "…"
    return phrase


def _confidence_for_entry(entry: dict[str, Any]) -> Confidence:
    tri = str(entry.get("triangulation_status") or "").strip().lower()
    peer = entry.get("peer_reviewed")
    score = entry.get("reliability_score")
    if tri == "dual_provider" and peer is True:
        return "high"
    if tri == "dual_provider" or peer is True:
        return "medium"
    if isinstance(score, (int, float)) and float(score) >= 0.4:
        return "medium"
    if str(entry.get("source_ref") or "").strip():
        return "low"
    return "unusable"


def _provenance(entry: dict[str, Any]) -> tuple[str, ...]:
    raw = entry.get("provider_provenance")
    if isinstance(raw, (list, tuple)):
        return tuple(str(p) for p in raw if str(p).strip())
    provider = str(entry.get("provider") or "").strip()
    return (provider,) if provider else ()


def _trend_from_entry(entry: dict[str, Any]) -> ResearchTrendClaim | None:
    source_ref = str(entry.get("source_ref") or "").strip()
    citation_id = str(entry.get("citation_id") or "").strip()
    provenance = _provenance(entry)
    if not source_ref or not citation_id or not provenance:
        return None
    title = str(entry.get("title") or "").strip()
    topic = _topic_phrase(title, fallback=citation_id)
    confidence = _confidence_for_entry(entry)
    claim = (
        f"Indexed literature signals continuing attention to **{topic}**, "
        f"as framed by “{title or '(untitled)'}”. This trend claim is "
        f"research-informed from the wrangled packet row — not a forecast "
        f"and not a semantic claim audit."
    )
    peer = entry.get("peer_reviewed")
    score = entry.get("reliability_score")
    return ResearchTrendClaim(
        claim_text=claim,
        citation_id=citation_id,
        source_ref=source_ref,
        source_id=str(entry.get("source_id") or "").strip(),
        title=title,
        confidence=confidence,
        evidence_hierarchy_tier=str(
            entry.get("evidence_hierarchy_tier") or "T8_unknown"
        ).strip(),
        peer_reviewed=peer if isinstance(peer, bool) else None,
        provider_provenance=provenance,
        triangulation_status=str(entry.get("triangulation_status") or "none").strip(),
        reliability_score=float(score) if isinstance(score, (int, float)) else None,
    )


def reject_model_prior_topic(
    topic: str,
    packet: ResearchPacket,
) -> HotTopicCallout:
    """Mark a model-prior-only topic unusable (no packet grounding).

    Used by RED tests and any caller that attempts to inject topics without
    matching wrangled rows.
    """
    needle = topic.strip().lower()
    grounded = False
    for entry in packet.entries:
        title = str(entry.get("title") or "").lower()
        if needle and needle in title:
            grounded = True
            break
    if grounded:
        # Should not be called for grounded topics; still return low-confidence
        # callout if somehow invoked.
        return HotTopicCallout(
            topic=topic.strip(),
            rationale=(
                "Topic appears in packet titles; prefer "
                "`project_trends_from_packet` for full provenance."
            ),
            supporting_citation_ids=(),
            source_refs=(),
            confidence="low",
        )
    return HotTopicCallout(
        topic=topic.strip() or "(empty topic)",
        rationale=(
            "UNUSABLE: model-prior / operator-injected topic with no matching "
            "wrangled research-packet title or source_ref. Hot-topics must be "
            "packet-grounded — not forecasting theater."
        ),
        supporting_citation_ids=(),
        source_refs=(),
        confidence="unusable",
    )


def project_trends_from_packet(
    packet: ResearchPacket,
    *,
    max_trends: int = 5,
    max_hot_topics: int = 3,
    injected_topics: Sequence[str] = (),
) -> ResearchTrendsBrief:
    """Project packet rows into trends + bounded hot-topics.

    ``injected_topics`` without packet grounding are marked ``unusable``
    (Amelia/Murat false-green guard).
    """
    losses: list[str] = list(packet.known_losses)
    if not packet.usable:
        return ResearchTrendsBrief(
            trends=(),
            hot_topics=(),
            known_losses=tuple(losses),
            empty_reason=(
                "no usable research packet rows for trends/hot-topics; "
                "recorded explicitly-empty (topics are not fabricated)"
            ),
        )

    trends: list[ResearchTrendClaim] = []
    for index, entry in enumerate(packet.entries):
        if len(trends) >= max_trends:
            losses.append(f"trends_capped_at_{max_trends}")
            break
        claim = _trend_from_entry(entry)
        if claim is None:
            losses.append(f"trend_skip_missing_provenance:{index}")
            continue
        if claim.confidence == "unusable":
            losses.append(f"trend_unusable:{claim.citation_id}")
            continue
        trends.append(claim)

    # Hot topics: prefer dual_provider / higher reliability among trend rows.
    ranked = sorted(
        trends,
        key=lambda t: (
            1 if t.triangulation_status == "dual_provider" else 0,
            t.reliability_score if t.reliability_score is not None else -1.0,
        ),
        reverse=True,
    )
    hot_topics: list[HotTopicCallout] = []
    for claim in ranked:
        if len(hot_topics) >= max_hot_topics:
            break
        topic = _topic_phrase(claim.title, fallback=claim.citation_id)
        hot_topics.append(
            HotTopicCallout(
                topic=topic,
                rationale=(
                    f"{TRENDS_WRITER_REQUIRED_MARKER} Bounded hot-topic callout "
                    f"grounded in `{claim.citation_id}` "
                    f"(tier={claim.evidence_hierarchy_tier}, "
                    f"triangulation={claim.triangulation_status}, "
                    f"confidence={claim.confidence}). Not a forecast."
                ),
                supporting_citation_ids=(claim.citation_id,),
                source_refs=(claim.source_ref,),
                confidence=claim.confidence,
            )
        )

    for injected in injected_topics:
        hot_topics.append(reject_model_prior_topic(injected, packet))
        losses.append(f"injected_topic_checked:{injected[:40]}")

    if not trends and not any(h.confidence != "unusable" for h in hot_topics):
        return ResearchTrendsBrief(
            trends=(),
            hot_topics=tuple(hot_topics),
            known_losses=tuple(losses),
            empty_reason=(
                "research packet present but no trends-eligible rows; "
                "recorded explicitly-empty"
            ),
        )
    return ResearchTrendsBrief(
        trends=tuple(trends),
        hot_topics=tuple(hot_topics),
        known_losses=tuple(losses),
        empty_reason=None,
    )


def trends_inputs_from_run(
    run_dir: Path,
    *,
    max_trends: int = 5,
    max_hot_topics: int = 3,
    injected_topics: Sequence[str] = (),
) -> ResearchTrendsBrief:
    """W3 intake: resolve trends consumer packet → backmatter brief."""
    packet = resolve_for_trends_projector(run_dir, require_usable=False)
    return project_trends_from_packet(
        packet,
        max_trends=max_trends,
        max_hot_topics=max_hot_topics,
        injected_topics=injected_topics,
    )


_INLINE_HTML_COMMENT_RE = re.compile(r"<!--.*?-->")


def _strip_inline_comments(text: str) -> str:
    """Drop inline ``<!-- ... -->`` spans from rendered client-facing prose.

    The ``TRENDS_WRITER_REQUIRED_MARKER`` is retained on the ``HotTopicCallout``
    ``rationale`` field (the programmatic "a writer must re-voice this" signal that
    tests / live-evidence harnesses assert against), but it must NEVER reach the
    rendered MD / DOCX — ``_render_docx_body`` only skips lines that START with
    ``<!--``, so an INLINE marker leaked verbatim into the client deliverable.
    Strip inline comment spans (and collapse the doubled whitespace they leave)
    at render time so the emitted output is clean while the field stays intact
    (mirrors how the glossary retired ``GLOSSARY-WRITER-REQUIRED`` from its body).
    """
    return re.sub(r"\s{2,}", " ", _INLINE_HTML_COMMENT_RE.sub("", text)).strip()


def render_trends_markdown(brief: ResearchTrendsBrief) -> str:
    """Render Research Trends section body (without the H2 heading)."""
    lines: list[str] = []
    if brief.empty_reason and not brief.usable:
        lines.append(f"*({brief.empty_reason})*")
        # Still surface unusable injected topics for honesty.
        unusable = [h for h in brief.hot_topics if h.confidence == "unusable"]
        if unusable:
            lines.append("")
            lines.append("#### Rejected / unusable topics")
            for topic in unusable:
                lines.append(f"- **{topic.topic}** — {_strip_inline_comments(topic.rationale)}")
        return "\n".join(lines)

    lines.append("#### Research trends")
    lines.append("")
    if not brief.trends:
        lines.append("*(no packet-grounded trend claims recorded)*")
    else:
        for claim in brief.trends:
            peer = (
                "peer-reviewed"
                if claim.peer_reviewed is True
                else "not peer-reviewed"
                if claim.peer_reviewed is False
                else "peer-review unknown"
            )
            score = (
                f", reliability={claim.reliability_score:.2f}"
                if claim.reliability_score is not None
                else ""
            )
            lines.append(f"- {claim.claim_text}")
            lines.append(
                f"  - **Provenance:** `{claim.citation_id}` · "
                f"`{claim.source_ref}` · tier={claim.evidence_hierarchy_tier}, "
                f"{peer}, triangulation={claim.triangulation_status}, "
                f"confidence={claim.confidence}{score}"
            )
            lines.append("")

    lines.append("#### Hot topics")
    lines.append("")
    lines.append(
        "*Bounded callout from wrangled evidence — not trend-forecasting theater.*"
    )
    lines.append("")
    usable_hot = [h for h in brief.hot_topics if h.confidence != "unusable"]
    unusable_hot = [h for h in brief.hot_topics if h.confidence == "unusable"]
    if not usable_hot:
        lines.append("*(no packet-grounded hot topics recorded)*")
    else:
        for topic in usable_hot:
            refs = ", ".join(f"`{r}`" for r in topic.source_refs) or "(none)"
            cites = ", ".join(f"`{c}`" for c in topic.supporting_citation_ids)
            lines.append(
                f"- **{topic.topic}** (confidence={topic.confidence}) — "
                f"{_strip_inline_comments(topic.rationale)} "
                f"Supporting: {cites}; source_refs: {refs}."
            )
    if unusable_hot:
        lines.append("")
        lines.append("#### Rejected / unusable topics")
        for topic in unusable_hot:
            lines.append(f"- **{topic.topic}** — {_strip_inline_comments(topic.rationale)}")
    return "\n".join(lines).rstrip()


__all__ = [
    "TRENDS_WRITER_REQUIRED_MARKER",
    "Confidence",
    "HotTopicCallout",
    "ResearchTrendClaim",
    "ResearchTrendsBrief",
    "project_trends_from_packet",
    "reject_model_prior_topic",
    "render_trends_markdown",
    "trends_inputs_from_run",
]
