# 📧 Email Open Tracking — Developer Deployment Guide
### For the PrimeRealOps dev team

---

## What This Does

When an outreach email is sent, a tiny invisible 1x1 pixel image is embedded in the HTML.
When the recipient opens the email, their browser loads that image from your Vercel site.
Your API catches the request → logs it to NeonDB → you know exactly who opened and when.

**Stack:** Next.js (App Router) + Vercel + NeonDB

---

## Setup — 3 Steps (~10 minutes)

---

### Step 1 — Run the Database Schema

Open your **Neon Console** (https://console.neon.tech) → go to the **SQL Editor** → paste and run:

```sql
CREATE TABLE IF NOT EXISTS email_opens (
    id            SERIAL PRIMARY KEY,
    recipient     VARCHAR(255) NOT NULL,
    opened_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_agent    TEXT,
    ip_address    VARCHAR(45),
    is_first_open BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_email_opens_recipient ON email_opens(recipient);
CREATE INDEX IF NOT EXISTS idx_email_opens_first ON email_opens(recipient, is_first_open) WHERE is_first_open = TRUE;
```

> The full schema file is at: `tracking-pixel/schema.sql`

---

### Step 2 — Add the API Routes

**File 1 — The tracking pixel endpoint:**
Copy `tracking-pixel/route.ts` to your Next.js project at:
```
app/api/track/route.ts
```

**File 2 — The opens dashboard endpoint (optional but useful):**
Copy `tracking-pixel/opens-route.ts` to your Next.js project at:
```
app/api/track/opens/route.ts
```

**Install the required package** (if not already installed):
```bash
npm install @neondatabase/serverless
```

---

### Step 3 — Set Environment Variables on Vercel

Go to **Vercel Dashboard** → your project → **Settings** → **Environment Variables**

Add these:

| Variable | Value | Required |
|---|---|---|
| `DATABASE_URL` | Your NeonDB connection string (probably already set) | ✅ Yes |
| `NOTIFY_EMAIL` | `info@primerealops.com` (for open notifications) | Optional |

---

## Deploy & Test

1. **Push the code** to your repo → Vercel auto-deploys
2. **Test the pixel** by opening this URL in your browser:
   ```
   https://primerealops.com/api/track?id=dGVzdEBleGFtcGxlLmNvbQ==
   ```
   You should see a blank page (that's the 1x1 invisible image — correct!)
3. **Check NeonDB** — run this query:
   ```sql
   SELECT * FROM email_opens;
   ```
   You should see one row with `recipient = test@example.com` ✅

4. **Check the dashboard API:**
   ```
   https://primerealops.com/api/track/opens
   ```
   Returns JSON with all opens and summary stats.

---

## How It Works (Technical)

```
Email sent with hidden <img> tag
     ↓
Recipient opens email → browser loads image
     ↓
GET https://primerealops.com/api/track?id=BASE64_EMAIL
     ↓
API decodes email → logs to NeonDB → returns 1x1 GIF
     ↓
NeonDB stores: recipient, timestamp, device, IP, is_first_open
```

The `id` parameter is the recipient's email address **base64url-encoded** for privacy.
For example: `nicole@kw.com` → `bmljb2xlQGt3LmNvbQ==`

---

## Viewing Opens

### Option A — Direct API (JSON)
```
GET https://primerealops.com/api/track/opens           → all opens
GET https://primerealops.com/api/track/opens?first_only=true  → first opens only
```

### Option B — SQL Query in Neon Console
```sql
-- Who opened? (first opens only)
SELECT recipient, opened_at FROM email_opens WHERE is_first_open = TRUE ORDER BY opened_at DESC;

-- How many total unique openers?
SELECT COUNT(DISTINCT recipient) FROM email_opens;

-- Opens today
SELECT * FROM email_opens WHERE opened_at >= CURRENT_DATE ORDER BY opened_at DESC;
```

---

## Security Notes

- The tracking API only accepts GET requests (no writes from external sources)
- The pixel always returns a valid image even if logging fails (no broken images in emails)
- Email addresses are base64-encoded in URLs (not plaintext)
- No authentication needed for the pixel endpoint (by design — email clients can't authenticate)
- The dashboard endpoint (`/api/track/opens`) should be protected if you don't want it public. Add auth middleware or an API key check if needed.

---

## File Summary

| File | Deploy To | Purpose |
|---|---|---|
| `tracking-pixel/schema.sql` | NeonDB SQL Editor | Creates the tracking table |
| `tracking-pixel/route.ts` | `app/api/track/route.ts` | Serves pixel + logs opens |
| `tracking-pixel/opens-route.ts` | `app/api/track/opens/route.ts` | Dashboard API for viewing opens |
