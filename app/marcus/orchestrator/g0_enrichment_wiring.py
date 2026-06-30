"""G0-enrichment runner-wired orchestration hook (Story G0-S2).

The Marcus-SPOC G0 pre-pass that (1) segments every enumerated source FILE into N
typed COMPONENTS (the closed 10-type taxonomy + ``other:<label>`` escape hatch),
each with a document-hierarchy locator + verbatim excerpt, and (2) extracts
candidate Learning Objectives at ``status=provisional`` with resolvable
``SourceRef`` provenance — both OFF the deterministic critical path (an LLM
pre-pass, result frozen + cached keyed to a CORPUS FINGERPRINT for replay
determinism). Replaces the prior file-level typing (one whole file → one type):
a 150KB outline that is all 'other' under file-typing becomes 188 typed
components under intra-document extraction (charter P1). The frozen result feeds
operator confirm-gate #1 (``G0E``).

ATTACH MECHANIC
---------------
Unlike research-wiring (option A, keyed off an existing node), this brick adds a
``g0-enrichment`` orchestration node + a ``g0-enrichment-gate`` (``G0E``) pause
gate to the manifest (mirrors the 07D.5 / 07W bricks — topology refinement within
the v4.2 lineage; pack/HUD-invisible). The runner invokes THIS hook at the
``g0-enrichment`` node id (the ``research_wiring`` / ``package_builders`` keyed
orchestration precedent), then pauses at the ``G0E`` gate node that follows.

TWO-WALK PARITY (memory ``project_production_runner_two_walks``)
---------------------------------------------------------------
The node sits BEFORE node ``01``, so on the trial path it fires on the START
walk; but the side-effect is present in BOTH walk bodies (start +
continuation/recover) so a resume/recover that re-enters the node before the
``G0E`` gate also produces the artifact. Wiring one walk only is the silent-no-op
bug.

OFFLINE GUARD
-------------
Live typing/LO extraction calls ``make_chat_model("marcus")`` (the
``pre_gate_marcus`` seam). Offline/test runs bypass the live LLM via the existing
``_has_live_openai()``-style guard (a ``dispatch_live`` flag threaded by the
runner) and use a deterministic, corpus-derived recorded pre-pass result. The
story's live-segment proof (AC-S2-8) exercises the REAL LLM on real corpus.
"""

from __future__ import annotations

import json
import logging
import os
import re
import sys
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from pydantic import ValidationError

from app.composers.section_02a.composer import _walk_corpus_files
from app.marcus.lesson_plan.coverage_annotation import (
    CoverageAnnotation,
    build_coverage_annotations,
)
from app.marcus.lesson_plan.g0_enrichment import (
    ENRICHMENT_CARD_BASENAME,
    CitationResolution,
    Dissent,
    EnumerationProvenance,
    G0EnrichmentResult,
    IndependentParse,
    ReconcileView,
    TraversalRoot,
    assert_run_dissent_invariant,
    corpus_fingerprint,
    file_content_hash,
)
from app.marcus.lesson_plan.learning_objective import LearningObjective, SourceRef, advance_lo
from app.marcus.lesson_plan.pedagogy_annotation import (
    PEDAGOGY_TRANSFORM_VERSION,
    PedagogyAnnotation,
    assert_pedagogy_referential_invariant,
    assert_pedagogy_teachable_consistency,
    build_pedagogy_annotations,
)
from app.marcus.lesson_plan.source_type import TypedComponent
from app.marcus.orchestrator.coverage_gate_wiring import coverage_pass_active
from app.models.runtime.production_envelope import ProductionEnvelope, SpecialistContribution

logger = logging.getLogger(__name__)

# Runner-wired at this manifest node id (mirrors RESEARCH_WIRING_NODE_ID).
G0_ENRICHMENT_NODE_ID = "g0-enrichment"
G0_ENRICHMENT_NODE_IDS: frozenset[str] = frozenset({G0_ENRICHMENT_NODE_ID})
G0_ENRICHMENT_GATE_CODE = "G0E"

# Dedicated contribution identity so a consumer expecting persona output never
# receives wiring output (mirrors RESEARCH_WIRING_SPECIALIST_ID). Canonicalizes
# to "g0_enrichment" (registered in CANONICAL_SPECIALIST_IDS).
G0_ENRICHMENT_SPECIALIST_ID = "g0_enrichment"
G0_ENRICHMENT_MODEL_MARKER = "deterministic-g0-enrichment-offline"
G0_ENRICHMENT_LIVE_MODEL_ID = "marcus"

# Live-extraction output budget + per-request hardening (root-cause fix for the
# 2026-06-29 gpt-5 truncation crash at G0E: the keystone component-extraction
# response was a well-formed JSON PREFIX truncated mid-structure because no
# generous output ceiling was bound — reasoning models spend budget on hidden
# reasoning first, then truncate the visible JSON). The DEFAULT (None-fallback)
# chat-model factory binds these; an injected harness factory may bind its own.
G0_EXTRACTION_MAX_COMPLETION_TOKENS = 32000
G0_EXTRACTION_REQUEST_TIMEOUT_S = 180.0

# Thin contract key (the frozen enrichment result on the contribution output).
ENRICHMENT_RESULT_KEY = "g0_enrichment_result"

# Feature flag (default OFF) so deck-default / existing pipeline behavior stays
# byte-identical (AC-S2-7): with the flag UNSET, the g0-enrichment node is a no-op
# pass and the G0E gate is traversed (no pause) — every existing trial flow that
# pauses first at G1 is unchanged. The G0-S2 live-segment proof (AC-S2-8) and the
# brick's own integration tests flip it ON to wake the node + the confirm gate.
# Mirrors the woken-via-membership precedent (07B-gate/11-gate) but as a runtime
# toggle. Making G0E the standard front-door gate by default is a follow-on once
# the existing integration suite is migrated to step through G0E first.
G0_ENRICHMENT_ACTIVE_ENV = "MARCUS_G0_ENRICHMENT_ACTIVE"


def g0_enrichment_active() -> bool:
    """Return True iff the G0-enrichment brick is woken (env toggle; default OFF)."""
    return os.environ.get(G0_ENRICHMENT_ACTIVE_ENV, "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


# Operator-gated LIVE-LLM toggle (default OFF), distinct from g0_enrichment_active.
# Mirrors research_wiring's MARCUS_RESEARCH_DISPATCH_LIVE: a woken brick uses the
# DETERMINISTIC recorded pre-pass unless this is explicitly flipped ON (and a real
# OpenAI key is present — the runner AND-gates _has_live_openai()), so a fake-key
# test never triggers a live model call. The AC-S2-8 live-segment proof sets this.
G0_DISPATCH_LIVE_ENV = "MARCUS_G0_DISPATCH_LIVE"


def g0_dispatch_live() -> bool:
    """Return True iff the operator-gated live G0 pre-pass toggle is enabled."""
    return os.environ.get(G0_DISPATCH_LIVE_ENV, "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


# Single-sourced (Winston A2) from the lesson_plan model module — the SAME
# basename ``workbook_enrichment.ENRICHMENT_CARD_BASENAME`` resolves to. The
# orchestrator-local name is kept as an alias so existing references are unchanged.
_DECISION_ARTIFACT_BASENAME = ENRICHMENT_CARD_BASENAME
_CACHE_DIRNAME = "g0-enrichment-cache"

# DD2 — the Texas-side pass-0 package (citation_resolver / universal_md /
# universal_markdown_preamble) lives under the texas scripts dir, imported via
# sys.path injection. The dependency arrow is app/marcus -> skills/bmad-agent-texas
# ONLY (mirrors research_wiring's _import_retrieval / _TEXAS_SCRIPTS_DIR pattern).
_TEXAS_SCRIPTS_DIR = (
    Path(__file__).resolve().parents[3] / "skills" / "bmad-agent-texas" / "scripts"
)


def _import_pass0_resolver() -> Callable[..., list[dict[str, Any]]]:
    """Late-import the Texas pass-0 ``resolve_citations`` (DD1/DD2 seam).

    Late import keeps module-load cheap and avoids a hard dependency on the Texas
    scripts dir being on ``sys.path`` at import time (mirrors research_wiring).
    """
    if str(_TEXAS_SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(_TEXAS_SCRIPTS_DIR))
    from pass0.citation_resolver import resolve_citations  # noqa: PLC0415

    return resolve_citations


def _resolve_citation_resolutions(
    typed: list[TypedComponent],
    source_by_id: dict[str, str],
    *,
    dispatch_live: bool,
    resolve_dispatch: Callable[[Any], Any] | None,
) -> tuple[CitationResolution, ...]:
    """DD3 attach: resolve citation-bearing components → CitationResolution rows.

    Runs ONLY when a real dispatch is available: ``dispatch_live`` (live scite via
    the default in-process Texas dispatcher) OR an explicitly injected
    ``resolve_dispatch`` (the offline-test seam). Otherwise returns ``()`` so the
    offline deterministic path stays network-free and byte-stable.

    The canonical markdown normalizer (``_normalize_for_groundedness``) is INJECTED
    into the Texas resolver (DD6 reuse without a back-arrow import). The resolver
    returns plain dicts; we map them into the ``CitationResolution`` model here
    (the app/marcus side owns the model — DD2 one-way arrow).
    """
    if not dispatch_live and resolve_dispatch is None:
        return ()
    resolve_citations = _import_pass0_resolver()
    raw = resolve_citations(
        typed,
        source_by_id,
        dispatch=resolve_dispatch,  # None -> resolver uses its live default
        normalize_fn=_normalize_for_groundedness,
    )
    return tuple(CitationResolution.model_validate(row) for row in raw)


def _build_pedagogy_frontmatter(
    typed: list[TypedComponent],
    citation_resolutions: tuple[CitationResolution, ...],
    los: list[LearningObjective],
) -> list[dict[str, Any]]:
    """Project typed components into the universal-md FRONT-MATTER P3 consumes.

    P3 reads the DD5 universal-md front matter (``component_id`` / ``type`` /
    ``doc_ordinal`` / ``resolution_status`` / ``locator`` / ``provisional_los``).
    The front-matter ``resolution_status`` is AUTHORITATIVE for the teachable
    derivation (M8 — front matter wins over ``citation_resolutions``):

      1. a ``flagged_ungrounded`` component is ``ungrounded`` (A4 hard rule);
      2. else a citation verdict for that component (if any) applies;
      3. else ``resolved``.

    ``doc_ordinal`` is the DOCUMENT-total position (1-based enumeration order;
    components arrive grouped-by-file in enumeration order). ``provisional_los``
    is the per-component LO id list (LOs whose provenance points at the parent
    file).
    """
    citation_status_by_id = {c.component_id: c.resolution_status for c in citation_resolutions}
    los_by_parent: dict[str, list[str]] = {}
    for lo in los:
        for ref in lo.source_refs:
            bucket = los_by_parent.setdefault(ref.source_id, [])
            if lo.objective_id not in bucket:
                bucket.append(lo.objective_id)

    records: list[dict[str, Any]] = []
    for ordinal, comp in enumerate(typed, start=1):
        if comp.flagged_ungrounded:
            status = "ungrounded"
        else:
            status = citation_status_by_id.get(comp.component_id, "resolved")
        records.append(
            {
                "component_id": comp.component_id,
                "type": comp.source_type,
                "doc_ordinal": ordinal,
                "resolution_status": status,
                "locator": comp.locator,
                "provisional_los": list(los_by_parent.get(comp.parent_source_id, [])),
            }
        )
    return records


def _attach_pedagogy_annotations(
    typed: list[TypedComponent],
    source_by_id: dict[str, str],
    citation_resolutions: tuple[CitationResolution, ...],
    los: list[LearningObjective],
    *,
    dispatch_live: bool,
    chat_model_factory: Any | None = None,
) -> tuple[PedagogyAnnotation, ...]:
    """P3 attach: build per-component pedagogy annotations (thin delegation).

    Projects the wiring-available data into the universal-md front matter P3
    reads, then delegates ALL annotation logic to
    ``pedagogy_annotation.build_pedagogy_annotations`` (W7/W11 — no business logic
    in the wiring). Gated by ``dispatch_live`` exactly like the citation resolver:
    offline → the deterministic pass; live → the pre_gate_marcus seam. The
    teachable-consistency guard runs on the assembled set before it rides the
    result.
    """
    del source_by_id  # P3 reads resolution_status from the front matter, not source text
    records = _build_pedagogy_frontmatter(typed, citation_resolutions, los)
    annotations = build_pedagogy_annotations(
        records,
        los,
        dispatch_live=dispatch_live,
        chat_model_factory=chat_model_factory,
    )
    assert_pedagogy_teachable_consistency(annotations, records)
    return annotations


def _build_coverage_frontmatter(
    typed: list[TypedComponent],
    pedagogy_annotations: tuple[PedagogyAnnotation, ...],
    los: list[LearningObjective],
) -> list[dict[str, Any]]:
    """Project typed components into the front matter the COVERAGE pass consumes.

    The coverage segmenter reads ``component_id`` / ``type`` / ``locator`` / the
    verbatim notes ``excerpt`` + the per-component ``pedagogical_role`` (from P3) and
    ``lo_refs`` (derived-first intent inputs). Only ``narration``-typed components are
    note-bearing; the coverage pass self-filters. Mirrors ``_build_pedagogy_frontmatter``.
    """
    role_by_component = {a.component_id: a.pedagogical_role for a in pedagogy_annotations}
    los_by_parent: dict[str, list[str]] = {}
    for lo in los:
        for ref in lo.source_refs:
            bucket = los_by_parent.setdefault(ref.source_id, [])
            if lo.objective_id not in bucket:
                bucket.append(lo.objective_id)
    records: list[dict[str, Any]] = []
    for comp in typed:
        records.append(
            {
                "component_id": comp.component_id,
                "type": comp.source_type,
                "locator": comp.locator,
                "excerpt": comp.excerpt,
                "pedagogical_role": role_by_component.get(comp.component_id),
                "lo_refs": list(los_by_parent.get(comp.parent_source_id, [])),
            }
        )
    return records


def _attach_coverage_annotations(
    typed: list[TypedComponent],
    pedagogy_annotations: tuple[PedagogyAnnotation, ...],
    los: list[LearningObjective],
    *,
    dispatch_live: bool,
    chat_model_factory: Any | None = None,
    non_verbatim_out: list[Any] | None = None,
) -> tuple[CoverageAnnotation, ...]:
    """Coverage attach (Step 1): per-component source-point annotations (thin delegation).

    Gated by ``coverage_pass_active()`` (default OFF) so an unflagged run attaches
    NOTHING -> the card firewall prunes the empty layer -> byte-identical. When woken,
    projects the coverage front matter (incl. the verbatim ``excerpt`` + P3 role) and
    delegates ALL segmentation to ``build_coverage_annotations`` (offline default; the
    gpt-5 live leg gated by ``dispatch_live`` exactly like P3). The receipt is DERIVED
    at the G3 seam from these authored annotations × the run's deck/narration surfaces.

    R5-A8: ``non_verbatim_out`` (when supplied) collects the F-012 dropped-paraphrase
    ledger from the live pass so the build site can persist it into g0-enrichment.json.
    """
    if not coverage_pass_active():
        return ()
    records = _build_coverage_frontmatter(typed, pedagogy_annotations, los)
    return build_coverage_annotations(
        records,
        dispatch_live=dispatch_live,
        chat_model_factory=chat_model_factory,
        non_verbatim_out=non_verbatim_out,
    )


# Filename-keyword → source-type heuristic for the OFFLINE deterministic pre-pass.
# (The LIVE LLM does the real typing; this keeps the offline surface reproducible.)
_TYPE_KEYWORDS: tuple[tuple[str, str], ...] = (
    ("quiz", "quiz"),
    ("knowledge-check", "quiz"),
    ("rubric", "rubric"),
    ("workbook", "workbook"),
    ("narration", "narration"),
    ("voiceover", "narration"),
    ("storyboard", "motion_script_storyboard"),
    ("motion", "motion_script_storyboard"),
    ("discussion", "discussion_forum"),
    ("forum", "discussion_forum"),
    ("assignment", "assignment_instructions"),
    ("exercise", "exercise_lab"),
    ("lab", "exercise_lab"),
    ("reference", "reference_citation"),
    ("citation", "reference_citation"),
    ("bibliography", "reference_citation"),
)
_DEFAULT_TYPE = "slide"


# ---------------------------------------------------------------------------
# Corpus enumeration + fingerprint (A6 enumeration is the composer's job)
# ---------------------------------------------------------------------------


def _enumerate(corpus_dir: Path) -> list[tuple[str, Path]]:
    """Return ``[(source_id, path)]`` for the deterministically-enumerated corpus.

    Reuses the composer's ``_walk_corpus_files`` so the A6 enumeration is single-
    sourced (the LLM only ADVISES type/LO; it never gates a file out). A1: an
    unreachable corpus dir raises inside ``_walk_corpus_files`` (never silently
    absent).
    """
    files = _walk_corpus_files(corpus_dir)
    return [(f"src-{i:03d}", path) for i, path in enumerate(files, start=1)]


def _fingerprint(enumerated: list[tuple[str, Path]], model_id: str) -> str:
    # A1: file_content_hash reads bytes — an unreadable/unextractable source
    # raises here (RED), never silently absent.
    hashes = [file_content_hash(path) for _, path in enumerated]
    # W9: P3 rides the SAME corpus-fingerprint freeze key — no second cache
    # namespace. `model_id` already subsumes the LLM model id (live "marcus" vs the
    # offline marker); pin the P3 transform VERSION alongside it so a P3 transform
    # bump invalidates the frozen result (and the pedagogy transform_model tracks
    # `model_id` 1:1 via the same live/offline split).
    seed = f"{model_id}|ped:{PEDAGOGY_TRANSFORM_VERSION}"
    return corpus_fingerprint(hashes, seed)


# Encoding ladder for reading a text source: utf-8 → cp1252 → latin-1, then a
# lossy replace as a last resort. A cp1252-only outline (e.g. a Windows smart
# quote 0x92) must still decode to text + segment into intra-document components
# rather than collapse to one whole-file binary fallback. Mirrors the Texas
# cp1252 Windows-portability fix (migration 7c-2).
_TEXT_ENCODINGS: tuple[str, ...] = ("utf-8", "cp1252", "latin-1")


def _read_text_resilient(path: Path) -> str | None:
    """Read a text source over the encoding ladder; ``None`` only on real binary/OSError.

    Tries utf-8, then cp1252, then latin-1, then a lossy ``errors="replace"``
    decode BEFORE giving up. Returns ``None`` (→ the binary fallback component)
    only when the file is unreadable (``OSError``) or genuinely binary (contains a
    NUL byte — text, including cp1252, does not). This keeps a cp1252 outline
    yielding real components while a true binary (image/pdf) still gets the
    whole-file fallback.
    """
    try:
        raw = path.read_bytes()
    except OSError:
        return None
    if b"\x00" in raw:
        return None  # genuine binary (NUL byte) → whole-file fallback
    for encoding in _TEXT_ENCODINGS:
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def _heuristic_type(path: Path) -> str:
    name = path.name.lower()
    for keyword, source_type in _TYPE_KEYWORDS:
        if keyword in name:
            return source_type
    return _DEFAULT_TYPE


def _component_type(label: str, body: str) -> str:
    """Heuristic component TYPE from heading-label + body text (offline only).

    The LIVE LLM does the real instructional-designer typing; this keeps the
    OFFLINE component split deterministic + reproducible.
    """
    haystack = f"{label}\n{body}".lower()
    for keyword, source_type in _TYPE_KEYWORDS:
        if keyword in haystack:
            return source_type
    return _DEFAULT_TYPE


# Excerpt cap for one offline component (verbatim prefix of the section body).
_COMPONENT_EXCERPT_MAX_CHARS = 200
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")


def _split_components(text: str, file_label: str) -> list[dict[str, str]]:
    """Deterministically segment ONE document into components by markdown heading.

    Each heading-delimited section becomes one component with a document-hierarchy
    ``locator`` (the breadcrumb of ancestor heading titles, e.g.
    ``"Doc Title > Section > Sub-section"``), a verbatim ``excerpt`` (the first
    non-empty body line, or the heading label when the section has no body), and a
    keyword-heuristic ``source_type``. Preamble text before the first heading
    becomes a leading component rooted at ``file_label``. A document with NO
    headings returns a single whole-file component; an empty document returns
    ``[]`` (the caller adds a coverage fallback so no FILE is silently dropped).

    Pure + reproducible (same bytes → same components), no LLM.
    """
    lines = text.splitlines()
    stack: list[tuple[int, str]] = []
    sections: list[dict[str, list[str]]] = []
    preamble: list[str] = []
    current: dict[str, list[str]] | None = None

    for line in lines:
        match = _HEADING_RE.match(line)
        if match:
            level = len(match.group(1))
            title = match.group(2).strip() or "(untitled)"
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, title))
            current = {"titles": [t for _, t in stack], "body": []}
            sections.append(current)
        elif current is None:
            preamble.append(line)
        else:
            current["body"].append(line)

    ordered: list[dict[str, list[str]]] = []
    if any(line.strip() for line in preamble):
        ordered.append({"titles": [file_label], "body": preamble})
    ordered.extend(sections)

    out: list[dict[str, str]] = []
    for sec in ordered:
        titles = sec["titles"] or [file_label]
        body_lines = [line for line in sec["body"] if line.strip()]
        label = titles[-1]
        locator = " > ".join(titles)
        excerpt = (body_lines[0].strip() if body_lines else label)[:_COMPONENT_EXCERPT_MAX_CHARS]
        excerpt = excerpt or label or file_label
        source_type = _component_type(label, "\n".join(sec["body"]))
        out.append(
            {"label": label, "locator": locator, "excerpt": excerpt, "source_type": source_type}
        )
    return out


def _file_components(source_id: str, path: Path, corpus_dir: Path) -> list[TypedComponent]:
    """Segment ONE enumerated file into >=1 TypedComponent (coverage guaranteed).

    A readable text file is split by heading (``_split_components``); an empty file
    or a binary/unreadable source yields a single whole-file fallback component so
    EVERY enumerated file is covered by >=1 component (no file silently dropped —
    the file-coverage reconcile invariant).
    """
    rel = path.relative_to(corpus_dir).as_posix()
    file_label = path.stem or rel
    text = _read_text_resilient(path)
    if text is None:
        sections: list[dict[str, str]] = []
        fallback_type = _heuristic_type(path)
        sections.append(
            {
                "label": file_label,
                "locator": file_label,
                "excerpt": "[binary or unreadable source — typed from filename]",
                "source_type": fallback_type,
            }
        )
    else:
        sections = _split_components(text, file_label)
        if not sections:
            sections = [
                {
                    "label": file_label,
                    "locator": file_label,
                    "excerpt": f"[empty source: {rel}]",
                    "source_type": _heuristic_type(path),
                }
            ]
    return [
        TypedComponent(
            component_id=f"{source_id}-c{idx:03d}",
            parent_source_id=source_id,
            source_type=sec["source_type"],  # type: ignore[arg-type]
            label=sec["label"],
            locator=sec["locator"],
            excerpt=sec["excerpt"],
        )
        for idx, sec in enumerate(sections, start=1)
    ]


# Per-source content budget fed to the LIVE pre-pass prompt. The model must SEE
# the WHOLE source document to extract ALL its embedded components — a small cap
# truncates the doc and the extraction collapses (a live run on the 150KB outline
# with a 6000-char cap found only 25 of ~188 components: it saw the first 4%).
# Sized to hold a full richly-annotated course-outline document (~150KB ≈ 40K
# tokens) with headroom; a frontier model's context easily fits one such file.
# FOLLOW-ON (huge multi-file corpora): if total corpus text would exceed the
# model context, chunk per-file / per-Part rather than lowering this cap — never
# silently truncate a document (that drops components). See charter P1.
_LIVE_EXCERPT_MAX_CHARS = 240_000


def _source_excerpt(path: Path, max_chars: int = _LIVE_EXCERPT_MAX_CHARS) -> str:
    """A bounded, verbatim content excerpt of a text source for the live prompt."""
    text = _read_text_resilient(path)
    if text is None:
        return "[binary or unreadable source — type from filename only]"
    text = text.strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n…[excerpt truncated]"


def _live_corpus_summary(enumerated: list[tuple[str, Path]], corpus_dir: Path) -> str:
    """Corpus block for the live prompt: id + path + VERBATIM content excerpt.

    Verbatim so the model's required ``quoted_span`` substrings actually resolve
    against text it was shown (A9 groundedness).
    """
    blocks = []
    for sid, path in enumerated:
        rel = path.relative_to(corpus_dir).as_posix()
        blocks.append(f"### {sid}: {rel}\n{_source_excerpt(path)}")
    return "\n\n".join(blocks)


# ---------------------------------------------------------------------------
# Excerpt groundedness (ADVISORY at P1 — flag, never crash)
# ---------------------------------------------------------------------------

# Backslash-escaped markdown punctuation the model routinely un-escapes when it
# quotes a span (e.g. source ``\$760`` → excerpt ``$760``). Unescaped on BOTH
# sides before the substring check so a benign markdown rewrite is NOT mistaken
# for a fabrication. Set per the P1 live finding (2026-06-27): a strict byte
# check false-rejected ~27% (4/26) of FAITHFUL extractions that diverged from the
# source ONLY by ``\$``/``> ``/whitespace.
_MD_PUNCT_UNESCAPE_RE = re.compile(r"\\([$#*\[\]()\-.])")
_WS_RUN_RE = re.compile(r"\s+")


def _strip_blockquote_prefix(line: str) -> str:
    """Strip leading blockquote ``>`` / ``> `` prefixes from one line (repeatable)."""
    stripped = line.lstrip()
    while stripped.startswith(">"):
        stripped = stripped[1:]
        if stripped.startswith(" "):
            stripped = stripped[1:]
    return stripped


def _normalize_for_groundedness(text: str) -> str:
    """Markdown-normalize text for an excerpt-vs-source substring comparison.

    Applied to BOTH the excerpt and the parent-source text before comparing:
      1. strip leading blockquote ``>``/``> `` prefixes per line;
      2. unescape backslash-escaped markdown punctuation (``\\$``→``$`` etc.);
      3. collapse every whitespace run (incl. newlines) to a single space.

    A strict byte check would false-reject faithful extractions that diverge only
    by these benign markdown artifacts (P1 live finding) — normalizing is the
    whole point.
    """
    lines = [_strip_blockquote_prefix(line) for line in text.splitlines()]
    joined = "\n".join(lines)
    joined = _MD_PUNCT_UNESCAPE_RE.sub(r"\1", joined)
    return _WS_RUN_RE.sub(" ", joined).strip()


def _is_excerpt_grounded(excerpt: str, source_text: str) -> bool:
    """True iff ``excerpt`` is a substring of ``source_text`` after md-normalization.

    An excerpt that normalizes to empty is treated as grounded (nothing to
    ground); otherwise a markdown-normalized substring containment decides it.
    """
    norm_excerpt = _normalize_for_groundedness(excerpt)
    if not norm_excerpt:
        return True
    return norm_excerpt in _normalize_for_groundedness(source_text)


def flag_ungrounded_components(
    typed: list[TypedComponent],
    source_by_id: dict[str, str],
) -> int:
    """ADVISORY (P1): flag components whose excerpt is not grounded in its parent.

    Mutates ``flagged_ungrounded=True`` + logs a warning for each component whose
    markdown-normalized excerpt is NOT a substring of its (md-normalized) parent
    source. NEVER raises and NEVER drops a component — the operator confirms at
    gate #1. Returns the number of components flagged.
    """
    normalized_sources = {
        sid: _normalize_for_groundedness(text) for sid, text in source_by_id.items()
    }
    n_flagged = 0
    for comp in typed:
        norm_source = normalized_sources.get(comp.parent_source_id)
        if norm_source is None:
            # No parent text available (e.g. binary/unreadable) — cannot judge
            # groundedness; leave unflagged rather than false-flag.
            continue
        norm_excerpt = _normalize_for_groundedness(comp.excerpt)
        if not norm_excerpt or norm_excerpt in norm_source:
            continue
        comp.flagged_ungrounded = True
        n_flagged += 1
        logger.warning(
            "g0-enrichment: component %r excerpt is NOT grounded in parent %r after "
            "markdown normalization (advisory flag; operator confirms at gate #1): %.80s",
            comp.component_id,
            comp.parent_source_id,
            comp.excerpt,
        )
    return n_flagged


# ---------------------------------------------------------------------------
# Offline deterministic pre-pass (corpus-derived; reproducible)
# ---------------------------------------------------------------------------


def _offline_pre_pass(
    enumerated: list[tuple[str, Path]],
    corpus_dir: Path,
) -> tuple[list[TypedComponent], list[LearningObjective], list[EnumerationProvenance]]:
    """Deterministically extract typed COMPONENTS (N per file) + provisional LOs.

    Replaces the prior file-level typing (one whole file → one type): each
    enumerated FILE is structurally split into >=1 typed component
    (``_file_components``), so a multi-section document yields many components.
    Reproducible (same bytes → same components), no LLM.
    """
    typed: list[TypedComponent] = []
    provenance: list[EnumerationProvenance] = []
    los: list[LearningObjective] = []
    enumerated_ids = {sid for sid, _ in enumerated}

    for lo_index, (source_id, path) in enumerate(enumerated, start=1):
        rel = path.relative_to(corpus_dir).as_posix()
        provenance.append(
            EnumerationProvenance(
                source_id=source_id,
                root_id=corpus_dir.resolve().as_posix(),
                connector="local_file",
                locator=rel,
            )
        )
        components = _file_components(source_id, path, corpus_dir)
        typed.extend(components)
        # Candidate LO: one provisional LO per file, GROUNDED in the file's first
        # extracted component (its locator + verbatim excerpt). A populated ref
        # points at the enumerated FILE id (A6) with the component locator (A9).
        first = components[0]
        refs = (
            SourceRef(
                source_id=source_id,
                locator=first.locator,
                quoted_span=first.excerpt,
            ),
        )
        lo = LearningObjective(
            objective_id=f"lo-g0-{lo_index:03d}",
            statement=(
                f"Understand the material introduced by {source_id} "
                f"({first.excerpt[:60]})."
            ),
            status="provisional",
            confidence="low",
            source_refs=refs,
        )
        # Surface the g0 mint edge (idempotent (provisional, provisional, g0)).
        lo = advance_lo(lo, "provisional", actor="g0")
        los.append(lo)

    _assert_refs_enumerated(los, enumerated_ids)
    return typed, los, provenance


def _assert_refs_enumerated(los: list[LearningObjective], enumerated_ids: set[str]) -> None:
    """RED on a fabricated source_id: every emitted SourceRef must resolve (A9/A1)."""
    for lo in los:
        for ref in lo.source_refs:
            if ref.source_id not in enumerated_ids:
                raise ValueError(
                    f"provisional LO {lo.objective_id!r} cites source_id "
                    f"{ref.source_id!r} which is NOT in the enumerated corpus set "
                    "(fabricated provenance is RED)"
                )


def _build_dissent(typed: list[TypedComponent], fingerprint: str) -> Dissent:
    """Derive ONE real, corpus-varying dissent (A3/A11 — never theater).

    The target component + alternative type are a deterministic function of the
    corpus fingerprint, so the dissent VARIES run-to-run across different corpora
    (a never-varying dissent carries no information). Independent-parse-sourced:
    Marcus's position is his own heuristic typing of the segmented component.
    """
    if not typed:
        # A component-less corpus still owes a real dissent: dissent the empty
        # enumeration itself (operator confirms there were genuinely no spans).
        return Dissent(
            against="corpus",
            marcus_position="independent parse found zero typeable components",
            operator_position="",
            disposition="upheld",
        )
    pick = int(fingerprint[:8], 16) % len(typed)
    target = typed[pick]
    alternatives = [
        t
        for t in ("slide", "workbook", "reference_citation", "narration")
        if t != target.source_type
    ]
    alt = alternatives[int(fingerprint[8:16], 16) % len(alternatives)]
    return Dissent(
        against=target.component_id,
        marcus_position=(
            f"typed {target.component_id} ({target.locator}) as "
            f"{target.source_type}; a defensible alternative reading is {alt}"
        ),
        operator_position="",
        disposition="upheld",
    )


# ---------------------------------------------------------------------------
# Live-response tolerant parse (the targeted reliability fix; UNIT-TESTABLE).
#
# Found LIVE (2026-06-29 tejal trial, real gpt-5): the bare ``json.loads(
# response.content)`` below crashed the whole production walk at G0E with
# ``JSONDecodeError: Invalid control character`` — gpt-5 returned a large JSON
# object carrying a LITERAL control character (unescaped newline/tab) INSIDE a
# string value, which strict ``json.loads`` rejects, before any gate. Extracted
# out of the ``# pragma: no cover`` live leg so it is unit-testable; mirrors the
# proven tolerant pattern (coverage ``extract_coverage_rows`` / pedagogy
# ``_extract_pedagogy_rows``) + the targeted ``strict=False`` fix.
# ---------------------------------------------------------------------------


class G0EnrichmentParseError(ValueError):
    """The live Marcus-SPOC pre-pass response could not be parsed as JSON.

    Raised by :func:`_parse_live_extraction_response` when a real gpt-5
    component-extraction response is not recoverable as JSON even after
    control-character-tolerant parsing (``strict=False``) and first-``{...}``-span
    extraction. Carries a snippet of the offending text + the underlying decoder
    reason so the operator sees WHY the keystone pre-pass failed. Subclasses
    ``ValueError`` (so existing ``except (ValueError, TypeError)`` guards catch it)
    but is a DISTINCT, named domain error — never a bare ``JSONDecodeError`` and
    never a silently-empty extraction (an empty keystone pre-pass would hide a
    broken live pass; this fails LOUD instead).
    """


def _live_response_to_text(content: Any) -> str:
    """Coerce a chat-model ``response.content`` to text (str or content-block list).

    Mirrors ``coverage_annotation._content_to_text`` /
    ``pedagogy_annotation._content_to_text``: a bare ``str`` passes through; a
    content-block list (``[{"text": "..."}, ...]``) is concatenated; anything else
    degrades to ``""``.
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and isinstance(block.get("text"), str):
                parts.append(block["text"])
        return "".join(parts)
    return ""


_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)

# Provenance keys stamped on a SALVAGED (truncated) payload so a PARTIAL extraction
# is surfaced downstream + at the decision card, never silently treated as complete.
_TRUNCATION_FLAG_KEY = "_g0_extraction_truncated"
_RECOVERED_COUNT_KEY = "_g0_extraction_recovered_components"


def _salvage_array(text: str, key: str) -> list[Any] | None:
    """Recover the longest valid PREFIX of a top-level JSON array ``"key": [ ... ]``.

    Parses as many COMPLETE element objects as possible from a possibly-TRUNCATED
    array, discarding a trailing partial element. Returns the recovered list
    (possibly empty) when the ``"key": [`` opener is found, else ``None``. Uses
    ``JSONDecoder.raw_decode`` (``strict=False`` — same control-char tolerance) to
    walk element-by-element so a truncated final object stops the walk cleanly.
    """
    opener = re.search(r'"' + re.escape(key) + r'"\s*:\s*\[', text)
    if not opener:
        return None
    decoder = json.JSONDecoder(strict=False)
    idx = opener.end()
    n = len(text)
    items: list[Any] = []
    while idx < n:
        while idx < n and text[idx] in " \t\r\n,":
            idx += 1
        if idx >= n or text[idx] == "]":
            break
        try:
            obj, idx = decoder.raw_decode(text, idx)
        except (ValueError, TypeError):
            break  # truncated / partial final element — stop, keep the prefix
        items.append(obj)
    return items


def _salvage_truncated_payload(text: str) -> dict[str, Any] | None:
    """Best-effort salvage of a TRUNCATED extraction payload (gpt-5 hit its output
    ceiling mid-JSON — the 2026-06-29 line-196 crash).

    Recovers the complete-object prefix of the ``components`` array (and
    ``learning_objectives`` if present). Returns a dict carrying the recovered
    arrays + a provenance flag when >=1 complete component is recovered, else
    ``None`` (the caller then raises — zero-recovery is total failure, never silent).
    """
    components = _salvage_array(text, "components")
    if not components:
        return None
    salvaged: dict[str, Any] = {
        "components": components,
        _TRUNCATION_FLAG_KEY: True,
        _RECOVERED_COUNT_KEY: len(components),
    }
    los = _salvage_array(text, "learning_objectives")
    if los:
        salvaged["learning_objectives"] = los
    return salvaged


def _parse_live_extraction_response(content: Any) -> Any:
    """Tolerant parse of the live COMPONENT-extraction response into a JSON payload.

    The targeted fix for the 2026-06-29 live crash (strict ``json.loads`` rejecting
    a literal control character inside a gpt-5 string value). Mirrors the proven
    tolerant pattern:

      1. normalize ``content`` (str OR content-block list) to text;
      2. strip a ```json ... ``` fence when the body is fenced;
      3. ``json.loads(text, strict=False)`` — ``strict=False`` permits control
         characters within strings (the exact crash class);
      4. on failure, extract the first ``{...}`` span and retry with ``strict=False``;
      5. on TOTAL failure raise :class:`G0EnrichmentParseError` (snippet + reason) —
         NOT a bare ``JSONDecodeError`` and NOT a silent ``{}``.

    Returns the parsed JSON value. The contract is a JSON OBJECT, but a
    successfully-parsed NON-dict is passed through unchanged so
    :func:`_parse_live_payload`'s MUST-2 file-coverage fallback can absorb shape
    drift (top-level list / bare value) without crashing — only a genuinely
    UNPARSEABLE (or empty) response raises.
    """
    text = _live_response_to_text(content).strip()
    if not text:
        raise G0EnrichmentParseError(
            "live G0 pre-pass returned EMPTY response content (no JSON to parse); the "
            "keystone component-extraction produced nothing — fail loud, do not ship an "
            "empty enrichment (strict=False parse not attempted: no text)."
        )
    fence = _JSON_FENCE_RE.search(text)
    if fence:
        text = fence.group(1).strip()
    try:
        return json.loads(text, strict=False)
    except (ValueError, TypeError) as exc:
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start : end + 1], strict=False)
            except (ValueError, TypeError):
                pass
        # SALVAGE (defense): the response is a well-formed JSON PREFIX truncated
        # mid-structure (gpt-5 spent its output budget on hidden reasoning then
        # truncated the visible JSON — the 2026-06-29 line-196 crash). Recover the
        # longest complete-object prefix of the components array. LOUD, never silent:
        # warn + stamp a provenance flag so a PARTIAL extraction is surfaced downstream
        # (operator confirms/corrects at gate #1), never treated as complete.
        salvaged = _salvage_truncated_payload(text)
        if salvaged is not None:
            n_recovered = salvaged[_RECOVERED_COUNT_KEY]
            logger.warning(
                "g0-enrichment live: extraction response was TRUNCATED mid-JSON "
                "(%s: %s) — SALVAGED %d complete component(s) from the valid prefix "
                "(of an UNKNOWN total; the model hit its output-token ceiling). This is "
                "a PARTIAL extraction surfaced for operator confirmation at gate #1, NOT "
                "a complete one. Raise G0_EXTRACTION_MAX_COMPLETION_TOKENS (currently "
                "%d) if truncation recurs.",
                type(exc).__name__,
                exc,
                n_recovered,
                G0_EXTRACTION_MAX_COMPLETION_TOKENS,
            )
            return salvaged
        # TOTAL failure (zero complete objects recovered): fail LOUD. Surface BOTH the
        # head AND the tail of the offending text — for a truncation the failure is at
        # the END, so the tail is the most diagnostic part (no live re-run needed).
        head = text[:400]
        tail = text[-400:] if len(text) > 800 else ""
        snippet = head + (f" […{len(text) - 800} chars elided…] {tail}" if tail else "")
        raise G0EnrichmentParseError(
            "live G0 pre-pass response is not parseable as JSON even with "
            "control-character-tolerant parsing (strict=False) + first-{...}-span "
            "extraction + truncated-prefix salvage (zero complete components recovered) "
            f"({type(exc).__name__}: {exc}); offending text (head+tail): {snippet!r}"
        ) from exc


# ---------------------------------------------------------------------------
# Live LLM pre-pass (exercised by AC-S2-8; reuses the pre_gate_marcus seam)
# ---------------------------------------------------------------------------


def _default_extraction_chat_factory() -> Callable[[str], Any]:
    """Build the DEFAULT (None-fallback) chat-model factory for the live extraction.

    Binds a HARD per-request timeout, ``max_retries=0``, AND a GENEROUS
    ``max_completion_tokens`` output budget so the keystone gpt-5 extraction does not
    truncate mid-JSON (the 2026-06-29 live crash root cause). Mirrors the proven
    coverage-leg pattern (``coverage_annotation._live_coverage_pass``). ``make_chat_model``
    binds NEITHER a timeout NOR an output ceiling by default, so the None-fallback MUST
    set them explicitly or the default path can hang AND/OR truncate.
    """
    from app.models.adapter import make_chat_model

    def factory(model_id: str) -> Any:
        return make_chat_model(
            model_id,
            request_timeout=G0_EXTRACTION_REQUEST_TIMEOUT_S,
            max_retries=0,
            max_completion_tokens=G0_EXTRACTION_MAX_COMPLETION_TOKENS,
        )

    return factory


def _live_pre_pass(
    enumerated: list[tuple[str, Path]],
    corpus_dir: Path,
    chat_model_factory: Any,
) -> tuple[
    list[TypedComponent], list[LearningObjective], list[EnumerationProvenance]
]:  # pragma: no cover - live leg
    """REAL Marcus-SPOC COMPONENT-extraction pre-pass via make_chat_model + j2.

    Mirrors the proven ``id_extract2`` Instructional-Designer prompt (188
    components from one 150KB outline): each enumerated FILE is shown with its id
    + VERBATIM content, and the model segments EACH document into the typed
    components embedded inline (type / label / locator / verbatim excerpt). Off
    the deterministic critical path; exercised by the operator-gated live-segment
    proof, not the offline suite.
    """
    from app.marcus.orchestrator.pre_gate_marcus import render_pre_fill_prompt

    # Feed VERBATIM per-source content excerpts (not just paths) so the model can
    # segment + type accurately + ground its components/LOs in shown text.
    corpus_summary = _live_corpus_summary(enumerated, corpus_dir)
    prompt = render_pre_fill_prompt(
        gate_id="g0-enrichment",
        slot_values={
            "corpus_summary": corpus_summary,
            "source_count": len(enumerated),
        },
    )
    if chat_model_factory is None:
        # Default path MUST bind the generous output budget + hard timeout (root-cause
        # fix for the 2026-06-29 truncation crash); a passed-in harness factory is used
        # as-is (it binds its own budget per the T8 contract).
        chat_model_factory = _default_extraction_chat_factory()
    handle = chat_model_factory("marcus")
    response = handle.chat.invoke([{"role": "user", "content": prompt}])
    # Control-character-tolerant parse (strict=False) of the live response — a bare
    # strict json.loads here crashed the whole walk at G0E on a gpt-5 string value
    # carrying a literal control char (2026-06-29). Raises a CLEAR G0EnrichmentParseError
    # (never a bare JSONDecodeError, never a silent {}) on a truly-unparseable response.
    payload = _parse_live_extraction_response(response.content)
    return _parse_live_payload(payload, enumerated, corpus_dir)


def _coerce_component_row(row: dict[str, Any], pid: str, parent_rel: str) -> dict[str, Any]:
    """Normalize one LLM component row to the TypedComponent kwargs shape.

    Tolerant of the proven ``id_extract2`` shape (``type``/``excerpt``) and minor
    drift; missing label/locator/excerpt are defensively filled so the reconcile
    never crashes on a sparse row (the operator confirms/corrects at gate #1).
    """
    source_type = row.get("source_type") or row.get("type") or _DEFAULT_TYPE
    label = str(row.get("label") or source_type).strip() or str(source_type)
    locator = str(row.get("locator") or parent_rel).strip() or parent_rel
    excerpt = str(row.get("excerpt") or row.get("quoted_span") or label).strip() or label
    # Normalize the `other` escape hatch: the OtherSourceType.kind is the fixed
    # literal "other" with the real label in `label`, but the live model often
    # puts the actual type name in `kind` (e.g. kind="learning_objectives") — that
    # tripped TypedComponent validation in a live E2E. Force kind="other", keep the
    # model's value as the label; non-`other` types carry no other_type.
    other_type: dict[str, Any] | None = None
    if source_type == "other":
        raw = row.get("other_type") if isinstance(row.get("other_type"), dict) else {}
        other_type = {
            "kind": "other",
            "label": str(raw.get("label") or raw.get("kind") or label),
            "provenance": str(raw.get("provenance") or "fell outside the closed 10-type set"),
        }
    return {
        "parent_source_id": pid,
        "source_type": source_type,
        "other_type": other_type,
        "label": label,
        "locator": locator,
        "excerpt": excerpt,
    }


def _parse_live_payload(
    payload: dict[str, Any],
    enumerated: list[tuple[str, Path]],
    corpus_dir: Path,
) -> tuple[list[TypedComponent], list[LearningObjective], list[EnumerationProvenance]]:
    """Reconcile an LLM COMPONENT-extraction payload against enumerated files (A6).

    The live model will not reliably segment EXACTLY the enumerated file set (it
    cites fabricated parent files, duplicates components, or returns zero
    components for a file). FILES are the A6 unit and COMPONENTS the deliverables,
    so the reconcile guarantees FILE-COVERAGE, not a 1:1 count:

      * DROP component rows whose ``parent_source_id`` is not an enumerated file
        (fabricated — A1/A9: the LLM cannot invent a source) with a loud log;
      * dedup a parent's components by ``(locator, label, excerpt)`` (first wins);
      * mint deterministic ``component_id`` = ``"{pid}-c{idx:03d}"`` per parent;
      * for any enumerated FILE the model returned ZERO components for, add ONE
        whole-file COVERAGE FALLBACK component (heuristic type) so no file is
        silently dropped (the file-coverage reconcile invariant).

    Components are emitted GROUPED BY enumerated file in enumeration order (so the
    decision card groups by parent file). ``n_files_covered == n_files_in`` by
    construction (every file owes >=1 component via the fallback).
    """
    enumerated_ids = [sid for sid, _ in enumerated]
    enumerated_id_set = set(enumerated_ids)
    by_id = {sid: path for sid, path in enumerated}

    # MUST-2: guard the live payload shape. A non-dict payload (top-level list,
    # bare string, ...) or a non-list ``components`` (e.g. components-as-dict) is
    # treated as ZERO component rows — the file-coverage fallback below still
    # covers every enumerated file, so the reconcile never crashes on drift.
    if not isinstance(payload, dict):
        logger.warning(
            "g0-enrichment live: payload is %s, not a dict; treating as zero "
            "component rows (the file-coverage fallback covers every file)",
            type(payload).__name__,
        )
        payload = {}
    rows = (
        payload.get("components")
        or payload.get("typed_components")
        or payload.get("typed_sources")
        or []
    )
    if not isinstance(rows, list):
        logger.warning(
            "g0-enrichment live: components payload is %s, not a list; treating as "
            "zero component rows (file-coverage fallback covers every file)",
            type(rows).__name__,
        )
        rows = []
    per_parent: dict[str, list[dict[str, Any]]] = {sid: [] for sid in enumerated_ids}
    for row in rows:
        if not isinstance(row, dict):
            logger.warning(
                "g0-enrichment live: skipping non-dict component row %r", row
            )
            continue
        pid = str(row.get("parent_source_id") or row.get("source_id") or "")
        if pid not in enumerated_id_set:
            logger.warning(
                "g0-enrichment live: dropping component for unknown parent id %r "
                "(not in enumerated corpus — fabricated)",
                pid,
            )
            continue
        per_parent[pid].append(row)

    typed: list[TypedComponent] = []
    for sid in enumerated_ids:
        path = by_id[sid]
        parent_rel = path.relative_to(corpus_dir).as_posix()
        seen: set[tuple[str, str, str]] = set()
        components: list[TypedComponent] = []
        for row in per_parent[sid]:
            kwargs = _coerce_component_row(row, sid, parent_rel)
            dedup_key = (kwargs["locator"], kwargs["label"], kwargs["excerpt"])
            if dedup_key in seen:
                logger.warning(
                    "g0-enrichment live: duplicate component %r for %r; keeping first",
                    kwargs["label"],
                    sid,
                )
                continue
            seen.add(dedup_key)
            components.append(
                TypedComponent(
                    component_id=f"{sid}-c{len(components) + 1:03d}",
                    **kwargs,
                )
            )
        if not components:
            logger.info(
                "g0-enrichment live: file %r returned zero components; adding a "
                "whole-file coverage fallback (operator confirms at gate #1)",
                sid,
            )
            components = _file_components(sid, path, corpus_dir)
        typed.extend(components)

    provenance = [
        EnumerationProvenance(
            source_id=sid,
            root_id=corpus_dir.resolve().as_posix(),
            connector="local_file",
            locator=path.relative_to(corpus_dir).as_posix(),
        )
        for sid, path in enumerated
    ]
    # MUST-1: guard EACH live LO row. One malformed/under-specified row must NOT
    # abort the whole pre-pass (which would also discard every already-extracted
    # component); skip the bad row + log + continue.
    raw_los = payload.get("provisional_los", [])
    if not isinstance(raw_los, list):
        logger.warning(
            "g0-enrichment live: provisional_los is %s, not a list; treating as none",
            type(raw_los).__name__,
        )
        raw_los = []
    los: list[LearningObjective] = []
    for row in raw_los:
        try:
            if not isinstance(row, dict):
                raise TypeError(f"LO row is {type(row).__name__}, not a dict")
            lo = LearningObjective.model_validate({**row, "status": "provisional"})
            lo = advance_lo(lo, "provisional", actor="g0")
        except (ValidationError, ValueError, TypeError) as exc:
            logger.warning(
                "g0-enrichment live: dropping malformed provisional LO row (%s); "
                "keeping the already-extracted components + the valid LOs",
                exc,
            )
            continue
        los.append(lo)
    _assert_refs_enumerated(los, enumerated_id_set)
    return typed, los, provenance


# ---------------------------------------------------------------------------
# Result assembly + cache
# ---------------------------------------------------------------------------


def _cache_path(run_dir: Path, fingerprint: str) -> Path:
    return run_dir / _CACHE_DIRNAME / f"{fingerprint}.json"


def build_enrichment_result(
    *,
    corpus_dir: Path,
    dispatch_live: bool,
    chat_model_factory: Any | None = None,
    resolve_dispatch: Callable[[Any], Any] | None = None,
    non_verbatim_out: list[Any] | None = None,
) -> G0EnrichmentResult:
    """Run the pre-pass (offline OR live) and assemble the frozen result.

    Pure of run-dir/cache side effects (those live in ``run_g0_enrichment``) so
    the assembly is unit-testable in isolation.

    R5-A8: ``non_verbatim_out`` (when supplied) collects the F-012 dropped-paraphrase
    ledger from the live coverage pass; ``run_g0_enrichment`` persists it additively
    into g0-enrichment.json for the G3 marshaller to surface ledger-only.

    ``resolve_dispatch`` is the DD3 citation-resolution dispatch seam: when
    supplied (offline tests) OR ``dispatch_live`` is True (live scite), the Texas
    pass-0 resolver runs over the citation-bearing components and the verdicts
    ride ``citation_resolutions``. Otherwise resolution is skipped (network-free
    offline path).
    """
    enumerated = _enumerate(corpus_dir)
    model_id = G0_ENRICHMENT_LIVE_MODEL_ID if dispatch_live else G0_ENRICHMENT_MODEL_MARKER
    fingerprint = _fingerprint(enumerated, model_id)

    independent_ts = datetime.now(UTC)
    if dispatch_live:
        typed, los, provenance = _live_pre_pass(enumerated, corpus_dir, chat_model_factory)
    else:
        typed, los, provenance = _offline_pre_pass(enumerated, corpus_dir)

    # SHOULD-A4 (advisory): flag any component whose excerpt is not grounded in
    # its parent source after markdown normalization (offline excerpts are
    # verbatim-by-construction → 0; the live leg is where this earns its keep).
    source_by_id = {sid: (_read_text_resilient(path) or "") for sid, path in enumerated}
    n_ungrounded = flag_ungrounded_components(typed, source_by_id)

    # DD3 attach: AFTER groundedness flagging, BEFORE result construction —
    # resolve the citation-bearing components live (scite) into CitationResolution
    # rows. Rides this existing g0-enrichment node + the existing fingerprint cache
    # (DD7) + the existing G0E gate; no new gate/side-effect.
    citation_resolutions = _resolve_citation_resolutions(
        typed,
        source_by_id,
        dispatch_live=dispatch_live,
        resolve_dispatch=resolve_dispatch,
    )

    # P3 attach: AFTER citation resolution, BEFORE result construction — layer the
    # per-component pedagogy annotations (bloom / role / teaches_after / teachable /
    # rationale) on the P2 universal-md front matter. Rides this existing
    # g0-enrichment node + the existing fingerprint cache (W9) + the existing G0E
    # gate; no new gate/side-effect. Gated by dispatch_live like the resolver.
    pedagogy_annotations = _attach_pedagogy_annotations(
        typed,
        source_by_id,
        citation_resolutions,
        los,
        dispatch_live=dispatch_live,
        chat_model_factory=chat_model_factory,
    )

    # Coverage attach (Step 1): AFTER pedagogy (it reads the per-component role) — layer
    # the authored source-point annotations onto the same g0-enrichment node + cache +
    # G0E gate. Gated by coverage_pass_active() (default OFF → empty → card pruned →
    # byte-identical). The G3 seam DERIVES the receipt from these × the run surfaces.
    coverage_annotations = _attach_coverage_annotations(
        typed,
        pedagogy_annotations,
        los,
        dispatch_live=dispatch_live,
        chat_model_factory=chat_model_factory,
        non_verbatim_out=non_verbatim_out,
    )

    independent_parse = IndependentParse(
        proposal={
            "typed_components": [t.model_dump(mode="json") for t in typed],
            "provisional_los": [lo.objective_id for lo in los],
        },
        ts=independent_ts,
    )
    dissent = _build_dissent(typed, fingerprint)
    n_files_in = len(enumerated)
    covered_files = {c.parent_source_id for c in typed}
    n_files_covered = len(covered_files)
    n_flagged = sum(1 for t in typed if t.flagged_unconsumed)
    reconcile = ReconcileView(
        n_files_in=n_files_in,
        n_files_covered=n_files_covered,
        # offline: every enumerated file is covered by >=1 component (the coverage
        # fallback guarantees it); operator-confirmed file-ignore happens at gate #1.
        n_files_ignored=n_files_in - n_files_covered,
        n_components=len(typed),
        n_flagged=n_flagged,
        n_ungrounded=n_ungrounded,
    )
    roots = [
        TraversalRoot(root_id=corpus_dir.resolve().as_posix(), kind="corpus_dir"),
    ]
    result = G0EnrichmentResult(
        corpus_fingerprint=fingerprint,
        model_id=model_id,
        typed_components=typed,
        provisional_los=los,
        traversal_roots=roots,
        enumeration_provenance=provenance,
        reconcile=reconcile,
        dissents=[dissent],
        citation_resolutions=citation_resolutions,
        pedagogy_annotations=pedagogy_annotations,
        coverage_annotations=coverage_annotations,
        independent_parse=independent_parse,
    )
    assert_run_dissent_invariant(result)
    assert_pedagogy_referential_invariant(result)
    return result


def run_g0_enrichment(
    *,
    node_id: str,
    production_envelope: ProductionEnvelope,
    corpus_dir: Path,
    trial_id: UUID | str,
    runs_root: Path,
    dispatch_live: bool = False,
    chat_model_factory: Any | None = None,
    resolve_dispatch: Callable[[Any], Any] | None = None,
) -> ProductionEnvelope:
    """Execute the G0-enrichment hook at ``node_id``; idempotent + corpus-cached.

    Mirrors ``research_wiring.run_research_wiring`` / ``package_builders``:
      - a node that already carries its contribution is not re-run (resume-safe);
      - the frozen result is cached keyed to the CORPUS FINGERPRINT under
        ``<run_dir>/g0-enrichment-cache/<fp>.json`` so a graph replay with an
        unchanged corpus reads the cache (determinism) rather than re-invoking the
        pre-pass.

    Writes ``<run_dir>/g0-enrichment.json`` (the frozen result the G0E decision
    card reads) and lands a first-class envelope contribution.
    """
    if node_id not in G0_ENRICHMENT_NODE_IDS:
        return production_envelope
    if (
        production_envelope.get_contribution(G0_ENRICHMENT_SPECIALIST_ID, node_id=node_id)
        is not None
    ):
        return production_envelope

    run_dir = runs_root / str(trial_id)
    run_dir.mkdir(parents=True, exist_ok=True)

    enumerated = _enumerate(corpus_dir)
    model_id = G0_ENRICHMENT_LIVE_MODEL_ID if dispatch_live else G0_ENRICHMENT_MODEL_MARKER
    fingerprint = _fingerprint(enumerated, model_id)
    cache_path = _cache_path(run_dir, fingerprint)

    # R5-A8: collect the F-012 dropped-paraphrase ledger from the live coverage pass so
    # it can be persisted additively into g0-enrichment.json (the G3 marshaller surfaces
    # it ledger-only). A cache HIT does not re-run the pass, so the ledger stays empty
    # there (the live re-prove writes fresh, not via replay).
    non_verbatim_spans: list[Any] = []
    if cache_path.is_file():
        # Corpus-keyed replay: read the frozen, operator-confirmed result.
        result = G0EnrichmentResult.model_validate_json(cache_path.read_text(encoding="utf-8"))
        logger.info("g0-enrichment: cache hit for fingerprint %s", fingerprint[:12])
    else:
        result = build_enrichment_result(
            corpus_dir=corpus_dir,
            dispatch_live=dispatch_live,
            chat_model_factory=chat_model_factory,
            resolve_dispatch=resolve_dispatch,
            non_verbatim_out=non_verbatim_spans,
        )
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        # Cache the FULL shape (audit sidecar included) so a replay rehydrates the
        # exact frozen result; the public card payload excludes the sidecar.
        cache_path.write_text(
            json.dumps(_full_dump(result), sort_keys=True, default=str, indent=2),
            encoding="utf-8",
        )

    artifact_path = run_dir / _DECISION_ARTIFACT_BASENAME
    card_payload = result.to_card_payload()
    if non_verbatim_spans:
        # Additive top-level ledger key (R5-A8) — read by the G3 marshaller's
        # ``_load_non_verbatim_diagnostics``; absent when no live drop occurred so the
        # byte-identical firewall holds for offline / no-drop runs.
        card_payload["non_verbatim_spans"] = [
            span.model_dump(mode="json") if hasattr(span, "model_dump") else span
            for span in non_verbatim_spans
        ]
    artifact_path.write_text(
        json.dumps(card_payload, indent=2, default=str),
        encoding="utf-8",
    )

    updated = production_envelope.model_copy(deep=True)
    updated.add_contribution(
        SpecialistContribution.from_output(
            specialist_id=G0_ENRICHMENT_SPECIALIST_ID,
            output={
                ENRICHMENT_RESULT_KEY: result.to_card_payload(),
                "corpus_fingerprint": fingerprint,
            },
            model_used=G0_ENRICHMENT_MODEL_MARKER
            if not dispatch_live
            else G0_ENRICHMENT_LIVE_MODEL_ID,
            node_id=node_id,
        )
    )
    return updated


def _full_dump(result: G0EnrichmentResult) -> dict[str, Any]:
    """Full shape (audit sidecar included) for the corpus-keyed cache."""
    payload = result.model_dump(mode="json")
    payload["independent_parse"] = result.independent_parse.model_dump(mode="json")
    payload["operator_merge"] = (
        result.operator_merge.model_dump(mode="json") if result.operator_merge is not None else None
    )
    return payload


def load_enrichment_result(run_dir: Path) -> dict[str, Any] | None:
    """Read the frozen public card payload off disk (decision-card builder seam)."""
    artifact = run_dir / _DECISION_ARTIFACT_BASENAME
    if not artifact.is_file():
        return None
    try:
        return json.loads(artifact.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


__all__ = [
    "ENRICHMENT_RESULT_KEY",
    "G0_ENRICHMENT_GATE_CODE",
    "G0_ENRICHMENT_LIVE_MODEL_ID",
    "G0_ENRICHMENT_MODEL_MARKER",
    "G0_ENRICHMENT_NODE_ID",
    "G0_ENRICHMENT_NODE_IDS",
    "G0_ENRICHMENT_SPECIALIST_ID",
    "G0_ENRICHMENT_ACTIVE_ENV",
    "G0_DISPATCH_LIVE_ENV",
    "build_enrichment_result",
    "flag_ungrounded_components",
    "g0_dispatch_live",
    "g0_enrichment_active",
    "load_enrichment_result",
    "run_g0_enrichment",
]
