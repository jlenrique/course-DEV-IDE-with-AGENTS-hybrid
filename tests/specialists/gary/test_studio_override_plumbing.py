"""studio-via-api-override-plumbing (step 1) — resolver + dispatch + prompt steer.

Teaches the production Gamma Studio path to carry per-record ``theme_id`` +
``image_model`` overrides on a base full-bleed from-template deck. RED-first.

Every assertion targets the NEXT layer's observed input:
- resolver tests assert the resolved dict the DISPATCH will read;
- dispatch tests assert the kwargs captured at the GammaClient boundary (the
  client already serializes ``theme_id``/``image_options`` to ``themeId``/
  ``imageOptions`` on the wire — confirmed, not modified here);
- the steer test asserts the outbound prompt string the model receives.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.specialists.gary import _act as gary_act
from app.specialists.gary._act import GammaDispatchError
from app.specialists.gary.styleguide_library import StyleguideError, expand_record

_REPO = Path(__file__).resolve().parents[3]
_STUDIO_PNG = (
    _REPO
    / "_bmad-output"
    / "implementation-artifacts"
    / "studio-mode-evidence"
    / "STUDIO-success-1-innovators-mindset.png"
)


def _studio_record(**template_extra: object) -> dict[str, object]:
    return {
        "production_mode": "studio",
        "studio_template": {"gamma_id": "g_test123", **template_extra},
        "presentation": {"narrative": {"triad_rationale": "x"}},
    }


class RecordingStudioClient:
    """Fake Gamma client that records exactly what kwargs the dispatch passes to
    ``generate_from_template`` (the next-layer input); ``**kwargs`` so a NOT-passed
    override is observably ABSENT, not merely None."""

    def __init__(self) -> None:
        self.template_calls: list[dict[str, object]] = []

    def generate_from_template(
        self, template_id: str, prompt: str, **kwargs: object
    ) -> dict[str, object]:
        self.template_calls.append(
            {"template_id": template_id, "prompt": prompt, "kwargs": dict(kwargs)}
        )
        return {"generationId": f"studio-{len(self.template_calls)}"}

    def wait_for_generation(self, generation_id: str) -> dict[str, object]:
        return {"exportUrl": "https://example.invalid/studio.png"}


def _run_studio_dispatch(client, variant_settings, tmp_path, monkeypatch):
    assert _STUDIO_PNG.exists(), "real Studio 16:9 fixture missing"
    monkeypatch.setattr(
        gary_act, "download_export", lambda url, *, output_dir, filename: str(_STUDIO_PNG)
    )
    slides = [{"slide_id": "s1", "title": "Only Topic Here"}]
    calls: list[str] = []
    return gary_act._generate_studio_variant(
        client, slides, variant_settings, tmp_path, "A", calls
    )


# --- Seam 1: RESOLVER -------------------------------------------------------- #
def test_resolver_emits_studio_overrides_when_present() -> None:
    """(1) resolver emits studio_template.theme_id + .image_model when present."""
    resolved = expand_record(
        _studio_record(theme_id="theme-abc", image_model="recraft-v3"), name="t"
    )
    assert resolved["studio_theme_id"] == "theme-abc"
    assert resolved["studio_image_model"] == "recraft-v3"


def test_resolver_fail_loud_on_non_string_theme_id() -> None:
    """(F1) a PRESENT-but-non-string studio_template.theme_id fails loud rather than
    coercing int 123 -> the garbage string '123' (mirrors _expand_api's contract)."""
    with pytest.raises(StyleguideError):
        expand_record(_studio_record(theme_id=123), name="t")


def test_resolver_fail_loud_on_non_string_image_model() -> None:
    """(F1) a PRESENT-but-non-string studio_template.image_model fails loud rather than
    coercing to a garbage string."""
    with pytest.raises(StyleguideError):
        expand_record(_studio_record(image_model=123), name="t")


def test_resolver_does_not_invent_studio_overrides_when_absent() -> None:
    """(2) resolver does NOT invent overrides when absent — keys absent, no default."""
    resolved = expand_record(_studio_record(), name="t")
    assert "studio_theme_id" not in resolved
    assert "studio_image_model" not in resolved
    assert resolved == {"production_mode": "studio", "studio_template_id": "g_test123"}


# --- Seam 2: DISPATCH -------------------------------------------------------- #
def test_dispatch_sends_theme_id_and_image_options(tmp_path, monkeypatch) -> None:
    """(3) THE load-bearing test: dispatch pulls the resolved overrides and passes
    theme_id=<val> + image_options={'model': <val>} to the client (which serializes
    them to themeId / imageOptions on the wire)."""
    client = RecordingStudioClient()
    _run_studio_dispatch(
        client,
        {
            "studio_template_id": "g_x",
            "studio_theme_id": "theme-abc",
            "studio_image_model": "recraft-v3",
        },
        tmp_path,
        monkeypatch,
    )
    kwargs = client.template_calls[0]["kwargs"]
    assert kwargs["theme_id"] == "theme-abc"
    assert kwargs["image_options"] == {"model": "recraft-v3"}


def test_dispatch_omits_overrides_cleanly_when_unset(tmp_path, monkeypatch) -> None:
    """(4) dispatch omits cleanly — the recorded kwargs carry NO theme_id/
    image_options keys (absent, not null); do not send theme_id='' or
    image_options={'model': None}."""
    client = RecordingStudioClient()
    _run_studio_dispatch(client, {"studio_template_id": "g_x"}, tmp_path, monkeypatch)
    kwargs = client.template_calls[0]["kwargs"]
    assert "theme_id" not in kwargs
    assert "image_options" not in kwargs


def test_dispatch_rejects_bogus_image_model_before_any_paid_call(
    tmp_path, monkeypatch
) -> None:
    """(F2) studio_image_model is a valid GAMMA_SETTING_KEY so it can arrive per-variant
    WITHOUT passing the offline write-gate; a bogus model must fail loud BEFORE any paid
    generation — assert the client recorded ZERO template calls."""
    client = RecordingStudioClient()
    with pytest.raises(GammaDispatchError):
        _run_studio_dispatch(
            client,
            {"studio_template_id": "g_x", "studio_image_model": "bogus-model"},
            tmp_path,
            monkeypatch,
        )
    assert client.template_calls == []


# --- A6: English-only steer inside the outbound prompt ----------------------- #
def test_studio_outbound_prompt_contains_english_only_steer(tmp_path, monkeypatch) -> None:
    """(A6) the English-only text steer is composed INSIDE the per-slide prompt that
    actually reaches the model — asserted on the captured outbound prompt string."""
    client = RecordingStudioClient()
    _run_studio_dispatch(client, {"studio_template_id": "g_x"}, tmp_path, monkeypatch)
    prompt = client.template_calls[0]["prompt"]
    assert gary_act._STUDIO_ENGLISH_ONLY_STEER in prompt
    assert "English" in prompt
