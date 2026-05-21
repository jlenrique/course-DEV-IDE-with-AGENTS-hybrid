"""Cache-prefix stability test (Story 1.3 AC-1.3-F / NFR-I6 + FR23).

The cache-prefix hash MUST be byte-identical across:
  1. repeated calls within one process (deterministic hashing)
  2. fresh subprocess invocations (no PYTHONHASHSEED randomization leak)
  3. logically-equivalent input dicts with different key insertion order
     (canonical-JSON sort_keys=True idiom)

If this test fails, NFR-I6 is violated and the story does not close.
No waivers per spec AC-1.3-F.
"""

from __future__ import annotations

import subprocess
import sys


def test_cache_prefix_hash_repeated_call_byte_identical() -> None:
    from app.models.selector import _compute_cache_prefix_hash

    h1 = _compute_cache_prefix_hash(
        specialist_id="irene", model_id="gpt-5", temperature=0.5
    )
    h2 = _compute_cache_prefix_hash(
        specialist_id="irene", model_id="gpt-5", temperature=0.5
    )
    assert h1 == h2, "NFR-I6 violation: same inputs produced different hashes"


def test_cache_prefix_hash_invariant_under_subprocess_invocations() -> None:
    """Fresh Python subprocess gets the same hash as this process — proves
    no Python `hash()` (process-randomized) leaked into the implementation."""
    from app.models.selector import _compute_cache_prefix_hash

    in_process = _compute_cache_prefix_hash(
        specialist_id="irene", model_id="gpt-5", temperature=0.5
    )
    proc = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from app.models.selector import _compute_cache_prefix_hash;"
                "print(_compute_cache_prefix_hash("
                "specialist_id='irene', model_id='gpt-5', temperature=0.5))"
            ),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    sub_process = proc.stdout.strip()
    assert in_process == sub_process, (
        f"NFR-I6 violation: subprocess hash {sub_process!r} differs from "
        f"in-process hash {in_process!r} — implementation likely uses "
        "Python's process-randomized hash() somewhere"
    )


def test_cache_prefix_hash_independent_of_keyword_arg_order() -> None:
    """sort_keys=True canonicalization means kwarg insertion order can't bleed."""
    from app.models.selector import _compute_cache_prefix_hash

    h1 = _compute_cache_prefix_hash(
        specialist_id="irene", model_id="gpt-5", temperature=0.5
    )
    h2 = _compute_cache_prefix_hash(
        temperature=0.5, model_id="gpt-5", specialist_id="irene"
    )
    assert h1 == h2


def test_cache_prefix_hash_changes_when_inputs_change() -> None:
    """Sanity: different inputs produce different hashes (not a constant function)."""
    from app.models.selector import _compute_cache_prefix_hash

    base = _compute_cache_prefix_hash(
        specialist_id="irene", model_id="gpt-5", temperature=0.0
    )
    diff_specialist = _compute_cache_prefix_hash(
        specialist_id="gary", model_id="gpt-5", temperature=0.0
    )
    diff_model = _compute_cache_prefix_hash(
        specialist_id="irene", model_id="gpt-5-nano", temperature=0.0
    )
    diff_temp = _compute_cache_prefix_hash(
        specialist_id="irene", model_id="gpt-5", temperature=0.5
    )
    diff_prompt = _compute_cache_prefix_hash(
        specialist_id="irene", model_id="gpt-5", temperature=0.0, system_prompt_hash="abc"
    )
    assert len({base, diff_specialist, diff_model, diff_temp, diff_prompt}) == 5
