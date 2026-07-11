"""L3 live push witness (Story 35.6, NFR5 — real, no mocks).

Excluded from the default suite (``live`` + ``serial``): it performs one REAL
push to the public accountless ntfy broker through Apprise (the exact transport
the notifier's ``_RealApprise`` uses) and then retrieves the delivered message
as the receipt. Run explicitly::

    .venv/Scripts/python.exe -m pytest tests/notify/test_live_ntfy_witness.py \
        -m live --run-live -n0 -q

The banked run of record lives at
``_bmad-output/implementation-artifacts/evidence/hud-35-6-ntfy-witness.md``.
"""

from __future__ import annotations

import json
import secrets
import time
import urllib.request
from datetime import UTC, datetime

import pytest

pytestmark = [pytest.mark.live, pytest.mark.serial]


def test_real_ntfy_push_delivers_and_receipts():
    apprise = pytest.importorskip("apprise")

    topic = "hud-35-6-witness-" + secrets.token_hex(6)
    url = f"ntfys://ntfy.sh/{topic}"  # scheme in the notifier allowlist
    title = "HUD 35.6 live witness"
    body = f"Story 35.6 notifier real push proof — {datetime.now(UTC).isoformat()}"

    client = apprise.Apprise()
    assert client.add(url) is True
    assert client.notify(title=title, body=body) is True

    time.sleep(2)  # let the broker persist before we poll the cache
    receipt_url = f"https://ntfy.sh/{topic}/json?poll=1"
    req = urllib.request.Request(receipt_url, headers={"User-Agent": "hud-witness"})
    raw = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")  # noqa: S310 — fixed https host

    messages = [json.loads(line) for line in raw.splitlines() if line.strip()]
    delivered = [m for m in messages if m.get("event") == "message"]
    assert delivered, f"no message retrieved from ntfy for topic {topic}"
    got = delivered[0]
    assert got["title"] == title
    assert got["message"] == body
    assert got.get("id")  # the broker assigned a real message id
