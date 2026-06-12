"""Platform-wide fixture-fallback ratchet (Murat MUST-FIX-BEFORE-S5, party
review 2026-06-12).

The S0 sweep converted the five KNOWN silent fixture fallbacks; this ratchet
guards against the SIXTH — a new production module growing a fixture-return
branch by pattern-matching off old code. Any app/ module that references
fixture machinery must (a) be on the explicit roster below and (b) gate the
fixture path behind the allow_fixture opt-in. New offenders fail CI, not a
postmortem three trials later.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_ROOT = REPO_ROOT / "app"

# Signatures of fixture machinery in production code. Input-side golden data
# in tests/ is legitimate (Murat doctrine) — this scans app/ only.
FIXTURE_SIGNATURES = re.compile(
    r"DEFAULT_FIXTURE_|_load_fixture|\"status\": \"mocked\"|'status': 'mocked'"
    r"|fixture short-circuit"
    # The EIGHTH seam's shape (gary act, Trial-3 cycle-2 2026-06-12): a
    # fabricated `fixture-{...}` identifier on the real path masked an
    # API-shape bug all the way to the G2C pause. Any reintroduction of
    # fabricated fixture-ids must either be rostered or die here.
    r"|fixture-\{"
    # The NINTH seam's shape (quinn_r G5 _slides, cycle-5 2026-06-12): an
    # INLINE fabricated single-row roster let a QA body audit a phantom
    # slide. Inline placeholder rosters in production modules are the same
    # genus as fixture reads.
    r"|\[\{['\"]slide_id['\"]:\s*['\"]slide-1['\"]\}\]"
)

# The S0-converted seams (five from the sweep + wanda's MB, the SEVENTH seam
# this very ratchet caught on its first run 2026-06-12): fixture paths exist
# but are allow_fixture-gated.
ALLOWED_FIXTURE_MODULES = {
    "app/specialists/gary/gamma_dispatch.py",
    "app/specialists/texas/retrieval_dispatch.py",
    "app/specialists/kira/kling_dispatch.py",
    "app/specialists/vera/sensory_bridges_dispatch.py",
    "app/specialists/quinn_r/sensory_bridges_dispatch.py",
    "app/specialists/wanda/wondercraft_dispatch.py",
}


def _offenders() -> dict[str, str]:
    found: dict[str, str] = {}
    for path in sorted(APP_ROOT.rglob("*.py")):
        rel = path.relative_to(REPO_ROOT).as_posix()
        source = path.read_text(encoding="utf-8")
        if FIXTURE_SIGNATURES.search(source):
            found[rel] = source
    return found


def test_fixture_machinery_only_in_rostered_modules() -> None:
    found = _offenders()
    unrostered = sorted(set(found) - ALLOWED_FIXTURE_MODULES)
    assert unrostered == [], (
        "Production module(s) reference fixture machinery without being on "
        f"the allow_fixture roster: {unrostered}. Per the S0 fail-loud policy "
        "(SCP 2026-06-11), absence of inputs is a contract violation, never a "
        "mode switch — gate the fixture path behind allow_fixture=True and "
        "add a deliberate roster entry, or remove the fixture branch."
    )


def test_rostered_modules_gate_fixture_paths_behind_opt_in() -> None:
    found = _offenders()
    ungated = sorted(
        rel
        for rel, source in found.items()
        if rel in ALLOWED_FIXTURE_MODULES and "allow_fixture" not in source
    )
    assert ungated == [], (
        f"Rostered fixture module(s) lost their allow_fixture gate: {ungated}"
    )


def test_roster_entries_still_reference_fixture_machinery() -> None:
    # Bidirectional pin (quarantine-not-landfill discipline): a rostered
    # module that no longer carries fixture machinery retires from the roster.
    found = _offenders()
    stale = sorted(ALLOWED_FIXTURE_MODULES - set(found))
    assert stale == [], (
        f"Roster entries no longer referencing fixture machinery: {stale} — "
        "remove them from ALLOWED_FIXTURE_MODULES."
    )
