"""Story enhanced-vo.2 — Enrique v3 provider-text consumption (RED-first).

Drives the REAL ``build_assembly_bundle`` through the injected
``FakeElevenLabsClient`` (offline, deterministic) to pin:

* AC-B7 — on the v3 branch (effective model == eleven_v3 + populated
  rhetorical_role) Enrique sends PROVIDER text (canonical + [tag]) to the proven
  ``text_to_speech_with_request_id`` call, with model_id=eleven_v3 + a fixed seed;
  the receipt gains the canonical/provider shas, provider_text, strategy, tags,
  compiler version, and render_mode;
* AC-B5 — the captions seam (.vtt) receives CANONICAL, never provider (no tag leak);
* AC-B6 — skip-if-exists is re-keyed on provider_text_sha256 (a provider change
  forces re-synthesis);
* AC-B12 — directed-but-NON-v3 (and a deferred role) stays byte-identical (no
  provider_text fields, captions=canonical, no compiler call).

No live API; the live two-arm A/B is the operator-gated T8 leg (out of scope).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from app.specialists._shared import voice_provider_text as vpt
from app.specialists.enrique import _act as enrique_act
from tests.specialists.enrique._fake_elevenlabs import FakeElevenLabsClient

FLAG = "MARCUS_NARRATION_VOICE_DIRECTION_ACTIVE"
SELECTION = {"selected_voice_id": "narrator"}
CANONICAL = "Remember access. The next decision changes the patient's path."


def _v3_segment(role: str | None = "warm_callback") -> dict[str, Any]:
    vd: dict[str, Any] = {"elevenlabs": {"model_id": "eleven_v3"}}
    if role is not None:
        vd["rhetorical_role"] = role
    return {
        "segment_id": "seg-01",
        "slide_id": "slide-01",
        "text": CANONICAL,
        "voice_direction": vd,
    }


def _build(
    tmp_path: Path, segments: list[dict[str, Any]], *, client: FakeElevenLabsClient
) -> dict[str, Any]:
    payload = {"bundle_path": str(tmp_path), "segments": segments}
    return enrique_act.build_assembly_bundle(payload, selection=SELECTION, client=client)  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# AC-B7 — v3 branch sends provider_text (canonical + [tag]); receipt extended.
# --------------------------------------------------------------------------- #
def test_v3_branch_sends_provider_text_with_seed(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(FLAG, "1")
    client = FakeElevenLabsClient()
    result = _build(tmp_path, [_v3_segment("warm_callback")], client=client)

    expected_provider = vpt.compile_provider_text(CANONICAL, rhetorical_role="warm_callback")
    # The proven call received PROVIDER text (with the [warm] tag), not canonical.
    assert len(client.calls) == 1
    call = client.calls[0]
    assert call.text == expected_provider
    assert "[warm]" in call.text
    assert call.settings["model_id"] == "eleven_v3"

    receipt = result["narration_receipts"][0]
    assert receipt["render_mode"] == "v3_provider_text"
    assert receipt["provider_text"] == expected_provider
    assert receipt["provider_text_strategy"] == "warm_callback"
    assert receipt["provider_text_tags"] == ["[warm]"]
    assert receipt["provider_text_compiler_version"] == vpt.COMPILER_VERSION
    assert receipt["canonical_text_sha256"] == vpt.sha256_text(CANONICAL)
    assert receipt["provider_text_sha256"] == vpt.sha256_text(expected_provider)


def test_v3_branch_passes_fixed_seed(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(FLAG, "1")

    seen: dict[str, Any] = {}

    class _SeedSpyClient(FakeElevenLabsClient):
        def text_to_speech_with_request_id(self, text: str, voice_id: str, **kwargs: Any):
            seen.update(kwargs)
            return super().text_to_speech_with_request_id(text, voice_id, **kwargs)

    _build(tmp_path, [_v3_segment("warm_callback")], client=_SeedSpyClient())
    assert "seed" in seen and isinstance(seen["seed"], int)


# --------------------------------------------------------------------------- #
# AC-B5 — captions (.vtt) receive canonical, never provider (no tag leak).
# --------------------------------------------------------------------------- #
def test_v3_captions_are_canonical_no_tag_leak(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(FLAG, "1")
    client = FakeElevenLabsClient()
    _build(tmp_path, [_v3_segment("warm_callback")], client=client)

    vtt = (tmp_path / "assembly-bundle" / "captions" / "seg-01.vtt").read_text(encoding="utf-8")
    assert CANONICAL in vtt
    assert "[warm]" not in vtt
    # The HARD gate would reject a tag in the captions channel.
    vpt.assert_no_tag_leak(vtt, channel="captions")


# --------------------------------------------------------------------------- #
# AC-B6 — skip-if-exists re-keyed on provider_text_sha256.
# --------------------------------------------------------------------------- #
def test_provider_text_change_forces_resynthesis(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(FLAG, "1")

    # First run: warm_callback -> provider has [warm].
    c1 = FakeElevenLabsClient()
    _build(tmp_path, [_v3_segment("warm_callback")], client=c1)
    assert len(c1.calls) == 1

    # Re-run with the SAME role -> reused (no re-spend).
    c2 = FakeElevenLabsClient()
    res2 = _build(tmp_path, [_v3_segment("warm_callback")], client=c2)
    assert len(c2.calls) == 0
    assert res2["narration_outputs"][0]["duration_source"] == "reused"

    # Re-run with a DIFFERENT role -> provider_text_sha changes -> re-synthesis.
    c3 = FakeElevenLabsClient()
    _build(tmp_path, [_v3_segment("contrast_emphasis")], client=c3)
    assert len(c3.calls) == 1


# --------------------------------------------------------------------------- #
# AC-B12 — directed-but-NON-v3 + deferred-role stay byte-identical (no provider).
# --------------------------------------------------------------------------- #
def test_non_v3_directed_run_has_no_provider_text_fields(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(FLAG, "1")
    client = FakeElevenLabsClient()
    seg = {
        "segment_id": "seg-01",
        "slide_id": "slide-01",
        "text": CANONICAL,
        "voice_direction": {"emotional_tone": "warm", "rhetorical_role": "warm_callback"},
    }
    result = _build(tmp_path, [seg], client=client)
    # effective model is the v2 default (no eleven_v3) -> NO compiler call, and the
    # receipt is byte-identical to today (no provider block, no render_mode key).
    assert client.calls[0].text == CANONICAL
    receipt = result["narration_receipts"][0]
    assert "render_mode" not in receipt
    assert "provider_text" not in receipt
    assert "provider_text_sha256" not in receipt


def test_v3_model_with_no_role_sends_canonical_byte_identical(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(FLAG, "1")
    client = FakeElevenLabsClient()
    # eleven_v3 model but NO rhetorical_role -> v2_settings at dispatch (canonical),
    # receipt byte-identical (compiler never ran).
    result = _build(tmp_path, [_v3_segment(None)], client=client)
    assert client.calls[0].text == CANONICAL
    receipt = result["narration_receipts"][0]
    assert "render_mode" not in receipt
    assert "provider_text" not in receipt


# --------------------------------------------------------------------------- #
# S1 — a DEFERRED rhetorical_role on the v3 model must FAIL LOUD (no silent
# downgrade to neutral v2). Pre-flight refuses BEFORE any segment bills.
# --------------------------------------------------------------------------- #
def test_v3_model_with_deferred_role_fails_loud(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(FLAG, "1")
    client = FakeElevenLabsClient()
    with pytest.raises(enrique_act.EnriqueActError) as ei:
        _build(tmp_path, [_v3_segment("curious_pivot")], client=client)
    assert ei.value.tag == "elevenlabs.v3.role.unpopulated"
    # Pre-flight: refused before any synthesis spend.
    assert len(client.calls) == 0


# --------------------------------------------------------------------------- #
# M1 — bracketed canonical ([1]/[Figure 2]/[CO2]) on BOTH paths.
# --------------------------------------------------------------------------- #
BRACKETED = "As shown in [Figure 2], [CO2] rises. See [1]."


def test_v2_directed_path_synthesizes_bracketed_canonical_byte_identical(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv(FLAG, "1")
    client = FakeElevenLabsClient()
    # NON-v3 directed run whose canonical legitimately contains brackets: it must
    # SYNTHESIZE (no raise), send canonical verbatim, and caption it verbatim.
    seg = {
        "segment_id": "seg-01",
        "slide_id": "slide-01",
        "text": BRACKETED,
        "voice_direction": {"emotional_tone": "warm"},
    }
    result = _build(tmp_path, [seg], client=client)
    assert client.calls[0].text == BRACKETED
    vtt = (tmp_path / "assembly-bundle" / "captions" / "seg-01.vtt").read_text(encoding="utf-8")
    assert BRACKETED in vtt  # the [1]/[Figure 2]/[CO2] citations survive in captions.
    receipt = result["narration_receipts"][0]
    assert "render_mode" not in receipt


def test_v3_path_bracketed_canonical_keeps_citations_drops_audio_tag(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv(FLAG, "1")
    client = FakeElevenLabsClient()
    seg = {
        "segment_id": "seg-01",
        "slide_id": "slide-01",
        "text": BRACKETED,
        "voice_direction": {
            "elevenlabs": {"model_id": "eleven_v3"},
            "rhetorical_role": "warm_callback",
        },
    }
    result = _build(tmp_path, [seg], client=client)
    # Provider = [warm] + canonical-with-citations; the [1]/[CO2] survive.
    sent = client.calls[0].text
    assert sent.startswith("[warm] ")
    assert "[Figure 2]" in sent and "[CO2]" in sent and "[1]" in sent
    # Captions keep the citations but NEVER the [warm] audio tag.
    vtt = (tmp_path / "assembly-bundle" / "captions" / "seg-01.vtt").read_text(encoding="utf-8")
    assert BRACKETED in vtt
    assert "[warm]" not in vtt
    receipt = result["narration_receipts"][0]
    assert receipt["render_mode"] == "v3_provider_text"
    assert receipt["provider_text_tags"] == ["[warm]"]  # citations not listed as tags.


# --------------------------------------------------------------------------- #
# S3 — a NON-v3 run must NOT reuse a prior v3 receipt's [tag]-rendered audio.
# --------------------------------------------------------------------------- #
def test_non_v3_plan_refuses_to_reuse_prior_v3_receipt(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv(FLAG, "1")
    # First: a v3 run lays down [warm]-rendered audio + a v3 receipt.
    c1 = FakeElevenLabsClient()
    _build(tmp_path, [_v3_segment("warm_callback")], client=c1)
    assert len(c1.calls) == 1

    # Now a NON-v3 directed run for the SAME segment id: render_mode mismatch must
    # FORCE re-synthesis (the prior audio was rendered from [warm] provider text).
    c2 = FakeElevenLabsClient()
    seg_v2 = {
        "segment_id": "seg-01",
        "slide_id": "slide-01",
        "text": CANONICAL,
        "voice_direction": {"emotional_tone": "warm"},
    }
    _build(tmp_path, [seg_v2], client=c2)
    assert len(c2.calls) == 1  # did NOT reuse the v3 audio.
