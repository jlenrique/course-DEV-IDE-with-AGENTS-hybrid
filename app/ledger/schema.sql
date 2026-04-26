CREATE TABLE IF NOT EXISTS ledger_events (
    event_id UUID PRIMARY KEY,
    trial_id UUID NOT NULL,
    gate_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    payload JSONB NOT NULL,
    idempotency_key TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_ledger_events_trial_kind
    ON ledger_events (trial_id, kind, created_at);

CREATE INDEX IF NOT EXISTS idx_ledger_events_gate
    ON ledger_events (trial_id, gate_id);
