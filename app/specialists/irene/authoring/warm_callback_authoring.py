"""Slice-2 leaf: warm_callback feature flag + the injectable renderer seam.

Story concierge-leg1b-warm-callback (Slice 2 — wire the authoring step into
Pass-2). This module is the SEPARABLE generative half (the "warm" surface is a
writer-rendered quality, NOT Irene's prose). It carries:

* :func:`warm_callback_authoring_active` — the default-OFF env flag mirroring
  ``voice_direction_active`` (``MARCUS_NARRATION_VOICE_DIRECTION_ACTIVE``). When
  OFF, ``_act_pass_2`` is byte-unchanged.

* :func:`render_warm_callback` — the INJECTABLE renderer seam. ``model_invoke``
  is the injected callable: the real gpt-5 chat-invoke by default (wired in
  ``_act_pass_2``), a deterministic fake in unit tests. NO MOCK in the live path.

AC6 POSITIVE STRUCTURAL CONTRACT. The renderer prompt constrains the callback to
reference the prior CONCEPT/PATTERN ONLY — no numerals/figures, no
negation/comparator polarity tokens, no new claim. That makes polarity-reversal
UNREACHABLE *by construction* (the model is told never to emit a comparator or a
negation, so it cannot reverse a source polarity), which is the chosen AC6(ii)
path: defer the span/dependency negation upgrade (Leg-4) behind a positive
contract that makes the failure mode unreachable. The bag-of-words Vera-R7 gate
(:func:`app.specialists.irene.authoring.warm_callback.gate_warm_callback`) remains
the runtime BACKSTOP — if a model ignores the contract and emits a stray
numeral/negation/comparator, the gate still blocks-by-omission. The span/dep
upgrade stays Leg-4.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any

__all__ = [
    "WARM_CALLBACK_AUTHORING_ACTIVE_ENV",
    "WARM_CALLBACK_RENDER_SYSTEM_PROMPT",
    "build_warm_callback_render_messages",
    "render_warm_callback",
    "warm_callback_authoring_active",
]

#: Env toggle for the generative callback-authoring step. Default OFF: an unset /
#: empty / falsey value keeps ``_act_pass_2`` byte-identical to the pre-Slice-2
#: baseline. Mirrors ``voice_direction_map.VOICE_DIRECTION_ACTIVE_ENV`` exactly.
WARM_CALLBACK_AUTHORING_ACTIVE_ENV = "MARCUS_WARM_CALLBACK_AUTHORING_ACTIVE"


def warm_callback_authoring_active() -> bool:
    """Return True iff generative warm_callback authoring is woken (default OFF)."""
    return os.environ.get(WARM_CALLBACK_AUTHORING_ACTIVE_ENV, "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


# --------------------------------------------------------------------------- #
# AC6(ii) POSITIVE structural contract — the renderer prompt.
# --------------------------------------------------------------------------- #
WARM_CALLBACK_RENDER_SYSTEM_PROMPT = (
    "You are Irene's narration writer producing ONE short connective 'warm "
    "callback' sentence. A warm callback gently re-orients the learner to a "
    "concept or pattern that was ALREADY established earlier in the lesson, so "
    "the new material lands on familiar ground.\n"
    "\n"
    "ABSOLUTE CONSTRAINTS (a violation makes the callback unusable):\n"
    "1. Reference ONLY the prior CONCEPT or PATTERN by its idea/name. Speak about "
    "what was taught, never a new fact.\n"
    "2. NEVER include any number, digit, figure, percentage, measurement, unit, "
    "currency, count, or statistic. No numerals at all.\n"
    "3. NEVER include a negation or a comparison word (for example: no, not, "
    "never, without, more, less, fewer, greater, lower, higher, than, increased, "
    "decreased, doubled, halved). State the recall positively.\n"
    "4. Introduce NO new claim, data, or material that was not part of the prior "
    "concept. Add nothing; only recall.\n"
    "5. Output EXACTLY one sentence of plain narration prose. No quotes, no "
    "markup, no preamble, no list — just the sentence.\n"
    "\n"
    "Phrase it as a positive recall/bridge, e.g. 'Recall how we established the "
    "idea of ...' or 'As we saw earlier with ...'."
)


def build_warm_callback_render_messages(
    *, anchor_text: str, segment_context: str
) -> list[dict[str, str]]:
    """Assemble the deterministic 2-message prompt for the renderer.

    ``anchor_text`` is the verbatim prior teachable component the callback may
    recall; ``segment_context`` is the current segment's narration the callback
    bridges INTO. Both are passed as reference only — the contract forbids
    copying any numeral/comparator out of either.
    """
    user = (
        "PRIOR CONCEPT TO RECALL (verbatim source — recall its idea, copy no "
        "numerals/comparators from it):\n"
        f"{anchor_text.strip()}\n"
        "\n"
        "CURRENT SEGMENT THIS CALLBACK BRIDGES INTO (for tone/topic only):\n"
        f"{segment_context.strip()}\n"
        "\n"
        "Write the single warm-callback sentence now, obeying every constraint."
    )
    return [
        {"role": "system", "content": WARM_CALLBACK_RENDER_SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]


def render_warm_callback(
    *,
    anchor_text: str,
    segment_context: str,
    model_invoke: Callable[[list[dict[str, str]]], Any],
) -> str:
    """Render ONE warm-callback sentence via the INJECTED ``model_invoke``.

    ``model_invoke`` receives the 2-message prompt list and returns either a
    chat-response object (``.content``) or a bare string — both are handled, so
    the real gpt-5 ``handle.chat.invoke`` and a deterministic test fake share the
    seam without a mock in the live path. Returns the stripped single-line
    sentence (empty string when the model returns nothing usable, which the
    caller treats as fail-safe SILENT).
    """
    messages = build_warm_callback_render_messages(
        anchor_text=anchor_text, segment_context=segment_context
    )
    response = model_invoke(messages)
    raw = response.content if hasattr(response, "content") else response
    text = raw if isinstance(raw, str) else str(raw)
    return " ".join(text.strip().split())
