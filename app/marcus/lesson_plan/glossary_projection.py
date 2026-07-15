"""W2/39.1 — term-keyed encyclopedia glossary downstream of the Deep Dive.

Story 39.1 (learner-deliverable path): the glossary is TERM-KEYED — exactly one
entry per bolded Deep Dive term, headword == the bolded term BYTE-EXACT (W3
post-writer invariant), entries composed ONLY from Ask-A pool rows whose
``supports_bold_terms`` contains the term ("association-covered" — token-match,
never claimed semantic, per 37-2b amendment J3). Bold-term authority is
STATUS-DEPENDENT on the 07W.3 contribution (W1/A-2): enriched ⇒
``result.bold_terms``; degraded-with-skeleton ⇒
``result.request.skeleton.bold_terms`` (all entries uncovered-honest with the
degradation reason surfaced); no contribution / no skeleton ⇒ explicitly-empty
with reason ``bold-term authority absent``. Uncovered terms render LEAN (J-1):
one ``###`` heading + one short honest line; the section lead carries one
coverage line; typed ``glossary_term_uncovered:<term>`` losses stay
artifact-side.

LEGACY (pre-39.1) generic-packet path: ``project_glossary_articles`` /
``glossary_inputs_from_run`` / ``default_glossary_writer`` (the
``_term_from_title`` title-mangling headword derivation) are RETIRED from the
learner deliverable — ``_act.py`` no longer calls them. They are retained ONLY
for the frozen W2/W4 evidence scripts and the legacy compose seam; never wire
them back into the deliverable (J-F3 regression pins + the deliverable-bar
negative pins reject mangled headwords).

Produce-time only (not CollateralSpec). Writers synthesize from wrangled,
tier-labeled rows — never invent scholarship.

M3-safe: imports ``research_packet`` (lesson_plan), not ``marcus.orchestrator``.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Sequence
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Literal

from app.marcus.lesson_plan.research_packet import (
    ResearchPacket,
    load_research_packet,
    resolve_for_glossary_writer,
)

# Retained for tooling / grep of unfinished injectables. The default writer no
# longer emits this HTML comment into learner-facing bodies (John done-bar
# 2026-07-10); honesty lives in ``GLOSSARY_CAPABILITY_NOTE`` instead (Winston).
GLOSSARY_WRITER_REQUIRED_MARKER = "<!-- GLOSSARY-WRITER-REQUIRED -->"

# AC-A4 (39.1): the note carries one sentence declaring tier labels are
# upstream machine labels, not this renderer's verification (J-F3 honesty).
GLOSSARY_CAPABILITY_NOTE = (
    "*Capability note: research-informed encyclopedia stub from indexed "
    "title/metadata and tier labels — not a human SME-reviewed article. "
    "Evidence-hierarchy tier labels are upstream machine labels carried "
    "verbatim; this renderer does not verify them.*"
)

# AC-A3 / matrix row d (39.1): the explicit reason literal when no bold-term
# authority exists (no 07W.3 contribution or no skeleton).
BOLD_TERM_AUTHORITY_ABSENT_REASON = "bold-term authority absent"

# Matrix row c (39.1): typed per-term loss prefix (artifact-side; learner
# surface stays lean per J-1).
GLOSSARY_TERM_UNCOVERED_LOSS_PREFIX = "glossary_term_uncovered"

# Row d′ truthfulness (39.1 remediation P2): a DISTINCT typed loss for a term
# that IS association-covered by a present pool row but renders uncovered
# because degradation forced it (the enrichment never composed).
GLOSSARY_TERM_UNCOVERED_DEGRADED_LOSS_PREFIX = "glossary_term_uncovered_degraded"

# P11 (39.1 remediation): a pool row whose ``supports_bold_terms`` intersects
# NO bolded term is recorded visibly, never vanished.
GLOSSARY_ROW_UNASSOCIATED_LOSS_PREFIX = "glossary_row_unassociated"

# P12 (39.1 remediation): the same citation_id carrying a DIFFERENT
# (source_id, source_ref) across rendered articles is a visible conflict.
GLOSSARY_REFERENCE_CONFLICT_LOSS_PREFIX = "glossary_reference_conflict"

# J-1 (39.1): the EXACT one-line uncovered-entry render (genuinely uncovered:
# no pool row associates with the term).
GLOSSARY_UNCOVERED_ENTRY_LINE = (
    "Key term from the Deep Dive. No research row in this run's pool covers "
    "it; no definition is invented."
)

# P2 (39.1 remediation): the state-accurate one-line render for a term that a
# PRESENT pool row association-covers but degradation forced uncovered.
GLOSSARY_UNCOVERED_DEGRADED_ENTRY_LINE = (
    "Enrichment was degraded this run; a research row associates with this "
    "term but was not composed."
)

# R9-consistent DOI-shape guard (mirrors deep_dive_enrichment._DOI_SHAPE_RE —
# duplicated locally to avoid a module-level import cycle): a doi.org link is
# emitted ONLY for a DOI-shaped source_id; anything else renders as a
# source_id-labeled entry (never a fabricated link).
_DOI_SHAPE_RE = re.compile(r"^10\.\d{4,9}/\S+$")

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
    # 39.1: the pool row's own content hash (G2 manifest join agrees with the
    # deep-dive used-rows join — no manifest hash-disagreement warnings).
    source_hash: str = ""


GlossaryWriter = Callable[[dict[str, Any]], GlossaryArticleBrief]

# 39.1 term-keyed writer seam (injectable; deterministic default today, a
# possible SME-prose writer later). Signature: (bolded term, pool-row payload)
# -> article brief. The projection VALIDATES/OVERRIDES the headword AFTER the
# writer returns (W3) — the invariant is enforced at the projection layer,
# never trusted to the writer.
GlossaryTermWriter = Callable[[str, dict[str, Any]], GlossaryArticleBrief]


def _term_from_title(title: str, *, fallback: str) -> str:
    """LEGACY headword mangle — RETIRED from the learner deliverable (39.1 J-F3).

    Retained only for the frozen W2/W4 evidence scripts via
    ``default_glossary_writer``; the term-keyed 39.1 path never derives a
    headword from a paper title.
    """
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
    """LEGACY writer (title-derived headword) — retired from the deliverable.

    Deterministic encyclopedia stub from a credibility-labeled packet row.
    Non-vacuous: multi-sentence body grounded in title + tier + triangulation.
    Does **not** invent study findings beyond the indexed title/metadata.
    Retained only for the frozen W2/W4 evidence scripts (39.1 J-F3: the
    learner deliverable is term-keyed and never mangles a title into a
    headword).
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
    """LEGACY generic-packet projection — retired from the deliverable (39.1).

    Returns ``(articles, empty_reason, known_losses)``. Rows missing provenance
    / source_ref are skipped into known_losses (never fabricated). Retained
    only for the frozen W2/W4 evidence scripts and legacy compose callers.
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
    """LEGACY W2 intake — replaced at the ``_act.py`` call site by the 39.1
    term-keyed :func:`glossary_projection_from_contribution`. Retained only for
    the frozen W2/W4 evidence scripts; never wire back into the deliverable."""
    packet = resolve_for_glossary_writer(run_dir, require_usable=False)
    return project_glossary_articles(
        packet, writer=writer, max_articles=max_articles
    )


# ---------------------------------------------------------------------------
# 39.1 — term-keyed projection (the learner-deliverable path)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GlossaryTermEntry:
    """One encyclopedia entry keyed to a bolded Deep Dive term.

    ``articles`` (covered): one rendered article brief per supporting Ask-A
    pool row, ordered by ``citation_id`` (matrix row b, byte-deterministic).
    Uncovered: ``articles == ()`` and the render is the J-1 lean shape —
    ``degraded_association=True`` (P2) when a PRESENT pool row
    association-covers the term but degradation forced uncovered, so the one
    lean line is state-accurate (never the "no research row covers it" claim).
    """

    term: str
    covered: bool
    articles: tuple[GlossaryArticleBrief, ...]
    degraded_association: bool = False


@dataclass(frozen=True)
class GlossaryProjection:
    """The 39.1 term-keyed glossary projection (structured artifact side).

    ``known_losses`` carries the typed ``glossary_term_uncovered:<term>``
    losses (artifact-side; the learner surface stays lean per J-1) plus any
    row-skip losses (row k idiom).
    """

    authority: Literal["enriched", "degraded_skeleton", "absent"]
    entries: tuple[GlossaryTermEntry, ...]
    covered_count: int
    term_count: int
    empty_reason: str | None
    degradation_reason: str | None
    known_losses: tuple[str, ...]
    # A5 re-point witness: the Ask-A packet digest the embedded pool rows are
    # digest-bound to (from the enrichment request; None when authority absent).
    pool_packet_digest: str | None = None

    @property
    def covered_articles(self) -> tuple[GlossaryArticleBrief, ...]:
        return tuple(a for entry in self.entries for a in entry.articles)


def _row_payload(row: Any) -> dict[str, Any]:
    """Normalize a pool row (AskAKnowledgeEntryV1 model or mapping) to a dict."""
    if hasattr(row, "model_dump"):
        return dict(row.model_dump(mode="json"))
    return dict(row)


def default_term_glossary_writer(term: str, entry: dict[str, Any]) -> GlossaryArticleBrief:
    """Deterministic 39.1 term-keyed article from an Ask-A pool row.

    The headword IS the bolded term (never derived from the paper title —
    J-F3); the indexed work's title appears INSIDE the entry as cited support.
    Association language is "association-covered" (token-match, never claimed
    semantic — 37-2b amendment J3). Tier / provenance / triangulation render
    verbatim from the row (AC-A4) — never re-derived, upgraded, or suppressed.
    """
    citation_id = str(entry.get("citation_id") or "").strip()
    source_ref = str(entry.get("source_ref") or "").strip()
    source_id = str(entry.get("source_id") or "").strip()
    provider = str(entry.get("provider") or "").strip()
    title = str(entry.get("title") or "").strip()
    tier = str(entry.get("evidence_hierarchy_tier") or "").strip()
    triangulation = str(entry.get("triangulation_status") or "none").strip()
    provenance_raw = entry.get("provider_provenance")
    if isinstance(provenance_raw, (list, tuple)):
        provenance: tuple[str, ...] = tuple(
            str(p) for p in provenance_raw if str(p).strip()
        )
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
    score = entry.get("reliability_score")
    score_phrase = (
        f" Composite reliability on the triangulation receipt is {float(score):.2f}."
        if isinstance(score, (int, float))
        else ""
    )
    body = "\n\n".join(
        [
            (
                f"**{term}** is a key term bolded in this workbook's Deep "
                f"Dive. The indexed work “{title or '(untitled)'}” is cited "
                f"here as association-covered support for this term — a "
                f"token-match association on the retrieved evidence, never a "
                f"semantic claim. The work's title is cited support inside "
                f"this entry, never the headword. No study findings are "
                f"invented beyond the indexed title and the credibility "
                f"labels on the pool row."
            ),
            (
                f"Evidence standing for this entry is explicitly surfaced: "
                f"hierarchy tier `{tier or 'unknown'}`, {peer_phrase}, "
                f"provider provenance `{','.join(provenance) or provider}`, "
                f"and triangulation status `{triangulation}`.{score_phrase}"
            ),
        ]
    )
    return GlossaryArticleBrief(
        term=term,
        headline=f"{term}: research-informed encyclopedia entry",
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
        source_hash=str(entry.get("source_hash") or ""),
    )


def project_glossary_entries_for_terms(
    bold_terms: Sequence[str],
    pool_rows: Sequence[Any],
    *,
    writer: GlossaryTermWriter | None = None,
    force_uncovered_reason: str | None = None,
) -> tuple[tuple[GlossaryTermEntry, ...], tuple[str, ...]]:
    """Term-keyed projection: exactly ONE entry per bolded term (AC-A1).

    ``pool_rows`` are Ask-A pool rows (models or mappings) — prefer the
    digest-verified embedded ``result.request.pool_rows`` join (A-3). Rows
    missing ``source_ref``/``provider_provenance`` are skipped into
    known_losses (row k — existing idiom); a term whose only support was
    skipped degrades to uncovered-honest. ``force_uncovered_reason`` (rows
    d′/e) renders EVERY term uncovered-honest regardless of coverage.

    W3 post-writer invariant: the returned entry's headword equals the bolded
    term BYTE-EXACT regardless of writer output — enforced HERE, after the
    writer returns.

    P13 (public-boundary defense): a term carrying a newline, a leading ``#``,
    edge whitespace, any ``*``, or an empty string is REJECTED fail-loud —
    such a headword would corrupt the MD/DOCX render (a ``### <term>`` heading
    or a ``**<term>**`` bold span). Production terms arrive via
    ``BoldTermMarker``; this guard defends the public seam against everything
    else.
    """
    for term in bold_terms:
        if (
            not term
            or term != term.strip()
            or "\n" in term
            or "\r" in term
            or term.startswith("#")
            or "*" in term
        ):
            raise ValueError(
                f"glossary bold term unsafe for MD/DOCX render: {term!r} "
                "(empty, edge whitespace, newline, leading '#', or '*' are "
                "rejected fail-loud at the projection boundary)"
            )
    write = writer or default_term_glossary_writer
    losses: list[str] = []
    rows: list[dict[str, Any]] = []
    for index, raw in enumerate(pool_rows):
        payload = _row_payload(raw)
        if not str(payload.get("source_ref") or "").strip():
            losses.append(f"glossary_skip_missing_source_ref:{index}")
            continue
        provenance = payload.get("provider_provenance")
        if not isinstance(provenance, (list, tuple)) or not provenance:
            losses.append(f"glossary_skip_missing_provenance:{index}")
            continue
        rows.append(payload)

    # P11: a pool row associating with NO bolded term is visibly recorded.
    term_set = set(bold_terms)
    for payload in rows:
        supports = tuple(payload.get("supports_bold_terms") or ())
        if not term_set.intersection(supports):
            citation_id = str(payload.get("citation_id") or "")
            losses.append(
                f"{GLOSSARY_ROW_UNASSOCIATED_LOSS_PREFIX}:{citation_id}"
            )

    entries: list[GlossaryTermEntry] = []
    for term in bold_terms:
        supporting = sorted(
            (
                payload
                for payload in rows
                if term in tuple(payload.get("supports_bold_terms") or ())
            ),
            key=lambda payload: str(payload.get("citation_id") or ""),
        )
        if force_uncovered_reason is not None:
            # P2 (row d′ truthfulness): with a PRESENT pool, a term that a
            # pool row association-covers gets the state-accurate degraded
            # line + the DISTINCT typed loss; a genuinely-uncovered term
            # keeps the original line + loss. One lean line either way (J-1).
            if supporting:
                losses.append(
                    f"{GLOSSARY_TERM_UNCOVERED_DEGRADED_LOSS_PREFIX}:{term}"
                )
                entries.append(
                    GlossaryTermEntry(
                        term=term,
                        covered=False,
                        articles=(),
                        degraded_association=True,
                    )
                )
            else:
                losses.append(f"{GLOSSARY_TERM_UNCOVERED_LOSS_PREFIX}:{term}")
                entries.append(
                    GlossaryTermEntry(term=term, covered=False, articles=())
                )
            continue
        if not supporting:
            losses.append(f"{GLOSSARY_TERM_UNCOVERED_LOSS_PREFIX}:{term}")
            entries.append(GlossaryTermEntry(term=term, covered=False, articles=()))
            continue
        articles: list[GlossaryArticleBrief] = []
        for payload in supporting:
            brief = write(term, dict(payload))
            if brief.term != term:
                # W3: headword == bolded term byte-exact, regardless of what
                # ANY writer returned (mutant-writer pinned).
                brief = replace(brief, term=term)
            articles.append(brief)
        entries.append(
            GlossaryTermEntry(term=term, covered=True, articles=tuple(articles))
        )

    # P12: the same citation_id carrying different (source_id, source_ref)
    # across rendered articles is a visible conflict — the reference emission
    # keeps the FIRST article deterministically (entry order is the bold-term
    # order; per-entry articles are citation_id-ordered), and the conflict is
    # recorded once per citation_id, never silently collapsed.
    seen_identity: dict[str, tuple[str, str]] = {}
    conflicted: set[str] = set()
    for entry in entries:
        for article in entry.articles:
            identity = (article.source_id, article.source_ref)
            prior = seen_identity.setdefault(article.citation_id, identity)
            if prior != identity and article.citation_id not in conflicted:
                conflicted.add(article.citation_id)
                losses.append(
                    f"{GLOSSARY_REFERENCE_CONFLICT_LOSS_PREFIX}:{article.citation_id}"
                )
    return tuple(entries), tuple(losses)


def glossary_projection_from_contribution(
    contribution: Any,
    *,
    writer: GlossaryTermWriter | None = None,
) -> GlossaryProjection:
    """AC-A3 (W1/A-2): status-dependent bold-term authority off the 07W.3 read.

    ``contribution`` is the ONE disk-read ``WorkbookReviewContributionV1``
    (or ``None``) — duck-typed so this module never imports the enrichment
    module at load time. Authority selection:

    - enriched          ⇒ ``result.bold_terms``
    - non-enriched with a request skeleton (degraded / unavailable) ⇒
      ``result.request.skeleton.bold_terms``; ALL entries uncovered-honest
      with the degradation reason surfaced (matrix row d′)
    - no contribution / no enrichment result ⇒ explicitly-empty with reason
      ``bold-term authority absent`` (matrix row d)

    Pool rows join from the digest-verified EMBEDDED ``result.request.pool_rows``
    (A-3 — one authority, no re-resolution drift); the Ask-A packet digest is
    witnessed via ``pool_packet_digest`` (A5 re-point). No research dispatch of
    any kind happens here.
    """
    result = (
        getattr(contribution, "deep_dive_enrichment", None)
        if contribution is not None
        else None
    )
    if result is None:
        if contribution is None:
            detail = (
                "no activated workbook-review contribution exists for this run"
            )
        else:
            losses = tuple(getattr(contribution, "known_losses", ()) or ())
            detail = (
                f"the workbook-review contribution carries no enrichment "
                f"result ({losses[0] if losses else 'loss unrecorded'})"
            )
        return GlossaryProjection(
            authority="absent",
            entries=(),
            covered_count=0,
            term_count=0,
            empty_reason=(
                f"{BOLD_TERM_AUTHORITY_ABSENT_REASON} — {detail}; no glossary "
                "entries are fabricated"
            ),
            degradation_reason=None,
            known_losses=("glossary_bold_term_authority_absent",),
            pool_packet_digest=None,
        )

    # P1 (malformed-contribution honesty): a result that is PRESENT but
    # carries no request (or, non-enriched, no request skeleton) can name no
    # bold-term authority — project typed authority-absent with an accurate
    # reason, never an AttributeError.
    request = getattr(result, "request", None)
    status = getattr(result, "status", None)
    skeleton = getattr(request, "skeleton", None) if request is not None else None
    if request is None or (status != "enriched" and skeleton is None):
        return GlossaryProjection(
            authority="absent",
            entries=(),
            covered_count=0,
            term_count=0,
            empty_reason=(
                f"{BOLD_TERM_AUTHORITY_ABSENT_REASON} — enrichment result "
                "malformed (result present but request/skeleton missing); "
                "no glossary entries are fabricated"
            ),
            degradation_reason=None,
            known_losses=(
                "glossary_bold_term_authority_absent",
                "glossary_enrichment_result_malformed",
            ),
            pool_packet_digest=None,
        )
    if status == "enriched":
        authority: Literal["enriched", "degraded_skeleton"] = "enriched"
        terms = tuple(marker.term for marker in result.bold_terms)
        degradation: str | None = None
    else:
        authority = "degraded_skeleton"
        terms = tuple(marker.term for marker in skeleton.bold_terms)
        result_losses = tuple(result.known_losses)
        loss = result_losses[0] if result_losses else "deep_dive_enrichment_unknown_loss"
        # P10: pool honesty rides the ONE degradation reason (the separate
        # "pool unusable" force-branch was unreachable — degradation always
        # shadowed it); pool_status surfaces here, and per-term state accuracy
        # (degraded-association vs genuinely-uncovered) is P2's job inside
        # project_glossary_entries_for_terms.
        degradation = (
            f"deep-dive enrichment did not author on this run ({loss}; "
            f"pool_status={request.pool_status}); bold-term authority falls "
            "back to the authored skeleton and every entry renders "
            "uncovered-honest"
        )
    pool_rows = tuple(request.pool_rows)
    entries, losses = project_glossary_entries_for_terms(
        terms, pool_rows, writer=writer, force_uncovered_reason=degradation
    )
    covered = sum(1 for entry in entries if entry.covered)
    return GlossaryProjection(
        authority=authority,
        entries=entries,
        covered_count=covered,
        term_count=len(entries),
        empty_reason=None,
        degradation_reason=degradation,
        known_losses=losses,
        pool_packet_digest=str(request.pool_packet_digest),
    )


def _article_doi_fragment(article: GlossaryArticleBrief) -> str:
    """R9-consistent link fragment: doi.org ONLY for a DOI-shaped source_id."""
    if _DOI_SHAPE_RE.fullmatch(article.source_id):
        return f"https://doi.org/{article.source_id}"
    return f"source_id=`{article.source_id}`"


def _article_provenance_line(article: GlossaryArticleBrief) -> str:
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
    return (
        f"**Provenance:** `{article.citation_id}` · source_ref "
        f"`{article.source_ref}` · {_article_doi_fragment(article)} · tier="
        f"{article.evidence_hierarchy_tier}, {peer}, provenance={prov}, "
        f"triangulation={article.triangulation_status}{score}"
    )


def render_glossary_projection_markdown(projection: GlossaryProjection) -> str:
    """Render the 39.1 term-keyed section body (without the H2 heading).

    Section lead: ONE coverage line (J-1) + the surfaced degradation/pool
    reason when present. Covered entries carry the capability note
    (renderer-enforced — a writer cannot drop it), per-row body + verbatim
    provenance line ordered by citation_id. Uncovered entries are LEAN: the
    ``###`` heading + exactly ONE short line — no citation, no tier, no
    capability note (J-1); the line is the P2 degraded-association variant
    when a present pool row associates with the term but degradation forced
    uncovered.

    P1 (zero-term honesty): a PRESENT authority (enriched / degraded-skeleton)
    with ZERO bolded terms renders the honest coverage line
    ("Research coverage this run: 0 of 0 terms.") — never the
    authority-absent literal.
    """
    if projection.authority == "absent":
        reason = projection.empty_reason or (
            f"{BOLD_TERM_AUTHORITY_ABSENT_REASON}; recorded explicitly-empty"
        )
        return f"*({reason})*"
    lines: list[str] = [
        f"Research coverage this run: {projection.covered_count} of "
        f"{projection.term_count} terms."
    ]
    if projection.degradation_reason:
        lines.append("")
        lines.append(f"> _Glossary honesty: {projection.degradation_reason}_")
    for entry in projection.entries:
        lines.append("")
        lines.append(f"### {entry.term}")
        lines.append("")
        if not entry.covered:
            lines.append(
                GLOSSARY_UNCOVERED_DEGRADED_ENTRY_LINE
                if entry.degraded_association
                else GLOSSARY_UNCOVERED_ENTRY_LINE
            )
            continue
        lines.append(GLOSSARY_CAPABILITY_NOTE)
        for article in entry.articles:
            lines.append("")
            lines.append(article.body.strip())
            lines.append("")
            lines.append(_article_provenance_line(article))
    return "\n".join(lines).rstrip()


def glossary_reference_lines(
    projection: GlossaryProjection | None,
    *,
    exclude_citation_ids: Sequence[str] = (),
) -> tuple[str, ...]:
    """AC-A9 (W2/M1): additive references-emission for glossary-covered rows.

    Resolvability floor ONLY (never the 37.5 References assemble/dedupe
    redesign): each glossary-covered row renders one reference line in the
    same idiom as ``render_deep_dive_reference_lines`` (R9-consistent
    DOI-shape guard), deduped by ``citation_id`` against
    ``exclude_citation_ids`` (the enrichment-emitted lines) AND within the
    glossary itself — a citation cited by both the deep dive and a glossary
    entry appears ONCE. Ordered by citation_id (deterministic). P12: when the
    same citation_id carries conflicting (source_id, source_ref) identities,
    the FIRST article in deterministic entry order wins here and the conflict
    is recorded as ``glossary_reference_conflict:<citation_id>`` in the
    projection's known_losses (visible, never silently collapsed).
    """
    if projection is None:
        return ()
    seen = set(exclude_citation_ids)
    articles: list[GlossaryArticleBrief] = []
    for entry in projection.entries:
        for article in entry.articles:
            if article.citation_id in seen:
                continue
            seen.add(article.citation_id)
            articles.append(article)
    articles.sort(key=lambda a: a.citation_id)
    lines: list[str] = []
    for article in articles:
        peer = (
            "peer-reviewed"
            if article.peer_reviewed is True
            else "not peer-reviewed"
            if article.peer_reviewed is False
            else "peer-review unknown"
        )
        prov = ",".join(article.provider_provenance) or article.provider
        label = article.title.strip() or article.source_ref
        link = (
            f" https://doi.org/{article.source_id}"
            if _DOI_SHAPE_RE.fullmatch(article.source_id)
            else ""
        )
        lines.append(
            f"- {label}.{link} "
            f"(provider: {article.provider}, source_ref: `{article.source_ref}`, "
            f"citation_id: `{article.citation_id}`, "
            f"tier={article.evidence_hierarchy_tier}, "
            f"{peer}, provenance={prov}, "
            f"triangulation={article.triangulation_status})"
        )
    return tuple(lines)


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
    "BOLD_TERM_AUTHORITY_ABSENT_REASON",
    "GLOSSARY_CAPABILITY_NOTE",
    "GLOSSARY_REFERENCE_CONFLICT_LOSS_PREFIX",
    "GLOSSARY_ROW_UNASSOCIATED_LOSS_PREFIX",
    "GLOSSARY_TERM_UNCOVERED_DEGRADED_LOSS_PREFIX",
    "GLOSSARY_TERM_UNCOVERED_LOSS_PREFIX",
    "GLOSSARY_UNCOVERED_DEGRADED_ENTRY_LINE",
    "GLOSSARY_UNCOVERED_ENTRY_LINE",
    "GLOSSARY_WRITER_REQUIRED_MARKER",
    "GlossaryArticleBrief",
    "GlossaryProjection",
    "GlossaryTermEntry",
    "GlossaryTermWriter",
    "GlossaryWriter",
    "default_glossary_writer",
    "default_term_glossary_writer",
    "glossary_inputs_from_run",
    "glossary_projection_from_contribution",
    "glossary_reference_lines",
    "load_research_packet",
    "project_glossary_articles",
    "project_glossary_entries_for_terms",
    "render_glossary_markdown",
    "render_glossary_projection_markdown",
]
