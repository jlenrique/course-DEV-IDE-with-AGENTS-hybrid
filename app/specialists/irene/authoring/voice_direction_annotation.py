"""Pure, deterministic post-freeze voice-direction annotation pass (P5 Step 2).

Authority:
`_bmad-output/planning-artifacts/p5-directed-voice-arc-strawman-2026-06-27.md`
§F (IR-1, IR-2, MUR-2) + the implementation control cards (Card 1).

IR-1 (BLOCKING, written into the contract): `voice_direction` is delivery
METADATA layered onto an ALREADY-FROZEN, figure-gate-passed segment manifest.
The emission is a SEPARATE, deterministic, PURE pass — NOT part of the LLM
Pass-2 generation call — so delivery intent can never leak into word choice or
figure paraphrase. This module is that pass.

GROUNDING NON-NEGOTIABLE (MUR-2): the annotation takes the frozen segment
manifest as READ-ONLY input and returns NEW segment dicts with `voice_direction`
attached. It MUST NOT modify `narration_text` / `text` / `visual_references` /
`behavioral_intent` or any other grounded field — it only ADDS the
`voice_direction` key. The pass deep-copies each segment so the caller's input
is never mutated.

Import-linter fence (M3): this leaf lives under `app.specialists.irene` and
imports only the sibling Step-1 contract (`pass_2_template.VoiceDirection`). It
does NOT import `app.marcus` (keeps `app.specialists` ↛ `app.marcus`
facade/intake/orchestrator green). No I/O, no LLM, no clock, no randomness.

Precedence for the ATTACHED direction (NOT the TTS-settings mapping — that is the
Step-1 pure leaf `app.specialists._shared.voice_direction_map`):

    explicit per-segment override  >  CD/Pass-2 `voice_direction_defaults`
    >  role-derived seed (Step-6 G0-enrichment, WIRED via graph._attach_voice_direction)
    >  conservative built-in default

Built-in default: `emotional_tone=neutral`, `pace=neutral`, `energy=medium`,
`render_strategy=tts`.

`source` provenance (per-segment, stamped to the highest-priority tier that
ACTUALLY contributed a non-None value — value-presence, the same test the merge
uses, NOT mere key-presence): `operator-override` (per-segment override drove a
value) > `cd-authored` (defaults drove a value) > `role-derived` (Step-6 seed
drove a value) > `cd-authored` (built-in only — the conservative default is CD
policy). An empty `{}` or all-None override does NOT claim `operator-override`.
An explicit `source` carried in any layer wins over the computed value (so an
operator can override provenance). `source` is the audit field UDAC trusts; it
must name the tier that drove the values.

Fail-loud surfaces (UDAC: fail loud past ratification, no silent fallback) —
all raise `VoiceDirectionError` (a `SpecialistDispatchError` ⇒ recoverable
error-pause, never a silent drop):
  * an override/defaults value that is out-of-contract (bad enum, unknown key,
    wrong type, empty `voice_id`) — named with the offending segment id + key;
  * an override/seed keyed to a segment id absent from the frozen manifest
    (operator typo) — named with the unmatched key(s) + available ids;
  * a non-dict segment in the manifest.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from pydantic import ValidationError

from app.specialists.dispatch_errors import SpecialistDispatchError
from app.specialists.irene.authoring.pass_2_template import VoiceDirection


class VoiceDirectionError(SpecialistDispatchError):
    """Fail-loud error in the voice-direction DELIVERY-METADATA layer (Step 2).

    Raised by the post-freeze annotation pass when an operator/CD-supplied
    override or default cannot be reconciled into a valid ``VoiceDirection``, or
    names a segment id absent from the frozen manifest, or the manifest carries a
    non-dict segment. This is the DELIVERY-METADATA layer failing — NOT the
    LLM-authored narration script, which is untouched and already figure-gated.

    ``SpecialistDispatchError`` family ⇒ the production runner converts this into
    a recoverable error-pause rather than shipping wrong (or silently dropped)
    delivery metadata downstream. UDAC posture (operator 2026-06-27): fail loud
    past ratification, no silent fallback — an operator typo or out-of-contract
    value must surface, never be swallowed.
    """


# Conservative built-in default (control-card baseline; rubric §4 neutral row).
_BUILTIN_DEFAULT: dict[str, Any] = {
    "render_strategy": "tts",
    "emotional_tone": "neutral",
    "pace": "neutral",
    "energy": "medium",
}


def _segment_id(segment: dict[str, Any]) -> str:
    """Per-segment match key — the segment ``id`` ONLY (never slide_id).

    Matching overrides/seeds by ``id`` alone avoids cross-id-space collisions: a
    key that happens to equal some segment's ``slide_id`` must not mis-apply, and
    a genuine segment-id override must not leak onto an id-less segment. Id-less
    segments (key ``""``) match no override/seed and take the default direction.
    By the time this runs in ``graph.py``, ``backfill_delta_ids`` has already
    aliased ``segment_id`` → ``id`` on every delta.
    """
    value = segment.get("id")
    return value.strip() if isinstance(value, str) and value.strip() else ""


def _contributes(layer: dict[str, Any] | None) -> bool:
    """True iff ``layer`` actually supplies at least one non-None value.

    Provenance (``source``) must reflect which tier DROVE the merged values, not
    merely which tier's key was present: an empty ``{}`` or all-``None`` layer
    contributes nothing and may not claim ``source``. This mirrors the
    value-presence test used by ``_overlay`` so provenance and values agree.
    """
    return bool(layer) and any(value is not None for value in layer.values())


def _overlay(base: dict[str, Any], layer: dict[str, Any] | None) -> None:
    """Copy only the present (non-None) keys of ``layer`` onto ``base``.

    A missing key never overrides; an explicit ``None`` never clobbers a lower
    tier's concrete value (precedence is by PRESENCE of a real value).
    """
    if not layer:
        return
    for key, value in layer.items():
        if value is not None:
            base[key] = value


def _offending_locs(exc: ValidationError) -> str:
    """Render the offending field path(s) from a pydantic ValidationError."""
    locs: list[str] = []
    for err in exc.errors():
        loc = ".".join(str(part) for part in err.get("loc", ()))
        locs.append(loc or "<root>")
    return ", ".join(sorted(set(locs)))


def annotate_segments_with_voice_direction(
    segments: list[dict[str, Any]],
    *,
    defaults: dict[str, Any] | None = None,
    per_segment_overrides: dict[str, dict[str, Any]] | None = None,
    role_derived_seeds: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Attach a `voice_direction` to each frozen segment (PURE, deterministic).

    Args:
        segments: the frozen segment-manifest deltas (READ-ONLY; not mutated).
        defaults: lesson/Pass-2 ``voice_direction_defaults`` (CD-authored).
        per_segment_overrides: explicit per-segment direction, keyed by segment
            id (``operator-override``).
        role_derived_seeds: per-segment seeds derived from G0 enrichment
            (``role-derived``). WIRED at the Step-6 seam: ``graph._attach_voice_direction``
            re-keys the orchestrator's per-slide role→voice table onto this pass's
            segment ids (guarded by the source↔final ordinal-space divergence check)
            and passes the result here. Seeds carry VALUES only; this leaf stamps
            ``source="role-derived"`` when the seed tier drove the merged values.

    Returns:
        A NEW list of NEW segment dicts, each carrying a validated
        ``voice_direction`` payload (``VoiceDirection`` model_dump). Every
        grounded field is byte-identical to the input.
    """
    overrides = per_segment_overrides or {}
    seeds = role_derived_seeds or {}
    defaults_contributes = _contributes(defaults)

    # Pass 1: validate segment shapes + collect present ids (id-only matching).
    # A non-dict delta is a clear-error fail-loud (leaf-contract robustness): the
    # frozen manifest must be a list of segment dicts.
    present_ids: set[str] = set()
    for segment in segments:
        if not isinstance(segment, dict):
            raise VoiceDirectionError(
                "voice-direction annotation received a non-dict segment "
                f"(type {type(segment).__name__}); the frozen segment manifest "
                "must be a list of segment dicts",
                tag="irene.voice_direction.non-dict-segment",
            )
        sid = _segment_id(segment)
        if sid:
            present_ids.add(sid)

    # Fail-loud on an override/seed keyed to a segment id absent from the
    # manifest (operator typo ⇒ lost intent). UDAC no-silent-fallback.
    unmatched = sorted(
        (set(overrides) | set(seeds)) - present_ids
    )
    if unmatched:
        raise VoiceDirectionError(
            "voice_direction override/seed keyed to segment id(s) absent from "
            f"the frozen manifest: {unmatched}; available segment ids: "
            f"{sorted(present_ids)}. This is the delivery-metadata layer (an "
            "operator/CD typo), not the LLM-authored script",
            tag="irene.voice_direction.unmatched-segment-id",
        )

    annotated: list[dict[str, Any]] = []
    for segment in segments:
        # Deep-copy first: grounded fields are carried through untouched and the
        # caller's input is never mutated (IR-1 read-only input; MUR-2).
        new_segment = deepcopy(segment)
        sid = _segment_id(segment)
        override = overrides.get(sid) if sid else None
        seed = seeds.get(sid) if sid else None

        # Provenance: the highest-priority tier that ACTUALLY contributed a
        # non-None value (value-presence, matching the merge — not key-presence).
        if _contributes(override):
            source = "operator-override"
        elif defaults_contributes:
            source = "cd-authored"
        elif _contributes(seed):
            source = "role-derived"
        else:
            source = "cd-authored"

        # Build the merged direction: built-in < role-seed < defaults < override.
        # An explicit `source` carried in any layer overrides the computed value.
        merged: dict[str, Any] = dict(_BUILTIN_DEFAULT)
        merged["source"] = source
        _overlay(merged, seed)
        _overlay(merged, defaults)
        _overlay(merged, override)

        # Validate through the frozen Step-1 contract; on failure raise a CLEAR
        # tagged error naming the segment id + the offending key, flagging the
        # delivery-metadata layer (not the LLM script) as at fault.
        try:
            direction = VoiceDirection.model_validate(merged)
        except ValidationError as exc:
            raise VoiceDirectionError(
                f"segment {sid or '<id-less>'}: voice_direction delivery-metadata "
                f"is invalid (offending: {_offending_locs(exc)}); this is the "
                "delivery layer, NOT the figure-gated LLM-authored narration "
                "script. Fix the override/defaults value.",
                tag="irene.voice_direction.invalid-direction",
            ) from exc
        new_segment["voice_direction"] = direction.model_dump(
            mode="json", exclude_none=True
        )
        annotated.append(new_segment)

    return annotated


__all__ = ["VoiceDirectionError", "annotate_segments_with_voice_direction"]
