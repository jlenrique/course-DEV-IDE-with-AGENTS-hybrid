"""Operator-facing HIL surface projector — Story 42.1 (finding C: tabular HIL).

Renders operator-facing human-in-the-loop review surfaces as markdown TABLES per
the worked exemplars in
``_bmad-output/implementation-artifacts/evidence/operator-hil-display-requirements-2026-07-16.md``
§1 (gate identity, enrichment summary metrics, one-row-per-flag ungrounded
advisories, one-row-per-LO learning objectives).

The bc747b51 trial exposed the anti-pattern: after G0 confirm, enrichment printed
a sheaf of ``... excerpt is NOT grounded ...`` log lines with no table, then
``trial start`` emitted a single dense JSON blob and returned to the shell — an
unreviewable surface. This projector re-shapes that same material into tables so
the operator can actually read and decide.

Pagination follows the Marcus HIL Display Standards
(``skills/bmad-agent-marcus/references/conversation-mgmt.md`` §HIL Display
Standards): "for displays exceeding roughly 15 rows ... present the first page and
offer ``show next`` on demand". Numbered rows carry a unique sequential index as
the first column.

Contract fences (Story 42.1 Scope Fences):

* **Display-layer only.** The machine JSON on disk (``g0-enrichment.json`` /
  ``decision-card-*.json`` / ``operator-surface.json``) stays dense and is never
  mutated — this module only READS dicts and returns strings.
* **Pure / stdlib-only.** No side effects; the CLI printer (``emit_gate_surface``)
  is the only IO seam and it merely writes the rendered string to a stream.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import IO, Any

#: Marcus HIL Display Standards pagination threshold (rows).
PAGE_SIZE: int = 15

#: Bound (chars) for a summarized nested value in the generic renderer — mirrors
#: ``operator_surface_assembler._CONTEXT_ENTRY_MAX_CHARS`` (240) per Epic 43 rider
#: R2, so a fat nested value can never dump raw JSON into the operator surface.
_NESTED_VALUE_MAX_CHARS: int = 240

#: Fixed display width (chars) for the value column of the generic key/value table
#: (rider R5 — width-aware / fixed-width columns, no ugly wrap at 80 cols).
_GENERIC_VALUE_WIDTH: int = 60

#: Fixed display widths (chars) for the two long free-text columns of the G0
#: directive source-inventory table (Story 43-1, rider R5 — width-aware columns,
#: no ugly wrap at 80 cols). ``locator`` and the brief ``description`` are the
#: only unbounded columns; ref_id / role / min-words / excluded are naturally
#: short. Both are hard-capped via :func:`_truncate_cell`.
_DIRECTIVE_LOCATOR_WIDTH: int = 44
_DIRECTIVE_DESC_WIDTH: int = 44

#: Role ordering for the directive table's primary-first sort (Story 43-1, AC-1).
#: Unknown / excluded-only roles sort last; ties break lexically by ``ref_id``.
_DIRECTIVE_ROLE_RANK: dict[str, int] = {"primary": 0, "supporting": 1}

#: Fixed display width (chars) for the free-text ``Description`` column of the G2B
#: per-slide-mode table (Story 43-3, rider R5 — width-aware columns).
_MODE_DESC_WIDTH: int = 56

#: Fixed display widths (chars) for the two long free-text columns of the G4A
#: voice-candidate table (Story 43-4, rider R5 — width-aware columns). The voice
#: ``voice_name`` (e.g. "Sarah - Mature, Reassuring, Confident") and the
#: ``use_case`` characteristic are the only unbounded cells; ``voice_id`` / gender
#: / accent are naturally short. Both are hard-capped via :func:`_truncate_cell`.
_VOICE_NAME_WIDTH: int = 40
_VOICE_USE_CASE_WIDTH: int = 24

#: Fixed display widths (chars) for the long free-text cells of the three Irene /
#: plan-band renderers (Story 43-5, rider R5 — width-aware columns). The plan-unit
#: ``source_fitness`` / ``rationale`` free text and the estimator ``summary`` are
#: the only unbounded cells; every value cell is hard-capped via
#: :func:`_truncate_cell`.
_PLAN_UNIT_TEXT_WIDTH: int = 60
_ESTIMATOR_VALUE_WIDTH: int = 60
_ESTIMATOR_SUMMARY_WIDTH: int = 72
_RUN_CONSTANTS_VALUE_WIDTH: int = 60

#: Fixed display widths (chars) for the long free-text cells of the three Story
#: 43-6 build-target renderers (rider R5 — width-aware columns). The 06B/07C
#: ``specification`` / ``body`` free text and the ``title`` / ``caption`` cells are
#: the only unbounded columns; ``slide_index`` / ``visual_kind`` are naturally short.
#: The G3B renderer's one long cell is the ``operator_prompt``. Every value cell is
#: hard-capped via :func:`_truncate_cell`.
_LITERAL_VISUAL_SPEC_WIDTH: int = 48
_LITERAL_VISUAL_CAPTION_WIDTH: int = 28
_STORYBOARD_TARGET_TITLE_WIDTH: int = 28
_STORYBOARD_TARGET_BODY_WIDTH: int = 48
_STORYBOARD_B_TEXT_WIDTH: int = 60

#: Fixed display widths (chars) for the long free-text cells of the two Story 43-8
#: final-handoff renderers (rider R5 — width-aware columns). The G4B input-package
#: ``artifact_paths`` locators / G5 ``handoff_artifact_paths`` locators and the
#: ``outcome_summary`` / ``handoff_summary`` free text are the only unbounded cells;
#: every value cell is hard-capped via :func:`_truncate_cell`.
_INPUT_PACKAGE_PATH_WIDTH: int = 72
_INPUT_PACKAGE_SUMMARY_WIDTH: int = 72
_FINAL_HANDOFF_PATH_WIDTH: int = 72
_FINAL_HANDOFF_SUMMARY_WIDTH: int = 72

#: Fixed display width (chars) for the value cells of the two Story 43-7 motion-band
#: renderers (rider R5 — width-aware columns). The G2C sanity card carries only short
#: review cells (UUID ids, a readiness word, issue/node counts, verb) — no long
#: free-text — but every value cell is still hard-capped so a fat id can never wrap
#: ugly at 80 cols.
_MOTION_VALUE_WIDTH: int = 60

#: Human-facing one-line descriptions distinguishing the two per-slide presentation
#: modes (Story 43-3). Sourced from ``app/gates/section_05_5/poll_surface.py``'s
#: closed ``_AVAILABLE_MODES`` tuple — the two modes the operator compares at G2B.
#: Unknown modes fall back to an em-dash so a new mode never raw-dumps.
_PER_SLIDE_MODE_DESCRIPTIONS: dict[str, str] = {
    "narrated-deck": "Narrated slide deck — synced voiceover, no motion clips.",
    "motion-enabled-narrated-lesson": (
        "Narrated deck plus motion / animation clips per slide."
    ),
}

#: Human-friendly labels for the ``source_type`` of an ungrounded advisory
#: component. Speaker-notes narration is the dominant flagged kind (bc747b51: all
#: 12 ungrounded advisories were ``narration``); other types fall back to a
#: title-cased rendering of the raw ``source_type``.
_SOURCE_TYPE_KIND_LABELS: dict[str, str] = {
    "narration": "Narration (Speaker Notes)",
}


def _md_table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> str:
    """Render a minimal GitHub-flavored markdown table.

    An empty ``rows`` still emits the header + separator so the operator sees the
    (empty) container rather than a silent gap.
    """
    head = "| " + " | ".join(str(h) for h in headers) + " |"
    sep = "| " + " | ".join("---" for _ in headers) + " |"
    body = [
        "| " + " | ".join("" if cell is None else str(cell) for cell in row) + " |"
        for row in rows
    ]
    return "\n".join([head, sep, *body])


def _paginate(
    rows: Sequence[Sequence[Any]], page_size: int
) -> tuple[list[Sequence[Any]], int]:
    """Return ``(first_page_rows, remaining_count)`` per the Display Standards.

    ``page_size <= 0`` disables pagination (returns every row). Otherwise the
    first ``page_size`` rows are shown and the remainder counted for a footer.
    """
    if page_size <= 0 or len(rows) <= page_size:
        return list(rows), 0
    return list(rows[:page_size]), len(rows) - page_size


def _pagination_footer(remaining: int) -> str:
    """Standard ``show next`` footer when a table was paginated."""
    return (
        f"_… {remaining} more row(s) not shown "
        f"(paginated at {PAGE_SIZE} per Marcus HIL Display Standards; `show next`)._"
    )


def _kind_label(component: Mapping[str, Any]) -> str:
    """Operator-facing "Kind" for an advisory row.

    Precedence: an explicit ``kind`` on the component > a mapped ``source_type``
    label > a title-cased raw ``source_type`` > an em-dash placeholder.
    """
    kind = component.get("kind")
    if kind:
        return str(kind)
    source_type = component.get("source_type")
    if not source_type:
        return "—"
    mapped = _SOURCE_TYPE_KIND_LABELS.get(str(source_type))
    if mapped:
        return mapped
    return str(source_type).replace("_", " ").title()


def render_gate_identity(identity: Mapping[str, Any]) -> str:
    """Exemplar — gate identity (trial / status / gate / ask) as a 2-col table."""
    rows = [
        ["Trial", identity.get("trial", "")],
        ["Status", identity.get("status", "")],
        ["Gate", identity.get("gate", "")],
        ["Ask", identity.get("ask", "")],
    ]
    return _md_table(["Item", "Value"], rows)


def _ungrounded_components(enrichment: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    """The flagged-ungrounded components (the advisory rows) in document order."""
    components = enrichment.get("typed_components") or []
    return [c for c in components if isinstance(c, Mapping) and c.get("flagged_ungrounded")]


def render_enrichment_metrics(enrichment: Mapping[str, Any]) -> str:
    """Exemplar — enrichment summary metrics (typed / ungrounded / provisional-LOs).

    ``ungrounded`` count prefers the dense ``reconcile.n_ungrounded`` tally when
    present (the authoritative machine count) and otherwise counts the
    ``flagged_ungrounded`` components directly.
    """
    typed = len(enrichment.get("typed_components") or [])
    provisional = len(enrichment.get("provisional_los") or [])
    reconcile = enrichment.get("reconcile")
    if isinstance(reconcile, Mapping) and reconcile.get("n_ungrounded") is not None:
        ungrounded = int(reconcile["n_ungrounded"])
    else:
        ungrounded = len(_ungrounded_components(enrichment))
    rows = [
        ["Typed components", typed],
        ["Flagged ungrounded (advisory)", ungrounded],
        ["Provisional LOs", provisional],
    ]
    return _md_table(["Metric", "Count"], rows)


def render_ungrounded_advisories(
    enrichment: Mapping[str, Any], *, page_size: int = PAGE_SIZE
) -> str:
    """Exemplar — ungrounded advisories as ONE ROW PER FLAG (#, component_id,
    parent, Kind), with the advisory caption and Display-Standards pagination.

    This is the tabular replacement for the free-scroll ``... NOT grounded ...``
    log sheaf (AC-3).
    """
    advisories = _ungrounded_components(enrichment)
    caption = "_advisory (speaker notes) — adjudicate at G0E_"
    rows = [
        [
            idx,
            c.get("component_id", ""),
            c.get("parent_source_id", ""),
            _kind_label(c),
        ]
        for idx, c in enumerate(advisories, start=1)
    ]
    shown, remaining = _paginate(rows, page_size)
    table = _md_table(["#", "component_id", "parent", "Kind"], shown)
    parts = [caption, table]
    if remaining:
        parts.append(_pagination_footer(remaining))
    return "\n".join(parts)


def render_learning_objectives(
    los: Sequence[Mapping[str, Any]],
    *,
    title: str = "Provisional LOs",
    page_size: int = PAGE_SIZE,
) -> str:
    """Exemplar — learning objectives as ONE ROW PER LO (#, Statement).

    Works for provisional (``g0-enrichment.provisional_los``) and ratified /
    refined (``decision-card-G0R.refined_los``) LO lists alike — both carry a
    ``statement`` field.
    """
    rows = [
        [idx, lo.get("statement", "") if isinstance(lo, Mapping) else str(lo)]
        for idx, lo in enumerate(los, start=1)
    ]
    shown, remaining = _paginate(rows, page_size)
    table = _md_table(["#", "Statement"], shown)
    parts = [f"**{title}**", table]
    if remaining:
        parts.append(_pagination_footer(remaining))
    return "\n".join(parts)


def _truncate_cell(text: str, width: int) -> str:
    """Fixed-width guard (rider R5): hard-cap a display cell so the generic table
    cannot wrap ugly at 80 cols. ``width <= 0`` disables the cap.
    """
    if width <= 0 or len(text) <= width:
        return text
    if width <= 1:
        return text[:width]
    return text[: width - 1] + "…"


def _summarize_shallow(value: Any) -> str:
    """One-level peek used inside a list summary (never recurses further)."""
    if isinstance(value, Mapping):
        return f"{{{len(value)} field(s)}}"
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return f"[{len(value)} item(s)]"
    return str(value)[:_NESTED_VALUE_MAX_CHARS]


def _summarize_nested_value(value: Any) -> str:
    """Bounded one-line summary of an arbitrary (possibly nested) value.

    Reuses the ``operator_surface_assembler._summarize_context_entry`` PATTERN
    (rider R2) — a concrete ``path`` > voice-option names > a ``kind (node_id)``
    tag > a field/count digest — generalized to any value and always bounded to
    ``_NESTED_VALUE_MAX_CHARS``. Never dumps raw nested JSON (AC-2).
    """
    if isinstance(value, Mapping):
        path = value.get("path")
        voices = value.get("voices")
        kind = value.get("kind")
        node = value.get("node_id")
        if isinstance(path, str) and path:
            text = path
        elif isinstance(voices, Sequence) and not isinstance(voices, (str, bytes)) and voices:
            names = [
                str(v.get("voice_name"))
                for v in voices
                if isinstance(v, Mapping) and v.get("voice_name")
            ]
            text = "voice options: " + ", ".join(names) if names else "voice options"
        elif kind and node:
            text = f"{kind} ({node})"
        else:
            fields = ", ".join(str(k) for k in list(value)[:8])
            text = f"{{{len(value)} field(s): {fields}}}" if fields else "{}"
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        text = f"[{len(value)} item(s)]"
        if value:
            text += f" e.g. {_summarize_shallow(value[0])}"
    else:
        text = str(value)
    return text[:_NESTED_VALUE_MAX_CHARS]


def render_generic_gate_content(
    content: Mapping[str, Any],
    *,
    title: str = "Gate content",
    page_size: int = PAGE_SIZE,
    value_width: int = _GENERIC_VALUE_WIDTH,
) -> str:
    """Generic FALLBACK renderer (AC-2) — project ANY paused gate's poll-surface /
    decision-card ``content`` mapping into a two-column ``Field | Value`` stderr
    table via :func:`_md_table`.

    Nested / complex values are bounded-summarized (``_summarize_nested_value`` —
    rider R2, 240-char cap) and every value cell is width-capped (rider R5); a
    deeply nested value is therefore never raw-dumped. Rows beyond ``page_size``
    paginate per the Marcus HIL Display Standards.

    This is the load-bearing scaffold: until a bespoke renderer is registered for a
    content type, this renderer tables it — so **no gate raw-dumps**.
    """
    rows: list[Sequence[Any]] = []
    for key, value in content.items():
        if isinstance(value, (Mapping, Sequence)) and not isinstance(value, (str, bytes)):
            display = _summarize_nested_value(value)
        else:
            display = "" if value is None else str(value)
        rows.append([key, _truncate_cell(display, value_width)])
    shown, remaining = _paginate(rows, page_size)
    table = _md_table(["Field", "Value"], shown)
    parts = [f"**{title}**", table]
    if remaining:
        parts.append(_pagination_footer(remaining))
    return "\n".join(parts)


def _source_is_excluded(source: Mapping[str, Any]) -> bool:
    """A directive source is excluded iff it carries a truthy ``excluded`` flag or
    a truthy ``excluded_reason``. The common ``excluded_reason: null`` is NOT
    excluded (the counts footer's ``X excluded`` tally rides on this predicate).
    """
    if source.get("excluded"):
        return True
    return bool(source.get("excluded_reason"))


def _directive_variant_slugs(gamma_settings: Any) -> dict[str, str]:
    """Map ``variant_id`` -> ``styleguide`` slug from a directive's
    ``gamma_settings`` list (each entry ``{variant_id, styleguide}``). Tolerant of
    a missing / malformed value — returns whatever well-formed entries exist.
    """
    slugs: dict[str, str] = {}
    if isinstance(gamma_settings, Sequence) and not isinstance(gamma_settings, (str, bytes)):
        for entry in gamma_settings:
            if isinstance(entry, Mapping):
                vid = entry.get("variant_id")
                slug = entry.get("styleguide")
                if vid is not None and slug is not None:
                    slugs[str(vid)] = str(slug)
    return slugs


def _corpus_basename(corpus_dir: Any) -> str:
    """Last path segment of a ``corpus_dir``, separator-agnostic and stdlib-pure
    (no ``os`` / ``pathlib`` platform coupling): normalize ``\\`` to ``/``, strip
    trailing slashes, take the final segment. Empty in, empty out.
    """
    text = str(corpus_dir or "").replace("\\", "/").rstrip("/")
    if not text:
        return ""
    return text.rsplit("/", 1)[-1]


def render_directive_sources(
    content: Mapping[str, Any],
    *,
    title: str = "G0 — Directive review",
    page_size: int = PAGE_SIZE,
) -> str:
    """Bespoke **G0 directive composition** renderer (Story 43-1) — project a
    composed *directive* mapping into the operator-approved source-inventory
    table so the operator can review the material partition (which sources, what
    roles, what floors) at the G0 confirm, instead of scanning a raw YAML dump.
    Registered under ``content_type="directive"``.

    Shape (operator-approved, BINDING — do not redesign)::

        G0 — Directive review   run <run_id> · corpus <corpus-basename>
        Variants:  A <styleguide-A> · B <styleguide-B>

        | ref | role | locator | min-words | excl | description |
        ...  (sorted PRIMARY-FIRST, lexical by ref within a role)

        N sources · P primary · S supporting · X excluded

    ``content`` is an ALREADY-PARSED directive mapping (``sources[]`` +
    ``run_id`` / ``corpus_dir`` / ``gamma_settings``) — the projector stays
    stdlib-pure, the caller (``trial.py``) does the ``yaml.safe_load``. The
    banner text is fixed to the approved shape; the contract ``title`` /
    ``page_size`` params are honored for pagination but the banner is not
    retitled. Reuses :func:`_md_table` + :func:`_truncate_cell` (rider R5).
    """
    sources = content.get("sources") or []
    source_list = [s for s in sources if isinstance(s, Mapping)]

    run_id = str(content.get("run_id") or "")
    corpus = _corpus_basename(content.get("corpus_dir"))
    slugs = _directive_variant_slugs(content.get("gamma_settings"))
    banner = f"G0 — Directive review   run {run_id} · corpus {corpus}"
    variants_line = f"Variants:  A {slugs.get('A', '—')} · B {slugs.get('B', '—')}"

    def _sort_key(entry: Mapping[str, Any]) -> tuple[int, str]:
        rank = _DIRECTIVE_ROLE_RANK.get(str(entry.get("role") or ""), 2)
        return (rank, str(entry.get("ref_id") or ""))

    ordered = sorted(source_list, key=_sort_key)
    rows: list[Sequence[Any]] = []
    for s in ordered:
        min_words = s.get("expected_min_words")
        rows.append(
            [
                s.get("ref_id", ""),
                s.get("role", ""),
                _truncate_cell(str(s.get("locator") or ""), _DIRECTIVE_LOCATOR_WIDTH),
                "—" if min_words is None else min_words,
                "yes" if _source_is_excluded(s) else "—",
                _truncate_cell(str(s.get("description") or ""), _DIRECTIVE_DESC_WIDTH),
            ]
        )

    shown, remaining = _paginate(rows, page_size)
    table = _md_table(
        ["ref", "role", "locator", "min-words", "excl", "description"], shown
    )

    n = len(source_list)
    p = sum(1 for s in source_list if str(s.get("role") or "") == "primary")
    sup = sum(1 for s in source_list if str(s.get("role") or "") == "supporting")
    x = sum(1 for s in source_list if _source_is_excluded(s))
    footer = f"{n} sources · {p} primary · {sup} supporting · {x} excluded"

    parts = [banner, variants_line, "", table]
    if remaining:
        parts.append(_pagination_footer(remaining))
    parts.extend(["", footer])
    return "\n".join(parts)


def _unwrap_payload(content: Mapping[str, Any], payload_key: str) -> Mapping[str, Any]:
    """Return ``content[payload_key]`` when it is the nested poll-surface payload,
    else ``content`` itself.

    The paused-at-gate path may feed EITHER the full poll-surface ``display_*``
    return (which nests the fields under ``payload_key``) OR the payload mapping
    directly — this keeps both bespoke renderers tolerant of the shape they are
    handed without ever raw-dumping.
    """
    nested = content.get(payload_key)
    if isinstance(nested, Mapping):
        return nested
    return content


def render_per_slide_mode(
    content: Mapping[str, Any],
    *,
    title: str = "G2B per-slide-mode selection",
    page_size: int = PAGE_SIZE,
) -> str:
    """Bespoke **G2B per-slide-mode selection** renderer (Story 43-3, AC-1) —
    table the available per-slide presentation modes with the field that
    distinguishes them, instead of the generic ``Field | Value`` dump.

    ``content`` is the ``app/gates/section_05_5/poll_surface.py::display_per_slide_mode``
    return shape (``surface_id`` / ``slide_id`` / ``decision_card`` /
    ``per_slide_mode_payload`` with ``available_modes`` + ``readiness_status``), or
    the ``per_slide_mode_payload`` mapping directly. Registered under
    ``content_type="per_slide_mode"``. Reuses :func:`_md_table` + :func:`_truncate_cell`
    (rider R5). Projector stays stdlib-pure — the caller parses any on-disk YAML/JSON.
    """
    payload = _unwrap_payload(content, "per_slide_mode_payload")
    modes = payload.get("available_modes") or []
    readiness = payload.get("readiness_status") or content.get("readiness_status") or "—"
    slide_id = content.get("slide_id") or payload.get("slide_id") or "—"
    banner = (
        f"G2B per-slide-mode selection   slide {slide_id} · readiness {readiness}"
    )
    rows: list[Sequence[Any]] = [
        [
            idx,
            mode,
            _truncate_cell(
                _PER_SLIDE_MODE_DESCRIPTIONS.get(str(mode), "—"), _MODE_DESC_WIDTH
            ),
        ]
        for idx, mode in enumerate(modes, start=1)
    ]
    shown, remaining = _paginate(rows, page_size)
    table = _md_table(["#", "Mode", "Description"], shown)
    parts = [banner, "", table]
    if remaining:
        parts.append(_pagination_footer(remaining))
    return "\n".join(parts)


def render_variant_ab(
    content: Mapping[str, Any],
    *,
    title: str = "G2M A/B variant selection",
    page_size: int = PAGE_SIZE,
) -> str:
    """Bespoke **G2M A/B variant selection** renderer (Story 43-3, AC-2) — table
    the per-slide A/B variants side-by-side (one column per variant), instead of
    the generic ``Field | Value`` dump.

    ``content`` is the ``app/gates/section_07b/poll_surface.py::display_per_slide_variant``
    return shape (``surface_id`` / ``slide_ids`` / ``decision_card`` /
    ``per_slide_variant_payload`` with ``readiness_status`` + ``ready_nodes``), or
    the ``per_slide_variant_payload`` mapping directly. One row per slide awaiting
    an A/B selection. Registered under ``content_type="variant_ab"``. Reuses
    :func:`_md_table` (rider R5); projector stays stdlib-pure.
    """
    payload = _unwrap_payload(content, "per_slide_variant_payload")
    slide_ids = content.get("slide_ids")
    if not isinstance(slide_ids, Sequence) or isinstance(slide_ids, (str, bytes)):
        slide_ids = payload.get("ready_nodes") or []
    readiness = payload.get("readiness_status") or content.get("readiness_status") or "—"
    banner = (
        f"G2M A/B variant selection   {len(slide_ids)} slide(s) · "
        f"readiness {readiness}"
    )
    rows: list[Sequence[Any]] = [
        [idx, slide_id, "A", "B"] for idx, slide_id in enumerate(slide_ids, start=1)
    ]
    shown, remaining = _paginate(rows, page_size)
    table = _md_table(["#", "slide_id", "Variant A", "Variant B"], shown)
    parts = [banner, "", table]
    if remaining:
        parts.append(_pagination_footer(remaining))
    return "\n".join(parts)


def _voice_options(card: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    """The rich voice-option dicts the operator picks FROM — sourced from the G4A
    card's ``pick_context`` entry whose ``kind == "voice-options"`` (each voice
    carries ``voice_name`` / ``voice_id`` / ``characteristics``). Empty when the
    card carries only the bare ``voice_candidates`` id list with no adjacent
    specialist voice-options block (the renderer then falls back to that id list).
    """
    pick_context = card.get("pick_context")
    if isinstance(pick_context, Sequence) and not isinstance(pick_context, (str, bytes)):
        for entry in pick_context:
            if isinstance(entry, Mapping) and entry.get("kind") == "voice-options":
                voices = entry.get("voices")
                if isinstance(voices, Sequence) and not isinstance(voices, (str, bytes)):
                    return [v for v in voices if isinstance(v, Mapping)]
    return []


def render_voice_candidates(
    content: Mapping[str, Any],
    *,
    title: str = "G4A voice-candidate selection",
    page_size: int = PAGE_SIZE,
) -> str:
    """Bespoke **G4A voice-candidate selection** renderer (Story 43-4, AC-1) — table
    the candidate voices ONE ROW PER CANDIDATE with their distinguishing fields
    (voice name + ``voice_id`` + gender / accent / use-case characteristics), instead
    of the generic ``Field | Value`` dump, so the operator can choose a voice on the
    merits.

    ``content`` is the ``app/models/decision_cards/g4a.py::G4ACard`` body the runner
    surfaces at a paused G4A ``11-gate`` (the ``decision-card-G4A.json`` ``card``
    mapping — ``voice_candidates`` id list + a ``pick_context`` entry
    ``{kind: "voice-options", voices: [...]}`` + ``selected_voice_id``). It also
    tolerates the nested section_11 ``poll_surface.display_voice_candidates`` display
    shape (the card body nested under ``decision_card``) — :func:`_unwrap_payload`
    drills in either way. Registered under ``content_type="voice_candidates"``.

    NB (Story 43-4 judgment call): ``section_11/poll_surface.py::display_voice_candidates``
    is bound to the ``G4Card`` FIDELITY-CLOSEOUT model (``extra="forbid"``, no
    ``voice_candidates`` / ``pick_context`` fields), so it does NOT carry the voice
    candidates — the card that actually flows at a paused G4A is the ``G4ACard``
    (proven by the on-disk ``decision-card-G4A.json`` evidence). This renderer targets
    that real card body.

    Reuses :func:`_md_table` + :func:`_truncate_cell` (rider R5). Projector stays
    stdlib-pure — the caller parses any on-disk YAML/JSON.
    """
    card = _unwrap_payload(content, "decision_card")
    voices = _voice_options(card)
    selected = card.get("selected_voice_id")
    candidate_ids = card.get("voice_candidates")
    if not (
        isinstance(candidate_ids, Sequence) and not isinstance(candidate_ids, (str, bytes))
    ):
        candidate_ids = []

    rows: list[Sequence[Any]] = []
    if voices:
        # Rich voice-options block — one row per candidate with distinguishing fields.
        for idx, voice in enumerate(voices, start=1):
            characteristics = voice.get("characteristics")
            if not isinstance(characteristics, Mapping):
                characteristics = {}
            voice_id = str(voice.get("voice_id") or "")
            rows.append(
                [
                    idx,
                    _truncate_cell(str(voice.get("voice_name") or ""), _VOICE_NAME_WIDTH),
                    voice_id,
                    characteristics.get("gender") or "—",
                    characteristics.get("accent") or "—",
                    _truncate_cell(
                        str(characteristics.get("use_case") or "—"), _VOICE_USE_CASE_WIDTH
                    ),
                    "yes" if selected and voice_id == str(selected) else "—",
                ]
            )
    else:
        # Fallback — the bare ``voice_candidates`` id list (no specialist options
        # attached); still one row per candidate so the operator sees the choices.
        for idx, voice_id in enumerate(candidate_ids, start=1):
            vid = str(voice_id)
            sel = "yes" if selected and vid == str(selected) else "—"
            rows.append([idx, "—", vid, "—", "—", "—", sel])

    n = len(rows)
    sel_note = f"selected {selected}" if selected else "no pick yet (default-accept)"
    banner = f"G4A voice-candidate selection   {n} candidate(s) · {sel_note}"
    shown, remaining = _paginate(rows, page_size)
    table = _md_table(
        ["#", "Voice", "voice_id", "Gender", "Accent", "Use case", "Sel"], shown
    )
    parts = [banner, "", table]
    if remaining:
        parts.append(_pagination_footer(remaining))
    return "\n".join(parts)


def _plan_unit_body(content: Mapping[str, Any]) -> Mapping[str, Any]:
    """Return the PlanUnit mapping from whatever shape the paused-gate path hands us.

    Tolerates (a) the ``section_04a/poll_surface.py::display_plan_unit`` return shape
    (PlanUnit under a top-level ``plan_unit`` key), (b) the G1 decision-card ``card``
    body (PlanUnit nested at ``drafted_proposal.plan_unit``), or (c) a bare PlanUnit
    mapping handed directly — so the renderer never raw-dumps regardless of shape.
    """
    plan_unit = content.get("plan_unit")
    if isinstance(plan_unit, Mapping):
        return plan_unit
    drafted = content.get("drafted_proposal")
    if isinstance(drafted, Mapping):
        nested = drafted.get("plan_unit")
        if isinstance(nested, Mapping):
            return nested
    return content


def render_plan_unit(
    content: Mapping[str, Any],
    *,
    title: str = "G1A plan-unit ratification",
    page_size: int = PAGE_SIZE,
) -> str:
    """Bespoke **G1A plan-unit ratification** renderer (Story 43-5, AC-1) — table the
    PlanUnit's ratification attributes (unit id, event type, weather band, scope
    verdict + state, modality, source-fitness, rationale, gap count) as named rows,
    instead of the generic ``Field | Value`` dump, so the operator ratifies the unit
    on its merits.

    ``content`` is the ``app/gates/section_04a/poll_surface.py::display_plan_unit``
    return shape (``surface_id`` / ``decision_card`` / ``plan_unit``), or the G1
    decision-card ``card`` body (PlanUnit nested under
    ``drafted_proposal.plan_unit``), or a bare PlanUnit mapping — :func:`_plan_unit_body`
    drills to the PlanUnit either way. Registered under ``content_type="plan_unit"``.
    Reuses :func:`_md_table` + :func:`_truncate_cell` (rider R5); projector stays
    stdlib-pure — the caller parses any on-disk YAML/JSON.
    """
    unit = _plan_unit_body(content)
    scope = unit.get("scope_decision")
    if not isinstance(scope, Mapping):
        scope = {}
    unit_id = unit.get("unit_id") or "—"
    event_type = unit.get("event_type") or "—"
    weather = unit.get("weather_band") or "—"
    gaps = unit.get("gaps")
    n_gaps = (
        len(gaps)
        if isinstance(gaps, Sequence) and not isinstance(gaps, (str, bytes))
        else 0
    )
    scope_cell = (
        f"{scope.get('scope') or '—'} "
        f"({scope.get('state') or '—'}; proposed_by {scope.get('proposed_by') or '—'}, "
        f"ratified_by {scope.get('ratified_by') or '—'})"
    )
    banner = (
        f"G1A plan-unit ratification   unit {unit_id} · {event_type} · weather {weather}"
    )
    rows: list[Sequence[Any]] = [
        ["unit_id", unit_id],
        ["event_type", event_type],
        ["weather_band", weather],
        ["scope", scope_cell],
        ["modality_ref", unit.get("modality_ref") or "—"],
        [
            "source_fitness",
            _truncate_cell(
                str(unit.get("source_fitness_diagnosis") or "—"), _PLAN_UNIT_TEXT_WIDTH
            ),
        ],
        ["rationale", _truncate_cell(str(unit.get("rationale") or "—"), _PLAN_UNIT_TEXT_WIDTH)],
        ["gaps", f"{n_gaps} gap(s)"],
    ]
    shown, remaining = _paginate(rows, page_size)
    table = _md_table(["Attribute", "Value"], shown)
    parts = [banner, "", table]
    if remaining:
        parts.append(_pagination_footer(remaining))
    return "\n".join(parts)


def _estimator_body(content: Mapping[str, Any]) -> Mapping[str, Any]:
    """Return the estimator G1Card mapping from whatever shape we are handed.

    Tolerates the ``section_04_5/poll_surface.py::display_estimator`` return shape
    (G1Card under a top-level ``estimator`` key) OR the bare G1Card ``card`` body
    handed directly.
    """
    estimator = content.get("estimator")
    if isinstance(estimator, Mapping):
        return estimator
    return content


def render_estimator(
    content: Mapping[str, Any],
    *,
    title: str = "G1.5 run-budget estimator",
    page_size: int = PAGE_SIZE,
) -> str:
    """Bespoke **G1.5 run-budget estimator** renderer (Story 43-5, AC-1) — table the
    estimator's line items (parent slide count, target runtime, estimated slides,
    per-slide seconds, feasibility — whatever the section_04_5 estimator's
    ``drafted_proposal`` carries) ONE ROW PER LINE ITEM, instead of the generic
    ``Field | Value`` dump.

    ``content`` is the ``app/gates/section_04_5/poll_surface.py::display_estimator``
    return shape (``surface_id`` / ``estimator_id`` / ``estimator``), or the bare
    estimator G1Card ``card`` body — :func:`_estimator_body` drills in either way. The
    estimate line items live in the G1Card's free-form ``drafted_proposal`` (the
    section_04_5 estimator reuses ``G1Card`` as its decision card, carrying the budget
    values there, NOT in dedicated model fields — verified against
    ``tests/gates/section_04_5/_helpers.py::fixture_estimator_card``). Registered under
    ``content_type="estimator"``. Reuses :func:`_md_table` + :func:`_truncate_cell`
    (rider R5); projector stays stdlib-pure.
    """
    card = _estimator_body(content)
    proposal = card.get("drafted_proposal")
    if not isinstance(proposal, Mapping):
        proposal = {}
    rows: list[Sequence[Any]] = []
    for key, value in proposal.items():
        if isinstance(value, (Mapping, Sequence)) and not isinstance(value, (str, bytes)):
            display = _summarize_nested_value(value)
        else:
            display = "" if value is None else str(value)
        rows.append([key, _truncate_cell(display, _ESTIMATOR_VALUE_WIDTH)])
    n = len(rows)
    banner = f"G1.5 run-budget estimator   {n} line item(s)"
    shown, remaining = _paginate(rows, page_size)
    table = _md_table(["Line item", "Value"], shown)
    parts = [banner, "", table]
    if remaining:
        parts.append(_pagination_footer(remaining))
    summary = card.get("trial_summary")
    if summary:
        parts.extend(
            ["", f"summary: {_truncate_cell(str(summary), _ESTIMATOR_SUMMARY_WIDTH)}"]
        )
    return "\n".join(parts)


def _run_constants_body(content: Mapping[str, Any]) -> Mapping[str, Any]:
    """Return the run-constants key/value mapping from whatever shape we are handed.

    Tolerates the ``section_04_55/poll_surface.py::display_run_constants`` return shape
    (the flat constants under a top-level ``run_constants`` key), the review-payload
    ``constants`` key, OR the bare constants mapping handed directly.
    """
    for key in ("run_constants", "constants"):
        nested = content.get(key)
        if isinstance(nested, Mapping):
            return nested
    return content


def render_run_constants(
    content: Mapping[str, Any],
    *,
    title: str = "G1.5 run-constants lock",
    page_size: int = PAGE_SIZE,
) -> str:
    """Bespoke **G1.5 run-constants lock** renderer (Story 43-5, AC-1) — table the
    run-constants as ONE ROW PER CONSTANT (key → value), instead of the generic
    ``Field | Value`` dump, so the operator reviews the locked run parameters on their
    merits. Nested values (e.g. a ``cluster_density`` sub-map) are bounded-summarized
    (:func:`_summarize_nested_value`, 240-char cap), never raw-dumped.

    ``content`` is the ``app/gates/section_04_55/poll_surface.py::display_run_constants``
    return shape (``surface_id`` / ``run_constants_id`` / ``run_constants``), the
    review-payload ``constants`` shape, or the bare constants mapping —
    :func:`_run_constants_body` drills in either way. Registered under
    ``content_type="run_constants"``. Reuses :func:`_md_table` + :func:`_truncate_cell`
    (rider R5); projector stays stdlib-pure.
    """
    constants = _run_constants_body(content)
    rc_id = (
        content.get("run_constants_id")
        or constants.get("run_id")
        or constants.get("RUN_ID")
        or "—"
    )
    rows: list[Sequence[Any]] = []
    for key, value in constants.items():
        if isinstance(value, (Mapping, Sequence)) and not isinstance(value, (str, bytes)):
            display = _summarize_nested_value(value)
        else:
            display = "" if value is None else str(value)
        rows.append([key, _truncate_cell(display, _RUN_CONSTANTS_VALUE_WIDTH)])
    n = len(rows)
    banner = f"G1.5 run-constants lock   {rc_id} · {n} constant(s)"
    shown, remaining = _paginate(rows, page_size)
    table = _md_table(["Constant", "Value"], shown)
    parts = [banner, "", table]
    if remaining:
        parts.append(_pagination_footer(remaining))
    return "\n".join(parts)


def _literal_visual_rows(content: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    """Return the literal-visual target rows from whatever shape we are handed.

    Tolerates the ``section_06b/poll_surface.py::display_literal_visual_targets``
    return shape (rows under ``literal_visual_targets``) OR a bare build payload
    (rows under ``slide_specifications`` / ``cards``) handed directly. The key
    precedence mirrors the poll-surface's own ``_target_rows``, replicated here so
    the projector stays stdlib-pure (no poll_surface import).
    """
    for key in ("literal_visual_targets", "slide_specifications", "cards"):
        rows = content.get(key)
        if isinstance(rows, Sequence) and not isinstance(rows, (str, bytes)):
            return [r for r in rows if isinstance(r, Mapping)]
    return []


def render_literal_visual(
    content: Mapping[str, Any],
    *,
    title: str = "06B literal-visual build targets",
    page_size: int = PAGE_SIZE,
) -> str:
    """Bespoke **06B literal-visual build targets** renderer (Story 43-6, AC-1) —
    table each literal-visual build target ONE ROW PER SLIDE with its distinguishing
    fields (slide index + visual kind + specification + caption), instead of the
    generic ``Field | Value`` dump, so the operator reviews the build list on its
    merits.

    ``content`` is the ``section_06b/poll_surface.py::display_literal_visual_targets``
    return shape (``surface_id`` / ``plan_unit_id`` / ``target_section`` /
    ``literal_visual_targets`` rows / ``source_payload``), or a bare build payload
    (``slide_specifications`` / ``cards``) — :func:`_literal_visual_rows` drills to the
    rows either way. Registered under ``content_type="literal_visual"``. The 06B
    poll-surface returns a plain dict (no bound Pydantic model / decision card — the
    manifest node "06B" is ``gate: false`` and never pauses at a gate string), so the
    routing key is the poll-surface ``surface_id``. Reuses :func:`_md_table` +
    :func:`_truncate_cell` (rider R5); projector stays stdlib-pure.
    """
    rows_src = _literal_visual_rows(content)
    plan_unit_id = content.get("plan_unit_id") or "—"
    rows: list[Sequence[Any]] = []
    for idx, row in enumerate(rows_src, start=1):
        slide = row.get("slide_index")
        if slide is None:
            slide = row.get("slide_id") or idx
        rows.append(
            [
                idx,
                slide,
                row.get("visual_kind") or "—",
                _truncate_cell(
                    str(row.get("specification") or "—"), _LITERAL_VISUAL_SPEC_WIDTH
                ),
                _truncate_cell(str(row.get("caption") or "—"), _LITERAL_VISUAL_CAPTION_WIDTH),
            ]
        )
    n = len(rows)
    banner = f"06B literal-visual build targets   {n} target(s) · unit {plan_unit_id}"
    shown, remaining = _paginate(rows, page_size)
    table = _md_table(["#", "slide", "Visual kind", "Specification", "Caption"], shown)
    parts = [banner, "", table]
    if remaining:
        parts.append(_pagination_footer(remaining))
    return "\n".join(parts)


def _storyboard_target_rows(content: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    """Return the storyboard target rows from whatever shape we are handed.

    Tolerates the ``section_07c/poll_surface.py::display_storyboard_targets`` return
    shape (rows under ``storyboard_targets``) OR a bare payload (rows under
    ``slides``) handed directly. Mirrors the poll-surface's own ``_slide_rows`` key
    precedence, replicated here so the projector stays stdlib-pure.
    """
    for key in ("storyboard_targets", "slides"):
        rows = content.get(key)
        if isinstance(rows, Sequence) and not isinstance(rows, (str, bytes)):
            return [r for r in rows if isinstance(r, Mapping)]
    return []


def render_storyboard_targets(
    content: Mapping[str, Any],
    *,
    title: str = "07C storyboard build targets",
    page_size: int = PAGE_SIZE,
) -> str:
    """Bespoke **07C storyboard build targets** renderer (Story 43-6, AC-1) — table
    each storyboard slide ONE ROW PER SLIDE with its distinguishing fields (slide
    index + title + body + caption), instead of the generic ``Field | Value`` dump.

    ``content`` is the ``section_07c/poll_surface.py::display_storyboard_targets``
    return shape (``surface_id`` / ``plan_unit_id`` / ``storyboard_targets`` rows /
    ``slide_count`` / ``source_payload``), or a bare payload (``slides``) —
    :func:`_storyboard_target_rows` drills to the rows either way. Registered under
    ``content_type="storyboard_targets"``. The 07C poll-surface returns a plain dict
    (no bound Pydantic model); node "07C" pauses at the SHARED "G2C" fold-target
    (G2B/G2M also fold into G2C), so the poll-surface ``surface_id`` is the
    disambiguating routing key (mirrors 43-5's shared-G1.5 discipline). Reuses
    :func:`_md_table` + :func:`_truncate_cell` (rider R5); projector stays stdlib-pure.
    """
    rows_src = _storyboard_target_rows(content)
    plan_unit_id = content.get("plan_unit_id") or "—"
    rows: list[Sequence[Any]] = []
    for idx, row in enumerate(rows_src, start=1):
        slide = row.get("slide_index")
        if slide is None:
            slide = row.get("slide_id") or idx
        rows.append(
            [
                idx,
                slide,
                _truncate_cell(str(row.get("title") or "—"), _STORYBOARD_TARGET_TITLE_WIDTH),
                _truncate_cell(str(row.get("body") or "—"), _STORYBOARD_TARGET_BODY_WIDTH),
                _truncate_cell(str(row.get("caption") or "—"), _STORYBOARD_TARGET_TITLE_WIDTH),
            ]
        )
    n = len(rows)
    banner = f"07C storyboard build targets   {n} slide(s) · unit {plan_unit_id}"
    shown, remaining = _paginate(rows, page_size)
    table = _md_table(["#", "slide", "Title", "Body", "Caption"], shown)
    parts = [banner, "", table]
    if remaining:
        parts.append(_pagination_footer(remaining))
    return "\n".join(parts)


def render_storyboard_b(
    content: Mapping[str, Any],
    *,
    title: str = "G3B storyboard / live-URL review",
    page_size: int = PAGE_SIZE,
) -> str:
    """Bespoke **G3B storyboard / live-URL review** renderer (Story 43-6, AC-1) — table
    the G3 card's review attributes (storyboard id, gate focus, progress, active node,
    pending count, verb, operator prompt) as named rows, instead of the generic
    ``Field | Value`` dump, so the operator reviews Storyboard B (published at G3) on
    its merits.

    ``content`` is the ``section_08b/poll_surface.py::display_storyboard_b`` return
    shape (``surface_id`` / ``storyboard_id`` / ``decision_card_digest`` /
    ``decision_card`` = a ``G3Card`` dump), or the bare ``G3Card`` ``card`` body —
    :func:`_unwrap_payload` drills into ``decision_card`` either way. Registered under
    ``content_type="storyboard_b"``.

    NB (Story 43-6 judgment call): the section_08b poll-surface binds the
    ``app/models/decision_cards/g3.py::G3Card`` model, and the card that ACTUALLY
    flows at the paused gate IS a ``G3Card`` (proven by the on-disk
    ``decision-card-G3.json`` evidence — node 08B/G3B ``fold_with: G3``, so G3B never
    pauses on its own; the G3 pause absorbs the Storyboard-B review). SAME model,
    fields present — so unlike 43-4 there is NO model-binding mismatch to file. The
    G3Card carries no dedicated "live-URL" field (the live URL is a published
    side-artifact, not a card field), so this renderer tables the real G3Card review
    attributes rather than an imaginary URL field. Routing: node 08B gate_code "G3B"
    and node 07F gate_code "G2F" (motion-clip, Story 43-7) BOTH fold into "G3", so the
    bare "G3" gate string is SHARED and deliberately NOT mapped (mirrors 43-5's
    shared-G1.5 discipline); the unambiguous "G3B" gate_code + the poll-surface
    ``surface_id`` are the routing keys.

    Reuses :func:`_md_table` + :func:`_truncate_cell` (rider R5); projector stays
    stdlib-pure — the caller parses any on-disk YAML/JSON.
    """
    card = _unwrap_payload(content, "decision_card")
    storyboard_id = content.get("storyboard_id") or card.get("card_id") or "—"
    progress = card.get("progress_percent")
    progress_cell = "—" if progress is None else f"{progress}%"
    pending = card.get("pending_nodes")
    n_pending = (
        len(pending)
        if isinstance(pending, Sequence) and not isinstance(pending, (str, bytes))
        else 0
    )
    banner = f"G3B storyboard / live-URL review   {storyboard_id} · {progress_cell}"
    rows: list[Sequence[Any]] = [
        ["storyboard_id", storyboard_id],
        ["gate_focus", card.get("gate_focus") or "—"],
        ["progress", progress_cell],
        ["active_node", card.get("active_node_id") or "—"],
        ["pending", f"{n_pending} pending node(s)"],
        ["verb", card.get("verb") or "—"],
        [
            "operator_prompt",
            _truncate_cell(str(card.get("operator_prompt") or "—"), _STORYBOARD_B_TEXT_WIDTH),
        ],
    ]
    shown, remaining = _paginate(rows, page_size)
    table = _md_table(["Attribute", "Value"], shown)
    parts = [banner, "", table]
    if remaining:
        parts.append(_pagination_footer(remaining))
    return "\n".join(parts)


def _input_package_body(content: Mapping[str, Any]) -> Mapping[str, Any]:
    """Return the input-package field mapping from whatever shape we are handed.

    Tolerates (a) the ``section_11b/poll_surface.py::display_input_package`` return
    shape (the curated ``input_package_payload`` sub-map carrying ``artifact_paths`` /
    ``outcome_summary`` / ``final_status``), (b) the full ``decision_card`` (a
    ``G4Card`` dump, which carries the SAME three fields), or (c) a bare payload /
    ``G4Card`` card body handed directly — so the renderer never raw-dumps regardless
    of shape.
    """
    payload = content.get("input_package_payload")
    if isinstance(payload, Mapping):
        return payload
    decision_card = content.get("decision_card")
    if isinstance(decision_card, Mapping):
        return decision_card
    return content


def render_input_package(
    content: Mapping[str, Any],
    *,
    title: str = "G4B input-package preview",
    page_size: int = PAGE_SIZE,
) -> str:
    """Bespoke **G4B input-package preview** renderer (Story 43-8, AC-1) — table the
    input package's artifact paths ONE ROW PER ARTIFACT, with the final status in the
    banner and the outcome summary in a footer, instead of the generic ``Field | Value``
    dump, so the operator reviews the package handed to audio synthesis on its merits.

    ``content`` is the ``section_11b/poll_surface.py::display_input_package`` return
    shape (``surface_id`` / ``input_package_id`` / ``decision_card_digest`` /
    ``decision_card`` = a ``G4Card`` dump / ``input_package_payload`` with
    ``artifact_paths`` + ``outcome_summary`` + ``final_status``), the bare
    ``input_package_payload`` sub-map, or the bare ``G4Card`` card body —
    :func:`_input_package_body` drills to the fields either way. Registered under
    ``content_type="input_package"``.

    NB (Story 43-8 judgment call): the section_11b poll-surface binds the
    ``app/models/decision_cards/g4.py::G4Card`` model, and the card that ACTUALLY flows
    at the paused gate IS a ``G4Card`` (proven by the on-disk ``runs/*/decision-card-G4.json``
    evidence — manifest node 11B-gate gate_code "G4B" declares ``fold_with: G4``, so G4B
    never pauses on its own; the G4 pause absorbs the input-package preview, and the
    curated ``input_package_payload`` reads exactly the G4Card's ``artifact_paths`` /
    ``outcome_summary`` / ``final_status``). SAME model, fields present — so like 43-6
    there is NO model-binding mismatch to file. Routing: node 11B-gate "G4B" and node 13
    "G5" (final handoff) BOTH fold into the shared "G4" pause (as does the G4 closeout
    itself), so the bare "G4" gate string is SHARED and deliberately NOT mapped (mirrors
    43-5/43-6's shared-gate discipline); the unambiguous "G4B" gate_code + the
    poll-surface ``surface_id`` are the routing keys.

    Reuses :func:`_md_table` + :func:`_truncate_cell` (rider R5); projector stays
    stdlib-pure — the caller parses any on-disk YAML/JSON.
    """
    body = _input_package_body(content)
    package_id = content.get("input_package_id") or body.get("card_id") or "—"
    final_status = body.get("final_status") or "—"
    paths = body.get("artifact_paths")
    if not (isinstance(paths, Sequence) and not isinstance(paths, (str, bytes))):
        paths = []
    rows: list[Sequence[Any]] = [
        [idx, _truncate_cell(str(path), _INPUT_PACKAGE_PATH_WIDTH)]
        for idx, path in enumerate(paths, start=1)
    ]
    n = len(rows)
    banner = (
        f"G4B input-package preview   package {package_id} · "
        f"{n} artifact(s) · status {final_status}"
    )
    shown, remaining = _paginate(rows, page_size)
    table = _md_table(["#", "Artifact path"], shown)
    parts = [banner, "", table]
    if remaining:
        parts.append(_pagination_footer(remaining))
    summary = body.get("outcome_summary")
    if summary:
        parts.extend(
            ["", f"summary: {_truncate_cell(str(summary), _INPUT_PACKAGE_SUMMARY_WIDTH)}"]
        )
    return "\n".join(parts)


def _final_handoff_body(content: Mapping[str, Any]) -> Mapping[str, Any]:
    """Return the final-handoff field mapping from whatever shape we are handed.

    Tolerates (a) the ``section_15/poll_surface.py::display_final_handoff`` return shape
    (the curated ``final_handoff_payload`` sub-map carrying ``handoff_artifact_paths`` /
    ``handoff_summary`` / ``bundle_run_id``), (b) the full ``decision_card`` (a ``G5Card``
    dump, which carries the SAME three fields), or (c) a bare payload / ``G5Card`` card
    body handed directly — so the renderer never raw-dumps regardless of shape.
    """
    payload = content.get("final_handoff_payload")
    if isinstance(payload, Mapping):
        return payload
    decision_card = content.get("decision_card")
    if isinstance(decision_card, Mapping):
        return decision_card
    return content


def render_final_handoff(
    content: Mapping[str, Any],
    *,
    title: str = "G5 final handoff",
    page_size: int = PAGE_SIZE,
) -> str:
    """Bespoke **G5 final handoff** renderer (Story 43-8, AC-1) — table the final
    operator-handoff bundle's artifact paths ONE ROW PER ARTIFACT, with the bundle run
    in the banner and the handoff summary in a footer, instead of the generic
    ``Field | Value`` dump, so the operator reviews the delivered bundle on its merits.

    ``content`` is the ``section_15/poll_surface.py::display_final_handoff`` return shape
    (``surface_id`` / ``handoff_id`` / ``decision_card_digest`` / ``decision_card`` = a
    ``G5Card`` dump / ``final_handoff_payload`` with ``bundle_run_id`` +
    ``handoff_artifact_paths`` + ``handoff_summary``), the bare ``final_handoff_payload``
    sub-map, or the bare ``G5Card`` card body — :func:`_final_handoff_body` drills to the
    fields either way. Registered under ``content_type="final_handoff"``.

    NB (Story 43-8 judgment call): the section_15 poll-surface binds the
    ``app/models/decision_cards/g5.py::G5Card`` model, and its ``final_handoff_payload``
    reads exactly the G5Card's ``handoff_artifact_paths`` / ``handoff_summary`` /
    ``bundle_run_id`` — the fields this renderer tables ARE present on the bound model, so
    there is NO field-absent model-binding mismatch to file (like 43-5/43-6). No real run
    reached G5 in the fixture corpus (G5 is NOT a woken ``ProductionGateId``; manifest node
    13 gate_code "G5" declares ``fold_with: G4``, so no ``decision-card-G5.json`` exists on
    disk), so this fixture is SYNTHETIC — built by invoking the real ``display_final_handoff``
    against a constructed ``G5Card`` (shape fidelity by construction, zero spend). Routing:
    the shared "G4" fold-target is deliberately NOT mapped (mirrors the shared-gate discipline);
    the unambiguous "G5" gate_code + the poll-surface ``surface_id`` are the routing keys.

    Reuses :func:`_md_table` + :func:`_truncate_cell` (rider R5); projector stays
    stdlib-pure — the caller parses any on-disk YAML/JSON.
    """
    body = _final_handoff_body(content)
    handoff_id = content.get("handoff_id") or body.get("card_id") or "—"
    bundle_run_id = body.get("bundle_run_id") or "—"
    paths = body.get("handoff_artifact_paths")
    if not (isinstance(paths, Sequence) and not isinstance(paths, (str, bytes))):
        paths = []
    rows: list[Sequence[Any]] = [
        [idx, _truncate_cell(str(path), _FINAL_HANDOFF_PATH_WIDTH)]
        for idx, path in enumerate(paths, start=1)
    ]
    n = len(rows)
    banner = (
        f"G5 final handoff   handoff {handoff_id} · "
        f"{n} artifact(s) · run {bundle_run_id}"
    )
    shown, remaining = _paginate(rows, page_size)
    table = _md_table(["#", "Handoff artifact"], shown)
    parts = [banner, "", table]
    if remaining:
        parts.append(_pagination_footer(remaining))
    summary = body.get("handoff_summary")
    if summary:
        parts.extend(
            ["", f"summary: {_truncate_cell(str(summary), _FINAL_HANDOFF_SUMMARY_WIDTH)}"]
        )
    return "\n".join(parts)


def _seq_count(value: Any) -> int:
    """Length of a list-like value (a JSON array), else 0 for a scalar / missing /
    string value. Small shared helper for the count cells of the motion renderers.
    """
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return len(value)
    return 0


def render_motion_plan(
    content: Mapping[str, Any],
    *,
    title: str = "G2.5 motion-plan status",
    page_size: int = PAGE_SIZE,
) -> str:
    """Bespoke **G2.5 motion-plan status** renderer (Story 43-7, AC-1) — table the
    motion-plan review card's sanity attributes (plan id, generation status, readiness,
    blocking-issue / ready-node counts, gate focus, verb) as named rows, instead of the
    generic ``Field | Value`` dump, so the operator reviews the motion plan on its merits.

    ``content`` is the ``app/gates/section_07d/poll_surface.py::display_motion_plan_status``
    return shape (``surface_id`` / ``motion_plan_id`` / ``motion_plan_status`` /
    ``decision_card_digest`` / ``decision_card`` = a ``G2CCard`` dump), or the bare
    ``G2CCard`` card body handed directly — :func:`_unwrap_payload` drills into
    ``decision_card`` either way. Registered under ``content_type="motion_plan"``.

    NB (Story 43-7 judgment call): the section_07d poll-surface binds the
    ``app/models/decision_cards/g2c.py::G2CCard`` model, and the card that ACTUALLY flows
    at the paused motion gate IS a ``G2CCard`` (manifest node "07D" gate_code "G2M"
    declares ``fold_with: G2C``, so the motion review is absorbed by the shared "G2C"
    pause — proven by the on-disk ``runs/*/decision-card-G2C.json`` evidence). SAME model,
    fields present — so like 43-6/43-8 there is NO field-absent model-binding mismatch to
    file. The generic G2C sanity card carries no dedicated motion-plan-detail field (the
    motion plan itself is an internal producer→consumer envelope, not a card field), so
    this renderer tables the real G2C review attributes rather than an imaginary detail
    field (mirrors 43-6's storyboard_b, which tables the G3Card's attributes rather than a
    non-existent live-URL field). The top-level ``motion_plan_status`` (present only in the
    ``display_*`` return, not on the bare card) falls back to a readiness-derived status
    when absent. Routing: node 07D's gate_code "G2M" is already claimed by 43-3's
    ``variant_ab`` and its fold-target "G2C" is SHARED (07C/G2B/G2M all fold there), and
    the bare "G2.5" gate_code belongs to the DIFFERENT cluster-coherence node (manifest
    "7.5"), so NO gate string is mapped for motion_plan — the unambiguous poll-surface
    ``surface_id`` (``section_07d_g2_5_motion_plan_polling``) is the sole routing key
    (mirrors 43-5's surface_id-only estimator / run_constants discipline).

    Reuses :func:`_md_table` + :func:`_truncate_cell` (rider R5); projector stays
    stdlib-pure — the caller parses any on-disk YAML/JSON.
    """
    card = _unwrap_payload(content, "decision_card")
    plan_id = content.get("motion_plan_id") or card.get("card_id") or "—"
    status = content.get("motion_plan_status")
    if not status:
        status = "completed" if card.get("readiness_status") == "ready" else "pending"
    readiness = card.get("readiness_status") or "—"
    banner = f"G2.5 motion-plan status   plan {plan_id} · status {status}"
    rows: list[Sequence[Any]] = [
        ["motion_plan_id", plan_id],
        ["status", status],
        ["readiness", readiness],
        ["blocking_issues", f"{_seq_count(card.get('blocking_issues'))} issue(s)"],
        ["ready_nodes", f"{_seq_count(card.get('ready_nodes'))} node(s)"],
        ["gate_focus", card.get("gate_focus") or "—"],
        ["verb", card.get("verb") or "—"],
    ]
    rows = [[k, _truncate_cell(str(v), _MOTION_VALUE_WIDTH)] for k, v in rows]
    shown, remaining = _paginate(rows, page_size)
    table = _md_table(["Attribute", "Value"], shown)
    parts = [banner, "", table]
    if remaining:
        parts.append(_pagination_footer(remaining))
    return "\n".join(parts)


def render_motion_clip(
    content: Mapping[str, Any],
    *,
    title: str = "G2F motion-clip",
    page_size: int = PAGE_SIZE,
) -> str:
    """Bespoke **G2F motion-clip** renderer (Story 43-7, AC-1) — table the motion-clip
    review card's sanity attributes (clip id, readiness, blocking-issue / ready-node
    counts, gate focus, verb) as named rows, instead of the generic ``Field | Value``
    dump, so the operator reviews the generated motion clip on its merits.

    ``content`` is the ``app/gates/section_07f/poll_surface.py::display_motion_clip``
    return shape (``surface_id`` / ``motion_clip_id`` / ``decision_card_digest`` /
    ``decision_card`` = a ``G2CCard`` dump), or the bare ``G2CCard`` card body handed
    directly — :func:`_unwrap_payload` drills into ``decision_card`` either way.
    Registered under ``content_type="motion_clip"``.

    NB (Story 43-7 judgment call): the section_07f poll-surface binds the same
    ``G2CCard`` model, and the card that ACTUALLY flows IS a ``G2CCard`` (manifest node
    "07F" gate_code "G2F" declares ``fold_with: G3``, so the motion-clip review is
    absorbed by the shared "G3" pause; the bound model has all fields present) — so, like
    43-6/43-8, there is NO model-binding mismatch to file. The G2C sanity card carries no
    dedicated clip-detail field, so this renderer tables the real G2C review attributes.
    Routing: node 07F's fold-target "G3" is SHARED (node 08B/G3B also folds there, and
    43-6 already pinned "G3" as deliberately unmapped), so the unambiguous "G2F" gate_code
    (never itself pauses, but a valid semantic identifier — mirrors 43-6's "G3B" and
    43-8's "G4B"/"G5") and the poll-surface ``surface_id`` (``section_07f_g2f_motion_gate``)
    are the routing keys.

    Reuses :func:`_md_table` + :func:`_truncate_cell` (rider R5); projector stays
    stdlib-pure — the caller parses any on-disk YAML/JSON.
    """
    card = _unwrap_payload(content, "decision_card")
    clip_id = content.get("motion_clip_id") or card.get("card_id") or "—"
    readiness = card.get("readiness_status") or "—"
    banner = f"G2F motion-clip   clip {clip_id} · readiness {readiness}"
    rows: list[Sequence[Any]] = [
        ["motion_clip_id", clip_id],
        ["readiness", readiness],
        ["blocking_issues", f"{_seq_count(card.get('blocking_issues'))} issue(s)"],
        ["ready_nodes", f"{_seq_count(card.get('ready_nodes'))} node(s)"],
        ["gate_focus", card.get("gate_focus") or "—"],
        ["verb", card.get("verb") or "—"],
    ]
    rows = [[k, _truncate_cell(str(v), _MOTION_VALUE_WIDTH)] for k, v in rows]
    shown, remaining = _paginate(rows, page_size)
    table = _md_table(["Attribute", "Value"], shown)
    parts = [banner, "", table]
    if remaining:
        parts.append(_pagination_footer(remaining))
    return "\n".join(parts)


#: Renderer signature: ``(content, *, title, page_size) -> str``. Bespoke renderers
#: (43-1, 43-3…43-9) register against this contract; the generic fallback above
#: satisfies it for every content type with no bespoke renderer yet.
GateContentRenderer = Callable[..., str]

#: content-type key -> bespoke renderer. Intentionally EMPTY at 43-2: this story
#: ships the scaffold + the generic fallback; later stories register here. The
#: 43-10 structural-coverage test enumerates it via ``registered_content_types``.
_RENDERER_REGISTRY: dict[str, GateContentRenderer] = {}

#: SSOT — the canonical universe of operator-facing gate content types (Story
#: 43-10, AC-1). Sourced verbatim from the Epic 43 audit inventory
#: (``_bmad-output/planning-artifacts/epic-43-hil-surface-tabular-coverage.md``
#: §2) — every gate content type the operator reviews. This is the SINGLE set that
#: BOTH the 43-10 coverage-ratchet test and every future bespoke
#: ``register_renderer`` call reference; a new gate content type is added HERE
#: first, which forces the coverage test to demand a renderer or an explicit
#: waiver. Gate mapping (audit §2): ``directive`` G0 · ``estimator`` G1.5 ·
#: ``run_constants`` G1.5 · ``plan_unit`` G1A · ``per_slide_mode`` G2B ·
#: ``variant_ab`` G2M · ``literal_visual`` 06B · ``storyboard_targets`` 07C ·
#: ``motion_plan`` G2.5 · ``motion_clip`` G2F · ``storyboard_b`` G3B ·
#: ``voice_candidates`` G4A · ``input_package`` G4B · ``final_handoff`` G5.
#: Additive data only, no behavior change (rider R7).
#:
#: Story 43-9 — HONEST DE-SCOPE of ``research_packet`` + ``workbook`` (removed
#: from this canonical set). 43-10 provisionally listed both, but the investigation
#: proved NEITHER is an operator-reviewed HIL surface at a paused gate:
#:   * ``workbook`` — the 07W band (07W.1 brief · 07W.2 Ask-A · 07W.3 review ·
#:     07W.4 Ask-B · 07W producer, wired in ``app/marcus/orchestrator/workbook_wiring.py``)
#:     is a deterministic orchestration seam that runs POST-G5 (after node 15 handoff)
#:     with NO gate code and NO poll_surface — none of its nodes pause for operator
#:     review. It is not in the woken ``ProductionGateId`` pause set and no
#:     ``decision-card-workbook*.json`` is ever written.
#:   * ``research_packet`` — the research dispatch at node 04.55 is consumed
#:     INTERNALLY (feeds enrichment / the workbook Ask-A/Ask-B seams); it has no gate,
#:     no poll_surface, and no decision card. (Node 04.55's only gated surface is the
#:     G1.5 estimator / run-constants, already covered as ``estimator`` / ``run_constants``.)
#: The coverage set should contain only content types the operator actually reviews at
#: a gate, so both are dropped — a correction of 43-10's provisional set, not a skip.
GATE_CONTENT_TYPES: frozenset[str] = frozenset(
    {
        "directive",  # G0 directive composition / sources[] material-partition
        "estimator",  # G1.5 run-budget estimator
        "run_constants",  # G1.5 run-constants lock
        "plan_unit",  # G1A PlanUnit ratification
        "per_slide_mode",  # G2B per-slide mode selection
        "variant_ab",  # G2M A/B variant selection
        "literal_visual",  # 06B literal-visual build targets
        "storyboard_targets",  # 07C storyboard build targets
        "motion_plan",  # G2.5 motion-plan status
        "motion_clip",  # G2F motion-clip card
        "storyboard_b",  # G3B storyboard / live-URL card
        "voice_candidates",  # G4A voice-candidate selection
        "input_package",  # G4B input-package preview
        "final_handoff",  # G5 final handoff artifacts + summary
        # research_packet / workbook DELIBERATELY OMITTED — Story 43-9 de-scope
        # (not operator-reviewed HIL surfaces; see the module note above).
    }
)

#: SHRINK-ONLY waiver list (Story 43-10, AC-2/AC-3). A canonical gate content type
#: appears here ONLY while it still lacks a bespoke renderer; the coverage-ratchet
#: test (``tests/marcus/cli/test_projector_coverage_ratchet_43_10.py``) accepts a
#: type as "covered" iff it is EITHER in ``registered_content_types()`` OR waived
#: here. At 43-2 (zero bespoke renderers) this is the FULL canonical set: every
#: type falls back to the generic renderer, so every type is waived and the test is
#: green. INVARIANT — this list only ever SHRINKS: each bespoke-renderer story
#: (43-1, 43-3…43-9) MUST delete its type's row here in the SAME change that calls
#: ``register_renderer`` (the test enforces registry ∩ allowlist == ∅ — you cannot
#: both register and waive). Do NOT add a new entry to "quiet" the test for a newly
#: added gate; add the renderer instead. **Empty-at-epic-close:** Story 43-12
#: (governance close) asserts ``KNOWN_UNRENDERED_ALLOWLIST == frozenset()`` — the
#: last bespoke story empties this, and the epic cannot close while any row remains.
#:
#: Story 43-1 (the FIRST allowlist→registry move) deletes ``directive`` here in the
#: same change that registers :func:`render_directive_sources` — so ``directive`` is
#: now covered by a bespoke renderer, NOT waived (the 43-10 disjoint invariant
#: ``registry ∩ allowlist == ∅`` requires the deletion).
#:
#: Story 43-3 (the SECOND allowlist→registry move) additionally deletes
#: ``per_slide_mode`` (G2B) and ``variant_ab`` (G2M) here in the same change that
#: registers :func:`render_per_slide_mode` + :func:`render_variant_ab` — both are
#: now covered by bespoke renderers, NOT waived.
#:
#: Story 43-4 (the THIRD allowlist→registry move) additionally deletes
#: ``voice_candidates`` (G4A) here in the same change that registers
#: :func:`render_voice_candidates` — now covered by a bespoke renderer, NOT waived.
#:
#: Story 43-5 (the FOURTH allowlist→registry move) additionally deletes ``plan_unit``
#: (G1A), ``estimator`` (G1.5) and ``run_constants`` (G1.5) here in the same change
#: that registers :func:`render_plan_unit` + :func:`render_estimator` +
#: :func:`render_run_constants` — all three now covered by bespoke renderers, NOT waived.
#:
#: Story 43-6 (the FIFTH allowlist→registry move) additionally deletes ``literal_visual``
#: (06B), ``storyboard_targets`` (07C) and ``storyboard_b`` (G3B) here in the same change
#: that registers :func:`render_literal_visual` + :func:`render_storyboard_targets` +
#: :func:`render_storyboard_b` — all three now covered by bespoke renderers, NOT waived.
#:
#: Story 43-8 (the SIXTH allowlist→registry move) additionally deletes ``input_package``
#: (G4B) and ``final_handoff`` (G5) here in the same change that registers
#: :func:`render_input_package` + :func:`render_final_handoff` — both now covered by
#: bespoke renderers, NOT waived.
#:
#: Story 43-7 (the SEVENTH allowlist→registry move) additionally deletes ``motion_plan``
#: (G2.5) and ``motion_clip`` (G2F) here in the same change that registers
#: :func:`render_motion_plan` + :func:`render_motion_clip` — both now covered by bespoke
#: renderers, NOT waived.
#:
#: Story 43-9 EMPTIES this allowlist. It does NOT register new renderers; instead it
#: de-scopes ``research_packet`` + ``workbook`` out of ``GATE_CONTENT_TYPES`` entirely
#: (neither is an operator-reviewed paused-gate HIL surface — see the GATE_CONTENT_TYPES
#: note above). With those two gone from the canonical set and all 14 remaining types
#: registered, the ``GATE_CONTENT_TYPES - {14 registered}`` difference below is now the
#: EMPTY set. The 43-12 governance-close assertion (``allowlist == frozenset()``)
#: therefore holds after this story.
KNOWN_UNRENDERED_ALLOWLIST: frozenset[str] = frozenset(
    GATE_CONTENT_TYPES
    - {
        "directive",
        "per_slide_mode",
        "variant_ab",
        "voice_candidates",
        "plan_unit",
        "estimator",
        "run_constants",
        "literal_visual",
        "storyboard_targets",
        "storyboard_b",
        "input_package",
        "final_handoff",
        "motion_plan",
        "motion_clip",
    }
)

#: Story 43-3, AC-0 — the gate→content_type BRIDGE. Maps the gate identifier the
#: paused-at-gate wiring sees (``trial.py::_emit_gate_surface_if_paused``'s
#: ``paused_gate`` string, or a poll-surface ``surface_id``) to the canonical
#: content-type key a bespoke renderer is registered under. This is the load-bearing
#: seam every later bespoke renderer on the paused path reuses: 43-10's canonical
#: keys (``per_slide_mode`` / ``variant_ab`` / …) are SEMANTIC, not gate_ids, so
#: without this map a renderer registered under ``"variant_ab"`` would never be
#: dispatched (the G2B/G2M cards both carry decision-card ``gate_id == "G2C"`` — the
#: PAUSED_GATE string is the disambiguator). Both the gate string and the
#: poll-surface ``surface_id`` are accepted keys so routing is robust to whichever
#: identifier the wiring holds. An UNMAPPED gate resolves to ``None`` → the generic
#: fallback renderer (behavior unchanged for every gate not listed here). Additive
#: data only, no schema bump (rider R7).
GATE_TO_CONTENT_TYPE: dict[str, str] = {
    # G2B per-slide presentation-mode selection (section_05_5).
    "G2B": "per_slide_mode",
    "section_05_5_g2b_per_slide_mode": "per_slide_mode",
    # G2M A/B variant selection (section_07b).
    "G2M": "variant_ab",
    "section_07b_g2m_per_slide_variant": "variant_ab",
    # G4A voice-candidate selection (section_11 woken 11-gate). Story 43-4.
    "G4A": "voice_candidates",
    "section_11_g4a_voice_selection": "voice_candidates",
    # Story 43-5 — G1A plan-unit ratification (section_04a). The paused-gate string
    # "G1A" is unambiguous, so both it and the poll-surface ``surface_id`` route.
    "G1A": "plan_unit",
    "section_04a_g1a_poll": "plan_unit",
    # Story 43-5 — the two G1.5 gates: run-budget estimator (section_04_5) and
    # run-constants lock (section_04_55). Both pause at the SAME "G1.5" gate string
    # (manifest RUNTIME_GATE_IDS carries a single "G1.5"), so the raw gate string
    # CANNOT disambiguate them — mapping "G1.5" to either would mis-route the other.
    # The poll-surface ``surface_id`` is therefore the disambiguating key (mirrors
    # 43-3's G2B/G2M split, where the distinct paused-gate string was the
    # disambiguator). "G1.5" is deliberately NOT mapped: an unmapped gate resolves to
    # None → the generic fallback, which still TABLES the content (no raw dump).
    "section_04_5_g1_5_estimator": "estimator",
    "section_04_55_g1_5_run_constants": "run_constants",
    # Story 43-6 — three build-target list gates.
    # 06B literal-visual build (section_06b) is a NON-gate operator-build node
    # (manifest node "06B" is ``gate: false``), so it never pauses at a gate string —
    # the poll-surface ``surface_id`` is the ONLY routing key.
    "section_06b_literal_visual_build": "literal_visual",
    # 07C storyboard build (section_07c) pauses at the SHARED "G2C" fold-target (node
    # 07C gate_code G2C; G2B/G2M also fold into G2C), so — like 43-5's G1.5 — "G2C" is
    # deliberately NOT mapped (mapping it would mis-route) and the surface_id is the
    # disambiguator.
    "section_07c_storyboard_build": "storyboard_targets",
    # G3B storyboard/live-URL (section_08b) folds into the SHARED "G3" pause (manifest
    # node 08B gate_code G3B ``fold_with: G3``; node 07F gate_code G2F motion-clip ALSO
    # folds into G3), so the bare "G3" gate string is SHARED and deliberately NOT mapped
    # (mirrors 43-5's shared-G1.5 discipline). The unambiguous "G3B" gate_code (never
    # itself pauses, but a valid semantic identifier) and the poll-surface ``surface_id``
    # are the routing keys.
    "G3B": "storyboard_b",
    "section_08b_g3b_poll": "storyboard_b",
    # Story 43-8 — G4B input-package preview (section_11b) + G5 final handoff
    # (section_15). Manifest node 11B-gate gate_code "G4B" and node 13 gate_code "G5"
    # BOTH declare ``fold_with: G4``, and the G4 closeout itself pauses at "G4" too — so
    # the bare "G4" gate string is SHARED by three surfaces and deliberately NOT mapped
    # (mapping it would mis-route; mirrors 43-5's G1.5 and 43-6's G3 shared-fold discipline).
    # "G4" is also the only one of the three in the woken ProductionGateId set. The
    # unambiguous "G4B" / "G5" gate_codes (never themselves pause, but are valid semantic
    # identifiers) and the poll-surface ``surface_id``s are the routing keys.
    "G4B": "input_package",
    "section_11b_g4b_input_package": "input_package",
    "G5": "final_handoff",
    "section_15_g5_final_handoff": "final_handoff",
    # Story 43-7 — G2.5 motion-plan status (section_07d) + G2F motion-clip (section_07f).
    # motion_plan: node 07D's gate_code "G2M" is already claimed by 43-3's ``variant_ab``,
    # its fold-target "G2C" is SHARED (07C/G2B/G2M all fold there), and the bare "G2.5"
    # gate_code belongs to the DIFFERENT cluster-coherence node (manifest "7.5") — so NO
    # gate string is mapped for motion_plan; the unambiguous poll-surface ``surface_id`` is
    # the sole routing key (mirrors 43-5's surface_id-only estimator / run_constants split).
    "section_07d_g2_5_motion_plan_polling": "motion_plan",
    # motion_clip: node 07F declares ``fold_with: G3`` and "G3" is SHARED (node 08B/G3B also
    # folds there; 43-6 already pinned "G3" as deliberately unmapped), so the unambiguous
    # "G2F" gate_code (never itself pauses, but a valid semantic identifier — mirrors 43-6's
    # "G3B" and 43-8's "G4B"/"G5") and the poll-surface ``surface_id`` are the routing keys.
    "G2F": "motion_clip",
    "section_07f_g2f_motion_gate": "motion_clip",
}


def resolve_content_type(gate_key: str | None) -> str | None:
    """Resolve a paused-gate identifier to its canonical content-type key via
    :data:`GATE_TO_CONTENT_TYPE` (Story 43-3, AC-0 bridge).

    Returns the mapped content-type key, or ``None`` for an empty / unmapped gate —
    ``None`` flows to the generic fallback in :func:`get_renderer`, so an unmapped
    gate keeps its current behavior.
    """
    if not gate_key:
        return None
    return GATE_TO_CONTENT_TYPE.get(str(gate_key))


def register_renderer(content_type: str, renderer: GateContentRenderer) -> None:
    """Register a bespoke renderer for a gate ``content_type`` (AC-1 extension
    point) — the single, obvious way a later story plugs a bespoke table into the
    scaffold.
    """
    if not content_type:
        raise ValueError("content_type must be a non-empty key")
    _RENDERER_REGISTRY[content_type] = renderer


def registered_content_types() -> frozenset[str]:
    """The enumerable set of content-type keys with a BESPOKE renderer (AC-1).

    43-10's structural-coverage test consumes this to assert every gate content
    type is covered (its shrinking known-unrendered allowlist → 0).
    """
    return frozenset(_RENDERER_REGISTRY)


def get_renderer(content_type: str | None) -> GateContentRenderer:
    """Return the bespoke renderer registered for ``content_type``, else the
    generic fallback (:func:`render_generic_gate_content`)."""
    if content_type is None:
        return render_generic_gate_content
    return _RENDERER_REGISTRY.get(content_type, render_generic_gate_content)


def render_gate_content(
    content: Mapping[str, Any],
    *,
    content_type: str | None = None,
    title: str = "Gate content",
    page_size: int = PAGE_SIZE,
) -> str:
    """Dispatch ``content`` to its registered renderer, else the generic fallback
    (AC-1/AC-2). Every paused gate's own content flows through here, so no gate
    raw-dumps even before a bespoke renderer exists.
    """
    renderer = get_renderer(content_type)
    return renderer(content, title=title, page_size=page_size)


#: Story 43-1 — register the bespoke G0 directive renderer at import time. This is
#: the first allowlist→registry move: ``directive`` leaves
#: ``KNOWN_UNRENDERED_ALLOWLIST`` (above) and gains a bespoke renderer here, so the
#: G0 confirm surface tables its source inventory instead of raw-dumping YAML.
register_renderer("directive", render_directive_sources)

#: Story 43-3 — register the two bespoke G2B/G2M renderers at import time (the
#: SECOND allowlist→registry move). ``per_slide_mode`` + ``variant_ab`` leave
#: ``KNOWN_UNRENDERED_ALLOWLIST`` (above) and gain bespoke renderers here, so the
#: paused G2B / G2M surfaces table their options instead of raw-dumping.
register_renderer("per_slide_mode", render_per_slide_mode)
register_renderer("variant_ab", render_variant_ab)

#: Story 43-4 — register the bespoke G4A voice-candidate renderer at import time (the
#: THIRD allowlist→registry move). ``voice_candidates`` leaves
#: ``KNOWN_UNRENDERED_ALLOWLIST`` (above) and gains a bespoke renderer here, so the
#: paused G4A surface tables its candidate voices instead of raw-dumping.
register_renderer("voice_candidates", render_voice_candidates)

#: Story 43-5 — register the three bespoke Irene / plan-band renderers at import time
#: (the FOURTH allowlist→registry move). ``plan_unit`` (G1A), ``estimator`` (G1.5) and
#: ``run_constants`` (G1.5) leave ``KNOWN_UNRENDERED_ALLOWLIST`` (above) and gain
#: bespoke renderers here, so the paused G1A / G1.5 surfaces table their content
#: instead of raw-dumping.
register_renderer("plan_unit", render_plan_unit)
register_renderer("estimator", render_estimator)
register_renderer("run_constants", render_run_constants)

#: Story 43-6 — register the three bespoke build-target renderers at import time (the
#: FIFTH allowlist→registry move). ``literal_visual`` (06B), ``storyboard_targets`` (07C)
#: and ``storyboard_b`` (G3B) leave ``KNOWN_UNRENDERED_ALLOWLIST`` (above) and gain
#: bespoke renderers here, so the paused 06B / 07C / G3B surfaces table their build-target
#: lists instead of raw-dumping.
register_renderer("literal_visual", render_literal_visual)
register_renderer("storyboard_targets", render_storyboard_targets)
register_renderer("storyboard_b", render_storyboard_b)

#: Story 43-8 — register the two bespoke final-handoff renderers at import time (the
#: SIXTH allowlist→registry move). ``input_package`` (G4B) and ``final_handoff`` (G5)
#: leave ``KNOWN_UNRENDERED_ALLOWLIST`` (above) and gain bespoke renderers here, so the
#: paused G4B / G5 surfaces table their artifact packages instead of raw-dumping.
register_renderer("input_package", render_input_package)
register_renderer("final_handoff", render_final_handoff)

#: Story 43-7 — register the two bespoke motion-band renderers at import time (the
#: SEVENTH allowlist→registry move). ``motion_plan`` (G2.5) and ``motion_clip`` (G2F)
#: leave ``KNOWN_UNRENDERED_ALLOWLIST`` (above) and gain bespoke renderers here, so the
#: paused motion surfaces (folded into G2C / G3) table their review card instead of
#: raw-dumping.
register_renderer("motion_plan", render_motion_plan)
register_renderer("motion_clip", render_motion_clip)


def render_hil_tables(surface: Mapping[str, Any], *, page_size: int = PAGE_SIZE) -> str:
    """Render an operator-facing HIL surface as stacked markdown tables.

    ``surface`` is a normalized dict; every section is optional and rendered only
    when present:

    * ``"gate_identity"``: ``{trial, status, gate, ask}`` -> gate-identity table.
    * ``"enrichment"``: a ``g0-enrichment.json`` dict -> metrics table +
      ungrounded-advisory table + provisional-LO table.
    * ``"learning_objectives"``: ``{"title": str, "rows": [ {statement}, ... ]}``
      -> an explicit LO table (e.g. G0R ratified/refined LOs). Rendered IN
      ADDITION to any provisional LOs from ``enrichment``.
    * ``"gate_content"``: ``{"content": Mapping, "content_type": str | None,
      "title": str}`` -> the paused gate's OWN poll-surface / decision-card content
      tabled via the renderer registry (bespoke if registered, else the generic
      fallback). This is the AC-3 scaffold so EVERY paused gate tables its content.

    Returns the sections joined by blank lines. An empty/None surface yields "".
    """
    sections: list[str] = []
    identity = surface.get("gate_identity")
    if identity:
        sections.append(render_gate_identity(identity))
    enrichment = surface.get("enrichment")
    if isinstance(enrichment, Mapping):
        sections.append(render_enrichment_metrics(enrichment))
        sections.append(render_ungrounded_advisories(enrichment, page_size=page_size))
        provisional = enrichment.get("provisional_los")
        if provisional:
            sections.append(
                render_learning_objectives(
                    provisional, title="Provisional LOs", page_size=page_size
                )
            )
    los_section = surface.get("learning_objectives")
    if isinstance(los_section, Mapping) and los_section.get("rows"):
        sections.append(
            render_learning_objectives(
                los_section["rows"],
                title=str(los_section.get("title", "Learning objectives")),
                page_size=page_size,
            )
        )
    gate_content = surface.get("gate_content")
    if isinstance(gate_content, Mapping) and isinstance(gate_content.get("content"), Mapping):
        sections.append(
            render_gate_content(
                gate_content["content"],
                content_type=gate_content.get("content_type"),
                title=str(gate_content.get("title", "Gate content")),
                page_size=page_size,
            )
        )
    return "\n\n".join(s for s in sections if s)


def build_gate_surface(
    *,
    gate_identity: Mapping[str, Any] | None = None,
    enrichment: Mapping[str, Any] | None = None,
    learning_objectives: Mapping[str, Any] | None = None,
    gate_content: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Assemble the normalized ``render_hil_tables`` surface dict from parts.

    Thin, keyword-only constructor so callers (CLI, tests) don't hand-shape the
    dict literal. Omitted parts are dropped. ``gate_content`` (the paused gate's
    own poll-surface / decision-card mapping) is a new optional part — additive
    within operator-surface v1 (rider R7), no schema bump.
    """
    surface: dict[str, Any] = {}
    if gate_identity:
        surface["gate_identity"] = dict(gate_identity)
    if enrichment is not None:
        surface["enrichment"] = enrichment
    if learning_objectives is not None:
        surface["learning_objectives"] = learning_objectives
    if gate_content is not None:
        surface["gate_content"] = gate_content
    return surface


def emit_gate_surface(
    surface: Mapping[str, Any],
    *,
    stream: IO[str],
    next_action: str | None = None,
    shell_context: str = "your shell prompt",
    raw_artifact: str | None = None,
) -> None:
    """CLI printer: write the tabular HIL surface (+ raw pointer + handoff cue) to
    ``stream``.

    The only IO seam in this module. Writes the rendered tables, then per AC-6 a
    consistent one-line raw-access pointer (the machine JSON on stdout is the
    documented raw form at EVERY gate — ``raw_artifact`` names the on-disk copy
    when known), then per AC-6 a handoff-cue footer stating the shell context and
    the exact resume affordance so the operator does not type ``c`` / ``approve``
    at the shell. ``next_action`` (when supplied) is the NEUTRAL next-step surface
    from ``app.marcus.cli.next_action.build_next_action`` — never an
    approve-prefilled command.
    """
    body = render_hil_tables(surface)
    if body:
        stream.write(body + "\n")
    raw_line = "raw: full machine JSON on stdout"
    if raw_artifact:
        raw_line += f" · on-disk: {raw_artifact}"
    stream.write("\n" + raw_line + "\n")
    gate = ""
    identity = surface.get("gate_identity")
    if isinstance(identity, Mapping):
        gate = str(identity.get("gate", ""))
    cue = (
        f"\nYou are back at {shell_context}; this trial is PAUSED"
        f"{f' at gate {gate}' if gate else ''} and nothing is running. "
        "Do NOT type 'c' / 'approve' here — that is not a shell command. "
        "To act, run one of the resume commands below."
    )
    stream.write(cue + "\n")
    if next_action:
        stream.write("\nNext step (Marcus proposes; you decide):\n")
        stream.write(next_action + "\n")


__all__ = [
    "GATE_CONTENT_TYPES",
    "GATE_TO_CONTENT_TYPE",
    "KNOWN_UNRENDERED_ALLOWLIST",
    "PAGE_SIZE",
    "GateContentRenderer",
    "build_gate_surface",
    "emit_gate_surface",
    "get_renderer",
    "register_renderer",
    "registered_content_types",
    "resolve_content_type",
    "render_directive_sources",
    "render_enrichment_metrics",
    "render_estimator",
    "render_final_handoff",
    "render_gate_content",
    "render_gate_identity",
    "render_generic_gate_content",
    "render_hil_tables",
    "render_input_package",
    "render_learning_objectives",
    "render_literal_visual",
    "render_motion_clip",
    "render_motion_plan",
    "render_per_slide_mode",
    "render_plan_unit",
    "render_run_constants",
    "render_storyboard_b",
    "render_storyboard_targets",
    "render_ungrounded_advisories",
    "render_variant_ab",
    "render_voice_candidates",
]
