# Story 35.6 — L3 live push witness (accountless ntfy)

**Status: WITNESS CLOSED (real delivery + receipt).** NFR5 — no mocks; one real
phone-push channel exercised end-to-end through Apprise (the exact transport the
notifier's `_RealApprise` uses: `apprise.Apprise().add(url)` + `.notify(title, body)`).

Per greenlight amendment 10 (party trim): the accountless **ntfy** channel is
the live witness; **Pushover** becomes a config-swap once the operator
provisions a token (no story fate-shares with operator account setup). Scheme
`ntfys` is inside the notifier's push allowlist `{ntfy, ntfys, pover}`.

## Method

1. Generate a random topic (`hud-35-6-witness-<rand>`), so the witness is
   isolated on the public server.
2. Send ONE real push via `apprise` to `ntfys://ntfy.sh/<topic>`.
3. GET `https://ntfy.sh/<topic>/json?poll=1` to retrieve the delivered message
   as the receipt.

Witness script: banked run below (executed with the live `.venv`).

## Request + receipt (banked)

| Field | Value |
|---|---|
| Server | `https://ntfy.sh` |
| Apprise URL scheme | `ntfys` (allowlisted) |
| Topic | `hud-35-6-witness-fc2118f1f464` |
| Title | `HUD 35.6 live witness` |
| Body | `Story 35.6 notifier real push proof — 2026-07-11T21:55:21.980243+00:00` |
| `apprise.notify()` result | `True` |
| Sent at (UTC) | `2026-07-11T21:55:21.980243+00:00` |
| Received at (UTC) | `2026-07-11T21:55:26.591811+00:00` |
| Delivered count | `1` |
| **Delivered message id** | **`wmUW9CnmLm6S`** |
| Delivered server time (epoch) | `1783806924` |
| Expires (epoch) | `1783850124` |

### Raw receipt (server JSON, `poll=1`)

```json
{"id":"wmUW9CnmLm6S","time":1783806924,"expires":1783850124,"event":"message","topic":"hud-35-6-witness-fc2118f1f464","title":"HUD 35.6 live witness","message":"Story 35.6 notifier real push proof — 2026-07-11T21:55:21.980243+00:00","icon":"https://github.com/caronc/apprise/raw/master/apprise/assets/themes/default/apprise-info-256x256.png"}
```

The delivered `title` + `message` match the request byte-for-byte (including the
UTC stamp embedded in the body), and the server assigned a message id — this is
a real round-trip through the public ntfy broker, not a local mock.

## Notes

- Credentials: none required for accountless ntfy; the notifier reads push URLs
  from `HUD_PUSH_URLS` env only (never config/repo). This witness used a bare
  topic URL, consistent with that env-only contract.
- Pushover parity: swapping to `pover://<user>@<token>` is a config/env change
  only — no code change (Apprise URL-string mechanism, AD-9).
