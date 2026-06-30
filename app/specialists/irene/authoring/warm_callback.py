"""Pure deterministic leaf: warm_callback grounding + Vera-R7 gate-with-teeth.

Story concierge-leg1b-warm-callback (Slice 1 — the deterministic safety core).
NO LLM. This leaf mirrors the pure-leaf style of
``app.specialists._shared.voice_provider_text``: it imports only the EXISTING
pure helpers and reuses them; it authors no ordering model of its own and edits
no frozen neck.

Two containment building blocks:

* :func:`select_grounded_callback_anchors` — the grounding DENOMINATOR (AC2/AC7):
  the strictly-prior teachable PARENT component_ids a callback may legitimately
  reference, computed from ``compute_teaches_after`` ∩ ``derive_teachable``
  (``app.marcus.lesson_plan.pedagogy_annotation``). Empty tuple when nothing
  qualifies (caller fail-safe SILENT).

* :func:`gate_warm_callback` — the Vera-R7 gate with TEETH (AC5): block-by-omission
  around ``assert_rhetorical_source_containment``. A FAIL returns ``kept=False`` +
  the audit; the caller DROPS the whole callback. STRIP is forbidden (it would
  silently alter canonical text and break the VO↔on-screen invariant + the audit
  trail). The no-new-figure check reuses the FROZEN ``figure_tokens`` neck
  READ-ONLY (inside R7's ``_figures(callback) − _figures(source)``).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.marcus.lesson_plan.pedagogy_annotation import (
    compute_teaches_after,
    derive_teachable,
)
from app.specialists._shared.voice_provider_text import (
    VoiceProviderTextError,
    assert_rhetorical_source_containment,
    audit_rhetorical_source_containment,
)

__all__ = [
    "WarmCallbackGateResult",
    "gate_warm_callback",
    "select_grounded_callback_anchors",
]


def select_grounded_callback_anchors(
    target_component_id: str,
    components: list[dict[str, Any]],
    pedagogy_annotations: Any,
) -> tuple[str, ...]:
    """Strictly-prior teachable PARENT component_ids a callback may reference.

    The denominator (AC2/AC7), computed from the EXISTING pure helpers — no new
    ordering model:

      * ``compute_teaches_after(target, all)`` gives the annotatable components
        ordered strictly before the target by ``(doc_ordinal, locator,
        component_id)`` (``pedagogy_annotation.py`` ordering primitive);
      * INTERSECTED with the subset where ``derive_teachable(resolution_status)``
        is True (i.e. front-matter ``resolution_status == "resolved"``);
      * scoped to components that actually carry a P3 annotation — a callback can
        only reference pedagogically-annotated material.

    Anchor identity is the PARENT ``component_id`` (never a ``source_point``
    ``#ordinal`` child id). Returns an EMPTY tuple when nothing qualifies (the
    caller then fails safe SILENT — no callback emitted).
    """
    by_id = {
        rec.get("component_id"): rec
        for rec in components
        if rec.get("component_id")
    }
    target = by_id.get(target_component_id)
    if target is None:
        return ()

    # Strictly-prior set via the EXISTING ordering primitive (no reinvention).
    prior_ids = compute_teaches_after(target, components)

    # Callbacks may only reference P3-annotated material.
    annotated_ids = {ann.component_id for ann in pedagogy_annotations}

    return tuple(
        cid
        for cid in prior_ids
        if cid in annotated_ids
        and derive_teachable((by_id.get(cid) or {}).get("resolution_status"))
    )


@dataclass(frozen=True)
class WarmCallbackGateResult:
    """Outcome of the Vera-R7 gate on a single generatively-authored callback.

    ``kept=False`` is BLOCK-BY-OMISSION: the caller drops the entire callback
    (fail-safe SILENT) and writes the ``audit`` record. It NEVER strips/edits the
    callback text.
    """

    kept: bool
    audit: dict
    reason: str | None = None


def gate_warm_callback(
    callback_text: str,
    source_text: str,
    *,
    clinical_terms: frozenset[str] | None = None,
) -> WarmCallbackGateResult:
    """Vera-R7 source-containment gate WITH TEETH (block-by-omission).

    Computes the audit via ``audit_rhetorical_source_containment`` and gates via
    ``assert_rhetorical_source_containment`` (tag
    ``elevenlabs.v3.vera-r7.source-containment``). On a FAIL — a numeral/figure,
    negation, comparator, or (when a lexicon is supplied) clinical term in the
    callback that does not trace to ``source_text`` — returns ``kept=False`` with
    the audit + reason so the caller OMITS the whole callback. STRIP is forbidden.

    The no-new-figure facet is R7's ``_figures(callback) − _figures(source)``,
    which reads the FROZEN ``figure_tokens`` neck READ-ONLY. The clinical leg is
    surfaced as ``deferred (no lexicon)`` in the audit when ``clinical_terms`` is
    None (Leg-4 wires a real lexicon).
    """
    audit = audit_rhetorical_source_containment(
        callback_text, source_text, clinical_terms=clinical_terms
    )
    try:
        assert_rhetorical_source_containment(
            callback_text, source_text, clinical_terms=clinical_terms
        )
    except VoiceProviderTextError as exc:
        # BLOCK-BY-OMISSION: caller drops the whole callback; never strip/edit.
        return WarmCallbackGateResult(kept=False, audit=audit, reason=str(exc))
    return WarmCallbackGateResult(kept=True, audit=audit, reason=None)
