"""Live ``gpt-5.5`` multimodal vision perceiver.

Replaces the prior pinned-endpoint fixture stub (``vision-fixture-v1`` POSTed
to an unconfigured ``VISION_PROVIDER_ENDPOINT``) with a genuine multimodal
OpenAI call via the house adapter (``app.models.adapter.make_chat_model`` →
``ChatOpenAI``). The PNG is base64-encoded into an ``image_url`` content block
on a ``HumanMessage``; the perception prompt demands the
:class:`~app.specialists.vision.payload_contract.VisionProviderResponse` JSON
shape, which is parsed + validated. Malformed JSON is retried (bounded, ≤3)
in-call; provider/SDK exceptions are mapped onto the EXISTING tagged errors so
``_act.py::_is_retryable_provider_error`` is untouched.

**Bbox provenance (AC-5):** ``visual_elements[].bbox`` are APPROXIMATE
normalized region estimates in ``[x1, y1, x2, y2]`` form, each coordinate in
``0..1``. They are LLM-estimated and coarse — the deterministic reading-path
classifier (``scripts.utilities.reading_path_classifier``) only buckets centers
into thirds, so sub-third precision is neither produced nor consumed.

``perceive_png``'s public signature ``(png_path, *, slide_id, model_id=...,
timeout_seconds=...)`` is preserved so ``_act.py`` is unchanged at the call
site. The ``endpoint``/``api_key``/``client`` kwargs and the
``ENDPOINT_ENV``/``API_KEY_ENV``/``DEFAULT_MODEL_ID`` constants are retired.
"""

from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any

import httpx
import openai
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import ValidationError

from app.models.adapter import make_chat_model
from app.runtime.llm_batch.prompt_cache import resolve_vision_prompt_cache_key
from app.specialists.dispatch_errors import SpecialistDispatchError
from app.specialists.vision.payload_contract import VisionProviderResponse

DEFAULT_MODEL_ID = "gpt-5.5"
DEFAULT_TIMEOUT_SECONDS = 60.0
MAX_JSON_REPAIR_ATTEMPTS = 3
VISION_SPECIALIST_ID = "vision"

PERCEPTION_SYSTEM_MESSAGE = (
    "You are a precise slide-perception engine. You look at a single rendered "
    "presentation slide image and report ONLY what is visually present — never "
    "invent content. You return a strict JSON object and nothing else."
)


class VisionProviderError(SpecialistDispatchError):
    """Raised when the vision provider returns an unsuccessful response."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        tag: str = "vision.provider.error",
    ) -> None:
        super().__init__(message, tag=tag)
        self.status_code = status_code


class VisionProviderTimeout(VisionProviderError):  # noqa: N818
    """Raised when the live multimodal call times out."""

    def __init__(self, message: str = "vision provider timed out") -> None:
        super().__init__(message, tag="vision.provider.timeout")


def _perception_prompt(slide_id: str) -> str:
    """Build the deterministic perception instruction demanding the response shape."""
    return (
        f"Perceive the slide image and return a single JSON object describing ONLY "
        f"what is visually present. Echo the slide_id verbatim as {slide_id!r}.\n\n"
        "Return EXACTLY this JSON shape (no prose, no markdown fences):\n"
        "{\n"
        f'  "slide_id": "{slide_id}",\n'
        '  "confidence": "HIGH" | "LOW",   // HIGH only if you can read the slide clearly\n'
        '  "coverage": "perceived" | "low-confidence" | "not-covered",\n'
        '  "confidence_score": 0.0..1.0,\n'
        '  "slide_title": "the slide title text, or empty string",\n'
        '  "extracted_text": "ALL legible text on the slide, verbatim, space-joined",\n'
        '  "layout_description": "one or two sentences describing the spatial layout",\n'
        '  "text_blocks": ["each distinct block of text as a string"],\n'
        '  "visual_elements": [\n'
        "    {\n"
        '      "id": "short stable id",\n'
        '      "kind": "title|callout|stat|photo|chart|diagram|icon|bullet|logo|...",\n'
        '      "text": "the text inside this element, or empty string",\n'
        '      "role_tier": "1" | "2" | "2_5" | "3" | "4",\n'
        '      "role_tier_reason": "short visual evidence for the tier",\n'
        '      "bbox": [x1, y1, x2, y2]\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        "IMPORTANT about bbox: each bbox is an APPROXIMATE normalized region "
        "estimate. x1,y1 is the top-left corner and x2,y2 the bottom-right corner, "
        "each a fraction of the slide in [0,1] (x rightward, y downward), with "
        "x1<x2 and y1<y2. Coarse thirds-level accuracy is sufficient — do NOT "
        "fabricate false precision. Include one visual_element per distinct "
        "perceptible region (title, each stat/callout, each photo/chart, etc.). "
        "For every visual_element, set role_tier using the eye-verb rubric "
        "feel/glance/confirm/trace/tag: 1=decorative/evocative background the "
        "viewer only feels; 2=illustrative supporting image the viewer glances at; "
        "2_5=evidentiary chart/table/exhibit the viewer confirms against nearby "
        "caption/text; 3=instructional technical diagram the viewer must trace, "
        "only when internal labels are visible; 4=pointer/icon/logo/tag the viewer "
        "uses as a label or navigation chip. Hard gates: kind icon/logo with area "
        "<0.05 is tier 4; tier 3 is forbidden when no internal labels are visible; "
        "edge-bleed image with overlapping text and no internal labels is a strong "
        "tier 1 prior. "
        "If you cannot read the slide, set confidence to LOW and coverage to "
        "low-confidence."
    )


def build_perception_openai_messages(
    png_path: str | Path,
    *,
    slide_id: str,
) -> list[dict[str, Any]]:
    """OpenAI chat-completions messages for one PNG (shared by realtime + Batch JSONL).

    Stable order: system, then user content with **text before** ``image_url``.
    Does not change ``perceive_png`` semantics — realtime wraps these into
    LangChain messages; Batch embeds the same dicts in JSONL bodies.
    """

    path = Path(png_path)
    if not path.is_file():
        raise VisionProviderError(
            f"vision input PNG is missing: {path}",
            status_code=None,
            tag="vision.provider.input-missing",
        )
    image_b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    data_uri = f"data:image/png;base64,{image_b64}"
    return [
        {"role": "system", "content": PERCEPTION_SYSTEM_MESSAGE},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": _perception_prompt(slide_id)},
                {"type": "image_url", "image_url": {"url": data_uri}},
            ],
        },
    ]


def _decode_content(response: Any) -> str:
    """Extract the assistant text content from a LangChain chat response."""
    content = getattr(response, "content", response)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        # Multimodal responses may return a list of content blocks.
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                text = block.get("text") or block.get("content")
                if isinstance(text, str):
                    parts.append(text)
        return "".join(parts)
    return str(content)


def _strip_json(raw: str) -> str:
    """Tolerate fenced ```json blocks and prose preamble; return the JSON slice."""
    stripped = raw.strip()
    if "```" in stripped:
        fence = "```json" if "```json" in stripped else "```"
        start = stripped.find(fence) + len(fence)
        end = stripped.find("```", start)
        if end > start:
            stripped = stripped[start:end].strip()
    # Fall back to the outermost { ... } if extra prose surrounds it.
    if not stripped.startswith("{"):
        first = stripped.find("{")
        last = stripped.rfind("}")
        if first != -1 and last > first:
            stripped = stripped[first : last + 1]
    return stripped


def _parse_response(
    raw: str, *, slide_id: str, model_id: str, source_png_path: str
) -> VisionProviderResponse:
    """Parse + validate raw model text into a VisionProviderResponse.

    Raises ``VisionProviderError`` (tag ``vision.provider.malformed-json``) on
    JSON decode failure or schema-validation failure so the caller's bounded
    repair loop can retry through the existing taxonomy.
    """
    try:
        data: Any = json.loads(_strip_json(raw))
    except ValueError as exc:
        raise VisionProviderError(
            f"vision model returned non-JSON content: {exc}",
            tag="vision.provider.malformed-json",
        ) from exc
    if not isinstance(data, dict):
        raise VisionProviderError(
            "vision model JSON was not an object",
            tag="vision.provider.malformed-json",
        )
    # A slide_id mismatch means the response is cross-wired to the wrong image:
    # fail loud (NON-retryable contract violation) rather than silently
    # overwrite — masking a cross-wired image/response violates no-fakes.
    if data.get("slide_id") != slide_id:
        raise VisionProviderError(
            f"vision model echoed wrong slide_id {data.get('slide_id')!r} "
            f"(expected {slide_id!r}); response is cross-wired to the wrong image",
            tag="vision.provider.contract",
        )
    # provider_model_id and source_png_path are CODE-controlled — never trust a
    # model-emitted value (overwrite, do not setdefault).
    data["provider_model_id"] = model_id
    data["source_png_path"] = source_png_path
    data.setdefault("provenance", "png-grounded")
    try:
        return VisionProviderResponse.model_validate(data)
    except ValidationError as exc:
        raise VisionProviderError(
            f"vision model JSON failed VisionProviderResponse validation: {exc}",
            tag="vision.provider.malformed-json",
        ) from exc


def _map_sdk_exception(exc: Exception) -> VisionProviderError:
    """Map an openai/httpx SDK exception onto the existing tagged-error taxonomy."""
    if isinstance(exc, (openai.APITimeoutError, httpx.TimeoutException)):
        return VisionProviderTimeout()
    # RateLimitError is an APIStatusError subclass — check it FIRST so a 429
    # always resolves with status_code=429 even when APIStatusError.status_code
    # is None. (S5: the generic APIStatusError branch below would otherwise
    # shadow this subclass and make it an unreachable dead branch.)
    if isinstance(exc, openai.RateLimitError):
        status = getattr(getattr(exc, "response", None), "status_code", None) or 429
        return VisionProviderError(
            f"vision provider rate-limited: {exc}",
            status_code=status,
        )
    if isinstance(exc, openai.APIStatusError):
        return VisionProviderError(
            f"vision provider HTTP {exc.status_code}",
            status_code=exc.status_code,
        )
    if isinstance(exc, (openai.APIConnectionError, httpx.HTTPError)):
        return VisionProviderError(str(exc), tag="vision.provider.transport")
    return VisionProviderError(str(exc), tag="vision.provider.transport")


def perceive_png(
    png_path: str | Path,
    *,
    slide_id: str,
    model_id: str = DEFAULT_MODEL_ID,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> VisionProviderResponse:
    """Make a live ``gpt-5.5`` multimodal call over the PNG and parse the response.

    The PNG bytes are base64-encoded into an ``image_url`` data-URI content
    block on a ``HumanMessage`` alongside the structured perception prompt; the
    model is resolved + constructed through the house ``make_chat_model``
    adapter (``ChatOpenAI``). The response JSON is parsed + validated against
    :class:`VisionProviderResponse`. Malformed JSON is repaired with a bounded
    in-call retry (≤ :data:`MAX_JSON_REPAIR_ATTEMPTS`); provider/SDK exceptions
    map onto the existing tagged errors (``VisionProviderTimeout``,
    ``status_code``-bearing ``VisionProviderError``,
    ``tag="vision.provider.transport"``).
    """
    path = Path(png_path)
    if not path.is_file():
        raise VisionProviderError(
            f"vision input PNG is missing: {path}",
            status_code=None,
            tag="vision.provider.input-missing",
        )

    openai_messages = build_perception_openai_messages(path, slide_id=slide_id)
    messages = [
        SystemMessage(content=openai_messages[0]["content"]),
        HumanMessage(content=openai_messages[1]["content"]),
    ]

    try:
        handle = make_chat_model(
            VISION_SPECIALIST_ID,
            per_call_override=model_id,
            temperature=0.0,
        )
    except VisionProviderError:
        raise
    except Exception as exc:  # noqa: BLE001 — map resolution/construction onto taxonomy
        # A ModelResolutionError (RuntimeError from selector.resolve) or any
        # other construction failure must NOT escape unmapped past _act's
        # retry/error-pause boundary. Map to a NON-retryable tagged error so
        # _act routes it to error-pause (NOT in the retryable set, no
        # status_code) — same uncaught-error class the P2-4a fix eliminated.
        raise VisionProviderError(
            f"vision model resolution/construction failed: {exc}",
            status_code=None,
            tag="vision.provider.model-resolution",
        ) from exc
    # B5: shared prompt_cache_key (stable across slides; same derivation as batch).
    # Pass it as a first-class Completions param (openai SDK >=1.x accepts
    # prompt_cache_key directly). `.bind(model_kwargs=...)` was wrong: LangChain
    # forwards a bound `model_kwargs` as a literal create() kwarg, which the SDK
    # rejects ("unexpected keyword argument 'model_kwargs'") — surfaced by the
    # 35.7 live E2E proofing run at node 07G.
    cache_key = resolve_vision_prompt_cache_key(mode="realtime")
    bind_kwargs: dict[str, Any] = {"timeout": timeout_seconds}
    if cache_key:
        bind_kwargs["prompt_cache_key"] = cache_key
    chat = handle.chat.bind(**bind_kwargs)

    last_error: VisionProviderError | None = None
    for _attempt in range(1, MAX_JSON_REPAIR_ATTEMPTS + 1):
        try:
            response = chat.invoke(messages)
        except VisionProviderError:
            raise
        except Exception as exc:  # noqa: BLE001 — mapped onto the taxonomy below
            raise _map_sdk_exception(exc) from exc
        raw = _decode_content(response)
        try:
            return _parse_response(
                raw,
                slide_id=slide_id,
                model_id=model_id,
                source_png_path=str(path),
            )
        except VisionProviderError as exc:
            # Only malformed-JSON failures are repaired in-call; any other tag
            # is a hard contract failure that propagates immediately.
            if exc.tag != "vision.provider.malformed-json":
                raise
            last_error = exc
            # S2: at temperature=0 re-invoking IDENTICAL messages just repeats
            # the same malformed response (wasted multimodal calls). Append a
            # repair instruction so the next attempt has a real chance and the
            # extra="forbid" hallucinated-key case is corrected too.
            messages = [
                *messages,
                HumanMessage(
                    content=(
                        "Your previous response was not valid JSON matching the "
                        f"required schema (error: {exc}). Return ONLY the JSON "
                        "object, no prose, no markdown fences, no extra keys."
                    )
                ),
            ]
    if last_error is None:  # pragma: no cover — loop always sets last_error on failure
        raise VisionProviderError(
            "vision repair loop exited without a result",
            tag="vision.provider.malformed-json",
        )
    raise last_error


__all__ = [
    "DEFAULT_MODEL_ID",
    "DEFAULT_TIMEOUT_SECONDS",
    "MAX_JSON_REPAIR_ATTEMPTS",
    "PERCEPTION_SYSTEM_MESSAGE",
    "VisionProviderError",
    "VisionProviderTimeout",
    "build_perception_openai_messages",
    "perceive_png",
    "_parse_response",
    "_perception_prompt",
]
