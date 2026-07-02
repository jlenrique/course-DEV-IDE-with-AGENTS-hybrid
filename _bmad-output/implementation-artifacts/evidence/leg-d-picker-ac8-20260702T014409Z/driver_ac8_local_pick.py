"""Leg-D AC-8 LIVE leg — a REAL pick driven through the actual rendered HTML.

Fully LOCAL (no external API): the picker's real ephemeral-port http.server +
the real rendered page + a headless client that PARSES the rendered HTML's form
(action + field names + card data-guide values — never a hand-authored JSON
shortcut) and POSTs the pick exactly as the page's Confirm would. The picker
writes a REAL directive + emits its REAL pick-event line into the production
sidecar; then the REAL ``production_runner`` payload builders
(``_runner_payload_for_specialist`` irene_pass1 + ``_gamma_settings_from_directive``)
read that directive and the outputs are pinned as the dispatch-payload snapshot.

Arbiter (M-3): the pinned dispatch-payload snapshot is diffed against the
picker's independently-emitted pick-event log — two artifacts, two code paths,
independently generated; guide identity must agree.
"""

from __future__ import annotations

import json
import sys
import threading
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

EVIDENCE_DIR = Path(__file__).resolve().parent
REPO_ROOT = EVIDENCE_DIR.parents[3]
sys.path.insert(0, str(REPO_ROOT))

from app.marcus.orchestrator.production_runner import (  # noqa: E402
    _gamma_settings_from_directive,
    _runner_payload_for_specialist,
)
from app.marcus.orchestrator.styleguide_picker import (  # noqa: E402
    GAMMA_STYLEGUIDE_PICKS_PATH,
    append_pick_event,
    capture_pick,
    load_picker_roster,
    write_pick_to_directive,
)

RUN_ID = EVIDENCE_DIR.name  # leg-d-picker-ac8-<UTCstamp>
DIRECTIVE_PATH = EVIDENCE_DIR / "directive.yaml"
HTML_PATH = EVIDENCE_DIR / "picker.html"
PICK_A = "classic-freeform-x-cards"
PICK_B = "leg-c-part3-floor-probe"  # probe carries scripted.min_cluster_floor=8


class _RenderedFormParser(HTMLParser):
    """Parse the REAL rendered page: form action/method, field names, card guides."""

    def __init__(self) -> None:
        super().__init__()
        self.form_action: str | None = None
        self.form_method: str | None = None
        self.field_names: list[str] = []
        self.card_guides: list[str] = []
        self.probe_guides: list[str] = []
        self._in_form = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = dict(attrs)
        if tag == "form" and attr.get("id") == "pick-form":
            self._in_form = True
            self.form_action = attr.get("action")
            self.form_method = (attr.get("method") or "").upper()
        elif tag == "input" and self._in_form and attr.get("name"):
            self.field_names.append(str(attr["name"]))
        elif tag == "article" and "card" in (attr.get("class") or ""):
            guide = str(attr.get("data-guide") or "")
            self.card_guides.append(guide)
            if attr.get("data-probe") == "1":
                self.probe_guides.append(guide)

    def handle_endtag(self, tag: str) -> None:
        if tag == "form":
            self._in_form = False


def main() -> int:
    result: dict = {"run_id": RUN_ID, "checks": {}}
    checks = result["checks"]

    # (a) the picker's REAL server + REAL rendered page (probes opted in so the
    #     pick can bind the Leg-C floor probe -> a non-trivial irene payload).
    roster = load_picker_roster(include_probes=True)

    def _on_pick(picks: dict[str, str]) -> dict:
        provenance = write_pick_to_directive(DIRECTIVE_PATH, picks)
        append_pick_event(
            picks,
            directive_path=DIRECTIVE_PATH,
            picked_at=provenance["picked_at"],
            run_id=RUN_ID,
        )  # -> the REAL production sidecar state/config/gamma-styleguide-picks.jsonl
        return {
            "directive_path": DIRECTIVE_PATH.as_posix(),
            "picks": picks,
            "picked_at": provenance["picked_at"],
        }

    capture_out: dict = {}

    def _serve() -> None:
        picks, receipt = capture_pick(
            roster,
            on_pick=_on_pick,
            html_path=HTML_PATH,
            opener=lambda url: capture_out.setdefault("opened_url", url) or True,
            timeout=60.0,
        )
        capture_out["picks"] = picks
        capture_out["receipt"] = receipt

    worker = threading.Thread(target=_serve)
    worker.start()
    for _ in range(200):
        if HTML_PATH.exists():
            break
        worker.join(0.05)

    # (b) drive a REAL pick by parsing the rendered HTML's form — no shortcut.
    parser = _RenderedFormParser()
    parser.feed(HTML_PATH.read_text(encoding="utf-8"))
    checks["form_parsed_from_rendered_html"] = (
        parser.form_action is not None and parser.form_method == "POST"
    )
    checks["form_fields_are_slot_A_slot_B"] = parser.field_names == ["slot_A", "slot_B"]
    checks["picked_guides_present_as_cards"] = (
        PICK_A in parser.card_guides and PICK_B in parser.card_guides
    )
    checks["probe_card_marked_probe"] = PICK_B in parser.probe_guides
    result["form_action"] = parser.form_action
    result["card_guides"] = parser.card_guides

    body = urllib.parse.urlencode(
        {parser.field_names[0]: PICK_A, parser.field_names[1]: PICK_B}
    ).encode("utf-8")
    request = urllib.request.Request(
        str(parser.form_action),
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method=parser.form_method,
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        page_receipt = json.loads(response.read().decode("utf-8"))
    worker.join(timeout=30)
    checks["server_exited_after_one_post"] = not worker.is_alive()
    checks["page_receipt_matches_server_receipt"] = page_receipt == capture_out.get("receipt")
    result["page_receipt"] = page_receipt

    # (c) real directive written + real pick-event lines in the production sidecar.
    checks["directive_written"] = DIRECTIVE_PATH.is_file()
    log_lines = [
        json.loads(line)
        for line in GAMMA_STYLEGUIDE_PICKS_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    pick_events = [event for event in log_lines if event.get("run_id") == RUN_ID]
    checks["pick_events_emitted"] = len(pick_events) == 2
    (EVIDENCE_DIR / "pick-event-log.json").write_text(
        json.dumps(pick_events, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    # (d) the REAL production_runner payload builders bind the picked guides.
    gamma_settings = _gamma_settings_from_directive(DIRECTIVE_PATH)
    irene_payload = _runner_payload_for_specialist(
        specialist_id="irene_pass1", directive_path=DIRECTIVE_PATH, bundle_dir=None
    )
    snapshot = {
        "directive_path": DIRECTIVE_PATH.as_posix(),
        "gamma_settings_from_directive": gamma_settings,
        "runner_payload_irene_pass1": irene_payload,
    }
    (EVIDENCE_DIR / "dispatch-payload-snapshot.json").write_text(
        json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    checks["gamma_settings_bound"] = gamma_settings == [
        {"variant_id": "A", "styleguide": PICK_A},
        {"variant_id": "B", "styleguide": PICK_B},
    ]
    checks["floor_probe_threads_min_cluster_floor_8"] = irene_payload == {
        "min_cluster_floor": 8
    }

    # (e) M-3 arbiter: two independently generated artifacts must agree on
    #     guide identity — snapshot (production_runner read) vs pick-event log
    #     (picker emit at pick time).
    snapshot_identity = sorted(
        (item["variant_id"], item["styleguide"]) for item in gamma_settings
    )
    log_identity = sorted(
        (event["variant_id"], event["guide_name"]) for event in pick_events
    )
    checks["two_artifact_guide_identity_agrees"] = snapshot_identity == log_identity
    result["snapshot_identity"] = snapshot_identity
    result["log_identity"] = log_identity

    result["AC8_PASS"] = all(checks.values())
    (EVIDENCE_DIR / "result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["AC8_PASS"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
