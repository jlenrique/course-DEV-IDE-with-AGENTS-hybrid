"""Pure leaf: TAG-ONLY ElevenLabs ``eleven_v3`` provider-text compiler.

Story enhanced-vo.2 (Slice 1). Authority:
`_bmad-output/implementation-artifacts/enhanced-vo-2-v3-provider-text-compiler.md`
(AC-B1..B12) + `_bmad-output/planning-artifacts/enhanced-vo-party-consensus-2026-06-29.md`.

This module is the v3 SIBLING of the frozen v2 numeric mapper
``app.specialists._shared.voice_direction_map`` (which stays FROZEN). It mirrors
that leaf's idioms:

* frozen ``frozenset`` / ``MappingProxyType`` constants loaded ONCE at import;
* a ``COMPILER_VERSION`` constant;
* a typed ``VoiceProviderTextError(tag=...)`` so the Enrique call site maps it to
  a tagged, recoverable ``EnriqueActError`` in one line;
* M3 fence (import-linter Contract M3, precedent ``voice_direction_map.py:22-27``):
  this leaf does NOT import ``app.marcus`` and imports nothing from the irene
  authoring tree at runtime — ``rhetorical_role`` rides in as a plain ``str``.

TAG-ONLY contract (AC-B1/B8 — the fidelity firewall): the compiler only
ASSEMBLES (allowlisted tag + canonical narration). It NEVER authors words, never
calls an LLM, and can introduce NO spoken token absent from the canonical text.
The build-breaking invariant is ``strip_tags(provider_text) == canonical_text``
BYTE-EXACT for every produced segment — asserted inside ``compile_provider_text``.

Channel separation (AC-B3/B5): ``canonical`` (the figure-gated narration / truth
artifact) and ``captions`` are the SAME bytes; ``provider`` (sent to TTS) and
``display`` (Storyboard B) are the SAME bytes. Captions are NEVER provider, and
``assert_no_tag_leak`` is the HARD zero-tag-leak gate wired into channel
construction so a tag can never reach a caption.
"""

from __future__ import annotations

import hashlib
import re
from types import MappingProxyType

from app.specialists._shared.figure_tokens import _figures

# Compiler contract version (mirrors voice_direction_map.MAP_VERSION idiom). Bump
# on any change to tag placement, the allowlist, or the channel shape.
COMPILER_VERSION = "voice-provider-text.v1"

# CLOSED, frozen eleven_v3 tag allowlist (AC-B2). Source of truth: the 8
# live-exercised v3 tags in
# evidence/elevenlabs-v3-rhetorical-audition-20260629/manifest.json. ``strip_tags``
# derives ONLY from this constant.
# LOCKSTEP CHANGE-UNIT (D2, Murat): any change to this 8-tag set MUST move together
# with strip_tags + extract_tags + assert_no_tag_leak (all three derive from it) AND
# the byte-identity / round-trip tests in
# tests/specialists/_shared/test_voice_provider_text.py. Never edit the set alone.
ELEVEN_V3_TAG_ALLOWLIST: frozenset[str] = frozenset(
    {
        "[slow]",
        "[sighs]",
        "[whispers]",
        "[urgent]",
        "[warm]",
        "[curious]",
        "[serious]",
        "[excited]",
    }
)

# The effective model id this compiler is wired for. Kept as a local constant so
# the leaf stays decoupled from scripts.api_clients (the Enrique consumer reconciles
# this against DEFAULT_DIALOGUE_MODEL).
ELEVEN_V3_MODEL_ID = "eleven_v3"

# Role -> ordered v3 tags (AC-B4/B10). This slice POPULATES two roles; the rest of
# the taxonomy is accepted by the VoiceDirection model but intentionally
# UNPOPULATED here (compiler fails loud if asked to compile them).
#   * warm_callback     — STRUCTURAL: Irene authors the callback as canonical;
#                         the compiler only adds [warm].
#   * contrast_emphasis — TONAL: the tag does the work on identical words
#                         ([slow] is the tag the audition contrast-emphasis
#                         variant used — manifest variant_slug "contrast-emphasis").
RHETORICAL_ROLE_TAGS: MappingProxyType[str, tuple[str, ...]] = MappingProxyType(
    {
        "warm_callback": ("[warm]",),
        "contrast_emphasis": ("[slow]",),
    }
)
POPULATED_RHETORICAL_ROLES: frozenset[str] = frozenset(RHETORICAL_ROLE_TAGS)

# Allowlist-DERIVED matchers (AC-B2 + M1). The compiler is ALLOWLIST-AWARE, NOT
# bracket-blind: bracket tokens that are NOT v3 audio tags (e.g. citations `[1]`,
# `[Figure 2]`, formulae `[CO2]`/`[Na+]`, editorial `[sic]`) are LEGITIMATE canonical
# narration content — they must pass through verbatim, never be stripped, and never
# raise. ONLY the 8 allowlisted v3 tags are compiler-added / strippable / leak-gated.
_ALLOWLIST_ALT = "(?:" + "|".join(re.escape(tag) for tag in sorted(ELEVEN_V3_TAG_ALLOWLIST)) + ")"
# Detector: "an allowlisted v3 tag is present" (captions-leak gate + the canonical
# precondition). The bracketed tokens are literal, so this never matches a longer
# word like "[warmth]".
_ALLOWLISTED_TAG_RE = re.compile(_ALLOWLIST_ALT)
# Strip matcher: an allowlisted tag plus the single trailing space the compiler
# inserts with it (prepend convention), so strip is the BYTE-EXACT inverse of compile
# for ANY canonical (brackets included).
_ALLOWLIST_STRIP_RE = re.compile(_ALLOWLIST_ALT + r"\s?")


class VoiceProviderTextError(Exception):
    """TAG-ONLY compiler / channel-firewall violation (typed, tagged).

    The pure leaf cannot import Enrique's ``EnriqueActError`` (M3 + cycle), so it
    raises this typed error carrying ``tag`` so the Enrique call site re-raises it
    as a tagged, recoverable ``EnriqueActError`` in one line.
    """

    def __init__(self, message: str, *, tag: str) -> None:
        super().__init__(message)
        self.tag = tag


def sha256_text(text: str) -> str:
    """sha256 hexdigest of the utf-8 bytes of ``text`` (channel digest)."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def extract_tags(text: str) -> list[str]:
    """Return the allowlisted v3 tags present in ``text``, in order of appearance.

    M1: non-allowlisted brackets (citations `[1]`, formulae `[CO2]`, …) are
    legitimate canonical content and are IGNORED here — never raised on, never
    listed as tags.
    """
    return [match.group(0) for match in _ALLOWLISTED_TAG_RE.finditer(text)]


def strip_tags(provider_text: str) -> str:
    """Remove ONLY the allowlisted v3 audio tags, recovering the canonical bytes.

    M1: the function is ALLOWLIST-AWARE, not bracket-blind. Non-allowlisted bracket
    tokens (citations `[1]`, `[Figure 2]`, formulae `[CO2]`/`[Na+]`, editorial
    `[sic]`) are LEGITIMATE canonical narration — they PASS THROUGH verbatim and
    NEVER raise. The strip pattern is derived ONLY from ``ELEVEN_V3_TAG_ALLOWLIST``,
    so strip is the byte-exact inverse of the compiler's prepend for ANY canonical.
    """
    return _ALLOWLIST_STRIP_RE.sub("", provider_text)


def assert_no_tag_leak(text: str, *, channel: str) -> None:
    """HARD zero-tag-leak gate (AC-B5): raise iff an allowlisted v3 AUDIO TAG appears.

    M1: ALLOWLIST-AWARE — a citation/formula bracket (`[1]`, `[Figure 2]`, `[CO2]`)
    in a learner-facing channel is FINE (real source content); only one of the 8 v3
    tags (`[warm]`, `[slow]`, …) constitutes a leak. Mutation-proven: planting a v3
    tag here turns it red.
    """
    match = _ALLOWLISTED_TAG_RE.search(text)
    if match is not None:
        raise VoiceProviderTextError(
            f"v3 audio tag {match.group(0)!r} leaked into the {channel} channel "
            "(captions/learner-facing channels must be free of v3 audio tags)",
            tag="elevenlabs.v3.captions.tag-leak",
        )


def compile_provider_text(canonical_text: str, *, rhetorical_role: str) -> str:
    """Assemble the v3 provider string for ``canonical_text`` + ``rhetorical_role``.

    TAG-ONLY: the canonical narration is preserved verbatim; the role's allowlisted
    tag(s) are prepended (deterministic order). The build-breaking firewall invariant
    ``strip_tags(provider) == canonical`` is asserted before returning, so a
    placement bug can never ship a provider string whose stripped form drifts from
    the figure-gated narration a learner reads.
    """
    tags = RHETORICAL_ROLE_TAGS.get(rhetorical_role)
    if tags is None:
        raise VoiceProviderTextError(
            f"no v3 tag mapping for rhetorical_role {rhetorical_role!r} "
            f"(populated this slice: {sorted(POPULATED_RHETORICAL_ROLES)})",
            tag="elevenlabs.v3.role.unpopulated",
        )
    # PRECONDITION (M1): if the canonical narration ALREADY contains a literal
    # allowlisted v3 tag, prepending another would make the firewall ambiguous (we
    # could not tell the compiler-added tag from a pre-existing one on strip). This
    # is pathological, never a normal figure-gated narration — fail loud rather than
    # corrupt the strip_tags(provider)==canonical invariant.
    existing = _ALLOWLISTED_TAG_RE.search(canonical_text)
    if existing is not None:
        raise VoiceProviderTextError(
            f"canonical narration already contains a literal v3 tag {existing.group(0)!r}; "
            "refusing to compile (ambiguous firewall — narration must be tag-free)",
            tag="elevenlabs.v3.canonical.contains-tag",
        )
    # NIT (optional, NOT enforced this slice): eleven_v3 has a ~5000-char request
    # limit. The compiler adds only a short tag, so a canonical already within the
    # narration-length budget stays under it; a hard length guard here is deferred
    # until a real over-length segment is observed (flagged, not implemented).
    provider_text = canonical_text
    for tag in tags:
        provider_text = f"{tag} {provider_text}"
    restored = strip_tags(provider_text)
    if restored != canonical_text:
        raise VoiceProviderTextError(
            "TAG-ONLY firewall breach: strip_tags(provider_text) != canonical_text "
            f"(got {restored!r}, expected {canonical_text!r})",
            tag="elevenlabs.v3.firewall.breach",
        )
    return provider_text


def build_text_channels(*, canonical_text: str, provider_text: str) -> dict[str, str]:
    """Build the four sha256'd channels (AC-B3) with the captions HARD gate.

    Routing (AC-B3/B5): ``canonical`` is the figure-gated narration truth artifact;
    ``captions`` is canonical (NEVER provider); ``display`` is provider (Storyboard
    B); ``provider`` is the TTS-bound string. ``assert_no_tag_leak`` guards the
    captions channel so a tag can never reach a caption.
    """
    captions_text = canonical_text  # NEVER provider (AC-B5).
    display_text = provider_text  # Storyboard B shows the literal provider bytes.
    assert_no_tag_leak(captions_text, channel="captions")
    return {
        "canonical_text": canonical_text,
        "canonical_text_sha256": sha256_text(canonical_text),
        "provider_text": provider_text,
        "provider_text_sha256": sha256_text(provider_text),
        "display_text": display_text,
        "display_text_sha256": sha256_text(display_text),
        "captions_text": captions_text,
        "captions_text_sha256": sha256_text(captions_text),
    }


# --------------------------------------------------------------------------- #
# Vera R7 source-containment authoring gate (AC-B8).
# --------------------------------------------------------------------------- #
# Closed lexicons for the zero-tolerance semantic categories that are
# deterministically extractable offline. numerals/units come from the frozen
# figure_tokens neck (read-only); negations + comparators are closed word lists.
# "clinical-term" detection requires a clinical ontology and is DEFERRED this
# slice (declared, like source_fidelity_audit.SEMANTIC_TRIPWIRE): callers may
# inject a ``clinical_terms`` lexicon to activate that leg.
_NEGATION_LEXICON: frozenset[str] = frozenset(
    {"no", "not", "never", "none", "nor", "neither", "without", "cannot", "nothing"}
)
_COMPARATOR_LEXICON: frozenset[str] = frozenset(
    {
        "more",
        "less",
        "fewer",
        "greater",
        "lower",
        "higher",
        "than",
        "most",
        "least",
        "increase",
        "increased",
        "decrease",
        "decreased",
        "rose",
        "fell",
        "doubled",
        "halved",
    }
)
_WORD_RE = re.compile(r"[A-Za-z][A-Za-z'-]*")


def _words(text: str) -> set[str]:
    return {match.group(0).lower() for match in _WORD_RE.finditer(text)}


def audit_rhetorical_source_containment(
    rhetorical_text: str,
    source_text: str,
    *,
    clinical_terms: frozenset[str] | None = None,
) -> dict:
    """Source-containment audit for Irene-authored rhetorical wording (Vera R7).

    Any numeral/unit (frozen figure_tokens neck), negation, or comparator INTRODUCED
    by ``rhetorical_text`` that does not trace to ``source_text`` is a ZERO-tolerance
    violation. A purely-connective callback that introduces no new semantic token is
    clean (PASS). The optional ``clinical_terms`` lexicon activates the deferred
    clinical-term leg (default: not checked — documented stub).

    PROVIDED-BUT-UNWIRED THIS SLICE (S4): this audit + its ``assert_*`` wrapper have
    NO runtime callers yet. The slice's primary firewall is the byte-exact TAG-ONLY
    invariant (``strip_tags(provider)==canonical``), which IS enforced; the two
    populated roles (warm_callback STRUCTURAL, contrast_emphasis TONAL) introduce no
    NEW Irene-authored clinical wording, so no authorship gate is needed yet. The
    reactivation trigger (first role that introduces new Irene-authored clinical
    wording -> wire this into the irene/enrique flow + supply a real clinical
    lexicon) is filed at deferred-inventory follow-on
    ``directed-voice-vera-r7-wire-clinical-lexicon``.

    LIMITATION (bag-of-words): negation/comparator detection is a set-membership
    check, so it has a FLIPPED-NEGATION false-negative — "not increased" vs
    "increased" both contain {"not","increased"}; a rhetorical sentence that REVERSES
    a source polarity using only source words is NOT caught. A real wiring needs
    span/dependency-aware checks, not bag-of-words.

    Pure / offline / deterministic. Returns a JSON-serializable report; never raises
    (use ``assert_rhetorical_source_containment`` for the gating wrapper).
    """
    rhet_figs = _figures(rhetorical_text)
    src_figs = _figures(source_text)
    rhet_words = _words(rhetorical_text)
    src_words = _words(source_text)

    unsourced_figures = sorted(rhet_figs - src_figs)
    unsourced_negations = sorted((rhet_words & _NEGATION_LEXICON) - src_words)
    unsourced_comparators = sorted((rhet_words & _COMPARATOR_LEXICON) - src_words)
    unsourced_clinical = (
        sorted((rhet_words & clinical_terms) - src_words) if clinical_terms else []
    )

    violated = bool(
        unsourced_figures
        or unsourced_negations
        or unsourced_comparators
        or unsourced_clinical
    )
    return {
        "status": "FAIL" if violated else "PASS",
        "gate": "vera-r7-source-containment",
        "unsourced": {
            "numerals_units": unsourced_figures,
            "negations": unsourced_negations,
            "comparators": unsourced_comparators,
            "clinical_terms": unsourced_clinical,
        },
        "clinical_terms_leg": "active" if clinical_terms else "deferred (no lexicon)",
    }


def assert_rhetorical_source_containment(
    rhetorical_text: str,
    source_text: str,
    *,
    clinical_terms: frozenset[str] | None = None,
) -> dict:
    """Gating wrapper around :func:`audit_rhetorical_source_containment` (AC-B8).

    Raises ``VoiceProviderTextError`` on a FAIL; returns the report on PASS.
    """
    report = audit_rhetorical_source_containment(
        rhetorical_text, source_text, clinical_terms=clinical_terms
    )
    if report["status"] == "FAIL":
        raise VoiceProviderTextError(
            "Vera R7 source-containment FAILED: Irene-authored rhetorical wording "
            f"introduced unsourced semantic tokens {report['unsourced']}",
            tag="elevenlabs.v3.vera-r7.source-containment",
        )
    return report


__all__ = [
    "COMPILER_VERSION",
    "ELEVEN_V3_MODEL_ID",
    "ELEVEN_V3_TAG_ALLOWLIST",
    "POPULATED_RHETORICAL_ROLES",
    "RHETORICAL_ROLE_TAGS",
    "VoiceProviderTextError",
    "assert_no_tag_leak",
    "assert_rhetorical_source_containment",
    "audit_rhetorical_source_containment",
    "build_text_channels",
    "compile_provider_text",
    "extract_tags",
    "sha256_text",
    "strip_tags",
]
