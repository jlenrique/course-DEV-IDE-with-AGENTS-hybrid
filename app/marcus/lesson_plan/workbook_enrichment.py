"""P5-S1 — project the frozen G0 enriched corpus into workbook producer inputs.

This is the **consumption layer** that closes the P5 loop: it READS the frozen,
operator-confirmed ``G0EnrichmentResult`` card payload (P1 typed_components +
P2 citation_resolutions + P3 pedagogy_annotations + provisional_los) and projects
it into the producer's render inputs so the learner-facing workbook is genuinely
SHAPED BY the enriched corpus rather than by hardcoded constants.

HONESTY BAR (Irene): a field is honestly consumed iff changing it changes the
rendered artifact. This module shapes the deliverable with TWO fields from TWO
passes: the P2 citation ``access_url`` (further-reading link) AND the P3 pedagogy
``bloom`` (exercise + learning-objective level).

RENDER GATE (Texas — most-restrictive-wins AND-conjunction):
    A citation renders an AUTHORITATIVE link IFF
        teachable == True              (P3, from the component's annotation)
      AND resolution_status == "resolved"
      AND resolved_ref["access_url"] is truthy.
    A ``resolved`` citation on a ``teachable == False`` component is a COHERENCE
    BREACH: it is SUPPRESSED and a hard diagnostic is emitted (logger.error —
    never a silent drop). ``failed`` / ``ungrounded`` citations never produce a
    clickable/authoritative URL (they are omitted; never a fabricated bare URL).

P5-RO READ-ONLY INVARIANT: this layer makes ZERO retrieval/network/model calls.
It READS the frozen verdict (the single source of truth) — no scite re-resolve,
no OpenAI. The byte-exact ``access_url`` is used VERBATIM; a DOI is NEVER
re-constructed into ``https://doi.org/{doi}`` here.

Dependency arrow (Winston): this module is lesson_plan-INTERNAL. It imports only
the low-level lesson_plan content models (``collateral_spec`` /
``workbook_producer``); it MUST NOT import ``app.marcus.orchestrator`` or any
``app.*.gates`` module (the specialist act imports THIS, never the reverse). The
trivial on-disk read is replicated here (rather than reusing the orchestrator's
``load_enrichment_result``) precisely to honor import-linter Contract M3
(``app.specialists`` may not import ``app.marcus.orchestrator``).
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.marcus.lesson_plan.collateral_spec import (
    DepthDeltaContract,
    Exercise,
    WorkbookSection,
    WorkbookSpec,
)
from app.marcus.lesson_plan.g0_enrichment import (
    ENRICHMENT_CARD_BASENAME as _SHARED_ENRICHMENT_CARD_BASENAME,
)
from app.marcus.lesson_plan.workbook_producer import (
    FurtherReadingEntry,
    LearningObjectiveBrief,
)

logger = logging.getLogger(__name__)

# The frozen public card payload the G0E decision card reads. SINGLE-SOURCED
# (Winston A2) from ``app.marcus.lesson_plan.g0_enrichment`` — the same basename
# the orchestrator loader uses — re-exported here so existing importers of
# ``workbook_enrichment.ENRICHMENT_CARD_BASENAME`` are unchanged. Sourced from the
# lesson_plan model module (NOT app.marcus.orchestrator) to honor Contract M3.
ENRICHMENT_CARD_BASENAME = _SHARED_ENRICHMENT_CARD_BASENAME

_DEFAULT_BLOOM = "understand"
_TITLE_MAX_CHARS = 160


@dataclass(frozen=True)
class WorkbookEnrichmentProjection:
    """The enriched producer inputs projected from the frozen G0 card payload.

    Drop-in replacements for the slots the enriched corpus covers: the
    ``spec`` (sections + Bloom-leveled exercises), the ``learning_objectives``
    (provisional LO statements + per-LO Bloom from the pedagogy overlay), the
    ``further_reading`` (gated, byte-exact citation links), and the G2
    citation/manifest pair. Segments / source_text / vo_script remain the
    producer's run-dir inputs (the enriched corpus does not displace them).
    """

    spec: WorkbookSpec
    learning_objectives: tuple[LearningObjectiveBrief, ...]
    further_reading: tuple[FurtherReadingEntry, ...]
    answer_keys: dict[str, str]
    citations: tuple[dict[str, str], ...]
    source_ref_manifest: dict[str, str]


# ---------------------------------------------------------------------------
# Loader (trivial on-disk read; READ-ONLY)
# ---------------------------------------------------------------------------


def load_enrichment_card(run_dir: Path) -> dict[str, Any] | None:
    """Read the frozen ``<run_dir>/g0-enrichment.json`` card payload (or None).

    READ-ONLY: returns the public card-payload dict
    (``G0EnrichmentResult.to_card_payload()`` shape) or ``None`` when the run
    carries no enrichment artifact (backward-compatible non-enrichment runs).
    Never raises on a missing/corrupt artifact — absence falls back to the
    constant producer path.
    """
    artifact = run_dir / ENRICHMENT_CARD_BASENAME
    if not artifact.is_file():
        return None
    try:
        decoded = json.loads(artifact.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return decoded if isinstance(decoded, dict) else None


# ---------------------------------------------------------------------------
# The render gate (Deliverable 2) — airtight AND-conjunction
# ---------------------------------------------------------------------------


def citation_renders_authoritative(
    *,
    teachable: bool,
    resolution_status: Any,
    resolved_ref: dict[str, Any] | None,
) -> bool:
    """Texas's 6-condition gate as a most-restrictive-wins AND-conjunction.

    Returns True iff an AUTHORITATIVE (clickable, real) citation link may render:
    ``teachable`` (P3) AND ``resolution_status == "resolved"`` (P2) AND a truthy
    ``resolved_ref["access_url"]``. Any failing conjunct → no authoritative link.
    """
    return bool(
        teachable is True
        and resolution_status == "resolved"
        and (resolved_ref or {}).get("access_url")
    )


def _teachable_for(component_id: str, annotation_by_id: dict[str, dict[str, Any]]) -> bool:
    """The P3 teachable verdict for a component (default True when un-annotated).

    Read VERBATIM from ``pedagogy_annotations`` (P3 already derived it from the
    front-matter resolution_status — NEVER recomputed from citation_resolutions
    here). A component with no annotation (e.g. a reference_citation, which P3
    does not annotate) carries no suppression signal, so it defaults to teachable
    — the citation rides on its resolution verdict + access_url, not on a P3 gate.
    """
    ann = annotation_by_id.get(component_id)
    if ann is None:
        return True
    return ann.get("teachable") is True


# ---------------------------------------------------------------------------
# Projection (Deliverable 1)
# ---------------------------------------------------------------------------


def _as_card_payload(card: Any) -> dict[str, Any]:
    """Accept a card-payload dict OR a parsed G0EnrichmentResult (duck-typed)."""
    if hasattr(card, "to_card_payload"):
        return card.to_card_payload()
    if isinstance(card, dict):
        return card
    raise TypeError(
        "project_enrichment_to_workbook_inputs expects a card-payload dict or a "
        f"G0EnrichmentResult; got {type(card).__name__}"
    )


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _project_further_reading(
    citation_resolutions: list[dict[str, Any]],
    annotation_by_id: dict[str, dict[str, Any]],
) -> tuple[FurtherReadingEntry, ...]:
    """One gated, byte-exact FurtherReadingEntry per AUTHORITATIVE citation.

    Non-authoritative citations (failed / ungrounded / teachable-False) are
    OMITTED (never a fabricated bare URL). A ``resolved`` citation on a
    ``teachable == False`` component is the COHERENCE BREACH: suppressed + a hard
    ``logger.error`` diagnostic (defense-in-depth; never silent).
    """
    entries: list[FurtherReadingEntry] = []
    for cit in citation_resolutions:
        cid = str(cit.get("component_id") or "")
        status = cit.get("resolution_status")
        resolved_ref = cit.get("resolved_ref") or {}
        access_url = resolved_ref.get("access_url")
        ann = annotation_by_id.get(cid)
        teachable = _teachable_for(cid, annotation_by_id)

        # COHERENCE BREACH: a real resolved+linkable citation hung on a component
        # P3 marked NOT teachable. Suppress AND alarm (never silent-drop).
        if (
            status == "resolved"
            and access_url
            and ann is not None
            and ann.get("teachable") is not True
        ):
            logger.error(
                "P5 coherence breach: resolved citation %r (access_url=%r) hangs on "
                "a teachable=False component; suppressing the authoritative link",
                cid,
                access_url,
            )
            continue

        if not citation_renders_authoritative(
            teachable=teachable,
            resolution_status=status,
            resolved_ref=resolved_ref,
        ):
            # failed / ungrounded / non-teachable -> no authoritative URL.
            continue

        title = str(resolved_ref.get("title") or cid)
        entries.append(
            FurtherReadingEntry(
                citation_id=cid,
                title=title,
                source_ref=cid,
                # P5-RO: the frozen access_url VERBATIM; never re-built from doi.
                locator=resolved_ref["access_url"],
                supports_segment_id=None,
            )
        )
    return tuple(entries)


def _lo_bloom_map(annotations: list[dict[str, Any]]) -> dict[str, str]:
    """objective_id -> Bloom (first annotation referencing the LO wins; stable)."""
    out: dict[str, str] = {}
    for ann in annotations:
        bloom = ann.get("bloom")
        if not bloom:
            continue
        for ref in ann.get("lo_refs") or ():
            out.setdefault(str(ref), str(bloom))
    return out


# --- Answer-leak hygiene (wave 39/40 D2.7) -------------------------------
#
# Live run 8b275e5b surfaced quiz excerpts that carry the corpus answer INLINE
# on the prompt line, e.g.::
#
#     - **Prompt:** ...question text... - **Correct Answer:** 25%
#
# ``answer_keys`` (the workbook's Answer Key section) is the DESIGNATED answer
# channel — the projected exercise PROMPT must never leak the answer ahead of
# it. Deterministic string processing only; CONSERVATIVE by design (RATIFIED):
# only a line/segment that unambiguously carries the answer label ("Correct
# Answer" — or the "Answer" synonym in the emphasized / line-anchored-marked
# forms only — followed by an ASCII or fullwidth colon, optionally
# bold/italic/emphasis-wrapped, optionally behind a list marker) AND carries
# real answer text is stripped. Prose that merely mentions the words (e.g.
# "the correct answer depends on ...", no label-colon form) stays put,
# byte-identical. Ambiguity keeps + warns; an answer is NEVER lost silently.

_EMPH = r"(?:\*{1,3}|_{1,3})"
_COLON = r"[:：]"  # ASCII or fullwidth colon
# "**Correct Answer:**" / "**Correct Answer**:" / "**Answer:**" (colon inside
# or outside the emphasis wrapper) — the emphasized label form. The bare
# "Answer" synonym is admitted ONLY here and in the line-anchored marked form.
_ANSWER_LABEL_EMPH = (
    rf"{_EMPH}\s*(?:correct\s+)?answer\s*(?:{_COLON}\s*{_EMPH}|{_EMPH}\s*{_COLON})"
)
# "Correct Answer:" — the bare plain label form (colon mandatory; the "Answer"
# synonym is NEVER admitted bare — too prose-ambiguous).
_ANSWER_LABEL_PLAIN = rf"correct\s+answer\s*{_COLON}"
# "Answer:" / "Correct Answer:" — plain form admitted ONLY behind a
# line-anchored list marker (dash/bullet/number).
_ANSWER_LABEL_MARKED_PLAIN = rf"(?:correct\s+)?answer\s*{_COLON}"
# Line-anchored marker class: dashes, unicode bullets, numbers, blockquote.
# Post-marker whitespace is OPTIONAL (the glued "-**Correct Answer:**" shape).
_LINE_MARKER = r"(?:[-*+–—•‣▪·]\s*|\d+[.)]\s*|>\s*)"
# Mid-line marker class: en/em dashes EXCLUDED — mid-line they read as prose
# punctuation ("Burnout is high — correct answer: varies") and must not strip.
_INLINE_MARKER = r"(?:[-*+]\s*|\d+[.)]\s*|>\s*)"

# A whole line that IS an answer line: the emphasized/plain label at line
# start, or the label behind one-or-more list markers. The un-marked branch is
# tried FIRST (and markers lazily) so emphasis asterisks are parsed as
# emphasis, not consumed as `*` list markers.
_ANSWER_LINE_RE = re.compile(
    rf"^\s*(?:(?:{_ANSWER_LABEL_EMPH}|{_ANSWER_LABEL_PLAIN})"
    rf"|{_LINE_MARKER}+?(?:{_ANSWER_LABEL_EMPH}|{_ANSWER_LABEL_MARKED_PLAIN}))"
    rf"\s*(?P<answer>.*)$",
    re.IGNORECASE,
)
# A trailing inline answer segment (the live 8b275e5b leak shape). Mid-line the
# bar is higher: the label must ride behind a list marker OR be
# emphasis-wrapped — a bare mid-sentence "correct answer:" is ambiguous prose
# and stays put. The segment may be preceded by whitespace OR glued directly
# after sentence punctuation ("What time?**Correct Answer:** 25%").
_ANSWER_INLINE_RE = re.compile(
    rf"(?:\s+|(?<=[?.!,;)]))"
    rf"(?:{_INLINE_MARKER}(?:{_ANSWER_LABEL_EMPH}|{_ANSWER_LABEL_PLAIN})"
    rf"|{_ANSWER_LABEL_EMPH})\s*(?P<answer>.*)$",
    re.IGNORECASE,
)
# A captured "answer" that is only blank markers / underscores / a
# parenthetical hint (e.g. "____ (fill in the blank)") is a fill-in-the-blank
# PROMPT, not a leak — the line is kept.
_BLANK_ANSWER_RE = re.compile(r"^(?:\([^)]*\)|[\s_\-–—.…*])*$")
# An emphasized label-shaped token ("**Prompt:**", "**…**:") INSIDE a captured
# answer signals answer-first ordering — stripping would destroy the question.
_EMPH_LABEL_TOKEN_RE = re.compile(
    rf"{_EMPH}\s*[^\s*_][^*_\n]*?(?:{_COLON}\s*{_EMPH}|{_EMPH}\s*{_COLON})",
    re.IGNORECASE,
)
# A captured answer longer than this smells like a truncated prompt (a mid-line
# label MENTION swallowing the rest of the question) — ambiguous; keep + warn.
_AMBIGUOUS_ANSWER_MAX_CHARS = 120

# Kept as prompt text when everything else is empty (P2 last-resort fallback).
_PROMPT_UNAVAILABLE = "(exercise prompt unavailable)"


def _strip_answer_leak(prompt: str) -> tuple[str, str | None]:
    """Strip unambiguously-labeled answer lines/segments from an exercise prompt.

    Returns ``(clean_prompt, leaked_answer)``.

    NO-MATCH PATH: the prompt is returned BYTE-IDENTICAL (the original object)
    and ``leaked_answer`` is ``None``. MATCH PATH: the surviving prompt is
    newline-NORMALIZED (``splitlines`` → LF rejoin → outer ``strip``) — byte
    identity is promised ONLY when nothing matched. Multiple stripped answers
    join with ``"; "`` (never embedded newlines).

    Stripped shapes (the closed set): the "Correct Answer"/"Answer" label with
    a mandatory (ASCII or fullwidth) colon, emphasis-wrapped anywhere, plain
    behind a line-anchored list marker, or plain-``correct answer:`` bare at
    line start / behind an inline dash marker. A label line whose answer group
    is empty consumes the FOLLOWING non-empty line as the answer (both
    removed).

    ACCEPTED-KEPT shapes (deliberately conservative): bare mid-prose
    ``correct answer:`` mentions; the bare un-marked ``Answer:`` synonym;
    labels outside the closed set (e.g. ``Solution:``); labels whose captured
    answer is only blank markers (fill-in-the-blank prompts); and AMBIGUOUS
    matches — a strip that would empty the prompt while the captured answer
    carries another emphasized label token (answer-first ordering), or a
    captured answer over ~120 chars — which are kept UNTOUCHED with a
    ``logger.warning``. An answer is never lost silently.
    """
    lines = prompt.splitlines()
    # Plan pass: classify each line before mutating anything, so the P3
    # ambiguity guard can veto a strip and restore the original lines.
    entries: list[dict[str, Any]] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        full = _ANSWER_LINE_RE.match(line)
        if full is not None:
            answer = full.group("answer").strip()
            if answer and not _BLANK_ANSWER_RE.match(answer):
                entries.append({"kind": "strip", "lines": [line], "answer": answer})
                i += 1
                continue
            if not answer:
                # Wrapped answer: the label line carries no answer text; the
                # answer rides on the FOLLOWING non-empty line. Consume both
                # (plus intervening blanks). A trailing label with nothing
                # after it stays untouched (never orphan an answer elsewhere).
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j < len(lines):
                    wrapped = lines[j].strip()
                    if (
                        _ANSWER_LINE_RE.match(lines[j]) is None
                        and not _BLANK_ANSWER_RE.match(wrapped)
                    ):
                        entries.append(
                            {
                                "kind": "strip",
                                "lines": lines[i : j + 1],
                                "answer": wrapped,
                            }
                        )
                        i = j + 1
                        continue
            # Label with a blank-marker answer (fill-in-the-blank prompt) or
            # an empty answer and no consumable follow-on line: keep as-is.
            entries.append({"kind": "keep", "lines": [line]})
            i += 1
            continue
        inline = _ANSWER_INLINE_RE.search(line)
        if inline is not None:
            answer = inline.group("answer").strip()
            if answer and not _BLANK_ANSWER_RE.match(answer):
                entries.append(
                    {
                        "kind": "inline",
                        "lines": [line],
                        "answer": answer,
                        "remainder": line[: inline.start()].rstrip(),
                    }
                )
                i += 1
                continue
        entries.append({"kind": "keep", "lines": [line]})
        i += 1

    def _rendered() -> str:
        out: list[str] = []
        for entry in entries:
            if entry["kind"] == "keep":
                out.extend(entry["lines"])
            elif entry["kind"] == "inline" and entry["remainder"]:
                out.append(entry["remainder"])
        return "\n".join(out).strip()

    def _revert(entry: dict[str, Any]) -> None:
        logger.warning(
            "answer-label detected but kept — ambiguous shape (conservative "
            "posture: never lose an answer silently): %r",
            entry["answer"][:160],
        )
        entry["kind"] = "keep"

    # P3 guard (a): an over-long capture smells like a truncated prompt.
    for entry in entries:
        if (
            entry["kind"] in ("strip", "inline")
            and len(entry["answer"]) > _AMBIGUOUS_ANSWER_MAX_CHARS
        ):
            _revert(entry)
    # P3 guard (b): a strip that EMPTIES the prompt while the captured answer
    # still carries another emphasized label token is answer-first ordering
    # ("- **Correct Answer:** 25% - **Prompt:** Q?") — keep, never destroy the
    # question. An empty-prompt strip whose answer is CLEAN still strips (the
    # caller's fallback chain supplies the prompt).
    if not _rendered():
        for entry in entries:
            if entry["kind"] in ("strip", "inline") and _EMPH_LABEL_TOKEN_RE.search(
                entry["answer"]
            ):
                _revert(entry)

    answers = [e["answer"] for e in entries if e["kind"] in ("strip", "inline")]
    if not answers:
        return prompt, None
    return _rendered(), "; ".join(answers)


def _route_answer_key(answer_keys: dict[str, str], exercise_id: str, worked: str) -> bool:
    """Route a worked answer into the ``answer_keys`` channel — NEVER overwrite.

    An existing NON-EMPTY key for ``exercise_id`` always wins; the routed text
    lands when the slot is absent OR holds only an empty string (the D2.7
    no-overwrite contract, truthiness-gated). Returns ``True`` iff the routed
    text landed.
    """
    if answer_keys.get(exercise_id):
        return False
    answer_keys[exercise_id] = worked
    return True


def _project_exercises(
    typed_components: list[dict[str, Any]],
    annotation_by_id: dict[str, dict[str, Any]],
    surfaced_ids: list[str],
) -> tuple[dict[str, list[Exercise]], dict[str, str]]:
    """Quiz components x their pedagogy annotation -> Bloom-leveled exercises.

    Each ``quiz`` typed-component with a pedagogy annotation becomes one
    :class:`Exercise` whose ``bloom_level`` is the annotation's Bloom and whose
    answer-key reference is the annotation's ``assessment_link`` (the assessed
    target) falling back to the first served LO. Render gate: a ``teachable ==
    False`` quiz is SUPPRESSED (no exercise). Returns (exercises grouped by the
    home-section objective_id, answer_keys).
    """
    surfaced = set(surfaced_ids)
    by_section: dict[str, list[Exercise]] = defaultdict(list)
    answer_keys: dict[str, str] = {}
    for comp in typed_components:
        if comp.get("source_type") != "quiz":
            continue
        cid = str(comp.get("component_id") or "")
        ann = annotation_by_id.get(cid)
        if ann is None:
            continue  # no pedagogy overlay -> no Bloom to consume; skip
        if ann.get("teachable") is not True:
            continue  # render gate: suppress a non-teachable exercise
        lo_refs = [str(r) for r in (ann.get("lo_refs") or ())]
        assessed = ann.get("assessment_link")
        answer_ref = str(assessed) if assessed else (lo_refs[0] if lo_refs else cid)
        # D2.7: the prompt must not leak the corpus answer — strip the labeled
        # answer segment and route it to the answer_keys channel instead.
        prompt, leaked_answer = _strip_answer_leak(
            str(comp.get("excerpt") or comp.get("label") or cid)
        )
        leaks: list[str] = [leaked_answer] if leaked_answer else []
        if not prompt:
            # The excerpt was ONLY an answer line -> fall back. The label is
            # RE-STRIPPED through the same hygiene (a label like
            # "Correct Answer: 25%" must not re-leak verbatim), then cid, then
            # the honest literal when even cid is empty.
            label_prompt, label_leak = _strip_answer_leak(str(comp.get("label") or ""))
            if label_leak and label_leak not in leaks:
                leaks.append(label_leak)
            prompt = label_prompt or cid or _PROMPT_UNAVAILABLE
        exercise = Exercise(
            exercise_id=cid,
            bloom_level=ann["bloom"],  # type: ignore[arg-type]
            prompt_intent=prompt,
            answer_key_source_ref=answer_ref,
            # D2 MERGE (39.1b): overlay-projected exercises are course-check
            # instruments — provenance is a field, never a list position.
            origin="enrichment",
        )
        # Home section: the first served LO that is surfaced, else the first LO.
        home = next((r for r in lo_refs if r in surfaced), None) or (
            surfaced_ids[0] if surfaced_ids else cid
        )
        by_section[home].append(exercise)
        # The Answer Key channel: the source-provided answer (when the prompt
        # leaked one) takes the slot iff it is still empty; otherwise the
        # source_ref grounding note. Never overwrite an existing key; never
        # lose the stripped answer. Multiple stripped answers join with "; "
        # and the grounding suffix appends ONCE at the end.
        if leaks:
            routed = _route_answer_key(
                answer_keys,
                cid,
                f"{'; '.join(leaks)} (source-provided correct answer; "
                f"grounded by source_ref `{answer_ref}`).",
            )
            if not routed:
                logger.warning(
                    "answer-leak routing: stripped answer for exercise %r could "
                    "not be routed — the answer-key slot is already claimed "
                    "(duplicate component_id?)",
                    cid,
                )
            if home not in surfaced:
                logger.warning(
                    "answer-leak routing: exercise %r routes its stripped answer "
                    "to home section %r, which is not in the surfaced LO set — "
                    "the answer lands in an unrendered section",
                    cid,
                    home,
                )
        _route_answer_key(
            answer_keys,
            cid,
            f"Worked answer is grounded by source_ref `{answer_ref}` "
            "(P3-linked assessment target).",
        )
    return dict(by_section), answer_keys


def project_enrichment_to_workbook_inputs(card: Any) -> WorkbookEnrichmentProjection:
    """Project the frozen G0 enriched card payload into workbook producer inputs.

    Maps:
      * P2 ``citation_resolutions`` -> gated, byte-exact ``further_reading``;
      * ``quiz`` ``typed_components`` x P3 ``pedagogy_annotations`` -> Bloom-leveled
        ``Exercise`` objects (suppressed when not teachable);
      * ``provisional_los`` + P3 ``lo_refs``/``bloom`` -> ``LearningObjectiveBrief``
        + one bound :class:`WorkbookSection` per LO (carrying its exercises).

    Pure + offline + deterministic (READ-ONLY over the frozen verdict).
    """
    payload = _as_card_payload(card)
    typed_components = list(payload.get("typed_components") or [])
    provisional_los = list(payload.get("provisional_los") or [])
    citation_resolutions = list(payload.get("citation_resolutions") or [])
    annotations = list(payload.get("pedagogy_annotations") or [])
    annotation_by_id = {
        str(a.get("component_id")): a for a in annotations if a.get("component_id")
    }

    # --- Learning objectives (statement from P0/P1; Bloom from the P3 overlay) ---
    bloom_map = _lo_bloom_map(annotations)
    surfaced_ids = [str(lo.get("objective_id")) for lo in provisional_los if lo.get("objective_id")]
    lo_briefs = tuple(
        LearningObjectiveBrief(
            objective_id=str(lo["objective_id"]),
            bloom_level=bloom_map.get(str(lo["objective_id"]), _DEFAULT_BLOOM),
            statement=str(lo.get("statement") or ""),
        )
        for lo in provisional_los
        if lo.get("objective_id")
    )

    # --- Exercises (quiz components x P3 annotation), grouped by home section ---
    exercises_by_section, answer_keys = _project_exercises(
        typed_components, annotation_by_id, surfaced_ids
    )

    # --- Sections: one per surfaced LO (bound 1:1 so S1 binding is exact) ---
    sections: list[WorkbookSection] = []
    for lo in provisional_los:
        oid = lo.get("objective_id")
        if not oid:
            continue
        oid = str(oid)
        statement = str(lo.get("statement") or oid)
        sections.append(
            WorkbookSection(
                section_id=f"sec-{oid}",
                learning_objective_id=oid,
                title=statement[:_TITLE_MAX_CHARS] or oid,
                depth_delta=DepthDeltaContract(
                    deferred_from_slide=oid,
                    deferred_depth=(
                        f"Workbook-deferred depth for {oid}: {statement} "
                        "(read-channel companion to the glance deck)."
                    ),
                ),
                exercises=exercises_by_section.get(oid, []),
                narrative_intent=statement,
            )
        )
    spec = WorkbookSpec(sections=sections)

    # --- Further reading (gated, byte-exact) + the G2 manifest/citation pair ---
    further_reading = _project_further_reading(citation_resolutions, annotation_by_id)
    source_ref_manifest = {e.source_ref: _hash(e.title) for e in further_reading}
    citations = tuple({"source_ref": e.source_ref} for e in further_reading)

    return WorkbookEnrichmentProjection(
        spec=spec,
        learning_objectives=lo_briefs,
        further_reading=further_reading,
        answer_keys=answer_keys,
        citations=citations,
        source_ref_manifest=source_ref_manifest,
    )


# ---------------------------------------------------------------------------
# S7 canonical-arc — pure run.json disk-readers (the ENVELOPE->PRODUCER seam)
# ---------------------------------------------------------------------------
#
# The workbook producer (``app.specialists.workbook_producer``) must CONSUME
# Irene's authored ``lesson_plan["collateral"]`` AND the S6 ``research_entries``,
# both of which live only in the persisted ProductionEnvelope (``run.json``).
# Contract M3 forbids ``app.specialists`` importing ``app.marcus.orchestrator``,
# so the producer may NOT call ``research_entries_from_envelope``. These pure
# disk-readers live here instead (an M3-allowed import for the producer, mirroring
# ``load_enrichment_card``): they deserialize ``run.json`` via the ``app.models.*``
# model classes (NOT the orchestrator) and use LOCAL literal seam constants.

# LOCAL literal seam constants (deliberately NOT imported from
# app.marcus.orchestrator.research_wiring — that is the M3-forbidden edge).
_IRENE_PASS1_SPECIALIST_ID = "irene_pass1"
_RESEARCH_WIRING_SPECIALIST_ID = "research_wiring"
_RESEARCH_WIRING_NODE_ID = "04.55"
_RESEARCH_ENTRIES_KEY = "research_entries"
_RUN_ENVELOPE_BASENAME = "run.json"


class RunEnvelopeCorruptError(ValueError):
    """Raised when ``run.json`` exists but cannot be deserialized honestly.

    Distinct from genuine absence (``None``): corrupt envelopes must not
    silently collapse into absent-collateral no-ops (Mine-next N6 /
    ``run-envelope-corrupt-vs-absent-fail-loud``).
    """


def load_run_envelope(run_dir: Path) -> Any | None:
    """Disk-read ``<run_dir>/run.json`` -> ``ProductionEnvelope`` (or ``None``).

    READ-ONLY. Deserializes the persisted trial envelope via the ``app.models.*``
    model classes (M3-safe: the MODEL, never the orchestrator).

    - Missing file → ``None`` (genuine absence; producer may skip).
    - Symlinked ``run.json`` → :class:`RunEnvelopeCorruptError` (38-2 T4 R9 /
      B5: the sole-writer envelope coordinate must be a regular file —
      additive containment guard mirroring every other Ask-B disk guard).
    - Present but unreadable / invalid JSON / ValidationError →
      :class:`RunEnvelopeCorruptError` (fail-loud; never silent no-op).
    """
    artifact = run_dir / _RUN_ENVELOPE_BASENAME
    if artifact.is_symlink():
        raise RunEnvelopeCorruptError(
            f"run.json coordinate is a symlink at {artifact}"
        )
    if not artifact.is_file():
        return None
    # Function-local import keeps the module import-graph thin and the M3 edge
    # unambiguous (the model, not app.marcus.orchestrator).
    from pydantic import ValidationError  # noqa: PLC0415

    from app.models.runtime.production_trial_envelope import (  # noqa: PLC0415
        ProductionTrialEnvelope,
    )

    try:
        raw = artifact.read_text(encoding="utf-8")
    except OSError as exc:
        raise RunEnvelopeCorruptError(
            f"run.json unreadable at {artifact}: {exc}"
        ) from exc
    try:
        trial = ProductionTrialEnvelope.model_validate_json(raw)
    except (ValidationError, ValueError) as exc:
        raise RunEnvelopeCorruptError(
            f"run.json corrupt at {artifact}: {exc}"
        ) from exc
    return trial.production_envelope


def lesson_plan_from_run(run_dir: Path) -> dict[str, Any] | None:
    """Read Irene's authored ``lesson_plan`` dict off ``run.json`` (or ``None``)."""
    envelope = load_run_envelope(run_dir)
    if envelope is None:
        return None
    contribution = envelope.latest_for_specialist(_IRENE_PASS1_SPECIALIST_ID)
    if contribution is None:
        return None
    lesson_plan = contribution.output.get("lesson_plan")
    return lesson_plan if isinstance(lesson_plan, dict) else None


def collateral_from_run(run_dir: Path) -> dict[str, Any] | None:
    """Read ``lesson_plan["collateral"]`` off ``run.json`` (the S7 blueprint)."""
    lesson_plan = lesson_plan_from_run(run_dir)
    if not isinstance(lesson_plan, dict):
        return None
    collateral = lesson_plan.get("collateral")
    return collateral if isinstance(collateral, dict) else None


def research_entries_from_run(run_dir: Path) -> list[dict[str, Any]]:
    """Read the S6 cited ``research_entries`` off ``run.json`` (node ``04.55``)."""
    envelope = load_run_envelope(run_dir)
    if envelope is None:
        return []
    contribution = envelope.get_contribution(
        _RESEARCH_WIRING_SPECIALIST_ID, node_id=_RESEARCH_WIRING_NODE_ID
    )
    if contribution is None:
        return []
    entries = contribution.output.get(_RESEARCH_ENTRIES_KEY)
    return list(entries) if isinstance(entries, list) else []


# ---------------------------------------------------------------------------
# Q2 — corpus-native references (references/*.md + per-slide References lines)
# ---------------------------------------------------------------------------
#
# The enrichment further-reading channel yields () when the run's
# ``citation_resolutions`` are empty, but a references-bearing corpus still
# carries real references: standalone ``references/*.md`` files (title + URL) and
# per-slide ``**References:**`` lines (name-only). Read them so the S6 References
# channel is populated from corpus-native data instead of rendering empty. No
# fabricated URLs — a name-only reference renders WITHOUT a locator.

_URL_RE = re.compile(r"https?://[^\s)\]]+")
_SLIDE_REF_RE = re.compile(r"\*\*References:\*\*\s*(.+)")
_EVIDENCE_TAG_RE = re.compile(r"\[evidence:[^\]]*\]")
_HEADING_RE = re.compile(r"^\s*#+\s*(.+?)\s*#*\s*$")
_REF_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _first_heading(text: str) -> str | None:
    for line in text.splitlines():
        match = _HEADING_RE.match(line)
        if match:
            return match.group(1).replace("*", "").strip()
    return None


def _ref_slug(text: str) -> str:
    return _REF_SLUG_RE.sub("-", text.lower()).strip("-")[:64] or "ref"


def corpus_root_from_run(run_dir: Path) -> Path | None:
    """Read the trial ``corpus_path`` off ``run.json`` -> an existing course root.

    READ-ONLY. Returns ``None`` when the envelope is absent/corrupt or the
    recorded corpus path does not exist on disk (backward-compatible: a fixture
    run whose corpus root is absent simply projects no corpus-native references).
    """
    artifact = run_dir / _RUN_ENVELOPE_BASENAME
    if not artifact.is_file():
        return None
    from pydantic import ValidationError  # noqa: PLC0415

    from app.models.runtime.production_trial_envelope import (  # noqa: PLC0415
        ProductionTrialEnvelope,
    )

    try:
        trial = ProductionTrialEnvelope.model_validate_json(
            artifact.read_text(encoding="utf-8")
        )
    except (ValidationError, ValueError, OSError):
        return None
    corpus_path = getattr(trial, "corpus_path", None)
    if not corpus_path:
        return None
    root = Path(str(corpus_path))
    return root if root.is_dir() else None


def corpus_native_further_reading(corpus_root: Path) -> tuple[FurtherReadingEntry, ...]:
    """Project corpus-native references into further-reading entries (Q2).

    Two tiers, both READ-ONLY over the corpus source files:
      (a) ``references/*.md`` standalone reference files -> H1 title + first URL
          locator (the URL-bearing corpus references);
      (b) per-slide ``**References:**`` lines under ``slides/*.md`` -> one
          name-only entry per ``;``-separated citation (no fabricated URL).

    De-duplicated by a stable slug; ``[evidence: src-NNN]`` tags are stripped from
    the rendered name.
    """
    entries: list[FurtherReadingEntry] = []
    seen: set[str] = set()

    refs_dir = corpus_root / "references"
    if refs_dir.is_dir():
        for md in sorted(refs_dir.glob("*.md")):
            try:
                text = md.read_text(encoding="utf-8")
            except OSError:
                continue
            title = _first_heading(text) or md.stem.replace("-", " ")
            url_match = _URL_RE.search(text)
            cid = f"corpus-ref-{md.stem}"
            if cid in seen:
                continue
            seen.add(cid)
            entries.append(
                FurtherReadingEntry(
                    citation_id=cid,
                    title=title,
                    source_ref=cid,
                    locator=url_match.group(0) if url_match else None,
                )
            )

    slides_dir = corpus_root / "slides"
    if slides_dir.is_dir():
        for md in sorted(slides_dir.glob("*.md")):
            try:
                text = md.read_text(encoding="utf-8")
            except OSError:
                continue
            for match in _SLIDE_REF_RE.finditer(text):
                raw = _EVIDENCE_TAG_RE.sub("", match.group(1))
                for name in (segment.strip(" .*") for segment in raw.split(";")):
                    if not name:
                        continue
                    cid = f"corpus-ref-{_ref_slug(name)}"
                    if cid in seen:
                        continue
                    seen.add(cid)
                    entries.append(
                        FurtherReadingEntry(
                            citation_id=cid,
                            title=name,
                            source_ref=cid,
                            locator=None,
                        )
                    )
    return tuple(entries)


__all__ = [
    "ENRICHMENT_CARD_BASENAME",
    "RunEnvelopeCorruptError",
    "WorkbookEnrichmentProjection",
    "citation_renders_authoritative",
    "collateral_from_run",
    "corpus_native_further_reading",
    "corpus_root_from_run",
    "lesson_plan_from_run",
    "load_enrichment_card",
    "load_run_envelope",
    "project_enrichment_to_workbook_inputs",
    "research_entries_from_run",
]
