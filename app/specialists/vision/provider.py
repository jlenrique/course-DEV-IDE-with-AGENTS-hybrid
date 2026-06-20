"""Thin pinned-endpoint vision provider client."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import httpx

from app.specialists.dispatch_errors import SpecialistDispatchError
from app.specialists.vision.payload_contract import VisionProviderResponse

ENDPOINT_ENV = "VISION_PROVIDER_ENDPOINT"
API_KEY_ENV = "VISION_PROVIDER_API_KEY"
DEFAULT_MODEL_ID = "vision-fixture-v1"
DEFAULT_TIMEOUT_SECONDS = 30.0


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
    """Raised when the pinned endpoint times out."""

    def __init__(self, message: str = "vision provider timed out") -> None:
        super().__init__(message, tag="vision.provider.timeout")


def perceive_png(
    png_path: str | Path,
    *,
    slide_id: str,
    model_id: str = DEFAULT_MODEL_ID,
    endpoint: str | None = None,
    api_key: str | None = None,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    client: httpx.Client | None = None,
) -> VisionProviderResponse:
    """POST PNG bytes to the configured endpoint and parse the pinned response."""

    path = Path(png_path)
    if not path.is_file():
        raise VisionProviderError(
            f"vision input PNG is missing: {path}",
            status_code=None,
            tag="vision.provider.input-missing",
        )
    resolved_endpoint = endpoint or os.getenv(ENDPOINT_ENV)
    if not resolved_endpoint:
        raise VisionProviderError(
            f"{ENDPOINT_ENV} is not configured",
            status_code=None,
            tag="vision.provider.unconfigured",
        )
    headers: dict[str, str] = {}
    resolved_api_key = api_key if api_key is not None else os.getenv(API_KEY_ENV)
    if resolved_api_key:
        headers["Authorization"] = f"Bearer {resolved_api_key}"
    payload = {
        "slide_id": slide_id,
        "model_id": model_id,
        "temperature": 0.0,
        "decode": "greedy",
        "max_tokens": 2048,
    }
    owns_client = client is None
    http = client or httpx.Client(timeout=timeout_seconds)
    try:
        with path.open("rb") as handle:
            response = http.post(
                resolved_endpoint,
                data=payload,
                files={"image": (path.name, handle, "image/png")},
                headers=headers,
            )
    except httpx.TimeoutException as exc:
        raise VisionProviderTimeout() from exc
    except httpx.HTTPError as exc:
        raise VisionProviderError(str(exc), tag="vision.provider.transport") from exc
    finally:
        if owns_client:
            http.close()
    if response.status_code >= 400:
        raise VisionProviderError(
            f"vision provider HTTP {response.status_code}",
            status_code=response.status_code,
        )
    try:
        data: dict[str, Any] = response.json()
    except ValueError as exc:
        raise VisionProviderError("vision provider returned non-JSON response") from exc
    if data.get("slide_id") != slide_id:
        observed_slide_id = data.get("slide_id")
        raise VisionProviderError(
            f"vision provider slide_id mismatch: expected {slide_id!r}, "
            f"got {observed_slide_id!r}",
            tag="vision.provider.contract",
        )
    if data.get("provider_model_id") != model_id:
        raise VisionProviderError(
            "vision provider model mismatch: "
            f"expected {model_id!r}, got {data.get('provider_model_id')!r}",
            tag="vision.provider.contract",
        )
    data.setdefault("source_png_path", str(path))
    return VisionProviderResponse.model_validate(data)


__all__ = [
    "API_KEY_ENV",
    "DEFAULT_MODEL_ID",
    "ENDPOINT_ENV",
    "VisionProviderError",
    "VisionProviderTimeout",
    "perceive_png",
]
