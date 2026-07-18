-- ============================================================
-- Email Open Tracking — NeonDB Schema
-- Run this in your Neon SQL console (https://console.neon.tech)
-- ============================================================

CREATE TABLE IF NOT EXISTS email_opens (
    id            SERIAL PRIMARY KEY,
    recipient     VARCHAR(255) NOT NULL,       -- email address of the recipient
    opened_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),  -- when they opened
    user_agent    TEXT,                         -- their browser/device info
    ip_address    VARCHAR(45),                  -- their IP address
    is_first_open BOOLEAN NOT NULL DEFAULT FALSE  -- true only for the very first open
);

-- Index for fast lookups by recipient email
CREATE INDEX IF NOT EXISTS idx_email_opens_recipient ON email_opens(recipient);

-- Index for finding first opens quickly
CREATE INDEX IF NOT EXISTS idx_email_opens_first ON email_opens(recipient, is_first_open) WHERE is_first_open = TRUE;
