"""W2 — project research-packet rows into encyclopedia glossary articles.

Produce-time only (not CollateralSpec). Writers synthesize from wrangled,
tier-labeled rows — never invent scholarship. Default projector builds a
non-vacuous encyclopedia stub from row metadata; fuller SME prose may replace
the body later via an injectable writer.

M3-safe: imports ``research_packet`` (lesson_plan), not ``marcus.orchestrator``.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.marcus.lesson_plan.research_packet import (
    ResearchPacket,
    load_research_packet,
    resolve_for_glossary_writer,
)

# Retained for tooling / grep of unfinished injectables. The default writer no
# longer emits this HTML comment into learner-facing bodies (John done-bar
# 2026-07-10); honesty lives in ``GLOSSARY_CAPABILITY_NOTE`` instead (Winston).
GLOSSARY_WRITER_REQUIRED_MARKER = "<!-- GLOSSARY-WRITER-REQUIRED -->"

GLOSSARY_CAPABILITY_NOTE = (
    "*Capability note: research-informed encyclopedia stub from indexed "
    "title/metadata and tier labels — not a human SME-reviewed article.*"
)

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
    }
)


@dataclass(frozen=True)
class GlossaryArticleBrief:
    """One encyclopedia-style glossary article (not a dictionary gloss)."""

    term: str
    headline: str
    body: str
    citation_id: str
    source_ref: str
    source_id: str
    provider: str
    evidence_hierarchy_tier: str
    peer_reviewed: bool | None
    provider_provenance: tuple[str, ...]
    triangulation_status: str
    reliability_score: float | None = None
    title: str = ""


GlossaryWriter = Callable[[dict[str, Any]], GlossaryArticleBrief]


def _term_from_title(title: str, *, fallback: str) -> str:
    """Derive a glossary term from a paper title (encyclopedia headword)."""
    cleaned = re.sub(r"\s+", " ", (title or "").strip())
    if not cleaned:
        return fallback
    # Prefer a short noun-phrase headword from leading content words.
    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9\-']*", cleaned)
    content = [w for w in words if w.lower() not in _STOPWORDS]
    if not content:
        return cleaned[:80]
    head = " ".join(content[:6])
    if len(head) > 72:
        head = head[:69].rstrip() + "…"
    return head


def default_glossary_writer(entry: dict[str, Any]) -> GlossaryArticleBrief:
    """Deterministic encyclopedia stub from a credibility-labeled packet row.

    Non-vacuous: multi-sentence body grounded in title + tier + triangulation.
    Does **not** invent study findings beyond the indexed title/metadata.
    """
    citation_id = str(entry.get("citation_id") or "").strip()
    source_ref = str(entry.get("source_ref") or "").strip()
    source_id = str(entry.get("source_id") or "").strip()
    provider = str(entry.get("provider") or "").strip()
    title = str(entry.get("title") or "").strip()
    tier = str(entry.get("evidence_hierarchy_tier") or "").strip()
    triangulation = str(entry.get("triangulation_status") or "none").strip()
    provenance_raw = entry.get("provider_provenance")
    provenance: tuple[str, ...]
    if isinstance(provenance_raw, (list, tuple)):
        provenance = tuple(str(p) for p in provenance_raw if str(p).strip())
    else:
        provenance = (provider,) if provider else ()

    peer = entry.get("peer_reviewed")
    peer_phrase = (
        "peer-reviewed"
        if peer is True
        else "not peer-reviewed"
        if peer is False
        else "peer-review status unknown"
    )
    term = _term_from_title(title, fallback=citation_id or source_id or "Untitled construct")
    headline = (
        f"{term}: research-informed encyclopedia entry"
        if title
        else f"{term}: research-informed encyclopedia entry (title absent)"
    )
    score = entry.get("reliability_score")
    score_phrase = (
        f" Composite reliability on the triangulation receipt is {float(score):.2f}."
        if isinstance(score, (int, float))
        else ""
    )
    body = "\n\n".join(
        [
            GLOSSARY_CAPABILITY_NOTE,
            (
                f"**{term}** is treated here as a learner-facing encyclopedia "
                f"construct, not a one-line dictionary gloss. The wrangled "
                f"literature for this run indexes the work "
                f"“{title or '(untitled)'}” as supporting context for this "
                f"construct. No study findings are invented beyond that "
                f"indexed title and the credibility labels on the packet row."
            ),
            (
                f"Evidence standing for this entry is explicitly surfaced: "
                f"hierarchy tier `{tier or 'unknown'}`, {peer_phrase}, "
                f"provider provenance `{','.join(provenance) or provider}`, "
                f"and triangulation status `{triangulation}`.{score_phrase} "
                f"This is research-informed synthesis from tier-labeled rows — "
                f"not a semantic claim↔source audit of course narration."
            ),
            (
                "Readers should treat the cited source as the authority for "
                "methods and findings; this article orients the construct and "
                "preserves provenance for downstream review."
            ),
        ]
    )
    return GlossaryArticleBrief(
        term=term,
        headline=headline,
        body=body,
        citation_id=citation_id,
        source_ref=source_ref,
        source_id=source_id,
        provider=provider,
        evidence_hierarchy_tier=tier or "T8_unknown",
        peer_reviewed=peer if isinstance(peer, bool) else None,
        provider_provenance=provenance,
        triangulation_status=triangulation or "none",
        reliability_score=float(score) if isinstance(score, (int, float)) else None,
        title=title,
    )


def project_glossary_articles(
    packet: ResearchPacket,
    *,
    writer: GlossaryWriter | None = None,
    max_articles: int = 5,
) -> tuple[tuple[GlossaryArticleBrief, ...], str | None, tuple[str, ...]]:
    """Project usable packet rows into glossary articles.

    Returns ``(articles, empty_reason, known_losses)``. Rows missing provenance
    / source_ref are skipped into known_losses (never fabricated).
    """
    write = writer or default_glossary_writer
    losses: list[str] = list(packet.known_losses)
    articles: list[GlossaryArticleBrief] = []

    if not packet.usable:
        reason = (
            "no usable research packet rows for glossary; recorded explicitly-empty "
            "(encyclopedia articles are not fabricated)"
        )
        return (), reason, tuple(losses)

    for index, entry in enumerate(packet.entries):
        if len(articles) >= max_articles:
            losses.append(f"glossary_capped_at_{max_articles}")
            break
        source_ref = str(entry.get("source_ref") or "").strip()
        provenance = entry.get("provider_provenance")
        if not source_ref:
            losses.append(f"glossary_skip_missing_source_ref:{index}")
            continue
        if not isinstance(provenance, list) or not provenance:
            losses.append(f"glossary_skip_missing_provenance:{index}")
            continue
        articles.append(write(entry))

    if not articles:
        reason = (
            "research packet present but no glossary-eligible rows "
            "(missing provenance/source_ref); recorded explicitly-empty"
        )
        return (), reason, tuple(losses)
    return tuple(articles), None, tuple(losses)


def glossary_inputs_from_run(
    run_dir: Path,
    *,
    writer: GlossaryWriter | None = None,
    max_articles: int = 5,
) -> tuple[tuple[GlossaryArticleBrief, ...], str | None, tuple[str, ...]]:
    """W2 intake: resolve glossary consumer packet → encyclopedia articles."""
    packet = resolve_for_glossary_writer(run_dir, require_usable=False)
    return project_glossary_articles(
        packet, writer=writer, max_articles=max_articles
    )


def render_glossary_markdown(
    articles: Sequence[GlossaryArticleBrief],
    *,
    empty_reason: str | None = None,
) -> str:
    """Render the Research Glossary section body (without the H2 heading)."""
    lines: list[str] = []
    if not articles:
        reason = empty_reason or (
            "no research-informed glossary articles recorded for this run; "
            "recorded explicitly-empty"
        )
        lines.append(f"*({reason})*")
        return "\n".join(lines)

    for article in articles:
        lines.append(f"### {article.term}")
        lines.append("")
        lines.append(f"*{article.headline}*")
        lines.append("")
        lines.append(article.body.strip())
        lines.append("")
        peer = (
            "peer-reviewed"
            if article.peer_reviewed is True
            else "not peer-reviewed"
            if article.peer_reviewed is False
            else "peer-review unknown"
        )
        prov = ",".join(article.provider_provenance) or article.provider
        score = (
            f", reliability={article.reliability_score:.2f}"
            if article.reliability_score is not None
            else ""
        )
        doi = (
            f"https://doi.org/{article.source_id}"
            if article.source_id.lower().startswith("10.")
            else f"source_id=`{article.source_id}`"
        )
        lines.append(
            f"**Provenance:** `{article.citation_id}` · source_ref "
            f"`{article.source_ref}` · {doi} · tier="
            f"{article.evidence_hierarchy_tier}, {peer}, provenance={prov}, "
            f"triangulation={article.triangulation_status}{score}"
        )
        lines.append("")
    return "\n".join(lines).rstrip()


__all__ = [
    "GLOSSARY_CAPABILITY_NOTE",
    "GLOSSARY_WRITER_REQUIRED_MARKER",
    "GlossaryArticleBrief",
    "GlossaryWriter",
    "default_glossary_writer",
    "glossary_inputs_from_run",
    "load_research_packet",
    "project_glossary_articles",
    "render_glossary_markdown",
]
