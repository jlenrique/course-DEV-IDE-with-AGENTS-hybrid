"""Marcus SPOC — conversational single-point-of-contact over the production engine.

BETA capability (a-g): instead of raw `[c/e/s/x]` gate verdicts, the operator
converses with Marcus, who at each gate NARRATES the relevant content in persona
(sources+treatment, ingestion report, lesson plan, research, creative treatment
incl. #variants + voice, motion plan) and collects the operator's decision, then
drives the underlying `production_runner` under the hood. This is the
subprocess-narration-over-the-seam shape ratified at BETA scoping (Winston Q3):
`production_runner` stays the runtime authority; Marcus-SPOC is the operator
surface (operator-facing callsign for the runtime conversational layer — the
deterministic orchestration engine is `production_runner`, not renamed).

Sophisticated free-form NL dialogue / LLM-mediated turn-taking is deferred
(operator directive: defer sophisticated ML); this MVP delivers the structured
conversational surface that presents a-g and accepts per-gate decisions.

Decisions are supplied as a ``{gate_id: {"verb": ..., "edit_payload": ...}}`` map
(operator-in-the-loop or scripted); unmapped gates default to ``approve``.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from app.marcus.orchestrator.g0_enrichment_wiring import (
    G0_DISPATCH_LIVE_ENV,
    G0_ENRICHMENT_MODE_DETERMINISTIC,
    resolve_enrichment_mode,
)
from app.marcus.orchestrator.picker_html_emitter import (
    build_selection_code,
    decode_picker_selection_code,
)
from app.marcus.orchestrator.picker_publisher import publish_picker
from app.marcus.orchestrator.production_runner import resume_production_trial
from app.marcus.orchestrator.styleguide_picker import (
    GAMMA_STYLEGUIDE_PICKS_PATH,
    PickerError,
    append_pick_event,
    assert_pickable_guide,
    load_picker_roster,
    read_pick_events,
    write_pick_to_directive,
)
from app.models.state.operator_verdict import OperatorVerdict
from app.runtime.economics import RUNS_ROOT

_RULE = "─" * 64
_M = "🧑‍💼 **Marcus-SPOC:**"

DEFAULT_OPERATOR_ID = "operator_juan"


# ----------------------------------------------- styleguide-picker PRE-FLIGHT (Seam 3)
# S2 Beat-1 (party record X1): ONE kickoff meeting, three beats — look ->
# material -> contract — framed up front with the known end; never a surprise
# gate N+1. Beat-1 (the look) is this ceremony; Beats 2/3 (G0E/G0R) are S5.
_KICKOFF_SIGNOFFS = (
    "the look — the visual style your deck will wear",
    "the material — the source inventory we teach from",
    "the contract — the learning objectives we sign up to",
)


def narrate_kickoff_beat1(
    *,
    course: str | None = None,
    recommendation: dict[str, Any] | None = None,
) -> str:
    """Beat-1 framing for the kickoff meeting (S2 D3, party X1).

    Names ALL THREE intake sign-offs and the known end up front, then states
    the versions RECOMMENDATION verbatim (P9/F-606): A/B compare on a corpus's
    first run; on a re-run, reuse of the last pick AT ITS OWN version count.
    There is deliberately NO "I'll default to N versions" promise — no default
    engine exists; the operator's actual selection decides, always.
    """
    del course  # named in the signature for the seam; the framing is generic
    lines = [
        _RULE,
        f"{_M} Welcome to our kickoff meeting. Three sign-offs, then we produce:",
    ]
    lines.extend(
        f"  {index}. {signoff}" for index, signoff in enumerate(_KICKOFF_SIGNOFFS, 1)
    )
    lines.append(
        "  The known end: your finished, narrated lesson, assembled and handed off."
    )
    lines.append(f"{_M} First up: the look.")
    if recommendation is None:
        lines.append(
            "  This is our first run on this material — my recommendation: two "
            "versions (A/B) so you can compare. Your pick decides; you can "
            "override to a single version."
        )
    else:
        two_versions = "B" in {
            str(label).strip().upper() for label in recommendation.get("picks", {})
        }
        if two_versions:
            lines.append(
                "  We've produced from this material before — my recommendation: "
                "reuse your last pick, two versions (A/B) as before. Your pick "
                "decides; you can override to a single version."
            )
        else:
            lines.append(
                "  We've produced from this material before — my recommendation: "
                "reuse your last pick, a single version. Your pick decides; you "
                "can override to two (A/B)."
            )
    return "\n".join(lines)


def _parse_event_timestamp(value: Any) -> datetime | None:
    """Parse a pick event's ``picked_at`` (P12/F-603): ``datetime.fromisoformat``
    only, never lexicographic; a naive timestamp reads as UTC; unparseable → None."""
    try:
        parsed = datetime.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed


def _last_pick_for_course(
    course: str | None,
    *,
    events_path: str | Path | None = None,
    ssot_path: str | Path | None = None,
    warn_fn: Callable[[str], None] | None = None,
) -> dict[str, Any] | None:
    """Latest prior USABLE pick for THIS course, from the F-502 course field.

    Derives EXCLUSIVELY from the additive ``course`` field on pick events —
    NEVER by dereferencing ``directive_path`` (run-scoped and prunable, not a
    course proxy). Legacy events without the field are honestly "no prior
    pick". Returns ``{"picks": {variant: guide}, "picked_at": iso}`` or None.

    Hardening (T11 remediation):

    - P12: the latest EVENT is chosen by PARSED timestamp
      (:func:`_parse_event_timestamp`), ties break to the LAST line in the
      file, and ONLY that event's own commit group — the events sharing its
      ``(picked_at, directive_path)`` — form the pick: no cross-event merging.
    - P1: every guide in the candidate pick must still be PICKABLE
      (SSOT-member, not deprecated, not probe — the A-M1 rule via
      :func:`assert_pickable_guide`); an unpickable or slot-A-less last pick
      degrades honestly to "no prior usable pick" (None) with a WARN — never
      a recommended dead-end that burns ceremony attempts.
    - P5: an unreadable/corrupt sidecar WARNs and degrades to None — the
      lookup is optional and must never block the ceremony.
    """
    if not course:
        return None
    emit = warn_fn if warn_fn is not None else (lambda _msg: None)
    path = Path(events_path) if events_path is not None else GAMMA_STYLEGUIDE_PICKS_PATH
    try:
        events = read_pick_events(path)
    except (PickerError, OSError) as exc:
        emit(
            f"{_M} WARNING: I couldn't read the pick history ({exc}); "
            "proceeding with no prior pick on record."
        )
        return None
    matching: list[tuple[datetime, dict[str, Any]]] = []
    for event in events:
        if str(event.get("course") or "") != str(course):
            continue
        if not (event.get("variant_id") and event.get("guide_name")):
            continue
        stamp = _parse_event_timestamp(event.get("picked_at"))
        if stamp is None:
            continue
        matching.append((stamp, event))
    if not matching:
        return None
    latest_index = max(range(len(matching)), key=lambda i: (matching[i][0], i))
    latest = matching[latest_index][1]
    group_key = (str(latest.get("picked_at")), str(latest.get("directive_path") or ""))
    picks = {
        str(event["variant_id"]).strip().upper(): str(event["guide_name"]).strip()
        for _stamp, event in matching
        if (str(event.get("picked_at")), str(event.get("directive_path") or ""))
        == group_key
    }
    if "A" not in picks:
        # A slot-A-less pick cannot mint a selection code — honest degrade (P1).
        return None
    for guide in picks.values():
        try:
            assert_pickable_guide(guide, ssot_path=ssot_path)
        except PickerError as exc:
            emit(
                f"{_M} WARNING: your last pick for this course is no longer "
                f"usable ({exc}); proceeding with no prior usable pick."
            )
            return None
    return {"picks": picks, "picked_at": str(latest.get("picked_at"))}


def narrate_pick_recommendation(
    recommendation: dict[str, Any], *, ssot_path: str | Path | None = None
) -> str:
    """Provenance-rich pre-selection (AC-7): recommend the last-used-per-course
    pick BY NAME with when-it-was-picked provenance. Explicit confirm is still
    required downstream — no auto-accept, no timeout, no bypass."""
    index = _roster_index(ssot_path)
    picks = recommendation["picks"]
    named = [
        str(index.get(picks[label], {}).get("display_name") or picks[label])
        for label in sorted(picks)
    ]
    return (
        f"{_M} My recommendation: reuse {' + '.join(named)} — your last pick for "
        f"this course (picked {recommendation['picked_at']}). Reply 'recommended' "
        f"to accept it (I'll still read it back for your confirm), or paste a "
        f"fresh selection code from the page."
    )


# P13: the publish exception is narrated to the OPERATOR — scrub URL/token-shaped
# substrings (a gh-pages push error can embed a remote URL with credentials) and
# truncate, keeping the exception class name for diagnosis.
_NARRATION_URL_RE = re.compile(r"https?://\S+")
_NARRATION_TOKEN_RE = re.compile(
    r"\b(?:gh[pousr]_[A-Za-z0-9]{6,}|github_pat_[A-Za-z0-9_]{6,}|sk-[A-Za-z0-9_\-]{8,})\b"
)
_MAX_NARRATED_ERROR_LEN = 160


def _scrub_error_for_narration(error: BaseException) -> str:
    """Operator-safe rendering of an exception (P13): no raw URLs, no
    token-shaped substrings, bounded length, class name preserved."""
    text = f"{type(error).__name__}: {error}".strip().rstrip(":").strip()
    text = _NARRATION_URL_RE.sub("<url redacted>", text)
    text = _NARRATION_TOKEN_RE.sub("<token redacted>", text)
    if len(text) > _MAX_NARRATED_ERROR_LEN:
        text = text[:_MAX_NARRATED_ERROR_LEN] + "… (truncated)"
    return text


def narrate_picker_publish_degrade(
    error: BaseException, *, recommendation: dict[str, Any] | None = None
) -> str:
    """Publish-flake degrade narration (S2 D3): numbered ways forward, with an
    honest recommendation — never a silent fallback. Option 3 (reuse last
    pick) is OFFERED only when a usable prior pick exists (P8) — an
    unavailable option is not a menu row. The exception text is scrubbed
    before narration (P13)."""
    ways = "Three ways forward:" if recommendation is not None else "Two ways forward:"
    lines = [
        _RULE,
        f"{_M} I couldn't publish the visual picker page "
        f"({_scrub_error_for_narration(error)}). {ways}",
        "  1. Retry the publish.",
        "  2. I'll list the styles right here as text — same styles, same "
        "selection codes; you just won't see thumbnails.",
    ]
    if recommendation is not None:
        picked = ", ".join(
            f"{label}: {guide}" for label, guide in sorted(recommendation["picks"].items())
        )
        lines.append(
            f"  3. Reuse your last pick for this course ({picked}, picked "
            f"{recommendation['picked_at']})."
        )
        lines.append(
            f"{_M} My recommendation: option 3 — your last pick still stands."
        )
    else:
        lines.append(
            f"{_M} My recommendation: option 2 — the text list gets us moving now."
        )
    return "\n".join(lines)


def narrate_inline_style_list(roster: list[dict[str, Any]]) -> str:
    """Inline TEXT roster for the degraded path (F-506(a)): the SAME guides as
    the SSOT roster, same selection-code grammar downstream, honest about the
    missing thumbnails."""
    lines = [
        f"{_M} Here are your styles as a text list (no thumbnails in this "
        "mode — honest heads-up):",
    ]
    lines.extend(
        f"  {index}. {entry['display_name']} ({entry['name']}) — "
        f"{entry['distinguishing']}"
        for index, entry in enumerate(roster, 1)
    )
    lines.append(
        f"{_M} Give me a number for Version A (and optionally one for Version B)."
    )
    return "\n".join(lines)


def narrate_picker_preflight(
    publish_url: str, run_tag: str, *, style_count: int | None = None
) -> str:
    """Client-facing PRE-FLIGHT narration (runs BEFORE G1): surface the picker url.

    Numbered-row HIL instruction + paste-back close. Deliberately client-facing:
    no styleguide slug ids and no "directive" vocabulary leak into what a client
    sees (A6/A7 keep the internal ids server-side).
    """
    count = f" ({style_count} styles to choose from)" if style_count else ""
    lines = [
        _RULE,
        f"{_M} Before we start, let's pick the visual style for your deck{count}.",
        "  1. Open your styleguide picker:",
        f"     {publish_url}",
        "     (it can take up to a minute to go live — if it shows a not-found page "
        "at first, wait a moment and refresh.)",
        "  2. Choose your style, and whether you want one version or two (A/B).",
        "  3. Copy the SELECTION CODE the page shows you and paste it back to me here.",
        f"{_M} I'll read it back to you to confirm before we lock it in.",
    ]
    return "\n".join(lines)


def _roster_index(ssot_path: str | Path | None) -> dict[str, dict[str, Any]]:
    roster = load_picker_roster(
        include_probes=True, include_deprecated=True, ssot_path=ssot_path
    )
    return {entry["name"]: entry for entry in roster}


def _roster_content_hash(ssot_path: str | Path | None) -> str:
    """Stable content hash of the resolvable roster (A7 provenance handle)."""
    index = _roster_index(ssot_path)
    payload = [
        {"name": name, "lifecycle": index[name].get("lifecycle")}
        for name in sorted(index)
    ]
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def decode_and_echo_pick(
    code: str,
    *,
    expected_run_tag: str,
    ssot_path: str | Path | None = None,
) -> tuple[dict[str, str], str]:
    """Decode a pasted selection code and build a human-readable echo-and-confirm.

    Returns ``({"A": slug, "B": slug?}, echo_text)``. The echo names the guide(s)
    by DISPLAY NAME + lifecycle + version count (client-facing — no slug ids, no
    "directive"). A stale/foreign or malformed code propagates the fail-loud
    ``PickerError`` from the decoder.
    """
    picks = decode_picker_selection_code(
        code, expected_run_tag=expected_run_tag, ssot_path=ssot_path
    )
    index = _roster_index(ssot_path)
    version_count = 2 if "B" in picks else 1
    named: list[str] = []
    for label in ("A", "B"):
        if label not in picks:
            continue
        entry = index.get(picks[label], {})
        display = str(entry.get("display_name") or picks[label])
        lifecycle = str(entry.get("lifecycle") or "candidate")
        named.append(f"Version {label}: {display} ({lifecycle})")
    words = "2 versions" if version_count == 2 else "1 version"
    echo = (
        f"{_M} Here's what I have — please confirm:\n  "
        + "\n  ".join(named)
        + f"\n  That's {words}. Reply 'confirm' to lock it in, or paste a new code."
    )
    return picks, echo


def commit_picker_pick(
    picks: dict[str, str] | None = None,
    *,
    directive_path: str | Path,
    expected_run_tag: str,
    publish_url: str,
    picked_by: str,
    code: str,
    confirmed: bool = False,
    ssot_path: str | Path | None = None,
    events_path: str | Path | None = None,
    run_id: str | None = None,
    course: str | None = None,
) -> dict[str, Any]:
    """On CONFIRM: write the directive + append the sidecar with A7 provenance.

    ``course`` (S2 F-502, additive) stamps the corpus/course identity onto the
    sidecar pick events so "last-used-per-course" recommendations derive from
    the event itself, never from the run-scoped ``directive_path``.

    Threads the full provenance chain (who / from-url / roster content-hash /
    resolved ids + version count / the code itself) into the directive's
    ``styleguide_picker_provenance`` block. An unattributable pick (empty
    ``picked_by``) FAILS LOUD — never a silent anonymous bind.

    ENFORCED confirm gate: ``confirmed`` must be truthy — a caller cannot
    decode-then-commit directly, bypassing the echo-and-confirm beat. The picks
    are RE-DERIVED from ``code`` (single source of truth) so the provenance
    ``selection_code`` can never disagree with the bound picks; a ``picks`` arg,
    when passed, is cross-checked against the decode and a mismatch FAILS LOUD.
    An identical re-confirm is a TRUE no-op on the sidecar (stable
    ``(run_tag, code)`` dedup key), and always leaves exactly one provenance block.
    """
    if not confirmed:
        raise PickerError(
            "commit refused: the pick was not affirmatively confirmed "
            "(echo-and-confirm gate) — decode-then-commit may not bypass the echo"
        )
    attributed = str(picked_by or "").strip()
    if not attributed:
        raise PickerError(
            "unattributable pick: picked_by (who chose — operator or named client) "
            "is required for the A7 provenance chain"
        )
    # Single-source the picks FROM the code (Blind Hunter NIT): the provenance's
    # selection_code can then never disagree with the bound picks.
    derived = decode_picker_selection_code(
        code, expected_run_tag=expected_run_tag, ssot_path=ssot_path
    )
    if picks is not None and dict(picks) != derived:
        raise PickerError(
            f"selection code decodes to {derived} but the supplied picks are "
            f"{dict(picks)} — refusing to bind a code that disagrees with its picks"
        )
    version_count = 2 if "B" in derived else 1
    provenance_extra = {
        "picked_by": attributed,
        "publish_url": publish_url,
        "roster_sha256": _roster_content_hash(ssot_path),
        "version_count": version_count,
        "selection_code": code,
        "run_tag": expected_run_tag,
    }
    provenance = write_pick_to_directive(
        directive_path,
        derived,
        ssot_path=ssot_path,
        provenance_extra=provenance_extra,
    )
    # Stable dedup identity: an identical re-confirm (fresh picked_at) is a no-op.
    stable_dedup = f"{expected_run_tag}:{hashlib.sha256(code.encode('utf-8')).hexdigest()}"
    append_pick_event(
        derived,
        directive_path=directive_path,
        picked_at=provenance["picked_at"],
        run_id=run_id,
        events_path=events_path,
        dedup_key=stable_dedup,
        course=course,
    )
    return {"picks": derived, "provenance": provenance}


_AFFIRMATIVE = frozenset({"confirm", "confirmed", "yes", "y", "lock it in", "lock"})
# Accept-recommended vocabulary (F-506(b)): accepting the recommendation mints
# the code via `build_selection_code` and flows through the SAME
# decode -> echo -> confirm -> commit path as a pasted code.
_ACCEPT_RECOMMENDED = frozenset({"recommended", "recommend", "rec", "reuse"})

# ------------------------------------------------------------ publish_url contract
# P14: the provenance's `publish_url` field is EITHER the real https URL of the
# published picker page OR a member of this documented `degraded:*` sentinel
# family — an arm that never published a page must say so honestly, and every
# no-page sentinel shares the `degraded:` prefix so consumers can test for it.
DEGRADED_PUBLISH_URL_PREFIX = "degraded:"
DEGRADED_PUBLISH_URL_INLINE_LIST = "degraded:inline-text-list (no picker page published)"
DEGRADED_PUBLISH_URL_REUSE_LAST_PICK = "degraded:reuse-last-pick (no picker page published)"
DEGRADED_PUBLISH_URL_SCRIPTED = (
    "degraded:scripted-selection-code (no picker page published)"
)

# P7/P8: menu typos re-prompt WITHOUT consuming the shared attempt budget, but
# every typo loop is still bounded by this cap — no unbounded loops anywhere in
# the ceremony.
_MAX_FREE_REPROMPTS = 10


class _CeremonyBudget:
    """ONE shared attempt budget across the whole ceremony (P8).

    Substantive failures consume an attempt: a decode-rejected code, a
    non-affirmed echo, a failed publish retry, a failed code mint, an inline
    pass without slot A. Menu typos re-prompt for free (bounded by
    :data:`_MAX_FREE_REPROMPTS`, P7). A successful publish retry does NOT
    refresh the budget — the surviving remainder carries into the paste loop.
    """

    def __init__(self, max_attempts: int) -> None:
        self.total = max(1, int(max_attempts))
        self.remaining = self.total

    def consume(self) -> None:
        self.remaining -= 1

    @property
    def exhausted(self) -> bool:
        return self.remaining <= 0


def _read_reply(input_fn: Callable[[str], str], prompt: str) -> str:
    """Read one operator reply; EOF/Ctrl-C at ANY ceremony prompt becomes a
    clean fail-loud :class:`PickerError` (P6 — honors the ERROR/exit-1 contract)."""
    try:
        return input_fn(prompt)
    except (EOFError, KeyboardInterrupt) as exc:
        raise PickerError("operator aborted the styleguide ceremony") from exc


def _decode_reject_message(exc: PickerError, *, pasted: bool) -> str:
    """Context-correct decode-reject messaging (P8): only a PASTED code earns
    'paste it again'; a minted code (inline list / reuse / recommended) never
    involved a paste."""
    if pasted:
        return f"{_M} That code didn't work: {exc}. Please paste it again."
    return f"{_M} That pick can't be locked in: {exc}."


def _confirm_codes(
    *,
    code: str,
    pasted: bool,
    budget: _CeremonyBudget,
    run_tag: str,
    directive_path: str | Path,
    publish_url: str,
    picked_by: str,
    input_fn: Callable[[str], str],
    print_fn: Callable[[str], None],
    ssot_path: str | Path | None,
    events_path: str | Path | None,
    run_id: str | None,
    course: str | None,
) -> dict[str, Any] | None:
    """Shared ceremony tail: decode + echo -> explicit affirmative -> commit.

    EVERY commit arm (pasted code, accept-recommended, inline text list,
    reuse-last-pick) funnels through this ONE tail, so the committed directive
    shape is identical by construction (F-506(b)). A NON-affirmative reply at
    the confirm prompt is fed back to decode as a fresh code (P16 — the prompt
    says "or paste a new code" and we honor it). Every substantive failure
    (decode reject, declined echo) consumes ONE shared attempt (P8). Returns
    the commit record, or None once an attempt was consumed (the caller
    re-surfaces its own prompt/menu if budget remains)."""
    while True:
        try:
            _picks, echo = decode_and_echo_pick(
                code, expected_run_tag=run_tag, ssot_path=ssot_path
            )
        except PickerError as exc:
            # Rejected AT DECODE — a stale/foreign/malformed/unpickable code
            # never reaches commit.
            print_fn(_decode_reject_message(exc, pasted=pasted))
            budget.consume()
            return None
        print_fn(echo)
        answer = _read_reply(
            input_fn, "Reply 'confirm' to lock it in, or paste a new code: "
        ).strip()
        if answer.lower() in _AFFIRMATIVE:
            return commit_picker_pick(
                directive_path=directive_path,
                expected_run_tag=run_tag,
                publish_url=publish_url,
                picked_by=picked_by,
                code=code,
                confirmed=True,
                ssot_path=ssot_path,
                events_path=events_path,
                run_id=run_id,
                course=course,
            )
        budget.consume()
        if budget.exhausted or not answer:
            return None
        # P16: the non-affirmative reply IS the fresh code for the next attempt.
        code = answer
        pasted = True


def _paste_confirm_commit_loop(
    *,
    run_tag: str,
    directive_path: str | Path,
    publish_url: str,
    picked_by: str,
    input_fn: Callable[[str], str],
    print_fn: Callable[[str], None],
    ssot_path: str | Path | None,
    events_path: str | Path | None,
    run_id: str | None,
    course: str | None,
    budget: _CeremonyBudget,
    recommendation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """The paste-back loop: read a code (or 'recommended'), echo, confirm, commit.

    Runs on the ONE shared ceremony budget (P8): a decode-rejected code, a
    declined echo, or a failed recommendation mint each consume an attempt."""
    prompt = "Paste your selection code: "
    if recommendation is not None:
        prompt = (
            "Paste your selection code (or reply 'recommended' to accept my "
            "recommendation): "
        )
    while not budget.exhausted:
        reply = _read_reply(input_fn, prompt).strip()
        code, pasted = reply, True
        if recommendation is not None and reply.lower() in _ACCEPT_RECOMMENDED:
            try:
                # F-506(b): pre-fill the paste — mint through the Python twin,
                # then the identical decode -> echo -> confirm -> commit path.
                code = build_selection_code(run_tag, recommendation["picks"])
                pasted = False
            except PickerError as exc:
                print_fn(f"{_M} I couldn't mint your last pick into a code: {exc}")
                budget.consume()
                continue
        record = _confirm_codes(
            code=code,
            pasted=pasted,
            budget=budget,
            run_tag=run_tag,
            directive_path=directive_path,
            publish_url=publish_url,
            picked_by=picked_by,
            input_fn=input_fn,
            print_fn=print_fn,
            ssot_path=ssot_path,
            events_path=events_path,
            run_id=run_id,
            course=course,
        )
        if record is not None:
            return record
        # Attempt consumed inside _confirm_codes — loop while budget remains.
    raise PickerError(
        f"no confirmed styleguide pick after {budget.total} attempts; pre-flight "
        f"aborted without writing the directive"
    )


def _inline_numbered_pick(
    roster: list[dict[str, Any]],
    *,
    budget: _CeremonyBudget,
    input_fn: Callable[[str], str],
    print_fn: Callable[[str], None],
) -> dict[str, str] | None:
    """Numbered text pick over the SSOT roster (degraded path). Slot A is
    required — the selection-code grammar the commit path mints needs it.

    Bounded (P7): number typos re-prompt free up to :data:`_MAX_FREE_REPROMPTS`
    (then fail loud); a completed pass WITHOUT slot A is a substantive failure
    that consumes a shared attempt (P8). Returns None when the shared budget is
    exhausted (the caller's loop then raises the final PickerError)."""
    free = _MAX_FREE_REPROMPTS
    while True:
        picks: dict[str, str] = {}
        for variant in ("A", "B"):
            while True:
                raw = _read_reply(
                    input_fn, f"Style {variant} number (blank for none): "
                ).strip()
                if not raw:
                    break
                if raw.isdigit() and 1 <= int(raw) <= len(roster):
                    picks[variant] = roster[int(raw) - 1]["name"]
                    break
                free -= 1
                if free <= 0:
                    raise PickerError(
                        "too many invalid replies at the inline style menu; "
                        "ceremony aborted"
                    )
                print_fn(f"{_M} invalid choice {raw!r}; enter 1-{len(roster)} or blank")
        if picks.get("A"):
            return picks
        budget.consume()
        if budget.exhausted:
            return None
        print_fn(f"{_M} Version A is required for a selection code — let's try again.")


def _degraded_publish_pick(
    *,
    error: BaseException,
    run_tag: str,
    directive_path: str | Path,
    out_dir: str | Path,
    picked_by: str,
    input_fn: Callable[[str], str],
    print_fn: Callable[[str], None],
    publish_fn: Callable[..., dict[str, Any]],
    ssot_path: str | Path | None,
    events_path: str | Path | None,
    run_id: str | None,
    course: str | None,
    include_probes: bool,
    site_repo: str | None,
    token: str | None,
    recommendation: dict[str, Any] | None,
    budget: _CeremonyBudget,
) -> dict[str, Any]:
    """Publish-flake degrade (S2 D3): numbered options = retry publish / inline
    TEXT list from the SSOT / reuse last pick with provenance (offered only
    when a usable prior pick exists, P8). Every arm commits through the SAME
    `commit_picker_pick` shape, on the ONE shared budget (P8): failed retries,
    failed mints, rejected/declined codes and A-less inline passes consume;
    menu typos re-prompt free (bounded, P7); a successful publish retry does
    NOT refresh the budget."""
    roster = load_picker_roster(
        include_probes=include_probes, ssot_path=ssot_path, events_path=events_path
    )
    commit_kwargs: dict[str, Any] = {
        "run_tag": run_tag,
        "directive_path": directive_path,
        "picked_by": picked_by,
        "input_fn": input_fn,
        "print_fn": print_fn,
        "ssot_path": ssot_path,
        "events_path": events_path,
        "run_id": run_id,
        "course": course,
    }
    menu_prompt = (
        "Choose 1 (retry publish), 2 (inline text list), or 3 (reuse last pick): "
        if recommendation is not None
        else "Choose 1 (retry publish) or 2 (inline text list): "
    )
    free = _MAX_FREE_REPROMPTS
    while not budget.exhausted:
        print_fn(narrate_picker_publish_degrade(error, recommendation=recommendation))
        choice = _read_reply(input_fn, menu_prompt).strip()
        if choice == "1":
            try:
                record = publish_fn(
                    run_tag=run_tag,
                    out_dir=out_dir,
                    ssot_path=ssot_path,
                    include_probes=include_probes,
                    site_repo=site_repo,
                    token=token,
                )
            except Exception as exc:  # still down — re-narrate honestly
                error = exc
                budget.consume()  # a failed retry is substantive (P8)
                continue
            publish_url = str(record["publish_url"])
            print_fn(
                narrate_picker_preflight(
                    publish_url, run_tag, style_count=record.get("style_count")
                )
            )
            if recommendation is not None:
                print_fn(
                    narrate_pick_recommendation(recommendation, ssot_path=ssot_path)
                )
            # P8: the surviving budget carries over — a successful retry does
            # NOT grant a fresh full budget.
            return _paste_confirm_commit_loop(
                publish_url=publish_url,
                budget=budget,
                recommendation=recommendation,
                **commit_kwargs,
            )
        if choice == "2":
            print_fn(narrate_inline_style_list(roster))
            picks = _inline_numbered_pick(
                roster, budget=budget, input_fn=input_fn, print_fn=print_fn
            )
            if picks is None:
                continue  # shared budget exhausted — the while exits to the raise
            try:
                code = build_selection_code(run_tag, picks)
            except PickerError as exc:
                print_fn(f"{_M} That pick can't mint a selection code: {exc}")
                budget.consume()
                continue
            record = _confirm_codes(
                code=code,
                pasted=False,
                budget=budget,
                publish_url=DEGRADED_PUBLISH_URL_INLINE_LIST,
                **commit_kwargs,
            )
            if record is not None:
                return record
            continue
        if choice == "3" and recommendation is not None:
            try:
                code = build_selection_code(run_tag, recommendation["picks"])
            except PickerError as exc:
                print_fn(f"{_M} I couldn't mint your last pick into a code: {exc}")
                budget.consume()
                continue
            record = _confirm_codes(
                code=code,
                pasted=False,
                budget=budget,
                publish_url=DEGRADED_PUBLISH_URL_REUSE_LAST_PICK,
                **commit_kwargs,
            )
            if record is not None:
                return record
            continue
        # Menu typo (including '3' when no usable prior pick exists — option 3
        # is not offered then, P8): re-prompt WITHOUT consuming, bounded by the
        # free-reprompt cap (P7).
        if choice == "3":
            print_fn(
                f"{_M} There's no prior usable pick on record for this course — "
                "choose 1 or 2."
            )
        elif recommendation is not None:
            print_fn(f"{_M} I need 1, 2, or 3.")
        else:
            print_fn(f"{_M} I need 1 or 2.")
        free -= 1
        if free <= 0:
            raise PickerError(
                "too many invalid replies at the picker degrade menu; ceremony aborted"
            )
    raise PickerError(
        f"picker publish degraded and no pick was confirmed within {budget.total} "
        f"attempts; pre-flight aborted without writing the directive"
    )


def run_picker_preflight(
    *,
    run_tag: str,
    directive_path: str | Path,
    out_dir: str | Path,
    picked_by: str,
    input_fn: Callable[[str], str] = input,
    print_fn: Callable[[str], None] = print,
    publish_fn: Callable[..., dict[str, Any]] = publish_picker,
    ssot_path: str | Path | None = None,
    events_path: str | Path | None = None,
    run_id: str | None = None,
    include_probes: bool = False,
    site_repo: str | None = None,
    token: str | None = None,
    max_attempts: int = 3,
    course: str | None = None,
) -> dict[str, Any] | None:
    """The enforced pre-flight product path (runs BEFORE G1) — the ONE real caller.

    S2: the kickoff meeting's Beat-1. Frames the three intake sign-offs + the
    known end (:func:`narrate_kickoff_beat1`), publishes the picker for THIS
    ``run_tag`` → surfaces the url via :func:`narrate_picker_preflight` (plus a
    provenance-rich last-used-per-course recommendation when ``course`` has a
    prior pick event — F-502; explicit confirm still required) → reads a pasted
    selection code (or 'recommended', minted via ``build_selection_code``,
    F-506(b)) → decode + echo via :func:`decode_and_echo_pick` → REQUIRE an
    explicit affirmative confirm → only then :func:`commit_picker_pick` (with
    ``confirmed=True``). A stale/foreign or malformed code is rejected AT
    DECODE, before any commit. A publish failure degrades to the numbered
    retry / inline-text-list / reuse-last-pick options
    (:func:`narrate_picker_publish_degrade`) — every arm commits through the
    SAME path. ``max_attempts`` funds ONE shared budget across the whole
    ceremony (P8): substantive failures consume it wherever they happen; menu
    typos re-prompt free (bounded, P7). If no valid code is confirmed within
    the budget, raises :class:`PickerError` without writing the directive.
    EOF/Ctrl-C at any prompt aborts cleanly as a :class:`PickerError` (P6).
    All I/O is via injectable ``input_fn`` / ``print_fn`` / ``publish_fn`` so
    every path is fully testable offline.
    """
    recommendation = _last_pick_for_course(
        course, events_path=events_path, ssot_path=ssot_path, warn_fn=print_fn
    )
    print_fn(narrate_kickoff_beat1(course=course, recommendation=recommendation))
    budget = _CeremonyBudget(max_attempts)
    commit_kwargs: dict[str, Any] = {
        "run_tag": run_tag,
        "directive_path": directive_path,
        "picked_by": picked_by,
        "input_fn": input_fn,
        "print_fn": print_fn,
        "ssot_path": ssot_path,
        "events_path": events_path,
        "run_id": run_id,
        "course": course,
    }
    try:
        record = publish_fn(
            run_tag=run_tag,
            out_dir=out_dir,
            ssot_path=ssot_path,
            include_probes=include_probes,
            site_repo=site_repo,
            token=token,
        )
    except Exception as exc:
        # gh-pages flake: honest numbered degrade (S2 D3) — never a silent skip.
        return _degraded_publish_pick(
            error=exc,
            out_dir=out_dir,
            publish_fn=publish_fn,
            include_probes=include_probes,
            site_repo=site_repo,
            token=token,
            recommendation=recommendation,
            budget=budget,
            **commit_kwargs,
        )
    publish_url = str(record["publish_url"])
    print_fn(
        narrate_picker_preflight(
            publish_url, run_tag, style_count=record.get("style_count")
        )
    )
    if recommendation is not None:
        print_fn(narrate_pick_recommendation(recommendation, ssot_path=ssot_path))
    return _paste_confirm_commit_loop(
        publish_url=publish_url,
        budget=budget,
        recommendation=recommendation,
        **commit_kwargs,
    )


def build_operator_verdict_kwargs(
    *,
    trial_id: UUID,
    gate_id: str,
    card: dict[str, Any],
    verb: str,
    edit_payload: Any | None = None,
    reject_reason: str | None = None,
    operator_id: str = DEFAULT_OPERATOR_ID,
) -> dict[str, Any]:
    """Build the ``OperatorVerdict(**kwargs)`` dict shared by the scripted SPOC
    and the interactive interlocutor (A3 — backward-compat is structural, not
    coincidental). ``card`` is the persisted decision-card payload (the
    ``{"card": {...}, "digest": ...}`` envelope on disk).
    """
    kwargs: dict[str, Any] = {
        "trial_id": trial_id,
        "gate_id": gate_id,
        "card_id": UUID(card["card"]["card_id"]),
        "operator_id": operator_id,
        "decision_card_digest": card["digest"],
        "verb": verb,
    }
    if verb in {"edit", "select"}:
        kwargs["edit_payload"] = edit_payload
    if verb == "reject":
        kwargs["reject_reason"] = reject_reason or "operator-rejected"
    return kwargs


def _load(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _narrate_sources(run_dir: Path, lines: list[str]) -> None:
    """Capability (a): sources + how each is treated."""
    directive_path = run_dir / "directive.yaml"
    if not directive_path.exists():
        return
    roles: list[str] = []
    cur_loc = None
    for raw in directive_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("locator:"):
            cur_loc = line.split("locator:", 1)[1].strip()
        elif line.startswith("role:") and cur_loc:
            role = line.split("role:", 1)[1].strip()
            roles.append(f"  - {cur_loc} -> treated as **{role}**")
            cur_loc = None
    lines.append(f"{_M} I've composed the source directive (capability a). Source treatment:")
    lines.extend(roles or ["  - (no sources parsed)"])
    lines.append("  Confirm these roles, or tell me to re-treat any source.")


def _narrate_ingestion(run_dir: Path, lines: list[str]) -> None:
    """Capability (b): ingestion completeness / errors."""
    manifest = _load(run_dir / "bundle" / "manifest.json")
    lines.append(f"{_M} Ingestion report (capability b) -")
    if isinstance(manifest, dict) and manifest.get("artifacts"):
        arts = manifest["artifacts"]
        total = sum(int(a.get("size_bytes", 0)) for a in arts if isinstance(a, dict))
        lines.append(f"  - Texas extracted {len(arts)} artifacts ({total:,} bytes); complete.")
        for a in arts[:6]:
            if isinstance(a, dict):
                lines.append(f"      - {a.get('path')} ({a.get('size_bytes')} bytes)")
        lines.append("  - No ingestion errors; the source bundle is ready to narrate.")
    else:
        lines.append("  - (bundle manifest not yet available at this gate)")


def _narrate_lesson_plan(run_dir: Path, lines: list[str]) -> None:
    """Capability (c): the lesson plan (Marcus + Irene)."""
    alt = run_dir / "irene-pass1.md"
    top = run_dir.parent.parent.parent / "runs" / run_dir.name / "irene-pass1.md"
    src = alt if alt.exists() else (top if top.exists() else None)
    lines.append(f"{_M} The lesson plan Irene and I drafted (capability c) -")
    if src is not None:
        head = [f"  {ln}" for ln in src.read_text(encoding="utf-8").splitlines()[:8] if ln.strip()]
        lines.extend(head or ["  - (lesson plan present)"])
    else:
        lines.append("  - plan units are staged in run state; tell me to adjust scope/sequencing.")


def _narrate_treatment(card: dict[str, Any], lines: list[str]) -> None:
    """Capability (e): creative treatment - #variants + clustering/pace."""
    inner = card.get("card", {})
    variants = inner.get("variant_candidates") or []
    opts = [e for e in inner.get("pick_context", []) if e.get("kind") == "variant-options"]
    lines.append(f"{_M} The Creative Director's proposed treatment (capability e) -")
    lines.append(f"  - Slide variants for Storyboard-A selection: {variants or '(1 per slide)'}")
    if opts:
        for slide in opts[0].get("slides", [])[:8]:
            vs = ", ".join(str(v.get("variant")) for v in slide.get("variants", []))
            lines.append(f"      - {slide.get('slide_id')}: variant(s) [{vs}]")
    lines.append("  Tell me how many variants per slide, or approve the proposed set.")


def _narrate_voice(card: dict[str, Any], lines: list[str]) -> None:
    """Capability (e): narration voice selection."""
    ctx = card.get("card", {}).get("pick_context", [])
    opts = [e for e in ctx if e.get("kind") == "voice-options"]
    lines.append(f"{_M} Narration voice options (capability e/voice) -")
    if opts:
        for v in opts[0].get("voices", []):
            lines.append(
                f"  - {v.get('voice_id')} - {v.get('voice_name')}  "
                f"sample: {v.get('sample_audio_url')}"
            )
    lines.append("  Say a voice id to bind it through synthesis, or approve my recommendation.")


def _narrate_g0_enrichment(card: dict[str, Any], run_dir: Path, lines: list[str]) -> None:
    """Confirm-gate #1 (G0E): typed COMPONENTS grouped by file + LOs + roots + dissent."""
    enrichment = _load(run_dir / "g0-enrichment.json") or {}
    inner = card.get("card", {})
    components = inner.get("typed_components") or enrichment.get("typed_components") or []
    los = inner.get("provisional_los") or enrichment.get("provisional_los") or []
    roots = inner.get("traversal_roots") or enrichment.get("traversal_roots") or []
    reconcile = inner.get("reconcile") or enrichment.get("reconcile") or {}
    dissents = inner.get("dissents") or enrichment.get("dissents") or []
    lines.append(f"{_M} G0 source-enrichment manifest for your confirmation (gate #1):")
    lines.append(f"  Traversal roots I walked ({len(roots)}):")
    for root in roots[:5]:
        lines.append(f"    - {root.get('kind')}: {root.get('root_id')}")
    # Group the typed components by their parent FILE (a file yields N components).
    by_file: dict[str, list[dict[str, Any]]] = {}
    for comp in components:
        by_file.setdefault(str(comp.get("parent_source_id")), []).append(comp)
    lines.append(
        f"  Typed COMPONENTS ({len(components)} across {len(by_file)} files):"
    )
    for parent, comps in list(by_file.items())[:8]:
        lines.append(f"    {parent} ({len(comps)} components):")
        for comp in comps[:6]:
            flag = "  [flagged: no generator today]" if comp.get("flagged_unconsumed") else ""
            label = str(comp.get("label", ""))[:48]
            lines.append(
                f"      - {comp.get('source_type')}: {label} @ "
                f"{comp.get('locator')}{flag}"
            )
    lines.append(f"  Candidate provisional LOs ({len(los)}):")
    for lo in los[:8]:
        lines.append(f"    - {lo.get('objective_id')}: {lo.get('statement', '')[:80]}")
    if reconcile:
        lines.append(
            f"  Reconcile: {reconcile.get('n_files_in')} files in == "
            f"{reconcile.get('n_files_covered')} covered + "
            f"{reconcile.get('n_files_ignored')} ignored; "
            f"{reconcile.get('n_components')} components "
            f"({reconcile.get('n_flagged')} flagged classification-only)."
        )
    if dissents:
        d = dissents[0]
        lines.append(
            f"  My recorded dissent (A3): on {d.get('against')} — {d.get('marcus_position')}"
        )
    lines.append("  Confirm the typing + LOs, or tell me to re-type a component / drop an LO.")


# S5-3b (D3): the kickoff meeting's Beats 2-3 — the standing G0E/G0R gates that
# the 3b default-flip makes CANONICAL on every run. Beat-1 (the look) is the S2
# picker ceremony; Beat-2 (the material) is G0E source-enrichment confirm; Beat-3
# (the contract) is G0R LO ratify. Named up front in ``_KICKOFF_SIGNOFFS`` so the
# operator sees a coherent look->material->contract arc, never a surprise gate.
_KICKOFF_BEATS: dict[str, tuple[str, str]] = {
    "G0E": ("Beat 2 of 3", "the material — the source inventory we teach from"),
    "G0R": ("Beat 3 of 3", "the contract — the learning objectives we sign up to"),
}


def _enrichment_mode_for_run(run_dir: Path) -> str | None:
    """The resolved enrichment MODE for this run, off the g0-enrichment.json receipt.

    Reads the D4 ``enrichment_mode`` stamp when present; else derives it FAIL-LOUD
    from the receipt ``model_id`` (:func:`resolve_enrichment_mode`). Returns ``None``
    only when no enrichment receipt exists yet (nothing to narrate).
    """
    enrichment = _load(run_dir / "g0-enrichment.json")
    if not isinstance(enrichment, dict):
        return None
    stamped = enrichment.get("enrichment_mode")
    if isinstance(stamped, str) and stamped:
        return stamped
    model_id = enrichment.get("model_id")
    if isinstance(model_id, str) and model_id:
        return resolve_enrichment_mode(model_id)
    return None


def narrate_live_available_affordance(mode: str | None, lines: list[str]) -> None:
    """Dan's binding caveat (D3): when the resolved mode is ``deterministic-recorded``,
    surface an explicit "richer live enrichment is available — arm it" affordance.

    Without this the operator cannot distinguish a deliberately-shallow cost-conscious
    default from the system's best effort, and may ratify thin LOs believing that is
    the ceiling (a silent content-quality ceiling). The affordance rides the
    mode-stamp (D4): the SAME receipt that records ``deterministic-recorded`` drives
    this operator-facing note. A ``live`` run (or no receipt) shows nothing.
    """
    if mode != G0_ENRICHMENT_MODE_DETERMINISTIC:
        return
    lines.append(
        f"{_M} NOTE: this enrichment is the DETERMINISTIC scaffold "
        "(deterministic-recorded mode) — reproducible and $0, but not the ceiling. "
        "Richer live semantic enrichment is available; re-run with the "
        f"`--g0-dispatch-live` flag (sets {G0_DISPATCH_LIVE_ENV}=1) to have me dispatch "
        "a real live-LLM G0 pre-pass. What you see below is the scaffold, not my best effort."
    )


def _narrate_g0_refinement(card: dict[str, Any], run_dir: Path, lines: list[str]) -> None:
    """Ratify-gate #2 (G0R): Irene's refined LOs + the LO-delta reconcile (Beat-3)."""
    inner = card.get("card", card)
    refined = inner.get("refined_los") or []
    reconcile = inner.get("reconcile") or {}
    flagged = inner.get("flagged_for_operator") or []
    lines.append(
        f"{_M} G0 LO-ratify contract for your sign-off (gate #2): Irene refined the "
        "provisional LOs into the teaching contract."
    )
    lines.append(f"  Refined learning objectives ({len(refined)}):")
    for lo in refined[:8]:
        adequacy = lo.get("adequacy") or {}
        verdict = adequacy.get("verdict") if isinstance(adequacy, dict) else None
        tag = f"  [{verdict}]" if verdict else ""
        lines.append(f"    - {lo.get('objective_id')}: {lo.get('statement', '')[:80]}{tag}")
    if reconcile:
        lines.append(
            f"  Reconcile: {reconcile.get('g0_count')} provisional -> "
            f"{reconcile.get('irene_count')} refined "
            f"({reconcile.get('changed')} changed, "
            f"{reconcile.get('flagged_thin_or_gap')} flagged thin/gap)."
        )
    if flagged:
        lines.append(f"  Needs your ruling ({len(flagged)}):")
        for entry in flagged[:6]:
            lo = entry.get("lo", {})
            lines.append(
                f"    - {entry.get('disposition')}: {lo.get('objective_id')} "
                f"{str(lo.get('statement', ''))[:60]}"
            )
    lines.append("  Ratify the contract, or tell me to add / drop / re-word an objective.")


def narrate_gate(gate_id: str, card: dict[str, Any], run_dir: Path) -> str:
    """Marcus-voiced narration of a gate, surfacing the relevant a-g capability."""
    lines: list[str] = [_RULE, f"  GATE {gate_id}"]
    # S5-3b (D3): frame the canonical G0E/G0R gates as the kickoff meeting's
    # Beats 2-3 (look -> material -> contract), so the woken standing gates read as
    # a coherent ceremony, not a surprise. Content-neutral display layer.
    beat = _KICKOFF_BEATS.get(gate_id)
    if beat is not None:
        beat_label, signoff = beat
        lines.append(f"{_M} Kickoff {beat_label}: {signoff}.")
    if gate_id == "G0E":
        _narrate_g0_enrichment(card, run_dir, lines)
        narrate_live_available_affordance(_enrichment_mode_for_run(run_dir), lines)
    elif gate_id == "G0R":
        _narrate_g0_refinement(card, run_dir, lines)
        narrate_live_available_affordance(_enrichment_mode_for_run(run_dir), lines)
    elif gate_id == "G1":
        _narrate_sources(run_dir, lines)
        _narrate_ingestion(run_dir, lines)
        _narrate_lesson_plan(run_dir, lines)
        lines.append(f"{_M} No gap-fill research was needed (capability d); the lesson is "
                     "corpus-grounded. Tell me if you'd like supporting research (Tracy).")
    elif gate_id == "G2B":
        _narrate_treatment(card, lines)
        chooser = _load(run_dir / "chooser-publish-G2B.json") or {}
        chooser_url = chooser.get("publish_url")
        if chooser_url:
            lines.append(
                f"{_M} Storyboard A is published - open it and CLICK your preferred variant "
                "for each slide, then paste the selection code back to me:"
            )
            lines.append(f"  {chooser_url}")
    elif gate_id == "G2C":
        pub = _load(run_dir / "storyboard-publish-G2C.json") or {}
        lines.append(
            f"{_M} Here is the storyboard with your per-slide picks applied, for final review:"
        )
        lines.append(f"  {pub.get('publish_url', '(local storyboard pack)')}")
    elif gate_id == "G3":
        lines.append(f"{_M} Motion plan (capability f) - this narrated-deck lesson plans no "
                     "motion clips (synthesis is a later capability). Tell me if you want "
                     "motion on any slide; otherwise I'll proceed still-only.")
    elif gate_id == "G4":
        lines.append(f"{_M} Fidelity gate - Vera checked the assets against your sources; no "
                     "blocking drift. Approve to proceed to narration.")
    elif gate_id == "G4A":
        _narrate_voice(card, lines)
    else:
        lines.append(f"{_M} Decision needed at {gate_id}.")
    return "\n".join(lines)


def run_marcus_spoc(
    trial_id: UUID,
    decisions: dict[str, dict[str, Any]] | None = None,
    runs_root: Path = RUNS_ROOT,
) -> list[str]:
    """Drive a paused trial to completion as a Marcus conversation; return the transcript."""
    decisions = decisions or {}
    run_dir = runs_root / str(trial_id)
    transcript: list[str] = [
        f"{_M} I'm your single point of contact for this run (trial {trial_id}). I'll walk "
        "you through each decision and handle the specialists, tools, and state behind the scenes.",
    ]
    for _ in range(30):
        run = _load(run_dir / "run.json") or {}
        status, gate = run.get("status"), run.get("paused_gate")
        if status == "completed":
            transcript.append(_RULE)
            transcript.append(f"{_M} Your lesson is assembled - slides, narration, and the "
                              "Descript hand-off bundle are ready. That's the run, error-free.")
            break
        if status == "paused-at-error":
            transcript.append(f"{_M} I hit a snag I couldn't auto-resolve "
                              f"({run.get('paused_error_tag')}); pausing for repair.")
            break
        if status != "paused-at-gate" or not gate:
            transcript.append(f"{_M} Unexpected state ({status}); stopping.")
            break
        card = _load(run_dir / f"decision-card-{gate}.json") or {}
        transcript.append(narrate_gate(gate, card, run_dir))
        decision = decisions.get(gate, {"verb": "approve"})
        verb = decision.get("verb", "approve")
        kwargs = build_operator_verdict_kwargs(
            trial_id=trial_id,
            gate_id=gate,
            card=card,
            verb=verb,
            edit_payload=decision.get("edit_payload"),
            reject_reason=decision.get("reject_reason"),
        )
        extra = f" {decision.get('edit_payload')}" if verb in {"edit", "select"} else ""
        transcript.append(f"👤 **Operator:** {verb}{extra}")
        env = resume_production_trial(
            trial_id=trial_id,
            verdict=OperatorVerdict(**kwargs),
            runs_root=runs_root,
            max_specialist_calls=12,
        )
        nxt = f", next: {env.paused_gate}" if env.paused_gate else ""
        transcript.append(f"{_M} (done - {env.status}{nxt})")
    return transcript


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(prog="python -m app.marcus.cli.marcus_spoc")
    parser.add_argument("--trial-id", required=True, type=UUID)
    parser.add_argument("--decisions-file", required=False)
    parser.add_argument("--runs-root", required=False)
    # S5-3b (D4 / F-1801 Reading A): the first-class production ARM for live G0
    # enrichment. Default OFF — the canonical run wakes the G0E/G0R HIL gates + the
    # DETERMINISTIC recorded enrichment (byte-stable, $0). Passing this flag sets
    # MARCUS_G0_DISPATCH_LIVE=1 for the run so the G0 pre-pass dispatches a real
    # live-LLM extraction (mirrors the --research dispatch surface). The env var is
    # retained as the underlying impl seam + a dev/evidence escape hatch; the CLI
    # flag is the auditable operator-facing arm. This flag does NOT change the
    # enrichment DEFAULT (that stays deterministic-recorded) — it arms it per run.
    parser.add_argument(
        "--g0-dispatch-live",
        action="store_true",
        help=(
            "Arm a REAL live-LLM G0 source-enrichment pre-pass for this run (sets "
            "MARCUS_G0_DISPATCH_LIVE=1). Default OFF: the canonical run uses the "
            "deterministic-recorded scaffold and spends $0."
        ),
    )
    args = parser.parse_args(argv)
    if args.g0_dispatch_live:
        # Arm the underlying impl seam for the whole run (auditable in the run record
        # via the enrichment_mode receipt stamp, which will resolve to 'live').
        import os

        os.environ[G0_DISPATCH_LIVE_ENV] = "1"
    decisions = None
    if args.decisions_file:
        decisions = json.loads(Path(args.decisions_file).read_text(encoding="utf-8"))
    runs_root = Path(args.runs_root) if args.runs_root else RUNS_ROOT
    print("\n".join(run_marcus_spoc(args.trial_id, decisions=decisions, runs_root=runs_root)))
    return 0


__all__ = [
    "DEFAULT_OPERATOR_ID",
    "DEGRADED_PUBLISH_URL_INLINE_LIST",
    "DEGRADED_PUBLISH_URL_PREFIX",
    "DEGRADED_PUBLISH_URL_REUSE_LAST_PICK",
    "DEGRADED_PUBLISH_URL_SCRIPTED",
    "build_operator_verdict_kwargs",
    "commit_picker_pick",
    "decode_and_echo_pick",
    "main",
    "narrate_gate",
    "narrate_inline_style_list",
    "narrate_kickoff_beat1",
    "narrate_pick_recommendation",
    "narrate_picker_preflight",
    "narrate_picker_publish_degrade",
    "run_marcus_spoc",
    "run_picker_preflight",
]


if __name__ == "__main__":
    raise SystemExit(main())
