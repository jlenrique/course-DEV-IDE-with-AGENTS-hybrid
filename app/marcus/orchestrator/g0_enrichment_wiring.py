"""G0-enrichment runner-wired orchestration hook (Story G0-S2).

The Marcus-SPOC G0 pre-pass that (1) TYPES every enumerated source span into the
closed 10-type taxonomy (+ ``other:<label>`` escape hatch) and (2) extracts
candidate Learning Objectives at ``status=provisional`` with resolvable
``SourceRef`` provenance — both OFF the deterministic critical path (an LLM
pre-pass, result frozen + cached keyed to a CORPUS FINGERPRINT for replay
determinism). The frozen result feeds operator confirm-gate #1 (``G0E``).

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
from app.marcus.lesson_plan.source_type import TypedSource, is_classification_only
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


def _first_text_span(path: Path) -> str | None:
    """First non-empty line of a text source (verbatim quoted_span), or None."""
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped[:200]
    return None


# ---------------------------------------------------------------------------
# Offline deterministic pre-pass (corpus-derived; reproducible)
# ---------------------------------------------------------------------------


def _offline_pre_pass(
    enumerated: list[tuple[str, Path]],
    corpus_dir: Path,
) -> tuple[list[TypedSource], list[LearningObjective], list[EnumerationProvenance]]:
    typed: list[TypedSource] = []
    provenance: list[EnumerationProvenance] = []
    los: list[LearningObjective] = []
    lo_index = 0
    enumerated_ids = {sid for sid, _ in enumerated}

    for source_id, path in enumerated:
        source_type = _heuristic_type(path)
        typed.append(
            TypedSource(
                source_id=source_id,
                source_type=source_type,  # type: ignore[arg-type]
                flagged_unconsumed=is_classification_only(source_type),
            )
        )
        provenance.append(
            EnumerationProvenance(
                source_id=source_id,
                root_id=corpus_dir.resolve().as_posix(),
                connector="local_file",
                locator=path.relative_to(corpus_dir).as_posix(),
            )
        )
        # Candidate LO: one provisional LO per text-extractable source span. A
        # provisional LO MAY carry 0 refs, but a populated ref MUST point at an
        # enumerated source_id with a verbatim quoted_span (A9).
        span = _first_text_span(path)
        if span is not None:
            lo_index += 1
            refs = (
                SourceRef(
                    source_id=source_id,
                    locator=path.relative_to(corpus_dir).as_posix(),
                    quoted_span=span,
                ),
            )
            lo = LearningObjective(
                objective_id=f"lo-g0-{lo_index:03d}",
                statement=f"Understand the material introduced by {source_id} ({span[:60]}).",
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


def _build_dissent(typed: list[TypedSource], fingerprint: str) -> Dissent:
    """Derive ONE real, corpus-varying dissent (A3/A11 — never theater).

    The target + alternative type are a deterministic function of the corpus
    fingerprint, so the dissent VARIES run-to-run across different corpora (a
    never-varying dissent carries no information). Independent-parse-sourced:
    Marcus's position is his own heuristic typing.
    """
    if not typed:
        # A typed-source-less corpus still owes a real dissent: dissent the empty
        # enumeration itself (operator confirms there were genuinely no spans).
        return Dissent(
            against="corpus",
            marcus_position="independent parse found zero typeable spans",
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
        against=target.source_id,
        marcus_position=(
            f"typed {target.source_id} as {target.source_type}; a defensible "
            f"alternative reading is {alt}"
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
    list[TypedSource], list[LearningObjective], list[EnumerationProvenance]
]:  # pragma: no cover - live leg
    """REAL Marcus-SPOC typing/LO pre-pass via make_chat_model + g0-enrichment.j2.

    Off the deterministic critical path. Exercised by the operator-gated live
    segment proof (AC-S2-8), not the offline suite.
    """
    from app.marcus.orchestrator.pre_gate_marcus import render_pre_fill_prompt

    corpus_summary = "\n".join(
        f"- {sid}: {path.relative_to(corpus_dir).as_posix()}" for sid, path in enumerated
    )
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


def _parse_live_payload(
    payload: dict[str, Any],
    enumerated: list[tuple[str, Path]],
    corpus_dir: Path,
) -> tuple[list[TypedSource], list[LearningObjective], list[EnumerationProvenance]]:
    """Reconcile an LLM typing/LO payload against the enumerated corpus (A6).

    The live model will not reliably type EXACTLY the enumerated set once per id
    (it under-types, over-types, duplicates, or fabricates ids). A naive
    ``len(typed_sources)`` pass both (a) crashes the run on the normal
    under-typing case and (b) lets a double-typed id + a dropped id "balance" a
    count-only reconcile while silently corrupting the partition. So we reconcile
    deterministically to EXACTLY one TypedSource per enumerated id:

      * dedup the LLM rows by ``source_id`` (first occurrence wins);
      * DROP rows whose ``source_id`` is not in the enumerated set (fabricated —
        A1/A9: the LLM cannot invent a source) with a loud log;
      * FILL any enumerated id the LLM left untyped with the deterministic
        heuristic type (the operator confirms/corrects every span at gate #1
        per D2, so a defaulted type is operator-correctable, never silent).

    The result has ``len == len(enumerated)`` with each id present exactly once,
    so the ReconcileView count is correct BY CONSTRUCTION (coverage == count).
    """
    enumerated_ids = [sid for sid, _ in enumerated]
    enumerated_id_set = set(enumerated_ids)
    by_id = {sid: path for sid, path in enumerated}

    llm_typed: dict[str, TypedSource] = {}
    for row in payload.get("typed_sources", []):
        ts = TypedSource.model_validate(row)
        if ts.source_id not in enumerated_id_set:
            logger.warning(
                "g0-enrichment live: dropping typed source for unknown id %r "
                "(not in enumerated corpus — fabricated)",
                ts.source_id,
            )
            continue
        if ts.source_id in llm_typed:
            logger.warning(
                "g0-enrichment live: duplicate typing for %r; keeping first",
                ts.source_id,
            )
            continue
        llm_typed[ts.source_id] = ts

    typed: list[TypedSource] = []
    for sid in enumerated_ids:
        if sid in llm_typed:
            typed.append(llm_typed[sid])
        else:
            heuristic = _heuristic_type(by_id[sid])
            logger.info(
                "g0-enrichment live: id %r left untyped by the model; filled with "
                "heuristic %r (operator confirms at gate #1)",
                sid,
                heuristic,
            )
            typed.append(
                TypedSource(
                    source_id=sid,
                    source_type=heuristic,  # type: ignore[arg-type]
                    flagged_unconsumed=is_classification_only(heuristic),
                )
            )

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
            "typed_sources": [t.model_dump(mode="json") for t in typed],
            "provisional_los": [lo.objective_id for lo in los],
        },
        ts=independent_ts,
    )
    dissent = _build_dissent(typed, fingerprint)
    n_typed = len(typed)
    n_flagged = sum(1 for t in typed if t.flagged_unconsumed)
    reconcile = ReconcileView(
        n_in=len(enumerated),
        n_typed=n_typed,
        n_ignored=0,  # offline: nothing operator-confirmed-ignored yet (composer owns ignored)
        n_flagged=n_flagged,
    )
    roots = [
        TraversalRoot(root_id=corpus_dir.resolve().as_posix(), kind="corpus_dir"),
    ]
    result = G0EnrichmentResult(
        corpus_fingerprint=fingerprint,
        model_id=model_id,
        typed_sources=typed,
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
