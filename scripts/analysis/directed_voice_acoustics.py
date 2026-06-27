"""Deterministic acoustic-analysis harness + judge for P5 directed-voice (Step 5).

This is a **pure, deterministic, offline** harness that backs MUR-4 (the
"materially different" bar from
``p5-directed-voice-arc-strawman-2026-06-27.md`` §F). It answers one question
with a *numeric* comparison rather than a vibe: did a directed ``voice_direction``
produce a clip that is materially different from the baseline on a scalar the
direction was *designed* to move?

Two pieces:

1. :func:`analyze_clip` — decode an audio file (MP3/WAV/...) to mono PCM via the
   ``imageio_ffmpeg`` bundled ffmpeg binary, load into numpy, and report the
   robust primary scalars ``duration_s``, ``rms``, ``peak``. No network, no
   librosa/scipy — only numpy + the bundled ffmpeg.

2. :func:`materially_different` — the deterministic judge. Given a *control
   pair* (same text + SAME direction rendered twice = the TTS-nondeterminism
   floor ``F``) and a *treatment pair* (the two distinct directions), on a
   scalar the direction was designed to move, return a verdict that PASSES iff
   ``|scalar(treatment_B) - scalar(treatment_A)| > k * F`` with ``k`` fixed at
   ``3`` **before** any live run (first-run-stands; no retry-to-green).

Targeted scalars (the direction dimension -> the scalar it moves):
- pace (slower/faster) -> ``duration_s`` (slower speech = longer clip),
- energy (low/high)    -> ``rms`` (higher energy/style + lower stability = louder).
"""

from __future__ import annotations

import subprocess
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any, NamedTuple

import numpy as np

# Fixed BEFORE any live run (MUR-4 / first-run-stands). The treatment delta on a
# targeted scalar must exceed k * F (the same-text+same-direction floor).
DEFAULT_K = 3

# Decode every clip to mono PCM at this rate. ffmpeg resamples while preserving
# real duration, so duration_s = n_samples / _DECODE_RATE is correct regardless
# of the source container's native rate.
_DECODE_RATE = 44100
_PCM_FULL_SCALE = 32768.0  # s16le full scale (2**15)


class ClipAnalysis(NamedTuple):
    """Deterministic acoustic scalars for one clip."""

    duration_s: float
    rms: float
    peak: float
    n_samples: int
    sample_rate: int


class Verdict(NamedTuple):
    """The deterministic judge's numeric verdict (no vibes)."""

    scalar: str
    k: int
    floor: float  # F = |scalar(A) - scalar(A')| (control: same text+direction x2)
    threshold: float  # k * F
    control_a: float
    control_a_prime: float
    treatment_a: float
    treatment_b: float
    delta: float  # |scalar(B) - scalar(A)| on the treatment pair
    passed: bool  # delta > threshold


def _ffmpeg_exe() -> str:
    import imageio_ffmpeg

    return imageio_ffmpeg.get_ffmpeg_exe()


def decode_to_mono_float(path: str | Path) -> tuple[np.ndarray, int]:
    """Decode an audio file to a mono float32 numpy array in [-1.0, 1.0].

    Uses the bundled ffmpeg binary to emit signed 16-bit little-endian mono PCM
    at ``_DECODE_RATE`` on stdout, then loads it into numpy. Deterministic and
    offline. Raises on a decode failure (never silently returns empty audio for
    a non-empty file).
    """
    src = Path(path)
    if not src.is_file():
        raise FileNotFoundError(f"clip not found: {src}")
    cmd = [
        _ffmpeg_exe(),
        "-nostdin",
        "-v",
        "error",
        "-i",
        str(src),
        "-f",
        "s16le",
        "-acodec",
        "pcm_s16le",
        "-ac",
        "1",
        "-ar",
        str(_DECODE_RATE),
        "-",
    ]
    proc = subprocess.run(cmd, capture_output=True, check=False)
    if proc.returncode != 0:
        stderr = proc.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"ffmpeg decode failed for {src}: {stderr}")
    pcm = np.frombuffer(proc.stdout, dtype="<i2").astype(np.float32) / _PCM_FULL_SCALE
    return pcm, _DECODE_RATE


def analyze_clip(path: str | Path) -> ClipAnalysis:
    """Decode + compute the deterministic primary scalars for one clip.

    Returns ``duration_s`` (sample count / rate), ``rms`` (sqrt(mean(x^2))),
    and ``peak`` (max abs sample). Silence (all-zero PCM) -> rms == peak == 0.0.
    """
    samples, rate = decode_to_mono_float(path)
    n = int(samples.shape[0])
    duration_s = n / float(rate)
    if n == 0:
        return ClipAnalysis(0.0, 0.0, 0.0, 0, rate)
    rms = float(np.sqrt(np.mean(np.square(samples, dtype=np.float64))))
    peak = float(np.max(np.abs(samples)))
    return ClipAnalysis(
        duration_s=duration_s,
        rms=rms,
        peak=peak,
        n_samples=n,
        sample_rate=rate,
    )


def _extract(scalar: str | Callable[[Any], float], obj: Any) -> float:
    """Pull the targeted scalar from an analysis (``ClipAnalysis``, mapping, or
    a custom callable). Keeps the judge generic so the deterministic integration
    test can feed parsed-fake scalars and the live leg can feed real analyses."""
    if callable(scalar):
        return float(scalar(obj))
    if isinstance(obj, Mapping):
        return float(obj[scalar])
    return float(getattr(obj, scalar))


def materially_different(
    control_pair: tuple[Any, Any],
    treatment_pair: tuple[Any, Any],
    scalar: str | Callable[[Any], float],
    *,
    k: int = DEFAULT_K,
) -> Verdict:
    """Deterministic MUR-4 judge.

    ``control_pair`` = (A, A') rendered from the SAME text with the SAME
    direction twice; ``F = |scalar(A) - scalar(A')|`` is the TTS-nondeterminism
    floor. ``treatment_pair`` = (B_a, B_b) the two distinct directions on the
    same text. PASS iff ``|scalar(B_b) - scalar(B_a)| > k * F``.

    The ``scalar`` MUST be one the direction was DESIGNED to move (pace ->
    ``duration_s``; energy -> ``rms``). ``k`` is fixed (default 3) before any
    live run. Pure arithmetic; identical inputs -> identical verdict.
    """
    a = _extract(scalar, control_pair[0])
    a_prime = _extract(scalar, control_pair[1])
    t_a = _extract(scalar, treatment_pair[0])
    t_b = _extract(scalar, treatment_pair[1])
    floor = abs(a - a_prime)
    threshold = k * floor
    delta = abs(t_b - t_a)
    scalar_name = scalar if isinstance(scalar, str) else getattr(scalar, "__name__", "custom")
    return Verdict(
        scalar=scalar_name,
        k=k,
        floor=floor,
        threshold=threshold,
        control_a=a,
        control_a_prime=a_prime,
        treatment_a=t_a,
        treatment_b=t_b,
        delta=delta,
        passed=delta > threshold,
    )
