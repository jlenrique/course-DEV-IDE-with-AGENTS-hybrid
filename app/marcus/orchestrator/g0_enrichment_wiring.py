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
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from app.composers.section_02a.composer import _walk_corpus_files
from app.marcus.lesson_plan.g0_enrichment import (
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
from app.marcus.lesson_plan.source_type import TypedComponent
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


_DECISION_ARTIFACT_BASENAME = "g0-enrichment.json"
_CACHE_DIRNAME = "g0-enrichment-cache"

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
    return corpus_fingerprint(hashes, model_id)


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
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
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
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
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
# Live LLM pre-pass (exercised by AC-S2-8; reuses the pre_gate_marcus seam)
# ---------------------------------------------------------------------------


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
        from app.models.adapter import make_chat_model

        chat_model_factory = make_chat_model
    handle = chat_model_factory("marcus")
    response = handle.chat.invoke([{"role": "user", "content": prompt}])
    payload = json.loads(response.content)
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

    rows = (
        payload.get("components")
        or payload.get("typed_components")
        or payload.get("typed_sources")
        or []
    )
    per_parent: dict[str, list[dict[str, Any]]] = {sid: [] for sid in enumerated_ids}
    for row in rows:
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
    los: list[LearningObjective] = []
    for row in payload.get("provisional_los", []):
        lo = LearningObjective.model_validate({**row, "status": "provisional"})
        lo = advance_lo(lo, "provisional", actor="g0")
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
) -> G0EnrichmentResult:
    """Run the pre-pass (offline OR live) and assemble the frozen result.

    Pure of run-dir/cache side effects (those live in ``run_g0_enrichment``) so
    the assembly is unit-testable in isolation.
    """
    enumerated = _enumerate(corpus_dir)
    model_id = G0_ENRICHMENT_LIVE_MODEL_ID if dispatch_live else G0_ENRICHMENT_MODEL_MARKER
    fingerprint = _fingerprint(enumerated, model_id)

    independent_ts = datetime.now(UTC)
    if dispatch_live:
        typed, los, provenance = _live_pre_pass(enumerated, corpus_dir, chat_model_factory)
    else:
        typed, los, provenance = _offline_pre_pass(enumerated, corpus_dir)

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
        independent_parse=independent_parse,
    )
    assert_run_dissent_invariant(result)
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

    if cache_path.is_file():
        # Corpus-keyed replay: read the frozen, operator-confirmed result.
        result = G0EnrichmentResult.model_validate_json(cache_path.read_text(encoding="utf-8"))
        logger.info("g0-enrichment: cache hit for fingerprint %s", fingerprint[:12])
    else:
        result = build_enrichment_result(
            corpus_dir=corpus_dir,
            dispatch_live=dispatch_live,
            chat_model_factory=chat_model_factory,
        )
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        # Cache the FULL shape (audit sidecar included) so a replay rehydrates the
        # exact frozen result; the public card payload excludes the sidecar.
        cache_path.write_text(
            json.dumps(_full_dump(result), sort_keys=True, default=str, indent=2),
            encoding="utf-8",
        )

    artifact_path = run_dir / _DECISION_ARTIFACT_BASENAME
    artifact_path.write_text(
        json.dumps(result.to_card_payload(), indent=2, default=str),
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
    "g0_dispatch_live",
    "g0_enrichment_active",
    "load_enrichment_result",
    "run_g0_enrichment",
]
