"""Image intake bridge — Texas-side helper for Story 27-3.

Distinct from :mod:`skills.sensory_bridges.scripts.png_to_agent`, which is a
downstream slide-perception bridge consumed by Irene / Vera / Quinn during
production. ``image_to_agent`` is an **intake** helper: it accepts a source
image path from a Texas directive row (``provider: image``) and returns the
canonical ``(title, body, SourceRecord)`` triple produced by every other
``wrangle_*`` function in :mod:`source_wrangler_operations`, so the runner's
``_fetch_source`` dispatch can route images through the same post-fetch
pipeline (extraction validation → extraction report → bundle).

Architecture (Story 27-3, Winston rider):
    New sibling helper. Do NOT extend :mod:`pdf_to_agent` — PDFs have a
    text-extraction model; images require vision / OCR which is a different
    confidence contract. Keeping them separate avoids conditional branches
    in ``extract_pdf``.

Dependency injection (Amelia rider):
    ``ImageAnalyzer`` is a Protocol-style base class with one method,
    :meth:`ImageAnalyzer.analyze`. Tests inject ``FakeImageAnalyzer`` with
    pre-scripted perception output; production uses ``VisionLLMAnalyzer``,
    which is a v1 **stub** that raises :class:`ImageVisionAPIError` with
    operator-facing remediation. Live vision-API integration is a follow-on.

Typed rejection taxonomy (Winston rider):
    :class:`ImageError` (base), :class:`ImageFetchError`,
    :class:`ImageDecodeError`, :class:`ImageOCRFailureError`,
    :class:`ImageVisionAPIError`. The runner's ``_classify_fetch_error``
    maps each to an ``error_kind`` string in the failed-outcome path.

LangGraph portability (Sprint 2 posture):
    No imports from ``marcus.orchestrator.*`` / ``marcus.dispatch.*``. The
    AST guard test asserts this at contract time.
"""

from __future__ import annotations

import hashlib
import io
import struct
from dataclasses import dataclass
from pathlib import Path

BRIDGE_VERSION = "image-intake/1.0"

SUPPORTED_SUFFIXES: frozenset[str] = frozenset({".jpg", ".jpeg", ".png", ".webp"})


class ImageError(Exception):
    """Base class for image-intake errors."""

    def __init__(self, message: str, *, remediation: str | None = None) -> None:
        super().__init__(message)
        self.remediation = remediation

    def __str__(self) -> str:  # pragma: no cover - trivial
        base = super().__str__()
        if self.remediation:
            return f"{base}\n\n{self.remediation}"
        return base


class ImageFetchError(ImageError):
    """Raised when the source image cannot be located, has an unsupported
    suffix, or fails basic byte-level integrity."""


class ImageDecodeError(ImageError):
    """Raised when image bytes are present but the header is corrupt."""


class ImageOCRFailureError(ImageError):
    """Raised when OCR produces empty text and the analyzer deems the
    outcome unrecoverable (distinct from an empty-but-intentional image)."""


class ImageVisionAPIError(ImageError):
    """Raised when the production analyzer needs a vision API key / endpoint
    that is not configured. Carries remediation naming the env var and the
    follow-on story that will wire live vision."""


@dataclass(frozen=True)
class ImagePerception:
    """Analyzer output — the intake bridge's contract with an ImageAnalyzer.

    Shape intentionally narrow: caption + OCR text + element list + layout
    string + optional slide title / text blocks. Downstream code uses these
    fields to assemble the canonical markdown body and to compute the
    image-specific fidelity signals.
    """

    caption: str
    extracted_text: str
    visual_elements: list[dict[str, str]]
    layout_description: str
    slide_title: str = ""
    text_blocks: list[str] | None = None
    confidence: str = "HIGH"
    confidence_rationale: str = ""


class ImageAnalyzer:
    """Protocol-style base class for vision/OCR backends.

    Production: :class:`VisionLLMAnalyzer` (stub in v1, raises
    :class:`ImageVisionAPIError`). Tests: ``FakeImageAnalyzer`` substitutes
    pre-scripted :class:`ImagePerception` payloads.
    """

    def analyze(self, path: Path) -> ImagePerception:  # pragma: no cover - abstract
        raise NotImplementedError


class VisionLLMAnalyzer(ImageAnalyzer):
    """v1 stub — surfaces remediation text pointing at the follow-on story.

    Intentional: Story 27-3 lands the provider *surface* (directive routing,
    extraction-report integration, transform-registry row). Live vision
    integration ships in a follow-on gated on key availability + cassette
    strategy. Tests substitute :class:`ImageAnalyzer` implementations via DI.
    """

    def analyze(self, path: Path) -> ImagePerception:
        raise ImageVisionAPIError(
            f"No production vision analyzer is configured for {path.name!r}.",
            remediation=(
                "Image intake requires an ImageAnalyzer implementation.\n"
                "Remediation:\n"
                "  1. For production runs: supply an analyzer via the runner's "
                "DI seam (src['_image_analyzer']) or await the live-vision "
                "follow-on story (Story 27-3b).\n"
                "  2. For ad-hoc trials: pre-compute perception and inject via "
                "a FakeImageAnalyzer-style harness.\n"
                "  3. Verify the image is truly visual-primary — if it is "
                "incidental context, route via OPTIONAL_CONTEXT_ASSETS in "
                "run-constants.yaml instead."
            ),
        )


@dataclass(frozen=True)
class SourceRecord:
    """Re-export of the source_wrangler_operations SourceRecord contract.

    This local dataclass exists only to keep this module import-free of the
    hyphenated ``skills/bmad-agent-texas/`` path (which blocks normal
    ``from ... import`` resolution). The runner adapts between the two by
    casting to the canonical type — both share the same field shape.
    """

    kind: str
    ref: str
    note: str


# ---------------------------------------------------------------------------
# Header integrity + provenance helpers
# ---------------------------------------------------------------------------


_JPEG_MAGIC = b"\xff\xd8\xff"
_PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
_WEBP_RIFF = b"RIFF"
_WEBP_WEBP = b"WEBP"


def _check_header(suffix: str, data: bytes) -> None:
    """Raise :class:`ImageDecodeError` if the header does not match the suffix.

    Intentionally minimal — we are guarding against the "binary decode"
    crash, not doing full decode. Full decode is the analyzer's job.
    """
    if suffix in (".jpg", ".jpeg"):
        if not data.startswith(_JPEG_MAGIC):
            raise ImageDecodeError(
                f"Image header does not match JPEG signature (suffix={suffix})."
            )
    elif suffix == ".png":
        if not data.startswith(_PNG_MAGIC):
            raise ImageDecodeError(
                f"Image header does not match PNG signature (suffix={suffix})."
            )
    elif suffix == ".webp" and not (
        len(data) >= 12 and data[0:4] == _WEBP_RIFF and data[8:12] == _WEBP_WEBP
    ):
        raise ImageDecodeError(
            f"Image header does not match WebP RIFF signature (suffix={suffix})."
        )


def _dimensions(suffix: str, data: bytes) -> tuple[int, int] | None:
    """Best-effort width/height from image header; return None on failure.

    Parses just enough bytes to extract dimensions without depending on Pillow
    (optional). Used for provenance enrichment; failures are non-fatal.
    """
    try:
        if suffix == ".png":
            # PNG: width/height at bytes 16..24 (big-endian u32 each).
            if len(data) >= 24 and data[12:16] == b"IHDR":
                w, h = struct.unpack(">II", data[16:24])
                return int(w), int(h)
            return None
        if suffix in (".jpg", ".jpeg"):
            stream = io.BytesIO(data)
            if stream.read(2) != b"\xff\xd8":
                return None
            while True:
                byte = stream.read(1)
                while byte == b"\xff":
                    byte = stream.read(1)
                marker = byte
                if not marker:
                    return None
                if marker[0] in (0xC0, 0xC1, 0xC2):  # SOF0/1/2
                    stream.read(3)  # length(2) + precision(1)
                    h, w = struct.unpack(">HH", stream.read(4))
                    return int(w), int(h)
                length_bytes = stream.read(2)
                if len(length_bytes) < 2:
                    return None
                length = struct.unpack(">H", length_bytes)[0]
                stream.read(length - 2)
        if suffix == ".webp":
            # VP8L simple header parse. Non-fatal if it fails. Needs at
            # least 25 bytes to reach the 4 dimension bytes at offset 21-24.
            if len(data) >= 25 and data[12:16] == b"VP8L":
                sig = data[20]
                if sig == 0x2F:
                    b0, b1, b2, b3 = data[21:25]
                    w = 1 + (((b1 & 0x3F) << 8) | b0)
                    h = 1 + (((b3 & 0x0F) << 10) | (b2 << 2) | ((b1 & 0xC0) >> 6))
                    return int(w), int(h)
            return None
    except Exception:
        return None
    return None


def _sha256_prefix(data: bytes, length: int = 12) -> str:
    return hashlib.sha256(data).hexdigest()[:length]


# ---------------------------------------------------------------------------
# Fidelity assessment — image-specific mapping into the existing
# ExtractionReport shape (no schema bifurcation per AC-4)
# ---------------------------------------------------------------------------


def assess_image_fidelity(perception: ImagePerception) -> tuple[str, int]:
    """Compute (structural_fidelity, perceived_content_words) for image sources.

    Mapping logic (Amelia rider — explicit thresholds):
      - ``structural_fidelity = "high"`` when the image exposes clear
        structure: ≥2 visual elements AND ≥20 OCR words AND non-empty
        layout description AND confidence HIGH.
      - ``"medium"`` when either (a) ≥1 visual element AND ≥10 OCR words, or
        (b) ≥30 OCR words with any layout.
      - ``"low"`` when only sparse signals survive — any OCR text OR any
        visual element, but not both in quantity.
      - ``"none"`` when nothing perceivable was produced.

    ``perceived_content_words`` is the OCR word count, inflated by element
    count × 3 (each identified element contributes "approximately 3 words
    of meaning" for completeness-ratio purposes). This never exceeds the
    effective floor for image sources (60 words) unless the OCR itself
    already exceeds it.
    """
    ocr_words = len(perception.extracted_text.split())
    element_count = len(perception.visual_elements)
    has_layout = bool(perception.layout_description.strip())
    confidence = (perception.confidence or "").upper()

    if (
        element_count >= 2
        and ocr_words >= 20
        and has_layout
        and confidence == "HIGH"
    ):
        fidelity = "high"
    elif (element_count >= 1 and ocr_words >= 10) or (ocr_words >= 30 and has_layout):
        fidelity = "medium"
    elif ocr_words > 0 or element_count > 0:
        fidelity = "low"
    else:
        fidelity = "none"

    perceived_content_words = ocr_words + (element_count * 3)
    return fidelity, perceived_content_words


# ---------------------------------------------------------------------------
# Body assembly — canonical markdown layout consumed by Irene downstream
# ---------------------------------------------------------------------------


def _format_body(
    *,
    title: str,
    perception: ImagePerception,
    structural_fidelity: str,
    completeness_hint: str,
) -> str:
    lines: list[str] = [f"# {title}", ""]

    caption = (perception.caption or "").strip()
    if caption:
        lines.extend(["## Caption", "", caption, ""])

    extracted = (perception.extracted_text or "").strip()
    lines.extend(["## Detected text (OCR)", ""])
    if extracted:
        lines.extend([extracted, ""])
    else:
        lines.extend(["_(no text detected)_", ""])

    lines.extend(["## Visual elements", ""])
    if perception.visual_elements:
        for element in perception.visual_elements:
            etype = str(element.get("type", "")).strip() or "element"
            edesc = str(element.get("description", "")).strip()
            if edesc:
                lines.append(f"- **{etype}** — {edesc}")
            else:
                lines.append(f"- **{etype}**")
        lines.append("")
    else:
        lines.extend(["_(no visual elements identified)_", ""])

    layout = (perception.layout_description or "").strip()
    lines.extend(["## Layout", ""])
    if layout:
        lines.extend([layout, ""])
    else:
        lines.extend(["_(layout not described)_", ""])

    lines.extend(
        [
            "## Tier classification",
            "",
            f"- **visual_structural_fidelity:** {structural_fidelity}",
            f"- **visual_completeness:** {completeness_hint}",
            f"- **confidence:** {perception.confidence}",
            f"- **bridge_version:** {BRIDGE_VERSION}",
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


# ---------------------------------------------------------------------------
# Public entry point — wrangle_local_image (mirrors wrangle_local_pdf signature)
# ---------------------------------------------------------------------------


def wrangle_local_image(
    path: str | Path,
    *,
    analyzer: ImageAnalyzer | None = None,
) -> tuple[str, str, SourceRecord]:
    """Intake a local image file and produce the wrangle_* contract.

    :param path: Path to the image on disk.
    :param analyzer: ImageAnalyzer implementation. Defaults to
        :class:`VisionLLMAnalyzer`, which currently raises
        :class:`ImageVisionAPIError`. Tests substitute a FakeImageAnalyzer.
    :returns: ``(title, body, SourceRecord)`` — identical shape to
        :func:`source_wrangler_operations.wrangle_local_pdf` and siblings so
        the runner's ``_fetch_source`` can route image items through the
        same post-fetch pipeline.
    :raises ImageFetchError: File missing / unsupported suffix.
    :raises ImageDecodeError: Header bytes do not match the declared format.
    :raises ImageVisionAPIError: Default analyzer invoked without a vision
        backend configured.
    :raises ImageOCRFailureError: Analyzer signals unrecoverable OCR failure.
    """
    p = Path(path)
    if not p.is_file():
        raise ImageFetchError(
            f"Image file not found: {p}",
            remediation=(
                "Verify the directive's 'locator' path exists and is readable "
                "from the runner's working directory."
            ),
        )

    suffix = p.suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        raise ImageFetchError(
            f"Unsupported image suffix {suffix!r} (got {p.name!r}).",
            remediation=(
                "Supported suffixes: "
                f"{sorted(SUPPORTED_SUFFIXES)}. For non-image sources, use "
                "provider='local_file' (text), 'pdf', 'docx', 'md', 'url', "
                "'notion_mcp', or 'box'."
            ),
        )

    data = p.read_bytes()
    if len(data) < 16:
        raise ImageDecodeError(
            f"Image file is too small to be valid ({len(data)} bytes)."
        )
    _check_header(suffix, data)

    active_analyzer = analyzer if analyzer is not None else VisionLLMAnalyzer()
    perception = active_analyzer.analyze(p)

    fidelity, perceived_words = assess_image_fidelity(perception)
    # Completeness hint is a human-readable label; the numeric completeness
    # ratio is recomputed downstream by extraction_validator from the body
    # itself (where _WORDS_PER_PAGE["image"] = 60 is the floor).
    if fidelity == "high":
        completeness_hint = "full"
    elif fidelity == "medium":
        completeness_hint = "partial"
    elif fidelity == "low":
        completeness_hint = "sparse"
    else:
        completeness_hint = "none"

    title = p.stem.replace("_", " ") if p.stem else "Image"

    if fidelity == "none":
        raise ImageOCRFailureError(
            f"Analyzer produced no perceivable signal for {p.name!r} "
            f"(no caption, no text, no elements, no layout).",
            remediation=(
                "The image appears to be blank, unreadable, or entirely "
                "abstract. Options:\n"
                "  1. Verify the file is the intended source.\n"
                "  2. Provide a manual caption via an accompanying .md file "
                "using provider='md' with role='visual-supplementary'.\n"
                "  3. Try a higher-resolution export of the same image."
            ),
        )

    body = _format_body(
        title=title,
        perception=perception,
        structural_fidelity=fidelity,
        completeness_hint=completeness_hint,
    )

    dims = _dimensions(suffix, data)
    dim_note = f"{dims[0]}x{dims[1]}" if dims else "unknown"
    sha = _sha256_prefix(data)

    note = (
        f"image intake via {BRIDGE_VERSION}; "
        f"sha256={sha}; suffix={suffix}; size={len(data)}; "
        f"dimensions={dim_note}; fidelity={fidelity}; "
        f"perceived_words={perceived_words}; confidence={perception.confidence}"
    )
    rec = SourceRecord(
        kind="image_source",
        ref=f"image://{sha}",
        note=note,
    )
    return title, body, rec
