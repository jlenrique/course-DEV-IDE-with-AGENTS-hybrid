"""Story enhanced-vo.2 — v3 provider-text compiler (TAG-ONLY) unit tests.

RED-first (T2/T3/Vera-R7). Pure/offline — ZERO network. Drives the new leaf
``app.specialists._shared.voice_provider_text`` directly:

* AC-B1/B8 — the byte-exact ``strip_tags(provider) == canonical`` firewall;
* AC-B2 — the CLOSED 8-tag eleven_v3 allowlist + unknown-bracket fail-loud;
* AC-B3 — the four sha256'd channels (canonical/provider/display/captions);
* AC-B5 — the captions zero-tag-leak HARD gate + the cross-channel MUTATION
  test (a planted tag in the captions channel MUST turn the gate red);
* AC-B8 — the Vera R7 source-containment authoring gate.
"""

from __future__ import annotations

import hashlib

import pytest

from app.specialists._shared import voice_provider_text as vpt

# The 8 live-exercised v3 tags (manifest.json,
# evidence/elevenlabs-v3-rhetorical-audition-20260629/manifest.json).
EXPECTED_ALLOWLIST = frozenset(
    {"[slow]", "[sighs]", "[whispers]", "[urgent]", "[warm]", "[curious]", "[serious]", "[excited]"}
)

CANONICAL = (
    "Access, cost, and continuity of care are all moving at once, and the next "
    "decision changes the patient's path."
)


# --------------------------------------------------------------------------- #
# AC-B2 — closed allowlist is frozen and EXACTLY the 8 audition tags.
# --------------------------------------------------------------------------- #
def test_allowlist_is_exactly_the_eight_audition_tags() -> None:
    assert vpt.ELEVEN_V3_TAG_ALLOWLIST == EXPECTED_ALLOWLIST


def test_allowlist_is_frozen() -> None:
    assert isinstance(vpt.ELEVEN_V3_TAG_ALLOWLIST, frozenset)
    with pytest.raises(AttributeError):
        vpt.ELEVEN_V3_TAG_ALLOWLIST.add("[nope]")  # type: ignore[attr-defined]


def test_compiler_version_present() -> None:
    assert isinstance(vpt.COMPILER_VERSION, str) and vpt.COMPILER_VERSION


# --------------------------------------------------------------------------- #
# AC-B1/B8 — byte-exact strip_tags firewall per populated role.
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("role", ["warm_callback", "contrast_emphasis"])
def test_strip_tags_byte_exact_recovers_canonical(role: str) -> None:
    provider = vpt.compile_provider_text(CANONICAL, rhetorical_role=role)
    # The compiler actually added a tag (provider differs from canonical).
    assert provider != CANONICAL
    assert any(tag in provider for tag in EXPECTED_ALLOWLIST)
    # Core build-breaking invariant: strip is the BYTE-EXACT inverse.
    assert vpt.strip_tags(provider) == CANONICAL


def test_strip_tags_is_idempotent_on_clean_text() -> None:
    assert vpt.strip_tags(CANONICAL) == CANONICAL


def test_tag_placement_is_deterministic() -> None:
    a = vpt.compile_provider_text(CANONICAL, rhetorical_role="warm_callback")
    b = vpt.compile_provider_text(CANONICAL, rhetorical_role="warm_callback")
    assert a == b


# --------------------------------------------------------------------------- #
# M1 — strip_tags is ALLOWLIST-AWARE, NOT bracket-blind: it removes ONLY the 8
# v3 audio tags and PASSES THROUGH legitimate canonical brackets ([1], [Figure 2],
# [CO2], [Na+], [sic]) WITHOUT raising. Those are real source content, not tags.
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "canonical_bracket",
    ["See [1].", "As shown in [Figure 2].", "Levels of [CO2] and [Na+].", "[sic] verbatim."],
)
def test_strip_tags_passes_through_non_allowlisted_canonical_brackets(
    canonical_bracket: str,
) -> None:
    # No raise; non-v3 brackets survive verbatim.
    assert vpt.strip_tags(canonical_bracket) == canonical_bracket


def test_strip_tags_derives_only_from_the_allowlist_constant() -> None:
    # Every allowlisted tag is stripped; nothing else is treated as strippable.
    for tag in EXPECTED_ALLOWLIST:
        assert vpt.strip_tags(f"{tag} hello") == "hello"
    # A non-allowlisted bracket adjacent to an allowlisted tag: only the tag goes.
    assert vpt.strip_tags("[warm] See [1] here.") == "See [1] here."


@pytest.mark.parametrize(
    "canonical",
    [
        "See [1]. The next decision changes the patient's path.",
        "As shown in [Figure 2], [CO2] rises while [Na+] falls.",
        "Plain narration with no brackets at all.",
    ],
)
@pytest.mark.parametrize("role", ["warm_callback", "contrast_emphasis"])
def test_compile_round_trips_byte_exact_with_bracketed_canonical(
    canonical: str, role: str
) -> None:
    # M1: provider = [tag] + canonical-with-brackets; strip recovers canonical EXACT.
    provider = vpt.compile_provider_text(canonical, rhetorical_role=role)
    assert vpt.strip_tags(provider) == canonical
    if "[1]" in canonical:
        assert "[1]" in provider  # the legitimate citation survives in provider.


def test_compile_fails_loud_when_canonical_already_has_v3_tag() -> None:
    # Pathological: canonical already carries a literal allowlisted tag -> ambiguous.
    with pytest.raises(vpt.VoiceProviderTextError) as ei:
        vpt.compile_provider_text("[warm] already tagged", rhetorical_role="warm_callback")
    assert ei.value.tag == "elevenlabs.v3.canonical.contains-tag"


def test_compile_unpopulated_role_fails_loud() -> None:
    with pytest.raises(vpt.VoiceProviderTextError) as ei:
        vpt.compile_provider_text(CANONICAL, rhetorical_role="curious_pivot")
    assert ei.value.tag == "elevenlabs.v3.role.unpopulated"


# --------------------------------------------------------------------------- #
# AC-B3 — four sha256'd channels.
# --------------------------------------------------------------------------- #
def test_four_channels_have_sha256_and_correct_routing() -> None:
    provider = vpt.compile_provider_text(CANONICAL, rhetorical_role="warm_callback")
    channels = vpt.build_text_channels(canonical_text=CANONICAL, provider_text=provider)
    # canonical == captions (NEVER provider); display == provider.
    assert channels["canonical_text"] == CANONICAL
    assert channels["captions_text"] == CANONICAL
    assert channels["provider_text"] == provider
    assert channels["display_text"] == provider
    # every channel carries its sha256.
    for name in ("canonical_text", "provider_text", "display_text", "captions_text"):
        expected = hashlib.sha256(channels[name].encode("utf-8")).hexdigest()
        assert channels[f"{name}_sha256"] == expected
    # captions sha == canonical sha (same bytes); provider sha differs.
    assert channels["captions_text_sha256"] == channels["canonical_text_sha256"]
    assert channels["provider_text_sha256"] != channels["canonical_text_sha256"]


# --------------------------------------------------------------------------- #
# AC-B5 — captions zero-tag-leak HARD gate + cross-channel MUTATION test.
# --------------------------------------------------------------------------- #
def test_captions_zero_tag_leak_gate_passes_on_clean_text() -> None:
    # No raise on a clean caption channel.
    vpt.assert_no_tag_leak(CANONICAL, channel="captions")


def test_captions_gate_allows_non_v3_citation_brackets() -> None:
    # M1: a citation/formula bracket in captions is FINE — only v3 audio tags leak.
    vpt.assert_no_tag_leak("See [1] and [Figure 2]; [CO2] rises.", channel="captions")


def test_captions_cross_channel_tag_bleed_mutation_turns_red() -> None:
    """MUTATION (AC-B5, HAND-BACK if absent): plant a v3 tag in the captions
    channel -> the zero-leak gate MUST turn red (only the 8 v3 tags, not [1])."""
    mutated = "[warm] " + CANONICAL  # provider bytes wrongly fed to captions
    with pytest.raises(vpt.VoiceProviderTextError) as ei:
        vpt.assert_no_tag_leak(mutated, channel="captions")
    assert ei.value.tag == "elevenlabs.v3.captions.tag-leak"


def test_build_channels_rejects_v3_tag_polluted_canonical() -> None:
    # If canonical (=> captions) carries a v3 tag, channel construction turns red.
    with pytest.raises(vpt.VoiceProviderTextError) as ei:
        vpt.build_text_channels(
            canonical_text="[warm] tainted", provider_text="[warm] tainted"
        )
    assert ei.value.tag == "elevenlabs.v3.captions.tag-leak"


def test_extract_tags_lists_allowlisted_tags_in_order_ignoring_citations() -> None:
    # M1: only allowlisted v3 tags are extracted; [1] citations are ignored.
    provider = "[warm] Access [1]. [slow] Cost [2]."
    assert vpt.extract_tags(provider) == ["[warm]", "[slow]"]


# --------------------------------------------------------------------------- #
# AC-B8 — Vera R7 source-containment authoring gate.
# --------------------------------------------------------------------------- #
SOURCE_NARRATION = (
    "Access, cost, and continuity of care are all moving at once. The next "
    "decision changes the patient's path."
)


def test_vera_r7_clean_connective_callback_passes() -> None:
    callback = (
        "Remember access. This is where it comes back. Cost and continuity now "
        "move, and the next decision changes the patient's path."
    )
    report = vpt.audit_rhetorical_source_containment(callback, SOURCE_NARRATION)
    assert report["status"] == "PASS", report
    # strict variant does not raise.
    vpt.assert_rhetorical_source_containment(callback, SOURCE_NARRATION)


def test_vera_r7_new_numeral_fails() -> None:
    callback = "Remember access. Cost rose 50% and the next decision changes the path."
    report = vpt.audit_rhetorical_source_containment(callback, SOURCE_NARRATION)
    assert report["status"] == "FAIL"
    assert report["unsourced"]["numerals_units"]
    with pytest.raises(vpt.VoiceProviderTextError) as ei:
        vpt.assert_rhetorical_source_containment(callback, SOURCE_NARRATION)
    assert ei.value.tag == "elevenlabs.v3.vera-r7.source-containment"


def test_vera_r7_new_negation_fails() -> None:
    callback = "Remember access. Continuity will not return, changing the path."
    report = vpt.audit_rhetorical_source_containment(callback, SOURCE_NARRATION)
    assert report["status"] == "FAIL"
    assert "not" in report["unsourced"]["negations"]


def test_vera_r7_new_comparator_fails() -> None:
    callback = "Remember access. Cost is greater than before, changing the path."
    report = vpt.audit_rhetorical_source_containment(callback, SOURCE_NARRATION)
    assert report["status"] == "FAIL"
    assert "greater" in report["unsourced"]["comparators"]


def test_vera_r7_comparator_present_in_source_is_clean() -> None:
    source = "Cost is greater than access. The decision changes the path."
    callback = "Cost is greater than access. The decision changes the path."
    report = vpt.audit_rhetorical_source_containment(callback, source)
    assert report["status"] == "PASS", report
